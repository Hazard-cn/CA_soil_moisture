"""Re-estimate and plot B067 irrigation heterogeneity with median irr_frac splits."""

from __future__ import annotations

import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

from f4_b067_full_bootstrap_counterfactual import (
    HAZARDS,
    SAMPLE_ID,
    Spec,
    b067_sample,
    fit_fe_from_frame,
    load_panel,
    prepare_model_frame,
    score_bootstrap,
)


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
OUTDIR = PROJ / "output/figures/f4_b067_v2"
TMPDIR = PROJ / "temp/2026-06-04_f4_b067_median_irrigation"
REPORT_MD = PROJ / "quality_reports/2026-06-04_b067_median_irrigation_split_figures.md"

REPS = 500
SEED = 420614
EFFECTS = ("IE", "DE", "TE")
CA_LEVELS = ("P25", "P50", "P75")
GROUPS = ("high_irr_median", "low_irr_median")
LAYERS = {
    "heterogeneity_median_irr": {"label": "B067 full", "ai_rule": "all"},
    "ai_gt2_median_irr": {"label": "Arid areas (AI>2)", "ai_rule": "gt2"},
    "ai_lt1_median_irr": {"label": "Humid areas (AI<1)", "ai_rule": "lt1"},
}

HAZARD_LABELS = {"drought": "Drought", "heat": "Heat", "hotdry": "Hot-dry"}
GROUP_LABELS = {
    "high_irr_median": "High irrigation",
    "low_irr_median": "Low irrigation",
}
EFFECT_LABELS = {"IE": "Indirect (via SM)", "DE": "Direct (residual)", "TE": "Total"}
EFFECT_COLORS = {"IE": "#2166AC", "DE": "#E66101", "TE": "#111111"}
GROUP_COLORS = {"high_irr_median": "#2166AC", "low_irr_median": "#B2182B"}
GROUP_MARKERS = {"high_irr_median": "o", "low_irr_median": "s"}


def layer_sample(base: pd.DataFrame, ai_rule: str) -> pd.DataFrame:
    if ai_rule == "all":
        return base.copy()
    if ai_rule == "gt2":
        return base.loc[base["ai_pet_over_p_gridmean"].gt(2)].copy()
    if ai_rule == "lt1":
        return base.loc[base["ai_pet_over_p_gridmean"].lt(1)].copy()
    raise ValueError(ai_rule)


