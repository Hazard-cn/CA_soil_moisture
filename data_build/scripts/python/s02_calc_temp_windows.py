"""
s02_calc_temp_windows.py — 按物候窗口聚合温度变量
Purpose: Calculate temperature statistics for each phenological window
Author: Data Build Pipeline
Date: 2026-03-28
Input: data/intermediate/panel_windows.csv, E:/daily_temp_CN/
Output: data/intermediate/temp_windows.csv

Variables per window:
  - t2m_mean, t2m_min, t2m_max, t2m_sd
  - tmax_mean, tmax_max, tmin_mean, tmin_min
  - dtr_mean, dtr_max (diurnal temperature range)
  - hotdays_ge{T} for T in [29..40]
  - hdd_ge{T} for T in [29..40]
  - hotdays_ge_basep90, hotdays_ge_basep95, hdd_ge_basep90, hdd_ge_basep95
  - nightheat_ge{T} for T in [20,22,24]
  - gdd_ge10
  - gdd_10_29, gdd_10_30, gdd_10_31, gdd_10_32
"""

import sys
import os
import numpy as np
import pandas as pd
import netCDF4 as nc
import time as timer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

np.random.seed(RANDOM_SEED)


def load_temp_year(year):
    """Load daily temperature for one year."""
    fpath = os.path.join(TEMP_DIR, f"daily_temp_{year}.nc")
    ds = nc.Dataset(fpath)
    t2m_max = np.ma.filled(ds.variables['t2m_max'][:], np.nan).astype(np.float32)
    t2m_min = np.ma.filled(ds.variables['t2m_min'][:], np.nan).astype(np.float32)
    t2m_mean = np.ma.filled(ds.variables['t2m_mean'][:], np.nan).astype(np.float32)
    ds.close()
    return t2m_mean, t2m_max, t2m_min


def compute_baseline_percentiles():
    """Compute Tmax p90/p95 per grid cell using growing season days from baseline years."""
    print("  Computing Tmax baseline percentiles (2013-2020)...")
    all_tmax = []
    for year in BASELINE_YEARS:
        fpath = os.path.join(TEMP_DIR, f"daily_temp_{year}.nc")
        if not os.path.exists(fpath):
            continue
        ds = nc.Dataset(fpath)
        tmax = np.ma.filled(ds.variables['t2m_max'][:], np.nan).astype(np.float32)
        ds.close()
        all_tmax.append(tmax[89:300, :, :])  # DOY 90-300 growing season

    stacked = np.concatenate(all_tmax, axis=0)
    p90 = np.nanpercentile(stacked, 90, axis=0)
    p95 = np.nanpercentile(stacked, 95, axis=0)
    del stacked, all_tmax
    print(f"    p90: [{np.nanmin(p90):.1f}, {np.nanmax(p90):.1f}], p95: [{np.nanmin(p95):.1f}, {np.nanmax(p95):.1f}]")
    return p90, p95


def _get_temp_var_names():
    """Return list of all temperature variable names (without window suffix)."""
    names = ['t2m_mean', 't2m_min', 't2m_max', 't2m_sd',
             'tmax_mean', 'tmax_max', 'tmin_mean', 'tmin_min',
             'dtr_mean', 'dtr_max']
    for t in HOT_ABS_THRESHOLDS:
        names.extend([f'hotdays_ge{t}', f'hdd_ge{t}'])
    names.extend(['hotdays_ge_basep90', 'hdd_ge_basep90',
                   'hotdays_ge_basep95', 'hdd_ge_basep95'])
    for t in NIGHTHEAT_THRESHOLDS:
        names.append(f'nightheat_ge{t}')
    names.append(LEGACY_GDD_VAR)
    names.extend(CAPPED_GDD_VARS)
    return names


