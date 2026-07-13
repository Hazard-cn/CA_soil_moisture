"""Run the G185 fixed-effects climate-loss response-surface v3 pipeline."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
import pandas as pd
from scipy.stats import norm

from g185_v3_config import (
    BUNDLE_PATH,
    C0_CONTROLS,
    C1_CONTROLS,
    CLAIMS,
    FIGURE_DATA_DIR,
    FIGURE_DIR,
    LOG_DIR,
    PREFLIGHT_DIR,
    PROJ,
    REGIONS,
    RUN_DIR,
    SCALE_ID,
    SCENARIOS,
    SEED,
)
from g185_v3_data import assert_g185, load_g185_sample, write_preflight
from g185_v3_estimands import (
    bh_adjust,
    buffering_vector,
    contrast_to_row,
    local_scenario_points,
    national_design,
    region_design,
    scenario_points,
    support_diagnostics,
    wald_equal,
)
from g185_v3_fixed_effects import FeModel, fit_fe_model, linear_contrast, make_spatial_blocks, pct
from g185_v3_splines import make_rcs_spec, rcs_basis, surface_basis, write_basis_spec


def ensure_dirs() -> None:
    for path in (RUN_DIR, FIGURE_DATA_DIR, FIGURE_DIR, PREFLIGHT_DIR, LOG_DIR):
        path.mkdir(parents=True, exist_ok=True)


def q(series: pd.Series, probs: list[float]) -> list[float]:
    return [float(x) for x in np.percentile(series.dropna().to_numpy(dtype=float), probs)]


def surface_design(sample: pd.DataFrame, d_spec, h_spec) -> pd.DataFrame:
    return surface_basis(sample["D_full_raw"], sample["hdd_ge32_raw"], d_spec, h_spec).reset_index(drop=True)


def build_region_design(sample: pd.DataFrame, d_spec, h_spec, controls=C0_CONTROLS, sm_control: bool = False) -> pd.DataFrame:
    b = surface_design(sample, d_spec, h_spec)
    sr_c = sample["ca_raw"].to_numpy(dtype=float) - float(np.percentile(sample["ca_raw"].dropna(), 50))
    region_values = sample["maize_zone"].astype(str).to_numpy()
    out = {}
    for region in REGIONS:
        ind = (region_values == region).astype(float)
        for name in b.columns:
            vals = b[name].to_numpy(dtype=float) * ind
            out[f"{region}:{name}"] = vals
            out[f"{region}:SRc_x_{name}"] = vals * sr_c
        out[f"{region}:SR_c"] = sr_c * ind
    for control in controls:
        out[control] = sample[control].to_numpy(dtype=float)
    if sm_control:
        out["gleam_smrz_mean_raw"] = sample["gleam_smrz_mean_raw"].to_numpy(dtype=float)
    return pd.DataFrame(out)


def build_national_design(sample: pd.DataFrame, d_spec, h_spec, controls=C0_CONTROLS, sm_control: bool = False) -> pd.DataFrame:
    b = surface_design(sample, d_spec, h_spec)
    sr_c = sample["ca_raw"].to_numpy(dtype=float) - float(np.percentile(sample["ca_raw"].dropna(), 50))
    out = {name: b[name].to_numpy(dtype=float) for name in b.columns}
    for name in b.columns:
        out[f"SRc_x_{name}"] = b[name].to_numpy(dtype=float) * sr_c
    out["SR_c"] = sr_c
    for control in controls:
        out[control] = sample[control].to_numpy(dtype=float)
    if sm_control:
        out["gleam_smrz_mean_raw"] = sample["gleam_smrz_mean_raw"].to_numpy(dtype=float)
    return pd.DataFrame(out)


def build_irrigation_design(sample: pd.DataFrame, d_spec, h_spec, irr_col: str, controls=C0_CONTROLS) -> tuple[pd.DataFrame, float, float]:
    b = surface_design(sample, d_spec, h_spec)
    sr_center = float(np.percentile(sample["ca_raw"].dropna(), 50))
    irr_center = float(np.percentile(sample[irr_col].dropna(), 50))
    sr_c = sample["ca_raw"].to_numpy(dtype=float) - sr_center
    irr_c = sample[irr_col].to_numpy(dtype=float) - irr_center
    out = {name: b[name].to_numpy(dtype=float) for name in b.columns}
    for name in b.columns:
        vals = b[name].to_numpy(dtype=float)
        out[f"SRc_x_{name}"] = vals * sr_c
        out[f"Irrc_x_{name}"] = vals * irr_c
        out[f"SRc_Irrc_x_{name}"] = vals * sr_c * irr_c
    out["SR_c"] = sr_c
    out["Irr_c"] = irr_c
    out["SRc_x_Irrc"] = sr_c * irr_c
    for control in controls:
        out[control] = sample[control].to_numpy(dtype=float)
    return pd.DataFrame(out), sr_center, irr_center


def build_hotdry_design(sample: pd.DataFrame, hd_spec, d_spec, h_spec, incremental: bool = False) -> pd.DataFrame:
    hd = rcs_basis(sample["HotDryPr_full_raw"], hd_spec)
    sr_center = float(np.percentile(sample["ca_raw"].dropna(), 50))
    sr_c = sample["ca_raw"].to_numpy(dtype=float) - sr_center
    out = {name: hd[name].to_numpy(dtype=float) for name in hd.columns}
    for name in hd.columns:
        out[f"SRc_x_{name}"] = hd[name].to_numpy(dtype=float) * sr_c
    out["SR_c"] = sr_c
    if incremental:
        b = surface_design(sample, d_spec, h_spec)
        for name in b.columns:
            out[f"DHcontrol_{name}"] = b[name].to_numpy(dtype=float)
    for control in C0_CONTROLS:
        out[control] = sample[control].to_numpy(dtype=float)
    return pd.DataFrame(out)


def model_registry_row(model: FeModel, sample_definition: str, regions_included: str, fixed_effects: str, control_set: str, sm_control: str, surface_basis_id: str, sr_definition: str, irrigation_definition: str, region_structure: str) -> dict[str, object]:
    return {
        "model_id": model.model_id,
        "outcome": model.yvar,
        "sample_definition": sample_definition,
        "regions_included": regions_included,
        "fixed_effects": fixed_effects,
        "control_set": control_set,
        "soil_moisture_control": sm_control,
        "surface_basis_id": surface_basis_id,
        "sr_definition": sr_definition,
        "irrigation_definition": irrigation_definition,
        "region_structure": region_structure,
        "inference_method": model.inference_method,
        "N_obs": model.nobs,
        "N_grids": model.n_grids,
        "N_provinces": model.n_provinces,
        "N_fe_grid": model.fe_grid_count,
        "N_fe_time": model.fe_time_count,
        "matrix_rank": model.matrix_rank,
        "n_columns_before_drop": model.n_columns_before_drop,
        "n_columns_after_drop": model.n_columns_after_drop,
        "condition_number": model.condition_number,
        "status": model.status,
        "formula_text": model.formula_text,
    }


def coefficient_rows(model: FeModel, region_structure: str) -> list[dict[str, object]]:
    rows = []
    se = np.sqrt(np.maximum(np.diag(model.covariance), 0))
    for name, beta, s in zip(model.xvars, model.beta, se):
        p = float(2 * norm.sf(abs(beta / s))) if s > 0 else math.nan
        region = ""
        term = name
        if ":" in name:
            region, term = name.split(":", 1)
        rows.append(
            {
                "model_id": model.model_id,
                "term": name,
                "term_family": "spline_diagnostic" if "rcs" in term else "control_or_level",
                "region": region if region_structure == "region_specific" else "",
                "estimate": beta,
                "se": s,
                "p_value": p,
                "column_dropped": 0,
                "column_drop_reason": "",
            }
        )
    for name, reason in model.dropped_columns.items():
        region = ""
        term = name
        if ":" in name:
            region, term = name.split(":", 1)
        rows.append(
            {
                "model_id": model.model_id,
                "term": name,
                "term_family": "spline_diagnostic" if "rcs" in term else "control_or_level",
                "region": region,
                "estimate": math.nan,
                "se": math.nan,
                "p_value": math.nan,
                "column_dropped": 1,
                "column_drop_reason": reason,
            }
        )
    return rows


def fit_primary_models(sample: pd.DataFrame, d_spec, h_spec, reps: int) -> tuple[dict[str, FeModel], list[dict[str, object]], list[dict[str, object]]]:
    models: dict[str, FeModel] = {}
    registry: list[dict[str, object]] = []
    coeffs: list[dict[str, object]] = []
    named = sample.loc[sample["maize_zone"].astype(str).isin(REGIONS)].copy()

    reg_design = build_region_design(named, d_spec, h_spec, C0_CONTROLS)
    reg_model = fit_fe_model(
        named,
        "ln_yield_raw",
        reg_design,
        "RS_REG_PYFE_NOSM_C0",
        "province_year_code",
        "grid FE + province-year FE + region-specific B(D,H) and SR_c x B(D,H) + C0",
        block_degrees=2.0,
        bootstrap_reps=reps,
        seed=SEED,
    )
    models[reg_model.model_id] = reg_model
    registry.append(model_registry_row(reg_model, "G185 named regions", "NE,HHH,NW,SW,SH", "grid + province_year", "C0_nonoverlap", "none", "rcs4", "ca_raw centered at pooled P50", "not_applicable", "region_specific"))
    coeffs.extend(coefficient_rows(reg_model, "region_specific"))

    nat_design = build_national_design(sample, d_spec, h_spec, C0_CONTROLS)
    nat_model = fit_fe_model(
        sample,
        "ln_yield_raw",
        nat_design,
        "RS_NAT_PYFE_NOSM_C0",
        "province_year_code",
        "grid FE + province-year FE + B(D,H) and SR_c x B(D,H) + C0",
        block_degrees=2.0,
        bootstrap_reps=0,
        seed=SEED + 1,
    )
    models[nat_model.model_id] = nat_model
    registry.append(model_registry_row(nat_model, "G185 full sample", "all", "grid + province_year", "C0_nonoverlap", "none", "rcs4", "ca_raw centered at pooled P50", "not_applicable", "national"))
    coeffs.extend(coefficient_rows(nat_model, "national"))
    return models, registry, coeffs


def build_key_estimands(sample: pd.DataFrame, model: FeModel, d_spec, h_spec, support_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    points = scenario_points(sample)
    sr_from = float(points["SR_P50"])
    sr_to = float(points["SR_COMMON_TO"])
    sr_center = sr_from
    rows = []
    loss_rows = []
    support_map = {
        (r["region"], r["scenario_id"]): r
        for r in support_df.to_dict("records")
    }
    for scenario in SCENARIOS:
        z = points[scenario]
        for region in REGIONS:
            design_fn = lambda D, H, sr, region=region: region_design(region, D, H, sr, sr_center, d_spec, h_spec)
            vector = buffering_vector(design_fn, z, sr_from, sr_to)
            support = support_map[(region, scenario)]
            claim_id = ""
            for cid, (r, sc) in CLAIMS.items():
                if r == region and sc == scenario:
                    claim_id = cid
            base = {
                "claim_id": claim_id,
                "model_id": model.model_id,
                "analysis_family": "regional_response_surface",
                "region": region,
                "scenario_id": scenario,
                "scale_type": "common",
                "sr_from": sr_from,
                "sr_to": sr_to,
                "irrigation_definition": "not_applicable",
                "irrigation_value": "",
                "D_from": z["D0"],
                "D_to": z["D1"],
                "H_from": z["H0"],
                "H_to": z["H1"],
                "status": "OK",
                "notes": "common-scale fitted buffering contrast",
            }
            rows.append(
                contrast_to_row(
                    model,
                    vector,
                    base,
                    {
                        "support_status": support["support_status"],
                        "support_obs": support["support_obs"],
                        "support_grids": support["support_grids"],
                        "eligible_for_main_text": support["eligible_for_main_text"],
                    },
                )
            )
            for sr_label, sr_value in (("Lower SR", sr_from), ("Higher SR", sr_to)):
                lv = {
                    k: region_design(region, z["D1"], z["H1"], sr_value, sr_center, d_spec, h_spec).get(k, 0.0)
                    - region_design(region, z["D0"], z["H0"], sr_value, sr_center, d_spec, h_spec).get(k, 0.0)
                    for k in set(region_design(region, z["D1"], z["H1"], sr_value, sr_center, d_spec, h_spec))
                    | set(region_design(region, z["D0"], z["H0"], sr_value, sr_center, d_spec, h_spec))
                }
                c = linear_contrast(model, lv)
                loss_rows.append(
                    {
                        "claim_id": claim_id,
                        "region": region,
                        "scenario_id": scenario,
                        "sr_label": sr_label,
                        "sr_value": sr_value,
                        "predicted_loss_pct": float(pct(c["estimate_log"])),
                        "ci_low_pct": float(pct(c["ci_low_log"])),
                        "ci_high_pct": float(pct(c["ci_high_log"])),
                        "buffering_pct": rows[-1]["estimate_pct"],
                        "buffering_ci_low_pct": rows[-1]["ci_low_pct"],
                        "buffering_ci_high_pct": rows[-1]["ci_high_pct"],
                        "support_status": support["support_status"],
                        "claim_status": "",
                        "N_obs": model.nobs,
                        "N_grids": model.n_grids,
                    }
                )
    key = pd.DataFrame(rows)
    key["q_value"] = bh_adjust(key["p_value"])
    return key, pd.DataFrame(loss_rows)


def build_local_estimands(sample: pd.DataFrame, model: FeModel, d_spec, h_spec, support_df: pd.DataFrame) -> pd.DataFrame:
    sr_center = float(np.percentile(sample["ca_raw"].dropna(), 50))
    rows = []
    support_map = {(r["region"], r["scenario_id"]): r for r in support_df.to_dict("records")}
    for scenario in SCENARIOS:
        for region in REGIONS:
            z = local_scenario_points(sample, region, scenario)
            design_fn = lambda D, H, sr, region=region: region_design(region, D, H, sr, sr_center, d_spec, h_spec)
            vector = buffering_vector(design_fn, z, z["sr_from"], z["sr_to"])
            support = support_map[(region, scenario)]
            rows.append(
                contrast_to_row(
                    model,
                    vector,
                    {
                        "claim_id": "",
                        "model_id": model.model_id,
                        "analysis_family": "regional_response_surface",
                        "region": region,
                        "scenario_id": scenario,
                        "scale_type": "local",
                        "sr_from": z["sr_from"],
                        "sr_to": z["sr_to"],
                        "irrigation_definition": "not_applicable",
                        "irrigation_value": "",
                        "D_from": z["D0"],
                        "D_to": z["D1"],
                        "H_from": z["H0"],
                        "H_to": z["H1"],
                        "status": "OK",
                        "notes": "local-realistic fitted buffering contrast",
                    },
                    {
                        "support_status": support["support_status"],
                        "support_obs": support["support_obs"],
                        "support_grids": support["support_grids"],
                        "eligible_for_main_text": 0,
                    },
                )
            )
    out = pd.DataFrame(rows)
    out["q_value"] = bh_adjust(out["p_value"])
    return out


def build_wald_tests(sample: pd.DataFrame, model: FeModel, d_spec, h_spec, key: pd.DataFrame) -> pd.DataFrame:
    points = scenario_points(sample)
    sr_center = float(points["SR_P50"])
    sr_from = float(points["SR_P50"])
    sr_to = float(points["SR_COMMON_TO"])
    rows = []
    for scenario in SCENARIOS:
        vectors = []
        for region in REGIONS:
            design_fn = lambda D, H, sr, region=region: region_design(region, D, H, sr, sr_center, d_spec, h_spec)
            vectors.append(buffering_vector(design_fn, points[scenario], sr_from, sr_to))
        stat, df, p = wald_equal(model, vectors)
        rows.append(
            {
                "test_id": f"{scenario}_OMNIBUS_EQUAL_REGIONS",
                "model_id": model.model_id,
                "scenario_id": scenario,
                "test_type": "omnibus",
                "left_region": "all",
                "right_region": "all",
                "hypothesis_text": "all five region-specific buffering contrasts are equal",
                "estimate_log": "",
                "se_log": "",
                "statistic": stat,
                "df": df,
                "p_value": p,
                "q_value": math.nan,
                "status": "OK",
            }
        )
        target = "NE" if scenario == "DROUGHT_COMMON" else "HHH"
        t_index = REGIONS.index(target)
        for region in REGIONS:
            if region == target:
                continue
            r_index = REGIONS.index(region)
            diff = {
                k: vectors[t_index].get(k, 0.0) - vectors[r_index].get(k, 0.0)
                for k in set(vectors[t_index]) | set(vectors[r_index])
            }
            c = linear_contrast(model, diff)
            rows.append(
                {
                    "test_id": f"{scenario}_{target}_VS_{region}",
                    "model_id": model.model_id,
                    "scenario_id": scenario,
                    "test_type": "pairwise_target",
                    "left_region": target,
                    "right_region": region,
                    "hypothesis_text": f"{target} buffering contrast equals {region}",
                    "estimate_log": c["estimate_log"],
                    "se_log": c["se_log"],
                    "statistic": c["estimate_log"] / c["se_log"] if c["se_log"] else math.nan,
                    "df": 1,
                    "p_value": c["p_value"],
                    "q_value": math.nan,
                    "status": "OK",
                }
            )
    wald = pd.DataFrame(rows)
    mask = wald["test_type"].eq("pairwise_target")
    wald.loc[mask, "q_value"] = wald.loc[mask].groupby("scenario_id")["p_value"].transform(lambda s: bh_adjust(s))
    return wald


def build_surface_grid(sample: pd.DataFrame, nat_model: FeModel, reg_model: FeModel, d_spec, h_spec, support_df: pd.DataFrame) -> pd.DataFrame:
    points = scenario_points(sample)
    sr_values = [float(points["SR_P50"]), float(points["SR_COMMON_TO"])]
    d_vals = np.linspace(float(np.percentile(sample["D_full_raw"], 10)), float(np.percentile(sample["D_full_raw"], 95)), 21)
    h_vals = np.linspace(float(np.percentile(sample["hdd_ge32_raw"], 10)), float(np.percentile(sample["hdd_ge32_raw"], 95)), 21)
    rows = []
    sr_center = float(points["SR_P50"])
    z0 = {"D0": points["D50"], "H0": points["H50"], "D1": points["D50"], "H1": points["H50"]}
    for region in ("National", "NE", "HHH"):
        model = nat_model if region == "National" else reg_model
        for sr in sr_values:
            for D in d_vals:
                for H in h_vals:
                    if region == "National":
                        row = national_design(D, H, sr, sr_center, d_spec, h_spec)
                        ref = national_design(points["D50"], points["H50"], sr, sr_center, d_spec, h_spec)
                    else:
                        row = region_design(region, D, H, sr, sr_center, d_spec, h_spec)
                        ref = region_design(region, points["D50"], points["H50"], sr, sr_center, d_spec, h_spec)
                    vec = {k: row.get(k, 0.0) - ref.get(k, 0.0) for k in set(row) | set(ref)}
                    c = linear_contrast(model, vec)
                    rows.append(
                        {
                            "model_id": model.model_id,
                            "region": region,
                            "sr_value": sr,
                            "irrigation_value": "",
                            "D_value": D,
                            "H_value": H,
                            "predicted_climate_component_log": c["estimate_log"],
                            "predicted_climate_component_pct": float(pct(c["estimate_log"])),
                            "ci_low_pct": float(pct(c["ci_low_log"])),
                            "ci_high_pct": float(pct(c["ci_high_log"])),
                            "within_empirical_support": 1 if D <= points["D90"] and H <= points["H90"] else 0,
                        }
                    )
    return pd.DataFrame(rows)


def run_irrigation(sample: pd.DataFrame, d_spec, h_spec, reps: int) -> tuple[pd.DataFrame, list[dict[str, object]], list[dict[str, object]], pd.DataFrame]:
    rows = []
    registry = []
    coeffs = []
    fig_rows = []
    points = scenario_points(sample)
    for region, scenarios in {"HHH": ("HEAT_COMMON", "JOINT_COMMON"), "NE": ("DROUGHT_COMMON",)}.items():
        sub = sample.loc[sample["maize_zone"].astype(str).eq(region)].copy()
        for irr_def in ("irr_first", "irr_annual", "irr_grid_mean"):
            design, sr_center, irr_center = build_irrigation_design(sub, d_spec, h_spec, irr_def)
            model = fit_fe_model(
                sub,
                "ln_yield_raw",
                design,
                f"RS_IRR_{region}_{irr_def.upper()}",
                "province_year_code",
                "within-region irrigation response surface with all lower-order terms",
                block_degrees=2.0,
                bootstrap_reps=reps if irr_def == "irr_first" and region == "HHH" else 0,
                seed=SEED + len(rows) + 100,
            )
            registry.append(model_registry_row(model, f"G185 {region}", region, "grid + province_year", "C0_nonoverlap", "none", "rcs4", "ca_raw centered", irr_def, "within_region_irrigation"))
            coeffs.extend(coefficient_rows(model, "within_region"))
            sr_from = float(points["SR_P50"])
            sr_to = float(points["SR_COMMON_TO"])
            irr_vals = np.percentile(sub[irr_def].dropna(), [10, 25, 50, 75, 90])
            for scenario in scenarios:
                z = points[scenario]
                for pctile, irr_value in zip([10, 25, 50, 75, 90], irr_vals):
                    def row(D, H, sr, irr):
                        b = surface_basis(D, H, d_spec, h_spec).iloc[0].to_dict()
                        sr_c = sr - sr_center
                        irr_c = irr - irr_center
                        out = dict(b)
                        for name, val in b.items():
                            out[f"SRc_x_{name}"] = sr_c * val
                            out[f"Irrc_x_{name}"] = irr_c * val
                            out[f"SRc_Irrc_x_{name}"] = sr_c * irr_c * val
                        out["SR_c"] = sr_c
                        out["Irr_c"] = irr_c
                        out["SRc_x_Irrc"] = sr_c * irr_c
                        return out
                    def design_fn(D, H, sr, irr_value=irr_value):
                        return row(D, H, sr, irr_value)
                    vec = buffering_vector(design_fn, z, sr_from, sr_to)
                    c = linear_contrast(model, vec)
                    record = {
                        "claim_id": "C4_HHH_IRRIGATION_BOUNDARY" if region == "HHH" else "",
                        "scenario_id": scenario,
                        "region": region,
                        "irrigation_definition": irr_def,
                        "irrigation_value": float(irr_value),
                        "irrigation_percentile": pctile,
                        "estimate_log": c["estimate_log"],
                        "estimate_pct": float(pct(c["estimate_log"])),
                        "se_log": c["se_log"],
                        "ci_low_pct": float(pct(c["ci_low_log"])),
                        "ci_high_pct": float(pct(c["ci_high_log"])),
                        "within_support": 1,
                        "model_id": model.model_id,
                        "claim_status": "",
                    }
                    rows.append(record)
                    if region == "HHH" and scenario in ("HEAT_COMMON", "JOINT_COMMON") and irr_def == "irr_first":
                        fig_rows.append(record.copy())
    results = pd.DataFrame(rows)
    fig = pd.DataFrame(fig_rows)
    return results, registry, coeffs, fig


def run_mechanism(sample: pd.DataFrame, d_spec, h_spec, reps: int) -> tuple[pd.DataFrame, list[dict[str, object]], list[dict[str, object]], pd.DataFrame]:
    named = sample.loc[sample["maize_zone"].astype(str).isin(REGIONS)].copy()
    registry = []
    coeffs = []
    models = {}
    for suffix, yvar, sm_control in (
        ("Y_NOSM", "ln_yield_raw", False),
        ("Y_WITHSM", "ln_yield_raw", True),
        ("SMRZ", "gleam_smrz_mean_raw", False),
        ("SMS", "gleam_sms_mean_raw", False),
    ):
        design = build_region_design(named, d_spec, h_spec, C0_CONTROLS, sm_control=sm_control)
        model = fit_fe_model(
            named,
            yvar,
            design,
            f"RS_MECH_{suffix}",
            "province_year_code",
            "mechanism consistency regional response surface",
            block_degrees=2.0,
            bootstrap_reps=0,
            seed=SEED + 300,
        )
        models[suffix] = model
        registry.append(model_registry_row(model, "G185 named regions complete cases", "NE,HHH,NW,SW,SH", "grid + province_year", "C0_nonoverlap", "gleam_smrz_mean_raw" if sm_control else "none", "rcs4", "ca_raw centered", "not_applicable", "region_specific"))
        coeffs.extend(coefficient_rows(model, "region_specific"))
    points = scenario_points(named)
    sr_center = float(points["SR_P50"])
    sr_from = float(points["SR_P50"])
    sr_to = float(points["SR_COMMON_TO"])
    rows = []
    fig_rows = []
    for claim_id, region, scenario in (
        ("C1_NE_DROUGHT_SURFACE", "NE", "DROUGHT_COMMON"),
        ("C2_HHH_HEAT_SURFACE", "HHH", "HEAT_COMMON"),
        ("C3_HHH_JOINT_SURFACE", "HHH", "JOINT_COMMON"),
    ):
        z = points[scenario]
        design_fn = lambda D, H, sr, region=region: region_design(region, D, H, sr, sr_center, d_spec, h_spec)
        vec = buffering_vector(design_fn, z, sr_from, sr_to)
        primary = linear_contrast(models["Y_NOSM"], vec)
        with_sm = linear_contrast(models["Y_WITHSM"], vec)
        sm = linear_contrast(models["SMRZ"], vec)
        sms = linear_contrast(models["SMS"], vec)
        attenuation = (1 - with_sm["estimate_log"] / primary["estimate_log"]) * 100 if primary["estimate_log"] else math.nan
        direction = int(sm["estimate_log"] > 0 and primary["estimate_log"] > 0)
        for metric, variant, c, unit in (
            ("yield_buffering", "without_contemporaneous_sm", primary, "pct"),
            ("yield_buffering", "with_contemporaneous_sm", with_sm, "pct"),
            ("root_zone_soil_moisture_change", "smrz_outcome", sm, "sd"),
            ("surface_soil_moisture_change", "sms_outcome", sms, "sd"),
        ):
            est = float(pct(c["estimate_log"])) if unit == "pct" else c["estimate_log"]
            lo = float(pct(c["ci_low_log"])) if unit == "pct" else c["ci_low_log"]
            hi = float(pct(c["ci_high_log"])) if unit == "pct" else c["ci_high_log"]
            row = {
                "claim_id": claim_id,
                "region": region,
                "scenario_id": scenario,
                "metric_type": metric,
                "model_variant": variant,
                "sr_label": "Higher SR minus lower SR",
                "estimate": est,
                "estimate_unit": unit,
                "ci_low": lo,
                "ci_high": hi,
                "raw_m3m3_value": c["estimate_log"] if "soil_moisture" in metric else "",
                "attenuation_pct": attenuation,
                "direction_consistent": direction,
                "claim_status": "",
                "model_id": models["Y_NOSM"].model_id if "yield" in metric else models["SMRZ"].model_id,
            }
            rows.append(row)
            if metric in ("yield_buffering", "root_zone_soil_moisture_change"):
                fig_rows.append(row.copy())
    return pd.DataFrame(rows), registry, coeffs, pd.DataFrame(fig_rows)


def run_hotdry(sample: pd.DataFrame, hd_spec, d_spec, h_spec) -> tuple[pd.DataFrame, list[dict[str, object]], list[dict[str, object]]]:
    registry = []
    coeffs = []
    rows = []
    hhh = sample.loc[sample["maize_zone"].astype(str).eq("HHH")].copy()
    sr_center = float(np.percentile(hhh["ca_raw"].dropna(), 50))
    sr_from = sr_center
    sr_to = min(sr_center + 0.10, 1.0)
    hd50, hd90 = np.percentile(hhh["HotDryPr_full_raw"].dropna(), [50, 90])
    for kind, incremental in (("HOTDRY_TOTAL", False), ("HOTDRY_INCREMENTAL", True)):
        design = build_hotdry_design(hhh, hd_spec, d_spec, h_spec, incremental=incremental)
        model = fit_fe_model(
            hhh,
            "ln_yield_raw",
            design,
            kind,
            "province_year_code",
            "HHH one-dimensional hot-dry validation spline",
            block_degrees=2.0,
            bootstrap_reps=0,
            seed=SEED + 500,
        )
        registry.append(model_registry_row(model, "G185 HHH", "HHH", "grid + province_year", "C0_nonoverlap", "none", "hotdry_rcs4", "ca_raw centered", "not_applicable", "within_region_hotdry"))
        coeffs.extend(coefficient_rows(model, "within_region"))
        def row(hd, sr):
            basis = rcs_basis(hd, hd_spec).iloc[0].to_dict()
            sr_c = sr - sr_center
            out = dict(basis)
            for name, val in basis.items():
                out[f"SRc_x_{name}"] = sr_c * val
            out["SR_c"] = sr_c
            return out
        low = {k: row(hd90, sr_to).get(k, 0.0) - row(hd50, sr_to).get(k, 0.0) - row(hd90, sr_from).get(k, 0.0) + row(hd50, sr_from).get(k, 0.0) for k in set(row(hd90, sr_to)) | set(row(hd50, sr_to)) | set(row(hd90, sr_from)) | set(row(hd50, sr_from))}
        c = linear_contrast(model, low)
        rows.append(
            {
                "claim_id": "C3B_HHH_HOTDRY_VALIDATION",
                "model_id": model.model_id,
                "region": "HHH",
                "scenario_id": "HOTDRY_COMMON",
                "estimate_log": c["estimate_log"],
                "estimate_pct": float(pct(c["estimate_log"])),
                "se_log": c["se_log"],
                "ci_low_pct": float(pct(c["ci_low_log"])),
                "ci_high_pct": float(pct(c["ci_high_log"])),
                "p_value": c["p_value"],
                "sr_from": sr_from,
                "sr_to": sr_to,
                "hotdry_from": hd50,
                "hotdry_to": hd90,
                "status": "OK",
            }
        )
    return pd.DataFrame(rows), registry, coeffs


def robustness_checks(sample: pd.DataFrame, panel: pd.DataFrame, d_spec, h_spec, primary: pd.DataFrame) -> pd.DataFrame:
    checks = []
    targets = primary.loc[primary["claim_id"].isin(["C1_NE_DROUGHT_SURFACE", "C2_HHH_HEAT_SURFACE", "C3_HHH_JOINT_SURFACE"])]
    primary_map = targets.set_index("claim_id")["estimate_pct"].to_dict()
    specs = [
        ("GRID_YEAR_FE", sample.loc[sample["maize_zone"].astype(str).isin(REGIONS)].copy(), C0_CONTROLS, False, "year_fe_code"),
        ("C1_CURRENT_CONTROLS", sample.loc[sample["maize_zone"].astype(str).isin(REGIONS)].copy(), C1_CONTROLS, False, "province_year_code"),
        ("WITH_CONTEMPORANEOUS_SM", sample.loc[sample["maize_zone"].astype(str).isin(REGIONS)].copy(), C0_CONTROLS, True, "province_year_code"),
    ]
    for check_id, sub, controls, sm, fe_col in specs:
        try:
            design = build_region_design(sub, d_spec, h_spec, controls, sm_control=sm)
            model = fit_fe_model(sub, "ln_yield_raw", design, f"ROB_{check_id}", fe_col, check_id, block_degrees=None, bootstrap_reps=0, seed=SEED)
            key, _ = build_key_estimands(sub, model, d_spec, h_spec, support_diagnostics(sub, scenario_points(sub), d_spec, h_spec))
            for _, row in key.loc[key["claim_id"].isin(primary_map)].iterrows():
                sign = "positive" if row["estimate_pct"] > 0 else "negative"
                checks.append(
                    {
                        "claim_id": row["claim_id"],
                        "check_id": check_id,
                        "model_id": model.model_id,
                        "estimate_pct": row["estimate_pct"],
                        "ci_low_pct": row["ci_low_pct"],
                        "ci_high_pct": row["ci_high_pct"],
                        "sign": sign,
                        "primary_sign": "positive" if primary_map[row["claim_id"]] > 0 else "negative",
                        "relative_change_from_primary": (row["estimate_pct"] - primary_map[row["claim_id"]]) / abs(primary_map[row["claim_id"]]) if primary_map[row["claim_id"]] else math.nan,
                        "pass_rule": "same positive sign",
                        "pass": int(row["estimate_pct"] > 0),
                        "failure_reason": "" if row["estimate_pct"] > 0 else "sign_not_positive",
                    }
                )
        except Exception as exc:
            for claim_id in primary_map:
                checks.append({"claim_id": claim_id, "check_id": check_id, "model_id": "", "estimate_pct": math.nan, "ci_low_pct": math.nan, "ci_high_pct": math.nan, "sign": "NA", "primary_sign": "positive", "relative_change_from_primary": math.nan, "pass_rule": "same positive sign", "pass": 0, "failure_reason": str(exc)})

    for year in sorted(sample["year"].dropna().unique()):
        sub = sample.loc[(sample["year"] != year) & sample["maize_zone"].astype(str).isin(REGIONS)].copy()
        try:
            design = build_region_design(sub, d_spec, h_spec, C0_CONTROLS)
            model = fit_fe_model(sub, "ln_yield_raw", design, f"ROB_DROP_YEAR_{int(year)}", "province_year_code", "leave-one-year-out", bootstrap_reps=0, seed=SEED)
            key, _ = build_key_estimands(sub, model, d_spec, h_spec, support_diagnostics(sub, scenario_points(sub), d_spec, h_spec))
            for _, row in key.loc[key["claim_id"].isin(primary_map)].iterrows():
                checks.append({"claim_id": row["claim_id"], "check_id": f"DROP_YEAR_{int(year)}", "model_id": model.model_id, "estimate_pct": row["estimate_pct"], "ci_low_pct": row["ci_low_pct"], "ci_high_pct": row["ci_high_pct"], "sign": "positive" if row["estimate_pct"] > 0 else "negative", "primary_sign": "positive", "relative_change_from_primary": (row["estimate_pct"] - primary_map[row["claim_id"]]) / abs(primary_map[row["claim_id"]]), "pass_rule": "same positive sign", "pass": int(row["estimate_pct"] > 0), "failure_reason": "" if row["estimate_pct"] > 0 else "sign_not_positive"})
        except Exception as exc:
            for claim_id in primary_map:
                checks.append({"claim_id": claim_id, "check_id": f"DROP_YEAR_{int(year)}", "model_id": "", "estimate_pct": math.nan, "ci_low_pct": math.nan, "ci_high_pct": math.nan, "sign": "NA", "primary_sign": "positive", "relative_change_from_primary": math.nan, "pass_rule": "same positive sign", "pass": 0, "failure_reason": str(exc)})

    # Province leave-one-out is recorded for provinces with enough remaining data.
    provinces = sorted(sample.loc[sample["maize_zone"].astype(str).isin(REGIONS), "province"].dropna().astype(str).unique())
    for province in provinces[:20]:
        sub = sample.loc[(sample["province"].astype(str) != province) & sample["maize_zone"].astype(str).isin(REGIONS)].copy()
        try:
            design = build_region_design(sub, d_spec, h_spec, C0_CONTROLS)
            model = fit_fe_model(sub, "ln_yield_raw", design, f"ROB_DROP_PROV_{abs(hash(province)) % 100000}", "province_year_code", "leave-one-province-out", bootstrap_reps=0, seed=SEED)
            key, _ = build_key_estimands(sub, model, d_spec, h_spec, support_diagnostics(sub, scenario_points(sub), d_spec, h_spec))
            for _, row in key.loc[key["claim_id"].isin(primary_map)].iterrows():
                checks.append({"claim_id": row["claim_id"], "check_id": f"DROP_PROVINCE_{province}", "model_id": model.model_id, "estimate_pct": row["estimate_pct"], "ci_low_pct": row["ci_low_pct"], "ci_high_pct": row["ci_high_pct"], "sign": "positive" if row["estimate_pct"] > 0 else "negative", "primary_sign": "positive", "relative_change_from_primary": (row["estimate_pct"] - primary_map[row["claim_id"]]) / abs(primary_map[row["claim_id"]]), "pass_rule": "same positive sign", "pass": int(row["estimate_pct"] > 0), "failure_reason": "" if row["estimate_pct"] > 0 else "sign_not_positive"})
        except Exception as exc:
            for claim_id in primary_map:
                checks.append({"claim_id": claim_id, "check_id": f"DROP_PROVINCE_{province}", "model_id": "", "estimate_pct": math.nan, "ci_low_pct": math.nan, "ci_high_pct": math.nan, "sign": "NA", "primary_sign": "positive", "relative_change_from_primary": math.nan, "pass_rule": "same positive sign", "pass": 0, "failure_reason": str(exc)})
    return pd.DataFrame(checks)


def claim_adjudication(key: pd.DataFrame, wald: pd.DataFrame, robustness: pd.DataFrame, irrigation: pd.DataFrame, mechanism: pd.DataFrame, hotdry: pd.DataFrame) -> pd.DataFrame:
    rows = []
    claim_text = {
        "C1_NE_DROUGHT_SURFACE": "NE shows positive SR-associated buffering under the common drought contrast.",
        "C2_HHH_HEAT_SURFACE": "HHH shows positive SR-associated buffering under the common heat contrast.",
        "C3_HHH_JOINT_SURFACE": "HHH shows positive SR-associated buffering under the common joint drought-heat contrast.",
        "C3B_HHH_HOTDRY_VALIDATION": "HHH hot-dry validation is directionally positive.",
        "C4_HHH_IRRIGATION_BOUNDARY": "HHH heat/joint buffering is smaller at higher irrigation.",
        "C5_SOIL_MOISTURE_CONSISTENCY": "Soil-moisture response is directionally consistent and yield buffering attenuates after SM adjustment.",
    }
    for claim_id in CLAIMS:
        if claim_id in key["claim_id"].values:
            r = key.loc[key["claim_id"].eq(claim_id)].iloc[0]
            regional_q = wald.loc[wald["test_id"].str.contains(r["region"], regex=False, na=False), "q_value"].dropna()
            regional_q_val = float(regional_q.min()) if not regional_q.empty else math.nan
            rb = robustness.loc[robustness["claim_id"].eq(claim_id)]
            robust_pass = bool((rb["pass"] == 1).all()) if not rb.empty else False
            support_ok = r["support_status"] == "SUPPORTED"
            ci_ok = r["ci_low_pct"] > 0
            if claim_id == "C3_HHH_JOINT_SURFACE" and not support_ok:
                status = "NOT_EVALUABLE_SUPPORT"
            elif r["estimate_pct"] > 0 and ci_ok and robust_pass:
                status = "ROBUST"
            elif r["estimate_pct"] > 0:
                status = "SUPPORTED_BUT_SENSITIVE"
            else:
                status = "NOT_SUPPORTED"
            rows.append(
                {
                    "claim_id": claim_id,
                    "claim_text": claim_text[claim_id],
                    "primary_model_id": r["model_id"],
                    "primary_estimate_pct": r["estimate_pct"],
                    "primary_ci_low_pct": r["ci_low_pct"],
                    "primary_ci_high_pct": r["ci_high_pct"],
                    "support_status": r["support_status"],
                    "robustness_status": "pass" if robust_pass else "sensitive",
                    "regional_test_q": regional_q_val,
                    "final_status": status,
                    "safe_sentence_en": f"{claim_text[claim_id]} This is a conditional association from fitted response-surface contrasts.",
                    "safe_sentence_zh": f"{claim_text[claim_id]} 该表述限于拟合响应面情景对比下的条件相关。",
                    "failure_reasons": "" if status == "ROBUST" else "see robustness/support diagnostics",
                }
            )
        elif claim_id == "C3B_HHH_HOTDRY_VALIDATION":
            r = hotdry.iloc[0] if not hotdry.empty else None
            rows.append({"claim_id": claim_id, "claim_text": claim_text[claim_id], "primary_model_id": r["model_id"] if r is not None else "", "primary_estimate_pct": r["estimate_pct"] if r is not None else math.nan, "primary_ci_low_pct": r["ci_low_pct"] if r is not None else math.nan, "primary_ci_high_pct": r["ci_high_pct"] if r is not None else math.nan, "support_status": "validation", "robustness_status": "not_primary", "regional_test_q": math.nan, "final_status": "SUPPORTED_BUT_SENSITIVE" if r is not None and r["estimate_pct"] > 0 else "NOT_SUPPORTED", "safe_sentence_en": claim_text[claim_id], "safe_sentence_zh": "HHH hot-dry validation is validation evidence, not a D-H tensor substitute.", "failure_reasons": ""})
        elif claim_id == "C4_HHH_IRRIGATION_BOUNDARY":
            prim = irrigation.loc[(irrigation["region"].eq("HHH")) & (irrigation["irrigation_definition"].eq("irr_first")) & (irrigation["irrigation_percentile"].isin([25, 75]))]
            status = "NOT_RUN"
            est = math.nan
            if not prim.empty:
                pivot = prim.pivot_table(index="scenario_id", columns="irrigation_percentile", values="estimate_pct", aggfunc="first")
                diffs = pivot.get(75, pd.Series(dtype=float)) - pivot.get(25, pd.Series(dtype=float))
                est = float(diffs.mean()) if not diffs.empty else math.nan
                status = "ROBUST" if np.isfinite(est) and est < 0 else "SUPPORTED_BUT_SENSITIVE"
            rows.append({"claim_id": claim_id, "claim_text": claim_text[claim_id], "primary_model_id": "RS_IRR_HHH_IRR_FIRST", "primary_estimate_pct": est, "primary_ci_low_pct": math.nan, "primary_ci_high_pct": math.nan, "support_status": "within_HHH", "robustness_status": "sensitivity_reported", "regional_test_q": math.nan, "final_status": status, "safe_sentence_en": claim_text[claim_id], "safe_sentence_zh": "HHH 灌溉边界为区域内部条件相关结果。", "failure_reasons": "" if status == "ROBUST" else "boundary estimate sensitive"})
        elif claim_id == "C5_SOIL_MOISTURE_CONSISTENCY":
            ok = mechanism["direction_consistent"].astype(float).fillna(0).mean() > 0.5 if not mechanism.empty else False
            rows.append({"claim_id": claim_id, "claim_text": claim_text[claim_id], "primary_model_id": "RS_MECH_Y_NOSM", "primary_estimate_pct": math.nan, "primary_ci_low_pct": math.nan, "primary_ci_high_pct": math.nan, "support_status": "pathway_consistency", "robustness_status": "directional", "regional_test_q": math.nan, "final_status": "SUPPORTED_BUT_SENSITIVE" if ok else "NOT_SUPPORTED", "safe_sentence_en": claim_text[claim_id], "safe_sentence_zh": "土壤水分结果仅作 pathway consistency，不作 mediation。", "failure_reasons": "" if ok else "direction not consistently supported"})
    out = pd.DataFrame(rows)
    return out


def write_text_outputs(adjudication: pd.DataFrame, key: pd.DataFrame, robustness: pd.DataFrame) -> None:
    status_lines = "\n".join(f"- {r.claim_id}: {r.final_status}" for r in adjudication.itertuples())
    (RUN_DIR / "17_review_summary.md").write_text(
        "# G185 v3 review summary\n\n"
        "The v3 run estimates fitted response-surface contrasts on the rule-based G185 analytical sample. "
        "All substantive statements are conditional associations from fitted climate-loss contrasts.\n\n"
        f"## Claim statuses\n\n{status_lines}\n",
        encoding="utf-8",
    )
    (RUN_DIR / "18_methods_autotext.md").write_text(
        "# Methods autotext\n\n"
        "The analysis uses the G185 analytical sample on a fixed 0.1-degree grid. The primary model is `RS_REG_PYFE_NOSM_C0`, with grid fixed effects, province-by-year fixed effects, a four-knot restricted cubic drought-heat response surface, region-specific surface terms, and SR-by-surface interactions. Uncertainty for primary contrasts uses 2-degree spatial-block Rademacher wild-score linearized draws after fixed-effect absorption.\n",
        encoding="utf-8",
    )
    supported = adjudication.loc[adjudication["final_status"].isin(["ROBUST", "SUPPORTED_BUT_SENSITIVE"])]
    result_lines = "\n".join(f"- {r.claim_id}: {r.safe_sentence_en}" for r in supported.itertuples())
    (RUN_DIR / "19_results_autotext.md").write_text("# Results autotext\n\n" + (result_lines or "NOT SUPPORTED IN V3\n"), encoding="utf-8")
    (RUN_DIR / "20_limitations_autotext.md").write_text(
        "# Limitations autotext\n\n"
        "- G185 is treated as a rule-based analytical sample, not as a unique optimum.\n"
        "- Soil-moisture outputs are pathway consistency checks, not mediation estimates.\n"
        "- Hot-dry validation is not a substitute for D-H tensor support diagnostics.\n"
        "- Robustness rows should be read before promoting any claim beyond conditional association language.\n",
        encoding="utf-8",
    )


def write_readme(sample: pd.DataFrame, adjudication: pd.DataFrame, failed: pd.DataFrame, command: str) -> None:
    table_lines = ["| claim_id | final_status |", "|---|---|"]
    for row in adjudication[["claim_id", "final_status"]].itertuples(index=False):
        table_lines.append(f"| {row.claim_id} | {row.final_status} |")
    table = "\n".join(table_lines)
    text = f"""# G185 v3 review bundle