def add_median_groups(df: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    out = df.copy()
    threshold = float(out["irr_frac"].median())
    out["irr_median_group"] = np.where(out["irr_frac"].ge(threshold), "high_irr_median", "low_irr_median")
    return out, threshold


def run_estimates() -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(SEED)
    panel = load_panel()
    base, meta = b067_sample(panel)

    support_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    skipped_rows: list[dict[str, object]] = []

    for layer, info in LAYERS.items():
        layer_df, threshold = add_median_groups(layer_sample(base, str(info["ai_rule"])))
        for subgroup in GROUPS:
            sub = layer_df.loc[layer_df["irr_median_group"].eq(subgroup)].copy()
            support_rows.append(
                {
                    "sample_id": SAMPLE_ID,
                    "layer": layer,
                    "layer_label": info["label"],
                    "subgroup": subgroup,
                    "irr_frac_median_threshold": threshold,
                    "split_rule": "high if irr_frac >= threshold; low if irr_frac < threshold",
                    "N_rows_before_dropna": int(len(sub)),
                    "N_grids_before_dropna": int(sub["grid_id"].nunique()),
                    "B067_N_rows": int(meta["N_sample"]),
                    "B067_N_grids": int(meta["N_grids_sample"]),
                }
            )
            for hazard in HAZARDS:
                spec = Spec(hazard=hazard, transform="raw", mediator_tag="mean", branch="mean", mediator_base="gleam_smrz_mean")
                try:
                    work, smeta = prepare_model_frame(sub, spec)
                    rhs_m = list(smeta["rhs_m"])
                    rhs_y = list(smeta["rhs_y"])
                    main = str(smeta["main"])
                    inter = str(smeta["inter"])
                    ca_values = dict(smeta["ca_values"])
                    fm = fit_fe_from_frame(work, spec.mediator, rhs_m)
                    fy = fit_fe_from_frame(work, str(smeta["y"]), rhs_y)
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
                except Exception as exc:  # noqa: BLE001
                    skipped_rows.append(
                        {
                            "sample_id": SAMPLE_ID,
                            "layer": layer,
                            "subgroup": subgroup,
                            "hazard": hazard,
                            "reason": str(exc),
                            "N_rows_before_dropna": int(len(sub)),
                            "N_grids_before_dropna": int(sub["grid_id"].nunique()),
                        }
                    )
                    continue

                for row in effect_summary.to_dict("records"):
                    summary_rows.append(
                        {
                            "sample_id": SAMPLE_ID,
                            "layer": layer,
                            "layer_label": info["label"],
                            "subgroup": subgroup,
                            "subgroup_label": GROUP_LABELS[subgroup],
                            "hazard": hazard,
                            "effect": row["effect"],
                            "ca_level": row["ca_level"],
                            "ca_value": float(row["ca_value"]),
                            "estimate": float(row["point_est"]),
                            "bs_se": float(row["bs_se"]),
                            "ci_lo_95": float(row["ci_lo_pct"]),
                            "ci_hi_95": float(row["ci_hi_pct"]),
                            "ci_excludes_zero": int(float(row["ci_lo_pct"]) * float(row["ci_hi_pct"]) > 0),
                            "N_boot": int(row["N_boot"]),
                            "N_model": int(fm.n_model),
                            "N_grids": int(fm.n_grids),
                            "irr_frac_median_threshold": threshold,
                        }
                    )

    support = pd.DataFrame(support_rows)
    summary = pd.DataFrame(summary_rows)
    skipped = pd.DataFrame(skipped_rows)
    support.to_csv(TMPDIR / "f4_b067_median_irrigation_support.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(TMPDIR / "f4_b067_median_irrigation_iede_summary.csv", index=False, encoding="utf-8-sig")
    skipped.to_csv(TMPDIR / "f4_b067_median_irrigation_skipped.csv", index=False, encoding="utf-8-sig")
    return summary, support


def prep_plot_data(summary: pd.DataFrame, layer: str, subgroup: str | None = None) -> pd.DataFrame:
    sub = summary.loc[summary["layer"].eq(layer)].copy()
    if subgroup is not None:
        sub = sub.loc[sub["subgroup"].eq(subgroup)].copy()
    sub["ca_level"] = pd.Categorical(sub["ca_level"], categories=CA_LEVELS, ordered=True)
    sub["effect"] = pd.Categorical(sub["effect"], categories=EFFECTS, ordered=True)
    sub["hazard"] = pd.Categorical(sub["hazard"], categories=HAZARDS, ordered=True)
    sub.sort_values(["subgroup", "effect", "hazard", "ca_level"], inplace=True)
    return sub


def plot_single_group(summary: pd.DataFrame, layer: str, subgroup: str, path: Path) -> None:
    data = prep_plot_data(summary, layer, subgroup)
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.9), sharex=True, constrained_layout=True)
    x = np.arange(len(CA_LEVELS))
    for col, hazard in enumerate(HAZARDS):
        ax = axes[col]
        for effect in EFFECTS:
            cell = data.loc[data["hazard"].eq(hazard) & data["effect"].eq(effect)]
            y = cell["estimate"].to_numpy(dtype=float)
            lo = cell["ci_lo_95"].to_numpy(dtype=float)
            hi = cell["ci_hi_95"].to_numpy(dtype=float)
            sig = cell["ci_excludes_zero"].to_numpy(dtype=bool)
            color = EFFECT_COLORS[effect]
            ax.plot(x, y, color=color, linewidth=1.0, label=EFFECT_LABELS[effect] if col == 0 else None)
            ax.vlines(x, lo, hi, color=color, linewidth=0.85, alpha=0.8)
            ax.scatter(x[sig], y[sig], s=24, color=color, edgecolor=color, linewidth=0.7)
            ax.scatter(x[~sig], y[~sig], s=24, facecolor="white", edgecolor=color, linewidth=0.9)
        ax.axhline(0, color="#777777", linewidth=0.7, linestyle="--")
        ax.set_xticks(x)
        ax.set_xticklabels(CA_LEVELS)
        ax.set_title(HAZARD_LABELS[hazard], fontsize=10, fontweight="bold")
        ax.grid(axis="y", color="#E6E6E6", linewidth=0.65)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    axes[0].set_ylabel("Conditional effect")
    fig.suptitle(f"{LAYERS[layer]['label']}: {GROUP_LABELS[subgroup]} median irrigation split", fontsize=12, fontweight="bold")
    fig.text(0.5, 0.01, "Straw return level", ha="center", fontsize=9)
    fig.legend(loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.055), frameon=False)
    fig.savefig(path, dpi=300, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def plot_combined(summary: pd.DataFrame, layer: str, path: Path) -> None:
    data = prep_plot_data(summary, layer)
    fig, axes = plt.subplots(6, 3, figsize=(11.2, 10.7), sharex=True, constrained_layout=True)
    x = np.arange(len(CA_LEVELS))
    row_pairs = [(group, effect) for group in GROUPS for effect in EFFECTS]
    for row, (group, effect) in enumerate(row_pairs):
        for col, hazard in enumerate(HAZARDS):
            ax = axes[row, col]
            cell = data.loc[data["subgroup"].eq(group) & data["effect"].eq(effect) & data["hazard"].eq(hazard)]
            y = cell["estimate"].to_numpy(dtype=float)
            lo = cell["ci_lo_95"].to_numpy(dtype=float)
            hi = cell["ci_hi_95"].to_numpy(dtype=float)
            sig = cell["ci_excludes_zero"].to_numpy(dtype=bool)
            color = EFFECT_COLORS[effect]
            ax.axhline(0, color="#777777", linewidth=0.7, linestyle="--", zorder=1)
            ax.plot(x, y, color=color, linewidth=1.1, zorder=2)
            ax.vlines(x, lo, hi, color=color, linewidth=0.95, alpha=0.82, zorder=2)
            ax.scatter(x[sig], y[sig], s=27, color=color, edgecolor=color, linewidth=0.75, zorder=3)
            ax.scatter(x[~sig], y[~sig], s=27, facecolor="white", edgecolor=color, linewidth=0.95, zorder=3)
            ax.set_xticks(x)
            ax.set_xticklabels(CA_LEVELS, fontsize=8)
            if row == 0:
                ax.set_title(HAZARD_LABELS[hazard], fontsize=10.5, fontweight="bold")
            if col == 2:
                ax.text(
                    1.03,
                    0.5,
                    f"{GROUP_LABELS[group]} | {EFFECT_LABELS[effect]}",
                    transform=ax.transAxes,
                    va="center",
                    ha="left",
                    fontsize=8.2,
                    fontweight="bold",
                )
            if col == 0:
                ax.set_ylabel("Conditional effect", fontsize=8.5)
            ax.grid(axis="y", color="#E6E6E6", linewidth=0.65)
            ax.grid(axis="x", color="#EEEEEE", linewidth=0.55)
            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)
            ax.spines["left"].set_color("#C0C0C0")
            ax.spines["bottom"].set_color("#C0C0C0")
            ax.tick_params(axis="y", labelsize=7)

    fig.suptitle(f"{LAYERS[layer]['label']}: IE / DE / TE across SR levels by median irrigation split", fontsize=13, fontweight="bold")
    fig.text(0.5, 0.03, "Straw return level", ha="center", fontsize=9.5)
    fig.savefig(path, dpi=300, facecolor="white")
    plt.close(fig)


