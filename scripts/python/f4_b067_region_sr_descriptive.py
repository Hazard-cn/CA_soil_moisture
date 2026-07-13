"""Region-level descriptive statistics for SR in the current F4-B067 scale."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
SCRIPT_DIR = PROJ / "scripts/python"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from bio_window_filter_128 import unique_variants  # noqa: E402
from ggcp10_parallel_rules_69038_search import load_panel  # noqa: E402


SAMPLE_ID = "B067"
OUT_DIR = PROJ / "output/figures/f4_b067_v2"
REPORT_MD = PROJ / "quality_reports/2026-06-04_region_sr_descriptive_stats.md"
REGION_ORDER = ["NE", "HHH", "NW", "SW", "SH"]
REGION_LABELS = {
    "NE": "NE",
    "HHH": "HHH",
    "NW": "NW",
    "SW": "SW",
    "SH": "SH",
}


def b067_sample(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    variants = unique_variants(df)
    meta = next(v for v in variants if v["sample_id"] == SAMPLE_ID)
    base = df.loc[meta["mask"]].copy()
    return base, {k: v for k, v in meta.items() if k != "mask"}


def q(series: pd.Series, pct: float) -> float:
    return float(series.quantile(pct))


def descriptive_tables(base: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    work = base.loc[:, ["grid_id", "year", "maize_zone", "ca"]].dropna().copy()
    work["maize_zone"] = work["maize_zone"].astype(str)
    work = work.loc[work["maize_zone"].isin(REGION_ORDER)].copy()

    grid = (
        work.groupby(["maize_zone", "grid_id"], as_index=False)
        .agg(
            n_years=("year", "nunique"),
            ca_grid_mean=("ca", "mean"),
            ca_grid_sd=("ca", "std"),
            ca_grid_min=("ca", "min"),
            ca_grid_max=("ca", "max"),
        )
        .assign(ca_grid_range=lambda d: d["ca_grid_max"] - d["ca_grid_min"])
    )
    grid["ca_grid_sd"] = grid["ca_grid_sd"].fillna(0.0)

    rows: list[dict[str, object]] = []
    for region in REGION_ORDER:
        sub = work.loc[work["maize_zone"].eq(region)]
        gsub = grid.loc[grid["maize_zone"].eq(region)]
        rows.append(
            {
                "sample_id": SAMPLE_ID,
                "region": region,
                "region_label": REGION_LABELS[region],
                "N_rows": int(len(sub)),
                "N_grids": int(sub["grid_id"].nunique()),
                "N_years_min": int(sub.groupby("grid_id")["year"].nunique().min()),
                "N_years_max": int(sub.groupby("grid_id")["year"].nunique().max()),
                "ca_mean": float(sub["ca"].mean()),
                "ca_sd": float(sub["ca"].std(ddof=1)),
                "ca_min": float(sub["ca"].min()),
                "ca_p10": q(sub["ca"], 0.10),
                "ca_p25": q(sub["ca"], 0.25),
                "ca_p50": q(sub["ca"], 0.50),
                "ca_p75": q(sub["ca"], 0.75),
                "ca_p90": q(sub["ca"], 0.90),
                "ca_max": float(sub["ca"].max()),
                "share_ca_gt0": float((sub["ca"] > 0).mean()),
                "share_ca_ge025": float((sub["ca"] >= 0.25).mean()),
                "share_ca_ge050": float((sub["ca"] >= 0.50).mean()),
                "share_ca_ge075": float((sub["ca"] >= 0.75).mean()),
                "gridmean_ca_mean": float(gsub["ca_grid_mean"].mean()),
                "gridmean_ca_p25": q(gsub["ca_grid_mean"], 0.25),
                "gridmean_ca_p50": q(gsub["ca_grid_mean"], 0.50),
                "gridmean_ca_p75": q(gsub["ca_grid_mean"], 0.75),
                "within_grid_ca_sd_mean": float(gsub["ca_grid_sd"].mean()),
                "within_grid_ca_sd_p50": q(gsub["ca_grid_sd"], 0.50),
                "within_grid_ca_range_mean": float(gsub["ca_grid_range"].mean()),
                "within_grid_ca_range_p50": q(gsub["ca_grid_range"], 0.50),
                "share_grids_with_ca_change": float((gsub["ca_grid_range"] > 1e-12).mean()),
            }
        )
    summary = pd.DataFrame(rows)
    return work, grid, summary


def plot_region_sr(work: pd.DataFrame, grid: pd.DataFrame, summary: pd.DataFrame, out_path: Path) -> None:
    colors = {
        "NE": "#2F5597",
        "HHH": "#C55A11",
        "NW": "#548235",
        "SW": "#7030A0",
        "SH": "#7F7F7F",
    }
    labels = [REGION_LABELS[r] for r in REGION_ORDER]
    data = [work.loc[work["maize_zone"].eq(r), "ca"].to_numpy(dtype=float) for r in REGION_ORDER]
    grid_sd_data = [grid.loc[grid["maize_zone"].eq(r), "ca_grid_sd"].to_numpy(dtype=float) for r in REGION_ORDER]

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), constrained_layout=True)
    ax = axes[0]
    bp = ax.boxplot(
        data,
        tick_labels=labels,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "black", "linewidth": 1.2},
        whiskerprops={"color": "#555555", "linewidth": 0.9},
        capprops={"color": "#555555", "linewidth": 0.9},
    )
    for patch, region in zip(bp["boxes"], REGION_ORDER):
        patch.set_facecolor(colors[region])
        patch.set_alpha(0.55)
        patch.set_edgecolor("#444444")
    means = summary.set_index("region").loc[REGION_ORDER, "ca_mean"].to_numpy(dtype=float)
    ax.scatter(np.arange(1, len(REGION_ORDER) + 1), means, marker="D", s=36, color="white", edgecolor="black", zorder=3)
    ax.set_ylim(-0.02, 1.02)
    ax.set_ylabel("SR adoption ratio (ca)")
    ax.set_title("A. Grid-year SR distribution by region")
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.6)
    ax.text(0.02, 0.97, "Diamond = mean; box = IQR", transform=ax.transAxes, va="top", fontsize=8)

    ax = axes[1]
    bp2 = ax.boxplot(
        grid_sd_data,
        tick_labels=labels,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "black", "linewidth": 1.2},
        whiskerprops={"color": "#555555", "linewidth": 0.9},
        capprops={"color": "#555555", "linewidth": 0.9},
    )
    for patch, region in zip(bp2["boxes"], REGION_ORDER):
        patch.set_facecolor(colors[region])
        patch.set_alpha(0.55)
        patch.set_edgecolor("#444444")
    sd_means = summary.set_index("region").loc[REGION_ORDER, "within_grid_ca_sd_mean"].to_numpy(dtype=float)
    ax.scatter(np.arange(1, len(REGION_ORDER) + 1), sd_means, marker="D", s=36, color="white", edgecolor="black", zorder=3)
    ax.set_ylim(bottom=-0.005)
    ax.set_ylabel("Within-grid SD of ca")
    ax.set_title("B. Within-grid SR variation by region")
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.6)
    ax.text(0.02, 0.97, "Computed across years within each grid", transform=ax.transAxes, va="top", fontsize=8)

    fig.suptitle("B067: Regional descriptive statistics of straw return adoption", fontsize=12, fontweight="bold")
    fig.savefig(out_path, dpi=300, facecolor="white")
    plt.close(fig)


def plot_region_sr_gridmean(grid: pd.DataFrame, out_path: Path) -> None:
    colors = {
        "NE": "#2F5597",
        "HHH": "#C55A11",
        "NW": "#548235",
        "SW": "#7030A0",
        "SH": "#7F7F7F",
    }
    labels = [REGION_LABELS[r] for r in REGION_ORDER]
    data = [grid.loc[grid["maize_zone"].eq(r), "ca_grid_mean"].to_numpy(dtype=float) for r in REGION_ORDER]

    fig, ax = plt.subplots(figsize=(7.2, 4.6), constrained_layout=True)
    parts = ax.violinplot(data, positions=np.arange(1, len(REGION_ORDER) + 1), showmeans=False, showmedians=False, showextrema=False)
    for body, region in zip(parts["bodies"], REGION_ORDER):
        body.set_facecolor(colors[region])
        body.set_edgecolor("#444444")
        body.set_alpha(0.45)

    bp = ax.boxplot(
        data,
        positions=np.arange(1, len(REGION_ORDER) + 1),
        widths=0.18,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "black", "linewidth": 1.2},
        whiskerprops={"color": "#333333", "linewidth": 0.8},
        capprops={"color": "#333333", "linewidth": 0.8},
    )
    for patch in bp["boxes"]:
        patch.set_facecolor("white")
        patch.set_edgecolor("#333333")
        patch.set_alpha(0.9)

    means = [np.nanmean(x) for x in data]
    ax.scatter(np.arange(1, len(REGION_ORDER) + 1), means, marker="D", s=34, color="white", edgecolor="black", zorder=4)
    ax.set_xticks(np.arange(1, len(REGION_ORDER) + 1))
    ax.set_xticklabels(labels)
    ax.set_ylim(-0.02, 1.02)
    ax.set_ylabel("Grid mean SR adoption ratio (mean ca across years)")
    ax.set_xlabel("Region")
    ax.set_title("B067: Distribution of grid-level mean straw return adoption")
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.6)
    ax.text(0.02, 0.97, "Unit = grid; diamond = regional mean; box = IQR", transform=ax.transAxes, va="top", fontsize=8)
    fig.savefig(out_path, dpi=300, facecolor="white")
    plt.close(fig)


def write_report(summary: pd.DataFrame, meta: dict[str, object], fig_path: Path) -> None:
    short = summary.loc[:, ["region", "N_rows", "N_grids", "ca_mean", "ca_p50", "within_grid_ca_sd_mean", "share_grids_with_ca_change"]].copy()
    for col in ["ca_mean", "ca_p50", "within_grid_ca_sd_mean", "share_grids_with_ca_change"]:
        short[col] = short[col].map(lambda x: f"{x:.4f}")
    md_rows = [
        "| region | N_rows | N_grids | ca_mean | ca_p50 | within_grid_ca_sd_mean | share_grids_with_ca_change |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in short.to_dict("records"):
        md_rows.append(
            f"| {row['region']} | {row['N_rows']} | {row['N_grids']} | {row['ca_mean']} | "
            f"{row['ca_p50']} | {row['within_grid_ca_sd_mean']} | {row['share_grids_with_ca_change']} |"
        )
    lines = [
        "# B067 不同 region 的 SR 描述性统计",
        "",
        "本文件只做描述统计，不重估回归。样本使用当前最新 `B067` scale，region 使用 `maize_zone`，SR 变量使用 `ca`。",
        "",
        f"- B067 样本行数：{int(meta['N_sample'])}",
        f"- B067 grid 数：{int(meta['N_grids_sample'])}",
        "- 样本规则：`zone_core=1, sr_within=1, years_ge3=0, stable_province=0`，其他可选清洗规则不启用。",
        "",
        "## 输出文件",
        "",
        "- `output/figures/f4_b067_v2/table13_region_sr_descriptive.csv`：region 层面的 grid-year SR 分布和 within-grid 变异摘要。",
        "- `output/figures/f4_b067_v2/table13_region_sr_gridlevel.csv`：每个 region-grid 的多年平均 SR、grid 内标准差和极差。",
        "- `output/figures/f4_b067_v2/fig13_region_sr_descriptive.png`：左图为 grid-year `ca` 分布，右图为 grid 内 `ca` 时间变异。",
        "",
        "## 快速读数",
        "",
        "\n".join(md_rows),
        "",
        "解释：`ca_mean` 和 `ca_p50` 是 grid-year 层面的 SR 采用比例均值和中位数；`within_grid_ca_sd_mean` 是先在每个 grid 内按年份计算 `ca` 标准差，再对 region 内 grid 取平均；`share_grids_with_ca_change` 是该 region 中 `ca` 跨年份发生变化的 grid 比例。",
        "",
        f"图文件：`{fig_path.as_posix()}`",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_panel()
    base, meta = b067_sample(df)
    work, grid, summary = descriptive_tables(base)

    expected_n = int(meta["N_sample"])
    if len(work) != expected_n:
        raise RuntimeError(f"region rows sum {len(work)} != B067 N {expected_n}")
    if int(work["grid_id"].nunique()) != int(meta["N_grids_sample"]):
        raise RuntimeError("grid count does not match B067 metadata")

    summary_path = OUT_DIR / "table13_region_sr_descriptive.csv"
    grid_path = OUT_DIR / "table13_region_sr_gridlevel.csv"
    fig_path = OUT_DIR / "fig13_region_sr_descriptive.png"
    fig_gridmean_path = OUT_DIR / "fig13_region_sr_gridmean_distribution.png"
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    grid.to_csv(grid_path, index=False, encoding="utf-8-sig")
    plot_region_sr(work, grid, summary, fig_path)
    plot_region_sr_gridmean(grid, fig_gridmean_path)
    with Image.open(fig_path) as img:
        if img.size[0] <= 0 or img.size[1] <= 0:
            raise RuntimeError("empty figure")
        image_size = img.size
    with Image.open(fig_gridmean_path) as img:
        if img.size[0] <= 0 or img.size[1] <= 0:
            raise RuntimeError("empty gridmean figure")
        gridmean_image_size = img.size
    write_report(summary, meta, fig_path)

    print(f"summary={summary_path}")
    print(f"gridlevel={grid_path}")
    print(f"figure={fig_path}")
    print(f"gridmean_figure={fig_gridmean_path}")
    print(f"report={REPORT_MD}")
    print(f"rows={len(work)} grids={work['grid_id'].nunique()} figure_size={image_size} gridmean_figure_size={gridmean_image_size}")


if __name__ == "__main__":
    main()
