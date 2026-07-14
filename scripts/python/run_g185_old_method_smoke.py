"""Run the non-inferential G185 old-method smoke test."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from jsonschema import Draft202012Validator, FormatChecker

from g185_old_method_core import (
    BASE_COLUMNS,
    EXPECTED_BASE_SHA256,
    EXPECTED_HOTDRY_SHA256,
    CANONICAL_SERIALIZER_VERSION,
    EXPECTED_CANONICAL_SAMPLE_KEY_SHA256,
    EXPECTED_LEGACY_SAMPLE_KEY_SHA256,
    HAC_BANDWIDTHS_KM,
    HAZARDS,
    REGIONS,
    LEGACY_SERIALIZER_VERSION,
    TEST_ORDER,
    algebraic_components,
    apply_g185_predicate,
    assert_frozen_sample,
    conley_covariance,
    delta_components,
    draw_wild_weights,
    ensure_new_output_dir,
    fit_absorbed_model,
    hazard_spec,
    legacy_sample_key_sha256,
    omnibus_region_tests,
    output_hashes,
    prepare_analysis_columns,
    romano_wolf_stepdown,
    sample_key_sha256,
    score_bootstrap_betas,
    select_smoke_panel,
    sha256_file,
    validate_drought_wet_definitions,
)


FROZEN_FES = ("grid_year", "grid_provyear")
FROZEN_SCORE_CLUSTERS = ("grid", "spatial_block")
FROZEN_METHODS = (
    "grid_rademacher",
    "spatial_block_rademacher",
    "spatial_block_webb",
)
METHOD_DIAGNOSTIC_KEYS = {
    "grid_rademacher": (
        "grid_rademacher_shape",
        "grid_rademacher_covariance_rank",
        "romano_wolf_grid_rademacher_count",
        "romano_wolf_grid_rademacher_finite_count",
        "omnibus_grid_rademacher",
    ),
    "spatial_block_rademacher": (
        "rademacher_shape",
        "rademacher_covariance_rank",
        "romano_wolf_rademacher_count",
        "romano_wolf_rademacher_finite_count",
        "omnibus_rademacher",
    ),
    "spatial_block_webb": (
        "webb_shape",
        "webb_covariance_rank",
        "romano_wolf_webb_count",
        "romano_wolf_webb_finite_count",
        "omnibus_webb",
    ),
}


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(description=__doc__)
    out.add_argument("--project-root", type=Path, required=True)
    out.add_argument("--worktree-root", type=Path, required=True)
    out.add_argument("--base-dta", type=Path, required=True)
    out.add_argument("--hotdry-dta", type=Path, required=True)
    out.add_argument("--output-dir", type=Path, required=True)
    out.add_argument("--fe", choices=("grid_year", "grid_provyear"), action="append")
    out.add_argument("--score-cluster", choices=("grid", "spatial_block"), action="append")
    out.add_argument("--block-degrees", type=float, default=2.0)
    out.add_argument("--reps", type=int, choices=(19, 39), default=19)
    out.add_argument("--seed", type=int, default=42)
    out.add_argument("--grids-per-region", type=int, default=120)
    return out


def validate_cli_contract(args: argparse.Namespace) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Allow only the complete frozen FE and score-cluster smoke combination."""
    fes = tuple(dict.fromkeys(args.fe or FROZEN_FES))
    clusters = tuple(dict.fromkeys(args.score_cluster or FROZEN_SCORE_CLUSTERS))
    if len(fes) != len(FROZEN_FES) or set(fes) != set(FROZEN_FES):
        raise ValueError(f"smoke requires the complete fixed-effect set: {FROZEN_FES}")
    if len(clusters) != len(FROZEN_SCORE_CLUSTERS) or set(clusters) != set(FROZEN_SCORE_CLUSTERS):
        raise ValueError(
            f"smoke requires the complete score-cluster set: {FROZEN_SCORE_CLUSTERS}"
        )
    if args.block_degrees != 2.0:
        raise ValueError("frozen smoke contract requires --block-degrees 2")
    if args.seed != 42:
        raise ValueError("frozen smoke contract requires --seed 42")
    return FROZEN_FES, FROZEN_SCORE_CLUSTERS


