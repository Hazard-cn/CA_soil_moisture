"""
s09_quality_check.py - Data quality validation
Purpose: Validate merged panel, compare full-season variables with v1
Author: Data Build Pipeline
Date: 2026-04-07
Input: data/processed/data_v3_phenowindows.csv, v1 .dta
Output: output/tables/descriptive_stats_v3.csv, console report
"""

import sys
import os

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

np.random.seed(RANDOM_SEED)


def make_compound_col(source_key, hot_t, suffix="", pct=None):
    """Construct one compound hot-dry column name."""
    source_cfg = COMPOUND_DRY_SOURCE_REGISTRY[source_key]
    if source_cfg["type"] == "soil_moisture":
        return f"hotdrydays_ge{hot_t}_{source_key}_p{pct}{suffix}"
    return f"hotdrydays_ge{hot_t}_{source_key}{suffix}"


def get_expected_compound_columns():
    """Expected compound columns implied by config."""
    cols = []
    for suffix in WINDOW_SUFFIXES:
        for source_key, source_cfg in COMPOUND_DRY_SOURCE_REGISTRY.items():
            if source_cfg["type"] == "soil_moisture":
                for hot_t in COMPOUND_HOT_THRESHOLDS:
                    for pct in COMPOUND_SM_PERCENTILES:
                        cols.append(make_compound_col(source_key, hot_t, suffix, pct))
            else:
                for hot_t in COMPOUND_HOT_THRESHOLDS:
                    cols.append(make_compound_col(source_key, hot_t, suffix))
    return cols


def get_compound_reference_col(source_key, suffix="", pct=None):
    """Reference dry-days column used by cross-consistency checks."""
    if source_key == "smrz":
        return f"drydays_gleam_smrz_le_p{pct}{suffix}"
    if source_key == "sms":
        return f"drydays_gleam_sms_le_p{pct}{suffix}"
    if source_key == "swsm_l1":
        return f"drydays_swsm_l1_le_p{pct}{suffix}"
    if source_key == "swsm_l3":
        return f"drydays_swsm_l3_le_p{pct}{suffix}"
    if source_key == "era5l_swvl1":
        return f"drydays_era5l_swvl1_le_p{pct}{suffix}"
    if source_key == "era5l_swvl3":
        return f"drydays_era5l_swvl3_le_p{pct}{suffix}"
    if source_key == "pr_lt1":
        return f"drydays_lt1{suffix}"
    raise KeyError(f"Unsupported source_key: {source_key}")


def check_basic(df):
    """Basic panel checks."""
    print("\n--- Basic Panel Checks ---")
    years = [int(year) for year in sorted(df["year"].unique())]
    checks = [
        ("Total rows", len(df), 122533),
        ("Unique grids", df["grid_id"].nunique(), 36340),
        ("Years", str(years), str(YEARS)),
        ("Duplicate grid-years", df.duplicated(subset=["grid_id", "year"]).sum(), 0),
        ("Phenology V3<HE<MA", ((df["v3_doy"] < df["he_doy"]) & (df["he_doy"] < df["ma_doy"])).all(), True),
    ]

    for name, actual, expected in checks:
        status = "PASS" if str(actual) == str(expected) else "FAIL"
        print(f"  [{status}] {name}: {actual} (expected {expected})")

    return all(str(actual) == str(expected) for _, actual, expected in checks)


