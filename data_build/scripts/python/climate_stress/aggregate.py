"""Window aggregation and event-audit construction for climate stress data."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from .core import RunEvent, detect_heatwaves, event_window_bridge_for_run, required_valid_count
from .era5 import attach_daily_temperature_thresholds, load_daily_dates, load_daily_metric


KEY_COLUMNS = [
    "era01_cell_id",
    "grid_id_v3",
    "lat_idx",
    "lon_idx",
    "latitude",
    "longitude",
    "lat10",
    "lon10",
    "year",
    "window",
    "window_start_doy",
    "window_end_doy",
    "window_days",
]

ERA_HEATWAVE_SEVERITY_MEASURE = "tmax_excess_above_calendar_p90"
ERA_HEATWAVE_SEVERITY_UNIT = "degree-Celsius-day"


def _python_dates(values: np.ndarray) -> list[date]:
    return [date.fromisoformat(np.datetime_as_string(value, unit="D")) for value in values]


def _window_template(
    panel: pd.DataFrame,
    windows: Sequence[str],
    years: Sequence[int],
) -> tuple[pd.DataFrame, dict[tuple[int, str], tuple[np.ndarray, np.ndarray, np.ndarray]]]:
    rows: list[pd.DataFrame] = []
    bounds: dict[tuple[int, str], tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    for year in years:
        current = panel.loc[panel["year"].eq(int(year))].sort_values("era01_cell_id").reset_index(drop=True)
        for window in windows:
            start = pd.to_numeric(current[f"win_{window}_start"], errors="coerce").to_numpy(dtype=float)
            end = pd.to_numeric(current[f"win_{window}_end"], errors="coerce").to_numpy(dtype=float)
            days = pd.to_numeric(current[f"win_{window}_days"], errors="coerce").to_numpy(dtype=float)
            bounds[(int(year), window)] = (start, end, days)
            frame = current[
                [
                    "era01_cell_id",
                    "grid_id_v3",
                    "lat_idx",
                    "lon_idx",
                    "latitude",
                    "longitude",
                    "lat10",
                    "lon10",
                    "year",
                ]
            ].copy()
            frame["window"] = window
            frame["window_start_doy"] = start
            frame["window_end_doy"] = end
            frame["window_days"] = days
            rows.append(frame)
    result = pd.concat(rows, ignore_index=True)
    return result, bounds


def _prefix_sum_and_count(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    finite = np.isfinite(values)
    cumulative = np.vstack(
        [
            np.zeros((1, values.shape[1]), dtype=np.float64),
            np.cumsum(np.where(finite, values, 0.0), axis=0, dtype=np.float64),
        ]
    )
    counts = np.vstack(
        [
            np.zeros((1, values.shape[1]), dtype=np.int32),
            np.cumsum(finite.astype(np.int32), axis=0, dtype=np.int32),
        ]
    )
    return cumulative, counts


def _window_sum_count(
    cumulative: np.ndarray,
    counts: np.ndarray,
    starts: np.ndarray,
    ends: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    n_cells = starts.size
    result = np.full(n_cells, np.nan, dtype=np.float64)
    valid_count = np.zeros(n_cells, dtype=np.int32)
    valid = np.isfinite(starts) & np.isfinite(ends) & (starts <= ends)
    cells = np.flatnonzero(valid)
    if cells.size:
        lower = starts[cells].astype(np.int64) - 1
        upper = ends[cells].astype(np.int64)
        result[cells] = cumulative[upper, cells] - cumulative[lower, cells]
        valid_count[cells] = counts[upper, cells] - counts[lower, cells]
    return result, valid_count


def _metric_window_validity(
    valid_days: np.ndarray,
    window_days: np.ndarray,
    required_days: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return coverage and the fail-closed mask for one metric's inputs."""

    coverage = np.divide(
        valid_days,
        window_days,
        out=np.full(valid_days.shape, np.nan, dtype=np.float64),
        where=np.isfinite(window_days) & (window_days > 0),
    )
    valid = np.isfinite(window_days) & (valid_days >= required_days)
    return coverage, valid