def plot_combined_group_overlay(summary: pd.DataFrame, layer: str, path: Path) -> None:
    data = prep_plot_data(summary, layer)
    fig, axes = plt.subplots(3, 3, figsize=(11.2, 7.1), sharex=True, constrained_layout=True)
    x = np.arange(len(CA_LEVELS))
    for row, effect in enumerate(EFFECTS):
        for col, hazard in enumerate(HAZARDS):
            ax = axes[row, col]
            for group in GROUPS:
                cell = data.loc[data["subgroup"].eq(group) & data["effect"].eq(effect) & data["hazard"].eq(hazard)].copy()
                cell.sort_values("ca_level", inplace=True)
                y = cell["estimate"].to_numpy(dtype=float)
                lo = cell["ci_lo_95"].to_numpy(dtype=float)
                hi = cell["ci_hi_95"].to_numpy(dtype=float)
                sig = cell["ci_excludes_zero"].to_numpy(dtype=bool)
                color = GROUP_COLORS[group]
                marker = GROUP_MARKERS[group]
                offset = -0.045 if group == "high_irr_median" else 0.045
                xx = x + offset
                ax.plot(xx, y, color=color, linewidth=1.15, label=GROUP_LABELS[group] if row == 0 and col == 0 else None, zorder=2)
                ax.vlines(xx, lo, hi, color=color, linewidth=0.9, alpha=0.82, zorder=2)
                ax.scatter(xx[sig], y[sig], s=27, marker=marker, color=color, edgecolor=color, linewidth=0.75, zorder=3)
                ax.scatter(xx[~sig], y[~sig], s=27, marker=marker, facecolor="white", edgecolor=color, linewidth=0.95, zorder=3)
            ax.axhline(0, color="#777777", linewidth=0.7, linestyle="--", zorder=1)
            ax.set_xticks(x)
            ax.set_xticklabels(CA_LEVELS, fontsize=8)
            if row == 0:
                ax.set_title(HAZARD_LABELS[hazard], fontsize=10.5, fontweight="bold")
            if col == 0:
                ax.set_ylabel(f"{EFFECT_LABELS[effect]}\nConditional effect", fontsize=8.5)
            ax.grid(axis="y", color="#E6E6E6", linewidth=0.65)
            ax.grid(axis="x", color="#EEEEEE", linewidth=0.55)
            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)
            ax.spines["left"].set_color("#C0C0C0")
            ax.spines["bottom"].set_color("#C0C0C0")
            ax.tick_params(axis="y", labelsize=7)

    fig.suptitle(f"{LAYERS[layer]['label']}: High vs low irrigation within each IE/DE/TE panel", fontsize=13, fontweight="bold")
    fig.text(0.5, 0.03, "Straw return level", ha="center", fontsize=9.5)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.005), frameon=False)
    fig.savefig(path, dpi=300, facecolor="white")
    plt.close(fig)