def check_ranges(df):
    """Check variable value ranges."""
    print("\n--- Value Range Checks ---")
    range_checks = [
        ("t2m_mean", -30, 50),
        ("tmax_max", -20, 55),
        ("tmin_min", -35, 40),
        ("pr_sum", 0, 5000),
        ("gleam_smrz_mean", 0, 1),
        ("gleam_sms_mean", 0, 1),
        ("swsm_l1_mean", 0, 1),
        ("swsm_l3_mean", 0, 1),
        ("et0_sum", 0, 2000),
        ("hotdays_ge32", 0, 366),
        (LEGACY_GDD_VAR, 0, 10000),
    ]
    range_checks.extend((var, 0, 10000) for var in CAPPED_GDD_VARS)

    all_ok = True
    for var, lo, hi in range_checks:
        if var not in df.columns:
            print(f"  [SKIP] {var} not in columns")
            continue
        vmin = df[var].min()
        vmax = df[var].max()
        ok = (vmin >= lo or np.isnan(vmin)) and (vmax <= hi or np.isnan(vmax))
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {var}: [{vmin:.4f}, {vmax:.4f}] (expected [{lo}, {hi}])")
        if not ok:
            all_ok = False

    compound_cols = [col for col in df.columns if col.startswith("hotdrydays_")]
    if compound_cols:
        violations = []
        for col in compound_cols:
            series = df[col].dropna()
            if len(series) == 0:
                continue
            if series.min() < 0 or series.max() > 366:
                violations.append((col, float(series.min()), float(series.max())))

        status = "PASS" if len(violations) == 0 else "FAIL"
        print(
            f"  [{status}] hotdrydays_*: checked {len(compound_cols)} columns "
            f"against [0, 366], violations={len(violations)}"
        )
        if violations:
            sample = ", ".join(f"{col}[{vmin:.1f},{vmax:.1f}]" for col, vmin, vmax in violations[:5])
            print(f"    Sample violations: {sample}")
            all_ok = False

    return all_ok


def check_capped_gdd_monotonicity(df):
    """Check capped GDD ordering within each window."""
    print("\n--- Capped GDD Monotonicity ---")
    all_ok = True

    ordered_vars = [*CAPPED_GDD_VARS, LEGACY_GDD_VAR]
    for suffix in WINDOW_SUFFIXES:
        cols = [f"{var}{suffix}" for var in ordered_vars]
        label = suffix if suffix else "(full)"

        if not all(col in df.columns for col in cols):
            print(f"  [SKIP] {label}: missing columns")
            continue

        valid = df[cols].notna().all(axis=1)
        if not valid.any():
            print(f"  [SKIP] {label}: no fully observed rows")
            continue

        subset = df.loc[valid, cols]
        monotonic = (
            (subset[cols[0]] <= subset[cols[1]])
            & (subset[cols[1]] <= subset[cols[2]])
            & (subset[cols[2]] <= subset[cols[3]])
            & (subset[cols[3]] <= subset[cols[4]])
        )
        violations = int((~monotonic).sum())
        status = "PASS" if violations == 0 else "FAIL"
        print(f"  [{status}] {label}: {violations} violations across {int(valid.sum())} rows")
        if violations > 0:
            all_ok = False

    return all_ok


