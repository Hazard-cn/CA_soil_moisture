from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts" / "python"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import fetch_gleam43a_year as fetch  # noqa: E402


def _remote(layer: str = "SMrz", *, size: int = 4) -> dict[str, object]:
    name = f"{layer}_2020_GLEAM_v4.3a.nc"
    return {
        "layer": layer,
        "logical_path": f"{fetch.OFFICIAL_REMOTE_ROOT}/2020/{name}",
        "name": name,
        "size_bytes": size,
        "mtime": "2026-05-14T19:07:01+08:00",
        "lsjson": {"Name": name, "Size": size, "IsDir": False},
    }


def test_resolve_gleam_root_rejects_disk_root() -> None:
    with pytest.raises(ValueError, match="filesystem root"):
        fetch.resolve_gleam_root(Path.cwd().anchor)


def test_resolve_gleam_root_rejects_repository_and_git_ancestor(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repository = tmp_path / "worktree"
    repository.mkdir()
    (repository / ".git").write_text("gitdir: test\n", encoding="utf-8")
    monkeypatch.setattr(fetch, "REPOSITORY_ROOT", repository)
    with pytest.raises(ValueError, match="outside the repository"):
        fetch.resolve_gleam_root(str(repository / "input"))

    other = tmp_path / "other-repository"
    other.mkdir()
    (other / ".git").mkdir()
    with pytest.raises(ValueError, match="any Git repository"):
        fetch.resolve_gleam_root(str(other / "input"))


def test_dry_run_has_no_network_or_filesystem_writes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / "not-created"
    monkeypatch.setattr(
        fetch,
        "query_remote_listing",
        lambda _year: (_ for _ in ()).throw(AssertionError("network used")),
    )
    args = argparse.Namespace(
        gleam_root=str(root), year=2020, mode="download", dry_run=True
    )
    assert fetch.run(args) == 0
    assert not root.exists()


def test_existing_same_size_bad_structure_is_not_accepted(tmp_path: Path) -> None:
    root = tmp_path / "gleam"
    final = root / "2020" / "SMrz_2020_GLEAM_v4.3a.nc"
    final.parent.mkdir(parents=True)
    final.write_bytes(b"bad!")

    with pytest.raises(OSError):
        fetch._download_one(
            root,
            layer="SMrz",
            year=2020,
            remote=_remote(size=final.stat().st_size),
        )
    assert final.read_bytes() == b"bad!"


def test_failed_attempt_is_retained_without_final_publish(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / "gleam"
    monkeypatch.setattr(
        fetch.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=7),
    )

    with pytest.raises(RuntimeError, match="rclone download failed"):
        fetch._download_one(
            root,
            layer="SMrz",
            year=2020,
            remote=_remote(),
        )
    assert not (root / "2020" / "SMrz_2020_GLEAM_v4.3a.nc").exists()
    assert (root / "climate_stress_repair_v1" / "download_attempts").is_dir()


def test_concurrent_final_is_never_replaced_and_attempt_is_retained(
    tmp_path: Path,
) -> None:
    attempt = tmp_path / "attempt.nc"
    final = tmp_path / "2020" / "final.nc"
    attempt.write_bytes(b"validated-attempt")
    final.parent.mkdir()
    final.write_bytes(b"concurrent-winner")

    with pytest.raises(FileExistsError, match="Refusing to replace"):
        fetch._publish_exclusive(attempt, final)
    assert attempt.read_bytes() == b"validated-attempt"
    assert final.read_bytes() == b"concurrent-winner"


def test_successful_attempt_is_validated_then_hardlink_published(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / "gleam"
    payload = b"valid-netcdf-placeholder"
    remote = _remote(size=len(payload))

    def fake_run(command: list[str], **_kwargs: object) -> SimpleNamespace:
        attempt = Path(command[3])
        attempt.write_bytes(payload)
        log = Path(command[command.index("--log-file") + 1])
        log.write_text("Copied (new)\n", encoding="utf-8")
        return SimpleNamespace(returncode=0)

    def fake_validate(path: Path, *, layer: str, year: int) -> dict[str, object]:
        assert layer == "SMrz" and year == 2020
        assert path.read_bytes() == payload
        return {
            "path": str(path),
            "layer": layer,
            "year": year,
            "size_bytes": path.stat().st_size,
            "sha256": "A" * 64,
        }

    monkeypatch.setattr(fetch.subprocess, "run", fake_run)
    monkeypatch.setattr(fetch, "validate_file", fake_validate)
    result = fetch._download_one(
        root, layer="SMrz", year=2020, remote=remote
    )

    final = root / "2020" / str(remote["name"])
    attempt = Path(str(result["immutable_download_attempt"]))
    assert final.read_bytes() == payload
    assert attempt.read_bytes() == payload
    assert result["disposition"] == (
        "downloaded_validated_then_exclusively_hardlink_published"
    )


def test_audit_is_exclusive_and_sanitized_endpoint_omits_credentials(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    audit = tmp_path / "meta" / "audit.json"
    fetch._write_audit_exclusive(audit, {"status": "SUCCESS"})
    with pytest.raises(FileExistsError):
        fetch._write_audit_exclusive(audit, {"status": "REPLACED"})

    config = """[gleam43a]
type = sftp
host = aether.ugent.be
user = secret-user
port = 2225
pass = obscured-secret
"""
    monkeypatch.setattr(
        fetch.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0, stdout=config, stderr=""
        ),
    )
    identity = fetch.query_sanitized_remote_identity()
    assert identity == {
        "rclone_alias": "gleam43a:",
        "backend": "sftp",
        "host": "aether.ugent.be",
        "port": 2225,
        "credentials_recorded": False,
    }
    serialized = repr(identity).lower()
    assert "secret-user" not in serialized and "obscured-secret" not in serialized
