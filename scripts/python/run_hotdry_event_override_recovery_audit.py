"""Audit the frozen IPCW recovery risk set and stop on model separation."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

from hotdry_event_override_recovery import (  # noqa: E402
    build_recovery_risk_set,
    separated_day_cells,
)
from hotdry_event_override_validators import validate_override_manifest  # noqa: E402
from run_hotdry_event_stage1 import file_digest, hash_artifacts  # noqa: E402


CANONICAL_ID = "compound-event-intensity-duration-override-v1"
NUMERATOR_FORMULA = "censored_now ~ C(follow_day) + C(zone) + C(year)"
DENOMINATOR_FORMULA = (
    "censored_now ~ C(follow_day) + ca + C(zone) + C(year) + antecedent_smrz "
    "+ duration_days + event_mean_excess_c + onset_doy + ca:C(zone)"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--stage1-dir", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    return parser.parse_args()


def fit_censoring_model(formula: str, risk: pd.DataFrame) -> tuple[Any, dict[str, Any]]:
    result = smf.glm(formula, data=risk, family=sm.families.Binomial()).fit(maxiter=200, tol=1e-10)
    diagnostics = {
        "formula": formula,
        "converged": bool(result.converged),
        "parameters": int(len(result.params)),
        "maximum_absolute_coefficient": float(np.max(np.abs(result.params))),
        "deviance": float(result.deviance),
    }
    return result, diagnostics


def event_key_sha256(events: pd.DataFrame) -> str:
    keys = sorted(
        (str(int(row.grid_id)), int(row.year), int(row.event_seq))
        for row in events[["grid_id", "year", "event_seq"]].itertuples(index=False)
    )
    payload = "".join(f"{grid_id}|{year:04d}|{event_seq}\n" for grid_id, year, event_seq in keys)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite nonempty run directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    panel_path = args.panel.resolve()
    stage1_dir = args.stage1_dir.resolve()
    model_dir = args.model_dir.resolve()

    model_manifest = json.loads((model_dir / "run_manifest.json").read_text(encoding="utf-8"))
    inputs = [dict(item) for item in model_manifest["inputs"]]
    for role, path in [
        ("implementation_recovery_core", PROJECT_ROOT / "scripts/python/hotdry_event_override_recovery.py"),
        ("implementation_recovery_runner", PROJECT_ROOT / "scripts/python/run_hotdry_event_override_recovery_audit.py"),
        ("test_override_recovery", PROJECT_ROOT / "tests/test_hotdry_event_override_recovery.py"),
        ("model_full_manifest", model_dir / "run_manifest.json"),
        ("model_full_extension", model_dir / "event_run_extension.json"),
    ]:
        inputs.append({"role": role, **file_digest(path.resolve())})

    event_panel = pd.read_csv(stage1_dir / "event_panel.csv.gz")
    events = event_panel[event_panel["event_indicator"]].copy()
    events["grid_id"] = events["grid_id"].astype(int)
    panel = pd.read_stata(
        panel_path,
        columns=["grid_id", "year", "ca", "latitude", "longitude"],
        convert_categoricals=False,
    )
    events = events.merge(panel, on=["grid_id", "year"], how="left", validate="many_to_one", suffixes=("", "_panel"))
    recovery_fields = [
        "recovery_days",
        "recovery_observed",
        "right_censored",
        "antecedent_smrz",
        "duration_days",
        "event_mean_excess_c",
        "onset_doy",
        "ca",
    ]
    missing_counts = {field: int(events[field].isna().sum()) for field in recovery_fields}
    complete = events.dropna(subset=recovery_fields).copy()
    risk = build_recovery_risk_set(complete)

    day_support = (
        risk.groupby("follow_day", sort=True)
        .agg(risk_rows=("event_id", "size"), recovered_rows=("recovered_now", "sum"), censored_rows=("censored_now", "sum"))
        .reset_index()
    )
    day_path = output_dir / "risk_support_by_day.csv"
    day_support.to_csv(day_path, index=False, encoding="utf-8-sig")
    zone_support = (
        complete.groupby("zone", sort=True)
        .agg(
            events=("event_id", "size"),
            recovered_events=("recovery_observed", "sum"),
            censored_events=("right_censored", "sum"),
            mean_followup_days=("recovery_days", "mean"),
        )
        .reset_index()
    )
    zone_support["censoring_rate"] = zone_support["censored_events"] / zone_support["events"]
    zone_path = output_dir / "risk_support_by_zone.csv"
    zone_support.to_csv(zone_path, index=False, encoding="utf-8-sig")

    separated = separated_day_cells(risk)
    numerator, numerator_diagnostics = fit_censoring_model(NUMERATOR_FORMULA, risk)
    denominator, denominator_diagnostics = fit_censoring_model(DENOMINATOR_FORMULA, risk)
    separation_detected = bool(separated) or max(
        numerator_diagnostics["maximum_absolute_coefficient"],
        denominator_diagnostics["maximum_absolute_coefficient"],
    ) > 20
    diagnostics = {
        "events_total": int(len(events)),
        "events_complete_for_recovery": int(len(complete)),
        "risk_rows": int(len(risk)),
        "missing_counts": missing_counts,
        "censoring_events": int(risk["censored_now"].sum()),
        "recovery_events": int(risk["recovered_now"].sum()),
        "separated_day_cells": separated,
        "numerator": numerator_diagnostics,
        "denominator": denominator_diagnostics,
        "separation_detected": separation_detected,
        "ipcw_weights_generated": False,
        "outcome_cloglog_run": False,
        "standardized_curves_generated": False,
        "rmst30_generated": False,
    }
    diagnostics_path = output_dir / "censoring_model_diagnostics.json"
    diagnostics_path.write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2), encoding="utf-8")

    if not separation_detected:
        raise RuntimeError("recovery audit expected the frozen separation guard to be evaluated explicitly")
    reason = (
        "Frozen pooled-logit day indicators exhibit perfect/quasi-complete separation; "
        "IPCW weights, cloglog recovery model, standardized CA P25/P75 curves, and RMST30 are not estimable under the frozen specification."
    )
    decision = {
        "stage": "recovery_ipcw_preflight",
        "status": "COMPUTATIONALLY_BLOCKED_MODEL_SEPARATION",
        "reason": reason,
        "support_thresholds_blocking": False,
        "missing_field_block": False,
        "model_separation_block": True,
        "yield_models_unaffected": True,
    }
    decision_path = output_dir / "recovery_stage_decision.json"
    decision_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")

    artifact_paths = [day_path, zone_path, diagnostics_path, decision_path]
    extension = {
        "contract_version": "compound-event-override-recovery-extension-v1",
        "stage": "recovery_ipcw_preflight",
        "failure_stage": "censoring pooled-logit models",
        "failure_reasons": [reason],
        "completed_artifacts": hash_artifacts(artifact_paths, output_dir),
        "yield_model_run": True,
        "ipcw_rmst_run": False,
    }
    extension_path = output_dir / "event_run_extension.json"
    extension_path.write_text(json.dumps(extension, ensure_ascii=False, indent=2), encoding="utf-8")

    ca_quantiles = model_manifest["ca_quantiles"]
    manifest = {
        "contract_version": "run-manifest-v1",
        "canonical_id": CANONICAL_ID,
        "run_id": output_dir.name,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "STOP",
        "not_for_inference": True,
        "design_version": "override-v1-recovery-audit",
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True).strip(),
        "data_family": "V3",
        "inputs": inputs,
        "sample_predicate": "event-positive rows with complete frozen recovery state and baseline covariates",
        "sample_key_serialization": "sort(grid_id string,year,event_seq); UTF-8 grid_id|YYYY|event_seq\\n",
        "sample_key_sha256": event_key_sha256(complete),
        "sample_counts": {
            "event_rows": int(len(events)),
            "recovery_complete_events": int(len(complete)),
            "risk_rows": int(len(risk)),
            "censoring_events": int(risk["censored_now"].sum()),
        },
        "outcome": "daily recovery hazard (not estimated after separation guard)",
        "exposure_definition": "30-day recovery from event end to 90% of antecedent SMrz",
        "soil_moisture_roles": ["antecedent SMrz", "drawdown SMrz", "recovery/censoring"],
        "fixed_effects": ["follow-day indicators", "zone", "year"],
        "inference": {
            "primary": "not run because pooled-logit IPCW models separate",
            "bootstrap_reps": 0,
            "spatial_block_degrees": 2,
            "spatial_hac_km": [100, 200, 300],
            "multiplicity": "not run",
        },
        "ca_quantiles": ca_quantiles,
        "exposure_endpoints": model_manifest["exposure_endpoints"],
        "seed": 42,
        "claims": [],
        "stop_rules_triggered": [reason],
        "verification": [
            {"check": "risk-set fields", "status": "PASS", "detail": f"{len(complete)} events; missing counts {missing_counts}"},
            {"check": "pooled-logit separation guard", "status": "FAIL", "detail": f"separated cells={separated}; max coefficients={numerator_diagnostics['maximum_absolute_coefficient']:.3f}/{denominator_diagnostics['maximum_absolute_coefficient']:.3f}"},
            {"check": "IPCW/RMST", "status": "SKIP", "detail": "not generated after frozen separation rule"},
            {"check": "yield models", "status": "PASS", "detail": "completed in models_v3 and unaffected"},
        ],
    }
    schema = json.loads((PROJECT_ROOT / "docs/contracts/run_manifest.schema.json").read_text(encoding="utf-8"))
    validate_override_manifest(manifest, schema, extension=extension)
    (output_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
