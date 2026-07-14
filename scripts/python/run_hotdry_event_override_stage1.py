"""Identity-closed smoke and non-blocking Stage-1 event support runner."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

from hotdry_event_override_validators import (  # noqa: E402
    validate_event_panel,
    validate_override_manifest,
)
from run_hotdry_event_stage1 import (  # noqa: E402
    NAMED_ZONES,
    REQUIRED_PANEL_FIELDS,
    YEARS,
    build_records_for_year,
    file_digest,
    hash_artifacts,
    sample_key_sha256,
    select_smoke_panel,
    support_tables,
    validate_panel_inventory,
    write_csv,
    zone_for_province,
    year_input_paths,
)


CANONICAL_ID = "compound-event-intensity-duration-override-v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("smoke", "stage1"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--tmax-dir", type=Path, required=True)
    parser.add_argument("--precip-dir", type=Path, required=True)
    parser.add_argument("--smrz-dir", type=Path, required=True)
    parser.add_argument("--hash-cache", type=Path)
    return parser.parse_args()


def implementation_paths(
    panel: Path,
    *,
    tmax_dir: Path,
    precip_dir: Path,
    smrz_dir: Path,
) -> list[tuple[str, Path]]:
    paths: list[tuple[str, Path]] = [
        ("v3_panel", panel),
        ("zone_mapping", PROJECT_ROOT / "scripts/stata/v3sub_step0_subsamples.do"),
    ]
    for year in YEARS:
        tmax, precipitation, smrz = year_input_paths(
            year,
            tmax_dir=tmax_dir,
            precip_dir=precip_dir,
            smrz_dir=smrz_dir,
        )
        paths.extend(
            [
                (f"tmax_{year}", tmax),
                (f"precipitation_{year}", precipitation),
                (f"smrz_{year}", smrz),
            ]
        )
    paths.extend(
        [
            ("implementation_core", PROJECT_ROOT / "scripts/python/hotdry_event_core.py"),
            ("implementation_validators", PROJECT_ROOT / "scripts/python/hotdry_event_validators.py"),
            ("implementation_runner", PROJECT_ROOT / "scripts/python/run_hotdry_event_override_stage1.py"),
            ("implementation_runner_original", PROJECT_ROOT / "scripts/python/run_hotdry_event_stage1.py"),
            ("implementation_override_runner", PROJECT_ROOT / "scripts/python/run_hotdry_event_override_stage1.py"),
            ("implementation_override_validators", PROJECT_ROOT / "scripts/python/hotdry_event_override_validators.py"),
            ("contract_event_panel", PROJECT_ROOT / "docs/contracts/event_panel.schema.json"),
            ("contract_run_manifest", PROJECT_ROOT / "docs/contracts/run_manifest.schema.json"),
            ("frozen_design", PROJECT_ROOT / "quality_reports/plans/2026-07-15_hotdry_event_duration_intensity_design_v1.md"),
            ("design_review_round2_pass", PROJECT_ROOT / "quality_reports/plans/2026-07-15_hotdry_event_design_review_round2_pass.md"),
            ("override_plan", PROJECT_ROOT / "quality_reports/plans/2026-07-15_hotdry_event_override_execution.md"),
            ("historical_smoke_review_round2_stop", PROJECT_ROOT / "quality_reports/plans/2026-07-15_hotdry_event_smoke_review_round2_stop.md"),
            ("historical_stop_report", PROJECT_ROOT / "docs/results/compound-event-intensity-duration-v1/report.md"),
            ("test_core", PROJECT_ROOT / "tests/test_hotdry_event_core.py"),
            ("test_validators", PROJECT_ROOT / "tests/test_hotdry_event_validators.py"),
            ("test_stage1_runner", PROJECT_ROOT / "tests/test_hotdry_event_stage1_runner.py"),
            ("test_override_runner", PROJECT_ROOT / "tests/test_hotdry_event_override_runner.py"),
        ]
    )
    return paths


def inventory_inputs(
    panel: Path,
    *,
    tmax_dir: Path,
    precip_dir: Path,
    smrz_dir: Path,
    cache_path: Path | None,
) -> list[dict[str, Any]]:
    cached_by_path: dict[str, dict[str, Any]] = {}
    if cache_path is not None and cache_path.is_file():
        cached = json.loads(cache_path.read_text(encoding="utf-8-sig"))
        cached_by_path = {str(item["path"]): item for item in cached}
    result: list[dict[str, Any]] = []
    for role, path in implementation_paths(
        panel,
        tmax_dir=tmax_dir,
        precip_dir=precip_dir,
        smrz_dir=smrz_dir,
    ):
        path = path.resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        key = str(path).replace("\\", "/")
        cached = cached_by_path.get(key)
        if cached is not None and int(cached.get("bytes", -1)) == path.stat().st_size:
            digest = {
                "path": key,
                "bytes": int(cached["bytes"]),
                "md5": str(cached["md5"]),
                "sha256": str(cached["sha256"]),
            }
        else:
            digest = file_digest(path)
        result.append({"role": role, **digest})
    return result


def peak_rss_mb() -> float | None:
    try:
        import psutil

        return float(psutil.Process().memory_info().rss / 1024**2)
    except (ImportError, OSError):
        return None


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite nonempty run directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()

    panel_path = args.panel.resolve()
    tmax_dir = args.tmax_dir.resolve()
    precip_dir = args.precip_dir.resolve()
    smrz_dir = args.smrz_dir.resolve()
    inputs = inventory_inputs(
        panel_path,
        tmax_dir=tmax_dir,
        precip_dir=precip_dir,
        smrz_dir=smrz_dir,
        cache_path=args.hash_cache.resolve() if args.hash_cache else None,
    )
    inventory_seconds = time.perf_counter() - started

    panel_started = time.perf_counter()
    panel = pd.read_stata(
        panel_path,
        columns=list(REQUIRED_PANEL_FIELDS),
        convert_categoricals=False,
    )
    validate_panel_inventory(panel)
    panel["zone"] = panel["province"].map(zone_for_province)
    analysis_panel = select_smoke_panel(panel) if args.mode == "smoke" else panel
    panel_seconds = time.perf_counter() - panel_started

    records: list[dict[str, Any]] = []
    statuses: list[dict[str, Any]] = []
    coordinate_audit: list[dict[str, Any]] = []
    performance: list[dict[str, Any]] = []
    rng = np.random.default_rng(42)
    for year in YEARS:
        year_started = time.perf_counter()
        year_panel = analysis_panel[analysis_panel["year"] == year].copy()
        year_records, year_statuses = build_records_for_year(
            year_panel,
            year,
            tmax_dir=tmax_dir,
            precip_dir=precip_dir,
            smrz_dir=smrz_dir,
            coordinate_audit=coordinate_audit,
            rng=rng,
        )
        records.extend(year_records)
        statuses.extend(year_statuses)
        performance.append(
            {
                "year": year,
                "panel_rows": len(year_panel),
                "event_panel_rows": len(year_records),
                "elapsed_seconds": time.perf_counter() - year_started,
                "rss_mb_after_year": peak_rss_mb(),
            }
        )

    event_schema = json.loads((PROJECT_ROOT / "docs/contracts/event_panel.schema.json").read_text(encoding="utf-8"))
    run_schema = json.loads((PROJECT_ROOT / "docs/contracts/run_manifest.schema.json").read_text(encoding="utf-8"))
    validate_event_panel(records, event_schema)

    event_panel_path = output_dir / "event_panel.csv.gz"
    pd.DataFrame(records).to_csv(
        event_panel_path,
        index=False,
        compression={"method": "gzip", "mtime": 0},
        encoding="utf-8",
    )
    status_path = output_dir / "grid_year_support.csv"
    write_csv(status_path, statuses)
    coordinate_path = output_dir / "coordinate_value_audit.csv"
    write_csv(coordinate_path, coordinate_audit)
    input_path = output_dir / "input_inventory.json"
    input_path.write_text(json.dumps(inputs, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.mode == "stage1":
        by_year, by_zone, support_warnings = support_tables(pd.DataFrame(statuses))
    else:
        by_year, by_zone, support_warnings = pd.DataFrame(), pd.DataFrame(), []
    by_year_path = output_dir / "support_by_zone_year.csv"
    by_zone_path = output_dir / "support_by_zone.csv"
    write_csv(by_year_path, by_year)
    write_csv(by_zone_path, by_zone)

    performance_path = output_dir / "performance.json"
    performance_payload = {
        "inventory_seconds": inventory_seconds,
        "panel_read_seconds": panel_seconds,
        "years": performance,
        "total_seconds_before_manifest": time.perf_counter() - started,
        "implementation_note": "11-column Stata read; yearly bulk NumPy pairwise gather",
    }
    performance_path.write_text(json.dumps(performance_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    decision = {
        "stage": "identity_closed_smoke" if args.mode == "smoke" else "stage1_support_override",
        "status": "PASS_SMOKE_IDENTITY_CLOSED" if args.mode == "smoke" else "PASS_STAGE1_WITH_WARNINGS",
        "not_for_inference": True,
        "yield_model_run": False,
        "support_warnings": support_warnings,
        "support_warnings_blocking": False,
        "record_count": len(records),
        "grid_year_status_count": len(statuses),
    }
    decision_path = output_dir / "stage_decision.json"
    decision_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")

    artifact_paths = [
        event_panel_path,
        status_path,
        coordinate_path,
        input_path,
        by_year_path,
        by_zone_path,
        performance_path,
        decision_path,
    ]
    extension = {
        "contract_version": "compound-event-override-run-extension-v1",
        "stage": decision["stage"],
        "failure_stage": None,
        "failure_reasons": [],
        "support_warnings": support_warnings,
        "support_warnings_blocking": False,
        "completed_artifacts": hash_artifacts(artifact_paths, output_dir),
        "yield_model_run": False,
    }
    extension_path = output_dir / "event_run_extension.json"
    extension_path.write_text(json.dumps(extension, ensure_ascii=False, indent=2), encoding="utf-8")

    ready = pd.DataFrame(statuses)
    ready_keys = ready[ready["analysis_ready"]][["grid_id", "year"]].copy()
    manifest = {
        "contract_version": "run-manifest-v1",
        "canonical_id": CANONICAL_ID,
        "run_id": output_dir.name,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "SMOKE",
        "not_for_inference": True,
        "design_version": "override-v1",
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True).strip(),
        "data_family": "V3",
        "inputs": inputs,
        "sample_predicate": (
            "deterministic first two grid_ids per named zone-year; identity interface only"
            if args.mode == "smoke"
            else "weather window 100% complete and all frozen yield-model fields complete-case; original support thresholds are nonblocking warnings"
        ),
        "sample_key_serialization": "sort(grid_id string,year); UTF-8 grid_id|YYYY\\n",
        "sample_key_sha256": sample_key_sha256(ready_keys),
        "sample_counts": {
            "source_rows": int(len(panel)),
            "selected_grid_years": int(len(statuses)),
            "analysis_ready_grid_years": int(ready["analysis_ready"].sum()),
            "event_panel_rows": int(len(records)),
        },
        "outcome": "ln_yield (not estimated in smoke or Stage 1)",
        "exposure_definition": "Tmax>=32C and precipitation<1mm/day for >=3 consecutive days inside v3_doy-30..ma_doy",
        "soil_moisture_roles": ["antecedent SMrz", "drawdown SMrz", "recovery/censoring"],
        "fixed_effects": ["grid FE (preregistered; not estimated)", "province-year FE (preregistered; not estimated)"],
        "inference": {
            "primary": "not run in Stage 1",
            "bootstrap_reps": 0,
            "spatial_block_degrees": 2,
            "spatial_hac_km": [100, 200, 300],
            "multiplicity": "not run",
        },
        "ca_quantiles": None,
        "exposure_endpoints": None,
        "seed": 42,
        "claims": [],
        "stop_rules_triggered": [],
        "verification": [
            {"check": "event row and cross-record validators", "status": "PASS", "detail": f"{len(records)} rows"},
            {"check": "implementation and all executed test identities", "status": "PASS", "detail": f"{len(inputs)} input roles"},
            {"check": "yield model not run", "status": "PASS", "detail": "Stage 1 boundary"},
            {
                "check": "historical support thresholds (nonblocking by user authorization)",
                "status": "FAIL" if support_warnings else ("SKIP" if args.mode == "smoke" else "PASS"),
                "detail": "; ".join(support_warnings) if support_warnings else None,
            },
        ],
    }
    validate_override_manifest(manifest, run_schema, extension=extension)
    manifest_path = output_dir / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