def _window_extreme(
    values: np.ndarray,
    starts: np.ndarray,
    ends: np.ndarray,
    *,
    mode: str,
) -> np.ndarray:
    if mode not in {"min", "max"}:
        raise ValueError("mode must be min or max")
    result = np.full(starts.size, np.nan, dtype=np.float64)
    valid = np.isfinite(starts) & np.isfinite(ends) & (starts <= ends)
    if not np.any(valid):
        return result
    pairs = np.unique(np.column_stack([starts[valid], ends[valid]]), axis=0)
    for raw_start, raw_end in pairs:
        start, end = int(raw_start) - 1, int(raw_end)
        members = np.flatnonzero(valid & (starts == raw_start) & (ends == raw_end))
        selected = values[start:end, :][:, members]
        finite = np.isfinite(selected).any(axis=0)
        if mode == "min":
            reduced = np.min(np.where(np.isfinite(selected), selected, np.inf), axis=0)
        else:
            reduced = np.max(np.where(np.isfinite(selected), selected, -np.inf), axis=0)
        result[members[finite]] = reduced[finite]
    return result


def _window_slice_offset(
    year: int,
    window_index: int,
    n_cells: int,
    windows: Sequence[str],
    years: Sequence[int],
) -> range:
    year_index = tuple(years).index(int(year))
    start = (year_index * len(windows) + int(window_index)) * n_cells
    return range(start, start + n_cells)


def _event_overlap_peak(event: RunEvent, window_start: date, window_end: date) -> float:
    values = [
        segment.severity / segment.days
        for segment in event.segments
        if segment.active
        and segment.start <= window_end
        and segment.end_exclusive > window_start
    ]
    return max(values) if values else 0.0


