from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import xarray as xr


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "python"
sys.path.insert(0, str(SCRIPT_DIR))

from climate_stress.gleam import (  # noqa: E402
    NATIVE_TIME_CHUNK_DAYS,
    apply_daily_p10_climatology,
    apply_pentad_climatology,
    build_spatial_map,
    compute_pentad_climatology,
    daily_p10_event_audit,
    daily_values_to_pentads,
    flash_drought_event_audit,
    interpolate_spatial_block,
    iter_selected_daily_blocks,
    write_selected_daily_cache,
)


def make_synthetic_gleam(
    path: Path,
    layer: str,
    *,
    days: int = 25,
    start: str = "2019-01-01",
    time: pd.DatetimeIndex | None = None,
) -> None:
    latitude = np.asarray([2.0, 1.0, 0.0, -1.0])
    longitude = np.asarray([10.0, 11.0, 12.0, 13.0, 14.0])
    time = pd.date_range(start, periods=days, freq="D") if time is None else time
    days = len(time)
    values = np.empty((days, len(latitude), len(longitude)), dtype=np.float32)
    for index in range(days):
        values[index] = index + latitude[:, None] + longitude[None, :]
    xr.Dataset(
        {layer: (("time", "lat", "lon"), values)},
        coords={"time": time, "lat": latitude, "lon": longitude},
    ).to_netcdf(path)


def all_dates(year: int) -> list[date]:
    count = 366 if year % 4 == 0 else 365
    return [date(year, 1, 1) + timedelta(days=offset) for offset in range(count)]


def test_descending_lat_ascending_lon_map_and_no_extrapolation() -> None:
    mapping = build_spatial_map(
        [2.0, 1.0, 0.0, -1.0],
        [10.0, 11.0, 12.0, 13.0],
        [0.5],
        [11.5],
        cell_ids=[99],
    )
    assert (mapping.lat_start, mapping.lat_stop) == (1, 3)
    assert (mapping.lon_start, mapping.lon_stop) == (1, 3)
    assert mapping.weights[0].tolist() == pytest.approx([0.25] * 4)
    assert mapping.cell_ids.tolist() == [99]
    with pytest.raises(ValueError, match="outside"):
        build_spatial_map([1.0, 0.0], [10.0, 11.0], [2.0], [10.5])


def test_two_of_four_valid_neighbors_are_renormalized_but_one_is_missing() -> None:
    mapping = build_spatial_map([1.0, 0.0], [10.0, 11.0], [0.5], [10.5])
    two_valid = np.asarray([[[1.0, np.nan], [np.nan, 4.0]]])
    assert interpolate_spatial_block(two_valid, mapping)[0, 0] == pytest.approx(2.5)
    one_valid = np.asarray([[[1.0, np.nan], [np.nan, np.nan]]])
    assert np.isnan(interpolate_spatial_block(one_valid, mapping)[0, 0])


@pytest.mark.parametrize("layer", ["SMrz", "SMs"])
def test_native_twelve_day_bbox_blocks_are_isomorphic(
    tmp_path: Path, layer: str
) -> None:
    source = tmp_path / f"{layer}_2019.nc"
    make_synthetic_gleam(source, layer)
    mapping = build_spatial_map(
        [2.0, 1.0, 0.0, -1.0],
        [10.0, 11.0, 12.0, 13.0, 14.0],
        [0.5],
        [11.5],
        cell_ids=[7],
    )
    blocks = list(iter_selected_daily_blocks(source, layer, mapping))
    assert [len(block.dates) for block in blocks] == [12, 12, 1]
    assert all(block.source_bbox_shape[1:] == (2, 2) for block in blocks)
    assert blocks[0].values[0, 0] == pytest.approx(12.0)
    assert NATIVE_TIME_CHUNK_DAYS == 12


