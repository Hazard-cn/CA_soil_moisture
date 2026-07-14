"""Pure functions for the preregistered hot-dry event data contract.

The functions in this module do not read project data or fit yield models.  They
implement the fixed 32 C / 1 mm / three-consecutive-day event rule and the
event-level GLEAM SMrz state, drawdown, and recovery definitions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class HotDryEvent:
    onset_doy: int
    end_doy: int
    duration_days: int
    mean_excess_c: float
    cumulative_excess_cday: float


@dataclass(frozen=True)
class RecoveryResult:
    antecedent_smrz: float | None
    antecedent_valid_days: int
    event_min_smrz: float | None
    drawdown_smrz: float | None
    drawdown_overlap_next_event: bool
    recovery_days: int | None
    recovery_observed: bool | None
    right_censored: bool | None
    censor_reason: str | None


def _as_daily_array(values: Iterable[float]) -> np.ndarray:
    array = np.asarray(list(values), dtype=float)
    if array.ndim != 1:
        raise ValueError("daily inputs must be one-dimensional")
    return array


def identify_hotdry_events(
    tmax_c: Iterable[float],
    precipitation_mm: Iterable[float],
    window_start_doy: int,
    window_end_doy: int,
    *,
    threshold_c: float = 32.0,
    precipitation_cutoff_mm: float = 1.0,
    minimum_duration_days: int = 3,
) -> list[HotDryEvent]:
    """Identify maximal qualifying runs inside an inclusive DOY window.

    Missing temperature or precipitation interrupts a run.  Days outside the
    requested window are never inspected and therefore cannot extend a run at
    either boundary.
    """

    tmax = _as_daily_array(tmax_c)
    precipitation = _as_daily_array(precipitation_mm)
    if tmax.size != precipitation.size:
        raise ValueError("temperature and precipitation must have equal length")
    if minimum_duration_days < 1:
        raise ValueError("minimum_duration_days must be positive")
    if not 1 <= window_start_doy <= window_end_doy <= tmax.size:
        raise ValueError("invalid inclusive DOY window")

    start_index = window_start_doy - 1
    end_index = window_end_doy
    valid = np.isfinite(tmax[start_index:end_index]) & np.isfinite(
        precipitation[start_index:end_index]
    )
    compound = valid & (tmax[start_index:end_index] >= threshold_c) & (
        precipitation[start_index:end_index] < precipitation_cutoff_mm
    )

    events: list[HotDryEvent] = []
    run_start: int | None = None
    for local_index, is_compound in enumerate(compound):
        if bool(is_compound) and run_start is None:
            run_start = local_index
        is_last = local_index == compound.size - 1
        if run_start is not None and ((not bool(is_compound)) or is_last):
            run_stop_exclusive = local_index if not bool(is_compound) else local_index + 1
            duration = run_stop_exclusive - run_start
            if duration >= minimum_duration_days:
                onset = window_start_doy + run_start
                end = onset + duration - 1
                run_tmax = tmax[onset - 1 : end]
                excess = np.maximum(run_tmax - threshold_c, 0.0)
                events.append(
                    HotDryEvent(
                        onset_doy=int(onset),
                        end_doy=int(end),
                        duration_days=int(duration),
                        mean_excess_c=float(np.mean(excess)),
                        cumulative_excess_cday=float(np.sum(excess)),
                    )
                )
            run_start = None
    return events


def aggregate_grid_year_events(
    events: list[HotDryEvent],
    tmax_c: Iterable[float],
    precipitation_mm: Iterable[float],
    window_start_doy: int,
    window_end_doy: int,
    *,
    threshold_c: float = 32.0,
    precipitation_cutoff_mm: float = 1.0,
) -> dict[str, int | float | None]:
    """Create the preregistered grid-year event aggregates."""

    tmax = _as_daily_array(tmax_c)
    precipitation = _as_daily_array(precipitation_mm)
    if tmax.size != precipitation.size:
        raise ValueError("temperature and precipitation must have equal length")
    start = window_start_doy - 1
    stop = window_end_doy
    valid = np.isfinite(tmax[start:stop]) & np.isfinite(precipitation[start:stop])
    heat = valid & (tmax[start:stop] >= threshold_c)
    compound_heat = heat & (precipitation[start:stop] < precipitation_cutoff_mm)
    heat_days = int(heat.sum())

    total_duration = int(sum(event.duration_days for event in events))
    cumulative_excess = float(
        sum(event.cumulative_excess_cday for event in events)
    )
    if total_duration:
        mean_intensity = cumulative_excess / total_duration
    else:
        mean_intensity = 0.0
    return {
        "event_count": len(events),
        "total_duration_days": total_duration,
        "longest_duration_days": max(
            (event.duration_days for event in events), default=0
        ),
        "mean_event_intensity_c": float(mean_intensity),
        "cumulative_excess_cday": cumulative_excess,
        "compound_share_of_heat_days": (
            float(compound_heat.sum() / heat_days) if heat_days else None
        ),
        "valid_weather_days": int(valid.sum()),
        "window_days": int(stop - start),
    }


def calculate_sm_recovery(
    smrz: Iterable[float],
    event: HotDryEvent,
    *,
    ma_doy: int,
    next_event_onset_doy: int | None = None,
    antecedent_days: int = 14,
    recovery_horizon_days: int = 30,
    recovery_fraction: float = 0.90,
) -> RecoveryResult:
    """Calculate antecedent state, drawdown, and recovery/censoring fields.

    `recovery_days` is event time for observed recovery and follow-up time for a
    censored event.  Any missing SM value before an otherwise observable first
    recovery makes that first-recovery time unidentified and is coded
    ``insufficient-sm``.
    """

    values = _as_daily_array(smrz)
    data_end_doy = int(values.size)
    if not 1 <= event.onset_doy <= event.end_doy <= data_end_doy:
        raise ValueError("event lies outside SM calendar")
    if not 1 <= ma_doy <= data_end_doy:
        raise ValueError("ma_doy lies outside SM calendar")

    antecedent_start = max(1, event.onset_doy - antecedent_days)
    antecedent_stop = event.onset_doy - 1
    antecedent_values = values[antecedent_start - 1 : antecedent_stop]
    valid_antecedent = antecedent_values[np.isfinite(antecedent_values)]
    antecedent_valid_days = int(valid_antecedent.size)
    antecedent_smrz = (
        float(np.mean(valid_antecedent)) if antecedent_valid_days else None
    )

    event_min_end = min(event.end_doy + 3, ma_doy, data_end_doy)
    event_values = values[event.onset_doy - 1 : event_min_end]
    valid_event_values = event_values[np.isfinite(event_values)]
    event_min_smrz = (
        float(np.min(valid_event_values)) if valid_event_values.size else None
    )
    drawdown_smrz = (
        float(antecedent_smrz - event_min_smrz)
        if antecedent_smrz is not None and event_min_smrz is not None
        else None
    )
    drawdown_overlap_next_event = bool(
        next_event_onset_doy is not None
        and next_event_onset_doy <= event_min_end
    )

    if antecedent_valid_days != antecedent_days or antecedent_smrz is None:
        return RecoveryResult(
            antecedent_smrz=antecedent_smrz,
            antecedent_valid_days=antecedent_valid_days,
            event_min_smrz=event_min_smrz,
            drawdown_smrz=drawdown_smrz,
            drawdown_overlap_next_event=drawdown_overlap_next_event,
            recovery_days=None,
            recovery_observed=None,
            right_censored=None,
            censor_reason="insufficient-sm",
        )

    target = recovery_fraction * antecedent_smrz
    end_value = values[event.end_doy - 1]
    if not math.isfinite(float(end_value)):
        return RecoveryResult(
            antecedent_smrz=antecedent_smrz,
            antecedent_valid_days=antecedent_valid_days,
            event_min_smrz=event_min_smrz,
            drawdown_smrz=drawdown_smrz,
            drawdown_overlap_next_event=drawdown_overlap_next_event,
            recovery_days=None,
            recovery_observed=None,
            right_censored=None,
            censor_reason="insufficient-sm",
        )
    if float(end_value) >= target:
        return RecoveryResult(
            antecedent_smrz=antecedent_smrz,
            antecedent_valid_days=antecedent_valid_days,
            event_min_smrz=event_min_smrz,
            drawdown_smrz=drawdown_smrz,
            drawdown_overlap_next_event=drawdown_overlap_next_event,
            recovery_days=0,
            recovery_observed=True,
            right_censored=False,
            censor_reason="recovered",
        )

    candidate_limits = {
        "thirty-day-limit": min(event.end_doy + recovery_horizon_days, data_end_doy),
        "ma-end": ma_doy,
        "data-end": data_end_doy,
    }
    if next_event_onset_doy is not None:
        if next_event_onset_doy <= event.end_doy:
            raise ValueError("next event onset must follow the current event")
        candidate_limits["next-event"] = next_event_onset_doy - 1
    follow_end = min(candidate_limits.values())
    reason_priority = ["next-event", "ma-end", "data-end", "thirty-day-limit"]
    limiting_reason = next(
        reason
        for reason in reason_priority
        if reason in candidate_limits and candidate_limits[reason] == follow_end
    )

    follow_start = event.end_doy + 1
    if follow_end >= follow_start:
        follow_values = values[follow_start - 1 : follow_end]
        missing_seen = False
        for offset, value in enumerate(follow_values, start=1):
            if not math.isfinite(float(value)):
                missing_seen = True
                continue
            if float(value) >= target:
                if missing_seen:
                    return RecoveryResult(
                        antecedent_smrz=antecedent_smrz,
                        antecedent_valid_days=antecedent_valid_days,
                        event_min_smrz=event_min_smrz,
                        drawdown_smrz=drawdown_smrz,
                        drawdown_overlap_next_event=drawdown_overlap_next_event,
                        recovery_days=None,
                        recovery_observed=None,
                        right_censored=None,
                        censor_reason="insufficient-sm",
                    )
                return RecoveryResult(
                    antecedent_smrz=antecedent_smrz,
                    antecedent_valid_days=antecedent_valid_days,
                    event_min_smrz=event_min_smrz,
                    drawdown_smrz=drawdown_smrz,
                    drawdown_overlap_next_event=drawdown_overlap_next_event,
                    recovery_days=offset,
                    recovery_observed=True,
                    right_censored=False,
                    censor_reason="recovered",
                )
        if missing_seen:
            return RecoveryResult(
                antecedent_smrz=antecedent_smrz,
                antecedent_valid_days=antecedent_valid_days,
                event_min_smrz=event_min_smrz,
                drawdown_smrz=drawdown_smrz,
                drawdown_overlap_next_event=drawdown_overlap_next_event,
                recovery_days=None,
                recovery_observed=None,
                right_censored=None,
                censor_reason="insufficient-sm",
            )

    return RecoveryResult(
        antecedent_smrz=antecedent_smrz,
        antecedent_valid_days=antecedent_valid_days,
        event_min_smrz=event_min_smrz,
        drawdown_smrz=drawdown_smrz,
        drawdown_overlap_next_event=drawdown_overlap_next_event,
        recovery_days=max(0, follow_end - event.end_doy),
        recovery_observed=False,
        right_censored=True,
        censor_reason=limiting_reason,
    )


def event_as_dict(event: HotDryEvent) -> dict[str, int | float]:
    return asdict(event)
