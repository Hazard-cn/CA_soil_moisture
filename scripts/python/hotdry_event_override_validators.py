"""Override-run semantic checks without changing historical event validators."""

from __future__ import annotations

from typing import Any, Mapping

from hotdry_event_validators import (  # re-export the frozen row checks
    EventContractError,
    NAMED_ZONES,
    validate_event_panel,
    validate_event_run_manifest as validate_historical_manifest,
)


CANONICAL_ID = "compound-event-intensity-duration-override-v1"
REQUIRED_OVERRIDE_INPUT_ROLES = {
    "implementation_runner_original",
    "implementation_override_runner",
    "implementation_override_validators",
    "override_plan",
    "historical_smoke_review_round2_stop",
    "historical_stop_report",
    "test_stage1_runner",
    "test_override_runner",
}


def validate_override_manifest(
    manifest: Mapping[str, Any],
    shared_schema: Mapping[str, Any],
    *,
    extension: Mapping[str, Any] | None = None,
) -> None:
    """Validate shared/frozen semantics and close the override identity set.

    The historical validator is run on an in-memory alias of the canonical ID;
    no historical file or run is changed. Extra override roles are then required
    explicitly, including every test file executed for this run.
    """

    errors: list[str] = []
    if manifest.get("canonical_id") != CANONICAL_ID:
        errors.append(f"canonical_id must equal {CANONICAL_ID}")

    historical_alias = dict(manifest)
    historical_alias["canonical_id"] = "compound-event-intensity-duration-v1"
    try:
        validate_historical_manifest(
            historical_alias,
            shared_schema,
            extension=extension,
        )
    except EventContractError as error:
        errors.append(str(error))

    roles = {
        item.get("role")
        for item in manifest.get("inputs", [])
        if isinstance(item, Mapping)
    }
    missing = sorted(REQUIRED_OVERRIDE_INPUT_ROLES - roles)
    if missing:
        errors.append(f"override manifest missing identity roles: {missing}")
    duplicates = sorted(
        role for role in roles if sum(item.get("role") == role for item in manifest.get("inputs", [])) > 1
    )
    if duplicates:
        errors.append(f"override manifest contains duplicate roles: {duplicates}")

    if errors:
        raise EventContractError("\n".join(sorted(set(errors))))
