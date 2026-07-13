"""
fix_pseudo_zeros.py — Fix pseudo-zero values caused by NaN in source data
Purpose: When source data is all-NaN for a cell, nansum/count returns 0 instead of NaN.
         This script propagates NaN from continuous indicators to count/sum indicators.
Author: Data Build Pipeline
Date: 2026-04-07
Input/Output: data/processed/data_v3_phenowindows.{csv,parquet,dta}
"""

import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

np.random.seed(RANDOM_SEED)


def _is_full_window_col(col):
    return not any(col.endswith(s) for s in WINDOW_SUFFIXES[1:])


def _load_panel():
    if os.path.exists(PHENOWINDOWS_CSV):
        return pd.read_csv(PHENOWINDOWS_CSV)
    if os.path.exists(PHENOWINDOWS_PARQUET):
        return pd.read_parquet(PHENOWINDOWS_PARQUET)
    raise FileNotFoundError(f"Neither {PHENOWINDOWS_CSV} nor {PHENOWINDOWS_PARQUET} exists")


def _export_stata(df, outpath):
    df_stata = df.copy()
    col_map = {}
    for col in df_stata.columns:
        if len(col) > 32:
            short = col[:32]
            i = 1
            while short in col_map.values():
                short = col[:30] + f"_{i}"
                i += 1
            col_map[col] = short
        else:
            col_map[col] = col

    df_stata.columns = [col_map[c] for c in df_stata.columns]

    str_cols = df_stata.select_dtypes(include=["object"]).columns
    for col in str_cols:
        df_stata[col] = df_stata[col].fillna("").astype(str)

    df_stata.to_stata(outpath, write_index=False, version=118)


