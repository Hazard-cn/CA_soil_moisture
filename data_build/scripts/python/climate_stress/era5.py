"""ERA5 hourly extraction, UTC+8 daily aggregation, and historical thresholds.

The module only materializes selected V3 cells.  Native NetCDF spatial chunks are
read one tile at a time so that neither a global cube nor the full China hourly
rectangle is loaded into memory.
"""

from __future__ import annotations

import calendar
import gc
import json
import math
import os
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import netCDF4 as nc
import numpy as np
import pandas as pd


EPOCH = np.datetime64("1970-01-01", "D")
CANONICAL_MONTH_DAYS = tuple(
    datetime(2000, 1, 1) + timedelta(days=offset) for offset in range(366)
)
CANONICAL_LOOKUP = {(value.month, value.day): idx for idx, value in enumerate(CANONICAL_MONTH_DAYS)}


def canonical_day_index(value: datetime | np.datetime64 | str) -> int:
    """Return a leap-calendar month-day index in ``[0, 365]``."""

    if isinstance(value, np.datetime64):
        text = np.datetime_as_string(value.astype("datetime64[D]"), unit="D")
        value = datetime.fromisoformat(text)
    elif isinstance(value, str):
        value = datetime.fromisoformat(value[:10])
    return CANONICAL_LOOKUP[(value.month, value.day)]


def _atomic_json(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}")
    partial = path.with_name(f".{path.name}.{uuid.uuid4().hex}.partial")
    partial.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")
    os.rename(partial, path)


def _atomic_npy(path: Path, values: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}")
    partial = path.with_name(f".{path.name}.{uuid.uuid4().hex}.partial")
    with partial.open("wb") as handle:
        np.save(handle, values, allow_pickle=False)
    os.rename(partial, path)


def save_daily_cache(
    root: str | Path,
    year: int,
    dates: np.ndarray,
    arrays: Mapping[str, np.ndarray],
    metadata: Mapping[str, object],
) -> list[Path]:
    """Persist one selected-cell daily partition without overwriting files."""

    target = Path(root) / f"year={int(year)}"
    target.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    date_path = target / "date_days_since_1970.npy"
    _atomic_npy(date_path, dates.astype(np.int32, copy=False))
    outputs.append(date_path)
    for name, values in arrays.items():
        out = target / f"{name}.npy"
        _atomic_npy(out, np.asarray(values))
        outputs.append(out)
    meta_path = target / "metadata.json"
    _atomic_json(meta_path, dict(metadata))
    outputs.append(meta_path)
    return outputs


def load_daily_dates(root: str | Path, year: int) -> np.ndarray:
    values = np.load(Path(root) / f"year={int(year)}" / "date_days_since_1970.npy", mmap_mode="r")
    return EPOCH + values.astype("timedelta64[D]")


def load_daily_metric(root: str | Path, year: int, name: str, mmap: bool = True) -> np.ndarray:
    return np.load(
        Path(root) / f"year={int(year)}" / f"{name}.npy",
        mmap_mode="r" if mmap else None,
    )


def expected_era_hourly_axis(year: int) -> np.ndarray:
    """Return the complete UTC hourly axis required for one named ERA year."""

    value = int(year)
    return np.arange(
        np.datetime64(f"{value:04d}-01-01T00:00:00", "us"),
        np.datetime64(f"{value + 1:04d}-01-01T00:00:00", "us"),
        np.timedelta64(1, "h"),
    )


def _decoded_hourly_axis(dataset: nc.Dataset) -> np.ndarray:
    time_name = "valid_time" if "valid_time" in dataset.variables else "time"
    if time_name not in dataset.variables:
        raise ValueError("ERA5 file is missing valid_time/time")
    variable = dataset.variables[time_name]
    raw = np.ma.asarray(variable[:])
    if np.ma.getmaskarray(raw).any():
        raise ValueError("ERA5 hourly time coordinate contains masked values")
    numeric = np.asarray(raw, dtype=np.float64)
    if not np.isfinite(numeric).all():
        raise ValueError("ERA5 hourly time coordinate contains non-finite values")
    decoded = nc.num2date(
        numeric,
        units=variable.units,
        calendar=getattr(variable, "calendar", "standard"),
        only_use_cftime_datetimes=False,
        only_use_python_datetimes=True,
    )
    try:
        return np.asarray(
            [
                np.datetime64(
                    datetime(
                        int(value.year),
                        int(value.month),
                        int(value.day),
                        int(value.hour),
                        int(value.minute),
                        int(value.second),
                        int(value.microsecond),
                    ),
                    "us",
                )
                for value in decoded
            ],
            dtype="datetime64[us]",
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"ERA5 hourly time coordinate cannot be decoded: {exc}") from exc


