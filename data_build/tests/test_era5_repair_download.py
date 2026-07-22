from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts" / "python"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import download_era5_repair as repair  # noqa: E402


def test_resolve_era_root_rejects_disk_root() -> None:
    disk_root = Path.cwd().anchor
    with pytest.raises(ValueError, match="filesystem root"):
        repair._resolve_era_root(disk_root)


def test_resolve_era_root_rejects_repository_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repository = tmp_path / "worktree"
    repository.mkdir()
    (repository / ".git").write_text("gitdir: test\n", encoding="utf-8")
    monkeypatch.setattr(repair, "REPOSITORY_ROOT", repository)
    with pytest.raises(ValueError, match="outside the repository/worktree"):
        repair._resolve_era_root(str(repository / "external-looking"))


def test_existing_valid_final_is_reused_without_download_or_mutation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    era_root = tmp_path / "era"
    repair_root = era_root / "climate_stress_repair_v1"
    final = repair_root / "CN_clipped" / "ERA1980_clipped.nc"
    final.parent.mkdir(parents=True)
    original = b"existing-valid-final"
    final.write_bytes(original)

    monkeypatch.setattr(
        repair,
        "validate_annual_file",
        lambda path, year: {"path": str(path), "size_bytes": path.stat().st_size},
    )
    monkeypatch.setattr(repair, "sha256_file", lambda _path: "new-sha")

    class NoDownloadClient:
        def retrieve(self, *_args: object, **_kwargs: object) -> None:
            raise AssertionError("existing final must not trigger CDS retrieval")

    result = repair._download_one(NoDownloadClient(), repair_root, era_root, 1980)
    assert result["disposition"] == "reused_existing_valid_repair"
    assert final.read_bytes() == original


def test_exclusive_publish_rejects_concurrent_final_without_mutation(tmp_path: Path) -> None:
    attempt = tmp_path / "attempt.nc"
    final = tmp_path / "final.nc"
    attempt.write_bytes(b"new-attempt")
    final.write_bytes(b"concurrent-winner")

    with pytest.raises(FileExistsError, match="Refusing to replace"):
        repair._publish_exclusive(attempt, final)

    assert attempt.read_bytes() == b"new-attempt"
    assert final.read_bytes() == b"concurrent-winner"


def test_forced_process_exit_leaves_started_record_and_blocks_validation(
    tmp_path: Path,
) -> None:
    repair_root = tmp_path / "repair"
    code = (
        "import os,sys; "
        f"sys.path.insert(0, {str(SCRIPTS)!r}); "
        "import download_era5_repair as r; "
        f"root=r.Path({str(repair_root)!r}); "
        "attempt=root/'download_attempts'/'ERA1980_clipped.cds-download.forced.nc'; "
        "attempt.parent.mkdir(parents=True, exist_ok=True); "
        "r._start_operation_record(root,year=1980,mode='download',attempt=attempt); "
        "os._exit(17)"
    )
    completed = subprocess.run([sys.executable, "-c", code], check=False)
    assert completed.returncode == 17

    health = repair._audit_health(repair_root, (1980,))
    assert len(health["unresolved_started_leases"]) == 1
    with pytest.raises(RuntimeError, match="unresolved STARTED"):
        repair._assert_audit_ready(repair_root, (1980,))


def test_orphan_attempt_without_started_record_blocks_validation(tmp_path: Path) -> None:
    repair_root = tmp_path / "repair"
    attempt = (
        repair_root
        / "download_attempts"
        / "ERA1985_clipped.cds-download.orphan.nc"
    )
    attempt.parent.mkdir(parents=True)
    attempt.write_bytes(b"orphan")

    health = repair._audit_health(repair_root, (1985,))
    assert health["orphan_attempts"] == [str(attempt.resolve())]
    with pytest.raises(RuntimeError, match="orphan attempts"):
        repair._assert_audit_ready(repair_root, (1985,))


def test_same_year_second_process_is_rejected_and_lock_recovers(tmp_path: Path) -> None:
    repair_root = tmp_path / "repair"
    code = (
        "import sys; "
        f"sys.path.insert(0, {str(SCRIPTS)!r}); "
        "import download_era5_repair as r; "
        f"root=r.Path({str(repair_root)!r}); "
        "\nwith r._exclusive_year_lock(root, 1980):\n pass\n"
    )
    with repair._exclusive_year_lock(repair_root, 1980):
        blocked = subprocess.run(
            [sys.executable, "-c", code], check=False, capture_output=True, text=True
        )
    assert blocked.returncode != 0
    assert "already owns the ERA5 repair lock" in blocked.stderr

    with repair._exclusive_year_lock(repair_root, 1980) as lock_path:
        assert lock_path.is_file()
