"""Post-run integrity and Stata/Python reconciliation for threshold Round 1."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


LEGACY_RESULT_FIELDS = {
    "damage_at_ca_p25",
    "damage_at_ca_p75",
    "buffer_contrast",
    "buffer_percent",
}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verification-files", nargs="+", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite validation manifest: {args.output}")
    run_manifest = json.loads((args.run_dir / "run_manifest.json").read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    yield_results = pd.read_csv(args.run_dir / "yield_results.csv")
    legacy_present = sorted(LEGACY_RESULT_FIELDS.intersection(yield_results.columns))
    checks.append({"check": "neutral yield-result field names", "status": "PASS" if not legacy_present else "FAIL", "detail": legacy_present})
    identity_error = float(
        np.max(
            np.abs(
                yield_results["conditional_yield_change_high_sr"]
                - yield_results["conditional_yield_change_low_sr"]
                - yield_results["high_minus_low_sr_slope_contrast"]
            )
        )
    )
    checks.append({"check": "high minus low SR identity", "status": "PASS" if identity_error < 1e-12 else "FAIL", "detail": identity_error})

    state = pd.read_csv(args.run_dir / "sm_state_results.csv")
    state_fields = {"exposure_p50_cday", "exposure_p90_cday", "antecedent_smrz_m3m3"}
    checks.append({"check": "state endpoint units explicit", "status": "PASS" if state_fields.issubset(state.columns) else "FAIL", "detail": sorted(state_fields)})

    loyo = pd.read_csv(args.run_dir / "loyo_results.csv")
    loyo_summary = pd.read_csv(args.run_dir / "loyo_direction_summary.csv")
    recomputed = (
        loyo.groupby("zone", sort=False)["same_direction_as_full"].agg(["sum", "size"]).reset_index()
    )
    merged_loyo = loyo_summary.merge(recomputed, on="zone", validate="one_to_one")
    loyo_match = bool(
        (merged_loyo["same_direction_folds"] == merged_loyo["sum"]).all()
        and (merged_loyo["total_folds"] == merged_loyo["size"]).all()
    )
    checks.append({"check": "LOYO summary generated from fold rows", "status": "PASS" if loyo_match else "FAIL", "detail": loyo_summary.to_dict(orient="records")})

    python_coefficients = pd.read_csv(args.run_dir / "model_coefficients.csv")
    python_coefficients = python_coefficients.loc[
        python_coefficients["exposure"].eq("external_continuous")
        & python_coefficients["window"].eq("full_ext"),
        ["term", "estimate", "se_cluster_grid"],
    ]
    stata_coefficients = pd.read_csv(args.run_dir / "stata_replication_coefficients.csv")
    comparison = python_coefficients.merge(stata_coefficients, on="term", suffixes=("_python", "_stata"), validate="one_to_one")
    comparison["abs_beta_diff"] = np.abs(comparison["estimate_python"] - comparison["estimate_stata"])
    comparison["abs_se_diff"] = np.abs(comparison["se_cluster_grid_python"] - comparison["se_cluster_grid_stata"])
    comparison_path = args.run_dir / "stata_python_replication_comparison_round1.csv"
    if comparison_path.exists():
        raise FileExistsError(f"refusing to overwrite comparison: {comparison_path}")
    comparison.to_csv(comparison_path, index=False, lineterminator="\n")
    max_beta = float(comparison["abs_beta_diff"].max())
    max_se = float(comparison["abs_se_diff"].max())
    checks.append(
        {
            "check": "Stata reghdfe versus Python point/SE tolerance",
            "status": "PASS" if max_beta < 0.01 and max_se < 0.05 else "FAIL",
            "detail": {
                "terms": len(comparison),
                "max_abs_beta_diff": max_beta,
                "max_abs_se_diff": max_se,
                "stata_singletons_dropped": 2_287,
                "stata_nobs": 52_603,
                "python_input_nobs": 54_890,
                "explanation": "singleton grid observations have zero within contribution; Stata drops them explicitly",
            },
        }
    )

    bootstrap = pd.read_csv(args.run_dir / "wild_bootstrap_primary_results.csv")
    checks.append(
        {
            "check": "joint wild bootstrap contract",
            "status": "PASS" if len(bootstrap) == 15 and bootstrap["bootstrap_reps"].eq(1_999).all() and bootstrap["seed"].eq(42).all() else "FAIL",
            "detail": {"rows": len(bootstrap), "blocks": sorted(bootstrap["n_spatial_blocks"].unique().tolist())},
        }
    )
    hac = pd.read_csv(args.run_dir / "spatial_hac_primary_results.csv")
    checks.append(
        {
            "check": "100/200/300 km spatial HAC",
            "status": "PASS" if set(hac["bandwidth_km"]) == {100.0, 200.0, 300.0} and len(hac) == 15 else "FAIL",
            "detail": {"rows": len(hac)},
        }
    )
    units_ok = all(
        item["units"] in {"°C", "degC", "degree_Celsius", "m3.m-3", "m3 m-3", "m3/m3"}
        and item["date_axis_complete"]
        for item in run_manifest["cube_metadata"]
    )
    checks.append({"check": "cube units and date axes", "status": "PASS" if units_ok else "FAIL", "detail": run_manifest["cube_metadata"]})
    raster = run_manifest["raster"]
    raster_ok = (
        raster["driver"] == "GTiff"
        and raster["crs"] == "EPSG:4326"
        and raster["valid_cells"] == 5_627
        and abs(raster["valid_min_c"] - 26.8) < 1e-5
        and raster["valid_max_c"] == 44.0
    )
    checks.append({"check": "external raster metadata", "status": "PASS" if raster_ok else "FAIL", "detail": raster})
    for figure in [
        "fig1_conditional_yield_changes.png",
        "fig2_conditional_yield_changes_by_window.png",
        "fig3_conditional_smrz_responses.png",
        "fig4_sample_coverage_map.png",
    ]:
        with Image.open(args.run_dir / figure) as image:
            checks.append({"check": f"figure size {figure}", "status": "PASS" if image.size == (3_600, 1_500) else "FAIL", "detail": list(image.size)})

    failed = [item for item in checks if item["status"] != "PASS"]
    output_files = {}
    for path in sorted(args.run_dir.iterdir()):
        if path.is_file() and path != args.output:
            output_files[path.name] = {"bytes": path.stat().st_size, "sha256": file_hash(path)}
    manifest = {
        "canonical_id": run_manifest["canonical_id"],
        "run_id": run_manifest["run_id"],
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "PASS" if not failed else "FAIL",
        "checks": checks,
        "verification_files": [
            {"path": path.as_posix(), "bytes": path.stat().st_size, "sha256": file_hash(path)}
            for path in args.verification_files
        ],
        "run_files_after_stata_replication": output_files,
    }
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": manifest["status"], "checks": len(checks), "failed": len(failed)}))


if __name__ == "__main__":
    main()
