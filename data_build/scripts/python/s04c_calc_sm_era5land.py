"""
s04c_calc_sm_era5land.py — ERA5-Land soil moisture by phenological window
Purpose: Calculate ERA5-Land SM statistics (swvl1 surface + swvl3 root zone) for each window
Author: Data Build Pipeline
Date: 2026-03-29
Input: data/intermediate/panel_windows.csv, ERA5-Land SM NetCDF (D:/Soil_data_sy/netCDF)
Output: data/intermediate/sm_era5land_windows.csv

Notes:
  - ERA5-Land grid: 386x631 (lat 54.5→16.0, lon 73.0→136.0, 0.1°)
  - Reference grid: 376x616 (ERA5 temp)
  - Data coverage: March-October only (months 3-10), 2016-2019
  - Units: m³/m³ (volumetric water content), float32, no scaling needed
  - Layers: swvl1 (0-7cm surface), swvl3 (28-100cm root zone)
  - Climatological LAI only → lowest endogeneity risk among 3 SM sources
"""

import sys
import os
import numpy as np
import pandas as pd
import netCDF4 as nc
import time as timer
from calendar import monthrange, isleap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *
from sm_state_utils import attach_maize_zone, build_state_thresholds

np.random.seed(RANDOM_SEED)


def build_era5l_alignment():
    """Build 1D nearest-neighbor mapping from ERA5-Land (386x631) to ref grid (376x616).

    Returns lat_map (376,) and lon_map (616,) index arrays.
    """
    # ERA5-Land grid
    sample_path = os.path.join(ERA5L_SM_DIR,
                               "SoilWater_2016_03/volumetric_soil_water_layer_1_0_daily-mean.nc")
    ds = nc.Dataset(sample_path)
    era5l_lat = ds.variables['latitude'][:].astype(np.float64)
    era5l_lon = ds.variables['longitude'][:].astype(np.float64)
    ds.close()

    # Reference grid (ERA5 temperature)
    import glob
    temp_files = glob.glob(os.path.join(TEMP_DIR, "*.nc"))
    ds_ref = nc.Dataset(temp_files[0])
    ref_lat = ds_ref.variables['latitude'][:].astype(np.float64)
    ref_lon = ds_ref.variables['longitude'][:].astype(np.float64)
    ds_ref.close()

    # 1D nearest-neighbor mapping
    lat_map = np.array([np.argmin(np.abs(era5l_lat - rl)) for rl in ref_lat])
    lon_map = np.array([np.argmin(np.abs(era5l_lon - rl)) for rl in ref_lon])

    # Report alignment quality
    lat_err = np.array([era5l_lat[lat_map[i]] - ref_lat[i] for i in range(len(ref_lat))])
    lon_err = np.array([era5l_lon[lon_map[i]] - ref_lon[i] for i in range(len(ref_lon))])
    print(f"  Alignment: lat err max={np.max(np.abs(lat_err)):.4f}°, "
          f"lon err max={np.max(np.abs(lon_err)):.4f}°")

    return lat_map, lon_map


def doy_from_month_day(year, month, day):
    """Convert (year, month, day) to DOY (1-based)."""
    from datetime import date
    return date(year, month, day).timetuple().tm_yday


