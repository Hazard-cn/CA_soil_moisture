"""Build a Nature-style bilingual HTML report for the G185 method upgrade.

The script is report-oriented and does not rerun fixed-effect or ML models. It
reads the existing G185 method-upgrade tables, copies the previous six figures,
adds four Nature-style interpretation figures, and writes English and Chinese
HTML pages.
"""

from __future__ import annotations

import csv
import html
import math
import re
import shutil
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
SRC_RUN = PROJ / "quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report"
DRAFT_RUN = PROJ / "quality_reports/agent_runs/2026-06-20_g185_draft_bootstrap_v1"
OUT_RUN = PROJ / "quality_reports/agent_runs/2026-06-20_g185_nature_style_html"
SRC_FIG = SRC_RUN / "figures"
SRC_TABLE = SRC_RUN / "tables"
OUT_FIG = OUT_RUN / "figures"
OUT_TABLE = OUT_RUN / "tables"

HAZARD_ORDER = ["drought", "heat", "hotdry"]
HAZARD_LABEL = {"drought": "Drought", "heat": "Heat", "hotdry": "Hot-dry"}
HAZARD_LABEL_CN = {"drought": "干旱", "heat": "高温", "hotdry": "热旱复合"}
REGION_ORDER = ["NE", "HHH", "NW", "SW", "SH"]
REGION_NAME_CN = {
    "NE": "东北",
    "HHH": "黄淮海",
    "NW": "西北",
    "SW": "西南",
    "SH": "南方",
}
CENTRAL_PAIRS = {("NE", "drought"), ("HHH", "heat"), ("HHH", "hotdry")}
PROHIBITED = ("causal effect", "causal mediation", "direct/indirect effect", "ml proves")


def ensure_dirs() -> None:
    for path in (OUT_RUN, OUT_FIG, OUT_TABLE):
        path.mkdir(parents=True, exist_ok=True)


def read_csv(name: str, source: Path = SRC_TABLE) -> pd.DataFrame:
    path = source / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def copy_inputs() -> None:
    for src in SRC_FIG.glob("*.png"):
        shutil.copy2(src, OUT_FIG / src.name)
    for src in SRC_TABLE.glob("*.csv"):
        shutil.copy2(src, OUT_TABLE / src.name)
    for name in ("g185_descriptive_stats.csv", "g185_region_descriptive_stats.csv"):
        src = DRAFT_RUN / name
        if src.exists():
            shutil.copy2(src, OUT_TABLE / name)


def metric_value(desc: pd.DataFrame, metric: str) -> float | str:
    row = desc.loc[desc["metric"].astype(str).eq(metric)]
    if row.empty:
        return math.nan
    val = row.iloc[0]["value"]
    try:
        return float(val)
    except (TypeError, ValueError):
        return str(val)


def fmt_num(x: object, digits: int = 2) -> str:
    try:
        xf = float(x)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(xf):
        return "NA"
    return f"{xf:.{digits}f}"


def fmt_ci(row: pd.Series) -> str:
    return f"{fmt_num(row['estimate'])} [{fmt_num(row['ci_low'])}, {fmt_num(row['ci_high'])}]"


