from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "python"
sys.path.insert(0, str(SCRIPT_DIR))

from climate_stress.core import (  # noqa: E402
    EventSegment,
    SpeiRecord,
    bilinear_renormalized,
    bilinear_weights,
    build_runs,
    calendar_pentad,
    calendar_pentad_dates,
    classify_hot_flash_drought,
    coverage_ok,
    detect_flash_droughts,
    detect_heatwaves,
    detect_spei_runs,
    event_window_bridge,
    event_window_bridge_for_run,
    event_window_bridge_for_spei,
    midrank_percentile,
    pentad_mean,
    pentad_percentile_metrics,
    reporting_intervals,
    required_valid_count,
    spei_2w_interval_contracts,
    spei_2w_records,
    type7_quantile,
)


def days(start: date, count: int) -> list[date]:
    return [start + timedelta(days=offset) for offset in range(count)]


def test_heatwave_threshold_is_strict_and_minimum_is_three() -> None:
    dates = days(date(2019, 7, 1), 5)
    assert detect_heatwaves(dates, [30, 31, 31, 30, 31], [30] * 5) == []


def test_heatwave_intensity_and_duration() -> None:
    event = detect_heatwaves(
        days(date(2019, 7, 1), 3), [31, 32, 33], [30, 30, 30]
    )[0]
    assert event.duration == event.active_duration == event.span_duration == 3
    assert event.gap_duration == 0
    assert event.severity == pytest.approx(6.0)
    assert event.peak_intensity == pytest.approx(3.0)
    assert event.mean_intensity == pytest.approx(2.0)


def test_heatwave_missing_and_calendar_holes_are_hard_boundaries() -> None:
    start = date(2019, 7, 1)
    assert detect_heatwaves(days(start, 5), [31, 31, None, 31, 31], [30] * 5) == []
    dates = [start, start + timedelta(days=1), *days(start + timedelta(days=3), 3)]
    events = detect_heatwaves(dates, [31] * 5, [30] * 5)
    assert len(events) == 1
    assert events[0].start == start + timedelta(days=3)


def test_gap_two_merges_and_stores_all_duration_definitions() -> None:
    event = build_runs(
        days(date(2019, 1, 1), 7),
        [True, True, False, False, True, True, True],
        min_active=5,
        max_gap=2,
    )[0]
    assert event.duration == event.active_duration == 5
    assert event.span_duration == 7
    assert event.gap_duration == 2


def test_gap_zero_or_one_does_not_merge_two_day_gap() -> None:
    mask = [True, True, False, False, True, True, True]
    dates = days(date(2019, 1, 1), len(mask))
    assert build_runs(dates, mask, min_active=5, max_gap=0) == []
    assert build_runs(dates, mask, min_active=5, max_gap=1) == []


def test_missing_cannot_be_gap_and_trailing_false_days_are_trimmed() -> None:
    start = date(2019, 1, 1)
    assert build_runs(
        days(start, 6), [True, True, None, True, True, True], min_active=5, max_gap=2
    ) == []
    event = build_runs(
        days(start, 7), [True] * 5 + [False, False], min_active=5, max_gap=2
    )[0]
    assert event.end == start + timedelta(days=4)
    assert event.span_duration == 5


def test_monthly_spei_threshold_is_strict_and_missing_breaks_run() -> None:
    records = [SpeiRecord.month(2019, 1, -1.0), SpeiRecord.month(2019, 2, -1.01)]
    event = detect_spei_runs(records, threshold=-1.0, min_periods=1)[0]
    assert event.period_count == 1
    assert event.start == date(2019, 2, 1)
    missing = [
        SpeiRecord.month(2019, 1, -2),
        SpeiRecord.month(2019, 2, None),
        SpeiRecord.month(2019, 3, -2),
    ]
    assert detect_spei_runs(missing, threshold=-1.5, min_periods=3) == []


