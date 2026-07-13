"""
s01_load_phenology.py — 加载物候数据 + 构建格点-年份面板 + 定义窗口边界
Purpose: Create the master grid-year panel with phenological window definitions
Author: Data Build Pipeline
Date: 2026-03-28
Dependencies: config.py
Output: data/intermediate/panel_windows.parquet (or .csv)
"""

import sys
import os
import numpy as np
import pandas as pd
import netCDF4 as nc
from datetime import date

np.random.seed(42)

# Add scripts dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

def load_phenology_ca():
    """Load phenology DOY and CA ratio from MaizePheno_CA file."""
    print("[01] Loading phenology and CA data...")
    ds = nc.Dataset(PHEN_CA_FILE)

    years = ds.variables['year'][:]
    lat = ds.variables['latitude'][:]
    lon = ds.variables['longitude'][:]

    v3_doy = ds.variables['v3_doy'][:]    # (4, 376, 616)
    he_doy = ds.variables['he_doy'][:]
    ma_doy = ds.variables['ma_doy'][:]
    maize_frac = ds.variables['maize_frac'][:]
    ca_ratio = ds.variables['ca_ratio'][:]

    ds.close()

    print(f"  Grid: {lat.shape[0]} x {lon.shape[0]}")
    print(f"  Years: {years}")
    print(f"  v3_doy non-NaN per year: {[np.count_nonzero(~np.isnan(v3_doy[y])) for y in range(len(years))]}")

    return years, lat, lon, v3_doy, he_doy, ma_doy, maize_frac, ca_ratio


def build_panel(years, lat, lon, v3_doy, he_doy, ma_doy, maize_frac, ca_ratio):
    """Build grid-year panel from phenology arrays."""
    print("[01] Building grid-year panel...")

    rows = []
    for yi, year in enumerate(years):
        v3 = v3_doy[yi]
        he = he_doy[yi]
        ma = ma_doy[yi]
        mf = maize_frac[yi]
        ca = ca_ratio[yi]

        # Find valid grid cells (non-NaN phenology AND valid ordering)
        valid = (~np.isnan(v3)) & (~np.isnan(he)) & (~np.isnan(ma))
        valid &= (v3 < he) & (he < ma)  # phenological ordering
        valid &= (v3 > 0) & (ma < 366)  # reasonable DOY range

        lat_idx, lon_idx = np.where(valid)

        for i in range(len(lat_idx)):
            li, lj = lat_idx[i], lon_idx[i]
            rows.append({
                'year': int(year),
                'lat_idx': int(li),
                'lon_idx': int(lj),
                'latitude': float(lat[li]),
                'longitude': float(lon[lj]),
                'v3_doy': int(v3[li, lj]),
                'he_doy': int(he[li, lj]),
                'ma_doy': int(ma[li, lj]),
                'maize_frac': float(mf[li, lj]) if not np.isnan(mf[li, lj]) else np.nan,
                'ca_ratio': float(ca[li, lj]) if not np.isnan(ca[li, lj]) else np.nan,
            })

    df = pd.DataFrame(rows)

    # Create grid_id from lat/lon
    df['grid_id'] = df.groupby(['latitude', 'longitude']).ngroup() + 1

    print(f"  Total rows: {len(df)}")
    print(f"  Unique grids: {df['grid_id'].nunique()}")
    print(f"  Years: {sorted(df['year'].unique())}")

    return df


