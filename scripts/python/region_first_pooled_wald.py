"""Pooled region heterogeneity tests for the region-first candidate scales."""

from __future__ import annotations

import json
import math
import time
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2, norm

from expanded_scale_story_search import (
    add_full_interactions,
    load_panel,
    rhs_for,
    unique_variants,
)


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
OUT_DIR = PROJ / "temp/2026-06-11_region_first_story_search"
SAMPLE_IDS = ("G057", "G185")
REGIONS = ("NE", "HHH", "NW", "SW", "SH")
HAZARDS = ("drought", "heat", "hotdry")
HAZARD_VAR = {
    "drought": "D_full_raw",
    "heat": "hdd_ge32_raw",
    "hotdry": "HotDryPr_full_raw",
}


def residualize_two_way(
    values: np.ndarray,
    grid: np.ndarray,
    region_year: np.ndarray,
    max_iter: int = 100,
) -> np.ndarray:
    residual = values.astype(np.float64, copy=True)
    grid_count = np.bincount(grid).astype(np.float64)
    region_year_count = np.bincount(region_year).astype(np.float64)
    for _ in range(max_iter):
        previous = residual.copy()
        for group, count in (
            (grid, grid_count),
            (region_year, region_year_count),
        ):
            sums = np.vstack(
                [
                    np.bincount(
                        group,
                        weights=residual[:, column],
                        minlength=len(count),
                    )
                    for column in range(residual.shape[1])
                ]
            ).T
            residual -= sums[group] / count[group, None]
        if float(np.max(np.abs(residual - previous))) < 1e-10:
            break
    return residual


def fit_fully_interacted(
    frame: pd.DataFrame,
    yvar: str,
    xvars: list[str],
) -> tuple[np.ndarray, np.ndarray, list[str], int, int]:
    needed = [yvar, *xvars, "grid_id", "year", "maize_zone"]
    work = frame.loc[:, needed].dropna().copy()
    work = work.loc[work["maize_zone"].astype(str).isin(REGIONS)].copy()

    names: list[str] = []
    columns: list[np.ndarray] = []
    region_values = work["maize_zone"].astype(str).to_numpy()
    for region in REGIONS:
        indicator = region_values == region
        for xvar in xvars:
            names.append(f"{region}:{xvar}")
            columns.append(work[xvar].to_numpy(dtype=np.float64) * indicator)

    y = work[yvar].to_numpy(dtype=np.float64)
    x = np.column_stack(columns)
    grid = pd.factorize(work["grid_id"], sort=True)[0].astype(np.int64)
    region_year_index = pd.MultiIndex.from_arrays(
        [region_values, work["year"].to_numpy()]
    )
    region_year = pd.factorize(region_year_index, sort=True)[0].astype(
        np.int64
    )
    residualized = residualize_two_way(
        np.column_stack([y, x]),
        grid,
        region_year,
    )
    yr = residualized[:, 0]
    xr = residualized[:, 1:]
    beta, *_ = np.linalg.lstsq(xr, yr, rcond=None)
    error = yr - xr @ beta
    xtx_inv = np.linalg.pinv(xr.T @ xr)

    cluster_count = int(grid.max()) + 1
    score = np.zeros((cluster_count, xr.shape[1]), dtype=np.float64)
    np.add.at(score, grid, xr * error[:, None])
    meat = score.T @ score
    n = len(work)
    k = xr.shape[1]
    correction = (
        cluster_count / max(cluster_count - 1, 1)
    ) * ((n - 1) / max(n - k, 1))
    covariance = correction * xtx_inv @ meat @ xtx_inv
    return beta, covariance, names, n, cluster_count


def two_sided_p(estimate: float, variance: float) -> float:
    if variance <= 0:
        return math.nan
    return float(2 * norm.sf(abs(estimate / math.sqrt(variance))))


