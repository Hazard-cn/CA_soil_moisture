from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "python"
sys.path.insert(0, str(SCRIPT_DIR))

from climate_stress.gleam import DailyTargetMetrics, PentadTargetMetrics  # noqa: E402
from climate_stress.soil import aggregate_gleam_windows  # noqa: E402


def test_gleam_window_states_daily_event_and_flash_drought() -> None:
    dates = tuple(date(2019, 1, 1) + timedelta(days=value) for value in range(365))
    values = np.full((365, 1), 0.30)
    values[9:14, 0] = 0.05
    q10 = np.full((365, 1), 0.10)
    daily = DailyTargetMetrics(
        q10=q10,
        percentile=np.full((365, 1), 50.0),
        below_p10=(values < q10).astype(float),
        history_count=np.full((365, 1), 150, dtype=np.int16),
        expected_history_count=np.full(365, 150, dtype=np.int16),
    )
    percentile = np.full((73, 1), 50.0)
    percentile[:4, 0] = [50, 30, 15, 25]
    pentad = PentadTargetMetrics(
        percentile=percentile,
        below_p10=(percentile < 10).astype(float),
        below_p20=(percentile < 20).astype(float),
        history_count=np.full((73, 1), 30, dtype=np.int16),
        q10=np.full((73, 1), 0.10),
        q20=np.full((73, 1), 0.20),
        q40=np.full((73, 1), 0.40),
    )
    panel = pd.DataFrame(
        {
            "era01_cell_id": [1],
            "grid_id_v3": [100],
            "lat_idx": [0],
            "lon_idx": [0],
            "latitude": [53.53],
            "longitude": [73.58],
            "lat10": [535],
            "lon10": [736],
            "year": [2019],
            "win_full_start": [1],
            "win_full_end": [30],
            "win_full_days": [30],
        }
    )
    long, events, bridges = aggregate_gleam_windows(
        panel,
        layer="SMrz",
        years=[2019],
        windows=["full"],
        daily_dates={2019: dates},
        daily_values={2019: values},
        daily_metrics={2019: daily},
        pentad_values={2019: np.full((73, 1), 0.30)},
        pentad_metrics={2019: pentad},
        cell_block_size=1,
    )
    row = long.iloc[0]
    assert row["gleam43a_smrz_p20_exposure_days"] == 5
    assert row["gleam43a_smrz_p20_longest_spell_days"] == 5
    assert row["gleam43a_smrz_min_pct"] == 15
    assert row["gleam43a_smrz_peak_dryness20"] == 5
    assert row["gleam43a_smrz_p20_deficit_area_pctdays"] == 25
    assert row["gleam43a_smrz_p10_event_main_gap0_any"] == 1
    assert row["gleam43a_smrz_p10_event_main_gap0_total_duration_days"] == 5
    assert row["gleam43a_smrz_p10_event_main_gap0_total_severity_m3m3_days"] == 0.25
    assert row["gleam43a_smrz_fd_main_any"] == 1
    assert row["gleam43a_smrz_fd_main_total_duration_days"] == 15
    assert row["gleam43a_smrz_fd_main_total_severity_pctdays"] == 175
    assert set(events["event_family"]) == {"daily_p10", "flash_drought"}
    assert set(bridges["event_family"]) == {"daily_p10", "flash_drought"}

    q10_with_gaps = q10.copy()
    q10_with_gaps[:4, 0] = np.nan
    daily_with_gaps = DailyTargetMetrics(
        q10=q10_with_gaps,
        percentile=np.full((365, 1), 50.0),
        below_p10=np.where(np.isfinite(q10_with_gaps), values < q10_with_gaps, np.nan),
        history_count=np.full((365, 1), 150, dtype=np.int16),
        expected_history_count=np.full(365, 150, dtype=np.int16),
    )
    gated, gated_events, gated_bridges = aggregate_gleam_windows(
        panel,
        layer="SMrz",
        years=[2019],
        windows=["full"],
        daily_dates={2019: dates},
        daily_values={2019: values},
        daily_metrics={2019: daily_with_gaps},
        pentad_values={2019: np.full((73, 1), 0.30)},
        pentad_metrics={2019: pentad},
        cell_block_size=1,
    )
    gated_row = gated.iloc[0]
    assert gated_row["gleam43a_smrz_daily_coverage"] == 1
    assert np.isclose(gated_row["gleam43a_smrz_p10_event_coverage"], 26 / 30)
    assert np.isnan(gated_row["gleam43a_smrz_p10_event_main_gap0_any"])
    assert "daily_p10" in set(gated_events["event_family"])
    assert "daily_p10" not in set(gated_bridges["event_family"])


