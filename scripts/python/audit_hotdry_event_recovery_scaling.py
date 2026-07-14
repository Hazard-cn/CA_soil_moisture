"""Audit recovery-v2 endpoint support and an algebraically equivalent scaled outcome model."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


ORIGINAL = (
    "recovered_now ~ time + time_sq + C(zone) + C(year) + ca + ca:C(zone) "
    "+ antecedent_smrz + duration_days + event_mean_excess_c + onset_doy"
)
SCALED = (
    "recovered_now ~ time_z + time_sq_z + C(zone) + C(year) + ca_z + ca_z:C(zone) "
    "+ antecedent_smrz_z + duration_days_z + event_mean_excess_c_z + onset_doy_z"
)


def digest(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    return {
        "path": str(path).replace("\\", "/"),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recovery-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source = args.recovery_dir.resolve()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(output)
    output.mkdir(parents=True, exist_ok=True)

    risk_path = source / "recovery_risk_set.csv.gz"
    risk = pd.read_csv(risk_path)
    continuous = [
        "time", "time_sq", "ca", "antecedent_smrz", "duration_days",
        "event_mean_excess_c", "onset_doy",
    ]
    scaling: dict[str, dict[str, float]] = {}
    for name in continuous:
        mean = float(risk[name].mean())
        sd = float(risk[name].std(ddof=0))
        if not np.isfinite(sd) or sd <= 0:
            raise ValueError(f"invalid scaling for {name}: {sd}")
        risk[f"{name}_z"] = (risk[name] - mean) / sd
        scaling[name] = {"mean": mean, "sd": sd}

    family = sm.families.Binomial(link=sm.families.links.CLogLog())
    original = smf.glm(ORIGINAL, data=risk, family=family, freq_weights=risk["ipcw"]).fit(
        maxiter=200, tol=1e-10
    )
    scaled = smf.glm(SCALED, data=risk, family=family, freq_weights=risk["ipcw"]).fit(
        maxiter=200, tol=1e-10
    )
    pred_original = np.asarray(original.predict(risk), dtype=float)
    pred_scaled = np.asarray(scaled.predict(risk), dtype=float)
    cond_original = float(np.linalg.cond(-original.model.hessian(original.params)))
    cond_scaled = float(np.linalg.cond(-scaled.model.hessian(scaled.params)))
    max_diff = float(np.max(np.abs(pred_original - pred_scaled)))
    summary = {
        "original_converged": bool(original.converged),
        "scaled_converged": bool(scaled.converged),
        "rows": int(len(risk)),
        "original_hessian_condition_number": cond_original,
        "scaled_hessian_condition_number": cond_scaled,
        "max_absolute_prediction_difference": max_diff,
        "equivalent_within_1e_10": bool(max_diff < 1e-10),
        "inference_use": "equivalence audit only; frozen recovery-v2 intervals remain unchanged",
    }
    (output / "scaling_equivalence.json").write_text(
        json.dumps({"summary": summary, "scaling": scaling}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    day0 = risk[risk["follow_day"] == 0].copy()
    rows = []
    for zone, part in list(day0.groupby("zone", sort=False)) + [("ALL", day0)]:
        recovered = int(part["recovered_now"].sum())
        rows.append({
            "zone": zone,
            "events_at_t0": int(len(part)),
            "recovered_at_t0": recovered,
            "proportion_recovered_at_t0": recovered / len(part),
        })
    support = pd.DataFrame(rows)
    support.to_csv(output / "recovery_endpoint_support.csv", index=False, encoding="utf-8-sig")

    manifest = {
        "contract_version": "run-manifest-v1",
        "canonical_id": "compound-event-intensity-duration-override-v1",
        "run_id": output.name,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "FULL_AUDIT",
        "not_for_inference": True,
        "design_version": "override-recovery-v2-scaling-audit-v1",
        "inputs": [digest(risk_path), digest(source / "run_manifest.json"), digest(Path(__file__).resolve())],
        "outputs": [digest(output / "scaling_equivalence.json"), digest(output / "recovery_endpoint_support.csv")],
        "claims": ["scaled and original parameterizations give equivalent fitted hazards; inference is not replaced"],
    }
    (output / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
