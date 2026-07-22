#!/usr/bin/env python3
"""Download and validate immutable ERA5 repair inputs for the climate panel.

The script is intentionally restricted to the three known-bad local years.  It
uses the official Copernicus Climate Data Store API, writes only below a new
``climate_stress_repair_v1`` directory, refuses to overwrite any file, and
records a credential-free JSON audit for every invocation.
"""

from __future__ import annotations

import argparse
import calendar
from contextlib import contextmanager
import hashlib
import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import netCDF4 as nc
import numpy as np


DATASET = "reanalysis-era5-single-levels"
VARIABLE = "2m_temperature"
SUPPORTED_YEARS = (1980, 1985, 1986)
TARGET_NLAT = 510
TARGET_NLON = 630
TARGET_LATITUDE = 53.93 - 0.1 * np.arange(TARGET_NLAT, dtype=np.float64)
TARGET_LONGITUDE = 73.08 + 0.1 * np.arange(TARGET_NLON, dtype=np.float64)
TARGET_AREA = [53.93, 73.08, 3.03, 135.98]
TARGET_GRID = [0.1, 0.1]
TIME_UNITS = "seconds since 1970-01-01"
TIME_CALENDAR = "proleptic_gregorian"
HASH_BLOCK_BYTES = 8 * 1024 * 1024
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _timestamp_token(moment: datetime | None = None) -> str:
    value = moment or _utc_now()
    return value.strftime("%Y%m%dT%H%M%S.%fZ")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(HASH_BLOCK_BYTES):
            digest.update(block)
    return digest.hexdigest()


def request_for_year(year: int) -> dict[str, Any]:
    if year not in SUPPORTED_YEARS:
        raise ValueError(f"Unsupported ERA5 repair year: {year}")
    return {
        "product_type": ["reanalysis"],
        "variable": [VARIABLE],
        "year": [str(year)],
        "month": [f"{month:02d}" for month in range(1, 13)],
        "day": [f"{day:02d}" for day in range(1, 32)],
        "time": [f"{hour:02d}:00" for hour in range(24)],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": TARGET_AREA,
        "grid": TARGET_GRID,
    }


def _expected_epoch_seconds(year: int) -> np.ndarray:
    count = (366 if calendar.isleap(year) else 365) * 24
    start = int(datetime(year, 1, 1, tzinfo=timezone.utc).timestamp())
    return start + np.arange(count, dtype=np.int64) * 3600


