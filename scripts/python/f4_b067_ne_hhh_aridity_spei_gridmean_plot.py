"""Grid-mean aridity and reconstructed SPEI distributions for NE and HHH."""

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

from bio_window_filter_128 import load_panel, unique_variants  # noqa: E402


SAMPLE_ID = "B067"
REGIONS = ("NE", "HHH")
REGION_LABELS = {"NE": "Northeast (NE)", "HHH": "Huang-Huai-Hai (HHH)"}
WINDOWS = ("full", "v3pre30", "v3pm10", "hepm10", "v3he", "hema")
WINDOW_LABELS = {
    "full": "Full",
    "v3pre30": "V3-30",
    "v3pm10": "V3+/-10",
    "hepm10": "HE+/-10",
    "v3he": "V3-HE",
    "hema": "HE-MA",
}
OUT_DIR = PROJ / "output/figures/f4_b067_v2"
FIG_PATH = OUT_DIR / "fig15_ne_hhh_aridity_spei_gridmean_distribution.png"
GRID_PATH = OUT_DIR / "table15_ne_hhh_aridity_spei_gridlevel.csv"
SUMMARY_PATH = OUT_DIR / "table15_ne_hhh_aridity_spei_gridmean_descriptive.csv"
REPORT_MD = PROJ / "quality_reports/2026-06-04_ne_hhh_aridity_spei_gridmean_distribution.md"


