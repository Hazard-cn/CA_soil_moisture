from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import netCDF4 as nc
import numpy as np
import pandas as pd
import pytest


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "python"
sys.path.insert(0, str(SCRIPT_DIR))

from climate_stress.era5 import (  # noqa: E402
    attach_daily_temperature_thresholds,
    canonical_day_index,
    column_searchsorted,
    extract_daily_temperature,
    resolve_era_hourly_path,
    type7_quantile_from_sorted,
)
import climate_stress.era5 as era5_module  # noqa: E402


def test_era_year_override_uses_repair_without_changing_default_pattern(
    tmp_path: Path,
) -> None:
    pattern = str(tmp_path / "original" / "ERA{year}.nc")
    repair = tmp_path / "repair" / "ERA1985.nc"
    overrides = {1985: repair}
    assert resolve_era_hourly_path(pattern, 1985, overrides) == repair
    assert resolve_era_hourly_path(pattern, 1984, overrides) == (
        tmp_path / "original" / "ERA1984.nc"
    )


def test_temperature_threshold_attachment_reads_only_requested_cell_block(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    daily_root = tmp_path / "daily"
    target = daily_root / "year=2019"
    target.mkdir(parents=True)
    np.save(target / "date_days_since_1970.npy", np.asarray([17897, 17898], dtype=np.int32))
    np.save(
        target / "era5u8_tmax_c.npy",
        np.asarray([[30.0, 31.0, 32.0, 33.0], [34.0, 35.0, 36.0, 37.0]]),
    )
    np.save(
        target / "era5u8_tmin_c.npy",
        np.asarray([[20.0, 21.0, 22.0, 23.0], [24.0, 25.0, 26.0, 27.0]]),
    )
    threshold_root = tmp_path / "thresholds"
    (threshold_root / "year=2019").mkdir(parents=True)
    np.save(
        threshold_root / "era5u8_tmax_p90_calendar.npy",
        np.broadcast_to(np.arange(4, dtype=float), (366, 4)),
    )
    np.save(
        threshold_root / "era5u8_tmin_p90_calendar.npy",
        np.broadcast_to(np.arange(4, dtype=float) - 1.0, (366, 4)),
    )
    np.save(
        threshold_root
        / "year=2019"
        / "era5u8_tmax_historical_percentile.npy",
        np.asarray([[80.0, 90.0, 95.0, 99.0], [81.0, 91.0, 96.0, 100.0]]),
    )

    real_load = np.load
    observed_selectors: list[slice] = []

    class GuardedTwoDimensionalArray:
        def __init__(self, values: np.ndarray) -> None:
            self.values = values

        def __getitem__(self, key):
            assert isinstance(key, tuple) and len(key) == 2
            selector = key[1]
            assert isinstance(selector, slice)
            assert selector != slice(None)
            observed_selectors.append(selector)
            return self.values[key]

    def guarded_load(*args, **kwargs):
        values = real_load(*args, **kwargs)
        if values.ndim == 2:
            return GuardedTwoDimensionalArray(values)
        return values

    monkeypatch.setattr(era5_module.np, "load", guarded_load)
    result = attach_daily_temperature_thresholds(
        daily_root,
        threshold_root,
        2019,
        cell_slice=slice(1, 3),
    )

    assert observed_selectors and all(value == slice(1, 3) for value in observed_selectors)
    assert result["era5u8_tmax_c"].shape == (2, 2)
    assert result["era5u8_tmax_c"].tolist() == [[31.0, 32.0], [35.0, 36.0]]
    assert result["era5u8_tmax_historical_percentile"].tolist() == [
        [90.0, 95.0],
        [91.0, 96.0],
    ]


def _write_era(
    path: Path,
    year: int,
    *,
    axis_year: int | None = None,
    omitted_hour_index: int | None = None,
    latitude_offset: float = 0.0,
) -> None:
    time_year = int(year if axis_year is None else axis_year)
    start = np.datetime64(f"{time_year:04d}-01-01T00", "h")
    end = np.datetime64(f"{time_year + 1:04d}-01-01T00", "h")
    hours = np.arange(start, end, np.timedelta64(1, "h"))
    if omitted_hour_index is not None:
        hours = np.delete(hours, int(omitted_hour_index))
    with nc.Dataset(path, "w") as dataset:
        dataset.createDimension("valid_time", len(hours))
        dataset.createDimension("latitude", 6)
        dataset.createDimension("longitude", 7)
        time = dataset.createVariable("valid_time", "f8", ("valid_time",))
        time.units = "hours since 1970-01-01 00:00:00"
        time.calendar = "standard"
        time[:] = nc.date2num(
            [datetime.fromisoformat(np.datetime_as_string(value, unit="h")) for value in hours],
            time.units,
            time.calendar,
        )
        latitude = dataset.createVariable("latitude", "f8", ("latitude",))
        longitude = dataset.createVariable("longitude", "f8", ("longitude",))
        latitude[:] = np.asarray(
            [53.93, 53.83, 53.73, 53.63, 53.53, 53.43]
        ) + float(latitude_offset)
        longitude[:] = [73.08, 73.18, 73.28, 73.38, 73.48, 73.58, 73.68]
        t2m = dataset.createVariable(
            "t2m",
            "f4",
            ("valid_time", "latitude", "longitude"),
            chunksizes=(48, 3, 4),
            fill_value=np.float32(np.nan),
        )
        utc_hour = (np.arange(len(hours)) % 24).astype(np.float32)
        t2m[:] = utc_hour[:, None, None] + np.float32(273.15)


def test_utc_plus_8_uses_previous_year_boundary_hours(tmp_path: Path) -> None:
    _write_era(tmp_path / "ERA2019.nc", 2019)
    _write_era(tmp_path / "ERA2020.nc", 2020)
    cells = pd.DataFrame(
        {
            "era01_cell_id": [1],
            "lat_idx": [0],
            "lon_idx": [0],
            "latitude": [53.53],
            "longitude": [73.58],
        }
    )
    dates, arrays, metadata = extract_daily_temperature(
        str(tmp_path / "ERA{year}.nc"),
        2020,
        cells,
        utc_offset_hours=8,
        gdd_pairs=((8, 29),),
        edd_thresholds=(10,),
        coordinate_tolerance=1e-9,
    )
    assert len(dates) == 366
    assert str(dates[0]) == "2020-01-01"
    assert str(dates[-1]) == "2020-12-31"
    assert arrays["era5u8_hour_count"][0, 0] == 24
    assert arrays["era5u8_tmean_c"][0, 0] == pytest.approx(11.5)
    assert arrays["era5u8_tmax_c"][0, 0] == pytest.approx(23.0)
    assert arrays["era5u8_tmin_c"][0, 0] == pytest.approx(0.0)
    assert arrays["era5u8_gdd_b8_u29"][0, 0] == pytest.approx(3.5)
    assert arrays["era5u8_edd_t10"][0, 0] == pytest.approx(91 / 24)
    assert metadata["timezone_offset_hours"] == 8


def test_wrong_year_previous_file_is_rejected_before_daily_aggregation(
    tmp_path: Path,
) -> None:
    _write_era(tmp_path / "ERA2019.nc", 2019, axis_year=2001)
    _write_era(tmp_path / "ERA2020.nc", 2020)
    cells = pd.DataFrame(
        {
            "era01_cell_id": [1],
            "lat_idx": [0],
            "lon_idx": [0],
            "latitude": [53.53],
            "longitude": [73.58],
        }
    )
    with pytest.raises(ValueError, match="filename year 2019"):
        extract_daily_temperature(
            str(tmp_path / "ERA{year}.nc"),
            2020,
            cells,
            utc_offset_hours=8,
            gdd_pairs=((8, 29),),
            edd_thresholds=(10,),
            coordinate_tolerance=1e-9,
        )


def test_missing_hour_is_rejected_before_daily_aggregation(tmp_path: Path) -> None:
    _write_era(tmp_path / "ERA2019.nc", 2019)
    _write_era(tmp_path / "ERA2020.nc", 2020, omitted_hour_index=100)
    cells = pd.DataFrame(
        {
            "era01_cell_id": [1],
            "lat_idx": [0],
            "lon_idx": [0],
            "latitude": [53.53],
            "longitude": [73.58],
        }
    )
    with pytest.raises(ValueError, match="filename year 2020"):
        extract_daily_temperature(
            str(tmp_path / "ERA{year}.nc"),
            2020,
            cells,
            utc_offset_hours=8,
            gdd_pairs=((8, 29),),
            edd_thresholds=(10,),
            coordinate_tolerance=1e-9,
        )


def test_adjacent_era_files_with_different_spatial_axes_are_rejected(
    tmp_path: Path,
) -> None:
    _write_era(tmp_path / "ERA2019.nc", 2019)
    _write_era(tmp_path / "ERA2020.nc", 2020, latitude_offset=0.01)
    cells = pd.DataFrame(
        {
            "era01_cell_id": [1],
            "lat_idx": [0],
            "lon_idx": [0],
            "latitude": [53.53],
            "longitude": [73.58],
        }
    )
    with pytest.raises(ValueError, match="spatial axes differ"):
        extract_daily_temperature(
            str(tmp_path / "ERA{year}.nc"),
            2020,
            cells,
            utc_offset_hours=8,
            gdd_pairs=((8, 29),),
            edd_thresholds=(10,),
            coordinate_tolerance=1e-9,
        )


def test_calendar_day_keeps_february_29_as_a_distinct_bin() -> None:
    assert canonical_day_index("2020-02-28") + 1 == canonical_day_index("2020-02-29")
    assert canonical_day_index("2020-02-29") + 1 == canonical_day_index("2019-03-01")
    assert canonical_day_index("2020-12-31") == 365


def test_type7_and_column_searchsorted_with_ties() -> None:
    sample = np.asarray([[0, 1], [10, 1], [10, 1], [20, np.nan]], dtype=float)
    sample.sort(axis=0)
    counts = np.asarray([4, 3])
    quantile = type7_quantile_from_sorted(sample, counts, 0.20)
    assert quantile[0] == pytest.approx(6.0)
    assert quantile[1] == pytest.approx(1.0)
    queries = np.asarray([[10, 1], [30, 0]], dtype=float)
    left = column_searchsorted(sample, queries, counts, side="left")
    right = column_searchsorted(sample, queries, counts, side="right")
    assert left.tolist() == [[1, 0], [4, 0]]
    assert right.tolist() == [[3, 3], [4, 0]]