def check_compound_logic(df):
    """Check structure and monotonicity of compound hot-dry variables."""
    print("\n--- Compound Hot-Dry Checks ---")
    all_ok = True

    expected_cols = get_expected_compound_columns()
    actual_cols = [col for col in df.columns if col.startswith("hotdrydays_")]
    missing_cols = sorted(set(expected_cols) - set(actual_cols))
    extra_cols = sorted(set(actual_cols) - set(expected_cols))

    status = "PASS" if not missing_cols and not extra_cols else "FAIL"
    print(
        f"  [{status}] hotdrydays_* structure: expected={len(expected_cols)}, "
        f"actual={len(actual_cols)}, missing={len(missing_cols)}, extra={len(extra_cols)}"
    )
    if missing_cols:
        print(f"    Missing sample: {', '.join(missing_cols[:5])}")
        all_ok = False
    if extra_cols:
        print(f"    Extra sample: {', '.join(extra_cols[:5])}")
        all_ok = False

    threshold_groups = 0
    threshold_violations = 0
    for suffix in WINDOW_SUFFIXES:
        for source_key, source_cfg in COMPOUND_DRY_SOURCE_REGISTRY.items():
            pct_values = COMPOUND_SM_PERCENTILES if source_cfg["type"] == "soil_moisture" else [None]
            for pct in pct_values:
                cols = [make_compound_col(source_key, hot_t, suffix, pct) for hot_t in COMPOUND_HOT_THRESHOLDS]
                if not all(col in df.columns for col in cols):
                    continue
                valid = df[cols].notna().all(axis=1)
                if not valid.any():
                    continue
                threshold_groups += 1
                subset = df.loc[valid, cols]
                monotonic = (subset[cols[2]] <= subset[cols[1]]) & (subset[cols[1]] <= subset[cols[0]])
                threshold_violations += int((~monotonic).sum())

    status = "PASS" if threshold_violations == 0 else "FAIL"
    print(
        f"  [{status}] hot threshold monotonicity: {threshold_violations} violations "
        f"across {threshold_groups} source-window groups"
    )
    if threshold_violations > 0:
        all_ok = False

    percentile_groups = 0
    percentile_violations = 0
    for suffix in WINDOW_SUFFIXES:
        for source_key, source_cfg in COMPOUND_DRY_SOURCE_REGISTRY.items():
            if source_cfg["type"] != "soil_moisture":
                continue
            for hot_t in COMPOUND_HOT_THRESHOLDS:
                p10_col = make_compound_col(source_key, hot_t, suffix, 10)
                p20_col = make_compound_col(source_key, hot_t, suffix, 20)
                if p10_col not in df.columns or p20_col not in df.columns:
                    continue
                valid = df[[p10_col, p20_col]].notna().all(axis=1)
                if not valid.any():
                    continue
                percentile_groups += 1
                percentile_violations += int((df.loc[valid, p10_col] > df.loc[valid, p20_col]).sum())

    status = "PASS" if percentile_violations == 0 else "FAIL"
    print(
        f"  [{status}] p10<=p20 consistency: {percentile_violations} violations "
        f"across {percentile_groups} source-window-threshold groups"
    )
    if percentile_violations > 0:
        all_ok = False

    missing_refs = []
    cross_groups = 0
    cross_violations = 0
    for suffix in WINDOW_SUFFIXES:
        for source_key, source_cfg in COMPOUND_DRY_SOURCE_REGISTRY.items():
            pct_values = COMPOUND_SM_PERCENTILES if source_cfg["type"] == "soil_moisture" else [None]
            for pct in pct_values:
                ref_col = get_compound_reference_col(source_key, suffix, pct)
                if ref_col not in df.columns:
                    missing_refs.append(ref_col)
                    continue
                for hot_t in COMPOUND_HOT_THRESHOLDS:
                    compound_col = make_compound_col(source_key, hot_t, suffix, pct)
                    if compound_col not in df.columns:
                        continue
                    valid = df[[compound_col, ref_col]].notna().all(axis=1)
                    if not valid.any():
                        continue
                    cross_groups += 1
                    cross_violations += int((df.loc[valid, compound_col] > df.loc[valid, ref_col]).sum())

    if missing_refs:
        print(f"  [FAIL] compound reference columns missing: {len(set(missing_refs))}")
        print(f"    Missing sample: {', '.join(sorted(set(missing_refs))[:5])}")
        all_ok = False
    else:
        print("  [PASS] compound reference columns present")

    status = "PASS" if cross_violations == 0 else "FAIL"
    print(
        f"  [{status}] compound <= reference drydays: {cross_violations} violations "
        f"across {cross_groups} comparisons"
    )
    if cross_violations > 0:
        all_ok = False

    return all_ok


def check_missing(df):
    """Report missing value rates."""
    print("\n--- Missing Value Report ---")
    categories = {
        "Identifiers": ["grid_id", "year", "latitude", "longitude"],
        "Phenology": ["v3_doy", "he_doy", "ma_doy", "ca_ratio", "maize_frac"],
        "Temperature (full)": [
            col for col in df.columns
            if col.startswith("t2m_") and not any(col.endswith(s) for s in WINDOW_SUFFIXES[1:])
        ],
        "Yield/SR": ["yield_tons_ha", "ln_yield", "ca", "crc_ca_ratio"],
    }

    for category, cols in categories.items():
        existing = [col for col in cols if col in df.columns]
        if not existing:
            continue
        miss_rates = {col: df[col].isna().mean() * 100 for col in existing}
        worst = max(miss_rates.values())
        print(f"  {category}: max missing = {worst:.1f}%")
        for col, rate in miss_rates.items():
            if rate > 0:
                print(f"    {col}: {rate:.1f}%")


