"""Non-overwriting runtime primitives for the climate-stress pipeline.

The runtime has two independent recovery boundaries:

* ``_RUN.json`` freezes the configuration and run-level parameters.
* ``stages/<stage>/_SUCCESS.json`` records a completed stage and its evidence.

Failed writes are intentionally left as uniquely named ``*.partial`` paths.
The orchestrator may reuse one only after its frozen source, parameter, config,
and dependency signatures have all been verified.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import getpass
import socket
import subprocess
import sys
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping

from .config import CODE_FROZEN_RUNTIME_CONSTANTS, PipelineConfig


RUN_MANIFEST = "_RUN.json"
STAGE_SUCCESS = "_SUCCESS.json"
RUN_LOCKS_DIR = ".run-locks"


class ResumeMismatchError(RuntimeError):
    """Raised when a resume marker does not match the requested execution."""


class PathOutsideRunError(ValueError):
    """Raised when mutable pipeline state is directed outside its run directory."""


class RunLockError(RuntimeError):
    """Raised when a run-id already has an owner or lock integrity is lost."""


def _jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, set):
        return sorted(_jsonable(item) for item in value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"Unsupported manifest value: {type(value).__name__}")


def canonical_json(value: Any) -> str:
    """Return the canonical JSON representation used for signatures."""

    return json.dumps(
        _jsonable(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def parameter_signature(parameters: Mapping[str, Any] | None) -> str:
    payload = canonical_json(dict(parameters or {})).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def process_memory_snapshot() -> dict[str, Any]:
    """Return current and process-peak RSS using OS facilities only."""

    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes

            class ProcessMemoryCountersEx(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                    ("PrivateUsage", ctypes.c_size_t),
                ]

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            kernel32.GetCurrentProcess.restype = wintypes.HANDLE
            psapi.GetProcessMemoryInfo.argtypes = (
                wintypes.HANDLE,
                ctypes.POINTER(ProcessMemoryCountersEx),
                wintypes.DWORD,
            )
            psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
            counters = ProcessMemoryCountersEx()
            counters.cb = ctypes.sizeof(counters)
            if not psapi.GetProcessMemoryInfo(
                kernel32.GetCurrentProcess(),
                ctypes.byref(counters),
                counters.cb,
            ):
                raise ctypes.WinError(ctypes.get_last_error())
            return {
                "sampled_at_utc": utc_now(),
                "rss_bytes": int(counters.WorkingSetSize),
                "process_peak_rss_bytes": int(counters.PeakWorkingSetSize),
                "source": "windows.GetProcessMemoryInfo",
            }
        except (AttributeError, ImportError, OSError):
            pass

    current_rss = 0
    source = "resource.getrusage"
    try:
        statm = Path("/proc/self/statm")
        if statm.is_file():
            resident_pages = int(statm.read_text(encoding="ascii").split()[1])
            current_rss = resident_pages * int(os.sysconf("SC_PAGE_SIZE"))
            source = "/proc/self/statm+resource.getrusage"
        import resource

        peak = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        if sys.platform != "darwin":
            peak *= 1024
        if current_rss <= 0:
            current_rss = peak
        return {
            "sampled_at_utc": utc_now(),
            "rss_bytes": max(0, current_rss),
            "process_peak_rss_bytes": max(0, peak),
            "source": source,
        }
    except (ImportError, IndexError, OSError, ValueError):
        return {
            "sampled_at_utc": utc_now(),
            "rss_bytes": 0,
            "process_peak_rss_bytes": 0,
            "source": "unavailable",
        }


def stage_resource_usage(
    start: Mapping[str, Any],
    end: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize two samples into the stable stage resource contract."""

    final = dict(end or process_memory_snapshot())
    initial = dict(start)
    values = {
        "stage_start_current_rss_bytes": max(0, int(initial.get("rss_bytes", 0))),
        "stage_end_current_rss_bytes": max(0, int(final.get("rss_bytes", 0))),
        "process_lifetime_peak_working_set_bytes": max(
            0,
            int(initial.get("process_peak_rss_bytes", 0)),
            int(final.get("process_peak_rss_bytes", 0)),
        ),
        "sampled_start_at_utc": str(initial.get("sampled_at_utc", utc_now())),
        "sampled_end_at_utc": str(final.get("sampled_at_utc", utc_now())),
        "start_source": str(initial.get("source", "unknown")),
        "end_source": str(final.get("source", "unknown")),
    }
    return values