def define_windows(df):
    """Calculate window boundaries (start_doy, end_doy) for each window type."""
    print("[01] Defining phenological windows...")

    # Full season: v3_doy - 30 to ma_doy
    df['win_full_start'] = df['v3_doy'] - 30
    df['win_full_end'] = df['ma_doy']

    # Scheme A: ±10 days around nodes
    df['win_v3pm10_start'] = df['v3_doy'] - WINDOW_PM_DAYS
    df['win_v3pm10_end'] = df['v3_doy'] + WINDOW_PM_DAYS

    df['win_hepm10_start'] = df['he_doy'] - WINDOW_PM_DAYS
    df['win_hepm10_end'] = df['he_doy'] + WINDOW_PM_DAYS

    # Pre-V3 window: 30 days before V3
    df['win_v3pre30_start'] = df['v3_doy'] - 30
    df['win_v3pre30_end'] = df['v3_doy']

    # Scheme B: between nodes
    df['win_v3he_start'] = df['v3_doy']
    df['win_v3he_end'] = df['he_doy']

    df['win_hema_start'] = df['he_doy']
    df['win_hema_end'] = df['ma_doy']

    # Compute window lengths for validation
    for wname in WINDOWS:
        start_col = f'win_{wname}_start'
        end_col = f'win_{wname}_end'
        df[f'win_{wname}_days'] = df[end_col] - df[start_col] + 1

    # Clip DOY to valid range [1, 366]
    for col in df.columns:
        if col.startswith('win_') and (col.endswith('_start') or col.endswith('_end')):
            df[col] = df[col].clip(1, 366)

    # Print summary
    for wname, wdef in WINDOWS.items():
        days_col = f'win_{wname}_days'
        print(f"  {wname}: mean={df[days_col].mean():.1f} days, "
              f"range=[{df[days_col].min()}, {df[days_col].max()}]")

    return df


def validate_panel(df):
    """Run basic quality checks on the panel."""
    print("[01] Validating panel...")

    checks = []

    # 1. Phenological ordering
    ordering_ok = ((df['v3_doy'] < df['he_doy']) & (df['he_doy'] < df['ma_doy'])).all()
    checks.append(('Phenology ordering (V3 < HE < MA)', ordering_ok))

    # 2. DOY ranges
    v3_range = (df['v3_doy'].between(30, 220)).all()
    checks.append(('V3 DOY in [30, 220]', v3_range))

    he_range = (df['he_doy'].between(80, 280)).all()
    checks.append(('HE DOY in [80, 280]', he_range))

    ma_range = (df['ma_doy'].between(120, 340)).all()
    checks.append(('MA DOY in [120, 340]', ma_range))

    # 3. Window days positive
    for wname in WINDOWS:
        days_col = f'win_{wname}_days'
        pos = (df[days_col] > 0).all()
        checks.append((f'{wname} window days > 0', pos))

    # 4. ±10 windows = 21 days
    v3_21 = (df['win_v3pm10_days'] == 21).mean()
    checks.append((f'V3±10 = 21 days ({v3_21:.1%})', v3_21 > 0.95))

    he_21 = (df['win_hepm10_days'] == 21).mean()
    checks.append((f'HE±10 = 21 days ({he_21:.1%})', he_21 > 0.95))

    v3pre30_31 = (df['win_v3pre30_days'] == 31).mean()
    checks.append((f'V3pre30 = 31 days ({v3pre30_31:.1%})', v3pre30_31 > 0.95))

    # 5. No duplicate grid-year
    no_dup = df.duplicated(subset=['grid_id', 'year']).sum() == 0
    checks.append(('No duplicate grid-year', no_dup))

    all_pass = True
    for desc, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}")
        if not passed:
            all_pass = False

    return all_pass


def main():
    print("=" * 70)
    print("Step 01: Load Phenology & Build Panel Windows")
    print("=" * 70)

    # Load raw data
    years, lat, lon, v3_doy, he_doy, ma_doy, maize_frac, ca_ratio = load_phenology_ca()

    # Build panel
    df = build_panel(years, lat, lon, v3_doy, he_doy, ma_doy, maize_frac, ca_ratio)

    # Define windows
    df = define_windows(df)

    # Validate
    all_pass = validate_panel(df)

    # Save
    outpath = os.path.join(INTERMEDIATE_DIR, "panel_windows.csv")
    df.to_csv(outpath, index=False)
    print(f"\n[01] Saved: {outpath} ({len(df)} rows, {len(df.columns)} cols)")

    # Summary stats
    print(f"\n[01] Summary:")
    print(f"  Rows: {len(df)}")
    print(f"  Grids: {df['grid_id'].nunique()}")
    print(f"  Years: {sorted(df['year'].unique())}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Validation: {'ALL PASS' if all_pass else 'SOME FAILED'}")

    return df


if __name__ == "__main__":
    df = main()
