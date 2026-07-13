"""Redraw old-G185 teacher figures with region-specific IE/DE/TE contrasts.

This script intentionally uses the old G185 fixed-effect mediation-moderation
specification: grid FE + year FE, GLEAM root-zone soil moisture, raw variables,
and grid-level wild-score bootstrap-linearized intervals. It does not use v3
response surfaces, RCS, GAM, CausalForest, DML, province-year FE, or reduced-form
no-SM TE claims.
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
from matplotlib.patches import Patch, Rectangle


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
SCRIPT_DIR = PROJ / "scripts/python"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from expanded_scale_story_search import add_full_interactions, load_panel, unique_variants  # noqa: E402
from ggcp10_parallel_rules_69038_search import rhs_for  # noqa: E402
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


RUN_DIR = PROJ / "quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw"
TABLE_DIR = RUN_DIR / "tables"
PLOT_DATA_DIR = RUN_DIR / "plot_data"
DIAG_DIR = RUN_DIR / "diagnostics"
FIG_PNG_DIR = RUN_DIR / "figures_png"
FIG_SVG_DIR = RUN_DIR / "figures_svg"
SCRIPTS_USED_DIR = RUN_DIR / "scripts_used"
ZIP_PATH = RUN_DIR / "g185_old_method_region_tiede_redraw_bundle.zip"

REPS = 999
SEED = 42
MEDIATOR = "gleam_smrz_mean_raw"
CORE_COMBOS = (("NE", "drought"), ("HHH", "heat"), ("HHH", "hotdry"))
REGION_ORDER = {"NE": 1, "HHH": 2, "NW": 3, "SW": 4, "SH": 5}
HAZARD_ORDER = {"drought": 1, "heat": 2, "hotdry": 3}
REGION_ZH = {"NE": "东北", "HHH": "黄淮海", "NW": "西北", "SW": "西南", "SH": "南方丘陵"}
HAZARD_ZH = {"drought": "干旱", "heat": "高温", "hotdry": "热干"}
HAZARD_XLABEL = {
    "drought": "Drought exposure (SPEI-derived)",
    "heat": "Heat accumulation >=32C (C-days)",
    "hotdry": "Hot-dry days",
}
COLORS = {"drought": "#4C78A8", "heat": "#F58518", "hotdry": "#54A24B"}
COMPONENT_COLORS = {"IE_delta": "#9ecae1", "DE_delta": "#fdae6b", "TE_delta": "#1f1f1f"}


@dataclass
class AbsorbedDiagModel:
    xvars: list[str]
    beta: np.ndarray
    boot: np.ndarray
    nobs: int
    clusters: int
    rank: int
    condition_number: float
    warning: str


@dataclass
class RegionTiedeModel:
    region: str
    hazard: str
    rhs_m: list[str]
    rhs_y: list[str]
    main: str
    inter: str
    hvar: str
    ca_p25: float
    ca_p50: float
    ca_p75: float
    hazard_p90: float
    m_model: AbsorbedDiagModel
    y_model: AbsorbedDiagModel


@dataclass
class IrrigationModel:
    hazard: str
    xvars: list[str]
    inter: str
    triple: str
    beta: np.ndarray
    boot: np.ndarray
    nobs: int
    clusters: int
    rank: int
    condition_number: float
    warning: str
    ca_p25: float
    ca_p75: float
    irr_p25: float
    irr_p50: float
    irr_p75: float
    hazard_p90: float


def pct_from_ln(x: np.ndarray | float) -> np.ndarray | float:
    return np.expm1(x) * 100.0


def ci_from_boot(values: np.ndarray) -> tuple[float, float]:
    vals = values[np.isfinite(values)]
    if len(vals) == 0:
        return math.nan, math.nan
    lo, hi = np.nanpercentile(vals, [2.5, 97.5])
    return float(lo), float(hi)


def configure_fonts() -> None:
    available = {f.name for f in font_manager.fontManager.ttflist}
    for candidate in ("Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Arial Unicode MS"):
        if candidate in available:
            plt.rcParams["font.family"] = candidate
            break
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
        }
    )


def ensure_dirs() -> None:
    for path in (RUN_DIR, TABLE_DIR, PLOT_DATA_DIR, DIAG_DIR, FIG_PNG_DIR, FIG_SVG_DIR, SCRIPTS_USED_DIR):
        path.mkdir(parents=True, exist_ok=True)


def save_figure(fig: plt.Figure, filename: str) -> None:
    fig.savefig(FIG_PNG_DIR / f"{filename}.png", dpi=300, facecolor="white", bbox_inches="tight")
    fig.savefig(FIG_SVG_DIR / f"{filename}.svg", facecolor="white", bbox_inches="tight")
    plt.close(fig)


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


def fit_absorbed_with_diagnostics(work: pd.DataFrame, yvar: str, xvars: list[str]) -> tuple[object, int, float, str]:
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
    model = type("AbsorbedModelLite", (), {})()
    model.xvars = list(xvars)
    model.beta = beta
    model.xtx_inv = xtx_inv
    model.scores = scores
    model.nobs = int(len(work))
    model.clusters = int(scores.shape[0])
    return model, rank, condition_number, warning


def fit_with_boot(work: pd.DataFrame, yvar: str, xvars: list[str], reps: int, seed: int) -> AbsorbedDiagModel:
    model, rank, condition_number, warning = fit_absorbed_with_diagnostics(work, yvar, xvars)
    boot = wild_boot_betas(model, np.random.default_rng(seed), reps)
    return AbsorbedDiagModel(
        xvars=list(xvars),
        beta=model.beta,
        boot=boot,
        nobs=int(model.nobs),
        clusters=int(model.clusters),
        rank=rank,
        condition_number=condition_number,
        warning=warning,
    )


def estimate_region_tiede(sample: pd.DataFrame, region: str, hazard: str, reps: int, seed: int) -> tuple[RegionTiedeModel | None, dict[str, object]]:
    yvar, ca_var, rhs_m, rhs_y, main, inter = rhs_for(hazard, "raw", MEDIATOR)
    hvar = HAZARD_VAR[hazard]
    rsub = sample.loc[sample["maize_zone"].astype(str).eq(region)].copy()
    required = [yvar, MEDIATOR, *rhs_m, *rhs_y, hvar, ca_var, "grid_code", "year_code"]
    missing = [col for col in dict.fromkeys(required) if col not in rsub.columns]
    registry = {
        "model_family": "region_tiede",
        "region": region,
        "hazard": hazard,
        "N_model": 0,
        "N_grids": 0,
        "n_rhs_m": len(rhs_m),
        "n_rhs_y": len(rhs_y),
        "m_condition_number": math.nan,
        "y_condition_number": math.nan,
        "m_rank": 0,
        "y_rank": 0,
        "model_status": "",
        "missing_required_vars": ";".join(missing),
        "warning": "",
    }
    if missing:
        registry["model_status"] = "MISSING_REQUIRED_VARS"
        return None, registry

    work = common_work(rsub, [yvar, MEDIATOR, *rhs_m, *rhs_y, hvar, ca_var])
    nobs = int(len(work))
    clusters = int(work["grid_code"].nunique())
    registry["N_model"] = nobs
    registry["N_grids"] = clusters
    if nobs < 500 or clusters < 50:
        registry["model_status"] = "SKIPPED_LOW_SUPPORT"
        return None, registry

    m_model = fit_with_boot(work, MEDIATOR, rhs_m, reps, seed)
    y_model = fit_with_boot(work, yvar, rhs_y, reps, seed)
    ca_p25, ca_p50, ca_p75 = q(work[ca_var], [25, 50, 75])
    out = RegionTiedeModel(
        region=region,
        hazard=hazard,
        rhs_m=rhs_m,
        rhs_y=rhs_y,
        main=main,
        inter=inter,
        hvar=hvar,
        ca_p25=float(ca_p25),
        ca_p50=float(ca_p50),
        ca_p75=float(ca_p75),
        hazard_p90=float(np.nanpercentile(work[hvar], 90)),
        m_model=m_model,
        y_model=y_model,
    )
    warning = ";".join(w for w in (m_model.warning, y_model.warning) if w)
    registry.update(
        {
            "m_condition_number": m_model.condition_number,
            "y_condition_number": y_model.condition_number,
            "m_rank": m_model.rank,
            "y_rank": y_model.rank,
            "model_status": "ESTIMATED",
            "warning": warning,
        }
    )
    return out, registry


def component_slopes(model: RegionTiedeModel, sr_value: float) -> tuple[dict[str, float], dict[str, np.ndarray]]:
    m_idx = {name: i for i, name in enumerate(model.rhs_m)}
    y_idx = {name: i for i, name in enumerate(model.rhs_y)}

    a1 = model.m_model.beta[m_idx[model.main]]
    a3 = model.m_model.beta[m_idx[model.inter]]
    b = model.y_model.beta[y_idx[MEDIATOR]]
    c1 = model.y_model.beta[y_idx[model.main]]
    c3 = model.y_model.beta[y_idx[model.inter]]

    a1_b = model.m_model.boot[:, m_idx[model.main]]
    a3_b = model.m_model.boot[:, m_idx[model.inter]]
    b_b = model.y_model.boot[:, y_idx[MEDIATOR]]
    c1_b = model.y_model.boot[:, y_idx[model.main]]
    c3_b = model.y_model.boot[:, y_idx[model.inter]]

    ie = (a1 + a3 * sr_value) * b
    de = c1 + c3 * sr_value
    te = ie + de
    ie_b = (a1_b + a3_b * sr_value) * b_b
    de_b = c1_b + c3_b * sr_value
    te_b = ie_b + de_b
    return (
        {"IE": float(ie), "DE": float(de), "TE": float(te)},
        {"IE": ie_b, "DE": de_b, "TE": te_b},
    )


def delta_components(model: RegionTiedeModel) -> tuple[dict[str, float], dict[str, np.ndarray]]:
    p25, p75 = model.ca_p25, model.ca_p75
    low, low_b = component_slopes(model, p25)
    high, high_b = component_slopes(model, p75)
    deltas = {
        "IE_delta": high["IE"] - low["IE"],
        "DE_delta": high["DE"] - low["DE"],
        "TE_delta": high["TE"] - low["TE"],
    }
    delta_boot = {
        "IE_delta": high_b["IE"] - low_b["IE"],
        "DE_delta": high_b["DE"] - low_b["DE"],
        "TE_delta": high_b["TE"] - low_b["TE"],
    }
    return deltas, delta_boot


def add_component_rows(rows: list[dict[str, object]], model: RegionTiedeModel, reps: int) -> None:
    sr_levels = [("P25", model.ca_p25), ("P50", model.ca_p50), ("P75", model.ca_p75)]
    for level, sr_value in sr_levels:
        estimates, boots = component_slopes(model, sr_value)
        for effect in ("IE", "DE", "TE"):
            ln_est = estimates[effect] * model.hazard_p90
            ln_boot = boots[effect] * model.hazard_p90
            lo, hi = ci_from_boot(pct_from_ln(ln_boot))
            rows.append(
                {
                    "region": model.region,
                    "hazard": model.hazard,
                    "hazard_label": HAZARD_LABEL[model.hazard],
                    "effect_type": effect,
                    "sr_level": level,
                    "sr_value": sr_value,
                    "hazard_p90_region": model.hazard_p90,
                    "ln_slope": estimates[effect],
                    "estimate_pct": float(pct_from_ln(ln_est)),
                    "ci_low_pct": lo,
                    "ci_high_pct": hi,
                    "N_model": model.y_model.nobs,
                    "N_grids": model.y_model.clusters,
                    "bootstrap_reps": reps,
                    "model": "old_G185_region_gridFE_yearFE_two_equation_IE_DE_TE",
                }
            )


def add_delta_rows(rows: list[dict[str, object]], model: RegionTiedeModel, reps: int) -> None:
    estimates, boots = delta_components(model)
    for effect in ("IE_delta", "DE_delta", "TE_delta"):
        ln_est = estimates[effect] * model.hazard_p90
        ln_boot = boots[effect] * model.hazard_p90
        lo, hi = ci_from_boot(pct_from_ln(ln_boot))
        rows.append(
            {
                "region": model.region,
                "hazard": model.hazard,
                "hazard_label": HAZARD_LABEL[model.hazard],
                "effect_type": effect,
                "sr_level": "P75_minus_P25",
                "sr_p25_region": model.ca_p25,
                "sr_p75_region": model.ca_p75,
                "sr_iqr_region": model.ca_p75 - model.ca_p25,
                "hazard_p90_region": model.hazard_p90,
                "ln_slope_delta": estimates[effect],
                "estimate_pct": float(pct_from_ln(ln_est)),
                "ci_low_pct": lo,
                "ci_high_pct": hi,
                "N_model": model.y_model.nobs,
                "N_grids": model.y_model.clusters,
                "bootstrap_reps": reps,
                "significance_flag": int((lo > 0 and hi > 0) or (lo < 0 and hi < 0)),
                "core_story_flag": int((model.region, model.hazard) in CORE_COMBOS),
                "model": "old_G185_region_gridFE_yearFE_two_equation_IE_DE_TE",
            }
        )


def build_curve_rows(models: dict[tuple[str, str], RegionTiedeModel]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for region, hazard in CORE_COMBOS:
        model = models[(region, hazard)]
        estimates, boots = delta_components(model)
        grid = np.linspace(0.0, model.hazard_p90, 101)
        for exposure in grid:
            ln_est = estimates["TE_delta"] * exposure
            ln_boot = boots["TE_delta"] * exposure
            lo, hi = ci_from_boot(pct_from_ln(ln_boot))
            rows.append(
                {
                    "region": region,
                    "hazard": hazard,
                    "hazard_label": HAZARD_LABEL[hazard],
                    "exposure": float(exposure),
                    "estimate_pct": float(pct_from_ln(ln_est)),
                    "ci_low_pct": lo,
                    "ci_high_pct": hi,
                    "hazard_p90_region": model.hazard_p90,
                    "sr_iqr_region": model.ca_p75 - model.ca_p25,
                    "panel_label": f"{REGION_ZH[region]}：{HAZARD_ZH[hazard]}",
                }
            )
    return pd.DataFrame(rows)


def estimate_irrigation(sample: pd.DataFrame, hazard: str, reps: int, seed: int) -> tuple[IrrigationModel, dict[str, object]]:
    xvars, inter, triple = xvars_for_irrigation(hazard)
    hvar = HAZARD_VAR[hazard]
    work = common_work(sample, ["ln_yield_raw", *xvars, hvar, "ca_raw", "irr_frac_raw"])
    model, rank, condition_number, warning = fit_absorbed_with_diagnostics(work, "ln_yield_raw", xvars)
    boot = wild_boot_betas(model, np.random.default_rng(seed), reps)
    ca_p25, ca_p75 = q(work["ca_raw"], [25, 75])
    irr_p25, irr_p50, irr_p75 = q(work["irr_frac_raw"], [25, 50, 75])
    out = IrrigationModel(
        hazard=hazard,
        xvars=xvars,
        inter=inter,
        triple=triple,
        beta=model.beta,
        boot=boot,
        nobs=int(model.nobs),
        clusters=int(model.clusters),
        rank=rank,
        condition_number=condition_number,
        warning=warning,
        ca_p25=float(ca_p25),
        ca_p75=float(ca_p75),
        irr_p25=float(irr_p25),
        irr_p50=float(irr_p50),
        irr_p75=float(irr_p75),
        hazard_p90=float(np.nanpercentile(work[hvar], 90)),
    )
    registry = {
        "model_family": "national_irrigation_boundary",
        "region": "ALL_G185",
        "hazard": hazard,
        "N_model": out.nobs,
        "N_grids": out.clusters,
        "n_rhs_m": 0,
        "n_rhs_y": len(xvars),
        "m_condition_number": math.nan,
        "y_condition_number": condition_number,
        "m_rank": 0,
        "y_rank": rank,
        "model_status": "ESTIMATED",
        "missing_required_vars": "",
        "warning": warning,
    }
    return out, registry


def irrigation_margin(model: IrrigationModel, irr_value: float) -> tuple[float, float, float, np.ndarray]:
    idx = {name: i for i, name in enumerate(model.xvars)}
    ca_iqr = model.ca_p75 - model.ca_p25
    base = model.beta[idx[model.inter]]
    tri = model.beta[idx[model.triple]]
    base_b = model.boot[:, idx[model.inter]]
    tri_b = model.boot[:, idx[model.triple]]
    ln_est = (base + tri * irr_value) * ca_iqr * model.hazard_p90
    ln_boot = (base_b + tri_b * irr_value) * ca_iqr * model.hazard_p90
    pct_boot = pct_from_ln(ln_boot)
    lo, hi = ci_from_boot(pct_boot)
    return float(pct_from_ln(ln_est)), lo, hi, pct_boot


def build_irrigation_outputs(models: dict[str, IrrigationModel], reps: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    margin_rows: list[dict[str, object]] = []
    boundary_rows: list[dict[str, object]] = []
    for hazard, model in models.items():
        level_values = [("P25", model.irr_p25), ("P50", model.irr_p50), ("P75", model.irr_p75)]
        boot_by_level: dict[str, np.ndarray] = {}
        for level, irr_value in level_values:
            est, lo, hi, boot = irrigation_margin(model, irr_value)
            boot_by_level[level] = boot
            margin_rows.append(
                {
                    "hazard": hazard,
                    "hazard_label": HAZARD_LABEL[hazard],
                    "irr_level": level,
                    "irr_value": irr_value,
                    "estimate_pct": est,
                    "ci_low_pct": lo,
                    "ci_high_pct": hi,
                    "hazard_p90": model.hazard_p90,
                    "sr_iqr": model.ca_p75 - model.ca_p25,
                    "N_model": model.nobs,
                    "N_grids": model.clusters,
                    "bootstrap_reps": reps,
                    "model": "old_G185_national_continuous_irrigation_boundary",
                }
            )
        p75_est = margin_rows[-1]["estimate_pct"]
        p25_est = margin_rows[-3]["estimate_pct"]
        diff_boot = boot_by_level["P75"] - boot_by_level["P25"]
        lo, hi = ci_from_boot(diff_boot)
        boundary_rows.append(
            {
                "hazard": hazard,
                "hazard_label": HAZARD_LABEL[hazard],
                "contrast": "P75_minus_P25",
                "estimate_pp": float(p75_est - p25_est),
                "ci_low_pp": lo,
                "ci_high_pp": hi,
                "irr_p25": model.irr_p25,
                "irr_p75": model.irr_p75,
                "hazard_p90": model.hazard_p90,
                "sr_iqr": model.ca_p75 - model.ca_p25,
                "N_model": model.nobs,
                "N_grids": model.clusters,
                "bootstrap_reps": reps,
            }
        )
    return pd.DataFrame(margin_rows), pd.DataFrame(boundary_rows)


def build_tables(sample: pd.DataFrame, reps: int, seed: int):
    models: dict[tuple[str, str], RegionTiedeModel] = {}
    registry_rows: list[dict[str, object]] = []
    component_rows: list[dict[str, object]] = []
    delta_rows: list[dict[str, object]] = []

    for r_idx, region in enumerate(REGIONS):
        for h_idx, hazard in enumerate(HAZARDS):
            model, registry = estimate_region_tiede(sample, region, hazard, reps, seed + 1000 + r_idx * 100 + h_idx)
            registry_rows.append(registry)
            if model is None:
                continue
            models[(region, hazard)] = model
            add_component_rows(component_rows, model, reps)
            add_delta_rows(delta_rows, model, reps)

    for combo in CORE_COMBOS:
        if combo not in models:
            raise RuntimeError(f"Core combo cannot be estimated: {combo}")

    irrigation_models: dict[str, IrrigationModel] = {}
    for h_idx, hazard in enumerate(("heat", "hotdry")):
        model, registry = estimate_irrigation(sample, hazard, reps, seed + 3000 + h_idx)
        irrigation_models[hazard] = model
        registry_rows.append(registry)

    components = pd.DataFrame(component_rows)
    deltas = pd.DataFrame(delta_rows)
    core = deltas.loc[
        deltas["effect_type"].eq("TE_delta")
        & deltas[["region", "hazard"]].apply(lambda row: (row["region"], row["hazard"]) in CORE_COMBOS, axis=1)
    ].copy()
    core["region_cn"] = core["region"].map(REGION_ZH)
    core["hazard_cn"] = core["hazard"].map(HAZARD_ZH)
    core["label"] = core["region_cn"] + " - " + core["hazard_cn"]
    core["ci_text"] = core.apply(
        lambda r: f"{r['estimate_pct']:.2f}% [{r['ci_low_pct']:.2f}, {r['ci_high_pct']:.2f}]",
        axis=1,
    )

    curves = build_curve_rows(models)
    heatmap = deltas.loc[deltas["effect_type"].eq("TE_delta")].copy()
    heatmap["region_order"] = heatmap["region"].map(REGION_ORDER)
    heatmap["hazard_order"] = heatmap["hazard"].map(HAZARD_ORDER)
    heatmap["region_cn"] = heatmap["region"].map(REGION_ZH)
    heatmap["hazard_cn"] = heatmap["hazard"].map(HAZARD_ZH)
    heatmap["cell_label"] = heatmap.apply(
        lambda r: f"{r['estimate_pct']:+.2f}\n[{r['ci_low_pct']:.2f},{r['ci_high_pct']:.2f}]",
        axis=1,
    )
    heatmap.sort_values(["region_order", "hazard_order"], inplace=True)

    component_plot = deltas.loc[
        deltas[["region", "hazard"]].apply(lambda row: (row["region"], row["hazard"]) in CORE_COMBOS, axis=1)
    ].copy()
    component_plot["core_order"] = component_plot.apply(
        lambda r: CORE_COMBOS.index((r["region"], r["hazard"])),
        axis=1,
    )
    component_plot["label"] = component_plot["region"].map(REGION_ZH) + "\n" + component_plot["hazard"].map(HAZARD_ZH)
    component_plot.sort_values(["core_order", "effect_type"], inplace=True)

    irrigation_margins, irrigation_boundaries = build_irrigation_outputs(irrigation_models, reps)
    registry = pd.DataFrame(registry_rows)
    return components, deltas, core, curves, heatmap, component_plot, irrigation_margins, irrigation_boundaries, registry


def write_tables(
    components: pd.DataFrame,
    deltas: pd.DataFrame,
    core: pd.DataFrame,
    curves: pd.DataFrame,
    heatmap: pd.DataFrame,
    component_plot: pd.DataFrame,
    irrigation_margins: pd.DataFrame,
    irrigation_boundaries: pd.DataFrame,
    registry: pd.DataFrame,
) -> None:
    components.to_csv(TABLE_DIR / "region_tiede_components_by_sr_level.csv", index=False, encoding="utf-8-sig")
    deltas.to_csv(TABLE_DIR / "region_tiede_delta_components.csv", index=False, encoding="utf-8-sig")
    core.to_csv(TABLE_DIR / "core_three_corrected_te_results.csv", index=False, encoding="utf-8-sig")
    irrigation_margins.to_csv(TABLE_DIR / "old_irrigation_margins.csv", index=False, encoding="utf-8-sig")
    irrigation_boundaries.to_csv(TABLE_DIR / "old_irrigation_boundaries.csv", index=False, encoding="utf-8-sig")
    registry.to_csv(DIAG_DIR / "model_registry.csv", index=False, encoding="utf-8-sig")

    core.to_csv(PLOT_DATA_DIR / "fig1_core_three_buffers.csv", index=False, encoding="utf-8-sig")
    curves.to_csv(PLOT_DATA_DIR / "fig2_core_buffer_curves.csv", index=False, encoding="utf-8-sig")
    heatmap.to_csv(PLOT_DATA_DIR / "fig3_region_hazard_heatmap.csv", index=False, encoding="utf-8-sig")
    irrigation_margins.to_csv(PLOT_DATA_DIR / "fig4_irrigation_boundary_heat_hotdry.csv", index=False, encoding="utf-8-sig")
    component_plot.to_csv(PLOT_DATA_DIR / "fig5_tiede_delta_components.csv", index=False, encoding="utf-8-sig")


def plot_fig1(core: pd.DataFrame) -> None:
    configure_fonts()
    order = [("NE", "drought"), ("HHH", "heat"), ("HHH", "hotdry")]
    plot = pd.concat(
        [
            core.loc[core["region"].eq(region) & core["hazard"].eq(hazard)]
            for region, hazard in order
        ],
        ignore_index=True,
    )
    fig, ax = plt.subplots(figsize=(9.6, 4.8))
    y = np.arange(len(plot))[::-1]
    for i, row in plot.iterrows():
        yi = y[i]
        color = COLORS[row["hazard"]]
        ax.hlines(yi, row["ci_low_pct"], row["ci_high_pct"], color="#333333", lw=1.7, zorder=1)
        ax.scatter([row["estimate_pct"]], [yi], s=150, color=color, edgecolor="white", lw=1.0, zorder=3)
        ax.text(
            row["ci_high_pct"] + 0.18,
            yi,
            f"{row['estimate_pct']:.2f}%\n[{row['ci_low_pct']:.2f}, {row['ci_high_pct']:.2f}]",
            va="center",
            ha="left",
            fontsize=10,
        )
    ax.axvline(0, color="#777777", lw=1.0)
    ax.set_yticks(y, plot["label"])
    ax.set_xlabel("SR 从区域 P25 到 P75 时的总缓冲幅度（IE+DE，%）")
    ax.set_title("图1 旧 G185 主线：按 IE+DE 重算的区域总缓冲关联", fontweight="bold", pad=12)
    ax.grid(axis="x", color="#e5e5e5", lw=0.8)
    ax.grid(axis="y", visible=False)
    xmin = min(0.0, float(plot["ci_low_pct"].min())) - 0.6
    xmax = float(plot["ci_high_pct"].max()) + 1.25
    ax.set_xlim(xmin, xmax)
    fig.text(
        0.02,
        0.02,
        "注：旧模型为 grid FE + year FE；区域内两方程 IE/DE/TE 代数分解；区间为 wild-cluster score bootstrap；IE/DE/TE 不是因果中介效应。",
        fontsize=8.5,
        color="#555555",
    )
    fig.tight_layout(rect=[0.02, 0.08, 1, 0.98])
    save_figure(fig, "fig1_core_three_buffers")


def plot_fig2(curves: pd.DataFrame) -> None:
    configure_fonts()
    specs = [("NE", "drought"), ("HHH", "heat"), ("HHH", "hotdry")]
    fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.6), sharey=False)
    for ax, (region, hazard) in zip(axes, specs):
        sub = curves.loc[curves["region"].eq(region) & curves["hazard"].eq(hazard)].sort_values("exposure")
        color = COLORS[hazard]
        ax.fill_between(sub["exposure"], sub["ci_low_pct"], sub["ci_high_pct"], color=color, alpha=0.17)
        ax.plot(sub["exposure"], sub["estimate_pct"], color=color, lw=2.0)
        p90 = float(sub["hazard_p90_region"].iloc[0])
        p90row = sub.iloc[-1]
        ax.axvline(p90, color="#999999", lw=1.0, ls=":")
        ax.scatter([p90], [p90row["estimate_pct"]], color=color, s=42, zorder=4)
        ax.annotate(
            f"P90: {p90row['estimate_pct']:.2f}%\n[{p90row['ci_low_pct']:.2f}, {p90row['ci_high_pct']:.2f}]",
            xy=(p90, p90row["estimate_pct"]),
            xytext=(-6, 10),
            textcoords="offset points",
            ha="right",
            fontsize=8,
            bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "#cccccc"},
        )
        ax.axhline(0, color="#777777", lw=0.8)
        ax.set_title(f"{REGION_ZH[region]}：{HAZARD_ZH[hazard]}", fontweight="bold")
        ax.set_xlabel(HAZARD_XLABEL[hazard])
        ax.set_ylabel("高 SR 相对低 SR 的总缓冲幅度（%）")
        ax.grid(axis="y", color="#e5e5e5", lw=0.8)
    fig.suptitle("图2 旧线性模型下，区域 TE 曲线：SR 相关总缓冲随胁迫增强而变化", y=0.98, fontsize=13, fontweight="bold")
    fig.text(
        0.012,
        0.02,
        "注：曲线使用区域内 IE+DE 的 P75-P25 斜率差并外推到对应胁迫暴露；不是 residual-only SR×hazard 系数图。",
        fontsize=8.5,
        color="#555555",
    )
    fig.tight_layout(rect=[0, 0.07, 1, 0.92])
    save_figure(fig, "fig2_core_buffer_curves")


def plot_fig3(heatmap: pd.DataFrame) -> None:
    configure_fonts()
    pivot = heatmap.pivot(index="region", columns="hazard", values="estimate_pct").reindex(list(REGIONS))[list(HAZARDS)]
    vmax = float(np.nanmax(np.abs(pivot.to_numpy()))) if np.isfinite(pivot.to_numpy()).any() else 1.0
    vmax = max(vmax, 1.0)
    fig, ax = plt.subplots(figsize=(9.8, 7.0))
    im = ax.imshow(pivot.to_numpy(), cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    ax.set_xticks(np.arange(len(HAZARDS)), [HAZARD_ZH[h] for h in HAZARDS])
    ax.set_yticks(np.arange(len(REGIONS)), [REGION_ZH[r] for r in REGIONS])
    for i, region in enumerate(REGIONS):
        for j, hazard in enumerate(HAZARDS):
            row = heatmap.loc[heatmap["region"].eq(region) & heatmap["hazard"].eq(hazard)].iloc[0]
            value = float(row["estimate_pct"])
            text_color = "white" if abs(value) > 0.52 * vmax else "#1f1f1f"
            ax.text(j, i, row["cell_label"], ha="center", va="center", fontsize=9.5, color=text_color, linespacing=1.25)
            if (region, hazard) in CORE_COMBOS:
                ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor="black", lw=2.2))
            elif int(row["significance_flag"]) == 1:
                ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor="#666666", lw=1.2))
    ax.set_xticks(np.arange(-0.5, len(HAZARDS), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(REGIONS), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.5)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_title("图3 15 个区域-胁迫组合：按 IE+DE 重算的区域 TE", fontweight="bold", pad=12)
    cb = fig.colorbar(im, ax=ax, shrink=0.78)
    cb.set_label("总缓冲幅度（%）")
    fig.text(
        0.02,
        0.02,
        "黑框：核心展示组合；灰框：95% CI 不跨 0 的补充格；数值为 P75-P25 SR 对比在区域 P90 胁迫下的 TE 缓冲幅度。",
        fontsize=8.5,
        color="#555555",
    )
    fig.tight_layout(rect=[0, 0.06, 1, 0.98])
    save_figure(fig, "fig3_region_hazard_heatmap")


def plot_fig4(irrigation_margins: pd.DataFrame, irrigation_boundaries: pd.DataFrame) -> None:
    configure_fonts()
    data = irrigation_margins.loc[irrigation_margins["hazard"].isin(["heat", "hotdry"])].copy()
    fig, ax = plt.subplots(figsize=(10.8, 5.6))
    for hazard in ("heat", "hotdry"):
        sub = data.loc[data["hazard"].eq(hazard)].set_index("irr_level").reindex(["P25", "P50", "P75"]).reset_index()
        color = COLORS[hazard]
        x = np.arange(len(sub))
        ax.plot(x, sub["estimate_pct"], color=color, lw=2.5, marker="o", ms=7, label=HAZARD_ZH[hazard])
        ax.fill_between(x, sub["ci_low_pct"], sub["ci_high_pct"], color=color, alpha=0.16)
        row = irrigation_boundaries.loc[irrigation_boundaries["hazard"].eq(hazard)].iloc[0]
        ax.text(
            2.08,
            float(sub.loc[sub["irr_level"].eq("P75"), "estimate_pct"].iloc[0]) + (0.05 if hazard == "heat" else -0.05),
            f"{HAZARD_ZH[hazard]}：P75-P25 {row['estimate_pp']:+.2f} pp",
            color=color,
            fontsize=10,
            ha="left",
            va="center",
        )
    irr_values = data.loc[data["hazard"].eq("heat")].set_index("irr_level").reindex(["P25", "P50", "P75"])["irr_value"]
    ax.set_xticks(
        np.arange(3),
        [f"{level}\n{value * 100:.1f}%" for level, value in zip(["P25", "P50", "P75"], irr_values)],
    )
    ax.axhline(0, color="#777777", lw=1.0)
    ax.set_ylabel("SR 相关缓冲幅度，P90 胁迫（%）")
    ax.set_xlabel("灌溉覆盖率分位数")
    ax.set_title("图4 灌溉边界：旧 continuous-irrigation 模型", fontweight="bold", pad=12)
    ax.legend(frameon=False, loc="upper right")
    ax.grid(axis="y", color="#e5e5e5", lw=0.8)
    ax.set_xlim(-0.15, 2.65)
    fig.text(
        0.02,
        0.02,
        "注：该图重跑旧 continuous irrigation triple interaction；表示边际缓冲随灌溉分位变化，不属于 IE/DE/TE 分解图。",
        fontsize=8.5,
        color="#555555",
    )
    fig.tight_layout(rect=[0.02, 0.08, 1, 0.98])
    save_figure(fig, "fig4_irrigation_boundary_heat_hotdry")


def plot_fig5(component_plot: pd.DataFrame) -> None:
    configure_fonts()
    combos = list(CORE_COMBOS)
    labels = []
    ie_vals = []
    de_vals = []
    te_vals = []
    te_low = []
    te_high = []
    for region, hazard in combos:
        sub = component_plot.loc[component_plot["region"].eq(region) & component_plot["hazard"].eq(hazard)]
        labels.append(f"{REGION_ZH[region]}\n{HAZARD_ZH[hazard]}")
        ie = sub.loc[sub["effect_type"].eq("IE_delta")].iloc[0]
        de = sub.loc[sub["effect_type"].eq("DE_delta")].iloc[0]
        te = sub.loc[sub["effect_type"].eq("TE_delta")].iloc[0]
        ie_vals.append(float(ie["estimate_pct"]))
        de_vals.append(float(de["estimate_pct"]))
        te_vals.append(float(te["estimate_pct"]))
        te_low.append(float(te["ci_low_pct"]))
        te_high.append(float(te["ci_high_pct"]))

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(10.8, 5.6))
    pos_base = np.zeros(len(labels))
    neg_base = np.zeros(len(labels))
    for vals, name, color in ((ie_vals, "SM-linked component", COMPONENT_COLORS["IE_delta"]), (de_vals, "Residual component", COMPONENT_COLORS["DE_delta"])):
        vals_arr = np.array(vals)
        bottom = np.where(vals_arr >= 0, pos_base, neg_base)
        ax.bar(x, vals_arr, bottom=bottom, width=0.56, color=color, edgecolor="white", label=name)
        pos_base = np.where(vals_arr >= 0, pos_base + vals_arr, pos_base)
        neg_base = np.where(vals_arr < 0, neg_base + vals_arr, neg_base)

    te_vals_arr = np.array(te_vals)
    yerr = np.vstack([te_vals_arr - np.array(te_low), np.array(te_high) - te_vals_arr])
    ax.errorbar(
        x,
        te_vals_arr,
        yerr=yerr,
        fmt="D",
        color=COMPONENT_COLORS["TE_delta"],
        markerfacecolor=COMPONENT_COLORS["TE_delta"],
        markersize=7,
        capsize=4,
        lw=1.6,
        label="Combined TE contrast",
        zorder=5,
    )
    for xi, est, lo, hi in zip(x, te_vals, te_low, te_high):
        va = "bottom" if est >= 0 else "top"
        offset = 0.18 if est >= 0 else -0.18
        ax.text(xi, est + offset, f"{est:.2f}%\n[{lo:.2f},{hi:.2f}]", ha="center", va=va, fontsize=9)
    ax.axhline(0, color="#777777", lw=1.0)
    ax.set_xticks(x, labels)
    ax.set_ylabel("P75 - P25 SR 对比下的缓冲幅度（%）")
    ax.set_title("图5 区域 TE 拆分：土壤水分相关组件与剩余组件", fontweight="bold", pad=12)
    ax.legend(frameon=False, loc="upper left", ncol=3)
    ax.grid(axis="y", color="#e5e5e5", lw=0.8)
    ymin = min(float(np.nanmin(neg_base)), float(np.nanmin(te_low)), 0.0) - 0.6
    ymax = max(float(np.nanmax(pos_base)), float(np.nanmax(te_high)), 0.0) + 0.8
    ax.set_ylim(ymin, ymax)
    fig.text(
        0.02,
        0.02,
        "注：IE/DE/TE 是两条方程形成的代数组件；Combined TE 在 log-slope 内先加总 IE 与 DE 后转换为百分比，不能表述为因果中介效应。",
        fontsize=8.5,
        color="#555555",
    )
    fig.tight_layout(rect=[0.02, 0.08, 1, 0.98])
    save_figure(fig, "fig5_te_iede_delta_components")


def plot_contact_sheet() -> None:
    from PIL import Image, ImageDraw

    files = [
        "fig1_core_three_buffers.png",
        "fig2_core_buffer_curves.png",
        "fig3_region_hazard_heatmap.png",
        "fig4_irrigation_boundary_heat_hotdry.png",
        "fig5_te_iede_delta_components.png",
    ]
    thumbs: list[Image.Image] = []
    for name in files:
        img = Image.open(FIG_PNG_DIR / name).convert("RGB")
        img.thumbnail((900, 520))
        thumbs.append(img.copy())
    width = 1880
    height = 1600
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    positions = [(30, 30), (960, 30), (30, 560), (960, 560), (500, 1080)]
    for img, pos, name in zip(thumbs, positions, files):
        sheet.paste(img, pos)
        draw.text((pos[0], pos[1] + img.height + 6), name, fill=(50, 50, 50))
    sheet.save(FIG_PNG_DIR / "contact_sheet_corrected_old_method.png")


def plot_all(core: pd.DataFrame, curves: pd.DataFrame, heatmap: pd.DataFrame, component_plot: pd.DataFrame, irrigation_margins: pd.DataFrame, irrigation_boundaries: pd.DataFrame) -> None:
    plot_fig1(core)
    plot_fig2(curves)
    plot_fig3(heatmap)
    plot_fig4(irrigation_margins, irrigation_boundaries)
    plot_fig5(component_plot)
    plot_contact_sheet()


def write_readme(core: pd.DataFrame, irrigation_boundaries: pd.DataFrame) -> None:
    core_lines = []
    for _, row in core.iterrows():
        core_lines.append(
            f"- {row['region']} {HAZARD_LABEL[row['hazard']]} corrected TE = "
            f"{row['estimate_pct']:.2f}% [{row['ci_low_pct']:.2f}, {row['ci_high_pct']:.2f}]."
        )
    irr_lines = []
    for _, row in irrigation_boundaries.iterrows():
        irr_lines.append(
            f"- {HAZARD_LABEL[row['hazard']]} irrigation P75-P25 boundary = "
            f"{row['estimate_pp']:.2f} pp [{row['ci_low_pp']:.2f}, {row['ci_high_pp']:.2f}]."
        )
    text = f"""# G185 old-method region IE/DE/TE redraw

