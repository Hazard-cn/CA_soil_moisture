from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

from hotdry_event_override_recovery_v2 import (  # noqa: E402
    build_recovery_v2_risk,
    stabilized_ipcw,
)


def event(event_id: str, days: int, observed: bool, reason: str) -> dict[str, object]:
    return {
        "event_id": event_id,
        "recovery_days": days,
        "recovery_observed": observed,
        "right_censored": not observed,
        "censor_reason": reason,
    }


def test_day30_administrative_censor_is_not_random_censor_hazard() -> None:
    risk = build_recovery_v2_risk(
        pd.DataFrame([event("admin", 30, False, "thirty-day-limit")])
    )
    assert risk["follow_day"].tolist() == list(range(30))
    assert risk["early_censor"].sum() == 0


def test_early_next_event_censor_enters_hazard_once() -> None:
    risk = build_recovery_v2_risk(pd.DataFrame([event("early", 5, False, "next-event")]))
    assert risk["early_censor"].sum() == 1
    assert risk.loc[risk["early_censor"] == 1, "follow_day"].item() == 5


def test_recovery_is_not_coded_as_censoring() -> None:
    risk = build_recovery_v2_risk(pd.DataFrame([event("recovered", 2, True, "recovered")]))
    assert risk["recovered_now"].sum() == 1
    assert risk["early_censor"].sum() == 0


def test_stabilized_weights_use_eventwise_cumulative_product_and_clip() -> None:
    risk = pd.DataFrame({"event_id": ["a", "a", "b"], "row": [0, 1, 2]})
    numerator = np.array([0.1, 0.1, 0.1])
    denominator = np.array([0.2, 0.2, 0.2])
    weights, diagnostics = stabilized_ipcw(risk, numerator, denominator)
    ratio = 0.9 / 0.8
    raw = np.array([ratio, ratio**2, ratio])
    lower, upper = np.quantile(raw, [0.01, 0.99])
    np.testing.assert_allclose(weights, np.clip(raw, lower, upper))
    assert diagnostics["upper_p99"] == upper
