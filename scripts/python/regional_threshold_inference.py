"""Spatial and multiple-testing inference for regional threshold contrasts."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from scipy.spatial import cKDTree


EARTH_RADIUS_KM = 6_371.0088


def spatial_block_labels(latitude: pd.Series, longitude: pd.Series, degrees: float = 2.0) -> np.ndarray:
    """Stable 2-degree block labels based on geographic coordinates."""

    lat_block = np.floor((latitude.to_numpy(dtype=float) + 90.0) / degrees).astype(int)
    lon_block = np.floor((longitude.to_numpy(dtype=float) + 180.0) / degrees).astype(int)
    return np.asarray([f"{lat}:{lon}" for lat, lon in zip(lat_block, lon_block, strict=True)])


def contrast_vector(names: list[str], weights: Mapping[str, float]) -> np.ndarray:
    vector = np.zeros(len(names), dtype=float)
    for name, value in weights.items():
        vector[names.index(name)] = float(value)
    return vector


def block_score_contributions(
    fit: Any,
    block_labels: np.ndarray,
    contrasts: Mapping[str, Mapping[str, float]],
) -> pd.DataFrame:
    """Linearized wild-bootstrap contributions by spatial block."""

    x = np.asarray(fit.model.exog, dtype=float)
    residual = np.asarray(fit.resid, dtype=float)
    names = list(fit.model.data.xnames)
    if len(block_labels) != len(residual):
        raise ValueError("spatial block labels do not match model observations")
    unique_blocks, block_codes = np.unique(block_labels, return_inverse=True)
    bread = np.linalg.inv(x.T @ x)
    result: dict[str, np.ndarray] = {}
    for label, weights in contrasts.items():
        c = contrast_vector(names, weights)
        observation_influence = (x @ (bread @ c)) * residual
        result[label] = np.bincount(
            block_codes, weights=observation_influence, minlength=len(unique_blocks)
        )
    return pd.DataFrame(result, index=unique_blocks)


def holm_adjust(pvalues: np.ndarray) -> np.ndarray:
    p = np.asarray(pvalues, dtype=float)
    order = np.argsort(p)
    adjusted = np.empty_like(p)
    running = 0.0
    m = len(p)
    for rank, index in enumerate(order):
        running = max(running, (m - rank) * p[index])
        adjusted[index] = min(running, 1.0)
    return adjusted


def romano_wolf_stepdown(
    estimates: np.ndarray,
    centered_draws: np.ndarray,
    standard_errors: np.ndarray,
) -> np.ndarray:
    """Romano-Wolf stepdown using joint multiplier-bootstrap t statistics."""

    estimates = np.asarray(estimates, dtype=float)
    draws = np.asarray(centered_draws, dtype=float)
    se = np.asarray(standard_errors, dtype=float)
    if draws.shape[1] != estimates.size or se.size != estimates.size:
        raise ValueError("bootstrap arrays have incompatible shapes")
    observed = np.abs(estimates / se)
    bootstrap_t = np.abs(draws / se[None, :])
    order = np.argsort(-observed)
    adjusted = np.empty_like(observed)
    previous = 0.0
    remaining = list(order)
    for index in order:
        maximum = bootstrap_t[:, remaining].max(axis=1)
        raw = (1.0 + float((maximum >= observed[index]).sum())) / (draws.shape[0] + 1.0)
        previous = max(previous, raw)
        adjusted[index] = min(previous, 1.0)
        remaining.remove(index)
    return adjusted


def joint_wild_bootstrap(
    contributions: pd.DataFrame,
    estimates: pd.Series,
    *,
    reps: int = 1_999,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run a joint Rademacher 2-degree block multiplier bootstrap."""

    labels = list(contributions.columns)
    estimates = estimates.reindex(labels)
    if estimates.isna().any():
        raise ValueError("estimate labels do not align with contribution labels")
    rng = np.random.default_rng(seed)
    weights = rng.choice(np.array([-1.0, 1.0]), size=(reps, len(contributions)))
    centered = weights @ contributions.to_numpy(dtype=float)
    boot_se = centered.std(axis=0, ddof=1)
    if (boot_se <= 0).any():
        raise ValueError("wild bootstrap produced a zero standard error")
    estimate_values = estimates.to_numpy(dtype=float)
    p_unadjusted = np.asarray(
        [
            (1.0 + float((np.abs(centered[:, j]) >= abs(estimate_values[j])).sum())) / (reps + 1.0)
            for j in range(len(labels))
        ]
    )
    ci_low = estimate_values + np.quantile(centered, 0.025, axis=0)
    ci_high = estimate_values + np.quantile(centered, 0.975, axis=0)
    romano = romano_wolf_stepdown(estimate_values, centered, boot_se)
    holm = holm_adjust(p_unadjusted)
    results = pd.DataFrame(
        {
            "contrast_id": labels,
            "estimate": estimate_values,
            "wild_bootstrap_se": boot_se,
            "wild_bootstrap_ci_low": ci_low,
            "wild_bootstrap_ci_high": ci_high,
            "wild_bootstrap_p": p_unadjusted,
            "romano_wolf_p": romano,
            "holm_p": holm,
            "bootstrap_reps": reps,
            "seed": seed,
            "spatial_block_degrees": 2.0,
            "n_spatial_blocks": len(contributions),
        }
    )
    covariance = pd.DataFrame(
        np.cov(centered, rowvar=False, ddof=1), index=labels, columns=labels
    )
    draws = pd.DataFrame(centered, columns=labels)
    draws.insert(0, "bootstrap_rep", np.arange(1, reps + 1))
    return results, covariance, draws


