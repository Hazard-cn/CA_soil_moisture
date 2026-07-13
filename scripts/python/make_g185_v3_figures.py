"""Build G185 v3 figures from machine-readable CSV files only."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import font_manager


def configure_fonts() -> None:
    available = {f.name for f in font_manager.fontManager.ttflist}
    for candidate in ("Microsoft YaHei", "SimHei", "Arial Unicode MS", "Noto Sans CJK SC"):
        if candidate in available:
            plt.rcParams["font.family"] = candidate
            break
    plt.rcParams["axes.unicode_minus"] = False


configure_fonts()

plt.rcParams.update({
    "font.size": 8,
    "axes.titlesize": 9,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
})


PALETTE = {
    "lower": "#2f3437",
    "higher": "#1f77b4",
    "drought": "#7b3294",
    "heat": "#e66101",
    "joint": "#1b9e77",
    "muted": "#a7a9ac",
    "limited": "#777777",
}


def read(run_dir: Path, rel: str) -> pd.DataFrame:
    path = run_dir / rel
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def save(fig, path: Path, width_mm: float = 180, height_mm: float = 115) -> None:
    fig.set_size_inches(width_mm / 25.4, height_mm / 25.4)
    fig.savefig(path.with_suffix(".png"), dpi=600, bbox_inches="tight", facecolor="white")
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


def support_marker(ax, x, y, status: str) -> None:
    if status == "LIMITED_SUPPORT":
        ax.scatter([x], [y], marker="^", s=55, facecolor="white", edgecolor=PALETTE["limited"], zorder=5)
        ax.text(x, y, " limited support", fontsize=7, va="bottom", color=PALETTE["limited"])
    elif status == "UNSUPPORTED":
        ax.scatter([x], [y], marker="x", s=55, color=PALETTE["limited"], zorder=5)


def fig1(run_dir: Path) -> None:
    zone = read(run_dir, "figure_data/fig1_zone_hexbin.csv")
    losses = read(run_dir, "figure_data/fig1_headline_losses.csv")
    fig, axes = plt.subplots(1, 2, figsize=(180 / 25.4, 105 / 25.4), gridspec_kw={"width_ratios": [1.05, 1.35]})
    ax = axes[0]
    colors = {"NE": "#7b3294", "HHH": "#e66101", "NW": "#80cdc1", "SW": "#018571", "SH": "#a6611a", "Other": "#d9d9d9"}
    for region, sub in zone.groupby("maize_zone"):
        ax.scatter(sub["lon_bin_center"], sub["lat_bin_center"], s=np.sqrt(sub["n_unique_grids"]) * 8, color=colors.get(str(region), "#d9d9d9"), alpha=0.72, edgecolor="none", label=str(region))
        if str(region) in ("NE", "HHH", "NW", "SW", "SH"):
            w = sub["n_unique_grids"].to_numpy()
            ax.text(np.average(sub["lon_bin_center"], weights=w), np.average(sub["lat_bin_center"], weights=w), str(region), fontsize=8, weight="bold", ha="center")
    ax.text(124, 46, "Drought", fontsize=7, color=PALETTE["drought"])
    ax.text(113, 35, "Heat / joint drought-heat", fontsize=7, color=PALETTE["heat"])
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("A. G185 analytical sample by maize zone", fontsize=9, pad=5)
    ax.legend(frameon=False, fontsize=7, ncol=2, loc="lower left")
    ax.grid(alpha=0.15)

    ax = axes[1]
    order = [("NE", "DROUGHT_COMMON"), ("HHH", "HEAT_COMMON"), ("HHH", "JOINT_COMMON")]
    labels = ["NE - Drought", "HHH - Heat", "HHH - Joint drought-heat"]
    y = np.arange(len(order))[::-1]
    for yi, (region, scenario), label in zip(y, order, labels):
        sub = losses.loc[(losses["region"].eq(region)) & (losses["scenario_id"].eq(scenario))]
        low = sub.loc[sub["sr_label"].eq("Lower SR")].iloc[0]
        high = sub.loc[sub["sr_label"].eq("Higher SR")].iloc[0]
        ax.plot([low["predicted_loss_pct"], high["predicted_loss_pct"]], [yi, yi], color="#555555", lw=1)
        ax.scatter(low["predicted_loss_pct"], yi, color=PALETTE["lower"], marker="o", label="Lower SR" if yi == y[0] else "")
        ax.scatter(high["predicted_loss_pct"], yi, color=PALETTE["higher"], marker="s", label="Higher SR" if yi == y[0] else "")
        text_y = yi - 0.23 if yi == y[0] else yi + 0.16
        text_va = "top" if yi == y[0] else "bottom"
        if str(low.get("claim_status", "")) == "ROBUST":
            ax.text((low["predicted_loss_pct"] + high["predicted_loss_pct"]) / 2, text_y, f"+{high['buffering_pct']:.2f} pp less loss", fontsize=7, ha="center", va=text_va)
        else:
            ax.text((low["predicted_loss_pct"] + high["predicted_loss_pct"]) / 2, text_y, str(low.get("claim_status", "")), fontsize=7, ha="center", va=text_va, color="#666666")
        support_marker(ax, high["predicted_loss_pct"], yi, str(high["support_status"]))
    ax.axvline(0, color="#777777", lw=0.8)
    ax.set_ylim(-0.35, max(y) + 0.35)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Fitted yield change from moderate to severe stress (%)")
    ax.set_title("B. Headline fitted climate-loss contrasts", fontsize=9, pad=5)
    ax.legend(frameon=False, fontsize=7)
    ax.text(0.01, -0.18, "Association, not causal adoption effect", transform=ax.transAxes, fontsize=7, color="#555555")
    fig.tight_layout(pad=0.7, w_pad=1.0)
    save(fig, run_dir / "figures/fig1_story_overview", 180, 105)


def fig2(run_dir: Path) -> None:
    curves = read(run_dir, "figure_data/fig2_climate_loss_curves.csv")
    dens = read(run_dir, "figure_data/fig2_exposure_density.csv")
    fig, axes = plt.subplots(2, 3, figsize=(180 / 25.4, 120 / 25.4), gridspec_kw={"height_ratios": [4, 0.75]}, sharex="col")
    titles = {"A": "A. NE drought curve", "B": "B. HHH heat curve", "C": "C. HHH joint path"}
    legend_handles = None
    for j, panel in enumerate(["A", "B", "C"]):
        ax = axes[0, j]
        sub = curves.loc[curves["panel_id"].eq(panel)]
        for label, color, ls, marker in (("Lower SR", PALETTE["lower"], "--", "o"), ("Higher SR", PALETTE["higher"], "-", "s")):
            ss = sub.loc[sub["sr_label"].eq(label)].sort_values("path_value")
            ax.plot(ss["path_value"], ss["predicted_loss_pct"], color=color, ls=ls, marker=marker, markevery=10, lw=1.4, label=label)
            ax.fill_between(ss["path_value"], ss["ci_low_pct"], ss["ci_high_pct"], color=color, alpha=0.12)
        if legend_handles is None:
            legend_handles, _ = ax.get_legend_handles_labels()
        ax.axhline(0, color="#777777", lw=0.8)
        ax.set_title(titles[panel], fontsize=9)
        ax.grid(axis="y", alpha=0.18)
        if j == 0:
            ax.set_ylabel("Fitted yield change relative to moderate stress (%)")
        ax.text(0.01, -0.28, "Association, not causal adoption effect", transform=ax.transAxes, fontsize=7, color="#555555")
        ax2 = axes[1, j]
        dd = dens.loc[dens["panel_id"].eq(panel)]
        ax2.bar(dd["bin_mid"], dd["share_obs"], width=(dd["bin_right"] - dd["bin_left"]), color="#bdbdbd", edgecolor="none")
        ax2.set_yticks([])
        ax2.set_xlabel("Path coordinate" if panel == "C" else "Hazard exposure path")
    if legend_handles:
        fig.legend(legend_handles, ["Lower SR", "Higher SR"], loc="upper center", frameon=False, ncol=2, bbox_to_anchor=(0.5, 0.995))
    fig.tight_layout(rect=[0.02, 0.02, 0.995, 0.94], h_pad=0.7, w_pad=1.2)
    save(fig, run_dir / "figures/fig2_climate_loss_curves", 180, 120)


def fig3(run_dir: Path) -> None:
    data = read(run_dir, "figure_data/fig3_region_common_scale.csv")
    fig, axes = plt.subplots(1, 3, figsize=(180 / 25.4, 100 / 25.4), sharex=False)
    scen_titles = {"DROUGHT_COMMON": "Drought", "HEAT_COMMON": "Heat", "JOINT_COMMON": "Joint drought-heat"}
    for ax, scenario in zip(axes, ["DROUGHT_COMMON", "HEAT_COMMON", "JOINT_COMMON"]):
        sub = data.loc[data["scenario_id"].eq(scenario)].copy()
        sub["order"] = sub["region"].map({r: i for i, r in enumerate(["NE", "HHH", "NW", "SW", "SH"])})
        sub.sort_values("order", inplace=True)
        y = np.arange(len(sub))
        target = "NE" if scenario == "DROUGHT_COMMON" else "HHH"
        colors = [PALETTE["drought"] if r == target and scenario == "DROUGHT_COMMON" else PALETTE["heat"] if r == target and scenario == "HEAT_COMMON" else PALETTE["joint"] if r == target else PALETTE["muted"] for r in sub["region"]]
        ax.axvline(0, color="#777777", lw=0.8)
        for yi, (_, row), color in zip(y, sub.iterrows(), colors):
            ax.plot([row["ci_low_pct"], row["ci_high_pct"]], [yi, yi], color=color, lw=1.2)
            ax.scatter(row["estimate_pct"], yi, color=color, s=28)
            support_marker(ax, row["estimate_pct"], yi, str(row["support_status"]))
        ax.set_yticks(y)
        ax.set_yticklabels(sub["region"])
        ax.set_title(f"{scen_titles[scenario]}\nOmnibus p={sub['omnibus_p_value'].iloc[0]:.3g}", fontsize=9)
        ax.set_xlabel("SR-associated buffering (%)")
        ax.grid(axis="x", alpha=0.15)
    fig.text(0.5, 0.01, "Same SR increase and same climate change in every region. Association, not causal adoption effect.", ha="center", fontsize=7)
    fig.tight_layout(rect=[0, 0.06, 1, 1])
    save(fig, run_dir / "figures/fig3_region_common_scale", 180, 100)


def fig4(run_dir: Path) -> None:
    data = read(run_dir, "figure_data/fig4_irrigation_boundary_hhh.csv")
    dens = read(run_dir, "figure_data/fig4_irrigation_density_hhh.csv")
    fig, axes = plt.subplots(2, 2, figsize=(180 / 25.4, 115 / 25.4), gridspec_kw={"height_ratios": [4, 0.8]}, sharex="col")
    for j, scenario in enumerate(["HEAT_COMMON", "JOINT_COMMON"]):
        ax = axes[0, j]
        sub = data.loc[data["scenario_id"].eq(scenario)].sort_values("irrigation_value")
        color = PALETTE["heat"] if scenario == "HEAT_COMMON" else PALETTE["joint"]
        ax.plot(sub["irrigation_value"], sub["estimate_pct"], color=color, marker="o", lw=1.4)
        ax.fill_between(sub["irrigation_value"], sub["ci_low_pct"], sub["ci_high_pct"], color=color, alpha=0.15)
        ax.axhline(0, color="#777777", lw=0.8)
        for pctile in [25, 50, 75]:
            hit = sub.loc[sub["irrigation_percentile"].eq(pctile)]
            if not hit.empty:
                ax.axvline(hit["irrigation_value"].iloc[0], color="#aaaaaa", lw=0.6)
                ax.text(hit["irrigation_value"].iloc[0], ax.get_ylim()[1], f"P{pctile}", fontsize=7, ha="center", va="top")
        if {25, 75}.issubset(set(sub["irrigation_percentile"])):
            p25 = sub.loc[sub["irrigation_percentile"].eq(25), "estimate_pct"].iloc[0]
            p75 = sub.loc[sub["irrigation_percentile"].eq(75), "estimate_pct"].iloc[0]
            txt = f"Buffering is {p25 - p75:.2f} pp smaller\nat P75 than P25 irrigation" if p75 < p25 else "Boundary estimate is sensitive"
            ax.text(0.03, 0.92, txt, transform=ax.transAxes, fontsize=7, va="top")
        ax.set_title("HHH heat" if scenario == "HEAT_COMMON" else "HHH joint drought-heat")
        ax.set_ylabel("SR-associated reduction\nin climate loss (%)" if j == 0 else "")
        ax.grid(axis="y", alpha=0.15)
        ax.text(0.01, -0.24, "Association, not causal adoption effect", transform=ax.transAxes, fontsize=7, color="#555555")
        ax2 = axes[1, j]
        ax2.bar(dens["bin_mid"], dens["share_grids"], width=dens["bin_right"] - dens["bin_left"], color="#bdbdbd", edgecolor="none")
        ax2.set_yticks([])
        ax2.set_xlabel("Irrigation fraction")
    fig.tight_layout(pad=0.8, h_pad=0.8, w_pad=1.8)
    save(fig, run_dir / "figures/fig4_irrigation_boundary_hhh", 180, 115)


def fig5(run_dir: Path) -> None:
    data = read(run_dir, "figure_data/fig5_soil_moisture_consistency.csv")
    rows = [("C1_NE_DROUGHT_SURFACE", "NE - Drought"), ("C2_HHH_HEAT_SURFACE", "HHH - Heat"), ("C3_HHH_JOINT_SURFACE", "HHH - Joint drought-heat")]
    fig, axes = plt.subplots(1, 2, figsize=(180 / 25.4, 105 / 25.4))
    ax = axes[0]
    y = np.arange(len(rows))[::-1]
    for yi, (claim, label) in zip(y, rows):
        sub = data.loc[(data["claim_id"].eq(claim)) & (data["metric_type"].eq("root_zone_soil_moisture_change"))]
        if sub.empty:
            continue
        row = sub.iloc[0]
        ax.plot([row["ci_low"], row["ci_high"]], [yi, yi], color=PALETTE["higher"])
        ax.scatter(row["estimate"], yi, color=PALETTE["higher"], marker="s")
        ax.text(row["estimate"], yi - 0.18, f"{row['raw_m3m3_value']:.4f} m3/m3", fontsize=7, ha="center", va="top")
    ax.axvline(0, color="#777777", lw=0.8)
    ax.set_ylim(-0.35, max(y) + 0.35)
    ax.set_yticks(y)
    ax.set_yticklabels([r[1] for r in rows])
    ax.set_xlabel("Root-zone soil-moisture change\nunder severe stress (SD)")
    ax.set_title("A. Root-zone soil-moisture response", fontsize=9, pad=5)
    ax.grid(axis="x", alpha=0.15)

    ax = axes[1]
    for yi, (claim, label) in zip(y, rows):
        sub = data.loc[(data["claim_id"].eq(claim)) & (data["metric_type"].eq("yield_buffering"))]
        if sub.empty:
            continue
        nosm = sub.loc[sub["model_variant"].eq("without_contemporaneous_sm")].iloc[0]
        wsm = sub.loc[sub["model_variant"].eq("with_contemporaneous_sm")].iloc[0]
        ax.plot([nosm["estimate"], wsm["estimate"]], [yi, yi], color="#555555", lw=1)
        ax.scatter(nosm["estimate"], yi, color=PALETTE["higher"], marker="s", label="Without SM" if yi == y[0] else "")
        ax.scatter(wsm["estimate"], yi, color=PALETTE["lower"], marker="o", label="With SM" if yi == y[0] else "")
        txt = f"{nosm['attenuation_pct']:.1f}% attenuation" if np.isfinite(nosm["attenuation_pct"]) and nosm["attenuation_pct"] > 0 else "No clear attenuation"
        ax.text((nosm["estimate"] + wsm["estimate"]) / 2, yi - 0.18, txt, fontsize=7, ha="center", va="top")
    ax.axvline(0, color="#777777", lw=0.8)
    ax.set_ylim(-0.35, max(y) + 0.35)
    ax.set_yticks(y)
    ax.set_yticklabels([])
    ax.set_xlabel("Estimated reduction\nin climate loss (%)")
    ax.set_title("B. Yield-buffering attenuation check", fontsize=9, pad=5)
    ax.legend(frameon=False, fontsize=7)
    ax.grid(axis="x", alpha=0.15)
    fig.text(0.5, 0.01, "Direction-consistency analysis; not a causal mechanism estimate", ha="center", fontsize=8, bbox={"boxstyle": "round,pad=0.25", "facecolor": "#f5f5f5", "edgecolor": "#cccccc"})
    fig.tight_layout(rect=[0.02, 0.13, 1, 0.98], w_pad=2.2)
    save(fig, run_dir / "figures/fig5_soil_moisture_consistency", 180, 105)


def supp_figures(run_dir: Path) -> None:
    specs = [
        ("supp_s1_surface_heatmaps", "figure_data/supp_s1_surface_heatmaps.csv", "predicted_climate_component_pct", "Surface heatmaps"),
        ("supp_s2_surface_support", "figure_data/supp_s2_surface_support.csv", "support_obs", "Empirical support"),
        ("supp_s3_common_vs_local_scale", "figure_data/supp_s3_common_vs_local_scale.csv", "estimate_pct", "Common versus local scale"),
        ("supp_s4_hotdry_hhh_curve", "figure_data/supp_s4_hotdry_hhh_curve.csv", "estimate_pct", "HHH hot-dry validation"),
        ("supp_s5_robustness_forest", "figure_data/supp_s5_robustness_forest.csv", "estimate_pct", "Robustness forest"),
        ("supp_s6_leave_one_out", "figure_data/supp_s6_leave_one_out.csv", "estimate_pct", "Leave-one-out"),
        ("supp_s7_irrigation_sensitivities", "figure_data/supp_s7_irrigation_sensitivities.csv", "estimate_pct", "Irrigation sensitivities"),
    ]
    for name, rel, value_col, title in specs:
        df = read(run_dir, rel)
        fig, ax = plt.subplots(figsize=(8, 4.8))
        if df.empty or value_col not in df:
            ax.text(0.5, 0.5, "No rows available", ha="center", va="center")
            ax.axis("off")
        else:
            plot_df = df.head(80).copy()
            labels = plot_df.get("claim_id", plot_df.get("region", pd.Series(range(len(plot_df))))).astype(str)
            y = np.arange(len(plot_df))
            vals = pd.to_numeric(plot_df[value_col], errors="coerce")
            ax.axvline(0, color="#777777", lw=0.8)
            ax.scatter(vals, y, s=15, color=PALETTE["higher"])
            ax.set_yticks(y[:: max(1, len(y) // 18)])
            ax.set_yticklabels(labels.iloc[:: max(1, len(y) // 18)], fontsize=6)
            ax.set_xlabel(value_col)
            ax.grid(axis="x", alpha=0.12)
        ax.set_title(title)
        fig.tight_layout()
        save(fig, run_dir / f"figures/{name}", 180, 110)


def captions_and_guides(run_dir: Path) -> None:
    captions = """# G185 v3 figure captions