def theme() -> None:
    matplotlib.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def plot_response_gap(component: pd.DataFrame, desc: pd.DataFrame, damage: pd.DataFrame) -> pd.DataFrame:
    sr_lookup = {
        "P25": float(metric_value(desc, "ca_P25")),
        "P50": float(metric_value(desc, "ca_P50")),
        "P75": float(metric_value(desc, "ca_P75")),
    }
    te = component.loc[component["effect_type"].eq("TE")].copy()
    te["sr_value"] = te["sr_level"].map(sr_lookup)
    te["avoidance_vs_p25"] = np.nan
    rows = []
    for hazard, sub in te.groupby("hazard", sort=False):
        base = float(sub.loc[sub["sr_level"].eq("P25"), "estimate"].iloc[0])
        for idx, row in sub.iterrows():
            te.loc[idx, "avoidance_vs_p25"] = float(row["estimate"]) - base
        hit = damage.loc[damage["hazard"].eq(hazard)].iloc[0]
        rows.append(
            {
                "hazard": hazard,
                "hazard_label": HAZARD_LABEL[hazard],
                "p25_slope": base,
                "p75_slope": float(sub.loc[sub["sr_level"].eq("P75"), "estimate"].iloc[0]),
                "damage_avoidance_margin": float(hit["estimate"]),
                "ci_low": float(hit["ci_low"]),
                "ci_high": float(hit["ci_high"]),
            }
        )
    summary = pd.DataFrame(rows)
    te.to_csv(OUT_TABLE / "g185_sr_response_gap_curve.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT_TABLE / "g185_sr_response_gap_summary.csv", index=False, encoding="utf-8-sig")

    colors = {"drought": "#0077BB", "heat": "#EE7733", "hotdry": "#009988"}
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 3.8), sharey=False)
    for ax, hazard in zip(axes, HAZARD_ORDER):
        sub = te.loc[te["hazard"].eq(hazard)].sort_values("sr_value")
        ax.axhline(0, color="#666666", linewidth=0.8)
        ax.plot(sub["sr_value"], sub["estimate"], color=colors[hazard], linewidth=2.2, marker="o")
        ax.fill_between(
            sub["sr_value"].astype(float).to_numpy(),
            sub["ci_low"].astype(float).to_numpy(),
            sub["ci_high"].astype(float).to_numpy(),
            color=colors[hazard],
            alpha=0.15,
            linewidth=0,
        )
        hit = damage.loc[damage["hazard"].eq(hazard)].iloc[0]
        ax.text(
            0.04,
            0.95,
            f"P75-P25 margin\n{fmt_ci(hit)} pp",
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=8,
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#cfd6df", "alpha": 0.92},
        )
        ax.set_title(HAZARD_LABEL[hazard])
        ax.set_xlabel("SR adoption ratio")
        ax.set_xticks([sr_lookup["P25"], sr_lookup["P50"], sr_lookup["P75"]])
        ax.set_xticklabels(["P25", "P50", "P75"])
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Fitted P90 stress-response slope (%)")
    fig.suptitle("G185 SR response curve and damage-avoidance margin", y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(OUT_FIG / "fig7_g185_sr_response_gap_curve.png", facecolor="white")
    plt.close(fig)
    return summary


def plot_targeting_matrix(region: pd.DataFrame) -> pd.DataFrame:
    region = region.copy()
    region["is_central"] = [(r, h) in CENTRAL_PAIRS for r, h in zip(region["region"], region["hazard"])]
    region["ci_excludes_zero"] = (region["ci_low"] > 0) | (region["ci_high"] < 0)
    region.to_csv(OUT_TABLE / "g185_region_hazard_targeting_matrix.csv", index=False, encoding="utf-8-sig")

    mat = region.pivot(index="region", columns="hazard", values="estimate").reindex(REGION_ORDER)[HAZARD_ORDER]
    fig, ax = plt.subplots(figsize=(6.7, 4.8))
    vmax = max(1.0, np.nanmax(np.abs(mat.to_numpy(dtype=float))))
    im = ax.imshow(mat.to_numpy(dtype=float), cmap="BrBG", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(np.arange(len(HAZARD_ORDER)))
    ax.set_xticklabels([HAZARD_LABEL[h] for h in HAZARD_ORDER])
    ax.set_yticks(np.arange(len(REGION_ORDER)))
    ax.set_yticklabels(REGION_ORDER)
    for i, region_name in enumerate(REGION_ORDER):
        for j, hazard in enumerate(HAZARD_ORDER):
            row = region.loc[region["region"].eq(region_name) & region["hazard"].eq(hazard)].iloc[0]
            mark = "*" if bool(row["ci_excludes_zero"]) else ""
            ax.text(j, i, f"{row['estimate']:.2f}{mark}", ha="center", va="center", fontsize=8, color="#111111")
            if bool(row["is_central"]):
                ax.add_patch(plt.Rectangle((j - 0.48, i - 0.48), 0.96, 0.96, fill=False, edgecolor="#CC3311", linewidth=2.2))
    ax.set_title("Region-hazard targeting matrix")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("SR-associated margin at regional P90 hazard (%)")
    fig.savefig(OUT_FIG / "fig8_g185_region_hazard_targeting_matrix.png", facecolor="white")
    plt.close(fig)
    return region


def plot_targeting_amplification(damage: pd.DataFrame, region: pd.DataFrame) -> pd.DataFrame:
    rows = []
    target_lookup = {"drought": "NE", "heat": "HHH", "hotdry": "HHH"}
    for hazard in HAZARD_ORDER:
        national = damage.loc[damage["hazard"].eq(hazard)].iloc[0]
        regional = region.loc[region["hazard"].eq(hazard) & region["region"].eq(target_lookup[hazard])].iloc[0]
        rows.append(
            {
                "hazard": hazard,
                "hazard_label": HAZARD_LABEL[hazard],
                "target_region": target_lookup[hazard],
                "national_margin": float(national["estimate"]),
                "national_ci_low": float(national["ci_low"]),
                "national_ci_high": float(national["ci_high"]),
                "targeted_margin": float(regional["estimate"]),
                "targeted_ci_low": float(regional["ci_low"]),
                "targeted_ci_high": float(regional["ci_high"]),
                "amplification_ratio": float(regional["estimate"]) / float(national["estimate"]),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(OUT_TABLE / "g185_targeting_amplification.csv", index=False, encoding="utf-8-sig")

    x = np.arange(len(df))
    width = 0.34
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for offset, prefix, label, color in [
        (-width / 2, "national", "National G185", "#0077BB"),
        (width / 2, "targeted", "Central target region", "#EE7733"),
    ]:
        y = df[f"{prefix}_margin"].to_numpy()
        lo = df[f"{prefix}_ci_low"].to_numpy()
        hi = df[f"{prefix}_ci_high"].to_numpy()
        ax.bar(x + offset, y, width=width, label=label, color=color, alpha=0.85)
        ax.errorbar(x + offset, y, yerr=np.vstack([y - lo, hi - y]), fmt="none", color="#222222", capsize=3, linewidth=0.8)
    for i, row in df.iterrows():
        ax.text(i, max(row["targeted_ci_high"], row["national_ci_high"]) + 0.25, f"{row['amplification_ratio']:.1f}x", ha="center", fontsize=8)
    ax.axhline(0, color="#555555", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r.hazard_label}\n{r.target_region}" for r in df.itertuples()])
    ax.set_ylabel("P75-minus-P25 SR margin at P90 hazard (%)")
    ax.set_title("Targeting amplification relative to national G185 margins")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    ymax = max(float(df["targeted_ci_high"].max()), float(df["national_ci_high"].max())) + 0.9
    ax.set_ylim(0, ymax)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(OUT_FIG / "fig9_g185_targeting_amplification.png", facecolor="white")
    plt.close(fig)
    return df


def plot_support_uncertainty(region: pd.DataFrame) -> pd.DataFrame:
    df = region.copy()
    df["ci_width"] = df["ci_high"] - df["ci_low"]
    df["support_class"] = np.where(df["N_grids"] >= 3000, "high", np.where(df["N_grids"] >= 1000, "medium", "low"))
    df.to_csv(OUT_TABLE / "g185_support_uncertainty_panel.csv", index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    y_labels = []
    y_pos = []
    colors = {"drought": "#0077BB", "heat": "#EE7733", "hotdry": "#009988"}
    pos = 0
    for region_name in REGION_ORDER:
        sub = df.loc[df["region"].eq(region_name)].set_index("hazard").reindex(HAZARD_ORDER).reset_index()
        for _, row in sub.iterrows():
            label = f"{region_name} - {HAZARD_LABEL[row['hazard']]}"
            y_labels.append(label)
            y_pos.append(pos)
            ax.plot([row["ci_low"], row["ci_high"]], [pos, pos], color=colors[row["hazard"]], linewidth=1.5, alpha=0.8)
            size = 24 + 0.018 * float(row["N_grids"])
            ax.scatter(row["estimate"], pos, s=size, color=colors[row["hazard"]], edgecolor="#222222", linewidth=0.4, zorder=3)
            if bool((row["region"], row["hazard"]) in CENTRAL_PAIRS):
                ax.text(row["ci_high"] + 0.18, pos, "target", va="center", fontsize=7, color="#CC3311")
            pos += 1
    ax.axvline(0, color="#555555", linewidth=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels)
    ax.invert_yaxis()
    ax.set_xlabel("SR-associated margin at regional P90 hazard (%)")
    ax.set_title("Support and uncertainty by region-hazard cell")
    ax.grid(axis="x", alpha=0.25)
    fig.savefig(OUT_FIG / "fig10_g185_support_uncertainty_panel.png", facecolor="white")
    plt.close(fig)
    return df


def img_tag(src: str, alt: str, caption: str) -> str:
    return (
        f'<figure><img src="{html.escape(src)}" alt="{html.escape(alt)}">'
        f"<figcaption>{html.escape(caption)}</figcaption></figure>"
    )


def table_html(df: pd.DataFrame, columns: list[str], max_rows: int = 12) -> str:
    view = df.loc[:, columns].head(max_rows).copy()
    out = ["<table>", "<thead><tr>"]
    for col in columns:
        out.append(f"<th>{html.escape(col)}</th>")
    out.append("</tr></thead><tbody>")
    for _, row in view.iterrows():
        out.append("<tr>")
        for col in columns:
            val = row[col]
            if isinstance(val, float):
                text = fmt_num(val)
            else:
                text = str(val)
            out.append(f"<td>{html.escape(text)}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def write_html(
    language: str,
    damage: pd.DataFrame,
    region: pd.DataFrame,
    irrigation: pd.DataFrame,
    response_summary: pd.DataFrame,
    targeting: pd.DataFrame,
) -> Path:
    is_cn = language == "cn"
    title = "G185 Nature-style SR Buffering Report" if not is_cn else "G185 子刊风格秸秆还田缓冲报告"
    subtitle = (
        "Response curves, targeted-use margins, support diagnostics, and appendix-level ML concordance"
        if not is_cn
        else "响应曲线、区域定向边际、支持度诊断与附录级机器学习一致性检验"
    )
    if is_cn:
        sections = [
            ("核心结论", "G185 结果最适合写成区域定向的气候风险缓冲：东北承载干旱缓冲，黄淮海承载高温与热旱复合缓冲；灌溉条件限定 heat/hot-dry 的边际空间。"),
            ("图形结构来自哪里", "本报告学习 Nature Geoscience SOC 补充材料的表达顺序：先给 response/gap 图，再给区域条件、潜在缓冲空间、支持度与不确定性，最后把 ML 放在附录稳健性。"),
            ("证据边界", "所有主结论基于 G185 fixed-effect / bootstrap-linearized margins。ML 图只检查异质性方向是否复现，不作为主识别。"),
        ]
        main_sentence = "可写主句：在 G185 口径下，秸秆还田更适合被解释为区域定向的 climate-damage buffering 技术，而不是全国统一平均增产技术。"
        note = "注：星号表示区间不跨 0；红框表示主文建议聚焦的 region-hazard 单元。"
        old_fig_heading = "原报告图"
        new_fig_heading = "新增图"
        source_heading = "可追溯表格"
        html_name = "report_nature_style_cn.html"
    else:
        sections = [
            ("Main finding", "The G185 evidence is best framed as targeted climate-risk buffering: NE carries the drought margin, while HHH carries the heat and hot-dry margins; irrigation bounds the heat and hot-dry buffering space."),
            ("What the Nature-style upgrade changes", "The report follows the local Nature Geoscience supplemental-material structure: response/gap first, regional targeting second, potential and support diagnostics third, and ML concordance as appendix-level evidence."),
            ("Evidence boundary", "The substantive claims rely on G185 fixed-effect / bootstrap-linearized margins. ML figures only test directional heterogeneity concordance and are not the main identification design."),
        ]
        main_sentence = "Recommended sentence: At the G185 scale, straw return is best interpreted as a region-targeted climate-damage buffering technology rather than a uniform national yield-gain technology."
        note = "Note: Asterisks indicate intervals excluding zero; red boxes mark the main region-hazard cells recommended for Results text."
        old_fig_heading = "Original Report Figures"
        new_fig_heading = "New Figures"
        source_heading = "Traceable Tables"
        html_name = "report_nature_style_en.html"

    section_html = "".join(f"<section><h2>{html.escape(h)}</h2><p>{html.escape(t)}</p></section>" for h, t in sections)
    new_figs = [
        img_tag("figures/fig7_g185_sr_response_gap_curve.png", "SR response gap curve", "Figure 7. SR response/gap curve showing P90 stress-response slopes at SR P25, P50, and P75."),
        img_tag("figures/fig8_g185_region_hazard_targeting_matrix.png", "Region hazard targeting matrix", "Figure 8. Region-hazard targeting matrix; red boxes mark NE drought, HHH heat, and HHH hot-dry."),
        img_tag("figures/fig9_g185_targeting_amplification.png", "Targeting amplification", "Figure 9. Central targeting margins compared with national G185 margins."),
        img_tag("figures/fig10_g185_support_uncertainty_panel.png", "Support and uncertainty panel", "Figure 10. Support and uncertainty across all region-hazard cells."),
    ]
    old_figs = [
        img_tag("figures/fig1_g185_damage_avoidance_margin.png", "Damage avoidance margin", "Original Figure 1. Damage-avoidance margin by hazard."),
        img_tag("figures/fig2_g185_region_targeted_margin.png", "Region targeted margin", "Original Figure 2. Central region-targeted buffering margins."),
        img_tag("figures/fig3_g185_irrigation_conditioned_margin.png", "Irrigation conditioned margin", "Original Figure 3. Irrigation-conditioned margins."),
        img_tag("figures/fig4_g185_component_profile.png", "Component profile", "Original Figure 4. Renamed IE/DE/TE component diagnostics."),
        img_tag("figures/fig5_g185_python_ml_concordance.png", "ML concordance", "Original Figure 5. Python/R ML region concordance."),
        img_tag("figures/fig6_g185_r_grf_heterogeneity.png", "R grf heterogeneity", "Original Figure 6. R grf irrigation heterogeneity."),
    ]

    damage_table = table_html(damage, ["hazard_label", "estimate", "ci_low", "ci_high", "N_model", "N_grids"], 10)
    target_table = table_html(targeting, ["hazard_label", "target_region", "national_margin", "targeted_margin", "amplification_ratio"], 10)
    response_table = table_html(response_summary, ["hazard_label", "p25_slope", "p75_slope", "damage_avoidance_margin", "ci_low", "ci_high"], 10)
    irr_table = table_html(irrigation, ["hazard_label", "irr_level", "irr_value", "estimate", "ci_low", "ci_high"], 12)

    css = """
body{font-family:Arial,Helvetica,sans-serif;margin:0;background:#f6f7f9;color:#17202a;line-height:1.55}
header{background:#1f2933;color:#fff;padding:36px 52px}
main{max-width:1160px;margin:0 auto;padding:28px}
section{background:#fff;border:1px solid #dde2e8;border-radius:8px;margin:18px 0;padding:22px}
h1{margin:0 0 8px 0;font-size:30px}
h2{margin:0 0 12px 0;font-size:21px}
h3{margin:18px 0 10px 0;font-size:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:18px}
figure{margin:0;background:#fff;border:1px solid #dde2e8;border-radius:8px;padding:12px}
img{width:100%;height:auto;display:block}
figcaption{font-size:13px;color:#4b5563;margin-top:8px}
table{border-collapse:collapse;width:100%;font-size:13px;margin-top:10px}
th,td{border:1px solid #d7dce2;padding:6px 8px;text-align:left}
th{background:#eef2f6}
.lead{font-size:16px;max-width:980px}
.callout{border-left:4px solid #cc3311;background:#fff8f5}
.small{font-size:13px;color:#59636f}
"""
    body = f"""<!doctype html>
<html lang="{'zh-CN' if is_cn else 'en'}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>{css}</style>
</head>
<body>
<header>
  <h1>{html.escape(title)}</h1>
  <p class="lead">{html.escape(subtitle)}</p>
</header>
<main>
  {section_html}
  <section class="callout"><p><strong>{html.escape(main_sentence)}</strong></p><p class="small">{html.escape(note)}</p></section>
  <section><h2>{html.escape(new_fig_heading)}</h2><div class="grid">{''.join(new_figs)}</div></section>
  <section><h2>{html.escape(old_fig_heading)}</h2><div class="grid">{''.join(old_figs)}</div></section>
  <section><h2>{html.escape(source_heading)}</h2>
    <h3>Damage-avoidance margins</h3>{damage_table}
    <h3>Response/gap summary</h3>{response_table}
    <h3>Targeting amplification</h3>{target_table}
    <h3>Irrigation boundary</h3>{irr_table}
  </section>
  <section><h2>Files</h2>
    <p class="small">Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. Figure and table files are stored next to this HTML under <code>figures/</code> and <code>tables/</code>.</p>
  </section>
</main>
</body>
</html>
"""
    lower = body.lower()
    found = [term for term in PROHIBITED if term in lower]
    if found:
        raise ValueError(f"Prohibited terms in {html_name}: {found}")
    path = OUT_RUN / html_name
    path.write_text(body, encoding="utf-8")
    return path


def verify_html(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    srcs = re.findall(r'<img[^>]+src="([^"]+)"', text)
    missing = []
    for src in srcs:
        if not (path.parent / src).exists():
            missing.append(src)
    if missing:
        raise FileNotFoundError(f"{path.name} missing image links: {missing}")


def write_manifest(en_path: Path, cn_path: Path) -> None:
    rows = [
        {"key": "output_dir", "value": str(OUT_RUN)},
        {"key": "english_html", "value": str(en_path)},
        {"key": "chinese_html", "value": str(cn_path)},
        {"key": "source_report", "value": str(SRC_RUN / "report.html")},
        {"key": "new_figure_count", "value": "4"},
        {"key": "copied_original_figure_count", "value": str(len(list(SRC_FIG.glob("*.png"))))},
    ]
    with (OUT_RUN / "run_manifest.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["key", "value"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    theme()
    ensure_dirs()
    copy_inputs()
    damage = read_csv("g185_damage_avoidance_results.csv")
    region = read_csv("g185_region_targeted_margin.csv")
    irrigation = read_csv("g185_irrigation_conditioned_margin.csv")
    component = read_csv("g185_component_diagnostics.csv")
    desc = read_csv("g185_descriptive_stats.csv", OUT_TABLE)

    response_summary = plot_response_gap(component, desc, damage)
    matrix = plot_targeting_matrix(region)
    targeting = plot_targeting_amplification(damage, region)
    plot_support_uncertainty(matrix)

    en_path = write_html("en", damage, matrix, irrigation, response_summary, targeting)
    cn_path = write_html("cn", damage, matrix, irrigation, response_summary, targeting)
    verify_html(en_path)
    verify_html(cn_path)
    write_manifest(en_path, cn_path)
    print(en_path)
    print(cn_path)


if __name__ == "__main__":
    main()
