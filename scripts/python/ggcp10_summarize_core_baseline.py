"""
Summarize the compact GGCP10 core baseline suite for quick comparison.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJ_DIR = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
RUN_DIR = PROJ_DIR / "temp" / "2026-05-18_ggcp10_harvarea_agg_baseline_suite"
COEF_CSV = RUN_DIR / "ggcp10_core_baseline_coefficients.csv"
FOCUS_CSV = RUN_DIR / "ggcp10_core_baseline_focus_terms.csv"
SUMMARY_CSV = RUN_DIR / "ggcp10_core_baseline_focus_summary.csv"


def sig_label(p: float) -> str:
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return "n.s."


def sign_label(value: float) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "zero"


def main() -> None:
    df = pd.read_csv(COEF_CSV)
    focus = df.loc[df["term"].isin(["Main", "SR_x_Main", "M"])].copy()
    focus["sig"] = focus["p"].map(sig_label)
    focus["sign"] = focus["b"].map(sign_label)
    focus.to_csv(FOCUS_CSV, index=False)

    summary = (
        focus.groupby(
            ["hazard", "mediator_type", "equation", "term", "sig", "sign"],
            dropna=False,
        )
        .size()
        .reset_index(name="n")
        .sort_values(["hazard", "mediator_type", "equation", "term", "sig", "sign"])
    )
    summary.to_csv(SUMMARY_CSV, index=False)

    print(f"Saved focus terms: {FOCUS_CSV}")
    print(f"Saved summary: {SUMMARY_CSV}")


if __name__ == "__main__":
    main()