def validate_era_hourly_time_axis(
    dataset: nc.Dataset,
    expected_year: int,
    *,
    source: str | Path | None = None,
) -> np.ndarray:
    """Fail unless a file contains exactly every UTC hour in its filename year."""

    expected = expected_era_hourly_axis(expected_year)
    actual = _decoded_hourly_axis(dataset)
    if np.array_equal(actual, expected):
        return actual

    label = str(source) if source is not None else "<open NetCDF dataset>"
    actual_start = str(actual[0]) if actual.size else None
    actual_end = str(actual[-1]) if actual.size else None
    mismatch_index: int | None = None
    common = min(actual.size, expected.size)
    if common:
        mismatches = np.flatnonzero(actual[:common] != expected[:common])
        if mismatches.size:
            mismatch_index = int(mismatches[0])
    if mismatch_index is None and actual.size != expected.size:
        mismatch_index = common
    raise ValueError(
        "ERA5 hourly time axis does not match filename year "
        f"{int(expected_year)} for {label}: expected {expected.size} hours "
        f"from {expected[0]} through {expected[-1]}, observed {actual.size} hours "
        f"from {actual_start} through {actual_end}, first_mismatch_index={mismatch_index}"
    )


def validate_era_hourly_file(path: str | Path, expected_year: int) -> np.ndarray:
    """Open one ERA file and validate its complete named-year hourly axis."""

    source = Path(path)
    with nc.Dataset(source) as dataset:
        return validate_era_hourly_time_axis(
            dataset,
            expected_year,
            source=source,
        )


def _time_indices(dataset: nc.Dataset, start: datetime, end: datetime) -> tuple[np.ndarray, np.ndarray]:
    time_name = "valid_time" if "valid_time" in dataset.variables else "time"
    variable = dataset.variables[time_name]
    units = variable.units
    calendar_name = getattr(variable, "calendar", "standard")
    raw = np.asarray(variable[:], dtype=np.float64)
    lower = float(nc.date2num(start, units=units, calendar=calendar_name))
    upper = float(nc.date2num(end, units=units, calendar=calendar_name))
    indices = np.flatnonzero((raw >= lower) & (raw < upper))
    if indices.size and not np.array_equal(indices, np.arange(indices[0], indices[-1] + 1)):
        raise ValueError("ERA5 time selection is not contiguous")
    return indices.astype(np.int64), raw[indices]


def _validate_selected_coordinates(dataset: nc.Dataset, cells: pd.DataFrame, tolerance: float) -> None:
    latitude = np.asarray(dataset.variables["latitude"][:], dtype=np.float64)
    longitude = np.asarray(dataset.variables["longitude"][:], dtype=np.float64)
    source_lat = cells["era_source_lat_idx"].to_numpy(dtype=np.int64)
    source_lon = cells["era_source_lon_idx"].to_numpy(dtype=np.int64)
    lat_error = np.max(np.abs(latitude[source_lat] - cells["latitude"].to_numpy(dtype=np.float64)))
    lon_error = np.max(np.abs(longitude[source_lon] - cells["longitude"].to_numpy(dtype=np.float64)))
    if lat_error > tolerance or lon_error > tolerance:
        raise ValueError(
            f"Selected ERA coordinates are not exact: lat_error={lat_error}, lon_error={lon_error}"
        )


def _prepare_cells(crosswalk: pd.DataFrame) -> pd.DataFrame:
    required = {"era01_cell_id", "lat_idx", "lon_idx", "latitude", "longitude"}
    missing = sorted(required.difference(crosswalk.columns))
    if missing:
        raise ValueError(f"Crosswalk is missing ERA columns: {missing}")
    cells = crosswalk.sort_values("era01_cell_id").reset_index(drop=True).copy()
    if cells["era01_cell_id"].duplicated().any():
        raise ValueError("era01_cell_id must be unique")
    cells["era_source_lat_idx"] = cells["lat_idx"].astype(np.int64) + 4
    cells["era_source_lon_idx"] = cells["lon_idx"].astype(np.int64) + 5
    return cells


