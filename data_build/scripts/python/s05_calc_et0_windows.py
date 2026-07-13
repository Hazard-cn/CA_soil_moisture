"""
s05_calc_et0_windows.py — ET0 by phenological window
Purpose: Calculate ET0 statistics (sum, mean) and water deficit for each window
Author: Data Build Pipeline
Date: 2026-03-28
Input: data/intermediate/panel_windows.csv, data/intermediate/precip_windows.csv, ET0 NetCDF
Output: data/intermediate/et0_windows.csv
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


def process_et0_window(panel_yr, et0_3d, wname, suffix):
    """Process ET0 for one window, all cells."""
    ndays = et0_3d.shape[0]
    n = len(panel_yr)

    var_names = ['et0_sum', 'et0_mean']
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

        et0 = et0_3d[si:ei, li, lj]  # (win_days, n_cells)

        result[f'et0_sum{suffix}'][cell_indices] = np.nansum(et0, axis=0)
        result[f'et0_mean{suffix}'][cell_indices] = np.nanmean(et0, axis=0)

    return result


def main():
    print("=" * 70)
    print("Step 05: ET0 Window Aggregation + Water Deficit")
    print("=" * 70)

    panel = pd.read_csv(os.path.join(INTERMEDIATE_DIR, "panel_windows.csv"))
    print(f"Panel: {len(panel)} rows")

    # Load precip for water deficit calculation
    precip_df = pd.read_csv(os.path.join(INTERMEDIATE_DIR, "precip_windows.csv"))
    print(f"Precip data: {len(precip_df)} rows")

    all_dfs = []
    for year in YEARS:
        panel_yr = panel[panel['year'] == year].copy()
        print(f"\n  Year {year}: {len(panel_yr)} cells")
        t0 = timer.time()

        # Load ET0
        fpath = os.path.join(ET0_DIR, f"agera5_et0_{year}_0.1deg.nc")
        ds = nc.Dataset(fpath)
        et0_3d = np.ma.filled(ds.variables['ET0'][:], np.nan).astype(np.float32)
        ds.close()
        print(f"    Loaded ET0: {et0_3d.shape}")

        all_results = {}
        for wname, wdef in WINDOWS.items():
            suffix = wdef['suffix']
            r = process_et0_window(panel_yr, et0_3d, wname, suffix)
            all_results.update(r)

        del et0_3d
        df_yr = pd.DataFrame(all_results, index=panel_yr.index)
        all_dfs.append(df_yr)
        print(f"    Total: {timer.time()-t0:.1f}s")

    df_et0 = pd.concat(all_dfs).loc[panel.index]

    # Compute water deficit: et0_sum - pr_sum for each window
    for wname, wdef in WINDOWS.items():
        suffix = wdef['suffix']
        et0_col = f'et0_sum{suffix}'
        pr_col = f'pr_sum{suffix}'
        wd_col = f'wd_deficit{suffix}'
        if et0_col in df_et0.columns and pr_col in precip_df.columns:
            df_et0[wd_col] = df_et0[et0_col].values - precip_df[pr_col].values

    output = pd.concat([
        panel[['grid_id', 'year', 'latitude', 'longitude', 'lat_idx', 'lon_idx']],
        df_et0
    ], axis=1)

    outpath = os.path.join(INTERMEDIATE_DIR, "et0_windows.csv")
    output.to_csv(outpath, index=False)
    print(f"\nSaved: {outpath} ({len(output)} rows, {len(output.columns)} cols)")

    print("\nValidation (full season):")
    for v in ['et0_sum', 'et0_mean', 'wd_deficit']:
        if v in output.columns:
            print(f"  {v}: mean={output[v].mean():.2f}, min={output[v].min():.2f}, max={output[v].max():.2f}")


if __name__ == "__main__":
    main()
