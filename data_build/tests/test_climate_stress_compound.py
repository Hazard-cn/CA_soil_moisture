from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "python"
sys.path.insert(0, str(SCRIPT_DIR))

from climate_stress.compound import (  # noqa: E402
    COMPOUND_VARIANTS,
    aggregate_daily_compound_window,
    aggregate_pentad_daily_overlap_window,
    bridge_daily_compound_event,
    build_pentad_daily_overlap_states,
    classify_hot_flash_drought_events,
    compound_event_table,
    compound_event_window_table,
    compound_valid_state,
    compute_hot_pentad_metrics,
    detect_daily_compound_events,
    detect_daily_compound_events_by_layer,
    hot_flash_drought_table,
    map_pentad_percentile_to_daily,
)
from climate_stress.core import (  # noqa: E402
    FlashDroughtEvent,
    calendar_pentad_dates,
)


def days(start: date, count: int) -> list[date]:
    return [start + timedelta(days=offset) for offset in range(count)]


def _compound_inputs(
    count: int,
) -> tuple[list[float], list[float], list[float], list[float]]:
    return [31.0] * count, [30.0] * count, [0.10] * count, [0.20] * count


def _variant(events, name: str):
    return [event for event in events if event.variant == name]


def _flash_event(start: int, end: int, event_id: str = "fd-1") -> FlashDroughtEvent:
    return FlashDroughtEvent(
        event_id=event_id,
        start_index=start,
        crossing_index=min(start + 1, end),
        end_index=end,
        recovery_index=end + 1,
        onset_pentads=1,
        onset_speed=10.0,
        span_pentads=end - start + 1,
        dry_pentads=1,
        severity=10.0,
        minimum_percentile=15.0,
        right_censored=False,
    )


def test_daily_compound_keeps_heat_and_sm_deficits_in_separate_units() -> None:
    dates = days(date(2019, 7, 1), 5)
    tmax, p90, sm, p10 = _compound_inputs(5)
    events = detect_daily_compound_events(
        dates, tmax, p90, sm, p10, layer="SMrz"
    )
    main = _variant(events, "main_gap0")[0]
    assert main.duration == main.active_duration == main.span_duration == 5
    assert main.heat_excess_cdays == pytest.approx(5.0)
    assert main.sm_deficit_m3m3_days == pytest.approx(0.5)
    table = compound_event_table([main])
    assert "heat_excess_cdays" in table
    assert "sm_deficit_m3m3_days" in table
    assert "severity" not in table


def test_daily_compound_comparisons_are_strict() -> None:
    dates = days(date(2019, 7, 1), 5)
    events = detect_daily_compound_events(
        dates,
        [30.0] * 5,
        [30.0] * 5,
        [0.20] * 5,
        [0.20] * 5,
        layer="SMrz",
    )
    assert events == []


def test_gap_zero_and_gap_two_variants_are_distinct() -> None:
    dates = days(date(2019, 7, 1), 7)
    tmax, p90, sm, p10 = _compound_inputs(7)
    tmax[2:4] = [29.0, 29.0]
    events = detect_daily_compound_events(
        dates, tmax, p90, sm, p10, layer="SMrz"
    )
    assert _variant(events, "main_gap0") == []
    sensitivity = _variant(events, "sensitivity_gap2")[0]
    assert sensitivity.duration == sensitivity.active_duration == 5
    assert sensitivity.span_duration == 7
    assert sensitivity.gap_duration == 2
    assert sensitivity.heat_excess_cdays == pytest.approx(5.0)
    assert sensitivity.sm_deficit_m3m3_days == pytest.approx(0.5)


def test_missing_day_is_a_hard_break_not_a_mergeable_gap() -> None:
    dates = days(date(2019, 7, 1), 6)
    tmax, p90, sm, p10 = _compound_inputs(6)
    sm[2] = np.nan
    events = detect_daily_compound_events(
        dates, tmax, p90, sm, p10, layer="SMrz"
    )
    assert events == []


