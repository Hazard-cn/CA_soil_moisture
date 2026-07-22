"""Pure algorithms for the climate-stress panel pipeline.

This module intentionally contains no file-system or product-specific I/O.  The
pipeline adapters are responsible for translating source metadata into the
explicit dates, support intervals, masks, and values accepted here.
"""

from __future__ import annotations

import calendar
import math
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, Mapping, Sequence


Number = int | float
TriState = bool | None
SPEI_2W_PENDING_STATUS = "SKIPPED_PENDING_ENDPOINT_DECISION"


def _finite_float(value: Number | None) -> float | None:
    if value is None:
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def _validate_dates(dates: Sequence[date]) -> None:
    if any(current <= previous for previous, current in zip(dates, dates[1:])):
        raise ValueError("Dates must be unique and strictly increasing")


def required_valid_count(expected: int, threshold: float = 0.9) -> int:
    """Return the smallest integer count satisfying a coverage threshold."""

    if expected <= 0:
        raise ValueError("expected must be positive")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must lie in [0, 1]")
    return math.ceil(expected * threshold - 1e-12)


def coverage_ok(valid: int, expected: int, threshold: float = 0.9) -> bool:
    """Return whether an observed count meets the frozen coverage rule."""

    if valid < 0 or valid > expected:
        raise ValueError("valid must lie between zero and expected")
    return valid >= required_valid_count(expected, threshold)


@dataclass(frozen=True)
class EventSegment:
    """A non-overlapping event-support interval with additive severity."""

    start: date
    end_exclusive: date
    active: bool
    severity: float = 0.0

    def __post_init__(self) -> None:
        if self.end_exclusive <= self.start:
            raise ValueError("Event segment must have positive duration")
        if not math.isfinite(self.severity) or self.severity < 0:
            raise ValueError("Segment severity must be finite and non-negative")
        if not self.active and self.severity != 0:
            raise ValueError("Inactive support cannot carry severity")

    @property
    def days(self) -> int:
        return (self.end_exclusive - self.start).days


def _validate_segments(segments: Sequence[EventSegment]) -> None:
    if not segments:
        raise ValueError("At least one event segment is required")
    for previous, current in zip(segments, segments[1:]):
        if current.start < previous.end_exclusive:
            raise ValueError("Event segments must be sorted and non-overlapping")


@dataclass(frozen=True)
class RunEvent:
    """A daily threshold event, including any explicitly permitted gaps."""

    event_id: str
    active_indices: tuple[int, ...]
    segments: tuple[EventSegment, ...]

    def __post_init__(self) -> None:
        if not self.active_indices:
            raise ValueError("Run event must contain at least one active index")
        _validate_segments(self.segments)

    @property
    def start(self) -> date:
        return self.segments[0].start

    @property
    def end(self) -> date:
        return self.segments[-1].end_exclusive - timedelta(days=1)

    @property
    def active_duration(self) -> int:
        return sum(segment.days for segment in self.segments if segment.active)

    @property
    def duration(self) -> int:
        """Canonical duration: active exposure days, excluding allowed gaps."""

        return self.active_duration

    @property
    def span_duration(self) -> int:
        return sum(segment.days for segment in self.segments)

    @property
    def gap_duration(self) -> int:
        return self.span_duration - self.active_duration

    @property
    def severity(self) -> float:
        return sum(segment.severity for segment in self.segments)

    @property
    def peak_intensity(self) -> float:
        return max(segment.severity / segment.days for segment in self.segments if segment.active)

    @property
    def mean_intensity(self) -> float:
        return self.severity / self.active_duration

    @property
    def active_dates(self) -> tuple[date, ...]:
        return tuple(segment.start for segment in self.segments if segment.active)

    @property
    def support_dates(self) -> tuple[date, ...]:
        return tuple(segment.start for segment in self.segments)