def process_window_vectorized(panel_yr, t2m_mean_3d, t2m_max_3d, t2m_min_3d,
                               p90_2d, p95_2d, wname, suffix):
    """Process one window for all cells in a year using semi-vectorized approach.

    Groups cells by (start_doy, end_doy) to batch-process cells with same window.
    """
    ndays = t2m_mean_3d.shape[0]
    var_names = _get_temp_var_names()
    n = len(panel_yr)

    # Pre-allocate result arrays
    result = {f'{v}{suffix}': np.full(n, np.nan, dtype=np.float32) for v in var_names}

    start_col = f'win_{wname}_start'
    end_col = f'win_{wname}_end'

    starts = panel_yr[start_col].values
    ends = panel_yr[end_col].values
    lat_idxs = panel_yr['lat_idx'].values.astype(int)
    lon_idxs = panel_yr['lon_idx'].values.astype(int)

    # Group by unique (start, end) pairs for efficiency
    window_pairs = np.column_stack([starts, ends])
    unique_pairs = np.unique(window_pairs, axis=0)

    for pair in unique_pairs:
        s_doy, e_doy = int(pair[0]), int(pair[1])
        si = max(0, s_doy - 1)
        ei = min(ndays, e_doy)
        if si >= ei:
            continue

        # Find cells with this window
        mask = (starts == s_doy) & (ends == e_doy)
        cell_indices = np.where(mask)[0]
        li = lat_idxs[cell_indices]
        lj = lon_idxs[cell_indices]

        # Extract time slices for all these cells at once: (nwin_days, n_cells)
        t_mean = t2m_mean_3d[si:ei, li, lj]  # (win_days, n_cells)
        t_max = t2m_max_3d[si:ei, li, lj]
        t_min = t2m_min_3d[si:ei, li, lj]
        dtr = t_max - t_min

        # Basic stats (axis=0 = across time)
        result[f't2m_mean{suffix}'][cell_indices] = np.nanmean(t_mean, axis=0)
        result[f't2m_min{suffix}'][cell_indices] = np.nanmin(t_mean, axis=0)
        result[f't2m_max{suffix}'][cell_indices] = np.nanmax(t_mean, axis=0)
        if t_mean.shape[0] > 1:
            result[f't2m_sd{suffix}'][cell_indices] = np.nanstd(t_mean, axis=0, ddof=1)
        else:
            result[f't2m_sd{suffix}'][cell_indices] = 0.0

        result[f'tmax_mean{suffix}'][cell_indices] = np.nanmean(t_max, axis=0)
        result[f'tmax_max{suffix}'][cell_indices] = np.nanmax(t_max, axis=0)
        result[f'tmin_mean{suffix}'][cell_indices] = np.nanmean(t_min, axis=0)
        result[f'tmin_min{suffix}'][cell_indices] = np.nanmin(t_min, axis=0)

        result[f'dtr_mean{suffix}'][cell_indices] = np.nanmean(dtr, axis=0)
        result[f'dtr_max{suffix}'][cell_indices] = np.nanmax(dtr, axis=0)

        # Hotdays and HDD (absolute thresholds)
        for thresh in HOT_ABS_THRESHOLDS:
            hot = (t_max >= thresh).astype(np.float32)
            hot[np.isnan(t_max)] = 0
            result[f'hotdays_ge{thresh}{suffix}'][cell_indices] = np.sum(hot, axis=0)

            excess = np.maximum(t_max - thresh, 0)
            excess[np.isnan(t_max)] = 0
            result[f'hdd_ge{thresh}{suffix}'][cell_indices] = np.sum(excess, axis=0)

        # Percentile-based hotdays/HDD
        cell_p90 = p90_2d[li, lj]  # (n_cells,)
        cell_p95 = p95_2d[li, lj]

        for pname, pvals in [('basep90', cell_p90), ('basep95', cell_p95)]:
            # Broadcast: (win_days, n_cells) >= (n_cells,)
            hot_p = (t_max >= pvals[np.newaxis, :]).astype(np.float32)
            hot_p[np.isnan(t_max)] = 0
            result[f'hotdays_ge_{pname}{suffix}'][cell_indices] = np.sum(hot_p, axis=0)

            excess_p = np.maximum(t_max - pvals[np.newaxis, :], 0)
            excess_p[np.isnan(t_max)] = 0
            result[f'hdd_ge_{pname}{suffix}'][cell_indices] = np.sum(excess_p, axis=0)

        # Night heat
        for thresh in NIGHTHEAT_THRESHOLDS:
            nh = (t_min >= thresh).astype(np.float32)
            nh[np.isnan(t_min)] = 0
            result[f'nightheat_ge{thresh}{suffix}'][cell_indices] = np.sum(nh, axis=0)

        # GDD
        gdd_daily = np.maximum(t_mean - GDD_BASE_TEMP, 0)
        gdd_daily[np.isnan(t_mean)] = 0
        result[f'{LEGACY_GDD_VAR}{suffix}'][cell_indices] = np.sum(gdd_daily, axis=0)

        for cap, var_name in zip(GDD_UPPER_CAPS, CAPPED_GDD_VARS):
            gdd_capped_daily = np.maximum(np.minimum(t_mean, cap) - GDD_BASE_TEMP, 0)
            gdd_capped_daily[np.isnan(t_mean)] = 0
            result[f'{var_name}{suffix}'][cell_indices] = np.sum(gdd_capped_daily, axis=0)

    return result


