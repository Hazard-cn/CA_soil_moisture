"""
s06_calc_vpd_spei.py — VPD (monthly weighted) and SPEI (end-month extraction)
Purpose: Calculate window-weighted VPD and v1-style SPEI from monthly data
Author: Data Build Pipeline
Date: 2026-03-28 (SPEI method updated 2026-04-04)
Input: data/intermediate/panel_windows.csv, CHM_VPD.nc, CHM_SPEI-*.nc
Output: data/intermediate/vpd_spei_windows.csv

VPD: Monthly weighted average (overlap days / total window days)
SPEI: End-month single-point extraction (v1 logic)
  - For each grid-year window: scale = end_month - start_month + 1
  - Extract SPEI-{scale} at end_month (exploits SPEI's built-in accumulation)
"""

import sys
import os
import numpy as np
import pandas as pd
import netCDF4 as nc
import time as timer
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

np.random.seed(RANDOM_SEED)

# Nominal SPEI scale prefix per window (keeps downstream column names unchanged)
SPEI_NOMINAL_PREFIX = {
    'full':    'spei6',
    'v3pre30': 'spei1',
    'v3pm10':  'spei1',
    'hepm10':  'spei1',
    'v3he':    'spei2',
    'hema':    'spei2',
}


def build_chm_alignment():
    """Build 1D nearest-neighbor mapping from ERA grid to CHM grid."""
    print("  Building ERA -> CHM grid alignment...")

    ds_ref = nc.Dataset(os.path.join(TEMP_DIR, "daily_temp_2016.nc"))
    era_lat = ds_ref.variables['latitude'][:]
    era_lon = ds_ref.variables['longitude'][:]
    ds_ref.close()

    ds = nc.Dataset(VPD_FILE)
    chm_lat = ds.variables['lat'][:]
    chm_lon = ds.variables['lon'][:]
    ds.close()

    lat_map = np.array([np.argmin(np.abs(chm_lat - elat)) for elat in era_lat])
    lon_map = np.array([np.argmin(np.abs(chm_lon - elon)) for elon in era_lon])

    return lat_map, lon_map


def doy_to_month_day(year, doy):
    """Convert DOY to (month, day_of_month)."""
    d = date(year, 1, 1) + pd.Timedelta(days=int(doy) - 1)
    return d.month, d.day


def month_doy_bounds(year, month):
    """Return (start_doy, end_doy) for a given month in a year."""
    start = date(year, month, 1)
    if month == 12:
        end = date(year, 12, 31)
    else:
        end = date(year, month + 1, 1) - pd.Timedelta(days=1)
    start_doy = (start - date(year, 1, 1)).days + 1
    end_doy = (end - date(year, 1, 1)).days + 1
    return start_doy, end_doy


def compute_window_month_weights(year, start_doy, end_doy):
    """Compute month weights for a window [start_doy, end_doy].

    Returns list of (month_index_0based, weight) tuples.
    month_index_0based: 0=Jan, 11=Dec
    """
    start_doy = max(1, int(start_doy))
    end_doy = min(366 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 365, int(end_doy))
    total_days = end_doy - start_doy + 1
    if total_days <= 0:
        return []

    weights = []
    for m in range(1, 13):
        m_start, m_end = month_doy_bounds(year, m)
        overlap_start = max(start_doy, m_start)
        overlap_end = min(end_doy, m_end)
        overlap = max(0, overlap_end - overlap_start + 1)
        if overlap > 0:
            weights.append((m - 1, overlap / total_days))  # 0-based month index

    return weights


def load_vpd_year(year, lat_map, lon_map):
    """Load monthly VPD for one year, aligned to ERA grid.

    VPD file: (744, 360, 640) = 62 years * 12 months, starting 1961.
    """
    ds = nc.Dataset(VPD_FILE)
    vpd_raw = ds.variables['VPD'][:]
    ds.close()

    vpd_raw = np.ma.filled(vpd_raw, np.nan).astype(np.float32)

    # Year offset: 1961 = index 0
    year_offset = (year - 1961) * 12
    vpd_year = vpd_raw[year_offset:year_offset + 12, :, :]  # (12, 360, 640)

    # Align to ERA grid
    vpd_aligned = vpd_year[:, lat_map, :][:, :, lon_map]  # (12, 376, 616)

    return vpd_aligned


