"""
pre_empirical_completeness.py — Data completeness and panel balance checks
Purpose: Validate panel structure, missing patterns, constant columns, ERA5-Land coverage,
         and effective sample sizes for planned regression specifications
Author: Data Build Pipeline
Date: 2026-03-29
Input: data/processed/data_v2_main.parquet (69,038 rows, 523 cols)
Output: output/tables/completeness_*.csv, output/figures/completeness_*.png
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

np.random.seed(RANDOM_SEED)


def check_panel_balance(df):
    """Check grid_id × year coverage and map spatial distribution."""
    print("\n" + "=" * 70)
    print("1. Panel Balance")
    print("=" * 70)

    # Count years per grid
    grid_years = df.groupby('grid_id')['year'].nunique().rename('n_years')
    year_dist = grid_years.value_counts().sort_index()
    n_grids = df['grid_id'].nunique()

    print(f"  Total grids: {n_grids:,}")
    print(f"  Year distribution:")
    for ny, cnt in year_dist.items():
        print(f"    {ny} years: {cnt:,} grids ({cnt/n_grids*100:.1f}%)")

    n_balanced = (grid_years == 4).sum()
    print(f"  Balanced (all 4 years): {n_balanced:,} / {n_grids:,} ({n_balanced/n_grids*100:.1f}%)")

    # Year-by-year count
    for y in YEARS:
        ny = df[df['year'] == y]['grid_id'].nunique()
        print(f"    {y}: {ny:,} grids")

    # Save balance table
    grid_loc = df.drop_duplicates('grid_id')[['grid_id', 'latitude', 'longitude']].set_index('grid_id')
    balance_df = grid_loc.join(grid_years)
    balance_df.to_csv(os.path.join(TABLE_DIR, 'completeness_panel_balance.csv'))

    # Spatial map
    fig, ax = plt.subplots(figsize=(12, 7))
    sc = ax.scatter(balance_df['longitude'], balance_df['latitude'],
                    c=balance_df['n_years'], cmap='RdYlGn', s=1, vmin=1, vmax=4)
    plt.colorbar(sc, ax=ax, label='Years with data', shrink=0.7)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title(f'Panel Balance: Grid-Year Coverage (N={n_grids:,} grids)')
    fig.savefig(os.path.join(FIG_DIR, 'completeness_grid_year_map.png'),
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: completeness_grid_year_map.png")


def check_missing_patterns(df):
    """Analyze cross-variable missing value correlations."""
    print("\n" + "=" * 70)
    print("2. Missing Value Patterns")
    print("=" * 70)

    # Key variables with known missing patterns
    miss_vars = [
        't2m_mean', 'tmax_mean', 'tmin_mean',
        'swsm_l1_mean', 'swsm_l3_mean',
        'era5l_swvl1_mean', 'era5l_swvl3_mean',
        'gleam_smrz_mean', 'gleam_sms_mean',
        'et0_mean', 'irr_frac',
        'bdod_0_5cm_01deg', 'crc_lag1',
        'pr_mean', 'aridity',
    ]
    miss_vars = [v for v in miss_vars if v in df.columns]

    # Missing counts
    print("\n  Per-variable missing:")
    for v in miss_vars:
        n_miss = df[v].isna().sum()
        if n_miss > 0:
            print(f"    {v:<30s}: {n_miss:>6,} ({n_miss/len(df)*100:.1f}%)")

    # Co-missingness matrix
    M = df[miss_vars].isna()
    n_miss_total = M.sum()
    miss_active = [v for v in miss_vars if n_miss_total[v] > 0]

    if len(miss_active) >= 2:
        M_active = M[miss_active]
        # Conditional co-missingness: P(miss B | miss A)
        co_miss = pd.DataFrame(index=miss_active, columns=miss_active, dtype=float)
        for a in miss_active:
            for b in miss_active:
                mask_a = M_active[a]
                if mask_a.sum() == 0:
                    co_miss.loc[a, b] = 0
                else:
                    co_miss.loc[a, b] = (M_active[b] & mask_a).sum() / mask_a.sum()

        print("\n  Co-missingness matrix (P(miss col | miss row)):")
        print(co_miss.to_string(float_format='{:.3f}'.format))

        co_miss.to_csv(os.path.join(TABLE_DIR, 'completeness_missing_patterns.csv'))

        # Heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(co_miss.values.astype(float), cmap='YlOrRd', vmin=0, vmax=1)
        ax.set_xticks(range(len(miss_active)))
        ax.set_yticks(range(len(miss_active)))
        short_labels = [v.replace('_mean', '').replace('_0_5cm_01deg', '') for v in miss_active]
        ax.set_xticklabels(short_labels, rotation=45, ha='right', fontsize=8)
        ax.set_yticklabels(short_labels, fontsize=8)
        # Annotate
        for i in range(len(miss_active)):
            for j in range(len(miss_active)):
                val = float(co_miss.iloc[i, j])
                color = 'white' if val > 0.6 else 'black'
                ax.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=7, color=color)
        plt.colorbar(im, ax=ax, label='P(miss col | miss row)', shrink=0.8)
        ax.set_title('Cross-Variable Missing Pattern Co-occurrence')
        fig.savefig(os.path.join(FIG_DIR, 'completeness_missing_heatmap.png'),
                    dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  Saved: completeness_missing_heatmap.png")

    # Identify the ~4,239 temperature-missing rows
    if 't2m_mean' in df.columns:
        temp_miss = df[df['t2m_mean'].isna()]
        print(f"\n  Temperature-missing rows: {len(temp_miss):,}")
        print(f"    Unique grids: {temp_miss['grid_id'].nunique()}")
        print(f"    Year distribution: {temp_miss['year'].value_counts().sort_index().to_dict()}")
        print(f"    Lat range: [{temp_miss['latitude'].min():.1f}, {temp_miss['latitude'].max():.1f}]")
        print(f"    Lon range: [{temp_miss['longitude'].min():.1f}, {temp_miss['longitude'].max():.1f}]")

        # Do temp-missing grids also miss SWSM?
        if 'swsm_l1_mean' in df.columns:
            both_miss = (df['t2m_mean'].isna() & df['swsm_l1_mean'].isna()).sum()
            print(f"    Also missing SWSM: {both_miss:,} / {len(temp_miss):,} ({both_miss/len(temp_miss)*100:.1f}%)")


def check_constant_columns(df):
    """Identify zero or near-zero variance columns."""
    print("\n" + "=" * 70)
    print("3. Constant / Near-Constant Columns")
    print("=" * 70)

    num_cols = df.select_dtypes(include=[np.number]).columns
    variances = df[num_cols].var()

    # Exactly constant (var < 1e-10)
    constant = variances[variances < 1e-10]
    near_constant = variances[(variances >= 1e-10) & (variances < 1e-6)]

    results = []
    print(f"\n  Exactly constant ({len(constant)} columns):")
    for col in constant.index:
        n_unique = df[col].nunique()
        mode_val = df[col].mode().iloc[0] if len(df[col].mode()) > 0 else np.nan
        print(f"    {col}: var={variances[col]:.2e}, n_unique={n_unique}, mode={mode_val}")
        results.append({'variable': col, 'variance': variances[col], 'n_unique': n_unique,
                        'mode': mode_val, 'type': 'constant'})

    print(f"\n  Near-constant ({len(near_constant)} columns):")
    for col in near_constant.index:
        n_unique = df[col].nunique()
        mode_val = df[col].mode().iloc[0] if len(df[col].mode()) > 0 else np.nan
        mode_frac = (df[col] == mode_val).mean() * 100
        print(f"    {col}: var={variances[col]:.2e}, n_unique={n_unique}, mode={mode_val} ({mode_frac:.1f}%)")
        results.append({'variable': col, 'variance': variances[col], 'n_unique': n_unique,
                        'mode': mode_val, 'type': 'near_constant'})

    pd.DataFrame(results).to_csv(os.path.join(TABLE_DIR, 'completeness_constant_cols.csv'), index=False)


def check_era5l_coverage(df):
    """Check ERA5-Land temporal coverage across windows."""
    print("\n" + "=" * 70)
    print("4. ERA5-Land Coverage")
    print("=" * 70)

    cov_cols = [c for c in df.columns if 'coverage' in c and 'era5l' in c]
    if not cov_cols:
        print("  No ERA5-Land coverage columns found.")
        return

    results = []
    for col in cov_cols:
        vals = df[col]
        n_lt1 = (vals < 1.0).sum()
        n_lt09 = (vals < 0.9).sum()
        n_lt05 = (vals < 0.5).sum()
        row = {
            'variable': col,
            'mean': vals.mean(),
            'min': vals.min(),
            'n_lt_1.0': n_lt1,
            'pct_lt_1.0': n_lt1 / len(df) * 100,
            'n_lt_0.9': n_lt09,
            'pct_lt_0.9': n_lt09 / len(df) * 100,
            'n_lt_0.5': n_lt05,
        }
        results.append(row)
        print(f"  {col}:")
        print(f"    mean={vals.mean():.4f}, min={vals.min():.4f}")
        print(f"    <1.0: {n_lt1:,} ({n_lt1/len(df)*100:.2f}%), <0.9: {n_lt09:,}, <0.5: {n_lt05:,}")

    pd.DataFrame(results).to_csv(os.path.join(TABLE_DIR, 'completeness_era5l_coverage.csv'), index=False)


def check_effective_sample_sizes(df):
    """Compute effective N for each planned regression specification."""
    print("\n" + "=" * 70)
    print("5. Effective Sample Sizes by Regression Specification")
    print("=" * 70)

    specs = {
        'Baseline (GLEAM)': [
            'ln_yield', 'ca', 'hdd_ge32', 'spei6_mean', 'pr_sum',
            'gleam_smrz_mean', 'irr_frac', 'gdd_ge10', 'et0_sum'
        ],
        'Baseline (SWSM)': [
            'ln_yield', 'ca', 'hdd_ge32', 'spei6_mean', 'pr_sum',
            'swsm_l3_mean', 'irr_frac', 'gdd_ge10', 'et0_sum'
        ],
        'Baseline (ERA5L)': [
            'ln_yield', 'ca', 'hdd_ge32', 'spei6_mean', 'pr_sum',
            'era5l_swvl3_mean', 'irr_frac', 'gdd_ge10', 'et0_sum'
        ],
        'Compound': [
            'ln_yield', 'ca', 'hdd_ge32', 'spei6_mean', 'pr_sum',
            'gleam_smrz_mean', 'irr_frac', 'gdd_ge10', 'et0_sum',
            'hotdrydays_ge32_smrz_p20'
        ],
        'Full controls': [
            'ln_yield', 'ca', 'hdd_ge32', 'spei6_mean', 'pr_sum',
            'gleam_smrz_mean', 'irr_frac', 'gdd_ge10', 'et0_sum',
            'vpd_mean', 'bdod_0_5cm_01deg', 'aridity'
        ],
        'Window V3-HE': [
            'ln_yield', 'ca', 'hdd_ge32_v3he', 'pr_sum_v3he',
            'gleam_smrz_mean_v3he', 'gdd_ge10_v3he', 'et0_sum_v3he'
        ],
        'Window HE-MA': [
            'ln_yield', 'ca', 'hdd_ge32_hema', 'pr_sum_hema',
            'gleam_smrz_mean_hema', 'gdd_ge10_hema', 'et0_sum_hema'
        ],
    }

    results = []
    N = len(df)
    for spec_name, vars_list in specs.items():
        existing = [v for v in vars_list if v in df.columns]
        missing_vars = [v for v in vars_list if v not in df.columns]

        if missing_vars:
            print(f"  WARNING: {spec_name} missing columns: {missing_vars}")

        n_complete = df[existing].dropna().shape[0]

        # Singleton check: grids with only 1 obs after dropping NAs
        complete_idx = df[existing].dropna().index
        df_complete = df.loc[complete_idx]
        grid_counts = df_complete.groupby('grid_id').size()
        singleton_grids = grid_counts[grid_counts == 1].index
        n_after_singleton = df_complete[~df_complete['grid_id'].isin(singleton_grids)].shape[0]

        row = {
            'specification': spec_name,
            'n_vars': len(vars_list),
            'n_complete': n_complete,
            'pct_complete': n_complete / N * 100,
            'n_singletons': len(singleton_grids),
            'n_after_singleton_drop': n_after_singleton,
            'pct_after_singleton': n_after_singleton / N * 100,
        }
        results.append(row)
        print(f"  {spec_name}:")
        print(f"    Complete: {n_complete:,} / {N:,} ({n_complete/N*100:.1f}%)")
        print(f"    After dropping {len(singleton_grids):,} singleton grids: {n_after_singleton:,} ({n_after_singleton/N*100:.1f}%)")

    res_df = pd.DataFrame(results)
    res_df.to_csv(os.path.join(TABLE_DIR, 'completeness_effective_N.csv'), index=False)
    print(f"\n  Saved: completeness_effective_N.csv")


def main():
    print("=" * 70)
    print("Pre-Empirical Completeness Check")
    print("=" * 70)

    df = pd.read_parquet(os.path.join(PROCESSED_DIR, 'data_v2_main.parquet'))
    print(f"Loaded: {len(df):,} rows, {len(df.columns)} cols")

    check_panel_balance(df)
    check_missing_patterns(df)
    check_constant_columns(df)
    check_era5l_coverage(df)
    check_effective_sample_sizes(df)

    print("\n" + "=" * 70)
    print("Completeness check complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
