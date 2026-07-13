"""Scenario design rows and estimand helpers for G185 v3."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import norm

from g185_v3_config import REGIONS, SCENARIOS
from g185_v3_fixed_effects import FeModel, linear_contrast, pct
from g185_v3_splines import RcsSpec, rcs_basis, surface_basis


def scenario_points(sample: pd.DataFrame) -> dict[str, dict[str, float]]:
    d50, d85, d90 = np.percentile(sample["D_full_raw"].dropna(), [50, 85, 90])
    h50, h85, h90 = np.percentile(sample["hdd_ge32_raw"].dropna(), [50, 85, 90])
    sr50 = float(np.percentile(sample["ca_raw"].dropna(), 50))
    sr_to = min(sr50 + 0.10, 1.0)
    return {
        "D50": float(d50),
        "D85": float(d85),
        "D90": float(d90),
        "H50": float(h50),
        "H85": float(h85),
        "H90": float(h90),
        "SR_P50": sr50,
        "SR_COMMON_TO": sr_to,
        "DROUGHT_COMMON": {"D0": float(d50), "H0": float(h50), "D1": float(d90), "H1": float(h50)},
        "HEAT_COMMON": {"D0": float(d50), "H0": float(h50), "D1": float(d50), "H1": float(h90)},
        "JOINT_COMMON": {"D0": float(d50), "H0": float(h50), "D1": float(d90), "H1": float(h90)},
    }


def local_scenario_points(sample: pd.DataFrame, region: str, scenario: str) -> dict[str, float]:
    sub = sample.loc[sample["maize_zone"].astype(str).eq(region)]
    d50, d90 = np.percentile(sub["D_full_raw"].dropna(), [50, 90])
    h50, h90 = np.percentile(sub["hdd_ge32_raw"].dropna(), [50, 90])
    sr25, sr75 = np.percentile(sub["ca_raw"].dropna(), [25, 75])
    if scenario == "DROUGHT_COMMON":
        d1, h1 = d90, h50
    elif scenario == "HEAT_COMMON":
        d1, h1 = d50, h90
    else:
        d1, h1 = d90, h90
    return {"D0": float(d50), "H0": float(h50), "D1": float(d1), "H1": float(h1), "sr_from": float(sr25), "sr_to": float(sr75)}


def support_diagnostics(sample: pd.DataFrame, points: dict[str, object], d_spec: RcsSpec, h_spec: RcsSpec) -> pd.DataFrame:
    rows = []
    d85 = float(points["D85"])
    h85 = float(points["H85"])
    scaled = np.column_stack(
        [
            (sample["D_full_raw"].to_numpy(dtype=float) - d_spec.raw_positive_median) / d_spec.raw_positive_iqr,
            (sample["hdd_ge32_raw"].to_numpy(dtype=float) - h_spec.raw_positive_median) / h_spec.raw_positive_iqr,
        ]
    )
    for region in REGIONS:
        sub = sample.loc[sample["maize_zone"].astype(str).eq(region)].copy()
        region_scaled = np.column_stack(
            [
                (sub["D_full_raw"].to_numpy(dtype=float) - d_spec.raw_positive_median) / d_spec.raw_positive_iqr,
                (sub["hdd_ge32_raw"].to_numpy(dtype=float) - h_spec.raw_positive_median) / h_spec.raw_positive_iqr,
            ]
        )
        tree = cKDTree(region_scaled)
        support = sub.loc[(sub["D_full_raw"] >= d85) & (sub["hdd_ge32_raw"] >= h85)]
        for scenario in SCENARIOS:
            sp = points[scenario]
            low = np.array([[(sp["D0"] - d_spec.raw_positive_median) / d_spec.raw_positive_iqr, (sp["H0"] - h_spec.raw_positive_median) / h_spec.raw_positive_iqr]])
            high = np.array([[(sp["D1"] - d_spec.raw_positive_median) / d_spec.raw_positive_iqr, (sp["H1"] - h_spec.raw_positive_median) / h_spec.raw_positive_iqr]])
            low_dist = float(tree.query(low, k=1)[0][0])
            high_dist = float(tree.query(high, k=1)[0][0])
            support_obs = int(len(support))
            support_grids = int(support["grid_id"].nunique())
            support_prov = int(support["province"].nunique())
            if scenario == "JOINT_COMMON":
                if support_obs >= 100 and support_grids >= 30 and support_prov >= 3:
                    status = "SUPPORTED"
                elif support_obs >= 30 or support_grids >= 10:
                    status = "LIMITED_SUPPORT"
                else:
                    status = "UNSUPPORTED"
            else:
                status = "SUPPORTED"
            rows.append(
                {
                    "region": region,
                    "scenario_id": scenario,
                    "D_threshold": d85,
                    "H_threshold": h85,
                    "support_obs": support_obs,
                    "support_grids": support_grids,
                    "support_provinces": support_prov,
                    "nearest_distance_low_point": low_dist,
                    "nearest_distance_high_point": high_dist,
                    "support_status": status,
                    "eligible_for_main_text": 1 if status == "SUPPORTED" else 0,
                }
            )
    return pd.DataFrame(rows)


def surface_terms(D: float, H: float, d_spec: RcsSpec, h_spec: RcsSpec) -> dict[str, float]:
    return surface_basis(D, H, d_spec, h_spec).iloc[0].to_dict()


def region_design(region: str, D: float, H: float, sr: float, sr_center: float, d_spec: RcsSpec, h_spec: RcsSpec) -> dict[str, float]:
    b = surface_terms(D, H, d_spec, h_spec)
    out: dict[str, float] = {}
    sr_c = sr - sr_center
    for name, val in b.items():
        out[f"{region}:{name}"] = val
        out[f"{region}:SRc_x_{name}"] = sr_c * val
    out[f"{region}:SR_c"] = sr_c
    return out


def national_design(D: float, H: float, sr: float, sr_center: float, d_spec: RcsSpec, h_spec: RcsSpec) -> dict[str, float]:
    b = surface_terms(D, H, d_spec, h_spec)
    sr_c = sr - sr_center
    out = dict(b)
    out.update({f"SRc_x_{name}": sr_c * val for name, val in b.items()})
    out["SR_c"] = sr_c
    return out


def loss_vector(design_fn, z0: dict[str, float], z1: dict[str, float], sr: float) -> dict[str, float]:
    row0 = design_fn(z0["D0"], z0["H0"], sr)
    row1 = design_fn(z1["D1"], z1["H1"], sr)
    keys = set(row0) | set(row1)
    return {k: row1.get(k, 0.0) - row0.get(k, 0.0) for k in keys}


def buffering_vector(design_fn, z: dict[str, float], sr_from: float, sr_to: float) -> dict[str, float]:
    low = loss_vector(design_fn, z, z, sr_from)
    high = loss_vector(design_fn, z, z, sr_to)
    keys = set(low) | set(high)
    return {k: high.get(k, 0.0) - low.get(k, 0.0) for k in keys}


def contrast_to_row(
    model: FeModel,
    vector: dict[str, float],
    base: dict[str, object],
    support: dict[str, object],
) -> dict[str, object]:
    c = linear_contrast(model, vector)
    return {
        **base,
        "estimate_log": c["estimate_log"],
        "estimate_pct": float(pct(c["estimate_log"])),
        "se_log": c["se_log"],
        "ci_low_pct": float(pct(c["ci_low_log"])),
        "ci_high_pct": float(pct(c["ci_high_log"])),
        "p_value": c["p_value"],
        "q_value": math.nan,
        "inference_method": model.inference_method,
        "block_degrees": model.block_degrees if model.block_degrees is not None else "",
        "bootstrap_reps": model.bootstrap_reps,
        "N_obs": model.nobs,
        "N_grids": model.n_grids,
        "N_provinces": model.n_provinces,
        **support,
    }


def bh_adjust(p_values: pd.Series) -> pd.Series:
    p = p_values.astype(float).to_numpy()
    out = np.full(len(p), np.nan)
    valid = np.isfinite(p)
    if not valid.any():
        return pd.Series(out, index=p_values.index)
    idx = np.where(valid)[0]
    order = idx[np.argsort(p[idx])]
    ranked = p[order]
    m = len(ranked)
    adj = ranked * m / np.arange(1, m + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    out[order] = np.minimum(adj, 1.0)
    return pd.Series(out, index=p_values.index)


def wald_equal(model: FeModel, vectors: list[dict[str, float]]) -> tuple[float, int, float]:
    if len(vectors) < 2:
        return math.nan, 0, math.nan
    rows = []
    first = vectors[0]
    for other in vectors[1:]:
        diff = {k: other.get(k, 0.0) - first.get(k, 0.0) for k in set(first) | set(other)}
        rows.append([diff.get(name, 0.0) for name in model.xvars])
    R = np.asarray(rows, dtype=float)
    diff_beta = R @ model.beta
    cov = R @ model.covariance @ R.T
    rank = int(np.linalg.matrix_rank(cov))
    if rank == 0:
        return math.nan, 0, math.nan
    stat = float(diff_beta.T @ np.linalg.pinv(cov) @ diff_beta)
    from scipy.stats import chi2

    return stat, rank, float(chi2.sf(stat, rank))

