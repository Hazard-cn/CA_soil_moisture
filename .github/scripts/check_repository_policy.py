"""Fail when a Git snapshot violates the public repository policy."""

from __future__ import annotations

import argparse
import ast
import csv
import io
import re
import subprocess
import sys
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

ALLOWED_SPECIAL_FILES = {"quality_reports/version_registry.csv"}
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

MACHINE_PATH_PATTERN = re.compile(r"[A-Za-z]:[\\/]Users[\\/]", flags=re.IGNORECASE)
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
    "date_start",
    "date_updated",
    "first_evidence_date",
    "status",
    "confidence",
    "parent_id",
    "context_ids",
    "data_base_ids",
    "input_variant",
    "main_change",
    "current_use",
    "evidence_visibility",
    "evidence_paths",
    "notes",
)
REGISTRY_STATUSES = {
    "current",
    "current_parallel",
    "current_data_base",
    "historical_latest",
    "historical",
    "superseded",
    "exploratory",
    "reviewed_sensitivity",
    "reference",
}
REGISTRY_NAMESPACES = {"report", "data", "analysis", "mechanism", "area", "scale", "g185"}


def git_bytes(*args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return result.stdout


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
        choices=("index", "HEAD"),
        default="index",
        help="Git snapshot to inspect; pre-commit uses index and CI uses HEAD.",
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
            "first_evidence_date",
            "status",
            "confidence",
            "main_change",
            "current_use",
            "evidence_visibility",
            "evidence_paths",
            "notes",
        ):
            if not row[field]:
                errors.append(f"Missing {field} on registry row {line_number}")
        if row["namespace"] not in REGISTRY_NAMESPACES:
            errors.append(f"Invalid namespace on registry row {line_number}: {row['namespace']}")
        if row["status"] not in REGISTRY_STATUSES:
            errors.append(f"Invalid status on registry row {line_number}: {row['status']}")
        if row["confidence"] not in {"confirmed", "mixed", "inferred"}:
            errors.append(f"Invalid confidence on registry row {line_number}: {row['confidence']}")
        if row["evidence_visibility"] not in {"public", "local", "mixed"}:
            errors.append(
                f"Invalid evidence_visibility on registry row {line_number}: "
                f"{row['evidence_visibility']}"
            )
        parsed_dates: dict[str, date] = {}
        for field in ("date_start", "date_updated", "first_evidence_date"):
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
        for field in ("parent_id", "context_ids", "data_base_ids"):
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


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    files = tracked_files(args.source)
    python_count = 0
    texts: dict[str, str] = {}

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

        if folded.startswith(RESULT_PREFIX) and suffix == ".html":
            for asset in external_html_assets(text):
                errors.append(f"HTML is not self-contained ({asset}) in {normalized}")

        if MACHINE_PATH_PATTERN.search(text):
            if folded in LEGACY_MACHINE_PATH_FILES:
                warnings.append(f"Legacy machine-specific user path in {normalized}")
            else:
                errors.append(f"New machine-specific user path in {normalized}")

    registry_text = texts.get("quality_reports/version_registry.csv")
    if registry_text is None:
        errors.append("Missing quality_reports/version_registry.csv")
    else:
        errors.extend(validate_version_registry(registry_text))

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