def test_flash_drought_does_not_bridge_nonconsecutive_pilot_years() -> None:
    years = [2010, 2016]
    daily_dates: dict[int, tuple[date, ...]] = {}
    daily_values: dict[int, np.ndarray] = {}
    daily_metrics: dict[int, DailyTargetMetrics] = {}
    pentad_values: dict[int, np.ndarray] = {}
    pentad_metrics: dict[int, PentadTargetMetrics] = {}
    for year in years:
        day_count = 366 if year == 2016 else 365
        year_dates = tuple(
            date(year, 1, 1) + timedelta(days=value) for value in range(day_count)
        )
        values = np.full((day_count, 1), 0.30)
        q10 = np.full((day_count, 1), 0.10)
        daily_dates[year] = year_dates
        daily_values[year] = values
        daily_metrics[year] = DailyTargetMetrics(
            q10=q10,
            percentile=np.full((day_count, 1), 50.0),
            below_p10=np.zeros((day_count, 1)),
            history_count=np.full((day_count, 1), 150, dtype=np.int16),
            expected_history_count=np.full(day_count, 150, dtype=np.int16),
        )
        percentile = np.full((73, 1), 50.0)
        if year == 2010:
            percentile[-2:, 0] = [45.0, 30.0]
        else:
            percentile[:2, 0] = [15.0, 25.0]
        pentad_values[year] = np.full((73, 1), 0.30)
        pentad_metrics[year] = PentadTargetMetrics(
            percentile=percentile,
            below_p10=(percentile < 10).astype(float),
            below_p20=(percentile < 20).astype(float),
            history_count=np.full((73, 1), 30, dtype=np.int16),
            q10=np.full((73, 1), 0.10),
            q20=np.full((73, 1), 0.20),
            q40=np.full((73, 1), 0.40),
        )
    panel = pd.DataFrame(
        {
            "era01_cell_id": [1, 1],
            "grid_id_v3": [100, 100],
            "lat_idx": [0, 0],
            "lon_idx": [0, 0],
            "latitude": [53.53, 53.53],
            "longitude": [73.58, 73.58],
            "lat10": [535, 535],
            "lon10": [736, 736],
            "year": years,
            "win_full_start": [1, 1],
            "win_full_end": [15, 15],
            "win_full_days": [15, 15],
        }
    )

    long, events, bridges = aggregate_gleam_windows(
        panel,
        layer="SMrz",
        years=years,
        windows=["full"],
        daily_dates=daily_dates,
        daily_values=daily_values,
        daily_metrics=daily_metrics,
        pentad_values=pentad_values,
        pentad_metrics=pentad_metrics,
        cell_block_size=1,
    )

    assert (long["gleam43a_smrz_fd_main_any"] == 0).all()
    assert events.empty
    assert bridges.empty


def test_context_events_before_output_preserve_stable_event_numbering() -> None:
    event_years = [2018, 2019]
    daily_dates: dict[int, tuple[date, ...]] = {}
    daily_values: dict[int, np.ndarray] = {}
    daily_metrics: dict[int, DailyTargetMetrics] = {}
    pentad_values: dict[int, np.ndarray] = {}
    pentad_metrics: dict[int, PentadTargetMetrics] = {}
    for year in event_years:
        days = 365
        dates = tuple(date(year, 1, 1) + timedelta(days=index) for index in range(days))
        values = np.full((days, 1), 0.30)
        values[:5, 0] = 0.05
        q10 = np.full((days, 1), 0.10)
        daily_dates[year] = dates
        daily_values[year] = values
        daily_metrics[year] = DailyTargetMetrics(
            q10=q10,
            percentile=np.full((days, 1), 50.0),
            below_p10=(values < q10).astype(float),
            history_count=np.full((days, 1), 30, dtype=np.int16),
            expected_history_count=np.full(days, 30, dtype=np.int16),
        )
        percentile = np.full((73, 1), 50.0)
        pentad_values[year] = np.full((73, 1), 0.30)
        pentad_metrics[year] = PentadTargetMetrics(
            percentile=percentile,
            below_p10=np.zeros((73, 1)),
            below_p20=np.zeros((73, 1)),
            history_count=np.full((73, 1), 30, dtype=np.int16),
            q10=np.full((73, 1), 0.10),
            q20=np.full((73, 1), 0.20),
            q40=np.full((73, 1), 0.40),
        )
    panel = pd.DataFrame(
        {
            "era01_cell_id": [1],
            "grid_id_v3": [100],
            "lat_idx": [0],
            "lon_idx": [0],
            "latitude": [53.53],
            "longitude": [73.58],
            "lat10": [535],
            "lon10": [736],
            "year": [2019],
            "win_full_start": [1],
            "win_full_end": [10],
            "win_full_days": [10],
        }
    )
    long, events, bridges = aggregate_gleam_windows(
        panel,
        layer="SMrz",
        years=[2019],
        event_years=event_years,
        windows=["full"],
        daily_dates=daily_dates,
        daily_values=daily_values,
        daily_metrics=daily_metrics,
        pentad_values=pentad_values,
        pentad_metrics=pentad_metrics,
        cell_block_size=1,
    )
    daily_events = events.loc[events["event_family"].eq("daily_p10")]
    assert len(daily_events) == 2
    assert daily_events["event_id"].str.endswith(":0002").all()
    assert not daily_events["source_left_censored"].any()
    assert not daily_events["source_right_censored"].any()
    assert bridges["event_id"].str.endswith(":0002").all()
    assert long.iloc[0]["gleam43a_smrz_p10_event_main_gap0_count"] == 1
