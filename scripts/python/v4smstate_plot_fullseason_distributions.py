"""
v4smstate_plot_fullseason_distributions.py
Purpose: Plot full-season raw SM distributions for the six source-layer series.
Author: YangSu + Codex
Date: 2026-04-21
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(r"C:\YangSu\00_Project\CA_mechanism\regression_SR")
TEMPDIR = ROOT / "temp" / "2026-04-21_sm_state_audit"
INPUT_DTA = TEMPDIR / "sm_state_analysis_ready.dta"

SERIES = [
    {"var": "gleam_sms_mean", "label": "GLEAM-Sfc", "fname": "sm_full_dist_gleam_sfc.png", "color": "#2E7D32"},
    {"var": "gleam_smrz_mean", "label": "GLEAM-Root", "fname": "sm_full_dist_gleam_root.png", "color": "#1B5E20"},
    {"var": "swsm_l1_mean", "label": "SWSM-L1", "fname": "sm_full_dist_swsm_l1.png", "color": "#E65100"},
    {"var": "swsm_l3_mean", "label": "SWSM-L3", "fname": "sm_full_dist_swsm_l3.png", "color": "#BF360C"},
    {"var": "era5l_swvl1_mean", "label": "ERA5L-L1", "fname": "sm_full_dist_era5l_l1.png", "color": "#1565C0"},
    {"var": "era5l_swvl3_mean", "label": "ERA5L-L3", "fname": "sm_full_dist_era5l_l3.png", "color": "#0D47A1"},
]


def load_data() -> pd.DataFrame:
    cols = ["state_full_6_sample"] + [item["var"] for item in SERIES]
    df = pd.read_stata(INPUT_DTA, columns=cols, convert_categoricals=False)
    df = df.loc[df["state_full_6_sample"] == 1, cols[1:]].copy()
    for item in SERIES:
        if df[item["var"]].isna().any():
            raise RuntimeError(f"Missing values found in {item['var']} under state_full_6_sample")
    return df


def add_reference_lines(ax: plt.Axes, values: pd.Series) -> None:
    mean_v = values.mean()
    p25, p50, p75 = values.quantile([0.25, 0.50, 0.75]).tolist()
    ax.axvline(mean_v, color="#212121", linestyle="-", linewidth=1.5, label=f"Mean = {mean_v:.3f}")
    ax.axvline(p25, color="#616161", linestyle="--", linewidth=1.1, label=f"P25 = {p25:.3f}")
    ax.axvline(p50, color="#424242", linestyle=":", linewidth=1.3, label=f"P50 = {p50:.3f}")
    ax.axvline(p75, color="#9E9E9E", linestyle="--", linewidth=1.1, label=f"P75 = {p75:.3f}")


def draw_single(values: pd.Series, meta: dict[str, str], n_obs: int) -> None:
    fig, ax = plt.subplots(figsize=(6, 4), facecolor="white")
    ax.hist(
        values,
        bins=35,
        density=True,
        color=meta["color"],
        alpha=0.75,
        edgecolor="white",
        linewidth=0.5,
    )
    add_reference_lines(ax, values)
    ax.set_title(f"{meta['label']} Full-Season SM Distribution", fontsize=12)
    ax.set_xlabel("Soil moisture")
    ax.set_ylabel("Density")
    ax.grid(axis="y", alpha=0.2, linewidth=0.5)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.text(
        0.98,
        0.95,
        f"N = {n_obs:,}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        color="#424242",
    )
    fig.tight_layout()
    fig.savefig(TEMPDIR / meta["fname"], dpi=300, facecolor="white")
    plt.close(fig)


def draw_panel(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(12, 7.8), facecolor="white")
    axes = axes.flatten()
    n_obs = len(df)

    for ax, meta in zip(axes, SERIES):
        values = df[meta["var"]]
        ax.hist(
            values,
            bins=35,
            density=True,
            color=meta["color"],
            alpha=0.75,
            edgecolor="white",
            linewidth=0.4,
        )
        add_reference_lines(ax, values)
        ax.set_title(meta["label"], fontsize=11)
        ax.set_xlabel("Soil moisture")
        ax.set_ylabel("Density")
        ax.grid(axis="y", alpha=0.2, linewidth=0.5)
        ax.text(
            0.98,
            0.95,
            f"N = {n_obs:,}",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=8.5,
            color="#424242",
        )

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, frameon=False, fontsize=8.5)
    fig.suptitle("Full-Season Raw Soil Moisture Distributions", fontsize=14, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(TEMPDIR / "sm_full_dist_6panel.png", dpi=300, facecolor="white")
    plt.close(fig)


def main() -> None:
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"
    plt.rcParams["font.family"] = "sans-serif"

    df = load_data()
    n_obs = len(df)

    for meta in SERIES:
        draw_single(df[meta["var"]], meta, n_obs)

    draw_panel(df)


if __name__ == "__main__":
    main()
