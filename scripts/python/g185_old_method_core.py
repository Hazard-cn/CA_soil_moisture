"""Pure numerical and data-contract functions for the G185 old-method pipeline.

This module has no import-time filesystem effects.  It reimplements the frozen
G185 sample predicate and the linear two-equation estimator without importing
legacy modules that contain project-root paths or write side effects.

Frozen source contracts (2026-07-14 design v2):
* GGCP10 base SHA-256: 03a36e25ed5375d055c7dc58e0b3b7b237ab4b16b9ce89e61f1b1b7fc3dcbaaa
* V3 hot-dry SHA-256: 3f3f045a8040b876565873febab3918d166b8bd6f6938669b48c634a46172517
* legacy sample-key serializer: legacy-sample-key-pipe-v1
* canonical secondary serializer: sample-key-csv-v1

All IE/DE/TE quantities returned here are algebraic two-equation components,
not identified causal mediation effects.
"""

from __future__ import annotations

import csv
import hashlib
import io
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


EXPECTED_BASE_SHA256 = "03a36e25ed5375d055c7dc58e0b3b7b237ab4b16b9ce89e61f1b1b7fc3dcbaaa"
EXPECTED_HOTDRY_SHA256 = "3f3f045a8040b876565873febab3918d166b8bd6f6938669b48c634a46172517"
EXPECTED_LEGACY_SAMPLE_KEY_SHA256 = "5474250d140bef9a8fc0957158ed815f635220e0c0df7080d7a1b5f7d4469b89"
EXPECTED_CANONICAL_SAMPLE_KEY_SHA256 = "36029c5f8ba689a1cbf6a14b688e8a43342ab8b7acd9b704136cb152fa170bcb"
LEGACY_SERIALIZER_VERSION = "legacy-sample-key-pipe-v1"
CANONICAL_SERIALIZER_VERSION = "sample-key-csv-v1"

REGIONS = ("NE", "HHH", "NW", "SW", "SH")
HAZARDS = ("drought", "heat", "hotdry")
TEST_ORDER = tuple((region, hazard) for region in REGIONS for hazard in HAZARDS)
HAC_BANDWIDTHS_KM = (100.0, 200.0, 300.0)

BASE_COLUMNS = (
    "grid_id",
    "year",
    "latitude",
    "longitude",
    "main_sample",
    "province",
    "maize_zone",
    "ggcp10_maize_frac",
    "yield_tons_ha",
    "ln_yield",
    "ca",
    "D_full",
    "W_full",
    "hdd_ge32",
    "pr_sum",
    "et0_sum",
    "gdd_10_30",
    "irr_frac",
    "aridity",
    "gleam_smrz_mean",
    "gleam_smrz_sd",
    "spei6_mean",
)

CONTROL_VARS = (
    "pr_sum_raw",
    "et0_sum_raw",
    "gdd_10_30_raw",
    "irr_frac_raw",
    "aridity_raw",
)


@dataclass(frozen=True)
class HazardSpec:
    hazard: str
    hazard_var: str
    main: str
    interaction: str
    mediator_rhs: tuple[str, ...]
    yield_rhs: tuple[str, ...]


@dataclass
class AbsorbedFit:
    yvar: str
    xvars: tuple[str, ...]
    beta: np.ndarray
    bread: np.ndarray
    residual: np.ndarray
    absorbed_x: np.ndarray
    grid_labels: np.ndarray
    cluster_labels: np.ndarray
    cluster_scores: np.ndarray
    nobs: int
    k: int
    rank: int
    singleton_grids: int
    zero_norm_rows: int
    max_abs_group_mean: float


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_grid_id(value: object) -> str:
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)) and np.isfinite(value) and float(value).is_integer():
        return str(int(value))
    return str(value)


def serialize_sample_keys(keys: pd.DataFrame) -> bytes:
    """Serialize grid_id/year according to the frozen sample-key-csv-v1 contract."""
    if list(keys.columns) != ["grid_id", "year"]:
        raise ValueError("sample keys must contain exactly grid_id,year in that order")
    work = keys.copy()
    if work.isna().any().any():
        raise ValueError("sample keys contain missing values")
    work["grid_id"] = work["grid_id"].map(_canonical_grid_id)
    years = pd.to_numeric(work["year"], errors="raise")
    if not np.all(np.isfinite(years)) or not np.all(np.equal(years, np.floor(years))):
        raise ValueError("year must be a finite integer")
    work["year"] = years.astype(np.int64).map(lambda value: f"{value:04d}")
    work.sort_values(["grid_id", "year"], kind="stable", inplace=True)
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter=",", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(("grid_id", "year"))
    writer.writerows(work.itertuples(index=False, name=None))
    return buffer.getvalue().encode("utf-8")


