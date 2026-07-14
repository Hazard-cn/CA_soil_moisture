from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

from hotdry_event_core import (  # noqa: E402
    HotDryEvent,
    aggregate_grid_year_events,
    calculate_sm_recovery,
    identify_hotdry_events,
)


def weather(days: int = 40) -> tuple[np.ndarray, np.ndarray]:
    return np.full(days, 25.0), np.full(days, 5.0)


def set_compound(tmax: np.ndarray, pre: np.ndarray, *days: int) -> None:
    for doy in days:
        tmax[doy - 1] = 34.0
        pre[doy - 1] = 0.5


def test_exactly_three_days_is_one_event() -> None:
    tmax, pre = weather()
    set_compound(tmax, pre, 10, 11, 12)
    events = identify_hotdry_events(tmax, pre, 1, 40)
    assert [(event.onset_doy, event.end_doy) for event in events] == [(10, 12)]


def test_two_days_break_then_three_days() -> None:
    tmax, pre = weather()
    set_compound(tmax, pre, 5, 6, 8, 9, 10)
    events = identify_hotdry_events(tmax, pre, 1, 40)
    assert [(event.onset_doy, event.end_doy) for event in events] == [(8, 10)]


def test_window_boundaries_do_not_complete_outside_runs() -> None:
    tmax, pre = weather()
    set_compound(tmax, pre, 4, 5, 6, 20, 21, 22)
    events = identify_hotdry_events(tmax, pre, 5, 21)
    assert events == []


def test_missing_weather_interrupts_run() -> None:
    tmax, pre = weather()
    set_compound(tmax, pre, 10, 11, 12, 13, 14, 15)
    tmax[11] = np.nan
    events = identify_hotdry_events(tmax, pre, 1, 40)
    assert [(event.onset_doy, event.end_doy) for event in events] == [(13, 15)]


def test_two_events_and_aggregates() -> None:
    tmax, pre = weather()
    set_compound(tmax, pre, 3, 4, 5, 15, 16, 17, 18)
    events = identify_hotdry_events(tmax, pre, 1, 40)
    summary = aggregate_grid_year_events(events, tmax, pre, 1, 40)
    assert [(event.onset_doy, event.end_doy) for event in events] == [(3, 5), (15, 18)]
    assert summary["event_count"] == 2
    assert summary["total_duration_days"] == 7
    assert summary["longest_duration_days"] == 4


def test_no_heat_day_has_null_compound_share() -> None:
    tmax, pre = weather()
    events = identify_hotdry_events(tmax, pre, 1, 40)
    summary = aggregate_grid_year_events(events, tmax, pre, 1, 40)
    assert events == []
    assert summary["compound_share_of_heat_days"] is None


def test_isolated_compound_day_is_not_event() -> None:
    tmax, pre = weather()
    set_compound(tmax, pre, 9)
    assert identify_hotdry_events(tmax, pre, 1, 40) == []


def base_sm(days: int = 100) -> np.ndarray:
    return np.full(days, 0.30)


def event(onset: int = 20, end: int = 22) -> HotDryEvent:
    return HotDryEvent(onset, end, end - onset + 1, 2.0, 2.0 * (end - onset + 1))


def test_complete_antecedent_and_immediate_recovery() -> None:
    sm = base_sm()
    result = calculate_sm_recovery(sm, event(), ma_doy=90)
    assert result.antecedent_valid_days == 14
    assert result.recovery_days == 0
    assert result.censor_reason == "recovered"


def test_missing_antecedent_is_insufficient_sm() -> None:
    sm = base_sm()
    sm[9] = np.nan
    result = calculate_sm_recovery(sm, event(), ma_doy=90)
    assert result.antecedent_valid_days == 13
    assert result.censor_reason == "insufficient-sm"


def test_recovery_within_thirty_days() -> None:
    sm = base_sm()
    sm[19:26] = 0.20
    sm[26] = 0.28
    result = calculate_sm_recovery(sm, event(), ma_doy=90)
    assert result.recovery_days == 5
    assert result.recovery_observed is True


def test_next_event_censoring_excludes_next_onset_day() -> None:
    sm = base_sm()
    sm[19:40] = 0.20
    result = calculate_sm_recovery(
        sm, event(), ma_doy=90, next_event_onset_doy=27
    )
    assert result.recovery_days == 4
    assert result.right_censored is True
    assert result.censor_reason == "next-event"


def test_ma_censoring() -> None:
    sm = base_sm()
    sm[19:40] = 0.20
    result = calculate_sm_recovery(sm, event(), ma_doy=25)
    assert result.recovery_days == 3
    assert result.censor_reason == "ma-end"


def test_drawdown_overlap_with_next_event() -> None:
    sm = base_sm()
    result = calculate_sm_recovery(
        sm, event(), ma_doy=90, next_event_onset_doy=25
    )
    assert result.drawdown_overlap_next_event is True


def test_drawdown_does_not_overlap_later_event() -> None:
    sm = base_sm()
    result = calculate_sm_recovery(
        sm, event(), ma_doy=90, next_event_onset_doy=26
    )
    assert result.drawdown_overlap_next_event is False


def test_thirty_day_limit() -> None:
    sm = base_sm()
    sm[19:60] = 0.20
    result = calculate_sm_recovery(sm, event(), ma_doy=90)
    assert result.recovery_days == 30
    assert result.censor_reason == "thirty-day-limit"


def test_missing_sm_before_first_recovery_is_insufficient() -> None:
    sm = base_sm()
    sm[19:26] = 0.20
    sm[24] = np.nan
    sm[26] = 0.28
    result = calculate_sm_recovery(sm, event(), ma_doy=90)
    assert result.recovery_days is None
    assert result.censor_reason == "insufficient-sm"
