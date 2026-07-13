"""
compare_sm_sources.py — Three-source soil moisture comparison
Purpose: Compare GLEAM, SWSM, and ERA5-Land SM across windows, years, and space
Author: Data Build Pipeline
Date: 2026-03-29
Input: data/processed/data_v2_main.parquet (69,038 rows, main sample with yield)
Output: output/tables/sm_correlations_*.csv, output/figures/sm_*.png

SM source correspondence:
  Surface:   GLEAM SMs (~0-10cm) vs SWSM L1 (~surface) vs ERA5-Land swvl1 (0-7cm)
  Root zone: GLEAM SMrz (0-100cm) vs SWSM L3 (~30-60cm) vs ERA5-Land swvl3 (28-100cm)
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

np.random.seed(RANDOM_SEED)

# SM variable mapping
SM_SOURCES = {
    'surface': {
        'GLEAM SMs': 'gleam_sms',
        'SWSM L1': 'swsm_l1',
        'ERA5-Land swvl1': 'era5l_swvl1',
    },
    'rootzone': {
        'GLEAM SMrz': 'gleam_smrz',
        'SWSM L3': 'swsm_l3',
        'ERA5-Land swvl3': 'era5l_swvl3',
    }
}

WINDOW_SUFFIXES = {
    'Full season': '',
    'V3pre30': '_v3pre30',
    'V3±10': '_v3pm10',
    'HE±10': '_hepm10',
    'V3→HE': '_v3he',
    'HE→MA': '_hema',
}


def compute_correlations(df, layer='surface'):
    """Compute pairwise Pearson and Spearman correlations for one depth layer."""
    sources = SM_SOURCES[layer]
    names = list(sources.keys())
    prefixes = list(sources.values())

    results = []
    for wname, wsuffix in WINDOW_SUFFIXES.items():
        for i in range(len(prefixes)):
            for j in range(i + 1, len(prefixes)):
                col_i = f'{prefixes[i]}_mean{wsuffix}'
                col_j = f'{prefixes[j]}_mean{wsuffix}'
                if col_i not in df.columns or col_j not in df.columns:
                    continue
                valid = df[[col_i, col_j]].dropna()
                if len(valid) < 10:
                    continue
                pearson_r = valid[col_i].corr(valid[col_j])
                spearman_r, _ = stats.spearmanr(valid[col_i], valid[col_j])
                rmse = np.sqrt(((valid[col_i] - valid[col_j]) ** 2).mean())
                mad = (valid[col_i] - valid[col_j]).abs().mean()
                results.append({
                    'layer': layer,
                    'window': wname,
                    'source_1': names[i],
                    'source_2': names[j],
                    'n_valid': len(valid),
                    'pearson_r': pearson_r,
                    'spearman_r': spearman_r,
                    'rmse': rmse,
                    'mean_abs_diff': mad,
                    'mean_1': valid[col_i].mean(),
                    'mean_2': valid[col_j].mean(),
                })
    return pd.DataFrame(results)


def compute_correlations_by_year(df, layer='surface'):
    """Compute pairwise correlations by year."""
    sources = SM_SOURCES[layer]
    names = list(sources.keys())
    prefixes = list(sources.values())

    results = []
    for year in YEARS:
        df_yr = df[df['year'] == year]
        for wname, wsuffix in WINDOW_SUFFIXES.items():
            if wsuffix != '':  # Only full season for by-year
                continue
            for i in range(len(prefixes)):
                for j in range(i + 1, len(prefixes)):
                    col_i = f'{prefixes[i]}_mean{wsuffix}'
                    col_j = f'{prefixes[j]}_mean{wsuffix}'
                    if col_i not in df_yr.columns or col_j not in df_yr.columns:
                        continue
                    valid = df_yr[[col_i, col_j]].dropna()
                    if len(valid) < 10:
                        continue
                    pearson_r = valid[col_i].corr(valid[col_j])
                    results.append({
                        'layer': layer,
                        'year': year,
                        'source_1': names[i],
                        'source_2': names[j],
                        'n_valid': len(valid),
                        'pearson_r': pearson_r,
                    })
    return pd.DataFrame(results)


def plot_scatter_hexbin(df, layer='surface'):
    """Create hexbin scatter plots for all pairs (full season)."""
    sources = SM_SOURCES[layer]
    names = list(sources.keys())
    prefixes = list(sources.values())

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    pairs = [(0, 1), (0, 2), (1, 2)]

    for ax, (i, j) in zip(axes, pairs):
        col_i = f'{prefixes[i]}_mean'
        col_j = f'{prefixes[j]}_mean'
        valid = df[[col_i, col_j]].dropna()

        hb = ax.hexbin(valid[col_i], valid[col_j], gridsize=50, cmap='YlOrRd',
                        mincnt=1, linewidths=0.2)
        ax.plot([0, 0.7], [0, 0.7], 'k--', alpha=0.5, lw=1)
        ax.set_xlabel(names[i], fontsize=11)
        ax.set_ylabel(names[j], fontsize=11)
        r = valid[col_i].corr(valid[col_j])
        ax.set_title(f'r = {r:.4f} (n={len(valid):,})', fontsize=11)
        ax.set_xlim(0, 0.7)
        ax.set_ylim(0, 0.7)
        ax.set_aspect('equal')
        plt.colorbar(hb, ax=ax, shrink=0.8)

    layer_label = 'Surface' if layer == 'surface' else 'Root Zone'
    fig.suptitle(f'{layer_label} Soil Moisture: 3-Source Comparison (Full Season Mean)',
                 fontsize=13, y=1.02)
    plt.tight_layout()
    outpath = os.path.join(FIG_DIR, f'sm_scatter_{layer}.png')
    fig.savefig(outpath, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {outpath}")


def plot_corr_by_window(corr_df):
    """Bar chart of Pearson r by window for all pairs and layers."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for ax, layer in zip(axes, ['surface', 'rootzone']):
        sub = corr_df[corr_df['layer'] == layer].copy()
        sub['pair'] = sub['source_1'] + ' vs ' + sub['source_2']
        pairs = sub['pair'].unique()

        x = np.arange(len(WINDOW_SUFFIXES))
        width = 0.25
        for k, pair in enumerate(pairs):
            vals = sub[sub['pair'] == pair].set_index('window')['pearson_r']
            vals = vals.reindex(WINDOW_SUFFIXES.keys())
            ax.bar(x + k * width, vals.values, width, label=pair, alpha=0.85)

        ax.set_xticks(x + width)
        ax.set_xticklabels(WINDOW_SUFFIXES.keys(), rotation=15, ha='right')
        ax.set_ylabel('Pearson r')
        ax.set_title('Surface SM' if layer == 'surface' else 'Root Zone SM')
        ax.legend(fontsize=8)
        ax.set_ylim(0, 1)
        ax.axhline(y=0.9, color='grey', ls='--', alpha=0.5)

    plt.tight_layout()
    outpath = os.path.join(FIG_DIR, 'sm_corr_by_window.png')
    fig.savefig(outpath, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {outpath}")


def plot_spatial_correlation(df, layer='surface'):
    """Map of grid-level correlation between SM sources (full season)."""
    sources = SM_SOURCES[layer]
    names = list(sources.keys())
    prefixes = list(sources.values())
    pairs = [(0, 1), (0, 2), (1, 2)]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    for ax, (i, j) in zip(axes, pairs):
        col_i = f'{prefixes[i]}_mean'
        col_j = f'{prefixes[j]}_mean'

        # Compute per-grid correlation across years
        grid_corrs = df.groupby('grid_id').apply(
            lambda g: g[[col_i, col_j]].dropna().corr().iloc[0, 1]
            if len(g[[col_i, col_j]].dropna()) >= 3 else np.nan
        )
        # Merge back lat/lon
        grid_loc = df.drop_duplicates('grid_id')[['grid_id', 'latitude', 'longitude']].set_index('grid_id')
        grid_data = grid_loc.join(grid_corrs.rename('corr')).dropna()

        sc = ax.scatter(grid_data['longitude'], grid_data['latitude'],
                        c=grid_data['corr'], cmap='RdYlGn', s=1, vmin=-1, vmax=1)
        ax.set_title(f'{names[i]} vs {names[j]}', fontsize=11)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        plt.colorbar(sc, ax=ax, shrink=0.8, label='Pearson r')

    layer_label = 'Surface' if layer == 'surface' else 'Root Zone'
    fig.suptitle(f'{layer_label} SM: Grid-level Temporal Correlation (2016-2019)',
                 fontsize=13, y=1.02)
    plt.tight_layout()
    outpath = os.path.join(FIG_DIR, f'sm_spatial_corr_{layer}.png')
    fig.savefig(outpath, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {outpath}")


def descriptive_summary(df):
    """Summary statistics for all SM sources."""
    rows = []
    for layer, sources in SM_SOURCES.items():
        for sname, prefix in sources.items():
            col = f'{prefix}_mean'
            if col not in df.columns:
                continue
            vals = df[col]
            rows.append({
                'layer': layer,
                'source': sname,
                'variable': col,
                'n': vals.notna().sum(),
                'mean': vals.mean(),
                'std': vals.std(),
                'min': vals.min(),
                'p25': vals.quantile(0.25),
                'median': vals.median(),
                'p75': vals.quantile(0.75),
                'max': vals.max(),
                'missing_pct': vals.isna().mean() * 100,
            })
    return pd.DataFrame(rows)


def main():
    print("=" * 70)
    print("SM Source Comparison: GLEAM vs SWSM vs ERA5-Land")
    print("=" * 70)

    # Load main sample
    df = pd.read_parquet(os.path.join(PROCESSED_DIR, 'data_v2_main.parquet'))
    print(f"Loaded main sample: {len(df)} rows")

    # 1. Descriptive summary
    print("\n--- Descriptive Summary ---")
    desc = descriptive_summary(df)
    print(desc.to_string(index=False))
    desc.to_csv(os.path.join(TABLE_DIR, 'sm_descriptive_summary.csv'), index=False)

    # 2. Overall correlations
    print("\n--- Overall Correlations ---")
    corr_all = pd.concat([
        compute_correlations(df, 'surface'),
        compute_correlations(df, 'rootzone'),
    ], ignore_index=True)
    print(corr_all[['layer', 'window', 'source_1', 'source_2', 'pearson_r', 'spearman_r', 'rmse']].to_string(index=False))
    corr_all.to_csv(os.path.join(TABLE_DIR, 'sm_correlations_overall.csv'), index=False)
    print(f"  Saved: {os.path.join(TABLE_DIR, 'sm_correlations_overall.csv')}")

    # 3. By-year correlations
    print("\n--- Correlations by Year ---")
    corr_yr = pd.concat([
        compute_correlations_by_year(df, 'surface'),
        compute_correlations_by_year(df, 'rootzone'),
    ], ignore_index=True)
    print(corr_yr.to_string(index=False))
    corr_yr.to_csv(os.path.join(TABLE_DIR, 'sm_correlations_by_year.csv'), index=False)

    # 4. Scatter plots
    print("\n--- Scatter Plots ---")
    plot_scatter_hexbin(df, 'surface')
    plot_scatter_hexbin(df, 'rootzone')

    # 5. Correlation by window bar chart
    print("\n--- Correlation by Window ---")
    plot_corr_by_window(corr_all)

    # 6. Spatial correlation maps
    print("\n--- Spatial Correlation Maps ---")
    plot_spatial_correlation(df, 'surface')
    plot_spatial_correlation(df, 'rootzone')

    print("\n" + "=" * 70)
    print("SM comparison complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