def _unit_sphere(latitude: np.ndarray, longitude: np.ndarray) -> np.ndarray:
    lat = np.radians(latitude)
    lon = np.radians(longitude)
    return np.column_stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])


def _haversine_km(
    lat1: np.ndarray, lon1: np.ndarray, lat2: np.ndarray, lon2: np.ndarray
) -> np.ndarray:
    lat1r, lon1r, lat2r, lon2r = map(np.radians, [lat1, lon1, lat2, lon2])
    a = np.sin((lat2r - lat1r) / 2.0) ** 2 + np.cos(lat1r) * np.cos(lat2r) * np.sin(
        (lon2r - lon1r) / 2.0
    ) ** 2
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.minimum(1.0, np.sqrt(a)))


def spatial_hac_covariance(
    fit: Any,
    frame: pd.DataFrame,
    bandwidth_km: float,
    *,
    pair_batch_size: int = 200_000,
) -> tuple[np.ndarray, dict[str, int | float]]:
    """Conley-type HAC: within-year Bartlett spatial kernel plus grid serial pairs."""

    x = np.asarray(fit.model.exog, dtype=float)
    residual = np.asarray(fit.resid, dtype=float)
    if len(frame) != len(residual):
        raise ValueError("HAC frame does not match model observations")
    score = x * residual[:, None]
    meat = score.T @ score
    spatial_pairs = 0
    chord = 2.0 * np.sin((bandwidth_km / EARTH_RADIUS_KM) / 2.0)
    latitude = frame["latitude"].to_numpy(dtype=float)
    longitude = frame["longitude"].to_numpy(dtype=float)
    years = frame["year"].to_numpy(dtype=int)
    for year in np.unique(years):
        indices = np.flatnonzero(years == year)
        tree = cKDTree(_unit_sphere(latitude[indices], longitude[indices]))
        local_pairs = tree.query_pairs(chord, output_type="ndarray")
        if local_pairs.size == 0:
            continue
        left = indices[local_pairs[:, 0]]
        right = indices[local_pairs[:, 1]]
        distance = _haversine_km(
            latitude[left], longitude[left], latitude[right], longitude[right]
        )
        keep = distance <= bandwidth_km
        left, right, distance = left[keep], right[keep], distance[keep]
        spatial_pairs += len(left)
        for start in range(0, len(left), pair_batch_size):
            stop = min(start + pair_batch_size, len(left))
            li, ri = left[start:stop], right[start:stop]
            weight = 1.0 - distance[start:stop] / bandwidth_km
            meat += score[li].T @ (weight[:, None] * score[ri])
            meat += score[ri].T @ (weight[:, None] * score[li])

    serial_pairs = 0
    grid_groups = frame.groupby("grid_id", sort=False).indices
    for indices_list in grid_groups.values():
        indices = np.asarray(indices_list, dtype=int)
        if len(indices) < 2:
            continue
        left, right = np.triu_indices(len(indices), k=1)
        li, ri = indices[left], indices[right]
        serial_pairs += len(li)
        meat += score[li].T @ score[ri]
        meat += score[ri].T @ score[li]

    bread = np.linalg.inv(x.T @ x)
    correction = len(frame) / max(len(frame) - x.shape[1], 1)
    covariance = correction * bread @ meat @ bread
    covariance = (covariance + covariance.T) / 2.0
    return covariance, {
        "bandwidth_km": float(bandwidth_km),
        "spatial_pairs": spatial_pairs,
        "serial_grid_pairs": serial_pairs,
        "nobs": len(frame),
        "parameters": x.shape[1],
    }


