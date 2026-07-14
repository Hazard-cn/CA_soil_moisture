"""Semantic validators for the preregistered hot-dry event direction.

JSON Schema validates one event-panel row and the shared run-manifest shape.
This module enforces the cross-record and direction-specific restrictions that
cannot be expressed in those shared contracts without changing their hashes.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import math
from typing import Any, Iterable, Mapping

import jsonschema


CANONICAL_ID = "compound-event-intensity-duration-v1"
NAMED_ZONES = ("NE", "HHH", "NW", "SW", "SH")
REQUIRED_EVENT_INPUT_ROLES = (
    "v3_panel",
    "zone_mapping",
    "tmax_2016",
    "precipitation_2016",
    "smrz_2016",
    "tmax_2017",
    "precipitation_2017",
    "smrz_2017",
    "tmax_2018",
    "precipitation_2018",
    "smrz_2018",
    "tmax_2019",
    "precipitation_2019",
    "smrz_2019",
    "implementation_core",
    "implementation_validators",
    "implementation_runner",
    "contract_event_panel",
    "contract_run_manifest",
    "frozen_design",
    "design_review_round2_pass",
    "test_core",
    "test_validators",
)
AGGREGATE_FIELDS = (
    "event_count",
    "total_duration_days",
    "longest_duration_days",
    "mean_event_intensity_c",
    "cumulative_excess_cday",
    "compound_share_of_heat_days",
    "window_start_doy",
    "window_end_doy",
    "window_total_days",
    "temp_valid_days",
    "pre_valid_days",
    "daily_complete_flag",
)


class EventContractError(ValueError):
    """Raised when a row set or manifest violates the frozen event contract."""


def _equal(left: Any, right: Any, *, atol: float = 1e-12) -> bool:
    if left is None or right is None:
        return left is right
    if isinstance(left, bool) or isinstance(right, bool):
        return left is right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=atol)
    return left == right


def validate_event_panel_semantics(records: Iterable[Mapping[str, Any]]) -> list[str]:
    """Return all cross-record event-panel violations in deterministic order."""

    rows = [dict(record) for record in records]
    errors: list[str] = []
    seen: set[tuple[str, int, int]] = set()
    groups: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)

    for row_number, row in enumerate(rows, start=1):
        key = (str(row["grid_id"]), int(row["year"]), int(row["event_seq"]))
        if key in seen:
            errors.append(f"duplicate key {key}")
        seen.add(key)
        groups[(key[0], key[1])].append(row)

        total_days = int(row["window_total_days"])
        expected_total = int(row["window_end_doy"]) - int(row["window_start_doy"]) + 1
        if total_days != expected_total:
            errors.append(f"row {row_number}: window_total_days != inclusive window length")
        expected_complete = (
            int(row["temp_valid_days"]) == total_days
            and int(row["pre_valid_days"]) == total_days
        )
        if bool(row["daily_complete_flag"]) != expected_complete:
            errors.append(f"row {row_number}: daily_complete_flag inconsistent with valid-day counts")

        if bool(row["event_indicator"]):
            if row["mean_event_intensity_c"] is None:
                errors.append(f"row {row_number}: event-positive mean intensity is null")
            if row["compound_share_of_heat_days"] is None:
                errors.append(f"row {row_number}: event-positive compound heat-day share is null")
            expected_duration = int(row["end_doy"]) - int(row["onset_doy"]) + 1
            if int(row["duration_days"]) != expected_duration:
                errors.append(f"row {row_number}: duration_days != end_doy-onset_doy+1")
            expected_event_id = f"{row['grid_id']}|{int(row['year']):04d}|{int(row['event_seq'])}"
            if row["event_id"] != expected_event_id:
                errors.append(f"row {row_number}: event_id serialization mismatch")
            if bool(row["sm_channel_complete_flag"]):
                expected_drawdown = float(row["antecedent_smrz"]) - float(row["event_min_smrz"])
                if not _equal(row["drawdown_smrz"], expected_drawdown):
                    errors.append(f"row {row_number}: drawdown_smrz identity mismatch")

    for (grid_id, year), group in sorted(groups.items()):
        label = f"{grid_id}|{year:04d}"
        representative_count = sum(bool(row["is_grid_year_representative"]) for row in group)
        if representative_count != 1:
            errors.append(f"{label}: expected exactly one representative row")

        event_flags = {bool(row["event_indicator"]) for row in group}
        if len(event_flags) != 1:
            errors.append(f"{label}: event_indicator differs within grid-year")
            continue
        event_positive = next(iter(event_flags))
        if not event_positive:
            if len(group) != 1 or int(group[0]["event_seq"]) != 0:
                errors.append(f"{label}: no-event grid-year must contain only event_seq=0")
            continue

        ordered = sorted(group, key=lambda row: int(row["event_seq"]))
        expected_sequence = list(range(1, len(ordered) + 1))
        actual_sequence = [int(row["event_seq"]) for row in ordered]
        if actual_sequence != expected_sequence:
            errors.append(f"{label}: event_seq is not consecutive from one")
        representative_sequences = [
            int(row["event_seq"])
            for row in ordered
            if bool(row["is_grid_year_representative"])
        ]
        if representative_sequences != [1]:
            errors.append(f"{label}: representative row must be event_seq=1")

        first = ordered[0]
        for field in AGGREGATE_FIELDS:
            if any(not _equal(row[field], first[field]) for row in ordered[1:]):
                errors.append(f"{label}: replicated aggregate {field} is inconsistent")

        if int(first["event_count"]) != len(ordered):
            errors.append(f"{label}: event_count != event row count")
        durations = [int(row["duration_days"]) for row in ordered]
        cumulatives = [float(row["event_cumulative_excess_cday"]) for row in ordered]
        total_duration = sum(durations)
        cumulative = sum(cumulatives)
        if int(first["total_duration_days"]) != total_duration:
            errors.append(f"{label}: total_duration_days != event duration sum")
        if int(first["longest_duration_days"]) != max(durations):
            errors.append(f"{label}: longest_duration_days != event duration maximum")
        if not _equal(first["cumulative_excess_cday"], cumulative):
            errors.append(f"{label}: cumulative_excess_cday != event cumulative sum")
        expected_mean = cumulative / total_duration
        if not _equal(first["mean_event_intensity_c"], expected_mean):
            errors.append(f"{label}: mean_event_intensity_c != cumulative/duration")

        for index, row in enumerate(ordered):
            next_onset = (
                int(ordered[index + 1]["onset_doy"])
                if index + 1 < len(ordered)
                else None
            )
            expected_overlap = bool(
                next_onset is not None
                and next_onset <= min(int(row["end_doy"]) + 3, int(row["window_end_doy"]))
            )
            if bool(row["drawdown_overlap_next_event"]) != expected_overlap:
                errors.append(f"{label}|{row['event_seq']}: drawdown overlap flag mismatch")

    return sorted(set(errors))


def validate_event_panel(
    records: Iterable[Mapping[str, Any]],
    schema: Mapping[str, Any],
) -> None:
    """Validate row schema and cross-record semantics, raising one exception."""

    rows = [dict(record) for record in records]
    validator = jsonschema.Draft202012Validator(dict(schema))
    errors: list[str] = []
    for row_number, row in enumerate(rows, start=1):
        for error in sorted(validator.iter_errors(row), key=lambda item: list(item.path)):
            errors.append(f"row {row_number} schema: {error.message}")
    errors.extend(validate_event_panel_semantics(rows))
    if errors:
        raise EventContractError("\n".join(errors))


def validate_event_run_manifest(
    manifest: Mapping[str, Any],
    shared_schema: Mapping[str, Any],
    *,
    extension: Mapping[str, Any] | None = None,
) -> None:
    """Validate the shared schema and event-direction semantic restrictions."""

    errors: list[str] = []
    validator = jsonschema.Draft202012Validator(dict(shared_schema), format_checker=jsonschema.FormatChecker())
    for error in sorted(validator.iter_errors(dict(manifest)), key=lambda item: list(item.path)):
        errors.append(f"shared schema: {error.message}")

    status = manifest.get("status")
    if manifest.get("canonical_id") != CANONICAL_ID:
        errors.append(f"canonical_id must equal {CANONICAL_ID}")
    if status in {"SMOKE", "STOP", "FAILED"} and manifest.get("not_for_inference") is not True:
        errors.append(f"{status} must set not_for_inference=true")

    for index, item in enumerate(manifest.get("inputs", [])):
        if not isinstance(item, Mapping) or not item.get("md5"):
            errors.append(f"input {index} must contain a non-null MD5")
        if not isinstance(item, Mapping) or not item.get("sha256"):
            errors.append(f"input {index} must contain SHA-256")
    input_roles = {
        item.get("role")
        for item in manifest.get("inputs", [])
        if isinstance(item, Mapping)
    }
    missing_roles = sorted(set(REQUIRED_EVENT_INPUT_ROLES) - input_roles)
    if missing_roles:
        errors.append(f"event manifest missing frozen input roles: {missing_roles}")

    if status in {"STOP", "FAILED"}:
        stop_rules = manifest.get("stop_rules_triggered")
        if not isinstance(stop_rules, list) or not stop_rules:
            errors.append(f"{status} must contain stop_rules_triggered")
        if manifest.get("claims") != []:
            errors.append(f"{status} must contain claims=[]")
        verification = manifest.get("verification")
        if not isinstance(verification, list) or not verification:
            errors.append(f"{status} must contain verification records")
        if not isinstance(extension, Mapping):
            errors.append(f"{status} requires an event run extension manifest")
        else:
            failure_stage = extension.get("failure_stage")
            failure_reasons = extension.get("failure_reasons")
            artifacts = extension.get("completed_artifacts")
            if not isinstance(failure_stage, str) or not failure_stage.strip():
                errors.append("event extension requires failure_stage")
            if not isinstance(failure_reasons, list) or not failure_reasons:
                errors.append("event extension requires failure_reasons")
            if not isinstance(artifacts, list) or not artifacts:
                errors.append("event extension requires completed_artifacts")
            else:
                for index, artifact in enumerate(artifacts):
                    if not isinstance(artifact, Mapping):
                        errors.append(f"completed artifact {index} must be an object")
                        continue
                    if not artifact.get("path"):
                        errors.append(f"completed artifact {index} requires path")
                    if not isinstance(artifact.get("bytes"), int) or artifact.get("bytes", -1) < 0:
                        errors.append(f"completed artifact {index} requires nonnegative bytes")
                    digest = artifact.get("sha256")
                    if not isinstance(digest, str) or len(digest) != 64:
                        errors.append(f"completed artifact {index} requires SHA-256")

    if status == "FULL":
        quantiles = manifest.get("ca_quantiles")
        if not isinstance(quantiles, Mapping) or any(
            key not in quantiles for key in ("p25", "p75", "population")
        ):
            errors.append("FULL requires frozen CA P25/P75 and population")
        endpoints = manifest.get("exposure_endpoints")
        if not isinstance(endpoints, Mapping):
            errors.append("FULL requires five-zone exposure endpoints")
        else:
            for zone in NAMED_ZONES:
                zone_value = endpoints.get(zone)
                if not isinstance(zone_value, Mapping):
                    errors.append(f"FULL exposure endpoints missing zone {zone}")
                    continue
                for exposure in ("duration", "intensity"):
                    value = zone_value.get(exposure)
                    if not isinstance(value, Mapping) or any(
                        key not in value for key in ("p50", "p90")
                    ):
                        errors.append(f"FULL endpoints missing {zone}.{exposure}.p50/p90")

    if errors:
        raise EventContractError("\n".join(sorted(set(errors))))