@pytest.mark.parametrize("year, expected_days", [(2019, 90), (2020, 91)])
def test_monthly_spei_uses_true_calendar_days(year: int, expected_days: int) -> None:
    records = [SpeiRecord.month(year, month, -2.0) for month in (1, 2, 3)]
    event = detect_spei_runs(records, threshold=-1.5, min_periods=3)[0]
    assert event.duration_days == expected_days
    assert event.severity == pytest.approx(0.5 * 3)
    assert event.mean_intensity == pytest.approx(0.5)
    assert event.peak_threshold_deficit == pytest.approx(0.5)


def test_monthly_spei_overlap_weights_partial_months_by_days() -> None:
    event = detect_spei_runs(
        [SpeiRecord.month(2019, 1, -2.0), SpeiRecord.month(2019, 2, -1.5)],
        threshold=-1.0,
        min_periods=1,
    )[0]
    result = event_window_bridge_for_spei(
        event, window_start=date(2019, 1, 15), window_end=date(2019, 2, 10)
    )
    assert result is not None
    assert result.duration == result.active_duration == result.span_duration == 27
    assert result.severity == pytest.approx(17 / 31 * 1.0 + 10 / 28 * 0.5)


def test_spei_2w_support_is_explicitly_configurable() -> None:
    timestamps = [date(2019, 1, 14), date(2019, 1, 21)]
    contracts = spei_2w_interval_contracts(
        timestamps,
        accumulation_days=14,
        state_days=7,
        accumulation_timestamp_position="end",
        state_timestamp_position="start",
    )
    assert contracts[0].accumulation_start == date(2019, 1, 1)
    assert contracts[0].accumulation_end_exclusive == date(2019, 1, 15)
    assert contracts[0].state_start == date(2019, 1, 14)
    assert contracts[0].state_end_exclusive == date(2019, 1, 21)
    assert contracts[1].state_start == contracts[0].state_end_exclusive
    records = spei_2w_records(
        timestamps,
        [-1.2, -1.3],
        accumulation_days=14,
        state_days=7,
        accumulation_timestamp_position="end",
        state_timestamp_position="start",
    )
    event = detect_spei_runs(records, threshold=-1.0, min_periods=1)[0]
    assert event.duration_days == 14
    assert records[0].support_start == date(2019, 1, 14)
    assert records[0].support_end_exclusive == date(2019, 1, 21)
    start_intervals = reporting_intervals(
        timestamps, state_days=7, timestamp_position="start"
    )
    assert start_intervals[0] == (date(2019, 1, 14), date(2019, 1, 21))
    gap_records = spei_2w_records(
        [date(2019, 1, 14), date(2019, 1, 28)],
        [-1.2, -1.3],
        accumulation_days=14,
        state_days=7,
        accumulation_timestamp_position="end",
        state_timestamp_position="start",
    )
    assert len(detect_spei_runs(gap_records, threshold=-1.0, min_periods=1)) == 2
    with pytest.raises(ValueError, match="strictly increasing"):
        spei_2w_interval_contracts(
            [date(2019, 1, 14), date(2019, 1, 14)],
            accumulation_days=14,
            state_days=7,
            accumulation_timestamp_position="end",
            state_timestamp_position="start",
        )
    with pytest.raises(ValueError, match="multiples"):
        spei_2w_interval_contracts(
            [date(2019, 1, 14), date(2019, 1, 22)],
            accumulation_days=14,
            state_days=7,
            accumulation_timestamp_position="end",
            state_timestamp_position="start",
        )
    with pytest.raises(ValueError):
        reporting_intervals(timestamps, state_days=7, timestamp_position="unknown")


def test_leap_day_is_excluded_from_fixed_pentads() -> None:
    assert calendar_pentad(date(2020, 2, 28)) == 12
    assert calendar_pentad(date(2020, 2, 29)) is None
    assert calendar_pentad(date(2020, 3, 1)) == 12
    assert calendar_pentad(date(2019, 3, 1)) == 12
    assert calendar_pentad(date(2020, 12, 31)) == 73
    assert len(calendar_pentad_dates(2020, 12)) == 5
    assert date(2020, 2, 29) not in calendar_pentad_dates(2020, 12)


