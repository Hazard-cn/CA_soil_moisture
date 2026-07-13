"""
Diagnose time-varying old-vs-GGCP10 area differences within grid and across
SR/drought cells.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJ_DIR = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
RUN_DIR = PROJ_DIR / "temp" / "2026-05-18_ggcp10_harvarea_agg_baseline_suite"
BASE_DTA = RUN_DIR / "v3_analysis_ready_ggcp10_harvarea_agg.dta"
GRID_STABILITY_CSV = RUN_DIR / "ggcp10_area_grid_stability.csv"
WITHIN_GRID_CSV = RUN_DIR / "ggcp10_area_within_grid_year_change.csv"
SR_D_GROUP_CSV = RUN_DIR / "ggcp10_area_by_sr_d_group.csv"


def main() -> None:
    df = pd.read_stata(BASE_DTA, convert_categoricals=False)
    df = df[df["main_sample"].eq(1)].copy()
    df["area_ratio_old_to_new"] = df["orig_maize_area_km2"] / df["maize_area_km2"]
    df["ln_area_ratio_old_to_new"] = np.log(df["area_ratio_old_to_new"])

    grid = (
        df.groupby("grid_id", observed=True)
        .agg(
            n_years=("year", "nunique"),
            old_area_sd=("orig_maize_area_km2", "std"),
            new_area_sd=("maize_area_km2", "std"),
            ln_ratio_sd=("ln_area_ratio_old_to_new", "std"),
            old_area_mean=("orig_maize_area_km2", "mean"),
            new_area_mean=("maize_area_km2", "mean"),
        )
        .reset_index()
    )
    grid_stability = pd.DataFrame(
        [
            {
                "n_grids": int(len(grid)),
                "share_old_area_time_invariant": float(
                    grid["old_area_sd"].fillna(0).le(1e-12).mean()
                ),
                "share_new_area_time_invariant": float(
                    grid["new_area_sd"].fillna(0).le(1e-12).mean()
                ),
                "share_ln_ratio_time_invariant": float(
                    grid["ln_ratio_sd"].fillna(0).le(1e-12).mean()
                ),
                "median_old_area_sd": float(grid["old_area_sd"].median()),
                "median_new_area_sd": float(grid["new_area_sd"].median()),
                "median_ln_ratio_sd": float(grid["ln_ratio_sd"].median()),
            }
        ]
    )

    for col in [
        "orig_maize_area_km2",
        "maize_area_km2",
        "ln_area_ratio_old_to_new",
        "D_full",
        "ca",
        "SR_x_D_full",
    ]:
        df[f"{col}_within"] = df[col] - df.groupby("grid_id", observed=True)[col].transform(
            "mean"
        )

    within_corr = []
    for x in ["D_full_within", "ca_within", "SR_x_D_full_within"]:
        within_corr.append(
            {
                "x": x.replace("_within", ""),
                "corr_within_ln_area_ratio": float(
                    df[[x, "ln_area_ratio_old_to_new_within"]].corr().iloc[0, 1]
                ),
                "corr_within_old_area": float(
                    df[[x, "orig_maize_area_km2_within"]].corr().iloc[0, 1]
                ),
                "corr_within_new_area": float(
                    df[[x, "maize_area_km2_within"]].corr().iloc[0, 1]
                ),
            }
        )
    within_grid = pd.DataFrame(within_corr)

    df["ca_group"] = pd.qcut(df["ca"], 3, labels=["low_sr", "mid_sr", "high_sr"])
    df["d_group"] = "zero_d"
    positive_d = df["D_full"].gt(0)
    df.loc[positive_d, "d_group"] = pd.qcut(
        df.loc[positive_d, "D_full"],
        2,
        labels=["low_pos_d", "high_pos_d"],
    ).astype(str)
    sr_d_group = (
        df.groupby(["ca_group", "d_group"], observed=True)
        .agg(
            n=("grid_id", "size"),
            ca_mean=("ca", "mean"),
            d_mean=("D_full", "mean"),
            srd_mean=("SR_x_D_full", "mean"),
            old_area_mean=("orig_maize_area_km2", "mean"),
            new_area_mean=("maize_area_km2", "mean"),
            ln_area_ratio_mean=("ln_area_ratio_old_to_new", "mean"),
            old_yield_mean=("orig_yield_tons_ha", "mean"),
            new_yield_mean=("yield_tons_ha", "mean"),
        )
        .reset_index()
    )

    grid_stability.to_csv(GRID_STABILITY_CSV, index=False)
    within_grid.to_csv(WITHIN_GRID_CSV, index=False)
    sr_d_group.to_csv(SR_D_GROUP_CSV, index=False)

    print(f"Saved: {GRID_STABILITY_CSV}")
    print(f"Saved: {WITHIN_GRID_CSV}")
    print(f"Saved: {SR_D_GROUP_CSV}")


if __name__ == "__main__":
    main()