def test_event_detection_crosses_calendar_year_boundary() -> None:
    dates = days(date(2019, 12, 29), 7)
    tmax, p90, sm, p10 = _compound_inputs(7)
    main = _variant(
        detect_daily_compound_events(dates, tmax, p90, sm, p10, layer="SMrz"),
        "main_gap0",
    )[0]
    assert main.start == date(2019, 12, 29)
    assert main.end == date(2020, 1, 4)
    assert main.duration == 7


def test_daily_compound_event_includes_february_29() -> None:
    dates = days(date(2020, 2, 27), 5)
    assert date(2020, 2, 29) in dates
    tmax, p90, sm, p10 = _compound_inputs(5)
    main = _variant(
        detect_daily_compound_events(dates, tmax, p90, sm, p10, layer="SMrz"),
        "main_gap0",
    )[0]
    assert main.duration == 5
    assert date(2020, 2, 29) in main.run.active_dates


def test_each_sm_layer_gets_independent_events() -> None:
    dates = days(date(2019, 7, 1), 5)
    tmax, p90, smrz, p10 = _compound_inputs(5)
    sms = [0.30] * 5
    events = detect_daily_compound_events_by_layer(
        dates,
        tmax,
        p90,
        {"SMrz": smrz, "SMs": sms},
        {"SMrz": p10, "SMs": p10},
    )
    assert {event.layer for event in events} == {"SMrz"}
    assert {event.variant for event in events} == set(COMPOUND_VARIANTS)


def test_window_bridge_censors_complete_event_and_prorates_both_units() -> None:
    dates = days(date(2019, 7, 1), 7)
    tmax, p90, sm, p10 = _compound_inputs(7)
    event = _variant(
        detect_daily_compound_events(dates, tmax, p90, sm, p10, layer="SMrz"),
        "main_gap0",
    )[0]
    bridge = bridge_daily_compound_event(
        event,
        window="middle",
        window_start=date(2019, 7, 3),
        window_end=date(2019, 7, 5),
    )
    assert bridge is not None
    assert bridge.event_count == 1
    assert bridge.duration == bridge.active_duration == bridge.span_duration == 3
    assert bridge.heat_excess_cdays == pytest.approx(3.0)
    assert bridge.sm_deficit_m3m3_days == pytest.approx(0.3)
    assert bridge.left_censored and bridge.right_censored


def test_pure_gap_window_counts_event_with_zero_active_duration() -> None:
    dates = days(date(2019, 7, 1), 7)
    tmax, p90, sm, p10 = _compound_inputs(7)
    tmax[2:4] = [29.0, 29.0]
    event = _variant(
        detect_daily_compound_events(dates, tmax, p90, sm, p10, layer="SMrz"),
        "sensitivity_gap2",
    )[0]
    bridge = bridge_daily_compound_event(
        event,
        window="gap_only",
        window_start=date(2019, 7, 3),
        window_end=date(2019, 7, 4),
    )
    assert bridge is not None
    assert bridge.event_count == 1
    assert bridge.duration == bridge.active_duration == 0
    assert bridge.span_duration == bridge.gap_duration == 2
    assert bridge.heat_excess_cdays == 0
    assert bridge.sm_deficit_m3m3_days == 0


def test_event_and_window_bridge_tables_keep_complete_and_window_fields() -> None:
    dates = days(date(2019, 7, 1), 5)
    tmax, p90, sm, p10 = _compound_inputs(5)
    main = _variant(
        detect_daily_compound_events(dates, tmax, p90, sm, p10, layer="SMrz"),
        "main_gap0",
    )[0]
    table = compound_event_window_table(
        [main], {"full": (date(2019, 7, 1), date(2019, 7, 5))}
    )
    assert len(table) == 1
    assert table.loc[0, "event_id"] == main.event_id
    assert table.loc[0, "window"] == "full"
    assert table.loc[0, "heat_excess_cdays"] == pytest.approx(5.0)
    assert "severity" not in table.columns


