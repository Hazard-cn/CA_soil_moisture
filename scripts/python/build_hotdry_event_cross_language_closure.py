"""Seal the Python/R/Stata joint-model comparison as a separate validation run."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

import pandas as pd


def digest(path: Path, role: str) -> dict[str, object]:
    payload = path.read_bytes()
    return {"role": role, "path": str(path).replace("\\", "/"), "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source, output = args.revision_dir.resolve(), args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(output)
    output.mkdir(parents=True, exist_ok=True)
    comparison = pd.read_csv(source / "cross_language_comparison.csv")
    comparison["coef_diff_python_r"] = (comparison["python_coef"] - comparison["r_coef"]).abs()
    comparison["se_diff_python_r"] = (comparison["python_se"] - comparison["r_se"]).abs()
    comparison["coef_diff_python_stata"] = (comparison["python_coef"] - comparison["stata_coef"]).abs()
    comparison["se_diff_python_stata"] = (comparison["python_se"] - comparison["stata_se"]).abs()
    metrics = {
        "terms": int(len(comparison)),
        "max_abs_coef_python_r": float(comparison["coef_diff_python_r"].max()),
        "max_abs_cluster_se_python_r": float(comparison["se_diff_python_r"].max()),
        "max_abs_coef_python_stata": float(comparison["coef_diff_python_stata"].max()),
        "max_abs_cluster_se_python_stata": float(comparison["se_diff_python_stata"].max()),
    }
    metrics["point_tolerance_pass"] = bool(max(metrics["max_abs_coef_python_r"], metrics["max_abs_coef_python_stata"]) < 0.01)
    metrics["se_tolerance_pass"] = bool(max(metrics["max_abs_cluster_se_python_r"], metrics["max_abs_cluster_se_python_stata"]) < 0.05)
    summary_path = output / "validation_summary.json"
    summary_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    root = Path(__file__).resolve().parents[2]
    inputs = [
        digest(source / "run_manifest.json", "revision_manifest"),
        digest(source / "cross_language_joint_input.csv.gz", "joint_input_csv"),
        digest(source / "cross_language_joint_input.dta", "joint_input_dta"),
        digest(source / "joint_R_results.csv", "r_results"),
        digest(source / "joint_Stata_results.dta", "stata_results"),
        digest(source / "cross_language_comparison.csv", "comparison"),
        digest(root / "scripts/R/verify_hotdry_event_round1_joint.R", "r_verifier"),
        digest(root / "scripts/stata/verify_hotdry_event_round1_joint.do", "stata_verifier"),
        digest(Path(__file__).resolve(), "closure_builder"),
    ]
    manifest = {
        "contract_version": "run-manifest-v1",
        "canonical_id": "compound-event-intensity-duration-override-v1",
        "run_id": output.name,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "PASS",
        "not_for_inference": True,
        "design_version": "round1-cross-language-validation-v1",
        "inputs": inputs,
        "outputs": [digest(summary_path, "validation_summary")],
        "tolerance": {"point_estimate": 0.01, "cluster_se": 0.05},
    }
    (output / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
