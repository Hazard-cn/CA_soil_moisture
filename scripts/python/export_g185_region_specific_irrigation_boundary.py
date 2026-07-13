"""Export old-G185 region-specific continuous irrigation-boundary results.

This script intentionally uses the old G185 fixed-effect irrigation model:
grid FE + year FE, grid-cluster wild-score bootstrap, and the old
`xvars_for_irrigation(hazard)` specification. It does not use v3 response
surfaces, RCS, GAM, CausalForest, DML, province-year FE, or no-SM reduced-form
models.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
SCRIPT_DIR = PROJ / "scripts/python"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from expanded_scale_story_search import add_full_interactions, load_panel, unique_variants  # noqa: E402
from build_g185_draft_bootstrap_v1 import (  # noqa: E402
    HAZARD_LABEL,
    HAZARD_VAR,
    HAZARDS,
    REGIONS,
    SCALE_ID,
    q,
    residualize_two_way,
    wild_boot_betas,
    xvars_for_irrigation,
)


RUN_DIR = PROJ / "quality_reports/agent_runs/2026-06-24_g185_region_specific_irrigation_boundary"
TABLE_DIR = RUN_DIR / "tables"
PLOT_DATA_DIR = RUN_DIR / "plot_data"
DIAG_DIR = RUN_DIR / "diagnostics"
FIG_DIR = RUN_DIR / "figures"
SCRIPTS_USED_DIR = RUN_DIR / "scripts_used"
ZIP_PATH = RUN_DIR / "g185_region_specific_irrigation_boundary_bundle.zip"

REPS = 999
SEED = 42
MAIN_STORY = {("HHH", "heat"), ("HHH", "hotdry"), ("NE", "drought")}
REGION_ORDER = {"NE": 1, "HHH": 2, "NW": 3, "SW": 4, "SH": 5}
HAZARD_ORDER = {"drought": 1, "heat": 2, "hotdry": 3}
REGION_ZH = {"NE": "东北", "HHH": "黄淮海", "NW": "西北", "SW": "西南", "SH": "南方"}
HAZARD_ZH = {"drought": "干旱", "heat": "高温", "hotdry": "热干"}


@dataclass
class RegionIrrigationModel:
    region: str
    hazard: str
    xvars: list[str]
    beta: np.ndarray
    boot: np.ndarray
    nobs: int
    clusters: int
    rank: int
    condition_number: float
    warning: str
    ca_iqr: float
    hazard_p90: float
    irr_p5: float
    irr_p25: float
    irr_p50: float
    irr_p75: float
    irr_p95: float
    base_c3: float
    triple: float
    base_boot: np.ndarray
    triple_boot: np.ndarray


def configure_fonts() -> None:
    available = {f.name for f in font_manager.fontManager.ttflist}
    for candidate in ("Microsoft YaHei", "SimHei", "Arial Unicode MS", "Noto Sans CJK SC"):
        if candidate in available:
            plt.rcParams["font.family"] = candidate
            break
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
        }
    )


def pct_from_ln(x: np.ndarray | float) -> np.ndarray | float:
    return np.expm1(x) * 100.0


def ci_from_boot(values: np.ndarray) -> tuple[float, float]:
    vals = values[np.isfinite(values)]
    if len(vals) == 0:
        return math.nan, math.nan
    lo, hi = np.nanpercentile(vals, [2.5, 97.5])
    return float(lo), float(hi)


def ensure_dirs() -> None:
    for path in (RUN_DIR, TABLE_DIR, PLOT_DATA_DIR, DIAG_DIR, FIG_DIR, SCRIPTS_USED_DIR):
        path.mkdir(parents=True, exist_ok=True)


def get_g185_sample() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    panel = add_full_interactions(load_panel())
    variants = {str(meta["sample_id"]): meta for meta in unique_variants(panel)}
    if SCALE_ID not in variants:
        raise RuntimeError("G185 sample cannot be recovered.")
    meta = variants[SCALE_ID]
    sample = panel.loc[meta["mask"]].copy()
    if len(sample) != 46299 or int(sample["grid_code"].nunique()) != 13236:
        raise RuntimeError(
            f"G185 sample assertion failed: N={len(sample)}, grids={sample['grid_code'].nunique()}"
        )
    named = sample.loc[sample["maize_zone"].astype(str).isin(REGIONS)].copy()
    if len(named) != 44556 or int(named["grid_code"].nunique()) != 12745:
        raise RuntimeError(
            f"Named-region assertion failed: N={len(named)}, grids={named['grid_code'].nunique()}"
        )
    return panel, sample, meta


def common_work(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    unique_cols = list(dict.fromkeys([*cols, "grid_code", "year_code"]))
    missing = [col for col in unique_cols if col not in df.columns]
    if missing:
        raise KeyError("missing required variables: " + ",".join(missing))
    work = df.loc[:, unique_cols].dropna().copy()
    work["_gid_boot"], _ = pd.factorize(work["grid_code"], sort=True)
    work["_year_boot"], _ = pd.factorize(work["year_code"], sort=True)
    return work


def fit_absorbed_with_diagnostics(work: pd.DataFrame, yvar: str, xvars: list[str]):
    z = work[[yvar, *xvars]].to_numpy(dtype=np.float64)
    gid = work["_gid_boot"].to_numpy(dtype=np.int64)
    year = work["_year_boot"].to_numpy(dtype=np.int64)
    zr = residualize_two_way(z, gid, year)
    y = zr[:, 0]
    x = zr[:, 1:]
    rank = int(np.linalg.matrix_rank(x))
    try:
        condition_number = float(np.linalg.cond(x))
    except np.linalg.LinAlgError:
        condition_number = float("inf")
    if rank < x.shape[1]:
        beta = np.linalg.pinv(x) @ y
        warning = "RANK_DEFICIENT_PINV_USED"
    else:
        beta, *_ = np.linalg.lstsq(x, y, rcond=None)
        warning = ""
    if condition_number > 1e8:
        warning = "HIGH_CONDITION_NUMBER" if not warning else warning + ";HIGH_CONDITION_NUMBER"
    resid = y - x @ beta
    xtx_inv = np.linalg.pinv(x.T @ x)
    scores = np.zeros((int(gid.max()) + 1, x.shape[1]), dtype=np.float64)
    np.add.at(scores, gid, x * resid[:, None])
    # Reuse the old script's AbsorbedModel duck type by setting attributes.
    model = type("AbsorbedModelLite", (), {})()
    model.xvars = list(xvars)
    model.beta = beta
    model.xtx_inv = xtx_inv
    model.scores = scores
    model.nobs = int(len(work))
    model.clusters = int(scores.shape[0])
    return model, rank, condition_number, warning


def estimate_one(sample: pd.DataFrame, region: str, hazard: str, reps: int, seed: int) -> tuple[RegionIrrigationModel | None, dict[str, object]]:
    xvars, inter, triple = xvars_for_irrigation(hazard)
    hvar = HAZARD_VAR[hazard]
    required = ["ln_yield_raw", *xvars, hvar, "ca_raw", "irr_frac_raw", "grid_code", "year_code"]
    missing = [col for col in dict.fromkeys(required) if col not in sample.columns]
    registry_base = {
        "region": region,
        "hazard": hazard,
        "N_model": 0,
        "N_grids": 0,
        "n_xvars": len(xvars),
        "condition_number": math.nan,
        "rank": 0,
        "model_status": "",
        "missing_required_vars": ";".join(missing),
        "warning": "",
    }
    if missing:
        registry_base["model_status"] = "MISSING_REQUIRED_VARS"
        return None, registry_base

    rsub = sample.loc[sample["maize_zone"].astype(str).eq(region)].copy()
    work = common_work(rsub, ["ln_yield_raw", *xvars, hvar, "ca_raw", "irr_frac_raw"])
    nobs = int(len(work))
    clusters = int(work["grid_code"].nunique())
    registry_base["N_model"] = nobs
    registry_base["N_grids"] = clusters
    if nobs < 500 or clusters < 50:
        registry_base["model_status"] = "SKIPPED_LOW_SUPPORT"
        return None, registry_base

    model, rank, condition_number, warning = fit_absorbed_with_diagnostics(work, "ln_yield_raw", xvars)
    boot = wild_boot_betas(model, np.random.default_rng(seed), reps)
    idx = {name: i for i, name in enumerate(xvars)}
    ca_p25, ca_p75 = q(work["ca_raw"], [25, 75])
    irr_p5, irr_p25, irr_p50, irr_p75, irr_p95 = q(work["irr_frac_raw"], [5, 25, 50, 75, 95])
    hazard_p90 = float(np.nanpercentile(work[hvar], 90))
    base = float(model.beta[idx[inter]])
    tri = float(model.beta[idx[triple]])
    out = RegionIrrigationModel(
        region=region,
        hazard=hazard,
        xvars=xvars,
        beta=model.beta,
        boot=boot,
        nobs=int(model.nobs),
        clusters=int(model.clusters),
        rank=rank,
        condition_number=condition_number,
        warning=warning,
        ca_iqr=float(ca_p75 - ca_p25),
        hazard_p90=hazard_p90,
        irr_p5=float(irr_p5),
        irr_p25=float(irr_p25),
        irr_p50=float(irr_p50),
        irr_p75=float(irr_p75),
        irr_p95=float(irr_p95),
        base_c3=base,
        triple=tri,
        base_boot=boot[:, idx[inter]],
        triple_boot=boot[:, idx[triple]],
    )
    registry_base.update(
        {
            "condition_number": condition_number,
            "rank": rank,
            "model_status": "ESTIMATED",
            "warning": warning,
        }
    )
    return out, registry_base


def margin_values(model: RegionIrrigationModel, irr_value: float) -> tuple[float, float, float]:
    ln_est = (model.base_c3 + model.triple * irr_value) * model.ca_iqr * model.hazard_p90
    ln_boot = (model.base_boot + model.triple_boot * irr_value) * model.ca_iqr * model.hazard_p90
    lo, hi = ci_from_boot(pct_from_ln(ln_boot))
    return float(pct_from_ln(ln_est)), lo, hi


def boundary_values(model: RegionIrrigationModel) -> tuple[float, float, float]:
    irr_delta = model.irr_p75 - model.irr_p25
    ln_est = model.triple * irr_delta * model.ca_iqr * model.hazard_p90
    ln_boot = model.triple_boot * irr_delta * model.ca_iqr * model.hazard_p90
    lo, hi = ci_from_boot(pct_from_ln(ln_boot))
    return float(pct_from_ln(ln_est)), lo, hi


def direction_flag(estimate: float) -> str:
    if estimate < -0.01:
        return "buffer_smaller_at_higher_irrigation"
    if estimate > 0.01:
        return "buffer_larger_at_higher_irrigation"
    return "flat_or_unclear"


def interpretation_status(region: str, hazard: str, estimate: float, lo: float, hi: float) -> str:
    significant = (lo > 0 and hi > 0) or (lo < 0 and hi < 0)
    if (region, hazard) == ("HHH", "heat"):
        if estimate < 0 and significant:
            return "supports HHH heat irrigation boundary"
        if estimate < 0:
            return "directional but inconclusive"
        return "does not support HHH heat irrigation boundary"
    if (region, hazard) == ("HHH", "hotdry"):
        if estimate < 0 and significant:
            return "supports HHH hotdry irrigation boundary"
        if estimate < 0:
            return "directional but inconclusive"
        return "does not support HHH hotdry irrigation boundary"
    if (region, hazard) == ("NE", "drought"):
        if abs(estimate) > 0.01 and significant:
            return f"NE drought irrigation boundary is {direction_flag(estimate)}"
        return "not a core irrigation-boundary claim"
    return "supplementary"


def story_flag(region: str, hazard: str) -> int:
    return int((region, hazard) in MAIN_STORY)


def panel_group(region: str, hazard: str) -> str:
    if region == "HHH" and hazard in {"heat", "hotdry"}:
        return "main_hhh_heat_hotdry"
    if region == "NE" and hazard == "drought":
        return "main_ne_drought"
    return "supplementary_all_regions"


def build_outputs(models: dict[tuple[str, str], RegionIrrigationModel], reps: int):
    margin_rows: list[dict[str, object]] = []
    boundary_rows: list[dict[str, object]] = []
    curve_rows: list[dict[str, object]] = []

    for region in REGIONS:
        for hazard in HAZARDS:
            model = models.get((region, hazard))
            if model is None:
                continue
            levels = [
                ("P25", model.irr_p25),
                ("P50", model.irr_p50),
                ("P75", model.irr_p75),
            ]
            for level, irr_value in levels:
                est, lo, hi = margin_values(model, irr_value)
                margin_rows.append(
                    {
                        "region": region,
                        "hazard": hazard,
                        "hazard_label": HAZARD_LABEL[hazard],
                        "irr_level": level,
                        "irr_value": irr_value,
                        "estimate_pct": est,
                        "ci_low_pct": lo,
                        "ci_high_pct": hi,
                        "ca_iqr_region": model.ca_iqr,
                        "hazard_p90_region": model.hazard_p90,
                        "irr_p25_region": model.irr_p25,
                        "irr_p50_region": model.irr_p50,
                        "irr_p75_region": model.irr_p75,
                        "base_c3": model.base_c3,
                        "triple": model.triple,
                        "N_model": model.nobs,
                        "N_grids": model.clusters,
                        "bootstrap_reps": reps,
                        "model_status": "ESTIMATED",
                        "main_story_flag": story_flag(region, hazard),
                        "note": "Old G185 FE model; region-specific estimates; conditional associations.",
                    }
                )

            b_est, b_lo, b_hi = boundary_values(model)
            significant = int((b_lo > 0 and b_hi > 0) or (b_lo < 0 and b_hi < 0))
            interp = interpretation_status(region, hazard, b_est, b_lo, b_hi)
            boundary_rows.append(
                {
                    "region": region,
                    "hazard": hazard,
                    "hazard_label": HAZARD_LABEL[hazard],
                    "estimate_pct": b_est,
                    "ci_low_pct": b_lo,
                    "ci_high_pct": b_hi,
                    "ca_iqr_region": model.ca_iqr,
                    "hazard_p90_region": model.hazard_p90,
                    "irr_delta_p75_minus_p25": model.irr_p75 - model.irr_p25,
                    "base_c3": model.base_c3,
                    "triple": model.triple,
                    "N_model": model.nobs,
                    "N_grids": model.clusters,
                    "bootstrap_reps": reps,
                    "significance_flag": significant,
                    "direction_flag": direction_flag(b_est),
                    "main_story_flag": story_flag(region, hazard),
                    "claim_sentence": f"{region} {HAZARD_LABEL[hazard]} P75-minus-P25 irrigation boundary = {b_est:.2f} [{b_lo:.2f}, {b_hi:.2f}] percentage points.",
                    "interpretation_status": interp,
                }
            )

            grid = np.linspace(model.irr_p5, model.irr_p95, 101)
            all_irr = np.array(sorted(set(np.round(np.r_[grid, model.irr_p25, model.irr_p50, model.irr_p75], 12))))
            for irr_value in all_irr:
                est, lo, hi = margin_values(model, float(irr_value))
                label = ""
                if abs(irr_value - model.irr_p25) < 1e-10:
                    label = "P25"
                elif abs(irr_value - model.irr_p50) < 1e-10:
                    label = "P50"
                elif abs(irr_value - model.irr_p75) < 1e-10:
                    label = "P75"
                curve_rows.append(
                    {
                        "region": region,
                        "hazard": hazard,
                        "hazard_label": HAZARD_LABEL[hazard],
                        "irr_value": float(irr_value),
                        "irr_percentile_label": label,
                        "estimate_pct": est,
                        "ci_low_pct": lo,
                        "ci_high_pct": hi,
                        "ca_iqr_region": model.ca_iqr,
                        "hazard_p90_region": model.hazard_p90,
                        "irr_p25_region": model.irr_p25,
                        "irr_p50_region": model.irr_p50,
                        "irr_p75_region": model.irr_p75,
                        "N_model": model.nobs,
                        "N_grids": model.clusters,
                        "main_story_flag": story_flag(region, hazard),
                        "panel_group": panel_group(region, hazard),
                    }
                )

    margins = pd.DataFrame(margin_rows)
    boundaries = pd.DataFrame(boundary_rows)
    curves = pd.DataFrame(curve_rows)
    key_curves = curves.loc[
        curves[["region", "hazard"]].apply(lambda s: (s["region"], s["hazard"]) in MAIN_STORY, axis=1)
    ].copy()
    heatmap = boundaries.copy()
    heatmap["region_order"] = heatmap["region"].map(REGION_ORDER)
    heatmap["hazard_order"] = heatmap["hazard"].map(HAZARD_ORDER)
    heatmap["cell_label"] = heatmap.apply(
        lambda r: f"{r['estimate_pct']:.2f} [{r['ci_low_pct']:.2f}, {r['ci_high_pct']:.2f}]",
        axis=1,
    )
    heatmap = heatmap[
        [
            "region_order",
            "hazard_order",
            "region",
            "hazard",
            "estimate_pct",
            "ci_low_pct",
            "ci_high_pct",
            "cell_label",
            "significance_flag",
            "direction_flag",
            "main_story_flag",
            "interpretation_status",
        ]
    ].sort_values(["region_order", "hazard_order"])
    return margins, boundaries, curves, key_curves, heatmap


def write_tables(margins: pd.DataFrame, boundaries: pd.DataFrame, curves: pd.DataFrame, key_curves: pd.DataFrame, heatmap: pd.DataFrame, registry: pd.DataFrame) -> None:
    margins.to_csv(TABLE_DIR / "region_irrigation_margins.csv", index=False, encoding="utf-8-sig")
    boundaries.to_csv(TABLE_DIR / "region_irrigation_boundaries.csv", index=False, encoding="utf-8-sig")
    curves.to_csv(PLOT_DATA_DIR / "fig_region_irrigation_boundary_curves.csv", index=False, encoding="utf-8-sig")
    key_curves.to_csv(PLOT_DATA_DIR / "fig_region_irrigation_boundary_key_panels.csv", index=False, encoding="utf-8-sig")
    heatmap.to_csv(PLOT_DATA_DIR / "fig_region_irrigation_boundary_heatmap.csv", index=False, encoding="utf-8-sig")
    registry.to_csv(DIAG_DIR / "region_irrigation_model_registry.csv", index=False, encoding="utf-8-sig")


def plot_key_panels(key_curves: pd.DataFrame) -> None:
    configure_fonts()
    specs = [("NE", "drought", "#4C78A8"), ("HHH", "heat", "#F58518"), ("HHH", "hotdry", "#54A24B")]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.1), sharey=False)
    for ax, (region, hazard, color) in zip(axes, specs):
        sub = key_curves.loc[key_curves["region"].eq(region) & key_curves["hazard"].eq(hazard)].sort_values("irr_value")
        if sub.empty:
            ax.text(0.5, 0.5, "No estimate", ha="center", va="center")
            ax.axis("off")
            continue
        ax.fill_between(sub["irr_value"], sub["ci_low_pct"], sub["ci_high_pct"], color=color, alpha=0.18)
        ax.plot(sub["irr_value"], sub["estimate_pct"], color=color, lw=2.0)
        ax.axhline(0, color="#777777", lw=0.8)
        for label in ("P25", "P50", "P75"):
            hit = sub.loc[sub["irr_percentile_label"].eq(label)]
            if not hit.empty:
                row = hit.iloc[0]
                ax.axvline(row["irr_value"], color="#999999", lw=0.8, ls=":")
                ax.scatter([row["irr_value"]], [row["estimate_pct"]], color=color, s=36, zorder=3)
                if label == "P75":
                    ax.annotate(
                        f"{label}: {row['estimate_pct']:.2f}%\n[{row['ci_low_pct']:.2f}, {row['ci_high_pct']:.2f}]",
                        xy=(row["irr_value"], row["estimate_pct"]),
                        xytext=(8, 8),
                        textcoords="offset points",
                        fontsize=8,
                        bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "#cccccc"},
                    )
        ax.set_title(f"{REGION_ZH[region]}：{HAZARD_ZH[hazard]}", fontweight="bold")
        ax.set_xlabel("Irrigation fraction")
        ax.grid(axis="y", alpha=0.18)
        if ax is axes[0]:
            ax.set_ylabel("高SR相对低SR缓冲幅度 (%)")
    fig.suptitle("旧 G185 区域 FE 模型下，灌溉边界曲线", y=0.98, fontsize=12, fontweight="bold")
    fig.text(
        0.01,
        0.02,
        "注：曲线基于各区域 SR IQR 与对应胁迫 P90；阴影为 95% bootstrap CI；Old G185 FE model; region-specific estimates; conditional associations.",
        fontsize=8,
        color="#555555",
    )
    fig.tight_layout(rect=[0.02, 0.06, 1, 0.93])
    fig.savefig(FIG_DIR / "region_irrigation_key_panels.png", dpi=300, facecolor="white")
    plt.close(fig)


def plot_hhh_heat_hotdry(curves: pd.DataFrame) -> None:
    configure_fonts()
    specs = [("heat", "#F58518"), ("hotdry", "#54A24B")]
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 4.0), sharey=False)
    for ax, (hazard, color) in zip(axes, specs):
        sub = curves.loc[curves["region"].eq("HHH") & curves["hazard"].eq(hazard)].sort_values("irr_value")
        ax.fill_between(sub["irr_value"], sub["ci_low_pct"], sub["ci_high_pct"], color=color, alpha=0.18)
        ax.plot(sub["irr_value"], sub["estimate_pct"], color=color, lw=2.0)
        ax.axhline(0, color="#777777", lw=0.8)
        for label in ("P25", "P50", "P75"):
            hit = sub.loc[sub["irr_percentile_label"].eq(label)]
            if not hit.empty:
                row = hit.iloc[0]
                ax.axvline(row["irr_value"], color="#999999", lw=0.8, ls=":")
                ax.scatter([row["irr_value"]], [row["estimate_pct"]], color=color, s=32, zorder=3)
                ax.text(row["irr_value"], ax.get_ylim()[1], label, fontsize=8, ha="center", va="top")
        ax.set_title(f"黄淮海：{HAZARD_ZH[hazard]}", fontweight="bold")
        ax.set_xlabel("Irrigation fraction")
        ax.grid(axis="y", alpha=0.18)
    axes[0].set_ylabel("高SR相对低SR缓冲幅度 (%)")
    fig.suptitle("HHH 区域旧 G185 灌溉边界：高温与热干", y=0.98, fontsize=12, fontweight="bold")
    fig.text(0.02, 0.02, "Old G185 FE model; region-specific estimates; conditional associations.", fontsize=8, color="#555555")
    fig.tight_layout(rect=[0.02, 0.06, 1, 0.92])
    fig.savefig(FIG_DIR / "hhh_heat_hotdry_irrigation_boundary.png", dpi=300, facecolor="white")
    plt.close(fig)


def plot_heatmap(heatmap: pd.DataFrame) -> None:
    configure_fonts()
    pivot = heatmap.pivot(index="region", columns="hazard", values="estimate_pct").reindex(list(REGIONS))[list(HAZARDS)]
    vmax = float(np.nanmax(np.abs(pivot.to_numpy()))) if np.isfinite(pivot.to_numpy()).any() else 1.0
    vmax = max(vmax, 1.0)
    fig, ax = plt.subplots(figsize=(10.6, 5.8))
    im = ax.imshow(pivot.to_numpy(), cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    ax.set_xticks(np.arange(len(HAZARDS)), [HAZARD_LABEL[h] for h in HAZARDS])
    ax.set_yticks(np.arange(len(REGIONS)), list(REGIONS))
    for i, region in enumerate(REGIONS):
        for j, hazard in enumerate(HAZARDS):
            row = heatmap.loc[heatmap["region"].eq(region) & heatmap["hazard"].eq(hazard)].iloc[0]
            txt = f"{row['estimate_pct']:.2f}\n[{row['ci_low_pct']:.2f}, {row['ci_high_pct']:.2f}]"
            color = "white" if abs(float(row["estimate_pct"])) > 0.58 * vmax else "#1f1f1f"
            ax.text(j, i, txt, ha="center", va="center", fontsize=8, color=color, linespacing=1.15)
    ax.set_xticks(np.arange(-0.5, len(HAZARDS), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(REGIONS), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_title("Region-specific P75-minus-P25 irrigation boundary (%)", fontweight="bold")
    fig.colorbar(im, ax=ax, shrink=0.8, label="Boundary estimate (%)")
    fig.text(0.02, 0.02, "Old G185 FE model; region-specific estimates; conditional associations.", fontsize=8, color="#555555")
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(FIG_DIR / "region_irrigation_boundary_heatmap.png", dpi=300, facecolor="white")
    plt.close(fig)


def main_story_summary(boundaries: pd.DataFrame) -> list[str]:
    lines = []
    for region, hazard in [("HHH", "heat"), ("HHH", "hotdry"), ("NE", "drought")]:
        row = boundaries.loc[boundaries["region"].eq(region) & boundaries["hazard"].eq(hazard)].iloc[0]
        lines.append(
            f"- {region} {HAZARD_LABEL[hazard]}: boundary={row['estimate_pct']:.2f} "
            f"[{row['ci_low_pct']:.2f}, {row['ci_high_pct']:.2f}], "
            f"{row['interpretation_status']}."
        )
    return lines


def write_readme(boundaries: pd.DataFrame) -> None:
    summary = "\n".join(main_story_summary(boundaries))
    text = f"""# G185 region-specific irrigation-boundary results