def estimate_scale(
    sample_id: str,
    sample: pd.DataFrame,
    hazard: str,
) -> tuple[list[dict[str, object]], dict[str, object], list[dict[str, object]]]:
    mediator = "gleam_smrz_mean_raw"
    yvar, _, _, rhs_y, _, target = rhs_for(hazard, "raw", mediator)
    beta, covariance, names, n, clusters = fit_fully_interacted(
        sample,
        yvar,
        rhs_y,
    )
    name_index = {name: index for index, name in enumerate(names)}

    complete = sample.loc[
        sample["maize_zone"].astype(str).isin(REGIONS),
        [yvar, *rhs_y, "maize_zone"],
    ].dropna()
    coefficients: list[dict[str, object]] = []
    target_indices: list[int] = []
    scale_factors: list[float] = []
    for region in REGIONS:
        region_complete = complete.loc[
            complete["maize_zone"].astype(str).eq(region)
        ]
        ca_iqr = float(
            region_complete["ca_raw"].quantile(0.75)
            - region_complete["ca_raw"].quantile(0.25)
        )
        hazard_p90 = float(
            region_complete[HAZARD_VAR[hazard]].quantile(0.90)
        )
        scale_factor = ca_iqr * hazard_p90
        index = name_index[f"{region}:{target}"]
        estimate = float(beta[index])
        variance = float(covariance[index, index])
        target_indices.append(index)
        scale_factors.append(scale_factor)
        coefficients.append(
            {
                "sample_id": sample_id,
                "hazard": hazard,
                "region": region,
                "c3": estimate,
                "c3_se": math.sqrt(max(variance, 0)),
                "c3_p": two_sided_p(estimate, variance),
                "ca_iqr": ca_iqr,
                "hazard_p90": hazard_p90,
                "scaled_buffer": estimate * scale_factor,
                "scaled_buffer_se": math.sqrt(max(variance, 0))
                * scale_factor,
                "N_model": n,
                "N_grids": clusters,
            }
        )

    target_beta = beta[target_indices]
    target_covariance = covariance[np.ix_(target_indices, target_indices)]
    scale_matrix = np.diag(scale_factors)
    scaled_beta = scale_matrix @ target_beta
    scaled_covariance = scale_matrix @ target_covariance @ scale_matrix

    restriction = np.zeros((len(REGIONS) - 1, len(REGIONS)))
    for row in range(len(REGIONS) - 1):
        restriction[row, 0] = -1
        restriction[row, row + 1] = 1
    difference = restriction @ scaled_beta
    restriction_covariance = (
        restriction @ scaled_covariance @ restriction.T
    )
    rank = int(np.linalg.matrix_rank(restriction_covariance))
    statistic = float(
        difference.T
        @ np.linalg.pinv(restriction_covariance)
        @ difference
    )
    omnibus = {
        "sample_id": sample_id,
        "hazard": hazard,
        "wald_chi2": statistic,
        "df": rank,
        "p_value": float(chi2.sf(statistic, rank)),
        "N_model": n,
        "N_grids": clusters,
    }

    pairwise: list[dict[str, object]] = []
    for left, right in combinations(range(len(REGIONS)), 2):
        contrast = np.zeros(len(REGIONS))
        contrast[left] = 1
        contrast[right] = -1
        estimate = float(contrast @ scaled_beta)
        variance = float(
            contrast @ scaled_covariance @ contrast
        )
        pairwise.append(
            {
                "sample_id": sample_id,
                "hazard": hazard,
                "left_region": REGIONS[left],
                "right_region": REGIONS[right],
                "difference": estimate,
                "se": math.sqrt(max(variance, 0)),
                "p_value": two_sided_p(estimate, variance),
            }
        )
    return coefficients, omnibus, pairwise


def main() -> None:
    np.random.seed(42)
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    panel = add_full_interactions(load_panel())
    variants = {
        str(variant["sample_id"]): variant
        for variant in unique_variants(panel)
    }

    coefficient_rows: list[dict[str, object]] = []
    omnibus_rows: list[dict[str, object]] = []
    pairwise_rows: list[dict[str, object]] = []
    for sample_id in SAMPLE_IDS:
        sample = panel.loc[variants[sample_id]["mask"]].copy()
        for hazard in HAZARDS:
            coefficients, omnibus, pairwise = estimate_scale(
                sample_id,
                sample,
                hazard,
            )
            coefficient_rows.extend(coefficients)
            omnibus_rows.append(omnibus)
            pairwise_rows.extend(pairwise)
            print(
                f"[POOLED_WALD] {sample_id} {hazard} "
                f"p={omnibus['p_value']:.6g}",
                flush=True,
            )

    pd.DataFrame(coefficient_rows).to_csv(
        OUT_DIR / "pooled_region_coefficients.csv",
        index=False,
    )
    pd.DataFrame(omnibus_rows).to_csv(
        OUT_DIR / "pooled_region_omnibus_wald.csv",
        index=False,
    )
    pd.DataFrame(pairwise_rows).to_csv(
        OUT_DIR / "pooled_region_pairwise_wald.csv",
        index=False,
    )
    manifest = {
        "sample_ids": list(SAMPLE_IDS),
        "regions": list(REGIONS),
        "hazards": list(HAZARDS),
        "fixed_effects": "grid and region-by-year",
        "standard_errors": "grid-clustered",
        "elapsed_seconds": time.time() - start,
    }
    (OUT_DIR / "pooled_region_wald_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