def redraw_overlay_fig11_fig12() -> None:
    summary_path = TMPDIR / "f4_b067_median_irrigation_iede_summary.csv"
    if not summary_path.exists():
        summary, _support = run_estimates()
    else:
        summary = pd.read_csv(summary_path)
    paths = [
        OUTDIR / "fig11_ai2_irr_median_combined_iede.png",
        OUTDIR / "fig12_ai_lt1_irr_median_combined_iede.png",
    ]
    plot_combined_group_overlay(summary, "ai_gt2_median_irr", paths[0])
    plot_combined_group_overlay(summary, "ai_lt1_median_irr", paths[1])
    validate_outputs(summary, [
        OUTDIR / "fig8_irr_median_high_irr_iede.png",
        OUTDIR / "fig9_irr_median_low_irr_iede.png",
        OUTDIR / "fig10_irr_median_combined_iede.png",
        *paths,
    ])
    print({"redrawn": [str(p) for p in paths]}, flush=True)


def write_tables_for_figures(summary: pd.DataFrame) -> None:
    outputs = {
        "table8_irr_median_high_irr_iede.csv": ("heterogeneity_median_irr", "high_irr_median"),
        "table9_irr_median_low_irr_iede.csv": ("heterogeneity_median_irr", "low_irr_median"),
        "table10_irr_median_combined_iede.csv": ("heterogeneity_median_irr", None),
        "table11_ai2_irr_median_combined_iede.csv": ("ai_gt2_median_irr", None),
        "table12_ai_lt1_irr_median_combined_iede.csv": ("ai_lt1_median_irr", None),
    }
    for name, (layer, subgroup) in outputs.items():
        prep_plot_data(summary, layer, subgroup).to_csv(OUTDIR / name, index=False, encoding="utf-8-sig")


