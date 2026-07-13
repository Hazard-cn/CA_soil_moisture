"""
Compare baseline v6gleambl coefficients between the original and GGCP10 branches.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJ_DIR = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
OLD_DIR = PROJ_DIR / "temp" / "2026-04-23_newSMsplit"
NEW_DIR = PROJ_DIR / "temp" / "2026-05-18_ggcp10_harvarea_v6gleambl"
OLD_COEF = OLD_DIR / "v6gleambl_baseline_coefficients.csv"
NEW_COEF = NEW_DIR / "v6gleambl_harvarea_baseline_coefficients.csv"
OUT_COMPARE = NEW_DIR / "v6gleambl_harvarea_vs_old_coefficients.csv"
OUT_SUMMARY = NEW_DIR / "v6gleambl_harvarea_vs_old_summary.csv"

KEYS = [
    "module",
    "window",
    "metric_family",
    "dry_pct",
    "wet_pct",
    "source_layer",
    "sm_label",
    "sample_tag",
    "equation",
    "term",
    "regressor",
]


def sig_level(p: float) -> str:
    if pd.isna(p):
        return ""
    if p < 0.01:
        return "p<0.01"
    if p < 0.05:
        return "p<0.05"
    if p < 0.10:
        return "p<0.10"
    return "n.s."


def main() -> None:
    old = pd.read_csv(OLD_COEF)
    new = pd.read_csv(NEW_COEF)
    old["dry_pct"] = old["dry_pct"].fillna(".").astype(str)
    old["wet_pct"] = old["wet_pct"].fillna(".").astype(str)
    new["dry_pct"] = new["dry_pct"].fillna(".").astype(str)
    new["wet_pct"] = new["wet_pct"].fillna(".").astype(str)
    merged = old.merge(new, on=KEYS, how="outer", suffixes=("_old", "_new"), indicator=True)
    if not (merged["_merge"] == "both").all():
        unmatched = merged["_merge"].value_counts(dropna=False).to_dict()
        raise ValueError(f"Coefficient keys do not align: {unmatched}")

    merged["sig_old"] = merged["p_old"].map(sig_level)
    merged["sig_new"] = merged["p_new"].map(sig_level)
    merged["sig_status_changed"] = merged["sig_old"] != merged["sig_new"]
    merged["sign_old"] = np.sign(merged["b_old"])
    merged["sign_new"] = np.sign(merged["b_new"])
    merged["sign_flipped"] = merged["sign_old"] != merged["sign_new"]
    merged["significant_sign_flip"] = (
        merged["sign_flipped"]
        & merged["sig_old"].isin(["p<0.01", "p<0.05", "p<0.10"])
        & merged["sig_new"].isin(["p<0.01", "p<0.05", "p<0.10"])
    )
    merged["b_delta"] = merged["b_new"] - merged["b_old"]
    merged["se_delta"] = merged["se_new"] - merged["se_old"]
    merged["N_delta"] = merged["N_new"] - merged["N_old"]
    merged.to_csv(OUT_COMPARE, index=False)

    summary = pd.DataFrame(
        [
            {
                "rows_compared": int(len(merged)),
                "sig_status_changes": int(merged["sig_status_changed"].sum()),
                "significant_sign_flips": int(merged["significant_sign_flip"].sum()),
                "any_sign_flips": int(merged["sign_flipped"].sum()),
                "median_abs_b_delta": float(merged["b_delta"].abs().median()),
                "median_N_delta": float(merged["N_delta"].median()),
                "min_N_delta": int(merged["N_delta"].min()),
                "max_N_delta": int(merged["N_delta"].max()),
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Saved comparison: {OUT_COMPARE}")
    print(f"Saved summary: {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