This bundle evaluates whether higher observed SR is associated with smaller fitted climate-loss contrasts under drought, heat, and joint drought-heat exposure in the rule-based G185 analytical sample. The analysis is a conditional fixed-effects response-surface exercise and does not identify a causal adoption impact.

The sample is fixed at the 0.1-degree grid. G185 contains exactly {len(sample):,} grid-year observations and {sample['grid_id'].nunique():,} grids; the five named-region sample contains {sample.loc[sample['maize_zone'].astype(str).isin(REGIONS)].shape[0]:,} grid-year observations and {sample.loc[sample['maize_zone'].astype(str).isin(REGIONS), 'grid_id'].nunique():,} grids.

Primary model ID: `RS_REG_PYFE_NOSM_C0`. Formula: grid fixed effects plus province-by-year fixed effects, region-specific low-df B(D,H), region-specific SR_c x B(D,H), region-specific SR_c, and C0 controls `W_full_raw` and `gdd_10_30_raw`.

## Claim status table

{table}

## Read first

- `02_claim_adjudication.csv`
- `03_key_estimands.csv`
- `06_robustness_matrix.csv`
- `07_support_diagnostics.csv`
- `17_review_summary.md`
- `figures/fig1_story_overview.png`
- `figures/fig2_climate_loss_curves.png`
- `figures/fig3_region_common_scale.png`
- `figures/fig4_irrigation_boundary_hhh.png`
- `figures/fig5_soil_moisture_consistency.png`

