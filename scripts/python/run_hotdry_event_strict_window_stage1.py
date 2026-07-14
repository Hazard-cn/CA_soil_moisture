"""Build the preregistered strict v3_doy..ma_doy event-panel sensitivity."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

from hotdry_event_override_validators import validate_event_panel, validate_override_manifest  # noqa: E402
from run_hotdry_event_stage1 import (  # noqa: E402
    REQUIRED_PANEL_FIELDS,
    YEARS,
    build_records_for_year,
    file_digest,
    hash_artifacts,
    sample_key_sha256,
    support_tables,
    validate_panel_inventory,
    write_csv,
    zone_for_province,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--tmax-dir", type=Path, required=True)
    parser.add_argument("--precip-dir", type=Path, required=True)
    parser.add_argument("--smrz-dir", type=Path, required=True)
    parser.add_argument("--extended-stage1-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out = args.output_dir.resolve()
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(out)
    out.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    base = json.loads((args.extended_stage1_dir / "run_manifest.json").read_text(encoding="utf-8"))
    inputs = [dict(item) for item in base["inputs"]]
    for role, path in [
        ("implementation_strict_window_runner", Path(__file__)),
        ("round1_method_review", PROJECT_ROOT / "quality_reports/plans/2026-07-15_hotdry_event_override_method_review_round1.md"),
    ]:
        inputs.append({"role": role, **file_digest(path.resolve())})

    panel = pd.read_stata(args.panel, columns=list(REQUIRED_PANEL_FIELDS), convert_categoricals=False)
    validate_panel_inventory(panel)
    panel["zone"] = panel["province"].map(zone_for_province)
    records: list[dict] = []
    statuses: list[dict] = []
    audit: list[dict] = []
    rng = np.random.default_rng(42)
    annual_performance = []
    for year in YEARS:
        tick = time.perf_counter()
        part = panel[panel["year"] == year].copy()
        part["v3_doy"] = part["v3_doy"] + 30
        rows, support = build_records_for_year(
            part,
            year,
            tmax_dir=args.tmax_dir,
            precip_dir=args.precip_dir,
            smrz_dir=args.smrz_dir,
            coordinate_audit=audit,
            rng=rng,
        )
        records.extend(rows)
        statuses.extend(support)
        annual_performance.append({"year": year, "seconds": time.perf_counter() - tick, "rows": len(rows)})
    event_schema = json.loads((PROJECT_ROOT / "docs/contracts/event_panel.schema.json").read_text(encoding="utf-8"))
    validate_event_panel(records, event_schema)
    event_path = out / "event_panel.csv.gz"
    pd.DataFrame(records).to_csv(event_path, index=False, compression={"method": "gzip", "mtime": 0}, encoding="utf-8")
    support_path = out / "grid_year_support.csv"
    write_csv(support_path, statuses)
    by_year, by_zone, warnings = support_tables(pd.DataFrame(statuses))
    by_year_path = out / "support_by_zone_year.csv"
    by_zone_path = out / "support_by_zone.csv"
    write_csv(by_year_path, by_year)
    write_csv(by_zone_path, by_zone)
    audit_path = out / "coordinate_value_audit.csv"
    write_csv(audit_path, audit)
    performance_path = out / "performance.json"
    performance_path.write_text(json.dumps({"annual": annual_performance, "total_seconds": time.perf_counter()-started}, indent=2), encoding="utf-8")
    decision = {
        "stage": "FULL_STAGE1_NONINFERENTIAL",
        "status": "PASS_STRICT_WINDOW_STAGE1",
        "window": "v3_doy..ma_doy inclusive",
        "support_warnings": warnings,
        "support_warnings_blocking": False,
    }
    decision_path = out / "stage_decision.json"
    decision_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
    artifact_paths = [event_path, support_path, by_year_path, by_zone_path, audit_path, performance_path, decision_path]
    extension = {
        "contract_version": "compound-event-strict-window-extension-v1",
        "stage": "FULL_STAGE1_NONINFERENTIAL",
        "failure_stage": None,
        "failure_reasons": [],
        "completed_artifacts": hash_artifacts(artifact_paths, out),
        "yield_model_run": False,
    }
    (out / "event_run_extension.json").write_text(json.dumps(extension, ensure_ascii=False, indent=2), encoding="utf-8")
    ready = pd.DataFrame(statuses)
    keys = ready[ready["analysis_ready"]][["grid_id", "year"]]
    manifest = {
        "contract_version": "run-manifest-v1",
        "canonical_id": "compound-event-intensity-duration-override-v1",
        "run_id": out.name,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "SMOKE",
        "not_for_inference": True,
        "design_version": "override-round1-strict-window",
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True).strip(),
        "data_family": "V3",
        "inputs": inputs,
        "sample_predicate": "strict v3_doy..ma_doy; weather complete and frozen yield fields complete-case",
        "sample_key_serialization": "sort(grid_id string,year); UTF-8 grid_id|YYYY\\n",
        "sample_key_sha256": sample_key_sha256(keys),
        "sample_counts": {"source_rows": len(panel), "analysis_ready_grid_years": int(ready.analysis_ready.sum()), "event_panel_rows": len(records)},
        "outcome": "ln_yield (not estimated in Stage1)",
        "exposure_definition": "strict v3_doy..ma_doy Tmax>=32C and precipitation<1mm/day runs >=3 days",
        "soil_moisture_roles": ["antecedent", "drawdown", "recovery"],
        "fixed_effects": ["grid FE planned", "province-year FE planned"],
        "inference": {"primary": "not run", "bootstrap_reps": 0, "spatial_block_degrees": 2, "spatial_hac_km": [100,200,300], "multiplicity": "not run"},
        "ca_quantiles": None,
        "exposure_endpoints": None,
        "seed": 42,
        "claims": [],
        "stop_rules_triggered": [],
        "verification": [
            {"check": "FULL_STAGE1_NONINFERENTIAL", "status": "PASS", "detail": f"{int(ready.analysis_ready.sum())} ready grid-years"},
            {"check": "support thresholds are nonblocking", "status": "FAIL" if warnings else "PASS", "detail": "; ".join(warnings) or None},
        ],
    }
    schema = json.loads((PROJECT_ROOT / "docs/contracts/run_manifest.schema.json").read_text(encoding="utf-8"))
    validate_override_manifest(manifest, schema, extension=extension)
    (out / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
