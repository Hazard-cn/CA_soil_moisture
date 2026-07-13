"""
s03_calc_precip_windows.py — 按物候窗口聚合降水变量
Purpose: Calculate precipitation statistics for each phenological window
Author: Data Build Pipeline
Date: 2026-03-28
Input: data/intermediate/panel_windows.csv, E:/CHM_PRE_0.1dg_19612022.nc
Output: data/intermediate/precip_windows.csv

Variables per window:
  - pr_sum, pr_mean, pr_max, pr_sd
  - drydays_lt1, wetdays_ge10, wetdays_ge20
  - max_cdd, max_cwd, pr_intensity
"""

import sys
import os
import numpy as np
import pandas as pd
import netCDF4 as nc
import time as timer
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

np.random.seed(RANDOM_SEED)


def build_chm_alignment():
    """Build 1D nearest-neighbor mapping from ERA grid indices to CHM grid indices."""
    print("  Building ERA -> CHM grid alignment...")

    # ERA grid
    ds_ref = nc.Dataset(os.path.join(TEMP_DIR, "daily_temp_2016.nc"))
    era_lat = ds_ref.variables['latitude'][:]
    era_lon = ds_ref.variables['longitude'][:]
    ds_ref.close()

    # CHM grid
    ds = nc.Dataset(PRECIP_FILE)
    chm_lat = ds.variables['latitude'][:]
    chm_lon = ds.variables['longitude'][:]
    ds.close()

    # 1D nearest-neighbor
    lat_map = np.array([np.argmin(np.abs(chm_lat - elat)) for elat in era_lat])
    lon_map = np.array([np.argmin(np.abs(chm_lon - elon)) for elon in era_lon])

    # Check max distance
    max_lat_dist = max(abs(chm_lat[lat_map[i]] - era_lat[i]) for i in range(len(era_lat)))
    max_lon_dist = max(abs(chm_lon[lon_map[i]] - era_lon[i]) for i in range(len(era_lon)))
    print(f"    Max lat offset: {max_lat_dist:.4f}°, Max lon offset: {max_lon_dist:.4f}°")

    return lat_map, lon_map, chm_lat, chm_lon


def load_precip_year(year, lat_map, lon_map):
    """Load daily precipitation for one year, aligned to ERA grid.

    CHM file: pre(time=22645, lat=360, lon=640), time in hours since 1961-01-01
    """
    print(f"    Loading precip for {year}...")
    ds = nc.Dataset(PRECIP_FILE)
    time_var = ds.variables['time'][:]

    # Find time indices for this year
    base = datetime(1961, 1, 1)
    start_h = (datetime(year, 1, 1) - base).total_seconds() / 3600
    end_h = (datetime(year, 12, 31) - base).total_seconds() / 3600
    tidx = np.where((time_var >= start_h) & (time_var <= end_h))[0]
    ndays = len(tidx)
    print(f"    Found {ndays} days for {year}")

    # Read data for this year: (ndays, 360, 640)
    pre_raw = ds.variables['pre'][tidx, :, :]
    ds.close()

    # Convert masked to NaN, replace fill value
    pre_raw = np.ma.filled(pre_raw, np.nan).astype(np.float32)
    pre_raw[pre_raw <= -99.0] = np.nan

    # Align to ERA grid: (ndays, 376, 616)
    # lat_map: ERA lat_idx -> CHM lat_idx, lon_map: ERA lon_idx -> CHM lon_idx
    pre_aligned = pre_raw[:, lat_map, :][:, :, lon_map]

    print(f"    Aligned shape: {pre_aligned.shape}, valid: {np.count_nonzero(~np.isnan(pre_aligned[0]))}")
    return pre_aligned


def max_consecutive_runs(condition_2d):
    """Max consecutive True runs along axis 0 for (time, n_cells) boolean array."""
    n_cells = condition_2d.shape[1]
    result = np.zeros(n_cells, dtype=np.int32)
    current = np.zeros(n_cells, dtype=np.int32)
    for t in range(condition_2d.shape[0]):
        active = condition_2d[t]
        current = np.where(active, current + 1, 0)
        result = np.maximum(result, current)
    return result


