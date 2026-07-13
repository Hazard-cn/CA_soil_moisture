"""
s11_period_stats.py — Phenological period duration and date position statistics
Purpose: Generate summary statistics for phenological node dates and period lengths
Author: Data Build Pipeline
Date: 2026-04-03
Input: data/intermediate/panel_windows.csv
Output: output/tables/period_length_stats.csv
"""

import sys
import os
import numpy as np
import pandas as pd

np.random.seed(42)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *


def compute_summary(series):
    """Compute N, mean, sd, min, p25, median, p75, max for a series."""
    return pd.Series({
        'N': int(series.count()),
        'mean': series.mean(),
        'sd': series.std(),
        'min': series.min(),
        'p25': series.quantile(0.25),
        'median': series.median(),
        'p75': series.quantile(0.75),
        'max': series.max(),
    })


def main():
    print("=" * 70)
    print("Step 11: Phenological Period Duration & Date Position Statistics")
    print("=" * 70)

    # Load panel
    panel_path = os.path.join(INTERMEDIATE_DIR, "panel_windows.csv")
    df = pd.read_csv(panel_path)
    print(f"Panel: {len(df)} rows, {df['grid_id'].nunique()} grids, years {sorted(df['year'].unique())}")

    # Derive inter-node intervals
    df['v3_to_he'] = df['he_doy'] - df['v3_doy']
    df['he_to_ma'] = df['ma_doy'] - df['he_doy']
    df['v3_to_ma'] = df['ma_doy'] - df['v3_doy']

    # Variables to summarize
    vars_info = [
        # Phenological node positions (DOY)
        ('v3_doy',           'V3 (三叶期) DOY'),
        ('he_doy',           'HE (抽穗期) DOY'),
        ('ma_doy',           'MA (成熟期) DOY'),
        # Inter-node intervals (days)
        ('v3_to_he',         'V3→HE 营养生长期 (days)'),
        ('he_to_ma',         'HE→MA 灌浆成熟期 (days)'),
        ('v3_to_ma',         'V3→MA 全生长期 (days)'),
        # Window lengths (days)
        ('win_full_days',    '全生育期窗口 (days)'),
        ('win_v3pre30_days', 'V3前30天窗口 (days)'),
        ('win_v3pm10_days',  'V3±10窗口 (days)'),
        ('win_hepm10_days',  'HE±10窗口 (days)'),
        ('win_v3he_days',    'V3→HE窗口 (days)'),
        ('win_hema_days',    'HE→MA窗口 (days)'),
    ]

    # Compute overall + by-year stats
    rows = []
    for var, label in vars_info:
        if var not in df.columns:
            print(f"  WARNING: {var} not found, skipping")
            continue

        # Overall
        overall = compute_summary(df[var])

        # By year
        by_year = {}
        for yr in sorted(df['year'].unique()):
            by_year[str(yr)] = compute_summary(df[df['year'] == yr][var])

        # Build rows for each statistic
        for stat in ['N', 'mean', 'sd', 'min', 'p25', 'median', 'p75', 'max']:
            row = {
                'variable': var,
                'label': label,
                'statistic': stat,
                'overall': overall[stat],
            }
            for yr_str, yr_stats in by_year.items():
                row[yr_str] = yr_stats[stat]
            rows.append(row)

    result = pd.DataFrame(rows)

    # Save
    outpath = os.path.join(TABLE_DIR, "period_length_stats.csv")
    result.to_csv(outpath, index=False, encoding='utf-8-sig')
    print(f"\nSaved: {outpath} ({len(result)} rows)")

    # Print summary
    print("\n" + "=" * 70)
    print("Summary (Overall)")
    print("=" * 70)
    print(f"  {'Variable':<25s} {'Mean':>8s} {'SD':>8s} {'Min':>6s} {'P25':>6s} {'Med':>6s} {'P75':>6s} {'Max':>6s}")
    print("  " + "-" * 75)

    for var, label in vars_info:
        if var not in df.columns:
            continue
        s = df[var]
        print(f"  {var:<25s} {s.mean():>8.1f} {s.std():>8.1f} {s.min():>6.0f} "
              f"{s.quantile(0.25):>6.0f} {s.median():>6.0f} {s.quantile(0.75):>6.0f} {s.max():>6.0f}")

    # Year-by-year mean
    print("\n" + "=" * 70)
    print("Mean by Year")
    print("=" * 70)
    print(f"  {'Variable':<25s}", end="")
    for yr in sorted(df['year'].unique()):
        print(f" {yr:>10}", end="")
    print()
    print("  " + "-" * 65)

    for var, label in vars_info:
        if var not in df.columns:
            continue
        print(f"  {var:<25s}", end="")
        for yr in sorted(df['year'].unique()):
            m = df[df['year'] == yr][var].mean()
            print(f" {m:>10.1f}", end="")
        print()


if __name__ == "__main__":
    main()