def load_era5l_year(year, layer, lat_map, lon_map):
    """Load ERA5-Land daily mean SM for one year, aligned to reference grid.

    Args:
        year: int
        layer: 1 or 3 (swvl1 or swvl3)
        lat_map, lon_map: alignment index arrays

    Returns:
        sm_3d: (ndays_year, 376, 616) float32, NaN outside Mar-Oct
    """
    ndays = 366 if isleap(year) else 365
    sm_3d = np.full((ndays, REF_NLAT, REF_NLON), np.nan, dtype=np.float32)

    var_name = f'swvl{layer}'

    for month in range(3, 11):  # March through October
        dirname = f"SoilWater_{year}_{month:02d}"
        fname = f"volumetric_soil_water_layer_{layer}_0_daily-mean.nc"
        fpath = os.path.join(ERA5L_SM_DIR, dirname, fname)

        if not os.path.exists(fpath):
            print(f"    WARNING: missing {fpath}")
            continue

        ds = nc.Dataset(fpath)
        data = np.ma.filled(ds.variables[var_name][:], np.nan).astype(np.float32)
        ds.close()
        # data shape: (ndays_month, 386, 631)

        # Align to reference grid
        data_aligned = data[:, lat_map, :][:, :, lon_map]  # (ndays_month, 376, 616)

        # Place into annual array
        start_doy = doy_from_month_day(year, month, 1)
        ndays_month = monthrange(year, month)[1]
        si = start_doy - 1  # 0-based index
        sm_3d[si:si + ndays_month] = data_aligned

    # Report coverage
    valid_days = np.sum(~np.isnan(sm_3d), axis=(1, 2))
    filled_days = np.sum(valid_days > 0)
    print(f"    Year {year}, swvl{layer}: {filled_days}/{ndays} days with data, "
          f"shape {sm_3d.shape}")

    return sm_3d


def compute_era5l_baseline_percentiles(lat_map, lon_map, layer):
    """Compute ERA5-Land p10/p20/p80/p90 per grid cell over 2016-2019 (DOY 90-300)."""
    print(f"  Computing swvl{layer} baseline percentiles (2016-2019)...")
    all_sm = []
    for year in YEARS:  # 2016-2019 only
        sm_3d = load_era5l_year(year, layer, lat_map, lon_map)
        all_sm.append(sm_3d[89:300, :, :])  # DOY 90-300
        del sm_3d

    stacked = np.concatenate(all_sm, axis=0)
    del all_sm
    p10 = np.nanpercentile(stacked, 10, axis=0)
    p20 = np.nanpercentile(stacked, 20, axis=0)
    p80 = np.nanpercentile(stacked, 80, axis=0)
    p90 = np.nanpercentile(stacked, 90, axis=0)
    del stacked
    print(f"    p10: [{np.nanmin(p10):.4f}, {np.nanmax(p10):.4f}]")
    print(f"    p20: [{np.nanmin(p20):.4f}, {np.nanmax(p20):.4f}]")
    print(f"    p80: [{np.nanmin(p80):.4f}, {np.nanmax(p80):.4f}]")
    print(f"    p90: [{np.nanmin(p90):.4f}, {np.nanmax(p90):.4f}]")
    return p10, p20, p80, p90


