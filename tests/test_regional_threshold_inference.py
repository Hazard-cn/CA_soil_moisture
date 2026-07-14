from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from scripts.python.regional_threshold_inference import (
    holm_adjust,
    joint_wild_bootstrap,
    romano_wolf_stepdown,
    spatial_block_labels,
)


class MultiplicityTests(unittest.TestCase):
    def test_holm_is_monotone_in_sorted_pvalues(self) -> None:
        p = np.array([0.03, 0.001, 0.20, 0.04])
        adjusted = holm_adjust(p)
        order = np.argsort(p)
        self.assertTrue(np.all(np.diff(adjusted[order]) >= -1e-15))
        self.assertTrue(np.all(adjusted >= p))
        self.assertTrue(np.all(adjusted <= 1))

    def test_romano_wolf_shape_and_bounds(self) -> None:
        rng = np.random.default_rng(42)
        draws = rng.normal(size=(499, 3))
        p = romano_wolf_stepdown(np.array([2.0, 1.0, 0.2]), draws, draws.std(axis=0, ddof=1))
        self.assertEqual(p.shape, (3,))
        self.assertTrue(np.all((p >= 0) & (p <= 1)))

    def test_joint_bootstrap_is_deterministic(self) -> None:
        contributions = pd.DataFrame(
            {"full_ext::NE": [0.1, -0.2, 0.05], "full_ext::HHH": [0.2, 0.1, -0.1]},
            index=["a", "b", "c"],
        )
        estimates = pd.Series({"full_ext::NE": 0.05, "full_ext::HHH": 0.10})
        first = joint_wild_bootstrap(contributions, estimates, reps=99, seed=42)
        second = joint_wild_bootstrap(contributions, estimates, reps=99, seed=42)
        pd.testing.assert_frame_equal(first[0], second[0])
        pd.testing.assert_frame_equal(first[1], second[1])
        pd.testing.assert_frame_equal(first[2], second[2])


class SpatialBlockTests(unittest.TestCase):
    def test_two_degree_blocks_are_stable(self) -> None:
        labels = spatial_block_labels(
            pd.Series([30.1, 31.9, 32.0]), pd.Series([110.1, 111.9, 112.0]), degrees=2.0
        )
        self.assertEqual(labels[0], labels[1])
        self.assertNotEqual(labels[1], labels[2])


if __name__ == "__main__":
    unittest.main()
