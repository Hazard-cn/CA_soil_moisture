"""GLEAM v4.3a extraction, climatology, and event adapters.

Only selected target cells and the smallest source bounding box are read.  The
module never materializes a global ``time x lat x lon`` array.
"""

from __future__ import annotations

import math
import warnings
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterator, Sequence

import numpy as np
import pandas as pd

from .core import (
    bilinear_weights,
    build_runs,
    calendar_pentad,
    detect_flash_droughts,
)
from .era5 import column_searchsorted, type7_quantile_from_sorted
from .runtime import atomic_output


GLEAM_LAYERS = ("SMrz", "SMs")
NATIVE_TIME_CHUNK_DAYS = 12


@dataclass(frozen=True)
class GleamSpatialMap:
    """Four-neighbour mapping from native GLEAM axes to selected cells."""

    cell_ids: np.ndarray
    target_latitude: np.ndarray
    target_longitude: np.ndarray
    neighbor_lat_indices: np.ndarray
    neighbor_lon_indices: np.ndarray
    weights: np.ndarray
    lat_start: int
    lat_stop: int
    lon_start: int
    lon_stop: int
    source_latitude: np.ndarray
    source_longitude: np.ndarray

    @property
    def cell_count(self) -> int:
        return int(len(self.cell_ids))

    @property
    def local_lat_indices(self) -> np.ndarray:
        return self.neighbor_lat_indices - self.lat_start

    @property
    def local_lon_indices(self) -> np.ndarray:
        return self.neighbor_lon_indices - self.lon_start


@dataclass(frozen=True)
class GleamDailyBlock:
    dates: tuple[date, ...]
    values: np.ndarray
    source_bbox_shape: tuple[int, int, int]


@dataclass(frozen=True)
class DailyCacheSummary:
    path: str
    layer: str
    year: int
    rows: int
    days: int
    cells: int
    valid_values: int
    time_chunk_days: int


@dataclass(frozen=True)
class PentadBlock:
    years: np.ndarray
    pentads: np.ndarray
    values: np.ndarray
    valid_day_counts: np.ndarray


@dataclass(frozen=True)
class PentadClimatology:
    q10: np.ndarray
    q20: np.ndarray
    q40: np.ndarray
    history_count: np.ndarray


@dataclass(frozen=True)
class PentadTargetMetrics:
    percentile: np.ndarray
    below_p10: np.ndarray
    below_p20: np.ndarray
    history_count: np.ndarray
    q10: np.ndarray
    q20: np.ndarray
    q40: np.ndarray


@dataclass(frozen=True)
class DailyTargetMetrics:
    q10: np.ndarray
    percentile: np.ndarray
    below_p10: np.ndarray
    history_count: np.ndarray
    expected_history_count: np.ndarray


def _validate_layer(layer: str) -> None:
    if layer not in GLEAM_LAYERS:
        raise ValueError(f"layer must be one of {GLEAM_LAYERS}")


