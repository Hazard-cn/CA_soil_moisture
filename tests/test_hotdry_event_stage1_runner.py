from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import xarray as xr


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

from run_hotdry_event_stage1 import daily_values  # noqa: E402


def fixture() -> xr.DataArray:
    values = np.arange(2 * 3 * 4, dtype=np.float32).reshape(2, 3, 4)
    return xr.DataArray(
        values,
        dims=("time", "latitude", "longitude"),
        coords={"time": [0, 1], "latitude": [3, 2, 1], "longitude": [10, 11, 12, 13]},
    )


def test_point_index_path_equals_numpy_pairwise_gather() -> None:
    variable = fixture()
    latitude = np.array([0, 2, 1])
    longitude = np.array([3, 1, 2])
    expected = variable.values[:, latitude, longitude].astype(float)
    np.testing.assert_array_equal(daily_values(variable, latitude, longitude), expected)


def test_bulk_read_path_equals_numpy_pairwise_gather() -> None:
    variable = fixture()
    latitude = np.arange(1_000) % 3
    longitude = np.arange(1_000) % 4
    expected = variable.values[:, latitude, longitude].astype(float)
    np.testing.assert_array_equal(daily_values(variable, latitude, longitude), expected)

