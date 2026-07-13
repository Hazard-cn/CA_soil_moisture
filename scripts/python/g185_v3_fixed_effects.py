"""Fixed-effect estimation and score-linearized inference for G185 v3."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import linalg
from scipy.stats import norm


@dataclass
class FeModel:
    model_id: str
    yvar: str
    xvars: list[str]
    beta: np.ndarray
    covariance: np.ndarray
    xtx_inv: np.ndarray
    scores: np.ndarray
    score_group_count: int
    nobs: int
    n_grids: int
    n_provinces: int
    fe_grid_count: int
    fe_time_count: int
    matrix_rank: int
    n_columns_before_drop: int
    n_columns_after_drop: int
    dropped_columns: dict[str, str]
    condition_number: float
    status: str
    formula_text: str
    boot_betas: np.ndarray | None = None
    bootstrap_reps: int = 0
    inference_method: str = "grid_cluster_sandwich"
    block_degrees: float | None = None


def factorize(values: pd.Series) -> np.ndarray:
    return pd.factorize(values, sort=True)[0].astype(np.int64)


def residualize(values: np.ndarray, groups: list[np.ndarray], max_iter: int = 200, tol: float = 1e-10) -> np.ndarray:
    r = np.asarray(values, dtype=float).copy()
    for _ in range(max_iter):
        previous = r.copy()
        for group in groups:
            n_group = int(group.max()) + 1
            count = np.bincount(group, minlength=n_group).astype(float)
            sums = np.vstack(
                [np.bincount(group, weights=r[:, col], minlength=n_group) for col in range(r.shape[1])]
            ).T
            r -= sums[group] / count[group, None]
        if float(np.max(np.abs(r - previous))) < tol:
            break
    return r


def _select_full_rank_columns(x: np.ndarray, names: list[str], tol: float = 1e-10) -> tuple[np.ndarray, list[str], dict[str, str], int, float]:
    norms = np.linalg.norm(x, axis=0)
    nonzero = np.where(norms > tol)[0]
    dropped: dict[str, str] = {names[i]: "near_zero_after_fe_absorption" for i in range(len(names)) if i not in set(nonzero)}
    if nonzero.size == 0:
        raise ValueError("all columns have near-zero norm after FE absorption")
    xnz = x[:, nonzero]
    q, r, piv = linalg.qr(xnz, mode="economic", pivoting=True)
    diag = np.abs(np.diag(r))
    threshold = max(xnz.shape) * np.finfo(float).eps * (diag[0] if diag.size else 1.0) * 100
    rank = int(np.sum(diag > max(tol, threshold)))
    keep_local = sorted(piv[:rank])
    keep_original = nonzero[keep_local]
    keep_set = set(int(i) for i in keep_original)
    for i in nonzero:
        if int(i) not in keep_set:
            dropped[names[int(i)]] = "linear_dependence_after_fe_absorption"
    kept_names = [names[int(i)] for i in keep_original]
    x_keep = x[:, keep_original]
    if x_keep.shape[1] == 0:
        raise ValueError("no full-rank columns retained")
    singular = np.linalg.svd(x_keep, compute_uv=False)
    condition = float(singular.max() / singular.min()) if singular.size and singular.min() > 0 else math.inf
    return x_keep, kept_names, dropped, rank, condition


def _cluster_covariance(x: np.ndarray, resid: np.ndarray, cluster: np.ndarray, xtx_inv: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n_clusters = int(cluster.max()) + 1
    scores = np.zeros((n_clusters, x.shape[1]), dtype=float)
    np.add.at(scores, cluster, x * resid[:, None])
    meat = scores.T @ scores
    n = x.shape[0]
    k = x.shape[1]
    correction = (n_clusters / max(n_clusters - 1, 1)) * ((n - 1) / max(n - k, 1))
    cov = correction * xtx_inv @ meat @ xtx_inv
    return cov, scores


def make_spatial_blocks(df: pd.DataFrame, degrees: float) -> np.ndarray:
    lat_block = np.floor((df["latitude"].to_numpy(dtype=float) + 90.0) / degrees).astype(int)
    lon_block = np.floor((df["longitude"].to_numpy(dtype=float) + 180.0) / degrees).astype(int)
    key = pd.MultiIndex.from_arrays([lat_block, lon_block])
    return pd.factorize(key, sort=True)[0].astype(np.int64)


def fit_fe_model(
    frame: pd.DataFrame,
    yvar: str,
    design: pd.DataFrame,
    model_id: str,
    fe_time_col: str,
    formula_text: str,
    inference: str = "grid_cluster_sandwich",
    block_degrees: float | None = None,
    bootstrap_reps: int = 0,
    seed: int = 20260620,
) -> FeModel:
    base_cols = [yvar, "grid_id", "province", fe_time_col]
    if block_degrees is not None:
        base_cols.extend(["latitude", "longitude"])
    base = frame.reset_index(drop=True).loc[:, list(dict.fromkeys(base_cols))]
    xdf = design.reset_index(drop=True).copy()
    work = pd.concat([base, xdf], axis=1).dropna().copy()
    y = work[yvar].to_numpy(dtype=float)
    x_start = len(base.columns)
    xraw = work.iloc[:, x_start : x_start + len(xdf.columns)].to_numpy(dtype=float)
    grid = factorize(work["grid_id"])
    time_fe = factorize(work[fe_time_col])
    z = residualize(np.column_stack([y, xraw]), [grid, time_fe])
    yr = z[:, 0]
    xr_full = z[:, 1:]
    xr, kept_names, dropped, rank, condition = _select_full_rank_columns(xr_full, list(design.columns))
    beta, *_ = np.linalg.lstsq(xr, yr, rcond=None)
    resid = yr - xr @ beta
    xtx_inv = np.linalg.pinv(xr.T @ xr)

    if block_degrees is not None:
        score_group = make_spatial_blocks(work, block_degrees)
        block_counts = int(score_group.max()) + 1
        scores = np.zeros((block_counts, xr.shape[1]), dtype=float)
        np.add.at(scores, score_group, xr * resid[:, None])
        meat = scores.T @ scores
        n = xr.shape[0]
        k = xr.shape[1]
        correction = (block_counts / max(block_counts - 1, 1)) * ((n - 1) / max(n - k, 1))
        covariance = correction * xtx_inv @ meat @ xtx_inv
        score_group_count = block_counts
        inference_method = f"{block_degrees:g}deg_spatial_block_wild_score_linearized"
    else:
        covariance, scores = _cluster_covariance(xr, resid, grid, xtx_inv)
        score_group_count = scores.shape[0]
        inference_method = inference

    boot_betas = None
    if bootstrap_reps > 0:
        rng = np.random.default_rng(seed)
        out = np.empty((bootstrap_reps, len(kept_names)), dtype=float)
        done = 0
        chunk = 500
        while done < bootstrap_reps:
            take = min(chunk, bootstrap_reps - done)
            weights = rng.choice(np.array([-1.0, 1.0]), size=(take, scores.shape[0]))
            out[done : done + take, :] = beta[None, :] + (weights @ scores) @ xtx_inv.T
            done += take
        boot_betas = out

    return FeModel(
        model_id=model_id,
        yvar=yvar,
        xvars=kept_names,
        beta=beta,
        covariance=covariance,
        xtx_inv=xtx_inv,
        scores=scores,
        score_group_count=score_group_count,
        nobs=int(len(work)),
        n_grids=int(work["grid_id"].nunique()),
        n_provinces=int(work["province"].nunique()),
        fe_grid_count=int(pd.Series(grid).nunique()),
        fe_time_count=int(pd.Series(time_fe).nunique()),
        matrix_rank=rank,
        n_columns_before_drop=int(len(design.columns)),
        n_columns_after_drop=int(len(kept_names)),
        dropped_columns=dropped,
        condition_number=condition,
        status="OK",
        formula_text=formula_text,
        boot_betas=boot_betas,
        bootstrap_reps=int(bootstrap_reps),
        inference_method=inference_method,
        block_degrees=block_degrees,
    )


def linear_contrast(model: FeModel, vector: pd.Series | dict[str, float]) -> dict[str, object]:
    v = np.array([float(vector.get(name, 0.0)) for name in model.xvars], dtype=float)
    est = float(v @ model.beta)
    var = float(v @ model.covariance @ v)
    se = math.sqrt(max(var, 0.0))
    p = float(2 * norm.sf(abs(est / se))) if se > 0 else math.nan
    if model.boot_betas is not None and len(model.boot_betas):
        draws = model.boot_betas @ v
        lo, hi = np.percentile(draws, [2.5, 97.5])
    else:
        lo, hi = est - 1.96 * se, est + 1.96 * se
    return {
        "estimate_log": est,
        "se_log": se,
        "ci_low_log": float(lo),
        "ci_high_log": float(hi),
        "p_value": p,
        "draws_log": None if model.boot_betas is None else (model.boot_betas @ v),
    }


def pct(log_value: float | np.ndarray) -> float | np.ndarray:
    return np.expm1(log_value) * 100.0