def build_runs(
    dates: Sequence[date],
    mask: Sequence[TriState],
    *,
    min_active: int,
    max_gap: int = 0,
    intensity: Sequence[Number | None] | None = None,
    event_id_prefix: str = "run",
) -> list[RunEvent]:
    """Detect daily three-state runs, optionally merging observed false gaps.

    ``None`` mask values and missing calendar dates are hard boundaries.  Runs
    are merged only when every intervening observation is an explicit ``False``
    and the number of such observations does not exceed ``max_gap``.  Minimum
    duration is evaluated after merging and counts active days only.
    """

    if len(dates) != len(mask):
        raise ValueError("dates and mask must have the same length")
    if intensity is not None and len(intensity) != len(mask):
        raise ValueError("intensity and mask must have the same length")
    if min_active <= 0 or max_gap < 0:
        raise ValueError("min_active must be positive and max_gap non-negative")
    _validate_dates(dates)
    for value in mask:
        if value is not None and not isinstance(value, bool):
            raise TypeError("mask values must be bool or None")

    primitive: list[list[int]] = []
    current: list[int] = []
    for index, state in enumerate(mask):
        consecutive = index == 0 or dates[index] == dates[index - 1] + timedelta(days=1)
        if state is True:
            if current and not consecutive:
                primitive.append(current)
                current = []
            current.append(index)
        else:
            if current:
                primitive.append(current)
                current = []
    if current:
        primitive.append(current)

    merged: list[list[int]] = []
    for run in primitive:
        if not merged:
            merged.append(run)
            continue
        previous = merged[-1]
        gap_indices = list(range(previous[-1] + 1, run[0]))
        calendar_contiguous = all(
            dates[index] == dates[index - 1] + timedelta(days=1)
            for index in range(previous[-1] + 1, run[0] + 1)
        )
        mergeable = (
            len(gap_indices) <= max_gap
            and all(mask[index] is False for index in gap_indices)
            and calendar_contiguous
        )
        if mergeable:
            merged[-1] = previous + run
        else:
            merged.append(run)

    events: list[RunEvent] = []
    for active_indices in merged:
        if len(active_indices) < min_active:
            continue
        active_set = set(active_indices)
        start_index, end_index = active_indices[0], active_indices[-1]
        segments: list[EventSegment] = []
        for index in range(start_index, end_index + 1):
            active = index in active_set
            if active:
                raw_intensity = 1.0 if intensity is None else _finite_float(intensity[index])
                if raw_intensity is None or raw_intensity < 0:
                    raise ValueError("Active intensity must be finite and non-negative")
                severity = raw_intensity
            else:
                severity = 0.0
            segments.append(
                EventSegment(
                    start=dates[index],
                    end_exclusive=dates[index] + timedelta(days=1),
                    active=active,
                    severity=severity,
                )
            )
        events.append(
            RunEvent(
                event_id=f"{event_id_prefix}-{len(events) + 1:06d}",
                active_indices=tuple(active_indices),
                segments=tuple(segments),
            )
        )
    return events


def detect_heatwaves(
    dates: Sequence[date],
    tmax: Sequence[Number | None],
    p90: Sequence[Number | None],
    *,
    min_active: int = 3,
) -> list[RunEvent]:
    """Detect strict Tmax>P90 heatwaves; missing values break events."""

    if len(tmax) != len(p90) or len(dates) != len(tmax):
        raise ValueError("dates, tmax, and p90 must have the same length")
    mask: list[TriState] = []
    intensity: list[float | None] = []
    for raw_value, raw_threshold in zip(tmax, p90):
        value = _finite_float(raw_value)
        threshold = _finite_float(raw_threshold)
        if value is None or threshold is None:
            mask.append(None)
            intensity.append(None)
        else:
            is_hot = value > threshold
            mask.append(is_hot)
            intensity.append(value - threshold if is_hot else 0.0)
    return build_runs(
        dates,
        mask,
        min_active=min_active,
        max_gap=0,
        intensity=intensity,
        event_id_prefix="heatwave",
    )


@dataclass(frozen=True)
class SpeiRecord:
    support_start: date
    support_end_exclusive: date
    value: float | None
    label: str = ""

    def __post_init__(self) -> None:
        if self.support_end_exclusive <= self.support_start:
            raise ValueError("SPEI support interval must have positive duration")

    @classmethod
    def month(cls, year: int, month: int, value: Number | None) -> "SpeiRecord":
        start = date(year, month, 1)
        end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
        return cls(start, end, _finite_float(value), f"{year:04d}-{month:02d}")

    @property
    def days(self) -> int:
        return (self.support_end_exclusive - self.support_start).days


