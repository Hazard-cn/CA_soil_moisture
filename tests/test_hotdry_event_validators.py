from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

from hotdry_event_validators import (  # noqa: E402
    EventContractError,
    REQUIRED_EVENT_INPUT_ROLES,
    validate_event_panel,
    validate_event_run_manifest,
)


EVENT_SCHEMA = json.loads(
    (PROJECT_ROOT / "docs" / "contracts" / "event_panel.schema.json").read_text(encoding="utf-8")
)
RUN_SCHEMA = json.loads(
    (PROJECT_ROOT / "docs" / "contracts" / "run_manifest.schema.json").read_text(encoding="utf-8")
)


def event_row(seq: int = 1, *, representative: bool = True) -> dict[str, object]:
    onset = 100 + (seq - 1) * 6
    return {
        "contract_version": "event-panel-v1",
        "grid_id": "123",
        "year": 2018,
        "zone": "HHH",
        "latitude": 35.05,
        "longitude": 114.05,
        "event_seq": seq,
        "event_id": f"123|2018|{seq}",
        "event_indicator": True,
        "is_grid_year_representative": representative,
        "window_start_doy": 70,
        "window_end_doy": 180,
        "window_total_days": 111,
        "temp_valid_days": 111,
        "pre_valid_days": 111,
        "daily_complete_flag": True,
        "event_count": 1,
        "total_duration_days": 3,
        "longest_duration_days": 3,
        "mean_event_intensity_c": 2.0,
        "cumulative_excess_cday": 6.0,
        "compound_share_of_heat_days": 0.5,
        "onset_doy": onset,
        "end_doy": onset + 2,
        "duration_days": 3,
        "event_mean_excess_c": 2.0,
        "event_cumulative_excess_cday": 6.0,
        "antecedent_smrz": 0.30,
        "antecedent_valid_days": 14,
        "sm_channel_complete_flag": True,
        "event_min_smrz": 0.20,
        "drawdown_smrz": 0.10,
        "drawdown_overlap_next_event": False,
        "recovery_days": 5,
        "recovery_observed": True,
        "right_censored": False,
        "censor_reason": "recovered",
    }


def no_event_row() -> dict[str, object]:
    row = event_row()
    row.update(
        {
            "event_seq": 0,
            "event_id": None,
            "event_indicator": False,
            "event_count": 0,
            "total_duration_days": 0,
            "longest_duration_days": 0,
            "mean_event_intensity_c": 0,
            "cumulative_excess_cday": 0,
            "compound_share_of_heat_days": None,
            "onset_doy": None,
            "end_doy": None,
            "duration_days": None,
            "event_mean_excess_c": None,
            "event_cumulative_excess_cday": None,
            "antecedent_smrz": None,
            "antecedent_valid_days": None,
            "sm_channel_complete_flag": None,
            "event_min_smrz": None,
            "drawdown_smrz": None,
            "drawdown_overlap_next_event": None,
            "recovery_days": None,
            "recovery_observed": None,
            "right_censored": None,
            "censor_reason": None,
        }
    )
    return row


def two_event_rows() -> list[dict[str, object]]:
    first = event_row(1, representative=True)
    second = event_row(2, representative=False)
    for row in (first, second):
        row.update(
            {
                "event_count": 2,
                "total_duration_days": 6,
                "longest_duration_days": 3,
                "mean_event_intensity_c": 2.0,
                "cumulative_excess_cday": 12.0,
            }
        )
    return [first, second]


def manifest(status: str = "SMOKE") -> dict[str, object]:
    return {
        "contract_version": "run-manifest-v1",
        "canonical_id": "compound-event-intensity-duration-v1",
        "run_id": "fixture",
        "created_utc": "2026-07-15T00:00:00+00:00",
        "status": status,
        "not_for_inference": status in {"SMOKE", "STOP", "FAILED"},
        "design_version": "v2",
        "git_commit": "3da8a12f94c04f7d19b6153bb1691787340ba4a8",
        "data_family": "V3",
        "inputs": [
            {
                "role": role,
                "path": f"{role}.fixture",
                "bytes": 1,
                "md5": "0" * 32,
                "sha256": "0" * 64,
            }
            for role in REQUIRED_EVENT_INPUT_ROLES
        ],
        "sample_predicate": "fixture",
        "sample_key_serialization": "grid_id|year",
        "sample_key_sha256": "1" * 64,
        "outcome": "ln_yield",
        "exposure_definition": "Tmax>=32 and pre<1 for >=3 consecutive days",
        "fixed_effects": ["grid", "province-year"],
        "inference": {
            "primary": "not run in smoke",
            "bootstrap_reps": 0,
            "spatial_block_degrees": 2,
            "multiplicity": "not run in smoke",
        },
        "seed": 42,
        "claims": [],
        "stop_rules_triggered": [],
        "verification": [{"check": "fixture", "status": "PASS", "detail": None}],
    }


def failure_extension() -> dict[str, object]:
    return {
        "failure_stage": "stage1_support",
        "failure_reasons": ["fixture stop"],
        "completed_artifacts": [
            {"path": "support.csv", "bytes": 1, "sha256": "2" * 64}
        ],
    }


