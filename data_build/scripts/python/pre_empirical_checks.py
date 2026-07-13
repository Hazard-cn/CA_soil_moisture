"""
pre_empirical_checks.py — Pre-empirical diagnostic checks
Purpose: Within/between variance decomposition, multicollinearity, distributions,
         outliers, temporal trends, and spatial coverage for regression design
Author: Data Build Pipeline
Date: 2026-03-29
Input: data/processed/data_v2_main.parquet (69,038 rows, 523 cols)
Output: output/tables/*.csv, output/figures/*.png
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats as sp_stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

np.random.seed(RANDOM_SEED)

KEY_VARS = [
    'yield_tons_ha', 'ln_yield', 'ca', 'crc_ca_ratio',
    't2m_mean', 'tmax_mean', 'pr_sum',
    'gleam_smrz_mean', 'swsm_l3_mean', 'era5l_swvl3_mean',
    'hotdays_ge32', 'hdd_ge32', 'hdd_ge35', 'gdd_ge10',
    'drydays_lt1', 'max_cdd', 'et0_sum', 'vpd_mean', 'spei6_mean',
    'hotdrydays_ge32_smrz_p20', 'irr_frac',
]


def within_between_decomposition(df):
    """Decompose total variance into between-grid and within-grid components."""
    print("\n" + "=" * 70)
    print("1. Within-Between Variance Decomposition")
    print("=" * 70)

    vars_list = [v for v in KEY_VARS if v in df.columns]
    results = []

    print(f"\n  {'Variable':<30s} {'Var_total':>10s} {'Var_betw':>10s} {'Var_with':>10s} "
          f"{'Within%':>8s} {'ICC':>6s} {'Var_2way':>10s} {'2way%':>7s}")
    print("  " + "-" * 95)

    for var in vars_list:
        s = df[['grid_id', 'year', var]].dropna()
        if len(s) < 10:
            continue

        var_total = s[var].var()
        if var_total == 0:
            continue

        # Within-grid (demean by grid)
        within_grid = s[var] - s.groupby('grid_id')[var].transform('mean')
        var_within = within_grid.var()

        # Between-grid
        var_between = var_total - var_within

        # Two-way FE residual (demean by grid AND year)
        grand_mean = s[var].mean()
        grid_mean = s.groupby('grid_id')[var].transform('mean')
        year_mean = s.groupby('year')[var].transform('mean')
        residual_2way = s[var] - grid_mean - year_mean + grand_mean
        var_2way = residual_2way.var()

        within_pct = var_within / var_total * 100
        icc = var_between / var_total
        twoway_pct = var_2way / var_total * 100

        results.append({
            'variable': var,
            'var_total': var_total,
            'var_between': var_between,
            'var_within': var_within,
            'within_pct': within_pct,
            'icc': icc,
            'var_2way_residual': var_2way,
            'twoway_pct': twoway_pct,
        })
        print(f"  {var:<30s} {var_total:>10.4f} {var_between:>10.4f} {var_within:>10.4f} "
              f"{within_pct:>7.1f}% {icc:>5.3f} {var_2way:>10.4f} {twoway_pct:>6.1f}%")

    res_df = pd.DataFrame(results)
    res_df.to_csv(os.path.join(TABLE_DIR, 'within_between_decomposition.csv'), index=False)

    # Flag low within-variation
    low_within = res_df[res_df['within_pct'] < 15]
    if len(low_within) > 0:
        print(f"\n  WARNING: {len(low_within)} variables with <15% within-grid variation:")
        for _, r in low_within.iterrows():
            print(f"    {r['variable']}: {r['within_pct']:.1f}% (poorly identified under grid FE)")

    # Bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    res_sorted = res_df.sort_values('within_pct')
    y_pos = range(len(res_sorted))
    bars_within = ax.barh(y_pos, res_sorted['within_pct'], color='steelblue', label='Within-grid')
    bars_between = ax.barh(y_pos, 100 - res_sorted['within_pct'],
                           left=res_sorted['within_pct'], color='lightcoral', label='Between-grid')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(res_sorted['variable'], fontsize=8)
    ax.set_xlabel('Share of Total Variance (%)')
    ax.set_title('Within vs Between Grid Variance Decomposition')
    ax.legend(loc='lower right')
    ax.axvline(x=50, color='grey', ls='--', alpha=0.5)
    ax.set_xlim(0, 100)
    fig.savefig(os.path.join(FIG_DIR, 'within_between_barplot.png'),
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"\n  Saved: within_between_barplot.png")


def multicollinearity_check(df):
    """Check VIF for baseline regressors and correlation matrices for variable groups."""
    print("\n" + "=" * 70)
    print("2. Multicollinearity Check")
    print("=" * 70)

    # --- Group A: Baseline regressors (VIF) ---
    group_a = ['hdd_ge32', 'spei6_mean', 'pr_sum', 'gleam_smrz_mean',
               'et0_sum', 'gdd_ge10', 'irr_frac', 'ca']
    group_a = [v for v in group_a if v in df.columns]

    print(f"\n  Group A (Baseline regressors) — VIF:")
    X = df[group_a].dropna().values
    if len(X) > 100:
        # Standardize
        X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-10)
        vifs = {}
        for i in range(X.shape[1]):
            y = X[:, i]
            others = np.delete(X, i, axis=1)
            others = np.column_stack([np.ones(len(y)), others])
            beta, _, _, _ = np.linalg.lstsq(others, y, rcond=None)
            yhat = others @ beta
            ss_res = ((y - yhat) ** 2).sum()
            ss_tot = ((y - y.mean()) ** 2).sum()
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            vifs[group_a[i]] = 1 / (1 - r2) if r2 < 1 else np.inf

        for var, vif in sorted(vifs.items(), key=lambda x: -x[1]):
            flag = " *** HIGH" if vif > 10 else (" * moderate" if vif > 5 else "")
            print(f"    {var:<25s} VIF = {vif:>8.2f}{flag}")

        vif_df = pd.DataFrame([{'variable': k, 'VIF': v} for k, v in vifs.items()])
        vif_df.to_csv(os.path.join(TABLE_DIR, 'multicollinearity_vif.csv'), index=False)

    # --- Group B: Heat variants (correlation) ---
    group_b = ['hdd_ge29', 'hdd_ge30', 'hdd_ge32', 'hdd_ge35',
               'hotdays_ge29', 'hotdays_ge32', 'hotdays_ge35', 'hotdays_ge_basep90']
    group_b = [v for v in group_b if v in df.columns]
    print(f"\n  Group B (Heat variants) — Pairwise correlations:")
    corr_b = df[group_b].corr()
    # Print pairs with |r| > 0.8
    for i in range(len(group_b)):
        for j in range(i + 1, len(group_b)):
            r = corr_b.iloc[i, j]
            flag = " *** HIGH" if abs(r) > 0.9 else (" * >0.8" if abs(r) > 0.8 else "")
            if flag:
                print(f"    {group_b[i]} vs {group_b[j]}: r={r:.4f}{flag}")
    corr_b.to_csv(os.path.join(TABLE_DIR, 'correlation_matrix_heat.csv'))

    # --- Group C: SM sources (correlation) ---
    group_c = ['gleam_smrz_mean', 'gleam_sms_mean', 'swsm_l1_mean',
               'swsm_l3_mean', 'era5l_swvl1_mean', 'era5l_swvl3_mean']
    group_c = [v for v in group_c if v in df.columns]
    print(f"\n  Group C (SM sources) — Pairwise correlations:")
    corr_c = df[group_c].corr()
    for i in range(len(group_c)):
        for j in range(i + 1, len(group_c)):
            r = corr_c.iloc[i, j]
            print(f"    {group_c[i]:<25s} vs {group_c[j]:<25s}: r={r:.4f}")
    corr_c.to_csv(os.path.join(TABLE_DIR, 'correlation_matrix_sm.csv'))

    # --- Group D: Water balance (correlation) ---
    group_d = ['pr_sum', 'drydays_lt1', 'max_cdd', 'wd_deficit',
               'spei6_mean', 'vpd_mean', 'et0_sum']
    group_d = [v for v in group_d if v in df.columns]
    print(f"\n  Group D (Water balance) — High correlations (|r|>0.6):")
    corr_d = df[group_d].corr()
    for i in range(len(group_d)):
        for j in range(i + 1, len(group_d)):
            r = corr_d.iloc[i, j]
            if abs(r) > 0.6:
                print(f"    {group_d[i]:<20s} vs {group_d[j]:<20s}: r={r:.4f}")
    corr_d.to_csv(os.path.join(TABLE_DIR, 'correlation_matrix_water.csv'))


def distribution_diagnostics(df):
    """Compute skewness, kurtosis, and normality tests for key variables."""
    print("\n" + "=" * 70)
    print("3. Distribution Diagnostics")
    print("=" * 70)

    vars_list = [v for v in KEY_VARS if v in df.columns]
    results = []

    print(f"\n  {'Variable':<30s} {'Mean':>10s} {'SD':>10s} {'Skew':>8s} {'Kurt':>8s} {'JB_p':>10s} {'Flag':>15s}")
    print("  " + "-" * 95)

    for var in vars_list:
        vals = df[var].dropna().values
        if len(vals) < 10:
            continue
        skew = sp_stats.skew(vals)
        kurt = sp_stats.kurtosis(vals)
        jb_stat, jb_p = sp_stats.jarque_bera(vals)

        flags = []
        if abs(skew) > 2:
            flags.append('high_skew')
        if kurt > 7:
            flags.append('heavy_tails')
        flag_str = ', '.join(flags) if flags else ''

        results.append({
            'variable': var,
            'mean': np.mean(vals),
            'std': np.std(vals),
            'skewness': skew,
            'kurtosis': kurt,
            'jarque_bera_stat': jb_stat,
            'jarque_bera_p': jb_p,
            'flag': flag_str,
        })
        print(f"  {var:<30s} {np.mean(vals):>10.3f} {np.std(vals):>10.3f} "
              f"{skew:>8.3f} {kurt:>8.3f} {jb_p:>10.2e} {flag_str:>15s}")

    res_df = pd.DataFrame(results)
    res_df.to_csv(os.path.join(TABLE_DIR, 'distribution_diagnostics.csv'), index=False)

    # Histograms
    n_vars = len(vars_list)
    ncols = 5
    nrows = (n_vars + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(20, nrows * 3))
    axes = axes.flatten()

    for i, var in enumerate(vars_list):
        vals = df[var].dropna().values
        axes[i].hist(vals, bins=50, color='steelblue', edgecolor='none', alpha=0.8)
        axes[i].set_title(var, fontsize=9)
        axes[i].tick_params(labelsize=7)
        skew = sp_stats.skew(vals)
        axes[i].text(0.95, 0.95, f'skew={skew:.2f}', transform=axes[i].transAxes,
                     ha='right', va='top', fontsize=7, color='red' if abs(skew) > 2 else 'black')

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle('Distribution of Key Variables', fontsize=13, y=1.01)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'distribution_histograms.png'),
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"\n  Saved: distribution_histograms.png")


def outlier_detection(df):
    """Count outliers by ±3SD and IQR methods."""
    print("\n" + "=" * 70)
    print("4. Outlier Detection")
    print("=" * 70)

    vars_list = [v for v in KEY_VARS if v in df.columns]
    results = []

    print(f"\n  {'Variable':<30s} {'N':>7s} {'3SD_out':>8s} {'3SD%':>7s} {'IQR_out':>8s} {'IQR%':>7s}")
    print("  " + "-" * 70)

    for var in vars_list:
        vals = df[var].dropna()
        n = len(vals)
        if n < 10:
            continue

        # ±3 SD
        mean, std = vals.mean(), vals.std()
        n_3sd = ((vals < mean - 3 * std) | (vals > mean + 3 * std)).sum()

        # IQR
        q1, q3 = vals.quantile(0.25), vals.quantile(0.75)
        iqr = q3 - q1
        n_iqr = ((vals < q1 - 1.5 * iqr) | (vals > q3 + 1.5 * iqr)).sum()

        results.append({
            'variable': var,
            'n_valid': n,
            'n_outlier_3sd': int(n_3sd),
            'pct_3sd': n_3sd / n * 100,
            'n_outlier_iqr': int(n_iqr),
            'pct_iqr': n_iqr / n * 100,
        })
        print(f"  {var:<30s} {n:>7,} {int(n_3sd):>8,} {n_3sd/n*100:>6.2f}% {int(n_iqr):>8,} {n_iqr/n*100:>6.2f}%")

    pd.DataFrame(results).to_csv(os.path.join(TABLE_DIR, 'outlier_counts.csv'), index=False)


def temporal_trends(df):
    """Check year-by-year means and simple trends."""
    print("\n" + "=" * 70)
    print("5. Temporal Trends")
    print("=" * 70)

    vars_list = [v for v in KEY_VARS if v in df.columns]
    results = []

    print(f"\n  {'Variable':<28s} {'2016':>10s} {'2017':>10s} {'2018':>10s} {'2019':>10s} {'Slope':>10s} {'p-val':>8s}")
    print("  " + "-" * 85)

    for var in vars_list:
        yr_means = df.groupby('year')[var].mean()
        means = {y: yr_means.get(y, np.nan) for y in YEARS}

        # Simple linear trend
        x = np.array(YEARS, dtype=float)
        y = np.array([means[yr] for yr in YEARS])
        valid = ~np.isnan(y)
        if valid.sum() >= 3:
            slope, intercept, r_value, p_value, std_err = sp_stats.linregress(x[valid], y[valid])
        else:
            slope, p_value = np.nan, np.nan

        results.append({
            'variable': var,
            'mean_2016': means[2016],
            'mean_2017': means[2017],
            'mean_2018': means[2018],
            'mean_2019': means[2019],
            'trend_slope': slope,
            'trend_pvalue': p_value,
        })
        print(f"  {var:<28s} {means[2016]:>10.3f} {means[2017]:>10.3f} "
              f"{means[2018]:>10.3f} {means[2019]:>10.3f} {slope:>10.4f} {p_value:>8.4f}")

    res_df = pd.DataFrame(results)
    res_df.to_csv(os.path.join(TABLE_DIR, 'temporal_trends.csv'), index=False)

    # Plot: normalize to 2016=100
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    var_groups = [
        ('Yield & SR', ['yield_tons_ha', 'ca', 'irr_frac']),
        ('Temperature & Heat', ['t2m_mean', 'tmax_mean', 'hotdays_ge32', 'hdd_ge32']),
        ('Water', ['pr_sum', 'drydays_lt1', 'spei6_mean', 'vpd_mean']),
        ('Soil Moisture', ['gleam_smrz_mean', 'swsm_l3_mean', 'era5l_swvl3_mean']),
    ]

    for ax, (title, gvars) in zip(axes.flatten(), var_groups):
        for var in gvars:
            if var not in df.columns:
                continue
            yr_means = df.groupby('year')[var].mean()
            base = yr_means.get(2016, np.nan)
            if base != 0 and not np.isnan(base):
                normed = yr_means / base * 100
                ax.plot(YEARS, [normed.get(y, np.nan) for y in YEARS], 'o-', label=var, markersize=4)
        ax.set_title(title, fontsize=11)
        ax.set_xlabel('Year')
        ax.set_ylabel('Index (2016=100)')
        ax.legend(fontsize=7, loc='best')
        ax.axhline(y=100, color='grey', ls='--', alpha=0.5)
        ax.set_xticks(YEARS)

    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'temporal_trends.png'),
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"\n  Saved: temporal_trends.png")


def spatial_coverage_map(df):
    """Three-panel spatial map: data completeness, mean yield, mean CA."""
    print("\n" + "=" * 70)
    print("6. Spatial Coverage Map")
    print("=" * 70)

    fig, axes = plt.subplots(1, 3, figsize=(20, 6))

    # Panel 1: Years with complete baseline data
    baseline_vars = ['ln_yield', 'ca', 'hdd_ge32', 'pr_sum', 'gleam_smrz_mean', 'irr_frac']
    baseline_vars = [v for v in baseline_vars if v in df.columns]
    df_tmp = df.copy()
    df_tmp['complete'] = df_tmp[baseline_vars].notna().all(axis=1).astype(int)
    grid_complete = df_tmp.groupby('grid_id').agg(
        n_complete=('complete', 'sum'),
        lat=('latitude', 'first'),
        lon=('longitude', 'first'),
    )
    sc1 = axes[0].scatter(grid_complete['lon'], grid_complete['lat'],
                          c=grid_complete['n_complete'], cmap='RdYlGn', s=1, vmin=0, vmax=4)
    plt.colorbar(sc1, ax=axes[0], label='Years with complete data', shrink=0.7)
    axes[0].set_title('Baseline Specification: Complete Cases')

    # Panel 2: Mean yield
    grid_yield = df.groupby('grid_id').agg(
        mean_yield=('yield_tons_ha', 'mean'),
        lat=('latitude', 'first'),
        lon=('longitude', 'first'),
    )
    sc2 = axes[1].scatter(grid_yield['lon'], grid_yield['lat'],
                          c=grid_yield['mean_yield'], cmap='YlGn', s=1, vmin=0, vmax=15)
    plt.colorbar(sc2, ax=axes[1], label='Mean yield (t/ha)', shrink=0.7)
    axes[1].set_title('Mean Maize Yield (2016-2019)')

    # Panel 3: Mean CA
    grid_ca = df.groupby('grid_id').agg(
        mean_ca=('ca', 'mean'),
        lat=('latitude', 'first'),
        lon=('longitude', 'first'),
    )
    sc3 = axes[2].scatter(grid_ca['lon'], grid_ca['lat'],
                          c=grid_ca['mean_ca'], cmap='YlOrRd', s=1, vmin=0, vmax=1)
    plt.colorbar(sc3, ax=axes[2], label='Mean CA adoption', shrink=0.7)
    axes[2].set_title('Mean Straw Return Adoption (2016-2019)')

    for ax in axes:
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'spatial_coverage_map.png'),
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: spatial_coverage_map.png")


def main():
    print("=" * 70)
    print("Pre-Empirical Diagnostic Checks")
    print("=" * 70)

    df = pd.read_parquet(os.path.join(PROCESSED_DIR, 'data_v2_main.parquet'))
    print(f"Loaded: {len(df):,} rows, {len(df.columns)} cols")

    within_between_decomposition(df)
    multicollinearity_check(df)
    distribution_diagnostics(df)
    outlier_detection(df)
    temporal_trends(df)
    spatial_coverage_map(df)

    # Final summary
    print("\n" + "=" * 70)
    print("Summary of Key Findings")
    print("=" * 70)

    wb = pd.read_csv(os.path.join(TABLE_DIR, 'within_between_decomposition.csv'))
    low_within = wb[wb['within_pct'] < 15]
    if len(low_within) > 0:
        print(f"\n  Variables with <15% within-grid variation (poor FE identification):")
        for _, r in low_within.iterrows():
            print(f"    {r['variable']}: {r['within_pct']:.1f}%")

    vif_path = os.path.join(TABLE_DIR, 'multicollinearity_vif.csv')
    if os.path.exists(vif_path):
        vif = pd.read_csv(vif_path)
        high_vif = vif[vif['VIF'] > 5]
        if len(high_vif) > 0:
            print(f"\n  Variables with VIF > 5:")
            for _, r in high_vif.iterrows():
                print(f"    {r['variable']}: VIF={r['VIF']:.2f}")

    dist = pd.read_csv(os.path.join(TABLE_DIR, 'distribution_diagnostics.csv'))
    flagged = dist[dist['flag'].fillna('') != '']
    if len(flagged) > 0:
        print(f"\n  Distribution flags:")
        for _, r in flagged.iterrows():
            print(f"    {r['variable']}: {r['flag']} (skew={r['skewness']:.2f}, kurt={r['kurtosis']:.2f})")

    print("\n" + "=" * 70)
    print("Pre-empirical checks complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
