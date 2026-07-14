"""Round-1 recovery safeguards: L2 separation, standardization, and gradients."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "python"))

from hotdry_event_override_recovery_v2 import standardized_survival  # noqa: E402
from run_hotdry_event_override_recovery_v2 import fit_l2_censoring  # noqa: E402


def test_l2_censoring_is_finite_under_complete_separation() -> None:
    frame = pd.DataFrame({
        "early_censor": [0] * 10 + [1] * 10,
        "time": np.linspace(0, 1, 20),
        "separator": [0] * 10 + [1] * 10,
    })
    result, prediction = fit_l2_censoring("early_censor ~ time + separator", frame)
    assert np.isfinite(result.params).all()
    assert np.isfinite(prediction).all()
    assert ((prediction > 0) & (prediction < 1)).all()


def _fit_small_model():
    rng = np.random.default_rng(42)
    events = pd.DataFrame({
        "zone": np.repeat(["NE", "HHH"], 20),
        "year": np.tile(np.repeat([2016, 2017], 10), 2),
        "ca": rng.uniform(0.1, 0.8, 40),
        "antecedent_smrz": rng.normal(0.25, 0.03, 40),
        "duration_days": rng.integers(3, 8, 40),
        "event_mean_excess_c": rng.uniform(0.2, 3.0, 40),
        "onset_doy": rng.integers(150, 240, 40),
    })
    rows = []
    for event_id, row in events.iterrows():
        for day in range(5):
            hazard = 0.13 + 0.03 * day + 0.04 * (row.ca > 0.45)
            item = row.to_dict()
            item.update({
                "event_id": event_id,
                "follow_day": day,
                "time": day / 30.0,
                "time_sq": (day / 30.0) ** 2,
                "recovered_now": int(rng.uniform() < hazard),
            })
            rows.append(item)
    risk = pd.DataFrame(rows)
    formula = (
        "recovered_now ~ time + time_sq + C(zone) + C(year) + ca + ca:C(zone) "
        "+ antecedent_smrz + duration_days + event_mean_excess_c + onset_doy"
    )
    fit = smf.glm(
        formula, data=risk,
        family=sm.families.Binomial(link=sm.families.links.CLogLog()),
    ).fit()
    return events, fit


def test_standardized_curve_is_finite_bounded_and_nonincreasing() -> None:
    events, fit = _fit_small_model()
    curve, gradient, rmst, rmst_gradient = standardized_survival(
        fit.params.to_numpy(), fit.model.data.design_info, events[events.zone == "NE"], 0.4
    )
    assert curve.shape == (30,)
    assert gradient.shape == (30, len(fit.params))
    assert np.isfinite(curve).all() and np.isfinite(gradient).all()
    assert ((curve >= 0) & (curve <= 1)).all()
    assert (np.diff(curve) <= 1e-12).all()
    assert np.isclose(rmst, curve.sum())
    assert np.isfinite(rmst_gradient).all()


def test_rmst_analytic_gradient_matches_centered_finite_difference() -> None:
    events, fit = _fit_small_model()
    beta = fit.params.to_numpy(dtype=float)
    zone_events = events[events.zone == "HHH"]
    _, _, _, analytic = standardized_survival(
        beta, fit.model.data.design_info, zone_events, 0.55
    )
    eps = 1e-6
    for index in [0, 1, min(4, len(beta) - 1), len(beta) - 1]:
        plus = beta.copy(); plus[index] += eps
        minus = beta.copy(); minus[index] -= eps
        rmst_plus = standardized_survival(plus, fit.model.data.design_info, zone_events, 0.55)[2]
        rmst_minus = standardized_survival(minus, fit.model.data.design_info, zone_events, 0.55)[2]
        numerical = (rmst_plus - rmst_minus) / (2 * eps)
        assert np.isclose(analytic[index], numerical, rtol=2e-4, atol=2e-5)