def b067_sample(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    variant = next(v for v in unique_variants(df) if v["sample_id"] == SAMPLE_ID)
    sub = df.loc[variant["mask"]].copy()
    return sub, {k: v for k, v in variant.items() if k != "mask"}


def d_var(window: str) -> str:
    return "D_full" if window == "full" else f"D_{window}"


def w_var(window: str) -> str:
    return "W_full" if window == "full" else f"W_{window}"


def add_spei(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for window in WINDOWS:
        out[f"spei_{window}"] = out[w_var(window)] - out[d_var(window)]
    return out


def make_gridlevel(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["aridity", *[f"spei_{w}" for w in WINDOWS]]
    grid = df.groupby(["maize_zone", "grid_id"], as_index=False).agg(
        N_years=("year", "nunique"),
        **{f"{col}_gridmean": (col, "mean") for col in cols},
    )
    return grid


def summarize_series(x: pd.Series) -> dict[str, float | int]:
    y = x.dropna()
    return {
        "N_grids": int(y.size),
        "mean": float(y.mean()),
        "sd": float(y.std(ddof=1)),
        "p10": float(y.quantile(0.10)),
        "p25": float(y.quantile(0.25)),
        "p50": float(y.quantile(0.50)),
        "p75": float(y.quantile(0.75)),
        "p90": float(y.quantile(0.90)),
        "share_lt0": float((y < 0).mean()),
        "share_le_minus1": float((y <= -1).mean()),
    }


def make_summary(grid: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    variables = [("aridity_gridmean", "aridity")]
    variables.extend((f"spei_{w}_gridmean", f"spei_{w}") for w in WINDOWS)
    for region in REGIONS:
        sub = grid.loc[grid["maize_zone"].astype(str).eq(region)]
        for col, variable in variables:
            row = {"sample_id": SAMPLE_ID, "region": region, "variable": variable}
            row.update(summarize_series(sub[col]))
            rows.append(row)
    return pd.DataFrame(rows)


def plot_distributions(grid: pd.DataFrame) -> None:
    fig, axes = plt.subplots(len(REGIONS), 2, figsize=(12.0, 7.6), constrained_layout=True)
    region_colors = {"NE": "#4E79A7", "HHH": "#C55A11"}
    spei_color = "#59A14F"
    for row, region in enumerate(REGIONS):
        sub = grid.loc[grid["maize_zone"].astype(str).eq(region)].copy()
        aridity = sub["aridity_gridmean"].dropna().to_numpy(dtype=float)
        ax = axes[row, 0]
        ax.hist(aridity, bins=30, density=True, color=region_colors[region], alpha=0.72, edgecolor="white", linewidth=0.6)
        ax.axvline(np.median(aridity), color="#111111", linewidth=1.2, label=f"median={np.median(aridity):.3f}")
        ax.axvline(np.mean(aridity), color="#D55E00", linewidth=1.2, linestyle="--", label=f"mean={np.mean(aridity):.3f}")
        ax.set_title(f"{REGION_LABELS[region]}: grid-mean aridity", fontsize=10.5, fontweight="bold")
        ax.set_xlabel("Grid mean aridity")
        ax.set_ylabel("Density")
        ax.grid(axis="y", color="#E6E6E6", linewidth=0.65)
        ax.legend(frameon=False, fontsize=8)

        ax = axes[row, 1]
        spei_data = [sub[f"spei_{w}_gridmean"].dropna().to_numpy(dtype=float) for w in WINDOWS]
        parts = ax.violinplot(spei_data, positions=np.arange(1, len(WINDOWS) + 1), showmeans=False, showmedians=False, showextrema=False)
        for body in parts["bodies"]:
            body.set_facecolor(spei_color)
            body.set_edgecolor("#333333")
            body.set_alpha(0.45)
        bp = ax.boxplot(
            spei_data,
            positions=np.arange(1, len(WINDOWS) + 1),
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
        ax.scatter(np.arange(1, len(WINDOWS) + 1), means, marker="D", s=32, color="white", edgecolor="black", zorder=4)
        ax.axhline(0, color="#777777", linewidth=0.8, linestyle="--")
        ax.axhline(-1, color="#B22222", linewidth=0.8, linestyle=":", alpha=0.85)
        ax.set_xticks(np.arange(1, len(WINDOWS) + 1))
        ax.set_xticklabels([WINDOW_LABELS[w] for w in WINDOWS], rotation=32, ha="right")
        ax.set_title(f"{REGION_LABELS[region]}: grid-mean SPEI by window", fontsize=10.5, fontweight="bold")
        ax.set_xlabel("Window")
        ax.set_ylabel("Grid mean SPEI")
        ax.grid(axis="y", color="#E6E6E6", linewidth=0.65)
        ax.text(0.02, 0.97, "Diamond = mean; box = IQR; dashed = 0; dotted = -1", transform=ax.transAxes, va="top", fontsize=8)

    fig.suptitle("B067 NE and HHH: grid-level mean aridity and SPEI distributions", fontsize=13, fontweight="bold")
    FIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_PATH, dpi=300, facecolor="white")
    plt.close(fig)


def md_table(df: pd.DataFrame) -> str:
    cols = ["region", "variable", "N_grids", "mean", "p25", "p50", "p75", "share_lt0", "share_le_minus1"]
    lines = ["| " + " | ".join(cols) + " |", "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for row in df[cols].to_dict("records"):
        lines.append(
            f"| {row['region']} | {row['variable']} | {int(row['N_grids'])} | "
            f"{row['mean']:.3f} | {row['p25']:.3f} | {row['p50']:.3f} | {row['p75']:.3f} | "
            f"{row['share_lt0']:.3f} | {row['share_le_minus1']:.3f} |"
        )
    return "\n".join(lines)


def write_report(summary: pd.DataFrame, support: pd.DataFrame) -> None:
    lines = [
        "# NE and HHH grid-mean aridity/SPEI distributions",
        "",
        "本文件只做描述统计和图形，不重估回归。样本为当前 `B067` scale。",
        "",
        "## Support",
        "",
        "| region | obs | grids |",
        "|---|---:|---:|",
    ]
    for row in support.to_dict("records"):
        lines.append(f"| {row['region']} | {int(row['obs'])} | {int(row['grids'])} |")
    lines.extend(
        [
            "",
            "## Grid-mean descriptive statistics",
            "",
            md_table(summary),
            "",
            "## Output files",
            "",
            "- `output/figures/f4_b067_v2/fig15_ne_hhh_aridity_spei_gridmean_distribution.png`",
            "- `output/figures/f4_b067_v2/table15_ne_hhh_aridity_spei_gridlevel.csv`",
            "- `output/figures/f4_b067_v2/table15_ne_hhh_aridity_spei_gridmean_descriptive.csv`",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def append_caption() -> None:
    cap = OUT_DIR / "figure_captions.md"
    text = (
        "\n\n---\n\n"
        "## Fig 15. NE and HHH grid-mean aridity and SPEI distributions\n"
        "![fig15](fig15_ne_hhh_aridity_spei_gridmean_distribution.png)\n\n"
        "This figure uses the B067 NE and HHH samples and first averages each variable within `grid_id` across years. "
        "The left column shows grid-mean `aridity`; the right column shows reconstructed grid-mean SPEI by biological window, using `SPEI = W - D`.\n"
    )
    with cap.open("a", encoding="utf-8") as f:
        f.write(text)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_panel()
    base, _meta = b067_sample(df)
    base = add_spei(base)
    target = base.loc[base["maize_zone"].astype(str).isin(REGIONS)].copy()
    support = (
        target.groupby("maize_zone", as_index=False)
        .agg(obs=("grid_id", "size"), grids=("grid_id", "nunique"))
        .rename(columns={"maize_zone": "region"})
    )
    expected = {"NE": (20818, 5655), "HHH": (12198, 3309)}
    for region, (obs, grids) in expected.items():
        got = support.loc[support["region"].eq(region)].iloc[0]
        if int(got["obs"]) != obs or int(got["grids"]) != grids:
            raise RuntimeError(f"unexpected support for {region}: {got.to_dict()}")
    grid = make_gridlevel(target)
    summary = make_summary(grid)
    grid.to_csv(GRID_PATH, index=False, encoding="utf-8-sig")
    summary.to_csv(SUMMARY_PATH, index=False, encoding="utf-8-sig")
    plot_distributions(grid)
    with Image.open(FIG_PATH) as img:
        if img.size[0] <= 0 or img.size[1] <= 0:
            raise RuntimeError("empty figure")
        image_size = img.size
    write_report(summary, support)
    append_caption()
    print(
        {
            "support": support.to_dict("records"),
            "grid_rows": int(len(grid)),
            "summary_rows": int(len(summary)),
            "figure": str(FIG_PATH),
            "figure_size": image_size,
            "report": str(REPORT_MD),
        },
        flush=True,
    )


if __name__ == "__main__":
    main()
