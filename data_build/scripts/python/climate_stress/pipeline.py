"""DAG orchestration for the climate-stress panel build.

Every concrete stage is published through :mod:`climate_stress.runtime`.  A
failed or unavailable stage retains its unique partial directory and never
receives a success marker.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import traceback
import uuid
from contextlib import ExitStack
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence, TextIO

import numpy as np
import pandas as pd

from .config import PipelineConfig, load_config
from .core import SPEI_2W_PENDING_STATUS
from .runtime import (
    PathOutsideRunError,
    RunLock,
    RunContext,
    STAGE_SUCCESS,
    StageSession,
    atomic_output,
    complete_stage,
    ensure_within_run,
    exclusive_run_lock,
    initialize_run,
    parameter_signature,
    process_memory_snapshot,
    sha256_file,
    sha256_path,
    stage_resource_usage,
    start_stage,
    utc_now,
)


STAGE_ORDER = (
    "assets",
    "grid",
    "phenology",
    "era_daily",
    "era_baseline",
    "spei",
    "gleam_daily",
    "gleam_baseline",
    "events",
    "aggregate",
    "export",
    "validate",
)

STAGE_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "assets": (),
    "grid": ("assets",),
    "phenology": ("grid",),
    "era_daily": ("grid",),
    "era_baseline": ("era_daily",),
    "spei": ("grid", "phenology"),
    "gleam_daily": ("grid",),
    "gleam_baseline": ("grid", "gleam_daily"),
    "events": (
        "grid",
        "phenology",
        "era_daily",
        "era_baseline",
        "spei",
        "gleam_daily",
        "gleam_baseline",
    ),
    "aggregate": (
        "grid",
        "phenology",
        "era_daily",
        "era_baseline",
        "spei",
        "gleam_daily",
        "gleam_baseline",
        "events",
    ),
    "export": ("aggregate",),
    "validate": ("spei", "export"),
}

CLI_STAGES = (*STAGE_ORDER, "all")
RANDOM_SEED = 42
PILOT_YEARS = (2010, 2016, 2019)
PILOT_CELLS = 100
STAGE_START = "_START.json"
PARTITION_RESUMABLE_STAGES = frozenset(
    {"era_daily", "spei", "gleam_daily", "gleam_baseline", "events", "aggregate"}
)


class StageUnavailableError(RuntimeError):
    """Raised when a planned stage adapter has not been implemented yet."""


class StageValidationError(RuntimeError):
    """Raised when a stage creates evidence that does not pass its gate."""


class StageResourceBudgetError(StageValidationError):
    """Raised before publication when process peak RSS exceeds the mode budget."""


class StageAttemptAuditError(RuntimeError):
    """Raised when a global or partial stage-failure record cannot publish."""

    def __init__(
        self,
        phase: str,
        audit_error: BaseException,
        *,
        published_audit_path: Path | None,
    ) -> None:
        super().__init__(
            f"{phase} persistence failed: {type(audit_error).__name__}: "
            f"{audit_error}"
        )
        self.phase = phase
        self.audit_error = audit_error
        self.published_audit_path = published_audit_path


@dataclass(frozen=True)
class InvocationAuditIssue:
    phase: str
    error: BaseException
    published_audit_path: Path | None = None

    def as_payload(self) -> dict[str, Any]:
        exception = _exception_payload(self.error) or {}
        return {
            "phase": self.phase,
            "error": {
                "type": exception.get("type", "BaseException"),
                "message": exception.get(
                    "message",
                    "<exception message unavailable>",
                ),
            },
            "published_audit_path": (
                None
                if self.published_audit_path is None
                else str(self.published_audit_path)
            ),
        }


@dataclass(frozen=True)
class ExecutionScope:
    mode: str
    years: tuple[int, ...]
    pilot_cells: int | None
    hash_mode: str
    random_seed: int = RANDOM_SEED

    @property
    def is_pilot(self) -> bool:
        return self.mode == "pilot"

    def as_parameters(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "years": list(self.years),
            "pilot_cells": self.pilot_cells,
            "hash_mode": self.hash_mode,
            "random_seed": self.random_seed,
        }


@dataclass
class StageOutcome:
    artifacts: dict[str, Path] = field(default_factory=dict)
    row_counts: dict[str, int] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StageRequest:
    pipeline: "ClimateStressPipeline"
    session: StageSession

    @property
    def stage(self) -> str:
        return self.session.stage

    @property
    def config(self) -> PipelineConfig:
        return self.pipeline.config

    @property
    def context(self) -> RunContext:
        return self.pipeline.context

    @property
    def scope(self) -> ExecutionScope:
        return self.pipeline.scope

    @property
    def work_dir(self) -> Path:
        return self.session.work_dir

    def dependency_dir(self, stage: str) -> Path:
        if stage not in STAGE_DEPENDENCIES[self.stage]:
            raise ValueError(f"{stage} is not a direct dependency of {self.stage}")
        path = self.context.stages_dir / stage
        if not (path / "_SUCCESS.json").is_file():
            raise FileNotFoundError(f"Dependency {stage} is not complete: {path}")
        return path


StageHandler = Callable[[StageRequest], StageOutcome]


def parse_years(value: str) -> tuple[int, ...]:
    """Parse comma-separated years and inclusive ``start-end`` ranges."""

    years: list[int] = []
    for raw_part in value.split(","):
        part = raw_part.strip()
        if not part:
            continue
        if "-" in part:
            pieces = part.split("-", 1)
            if len(pieces) != 2:
                raise argparse.ArgumentTypeError(f"Invalid year range: {part}")
            try:
                start, end = (int(piece) for piece in pieces)
            except ValueError as exc:
                raise argparse.ArgumentTypeError(f"Invalid year range: {part}") from exc
            if end < start:
                raise argparse.ArgumentTypeError(f"Descending year range: {part}")
            years.extend(range(start, end + 1))
        else:
            try:
                years.append(int(part))
            except ValueError as exc:
                raise argparse.ArgumentTypeError(f"Invalid year: {part}") from exc
    if not years or len(years) != len(set(years)):
        raise argparse.ArgumentTypeError("Years must be non-empty and unique")
    return tuple(sorted(years))


def resolve_scope(
    config: PipelineConfig,
    *,
    pilot_cells: int | None,
    years: Sequence[int] | None,
    hash_mode: str | None,
) -> ExecutionScope:
    configured_target = tuple(config.target_years)
    configured_pilot_years = tuple(
        int(value) for value in config.data["quality"].get("pilot_years", PILOT_YEARS)
    )
    configured_pilot_cells = int(
        config.data["quality"].get("pilot_grid_limit", PILOT_CELLS)
    )
    if pilot_cells is not None:
        if int(pilot_cells) != configured_pilot_cells:
            raise ValueError(
                f"Pilot is frozen at {configured_pilot_cells} cells, received {pilot_cells}"
            )
        selected_years = tuple(int(value) for value in (years or configured_pilot_years))
        if selected_years != configured_pilot_years:
            raise ValueError(
                f"Pilot years are frozen at {configured_pilot_years}, received {selected_years}"
            )
        return ExecutionScope(
            "pilot",
            selected_years,
            configured_pilot_cells,
            hash_mode or "pilot",
        )
    selected_years = tuple(int(value) for value in (years or configured_target))
    if selected_years != configured_target:
        raise ValueError(
            f"Full run years are frozen at {configured_target}, received {selected_years}"
        )
    return ExecutionScope("full", selected_years, None, hash_mode or "full")


def dependency_closure(stage: str) -> tuple[str, ...]:
    if stage == "all":
        return STAGE_ORDER
    if stage not in STAGE_DEPENDENCIES:
        raise ValueError(f"Unknown stage: {stage}")
    required: set[str] = set()

    def visit(name: str) -> None:
        for dependency in STAGE_DEPENDENCIES[name]:
            visit(dependency)
        required.add(name)

    visit(stage)
    return tuple(name for name in STAGE_ORDER if name in required)


def _contiguous_year_groups(years: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    """Split sorted years so period-index event detectors receive hard gaps."""

    ordered = tuple(sorted(int(value) for value in years))
    if not ordered or len(ordered) != len(set(ordered)):
        raise ValueError("years must be a non-empty unique sequence")
    groups: list[list[int]] = [[ordered[0]]]
    for year in ordered[1:]:
        if year == groups[-1][-1] + 1:
            groups[-1].append(year)
        else:
            groups.append([year])
    return tuple(tuple(group) for group in groups)


def _event_context_years(config: PipelineConfig) -> tuple[int, ...]:
    """Return the continuous source sequence used for event detection only."""

    configured = config.data.get("years", {}).get("event_context")
    if isinstance(configured, Mapping):
        start = int(configured["start"])
        end = int(configured["end"])
        years = tuple(range(start, end + 1))
    elif configured is not None:
        years = tuple(sorted(int(value) for value in configured))
    else:
        start = min(int(value) for value in config.historical_years)
        end = max(int(value) for value in config.target_years) + 1
        years = tuple(range(start, end + 1))
    if not years or len(years) != len(set(years)):
        raise ValueError("years.event_context must be non-empty and unique")
    if any(right != left + 1 for left, right in zip(years, years[1:])):
        raise ValueError("years.event_context must be a continuous annual sequence")
    required_start = min(int(value) for value in config.historical_years)
    required_end = max(int(value) for value in config.target_years) + 1
    if years[0] > required_start or years[-1] < required_end:
        raise ValueError(
            "years.event_context must cover the historical baseline through one "
            "year after the final output year"
        )
    return years


def _event_overlaps_output_years(
    start: date,
    end: date,
    output_years: Sequence[int],
) -> bool:
    return any(
        end >= date(int(year), 1, 1) and start <= date(int(year), 12, 31)
        for year in output_years
    )


def _source_censor_flags(
    dates: Sequence[date],
    valid: np.ndarray,
    *,
    start: date,
    end: date,
) -> tuple[bool, bool]:
    """Flag events touching the first/last valid source support for one cell."""

    values = np.asarray(valid, dtype=bool)
    if values.ndim != 1 or len(values) != len(dates):
        raise ValueError("Source-censor validity must be one-dimensional")
    positions = {value: index for index, value in enumerate(dates)}
    start_index = positions[start]
    end_index = positions[end]
    return (
        not bool(values[:start_index].any()),
        not bool(values[end_index + 1 :].any()),
    )


def _write_json_new(path: Path, payload: Mapping[str, Any]) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2),
        encoding="utf-8",
    )


def _write_json_atomic_new(
    path: Path,
    payload: Mapping[str, Any],
    *,
    evidence_root: Path,
) -> None:
    """Atomically publish one immutable invocation record below its evidence root."""

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ).encode("utf-8")
    with atomic_output(path, evidence_root) as partial:
        with partial.open("xb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())


def _initialization_evidence_root(
    config: PipelineConfig,
    *,
    run_id: str,
    invocation_id: str,
    exc: BaseException,
) -> tuple[Path, str]:
    """Choose an existing run, its incomplete init tree, or a safe fallback."""

    output_root = config.output_root.resolve(strict=False)
    run_root = (output_root / run_id).resolve(strict=False)
    try:
        relative_run_root = run_root.relative_to(output_root)
    except ValueError:
        relative_run_root = None
    audit_root = (run_root / "audit").resolve(strict=False)
    try:
        relative_audit_root = audit_root.relative_to(run_root)
    except ValueError:
        relative_audit_root = None
    if (
        relative_run_root is not None
        and relative_run_root.parts == (run_id,)
        and relative_audit_root is not None
        and relative_audit_root.parts == ("audit",)
        and run_root.is_dir()
        and audit_root.is_dir()
    ):
        return run_root, "existing_run"

    attached = getattr(exc, "initialization_audit_context", {})
    raw_evidence = (
        attached.get("initialization_evidence_dir")
        if isinstance(attached, Mapping)
        else None
    )
    if raw_evidence:
        candidate: Path | None = Path(str(raw_evidence)).resolve(strict=False)
        try:
            relative_candidate = candidate.relative_to(output_root)
        except ValueError:
            candidate = None
        else:
            expected_prefix = f".{run_id}.{invocation_id}."
            if (
                len(relative_candidate.parts) != 1
                or not candidate.name.startswith(expected_prefix)
                or not candidate.name.endswith(".initializing.incomplete")
            ):
                candidate = None
        if candidate is not None and candidate.is_dir():
            return candidate, "initialization_incomplete"

    fallback = (output_root / ".run-invocations" / run_id / invocation_id).resolve(
        strict=False
    )
    relative_fallback = fallback.relative_to(output_root)
    if relative_fallback.parts != (".run-invocations", run_id, invocation_id):
        raise PathOutsideRunError(
            "Resolved initialization fallback is not the dedicated audit path: "
            f"{fallback}"
        )
    fallback.mkdir(parents=True, exist_ok=False)
    return fallback, "output_root_fallback"


@dataclass(frozen=True)
class InitializationFailureEvidence:
    evidence_root: Path
    evidence_location: str
    failure_path: Path
    quality_path: Path
    quality_payload: dict[str, Any]


@dataclass(frozen=True)
class PreparedQualitySummary:
    """Immutable invocation payload frozen while the run lease is held."""

    target: Path
    evidence_root: Path
    payload: dict[str, Any]


def _snapshot_quality_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Detach a JSON-safe deep snapshot from mutable pipeline state."""

    return json.loads(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            allow_nan=False,
        )
    )


def _write_initialization_failure_records(
    config: PipelineConfig,
    scope: "ExecutionScope",
    *,
    run_id: str,
    requested_stage: str,
    resume: bool,
    invocation_id: str,
    invocation_started_at_utc: str,
    initialization_started_at_utc: str,
    lease: RunLock,
    exc: BaseException,
    exit_status: int = 2,
) -> InitializationFailureEvidence:
    """Persist the failure record and defer the unique summary until release."""

    evidence_root, evidence_location = _initialization_evidence_root(
        config,
        run_id=run_id,
        invocation_id=invocation_id,
        exc=exc,
    )
    audit_root = evidence_root / "audit"
    failure_path = (
        audit_root
        / "initialization_failures"
        / f"initialization_failure.{invocation_id}.json"
    )
    quality_path = (
        audit_root
        / "quality_summaries"
        / f"run_quality_summary.{invocation_id}.json"
    )
    failed_at = utc_now()
    acquired_name = f"{run_id}.acquired.{lease.lease_id}.json"
    released_name = f"{run_id}.released.{lease.lease_id}.json"
    lock_root = lease.path.parent
    output_root = config.output_root.resolve(strict=False)
    acquired_path = lock_root / acquired_name
    released_path = lock_root / released_name
    lease_record = {
        "lease_id": lease.lease_id,
        "owner": lease.metadata.get("owner"),
        "pid": lease.metadata.get("pid"),
        "hostname": lease.metadata.get("hostname"),
        "acquired_at_utc": lease.metadata.get("acquired_at_utc"),
        "acquired_audit": acquired_path.relative_to(output_root).as_posix(),
        "release_audit_expected": released_path.relative_to(output_root).as_posix(),
        "release_occurs_after_failure_record": True,
    }
    initialization_context = getattr(exc, "initialization_audit_context", {})
    if not isinstance(initialization_context, Mapping):
        initialization_context = {}
    requested_signatures = dict(
        initialization_context.get("requested_signatures", {})
    )
    exception_record = _exception_payload(exc) or {}
    scope_parameters = scope.as_parameters()
    common = {
        "schema_version": 1,
        "invocation_id": invocation_id,
        "run_id": run_id,
        "requested_stage": requested_stage,
        "requested_scope": scope_parameters,
        "resume": bool(resume),
        "failure_phase": "INITIALIZE_RUN",
        "execution_status": "FAILED",
        "invocation_status": "FAILED",
        "stage_execution_status": "NOT_STARTED",
        "exit_status": int(exit_status),
        "scope_profile": config.scope_profile,
        "completion_scope_status": config.completion_scope_status,
        "invocation_started_at_utc": invocation_started_at_utc,
        "initialization_started_at_utc": initialization_started_at_utc,
        "failed_at_utc": failed_at,
        "evidence_written_at_utc": failed_at,
        "config_sha256": config.sha256,
        "template_config_sha256": config.template_sha256 or config.sha256,
        "effective_config_sha256": config.sha256,
        "code_git_commit": initialization_context.get("code_git_commit"),
        "parameter_sha256": parameter_signature(scope_parameters),
        "source_tree_sha256": requested_signatures.get("source_tree_sha256"),
        "environment_sha256": requested_signatures.get("environment_sha256"),
        "requested_signatures": requested_signatures,
        "observed_signatures": dict(
            initialization_context.get("observed_signatures", {})
        ),
        "initialization_evidence_dir": initialization_context.get(
            "initialization_evidence_dir"
        ),
        "evidence_location": evidence_location,
        "lease": lease_record,
        "exception": exception_record,
        "stage_attempt_created": False,
        "stage_partial_created": False,
        "capture_mode": "automatic_runtime",
        "retrospective": False,
    }
    _write_json_atomic_new(
        failure_path,
        common,
        evidence_root=evidence_root,
    )
    quality_payload = {
        **common,
        "status": config.completion_scope_status,
        "spei_2w_numeric_enabled": bool(
            config.data["scope"]["spei_2w_numeric"]
        ),
        "spei_2w_output_enabled": bool(
            config.data["scope"]["spei_2w_output"]
        ),
        "spei_2w_numeric_executed": False,
        "spei_2w_output_included": False,
        "compound_mode": str(config.data["scope"]["compound_mode"]),
        "created_at_utc": failed_at,
        "resolved_paths": config.resolved_paths(),
        "parameters": {
            "run": scope_parameters,
            "stage": {"stage": requested_stage, **scope_parameters},
        },
        "stages": [],
        "initialization_failure_audit": failure_path.relative_to(
            evidence_root
        ).as_posix(),
    }
    return InitializationFailureEvidence(
        evidence_root=evidence_root,
        evidence_location=evidence_location,
        failure_path=failure_path,
        quality_path=quality_path,
        quality_payload=quality_payload,
    )


def _initialization_exit_status(exc: BaseException) -> int:
    """Return a non-success process status for an incomplete invocation."""

    if isinstance(exc, KeyboardInterrupt):
        return 130
    if isinstance(exc, SystemExit):
        if exc.code is None or exc.code == 0:
            return 2
        return int(exc.code) if isinstance(exc.code, int) else 1
    return 2 if isinstance(exc, Exception) else 1


def _normalize_incomplete_exit_status(exc: BaseException) -> int:
    """Prevent an unfinished initialization or stage from exiting successfully."""

    status = _initialization_exit_status(exc)
    if isinstance(exc, SystemExit) and (exc.code is None or exc.code == 0):
        exc.code = status
    return status


def _annotate_failure_phase(exc: BaseException, phase: str) -> None:
    """Attach a stable phase label without changing the active exception."""

    try:
        if not getattr(exc, "failure_phase", None):
            setattr(exc, "failure_phase", phase)
    except (AttributeError, TypeError):
        pass


def _add_note_without_masking(exc: BaseException, note: str) -> None:
    """Best-effort exception annotation that can never replace the cause."""

    try:
        exc.add_note(note)
    except BaseException:
        pass


def _safe_exception_description(exc: BaseException) -> str:
    """Describe an exception without trusting its potentially hostile __str__."""

    try:
        name = type(exc).__name__
    except BaseException:
        name = "BaseException"
    try:
        message = str(exc)
    except BaseException:
        message = "<exception message unavailable>"
    try:
        return f"{name}: {message}"
    except BaseException:
        return "BaseException: <exception description unavailable>"


def _report_audit_failure(
    *,
    errors: TextIO,
    original: BaseException,
    phase: str,
    audit_error: BaseException,
) -> None:
    """Expose an audit-write failure without replacing the active exception."""

    try:
        warning = (
            f"{phase} audit persistence failed; durable evidence is absent or "
            "incomplete and must not be treated as a completed audit; preserving "
            f"{_safe_exception_description(original)}; audit_error="
            f"{_safe_exception_description(audit_error)}"
        )
    except BaseException:
        return
    _add_note_without_masking(original, warning)
    _emit_warning_without_masking(
        errors,
        f"AUDIT_WARNING: {warning}",
        original=original,
    )


def _emit_warning_without_masking(
    errors: TextIO,
    message: str,
    *,
    original: BaseException,
) -> None:
    """Report an audit warning without letting the reporter replace the cause."""

    try:
        print(message, file=errors)
    except BaseException as reporting_error:
        reporting_note = (
            "Failed to emit the audit warning while preserving the active "
            f"{_safe_exception_description(original)}; reporter_error="
            f"{_safe_exception_description(reporting_error)}"
        )
        _add_note_without_masking(original, reporting_note)
        fallback = sys.__stderr__
        if fallback is None or fallback is errors:
            return
        try:
            print(f"AUDIT_WARNING: {reporting_note}", file=fallback)
        except BaseException as fallback_error:
            _add_note_without_masking(
                original,
                "Failed to emit the fallback audit warning: "
                f"{_safe_exception_description(fallback_error)}"
            )


def _exception_payload(exc: BaseException | None) -> dict[str, Any] | None:
    if exc is None:
        return None
    try:
        exception_type = type(exc).__name__
    except BaseException:
        exception_type = "BaseException"
    try:
        message = str(exc)
    except BaseException:
        message = "<exception message unavailable>"
    try:
        formatted_traceback = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )
    except BaseException:
        formatted_traceback = "<traceback unavailable>"
    return {
        "type": exception_type,
        "message": message,
        "traceback": formatted_traceback,
    }


def _lease_quality_record(
    lease: RunLock,
    output_root: Path,
) -> dict[str, Any]:
    lock_root = lease.path.parent
    acquired = lock_root / (
        f"{lease.metadata['run_id']}.acquired.{lease.lease_id}.json"
    )
    released = lock_root / (
        f"{lease.metadata['run_id']}.released.{lease.lease_id}.json"
    )
    os_lease_terminal = bool(
        lease.os_unlock_succeeded and lease.handle_closed
    )
    return {
        "lease_id": lease.lease_id,
        "owner": lease.metadata.get("owner"),
        "pid": lease.metadata.get("pid"),
        "hostname": lease.metadata.get("hostname"),
        "acquired_at_utc": lease.metadata.get("acquired_at_utc"),
        "release_attempted_at_utc": lease.release_attempted_at_utc,
        "release_terminal_at_utc": lease.release_terminal_at_utc,
        "released_at_utc": lease.released_at_utc,
        "release_attempted": bool(lease.release_attempted),
        "released": bool(lease.released),
        "release_workflow_succeeded": bool(lease.released),
        "os_lease_terminal": os_lease_terminal,
        "release_audit_persisted": lease.release_audit_persisted,
        "release_timestamp_recorded": lease.release_timestamp_recorded,
        "os_unlock_succeeded": lease.os_unlock_succeeded,
        "handle_closed": lease.handle_closed,
        "acquired_audit": acquired.relative_to(output_root).as_posix(),
        "release_audit_expected": released.relative_to(output_root).as_posix(),
        "release_audit_present": released.is_file(),
    }


def _report_release_failure(
    *,
    errors: TextIO,
    primary: BaseException,
    release_error: BaseException,
) -> None:
    try:
        warning = (
            "run-lock release evidence or unlock failed; durable lease evidence is "
            "absent or incomplete; preserving "
            f"{_safe_exception_description(primary)}; release_error="
            f"{_safe_exception_description(release_error)}"
        )
    except BaseException:
        return
    _add_note_without_masking(primary, warning)
    _emit_warning_without_masking(
        errors,
        f"AUDIT_WARNING: {warning}",
        original=primary,
    )


def _publish_quality_summary(
    prepared: PreparedQualitySummary,
    *,
    invocation_status: str,
    stage_execution_status: str,
    failure_phase: str | None,
    primary_exception: BaseException | None,
    release_exception: BaseException | None,
    exit_status: int,
    lease: RunLock,
    output_root: Path,
) -> Path:
    """Add lease terminal state and publish one no-overwrite summary."""

    authoritative = primary_exception or release_exception
    payload = {
        **prepared.payload,
        "execution_status": invocation_status,
        "invocation_status": invocation_status,
        "stage_execution_status": stage_execution_status,
        "failure_phase": failure_phase,
        "exit_status": int(exit_status),
        "exception": _exception_payload(authoritative),
        "primary_exception": _exception_payload(primary_exception),
        "release_exception": _exception_payload(release_exception),
        "lease": _lease_quality_record(lease, output_root),
        "summary_written_after_lease_release_attempt": bool(
            lease.release_attempted
        ),
        "summary_written_after_os_lease_terminal": bool(
            lease.os_unlock_succeeded and lease.handle_closed
        ),
        "summary_written_after_successful_release_workflow": bool(
            lease.released
        ),
        "summary_written_after_lease_release": bool(lease.released),
        "shared_stage_artifacts_modified_by_summary": False,
    }
    _write_json_atomic_new(
        prepared.target,
        payload,
        evidence_root=prepared.evidence_root,
    )
    return prepared.target


def _prepare_context_failure_summary(
    *,
    config: PipelineConfig,
    context: RunContext,
    scope: "ExecutionScope",
    invocation_id: str,
    requested_stage: str,
    resume: bool,
    failure_phase: str,
    primary_exception: BaseException | None,
    release_exception: BaseException | None,
    exit_status: int,
) -> PreparedQualitySummary:
    """Freeze a setup-failure summary before the run lease is released."""

    target = (
        context.audit_dir
        / "quality_summaries"
        / f"run_quality_summary.{invocation_id}.json"
    )
    authoritative = primary_exception or release_exception
    payload = {
        "schema_version": 1,
        "invocation_id": invocation_id,
        "run_id": context.run_id,
        "requested_stage": requested_stage,
        "requested_scope": scope.as_parameters(),
        "resume": bool(resume),
        "execution_status": "FAILED",
        "invocation_status": "FAILED",
        "stage_execution_status": "NOT_STARTED",
        "failure_phase": failure_phase,
        "exit_status": int(exit_status),
        "status": context.completion_scope_status,
        "scope_profile": context.scope_profile,
        "completion_scope_status": context.completion_scope_status,
        "created_at_utc": utc_now(),
        "config_sha256": config.sha256,
        "template_config_sha256": config.template_sha256 or config.sha256,
        "effective_config_sha256": config.sha256,
        "resolved_paths": config.resolved_paths(),
        "parameter_sha256": context.parameter_sha256,
        "source_tree_sha256": context.source_tree_sha256,
        "environment_sha256": context.environment_sha256,
        "code_git_commit": context.code_git_commit,
        "stages": [],
        "exception": _exception_payload(authoritative),
        "primary_exception": _exception_payload(primary_exception),
        "release_exception": _exception_payload(release_exception),
        "audit_issues": [],
        "diagnostic_issues": [],
        "capture_mode": "automatic_runtime",
        "retrospective": False,
    }
    return PreparedQualitySummary(
        target=target,
        evidence_root=context.run_dir,
        payload=_snapshot_quality_payload(payload),
    )


def _stage_file(context: RunContext, stage: str, *parts: str) -> Path:
    path = context.stages_dir.joinpath(stage, *parts)
    return ensure_within_run(path, context.run_dir)


def _select_crosswalk(crosswalk: pd.DataFrame, scope: ExecutionScope) -> pd.DataFrame:
    ordered = crosswalk.sort_values("era01_cell_id").reset_index(drop=True)
    if not scope.is_pilot:
        return ordered
    generator = np.random.default_rng(scope.random_seed)
    positions = np.sort(
        generator.choice(len(ordered), size=int(scope.pilot_cells), replace=False)
    )
    return ordered.iloc[positions].sort_values("era01_cell_id").reset_index(drop=True)


def _handle_assets(request: StageRequest) -> StageOutcome:
    from .inventory import build_inventory, write_inventory

    result = build_inventory(
        request.config,
        hash_mode=request.scope.hash_mode,
        inspect_axes=True,
    )
    json_path, parquet_path = write_inventory(result, request.work_dir)
    if not result.ok or result.pipeline_blocked:
        failures = [
            item["check_id"]
            for item in result.checks
            if item["status"] == "fail"
            or (
                item["status"] == "blocked"
                and item.get("evidence", {}).get("blocking_scope", "pipeline")
                == "pipeline"
            )
        ]
        raise StageValidationError(
            f"Asset inventory has failed or unresolved checks: {failures}"
        )
    return StageOutcome(
        artifacts={"inventory_json": json_path, "inventory_parquet": parquet_path},
        row_counts={"assets": len(result.records), "checks": len(result.checks)},
        extra={
            "inventory_blocked": result.pipeline_blocked,
            "inventory_scope_limited_blocks": [
                item["check_id"]
                for item in result.checks
                if item["status"] == "blocked"
                and item.get("evidence", {}).get("blocking_scope")
                != "pipeline"
            ],
            "spei_2w_timestamp_semantics": request.config.data["spei"][
                "two_week_timestamp_semantics"
            ],
            "spei_2w_numeric_executed": False,
            "spei_2w_numeric_stage": "spei",
            "spei_2w_output_enabled": bool(
                request.config.data["scope"]["spei_2w_output"]
            ),
        },
    )