def test_selected_daily_cache_stays_inside_run_and_contains_only_cells(
    tmp_path: Path,
) -> None:
    from netCDF4 import Dataset

    source = tmp_path / "SMrz_2019.nc"
    make_synthetic_gleam(source, "SMrz")
    mapping = build_spatial_map(
        [2.0, 1.0, 0.0, -1.0],
        [10.0, 11.0, 12.0, 13.0, 14.0],
        [0.5, 0.25],
        [11.5, 11.75],
        cell_ids=[7, 8],
    )
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    target = run_dir / "cache" / "gleam" / "SMrz_2019.nc"
    summary = write_selected_daily_cache(
        source, target, run_dir, "SMrz", mapping, cell_chunk_size=2
    )
    assert summary.days == 25 and summary.cells == 2 and summary.rows == 50
    assert summary.time_chunk_days == 12
    with Dataset(target) as dataset:
        assert len(dataset.dimensions["time"]) == 25
        assert len(dataset.dimensions["cell"]) == 2
        assert dataset.variables["SMrz"].shape == (25, 2)
        assert dataset.variables["era01_cell_id"][:].tolist() == [7, 8]


def test_selected_daily_cache_requires_the_named_complete_calendar_year(
    tmp_path: Path,
) -> None:
    mapping = build_spatial_map(
        [2.0, 1.0, 0.0, -1.0],
        [10.0, 11.0, 12.0, 13.0, 14.0],
        [0.5],
        [11.5],
        cell_ids=[7],
    )

    valid_source = tmp_path / "valid_2019.nc"
    make_synthetic_gleam(valid_source, "SMrz", days=365)
    valid_run = tmp_path / "valid_run"
    valid_run.mkdir()
    summary = write_selected_daily_cache(
        valid_source,
        valid_run / "SMrz_2019.nc",
        valid_run,
        "SMrz",
        mapping,
        expected_year=2019,
    )
    assert summary.year == 2019 and summary.days == 365

    wrong_year = tmp_path / "wrong_year.nc"
    make_synthetic_gleam(wrong_year, "SMrz", days=366, start="2020-01-01")
    wrong_run = tmp_path / "wrong_run"
    wrong_run.mkdir()
    with pytest.raises(ValueError, match="source year is 2020, expected 2019"):
        write_selected_daily_cache(
            wrong_year,
            wrong_run / "SMrz_2019.nc",
            wrong_run,
            "SMrz",
            mapping,
            expected_year=2019,
        )


@pytest.mark.parametrize("defect", ["missing", "duplicate"])
def test_selected_daily_cache_rejects_missing_or_duplicate_dates(
    tmp_path: Path, defect: str
) -> None:
    time = pd.date_range("2019-01-01", periods=365, freq="D")
    if defect == "missing":
        time = time.delete(100)
    else:
        values = time.to_numpy(copy=True)
        values[100] = values[99]
        time = pd.DatetimeIndex(values)
    source = tmp_path / f"{defect}.nc"
    make_synthetic_gleam(source, "SMrz", time=time)
    mapping = build_spatial_map(
        [2.0, 1.0, 0.0, -1.0],
        [10.0, 11.0, 12.0, 13.0, 14.0],
        [0.5],
        [11.5],
        cell_ids=[7],
    )
    run_dir = tmp_path / f"run_{defect}"
    run_dir.mkdir()
    with pytest.raises(ValueError, match="daily axis is not the complete consecutive"):
        write_selected_daily_cache(
            source,
            run_dir / "SMrz_2019.nc",
            run_dir,
            "SMrz",
            mapping,
            expected_year=2019,
        )


def test_leap_day_is_retained_daily_but_excluded_from_73_complete_pentads() -> None:
    dates = all_dates(2020)
    values = np.ones((len(dates), 1), dtype=float)
    values[dates.index(date(2020, 2, 29)), 0] = 999.0
    result = daily_values_to_pentads(dates, values)
    assert result.values.shape == (73, 1)
    assert np.all(result.values == 1.0)
    assert np.all(result.valid_day_counts == 5)
    missing_date = date(2020, 3, 1)
    values[dates.index(missing_date), 0] = np.nan
    incomplete = daily_values_to_pentads(dates, values)
    assert np.isnan(incomplete.values[11, 0])
    assert incomplete.valid_day_counts[11, 0] == 4