def test_pentad_mean_requires_all_five_days_under_ninety_percent_rule() -> None:
    assert pentad_mean([1, 2, 3, 4, None]) is None
    assert pentad_mean([1, 2, 3, 4, 5]) == pytest.approx(3.0)


def test_type7_quantiles_and_midrank_ties() -> None:
    assert type7_quantile([0, 10, 20, 30], 0.10) == pytest.approx(3.0)
    assert type7_quantile([0, 10, 20, 30], 0.20) == pytest.approx(6.0)
    assert midrank_percentile(10, [0, 10, 10, 20]) == pytest.approx(50.0)


def test_pentad_threshold_states_are_strict_and_need_27_years() -> None:
    insufficient = pentad_percentile_metrics(0.5, [1.0] * 26 + [None] * 4)
    assert insufficient.q20_threshold is None
    sufficient = pentad_percentile_metrics(1.0, [1.0] * 27 + [None] * 3)
    assert sufficient.q10_threshold == pytest.approx(1.0)
    assert sufficient.q20_threshold == pytest.approx(1.0)
    assert sufficient.below_q10 is False
    assert sufficient.below_q20 is False
    assert sufficient.percentile_rank == pytest.approx(50.0)


def test_midrank_is_monotone_and_bounded() -> None:
    ranks = [midrank_percentile(value, [0, 10, 20, 30]) for value in (-1, 0, 5, 10, 40)]
    assert ranks == sorted(ranks)
    assert all(rank is not None and 0 <= rank <= 100 for rank in ranks)


def test_bilinear_weights_and_four_neighbour_renormalization() -> None:
    assert bilinear_weights(0.5, 0.5) == pytest.approx((0.25,) * 4)
    assert bilinear_renormalized([1, 2, None, 4], [0.25] * 4) == pytest.approx(7 / 3)
    assert bilinear_renormalized([1, None, None, None], [0.25] * 4) is None
    assert bilinear_renormalized([1, 2, 3, 4], [0.1, 0.2, 0.3, 0.4]) == pytest.approx(3.0)


def test_coverage_boundary_is_integer_safe() -> None:
    assert required_valid_count(10, 0.9) == 9
    assert required_valid_count(3, 0.9) == 3
    assert coverage_ok(9, 10, 0.9)
    assert not coverage_ok(8, 10, 0.9)


def test_flash_drought_uses_latest_start_and_complete_span_duration() -> None:
    event = detect_flash_droughts(
        [60, 45, 35, 15, 25], min_span_pentads=3, recovery_confirm=1
    )[0]
    assert event.start_index == 1
    assert event.crossing_index == 3
    assert event.end_index == 3
    assert event.onset_pentads == 2
    assert event.onset_speed == pytest.approx(15.0)
    assert event.span_pentads == event.duration == 3
    assert event.dry_pentads == 1
    assert event.severity == pytest.approx(150.0)


def test_flash_drought_span_three_and_four_boundaries() -> None:
    values = [45, 30, 19, 25]
    assert len(detect_flash_droughts(values, min_span_pentads=3, recovery_confirm=1)) == 1
    assert detect_flash_droughts(values, min_span_pentads=4, recovery_confirm=1) == []
    values_four = [45, 35, 30, 19, 25]
    assert len(
        detect_flash_droughts(values_four, min_span_pentads=4, recovery_confirm=1)
    ) == 1


def test_flash_drought_speed_onset_limit_and_missing_boundary() -> None:
    assert detect_flash_droughts(
        [41, 35, 30, 25, 21, 19, 25],
        min_span_pentads=3,
        recovery_confirm=1,
    ) == []
    exact_five = detect_flash_droughts(
        [45, 38, 32, 27, 23, 19, 25],
        min_span_pentads=3,
        recovery_confirm=1,
    )[0]
    assert exact_five.onset_pentads == 5
    assert exact_five.onset_speed == pytest.approx(5.2)
    assert detect_flash_droughts(
        [60, 35, None, 15, 15, 25],
        min_span_pentads=3,
        recovery_confirm=1,
    ) == []