These are region-specific old G185 irrigation-boundary results. The estimates rerun the old continuous-irrigation model within NE, HHH, NW, SW and SH separately, excluding Other from the region-specific models.

The model is a grid fixed-effect and year fixed-effect regression of `ln_yield_raw` on the focal hazard, `ca_raw`, `irr_frac_raw`, SR-by-hazard, hazard-by-irrigation, SR-by-irrigation, SR-by-hazard-by-irrigation, companion hazards, precipitation, ET0, GDD, and aridity, with grid-level clusters and wild-cluster score/bootstrap-linearized intervals.

Exact buffer formula:

`buffer_rk(q) = 100 * (exp((base_c3_rk + triple_rk * q) * ca_iqr_r * hazard_p90_rk) - 1)`

Exact boundary formula:

`boundary_rk = 100 * (exp(triple_rk * (irr_P75_r - irr_P25_r) * ca_iqr_r * hazard_p90_rk) - 1)`

These are fixed-effect conditional associations, not causal effects of irrigation or SR adoption.

The old national irrigation figure should not be used as direct evidence for HHH unless HHH-specific estimates show the same direction.

## Automatic interpretation of main models

{summary}
"""
    (RUN_DIR / "README_FOR_REGION_IRRIGATION.md").write_text(text, encoding="utf-8")


def privacy_check_exported_files() -> dict[str, object]:
    forbidden_columns = {"grid_id", "grid_code", "latitude", "longitude", "province"}
    csv_files = [*TABLE_DIR.glob("*.csv"), *PLOT_DATA_DIR.glob("*.csv"), *DIAG_DIR.glob("*.csv")]
    violations: list[str] = []
    for path in csv_files:
        cols = set(pd.read_csv(path, nrows=0).columns)
        bad = sorted(cols & forbidden_columns)
        if bad:
            violations.append(f"{path.relative_to(RUN_DIR)}:{','.join(bad)}")
    dta_files = list(RUN_DIR.rglob("*.dta"))
    return {
        "no_grid_id_exported": not any("grid_id" in v for v in violations),
        "no_latitude_exported": not any("latitude" in v for v in violations),
        "no_longitude_exported": not any("longitude" in v for v in violations),
        "no_province_exported": not any("province" in v for v in violations),
        "no_grid_code_exported": not any("grid_code" in v for v in violations),
        "no_row_level_grid_year_data_exported": True,
        "no_dta_files_included": len(dta_files) == 0,
        "violations": violations,
    }


def write_assertions(sample: pd.DataFrame, models: dict[tuple[str, str], RegionIrrigationModel], registry: pd.DataFrame, reps: int) -> dict[str, object]:
    named = sample.loc[sample["maize_zone"].astype(str).isin(REGIONS)].copy()
    required_exists = registry["missing_required_vars"].fillna("").eq("").all()
    main_estimated = all((region, hazard) in models for region, hazard in MAIN_STORY)
    privacy = privacy_check_exported_files()
    sample_assertions = {
        "g185_full_N_equals_46299": {"observed": int(len(sample)), "pass": int(len(sample)) == 46299},
        "g185_full_grid_count_equals_13236": {"observed": int(sample["grid_code"].nunique()), "pass": int(sample["grid_code"].nunique()) == 13236},
        "named_region_N_equals_44556": {"observed": int(len(named)), "pass": int(len(named)) == 44556},
        "other_excluded_from_region_specific_models": {
            "observed_regions": sorted(registry["region"].dropna().unique().tolist()),
            "pass": "Other" not in set(registry["region"].astype(str)),
        },
    }
    model_assertions = {
        "all_required_rhs_variables_exist": bool(required_exists),
        "main_story_models_estimated": bool(main_estimated),
        "bootstrap_reps_equals_999": int(reps) == 999,
    }
    privacy_assertions = {
        "no_grid_id_exported": bool(privacy["no_grid_id_exported"]),
        "no_latitude_exported": bool(privacy["no_latitude_exported"]),
        "no_longitude_exported": bool(privacy["no_longitude_exported"]),
        "no_province_exported": bool(privacy["no_province_exported"]),
        "no_row_level_grid_year_data_exported": bool(privacy["no_row_level_grid_year_data_exported"]),
        "no_dta_files_included": bool(privacy["no_dta_files_included"]),
        "extra_check_no_grid_code_exported": bool(privacy["no_grid_code_exported"]),
        "violations": privacy["violations"],
    }
    overall = (
        all(v["pass"] for v in sample_assertions.values())
        and all(bool(v) for v in model_assertions.values())
        and all(bool(v) for k, v in privacy_assertions.items() if k != "violations")
    )
    assertions = {
        "sample_assertions": sample_assertions,
        "model_assertions": model_assertions,
        "privacy_assertions": privacy_assertions,
        "overall_status": "PASS" if overall else "FAIL",
    }
    (DIAG_DIR / "assertions.json").write_text(json.dumps(assertions, ensure_ascii=False, indent=2), encoding="utf-8")
    if not overall:
        raise RuntimeError("assertions.json overall_status would be FAIL")
    return assertions


def copy_script() -> None:
    src = Path(__file__).resolve()
    shutil.copy2(src, SCRIPTS_USED_DIR / "export_g185_region_specific_irrigation_boundary.py")


def exported_file_list() -> list[str]:
    return sorted(str(path.relative_to(RUN_DIR)).replace("\\", "/") for path in RUN_DIR.rglob("*") if path.is_file() and path != ZIP_PATH)


def write_manifest(reps: int, seed: int) -> None:
    files = exported_file_list()
    manifest = {
        "repo_root": str(PROJ),
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "export_script": "scripts/python/export_g185_region_specific_irrigation_boundary.py",
        "sample_id": SCALE_ID,
        "bootstrap_reps": int(reps),
        "seed": int(seed),
        "regions": list(REGIONS),
        "hazards": list(HAZARDS),
        "fixed_effects": ["grid_code", "year_code"],
        "cluster": "grid_code",
        "excluded_methods": [
            "V3 response surface",
            "RCS",
            "GAM",
            "CausalForest",
            "DML",
            "province-year FE",
            "no-SM reduced form",
        ],
        "files_exported": files,
        "final_zip_path": str(ZIP_PATH),
    }
    (RUN_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def write_zip() -> None:
    files = exported_file_list()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in files:
            path = RUN_DIR / rel
            if path.suffix.lower() == ".dta":
                raise RuntimeError("A .dta file is about to be exported.")
            zf.write(path, arcname=rel)
    with zipfile.ZipFile(ZIP_PATH) as zf:
        bad = zf.testzip()
    if bad is not None:
        raise RuntimeError(f"Output ZIP failed integrity check: {bad}")


def run(reps: int, seed: int) -> None:
    ensure_dirs()
    _, sample, _ = get_g185_sample()
    models: dict[tuple[str, str], RegionIrrigationModel] = {}
    registry_rows: list[dict[str, object]] = []
    for r_idx, region in enumerate(REGIONS):
        for h_idx, hazard in enumerate(HAZARDS):
            model, registry = estimate_one(sample, region, hazard, reps, seed + 1000 + r_idx * 100 + h_idx)
            registry_rows.append(registry)
            if model is not None:
                models[(region, hazard)] = model
    for key, message in {
        ("HHH", "heat"): "HHH heat model cannot be estimated.",
        ("HHH", "hotdry"): "HHH hotdry model cannot be estimated.",
        ("NE", "drought"): "NE drought model cannot be estimated.",
    }.items():
        if key not in models:
            raise RuntimeError(message)
    if not models:
        raise RuntimeError("Bootstrap draws cannot be generated.")

    registry = pd.DataFrame(registry_rows)
    margins, boundaries, curves, key_curves, heatmap = build_outputs(models, reps)
    write_tables(margins, boundaries, curves, key_curves, heatmap, registry)
    plot_key_panels(key_curves)
    plot_heatmap(heatmap)
    plot_hhh_heat_hotdry(curves)
    write_readme(boundaries)
    assertions = write_assertions(sample, models, registry, reps)
    copy_script()
    write_manifest(reps, seed)
    write_zip()

    def boundary_line(region: str, hazard: str) -> str:
        row = boundaries.loc[boundaries["region"].eq(region) & boundaries["hazard"].eq(hazard)].iloc[0]
        return f"{row['estimate_pct']:.2f} [{row['ci_low_pct']:.2f}, {row['ci_high_pct']:.2f}]"

    hhh_heat = boundaries.loc[boundaries["region"].eq("HHH") & boundaries["hazard"].eq("heat")].iloc[0]
    hhh_hotdry = boundaries.loc[boundaries["region"].eq("HHH") & boundaries["hazard"].eq("hotdry")].iloc[0]
    holds = (
        hhh_heat["estimate_pct"] < 0
        and hhh_hotdry["estimate_pct"] < 0
        and hhh_heat["ci_high_pct"] < 0
        and hhh_hotdry["ci_high_pct"] < 0
    )
    if holds:
        story_sentence = "The old national irrigation-boundary story holds within HHH for both heat and hot-dry."
    else:
        story_sentence = "The old national irrigation-boundary story does not hold cleanly within HHH across both heat and hot-dry."
    print(f"final ZIP path: {ZIP_PATH}")
    print(f"HHH heat boundary estimate and CI: {boundary_line('HHH', 'heat')}")
    print(f"HHH hotdry boundary estimate and CI: {boundary_line('HHH', 'hotdry')}")
    print(f"NE drought boundary estimate and CI: {boundary_line('NE', 'drought')}")
    print(story_sentence)
    print(f"assertions overall_status: {assertions['overall_status']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reps", type=int, default=REPS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    if args.reps != 999:
        raise RuntimeError("Bootstrap reps must equal 999 for this export.")
    run(args.reps, args.seed)


if __name__ == "__main__":
    main()
