"""
Summarize old phenology-area vs GGCP10 harvested-area differences by province,
old maize fraction, and GGCP10 maize fraction.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJ_DIR = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
RUN_DIR = PROJ_DIR / "temp" / "2026-05-18_ggcp10_harvarea_agg_baseline_suite"
BASE_DTA = RUN_DIR / "v3_analysis_ready_ggcp10_harvarea_agg.dta"
PROV_CSV = RUN_DIR / "ggcp10_area_difference_by_province.csv"
OLD_FRAC_CSV = RUN_DIR / "ggcp10_area_difference_by_old_maize_frac.csv"
NEW_FRAC_CSV = RUN_DIR / "ggcp10_area_difference_by_ggcp10_frac.csv"
REL_CSV = RUN_DIR / "ggcp10_area_fraction_relationships.csv"


def summarize(df: pd.DataFrame, by: str) -> pd.DataFrame:
    return (
        df.groupby(by, observed=True)
        .agg(
            n=("grid_id", "size"),
            old_area_mean=("orig_maize_area_km2", "mean"),
            new_area_mean=("maize_area_km2", "mean"),
            old_frac_mean=("maize_frac", "mean"),
            ggcp10_frac_mean=("ggcp10_maize_frac", "mean"),
            area_ratio_mean=("area_ratio_old_to_new", "mean"),
            ln_area_ratio_mean=("ln_area_ratio_old_to_new", "mean"),
            srd_mean=("SR_x_D_full", "mean"),
            old_yield_mean=("orig_yield_tons_ha", "mean"),
            new_yield_mean=("yield_tons_ha", "mean"),
        )
        .reset_index()
    )


def main() -> None:
    df = pd.read_stata(BASE_DTA, convert_categoricals=False)
    df = df[df["main_sample"].eq(1)].copy()
    df["area_ratio_old_to_new"] = df["orig_maize_area_km2"] / df["maize_area_km2"]
    df["ln_area_ratio_old_to_new"] = np.log(df["area_ratio_old_to_new"])
    df["old_frac_bin"] = pd.qcut(df["maize_frac"], 10, duplicates="drop")
    df["ggcp10_frac_bin"] = pd.qcut(df["ggcp10_maize_frac"], 10, duplicates="drop")

    prov = summarize(df, "province").sort_values("ln_area_ratio_mean", ascending=False)
    old_frac = summarize(df, "old_frac_bin")
    new_frac = summarize(df, "ggcp10_frac_bin")

    rel = pd.DataFrame(
        [
            {
                "corr_oldfrac_ggcp10frac": float(
                    df[["maize_frac", "ggcp10_maize_frac"]].corr().iloc[0, 1]
                ),
                "corr_oldarea_newarea": float(
                    df[["orig_maize_area_km2", "maize_area_km2"]].corr().iloc[0, 1]
                ),
                "corr_oldfrac_ln_area_ratio": float(
                    df[["maize_frac", "ln_area_ratio_old_to_new"]].corr().iloc[0, 1]
                ),
                "corr_ggcp10frac_ln_area_ratio": float(
                    df[["ggcp10_maize_frac", "ln_area_ratio_old_to_new"]].corr().iloc[0, 1]
                ),
            }
        ]
    )

    prov.to_csv(PROV_CSV, index=False)
    old_frac.to_csv(OLD_FRAC_CSV, index=False)
    new_frac.to_csv(NEW_FRAC_CSV, index=False)
    rel.to_csv(REL_CSV, index=False)

    print(f"Saved: {PROV_CSV}")
    print(f"Saved: {OLD_FRAC_CSV}")
    print(f"Saved: {NEW_FRAC_CSV}")
    print(f"Saved: {REL_CSV}")


if __name__ == "__main__":
    main()
