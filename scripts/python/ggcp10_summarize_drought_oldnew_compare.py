"""
Summarize old/new yield and spec effects for drought SR x D coefficients.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJ_DIR = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
RUN_DIR = PROJ_DIR / "temp" / "2026-05-18_ggcp10_harvarea_agg_baseline_suite"
IN_CSV = RUN_DIR / "ggcp10_drought_oldnew_yield_compare.csv"
OUT_CSV = RUN_DIR / "ggcp10_drought_oldnew_yield_compare_summary.csv"


def sig(p: float) -> str:
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return "n.s."


def main() -> None:
    df = pd.read_csv(IN_CSV)
    focus = df[df["term"].eq("SR_x_D_full")].copy()
    focus["sig"] = focus["p"].map(sig)
    pivot = focus.pivot_table(
        index=["source_layer", "sm_label"],
        columns=["spec", "outcome"],
        values=["b", "p", "sig"],
        aggfunc="first",
    )
    pivot.columns = [
        "_".join(str(part) for part in col if part)
        for col in pivot.columns.to_flat_index()
    ]
    out = pivot.reset_index()
    out.to_csv(OUT_CSV, index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
