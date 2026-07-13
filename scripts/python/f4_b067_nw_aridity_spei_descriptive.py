"""Descriptive statistics for aridity and reconstructed SPEI in NW B067 sample."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from PIL import Image


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
SCRIPT_DIR = PROJ / "scripts/python"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from bio_window_filter_128 import load_panel, unique_variants  # noqa: E402


SAMPLE_ID = "B067"
REGION = "NW"
OUT_DIR = PROJ / "output/figures/f4_b067_v2"
REPORT_MD = PROJ / "quality_reports/2026-06-04_nw_aridity_spei_descriptive.md"
FIG_PATH = OUT_DIR / "fig14_nw_aridity_spei_gridmean_distribution.png"
WINDOWS = ("full", "v3pre30", "v3pm10", "hepm10", "v3he", "hema")
WINDOW_LABELS = {
    "full": "Full season",
    "v3pre30": "V3 pre-30",
    "v3pm10": "V3 +/-10",
    "hepm10": "HE +/-10",
    "v3he": "V3-HE",
    "hema": "HE-MA",
}


def b067_sample(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    variant = next(v for v in unique_variants(df) if v["sample_id"] == SAMPLE_ID)
    sub = df.loc[variant["mask"]].copy()
    return sub, {k: v for k, v in variant.items() if k != "mask"}


def d_var(window: str) -> str:
    return "D_full" if window == "full" else f"D_{window}"


def w_var(window: str) -> str:
    return "W_full" if window == "full" else f"W_{window}"


def add_spei(work: pd.DataFrame) -> pd.DataFrame:
    out = work.copy()
    for window in WINDOWS:
        out[f"spei_{window}"] = out[w_var(window)] - out[d_var(window)]
    return out


def summarize_series(series: pd.Series) -> dict[str, float | int]:
    x = series.dropna()
    return {
        "N": int(x.size),
        "missing": int(series.isna().sum()),
        "mean": float(x.mean()),
        "sd": float(x.std(ddof=1)),
        "min": float(x.min()),
        "p05": float(x.quantile(0.05)),
        "p10": float(x.quantile(0.10)),
        "p25": float(x.quantile(0.25)),
        "p50": float(x.quantile(0.50)),
        "p75": float(x.quantile(0.75)),
        "p90": float(x.quantile(0.90)),
        "p95": float(x.quantile(0.95)),
        "max": float(x.max()),
        "share_lt0": float((x < 0).mean()),
        "share_le_minus1": float((x <= -1).mean()),
        "share_le_minus15": float((x <= -1.5).mean()),
        "share_le_minus2": float((x <= -2).mean()),
    }


def make_obs_summary(nw: pd.DataFrame) -> pd.DataFrame:
    rows = []
    variables = [("aridity", "aridity", "Aridity")]
    variables.extend((f"spei_{w}", f"spei_{w}", f"SPEI {WINDOW_LABELS[w]}") for w in WINDOWS)
    for var, variable, label in variables:
        row = {
            "sample_id": SAMPLE_ID,
            "region": REGION,
            "scale": "grid_year_obs",
            "variable": variable,
            "label": label,
        }
        row.update(summarize_series(nw[var]))
        rows.append(row)
    return pd.DataFrame(rows)


def make_gridlevel(nw: pd.DataFrame) -> pd.DataFrame:
    cols = ["aridity", *[f"spei_{w}" for w in WINDOWS]]
    grid = nw.groupby("grid_id", as_index=False).agg(
        maize_zone=("maize_zone", "first"),
        N_years=("year", "nunique"),
        **{f"{col}_gridmean": (col, "mean") for col in cols},
        **{f"{col}_gridsd": (col, "std") for col in cols},
    )
    for col in cols:
        grid[f"{col}_gridsd"] = grid[f"{col}_gridsd"].fillna(0.0)
    return grid


def make_gridmean_summary(grid: pd.DataFrame) -> pd.DataFrame:
    rows = []
    variables = [("aridity_gridmean", "aridity", "Aridity")]
    variables.extend((f"spei_{w}_gridmean", f"spei_{w}", f"SPEI {WINDOW_LABELS[w]}") for w in WINDOWS)
    for col, variable, label in variables:
        row = {
            "sample_id": SAMPLE_ID,
            "region": REGION,
            "scale": "grid_mean",
            "variable": variable,
            "label": label,
        }
        row.update(summarize_series(grid[col]))
        rows.append(row)
    return pd.DataFrame(rows)


def plot_gridmean_distributions(grid: pd.DataFrame) -> None:
    spei_cols = [f"spei_{w}_gridmean" for w in WINDOWS]
    spei_labels = [WINDOW_LABELS[w] for w in WINDOWS]
    spei_data = [grid[col].dropna().to_numpy(dtype=float) for col in spei_cols]

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.6), constrained_layout=True)

    ax = axes[0]
    aridity = grid["aridity_gridmean"].dropna().to_numpy(dtype=float)
    ax.hist(aridity, bins=28, density=True, color="#4E79A7", alpha=0.72, edgecolor="white", linewidth=0.6)
    ax.axvline(np.median(aridity), color="#111111", linewidth=1.2, label=f"median={np.median(aridity):.3f}")
    ax.axvline(np.mean(aridity), color="#D55E00", linewidth=1.2, linestyle="--", label=f"mean={np.mean(aridity):.3f}")
    ax.set_title("A. Grid-mean aridity", fontsize=11, fontweight="bold")
    ax.set_xlabel("Grid mean aridity")
    ax.set_ylabel("Density")
    ax.grid(axis="y", color="#E6E6E6", linewidth=0.65)
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1]
    parts = ax.violinplot(spei_data, positions=np.arange(1, len(spei_data) + 1), showmeans=False, showmedians=False, showextrema=False)
    for body in parts["bodies"]:
        body.set_facecolor("#59A14F")
        body.set_edgecolor("#333333")
        body.set_alpha(0.45)
    bp = ax.boxplot(
        spei_data,
        positions=np.arange(1, len(spei_data) + 1),
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
        patch.set_alpha(0.92)
    means = [float(np.mean(x)) for x in spei_data]
    ax.scatter(np.arange(1, len(spei_data) + 1), means, marker="D", s=32, color="white", edgecolor="black", zorder=4)
    ax.axhline(0, color="#777777", linewidth=0.8, linestyle="--")
    ax.axhline(-1, color="#B22222", linewidth=0.8, linestyle=":", alpha=0.85)
    ax.set_xticks(np.arange(1, len(spei_data) + 1))
    ax.set_xticklabels(spei_labels, rotation=35, ha="right")
    ax.set_title("B. Grid-mean SPEI by window", fontsize=11, fontweight="bold")
    ax.set_xlabel("Window")
    ax.set_ylabel("Grid mean SPEI")
    ax.grid(axis="y", color="#E6E6E6", linewidth=0.65)
    ax.text(0.02, 0.97, "Diamond = mean; box = IQR; dashed line = 0; dotted line = -1", transform=ax.transAxes, va="top", fontsize=8)

    fig.suptitle("NW B067: grid-level mean aridity and SPEI distributions", fontsize=13, fontweight="bold")
    FIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_PATH, dpi=300, facecolor="white")
    plt.close(fig)


def fmt(x: object, digits: int = 3) -> str:
    if pd.isna(x):
        return ""
    if isinstance(x, str):
        return x
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    return f"{float(x):.{digits}f}"


def md_table(df: pd.DataFrame, cols: list[str], digits: int = 3) -> str:
    lines = ["| " + " | ".join(cols) + " |"]
    aligns = ["---" if c in {"variable", "label", "scale"} else "---:" for c in cols]
    lines.append("|" + "|".join(aligns) + "|")
    for row in df[cols].to_dict("records"):
        lines.append("| " + " | ".join(fmt(row[c], digits) for c in cols) + " |")
    return "\n".join(lines)


def write_report(obs: pd.DataFrame, gridmean: pd.DataFrame, grid: pd.DataFrame, meta: dict[str, object]) -> None:
    keep_cols = ["variable", "N", "mean", "sd", "p10", "p25", "p50", "p75", "p90", "share_lt0", "share_le_minus1"]
    lines = [
        "# NW aridity and SPEI descriptive statistics",
        "",
        "本文件只做描述统计，不重估回归。",
        "",
        f"- 样本：`{SAMPLE_ID}`",
        f"- B067 全样本：{int(meta['N_sample'])} obs，{int(meta['N_grids_sample'])} grids",
        f"- 区域：`maize_zone == \"{REGION}\"`",
        f"- NW 样本：{int(obs.loc[obs['variable'].eq('aridity'), 'N'].iloc[0])} obs，{int(len(grid))} grids",
        "- `ari` 按数据中的 `aridity` 变量处理。",
        "- `SPEI` 按 `SPEI = W - D` 从窗口 `D_*` 和 `W_*` 还原；该还原对应脚本中 `D=max(0,-SPEI)`、`W=max(0,SPEI)` 的定义。",
        "",
        "## Grid-year obs scale",
        "",
        md_table(obs, keep_cols),
        "",
        "## Grid mean scale",
        "",
        md_table(gridmean, keep_cols),
        "",
        "## Output files",
        "",
        "- `output/figures/f4_b067_v2/table14_nw_aridity_spei_obs_descriptive.csv`",
        "- `output/figures/f4_b067_v2/table14_nw_aridity_spei_gridmean_descriptive.csv`",
        "- `output/figures/f4_b067_v2/table14_nw_aridity_spei_gridlevel.csv`",
        "- `output/figures/f4_b067_v2/fig14_nw_aridity_spei_gridmean_distribution.png`",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_panel()
    base, meta = b067_sample(df)
    nw = base.loc[base["maize_zone"].astype(str).eq(REGION)].copy()
    nw = add_spei(nw)
    if len(nw) != 3381 or int(nw["grid_id"].nunique()) != 1113:
        raise RuntimeError(f"unexpected NW support: rows={len(nw)}, grids={nw['grid_id'].nunique()}")
    obs = make_obs_summary(nw)
    grid = make_gridlevel(nw)
    gridmean = make_gridmean_summary(grid)
    if obs["N"].min() <= 0 or gridmean["N"].min() <= 0:
        raise RuntimeError("empty descriptive statistics")
    obs.to_csv(OUT_DIR / "table14_nw_aridity_spei_obs_descriptive.csv", index=False, encoding="utf-8-sig")
    gridmean.to_csv(OUT_DIR / "table14_nw_aridity_spei_gridmean_descriptive.csv", index=False, encoding="utf-8-sig")
    grid.to_csv(OUT_DIR / "table14_nw_aridity_spei_gridlevel.csv", index=False, encoding="utf-8-sig")
    plot_gridmean_distributions(grid)
    with Image.open(FIG_PATH) as img:
        if img.size[0] <= 0 or img.size[1] <= 0:
            raise RuntimeError("empty gridmean distribution figure")
    write_report(obs, gridmean, grid, meta)
    print(
        {
            "nw_obs": int(len(nw)),
            "nw_grids": int(nw["grid_id"].nunique()),
            "obs_rows": int(len(obs)),
            "gridmean_rows": int(len(gridmean)),
            "figure": str(FIG_PATH),
            "report": str(REPORT_MD),
        },
        flush=True,
    )


if __name__ == "__main__":
    main()
