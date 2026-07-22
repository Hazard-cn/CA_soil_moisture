from __future__ import annotations

import io
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "python"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from climate_stress.config import load_config  # noqa: E402
from climate_stress.pipeline import (  # noqa: E402
    STAGE_ORDER,
    ClimateStressPipeline,
    ExecutionScope,
    StageOutcome,
    StageValidationError,
    _add_hot_flash_window_metrics,
    _contiguous_year_groups,
    _event_partition_years,
    _read_v3_legacy_projection,
    _read_v3_validation_projection,
    _validate_spei_2w_event_row_counts,
    build_parser,
    default_handlers,
    dependency_closure,
    main,
    parse_years,
    resolve_scope,
)
from climate_stress.runtime import exclusive_run_lock, initialize_run  # noqa: E402
from climate_stress_config_fixture import complete_frozen_v1_fixture  # noqa: E402


def write_config(tmp_path: Path) -> Path:
    path = tmp_path / "config.yaml"
    data = {
        "version_id": "data-climate-stress-2010-2019-v1",
        "inputs": {"v3_main": str(tmp_path / "v3.parquet")},
        "output": {"root": str(tmp_path / "output")},
        "years": {
            "target": list(range(2010, 2020)),
            "historical": list(range(1981, 2011)),
            "daily_validation": list(range(2013, 2020)),
        },
        "grid": {
            "expected_cells": 22180,
            "v3_coordinate_tolerance_degrees": 2.5e-5,
        },
        "phenology": {"windows": {"full": {}}},
        "quality": {
            "pilot_grid_limit": 100,
            "pilot_years": [2010, 2016, 2019],
        },
    }
    data = complete_frozen_v1_fixture(data, tmp_path)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


class RecordingHandlers:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def handler(self, request) -> StageOutcome:
        self.calls.append(request.stage)
        artifact = request.work_dir / f"{request.stage}.txt"
        artifact.write_text(request.stage, encoding="utf-8")
        return StageOutcome(
            artifacts={"artifact": artifact},
            row_counts={"rows": 1},
            extra={"mock": True},
        )

    def mapping(self):
        return {stage: self.handler for stage in STAGE_ORDER}


def test_year_parser_supports_lists_and_inclusive_ranges() -> None:
    assert parse_years("2010,2012-2014,2019") == (2010, 2012, 2013, 2014, 2019)
    with pytest.raises(Exception):
        parse_years("2014-2012")
    with pytest.raises(Exception):
        parse_years("2010,2010")


def test_two_week_event_count_audit_is_bounded_and_rejects_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = tmp_path / "events.parquet"
    bridges = tmp_path / "bridges.parquet"
    timescales = ["2W" if index % 3 == 0 else "1M" for index in range(101)]
    pd.DataFrame({"timescale": timescales}).to_parquet(events, index=False)
    pd.DataFrame({"timescale": timescales[:40]}).to_parquet(bridges, index=False)
    monkeypatch.setattr(
        pd,
        "read_parquet",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("bounded audit must not call pandas.read_parquet")
        ),
    )
    observed = _validate_spei_2w_event_row_counts(
        {"event_rows": 34, "bridge_rows": 14},
        events,
        bridges,
        batch_size=13,
    )
    assert observed[:2] == (34, 14)
    assert observed[2] <= 13 and observed[3] <= 13
    with pytest.raises(StageValidationError, match="event rows differ"):
        _validate_spei_2w_event_row_counts(
            {"event_rows": 33, "bridge_rows": 14},
            events,
            bridges,
            batch_size=13,
        )
    with pytest.raises(StageValidationError, match="bridge rows differ"):
        _validate_spei_2w_event_row_counts(
            {"event_rows": 34, "bridge_rows": 13},
            events,
            bridges,
            batch_size=13,
        )


def test_cli_parser_exposes_all_frozen_arguments() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "--config",
            "config.yaml",
            "--stage",
            "era_daily",
            "--run-id",
            "run-1",
            "--resume",
            "--pilot-cells",
            "100",
            "--years",
            "2010,2016,2019",
            "--hash-mode",
            "pilot",
        ]
    )
    assert args.stage == "era_daily"
    assert args.resume and args.pilot_cells == 100
    assert args.years == (2010, 2016, 2019)


def test_scope_freezes_pilot_and_full_boundaries(tmp_path: Path) -> None:
    config = load_config(write_config(tmp_path))
    pilot = resolve_scope(
        config,
        pilot_cells=100,
        years=(2010, 2016, 2019),
        hash_mode=None,
    )
    assert pilot == ExecutionScope("pilot", (2010, 2016, 2019), 100, "pilot")
    full = resolve_scope(config, pilot_cells=None, years=None, hash_mode=None)
    assert full.mode == "full" and full.years == tuple(range(2010, 2020))
    assert full.hash_mode == "full"
    with pytest.raises(ValueError, match="frozen at 100"):
        resolve_scope(config, pilot_cells=10, years=None, hash_mode="pilot")
    with pytest.raises(ValueError, match="Pilot years"):
        resolve_scope(
            config, pilot_cells=100, years=(2010,), hash_mode="pilot"
        )


def test_dependency_closure_is_deterministic_and_explicit() -> None:
    assert dependency_closure("era_baseline") == (
        "assets",
        "grid",
        "era_daily",
        "era_baseline",
    )
    assert dependency_closure("events") == (
        "assets",
        "grid",
        "phenology",
        "era_daily",
        "era_baseline",
        "spei",
        "gleam_daily",
        "gleam_baseline",
        "events",
    )
    assert dependency_closure("all") == STAGE_ORDER
    assert _contiguous_year_groups((2010, 2016, 2019)) == (
        (2010,),
        (2016,),
        (2019,),
    )
    assert _contiguous_year_groups((2010, 2011, 2013, 2014, 2015)) == (
        (2010, 2011),
        (2013, 2014, 2015),
    )


def test_complete_event_start_year_and_bridge_window_year_are_distinct() -> None:
    event = pd.DataFrame(
        {
            "event_id": ["1:test:0001"],
            "start_date": [date(2015, 12, 30)],
            "event_start_year": [2015],
            "first_target_overlap_year": [2016],
        }
    )
    bridge = pd.DataFrame(
        {
            "event_id": ["1:test:0001"],
            "year": [2016],
            "window": ["full"],
        }
    )
    assert _event_partition_years(event, audit_kind="event").tolist() == [2015]
    assert _event_partition_years(bridge, audit_kind="bridge").tolist() == [2016]
    assert len(event) == 1 and event["event_id"].is_unique


def test_v3_validation_projection_never_reads_unrelated_columns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy_fields = [f"legacy_spei_{index:02d}" for index in range(12)]
    source = pd.DataFrame(
        {
            "grid_id": [101],
            "year": [2019],
            "latitude": [53.53],
            "longitude": [73.58],
            **{name: [-0.1] for name in legacy_fields},
            **{f"unrelated_{index:03d}": [index] for index in range(100)},
        }
    )
    source_path = tmp_path / "v3-wide-source.parquet"
    source.to_parquet(source_path, index=False)
    real_read_parquet = pd.read_parquet
    observed_columns: list[list[str] | None] = []

    def recording_read_parquet(path, *args, **kwargs):
        if Path(path) == source_path:
            columns = kwargs.get("columns")
            observed_columns.append(None if columns is None else list(columns))
        return real_read_parquet(path, *args, **kwargs)

    monkeypatch.setattr(pd, "read_parquet", recording_read_parquet)
    projected = _read_v3_validation_projection(source_path, legacy_fields)

    expected = [
        "grid_id",
        "year",
        "latitude",
        "longitude",
        *legacy_fields,
    ]
    assert observed_columns == [expected]
    assert projected.columns.tolist() == expected


def test_v3_legacy_projection_forbids_full_table_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    windows = ("full", "v3pre30", "v3pm10", "hepm10", "v3he", "hema")
    field_map = {
        window: (f"legacy_{index:02d}_mean", f"legacy_{index:02d}_max")
        for index, window in enumerate(windows)
    }
    source_data: dict[str, list[object]] = {
        "grid_id": [101],
        "year": [2019],
        "latitude": [53.53],
        "longitude": [73.58],
    }
    for window, fields in field_map.items():
        source_data[f"win_{window}_start"] = [100]
        source_data[f"win_{window}_end"] = [150]
        source_data[fields[0]] = [-0.1]
        source_data[fields[1]] = [-0.1]
    source_data.update(
        {f"unrelated_{index:03d}": [index] for index in range(100)}
    )
    source_path = tmp_path / "v3-legacy-wide-source.parquet"
    pd.DataFrame(source_data).to_parquet(source_path, index=False)
    real_read_parquet = pd.read_parquet
    observed_columns: list[list[str] | None] = []

    def recording_read_parquet(path, *args, **kwargs):
        if Path(path) == source_path:
            columns = kwargs.get("columns")
            observed_columns.append(None if columns is None else list(columns))
            if columns is None:
                raise AssertionError("Full V3 table reads are forbidden")
        return real_read_parquet(path, *args, **kwargs)

    monkeypatch.setattr(pd, "read_parquet", recording_read_parquet)
    projected, grid_name = _read_v3_legacy_projection(source_path, field_map)

    assert grid_name == "grid_id"
    assert observed_columns == [projected.columns.tolist()]
    assert not any(name.startswith("unrelated_") for name in projected.columns)
    assert len(projected.columns) == 28


