from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from scripts.python.regional_threshold_daily_core import (
    ZONE_ORDER,
    assign_zone,
    build_three_way_state_design,
    build_two_way_design,
    containing_pixel_indices,
    daily_exposure,
    soil_moisture_metrics,
    two_way_residualize,
    window_bounds,
)


class WindowTests(unittest.TestCase):
    def test_frozen_window_boundaries(self) -> None:
        full = window_bounds("full_ext", 100, 150, 200, 366)
        v3he = window_bounds("v3he", 100, 150, 200, 366)
        hema = window_bounds("hema", 100, 150, 200, 366)
        self.assertEqual((full.start, full.stop, full.expected_days), (69, 200, 131))
        self.assertEqual((v3he.start, v3he.stop, v3he.expected_days), (99, 149, 50))
        self.assertEqual((hema.start, hema.stop, hema.expected_days), (149, 200, 51))
        self.assertEqual(v3he.stop, hema.start)
        self.assertEqual(v3he.expected_days + hema.expected_days, 101)

    def test_early_full_window_clips_to_january_first(self) -> None:
        bounds = window_bounds("full_ext", 20, 80, 120, 365)
        self.assertEqual((bounds.start, bounds.stop), (0, 120))

    def test_invalid_phenology_fails(self) -> None:
        with self.assertRaises(ValueError):
            window_bounds("v3he", 150, 100, 200, 365)


class ExposureTests(unittest.TestCase):
    def test_daily_exposure_strict_definition(self) -> None:
        result = daily_exposure(np.array([30.0, 32.0, 33.5, 29.0]), 32.0)
        self.assertTrue(result["complete"])
        self.assertEqual(result["exceedance_days_daily"], 2)
        self.assertAlmostEqual(result["hdd_cday_daily"], 1.5)

    def test_missing_day_invalidates_window(self) -> None:
        result = daily_exposure(np.array([32.0, np.nan, 34.0]), 32.0)
        self.assertFalse(result["complete"])
        self.assertTrue(np.isnan(result["hdd_cday_daily"]))
        self.assertEqual(result["valid_days"], 2)

    def test_external_and_fixed_threshold_not_conflated(self) -> None:
        values = np.array([30.0, 31.0, 32.0])
        external = daily_exposure(values, 30.5)
        fixed = daily_exposure(values, 32.0)
        self.assertEqual(external["exceedance_days_daily"], 2)
        self.assertEqual(fixed["exceedance_days_daily"], 1)
        self.assertNotEqual(external["hdd_cday_daily"], fixed["hdd_cday_daily"])


class SoilMoistureTests(unittest.TestCase):
    def test_antecedent_and_drawdown(self) -> None:
        values = np.linspace(0.40, 0.10, 40)
        bounds = window_bounds("v3he", 21, 25, 30, 365)
        result = soil_moisture_metrics(values, bounds, antecedent_days=14)
        self.assertTrue(result["complete"])
        self.assertEqual(result["antecedent_valid_days"], 14)
        self.assertLess(result["mean_change"], 0)
        self.assertLess(result["min_drawdown"], result["mean_change"])

    def test_incomplete_antecedent_is_missing(self) -> None:
        values = np.linspace(0.40, 0.10, 40)
        bounds = window_bounds("v3he", 10, 20, 30, 365)
        result = soil_moisture_metrics(values, bounds, antecedent_days=14)
        self.assertFalse(result["complete"])
        self.assertTrue(np.isnan(result["antecedent_mean"]))


class FixedEffectTests(unittest.TestCase):
    def test_two_way_residual_group_means_are_zero(self) -> None:
        rng = np.random.default_rng(42)
        first = np.repeat(np.arange(20), 8)
        second = np.tile(np.repeat(np.arange(4), 2), 20)
        values = rng.normal(size=(len(first), 3)) + first[:, None] + second[:, None]
        residual, iterations, delta = two_way_residualize(values, first, second)
        self.assertLess(iterations, 100)
        self.assertLess(delta, 1e-10)
        frame = pd.DataFrame(residual)
        frame["first"] = first
        frame["second"] = second
        self.assertLess(frame.groupby("first")[[0, 1, 2]].mean().abs().to_numpy().max(), 1e-9)
        self.assertLess(frame.groupby("second")[[0, 1, 2]].mean().abs().to_numpy().max(), 1e-9)


class DesignTests(unittest.TestCase):
    def test_zone_assignment_and_complete_interaction_columns(self) -> None:
        provinces = pd.Series(["辽宁省", "河南省", "陕西省", "湖北省", "云南省", "北京市"])
        self.assertEqual(assign_zone(provinces).tolist(), ["NE", "HHH", "NW", "SH", "SW", "Other"])
        rows = []
        for zone_index, zone in enumerate(ZONE_ORDER):
            for i in range(8):
                rows.append(
                    {
                        "zone": zone,
                        "ca": i / 10,
                        "exposure": zone_index + i,
                        "gdd_10_29": 500 + i,
                        "pr_sum": 100 + i,
                    }
                )
        frame = pd.DataFrame(rows)
        design, ca_points, endpoints = build_two_way_design(frame, "exposure")
        for zone in ZONE_ORDER:
            self.assertIn(f"{zone}_exposure", design)
            self.assertIn(f"{zone}_ca", design)
            self.assertIn(f"{zone}_ca_exposure", design)
            self.assertLess(endpoints[zone]["p50"], endpoints[zone]["p90"])
        self.assertLess(ca_points["p25"], ca_points["p75"])

    def test_state_endpoints_have_explicit_units_and_no_key_collision(self) -> None:
        rows = []
        for zone_index, zone in enumerate(ZONE_ORDER):
            for i in range(12):
                rows.append(
                    {
                        "zone": zone,
                        "ca": i / 20,
                        "exposure": 10 * zone_index + i,
                        "state": 0.1 + i / 100,
                        "gdd_10_29": 500 + i,
                        "pr_sum": 100 + i,
                    }
                )
        frame = pd.DataFrame(rows)
        _, _, endpoints = build_three_way_state_design(frame, "exposure", "state")
        expected = {
            "exposure_p50_cday",
            "exposure_p90_cday",
            "state_p25_m3m3",
            "state_p50_m3m3",
            "state_p75_m3m3",
        }
        for zone in ZONE_ORDER:
            self.assertEqual(set(endpoints[zone]), expected)
            self.assertGreater(endpoints[zone]["exposure_p90_cday"], endpoints[zone]["exposure_p50_cday"])
            self.assertLess(endpoints[zone]["state_p25_m3m3"], endpoints[zone]["state_p75_m3m3"])

    def test_pixel_is_area_containing_cell_boundaries(self) -> None:
        rows, cols = containing_pixel_indices(
            np.array([100.0, 100.499999, 100.5]),
            np.array([50.0, 49.500001, 49.5]),
            west=100.0,
            north=50.0,
            resolution=0.5,
        )
        self.assertEqual(cols.tolist(), [0, 0, 1])
        self.assertEqual(rows.tolist(), [0, 0, 1])


if __name__ == "__main__":
    unittest.main()