def get_spei_slice(scale, year, end_month, lat_map, lon_map, cache):
    """Load a single 2D SPEI slice for (scale, year, end_month).

    Uses cache to avoid reopening the same NetCDF file.
    Returns aligned array of shape (REF_NLAT, REF_NLON).
    """
    if scale not in cache:
        fpath = os.path.join(SPEI_DIR, f"CHM_SPEI-{scale}.nc")
        cache[scale] = nc.Dataset(fpath)
    ds = cache[scale]
    var_name = f'SPEI-{scale}'
    time_idx = (year - 1961) * 12 + (end_month - 1)
    slice_2d = np.ma.filled(
        ds.variables[var_name][time_idx, :, :], np.nan
    ).astype(np.float32)
    return slice_2d[lat_map, :][:, lon_map]  # (REF_NLAT, REF_NLON)


def compute_spei_for_window(panel_yr, year, wname, suffix, nominal_prefix,
                            lat_map, lon_map, spei_cache):
    """Extract SPEI using v1 end-month logic for one window.

    For each grid cell:
      1. start_month, end_month from window DOY boundaries
      2. scale = end_month - start_month + 1 (per grid-year)
      3. Extract SPEI-{scale} at end_month
    _max = _mean (single extraction; no distributional max).
    """
    n = len(panel_yr)
    values = np.full(n, np.nan, dtype=np.float32)

    starts = panel_yr[f'win_{wname}_start'].values
    ends = panel_yr[f'win_{wname}_end'].values
    lat_idxs = panel_yr['lat_idx'].values.astype(int)
    lon_idxs = panel_yr['lon_idx'].values.astype(int)

    # Vectorized: DOY -> month
    valid = ~(np.isnan(starts) | np.isnan(ends))
    end_months = np.full(n, np.nan)
    start_months = np.full(n, np.nan)
    for i in np.where(valid)[0]:
        start_months[i] = doy_to_month_day(year, int(starts[i]))[0]
        end_months[i] = doy_to_month_day(year, int(ends[i]))[0]

    # Compute per-cell scale
    scales = np.full(n, np.nan)
    v = valid & ~(np.isnan(start_months) | np.isnan(end_months))
    # Normal case: start_month <= end_month
    normal = v & (start_months <= end_months)
    scales[normal] = end_months[normal] - start_months[normal] + 1
    # Cross-year case: start_month > end_month (defensive)
    cross = v & (start_months > end_months)
    scales[cross] = (12 - start_months[cross] + 1) + end_months[cross]
    # Clamp to [1, 12]
    scales[v] = np.clip(scales[v], 1, 12)

    # Group by unique (scale, end_month) and batch-extract
    pairs = np.column_stack([scales[v], end_months[v]])
    unique_pairs = np.unique(pairs, axis=0)

    for pair in unique_pairs:
        sc_int, em_int = int(pair[0]), int(pair[1])
        mask = v & (scales == sc_int) & (end_months == em_int)
        idxs = np.where(mask)[0]

        spei_slice = get_spei_slice(sc_int, year, em_int,
                                    lat_map, lon_map, spei_cache)
        values[idxs] = spei_slice[lat_idxs[idxs], lon_idxs[idxs]]

    return {
        f'{nominal_prefix}_mean{suffix}': values,
        f'{nominal_prefix}_max{suffix}': values.copy(),  # _max = _mean
    }