def validate_outputs(summary: pd.DataFrame, figure_paths: list[Path]) -> None:
    expected = len(LAYERS) * len(GROUPS) * len(HAZARDS) * len(EFFECTS) * len(CA_LEVELS)
    if len(summary) != expected:
        raise RuntimeError(f"summary row count {len(summary)} != expected {expected}")
    counts = summary.groupby(["layer", "subgroup", "hazard", "effect"], observed=True)["ca_level"].nunique()
    if int(counts.min()) != 3 or int(counts.max()) != 3:
        raise RuntimeError("not every layer/subgroup/hazard/effect has three SR levels")
    for path in figure_paths:
        with Image.open(path) as img:
            if img.size[0] <= 0 or img.size[1] <= 0:
                raise RuntimeError(f"empty figure: {path}")


def write_report(summary: pd.DataFrame, support: pd.DataFrame, figure_paths: list[Path], elapsed: float) -> None:
    support_short = support.loc[:, ["layer", "subgroup", "irr_frac_median_threshold", "N_rows_before_dropna", "N_grids_before_dropna"]].copy()
    lines = [
        "# B067 median irrigation split figures",
        "",
        "本轮灌溉异质性不使用已有 `irr_group`，而是在对应分析样本内按 `irr_frac` 中位数重新切分。",
        "",
        "切分规则：`high_irr_median = irr_frac >= median(irr_frac)`；`low_irr_median = irr_frac < median(irr_frac)`。",
        "",
        "## Support",
        "",
        "| layer | subgroup | irr_frac median | obs | grids |",
        "|---|---|---:|---:|---:|",
    ]
    for row in support_short.to_dict("records"):
        lines.append(
            f"| {row['layer']} | {row['subgroup']} | {row['irr_frac_median_threshold']:.6g} | "
            f"{int(row['N_rows_before_dropna'])} | {int(row['N_grids_before_dropna'])} |"
        )
    lines.extend(["", "## Figures", ""])
    for path in figure_paths:
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "## Tables",
            "",
            "- `temp/2026-06-04_f4_b067_median_irrigation/f4_b067_median_irrigation_iede_summary.csv`",
            "- `temp/2026-06-04_f4_b067_median_irrigation/f4_b067_median_irrigation_support.csv`",
            "- `output/figures/f4_b067_v2/table8_irr_median_high_irr_iede.csv`",
            "- `output/figures/f4_b067_v2/table9_irr_median_low_irr_iede.csv`",
            "- `output/figures/f4_b067_v2/table10_irr_median_combined_iede.csv`",
            "- `output/figures/f4_b067_v2/table11_ai2_irr_median_combined_iede.csv`",
            "- `output/figures/f4_b067_v2/table12_ai_lt1_irr_median_combined_iede.csv`",
            "",
            f"运行耗时：{elapsed:.1f} 秒。",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    start = time.time()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    TMPDIR.mkdir(parents=True, exist_ok=True)
    summary, support = run_estimates()
    write_tables_for_figures(summary)
    figure_paths = [
        OUTDIR / "fig8_irr_median_high_irr_iede.png",
        OUTDIR / "fig9_irr_median_low_irr_iede.png",
        OUTDIR / "fig10_irr_median_combined_iede.png",
        OUTDIR / "fig11_ai2_irr_median_combined_iede.png",
        OUTDIR / "fig12_ai_lt1_irr_median_combined_iede.png",
    ]
    plot_single_group(summary, "heterogeneity_median_irr", "high_irr_median", figure_paths[0])
    plot_single_group(summary, "heterogeneity_median_irr", "low_irr_median", figure_paths[1])
    plot_combined(summary, "heterogeneity_median_irr", figure_paths[2])
    plot_combined(summary, "ai_gt2_median_irr", figure_paths[3])
    plot_combined(summary, "ai_lt1_median_irr", figure_paths[4])
    validate_outputs(summary, figure_paths)
    elapsed = time.time() - start
    write_report(summary, support, figure_paths, elapsed)
    print(
        {
            "summary_rows": int(len(summary)),
            "support": support.to_dict("records"),
            "figures": [str(p) for p in figure_paths],
            "elapsed_seconds": elapsed,
        },
        flush=True,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--redraw-overlay-fig11-fig12", action="store_true")
    ns = parser.parse_args()
    if ns.redraw_overlay_fig11_fig12:
        redraw_overlay_fig11_fig12()
    else:
        main()
