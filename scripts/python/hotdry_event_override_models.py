"""Fixed-effect yield-model utilities for the event override run."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass
class AbsorbedFit:
    beta: np.ndarray
    covariance_cluster: np.ndarray
    bootstrap_beta: np.ndarray
    residuals: np.ndarray
    rank: int
    condition_number: float
    absorption_iterations: int
    column_scale: np.ndarray


def _demean_inplace(values: np.ndarray, codes: np.ndarray, group_count: int) -> None:
    counts = np.bincount(codes, minlength=group_count).astype(float)
    sums = np.zeros((group_count, values.shape[1]), dtype=float)
    np.add.at(sums, codes, values)
    means = sums / counts[:, None]
    values -= means[codes]


def absorb_two_way(
    values: np.ndarray,
    first_codes: np.ndarray,
    second_codes: np.ndarray,
    *,
    tolerance: float = 1e-9,
    max_iterations: int = 500,
) -> tuple[np.ndarray, int]:
    """Alternating-projection absorption for two sets of fixed effects."""

    transformed = np.asarray(values, dtype=float).copy()
    first_codes = np.asarray(first_codes, dtype=int)
    second_codes = np.asarray(second_codes, dtype=int)
    if transformed.ndim != 2 or transformed.shape[0] != first_codes.size:
        raise ValueError("values and fixed-effect codes have incompatible shapes")
    first_count = int(first_codes.max()) + 1
    second_count = int(second_codes.max()) + 1
    for iteration in range(1, max_iterations + 1):
        previous = transformed.copy()
        _demean_inplace(transformed, first_codes, first_count)
        _demean_inplace(transformed, second_codes, second_count)
        if float(np.max(np.abs(transformed - previous))) <= tolerance:
            return transformed, iteration
    raise RuntimeError("two-way fixed-effect absorption did not converge")


def grouped_scores(x: np.ndarray, residuals: np.ndarray, codes: np.ndarray) -> np.ndarray:
    scores = np.zeros((int(codes.max()) + 1, x.shape[1]), dtype=float)
    np.add.at(scores, codes, x * residuals[:, None])
    return scores


def fit_absorbed_ols(
    y: np.ndarray,
    x: np.ndarray,
    *,
    grid_codes: np.ndarray,
    province_year_codes: np.ndarray,
    cluster_codes: np.ndarray,
    block_codes: np.ndarray,
    bootstrap_weights: np.ndarray,
) -> AbsorbedFit:
    """Fit OLS after two-way absorption with cluster and wild-score inference."""

    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    combined, iterations = absorb_two_way(
        np.column_stack([y, x]),
        np.asarray(grid_codes, dtype=int),
        np.asarray(province_year_codes, dtype=int),
    )
    yw = combined[:, 0]
    xw = combined[:, 1:]
    scale = np.sqrt(np.mean(xw**2, axis=0))
    if np.any(~np.isfinite(scale)) or np.any(scale <= 1e-12):
        bad = np.flatnonzero((~np.isfinite(scale)) | (scale <= 1e-12)).tolist()
        raise np.linalg.LinAlgError(f"absorbed design has zero columns: {bad}")
    xs = xw / scale
    rank = int(np.linalg.matrix_rank(xs))
    if rank != xs.shape[1]:
        raise np.linalg.LinAlgError(f"absorbed design rank {rank} != {xs.shape[1]}")
    condition = float(np.linalg.cond(xs))
    xtx_inverse = np.linalg.inv(xs.T @ xs)
    beta_scaled = xtx_inverse @ xs.T @ yw
    residuals = yw - xs @ beta_scaled

    cluster_scores = grouped_scores(xs, residuals, np.asarray(cluster_codes, dtype=int))
    cluster_count = cluster_scores.shape[0]
    n, k = xs.shape
    correction = (cluster_count / (cluster_count - 1)) * ((n - 1) / (n - k))
    covariance_scaled = correction * xtx_inverse @ (cluster_scores.T @ cluster_scores) @ xtx_inverse

    block_scores = grouped_scores(xs, residuals, np.asarray(block_codes, dtype=int))
    if bootstrap_weights.shape[1] != block_scores.shape[0]:
        raise ValueError("bootstrap block weights do not match block scores")
    bootstrap_scaled = beta_scaled[None, :] + (bootstrap_weights @ block_scores) @ xtx_inverse.T

    beta = beta_scaled / scale
    covariance = covariance_scaled / scale[:, None] / scale[None, :]
    bootstrap = bootstrap_scaled / scale[None, :]
    return AbsorbedFit(
        beta=beta,
        covariance_cluster=covariance,
        bootstrap_beta=bootstrap,
        residuals=residuals,
        rank=rank,
        condition_number=condition,
        absorption_iterations=iterations,
        column_scale=scale,
    )


def romano_wolf_stepdown(
    estimates: np.ndarray,
    bootstrap_draws: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return raw, Romano-Wolf stepdown, and Holm two-sided p-values."""

    estimates = np.asarray(estimates, dtype=float)
    draws = np.asarray(bootstrap_draws, dtype=float)
    centered = draws - estimates[None, :]
    se = centered.std(axis=0, ddof=1)
    observed = np.abs(estimates / se)
    sampled = np.abs(centered / se[None, :])
    reps, hypotheses = sampled.shape
    raw = (1 + (sampled >= observed[None, :]).sum(axis=0)) / (reps + 1)

    order = np.argsort(-observed)
    adjusted_sorted = np.empty(hypotheses, dtype=float)
    running = 0.0
    for position, hypothesis in enumerate(order):
        remaining = order[position:]
        maxima = sampled[:, remaining].max(axis=1)
        value = (1 + np.sum(maxima >= observed[hypothesis])) / (reps + 1)
        running = max(running, float(value))
        adjusted_sorted[position] = running
    adjusted = np.empty(hypotheses, dtype=float)
    adjusted[order] = np.minimum(adjusted_sorted, 1.0)

    holm_order = np.argsort(raw)
    holm_sorted = np.empty(hypotheses, dtype=float)
    running = 0.0
    for position, hypothesis in enumerate(holm_order):
        value = min(1.0, (hypotheses - position) * raw[hypothesis])
        running = max(running, float(value))
        holm_sorted[position] = running
    holm = np.empty(hypotheses, dtype=float)
    holm[holm_order] = holm_sorted
    return raw, adjusted, holm


def rademacher_weights(repetitions: int, blocks: int, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.choice(np.array([-1.0, 1.0]), size=(repetitions, blocks), replace=True)
