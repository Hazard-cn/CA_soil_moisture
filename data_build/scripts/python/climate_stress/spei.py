"""CHM SPEI spatial alignment, streaming caches, and window summaries.

The three interfaces are intentionally separate:

* ``legacy_v3_exact`` and ``dynamic_ext`` use nearest-neighbour values.
* ``manual`` SPEI-1/3 uses bilinear interpolation renormalized over at least
  two valid, positive-weight source neighbours.
* SPEI-2W contains a development-candidate split contract: each label ends a
  trailing 14-day accumulation, while run detection maps that release to the
  non-overlapping forward seven-day state beginning on the label date.  The
  candidate remains disabled until the endpoint decision is confirmed.

Three-dimensional NetCDF variables are read one time index at a time.  No
function in this module materializes an entire source cube.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import uuid
import zipfile
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Iterator, Mapping, Sequence

import netCDF4 as nc
import numpy as np
import pandas as pd

from .core import (
    SPEI_2W_PENDING_STATUS,
    SpeiEvent,
    SpeiRecord,
    detect_spei_runs,
    event_window_bridge_for_spei,
    spei_2w_interval_contracts,
    spei_2w_records,
)


WINDOW_NAMES = ("full", "v3pre30", "v3pm10", "hepm10", "v3he", "hema")
MANUAL_EVENT_SPECS: dict[str, tuple[float, int]] = {
    "k10_main": (-1.0, 1),
    "k15_strict": (-1.5, 3),
}
TWO_WEEK_EVENT_SPECS: dict[str, tuple[float, int]] = {
    "k10_main": (-1.0, 1),
    "k15_strict": (-1.5, 3),
}
LEGACY_FIELD_MAP: dict[str, tuple[str, str]] = {
    "full": ("spei6_mean", "spei6_max"),
    "v3pre30": ("spei1_mean_v3pre30", "spei1_max_v3pre30"),
    "v3pm10": ("spei1_mean_v3pm10", "spei1_max_v3pm10"),
    "hepm10": ("spei1_mean_hepm10", "spei1_max_hepm10"),
    "v3he": ("spei2_mean_v3he", "spei2_max_v3he"),
    "hema": ("spei2_mean_hema", "spei2_max_hema"),
}


def _finite(value: object) -> float | None:
    if value is None:
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def _month_code(value: date) -> int:
    return value.year * 100 + value.month


def _month_start(code: int) -> date:
    year, month = divmod(int(code), 100)
    if not 1 <= month <= 12:
        raise ValueError(f"Invalid month code: {code}")
    return date(year, month, 1)


def _next_month(value: date) -> date:
    return date(value.year + 1, 1, 1) if value.month == 12 else date(value.year, value.month + 1, 1)


def _requested_month_codes(years: Sequence[int]) -> np.ndarray:
    return np.asarray(
        [int(year) * 100 + month for year in sorted({int(item) for item in years}) for month in range(1, 13)],
        dtype=np.int32,
    )


@dataclass(frozen=True)
class CHMSpatialMapping:
    source_latitude: np.ndarray
    source_longitude: np.ndarray
    target_latitude: np.ndarray
    target_longitude: np.ndarray
    nearest_lat_index: np.ndarray
    nearest_lon_index: np.ndarray
    bilinear_lat_index: np.ndarray
    bilinear_lon_index: np.ndarray
    bilinear_weights: np.ndarray
    bilinear_in_bounds: np.ndarray

    @property
    def target_count(self) -> int:
        return int(self.target_latitude.size)


def _sorted_axis(axis: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(axis, dtype=np.float64)
    if values.ndim != 1 or values.size < 2 or not np.isfinite(values).all():
        raise ValueError("Source coordinate axes must be finite one-dimensional arrays")
    if np.unique(values).size != values.size:
        raise ValueError("Source coordinate axes must be unique")
    order = np.argsort(values, kind="stable")
    return values[order], order


def _nearest_axis_indices(axis: Sequence[float], targets: np.ndarray) -> np.ndarray:
    ordered, order = _sorted_axis(axis)
    right = np.searchsorted(ordered, targets, side="left")
    right = np.clip(right, 0, ordered.size - 1)
    left = np.clip(right - 1, 0, ordered.size - 1)
    choose_right = np.abs(ordered[right] - targets) < np.abs(ordered[left] - targets)
    selected = np.where(choose_right, right, left)
    return order[selected].astype(np.int32)


def _axis_brackets(
    axis: Sequence[float], targets: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    ordered, order = _sorted_axis(axis)
    in_bounds = (targets >= ordered[0]) & (targets <= ordered[-1])
    upper_position = np.searchsorted(ordered, targets, side="right")
    upper_position = np.clip(upper_position, 1, ordered.size - 1)
    lower_position = upper_position - 1
    lower_value = ordered[lower_position]
    upper_value = ordered[upper_position]
    fraction = (targets - lower_value) / (upper_value - lower_value)
    fraction = np.clip(fraction, 0.0, 1.0)
    return (
        order[lower_position].astype(np.int32),
        order[upper_position].astype(np.int32),
        fraction.astype(np.float64),
        in_bounds,
    )


def build_chm_spatial_mapping(
    source_latitude: Sequence[float],
    source_longitude: Sequence[float],
    target_latitude: Sequence[float],
    target_longitude: Sequence[float],
) -> CHMSpatialMapping:
    """Build nearest and four-neighbour mappings from CHM's own coordinates."""

    target_lat = np.asarray(target_latitude, dtype=np.float64)
    target_lon = np.asarray(target_longitude, dtype=np.float64)
    if target_lat.ndim != 1 or target_lon.ndim != 1 or target_lat.shape != target_lon.shape:
        raise ValueError("Target latitude and longitude must be equal-length vectors")
    if not np.isfinite(target_lat).all() or not np.isfinite(target_lon).all():
        raise ValueError("Target coordinates must be finite")
    source_lat = np.asarray(source_latitude, dtype=np.float64)
    source_lon = np.asarray(source_longitude, dtype=np.float64)
    nearest_lat = _nearest_axis_indices(source_lat, target_lat)
    nearest_lon = _nearest_axis_indices(source_lon, target_lon)
    south, north, y_fraction, lat_in_bounds = _axis_brackets(source_lat, target_lat)
    west, east, x_fraction, lon_in_bounds = _axis_brackets(source_lon, target_lon)
    lat_indices = np.column_stack((south, north)).astype(np.int32)
    lon_indices = np.column_stack((west, east)).astype(np.int32)
    weights = np.column_stack(
        (
            (1.0 - x_fraction) * (1.0 - y_fraction),
            x_fraction * (1.0 - y_fraction),
            (1.0 - x_fraction) * y_fraction,
            x_fraction * y_fraction,
        )
    )
    return CHMSpatialMapping(
        source_latitude=source_lat,
        source_longitude=source_lon,
        target_latitude=target_lat,
        target_longitude=target_lon,
        nearest_lat_index=nearest_lat,
        nearest_lon_index=nearest_lon,
        bilinear_lat_index=lat_indices,
        bilinear_lon_index=lon_indices,
        bilinear_weights=weights,
        bilinear_in_bounds=lat_in_bounds & lon_in_bounds,
    )


def map_nearest(source_slice: np.ndarray, mapping: CHMSpatialMapping) -> np.ndarray:
    """Map one CHM time slice to target cells with nearest neighbours."""

    values = np.asarray(source_slice, dtype=np.float64)
    expected = (mapping.source_latitude.size, mapping.source_longitude.size)
    if values.shape != expected:
        raise ValueError(f"Source slice shape {values.shape} does not match {expected}")
    return values[mapping.nearest_lat_index, mapping.nearest_lon_index]


def map_bilinear_renormalized(
    source_slice: np.ndarray,
    mapping: CHMSpatialMapping,
    *,
    minimum_valid_neighbors: int = 2,
) -> np.ndarray:
    """Map a slice with four-neighbour bilinear renormalization and no extrapolation."""

    if not 1 <= minimum_valid_neighbors <= 4:
        raise ValueError("minimum_valid_neighbors must lie in 1..4")
    values = np.asarray(source_slice, dtype=np.float64)
    expected = (mapping.source_latitude.size, mapping.source_longitude.size)
    if values.shape != expected:
        raise ValueError(f"Source slice shape {values.shape} does not match {expected}")
    south = mapping.bilinear_lat_index[:, 0]
    north = mapping.bilinear_lat_index[:, 1]
    west = mapping.bilinear_lon_index[:, 0]
    east = mapping.bilinear_lon_index[:, 1]
    neighbours = np.column_stack(
        (
            values[south, west],
            values[south, east],
            values[north, west],
            values[north, east],
        )
    )
    positive_weight = mapping.bilinear_weights > 0.0
    usable = np.isfinite(neighbours) & positive_weight
    usable_count = usable.sum(axis=1)
    weights = np.where(usable, mapping.bilinear_weights, 0.0)
    denominator = weights.sum(axis=1)
    numerator = np.where(usable, neighbours, 0.0) * weights
    result = np.full(mapping.target_count, np.nan, dtype=np.float64)
    valid = (
        mapping.bilinear_in_bounds
        & (usable_count >= int(minimum_valid_neighbors))
        & (denominator > 0.0)
    )
    result[valid] = numerator.sum(axis=1)[valid] / denominator[valid]
    return result


def _coordinate_values(dataset: nc.Dataset, name: str) -> np.ndarray:
    variable = dataset.variables[name]
    return np.asarray(variable[0 : variable.shape[0]], dtype=np.float64)


def _time_dates(dataset: nc.Dataset) -> tuple[date, ...]:
    variable = dataset.variables["time"]
    raw = np.asarray(variable[0 : variable.shape[0]], dtype=np.float64)
    decoded = nc.num2date(
        raw,
        units=variable.units,
        calendar=getattr(variable, "calendar", "standard"),
    )
    return tuple(date(int(item.year), int(item.month), int(item.day)) for item in decoded)


def _time_month_codes(dataset: nc.Dataset) -> np.ndarray:
    dates = _time_dates(dataset)
    codes = np.asarray([_month_code(item) for item in dates], dtype=np.int32)
    if np.unique(codes).size != codes.size or np.any(np.diff(codes) <= 0):
        raise ValueError("CHM monthly time coordinates must be unique and increasing")
    return codes


def _variable_name(scale: int | str) -> str:
    return f"SPEI-{scale}"


def _validate_source_grid(dataset: nc.Dataset, mapping: CHMSpatialMapping) -> None:
    latitude = _coordinate_values(dataset, "lat")
    longitude = _coordinate_values(dataset, "lon")
    if not np.array_equal(latitude, mapping.source_latitude) or not np.array_equal(
        longitude, mapping.source_longitude
    ):
        raise ValueError("CHM source grids differ across SPEI files")