def aggregate_temperature_windows(
    panel: pd.DataFrame,
    daily_root: str | Path,
    threshold_root: str | Path,
    *,
    years: Sequence[int],
    event_years: Sequence[int] | None = None,
    windows: Sequence[str],
    minimum_coverage: float = 0.90,
    heatwave_min_days: int = 3,
    cell_block_size: int = 128,
    source_cell_slice: slice | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Aggregate ERA temperature families and build full-event audit layers.

    ``source_cell_slice`` selects the matching columns from the persisted ERA
    caches and threshold arrays.  It lets the stage aggregate one canonical
    spatial block without materialising the full selected-grid history.  The
    panel passed to this function must describe exactly that same ordered
    block.
    """

    years = tuple(sorted(int(value) for value in years))
    event_years = tuple(
        sorted(int(value) for value in (years if event_years is None else event_years))
    )
    if not set(years).issubset(event_years):
        raise ValueError("Temperature output years must be contained in event years")
    windows = tuple(windows)
    long, bounds = _window_template(panel, windows, years)
    n_cells = int(panel["era01_cell_id"].nunique())
    expected_rows = n_cells * len(years) * len(windows)
    if len(long) != expected_rows:
        raise ValueError(f"Temperature template has {len(long):,} rows, expected {expected_rows:,}")
    sorted_cells = (
        panel[
            [
                "era01_cell_id",
                "grid_id_v3",
                "lat_idx",
                "lon_idx",
                "latitude",
                "longitude",
                "lat10",
                "lon10",
            ]
        ]
        .drop_duplicates("era01_cell_id")
        .sort_values("era01_cell_id")
        .reset_index(drop=True)
    )
    source_selector = slice(None) if source_cell_slice is None else source_cell_slice

    output_names = [
        "era5u8_valid_days",
        "era5u8_coverage",
        "era5u8_tmax_valid_days",
        "era5u8_tmax_coverage",
        "era5u8_tmin_valid_days",
        "era5u8_tmin_coverage",
        "era5u8_tmax_p90_valid_days",
        "era5u8_tmax_p90_coverage",
        "era5u8_tmin_p90_valid_days",
        "era5u8_tmin_p90_coverage",
        "era5u8_tx90p_valid_days",
        "era5u8_tx90p_coverage",
        "era5u8_hot_day_night_valid_days",
        "era5u8_hot_day_night_coverage",
        "era5u8_tmean_mean_c",
        "era5u8_tmax_mean_c",
        "era5u8_tmax_max_c",
        "era5u8_tmin_mean_c",
        "era5u8_tmin_min_c",
        "era5u8_tmax_p90_mean_c",
        "era5u8_tmin_p90_mean_c",
        "era5u8_tx90p_days",
        "era5u8_tx90p_share",
        "era5u8_hot_day_night_days",
    ]
    gdd_names = [
        "era5u8_gdd_b8_u29",
        "era5u8_gdd_b8_u30",
        "era5u8_gdd_b10_u29",
        "era5u8_gdd_b10_u30",
    ]
    edd_names = [f"era5u8_edd_t{threshold}" for threshold in (29, 30, 32, 34, 35)]
    for name in output_names:
        long[name] = np.nan
    for name in gdd_names:
        long[f"{name}_sum_cdays"] = np.nan
        long[f"{name}_mean_cday"] = np.nan
    for name in edd_names:
        long[f"{name}_sum_cdays"] = np.nan

    threshold_calendar = {
        "tmax": np.load(Path(threshold_root) / "era5u8_tmax_p90_calendar.npy", mmap_mode="r"),
        "tmin": np.load(Path(threshold_root) / "era5u8_tmin_p90_calendar.npy", mmap_mode="r"),
    }
    from .era5 import canonical_day_index

    daily_by_year: dict[int, dict[str, np.ndarray]] = {}
    valid_event_windows = np.zeros(len(long), dtype=bool)
    for year in years:
        dates = load_daily_dates(daily_root, year)
        canonical = np.asarray([canonical_day_index(value) for value in dates], dtype=np.int16)
        current: dict[str, np.ndarray] = {
            "date": dates,
            "tmean": np.asarray(
                load_daily_metric(daily_root, year, "era5u8_tmean_c")[:, source_selector]
            ),
            "tmax": np.asarray(
                load_daily_metric(daily_root, year, "era5u8_tmax_c")[:, source_selector]
            ),
            "tmin": np.asarray(
                load_daily_metric(daily_root, year, "era5u8_tmin_c")[:, source_selector]
            ),
            "tmax_p90": np.asarray(
                threshold_calendar["tmax"][canonical, source_selector], dtype=np.float32
            ),
            "tmin_p90": np.asarray(
                threshold_calendar["tmin"][canonical, source_selector], dtype=np.float32
            ),
        }
        for name in (*gdd_names, *edd_names):
            current[name] = np.asarray(
                load_daily_metric(daily_root, year, name)[:, source_selector]
            )
        for name, values in current.items():
            if name == "date":
                continue
            if values.shape != (len(dates), n_cells):
                raise ValueError(
                    f"ERA {year} {name} block shape {values.shape} differs from "
                    f"({len(dates)}, {n_cells})"
                )
        valid_hot = np.isfinite(current["tmax"]) & np.isfinite(current["tmax_p90"])
        valid_night = np.isfinite(current["tmin"]) & np.isfinite(current["tmin_p90"])
        current["hot"] = np.where(
            valid_hot, current["tmax"] > current["tmax_p90"], np.nan
        ).astype(np.float32)
        current["hot_day_night"] = np.where(
            valid_hot & valid_night,
            (current["tmax"] > current["tmax_p90"])
            & (current["tmin"] > current["tmin_p90"]),
            np.nan,
        ).astype(np.float32)
        daily_by_year[year] = current

        metric_cache = {
            key: _prefix_sum_and_count(current[key])
            for key in (
                "tmean",
                "tmax",
                "tmin",
                "tmax_p90",
                "tmin_p90",
                "hot",
                "hot_day_night",
                *gdd_names,
                *edd_names,
            )
        }
        for window_index, window in enumerate(windows):
            destination = _window_slice_offset(year, window_index, n_cells, windows, years)
            starts, ends, window_days = bounds[(year, window)]
            tmean_sum, valid_days = _window_sum_count(*metric_cache["tmean"], starts, ends)
            required = np.asarray(
                [
                    required_valid_count(int(value), minimum_coverage)
                    if np.isfinite(value)
                    else 1
                    for value in window_days
                ],
                dtype=np.int32,
            )
            coverage, valid_window = _metric_window_validity(
                valid_days, window_days, required
            )
            long.loc[destination, "era5u8_valid_days"] = valid_days
            long.loc[destination, "era5u8_coverage"] = coverage
            mean = np.divide(
                tmean_sum,
                valid_days,
                out=np.full(n_cells, np.nan),
                where=valid_days > 0,
            )
            mean[~valid_window] = np.nan
            long.loc[destination, "era5u8_tmean_mean_c"] = mean
            metric_validity: dict[str, np.ndarray] = {}
            for key, output_name, coverage_prefix in (
                ("tmax", "era5u8_tmax_mean_c", "era5u8_tmax"),
                ("tmin", "era5u8_tmin_mean_c", "era5u8_tmin"),
                ("tmax_p90", "era5u8_tmax_p90_mean_c", "era5u8_tmax_p90"),
                ("tmin_p90", "era5u8_tmin_p90_mean_c", "era5u8_tmin_p90"),
            ):
                total, count = _window_sum_count(*metric_cache[key], starts, ends)
                metric_coverage, metric_valid = _metric_window_validity(
                    count, window_days, required
                )
                metric_validity[key] = metric_valid
                value = np.divide(total, count, out=np.full(n_cells, np.nan), where=count > 0)
                value[~metric_valid] = np.nan
                long.loc[destination, output_name] = value
                long.loc[destination, f"{coverage_prefix}_valid_days"] = count
                long.loc[destination, f"{coverage_prefix}_coverage"] = metric_coverage
            tmax_extreme = _window_extreme(current["tmax"], starts, ends, mode="max")
            tmin_extreme = _window_extreme(current["tmin"], starts, ends, mode="min")
            tmax_extreme[~metric_validity["tmax"]] = np.nan
            tmin_extreme[~metric_validity["tmin"]] = np.nan
            long.loc[destination, "era5u8_tmax_max_c"] = tmax_extreme
            long.loc[destination, "era5u8_tmin_min_c"] = tmin_extreme
            for key, output_name, coverage_prefix in (
                ("hot", "era5u8_tx90p_days", "era5u8_tx90p"),
                (
                    "hot_day_night",
                    "era5u8_hot_day_night_days",
                    "era5u8_hot_day_night",
                ),
            ):
                total, count = _window_sum_count(*metric_cache[key], starts, ends)
                metric_coverage, metric_valid = _metric_window_validity(
                    count, window_days, required
                )
                total[~metric_valid] = np.nan
                long.loc[destination, output_name] = total
                long.loc[destination, f"{coverage_prefix}_valid_days"] = count
                long.loc[destination, f"{coverage_prefix}_coverage"] = metric_coverage
                if key == "hot":
                    share = np.divide(total, count, out=np.full(n_cells, np.nan), where=count > 0)
                    share[~metric_valid] = np.nan
                    long.loc[destination, "era5u8_tx90p_share"] = share
                    valid_event_windows[destination] = metric_valid
            for key in gdd_names:
                total, count = _window_sum_count(*metric_cache[key], starts, ends)
                _metric_coverage, metric_valid = _metric_window_validity(
                    count, window_days, required
                )
                total[~metric_valid] = np.nan
                daily_mean = np.divide(total, count, out=np.full(n_cells, np.nan), where=count > 0)
                daily_mean[~metric_valid] = np.nan
                long.loc[destination, f"{key}_sum_cdays"] = total
                long.loc[destination, f"{key}_mean_cday"] = daily_mean
            for key in edd_names:
                total, count = _window_sum_count(*metric_cache[key], starts, ends)
                _metric_coverage, metric_valid = _metric_window_validity(
                    count, window_days, required
                )
                total[~metric_valid] = np.nan
                long.loc[destination, f"{key}_sum_cdays"] = total

    for year in event_years:
        if year in daily_by_year:
            continue
        dates = load_daily_dates(daily_root, year)
        canonical = np.asarray(
            [canonical_day_index(value) for value in dates], dtype=np.int16
        )
        daily_by_year[year] = {
            "date": dates,
            "tmax": np.asarray(
                load_daily_metric(daily_root, year, "era5u8_tmax_c")[:, source_selector]
            ),
            "tmax_p90": np.asarray(
                threshold_calendar["tmax"][canonical, source_selector], dtype=np.float32
            ),
        }

    event_metrics = [
        "era5u8_hw_p90_any",
        "era5u8_hw_p90_count",
        "era5u8_hw_p90_total_duration_days",
        "era5u8_hw_p90_max_duration_days",
        "era5u8_hw_p90_mean_intensity_c",
        "era5u8_hw_p90_peak_intensity_c",
        "era5u8_hw_p90_cumulative_heat_cdays",
        "era5u8_hw_p90_left_censored_any",
        "era5u8_hw_p90_right_censored_any",
    ]
    for name in event_metrics:
        long[name] = np.where(valid_event_windows, 0.0, np.nan)

    event_rows: list[dict[str, object]] = []
    bridge_rows: list[dict[str, object]] = []
    total_days = sum(len(daily_by_year[year]["date"]) for year in event_years)
    all_dates_np = np.concatenate(
        [daily_by_year[year]["date"] for year in event_years]
    )
    all_dates = _python_dates(all_dates_np)
    for block_start in range(0, n_cells, int(cell_block_size)):
        block_end = min(block_start + int(cell_block_size), n_cells)
        combined_tmax = np.concatenate(
            [
                daily_by_year[year]["tmax"][:, block_start:block_end]
                for year in event_years
            ],
            axis=0,
        )
        combined_p90 = np.concatenate(
            [
                daily_by_year[year]["tmax_p90"][:, block_start:block_end]
                for year in event_years
            ],
            axis=0,
        )
        if combined_tmax.shape[0] != total_days:
            raise AssertionError("Combined target temperature dates are incomplete")
        for within_block, cell_index in enumerate(range(block_start, block_end)):
            values = combined_tmax[:, within_block].astype(float)
            thresholds = combined_p90[:, within_block].astype(float)
            events = detect_heatwaves(
                all_dates,
                [None if not np.isfinite(value) else float(value) for value in values],
                [None if not np.isfinite(value) else float(value) for value in thresholds],
                min_active=heatwave_min_days,
            )
            cell = sorted_cells.iloc[cell_index]
            source_valid = np.isfinite(values) & np.isfinite(thresholds)
            date_positions = {value: index for index, value in enumerate(all_dates)}
            for event_number, event in enumerate(events, start=1):
                if not any(
                    event.end >= date(year, 1, 1)
                    and event.start <= date(year, 12, 31)
                    for year in years
                ):
                    continue
                event_id = f"{int(cell.era01_cell_id)}:era5u8_hw_p90:{event_number:04d}"
                event_start_index = date_positions[event.start]
                event_end_index = date_positions[event.end]
                source_left_censored = not bool(
                    source_valid[:event_start_index].any()
                )
                source_right_censored = not bool(
                    source_valid[event_end_index + 1 :].any()
                )
                event_rows.append(
                    {
                        "era01_cell_id": int(cell.era01_cell_id),
                        "grid_id_v3": int(cell.grid_id_v3),
                        "event_type": "era5u8_hw_p90",
                        "event_id": event_id,
                        "start_date": event.start,
                        "end_date": event.end,
                        "duration": event.duration,
                        "active_duration": event.active_duration,
                        "span_duration": event.span_duration,
                        "gap_duration": event.gap_duration,
                        "severity": event.severity,
                        "severity_measure": ERA_HEATWAVE_SEVERITY_MEASURE,
                        "severity_unit": ERA_HEATWAVE_SEVERITY_UNIT,
                        "mean_intensity": event.mean_intensity,
                        "peak_intensity": event.peak_intensity,
                        "source_left_censored": source_left_censored,
                        "source_right_censored": source_right_censored,
                    }
                )
                for year in years:
                    if event.end < date(year, 1, 1) or event.start > date(year, 12, 31):
                        continue
                    for window_index, window in enumerate(windows):
                        starts, ends, _days = bounds[(year, window)]
                        if not np.isfinite(starts[cell_index]) or not np.isfinite(ends[cell_index]):
                            continue
                        window_start = date(year, 1, 1) + timedelta(days=int(starts[cell_index]) - 1)
                        window_end = date(year, 1, 1) + timedelta(days=int(ends[cell_index]) - 1)
                        bridge = event_window_bridge_for_run(
                            event, window_start=window_start, window_end=window_end
                        )
                        if bridge is None:
                            continue
                        index = _window_slice_offset(year, window_index, n_cells, windows, years).start + cell_index
                        if not valid_event_windows[index]:
                            continue
                        peak = _event_overlap_peak(event, window_start, window_end)
                        long.at[index, "era5u8_hw_p90_any"] = 1.0
                        long.at[index, "era5u8_hw_p90_count"] += 1.0
                        long.at[index, "era5u8_hw_p90_total_duration_days"] += bridge.active_duration
                        long.at[index, "era5u8_hw_p90_max_duration_days"] = max(
                            float(long.at[index, "era5u8_hw_p90_max_duration_days"]),
                            float(bridge.active_duration),
                        )
                        long.at[index, "era5u8_hw_p90_peak_intensity_c"] = max(
                            float(long.at[index, "era5u8_hw_p90_peak_intensity_c"]), peak
                        )
                        long.at[index, "era5u8_hw_p90_cumulative_heat_cdays"] += bridge.severity
                        long.at[index, "era5u8_hw_p90_left_censored_any"] = max(
                            float(long.at[index, "era5u8_hw_p90_left_censored_any"]),
                            float(bridge.left_censored),
                        )
                        long.at[index, "era5u8_hw_p90_right_censored_any"] = max(
                            float(long.at[index, "era5u8_hw_p90_right_censored_any"]),
                            float(bridge.right_censored),
                        )
                        bridge_payload = asdict(bridge)
                        bridge_payload.pop("event_id", None)
                        bridge_rows.append(
                            {
                                "era01_cell_id": int(cell.era01_cell_id),
                                "grid_id_v3": int(cell.grid_id_v3),
                                "event_id": event_id,
                                "event_type": "era5u8_hw_p90",
                                "year": year,
                                "window": window,
                                "source_left_censored": source_left_censored,
                                "source_right_censored": source_right_censored,
                                **bridge_payload,
                                "severity_measure": ERA_HEATWAVE_SEVERITY_MEASURE,
                                "severity_unit": ERA_HEATWAVE_SEVERITY_UNIT,
                                "peak_intensity": peak,
                            }
                        )
    positive_duration = long["era5u8_hw_p90_total_duration_days"].gt(0)
    long.loc[positive_duration, "era5u8_hw_p90_mean_intensity_c"] = (
        long.loc[positive_duration, "era5u8_hw_p90_cumulative_heat_cdays"]
        / long.loc[positive_duration, "era5u8_hw_p90_total_duration_days"]
    )
    long.loc[valid_event_windows & ~positive_duration.to_numpy(), "era5u8_hw_p90_mean_intensity_c"] = 0.0
    if long.duplicated(["era01_cell_id", "year", "window"]).any():
        raise AssertionError("Temperature long panel key is not unique")
    return long, pd.DataFrame(event_rows), pd.DataFrame(bridge_rows)