def test_flash_drought_one_and_two_pentad_recovery() -> None:
    values = [50, 30, 15, 15, 15, 22, 18, 25, 25]
    main = detect_flash_droughts(
        values, min_span_pentads=3, recovery_confirm=1
    )[0]
    strict = detect_flash_droughts(
        values, min_span_pentads=4, recovery_confirm=2
    )[0]
    assert main.end_index == 4
    assert strict.end_index == 6
    assert strict.dry_pentads == 4


def test_flash_drought_recovery_requires_a_new_q40_start() -> None:
    events = detect_flash_droughts(
        [50, 35, 15, 25, 15, 25],
        min_span_pentads=3,
        recovery_confirm=1,
    )
    assert [(event.start_index, event.end_index) for event in events] == [(0, 2)]

    separate = detect_flash_droughts(
        [50, 35, 15, 25, 50, 35, 15, 25],
        min_span_pentads=3,
        recovery_confirm=1,
    )
    assert [(event.start_index, event.end_index) for event in separate] == [
        (0, 2),
        (4, 6),
    ]


def test_flash_drought_without_recovery_is_right_censored() -> None:
    event = detect_flash_droughts(
        [50, 35, 15, 15], min_span_pentads=3, recovery_confirm=1
    )[0]
    assert event.right_censored
    assert event.recovery_index is None
    assert event.end_index == 3


def test_hot_flash_drought_any_and_strict_majority() -> None:
    assert classify_hot_flash_drought([False, True, False], rule="any") is True
    assert classify_hot_flash_drought([False, True, False], rule="majority") is False
    assert classify_hot_flash_drought([True, True, False, False], rule="majority") is False
    assert classify_hot_flash_drought([True, True, True, False], rule="majority") is True
    assert classify_hot_flash_drought([True, None], rule="any") is None


def test_event_window_overlap_censoring_and_endpoint_touch() -> None:
    dates = days(date(2019, 1, 1), 10)
    event = build_runs(dates, [True] * 10, min_active=1, intensity=[2] * 10)[0]
    middle = event_window_bridge_for_run(
        event, window_start=date(2019, 1, 5), window_end=date(2019, 1, 7)
    )
    assert middle is not None
    assert middle.event_count == 1
    assert middle.duration == middle.active_duration == middle.span_duration == 3
    assert middle.severity == pytest.approx(6.0)
    assert middle.left_censored and middle.right_censored
    endpoint = event_window_bridge_for_run(
        event, window_start=date(2019, 1, 10), window_end=date(2019, 1, 12)
    )
    assert endpoint is not None and endpoint.active_duration == 1
    assert event_window_bridge_for_run(
        event, window_start=date(2019, 1, 11), window_end=date(2019, 1, 12)
    ) is None


def test_event_window_counts_pure_gap_overlap_but_duration_is_zero() -> None:
    start = date(2019, 1, 1)
    event = build_runs(
        days(start, 7),
        [True, True, False, False, True, True, True],
        min_active=5,
        max_gap=2,
    )[0]
    result = event_window_bridge_for_run(
        event,
        window_start=start + timedelta(days=2),
        window_end=start + timedelta(days=3),
    )
    assert result is not None
    assert result.event_count == 1
    assert result.duration == result.active_duration == 0
    assert result.span_duration == result.gap_duration == 2
    assert result.severity == 0


def test_event_window_pentad_severity_is_prorated_by_overlap_days() -> None:
    segment = EventSegment(date(2019, 1, 1), date(2019, 1, 6), True, 50.0)
    result = event_window_bridge(
        "pentad-1",
        [segment],
        window_start=date(2019, 1, 3),
        window_end=date(2019, 1, 4),
    )
    assert result is not None
    assert result.active_duration == 2
    assert result.severity == pytest.approx(20.0)
