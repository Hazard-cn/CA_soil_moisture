from __future__ import annotations

from pathlib import Path
import sys

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

from hotdry_event_override_models import (  # noqa: E402
    absorb_two_way,
    fit_absorbed_ols,
    rademacher_weights,
    romano_wolf_stepdown,
)


def test_two_way_absorption_removes_both_group_means() -> None:
    first = np.array([0, 0, 1, 1, 2, 2, 3, 3])
    second = np.array([0, 1, 0, 1, 0, 1, 0, 1])
    values = np.column_stack([np.arange(8.0), np.array([1, 3, 2, 5, 4, 8, 7, 9])])
    transformed, _ = absorb_two_way(values, first, second)
    for codes in (first, second):
        for group in np.unique(codes):
            np.testing.assert_allclose(transformed[codes == group].mean(axis=0), 0.0, atol=1e-9)


def test_absorbed_ols_recovers_slope() -> None:
    rng = np.random.default_rng(4)
    grids = np.repeat(np.arange(80), 4)
    years = np.tile(np.arange(4), 80)
    province_year = (grids % 8) * 4 + years
    x = rng.normal(size=(grids.size, 2))
    y = 1.5 * x[:, 0] - 0.75 * x[:, 1] + (grids % 7) + 0.2 * province_year
    blocks = grids % 10
    fit = fit_absorbed_ols(
        y,
        x,
        grid_codes=grids,
        province_year_codes=province_year,
        cluster_codes=grids,
        block_codes=blocks,
        bootstrap_weights=rademacher_weights(99, 10),
    )
    np.testing.assert_allclose(fit.beta, [1.5, -0.75], atol=1e-10)
    assert fit.rank == 2
    assert fit.bootstrap_beta.shape == (99, 2)


def test_romano_wolf_and_holm_are_not_below_raw_p_values() -> None:
    estimates = np.array([1.0, 0.5, 0.1])
    rng = np.random.default_rng(2)
    draws = estimates + rng.normal(scale=0.4, size=(999, 3))
    raw, romano_wolf, holm = romano_wolf_stepdown(estimates, draws)
    assert np.all(romano_wolf >= raw)
    assert np.all(holm >= raw)
    assert np.all((romano_wolf >= 0) & (romano_wolf <= 1))