def resolve_era_hourly_path(
    file_pattern: str,
    year: int,
    file_overrides: Mapping[int | str, str | Path] | None = None,
) -> Path:
    """Resolve one annual ERA file, preferring an explicit read-only repair."""

    overrides = file_overrides or {}
    raw = overrides.get(int(year), overrides.get(str(int(year))))
    if raw is None:
        raw = file_pattern.format(year=int(year))
    return Path(str(raw).format(year=int(year)))


def _source_segments(
    file_pattern: str,
    year: int,
    utc_offset_hours: int,
    file_overrides: Mapping[int | str, str | Path] | None = None,
) -> tuple[list[tuple[int, Path, datetime, datetime]], np.ndarray]:
    local_start = datetime(int(year), 1, 1)
    local_end = datetime(int(year) + 1, 1, 1)
    utc_start = local_start - timedelta(hours=int(utc_offset_hours))
    utc_end = local_end - timedelta(hours=int(utc_offset_hours))
    segments: list[tuple[int, Path, datetime, datetime]] = []
    for source_year in range(utc_start.year, utc_end.year + 1):
        source_start = datetime(source_year, 1, 1)
        source_end = datetime(source_year + 1, 1, 1)
        start = max(utc_start, source_start)
        end = min(utc_end, source_end)
        if start < end:
            segments.append(
                (
                    source_year,
                    resolve_era_hourly_path(
                        file_pattern, source_year, file_overrides
                    ),
                    start,
                    end,
                )
            )
    expected_hours = int((utc_end - utc_start).total_seconds() // 3600)
    expected = np.arange(
        np.datetime64(utc_start, "h"), np.datetime64(utc_end, "h"), np.timedelta64(1, "h")
    )
    if expected.size != expected_hours:
        raise AssertionError("Unexpected hourly range length")
    return segments, expected


def extract_daily_temperature(
    file_pattern: str,
    year: int,
    crosswalk: pd.DataFrame,
    *,
    file_overrides: Mapping[int | str, str | Path] | None = None,
    utc_offset_hours: int = 8,
    gdd_pairs: Sequence[tuple[float, float]] = ((8.0, 29.0), (8.0, 30.0), (10.0, 29.0), (10.0, 30.0)),
    edd_thresholds: Sequence[float] = (29.0, 30.0, 32.0, 34.0, 35.0),
    coordinate_tolerance: float = 1e-6,
) -> tuple[np.ndarray, dict[str, np.ndarray], dict[str, object]]:
    """Extract one local calendar year and aggregate exactly 24 hourly values/day."""

    cells = _prepare_cells(crosswalk)
    segments, expected_hours = _source_segments(
        file_pattern,
        int(year),
        int(utc_offset_hours),
        file_overrides,
    )
    datasets: list[nc.Dataset] = []
    selections: list[np.ndarray] = []
    numeric_times: list[np.ndarray] = []
    try:
        for _source_year, path, start, end in segments:
            if not path.is_file():
                raise FileNotFoundError(path)
            dataset = nc.Dataset(path)
            try:
                validate_era_hourly_time_axis(
                    dataset,
                    _source_year,
                    source=path,
                )
                indices, raw_times = _time_indices(dataset, start, end)
            except Exception:
                dataset.close()
                raise
            datasets.append(dataset)
            selections.append(indices)
            time_name = "valid_time" if "valid_time" in dataset.variables else "time"
            tvar = dataset.variables[time_name]
            decoded = nc.num2date(
                raw_times,
                units=tvar.units,
                calendar=getattr(tvar, "calendar", "standard"),
                only_use_cftime_datetimes=False,
                only_use_python_datetimes=True,
            )
            numeric_times.append(
                np.asarray(
                    [np.datetime64(v.replace(tzinfo=None), "h") for v in decoded], dtype="datetime64[h]"
                )
            )
        actual_hours = (
            np.concatenate(numeric_times)
            if numeric_times
            else np.empty(0, dtype="datetime64[h]")
        )
        if not np.array_equal(actual_hours, expected_hours):
            raise ValueError(
                f"ERA5 selected hourly support is incomplete for {year} "
                f"UTC{utc_offset_hours:+}: expected={expected_hours.size}, "
                f"actual={actual_hours.size}"
            )
        if expected_hours.size % 24:
            raise AssertionError("Requested local year is not a multiple of 24 hours")
        n_days = expected_hours.size // 24
        n_cells = len(cells)
        arrays: dict[str, np.ndarray] = {
            "era5u8_tmean_c": np.full((n_days, n_cells), np.nan, dtype=np.float32),
            "era5u8_tmax_c": np.full((n_days, n_cells), np.nan, dtype=np.float32),
            "era5u8_tmin_c": np.full((n_days, n_cells), np.nan, dtype=np.float32),
            "era5u8_hour_count": np.zeros((n_days, n_cells), dtype=np.uint8),
        }
        for base, upper in gdd_pairs:
            arrays[f"era5u8_gdd_b{int(base)}_u{int(upper)}"] = np.full(
                (n_days, n_cells), np.nan, dtype=np.float32
            )
        for threshold in edd_thresholds:
            arrays[f"era5u8_edd_t{int(threshold)}"] = np.full(
                (n_days, n_cells), np.nan, dtype=np.float32
            )

        reference_latitude = np.asarray(
            datasets[0].variables["latitude"][:], dtype=np.float64
        )
        reference_longitude = np.asarray(
            datasets[0].variables["longitude"][:], dtype=np.float64
        )
        for dataset in datasets:
            latitude = np.asarray(
                dataset.variables["latitude"][:], dtype=np.float64
            )
            longitude = np.asarray(
                dataset.variables["longitude"][:], dtype=np.float64
            )
            if not np.array_equal(latitude, reference_latitude) or not np.array_equal(
                longitude, reference_longitude
            ):
                raise ValueError(
                    "ERA5 spatial axes differ across adjacent/repair annual files"
                )
            _validate_selected_coordinates(dataset, cells, coordinate_tolerance)

        first_t2m = datasets[0].variables["t2m"]
        chunking = first_t2m.chunking()
        lat_chunk = int(chunking[1]) if isinstance(chunking, (list, tuple)) else 57
        lon_chunk = int(chunking[2]) if isinstance(chunking, (list, tuple)) else 70
        tile_members: dict[tuple[int, int], list[int]] = defaultdict(list)
        src_lat = cells["era_source_lat_idx"].to_numpy(dtype=np.int64)
        src_lon = cells["era_source_lon_idx"].to_numpy(dtype=np.int64)
        for cell_index, (lat_index, lon_index) in enumerate(zip(src_lat, src_lon, strict=True)):
            tile_members[(int(lat_index // lat_chunk), int(lon_index // lon_chunk))].append(cell_index)

        nlat = len(datasets[0].dimensions["latitude"])
        nlon = len(datasets[0].dimensions["longitude"])
        for (lat_tile, lon_tile), members_list in sorted(tile_members.items()):
            members = np.asarray(members_list, dtype=np.int64)
            row_start = lat_tile * lat_chunk
            row_end = min(row_start + lat_chunk, nlat)
            col_start = lon_tile * lon_chunk
            col_end = min(col_start + lon_chunk, nlon)
            rel_lat = src_lat[members] - row_start
            rel_lon = src_lon[members] - col_start
            hourly_flat = np.full(
                (expected_hours.size, members.size), np.nan, dtype=np.float32
            )
            for dataset, selection, selected_hours in zip(
                datasets, selections, numeric_times, strict=True
            ):
                if selection.size == 0:
                    continue
                raw = dataset.variables["t2m"][
                    int(selection[0]) : int(selection[-1]) + 1,
                    row_start:row_end,
                    col_start:col_end,
                ]
                values = np.ma.filled(raw, np.nan).astype(np.float32, copy=False)
                selected = values[:, rel_lat, rel_lon] - np.float32(273.15)
                positions = np.searchsorted(expected_hours, selected_hours)
                hourly_flat[positions, :] = selected
            hourly = hourly_flat.reshape(n_days, 24, members.size)
            counts = np.isfinite(hourly).sum(axis=1).astype(np.uint8)
            complete = counts == 24
            with np.errstate(invalid="ignore"):
                tmean = np.nanmean(hourly, axis=1)
                tmax = np.nanmax(hourly, axis=1)
                tmin = np.nanmin(hourly, axis=1)
            tmean[~complete] = np.nan
            tmax[~complete] = np.nan
            tmin[~complete] = np.nan
            arrays["era5u8_hour_count"][:, members] = counts
            arrays["era5u8_tmean_c"][:, members] = tmean.astype(np.float32)
            arrays["era5u8_tmax_c"][:, members] = tmax.astype(np.float32)
            arrays["era5u8_tmin_c"][:, members] = tmin.astype(np.float32)
            for base, upper in gdd_pairs:
                daily = np.minimum(np.maximum(tmean, base), upper) - base
                daily[~complete] = np.nan
                arrays[f"era5u8_gdd_b{int(base)}_u{int(upper)}"][:, members] = daily.astype(np.float32)
            for threshold in edd_thresholds:
                with np.errstate(invalid="ignore"):
                    daily = np.nansum(np.maximum(hourly - threshold, 0.0), axis=1) / 24.0
                daily[~complete] = np.nan
                arrays[f"era5u8_edd_t{int(threshold)}"][:, members] = daily.astype(np.float32)

        local_dates = (
            expected_hours.reshape(n_days, 24)[:, 0]
            + np.timedelta64(int(utc_offset_hours), "h")
        ).astype("datetime64[D]")
        expected_dates = np.arange(
            np.datetime64(f"{int(year):04d}-01-01", "D"),
            np.datetime64(f"{int(year) + 1:04d}-01-01", "D"),
            np.timedelta64(1, "D"),
        )
        if not np.array_equal(local_dates, expected_dates):
            raise ValueError("Local daily dates are not the requested calendar year")
        metadata: dict[str, object] = {
            "year": int(year),
            "timezone_offset_hours": int(utc_offset_hours),
            "source_variable": "t2m",
            "source_unit": "K",
            "output_unit": "degC",
            "n_days": int(n_days),
            "n_cells": int(n_cells),
            "source_files": [str(item[1]) for item in segments],
            "native_chunking": list(chunking) if isinstance(chunking, (list, tuple)) else chunking,
            "hours_required_per_day": 24,
            "expected_hour_count": int(expected_hours.size),
            "available_hour_count": int(actual_hours.size),
            "missing_hour_count": int(expected_hours.size - actual_hours.size),
        }
        return local_dates, arrays, metadata
    finally:
        for dataset in datasets:
            dataset.close()


def build_era_daily_cache(
    file_pattern: str,
    years: Iterable[int],
    crosswalk: pd.DataFrame,
    output_root: str | Path,
    *,
    file_overrides: Mapping[int | str, str | Path] | None = None,
    utc_offset_hours: int = 8,
    gdd_pairs: Sequence[tuple[float, float]] = ((8, 29), (8, 30), (10, 29), (10, 30)),
    edd_thresholds: Sequence[float] = (29, 30, 32, 34, 35),
    resume: bool = False,
) -> list[Path]:
    outputs: list[Path] = []
    for year in sorted({int(v) for v in years}):
        target = Path(output_root) / f"year={year}" / "metadata.json"
        if resume and target.is_file():
            outputs.extend(sorted(target.parent.glob("*")))
            continue
        dates, arrays, metadata = extract_daily_temperature(
            file_pattern,
            year,
            crosswalk,
            file_overrides=file_overrides,
            utc_offset_hours=utc_offset_hours,
            gdd_pairs=gdd_pairs,
            edd_thresholds=edd_thresholds,
        )
        encoded_dates = (dates - EPOCH).astype(np.int32)
        outputs.extend(save_daily_cache(output_root, year, encoded_dates, arrays, metadata))
    return outputs


def _circular_window_indices(canonical: np.ndarray, center: int, half_width: int) -> np.ndarray:
    distance = np.abs(canonical.astype(np.int16) - int(center))
    distance = np.minimum(distance, 366 - distance)
    return np.flatnonzero(distance <= int(half_width))


def type7_quantile_from_sorted(sorted_values: np.ndarray, valid_counts: np.ndarray, q: float) -> np.ndarray:
    """R/NumPy linear (Type 7) quantile for independently sorted columns."""

    if sorted_values.ndim != 2:
        raise ValueError("sorted_values must be observations x columns")
    counts = np.asarray(valid_counts, dtype=np.int64)
    result = np.full(sorted_values.shape[1], np.nan, dtype=np.float64)
    valid = counts > 0
    if not np.any(valid):
        return result
    h = (counts[valid] - 1) * float(q)
    lower = np.floor(h).astype(np.int64)
    upper = np.ceil(h).astype(np.int64)
    frac = h - lower
    columns = np.flatnonzero(valid)
    low_values = sorted_values[lower, columns]
    high_values = sorted_values[upper, columns]
    result[valid] = low_values + frac * (high_values - low_values)
    return result


def column_searchsorted(
    sorted_values: np.ndarray,
    queries: np.ndarray,
    valid_counts: np.ndarray,
    *,
    side: str,
) -> np.ndarray:
    """Vectorized ``searchsorted`` for one independently sorted sample per column."""

    if side not in {"left", "right"}:
        raise ValueError("side must be left or right")
    sample = np.asarray(sorted_values)
    query = np.asarray(queries)
    if sample.ndim != 2 or query.ndim != 2 or sample.shape[1] != query.shape[1]:
        raise ValueError("sample and queries must share their column dimension")
    n_queries, n_columns = query.shape
    low = np.zeros((n_queries, n_columns), dtype=np.int32)
    high = np.broadcast_to(np.asarray(valid_counts, dtype=np.int32), (n_queries, n_columns)).copy()
    columns = np.broadcast_to(np.arange(n_columns, dtype=np.int64), (n_queries, n_columns))
    while np.any(low < high):
        active = low < high
        middle = (low + high) // 2
        # Inactive queries can already have low==high==n_observations; clip
        # their unused probe index while active queries remain strictly below
        # the corresponding valid count.
        probe = sample[np.minimum(middle, sample.shape[0] - 1), columns]
        if side == "left":
            move_low = probe < query
        else:
            move_low = probe <= query
        low = np.where(active & move_low, middle + 1, low)
        high = np.where(active & ~move_low, middle, high)
    return low


def build_calendar_thresholds(
    daily_root: str | Path,
    baseline_years: Sequence[int],
    target_years: Sequence[int],
    output_root: str | Path,
    *,
    half_width: int = 7,
    quantile: float = 0.90,
    minimum_history_fraction: float = 0.90,
    cell_block_size: int = 256,
) -> list[Path]:
    """Build Tmax/Tmin P90 and target-day Tmax average-rank percentiles."""

    baseline_years = tuple(sorted(int(v) for v in baseline_years))
    target_years = tuple(sorted(int(v) for v in target_years))
    if not baseline_years or not target_years:
        raise ValueError("baseline_years and target_years must be non-empty")
    sample_metric = load_daily_metric(daily_root, baseline_years[0], "era5u8_tmax_c")
    n_cells = int(sample_metric.shape[1])
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    threshold_paths = {
        "tmax": output_root / "era5u8_tmax_p90_calendar.npy",
        "tmin": output_root / "era5u8_tmin_p90_calendar.npy",
    }
    for path in threshold_paths.values():
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite {path}")
    partial_thresholds = {
        key: path.with_name(f".{path.name}.{uuid.uuid4().hex}.partial")
        for key, path in threshold_paths.items()
    }
    thresholds = {
        key: np.lib.format.open_memmap(path, mode="w+", dtype=np.float64, shape=(366, n_cells))
        for key, path in partial_thresholds.items()
    }
    for values in thresholds.values():
        values[:] = np.nan

    percentile_targets: dict[int, tuple[Path, Path, np.memmap]] = {}
    for year in target_years:
        final = output_root / f"year={year}" / "era5u8_tmax_historical_percentile.npy"
        final.parent.mkdir(parents=True, exist_ok=True)
        if final.exists():
            raise FileExistsError(f"Refusing to overwrite {final}")
        partial = final.with_name(f".{final.name}.{uuid.uuid4().hex}.partial")
        shape = load_daily_metric(daily_root, year, "era5u8_tmax_c").shape
        values = np.lib.format.open_memmap(partial, mode="w+", dtype=np.float32, shape=shape)
        values[:] = np.nan
        percentile_targets[year] = (final, partial, values)

    baseline_dates: list[np.ndarray] = []
    baseline_canonical: list[np.ndarray] = []
    for year in baseline_years:
        dates = load_daily_dates(daily_root, year)
        baseline_dates.append(dates)
        baseline_canonical.append(np.asarray([canonical_day_index(v) for v in dates], dtype=np.int16))
    flat_canonical = np.concatenate(baseline_canonical)
    expected_by_center = np.asarray(
        [_circular_window_indices(flat_canonical, center, half_width).size for center in range(366)],
        dtype=np.int32,
    )
    target_rows: dict[int, dict[int, np.ndarray]] = {}
    for year in target_years:
        dates = load_daily_dates(daily_root, year)
        canonical = np.asarray([canonical_day_index(v) for v in dates], dtype=np.int16)
        target_rows[year] = {center: np.flatnonzero(canonical == center) for center in range(366)}

    try:
        metric_map = {
            "tmax": "era5u8_tmax_c",
            "tmin": "era5u8_tmin_c",
        }
        for block_start in range(0, n_cells, int(cell_block_size)):
            block_end = min(block_start + int(cell_block_size), n_cells)
            for threshold_key, metric_name in metric_map.items():
                baseline = np.concatenate(
                    [
                        np.asarray(load_daily_metric(daily_root, year, metric_name)[:, block_start:block_end])
                        for year in baseline_years
                    ],
                    axis=0,
                ).astype(np.float64, copy=False)
                for center in range(366):
                    history_rows = _circular_window_indices(flat_canonical, center, half_width)
                    history = baseline[history_rows]
                    history.sort(axis=0)
                    counts = np.isfinite(history).sum(axis=0).astype(np.int32)
                    required = int(math.ceil(expected_by_center[center] * float(minimum_history_fraction)))
                    values = type7_quantile_from_sorted(history, counts, quantile)
                    values[counts < required] = np.nan
                    thresholds[threshold_key][center, block_start:block_end] = values
                    if threshold_key != "tmax":
                        continue
                    for year in target_years:
                        rows = target_rows[year][center]
                        if rows.size == 0:
                            continue
                        queries = np.asarray(
                            load_daily_metric(daily_root, year, metric_name)[rows, block_start:block_end],
                            dtype=np.float64,
                        )
                        left = column_searchsorted(history, queries, counts, side="left")
                        right = column_searchsorted(history, queries, counts, side="right")
                        ranks = 100.0 * (left + 0.5 * (right - left)) / np.maximum(counts, 1)
                        invalid = (~np.isfinite(queries)) | (counts < required)
                        ranks[invalid] = np.nan
                        percentile_targets[year][2][rows, block_start:block_end] = ranks.astype(np.float32)
        for values in thresholds.values():
            values.flush()
        for _year, (_final, _partial, values) in percentile_targets.items():
            values.flush()
    except Exception:
        raise
    finally:
        thresholds.clear()
        for year, (final, partial, mapped_values) in list(percentile_targets.items()):
            del mapped_values
            percentile_targets[year] = (final, partial, None)  # type: ignore[assignment]
        try:
            del values
        except UnboundLocalError:
            pass
        try:
            del mapped_values
        except UnboundLocalError:
            pass
        # Windows keeps mapped files open until the final ndarray references
        # are collected; release them before the atomic rename below.
        gc.collect()

    outputs: list[Path] = []
    for key, final in threshold_paths.items():
        os.rename(partial_thresholds[key], final)
        outputs.append(final)
    for year, (final, partial, _values) in percentile_targets.items():
        os.rename(partial, final)
        outputs.append(final)
    metadata = {
        "history_period": [int(min(baseline_years)), int(max(baseline_years))],
        "history_years": list(baseline_years),
        "target_years": list(target_years),
        "calendar": "366-bin month-day calendar; leap day retained",
        "calendar_window_half_width_days": int(half_width),
        "quantile": float(quantile),
        "quantile_method": "Type 7 / linear",
        "percentile_rank": "midrank against historical samples",
        "minimum_history_fraction": float(minimum_history_fraction),
        "strict_state_rule": "Tmax > P90 and Tmin > P90",
    }
    meta_path = output_root / "metadata.json"
    _atomic_json(meta_path, metadata)
    outputs.append(meta_path)
    return outputs


def attach_daily_temperature_thresholds(
    daily_root: str | Path,
    threshold_root: str | Path,
    year: int,
    *,
    cell_slice: slice | None = None,
) -> dict[str, np.ndarray]:
    """Load one target year and map calendar P90 thresholds to its dates.

    ``cell_slice`` is applied while the persisted arrays are still memory
    mapped.  Event construction uses this contract to keep its resident arrays
    bounded by the configured spatial block instead of materializing every
    selected cell for the full event-history period.
    """

    dates = load_daily_dates(daily_root, year)
    indices = np.asarray([canonical_day_index(value) for value in dates], dtype=np.int16)
    selector = slice(None) if cell_slice is None else cell_slice
    tmax_p90 = np.load(Path(threshold_root) / "era5u8_tmax_p90_calendar.npy", mmap_mode="r")
    tmin_p90 = np.load(Path(threshold_root) / "era5u8_tmin_p90_calendar.npy", mmap_mode="r")
    tmax = np.asarray(
        load_daily_metric(daily_root, year, "era5u8_tmax_c")[:, selector],
        dtype=np.float32,
    )
    tmin = np.asarray(
        load_daily_metric(daily_root, year, "era5u8_tmin_c")[:, selector],
        dtype=np.float32,
    )
    daily_tmax_p90 = np.asarray(tmax_p90[:, selector][indices], dtype=np.float32)
    daily_tmin_p90 = np.asarray(tmin_p90[:, selector][indices], dtype=np.float32)
    valid_hot = np.isfinite(tmax) & np.isfinite(daily_tmax_p90)
    valid_night = np.isfinite(tmin) & np.isfinite(daily_tmin_p90)
    hot = np.full(tmax.shape, -1, dtype=np.int8)
    hot_night = np.full(tmax.shape, -1, dtype=np.int8)
    compound = np.full(tmax.shape, -1, dtype=np.int8)
    hot[valid_hot] = (tmax[valid_hot] > daily_tmax_p90[valid_hot]).astype(np.int8)
    hot_night[valid_night] = (tmin[valid_night] > daily_tmin_p90[valid_night]).astype(np.int8)
    both_valid = valid_hot & valid_night
    compound[both_valid] = ((hot[both_valid] == 1) & (hot_night[both_valid] == 1)).astype(np.int8)
    return {
        "date": dates,
        "era5u8_tmax_c": tmax,
        "era5u8_tmin_c": tmin,
        "era5u8_tmax_p90_c": daily_tmax_p90,
        "era5u8_tmin_p90_c": daily_tmin_p90,
        "era5u8_tmax_historical_percentile": np.asarray(
            np.load(
                Path(threshold_root) / f"year={int(year)}" / "era5u8_tmax_historical_percentile.npy",
                mmap_mode="r",
            )[:, selector]
        ),
        "era5u8_tx90_state": hot,
        "era5u8_tn90_state": hot_night,
        "era5u8_hot_day_night_state": compound,
    }


def utc_daily_validation(
    file_pattern: str,
    validation_pattern: str,
    year: int,
    crosswalk: pd.DataFrame,
    *,
    file_overrides: Mapping[int | str, str | Path] | None = None,
) -> pd.DataFrame:
    """Reproduce UTC-day aggregates and compare them with legacy daily files."""

    dates, computed, _metadata = extract_daily_temperature(
        file_pattern,
        year,
        crosswalk,
        file_overrides=file_overrides,
        utc_offset_hours=0,
    )
    path = Path(validation_pattern.format(year=int(year)))
    with nc.Dataset(path) as dataset:
        latitude = np.asarray(dataset.variables["latitude"][:], dtype=np.float64)
        longitude = np.asarray(dataset.variables["longitude"][:], dtype=np.float64)
        cells = _prepare_cells(crosswalk)
        lat_index = cells["lat_idx"].to_numpy(dtype=np.int64)
        lon_index = cells["lon_idx"].to_numpy(dtype=np.int64)
        rows: list[dict[str, object]] = []
        mapping = {
            "era5u8_tmean_c": "t2m_mean",
            "era5u8_tmax_c": "t2m_max",
            "era5u8_tmin_c": "t2m_min",
        }
        for computed_name, candidates in mapping.items():
            source_name = candidates if candidates in dataset.variables else computed_name.replace("era5u8_", "")
            if source_name not in dataset.variables:
                continue
            reference = np.ma.filled(dataset.variables[source_name][:], np.nan).astype(np.float64)
            reference = reference[:, lat_index, lon_index]
            delta = np.asarray(computed[computed_name], dtype=np.float64) - reference
            finite = np.isfinite(delta)
            rows.append(
                {
                    "year": int(year),
                    "variable": computed_name,
                    "reference_variable": source_name,
                    "n_compared": int(finite.sum()),
                    "mean_difference": float(np.nanmean(delta)),
                    "rmse": float(np.sqrt(np.nanmean(delta**2))),
                    "max_absolute_difference": float(np.nanmax(np.abs(delta))),
                    "date_start": str(dates[0]),
                    "date_end": str(dates[-1]),
                    "reference_lat_error": float(
                        np.max(np.abs(latitude[lat_index] - cells["latitude"].to_numpy(dtype=np.float64)))
                    ),
                    "reference_lon_error": float(
                        np.max(np.abs(longitude[lon_index] - cells["longitude"].to_numpy(dtype=np.float64)))
                    ),
                }
            )
    return pd.DataFrame(rows)
