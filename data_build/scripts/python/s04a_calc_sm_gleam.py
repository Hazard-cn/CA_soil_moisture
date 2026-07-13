"""
s04a_calc_sm_gleam.py — GLEAM土壤水分按物候窗口聚合
Purpose: Calculate GLEAM SM statistics (surface SMs + root zone SMrz) for each window
Author: Data Build Pipeline
Date: 2026-03-28
Input: data/intermediate/panel_windows.csv, GLEAM aligned NetCDF
Output: data/intermediate/sm_gleam_windows.csv
"""

import sys
import os
import numpy as np
import pandas as pd
import netCDF4 as nc
import time as timer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *
from sm_state_utils import attach_maize_zone, build_state_thresholds

np.random.seed(RANDOM_SEED)


def load_gleam_year(year, var_name, file_pattern):
    fpath = os.path.join(GLEAM_DIR, file_pattern.format(year=year))
    ds = nc.Dataset(fpath)
    sm = np.ma.filled(ds.variables[var_name][:], np.nan).astype(np.float32)
    ds.close()
    return sm


def compute_sm_baseline_percentiles(sm_dir, var_name, file_pattern):
    """Compute SM p10/p20/p80/p90 per grid cell over baseline years (growing season)."""
    print(f"  Computing {var_name} baseline percentiles...")
    all_sm = []
    for year in BASELINE_YEARS:
        fpath = os.path.join(sm_dir, file_pattern.format(year=year))
        if not os.path.exists(fpath):
            continue
        sm = load_gleam_year(year, var_name, file_pattern)
        all_sm.append(sm[89:300, :, :])  # DOY 90-300

    if not all_sm:
        print(f"    WARNING: No baseline data found!")
        return None, None, None, None

    stacked = np.concatenate(all_sm, axis=0)
    p10 = np.nanpercentile(stacked, 10, axis=0)
    p20 = np.nanpercentile(stacked, 20, axis=0)
    p80 = np.nanpercentile(stacked, 80, axis=0)
    p90 = np.nanpercentile(stacked, 90, axis=0)
    del stacked, all_sm
    print(f"    p10: [{np.nanmin(p10):.4f}, {np.nanmax(p10):.4f}]")
    print(f"    p20: [{np.nanmin(p20):.4f}, {np.nanmax(p20):.4f}]")
    print(f"    p80: [{np.nanmin(p80):.4f}, {np.nanmax(p80):.4f}]")
    print(f"    p90: [{np.nanmin(p90):.4f}, {np.nanmax(p90):.4f}]")
    return p10, p20, p80, p90


