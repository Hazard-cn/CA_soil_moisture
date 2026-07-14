"""Estimate frozen recovery-v2 IPCW, standardized curves, and RMST30."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

from hotdry_event_override_models import (  # noqa: E402
    grouped_scores,
    rademacher_weights,
    romano_wolf_stepdown,
)
from hotdry_event_override_recovery_v2 import (  # noqa: E402
    build_recovery_v2_risk,
    stabilized_ipcw,
    standardized_survival,
)
from hotdry_event_override_validators import NAMED_ZONES, validate_override_manifest  # noqa: E402
from run_hotdry_event_override_recovery_audit import event_key_sha256  # noqa: E402
from run_hotdry_event_stage1 import file_digest, hash_artifacts  # noqa: E402


CANONICAL_ID = "compound-event-intensity-duration-override-v1"
NUMERATOR_FORMULA = "early_censor ~ time + time_sq + C(year)"
DENOMINATOR_FORMULA = (
    "early_censor ~ time + time_sq + C(zone) + C(year) + ca + antecedent_smrz "
    "+ duration_days + event_mean_excess_c + onset_doy"
)
OUTCOME_FORMULA = (
    "recovered_now ~ time + time_sq + C(zone) + C(year) + ca + ca:C(zone) "
    "+ antecedent_smrz + duration_days + event_mean_excess_c + onset_doy"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--stage1-dir", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--audit-v1-dir", type=Path, required=True)
    return parser.parse_args()


def fit_l2_censoring(formula: str, risk: pd.DataFrame) -> tuple[Any, Any]:
    model = smf.glm(formula, data=risk, family=sm.families.Binomial())
    result = model.fit_regularized(
        alpha=1e-6,
        L1_wt=0.0,
        maxiter=1_000,
        cnvrg_tol=1e-10,
    )
    if np.any(~np.isfinite(result.params)):
        raise FloatingPointError("L2 censoring model has non-finite parameters")
    prediction = np.asarray(result.predict(), dtype=float)
    if np.any(~np.isfinite(prediction)):
        raise FloatingPointError("L2 censoring model has non-finite predictions")
    return result, prediction


def block_codes(frame: pd.DataFrame) -> np.ndarray:
    longitude = np.floor((frame["longitude"].to_numpy(dtype=float) + 180.0) / 2.0).astype(int)
    latitude = np.floor((frame["latitude"].to_numpy(dtype=float) + 90.0) / 2.0).astype(int)
    codes, _ = pd.factorize(pd.Series(longitude.astype(str) + "|" + latitude.astype(str)), sort=True)
    return codes.astype(int)


def render_curves(curves: pd.DataFrame, path: Path) -> None:
    figure, axes = plt.subplots(1, 5, figsize=(12, 5), sharey=True)
    for axis, zone in zip(axes, NAMED_ZONES):
        part = curves[curves["zone"] == zone]
        for ca_label, color in (("P25", "#4c78a8"), ("P75", "#e45756")):
            line = part[part["ca_level"] == ca_label]
            axis.plot(line["follow_day"], line["survival"], label=f"CA {ca_label}", color=color)
            axis.fill_between(
                line["follow_day"],
                line["ci_low"],
                line["ci_high"],
                color=color,
                alpha=0.15,
                linewidth=0,
            )
        axis.set_title(zone)
        axis.set_xlabel("Day")
        axis.grid(color="#dddddd", linewidth=0.5)
    axes[0].set_ylabel("P(not recovered after day t)")
    axes[-1].legend(frameon=False, loc="upper right")
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
    model_dir = args.model_dir.resolve()
    audit_v1_dir = args.audit_v1_dir.resolve()

    model_manifest = json.loads((model_dir / "run_manifest.json").read_text(encoding="utf-8"))
    inputs = [dict(item) for item in model_manifest["inputs"]]
    for role, path in [
        ("implementation_recovery_core_v1", PROJECT_ROOT / "scripts/python/hotdry_event_override_recovery.py"),
        ("implementation_recovery_core_v2", PROJECT_ROOT / "scripts/python/hotdry_event_override_recovery_v2.py"),
        ("implementation_recovery_runner_v2", PROJECT_ROOT / "scripts/python/run_hotdry_event_override_recovery_v2.py"),
        ("test_override_recovery_audit", PROJECT_ROOT / "tests/test_hotdry_event_override_recovery.py"),
        ("test_override_recovery_v2", PROJECT_ROOT / "tests/test_hotdry_event_override_recovery_v2.py"),
        ("recovery_v2_frozen_appendix", PROJECT_ROOT / "quality_reports/plans/2026-07-15_hotdry_event_override_recovery_v2_frozen_appendix.md"),
        ("recovery_audit_v1_manifest", audit_v1_dir / "run_manifest.json"),
        ("recovery_audit_v1_diagnostics", audit_v1_dir / "censoring_model_diagnostics.json"),
    ]:
        inputs.append({"role": role, **file_digest(path.resolve())})

    event_panel = pd.read_csv(stage1_dir / "event_panel.csv.gz")
    events = event_panel[
        event_panel["event_indicator"] & event_panel["zone"].isin(NAMED_ZONES)
    ].copy()
    events["grid_id"] = events["grid_id"].astype(int)
    panel = pd.read_stata(
        panel_path,
        columns=["grid_id", "year", "ca", "latitude", "longitude"],
        convert_categoricals=False,
    )
    events = events.merge(panel, on=["grid_id", "year"], how="left", validate="many_to_one", suffixes=("", "_panel"))
    required = [
        "recovery_days",
        "recovery_observed",
        "right_censored",
        "antecedent_smrz",
        "duration_days",
        "event_mean_excess_c",
        "onset_doy",
        "ca",
        "latitude",
        "longitude",
    ]
    events = events.dropna(subset=required).copy()
    risk = build_recovery_v2_risk(events)

    numerator, p_numerator = fit_l2_censoring(NUMERATOR_FORMULA, risk)
    denominator, p_denominator = fit_l2_censoring(DENOMINATOR_FORMULA, risk)
    weights, weight_diagnostics = stabilized_ipcw(risk, p_numerator, p_denominator)
    if weight_diagnostics["upper_p99"] > 50:
        raise FloatingPointError("IPCW p99 exceeds frozen limit 50")
    risk["ipcw"] = weights

    outcome_model = smf.glm(
        OUTCOME_FORMULA,
        data=risk,
        family=sm.families.Binomial(link=sm.families.links.CLogLog()),
        freq_weights=risk["ipcw"],
    )
    outcome = outcome_model.fit(maxiter=200, tol=1e-10)
    if not bool(outcome.converged) or np.any(~np.isfinite(outcome.params)):
        raise RuntimeError("weighted cloglog did not converge with finite parameters")
    rank = int(np.linalg.matrix_rank(outcome.model.exog))
    if rank != outcome.model.exog.shape[1]:
        raise np.linalg.LinAlgError("weighted cloglog design is rank deficient")
    hessian = outcome.model.hessian(outcome.params)
    bread = np.linalg.inv(-hessian)
    score_obs = outcome.model.score_obs(outcome.params)
    codes = block_codes(risk)
    scores = grouped_scores(score_obs, np.ones(len(risk)), codes)
    weights_bootstrap = rademacher_weights(1_999, scores.shape[0], seed=42)
    beta_shocks = (weights_bootstrap @ scores) @ bread.T
    if np.any(~np.isfinite(beta_shocks)):
        raise FloatingPointError("wild-score update contains non-finite values")

    ca = model_manifest["ca_quantiles"]
    curve_rows: list[dict[str, Any]] = []
    rmst_by_zone: dict[str, dict[str, Any]] = {}
    design_info = outcome.model.data.design_info
    for zone in NAMED_ZONES:
        zone_events = events[events["zone"] == zone].copy()
        if zone_events.empty:
            raise ValueError(f"zone {zone} has no standardization events")
        rmst_by_zone[zone] = {}
        for label, value in (("P25", float(ca["p25"])), ("P75", float(ca["p75"]))):
            curve, curve_gradient, rmst, rmst_gradient = standardized_survival(
                outcome.params.to_numpy(dtype=float),
                design_info,
                zone_events,
                value,
            )
            curve_draws = curve[None, :] + beta_shocks @ curve_gradient.T
            for day in range(30):
                curve_rows.append(
                    {
                        "zone": zone,
                        "ca_level": label,
                        "ca_value": value,
                        "follow_day": day,
                        "survival": float(curve[day]),
                        "ci_low": max(0.0, float(np.quantile(curve_draws[:, day], 0.025))),
                        "ci_high": min(1.0, float(np.quantile(curve_draws[:, day], 0.975))),
                    }
                )
            rmst_by_zone[zone][label] = {
                "point": rmst,
                "gradient": rmst_gradient,
            }

    curve_frame = pd.DataFrame(curve_rows)
    curve_path = output_dir / "standardized_recovery_curves.csv"
    curve_frame.to_csv(curve_path, index=False, encoding="utf-8-sig")
    rmst_rows: list[dict[str, Any]] = []
    rmst_draw_columns: list[np.ndarray] = []
    rmst_points: list[float] = []
    for zone in NAMED_ZONES:
        low = rmst_by_zone[zone]["P25"]
        high = rmst_by_zone[zone]["P75"]
        difference = float(high["point"] - low["point"])
        gradient = np.asarray(high["gradient"]) - np.asarray(low["gradient"])
        draws = difference + beta_shocks @ gradient
        rmst_points.append(difference)
        rmst_draw_columns.append(draws)
        rmst_rows.append(
            {
                "zone": zone,
                "events": int((events["zone"] == zone).sum()),
                "rmst30_ca_p25": float(low["point"]),
                "rmst30_ca_p75": float(high["point"]),
                "rmst30_difference_p75_minus_p25": difference,
                "ci_low": float(np.quantile(draws, 0.025)),
                "ci_high": float(np.quantile(draws, 0.975)),
                "bootstrap_se": float(np.std(draws, ddof=1)),
            }
        )
    rmst_draws = np.column_stack(rmst_draw_columns)
    p_raw, p_rw, p_holm = romano_wolf_stepdown(np.asarray(rmst_points), rmst_draws)
    for row, raw, rw, holm in zip(rmst_rows, p_raw, p_rw, p_holm):
        row.update(p_raw=float(raw), p_romano_wolf=float(rw), p_holm=float(holm))
    rmst_frame = pd.DataFrame(rmst_rows)
    rmst_path = output_dir / "rmst30_results.csv"
    rmst_frame.to_csv(rmst_path, index=False, encoding="utf-8-sig")
    covariance_path = output_dir / "rmst30_bootstrap_covariance.csv"
    pd.DataFrame(np.cov(rmst_draws, rowvar=False, ddof=1), index=NAMED_ZONES, columns=NAMED_ZONES).to_csv(
        covariance_path,
        encoding="utf-8-sig",
    )

    censor_path = output_dir / "censoring_model_coefficients.csv"
    pd.concat(
        [
            pd.DataFrame({"model": "numerator", "term": numerator.params.index, "coefficient": numerator.params.to_numpy()}),
            pd.DataFrame({"model": "denominator", "term": denominator.params.index, "coefficient": denominator.params.to_numpy()}),
        ],
        ignore_index=True,
    ).to_csv(censor_path, index=False, encoding="utf-8-sig")
    outcome_path = output_dir / "recovery_cloglog_coefficients.csv"
    pd.DataFrame(
        {
            "term": outcome.params.index,
            "coefficient": outcome.params.to_numpy(),
            "model_se": outcome.bse.to_numpy(),
        }
    ).to_csv(outcome_path, index=False, encoding="utf-8-sig")
    diagnostic_path = output_dir / "recovery_v2_diagnostics.json"
    diagnostics = {
        "events": int(len(events)),
        "risk_rows_t0_t29": int(len(risk)),
        "early_censor_events": int(risk["early_censor"].sum()),
        "administrative_day30_events": int((events["censor_reason"] == "thirty-day-limit").sum()),
        "l2_alpha": 1e-6,
        "numerator_formula": NUMERATOR_FORMULA,
        "denominator_formula": DENOMINATOR_FORMULA,
        "outcome_formula": OUTCOME_FORMULA,
        "numerator_max_abs_coefficient": float(np.max(np.abs(numerator.params))),
        "denominator_max_abs_coefficient": float(np.max(np.abs(denominator.params))),
        "weight_diagnostics": weight_diagnostics,
        "outcome_converged": bool(outcome.converged),
        "outcome_columns": int(outcome.model.exog.shape[1]),
        "outcome_rank": rank,
        "outcome_hessian_condition": float(np.linalg.cond(-hessian)),
        "spatial_blocks": int(scores.shape[0]),
        "bootstrap_repetitions": 1_999,
        "bootstrap_note": "fixed-IPCW one-step weighted-cloglog wild-score with analytic standardization gradient",
    }
    diagnostic_path.write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2), encoding="utf-8")

    risk_path = output_dir / "recovery_risk_set.csv.gz"
    risk.to_csv(risk_path, index=False, compression={"method": "gzip", "mtime": 0}, encoding="utf-8")
    figure_path = output_dir / "figure_standardized_recovery_curves.png"
    render_curves(curve_frame, figure_path)
    performance_path = output_dir / "performance.json"
    performance_path.write_text(
        json.dumps({"elapsed_seconds_before_manifest": time.perf_counter() - started}, indent=2),
        encoding="utf-8",
    )

    decision = {
        "stage": "recovery_v2_ipcw_cloglog_rmst",
        "status": "PASS_RECOVERY_V2",
        "support_thresholds_blocking": False,
        "ipcw_generated": True,
        "standardized_curves_generated": True,
        "rmst30_generated": True,
        "bootstrap_generated": True,
    }
    decision_path = output_dir / "recovery_stage_decision.json"
    decision_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")

    artifacts = [
        curve_path,
        rmst_path,
        covariance_path,
        censor_path,
        outcome_path,
        diagnostic_path,
        risk_path,
        figure_path,
        performance_path,
        decision_path,
    ]
    extension = {
        "contract_version": "compound-event-override-recovery-v2-extension-v1",
        "stage": "recovery_v2_ipcw_cloglog_rmst",
        "failure_stage": None,
        "failure_reasons": [],
        "completed_artifacts": hash_artifacts(artifacts, output_dir),
        "yield_model_run": True,
        "ipcw_rmst_run": True,
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
        "design_version": "override-recovery-v2",
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True).strip(),
        "data_family": "V3",
        "inputs": inputs,
        "sample_predicate": "five named-zone events with complete frozen recovery fields; t=0..29 risk rows; day30 administrative censor",
        "sample_key_serialization": "sort(grid_id string,year,event_seq); UTF-8 grid_id|YYYY|event_seq\\n",
        "sample_key_sha256": event_key_sha256(events),
        "sample_counts": {
            "events": int(len(events)),
            "risk_rows": int(len(risk)),
            "early_censor_events": int(risk["early_censor"].sum()),
            "administrative_day30_events": int((events["censor_reason"] == "thirty-day-limit").sum()),
        },
        "outcome": "30-day recovery hazard and RMST30",
        "exposure_definition": "CA P25/P75 standardized recovery to 90% of antecedent SMrz after fixed hot-dry events",
        "soil_moisture_roles": ["antecedent SMrz", "drawdown SMrz", "IPCW recovery and RMST30"],
        "fixed_effects": ["quadratic follow time", "zone", "year", "CA-by-zone"],
        "inference": {
            "primary": "2-degree spatial-block Rademacher one-step wild-score; fixed IPCW; analytic standardization gradient",
            "bootstrap_reps": 1_999,
            "spatial_block_degrees": 2,
            "spatial_hac_km": [100, 200, 300],
            "multiplicity": "five-zone RMST30 Romano-Wolf stepdown; Holm verification",
        },
        "ca_quantiles": model_manifest["ca_quantiles"],
        "exposure_endpoints": model_manifest["exposure_endpoints"],
        "seed": 42,
        "claims": ["conditional recovery associations only; not causal mediation"],
        "stop_rules_triggered": [],
        "verification": [
            {"check": "runtime interpreter", "status": "PASS", "detail": f"{sys.executable}; Python {sys.version.split()[0]}"},
            {"check": "administrative censoring", "status": "PASS", "detail": "day30 excluded from stochastic censor hazard"},
            {"check": "L2 censoring models", "status": "PASS", "detail": "alpha=1e-6 fixed before execution; finite parameters and probabilities"},
            {"check": "IPCW", "status": "PASS", "detail": f"p99={weight_diagnostics['upper_p99']:.6f}; clipped ESS={weight_diagnostics['clipped_ess']:.1f}"},
            {"check": "weighted cloglog", "status": "PASS", "detail": f"rank={rank}/{outcome.model.exog.shape[1]}; Hessian condition={np.linalg.cond(-hessian):.3f}"},
            {"check": "joint spatial bootstrap", "status": "PASS", "detail": f"{scores.shape[0]} blocks; 1999 draws; seed 42"},
        ],
    }
    schema = json.loads((PROJECT_ROOT / "docs/contracts/run_manifest.schema.json").read_text(encoding="utf-8"))
    validate_override_manifest(manifest, schema, extension=extension)
    manifest_path = output_dir / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(rmst_frame.to_json(orient="records", force_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