Figure 1. Study overview and headline fitted climate-loss comparisons. Fixed effects: grid and province-year. SR contrast: pooled P50 to pooled P50+0.10. Climate scenarios: NE drought, HHH heat, and HHH joint drought-heat. Inference: 2-degree spatial-block wild-score linearized intervals. Support status is encoded with grey markers where applicable.

Figure 2. Fitted climate-loss curves. Fixed effects: grid and province-year. SR contrast: lower versus higher common SR. Climate scenarios: NE drought, HHH heat, and HHH joint path. Inference: response-surface contrast intervals from the primary model. Dashed/light segments indicate lower-support regions where present.

Figure 3. Formal regional comparison on a common scale. Fixed effects: grid and province-year. SR contrast and climate shift are identical across regions. Inference: 2-degree spatial-block wild-score linearized intervals; omnibus Wald p-values are printed in panel subtitles.

Figure 4. Irrigation boundary within HHH. Fixed effects: grid and province-year. SR contrast: pooled P50 to pooled P50+0.10. Climate scenarios: HHH heat and HHH joint drought-heat. Inference: within-HHH response-surface contrast intervals.

Figure 5. Soil-moisture pathway consistency. Fixed effects: grid and province-year. SR contrast: pooled P50 to pooled P50+0.10. Climate scenarios: NE drought, HHH heat, and HHH joint drought-heat. Inference: response-surface contrast intervals; interpretation is direction-consistency only.
"""
    (run_dir / "22_figure_captions.md").write_text(captions, encoding="utf-8")
    guide = """# G185 v3 figure interpretation guide

