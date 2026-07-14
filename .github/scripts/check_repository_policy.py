"""Fail when a Git snapshot violates the public repository policy."""

from __future__ import annotations

import argparse
import ast
import csv
import io
import re
import subprocess
import sys
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
MAX_FILE_BYTES = 20 * 1024 * 1024

FORBIDDEN_PREFIXES = tuple(
    item.casefold()
    for item in (
        "data/",
        "data_build/data/",
        "data_build/output/",
        "temp/",
        "tmp/",
        "output/",
        "runs/",
        "archive/",
        "scratch/",
        "references/",
        "background_knowledge/",
        "reviews/",
        "CODEX/",
        "quality_reports/agent_runs/",
        "quality_reports/runs/",
        "quality_reports/archive/",
        "quality_reports/scratch/",
        "quality_reports/session_logs/",
    )
)

FORBIDDEN_SUFFIXES = {
    ".7z",
    ".aux",
    ".csv",
    ".db",
    ".dbf",
    ".docx",
    ".dta",
    ".feather",
    ".fst",
    ".geojson",
    ".gpkg",
    ".grd",
    ".gz",
    ".h5",
    ".hdf",
    ".hdf4",
    ".hdf5",
    ".joblib",
    ".jpeg",
    ".jpg",
    ".json",
    ".jsonl",
    ".key",
    ".log",
    ".mat",
    ".nav",
    ".nc",
    ".nc4",
    ".ndjson",
    ".npy",
    ".npz",
    ".onnx",
    ".p12",
    ".parquet",
    ".pdf",
    ".pem",
    ".pfx",
    ".pickle",
    ".pkl",
    ".png",
    ".pptx",
    ".pt",
    ".pth",
    ".rda",
    ".rdata",
    ".rds",
    ".sas7bdat",
    ".sav",
    ".shp",
    ".shx",
    ".snm",
    ".sqlite",
    ".sqlite3",
    ".svg",
    ".tar",
    ".tgz",
    ".tif",
    ".tiff",
    ".toc",
    ".tsv",
    ".xls",
    ".xlsx",
    ".zip",
}

MACHINE_READABLE_SCHEMA_FILES = {
    # The portfolio design freezes exactly these three public JSON Schemas.
    # No other JSON file or path receives an exception to the repository policy.
    "docs/contracts/event_panel.schema.json",
    "docs/contracts/run_manifest.schema.json",
    "docs/contracts/threshold_grid.schema.json",
}

GOVERNANCE_REGISTRY_FILES = {
    "quality_reports/version_registry.csv",
    "quality_reports/lineage/analysis_runs.csv",
    "quality_reports/lineage/artifact_registry.csv",
    "quality_reports/lineage/change_events.csv",
    "quality_reports/lineage/conversation_registry.csv",
    "quality_reports/lineage/data_lineage.csv",
    "quality_reports/lineage/method_registry.csv",
    "quality_reports/lineage/sample_rules.csv",
    "quality_reports/lineage/version_aliases.csv",
}
ALLOWED_SPECIAL_FILES = GOVERNANCE_REGISTRY_FILES | MACHINE_READABLE_SCHEMA_FILES
RESULT_PREFIX = "docs/results/"
RESULT_SUFFIXES = {".md", ".html"}

LEGACY_MACHINE_PATH_FILES = {
    item.casefold()
    for item in (
        "AGENTS.md",
        "CLAUDE.md",
        "MEMORY.md",
        "quality_reports/handoffs/2026-06-21_g185_method_upgrade_report_handoff.md",
        "quality_reports/plans/2026-04-07_beamer_ppt_skill_install_plan.md",
        "quality_reports/plans/2026-06-18_story_empirical_review_match_plan.md",
        "quality_reports/plans/2026-06-18_zotero_story_direction_review.md",
        "scripts/env/g185_ml_env.ps1",
        "scripts/python/build_g185_method_upgrade_report.py",
        "scripts/python/export_mediation_to_feishu.py",
        "scripts/python/import_to_feishu_base.py",
        "scripts/python/replace_feishu_data_variable.py",
        "scripts/python/v3proxy_setAB_feishu_export.py",
        "scripts/python/zotero_story_direction_review.py",
    )
}

SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "Bearer token": re.compile(
        r"(?i)\bAuthorization\s*[:=]\s*[\"']?Bearer\s+[A-Za-z0-9._~+/-]{20,}"
    ),
}

MACHINE_PATH_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])(?:[A-Za-z]:[\\/][^\s\"'`<>|,;)\]}]+|"
    r"/(?:Users|home)/[^\s\"'`<>|,;)\]}]+)",
    flags=re.IGNORECASE,
)
RAW_TRANSCRIPT_PATTERN = re.compile(
    r"(?ms)^\s*\{[^\r\n]{0,4000}\"type\"\s*:\s*"
    r"\"(?:session_meta|response_item|turn_context|event_msg)\"[^\r\n]*\}\s*$"
)
RAW_TRANSCRIPT_IMPLEMENTATION_FILES = {
    ".github/scripts/check_repository_policy.py",
    "scripts/python/version_lineage.py",
    "tests/test_version_lineage.py",
}
HTML_RESOURCE_ATTRIBUTES = {
    "audio": {"src"},
    "base": {"href"},
    "embed": {"src"},
    "feimage": {"href", "xlink:href"},
    "iframe": {"src"},
    "image": {"href", "xlink:href"},
    "img": {"src", "srcset"},
    "input": {"src"},
    "link": {"href"},
    "object": {"data"},
    "script": {"src"},
    "source": {"src", "srcset"},
    "track": {"src"},
    "use": {"href", "xlink:href"},
    "video": {"poster", "src"},
}
CSS_RESOURCE_PATTERN = re.compile(r"(?is)url\(\s*[\"']?([^\"')]+)[\"']?\s*\)")
CSS_IMPORT_PATTERN = re.compile(
    r"(?is)@import\s+(?:url\(\s*)?[\"']?([^\"')\s;]+)[\"']?\s*\)?"
)

REGISTRY_FIELDS = (
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
)
REGISTRY_STATUSES = {
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
REGISTRY_NAMESPACES = {
    "design",
    "report",
    "data",
    "analysis",
    "mechanism",
    "area",
    "scale",
    "g185",
}


def git_bytes(*args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return result.stdout


def optional_git_blob(ref: str, relative: str) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"{ref}:{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    return result.stdout if result.returncode == 0 else None


def baseline_main_ref() -> str | None:
    for candidate in ("origin/main", "main"):
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", candidate],
            cwd=ROOT,
            check=False,
            capture_output=True,
        )
        if result.returncode == 0:
            return candidate
    return None


def tracked_files(source: str) -> list[str]:
    if source == "index":
        output = git_bytes("ls-files", "-z")
    else:
        output = git_bytes("ls-tree", "-r", "-z", "--name-only", source)
    return [item.decode("utf-8") for item in output.split(b"\0") if item]


def blob_bytes(source: str, relative: str) -> bytes:
    object_name = f":{relative}" if source == "index" else f"{source}:{relative}"
    return git_bytes("show", object_name)


def sensitive_filename(normalized: str) -> bool:
    basename = PurePosixPath(normalized).name.casefold()
    if basename == ".env.example":
        return False
    if basename == ".env" or basename.startswith(".env."):
        return True
    if basename in {".git-credentials", ".netrc", ".npmrc", ".pypirc"}:
        return True
    if basename.startswith(("id_rsa", "id_dsa", "id_ecdsa", "id_ed25519")):
        return True
    return bool(
        re.fullmatch(
            r"(?:credentials?|service[-_]?account)[^/]*[.]json",
            basename,
            flags=re.IGNORECASE,
        )
    )


def inline_resource(value: str) -> bool:
    normalized = value.strip().casefold()
    return normalized.startswith(("data:", "#"))


def inline_srcset(value: str) -> bool:
    return bool(
        re.fullmatch(
            r"(?:data:[^\s]+|#[^\s,]+)(?:\s+\d+(?:[.]\d+)?[wx])?",
            value.strip(),
            flags=re.IGNORECASE,
        )
    )


class SelfContainedHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.assets: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        resource_attributes = HTML_RESOURCE_ATTRIBUTES.get(tag.casefold(), set())
        for name, value in attrs:
            if value is None or name.casefold() not in resource_attributes:
                continue
            if name.casefold() == "srcset":
                if not inline_srcset(value):
                    self.assets.append(value.strip())
            elif not inline_resource(value):
                self.assets.append(value.strip())


def external_html_assets(text: str) -> list[str]:
    parser = SelfContainedHTMLParser()
    parser.feed(text)
    parser.close()
    assets = parser.assets
    for pattern in (CSS_RESOURCE_PATTERN, CSS_IMPORT_PATTERN):
        for match in pattern.finditer(text):
            value = match.group(1).strip()
            if not inline_resource(value):
                assets.append(value)
    return assets


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        default="index",
        help="Git snapshot to inspect: index, HEAD, or an explicit commit SHA/ref.",
    )
    return parser.parse_args()


def validate_version_registry(text: str) -> list[str]:
    errors: list[str] = []
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if tuple(reader.fieldnames or ()) != REGISTRY_FIELDS:
        return ["Version registry fields do not match the required schema"]

    rows = list(reader)
    ids: set[str] = set()
    for line_number, row in enumerate(rows, start=2):
        if None in row:
            errors.append(f"Version registry row {line_number} has extra columns")
            continue
        canonical_id = row["canonical_id"]
        if not re.fullmatch(r"[a-z0-9]+(?:[.-][a-z0-9]+)*", canonical_id):
            errors.append(f"Invalid canonical_id on registry row {line_number}: {canonical_id}")
        if canonical_id in ids:
            errors.append(f"Duplicate canonical_id on registry row {line_number}: {canonical_id}")
        ids.add(canonical_id)

        for field, value in row.items():
            if value != value.strip():
                errors.append(
                    f"Leading or trailing whitespace in registry row {line_number}, field {field}"
                )
        for field in (
            "canonical_id",
            "display_name",
            "namespace",
            "version_kind",
            "first_evidence_date",
            "status",
            "lineage_confidence",
            "main_change",
            "data_change",
            "method_change",
            "result_presentation_change",
            "current_use",
            "evidence_visibility",
            "notes",
        ):
            if not row[field]:
                errors.append(f"Missing {field} on registry row {line_number}")
        if row["namespace"] not in REGISTRY_NAMESPACES:
            errors.append(f"Invalid namespace on registry row {line_number}: {row['namespace']}")
        if row["status"] not in REGISTRY_STATUSES:
            errors.append(f"Invalid status on registry row {line_number}: {row['status']}")
        if row["lineage_confidence"] not in {
            "three-source-confirmed",
            "two-source-supported",
            "single-source-inferred",
            "missing-snapshot",
            "git-native",
        }:
            errors.append(
                f"Invalid lineage_confidence on registry row {line_number}: "
                f"{row['lineage_confidence']}"
            )
        if row["evidence_visibility"] not in {"public", "local", "mixed"}:
            errors.append(
                f"Invalid evidence_visibility on registry row {line_number}: "
                f"{row['evidence_visibility']}"
            )
        parsed_dates: dict[str, date] = {}
        for field in (
            "date_start",
            "date_updated",
            "first_evidence_date",
            "result_run_date",
            "interpretation_updated_at",
        ):
            if not row[field]:
                continue
            try:
                parsed_dates[field] = date.fromisoformat(row[field])
            except ValueError:
                errors.append(
                    f"Invalid ISO date on registry row {line_number}, field {field}: {row[field]}"
                )
        if (
            "date_start" in parsed_dates
            and "date_updated" in parsed_dates
            and parsed_dates["date_updated"] < parsed_dates["date_start"]
        ):
            errors.append(f"date_updated precedes date_start on registry row {line_number}")

    for line_number, row in enumerate(rows, start=2):
        for field in ("parent_id", "supersedes_ids", "context_ids"):
            for reference in filter(None, row[field].split("|")):
                if reference not in ids:
                    errors.append(
                        f"Unknown {field} reference on registry row {line_number}: {reference}"
                    )
                if field == "parent_id" and reference == row["canonical_id"]:
                    errors.append(f"Self parent on registry row {line_number}: {reference}")
    if not rows:
        errors.append("Version registry has no data rows")
    return errors


def validate_lineage_snapshot(texts: dict[str, str]) -> list[str]:
    """Run the canonical cross-registry validator against the selected Git snapshot."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        from scripts.python import version_lineage as lineage
    except (ImportError, OSError) as exc:
        return [f"Cannot load lineage validator: {exc}"]

    registries: dict[str, lineage.Registry] = {}
    errors: list[str] = []
    for name, fields in lineage.SCHEMAS.items():
        relative = (
            "quality_reports/version_registry.csv"
            if name == "version_registry.csv"
            else f"quality_reports/lineage/{name}"
        )
        text = texts.get(relative.casefold())
        if text is None:
            errors.append(f"Missing governance registry: {relative}")
            continue
        reader = csv.DictReader(io.StringIO(text, newline=""))
        actual = tuple(reader.fieldnames or ())
        if actual != fields:
            errors.append(
                f"Governance registry schema mismatch for {relative}: expected {fields}, got {actual}"
            )
            continue
        rows = list(reader)
        for line_number, row in enumerate(rows, start=2):
            if None in row:
                errors.append(f"Governance registry has extra columns: {relative}:{line_number}")
                continue
            for field, value in row.items():
                if value != value.strip():
                    errors.append(
                        f"Governance registry has surrounding whitespace: "
                        f"{relative}:{line_number}:{field}"
                    )
        registries[name] = lineage.Registry(name, fields, rows)

    if errors:
        return errors
    return [f"Lineage: {error}" for error in lineage.validate_registries(registries)]


def validate_snapshot_repo_uris(
    texts: dict[str, str], tracked: set[str]
) -> list[str]:
    """Require every exact repo:// registry target to exist in the same Git tree."""
    errors: list[str] = []
    registry_paths = set(GOVERNANCE_REGISTRY_FILES)
    for relative in sorted(registry_paths):
        text = texts.get(relative.casefold())
        if text is None:
            continue
        reader = csv.DictReader(io.StringIO(text, newline=""))
        for line_number, row in enumerate(reader, start=2):
            for field, value in row.items():
                if not value:
                    continue
                for item in filter(None, re.split(r"[|;]", value)):
                    if not re.fullmatch(r"repo://[^\s]+", item):
                        continue
                    target = item.removeprefix("repo://").casefold()
                    if target not in tracked:
                        errors.append(
                            f"Missing repo URI target in snapshot: "
                            f"{relative}:{line_number}:{field}: {item}"
                        )
    return errors


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        files = tracked_files(args.source)
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: invalid Git source {args.source}: {exc}", file=sys.stderr)
        return 1
    python_count = 0
    texts: dict[str, str] = {}
    baseline_ref = baseline_main_ref()
    legacy_machine_path_files: list[str] = []

    # Fail closed if a future edit silently expands the JSON exception beyond
    # the three frozen machine-readable contracts above.
    json_exceptions = {
        path for path in ALLOWED_SPECIAL_FILES if PurePosixPath(path).suffix.casefold() == ".json"
    }
    if json_exceptions != MACHINE_READABLE_SCHEMA_FILES:
        errors.append(
            "Policy configuration error: JSON exceptions must equal the three frozen contracts"
        )

    for relative in files:
        normalized = relative.replace("\\", "/")
        folded = normalized.casefold()
        suffix = PurePosixPath(normalized).suffix.casefold()

        if sensitive_filename(normalized):
            errors.append(f"Sensitive filename is tracked: {normalized}")
        elif folded in ALLOWED_SPECIAL_FILES:
            pass
        elif folded.startswith(FORBIDDEN_PREFIXES):
            errors.append(f"Forbidden tracked path: {normalized}")
        elif any(folded.endswith(item) for item in FORBIDDEN_SUFFIXES):
            errors.append(f"Forbidden tracked file type: {normalized}")

        if folded.startswith(RESULT_PREFIX):
            if suffix not in RESULT_SUFFIXES:
                errors.append(f"Published result must be Markdown or HTML: {normalized}")
        elif suffix == ".html":
            errors.append(f"HTML is only allowed under {RESULT_PREFIX}: {normalized}")

        raw = blob_bytes(args.source, relative)
        if len(raw) > MAX_FILE_BYTES:
            errors.append(f"Tracked file exceeds 20 MiB: {normalized}")
            continue
        if raw.startswith(b"version https://git-lfs.github.com/spec/v1"):
            errors.append(f"Git LFS pointer is not allowed: {normalized}")
            continue
        if b"\0" in raw:
            errors.append(f"Unexpected binary content: {normalized}")
            continue
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            errors.append(f"Tracked text is not strict UTF-8: {normalized}: {exc}")
            continue
        texts[folded] = text

        if suffix == ".py":
            python_count += 1
            try:
                ast.parse(text, filename=normalized)
            except SyntaxError as exc:
                errors.append(f"Python parse failure: {normalized}: {exc}")

        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"Possible {label} in {normalized}")

        if (
            folded not in RAW_TRANSCRIPT_IMPLEMENTATION_FILES
            and RAW_TRANSCRIPT_PATTERN.search(text)
        ):
            errors.append(f"Possible raw conversation/session record in {normalized}")

        if folded.startswith(RESULT_PREFIX) and suffix == ".html":
            for asset in external_html_assets(text):
                errors.append(f"HTML is not self-contained ({asset}) in {normalized}")

        machine_paths = Counter(MACHINE_PATH_PATTERN.findall(text))
        if machine_paths:
            baseline_paths: Counter[str] = Counter()
            if baseline_ref:
                baseline_raw = optional_git_blob(baseline_ref, relative)
                if baseline_raw is not None:
                    try:
                        baseline_text = baseline_raw.decode("utf-8-sig")
                    except UnicodeDecodeError:
                        baseline_text = ""
                    baseline_paths = Counter(MACHINE_PATH_PATTERN.findall(baseline_text))
            new_paths = machine_paths - baseline_paths
            if new_paths:
                errors.append(f"New machine-specific absolute path in {normalized}")
            elif folded in LEGACY_MACHINE_PATH_FILES or baseline_paths:
                legacy_machine_path_files.append(normalized)
            else:
                errors.append(f"Machine-specific absolute path in {normalized}")

    registry_text = texts.get("quality_reports/version_registry.csv")
    if registry_text is None:
        errors.append("Missing quality_reports/version_registry.csv")
    else:
        errors.extend(validate_version_registry(registry_text))
    errors.extend(validate_lineage_snapshot(texts))
    errors.extend(validate_snapshot_repo_uris(texts, {item.casefold() for item in files}))

    if legacy_machine_path_files:
        warnings.append(
            f"{len(legacy_machine_path_files)} tracked files retain unchanged legacy "
            "machine-specific paths; no new absolute path was added"
        )

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    print(
        f"Checked {len(files)} files from {args.source} and parsed {python_count} Python files; "
        f"warnings={len(warnings)}, errors={len(errors)}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
