"""
Summarize theory-consistency for drought across all SM source-layer options.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJ_DIR = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
RUN_DIR = PROJ_DIR / "temp" / "2026-05-18_ggcp10_harvarea_agg_baseline_suite"
COEF_CSV = RUN_DIR / "ggcp10_drought_sm_screen_coefficients.csv"
SCREEN_CSV = RUN_DIR / "ggcp10_drought_sm_screen_summary.csv"


def sig_ok(p: float) -> bool:
    return p < 0.10


def main() -> None:
    df = pd.read_csv(COEF_CSV)
    rows: list[dict[str, object]] = []
    keys = [
        "mediator_type",
        "threshold_scheme",
        "source_layer",
        "sm_label",
        "mediator",
        "paired_control",
    ]
    for key, sub in df.groupby(keys, dropna=False):
        vals = {
            (row.equation, row.term): row
            for row in sub.itertuples(index=False)
        }
        m_main = vals[("mediator", "Main")]
        m_inter = vals[("mediator", "SR_x_Main")]
        y_main = vals[("outcome", "Main")]
        y_inter = vals[("outcome", "SR_x_Main")]
        y_m = vals[("outcome", "M")]

        mediator_type = key[0]
        if mediator_type == "raw_sm":
            mediator_main_ok = (m_main.b < 0) and sig_ok(m_main.p)
            mediator_inter_ok = (m_inter.b > 0) and sig_ok(m_inter.p)
            outcome_m_ok = (y_m.b > 0) and sig_ok(y_m.p)
        else:
            mediator_main_ok = (m_main.b > 0) and sig_ok(m_main.p)
            mediator_inter_ok = (m_inter.b < 0) and sig_ok(m_inter.p)
            outcome_m_ok = (y_m.b < 0) and sig_ok(y_m.p)

        outcome_main_ok = (y_main.b < 0) and sig_ok(y_main.p)
        outcome_inter_ok = (y_inter.b > 0) and sig_ok(y_inter.p)
        full_pass = all(
            [
                mediator_main_ok,
                mediator_inter_ok,
                outcome_main_ok,
                outcome_inter_ok,
                outcome_m_ok,
            ]
        )
        rows.append(
            {
                **dict(zip(keys, key)),
                "mediator_main_ok": mediator_main_ok,
                "mediator_inter_ok": mediator_inter_ok,
                "outcome_main_ok": outcome_main_ok,
                "outcome_inter_ok": outcome_inter_ok,
                "outcome_m_ok": outcome_m_ok,
                "full_pass": full_pass,
                "mediator_main_b": m_main.b,
                "mediator_inter_b": m_inter.b,
                "outcome_main_b": y_main.b,
                "outcome_inter_b": y_inter.b,
                "outcome_m_b": y_m.b,
                "mediator_main_p": m_main.p,
                "mediator_inter_p": m_inter.p,
                "outcome_main_p": y_main.p,
                "outcome_inter_p": y_inter.p,
                "outcome_m_p": y_m.p,
            }
        )

    out = pd.DataFrame(rows).sort_values(
        ["full_pass", "mediator_type", "threshold_scheme", "source_layer"],
        ascending=[False, True, True, True],
    )
    out.to_csv(SCREEN_CSV, index=False)
    print(f"Saved summary: {SCREEN_CSV}")
    print(out[["mediator_type", "threshold_scheme", "source_layer", "full_pass"]].to_string(index=False))


if __name__ == "__main__":
    main()
