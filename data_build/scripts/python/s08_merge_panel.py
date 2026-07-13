"""
s08_merge_panel.py — Merge all intermediate files into final panel
Purpose: Combine window-aggregated climate variables with v1 annual/static variables
Author: Data Build Pipeline
Date: 2026-03-28
Input: data/intermediate/*.csv, v1 data
Output: data/processed/data_v3_phenowindows.csv
"""

import sys
import os
import numpy as np
import pandas as pd
import time as timer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

np.random.seed(RANDOM_SEED)


def main():
    print("=" * 70)
    print("Step 08: Merge All Intermediate Files into Final Panel")
    print("=" * 70)

    t0 = timer.time()

    # Load panel windows (master index)
    panel = pd.read_csv(os.path.join(INTERMEDIATE_DIR, "panel_windows.csv"))
    print(f"Panel: {len(panel)} rows, {len(panel.columns)} cols")

    # Load all intermediate files
    intermediates = {
        'temp': 'temp_windows.csv',
        'precip': 'precip_windows.csv',
        'sm_gleam': 'sm_gleam_windows.csv',
        'sm_gleam_rework': 'sm_gleam_rework_windows.csv',
        'sm_swsm': 'sm_swsm_windows.csv',
        'et0': 'et0_windows.csv',
        'vpd_spei': 'vpd_spei_windows.csv',
        'compound': 'compound_windows.csv',
        'sm_era5land': 'sm_era5land_windows.csv',
    }

    merge_keys = ['grid_id', 'year', 'latitude', 'longitude', 'lat_idx', 'lon_idx']

    merged = panel.copy()
    for name, fname in intermediates.items():
        fpath = os.path.join(INTERMEDIATE_DIR, fname)
        df = pd.read_csv(fpath)
        print(f"  {name}: {len(df)} rows, {len(df.columns)} cols")

        # Drop merge keys (already in panel), keep only new columns
        new_cols = [c for c in df.columns if c not in merge_keys]
        df_new = df[merge_keys + new_cols]

        merged = merged.merge(df_new, on=merge_keys, how='left')
        print(f"    After merge: {len(merged)} rows, {len(merged.columns)} cols")

    print(f"\n  Merged panel: {len(merged)} rows, {len(merged.columns)} cols")

    # Load v1 data for annual/static variables
    print("\n  Loading v1 data for annual/static variables...")
    v1_path = os.path.join(PARENT_DIR, "data/processed/analysis_main_sample.dta")
    v1 = pd.read_stata(v1_path)
    print(f"  v1: {len(v1)} rows, {len(v1.columns)} cols")

    # Identify v1 columns to bring in (annual + static, not climate)
    # Annual variables
    annual_vars = ['yield_tons_ha', 'ln_yield', 'ca', 'crc_ca_ratio', 'crc_lag1',
                   'irr_frac', 'maize_area_km2']
    # Static variables (v1 uses different naming)
    static_vars = ['bdod_0_5cm_01deg', 'clay_0_5cm_01deg', 'sand_0_5cm_01deg',
                   'silt_0_5cm_01deg', 'phh2o_0_5cm_01deg', 'aridity',
                   'pixel_area_km2']
    # FE keys
    fe_vars = ['prov_id', 'prov_year', 'prov_code', 'province',
               'county_name', 'county_code', 'city_name', 'city_code']

    v1_vars_to_merge = [v for v in annual_vars + static_vars + fe_vars
                        if v in v1.columns]
    print(f"  v1 variables to merge: {v1_vars_to_merge}")

    # v1 uses grid_id + year as key
    # Match on integer-rounded lat/lon to avoid float32 vs float64 precision issues
    if 'grid_id' in v1.columns and 'year' in v1.columns:
        v1['lat_int'] = (v1['latitude'] * 10).round().astype(int)
        v1['lon_int'] = (v1['longitude'] * 10).round().astype(int)
        merged['lat_int'] = (merged['latitude'] * 10).round().astype(int)
        merged['lon_int'] = (merged['longitude'] * 10).round().astype(int)

        v1_subset = v1[['lat_int', 'lon_int', 'year'] + v1_vars_to_merge].copy()
        v1_subset = v1_subset.drop_duplicates(subset=['lat_int', 'lon_int', 'year'])

        n_before = len(merged)
        merged = merged.merge(v1_subset, on=['lat_int', 'lon_int', 'year'], how='left')
        merged.drop(columns=['lat_int', 'lon_int'], inplace=True)
        print(f"  After v1 merge: {len(merged)} rows (was {n_before})")

        n_with_yield = merged['yield_tons_ha'].notna().sum() if 'yield_tons_ha' in merged.columns else 0
        print(f"  Rows with yield data: {n_with_yield} ({n_with_yield/len(merged)*100:.1f}%)")

    # Save
    merged.to_csv(PHENOWINDOWS_CSV, index=False)
    print(f"\nSaved: {PHENOWINDOWS_CSV}")
    print(f"  Rows: {len(merged)}")
    print(f"  Columns: {len(merged.columns)}")
    print(f"  Total time: {timer.time()-t0:.1f}s")

    # Column summary
    print(f"\nColumn categories:")
    window_suffixes = [wdef['suffix'] for wdef in WINDOWS.values() if wdef['suffix']]
    window_cols = [c for c in merged.columns if any(c.endswith(s) for s in window_suffixes)]
    fullseason_cols = [c for c in merged.columns if c not in window_cols and c not in merge_keys
                       and c not in v1_vars_to_merge and not c.startswith('win_')]
    print(f"  Identifiers: {len(merge_keys)}")
    print(f"  Window definitions: {len([c for c in merged.columns if c.startswith('win_')])}")
    print(f"  Full-season climate: {len(fullseason_cols)}")
    print(f"  Period-specific climate: {len(window_cols)}")
    print(f"  v1 annual/static: {len([c for c in v1_vars_to_merge if c in merged.columns])}")

    return merged


if __name__ == "__main__":
    merged = main()