def compare_with_v1(df):
    """Compare full-season variables with v1 data."""
    print("\n--- v1 Comparison (Full Season) ---")

    v1_path = os.path.join(PARENT_DIR, "data/processed/analysis_main_sample.dta")
    v1 = pd.read_stata(v1_path)

    v1["lat_int"] = (v1["latitude"] * 10).round().astype(int)
    v1["lon_int"] = (v1["longitude"] * 10).round().astype(int)
    df["lat_int"] = (df["latitude"] * 10).round().astype(int)
    df["lon_int"] = (df["longitude"] * 10).round().astype(int)

    matched = df.merge(
        v1[
            [
                "lat_int",
                "lon_int",
                "year",
                "t2m_mean",
                "pre_sum",
                "gleam_smrz_mean",
                "gleam_sms_mean",
                "et0_mean",
                "hdd_tmax_ge32",
                "hotdays_tmax_ge32",
                "SPEI_season",
                "VPD_season_mean",
            ]
        ],
        on=["lat_int", "lon_int", "year"],
        how="inner",
        suffixes=(f"_{DATA_VERSION}", "_v1"),
    )
    print(f"  Matched rows: {len(matched)}")

    comparisons = [
        ("t2m_mean", "t2m_mean_v1"),
        ("gleam_smrz_mean", "gleam_smrz_mean_v1"),
        ("gleam_sms_mean", "gleam_sms_mean_v1"),
    ]

    for left_col, right_col in comparisons:
        if left_col not in matched.columns or right_col not in matched.columns:
            left_actual = left_col + f"_{DATA_VERSION}" if left_col + f"_{DATA_VERSION}" in matched.columns else left_col
            right_actual = right_col if right_col in matched.columns else left_col + "_v1"
        else:
            left_actual, right_actual = left_col, right_col

        if left_actual not in matched.columns or right_actual not in matched.columns:
            print(f"  [SKIP] {left_col}: columns not found")
            continue

        valid = matched[[left_actual, right_actual]].dropna()
        if len(valid) == 0:
            print(f"  [SKIP] {left_col}: no valid pairs")
            continue

        corr = valid[left_actual].corr(valid[right_actual])
        mean_diff = (valid[left_actual] - valid[right_actual]).abs().mean()
        status = "PASS" if corr > 0.99 else ("WARN" if corr > 0.95 else "FAIL")
        print(f"  [{status}] {left_col}: corr={corr:.6f}, mean_abs_diff={mean_diff:.4f}")

    if "pr_sum" in matched.columns and "pre_sum" in matched.columns:
        valid = matched[["pr_sum", "pre_sum"]].dropna()
        corr = valid["pr_sum"].corr(valid["pre_sum"])
        mean_diff = (valid["pr_sum"] - valid["pre_sum"]).abs().mean()
        status = "PASS" if corr > 0.99 else ("WARN" if corr > 0.95 else "FAIL")
        print(f"  [{status}] pr_sum vs pre_sum: corr={corr:.6f}, mean_abs_diff={mean_diff:.4f}")

    df.drop(columns=["lat_int", "lon_int"], inplace=True)


def generate_summary_table(df):
    """Generate descriptive statistics table."""
    print("\n--- Generating Summary Statistics ---")

    key_prefixes = [
        "t2m_mean",
        "tmax_mean",
        "pr_sum",
        "pr_mean",
        "gleam_smrz_mean",
        "gleam_sms_mean",
        "swsm_l1_mean",
        "swsm_l3_mean",
        "et0_sum",
        "vpd_mean",
        "hotdays_ge32",
        "hdd_ge32",
        LEGACY_GDD_VAR,
        *CAPPED_GDD_VARS,
        "drydays_lt1",
        "max_cdd",
    ]

    key_vars = []
    for prefix in key_prefixes:
        for suffix in WINDOW_SUFFIXES:
            col = prefix + suffix
            if col in df.columns:
                key_vars.append(col)

    key_vars.extend(sorted(col for col in df.columns if col.startswith("hotdrydays_")))
    key_vars = list(dict.fromkeys(key_vars))

    stats = df[key_vars].describe().T
    stats["missing%"] = df[key_vars].isna().mean() * 100
    stats.to_csv(QUALITY_TABLE_PATH)
    print(f"  Saved: {QUALITY_TABLE_PATH} ({len(stats)} variables)")

    return stats


def main():
    print("=" * 70)
    print(f"Step 09: Data Quality Check ({DATA_VERSION.upper()})")
    print("=" * 70)

    df = pd.read_csv(PHENOWINDOWS_CSV)
    print(f"Loaded: {len(df)} rows, {len(df.columns)} cols")

    check_basic(df)
    check_ranges(df)
    check_capped_gdd_monotonicity(df)
    check_compound_logic(df)
    check_missing(df)
    compare_with_v1(df)
    generate_summary_table(df)

    print("\n" + "=" * 70)
    print("Quality check completed.")
    print("=" * 70)


if __name__ == "__main__":
    main()
