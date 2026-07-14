"""Round-1 revision inference for separate, joint, Webb, and spatial-HAC models."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

from hotdry_event_override_models import absorb_two_way, grouped_scores


@dataclass
class RevisionFit:
    beta: np.ndarray
    covariance_cluster: np.ndarray
    bootstrap_beta: np.ndarray
    residuals: np.ndarray
    x_scaled: np.ndarray
    xtx_inverse: np.ndarray
    column_scale: np.ndarray
    grid_codes: np.ndarray
    block_codes: np.ndarray
    rank: int
    condition_number: float
    iterations: int


def fit_revision(
    y: np.ndarray,
    x: np.ndarray,
    grid_codes: np.ndarray,
    province_year_codes: np.ndarray,
    block_codes: np.ndarray,
    bootstrap_weights: np.ndarray,
) -> RevisionFit:
    combined, iterations = absorb_two_way(
        np.column_stack([y, x]), grid_codes, province_year_codes, tolerance=1e-9
    )
    yw, xw = combined[:, 0], combined[:, 1:]
    scale = np.sqrt(np.mean(xw**2, axis=0))
    if np.any(scale <= 1e-12):
        raise np.linalg.LinAlgError("zero absorbed column")
    xs = xw / scale
    rank = int(np.linalg.matrix_rank(xs))
    if rank != xs.shape[1]:
        raise np.linalg.LinAlgError(f"rank {rank}/{xs.shape[1]}")
    condition = float(np.linalg.cond(xs))
    inverse = np.linalg.inv(xs.T @ xs)
    beta_scaled = inverse @ xs.T @ yw
    residuals = yw - xs @ beta_scaled
    cluster_scores = grouped_scores(xs, residuals, grid_codes)
    n, k = xs.shape
    groups = cluster_scores.shape[0]
    correction = groups/(groups-1) * (n-1)/(n-k)
    cov_scaled = correction * inverse @ (cluster_scores.T @ cluster_scores) @ inverse
    block_scores = grouped_scores(xs, residuals, block_codes)
    draws_scaled = beta_scaled[None, :] + (bootstrap_weights @ block_scores) @ inverse.T
    return RevisionFit(
        beta=beta_scaled/scale,
        covariance_cluster=cov_scaled/scale[:,None]/scale[None,:],
        bootstrap_beta=draws_scaled/scale[None,:],
        residuals=residuals,
        x_scaled=xs,
        xtx_inverse=inverse,
        column_scale=scale,
        grid_codes=grid_codes,
        block_codes=block_codes,
        rank=rank,
        condition_number=condition,
        iterations=iterations,
    )


def webb_weights(repetitions: int, blocks: int, seed: int = 42) -> np.ndarray:
    values = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)])
    return np.random.default_rng(seed).choice(values, size=(repetitions, blocks), replace=True)


def spatial_hac_covariance(
    fit: RevisionFit,
    frame: pd.DataFrame,
    bandwidth_km: float,
) -> np.ndarray:
    scores = grouped_scores(fit.x_scaled, fit.residuals, fit.grid_codes)
    first = frame.groupby(fit.grid_codes, sort=True)[["latitude", "longitude"]].first()
    coordinates = np.radians(first[["latitude", "longitude"]].to_numpy(dtype=float))
    tree = BallTree(coordinates, metric="haversine")
    neighbors, distances = tree.query_radius(
        coordinates,
        r=bandwidth_km/6371.0088,
        return_distance=True,
        sort_results=False,
    )
    meat = np.zeros((scores.shape[1], scores.shape[1]), dtype=float)
    for index, (neighbor, distance) in enumerate(zip(neighbors, distances)):
        kernel = np.maximum(1.0 - distance * 6371.0088 / bandwidth_km, 0.0)
        weighted = (scores[neighbor] * kernel[:, None]).sum(axis=0)
        meat += np.outer(scores[index], weighted)
    cov_scaled = fit.xtx_inverse @ meat @ fit.xtx_inverse
    scale = fit.column_scale
    return cov_scaled / scale[:, None] / scale[None, :]


def vif_pair(left: np.ndarray, right: np.ndarray) -> float:
    correlation = float(np.corrcoef(left, right)[0, 1])
    return float(1.0 / (1.0 - correlation**2))