def test_grid_stage_records_configured_v3_tolerance_and_residuals(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = load_config(write_config(tmp_path))
    scope = resolve_scope(config, pilot_cells=100, years=None, hash_mode="pilot")
    context = initialize_run(
        config,
        run_id="grid-tolerance-run",
        parameters=scope.as_parameters(),
        repo_root=tmp_path,
    )
    positions = np.arange(100, dtype=np.int32)
    fake = pd.DataFrame(
        {
            "grid_id_v3": positions + 1,
            "era01_cell_id": positions + 1,
            "lat_idx": np.zeros(100, dtype=np.int32),
            "lon_idx": positions,
            "latitude": np.full(100, 53.53),
            "longitude": 73.58 + positions * 0.1,
            "lat10": np.full(100, 535, dtype=np.int32),
            "lon10": np.floor((73.58 + positions * 0.1) * 10 + 0.5).astype(np.int32),
            "v3_lat_err_abs_deg": np.linspace(0, 2.0e-5, 100),
            "v3_lon_err_abs_deg": np.linspace(0, 2.4e-5, 100),
        }
    )
    observed: dict[str, float] = {}

    def fake_crosswalk(_source, **kwargs):
        observed["tolerance"] = kwargs["input_coordinate_tolerance"]
        return fake.copy()

    monkeypatch.setattr("climate_stress.grid.build_v3_crosswalk", fake_crosswalk)

    def assets(request) -> StageOutcome:
        artifact = request.work_dir / "inventory.json"
        artifact.write_text("{}", encoding="utf-8")
        return StageOutcome(artifacts={"inventory": artifact})

    handlers = default_handlers()
    handlers["assets"] = assets
    pipeline = ClimateStressPipeline(config, context, scope, handlers=handlers)
    pipeline.run("grid")
    selection = json.loads(
        (context.stages_dir / "grid" / "selection.json").read_text(encoding="utf-8")
    )
    evidence = selection["v3_coordinate_alignment"]
    assert observed["tolerance"] == pytest.approx(2.5e-5)
    assert evidence["full_max_v3_lat_err_abs_deg"] == pytest.approx(2.0e-5)
    assert evidence["full_max_v3_lon_err_abs_deg"] == pytest.approx(2.4e-5)
    marker = json.loads(
        (context.stages_dir / "grid" / "_SUCCESS.json").read_text(encoding="utf-8")
    )
    assert marker["extra"]["v3_coordinate_alignment"] == evidence


def test_mock_pipeline_stage_writes_markers_hashes_and_rows_inside_run(
    tmp_path: Path,
) -> None:
    config = load_config(write_config(tmp_path))
    scope = resolve_scope(
        config, pilot_cells=100, years=None, hash_mode="pilot"
    )
    context = initialize_run(
        config,
        run_id="mock-run",
        parameters=scope.as_parameters(),
        repo_root=tmp_path,
    )
    recorder = RecordingHandlers()
    pipeline = ClimateStressPipeline(
        config,
        context,
        scope,
        handlers=recorder.mapping(),
    )
    results = pipeline.run("era_baseline")
    assert recorder.calls == ["assets", "grid", "era_daily", "era_baseline"]
    assert [result["status"] for result in results] == ["COMPLETED"] * 4
    for stage in recorder.calls:
        marker_path = context.stages_dir / stage / "_SUCCESS.json"
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
        assert marker["config_sha256"] == config.sha256
        assert marker["row_counts"] == {"rows": 1}
        assert "artifact" in marker["output_hashes"]
        assert marker["parameters"]["stage"]["random_seed"] == 42
        assert (context.stages_dir / stage / f"{stage}.txt").is_file()
    assert not list(context.stages_dir.glob("*/**/*.partial"))


def test_cli_resume_skips_matching_success_markers_without_rerun(
    tmp_path: Path,
) -> None:
    config_path = write_config(tmp_path)
    recorder = RecordingHandlers()
    stdout = io.StringIO()
    stderr = io.StringIO()
    arguments = [
        "--config",
        str(config_path),
        "--stage",
        "grid",
        "--run-id",
        "resume-run",
        "--pilot-cells",
        "100",
        "--hash-mode",
        "pilot",
    ]
    assert main(
        arguments,
        handlers=recorder.mapping(),
        stdout=stdout,
        stderr=stderr,
    ) == 0
    assert recorder.calls == ["assets", "grid"]
    stdout.seek(0)
    stdout.truncate(0)
    assert main(
        [*arguments, "--resume"],
        handlers=recorder.mapping(),
        stdout=stdout,
        stderr=stderr,
    ) == 0
    assert recorder.calls == ["assets", "grid"]
    payload = json.loads(stdout.getvalue())
    assert [item["status"] for item in payload["executed_stages"]] == [
        "SKIPPED_SUCCESS_MARKER",
        "SKIPPED_SUCCESS_MARKER",
    ]


def test_resume_rejects_external_raw_source_changed_after_assets(
    tmp_path: Path,
) -> None:
    from climate_stress.inventory import fingerprint_file

    config = load_config(write_config(tmp_path))
    scope = resolve_scope(
        config, pilot_cells=100, years=None, hash_mode="pilot"
    )
    raw = tmp_path / "external_raw.bin"
    raw.write_bytes(b"original")

    def assets(request) -> StageOutcome:
        fingerprint = fingerprint_file(raw, mode="pilot")
        record = {
            "asset_id": "test.raw",
            "family": "test",
            "role": "resume mutation fixture",
            "path": str(raw),
            "exists": True,
            "size_bytes": fingerprint.size_bytes,
            "mtime_utc": fingerprint.mtime_utc,
            "sha256": fingerprint.sha256,
            "hash_algorithm": fingerprint.hash_algorithm,
            "hash_is_full": fingerprint.hash_is_full,
        }
        destination = request.work_dir / "audit" / "inventory"
        destination.mkdir(parents=True)
        parquet = destination / "source_inventory.parquet"
        json_path = destination / "source_inventory.json"
        pd.DataFrame([record]).to_parquet(parquet, index=False)
        json_path.write_text(json.dumps({"records": [record]}), encoding="utf-8")
        return StageOutcome(
            artifacts={"inventory_json": json_path, "inventory_parquet": parquet},
            row_counts={"assets": 1},
        )

    recorder = RecordingHandlers()
    handlers = recorder.mapping()
    handlers["assets"] = assets
    context = initialize_run(
        config,
        run_id="raw-mutation-run",
        parameters=scope.as_parameters(),
        repo_root=tmp_path,
    )
    ClimateStressPipeline(config, context, scope, handlers=handlers).run("grid")
    raw.write_bytes(b"changed!")

    resumed_context = initialize_run(
        config,
        run_id="raw-mutation-run",
        parameters=scope.as_parameters(),
        resume=True,
        repo_root=tmp_path,
    )
    with pytest.raises(Exception, match="raw source fingerprint mismatch"):
        ClimateStressPipeline(
            config,
            resumed_context,
            scope,
            handlers=handlers,
            resume=True,
        ).run("grid")


def test_resume_rehashes_completed_artifacts_before_skip(tmp_path: Path) -> None:
    config_path = write_config(tmp_path)
    recorder = RecordingHandlers()
    arguments = [
        "--config",
        str(config_path),
        "--stage",
        "assets",
        "--run-id",
        "artifact-integrity-run",
        "--pilot-cells",
        "100",
        "--hash-mode",
        "pilot",
    ]
    assert main(
        arguments,
        handlers=recorder.mapping(),
        stdout=io.StringIO(),
        stderr=io.StringIO(),
    ) == 0
    artifact = tmp_path / "output" / "artifact-integrity-run" / "stages" / "assets" / "assets.txt"
    artifact.write_text("corrupted", encoding="utf-8")
    errors = io.StringIO()
    assert main(
        [*arguments, "--resume"],
        handlers=recorder.mapping(),
        stdout=io.StringIO(),
        stderr=errors,
    ) == 2
    assert "artifact hash mismatch" in errors.getvalue()


def test_resume_rejects_changed_source_tree_signature(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import climate_stress.runtime as runtime

    config_path = write_config(tmp_path)
    state = {
        "available": True,
        "is_dirty": True,
        "status_counts": {"untracked": 1},
        "scoped_path_count": 1,
    }
    monkeypatch.setattr(
        runtime, "source_tree_provenance", lambda *_args, **_kwargs: ("a" * 64, state)
    )
    arguments = [
        "--config",
        str(config_path),
        "--stage",
        "assets",
        "--run-id",
        "source-signature-run",
        "--pilot-cells",
        "100",
        "--hash-mode",
        "pilot",
    ]
    handlers = RecordingHandlers().mapping()
    assert main(
        arguments,
        handlers=handlers,
        stdout=io.StringIO(),
        stderr=io.StringIO(),
    ) == 0
    monkeypatch.setattr(
        runtime, "source_tree_provenance", lambda *_args, **_kwargs: ("b" * 64, state)
    )
    errors = io.StringIO()
    assert main(
        [*arguments, "--resume"],
        handlers=handlers,
        stdout=io.StringIO(),
        stderr=errors,
    ) == 2
    assert "source signature" in errors.getvalue()


def test_resume_rejects_changed_runtime_environment_signature(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import climate_stress.runtime as runtime

    config_path = write_config(tmp_path)
    state = {
        "python": {"version": "test"},
        "packages": {"numpy": "test"},
        "requirements_lock": {"exists": True, "sha256": "a" * 64},
    }
    monkeypatch.setattr(
        runtime,
        "runtime_environment_provenance",
        lambda *_args, **_kwargs: ("a" * 64, state),
    )
    arguments = [
        "--config",
        str(config_path),
        "--stage",
        "assets",
        "--run-id",
        "environment-signature-run",
        "--pilot-cells",
        "100",
        "--hash-mode",
        "pilot",
    ]
    handlers = RecordingHandlers().mapping()
    assert main(
        arguments,
        handlers=handlers,
        stdout=io.StringIO(),
        stderr=io.StringIO(),
    ) == 0
    monkeypatch.setattr(
        runtime,
        "runtime_environment_provenance",
        lambda *_args, **_kwargs: ("b" * 64, state),
    )
    errors = io.StringIO()
    assert main(
        [*arguments, "--resume"],
        handlers=handlers,
        stdout=io.StringIO(),
        stderr=errors,
    ) == 2
    assert "environment signature" in errors.getvalue()


def test_resume_requires_explicit_run_id(tmp_path: Path) -> None:
    config_path = write_config(tmp_path)
    errors = io.StringIO()
    code = main(
        [
            "--config",
            str(config_path),
            "--stage",
            "assets",
            "--resume",
            "--pilot-cells",
            "100",
        ],
        handlers=RecordingHandlers().mapping(),
        stdout=io.StringIO(),
        stderr=errors,
    )
    assert code == 2
    assert "--resume requires an explicit --run-id" in errors.getvalue()


def test_main_rejects_concurrent_same_run_without_touching_active_partial(
    tmp_path: Path,
) -> None:
    config_path = write_config(tmp_path)
    config = load_config(config_path)
    scope = resolve_scope(config, pilot_cells=100, years=None, hash_mode="pilot")
    run_id = "main-concurrent-run"
    with exclusive_run_lock(config.output_root, run_id):
        context = initialize_run(
            config,
            run_id=run_id,
            parameters=scope.as_parameters(),
            repo_root=Path(__file__).resolve().parents[2],
        )
        partial = context.stages_dir / ".assets.active.partial"
        partial.mkdir()
        sentinel = partial / "sentinel.bin"
        sentinel.write_bytes(b"active-owner-bytes")
        before = sentinel.read_bytes()
        errors = io.StringIO()
        assert main(
            [
                "--config",
                str(config_path),
                "--stage",
                "assets",
                "--run-id",
                run_id,
                "--resume",
                "--pilot-cells",
                "100",
                "--hash-mode",
                "pilot",
            ],
            handlers=RecordingHandlers().mapping(),
            stdout=io.StringIO(),
            stderr=errors,
        ) == 2
        assert "Concurrent execution was rejected" in errors.getvalue()
        assert sentinel.read_bytes() == before
    lock_dir = config.output_root / ".run-locks"
    assert list(lock_dir.glob(f"{run_id}.rejected.*.json"))
    assert list(lock_dir.glob(f"{run_id}.released.*.json"))


def test_assets_allows_2w_scope_block_but_rejects_pipeline_scope_block(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import SimpleNamespace

    import climate_stress.inventory as inventory_module
    from climate_stress.inventory import InventoryResult
    from climate_stress.pipeline import StageValidationError, _handle_assets

    config = load_config(write_config(tmp_path))
    request = SimpleNamespace(
        config=config,
        scope=SimpleNamespace(hash_mode="pilot"),
        work_dir=tmp_path / "asset-work",
    )
    request.work_dir.mkdir()
    records = pd.DataFrame({"asset_id": ["spei_2w"], "exists": [True]})

    def fake_write(result, work_dir):
        json_path = work_dir / "inventory.json"
        parquet_path = work_dir / "inventory.parquet"
        json_path.write_text("{}", encoding="utf-8")
        result.records.to_parquet(parquet_path, index=False)
        return json_path, parquet_path

    monkeypatch.setattr(inventory_module, "write_inventory", fake_write)
    scope_limited = InventoryResult(
        records=records,
        checks=[
            {
                "check_id": "spei_2w.timestamp_semantics",
                "status": "blocked",
                "evidence": {
                    "blocking_scope": "spei_2w_only",
                    "numeric_executed": False,
                },
            }
        ],
    )
    monkeypatch.setattr(
        inventory_module, "build_inventory", lambda *_args, **_kwargs: scope_limited
    )
    outcome = _handle_assets(request)
    assert outcome.extra["inventory_blocked"] is False
    assert outcome.extra["inventory_scope_limited_blocks"] == [
        "spei_2w.timestamp_semantics"
    ]
    assert outcome.extra["spei_2w_numeric_executed"] is False

    pipeline_block = InventoryResult(
        records=records,
        checks=[
            {
                "check_id": "required.asset",
                "status": "blocked",
                "evidence": {"blocking_scope": "pipeline"},
            }
        ],
    )
    monkeypatch.setattr(
        inventory_module, "build_inventory", lambda *_args, **_kwargs: pipeline_block
    )
    request.work_dir = tmp_path / "asset-work-pipeline-block"
    request.work_dir.mkdir()
    with pytest.raises(StageValidationError, match="required.asset"):
        _handle_assets(request)


def test_era_baseline_uses_temperature_history_fraction_not_window_coverage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import SimpleNamespace

    import climate_stress.era5 as era5_module
    from climate_stress.pipeline import _handle_era_baseline

    config = load_config(write_config(tmp_path))
    config.data["temperature"].update(
        {
            "calendar_window_half_width_days": 7,
            "hot_quantile": 0.90,
            "minimum_history_fraction": 0.61,
        }
    )
    config.data["quality"]["minimum_window_coverage"] = 0.97
    config.data["years"]["event_context"] = {"start": 1981, "end": 2020}
    context = initialize_run(config, run_id="era-history-fraction", repo_root=tmp_path)
    (context.stages_dir / "era_daily" / "daily_cache").mkdir(parents=True)
    work_dir = context.stages_dir / ".era_baseline.test.partial"
    work_dir.mkdir()
    observed: dict[str, float] = {}

    def fake_build(_daily, _history, _targets, root, **kwargs):
        observed.update(kwargs)
        root.mkdir()
        artifact = root / "threshold.npy"
        artifact.write_bytes(b"threshold")
        return [artifact]

    monkeypatch.setattr(era5_module, "build_calendar_thresholds", fake_build)
    outcome = _handle_era_baseline(
        SimpleNamespace(config=config, context=context, work_dir=work_dir)
    )
    assert observed["minimum_history_fraction"] == pytest.approx(0.61)
    assert observed["minimum_history_fraction"] != pytest.approx(0.97)
    assert outcome.row_counts["threshold_files"] == 1


def test_failed_stage_writes_structured_attempt_logs_without_deleting_partial(
    tmp_path: Path,
) -> None:
    config_path = write_config(tmp_path)

    def fail(request) -> StageOutcome:
        (request.work_dir / "partial-evidence.txt").write_text(
            "preserve", encoding="utf-8"
        )
        raise RuntimeError("simulated structured failure")

    errors = io.StringIO()
    code = main(
        [
            "--config",
            str(config_path),
            "--stage",
            "assets",
            "--run-id",
            "structured-failure-run",
            "--pilot-cells",
            "100",
            "--hash-mode",
            "pilot",
        ],
        handlers={"assets": fail},
        stdout=io.StringIO(),
        stderr=errors,
    )
    assert code == 2
    run_dir = tmp_path / "output" / "structured-failure-run"
    audit_logs = list((run_dir / "audit" / "attempts").glob("assets.*.failed.json"))
    partials = list((run_dir / "stages").glob(".assets.*.partial"))
    assert len(audit_logs) == 1 and len(partials) == 1
    payload = json.loads(audit_logs[0].read_text(encoding="utf-8"))
    assert payload["exception_type"] == "RuntimeError"
    assert payload["exception_message"] == "simulated structured failure"
    assert "Traceback" in payload["traceback"]
    assert list(partials[0].glob("_FAILED.*.json"))
    assert (partials[0] / "partial-evidence.txt").read_text(encoding="utf-8") == "preserve"


def _memory_sample(rss: int, peak: int, source: str = "test-sampler") -> dict:
    return {
        "sampled_at_utc": "2026-07-22T00:00:00Z",
        "rss_bytes": rss,
        "process_peak_rss_bytes": peak,
        "source": source,
    }


def test_stage_resource_marker_and_quality_summary_are_complete(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import climate_stress.pipeline as pipeline_module

    config_path = write_config(tmp_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["runtime"]["pilot_peak_rss_budget_bytes"] = 1_000
    config["runtime"]["full_peak_rss_budget_bytes"] = 2_000
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    samples = iter((_memory_sample(100, 120), _memory_sample(140, 180)))
    monkeypatch.setattr(
        pipeline_module, "process_memory_snapshot", lambda: next(samples)
    )
    stdout = io.StringIO()
    code = main(
        [
            "--config",
            str(config_path),
            "--stage",
            "assets",
            "--run-id",
            "resource-success",
            "--pilot-cells",
            "100",
            "--hash-mode",
            "pilot",
        ],
        handlers=RecordingHandlers().mapping(),
        stdout=stdout,
        stderr=io.StringIO(),
    )
    assert code == 0
    response = json.loads(stdout.getvalue())
    assert response["status"] == "PARTIAL_SCOPE"
    assert response["scope_profile"] == "non2w-dual-severity"
    marker = json.loads(
        (
            Path(response["run_dir"])
            / "stages"
            / "assets"
            / "_SUCCESS.json"
        ).read_text(encoding="utf-8")
    )
    resources = marker["resources"]
    assert resources["stage_start_current_rss_bytes"] == 100
    assert resources["stage_end_current_rss_bytes"] == 140
    assert resources["process_lifetime_peak_working_set_bytes"] == 180
    assert resources["peak_rss_budget_bytes"] == 1_000
    assert resources["budget_exceeded"] is False
    assert marker["extra"]["resources"] == resources
    assert marker["status"] == "PARTIAL_SCOPE"
    estimates = marker["resource_workload"]["estimated_block_bytes"]
    assert estimates and all(int(value) >= 0 for value in estimates.values())
    summary = json.loads(Path(response["quality_summary"]).read_text(encoding="utf-8"))
    assert summary["execution_status"] == "COMPLETED"
    assert summary["completion_scope_status"] == "PARTIAL_SCOPE"
    assert [record["stage"] for record in summary["stages"]] == ["assets"]
    assert summary["stages"][0]["resources"] == resources


def test_unavailable_memory_sampler_still_records_nonnegative_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import climate_stress.pipeline as pipeline_module

    monkeypatch.setattr(
        pipeline_module,
        "process_memory_snapshot",
        lambda: _memory_sample(0, 0, source="unavailable"),
    )
    config_path = write_config(tmp_path)
    stdout = io.StringIO()
    assert main(
        [
            "--config",
            str(config_path),
            "--stage",
            "assets",
            "--run-id",
            "resource-unavailable",
            "--pilot-cells",
            "100",
            "--hash-mode",
            "pilot",
        ],
        handlers=RecordingHandlers().mapping(),
        stdout=stdout,
        stderr=io.StringIO(),
    ) == 0
    marker = json.loads(
        (
            Path(json.loads(stdout.getvalue())["run_dir"])
            / "stages"
            / "assets"
            / "_SUCCESS.json"
        ).read_text(encoding="utf-8")
    )
    resources = marker["resources"]
    assert resources["start_source"] == "unavailable"
    assert resources["end_source"] == "unavailable"
    assert all(
        resources[key] >= 0
        for key in (
            "stage_start_current_rss_bytes",
            "stage_end_current_rss_bytes",
            "process_lifetime_peak_working_set_bytes",
        )
    )


def test_over_budget_attempt_is_immutable_and_low_rss_resume_cannot_bypass(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import climate_stress.pipeline as pipeline_module

    config_path = write_config(tmp_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["runtime"]["pilot_peak_rss_budget_bytes"] = 100
    config["runtime"]["full_peak_rss_budget_bytes"] = 100
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    first_samples = iter((_memory_sample(40, 50), _memory_sample(60, 250)))
    monkeypatch.setattr(
        pipeline_module, "process_memory_snapshot", lambda: next(first_samples)
    )
    arguments = [
        "--config",
        str(config_path),
        "--stage",
        "assets",
        "--run-id",
        "resource-over-budget",
        "--pilot-cells",
        "100",
        "--hash-mode",
        "pilot",
    ]
    first_errors = io.StringIO()
    assert main(
        arguments,
        handlers=RecordingHandlers().mapping(),
        stdout=io.StringIO(),
        stderr=first_errors,
    ) == 2
    assert "exceeds 100 bytes" in first_errors.getvalue()
    run_dir = tmp_path / "output" / "resource-over-budget"
    partial = next((run_dir / "stages").glob(".assets.*.partial"))
    assert not (run_dir / "stages" / "assets" / "_SUCCESS.json").exists()
    stage_result = partial / "_STAGE_RESULT.json"
    preserved_result = stage_result.read_bytes()
    first_failed = next(partial.glob("_FAILED.*.json"))
    preserved_failed = first_failed.read_bytes()
    first_payload = json.loads(preserved_failed)
    assert first_payload["resources"]["budget_exceeded"] is True
    assert (
        first_payload["resources"]["process_lifetime_peak_working_set_bytes"]
        == 250
    )
    first_summaries = list((run_dir / "audit" / "quality_summaries").glob("*.json"))
    assert len(first_summaries) == 1

    low_samples = iter((_memory_sample(10, 20), _memory_sample(12, 25)))
    monkeypatch.setattr(
        pipeline_module, "process_memory_snapshot", lambda: next(low_samples)
    )
    resume_errors = io.StringIO()
    assert main(
        [*arguments, "--resume"],
        handlers=RecordingHandlers().mapping(),
        stdout=io.StringIO(),
        stderr=resume_errors,
    ) == 2
    assert "prior over-budget attempt" in resume_errors.getvalue()
    assert not (run_dir / "stages" / "assets" / "_SUCCESS.json").exists()
    assert stage_result.read_bytes() == preserved_result
    assert first_failed.read_bytes() == preserved_failed
    failure_payloads = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in partial.glob("_FAILED.*.json")
    ]
    assert len(failure_payloads) == 2
    assert max(
        payload["resources"]["process_lifetime_peak_working_set_bytes"]
        for payload in failure_payloads
    ) == 250
    assert all(payload["resources"]["budget_exceeded"] for payload in failure_payloads)
    summaries = list((run_dir / "audit" / "quality_summaries").glob("*.json"))
    assert len(summaries) == 2
    assert all(
        json.loads(path.read_text(encoding="utf-8"))["stages"][0]["resources"]
        ["budget_exceeded"]
        for path in summaries
    )


def test_resume_reuses_exact_signature_partitioned_partial(tmp_path: Path) -> None:
    config_path = write_config(tmp_path)
    calls: list[tuple[str, str]] = []
    first_work_dir: list[Path] = []

    def handler(request) -> StageOutcome:
        calls.append((request.stage, request.work_dir.name))
        if request.stage == "era_daily":
            sentinel = request.work_dir / "year=2019.partition.done"
            if not sentinel.exists():
                sentinel.write_text("complete partition", encoding="utf-8")
                first_work_dir.append(request.work_dir)
                raise RuntimeError("simulated interruption after one partition")
            assert request.work_dir == first_work_dir[0]
        artifact = request.work_dir / f"{request.stage}.txt"
        artifact.write_text(request.stage, encoding="utf-8")
        return StageOutcome(artifacts={"artifact": artifact}, row_counts={"rows": 1})

    handlers = {stage: handler for stage in STAGE_ORDER}
    arguments = [
        "--config",
        str(config_path),
        "--stage",
        "era_daily",
        "--run-id",
        "interrupted-run",
        "--pilot-cells",
        "100",
        "--hash-mode",
        "pilot",
    ]
    errors = io.StringIO()
    assert main(
        arguments, handlers=handlers, stdout=io.StringIO(), stderr=errors
    ) == 2
    assert "simulated interruption" in errors.getvalue()
    run_dir = tmp_path / "output" / "interrupted-run"
    partials = list((run_dir / "stages").glob(".era_daily.*.partial"))
    assert partials == first_work_dir
    assert (partials[0] / "_START.json").is_file()

    stdout = io.StringIO()
    assert main(
        [*arguments, "--resume"],
        handlers=handlers,
        stdout=stdout,
        stderr=io.StringIO(),
    ) == 0
    payload = json.loads(stdout.getvalue())
    assert [item["status"] for item in payload["executed_stages"]] == [
        "SKIPPED_SUCCESS_MARKER",
        "SKIPPED_SUCCESS_MARKER",
        "COMPLETED",
    ]
    assert [stage for stage, _directory in calls].count("assets") == 1
    assert [stage for stage, _directory in calls].count("grid") == 1
    assert [stage for stage, _directory in calls].count("era_daily") == 2
    marker = json.loads(
        (run_dir / "stages" / "era_daily" / "_SUCCESS.json").read_text(
            encoding="utf-8"
        )
    )
    assert marker["extra"]["resumed_partial"] is True
    assert not list((run_dir / "stages").glob(".era_daily.*.partial"))


def test_resume_preserves_nonpartition_partial_and_starts_fresh(tmp_path: Path) -> None:
    config_path = write_config(tmp_path)
    grid_work_dirs: list[Path] = []

    def handler(request) -> StageOutcome:
        artifact = request.work_dir / f"{request.stage}.txt"
        if request.stage == "grid" and not grid_work_dirs:
            grid_work_dirs.append(request.work_dir)
            artifact.write_text("partial-content", encoding="utf-8")
            raise RuntimeError("simulated nonpartition interruption")
        if request.stage == "grid":
            grid_work_dirs.append(request.work_dir)
        artifact.write_text(request.stage, encoding="utf-8")
        return StageOutcome(artifacts={"artifact": artifact}, row_counts={"rows": 1})

    handlers = {stage: handler for stage in STAGE_ORDER}
    arguments = [
        "--config",
        str(config_path),
        "--stage",
        "grid",
        "--run-id",
        "nonpartition-run",
        "--pilot-cells",
        "100",
        "--hash-mode",
        "pilot",
    ]
    assert main(
        arguments,
        handlers=handlers,
        stdout=io.StringIO(),
        stderr=io.StringIO(),
    ) == 2
    assert main(
        [*arguments, "--resume"],
        handlers=handlers,
        stdout=io.StringIO(),
        stderr=io.StringIO(),
    ) == 0
    assert len(grid_work_dirs) == 2 and grid_work_dirs[0] != grid_work_dirs[1]
    archived = list((tmp_path / "output" / "nonpartition-run" / "stages").glob(
        "*.incomplete"
    ))
    assert len(archived) == 1
    assert (archived[0] / "grid.txt").read_text(encoding="utf-8") == "partial-content"
    marker = json.loads(
        (
            tmp_path
            / "output"
            / "nonpartition-run"
            / "stages"
            / "grid"
            / "_SUCCESS.json"
        ).read_text(encoding="utf-8")
    )
    assert marker["extra"]["restarted_after_preserved_partial"] is True


def test_default_handlers_cover_every_stage_without_delayed_placeholders() -> None:
    handlers = default_handlers()
    assert tuple(handlers) == STAGE_ORDER
    assert all(callable(handler) for handler in handlers.values())
    assert all("delayed" not in handler.__name__ for handler in handlers.values())


def test_hot_flash_window_metrics_keep_unknown_classification_as_na() -> None:
    long = pd.DataFrame(
        {
            "era01_cell_id": [1, 2],
            "grid_id_v3": [101, 102],
            "year": [2019, 2019],
            "window": ["full", "full"],
            "gleam43a_smrz_fd_main_any": [1.0, 0.0],
            "gleam43a_smrz_fd_strict_any": [0.0, 0.0],
        }
    )
    bridges = pd.DataFrame(
        {
            "era01_cell_id": [1],
            "grid_id_v3": [101],
            "event_id": ["1:gleam43a_smrz_fd_main:0001"],
            "event_family": ["flash_drought"],
            "year": [2019],
            "window": ["full"],
        }
    )
    classifications = pd.DataFrame(
        {
            "era01_cell_id": [1],
            "grid_id_v3": [101],
            "event_id": ["1:gleam43a_smrz_fd_main:0001"],
            "layer": ["SMrz"],
            "fd_variant": ["main"],
            "span_pentads": [3],
            "valid_hot_pentads": [2],
            "hot_pentad_count": [1],
            "hot_pentad_coverage": [2 / 3],
            "hot_fd_main_any": [None],
            "hot_fd_strict_majority": [None],
        }
    )

    output = _add_hot_flash_window_metrics(
        long, bridges, classifications, ["SMrz"]
    )
    unknown = output.loc[output["era01_cell_id"].eq(1)].iloc[0]
    no_event = output.loc[output["era01_cell_id"].eq(2)].iloc[0]
    assert np.isnan(unknown["gleam43a_smrz_fd_main_hot_main_any"])
    assert np.isnan(unknown["gleam43a_smrz_fd_main_hot_main_count"])
    assert np.isnan(unknown["gleam43a_smrz_fd_main_hot_strict_majority_any"])
    assert np.isnan(unknown["gleam43a_smrz_fd_main_hot_strict_majority_count"])
    assert unknown["gleam43a_smrz_fd_main_hot_valid_pentads"] == 2
    assert unknown["gleam43a_smrz_fd_main_hot_span_pentads"] == 3
    assert unknown["gleam43a_smrz_fd_main_hot_coverage"] == pytest.approx(2 / 3)
    assert no_event["gleam43a_smrz_fd_main_hot_main_any"] == 0
    assert no_event["gleam43a_smrz_fd_main_hot_main_count"] == 0


def test_gleam_partition_reader_never_requests_all_cell_columns(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import SimpleNamespace

    import climate_stress.pipeline as pipeline_module

    observed: list[object] = []

    class GuardedVariable:
        def __init__(self, values: np.ndarray) -> None:
            self.values = values

        def __getitem__(self, key):
            observed.append(key)
            if self.values.ndim == 1:
                assert key == slice(1, 3)
            else:
                assert isinstance(key, tuple) and key[0] == slice(None)
                assert key[1] == slice(1, 3)
            return self.values[key]

    class FakeDataset:
        def __init__(self) -> None:
            self.variables = {
                "era01_cell_id": GuardedVariable(np.asarray([1, 2, 3, 4])),
                "SMrz": GuardedVariable(
                    np.asarray(
                        [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]]
                    )
                ),
            }

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

    monkeypatch.setitem(
        sys.modules,
        "netCDF4",
        SimpleNamespace(Dataset=lambda _path: FakeDataset()),
    )
    monkeypatch.setattr(
        pipeline_module,
        "_netcdf_python_dates",
        lambda _dataset: (date(2019, 1, 1), date(2019, 1, 2)),
    )
    dates, cell_ids, values = pipeline_module._read_gleam_partition(
        tmp_path,
        "SMrz",
        2019,
        cell_slice=slice(1, 3),
    )

    assert observed == [slice(1, 3), (slice(None), slice(1, 3))]
    assert dates == (date(2019, 1, 1), date(2019, 1, 2))
    assert cell_ids.tolist() == [2, 3]
    assert values.tolist() == [[0.2, 0.3], [0.6, 0.7]]


def write_integration_config(tmp_path: Path, *, full_scope: bool = False) -> Path:
    path = tmp_path / "integration-config.yaml"
    data = {
        "version_id": "data-climate-stress-2010-2019-v1-test",
        "inputs": {
            "v3_main": str(tmp_path / "unused-v3.parquet"),
            "spei_monthly_pattern": str(
                tmp_path / "missing-monthly" / "SPEI-{scale}.nc"
            ),
        },
        "output": {
            "root": str(tmp_path / "integration-output"),
            "compression": "zstd",
            "netcdf_complevel": 1,
        },
        "years": {
            "target": [2019],
            "historical": [2016, 2017, 2018],
            "event_context": {"start": 2016, "end": 2020},
            "daily_validation": [],
        },
        "grid": {"expected_cells": 1},
        "phenology": {
            "windows": {
                "full": {},
                "v3pre30": {},
                "v3pm10": {},
                "hepm10": {},
                "v3he": {},
                "hema": {},
            }
        },
        "temperature": {
            "gdd": [
                {"base": 8, "upper": 29},
                {"base": 8, "upper": 30},
                {"base": 10, "upper": 29},
                {"base": 10, "upper": 30},
            ],
            "edd_thresholds": [29, 30, 32, 34, 35],
            "heatwave_min_days": 3,
            "minimum_history_fraction": 0.90,
        },
        "spei": {"minimum_valid_neighbors": 2},
        "gleam": {
            "layers": {"SMrz": "primary"},
            "daily_p10_calendar_half_width_days": 2,
        },
        "compound": {"daily_hot_sm_min_days": 5},
        "quality": {
            "minimum_window_coverage": 0.90,
            "coordinate_tolerance": 1.0e-8,
            "numeric_tolerance": 1.0e-6,
            "require_utc_daily_validation": False,
            "require_historical_occurrence_validation": False,
            "expected_wide_rows": 1,
            "expected_long_rows": 6,
            "pilot_grid_limit": 1,
            "pilot_years": [2019],
        },
        "runtime": {
            "gleam_cell_block_size": 1,
            "parquet_row_group_size": 64,
            "storage_dtype": "float64",
        },
    }
    data = complete_frozen_v1_fixture(data, tmp_path)
    if full_scope:
        data["spei"]["two_week_endpoint_decision_status"] = "CONFIRMED"
        data["scope"].update(
            {
                "profile": "full-spei2w-dual-severity",
                "completion_scope_status": "FULL_SCOPE",
                "spei_2w_numeric": True,
                "spei_2w_output": True,
            }
        )
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


class SyntheticClimateStages:
    """Create tiny real cache contracts for the expensive source-read stages."""

    @staticmethod
    def _crosswalk() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "grid_id_v3": [101],
                "era01_cell_id": [1],
                "lat_idx": [0],
                "lon_idx": [0],
                "latitude": [53.53],
                "longitude": [73.58],
                "lat10": [535],
                "lon10": [736],
            }
        )

    @staticmethod
    def _calendar(year: int) -> tuple[list[date], np.ndarray]:
        start = date(year, 1, 1)
        stop = date(year + 1, 1, 1)
        count = (stop - start).days
        dates = [start + timedelta(days=offset) for offset in range(count)]
        date_values = np.asarray(dates, dtype="datetime64[D]")
        return dates, date_values

    @staticmethod
    def _gleam_year_values() -> tuple[tuple[int, float], ...]:
        return (
            (2016, 0.30),
            (2017, 0.35),
            (2018, 0.40),
            (2019, 0.10),
            (2020, 0.30),
        )

    def assets(self, request) -> StageOutcome:
        from climate_stress.inventory import fingerprint_file

        source = request.config.path
        fingerprint = fingerprint_file(source, mode="full")
        record = {
            "asset_id": "synthetic.config",
            "family": "synthetic",
            "role": "integration fixture",
            "path": str(source),
            "exists": True,
            "size_bytes": fingerprint.size_bytes,
            "mtime_utc": fingerprint.mtime_utc,
            "sha256": fingerprint.sha256,
            "hash_algorithm": fingerprint.hash_algorithm,
            "hash_is_full": fingerprint.hash_is_full,
        }
        inventory_dir = request.work_dir / "audit" / "inventory"
        inventory_dir.mkdir(parents=True)
        json_path = inventory_dir / "source_inventory.json"
        parquet_path = inventory_dir / "source_inventory.parquet"
        json_path.write_text(
            json.dumps({"inventory_schema_version": 1, "records": [record]}),
            encoding="utf-8",
        )
        pd.DataFrame([record]).to_parquet(parquet_path, index=False)
        return StageOutcome(
            artifacts={
                "inventory_json": json_path,
                "inventory_parquet": parquet_path,
            },
            row_counts={"assets": 1},
        )

    def grid(self, request) -> StageOutcome:
        crosswalk = self._crosswalk()
        grid_year = crosswalk.copy()
        grid_year["year"] = 2019
        crosswalk_path = request.work_dir / "crosswalk.parquet"
        grid_year_path = request.work_dir / "grid_year.parquet"
        selection_path = request.work_dir / "selection.json"
        crosswalk.to_parquet(crosswalk_path, index=False)
        grid_year.to_parquet(grid_year_path, index=False)
        selection_path.write_text(
            json.dumps(
                {"selected_cells": len(crosswalk), "full_cells": len(crosswalk)}
            ),
            encoding="utf-8",
        )
        return StageOutcome(
            artifacts={
                "crosswalk": crosswalk_path,
                "grid_year": grid_year_path,
                "selection": selection_path,
            },
            row_counts={
                "selected_cells": len(crosswalk),
                "grid_year_rows": len(grid_year),
            },
        )

    def phenology(self, request) -> StageOutcome:
        from climate_stress.phenology import add_phenology_windows

        panel = self._crosswalk()
        panel["year"] = 2019
        panel["v3_doy"] = 100
        panel["he_doy"] = 150
        panel["ma_doy"] = 200
        panel = add_phenology_windows(panel)
        output = request.work_dir / "phenology_panel.parquet"
        panel.to_parquet(output, index=False)
        return StageOutcome(artifacts={"phenology_panel": output}, row_counts={"rows": 1})

    def era_daily(self, request) -> StageOutcome:
        from climate_stress.era5 import save_daily_cache

        root = request.work_dir / "daily_cache"
        outputs = []
        for year in range(2016, 2021):
            _dates, date_values = self._calendar(year)
            day_codes = (
                date_values - np.datetime64("1970-01-01", "D")
            ).astype(np.int32)
            shape = (len(date_values), len(self._crosswalk()))
            arrays = {
                "era5u8_tmean_c": np.full(shape, 31.0),
                "era5u8_tmax_c": np.full(shape, 35.0),
                "era5u8_tmin_c": np.full(shape, 24.0),
                "era5u8_gdd_b8_u29": np.full(shape, 21.0),
                "era5u8_gdd_b8_u30": np.full(shape, 22.0),
                "era5u8_gdd_b10_u29": np.full(shape, 19.0),
                "era5u8_gdd_b10_u30": np.full(shape, 20.0),
                "era5u8_edd_t29": np.full(shape, 0.25),
                "era5u8_edd_t30": np.full(shape, 0.20),
                "era5u8_edd_t32": np.full(shape, 0.10),
                "era5u8_edd_t34": np.full(shape, 0.05),
                "era5u8_edd_t35": np.zeros(shape),
            }
            outputs.extend(
                save_daily_cache(
                    root, year, day_codes, arrays, {"synthetic": True}
                )
            )
        return StageOutcome(
            artifacts={"daily_cache": root}, row_counts={"cache_files": len(outputs)}
        )

    def era_baseline(self, request) -> StageOutcome:
        root = request.work_dir / "thresholds"
        root.mkdir(parents=True)
        n_cells = len(self._crosswalk())
        np.save(
            root / "era5u8_tmax_p90_calendar.npy",
            np.full((366, n_cells), 30.0),
        )
        np.save(
            root / "era5u8_tmin_p90_calendar.npy",
            np.full((366, n_cells), 20.0),
        )
        files = 2
        for year in range(2016, 2021):
            _dates, values = self._calendar(year)
            target = root / f"year={year}"
            target.mkdir()
            np.save(
                target / "era5u8_tmax_historical_percentile.npy",
                np.full((len(values), n_cells), 95.0),
            )
            files += 1
        return StageOutcome(artifacts={"thresholds": root}, row_counts={"files": files})

    def spei(self, request) -> StageOutcome:
        from climate_stress.spei import prepare_two_week_records

        windows = tuple(request.config.windows)
        cell_ids = self._crosswalk()["era01_cell_id"].astype("int64").tolist()
        rows = [(cell_id, window) for cell_id in cell_ids for window in windows]
        manual = pd.DataFrame(
            {
                "era01_cell_id": [cell_id for cell_id, _window in rows],
                "year": [2019] * len(rows),
                "window": [window for _cell_id, window in rows],
                "chm_spei_s1_mean": [-0.5] * len(rows),
                "chm_spei_s3_mean": [-0.4] * len(rows),
            }
        )
        dynamic = manual[["era01_cell_id", "year", "window"]].copy()
        dynamic["chm_spei_dynamic_ext_value"] = -0.3
        event_long = manual[["era01_cell_id", "year", "window"]].copy()
        event_long["chm_spei_s1_k10_main_count"] = 0.0
        full_scope = request.config.completion_scope_status == "FULL_SCOPE"
        if full_scope:
            event_long["chm_spei_2w_k10_main_count"] = 0.0
        manual_path = request.work_dir / "chm_spei_manual.parquet"
        dynamic_path = request.work_dir / "chm_spei_dynamic_ext.parquet"
        event_long_path = request.work_dir / "chm_spei_event_window_long.parquet"
        event_path = request.work_dir / "chm_spei_events.parquet"
        bridge_path = request.work_dir / "chm_spei_event_window_bridge.parquet"
        cache_path = request.work_dir / "cache"
        cache_path.mkdir()
        (cache_path / "metadata.json").write_text(
            '{"synthetic":true}', encoding="utf-8"
        )
        two_week_path = request.work_dir / "spei_2w_audit.json"
        spei_config = request.config.data["spei"]
        audit_dates = (
            [date(2019, 1, 1), date(2019, 1, 8)] if full_scope else []
        )
        audit_values = [-0.5, -0.4] if full_scope else []
        _records, two_week_audit = prepare_two_week_records(
            audit_dates,
            audit_values,
            config_semantics=str(spei_config["two_week_timestamp_semantics"]),
            endpoint_decision_status=str(
                spei_config["two_week_endpoint_decision_status"]
            ),
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
            cell_count=1 if full_scope else 0,
            canonical_field_count=1 if full_scope else 0,
        )
        two_week_payload = two_week_audit.as_dict()
        two_week_path.write_text(
            json.dumps(two_week_payload, sort_keys=True), encoding="utf-8"
        )
        manual.to_parquet(manual_path, index=False)
        dynamic.to_parquet(dynamic_path, index=False)
        event_long.to_parquet(event_long_path, index=False)
        pd.DataFrame(
            {
                "event_id": pd.Series(dtype="string"),
                "timescale": pd.Series(dtype="string"),
            }
        ).to_parquet(
            event_path, index=False
        )
        pd.DataFrame(
            {
                "event_id": pd.Series(dtype="string"),
                "timescale": pd.Series(dtype="string"),
            }
        ).to_parquet(
            bridge_path, index=False
        )
        return StageOutcome(
            artifacts={
                "cache": cache_path,
                "manual": manual_path,
                "dynamic": dynamic_path,
                "event_long": event_long_path,
                "events": event_path,
                "event_bridge": bridge_path,
                "spei_2w_audit": two_week_path,
            },
            row_counts={
                "manual_rows": len(manual),
                "dynamic_rows": len(dynamic),
                "event_long_rows": len(event_long),
            },
            extra={"spei_2w": two_week_payload},
        )

    def gleam_daily(self, request) -> StageOutcome:
        import netCDF4 as nc

        root = request.work_dir / "daily_cache"
        files = 0
        for year, value in self._gleam_year_values():
            dates, _values = self._calendar(year)
            output = root / "SMrz" / f"year={year}.nc"
            output.parent.mkdir(parents=True, exist_ok=True)
            with nc.Dataset(output, "w", format="NETCDF4") as dataset:
                dataset.createDimension("time", len(dates))
                crosswalk = self._crosswalk()
                dataset.createDimension("cell", len(crosswalk))
                time = dataset.createVariable("time", "i4", ("time",))
                time.units = "days since 1900-01-01"
                time.calendar = "proleptic_gregorian"
                time[:] = [(day - date(1900, 1, 1)).days for day in dates]
                cell = dataset.createVariable("era01_cell_id", "i8", ("cell",))
                cell[:] = crosswalk["era01_cell_id"].to_numpy(dtype=np.int64)
                sm = dataset.createVariable("SMrz", "f8", ("time", "cell"))
                sm[:] = value
            files += 1
        return StageOutcome(
            artifacts={"daily_cache": root}, row_counts={"cache_files": files}
        )

    def mapping(self):
        return {
            "assets": self.assets,
            "grid": self.grid,
            "phenology": self.phenology,
            "era_daily": self.era_daily,
            "era_baseline": self.era_baseline,
            "spei": self.spei,
            "gleam_daily": self.gleam_daily,
        }


class TwoCellSyntheticClimateStages(SyntheticClimateStages):
    @staticmethod
    def _crosswalk() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "grid_id_v3": [101, 102],
                "era01_cell_id": [1, 2],
                "lat_idx": [0, 0],
                "lon_idx": [0, 1],
                "latitude": [53.53, 53.53],
                "longitude": [73.58, 73.68],
                "lat10": [535, 535],
                "lon10": [736, 737],
            }
        )

    @staticmethod
    def _gleam_year_values() -> tuple[tuple[int, float], ...]:
        return (
            (2016, 0.10),
            (2017, 0.50),
            (2018, 0.10),
            (2019, 0.10),
            (2020, 0.10),
        )


def test_real_event_stage_keeps_complete_context_ids_across_cell_blocks(
    tmp_path: Path,
) -> None:
    config_path = write_integration_config(tmp_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["grid"]["expected_cells"] = 2
    config["quality"]["pilot_grid_limit"] = 2
    config["quality"]["expected_wide_rows"] = 2
    config["quality"]["expected_long_rows"] = 12
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    handlers = default_handlers()
    handlers.update(TwoCellSyntheticClimateStages().mapping())
    real_gleam_baseline = handlers["gleam_baseline"]

    def gleam_baseline_with_fixed_event_threshold(request):
        outcome = real_gleam_baseline(request)
        metric_root = Path(outcome.artifacts["metrics"])
        for year in range(2016, 2021):
            q10 = np.load(
                metric_root / "SMrz" / f"year={year}" / "daily_q10.npy",
                mmap_mode="r+",
            )
            q10[:] = 0.20
            q10.flush()
        return outcome

    handlers["gleam_baseline"] = gleam_baseline_with_fixed_event_threshold
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = main(
        [
            "--config",
            str(config_path),
            "--stage",
            "events",
            "--run-id",
            "two-cell-event-blocks",
            "--pilot-cells",
            "2",
            "--years",
            "2019",
            "--hash-mode",
            "pilot",
        ],
        handlers=handlers,
        stdout=stdout,
        stderr=stderr,
    )
    assert exit_code == 0, stderr.getvalue()
    run_dir = Path(json.loads(stdout.getvalue())["run_dir"])
    event_dataset = run_dir / "stages" / "events" / "compound_events.parquet"
    bridge_dataset = (
        run_dir / "stages" / "events" / "compound_event_window_bridge.parquet"
    )
    for dataset, partition_year in (
        (event_dataset, 2018),
        (bridge_dataset, 2019),
    ):
        assert dataset.is_dir()
        assert (dataset / "_DATASET.json").is_file()
        partitions = [
            path
            for path in dataset.rglob("*.parquet")
            if path.name != "empty.parquet"
        ]
        assert len(partitions) == 2
        relative_parts = [path.relative_to(dataset).parts for path in partitions]
        assert all(parts[0] == "family-daily_hot_sm_p10" for parts in relative_parts)
        assert all(parts[1] == f"year-{partition_year}" for parts in relative_parts)
        assert {parts[2] for parts in relative_parts} == {
            "cell-block-000000",
            "cell-block-000001",
        }
    events = pd.read_parquet(
        event_dataset
    )
    daily = events.loc[events["event_family"].eq("daily_hot_sm_p10")]
    assert set(daily["era01_cell_id"]) == {1, 2}
    assert "year" not in daily.columns
    assert not daily.duplicated(
        ["era01_cell_id", "event_family", "variant", "event_id"]
    ).any()
    bridge = pd.read_parquet(bridge_dataset)
    daily_bridge = bridge.loc[bridge["event_family"].eq("daily_hot_sm_p10")]
    assert set(daily_bridge["year"]) == {2019}
    for variant in ("main_gap0", "sensitivity_gap2"):
        current = daily.loc[daily["variant"].eq(variant)]
        current_bridge = daily_bridge.loc[daily_bridge["variant"].eq(variant)]
        assert len(current) == 2
        assert current["event_id"].str.endswith(":0002").all()
        assert set(current["event_start_year"]) == {2018}
        assert set(current["first_target_overlap_year"]) == {2019}
        assert set(current["event_end_year"]) == {2020}
        assert set(current["start_date"].astype(str)) == {"2018-01-01"}
        assert set(current["end_date"].astype(str)) == {"2020-12-31"}
        assert set(current_bridge["event_id"]) == set(current["event_id"])

    config["runtime"]["gleam_cell_block_size"] = 2
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    second_stdout = io.StringIO()
    second_stderr = io.StringIO()
    second_exit_code = main(
        [
            "--config",
            str(config_path),
            "--stage",
            "events",
            "--run-id",
            "two-cell-event-single-block",
            "--pilot-cells",
            "2",
            "--years",
            "2019",
            "--hash-mode",
            "pilot",
        ],
        handlers=handlers,
        stdout=second_stdout,
        stderr=second_stderr,
    )
    assert second_exit_code == 0, second_stderr.getvalue()
    second_run_dir = Path(json.loads(second_stdout.getvalue())["run_dir"])
    for filename, sort_keys in (
        (
            "compound_window_long.parquet",
            ["era01_cell_id", "year", "window"],
        ),
        (
            "compound_events.parquet",
            ["era01_cell_id", "event_family", "variant", "event_id"],
        ),
        (
            "compound_event_window_bridge.parquet",
            ["era01_cell_id", "event_family", "variant", "event_id", "year", "window"],
        ),
        (
            "hot_flash_drought_classification.parquet",
            ["era01_cell_id", "fd_variant", "event_id"],
        ),
    ):
        first = pd.read_parquet(run_dir / "stages" / "events" / filename)
        second = pd.read_parquet(second_run_dir / "stages" / "events" / filename)
        available = [name for name in sort_keys if name in first.columns]
        if available:
            first = first.sort_values(available).reset_index(drop=True)
            second = second.sort_values(available).reset_index(drop=True)
        pd.testing.assert_frame_equal(first, second, check_like=True)


def test_event_resume_reuses_partial_and_isolates_only_corrupt_partition(
    tmp_path: Path,
) -> None:
    config_path = write_integration_config(tmp_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["grid"]["expected_cells"] = 2
    config["quality"]["pilot_grid_limit"] = 2
    config["runtime"]["gleam_cell_block_size"] = 1
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    handlers = default_handlers()
    handlers.update(TwoCellSyntheticClimateStages().mapping())
    real_gleam_baseline = handlers["gleam_baseline"]

    def gleam_baseline_with_fixed_event_threshold(request):
        outcome = real_gleam_baseline(request)
        metric_root = Path(outcome.artifacts["metrics"])
        for year in range(2016, 2021):
            q10 = np.load(
                metric_root / "SMrz" / f"year={year}" / "daily_q10.npy",
                mmap_mode="r+",
            )
            q10[:] = 0.20
            q10.flush()
        return outcome

    handlers["gleam_baseline"] = gleam_baseline_with_fixed_event_threshold
    real_event_handler = handlers["events"]
    event_work_dirs: list[Path] = []
    interrupt_once = {"value": True}

    def interrupted_event_handler(request):
        event_work_dirs.append(request.work_dir)
        outcome = real_event_handler(request)
        if interrupt_once["value"]:
            interrupt_once["value"] = False
            raise RuntimeError("simulated interruption after event partitions")
        return outcome

    handlers["events"] = interrupted_event_handler
    arguments = [
        "--config",
        str(config_path),
        "--stage",
        "events",
        "--run-id",
        "event-partition-resume",
        "--pilot-cells",
        "2",
        "--years",
        "2019",
        "--hash-mode",
        "pilot",
    ]
    first_stderr = io.StringIO()
    assert main(
        arguments,
        handlers=handlers,
        stdout=io.StringIO(),
        stderr=first_stderr,
    ) == 2
    assert "simulated interruption after event partitions" in first_stderr.getvalue()
    run_dir = tmp_path / "integration-output" / "event-partition-resume"
    partials = list((run_dir / "stages").glob(".events.*.partial"))
    assert partials == event_work_dirs
    event_root = partials[0] / "compound_events.parquet"
    partitions = sorted(event_root.rglob("*.parquet"))
    assert len(partitions) == 2
    corrupt_relative = partitions[0].relative_to(partials[0])
    intact_relative = partitions[1].relative_to(partials[0])
    intact_hash = partitions[1].read_bytes()
    partitions[0].write_bytes(b"intentionally corrupt parquet partition")

    second_stdout = io.StringIO()
    second_stderr = io.StringIO()
    assert main(
        [*arguments, "--resume"],
        handlers=handlers,
        stdout=second_stdout,
        stderr=second_stderr,
    ) == 0, second_stderr.getvalue()
    assert len(event_work_dirs) == 2
    assert event_work_dirs[0] == event_work_dirs[1]
    final_stage = run_dir / "stages" / "events"
    repaired = final_stage / corrupt_relative
    intact = final_stage / intact_relative
    assert pd.read_parquet(repaired).shape[0] > 0
    assert intact.read_bytes() == intact_hash
    archived = list(
        repaired.parent.glob(f".{repaired.name}.*.incomplete")
    )
    assert len(archived) == 1
    assert archived[0].read_bytes() == b"intentionally corrupt parquet partition"
    result = json.loads(
        (final_stage / "_STAGE_RESULT.json").read_text(encoding="utf-8")
    )
    stats = result["extra"]["partition_stats"]["events"]
    assert stats["repaired"] == 1
    assert stats["reused"] >= 1


def test_aggregate_resume_reuses_intact_block_and_archives_corrupt_block(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = write_integration_config(tmp_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["grid"]["expected_cells"] = 2
    config["quality"]["pilot_grid_limit"] = 2
    config["runtime"]["gleam_cell_block_size"] = 1
    config["runtime"]["aggregate_cell_block_size"] = 1
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    handlers = default_handlers()
    handlers.update(TwoCellSyntheticClimateStages().mapping())
    real_aggregate = handlers["aggregate"]
    real_read_parquet = pd.read_parquet
    aggregate_work_dirs: list[Path] = []
    interrupt_once = {"value": True}

    def interrupted_aggregate(request):
        aggregate_work_dirs.append(request.work_dir)
        def forbid_full_phenology_read(path, *args, **kwargs):
            if Path(path).name == "phenology_panel.parquet":
                raise AssertionError(
                    "Aggregate must predicate-push the phenology panel by cell block"
                )
            return real_read_parquet(path, *args, **kwargs)

        with monkeypatch.context() as scoped_patch:
            scoped_patch.setattr(pd, "read_parquet", forbid_full_phenology_read)
            outcome = real_aggregate(request)
        if interrupt_once["value"]:
            interrupt_once["value"] = False
            raise RuntimeError("simulated interruption after aggregate partitions")
        return outcome

    handlers["aggregate"] = interrupted_aggregate
    arguments = [
        "--config",
        str(config_path),
        "--stage",
        "aggregate",
        "--run-id",
        "aggregate-partition-resume",
        "--pilot-cells",
        "2",
        "--years",
        "2019",
        "--hash-mode",
        "pilot",
    ]
    first_stderr = io.StringIO()
    assert main(
        arguments,
        handlers=handlers,
        stdout=io.StringIO(),
        stderr=first_stderr,
    ) == 2
    assert "simulated interruption after aggregate partitions" in first_stderr.getvalue()
    run_dir = tmp_path / "integration-output" / "aggregate-partition-resume"
    partials = list((run_dir / "stages").glob(".aggregate.*.partial"))
    assert partials == aggregate_work_dirs
    partitions = sorted((partials[0] / "partitions" / "canonical").glob("*.parquet"))
    assert len(partitions) == 2
    corrupt_relative = partitions[0].relative_to(partials[0])
    intact_relative = partitions[1].relative_to(partials[0])
    intact_bytes = partitions[1].read_bytes()
    partitions[0].write_bytes(b"intentionally corrupt aggregate partition")

    second_stderr = io.StringIO()
    assert main(
        [*arguments, "--resume"],
        handlers=handlers,
        stdout=io.StringIO(),
        stderr=second_stderr,
    ) == 0, second_stderr.getvalue()
    assert aggregate_work_dirs[0] == aggregate_work_dirs[1]
    final_stage = run_dir / "stages" / "aggregate"
    repaired = final_stage / corrupt_relative
    intact = final_stage / intact_relative
    assert pd.read_parquet(repaired).shape[0] == 6
    assert intact.read_bytes() == intact_bytes
    archived = list(repaired.parent.glob(f".{repaired.name}.*.incomplete"))
    assert len(archived) == 1
    assert archived[0].read_bytes() == b"intentionally corrupt aggregate partition"
    assert default_handlers()["aggregate"].__name__ == "_handle_aggregate"


def test_cli_real_stage_chain_consumes_and_publishes_each_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import climate_stress.era5 as era5_module
    import climate_stress.pipeline as pipeline_module

    config_path = write_integration_config(tmp_path)
    handlers = default_handlers()
    handlers.update(SyntheticClimateStages().mapping())
    active_event_stage = {"value": False}
    era_cell_slices: list[slice] = []
    gleam_cell_slices: list[slice] = []
    real_event_handler = handlers["events"]
    real_temperature_loader = era5_module.attach_daily_temperature_thresholds
    real_gleam_reader = pipeline_module._read_gleam_partition

    def monitored_event_handler(request):
        active_event_stage["value"] = True
        try:
            return real_event_handler(request)
        finally:
            active_event_stage["value"] = False

    def guarded_temperature_loader(*args, **kwargs):
        if active_event_stage["value"]:
            selector = kwargs.get("cell_slice")
            assert isinstance(selector, slice)
            assert selector.stop - selector.start <= 1
            era_cell_slices.append(selector)
        return real_temperature_loader(*args, **kwargs)

    def guarded_gleam_reader(*args, **kwargs):
        if active_event_stage["value"]:
            selector = kwargs.get("cell_slice")
            assert isinstance(selector, slice)
            assert selector.stop - selector.start <= 1
            gleam_cell_slices.append(selector)
        return real_gleam_reader(*args, **kwargs)

    handlers["events"] = monitored_event_handler
    monkeypatch.setattr(
        era5_module,
        "attach_daily_temperature_thresholds",
        guarded_temperature_loader,
    )
    monkeypatch.setattr(
        pipeline_module,
        "_read_gleam_partition",
        guarded_gleam_reader,
    )
    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_code = main(
        [
            "--config",
            str(config_path),
            "--stage",
            "all",
            "--run-id",
            "synthetic-chain",
            "--pilot-cells",
            "1",
            "--years",
            "2019",
            "--hash-mode",
            "pilot",
        ],
        handlers=handlers,
        stdout=stdout,
        stderr=stderr,
    )
    assert exit_code == 0, stderr.getvalue()
    payload = json.loads(stdout.getvalue())
    assert [item["stage"] for item in payload["executed_stages"]] == list(STAGE_ORDER)
    assert all(item["status"] == "COMPLETED" for item in payload["executed_stages"])
    quality_summary = json.loads(
        Path(payload["quality_summary"]).read_text(encoding="utf-8")
    )
    assert [record["stage"] for record in quality_summary["stages"]] == list(
        STAGE_ORDER
    )
    assert all(
        set(record["resources"])
        >= {
            "stage_start_current_rss_bytes",
            "stage_end_current_rss_bytes",
            "process_lifetime_peak_working_set_bytes",
            "peak_rss_budget_bytes",
            "budget_exceeded",
        }
        for record in quality_summary["stages"]
    )
    run_dir = Path(payload["run_dir"])
    for stage in STAGE_ORDER:
        assert (run_dir / "stages" / stage / "_SUCCESS.json").is_file()
    long = pd.read_parquet(
        run_dir
        / "stages"
        / "export"
        / "bundle"
        / "climate_stress_long.parquet"
    )
    wide = pd.read_parquet(
        run_dir
        / "stages"
        / "export"
        / "bundle"
        / "climate_stress_wide.parquet"
    )
    assert len(long) == 6 and len(wide) == 1
    assert "era5u8_tmean_mean_c" in long
    assert "chm_spei_s1_mean" in long
    assert "gleam43a_smrz_p20_exposure_days" in long
    assert "compound_smrz_hot_p10_main_gap0_count" in long
    validation = json.loads(
        (run_dir / "stages" / "validate" / "validation_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert validation["validation_status"] == "PASS"
    assert validation["status"] == "PARTIAL_SCOPE"
    assert validation["completion_scope_status"] == "PARTIAL_SCOPE"
    assert validation["scope_profile"] == "non2w-dual-severity"
    assert validation["spei_2w_numeric"] is False
    assert validation["spei_2w_output"] is False
    assert validation["spei_2w_numeric_enabled"] is False
    assert validation["spei_2w_output_enabled"] is False
    assert validation["compound_mode"] == "dual_independent_severity"
    validation_stage_result = json.loads(
        (run_dir / "stages" / "validate" / "_STAGE_RESULT.json").read_text(
            encoding="utf-8"
        )
    )
    assert validation_stage_result["extra"] == {
        "validation_status": "PASS",
        "status": "PARTIAL_SCOPE",
        "completion_scope_status": "PARTIAL_SCOPE",
        "scope_profile": "non2w-dual-severity",
        "spei_2w_numeric": False,
        "spei_2w_output": False,
        "spei_2w_numeric_enabled": False,
        "spei_2w_output_enabled": False,
        "compound_mode": "dual_independent_severity",
    }
    assert era_cell_slices and gleam_cell_slices
    assert all(value == slice(0, 1) for value in era_cell_slices)
    assert all(value == slice(0, 1) for value in gleam_cell_slices)

    manifest = json.loads(
        (run_dir / "stages" / "export" / "bundle" / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    for records in (manifest["outputs"], manifest["audit_artifacts"]):
        for record in records.values():
            linked = Path(record["path"])
            assert not linked.is_absolute()
            assert ".partial" not in linked.parts
            assert (run_dir / linked).exists()
    for stage in STAGE_ORDER:
        result = json.loads(
            (run_dir / "stages" / stage / "_STAGE_RESULT.json").read_text(
                encoding="utf-8"
            )
        )
        assert all((run_dir / path).exists() for path in result["artifacts"].values())

    second_stdout = io.StringIO()
    second_stderr = io.StringIO()
    assert main(
        [
            "--config",
            str(config_path),
            "--stage",
            "all",
            "--run-id",
            "synthetic-chain-repeat",
            "--pilot-cells",
            "1",
            "--years",
            "2019",
            "--hash-mode",
            "pilot",
        ],
        handlers=handlers,
        stdout=second_stdout,
        stderr=second_stderr,
    ) == 0, second_stderr.getvalue()
    second_run_dir = Path(json.loads(second_stdout.getvalue())["run_dir"])
    from climate_stress.runtime import sha256_file

    relative_files = (
        Path("stages/assets/audit/inventory/source_inventory.json"),
        Path("stages/assets/audit/inventory/source_inventory.parquet"),
        Path("stages/export/bundle/climate_stress_long.parquet"),
        Path("stages/export/bundle/climate_stress_wide.parquet"),
        Path("stages/export/bundle/climate_stress_cube.nc"),
        Path("stages/export/bundle/climate_stress_merge_ready.dta"),
        Path("stages/export/bundle/manifest.json"),
    )
    assert {
        str(path): sha256_file(run_dir / path) for path in relative_files
    } == {
        str(path): sha256_file(second_run_dir / path) for path in relative_files
    }


def test_confirmed_full_scope_fixture_publishes_and_validates_2w_contract(
    tmp_path: Path,
) -> None:
    config_path = write_integration_config(tmp_path, full_scope=True)
    handlers = default_handlers()
    handlers.update(SyntheticClimateStages().mapping())
    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_code = main(
        [
            "--config",
            str(config_path),
            "--stage",
            "all",
            "--run-id",
            "synthetic-full-scope",
            "--pilot-cells",
            "1",
            "--years",
            "2019",
            "--hash-mode",
            "pilot",
        ],
        handlers=handlers,
        stdout=stdout,
        stderr=stderr,
    )
    assert exit_code == 0, stderr.getvalue()
    payload = json.loads(stdout.getvalue())
    run_dir = Path(payload["run_dir"])
    bundle = run_dir / "stages" / "export" / "bundle"
    long = pd.read_parquet(bundle / "climate_stress_long.parquet")
    assert "chm_spei_2w_k10_main_count" in long
    validation = json.loads(
        (run_dir / "stages" / "validate" / "validation_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert validation["validation_status"] == "PASS"
    assert validation["completion_scope_status"] == "FULL_SCOPE"
    assert validation["scope_profile"] == "full-spei2w-dual-severity"
    assert validation["spei_2w_numeric"] is True
    assert validation["spei_2w_output"] is True
    assert validation["gates"]["spei_2w_scope_contract"]["status"] == "PASS"
    contract = json.loads(
        (bundle / "output_contract.json").read_text(encoding="utf-8")
    )
    assert contract["status"] == "FULL_SCOPE"
    assert contract["spei_2w"]["numeric_executed"] is True
    assert contract["spei_2w"]["output_included"] is True
    assert contract["spei_2w"]["stage_evidence"]["status"] == "EXECUTED"


def test_partial_scope_real_spei_skips_missing_2w_and_completes_export_validate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import climate_stress.spei as spei_module
    from climate_stress.core import SPEI_2W_PENDING_STATUS
    from climate_stress.spei import SpeiCachePaths

    config_path = write_integration_config(tmp_path)
    config = load_config(config_path)
    assert "spei_2w" not in config.data["inputs"]

    def fake_monthly_cache(
        _pattern,
        _target_latitude,
        _target_longitude,
        output_root,
        **_kwargs,
    ) -> SpeiCachePaths:
        root = Path(output_root)
        root.mkdir(parents=True, exist_ok=True)
        target_codes = np.asarray(
            [201900 + month for month in range(1, 13)], dtype=np.int32
        )
        full_codes = np.asarray(
            [
                year * 100 + month
                for year in range(2016, 2021)
                for month in range(1, 13)
            ],
            dtype=np.int32,
        )
        target_codes_path = root / "target_month_codes.npy"
        full_codes_path = root / "full_month_codes.npy"
        np.save(target_codes_path, target_codes)
        np.save(full_codes_path, full_codes)
        target_paths: dict[int, Path] = {}
        for scale in range(1, 13):
            path = root / f"target-scale-{scale:02d}.npy"
            np.save(path, np.full((len(target_codes), 1), -0.5))
            target_paths[scale] = path
        full_paths: dict[int, Path] = {}
        for scale in (1, 3):
            path = root / f"full-scale-{scale:02d}.npy"
            np.save(path, np.full((len(full_codes), 1), -0.5))
            full_paths[scale] = path
        mapping = root / "mapping.npz"
        np.savez(mapping, synthetic=np.asarray([1], dtype=np.int8))
        metadata = root / "metadata.json"
        metadata.write_text('{"synthetic":true}', encoding="utf-8")
        return SpeiCachePaths(
            root=root,
            mapping=mapping,
            target_month_codes=target_codes_path,
            full_month_codes=full_codes_path,
            target_nearest=target_paths,
            full_manual=full_paths,
            metadata=metadata,
        )

    monkeypatch.setattr(spei_module, "build_spei_caches", fake_monthly_cache)
    monkeypatch.setattr(
        spei_module,
        "build_two_week_cache",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("PARTIAL_SCOPE must not open the SPEI-2W source")
        ),
    )
    handlers = default_handlers()
    synthetic = SyntheticClimateStages().mapping()
    synthetic.pop("spei")
    handlers.update(synthetic)
    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_code = main(
        [
            "--config",
            str(config_path),
            "--stage",
            "all",
            "--run-id",
            "partial-real-spei",
            "--pilot-cells",
            "1",
            "--years",
            "2019",
            "--hash-mode",
            "pilot",
        ],
        handlers=handlers,
        stdout=stdout,
        stderr=stderr,
    )
    assert exit_code == 0, stderr.getvalue()
    run_dir = Path(json.loads(stdout.getvalue())["run_dir"])
    audit = json.loads(
        (run_dir / "stages" / "spei" / "spei_2w_audit.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit["status"] == SPEI_2W_PENDING_STATUS
    assert audit["numeric_executed"] is False
    assert all(
        audit[name] == 0
        for name in (
            "release_count",
            "cell_count",
            "canonical_field_count",
            "event_rows",
            "bridge_rows",
        )
    )
    long = pd.read_parquet(
        run_dir / "stages" / "export" / "bundle" / "climate_stress_long.parquet"
    )
    assert not any(name.startswith("chm_spei_2w_") for name in long.columns)
    validation = json.loads(
        (run_dir / "stages" / "validate" / "validation_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert validation["validation_status"] == "PASS"
    assert validation["completion_scope_status"] == "PARTIAL_SCOPE"
    assert validation["gates"]["spei_2w_scope_contract"]["status"] == "PASS"
