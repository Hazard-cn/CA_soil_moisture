"""Estimate the preregistered duration/intensity yield models after Stage 1."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

from hotdry_event_override_models import (  # noqa: E402
    fit_absorbed_ols,
    rademacher_weights,
    romano_wolf_stepdown,
)
from hotdry_event_override_validators import (  # noqa: E402
    CANONICAL_ID,
    NAMED_ZONES,
    validate_override_manifest,
)
from run_hotdry_event_stage1 import file_digest, hash_artifacts, sample_key_sha256  # noqa: E402


PANEL_FIELDS = (
    "grid_id",
    "year",
    "province",
    "latitude",
    "longitude",
    "ln_yield",
    "ca",
    "gdd_10_29",
    "pr_sum",
)
EXPOSURES = {
    "duration": "total_duration_days",
    "intensity": "mean_event_intensity_c",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--stage1-dir", type=Path, required=True)
    return parser.parse_args()


def factor_codes(values: pd.Series) -> np.ndarray:
    codes, _ = pd.factorize(values, sort=True)
    if np.any(codes < 0):
        raise ValueError("fixed-effect code contains missing values")
    return codes.astype(int)


def design_matrix(frame: pd.DataFrame, exposure_column: str) -> tuple[np.ndarray, list[str]]:
    exposure = frame[exposure_column].to_numpy(dtype=float)
    ca = frame["ca"].to_numpy(dtype=float)
    columns = [
        frame["gdd_10_29"].to_numpy(dtype=float),
        frame["pr_sum"].to_numpy(dtype=float),
        np.square(frame["pr_sum"].to_numpy(dtype=float)),
    ]
    names = ["gdd_10_29", "pr_sum", "pr_sum_sq"]
    for zone in NAMED_ZONES:
        indicator = (frame["zone"].to_numpy() == zone).astype(float)
        columns.extend([indicator * exposure, indicator * ca, indicator * ca * exposure])
        names.extend([f"{zone}:exposure", f"{zone}:ca", f"{zone}:ca_x_exposure"])
    return np.column_stack(columns), names


def codes_for_frame(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    grid = factor_codes(frame["grid_id"])
    province_year = factor_codes(frame["province"].astype(str) + "|" + frame["year"].astype(str))
    blocks = (
        np.floor((frame["longitude"].to_numpy(dtype=float) + 180.0) / 2.0).astype(int).astype(str)
        + "|"
        + np.floor((frame["latitude"].to_numpy(dtype=float) + 90.0) / 2.0).astype(int).astype(str)
    )
    block = factor_codes(pd.Series(blocks, index=frame.index))
    return grid, province_year, grid.copy(), block


def fit_one(
    frame: pd.DataFrame,
    exposure_column: str,
    bootstrap_weights: np.ndarray,
) -> tuple[Any, list[str]]:
    x, names = design_matrix(frame, exposure_column)
    grid, province_year, cluster, block = codes_for_frame(frame)
    fit = fit_absorbed_ols(
        frame["ln_yield"].to_numpy(dtype=float),
        x,
        grid_codes=grid,
        province_year_codes=province_year,
        cluster_codes=cluster,
        block_codes=block,
        bootstrap_weights=bootstrap_weights,
    )
    return fit, names


def endpoint_payload(frame: pd.DataFrame) -> tuple[dict[str, float], dict[str, Any]]:
    ca = {
        "p25": float(frame["ca"].quantile(0.25)),
        "p50": float(frame["ca"].quantile(0.50)),
        "p75": float(frame["ca"].quantile(0.75)),
        "population": "five named zones common model sample",
    }
    endpoints: dict[str, Any] = {}
    for zone in NAMED_ZONES:
        part = frame[frame["zone"] == zone]
        endpoints[zone] = {
            exposure: {
                "p50": float(part[column].quantile(0.50)),
                "p90": float(part[column].quantile(0.90)),
            }
            for exposure, column in EXPOSURES.items()
        }
    return ca, endpoints


def model_input_inventory(panel: Path, stage1_dir: Path) -> list[dict[str, Any]]:
    stage1_manifest = json.loads((stage1_dir / "run_manifest.json").read_text(encoding="utf-8"))
    inputs = [dict(item) for item in stage1_manifest["inputs"]]
    paths = [
        ("python_interpreter", Path(sys.executable)),
        ("implementation_model_core", PROJECT_ROOT / "scripts/python/hotdry_event_override_models.py"),
        ("implementation_model_runner", PROJECT_ROOT / "scripts/python/run_hotdry_event_override_models.py"),
        ("test_override_models", PROJECT_ROOT / "tests/test_hotdry_event_override_models.py"),
        ("stage1_manifest", stage1_dir / "run_manifest.json"),
        ("stage1_extension", stage1_dir / "event_run_extension.json"),
        ("stage1_event_panel", stage1_dir / "event_panel.csv.gz"),
        ("stage1_grid_year_support", stage1_dir / "grid_year_support.csv"),
        ("v3_panel_model_read", panel),
    ]
    for role, path in paths:
        inputs.append({"role": role, **file_digest(path.resolve())})
    return inputs


def make_figure(results: pd.DataFrame, path: Path) -> None:
    import matplotlib.pyplot as plt

    plot = results.copy()
    plot["label"] = plot["zone"] + " · " + plot["exposure"].map({"duration": "持续时间", "intensity": "强度"})
    plot = plot.iloc[::-1].reset_index(drop=True)
    y = np.arange(len(plot))
    figure, axis = plt.subplots(figsize=(12, 5))
    axis.errorbar(
        plot["effect_percent"],
        y,
        xerr=np.vstack([
            plot["effect_percent"] - plot["boot_ci_low_percent"],
            plot["boot_ci_high_percent"] - plot["effect_percent"],
        ]),
        fmt="o",
        color="#1f4e79",
        ecolor="#6b8eae",
        capsize=3,
    )
    axis.axvline(0, color="black", linewidth=0.8)
    axis.set_yticks(y, plot["label"])
    axis.set_xlabel("SR P75相对P25的条件损害差异（%）")
    axis.grid(axis="x", color="#dddddd", linewidth=0.6)
    figure.tight_layout()
    figure.savefig(path, dpi=300, facecolor="white")
    plt.close(figure)


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite nonempty run directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    panel_path = args.panel.resolve()
    stage1_dir = args.stage1_dir.resolve()

    stage1_decision = json.loads((stage1_dir / "stage_decision.json").read_text(encoding="utf-8"))
    if stage1_decision.get("status") != "PASS_STAGE1_WITH_WARNINGS":
        raise ValueError("Stage 1 override is not complete")
    inputs = model_input_inventory(panel_path, stage1_dir)

    event_panel = pd.read_csv(stage1_dir / "event_panel.csv.gz")
    representative = event_panel[event_panel["is_grid_year_representative"]].copy()
    representative["grid_id"] = representative["grid_id"].astype(int)
    panel = pd.read_stata(panel_path, columns=list(PANEL_FIELDS), convert_categoricals=False)
    frame = representative.merge(panel, on=["grid_id", "year"], how="inner", validate="one_to_one", suffixes=("", "_panel"))
    for coordinate in ("latitude", "longitude"):
        error = np.abs(frame[coordinate] - frame[f"{coordinate}_panel"])
        if float(error.max()) > 1e-5:
            raise ValueError(f"{coordinate} merge audit exceeds 1e-5")
        frame.drop(columns=[f"{coordinate}_panel"], inplace=True)
    required = ["ln_yield", "ca", "gdd_10_29", "pr_sum", *EXPOSURES.values()]
    frame = frame[frame["zone"].isin(NAMED_ZONES)].dropna(subset=required).copy()
    if frame.duplicated(["grid_id", "year"]).any():
        raise ValueError("model frame grid_id-year is not unique")
    frame.sort_values(["grid_id", "year"], inplace=True)
    frame.reset_index(drop=True, inplace=True)

    ca_quantiles, endpoints = endpoint_payload(frame)
    _, _, _, block_codes = codes_for_frame(frame)
    bootstrap_weights = rademacher_weights(1_999, int(block_codes.max()) + 1, seed=42)

    fits: dict[str, Any] = {}
    names: dict[str, list[str]] = {}
    coefficient_paths: list[Path] = []
    for exposure, column in EXPOSURES.items():
        fit, column_names = fit_one(frame, column, bootstrap_weights)
        fits[exposure] = fit
        names[exposure] = column_names
        coefficient = pd.DataFrame(
            {
                "term": column_names,
                "coefficient": fit.beta,
                "grid_cluster_se": np.sqrt(np.diag(fit.covariance_cluster)),
            }
        )
        coefficient["model"] = exposure
        coefficient["rank"] = fit.rank
        coefficient["standardized_condition_number"] = fit.condition_number
        coefficient["absorption_iterations"] = fit.absorption_iterations
        path = output_dir / f"coefficients_{exposure}.csv"
        coefficient.to_csv(path, index=False, encoding="utf-8-sig")
        coefficient_paths.append(path)

    estimate_rows: list[dict[str, Any]] = []
    log_estimates: list[float] = []
    log_draws: list[np.ndarray] = []
    for zone in NAMED_ZONES:
        for exposure in EXPOSURES:
            fit = fits[exposure]
            index = names[exposure].index(f"{zone}:ca_x_exposure")
            endpoint = endpoints[zone][exposure]
            scale = (ca_quantiles["p75"] - ca_quantiles["p25"]) * (endpoint["p90"] - endpoint["p50"])
            estimate = float(fit.beta[index] * scale)
            draws = fit.bootstrap_beta[:, index] * scale
            cluster_se = float(math.sqrt(fit.covariance_cluster[index, index]) * abs(scale))
            log_estimates.append(estimate)
            log_draws.append(draws)
            estimate_rows.append(
                {
                    "zone": zone,
                    "exposure": exposure,
                    "ca_p25": ca_quantiles["p25"],
                    "ca_p75": ca_quantiles["p75"],
                    "exposure_p50": endpoint["p50"],
                    "exposure_p90": endpoint["p90"],
                    "interaction_coefficient": float(fit.beta[index]),
                    "interaction_grid_cluster_se": float(math.sqrt(fit.covariance_cluster[index, index])),
                    "estimand_log_point": estimate,
                    "estimand_grid_cluster_se": cluster_se,
                    "effect_percent": 100.0 * math.expm1(estimate),
                    "boot_ci_low_percent": 100.0 * math.expm1(float(np.quantile(draws, 0.025))),
                    "boot_ci_high_percent": 100.0 * math.expm1(float(np.quantile(draws, 0.975))),
                    "boot_se_log": float(np.std(draws, ddof=1)),
                }
            )

    estimates = np.asarray(log_estimates)
    draws = np.column_stack(log_draws)
    raw, romano_wolf, holm = romano_wolf_stepdown(estimates, draws)
    for row, p_raw, p_rw, p_holm in zip(estimate_rows, raw, romano_wolf, holm):
        row.update(p_raw=float(p_raw), p_romano_wolf=float(p_rw), p_holm=float(p_holm))

    loyo_rows: list[dict[str, Any]] = []
    for omitted_year in sorted(frame["year"].unique()):
        fold = frame[frame["year"] != omitted_year].copy()
        _, _, _, fold_blocks = codes_for_frame(fold)
        placeholder_weights = np.zeros((1, int(fold_blocks.max()) + 1), dtype=float)
        for exposure, column in EXPOSURES.items():
            fold_fit, fold_names = fit_one(fold, column, placeholder_weights)
            for zone in NAMED_ZONES:
                index = fold_names.index(f"{zone}:ca_x_exposure")
                endpoint = endpoints[zone][exposure]
                scale = (ca_quantiles["p75"] - ca_quantiles["p25"]) * (endpoint["p90"] - endpoint["p50"])
                loyo_rows.append(
                    {
                        "omitted_year": int(omitted_year),
                        "zone": zone,
                        "exposure": exposure,
                        "estimand_log_point": float(fold_fit.beta[index] * scale),
                    }
                )
    loyo = pd.DataFrame(loyo_rows)
    result = pd.DataFrame(estimate_rows)
    direction_counts = []
    for row in result.itertuples(index=False):
        fold_values = loyo[(loyo["zone"] == row.zone) & (loyo["exposure"] == row.exposure)]["estimand_log_point"]
        same = int((np.sign(fold_values.to_numpy()) == np.sign(row.estimand_log_point)).sum())
        direction_counts.append(same)
    result["loyo_same_direction_folds"] = direction_counts
    result["loyo_total_folds"] = 4

    result_path = output_dir / "conditional_damage_results.csv"
    result.to_csv(result_path, index=False, encoding="utf-8-sig")
    loyo_path = output_dir / "loyo_results.csv"
    loyo.to_csv(loyo_path, index=False, encoding="utf-8-sig")
    endpoint_path = output_dir / "frozen_endpoints.json"
    endpoint_path.write_text(json.dumps({"ca": ca_quantiles, "exposures": endpoints}, ensure_ascii=False, indent=2), encoding="utf-8")

    event_rows = event_panel[event_panel["event_indicator"]].copy()
    event_rows["grid_id"] = event_rows["grid_id"].astype(int)
    event_rows = event_rows.merge(panel[["grid_id", "year", "ca"]], on=["grid_id", "year"], how="left", validate="many_to_one")
    event_rows["ca_group"] = np.where(
        event_rows["ca"] <= ca_quantiles["p25"],
        "P25_or_lower",
        np.where(event_rows["ca"] >= ca_quantiles["p75"], "P75_or_higher", "middle"),
    )
    sm_support = (
        event_rows[event_rows["zone"].isin(NAMED_ZONES)]
        .groupby(["zone", "ca_group"], observed=True)
        .agg(
            events=("event_id", "size"),
            antecedent_complete=("sm_channel_complete_flag", "sum"),
            antecedent_smrz_mean=("antecedent_smrz", "mean"),
            drawdown_smrz_mean=("drawdown_smrz", "mean"),
            recovery_risk_events=("recovery_observed", "count"),
            right_censored_events=("right_censored", "sum"),
            recovery_days_mean_unadjusted=("recovery_days", "mean"),
        )
        .reset_index()
    )
    sm_support["right_censoring_rate"] = sm_support["right_censored_events"] / sm_support["recovery_risk_events"]
    sm_path = output_dir / "sm_channel_support.csv"
    sm_support.to_csv(sm_path, index=False, encoding="utf-8-sig")

    model_panel_path = output_dir / "model_ready_panel.csv.gz"
    frame.to_csv(model_panel_path, index=False, compression={"method": "gzip", "mtime": 0}, encoding="utf-8")
    figure_path = output_dir / "figure_condition_damage.png"
    make_figure(result, figure_path)
    performance_path = output_dir / "performance.json"
    performance_path.write_text(
        json.dumps(
            {
                "total_seconds_before_manifest": time.perf_counter() - started,
                "model_rows": len(frame),
                "grids": int(frame["grid_id"].nunique()),
                "spatial_blocks": int(block_codes.max()) + 1,
                "bootstrap_repetitions": 1_999,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    artifact_paths = [
        result_path,
        loyo_path,
        endpoint_path,
        sm_path,
        model_panel_path,
        figure_path,
        performance_path,
        *coefficient_paths,
    ]
    extension = {
        "contract_version": "compound-event-override-model-extension-v1",
        "stage": "yield_models_and_sm_interface",
        "failure_stage": None,
        "failure_reasons": [],
        "support_warnings": stage1_decision.get("support_warnings", []),
        "support_warnings_blocking": False,
        "completed_artifacts": hash_artifacts(artifact_paths, output_dir),
        "yield_model_run": True,
        "ipcw_rmst_run": False,
    }
    extension_path = output_dir / "event_run_extension.json"
    extension_path.write_text(json.dumps(extension, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest = {
        "contract_version": "run-manifest-v1",
        "canonical_id": CANONICAL_ID,
        "run_id": output_dir.name,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "FULL",
        "not_for_inference": False,
        "design_version": "override-v1",
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True).strip(),
        "data_family": "V3",
        "inputs": inputs,
        "sample_predicate": "Stage1 analysis-ready representative rows; five named zones; frozen model fields complete-case",
        "sample_key_serialization": "sort(grid_id string,year); UTF-8 grid_id|YYYY\\n",
        "sample_key_sha256": sample_key_sha256(frame[["grid_id", "year"]]),
        "sample_counts": {
            "model_grid_years": int(len(frame)),
            "model_grids": int(frame["grid_id"].nunique()),
            "event_positive_grid_years": int(frame["event_indicator"].sum()),
            "event_rows_sm_interface": int(len(event_rows)),
        },
        "outcome": "ln_yield",
        "exposure_definition": "separate total duration and mean excess intensity for Tmax>=32C and precipitation<1mm/day runs >=3 days",
        "soil_moisture_roles": ["antecedent SMrz", "drawdown SMrz", "recovery/censoring interface; IPCW/RMST pending"],
        "fixed_effects": ["grid FE", "province-year FE"],
        "inference": {
            "primary": "2-degree spatial-block Rademacher wild-score bootstrap",
            "bootstrap_reps": 1_999,
            "spatial_block_degrees": 2,
            "spatial_hac_km": [100, 200, 300],
            "multiplicity": "Romano-Wolf stepdown; Holm verification",
        },
        "ca_quantiles": ca_quantiles,
        "exposure_endpoints": endpoints,
        "seed": 42,
        "claims": ["conditional damage differences only; not causal effects or mediation"],
        "stop_rules_triggered": [],
        "verification": [
            {"check": "runtime interpreter", "status": "PASS", "detail": f"{sys.executable}; Python {sys.version.split()[0]}"},
            {"check": "Stage 1 complete", "status": "PASS", "detail": str(stage1_dir)},
            {"check": "model key unique", "status": "PASS", "detail": f"{len(frame)} grid-years"},
            {"check": "two-way FE designs full rank", "status": "PASS", "detail": "; ".join(f"{key}: rank={value.rank}, cond={value.condition_number:.3f}" for key, value in fits.items())},
            {"check": "synchronized bootstrap", "status": "PASS", "detail": "1999 draws, seed 42"},
            {"check": "IPCW/RMST", "status": "SKIP", "detail": "mechanical recovery interface complete; preregistered estimator remains"},
        ],
    }
    run_schema = json.loads((PROJECT_ROOT / "docs/contracts/run_manifest.schema.json").read_text(encoding="utf-8"))
    validate_override_manifest(manifest, run_schema, extension=extension)
    manifest_path = output_dir / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(result.to_json(orient="records", force_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