@dataclass(frozen=True)
class SpeiEvent:
    event_id: str
    threshold: float
    records: tuple[SpeiRecord, ...]
    segments: tuple[EventSegment, ...]

    @property
    def start(self) -> date:
        return self.records[0].support_start

    @property
    def end(self) -> date:
        return self.records[-1].support_end_exclusive - timedelta(days=1)

    @property
    def period_count(self) -> int:
        return len(self.records)

    @property
    def duration_days(self) -> int:
        return sum(record.days for record in self.records)

    @property
    def duration(self) -> int:
        return self.duration_days

    @property
    def severity(self) -> float:
        """Threshold-deficit sum in native SPEI reporting-period units."""

        return sum(segment.severity for segment in self.segments)

    @property
    def min_spei(self) -> float:
        return min(float(record.value) for record in self.records if record.value is not None)

    @property
    def peak_threshold_deficit(self) -> float:
        return max(self.threshold - self.min_spei, 0.0)

    @property
    def mean_intensity(self) -> float:
        """Mean threshold deficit per native SPEI reporting period."""

        return self.severity / self.period_count


def detect_spei_runs(
    records: Sequence[SpeiRecord],
    *,
    threshold: float,
    min_periods: int,
    event_id_prefix: str = "spei",
) -> list[SpeiEvent]:
    """Detect strict below-threshold runs on adjacent SPEI support periods."""

    if min_periods <= 0:
        raise ValueError("min_periods must be positive")
    previous: SpeiRecord | None = None
    for record in records:
        if previous is not None and record.support_start < previous.support_end_exclusive:
            raise ValueError("SPEI records must be sorted and non-overlapping")
        previous = record

    groups: list[list[SpeiRecord]] = []
    current: list[SpeiRecord] = []
    for record in records:
        value = _finite_float(record.value)
        active = value is not None and value < threshold
        adjacent = not current or record.support_start == current[-1].support_end_exclusive
        if active:
            if current and not adjacent:
                groups.append(current)
                current = []
            current.append(record)
        elif current:
            groups.append(current)
            current = []
    if current:
        groups.append(current)

    events: list[SpeiEvent] = []
    for group in groups:
        if len(group) < min_periods:
            continue
        segments = tuple(
            EventSegment(
                record.support_start,
                record.support_end_exclusive,
                True,
                threshold - float(record.value),
            )
            for record in group
        )
        events.append(
            SpeiEvent(
                event_id=f"{event_id_prefix}-{len(events) + 1:06d}",
                threshold=float(threshold),
                records=tuple(group),
                segments=segments,
            )
        )
    return events


def reporting_intervals(
    timestamps: Sequence[date],
    *,
    state_days: int,
    timestamp_position: str,
) -> tuple[tuple[date, date], ...]:
    """Convert product timestamps to explicitly configured state intervals.

    This helper makes no claim about a product's time metadata.  Callers must
    select ``timestamp_position='start'`` or ``'end'`` after inspecting that
    metadata.  End timestamps are treated as inclusive calendar dates.
    """

    if state_days <= 0:
        raise ValueError("state_days must be positive")
    _validate_dates(timestamps)
    if timestamp_position == "start":
        return tuple((stamp, stamp + timedelta(days=state_days)) for stamp in timestamps)
    if timestamp_position == "end":
        return tuple(
            (stamp - timedelta(days=state_days - 1), stamp + timedelta(days=1))
            for stamp in timestamps
        )
    raise ValueError("timestamp_position must be 'start' or 'end'")


@dataclass(frozen=True)
class Spei2WIntervalContract:
    """One CHM 2W release with separate accumulation and state intervals.

    The accumulation interval describes the value encoded by the product.
    The state interval is the non-overlapping interval used for run detection
    and phenology-window intersection.  Keeping both intervals prevents the
    overlapping 14-day accumulations from being counted as overlapping event
    duration.
    """

    label_date: date
    accumulation_start: date
    accumulation_end_exclusive: date
    state_start: date
    state_end_exclusive: date

    def __post_init__(self) -> None:
        if self.accumulation_end_exclusive <= self.accumulation_start:
            raise ValueError("SPEI-2W accumulation support must have positive duration")
        if self.state_end_exclusive <= self.state_start:
            raise ValueError("SPEI-2W state support must have positive duration")


