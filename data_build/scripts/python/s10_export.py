"""
s10_export.py — Export final panel in multiple formats
Purpose: Export versioned phenowindows/main/noyield panels
Author: Data Build Pipeline
Date: 2026-04-07
Input: data/processed/data_v3_phenowindows.csv
Output: data/processed/data_v3_*.{csv,dta,parquet}
"""

import sys
import os
import numpy as np
import pandas as pd
import time as timer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *
from stata_alias_utils import build_stata_alias_map, build_variable_labels, write_alias_outputs

np.random.seed(RANDOM_SEED)


def export_stata(df, dta_path, alias_df):
    """Export a dataframe to Stata with safe variable names."""
    df_stata = df.copy()
    col_map = dict(zip(alias_df["original_name"], alias_df["stata_name"]))
    df_stata.columns = [col_map[c] for c in df_stata.columns]

    str_cols = df_stata.select_dtypes(include=["object"]).columns
    for col in str_cols:
        df_stata[col] = df_stata[col].fillna("").astype(str)

    var_labels = build_variable_labels(alias_df)

    try:
        df_stata.to_stata(dta_path, write_index=False, version=118, variable_labels=var_labels)
        return os.path.getsize(dta_path) / (1024 * 1024)
    except Exception as exc:
        print(f"    Stata export WARNING: {exc}")
        df_numeric = df_stata.select_dtypes(include=[np.number])
        numeric_labels = {k: v for k, v in var_labels.items() if k in df_numeric.columns}
        df_numeric.to_stata(dta_path, write_index=False, version=118, variable_labels=numeric_labels)
        return os.path.getsize(dta_path) / (1024 * 1024)


def export_bundle(df, label, alias_df, csv_path=None, parquet_path=None, dta_path=None):
    """Export a dataset bundle and report file sizes."""
    print(f"\n  Exporting {label}: {len(df)} rows, {len(df.columns)} cols")
    sizes = {}

    if csv_path is not None:
        df.to_csv(csv_path, index=False)
        sizes["csv"] = os.path.getsize(csv_path) / (1024 * 1024)
        print(f"    CSV: {csv_path} ({sizes['csv']:.1f} MB)")

    if parquet_path is not None:
        df.to_parquet(parquet_path, index=False, engine="pyarrow")
        sizes["parquet"] = os.path.getsize(parquet_path) / (1024 * 1024)
        print(f"    Parquet: {parquet_path} ({sizes['parquet']:.1f} MB)")

    if dta_path is not None:
        sizes["dta"] = export_stata(df, dta_path, alias_df)
        print(f"    Stata: {dta_path} ({sizes['dta']:.1f} MB)")

    return sizes


def main():
    print("=" * 70)
    print(f"Step 10: Export Final Panel ({DATA_VERSION.upper()})")
    print("=" * 70)

    t0 = timer.time()
    df = pd.read_csv(PHENOWINDOWS_CSV)
    print(f"Loaded corrected phenowindows panel: {len(df)} rows, {len(df.columns)} cols")
    alias_df = build_stata_alias_map(df.columns.tolist())
    write_alias_outputs(alias_df)
    print(
        f"Alias map: {int(alias_df['changed'].sum())} renamed / {len(alias_df)} total "
        f"-> {STATA_ALIAS_TABLE_PATH}"
    )
    print(f"Alias markdown: {STATA_ALIAS_MARKDOWN_PATH}")

    phen_sizes = export_bundle(
        df,
        label="phenowindows",
        alias_df=alias_df,
        csv_path=PHENOWINDOWS_CSV,
        parquet_path=PHENOWINDOWS_PARQUET,
        dta_path=PHENOWINDOWS_DTA,
    )

    if "yield_tons_ha" not in df.columns:
        raise KeyError("yield_tons_ha not found; cannot split main and no-yield samples")

    df_main = df[df["yield_tons_ha"].notna()].copy()
    df_noyield = df[df["yield_tons_ha"].isna()].copy()

    main_sizes = export_bundle(
        df_main,
        label="main sample",
        alias_df=alias_df,
        csv_path=MAIN_CSV,
        parquet_path=MAIN_PARQUET,
        dta_path=MAIN_DTA,
    )

    noyield_sizes = export_bundle(
        df_noyield,
        label="no-yield sample",
        alias_df=alias_df,
        parquet_path=NOYIELD_PARQUET,
    )

    print("\n  File sizes summary:")
    print(
        f"    Phenowindows: CSV={phen_sizes.get('csv', 0):.1f} MB, "
        f"Parquet={phen_sizes.get('parquet', 0):.1f} MB, DTA={phen_sizes.get('dta', 0):.1f} MB"
    )
    print(
        f"    Main sample:  CSV={main_sizes.get('csv', 0):.1f} MB, "
        f"Parquet={main_sizes.get('parquet', 0):.1f} MB, DTA={main_sizes.get('dta', 0):.1f} MB"
    )
    print(f"    No-yield:     Parquet={noyield_sizes.get('parquet', 0):.1f} MB")

    print(f"\n  Total time: {timer.time()-t0:.1f}s")
    print("\n  Panel summary:")
    years = [int(year) for year in sorted(df["year"].unique())]
    print(f"    Phenowindows rows: {len(df)}")
    print(f"    Main rows:         {len(df_main)}")
    print(f"    No-yield rows:     {len(df_noyield)}")
    print(f"    Columns:           {len(df.columns)}")
    print(f"    Grids:             {df['grid_id'].nunique()}")
    print(f"    Years:             {years}")


if __name__ == "__main__":
    main()