def summarize_hac_status(registry: pd.DataFrame) -> dict[str, object]:
    expected_rows = len(FROZEN_FES) * len(TEST_ORDER)
    if len(registry) != expected_rows:
        raise AssertionError(f"HAC registry rows {len(registry)} != {expected_rows}")
    if registry.duplicated(["fe", "region", "hazard"]).any():
        raise AssertionError("HAC registry contains duplicate FE-region-hazard cells")
    expected_bandwidths = {str(int(value)) for value in HAC_BANDWIDTHS_KM}
    finite_count = 0
    status_items = 0
    for row in registry.itertuples(index=False):
        status = json.loads(row.hac_status)
        if set(status) != expected_bandwidths:
            raise AssertionError(
                f"HAC bandwidth set mismatch for {row.fe}/{row.region}/{row.hazard}: {set(status)}"
            )
        for bandwidth in expected_bandwidths:
            for equation in ("mediator", "yield"):
                key = f"{equation}_finite"
                if key not in status[bandwidth] or not isinstance(status[bandwidth][key], bool):
                    raise AssertionError(f"missing boolean HAC status: {bandwidth}/{key}")
                status_items += 1
                finite_count += int(status[bandwidth][key])
    expected_items = len(FROZEN_FES) * len(TEST_ORDER) * len(HAC_BANDWIDTHS_KM) * 2
    if status_items != expected_items or finite_count != expected_items:
        raise RuntimeError(
            f"HAC completion failed: finite={finite_count}, actual={status_items}, expected={expected_items}"
        )
    return {
        "status_items": status_items,
        "expected_items": expected_items,
        "finite_items": finite_count,
        "all_finite": finite_count == expected_items,
    }


def validate_completion_contract(
    declaration: dict[str, object], diagnostics: dict[str, object]
) -> dict[str, object]:
    """Bind declared FE/method pairs to completed B-by-15 diagnostics."""
    declared_fes = tuple(declaration.get("fixed_effects", []))
    declared_methods = tuple(declaration.get("methods", []))
    reps = int(declaration.get("bootstrap_reps", -1))
    dimension = int(declaration.get("test_dimension", -1))
    if declared_fes != FROZEN_FES or declared_methods != FROZEN_METHODS:
        raise AssertionError("manifest completion declaration is not the frozen FE-by-method set")
    if set(diagnostics) != set(declared_fes):
        raise AssertionError("diagnostic fixed effects do not match manifest declaration")
    completed: list[str] = []
    for fe in declared_fes:
        diag = diagnostics[fe]
        if int(diag.get("dimension", -1)) != dimension or dimension != 15:
            raise AssertionError(f"invalid diagnostic dimension for {fe}")
        for method in declared_methods:
            shape_key, rank_key, rw_count_key, rw_finite_key, omnibus_key = METHOD_DIAGNOSTIC_KEYS[
                method
            ]
            if diag.get(shape_key) != [reps, dimension]:
                raise AssertionError(f"{fe}/{method} does not have B-by-15 draws")
            if int(diag.get(rank_key, -1)) != dimension:
                raise AssertionError(f"{fe}/{method} covariance rank is not 15")
            if int(diag.get(rw_count_key, -1)) != dimension:
                raise AssertionError(f"{fe}/{method} Romano-Wolf count is not 15")
            if int(diag.get(rw_finite_key, -1)) != dimension:
                raise AssertionError(f"{fe}/{method} Romano-Wolf finite count is not 15")
            omnibus = diag.get(omnibus_key)
            if not isinstance(omnibus, list) or [row.get("hazard") for row in omnibus] != list(HAZARDS):
                raise AssertionError(f"{fe}/{method} omnibus hazard set/order is invalid")
            if not all(
                int(row.get("rank", -1)) == 4
                and row.get("finite") is True
                and row.get("holm_finite") is True
                for row in omnibus
            ):
                raise AssertionError(f"{fe}/{method} omnibus completion is invalid")
            completed.append(f"{fe}:{method}")
    expected_pairs = [f"{fe}:{method}" for fe in FROZEN_FES for method in FROZEN_METHODS]
    if completed != expected_pairs:
        raise AssertionError("completed FE-by-method pair order/set mismatch")
    return {"completed_pairs": completed, "pair_count": len(completed), "status": "PASS"}