def process_sm_window(panel_yr, sm_3d, p10_2d, p20_2d, p80_2d, p90_2d,
                      pooled_lookup, zone_lookup, wname, suffix, prefix):
    """Process ERA5-Land SM for one window, all cells. Adds coverage fraction."""
    ndays = sm_3d.shape[0]
    n = len(panel_yr)

    var_names = [
        f'{prefix}_mean', f'{prefix}_min', f'{prefix}_max', f'{prefix}_sd',
        f'drydays_{prefix}_le_p10', f'drydays_{prefix}_le_p20',
        f'wetdays_{prefix}_ge_p80', f'wetdays_{prefix}_ge_p90',
        f'dryshare_{prefix}_le_p10', f'dryshare_{prefix}_le_p20',
        f'wetshare_{prefix}_ge_p80', f'wetshare_{prefix}_ge_p90',
        f'drydeficit_{prefix}_le_p10', f'drydeficit_{prefix}_le_p20',
        f'wetexcess_{prefix}_ge_p80', f'wetexcess_{prefix}_ge_p90',
        f'dryshare_pl_{prefix}_le_p25', f'wetshare_pl_{prefix}_ge_p75',
        f'drydeficit_pl_{prefix}_le_p25', f'wetexcess_pl_{prefix}_ge_p75',
        f'dryshare_mz_{prefix}_le_p25', f'wetshare_mz_{prefix}_ge_p75',
        f'drydeficit_mz_{prefix}_le_p25', f'wetexcess_mz_{prefix}_ge_p75',
        f'{prefix}_coverage',
    ]
    result = {f'{v}{suffix}': np.full(n, np.nan, dtype=np.float32) for v in var_names}

    starts = panel_yr[f'win_{wname}_start'].values
    ends = panel_yr[f'win_{wname}_end'].values
    lat_idxs = panel_yr['lat_idx'].values.astype(int)
    lon_idxs = panel_yr['lon_idx'].values.astype(int)
    zones = panel_yr['maize_zone'].values.astype(object)

    unique_pairs = np.unique(np.column_stack([starts, ends]), axis=0)

    for pair in unique_pairs:
        s_doy, e_doy = int(pair[0]), int(pair[1])
        si = max(0, s_doy - 1)
        ei = min(ndays, e_doy)
        if si >= ei:
            continue

        mask = (starts == s_doy) & (ends == e_doy)
        cell_indices = np.where(mask)[0]
        li = lat_idxs[cell_indices]
        lj = lon_idxs[cell_indices]
        pair_zones = zones[cell_indices]

        sm = sm_3d[si:ei, li, lj]  # (win_days, n_cells)
        win_len = ei - si

        # Coverage: fraction of non-NaN days in window
        n_valid = np.sum(~np.isnan(sm), axis=0).astype(np.float32)
        result[f'{prefix}_coverage{suffix}'][cell_indices] = n_valid / win_len

        # Only compute stats where there's data
        has_data = n_valid > 0

        if has_data.any():
            ci_data = cell_indices[has_data]
            sm_data = sm[:, has_data]
            valid_data = ~np.isnan(sm_data)
            zone_data = pair_zones[has_data]
            li_data = li[has_data]
            lj_data = lj[has_data]
            valid_days_data = n_valid[has_data]

            result[f'{prefix}_mean{suffix}'][ci_data] = np.nanmean(sm_data, axis=0)
            result[f'{prefix}_min{suffix}'][ci_data] = np.nanmin(sm_data, axis=0)
            result[f'{prefix}_max{suffix}'][ci_data] = np.nanmax(sm_data, axis=0)
            if sm_data.shape[0] > 1:
                result[f'{prefix}_sd{suffix}'][ci_data] = np.nanstd(sm_data, axis=0, ddof=1)

            if p10_2d is not None:
                cell_p10 = p10_2d[li_data, lj_data]
                cell_p20 = p20_2d[li_data, lj_data]
                cell_p80 = p80_2d[li_data, lj_data]
                cell_p90 = p90_2d[li_data, lj_data]

                dry10 = (sm_data <= cell_p10[np.newaxis, :]) & valid_data
                dry20 = (sm_data <= cell_p20[np.newaxis, :]) & valid_data
                wet80 = (sm_data >= cell_p80[np.newaxis, :]) & valid_data
                wet90 = (sm_data >= cell_p90[np.newaxis, :]) & valid_data

                dry10_days = np.sum(dry10, axis=0).astype(np.float32)
                dry20_days = np.sum(dry20, axis=0).astype(np.float32)
                wet80_days = np.sum(wet80, axis=0).astype(np.float32)
                wet90_days = np.sum(wet90, axis=0).astype(np.float32)

                result[f'drydays_{prefix}_le_p10{suffix}'][ci_data] = dry10_days
                result[f'drydays_{prefix}_le_p20{suffix}'][ci_data] = dry20_days
                result[f'wetdays_{prefix}_ge_p80{suffix}'][ci_data] = wet80_days
                result[f'wetdays_{prefix}_ge_p90{suffix}'][ci_data] = wet90_days

                result[f'dryshare_{prefix}_le_p10{suffix}'][ci_data] = dry10_days / valid_days_data
                result[f'dryshare_{prefix}_le_p20{suffix}'][ci_data] = dry20_days / valid_days_data
                result[f'wetshare_{prefix}_ge_p80{suffix}'][ci_data] = wet80_days / valid_days_data
                result[f'wetshare_{prefix}_ge_p90{suffix}'][ci_data] = wet90_days / valid_days_data

                result[f'drydeficit_{prefix}_le_p10{suffix}'][ci_data] = np.nanmean(
                    np.where(valid_data, np.maximum(cell_p10[np.newaxis, :] - sm_data, 0.0), np.nan), axis=0
                ).astype(np.float32)
                result[f'drydeficit_{prefix}_le_p20{suffix}'][ci_data] = np.nanmean(
                    np.where(valid_data, np.maximum(cell_p20[np.newaxis, :] - sm_data, 0.0), np.nan), axis=0
                ).astype(np.float32)
                result[f'wetexcess_{prefix}_ge_p80{suffix}'][ci_data] = np.nanmean(
                    np.where(valid_data, np.maximum(sm_data - cell_p80[np.newaxis, :], 0.0), np.nan), axis=0
                ).astype(np.float32)
                result[f'wetexcess_{prefix}_ge_p90{suffix}'][ci_data] = np.nanmean(
                    np.where(valid_data, np.maximum(sm_data - cell_p90[np.newaxis, :], 0.0), np.nan), axis=0
                ).astype(np.float32)

            p25 = pooled_lookup[wname]['p25']
            p75 = pooled_lookup[wname]['p75']
            dry_pl = (sm_data <= p25) & valid_data
            wet_pl = (sm_data >= p75) & valid_data
            dry_pl_days = np.sum(dry_pl, axis=0).astype(np.float32)
            wet_pl_days = np.sum(wet_pl, axis=0).astype(np.float32)
            result[f'dryshare_pl_{prefix}_le_p25{suffix}'][ci_data] = dry_pl_days / valid_days_data
            result[f'wetshare_pl_{prefix}_ge_p75{suffix}'][ci_data] = wet_pl_days / valid_days_data
            result[f'drydeficit_pl_{prefix}_le_p25{suffix}'][ci_data] = np.nanmean(
                np.where(valid_data, np.maximum(p25 - sm_data, 0.0), np.nan), axis=0
            ).astype(np.float32)
            result[f'wetexcess_pl_{prefix}_ge_p75{suffix}'][ci_data] = np.nanmean(
                np.where(valid_data, np.maximum(sm_data - p75, 0.0), np.nan), axis=0
            ).astype(np.float32)

            local_p25 = np.array([zone_lookup[(wname, str(zone))]['p25'] for zone in zone_data], dtype=np.float32)
            local_p75 = np.array([zone_lookup[(wname, str(zone))]['p75'] for zone in zone_data], dtype=np.float32)
            dry_mz = (sm_data <= local_p25[np.newaxis, :]) & valid_data
            wet_mz = (sm_data >= local_p75[np.newaxis, :]) & valid_data
            dry_mz_days = np.sum(dry_mz, axis=0).astype(np.float32)
            wet_mz_days = np.sum(wet_mz, axis=0).astype(np.float32)
            result[f'dryshare_mz_{prefix}_le_p25{suffix}'][ci_data] = dry_mz_days / valid_days_data
            result[f'wetshare_mz_{prefix}_ge_p75{suffix}'][ci_data] = wet_mz_days / valid_days_data
            result[f'drydeficit_mz_{prefix}_le_p25{suffix}'][ci_data] = np.nanmean(
                np.where(valid_data, np.maximum(local_p25[np.newaxis, :] - sm_data, 0.0), np.nan), axis=0
            ).astype(np.float32)
            result[f'wetexcess_mz_{prefix}_ge_p75{suffix}'][ci_data] = np.nanmean(
                np.where(valid_data, np.maximum(sm_data - local_p75[np.newaxis, :], 0.0), np.nan), axis=0
            ).astype(np.float32)

    return result