def spei_2w_interval_contracts(
    timestamps: Sequence[date],
    *,
    accumulation_days: int,
    state_days: int,
    accumulation_timestamp_position: str,
    state_timestamp_position: str,
) -> tuple[Spei2WIntervalContract, ...]:
    """Build the explicit CHM 2W accumulation/state mapping.

    This is a development-candidate mapping only: an inclusive trailing
    14-day accumulation ending on the label date and a forward seven-day state
    beginning on that label date.  It must remain disabled until the endpoint
    decision is confirmed; confirmation atomically updates scope, config, and
    audit evidence.  Observed releases follow a ``state_days`` cadence.
    Missing releases are represented by a gap between state intervals;
    duplicate, out-of-order, off-cadence, or overlapping labels fail closed.
    """

    if accumulation_timestamp_position != "end":
        raise ValueError("SPEI-2W accumulation labels must be interval endpoints")
    if state_timestamp_position != "start":
        raise ValueError("SPEI-2W state labels must be interval starts")
    _validate_dates(timestamps)
    gaps = [
        (current - previous).days
        for previous, current in zip(timestamps, timestamps[1:])
    ]
    if any(gap < int(state_days) or gap % int(state_days) != 0 for gap in gaps):
        raise ValueError(
            "SPEI-2W labels must be non-overlapping multiples of state_days apart"
        )
    accumulation = reporting_intervals(
        timestamps,
        state_days=int(accumulation_days),
        timestamp_position="end",
    )
    states = reporting_intervals(
        timestamps,
        state_days=int(state_days),
        timestamp_position="start",
    )
    contracts = tuple(
        Spei2WIntervalContract(
            label_date=stamp,
            accumulation_start=accumulation_interval[0],
            accumulation_end_exclusive=accumulation_interval[1],
            state_start=state_interval[0],
            state_end_exclusive=state_interval[1],
        )
        for stamp, accumulation_interval, state_interval in zip(
            timestamps, accumulation, states, strict=True
        )
    )
    if any(
        current.state_start < previous.state_end_exclusive
        for previous, current in zip(contracts, contracts[1:])
    ):
        raise AssertionError("SPEI-2W state intervals must not overlap")
    return contracts


def spei_2w_records(
    timestamps: Sequence[date],
    values: Sequence[Number | None],
    *,
    accumulation_days: int,
    state_days: int,
    accumulation_timestamp_position: str,
    state_timestamp_position: str,
) -> tuple[SpeiRecord, ...]:
    """Create non-overlapping 2W event-state records from explicit semantics."""

    if len(timestamps) != len(values):
        raise ValueError("timestamps and values must have the same length")
    contracts = spei_2w_interval_contracts(
        timestamps,
        accumulation_days=accumulation_days,
        state_days=state_days,
        accumulation_timestamp_position=accumulation_timestamp_position,
        state_timestamp_position=state_timestamp_position,
    )
    return tuple(
        SpeiRecord(
            contract.state_start,
            contract.state_end_exclusive,
            _finite_float(value),
            contract.label_date.isoformat(),
        )
        for contract, value in zip(contracts, values, strict=True)
    )


def climatological_day(value: date) -> int | None:
    """Return a 365-day climatological ordinal, excluding February 29."""

    if value.month == 2 and value.day == 29:
        return None
    ordinal = value.timetuple().tm_yday
    if calendar.isleap(value.year) and value > date(value.year, 2, 29):
        ordinal -= 1
    return ordinal


def calendar_pentad(value: date) -> int | None:
    """Map a date to one of 73 fixed five-day climatological pentads."""

    ordinal = climatological_day(value)
    return None if ordinal is None else (ordinal - 1) // 5 + 1