def sample_key_sha256(keys: pd.DataFrame) -> str:
    return hashlib.sha256(serialize_sample_keys(keys)).hexdigest()


def legacy_sample_key_sha256(keys: pd.DataFrame) -> str:
    """Reproduce the historical G185 key digest exactly.

    The legacy contract sorts numeric grid_id/year, joins each row as
    ``grid_id|year`` with LF, and has no header or terminal LF.
    """
    if list(keys.columns) != ["grid_id", "year"]:
        raise ValueError("legacy sample keys must contain exactly grid_id,year in that order")
    work = keys.copy()
    if work.isna().any().any():
        raise ValueError("legacy sample keys contain missing values")
    grid_numeric = pd.to_numeric(work["grid_id"], errors="raise")
    year_numeric = pd.to_numeric(work["year"], errors="raise")
    if not np.all(np.equal(grid_numeric, np.floor(grid_numeric))):
        raise ValueError("legacy grid_id must be integer-valued")
    if not np.all(np.equal(year_numeric, np.floor(year_numeric))):
        raise ValueError("legacy year must be integer-valued")
    work["grid_id"] = grid_numeric.astype(np.int64)
    work["year"] = year_numeric.astype(np.int64)
    work.sort_values(["grid_id", "year"], kind="stable", inplace=True)
    payload = "\n".join(
        work["grid_id"].astype(str) + "|" + work["year"].astype(str)
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def ensure_new_output_dir(worktree_root: Path, output_dir: Path) -> Path:
    """Create a new output path strictly below worktree/temp, rejecting links."""
    worktree_root = worktree_root.resolve(strict=True)
    temp_candidate = worktree_root / "temp"
    if not temp_candidate.exists():
        attrs = getattr(worktree_root.stat(), "st_file_attributes", 0)
        if worktree_root.is_symlink() or attrs & 0x400:
            raise ValueError(f"worktree root is a symlink/reparse point: {worktree_root}")
        temp_candidate.mkdir(exist_ok=False)
    temp_root = temp_candidate.resolve(strict=True)
    requested = Path(os.path.abspath(output_dir))
    if requested.exists():
        raise FileExistsError(f"output directory already exists: {requested}")
    if os.path.commonpath((str(temp_root), str(requested))) != str(temp_root) or requested == temp_root:
        raise ValueError("output directory must be a strict descendant of worktree/temp")
    current = requested.parent
    ancestors: list[Path] = []
    while True:
        ancestors.append(current)
        if current == temp_root:
            break
        if current.parent == current:
            raise ValueError("output path escapes worktree/temp")
        current = current.parent
    for ancestor in ancestors:
        if ancestor.exists() and ancestor.is_symlink():
            raise ValueError(f"symlink/reparse ancestor rejected: {ancestor}")
        if ancestor.exists():
            attrs = getattr(ancestor.stat(), "st_file_attributes", 0)
            if attrs & 0x400:  # FILE_ATTRIBUTE_REPARSE_POINT
                raise ValueError(f"symlink/reparse ancestor rejected: {ancestor}")
    requested.mkdir(parents=False, exist_ok=False)
    resolved = requested.resolve(strict=True)
    if os.path.commonpath((str(temp_root), str(resolved))) != str(temp_root) or resolved == temp_root:
        raise ValueError("created output directory failed strict-descendant check")
    return resolved


def apply_g185_predicate(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Apply the frozen G185 rules mechanically and return waterfall counts."""
    required = {
        "grid_id",
        "year",
        "ggcp10_maize_frac",
        "main_sample",
        "yield_tons_ha",
        "ln_yield",
        "gleam_smrz_sd",
    }
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise KeyError(f"missing predicate columns: {missing}")
    work = frame.sort_values(["grid_id", "year"], kind="stable").copy()
    counts: dict[str, int] = {"input": int(len(work))}
    mask = work["ggcp10_maize_frac"].ge(0.05)
    counts["ggcp10_maize_frac_ge_0p05"] = int(mask.sum())
    mask &= work["main_sample"].eq(1)
    counts["main_sample_eq_1"] = int(mask.sum())
    mask &= work["yield_tons_ha"].ge(0.5) & work["yield_tons_ha"].lt(18.0)
    counts["yield_domain"] = int(mask.sum())

    same_prev = work["grid_id"].eq(work["grid_id"].shift()) & work["year"].eq(work["year"].shift() + 1)
    same_next = work["grid_id"].eq(work["grid_id"].shift(-1)) & work["year"].shift(-1).eq(work["year"] + 1)
    prev_jump = (work["ln_yield"] - work["ln_yield"].shift()).abs().gt(1) & same_prev
    next_jump = (work["ln_yield"].shift(-1) - work["ln_yield"]).abs().gt(1) & same_next
    mask &= ~(prev_jump | next_jump)
    counts["yield_jump"] = int(mask.sum())
    mask &= work["gleam_smrz_sd"].ge(0.001)
    counts["sm_sd"] = int(mask.sum())
    return work.loc[mask].copy(), counts


def hazard_spec(hazard: str) -> HazardSpec:
    controls = CONTROL_VARS
    mediator = "gleam_smrz_mean_raw"
    if hazard == "drought":
        main, inter = "D_full_raw", "SR_x_D_full_raw"
        rhs_m = (main, "ca_raw", inter, "W_full_raw", "hdd_ge32_raw", *controls)
        rhs_y = (main, "ca_raw", inter, mediator, "W_full_raw", "hdd_ge32_raw", *controls)
    elif hazard == "heat":
        main, inter = "hdd_ge32_raw", "SR_x_Heat_full_raw"
        rhs_m = (main, "ca_raw", inter, "D_full_raw", "W_full_raw", *controls)
        rhs_y = (main, "ca_raw", inter, mediator, "D_full_raw", "W_full_raw", *controls)
    elif hazard == "hotdry":
        main, inter = "HotDryPr_full_raw", "SR_x_HotDryPr_full_raw"
        rhs_m = (main, "ca_raw", inter, "D_full_raw", "hdd_ge32_raw", "W_full_raw", *controls)
        rhs_y = (main, "ca_raw", inter, mediator, "D_full_raw", "hdd_ge32_raw", "W_full_raw", *controls)
    else:
        raise ValueError(f"unknown hazard: {hazard}")
    return HazardSpec(hazard, main, main, inter, tuple(rhs_m), tuple(rhs_y))


def prepare_analysis_columns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    raw_names = (
        "ln_yield",
        "ca",
        "D_full",
        "W_full",
        "hdd_ge32",
        "HotDryPr_full",
        "pr_sum",
        "et0_sum",
        "gdd_10_30",
        "irr_frac",
        "aridity",
        "gleam_smrz_mean",
    )
    for name in raw_names:
        out[f"{name}_raw"] = out[name]
    out["SR_x_D_full_raw"] = out["ca_raw"] * out["D_full_raw"]
    out["SR_x_Heat_full_raw"] = out["ca_raw"] * out["hdd_ge32_raw"]
    out["SR_x_HotDryPr_full_raw"] = out["ca_raw"] * out["HotDryPr_full_raw"]
    out["province_norm"] = out["province"].astype("string").str.strip()
    if out["province_norm"].isna().any() or out["province_norm"].eq("").any():
        raise AssertionError("province contains missing or empty values")
    out["province_year_key"] = out["province_norm"] + "|" + out["year"].astype(int).map(lambda x: f"{x:04d}")
    out["block_lon"] = np.floor((out["longitude"].astype(float) + 180.0) / 2.0).astype(np.int64)
    out["block_lat"] = np.floor((out["latitude"].astype(float) + 90.0) / 2.0).astype(np.int64)
    out["spatial_block"] = out["block_lon"].astype(str) + ":" + out["block_lat"].astype(str)
    return out


def assert_frozen_sample(sample: pd.DataFrame) -> dict[str, object]:
    named = sample.loc[sample["maize_zone"].astype(str).isin(REGIONS)]
    checks = {
        "rows": int(len(sample)),
        "grids": int(sample["grid_id"].nunique()),
        "named_rows": int(len(named)),
        "named_grids": int(named["grid_id"].nunique()),
        "province_year_groups": int(sample["province_year_key"].nunique()),
        "all_spatial_blocks": int(sample["spatial_block"].nunique()),
        "named_spatial_blocks": int(named["spatial_block"].nunique()),
        "model_cells": int(len(REGIONS) * len(HAZARDS)),
    }
    expected = {
        "rows": 46299,
        "grids": 13236,
        "named_rows": 44556,
        "named_grids": 12745,
        "province_year_groups": 87,
        "all_spatial_blocks": 151,
        "named_spatial_blocks": 149,
        "model_cells": 15,
    }
    if checks != expected:
        raise AssertionError(f"frozen sample assertion failed: got={checks}, expected={expected}")
    return checks


def validate_drought_wet_definitions(frame: pd.DataFrame, tolerance: float = 1e-6) -> dict[str, float]:
    spei = frame["spei6_mean"].to_numpy(dtype=float)
    d = frame["D_full"].to_numpy(dtype=float)
    w = frame["W_full"].to_numpy(dtype=float)
    d_err = float(np.nanmax(np.abs(d - np.maximum(0.0, -spei))))
    w_err = float(np.nanmax(np.abs(w - np.maximum(0.0, spei))))
    if d_err > tolerance or w_err > tolerance:
        raise AssertionError(f"D/W formula mismatch: drought={d_err}, wet={w_err}")
    return {"D_full_max_abs_error": d_err, "W_full_max_abs_error": w_err}


def select_smoke_panel(named: pd.DataFrame, grids_per_region: int) -> pd.DataFrame:
    """Select an evenly-spaced deterministic grid subset, independent of outcomes."""
    selected: list[object] = []
    for region in REGIONS:
        grids = np.array(sorted(named.loc[named["maize_zone"].astype(str).eq(region), "grid_id"].unique()))
        if len(grids) < grids_per_region:
            raise AssertionError(f"insufficient grids for smoke region {region}")
        indices = np.linspace(0, len(grids) - 1, grids_per_region, dtype=int)
        selected.extend(grids[indices].tolist())
    smoke = named.loc[named["grid_id"].isin(selected)].copy()
    if smoke["grid_id"].nunique() != grids_per_region * len(REGIONS):
        raise AssertionError("smoke grid selection is not unique across regions")
    return smoke


def factorize_stable(values: Iterable[object]) -> tuple[np.ndarray, np.ndarray]:
    codes, labels = pd.factorize(pd.Series(values), sort=True)
    if np.any(codes < 0):
        raise ValueError("fixed-effect or cluster key contains missing values")
    return codes.astype(np.int64), np.asarray(labels)


def _group_means(matrix: np.ndarray, codes: np.ndarray, n_groups: int) -> np.ndarray:
    counts = np.bincount(codes, minlength=n_groups).astype(float)
    sums = np.vstack(
        [np.bincount(codes, weights=matrix[:, col], minlength=n_groups) for col in range(matrix.shape[1])]
    ).T
    return sums / counts[:, None]


def absorb_fixed_effects(
    matrix: np.ndarray,
    groups: Sequence[np.ndarray],
    tolerance: float = 1e-10,
    max_iter: int = 2000,
) -> tuple[np.ndarray, float, int]:
    """Absorb multiple additive fixed effects by alternating projections."""
    residual = np.asarray(matrix, dtype=float).copy()
    normalized: list[tuple[np.ndarray, int]] = []
    for group in groups:
        codes, _ = factorize_stable(group)
        normalized.append((codes, int(codes.max()) + 1))
    max_mean = math.inf
    for iteration in range(1, max_iter + 1):
        for codes, n_groups in normalized:
            means = _group_means(residual, codes, n_groups)
            residual -= means[codes]
        max_mean = 0.0
        for codes, n_groups in normalized:
            max_mean = max(max_mean, float(np.max(np.abs(_group_means(residual, codes, n_groups)))))
        if max_mean < tolerance:
            return residual, max_mean, iteration
    raise RuntimeError(f"fixed-effect absorption did not converge: max_group_mean={max_mean}")


def fit_absorbed_model(
    frame: pd.DataFrame,
    yvar: str,
    xvars: Sequence[str],
    fe: str,
    score_cluster: str,
) -> tuple[AbsorbedFit, pd.DataFrame]:
    required = [
        yvar,
        *xvars,
        "grid_id",
        "year",
        "province_year_key",
        "spatial_block",
        "latitude",
        "longitude",
    ]
    work = frame.loc[:, list(dict.fromkeys(required))].dropna().copy()
    if work.empty:
        raise ValueError("complete-case sample is empty")
    grid_codes, _ = factorize_stable(work["grid_id"])
    if fe == "grid_year":
        second_fe = work["year"].to_numpy()
    elif fe == "grid_provyear":
        second_fe = work["province_year_key"].to_numpy()
    else:
        raise ValueError(f"unsupported fixed effects: {fe}")
    matrix = work[[yvar, *xvars]].to_numpy(dtype=float)
    absorbed, max_mean, _ = absorb_fixed_effects(matrix, (work["grid_id"].to_numpy(), second_fe))
    y = absorbed[:, 0]
    x = absorbed[:, 1:]
    column_norm = np.linalg.norm(x, axis=0)
    if np.any(column_norm <= 1e-12):
        bad = [name for name, norm in zip(xvars, column_norm, strict=True) if norm <= 1e-12]
        raise RuntimeError(f"RHS absorbed to zero: {bad}")
    rank = int(np.linalg.matrix_rank(x))
    if rank != len(xvars):
        raise RuntimeError(f"absorbed design rank deficient: rank={rank}, K={len(xvars)}")
    xtx = x.T @ x
    bread = np.linalg.inv(xtx)
    beta = bread @ (x.T @ y)
    residual = y - x @ beta
    cluster_values = work["grid_id"] if score_cluster == "grid" else work["spatial_block"]
    cluster_codes, cluster_labels = factorize_stable(cluster_values)
    scores = np.zeros((len(cluster_labels), len(xvars)), dtype=float)
    np.add.at(scores, cluster_codes, x * residual[:, None])
    grid_counts = np.bincount(grid_codes)
    zero_rows = int(np.sum(np.linalg.norm(x, axis=1) <= 1e-12))
    fit = AbsorbedFit(
        yvar=yvar,
        xvars=tuple(xvars),
        beta=beta,
        bread=bread,
        residual=residual,
        absorbed_x=x,
        grid_labels=work["grid_id"].to_numpy(),
        cluster_labels=cluster_labels,
        cluster_scores=scores,
        nobs=int(len(work)),
        k=int(len(xvars)),
        rank=rank,
        singleton_grids=int(np.sum(grid_counts == 1)),
        zero_norm_rows=zero_rows,
        max_abs_group_mean=max_mean,
    )
    return fit, work


def draw_wild_weights(reps: int, labels: Sequence[object], seed: int, distribution: str) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if distribution == "rademacher":
        support = np.array([-1.0, 1.0])
    elif distribution == "webb":
        support = np.array([-math.sqrt(1.5), -1.0, -math.sqrt(0.5), math.sqrt(0.5), 1.0, math.sqrt(1.5)])
    else:
        raise ValueError(f"unsupported wild-weight distribution: {distribution}")
    return rng.choice(support, size=(reps, len(labels)), replace=True)


def score_bootstrap_betas(
    fit: AbsorbedFit,
    global_labels: Sequence[object],
    global_weights: np.ndarray,
) -> np.ndarray:
    lookup = {str(label): idx for idx, label in enumerate(global_labels)}
    try:
        positions = np.array([lookup[str(label)] for label in fit.cluster_labels], dtype=int)
    except KeyError as exc:
        raise ValueError(f"model cluster absent from global weight universe: {exc}") from exc
    perturbation = global_weights[:, positions] @ fit.cluster_scores
    return fit.beta[None, :] + perturbation @ fit.bread.T


def algebraic_components(
    mediator_beta: np.ndarray,
    yield_beta: np.ndarray,
    mediator_xvars: Sequence[str],
    yield_xvars: Sequence[str],
    spec: HazardSpec,
    sr_value: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    m = np.atleast_2d(mediator_beta)
    y = np.atleast_2d(yield_beta)
    a1 = m[:, list(mediator_xvars).index(spec.main)]
    a3 = m[:, list(mediator_xvars).index(spec.interaction)]
    b = y[:, list(yield_xvars).index("gleam_smrz_mean_raw")]
    c1 = y[:, list(yield_xvars).index(spec.main)]
    c3 = y[:, list(yield_xvars).index(spec.interaction)]
    indirect = (a1 + a3 * sr_value) * b
    direct = c1 + c3 * sr_value
    total = indirect + direct
    return indirect, direct, total


def delta_components(
    mediator_beta: np.ndarray,
    yield_beta: np.ndarray,
    mediator_xvars: Sequence[str],
    yield_xvars: Sequence[str],
    spec: HazardSpec,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    m = np.atleast_2d(mediator_beta)
    y = np.atleast_2d(yield_beta)
    a3 = m[:, list(mediator_xvars).index(spec.interaction)]
    b = y[:, list(yield_xvars).index("gleam_smrz_mean_raw")]
    c3 = y[:, list(yield_xvars).index(spec.interaction)]
    indirect = a3 * b
    direct = c3
    return indirect, direct, indirect + direct


def haversine_distance_matrix(latitude: np.ndarray, longitude: np.ndarray) -> np.ndarray:
    lat = np.radians(np.asarray(latitude, dtype=float))
    lon = np.radians(np.asarray(longitude, dtype=float))
    dlat = lat[:, None] - lat[None, :]
    dlon = lon[:, None] - lon[None, :]
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat[:, None]) * np.cos(lat[None, :]) * np.sin(dlon / 2.0) ** 2
    return 6371.0088 * 2.0 * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def _haversine_pairs(
    latitude: np.ndarray, longitude: np.ndarray, left: np.ndarray, right: np.ndarray
) -> np.ndarray:
    lat = np.radians(np.asarray(latitude, dtype=float))
    lon = np.radians(np.asarray(longitude, dtype=float))
    dlat = lat[left] - lat[right]
    dlon = lon[left] - lon[right]
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat[left]) * np.cos(lat[right]) * np.sin(dlon / 2.0) ** 2
    return 6371.0088 * 2.0 * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def _grid_scores_and_coordinates(
    fit: AbsorbedFit, work: pd.DataFrame
) -> tuple[np.ndarray, np.ndarray, np.ndarray, pd.Index]:
    observation_scores = fit.absorbed_x * fit.residual[:, None]
    grids = pd.Index(sorted(work["grid_id"].unique()))
    grid_map = {value: idx for idx, value in enumerate(grids)}
    codes = work["grid_id"].map(grid_map).to_numpy(dtype=int)
    scores = np.zeros((len(grids), fit.k), dtype=float)
    np.add.at(scores, codes, observation_scores)
    coords = work.groupby("grid_id", sort=True)[["latitude", "longitude"]].agg(["min", "max"])
    if not np.allclose(coords[("latitude", "min")], coords[("latitude", "max")], atol=1e-12):
        raise AssertionError("latitude is not constant within grid")
    if not np.allclose(coords[("longitude", "min")], coords[("longitude", "max")], atol=1e-12):
        raise AssertionError("longitude is not constant within grid")
    return (
        scores,
        coords[("latitude", "min")].to_numpy(dtype=float),
        coords[("longitude", "min")].to_numpy(dtype=float),
        grids,
    )


def _conley_from_grid_scores(
    scores: np.ndarray,
    latitude: np.ndarray,
    longitude: np.ndarray,
    bread: np.ndarray,
    nobs: int,
    bandwidth_km: float,
) -> tuple[np.ndarray, dict[str, float]]:
    """Sparse exact Bartlett-kernel Conley calculation over all nonzero pairs."""
    g, k = scores.shape
    if g <= 1 or nobs <= k:
        raise RuntimeError("Conley small-sample correction undefined")
    lat_rad = np.radians(np.asarray(latitude, dtype=float))
    lon_rad = np.radians(np.asarray(longitude, dtype=float))
    xyz = np.column_stack(
        (np.cos(lat_rad) * np.cos(lon_rad), np.cos(lat_rad) * np.sin(lon_rad), np.sin(lat_rad))
    )
    chord = 2.0 * np.sin(float(bandwidth_km) / (2.0 * 6371.0088))
    pairs = cKDTree(xyz).query_pairs(r=chord, output_type="ndarray")
    meat = scores.T @ scores
    if len(pairs):
        left = pairs[:, 0]
        right = pairs[:, 1]
        distance = _haversine_pairs(latitude, longitude, left, right)
        weight = np.maximum(1.0 - distance / float(bandwidth_km), 0.0)
        keep = weight > 0.0
        left, right, weight = left[keep], right[keep], weight[keep]
        weighted_left = scores[left] * weight[:, None]
        weighted_right = scores[right] * weight[:, None]
        meat += weighted_left.T @ scores[right]
        meat += weighted_right.T @ scores[left]
        nonzero_pairs = int(g + 2 * len(left))
    else:
        nonzero_pairs = int(g)
    meat = (meat + meat.T) / 2.0
    correction = (g / (g - 1.0)) * ((nobs - 1.0) / (nobs - k))
    covariance = correction * bread @ meat @ bread
    covariance = (covariance + covariance.T) / 2.0
    if not np.isfinite(covariance).all():
        raise RuntimeError("Conley covariance contains non-finite values")
    eigenvalues = np.linalg.eigvalsh(covariance)
    scale = max(1.0, float(np.max(np.diag(covariance))))
    tolerance = 1e-8 * scale
    min_eigenvalue = float(eigenvalues.min())
    if min_eigenvalue < -tolerance:
        raise RuntimeError(
            f"Conley covariance violates frozen eigenvalue tolerance: {min_eigenvalue} < {-tolerance}"
        )
    diagonal = np.diag(covariance).copy()
    negative_zero = (diagonal < 0.0) & (np.abs(diagonal) <= tolerance)
    if np.any(negative_zero):
        covariance[np.diag_indices_from(covariance)] = np.where(negative_zero, 0.0, diagonal)
    return covariance, {
        "bandwidth_km": float(bandwidth_km),
        "grids": int(g),
        "ordered_pairs": int(g * g),
        "nonzero_kernel_ordered_pairs": nonzero_pairs,
        "min_eigenvalue": min_eigenvalue,
        "tolerance": float(tolerance),
        "finite": True,
    }


def conley_covariance(
    fit: AbsorbedFit,
    work: pd.DataFrame,
    bandwidth_km: float,
) -> tuple[np.ndarray, dict[str, float]]:
    """Conley covariance using all ordered grid pairs and a Bartlett distance kernel."""
    scores, latitude, longitude, _ = _grid_scores_and_coordinates(fit, work)
    return _conley_from_grid_scores(
        scores, latitude, longitude, fit.bread, fit.nobs, bandwidth_km
    )


def conley_stacked_covariance(
    mediator_fit: AbsorbedFit,
    yield_fit: AbsorbedFit,
    mediator_work: pd.DataFrame,
    yield_work: pd.DataFrame,
    bandwidth_km: float,
) -> tuple[np.ndarray, dict[str, float]]:
    """Joint two-equation Conley covariance preserving cross-equation scores."""
    mkeys = mediator_work[["grid_id", "year"]].reset_index(drop=True)
    ykeys = yield_work[["grid_id", "year"]].reset_index(drop=True)
    if not mkeys.equals(ykeys):
        raise AssertionError("stacked Conley equations do not share identical complete cases")
    m_scores, latitude, longitude, m_grids = _grid_scores_and_coordinates(
        mediator_fit, mediator_work
    )
    y_scores, y_latitude, y_longitude, y_grids = _grid_scores_and_coordinates(
        yield_fit, yield_work
    )
    if not m_grids.equals(y_grids):
        raise AssertionError("stacked Conley equations do not share identical grids")
    if not np.allclose(latitude, y_latitude) or not np.allclose(longitude, y_longitude):
        raise AssertionError("stacked Conley coordinate mismatch")
    scores = np.column_stack((m_scores, y_scores))
    bread = np.zeros((mediator_fit.k + yield_fit.k, mediator_fit.k + yield_fit.k), dtype=float)
    bread[: mediator_fit.k, : mediator_fit.k] = mediator_fit.bread
    bread[mediator_fit.k :, mediator_fit.k :] = yield_fit.bread
    return _conley_from_grid_scores(
        scores, latitude, longitude, bread, mediator_fit.nobs, bandwidth_km
    )


def romano_wolf_stepdown(
    estimate: np.ndarray,
    bootstrap: np.ndarray,
    preset_order: Sequence[object],
) -> np.ndarray:
    estimate = np.asarray(estimate, dtype=float)
    bootstrap = np.asarray(bootstrap, dtype=float)
    if bootstrap.ndim != 2 or bootstrap.shape[1] != len(estimate) or len(preset_order) != len(estimate):
        raise ValueError("Romano-Wolf requires a complete B by J bootstrap matrix")
    se = np.std(bootstrap, axis=0, ddof=1)
    if np.any(~np.isfinite(se)) or np.any(se <= 0):
        raise RuntimeError("Romano-Wolf bootstrap standard errors are invalid")
    observed = np.abs(estimate / se)
    centered = np.abs((bootstrap - estimate[None, :]) / se[None, :])
    ordering = sorted(range(len(estimate)), key=lambda idx: (-observed[idx], idx))
    adjusted_sorted: list[float] = []
    for step, idx in enumerate(ordering):
        remaining = ordering[step:]
        max_t = np.max(centered[:, remaining], axis=1)
        raw = (1.0 + float(np.sum(max_t >= observed[idx]))) / (bootstrap.shape[0] + 1.0)
        adjusted_sorted.append(max(raw, adjusted_sorted[-1] if adjusted_sorted else 0.0))
    out = np.empty(len(estimate), dtype=float)
    for idx, value in zip(ordering, adjusted_sorted, strict=True):
        out[idx] = min(value, 1.0)
    return out


def holm_adjust(pvalues: np.ndarray) -> np.ndarray:
    pvalues = np.asarray(pvalues, dtype=float)
    order = np.argsort(pvalues, kind="stable")
    out = np.empty_like(pvalues)
    running = 0.0
    m = len(pvalues)
    for position, idx in enumerate(order):
        running = max(running, (m - position) * pvalues[idx])
        out[idx] = min(running, 1.0)
    return out


def omnibus_region_tests(
    estimate: np.ndarray,
    bootstrap: np.ndarray,
) -> list[dict[str, object]]:
    """Compute the three frozen four-difference regional omnibus diagnostics."""
    estimate = np.asarray(estimate, dtype=float)
    bootstrap = np.asarray(bootstrap, dtype=float)
    if estimate.shape != (15,) or bootstrap.ndim != 2 or bootstrap.shape[1] != 15:
        raise ValueError("omnibus interface requires the complete 15-dimensional family")
    covariance = np.cov(bootstrap, rowvar=False, ddof=1)
    raw_p: list[float] = []
    rows: list[dict[str, object]] = []
    for hazard_index, hazard in enumerate(HAZARDS):
        indices = [region_index * len(HAZARDS) + hazard_index for region_index in range(len(REGIONS))]
        contrast = np.zeros((4, 15), dtype=float)
        for row, index in enumerate(indices[1:]):
            contrast[row, index] = 1.0
            contrast[row, indices[0]] = -1.0
        vc = contrast @ covariance @ contrast.T
        eig = np.linalg.eigvalsh((vc + vc.T) / 2.0)
        lambda_max = float(np.max(eig))
        rank = int(np.sum(eig > 1e-10 * lambda_max)) if lambda_max > 0 else 0
        if rank < 4:
            raise RuntimeError(f"omnibus rank below four for {hazard}: {rank}")
        inverse = np.linalg.pinv(vc, rcond=1e-10)
        observed_diff = contrast @ estimate
        observed_wald = float(observed_diff @ inverse @ observed_diff)
        centered = (bootstrap - estimate[None, :]) @ contrast.T
        boot_wald = np.einsum("bi,ij,bj->b", centered, inverse, centered)
        pvalue = (1.0 + float(np.sum(boot_wald >= observed_wald))) / (bootstrap.shape[0] + 1.0)
        raw_p.append(pvalue)
        rows.append(
            {
                "hazard": hazard,
                "rank": rank,
                "wald": observed_wald,
                "pvalue": pvalue,
                "finite": bool(np.isfinite(observed_wald) and np.isfinite(pvalue)),
            }
        )
    adjusted = holm_adjust(np.asarray(raw_p))
    for row, value in zip(rows, adjusted, strict=True):
        row["holm_pvalue"] = float(value)
        row["holm_finite"] = bool(np.isfinite(value))
    return rows


def output_hashes(directory: Path, exclude: Sequence[str] = ("smoke_manifest.json",)) -> dict[str, str]:
    excluded = set(exclude)
    return {
        path.relative_to(directory).as_posix(): sha256_file(path)
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.name not in excluded
    }
