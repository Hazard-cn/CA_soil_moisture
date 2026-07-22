from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import netCDF4 as nc
import numpy as np
import pandas as pd
import pytest
import yaml


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "python"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from climate_stress.config import (  # noqa: E402
    _FROZEN_V1_VALUES,
    PipelineConfig,
    load_config,
)
from climate_stress.inventory import (  # noqa: E402
    AssetSpec,
    InventoryResult,
    _validate_netcdf_axes,
    build_inventory,
    enumerate_assets,
    exact_subgrid_indices,
    fingerprint_file,
    spei_domain_covers,
    write_inventory,
)
from climate_stress.runtime import (  # noqa: E402
    PathOutsideRunError,
    ResumeMismatchError,
    RunLockError,
    atomic_output,
    complete_stage,
    ensure_within_run,
    exclusive_run_lock,
    initialize_run,
    start_stage,
)
from climate_stress_config_fixture import complete_frozen_v1_fixture  # noqa: E402


FORMAL_CONFIG = Path(__file__).resolve().parents[1] / "config" / "climate_stress_panel_v1.yaml"
FORMAL_ENV_NAMES = (
    "CLIMATE_STRESS_MANUAL_PATH",
    "PROJECT_DATA_ROOT",
    "ERA5_ROOT",
    "DAILY_TEMP_ROOT",
    "GLEAM_ROOT",
    "CHM_SPEI_ROOT",
    "PHENOLOGY_ROOT",
    "CLIMATE_STRESS_OUTPUT_ROOT",
)


def set_formal_config_environment(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    output_root: Path | None = None,
) -> None:
    values = {
        "CLIMATE_STRESS_MANUAL_PATH": tmp_path / "manual.docx",
        "PROJECT_DATA_ROOT": tmp_path / "project-data",
        "ERA5_ROOT": tmp_path / "era5",
        "DAILY_TEMP_ROOT": tmp_path / "daily-temp",
        "GLEAM_ROOT": tmp_path / "gleam",
        "CHM_SPEI_ROOT": tmp_path / "spei",
        "PHENOLOGY_ROOT": tmp_path / "phenology",
        "CLIMATE_STRESS_OUTPUT_ROOT": output_root or (tmp_path / "output"),
    }
    for name, value in values.items():
        monkeypatch.setenv(name, str(value.resolve(strict=False)))


def make_config(tmp_path: Path) -> PipelineConfig:
    data = {
        "version_id": "data-climate-stress-2010-2019-v1",
        "manual": {
            "path": str(tmp_path / "manual.docx"),
            "sha256": "0" * 64,
        },
        "inputs": {
            "v3_main": str(tmp_path / "v3_main.parquet"),
            "v3_phenowindows": str(tmp_path / "v3_pheno.parquet"),
            "era5_hourly_pattern": str(tmp_path / "era" / "ERA{year}.nc"),
            "era5_daily_validation_pattern": str(
                tmp_path / "daily" / "daily_{year}.nc"
            ),
            "gleam_pattern": str(
                tmp_path / "gleam" / "{year}" / "{layer}_{year}.nc"
            ),
            "spei_monthly_pattern": str(tmp_path / "spei" / "SPEI-{scale}.nc"),
            "spei_2w": str(tmp_path / "spei" / "SPEI-2W.nc"),
            "phenology_pattern": str(
                tmp_path / "maize" / "CHN_Maize_{stage}_{year}.tif"
            ),
        },
        "output": {"root": str(tmp_path / "output")},
        "years": {
            "target": list(range(2010, 2020)),
            "historical": list(range(1981, 2011)),
            "daily_validation": list(range(2013, 2020)),
        },
        "grid": {
            "nlat": 376,
            "nlon": 616,
            "north": 53.53,
            "west": 73.58,
            "step": 0.1,
            "expected_cells": 22180,
        },
        "phenology": {"stages": ["V3", "HE", "MA"], "windows": {}},
        "temperature": {"source_variable": "t2m"},
        "gleam": {"layers": {"SMrz": "primary", "SMs": "supplementary"}},
        "quality": {"coordinate_tolerance": 1e-8},
    }
    return PipelineConfig(
        path=tmp_path / "config.yaml",
        data=complete_frozen_v1_fixture(data, tmp_path),
        sha256="c" * 64,
    )