def process_sm_window(panel_yr, sm_3d, p10_2d, p20_2d, p80_2d, p90_2d,
                      pooled_lookup, zone_lookup, wname, suffix, prefix):
    """Process SM for one window, all cells."""
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
        valid = ~np.isnan(sm)
        valid_days = np.sum(valid, axis=0).astype(np.float32)
        has_data = valid_days > 0

        if not has_data.any():
            continue

        out_idx = cell_indices[has_data]
        sm_data = sm[:, has_data]
        valid_data = valid[:, has_data]
        li_data = li[has_data]
        lj_data = lj[has_data]
        zone_data = pair_zones[has_data]
        valid_days_data = valid_days[has_data]

        result[f'{prefix}_mean{suffix}'][out_idx] = np.nanmean(sm_data, axis=0)
        result[f'{prefix}_min{suffix}'][out_idx] = np.nanmin(sm_data, axis=0)
        result[f'{prefix}_max{suffix}'][out_idx] = np.nanmax(sm_data, axis=0)
        if sm_data.shape[0] > 1:
            result[f'{prefix}_sd{suffix}'][out_idx] = np.nanstd(sm_data, axis=0, ddof=1)

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

            result[f'drydays_{prefix}_le_p10{suffix}'][out_idx] = dry10_days
            result[f'drydays_{prefix}_le_p20{suffix}'][out_idx] = dry20_days
            result[f'wetdays_{prefix}_ge_p80{suffix}'][out_idx] = wet80_days
            result[f'wetdays_{prefix}_ge_p90{suffix}'][out_idx] = wet90_days

            result[f'dryshare_{prefix}_le_p10{suffix}'][out_idx] = dry10_days / valid_days_data
            result[f'dryshare_{prefix}_le_p20{suffix}'][out_idx] = dry20_days / valid_days_data
            result[f'wetshare_{prefix}_ge_p80{suffix}'][out_idx] = wet80_days / valid_days_data
            result[f'wetshare_{prefix}_ge_p90{suffix}'][out_idx] = wet90_days / valid_days_data

            dry_gap10 = np.where(valid_data, np.maximum(cell_p10[np.newaxis, :] - sm_data, 0.0), np.nan)
            dry_gap20 = np.where(valid_data, np.maximum(cell_p20[np.newaxis, :] - sm_data, 0.0), np.nan)
            wet_gap80 = np.where(valid_data, np.maximum(sm_data - cell_p80[np.newaxis, :], 0.0), np.nan)
            wet_gap90 = np.where(valid_data, np.maximum(sm_data - cell_p90[np.newaxis, :], 0.0), np.nan)

            result[f'drydeficit_{prefix}_le_p10{suffix}'][out_idx] = np.nanmean(dry_gap10, axis=0).astype(np.float32)
            result[f'drydeficit_{prefix}_le_p20{suffix}'][out_idx] = np.nanmean(dry_gap20, axis=0).astype(np.float32)
            result[f'wetexcess_{prefix}_ge_p80{suffix}'][out_idx] = np.nanmean(wet_gap80, axis=0).astype(np.float32)
            result[f'wetexcess_{prefix}_ge_p90{suffix}'][out_idx] = np.nanmean(wet_gap90, axis=0).astype(np.float32)

        p25 = pooled_lookup[wname]['p25']
        p75 = pooled_lookup[wname]['p75']
        dry_pl = (sm_data <= p25) & valid_data
        wet_pl = (sm_data >= p75) & valid_data
        dry_pl_days = np.sum(dry_pl, axis=0).astype(np.float32)
        wet_pl_days = np.sum(wet_pl, axis=0).astype(np.float32)
        result[f'dryshare_pl_{prefix}_le_p25{suffix}'][out_idx] = dry_pl_days / valid_days_data
        result[f'wetshare_pl_{prefix}_ge_p75{suffix}'][out_idx] = wet_pl_days / valid_days_data
        result[f'drydeficit_pl_{prefix}_le_p25{suffix}'][out_idx] = np.nanmean(
            np.where(valid_data, np.maximum(p25 - sm_data, 0.0), np.nan), axis=0
        ).astype(np.float32)
        result[f'wetexcess_pl_{prefix}_ge_p75{suffix}'][out_idx] = np.nanmean(
            np.where(valid_data, np.maximum(sm_data - p75, 0.0), np.nan), axis=0
        ).astype(np.float32)

        local_p25 = np.array([zone_lookup[(wname, str(zone))]['p25'] for zone in zone_data], dtype=np.float32)
        local_p75 = np.array([zone_lookup[(wname, str(zone))]['p75'] for zone in zone_data], dtype=np.float32)
        dry_mz = (sm_data <= local_p25[np.newaxis, :]) & valid_data
        wet_mz = (sm_data >= local_p75[np.newaxis, :]) & valid_data
        dry_mz_days = np.sum(dry_mz, axis=0).astype(np.float32)
        wet_mz_days = np.sum(wet_mz, axis=0).astype(np.float32)
        result[f'dryshare_mz_{prefix}_le_p25{suffix}'][out_idx] = dry_mz_days / valid_days_data
        result[f'wetshare_mz_{prefix}_ge_p75{suffix}'][out_idx] = wet_mz_days / valid_days_data
        result[f'drydeficit_mz_{prefix}_le_p25{suffix}'][out_idx] = np.nanmean(
            np.where(valid_data, np.maximum(local_p25[np.newaxis, :] - sm_data, 0.0), np.nan), axis=0
        ).astype(np.float32)
        result[f'wetexcess_mz_{prefix}_ge_p75{suffix}'][out_idx] = np.nanmean(
            np.where(valid_data, np.maximum(sm_data - local_p75[np.newaxis, :], 0.0), np.nan), axis=0
        ).astype(np.float32)

    return result