def validate_contract_manifest(instance: dict[str, object], schema_path: Path) -> dict[str, str]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.absolute_path))
    if errors:
        detail = "; ".join(
            f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
            for error in errors
        )
        raise AssertionError(f"run_manifest schema validation failed: {detail}")
    return {
        "validator": "jsonschema.Draft202012Validator",
        "schema_sha256": sha256_file(schema_path),
        "schema_path": str(schema_path.resolve()),
    }


def read_inputs(base_dta: Path, hotdry_dta: Path) -> pd.DataFrame:
    base = pd.read_stata(base_dta, columns=list(BASE_COLUMNS), convert_categoricals=True)
    hotdry = pd.read_stata(
        hotdry_dta,
        columns=["grid_id", "year", "hotdrydays_ge32_pr_lt1"],
        convert_categoricals=False,
    )
    if base.duplicated(["grid_id", "year"]).any():
        raise AssertionError("base grid_id/year is not unique")
    if hotdry.duplicated(["grid_id", "year"]).any():
        raise AssertionError("hot-dry grid_id/year is not unique")
    merged = base.merge(hotdry, on=["grid_id", "year"], how="left", validate="one_to_one", indicator=True)
    if not merged["_merge"].eq("both").all():
        raise AssertionError("hot-dry one-to-one left merge has unmatched base rows")
    merged.drop(columns="_merge", inplace=True)
    merged.rename(columns={"hotdrydays_ge32_pr_lt1": "HotDryPr_full"}, inplace=True)
    return merged