def test_ninety_percent_coverage_gate_returns_na_below_threshold() -> None:
    dates = days(date(2019, 7, 1), 10)
    tmax, p90, sm, p10 = _compound_inputs(10)
    events = detect_daily_compound_events(dates, tmax, p90, sm, p10, layer="SMrz")
    passing = aggregate_daily_compound_window(
        events,
        dates,
        [True] * 9 + [False],
        layer="SMrz",
        variant="main_gap0",
        window="full",
        window_start=dates[0],
        window_end=dates[-1],
    )
    assert passing.coverage == pytest.approx(0.9)
    assert passing.event_count == 1
    failing = aggregate_daily_compound_window(
        events,
        dates,
        [True] * 8 + [False] * 2,
        layer="SMrz",
        variant="main_gap0",
        window="full",
        window_start=dates[0],
        window_end=dates[-1],
    )
    assert failing.coverage == pytest.approx(0.8)
    assert failing.any_event is None
    assert failing.event_count is None
    assert failing.heat_excess_cdays is None
    assert failing.sm_deficit_m3m3_days is None


def test_compound_valid_state_requires_all_four_daily_inputs() -> None:
    valid = compound_valid_state(
        [31, 31, np.nan], [30, 30, 30], [0.1, None, 0.1], [0.2, 0.2, 0.2]
    )
    assert valid.tolist() == [True, False, False]


def test_pentad_percentile_maps_to_five_analysis_days_and_excludes_leap_day() -> None:
    dates = days(date(2020, 2, 25), 6)  # includes Feb 29 and Mar 1
    mapped = map_pentad_percentile_to_daily(dates, [2020], [12], [15.0])
    assert np.isfinite(mapped).sum() == 5
    assert np.isnan(mapped[4])  # Feb 29
    assert mapped[5] == pytest.approx(15.0)  # Mar 1 remains pentad 12


def test_pentad_q20_and_q10_overlap_days_are_separate() -> None:
    dates = days(date(2020, 2, 25), 6)
    states = build_pentad_daily_overlap_states(
        dates,
        [True] * 6,
        [2020],
        [12],
        [15.0],
    )
    short = aggregate_pentad_daily_overlap_window(
        dates,
        states,
        window="pre_leap",
        window_start=date(2020, 2, 25),
        window_end=date(2020, 2, 28),
    )
    assert short.coverage == 1.0
    assert short.hot_q20_overlap_days == 4
    assert short.hot_q10_overlap_days == 0
    leap_window = aggregate_pentad_daily_overlap_window(
        dates,
        states,
        window="with_leap",
        window_start=date(2020, 2, 25),
        window_end=date(2020, 3, 1),
    )
    assert leap_window.coverage == pytest.approx(5 / 6)
    assert leap_window.hot_q20_overlap_days is None
    assert leap_window.hot_q10_overlap_days is None


def test_q_below_ten_implies_both_primary_and_strict_overlap() -> None:
    dates = list(calendar_pentad_dates(2019, 1))
    states = build_pentad_daily_overlap_states(
        dates,
        [True, False, True, False, True],
        [2019],
        [1],
        [5.0],
    )
    result = aggregate_pentad_daily_overlap_window(
        dates,
        states,
        window="p1",
        window_start=dates[0],
        window_end=dates[-1],
    )
    assert result.hot_q20_overlap_days == 3
    assert result.hot_q10_overlap_days == 3


def test_pentad_overlap_accepts_pipeline_int8_hot_state_encoding() -> None:
    dates = list(calendar_pentad_dates(2019, 1))
    states = build_pentad_daily_overlap_states(
        dates,
        np.asarray([1, 0, -1, 1, 0], dtype=np.int8),
        [2019],
        [1],
        [5.0],
    )
    assert states.valid.tolist() == [True, True, False, True, True]
    assert np.nansum(states.strict_hot_q10) == 2
    with pytest.raises(ValueError, match="Daily heat state"):
        build_pentad_daily_overlap_states(
            dates, [2, 0, 0, 0, 0], [2019], [1], [5.0]
        )


