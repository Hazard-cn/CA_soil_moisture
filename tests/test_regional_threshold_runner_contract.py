from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from netCDF4 import Dataset


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "python"
sys.path.insert(0, str(SCRIPT_DIR))

from regional_threshold_daily_core import (  # noqa: E402
    ZONE_ORDER,
    build_two_way_design,
    fit_two_way_fe_cluster,
)
from run_regional_threshold_daily_override import read_daily_cube  # noqa: E402


class NetCdfContractTests(unittest.TestCase):
    def _write_cube(self, path: Path, units: str) -> None:
        dates = pd.date_range("2019-01-01", "2019-12-31", freq="D")
        with Dataset(path, "w") as ds:
            ds.createDimension("valid_time", len(dates))
            ds.createDimension("latitude", 2)
            ds.createDimension("longitude", 2)
            time = ds.createVariable("valid_time", "i4", ("valid_time",))
            time.units = "days since 2019-01-01"
            time[:] = np.arange(len(dates))
            ds.createVariable("latitude", "f8", ("latitude",))[:] = [30.0, 29.9]
            ds.createVariable("longitude", "f8", ("longitude",))[:] = [110.0, 110.1]
            value = ds.createVariable("t2m_max", "f4", ("valid_time", "latitude", "longitude"))
            value.units = units
            value[:] = 30.0

    def test_units_dimensions_and_calendar_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "valid.nc"
            self._write_cube(path, "°C")
            values, latitude, longitude, metadata = read_daily_cube(
                path, "t2m_max", "valid_time", 2019, expected_units={"°C"}
            )
            self.assertEqual(values.shape, (365, 2, 2))
            self.assertEqual(metadata["units"], "°C")
            self.assertEqual(len(latitude), 2)
            self.assertEqual(len(longitude), 2)
            wrong = Path(tmp) / "wrong.nc"
            self._write_cube(wrong, "K")
            with self.assertRaises(AssertionError):
                read_daily_cube(wrong, "t2m_max", "valid_time", 2019, expected_units={"°C"})


class KnownCoefficientTests(unittest.TestCase):
    def test_two_way_fe_recovers_known_coefficients(self) -> None:
        rng = np.random.default_rng(42)
        rows = []
        grid = 0
        for zone_index, zone in enumerate(ZONE_ORDER):
            for local_grid in range(18):
                grid += 1
                province = f"p{zone_index}_{local_grid % 3}"
                grid_fe = rng.normal()
                for year in range(2016, 2020):
                    rows.append(
                        {
                            "grid_id": grid,
                            "year": year,
                            "province": province,
                            "zone": zone,
                            "ca": 0.05 + 0.12 * (year - 2016) + rng.normal(scale=0.03),
                            "exposure": 2 * zone_index + 3 * (year - 2016) + rng.normal(scale=1.0),
                            "gdd_10_29": 500 + 20 * year + rng.normal(scale=10),
                            "pr_sum": 200 + 5 * year + rng.normal(scale=20),
                            "grid_fe": grid_fe,
                        }
                    )
        frame = pd.DataFrame(rows)
        design, _, _ = build_two_way_design(frame, "exposure")
        beta = np.linspace(-0.03, 0.04, design.shape[1])
        province_year = pd.factorize(frame["province"] + "::" + frame["year"].astype(str))[0]
        frame["ln_yield"] = (
            design.to_numpy() @ beta
            + frame["grid_fe"].to_numpy()
            + 0.2 * np.sin(province_year)
        )
        fit, diagnostics = fit_two_way_fe_cluster(frame, "ln_yield", design)
        self.assertEqual(diagnostics["rank"], design.shape[1])
        self.assertLess(np.max(np.abs(np.asarray(fit.params) - beta)), 1e-8)


if __name__ == "__main__":
    unittest.main()