def test_type7_pentad_thresholds_midrank_and_strict_states() -> None:
    history = np.broadcast_to(
        np.arange(30, dtype=float)[:, None, None], (30, 73, 1)
    ).copy()
    climatology = compute_pentad_climatology(history)
    assert climatology.q10[0, 0] == pytest.approx(2.9)
    assert climatology.q20[0, 0] == pytest.approx(5.8)
    assert climatology.q40[0, 0] == pytest.approx(11.6)
    target = np.full((73, 1), 5.0)
    result = apply_pentad_climatology(target, history)
    assert result.percentile[0, 0] == pytest.approx(100 * 5.5 / 30)
    assert result.below_p10[0, 0] == 0
    assert result.below_p20[0, 0] == 1
    equal_q10 = climatology.q10.copy()
    strict = apply_pentad_climatology(equal_q10, history)
    assert strict.below_p10[0, 0] == 0


def test_pentad_threshold_requires_at_least_twenty_seven_years() -> None:
    history = np.ones((30, 73, 1), dtype=float)
    history[:4, 0, 0] = np.nan
    result = compute_pentad_climatology(history)
    assert result.history_count[0, 0] == 26
    assert np.isnan(result.q10[0, 0])
    assert result.history_count[1, 0] == 30
    assert result.q10[1, 0] == pytest.approx(1.0)


def test_daily_plus_minus_two_calendar_day_p10_includes_leap_day_rule() -> None:
    historical_dates = [day for year in range(1981, 2011) for day in all_dates(year)]
    historical_values = np.ones((len(historical_dates), 1), dtype=float)
    target_dates = [date(2012, 2, 29), date(2012, 3, 1)]
    target_values = np.asarray([[1.0], [0.5]])
    result = apply_daily_p10_climatology(
        target_dates, target_values, historical_dates, historical_values
    )
    # Feb 27, Feb 28, Mar 1, Mar 2 occur in all 30 years; Feb 29 in 7.
    assert result.expected_history_count[0] == 127
    assert result.history_count[0, 0] == 127
    assert result.q10[0, 0] == pytest.approx(1.0)
    assert result.percentile[0, 0] == pytest.approx(50.0)
    assert result.below_p10[0, 0] == 0
    assert result.below_p10[1, 0] == 1


def test_daily_p10_events_use_gap_zero_and_gap_two_core_rules() -> None:
    dates = [date(2019, 1, 1) + timedelta(days=offset) for offset in range(7)]
    values = [0, 0, 2, 2, 0, 0, 0]
    audit = daily_p10_event_audit(
        cell_id=1,
        layer="SMrz",
        dates=dates,
        values=values,
        q10=[1] * 7,
    )
    assert audit["variant"].tolist() == ["sensitivity_gap2"]
    row = audit.iloc[0]
    assert row["duration_days"] == 5
    assert row["span_days"] == 7
    assert row["gap_days"] == 2
    assert row["severity"] == pytest.approx(5.0)


def test_flash_drought_audit_keeps_primary_and_strict_complete_spans() -> None:
    percentiles = [45, 35, 30, 19, 15, 25, 25]
    years = [2019] * len(percentiles)
    pentads = list(range(1, len(percentiles) + 1))
    audit = flash_drought_event_audit(
        cell_id=1,
        layer="SMs",
        years=years,
        pentads=pentads,
        percentiles=percentiles,
    )
    assert set(audit["variant"]) == {
        "primary_span3_recovery1",
        "strict_span4_recovery2",
    }
    strict = audit.loc[audit["variant"] == "strict_span4_recovery2"].iloc[0]
    assert strict["span_pentads"] == 5
    assert strict["recovery_pentad"] == 6
