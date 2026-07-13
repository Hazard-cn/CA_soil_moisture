"""Collect, validate, and publish the reconstructed research-version lineage.

The committed registries contain metadata only. Raw Codex conversations, private
data, complete shell commands, and machine-specific absolute paths are never
written by this module.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
LINEAGE_DIR = ROOT / "quality_reports" / "lineage"
VERSION_REGISTRY = ROOT / "quality_reports" / "version_registry.csv"
DOC_VERSION_MAP = ROOT / "docs" / "VERSION_MAP.md"
DOC_VERSION_CHANGELOG = ROOT / "docs" / "VERSION_CHANGELOG.md"
DOC_DATA_LINEAGE = ROOT / "docs" / "DATA_LINEAGE.md"
DOC_GAPS = ROOT / "docs" / "PRE_GIT_RECONSTRUCTION_GAPS.md"
DOC_CONVERSATION_EVIDENCE = ROOT / "docs" / "CONVERSATION_EVIDENCE.md"
CUTOFF = date(2026, 7, 13)
RECONSTRUCTION_START = date(2026, 1, 1)
INITIAL_CONVERSATION_CANDIDATES = 124
FROZEN_SCALE_COUNTS = {
    "sample-g049": ("50844", "15737"),
    "sample-g057": ("50771", "15729"),
    "sample-g185": ("46299", "13236"),
    "sample-b067-g195": ("42187", "11775"),
}
FROZEN_SAMPLE_VERSIONS = {
    "sample-g049": "scale-g049",
    "sample-g057": "scale-g057",
    "sample-g185": "scale-g185",
    "sample-b067-g195": "scale-b067-g195",
}

SCHEMAS: dict[str, tuple[str, ...]] = {
    "version_registry.csv": (
        "canonical_id",
        "display_name",
        "namespace",
        "version_kind",
        "date_start",
        "date_updated",
        "first_evidence_date",
        "result_run_date",
        "interpretation_updated_at",
        "status",
        "current_truth_role",
        "lineage_confidence",
        "parent_id",
        "supersedes_ids",
        "context_ids",
        "main_change",
        "data_change",
        "method_change",
        "result_presentation_change",
        "current_use",
        "evidence_visibility",
        "public_evidence_paths",
        "notes",
    ),
    "version_aliases.csv": (
        "alias",
        "alias_scope",
        "canonical_id",
        "meaning",
        "collision_group",
        "notes",
    ),
    "artifact_registry.csv": (
        "artifact_id",
        "canonical_id",
        "role",
        "status",
        "path_uri",
        "storage_scope",
        "format",
        "size_bytes",
        "sha256",
        "row_count",
        "column_count",
        "schema_sha256",
        "builder_entrypoint",
        "observed_modified_at",
        "visibility",
        "git_policy",
        "lineage_confidence",
        "notes",
    ),
    "data_lineage.csv": (
        "edge_id",
        "input_artifact_id",
        "output_artifact_id",
        "transformation_id",
        "code_path",
        "join_keys",
        "join_type",
        "filter_expression",
        "outcome_redefinition",
        "verification_status",
        "notes",
    ),
    "sample_rules.csv": (
        "sample_rule_id",
        "base_artifact_id",
        "semantic_name",
        "predicate_json",
        "rule_vector",
        "row_count",
        "grid_count",
        "region_counts_json",
        "rule_code_path",
        "rule_code_sha256",
        "status",
        "supersedes",
        "verified_at",
    ),
    "method_registry.csv": (
        "method_id",
        "canonical_id",
        "outcome",
        "estimand",
        "mediator",
        "exposures",
        "controls",
        "fixed_effects",
        "inference",
        "bootstrap_method",
        "reps",
        "seed",
        "entrypoint",
        "claim_boundary",
    ),
    "analysis_runs.csv": (
        "analysis_run_id",
        "canonical_id",
        "input_artifact_ids",
        "sample_rule_id",
        "method_id",
        "entrypoint",
        "parameter_manifest",
        "environment_lock",
        "result_manifest",
        "public_result",
        "code_git_sha",
        "run_started_at",
        "run_completed_at",
        "reproducibility_status",
    ),
    "conversation_registry.csv": (
        "thread_id",
        "parent_thread_id",
        "source_type",
        "started_at",
        "ended_at",
        "scope_reason",
        "canonical_ids",
        "decision_summary",
        "evidence_level",
        "raw_committed",
    ),
    "change_events.csv": (
        "event_id",
        "thread_id",
        "event_time",
        "tool",
        "operation",
        "path_or_artifact_id",
        "command_sha256",
        "verification_status",
        "notes",
    ),
}

ID_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*$")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}$")
URI_PATTERN = re.compile(r"(?:repo|local|external)://[^\s]+$")
ABSOLUTE_PATH_PATTERN = re.compile(
    r"(?:(?<![A-Za-z])[A-Za-z]:[\\/]|/Users/|/home/)", re.IGNORECASE
)
INJECTED_PREFIXES = (
    "# AGENTS.md instructions",
    "<recommended_plugins>",
    "<environment_context>",
    "<permissions instructions>",
    "<app-context>",
    "<collaboration_mode>",
    "<skills_instructions>",
    "<apps_instructions>",
    "<plugins_instructions>",
)
CONFIDENCE_LEVELS = {
    "three-source-confirmed",
    "two-source-supported",
    "single-source-inferred",
    "missing-snapshot",
    "git-native",
}
VERSION_STATUSES = {
    "design_only",
    "current",
    "current_parallel",
    "current_data_base",
    "historical_latest",
    "historical",
    "superseded",
    "exploratory",
    "reviewed_sensitivity",
    "reference",
    "missing_snapshot",
    "umbrella",
}
SAMPLE_STATUSES = {"current", "reference", "historical"}
ARTIFACT_STATUSES = {"present", "missing", "virtual"}
ARTIFACT_STORAGE_SCOPES = {
    "derived-virtual",
    "external-local",
    "repository-ignored",
    "repository-tracked",
}
ARTIFACT_VISIBILITIES = {"local", "public"}
ARTIFACT_GIT_POLICIES = {"never-track", "track", "track-metadata-only"}
RUN_REPRODUCIBILITY_STATUSES = {
    "blocked_upstream_snapshot",
    "historical_static",
    "reconstructed_executable",
    "verified_current",
    "verified_sensitivity",
    "verified_superseded_interpretation",
}
CONVERSATION_SOURCE_TYPES = {"user", "subagent", "legacy-user"}
CONVERSATION_EVIDENCE_LEVELS = {
    "not-evidence",
    "single-source-inferred",
    "two-source-supported",
}
CHANGE_OPERATIONS = {
    "add-file",
    "analysis-run",
    "delete-observed",
    "file-write-command",
    "handoff-write",
    "manifest-write",
    "plan-write",
    "update-file",
}
CHANGE_VERIFICATION_STATUSES = {
    "failed-session",
    "historical-path-missing",
    "observed-unverified",
    "verified-current",
    "verified-session",
}
STRUCTURED_DATA_ROLES = {
    "analysis-panel",
    "data-base",
    "data-format-variant",
    "data-sidecar",
}
NAMESPACES = {"design", "report", "data", "analysis", "mechanism", "area", "scale", "g185"}


@dataclass
class Registry:
    name: str
    fields: tuple[str, ...]
    rows: list[dict[str, str]]


def split_ids(value: str) -> list[str]:
    return [item for item in re.split(r"[|;]", value) if item]


def unique_alias_map(aliases: Registry) -> tuple[dict[str, str], set[str]]:
    """Return only unambiguous aliases; keep collisions explicit for validation."""
    targets: dict[str, set[str]] = defaultdict(set)
    for row in aliases.rows:
        targets[row["alias"]].add(row["canonical_id"])
    ambiguous = {alias for alias, values in targets.items() if len(values) > 1}
    unique = {
        alias: next(iter(values))
        for alias, values in targets.items()
        if len(values) == 1
    }
    return unique, ambiguous


def timestamp_date(value: str) -> date | None:
    try:
        if len(value) <= 10:
            return date.fromisoformat(value)
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone(timedelta(hours=8)))
        return parsed.date()
    except (TypeError, ValueError):
        return None


def timestamp_in_window(value: str, start: date, before: date) -> bool:
    parsed = timestamp_date(value)
    return parsed is not None and start <= parsed < before


def index_samples_by_version(
    versions: Registry,
    artifacts: Registry,
    samples: Registry,
) -> dict[str, list[dict[str, str]]]:
    """Associate a sample rule with its data owner and, where applicable, scale ID."""
    version_ids = {row["canonical_id"] for row in versions.rows}
    artifact_owner = {
        row["artifact_id"]: row["canonical_id"] for row in artifacts.rows
    }
    indexed: dict[str, list[dict[str, str]]] = defaultdict(list)
    for sample in samples.rows:
        owners: set[str] = set()
        base_owner = artifact_owner.get(sample["base_artifact_id"])
        if base_owner in version_ids:
            owners.add(base_owner)

        sample_id = sample["sample_rule_id"]
        semantic = sample["semantic_name"].casefold()
        for version in versions.rows:
            version_id = version["canonical_id"]
            if version["namespace"] != "scale":
                continue
            scale_tokens = version_id.removeprefix("scale-").split("-")
            if any(
                sample_id == f"sample-{token}"
                or sample_id.startswith(f"sample-{token}-")
                or token in semantic
                for token in scale_tokens
                if token.startswith(("g", "b")) and token[1:].isdigit()
            ):
                owners.add(version_id)

        for owner in owners:
            indexed[owner].append(sample)
    return indexed


def csv_text(fields: Sequence[str], rows: Iterable[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def read_registry(path: Path, name: str | None = None) -> Registry:
    registry_name = name or path.name
    fields = SCHEMAS[registry_name]
    text = path.read_text(encoding="utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    actual = tuple(reader.fieldnames or ())
    if actual != fields:
        raise ValueError(f"{path}: schema mismatch: expected {fields}, got {actual}")
    rows = list(reader)
    for line_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"{path}:{line_number}: extra columns")
        for field, value in row.items():
            if value != value.strip():
                raise ValueError(f"{path}:{line_number}: whitespace in {field}")
    return Registry(registry_name, fields, rows)


def registry_paths() -> dict[str, Path]:
    return {
        "version_registry.csv": VERSION_REGISTRY,
        **{name: LINEAGE_DIR / name for name in SCHEMAS if name != "version_registry.csv"},
    }


def load_all() -> dict[str, Registry]:
    registries: dict[str, Registry] = {}
    for name, path in registry_paths().items():
        if not path.exists():
            raise ValueError(f"Missing registry: {path.relative_to(ROOT)}")
        registries[name] = read_registry(path, name)
    return registries


def require_unique(
    errors: list[str], registry: Registry, field: str, *, composite: Sequence[str] = ()
) -> set[str]:
    seen: set[str] = set()
    for line_number, row in enumerate(registry.rows, start=2):
        key = "|".join(row[item] for item in composite) if composite else row[field]
        if not key:
            errors.append(f"{registry.name}:{line_number}: missing {field}")
        elif key in seen:
            errors.append(f"{registry.name}:{line_number}: duplicate {key}")
        seen.add(key)
    return seen


def validate_uri(errors: list[str], name: str, line_number: int, field: str, value: str) -> None:
    if not value:
        return
    for item in split_ids(value):
        if not URI_PATTERN.fullmatch(item):
            errors.append(f"{name}:{line_number}: invalid URI in {field}: {item}")
        if ABSOLUTE_PATH_PATTERN.search(item):
            errors.append(f"{name}:{line_number}: absolute path in {field}")
        scheme, separator, payload = item.partition("://")
        normalized_payload = payload.replace("\\", "/")
        parts = PurePosixPath(normalized_payload).parts if payload else ()
        if (
            not separator
            or scheme not in {"repo", "local", "external"}
            or not payload
            or "\\" in payload
            or PurePosixPath(normalized_payload).is_absolute()
            or ".." in parts
            or any(character in payload for character in "\r\n\0")
        ):
            errors.append(f"{name}:{line_number}: unsafe URI path in {field}: {item}")


def resolve_local_uri(uri: str) -> Path | None:
    base: Path | None = None
    payload = ""
    if uri.startswith("repo://"):
        base = ROOT
        payload = uri.removeprefix("repo://")
    elif uri.startswith("local://"):
        base = ROOT
        payload = uri.removeprefix("local://")
    elif uri.startswith("external://CA_mechanism/"):
        base = ROOT.parent
        payload = uri.removeprefix("external://CA_mechanism/")
    if base is None or not payload or "\\" in payload:
        return None
    relative = PurePosixPath(payload)
    if relative.is_absolute() or ".." in relative.parts:
        return None
    try:
        resolved_base = base.resolve()
        candidate = (resolved_base / Path(*relative.parts)).resolve()
    except (OSError, RuntimeError):
        return None
    return candidate if candidate.is_relative_to(resolved_base) else None


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_structured_data_artifact(row: dict[str, str], path: Path) -> list[str]:
    """Verify dimensions, ordered-column schema, and grid-year uniqueness."""
    errors: list[str] = []
    artifact_id = row["artifact_id"]
    suffix = path.suffix.casefold()
    try:
        import pandas as pd

        if suffix == ".parquet":
            import pyarrow.parquet as pq

            parquet = pq.ParquetFile(path)
            row_count = parquet.metadata.num_rows
            columns = parquet.schema_arrow.names
            keys = (
                parquet.read(columns=["grid_id", "year"]).to_pandas()
                if {"grid_id", "year"}.issubset(columns)
                else None
            )
        elif suffix == ".dta":
            from pandas.io.stata import StataReader

            with StataReader(path) as reader:
                reader.read(nrows=1)
                row_count = int(reader._nobs)
                columns = list(reader._varlist)
            keys = (
                pd.read_stata(path, columns=["grid_id", "year"], convert_categoricals=False)
                if {"grid_id", "year"}.issubset(columns)
                else None
            )
        elif suffix == ".csv":
            with path.open("rb") as stream:
                header_bytes = stream.readline()
            header_text = ""
            csv_encoding = "utf-8-sig"
            for encoding in ("utf-8-sig", "gb18030"):
                try:
                    header_text = header_bytes.decode(encoding)
                    csv_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
            columns = next(csv.reader([header_text]))
            if not {"grid_id", "year"}.issubset(columns):
                return [f"{artifact_id}: structured CSV lacks grid_id/year"]
            key_parts = []
            decode_error: UnicodeDecodeError | None = None
            for encoding in (csv_encoding, "gb18030"):
                try:
                    chunks = pd.read_csv(
                        path,
                        usecols=["grid_id", "year"],
                        chunksize=100_000,
                        low_memory=False,
                        encoding=encoding,
                    )
                    key_parts = list(chunks)
                    decode_error = None
                    break
                except UnicodeDecodeError as exc:
                    decode_error = exc
            if decode_error is not None:
                raise decode_error
            keys = pd.concat(key_parts, ignore_index=True) if key_parts else pd.DataFrame()
            row_count = len(keys)
        else:
            return errors
    except (OSError, ValueError, KeyError, ImportError, StopIteration) as exc:
        return [f"{artifact_id}: cannot verify structured data: {exc}"]

    if str(row_count) != row["row_count"]:
        errors.append(
            f"{artifact_id}: row count drift; expected {row['row_count']}, got {row_count}"
        )
    if str(len(columns)) != row["column_count"]:
        errors.append(
            f"{artifact_id}: column count drift; expected {row['column_count']}, got {len(columns)}"
        )
    schema_sha256 = hashlib.sha256("\n".join(columns).encode("utf-8")).hexdigest()
    if schema_sha256 != row["schema_sha256"]:
        errors.append(f"{artifact_id}: ordered-column schema hash drift")
    if keys is None:
        errors.append(f"{artifact_id}: structured data lacks grid_id/year")
    elif keys[["grid_id", "year"]].isna().any(axis=None):
        errors.append(f"{artifact_id}: grid_id/year contains missing values")
    elif keys.duplicated(["grid_id", "year"]).any():
        errors.append(f"{artifact_id}: grid_id/year is not unique")
    return errors


def validate_registries(
    registries: dict[str, Registry],
    verify_local: bool = False,
    strict: bool = False,
) -> list[str]:
    errors: list[str] = []
    versions = registries["version_registry.csv"]
    aliases = registries["version_aliases.csv"]
    artifacts = registries["artifact_registry.csv"]
    edges = registries["data_lineage.csv"]
    samples = registries["sample_rules.csv"]
    methods = registries["method_registry.csv"]
    runs = registries["analysis_runs.csv"]
    conversations = registries["conversation_registry.csv"]
    changes = registries["change_events.csv"]
    alias_to_version, ambiguous_aliases = unique_alias_map(aliases)
    version_evidence_dates: dict[str, date] = {}
    for version in versions.rows:
        parsed = timestamp_date(version["first_evidence_date"])
        if parsed:
            version_evidence_dates[version["canonical_id"]] = parsed

    for registry in registries.values():
        for line_number, row in enumerate(registry.rows, start=2):
            if ABSOLUTE_PATH_PATTERN.search("|".join(row.values())):
                errors.append(f"{registry.name}:{line_number}: absolute path leaked")

    version_ids = require_unique(errors, versions, "canonical_id")
    artifact_ids = require_unique(errors, artifacts, "artifact_id")
    sample_ids = require_unique(errors, samples, "sample_rule_id")
    method_ids = require_unique(errors, methods, "method_id")
    run_ids = require_unique(errors, runs, "analysis_run_id")
    thread_ids = require_unique(errors, conversations, "thread_id")
    require_unique(errors, changes, "event_id")
    require_unique(errors, edges, "edge_id")
    require_unique(errors, aliases, "alias", composite=("alias_scope", "alias", "canonical_id"))

    for line_number, row in enumerate(versions.rows, start=2):
        canonical_id = row["canonical_id"]
        if not ID_PATTERN.fullmatch(canonical_id):
            errors.append(f"version_registry.csv:{line_number}: invalid canonical_id")
        if row["namespace"] not in NAMESPACES:
            errors.append(f"version_registry.csv:{line_number}: invalid namespace {row['namespace']}")
        if row["status"] not in VERSION_STATUSES:
            errors.append(f"version_registry.csv:{line_number}: invalid status {row['status']}")
        if row["lineage_confidence"] not in CONFIDENCE_LEVELS:
            errors.append(
                f"version_registry.csv:{line_number}: invalid confidence {row['lineage_confidence']}"
            )
        for field in ("data_change", "method_change", "result_presentation_change"):
            if not row[field]:
                errors.append(f"version_registry.csv:{line_number}: missing {field}")
        for field in ("date_start", "date_updated", "first_evidence_date", "result_run_date"):
            if not row[field]:
                continue
            try:
                date.fromisoformat(row[field])
            except ValueError:
                errors.append(f"version_registry.csv:{line_number}: invalid {field}")
        for field in ("parent_id", "supersedes_ids", "context_ids"):
            for reference in split_ids(row[field]):
                if reference not in version_ids:
                    errors.append(
                        f"version_registry.csv:{line_number}: unknown {field} {reference}"
                    )
        validate_uri(
            errors,
            "version_registry.csv",
            line_number,
            "public_evidence_paths",
            row["public_evidence_paths"],
        )

    for line_number, row in enumerate(aliases.rows, start=2):
        if row["canonical_id"] not in version_ids:
            errors.append(f"version_aliases.csv:{line_number}: unknown canonical_id")

    for line_number, row in enumerate(artifacts.rows, start=2):
        if row["canonical_id"] not in version_ids:
            errors.append(
                f"artifact_registry.csv:{line_number}: unknown canonical_id {row['canonical_id']}"
            )
        validate_uri(errors, "artifact_registry.csv", line_number, "path_uri", row["path_uri"])
        validate_uri(
            errors,
            "artifact_registry.csv",
            line_number,
            "builder_entrypoint",
            row["builder_entrypoint"],
        )
        if row["sha256"] and not SHA256_PATTERN.fullmatch(row["sha256"]):
            errors.append(f"artifact_registry.csv:{line_number}: invalid sha256")
        if row["schema_sha256"] and not SHA256_PATTERN.fullmatch(row["schema_sha256"]):
            errors.append(f"artifact_registry.csv:{line_number}: invalid schema_sha256")
        if row["lineage_confidence"] not in CONFIDENCE_LEVELS:
            errors.append(f"artifact_registry.csv:{line_number}: invalid lineage_confidence")
        if row["status"] not in ARTIFACT_STATUSES:
            errors.append(f"artifact_registry.csv:{line_number}: invalid status {row['status']}")
        if row["storage_scope"] not in ARTIFACT_STORAGE_SCOPES:
            errors.append(
                f"artifact_registry.csv:{line_number}: invalid storage_scope {row['storage_scope']}"
            )
        if row["visibility"] not in ARTIFACT_VISIBILITIES:
            errors.append(
                f"artifact_registry.csv:{line_number}: invalid visibility {row['visibility']}"
            )
        if row["git_policy"] not in ARTIFACT_GIT_POLICIES:
            errors.append(
                f"artifact_registry.csv:{line_number}: invalid git_policy {row['git_policy']}"
            )
        if row["status"] == "present" and not row["sha256"]:
            errors.append(f"artifact_registry.csv:{line_number}: present artifact lacks sha256")
        if row["status"] == "present" and row["role"] in {
            "analysis-panel",
            "data-base",
            "data-format-variant",
            "data-sidecar",
        } and not (row["row_count"] and row["column_count"] and row["schema_sha256"]):
            errors.append(
                f"artifact_registry.csv:{line_number}: present data artifact lacks dimensions/schema"
            )
        if row["status"] == "missing" and (row["sha256"] or row["size_bytes"]):
            errors.append(f"artifact_registry.csv:{line_number}: missing artifact has physical hash")
        if verify_local:
            path = resolve_local_uri(row["path_uri"])
            logical_series = "{" in row["path_uri"] and "}" in row["path_uri"]
            if row["status"] == "present" and path and not logical_series:
                if not path.exists() or not path.is_file():
                    errors.append(
                        f"artifact_registry.csv:{line_number}: missing present artifact"
                    )
                else:
                    if row["sha256"] and file_sha256(path) != row["sha256"]:
                        errors.append(
                            f"artifact_registry.csv:{line_number}: local sha256 drift"
                        )
                    if row["role"] in STRUCTURED_DATA_ROLES:
                        errors.extend(verify_structured_data_artifact(row, path))

    for line_number, row in enumerate(edges.rows, start=2):
        if row["input_artifact_id"] not in artifact_ids:
            errors.append(f"data_lineage.csv:{line_number}: unknown input artifact")
        if row["output_artifact_id"] not in artifact_ids:
            errors.append(f"data_lineage.csv:{line_number}: unknown output artifact")
        validate_uri(errors, "data_lineage.csv", line_number, "code_path", row["code_path"])
        if row["verification_status"] not in CONFIDENCE_LEVELS:
            errors.append(
                f"data_lineage.csv:{line_number}: invalid verification_status"
            )

    for line_number, row in enumerate(samples.rows, start=2):
        if row["base_artifact_id"] not in artifact_ids:
            errors.append(f"sample_rules.csv:{line_number}: unknown base artifact")
        if row["supersedes"] and row["supersedes"] not in sample_ids:
            errors.append(f"sample_rules.csv:{line_number}: unknown supersedes")
        try:
            json.loads(row["predicate_json"] or "{}")
            json.loads(row["region_counts_json"] or "{}")
        except json.JSONDecodeError:
            errors.append(f"sample_rules.csv:{line_number}: invalid JSON")
        validate_uri(errors, "sample_rules.csv", line_number, "rule_code_path", row["rule_code_path"])
        if row["rule_code_sha256"] and not SHA256_PATTERN.fullmatch(row["rule_code_sha256"]):
            errors.append(f"sample_rules.csv:{line_number}: invalid rule_code_sha256")
        if row["status"] not in SAMPLE_STATUSES:
            errors.append(f"sample_rules.csv:{line_number}: invalid status {row['status']}")
        if row["verified_at"]:
            try:
                date.fromisoformat(row["verified_at"])
            except ValueError:
                errors.append(f"sample_rules.csv:{line_number}: invalid verified_at")
        try:
            region_counts = json.loads(row["region_counts_json"] or "{}")
            if not isinstance(region_counts, dict):
                errors.append(f"sample_rules.csv:{line_number}: region_counts_json must be an object")
                region_counts = {}
            if region_counts and all(
                isinstance(value, dict) and "rows" in value
                for value in region_counts.values()
            ):
                region_rows = sum(int(value["rows"]) for value in region_counts.values())
                if row["row_count"] and region_rows != int(row["row_count"]):
                    errors.append(f"sample_rules.csv:{line_number}: region row counts do not sum")
            if region_counts and all(
                isinstance(value, dict) and "grids" in value
                for value in region_counts.values()
            ):
                region_grids = sum(int(value["grids"]) for value in region_counts.values())
                if row["grid_count"] and region_grids != int(row["grid_count"]):
                    errors.append(f"sample_rules.csv:{line_number}: region grid counts do not sum")
        except (AttributeError, TypeError, ValueError):
            errors.append(f"sample_rules.csv:{line_number}: invalid region count values")
        if verify_local and row["rule_code_sha256"]:
            path = resolve_local_uri(row["rule_code_path"])
            if path is None or not path.exists() or not path.is_file():
                errors.append(f"sample_rules.csv:{line_number}: rule code path missing")
            elif file_sha256(path) != row["rule_code_sha256"]:
                errors.append(f"sample_rules.csv:{line_number}: rule code sha256 drift")

    for line_number, row in enumerate(methods.rows, start=2):
        if row["canonical_id"] not in version_ids:
            errors.append(f"method_registry.csv:{line_number}: unknown canonical_id")
        validate_uri(errors, "method_registry.csv", line_number, "entrypoint", row["entrypoint"])
        for field in ("outcome", "estimand", "fixed_effects", "inference", "entrypoint", "claim_boundary"):
            if not row[field]:
                errors.append(f"method_registry.csv:{line_number}: missing {field}")

    for line_number, row in enumerate(runs.rows, start=2):
        if row["canonical_id"] not in version_ids:
            errors.append(f"analysis_runs.csv:{line_number}: unknown canonical_id")
        for artifact_id in split_ids(row["input_artifact_ids"]):
            if artifact_id not in artifact_ids:
                errors.append(
                    f"analysis_runs.csv:{line_number}: unknown input artifact {artifact_id}"
                )
        if row["sample_rule_id"] and row["sample_rule_id"] not in sample_ids:
            errors.append(f"analysis_runs.csv:{line_number}: unknown sample_rule_id")
        if row["method_id"] and row["method_id"] not in method_ids:
            errors.append(f"analysis_runs.csv:{line_number}: unknown method_id")
        for field in ("entrypoint", "parameter_manifest", "environment_lock", "result_manifest", "public_result"):
            validate_uri(errors, "analysis_runs.csv", line_number, field, row[field])
        if row["code_git_sha"] and not re.fullmatch(r"[0-9a-f]{40}", row["code_git_sha"]):
            errors.append(f"analysis_runs.csv:{line_number}: invalid code_git_sha")
        if row["run_completed_at"]:
            try:
                run_date = date.fromisoformat(row["run_completed_at"][:10])
                if run_date < CUTOFF and row["code_git_sha"]:
                    errors.append(f"analysis_runs.csv:{line_number}: pre-Git run has Git SHA")
            except ValueError:
                errors.append(f"analysis_runs.csv:{line_number}: invalid run_completed_at")
        if row["reproducibility_status"] not in RUN_REPRODUCIBILITY_STATUSES:
            errors.append(
                f"analysis_runs.csv:{line_number}: invalid reproducibility_status"
            )

    thread_windows: dict[str, tuple[date, date]] = {}
    conversation_limits = {
        "thread_id": 64,
        "parent_thread_id": 64,
        "source_type": 32,
        "started_at": 64,
        "ended_at": 64,
        "scope_reason": 512,
        "canonical_ids": 2048,
        "decision_summary": 2048,
        "evidence_level": 64,
        "raw_committed": 8,
    }
    for line_number, row in enumerate(conversations.rows, start=2):
        for field, limit in conversation_limits.items():
            if any(character in row[field] for character in "\r\n\0"):
                errors.append(
                    f"conversation_registry.csv:{line_number}: control character in {field}"
                )
            if len(row[field]) > limit:
                errors.append(
                    f"conversation_registry.csv:{line_number}: {field} exceeds {limit} characters"
                )
        if row["raw_committed"].casefold() != "false":
            errors.append(f"conversation_registry.csv:{line_number}: raw_committed must be false")
        if row["source_type"] not in CONVERSATION_SOURCE_TYPES:
            errors.append(f"conversation_registry.csv:{line_number}: invalid source_type")
        if row["evidence_level"] not in CONVERSATION_EVIDENCE_LEVELS:
            errors.append(f"conversation_registry.csv:{line_number}: invalid evidence_level")
        excluded = row["scope_reason"].startswith("excluded:")
        if excluded != (row["evidence_level"] == "not-evidence"):
            errors.append(
                f"conversation_registry.csv:{line_number}: disposition/evidence mismatch"
            )
        if excluded and row["canonical_ids"]:
            errors.append(
                f"conversation_registry.csv:{line_number}: excluded task must not map versions"
            )
        started_date = timestamp_date(row["started_at"])
        ended_date = timestamp_date(row["ended_at"])
        if started_date is None or ended_date is None:
            errors.append(f"conversation_registry.csv:{line_number}: invalid timestamp")
        elif not (
            RECONSTRUCTION_START <= started_date <= ended_date < CUTOFF
        ):
            errors.append(
                f"conversation_registry.csv:{line_number}: timestamp outside reconstruction window"
            )
        else:
            thread_windows[row["thread_id"]] = (started_date, ended_date)
        for canonical_id in split_ids(row["canonical_ids"]):
            if canonical_id in version_ids:
                resolved = canonical_id
            elif canonical_id in alias_to_version:
                errors.append(
                    f"conversation_registry.csv:{line_number}: use canonical ID instead of alias {canonical_id}"
                )
                resolved = alias_to_version[canonical_id]
            else:
                resolved = canonical_id
            if canonical_id in ambiguous_aliases:
                errors.append(
                    f"conversation_registry.csv:{line_number}: ambiguous alias {canonical_id}"
                )
                continue
            if resolved not in version_ids:
                errors.append(
                    f"conversation_registry.csv:{line_number}: unknown canonical_id {canonical_id}"
                )
            elif ended_date is not None and (
                evidence_date := version_evidence_dates.get(resolved)
            ) is not None and ended_date < evidence_date:
                errors.append(
                    f"conversation_registry.csv:{line_number}: temporal inversion for {resolved}"
                )
        if row["parent_thread_id"] and row["parent_thread_id"] not in thread_ids:
            errors.append(f"conversation_registry.csv:{line_number}: missing parent thread")
        if ABSOLUTE_PATH_PATTERN.search("|".join(row.values())):
            errors.append(f"conversation_registry.csv:{line_number}: absolute path leaked")

    change_limits = {
        "event_id": 64,
        "thread_id": 64,
        "event_time": 64,
        "tool": 128,
        "operation": 64,
        "path_or_artifact_id": 240,
        "command_sha256": 64,
        "verification_status": 64,
        "notes": 2048,
    }
    for line_number, row in enumerate(changes.rows, start=2):
        for field, limit in change_limits.items():
            if any(character in row[field] for character in "\r\n\0"):
                errors.append(f"change_events.csv:{line_number}: control character in {field}")
            if len(row[field]) > limit:
                errors.append(
                    f"change_events.csv:{line_number}: {field} exceeds {limit} characters"
                )
        if row["thread_id"] not in thread_ids:
            errors.append(f"change_events.csv:{line_number}: unknown thread_id")
        if row["command_sha256"] and not SHA256_PATTERN.fullmatch(row["command_sha256"]):
            errors.append(f"change_events.csv:{line_number}: invalid command_sha256")
        if row["operation"] not in CHANGE_OPERATIONS:
            errors.append(f"change_events.csv:{line_number}: invalid operation")
        if row["verification_status"] not in CHANGE_VERIFICATION_STATUSES:
            errors.append(f"change_events.csv:{line_number}: invalid verification_status")
        event_date = timestamp_date(row["event_time"])
        if event_date is None or not RECONSTRUCTION_START <= event_date < CUTOFF:
            errors.append(f"change_events.csv:{line_number}: event outside reconstruction window")
        elif row["thread_id"] in thread_windows:
            thread_start, thread_end = thread_windows[row["thread_id"]]
            if not thread_start <= event_date <= thread_end:
                errors.append(f"change_events.csv:{line_number}: event outside thread window")
        target = row["path_or_artifact_id"]
        if "://" in target:
            validate_uri(
                errors,
                "change_events.csv",
                line_number,
                "path_or_artifact_id",
                target,
            )
        else:
            normalized_target_path = target.replace("\\", "/")
            target_parts = PurePosixPath(normalized_target_path).parts
            if (
                not target
                or PurePosixPath(normalized_target_path).is_absolute()
                or ".." in target_parts
                or not re.fullmatch(r"[A-Za-z0-9_./*{}-]+", normalized_target_path)
            ):
                errors.append(f"change_events.csv:{line_number}: unsafe normalized target")
        if ABSOLUTE_PATH_PATTERN.search("|".join(row.values())):
            errors.append(f"change_events.csv:{line_number}: absolute path leaked")

    for sample_id, expected_counts in FROZEN_SCALE_COUNTS.items():
        if FROZEN_SAMPLE_VERSIONS[sample_id] not in version_ids:
            continue
        matches = [row for row in samples.rows if row["sample_rule_id"] == sample_id]
        if len(matches) != 1:
            errors.append(f"sample_rules.csv: expected exactly one {sample_id} row")
        elif (matches[0]["row_count"], matches[0]["grid_count"]) != expected_counts:
            errors.append(
                f"sample_rules.csv: {sample_id} count drift; create a new scale ID"
            )

    artifacts_by_version: dict[str, list[dict[str, str]]] = defaultdict(list)
    methods_by_version: dict[str, list[dict[str, str]]] = defaultdict(list)
    runs_by_version: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in artifacts.rows:
        artifacts_by_version[row["canonical_id"]].append(row)
    for row in methods.rows:
        methods_by_version[row["canonical_id"]].append(row)
    for row in runs.rows:
        runs_by_version[row["canonical_id"]].append(row)
    samples_by_version = index_samples_by_version(versions, artifacts, samples)
    result_manifest_paths = {
        row["path_uri"]
        for row in artifacts.rows
        if row["role"] == "result-manifest" and row["status"] == "present"
    }

    for row in versions.rows:
        version_id = row["canonical_id"]
        if row["namespace"] == "data" and row["version_kind"] in {
            "physical_data_snapshot",
            "missing_physical_snapshot",
        } and not artifacts_by_version[version_id]:
            errors.append(f"version_registry.csv: physical data node lacks artifact: {version_id}")
        if row["status"] == "current_data_base" and not (
            artifacts_by_version[version_id]
            or any(
                child["parent_id"] == version_id
                and artifacts_by_version[child["canonical_id"]]
                for child in versions.rows
            )
        ):
            errors.append(f"version_registry.csv: current data base lacks artifact family: {version_id}")
        if row["namespace"] == "scale" and row["version_kind"] in {
            "sample_rule",
            "sample_rule_alias_group",
        } and not samples_by_version[version_id]:
            errors.append(f"version_registry.csv: scale lacks registered sample rule: {version_id}")
        if row["status"] in {"current", "current_parallel"} and row["namespace"] not in {"data", "scale", "area"}:
            if not methods_by_version[version_id] or not runs_by_version[version_id]:
                errors.append(f"version_registry.csv: current analysis lacks method/run: {version_id}")
            elif not any(item["public_result"] for item in runs_by_version[version_id]):
                errors.append(f"version_registry.csv: current analysis lacks public result: {version_id}")

        if strict and row["status"] in {"current", "current_parallel", "current_data_base"}:
            complete_run = False
            for run in runs_by_version[version_id]:
                required = (
                    run["input_artifact_ids"],
                    run["sample_rule_id"],
                    run["method_id"],
                    run["entrypoint"],
                    run["result_manifest"],
                    run["environment_lock"],
                    run["public_result"],
                )
                public_result = run["public_result"]
                if (
                    all(required)
                    and run["result_manifest"] in result_manifest_paths
                    and public_result.startswith("repo://docs/results/")
                    and PurePosixPath(public_result.removeprefix("repo://")).suffix.casefold()
                    in {".md", ".html"}
                ):
                    complete_run = True
                    break
            if not complete_run:
                errors.append(
                    f"version_registry.csv: current node lacks complete run binding: {version_id}"
                )

    if strict:
        checked_repo_uris: set[str] = set()
        for registry in registries.values():
            for row in registry.rows:
                for value in row.values():
                    for item in split_ids(value):
                        if item in checked_repo_uris or not item.startswith("repo://"):
                            continue
                        if not URI_PATTERN.fullmatch(item):
                            continue
                        checked_repo_uris.add(item)
                        path = resolve_local_uri(item)
                        if path is None or not path.exists() or not path.is_file():
                            errors.append(f"strict: missing repo URI target {item}")

    if run_ids and not changes.rows:
        errors.append("change_events.csv: no modification events recorded")
    return errors


def markdown_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def generated_version_map(registries: dict[str, Registry]) -> str:
    rows = registries["version_registry.csv"].rows
    lines = [
        "---",
        "layout: default",
        "title: 2026 年版本地图",
        "---",
        "",
        "# 2026 年版本地图",
        "",
        "> 本页由 `scripts/python/version_lineage.py build-docs` 生成。Git 前版本是证据重建结果，不等同于可 checkout 的历史提交。",
        "",
    ]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["namespace"]].append(row)
    labels = {
        "design": "研究设计",
        "data": "数据",
        "report": "报告框架",
        "analysis": "分析",
        "mechanism": "机制",
        "area": "种植面积",
        "scale": "样本尺度",
        "g185": "G185 方法与结果",
    }
    for namespace in ("design", "data", "report", "analysis", "mechanism", "area", "scale", "g185"):
        if not grouped.get(namespace):
            continue
        lines.extend(
            [
                f"## {labels[namespace]}",
                "",
                "| Canonical ID | 日期 | 状态 | 当前角色 | 主要改变 | 当前用途 | 证据等级 |",
                "|---|---|---|---|---|---|---|",
            ]
        )
        for row in sorted(grouped[namespace], key=lambda item: (item["date_start"], item["canonical_id"])):
            lines.append(
                "| "
                + " | ".join(
                    markdown_escape(item)
                    for item in (
                        row["canonical_id"],
                        row["date_start"] or row["first_evidence_date"],
                        row["status"],
                        row["current_truth_role"],
                        row["main_change"],
                        row["current_use"],
                        row["lineage_confidence"],
                    )
                )
                + " |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def mermaid_id(value: str) -> str:
    return "n_" + re.sub(r"[^a-zA-Z0-9_]", "_", value)


def generated_version_changelog(registries: dict[str, Registry]) -> str:
    """Build a detailed, version-by-version account of data, method, and presentation changes."""
    versions = registries["version_registry.csv"].rows
    artifacts: dict[str, list[dict[str, str]]] = defaultdict(list)
    methods: dict[str, list[dict[str, str]]] = defaultdict(list)
    runs: dict[str, list[dict[str, str]]] = defaultdict(list)
    conversations: dict[str, int] = defaultdict(int)
    children: dict[str, list[dict[str, str]]] = defaultdict(list)
    alias_to_version, _ = unique_alias_map(registries["version_aliases.csv"])
    for row in registries["artifact_registry.csv"].rows:
        artifacts[row["canonical_id"]].append(row)
    for row in registries["method_registry.csv"].rows:
        methods[row["canonical_id"]].append(row)
    for row in registries["analysis_runs.csv"].rows:
        runs[row["canonical_id"]].append(row)
    associated_samples = index_samples_by_version(
        registries["version_registry.csv"],
        registries["artifact_registry.csv"],
        registries["sample_rules.csv"],
    )
    sample_by_id = {
        row["sample_rule_id"]: row for row in registries["sample_rules.csv"].rows
    }
    used_samples: dict[str, list[dict[str, str]]] = defaultdict(list)
    for run_rows in runs.values():
        for run in run_rows:
            sample = sample_by_id.get(run["sample_rule_id"])
            if sample and sample not in used_samples[run["canonical_id"]]:
                used_samples[run["canonical_id"]].append(sample)
    for row in registries["conversation_registry.csv"].rows:
        if row["scope_reason"].startswith("excluded:") or row["evidence_level"] == "not-evidence":
            continue
        for canonical_id in split_ids(row["canonical_ids"]):
            conversations[alias_to_version.get(canonical_id, canonical_id)] += 1
    for version in versions:
        if version["parent_id"]:
            children[version["parent_id"]].append(version)

    lines = [
        "---",
        "layout: default",
        "title: 2026 年逐版本变化详表",
        "---",
        "",
        "# 2026 年逐版本变化详表",
        "",
        "> 本页由 `scripts/python/version_lineage.py build-docs` 生成。每个版本分别说明数据、方法和结果呈现变化；Git 前版本是证据重建，不代表存在可 checkout 的同期提交。",
        "> `sample_rules.csv` 的行数、grid 数和区域计数均指规则 mask 的原始支持；回归运行还可能因模型变量缺失形成更小的 complete-case 样本，两者不得混用。",
        "",
    ]
    ordered = sorted(
        versions,
        key=lambda row: (row["date_start"] or row["first_evidence_date"], row["canonical_id"]),
    )
    for row in ordered:
        canonical_id = row["canonical_id"]
        lines.extend(
            [
                f"## `{canonical_id}` — {row['display_name']}",
                "",
                "| 项目 | 内容 |",
                "|---|---|",
                f"| 时间与状态 | {markdown_escape(row['date_start'] or row['first_evidence_date'])}；`{markdown_escape(row['status'])}`；`{markdown_escape(row['version_kind'])}` |",
                f"| 父版/取代关系 | parent=`{markdown_escape(row['parent_id'] or 'none')}`；supersedes=`{markdown_escape(row['supersedes_ids'] or 'none')}` |",
                f"| 当前用途 | {markdown_escape(row['current_use'])}；truth role=`{markdown_escape(row['current_truth_role'] or 'none')}` |",
                f"| 证据 | `{markdown_escape(row['lineage_confidence'])}`；关联脱敏对话 {conversations.get(canonical_id, 0)} 个 |",
                "",
                "### 数据变化",
                "",
                row["data_change"],
                "",
            ]
        )
        if artifacts.get(canonical_id):
            lines.extend(
                [
                    "关联 artifact：",
                    "",
                    "| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |",
                    "|---|---|---|---|---|",
                ]
            )
            for artifact in artifacts[canonical_id]:
                size = "×".join(filter(None, (artifact["row_count"], artifact["column_count"]))) or "未记录"
                lines.append(
                    f"| `{markdown_escape(artifact['artifact_id'])}` | {markdown_escape(artifact['role'])} | "
                    f"{markdown_escape(artifact['status'])} | {markdown_escape(size)} | "
                    f"`{markdown_escape(artifact['path_uri'])}` |"
                )
            lines.append("")
        primary_samples = list(used_samples.get(canonical_id, []))
        if row["namespace"] == "scale":
            for sample in associated_samples.get(canonical_id, []):
                if sample not in primary_samples:
                    primary_samples.append(sample)
        downstream_samples = [
            sample
            for sample in associated_samples.get(canonical_id, [])
            if sample not in primary_samples
        ]
        for sample_group, heading in (
            (primary_samples, "本版本运行使用或定义的样本规则："),
            (downstream_samples, "基于本版本数据形成、由下游节点使用的派生规则："),
        ):
            if not sample_group:
                continue
            lines.extend([heading, ""])
            for sample in sample_group:
                counts = (
                    f"rows={sample['row_count'] or '未记录'}；"
                    f"grids={sample['grid_count'] or '未记录'}"
                )
                lines.extend(
                    [
                        f"#### `{sample['sample_rule_id']}` — {sample['semantic_name']}",
                        "",
                        f"- 谓词：`{sample['predicate_json']}`。",
                        f"- 规则向量：`{sample['rule_vector'] or '未冻结'}`。",
                        f"- 样本规模：{counts}；区域计数=`{sample['region_counts_json'] or '{}'}`。",
                        f"- 规则代码：`{sample['rule_code_path'] or '未记录'}`；代码 SHA-256=`{sample['rule_code_sha256'] or '未记录'}`。",
                        f"- 状态：`{sample['status']}`；verified_at=`{sample['verified_at'] or '未验证'}`；supersedes=`{sample['supersedes'] or 'none'}`。",
                        "",
                    ]
                )
        if children.get(canonical_id):
            lines.extend(
                [
                    "直接子版本或组件：",
                    "",
                    "| 子节点 | 日期 | 状态 | 相对变化摘要 |",
                    "|---|---|---|---|",
                ]
            )
            for child in sorted(
                children[canonical_id],
                key=lambda item: (item["date_start"] or item["first_evidence_date"], item["canonical_id"]),
            ):
                lines.append(
                    f"| `{child['canonical_id']}` | {child['date_start'] or child['first_evidence_date'] or '未定'} | "
                    f"`{child['status']}` | {markdown_escape(child['main_change'])} |"
                )
            lines.append("")
        lines.extend(["### 方法变化", "", row["method_change"], ""])
        if methods.get(canonical_id):
            for method in methods[canonical_id]:
                lines.extend(
                    [
                        f"#### `{method['method_id']}`",
                        "",
                        f"- Outcome / estimand：{method['outcome']}；{method['estimand']}。",
                        f"- Exposure / mediator：{method['exposures'] or '不适用'}；{method['mediator'] or '不适用'}。",
                        f"- Controls / FE：{method['controls'] or '未记录'}；{method['fixed_effects'] or '未记录'}。",
                        f"- Inference：{method['inference'] or '未记录'}；bootstrap={method['bootstrap_method'] or 'none'}；reps={method['reps'] or 'none'}；seed={method['seed'] or 'none'}。",
                        f"- 代码入口：`{method['entrypoint'] or '未记录'}`。",
                        f"- 解释边界：{method['claim_boundary']}。",
                        "",
                    ]
                )
        lines.extend(["### 结果呈现变化", "", row["result_presentation_change"], ""])
        if runs.get(canonical_id):
            lines.extend(
                [
                    "关联运行与结果载体：",
                    "",
                    "| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |",
                    "|---|---|---|---|---|---|---|---|",
                ]
            )
            for run in runs[canonical_id]:
                lines.append(
                    f"| `{markdown_escape(run['analysis_run_id'])}` | `{markdown_escape(run['input_artifact_ids'] or '未冻结')}` | "
                    f"`{markdown_escape(run['sample_rule_id'] or '未冻结')}` | "
                    f"`{markdown_escape(run['method_id'] or '未冻结')}` | "
                    f"`{markdown_escape(run['entrypoint'])}` | "
                    f"`{markdown_escape(run['result_manifest'] or '未冻结')}` | "
                    f"`{markdown_escape(run['public_result'] or '未公开')}` | "
                    f"{markdown_escape(run['reproducibility_status'])} |"
                )
            lines.append("")
        lines.extend(
            [
                "### 相对前版与证据边界",
                "",
                f"- 综合变化：{row['main_change']}",
                f"- 证据限制：{row['notes']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def generated_data_lineage(registries: dict[str, Registry]) -> str:
    artifacts = {row["artifact_id"]: row for row in registries["artifact_registry.csv"].rows}
    edges = registries["data_lineage.csv"].rows
    lines = [
        "---",
        "layout: default",
        "title: 2026 年数据谱系",
        "---",
        "",
        "# 2026 年数据谱系",
        "",
        "> 本页由 `scripts/python/version_lineage.py build-docs` 生成。图中的节点代表逻辑 artifact；数据本体不进入 Git。",
        "",
        "```mermaid",
        "flowchart LR",
    ]
    used = {row["input_artifact_id"] for row in edges} | {row["output_artifact_id"] for row in edges}
    for artifact_id in sorted(used):
        row = artifacts[artifact_id]
        label = f"{artifact_id}\\n{row['status']}"
        lines.append(f'  {mermaid_id(artifact_id)}["{label}"]')
    for row in edges:
        label = row["transformation_id"].replace('"', "'")
        lines.append(
            f"  {mermaid_id(row['input_artifact_id'])} -->|{label}| {mermaid_id(row['output_artifact_id'])}"
        )
    lines.extend(
        [
            "```",
            "",
            "## 转换登记",
            "",
            "| Edge | 输入 | 输出 | 代码 | 过滤或重定义 | 验证状态 |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in edges:
        change = "; ".join(filter(None, (row["filter_expression"], row["outcome_redefinition"])))
        lines.append(
            "| "
            + " | ".join(
                markdown_escape(item)
                for item in (
                    row["edge_id"],
                    row["input_artifact_id"],
                    row["output_artifact_id"],
                    row["code_path"],
                    change,
                    row["verification_status"],
                )
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def generated_gaps(registries: dict[str, Registry]) -> str:
    versions = registries["version_registry.csv"].rows
    artifacts = registries["artifact_registry.csv"].rows
    runs = registries["analysis_runs.csv"].rows
    lines = [
        "---",
        "layout: default",
        "title: Git 前版本重建缺口",
        "---",
        "",
        "# Git 前版本重建缺口",
        "",
        "> 本页由 `scripts/python/version_lineage.py build-docs` 生成。缺口被保留为可审计状态，不用当前文件替代历史快照。",
        "",
        "## 缺失或被覆盖的 artifact",
        "",
        "| Artifact | 状态 | 证据等级 | 说明 |",
        "|---|---|---|---|",
    ]
    gap_artifacts = [
        row
        for row in artifacts
        if row["status"] in {"missing", "historical-overwritten", "overwritten"}
        or row["lineage_confidence"] == "missing-snapshot"
    ]
    for row in gap_artifacts:
        lines.append(
            f"| {markdown_escape(row['artifact_id'])} | {markdown_escape(row['status'])} | "
            f"{markdown_escape(row['lineage_confidence'])} | {markdown_escape(row['notes'])} |"
        )
    if not gap_artifacts:
        lines.append("| - | - | - | 当前登记未发现缺失项 |")
    lines.extend(
        [
            "",
            "## 不能解释为同期可复现的运行",
            "",
            "| Run | 版本 | 状态 |",
            "|---|---|---|",
        ]
    )
    gap_runs = [
        row
        for row in runs
        if row["reproducibility_status"]
        not in {
            "verified",
            "current-verified",
            "git-native-verified",
            "verified_current",
            "verified_sensitivity",
        }
    ]
    for row in gap_runs:
        lines.append(
            f"| {markdown_escape(row['analysis_run_id'])} | {markdown_escape(row['canonical_id'])} | "
            f"{markdown_escape(row['reproducibility_status'])} |"
        )
    lines.extend(
        [
            "",
            "## 解释规则",
            "",
            "- 2026-07-13 以前没有 commit 级历史；文件时间只表示当前观察到的时间。",
            "- 历史报告使用的共享结果文件可能被后续运行覆盖，重新渲染不等于恢复原始报告。",
            "- `three-source-confirmed` 只表示至少三类证据一致，不表示历史环境和输入快照仍可完整复现。",
            "- response-surface 与 old-method 使用不同估计量、固定效应和函数形式，不能解释为相互验证。",
            "",
            "## 当前节点中的低置信度项",
            "",
        ]
    )
    for row in versions:
        if row["lineage_confidence"] in {"single-source-inferred", "missing-snapshot"}:
            lines.append(f"- `{row['canonical_id']}`：{row['notes']}")
    return "\n".join(lines).rstrip() + "\n"


def generated_conversation_evidence(registries: dict[str, Registry]) -> str:
    conversations = registries["conversation_registry.csv"].rows
    changes = registries["change_events.csv"].rows
    by_month: dict[str, int] = defaultdict(int)
    by_source: dict[str, int] = defaultdict(int)
    by_operation: dict[str, int] = defaultdict(int)
    included = sum(
        not row["scope_reason"].startswith("excluded:") for row in conversations
    )
    excluded = len(conversations) - included
    included_unmapped = sum(
        not row["scope_reason"].startswith("excluded:") and not row["canonical_ids"]
        for row in conversations
    )
    change_candidates = 0
    for row in conversations:
        by_month[row["started_at"][:7] or "unknown"] += 1
        by_source[row["source_type"] or "unknown"] += 1
    for row in changes:
        by_operation[row["operation"] or "unknown"] += 1
        match = re.search(r"(?:^|;) candidates=(\d+)(?:;|$)", row["notes"])
        if match:
            change_candidates += int(match.group(1))
    lines = [
        "---",
        "layout: default",
        "title: 2026 年对话与修改证据",
        "---",
        "",
        "# 2026 年对话与修改证据",
        "",
        "> 本页由 `scripts/python/version_lineage.py build-docs` 生成。只展示脱敏元数据、决策摘要和修改事件统计；原始对话与完整命令不进入仓库。",
        "",
        f"初筛发现 {INITIAL_CONVERSATION_CANDIDATES} 个项目相关记录；按 thread ID 去重并完成语义 disposition 后，正式登记 {len(conversations)} 个候选，其中纳入 {included} 个、排除 context-only {excluded} 个。",
        "",
        f"版本关联使用北京时间核对任务结束日期与版本 first_evidence_date；excluded 任务的 canonical_ids 为空，最终不存在早于版本首证据日期的关联。{included_unmapped} 个纳入任务因缺少足够的版本级交叉证据而保持未映射。",
        "",
        f"修改记录从 {change_candidates} 个候选操作聚合为 {len(changes)} 条代表事件，聚合键为 thread ID 与 operation；登记表保留代表路径、候选数、去重路径数和命令哈希，不保留完整命令。",
        "",
        "## 覆盖统计",
        "",
        "| 维度 | 值 | 数量 |",
        "|---|---|---:|",
    ]
    for key, value in sorted(by_month.items()):
        lines.append(f"| 月份 | {markdown_escape(key)} | {value} |")
    for key, value in sorted(by_source.items()):
        lines.append(f"| 来源 | {markdown_escape(key)} | {value} |")
    lines.append(f"| disposition | included | {included} |")
    lines.append(f"| disposition | excluded:context-only-reference | {excluded} |")
    for key, value in sorted(by_operation.items()):
        lines.append(f"| 修改事件 | {markdown_escape(key)} | {value} |")
    lines.extend(
        [
            "",
            "## 对话候选与 disposition",
            "",
            "| Thread ID | 开始时间 | 来源 | 范围判定 | 关联版本 | 决策摘要 | 证据等级 |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in sorted(conversations, key=lambda item: (item["started_at"], item["thread_id"])):
        lines.append(
            "| "
            + " | ".join(
                markdown_escape(item)
                for item in (
                    row["thread_id"],
                    row["started_at"],
                    row["source_type"],
                    row["scope_reason"],
                    row["canonical_ids"] or "未映射",
                    row["decision_summary"],
                    row["evidence_level"],
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## 修改事件的使用边界",
            "",
            "- `apply_patch` 或写入命令只能证明对话中发生过修改动作；只有与当前文件、日志、manifest 或结果相互核对后，才能提升为版本谱系证据。",
            "- `command_sha256` 用于在本机原始 session 中复核同一命令，不公开命令原文。",
            "- `path_or_artifact_id` 只使用规范化仓库 URI 或逻辑 artifact ID，不保存用户机器绝对路径。",
            "",
        ]
    )
    return "\n".join(lines)


def build_docs(registries: dict[str, Registry], check: bool) -> list[str]:
    outputs = {
        DOC_VERSION_MAP: generated_version_map(registries),
        DOC_VERSION_CHANGELOG: generated_version_changelog(registries),
        DOC_DATA_LINEAGE: generated_data_lineage(registries),
        DOC_GAPS: generated_gaps(registries),
        DOC_CONVERSATION_EVIDENCE: generated_conversation_evidence(registries),
    }
    drift: list[str] = []
    for path, content in outputs.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8-sig") != content:
                drift.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    return drift


def source_kind(source: object) -> tuple[str, str]:
    if source == "vscode" or source == "user":
        return "user", ""
    if isinstance(source, dict) and "subagent" in source:
        details = source["subagent"]
        if isinstance(details, dict) and "thread_spawn" in details:
            spawn = details["thread_spawn"]
            return "subagent", str(spawn.get("parent_thread_id", ""))
        return "subagent", ""
    return "legacy-user", ""


def actual_user_text(payload: dict[str, object]) -> str:
    if payload.get("type") != "message" or payload.get("role") != "user":
        return ""
    parts: list[str] = []
    for item in payload.get("content", []):
        if isinstance(item, dict) and item.get("type") in {"input_text", "text"}:
            parts.append(str(item.get("text", "")))
    text = "\n".join(parts).strip()
    if not text or text.startswith(INJECTED_PREFIXES):
        return ""
    return text


def classify_topic(text: str) -> tuple[str, str]:
    folded = text.casefold()
    rules = (
        (("g185", "response surface", "old method"), "g185-method-upgrade|g185-response-surface-v3|g185-old-method-corrected", "G185 方法、估计量或结果边界"),
        (("g057", "g049", "scale", "ggcp10"), "scale-search-region-first|scale-g057|scale-g185|scale-g049", "GGCP10 scale、区域证据或样本规则"),
        (("v6gleam", "v5drymed", "v4smstate", "v3med", "bpath"), "mechanism-v6gleambl|mechanism-v5drymed|mechanism-v4smstate", "土壤湿度机制分支与稳健性尝试"),
        (("data_v3", "data_v2", "data build", "phenowindow"), "data-v2|data-v3-expanded|analysis-v3", "数据构建、变量定义或 analysis-ready 面板"),
        (("complete_report", "联合胁迫", "compound", "sr×d×h"), "report-v4|report-v5|report-v6.1", "历史报告与联合胁迫框架"),
        (("git", "github", "版本", "version"), "", "版本谱系与 Git/GitHub 治理"),
    )
    for keywords, canonical_ids, summary in rules:
        if any(keyword in folded for keyword in keywords):
            return canonical_ids, summary
    return "", "项目相关任务或支持工作"


def normalized_repo_target(candidate: str) -> str | None:
    """Normalize one path token without retaining adjacent command or patch content."""
    value = candidate.strip().strip("'\"").replace("\\", "/")
    root_text = str(ROOT).replace("\\", "/")
    if value.casefold().startswith(root_text.casefold() + "/"):
        value = value[len(root_text) + 1 :]
    elif re.match(r"^[A-Za-z]:/", value) or value.startswith("/"):
        return None
    value = value.strip().rstrip(",;)")
    if (
        not value
        or len(value) > 240
        or any(character in value for character in "\r\n\0")
    ):
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        return None
    if not re.fullmatch(r"[A-Za-z0-9_.()/*{}+-]+", value) or " " in value:
        return None
    return "repo://" + path.as_posix()


def normalized_target(raw: str) -> str:
    for line in raw.splitlines():
        patch_header = re.match(
            r"^\*\*\* (?:Add|Update|Delete) File:\s*(.+?)\s*$", line
        )
        if patch_header:
            target = normalized_repo_target(patch_header.group(1))
            if target:
                return target

    folded = raw.replace("\\", "/")
    root_text = re.escape(str(ROOT).replace("\\", "/"))
    file_token = (
        r"[A-Za-z0-9_.()/+*-]+?\."
        r"(?:csv|do|dta|html|ini|json|md|parquet|ps1|py|r|rmd|tex|toml|txt|yaml|yml)"
    )
    relative_match = re.search(
        r"(?:\./)?(?P<path>(?:scripts|docs|quality_reports|data_build|data|output|temp)/"
        + file_token
        + r")(?=[\"'\r\n,;)]|\s|$)",
        folded,
        flags=re.IGNORECASE,
    )
    if relative_match:
        target = normalized_repo_target(relative_match.group("path"))
        if target:
            return target

    absolute_match = re.search(
        root_text + r"/(?P<path>" + file_token + r")(?=[\"'\r\n,;)]|\s|$)",
        folded,
        flags=re.IGNORECASE,
    )
    if absolute_match:
        target = normalized_repo_target(absolute_match.group("path"))
        if target:
            return target
    return "repo://unresolved-change-target"


def mutating_operation(name: str, raw: str) -> str | None:
    if name == "apply_patch":
        if re.search(r"(?m)^\*\*\* Add File:", raw):
            return "add-file"
        if re.search(r"(?m)^\*\*\* Delete File:", raw):
            return "delete-observed"
        return "update-file"
    folded = raw.casefold()
    markers = {
        "file-write-command": (
            "set-content",
            "out-file",
            "add-content",
            "write_text",
            "to_csv",
            "to_excel",
        ),
        "analysis-run": ("stata", "rscript", "python scripts/", "python .\\scripts\\"),
    }
    for operation, values in markers.items():
        if any(value in folded for value in values):
            return operation
    return None


def collect_conversations(
    sessions_root: Path,
    output_dir: Path,
    start: date,
    before: date,
) -> tuple[int, int]:
    project_cwd = str(ROOT).casefold()
    project_tokens = ("regression_sr", "ca_mechanism")
    threads: dict[str, dict[str, object]] = {}
    version_evidence: dict[str, date] = {}
    if VERSION_REGISTRY.exists():
        try:
            for version in read_registry(VERSION_REGISTRY, "version_registry.csv").rows:
                evidence_date = timestamp_date(version["first_evidence_date"])
                if evidence_date:
                    version_evidence[version["canonical_id"]] = evidence_date
        except (OSError, ValueError):
            version_evidence = {}

    for path in sessions_root.rglob("*.jsonl"):
        meta: dict[str, object] | None = None
        messages: list[str] = []
        calls: list[dict[str, str]] = []
        timestamps: list[str] = []
        tool_reference = False
        try:
            with path.open("r", encoding="utf-8") as stream:
                for line in stream:
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    stamp = str(item.get("timestamp", ""))
                    if item.get("type") == "session_meta":
                        meta = item.get("payload", {})
                        meta_stamp = str(meta.get("timestamp", ""))
                        if timestamp_in_window(meta_stamp, start, before):
                            timestamps.append(meta_stamp)
                        continue
                    if item.get("type") != "response_item":
                        continue
                    effective_stamp = stamp or str((meta or {}).get("timestamp", ""))
                    if not timestamp_in_window(effective_stamp, start, before):
                        continue
                    timestamps.append(effective_stamp)
                    payload = item.get("payload", {})
                    text = actual_user_text(payload)
                    if text:
                        messages.append(text)
                    if payload.get("type") not in {"function_call", "custom_tool_call"}:
                        continue
                    name = str(payload.get("name", ""))
                    raw = str(payload.get("arguments") or payload.get("input") or "")
                    if any(token in raw.casefold() for token in project_tokens):
                        tool_reference = True
                    operation = mutating_operation(name, raw)
                    if operation:
                        calls.append(
                            {
                                "call_id": str(payload.get("call_id", "")),
                                "tool": name,
                                "operation": operation,
                                "target": normalized_target(raw),
                                "sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
                                "time": effective_stamp,
                            }
                        )
        except OSError:
            continue
        if not meta:
            continue
        started = str(meta.get("timestamp", ""))
        if not timestamp_in_window(started, start, before):
            continue
        full_text = "\n".join(messages)
        normalized_cwd = str(meta.get("cwd", "")).replace("/", "\\").casefold()
        normalized_project = project_cwd.replace("/", "\\")
        exact_cwd = normalized_cwd == normalized_project
        subdir_cwd = normalized_cwd.startswith(normalized_project + "\\")
        content_hit = any(token in full_text.casefold() for token in project_tokens)
        if not exact_cwd and not subdir_cwd and not content_hit and not tool_reference:
            continue
        thread_id = str(meta.get("id", ""))
        if not thread_id:
            continue
        kind, parent = source_kind(meta.get("source") or meta.get("thread_source"))
        canonical_ids, summary = classify_topic(full_text)
        ended = max(timestamps, default=started)
        ended_date = timestamp_date(ended)
        classified_ids = split_ids(canonical_ids)
        screened_ids = (
            [
                canonical_id
                for canonical_id in classified_ids
                if canonical_id in version_evidence
                and ended_date is not None
                and version_evidence[canonical_id] <= ended_date
            ]
            if version_evidence
            else classified_ids
        )
        screened_count = len(classified_ids) - len(screened_ids)
        if screened_count:
            summary = (
                "与筛选后列示版本相关的项目任务或支持工作"
                if screened_ids
                else "项目支持或治理任务；未形成可按任务日期映射的版本节点"
            )
        candidate = {
            "thread_id": thread_id,
            "parent_thread_id": str(meta.get("parent_thread_id") or parent),
            "source_type": kind,
            "started_at": started,
            "ended_at": ended,
            "scope_reason": "disposition=relevant;"
            + (
                "exact-cwd"
                if exact_cwd
                else "subdir-cwd"
                if subdir_cwd
                else "content-reference"
                if content_hit
                else "tool-reference"
            )
            + (f";temporal-screened={screened_count}" if screened_count else ""),
            "canonical_ids": "|".join(screened_ids),
            "decision_summary": summary,
            "evidence_level": "single-source-inferred",
            "raw_committed": "false",
            "calls": calls,
        }
        previous = threads.get(thread_id)
        if previous is None or len(calls) > len(previous.get("calls", [])):
            threads[thread_id] = candidate

    # Keep subagent rows only when the parent is also part of the sanitized registry.
    included = set(threads)
    for row in threads.values():
        if row["parent_thread_id"] and row["parent_thread_id"] not in included:
            row["parent_thread_id"] = ""
            row["scope_reason"] += ";parent-outside-scope"

    conversation_rows = [
        {field: str(row[field]) for field in SCHEMAS["conversation_registry.csv"]}
        for row in sorted(threads.values(), key=lambda item: (str(item["started_at"]), str(item["thread_id"])))
    ]
    change_rows: list[dict[str, str]] = []
    seen_events: set[str] = set()
    for row in threads.values():
        for call in row["calls"]:
            event_id = hashlib.sha256(
                f"{row['thread_id']}|{call['call_id']}|{call['sha256']}".encode("utf-8")
            ).hexdigest()[:24]
            if event_id in seen_events:
                continue
            seen_events.add(event_id)
            change_rows.append(
                {
                    "event_id": event_id,
                    "thread_id": str(row["thread_id"]),
                    "event_time": call["time"] or str(row["started_at"]),
                    "tool": call["tool"],
                    "operation": call["operation"],
                    "path_or_artifact_id": call["target"],
                    "command_sha256": call["sha256"],
                    "verification_status": "observed-unverified",
                    "notes": "仅保存命令哈希和规范化目标；原始命令未提交",
                }
            )
    change_rows.sort(key=lambda item: (item["event_time"], item["event_id"]))
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "conversation_registry.csv").write_text(
        csv_text(SCHEMAS["conversation_registry.csv"], conversation_rows),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "change_events.csv").write_text(
        csv_text(SCHEMAS["change_events.csv"], change_rows), encoding="utf-8", newline="\n"
    )
    return len(conversation_rows), len(change_rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect = subparsers.add_parser("collect-conversations")
    collect.add_argument("--sessions-root", type=Path, required=True)
    collect.add_argument("--output-dir", type=Path, required=True)
    collect.add_argument("--from-date", type=date.fromisoformat, default=date(2026, 1, 1))
    collect.add_argument("--before-date", type=date.fromisoformat, default=CUTOFF)

    build = subparsers.add_parser("build-docs")
    build.add_argument("--check", action="store_true")

    validate = subparsers.add_parser("validate")
    validate.add_argument("--strict", action="store_true")
    validate.add_argument("--verify-local", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "collect-conversations":
        count, events = collect_conversations(
            args.sessions_root, args.output_dir, args.from_date, args.before_date
        )
        print(f"Collected {count} sanitized conversations and {events} candidate change events")
        return 0
    try:
        registries = load_all()
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.command == "build-docs":
        drift = build_docs(registries, args.check)
        if drift:
            for path in drift:
                print(f"ERROR: generated document drift: {path}", file=sys.stderr)
            return 1
        print("Lineage documents are current" if args.check else "Generated lineage documents")
        return 0
    errors = validate_registries(
        registries,
        verify_local=args.verify_local,
        strict=args.strict or args.verify_local,
    )
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    print(
        f"Validated {sum(len(item.rows) for item in registries.values())} registry rows; "
        f"errors={len(errors)}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
