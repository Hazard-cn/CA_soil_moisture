"""
Build humid-area (AI<1) irrigation IE/DE/TE figure for F4-B067 v2 outputs.

AI is defined as grid-mean et0_sum / pr_sum. Lower values are wetter. This
script uses AI<1.0 as the humid support threshold because it retains balanced
high/low irrigation support under the current B067 scale.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from f4_b067_full_bootstrap_counterfactual import (
    HAZARDS,
    SAMPLE_ID,
    Spec,
    b067_sample,
    fit_fe_from_frame,
    load_panel,
    prepare_model_frame,
    score_bootstrap,
    spec_roles,
)


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
OUTDIR = PROJ / "output/figures/f4_b067_v2"
TMPDIR = PROJ / "temp/2026-06-04_f4_b067_humid_ai_irrigation"
FIG_PATH = OUTDIR / "fig12_ai_lt1_irr_combined_iede.png"
TABLE_PATH = OUTDIR / "table12_ai_lt1_irr_combined_iede.csv"
DETAIL_PATH = TMPDIR / "f4_b067_ai_lt1_irrigation_iede_summary.csv"
SUPPORT_PATH = TMPDIR / "f4_b067_ai_lt1_irrigation_support.csv"

AI_THRESHOLD = 1.0
REPS = 500
SEED = 420612
IRR_GROUPS = ("high_irr", "low_irr")
EFFECTS = ("IE", "DE", "TE")
CA_LEVELS = ("P25", "P50", "P75")

HAZARD_LABELS = {"drought": "Drought", "heat": "Heat", "hotdry": "Hot-dry"}
IRR_LABELS = {"high_irr": "High irrigation", "low_irr": "Low irrigation"}
EFFECT_LABELS = {"IE": "Indirect (via SM)", "DE": "Direct (residual)", "TE": "Total"}
EFFECT_COLORS = {"IE": "#2166AC", "DE": "#E66101", "TE": "#111111"}


def run_humid_irrigation() -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(SEED)
    df = load_panel()
    base, meta = b067_sample(df)
    humid = base.loc[base["ai_pet_over_p_gridmean"].lt(AI_THRESHOLD)].copy()

    support_rows = []
    summary_rows = []
    for subgroup in IRR_GROUPS:
        sub = humid.loc[humid["irr_group"].astype(str).eq(subgroup)].copy()
        support_rows.append(
            {
                "sample_id": SAMPLE_ID,
                "threshold_rule": f"ai_pet_over_p_gridmean < {AI_THRESHOLD:g}",
                "subgroup": subgroup,
                "N_rows_before_dropna": int(len(sub)),
                "N_grids_before_dropna": int(sub["grid_id"].nunique()),
                "B067_N_rows": int(meta["N_sample"]),
                "B067_N_grids": int(meta["N_grids_sample"]),
            }
        )
        for hazard in HAZARDS:
            spec = Spec(hazard=hazard, transform="raw", mediator_tag="mean", branch="mean", mediator_base="gleam_smrz_mean")
            work, smeta = prepare_model_frame(sub, spec)
            y = str(smeta["y"])
            rhs_m = list(smeta["rhs_m"])
            rhs_y = list(smeta["rhs_y"])
            main = str(smeta["main"])
            inter = str(smeta["inter"])
            ca_values = dict(smeta["ca_values"])
            _y, _ca, _rhs_m, _rhs_y, _main, _inter, _role_m, _role_y = spec_roles(spec)
            fm = fit_fe_from_frame(work, spec.mediator, rhs_m)
            fy = fit_fe_from_frame(work, y, rhs_y)
            effect_summary, _effect_draws, _path_summary, _path_draws = score_bootstrap(
                fm,
                fy,
                spec,
                main,
                inter,
                ca_values,
                reps=REPS,
                rng=rng,
                batch_size=250,
            )
            for row in effect_summary.to_dict("records"):
                summary_rows.append(
                    {
                        "sample_id": SAMPLE_ID,
                        "layer": "ai_lt1_irrigation",
                        "threshold_rule": f"ai_pet_over_p_gridmean < {AI_THRESHOLD:g}",
                        "subgroup": subgroup,
                        "hazard": hazard,
                        "effect": row["effect"],
                        "ca_level": row["ca_level"],
                        "ca_value": row["ca_value"],
                        "estimate": row["point_est"],
                        "bs_se": row["bs_se"],
                        "ci_lo_95": row["ci_lo_pct"],
                        "ci_hi_95": row["ci_hi_pct"],
                        "ci_excludes_zero": int(row["ci_lo_pct"] * row["ci_hi_pct"] > 0),
                        "N_boot": int(row["N_boot"]),
                        "N_model": int(fm.n_model),
                        "N_grids": int(fm.n_grids),
                    }
                )
    return pd.DataFrame(summary_rows), pd.DataFrame(support_rows)


def plot_humid(summary: pd.DataFrame) -> None:
    fig, axes = plt.subplots(
        nrows=6,
        ncols=3,
        figsize=(11.2, 10.7),
        sharex=True,
        constrained_layout=True,
    )
    x = np.arange(len(CA_LEVELS))
    for row_i, (subgroup, effect) in enumerate((sg, ef) for sg in IRR_GROUPS for ef in EFFECTS):
        for col_i, hazard in enumerate(HAZARDS):
            ax = axes[row_i, col_i]
            cell = summary.loc[
                summary["subgroup"].eq(subgroup)
                & summary["effect"].eq(effect)
                & summary["hazard"].eq(hazard)
            ].copy()
            cell["ca_level"] = pd.Categorical(cell["ca_level"], categories=CA_LEVELS, ordered=True)
            cell.sort_values("ca_level", inplace=True)
            y = cell["estimate"].to_numpy(dtype=float)
            lo = cell["ci_lo_95"].to_numpy(dtype=float)
            hi = cell["ci_hi_95"].to_numpy(dtype=float)
            sig = cell["ci_excludes_zero"].to_numpy(dtype=bool)
            color = EFFECT_COLORS[effect]
            ax.axhline(0, color="#777777", linewidth=0.75, linestyle="--", zorder=1)
            ax.plot(x, y, color=color, linewidth=1.15, zorder=2)
            ax.vlines(x, lo, hi, color=color, linewidth=1.0, alpha=0.82, zorder=2)
            ax.scatter(x[sig], y[sig], s=28, color=color, edgecolor=color, linewidth=0.8, zorder=3)
            ax.scatter(x[~sig], y[~sig], s=28, facecolor="white", edgecolor=color, linewidth=1.0, zorder=3)
            ax.set_xticks(x)
            ax.set_xticklabels(CA_LEVELS, fontsize=8)
            if row_i == 0:
                ax.set_title(HAZARD_LABELS[hazard], fontsize=11, fontweight="bold")
            if col_i == 2:
                ax.text(
                    1.03,
                    0.5,
                    f"{IRR_LABELS[subgroup]} | {EFFECT_LABELS[effect]}",
                    transform=ax.transAxes,
                    va="center",
                    ha="left",
                    fontsize=8.5,
                    fontweight="bold",
                )
            if col_i == 0:
                ax.set_ylabel("Conditional effect", fontsize=9)
            ax.grid(axis="y", color="#E6E6E6", linewidth=0.7)
            ax.grid(axis="x", color="#EEEEEE", linewidth=0.7)
            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)
            ax.spines["left"].set_color("#C0C0C0")
            ax.spines["bottom"].set_color("#C0C0C0")
            ax.tick_params(axis="y", labelsize=7)

    fig.suptitle("Humid areas (AI<1): IE / DE / TE across SR levels by irrigation", fontsize=14, fontweight="bold")
    fig.text(0.5, 0.03, "Straw return level", ha="center", fontsize=10)
    FIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_PATH, dpi=300, facecolor="white")
    plt.close(fig)


def append_caption() -> None:
    cap = OUTDIR / "figure_captions.md"
    text = "\n\n---\n\n## Fig 12. Humid areas (AI<1) irrigation combined panel\n"
    text += "![fig12](fig12_ai_lt1_irr_combined_iede.png)\n\n"
    text += (
        "This figure restricts B067 to humid grids defined by grid-mean PET/P < 1. "
        "Rows split irrigation group and effect type, so near-zero IE/DE/TE series do not overlap. "
        "It is the humid counterpart to Fig 11 and should be read as a boundary-condition check.\n"
    )
    with cap.open("a", encoding="utf-8") as f:
        f.write(text)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    TMPDIR.mkdir(parents=True, exist_ok=True)
    summary, support = run_humid_irrigation()
    summary.to_csv(DETAIL_PATH, index=False, encoding="utf-8")
    summary.to_csv(TABLE_PATH, index=False, encoding="utf-8")
    support.to_csv(SUPPORT_PATH, index=False, encoding="utf-8")
    plot_humid(summary)
    append_caption()
    print(
        {
            "rows": int(len(summary)),
            "support": support.to_dict("records"),
            "table": str(TABLE_PATH),
            "figure": str(FIG_PATH),
            "detail": str(DETAIL_PATH),
        },
        flush=True,
    )


if __name__ == "__main__":
    main()