def test_hot_pentad_uses_strict_mean_above_ninety_and_five_day_coverage() -> None:
    p1 = list(calendar_pentad_dates(2019, 1))
    p2 = list(calendar_pentad_dates(2019, 2))
    p3 = list(calendar_pentad_dates(2019, 3))
    metrics = compute_hot_pentad_metrics(
        p1 + p2 + p3,
        [90.0] * 5 + [91.0] * 5 + [92.0, 92.0, 92.0, 92.0, None],
    )
    assert metrics[(2019, 1)].hot is False
    assert metrics[(2019, 2)].hot is True
    assert metrics[(2019, 3)].coverage == pytest.approx(0.8)
    assert metrics[(2019, 3)].hot is None


def test_hot_flash_drought_any_and_strict_majority_use_complete_support() -> None:
    dates = []
    percentiles = []
    for pentad, value in ((1, 80.0), (2, 95.0), (3, 80.0)):
        dates.extend(calendar_pentad_dates(2019, pentad))
        percentiles.extend([value] * 5)
    metrics = compute_hot_pentad_metrics(dates, percentiles)
    classification = classify_hot_flash_drought_events(
        [_flash_event(0, 2)],
        [2019, 2019, 2019],
        [1, 2, 3],
        metrics,
    )[0]
    assert classification.hot_pentad_coverage == 1.0
    assert classification.valid_hot_pentads == 3
    assert classification.hot_pentad_count == 1
    assert classification.hot_fd_main_any is True
    assert classification.hot_fd_strict_majority is False


def test_hot_flash_strict_majority_excludes_exact_half() -> None:
    dates = []
    percentiles = []
    for pentad, value in ((1, 95.0), (2, 95.0), (3, 80.0), (4, 80.0)):
        dates.extend(calendar_pentad_dates(2019, pentad))
        percentiles.extend([value] * 5)
    metrics = compute_hot_pentad_metrics(dates, percentiles)
    half = classify_hot_flash_drought_events(
        [_flash_event(0, 3)], [2019] * 4, [1, 2, 3, 4], metrics
    )[0]
    assert half.hot_fd_main_any is True
    assert half.hot_fd_strict_majority is False


def test_hot_flash_drought_coverage_below_ninety_returns_na() -> None:
    dates = []
    percentiles = []
    for pentad, values in (
        (1, [95.0] * 5),
        (2, [95.0] * 4 + [None]),
        (3, [80.0] * 5),
    ):
        dates.extend(calendar_pentad_dates(2019, pentad))
        percentiles.extend(values)
    metrics = compute_hot_pentad_metrics(dates, percentiles)
    classification = classify_hot_flash_drought_events(
        [_flash_event(0, 2)], [2019] * 3, [1, 2, 3], metrics
    )[0]
    assert classification.hot_pentad_coverage == pytest.approx(2 / 3)
    assert classification.hot_fd_main_any is None
    assert classification.hot_fd_strict_majority is None


def test_hot_flash_drought_support_can_cross_years() -> None:
    keys = [(2019, 73), (2020, 1), (2020, 2)]
    dates = []
    percentiles = []
    for year, pentad in keys:
        dates.extend(calendar_pentad_dates(year, pentad))
        percentiles.extend(([95.0] if (year, pentad) == (2020, 1) else [80.0]) * 5)
    metrics = compute_hot_pentad_metrics(dates, percentiles)
    classification = classify_hot_flash_drought_events(
        [_flash_event(0, 2, "fd-cross-year")],
        [key[0] for key in keys],
        [key[1] for key in keys],
        metrics,
    )[0]
    assert classification.event_id == "fd-cross-year"
    assert classification.hot_fd_main_any is True
    assert classification.hot_fd_strict_majority is False
    table = hot_flash_drought_table([classification])
    assert len(table) == 1
    assert table.loc[0, "hot_pentad_coverage"] == 1.0