def main():
    print("=" * 70)
    print("Fix Pseudo-Zeros: propagate NaN from continuous to count indicators")
    print("=" * 70)

    df = _load_panel()
    print(f"Loaded: {len(df)} rows, {len(df.columns)} cols")

    total_fixed = 0

    for suffix in WINDOW_SUFFIXES:
        suffix_label = suffix if suffix else "(full)"
        fixes_in_suffix = 0

        sentinel_temp = f"t2m_mean{suffix}"
        if sentinel_temp in df.columns:
            temp_mask = df[sentinel_temp].isna()
            n_temp = int(temp_mask.sum())

            temp_derived = []
            for prefix in ["hotdays_ge", "hdd_ge", "nightheat_ge", "gdd_", "hotdays_ge_basep", "hdd_ge_basep"]:
                for col in df.columns:
                    if not col.startswith(prefix):
                        continue
                    if suffix:
                        if col.endswith(suffix):
                            temp_derived.append(col)
                    elif _is_full_window_col(col):
                        temp_derived.append(col)

            for col in temp_derived:
                n_before = df[col].isna().sum()
                df.loc[temp_mask, col] = np.nan
                fixed = df[col].isna().sum() - n_before
                if fixed > 0:
                    fixes_in_suffix += fixed

            if n_temp > 0:
                print(
                    f"  {suffix_label} Temperature NaN ({n_temp} rows) -> "
                    f"fixed {fixes_in_suffix} cells across {len(temp_derived)} cols"
                )

        sentinel_gleam = f"gleam_smrz_mean{suffix}"
        if sentinel_gleam in df.columns:
            gleam_mask = df[sentinel_gleam].isna()
            gleam_derived = []
            for col in df.columns:
                if not col.startswith("drydays_gleam_"):
                    continue
                if suffix:
                    if col.endswith(suffix):
                        gleam_derived.append(col)
                elif _is_full_window_col(col):
                    gleam_derived.append(col)

            fixes_gleam = 0
            for col in gleam_derived:
                n_before = df[col].isna().sum()
                df.loc[gleam_mask, col] = np.nan
                fixes_gleam += df[col].isna().sum() - n_before
            if fixes_gleam > 0:
                print(
                    f"  {suffix_label} GLEAM NaN ({gleam_mask.sum()} rows) -> "
                    f"fixed {fixes_gleam} cells across {len(gleam_derived)} cols"
                )
            fixes_in_suffix += fixes_gleam

        sentinel_swsm = f"swsm_l1_mean{suffix}"
        if sentinel_swsm in df.columns:
            swsm_mask = df[sentinel_swsm].isna()
            swsm_derived = []
            for col in df.columns:
                if not col.startswith("drydays_swsm_"):
                    continue
                if suffix:
                    if col.endswith(suffix):
                        swsm_derived.append(col)
                elif _is_full_window_col(col):
                    swsm_derived.append(col)

            fixes_swsm = 0
            for col in swsm_derived:
                n_before = df[col].isna().sum()
                df.loc[swsm_mask, col] = np.nan
                fixes_swsm += df[col].isna().sum() - n_before
            if fixes_swsm > 0:
                print(
                    f"  {suffix_label} SWSM NaN ({swsm_mask.sum()} rows) -> "
                    f"fixed {fixes_swsm} cells across {len(swsm_derived)} cols"
                )
            fixes_in_suffix += fixes_swsm

        sentinel_et0 = f"et0_mean{suffix}"
        if sentinel_et0 in df.columns:
            et0_mask = df[sentinel_et0].isna()
            et0_derived = [c for c in [f"et0_sum{suffix}", f"wd_deficit{suffix}"] if c in df.columns]
            fixes_et0 = 0
            for col in et0_derived:
                n_before = df[col].isna().sum()
                df.loc[et0_mask, col] = np.nan
                fixes_et0 += df[col].isna().sum() - n_before
            if fixes_et0 > 0:
                print(
                    f"  {suffix_label} ET0 NaN ({et0_mask.sum()} rows) -> "
                    f"fixed {fixes_et0} cells across {len(et0_derived)} cols"
                )
            fixes_in_suffix += fixes_et0

        if sentinel_temp in df.columns:
            temp_mask = df[sentinel_temp].isna()
            compound_cols = []
            for col in df.columns:
                if not col.startswith("hotdrydays_"):
                    continue
                if suffix:
                    if col.endswith(suffix):
                        compound_cols.append(col)
                elif _is_full_window_col(col):
                    compound_cols.append(col)

            fixes_comp = 0
            for col in compound_cols:
                n_before = df[col].isna().sum()
                df.loc[temp_mask, col] = np.nan
                fixes_comp += df[col].isna().sum() - n_before
            if fixes_comp > 0:
                print(
                    f"  {suffix_label} Compound (temp-driven) -> "
                    f"fixed {fixes_comp} cells across {len(compound_cols)} cols"
                )
            fixes_in_suffix += fixes_comp

        total_fixed += fixes_in_suffix

    print(f"\nTotal cells fixed: {total_fixed:,}")

    df.to_csv(PHENOWINDOWS_CSV, index=False)
    df.to_parquet(PHENOWINDOWS_PARQUET, index=False)
    _export_stata(df, PHENOWINDOWS_DTA)
    print(f"Saved: {PHENOWINDOWS_CSV}")
    print(f"Saved: {PHENOWINDOWS_PARQUET}")
    print(f"Saved: {PHENOWINDOWS_DTA}")

    print("\n--- Post-fix verification (yield subsample) ---")
    df_y = df[df["yield_tons_ha"].notna()]
    verify_vars = [
        "t2m_mean",
        "hotdays_ge32",
        "hdd_ge32",
        LEGACY_GDD_VAR,
        *CAPPED_GDD_VARS,
        "gleam_smrz_mean",
        "drydays_gleam_smrz_le_p10",
        "swsm_l1_mean",
        "drydays_swsm_l1_le_p10",
        "et0_mean",
        "et0_sum",
        "wd_deficit",
        "hotdrydays_ge32_smrz_p20",
    ]
    for var in verify_vars:
        if var in df_y.columns:
            miss = df_y[var].isna().sum()
            print(f"  {var:40s} missing: {miss:5d} ({miss/len(df_y)*100:.2f}%)")


if __name__ == "__main__":
    main()