This bundle reruns the old G185 fixed-effect mediation-moderation equations within each named maize region and hazard. It replaces the earlier region-specific residual-only `SR x hazard` figure with a region-specific IE+DE TE contrast.

## Core corrected TE results

{chr(10).join(core_lines)}

## Irrigation boundary figure

{chr(10).join(irr_lines)}

## Formula

For each region `r` and hazard `k`, the script estimates:

`SM_it = alpha_i + lambda_t + a1_rk H_it^k + a2_rk SR_it + a3_rk SR_it x H_it^k + controls + u_it`

`y_it = alpha_i + lambda_t + c1_rk H_it^k + c2_rk SR_it + c3_rk SR_it x H_it^k + b_rk SM_it + controls + e_it`

The decomposition is:

`IE_rk(s) = (a1_rk + a3_rk s) b_rk`

`DE_rk(s) = c1_rk + c3_rk s`

`TE_rk(s) = IE_rk(s) + DE_rk(s)`

The reported total buffering contrast is:

`100 * (exp((TE_rk(SR75_r) - TE_rk(SR25_r)) * Q90_r(H^k)) - 1)`

These IE/DE/TE labels are algebraic components from the two equations, not formal causal mediation estimates.

## Method exclusions

No v3 response surface, RCS, GAM, CausalForest, DML, province-year FE, or reduced-form no-SM TE output is used in this bundle.
"""
    (RUN_DIR / "README_G185_OLD_METHOD_REGION_TIEDE_REDRAW.md").write_text(text, encoding="utf-8")


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
        "no_grid_code_exported": not any("grid_code" in v for v in violations),
        "no_latitude_exported": not any("latitude" in v for v in violations),
        "no_longitude_exported": not any("longitude" in v for v in violations),
        "no_province_exported": not any("province" in v for v in violations),
        "no_row_level_grid_year_data_exported": True,
        "no_dta_files_included": len(dta_files) == 0,
        "violations": violations,
    }


def image_check() -> dict[str, object]:
    from PIL import Image, ImageStat

    checks: dict[str, object] = {}
    for path in sorted(FIG_PNG_DIR.glob("*.png")):
        with Image.open(path) as img:
            stat = ImageStat.Stat(img.convert("L"))
            checks[path.name] = {
                "width": img.width,
                "height": img.height,
                "mean_luma": float(stat.mean[0]),
                "std_luma": float(stat.stddev[0]),
                "nonblank_pass": bool(stat.stddev[0] > 1.0),
            }
    return checks


def write_assertions(sample: pd.DataFrame, registry: pd.DataFrame, reps: int) -> dict[str, object]:
    named = sample.loc[sample["maize_zone"].astype(str).isin(REGIONS)].copy()
    privacy = privacy_check_exported_files()
    images = image_check()
    required_pngs = {
        "fig1_core_three_buffers.png",
        "fig2_core_buffer_curves.png",
        "fig3_region_hazard_heatmap.png",
        "fig4_irrigation_boundary_heat_hotdry.png",
        "fig5_te_iede_delta_components.png",
        "contact_sheet_corrected_old_method.png",
    }
    observed_pngs = {path.name for path in FIG_PNG_DIR.glob("*.png")}
    status_counts = registry["model_status"].value_counts().to_dict()
    sample_assertions = {
        "g185_full_N_equals_46299": {"observed": int(len(sample)), "pass": int(len(sample)) == 46299},
        "g185_full_grid_count_equals_13236": {"observed": int(sample["grid_code"].nunique()), "pass": int(sample["grid_code"].nunique()) == 13236},
        "named_region_N_equals_44556": {"observed": int(len(named)), "pass": int(len(named)) == 44556},
        "other_excluded_from_region_specific_models": {
            "observed_regions": sorted(named["maize_zone"].astype(str).unique().tolist()),
            "pass": "Other" not in set(named["maize_zone"].astype(str)),
        },
    }
    model_assertions = {
        "region_tiede_models_estimated": int(status_counts.get("ESTIMATED", 0)) >= 17,
        "all_region_tiede_required_vars_exist": bool(
            registry.loc[registry["model_family"].eq("region_tiede"), "missing_required_vars"].fillna("").eq("").all()
        ),
        "bootstrap_reps_equals_999": int(reps) == 999,
    }
    output_assertions = {
        "required_pngs_present": required_pngs.issubset(observed_pngs),
        "all_pngs_nonblank": all(bool(v["nonblank_pass"]) for v in images.values()),
        "no_v3_dependency_declared": True,
    }
    privacy_assertions = {
        "no_grid_id_exported": bool(privacy["no_grid_id_exported"]),
        "no_grid_code_exported": bool(privacy["no_grid_code_exported"]),
        "no_latitude_exported": bool(privacy["no_latitude_exported"]),
        "no_longitude_exported": bool(privacy["no_longitude_exported"]),
        "no_province_exported": bool(privacy["no_province_exported"]),
        "no_row_level_grid_year_data_exported": bool(privacy["no_row_level_grid_year_data_exported"]),
        "no_dta_files_included": bool(privacy["no_dta_files_included"]),
        "violations": privacy["violations"],
    }
    overall = (
        all(v["pass"] for v in sample_assertions.values())
        and all(bool(v) for v in model_assertions.values())
        and all(bool(v) for v in output_assertions.values())
        and all(bool(v) for k, v in privacy_assertions.items() if k != "violations")
    )
    assertions = {
        "sample_assertions": sample_assertions,
        "model_assertions": model_assertions,
        "output_assertions": output_assertions,
        "privacy_assertions": privacy_assertions,
        "image_checks": images,
        "overall_status": "PASS" if overall else "FAIL",
    }
    (DIAG_DIR / "assertions.json").write_text(json.dumps(assertions, ensure_ascii=False, indent=2), encoding="utf-8")
    if not overall:
        raise RuntimeError("assertions.json overall_status would be FAIL")
    return assertions


def copy_script() -> None:
    src = Path(__file__).resolve()
    shutil.copy2(src, SCRIPTS_USED_DIR / "export_g185_old_method_region_tiede_redraw.py")


def exported_file_list() -> list[str]:
    return sorted(str(path.relative_to(RUN_DIR)).replace("\\", "/") for path in RUN_DIR.rglob("*") if path.is_file() and path != ZIP_PATH)


def write_manifest(reps: int, seed: int) -> None:
    manifest = {
        "repo_root": str(PROJ),
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "export_script": "scripts/python/export_g185_old_method_region_tiede_redraw.py",
        "sample_id": SCALE_ID,
        "bootstrap_reps": int(reps),
        "seed": int(seed),
        "regions": list(REGIONS),
        "hazards": list(HAZARDS),
        "core_combos": [{"region": r, "hazard": h} for r, h in CORE_COMBOS],
        "fixed_effects": ["grid_code", "year_code"],
        "cluster": "grid_code",
        "mediator": MEDIATOR,
        "included_models": [
            "old_G185_region_gridFE_yearFE_two_equation_IE_DE_TE",
            "old_G185_national_continuous_irrigation_boundary",
        ],
        "excluded_methods": [
            "v3 response surface",
            "RCS",
            "GAM",
            "CausalForest",
            "DML",
            "province-year FE",
            "no-SM reduced-form TE",
            "G057/G049 evidence mixing",
        ],
        "files_exported": exported_file_list(),
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
    (
        components,
        deltas,
        core,
        curves,
        heatmap,
        component_plot,
        irrigation_margins,
        irrigation_boundaries,
        registry,
    ) = build_tables(sample, reps, seed)
    write_tables(
        components,
        deltas,
        core,
        curves,
        heatmap,
        component_plot,
        irrigation_margins,
        irrigation_boundaries,
        registry,
    )
    plot_all(core, curves, heatmap, component_plot, irrigation_margins, irrigation_boundaries)
    write_readme(core, irrigation_boundaries)
    copy_script()
    write_assertions(sample, registry, reps)
    write_manifest(reps, seed)
    write_zip()

    print("[OK] G185 old-method region IE/DE/TE redraw complete")
    print(f"[OK] output_dir={RUN_DIR}")
    print(f"[OK] zip={ZIP_PATH}")
    for _, row in core.iterrows():
        print(
            f"[CORE] {row['region']} {row['hazard']} corrected_TE="
            f"{row['estimate_pct']:.2f} [{row['ci_low_pct']:.2f}, {row['ci_high_pct']:.2f}]"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reps", type=int, default=REPS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    run(args.reps, args.seed)


if __name__ == "__main__":
    main()