def spatial_hac_covariances(
    fit: Any,
    frame: pd.DataFrame,
    bandwidths_km: tuple[float, ...] = (100.0, 200.0, 300.0),
    *,
    pair_batch_size: int = 200_000,
) -> tuple[dict[float, np.ndarray], list[dict[str, int | float]]]:
    """Compute several Conley bandwidths while reusing the maximum-distance pairs."""

    bandwidths = tuple(sorted(float(value) for value in bandwidths_km))
    maximum_bandwidth = bandwidths[-1]
    x = np.asarray(fit.model.exog, dtype=float)
    residual = np.asarray(fit.resid, dtype=float)
    if len(frame) != len(residual):
        raise ValueError("HAC frame does not match model observations")
    score = x * residual[:, None]
    meats = {bandwidth: score.T @ score for bandwidth in bandwidths}
    pair_counts = {bandwidth: 0 for bandwidth in bandwidths}
    chord = 2.0 * np.sin((maximum_bandwidth / EARTH_RADIUS_KM) / 2.0)
    latitude = frame["latitude"].to_numpy(dtype=float)
    longitude = frame["longitude"].to_numpy(dtype=float)
    years = frame["year"].to_numpy(dtype=int)
    for year in np.unique(years):
        indices = np.flatnonzero(years == year)
        tree = cKDTree(_unit_sphere(latitude[indices], longitude[indices]))
        local_pairs = tree.query_pairs(chord, output_type="ndarray")
        if local_pairs.size == 0:
            continue
        left = indices[local_pairs[:, 0]]
        right = indices[local_pairs[:, 1]]
        distance = _haversine_km(latitude[left], longitude[left], latitude[right], longitude[right])
        for start in range(0, len(left), pair_batch_size):
            stop = min(start + pair_batch_size, len(left))
            li, ri = left[start:stop], right[start:stop]
            dist = distance[start:stop]
            for bandwidth in bandwidths:
                keep = dist <= bandwidth
                if not keep.any():
                    continue
                pair_counts[bandwidth] += int(keep.sum())
                weight = 1.0 - dist[keep] / bandwidth
                lkeep, rkeep = li[keep], ri[keep]
                meats[bandwidth] += score[lkeep].T @ (weight[:, None] * score[rkeep])
                meats[bandwidth] += score[rkeep].T @ (weight[:, None] * score[lkeep])

    serial_pairs = 0
    serial_meat = np.zeros_like(next(iter(meats.values())))
    for indices_list in frame.groupby("grid_id", sort=False).indices.values():
        indices = np.asarray(indices_list, dtype=int)
        if len(indices) < 2:
            continue
        left, right = np.triu_indices(len(indices), k=1)
        li, ri = indices[left], indices[right]
        serial_pairs += len(li)
        serial_meat += score[li].T @ score[ri]
        serial_meat += score[ri].T @ score[li]

    bread = np.linalg.inv(x.T @ x)
    correction = len(frame) / max(len(frame) - x.shape[1], 1)
    covariances: dict[float, np.ndarray] = {}
    diagnostics: list[dict[str, int | float]] = []
    for bandwidth in bandwidths:
        covariance = correction * bread @ (meats[bandwidth] + serial_meat) @ bread
        covariance = (covariance + covariance.T) / 2.0
        covariances[bandwidth] = covariance
        diagnostics.append(
            {
                "bandwidth_km": bandwidth,
                "spatial_pairs": pair_counts[bandwidth],
                "serial_grid_pairs": serial_pairs,
                "nobs": len(frame),
                "parameters": x.shape[1],
            }
        )
    return covariances, diagnostics


def contrast_from_covariance(
    fit: Any, covariance: np.ndarray, weights: Mapping[str, float]
) -> dict[str, float]:
    vector = contrast_vector(list(fit.model.data.xnames), weights)
    estimate = float(vector @ np.asarray(fit.params))
    se = float(np.sqrt(max(vector @ covariance @ vector, 0.0)))
    pvalue = float(2.0 * stats.norm.sf(abs(estimate / se))) if se > 0 else float(estimate != 0)
    return {
        "estimate": estimate,
        "se": se,
        "ci_low": estimate - 1.96 * se,
        "ci_high": estimate + 1.96 * se,
        "p": pvalue,
    }