def calendar_pentad_dates(year: int, pentad: int) -> tuple[date, ...]:
    """Return the five actual dates in a fixed climatological pentad."""

    if not 1 <= pentad <= 73:
        raise ValueError("pentad must lie in 1..73")
    count = 366 if calendar.isleap(year) else 365
    dates = tuple(
        day
        for offset in range(count)
        if (day := date(year, 1, 1) + timedelta(days=offset))
        and calendar_pentad(day) == pentad
    )
    if len(dates) != 5:
        raise AssertionError("Every fixed climatological pentad must contain five dates")
    return dates


def pentad_mean(
    values: Sequence[Number | None],
    *,
    expected_days: int = 5,
    coverage_threshold: float = 0.9,
) -> float | None:
    """Compute a pentad mean only when the frozen coverage rule is met."""

    if len(values) != expected_days:
        raise ValueError("values must include one slot per expected pentad day")
    finite = [value for raw in values if (value := _finite_float(raw)) is not None]
    if not coverage_ok(len(finite), expected_days, coverage_threshold):
        return None
    return sum(finite) / len(finite)


def type7_quantile(
    values: Iterable[Number | None],
    probability: float,
    *,
    min_count: int = 1,
) -> float | None:
    """R Type 7 / NumPy linear empirical quantile."""

    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must lie in [0, 1]")
    if min_count <= 0:
        raise ValueError("min_count must be positive")
    clean = sorted(value for raw in values if (value := _finite_float(raw)) is not None)
    if len(clean) < min_count:
        return None
    if len(clean) == 1:
        return clean[0]
    position = (len(clean) - 1) * probability
    lower = math.floor(position)
    fraction = position - lower
    if fraction == 0:
        return clean[lower]
    return clean[lower] + fraction * (clean[lower + 1] - clean[lower])


def midrank_percentile(
    value: Number | None,
    historical_values: Iterable[Number | None],
    *,
    min_count: int = 1,
) -> float | None:
    """Return 100*(n_less + 0.5*n_equal)/n against the frozen history."""

    target = _finite_float(value)
    historical = [
        item for raw in historical_values if (item := _finite_float(raw)) is not None
    ]
    if target is None or len(historical) < min_count:
        return None
    less = sum(item < target for item in historical)
    equal = sum(item == target for item in historical)
    return 100.0 * (less + 0.5 * equal) / len(historical)


@dataclass(frozen=True)
class PentadPercentileMetrics:
    historical_count: int
    q10_threshold: float | None
    q20_threshold: float | None
    percentile_rank: float | None
    below_q10: bool | None
    below_q20: bool | None


def pentad_percentile_metrics(
    value: Number | None,
    historical_values: Iterable[Number | None],
    *,
    min_historical_count: int = 27,
) -> PentadPercentileMetrics:
    """Compute frozen-history GLEAM pentad thresholds, rank, and states."""

    current = _finite_float(value)
    historical = tuple(
        item for raw in historical_values if (item := _finite_float(raw)) is not None
    )
    q10 = type7_quantile(historical, 0.10, min_count=min_historical_count)
    q20 = type7_quantile(historical, 0.20, min_count=min_historical_count)
    rank = midrank_percentile(current, historical, min_count=min_historical_count)
    valid = current is not None and q10 is not None and q20 is not None
    return PentadPercentileMetrics(
        historical_count=len(historical),
        q10_threshold=q10,
        q20_threshold=q20,
        percentile_rank=rank,
        below_q10=(current < q10) if valid else None,
        below_q20=(current < q20) if valid else None,
    )


def bilinear_weights(x_fraction: float, y_fraction: float) -> tuple[float, ...]:
    """Return weights ordered SW, SE, NW, NE for unit-square fractions."""

    if not 0.0 <= x_fraction <= 1.0 or not 0.0 <= y_fraction <= 1.0:
        raise ValueError("Bilinear fractions must lie in [0, 1]")
    return (
        (1.0 - x_fraction) * (1.0 - y_fraction),
        x_fraction * (1.0 - y_fraction),
        (1.0 - x_fraction) * y_fraction,
        x_fraction * y_fraction,
    )