def test_valid_no_event_and_two_event_panels() -> None:
    validate_event_panel([no_event_row()], EVENT_SCHEMA)
    validate_event_panel(two_event_rows(), EVENT_SCHEMA)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda rows: rows.append(deepcopy(rows[0])), "duplicate key"),
        (lambda rows: rows[1].update(event_seq=3, event_id="123|2018|3"), "not consecutive"),
        (lambda rows: rows[0].update(is_grid_year_representative=False), "exactly one representative"),
        (lambda rows: rows[0].update(event_count=3), "event_count"),
        (lambda rows: rows[1].update(total_duration_days=9), "replicated aggregate"),
        (lambda rows: rows[0].update(duration_days=4), "end_doy-onset_doy"),
        (lambda rows: rows[0].update(event_id="wrong|2018|1"), "event_id serialization"),
        (lambda rows: rows[0].update(cumulative_excess_cday=13.0), "cumulative_excess"),
        (lambda rows: rows[0].update(longest_duration_days=4), "longest_duration"),
    ],
)
def test_cross_record_counterexamples_are_rejected(mutation, message: str) -> None:
    rows = two_event_rows()
    mutation(rows)
    with pytest.raises(EventContractError, match=message):
        validate_event_panel(rows, EVENT_SCHEMA)


def test_event_positive_intensity_and_share_cannot_be_null() -> None:
    for field in ("mean_event_intensity_c", "compound_share_of_heat_days"):
        row = event_row()
        row[field] = None
        with pytest.raises(EventContractError):
            validate_event_panel([row], EVENT_SCHEMA)


def test_daily_complete_must_match_valid_days() -> None:
    row = no_event_row()
    row["temp_valid_days"] = 110
    with pytest.raises(EventContractError, match="daily_complete_flag"):
        validate_event_panel([row], EVENT_SCHEMA)


def test_drawdown_overlap_flag_is_cross_record_checked() -> None:
    rows = two_event_rows()
    rows[1]["onset_doy"] = 105
    rows[1]["end_doy"] = 107
    rows[0]["drawdown_overlap_next_event"] = False
    with pytest.raises(EventContractError, match="overlap flag"):
        validate_event_panel(rows, EVENT_SCHEMA)


def test_sm_recovery_state_counterexample_is_rejected() -> None:
    row = event_row()
    row.update(recovery_observed=False, right_censored=False, censor_reason=None)
    with pytest.raises(EventContractError):
        validate_event_panel([row], EVENT_SCHEMA)


def test_sm_censored_state_with_ma_end_is_valid() -> None:
    row = event_row()
    row.update(recovery_days=3, recovery_observed=False, right_censored=True, censor_reason="ma-end")
    validate_event_panel([row], EVENT_SCHEMA)


def test_sm_insufficient_state_is_valid() -> None:
    row = event_row()
    row.update(
        antecedent_smrz=None,
        antecedent_valid_days=13,
        sm_channel_complete_flag=False,
        event_min_smrz=0.2,
        drawdown_smrz=None,
        recovery_days=None,
        recovery_observed=None,
        right_censored=None,
        censor_reason="insufficient-sm",
    )
    validate_event_panel([row], EVENT_SCHEMA)


def test_valid_smoke_manifest() -> None:
    validate_event_run_manifest(manifest(), RUN_SCHEMA)


def test_smoke_must_be_not_for_inference() -> None:
    value = manifest()
    value["not_for_inference"] = False
    with pytest.raises(EventContractError, match="not_for_inference"):
        validate_event_run_manifest(value, RUN_SCHEMA)


def test_every_input_requires_md5() -> None:
    value = manifest()
    value["inputs"][0]["md5"] = None  # type: ignore[index]
    with pytest.raises(EventContractError, match="MD5"):
        validate_event_run_manifest(value, RUN_SCHEMA)


def test_manifest_requires_implementation_identity_inputs() -> None:
    value = manifest()
    value["inputs"] = [  # type: ignore[index]
        item
        for item in value["inputs"]  # type: ignore[index]
        if item["role"] != "implementation_runner"
    ]
    with pytest.raises(EventContractError, match="implementation_runner"):
        validate_event_run_manifest(value, RUN_SCHEMA)


def test_stop_manifest_requires_failure_semantics_and_extension() -> None:
    value = manifest("STOP")
    with pytest.raises(EventContractError, match="stop_rules_triggered"):
        validate_event_run_manifest(value, RUN_SCHEMA)
    value["stop_rules_triggered"] = ["fixture stop"]
    with pytest.raises(EventContractError, match="extension"):
        validate_event_run_manifest(value, RUN_SCHEMA)
    validate_event_run_manifest(value, RUN_SCHEMA, extension=failure_extension())


def test_stop_manifest_forbids_claims_and_empty_verification() -> None:
    value = manifest("STOP")
    value["stop_rules_triggered"] = ["fixture stop"]
    value["claims"] = ["claim"]
    value["verification"] = []
    with pytest.raises(EventContractError, match="claims"):
        validate_event_run_manifest(value, RUN_SCHEMA, extension=failure_extension())


def test_full_manifest_requires_frozen_endpoints() -> None:
    value = manifest("FULL")
    with pytest.raises(EventContractError, match="CA P25/P75"):
        validate_event_run_manifest(value, RUN_SCHEMA)
    value["ca_quantiles"] = {"p25": 0.1, "p75": 0.4, "population": "common sample"}
    value["exposure_endpoints"] = {
        zone: {
            "duration": {"p50": 0.0, "p90": 7.0},
            "intensity": {"p50": 0.0, "p90": 2.0},
        }
        for zone in ("NE", "HHH", "NW", "SW", "SH")
    }
    validate_event_run_manifest(value, RUN_SCHEMA)