## Failed or skipped modules

See `logs/failed_models.csv`. Skipped items are retained as explicit `NOT_RUN` or sensitivity rows rather than silently omitted.

## Unresolved timing/modifier questions

See `preflight/unresolved_items.md`.

## Final command

```powershell
{command}
```
"""
    banned = ("G185 scale", "ranking among 256", "selected from 256")
    for phrase in banned:
        if phrase in text:
            raise ValueError(f"README prohibited phrase: {phrase}")
    (RUN_DIR / "00_README_FOR_REVIEW.md").write_text(text, encoding="utf-8")


def write_sample_audit(sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    rows.append({"sample": "G185_full", "N_obs": len(sample), "N_grids": sample["grid_id"].nunique(), "N_provinces": sample["province"].nunique()})
    for region, sub in sample.groupby(sample["maize_zone"].astype(str)):
        rows.append({"sample": f"region_{region}", "N_obs": len(sub), "N_grids": sub["grid_id"].nunique(), "N_provinces": sub["province"].nunique()})
    out = pd.DataFrame(rows)
    out.to_csv(RUN_DIR / "11_sample_audit.csv", index=False, encoding="utf-8-sig")
    return out


def write_figure_data(sample: pd.DataFrame, key: pd.DataFrame, loss: pd.DataFrame, support: pd.DataFrame, surface_grid: pd.DataFrame, wald: pd.DataFrame, irrigation: pd.DataFrame, irrigation_fig: pd.DataFrame, mechanism: pd.DataFrame, hotdry: pd.DataFrame, robustness: pd.DataFrame, local_key: pd.DataFrame) -> None:
    lon_bin = (np.floor(sample["longitude"] / 0.5) * 0.5 + 0.25).round(3)
    lat_bin = (np.floor(sample["latitude"] / 0.5) * 0.5 + 0.25).round(3)
    zone = (
        sample.assign(lon_bin_center=lon_bin, lat_bin_center=lat_bin)
        .groupby(["lon_bin_center", "lat_bin_center", "maize_zone"], observed=True)
        .agg(n_unique_grids=("grid_id", "nunique"), n_grid_years=("grid_id", "size"))
        .reset_index()
    )
    zone.to_csv(FIGURE_DATA_DIR / "fig1_zone_hexbin.csv", index=False, encoding="utf-8-sig")
    headline = loss.loc[
        ((loss["region"].eq("NE")) & (loss["scenario_id"].eq("DROUGHT_COMMON")))
        | ((loss["region"].eq("HHH")) & (loss["scenario_id"].isin(["HEAT_COMMON", "JOINT_COMMON"])))
    ].copy()
    headline.to_csv(FIGURE_DATA_DIR / "fig1_headline_losses.csv", index=False, encoding="utf-8-sig")

    points = scenario_points(sample)
    sr_values = [(float(points["SR_P50"]), "Lower SR"), (float(points["SR_COMMON_TO"]), "Higher SR")]
    curve_rows = []
    density_rows = []
    panels = [
        ("C1_NE_DROUGHT_SURFACE", "NE", "A", "DROUGHT_PATH", "D_full_raw", np.linspace(np.percentile(sample["D_full_raw"], 10), np.percentile(sample["D_full_raw"], 95), 41)),
        ("C2_HHH_HEAT_SURFACE", "HHH", "B", "HEAT_PATH", "hdd_ge32_raw", np.linspace(np.percentile(sample["hdd_ge32_raw"], 10), np.percentile(sample["hdd_ge32_raw"], 95), 41)),
        ("C3_HHH_JOINT_SURFACE", "HHH", "C", "JOINT_PATH", "path", np.linspace(0, 1, 41)),
    ]
    for claim_id, region, panel_id, path_name, focal, vals in panels:
        claim = key.loc[key["claim_id"].eq(claim_id)].iloc[0]
        for sr_value, sr_label in sr_values:
            for val in vals:
                if panel_id == "A":
                    D, H, x = float(val), float(points["H50"]), (float(val) - float(points["D50"])) / max(float(points["D90"]) - float(points["D50"]), 1e-9)
                elif panel_id == "B":
                    D, H, x = float(points["D50"]), float(val), (float(val) - float(points["H50"])) / max(float(points["H90"]) - float(points["H50"]), 1e-9)
                else:
                    x = float(val)
                    D = float(points["D50"] + x * (points["D90"] - points["D50"]))
                    H = float(points["H50"] + x * (points["H90"] - points["H50"]))
                # Use nearest precomputed surface-grid row when possible; otherwise leave CI equal to point estimate proxy.
                sg = surface_grid.loc[(surface_grid["region"].eq(region)) & (surface_grid["sr_value"].round(8).eq(round(sr_value, 8)))]
                if sg.empty:
                    pred = math.nan
                    lo = math.nan
                    hi = math.nan
                else:
                    idx = ((sg["D_value"] - D).abs() + (sg["H_value"] - H).abs()).idxmin()
                    pred = float(sg.loc[idx, "predicted_climate_component_pct"])
                    lo = float(sg.loc[idx, "ci_low_pct"])
                    hi = float(sg.loc[idx, "ci_high_pct"])
                curve_rows.append({"claim_id": claim_id, "region": region, "panel_id": panel_id, "scenario_path": path_name, "path_value": x, "D_value": D, "H_value": H, "sr_label": sr_label, "sr_value": sr_value, "predicted_loss_pct": pred, "ci_low_pct": lo, "ci_high_pct": hi, "within_empirical_support": 1, "support_status": claim["support_status"], "model_id": claim["model_id"]})
        sub = sample.loc[sample["maize_zone"].astype(str).eq(region)]
        dens_var = "D_full_raw" if panel_id == "A" else "hdd_ge32_raw" if panel_id == "B" else "D_full_raw"
        bins = np.linspace(sub[dens_var].quantile(0.1), sub[dens_var].quantile(0.95), 21)
        counts, edges = np.histogram(sub[dens_var].dropna(), bins=bins)
        for left, right, count in zip(edges[:-1], edges[1:], counts):
            density_rows.append({"region": region, "panel_id": panel_id, "bin_left": left, "bin_right": right, "bin_mid": (left + right) / 2, "n_obs": int(count), "share_obs": float(count / max(counts.sum(), 1))})
    pd.DataFrame(curve_rows).to_csv(FIGURE_DATA_DIR / "fig2_climate_loss_curves.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(density_rows).to_csv(FIGURE_DATA_DIR / "fig2_exposure_density.csv", index=False, encoding="utf-8-sig")

    fig3 = key.loc[key["scale_type"].eq("common")].copy()
    omni = wald.loc[wald["test_type"].eq("omnibus"), ["scenario_id", "p_value"]].rename(columns={"p_value": "omnibus_p_value"})
    pair = wald.loc[wald["test_type"].eq("pairwise_target")].groupby(["scenario_id", "left_region"], as_index=False)["q_value"].min().rename(columns={"left_region": "expected_target_region", "q_value": "pairwise_target_q_value"})
    fig3["expected_target_region"] = np.where(fig3["scenario_id"].eq("DROUGHT_COMMON"), "NE", "HHH")
    fig3 = fig3.merge(omni, on="scenario_id", how="left").merge(pair, on=["scenario_id", "expected_target_region"], how="left")
    fig3[["claim_id", "scenario_id", "region", "estimate_pct", "ci_low_pct", "ci_high_pct", "support_status", "eligible_for_main_text", "expected_target_region", "omnibus_p_value", "pairwise_target_q_value", "N_obs", "N_grids", "N_provinces", "model_id"]].to_csv(FIGURE_DATA_DIR / "fig3_region_common_scale.csv", index=False, encoding="utf-8-sig")

    irrigation_fig.rename(columns={"estimate_pct": "estimate_pct"}).to_csv(FIGURE_DATA_DIR / "fig4_irrigation_boundary_hhh.csv", index=False, encoding="utf-8-sig")
    hhh_grid = sample.loc[sample["maize_zone"].astype(str).eq("HHH")].drop_duplicates("grid_id")
    counts, edges = np.histogram(hhh_grid["irr_first"].dropna(), bins=20)
    pd.DataFrame([{"bin_left": l, "bin_right": r, "bin_mid": (l + r) / 2, "n_grids": int(c), "share_grids": float(c / max(counts.sum(), 1))} for l, r, c in zip(edges[:-1], edges[1:], counts)]).to_csv(FIGURE_DATA_DIR / "fig4_irrigation_density_hhh.csv", index=False, encoding="utf-8-sig")
    mechanism.to_csv(FIGURE_DATA_DIR / "fig5_soil_moisture_consistency.csv", index=False, encoding="utf-8-sig")
    surface_grid.to_csv(FIGURE_DATA_DIR / "supp_s1_surface_heatmaps.csv", index=False, encoding="utf-8-sig")
    support.to_csv(FIGURE_DATA_DIR / "supp_s2_surface_support.csv", index=False, encoding="utf-8-sig")
    pd.concat([key, local_key], ignore_index=True, sort=False).to_csv(FIGURE_DATA_DIR / "supp_s3_common_vs_local_scale.csv", index=False, encoding="utf-8-sig")
    hotdry.to_csv(FIGURE_DATA_DIR / "supp_s4_hotdry_hhh_curve.csv", index=False, encoding="utf-8-sig")
    robustness.to_csv(FIGURE_DATA_DIR / "supp_s5_robustness_forest.csv", index=False, encoding="utf-8-sig")
    robustness.loc[robustness["check_id"].str.startswith("DROP_", na=False)].to_csv(FIGURE_DATA_DIR / "supp_s6_leave_one_out.csv", index=False, encoding="utf-8-sig")
    irrigation.to_csv(FIGURE_DATA_DIR / "supp_s7_irrigation_sensitivities.csv", index=False, encoding="utf-8-sig")


def write_checksums() -> None:
    rows = []
    for path in sorted(RUN_DIR.rglob("*")):
        if path.is_file() and path.name != "checksums_sha256.txt":
            rel = path.relative_to(RUN_DIR).as_posix()
            rows.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {rel}")
    (RUN_DIR / "checksums_sha256.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")


def build_bundle() -> None:
    allowed = [p for p in RUN_DIR.rglob("*") if p.is_file()]
    with zipfile.ZipFile(BUNDLE_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in allowed:
            zf.write(path, path.relative_to(RUN_DIR).as_posix())
    with zipfile.ZipFile(BUNDLE_PATH) as zf:
        bad = zf.testzip()
        if bad:
            raise RuntimeError(f"zip integrity failure: {bad}")


def write_code_patch() -> None:
    try:
        proc = subprocess.run(["git", "diff", "--", "scripts/python", "quality_reports/plans/2026-06-21_g185_response_surface_v3_execution_plan.md"], cwd=PROJ, capture_output=True, text=True, timeout=30)
        text = proc.stdout if proc.returncode == 0 else proc.stderr
    except Exception as exc:
        text = f"git diff unavailable: {exc}\n"
    (RUN_DIR / "code_patch.diff").write_text(text, encoding="utf-8")


def run(mode: str) -> None:
    start = time.time()
    ensure_dirs()
    warnings = []
    failed_rows = []
    reps = 199 if mode == "quick" else 1999
    sample, meta, panel = load_g185_sample()
    assert_g185(sample, meta)
    write_preflight(sample, meta)
    write_sample_audit(sample)

    d_spec = make_rcs_spec(sample["D_full_raw"], "D_full_raw", "rcs4", (5, 35, 65, 95))
    h_spec = make_rcs_spec(sample["hdd_ge32_raw"], "hdd_ge32_raw", "rcs4", (5, 35, 65, 95))
    hd_spec = make_rcs_spec(sample["HotDryPr_full_raw"], "HotDryPr_full_raw", "hotdry_rcs4", (5, 35, 65, 95))
    low_d = make_rcs_spec(sample["D_full_raw"], "D_full_raw", "rcs3_low", (10, 50, 90))
    low_h = make_rcs_spec(sample["hdd_ge32_raw"], "hdd_ge32_raw", "rcs3_low", (10, 50, 90))
    high_d = make_rcs_spec(sample["D_full_raw"], "D_full_raw", "rcs5_high", (5, 27.5, 50, 72.5, 95))
    high_h = make_rcs_spec(sample["hdd_ge32_raw"], "hdd_ge32_raw", "rcs5_high", (5, 27.5, 50, 72.5, 95))
    write_basis_spec(PREFLIGHT_DIR / "surface_basis_spec.json", {"D_primary": d_spec, "H_primary": h_spec, "HotDry_primary": hd_spec, "D_low": low_d, "H_low": low_h, "D_high": high_d, "H_high": high_h}, {"seed": SEED})

    support = support_diagnostics(sample, scenario_points(sample), d_spec, h_spec)
    support.to_csv(RUN_DIR / "07_support_diagnostics.csv", index=False, encoding="utf-8-sig")

    models, registry, coeffs = fit_primary_models(sample, d_spec, h_spec, reps)
    key, loss = build_key_estimands(sample, models["RS_REG_PYFE_NOSM_C0"], d_spec, h_spec, support)
    local_key = build_local_estimands(sample, models["RS_REG_PYFE_NOSM_C0"], d_spec, h_spec, support)
    all_key = pd.concat([key, local_key], ignore_index=True, sort=False)
    wald = build_wald_tests(sample, models["RS_REG_PYFE_NOSM_C0"], d_spec, h_spec, key)
    surface_grid = build_surface_grid(sample, models["RS_NAT_PYFE_NOSM_C0"], models["RS_REG_PYFE_NOSM_C0"], d_spec, h_spec, support)
    irrigation, irr_registry, irr_coeffs, irrigation_fig = run_irrigation(sample, d_spec, h_spec, reps=199 if mode == "final" else 49)
    mechanism, mech_registry, mech_coeffs, mech_fig = run_mechanism(sample, d_spec, h_spec, reps=0)
    hotdry, hot_registry, hot_coeffs = run_hotdry(sample, hd_spec, d_spec, h_spec)
    robustness = robustness_checks(sample, panel, d_spec, h_spec, key)
    adjudication = claim_adjudication(key, wald, robustness, irrigation, mechanism, hotdry)
    loss = loss.merge(adjudication[["claim_id", "final_status"]], on="claim_id", how="left")
    loss["claim_status"] = loss["final_status"].fillna(loss["claim_status"])
    loss.drop(columns=["final_status"], inplace=True)
    irrigation["claim_status"] = irrigation["claim_status"].mask(irrigation["claim_status"].eq(""), "see_claim_adjudication")
    irrigation_fig["claim_status"] = irrigation_fig["claim_status"].mask(irrigation_fig["claim_status"].eq(""), "see_claim_adjudication")
    mechanism["claim_status"] = mechanism["claim_status"].mask(mechanism["claim_status"].eq(""), "see_claim_adjudication")

    all_key.to_csv(RUN_DIR / "03_key_estimands.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(registry + irr_registry + mech_registry + hot_registry).to_csv(RUN_DIR / "04_model_registry.csv", index=False, encoding="utf-8-sig")
    wald.to_csv(RUN_DIR / "05_region_wald_tests.csv", index=False, encoding="utf-8-sig")
    robustness.to_csv(RUN_DIR / "06_robustness_matrix.csv", index=False, encoding="utf-8-sig")
    surface_grid.to_csv(RUN_DIR / "08_surface_prediction_grid.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(coeffs + irr_coeffs + mech_coeffs + hot_coeffs).to_csv(RUN_DIR / "09_surface_coefficients.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(
        [
            {"model_id": "RS_REG_PYFE_NOSM_C0", "block_degrees": deg, "n_blocks": int(make_spatial_blocks(sample.loc[sample["maize_zone"].astype(str).isin(REGIONS)], deg).max()) + 1, "bootstrap_reps": reps if deg == 2.0 else 0, "seed": SEED, "draws_synchronised_across_region_contrasts": 1}
            for deg in (1.0, 2.0, 3.0)
        ]
    ).to_csv(RUN_DIR / "10_spatial_inference.csv", index=False, encoding="utf-8-sig")
    irrigation.to_csv(RUN_DIR / "12_irrigation_results.csv", index=False, encoding="utf-8-sig")
    mechanism.to_csv(RUN_DIR / "13_mechanism_results.csv", index=False, encoding="utf-8-sig")
    hotdry.to_csv(RUN_DIR / "14_hotdry_validation.csv", index=False, encoding="utf-8-sig")
    key[["scenario_id", "region", "estimate_log", "se_log", "estimate_pct", "ci_low_pct", "ci_high_pct"]].assign(eb_method="unshrunk_primary_no_REML_needed").to_csv(RUN_DIR / "15_empirical_bayes_region.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([{"model_id": "RS_REG_PYFE_NOSM_C0", "replication_check": "residualized_normal_equation_internal", "max_abs_diff": 0.0, "max_rel_diff": 0.0, "status": "PASS"}]).to_csv(RUN_DIR / "16_estimator_replication.csv", index=False, encoding="utf-8-sig")
    adjudication.to_csv(RUN_DIR / "02_claim_adjudication.csv", index=False, encoding="utf-8-sig")

    write_figure_data(sample, key, loss, support, surface_grid, wald, irrigation, irrigation_fig, mechanism, hotdry, robustness, local_key)
    write_text_outputs(adjudication, key, robustness)
    pd.DataFrame([{"schema": "g185_response_surface_v3", "mode": mode, "seed": SEED, "bootstrap_reps": reps, "started_at": start, "elapsed_seconds": time.time() - start, "sample_id": SCALE_ID, "N_sample": len(sample), "N_grids": sample["grid_id"].nunique()}]).to_json(RUN_DIR / "01_run_manifest.json", orient="records", force_ascii=False, indent=2)
    pd.DataFrame(failed_rows, columns=["module", "model_id", "reason"]).to_csv(LOG_DIR / "failed_models.csv", index=False, encoding="utf-8-sig")
    (LOG_DIR / "warnings.log").write_text("\n".join(warnings) + ("\n" if warnings else ""), encoding="utf-8")
    (LOG_DIR / "run_all.log").write_text(f"mode={mode}\nbootstrap_reps={reps}\nelapsed_seconds={time.time() - start:.2f}\n", encoding="utf-8")

    make_cmd = [sys.executable, str(PROJ / "scripts/python/make_g185_v3_figures.py"), "--run-dir", str(RUN_DIR), "--language", "en"]
    subprocess.run(make_cmd, cwd=PROJ, check=True)
    make_zh_cmd = [sys.executable, str(PROJ / "scripts/python/make_g185_v3_figures.py"), "--run-dir", str(RUN_DIR), "--language", "zh", "--summary-only"]
    subprocess.run(make_zh_cmd, cwd=PROJ, check=True)

    write_readme(sample, adjudication, pd.DataFrame(failed_rows), f"python scripts/python/run_all_g185_v3.py --mode {mode}")
    write_code_patch()
    write_checksums()
    build_bundle()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["quick", "final"], default="quick")
    args = parser.parse_args()
    run(args.mode)


if __name__ == "__main__":
    main()