def bilinear_renormalized(
    values: Sequence[Number | None],
    weights: Sequence[Number],
    *,
    min_valid_neighbors: int = 2,
) -> float | None:
    """Bilinearly interpolate after renormalizing over valid neighbours."""

    if len(values) != 4 or len(weights) != 4:
        raise ValueError("Exactly four neighbour values and weights are required")
    if not 1 <= min_valid_neighbors <= 4:
        raise ValueError("min_valid_neighbors must lie in 1..4")
    numeric_weights = [float(weight) for weight in weights]
    if any(not math.isfinite(weight) or weight < 0 for weight in numeric_weights):
        raise ValueError("Weights must be finite and non-negative")
    valid = [
        (value, weight)
        for raw, weight in zip(values, numeric_weights)
        if (value := _finite_float(raw)) is not None and weight > 0
    ]
    if len(valid) < min_valid_neighbors:
        return None
    denominator = sum(weight for _, weight in valid)
    if denominator <= 0:
        return None
    return sum(value * weight for value, weight in valid) / denominator


@dataclass(frozen=True)
class FlashDroughtEvent:
    event_id: str
    start_index: int
    crossing_index: int
    end_index: int
    recovery_index: int | None
    onset_pentads: int
    onset_speed: float
    span_pentads: int
    dry_pentads: int
    severity: float
    minimum_percentile: float
    right_censored: bool

    @property
    def duration(self) -> int:
        """Flash-drought duration is the complete event span in pentads."""

        return self.span_pentads


def _first_confirmed_recovery(
    values: Sequence[float], crossing: int, confirmation: int
) -> int | None:
    for index in range(crossing + 1, len(values) - confirmation + 1):
        if all(values[position] >= 20.0 for position in range(index, index + confirmation)):
            return index
    return None


def _detect_flash_drought_segment(
    values: Sequence[float],
    *,
    offset: int,
    min_span_pentads: int,
    recovery_confirm: int,
    event_number_start: int,
) -> list[FlashDroughtEvent]:
    events: list[FlashDroughtEvent] = []
    cursor = 1
    candidate_floor = 0
    while cursor < len(values):
        crossing = next(
            (
                index
                for index in range(cursor, len(values))
                if values[index] < 20.0 and values[index - 1] >= 20.0
            ),
            None,
        )
        if crossing is None:
            break
        candidates = [
            index
            for index in range(max(candidate_floor, crossing - 5), crossing)
            if values[index] > 40.0
        ]
        if not candidates:
            cursor = crossing + 1
            continue
        start = max(candidates)
        onset_pentads = crossing - start
        onset_speed = (values[start] - values[crossing]) / onset_pentads
        if onset_speed < 5.0:
            cursor = crossing + 1
            continue

        recovery = _first_confirmed_recovery(values, crossing, recovery_confirm)
        end = len(values) - 1 if recovery is None else recovery - 1
        span = end - start + 1
        if span >= min_span_pentads:
            support = values[start : end + 1]
            events.append(
                FlashDroughtEvent(
                    event_id=f"flash-drought-{event_number_start + len(events):06d}",
                    start_index=offset + start,
                    crossing_index=offset + crossing,
                    end_index=offset + end,
                    recovery_index=None if recovery is None else offset + recovery,
                    onset_pentads=onset_pentads,
                    onset_speed=onset_speed,
                    span_pentads=span,
                    dry_pentads=sum(value < 20.0 for value in values[crossing : end + 1]),
                    severity=5.0 * sum(max(40.0 - value, 0.0) for value in support),
                    minimum_percentile=min(support),
                    right_censored=recovery is None,
                )
            )
        if recovery is None:
            break
        # A confirmed recovery closes the preceding onset support.  A later
        # event must establish a new q>40 start after the full recovery run;
        # otherwise the old start can be reused and produce overlapping
        # duration, severity, and event counts.
        candidate_floor = recovery + recovery_confirm
        cursor = recovery + recovery_confirm
    return events


