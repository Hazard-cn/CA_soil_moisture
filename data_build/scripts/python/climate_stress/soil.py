"""GLEAM daily/pentad window aggregation and event-window audit bridges."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date, timedelta
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from .aggregate import (
    _prefix_sum_and_count,
    _python_dates,
    _window_extreme,
    _window_slice_offset,
    _window_sum_count,
    _window_template,
)
from .core import (
    build_runs,
    detect_flash_droughts,
    event_window_bridge_for_run,
    required_valid_count,
)
from .gleam import DailyTargetMetrics, PentadTargetMetrics


def _layer_prefix(layer: str) -> str:
    normalized = str(layer).lower()
    if normalized not in {"smrz", "sms"}:
        raise ValueError("layer must be SMrz or SMs")
    return f"gleam43a_{normalized}"


def _pentad_doys(year: int) -> tuple[tuple[int, ...], ...]:
    from .core import calendar_pentad_dates

    start = date(int(year), 1, 1)
    return tuple(
        tuple((value - start).days + 1 for value in calendar_pentad_dates(int(year), pentad))
        for pentad in range(1, 74)
    )


def _pentad_overlap_matrix(
    year: int,
    starts: np.ndarray,
    ends: np.ndarray,
) -> np.ndarray:
    overlap = np.zeros((73, starts.size), dtype=np.int8)
    valid = np.isfinite(starts) & np.isfinite(ends) & (starts <= ends)
    for pentad_index, doys in enumerate(_pentad_doys(year)):
        total = np.zeros(starts.size, dtype=np.int8)
        for doy in doys:
            total += (valid & (starts <= doy) & (ends >= doy)).astype(np.int8)
        overlap[pentad_index] = total
    return overlap


def _longest_weighted_run(states: np.ndarray, overlap_days: np.ndarray) -> np.ndarray:
    """Longest consecutive pentad run, measured in overlapping analysis days."""

    if states.shape != overlap_days.shape:
        raise ValueError("states and overlap_days must have the same shape")
    n_cells = states.shape[1]
    longest = np.zeros(n_cells, dtype=np.float64)
    current = np.zeros(n_cells, dtype=np.float64)
    for row in range(states.shape[0]):
        active = np.isfinite(states[row]) & (states[row] == 1) & (overlap_days[row] > 0)
        current = np.where(active, current + overlap_days[row], 0.0)
        longest = np.maximum(longest, current)
    return longest


def _daily_run_inputs(
    values: np.ndarray,
    thresholds: np.ndarray,
) -> tuple[list[bool | None], list[float | None]]:
    mask: list[bool | None] = []
    intensity: list[float | None] = []
    for value, threshold in zip(values, thresholds, strict=True):
        if not np.isfinite(value) or not np.isfinite(threshold):
            mask.append(None)
            intensity.append(None)
        else:
            active = bool(value < threshold)
            mask.append(active)
            intensity.append(float(threshold - value) if active else 0.0)
    return mask, intensity


def _run_overlap_peak(event, window_start: date, window_end: date) -> float:
    intensities = [
        segment.severity / segment.days
        for segment in event.segments
        if segment.active
        and segment.start <= window_end
        and segment.end_exclusive > window_start
    ]
    return max(intensities) if intensities else 0.0


def _fd_variant_prefix(prefix: str, variant: str) -> str:
    return f"{prefix}_fd_{variant}"


def aggregate_gleam_windows(
    panel: pd.DataFrame,
    *,
    layer: str,
    years: Sequence[int],
    event_years: Sequence[int] | None = None,
    windows: Sequence[str],
    daily_dates: Mapping[int, Sequence[date]],
    daily_values: Mapping[int, np.ndarray],
    daily_metrics: Mapping[int, DailyTargetMetrics],
    pentad_values: Mapping[int, np.ndarray],
    pentad_metrics: Mapping[int, PentadTargetMetrics],
    minimum_coverage: float = 0.90,
    cell_block_size: int = 128,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Aggregate one GLEAM layer and preserve event/bridge audit rows."""

    prefix = _layer_prefix(layer)
    years = tuple(sorted(int(value) for value in years))
    if len(set(years)) != len(years):
        raise ValueError("years must be unique")
    event_years = tuple(
        sorted(int(value) for value in (years if event_years is None else event_years))
    )
    if not set(years).issubset(event_years):
        raise ValueError("GLEAM output years must be contained in event years")
    windows = tuple(windows)
    long, bounds = _window_template(panel, windows, years)
    n_cells = int(panel["era01_cell_id"].nunique())
    cells = (
        panel[["era01_cell_id", "grid_id_v3"]]
        .drop_duplicates("era01_cell_id")
        .sort_values("era01_cell_id")
        .reset_index(drop=True)
    )
    if len(long) != n_cells * len(years) * len(windows):
        raise AssertionError("GLEAM long template is not balanced")

    base_columns = (
        f"{prefix}_daily_valid_days",
        f"{prefix}_daily_coverage",
        f"{prefix}_p10_event_valid_days",
        f"{prefix}_p10_event_coverage",
        f"{prefix}_mean_m3m3",
        f"{prefix}_min_m3m3",
        f"{prefix}_pentad_valid_days",
        f"{prefix}_pentad_coverage",
        f"{prefix}_pct_mean",
        f"{prefix}_p10_exposure_days",
        f"{prefix}_p20_exposure_days",
        f"{prefix}_p20_longest_spell_days",
        f"{prefix}_min_pct",
        f"{prefix}_peak_dryness20",
        f"{prefix}_p20_deficit_area_pctdays",
    )
    for column in base_columns:
        long[column] = np.nan

    overlap_cache: dict[tuple[int, str], np.ndarray] = {}
    pentad_valid_windows = np.zeros(len(long), dtype=bool)
    daily_valid_windows = np.zeros(len(long), dtype=bool)
    daily_event_valid_windows = np.zeros(len(long), dtype=bool)
    for year in years:
        values = np.asarray(daily_values[year], dtype=float)
        if values.shape[1] != n_cells or values.shape[0] != len(daily_dates[year]):
            raise ValueError(f"Daily {layer} shape is invalid for {year}")
        daily_prefix, daily_counts = _prefix_sum_and_count(values)
        daily_q10 = np.asarray(daily_metrics[year].q10, dtype=float)
        if daily_q10.shape != values.shape:
            raise ValueError(f"Daily {layer} Q10 shape is invalid for {year}")
        joint_event_inputs = np.where(
            np.isfinite(values) & np.isfinite(daily_q10), 1.0, np.nan
        )
        _joint_sum, joint_event_counts = _prefix_sum_and_count(joint_event_inputs)
        pvalues = np.asarray(pentad_values[year], dtype=float)
        metrics = pentad_metrics[year]
        if pvalues.shape != (73, n_cells) or metrics.percentile.shape != pvalues.shape:
            raise ValueError(f"Pentad {layer} shape is invalid for {year}")
        for window_index, window in enumerate(windows):
            destination = _window_slice_offset(year, window_index, n_cells, windows, years)
            starts, ends, window_days = bounds[(year, window)]
            total, valid_days = _window_sum_count(daily_prefix, daily_counts, starts, ends)
            required_daily = np.asarray(
                [
                    required_valid_count(int(value), minimum_coverage) if np.isfinite(value) else 1
                    for value in window_days
                ],
                dtype=np.int32,
            )
            valid_daily = np.isfinite(window_days) & (valid_days >= required_daily)
            daily_valid_windows[np.asarray(destination)] = valid_daily
            coverage = np.divide(
                valid_days,
                window_days,
                out=np.full(n_cells, np.nan),
                where=np.isfinite(window_days) & (window_days > 0),
            )
            _joint_total, joint_valid_days = _window_sum_count(
                _joint_sum, joint_event_counts, starts, ends
            )
            valid_daily_event = np.isfinite(window_days) & (
                joint_valid_days >= required_daily
            )
            daily_event_valid_windows[np.asarray(destination)] = valid_daily_event
            event_coverage = np.divide(
                joint_valid_days,
                window_days,
                out=np.full(n_cells, np.nan),
                where=np.isfinite(window_days) & (window_days > 0),
            )
            mean = np.divide(total, valid_days, out=np.full(n_cells, np.nan), where=valid_days > 0)
            minimum = _window_extreme(values, starts, ends, mode="min")
            mean[~valid_daily] = np.nan
            minimum[~valid_daily] = np.nan
            long.loc[destination, f"{prefix}_daily_valid_days"] = valid_days
            long.loc[destination, f"{prefix}_daily_coverage"] = coverage
            long.loc[destination, f"{prefix}_p10_event_valid_days"] = joint_valid_days
            long.loc[destination, f"{prefix}_p10_event_coverage"] = event_coverage
            long.loc[destination, f"{prefix}_mean_m3m3"] = mean
            long.loc[destination, f"{prefix}_min_m3m3"] = minimum

            overlap = _pentad_overlap_matrix(year, starts, ends)
            overlap_cache[(year, window)] = overlap
            expected = overlap.sum(axis=0).astype(np.int32)
            valid_pentad = np.isfinite(metrics.percentile)
            represented = (overlap * valid_pentad).sum(axis=0).astype(np.int32)
            required_pentad = np.asarray(
                [required_valid_count(int(value), minimum_coverage) if value > 0 else 1 for value in expected],
                dtype=np.int32,
            )
            valid_window = (expected > 0) & (represented >= required_pentad)
            pentad_valid_windows[np.asarray(destination)] = valid_window
            pcoverage = np.divide(
                represented, expected, out=np.full(n_cells, np.nan), where=expected > 0
            )
            weighted_pct = np.nansum(metrics.percentile * overlap, axis=0)
            mean_pct = np.divide(
                weighted_pct, represented, out=np.full(n_cells, np.nan), where=represented > 0
            )
            p10_days = np.nansum(metrics.below_p10 * overlap, axis=0)
            p20_days = np.nansum(metrics.below_p20 * overlap, axis=0)
            deficit = np.nansum(np.maximum(20.0 - metrics.percentile, 0.0) * overlap, axis=0)
            masked_pct = np.where((overlap > 0) & valid_pentad, metrics.percentile, np.nan)
            minimum_pct = np.min(
                np.where(np.isfinite(masked_pct), masked_pct, np.inf), axis=0
            )
            minimum_pct[~np.isfinite(masked_pct).any(axis=0)] = np.nan
            longest = _longest_weighted_run(metrics.below_p20, overlap)
            for array in (mean_pct, p10_days, p20_days, deficit, minimum_pct, longest):
                array[~valid_window] = np.nan
            peak = np.maximum(20.0 - minimum_pct, 0.0)
            long.loc[destination, f"{prefix}_pentad_valid_days"] = represented
            long.loc[destination, f"{prefix}_pentad_coverage"] = pcoverage
            long.loc[destination, f"{prefix}_pct_mean"] = mean_pct
            long.loc[destination, f"{prefix}_p10_exposure_days"] = p10_days
            long.loc[destination, f"{prefix}_p20_exposure_days"] = p20_days
            long.loc[destination, f"{prefix}_p20_longest_spell_days"] = longest
            long.loc[destination, f"{prefix}_min_pct"] = minimum_pct
            long.loc[destination, f"{prefix}_peak_dryness20"] = peak
            long.loc[destination, f"{prefix}_p20_deficit_area_pctdays"] = deficit

    daily_event_fields = (
        "any",
        "count",
        "total_duration_days",
        "max_duration_days",
        "span_duration_days",
        "gap_duration_days",
        "total_severity_m3m3_days",
        "peak_intensity_m3m3",
        "left_censored_any",
        "right_censored_any",
    )
    for variant in ("main_gap0", "sensitivity_gap2"):
        for field in daily_event_fields:
            name = f"{prefix}_p10_event_{variant}_{field}"
            long[name] = np.where(daily_event_valid_windows, 0.0, np.nan)

    fd_fields = (
        "any",
        "count",
        "total_duration_days",
        "max_duration_days",
        "total_dry_phase_days",
        "total_severity_pctdays",
        "max_severity_pctdays",
        "mean_onset_speed",
        "max_onset_speed",
        "min_sm_pct",
        "recovered_count",
        "mean_recovery_duration_days",
        "max_recovery_duration_days",
        "left_censored_any",
        "right_censored_any",
    )
    for variant in ("main", "strict"):
        for field in fd_fields:
            long[f"{_fd_variant_prefix(prefix, variant)}_{field}"] = np.where(
                pentad_valid_windows, 0.0, np.nan
            )

    event_rows: list[dict[str, object]] = []
    bridge_rows: list[dict[str, object]] = []
    all_daily_dates = [item for year in event_years for item in daily_dates[year]]
    pentad_year_parts: list[np.ndarray] = []
    pentad_number_parts: list[np.ndarray] = []
    for position, year in enumerate(event_years):
        if position and year != event_years[position - 1] + 1:
            # A missing source year is a hard event boundary.
            pentad_year_parts.append(np.asarray([-1], dtype=np.int16))
            pentad_number_parts.append(np.asarray([0], dtype=np.int8))
        pentad_year_parts.append(np.full(73, year, dtype=np.int16))
        pentad_number_parts.append(np.arange(1, 74, dtype=np.int8))
    all_pentad_years = np.concatenate(pentad_year_parts)
    all_pentad_numbers = np.concatenate(pentad_number_parts)
    for block_start in range(0, n_cells, int(cell_block_size)):
        block_end = min(block_start + int(cell_block_size), n_cells)
        combined_daily = np.concatenate(
            [
                np.asarray(daily_values[year])[:, block_start:block_end]
                for year in event_years
            ],
            axis=0,
        )
        combined_q10 = np.concatenate(
            [
                np.asarray(daily_metrics[year].q10)[:, block_start:block_end]
                for year in event_years
            ],
            axis=0,
        )
        pentad_parts: list[np.ndarray] = []
        for position, year in enumerate(event_years):
            if position and year != event_years[position - 1] + 1:
                pentad_parts.append(
                    np.full((1, block_end - block_start), np.nan, dtype=float)
                )
            pentad_parts.append(
                np.asarray(pentad_metrics[year].percentile)[
                    :, block_start:block_end
                ]
            )
        combined_pct = np.concatenate(pentad_parts, axis=0)
        for local_index, cell_index in enumerate(range(block_start, block_end)):
            cell_id = int(cells.at[cell_index, "era01_cell_id"])
            grid_id = int(cells.at[cell_index, "grid_id_v3"])
            mask, intensity = _daily_run_inputs(
                combined_daily[:, local_index], combined_q10[:, local_index]
            )
            source_valid_daily = np.isfinite(
                combined_daily[:, local_index]
            ) & np.isfinite(combined_q10[:, local_index])
            date_positions = {
                value: index for index, value in enumerate(all_daily_dates)
            }
            for variant, gap in (("main_gap0", 0), ("sensitivity_gap2", 2)):
                runs = build_runs(
                    all_daily_dates,
                    mask,
                    min_active=5,
                    max_gap=gap,
                    intensity=intensity,
                    event_id_prefix=f"{layer.lower()}-p10-{variant}",
                )
                for event_number, event in enumerate(runs, start=1):
                    if not any(
                        event.end >= date(year, 1, 1)
                        and event.start <= date(year, 12, 31)
                        for year in years
                    ):
                        continue
                    event_id = f"{cell_id}:{prefix}_p10_{variant}:{event_number:04d}"
                    event_start_index = date_positions[event.start]
                    event_end_index = date_positions[event.end]
                    source_left_censored = not bool(
                        source_valid_daily[:event_start_index].any()
                    )
                    source_right_censored = not bool(
                        source_valid_daily[event_end_index + 1 :].any()
                    )
                    event_payload = asdict(event)
                    event_payload.pop("event_id", None)
                    event_rows.append(
                        {
                            "era01_cell_id": cell_id,
                            "grid_id_v3": grid_id,
                            "layer": layer,
                            "event_family": "daily_p10",
                            "variant": variant,
                            "event_id": event_id,
                            "start_date": event.start,
                            "end_date": event.end,
                            "duration": event.duration,
                            "active_duration": event.active_duration,
                            "span_duration": event.span_duration,
                            "gap_duration": event.gap_duration,
                            "severity": event.severity,
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
                            row_index = (
                                _window_slice_offset(year, window_index, n_cells, windows, years).start
                                + cell_index
                            )
                            if not daily_event_valid_windows[row_index]:
                                continue
                            stem = f"{prefix}_p10_event_{variant}"
                            long.at[row_index, f"{stem}_any"] = 1.0
                            long.at[row_index, f"{stem}_count"] += 1.0
                            long.at[row_index, f"{stem}_total_duration_days"] += bridge.active_duration
                            long.at[row_index, f"{stem}_max_duration_days"] = max(
                                long.at[row_index, f"{stem}_max_duration_days"], bridge.active_duration
                            )
                            long.at[row_index, f"{stem}_span_duration_days"] += bridge.span_duration
                            long.at[row_index, f"{stem}_gap_duration_days"] += bridge.gap_duration
                            long.at[row_index, f"{stem}_total_severity_m3m3_days"] += bridge.severity
                            long.at[row_index, f"{stem}_peak_intensity_m3m3"] = max(
                                long.at[row_index, f"{stem}_peak_intensity_m3m3"],
                                _run_overlap_peak(event, window_start, window_end),
                            )
                            long.at[row_index, f"{stem}_left_censored_any"] = max(
                                long.at[row_index, f"{stem}_left_censored_any"],
                                float(bridge.left_censored),
                            )
                            long.at[row_index, f"{stem}_right_censored_any"] = max(
                                long.at[row_index, f"{stem}_right_censored_any"],
                                float(bridge.right_censored),
                            )
                            payload = asdict(bridge)
                            payload.pop("event_id", None)
                            bridge_rows.append(
                                {
                                    "era01_cell_id": cell_id,
                                    "grid_id_v3": grid_id,
                                    "event_id": event_id,
                                    "event_family": "daily_p10",
                                    "variant": variant,
                                    "year": year,
                                    "window": window,
                                    "source_left_censored": source_left_censored,
                                    "source_right_censored": source_right_censored,
                                    **payload,
                                }
                            )

            pct = combined_pct[:, local_index]
            for variant, min_span, recovery in (("main", 3, 1), ("strict", 4, 2)):
                events = detect_flash_droughts(
                    [None if not np.isfinite(value) else float(value) for value in pct],
                    min_span_pentads=min_span,
                    recovery_confirm=recovery,
                )
                for event_number, event in enumerate(events, start=1):
                    support_years = set(
                        int(value)
                        for value in all_pentad_years[
                            event.start_index : event.end_index + 1
                        ]
                    )
                    if not support_years.intersection(years):
                        continue
                    event_id = f"{cell_id}:{prefix}_fd_{variant}:{event_number:04d}"
                    support_values = pct[event.start_index : event.end_index + 1]
                    minimum_index = event.start_index + int(np.argmin(support_values))
                    recovery_duration_days = (
                        None
                        if event.recovery_index is None
                        else 5 * (event.recovery_index - minimum_index)
                    )
                    event_payload = asdict(event)
                    event_payload.pop("event_id", None)
                    valid_pct = np.isfinite(pct)
                    source_left_censored = not bool(
                        valid_pct[: event.start_index].any()
                    )
                    source_right_censored = not bool(
                        valid_pct[event.end_index + 1 :].any()
                    )
                    event_rows.append(
                        {
                            "era01_cell_id": cell_id,
                            "grid_id_v3": grid_id,
                            "layer": layer,
                            "event_family": "flash_drought",
                            "variant": variant,
                            "event_id": event_id,
                            **event_payload,
                            "start_year": int(all_pentad_years[event.start_index]),
                            "start_pentad": int(all_pentad_numbers[event.start_index]),
                            "end_year": int(all_pentad_years[event.end_index]),
                            "end_pentad": int(all_pentad_numbers[event.end_index]),
                            "minimum_index": minimum_index,
                            "recovery_duration_days": recovery_duration_days,
                            "source_left_censored": source_left_censored,
                            "source_right_censored": source_right_censored,
                        }
                    )
                    for year in years:
                        event_indices = np.arange(event.start_index, event.end_index + 1)
                        same_year = event_indices[all_pentad_years[event_indices] == year]
                        if same_year.size == 0:
                            continue
                        local_pentads = all_pentad_numbers[same_year].astype(np.int64) - 1
                        for window_index, window in enumerate(windows):
                            overlap = overlap_cache[(year, window)][local_pentads, cell_index]
                            if int(overlap.sum()) == 0:
                                continue
                            row_index = (
                                _window_slice_offset(year, window_index, n_cells, windows, years).start
                                + cell_index
                            )
                            if not pentad_valid_windows[row_index]:
                                continue
                            q = pct[same_year]
                            duration = int(overlap.sum())
                            dry_duration = int(overlap[q < 20.0].sum())
                            severity = float(np.sum(overlap * np.maximum(40.0 - q, 0.0)))
                            starts, ends, _days = bounds[(year, window)]
                            window_start_doy = int(starts[cell_index])
                            window_end_doy = int(ends[cell_index])
                            event_first_doy = min(_pentad_doys(year)[int(local_pentads[0])])
                            event_last_doy = max(_pentad_doys(year)[int(local_pentads[-1])])
                            left_censored = event_first_doy < window_start_doy or event.start_index < same_year[0]
                            right_censored = event_last_doy > window_end_doy or event.end_index > same_year[-1]
                            stem = _fd_variant_prefix(prefix, variant)
                            long.at[row_index, f"{stem}_any"] = 1.0
                            long.at[row_index, f"{stem}_count"] += 1.0
                            long.at[row_index, f"{stem}_total_duration_days"] += duration
                            long.at[row_index, f"{stem}_max_duration_days"] = max(
                                long.at[row_index, f"{stem}_max_duration_days"], duration
                            )
                            long.at[row_index, f"{stem}_total_dry_phase_days"] += dry_duration
                            long.at[row_index, f"{stem}_total_severity_pctdays"] += severity
                            long.at[row_index, f"{stem}_max_severity_pctdays"] = max(
                                long.at[row_index, f"{stem}_max_severity_pctdays"], severity
                            )
                            current_count = long.at[row_index, f"{stem}_count"]
                            previous_sum_speed = long.at[row_index, f"{stem}_mean_onset_speed"] * (current_count - 1)
                            long.at[row_index, f"{stem}_mean_onset_speed"] = (
                                previous_sum_speed + event.onset_speed
                            ) / current_count
                            long.at[row_index, f"{stem}_max_onset_speed"] = max(
                                long.at[row_index, f"{stem}_max_onset_speed"], event.onset_speed
                            )
                            current_min = long.at[row_index, f"{stem}_min_sm_pct"]
                            long.at[row_index, f"{stem}_min_sm_pct"] = (
                                event.minimum_percentile
                                if current_count == 1
                                else min(current_min, event.minimum_percentile)
                            )
                            if recovery_duration_days is not None:
                                recovered_count = long.at[row_index, f"{stem}_recovered_count"] + 1.0
                                previous_recovery = (
                                    long.at[row_index, f"{stem}_mean_recovery_duration_days"]
                                    * (recovered_count - 1.0)
                                )
                                long.at[row_index, f"{stem}_recovered_count"] = recovered_count
                                long.at[row_index, f"{stem}_mean_recovery_duration_days"] = (
                                    previous_recovery + recovery_duration_days
                                ) / recovered_count
                                long.at[row_index, f"{stem}_max_recovery_duration_days"] = max(
                                    long.at[row_index, f"{stem}_max_recovery_duration_days"],
                                    recovery_duration_days,
                                )
                            long.at[row_index, f"{stem}_left_censored_any"] = max(
                                long.at[row_index, f"{stem}_left_censored_any"], float(left_censored)
                            )
                            long.at[row_index, f"{stem}_right_censored_any"] = max(
                                long.at[row_index, f"{stem}_right_censored_any"], float(right_censored)
                            )
                            bridge_rows.append(
                                {
                                    "era01_cell_id": cell_id,
                                    "grid_id_v3": grid_id,
                                    "event_id": event_id,
                                    "event_family": "flash_drought",
                                    "variant": variant,
                                    "year": year,
                                    "window": window,
                                    "event_count": 1,
                                    "duration": duration,
                                    "active_duration": duration,
                                    "span_duration": duration,
                                    "gap_duration": 0,
                                    "dry_phase_duration": dry_duration,
                                    "severity": severity,
                                    "left_censored": left_censored,
                                    "right_censored": right_censored,
                                    "source_left_censored": source_left_censored,
                                    "source_right_censored": source_right_censored,
                                }
                            )
    for variant in ("main", "strict"):
        stem = _fd_variant_prefix(prefix, variant)
        no_recovery = pentad_valid_windows & long[f"{stem}_recovered_count"].eq(0).to_numpy()
        long.loc[no_recovery, f"{stem}_mean_recovery_duration_days"] = np.nan
        long.loc[no_recovery, f"{stem}_max_recovery_duration_days"] = np.nan
    return long, pd.DataFrame(event_rows), pd.DataFrame(bridge_rows)
