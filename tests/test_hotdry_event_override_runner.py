from __future__ import annotations

from pathlib import Path
import sys

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

import hotdry_event_override_validators as override_validators  # noqa: E402
from hotdry_event_override_validators import EventContractError  # noqa: E402
from run_hotdry_event_override_stage1 import implementation_paths  # noqa: E402


def test_override_input_roles_are_unique_and_identity_closed() -> None:
    paths = implementation_paths(
        Path("panel.dta"),
        tmax_dir=Path("tmax"),
        precip_dir=Path("precipitation"),
        smrz_dir=Path("smrz"),
    )
    roles = [role for role, _ in paths]
    assert len(roles) == len(set(roles))
    assert {
        "implementation_runner_original",
        "implementation_override_runner",
        "implementation_override_validators",
        "test_core",
        "test_validators",
        "test_stage1_runner",
        "test_override_runner",
        "override_plan",
        "historical_smoke_review_round2_stop",
        "historical_stop_report",
    }.issubset(roles)


def test_override_validator_rejects_missing_runner_test(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(override_validators, "validate_historical_manifest", lambda *args, **kwargs: None)
    roles = override_validators.REQUIRED_OVERRIDE_INPUT_ROLES - {"test_stage1_runner"}
    value = {
        "canonical_id": override_validators.CANONICAL_ID,
        "inputs": [{"role": role} for role in sorted(roles)],
    }
    with pytest.raises(EventContractError, match="test_stage1_runner"):
        override_validators.validate_override_manifest(value, {})


def test_override_validator_accepts_complete_override_roles(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(override_validators, "validate_historical_manifest", lambda *args, **kwargs: None)
    value = {
        "canonical_id": override_validators.CANONICAL_ID,
        "inputs": [
            {"role": role}
            for role in sorted(override_validators.REQUIRED_OVERRIDE_INPUT_ROLES)
        ],
    }
    override_validators.validate_override_manifest(value, {})