def detect_flash_droughts(
    percentiles: Sequence[Number | None],
    *,
    min_span_pentads: int,
    recovery_confirm: int,
) -> list[FlashDroughtEvent]:
    """Detect flash droughts using the frozen complete-span duration rule.

    The start is the most recent q>40 pentad within five transitions of the
    first q<20 crossing.  The average onset speed must be at least five
    percentile points per pentad.  Missing values split independent segments.
    """

    if min_span_pentads <= 0:
        raise ValueError("min_span_pentads must be positive")
    if recovery_confirm not in (1, 2):
        raise ValueError("recovery_confirm must be one or two pentads")

    events: list[FlashDroughtEvent] = []
    segment_start = 0
    while segment_start < len(percentiles):
        while (
            segment_start < len(percentiles)
            and _finite_float(percentiles[segment_start]) is None
        ):
            segment_start += 1
        if segment_start >= len(percentiles):
            break
        segment_end = segment_start
        values: list[float] = []
        while segment_end < len(percentiles):
            value = _finite_float(percentiles[segment_end])
            if value is None:
                break
            if not 0.0 <= value <= 100.0:
                raise ValueError("Soil-moisture percentiles must lie in [0, 100]")
            values.append(value)
            segment_end += 1
        events.extend(
            _detect_flash_drought_segment(
                values,
                offset=segment_start,
                min_span_pentads=min_span_pentads,
                recovery_confirm=recovery_confirm,
                event_number_start=len(events) + 1,
            )
        )
        segment_start = segment_end + 1
    return events


def classify_hot_flash_drought(
    hot_pentads: Sequence[TriState],
    *,
    rule: str,
    min_valid_fraction: float = 0.9,
) -> bool | None:
    """Classify a flash drought by any-hot or strict-majority-hot pentads."""

    for value in hot_pentads:
        if value is not None and not isinstance(value, bool):
            raise TypeError("hot_pentads must contain bool or None")
    valid = [value for value in hot_pentads if value is not None]
    if not hot_pentads or not coverage_ok(
        len(valid), len(hot_pentads), min_valid_fraction
    ):
        return None
    if rule == "any":
        return any(valid)
    if rule == "majority":
        return sum(valid) / len(valid) > 0.5
    raise ValueError("rule must be 'any' or 'majority'")


@dataclass(frozen=True)
class EventWindowResult:
    event_id: str
    event_count: int
    duration: int
    active_duration: int
    span_duration: int
    gap_duration: int
    severity: float
    left_censored: bool
    right_censored: bool


def _interval_overlap_days(
    left_start: date,
    left_end: date,
    right_start: date,
    right_end: date,
) -> int:
    return max((min(left_end, right_end) - max(left_start, right_start)).days, 0)


def event_window_bridge(
    event_id: str,
    segments: Sequence[EventSegment],
    *,
    window_start: date,
    window_end: date,
) -> EventWindowResult | None:
    """Intersect a complete event with a closed window.

    The frozen counting rule is support-based: overlap with an internal allowed
    gap still contributes one event, while canonical duration remains zero when
    no active exposure unit overlaps.
    """

    if window_end < window_start:
        raise ValueError("window_end must not precede window_start")
    _validate_segments(segments)
    window_end_exclusive = window_end + timedelta(days=1)
    support_days = 0
    active_days = 0
    severity = 0.0
    for segment in segments:
        overlap = _interval_overlap_days(
            segment.start,
            segment.end_exclusive,
            window_start,
            window_end_exclusive,
        )
        if overlap == 0:
            continue
        support_days += overlap
        if segment.active:
            active_days += overlap
            severity += segment.severity * overlap / segment.days
    if support_days == 0:
        return None
    gap_days = support_days - active_days
    return EventWindowResult(
        event_id=event_id,
        event_count=1,
        duration=active_days,
        active_duration=active_days,
        span_duration=support_days,
        gap_duration=gap_days,
        severity=severity,
        left_censored=segments[0].start < window_start,
        right_censored=segments[-1].end_exclusive > window_end_exclusive,
    )


def event_window_bridge_for_run(
    event: RunEvent,
    *,
    window_start: date,
    window_end: date,
) -> EventWindowResult | None:
    return event_window_bridge(
        event.event_id,
        event.segments,
        window_start=window_start,
        window_end=window_end,
    )


def event_window_bridge_for_spei(
    event: SpeiEvent,
    *,
    window_start: date,
    window_end: date,
) -> EventWindowResult | None:
    return event_window_bridge(
        event.event_id,
        event.segments,
        window_start=window_start,
        window_end=window_end,
    )