def process_monthly_window(panel_yr, monthly_3d, year, wname, suffix, prefix):
    """Weighted average of monthly data for one window (used for VPD only)."""
    n = len(panel_yr)
    result = {f'{prefix}_mean{suffix}': np.full(n, np.nan, dtype=np.float32),
              f'{prefix}_max{suffix}': np.full(n, np.nan, dtype=np.float32)}

    starts = panel_yr[f'win_{wname}_start'].values
    ends = panel_yr[f'win_{wname}_end'].values
    lat_idxs = panel_yr['lat_idx'].values.astype(int)
    lon_idxs = panel_yr['lon_idx'].values.astype(int)

    unique_pairs = np.unique(np.column_stack([starts, ends]), axis=0)

    for pair in unique_pairs:
        s_doy, e_doy = int(pair[0]), int(pair[1])
        weights = compute_window_month_weights(year, s_doy, e_doy)
        if not weights:
            continue

        mask = (starts == s_doy) & (ends == e_doy)
        cell_indices = np.where(mask)[0]
        li = lat_idxs[cell_indices]
        lj = lon_idxs[cell_indices]

        # Weighted mean
        weighted_sum = np.zeros(len(cell_indices), dtype=np.float32)
        max_val = np.full(len(cell_indices), -np.inf, dtype=np.float32)

        for m_idx, w in weights:
            month_vals = monthly_3d[m_idx, li, lj]  # (n_cells,)
            weighted_sum += np.where(np.isnan(month_vals), 0, month_vals * w)
            max_val = np.fmax(max_val, month_vals)

        result[f'{prefix}_mean{suffix}'][cell_indices] = weighted_sum
        max_val[max_val == -np.inf] = np.nan
        result[f'{prefix}_max{suffix}'][cell_indices] = max_val

    return result


def main():
    print("=" * 70)
    print("Step 06: VPD (Monthly Weighted) + SPEI (End-Month Extraction)")
    print("=" * 70)

    panel = pd.read_csv(os.path.join(INTERMEDIATE_DIR, "panel_windows.csv"))
    print(f"Panel: {len(panel)} rows")

    lat_map, lon_map = build_chm_alignment()

    # Show nominal SPEI prefixes
    for wname, prefix in SPEI_NOMINAL_PREFIX.items():
        print(f"  Window {wname}: nominal prefix = {prefix} (actual scale per grid-year)")

    all_dfs = []
    for year in YEARS:
        panel_yr = panel[panel['year'] == year].copy()
        print(f"\n  Year {year}: {len(panel_yr)} cells")
        t0 = timer.time()

        # Load VPD for this year
        vpd_12 = load_vpd_year(year, lat_map, lon_map)
        print(f"    VPD shape: {vpd_12.shape}")

        spei_cache = {}  # {scale: nc.Dataset} — reuse file handles within year
        all_results = {}
        for wname, wdef in WINDOWS.items():
            suffix = wdef['suffix']

            # VPD: monthly weighted average (unchanged)
            r_vpd = process_monthly_window(panel_yr, vpd_12, year,
                                           wname, suffix, 'vpd')
            all_results.update(r_vpd)

            # SPEI: v1-style end-month extraction
            r_spei = compute_spei_for_window(
                panel_yr, year, wname, suffix,
                SPEI_NOMINAL_PREFIX[wname], lat_map, lon_map, spei_cache
            )
            all_results.update(r_spei)

        # Close SPEI file handles
        for ds in spei_cache.values():
            ds.close()
        del vpd_12, spei_cache

        df_yr = pd.DataFrame(all_results, index=panel_yr.index)
        all_dfs.append(df_yr)
        print(f"    Total: {timer.time()-t0:.1f}s")

    df_vs = pd.concat(all_dfs).loc[panel.index]

    output = pd.concat([
        panel[['grid_id', 'year', 'latitude', 'longitude', 'lat_idx', 'lon_idx']],
        df_vs
    ], axis=1)

    outpath = os.path.join(INTERMEDIATE_DIR, "vpd_spei_windows.csv")
    output.to_csv(outpath, index=False)
    print(f"\nSaved: {outpath} ({len(output)} rows, {len(output.columns)} cols)")

    print("\nValidation (full season):")
    for v in output.columns:
        if v.startswith(('vpd_', 'spei')) and not v.endswith(('_v3pre30', '_v3pm10', '_hepm10', '_v3he', '_hema')):
            if v in output.columns:
                print(f"  {v}: mean={output[v].mean():.4f}, min={output[v].min():.4f}, max={output[v].max():.4f}")


if __name__ == "__main__":
    main()