def process_window_precip(panel_yr, pr_3d, wname, suffix):
    """Process precipitation for one window, all cells."""
    ndays = pr_3d.shape[0]
    n = len(panel_yr)

    var_names = ['pr_sum', 'pr_mean', 'pr_max', 'pr_sd',
                 'drydays_lt1', 'wetdays_ge10', 'wetdays_ge20',
                 'max_cdd', 'max_cwd', 'pr_intensity']
    result = {f'{v}{suffix}': np.full(n, np.nan, dtype=np.float32) for v in var_names}

    starts = panel_yr[f'win_{wname}_start'].values
    ends = panel_yr[f'win_{wname}_end'].values
    lat_idxs = panel_yr['lat_idx'].values.astype(int)
    lon_idxs = panel_yr['lon_idx'].values.astype(int)

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

        pr = pr_3d[si:ei, li, lj]  # (win_days, n_cells)
        valid = ~np.isnan(pr)

        # Basic stats
        result[f'pr_sum{suffix}'][cell_indices] = np.nansum(pr, axis=0)
        result[f'pr_mean{suffix}'][cell_indices] = np.nanmean(pr, axis=0)
        result[f'pr_max{suffix}'][cell_indices] = np.nanmax(pr, axis=0)
        if pr.shape[0] > 1:
            result[f'pr_sd{suffix}'][cell_indices] = np.nanstd(pr, axis=0, ddof=1)

        # Dry/wet day counts
        dry = (pr < DRY_DAY_THRESHOLD) & valid
        result[f'drydays_lt1{suffix}'][cell_indices] = np.sum(dry, axis=0)

        for thresh in WET_DAY_THRESHOLDS:
            wet = (pr >= thresh) & valid
            result[f'wetdays_ge{thresh}{suffix}'][cell_indices] = np.sum(wet, axis=0)

        # Max consecutive dry/wet days
        wet_bool = (pr >= DRY_DAY_THRESHOLD) & valid
        dry_bool = (pr < DRY_DAY_THRESHOLD) & valid
        result[f'max_cdd{suffix}'][cell_indices] = max_consecutive_runs(dry_bool)
        result[f'max_cwd{suffix}'][cell_indices] = max_consecutive_runs(wet_bool)

        # Precipitation intensity
        wet_count = np.sum(wet_bool, axis=0).astype(np.float32)
        pr_wet = np.where(wet_bool, pr, 0)
        pr_wet_sum = np.nansum(pr_wet, axis=0)
        intensity = np.where(wet_count > 0, pr_wet_sum / wet_count, 0.0)
        result[f'pr_intensity{suffix}'][cell_indices] = intensity

    return result


def main():
    print("=" * 70)
    print("Step 03: Precipitation Window Aggregation")
    print("=" * 70)

    panel = pd.read_csv(os.path.join(INTERMEDIATE_DIR, "panel_windows.csv"))
    print(f"Panel: {len(panel)} rows")

    lat_map, lon_map, chm_lat, chm_lon = build_chm_alignment()

    all_dfs = []
    for year in YEARS:
        panel_yr = panel[panel['year'] == year].copy()
        print(f"\n  Year {year}: {len(panel_yr)} cells")
        t0 = timer.time()

        pr_3d = load_precip_year(year, lat_map, lon_map)

        all_results = {}
        for wname, wdef in WINDOWS.items():
            wt0 = timer.time()
            win_result = process_window_precip(panel_yr, pr_3d, wname, wdef['suffix'])
            all_results.update(win_result)
            print(f"    Window {wname}: {timer.time()-wt0:.1f}s")

        del pr_3d
        df_yr = pd.DataFrame(all_results, index=panel_yr.index)
        all_dfs.append(df_yr)
        print(f"    Total: {timer.time()-t0:.1f}s")

    df_precip = pd.concat(all_dfs).loc[panel.index]

    output = pd.concat([
        panel[['grid_id', 'year', 'latitude', 'longitude', 'lat_idx', 'lon_idx']],
        df_precip
    ], axis=1)

    outpath = os.path.join(INTERMEDIATE_DIR, "precip_windows.csv")
    output.to_csv(outpath, index=False)
    print(f"\nSaved: {outpath} ({len(output)} rows, {len(output.columns)} cols)")

    print("\nValidation (full season):")
    for v in ['pr_sum', 'pr_mean', 'pr_max', 'drydays_lt1', 'max_cdd', 'pr_intensity']:
        if v in output.columns:
            print(f"  {v}: mean={output[v].mean():.2f}, min={output[v].min():.2f}, max={output[v].max():.2f}")


if __name__ == "__main__":
    main()