def _handle_grid(request: StageRequest) -> StageOutcome:
    from .grid import build_balanced_grid_year, build_v3_crosswalk

    coordinate_tolerance = float(
        request.config.data["grid"].get("v3_coordinate_tolerance_degrees", 1e-5)
    )
    full = build_v3_crosswalk(
        request.config.data["inputs"]["v3_main"],
        expected_unique=int(request.config.data["grid"]["expected_cells"]),
        input_coordinate_tolerance=coordinate_tolerance,
    )
    selected = _select_crosswalk(full, request.scope)
    panel = build_balanced_grid_year(
        selected, request.scope.years, expected_unique=None
    )
    crosswalk_path = request.work_dir / "crosswalk.parquet"
    panel_path = request.work_dir / "grid_year.parquet"
    selected.to_parquet(crosswalk_path, index=False)
    panel.to_parquet(panel_path, index=False)
    selection_path = request.work_dir / "selection.json"
    residuals = {
        "input_coordinate_tolerance_degrees": coordinate_tolerance,
        "full_max_v3_lat_err_abs_deg": float(full["v3_lat_err_abs_deg"].max()),
        "full_max_v3_lon_err_abs_deg": float(full["v3_lon_err_abs_deg"].max()),
        "selected_max_v3_lat_err_abs_deg": float(
            selected["v3_lat_err_abs_deg"].max()
        ),
        "selected_max_v3_lon_err_abs_deg": float(
            selected["v3_lon_err_abs_deg"].max()
        ),
    }
    _write_json_new(
        selection_path,
        {
            **request.scope.as_parameters(),
            "full_cells": len(full),
            "selected_cells": len(selected),
            "v3_coordinate_alignment": residuals,
            "selected_era01_cell_id_sha256": __import__("hashlib").sha256(
                selected["era01_cell_id"].to_numpy(dtype="<i8").tobytes()
            ).hexdigest(),
        },
    )
    return StageOutcome(
        artifacts={
            "crosswalk": crosswalk_path,
            "grid_year": panel_path,
            "selection": selection_path,
        },
        row_counts={
            "full_cells": len(full),
            "selected_cells": len(selected),
            "grid_year_rows": len(panel),
        },
        extra={"v3_coordinate_alignment": residuals},
    )


def _handle_phenology(request: StageRequest) -> StageOutcome:
    from .phenology import build_phenology_panel

    crosswalk = pd.read_parquet(
        _stage_file(request.context, "grid", "crosswalk.parquet")
    )
    pattern_path = Path(request.config.data["inputs"]["phenology_pattern"])
    panel = build_phenology_panel(
        crosswalk,
        request.scope.years,
        pattern_path.parent,
        source_crs=request.config.data["phenology"]["source_crs"],
        pattern=pattern_path.name,
    )
    output = request.work_dir / "phenology_panel.parquet"
    panel.to_parquet(output, index=False)
    valid = int(panel[["v3_doy", "he_doy", "ma_doy"]].notna().all(axis=1).sum())
    return StageOutcome(
        artifacts={"phenology_panel": output},
        row_counts={"rows": len(panel), "valid_phenology_rows": valid},
    )


def _handle_era_daily(request: StageRequest) -> StageOutcome:
    from .era5 import build_era_daily_cache

    crosswalk = pd.read_parquet(
        _stage_file(request.context, "grid", "crosswalk.parquet")
    )
    years = _event_context_years(request.config)
    root = request.work_dir / "daily_cache"
    gdd_pairs = tuple(
        (float(item["base"]), float(item["upper"]))
        for item in request.config.data["temperature"]["gdd"]
    )
    edd_thresholds = tuple(
        float(value) for value in request.config.data["temperature"]["edd_thresholds"]
    )
    gdd_names = tuple(
        f"era5u8_gdd_b{int(base)}_u{int(upper)}" for base, upper in gdd_pairs
    )
    edd_names = tuple(f"era5u8_edd_t{int(value)}" for value in edd_thresholds)
    if request.pipeline.resume:
        for year in years:
            partition = root / f"year={year}"
            if partition.exists() and not _era_partition_complete(
                root,
                year,
                cells=len(crosswalk),
                gdd_names=gdd_names,
                edd_names=edd_names,
            ):
                _archive_incomplete(partition)
    outputs = build_era_daily_cache(
        request.config.data["inputs"]["era5_hourly_pattern"],
        years,
        crosswalk,
        root,
        file_overrides=request.config.data["inputs"].get(
            "era5_hourly_overrides", {}
        ),
        utc_offset_hours=8,
        gdd_pairs=gdd_pairs,
        edd_thresholds=edd_thresholds,
        resume=request.pipeline.resume,
    )
    return StageOutcome(
        artifacts={"daily_cache": root},
        row_counts={
            "years": len(years),
            "cells": len(crosswalk),
            "cache_files": len(outputs),
        },
        extra={"utc_offset_hours": 8},
    )


def _handle_era_baseline(request: StageRequest) -> StageOutcome:
    from .era5 import build_calendar_thresholds

    daily_root = _stage_file(request.context, "era_daily", "daily_cache")
    root = request.work_dir / "thresholds"
    outputs = build_calendar_thresholds(
        daily_root,
        request.config.historical_years,
        _event_context_years(request.config),
        root,
        half_width=int(
            request.config.data["temperature"]["calendar_window_half_width_days"]
        ),
        quantile=float(request.config.data["temperature"]["hot_quantile"]),
        minimum_history_fraction=float(
            request.config.data["temperature"]["minimum_history_fraction"]
        ),
    )
    return StageOutcome(
        artifacts={"thresholds": root},
        row_counts={"threshold_files": len(outputs)},
        extra={"history_years": request.config.historical_years},
    )


def _add_cell_index(frame: pd.DataFrame, crosswalk: pd.DataFrame) -> pd.DataFrame:
    index = crosswalk[["era01_cell_id"]].copy()
    index["cell_index"] = np.arange(len(index), dtype=np.int32)
    merged = frame.merge(index, on="era01_cell_id", how="left", validate="many_to_one")
    if merged["cell_index"].isna().any():
        raise StageValidationError("Panel rows do not map to the selected SPEI cells")
    merged["cell_index"] = merged["cell_index"].astype(np.int32)
    return merged


def _read_v3_legacy_projection(
    v3_path: str | Path,
    legacy_field_map: Mapping[str, tuple[str, str]],
) -> tuple[pd.DataFrame, str]:
    """Read only fields required to reconstruct the frozen V3 SPEI sidecar."""

    import pyarrow.parquet as pq

    source = Path(v3_path)
    schema_names = set(pq.ParquetFile(source).schema_arrow.names)
    grid_name = "grid_id_v3" if "grid_id_v3" in schema_names else "grid_id"
    projected = [grid_name, "year", "latitude", "longitude"]
    for window in legacy_field_map:
        date_pair = (f"win_{window}_start_date", f"win_{window}_end_date")
        doy_pair = (f"win_{window}_start", f"win_{window}_end")
        if set(date_pair).issubset(schema_names):
            projected.extend(date_pair)
        elif set(doy_pair).issubset(schema_names):
            projected.extend(doy_pair)
        else:
            raise StageValidationError(
                f"V3 main lacks a complete projected window pair for {window}"
            )
    projected.extend(
        field for pair in legacy_field_map.values() for field in pair
    )
    missing = [name for name in projected if name not in schema_names]
    if missing:
        raise StageValidationError(
            f"V3 main lacks projected legacy-sidecar fields: {missing}"
        )
    return pd.read_parquet(source, columns=projected), grid_name


def _count_parquet_value_batched(
    path: str | Path,
    *,
    column: str,
    value: str,
    batch_size: int = 65_536,
) -> tuple[int, int]:
    """Count one Parquet value without materializing the complete string column."""

    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    if int(batch_size) <= 0:
        raise ValueError("batch_size must be positive")
    parquet = pq.ParquetFile(path)
    if column not in parquet.schema_arrow.names:
        raise StageValidationError(
            f"Parquet audit output lacks {column} schema: {Path(path).name}"
        )
    total = 0
    maximum = 0
    for batch in parquet.iter_batches(
        columns=[column], batch_size=int(batch_size)
    ):
        if batch.num_rows > int(batch_size):
            raise AssertionError("Parquet audit scan exceeded its batch contract")
        maximum = max(maximum, batch.num_rows)
        matches = pc.fill_null(pc.equal(batch.column(0), value), False)
        total += int(pc.sum(pc.cast(matches, "int64")).as_py() or 0)
    return total, maximum


def _validate_spei_2w_event_row_counts(
    audit: Mapping[str, Any],
    event_path: str | Path,
    bridge_path: str | Path,
    *,
    batch_size: int = 65_536,
) -> tuple[int, int, int, int]:
    """Cross-check 2W event/bridge counts with bounded Arrow scans."""

    event_rows, event_max = _count_parquet_value_batched(
        event_path, column="timescale", value="2W", batch_size=batch_size
    )
    bridge_rows, bridge_max = _count_parquet_value_batched(
        bridge_path, column="timescale", value="2W", batch_size=batch_size
    )
    if event_rows != int(audit.get("event_rows", -1)):
        raise StageValidationError("SPEI-2W event rows differ from stage audit")
    if bridge_rows != int(audit.get("bridge_rows", -1)):
        raise StageValidationError("SPEI-2W bridge rows differ from stage audit")
    return event_rows, bridge_rows, event_max, bridge_max


def _handle_spei(request: StageRequest) -> StageOutcome:
    from .spei import (
        LEGACY_FIELD_MAP,
        build_spei_caches,
        build_two_week_cache,
        combine_parquet_partitions_new,
        iter_spei_aggregation_blocks,
        legacy_v3_exact_sidecar,
        load_cache_array,
        parquet_partition_contract,
        prepare_two_week_records,
        write_parquet_partition_new,
        write_two_week_audit,
    )

    spei_config = request.config.data["spei"]
    scope_config = request.config.data["scope"]
    two_week_enabled = bool(scope_config["spei_2w_numeric"])
    endpoint_status = str(spei_config["two_week_endpoint_decision_status"])
    if two_week_enabled and endpoint_status != "CONFIRMED":
        raise StageValidationError(
            "SPEI-2W endpoint is not confirmed; FULL_SCOPE numerics are disabled"
        )
    crosswalk = pd.read_parquet(
        _stage_file(request.context, "grid", "crosswalk.parquet")
    ).sort_values("era01_cell_id").reset_index(drop=True)
    panel = _add_cell_index(
        pd.read_parquet(
            _stage_file(request.context, "phenology", "phenology_panel.parquet")
        ),
        crosswalk,
    )
    cache_root = request.work_dir / "cache"
    caches = build_spei_caches(
        request.config.data["inputs"]["spei_monthly_pattern"],
        crosswalk["latitude"].to_numpy(),
        crosswalk["longitude"].to_numpy(),
        cache_root,
        target_years=request.scope.years,
        target_scales=tuple(range(1, 13)),
        full_years=tuple(range(1961, 2023)),
        manual_scales=(1, 3),
        minimum_valid_neighbors=int(
            request.config.data["spei"]["minimum_valid_neighbors"]
        ),
        resume=request.pipeline.resume,
    )
    two_week_caches = None
    if two_week_enabled:
        two_week_caches = build_two_week_cache(
            request.config.data["inputs"]["spei_2w"],
            crosswalk["latitude"].to_numpy(),
            crosswalk["longitude"].to_numpy(),
            cache_root / "two_week",
            minimum_valid_neighbors=int(spei_config["minimum_valid_neighbors"]),
            interpolation=str(spei_config["two_week_interpolation"]),
            accumulation_days=int(spei_config["two_week_accumulation_days"]),
            state_days=int(spei_config["two_week_state_days"]),
            accumulation_timestamp_position=str(
                spei_config["two_week_accumulation_timestamp_position"]
            ),
            state_timestamp_position=str(
                spei_config["two_week_state_timestamp_position"]
            ),
            timestamp_semantics=str(spei_config["two_week_timestamp_semantics"]),
            endpoint_decision_status=endpoint_status,
            resume=request.pipeline.resume,
        )
    full_codes = load_cache_array(caches.full_month_codes)
    full_values = {
        scale: load_cache_array(path) for scale, path in caches.full_manual.items()
    }
    target_codes = load_cache_array(caches.target_month_codes)
    target_values = {
        scale: load_cache_array(path) for scale, path in caches.target_nearest.items()
    }
    two_week_release_dates = None
    two_week_values = None
    two_week_event_specs = None
    if two_week_caches is not None:
        two_week_release_ordinals = load_cache_array(
            two_week_caches.release_ordinals
        )
        two_week_release_dates = tuple(
            date.fromordinal(int(value)) for value in two_week_release_ordinals
        )
        two_week_values = load_cache_array(two_week_caches.values)
        two_week_event_specs = {
            "k10_main": (
                float(spei_config["two_week_primary_threshold"]),
                int(spei_config["two_week_primary_min_units"]),
            ),
            "k15_strict": (
                float(spei_config["two_week_strict_threshold"]),
                int(spei_config["two_week_strict_min_units"]),
            ),
        }
    manual_path = request.work_dir / "chm_spei_manual.parquet"
    dynamic_path = request.work_dir / "chm_spei_dynamic_ext.parquet"
    event_long_path = request.work_dir / "chm_spei_event_window_long.parquet"
    event_audit_path = request.work_dir / "chm_spei_events.parquet"
    event_bridge_path = request.work_dir / "chm_spei_event_window_bridge.parquet"
    cell_block_size = int(
        request.config.data.get("runtime", {}).get("spei_cell_block_size", 128)
    )
    if cell_block_size <= 0:
        raise StageValidationError("runtime.spei_cell_block_size must be positive")
    row_group_size = int(
        request.config.data.get("runtime", {}).get(
            "parquet_row_group_size", 262_144
        )
    )
    partition_root = request.work_dir / "parquet_partitions"
    output_paths = {
        "manual": manual_path,
        "dynamic": dynamic_path,
        "event_long": event_long_path,
        "events": event_audit_path,
        "event_bridge": event_bridge_path,
    }
    required_columns = {
        "manual": ("source_row", "window", "chm_spei_s1_mean"),
        "dynamic": (
            "source_row",
            "window",
            "chm_spei_dynamic_ext_value",
        ),
        "event_long": (
            "source_row",
            "window",
            "chm_spei_s1_k10_main_count",
        )
        + (("chm_spei_2w_k10_main_count",) if two_week_enabled else ()),
        "events": ("event_id", "timescale"),
        "event_bridge": ("event_id", "timescale"),
    }
    partition_paths: dict[str, list[Path]] = {
        name: [] for name in output_paths
    }
    ranges: list[tuple[int, int]] = []
    incomplete_ranges: list[tuple[int, int]] = []
    panel_indices = panel["cell_index"].to_numpy(dtype=np.int64)
    for cell_start in range(0, len(crosswalk), cell_block_size):
        cell_stop = min(cell_start + cell_block_size, len(crosswalk))
        ranges.append((cell_start, cell_stop))
        block_rows = int(
            np.count_nonzero(
                (panel_indices >= cell_start) & (panel_indices < cell_stop)
            )
        )
        expected_long_rows = block_rows * 6
        block_complete = True
        for name in output_paths:
            path = (
                partition_root
                / name
                / f"cells={cell_start:06d}-{cell_stop - 1:06d}.parquet"
            )
            partition_paths[name].append(path)
            expected = expected_long_rows if name in {
                "manual",
                "dynamic",
                "event_long",
            } else None
            valid, _rows = parquet_partition_contract(
                path,
                expected_rows=expected,
                required_columns=required_columns[name],
            )
            if not valid:
                block_complete = False
                if path.exists():
                    if not request.pipeline.resume:
                        raise FileExistsError(path)
                    _archive_incomplete(path)
        if not block_complete:
            incomplete_ranges.append((cell_start, cell_stop))

    generated = iter_spei_aggregation_blocks(
        panel,
        full_codes,
        full_values,
        target_codes,
        target_values,
        cell_index_column="cell_index",
        cell_count=len(crosswalk),
        cell_block_size=cell_block_size,
        cell_ranges=incomplete_ranges,
        minimum_coverage=float(
            request.config.data["quality"]["minimum_window_coverage"]
        ),
        two_week_release_dates=two_week_release_dates,
        two_week_values=two_week_values,
        two_week_accumulation_days=int(
            spei_config["two_week_accumulation_days"]
        ),
        two_week_state_days=int(spei_config["two_week_state_days"]),
        two_week_accumulation_timestamp_position=str(
            spei_config["two_week_accumulation_timestamp_position"]
        ),
        two_week_state_timestamp_position=str(
            spei_config["two_week_state_timestamp_position"]
        ),
        two_week_event_specs=(
            two_week_event_specs
            if two_week_event_specs is not None
            else {
                "k10_main": (-1.0, 1),
                "k15_strict": (-1.5, 3),
            }
        ),
    )
    range_position = {value: index for index, value in enumerate(ranges)}
    for block in generated:
        position = range_position[(block.cell_start, block.cell_stop)]
        frames = {
            "manual": block.manual,
            "dynamic": block.dynamic,
            "event_long": block.event_long,
            "events": block.events,
            "event_bridge": block.event_bridges,
        }
        for name, raw_frame in frames.items():
            frame = raw_frame
            if name in {"events", "event_bridge"} and frame.empty:
                if "event_id" not in frame:
                    frame["event_id"] = pd.Series(dtype="string")
                if "timescale" not in frame:
                    frame["timescale"] = pd.Series(dtype="string")
            path = partition_paths[name][position]
            expected_rows = len(frame)
            valid, _existing_rows = parquet_partition_contract(
                path,
                expected_rows=expected_rows,
                required_columns=required_columns[name],
            )
            if valid:
                continue
            if path.exists():
                if not request.pipeline.resume:
                    raise FileExistsError(path)
                _archive_incomplete(path)
            write_parquet_partition_new(
                path,
                frame,
                row_group_size=row_group_size,
            )
            valid, written_rows = parquet_partition_contract(
                path,
                expected_rows=expected_rows,
                required_columns=required_columns[name],
            )
            if not valid or written_rows != expected_rows:
                raise StageValidationError(
                    f"Invalid SPEI {name} partition {path}"
                )

    row_counts: dict[str, int] = {}
    count_names = {
        "manual": "manual_rows",
        "dynamic": "dynamic_rows",
        "event_long": "event_long_rows",
        "events": "events",
        "event_bridge": "event_bridges",
    }
    for name, target in output_paths.items():
        counts: list[int] = []
        for path in partition_paths[name]:
            valid, rows = parquet_partition_contract(
                path, required_columns=required_columns[name]
            )
            if not valid:
                raise StageValidationError(f"Incomplete SPEI {name} partition {path}")
            counts.append(rows)
        expected_total = sum(counts)
        canonical_valid, canonical_rows = parquet_partition_contract(
            target,
            expected_rows=expected_total,
            required_columns=required_columns[name],
        )
        if not canonical_valid:
            if target.exists():
                if not request.pipeline.resume:
                    raise FileExistsError(target)
                _archive_incomplete(target)
            empty_frame = (
                pd.DataFrame(
                    {
                        "event_id": pd.Series(dtype="string"),
                        "timescale": pd.Series(dtype="string"),
                    }
                )
                if name in {"events", "event_bridge"}
                else None
            )
            _target, canonical_rows = combine_parquet_partitions_new(
                partition_paths[name],
                target,
                row_group_size=row_group_size,
                empty_frame=empty_frame,
            )
        if canonical_rows != expected_total:
            raise StageValidationError(
                f"Canonical SPEI {name} row count differs from its partitions"
            )
        row_counts[count_names[name]] = canonical_rows
    artifacts: dict[str, Path] = {
        "cache": cache_root,
        "parquet_partitions": partition_root,
        "manual": manual_path,
        "dynamic": dynamic_path,
        "event_long": event_long_path,
        "events": event_audit_path,
        "event_bridge": event_bridge_path,
    }
    if two_week_caches is not None:
        artifacts["spei_2w_cache"] = two_week_caches.root

    if not request.scope.is_pilot:
        v3, grid_name = _read_v3_legacy_projection(
            request.config.data["inputs"]["v3_main"], LEGACY_FIELD_MAP
        )
        mapping = crosswalk[["grid_id_v3"]].copy()
        mapping["cell_index"] = np.arange(len(mapping), dtype=np.int32)
        v3 = v3.merge(
            mapping,
            left_on=grid_name,
            right_on="grid_id_v3",
            how="left",
            validate="many_to_one",
        )
        legacy = legacy_v3_exact_sidecar(
            v3,
            target_codes,
            target_values,
            cell_index_column="cell_index",
        )
        legacy_path = request.work_dir / "legacy_v3_exact.parquet"
        if request.pipeline.resume and legacy_path.exists():
            _archive_incomplete(legacy_path)
        legacy.to_parquet(legacy_path, index=False)
        artifacts["legacy_v3_exact"] = legacy_path
        row_counts["legacy_rows"] = len(legacy)

    import pyarrow.parquet as pq

    event_long_schema = pq.ParquetFile(event_long_path).schema_arrow.names
    two_week_fields = [
        name for name in event_long_schema if name.startswith("chm_spei_2w_")
    ]
    if two_week_enabled and not two_week_fields:
        raise StageValidationError("SPEI event long output lacks 2W canonical fields")
    if not two_week_enabled and two_week_fields:
        raise StageValidationError(
            "PARTIAL_SCOPE SPEI output must not contain 2W canonical fields"
        )

    count_scan_batch_size = 65_536
    two_week_event_rows, event_scan_max = _count_parquet_value_batched(
        event_audit_path,
        column="timescale",
        value="2W",
        batch_size=count_scan_batch_size,
    )
    two_week_bridge_rows, bridge_scan_max = _count_parquet_value_batched(
        event_bridge_path,
        column="timescale",
        value="2W",
        batch_size=count_scan_batch_size,
    )
    semantics = str(spei_config["two_week_timestamp_semantics"])
    audit_dates = tuple(two_week_release_dates or ())
    audit_values = (
        np.asarray(two_week_values[:, 0], dtype=float)
        if two_week_values is not None
        else np.asarray([], dtype=float)
    )
    _records, audit = prepare_two_week_records(
        audit_dates,
        audit_values,
        config_semantics=semantics,
        endpoint_decision_status=endpoint_status,
        accumulation_timestamp_position=str(
            spei_config["two_week_accumulation_timestamp_position"]
        ),
        state_timestamp_position=str(
            spei_config["two_week_state_timestamp_position"]
        ),
        accumulation_days=int(spei_config["two_week_accumulation_days"]),
        state_days=int(spei_config["two_week_state_days"]),
        primary_threshold=float(spei_config["two_week_primary_threshold"]),
        primary_min_units=int(spei_config["two_week_primary_min_units"]),
        strict_threshold=float(spei_config["two_week_strict_threshold"]),
        strict_min_units=int(spei_config["two_week_strict_min_units"]),
        cell_count=(int(two_week_values.shape[1]) if two_week_values is not None else 0),
        canonical_field_count=len(two_week_fields),
        event_rows=two_week_event_rows,
        bridge_rows=two_week_bridge_rows,
        count_scan_batch_size=count_scan_batch_size,
        event_count_scan_max_batch_rows=event_scan_max,
        bridge_count_scan_max_batch_rows=bridge_scan_max,
    )
    audit_target = request.work_dir / "spei_2w_audit.json"
    if request.pipeline.resume and audit_target.exists():
        _archive_incomplete(audit_target)
    audit_path = write_two_week_audit(audit_target, audit)
    artifacts["spei_2w_audit"] = audit_path
    row_counts["spei_2w_releases"] = len(audit_dates)
    row_counts["spei_2w_cells"] = (
        int(two_week_values.shape[1]) if two_week_values is not None else 0
    )
    return StageOutcome(
        artifacts=artifacts,
        row_counts=row_counts,
        extra={
            "spei_2w": audit.as_dict(),
            "product_standardization": request.config.data["spei"][
                "product_standardization"
            ],
        },
    )


def _handle_gleam_daily(request: StageRequest) -> StageOutcome:
    from .gleam import build_spatial_map, read_source_axes, write_selected_daily_cache

    crosswalk = pd.read_parquet(
        _stage_file(request.context, "grid", "crosswalk.parquet")
    ).sort_values("era01_cell_id").reset_index(drop=True)
    first_year = min(request.config.historical_years)
    first_layer = next(iter(request.config.data["gleam"]["layers"]))
    pattern = request.config.data["inputs"]["gleam_pattern"]
    sample = Path(pattern.format(year=first_year, layer=first_layer))
    source_latitude, source_longitude = read_source_axes(sample)
    mapping = build_spatial_map(
        source_latitude,
        source_longitude,
        crosswalk["latitude"].to_numpy(),
        crosswalk["longitude"].to_numpy(),
        cell_ids=crosswalk["era01_cell_id"].to_numpy(),
    )
    years = _event_context_years(request.config)
    root = request.work_dir / "daily_cache"
    total_rows = 0
    files = 0
    expected_cell_ids = crosswalk["era01_cell_id"].to_numpy(dtype=np.int64)
    for layer in request.config.data["gleam"]["layers"]:
        for year in years:
            source = Path(pattern.format(year=year, layer=layer))
            target = root / str(layer) / f"year={year}.nc"
            if request.pipeline.resume and target.exists():
                if _gleam_daily_partition_complete(
                    target,
                    layer=str(layer),
                    year=year,
                    cell_ids=expected_cell_ids,
                ):
                    days = 366 if __import__("calendar").isleap(year) else 365
                    total_rows += days * len(crosswalk)
                    files += 1
                    continue
                _archive_incomplete(target)
            summary = write_selected_daily_cache(
                source,
                target,
                request.work_dir,
                str(layer),
                mapping,
                expected_year=year,
                min_valid_neighbors=int(
                    request.config.data["gleam"]["minimum_valid_neighbors"]
                ),
            )
            if summary.year != year:
                raise StageValidationError(
                    f"GLEAM {layer} source year is {summary.year}, expected {year}"
                )
            total_rows += summary.rows
            files += 1
    return StageOutcome(
        artifacts={"daily_cache": root},
        row_counts={
            "cache_files": files,
            "daily_cell_rows": total_rows,
            "cells": len(crosswalk),
        },
        extra={"time_chunk_days": 12, "years": list(years)},
    )


def _save_npy_new(path: Path, values: np.ndarray) -> Path:
    """Persist one stage-local array without replacing an existing artifact."""

    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        np.save(handle, np.asarray(values), allow_pickle=False)
    return path


def _archive_incomplete(path: Path) -> Path:
    """Preserve an incomplete stage artifact under a unique sibling name."""

    if not path.exists():
        raise FileNotFoundError(path)
    archived = path.with_name(f".{path.name}.{uuid.uuid4().hex}.incomplete")
    os.rename(path, archived)
    return archived


def _era_partition_complete(
    root: Path,
    year: int,
    *,
    cells: int,
    gdd_names: Sequence[str],
    edd_names: Sequence[str],
) -> bool:
    directory = root / f"year={int(year)}"
    expected_days = 366 if __import__("calendar").isleap(int(year)) else 365
    names = (
        "era5u8_tmean_c",
        "era5u8_tmax_c",
        "era5u8_tmin_c",
        "era5u8_hour_count",
        *gdd_names,
        *edd_names,
    )
    try:
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        dates = np.load(directory / "date_days_since_1970.npy", mmap_mode="r")
        if dates.shape != (expected_days,):
            return False
        for name in names:
            if np.load(directory / f"{name}.npy", mmap_mode="r").shape != (
                expected_days,
                cells,
            ):
                return False
        return int(metadata.get("year", year)) == year
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return False


def _gleam_daily_partition_complete(
    path: Path,
    *,
    layer: str,
    year: int,
    cell_ids: np.ndarray,
) -> bool:
    import calendar
    import netCDF4 as nc

    try:
        with nc.Dataset(path) as dataset:
            if layer not in dataset.variables:
                return False
            if dataset.variables[layer].shape != (
                366 if calendar.isleap(year) else 365,
                len(cell_ids),
            ):
                return False
            observed = np.asarray(dataset.variables["era01_cell_id"][:], dtype=np.int64)
            if not np.array_equal(observed, cell_ids):
                return False
            dates = _netcdf_python_dates(dataset)
            return bool(dates) and all(value.year == year for value in dates)
    except (OSError, ValueError, KeyError):
        return False