def test_formal_config_expands_all_environment_paths_and_hashes_resolution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_formal_config_environment(monkeypatch, tmp_path)
    first = load_config(FORMAL_CONFIG)
    assert first.template_sha256 and first.template_sha256 != first.sha256
    assert all(Path(value).is_absolute() for value in first.resolved_paths().values())
    assert first.scope_profile == "non2w-dual-severity"
    assert first.completion_scope_status == "PARTIAL_SCOPE"

    set_formal_config_environment(
        monkeypatch,
        tmp_path,
        output_root=tmp_path / "different-output",
    )
    second = load_config(FORMAL_CONFIG)
    assert second.template_sha256 == first.template_sha256
    assert second.sha256 != first.sha256


def test_formal_config_reports_every_missing_or_empty_environment_variable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in FORMAL_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(ValueError) as missing:
        load_config(FORMAL_CONFIG)
    assert all(name in str(missing.value) for name in FORMAL_ENV_NAMES)

    set_formal_config_environment(monkeypatch, tmp_path)
    monkeypatch.setenv("ERA5_ROOT", "   ")
    monkeypatch.setenv("GLEAM_ROOT", "")
    with pytest.raises(ValueError) as empty:
        load_config(FORMAL_CONFIG)
    assert "ERA5_ROOT" in str(empty.value) and "GLEAM_ROOT" in str(empty.value)


def test_config_rejects_relative_dangerous_and_repository_output_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = make_config(tmp_path).data
    path = tmp_path / "invalid-path-config.yaml"
    data["inputs"]["v3_main"] = "relative/v3.parquet"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    with pytest.raises(ValueError, match="must be absolute"):
        load_config(path)

    data = make_config(tmp_path).data
    data["output"]["root"] = str(Path.home())
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    with pytest.raises(ValueError, match="unsafe broad"):
        load_config(path)

    set_formal_config_environment(
        monkeypatch,
        tmp_path,
        output_root=FORMAL_CONFIG.parents[2],
    )
    with pytest.raises(ValueError, match="outside the repository"):
        load_config(FORMAL_CONFIG)


def _unsupported_mutation(expected):
    if isinstance(expected, bool):
        return not expected
    if isinstance(expected, int):
        return expected + 1
    if isinstance(expected, float):
        return expected + 0.125
    if isinstance(expected, str):
        return expected + "-unsupported"
    if isinstance(expected, list):
        return [*expected, "unsupported"]
    raise TypeError(type(expected))


@pytest.mark.parametrize(
    ("key_path", "expected"),
    list(_FROZEN_V1_VALUES.items()),
    ids=lambda value: ".".join(value) if isinstance(value, tuple) else None,
)
def test_every_code_frozen_v1_method_mutation_fails_closed(
    tmp_path: Path,
    key_path: tuple[str, ...],
    expected,
) -> None:
    data = make_config(tmp_path).data
    current = data
    for component in key_path[:-1]:
        current = current[component]
    current[key_path[-1]] = _unsupported_mutation(expected)
    path = tmp_path / "mutated-config.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    with pytest.raises(ValueError, match="code-frozen"):
        load_config(path)


@pytest.mark.parametrize(
    "key",
    ["era_time_chunk_hours", "gleam_time_chunk_days", "compute_dtype"],
)
def test_unsupported_runtime_claims_are_rejected(tmp_path: Path, key: str) -> None:
    data = make_config(tmp_path).data
    data["runtime"][key] = 24 if "dtype" not in key else "float64"
    path = tmp_path / "unsupported-runtime.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    with pytest.raises(ValueError, match="must be absent"):
        load_config(path)


