"""Render three descriptive/inferential figures for the event override report."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ZONE_ORDER = ("NE", "HHH", "NW", "SW", "SH")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage1-dir", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def save(figure: plt.Figure, path: Path) -> None:
    figure.tight_layout()
    figure.savefig(path, dpi=300, facecolor="white")
    plt.close(figure)


def main() -> int:
    args = parse_args()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"refusing to overwrite nonempty report directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "sans-serif", "font.size": 10})

    results = pd.read_csv(args.model_dir / "conditional_damage_results.csv")
    order = [(zone, exposure) for zone in ZONE_ORDER for exposure in ("duration", "intensity")]
    results["order"] = results.apply(lambda row: order.index((row["zone"], row["exposure"])), axis=1)
    plot = results.sort_values("order", ascending=False).reset_index(drop=True)
    labels = [f"{row.zone} - {row.exposure}" for row in plot.itertuples()]
    y = np.arange(len(plot))
    figure, axis = plt.subplots(figsize=(12, 5))
    axis.errorbar(
        plot["effect_percent"],
        y,
        xerr=np.vstack([
            plot["effect_percent"] - plot["boot_ci_low_percent"],
            plot["boot_ci_high_percent"] - plot["effect_percent"],
        ]),
        fmt="o",
        color="#1f4e79",
        ecolor="#6b8eae",
        capsize=3,
    )
    axis.axvline(0, color="black", linewidth=0.8)
    axis.set_yticks(y, labels)
    axis.set_xlabel("Conditional damage difference: CA P75 vs P25 (%)")
    axis.grid(axis="x", color="#dddddd", linewidth=0.6)
    save(figure, output / "fig1_conditional_damage_forest.png")

    support = pd.read_csv(args.stage1_dir / "support_by_zone.csv").set_index("zone").loc[list(ZONE_ORDER)]
    figure, axis = plt.subplots(figsize=(12, 5))
    x = np.arange(len(support))
    axis.bar(x - 0.18, support["event_positive_grid_years"], width=0.36, label="Event-positive grid-years", color="#4c78a8")
    axis.bar(x + 0.18, support["event_count"], width=0.36, label="Events", color="#f58518")
    axis.set_xticks(x, support.index)
    axis.set_ylabel("Count")
    axis.legend(frameon=False)
    axis.grid(axis="y", color="#dddddd", linewidth=0.6)
    save(figure, output / "fig2_event_support.png")

    sm = pd.read_csv(args.model_dir / "sm_channel_support.csv")
    sm = sm[sm["ca_group"].isin(["P25_or_lower", "P75_or_higher"])].copy()
    pivot = sm.pivot(index="zone", columns="ca_group", values="drawdown_smrz_mean").loc[list(ZONE_ORDER)]
    figure, axis = plt.subplots(figsize=(12, 5))
    x = np.arange(len(pivot))
    axis.bar(x - 0.18, pivot["P25_or_lower"], width=0.36, label="CA <= P25", color="#72b7b2")
    axis.bar(x + 0.18, pivot["P75_or_higher"], width=0.36, label="CA >= P75", color="#e45756")
    axis.set_xticks(x, pivot.index)
    axis.set_ylabel("Mean SMrz drawdown (m3/m3; unadjusted)")
    axis.legend(frameon=False)
    axis.grid(axis="y", color="#dddddd", linewidth=0.6)
    save(figure, output / "fig3_smrz_drawdown_descriptive.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