def main():
    print("=" * 70)
    print("Step 04c: ERA5-Land Soil Moisture Window Aggregation")
    print("=" * 70)

    panel = pd.read_csv(os.path.join(INTERMEDIATE_DIR, "panel_windows.csv"))
    panel = attach_maize_zone(panel)
    print(f"Panel: {len(panel)} rows")

    # Build alignment mapping
    print("\nBuilding ERA5-Land → reference grid alignment...")
    lat_map, lon_map = build_era5l_alignment()

    # Compute baseline percentiles (2016-2019)
    print("\nComputing baseline percentiles...")
    swvl1_p10, swvl1_p20, swvl1_p80, swvl1_p90 = compute_era5l_baseline_percentiles(lat_map, lon_map, 1)
    swvl3_p10, swvl3_p20, swvl3_p80, swvl3_p90 = compute_era5l_baseline_percentiles(lat_map, lon_map, 3)
    swvl1_pooled, swvl1_zone = build_state_thresholds(
        panel, YEARS, lambda year: load_era5l_year(year, 1, lat_map, lon_map)
    )
    swvl3_pooled, swvl3_zone = build_state_thresholds(
        panel, YEARS, lambda year: load_era5l_year(year, 3, lat_map, lon_map)
    )

    # Process each year
    all_dfs = []
    for year in YEARS:
        panel_yr = panel[panel['year'] == year].copy()
        print(f"\n  Year {year}: {len(panel_yr)} cells")
        t0 = timer.time()

        # Load ERA5-Land for this year
        swvl1_3d = load_era5l_year(year, 1, lat_map, lon_map)
        swvl3_3d = load_era5l_year(year, 3, lat_map, lon_map)

        all_results = {}
        for wname, wdef in WINDOWS.items():
            suffix = wdef['suffix']
            # Surface (swvl1, 0-7cm)
            r1 = process_sm_window(
                panel_yr, swvl1_3d, swvl1_p10, swvl1_p20, swvl1_p80, swvl1_p90,
                swvl1_pooled, swvl1_zone, wname, suffix, 'era5l_swvl1'
            )
            # Root zone (swvl3, 28-100cm)
            r2 = process_sm_window(
                panel_yr, swvl3_3d, swvl3_p10, swvl3_p20, swvl3_p80, swvl3_p90,
                swvl3_pooled, swvl3_zone, wname, suffix, 'era5l_swvl3'
            )
            all_results.update(r1)
            all_results.update(r2)

        del swvl1_3d, swvl3_3d
        df_yr = pd.DataFrame(all_results, index=panel_yr.index)
        all_dfs.append(df_yr)
        print(f"    Total: {timer.time()-t0:.1f}s")

    df_sm = pd.concat(all_dfs).loc[panel.index]

    output = pd.concat([
        panel[['grid_id', 'year', 'latitude', 'longitude', 'lat_idx', 'lon_idx']],
        df_sm
    ], axis=1)

    outpath = os.path.join(INTERMEDIATE_DIR, "sm_era5land_windows.csv")
    output.to_csv(outpath, index=False)
    print(f"\nSaved: {outpath} ({len(output)} rows, {len(output.columns)} cols)")

    # Validation
    print("\nValidation (full season):")
    for v in ['era5l_swvl3_mean', 'era5l_swvl3_coverage', 'drydays_era5l_swvl3_le_p10',
              'wetdays_era5l_swvl3_ge_p90', 'dryshare_pl_era5l_swvl3_le_p25',
              'wetshare_mz_era5l_swvl3_ge_p75']:
        if v in output.columns:
            vals = output[v]
            print(f"  {v}: mean={vals.mean():.4f}, min={vals.min():.4f}, "
                  f"max={vals.max():.4f}, missing={vals.isna().mean()*100:.1f}%")

    # Coverage summary by window
    print("\nCoverage by window:")
    for wname, wdef in WINDOWS.items():
        suffix = wdef['suffix']
        col = f'era5l_swvl1_coverage{suffix}'
        if col in output.columns:
            vals = output[col]
            print(f"  {wname}: mean={vals.mean():.4f}, min={vals.min():.4f}")


if __name__ == "__main__":
    main()