def extract_mapped_time_slices(
    dataset: nc.Dataset,
    variable_name: str,
    time_indices: Sequence[int],
    mapping: CHMSpatialMapping,
    *,
    method: str,
    minimum_valid_neighbors: int = 2,
    out: np.ndarray | None = None,
) -> np.ndarray:
    """Read and map selected time indices without loading a complete cube."""

    variable = dataset.variables[variable_name]
    if variable.ndim != 3:
        raise ValueError(f"{variable_name} must be time x lat x lon")
    nlat, nlon = int(variable.shape[1]), int(variable.shape[2])
    if out is None:
        output = np.full((len(time_indices), mapping.target_count), np.nan, dtype=np.float32)
    else:
        output = out
        if output.shape != (len(time_indices), mapping.target_count):
            raise ValueError("Output array has the wrong shape")
    for output_index, source_index in enumerate(time_indices):
        raw = variable[int(source_index), 0:nlat, 0:nlon]
        source_slice = np.ma.filled(raw, np.nan).astype(np.float64, copy=False)
        if method == "nearest":
            mapped = map_nearest(source_slice, mapping)
        elif method == "bilinear_renormalized":
            mapped = map_bilinear_renormalized(
                source_slice,
                mapping,
                minimum_valid_neighbors=minimum_valid_neighbors,
            )
        else:
            raise ValueError("method must be nearest or bilinear_renormalized")
        output[output_index] = mapped.astype(output.dtype, copy=False)
    return output


def _lookup_time_indices(source_codes: np.ndarray, requested_codes: np.ndarray) -> np.ndarray:
    positions = np.searchsorted(source_codes, requested_codes)
    valid = positions < source_codes.size
    matched = np.zeros(requested_codes.size, dtype=bool)
    matched[valid] = source_codes[positions[valid]] == requested_codes[valid]
    if not matched.all():
        missing = requested_codes[~matched].tolist()
        raise ValueError(f"Requested CHM months are absent: {missing[:12]}")
    return positions.astype(np.int64)