def git_commit(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def run(args: argparse.Namespace, output_dir: Path) -> None:
    fes, clusters = validate_cli_contract(args)
    project_root = args.project_root.resolve(strict=True)
    worktree_root = args.worktree_root.resolve(strict=True)
    if project_root == worktree_root:
        raise ValueError("project-root and worktree-root must be distinct")
    log: list[str] = ["NOT_FOR_INFERENCE", "G185 old-method smoke test started"]

    base_hash = sha256_file(args.base_dta)
    hotdry_hash = sha256_file(args.hotdry_dta)
    if base_hash != EXPECTED_BASE_SHA256 or hotdry_hash != EXPECTED_HOTDRY_SHA256:
        raise AssertionError("input SHA-256 does not match frozen design")
    panel = read_inputs(args.base_dta, args.hotdry_dta)
    dw = validate_drought_wet_definitions(panel)
    sample, waterfall = apply_g185_predicate(panel)
    sample = prepare_analysis_columns(sample)
    sample_hash = sample_key_sha256(sample[["grid_id", "year"]])
    legacy_sample_hash = legacy_sample_key_sha256(sample[["grid_id", "year"]])
    if sample_hash != EXPECTED_CANONICAL_SAMPLE_KEY_SHA256:
        raise AssertionError(f"canonical sample-key SHA-256 mismatch: {sample_hash}")
    if legacy_sample_hash != EXPECTED_LEGACY_SAMPLE_KEY_SHA256:
        raise AssertionError(f"legacy sample-key SHA-256 mismatch: {legacy_sample_hash}")
    sample_checks = assert_frozen_sample(sample)
    named = sample.loc[sample["maize_zone"].astype(str).isin(REGIONS)].copy()
    smoke = select_smoke_panel(named, args.grids_per_region)
    log.append(f"full G185 rows={len(sample)}, grids={sample['grid_id'].nunique()}")
    log.append(f"smoke rows={len(smoke)}, grids={smoke['grid_id'].nunique()}")

    global_grid_labels = np.array(sorted(named["grid_id"].unique()))
    global_block_labels = np.array(sorted(named["spatial_block"].unique()))
    if len(global_block_labels) != 149:
        raise AssertionError("named-zone block universe is not 149")
    global_weights = {
        "grid_rademacher": draw_wild_weights(args.reps, global_grid_labels, args.seed, "rademacher"),
        "block_rademacher": draw_wild_weights(args.reps, global_block_labels, args.seed, "rademacher"),
        "block_webb": draw_wild_weights(args.reps, global_block_labels, args.seed, "webb"),
    }

    registry: list[dict[str, object]] = []
    joint_diagnostics: dict[str, object] = {}
    for fe in fes:
        point_deltas: list[float] = []
        grid_rad_deltas: list[np.ndarray] = []
        block_rad_deltas: list[np.ndarray] = []
        block_webb_deltas: list[np.ndarray] = []
        for region, hazard in TEST_ORDER:
            region_frame = smoke.loc[smoke["maize_zone"].astype(str).eq(region)].copy()
            spec = hazard_spec(hazard)
            required = list(dict.fromkeys(["gleam_smrz_mean_raw", "ln_yield_raw", *spec.mediator_rhs, *spec.yield_rhs]))
            complete = region_frame.loc[:, required].notna().all(axis=1)
            model_frame = region_frame.loc[complete].copy()
            if model_frame["grid_id"].nunique() < 50:
                raise RuntimeError(f"smoke support below 50 grids: {region}/{hazard}")
            hac_status: dict[str, object] = {}
            fits: dict[str, tuple[object, object, pd.DataFrame, pd.DataFrame]] = {}
            for cluster in clusters:
                m_fit, m_work = fit_absorbed_model(
                    model_frame, "gleam_smrz_mean_raw", spec.mediator_rhs, fe, cluster
                )
                y_fit, y_work = fit_absorbed_model(model_frame, "ln_yield_raw", spec.yield_rhs, fe, cluster)
                if not m_work[["grid_id", "year"]].reset_index(drop=True).equals(
                    y_work[["grid_id", "year"]].reset_index(drop=True)
                ):
                    raise AssertionError("two equations do not use identical complete cases")
                fits[cluster] = (m_fit, y_fit, m_work, y_work)
                if cluster == "grid":
                    for bandwidth in HAC_BANDWIDTHS_KM:
                        _, m_hac = conley_covariance(m_fit, m_work, bandwidth)
                        _, y_hac = conley_covariance(y_fit, y_work, bandwidth)
                        hac_status[str(int(bandwidth))] = {
                            "mediator_finite": m_hac["finite"],
                            "yield_finite": y_hac["finite"],
                            "mediator_pairs": m_hac["ordered_pairs"],
                            "yield_pairs": y_hac["ordered_pairs"],
                        }
            grid_m, grid_y, _, _ = fits["grid"]
            _, _, point_total = delta_components(
                grid_m.beta, grid_y.beta, grid_m.xvars, grid_y.xvars, spec
            )
            point_deltas.append(float(point_total[0]))
            grid_m_draw = score_bootstrap_betas(
                grid_m, global_grid_labels, global_weights["grid_rademacher"]
            )
            grid_y_draw = score_bootstrap_betas(
                grid_y, global_grid_labels, global_weights["grid_rademacher"]
            )
            _, _, grid_total_draw = delta_components(
                grid_m_draw, grid_y_draw, grid_m.xvars, grid_y.xvars, spec
            )
            if len(grid_total_draw) != args.reps or not np.isfinite(grid_total_draw).all():
                raise RuntimeError("invalid grid Rademacher nonlinear draw vector")
            grid_rad_deltas.append(grid_total_draw)
            # Algebra identity smoke assertion at the region-specific median SR.
            sr_value = float(model_frame["ca_raw"].median())
            ie, de, te = algebraic_components(
                grid_m.beta, grid_y.beta, grid_m.xvars, grid_y.xvars, spec, sr_value
            )
            if float(np.max(np.abs(te - (ie + de)))) >= 1e-10:
                raise AssertionError("TE != IE + DE")

            block_m, block_y, _, _ = fits["spatial_block"]
            for label, weights, target in (
                ("rademacher", global_weights["block_rademacher"], block_rad_deltas),
                ("webb", global_weights["block_webb"], block_webb_deltas),
            ):
                m_draw = score_bootstrap_betas(block_m, global_block_labels, weights)
                y_draw = score_bootstrap_betas(block_y, global_block_labels, weights)
                _, _, total_draw = delta_components(m_draw, y_draw, block_m.xvars, block_y.xvars, spec)
                if len(total_draw) != args.reps or not np.isfinite(total_draw).all():
                    raise RuntimeError(f"invalid {label} nonlinear draw vector")
                target.append(total_draw)
            registry.append(
                {
                    "fe": fe,
                    "region": region,
                    "hazard": hazard,
                    "N": int(grid_m.nobs),
                    "grids": int(model_frame["grid_id"].nunique()),
                    "spatial_blocks": int(model_frame["spatial_block"].nunique()),
                    "mediator_K": grid_m.k,
                    "yield_K": grid_y.k,
                    "mediator_rank": grid_m.rank,
                    "yield_rank": grid_y.rank,
                    "singleton_grids": grid_m.singleton_grids,
                    "zero_norm_rows_m": grid_m.zero_norm_rows,
                    "zero_norm_rows_y": grid_y.zero_norm_rows,
                    "max_abs_group_mean_m": grid_m.max_abs_group_mean,
                    "max_abs_group_mean_y": grid_y.max_abs_group_mean,
                    "hac_status": json.dumps(hac_status, ensure_ascii=False, sort_keys=True),
                    "not_for_inference": True,
                }
            )
        point = np.asarray(point_deltas)
        grid_rad = np.column_stack(grid_rad_deltas)
        rad = np.column_stack(block_rad_deltas)
        webb = np.column_stack(block_webb_deltas)
        if (
            point.shape != (15,)
            or grid_rad.shape != (args.reps, 15)
            or rad.shape != (args.reps, 15)
            or webb.shape != (args.reps, 15)
        ):
            raise AssertionError("15-dimensional synchronized interface is incomplete")
        rw_grid = romano_wolf_stepdown(point, grid_rad, TEST_ORDER)
        rw_rad = romano_wolf_stepdown(point, rad, TEST_ORDER)
        rw_webb = romano_wolf_stepdown(point, webb, TEST_ORDER)
        omni_grid = omnibus_region_tests(point, grid_rad)
        omni_rad = omnibus_region_tests(point, rad)
        omni_webb = omnibus_region_tests(point, webb)
        joint_diagnostics[fe] = {
            "dimension": 15,
            "grid_rademacher_shape": list(grid_rad.shape),
            "rademacher_shape": list(rad.shape),
            "webb_shape": list(webb.shape),
            "grid_rademacher_covariance_rank": int(
                np.linalg.matrix_rank(np.cov(grid_rad, rowvar=False, ddof=1))
            ),
            "rademacher_covariance_rank": int(np.linalg.matrix_rank(np.cov(rad, rowvar=False, ddof=1))),
            "webb_covariance_rank": int(np.linalg.matrix_rank(np.cov(webb, rowvar=False, ddof=1))),
            "romano_wolf_grid_rademacher_complete": bool(
                len(rw_grid) == 15 and np.isfinite(rw_grid).all()
            ),
            "romano_wolf_grid_rademacher_count": int(len(rw_grid)),
            "romano_wolf_grid_rademacher_finite_count": int(np.isfinite(rw_grid).sum()),
            "romano_wolf_rademacher_complete": bool(len(rw_rad) == 15 and np.isfinite(rw_rad).all()),
            "romano_wolf_rademacher_count": int(len(rw_rad)),
            "romano_wolf_rademacher_finite_count": int(np.isfinite(rw_rad).sum()),
            "romano_wolf_webb_complete": bool(len(rw_webb) == 15 and np.isfinite(rw_webb).all()),
            "romano_wolf_webb_count": int(len(rw_webb)),
            "romano_wolf_webb_finite_count": int(np.isfinite(rw_webb).sum()),
            "omnibus_grid_rademacher": omni_grid,
            "omnibus_rademacher": omni_rad,
            "omnibus_webb": omni_webb,
            "not_for_inference": True,
        }

    registry_frame = pd.DataFrame(registry)
    expected_registry = len(fes) * len(TEST_ORDER)
    if len(registry_frame) != expected_registry:
        raise AssertionError(f"model registry incomplete: {len(registry_frame)} != {expected_registry}")
    completion_contract = {
        "fixed_effects": list(fes),
        "methods": list(FROZEN_METHODS),
        "bootstrap_reps": args.reps,
        "test_dimension": 15,
    }
    completion_validation = validate_completion_contract(completion_contract, joint_diagnostics)
    hac_summary = summarize_hac_status(registry_frame)
    if completion_validation["pair_count"] != 6 or hac_summary["expected_items"] != 180:
        raise AssertionError("run-level completion cardinality does not match frozen smoke contract")

    created_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    commit = git_commit(worktree_root)
    schema_path = worktree_root / "docs" / "contracts" / "run_manifest.schema.json"
    predicate_text = (
        "ggcp10_maize_frac>=0.05; main_sample==1; 0.5<=yield_tons_ha<18; "
        "exclude both members of consecutive-year abs(d_ln_yield)>1 pair; "
        "gleam_smrz_sd>=0.001"
    )
    run_manifest = {
        "contract_version": "run-manifest-v1",
        "canonical_id": "g185-old-method-unified-v1",
        "run_id": output_dir.name,
        "created_utc": created_utc,
        "status": "SMOKE",
        "not_for_inference": True,
        "design_version": "g185-old-method-unified-design-v2+dual-sample-key-amendment",
        "git_commit": commit,
        "data_family": "GGCP10-G185",
        "inputs": [
            {
                "role": "GGCP10 G185 base panel",
                "path": str(args.base_dta.resolve()),
                "bytes": int(args.base_dta.stat().st_size),
                "md5": None,
                "sha256": base_hash,
            },
            {
                "role": "V3 precipitation hot-dry sidecar",
                "path": str(args.hotdry_dta.resolve()),
                "bytes": int(args.hotdry_dta.stat().st_size),
                "md5": None,
                "sha256": hotdry_hash,
            },
        ],
        "sample_predicate": predicate_text,
        "sample_key_serialization": CANONICAL_SERIALIZER_VERSION,
        "sample_key_sha256": sample_hash,
        "sample_counts": {
            "full_rows": int(len(sample)),
            "full_grids": int(sample["grid_id"].nunique()),
            "named_rows": int(len(named)),
            "named_grids": int(named["grid_id"].nunique()),
            "smoke_rows": int(len(smoke)),
            "smoke_grids": int(smoke["grid_id"].nunique()),
        },
        "outcome": "ln_yield_raw",
        "exposure_definition": (
            "D_full_raw; hdd_ge32_raw; HotDryPr_full_raw, each with ca_raw interaction"
        ),
        "soil_moisture_roles": [
            "gleam_smrz_mean_raw as contemporaneous complete-season algebraic channel"
        ],
        "fixed_effects": list(fes),
        "inference": {
            "primary": ",".join(FROZEN_METHODS) + "; computational smoke only",
            "bootstrap_reps": int(args.reps),
            "spatial_block_degrees": 2.0,
            "spatial_hac_km": [int(value) for value in HAC_BANDWIDTHS_KM],
            "multiplicity": "Romano-Wolf 15-test family; Holm check; smoke only",
        },
        "ca_quantiles": None,
        "exposure_endpoints": None,
        "seed": 42,
        "claims": [],
        "stop_rules_triggered": [],
        "verification": [
            {"check": "frozen input SHA-256", "status": "PASS", "detail": "two inputs"},
            {
                "check": "dual sample-key hashes",
                "status": "PASS",
                "detail": f"{LEGACY_SERIALIZER_VERSION} and {CANONICAL_SERIALIZER_VERSION}",
            },
            {
                "check": "FE-by-method completion validator",
                "status": "PASS",
                "detail": f"{completion_validation['pair_count']} of 6 pairs",
            },
            {
                "check": "Conley HAC finite status",
                "status": "PASS",
                "detail": f"{hac_summary['finite_items']} of {hac_summary['expected_items']} items",
            },
            {
                "check": "Draft 2020-12 run manifest schema",
                "status": "PASS",
                "detail": "validated in memory before any PASS artifact was written",
            },
        ],
    }
    schema_validation = validate_contract_manifest(run_manifest, schema_path)

    assertions = {
        "status": "SMOKE_PASS_NOT_FOR_INFERENCE",
        "not_for_inference": True,
        "input_hashes_match": True,
        "legacy_sample_key_hash_match": True,
        "canonical_sample_key_hash_match": True,
        "sample_checks": sample_checks,
        "waterfall": waterfall,
        "drought_wet_definition": dw,
        "smoke_rows": int(len(smoke)),
        "smoke_grids": int(smoke["grid_id"].nunique()),
        "smoke_zone_rows": {region: int(smoke["maize_zone"].astype(str).eq(region).sum()) for region in REGIONS},
        "smoke_zone_grids": {
            region: int(smoke.loc[smoke["maize_zone"].astype(str).eq(region), "grid_id"].nunique())
            for region in REGIONS
        },
        "model_registry_rows": int(len(registry_frame)),
        "completion_validation": completion_validation,
        "hac_summary": hac_summary,
        "all_hac_finite": bool(hac_summary["all_finite"]),
        "run_manifest_schema_validated": True,
    }
    readme = f"""# G185 old-method smoke test

**NOT_FOR_INFERENCE**

本运行只验证冻结样本谓词、1:1 合并、两类固定效应吸收、grid/2°空间块线性化 score bootstrap、Webb 权重、IE/DE/TE 代数、100/200/300 km Conley 公式及15维同步接口是否可计算。运行使用 `{args.reps}` 次抽样和每区 `{args.grids_per_region}` 个按 grid_id 等距选取的固定小样本，不生成可用于正文、显著性判断或投稿主张的实证结果。

- 完整 G185：{len(sample):,} 行，{sample['grid_id'].nunique():,} grids。
- 五个命名区：{len(named):,} 行，{named['grid_id'].nunique():,} grids。
- smoke 子样本：{len(smoke):,} 行，{smoke['grid_id'].nunique():,} grids。
- 模型接口：{len(registry_frame)} 个区域—胁迫—FE 单元；每个单元包含两条方程。
- 运行级完成验证：{completion_validation['pair_count']} 个FE×权重方法组合；HAC有限状态 {hac_summary['finite_items']}/{hac_summary['expected_items']}。
- 数据契约：`run_manifest.json` 已通过 JSON Schema Draft 2020-12 验证。
- 推断限制：本目录中任何数值均不得作为估计结果、置信区间或显著性证据引用。
"""

    # No artifact containing PASS is written before both validators above have
    # returned successfully.
    registry_frame.to_csv(output_dir / "smoke_model_registry.csv", index=False, encoding="utf-8")
    (output_dir / "smoke_assertions.json").write_text(
        json.dumps(assertions, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "smoke_joint_diagnostics.json").write_text(
        json.dumps(joint_diagnostics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "smoke_log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    (output_dir / "SMOKE_README.md").write_text(readme, encoding="utf-8")
    (output_dir / "run_manifest.json").write_text(
        json.dumps(run_manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    script_paths = [Path(__file__).resolve(), Path(__file__).with_name("g185_old_method_core.py").resolve()]
    manifest = {
        "canonical_id": "g185-old-method-unified-v1",
        "run_id": output_dir.name,
        "stage": "smoke",
        "status": "SMOKE_PASS_NOT_FOR_INFERENCE",
        "not_for_inference": True,
        "public_claim": "none; computational smoke only",
        "project_root_read_only": str(project_root),
        "worktree_root": str(worktree_root),
        "output_dir": str(output_dir),
        "git_commit": commit,
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "r": "not invoked",
            "stata": "not invoked",
        },
        "input_hashes": {str(args.base_dta.resolve()): base_hash, str(args.hotdry_dta.resolve()): hotdry_hash},
        "imported_scripts": {str(path): sha256_file(path) for path in script_paths},
        "sample_predicate": [
            "ggcp10_maize_frac>=0.05",
            "main_sample==1",
            "0.5<=yield_tons_ha<18",
            "exclude both members of consecutive-year abs(d_ln_yield)>1 pair",
            "gleam_smrz_sd>=0.001",
        ],
        "sample_keys": {
            "legacy": {"algorithm": LEGACY_SERIALIZER_VERSION, "sha256": legacy_sample_hash},
            "canonical_secondary": {
                "algorithm": CANONICAL_SERIALIZER_VERSION,
                "sha256": sample_hash,
            },
        },
        "fe": list(fes),
        "score_cluster": list(clusters),
        "weights": ["grid Rademacher", "2-degree Rademacher", "2-degree Webb"],
        "completion_contract": completion_contract,
        "completion_validation": completion_validation,
        "block_definition": {
            "degrees": 2,
            "longitude": "floor((longitude+180)/2)",
            "latitude": "floor((latitude+90)/2)",
            "global_origin": [-180, -90],
            "named_universe_blocks": len(global_block_labels),
        },
        "bootstrap": {"reps": args.reps, "seed": args.seed, "ddof": 1, "monte_carlo_correction": "(1+#)/(B+1)"},
        "hac": {
            "bandwidths_km": list(HAC_BANDWIDTHS_KM),
            "kernel": "max(1-d/L,0)",
            "ordered_pairs_and_diagonal": True,
            "distance": "haversine grid-center",
            "completion_summary": hac_summary,
        },
        "run_manifest_contract": {
            "file": "run_manifest.json",
            "validated": True,
            **schema_validation,
        },
        "test_order": [f"{region}:{hazard}" for region, hazard in TEST_ORDER],
        "quantiles": "not estimated for publication in smoke",
        "smoke_sample": {
            "selection": "equally spaced indices over sorted grid_id within each named zone",
            "grids_per_region": args.grids_per_region,
            "rows": len(smoke),
            "grids": int(smoke["grid_id"].nunique()),
        },
        "output_hashes": output_hashes(output_dir),
    }
    (output_dir / "smoke_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"status": manifest["status"], "output_dir": str(output_dir), "assertions": assertions}, ensure_ascii=False))


def main() -> None:
    args = parser().parse_args()
    validate_cli_contract(args)
    # Keep directory creation outside the failure-recording scope. If the
    # target already exists or a path guard fails, no byte may be written to
    # that target.
    worktree_root = args.worktree_root.resolve(strict=True)
    output_dir = ensure_new_output_dir(worktree_root, args.output_dir)
    try:
        run(args, output_dir)
    except Exception as exc:
        # Reaching this block proves the directory was newly created by this
        # invocation. Preserve only this new run's failure record.
        failure_path = output_dir / "SMOKE_FAILED.json"
        if not failure_path.exists():
            failure_path.write_text(
                json.dumps(
                    {
                        "status": "SMOKE_STOPPED",
                        "not_for_inference": True,
                        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                        "exception_type": type(exc).__name__,
                        "message": str(exc),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
        raise


if __name__ == "__main__":
    main()
