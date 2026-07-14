from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

from hotdry_event_override_recovery import (  # noqa: E402
    build_recovery_risk_set,
    separated_day_cells,
)


def events() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"event_id": "a", "recovery_days": 0, "recovery_observed": True, "right_censored": False},
            {"event_id": "b", "recovery_days": 2, "recovery_observed": True, "right_censored": False},
            {"event_id": "c", "recovery_days": 2, "recovery_observed": False, "right_censored": True},
        ]
    )


def test_risk_set_has_one_row_per_at_risk_day() -> None:
    risk = build_recovery_risk_set(events())
    assert len(risk) == 7
    assert risk["recovered_now"].sum() == 2
    assert risk["censored_now"].sum() == 1
    assert risk.groupby("event_id")["follow_day"].max().to_dict() == {"a": 0, "b": 2, "c": 2}


def test_day_indicator_separation_is_detected() -> None:
    cells = separated_day_cells(build_recovery_risk_set(events()))
    assert any(cell["follow_day"] == 1 and cell["separation_type"] == "zero-censor" for cell in cells)


def test_incomplete_recovery_state_is_rejected() -> None:
    value = events()
    value.loc[0, "recovery_days"] = None
    with pytest.raises(ValueError, match="incomplete"):
        build_recovery_risk_set(value)