@dataclass
class RunLock:
    """One OS-backed run lease with immutable acquire/release audits."""

    path: Path
    lease_id: str
    metadata: dict[str, Any]
    handle: Any
    release_attempted: bool = False
    released: bool = False
    release_error: BaseException | None = None
    release_attempted_at_utc: str | None = None
    release_terminal_at_utc: str | None = None
    released_at_utc: str | None = None
    release_audit_persisted: bool | None = None
    release_timestamp_recorded: bool | None = None
    os_unlock_succeeded: bool | None = None
    handle_closed: bool | None = None

    def release(self) -> None:
        if self.release_attempted:
            return
        audit_error: BaseException | None = None
        attempt_timestamp_error: BaseException | None = None
        terminal_timestamp_error: BaseException | None = None
        unlock_error: BaseException | None = None
        close_error: BaseException | None = None
        release_attempted_at_utc: str | None = None
        release_terminal_at_utc: str | None = None
        try:
            release_attempted_at_utc = utc_now()
        except BaseException as exc:
            attempt_timestamp_error = exc
        try:
            try:
                _unlock_file(self.handle)
            except BaseException as exc:
                unlock_error = exc
        finally:
            try:
                self.handle.close()
            except BaseException as exc:
                close_error = exc
        release_operation_succeeded = (
            unlock_error is None and close_error is None
        )
        try:
            release_terminal_at_utc = utc_now()
        except BaseException as exc:
            terminal_timestamp_error = exc
        released_at_utc = (
            release_terminal_at_utc if release_operation_succeeded else None
        )
        try:
            _write_lock_audit(
                self.path.parent
                / f"{self.metadata['run_id']}.released.{self.lease_id}.json",
                {
                    **self.metadata,
                    "release_attempted_at_utc": release_attempted_at_utc,
                    "release_terminal_at_utc": release_terminal_at_utc,
                    "released_at_utc": released_at_utc,
                    "release_attempted": True,
                    "released": (
                        release_operation_succeeded
                        and attempt_timestamp_error is None
                        and terminal_timestamp_error is None
                    ),
                    "release_timestamp_recorded": (
                        attempt_timestamp_error is None
                        and terminal_timestamp_error is None
                    ),
                    "os_unlock_succeeded": unlock_error is None,
                    "handle_closed": close_error is None,
                },
            )
        except BaseException as exc:
            audit_error = exc
        finally:
            self.release_attempted = True
            self.release_attempted_at_utc = release_attempted_at_utc
            self.release_terminal_at_utc = release_terminal_at_utc
            self.released_at_utc = released_at_utc
            self.release_audit_persisted = audit_error is None
            self.release_timestamp_recorded = (
                attempt_timestamp_error is None
                and terminal_timestamp_error is None
            )
            self.os_unlock_succeeded = unlock_error is None
            self.handle_closed = close_error is None
        failures = [
            ("release attempt timestamp", attempt_timestamp_error),
            ("release terminal timestamp", terminal_timestamp_error),
            ("release audit", audit_error),
            ("OS unlock", unlock_error),
            ("lock handle close", close_error),
        ]
        active_failures = [
            (label, error) for label, error in failures if error is not None
        ]
        self.released = not active_failures
        if active_failures:
            detail = "; ".join(
                f"{label}={type(error).__name__}: {error}"
                for label, error in active_failures
            )
            prefix = (
                "Failed to persist run-lock release audit"
                if audit_error is not None
                and attempt_timestamp_error is None
                and terminal_timestamp_error is None
                and unlock_error is None
                and close_error is None
                else "Failed to complete run-lock release"
            )
            release_failure = RunLockError(f"{prefix}: {detail}")
            first_cause = active_failures[0][1]
            release_failure.__cause__ = first_cause
            self.release_error = release_failure
            raise release_failure from first_cause


def _write_lock_audit(path: Path, payload: Mapping[str, Any]) -> None:
    encoded = json.dumps(
        _jsonable(payload),
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ).encode("utf-8")
    with path.open("xb") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())


def _try_lock_file(handle: Any) -> None:
    handle.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        return
    import fcntl

    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock_file(handle: Any) -> None:
    handle.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        return
    import fcntl

    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextmanager
def exclusive_run_lock(
    output_root: str | Path,
    run_id: str,
) -> Iterator[RunLock]:
    """Hold a non-blocking OS lock while preserving every lease audit."""

    _validate_run_id(run_id)
    root = Path(output_root).resolve(strict=False)
    lock_dir = root / RUN_LOCKS_DIR
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / f"{run_id}.lock"
    lease_id = uuid.uuid4().hex
    metadata = {
        "schema_version": 1,
        "run_id": run_id,
        "lease_id": lease_id,
        "owner": getpass.getuser(),
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "acquired_at_utc": utc_now(),
    }
    handle = lock_path.open("a+b")
    try:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
            os.fsync(handle.fileno())
        _try_lock_file(handle)
    except OSError as exc:
        handle.close()
        try:
            candidates = list(lock_dir.glob(f"{run_id}.acquired.*.json"))
            owner = _load_json(max(candidates, key=lambda path: path.stat().st_mtime_ns))
        except (OSError, ValueError, json.JSONDecodeError, FileNotFoundError):
            owner = {"status": "unreadable"}
        rejection = {
            **metadata,
            "rejected_at_utc": utc_now(),
            "active_owner": owner,
        }
        _write_lock_audit(
            lock_dir / f"{run_id}.rejected.{lease_id}.json", rejection
        )
        raise RunLockError(
            f"Run {run_id!r} is locked at {lock_path}; owner={canonical_json(owner)}. "
            "Concurrent execution was rejected without modifying the active run."
        ) from exc
    try:
        _write_lock_audit(
            lock_dir / f"{run_id}.acquired.{lease_id}.json", metadata
        )
    except BaseException as exc:
        try:
            _write_lock_audit(
                lock_dir / f"{run_id}.failed-acquire.{lease_id}.json",
                {**metadata, "failed_at_utc": utc_now(), "error": str(exc)},
            )
        finally:
            _unlock_file(handle)
            handle.close()
        raise
    lock = RunLock(
        path=lock_path,
        lease_id=lease_id,
        metadata=metadata,
        handle=handle,
    )
    try:
        yield lock
    except BaseException as active_error:
        try:
            lock.release()
        except BaseException as release_error:
            release_cause = release_error.__cause__
            cause_detail = (
                ""
                if release_cause is None
                else (
                    f"; cause={type(release_cause).__name__}: "
                    f"{release_cause}"
                )
            )
            try:
                active_error.add_note(
                    "Failed to persist or complete run-lock release while preserving "
                    f"the active {type(active_error).__name__}: "
                    f"{type(release_error).__name__}: {release_error}{cause_detail}"
                )
            except BaseException:
                pass
        raise
    else:
        lock.release()