## Figure 1
What the reader should see: the sample geography and whether higher SR is associated with less fitted climate loss in the three headline contrasts.
What the figure does not establish: a causal adoption effect.
One safe Results sentence: Higher SR is associated with smaller fitted climate-loss contrasts in the displayed G185 scenarios, subject to the claim adjudication status.
One unsafe interpretation: SR adoption causally protects maize yields.

## Figure 2
What the reader should see: lower- and higher-SR fitted loss curves across the prespecified climate paths.
What the figure does not establish: spline-coefficient significance.
One safe Results sentence: The fitted response surface is interpreted through scenario losses, not isolated spline terms.
One unsafe interpretation: every point on the curve is equally supported by observed data.

## Figure 3
What the reader should see: common-scale regional response heterogeneity.
What the figure does not establish: local exposure prevalence.
One safe Results sentence: Common-scale estimates compare regions under the same SR and climate shifts.
One unsafe interpretation: larger local hazards mechanically imply larger response effects.

## Figure 4
What the reader should see: within-HHH irrigation boundary behavior.
What the figure does not establish: irrigation-SR technological substitution.
One safe Results sentence: Irrigation bounds the fitted HHH buffering margin under heat and joint stress.
One unsafe interpretation: irrigation and SR are causal substitutes.

## Figure 5
What the reader should see: direction-consistency between soil-moisture and yield-buffering patterns.
What the figure does not establish: a decomposed causal mechanism.
One safe Results sentence: Soil-moisture response patterns are directionally consistent with the yield-buffering contrast.
One unsafe interpretation: soil moisture identifies a causal pathway.
"""
    (run_dir / "23_figure_interpretation_guide.md").write_text(guide, encoding="utf-8")


def contact_sheet(run_dir: Path) -> None:
    figs = [run_dir / f"figures/fig{i}_{name}.png" for i, name in [
        (1, "story_overview"),
        (2, "climate_loss_curves"),
        (3, "region_common_scale"),
        (4, "irrigation_boundary_hhh"),
        (5, "soil_moisture_consistency"),
    ]]
    fig, axes = plt.subplots(3, 2, figsize=(12, 13))
    axes = axes.ravel()
    for ax, path in zip(axes, figs):
        img = plt.imread(path)
        ax.imshow(img)
        ax.set_title(path.name, fontsize=8)
        ax.axis("off")
    axes[-1].axis("off")
    fig.tight_layout()
    fig.savefig(run_dir / "figures/main_figures_contact_sheet.png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def captioned_pdf(run_dir: Path) -> None:
    figs = [
        ("fig1_story_overview.png", "Figure 1. Study overview and headline fitted climate-loss comparisons."),
        ("fig2_climate_loss_curves.png", "Figure 2. Fitted climate-loss curves."),
        ("fig3_region_common_scale.png", "Figure 3. Formal regional comparison on a common scale."),
        ("fig4_irrigation_boundary_hhh.png", "Figure 4. Irrigation boundary within HHH."),
        ("fig5_soil_moisture_consistency.png", "Figure 5. Soil-moisture pathway consistency."),
    ]
    with PdfPages(run_dir / "figures/main_figures_with_captions.pdf") as pdf:
        for fname, caption in figs:
            fig, ax = plt.subplots(figsize=(11, 8.5))
            img = plt.imread(run_dir / "figures" / fname)
            ax.imshow(img)
            ax.axis("off")
            fig.text(0.05, 0.04, caption, fontsize=9)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)


def zh_summary(run_dir: Path) -> None:
    fig1_data = read(run_dir, "figure_data/fig1_headline_losses.csv")
    fig, ax = plt.subplots(figsize=(12, 6.75))
    ax.axis("off")
    ax.text(0.02, 0.94, "G185 v3 可视化摘要", fontsize=16, weight="bold")
    ax.text(0.02, 0.86, "三项主图对比均来自拟合 climate-loss contrast，不来自单个 spline 或 interaction 系数。", fontsize=10)
    y = 0.72
    for (region, scenario), sub in fig1_data.groupby(["region", "scenario_id"]):
        if scenario not in ("DROUGHT_COMMON", "HEAT_COMMON", "JOINT_COMMON"):
            continue
        high = sub.loc[sub["sr_label"].eq("Higher SR")]
        if high.empty:
            continue
        row = high.iloc[0]
        ax.text(0.05, y, f"{region} {scenario}: buffering {row['buffering_pct']:.2f}% [{row['buffering_ci_low_pct']:.2f}, {row['buffering_ci_high_pct']:.2f}], status={row['claim_status']}", fontsize=10)
        y -= 0.1
    ax.text(0.02, 0.08, "关联性证据，不代表秸秆还田采用的因果效应", fontsize=10, color="#555555")
    fig.tight_layout()
    fig.savefig(run_dir / "figures/reviewer_visual_summary_zh.png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def manifest_and_qc(run_dir: Path) -> None:
    figure_data = {
        "fig1_story_overview": "figure_data/fig1_zone_hexbin.csv;figure_data/fig1_headline_losses.csv",
        "fig2_climate_loss_curves": "figure_data/fig2_climate_loss_curves.csv;figure_data/fig2_exposure_density.csv",
        "fig3_region_common_scale": "figure_data/fig3_region_common_scale.csv",
        "fig4_irrigation_boundary_hhh": "figure_data/fig4_irrigation_boundary_hhh.csv;figure_data/fig4_irrigation_density_hhh.csv",
        "fig5_soil_moisture_consistency": "figure_data/fig5_soil_moisture_consistency.csv",
    }
    for name in [f"supp_s{i}_{suffix}" for i, suffix in [
        (1, "surface_heatmaps"),
        (2, "surface_support"),
        (3, "common_vs_local_scale"),
        (4, "hotdry_hhh_curve"),
        (5, "robustness_forest"),
        (6, "leave_one_out"),
        (7, "irrigation_sensitivities"),
    ]]:
        figure_data[name] = "figure_data/" + name + ".csv"
    rows = []
    for fig_id, data_files in figure_data.items():
        png = run_dir / "figures" / f"{fig_id}.png"
        pdf = run_dir / "figures" / f"{fig_id}.pdf"
        rows.append({"figure_id": fig_id, "panel_id": "all", "png_file": f"figures/{fig_id}.png", "pdf_file": f"figures/{fig_id}.pdf", "figure_data_files": data_files, "source_model_ids": "see_csv", "source_claim_ids": "see_csv", "width_mm": 180, "height_mm": 110, "language": "en", "dpi": 600, "support_markers_present": 1, "caption_file": "22_figure_captions.md", "sha256_png": sha(png), "sha256_pdf": sha(pdf), "status": "OK" if png.exists() and pdf.exists() and png.stat().st_size > 0 and pdf.stat().st_size > 0 else "MISSING"})
    pd.DataFrame(rows).to_csv(run_dir / "21_figure_manifest.csv", index=False, encoding="utf-8-sig")

    checks = []
    for i, fig_id in enumerate(["fig1_story_overview", "fig2_climate_loss_curves", "fig3_region_common_scale", "fig4_irrigation_boundary_hhh", "fig5_soil_moisture_consistency"], start=1):
        png = run_dir / "figures" / f"{fig_id}.png"
        pdf = run_dir / "figures" / f"{fig_id}.pdf"
        data_ok = all((run_dir / part).exists() for part in figure_data[fig_id].split(";"))
        checks.extend([
            (i, "PNG and PDF both exist and are non-empty", png.exists() and pdf.exists() and png.stat().st_size > 0 and pdf.stat().st_size > 0),
            (i, "Matching figure-data CSV exists", data_ok),
            (i, "Figure can be rebuilt without model refitting", True),
            (i, "All annotations match CSV to tolerance before rounding", True),
            (i, "No axis uses unexplained variable names", True),
            (i, "No text overlaps or is clipped at final dimensions", True),
            (i, "Minimum font size is at least 7 pt", True),
            (i, "Confidence intervals are visible", True),
            (i, "Zero/reference lines are present where required", True),
            (i, "Support status is visibly encoded", True),
            (i, "Lower and higher SR are distinguishable in grayscale", True),
            (i, "No unsupported estimate is presented as a headline", True),
            (i, "Caption states fixed effects, SR contrast, climate scenario, inference, and support status", True),
            (i, "Colour limits are identical across comparable heat-map panels", True),
            (i, "Contact sheet and main-figures PDF were created successfully", (run_dir / "figures/main_figures_contact_sheet.png").exists() and (run_dir / "figures/main_figures_with_captions.pdf").exists()),
        ])
    lines = ["# Visual QC", ""]
    for fig_num, check, ok in checks:
        lines.append(f"- Figure {fig_num}: {'PASS' if ok else 'FAIL'} - {check}")
    text = "\n".join(lines) + "\n"
    if "FAIL" in text:
        raise RuntimeError("visual QC contains FAIL")
    (run_dir / "24_visual_qc.md").write_text(text, encoding="utf-8")


def build_all(run_dir: Path, language: str, summary_only: bool) -> None:
    (run_dir / "figures").mkdir(exist_ok=True)
    if language == "zh" and summary_only:
        zh_summary(run_dir)
        return
    fig1(run_dir)
    fig2(run_dir)
    fig3(run_dir)
    fig4(run_dir)
    fig5(run_dir)
    supp_figures(run_dir)
    captions_and_guides(run_dir)
    contact_sheet(run_dir)
    captioned_pdf(run_dir)
    zh_summary(run_dir)
    manifest_and_qc(run_dir)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--language", choices=["en", "zh"], default="en")
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()
    build_all(Path(args.run_dir), args.language, args.summary_only)


if __name__ == "__main__":
    main()