def _gleam_metric_partition_complete(
    root: Path,
    *,
    layer: str,
    year: int,
    days: int,
    cells: int,
) -> bool:
    directory = root / layer / f"year={int(year)}"
    daily = (
        "daily_q10",
        "daily_percentile",
        "daily_below_p10",
        "daily_history_count",
    )
    pentad = (
        "pentad_values",
        "pentad_valid_day_counts",
        "pentad_percentile",
        "pentad_below_p10",
        "pentad_below_p20",
        "pentad_history_count",
        "pentad_q10",
        "pentad_q20",
        "pentad_q40",
    )
    try:
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        if int(metadata["year"]) != year or int(metadata["cells"]) != cells:
            return False
        if np.load(
            directory / "daily_expected_history_count.npy", mmap_mode="r"
        ).shape != (days,):
            return False
        if any(
            np.load(directory / f"{name}.npy", mmap_mode="r").shape
            != (days, cells)
            for name in daily
        ):
            return False
        return not any(
            np.load(directory / f"{name}.npy", mmap_mode="r").shape
            != (73, cells)
            for name in pentad
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return False


def _gleam_partition_path(root: Path, layer: str, year: int) -> Path:
    return root / str(layer) / f"year={int(year)}.nc"


def _netcdf_python_dates(dataset: Any) -> tuple[date, ...]:
    import netCDF4 as nc

    variable = dataset.variables["time"]
    decoded = nc.num2date(
        variable[:],
        units=variable.units,
        calendar=getattr(variable, "calendar", "standard"),
    )
    return tuple(date(int(value.year), int(value.month), int(value.day)) for value in decoded)


def _read_gleam_partition(
    root: Path,
    layer: str,
    year: int,
    *,
    cell_slice: slice | None = None,
) -> tuple[tuple[date, ...], np.ndarray, np.ndarray]:
    """Read one GLEAM cache partition, optionally limited to a cell block."""

    import netCDF4 as nc

    path = _gleam_partition_path(root, layer, year)
    selector = slice(None) if cell_slice is None else cell_slice
    with nc.Dataset(path) as dataset:
        dates = _netcdf_python_dates(dataset)
        cell_ids = np.asarray(
            dataset.variables["era01_cell_id"][selector], dtype=np.int64
        )
        values = np.ma.filled(dataset.variables[layer][:, selector], np.nan).astype(
            np.float64, copy=False
        )
    if values.shape != (len(dates), len(cell_ids)):
        raise StageValidationError(f"Invalid GLEAM cache shape: {path}")
    return dates, cell_ids, values


def _metric_path(root: Path, layer: str, year: int, name: str) -> Path:
    return root / str(layer) / f"year={int(year)}" / f"{name}.npy"


def _new_metric_writer(
    root: Path,
    layer: str,
    year: int,
    name: str,
    *,
    dtype: np.dtype[Any] | str,
    shape: tuple[int, ...],
) -> np.memmap:
    path = _metric_path(root, layer, year, name)
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return np.lib.format.open_memmap(path, mode="w+", dtype=dtype, shape=shape)


def _handle_gleam_baseline(request: StageRequest) -> StageOutcome:
    """Build persisted daily and pentad historical metrics in bounded cell blocks."""

    import netCDF4 as nc

    from .gleam import (
        apply_daily_p10_climatology,
        apply_pentad_climatology,
        daily_values_to_pentads,
    )

    daily_root = _stage_file(request.context, "gleam_daily", "daily_cache")
    metric_root = request.work_dir / "metrics"
    crosswalk = pd.read_parquet(
        _stage_file(request.context, "grid", "crosswalk.parquet")
    ).sort_values("era01_cell_id").reset_index(drop=True)
    expected_cell_ids = crosswalk["era01_cell_id"].to_numpy(dtype=np.int64)
    historical_years = tuple(sorted(int(value) for value in request.config.historical_years))
    target_years = _event_context_years(request.config)
    all_years = tuple(sorted(set(historical_years) | set(target_years)))
    minimum_fraction = float(
        request.config.data["temperature"].get("minimum_history_fraction", 0.90)
    )
    minimum_historical_years = max(
        1, math.ceil(len(historical_years) * minimum_fraction - 1e-12)
    )
    cell_block_size = int(
        request.config.data.get("runtime", {}).get("gleam_cell_block_size", 128)
    )
    if cell_block_size <= 0:
        raise ValueError("runtime.gleam_cell_block_size must be positive")
    storage_dtype = np.dtype(
        request.config.data.get("runtime", {}).get("storage_dtype", "float64")
    )
    if storage_dtype.kind != "f":
        raise ValueError("runtime.storage_dtype must be a floating dtype")

    file_count = 0
    daily_cell_rows = 0
    pentad_cell_rows = 0
    layer_summaries: dict[str, Any] = {}
    for layer in request.config.data["gleam"]["layers"]:
        with ExitStack() as stack:
            datasets = {
                year: stack.enter_context(
                    nc.Dataset(_gleam_partition_path(daily_root, str(layer), year))
                )
                for year in all_years
            }
            dates_by_year: dict[int, tuple[date, ...]] = {}
            for year, dataset in datasets.items():
                dates_by_year[year] = _netcdf_python_dates(dataset)
                observed_ids = np.asarray(
                    dataset.variables["era01_cell_id"][:], dtype=np.int64
                )
                if not np.array_equal(observed_ids, expected_cell_ids):
                    raise StageValidationError(
                        f"GLEAM {layer} {year} cell order differs from crosswalk"
                    )
                variable = dataset.variables[str(layer)]
                if variable.shape != (len(dates_by_year[year]), len(crosswalk)):
                    raise StageValidationError(
                        f"GLEAM {layer} {year} daily cache shape is invalid"
                    )

            complete_years: set[int] = set()
            if request.pipeline.resume:
                for year in target_years:
                    partition = metric_root / str(layer) / f"year={year}"
                    if _gleam_metric_partition_complete(
                        metric_root,
                        layer=str(layer),
                        year=year,
                        days=len(dates_by_year[year]),
                        cells=len(crosswalk),
                    ):
                        complete_years.add(year)
                    elif partition.exists():
                        _archive_incomplete(partition)
            pending_years = tuple(
                year for year in target_years if year not in complete_years
            )
            file_count += len(complete_years) * 15
            daily_cell_rows += sum(
                len(dates_by_year[year]) * len(crosswalk) for year in complete_years
            )
            pentad_cell_rows += len(complete_years) * 73 * len(crosswalk)

            writers: dict[tuple[int, str], np.memmap] = {}
            daily_names = {
                "daily_q10": storage_dtype,
                "daily_percentile": storage_dtype,
                "daily_below_p10": storage_dtype,
                "daily_history_count": np.dtype("int16"),
            }
            pentad_names = {
                "pentad_values": storage_dtype,
                "pentad_valid_day_counts": np.dtype("int8"),
                "pentad_percentile": storage_dtype,
                "pentad_below_p10": storage_dtype,
                "pentad_below_p20": storage_dtype,
                "pentad_history_count": np.dtype("int16"),
                "pentad_q10": storage_dtype,
                "pentad_q20": storage_dtype,
                "pentad_q40": storage_dtype,
            }
            for year in pending_years:
                for name, dtype in daily_names.items():
                    writers[(year, name)] = _new_metric_writer(
                        metric_root,
                        str(layer),
                        year,
                        name,
                        dtype=dtype,
                        shape=(len(dates_by_year[year]), len(crosswalk)),
                    )
                for name, dtype in pentad_names.items():
                    writers[(year, name)] = _new_metric_writer(
                        metric_root,
                        str(layer),
                        year,
                        name,
                        dtype=dtype,
                        shape=(73, len(crosswalk)),
                    )

            historical_dates = tuple(
                value for year in historical_years for value in dates_by_year[year]
            )
            target_dates = tuple(
                value for year in pending_years for value in dates_by_year[year]
            )
            expected_counts: dict[int, np.ndarray] = {}
            for start in range(0, len(crosswalk), cell_block_size):
                if not pending_years:
                    break
                stop = min(start + cell_block_size, len(crosswalk))
                history_values_by_year = {
                    year: np.ma.filled(
                        datasets[year].variables[str(layer)][:, start:stop], np.nan
                    ).astype(np.float64, copy=False)
                    for year in historical_years
                }
                target_values_by_year = {
                    year: np.ma.filled(
                        datasets[year].variables[str(layer)][:, start:stop], np.nan
                    ).astype(np.float64, copy=False)
                    for year in pending_years
                }
                historical_values = np.concatenate(
                    [history_values_by_year[year] for year in historical_years], axis=0
                )
                target_values = np.concatenate(
                    [target_values_by_year[year] for year in pending_years], axis=0
                )
                daily_metrics = apply_daily_p10_climatology(
                    target_dates,
                    target_values,
                    historical_dates,
                    historical_values,
                    half_width_days=int(
                        request.config.data["gleam"][
                            "daily_p10_calendar_half_width_days"
                        ]
                    ),
                    minimum_history_fraction=minimum_fraction,
                )
                row_start = 0
                for year in pending_years:
                    row_stop = row_start + len(dates_by_year[year])
                    writers[(year, "daily_q10")][:, start:stop] = daily_metrics.q10[
                        row_start:row_stop
                    ]
                    writers[(year, "daily_percentile")][
                        :, start:stop
                    ] = daily_metrics.percentile[row_start:row_stop]
                    writers[(year, "daily_below_p10")][
                        :, start:stop
                    ] = daily_metrics.below_p10[row_start:row_stop]
                    writers[(year, "daily_history_count")][
                        :, start:stop
                    ] = daily_metrics.history_count[row_start:row_stop]
                    expected_counts.setdefault(
                        year,
                        np.asarray(
                            daily_metrics.expected_history_count[row_start:row_stop],
                            dtype=np.int16,
                        ),
                    )
                    row_start = row_stop

                history_pentads = {
                    year: daily_values_to_pentads(
                        dates_by_year[year], history_values_by_year[year]
                    )
                    for year in historical_years
                }
                historical_pentad_values = np.stack(
                    [history_pentads[year].values for year in historical_years],
                    axis=0,
                )
                for year in pending_years:
                    target_pentad = daily_values_to_pentads(
                        dates_by_year[year], target_values_by_year[year]
                    )
                    target_metrics = apply_pentad_climatology(
                        target_pentad.values,
                        historical_pentad_values,
                        min_historical_years=minimum_historical_years,
                    )
                    writers[(year, "pentad_values")][:, start:stop] = target_pentad.values
                    writers[(year, "pentad_valid_day_counts")][
                        :, start:stop
                    ] = target_pentad.valid_day_counts
                    for name, values in (
                        ("pentad_percentile", target_metrics.percentile),
                        ("pentad_below_p10", target_metrics.below_p10),
                        ("pentad_below_p20", target_metrics.below_p20),
                        ("pentad_history_count", target_metrics.history_count),
                        ("pentad_q10", target_metrics.q10),
                        ("pentad_q20", target_metrics.q20),
                        ("pentad_q40", target_metrics.q40),
                    ):
                        writers[(year, name)][:, start:stop] = values

            for writer in writers.values():
                writer.flush()
            file_count += len(writers)
            del writers
            for year in pending_years:
                expected_path = _metric_path(
                    metric_root,
                    str(layer),
                    year,
                    "daily_expected_history_count",
                )
                _save_npy_new(expected_path, expected_counts[year])
                file_count += 1
                metadata_path = expected_path.parent / "metadata.json"
                _write_json_new(
                    metadata_path,
                    {
                        "layer": str(layer),
                        "year": year,
                        "days": len(dates_by_year[year]),
                        "pentads": 73,
                        "cells": len(crosswalk),
                        "historical_years": list(historical_years),
                        "minimum_historical_years": minimum_historical_years,
                        "daily_calendar_half_width_days": int(
                            request.config.data["gleam"][
                                "daily_p10_calendar_half_width_days"
                            ]
                        ),
                        "strict_state_rules": ["SM < Q10", "SM < Q20"],
                    },
                )
                file_count += 1
                daily_cell_rows += len(dates_by_year[year]) * len(crosswalk)
                pentad_cell_rows += 73 * len(crosswalk)
            layer_summaries[str(layer)] = {
                "target_years": list(target_years),
                "historical_years": list(historical_years),
                "minimum_historical_years": minimum_historical_years,
            }

    metadata_path = request.work_dir / "gleam_baseline_metadata.json"
    if request.pipeline.resume and metadata_path.exists():
        _archive_incomplete(metadata_path)
    _write_json_new(
        metadata_path,
        {
            "layers": layer_summaries,
            "cell_block_size": cell_block_size,
            "storage_dtype": str(storage_dtype),
            "calendar_pentads": 73,
            "february_29_in_pentads": False,
        },
    )
    return StageOutcome(
        artifacts={"metrics": metric_root, "metadata": metadata_path},
        row_counts={
            "metric_files": file_count,
            "daily_target_cell_rows": daily_cell_rows,
            "pentad_target_cell_rows": pentad_cell_rows,
            "cells": len(crosswalk),
        },
        extra={"layers": layer_summaries},
    )


def _load_gleam_target_inputs(
    request: StageRequest,
    layer: str,
    *,
    years: Sequence[int] | None = None,
    cell_slice: slice | None = None,
) -> tuple[
    dict[int, tuple[date, ...]],
    dict[int, np.ndarray],
    dict[int, Any],
    dict[int, np.ndarray],
    dict[int, Any],
]:
    from .gleam import DailyTargetMetrics, PentadTargetMetrics

    daily_root = _stage_file(request.context, "gleam_daily", "daily_cache")
    metric_root = _stage_file(request.context, "gleam_baseline", "metrics")
    all_expected_ids = pd.read_parquet(
        _stage_file(request.context, "grid", "crosswalk.parquet")
    ).sort_values("era01_cell_id")["era01_cell_id"].to_numpy(dtype=np.int64)
    selector = slice(None) if cell_slice is None else cell_slice
    expected_ids = all_expected_ids[selector]
    dates: dict[int, tuple[date, ...]] = {}
    values: dict[int, np.ndarray] = {}
    daily_metrics: dict[int, DailyTargetMetrics] = {}
    pentad_values: dict[int, np.ndarray] = {}
    pentad_metrics: dict[int, PentadTargetMetrics] = {}
    load_years = tuple(
        sorted(
            int(value)
            for value in (
                _event_context_years(request.config) if years is None else years
            )
        )
    )
    for year in load_years:
        current_dates, cell_ids, current_values = _read_gleam_partition(
            daily_root, layer, int(year), cell_slice=cell_slice
        )
        if not np.array_equal(cell_ids, expected_ids):
            raise StageValidationError(
                f"GLEAM {layer} {year} cell order differs from crosswalk"
            )
        dates[int(year)] = current_dates
        values[int(year)] = current_values
        load = lambda name: np.load(  # noqa: E731 - compact frozen metric loader
            _metric_path(metric_root, layer, int(year), name), mmap_mode="r"
        )[:, selector]
        daily_metrics[int(year)] = DailyTargetMetrics(
            q10=load("daily_q10"),
            percentile=load("daily_percentile"),
            below_p10=load("daily_below_p10"),
            history_count=load("daily_history_count"),
            expected_history_count=np.load(
                _metric_path(
                    metric_root,
                    layer,
                    int(year),
                    "daily_expected_history_count",
                ),
                mmap_mode="r",
            ),
        )
        pentad_values[int(year)] = load("pentad_values")
        pentad_metrics[int(year)] = PentadTargetMetrics(
            percentile=load("pentad_percentile"),
            below_p10=load("pentad_below_p10"),
            below_p20=load("pentad_below_p20"),
            history_count=load("pentad_history_count"),
            q10=load("pentad_q10"),
            q20=load("pentad_q20"),
            q40=load("pentad_q40"),
        )
    return dates, values, daily_metrics, pentad_values, pentad_metrics


def _partition_token(value: object) -> str:
    """Return a filesystem-safe, deterministic audit partition token."""

    text_value = str(value).strip().lower()
    normalized = "".join(
        character if character.isalnum() or character in {"-", "_"} else "-"
        for character in text_value
    ).strip("-")
    if not normalized:
        raise StageValidationError(f"Empty audit partition token: {value!r}")
    return normalized


def _parquet_frames_equal(expected: pd.DataFrame, observed: pd.DataFrame) -> bool:
    """Compare one bounded partition after a Parquet round trip."""

    if list(expected.columns) != list(observed.columns):
        return False
    try:
        pd.testing.assert_frame_equal(
            expected.reset_index(drop=True),
            observed.reset_index(drop=True),
            check_dtype=False,
            check_exact=True,
            check_names=True,
        )
    except AssertionError:
        return False
    return True


def _write_parquet_partition_resumable(
    path: Path,
    frame: pd.DataFrame,
    *,
    resume: bool,
) -> str:
    """Write one immutable partition, repairing only a damaged resumed file."""

    repaired = False
    if path.exists():
        if not resume:
            raise FileExistsError(path)
        try:
            observed = pd.read_parquet(path)
        except Exception:
            _archive_incomplete(path)
            repaired = True
        else:
            if _parquet_frames_equal(frame, observed):
                return "reused"
            _archive_incomplete(path)
            repaired = True
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(f".{path.name}.{uuid.uuid4().hex}.partial")
    frame.to_parquet(partial, index=False)
    os.rename(partial, path)
    return "repaired" if repaired else "written"


def _event_partition_years(
    frame: pd.DataFrame,
    *,
    audit_kind: str,
) -> pd.Series:
    """Return a complete-event start year or a bridge window year."""

    values = pd.Series(np.nan, index=frame.index, dtype=np.float64)
    if audit_kind == "bridge":
        if "year" not in frame:
            raise StageValidationError("Event-window bridge rows lack window year")
        values = pd.to_numeric(frame["year"], errors="coerce")
        if values.isna().any():
            raise StageValidationError(
                "Event-window bridge rows contain an invalid window year"
            )
        return values.astype(np.int32)
    if audit_kind != "event":
        raise ValueError(f"Unsupported audit kind: {audit_kind}")

    found = False
    for name in ("event_start_year", "start_year"):
        if name not in frame:
            continue
        found = True
        values = values.fillna(pd.to_numeric(frame[name], errors="coerce"))
    for name in ("start_date", "start"):
        if name not in frame:
            continue
        found = True
        values = values.fillna(
            pd.to_datetime(frame[name], errors="coerce").dt.year
        )
    if not found:
        raise StageValidationError("Audit rows lack a year anchor")
    if values.isna().any():
        raise StageValidationError("Audit rows contain an invalid year anchor")
    return values.astype(np.int32)


def _write_event_block_partitions(
    root: Path,
    rows: Sequence[Mapping[str, Any]],
    *,
    layer: str,
    block_index: int,
    audit_kind: str,
    resume: bool,
) -> dict[str, int]:
    """Persist one bounded event block by family/year/cell-block."""

    stats = {"rows": 0, "written": 0, "reused": 0, "repaired": 0}
    if not rows:
        return stats
    frame = pd.DataFrame.from_records(rows)
    if "event_family" not in frame:
        raise StageValidationError("Partitioned event audit lacks event_family")
    years = _event_partition_years(frame, audit_kind=audit_kind)
    grouping = pd.DataFrame(
        {
            "family": frame["event_family"].astype(str),
            "year": years,
        },
        index=frame.index,
    )
    part_name = f"part-{_partition_token(layer)}.parquet"
    for (family, year), indices in grouping.groupby(
        ["family", "year"], sort=True, observed=True
    ).groups.items():
        partition = frame.loc[list(indices)].reset_index(drop=True)
        path = (
            root
            / f"family-{_partition_token(family)}"
            / f"year-{int(year):04d}"
            / f"cell-block-{int(block_index):06d}"
            / part_name
        )
        status = _write_parquet_partition_resumable(
            path, partition, resume=resume
        )
        stats[status] += 1
        stats["rows"] += len(partition)
    return stats


def _ensure_partition_dataset(
    root: Path,
    *,
    schema_name: str,
    resume: bool,
) -> None:
    """Create a readable empty dataset and deterministic dataset metadata."""

    root.mkdir(parents=True, exist_ok=True)
    if not any(root.rglob("*.parquet")):
        _write_parquet_partition_resumable(
            root / "empty.parquet", pd.DataFrame(), resume=resume
        )
    metadata = {
        "schema_name": schema_name,
        "format": "parquet-dataset",
        "partition_order": ["event_family", "year", "cell_block"],
        "overwrite_policy": "immutable; damaged resumed partitions archived as .incomplete",
    }
    metadata_path = root / "_DATASET.json"
    if metadata_path.exists():
        if not resume:
            raise FileExistsError(metadata_path)
        try:
            observed = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            _archive_incomplete(metadata_path)
        else:
            if observed == metadata:
                return
            _archive_incomplete(metadata_path)
    _write_json_new(metadata_path, metadata)


def _handle_events(request: StageRequest) -> StageOutcome:
    """Construct compound daily, pentad-overlap, and hot-FD audit layers."""

    from .aggregate import (
        _prefix_sum_and_count,
        _python_dates,
        _window_slice_offset,
        _window_sum_count,
        _window_template,
    )
    from .compound import (
        bridge_daily_compound_event,
        classify_hot_flash_drought_events,
        compound_event_table,
        compute_hot_pentad_metrics,
        detect_daily_compound_events,
        hot_flash_drought_table,
    )
    from .core import calendar_pentad, detect_flash_droughts, required_valid_count
    from .era5 import attach_daily_temperature_thresholds, load_daily_dates

    phenology_source = _stage_file(
        request.context, "phenology", "phenology_panel.parquet"
    )
    years = tuple(sorted(int(value) for value in request.scope.years))
    event_years = _event_context_years(request.config)
    windows = tuple(request.config.windows)
    phenology_columns = [
        "era01_cell_id",
        "grid_id_v3",
        "lat_idx",
        "lon_idx",
        "latitude",
        "longitude",
        "lat10",
        "lon10",
        "year",
        *(
            name
            for window in windows
            for name in (
                f"win_{window}_start",
                f"win_{window}_end",
                f"win_{window}_days",
            )
        ),
    ]
    panel = pd.read_parquet(
        phenology_source,
        columns=phenology_columns,
        filters=[("year", "in", list(years))],
    )
    minimum_coverage = float(
        request.config.data["quality"]["minimum_window_coverage"]
    )
    cell_block_size = int(
        request.config.data.get("runtime", {}).get("gleam_cell_block_size", 128)
    )
    if cell_block_size <= 0:
        raise ValueError("runtime.gleam_cell_block_size must be positive")
    daily_root = _stage_file(request.context, "era_daily", "daily_cache")
    threshold_root = _stage_file(request.context, "era_baseline", "thresholds")
    temperature_dates = {
        year: tuple(_python_dates(load_daily_dates(daily_root, year)))
        for year in event_years
    }
    all_dates = tuple(
        value for year in event_years for value in temperature_dates[year]
    )
    long, bounds = _window_template(panel, windows, years)
    n_cells = int(panel["era01_cell_id"].nunique())
    cells = (
        panel[["era01_cell_id", "grid_id_v3"]]
        .drop_duplicates("era01_cell_id")
        .sort_values("era01_cell_id")
        .reset_index(drop=True)
    )
    if len(long) != n_cells * len(years) * len(windows):
        raise StageValidationError("Compound long template is not balanced")

    event_path = request.work_dir / "compound_events.parquet"
    bridge_path = request.work_dir / "compound_event_window_bridge.parquet"
    hot_flash_path = request.work_dir / "hot_flash_drought_classification.parquet"
    partition_stats = {
        "events": {"rows": 0, "written": 0, "reused": 0, "repaired": 0},
        "bridges": {"rows": 0, "written": 0, "reused": 0, "repaired": 0},
        "hot_flash": {"rows": 0, "written": 0, "reused": 0, "repaired": 0},
    }
    for raw_layer in request.config.data["gleam"]["layers"]:
        layer = str(raw_layer)
        prefix = f"compound_{layer.lower()}"
        coverage_name = f"{prefix}_hot_p10_coverage"
        valid_days_name = f"{prefix}_hot_p10_valid_days"
        overlap_coverage_name = f"{prefix}_tx90_sm_pct_coverage"
        overlap_valid_name = f"{prefix}_tx90_sm_pct_valid_days"
        overlap_q20_name = f"{prefix}_tx90_sm20_overlap_days"
        overlap_q10_name = f"{prefix}_tx90_sm10_overlap_days"
        for name in (
            coverage_name,
            valid_days_name,
            overlap_coverage_name,
            overlap_valid_name,
            overlap_q20_name,
            overlap_q10_name,
        ):
            long[name] = np.nan

        variant_fields = (
            "any",
            "count",
            "total_active_duration_days",
            "total_span_duration_days",
            "total_gap_duration_days",
            "max_active_duration_days",
            "max_span_duration_days",
            "heat_excess_cdays",
            "sm_deficit_m3m3_days",
            "left_censored_any",
            "right_censored_any",
        )
        daily_valid_windows = np.zeros(len(long), dtype=bool)
        for variant in ("main_gap0", "sensitivity_gap2"):
            for field_name in variant_fields:
                long[f"{prefix}_hot_p10_{variant}_{field_name}"] = np.nan

        for block_start in range(0, n_cells, cell_block_size):
            block_stop = min(block_start + cell_block_size, n_cells)
            block_slice = slice(block_start, block_stop)
            block_width = block_stop - block_start
            block_index = block_start // cell_block_size
            block_event_rows: list[dict[str, Any]] = []
            block_bridge_rows: list[dict[str, Any]] = []
            block_hot_flash_rows: list[dict[str, Any]] = []
            temperature = {
                year: attach_daily_temperature_thresholds(
                    daily_root,
                    threshold_root,
                    year,
                    cell_slice=block_slice,
                )
                for year in event_years
            }
            (
                daily_dates,
                daily_values,
                daily_metrics,
                _pentad_values,
                pentad_metrics,
            ) = _load_gleam_target_inputs(
                request,
                layer,
                cell_slice=block_slice,
            )
            for year in event_years:
                if tuple(daily_dates[year]) != temperature_dates[year]:
                    raise StageValidationError(
                        f"ERA and GLEAM daily dates differ for {layer} {year}"
                    )
                if daily_values[year].shape[1] != block_width:
                    raise StageValidationError(
                        f"GLEAM {layer} {year} cell block has invalid width"
                    )
                if temperature[year]["era5u8_tmax_c"].shape[1] != block_width:
                    raise StageValidationError(
                        f"ERA {year} cell block has invalid width"
                    )

            for year in years:
                tmax = np.asarray(
                    temperature[year]["era5u8_tmax_c"], dtype=float
                )
                p90 = np.asarray(
                    temperature[year]["era5u8_tmax_p90_c"], dtype=float
                )
                sm = np.asarray(daily_values[year], dtype=float)
                sm_p10 = np.asarray(daily_metrics[year].q10, dtype=float)
                valid_compound = (
                    np.isfinite(tmax)
                    & np.isfinite(p90)
                    & np.isfinite(sm)
                    & np.isfinite(sm_p10)
                )
                compound_prefix, compound_counts = _prefix_sum_and_count(
                    valid_compound.astype(np.float64)
                )

                dates = daily_dates[year]
                pentad_index = np.asarray(
                    [
                        -1
                        if (value := calendar_pentad(day)) is None
                        else int(value) - 1
                        for day in dates
                    ],
                    dtype=np.int16,
                )
                daily_percentile = np.full(
                    (len(dates), block_width), np.nan, dtype=float
                )
                represented = pentad_index >= 0
                daily_percentile[represented] = np.asarray(
                    pentad_metrics[year].percentile, dtype=float
                )[pentad_index[represented]]
                hot_state = np.asarray(
                    temperature[year]["era5u8_tx90_state"], dtype=np.int8
                )
                valid_overlap = (hot_state >= 0) & np.isfinite(daily_percentile)
                primary_overlap = np.where(
                    valid_overlap,
                    (hot_state == 1) & (daily_percentile < 20.0),
                    0.0,
                ).astype(float)
                strict_overlap = np.where(
                    valid_overlap,
                    (hot_state == 1) & (daily_percentile < 10.0),
                    0.0,
                ).astype(float)
                overlap_valid_prefix, overlap_valid_counts = _prefix_sum_and_count(
                    valid_overlap.astype(float)
                )
                primary_prefix, primary_counts = _prefix_sum_and_count(primary_overlap)
                strict_prefix, strict_counts = _prefix_sum_and_count(strict_overlap)

                for window_index, window in enumerate(windows):
                    full_destination = _window_slice_offset(
                        year, window_index, n_cells, windows, years
                    )
                    destination = range(
                        full_destination.start + block_start,
                        full_destination.start + block_stop,
                    )
                    all_starts, all_ends, all_window_days = bounds[(year, window)]
                    starts = all_starts[block_slice]
                    ends = all_ends[block_slice]
                    window_days = all_window_days[block_slice]
                    compound_valid, _ = _window_sum_count(
                        compound_prefix, compound_counts, starts, ends
                    )
                    required = np.asarray(
                        [
                            required_valid_count(int(value), minimum_coverage)
                            if np.isfinite(value)
                            else 1
                            for value in window_days
                        ],
                        dtype=np.int32,
                    )
                    valid_window = np.isfinite(window_days) & (
                        compound_valid >= required
                    )
                    daily_valid_windows[np.asarray(destination)] = valid_window
                    coverage = np.divide(
                        compound_valid,
                        window_days,
                        out=np.full(block_width, np.nan),
                        where=np.isfinite(window_days) & (window_days > 0),
                    )
                    long.loc[destination, coverage_name] = coverage
                    long.loc[destination, valid_days_name] = compound_valid
                    for variant in ("main_gap0", "sensitivity_gap2"):
                        for field_name in variant_fields:
                            long.loc[
                                destination,
                                f"{prefix}_hot_p10_{variant}_{field_name}",
                            ] = np.where(valid_window, 0.0, np.nan)

                    overlap_valid_days, _ = _window_sum_count(
                        overlap_valid_prefix, overlap_valid_counts, starts, ends
                    )
                    overlap_ok = np.isfinite(window_days) & (
                        overlap_valid_days >= required
                    )
                    overlap_coverage = np.divide(
                        overlap_valid_days,
                        window_days,
                        out=np.full(block_width, np.nan),
                        where=np.isfinite(window_days) & (window_days > 0),
                    )
                    primary_days, _ = _window_sum_count(
                        primary_prefix, primary_counts, starts, ends
                    )
                    strict_days, _ = _window_sum_count(
                        strict_prefix, strict_counts, starts, ends
                    )
                    primary_days[~overlap_ok] = np.nan
                    strict_days[~overlap_ok] = np.nan
                    long.loc[destination, overlap_coverage_name] = overlap_coverage
                    long.loc[destination, overlap_valid_name] = overlap_valid_days
                    long.loc[destination, overlap_q20_name] = primary_days
                    long.loc[destination, overlap_q10_name] = strict_days

            all_tmax = np.concatenate(
                [
                    np.asarray(temperature[year]["era5u8_tmax_c"])
                    for year in event_years
                ],
                axis=0,
            )
            all_p90 = np.concatenate(
                [
                    np.asarray(temperature[year]["era5u8_tmax_p90_c"])
                    for year in event_years
                ],
                axis=0,
            )
            all_sm = np.concatenate(
                [np.asarray(daily_values[year]) for year in event_years], axis=0
            )
            all_sm_p10 = np.concatenate(
                [np.asarray(daily_metrics[year].q10) for year in event_years],
                axis=0,
            )
            if any(
                values.shape != (len(all_dates), block_width)
                for values in (all_tmax, all_p90, all_sm, all_sm_p10)
            ):
                raise StageValidationError(
                    f"Compound event block axes are incomplete for {layer}"
                )

            for local_index, global_index in enumerate(
                range(block_start, block_stop)
            ):
                cell = cells.iloc[global_index]
                source_valid = (
                    np.isfinite(all_tmax[:, local_index])
                    & np.isfinite(all_p90[:, local_index])
                    & np.isfinite(all_sm[:, local_index])
                    & np.isfinite(all_sm_p10[:, local_index])
                )
                compound_events = detect_daily_compound_events(
                    all_dates,
                    all_tmax[:, local_index],
                    all_p90[:, local_index],
                    all_sm[:, local_index],
                    all_sm_p10[:, local_index],
                    layer=layer,
                    minimum_active_days=int(
                        request.config.data["compound"]["daily_hot_sm_min_days"]
                    ),
                )
                variant_counter = {"main_gap0": 0, "sensitivity_gap2": 0}
                for event in compound_events:
                    variant_counter[event.variant] += 1
                    if not _event_overlaps_output_years(
                        event.start, event.end, years
                    ):
                        continue
                    event_id = (
                        f"{int(cell.era01_cell_id)}:{prefix}_hot_p10_"
                        f"{event.variant}:{variant_counter[event.variant]:04d}"
                    )
                    event_payload = compound_event_table([event]).iloc[0].to_dict()
                    event_payload["event_id"] = event_id
                    target_event_years = [
                        year
                        for year in years
                        if event.end >= date(year, 1, 1)
                        and event.start <= date(year, 12, 31)
                    ]
                    if not target_event_years:
                        raise StageValidationError(
                            "Retained compound event lacks a target-year overlap"
                        )
                    source_left_censored, source_right_censored = (
                        _source_censor_flags(
                            all_dates,
                            source_valid,
                            start=event.start,
                            end=event.end,
                        )
                    )
                    block_event_rows.append(
                        {
                            "era01_cell_id": int(cell.era01_cell_id),
                            "grid_id_v3": int(cell.grid_id_v3),
                            "event_family": "daily_hot_sm_p10",
                            "first_target_overlap_year": min(target_event_years),
                            "event_start_year": int(event.start.year),
                            "event_end_year": int(event.end.year),
                            "source_left_censored": source_left_censored,
                            "source_right_censored": source_right_censored,
                            **event_payload,
                        }
                    )
                    for year in years:
                        year_start = date(year, 1, 1)
                        year_end = date(year, 12, 31)
                        if event.end < year_start or event.start > year_end:
                            continue
                        for window_index, window in enumerate(windows):
                            starts, ends, _window_days = bounds[(year, window)]
                            if not np.isfinite(
                                starts[global_index]
                            ) or not np.isfinite(ends[global_index]):
                                continue
                            window_start = year_start + timedelta(
                                days=int(starts[global_index]) - 1
                            )
                            window_end = year_start + timedelta(
                                days=int(ends[global_index]) - 1
                            )
                            bridge = bridge_daily_compound_event(
                                event,
                                window=window,
                                window_start=window_start,
                                window_end=window_end,
                            )
                            if bridge is None:
                                continue
                            row_index = (
                                _window_slice_offset(
                                    year,
                                    window_index,
                                    n_cells,
                                    windows,
                                    years,
                                ).start
                                + global_index
                            )
                            if not daily_valid_windows[row_index]:
                                continue
                            stem = f"{prefix}_hot_p10_{event.variant}"
                            long.at[row_index, f"{stem}_any"] = 1.0
                            long.at[row_index, f"{stem}_count"] += 1.0
                            long.at[
                                row_index,
                                f"{stem}_total_active_duration_days",
                            ] += bridge.active_duration
                            long.at[
                                row_index,
                                f"{stem}_total_span_duration_days",
                            ] += bridge.span_duration
                            long.at[
                                row_index,
                                f"{stem}_total_gap_duration_days",
                            ] += bridge.gap_duration
                            long.at[
                                row_index,
                                f"{stem}_max_active_duration_days",
                            ] = max(
                                long.at[
                                    row_index,
                                    f"{stem}_max_active_duration_days",
                                ],
                                bridge.active_duration,
                            )
                            long.at[
                                row_index,
                                f"{stem}_max_span_duration_days",
                            ] = max(
                                long.at[
                                    row_index,
                                    f"{stem}_max_span_duration_days",
                                ],
                                bridge.span_duration,
                            )
                            long.at[
                                row_index, f"{stem}_heat_excess_cdays"
                            ] += bridge.heat_excess_cdays
                            long.at[
                                row_index, f"{stem}_sm_deficit_m3m3_days"
                            ] += bridge.sm_deficit_m3m3_days
                            long.at[
                                row_index, f"{stem}_left_censored_any"
                            ] = max(
                                long.at[
                                    row_index,
                                    f"{stem}_left_censored_any",
                                ],
                                float(bridge.left_censored),
                            )
                            long.at[
                                row_index, f"{stem}_right_censored_any"
                            ] = max(
                                long.at[
                                    row_index,
                                    f"{stem}_right_censored_any",
                                ],
                                float(bridge.right_censored),
                            )
                            bridge_payload = asdict(bridge)
                            bridge_payload["event_id"] = event_id
                            block_bridge_rows.append(
                                {
                                    "era01_cell_id": int(cell.era01_cell_id),
                                    "grid_id_v3": int(cell.grid_id_v3),
                                    "event_family": "daily_hot_sm_p10",
                                    "year": year,
                                    "source_left_censored": source_left_censored,
                                    "source_right_censored": source_right_censored,
                                    **bridge_payload,
                                }
                            )

                flash_counters = {"main": 0, "strict": 0}
                for year_group in _contiguous_year_groups(event_years):
                    group_dates = tuple(
                        value for year in year_group for value in daily_dates[year]
                    )
                    group_temperature_percentile = np.concatenate(
                        [
                            np.asarray(
                                temperature[year][
                                    "era5u8_tmax_historical_percentile"
                                ]
                            )[:, local_index]
                            for year in year_group
                        ]
                    )
                    hot_pentads = compute_hot_pentad_metrics(
                        group_dates,
                        group_temperature_percentile,
                        minimum_coverage=minimum_coverage,
                    )
                    group_percentile = np.concatenate(
                        [
                            np.asarray(
                                pentad_metrics[year].percentile
                            )[:, local_index]
                            for year in year_group
                        ]
                    )
                    normalized_percentile = [
                        None if not np.isfinite(value) else float(value)
                        for value in group_percentile
                    ]
                    group_pentad_years = np.repeat(
                        np.asarray(year_group, dtype=np.int16), 73
                    )
                    group_pentad_numbers = np.tile(
                        np.arange(1, 74, dtype=np.int8), len(year_group)
                    )
                    global_offset = event_years.index(year_group[0]) * 73
                    for variant, minimum_span, recovery_confirm in (
                        ("main", 3, 1),
                        ("strict", 4, 2),
                    ):
                        flash_events = detect_flash_droughts(
                            normalized_percentile,
                            min_span_pentads=minimum_span,
                            recovery_confirm=recovery_confirm,
                        )
                        classifications = classify_hot_flash_drought_events(
                            flash_events,
                            group_pentad_years,
                            group_pentad_numbers,
                            hot_pentads,
                            minimum_coverage=minimum_coverage,
                        )
                        table = hot_flash_drought_table(classifications)
                        for row in table.to_dict("records"):
                            flash_counters[variant] += 1
                            event_year_support = set(
                                int(value)
                                for value in group_pentad_years[
                                    int(row["start_index"]) : int(
                                        row["end_index"]
                                    )
                                    + 1
                                ]
                            )
                            if not event_year_support.intersection(years):
                                continue
                            target_event_years = sorted(
                                event_year_support.intersection(years)
                            )
                            valid_group_percentile = np.isfinite(
                                group_percentile
                            )
                            row["source_left_censored"] = not bool(
                                valid_group_percentile[
                                    : int(row["start_index"])
                                ].any()
                            )
                            row["source_right_censored"] = not bool(
                                valid_group_percentile[
                                    int(row["end_index"]) + 1 :
                                ].any()
                            )
                            row["start_index"] = (
                                int(row["start_index"]) + global_offset
                            )
                            row["end_index"] = (
                                int(row["end_index"]) + global_offset
                            )
                            row["event_id"] = (
                                f"{int(cell.era01_cell_id)}:gleam43a_"
                                f"{layer.lower()}_fd_{variant}:"
                                f"{flash_counters[variant]:04d}"
                            )
                            block_hot_flash_rows.append(
                                {
                                    "era01_cell_id": int(cell.era01_cell_id),
                                    "grid_id_v3": int(cell.grid_id_v3),
                                    "event_family": "hot_flash_drought",
                                    "first_target_overlap_year": min(target_event_years),
                                    "event_start_year": min(event_year_support),
                                    "event_end_year": max(event_year_support),
                                    "layer": layer,
                                    "fd_variant": variant,
                                    **row,
                                }
                            )

            for stats_name, dataset_root, rows, audit_kind in (
                ("events", event_path, block_event_rows, "event"),
                ("bridges", bridge_path, block_bridge_rows, "bridge"),
                ("hot_flash", hot_flash_path, block_hot_flash_rows, "event"),
            ):
                current_stats = _write_event_block_partitions(
                    dataset_root,
                    rows,
                    layer=layer,
                    block_index=block_index,
                    audit_kind=audit_kind,
                    resume=request.pipeline.resume,
                )
                for key, value in current_stats.items():
                    partition_stats[stats_name][key] += int(value)

            del (
                temperature,
                daily_values,
                daily_metrics,
                pentad_metrics,
                _pentad_values,
                all_tmax,
                all_p90,
                all_sm,
                all_sm_p10,
                block_event_rows,
                block_bridge_rows,
                block_hot_flash_rows,
            )

    long_path = request.work_dir / "compound_window_long.parquet"
    _write_parquet_partition_resumable(
        long_path, long, resume=request.pipeline.resume
    )
    _ensure_partition_dataset(
        event_path,
        schema_name="compound-complete-events-v1",
        resume=request.pipeline.resume,
    )
    _ensure_partition_dataset(
        bridge_path,
        schema_name="compound-event-window-bridge-v1",
        resume=request.pipeline.resume,
    )
    _ensure_partition_dataset(
        hot_flash_path,
        schema_name="hot-flash-drought-classification-v1",
        resume=request.pipeline.resume,
    )
    return StageOutcome(
        artifacts={
            "compound_long": long_path,
            "compound_events": event_path,
            "compound_event_bridge": bridge_path,
            "hot_flash_classification": hot_flash_path,
        },
        row_counts={
            "compound_long_rows": len(long),
            "compound_events": partition_stats["events"]["rows"],
            "compound_event_bridges": partition_stats["bridges"]["rows"],
            "hot_flash_classifications": partition_stats["hot_flash"]["rows"],
        },
        extra={
            "cell_block_size": cell_block_size,
            "partition_stats": partition_stats,
        },
    )


def _merge_window_metrics(
    base: pd.DataFrame,
    addition: pd.DataFrame,
    *,
    source: str,
) -> pd.DataFrame:
    """Merge only numeric climate metrics on the canonical long key."""

    keys = ["era01_cell_id", "year", "window"]
    missing = sorted(set(keys).difference(addition.columns))
    if missing:
        raise StageValidationError(f"{source} lacks long keys: {missing}")
    if addition.duplicated(keys).any():
        raise StageValidationError(f"{source} is not unique by cell-year-window")
    if len(addition) != len(base):
        raise StageValidationError(
            f"{source} has {len(addition):,} rows; canonical support has {len(base):,}"
        )
    excluded = {
        *keys,
        "grid_id",
        "grid_id_v3",
        "lat_idx",
        "lon_idx",
        "latitude",
        "longitude",
        "lat10",
        "lon10",
        "source_row",
        "cell_index",
    }
    metric_columns: list[str] = []
    converted = addition.copy()
    for column in addition.columns:
        if column in excluded or column in base.columns:
            continue
        if pd.api.types.is_numeric_dtype(addition[column]):
            metric_columns.append(column)
            continue
        numeric = pd.to_numeric(addition[column], errors="coerce")
        invalid = addition[column].notna() & numeric.isna()
        if invalid.any():
            raise StageValidationError(
                f"{source} contains nonnumeric climate field {column}"
            )
        converted[column] = numeric
        metric_columns.append(column)
    if not metric_columns:
        raise StageValidationError(f"{source} contains no numeric climate metrics")
    collisions = sorted(set(metric_columns).intersection(base.columns))
    if collisions:
        raise StageValidationError(f"{source} metric collisions: {collisions}")
    merged = base.merge(
        converted[keys + metric_columns],
        on=keys,
        how="left",
        validate="one_to_one",
        sort=False,
        indicator="__stage_alignment",
    )
    if not merged["__stage_alignment"].eq("both").all():
        unmatched = int(merged["__stage_alignment"].ne("both").sum())
        raise StageValidationError(
            f"{source} does not cover {unmatched:,} canonical long keys"
        )
    merged = merged.drop(columns="__stage_alignment")
    if len(merged) != len(base) or merged[metric_columns].shape[0] != len(base):
        raise StageValidationError(f"{source} changed canonical long row support")
    return merged


def _tag_audit(frame: pd.DataFrame, source_family: str) -> pd.DataFrame:
    output = frame.copy()
    output.insert(0, "source_family", source_family)
    return output


def _iter_audit_frames(payload: pd.DataFrame | Path) -> Iterable[pd.DataFrame]:
    """Yield bounded audit frames from an in-memory source or dataset path."""

    if isinstance(payload, pd.DataFrame):
        if not payload.empty:
            yield payload
        return
    path = Path(payload)
    files = [path] if path.is_file() else sorted(path.rglob("*.parquet"))
    for file_path in files:
        if file_path.name.startswith("."):
            continue
        frame = pd.read_parquet(file_path)
        if not frame.empty:
            yield frame


def _tag_audit_arrow(frame: pd.DataFrame, source_family: str) -> Any:
    import pyarrow as pa

    table = pa.Table.from_pandas(frame, preserve_index=False).replace_schema_metadata()
    source = pa.array([str(source_family)] * len(frame), type=pa.string())
    return table.add_column(0, pa.field("source_family", pa.string()), source)


def _align_audit_arrow_table(table: Any, schema: Any) -> Any:
    import pyarrow as pa

    arrays: list[Any] = []
    names = set(table.column_names)
    for field in schema:
        if field.name not in names:
            arrays.append(pa.nulls(len(table), type=field.type))
            continue
        values = table[field.name]
        if values.type != field.type:
            values = values.cast(field.type, safe=False)
        arrays.append(values)
    return pa.Table.from_arrays(arrays, schema=schema)


def _write_arrow_partition_new(path: Path, table: Any) -> None:
    import pyarrow.parquet as pq

    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(f".{path.name}.{uuid.uuid4().hex}.partial")
    pq.write_table(table, partial, compression="zstd")
    os.rename(partial, path)


def _audit_partition_family(frame: pd.DataFrame, source_family: str) -> pd.Series:
    if "event_family" in frame:
        detail = frame["event_family"].astype(str)
    elif "event_type" in frame:
        detail = frame["event_type"].astype(str)
    else:
        detail = pd.Series("event", index=frame.index, dtype="string")
    return pd.Series(
        [f"{source_family}-{value}" for value in detail],
        index=frame.index,
        dtype="string",
    )


def _write_partitioned_audit_dataset(
    root: Path,
    sources: Sequence[tuple[str, pd.DataFrame | Path]],
    *,
    crosswalk: pd.DataFrame,
    cell_block_size: int,
    schema_name: str,
    audit_kind: str,
) -> dict[str, int]:
    """Write heterogeneous audit sources with one unified Arrow schema.

    Sources are scanned and written one bounded frame at a time.  No global
    pandas concatenation or monolithic audit table is constructed.
    """

    import pyarrow as pa

    schemas: list[Any] = []
    for source_family, payload in sources:
        for frame in _iter_audit_frames(payload):
            schemas.append(_tag_audit_arrow(frame, source_family).schema)
    root.mkdir(parents=True, exist_ok=True)
    if not schemas:
        _write_arrow_partition_new(
            root / "empty.parquet",
            pa.table({"source_family": pa.array([], type=pa.string())}),
        )
        _write_json_new(
            root / "_DATASET.json",
            {
                "schema_name": schema_name,
                "format": "parquet-dataset",
                "rows": 0,
                "partitions": 1,
                "partition_order": ["family", "year", "cell_block"],
            },
        )
        return {"rows": 0, "partitions": 1}
    try:
        unified_schema = pa.unify_schemas(
            schemas, promote_options="permissive"
        ).remove_metadata()
    except pa.ArrowInvalid as exc:
        raise StageValidationError(
            f"Audit Parquet schemas cannot be unified: {exc}"
        ) from exc

    ordered = (
        crosswalk[["era01_cell_id"]]
        .drop_duplicates("era01_cell_id")
        .sort_values("era01_cell_id")
        .reset_index(drop=True)
    )
    block_lookup = {
        int(identifier): int(position // cell_block_size)
        for position, identifier in enumerate(ordered["era01_cell_id"])
    }
    rows = 0
    partitions = 0
    for source_index, (source_family, payload) in enumerate(sources):
        frame_index = 0
        for frame in _iter_audit_frames(payload):
            if "era01_cell_id" not in frame:
                raise StageValidationError(
                    f"Audit source {source_family} lacks era01_cell_id"
                )
            years = _event_partition_years(frame, audit_kind=audit_kind)
            blocks = frame["era01_cell_id"].map(block_lookup)
            if blocks.isna().any():
                raise StageValidationError(
                    f"Audit source {source_family} contains an unknown cell"
                )
            families = _audit_partition_family(frame, source_family)
            grouping = pd.DataFrame(
                {"family": families, "year": years, "block": blocks.astype(int)},
                index=frame.index,
            )
            for (family, year, block), indices in grouping.groupby(
                ["family", "year", "block"], sort=True, observed=True
            ).groups.items():
                part = frame.loc[list(indices)].reset_index(drop=True)
                table = _align_audit_arrow_table(
                    _tag_audit_arrow(part, source_family), unified_schema
                )
                output = (
                    root
                    / f"family-{_partition_token(family)}"
                    / f"year-{int(year):04d}"
                    / f"cell-block-{int(block):06d}"
                    / f"part-{source_index:03d}-{frame_index:06d}.parquet"
                )
                _write_arrow_partition_new(output, table)
                rows += len(part)
                partitions += 1
            frame_index += 1
    _write_json_new(
        root / "_DATASET.json",
        {
            "schema_name": schema_name,
            "format": "parquet-dataset",
            "rows": rows,
            "partitions": partitions,
            "partition_order": ["family", "year", "cell_block"],
            "schema": str(unified_schema),
        },
    )
    return {"rows": rows, "partitions": partitions}


def _parquet_dataset_row_count(path: Path) -> int:
    import pyarrow.parquet as pq

    files = [path] if path.is_file() else sorted(path.rglob("*.parquet"))
    return sum(
        int(pq.ParquetFile(file_path).metadata.num_rows)
        for file_path in files
        if not file_path.name.startswith(".")
    )


def _renumber_group_event_ids(
    events: pd.DataFrame,
    bridges: pd.DataFrame,
    counters: dict[str, int],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Make event identifiers unique after contiguous-year group processing."""

    if events.empty:
        if not bridges.empty:
            raise StageValidationError("Event bridges exist without complete events")
        return events, bridges
    mapping: dict[str, str] = {}
    rewritten = events.copy()
    for index, raw_event_id in rewritten["event_id"].items():
        event_id = str(raw_event_id)
        prefix, separator, _number = event_id.rpartition(":")
        if not separator:
            raise StageValidationError(f"Event ID lacks numeric suffix: {event_id}")
        counters[prefix] = counters.get(prefix, 0) + 1
        replacement = f"{prefix}:{counters[prefix]:04d}"
        mapping[event_id] = replacement
        rewritten.at[index, "event_id"] = replacement
    rewritten_bridges = bridges.copy()
    if not rewritten_bridges.empty:
        mapped = rewritten_bridges["event_id"].astype(str).map(mapping)
        if mapped.isna().any():
            raise StageValidationError("Event-window bridge lacks a complete-event ID")
        rewritten_bridges["event_id"] = mapped
    return rewritten, rewritten_bridges


def _add_hot_flash_window_metrics(
    long: pd.DataFrame,
    bridges: pd.DataFrame,
    classifications: pd.DataFrame,
    layers: Iterable[str],
) -> pd.DataFrame:
    output = long.copy()
    if not classifications.empty and classifications["event_id"].duplicated().any():
        raise StageValidationError("Hot-flash classifications duplicate event_id")
    flash_bridges = (
        bridges.loc[bridges["event_family"].eq("flash_drought")].copy()
        if not bridges.empty
        else pd.DataFrame()
    )
    joined = pd.DataFrame()
    if not flash_bridges.empty and not classifications.empty:
        joined = flash_bridges.merge(
            classifications,
            on=["era01_cell_id", "grid_id_v3", "event_id"],
            how="left",
            validate="many_to_one",
            suffixes=("", "_classification"),
        )
    keys = ["era01_cell_id", "year", "window"]
    for raw_layer in layers:
        layer = str(raw_layer)
        layer_prefix = f"gleam43a_{layer.lower()}"
        for variant in ("main", "strict"):
            valid_column = f"{layer_prefix}_fd_{variant}_any"
            if valid_column not in output:
                raise StageValidationError(
                    f"GLEAM long panel lacks hot-FD support field {valid_column}"
                )
            soil_valid = output[valid_column].notna()
            fd_present = output[valid_column].eq(1.0)
            relevant = pd.DataFrame()
            if not joined.empty:
                relevant = joined.loc[
                    joined["layer"].eq(layer)
                    & joined["fd_variant"].eq(variant)
                ].copy()

            valid_pentads_name = f"{layer_prefix}_fd_{variant}_hot_valid_pentads"
            span_pentads_name = f"{layer_prefix}_fd_{variant}_hot_span_pentads"
            coverage_name = f"{layer_prefix}_fd_{variant}_hot_coverage"
            output[valid_pentads_name] = np.where(
                soil_valid & ~fd_present, 0.0, np.nan
            )
            output[span_pentads_name] = np.where(
                soil_valid & ~fd_present, 0.0, np.nan
            )
            output[coverage_name] = np.nan
            if not relevant.empty:
                diagnostics = (
                    relevant.groupby(keys, observed=True)
                    .agg(
                        __hot_valid_pentads=(
                            "valid_hot_pentads",
                            lambda values: values.sum(min_count=1),
                        ),
                        __hot_span_pentads=(
                            "span_pentads",
                            lambda values: values.sum(min_count=1),
                        ),
                    )
                    .reset_index()
                )
                diagnostics["__hot_coverage"] = np.divide(
                    diagnostics["__hot_valid_pentads"],
                    diagnostics["__hot_span_pentads"],
                    out=np.full(len(diagnostics), np.nan, dtype=float),
                    where=diagnostics["__hot_span_pentads"].to_numpy() > 0,
                )
                output = output.merge(
                    diagnostics,
                    on=keys,
                    how="left",
                    validate="one_to_one",
                    sort=False,
                )
                observed_diagnostics = (
                    output["__hot_span_pentads"].notna()
                    & output[valid_column].notna()
                )
                output.loc[
                    observed_diagnostics, valid_pentads_name
                ] = output.loc[observed_diagnostics, "__hot_valid_pentads"]
                output.loc[
                    observed_diagnostics, span_pentads_name
                ] = output.loc[observed_diagnostics, "__hot_span_pentads"]
                output.loc[observed_diagnostics, coverage_name] = output.loc[
                    observed_diagnostics, "__hot_coverage"
                ]
                output = output.drop(
                    columns=[
                        "__hot_valid_pentads",
                        "__hot_span_pentads",
                        "__hot_coverage",
                    ]
                )

            for classification_column, suffix in (
                ("hot_fd_main_any", "hot_main"),
                ("hot_fd_strict_majority", "hot_strict_majority"),
            ):
                count_name = f"{layer_prefix}_fd_{variant}_{suffix}_count"
                any_name = f"{layer_prefix}_fd_{variant}_{suffix}_any"
                output[count_name] = np.where(
                    soil_valid & ~fd_present, 0.0, np.nan
                )
                output[any_name] = np.where(
                    soil_valid & ~fd_present, 0.0, np.nan
                )
                if relevant.empty:
                    continue
                classified = (
                    relevant.groupby(keys, observed=True)[classification_column]
                    .agg(
                        __classified_count=lambda values: int(
                            values.eq(True).sum()  # noqa: E712
                        ),
                        __classification_complete=lambda values: bool(
                            values.notna().all()
                        ),
                    )
                    .reset_index()
                )
                output = output.merge(
                    classified,
                    on=keys,
                    how="left",
                    validate="one_to_one",
                    sort=False,
                )
                observed = (
                    output["__classification_complete"].eq(True)  # noqa: E712
                    & output[valid_column].notna()
                )
                output.loc[observed, count_name] = output.loc[
                    observed, "__classified_count"
                ]
                output.loc[observed, any_name] = output.loc[
                    observed, "__classified_count"
                ].gt(0).astype(float)
                output = output.drop(
                    columns=["__classified_count", "__classification_complete"]
                )
    return output


def _deprecated_handle_aggregate_monolithic_unreachable(
    request: StageRequest,
) -> StageOutcome:
    """Preserved pre-streaming implementation; never registered as a handler."""
    from .aggregate import aggregate_temperature_windows
    from .soil import aggregate_gleam_windows

    panel = pd.read_parquet(
        _stage_file(request.context, "phenology", "phenology_panel.parquet")
    )
    minimum_coverage = float(
        request.config.data["quality"]["minimum_window_coverage"]
    )
    event_years = _event_context_years(request.config)
    cell_block_size = int(
        request.config.data.get("runtime", {}).get("gleam_cell_block_size", 128)
    )
    if cell_block_size <= 0:
        raise ValueError("runtime.gleam_cell_block_size must be positive")
    crosswalk = pd.read_parquet(
        _stage_file(request.context, "grid", "crosswalk.parquet")
    )
    temperature_long, temperature_events, temperature_bridges = (
        aggregate_temperature_windows(
            panel,
            _stage_file(request.context, "era_daily", "daily_cache"),
            _stage_file(request.context, "era_baseline", "thresholds"),
            years=request.scope.years,
            event_years=event_years,
            windows=request.config.windows,
            minimum_coverage=minimum_coverage,
            heatwave_min_days=int(
                request.config.data["temperature"]["heatwave_min_days"]
            ),
        )
    )
    combined = temperature_long
    component_artifacts: dict[str, Path] = {}
    audit_events: list[tuple[str, pd.DataFrame | Path]] = []
    audit_bridges: list[tuple[str, pd.DataFrame | Path]] = []
    if not temperature_events.empty:
        audit_events.append(("era5u8", temperature_events))
    if not temperature_bridges.empty:
        audit_bridges.append(("era5u8", temperature_bridges))

    soil_events: dict[str, pd.DataFrame] = {}
    soil_bridges: dict[str, pd.DataFrame] = {}
    for raw_layer in request.config.data["gleam"]["layers"]:
        layer = str(raw_layer)
        (
            daily_dates,
            daily_values,
            daily_metrics,
            pentad_values,
            pentad_metrics,
        ) = _load_gleam_target_inputs(request, layer)
        gleam_long, gleam_events, gleam_bridges = aggregate_gleam_windows(
            panel,
            layer=layer,
            years=request.scope.years,
            event_years=event_years,
            windows=request.config.windows,
            daily_dates=daily_dates,
            daily_values=daily_values,
            daily_metrics=daily_metrics,
            pentad_values=pentad_values,
            pentad_metrics=pentad_metrics,
            minimum_coverage=minimum_coverage,
        )
        combined = _merge_window_metrics(
            combined, gleam_long, source=f"GLEAM {layer}"
        )
        component_path = request.work_dir / f"gleam43a_{layer.lower()}_window_long.parquet"
        gleam_long.to_parquet(component_path, index=False)
        component_artifacts[f"gleam_{layer.lower()}_long"] = component_path
        if not gleam_events.empty:
            soil_events[layer] = gleam_events
        if not gleam_bridges.empty:
            soil_bridges[layer] = gleam_bridges

    manual = pd.read_parquet(
        _stage_file(request.context, "spei", "chm_spei_manual.parquet")
    )
    dynamic = pd.read_parquet(
        _stage_file(request.context, "spei", "chm_spei_dynamic_ext.parquet")
    )
    spei_event_long = pd.read_parquet(
        _stage_file(request.context, "spei", "chm_spei_event_window_long.parquet")
    )
    combined = _merge_window_metrics(combined, manual, source="CHM SPEI manual")
    combined = _merge_window_metrics(combined, dynamic, source="CHM SPEI dynamic")
    combined = _merge_window_metrics(
        combined, spei_event_long, source="CHM SPEI events"
    )
    spei_events = pd.read_parquet(
        _stage_file(request.context, "spei", "chm_spei_events.parquet")
    )
    spei_bridges = pd.read_parquet(
        _stage_file(request.context, "spei", "chm_spei_event_window_bridge.parquet")
    )
    if not spei_events.empty:
        audit_events.append(("chm_spei", spei_events))
    if not spei_bridges.empty:
        audit_bridges.append(("chm_spei", spei_bridges))
    compound_long = pd.read_parquet(
        _stage_file(request.context, "events", "compound_window_long.parquet")
    )
    combined = _merge_window_metrics(combined, compound_long, source="compound events")

    hot_flash = pd.read_parquet(
        _stage_file(
            request.context,
            "events",
            "hot_flash_drought_classification.parquet",
        )
    )
    all_soil_bridges = (
        pd.concat(soil_bridges, ignore_index=True, sort=False)
        if soil_bridges
        else pd.DataFrame()
    )
    combined = _add_hot_flash_window_metrics(
        combined,
        all_soil_bridges,
        hot_flash,
        request.config.data["gleam"]["layers"],
    )
    if combined.duplicated(["era01_cell_id", "year", "window"]).any():
        raise StageValidationError("Canonical aggregate contains duplicate long keys")

    if soil_events:
        current = pd.concat(soil_events, ignore_index=True, sort=False)
        if not hot_flash.empty:
            current = current.merge(
                hot_flash.drop(columns=["layer"], errors="ignore"),
                on=["era01_cell_id", "grid_id_v3", "event_id"],
                how="left",
                validate="one_to_one",
            )
        audit_events.append(_tag_audit(current, "gleam43a"))
    if not all_soil_bridges.empty:
        audit_bridges.append(_tag_audit(all_soil_bridges, "gleam43a"))
    compound_events = pd.read_parquet(
        _stage_file(request.context, "events", "compound_events.parquet")
    )
    compound_bridges = pd.read_parquet(
        _stage_file(request.context, "events", "compound_event_window_bridge.parquet")
    )
    if not compound_events.empty:
        audit_events.append(_tag_audit(compound_events, "compound"))
    if not compound_bridges.empty:
        audit_bridges.append(_tag_audit(compound_bridges, "compound"))

    event_audit = (
        pd.concat(audit_events, ignore_index=True, sort=False)
        if audit_events
        else pd.DataFrame({"source_family": pd.Series(dtype="string")})
    )
    bridge_audit = (
        pd.concat(audit_bridges, ignore_index=True, sort=False)
        if audit_bridges
        else pd.DataFrame({"source_family": pd.Series(dtype="string")})
    )
    long_path = request.work_dir / "climate_window_long.parquet"
    temperature_path = request.work_dir / "temperature_window_long.parquet"
    event_path = request.work_dir / "event_audit.parquet"
    bridge_path = request.work_dir / "event_window_bridge.parquet"
    combined.to_parquet(long_path, index=False)
    temperature_long.to_parquet(temperature_path, index=False)
    event_audit.to_parquet(event_path, index=False)
    bridge_audit.to_parquet(bridge_path, index=False)
    return StageOutcome(
        artifacts={
            "long": long_path,
            "temperature_long": temperature_path,
            "event_audit": event_path,
            "event_window_bridge": bridge_path,
            **component_artifacts,
        },
        row_counts={
            "long_rows": len(combined),
            "temperature_events": len(temperature_events),
            "spei_events": len(spei_events),
            "gleam_events": sum(len(frame) for frame in soil_events),
            "compound_events": len(compound_events),
            "event_audit_rows": len(event_audit),
            "event_bridge_rows": len(bridge_audit),
        },
        extra={
            "families": ["era5u8", "chm_spei", "gleam43a", "compound"],
            "minimum_window_coverage": minimum_coverage,
        },
    )


def _read_parquet_cell_block(
    path: str | Path,
    cell_ids: np.ndarray,
    *,
    expected_rows: int | None = None,
    require_all_cells: bool = False,
) -> pd.DataFrame:
    """Read one selected-cell range through Arrow predicate pushdown."""

    import pyarrow.dataset as ds

    source = Path(path)
    dataset = ds.dataset(str(source), format="parquet")
    if "era01_cell_id" not in dataset.schema.names:
        if dataset.count_rows() == 0 and expected_rows in (None, 0):
            return dataset.to_table().to_pandas()
        raise StageValidationError(f"Parquet source lacks era01_cell_id: {source}")
    expected_ids = np.asarray(cell_ids, dtype=np.int64)
    if expected_ids.ndim != 1 or expected_ids.size == 0:
        raise ValueError("cell_ids must be a non-empty one-dimensional array")
    expression = (ds.field("era01_cell_id") >= int(expected_ids[0])) & (
        ds.field("era01_cell_id") <= int(expected_ids[-1])
    )
    frame = dataset.to_table(filter=expression).to_pandas()
    if expected_rows is not None and len(frame) != int(expected_rows):
        raise StageValidationError(
            f"{source} block has {len(frame):,} rows; expected {expected_rows:,}"
        )
    if not frame.empty:
        observed = set(
            pd.to_numeric(frame["era01_cell_id"], errors="raise")
            .astype(np.int64)
            .unique()
            .tolist()
        )
        allowed = set(expected_ids.tolist())
        if not observed.issubset(allowed):
            raise StageValidationError(f"{source} predicate returned cells outside the block")
        if require_all_cells and observed != allowed:
            raise StageValidationError(f"{source} does not cover every cell in the block")
    elif require_all_cells:
        raise StageValidationError(f"{source} has no rows for a required cell block")
    return frame


def _aggregate_partition_valid(
    contract_path: Path,
    *,
    work_dir: Path,
    cell_start: int,
    cell_stop: int,
    cell_id_sha256: str,
) -> tuple[bool, dict[str, Any]]:
    """Validate every reusable block file by Parquet footer and SHA-256."""

    from .spei import parquet_partition_contract

    try:
        payload = json.loads(contract_path.read_text(encoding="utf-8"))
        if (
            int(payload["cell_start"]) != int(cell_start)
            or int(payload["cell_stop"]) != int(cell_stop)
            or str(payload["cell_id_sha256"]) != cell_id_sha256
        ):
            return False, {}
        files = payload["files"]
        if not isinstance(files, dict) or not files:
            return False, {}
        for record in files.values():
            linked = work_dir / str(record["path"])
            valid, rows = parquet_partition_contract(
                linked,
                expected_rows=int(record["rows"]),
                required_columns=tuple(record.get("required_columns", ())),
            )
            if not valid or rows != int(record["rows"]):
                return False, {}
            if sha256_file(linked) != str(record["sha256"]):
                return False, {}
    except (FileNotFoundError, KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False, {}
    return True, payload


def _handle_aggregate(request: StageRequest) -> StageOutcome:
    """Build canonical window rows in resumable, hash-checked spatial blocks."""

    from .aggregate import aggregate_temperature_windows
    from .soil import aggregate_gleam_windows
    from .spei import combine_parquet_partitions_new, write_parquet_partition_new

    phenology_source = _stage_file(
        request.context, "phenology", "phenology_panel.parquet"
    )
    crosswalk = pd.read_parquet(
        _stage_file(request.context, "grid", "crosswalk.parquet")
    ).sort_values("era01_cell_id").reset_index(drop=True)
    minimum_coverage = float(
        request.config.data["quality"]["minimum_window_coverage"]
    )
    event_years = _event_context_years(request.config)
    runtime = request.config.data.get("runtime", {})
    cell_block_size = int(
        runtime.get(
            "aggregate_cell_block_size",
            runtime.get("gleam_cell_block_size", 128),
        )
    )
    if cell_block_size <= 0:
        raise ValueError("runtime.aggregate_cell_block_size must be positive")
    row_group_size = int(runtime.get("parquet_row_group_size", 262_144))
    layers = tuple(str(value) for value in request.config.data["gleam"]["layers"])
    expected_rows_per_cell = len(request.scope.years) * len(request.config.windows)
    partition_root = request.work_dir / "partitions"
    contract_root = partition_root / "contracts"
    long_families = (
        "canonical",
        "temperature",
        *(f"gleam_{layer.lower()}" for layer in layers),
    )
    audit_families = ("era5u8", "chm_spei", "gleam43a", "compound")
    all_partition_names = (
        *long_families,
        *(f"event_{family}" for family in audit_families),
        *(f"bridge_{family}" for family in audit_families),
    )
    partition_paths: dict[str, list[Path]] = {
        name: [] for name in all_partition_names
    }
    totals = {
        "temperature_events": 0,
        "spei_events": 0,
        "gleam_events": 0,
        "compound_events": 0,
        "event_audit_rows": 0,
        "event_bridge_rows": 0,
    }
    block_contracts: list[dict[str, Any]] = []

    spei_sources = {
        "manual": _stage_file(request.context, "spei", "chm_spei_manual.parquet"),
        "dynamic": _stage_file(
            request.context, "spei", "chm_spei_dynamic_ext.parquet"
        ),
        "event_long": _stage_file(
            request.context, "spei", "chm_spei_event_window_long.parquet"
        ),
        "events": _stage_file(request.context, "spei", "chm_spei_events.parquet"),
        "bridges": _stage_file(
            request.context, "spei", "chm_spei_event_window_bridge.parquet"
        ),
    }
    compound_sources = {
        "long": _stage_file(request.context, "events", "compound_window_long.parquet"),
        "events": _stage_file(request.context, "events", "compound_events.parquet"),
        "bridges": _stage_file(
            request.context, "events", "compound_event_window_bridge.parquet"
        ),
        "hot_flash": _stage_file(
            request.context, "events", "hot_flash_drought_classification.parquet"
        ),
    }

    for cell_start in range(0, len(crosswalk), cell_block_size):
        cell_stop = min(cell_start + cell_block_size, len(crosswalk))
        block_cells = crosswalk.iloc[cell_start:cell_stop].copy()
        cell_ids = block_cells["era01_cell_id"].to_numpy(dtype=np.int64)
        cell_id_sha256 = __import__("hashlib").sha256(
            cell_ids.astype("<i8", copy=False).tobytes()
        ).hexdigest()
        label = f"part-{cell_start:06d}-{cell_stop:06d}"
        paths = {
            name: partition_root / name / f"{label}.parquet"
            for name in all_partition_names
        }
        contract_path = contract_root / f"{label}.json"
        valid = False
        payload: dict[str, Any] = {}
        if request.pipeline.resume and contract_path.is_file():
            valid, payload = _aggregate_partition_valid(
                contract_path,
                work_dir=request.work_dir,
                cell_start=cell_start,
                cell_stop=cell_stop,
                cell_id_sha256=cell_id_sha256,
            )
        if valid:
            for name, path in paths.items():
                partition_paths[name].append(path)
            for name in totals:
                totals[name] += int(payload["row_counts"].get(name, 0))
            block_contracts.append(payload)
            continue
        if request.pipeline.resume:
            for path in (*paths.values(), contract_path):
                if path.exists():
                    _archive_incomplete(path)

        expected_panel_rows = len(cell_ids) * len(request.scope.years)
        block_panel = _read_parquet_cell_block(
            phenology_source,
            cell_ids,
            expected_rows=expected_panel_rows,
            require_all_cells=True,
        )
        expected_long_rows = len(cell_ids) * expected_rows_per_cell
        temperature_long, temperature_events, temperature_bridges = (
            aggregate_temperature_windows(
                block_panel,
                _stage_file(request.context, "era_daily", "daily_cache"),
                _stage_file(request.context, "era_baseline", "thresholds"),
                years=request.scope.years,
                event_years=event_years,
                windows=request.config.windows,
                minimum_coverage=minimum_coverage,
                heatwave_min_days=int(
                    request.config.data["temperature"]["heatwave_min_days"]
                ),
                cell_block_size=cell_block_size,
                source_cell_slice=slice(cell_start, cell_stop),
            )
        )
        combined = temperature_long

        soil_events: list[pd.DataFrame] = []
        soil_bridges: list[pd.DataFrame] = []
        gleam_frames: dict[str, pd.DataFrame] = {}
        for layer in layers:
            (
                daily_dates,
                daily_values,
                daily_metrics,
                pentad_values,
                pentad_metrics,
            ) = _load_gleam_target_inputs(
                request,
                layer,
                cell_slice=slice(cell_start, cell_stop),
            )
            gleam_long, gleam_events, gleam_bridges = aggregate_gleam_windows(
                block_panel,
                layer=layer,
                years=request.scope.years,
                event_years=event_years,
                windows=request.config.windows,
                daily_dates=daily_dates,
                daily_values=daily_values,
                daily_metrics=daily_metrics,
                pentad_values=pentad_values,
                pentad_metrics=pentad_metrics,
                minimum_coverage=minimum_coverage,
                cell_block_size=cell_block_size,
            )
            combined = _merge_window_metrics(
                combined, gleam_long, source=f"GLEAM {layer}"
            )
            gleam_frames[f"gleam_{layer.lower()}"] = gleam_long
            if not gleam_events.empty:
                soil_events.append(gleam_events)
            if not gleam_bridges.empty:
                soil_bridges.append(gleam_bridges)

        manual = _read_parquet_cell_block(
            spei_sources["manual"],
            cell_ids,
            expected_rows=expected_long_rows,
            require_all_cells=True,
        )
        dynamic = _read_parquet_cell_block(
            spei_sources["dynamic"],
            cell_ids,
            expected_rows=expected_long_rows,
            require_all_cells=True,
        )
        spei_event_long = _read_parquet_cell_block(
            spei_sources["event_long"],
            cell_ids,
            expected_rows=expected_long_rows,
            require_all_cells=True,
        )
        combined = _merge_window_metrics(combined, manual, source="CHM SPEI manual")
        combined = _merge_window_metrics(combined, dynamic, source="CHM SPEI dynamic")
        combined = _merge_window_metrics(
            combined, spei_event_long, source="CHM SPEI events"
        )
        spei_events = _read_parquet_cell_block(spei_sources["events"], cell_ids)
        spei_bridges = _read_parquet_cell_block(spei_sources["bridges"], cell_ids)

        compound_long = _read_parquet_cell_block(
            compound_sources["long"],
            cell_ids,
            expected_rows=expected_long_rows,
            require_all_cells=True,
        )
        combined = _merge_window_metrics(
            combined, compound_long, source="compound events"
        )
        hot_flash = _read_parquet_cell_block(
            compound_sources["hot_flash"], cell_ids
        )
        all_soil_bridges = (
            pd.concat(soil_bridges, ignore_index=True, sort=False)
            if soil_bridges
            else pd.DataFrame()
        )
        combined = _add_hot_flash_window_metrics(
            combined, all_soil_bridges, hot_flash, layers
        )
        if len(combined) != expected_long_rows or combined.duplicated(
            ["era01_cell_id", "year", "window"]
        ).any():
            raise StageValidationError(
                "Canonical aggregate block changed or duplicated long-key support"
            )

        gleam_event_frame = (
            pd.concat(soil_events, ignore_index=True, sort=False)
            if soil_events
            else pd.DataFrame()
        )
        if not gleam_event_frame.empty and not hot_flash.empty:
            gleam_event_frame = gleam_event_frame.merge(
                hot_flash.drop(columns=["layer"], errors="ignore"),
                on=["era01_cell_id", "grid_id_v3", "event_id"],
                how="left",
                validate="one_to_one",
            )
        compound_events = _read_parquet_cell_block(
            compound_sources["events"], cell_ids
        )
        compound_bridges = _read_parquet_cell_block(
            compound_sources["bridges"], cell_ids
        )
        event_frames = {
            "era5u8": temperature_events,
            "chm_spei": spei_events,
            "gleam43a": gleam_event_frame,
            "compound": compound_events,
        }
        bridge_frames = {
            "era5u8": temperature_bridges,
            "chm_spei": spei_bridges,
            "gleam43a": all_soil_bridges,
            "compound": compound_bridges,
        }

        frames = {
            "canonical": combined,
            "temperature": temperature_long,
            **gleam_frames,
            **{f"event_{name}": frame for name, frame in event_frames.items()},
            **{f"bridge_{name}": frame for name, frame in bridge_frames.items()},
        }
        file_records: dict[str, dict[str, Any]] = {}
        for name, frame in frames.items():
            path = paths[name]
            write_parquet_partition_new(
                path,
                frame,
                row_group_size=min(row_group_size, max(len(frame), 1)),
            )
            required_columns = (
                ["era01_cell_id", "year", "window"]
                if name in long_families
                else ([] if frame.empty else ["era01_cell_id"])
            )
            file_records[name] = {
                "path": path.relative_to(request.work_dir).as_posix(),
                "rows": len(frame),
                "sha256": sha256_file(path),
                "required_columns": required_columns,
            }
            partition_paths[name].append(path)

        row_counts = {
            "temperature_events": len(temperature_events),
            "spei_events": len(spei_events),
            "gleam_events": len(gleam_event_frame),
            "compound_events": len(compound_events),
            "event_audit_rows": sum(len(frame) for frame in event_frames.values()),
            "event_bridge_rows": sum(len(frame) for frame in bridge_frames.values()),
        }
        payload = {
            "contract_version": 1,
            "cell_start": cell_start,
            "cell_stop": cell_stop,
            "cell_count": len(cell_ids),
            "cell_id_sha256": cell_id_sha256,
            "expected_long_rows": expected_long_rows,
            "files": file_records,
            "row_counts": row_counts,
        }
        _write_json_new(contract_path, payload)
        for name in totals:
            totals[name] += int(row_counts[name])
        block_contracts.append(payload)

    final_long_paths = {
        "canonical": request.work_dir / "climate_window_long.parquet",
        "temperature": request.work_dir / "temperature_window_long.parquet",
        **{
            f"gleam_{layer.lower()}": request.work_dir
            / f"gleam43a_{layer.lower()}_window_long.parquet"
            for layer in layers
        },
    }
    for name, path in final_long_paths.items():
        if path.exists():
            _archive_incomplete(path)
        _target, rows = combine_parquet_partitions_new(
            partition_paths[name], path, row_group_size=row_group_size
        )
        expected = len(crosswalk) * expected_rows_per_cell
        if rows != expected:
            raise StageValidationError(
                f"Aggregate {name} partitions total {rows:,} rows; expected {expected:,}"
            )

    event_path = request.work_dir / "event_audit.parquet"
    bridge_path = request.work_dir / "event_window_bridge.parquet"
    for path in (event_path, bridge_path):
        if path.exists():
            _archive_incomplete(path)
    event_report = _write_partitioned_audit_dataset(
        event_path,
        [
            (family, partition_root / f"event_{family}")
            for family in audit_families
        ],
        crosswalk=crosswalk,
        cell_block_size=cell_block_size,
        schema_name="complete-event-audit",
        audit_kind="event",
    )
    bridge_report = _write_partitioned_audit_dataset(
        bridge_path,
        [
            (family, partition_root / f"bridge_{family}")
            for family in audit_families
        ],
        crosswalk=crosswalk,
        cell_block_size=cell_block_size,
        schema_name="event-window-bridge",
        audit_kind="bridge",
    )
    if event_report["rows"] != totals["event_audit_rows"]:
        raise StageValidationError("Event audit partition count changed on publication")
    if bridge_report["rows"] != totals["event_bridge_rows"]:
        raise StageValidationError("Event bridge partition count changed on publication")

    aggregate_contract_path = request.work_dir / "aggregate_partition_manifest.json"
    if aggregate_contract_path.exists():
        _archive_incomplete(aggregate_contract_path)
    _write_json_new(
        aggregate_contract_path,
        {
            "contract_version": 1,
            "cell_block_size": cell_block_size,
            "blocks": len(block_contracts),
            "selected_cells": len(crosswalk),
            "long_rows_per_full_block_max": cell_block_size * expected_rows_per_cell,
            "partition_order": "ascending selected-cell position",
            "partition_contracts": [
                (contract_root / f"part-{item['cell_start']:06d}-{item['cell_stop']:06d}.json")
                .relative_to(request.work_dir)
                .as_posix()
                for item in block_contracts
            ],
            "final_files": {
                **{
                    name: {
                        "path": path.relative_to(request.work_dir).as_posix(),
                        "sha256": sha256_file(path),
                    }
                    for name, path in final_long_paths.items()
                },
                "event_audit": {
                    "path": event_path.relative_to(request.work_dir).as_posix(),
                    "sha256": sha256_path(event_path),
                },
                "event_bridge": {
                    "path": bridge_path.relative_to(request.work_dir).as_posix(),
                    "sha256": sha256_path(bridge_path),
                },
            },
            "peak_memory_contract": {
                "spatial_cells_per_block_max": cell_block_size,
                "long_rows_per_block_max": cell_block_size * expected_rows_per_cell,
                "full_canonical_long_dataframe_forbidden": True,
                "full_wide_dataframe_forbidden": True,
            },
        },
    )
    component_artifacts = {
        "temperature_long": final_long_paths["temperature"],
        **{
            f"gleam_{layer.lower()}_long": final_long_paths[f"gleam_{layer.lower()}"]
            for layer in layers
        },
    }
    return StageOutcome(
        artifacts={
            "long": final_long_paths["canonical"],
            "canonical_partitions": partition_root / "canonical",
            "partition_manifest": aggregate_contract_path,
            "event_audit": event_path,
            "event_window_bridge": bridge_path,
            **component_artifacts,
        },
        row_counts={
            "long_rows": len(crosswalk) * expected_rows_per_cell,
            **totals,
        },
        extra={
            "families": ["era5u8", "chm_spei", "gleam43a", "compound"],
            "minimum_window_coverage": minimum_coverage,
            "cell_block_size": cell_block_size,
            "partition_blocks": len(block_contracts),
            "peak_long_rows_per_block": cell_block_size * expected_rows_per_cell,
        },
    )


def _handle_export(request: StageRequest) -> StageOutcome:
    from .export import (
        export_panel_bundle_streaming,
        manifest_input_records_from_inventory,
    )

    crosswalk = pd.read_parquet(
        _stage_file(request.context, "grid", "crosswalk.parquet")
    ).sort_values("era01_cell_id").reset_index(drop=True)
    selected_cells = len(crosswalk)
    expected_long = selected_cells * len(request.scope.years) * len(
        request.config.windows
    )
    expected_wide = selected_cells * len(request.scope.years)
    bundle_root = request.work_dir / "bundle"
    inventory_parquet = _stage_file(
        request.context,
        "assets",
        "audit/inventory/source_inventory.parquet",
    )
    input_records = manifest_input_records_from_inventory(
        inventory_parquet,
        require_full_hash=not request.scope.is_pilot,
    )
    spei_2w_audit_path = _stage_file(
        request.context, "spei", "spei_2w_audit.json"
    )
    spei_2w_audit = json.loads(
        spei_2w_audit_path.read_text(encoding="utf-8")
    )
    spei_2w_numeric_executed = bool(
        spei_2w_audit.get("numeric_executed", False)
    )
    full_scope = request.context.completion_scope_status == "FULL_SCOPE"
    required_positive_2w = (
        "release_count",
        "cell_count",
        "canonical_field_count",
    )
    if full_scope:
        if (
            spei_2w_audit.get("status") != "EXECUTED"
            or not spei_2w_numeric_executed
            or any(
                int(spei_2w_audit.get(name, 0)) <= 0
                for name in required_positive_2w
            )
        ):
            raise StageValidationError(
                "Full-scope export requires executed SPEI-2W stage evidence"
            )
    elif (
        spei_2w_audit.get("status") != SPEI_2W_PENDING_STATUS
        or spei_2w_numeric_executed
        or any(
            int(spei_2w_audit.get(name, -1)) != 0
            for name in (
                "release_count",
                "cell_count",
                "canonical_field_count",
                "event_rows",
                "bridge_rows",
            )
        )
    ):
        raise StageValidationError(
            "Partial-scope export requires skipped zero-output SPEI-2W evidence"
        )
    frozen_2w = request.config.data["spei"]
    expected_2w_audit = {
        "endpoint_decision_status": frozen_2w[
            "two_week_endpoint_decision_status"
        ],
        "config_semantics": frozen_2w["two_week_timestamp_semantics"],
        "accumulation_timestamp_position": frozen_2w[
            "two_week_accumulation_timestamp_position"
        ],
        "state_timestamp_position": frozen_2w[
            "two_week_state_timestamp_position"
        ],
        "accumulation_days": int(frozen_2w["two_week_accumulation_days"]),
        "state_days": int(frozen_2w["two_week_state_days"]),
        "primary_threshold": float(frozen_2w["two_week_primary_threshold"]),
        "primary_min_units": int(frozen_2w["two_week_primary_min_units"]),
        "strict_threshold": float(frozen_2w["two_week_strict_threshold"]),
        "strict_min_units": int(frozen_2w["two_week_strict_min_units"]),
    }
    mismatched_2w = [
        name
        for name, expected in expected_2w_audit.items()
        if spei_2w_audit.get(name) != expected
    ]
    if mismatched_2w:
        raise StageValidationError(
            f"SPEI-2W audit differs from frozen config: {mismatched_2w}"
        )
    spei_event_source = _stage_file(
        request.context, "spei", "chm_spei_events.parquet"
    )
    spei_bridge_source = _stage_file(
        request.context, "spei", "chm_spei_event_window_bridge.parquet"
    )
    observed_2w_events, observed_2w_bridges, _event_max, _bridge_max = (
        _validate_spei_2w_event_row_counts(
            spei_2w_audit,
            spei_event_source,
            spei_bridge_source,
        )
    )
    spei_2w_output_included = bool(
        request.config.data["scope"]["spei_2w_output"]
        and spei_2w_numeric_executed
    )
    if full_scope != spei_2w_output_included:
        raise StageValidationError(
            "SPEI-2W output inclusion differs from the configured scope"
        )
    audit_artifacts: dict[str, Path] = {
        "source_inventory_json": _stage_file(
            request.context,
            "assets",
            "audit/inventory/source_inventory.json",
        ),
        "source_inventory_parquet": inventory_parquet,
        "grid_crosswalk": _stage_file(
            request.context, "grid", "crosswalk.parquet"
        ),
        "grid_selection": _stage_file(
            request.context, "grid", "selection.json"
        ),
        "phenology_panel": _stage_file(
            request.context, "phenology", "phenology_panel.parquet"
        ),
        "era_daily_cache": _stage_file(
            request.context, "era_daily", "daily_cache"
        ),
        "era_thresholds": _stage_file(
            request.context, "era_baseline", "thresholds"
        ),
        "spei_month_cache": _stage_file(request.context, "spei", "cache"),
        "spei_manual": _stage_file(
            request.context, "spei", "chm_spei_manual.parquet"
        ),
        "spei_dynamic_ext": _stage_file(
            request.context, "spei", "chm_spei_dynamic_ext.parquet"
        ),
        "spei_events": _stage_file(
            request.context, "spei", "chm_spei_events.parquet"
        ),
        "spei_event_window": _stage_file(
            request.context, "spei", "chm_spei_event_window_long.parquet"
        ),
        "spei_event_bridge": _stage_file(
            request.context, "spei", "chm_spei_event_window_bridge.parquet"
        ),
        "spei_2w_audit": _stage_file(
            request.context, "spei", "spei_2w_audit.json"
        ),
        "gleam_daily_cache": _stage_file(
            request.context, "gleam_daily", "daily_cache"
        ),
        "gleam_metrics": _stage_file(
            request.context, "gleam_baseline", "metrics"
        ),
        "gleam_baseline_metadata": _stage_file(
            request.context, "gleam_baseline", "gleam_baseline_metadata.json"
        ),
        "compound_window": _stage_file(
            request.context, "events", "compound_window_long.parquet"
        ),
        "compound_events": _stage_file(
            request.context, "events", "compound_events.parquet"
        ),
        "compound_event_bridge": _stage_file(
            request.context, "events", "compound_event_window_bridge.parquet"
        ),
        "hot_flash_classification": _stage_file(
            request.context,
            "events",
            "hot_flash_drought_classification.parquet",
        ),
        "event_audit": _stage_file(
            request.context, "aggregate", "event_audit.parquet"
        ),
        "event_window_bridge": _stage_file(
            request.context, "aggregate", "event_window_bridge.parquet"
        ),
        "aggregate_canonical_partitions": _stage_file(
            request.context, "aggregate", "partitions/canonical"
        ),
        "aggregate_partition_manifest": _stage_file(
            request.context, "aggregate", "aggregate_partition_manifest.json"
        ),
    }
    legacy_sidecar = _stage_file(
        request.context, "spei", "legacy_v3_exact.parquet"
    )
    attempt_logs = request.context.audit_dir / "attempts"
    if attempt_logs.is_dir():
        audit_artifacts["stage_attempt_logs"] = attempt_logs
    if legacy_sidecar.is_file():
        audit_artifacts["spei_legacy_v3_exact"] = legacy_sidecar
    aggregate_stage = request.context.stages_dir / "aggregate"
    for component in sorted(aggregate_stage.glob("*_window_long.parquet")):
        audit_artifacts[f"aggregate_{component.stem}"] = component
    audit_record_paths = {
        name: path.relative_to(request.context.run_dir).as_posix()
        for name, path in audit_artifacts.items()
    }
    paths, export_report = export_panel_bundle_streaming(
        _stage_file(request.context, "aggregate", "partitions/canonical"),
        crosswalk,
        bundle_root,
        config_path=request.config.path,
        input_records=input_records,
        audit_artifacts=audit_artifacts,
        audit_record_paths=audit_record_paths,
        years=request.scope.years,
        windows=request.config.windows,
        expected_long_rows=expected_long,
        expected_wide_rows=expected_wide,
        version_id=request.config.version_id,
        gleam_layer_roles=request.config.data["gleam"]["layers"],
        sources={
            name: {
                key: record[key]
                for key in ("family", "path", "sha256", "hash_algorithm")
                if key in record
            }
            for name, record in input_records.items()
        },
        transformations={
            "temperature": "ERA5 hourly to UTC+8 daily and six clipped phenology windows",
            "spei": (
                "CHM native monthly SPEI plus confirmed 2W trailing-14-day "
                "releases mapped to forward 7-day event states"
                if full_scope
                else "CHM native monthly SPEI; partial-scope 2W numerics excluded"
            ),
            "soil_moisture": "GLEAM 4.3a daily and fixed calendar-pentad metrics",
            "events": "complete-sequence detection with event-window audit bridges",
        },
        quality={
            "mode": request.scope.mode,
            "runtime_environment_sha256": request.context.environment_sha256,
            "runtime_environment": request.context.environment_state,
            "minimum_window_coverage": float(
                request.config.data["quality"]["minimum_window_coverage"]
            ),
            "selected_cells": selected_cells,
            "expected_long_rows": expected_long,
            "expected_wide_rows": expected_wide,
        },
        exclusions=(
            "precipitation dry days, CDD, and VPD",
            "fixed hot-without-rain events",
            "yield/SR-dependent splines, response surfaces, and predictions",
        ),
        compression=str(request.config.data["output"].get("compression", "zstd")),
        row_group_size=int(
            request.config.data.get("runtime", {}).get(
                "parquet_row_group_size", 262_144
            )
        ),
        netcdf_complevel=int(
            request.config.data["output"].get("netcdf_complevel", 4)
        ),
        published_output_directory=Path("stages") / "export" / "bundle",
        scope_id=request.context.scope_profile,
        scope_status=request.context.completion_scope_status,
        spei_2w_numeric_executed=spei_2w_numeric_executed,
        spei_2w_output_included=spei_2w_output_included,
        spei_2w_evidence=spei_2w_audit,
    )
    artifacts = {
        name: getattr(paths, name) for name in paths.__dataclass_fields__
    }
    artifacts["wide_partitions"] = Path(export_report["wide_partitions"])
    artifacts["output_contract"] = Path(export_report["output_contract"])
    return StageOutcome(
        artifacts=artifacts,
        row_counts={
            "long_rows": int(export_report["long_rows"]),
            "wide_rows": int(export_report["wide_rows"]),
            "selected_cells": selected_cells,
            "bundle_files": len(artifacts),
        },
        extra={
            "bundle_directory": "bundle",
            "streaming_contract": export_report["streaming_contract"],
            "spei_2w_numeric_executed": spei_2w_numeric_executed,
            "spei_2w_output_included": spei_2w_output_included,
        },
    )


def _run_utc_validation(
    request: StageRequest,
    crosswalk: pd.DataFrame,
) -> tuple[dict[str, Any], dict[str, Path], list[str]]:
    """Run legacy UTC reproduction and report the intentional UTC+8 delta."""

    from .era5 import (
        extract_daily_temperature,
        load_daily_dates,
        load_daily_metric,
        utc_daily_validation,
    )

    quality = request.config.data["quality"]
    required = bool(quality.get("require_utc_daily_validation", True))
    inputs = request.config.data.get("inputs", {})
    hourly_pattern = inputs.get("era5_hourly_pattern")
    hourly_overrides = inputs.get("era5_hourly_overrides", {})
    validation_pattern = inputs.get("era5_daily_validation_pattern")
    configured_years = tuple(
        int(value)
        for value in request.config.data.get("years", {}).get(
            "daily_validation", ()
        )
    )
    years = tuple(sorted(set(configured_years).intersection(request.scope.years)))
    if not hourly_pattern or not validation_pattern or not years:
        status = "SKIPPED_EXPLICITLY" if not required else "MISSING_REQUIRED_INPUT"
        gate = {
            "status": status,
            "required": required,
            "years": list(years),
            "hourly_pattern_configured": bool(hourly_pattern),
            "validation_pattern_configured": bool(validation_pattern),
        }
        failures = (
            []
            if not required
            else ["UTC daily validation is required but its patterns/years are unavailable"]
        )
        return gate, {}, failures

    reproduction_frames: list[pd.DataFrame] = []
    difference_rows: list[dict[str, Any]] = []
    daily_root = _stage_file(request.context, "era_daily", "daily_cache")
    metric_names = (
        "era5u8_tmean_c",
        "era5u8_tmax_c",
        "era5u8_tmin_c",
    )
    for year in years:
        reproduction_frames.append(
            utc_daily_validation(
                str(hourly_pattern),
                str(validation_pattern),
                year,
                crosswalk,
                file_overrides=hourly_overrides,
            )
        )
        utc_dates, utc_values, _metadata = extract_daily_temperature(
            str(hourly_pattern),
            year,
            crosswalk,
            file_overrides=hourly_overrides,
            utc_offset_hours=0,
        )
        utc8_dates = load_daily_dates(daily_root, year)
        if not np.array_equal(utc_dates, utc8_dates):
            raise StageValidationError(
                f"UTC and UTC+8 calendar-date labels differ for {year}"
            )
        for metric in metric_names:
            utc8 = np.asarray(load_daily_metric(daily_root, year, metric), dtype=float)
            utc = np.asarray(utc_values[metric], dtype=float)
            delta = utc8 - utc
            finite = np.isfinite(delta)
            difference_rows.append(
                {
                    "year": year,
                    "variable": metric,
                    "comparison": "UTC+8 minus UTC",
                    "n_compared": int(finite.sum()),
                    "mean_difference": float(np.nanmean(delta)),
                    "mean_absolute_difference": float(np.nanmean(np.abs(delta))),
                    "rmse": float(np.sqrt(np.nanmean(delta**2))),
                    "max_absolute_difference": float(np.nanmax(np.abs(delta))),
                }
            )
    reproduction = pd.concat(reproduction_frames, ignore_index=True, sort=False)
    difference = pd.DataFrame(difference_rows)
    reproduction_path = request.work_dir / "era5_utc_daily_reproduction.csv"
    difference_path = request.work_dir / "era5_utc8_vs_utc_summary.csv"
    reproduction.to_csv(reproduction_path, index=False, encoding="utf-8-sig")
    difference.to_csv(difference_path, index=False, encoding="utf-8-sig")
    tolerance = float(quality.get("utc_daily_reproduction_tolerance_c", 1e-4))
    coordinate_tolerance = float(quality.get("coordinate_tolerance", 1e-8))
    failures: list[str] = []
    if reproduction.empty:
        failures.append("UTC daily reproduction returned no comparable variables")
    else:
        invalid_rows = reproduction["n_compared"].le(0)
        excessive = reproduction["max_absolute_difference"].gt(tolerance)
        coordinate_error = (
            reproduction["reference_lat_error"].gt(coordinate_tolerance)
            | reproduction["reference_lon_error"].gt(coordinate_tolerance)
        )
        if invalid_rows.any():
            failures.append(
                f"UTC daily reproduction has {int(invalid_rows.sum())} empty comparisons"
            )
        if excessive.any():
            failures.append(
                f"UTC daily reproduction has {int(excessive.sum())} rows above "
                f"{tolerance:g} degC"
            )
        if coordinate_error.any():
            failures.append(
                f"Legacy daily coordinate axes exceed {coordinate_tolerance:g} degrees"
            )
    gate = {
        "status": "FAIL" if failures else "PASS",
        "required": required,
        "years": list(years),
        "rows": len(reproduction),
        "tolerance_c": tolerance,
        "max_absolute_difference_c": (
            float(reproduction["max_absolute_difference"].max())
            if not reproduction.empty
            else None
        ),
        "utc8_vs_utc_rows": len(difference),
    }
    return (
        gate,
        {
            "utc_daily_reproduction": reproduction_path,
            "utc8_vs_utc_summary": difference_path,
        },
        failures,
    )


def _v3_zone_labels(
    request: StageRequest,
    crosswalk: pd.DataFrame,
) -> np.ndarray:
    from config import MAIZE_ZONE_MAP

    source = Path(request.config.data["inputs"]["v3_main"])
    if source.suffix.lower() in {".parquet", ".pq"}:
        v3 = pd.read_parquet(source, columns=["grid_id", "province"])
    elif source.suffix.lower() == ".dta":
        v3 = pd.read_stata(source, convert_categoricals=False)[
            ["grid_id", "province"]
        ]
    else:
        v3 = pd.read_csv(source, usecols=["grid_id", "province"])
    stable = v3[["grid_id", "province"]].drop_duplicates()
    if stable.groupby("grid_id")["province"].nunique(dropna=False).max() != 1:
        raise StageValidationError("V3 province is not stable within grid_id")
    selected = crosswalk[["grid_id_v3"]].merge(
        stable,
        left_on="grid_id_v3",
        right_on="grid_id",
        how="left",
        validate="one_to_one",
    )
    if selected["province"].isna().any():
        raise StageValidationError("Selected climate cells lack V3 province labels")
    return selected["province"].map(MAIZE_ZONE_MAP).fillna("Other").to_numpy(
        dtype=object
    )


def _accumulate_occurrence(
    accumulator: dict[tuple[str, str, str, str], list[int]],
    *,
    family: str,
    layer: str,
    indicator: str,
    active: np.ndarray,
    valid: np.ndarray,
    zones: np.ndarray,
) -> None:
    if active.shape != valid.shape or active.ndim < 2 or active.shape[-1] != len(zones):
        raise ValueError("Historical occurrence arrays do not match zone labels")
    if not np.issubdtype(active.dtype, np.bool_) or not np.issubdtype(
        valid.dtype, np.bool_
    ):
        raise ValueError("Historical occurrence active/valid states must be binary")
    for zone in ("Overall", *sorted(set(str(value) for value in zones))):
        selected = np.ones(len(zones), dtype=bool) if zone == "Overall" else zones == zone
        key = (family, layer, indicator, zone)
        counts = accumulator.setdefault(key, [0, 0])
        counts[0] += int(np.sum(active[..., selected] & valid[..., selected]))
        counts[1] += int(np.sum(valid[..., selected]))


def _run_historical_occurrence_validation(
    request: StageRequest,
    crosswalk: pd.DataFrame,
) -> tuple[dict[str, Any], dict[str, Path], list[str]]:
    """Check 1981-2010 ERA/GLEAM tail rates overall and by frozen maize zone."""

    from .era5 import canonical_day_index, load_daily_dates, load_daily_metric
    from .gleam import compute_pentad_climatology, daily_values_to_pentads

    quality = request.config.data["quality"]
    required = bool(quality.get("require_historical_occurrence_validation", True))
    if not required:
        return {"status": "SKIPPED_EXPLICITLY", "required": False}, {}, []
    historical_years = tuple(sorted(int(value) for value in request.config.historical_years))
    if not historical_years:
        return (
            {"status": "MISSING_REQUIRED_INPUT", "required": True},
            {},
            ["Historical occurrence validation has no configured baseline years"],
        )
    zones = _v3_zone_labels(request, crosswalk)
    n_cells = len(crosswalk)
    block_size = int(
        request.config.data.get("runtime", {}).get("validation_cell_block_size", 128)
    )
    configured_tolerance = quality.get("historical_occurrence_tolerance")
    tolerance = (
        None if configured_tolerance is None else float(configured_tolerance)
    )
    if tolerance is not None and tolerance < 0:
        raise ValueError("quality.historical_occurrence_tolerance must be non-negative")
    minimum_historical_years = max(
        1,
        math.ceil(
            len(historical_years)
            * float(
                request.config.data["temperature"].get(
                    "minimum_history_fraction", 0.90
                )
            )
            - 1e-12
        ),
    )
    accumulator: dict[tuple[str, str, str, str], list[int]] = {}

    era_daily_root = _stage_file(request.context, "era_daily", "daily_cache")
    threshold_root = _stage_file(request.context, "era_baseline", "thresholds")
    temperature_thresholds = {
        "tx90": np.load(
            threshold_root / "era5u8_tmax_p90_calendar.npy", mmap_mode="r"
        ),
        "tn90": np.load(
            threshold_root / "era5u8_tmin_p90_calendar.npy", mmap_mode="r"
        ),
    }
    temperature_metrics = {"tx90": "era5u8_tmax_c", "tn90": "era5u8_tmin_c"}
    canonical_by_year = {
        year: np.asarray(
            [canonical_day_index(value) for value in load_daily_dates(era_daily_root, year)],
            dtype=np.int16,
        )
        for year in historical_years
    }
    for start in range(0, n_cells, block_size):
        stop = min(start + block_size, n_cells)
        block_zones = zones[start:stop]
        for indicator, metric in temperature_metrics.items():
            for year in historical_years:
                values = np.asarray(
                    load_daily_metric(era_daily_root, year, metric)[:, start:stop],
                    dtype=float,
                )
                thresholds = np.asarray(
                    temperature_thresholds[indicator][canonical_by_year[year], start:stop],
                    dtype=float,
                )
                valid = np.isfinite(values) & np.isfinite(thresholds)
                _accumulate_occurrence(
                    accumulator,
                    family="era5",
                    layer="temperature",
                    indicator=indicator,
                    active=values > thresholds,
                    valid=valid,
                    zones=block_zones,
                )

    import netCDF4 as nc

    gleam_daily_root = _stage_file(request.context, "gleam_daily", "daily_cache")
    for raw_layer in request.config.data["gleam"]["layers"]:
        layer = str(raw_layer)
        with ExitStack() as stack:
            datasets = {
                year: stack.enter_context(
                    nc.Dataset(_gleam_partition_path(gleam_daily_root, layer, year))
                )
                for year in historical_years
            }
            dates_by_year = {
                year: _netcdf_python_dates(dataset)
                for year, dataset in datasets.items()
            }
            for start in range(0, n_cells, block_size):
                stop = min(start + block_size, n_cells)
                histories: list[np.ndarray] = []
                for year in historical_years:
                    daily_values = np.ma.filled(
                        datasets[year].variables[layer][:, start:stop], np.nan
                    ).astype(float, copy=False)
                    histories.append(
                        daily_values_to_pentads(dates_by_year[year], daily_values).values
                    )
                history = np.stack(histories, axis=0)
                climatology = compute_pentad_climatology(
                    history, min_historical_years=minimum_historical_years
                )
                block_zones = zones[start:stop]
                for indicator, threshold in (
                    ("pentad_sm_p10", climatology.q10),
                    ("pentad_sm_p20", climatology.q20),
                ):
                    valid = np.isfinite(history) & np.isfinite(threshold)[None, :, :]
                    _accumulate_occurrence(
                        accumulator,
                        family="gleam43a",
                        layer=layer,
                        indicator=indicator,
                        active=history < threshold[None, :, :],
                        valid=valid,
                        zones=block_zones,
                    )

    expected_rates = {
        "tx90": 0.10,
        "tn90": 0.10,
        "pentad_sm_p10": 0.10,
        "pentad_sm_p20": 0.20,
    }
    rows: list[dict[str, Any]] = []
    failures: list[str] = []
    for (family, layer, indicator, zone), (hits, valid) in sorted(accumulator.items()):
        rate = hits / valid if valid else math.nan
        expected = expected_rates[indicator]
        deviation = rate - expected if valid else math.nan
        within = (
            None
            if tolerance is None
            else bool(valid and abs(deviation) <= tolerance)
        )
        rows.append(
            {
                "history_start": min(historical_years),
                "history_end": max(historical_years),
                "history_years": len(historical_years),
                "family": family,
                "layer": layer,
                "indicator": indicator,
                "zone": zone,
                "hits": hits,
                "valid": valid,
                "rate": rate,
                "expected_rate": expected,
                "deviation_from_expected": deviation,
                "tolerance": tolerance,
                "within_tolerance": within,
            }
        )
        if not valid or not math.isfinite(rate):
            failures.append(
                f"Historical rate {family}/{layer}/{indicator}/{zone} has no valid values"
            )
        elif rate < 0.0 or rate > 1.0:
            failures.append(
                f"Historical rate {family}/{layer}/{indicator}/{zone} is non-binary: "
                f"{rate:.6g}"
            )
        elif tolerance is not None and not within:
            failures.append(
                f"Historical rate {family}/{layer}/{indicator}/{zone}="
                f"{rate:.6g} is outside {expected:.2f}+/-{tolerance:.2f}"
            )
    if not rows:
        failures.append("Historical occurrence validation produced no indicators")
    report = pd.DataFrame(rows)
    path = request.work_dir / "historical_occurrence_rates_by_maize_zone.csv"
    report.to_csv(path, index=False, encoding="utf-8-sig")
    gate = {
        "status": "FAIL" if failures else "PASS",
        "required": True,
        "history_period": [min(historical_years), max(historical_years)],
        "history_years": len(historical_years),
        "rows": len(report),
        "tolerance": tolerance,
        "rate_deviation_gate": "diagnostic_only" if tolerance is None else "configured_hard_gate",
        "zones": sorted(str(value) for value in report["zone"].unique()),
    }
    return gate, {"historical_occurrence_rates": path}, failures


def _read_v3_validation_projection(
    v3_path: Path,
    legacy_fields: Sequence[str],
) -> pd.DataFrame:
    """Read only the V3 keys, coordinates, and frozen legacy SPEI fields."""

    import pyarrow.parquet as pq

    schema_names = set(pq.ParquetFile(v3_path).schema_arrow.names)
    projected_columns = [
        name
        for name in (
            "grid_id",
            "year",
            "lat10",
            "lon10",
            "latitude",
            "longitude",
            *legacy_fields,
        )
        if name in schema_names
    ]
    required = {"grid_id", "year", *legacy_fields}
    if not required.issubset(projected_columns):
        raise StageValidationError("V3 main lacks projected legacy fields")
    if not ({"lat10", "latitude"} & set(projected_columns)) or not (
        {"lon10", "longitude"} & set(projected_columns)
    ):
        raise StageValidationError("V3 main lacks projected coordinate fields")
    return pd.read_parquet(v3_path, columns=projected_columns)


def _handle_validate(request: StageRequest) -> StageOutcome:
    from .export import LONG_KEY_COLUMNS, WIDE_KEY_COLUMNS
    from .validate import (
        validate_export_bundle_full,
        validate_legacy_fields,
        validate_v3_coordinate_year_match,
    )

    marker_rows: list[dict[str, Any]] = []
    failures: list[str] = []
    validation_artifacts: dict[str, Path] = {}
    for stage in STAGE_ORDER:
        if stage == "validate":
            continue
        marker_path = request.context.stages_dir / stage / "_SUCCESS.json"
        if not marker_path.is_file():
            failures.append(f"missing marker: {stage}")
            continue
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
        if marker.get("config_sha256") != request.config.sha256:
            failures.append(f"config hash mismatch: {stage}")
        if marker.get("source_tree_sha256") != request.context.source_tree_sha256:
            failures.append(f"source-tree hash mismatch: {stage}")
        if marker.get("environment_sha256") != request.context.environment_sha256:
            failures.append(f"runtime-environment hash mismatch: {stage}")
        marker_artifacts = marker.get("extra", {}).get("artifacts", {})
        for name, raw_path in marker_artifacts.items():
            linked = request.context.run_dir / str(raw_path)
            if not linked.exists():
                failures.append(f"published marker artifact missing: {stage}/{name}")
        stage_result_path = request.context.stages_dir / stage / "_STAGE_RESULT.json"
        if not stage_result_path.is_file():
            failures.append(f"stage result missing: {stage}")
        else:
            stage_result = json.loads(stage_result_path.read_text(encoding="utf-8"))
            result_artifacts = stage_result.get("artifacts", {})
            result_hashes = stage_result.get("artifact_hashes", {})
            if set(result_artifacts) != set(result_hashes):
                failures.append(f"stage result artifact/hash keys differ: {stage}")
            for name, raw_path in result_artifacts.items():
                linked = request.context.run_dir / str(raw_path)
                if not linked.exists():
                    failures.append(f"published stage-result artifact missing: {stage}/{name}")
                elif sha256_path(linked) != result_hashes.get(name):
                    failures.append(f"published stage-result hash mismatch: {stage}/{name}")
        marker_rows.append(
            {
                "stage": stage,
                "marker": str(marker_path),
                "parameter_sha256": marker.get("parameter_sha256"),
                "row_counts": marker.get("row_counts", {}),
                "output_hash_count": len(marker.get("output_hashes", {})),
            }
        )

    bundle = _stage_file(request.context, "export", "bundle")
    long_path = bundle / "climate_stress_long.parquet"
    wide_path = bundle / "climate_stress_wide.parquet"
    netcdf_path = bundle / "climate_stress_cube.nc"
    dta_path = bundle / "climate_stress_merge_ready.dta"
    alias_path = bundle / "stata_alias_map.csv"
    gates: dict[str, Any] = {}
    legacy_report = pd.DataFrame()
    try:
        validation_crosswalk = pd.read_parquet(
            _stage_file(request.context, "grid", "crosswalk.parquet")
        ).sort_values("era01_cell_id").reset_index(drop=True)
        selected_cells = len(validation_crosswalk)
        expected_long = selected_cells * len(request.scope.years) * len(
            request.config.windows
        )
        expected_wide = selected_cells * len(request.scope.years)
        tolerance = float(request.config.data["quality"]["numeric_tolerance"])
        gates["full_export_roundtrip"] = validate_export_bundle_full(
            _stage_file(
                request.context, "aggregate", "climate_window_long.parquet"
            ),
            long_path,
            wide_path,
            netcdf_path,
            dta_path,
            alias_path,
            years=request.scope.years,
            windows=request.config.windows,
            tolerance=tolerance,
            metric_batch_size=int(
                request.config.data.get("runtime", {}).get(
                    "validation_metric_batch_size", 8
                )
            ),
            dta_row_batch_size=int(
                request.config.data.get("runtime", {}).get(
                    "validation_row_batch_size", 50_000
                )
            ),
            spatial_row_block=int(
                request.config.data.get("runtime", {}).get(
                    "validation_spatial_row_block", 32
                )
            ),
        )
        long_report = gates["full_export_roundtrip"]["long_parquet"]
        wide_report = gates["full_export_roundtrip"]["wide_parquet"]
        if int(long_report["rows"]) != expected_long:
            raise StageValidationError("Streamed long validation row count is incorrect")
        if int(wide_report["rows"]) != expected_wide:
            raise StageValidationError("Streamed wide validation row count is incorrect")
        gates["long_panel"] = {
            "rows": int(long_report["rows"]),
            "selected_cells": selected_cells,
            "years": len(request.scope.years),
            "windows": len(request.config.windows),
            "validation_mode": "partitioned_full_value_comparison",
        }
        gates["wide_panel"] = {
            "rows": int(wide_report["rows"]),
            "selected_cells": selected_cells,
            "years": len(request.scope.years),
            "validation_mode": "partitioned_full_value_comparison",
        }
        manifest_path = bundle / "manifest.json"
        bundle_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        published_outputs = bundle_manifest.get("outputs", {})
        published_audits = bundle_manifest.get("audit_artifacts", {})
        manifest_link_failures: list[str] = []
        for section, records in (
            ("output", published_outputs),
            ("audit", published_audits),
        ):
            for name, record in sorted(records.items()):
                raw_path = Path(str(record.get("path", "")))
                if raw_path.is_absolute() or ".partial" in raw_path.parts:
                    manifest_link_failures.append(
                        f"unstable manifest {section} path: {name}"
                    )
                    continue
                linked = request.context.run_dir / raw_path
                kind = str(record.get("kind", "file"))
                if kind == "directory":
                    exists = linked.is_dir()
                else:
                    exists = linked.is_file()
                if not exists:
                    manifest_link_failures.append(
                        f"missing manifest {section}: {name}"
                    )
                    continue
                if sha256_path(linked) != record.get("sha256"):
                    manifest_link_failures.append(
                        f"manifest {section} hash mismatch: {name}"
                    )
                if linked.is_dir():
                    files = [item for item in linked.rglob("*") if item.is_file()]
                    observed_bytes = sum(item.stat().st_size for item in files)
                    if len(files) != int(record.get("file_count", -1)):
                        manifest_link_failures.append(
                            f"manifest {section} file-count mismatch: {name}"
                        )
                else:
                    observed_bytes = linked.stat().st_size
                if observed_bytes != int(record.get("bytes", -1)):
                    manifest_link_failures.append(
                        f"manifest {section} byte mismatch: {name}"
                    )
        failures.extend(manifest_link_failures)
        gates["published_artifact_links"] = {
            "manifest_outputs": len(published_outputs),
            "manifest_audits": len(published_audits),
            "failures": manifest_link_failures,
        }
        spei_2w_failures: list[str] = []
        spei_audit_path = _stage_file(
            request.context, "spei", "spei_2w_audit.json"
        )
        spei_audit = json.loads(spei_audit_path.read_text(encoding="utf-8"))
        spei_marker = json.loads(
            (
                request.context.stages_dir / "spei" / "_SUCCESS.json"
            ).read_text(encoding="utf-8")
        )
        output_contract = json.loads(
            (bundle / "output_contract.json").read_text(encoding="utf-8")
        )
        passport = json.loads(
            (bundle / "material_passport.json").read_text(encoding="utf-8")
        )
        output_2w = output_contract.get("spei_2w", {})
        marker_2w = spei_marker.get("extra", {}).get("spei_2w", {})
        manifest_2w = bundle_manifest.get("metadata", {}).get(
            "spei_2w_stage_evidence", {}
        )
        full_scope = request.context.completion_scope_status == "FULL_SCOPE"
        if full_scope:
            if not (
                spei_audit.get("status") == "EXECUTED"
                and spei_audit.get("numeric_executed") is True
                and spei_audit.get("endpoint_decision_status") == "CONFIRMED"
                and all(
                    int(spei_audit.get(name, 0)) > 0
                    for name in (
                        "release_count",
                        "cell_count",
                        "canonical_field_count",
                    )
                )
            ):
                spei_2w_failures.append("SPEI-2W full-scope audit is incomplete")
        elif not (
            spei_audit.get("status") == SPEI_2W_PENDING_STATUS
            and spei_audit.get("numeric_executed") is False
            and spei_audit.get("endpoint_decision_status")
            == "PENDING_USER_DECISION"
            and all(
                int(spei_audit.get(name, -1)) == 0
                for name in (
                    "release_count",
                    "cell_count",
                    "canonical_field_count",
                    "event_rows",
                    "bridge_rows",
                )
            )
        ):
            spei_2w_failures.append("SPEI-2W partial-scope audit is not disabled")
        if marker_2w != spei_audit:
            spei_2w_failures.append("SPEI-2W stage marker differs from audit")
        if output_2w.get("stage_evidence") != spei_audit:
            spei_2w_failures.append("SPEI-2W output contract differs from audit")
        if manifest_2w != spei_audit:
            spei_2w_failures.append("SPEI-2W manifest evidence differs from audit")
        if passport.get("spei_2w_stage_evidence") != spei_audit:
            spei_2w_failures.append("SPEI-2W Material Passport differs from audit")
        expected_output_flag = full_scope
        if not (
            output_2w.get("numeric_executed") is expected_output_flag
            and output_2w.get("output_included") is expected_output_flag
        ):
            spei_2w_failures.append("SPEI-2W output flags differ from scope")
        import netCDF4 as nc
        import pyarrow.parquet as pq

        canonical_2w_fields = [
            name
            for name in pq.ParquetFile(long_path).schema_arrow.names
            if name.startswith("chm_spei_2w_")
        ]
        if len(canonical_2w_fields) != int(
            spei_audit.get("canonical_field_count", -1)
        ):
            spei_2w_failures.append("SPEI-2W canonical field count differs")
        if not full_scope and canonical_2w_fields:
            spei_2w_failures.append("PARTIAL_SCOPE contains SPEI-2W fields")
        observed_events, _event_batch = _count_parquet_value_batched(
            _stage_file(request.context, "spei", "chm_spei_events.parquet"),
            column="timescale",
            value="2W",
        )
        observed_bridges, _bridge_batch = _count_parquet_value_batched(
            _stage_file(
                request.context,
                "spei",
                "chm_spei_event_window_bridge.parquet",
            ),
            column="timescale",
            value="2W",
        )
        if observed_events != int(spei_audit.get("event_rows", -1)):
            spei_2w_failures.append("SPEI-2W event row count differs")
        if observed_bridges != int(spei_audit.get("bridge_rows", -1)):
            spei_2w_failures.append("SPEI-2W bridge row count differs")
        dictionary = pd.read_csv(
            bundle / "variable_dictionary.csv", encoding="utf-8-sig"
        )
        if set(dictionary["scope_id"].astype(str)) != {
            request.context.scope_profile
        } or set(dictionary["scope_status"].astype(str)) != {
            request.context.completion_scope_status
        }:
            spei_2w_failures.append("Variable dictionary scope metadata differs")
        with nc.Dataset(netcdf_path) as netcdf_dataset:
            if (
                netcdf_dataset.getncattr("output_scope_id")
                != request.context.scope_profile
                or netcdf_dataset.getncattr("output_scope_status")
                != request.context.completion_scope_status
            ):
                spei_2w_failures.append("NetCDF scope attributes differ")
        failures.extend(spei_2w_failures)
        gates["spei_2w_scope_contract"] = {
            "status": "FAIL" if spei_2w_failures else "PASS",
            "scope_status": request.context.completion_scope_status,
            "release_count": int(spei_audit.get("release_count", 0)),
            "cell_count": int(spei_audit.get("cell_count", 0)),
            "canonical_field_count": len(canonical_2w_fields),
            "event_rows": observed_events,
            "bridge_rows": observed_bridges,
            "failures": spei_2w_failures,
        }
        utc_gate, utc_artifacts, utc_failures = _run_utc_validation(
            request, validation_crosswalk
        )
        gates["utc_daily_validation"] = utc_gate
        validation_artifacts.update(utc_artifacts)
        failures.extend(utc_failures)
        historical_gate, historical_artifacts, historical_failures = (
            _run_historical_occurrence_validation(
                request, validation_crosswalk
            )
        )
        gates["historical_occurrence_validation"] = historical_gate
        validation_artifacts.update(historical_artifacts)
        failures.extend(historical_failures)
        if not request.scope.is_pilot:
            from .spei import LEGACY_FIELD_MAP

            legacy_fields = [
                field for pair in LEGACY_FIELD_MAP.values() for field in pair
            ]
            v3_path = Path(request.config.data["inputs"]["v3_main"])
            v3 = _read_v3_validation_projection(v3_path, legacy_fields)
            wide_keys = pd.read_parquet(wide_path, columns=list(WIDE_KEY_COLUMNS))
            v3_coordinate_tolerance = float(
                request.config.data["grid"].get(
                    "v3_coordinate_tolerance_degrees", 1e-5
                )
            )
            gates["v3_coordinate_year_match"] = validate_v3_coordinate_year_match(
                wide_keys,
                v3,
                expected_v3_rows=69_038,
                coordinate_tolerance=v3_coordinate_tolerance,
            )
            selection = json.loads(
                _stage_file(request.context, "grid", "selection.json").read_text(
                    encoding="utf-8"
                )
            )
            gates["v3_coordinate_year_match"]["coordinate_tolerance_degrees"] = (
                v3_coordinate_tolerance
            )
            gates["v3_coordinate_year_match"]["coordinate_alignment"] = selection[
                "v3_coordinate_alignment"
            ]
            legacy_path = _stage_file(
                request.context, "spei", "legacy_v3_exact.parquet"
            )
            if not legacy_path.is_file():
                raise StageValidationError("Full run lacks legacy_v3_exact sidecar")
            legacy_report = validate_legacy_fields(
                pd.read_parquet(
                    legacy_path,
                    columns=["grid_id", "year", *legacy_fields],
                ),
                v3,
                legacy_fields,
                keys=("grid_id", "year"),
                tolerance=tolerance,
                required_field_count=12,
            )
            gates["legacy_v3_exact"] = {
                "fields": len(legacy_report),
                "candidate_rows": int(legacy_report["candidate_rows"].iloc[0]),
                "reference_rows": int(legacy_report["reference_rows"].iloc[0]),
                "matched_rows": int(legacy_report["matched_rows"].iloc[0]),
                "candidate_only_rows": int(
                    legacy_report["candidate_only_rows"].iloc[0]
                ),
                "reference_only_rows": int(
                    legacy_report["reference_only_rows"].iloc[0]
                ),
                "max_abs_difference": float(
                    legacy_report["max_abs_difference"].max()
                ),
            }
        gates["canonical_key_columns"] = list(LONG_KEY_COLUMNS)
    except (AssertionError, OSError, TypeError, ValueError, RuntimeError) as exc:
        failures.append(f"{type(exc).__name__}: {exc}")

    validation_status = "FAIL" if failures else "PASS"
    scope = request.config.data["scope"]
    scope_status = request.context.completion_scope_status
    scope_contract = {
        "status": scope_status,
        "completion_scope_status": scope_status,
        "scope_profile": request.context.scope_profile,
        "spei_2w_numeric": bool(scope["spei_2w_numeric"]),
        "spei_2w_output": bool(scope["spei_2w_output"]),
        "spei_2w_numeric_enabled": bool(scope["spei_2w_numeric"]),
        "spei_2w_output_enabled": bool(scope["spei_2w_output"]),
        "compound_mode": str(scope["compound_mode"]),
    }
    report_path = request.work_dir / "validation_report.json"
    _write_json_new(
        report_path,
        {
            **scope_contract,
            "validation_status": validation_status,
            "failures": failures,
            "gates": gates,
            "stages": marker_rows,
        },
    )
    artifacts = {"validation_report": report_path, **validation_artifacts}
    if not legacy_report.empty:
        legacy_report_path = request.work_dir / "legacy_v3_exact_validation.csv"
        legacy_report.to_csv(legacy_report_path, index=False, encoding="utf-8-sig")
        artifacts["legacy_validation"] = legacy_report_path
    if failures:
        raise StageValidationError(f"Validation failures: {failures}")
    return StageOutcome(
        artifacts=artifacts,
        row_counts={
            "validated_stages": len(marker_rows),
            "validation_gates": len(gates),
        },
        extra={
            **scope_contract,
            "validation_status": validation_status,
        },
    )


def default_handlers() -> dict[str, StageHandler]:
    return {
        "assets": _handle_assets,
        "grid": _handle_grid,
        "phenology": _handle_phenology,
        "era_daily": _handle_era_daily,
        "era_baseline": _handle_era_baseline,
        "spei": _handle_spei,
        "gleam_daily": _handle_gleam_daily,
        "gleam_baseline": _handle_gleam_baseline,
        "events": _handle_events,
        "aggregate": _handle_aggregate,
        "export": _handle_export,
        "validate": _handle_validate,
    }


@dataclass
class ClimateStressPipeline:
    config: PipelineConfig
    context: RunContext
    scope: ExecutionScope
    handlers: Mapping[str, StageHandler] = field(default_factory=default_handlers)
    resume: bool = False
    invocation_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    quality_records: list[dict[str, Any]] = field(default_factory=list, init=False)
    audit_issues: list[InvocationAuditIssue] = field(default_factory=list, init=False)
    diagnostic_issues: list[InvocationAuditIssue] = field(
        default_factory=list,
        init=False,
    )
    active_stage_partials: dict[str, Path | None] = field(
        default_factory=dict,
        init=False,
    )
    authoritative_stage_markers: dict[str, dict[str, Any]] = field(
        default_factory=dict,
        init=False,
    )
    completed_run_results: list[dict[str, Any]] = field(
        default_factory=list,
        init=False,
    )
    requested_stage_execution_completed: bool = field(default=False, init=False)

    def stage_parameters(self, stage: str) -> dict[str, Any]:
        return {"stage": stage, **self.scope.as_parameters()}

    def _input_hashes(self, stage: str) -> dict[str, str]:
        hashes = {"config": self.config.sha256}
        for dependency in STAGE_DEPENDENCIES[stage]:
            marker = self.context.stages_dir / dependency / "_SUCCESS.json"
            if not marker.is_file():
                raise FileNotFoundError(f"Dependency marker is missing: {marker}")
            payload = json.loads(marker.read_text(encoding="utf-8"))
            stable_payload = {
                key: value
                for key, value in payload.items()
                if key not in {"completed_at_utc", "elapsed_seconds"}
            }
            hashes[f"dependency:{dependency}"] = parameter_signature(stable_payload)
        return hashes

    def _verify_completed_stage(self, stage: str, marker: Mapping[str, Any]) -> None:
        """Re-hash every published artifact before accepting a resume skip."""

        expected_hashes = dict(marker.get("output_hashes", {}))
        linked_artifacts = dict(marker.get("extra", {}).get("artifacts", {}))
        expected_names = set(expected_hashes) - {"_stage_result"}
        if set(linked_artifacts) != expected_names:
            raise StageValidationError(
                f"Completed stage {stage} artifact/hash keys differ"
            )
        for name, raw_path in sorted(linked_artifacts.items()):
            path = ensure_within_run(
                self.context.run_dir / str(raw_path), self.context.run_dir
            )
            if not path.exists() or sha256_path(path) != expected_hashes[name]:
                raise StageValidationError(
                    f"Completed stage {stage} artifact hash mismatch: {name}"
                )
        result_path = self.context.stages_dir / stage / "_STAGE_RESULT.json"
        if (
            not result_path.is_file()
            or sha256_file(result_path) != expected_hashes.get("_stage_result")
        ):
            raise StageValidationError(
                f"Completed stage {stage} stage-result hash mismatch"
            )
        if stage == "assets" and "inventory_parquet" in linked_artifacts:
            inventory_path = ensure_within_run(
                self.context.run_dir / str(linked_artifacts["inventory_parquet"]),
                self.context.run_dir,
            )
            self._verify_inventory_sources(inventory_path)

    def _verify_inventory_sources(self, inventory_path: Path) -> None:
        """Re-fingerprint every external source before trusting a resumed run."""

        from .inventory import fingerprint_file

        if not inventory_path.is_file():
            raise StageValidationError(
                f"Resumed assets stage lacks source inventory: {inventory_path}"
            )
        records = pd.read_parquet(inventory_path)
        failures: list[str] = []
        for row in records.to_dict("records"):
            asset_id = str(row.get("asset_id"))
            source = Path(str(row.get("path")))
            if not bool(row.get("exists")) or not source.is_file():
                failures.append(f"{asset_id}: missing source {source}")
                continue
            mode = "full" if bool(row.get("hash_is_full")) else "pilot"
            current = fingerprint_file(source, mode=mode)
            expected = {
                "size_bytes": int(row["size_bytes"]),
                "mtime_utc": str(row["mtime_utc"]),
                "sha256": str(row["sha256"]),
                "hash_algorithm": str(row["hash_algorithm"]),
                "hash_is_full": bool(row["hash_is_full"]),
            }
            observed = {
                "size_bytes": current.size_bytes,
                "mtime_utc": current.mtime_utc,
                "sha256": current.sha256,
                "hash_algorithm": current.hash_algorithm,
                "hash_is_full": current.hash_is_full,
            }
            if observed != expected:
                failures.append(
                    f"{asset_id}: fingerprint changed for {source}"
                )
        if failures:
            raise StageValidationError(
                "Resumed raw source fingerprint mismatch: " + "; ".join(failures)
            )

    def _stage_start_payload(
        self,
        stage: str,
        *,
        input_hashes: Mapping[str, str],
    ) -> dict[str, Any]:
        parameters = self.stage_parameters(stage)
        signature = parameter_signature(
            {
                "run": self.context.parameters,
                "stage": parameters,
                "source_tree_sha256": self.context.source_tree_sha256,
                "environment_sha256": self.context.environment_sha256,
            }
        )
        return {
            "schema_version": 1,
            "stage": stage,
            "config_sha256": self.config.sha256,
            "source_tree_sha256": self.context.source_tree_sha256,
            "environment_sha256": self.context.environment_sha256,
            "parameter_sha256": signature,
            "parameters": {
                "run": self.context.parameters,
                "stage": parameters,
            },
            "input_hashes": dict(sorted(input_hashes.items())),
        }

    def _start_or_resume_partial(
        self,
        stage: str,
        *,
        input_hashes: Mapping[str, str],
    ) -> tuple[StageSession, bool]:
        """Start a stage or reuse one exact-signature failed partial directory."""

        target = ensure_within_run(
            self.context.stages_dir / stage, self.context.run_dir
        )
        if target.exists():
            return (
                start_stage(
                    self.context,
                    stage,
                    parameters=self.stage_parameters(stage),
                    resume=self.resume,
                ),
                False,
            )
        expected = self._stage_start_payload(stage, input_hashes=input_hashes)
        if self.resume:
            matching: list[Path] = []
            for candidate in self.context.stages_dir.glob(
                f".{stage}.*.partial"
            ):
                if not candidate.is_dir():
                    continue
                start_path = candidate / STAGE_START
                try:
                    observed = json.loads(start_path.read_text(encoding="utf-8"))
                except (OSError, ValueError, json.JSONDecodeError):
                    continue
                if observed == expected:
                    matching.append(candidate)
            if matching:
                partial = max(
                    matching,
                    key=lambda path: (path.stat().st_mtime_ns, path.name),
                )
                parameters = self.stage_parameters(stage)
                return (
                    StageSession(
                        context=self.context,
                        stage=stage,
                        parameters=parameters,
                        parameter_sha256=expected["parameter_sha256"],
                        target_dir=target,
                        partial_dir=partial,
                        started_monotonic=time.monotonic(),
                    ),
                    True,
                )
        session = start_stage(
            self.context,
            stage,
            parameters=self.stage_parameters(stage),
            resume=self.resume,
        )
        _write_json_new(session.work_dir / STAGE_START, expected)
        return session, False

    def _recover_stage_outcome(
        self,
        session: StageSession,
    ) -> StageOutcome | None:
        """Recover a handler result written before a late publication failure."""

        result_path = session.work_dir / "_STAGE_RESULT.json"
        if not result_path.is_file():
            return None
        try:
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            if payload.get("stage") != session.stage:
                raise ValueError("stage-result name mismatch")
            recorded = payload["artifacts"]
            recorded_hashes = payload["artifact_hashes"]
            if not isinstance(recorded, dict) or set(recorded) != set(recorded_hashes):
                raise ValueError("stage-result artifact/hash keys differ")
            artifacts: dict[str, Path] = {}
            for name, raw_final in sorted(recorded.items()):
                final_path = ensure_within_run(
                    self.context.run_dir / str(raw_final), self.context.run_dir
                )
                relative = final_path.relative_to(session.target_dir)
                partial_path = ensure_within_run(
                    session.work_dir / relative, self.context.run_dir
                )
                if not partial_path.exists():
                    raise FileNotFoundError(partial_path)
                if sha256_path(partial_path) != str(recorded_hashes[name]):
                    raise ValueError(f"stage-result hash mismatch: {name}")
                artifacts[str(name)] = partial_path
            row_counts = {
                str(name): int(value)
                for name, value in dict(payload.get("row_counts", {})).items()
            }
            if any(value < 0 for value in row_counts.values()):
                raise ValueError("negative stage-result row count")
            extra = dict(payload.get("extra", {}))
            return StageOutcome(
                artifacts=artifacts,
                row_counts=row_counts,
                extra=extra,
            )
        except (
            OSError,
            TypeError,
            ValueError,
            KeyError,
            json.JSONDecodeError,
        ):
            _archive_incomplete(result_path)
            return None

    def _stage_resources(self, start: Mapping[str, Any]) -> dict[str, Any]:
        resources = stage_resource_usage(start, process_memory_snapshot())
        budget = self.config.peak_rss_budget_bytes(self.scope.mode)
        resources.update(
            {
                "execution_mode": self.scope.mode,
                "peak_rss_budget_bytes": budget,
                "budget_exceeded": (
                    resources["process_lifetime_peak_working_set_bytes"] > budget
                ),
            }
        )
        return resources

    def _unavailable_stage_resources(
        self,
        reason: BaseException,
        *,
        start: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return a complete fail-closed resource record without resampling."""

        sampled_at = utc_now()
        start_record = dict(start or {})
        start_rss = max(0, int(start_record.get("rss_bytes", 0)))
        start_peak = max(
            start_rss,
            int(start_record.get("process_peak_rss_bytes", 0)),
        )
        budget = self.config.peak_rss_budget_bytes(self.scope.mode)
        return {
            "stage_start_current_rss_bytes": start_rss,
            "stage_end_current_rss_bytes": 0,
            "process_lifetime_peak_working_set_bytes": start_peak,
            "sampled_start_at_utc": str(
                start_record.get("sampled_at_utc", sampled_at)
            ),
            "sampled_end_at_utc": sampled_at,
            "start_source": str(start_record.get("source", "unavailable")),
            "end_source": "unavailable",
            "execution_mode": self.scope.mode,
            "peak_rss_budget_bytes": budget,
            "budget_exceeded": start_peak > budget,
            "resource_sampling_available": False,
            "resource_sampling_error": {
                "type": type(reason).__name__,
                "message": str(reason),
            },
        }

    @staticmethod
    def _unavailable_resource_workload(
        stage: str,
        reason: BaseException,
    ) -> dict[str, Any]:
        """Return a stable workload record when diagnostic construction fails."""

        return {
            "stage": stage,
            "configured_block_chunk_parameters": {},
            "configured_block_chunk_shapes": {},
            "estimated_block_bytes": {},
            "estimation_note": "Unavailable after diagnostic failure.",
            "artifact_bytes": {},
            "stage_outcome_extra": {},
            "diagnostic_available": False,
            "diagnostic_error": {
                "type": type(reason).__name__,
                "message": str(reason),
            },
        }

    @staticmethod
    def _prior_attempt_resources(work_dir: Path) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        candidates = sorted(work_dir.glob("_FAILED.*.json"))
        result_path = work_dir / "_STAGE_RESULT.json"
        if result_path.is_file():
            candidates.append(result_path)
        for path in candidates:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                resources = payload.get("resources")
                if isinstance(resources, dict):
                    records.append(dict(resources))
            except (OSError, ValueError, json.JSONDecodeError):
                continue
        return records

    def _aggregate_attempt_resources(
        self,
        current: Mapping[str, Any],
        prior: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        result = dict(current)
        attempts = [dict(value) for value in prior]
        peaks = [
            max(0, int(value.get("process_lifetime_peak_working_set_bytes", 0)))
            for value in (*attempts, result)
        ]
        result["process_lifetime_peak_working_set_bytes"] = max(peaks, default=0)
        result["budget_exceeded"] = any(
            bool(value.get("budget_exceeded", False)) for value in attempts
        ) or bool(result.get("budget_exceeded", False)) or (
            result["process_lifetime_peak_working_set_bytes"]
            > int(result["peak_rss_budget_bytes"])
        )
        result["attempt_count"] = len(attempts) + 1
        result["prior_attempt_process_lifetime_peaks_bytes"] = peaks[:-1]
        return result

    def _resource_workload(
        self,
        stage: str,
        *,
        outcome: StageOutcome | None = None,
        artifacts: Mapping[str, Path] | None = None,
    ) -> dict[str, Any]:
        runtime = dict(self.config.data.get("runtime", {}))
        configured = {
            key: value
            for key, value in sorted(runtime.items())
            if any(
                token in key.lower()
                for token in ("block", "chunk", "row_group", "batch", "dtype")
            )
        }
        cells = int(
            self.scope.pilot_cells
            if self.scope.pilot_cells is not None
            else self.config.data["grid"]["expected_cells"]
        )
        dtype_bytes = int(np.dtype(runtime.get("storage_dtype", "float64")).itemsize)
        gleam_cells = int(runtime.get("gleam_cell_block_size", cells))
        validation_cells = int(runtime.get("validation_cell_block_size", cells))
        row_group = int(runtime.get("parquet_row_group_size", 0))
        shapes = {
            "gleam_native_time_by_cell_block": [12, gleam_cells],
            "validation_cell_by_year_by_window": [
                validation_cells,
                len(self.scope.years),
                len(self.config.windows),
            ],
            "parquet_row_group_rows": [row_group],
        }
        estimates = {
            "gleam_native_time_by_cell_block": 12 * gleam_cells * dtype_bytes,
            "validation_cell_by_year_by_window": (
                validation_cells
                * len(self.scope.years)
                * len(self.config.windows)
                * dtype_bytes
            ),
            "parquet_row_group_per_numeric_column": row_group * dtype_bytes,
        }

        def path_bytes(path: Path) -> int:
            if path.is_file():
                return int(path.stat().st_size)
            if path.is_dir():
                return sum(
                    int(item.stat().st_size)
                    for item in path.rglob("*")
                    if item.is_file()
                )
            return 0

        return {
            "stage": stage,
            "configured_block_chunk_parameters": configured,
            "configured_block_chunk_shapes": shapes,
            "estimated_block_bytes": estimates,
            "estimation_note": (
                "Configured dimensional products; process RSS is measured separately."
            ),
            "artifact_bytes": {
                name: path_bytes(path)
                for name, path in sorted((artifacts or {}).items())
            },
            "stage_outcome_extra": {} if outcome is None else outcome.extra,
        }

    def _run_one_impl(
        self,
        stage: str,
        resource_start: Mapping[str, Any],
    ) -> dict[str, Any]:
        self.active_stage_partials[stage] = None
        handler = self.handlers.get(stage)
        if handler is None:
            error = StageUnavailableError(
                f"No handler is registered for stage {stage}"
            )
            _annotate_failure_phase(error, "STAGE_SETUP")
            raise error
        try:
            input_hashes = self._input_hashes(stage)
            session, resumed_partial = self._start_or_resume_partial(
                stage, input_hashes=input_hashes
            )
        except BaseException as exc:
            _annotate_failure_phase(exc, "STAGE_SETUP")
            raise
        if session.skipped:
            verified_marker: dict[str, Any] | None = None
            try:
                self._verify_completed_stage(stage, session.marker or {})
                verified_marker = dict(session.marker or {})
                self.authoritative_stage_markers[stage] = verified_marker
                return {
                    "stage": stage,
                    "status": "SKIPPED_SUCCESS_MARKER",
                    "marker": verified_marker,
                }
            except BaseException as exc:
                if verified_marker is not None:
                    _annotate_failure_phase(exc, "STAGE_POST_VERIFY")
                    try:
                        setattr(exc, "stage_execution_status", "COMPLETED")
                        setattr(exc, "published_stage_marker", verified_marker)
                    except (AttributeError, TypeError):
                        pass
                elif not isinstance(exc, Exception):
                    # start_stage already parsed and signature-checked this
                    # immutable marker; a control-flow signal during the deeper
                    # artifact verification must not turn the existing success
                    # into a failed stage attempt.
                    _annotate_failure_phase(exc, "STAGE_RESUME_VERIFY")
                    existing_marker = dict(session.marker or {})
                    self.authoritative_stage_markers[stage] = existing_marker
                    try:
                        setattr(exc, "stage_execution_status", "COMPLETED")
                        setattr(
                            exc,
                            "published_stage_marker",
                            existing_marker,
                        )
                        setattr(exc, "resume_verification_completed", False)
                    except (AttributeError, TypeError):
                        pass
                else:
                    _annotate_failure_phase(exc, "STAGE_RESUME_VERIFY")
                raise
        self.active_stage_partials[stage] = session.work_dir
        prior_attempt_resources = self._prior_attempt_resources(session.work_dir)
        if any(
            bool(record.get("budget_exceeded", False))
            for record in prior_attempt_resources
        ):
            resources = self._aggregate_attempt_resources(
                self._stage_resources(resource_start), prior_attempt_resources
            )
            workload = self._resource_workload(stage)
            error = StageResourceBudgetError(
                f"Stage {stage} has a prior over-budget attempt in this run; "
                "resume cannot publish it. Use a new run-id after reducing memory."
            )
            error.resources = resources
            error.resource_workload = workload
            raise error
        request = StageRequest(self, session)
        outcome = self._recover_stage_outcome(session) if resumed_partial else None
        recovered_stage_result = outcome is not None
        restarted_after_partial = False
        if (
            resumed_partial
            and outcome is None
            and stage not in PARTITION_RESUMABLE_STAGES
        ):
            _archive_incomplete(session.work_dir)
            session = start_stage(
                self.context,
                stage,
                parameters=self.stage_parameters(stage),
                resume=self.resume,
            )
            _write_json_new(
                session.work_dir / STAGE_START,
                self._stage_start_payload(stage, input_hashes=input_hashes),
            )
            self.active_stage_partials[stage] = session.work_dir
            request = StageRequest(self, session)
            resumed_partial = False
            restarted_after_partial = True
        if outcome is None:
            try:
                outcome = handler(request)
            except BaseException as exc:
                _annotate_failure_phase(exc, "STAGE_HANDLER")
                raise
        if not isinstance(outcome, StageOutcome):
            raise TypeError(f"Stage handler {stage} must return StageOutcome")
        artifact_paths: dict[str, Path] = {}
        output_hashes: dict[str, str] = {}
        relative_artifacts: dict[str, Path] = {}
        for name, raw_path in sorted(outcome.artifacts.items()):
            path = ensure_within_run(raw_path, self.context.run_dir)
            if not path.exists():
                raise FileNotFoundError(f"Stage artifact does not exist: {path}")
            try:
                relative = path.relative_to(session.work_dir)
            except ValueError as exc:
                raise StageValidationError(
                    f"Stage artifact is outside its partial directory: {path}"
                ) from exc
            artifact_paths[name] = path
            relative_artifacts[name] = relative
            output_hashes[name] = sha256_path(path)
        resources = self._aggregate_attempt_resources(
            self._stage_resources(resource_start), prior_attempt_resources
        )
        workload = self._resource_workload(
            stage,
            outcome=outcome,
            artifacts=artifact_paths,
        )
        stage_result_path = session.work_dir / "_STAGE_RESULT.json"
        if not recovered_stage_result:
            _write_json_new(
                stage_result_path,
                {
                    "schema_version": 2,
                    "stage": stage,
                    "source_tree_sha256": self.context.source_tree_sha256,
                    "environment_sha256": self.context.environment_sha256,
                    "artifacts": {
                        name: str(
                            (session.target_dir / relative).relative_to(
                                self.context.run_dir
                            )
                        )
                        for name, relative in relative_artifacts.items()
                    },
                    "artifact_hashes": output_hashes,
                    "row_counts": outcome.row_counts,
                    "extra": outcome.extra,
                    "resources": resources,
                    "resource_workload": workload,
                },
            )
        output_hashes["_stage_result"] = sha256_file(stage_result_path)
        if resources["budget_exceeded"]:
            error = StageResourceBudgetError(
                f"Stage {stage} process lifetime peak working set "
                f"{resources['process_lifetime_peak_working_set_bytes']} exceeds "
                f"{resources['peak_rss_budget_bytes']} bytes for {self.scope.mode}"
            )
            error.resources = resources
            error.resource_workload = workload
            raise error
        marker: dict[str, Any] | None = None
        try:
            marker = complete_stage(
                session,
                input_hashes=input_hashes,
                output_hashes=output_hashes,
                row_counts=outcome.row_counts,
                extra={
                    **outcome.extra,
                    "resources": resources,
                    "resource_workload": workload,
                    "resumed_partial": resumed_partial,
                    "recovered_stage_result": recovered_stage_result,
                    "restarted_after_preserved_partial": restarted_after_partial,
                    "artifacts": {
                        name: str(Path("stages") / stage / relative)
                        for name, relative in relative_artifacts.items()
                    },
                },
                resources=resources,
                resource_workload=workload,
            )
            self.active_stage_partials[stage] = None
            self.authoritative_stage_markers[stage] = marker
            final_artifacts = {
                name: self.context.stages_dir / stage / relative
                for name, relative in relative_artifacts.items()
            }
            return {
                "stage": stage,
                "status": "COMPLETED",
                "marker": marker,
                "artifacts": {
                    name: str(path) for name, path in final_artifacts.items()
                },
            }
        except BaseException as exc:
            published_marker = (
                marker
                if marker is not None
                else (
                    getattr(exc, "published_stage_marker", None)
                    or self._published_marker_after_interruption(
                        session,
                        stage=stage,
                        input_hashes=input_hashes,
                        output_hashes=output_hashes,
                    )
                )
            )
            if published_marker is not None:
                self.active_stage_partials[stage] = None
                self.authoritative_stage_markers[stage] = dict(published_marker)
                _annotate_failure_phase(exc, "STAGE_POST_PUBLISH")
                try:
                    setattr(exc, "stage_execution_status", "COMPLETED")
                    setattr(exc, "published_stage_marker", published_marker)
                except (AttributeError, TypeError):
                    pass
            raise

    def _published_marker_after_interruption(
        self,
        session: StageSession,
        *,
        stage: str,
        input_hashes: Mapping[str, str],
        output_hashes: Mapping[str, str],
    ) -> dict[str, Any] | None:
        """Recognize a stage atomically published before a control-flow signal."""

        try:
            marker_path = session.target_dir / STAGE_SUCCESS
            if not session.target_dir.is_dir() or not marker_path.is_file():
                return None
            marker = json.loads(marker_path.read_text(encoding="utf-8"))
            observed = (
                marker.get("stage"),
                marker.get("config_sha256"),
                marker.get("parameter_sha256"),
                marker.get("source_tree_sha256"),
                marker.get("environment_sha256"),
                marker.get("input_hashes"),
                marker.get("output_hashes"),
            )
            expected = (
                stage,
                self.config.sha256,
                session.parameter_sha256,
                self.context.source_tree_sha256,
                self.context.environment_sha256,
                dict(sorted(input_hashes.items())),
                dict(sorted(output_hashes.items())),
            )
            return marker if observed == expected else None
        except BaseException as diagnostic_error:
            self.diagnostic_issues.append(
                InvocationAuditIssue(
                    phase="stage post-publish marker verification",
                    error=diagnostic_error,
                )
            )
            return None

    def _record_failed_attempt(
        self,
        stage: str,
        exc: BaseException,
        *,
        resources: Mapping[str, Any],
        resource_workload: Mapping[str, Any],
    ) -> Path:
        """Persist one non-overwriting failure record globally and in its partial."""

        attempt_id = uuid.uuid4().hex
        candidates = sorted(
            self.context.stages_dir.glob(f".{stage}.*.partial"),
            key=lambda path: path.stat().st_mtime_ns,
        )
        active_partial = self.active_stage_partials.get(stage)
        if active_partial is not None and (
            not active_partial.is_dir()
            or active_partial.parent != self.context.stages_dir
            or active_partial not in candidates
        ):
            active_partial = None
        payload = {
            "schema_version": 1,
            "attempt_id": attempt_id,
            "stage": stage,
            "status": self.context.completion_scope_status,
            "scope_profile": self.context.scope_profile,
            "completion_scope_status": self.context.completion_scope_status,
            "failed_at_utc": utc_now(),
            "exception_type": (_exception_payload(exc) or {}).get(
                "type",
                "BaseException",
            ),
            "exception_message": (_exception_payload(exc) or {}).get(
                "message",
                "<exception message unavailable>",
            ),
            "exit_status": _initialization_exit_status(exc),
            "traceback": (_exception_payload(exc) or {}).get(
                "traceback",
                "<traceback unavailable>",
            ),
            "config_sha256": self.config.sha256,
            "template_config_sha256": (
                self.config.template_sha256 or self.config.sha256
            ),
            "effective_config_sha256": self.config.sha256,
            "effective_config": self.config.data,
            "resolved_paths": self.config.resolved_paths(),
            "source_tree_sha256": self.context.source_tree_sha256,
            "environment_sha256": self.context.environment_sha256,
            "parameters": {
                "run": self.context.parameters,
                "stage": self.stage_parameters(stage),
            },
            "partial_dir": (
                None
                if active_partial is None
                else active_partial.relative_to(self.context.run_dir).as_posix()
            ),
            "partial_candidates": [
                path.relative_to(self.context.run_dir).as_posix()
                for path in candidates
            ],
            "partial_mirror_selection": "current_stage_session_only",
            "resources": dict(resources),
            "resource_workload": dict(resource_workload),
        }
        attempts_dir = self.context.audit_dir / "attempts"
        audit_path = attempts_dir / f"{stage}.{attempt_id}.failed.json"
        try:
            _write_json_new(audit_path, payload)
        except BaseException as audit_error:
            raise StageAttemptAuditError(
                "stage attempt global audit",
                audit_error,
                published_audit_path=None,
            ) from audit_error
        if active_partial is not None:
            try:
                _write_json_new(
                    active_partial / f"_FAILED.{attempt_id}.json", payload
                )
            except BaseException as audit_error:
                raise StageAttemptAuditError(
                    "stage attempt partial mirror",
                    audit_error,
                    published_audit_path=audit_path,
                ) from audit_error
        return audit_path

    def run_one(self, stage: str) -> dict[str, Any]:
        resource_start: Mapping[str, Any] | None = None
        try:
            try:
                resource_start = process_memory_snapshot()
            except BaseException as exc:
                _annotate_failure_phase(exc, "STAGE_RESOURCE_START")
                raise
            result = self._run_one_impl(stage, resource_start)
        except BaseException as exc:
            exit_status = _normalize_incomplete_exit_status(exc)
            _annotate_failure_phase(exc, "STAGE_EXECUTION")
            published_marker = (
                getattr(exc, "published_stage_marker", None)
                or self.authoritative_stage_markers.get(stage)
            )
            if isinstance(published_marker, Mapping):
                resume_verification_completed = getattr(
                    exc,
                    "resume_verification_completed",
                    None,
                )
                published_record = {
                        "stage": stage,
                        "execution_status": "COMPLETED",
                        "failure_phase": getattr(
                            exc,
                            "failure_phase",
                            "STAGE_POST_PUBLISH",
                        ),
                        "invocation_interrupted_after_stage_publish": (
                            resume_verification_completed is None
                        ),
                        "resume_verification_completed": (
                            resume_verification_completed
                        ),
                        "exit_status": exit_status,
                        "exception": _exception_payload(exc),
                        "resources": dict(
                            published_marker.get("resources", {})
                        ),
                        "resource_workload": dict(
                            published_marker.get("resource_workload", {})
                        ),
                        "failure_audit": None,
                    }
                try:
                    self.quality_records.append(published_record)
                except BaseException as record_error:
                    self.audit_issues.append(
                        InvocationAuditIssue(
                            phase="stage quality record",
                            error=record_error,
                        )
                    )
                    _add_note_without_masking(
                        exc,
                        "Failed to preserve the completed stage quality record: "
                        f"{_safe_exception_description(record_error)}",
                    )
                raise
            resources = getattr(exc, "resources", None)
            if not resources:
                if resource_start is None:
                    resources = self._unavailable_stage_resources(exc)
                else:
                    try:
                        resources = self._stage_resources(resource_start)
                    except BaseException as diagnostic_error:
                        issue = InvocationAuditIssue(
                            phase="stage resource final sample",
                            error=diagnostic_error,
                        )
                        self.diagnostic_issues.append(issue)
                        _add_note_without_masking(
                            exc,
                            "Failed to finalize stage resource evidence while "
                            f"preserving {_safe_exception_description(exc)}; "
                            "diagnostic_error="
                            f"{_safe_exception_description(diagnostic_error)}"
                        )
                        resources = self._unavailable_stage_resources(
                            diagnostic_error,
                            start=resource_start,
                        )
            workload = getattr(exc, "resource_workload", None)
            if not workload:
                try:
                    workload = self._resource_workload(stage)
                except BaseException as diagnostic_error:
                    issue = InvocationAuditIssue(
                        phase="stage resource workload",
                        error=diagnostic_error,
                    )
                    self.diagnostic_issues.append(issue)
                    _add_note_without_masking(
                        exc,
                        "Failed to construct stage workload evidence while "
                        f"preserving {_safe_exception_description(exc)}; "
                        "diagnostic_error="
                        f"{_safe_exception_description(diagnostic_error)}"
                    )
                    workload = self._unavailable_resource_workload(
                        stage,
                        diagnostic_error,
                    )
            try:
                audit_path = self._record_failed_attempt(
                    stage,
                    exc,
                    resources=resources,
                    resource_workload=workload,
                )
            except BaseException as logging_error:
                if isinstance(logging_error, StageAttemptAuditError):
                    audit_path = logging_error.published_audit_path
                    root_error = logging_error.audit_error
                    issue_phase = logging_error.phase
                else:
                    audit_path = None
                    root_error = logging_error
                    issue_phase = "stage attempt audit"
                self.audit_issues.append(
                    InvocationAuditIssue(
                        phase=issue_phase,
                        error=root_error,
                        published_audit_path=audit_path,
                    )
                )
                _add_note_without_masking(
                    exc,
                    "Failed to persist complete structured attempt evidence: "
                    f"{_safe_exception_description(root_error)}"
                )
            failed_record = {
                    "stage": stage,
                    "execution_status": "FAILED",
                    "failure_phase": getattr(
                        exc,
                        "failure_phase",
                        "STAGE_EXECUTION",
                    ),
                    "exit_status": exit_status,
                    "exception": _exception_payload(exc),
                    "resources": resources,
                    "resource_workload": workload,
                    "failure_audit": None if audit_path is None else str(audit_path),
                }
            try:
                self.quality_records.append(failed_record)
            except BaseException as record_error:
                self.audit_issues.append(
                    InvocationAuditIssue(
                        phase="stage quality record",
                        error=record_error,
                        published_audit_path=audit_path,
                    )
                )
                _add_note_without_masking(
                    exc,
                    "Failed to preserve the failed stage quality record: "
                    f"{_safe_exception_description(record_error)}",
                )
            raise
        success_record: dict[str, Any] | None = None
        try:
            marker = result.get("marker") or {}
            success_record = {
                "stage": stage,
                "execution_status": result["status"],
                "resources": marker.get("resources", {}),
                "resource_workload": marker.get("resource_workload", {}),
            }
            self.quality_records.append(success_record)
            return result
        except BaseException as exc:
            phase = (
                "STAGE_POST_VERIFY"
                if result.get("status") == "SKIPPED_SUCCESS_MARKER"
                else "STAGE_POST_PUBLISH"
            )
            _annotate_failure_phase(exc, phase)
            if success_record is not None and success_record not in self.quality_records:
                try:
                    self.quality_records.append(success_record)
                except BaseException:
                    pass
            try:
                setattr(exc, "stage_execution_status", "COMPLETED")
                setattr(exc, "published_stage_marker", result.get("marker") or {})
            except (AttributeError, TypeError):
                pass
            raise

    def prepare_quality_summary(
        self,
        requested_stage: str,
        *,
        resume: bool,
    ) -> PreparedQualitySummary:
        """Freeze run-derived summary fields while the run lease is held."""

        target = (
            self.context.audit_dir
            / "quality_summaries"
            / f"run_quality_summary.{self.invocation_id}.json"
        )
        spei_audit_path = self.context.stages_dir / "spei" / "spei_2w_audit.json"
        spei_audit = (
            json.loads(spei_audit_path.read_text(encoding="utf-8"))
            if spei_audit_path.is_file()
            else {}
        )
        output_contract_path = (
            self.context.stages_dir / "export" / "bundle" / "output_contract.json"
        )
        output_contract = (
            json.loads(output_contract_path.read_text(encoding="utf-8"))
            if output_contract_path.is_file()
            else {}
        )
        output_2w = output_contract.get("spei_2w", {})
        payload = {
            "schema_version": 1,
            "invocation_id": self.invocation_id,
            "run_id": self.context.run_id,
            "requested_stage": requested_stage,
            "requested_scope": self.scope.as_parameters(),
            "resume": bool(resume),
            "status": self.context.completion_scope_status,
            "scope_profile": self.context.scope_profile,
            "completion_scope_status": self.context.completion_scope_status,
            "spei_2w_numeric_enabled": bool(
                self.config.data["scope"]["spei_2w_numeric"]
            ),
            "spei_2w_output_enabled": bool(
                self.config.data["scope"]["spei_2w_output"]
            ),
            "spei_2w_numeric_executed": bool(
                spei_audit.get("numeric_executed", False)
            ),
            "spei_2w_output_included": bool(
                output_2w.get("output_included", False)
            ),
            "compound_mode": str(
                self.config.data["scope"]["compound_mode"]
            ),
            "created_at_utc": utc_now(),
            "config_sha256": self.config.sha256,
            "template_config_sha256": (
                self.config.template_sha256 or self.config.sha256
            ),
            "effective_config_sha256": self.config.sha256,
            "resolved_paths": self.config.resolved_paths(),
            "parameter_sha256": self.context.parameter_sha256,
            "source_tree_sha256": self.context.source_tree_sha256,
            "environment_sha256": self.context.environment_sha256,
            "code_git_commit": self.context.code_git_commit,
            "stages": self.quality_records,
            "audit_issues": [issue.as_payload() for issue in self.audit_issues],
            "diagnostic_issues": [
                issue.as_payload() for issue in self.diagnostic_issues
            ],
            "run_state_frozen_while_lease_held": True,
            "capture_mode": "automatic_runtime",
            "retrospective": False,
        }
        return PreparedQualitySummary(
            target,
            self.context.run_dir,
            _snapshot_quality_payload(payload),
        )

    def run(self, requested_stage: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        stages = dependency_closure(requested_stage)
        try:
            for stage in stages:
                result = self.run_one(stage)
                results.append(result)
            self.completed_run_results = _snapshot_quality_payload(
                {"results": results}
            )["results"]
            self.requested_stage_execution_completed = True
            return results
        except BaseException as exc:
            if all(stage in self.authoritative_stage_markers for stage in stages):
                _annotate_failure_phase(exc, "INVOCATION_POST_STAGE")
                try:
                    setattr(exc, "stage_execution_status", "COMPLETED")
                    setattr(exc, "requested_stage_execution_completed", True)
                except (AttributeError, TypeError):
                    pass
            raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the 2010-2019 climate-stress grid panel without overwrite"
    )
    parser.add_argument("--config", required=True, help="Frozen YAML configuration")
    parser.add_argument("--stage", required=True, choices=CLI_STAGES)
    parser.add_argument("--run-id", help="Immutable run directory name")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--pilot-cells", type=int)
    parser.add_argument("--years", type=parse_years)
    parser.add_argument("--hash-mode", choices=("pilot", "full"))
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    handlers: Mapping[str, StageHandler] | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    output = stdout or sys.stdout
    errors = stderr or sys.stderr
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        config = load_config(args.config)
        scope = resolve_scope(
            config,
            pilot_cells=args.pilot_cells,
            years=args.years,
            hash_mode=args.hash_mode,
        )
        if args.resume and not args.run_id:
            raise ValueError("--resume requires an explicit --run-id")
        run_id = args.run_id or config.make_run_id(scope.mode)
        invocation_id = uuid.uuid4().hex
        invocation_started_at_utc = utc_now()
        # This timestamp is acquired before the lease so that the first
        # statement after lease acquisition is already inside the unified
        # BaseException boundary.
        initialization_started_at_utc = invocation_started_at_utc
        lease: RunLock | None = None
        context: RunContext | None = None
        pipeline: ClimateStressPipeline | None = None
        initialization_evidence: InitializationFailureEvidence | None = None
        prepared_summary: PreparedQualitySummary | None = None
        execution_error: BaseException | None = None
        release_error: BaseException | None = None
        failure_phase: str | None = None
        stage_execution_status = "NOT_STARTED"
        results: list[dict[str, Any]] = []

        try:
            with exclusive_run_lock(config.output_root, run_id) as active_lease:
                lease = active_lease
                try:
                    context = initialize_run(
                        config,
                        run_id=run_id,
                        parameters=scope.as_parameters(),
                        resume=args.resume,
                        repo_root=Path(__file__).resolve().parents[4],
                        invocation_id=invocation_id,
                    )
                except BaseException as exc:
                    _normalize_incomplete_exit_status(exc)
                    execution_error = exc
                    failure_phase = "INITIALIZE_RUN"
                    try:
                        initialization_evidence = (
                            _write_initialization_failure_records(
                                config,
                                scope,
                                run_id=run_id,
                                requested_stage=args.stage,
                                resume=args.resume,
                                invocation_id=invocation_id,
                                invocation_started_at_utc=invocation_started_at_utc,
                                initialization_started_at_utc=(
                                    initialization_started_at_utc
                                ),
                                lease=active_lease,
                                exc=exc,
                                exit_status=_initialization_exit_status(exc),
                            )
                        )
                    except BaseException as audit_error:
                        _report_audit_failure(
                            errors=errors,
                            original=exc,
                            phase="initialization failure record",
                            audit_error=audit_error,
                        )
                if execution_error is None:
                    try:
                        pipeline = ClimateStressPipeline(
                            config=config,
                            context=context,
                            scope=scope,
                            handlers={},
                            resume=args.resume,
                            invocation_id=invocation_id,
                        )
                        pipeline.handlers = (
                            handlers if handlers is not None else default_handlers()
                        )
                    except BaseException as exc:
                        _normalize_incomplete_exit_status(exc)
                        _annotate_failure_phase(exc, "STAGE_SETUP")
                        execution_error = exc
                        failure_phase = "STAGE_SETUP"

                if execution_error is None and pipeline is not None:
                    try:
                        results = pipeline.run(args.stage)
                        stage_execution_status = "COMPLETED"
                    except BaseException as exc:
                        _normalize_incomplete_exit_status(exc)
                        execution_error = exc
                        if pipeline.requested_stage_execution_completed:
                            results = list(pipeline.completed_run_results)
                            failure_phase = "INVOCATION_POST_STAGE"
                            stage_execution_status = "COMPLETED"
                        else:
                            failure_phase = str(
                                getattr(
                                    exc,
                                    "failure_phase",
                                    "STAGE_EXECUTION",
                                )
                            )
                            stage_execution_status = str(
                                getattr(
                                    exc,
                                    "stage_execution_status",
                                    "FAILED",
                                )
                            )

                # Freeze all run-derived fields under the lease. After release,
                # only terminal lease/exception fields are added before the
                # invocation-unique no-overwrite publication.
                try:
                    if initialization_evidence is not None:
                        prepared_summary = PreparedQualitySummary(
                            target=initialization_evidence.quality_path,
                            evidence_root=initialization_evidence.evidence_root,
                            payload=_snapshot_quality_payload(
                                {
                                    **initialization_evidence.quality_payload,
                                    "run_state_frozen_while_lease_held": True,
                                }
                            ),
                        )
                    elif pipeline is not None:
                        prepared_summary = pipeline.prepare_quality_summary(
                            args.stage,
                            resume=args.resume,
                        )
                    elif context is not None:
                        prepared_summary = _prepare_context_failure_summary(
                            config=config,
                            context=context,
                            scope=scope,
                            invocation_id=invocation_id,
                            requested_stage=args.stage,
                            resume=args.resume,
                            failure_phase=failure_phase or "STAGE_SETUP",
                            primary_exception=execution_error,
                            release_exception=None,
                            exit_status=(
                                2
                                if execution_error is None
                                else _initialization_exit_status(execution_error)
                            ),
                        )
                except BaseException as summary_prepare_error:
                    if execution_error is None:
                        _normalize_incomplete_exit_status(summary_prepare_error)
                        _annotate_failure_phase(
                            summary_prepare_error,
                            "QUALITY_SUMMARY_PREPARE",
                        )
                        execution_error = summary_prepare_error
                        failure_phase = "QUALITY_SUMMARY_PREPARE"
                    else:
                        _report_audit_failure(
                            errors=errors,
                            original=execution_error,
                            phase="run quality summary preparation",
                            audit_error=summary_prepare_error,
                        )
        except BaseException as lock_boundary_error:
            if lease is None:
                raise
            observed_release_error = lease.release_error
            if observed_release_error is None:
                # The body normally defers all failures until after release.
                # Preserve any unexpected boundary failure as the primary one.
                if execution_error is None:
                    _normalize_incomplete_exit_status(lock_boundary_error)
                    execution_error = lock_boundary_error
                    failure_phase = str(
                        getattr(
                            lock_boundary_error,
                            "failure_phase",
                            "INVOCATION_BOUNDARY",
                        )
                    )
                else:
                    _report_audit_failure(
                        errors=errors,
                        original=execution_error,
                        phase="invocation boundary",
                        audit_error=lock_boundary_error,
                    )
            else:
                release_error = observed_release_error
                if (
                    execution_error is None
                    and lock_boundary_error is not observed_release_error
                ):
                    _normalize_incomplete_exit_status(lock_boundary_error)
                    execution_error = lock_boundary_error
                    failure_phase = str(
                        getattr(
                            lock_boundary_error,
                            "failure_phase",
                            "INVOCATION_BOUNDARY",
                        )
                    )

        final_error = execution_error or release_error
        final_phase = (
            failure_phase
            if execution_error is not None
            else ("LEASE_RELEASE" if release_error is not None else None)
        )
        invocation_status = "FAILED" if final_error is not None else "COMPLETED"
        exit_status = (
            0 if final_error is None else _initialization_exit_status(final_error)
        )

        if pipeline is not None and execution_error is not None:
            for issue in pipeline.audit_issues:
                _report_audit_failure(
                    errors=errors,
                    original=execution_error,
                    phase=issue.phase,
                    audit_error=issue.error,
                )
            for issue in pipeline.diagnostic_issues:
                _emit_warning_without_masking(
                    errors,
                    (
                        "DIAGNOSTIC_WARNING: "
                        f"{issue.phase} failed while preserving "
                        f"{_safe_exception_description(execution_error)}; "
                        "diagnostic_error="
                        f"{_safe_exception_description(issue.error)}"
                    ),
                    original=execution_error,
                )
        if release_error is not None:
            _report_release_failure(
                errors=errors,
                primary=execution_error or release_error,
                release_error=release_error,
            )

        response_written = False
        if final_error is None:
            if (
                pipeline is None
                or context is None
                or lease is None
                or prepared_summary is None
            ):
                execution_error = RuntimeError(
                    "Invocation completed without initialized finalization state"
                )
                failure_phase = "INVOCATION_FINALIZE"
            else:
                response = {
                    "run_id": run_id,
                    "run_dir": str(context.run_dir),
                    "status": context.completion_scope_status,
                    "scope_profile": context.scope_profile,
                    "completion_scope_status": context.completion_scope_status,
                    "scope": scope.as_parameters(),
                    "requested_stage": args.stage,
                    "executed_stages": results,
                    "quality_summary": str(prepared_summary.target),
                    "quality_summary_state_at_response_write": "PENDING",
                    "quality_summary_finalized_on_process_exit": True,
                }
                try:
                    print(
                        json.dumps(
                            response,
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                        file=output,
                    )
                    output.flush()
                    response_written = True
                except BaseException as response_error:
                    _normalize_incomplete_exit_status(response_error)
                    _annotate_failure_phase(response_error, "RESPONSE_WRITE")
                    execution_error = response_error
                    failure_phase = "RESPONSE_WRITE"
                    _emit_warning_without_masking(
                        errors,
                        "AUDIT_WARNING: CLI response delivery failed; the final "
                        "quality summary will record invocation failure: "
                        f"{_safe_exception_description(response_error)}",
                        original=response_error,
                    )

        final_error = execution_error or release_error
        final_phase = (
            failure_phase
            if execution_error is not None
            else ("LEASE_RELEASE" if release_error is not None else None)
        )
        invocation_status = "FAILED" if final_error is not None else "COMPLETED"
        exit_status = (
            0 if final_error is None else _initialization_exit_status(final_error)
        )

        quality_summary: Path | None = None
        if prepared_summary is not None and lease is not None:
            try:
                quality_summary = _publish_quality_summary(
                    prepared_summary,
                    invocation_status=invocation_status,
                    stage_execution_status=stage_execution_status,
                    failure_phase=final_phase,
                    primary_exception=execution_error,
                    release_exception=release_error,
                    exit_status=exit_status,
                    lease=lease,
                    output_root=config.output_root.resolve(strict=False),
                )
            except BaseException as summary_error:
                _normalize_incomplete_exit_status(summary_error)
                preserved = final_error or summary_error
                _report_audit_failure(
                    errors=errors,
                    original=preserved,
                    phase=(
                        "completed run quality summary"
                        if final_error is None
                        else "run quality summary"
                    ),
                    audit_error=summary_error,
                )
                if final_error is None:
                    execution_error = summary_error
                    final_error = summary_error
                    final_phase = "QUALITY_SUMMARY_WRITE"

        if final_error is not None:
            raise final_error

        if quality_summary is None:
            raise RuntimeError("Invocation completed without a quality summary")
        if not response_written:
            raise RuntimeError("Invocation completed without a CLI response")
        return 0
    except Exception as exc:
        message = _safe_exception_description(exc)
        try:
            print(message, file=errors)
        except BaseException as reporting_error:
            _add_note_without_masking(
                exc,
                "Failed to emit final CLI error output: "
                f"{_safe_exception_description(reporting_error)}",
            )
            fallback = sys.__stderr__
            if fallback is not None and fallback is not errors:
                try:
                    print(message, file=fallback)
                except BaseException:
                    pass
        return 2
