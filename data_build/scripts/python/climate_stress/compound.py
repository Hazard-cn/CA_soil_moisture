"""Compound heat and soil-moisture event algorithms.

The module keeps heat excess (degree-C days) and soil-moisture deficit
(``m3 m-3 days``) as separate quantities.  It never constructs a synthetic
severity by adding unlike units.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from .core import (
    FlashDroughtEvent,
    RunEvent,
    build_runs,
    calendar_pentad,
    classify_hot_flash_drought,
    coverage_ok,
    event_window_bridge_for_run,
)


COMPOUND_VARIANTS: dict[str, int] = {"main_gap0": 0, "sensitivity_gap2": 2}


def _finite(value: object) -> float | None:
    if value is None:
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def _tri_hot_state(value: object) -> bool | None:
    """Normalize bool/None or pipeline int8 {-1,0,1} heat states."""

    if value is None:
        return None
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    numeric = _finite(value)
    if numeric is None or numeric == -1.0:
        return None
    if numeric == 0.0:
        return False
    if numeric == 1.0:
        return True
    raise ValueError("Daily heat state must be bool, None, or one of {-1, 0, 1}")


def _validate_dates(dates: Sequence[date]) -> None:
    if len(set(dates)) != len(dates) or any(
        current <= previous for previous, current in zip(dates, dates[1:])
    ):
        raise ValueError("dates must be unique and strictly increasing")


@dataclass(frozen=True)
class DailyCompoundEvent:
    """One full-series hot-and-dry event with two separate intensity measures."""

    layer: str
    variant: str
    run: RunEvent
    heat_excess_by_segment: tuple[float, ...]
    sm_deficit_by_segment: tuple[float, ...]

    def __post_init__(self) -> None:
        expected = len(self.run.segments)
        if len(self.heat_excess_by_segment) != expected or len(
            self.sm_deficit_by_segment
        ) != expected:
            raise ValueError("Compound contributions must align with run segments")
        if any(value < 0 or not math.isfinite(value) for value in self.heat_excess_by_segment):
            raise ValueError("Heat excess contributions must be finite and non-negative")
        if any(value < 0 or not math.isfinite(value) for value in self.sm_deficit_by_segment):
            raise ValueError("SM deficit contributions must be finite and non-negative")

    @property
    def event_id(self) -> str:
        return self.run.event_id

    @property
    def start(self) -> date:
        return self.run.start

    @property
    def end(self) -> date:
        return self.run.end

    @property
    def duration(self) -> int:
        return self.run.duration

    @property
    def active_duration(self) -> int:
        return self.run.active_duration

    @property
    def span_duration(self) -> int:
        return self.run.span_duration

    @property
    def gap_duration(self) -> int:
        return self.run.gap_duration

    @property
    def heat_excess_cdays(self) -> float:
        return sum(self.heat_excess_by_segment)

    @property
    def sm_deficit_m3m3_days(self) -> float:
        return sum(self.sm_deficit_by_segment)


def _daily_compound_inputs(
    dates: Sequence[date],
    tmax: Sequence[float | None],
    tmax_p90: Sequence[float | None],
    sm: Sequence[float | None],
    sm_p10: Sequence[float | None],
) -> tuple[list[bool | None], list[float | None], list[float | None]]:
    lengths = {len(dates), len(tmax), len(tmax_p90), len(sm), len(sm_p10)}
    if len(lengths) != 1:
        raise ValueError("All daily compound inputs must have equal length")
    _validate_dates(dates)
    mask: list[bool | None] = []
    heat_excess: list[float | None] = []
    sm_deficit: list[float | None] = []
    for raw_tmax, raw_p90, raw_sm, raw_p10 in zip(
        tmax, tmax_p90, sm, sm_p10, strict=True
    ):
        value_tmax = _finite(raw_tmax)
        threshold_tmax = _finite(raw_p90)
        value_sm = _finite(raw_sm)
        threshold_sm = _finite(raw_p10)
        if None in (value_tmax, threshold_tmax, value_sm, threshold_sm):
            mask.append(None)
            heat_excess.append(None)
            sm_deficit.append(None)
            continue
        active = value_tmax > threshold_tmax and value_sm < threshold_sm
        mask.append(active)
        heat_excess.append(value_tmax - threshold_tmax if active else 0.0)
        sm_deficit.append(threshold_sm - value_sm if active else 0.0)
    return mask, heat_excess, sm_deficit


def detect_daily_compound_events(
    dates: Sequence[date],
    tmax: Sequence[float | None],
    tmax_p90: Sequence[float | None],
    sm: Sequence[float | None],
    sm_p10: Sequence[float | None],
    *,
    layer: str,
    minimum_active_days: int = 5,
) -> list[DailyCompoundEvent]:
    """Detect both frozen gap variants on one complete target sequence."""

    mask, heat_excess, sm_deficit = _daily_compound_inputs(
        dates, tmax, tmax_p90, sm, sm_p10
    )
    date_to_index = {value: index for index, value in enumerate(dates)}
    events: list[DailyCompoundEvent] = []
    for variant, max_gap in COMPOUND_VARIANTS.items():
        runs = build_runs(
            dates,
            mask,
            min_active=minimum_active_days,
            max_gap=max_gap,
            intensity=heat_excess,
            event_id_prefix=f"{layer.lower()}-hot-p10-{variant}",
        )
        for run in runs:
            heat: list[float] = []
            soil: list[float] = []
            for segment in run.segments:
                index = date_to_index[segment.start]
                if segment.active:
                    heat.append(float(heat_excess[index]))
                    soil.append(float(sm_deficit[index]))
                else:
                    heat.append(0.0)
                    soil.append(0.0)
            events.append(
                DailyCompoundEvent(
                    layer=layer,
                    variant=variant,
                    run=run,
                    heat_excess_by_segment=tuple(heat),
                    sm_deficit_by_segment=tuple(soil),
                )
            )
    return events


def detect_daily_compound_events_by_layer(
    dates: Sequence[date],
    tmax: Sequence[float | None],
    tmax_p90: Sequence[float | None],
    soil_moisture: Mapping[str, Sequence[float | None]],
    soil_moisture_p10: Mapping[str, Sequence[float | None]],
    *,
    minimum_active_days: int = 5,
) -> list[DailyCompoundEvent]:
    """Detect the same event family independently for each supplied SM layer."""

    if set(soil_moisture) != set(soil_moisture_p10):
        raise ValueError("SM value and P10 mappings must contain the same layers")
    result: list[DailyCompoundEvent] = []
    for layer in sorted(soil_moisture):
        result.extend(
            detect_daily_compound_events(
                dates,
                tmax,
                tmax_p90,
                soil_moisture[layer],
                soil_moisture_p10[layer],
                layer=layer,
                minimum_active_days=minimum_active_days,
            )
        )
    return result


def compound_event_table(events: Sequence[DailyCompoundEvent]) -> pd.DataFrame:
    """Return the complete event audit without a mixed-unit severity column."""

    rows = [
        {
            "layer": event.layer,
            "variant": event.variant,
            "event_id": event.event_id,
            "start_date": event.start,
            "end_date": event.end,
            "duration": event.duration,
            "active_duration": event.active_duration,
            "span_duration": event.span_duration,
            "gap_duration": event.gap_duration,
            "heat_excess_cdays": event.heat_excess_cdays,
            "sm_deficit_m3m3_days": event.sm_deficit_m3m3_days,
        }
        for event in events
    ]
    return pd.DataFrame(rows)


@dataclass(frozen=True)
class CompoundEventWindowBridge:
    layer: str
    variant: str
    event_id: str
    window: str
    event_count: int
    duration: int
    active_duration: int
    span_duration: int
    gap_duration: int
    heat_excess_cdays: float
    sm_deficit_m3m3_days: float
    left_censored: bool
    right_censored: bool


def bridge_daily_compound_event(
    event: DailyCompoundEvent,
    *,
    window: str,
    window_start: date,
    window_end: date,
) -> CompoundEventWindowBridge | None:
    """Bridge a complete event; support-only gap overlap still counts."""

    core_bridge = event_window_bridge_for_run(
        event.run, window_start=window_start, window_end=window_end
    )
    if core_bridge is None:
        return None
    heat = 0.0
    soil = 0.0
    window_end_exclusive = window_end + timedelta(days=1)
    for index, segment in enumerate(event.run.segments):
        overlap = max(
            (
                min(segment.end_exclusive, window_end_exclusive)
                - max(segment.start, window_start)
            ).days,
            0,
        )
        if overlap and segment.active:
            fraction = overlap / segment.days
            heat += event.heat_excess_by_segment[index] * fraction
            soil += event.sm_deficit_by_segment[index] * fraction
    return CompoundEventWindowBridge(
        layer=event.layer,
        variant=event.variant,
        event_id=event.event_id,
        window=window,
        event_count=1,
        duration=core_bridge.duration,
        active_duration=core_bridge.active_duration,
        span_duration=core_bridge.span_duration,
        gap_duration=core_bridge.gap_duration,
        heat_excess_cdays=heat,
        sm_deficit_m3m3_days=soil,
        left_censored=core_bridge.left_censored,
        right_censored=core_bridge.right_censored,
    )


def compound_event_window_table(
    events: Sequence[DailyCompoundEvent],
    windows: Mapping[str, tuple[date, date]],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for event in events:
        for name, (start, end) in windows.items():
            bridge = bridge_daily_compound_event(
                event, window=name, window_start=start, window_end=end
            )
            if bridge is not None:
                rows.append(asdict(bridge))
    return pd.DataFrame(rows)


@dataclass(frozen=True)
class CompoundWindowAggregate:
    layer: str
    variant: str
    window: str
    window_start: date
    window_end: date
    coverage: float
    valid_days: int
    expected_days: int
    any_event: bool | None
    event_count: int | None
    total_active_duration: int | None
    total_span_duration: int | None
    total_gap_duration: int | None
    max_active_duration: int | None
    max_span_duration: int | None
    heat_excess_cdays: float | None
    sm_deficit_m3m3_days: float | None


def aggregate_daily_compound_window(
    events: Sequence[DailyCompoundEvent],
    dates: Sequence[date],
    valid_state: Sequence[bool],
    *,
    layer: str,
    variant: str,
    window: str,
    window_start: date,
    window_end: date,
    minimum_coverage: float = 0.9,
) -> CompoundWindowAggregate:
    """Aggregate event bridges after applying the 90% window coverage gate."""

    if len(dates) != len(valid_state):
        raise ValueError("dates and valid_state must have equal length")
    _validate_dates(dates)
    if window_end < window_start:
        raise ValueError("window_end must not precede window_start")
    expected = (window_end - window_start).days + 1
    valid_lookup = {day: bool(valid) for day, valid in zip(dates, valid_state, strict=True)}
    valid_days = sum(
        valid_lookup.get(window_start + timedelta(days=offset), False)
        for offset in range(expected)
    )
    coverage = valid_days / expected
    if not coverage_ok(valid_days, expected, minimum_coverage):
        return CompoundWindowAggregate(
            layer,
            variant,
            window,
            window_start,
            window_end,
            coverage,
            valid_days,
            expected,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
    bridges = [
        bridge
        for event in events
        if event.layer == layer and event.variant == variant
        if (
            bridge := bridge_daily_compound_event(
                event,
                window=window,
                window_start=window_start,
                window_end=window_end,
            )
        )
        is not None
    ]
    if not bridges:
        return CompoundWindowAggregate(
            layer,
            variant,
            window,
            window_start,
            window_end,
            coverage,
            valid_days,
            expected,
            False,
            0,
            0,
            0,
            0,
            0,
            0,
            0.0,
            0.0,
        )
    return CompoundWindowAggregate(
        layer,
        variant,
        window,
        window_start,
        window_end,
        coverage,
        valid_days,
        expected,
        True,
        len(bridges),
        sum(item.active_duration for item in bridges),
        sum(item.span_duration for item in bridges),
        sum(item.gap_duration for item in bridges),
        max(item.active_duration for item in bridges),
        max(item.span_duration for item in bridges),
        sum(item.heat_excess_cdays for item in bridges),
        sum(item.sm_deficit_m3m3_days for item in bridges),
    )


def compound_valid_state(
    tmax: Sequence[float | None],
    tmax_p90: Sequence[float | None],
    sm: Sequence[float | None],
    sm_p10: Sequence[float | None],
) -> np.ndarray:
    """Return whether all four daily inputs needed by the event are observed."""

    lengths = {len(tmax), len(tmax_p90), len(sm), len(sm_p10)}
    if len(lengths) != 1:
        raise ValueError("Daily compound inputs must have equal length")
    return np.asarray(
        [
            all(_finite(value) is not None for value in values)
            for values in zip(tmax, tmax_p90, sm, sm_p10, strict=True)
        ],
        dtype=bool,
    )


def map_pentad_percentile_to_daily(
    daily_dates: Sequence[date],
    pentad_years: Sequence[int],
    pentad_numbers: Sequence[int],
    pentad_percentiles: Sequence[float | None],
) -> np.ndarray:
    """Map fixed-pentad SM percentiles to their five analysis dates."""

    if not (
        len(pentad_years) == len(pentad_numbers) == len(pentad_percentiles)
    ):
        raise ValueError("Pentad keys and percentiles must have equal length")
    lookup: dict[tuple[int, int], float | None] = {}
    for year, pentad, raw in zip(
        pentad_years, pentad_numbers, pentad_percentiles, strict=True
    ):
        key = (int(year), int(pentad))
        if key in lookup:
            raise ValueError(f"Duplicate pentad key: {key}")
        lookup[key] = _finite(raw)
    result = np.full(len(daily_dates), np.nan, dtype=np.float64)
    for index, day in enumerate(daily_dates):
        pentad = calendar_pentad(day)
        if pentad is None:
            continue
        value = lookup.get((day.year, pentad))
        if value is not None:
            result[index] = value
    return result


@dataclass(frozen=True)
class PentadDailyOverlapStates:
    daily_pentad_percentile: np.ndarray
    valid: np.ndarray
    primary_hot_q20: np.ndarray
    strict_hot_q10: np.ndarray


def build_pentad_daily_overlap_states(
    daily_dates: Sequence[date],
    daily_hot_state: Sequence[bool | int | None],
    pentad_years: Sequence[int],
    pentad_numbers: Sequence[int],
    pentad_percentiles: Sequence[float | None],
) -> PentadDailyOverlapStates:
    if len(daily_dates) != len(daily_hot_state):
        raise ValueError("daily_dates and daily_hot_state must have equal length")
    _validate_dates(daily_dates)
    percentile = map_pentad_percentile_to_daily(
        daily_dates, pentad_years, pentad_numbers, pentad_percentiles
    )
    hot = np.full(len(daily_hot_state), np.nan, dtype=np.float64)
    for index, value in enumerate(daily_hot_state):
        normalized = _tri_hot_state(value)
        if normalized is not None:
            hot[index] = float(normalized)
    valid = np.isfinite(hot) & np.isfinite(percentile)
    primary = np.full(len(hot), np.nan, dtype=np.float64)
    strict = np.full(len(hot), np.nan, dtype=np.float64)
    primary[valid] = ((hot[valid] == 1.0) & (percentile[valid] < 20.0)).astype(float)
    strict[valid] = ((hot[valid] == 1.0) & (percentile[valid] < 10.0)).astype(float)
    return PentadDailyOverlapStates(percentile, valid, primary, strict)


@dataclass(frozen=True)
class PentadOverlapWindowAggregate:
    window: str
    coverage: float
    valid_days: int
    expected_days: int
    hot_q20_overlap_days: int | None
    hot_q10_overlap_days: int | None


def aggregate_pentad_daily_overlap_window(
    daily_dates: Sequence[date],
    states: PentadDailyOverlapStates,
    *,
    window: str,
    window_start: date,
    window_end: date,
    minimum_coverage: float = 0.9,
) -> PentadOverlapWindowAggregate:
    if window_end < window_start:
        raise ValueError("window_end must not precede window_start")
    if len(daily_dates) != len(states.valid):
        raise ValueError("daily_dates and states must have equal length")
    date_index = {day: index for index, day in enumerate(daily_dates)}
    expected = (window_end - window_start).days + 1
    indices = [
        date_index.get(window_start + timedelta(days=offset)) for offset in range(expected)
    ]
    valid_indices = [index for index in indices if index is not None and states.valid[index]]
    valid_days = len(valid_indices)
    coverage = valid_days / expected
    if not coverage_ok(valid_days, expected, minimum_coverage):
        return PentadOverlapWindowAggregate(window, coverage, valid_days, expected, None, None)
    return PentadOverlapWindowAggregate(
        window,
        coverage,
        valid_days,
        expected,
        int(np.nansum(states.primary_hot_q20[valid_indices])),
        int(np.nansum(states.strict_hot_q10[valid_indices])),
    )


@dataclass(frozen=True)
class HotPentadMetric:
    year: int
    pentad: int
    valid_days: int
    expected_days: int
    coverage: float
    mean_tmax_historical_percentile: float
    hot: bool | None


def compute_hot_pentad_metrics(
    daily_dates: Sequence[date],
    daily_tmax_historical_percentile: Sequence[float | None],
    *,
    minimum_coverage: float = 0.9,
) -> dict[tuple[int, int], HotPentadMetric]:
    """Classify each pentad by mean daily Tmax historical percentile >90."""

    if len(daily_dates) != len(daily_tmax_historical_percentile):
        raise ValueError("Daily dates and temperature percentiles must have equal length")
    _validate_dates(daily_dates)
    grouped: dict[tuple[int, int], list[float | None]] = {}
    for day, raw in zip(daily_dates, daily_tmax_historical_percentile, strict=True):
        pentad = calendar_pentad(day)
        if pentad is None:
            continue
        grouped.setdefault((day.year, pentad), []).append(_finite(raw))
    result: dict[tuple[int, int], HotPentadMetric] = {}
    for (year, pentad), values in sorted(grouped.items()):
        expected = 5
        finite = [value for value in values if value is not None]
        valid_days = len(finite)
        coverage = valid_days / expected
        if len(values) != expected or not coverage_ok(
            valid_days, expected, minimum_coverage
        ):
            mean = math.nan
            hot = None
        else:
            mean = sum(finite) / valid_days
            hot = mean > 90.0
        result[(year, pentad)] = HotPentadMetric(
            year,
            pentad,
            valid_days,
            expected,
            coverage,
            mean,
            hot,
        )
    return result


@dataclass(frozen=True)
class HotFlashDroughtClassification:
    event_id: str
    start_index: int
    end_index: int
    span_pentads: int
    valid_hot_pentads: int
    hot_pentad_count: int
    hot_pentad_coverage: float
    hot_fd_main_any: bool | None
    hot_fd_strict_majority: bool | None


def classify_hot_flash_drought_events(
    events: Sequence[FlashDroughtEvent],
    pentad_years: Sequence[int],
    pentad_numbers: Sequence[int],
    hot_pentad_metrics: Mapping[tuple[int, int], HotPentadMetric],
    *,
    minimum_coverage: float = 0.9,
) -> list[HotFlashDroughtClassification]:
    """Classify each FD using all pentads in its complete support span."""

    if len(pentad_years) != len(pentad_numbers):
        raise ValueError("pentad_years and pentad_numbers must have equal length")
    output: list[HotFlashDroughtClassification] = []
    for event in events:
        if event.start_index < 0 or event.end_index >= len(pentad_years):
            raise IndexError("Flash-drought support falls outside supplied pentad keys")
        flags: list[bool | None] = []
        for index in range(event.start_index, event.end_index + 1):
            metric = hot_pentad_metrics.get(
                (int(pentad_years[index]), int(pentad_numbers[index]))
            )
            flags.append(None if metric is None else metric.hot)
        valid = [flag for flag in flags if flag is not None]
        coverage = len(valid) / len(flags)
        main = classify_hot_flash_drought(
            flags, rule="any", min_valid_fraction=minimum_coverage
        )
        strict = classify_hot_flash_drought(
            flags, rule="majority", min_valid_fraction=minimum_coverage
        )
        output.append(
            HotFlashDroughtClassification(
                event.event_id,
                event.start_index,
                event.end_index,
                event.span_pentads,
                len(valid),
                sum(flag is True for flag in valid),
                coverage,
                main,
                strict,
            )
        )
    return output


def hot_flash_drought_table(
    classifications: Sequence[HotFlashDroughtClassification],
) -> pd.DataFrame:
    return pd.DataFrame([asdict(item) for item in classifications])