def runtime_environment_provenance(
    repo_root: str | Path | None = None,
) -> tuple[str, dict[str, Any]]:
    """Return a stable signature of the executable environment and lock file."""

    distributions = (
        "netCDF4",
        "numpy",
        "pandas",
        "Pillow",
        "pyarrow",
        "pyproj",
        "PyYAML",
        "xarray",
    )
    versions: dict[str, str] = {}
    for distribution in distributions:
        try:
            versions[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            versions[distribution] = "not-installed"

    root = (
        Path(repo_root).resolve()
        if repo_root is not None
        else Path(__file__).resolve().parents[4]
    )
    lock_path = root / "data_build" / "requirements-climate-stress-lock.txt"
    lock_record: dict[str, Any] = {
        "path": str(lock_path),
        "exists": lock_path.is_file(),
    }
    if lock_path.is_file():
        lock_record.update(
            {
                "bytes": lock_path.stat().st_size,
                "sha256": sha256_file(lock_path),
            }
        )
    state = {
        "python": {
            "executable": str(Path(sys.executable).resolve()),
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "packages": versions,
        "requirements_lock": lock_record,
    }
    return parameter_signature(state), state


def git_commit(repo_root: str | Path | None = None) -> str:
    """Return the checked-out Git commit, or ``unknown`` outside a repository."""

    cwd = Path(repo_root).resolve() if repo_root is not None else Path.cwd()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    commit = result.stdout.strip()
    return commit if len(commit) == 40 else "unknown"


def _git_status_summary(
    repo_root: Path,
    scoped_paths: list[Path],
) -> dict[str, Any]:
    """Return aggregate Git state for source inputs without storing a diff."""

    relative_paths: list[str] = []
    for path in scoped_paths:
        try:
            relative_paths.append(path.resolve().relative_to(repo_root).as_posix())
        except ValueError:
            continue
    if not relative_paths:
        return {
            "available": False,
            "is_dirty": None,
            "status_counts": {},
            "scoped_path_count": 0,
        }
    try:
        result = subprocess.run(
            [
                "git",
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
                "--",
                *relative_paths,
            ],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return {
            "available": False,
            "is_dirty": None,
            "status_counts": {},
            "scoped_path_count": len(relative_paths),
        }
    counts = {
        "untracked": 0,
        "modified": 0,
        "added": 0,
        "deleted": 0,
        "renamed": 0,
        "other": 0,
    }
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    for line in lines:
        status = line[:2]
        if status == "??":
            counts["untracked"] += 1
        elif "R" in status:
            counts["renamed"] += 1
        elif "D" in status:
            counts["deleted"] += 1
        elif "A" in status:
            counts["added"] += 1
        elif "M" in status:
            counts["modified"] += 1
        else:
            counts["other"] += 1
    return {
        "available": True,
        "is_dirty": bool(lines),
        "status_counts": counts,
        "scoped_path_count": len(relative_paths),
        "status_entry_count": len(lines),
    }


def source_tree_provenance(
    config: PipelineConfig,
    *,
    repo_root: str | Path | None = None,
) -> tuple[str, dict[str, Any]]:
    """Hash the executable climate module, CLI, and frozen config identity."""

    module_root = Path(__file__).resolve().parent
    cli_path = module_root.parent / "build_climate_stress_panel.py"
    source_files = sorted(module_root.rglob("*.py"))
    if cli_path.is_file():
        source_files.append(cli_path)
    source_files = sorted(set(path.resolve() for path in source_files))
    digest = hashlib.sha256()
    for path in source_files:
        logical = (
            f"climate_stress/{path.relative_to(module_root).as_posix()}"
            if path.is_relative_to(module_root)
            else "build_climate_stress_panel.py"
        )
        encoded = logical.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        digest.update(bytes.fromhex(sha256_file(path)))
    config_label = b"frozen_config_sha256"
    digest.update(len(config_label).to_bytes(8, "big"))
    digest.update(config_label)
    digest.update(bytes.fromhex(config.sha256))

    root = Path(repo_root).resolve() if repo_root is not None else Path.cwd().resolve()
    status_paths = [module_root, cli_path]
    if config.path.exists():
        status_paths.append(config.path.resolve())
    state = _git_status_summary(root, status_paths)
    state.update(
        {
            "scope": "climate_stress_module_cli_config",
            "source_file_count": len(source_files),
            "config_sha256": config.sha256,
        }
    )
    return digest.hexdigest(), state


def sha256_file(path: str | Path, block_size: int = 8 * 1024 * 1024) -> str:
    """Compute a complete SHA-256 digest for a file."""

    source = Path(path)
    digest = hashlib.sha256()
    with source.open("rb") as handle:
        while block := handle.read(block_size):
            digest.update(block)
    return digest.hexdigest()


def sha256_path(path: str | Path) -> str:
    """Hash one file or a directory tree without following symlinks."""

    source = Path(path)
    if source.is_file():
        return sha256_file(source)
    if not source.is_dir():
        raise FileNotFoundError(source)
    digest = hashlib.sha256()
    files = sorted(item for item in source.rglob("*") if item.is_file())
    for item in files:
        relative = item.relative_to(source).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(bytes.fromhex(sha256_file(item)))
    return digest.hexdigest()


def ensure_within_run(path: str | Path, run_dir: str | Path) -> Path:
    """Resolve a mutable path and require it to be inside ``run_dir``."""

    candidate = Path(path).resolve(strict=False)
    root = Path(run_dir).resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise PathOutsideRunError(f"Path is outside run directory: {candidate}") from exc
    if candidate == root:
        raise PathOutsideRunError("A mutable artifact must be below the run directory")
    return candidate


def unique_partial_path(target: str | Path) -> Path:
    """Return an unused sibling path ending in ``.partial``."""

    destination = Path(target)
    while True:
        candidate = destination.with_name(
            f".{destination.name}.{uuid.uuid4().hex}.partial"
        )
        if not candidate.exists():
            return candidate


@contextmanager
def atomic_output(target: str | Path, run_dir: str | Path) -> Iterator[Path]:
    """Yield a unique partial path and rename it only if the target is absent.

    Any exception leaves the partial path untouched for diagnosis.  ``os.rename``
    is used rather than ``Path.replace`` because replacement is forbidden.
    """

    destination = ensure_within_run(target, run_dir)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(destination)
    partial = unique_partial_path(destination)
    try:
        yield partial
        if not partial.exists():
            raise FileNotFoundError(f"Atomic writer did not create {partial}")
        if destination.exists():
            raise FileExistsError(destination)
        os.rename(partial, destination)
    except BaseException:
        # Deliberately do not remove a failed partial artifact.
        raise


def _write_json_new(target: Path, payload: Mapping[str, Any], run_dir: Path) -> None:
    encoded = json.dumps(
        _jsonable(payload),
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ).encode("utf-8")
    with atomic_output(target, run_dir) as partial:
        with partial.open("xb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())


@dataclass(frozen=True)
class RunContext:
    config: PipelineConfig
    run_id: str
    run_dir: Path
    parameters: dict[str, Any]
    parameter_sha256: str
    source_tree_sha256: str
    source_state: dict[str, Any]
    environment_sha256: str
    environment_state: dict[str, Any]
    code_git_commit: str
    scope_profile: str
    completion_scope_status: str

    @property
    def cache_dir(self) -> Path:
        return self.run_dir / "cache"

    @property
    def temp_dir(self) -> Path:
        return self.run_dir / "temp"

    @property
    def audit_dir(self) -> Path:
        return self.run_dir / "audit"

    @property
    def output_dir(self) -> Path:
        return self.run_dir / "output"

    @property
    def stages_dir(self) -> Path:
        return self.run_dir / "stages"

    @property
    def manifest_path(self) -> Path:
        return self.run_dir / RUN_MANIFEST

    def mutable_path(self, *parts: str) -> Path:
        return ensure_within_run(self.run_dir.joinpath(*parts), self.run_dir)


def _run_manifest_payload(context: RunContext) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": context.run_id,
        "status": context.completion_scope_status,
        "scope_profile": context.scope_profile,
        "completion_scope_status": context.completion_scope_status,
        "created_at_utc": utc_now(),
        "version_id": context.config.version_id,
        "config_path": str(context.config.path),
        "config_sha256": context.config.sha256,
        "template_config_sha256": (
            context.config.template_sha256 or context.config.sha256
        ),
        "effective_config_sha256": context.config.sha256,
        "effective_config": context.config.data,
        "resolved_paths": context.config.resolved_paths(),
        "code_frozen_runtime_constants": CODE_FROZEN_RUNTIME_CONSTANTS,
        "parameters": context.parameters,
        "parameter_sha256": context.parameter_sha256,
        "source_tree_sha256": context.source_tree_sha256,
        "source_state": context.source_state,
        "environment_sha256": context.environment_sha256,
        "environment": context.environment_state,
        "run_signature_sha256": parameter_signature(
            {
                "parameters": context.parameters,
                "source_tree_sha256": context.source_tree_sha256,
                "environment_sha256": context.environment_sha256,
            }
        ),
        "code_git_commit": context.code_git_commit,
        "layout": {
            "cache": "cache",
            "temp": "temp",
            "audit": "audit",
            "output": "output",
            "stages": "stages",
        },
    }


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def _validate_run_id(run_id: str) -> None:
    if not run_id or run_id in {".", ".."} or Path(run_id).name != run_id:
        raise ValueError("run_id must be one non-empty path component")


def _preserve_failed_initialization(
    staging_dir: Path,
    *,
    run_id: str,
    invocation_id: str | None,
    exc: BaseException,
) -> Path | None:
    """Best-effort annotation and unique rename of a failed staging tree."""

    if not staging_dir.exists():
        return None
    payload = {
        "schema_version": 1,
        "run_id": run_id,
        "invocation_id": invocation_id,
        "failed_at_utc": utc_now(),
        "owner": getpass.getuser(),
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
    }
    try:
        _write_json_new(
            staging_dir / f"_INITIALIZATION_FAILED.{uuid.uuid4().hex}.json",
            payload,
            staging_dir,
        )
    except BaseException:
        # The directory name remains sufficient evidence if annotation itself
        # was the interrupted operation.
        pass
    incomplete = staging_dir.with_name(
        f"{staging_dir.name.removesuffix('.partial')}.incomplete"
    )
    try:
        os.rename(staging_dir, incomplete)
    except BaseException:
        return staging_dir
    return incomplete


def _annotate_initialization_exception(
    exc: BaseException,
    context: RunContext,
    *,
    evidence_dir: Path | None = None,
    observed_signatures: Mapping[str, Any] | None = None,
) -> None:
    """Attach JSON-safe requested-run evidence without changing exception text."""

    requested = {
        "run_id": context.run_id,
        "run_dir": str(context.run_dir),
        "parameters": context.parameters,
        "scope_profile": context.scope_profile,
        "completion_scope_status": context.completion_scope_status,
        "code_git_commit": context.code_git_commit,
        "requested_signatures": {
            "config_sha256": context.config.sha256,
            "parameter_sha256": context.parameter_sha256,
            "source_tree_sha256": context.source_tree_sha256,
            "environment_sha256": context.environment_sha256,
        },
        "observed_signatures": dict(observed_signatures or {}),
        "initialization_evidence_dir": (
            None if evidence_dir is None else str(evidence_dir)
        ),
    }
    try:
        setattr(exc, "initialization_audit_context", _jsonable(requested))
    except (AttributeError, TypeError):
        # The original exception remains authoritative if a third-party
        # exception type does not permit attached diagnostic attributes.
        pass


def initialize_run(
    config: PipelineConfig,
    *,
    run_id: str,
    parameters: Mapping[str, Any] | None = None,
    resume: bool = False,
    repo_root: str | Path | None = None,
    invocation_id: str | None = None,
) -> RunContext:
    """Create a new immutable run directory or validate an existing one."""

    _validate_run_id(run_id)
    if invocation_id is not None:
        _validate_run_id(invocation_id)
    normalized = _jsonable(dict(parameters or {}))
    signature = parameter_signature(normalized)
    source_digest, source_state = source_tree_provenance(
        config, repo_root=repo_root
    )
    environment_digest, environment_state = runtime_environment_provenance(
        repo_root=repo_root
    )
    output_root = config.output_root.resolve(strict=False)
    run_dir = (output_root / run_id).resolve(strict=False)
    context = RunContext(
        config=config,
        run_id=run_id,
        run_dir=run_dir,
        parameters=normalized,
        parameter_sha256=signature,
        source_tree_sha256=source_digest,
        source_state=source_state,
        environment_sha256=environment_digest,
        environment_state=environment_state,
        code_git_commit=git_commit(repo_root),
        scope_profile=config.scope_profile,
        completion_scope_status=config.completion_scope_status,
    )

    try:
        relative_run_dir = run_dir.relative_to(output_root)
    except ValueError:
        exc = PathOutsideRunError(
            f"Resolved run directory escapes output root: {run_dir}"
        )
        _annotate_initialization_exception(exc, context)
        raise exc
    if relative_run_dir.parts != (run_id,):
        exc = PathOutsideRunError(
            "Resolved run directory is not the dedicated direct child of "
            f"output root for {run_id!r}: {run_dir}"
        )
        _annotate_initialization_exception(exc, context)
        raise exc

    try:
        if run_dir.exists():
            if not resume:
                exc = FileExistsError(run_dir)
                _annotate_initialization_exception(exc, context)
                raise exc
            manifest_path = context.manifest_path.resolve(strict=False)
            try:
                relative_manifest = manifest_path.relative_to(run_dir)
            except ValueError:
                relative_manifest = None
            if (
                not run_dir.is_dir()
                or relative_manifest is None
                or relative_manifest.parts != (RUN_MANIFEST,)
                or not manifest_path.is_file()
            ):
                exc = ResumeMismatchError(
                    "Run manifest is missing or does not resolve to the dedicated "
                    f"run child: {context.manifest_path}"
                )
                _annotate_initialization_exception(exc, context)
                raise exc
            manifest = _load_json(manifest_path)
            expected = (config.sha256, signature, source_digest, environment_digest)
            observed = (
                manifest.get("config_sha256"),
                manifest.get("parameter_sha256"),
                manifest.get("source_tree_sha256"),
                manifest.get("environment_sha256"),
            )
            if observed != expected:
                exc = ResumeMismatchError(
                    "Run config, parameter, source signature, or environment signature "
                    "does not match the existing run"
                )
                _annotate_initialization_exception(
                    exc,
                    context,
                    observed_signatures={
                        "config_sha256": observed[0],
                        "parameter_sha256": observed[1],
                        "source_tree_sha256": observed[2],
                        "environment_sha256": observed[3],
                    },
                )
                raise exc
            for child_name, directory in (
                ("cache", context.cache_dir),
                ("temp", context.temp_dir),
                ("audit", context.audit_dir),
                ("output", context.output_dir),
                ("stages", context.stages_dir),
            ):
                resolved_directory = directory.resolve(strict=False)
                try:
                    relative_directory = resolved_directory.relative_to(run_dir)
                except ValueError:
                    relative_directory = None
                if (
                    relative_directory is None
                    or relative_directory.parts != (child_name,)
                    or not resolved_directory.is_dir()
                ):
                    exc = ResumeMismatchError(
                        "Run layout is incomplete or a child path escapes its "
                        f"dedicated location: {directory}"
                    )
                    _annotate_initialization_exception(exc, context)
                    raise exc
            return context
    except BaseException as exc:
        attached = getattr(exc, "initialization_audit_context", None)
        if not isinstance(attached, Mapping):
            _annotate_initialization_exception(exc, context)
        raise

    if resume:
        # Resuming a requested run that has not published is safe and creates it;
        # any prior .incomplete evidence remains untouched beside the run.
        pass
    output_root.mkdir(parents=True, exist_ok=True)
    initialization_token = invocation_id or uuid.uuid4().hex
    staging_dir = output_root / (
        f".{run_id}.{initialization_token}.{uuid.uuid4().hex}.initializing.partial"
    )
    staging_context = replace(context, run_dir=staging_dir)
    try:
        staging_dir.mkdir(exist_ok=False)
        for directory in (
            staging_context.cache_dir,
            staging_context.temp_dir,
            staging_context.audit_dir,
            staging_context.output_dir,
            staging_context.stages_dir,
        ):
            directory.mkdir(exist_ok=False)
        _write_json_new(
            staging_context.manifest_path,
            _run_manifest_payload(staging_context),
            staging_dir,
        )
        if run_dir.exists():
            raise FileExistsError(run_dir)
        os.rename(staging_dir, run_dir)
    except BaseException as exc:
        evidence_dir = _preserve_failed_initialization(
            staging_dir,
            run_id=run_id,
            invocation_id=invocation_id,
            exc=exc,
        )
        _annotate_initialization_exception(
            exc,
            context,
            evidence_dir=evidence_dir,
        )
        raise
    return context


@dataclass
class StageSession:
    context: RunContext
    stage: str
    parameters: dict[str, Any]
    parameter_sha256: str
    target_dir: Path
    partial_dir: Path | None
    started_monotonic: float
    skipped: bool = False
    marker: dict[str, Any] | None = None

    @property
    def work_dir(self) -> Path:
        if self.partial_dir is None:
            raise RuntimeError("A skipped stage has no writable work directory")
        return self.partial_dir


def _validate_stage_name(stage: str) -> None:
    if not stage or Path(stage).name != stage or stage in {".", ".."}:
        raise ValueError("stage must be one non-empty path component")


def start_stage(
    context: RunContext,
    stage: str,
    *,
    parameters: Mapping[str, Any] | None = None,
    resume: bool = False,
) -> StageSession:
    """Start a unique stage partial or validate a completed stage marker."""

    _validate_stage_name(stage)
    stage_parameters = _jsonable(dict(parameters or {}))
    effective = {
        "run": context.parameters,
        "stage": stage_parameters,
        "source_tree_sha256": context.source_tree_sha256,
        "environment_sha256": context.environment_sha256,
    }
    signature = parameter_signature(effective)
    target = ensure_within_run(context.stages_dir / stage, context.run_dir)
    marker_path = target / STAGE_SUCCESS

    if target.exists():
        if not resume:
            raise FileExistsError(target)
        if not target.is_dir() or not marker_path.is_file():
            raise ResumeMismatchError(
                f"Resume requires a completed {STAGE_SUCCESS} marker: {target}"
            )
        marker = _load_json(marker_path)
        observed = (
            marker.get("config_sha256"),
            marker.get("parameter_sha256"),
            marker.get("source_tree_sha256"),
            marker.get("environment_sha256"),
            marker.get("stage"),
        )
        expected = (
            context.config.sha256,
            signature,
            context.source_tree_sha256,
            context.environment_sha256,
            stage,
        )
        if observed != expected:
            raise ResumeMismatchError(
                f"Stage {stage} config/parameter signature does not match"
            )
        return StageSession(
            context=context,
            stage=stage,
            parameters=stage_parameters,
            parameter_sha256=signature,
            target_dir=target,
            partial_dir=None,
            started_monotonic=time.monotonic(),
            skipped=True,
            marker=marker,
        )

    partial = unique_partial_path(target)
    partial.mkdir(parents=False, exist_ok=False)
    return StageSession(
        context=context,
        stage=stage,
        parameters=stage_parameters,
        parameter_sha256=signature,
        target_dir=target,
        partial_dir=partial,
        started_monotonic=time.monotonic(),
    )


def _validate_hash_mapping(label: str, values: Mapping[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name, digest in values.items():
        value = str(digest).lower()
        if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
            raise ValueError(f"{label}[{name!r}] is not a SHA-256 digest")
        result[str(name)] = value
    return dict(sorted(result.items()))


def complete_stage(
    session: StageSession,
    *,
    input_hashes: Mapping[str, str],
    output_hashes: Mapping[str, str],
    row_counts: Mapping[str, int],
    extra: Mapping[str, Any] | None = None,
    resources: Mapping[str, Any] | None = None,
    resource_workload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Write an auditable success marker and atomically publish the stage."""

    if session.skipped or session.partial_dir is None:
        raise RuntimeError("Cannot complete a skipped stage")
    if session.target_dir.exists():
        raise FileExistsError(session.target_dir)
    counts = {str(name): int(value) for name, value in row_counts.items()}
    if any(value < 0 for value in counts.values()):
        raise ValueError("row_counts must be non-negative")
    if resources is None:
        snapshot = process_memory_snapshot()
        normalized_resources = stage_resource_usage(snapshot, snapshot)
    else:
        normalized_resources = dict(resources)
    for key in (
        "stage_start_current_rss_bytes",
        "stage_end_current_rss_bytes",
        "process_lifetime_peak_working_set_bytes",
    ):
        value = normalized_resources.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"resources.{key} must be a non-negative integer")
    elapsed = max(0.0, time.monotonic() - session.started_monotonic)
    marker = {
        "schema_version": 1,
        "stage": session.stage,
        "status": session.context.completion_scope_status,
        "scope_profile": session.context.scope_profile,
        "completion_scope_status": session.context.completion_scope_status,
        "completed_at_utc": utc_now(),
        "config_sha256": session.context.config.sha256,
        "template_config_sha256": (
            session.context.config.template_sha256
            or session.context.config.sha256
        ),
        "effective_config_sha256": session.context.config.sha256,
        "effective_config": session.context.config.data,
        "resolved_paths": session.context.config.resolved_paths(),
        "code_frozen_runtime_constants": CODE_FROZEN_RUNTIME_CONSTANTS,
        "source_tree_sha256": session.context.source_tree_sha256,
        "source_state": session.context.source_state,
        "environment_sha256": session.context.environment_sha256,
        "environment": session.context.environment_state,
        "code_git_commit": session.context.code_git_commit,
        "parameters": {
            "run": session.context.parameters,
            "stage": session.parameters,
        },
        "parameter_sha256": session.parameter_sha256,
        "input_hashes": _validate_hash_mapping("input_hashes", input_hashes),
        "output_hashes": _validate_hash_mapping("output_hashes", output_hashes),
        "row_counts": dict(sorted(counts.items())),
        "elapsed_seconds": elapsed,
        "resources": _jsonable(normalized_resources),
        "resource_workload": _jsonable(dict(resource_workload or {})),
        "extra": _jsonable(dict(extra or {})),
    }
    marker_path = session.partial_dir / STAGE_SUCCESS
    _write_json_new(marker_path, marker, session.context.run_dir)
    if session.target_dir.exists():
        raise FileExistsError(session.target_dir)
    published_partial = session.partial_dir
    try:
        os.rename(published_partial, session.target_dir)
    except BaseException as exc:
        committed = False
        try:
            committed = (
                session.target_dir.is_dir()
                and not published_partial.exists()
                and (session.target_dir / STAGE_SUCCESS).is_file()
            )
        except BaseException:
            committed = False
        if committed:
            try:
                setattr(exc, "stage_publish_committed", True)
                setattr(exc, "stage_execution_status", "COMPLETED")
                setattr(exc, "published_stage_marker", marker)
            except (AttributeError, TypeError):
                pass
        raise
    session.partial_dir = None
    session.marker = marker
    return marker