def main():
    print("=" * 70)
    print("Step 04a: GLEAM Soil Moisture Window Aggregation")
    print("=" * 70)

    panel = pd.read_csv(os.path.join(INTERMEDIATE_DIR, "panel_windows.csv"))
    panel = attach_maize_zone(panel)
    print(f"Panel: {len(panel)} rows")

    file_pattern = "GLEAM_SM_0.1deg_TEMPgrid_{year}.nc"

    # Compute baseline percentiles for both layers
    smrz_p10, smrz_p20, smrz_p80, smrz_p90 = compute_sm_baseline_percentiles(
        GLEAM_DIR, 'SMrz', file_pattern)
    sms_p10, sms_p20, sms_p80, sms_p90 = compute_sm_baseline_percentiles(
        GLEAM_DIR, 'SMs', file_pattern)
    smrz_pooled, smrz_zone = build_state_thresholds(
        panel, YEARS, lambda year: load_gleam_year(year, 'SMrz', file_pattern)
    )
    sms_pooled, sms_zone = build_state_thresholds(
        panel, YEARS, lambda year: load_gleam_year(year, 'SMs', file_pattern)
    )

    all_dfs = []
    for year in YEARS:
        panel_yr = panel[panel['year'] == year].copy()
        print(f"\n  Year {year}: {len(panel_yr)} cells")
        t0 = timer.time()

        # Load GLEAM data
        smrz_3d = load_gleam_year(year, 'SMrz', file_pattern)
        sms_3d = load_gleam_year(year, 'SMs', file_pattern)
        print(f"    Loaded: SMrz {smrz_3d.shape}, SMs {sms_3d.shape}")

        all_results = {}
        for wname, wdef in WINDOWS.items():
            suffix = wdef['suffix']
            # Root zone
            r1 = process_sm_window(
                panel_yr, smrz_3d, smrz_p10, smrz_p20, smrz_p80, smrz_p90,
                smrz_pooled, smrz_zone, wname, suffix, 'gleam_smrz'
            )
            # Surface
            r2 = process_sm_window(
                panel_yr, sms_3d, sms_p10, sms_p20, sms_p80, sms_p90,
                sms_pooled, sms_zone, wname, suffix, 'gleam_sms'
            )
            all_results.update(r1)
            all_results.update(r2)

        del smrz_3d, sms_3d
        df_yr = pd.DataFrame(all_results, index=panel_yr.index)
        all_dfs.append(df_yr)
        print(f"    Total: {timer.time()-t0:.1f}s")

    df_sm = pd.concat(all_dfs).loc[panel.index]

    output = pd.concat([
        panel[['grid_id', 'year', 'latitude', 'longitude', 'lat_idx', 'lon_idx']],
        df_sm
    ], axis=1)

    outpath = os.path.join(INTERMEDIATE_DIR, "sm_gleam_windows.csv")
    output.to_csv(outpath, index=False)
    print(f"\nSaved: {outpath} ({len(output)} rows, {len(output.columns)} cols)")

    print("\nValidation (full season):")
    for v in [
        'gleam_smrz_mean',
        'drydays_gleam_smrz_le_p10',
        'wetdays_gleam_smrz_ge_p90',
        'dryshare_pl_gleam_smrz_le_p25',
        'wetshare_mz_gleam_smrz_ge_p75',
    ]:
        if v in output.columns:
            print(f"  {v}: mean={output[v].mean():.4f}, min={output[v].min():.4f}, max={output[v].max():.4f}")


if __name__ == "__main__":
    main()