def validate_annual_file(path: Path, year: int) -> dict[str, Any]:
    """Validate the complete frozen input contract without loading all t2m."""
    if not path.is_file():
        raise FileNotFoundError(path)

    expected_time = _expected_epoch_seconds(year)
    with nc.Dataset(path, "r") as dataset:
        dimensions = {name: len(value) for name, value in dataset.dimensions.items()}
        expected_dimensions = {
            "valid_time": int(expected_time.size),
            "latitude": TARGET_NLAT,
            "longitude": TARGET_NLON,
        }
        if dimensions != expected_dimensions:
            raise ValueError(
                f"Unexpected dimensions for {path}: {dimensions}; "
                f"expected {expected_dimensions}"
            )

        required_variables = {
            "number",
            "valid_time",
            "latitude",
            "longitude",
            "expver",
            "t2m",
        }
        missing = sorted(required_variables.difference(dataset.variables))
        if missing:
            raise ValueError(f"Missing variables in {path}: {missing}")

        latitude = np.asarray(dataset.variables["latitude"][:], dtype=np.float64)
        longitude = np.asarray(dataset.variables["longitude"][:], dtype=np.float64)
        if not np.allclose(latitude, TARGET_LATITUDE, rtol=0.0, atol=5e-12):
            raise ValueError(f"Latitude axis differs from the frozen ERA5 axis: {path}")
        if not np.allclose(longitude, TARGET_LONGITUDE, rtol=0.0, atol=5e-12):
            raise ValueError(f"Longitude axis differs from the frozen ERA5 axis: {path}")

        time_variable = dataset.variables["valid_time"]
        units = str(getattr(time_variable, "units", ""))
        time_calendar = str(getattr(time_variable, "calendar", ""))
        if units != TIME_UNITS or time_calendar != TIME_CALENDAR:
            raise ValueError(
                f"Unexpected time encoding in {path}: units={units!r}, "
                f"calendar={time_calendar!r}"
            )
        actual_time = np.asarray(time_variable[:], dtype=np.int64)
        if not np.array_equal(actual_time, expected_time):
            mismatch = np.flatnonzero(actual_time != expected_time)
            first = int(mismatch[0]) if mismatch.size else None
            raise ValueError(f"UTC hourly axis is not exact in {path}; first mismatch={first}")

        temperature = dataset.variables["t2m"]
        if temperature.dimensions != ("valid_time", "latitude", "longitude"):
            raise ValueError(f"Unexpected t2m dimensions in {path}: {temperature.dimensions}")
        if np.dtype(temperature.dtype) != np.dtype("float32"):
            raise ValueError(f"Unexpected t2m dtype in {path}: {temperature.dtype}")
        if str(getattr(temperature, "units", "")) != "K":
            raise ValueError(f"Unexpected t2m units in {path}")

        sample_indices = np.unique(
            np.asarray([0, expected_time.size // 2, expected_time.size - 1], dtype=np.int64)
        )
        sample = np.ma.asarray(temperature[sample_indices, :, :])
        finite = np.asarray(sample.compressed(), dtype=np.float64)
        if finite.size == 0 or not np.isfinite(finite).all():
            raise ValueError(f"t2m validation sample is empty or non-finite in {path}")
        sample_min = float(finite.min())
        sample_max = float(finite.max())
        if sample_min < 150.0 or sample_max > 350.0:
            raise ValueError(
                f"t2m validation sample is outside broad Kelvin limits in {path}: "
                f"{sample_min}..{sample_max}"
            )

        return {
            "path": str(path.resolve()),
            "size_bytes": path.stat().st_size,
            "dimensions": dimensions,
            "variables": list(dataset.variables),
            "t2m_dtype": str(temperature.dtype),
            "t2m_dimensions": list(temperature.dimensions),
            "t2m_chunking": temperature.chunking(),
            "t2m_filters": temperature.filters(),
            "t2m_units": str(getattr(temperature, "units", "")),
            "sample_min_k": sample_min,
            "sample_max_k": sample_max,
            "time_units": units,
            "time_calendar": time_calendar,
            "first_utc": datetime.fromtimestamp(
                int(actual_time[0]), tz=timezone.utc
            ).isoformat(),
            "last_utc": datetime.fromtimestamp(
                int(actual_time[-1]), tz=timezone.utc
            ).isoformat(),
            "hour_count": int(actual_time.size),
            "latitude_first": float(latitude[0]),
            "latitude_last": float(latitude[-1]),
            "longitude_first": float(longitude[0]),
            "longitude_last": float(longitude[-1]),
        }


def _audit_path(repair_root: Path, started: datetime) -> Path:
    audit_root = repair_root / "audit"
    audit_root.mkdir(parents=True, exist_ok=True)
    return audit_root / f"era5_repair_{_timestamp_token(started)}_{os.getpid()}.json"


def _write_audit_exclusive(path: Path, payload: dict[str, Any]) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def _json_sha256(payload: Any) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _operation_record_root(repair_root: Path) -> Path:
    root = repair_root / "audit" / "operation_records"
    root.mkdir(parents=True, exist_ok=True)
    return root


@contextmanager
def _exclusive_year_lock(repair_root: Path, year: int) -> Iterable[Path]:
    """Hold a crash-releasing OS lock without deleting the persistent lock file."""
    lock_root = repair_root / "audit" / "year_locks"
    lock_root.mkdir(parents=True, exist_ok=True)
    lock_path = lock_root / f"ERA{year}.lock"
    handle = lock_path.open("a+b")
    if handle.tell() == 0:
        handle.write(b"0")
        handle.flush()
        os.fsync(handle.fileno())
    handle.seek(0)
    locked = False
    try:
        if os.name == "nt":
            import msvcrt

            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise RuntimeError(
                    f"Another process already owns the ERA5 repair lock for {year}: "
                    f"{lock_path}"
                ) from exc
        else:
            import fcntl

            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise RuntimeError(
                    f"Another process already owns the ERA5 repair lock for {year}: "
                    f"{lock_path}"
                ) from exc
        locked = True
        yield lock_path
    finally:
        if locked:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def _start_operation_record(
    repair_root: Path,
    *,
    year: int,
    mode: str,
    attempt: Path | None,
    lock_path: Path | None = None,
) -> dict[str, Any]:
    started = _utc_now()
    lease_id = f"{year}-{_timestamp_token(started)}-{os.getpid()}"
    request = request_for_year(year)
    payload = {
        "schema_version": 1,
        "record_kind": "SCRIPT_OPERATION_STARTED",
        "status": "STARTED",
        "lease_id": lease_id,
        "year": year,
        "mode": mode,
        "pid": os.getpid(),
        "host": socket.gethostname(),
        "started_at_utc": started.isoformat(),
        "dataset": DATASET,
        "request_sha256": _json_sha256(request),
        "request": request,
        "script_path": str(Path(__file__).resolve()),
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "git_head": _git_head(),
        "attempt_path": str(attempt.resolve()) if attempt is not None else None,
        "year_lock_path": str(lock_path.resolve()) if lock_path is not None else None,
        "final_path": str(
            (repair_root / "CN_clipped" / f"ERA{year}_clipped.nc").resolve()
        ),
        "immutability": "exclusive create; this STARTED record is never updated",
    }
    path = _operation_record_root(repair_root) / f"{lease_id}.STARTED.json"
    _write_audit_exclusive(path, payload)
    payload["record_path"] = str(path.resolve())
    return payload


def _write_terminal_operation_record(
    repair_root: Path,
    started_record: dict[str, Any],
    *,
    status: str,
    result: dict[str, Any] | None = None,
    error: BaseException | None = None,
) -> Path:
    if status not in {"SUCCESS", "FAILED", "INTERRUPTED"}:
        raise ValueError(f"Unsupported terminal operation status: {status}")
    payload: dict[str, Any] = {
        "schema_version": 1,
        "record_kind": "SCRIPT_OPERATION_TERMINAL",
        "status": status,
        "lease_id": started_record["lease_id"],
        "year": started_record["year"],
        "pid": started_record["pid"],
        "host": started_record["host"],
        "started_record": started_record["record_path"],
        "finished_at_utc": _utc_now().isoformat(),
        "attempt_path": started_record["attempt_path"],
    }
    if result is not None:
        payload["result"] = result
    if error is not None:
        payload["error_type"] = type(error).__name__
        payload["error"] = str(error)
    path = _operation_record_root(repair_root) / (
        f"{started_record['lease_id']}.{status}.json"
    )
    _write_audit_exclusive(path, payload)
    return path


def _audit_health(repair_root: Path, years: Iterable[int]) -> dict[str, Any]:
    record_root = repair_root / "audit" / "operation_records"
    records: list[dict[str, Any]] = []
    if record_root.is_dir():
        for path in sorted(record_root.glob("*.json")):
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            payload["_path"] = str(path.resolve())
            records.append(payload)

    requested = set(int(year) for year in years)
    started = {
        str(record["lease_id"]): record
        for record in records
        if record.get("record_kind") == "SCRIPT_OPERATION_STARTED"
        and int(record.get("year", -1)) in requested
    }
    terminal = {
        str(record["lease_id"]): record
        for record in records
        if record.get("record_kind") == "SCRIPT_OPERATION_TERMINAL"
        and int(record.get("year", -1)) in requested
    }
    unresolved = sorted(set(started).difference(terminal))

    known_attempts = {
        str(Path(record["attempt_path"]).resolve())
        for record in started.values()
        if record.get("attempt_path")
    }
    external_root = repair_root / "audit" / "external_supervisor_records"
    if external_root.is_dir():
        for path in sorted(external_root.glob("*.json")):
            with path.open("r", encoding="utf-8") as handle:
                external = json.load(handle)
            if external.get("attempt_path"):
                known_attempts.add(str(Path(external["attempt_path"]).resolve()))

    orphan_attempts: list[str] = []
    attempt_root = repair_root / "download_attempts"
    if attempt_root.is_dir():
        for year in requested:
            for attempt in attempt_root.glob(f"ERA{year}_clipped.cds-download.*.nc"):
                resolved = str(attempt.resolve())
                if resolved not in known_attempts:
                    orphan_attempts.append(resolved)

    successful_years = {
        int(record["year"])
        for record in terminal.values()
        if record.get("status") == "SUCCESS"
    }
    return {
        "unresolved_started_leases": unresolved,
        "orphan_attempts": sorted(orphan_attempts),
        "successful_years": sorted(successful_years),
    }


def _assert_audit_ready(repair_root: Path, years: Iterable[int]) -> None:
    requested = tuple(int(year) for year in years)
    health = _audit_health(repair_root, requested)
    missing_success = sorted(set(requested).difference(health["successful_years"]))
    problems: list[str] = []
    if health["unresolved_started_leases"]:
        problems.append(
            f"unresolved STARTED leases={health['unresolved_started_leases']}"
        )
    if health["orphan_attempts"]:
        problems.append(f"orphan attempts={health['orphan_attempts']}")
    if missing_success:
        problems.append(f"years without SCRIPT SUCCESS={missing_success}")
    if problems:
        raise RuntimeError("ERA5 repair audit is incomplete: " + "; ".join(problems))


def _resolve_era_root(argument: str | None) -> Path:
    raw = argument or os.environ.get("ERA5_ROOT", "")
    if not raw.strip():
        raise ValueError("Provide --era-root or define the non-empty ERA5_ROOT variable")
    root = Path(raw).expanduser()
    if not root.is_absolute():
        raise ValueError(f"ERA5 root must be absolute: {root}")
    if root.parent == root:
        raise ValueError(f"ERA5 root may not be a filesystem root: {root}")
    resolved = root.resolve()
    repair_root = (resolved / "climate_stress_repair_v1").resolve()
    repository_root = REPOSITORY_ROOT.resolve()
    if repair_root == repository_root or repository_root in repair_root.parents:
        raise ValueError(
            f"ERA5 repair output must remain outside the repository/worktree: {repair_root}"
        )
    for ancestor in (repair_root, *repair_root.parents):
        if (ancestor / ".git").exists():
            raise ValueError(
                f"ERA5 repair output may not be inside any Git repository/worktree: "
                f"{repair_root}"
            )
    return resolved


def _publish_exclusive(attempt: Path, final: Path) -> None:
    """Publish without an overwrite race and retain the immutable attempt."""
    if final.exists():
        raise FileExistsError(f"Refusing to replace an existing repair file: {final}")
    try:
        os.link(attempt, final)
    except FileExistsError as exc:
        raise FileExistsError(
            f"Concurrent repair publication already created: {final}"
        ) from exc
    if not final.is_file() or final.stat().st_size != attempt.stat().st_size:
        raise RuntimeError(f"Exclusive repair publication was not durable: {final}")


def _download_one(
    client: Any,
    repair_root: Path,
    era_root: Path,
    year: int,
    *,
    attempt: Path | None = None,
) -> dict[str, Any]:
    final_root = repair_root / "CN_clipped"
    attempt_root = repair_root / "download_attempts"
    final_root.mkdir(parents=True, exist_ok=True)
    attempt_root.mkdir(parents=True, exist_ok=True)
    final = final_root / f"ERA{year}_clipped.nc"
    old = era_root / "CN_clipped" / f"ERA{year}_clipped.nc"

    if final.exists():
        validation = validate_annual_file(final, year)
        disposition = "reused_existing_valid_repair"
    else:
        if attempt is None:
            raise ValueError("A predeclared attempt path is required before CDS retrieval")
        if attempt.exists():
            raise FileExistsError(f"Refusing to overwrite download attempt: {attempt}")
        client.retrieve(DATASET, request_for_year(year), str(attempt))
        validation = validate_annual_file(attempt, year)
        _publish_exclusive(attempt, final)
        validation["path"] = str(final.resolve())
        validation["immutable_download_attempt"] = str(attempt.resolve())
        disposition = "downloaded_validated_and_exclusively_hardlink_published"

    validation["sha256"] = sha256_file(final)
    validation["disposition"] = disposition
    if old.is_file():
        validation["old_wrong_path"] = str(old.resolve())
        validation["old_wrong_size_bytes"] = old.stat().st_size
        validation["old_wrong_sha256"] = sha256_file(old)
        validation["differs_from_old_wrong_file"] = (
            validation["sha256"] != validation["old_wrong_sha256"]
        )
        if not validation["differs_from_old_wrong_file"]:
            raise ValueError(f"Repair file unexpectedly matches old wrong file: {final}")
    else:
        validation["old_wrong_path"] = str(old.resolve())
        validation["old_wrong_status"] = "missing"
    return validation


def run(args: argparse.Namespace) -> int:
    started = _utc_now()
    era_root = _resolve_era_root(args.era_root)
    repair_root = era_root / "climate_stress_repair_v1"
    audit = {
        "schema_version": 1,
        "started_at_utc": started.isoformat(),
        "status": "RUNNING",
        "mode": args.mode,
        "years": list(args.years),
        "dataset": DATASET,
        "request_template": {
            "variable": VARIABLE,
            "product_type": "reanalysis",
            "data_format": "netcdf",
            "download_format": "unarchived",
            "area": TARGET_AREA,
            "grid": TARGET_GRID,
        },
        "official_sources": [
            "https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels",
            "https://cds.climate.copernicus.eu/how-to-api",
        ],
        "repair_root": str(repair_root.resolve()),
        "overwrite_policy": "exclusive_create_only; existing files are never replaced or deleted",
        "results": [],
    }

    if args.dry_run:
        for year in args.years:
            print(json.dumps(request_for_year(year), indent=2, sort_keys=True))
        return 0

    audit_path = _audit_path(repair_root, started)
    try:
        if args.mode == "download":
            try:
                import cdsapi
            except ImportError as exc:
                raise RuntimeError(
                    "Install cdsapi>=0.7.7 before using --mode download"
                ) from exc
            client = cdsapi.Client(quiet=False, debug=False)
            for year in args.years:
                with _exclusive_year_lock(repair_root, year) as lock_path:
                    final = repair_root / "CN_clipped" / f"ERA{year}_clipped.nc"
                    attempt = None
                    if not final.exists():
                        attempt = repair_root / "download_attempts" / (
                            f"ERA{year}_clipped.cds-download."
                            f"{_timestamp_token()}.{os.getpid()}.nc"
                        )
                    operation = _start_operation_record(
                        repair_root,
                        year=year,
                        mode="download" if attempt is not None else "validate_existing",
                        attempt=attempt,
                        lock_path=lock_path,
                    )
                    try:
                        result = _download_one(
                            client,
                            repair_root,
                            era_root,
                            year,
                            attempt=attempt,
                        )
                    except BaseException as exc:
                        status = (
                            "INTERRUPTED"
                            if isinstance(exc, (KeyboardInterrupt, SystemExit))
                            else "FAILED"
                        )
                        _write_terminal_operation_record(
                            repair_root, operation, status=status, error=exc
                        )
                        raise
                    _write_terminal_operation_record(
                        repair_root, operation, status="SUCCESS", result=result
                    )
                audit["results"].append(result)
                print(
                    f"VALID|{year}|{result['path']}|{result['size_bytes']}|"
                    f"{result['sha256']}|{result['first_utc']}|{result['last_utc']}"
                )
        else:
            _assert_audit_ready(repair_root, args.years)
            for year in args.years:
                final = repair_root / "CN_clipped" / f"ERA{year}_clipped.nc"
                result = validate_annual_file(final, year)
                result["sha256"] = sha256_file(final)
                old = era_root / "CN_clipped" / f"ERA{year}_clipped.nc"
                if old.is_file():
                    result["old_wrong_path"] = str(old.resolve())
                    result["old_wrong_sha256"] = sha256_file(old)
                    result["differs_from_old_wrong_file"] = (
                        result["sha256"] != result["old_wrong_sha256"]
                    )
                    if not result["differs_from_old_wrong_file"]:
                        raise ValueError(f"Repair file matches old wrong file: {final}")
                audit["results"].append(result)
                print(
                    f"VALID|{year}|{result['path']}|{result['size_bytes']}|"
                    f"{result['sha256']}|{result['first_utc']}|{result['last_utc']}"
                )
        audit["status"] = "SUCCESS"
        return_code = 0
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


def _parse_years(values: Iterable[str]) -> tuple[int, ...]:
    parsed = tuple(int(value) for value in values)
    unsupported = sorted(set(parsed).difference(SUPPORTED_YEARS))
    if unsupported:
        raise argparse.ArgumentTypeError(f"Unsupported repair years: {unsupported}")
    if len(set(parsed)) != len(parsed):
        raise argparse.ArgumentTypeError("Repair years must be unique")
    return parsed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--era-root",
        help="Absolute ERA5 root; defaults to the ERA5_ROOT environment variable",
    )
    parser.add_argument(
        "--mode",
        choices=("download", "validate"),
        default="download",
        help="Download and validate, or validate already-published repair files",
    )
    parser.add_argument(
        "--years",
        nargs="+",
        default=[str(year) for year in SUPPORTED_YEARS],
        metavar="YEAR",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print credential-free CDS requests without writing external files",
    )
    args = parser.parse_args(argv)
    try:
        args.years = _parse_years(args.years)
    except (ValueError, argparse.ArgumentTypeError) as exc:
        parser.error(str(exc))
    return args


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