def _new_partial_path(target: Path) -> Path:
    if target.exists():
        raise FileExistsError(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    return target.with_name(f".{target.name}.{uuid.uuid4().hex}.partial")


def _write_npy_new(target: Path, values: np.ndarray) -> None:
    partial = _new_partial_path(target)
    with partial.open("xb") as handle:
        np.save(handle, values, allow_pickle=False)
        handle.flush()
        os.fsync(handle.fileno())
    if target.exists():
        raise FileExistsError(target)
    os.rename(partial, target)


def _write_npz_new(target: Path, values: Mapping[str, np.ndarray]) -> None:
    partial = _new_partial_path(target)
    with partial.open("xb") as handle:
        np.savez(handle, **values)
        handle.flush()
        os.fsync(handle.fileno())
    if target.exists():
        raise FileExistsError(target)
    os.rename(partial, target)


def _write_json_new(target: Path, payload: Mapping[str, object]) -> None:
    partial = _new_partial_path(target)
    partial.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    if target.exists():
        raise FileExistsError(target)
    os.rename(partial, target)


def _write_mapped_cache(
    target: Path,
    dataset: nc.Dataset,
    variable_name: str,
    time_indices: np.ndarray,
    mapping: CHMSpatialMapping,
    *,
    method: str,
    minimum_valid_neighbors: int,
) -> None:
    partial = _new_partial_path(target)
    output = np.lib.format.open_memmap(
        partial,
        mode="w+",
        dtype=np.float32,
        shape=(time_indices.size, mapping.target_count),
    )
    output[:] = np.nan
    extract_mapped_time_slices(
        dataset,
        variable_name,
        time_indices,
        mapping,
        method=method,
        minimum_valid_neighbors=minimum_valid_neighbors,
        out=output,
    )
    output.flush()
    del output
    if target.exists():
        raise FileExistsError(target)
    os.rename(partial, target)


def _quarantine_incomplete(path: Path) -> Path:
    """Move an invalid cache aside without deleting or overwriting it."""

    quarantined = path.with_name(f"{path.name}.incomplete.{uuid.uuid4().hex}")
    os.rename(path, quarantined)
    return quarantined


def _valid_npy(
    path: Path,
    *,
    shape: tuple[int, ...],
    dtype: np.dtype | type,
    expected: np.ndarray | None = None,
) -> bool:
    try:
        values = np.load(path, mmap_mode="r", allow_pickle=False)
        valid = values.shape == shape and values.dtype == np.dtype(dtype)
        if valid and expected is not None:
            valid = np.array_equal(np.asarray(values), expected, equal_nan=True)
        del values
        return bool(valid)
    except (OSError, ValueError, EOFError):
        return False


def _valid_npz(path: Path, expected: Mapping[str, np.ndarray]) -> bool:
    try:
        with np.load(path, allow_pickle=False) as archive:
            if set(archive.files) != set(expected):
                return False
            for name, reference in expected.items():
                values = np.asarray(archive[name])
                if values.dtype != reference.dtype or not np.array_equal(
                    values, reference, equal_nan=True
                ):
                    return False
        return True
    except (OSError, ValueError, EOFError, KeyError, zipfile.BadZipFile):
        return False


def _valid_json(path: Path, expected: Mapping[str, object]) -> bool:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    return payload == dict(expected)


def _metadata_with_signature(payload: Mapping[str, object]) -> dict[str, object]:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return {**payload, "signature_sha256": hashlib.sha256(canonical).hexdigest()}


def _sha256_file(path: Path, *, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(int(chunk_bytes)):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class SpeiCachePaths:
    root: Path
    mapping: Path
    target_month_codes: Path
    full_month_codes: Path
    target_nearest: dict[int, Path]
    full_manual: dict[int, Path]
    metadata: Path


@dataclass(frozen=True)
class TwoWeekCachePaths:
    root: Path
    mapping: Path
    release_ordinals: Path
    values: Path
    metadata: Path


def build_spei_caches(
    file_pattern: str,
    target_latitude: Sequence[float],
    target_longitude: Sequence[float],
    output_root: str | Path,
    *,
    target_years: Sequence[int] = tuple(range(2010, 2020)),
    target_scales: Sequence[int] = tuple(range(1, 13)),
    full_years: Sequence[int] = tuple(range(1961, 2023)),
    manual_scales: Sequence[int] = (1, 3),
    minimum_valid_neighbors: int = 2,
    resume: bool = False,
) -> SpeiCachePaths:
    """Build or safely resume nearest and full-history manual caches."""

    target_scales = tuple(sorted({int(item) for item in target_scales}))
    manual_scales = tuple(sorted({int(item) for item in manual_scales}))
    if not target_scales or not manual_scales:
        raise ValueError("target_scales and manual_scales must be non-empty")
    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    first_path = Path(file_pattern.format(scale=target_scales[0]))
    with nc.Dataset(first_path) as dataset:
        mapping = build_chm_spatial_mapping(
            _coordinate_values(dataset, "lat"),
            _coordinate_values(dataset, "lon"),
            target_latitude,
            target_longitude,
        )

    target_codes = _requested_month_codes(target_years)
    full_codes = _requested_month_codes(full_years)
    mapping_path = root / "chm_spatial_mapping.npz"
    target_codes_path = root / "target_month_codes.npy"
    full_codes_path = root / "full_month_codes.npy"
    metadata_path = root / "metadata.json"
    target_paths = {
        scale: root / "target_nearest" / f"scale={scale:02d}.npy" for scale in target_scales
    }
    full_paths = {
        scale: root / "full_manual" / f"scale={scale:02d}.npy" for scale in manual_scales
    }
    mapping_values = {
        "source_latitude": mapping.source_latitude,
        "source_longitude": mapping.source_longitude,
        "target_latitude": mapping.target_latitude,
        "target_longitude": mapping.target_longitude,
        "nearest_lat_index": mapping.nearest_lat_index,
        "nearest_lon_index": mapping.nearest_lon_index,
        "bilinear_lat_index": mapping.bilinear_lat_index,
        "bilinear_lon_index": mapping.bilinear_lon_index,
        "bilinear_weights": mapping.bilinear_weights,
        "bilinear_in_bounds": mapping.bilinear_in_bounds,
    }
    metadata_payload = _metadata_with_signature(
        {
            "target_years": [int(item) for item in sorted(set(target_years))],
            "target_scales": list(target_scales),
            "target_interpolation": "nearest",
            "full_years": [int(item) for item in sorted(set(full_years))],
            "manual_scales": list(manual_scales),
            "manual_interpolation": "bilinear_renormalized",
            "minimum_valid_neighbors": int(minimum_valid_neighbors),
            "target_cells": mapping.target_count,
            "source_grid": [
                int(mapping.source_latitude.size),
                int(mapping.source_longitude.size),
            ],
            "source_pattern": str(file_pattern),
            "read_policy": "one explicit time index per source read",
            "complete": True,
        }
    )
    all_targets = [
        mapping_path,
        target_codes_path,
        full_codes_path,
        metadata_path,
        *target_paths.values(),
        *full_paths.values(),
    ]
    existing = [path for path in all_targets if path.exists()]
    if existing and not resume:
        raise FileExistsError(existing[0])

    metadata_valid = resume and metadata_path.exists() and _valid_json(
        metadata_path, metadata_payload
    )
    invalidate_target = False
    invalidate_full = False
    if resume and metadata_path.exists() and not metadata_valid:
        _quarantine_incomplete(metadata_path)
        invalidate_target = True
        invalidate_full = True

    mapping_valid = resume and mapping_path.exists() and _valid_npz(
        mapping_path, mapping_values
    )
    if not mapping_valid:
        if mapping_path.exists():
            _quarantine_incomplete(mapping_path)
        _write_npz_new(mapping_path, mapping_values)
        invalidate_target = True
        invalidate_full = True

    target_codes_valid = resume and target_codes_path.exists() and _valid_npy(
        target_codes_path,
        shape=target_codes.shape,
        dtype=target_codes.dtype,
        expected=target_codes,
    )
    if not target_codes_valid:
        if target_codes_path.exists():
            _quarantine_incomplete(target_codes_path)
        _write_npy_new(target_codes_path, target_codes)
        invalidate_target = True

    full_codes_valid = resume and full_codes_path.exists() and _valid_npy(
        full_codes_path,
        shape=full_codes.shape,
        dtype=full_codes.dtype,
        expected=full_codes,
    )
    if not full_codes_valid:
        if full_codes_path.exists():
            _quarantine_incomplete(full_codes_path)
        _write_npy_new(full_codes_path, full_codes)
        invalidate_full = True

    for scale, path in target_paths.items():
        cache_valid = (
            resume
            and not invalidate_target
            and path.exists()
            and _valid_npy(
                path,
                shape=(target_codes.size, mapping.target_count),
                dtype=np.float32,
            )
        )
        if cache_valid:
            continue
        if path.exists():
            _quarantine_incomplete(path)
        source = Path(file_pattern.format(scale=scale))
        with nc.Dataset(source) as dataset:
            _validate_source_grid(dataset, mapping)
            source_codes = _time_month_codes(dataset)
            indices = _lookup_time_indices(source_codes, target_codes)
            _write_mapped_cache(
                path,
                dataset,
                _variable_name(scale),
                indices,
                mapping,
                method="nearest",
                minimum_valid_neighbors=minimum_valid_neighbors,
            )

    for scale, path in full_paths.items():
        cache_valid = (
            resume
            and not invalidate_full
            and path.exists()
            and _valid_npy(
                path,
                shape=(full_codes.size, mapping.target_count),
                dtype=np.float32,
            )
        )
        if cache_valid:
            continue
        if path.exists():
            _quarantine_incomplete(path)
        source = Path(file_pattern.format(scale=scale))
        with nc.Dataset(source) as dataset:
            _validate_source_grid(dataset, mapping)
            source_codes = _time_month_codes(dataset)
            indices = _lookup_time_indices(source_codes, full_codes)
            _write_mapped_cache(
                path,
                dataset,
                _variable_name(scale),
                indices,
                mapping,
                method="bilinear_renormalized",
                minimum_valid_neighbors=minimum_valid_neighbors,
            )

    if not metadata_valid:
        _write_json_new(metadata_path, metadata_payload)
    return SpeiCachePaths(
        root=root,
        mapping=mapping_path,
        target_month_codes=target_codes_path,
        full_month_codes=full_codes_path,
        target_nearest=target_paths,
        full_manual=full_paths,
        metadata=metadata_path,
    )


def build_two_week_cache(
    source_path: str | Path,
    target_latitude: Sequence[float],
    target_longitude: Sequence[float],
    output_root: str | Path,
    *,
    minimum_valid_neighbors: int = 2,
    interpolation: str = "bilinear_renormalized",
    accumulation_days: int = 14,
    state_days: int = 7,
    accumulation_timestamp_position: str = "end",
    state_timestamp_position: str = "start",
    timestamp_semantics: str = (
        "trailing_14_day_accumulation_end_with_forward_7_day_state"
    ),
    endpoint_decision_status: str,
    resume: bool = False,
) -> TwoWeekCachePaths:
    """Map the complete CHM SPEI-2W cube without loading it into memory."""

    if interpolation != "bilinear_renormalized":
        raise ValueError("Frozen SPEI-2W interpolation must be bilinear_renormalized")
    if endpoint_decision_status != "CONFIRMED":
        raise ValueError("SPEI-2W cache requires a confirmed endpoint decision")
    source = Path(source_path)
    source_sha256 = _sha256_file(source)
    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    with nc.Dataset(source) as dataset:
        mapping = build_chm_spatial_mapping(
            _coordinate_values(dataset, "lat"),
            _coordinate_values(dataset, "lon"),
            target_latitude,
            target_longitude,
        )
        release_dates = _time_dates(dataset)
        # Validation is performed before any cache target is published.
        contracts = spei_2w_interval_contracts(
            release_dates,
            accumulation_days=int(accumulation_days),
            state_days=int(state_days),
            accumulation_timestamp_position=accumulation_timestamp_position,
            state_timestamp_position=state_timestamp_position,
        )
        if "SPEI-2W" not in dataset.variables:
            raise ValueError("CHM SPEI-2W source lacks variable SPEI-2W")
        release_ordinals = np.asarray(
            [item.label_date.toordinal() for item in contracts], dtype=np.int32
        )

    mapping_path = root / "chm_spei_2w_spatial_mapping.npz"
    dates_path = root / "release_date_ordinals.npy"
    values_path = root / "full_bilinear.npy"
    metadata_path = root / "metadata.json"
    mapping_values = {
        "source_latitude": mapping.source_latitude,
        "source_longitude": mapping.source_longitude,
        "target_latitude": mapping.target_latitude,
        "target_longitude": mapping.target_longitude,
        "nearest_lat_index": mapping.nearest_lat_index,
        "nearest_lon_index": mapping.nearest_lon_index,
        "bilinear_lat_index": mapping.bilinear_lat_index,
        "bilinear_lon_index": mapping.bilinear_lon_index,
        "bilinear_weights": mapping.bilinear_weights,
        "bilinear_in_bounds": mapping.bilinear_in_bounds,
    }
    metadata_payload = _metadata_with_signature(
        {
            "source_path": str(source),
            "source_sha256": source_sha256,
            "variable": "SPEI-2W",
            "release_count": int(release_ordinals.size),
            "first_release_date": release_dates[0].isoformat(),
            "last_release_date": release_dates[-1].isoformat(),
            "sampling_days": int(state_days),
            "accumulation_days": int(accumulation_days),
            "accumulation_timestamp_position": accumulation_timestamp_position,
            "state_days": int(state_days),
            "state_timestamp_position": state_timestamp_position,
            "timestamp_semantics": timestamp_semantics,
            "endpoint_decision_status": endpoint_decision_status,
            "accumulation_support": (
                "confirmed: [label-13 days, label] inclusive"
            ),
            "event_state_support": (
                "confirmed: [label, label+6 days] inclusive"
            ),
            "interpolation": interpolation,
            "minimum_valid_neighbors": int(minimum_valid_neighbors),
            "target_cells": mapping.target_count,
            "source_grid": [
                int(mapping.source_latitude.size),
                int(mapping.source_longitude.size),
            ],
            "read_policy": "one explicit time index per source read",
            "complete": True,
        }
    )
    targets = (mapping_path, dates_path, values_path, metadata_path)
    existing = [path for path in targets if path.exists()]
    if existing and not resume:
        raise FileExistsError(existing[0])
    metadata_valid = resume and metadata_path.exists() and _valid_json(
        metadata_path, metadata_payload
    )
    invalidate_values = False
    if resume and metadata_path.exists() and not metadata_valid:
        _quarantine_incomplete(metadata_path)
        invalidate_values = True
    mapping_valid = resume and mapping_path.exists() and _valid_npz(
        mapping_path, mapping_values
    )
    if not mapping_valid:
        if mapping_path.exists():
            _quarantine_incomplete(mapping_path)
        _write_npz_new(mapping_path, mapping_values)
        invalidate_values = True
    dates_valid = resume and dates_path.exists() and _valid_npy(
        dates_path,
        shape=release_ordinals.shape,
        dtype=np.int32,
        expected=release_ordinals,
    )
    if not dates_valid:
        if dates_path.exists():
            _quarantine_incomplete(dates_path)
        _write_npy_new(dates_path, release_ordinals)
        invalidate_values = True
    values_valid = (
        resume
        and not invalidate_values
        and values_path.exists()
        and _valid_npy(
            values_path,
            shape=(release_ordinals.size, mapping.target_count),
            dtype=np.float32,
        )
    )
    if not values_valid:
        if values_path.exists():
            _quarantine_incomplete(values_path)
        with nc.Dataset(source) as dataset:
            _validate_source_grid(dataset, mapping)
            _write_mapped_cache(
                values_path,
                dataset,
                "SPEI-2W",
                np.arange(release_ordinals.size, dtype=np.int64),
                mapping,
                method=interpolation,
                minimum_valid_neighbors=minimum_valid_neighbors,
            )
    if not metadata_valid:
        _write_json_new(metadata_path, metadata_payload)
    return TwoWeekCachePaths(
        root=root,
        mapping=mapping_path,
        release_ordinals=dates_path,
        values=values_path,
        metadata=metadata_path,
    )


def load_cache_array(path: str | Path, *, mmap: bool = True) -> np.ndarray:
    return np.load(Path(path), mmap_mode="r" if mmap else None, allow_pickle=False)


@dataclass(frozen=True)
class ManualWindowSummary:
    mean: float
    min_spei: float
    end: float
    coverage: float
    valid_days: int
    expected_days: int
    peak_threshold_deficit: float


def summarize_manual_window(
    month_codes: Sequence[int],
    values: Sequence[float],
    *,
    window_start: date,
    window_end: date,
    minimum_coverage: float = 0.9,
    deficit_threshold: float = -1.0,
) -> ManualWindowSummary:
    """Summarize monthly SPEI with actual overlap-day weights."""

    if window_end < window_start:
        raise ValueError("window_end must not precede window_start")
    codes = np.asarray(month_codes, dtype=np.int32)
    series = np.asarray(values, dtype=np.float64)
    if codes.ndim != 1 or series.shape != codes.shape:
        raise ValueError("month_codes and values must be equal-length vectors")
    if np.any(np.diff(codes) <= 0):
        raise ValueError("month_codes must be unique and increasing")
    expected_days = (window_end - window_start).days + 1
    first_code = _month_code(window_start)
    last_code = _month_code(window_end)
    first_index = int(np.searchsorted(codes, first_code, side="left"))
    last_index = int(np.searchsorted(codes, last_code, side="right"))
    window_codes = codes[first_index:last_index]
    window_series = series[first_index:last_index]
    weighted_sum = 0.0
    valid_days = 0
    overlapping_values: list[float] = []
    end_value = math.nan
    for code, raw_value in zip(window_codes, window_series, strict=True):
        support_start = _month_start(int(code))
        support_end = _next_month(support_start)
        overlap = max(
            (
                min(support_end, window_end + timedelta(days=1))
                - max(support_start, window_start)
            ).days,
            0,
        )
        if overlap == 0:
            continue
        value = _finite(raw_value)
        if value is not None:
            weighted_sum += value * overlap
            valid_days += overlap
            overlapping_values.append(value)
        if int(code) == _month_code(window_end) and value is not None:
            end_value = value
    coverage = valid_days / expected_days
    if coverage < minimum_coverage or not overlapping_values:
        return ManualWindowSummary(
            mean=math.nan,
            min_spei=math.nan,
            end=math.nan,
            coverage=coverage,
            valid_days=valid_days,
            expected_days=expected_days,
            peak_threshold_deficit=math.nan,
        )
    minimum = min(overlapping_values)
    return ManualWindowSummary(
        mean=weighted_sum / valid_days,
        min_spei=minimum,
        end=end_value,
        coverage=coverage,
        valid_days=valid_days,
        expected_days=expected_days,
        peak_threshold_deficit=max(float(deficit_threshold) - minimum, 0.0),
    )


def _window_dates(row: Mapping[str, object], window: str) -> tuple[date, date] | None:
    start_date_key = f"win_{window}_start_date"
    end_date_key = f"win_{window}_end_date"
    if start_date_key in row and end_date_key in row:
        start_raw, end_raw = row[start_date_key], row[end_date_key]
        if pd.isna(start_raw) or pd.isna(end_raw):
            return None
        return pd.Timestamp(start_raw).date(), pd.Timestamp(end_raw).date()
    start_key, end_key = f"win_{window}_start", f"win_{window}_end"
    if start_key not in row or end_key not in row:
        raise KeyError(f"Missing window fields for {window}")
    if pd.isna(row[start_key]) or pd.isna(row[end_key]) or pd.isna(row["year"]):
        return None
    year = int(row["year"])
    first = date(year, 1, 1)
    return (
        first + timedelta(days=int(row[start_key]) - 1),
        first + timedelta(days=int(row[end_key]) - 1),
    )


def aggregate_manual_six_windows(
    panel: pd.DataFrame,
    month_codes: Sequence[int],
    scale_values: Mapping[int, np.ndarray],
    *,
    cell_index_column: str,
    cell_index_offset: int = 0,
    minimum_coverage: float = 0.9,
    deficit_threshold: float = -1.0,
) -> pd.DataFrame:
    """Return one manual SPEI-1/3 row per panel-row and frozen window."""

    required_scales = {1, 3}
    if set(scale_values) != required_scales:
        raise ValueError("Manual aggregation requires exactly SPEI-1 and SPEI-3")
    codes = np.asarray(month_codes, dtype=np.int32)
    for scale, values in scale_values.items():
        if np.asarray(values).ndim != 2 or np.asarray(values).shape[0] != codes.size:
            raise ValueError(f"SPEI-{scale} cache must be month x cell")
    rows: list[dict[str, object]] = []
    key_columns = [
        name
        for name in ("era01_cell_id", "grid_id_v3", "grid_id", "year", "latitude", "longitude")
        if name in panel.columns
    ]
    for row_index, series in panel.iterrows():
        row = series.to_dict()
        cell_index = int(row[cell_index_column]) - int(cell_index_offset)
        if cell_index < 0:
            raise IndexError("Panel cell index precedes the SPEI cache block")
        for window in WINDOW_NAMES:
            output: dict[str, object] = {name: row[name] for name in key_columns}
            output.update({"source_row": row_index, "window": window})
            bounds = _window_dates(row, window)
            for scale in (1, 3):
                prefix = f"chm_spei_s{scale}"
                if bounds is None:
                    summary = ManualWindowSummary(
                        math.nan, math.nan, math.nan, math.nan, 0, 0, math.nan
                    )
                else:
                    summary = summarize_manual_window(
                        codes,
                        np.asarray(scale_values[scale])[:, cell_index],
                        window_start=bounds[0],
                        window_end=bounds[1],
                        minimum_coverage=minimum_coverage,
                        deficit_threshold=deficit_threshold,
                    )
                output.update(
                    {
                        f"{prefix}_mean": summary.mean,
                        f"{prefix}_min": summary.min_spei,
                        f"{prefix}_min_spei": summary.min_spei,
                        f"{prefix}_end": summary.end,
                        f"{prefix}_coverage": summary.coverage,
                        f"{prefix}_valid_days": summary.valid_days,
                        f"{prefix}_peak_threshold_deficit": summary.peak_threshold_deficit,
                    }
                )
            rows.append(output)
    return pd.DataFrame(rows)


def _dynamic_value(
    year: int,
    start: date,
    end: date,
    cell_index: int,
    month_lookup: Mapping[int, int],
    scale_values: Mapping[int, np.ndarray],
) -> tuple[float, int, int]:
    if start.year != year or end.year != year:
        raise ValueError("Dynamic windows must be clipped to one calendar year")
    actual_scale = min(max(end.month - start.month + 1, 1), 12)
    code = year * 100 + end.month
    if actual_scale not in scale_values or code not in month_lookup:
        return math.nan, actual_scale, end.month
    value = _finite(np.asarray(scale_values[actual_scale])[month_lookup[code], cell_index])
    return (math.nan if value is None else value), actual_scale, end.month


def dynamic_ext_six_windows(
    panel: pd.DataFrame,
    target_month_codes: Sequence[int],
    nearest_scale_values: Mapping[int, np.ndarray],
    *,
    cell_index_column: str,
    cell_index_offset: int = 0,
) -> pd.DataFrame:
    """Apply the V3 dynamic-scale/end-month rule to 2010-2019 windows."""

    codes = np.asarray(target_month_codes, dtype=np.int32)
    month_lookup = {int(code): index for index, code in enumerate(codes)}
    rows: list[dict[str, object]] = []
    key_columns = [
        name
        for name in ("era01_cell_id", "grid_id_v3", "grid_id", "year", "latitude", "longitude")
        if name in panel.columns
    ]
    for row_index, series in panel.iterrows():
        row = series.to_dict()
        year = int(row["year"])
        cell_index = int(row[cell_index_column]) - int(cell_index_offset)
        if cell_index < 0:
            raise IndexError("Panel cell index precedes the SPEI cache block")
        for window in WINDOW_NAMES:
            output = {name: row[name] for name in key_columns}
            output.update({"source_row": row_index, "window": window})
            bounds = _window_dates(row, window)
            if bounds is None:
                value, scale, end_month = math.nan, None, None
            else:
                value, scale, end_month = _dynamic_value(
                    year,
                    bounds[0],
                    bounds[1],
                    cell_index,
                    month_lookup,
                    nearest_scale_values,
                )
            output.update(
                {
                    "chm_spei_dynamic_ext_value": value,
                    "chm_spei_dynamic_ext_actual_scale": scale,
                    "chm_spei_dynamic_ext_end_month": end_month,
                }
            )
            rows.append(output)
    return pd.DataFrame(rows)


def legacy_v3_exact_sidecar(
    v3: pd.DataFrame,
    target_month_codes: Sequence[int],
    nearest_scale_values: Mapping[int, np.ndarray],
    *,
    cell_index_column: str,
    expected_rows: int = 69_038,
    tolerance: float = 1e-6,
) -> pd.DataFrame:
    """Rebuild and verify all twelve legacy V3 SPEI fields."""

    if len(v3) != int(expected_rows):
        raise AssertionError(f"Legacy V3 row count is {len(v3)}, expected {expected_rows}")
    legacy_columns = [field for pair in LEGACY_FIELD_MAP.values() for field in pair]
    missing = [column for column in legacy_columns if column not in v3.columns]
    if missing:
        raise KeyError(f"Legacy V3 fields are missing: {missing}")
    codes = np.asarray(target_month_codes, dtype=np.int32)
    month_lookup = {int(code): index for index, code in enumerate(codes)}
    computed = {column: np.full(len(v3), np.nan, dtype=np.float64) for column in legacy_columns}
    for position, (_, series) in enumerate(v3.iterrows()):
        row = series.to_dict()
        year = int(row["year"])
        cell_index = int(row[cell_index_column])
        for window, fields in LEGACY_FIELD_MAP.items():
            bounds = _window_dates(row, window)
            if bounds is None:
                value = math.nan
            else:
                value, _scale, _month = _dynamic_value(
                    year,
                    bounds[0],
                    bounds[1],
                    cell_index,
                    month_lookup,
                    nearest_scale_values,
                )
            computed[fields[0]][position] = value
            computed[fields[1]][position] = value

    maximum_difference = 0.0
    compared = 0
    for column in legacy_columns:
        expected = v3[column].to_numpy(dtype=np.float64)
        actual = computed[column]
        one_missing = np.isnan(expected) ^ np.isnan(actual)
        if np.any(one_missing):
            raise AssertionError(f"Legacy V3 missingness differs for {column}")
        finite = np.isfinite(expected) & np.isfinite(actual)
        if np.any(finite):
            differences = np.abs(expected[finite] - actual[finite])
            field_maximum = float(differences.max())
            maximum_difference = max(maximum_difference, field_maximum)
            compared += int(finite.sum())
            if field_maximum > tolerance:
                raise AssertionError(
                    f"Legacy V3 field {column} max abs difference {field_maximum} exceeds {tolerance}"
                )
    key_columns = [
        column
        for column in ("grid_id", "year", "latitude", "longitude")
        if column in v3.columns
    ]
    sidecar = pd.concat(
        [v3[key_columns].reset_index(drop=True), pd.DataFrame(computed)], axis=1
    )
    sidecar.attrs.update(
        {
            "rows": len(sidecar),
            "fields": len(legacy_columns),
            "compared_values": compared,
            "max_absolute_difference": maximum_difference,
            "tolerance": float(tolerance),
        }
    )
    return sidecar


@dataclass(frozen=True)
class SpeiRunWindowSummary:
    any_event: bool
    event_count: int
    window_duration_days: int
    window_duration_periods: float
    window_max_duration_days: int
    complete_duration_days: int
    complete_duration_periods: int
    complete_max_duration_days: int
    severity: float
    mean_intensity: float
    min_spei: float
    peak_threshold_deficit: float
    left_censored_events: int
    right_censored_events: int


def monthly_records(month_codes: Sequence[int], values: Sequence[float]) -> tuple[SpeiRecord, ...]:
    codes = np.asarray(month_codes, dtype=np.int32)
    series = np.asarray(values, dtype=np.float64)
    if codes.shape != series.shape or codes.ndim != 1:
        raise ValueError("month_codes and values must be equal-length vectors")
    return tuple(
        SpeiRecord.month(int(code) // 100, int(code) % 100, _finite(value))
        for code, value in zip(codes, series, strict=True)
    )


def detect_manual_spei_events(
    month_codes: Sequence[int], values: Sequence[float], *, threshold: float, min_months: int
) -> list[SpeiEvent]:
    """Detect events on the complete 1961-2022 monthly sequence."""

    return detect_spei_runs(
        monthly_records(month_codes, values),
        threshold=threshold,
        min_periods=min_months,
        event_id_prefix=f"spei-k{str(threshold).replace('.', 'p')}-m{min_months}",
    )


def summarize_spei_events_for_window(
    events: Sequence[SpeiEvent], *, window_start: date, window_end: date
) -> SpeiRunWindowSummary:
    """Aggregate complete monthly events after proportional window intersection.

    SPEI severity follows the manual's native-period definition
    ``sum(K - SPEI)``.  A partly overlapping month therefore contributes its
    deficit multiplied by ``overlap_days / month_days``.  Calendar-day
    duration is retained separately for panel interpretation.
    """

    bridges = []
    overlapping_records: list[SpeiRecord] = []
    complete_duration = 0
    complete_periods = 0
    complete_max_duration = 0
    window_periods = 0.0
    left = 0
    right = 0
    threshold = events[0].threshold if events else math.nan
    for event in events:
        bridge = event_window_bridge_for_spei(
            event, window_start=window_start, window_end=window_end
        )
        if bridge is None:
            continue
        bridges.append(bridge)
        complete_duration += event.duration_days
        complete_periods += event.period_count
        complete_max_duration = max(complete_max_duration, event.duration_days)
        left += int(bridge.left_censored)
        right += int(bridge.right_censored)
        for record in event.records:
            if record.support_start <= window_end and record.support_end_exclusive > window_start:
                overlapping_records.append(record)
                overlap_start = max(record.support_start, window_start)
                overlap_end = min(record.support_end_exclusive, window_end + timedelta(days=1))
                window_periods += (overlap_end - overlap_start).days / record.days
    if not bridges:
        return SpeiRunWindowSummary(
            any_event=False,
            event_count=0,
            window_duration_days=0,
            window_duration_periods=0.0,
            window_max_duration_days=0,
            complete_duration_days=0,
            complete_duration_periods=0,
            complete_max_duration_days=0,
            severity=0.0,
            mean_intensity=math.nan,
            min_spei=math.nan,
            peak_threshold_deficit=math.nan,
            left_censored_events=0,
            right_censored_events=0,
        )
    duration = sum(item.active_duration for item in bridges)
    severity = sum(item.severity for item in bridges)
    minimum = min(
        float(record.value) for record in overlapping_records if record.value is not None
    )
    return SpeiRunWindowSummary(
        any_event=True,
        event_count=len(bridges),
        window_duration_days=duration,
        window_duration_periods=window_periods,
        window_max_duration_days=max(item.active_duration for item in bridges),
        complete_duration_days=complete_duration,
        complete_duration_periods=complete_periods,
        complete_max_duration_days=complete_max_duration,
        severity=severity,
        mean_intensity=severity / window_periods,
        min_spei=minimum,
        peak_threshold_deficit=max(threshold - minimum, 0.0),
        left_censored_events=left,
        right_censored_events=right,
    )


def _spei_event_window_support(
    event: SpeiEvent,
    *,
    window_start: date,
    window_end: date,
) -> tuple[float, float]:
    """Return overlapping native-period equivalents and minimum SPEI."""

    period_equivalents = 0.0
    values: list[float] = []
    window_end_exclusive = window_end + timedelta(days=1)
    for record in event.records:
        overlap_start = max(record.support_start, window_start)
        overlap_end = min(record.support_end_exclusive, window_end_exclusive)
        overlap_days = max((overlap_end - overlap_start).days, 0)
        if overlap_days == 0:
            continue
        period_equivalents += overlap_days / record.days
        if record.value is not None:
            values.append(float(record.value))
    return period_equivalents, min(values) if values else math.nan


def aggregate_manual_spei_event_six_windows(
    panel: pd.DataFrame,
    month_codes: Sequence[int],
    scale_values: Mapping[int, np.ndarray],
    *,
    cell_index_column: str,
    cell_index_offset: int = 0,
    minimum_coverage: float = 0.9,
    event_specs: Mapping[str, tuple[float, int]] = MANUAL_EVENT_SPECS,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build six-window SPEI run aggregates plus complete-event audit tables.

    Events are detected once on each cell's complete monthly source sequence.
    Only afterward are they intersected with the six frozen phenology windows.
    Window aggregates fail closed when the corresponding SPEI scale has less
    than ``minimum_coverage`` observed day support.  The event table contains
    complete events that overlap at least one requested panel window, and the
    bridge table preserves proportional monthly severity and censoring.
    """

    required_scales = {1, 3}
    if set(scale_values) != required_scales:
        raise ValueError("Manual event aggregation requires exactly SPEI-1 and SPEI-3")
    if cell_index_column not in panel.columns:
        raise KeyError(f"Panel is missing cell index column {cell_index_column}")
    if not 0.0 <= float(minimum_coverage) <= 1.0:
        raise ValueError("minimum_coverage must lie in [0, 1]")
    if not event_specs:
        raise ValueError("event_specs must not be empty")
    normalized_specs: dict[str, tuple[float, int]] = {}
    for name, (threshold, min_months) in event_specs.items():
        if not str(name):
            raise ValueError("Event specification names must be non-empty")
        if not math.isfinite(float(threshold)) or int(min_months) <= 0:
            raise ValueError("Each event specification needs a finite threshold and positive duration")
        normalized_specs[str(name)] = (float(threshold), int(min_months))

    codes = np.asarray(month_codes, dtype=np.int32)
    if codes.ndim != 1 or codes.size == 0 or np.any(np.diff(codes) <= 0):
        raise ValueError("month_codes must be a non-empty strictly increasing vector")
    arrays = {scale: np.asarray(values) for scale, values in scale_values.items()}
    n_cells = arrays[1].shape[1] if arrays[1].ndim == 2 else 0
    for scale, values in arrays.items():
        if values.ndim != 2 or values.shape[0] != codes.size:
            raise ValueError(f"SPEI-{scale} cache must be month x cell")
        if values.shape[1] != n_cells:
            raise ValueError("SPEI-1 and SPEI-3 caches must share their cell dimension")

    cell_indices = (
        panel[cell_index_column].to_numpy(dtype=np.int64) - int(cell_index_offset)
    )
    if np.any(cell_indices < 0) or np.any(cell_indices >= n_cells):
        raise IndexError("Panel cell indices fall outside the SPEI cache")
    key_columns = [
        name
        for name in (
            "era01_cell_id",
            "grid_id_v3",
            "grid_id",
            "year",
            "latitude",
            "longitude",
        )
        if name in panel.columns
    ]
    cell_key_columns = [name for name in key_columns if name != "year"]
    cell_metadata: dict[int, dict[str, object]] = {}
    for _, series in panel.iterrows():
        global_cell_index = int(series[cell_index_column])
        cell_index = global_cell_index - int(cell_index_offset)
        metadata = {name: series[name] for name in cell_key_columns}
        previous = cell_metadata.setdefault(cell_index, metadata)
        if any(
            not (
                (pd.isna(previous[name]) and pd.isna(metadata[name]))
                or previous[name] == metadata[name]
            )
            for name in cell_key_columns
        ):
            raise ValueError(f"Cell index {cell_index} maps to inconsistent panel identities")

    event_cache: dict[tuple[int, int, str], list[SpeiEvent]] = {}
    public_ids: dict[tuple[int, int, str, str], str] = {}
    event_payloads: dict[str, dict[str, object]] = {}
    for cell_index in sorted(cell_metadata):
        metadata = cell_metadata[cell_index]
        global_cell_index = cell_index + int(cell_index_offset)
        raw_identifier = metadata.get("era01_cell_id", global_cell_index)
        identifier = (
            int(raw_identifier) if not pd.isna(raw_identifier) else global_cell_index
        )
        for scale in (1, 3):
            vector = arrays[scale][:, cell_index]
            for spec_name, (threshold, min_months) in normalized_specs.items():
                events = detect_manual_spei_events(
                    codes,
                    vector,
                    threshold=threshold,
                    min_months=min_months,
                )
                event_cache[(cell_index, scale, spec_name)] = events
                for event_number, event in enumerate(events, start=1):
                    public_id = (
                        f"{identifier}:chm_spei_s{scale}_{spec_name}:{event_number:04d}"
                    )
                    public_ids[(cell_index, scale, spec_name, event.event_id)] = public_id
                    event_start_code = event.start.year * 100 + event.start.month
                    event_end_code = event.end.year * 100 + event.end.month
                    start_index = int(np.searchsorted(codes, event_start_code))
                    end_index = int(np.searchsorted(codes, event_end_code))
                    valid_source = np.isfinite(vector)
                    source_left_censored = not bool(
                        valid_source[:start_index].any()
                    )
                    source_right_censored = not bool(
                        valid_source[end_index + 1 :].any()
                    )
                    event_payloads[public_id] = {
                        **metadata,
                        "event_id": public_id,
                        "scale_months": scale,
                        "variant": spec_name,
                        "threshold": threshold,
                        "minimum_duration_months": min_months,
                        "start_date": event.start,
                        "end_date": event.end,
                        "period_count": event.period_count,
                        "duration_days": event.duration_days,
                        "severity_spei_periods": event.severity,
                        "mean_intensity_spei": event.mean_intensity,
                        "min_spei": event.min_spei,
                        "peak_threshold_deficit": event.peak_threshold_deficit,
                        "source_left_censored": source_left_censored,
                        "source_right_censored": source_right_censored,
                    }

    rows: list[dict[str, object]] = []
    bridge_rows: list[dict[str, object]] = []
    retained_event_ids: set[str] = set()
    for source_row, series in panel.iterrows():
        row = series.to_dict()
        cell_index = int(row[cell_index_column]) - int(cell_index_offset)
        for window in WINDOW_NAMES:
            output: dict[str, object] = {name: row[name] for name in key_columns}
            output.update({"source_row": source_row, "window": window})
            bounds = _window_dates(row, window)
            for scale in (1, 3):
                if bounds is None:
                    coverage_summary = ManualWindowSummary(
                        math.nan, math.nan, math.nan, math.nan, 0, 0, math.nan
                    )
                else:
                    coverage_summary = summarize_manual_window(
                        codes,
                        arrays[scale][:, cell_index],
                        window_start=bounds[0],
                        window_end=bounds[1],
                        minimum_coverage=minimum_coverage,
                    )
                scale_prefix = f"chm_spei_s{scale}_event"
                output[f"{scale_prefix}_coverage"] = coverage_summary.coverage
                output[f"{scale_prefix}_valid_days"] = coverage_summary.valid_days
                output[f"{scale_prefix}_expected_days"] = coverage_summary.expected_days
                coverage_valid = (
                    bounds is not None
                    and math.isfinite(coverage_summary.coverage)
                    and coverage_summary.coverage >= minimum_coverage
                    and math.isfinite(coverage_summary.min_spei)
                )
                for spec_name, (threshold, _min_months) in normalized_specs.items():
                    stem = f"chm_spei_s{scale}_{spec_name}"
                    events = event_cache[(cell_index, scale, spec_name)]
                    summary = (
                        summarize_spei_events_for_window(
                            events, window_start=bounds[0], window_end=bounds[1]
                        )
                        if bounds is not None
                        else SpeiRunWindowSummary(
                            False,
                            0,
                            0,
                            0.0,
                            0,
                            0,
                            0,
                            0,
                            0.0,
                            math.nan,
                            math.nan,
                            math.nan,
                            0,
                            0,
                        )
                    )
                    if coverage_valid:
                        values: dict[str, object] = {
                            "any": float(summary.any_event),
                            "count": summary.event_count,
                            "window_total_duration_days": summary.window_duration_days,
                            "window_total_duration_periods_equiv": summary.window_duration_periods,
                            "window_max_duration_days": summary.window_max_duration_days,
                            "complete_total_duration_days": summary.complete_duration_days,
                            "complete_total_duration_months": summary.complete_duration_periods,
                            "complete_max_duration_days": summary.complete_max_duration_days,
                            "severity_spei_periods": summary.severity,
                            "mean_intensity_spei": summary.mean_intensity,
                            "event_min_spei": summary.min_spei,
                            "window_min_spei": coverage_summary.min_spei,
                            "peak_threshold_deficit": summary.peak_threshold_deficit,
                            "left_censored_count": summary.left_censored_events,
                            "right_censored_count": summary.right_censored_events,
                        }
                    else:
                        values = {
                            name: math.nan
                            for name in (
                                "any",
                                "count",
                                "window_total_duration_days",
                                "window_total_duration_periods_equiv",
                                "window_max_duration_days",
                                "complete_total_duration_days",
                                "complete_total_duration_months",
                                "complete_max_duration_days",
                                "severity_spei_periods",
                                "mean_intensity_spei",
                                "event_min_spei",
                                "window_min_spei",
                                "peak_threshold_deficit",
                                "left_censored_count",
                                "right_censored_count",
                            )
                        }
                    output.update({f"{stem}_{name}": value for name, value in values.items()})

                    if bounds is None:
                        continue
                    for event in events:
                        bridge = event_window_bridge_for_spei(
                            event, window_start=bounds[0], window_end=bounds[1]
                        )
                        if bridge is None:
                            continue
                        public_id = public_ids[
                            (cell_index, scale, spec_name, event.event_id)
                        ]
                        retained_event_ids.add(public_id)
                        period_equivalents, minimum = _spei_event_window_support(
                            event, window_start=bounds[0], window_end=bounds[1]
                        )
                        bridge_rows.append(
                            {
                                **{name: row[name] for name in key_columns},
                                "source_row": source_row,
                                "window": window,
                                "event_id": public_id,
                                "scale_months": scale,
                                "variant": spec_name,
                                "threshold": threshold,
                                "window_coverage": coverage_summary.coverage,
                                "window_coverage_ok": coverage_valid,
                                "event_count": 1,
                                "window_duration_days": bridge.active_duration,
                                "window_duration_periods_equiv": period_equivalents,
                                "complete_duration_days": event.duration_days,
                                "complete_duration_months": event.period_count,
                                "severity_spei_periods": bridge.severity,
                                "mean_intensity_spei": (
                                    bridge.severity / period_equivalents
                                    if period_equivalents > 0
                                    else math.nan
                                ),
                                "min_spei": minimum,
                                "peak_threshold_deficit": (
                                    max(threshold - minimum, 0.0)
                                    if math.isfinite(minimum)
                                    else math.nan
                                ),
                                "left_censored": bridge.left_censored,
                                "right_censored": bridge.right_censored,
                                "source_left_censored": event_payloads[public_id][
                                    "source_left_censored"
                                ],
                                "source_right_censored": event_payloads[public_id][
                                    "source_right_censored"
                                ],
                            }
                        )
            rows.append(output)

    long = pd.DataFrame(rows)
    if len(long) != len(panel) * len(WINDOW_NAMES):
        raise AssertionError("SPEI event long table is not panel x six windows")
    if long.duplicated(["source_row", "window"]).any():
        raise AssertionError("SPEI event long table key is not unique")
    event_frame = pd.DataFrame(
        [event_payloads[event_id] for event_id in event_payloads if event_id in retained_event_ids]
    )
    bridge_frame = pd.DataFrame(bridge_rows)
    return long, event_frame, bridge_frame


@dataclass(frozen=True)
class TwoWeekWindowCoverage:
    coverage: float
    valid_days: int
    expected_days: int
    min_spei: float


def summarize_two_week_window(
    records: Sequence[SpeiRecord],
    *,
    window_start: date,
    window_end: date,
    minimum_coverage: float = 0.9,
) -> TwoWeekWindowCoverage:
    """Summarize valid forward-state support, counting release gaps as missing."""

    if window_end < window_start:
        raise ValueError("window_end must not precede window_start")
    expected_days = (window_end - window_start).days + 1
    window_end_exclusive = window_end + timedelta(days=1)
    valid_days = 0
    values: list[float] = []
    for record in records:
        overlap_start = max(record.support_start, window_start)
        overlap_end = min(record.support_end_exclusive, window_end_exclusive)
        overlap_days = max((overlap_end - overlap_start).days, 0)
        if overlap_days and record.value is not None:
            valid_days += overlap_days
            values.append(float(record.value))
    coverage = valid_days / expected_days
    minimum = (
        min(values)
        if coverage >= float(minimum_coverage) and values
        else math.nan
    )
    return TwoWeekWindowCoverage(
        coverage=coverage,
        valid_days=valid_days,
        expected_days=expected_days,
        min_spei=minimum,
    )


def detect_two_week_spei_events(
    release_dates: Sequence[date],
    values: Sequence[float],
    *,
    threshold: float,
    min_units: int,
    accumulation_days: int = 14,
    state_days: int = 7,
    accumulation_timestamp_position: str = "end",
    state_timestamp_position: str = "start",
) -> list[SpeiEvent]:
    """Detect runs on non-overlapping forward states; gaps and NaNs interrupt."""

    records = spei_2w_records(
        release_dates,
        values,
        accumulation_days=int(accumulation_days),
        state_days=int(state_days),
        accumulation_timestamp_position=accumulation_timestamp_position,
        state_timestamp_position=state_timestamp_position,
    )
    return detect_spei_runs(
        records,
        threshold=float(threshold),
        min_periods=int(min_units),
        event_id_prefix=(
            f"spei-2w-k{str(float(threshold)).replace('.', 'p')}-u{int(min_units)}"
        ),
    )


def _merge_spei_window_metrics(
    left: pd.DataFrame,
    right: pd.DataFrame,
) -> pd.DataFrame:
    keys = [
        name
        for name in (
            "source_row",
            "era01_cell_id",
            "grid_id_v3",
            "grid_id",
            "year",
            "latitude",
            "longitude",
            "window",
        )
        if name in left.columns and name in right.columns
    ]
    if "source_row" not in keys or "window" not in keys:
        raise KeyError("SPEI window metrics require source_row and window keys")
    metrics = [name for name in right.columns if name not in keys]
    if set(metrics).intersection(left.columns):
        raise ValueError("SPEI monthly and 2W metric names must be disjoint")
    return left.merge(
        right[keys + metrics],
        on=keys,
        how="left",
        validate="one_to_one",
    )


def aggregate_two_week_spei_event_six_windows(
    panel: pd.DataFrame,
    release_dates: Sequence[date],
    values: np.ndarray,
    *,
    cell_index_column: str,
    cell_index_offset: int = 0,
    minimum_coverage: float = 0.9,
    accumulation_days: int = 14,
    state_days: int = 7,
    accumulation_timestamp_position: str = "end",
    state_timestamp_position: str = "start",
    event_specs: Mapping[str, tuple[float, int]] = TWO_WEEK_EVENT_SPECS,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build 2W run metrics, complete events, and window bridge records."""

    if cell_index_column not in panel.columns:
        raise KeyError(f"Panel is missing cell index column {cell_index_column}")
    if not 0.0 <= float(minimum_coverage) <= 1.0:
        raise ValueError("minimum_coverage must lie in [0, 1]")
    release_tuple = tuple(release_dates)
    arrays = np.asarray(values)
    if arrays.ndim != 2 or arrays.shape[0] != len(release_tuple):
        raise ValueError("SPEI-2W values must be release x cell")
    # This validates duplicate/order/cadence and constructs the fixed state support.
    contracts = spei_2w_interval_contracts(
        release_tuple,
        accumulation_days=int(accumulation_days),
        state_days=int(state_days),
        accumulation_timestamp_position=accumulation_timestamp_position,
        state_timestamp_position=state_timestamp_position,
    )
    normalized_specs = {
        str(name): (float(threshold), int(min_units))
        for name, (threshold, min_units) in event_specs.items()
    }
    if not normalized_specs or any(
        not name or not math.isfinite(threshold) or min_units <= 0
        for name, (threshold, min_units) in normalized_specs.items()
    ):
        raise ValueError("SPEI-2W event specifications are invalid")
    cell_indices = (
        panel[cell_index_column].to_numpy(dtype=np.int64) - int(cell_index_offset)
    )
    if np.any(cell_indices < 0) or np.any(cell_indices >= arrays.shape[1]):
        raise IndexError("Panel cell indices fall outside the SPEI-2W cache")
    key_columns = [
        name
        for name in (
            "era01_cell_id",
            "grid_id_v3",
            "grid_id",
            "year",
            "latitude",
            "longitude",
        )
        if name in panel.columns
    ]
    cell_key_columns = [name for name in key_columns if name != "year"]
    cell_metadata: dict[int, dict[str, object]] = {}
    for _, series in panel.iterrows():
        cell_index = int(series[cell_index_column]) - int(cell_index_offset)
        metadata = {name: series[name] for name in cell_key_columns}
        previous = cell_metadata.setdefault(cell_index, metadata)
        if any(
            not (
                (pd.isna(previous[name]) and pd.isna(metadata[name]))
                or previous[name] == metadata[name]
            )
            for name in cell_key_columns
        ):
            raise ValueError(f"Cell index {cell_index} has inconsistent identity")

    records_by_cell: dict[int, tuple[SpeiRecord, ...]] = {}
    event_cache: dict[tuple[int, str], list[SpeiEvent]] = {}
    public_ids: dict[tuple[int, str, str], str] = {}
    event_payloads: dict[str, dict[str, object]] = {}
    release_position = {
        item.label_date.isoformat(): position
        for position, item in enumerate(contracts)
    }
    for cell_index in sorted(cell_metadata):
        vector = arrays[:, cell_index]
        records = spei_2w_records(
            release_tuple,
            vector,
            accumulation_days=int(accumulation_days),
            state_days=int(state_days),
            accumulation_timestamp_position=accumulation_timestamp_position,
            state_timestamp_position=state_timestamp_position,
        )
        records_by_cell[cell_index] = records
        valid_source = np.isfinite(vector)
        metadata = cell_metadata[cell_index]
        raw_identifier = metadata.get(
            "era01_cell_id", cell_index + int(cell_index_offset)
        )
        identifier = (
            int(raw_identifier)
            if not pd.isna(raw_identifier)
            else cell_index + int(cell_index_offset)
        )
        for spec_name, (threshold, min_units) in normalized_specs.items():
            events = detect_spei_runs(
                records,
                threshold=threshold,
                min_periods=min_units,
                event_id_prefix=f"spei-2w-{spec_name}",
            )
            event_cache[(cell_index, spec_name)] = events
            for event_number, event in enumerate(events, start=1):
                public_id = (
                    f"{identifier}:chm_spei_2w_{spec_name}:{event_number:04d}"
                )
                public_ids[(cell_index, spec_name, event.event_id)] = public_id
                start_position = release_position[str(event.records[0].label)]
                end_position = release_position[str(event.records[-1].label)]
                first_contract = contracts[start_position]
                last_contract = contracts[end_position]
                left_adjacent_known = (
                    start_position > 0
                    and (
                        first_contract.label_date
                        - contracts[start_position - 1].label_date
                    ).days
                    == int(state_days)
                    and bool(valid_source[start_position - 1])
                )
                right_adjacent_known = (
                    end_position + 1 < len(contracts)
                    and (
                        contracts[end_position + 1].label_date
                        - last_contract.label_date
                    ).days
                    == int(state_days)
                    and bool(valid_source[end_position + 1])
                )
                event_payloads[public_id] = {
                    **metadata,
                    "event_id": public_id,
                    "timescale": "2W",
                    "variant": spec_name,
                    "threshold": threshold,
                    "minimum_duration_releases": min_units,
                    "accumulation_days": int(accumulation_days),
                    "state_days": int(state_days),
                    "start_date": event.start,
                    "end_date": event.end,
                    "first_release_date": first_contract.label_date,
                    "last_release_date": last_contract.label_date,
                    "first_accumulation_start": first_contract.accumulation_start,
                    "last_accumulation_end": (
                        last_contract.accumulation_end_exclusive
                        - timedelta(days=1)
                    ),
                    "release_count": event.period_count,
                    "duration_days": event.duration_days,
                    "severity_spei_releases": event.severity,
                    "mean_intensity_spei": event.mean_intensity,
                    "min_spei": event.min_spei,
                    "peak_threshold_deficit": event.peak_threshold_deficit,
                    "source_left_censored": not left_adjacent_known,
                    "source_right_censored": not right_adjacent_known,
                }

    rows: list[dict[str, object]] = []
    bridge_rows: list[dict[str, object]] = []
    retained_event_ids: set[str] = set()
    empty_summary = SpeiRunWindowSummary(
        False, 0, 0, 0.0, 0, 0, 0, 0, 0.0,
        math.nan, math.nan, math.nan, 0, 0,
    )
    for source_row, series in panel.iterrows():
        row = series.to_dict()
        cell_index = int(row[cell_index_column]) - int(cell_index_offset)
        records = records_by_cell[cell_index]
        for window in WINDOW_NAMES:
            output = {name: row[name] for name in key_columns}
            output.update({"source_row": source_row, "window": window})
            bounds = _window_dates(row, window)
            coverage = (
                summarize_two_week_window(
                    records,
                    window_start=bounds[0],
                    window_end=bounds[1],
                    minimum_coverage=minimum_coverage,
                )
                if bounds is not None
                else TwoWeekWindowCoverage(math.nan, 0, 0, math.nan)
            )
            coverage_valid = (
                bounds is not None
                and math.isfinite(coverage.coverage)
                and coverage.coverage >= minimum_coverage
                and math.isfinite(coverage.min_spei)
            )
            output.update(
                {
                    "chm_spei_2w_event_coverage": coverage.coverage,
                    "chm_spei_2w_event_valid_days": coverage.valid_days,
                    "chm_spei_2w_event_expected_days": coverage.expected_days,
                }
            )
            for spec_name, (threshold, _min_units) in normalized_specs.items():
                stem = f"chm_spei_2w_{spec_name}"
                events = event_cache[(cell_index, spec_name)]
                summary = (
                    summarize_spei_events_for_window(
                        events, window_start=bounds[0], window_end=bounds[1]
                    )
                    if bounds is not None
                    else empty_summary
                )
                if coverage_valid:
                    metric_values: dict[str, object] = {
                        "any": float(summary.any_event),
                        "count": summary.event_count,
                        "window_total_duration_days": summary.window_duration_days,
                        "window_total_duration_releases_equiv": summary.window_duration_periods,
                        "window_max_duration_days": summary.window_max_duration_days,
                        "complete_total_duration_days": summary.complete_duration_days,
                        "complete_total_duration_releases": summary.complete_duration_periods,
                        "complete_max_duration_days": summary.complete_max_duration_days,
                        "severity_spei_releases": summary.severity,
                        "mean_intensity_spei": summary.mean_intensity,
                        "event_min_spei": summary.min_spei,
                        "window_min_spei": coverage.min_spei,
                        "peak_threshold_deficit": summary.peak_threshold_deficit,
                        "left_censored_count": summary.left_censored_events,
                        "right_censored_count": summary.right_censored_events,
                    }
                else:
                    metric_values = {
                        name: math.nan
                        for name in (
                            "any",
                            "count",
                            "window_total_duration_days",
                            "window_total_duration_releases_equiv",
                            "window_max_duration_days",
                            "complete_total_duration_days",
                            "complete_total_duration_releases",
                            "complete_max_duration_days",
                            "severity_spei_releases",
                            "mean_intensity_spei",
                            "event_min_spei",
                            "window_min_spei",
                            "peak_threshold_deficit",
                            "left_censored_count",
                            "right_censored_count",
                        )
                    }
                output.update(
                    {f"{stem}_{name}": value for name, value in metric_values.items()}
                )
                if bounds is None:
                    continue
                for event in events:
                    bridge = event_window_bridge_for_spei(
                        event, window_start=bounds[0], window_end=bounds[1]
                    )
                    if bridge is None:
                        continue
                    public_id = public_ids[
                        (cell_index, spec_name, event.event_id)
                    ]
                    retained_event_ids.add(public_id)
                    release_equivalents, minimum = _spei_event_window_support(
                        event, window_start=bounds[0], window_end=bounds[1]
                    )
                    bridge_rows.append(
                        {
                            **{name: row[name] for name in key_columns},
                            "source_row": source_row,
                            "window": window,
                            "event_id": public_id,
                            "timescale": "2W",
                            "variant": spec_name,
                            "threshold": threshold,
                            "accumulation_days": int(accumulation_days),
                            "state_days": int(state_days),
                            "window_coverage": coverage.coverage,
                            "window_coverage_ok": coverage_valid,
                            "event_count": 1,
                            "window_duration_days": bridge.active_duration,
                            "window_duration_releases_equiv": release_equivalents,
                            "complete_duration_days": event.duration_days,
                            "complete_duration_releases": event.period_count,
                            "severity_spei_releases": bridge.severity,
                            "mean_intensity_spei": (
                                bridge.severity / release_equivalents
                                if release_equivalents > 0
                                else math.nan
                            ),
                            "min_spei": minimum,
                            "peak_threshold_deficit": (
                                max(threshold - minimum, 0.0)
                                if math.isfinite(minimum)
                                else math.nan
                            ),
                            "left_censored": bridge.left_censored,
                            "right_censored": bridge.right_censored,
                            "source_left_censored": event_payloads[public_id][
                                "source_left_censored"
                            ],
                            "source_right_censored": event_payloads[public_id][
                                "source_right_censored"
                            ],
                        }
                    )
            rows.append(output)
    long = pd.DataFrame(rows)
    if len(long) != len(panel) * len(WINDOW_NAMES):
        raise AssertionError("SPEI-2W long table is not panel x six windows")
    if long.duplicated(["source_row", "window"]).any():
        raise AssertionError("SPEI-2W long table key is not unique")
    event_frame = pd.DataFrame(
        [
            payload
            for event_id, payload in event_payloads.items()
            if event_id in retained_event_ids
        ]
    )
    if event_frame.empty:
        event_frame = pd.DataFrame(
            {
                "event_id": pd.Series(dtype="string"),
                "timescale": pd.Series(dtype="string"),
            }
        )
    bridge_frame = pd.DataFrame(bridge_rows)
    if bridge_frame.empty:
        bridge_frame = pd.DataFrame(
            {
                "event_id": pd.Series(dtype="string"),
                "timescale": pd.Series(dtype="string"),
            }
        )
    return long, event_frame, bridge_frame


@dataclass(frozen=True)
class SpeiAggregationBlock:
    """One bounded spatial block of the five canonical SPEI tables."""

    cell_start: int
    cell_stop: int
    manual: pd.DataFrame
    dynamic: pd.DataFrame
    event_long: pd.DataFrame
    events: pd.DataFrame
    event_bridges: pd.DataFrame


def iter_spei_aggregation_blocks(
    panel: pd.DataFrame,
    full_month_codes: Sequence[int],
    full_manual_values: Mapping[int, np.ndarray],
    target_month_codes: Sequence[int],
    target_nearest_values: Mapping[int, np.ndarray],
    *,
    cell_index_column: str,
    cell_count: int,
    cell_block_size: int = 128,
    cell_ranges: Sequence[tuple[int, int]] | None = None,
    minimum_coverage: float = 0.9,
    deficit_threshold: float = -1.0,
    event_specs: Mapping[str, tuple[float, int]] = MANUAL_EVENT_SPECS,
    two_week_release_dates: Sequence[date] | None = None,
    two_week_values: np.ndarray | None = None,
    two_week_accumulation_days: int = 14,
    two_week_state_days: int = 7,
    two_week_accumulation_timestamp_position: str = "end",
    two_week_state_timestamp_position: str = "start",
    two_week_event_specs: Mapping[str, tuple[float, int]] = TWO_WEEK_EVENT_SPECS,
) -> Iterator[SpeiAggregationBlock]:
    """Aggregate spatial blocks without materializing the full panel outputs.

    Cache arrays remain month-by-cell memory maps at the call site.  Each
    yielded block slices only ``cell_block_size`` columns and therefore bounds
    both the numeric working set and the temporary Python-row dictionaries.
    Complete 1961--2022 columns are retained inside each slice, so event
    detection and public event numbering are identical to an unblocked call.
    """

    if cell_index_column not in panel.columns:
        raise KeyError(f"Panel is missing cell index column {cell_index_column}")
    if int(cell_count) <= 0:
        raise ValueError("cell_count must be positive")
    if int(cell_block_size) <= 0:
        raise ValueError("cell_block_size must be positive")
    indices = panel[cell_index_column].to_numpy(dtype=np.int64)
    if indices.size == 0 or np.any(indices < 0) or np.any(indices >= int(cell_count)):
        raise IndexError("Panel cell indices fall outside the requested SPEI blocks")

    full_codes = np.asarray(full_month_codes, dtype=np.int32)
    target_codes = np.asarray(target_month_codes, dtype=np.int32)
    for scale in (1, 3):
        values = full_manual_values.get(scale)
        if values is None or getattr(values, "ndim", None) != 2:
            raise ValueError(f"SPEI-{scale} full cache must be month x cell")
        if tuple(values.shape) != (full_codes.size, int(cell_count)):
            raise ValueError(f"SPEI-{scale} full cache has an unexpected shape")
    if not target_nearest_values:
        raise ValueError("Target nearest-neighbour caches must not be empty")
    for scale, values in target_nearest_values.items():
        if getattr(values, "ndim", None) != 2 or tuple(values.shape) != (
            target_codes.size,
            int(cell_count),
        ):
            raise ValueError(f"SPEI-{scale} target cache has an unexpected shape")
    if (two_week_release_dates is None) != (two_week_values is None):
        raise ValueError("SPEI-2W dates and values must be supplied together")
    if two_week_values is not None:
        two_week_array = np.asarray(two_week_values)
        if two_week_array.ndim != 2 or two_week_array.shape != (
            len(tuple(two_week_release_dates or ())),
            int(cell_count),
        ):
            raise ValueError("SPEI-2W cache has an unexpected shape")

    ranges = (
        tuple(
            (start, min(start + int(cell_block_size), int(cell_count)))
            for start in range(0, int(cell_count), int(cell_block_size))
        )
        if cell_ranges is None
        else tuple((int(start), int(stop)) for start, stop in cell_ranges)
    )
    for cell_start, cell_stop in ranges:
        if not 0 <= cell_start < cell_stop <= int(cell_count):
            raise ValueError("Each SPEI cell range must lie within the cache")
        if cell_stop - cell_start > int(cell_block_size):
            raise ValueError("A SPEI cell range exceeds cell_block_size")
        in_block = (indices >= cell_start) & (indices < cell_stop)
        block_panel = panel.loc[in_block].copy()
        if block_panel.empty:
            continue
        block_full = {
            scale: np.asarray(values[:, cell_start:cell_stop])
            for scale, values in full_manual_values.items()
        }
        block_target = {
            scale: np.asarray(values[:, cell_start:cell_stop])
            for scale, values in target_nearest_values.items()
        }
        manual = aggregate_manual_six_windows(
            block_panel,
            full_codes,
            block_full,
            cell_index_column=cell_index_column,
            cell_index_offset=cell_start,
            minimum_coverage=minimum_coverage,
            deficit_threshold=deficit_threshold,
        )
        dynamic = dynamic_ext_six_windows(
            block_panel,
            target_codes,
            block_target,
            cell_index_column=cell_index_column,
            cell_index_offset=cell_start,
        )
        event_long, events, event_bridges = (
            aggregate_manual_spei_event_six_windows(
                block_panel,
                full_codes,
                block_full,
                cell_index_column=cell_index_column,
                cell_index_offset=cell_start,
                minimum_coverage=minimum_coverage,
                event_specs=event_specs,
            )
        )
        if two_week_values is not None and two_week_release_dates is not None:
            two_week_long, two_week_events, two_week_bridges = (
                aggregate_two_week_spei_event_six_windows(
                    block_panel,
                    two_week_release_dates,
                    np.asarray(two_week_values[:, cell_start:cell_stop]),
                    cell_index_column=cell_index_column,
                    cell_index_offset=cell_start,
                    minimum_coverage=minimum_coverage,
                    accumulation_days=two_week_accumulation_days,
                    state_days=two_week_state_days,
                    accumulation_timestamp_position=(
                        two_week_accumulation_timestamp_position
                    ),
                    state_timestamp_position=two_week_state_timestamp_position,
                    event_specs=two_week_event_specs,
                )
            )
            event_long = _merge_spei_window_metrics(event_long, two_week_long)
            events = pd.concat(
                [events, two_week_events], ignore_index=True, sort=False
            )
            event_bridges = pd.concat(
                [event_bridges, two_week_bridges], ignore_index=True, sort=False
            )
        yield SpeiAggregationBlock(
            cell_start=cell_start,
            cell_stop=cell_stop,
            manual=manual,
            dynamic=dynamic,
            event_long=event_long,
            events=events,
            event_bridges=event_bridges,
        )


def write_parquet_partition_new(
    path: str | Path,
    frame: pd.DataFrame,
    *,
    row_group_size: int = 262_144,
) -> Path:
    """Publish one Parquet partition atomically without overwriting a file."""

    import pyarrow as pa
    import pyarrow.parquet as pq

    target = Path(path)
    partial = _new_partial_path(target)
    table = pa.Table.from_pandas(frame, preserve_index=False)
    pq.write_table(
        table,
        partial,
        row_group_size=max(int(row_group_size), 1),
        compression="zstd",
        write_statistics=True,
    )
    if target.exists():
        raise FileExistsError(target)
    os.rename(partial, target)
    return target


def parquet_partition_contract(
    path: str | Path,
    *,
    expected_rows: int | None = None,
    required_columns: Sequence[str] = (),
) -> tuple[bool, int]:
    """Validate a reusable Parquet partition from footer metadata only."""

    import pyarrow.parquet as pq

    target = Path(path)
    try:
        parquet = pq.ParquetFile(target)
        rows = int(parquet.metadata.num_rows)
        columns = set(parquet.schema_arrow.names)
    except (OSError, ValueError):
        return False, 0
    valid = (expected_rows is None or rows == int(expected_rows)) and set(
        required_columns
    ).issubset(columns)
    return bool(valid), rows


def combine_parquet_partitions_new(
    partition_paths: Sequence[str | Path],
    target_path: str | Path,
    *,
    row_group_size: int = 262_144,
    empty_frame: pd.DataFrame | None = None,
) -> tuple[Path, int]:
    """Stream ordered partitions into one canonical Parquet file.

    Only Parquet footers and one bounded record batch are resident at once.
    Schemas are unified permissively to handle a block whose optional values
    are all missing; no pandas concatenation or full-table read occurs.
    """

    import pyarrow as pa
    import pyarrow.parquet as pq

    paths = tuple(Path(item) for item in partition_paths)
    if not paths:
        raise ValueError("At least one Parquet partition is required")
    target = Path(target_path)
    partial = _new_partial_path(target)
    nonempty_paths: list[Path] = []
    total_rows = 0
    schemas: list[pa.Schema] = []
    for path in paths:
        parquet = pq.ParquetFile(path)
        rows = int(parquet.metadata.num_rows)
        total_rows += rows
        if rows > 0:
            nonempty_paths.append(path)
            schemas.append(parquet.schema_arrow.remove_metadata())

    if not nonempty_paths:
        frame = empty_frame if empty_frame is not None else pd.DataFrame()
        table = pa.Table.from_pandas(frame, preserve_index=False)
        pq.write_table(
            table,
            partial,
            row_group_size=max(int(row_group_size), 1),
            compression="zstd",
            write_statistics=True,
        )
    else:
        schema = pa.unify_schemas(schemas, promote_options="permissive")
        writer = pq.ParquetWriter(
            partial,
            schema,
            compression="zstd",
            write_statistics=True,
        )
        try:
            for path in nonempty_paths:
                parquet = pq.ParquetFile(path)
                for batch in parquet.iter_batches(
                    batch_size=max(int(row_group_size), 1)
                ):
                    table = pa.Table.from_batches([batch]).replace_schema_metadata(None)
                    arrays = []
                    for field in schema:
                        if field.name in table.column_names:
                            arrays.append(table[field.name].cast(field.type, safe=True))
                        else:
                            arrays.append(pa.nulls(table.num_rows, type=field.type))
                    aligned = pa.Table.from_arrays(arrays, schema=schema)
                    writer.write_table(
                        aligned, row_group_size=max(int(row_group_size), 1)
                    )
        finally:
            writer.close()
    if target.exists():
        raise FileExistsError(target)
    os.rename(partial, target)
    return target, total_rows


@dataclass(frozen=True)
class TwoWeekAudit:
    status: str
    numeric_executed: bool
    config_semantics: str
    endpoint_decision_status: str
    accumulation_timestamp_position: str | None
    state_timestamp_position: str | None
    accumulation_days: int | None
    state_days: int | None
    release_count: int
    missing_release_slots: int
    cell_count: int
    canonical_field_count: int
    event_rows: int
    bridge_rows: int
    count_scan_batch_size: int
    event_count_scan_max_batch_rows: int
    bridge_count_scan_max_batch_rows: int
    primary_threshold: float
    primary_min_units: int
    strict_threshold: float
    strict_min_units: int
    reason: str

    def as_dict(self) -> dict[str, object]:
        support_status = (
            "confirmed"
            if self.endpoint_decision_status == "CONFIRMED"
            else "development_candidate"
        )
        return {
            "status": self.status,
            "numeric_executed": self.numeric_executed,
            "config_semantics": self.config_semantics,
            "endpoint_decision_status": self.endpoint_decision_status,
            "accumulation_timestamp_position": self.accumulation_timestamp_position,
            "state_timestamp_position": self.state_timestamp_position,
            "accumulation_days": self.accumulation_days,
            "state_days": self.state_days,
            "accumulation_support": (
                f"{support_status}: [label-13 days, label] inclusive"
            ),
            "event_state_support": (
                f"{support_status}: [label, label+6 days] inclusive"
            ),
            "release_count": self.release_count,
            "missing_release_slots": self.missing_release_slots,
            "cell_count": self.cell_count,
            "canonical_field_count": self.canonical_field_count,
            "event_rows": self.event_rows,
            "bridge_rows": self.bridge_rows,
            "count_scan_batch_size": self.count_scan_batch_size,
            "event_count_scan_max_batch_rows": self.event_count_scan_max_batch_rows,
            "bridge_count_scan_max_batch_rows": self.bridge_count_scan_max_batch_rows,
            "primary_threshold": self.primary_threshold,
            "primary_min_units": self.primary_min_units,
            "strict_threshold": self.strict_threshold,
            "strict_min_units": self.strict_min_units,
            "reason": self.reason,
        }


def prepare_two_week_records(
    timestamps: Sequence[date],
    values: Sequence[float],
    *,
    config_semantics: str,
    endpoint_decision_status: str,
    accumulation_timestamp_position: str | None,
    state_timestamp_position: str | None,
    accumulation_days: int | None,
    state_days: int | None,
    primary_threshold: float = -1.0,
    primary_min_units: int = 1,
    strict_threshold: float = -1.5,
    strict_min_units: int = 3,
    cell_count: int = 0,
    canonical_field_count: int = 0,
    event_rows: int = 0,
    bridge_rows: int = 0,
    count_scan_batch_size: int = 65_536,
    event_count_scan_max_batch_rows: int = 0,
    bridge_count_scan_max_batch_rows: int = 0,
) -> tuple[tuple[SpeiRecord, ...] | None, TwoWeekAudit]:
    """Execute 2W numerics only after all time semantics are explicitly resolved."""

    if endpoint_decision_status != "CONFIRMED":
        audit = TwoWeekAudit(
            SPEI_2W_PENDING_STATUS,
            False,
            str(config_semantics),
            str(endpoint_decision_status),
            accumulation_timestamp_position,
            state_timestamp_position,
            accumulation_days,
            state_days,
            0,
            0,
            int(cell_count),
            int(canonical_field_count),
            int(event_rows),
            int(bridge_rows),
            int(count_scan_batch_size),
            int(event_count_scan_max_batch_rows),
            int(bridge_count_scan_max_batch_rows),
            float(primary_threshold),
            int(primary_min_units),
            float(strict_threshold),
            int(strict_min_units),
            "Development candidate is disabled until the endpoint decision is confirmed",
        )
        return None, audit
    if str(config_semantics).strip().lower() == "unresolved":
        audit = TwoWeekAudit(
            "SKIPPED_UNRESOLVED_TIME_SEMANTICS",
            False,
            str(config_semantics),
            str(endpoint_decision_status),
            accumulation_timestamp_position,
            state_timestamp_position,
            accumulation_days,
            state_days,
            0,
            0,
            int(cell_count),
            int(canonical_field_count),
            int(event_rows),
            int(bridge_rows),
            int(count_scan_batch_size),
            int(event_count_scan_max_batch_rows),
            int(bridge_count_scan_max_batch_rows),
            float(primary_threshold),
            int(primary_min_units),
            float(strict_threshold),
            int(strict_min_units),
            "Config keeps CHM SPEI-2W timestamp semantics unresolved",
        )
        return None, audit
    if (
        accumulation_timestamp_position != "end"
        or state_timestamp_position != "start"
        or accumulation_days is None
        or accumulation_days <= 0
        or state_days is None
        or state_days <= 0
    ):
        audit = TwoWeekAudit(
            "SKIPPED_INCOMPLETE_TIME_PARAMETERS",
            False,
            str(config_semantics),
            str(endpoint_decision_status),
            accumulation_timestamp_position,
            state_timestamp_position,
            accumulation_days,
            state_days,
            0,
            0,
            int(cell_count),
            int(canonical_field_count),
            int(event_rows),
            int(bridge_rows),
            int(count_scan_batch_size),
            int(event_count_scan_max_batch_rows),
            int(bridge_count_scan_max_batch_rows),
            float(primary_threshold),
            int(primary_min_units),
            float(strict_threshold),
            int(strict_min_units),
            "Resolved config requires accumulation-end and forward-state parameters",
        )
        return None, audit
    records = spei_2w_records(
        timestamps,
        values,
        accumulation_days=int(accumulation_days),
        state_days=int(state_days),
        accumulation_timestamp_position=accumulation_timestamp_position,
        state_timestamp_position=state_timestamp_position,
    )
    gaps = [
        (current - previous).days
        for previous, current in zip(timestamps, timestamps[1:])
    ]
    missing_slots = sum(max(gap // int(state_days) - 1, 0) for gap in gaps)
    return records, TwoWeekAudit(
        "EXECUTED",
        True,
        str(config_semantics),
        str(endpoint_decision_status),
        accumulation_timestamp_position,
        state_timestamp_position,
        int(accumulation_days),
        int(state_days),
        len(records),
        missing_slots,
        int(cell_count),
        int(canonical_field_count),
        int(event_rows),
        int(bridge_rows),
        int(count_scan_batch_size),
        int(event_count_scan_max_batch_rows),
        int(bridge_count_scan_max_batch_rows),
        float(primary_threshold),
        int(primary_min_units),
        float(strict_threshold),
        int(strict_min_units),
        "Confirmed endpoint decision and explicit accumulation/state mapping executed",
    )


def write_two_week_audit(path: str | Path, audit: TwoWeekAudit) -> Path:
    target = Path(path)
    _write_json_new(target, audit.as_dict())
    return target