def process_year(year, panel_yr, p90, p95):
    """Process all temperature windows for one year."""
    print(f"  Year {year}: {len(panel_yr)} cells...")
    t0 = timer.time()

    t2m_mean, t2m_max, t2m_min = load_temp_year(year)
    print(f"    Loaded {t2m_mean.shape[0]} days")

    all_results = {}
    for wname, wdef in WINDOWS.items():
        suffix = wdef['suffix']
        wt0 = timer.time()
        win_result = process_window_vectorized(
            panel_yr, t2m_mean, t2m_max, t2m_min, p90, p95, wname, suffix
        )
        all_results.update(win_result)
        print(f"    Window {wname}: {timer.time()-wt0:.1f}s")

    del t2m_mean, t2m_max, t2m_min

    df = pd.DataFrame(all_results, index=panel_yr.index)
    print(f"    Total: {timer.time()-t0:.1f}s")
    return df


def main():
    print("=" * 70)
    print("Step 02: Temperature Window Aggregation")
    print("=" * 70)

    panel = pd.read_csv(os.path.join(INTERMEDIATE_DIR, "panel_windows.csv"))
    print(f"Panel: {len(panel)} rows")

    p90, p95 = compute_baseline_percentiles()

    all_dfs = []
    for year in YEARS:
        panel_yr = panel[panel['year'] == year].copy()
        yr_df = process_year(year, panel_yr, p90, p95)
        all_dfs.append(yr_df)

    df_temp = pd.concat(all_dfs)
    df_temp = df_temp.loc[panel.index]

    # Merge identifiers
    output = pd.concat([
        panel[['grid_id', 'year', 'latitude', 'longitude', 'lat_idx', 'lon_idx']],
        df_temp
    ], axis=1)

    outpath = os.path.join(INTERMEDIATE_DIR, "temp_windows.csv")
    output.to_csv(outpath, index=False)
    print(f"\nSaved: {outpath} ({len(output)} rows, {len(output.columns)} cols)")

    # Quick validation
    print("\nValidation (full season, no suffix):")
    for v in ['t2m_mean', 'tmax_mean', 'hotdays_ge32', 'hdd_ge32',
              LEGACY_GDD_VAR, *CAPPED_GDD_VARS, 'dtr_mean']:
        if v in output.columns:
            print(f"  {v}: mean={output[v].mean():.2f}, min={output[v].min():.2f}, max={output[v].max():.2f}")

    print("\nValidation (V3±10):")
    for v in ['t2m_mean_v3pm10', 'hotdays_ge32_v3pm10', 'hdd_ge32_v3pm10',
              'gdd_ge10_v3pm10', 'gdd_10_29_v3pm10']:
        if v in output.columns:
            print(f"  {v}: mean={output[v].mean():.2f}, min={output[v].min():.2f}, max={output[v].max():.2f}")


if __name__ == "__main__":
    main()