def _write_inventory_era(path: Path, axis_year: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    start = np.datetime64(f"{int(axis_year):04d}-01-01T00", "h")
    end = np.datetime64(f"{int(axis_year) + 1:04d}-01-01T00", "h")
    hours = np.arange(start, end, np.timedelta64(1, "h"))
    epoch = np.datetime64("1970-01-01T00", "h")
    with nc.Dataset(path, "w") as dataset:
        dataset.createDimension("valid_time", len(hours))
        dataset.createDimension("latitude", 2)
        dataset.createDimension("longitude", 2)
        time = dataset.createVariable("valid_time", "f8", ("valid_time",))
        time.units = "hours since 1970-01-01 00:00:00"
        time.calendar = "standard"
        time[:] = ((hours - epoch) / np.timedelta64(1, "h")).astype(np.float64)
        latitude = dataset.createVariable("latitude", "f8", ("latitude",))
        longitude = dataset.createVariable("longitude", "f8", ("longitude",))
        latitude[:] = [53.53, 53.43]
        longitude[:] = [73.58, 73.68]
        dataset.createVariable(
            "t2m", "f4", ("valid_time", "latitude", "longitude")
        )


def test_initialize_run_is_non_overwriting_and_confines_all_state(
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    context = initialize_run(
        config,
        run_id="run-001",
        parameters={"pilot": True},
        repo_root=tmp_path,
    )
    for directory in (
        context.cache_dir,
        context.temp_dir,
        context.audit_dir,
        context.output_dir,
        context.stages_dir,
    ):
        assert directory.is_dir()
        assert directory.is_relative_to(context.run_dir)
    manifest = json.loads(context.manifest_path.read_text(encoding="utf-8"))
    assert manifest["config_sha256"] == config.sha256
    assert manifest["parameter_sha256"] == context.parameter_sha256
    with pytest.raises(FileExistsError):
        initialize_run(config, run_id="run-001", parameters={"pilot": True})


def test_run_resume_requires_matching_config_and_parameters(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    original = initialize_run(config, run_id="run-001", parameters={"limit": 100})
    resumed = initialize_run(
        config, run_id="run-001", parameters={"limit": 100}, resume=True
    )
    assert resumed.run_dir == original.run_dir
    with pytest.raises(ResumeMismatchError):
        initialize_run(
            config, run_id="run-001", parameters={"limit": 101}, resume=True
        )
    changed_config = PipelineConfig(
        path=config.path, data=config.data, sha256="d" * 64
    )
    with pytest.raises(ResumeMismatchError):
        initialize_run(
            changed_config,
            run_id="run-001",
            parameters={"limit": 100},
            resume=True,
        )


def test_initialize_interruption_preserves_incomplete_and_allows_safe_retry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import climate_stress.runtime as runtime

    config = make_config(tmp_path)
    real_write = runtime._write_json_new

    def interrupted_write(target, payload, run_dir):
        if target.name == "_RUN.json":
            raise RuntimeError("simulated initialization interruption")
        return real_write(target, payload, run_dir)

    monkeypatch.setattr(runtime, "_write_json_new", interrupted_write)
    with pytest.raises(RuntimeError, match="initialization interruption"):
        initialize_run(config, run_id="atomic-init")
    assert not (config.output_root / "atomic-init").exists()
    incomplete = list(config.output_root.glob(".atomic-init.*.initializing.incomplete"))
    assert len(incomplete) == 1
    evidence = list(incomplete[0].glob("_INITIALIZATION_FAILED.*.json"))
    assert len(evidence) == 1
    preserved = evidence[0].read_bytes()

    monkeypatch.setattr(runtime, "_write_json_new", real_write)
    context = initialize_run(config, run_id="atomic-init", resume=True)
    assert context.manifest_path.is_file()
    assert incomplete[0].is_dir()
    assert evidence[0].read_bytes() == preserved


def test_run_lock_records_owner_rejects_competitor_and_preserves_audits(
    tmp_path: Path,
) -> None:
    root = tmp_path / "locks"
    with exclusive_run_lock(root, "concurrent-run") as first:
        lock_size = first.path.stat().st_size
        acquired = list(
            (root / ".run-locks").glob(
                f"concurrent-run.acquired.{first.lease_id}.json"
            )
        )
        assert len(acquired) == 1
        owner = json.loads(acquired[0].read_text(encoding="utf-8"))
        assert owner["run_id"] == "concurrent-run"
        assert owner["lease_id"] == first.lease_id
        assert owner["pid"] == os.getpid()
        assert owner["owner"] and owner["hostname"] and owner["acquired_at_utc"]
        with pytest.raises(RunLockError, match="Concurrent execution was rejected"):
            with exclusive_run_lock(root, "concurrent-run"):
                pass
        assert first.path.stat().st_size == lock_size
    released = list(
        (root / ".run-locks").glob(
            f"concurrent-run.released.{first.lease_id}.json"
        )
    )
    assert len(released) == 1
    with pytest.raises(RuntimeError, match="simulated owner failure"):
        with exclusive_run_lock(root, "concurrent-run"):
            raise RuntimeError("simulated owner failure")
    with exclusive_run_lock(root, "concurrent-run") as recovered:
        assert recovered.lease_id != first.lease_id


def test_process_crash_releases_os_lock_without_deleting_persistent_file(
    tmp_path: Path,
) -> None:
    root = tmp_path / "crash-lock"
    code = (
        "import os,sys; from climate_stress.runtime import exclusive_run_lock; "
        "lock=exclusive_run_lock(sys.argv[1], 'crash-run'); "
        "lease=lock.__enter__(); os._exit(23)"
    )
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SCRIPT_DIR)
    completed = subprocess.run(
        [sys.executable, "-c", code, str(root)],
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 23
    persistent = root / ".run-locks" / "crash-run.lock"
    assert persistent.is_file()
    with exclusive_run_lock(root, "crash-run") as recovered:
        assert recovered.metadata["pid"] == os.getpid()
    assert persistent.is_file()


def test_atomic_output_never_overwrites_and_preserves_failed_partial(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    target = run_dir / "output" / "panel.parquet"
    with pytest.raises(RuntimeError):
        with atomic_output(target, run_dir) as partial:
            partial.write_bytes(b"incomplete")
            raise RuntimeError("simulated failure")
    partials = list(target.parent.glob("*.partial"))
    assert len(partials) == 1
    assert partials[0].read_bytes() == b"incomplete"
    target.write_bytes(b"existing")
    with pytest.raises(FileExistsError):
        with atomic_output(target, run_dir):
            pass
    assert target.read_bytes() == b"existing"
    assert partials[0].exists()


def test_runtime_rejects_mutable_paths_outside_run(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    assert ensure_within_run(run_dir / "audit" / "x.json", run_dir).is_relative_to(
        run_dir
    )
    with pytest.raises(PathOutsideRunError):
        ensure_within_run(tmp_path / "outside.json", run_dir)
    with pytest.raises(PathOutsideRunError):
        ensure_within_run(run_dir, run_dir)


def test_stage_marker_contains_required_evidence_and_resumes_exactly(
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    context = initialize_run(config, run_id="run-001", parameters={"pilot": True})
    session = start_stage(context, "inventory", parameters={"hash_mode": "pilot"})
    assert session.work_dir.name.endswith(".partial")
    (session.work_dir / "stage-note.txt").write_text("complete", encoding="utf-8")
    marker = complete_stage(
        session,
        input_hashes={"config": "a" * 64},
        output_hashes={"inventory": "b" * 64},
        row_counts={"assets": 172},
        extra={"hash_mode": "pilot"},
    )
    assert marker["config_sha256"] == config.sha256
    assert marker["code_git_commit"]
    assert marker["parameters"]["stage"] == {"hash_mode": "pilot"}
    assert marker["input_hashes"] == {"config": "a" * 64}
    assert marker["output_hashes"] == {"inventory": "b" * 64}
    assert marker["row_counts"] == {"assets": 172}
    assert marker["elapsed_seconds"] >= 0
    success = context.stages_dir / "inventory" / "_SUCCESS.json"
    assert success.is_file()
    resumed = start_stage(
        context,
        "inventory",
        parameters={"hash_mode": "pilot"},
        resume=True,
    )
    assert resumed.skipped
    with pytest.raises(ResumeMismatchError):
        start_stage(
            context,
            "inventory",
            parameters={"hash_mode": "full"},
            resume=True,
        )


def test_stage_resume_rejects_directory_without_success_marker(tmp_path: Path) -> None:
    context = initialize_run(make_config(tmp_path), run_id="run-001")
    (context.stages_dir / "broken").mkdir()
    with pytest.raises(ResumeMismatchError):
        start_stage(context, "broken", resume=True)


def test_inventory_enumerates_frozen_asset_universe(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    repair = tmp_path / "repair" / "ERA1985.nc"
    config.data["inputs"]["era5_hourly_overrides"] = {1985: str(repair)}
    specs = enumerate_assets(config)
    assert len(specs) == 174
    by_family: dict[str, list] = {}
    for spec in specs:
        by_family.setdefault(spec.family, []).append(spec)
    assert len(by_family["era5_hourly"]) == 41
    assert {spec.year for spec in by_family["era5_hourly"]} == set(
        range(1980, 2021)
    )
    era_by_year = {spec.year: spec for spec in by_family["era5_hourly"]}
    assert era_by_year[1985].path == repair
    assert era_by_year[1984].path == tmp_path / "era" / "ERA1984.nc"
    assert len(by_family["era5_daily_validation"]) == 7
    assert len(by_family["gleam"]) == 80
    assert {spec.year for spec in by_family["gleam"]} == set(range(1981, 2021))
    assert len(by_family["spei_monthly"]) == 12
    assert len(by_family["phenology"]) == 30
    assert all(spec.path.parent.name == "maize" for spec in by_family["phenology"])
    two_week = by_family["spei_2w"][0]
    assert two_week.timestamp_semantics == "unresolved"
    assert "disabled" in two_week.role


@pytest.mark.parametrize("mode", ["representative", "all"])
def test_inventory_scans_every_era_year_and_lists_all_misdated_files(
    tmp_path: Path,
    mode: str,
) -> None:
    wrong_axis_year = {1980: 2001, 1985: 2002, 1986: 2003}
    specs: list[AssetSpec] = []
    for year in range(1980, 2021):
        path = tmp_path / "era" / f"ERA{year}.nc"
        _write_inventory_era(path, wrong_axis_year.get(year, year))
        specs.append(
            AssetSpec(
                asset_id=f"era5.hourly.{year}",
                family="era5_hourly",
                path=path,
                role="historical/target temperature plus UTC+8 boundary",
                year=year,
                variable="t2m",
            )
        )

    checks, _axes = _validate_netcdf_axes(
        make_config(tmp_path),
        specs,
        mode=mode,
    )
    time_check = next(
        item for item in checks if item["check_id"] == "era5.hourly_time_axis"
    )
    assert time_check["status"] == "fail"
    assert time_check["evidence"]["inspected_years"] == list(range(1980, 2021))
    assert time_check["evidence"]["failed_years"] == [1980, 1985, 1986]
    errors = "\n".join(time_check["evidence"]["errors"])
    for year in (1980, 1985, 1986):
        assert f"era5.hourly.{year}" in errors
        assert f"filename year {year}" in errors


def test_pilot_fingerprint_samples_large_file_and_full_mode_hashes_all(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.bin"
    source.write_bytes(b"0123456789abcdef")
    pilot = fingerprint_file(source, mode="pilot", sample_bytes=4)
    full = fingerprint_file(source, mode="full", sample_bytes=4)
    assert not pilot.hash_is_full
    assert pilot.hash_algorithm == "sha256-size-head-tail-v1"
    assert full.hash_is_full
    assert full.sha256 == hashlib.sha256(source.read_bytes()).hexdigest()
    assert pilot.sha256 != full.sha256


def test_small_pilot_asset_receives_true_full_hash(tmp_path: Path) -> None:
    source = tmp_path / "small.bin"
    source.write_bytes(b"small")
    result = fingerprint_file(source, mode="pilot", sample_bytes=4)
    assert result.hash_is_full
    assert result.sha256 == hashlib.sha256(b"small").hexdigest()


def test_exact_subgrid_and_spei_selected_domain_helpers() -> None:
    source = [54.0, 53.9, 53.8, 53.7, 53.6, 53.5, 53.4]
    indices = exact_subgrid_indices(
        source, [53.7, 53.6, 53.5], tolerance=1e-9
    )
    assert indices.tolist() == [3, 4, 5]
    with pytest.raises(ValueError):
        exact_subgrid_indices(source, [53.75], tolerance=1e-9)
    assert spei_domain_covers(
        [18.05, 53.95],
        [72.05, 135.95],
        [21.73, 51.13],
        [75.58, 134.58],
        tolerance=1e-8,
    )
    assert not spei_domain_covers(
        [18.05, 53.95],
        [72.05, 135.95],
        [16.03, 53.53],
        [73.58, 135.08],
        tolerance=1e-8,
    )


def test_inventory_marks_2w_semantics_blocked_without_interpreting_it(
    tmp_path: Path,
) -> None:
    result = build_inventory(
        make_config(tmp_path), hash_mode="pilot", inspect_axes=False
    )
    check = next(
        item
        for item in result.checks
        if item["check_id"] == "spei_2w.timestamp_semantics"
    )
    assert check["status"] == "blocked"
    assert check["evidence"]["timestamp_semantics"] == "unresolved"
    assert check["evidence"]["event_construction_allowed"] is False
    assert check["evidence"]["blocking_scope"] == "spei_2w_only"
    assert check["evidence"]["numeric_executed"] is False
    assert check["evidence"]["excluded_from_output_contract"] is True
    assert result.metadata["spei_2w_timestamp_semantics"] == "unresolved"
    assert result.blocked
    assert not result.pipeline_blocked


def test_inventory_json_and_parquet_are_non_overwriting(tmp_path: Path) -> None:
    records = pd.DataFrame(
        [
            {
                "asset_id": "test.asset",
                "family": "test",
                "exists": True,
                "size_bytes": 4,
            }
        ]
    )
    result = InventoryResult(
        records=records,
        checks=[{"check_id": "test", "status": "pass", "detail": "ok"}],
        metadata={"spei_2w_timestamp_semantics": "unresolved"},
    )
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    json_path, parquet_path = write_inventory(result, run_dir)
    assert json_path.is_file() and parquet_path.is_file()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["summary"]["asset_count"] == 1
    assert pd.read_parquet(parquet_path).iloc[0]["asset_id"] == "test.asset"
    with pytest.raises(FileExistsError):
        write_inventory(result, run_dir)