def _bracket_indices(axis: np.ndarray, values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return lower/upper coordinate indices for an ascending or descending axis."""

    if axis.ndim != 1 or len(axis) < 2:
        raise ValueError("source axis must be one-dimensional with at least two cells")
    delta = np.diff(axis)
    if np.all(delta > 0):
        ascending = axis
        index_map = np.arange(len(axis))
    elif np.all(delta < 0):
        ascending = axis[::-1]
        index_map = np.arange(len(axis) - 1, -1, -1)
    else:
        raise ValueError("source axis must be strictly monotonic")
    if np.any(values < ascending[0]) or np.any(values > ascending[-1]):
        raise ValueError("target coordinates fall outside the native GLEAM domain")
    upper_position = np.searchsorted(ascending, values, side="right")
    upper_position = np.clip(upper_position, 1, len(ascending) - 1)
    lower_position = upper_position - 1
    return index_map[lower_position], index_map[upper_position]


def build_spatial_map(
    source_latitude: Sequence[float],
    source_longitude: Sequence[float],
    target_latitude: Sequence[float],
    target_longitude: Sequence[float],
    *,
    cell_ids: Sequence[int] | None = None,
) -> GleamSpatialMap:
    """Build a no-extrapolation SW/SE/NW/NE bilinear mapping."""

    source_lat = np.asarray(source_latitude, dtype=float)
    source_lon = np.asarray(source_longitude, dtype=float)
    target_lat = np.asarray(target_latitude, dtype=float)
    target_lon = np.asarray(target_longitude, dtype=float)
    if target_lat.ndim != 1 or target_lon.ndim != 1 or len(target_lat) != len(target_lon):
        raise ValueError("target latitude/longitude must be equal-length 1-D arrays")
    if not len(target_lat) or not np.all(np.isfinite(target_lat)) or not np.all(
        np.isfinite(target_lon)
    ):
        raise ValueError("target coordinates must be finite and non-empty")

    first_lat, second_lat = _bracket_indices(source_lat, target_lat)
    south_lat = np.where(
        source_lat[first_lat] < source_lat[second_lat], first_lat, second_lat
    )
    north_lat = np.where(south_lat == first_lat, second_lat, first_lat)
    first_lon, second_lon = _bracket_indices(source_lon, target_lon)
    west_lon = np.where(
        source_lon[first_lon] < source_lon[second_lon], first_lon, second_lon
    )
    east_lon = np.where(west_lon == first_lon, second_lon, first_lon)

    x_fraction = (target_lon - source_lon[west_lon]) / (
        source_lon[east_lon] - source_lon[west_lon]
    )
    y_fraction = (target_lat - source_lat[south_lat]) / (
        source_lat[north_lat] - source_lat[south_lat]
    )
    weights = np.asarray(
        [bilinear_weights(float(x), float(y)) for x, y in zip(x_fraction, y_fraction)],
        dtype=float,
    )
    neighbor_lat = np.column_stack((south_lat, south_lat, north_lat, north_lat))
    neighbor_lon = np.column_stack((west_lon, east_lon, west_lon, east_lon))
    identifiers = (
        np.arange(1, len(target_lat) + 1, dtype=np.int64)
        if cell_ids is None
        else np.asarray(cell_ids, dtype=np.int64)
    )
    if len(identifiers) != len(target_lat) or len(np.unique(identifiers)) != len(
        identifiers
    ):
        raise ValueError("cell_ids must be unique and match target coordinates")
    return GleamSpatialMap(
        cell_ids=identifiers,
        target_latitude=target_lat,
        target_longitude=target_lon,
        neighbor_lat_indices=neighbor_lat,
        neighbor_lon_indices=neighbor_lon,
        weights=weights,
        lat_start=int(neighbor_lat.min()),
        lat_stop=int(neighbor_lat.max()) + 1,
        lon_start=int(neighbor_lon.min()),
        lon_stop=int(neighbor_lon.max()) + 1,
        source_latitude=source_lat.copy(),
        source_longitude=source_lon.copy(),
    )


def interpolate_spatial_block(
    source_block: np.ndarray,
    mapping: GleamSpatialMap,
    *,
    min_valid_neighbors: int = 2,
) -> np.ndarray:
    """Interpolate ``time x bbox_lat x bbox_lon`` to ``time x selected_cell``."""

    values = np.asarray(source_block, dtype=float)
    if values.ndim != 3:
        raise ValueError("source_block must have dimensions time x lat x lon")
    expected = (
        mapping.lat_stop - mapping.lat_start,
        mapping.lon_stop - mapping.lon_start,
    )
    if values.shape[1:] != expected:
        raise ValueError(f"source bbox shape is {values.shape[1:]}, expected {expected}")
    if not 1 <= min_valid_neighbors <= 4:
        raise ValueError("min_valid_neighbors must lie in 1..4")
    gathered = values[
        :, mapping.local_lat_indices, mapping.local_lon_indices
    ]  # time x cells x 4
    weights = mapping.weights[None, :, :]
    usable = np.isfinite(gathered) & (weights > 0)
    valid_count = usable.sum(axis=2)
    denominator = np.where(usable, weights, 0.0).sum(axis=2)
    numerator = np.where(usable, gathered * weights, 0.0).sum(axis=2)
    result = np.full(numerator.shape, np.nan, dtype=float)
    valid = (valid_count >= min_valid_neighbors) & (denominator > 0)
    result[valid] = numerator[valid] / denominator[valid]
    return result


def read_source_axes(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    import xarray as xr

    with xr.open_dataset(path, decode_times=False, cache=False) as dataset:
        return (
            np.asarray(dataset["lat"].values, dtype=float),
            np.asarray(dataset["lon"].values, dtype=float),
        )


def iter_selected_daily_blocks(
    source_path: str | Path,
    layer: str,
    mapping: GleamSpatialMap,
    *,
    min_valid_neighbors: int = 2,
) -> Iterator[GleamDailyBlock]:
    """Yield selected daily values using native 12-day source slices."""

    import xarray as xr

    _validate_layer(layer)
    with xr.open_dataset(source_path, decode_times=True, cache=False) as dataset:
        if layer not in dataset.data_vars:
            raise ValueError(f"{source_path} does not contain {layer}")
        source_lat = np.asarray(dataset["lat"].values, dtype=float)
        source_lon = np.asarray(dataset["lon"].values, dtype=float)
        if source_lat.shape != mapping.source_latitude.shape or not np.allclose(
            source_lat, mapping.source_latitude, rtol=0, atol=1e-10
        ):
            raise ValueError("source latitude axis differs from spatial mapping")
        if source_lon.shape != mapping.source_longitude.shape or not np.allclose(
            source_lon, mapping.source_longitude, rtol=0, atol=1e-10
        ):
            raise ValueError("source longitude axis differs from spatial mapping")
        count = int(dataset.sizes["time"])
        for start in range(0, count, NATIVE_TIME_CHUNK_DAYS):
            stop = min(start + NATIVE_TIME_CHUNK_DAYS, count)
            subset = dataset[layer].isel(
                time=slice(start, stop),
                lat=slice(mapping.lat_start, mapping.lat_stop),
                lon=slice(mapping.lon_start, mapping.lon_stop),
            )
            raw = np.asarray(subset.transpose("time", "lat", "lon").values)
            selected = interpolate_spatial_block(
                raw, mapping, min_valid_neighbors=min_valid_neighbors
            )
            dates = tuple(
                pd.Timestamp(value).date()
                for value in dataset["time"].isel(time=slice(start, stop)).values
            )
            yield GleamDailyBlock(dates, selected, tuple(int(v) for v in raw.shape))


def write_selected_daily_cache(
    source_path: str | Path,
    target_path: str | Path,
    run_dir: str | Path,
    layer: str,
    mapping: GleamSpatialMap,
    *,
    expected_year: int | None = None,
    min_valid_neighbors: int = 2,
    cell_chunk_size: int = 512,
) -> DailyCacheSummary:
    """Write a compressed selected-cell daily NetCDF without a global read."""

    from netCDF4 import Dataset

    _validate_layer(layer)
    if cell_chunk_size <= 0:
        raise ValueError("cell_chunk_size must be positive")
    days = 0
    valid_values = 0
    source_year: int | None = None
    expected_next_date: date | None = (
        date(int(expected_year), 1, 1) if expected_year is not None else None
    )
    with atomic_output(target_path, run_dir) as partial:
        with Dataset(partial, "w", format="NETCDF4") as output:
            output.createDimension("time", None)
            output.createDimension("cell", mapping.cell_count)
            time_var = output.createVariable("time", "i4", ("time",))
            time_var.units = "days since 1900-01-01"
            time_var.calendar = "proleptic_gregorian"
            cell_var = output.createVariable("era01_cell_id", "i8", ("cell",))
            lat_var = output.createVariable("latitude", "f8", ("cell",))
            lon_var = output.createVariable("longitude", "f8", ("cell",))
            sm_var = output.createVariable(
                layer,
                "f4",
                ("time", "cell"),
                zlib=True,
                complevel=4,
                shuffle=True,
                chunksizes=(
                    NATIVE_TIME_CHUNK_DAYS,
                    min(cell_chunk_size, mapping.cell_count),
                ),
                fill_value=np.float32(np.nan),
            )
            sm_var.units = "m3 m-3"
            sm_var.long_name = f"GLEAM v4.3a {layer}, bilinear selected cells"
            output.source = str(Path(source_path))
            output.interpolation = "bilinear_renormalized"
            output.minimum_valid_neighbors = min_valid_neighbors
            output.time_chunk_days = NATIVE_TIME_CHUNK_DAYS
            cell_var[:] = mapping.cell_ids
            lat_var[:] = mapping.target_latitude
            lon_var[:] = mapping.target_longitude
            for block in iter_selected_daily_blocks(
                source_path,
                layer,
                mapping,
                min_valid_neighbors=min_valid_neighbors,
            ):
                if block.dates:
                    years = {value.year for value in block.dates}
                    if len(years) != 1:
                        raise ValueError("one GLEAM source cache must contain one year")
                    year = next(iter(years))
                    if source_year is not None and source_year != year:
                        raise ValueError("one GLEAM source cache must contain one year")
                    source_year = year
                    if expected_year is not None and source_year != int(expected_year):
                        raise ValueError(
                            f"GLEAM source year is {source_year}, expected {int(expected_year)}"
                        )
                    if expected_next_date is None:
                        expected_next_date = date(source_year, 1, 1)
                    for observed_date in block.dates:
                        if observed_date != expected_next_date:
                            raise ValueError(
                                "GLEAM source daily axis is not the complete consecutive "
                                f"calendar year: expected {expected_next_date}, "
                                f"observed {observed_date}"
                            )
                        expected_next_date += timedelta(days=1)
                stop = days + len(block.dates)
                epoch = date(1900, 1, 1)
                time_var[days:stop] = [
                    (value - epoch).days for value in block.dates
                ]
                sm_var[days:stop, :] = block.values.astype(np.float32)
                valid_values += int(np.isfinite(block.values).sum())
                days = stop
    if source_year is None:
        raise ValueError("source file contains no daily observations")
    if (
        expected_year is not None
        and expected_next_date != date(source_year + 1, 1, 1)
    ):
        raise ValueError(
            f"GLEAM source year {source_year} ends before December 31"
        )
    return DailyCacheSummary(
        path=str(Path(target_path)),
        layer=layer,
        year=source_year,
        rows=days * mapping.cell_count,
        days=days,
        cells=mapping.cell_count,
        valid_values=valid_values,
        time_chunk_days=NATIVE_TIME_CHUNK_DAYS,
    )


def daily_values_to_pentads(
    dates: Sequence[date],
    values: np.ndarray,
) -> PentadBlock:
    """Aggregate daily selected-cell values to fixed 5/5 calendar pentads."""

    matrix = np.asarray(values, dtype=float)
    if matrix.ndim == 1:
        matrix = matrix[:, None]
    if matrix.ndim != 2 or matrix.shape[0] != len(dates):
        raise ValueError("values must be date x cell")
    if len(set(dates)) != len(dates) or any(
        current <= previous for previous, current in zip(dates, dates[1:])
    ):
        raise ValueError("dates must be unique and strictly increasing")
    years = sorted({value.year for value in dates})
    labels: list[tuple[int, int]] = []
    means: list[np.ndarray] = []
    counts: list[np.ndarray] = []
    date_array = np.asarray(dates, dtype=object)
    for year in years:
        for pentad in range(1, 74):
            indices = [
                index
                for index, value in enumerate(date_array)
                if value.year == year and calendar_pentad(value) == pentad
            ]
            if len(indices) != 5:
                raise ValueError(f"{year} pentad {pentad} does not have five dates")
            block = matrix[indices, :]
            valid_count = np.isfinite(block).sum(axis=0)
            mean = np.full(matrix.shape[1], np.nan, dtype=float)
            complete = valid_count == 5
            mean[complete] = np.mean(block[:, complete], axis=0)
            labels.append((year, pentad))
            means.append(mean)
            counts.append(valid_count)
    return PentadBlock(
        years=np.asarray([label[0] for label in labels], dtype=np.int16),
        pentads=np.asarray([label[1] for label in labels], dtype=np.int8),
        values=np.vstack(means),
        valid_day_counts=np.vstack(counts).astype(np.int8),
    )


def compute_pentad_climatology(
    historical_values: np.ndarray,
    *,
    min_historical_years: int = 27,
) -> PentadClimatology:
    """Compute Type-7 Q10/Q20/Q40 for year x pentad x cell history."""

    history = np.asarray(historical_values, dtype=float)
    if history.ndim != 3 or history.shape[1] != 73:
        raise ValueError("historical_values must be year x 73 pentads x cell")
    if not 1 <= min_historical_years <= history.shape[0]:
        raise ValueError("min_historical_years is outside available history")
    count = np.isfinite(history).sum(axis=0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        quantiles = np.nanquantile(
            history, [0.10, 0.20, 0.40], axis=0, method="linear"
        )
    insufficient = count < min_historical_years
    quantiles[:, insufficient] = np.nan
    return PentadClimatology(
        q10=quantiles[0],
        q20=quantiles[1],
        q40=quantiles[2],
        history_count=count.astype(np.int16),
    )


def apply_pentad_climatology(
    target_values: np.ndarray,
    historical_values: np.ndarray,
    *,
    min_historical_years: int = 27,
) -> PentadTargetMetrics:
    """Apply frozen history using midrank and strict P10/P20 states."""

    target = np.asarray(target_values, dtype=float)
    history = np.asarray(historical_values, dtype=float)
    if target.ndim != 2 or target.shape[0] != 73:
        raise ValueError("target_values must be 73 pentads x cell")
    if history.ndim != 3 or history.shape[1:] != target.shape:
        raise ValueError("historical_values must be year x target shape")
    climatology = compute_pentad_climatology(
        history, min_historical_years=min_historical_years
    )
    valid_history = np.isfinite(history)
    valid_target = np.isfinite(target)
    less = (valid_history & (history < target[None, :, :])).sum(axis=0)
    equal = (valid_history & (history == target[None, :, :])).sum(axis=0)
    count = climatology.history_count
    eligible = valid_target & (count >= min_historical_years)
    percentile = np.full(target.shape, np.nan, dtype=float)
    percentile[eligible] = (
        100.0 * (less[eligible] + 0.5 * equal[eligible]) / count[eligible]
    )
    below_p10 = np.full(target.shape, np.nan, dtype=float)
    below_p20 = np.full(target.shape, np.nan, dtype=float)
    below_p10[eligible] = (target[eligible] < climatology.q10[eligible]).astype(float)
    below_p20[eligible] = (target[eligible] < climatology.q20[eligible]).astype(float)
    return PentadTargetMetrics(
        percentile=percentile,
        below_p10=below_p10,
        below_p20=below_p20,
        history_count=count,
        q10=climatology.q10,
        q20=climatology.q20,
        q40=climatology.q40,
    )


def _calendar_window_month_days(value: date, half_width_days: int) -> set[tuple[int, int]]:
    if half_width_days < 0:
        raise ValueError("half_width_days must be non-negative")
    reference = date(2000, value.month, value.day)
    return {
        ((reference + timedelta(days=offset)).month, (reference + timedelta(days=offset)).day)
        for offset in range(-half_width_days, half_width_days + 1)
    }


def apply_daily_p10_climatology(
    target_dates: Sequence[date],
    target_values: np.ndarray,
    historical_dates: Sequence[date],
    historical_values: np.ndarray,
    *,
    half_width_days: int = 2,
    minimum_history_fraction: float = 0.90,
) -> DailyTargetMetrics:
    """Apply a +/- calendar-day Type-7 P10, including an explicit Feb 29 rule.

    February 29 uses the month/day window Feb 27--Mar 2.  Non-leap historical
    years therefore contribute four available calendar days and leap years five;
    coverage is evaluated against that actual expected sample count.
    """

    target = np.asarray(target_values, dtype=float)
    history = np.asarray(historical_values, dtype=float)
    if target.ndim == 1:
        target = target[:, None]
    if history.ndim == 1:
        history = history[:, None]
    if target.shape[0] != len(target_dates) or history.shape[0] != len(
        historical_dates
    ):
        raise ValueError("date and value lengths differ")
    if target.shape[1] != history.shape[1]:
        raise ValueError("target and history cell dimensions differ")
    if not 0 < minimum_history_fraction <= 1:
        raise ValueError("minimum_history_fraction must lie in (0, 1]")

    q10 = np.full(target.shape, np.nan, dtype=float)
    percentile = np.full(target.shape, np.nan, dtype=float)
    below = np.full(target.shape, np.nan, dtype=float)
    count = np.zeros(target.shape, dtype=np.int16)
    expected = np.zeros(len(target_dates), dtype=np.int16)
    history_month_day = [(value.month, value.day) for value in historical_dates]
    target_groups: dict[tuple[int, int], list[int]] = {}
    for row, target_date in enumerate(target_dates):
        target_groups.setdefault((target_date.month, target_date.day), []).append(row)

    # The frozen threshold depends on month/day, not target year.  Sort each
    # historical +/-2-day sample once and apply all target years together.
    # Column-wise binary search avoids a sample-by-target-by-cell comparison
    # cube during the full 22,180-cell run.
    for month_day, row_list in sorted(target_groups.items()):
        representative = date(2000, month_day[0], month_day[1])
        allowed = _calendar_window_month_days(representative, half_width_days)
        indices = np.asarray(
            [index for index, key in enumerate(history_month_day) if key in allowed],
            dtype=int,
        )
        rows = np.asarray(row_list, dtype=int)
        expected[rows] = len(indices)
        minimum = math.ceil(len(indices) * minimum_history_fraction - 1e-12)
        sample = np.asarray(history[indices, :], dtype=float)
        sample.sort(axis=0)
        row_count = np.isfinite(sample).sum(axis=0).astype(np.int32)
        count[rows, :] = row_count[None, :]
        row_q10 = type7_quantile_from_sorted(sample, row_count, 0.10)
        queries = target[rows, :]
        left = column_searchsorted(sample, queries, row_count, side="left")
        right = column_searchsorted(sample, queries, row_count, side="right")
        eligible = np.isfinite(queries) & (row_count[None, :] >= minimum)
        q10[rows, :] = np.where(eligible, row_q10[None, :], np.nan)
        ranks = 100.0 * (left + 0.5 * (right - left)) / np.maximum(
            row_count[None, :], 1
        )
        percentile[rows, :] = np.where(eligible, ranks, np.nan)
        below[rows, :] = np.where(eligible, queries < row_q10[None, :], np.nan)
    return DailyTargetMetrics(
        q10=q10,
        percentile=percentile,
        below_p10=below,
        history_count=count,
        expected_history_count=expected,
    )


def daily_p10_event_audit(
    *,
    cell_id: int,
    layer: str,
    dates: Sequence[date],
    values: Sequence[float | None],
    q10: Sequence[float | None],
) -> pd.DataFrame:
    """Return gap-0 and gap-2 P10 event rows using the core run detector."""

    _validate_layer(layer)
    if len(dates) != len(values) or len(dates) != len(q10):
        raise ValueError("dates, values, and q10 must have equal length")
    mask: list[bool | None] = []
    intensity: list[float | None] = []
    for raw_value, raw_threshold in zip(values, q10):
        value = float(raw_value) if raw_value is not None else np.nan
        threshold = float(raw_threshold) if raw_threshold is not None else np.nan
        if not np.isfinite(value) or not np.isfinite(threshold):
            mask.append(None)
            intensity.append(None)
        else:
            active = value < threshold
            mask.append(active)
            intensity.append(threshold - value if active else 0.0)
    rows: list[dict[str, Any]] = []
    for variant, gap in (("main_gap0", 0), ("sensitivity_gap2", 2)):
        events = build_runs(
            dates,
            mask,
            min_active=5,
            max_gap=gap,
            intensity=intensity,
            event_id_prefix=f"{layer.lower()}-p10-{variant}",
        )
        for event in events:
            rows.append(
                {
                    "era01_cell_id": int(cell_id),
                    "layer": layer,
                    "event_family": "daily_p10",
                    "variant": variant,
                    "event_id": event.event_id,
                    "start_date": event.start,
                    "end_date": event.end,
                    "duration_days": event.duration,
                    "span_days": event.span_duration,
                    "gap_days": event.gap_duration,
                    "severity": event.severity,
                    "mean_intensity": event.mean_intensity,
                    "peak_intensity": event.peak_intensity,
                }
            )
    return pd.DataFrame(rows)


def flash_drought_event_audit(
    *,
    cell_id: int,
    layer: str,
    years: Sequence[int],
    pentads: Sequence[int],
    percentiles: Sequence[float | None],
) -> pd.DataFrame:
    """Return primary/strict complete-span flash-drought event audit rows."""

    _validate_layer(layer)
    if not (len(years) == len(pentads) == len(percentiles)):
        raise ValueError("years, pentads, and percentiles must have equal length")
    rows: list[dict[str, Any]] = []
    for variant, minimum, recovery in (
        ("primary_span3_recovery1", 3, 1),
        ("strict_span4_recovery2", 4, 2),
    ):
        for event in detect_flash_droughts(
            percentiles,
            min_span_pentads=minimum,
            recovery_confirm=recovery,
        ):
            row = asdict(event)
            row.update(
                {
                    "era01_cell_id": int(cell_id),
                    "layer": layer,
                    "event_family": "flash_drought",
                    "variant": variant,
                    "start_year": int(years[event.start_index]),
                    "start_pentad": int(pentads[event.start_index]),
                    "crossing_year": int(years[event.crossing_index]),
                    "crossing_pentad": int(pentads[event.crossing_index]),
                    "end_year": int(years[event.end_index]),
                    "end_pentad": int(pentads[event.end_index]),
                }
            )
            if event.recovery_index is not None:
                row["recovery_year"] = int(years[event.recovery_index])
                row["recovery_pentad"] = int(pentads[event.recovery_index])
            else:
                row["recovery_year"] = None
                row["recovery_pentad"] = None
            rows.append(row)
    return pd.DataFrame(rows)
