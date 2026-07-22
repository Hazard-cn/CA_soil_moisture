"""Safely fetch and validate frozen daily GLEAM 4.3a soil-moisture inputs.

The official logical remote is fixed in code.  Downloads are retained under a
unique attempt name, validated before publication, and then create-only hard
linked into the year directory.  Existing files are never replaced or deleted.
Every non-dry invocation writes a unique audit below ``GLEAM_ROOT/_meta``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from validate_gleam43a_year_input import LAYERS, sha256_file, validate_file


SUPPORTED_YEARS = (2020,)
OFFICIAL_REMOTE_ROOT = "gleam43a:data/v4.3a/daily"
OFFICIAL_SOURCE_URL = "https://www.gleam.eu/"
OFFICIAL_SFTP_HOST = "aether.ugent.be"
OFFICIAL_SFTP_PORT = 2225
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _token(moment: datetime | None = None) -> str:
    value = moment or _utc_now()
    return value.strftime("%Y%m%dT%H%M%S.%fZ")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def _git_head() -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(REPOSITORY_ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def _validate_external_path(path: Path, *, label: str) -> Path:
    resolved = path.expanduser().resolve(strict=False)
    if not resolved.is_absolute():
        raise ValueError(f"{label} must be absolute: {path}")
    if resolved.parent == resolved:
        raise ValueError(f"{label} may not be a filesystem root: {resolved}")
    home = Path.home().resolve()
    if resolved == home:
        raise ValueError(f"{label} may not be the user home directory: {resolved}")

    repository = REPOSITORY_ROOT.resolve()
    if (
        resolved == repository
        or repository in resolved.parents
        or resolved in repository.parents
    ):
        raise ValueError(f"{label} must remain outside the repository: {resolved}")
    for ancestor in (resolved, *resolved.parents):
        if (ancestor / ".git").exists():
            raise ValueError(
                f"{label} may not be inside any Git repository/worktree: {resolved}"
            )
    return resolved


def resolve_gleam_root(argument: str | None) -> Path:
    raw = argument or os.environ.get("GLEAM_ROOT", "")
    if not raw.strip():
        raise ValueError("Provide --gleam-root or define non-empty GLEAM_ROOT")
    candidate = Path(raw)
    if not candidate.is_absolute():
        raise ValueError(f"GLEAM root must be absolute: {candidate}")
    return _validate_external_path(candidate, label="GLEAM root")


def _run_json(command: list[str], *, label: str) -> Any:
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"{label} failed with exit {completed.returncode}: "
            f"{completed.stderr.strip()}"
        )
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label} did not return valid JSON") from exc


def remote_object_path(layer: str, year: int) -> str:
    if layer not in LAYERS or year not in SUPPORTED_YEARS:
        raise ValueError(f"Unsupported GLEAM object: {layer} {year}")
    name = f"{layer}_{year}_GLEAM_v4.3a.nc"
    return f"{OFFICIAL_REMOTE_ROOT}/{year}/{name}"


def query_remote_listing(year: int) -> tuple[list[dict[str, Any]], str]:
    listing: list[dict[str, Any]] = []
    for layer in LAYERS:
        remote_path = remote_object_path(layer, year)
        item = _run_json(
            ["rclone", "lsjson", remote_path, "--stat", "--no-mimetype"],
            label=f"remote listing for {layer}",
        )
        expected_name = f"{layer}_{year}_GLEAM_v4.3a.nc"
        if item.get("IsDir") or item.get("Name") != expected_name:
            raise ValueError(f"Unexpected official remote object: {item!r}")
        if int(item.get("Size", 0)) <= 0 or not item.get("ModTime"):
            raise ValueError(f"Incomplete official remote metadata: {item!r}")
        listing.append(
            {
                "layer": layer,
                "logical_path": remote_path,
                "name": expected_name,
                "size_bytes": int(item["Size"]),
                "mtime": str(item["ModTime"]),
                "lsjson": item,
            }
        )
    listing.sort(key=lambda row: row["layer"])
    canonical = json.dumps(
        listing,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return listing, _sha256_bytes(canonical)


def remote_has_native_checksums() -> bool:
    features = _run_json(
        ["rclone", "backend", "features", "gleam43a:"],
        label="GLEAM remote feature query",
    )
    return bool(features.get("Hashes"))


def query_sanitized_remote_identity() -> dict[str, Any]:
    """Return only non-secret backend identity fields from rclone config."""

    completed = subprocess.run(
        ["rclone", "config", "show", "gleam43a"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError("Unable to inspect the configured GLEAM remote")
    allowed = {"type", "host", "port"}
    parsed: dict[str, str] = {}
    for raw_line in completed.stdout.splitlines():
        if "=" not in raw_line:
            continue
        key, value = (part.strip() for part in raw_line.split("=", 1))
        if key in allowed:
            parsed[key] = value
    expected = {
        "type": "sftp",
        "host": OFFICIAL_SFTP_HOST,
        "port": str(OFFICIAL_SFTP_PORT),
    }
    if parsed != expected:
        raise ValueError(
            "Configured gleam43a remote does not match the frozen official "
            f"SFTP endpoint: {parsed!r}"
        )
    return {
        "rclone_alias": "gleam43a:",
        "backend": parsed["type"],
        "host": parsed["host"],
        "port": int(parsed["port"]),
        "credentials_recorded": False,
    }


def query_rclone_version() -> str:
    completed = subprocess.run(
        ["rclone", "version"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode or not completed.stdout.strip():
        raise RuntimeError("Unable to query rclone version")
    return completed.stdout.splitlines()[0].strip()


def _write_audit_exclusive(path: Path, payload: dict[str, Any]) -> None:
    _validate_external_path(path, label="GLEAM audit path")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def _audit_path(root: Path, year: int, started: datetime) -> Path:
    path = root / "_meta" / f"gleam43a_{year}_fetch_{_token(started)}_{os.getpid()}.json"
    return _validate_external_path(path, label="GLEAM audit path")


def _publish_exclusive(attempt: Path, final: Path) -> None:
    """Create the final hard link without a check-then-replace race."""

    if final.exists():
        raise FileExistsError(f"Refusing to replace existing GLEAM input: {final}")
    final.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(attempt, final)
    except FileExistsError as exc:
        raise FileExistsError(
            f"Concurrent GLEAM publication already created: {final}"
        ) from exc
    if not final.is_file() or final.stat().st_size != attempt.stat().st_size:
        raise RuntimeError(f"Exclusive GLEAM publication was not durable: {final}")


def _validate_against_remote(
    path: Path,
    *,
    layer: str,
    year: int,
    remote: dict[str, Any],
) -> dict[str, Any]:
    report = validate_file(path, layer=layer, year=year)
    if int(report["size_bytes"]) != int(remote["size_bytes"]):
        raise ValueError(
            f"Validated local size differs from official listing for {layer}: "
            f"{report['size_bytes']} != {remote['size_bytes']}"
        )
    report["remote_logical_path"] = remote["logical_path"]
    report["remote_size_bytes"] = int(remote["size_bytes"])
    report["remote_mtime"] = remote["mtime"]
    report["remote_checksum_available"] = False
    report["local_sha256_baseline_origin"] = (
        "first_validated_download_no_upstream_checksum"
    )
    return report


def _download_one(
    root: Path,
    *,
    layer: str,
    year: int,
    remote: dict[str, Any],
) -> dict[str, Any]:
    final = root / str(year) / str(remote["name"])
    if final.exists():
        report = _validate_against_remote(
            final, layer=layer, year=year, remote=remote
        )
        report["disposition"] = "reused_existing_fully_validated_immutable_input"
        return report

    repair = root / "climate_stress_repair_v1"
    attempt_root = _validate_external_path(
        repair / "download_attempts", label="GLEAM download attempt root"
    )
    log_root = _validate_external_path(
        repair / "download_logs", label="GLEAM download log root"
    )
    attempt_root.mkdir(parents=True, exist_ok=True)
    log_root.mkdir(parents=True, exist_ok=True)
    suffix = f"{_token()}.{os.getpid()}"
    attempt = attempt_root / f"{remote['name']}.rclone-download.{suffix}"
    log = log_root / f"{remote['name']}.rclone-download.{suffix}.log"
    if attempt.exists() or log.exists():
        raise FileExistsError("Unique GLEAM attempt or log path already exists")

    command = [
        "rclone",
        "copyto",
        str(remote["logical_path"]),
        str(attempt),
        "--immutable",
        "--local-no-sparse",
        "--transfers",
        "1",
        "--checkers",
        "1",
        "--retries",
        "3",
        "--low-level-retries",
        "10",
        "--stats",
        "30s",
        "--stats-one-line",
        "--log-level",
        "INFO",
        "--log-file",
        str(log),
    ]
    completed = subprocess.run(command, check=False)
    if completed.returncode:
        raise RuntimeError(f"rclone download failed for {remote['logical_path']}")

    report = _validate_against_remote(
        attempt, layer=layer, year=year, remote=remote
    )
    _publish_exclusive(attempt, final)
    report["path"] = str(final.resolve())
    report["immutable_download_attempt"] = str(attempt.resolve())
    report["rclone_log"] = str(log.resolve())
    report["rclone_log_sha256"] = sha256_file(log)
    report["disposition"] = "downloaded_validated_then_exclusively_hardlink_published"
    return report


def _validate_existing(
    root: Path,
    *,
    layer: str,
    year: int,
    remote: dict[str, Any],
) -> dict[str, Any]:
    final = root / str(year) / str(remote["name"])
    report = _validate_against_remote(final, layer=layer, year=year, remote=remote)
    report["disposition"] = "validated_existing_input"
    return report


def run(args: argparse.Namespace) -> int:
    started = _utc_now()
    root = resolve_gleam_root(args.gleam_root)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "year": args.year,
                    "official_remote_root": OFFICIAL_REMOTE_ROOT,
                    "target_pattern": str(root / "{year}" / "{layer}_{year}_GLEAM_v4.3a.nc"),
                    "overwrite_policy": "exclusive_create_only_no_delete_no_replace",
                },
                indent=2,
            )
        )
        return 0

    audit_path = _audit_path(root, args.year, started)
    script_path = Path(__file__).resolve()
    validator_path = script_path.with_name("validate_gleam43a_year_input.py")
    audit: dict[str, Any] = {
        "schema_version": 1,
        "status": "RUNNING",
        "started_at_utc": started.isoformat(),
        "mode": args.mode,
        "year": args.year,
        "official_source_url": OFFICIAL_SOURCE_URL,
        "official_remote_root": OFFICIAL_REMOTE_ROOT,
        "remote_checksum_available": False,
        "local_sha256_baseline_origin": (
            "first_validated_download_no_upstream_checksum"
        ),
        "overwrite_policy": (
            "download_to_unique_retained_attempt; validate_before publish; "
            "exclusive_create-only hard link; never replace or delete"
        ),
        "source_code": {
            "repository_head_at_run": _git_head(),
            "fetcher_sha256": sha256_file(script_path),
            "validator_sha256": sha256_file(validator_path),
            "validator_schema_version": 1,
        },
        "results": [],
    }
    return_code = 0
    try:
        listing, listing_hash = query_remote_listing(args.year)
        audit["remote_endpoint"] = query_sanitized_remote_identity()
        audit["rclone_version"] = query_rclone_version()
        if remote_has_native_checksums():
            raise ValueError(
                "Official remote unexpectedly reports native hashes; update audit semantics"
            )
        audit["remote_listing"] = listing
        audit["remote_listing_canonical_sha256"] = listing_hash
        for remote in listing:
            layer = str(remote["layer"])
            if args.mode == "download":
                result = _download_one(
                    root,
                    layer=layer,
                    year=args.year,
                    remote=remote,
                )
            else:
                result = _validate_existing(
                    root,
                    layer=layer,
                    year=args.year,
                    remote=remote,
                )
            audit["results"].append(result)
            print(
                f"VALID|{layer}|{result['size_bytes']}|{result['sha256']}|"
                f"{result['time_start']}|{result['time_end']}"
            )
        audit["status"] = "SUCCESS"
    except Exception as exc:
        audit["status"] = "FAILED"
        audit["error_type"] = type(exc).__name__
        audit["error"] = str(exc)
        return_code = 2
    finally:
        audit["finished_at_utc"] = _utc_now().isoformat()
        _write_audit_exclusive(audit_path, audit)
        print(f"AUDIT|{audit_path}")

    if return_code:
        print(f"ERROR|{audit['error_type']}|{audit['error']}", file=sys.stderr)
    return return_code


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--gleam-root",
        help="absolute input root; defaults to GLEAM_ROOT",
    )
    parser.add_argument("--year", type=int, choices=SUPPORTED_YEARS, default=2020)
    parser.add_argument(
        "--mode", choices=("download", "validate"), default="download"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print frozen logical paths without network or filesystem writes",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
