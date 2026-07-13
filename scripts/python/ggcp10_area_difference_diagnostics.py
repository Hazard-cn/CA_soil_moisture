"""
Diagnose how old-vs-GGCP10 area differences relate to drought, SR, and SR x D.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJ_DIR = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
RUN_DIR = PROJ_DIR / "temp" / "2026-05-18_ggcp10_harvarea_agg_baseline_suite"
BASE_DTA = RUN_DIR / "v3_analysis_ready_ggcp10_harvarea_agg.dta"
SUMMARY_CSV = RUN_DIR / "ggcp10_area_difference_summary.csv"
QUANTILE_CSV = RUN_DIR / "ggcp10_area_difference_by_srd_quantile.csv"
CORR_CSV = RUN_DIR / "ggcp10_area_difference_correlations.csv"
EXTREME_CSV = RUN_DIR / "ggcp10_area_difference_extreme_rows.csv"
YEAR_CSV = RUN_DIR / "ggcp10_area_difference_by_year.csv"


def main() -> None:
    df = pd.read_stata(BASE_DTA, convert_categoricals=False)
    df = df[df["main_sample"].eq(1)].copy()
    df["area_ratio_old_to_new"] = df["orig_maize_area_km2"] / df["maize_area_km2"]
    df["ln_area_ratio_old_to_new"] = np.log(df["area_ratio_old_to_new"])
    df["yield_ratio_new_to_old"] = df["yield_tons_ha"] / df["orig_yield_tons_ha"]
    df["srd_decile"] = pd.qcut(df["SR_x_D_full"], 10, labels=False, duplicates="drop") + 1

    summary = pd.DataFrame(
        [
            {
                "n": int(len(df)),
                "old_area_mean": float(df["orig_maize_area_km2"].mean()),
                "new_area_mean": float(df["maize_area_km2"].mean()),
                "area_ratio_mean": float(df["area_ratio_old_to_new"].mean()),
                "area_ratio_median": float(df["area_ratio_old_to_new"].median()),
                "ln_area_ratio_mean": float(df["ln_area_ratio_old_to_new"].mean()),
                "old_yield_mean": float(df["orig_yield_tons_ha"].mean()),
                "new_yield_mean": float(df["yield_tons_ha"].mean()),
                "new_to_old_yield_ratio_mean": float(df["yield_ratio_new_to_old"].mean()),
            }
        ]
    )

    q = (
        df.groupby("srd_decile", observed=True)
        .agg(
            n=("grid_id", "size"),
            srd_mean=("SR_x_D_full", "mean"),
            d_mean=("D_full", "mean"),
            ca_mean=("ca", "mean"),
            old_area_mean=("orig_maize_area_km2", "mean"),
            new_area_mean=("maize_area_km2", "mean"),
            area_ratio_mean=("area_ratio_old_to_new", "mean"),
            ln_area_ratio_mean=("ln_area_ratio_old_to_new", "mean"),
            old_yield_mean=("orig_yield_tons_ha", "mean"),
            new_yield_mean=("yield_tons_ha", "mean"),
            new_to_old_yield_ratio_mean=("yield_ratio_new_to_old", "mean"),
        )
        .reset_index()
    )

    corr_rows = []
    for x in ["D_full", "ca", "SR_x_D_full"]:
        corr_rows.append(
            {
                "x": x,
                "corr_with_ln_area_ratio": float(df[[x, "ln_area_ratio_old_to_new"]].corr().iloc[0, 1]),
                "corr_with_area_ratio": float(df[[x, "area_ratio_old_to_new"]].corr().iloc[0, 1]),
            }
        )
    corr = pd.DataFrame(corr_rows)

    yr = (
        df.groupby("year", observed=True)
        .agg(
            n=("grid_id", "size"),
            old_area_mean=("orig_maize_area_km2", "mean"),
            new_area_mean=("maize_area_km2", "mean"),
            area_ratio_mean=("area_ratio_old_to_new", "mean"),
            ln_area_ratio_mean=("ln_area_ratio_old_to_new", "mean"),
            old_yield_mean=("orig_yield_tons_ha", "mean"),
            new_yield_mean=("yield_tons_ha", "mean"),
        )
        .reset_index()
    )

    extreme = (
        df.assign(abs_ln_area_ratio=lambda x: x["ln_area_ratio_old_to_new"].abs())
        .nlargest(50, "abs_ln_area_ratio")
        [
            [
                "year",
                "grid_id",
                "latitude",
                "longitude",
                "D_full",
                "ca",
                "SR_x_D_full",
                "orig_maize_area_km2",
                "maize_area_km2",
                "area_ratio_old_to_new",
                "ln_area_ratio_old_to_new",
                "orig_yield_tons_ha",
                "yield_tons_ha",
            ]
        ]
    )

    summary.to_csv(SUMMARY_CSV, index=False)
    q.to_csv(QUANTILE_CSV, index=False)
    corr.to_csv(CORR_CSV, index=False)
    yr.to_csv(YEAR_CSV, index=False)
    extreme.to_csv(EXTREME_CSV, index=False)

    print(f"Saved: {SUMMARY_CSV}")
    print(f"Saved: {QUANTILE_CSV}")
    print(f"Saved: {CORR_CSV}")
    print(f"Saved: {YEAR_CSV}")
    print(f"Saved: {EXTREME_CSV}")


if __name__ == "__main__":
    main()
