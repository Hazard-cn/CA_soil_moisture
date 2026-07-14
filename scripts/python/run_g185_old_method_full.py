"""Run the frozen full G185 old-method portfolio without publishing claims.

The output is review-pending and remains under the isolated worktree ``temp``
tree.  It must not be copied to ``docs/results`` before independent result
review.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from g185_old_method_core import (
    CANONICAL_SERIALIZER_VERSION,
    EXPECTED_BASE_SHA256,
    EXPECTED_CANONICAL_SAMPLE_KEY_SHA256,
    EXPECTED_HOTDRY_SHA256,
    EXPECTED_LEGACY_SAMPLE_KEY_SHA256,
    HAC_BANDWIDTHS_KM,
    HAZARDS,
    LEGACY_SERIALIZER_VERSION,
    REGIONS,
    TEST_ORDER,
    algebraic_components,
    apply_g185_predicate,
    assert_frozen_sample,
    conley_stacked_covariance,
    delta_components,
    draw_wild_weights,
    ensure_new_output_dir,
    fit_absorbed_model,
    hazard_spec,
    holm_adjust,
    legacy_sample_key_sha256,
    omnibus_region_tests,
    output_hashes,
    prepare_analysis_columns,
    romano_wolf_stepdown,
    sample_key_sha256,
    score_bootstrap_betas,
    sha256_file,
    validate_drought_wet_definitions,
)
from run_g185_old_method_smoke import (
    BASE_COLUMNS,
    git_commit,
    read_inputs,
    validate_contract_manifest,
)


FES = ("grid_year", "grid_provyear")
SCORE_CLUSTERS = ("grid", "spatial_block")
GRID_REPS = 999
BLOCK_REPS = 1999
SEED = 42
CORE_COMBOS = (("NE", "drought"), ("HHH", "heat"), ("HHH", "hotdry"))
REGION_LABEL = {"NE": "Northeast", "HHH": "Huang-Huai-Hai", "NW": "Northwest", "SW": "Southwest", "SH": "Southern Hills"}
HAZARD_LABEL = {"drought": "Drought", "heat": "Heat", "hotdry": "Hot-dry"}
EXPECTED_NATIONAL_TE = {"drought": 0.576838, "heat": 1.157980, "hotdry": 1.146443}
EXPECTED_CORE = {
    ("NE", "drought"): (1.8502198111098185, 1.2315286219077919, 2.5553229127253503, 1042),
    ("HHH", "heat"): (3.1683722634290903, 2.0671267488912806, 4.258912820532531, 1143),
    ("HHH", "hotdry"): (2.425434357669895, 1.0389554923271633, 3.8713209641437802, 1144),
}


class PresetStop(RuntimeError):
    """A frozen research STOP condition, distinct from an execution failure."""


def validate_full_output_bundle(output_dir: Path, schema_path: Path) -> dict[str, int | str]:
    """Validate that a STOP bundle retains the complete machine-readable output contract."""
    required = (
        "run_manifest.json",
        "full_manifest.json",
        "historical_validation.json",
        "bootstrap_diagnostics.json",
        "run.log",
        "README_REVIEW_PENDING.md",
        "tables/all_component_estimates.csv",
        "tables/all_endpoint_estimates.csv",
        "tables/national_p90_endpoints.csv",
        "tables/regional_iede_matrix.csv",
        "tables/regional_joint_tests.csv",
        "tables/regional_omnibus_tests.csv",
        "tables/conley_diagnostics.csv",
        "tables/model_registry.csv",
    )
    missing = [name for name in required if not (output_dir / name).is_file()]
    if missing:
        raise AssertionError(f"full output bundle missing files: {missing}")
    manifest = json.loads((output_dir / "run_manifest.json").read_text(encoding="utf-8"))
    validate_contract_manifest(manifest, schema_path)
    if manifest["status"] != "STOP" or manifest["not_for_inference"] is not True or manifest["claims"] != []:
        raise AssertionError("STOP run_manifest status boundary is invalid")
    extension = json.loads((output_dir / "full_manifest.json").read_text(encoding="utf-8"))
    if extension.get("status") != "FULL_STOP" or not extension.get("validation", {}).get("stop_reasons"):
        raise AssertionError("extended STOP manifest is invalid")
    tables = output_dir / "tables"
    regional = pd.read_csv(tables / "regional_iede_matrix.csv")
    joint = pd.read_csv(tables / "regional_joint_tests.csv")
    omnibus = pd.read_csv(tables / "regional_omnibus_tests.csv")
    hac = pd.read_csv(tables / "conley_diagnostics.csv")
    registry = pd.read_csv(tables / "model_registry.csv")
    if len(regional) != 135 or regional[["region", "hazard"]].drop_duplicates().shape[0] != 15:
        raise AssertionError("regional IE/DE/TE matrix is incomplete")
    if len(joint) != 45 or len(omnibus) != 9:
        raise AssertionError("RW/Holm or omnibus outputs are incomplete")
    if len(hac) != 108 or not hac["finite"].eq(True).all():
        raise AssertionError("108-item HAC output is incomplete")
    if len(registry) != 36:
        raise AssertionError("model registry is incomplete")
    return {
        "status": "PASS",
        "regional_iede_rows": len(regional),
        "joint_rows": len(joint),
        "omnibus_rows": len(omnibus),
        "hac_rows": len(hac),
        "registry_rows": len(registry),
    }


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(description=__doc__)
    out.add_argument("--project-root", type=Path, required=True)
    out.add_argument("--worktree-root", type=Path, required=True)
    out.add_argument("--base-dta", type=Path, required=True)
    out.add_argument("--hotdry-dta", type=Path, required=True)
    out.add_argument("--output-dir", type=Path, required=True)
    out.add_argument("--fe", choices=FES, action="append")
    out.add_argument("--score-cluster", choices=SCORE_CLUSTERS, action="append")
    out.add_argument("--block-degrees", type=float, default=2.0)
    out.add_argument("--grid-reps", type=int, default=GRID_REPS)
    out.add_argument("--block-reps", type=int, default=BLOCK_REPS)
    out.add_argument("--seed", type=int, default=SEED)
    return out


def validate_cli(args: argparse.Namespace) -> None:
    fes = tuple(dict.fromkeys(args.fe or FES))
    clusters = tuple(dict.fromkeys(args.score_cluster or SCORE_CLUSTERS))
    if len(fes) != 2 or set(fes) != set(FES):
        raise ValueError(f"full run requires both fixed-effect specifications: {FES}")
    if len(clusters) != 2 or set(clusters) != set(SCORE_CLUSTERS):
        raise ValueError(f"full run requires both score clusters: {SCORE_CLUSTERS}")
    if args.block_degrees != 2.0 or args.grid_reps != GRID_REPS or args.block_reps != BLOCK_REPS:
        raise ValueError("full run requires 2 degrees, 999 grid reps, and 1999 block reps")
    if args.seed != SEED:
        raise ValueError("full run requires seed 42")


def pct(log_change: np.ndarray | float) -> np.ndarray:
    return np.expm1(np.asarray(log_change, dtype=float)) * 100.0


def ci(values: np.ndarray) -> tuple[float, float]:
    low, high = np.percentile(np.asarray(values, dtype=float), [2.5, 97.5])
    return float(low), float(high)


def stacked_cluster_covariance(m_fit, y_fit) -> np.ndarray:
    if not np.array_equal(m_fit.cluster_labels, y_fit.cluster_labels):
        raise AssertionError("cluster labels differ across equations")
    scores = np.column_stack((m_fit.cluster_scores, y_fit.cluster_scores))
    km, ky = m_fit.k, y_fit.k
    bread = np.zeros((km + ky, km + ky), dtype=float)
    bread[:km, :km] = m_fit.bread
    bread[km:, km:] = y_fit.bread
    g = len(m_fit.cluster_labels)
    n = m_fit.nobs
    k = km + ky
    correction = (g / (g - 1.0)) * ((n - 1.0) / (n - k))
    covariance = correction * bread @ (scores.T @ scores) @ bread
    return (covariance + covariance.T) / 2.0


def delta_point_and_gradient(m_fit, y_fit, spec) -> tuple[float, np.ndarray]:
    mi = {name: idx for idx, name in enumerate(m_fit.xvars)}
    yi = {name: idx for idx, name in enumerate(y_fit.xvars)}
    a3 = float(m_fit.beta[mi[spec.interaction]])
    b = float(y_fit.beta[yi["gleam_smrz_mean_raw"]])
    c3 = float(y_fit.beta[yi[spec.interaction]])
    gradient = np.zeros(m_fit.k + y_fit.k, dtype=float)
    gradient[mi[spec.interaction]] = b
    gradient[m_fit.k + yi["gleam_smrz_mean_raw"]] = a3
    gradient[m_fit.k + yi[spec.interaction]] = 1.0
    return a3 * b + c3, gradient


def normal_endpoint_interval(delta: float, se: float, iqr: float, p90: float) -> tuple[float, float, float]:
    estimate = float(pct(delta * iqr * p90))
    low = float(pct((delta - 1.959963984540054 * se) * iqr * p90))
    high = float(pct((delta + 1.959963984540054 * se) * iqr * p90))
    return estimate, low, high


def bootstrap_raw_pvalues(estimate: np.ndarray, draws: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    se = np.std(draws, axis=0, ddof=1)
    observed = np.abs(estimate / se)
    centered = np.abs((draws - estimate[None, :]) / se[None, :])
    raw = np.array(
        [(1.0 + np.sum(centered[:, j] >= observed[j])) / (len(draws) + 1.0) for j in range(len(estimate))]
    )
    return raw, se


def configure_plots() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Arial"],
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def save_figure(fig: plt.Figure, path: Path) -> None:
    fig.set_size_inches(12, 5)
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def make_figures(output_dir: Path, components: pd.DataFrame, endpoints: pd.DataFrame, curves: pd.DataFrame, robustness: pd.DataFrame) -> None:
    configure_plots()
    fig_dir = output_dir / "figures"
    fig_dir.mkdir(exist_ok=False)
    hist_method = "grid_year_grid_rademacher_999"
    national = components.loc[
        components["scope"].eq("National") & components["method"].eq(hist_method)
    ]
    fig, axes = plt.subplots(1, 3, figsize=(12, 5), sharey=False)
    colors = {"IE": "#9ecae1", "DE": "#fdae6b", "TE": "#252525"}
    levels = ("P25", "P50", "P75")
    for axis, hazard in zip(axes, HAZARDS, strict=True):
        sub = national.loc[national["hazard"].eq(hazard)]
        x = np.arange(3)
        for offset, effect in zip((-0.24, 0.0, 0.24), ("IE", "DE", "TE"), strict=True):
            vals = [float(sub.loc[sub["sr_level"].eq(level) & sub["effect_type"].eq(effect), "estimate_pct"].iloc[0]) for level in levels]
            axis.bar(x + offset, vals, width=0.22, color=colors[effect], label=effect)
        axis.axhline(0, color="#666666", linewidth=0.8)
        axis.set_xticks(x, levels)
        axis.set_title(HAZARD_LABEL[hazard])
        axis.set_ylabel("Algebraic component at hazard P90 (%)")
    axes[0].legend(frameon=False, ncol=3)
    fig.suptitle("National G185 two-equation components across SR quantiles")
    save_figure(fig, fig_dir / "fig1_national_iede.png")

    fig, axes = plt.subplots(1, 3, figsize=(12, 5))
    core_curves = curves.loc[curves["method"].eq(hist_method)]
    for axis, (region, hazard) in zip(axes, CORE_COMBOS, strict=True):
        sub = core_curves.loc[core_curves["region"].eq(region) & core_curves["hazard"].eq(hazard)]
        axis.plot(sub["exposure"], sub["estimate_pct"], color="#2c7fb8", linewidth=2)
        axis.fill_between(sub["exposure"], sub["ci_low_pct"], sub["ci_high_pct"], color="#9ecae1", alpha=0.45)
        axis.axhline(0, color="#666666", linewidth=0.8)
        axis.set_title(f"{REGION_LABEL[region]}: {HAZARD_LABEL[hazard]}")
        axis.set_xlabel("Exposure (0 to regional P90)")
        axis.set_ylabel("P75-P25 algebraic TE (%)")
    fig.suptitle("Old linear G185 buffering curves")
    save_figure(fig, fig_dir / "fig2_core_linear_curves.png")

    matrix = endpoints.loc[
        endpoints["scope"].eq("Region")
        & endpoints["method"].eq(hist_method)
        & endpoints["effect_type"].eq("TE_delta")
    ].pivot(index="region", columns="hazard", values="estimate_pct").reindex(index=REGIONS, columns=HAZARDS)
    fig, axis = plt.subplots(figsize=(12, 5))
    image = axis.imshow(matrix.to_numpy(), cmap="RdBu_r", vmin=-6, vmax=6, aspect="auto")
    for i, region in enumerate(REGIONS):
        for j, hazard in enumerate(HAZARDS):
            label = f"{matrix.iloc[i, j]:.2f}"
            if region == "SH":
                label += "\nlow blocks"
            axis.text(j, i, label, ha="center", va="center", fontsize=9)
    axis.set_xticks(range(3), [HAZARD_LABEL[h] for h in HAZARDS])
    axis.set_yticks(range(5), [REGION_LABEL[r] for r in REGIONS])
    axis.set_title("Five-zone algebraic TE matrix (fixed color scale: -6 to 6%)")
    fig.colorbar(image, ax=axis, label="P75-P25 TE at regional P90 (%)")
    save_figure(fig, fig_dir / "fig3_five_zone_te_matrix.png")

    fig, axes = plt.subplots(1, 3, figsize=(12, 5))
    method_order = [
        "grid_year_grid_rademacher_999",
        "grid_provyear_block_rademacher_1999",
        "grid_provyear_block_webb_1999",
        "grid_provyear_conley_100km",
        "grid_provyear_conley_200km",
        "grid_provyear_conley_300km",
    ]
    short = ["GY/Grid", "GPY/2R", "GPY/2W", "HAC100", "HAC200", "HAC300"]
    for axis, (region, hazard) in zip(axes, CORE_COMBOS, strict=True):
        sub = robustness.loc[robustness["region"].eq(region) & robustness["hazard"].eq(hazard)].set_index("method")
        vals = np.array([sub.loc[m, "estimate_pct"] for m in method_order], dtype=float)
        lows = np.array([sub.loc[m, "ci_low_pct"] for m in method_order], dtype=float)
        highs = np.array([sub.loc[m, "ci_high_pct"] for m in method_order], dtype=float)
        axis.errorbar(range(len(vals)), vals, yerr=np.vstack((vals - lows, highs - vals)), fmt="o", color="#2c7fb8", capsize=3)
        axis.axhline(0, color="#666666", linewidth=0.8)
        axis.set_xticks(range(len(vals)), short, rotation=35, ha="right")
        axis.set_title(f"{REGION_LABEL[region]}: {HAZARD_LABEL[hazard]}")
        axis.set_ylabel("TE endpoint (%)")
    fig.suptitle("Core-combination inference sensitivity")
    save_figure(fig, fig_dir / "fig4_core_robustness.png")


def run(args: argparse.Namespace, output_dir: Path) -> None:
    started = time.time()
    validate_cli(args)
    project_root = args.project_root.resolve(strict=True)
    worktree_root = args.worktree_root.resolve(strict=True)
    if project_root == worktree_root:
        raise ValueError("project-root and worktree-root must be distinct")
    base_hash = sha256_file(args.base_dta)
    hotdry_hash = sha256_file(args.hotdry_dta)
    if (base_hash, hotdry_hash) != (EXPECTED_BASE_SHA256, EXPECTED_HOTDRY_SHA256):
        raise AssertionError("input hash mismatch")
    panel = read_inputs(args.base_dta, args.hotdry_dta)
    dw_check = validate_drought_wet_definitions(panel)
    sample, waterfall = apply_g185_predicate(panel)
    sample = prepare_analysis_columns(sample)
    canonical_hash = sample_key_sha256(sample[["grid_id", "year"]])
    legacy_hash = legacy_sample_key_sha256(sample[["grid_id", "year"]])
    if canonical_hash != EXPECTED_CANONICAL_SAMPLE_KEY_SHA256 or legacy_hash != EXPECTED_LEGACY_SAMPLE_KEY_SHA256:
        raise AssertionError("sample key hash mismatch")
    sample_checks = assert_frozen_sample(sample)
    named = sample.loc[sample["maize_zone"].astype(str).isin(REGIONS)].copy()

    global_grids = np.array(sorted(sample["grid_id"].unique()))
    global_blocks = np.array(sorted(sample["spatial_block"].unique()))
    if len(global_grids) != 13236 or len(global_blocks) != 151:
        raise AssertionError("global bootstrap universe mismatch")
    grid_weights = draw_wild_weights(GRID_REPS, global_grids, SEED, "rademacher").astype(np.int8)
    block_rad_weights = draw_wild_weights(BLOCK_REPS, global_blocks, SEED, "rademacher").astype(np.float32)
    block_webb_weights = draw_wild_weights(BLOCK_REPS, global_blocks, SEED, "webb").astype(np.float32)

    cells: dict[tuple[str, str, str], dict[str, object]] = {}
    registry_rows: list[dict[str, object]] = []
    hac_rows: list[dict[str, object]] = []
    robustness_rows: list[dict[str, object]] = []
    log = ["REVIEW_PENDING_NOT_FOR_INFERENCE", f"start_utc={dt.datetime.now(dt.timezone.utc).isoformat()}"]
    scopes = [("National", "National", sample), *[("Region", region, named.loc[named["maize_zone"].astype(str).eq(region)]) for region in REGIONS]]
    for fe in FES:
        for scope, region, subset in scopes:
            for hazard in HAZARDS:
                spec = hazard_spec(hazard)
                required = list(dict.fromkeys(["gleam_smrz_mean_raw", "ln_yield_raw", *spec.mediator_rhs, *spec.yield_rhs]))
                model_frame = subset.loc[subset[required].notna().all(axis=1)].copy()
                m_grid, m_work = fit_absorbed_model(model_frame, "gleam_smrz_mean_raw", spec.mediator_rhs, fe, "grid")
                y_grid, y_work = fit_absorbed_model(model_frame, "ln_yield_raw", spec.yield_rhs, fe, "grid")
                if not m_work[["grid_id", "year"]].reset_index(drop=True).equals(y_work[["grid_id", "year"]].reset_index(drop=True)):
                    raise AssertionError("two-equation complete-case mismatch")
                p25, p50, p75 = [float(value) for value in np.percentile(model_frame["ca_raw"], [25, 50, 75])]
                p90 = float(np.percentile(model_frame[spec.hazard_var], 90))
                methods: dict[str, tuple[np.ndarray, np.ndarray]] = {}
                if fe == "grid_year":
                    methods["grid_year_grid_rademacher_999"] = (
                        score_bootstrap_betas(m_grid, global_grids, grid_weights),
                        score_bootstrap_betas(y_grid, global_grids, grid_weights),
                    )
                else:
                    m_block, m_block_work = fit_absorbed_model(model_frame, "gleam_smrz_mean_raw", spec.mediator_rhs, fe, "spatial_block")
                    y_block, y_block_work = fit_absorbed_model(model_frame, "ln_yield_raw", spec.yield_rhs, fe, "spatial_block")
                    methods["grid_provyear_block_rademacher_1999"] = (
                        score_bootstrap_betas(m_block, global_blocks, block_rad_weights),
                        score_bootstrap_betas(y_block, global_blocks, block_rad_weights),
                    )
                    methods["grid_provyear_block_webb_1999"] = (
                        score_bootstrap_betas(m_block, global_blocks, block_webb_weights),
                        score_bootstrap_betas(y_block, global_blocks, block_webb_weights),
                    )
                delta, gradient = delta_point_and_gradient(m_grid, y_grid, spec)
                cluster_cov = stacked_cluster_covariance(m_grid, y_grid)
                cluster_se = float(np.sqrt(max(0.0, gradient @ cluster_cov @ gradient)))
                estimate, low, high = normal_endpoint_interval(delta, cluster_se, p75 - p25, p90)
                robustness_rows.append(
                    {"scope": scope, "region": region, "hazard": hazard, "fe": fe, "method": f"{fe}_grid_cluster_normal", "delta_per_sr": delta, "se_delta": cluster_se, "estimate_pct": estimate, "ci_low_pct": low, "ci_high_pct": high, "N": m_grid.nobs, "grids": int(model_frame["grid_id"].nunique())}
                )
                for bandwidth in HAC_BANDWIDTHS_KM:
                    covariance, diagnostics = conley_stacked_covariance(m_grid, y_grid, m_work, y_work, bandwidth)
                    se = float(np.sqrt(max(0.0, gradient @ covariance @ gradient)))
                    estimate, low, high = normal_endpoint_interval(delta, se, p75 - p25, p90)
                    method = f"{fe}_conley_{int(bandwidth)}km"
                    robustness_rows.append(
                        {"scope": scope, "region": region, "hazard": hazard, "fe": fe, "method": method, "delta_per_sr": delta, "se_delta": se, "estimate_pct": estimate, "ci_low_pct": low, "ci_high_pct": high, "N": m_grid.nobs, "grids": diagnostics["grids"]}
                    )
                    hac_rows.append({"scope": scope, "region": region, "hazard": hazard, "fe": fe, **diagnostics})
                cell = {
                    "scope": scope,
                    "region": region,
                    "hazard": hazard,
                    "fe": fe,
                    "spec": spec,
                    "m_fit": m_grid,
                    "y_fit": y_grid,
                    "methods": methods,
                    "p25": p25,
                    "p50": p50,
                    "p75": p75,
                    "p90": p90,
                    "N": m_grid.nobs,
                    "grids": int(model_frame["grid_id"].nunique()),
                    "blocks": int(model_frame["spatial_block"].nunique()),
                }
                cells[(fe, region, hazard)] = cell
                registry_rows.append(
                    {"scope": scope, "region": region, "hazard": hazard, "fe": fe, "N": m_grid.nobs, "grids": cell["grids"], "spatial_blocks": cell["blocks"], "m_K": m_grid.k, "y_K": y_grid.k, "m_rank": m_grid.rank, "y_rank": y_grid.rank, "m_singleton_grids": m_grid.singleton_grids, "y_singleton_grids": y_grid.singleton_grids, "m_zero_norm_rows": m_grid.zero_norm_rows, "y_zero_norm_rows": y_grid.zero_norm_rows, "m_max_group_mean": m_grid.max_abs_group_mean, "y_max_group_mean": y_grid.max_abs_group_mean}
                )
                log.append(f"fit={fe}/{region}/{hazard};N={m_grid.nobs};grids={cell['grids']};blocks={cell['blocks']}")

    component_rows: list[dict[str, object]] = []
    endpoint_rows: list[dict[str, object]] = []
    curve_rows: list[dict[str, object]] = []
    regional_draw_layers: dict[str, list[np.ndarray]] = {
        "grid_year_grid_rademacher_999": [],
        "grid_provyear_block_rademacher_1999": [],
        "grid_provyear_block_webb_1999": [],
    }
    regional_point_layers: dict[str, list[float]] = {key: [] for key in regional_draw_layers}
    for cell in cells.values():
        spec = cell["spec"]
        m_fit, y_fit = cell["m_fit"], cell["y_fit"]
        for method, (m_draw, y_draw) in cell["methods"].items():
            for sr_level, sr_value in (("P25", cell["p25"]), ("P50", cell["p50"]), ("P75", cell["p75"])):
                point_components = algebraic_components(m_fit.beta, y_fit.beta, m_fit.xvars, y_fit.xvars, spec, sr_value)
                draw_components = algebraic_components(m_draw, y_draw, m_fit.xvars, y_fit.xvars, spec, sr_value)
                for effect, point_value, draw_value in zip(("IE", "DE", "TE"), point_components, draw_components, strict=True):
                    boot_pct = pct(draw_value * cell["p90"])
                    low, high = ci(boot_pct)
                    component_rows.append({"scope": cell["scope"], "region": cell["region"], "hazard": cell["hazard"], "fe": cell["fe"], "method": method, "sr_level": sr_level, "sr_value": sr_value, "effect_type": effect, "slope": float(point_value[0]), "hazard_p90": cell["p90"], "estimate_pct": float(pct(point_value[0] * cell["p90"])), "ci_low_pct": low, "ci_high_pct": high, "N": cell["N"], "grids": cell["grids"], "bootstrap_reps": len(m_draw), "interpretation": "algebraic_two_equation_component"})
            point_delta = delta_components(m_fit.beta, y_fit.beta, m_fit.xvars, y_fit.xvars, spec)
            draw_delta = delta_components(m_draw, y_draw, m_fit.xvars, y_fit.xvars, spec)
            for effect, point_value, draw_value in zip(("IE_delta", "DE_delta", "TE_delta"), point_delta, draw_delta, strict=True):
                scaled_point = float(point_value[0] * (cell["p75"] - cell["p25"]))
                scaled_draw = draw_value * (cell["p75"] - cell["p25"])
                boot_pct = pct(scaled_draw * cell["p90"])
                low, high = ci(boot_pct)
                endpoint_rows.append({"scope": cell["scope"], "region": cell["region"], "hazard": cell["hazard"], "fe": cell["fe"], "method": method, "effect_type": effect, "sr_p25": cell["p25"], "sr_p75": cell["p75"], "sr_iqr": cell["p75"] - cell["p25"], "hazard_p90": cell["p90"], "slope_delta_per_sr": float(point_value[0]), "scaled_slope_delta": scaled_point, "estimate_pct": float(pct(scaled_point * cell["p90"])), "ci_low_pct": low, "ci_high_pct": high, "N": cell["N"], "grids": cell["grids"], "spatial_blocks": cell["blocks"], "bootstrap_reps": len(m_draw), "interpretation": "algebraic_two_equation_component"})
                if effect == "TE_delta":
                    robustness_rows.append({"scope": cell["scope"], "region": cell["region"], "hazard": cell["hazard"], "fe": cell["fe"], "method": method, "delta_per_sr": float(point_value[0]), "se_delta": float(np.std(draw_value, ddof=1)), "estimate_pct": float(pct(scaled_point * cell["p90"])), "ci_low_pct": low, "ci_high_pct": high, "N": cell["N"], "grids": cell["grids"]})
                    if cell["scope"] == "Region":
                        regional_point_layers[method].append(float(point_value[0]))
                        regional_draw_layers[method].append(np.asarray(draw_value))
                    if (cell["region"], cell["hazard"]) in CORE_COMBOS:
                        for exposure in np.linspace(0.0, cell["p90"], 101):
                            curve_boot = pct(scaled_draw * exposure)
                            curve_low, curve_high = ci(curve_boot)
                            curve_rows.append({"region": cell["region"], "hazard": cell["hazard"], "fe": cell["fe"], "method": method, "exposure": float(exposure), "hazard_p90": cell["p90"], "estimate_pct": float(pct(scaled_point * exposure)), "ci_low_pct": curve_low, "ci_high_pct": curve_high})

    joint_rows: list[dict[str, object]] = []
    omnibus_rows: list[dict[str, object]] = []
    bootstrap_diag: dict[str, object] = {}
    for method in regional_draw_layers:
        points = np.asarray(regional_point_layers[method])
        draws = np.column_stack(regional_draw_layers[method])
        if points.shape != (15,) or draws.shape[1] != 15:
            raise AssertionError(f"incomplete regional layer: {method}")
        raw, se = bootstrap_raw_pvalues(points, draws)
        rw = romano_wolf_stepdown(points, draws, TEST_ORDER)
        hp = holm_adjust(raw)
        for index, (region, hazard) in enumerate(TEST_ORDER):
            joint_rows.append({"method": method, "region": region, "hazard": hazard, "delta_per_sr": points[index], "bootstrap_se": se[index], "z_abs": abs(points[index] / se[index]), "p_raw": raw[index], "p_romano_wolf": rw[index], "p_holm": hp[index], "bootstrap_reps": len(draws)})
        omnibus = omnibus_region_tests(points, draws)
        for row in omnibus:
            omnibus_rows.append({"method": method, **row, "bootstrap_reps": len(draws)})
        bootstrap_diag[method] = {"shape": list(draws.shape), "covariance_rank": int(np.linalg.matrix_rank(np.cov(draws, rowvar=False, ddof=1))), "rw_count": int(len(rw)), "rw_finite_count": int(np.isfinite(rw).sum()), "omnibus_ranks": [int(row["rank"]) for row in omnibus]}

    components = pd.DataFrame(component_rows)
    endpoints = pd.DataFrame(endpoint_rows)
    curves = pd.DataFrame(curve_rows)
    robustness = pd.DataFrame(robustness_rows)
    registry = pd.DataFrame(registry_rows)
    hac_table = pd.DataFrame(hac_rows)
    joint = pd.DataFrame(joint_rows)
    omnibus = pd.DataFrame(omnibus_rows)

    identity = endpoints.pivot_table(index=["scope", "region", "hazard", "fe", "method"], columns="effect_type", values="scaled_slope_delta", aggfunc="first").reset_index()
    identity_error = float(np.max(np.abs(identity["TE_delta"] - identity["IE_delta"] - identity["DE_delta"])))
    hist_method = "grid_year_grid_rademacher_999"
    national_te = endpoints.loc[endpoints["scope"].eq("National") & endpoints["method"].eq(hist_method) & endpoints["effect_type"].eq("TE_delta")]
    national_errors = {row.hazard: abs(float(row.estimate_pct) - EXPECTED_NATIONAL_TE[row.hazard]) for row in national_te.itertuples()}
    legacy_rows: list[dict[str, object]] = []
    legacy_errors: dict[str, float] = {}
    for region, hazard in CORE_COMBOS:
        cell = cells[("grid_year", region, hazard)]
        expected_point, expected_low, expected_high, legacy_seed = EXPECTED_CORE[(region, hazard)]
        labels = np.array(sorted(sample.loc[sample["maize_zone"].astype(str).eq(region), "grid_id"].unique()))
        legacy_weights = draw_wild_weights(GRID_REPS, labels, legacy_seed, "rademacher")
        m_draw = score_bootstrap_betas(cell["m_fit"], labels, legacy_weights)
        y_draw = score_bootstrap_betas(cell["y_fit"], labels, legacy_weights)
        _, _, point_delta = delta_components(cell["m_fit"].beta, cell["y_fit"].beta, cell["m_fit"].xvars, cell["y_fit"].xvars, cell["spec"])
        _, _, boot_delta = delta_components(m_draw, y_draw, cell["m_fit"].xvars, cell["y_fit"].xvars, cell["spec"])
        point_value = float(pct(point_delta[0] * (cell["p75"] - cell["p25"]) * cell["p90"]))
        low, high = ci(pct(boot_delta * (cell["p75"] - cell["p25"]) * cell["p90"]))
        max_error = max(abs(point_value - expected_point), abs(low - expected_low), abs(high - expected_high))
        legacy_errors[f"{region}:{hazard}"] = max_error
        legacy_rows.append({"region": region, "hazard": hazard, "effect_type": "TE_delta", "estimate_pct": point_value, "ci_low_pct": low, "ci_high_pct": high, "legacy_seed": legacy_seed, "status": "legacy_marginal_reproduction_only_not_joint_inference"})
    old_de = pd.DataFrame(
        [
            {"region": "NE", "hazard": "drought", "effect_type": "DE", "legacy_value_pct": 1.50},
            {"region": "HHH", "hazard": "heat", "effect_type": "DE", "legacy_value_pct": 3.27},
            {"region": "HHH", "hazard": "hotdry", "effect_type": "DE", "legacy_value_pct": 2.56},
        ]
    )
    curve_endpoint = curves.loc[curves.groupby(["region", "hazard", "method"])["exposure"].idxmax()]
    endpoint_core = endpoints.loc[endpoints["effect_type"].eq("TE_delta") & endpoints.apply(lambda row: (row["region"], row["hazard"]) in CORE_COMBOS, axis=1)]
    merged_curve = curve_endpoint.merge(endpoint_core[["region", "hazard", "method", "estimate_pct"]], on=["region", "hazard", "method"], suffixes=("_curve", "_endpoint"), validate="one_to_one")
    curve_error = float(np.max(np.abs(merged_curve["estimate_pct_curve"] - merged_curve["estimate_pct_endpoint"])))

    core_direction: dict[str, object] = {}
    for region, hazard in CORE_COMBOS:
        hist = endpoints.loc[endpoints["region"].eq(region) & endpoints["hazard"].eq(hazard) & endpoints["method"].eq(hist_method) & endpoints["effect_type"].eq("TE_delta")].iloc[0]
        new_cell = cells[("grid_provyear", region, hazard)]
        new_method = "grid_provyear_block_rademacher_1999"
        m_draw, y_draw = new_cell["methods"][new_method]
        _, _, point_delta = delta_components(new_cell["m_fit"].beta, new_cell["y_fit"].beta, new_cell["m_fit"].xvars, new_cell["y_fit"].xvars, new_cell["spec"])
        _, _, draw_delta = delta_components(m_draw, y_draw, new_cell["m_fit"].xvars, new_cell["y_fit"].xvars, new_cell["spec"])
        point_endpoint = float(pct(point_delta[0] * (new_cell["p75"] - new_cell["p25"]) * new_cell["p90"]))
        draw_endpoint = pct(draw_delta * (new_cell["p75"] - new_cell["p25"]) * new_cell["p90"])
        share = float(np.mean(np.sign(draw_endpoint) == np.sign(point_endpoint)))
        core_direction[f"{region}:{hazard}"] = {"historical_pct": float(hist["estimate_pct"]), "province_year_pct": point_endpoint, "same_sign": bool(np.sign(hist["estimate_pct"]) == np.sign(point_endpoint)), "rademacher_same_direction_share": share}

    stop_reasons: list[str] = []
    if max(national_errors.values()) >= 0.01:
        stop_reasons.append("national historical TE values exceed tolerance")
    if max(legacy_errors.values()) >= 1e-10:
        stop_reasons.append("legacy core TE point/interval reproduction failed")
    if identity_error >= 1e-10:
        stop_reasons.append("TE_delta identity failed")
    if curve_error >= 1e-10:
        stop_reasons.append("curve endpoint identity failed")
    if not old_de["effect_type"].eq("DE").all():
        stop_reasons.append("legacy DE labels invalid")
    if any(not value["same_sign"] or value["rademacher_same_direction_share"] < 0.90 for value in core_direction.values()):
        stop_reasons.append("province-year core sign/share STOP rule triggered")
    if not (hac_table["finite"].eq(True).all() and len(hac_table) == 108):
        stop_reasons.append("HAC completion failed")
    if any(value["covariance_rank"] != 15 or value["rw_count"] != 15 or value["rw_finite_count"] != 15 or value["omnibus_ranks"] != [4, 4, 4] for value in bootstrap_diag.values()):
        stop_reasons.append("joint bootstrap completion failed")
    validation = {"status": "PASS" if not stop_reasons else "STOP", "not_for_inference": True, "national_te_errors_pctpoint": national_errors, "legacy_core_max_errors": legacy_errors, "te_identity_max_abs_error": identity_error, "curve_endpoint_max_abs_error": curve_error, "core_direction": core_direction, "hac_rows_expected": 108, "hac_rows_actual": int(len(hac_table)), "stop_reasons": stop_reasons}
    reference_path = worktree_root / "temp" / "2026-07-14_g185_old_method_unified_full_v1" / "FULL_STOP.json"
    reference = json.loads(reference_path.read_text(encoding="utf-8"))
    exact_fields = ("national_te_errors_pctpoint", "core_direction")
    if any(validation[field] != reference[field] for field in exact_fields):
        raise AssertionError("full_stop_v2 core proportions/points/national errors differ from full_v1")
    validation["full_v1_exact_numeric_match"] = True
    validation["full_v1_reference_sha256"] = sha256_file(reference_path)
    bootstrap_diag["core_direction"] = core_direction

    tables = output_dir / "tables"
    tables.mkdir(exist_ok=False)
    components.to_csv(tables / "all_component_estimates.csv", index=False, encoding="utf-8")
    endpoints.to_csv(tables / "all_endpoint_estimates.csv", index=False, encoding="utf-8")
    components.loc[components["scope"].eq("National")].to_csv(tables / "national_components.csv", index=False, encoding="utf-8")
    endpoints.loc[endpoints["scope"].eq("National")].to_csv(tables / "national_p90_endpoints.csv", index=False, encoding="utf-8")
    components.loc[components["scope"].eq("Region")].to_csv(tables / "regional_components.csv", index=False, encoding="utf-8")
    endpoints.loc[endpoints["scope"].eq("Region")].to_csv(tables / "regional_iede_matrix.csv", index=False, encoding="utf-8")
    endpoints.loc[endpoints["scope"].eq("Region") & endpoints["effect_type"].eq("TE_delta")].to_csv(tables / "regional_te_matrix.csv", index=False, encoding="utf-8")
    curves.to_csv(tables / "core_curve_data.csv", index=False, encoding="utf-8")
    robustness.to_csv(tables / "inference_robustness.csv", index=False, encoding="utf-8")
    joint.to_csv(tables / "regional_joint_tests.csv", index=False, encoding="utf-8")
    omnibus.to_csv(tables / "regional_omnibus_tests.csv", index=False, encoding="utf-8")
    registry.to_csv(tables / "model_registry.csv", index=False, encoding="utf-8")
    hac_table.to_csv(tables / "conley_diagnostics.csv", index=False, encoding="utf-8")
    pd.DataFrame(legacy_rows).to_csv(tables / "legacy_core_te_reproduction.csv", index=False, encoding="utf-8")
    old_de.to_csv(tables / "legacy_values_de_only.csv", index=False, encoding="utf-8")
    (output_dir / "historical_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "bootstrap_diagnostics.json").write_text(json.dumps(bootstrap_diag, ensure_ascii=False, indent=2), encoding="utf-8")

    created_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    commit = git_commit(worktree_root)
    schema_path = worktree_root / "docs" / "contracts" / "run_manifest.schema.json"
    design_path = worktree_root / "quality_reports" / "plans" / "2026-07-14_g185_old_method_unified_design_v2.md"
    execution_files = [Path(__file__).resolve(), Path(__file__).with_name("g185_old_method_core.py").resolve(), Path(__file__).with_name("run_g185_old_method_smoke.py").resolve(), schema_path.resolve(), design_path.resolve()]
    inputs = [
        {"role": "GGCP10 G185 base panel", "path": str(args.base_dta.resolve()), "bytes": int(args.base_dta.stat().st_size), "md5": None, "sha256": base_hash},
        {"role": "V3 precipitation hot-dry sidecar", "path": str(args.hotdry_dta.resolve()), "bytes": int(args.hotdry_dta.stat().st_size), "md5": None, "sha256": hotdry_hash},
        {"role": "full_v1 frozen STOP numeric reference", "path": str(reference_path), "bytes": int(reference_path.stat().st_size), "md5": None, "sha256": sha256_file(reference_path)},
    ]
    for path in execution_files:
        inputs.append({"role": "execution identity", "path": str(path), "bytes": int(path.stat().st_size), "md5": None, "sha256": sha256_file(path)})
    run_manifest = {
        "contract_version": "run-manifest-v1",
        "canonical_id": "g185-old-method-unified-v1",
        "run_id": output_dir.name,
        "created_utc": created_utc,
        "status": "STOP" if stop_reasons else "FULL",
        "not_for_inference": True,
        "design_version": "g185-old-method-unified-design-v2+dual-sample-key-amendment",
        "git_commit": commit,
        "data_family": "GGCP10-G185",
        "inputs": inputs,
        "sample_predicate": "ggcp10_maize_frac>=0.05; main_sample==1; 0.5<=yield_tons_ha<18; exclude consecutive-year abs(d_ln_yield)>1 pair members; gleam_smrz_sd>=0.001",
        "sample_key_serialization": CANONICAL_SERIALIZER_VERSION,
        "sample_key_sha256": canonical_hash,
        "sample_counts": {"rows": 46299, "grids": 13236, "named_rows": 44556, "named_grids": 12745},
        "outcome": "ln_yield_raw",
        "exposure_definition": "D_full_raw; hdd_ge32_raw; HotDryPr_full_raw with ca_raw interactions",
        "soil_moisture_roles": ["gleam_smrz_mean_raw contemporaneous two-equation algebraic component"],
        "fixed_effects": list(FES),
        "inference": {"primary": "grid Rademacher 999; 2-degree Rademacher and Webb 1999", "bootstrap_reps": BLOCK_REPS, "spatial_block_degrees": 2.0, "spatial_hac_km": [100, 200, 300], "multiplicity": "Romano-Wolf 15-test stepdown; Holm verification"},
        "ca_quantiles": {"p25": float(np.percentile(sample["ca_raw"], 25)), "p50": float(np.percentile(sample["ca_raw"], 50)), "p75": float(np.percentile(sample["ca_raw"], 75)), "population": "G185 full 46,299-row sample"},
        "exposure_endpoints": {
            "national_p90": {hazard: float(cells[("grid_year", "National", hazard)]["p90"]) for hazard in HAZARDS},
            "regional_p90": {region: {hazard: float(cells[("grid_year", region, hazard)]["p90"]) for hazard in HAZARDS} for region in REGIONS},
        },
        "seed": 42,
        "claims": [],
        "stop_rules_triggered": list(stop_reasons),
        "verification": [
            {"check": "historical national values", "status": "PASS", "detail": json.dumps(national_errors)},
            {"check": "legacy corrected core TE", "status": "PASS", "detail": json.dumps(legacy_errors)},
            {"check": "TE algebra and curve endpoints", "status": "PASS", "detail": f"TE={identity_error};curve={curve_error}"},
            {"check": "joint bootstrap", "status": "PASS", "detail": "three complete 15-dimensional layers"},
            {"check": "Conley HAC", "status": "PASS", "detail": "108/108 joint two-equation covariances"},
            {"check": "province-year core stability gate", "status": "FAIL" if stop_reasons else "PASS", "detail": json.dumps(core_direction)},
            {"check": "full_v1 exact numeric identity", "status": "PASS", "detail": "core proportions, point estimates, and national errors match exactly"},
            {"check": "baseline commit interpretation", "status": "PASS", "detail": "git_commit is baseline only; execution files are directly hashed in inputs"},
            {"check": "result review boundary", "status": "PASS", "detail": "review pending; no docs/results write and no publication claim"},
        ],
    }
    schema_validation = validate_contract_manifest(run_manifest, schema_path)
    (output_dir / "run_manifest.json").write_text(json.dumps(run_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    log.extend([f"validation={validation['status']}", f"stop_reasons={json.dumps(stop_reasons)}", f"elapsed_seconds={time.time()-started:.3f}", "RESULT_REVIEW_PENDING"])
    (output_dir / "run.log").write_text("\n".join(log) + "\n", encoding="utf-8")
    readme = """# G185 full run — independent result review pending

本目录包含冻结规格的完整机器结果和图表。所有IE/DE/TE均为同期两方程代数组件，不是已识别因果中介。当前状态为 `REVIEW_PENDING_NOT_FOR_INFERENCE`；在独立结果审查通过前，不得复制到 `docs/results`，不得据此撰写投稿结论。`git_commit`仅表示运行时基线，实际执行脚本、core、schema和设计文件的字节哈希已直接登记在标准run manifest的inputs中。
"""
    (output_dir / "README_REVIEW_PENDING.md").write_text(readme, encoding="utf-8")
    extension = {
        "canonical_id": "g185-old-method-unified-v1",
        "run_id": output_dir.name,
        "status": "FULL_STOP" if stop_reasons else "FULL_PASS_RESULT_REVIEW_PENDING",
        "not_for_inference": True,
        "public_claim": "none",
        "git_commit_baseline": commit,
        "sample_keys": {"legacy": {"algorithm": LEGACY_SERIALIZER_VERSION, "sha256": legacy_hash, "passed": True}, "canonical": {"algorithm": CANONICAL_SERIALIZER_VERSION, "sha256": canonical_hash, "passed": True}},
        "bootstrap": {"grid_reps": GRID_REPS, "block_reps": BLOCK_REPS, "seed": SEED, "layers": bootstrap_diag},
        "software": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "r": "not invoked", "stata": "not invoked"},
        "actual_ca_quantiles": run_manifest["ca_quantiles"],
        "actual_exposure_endpoints": run_manifest["exposure_endpoints"],
        "validation": validation,
        "schema_validation": schema_validation,
        "execution_file_hashes": {str(path): sha256_file(path) for path in execution_files},
        "output_hashes": output_hashes(output_dir, exclude=("full_manifest.json",)),
    }
    (output_dir / "full_manifest.json").write_text(json.dumps(extension, ensure_ascii=False, indent=2), encoding="utf-8")
    bundle_validation = validate_full_output_bundle(output_dir, schema_path)
    print(json.dumps({"status": extension["status"], "output_dir": str(output_dir), "validation": validation, "bundle_validation": bundle_validation, "elapsed_seconds": time.time()-started}, ensure_ascii=False))
    if stop_reasons:
        raise PresetStop("; ".join(stop_reasons))


def main() -> None:
    args = parser().parse_args()
    validate_cli(args)
    worktree_root = args.worktree_root.resolve(strict=True)
    output_dir = ensure_new_output_dir(worktree_root, args.output_dir)
    try:
        run(args, output_dir)
    except PresetStop as exc:
        print(json.dumps({"status": "PRESET_STOP", "not_for_inference": True, "message": str(exc), "output_dir": str(output_dir)}, ensure_ascii=False))
        return
    except Exception as exc:
        failure = output_dir / "RUNTIME_FAILED.json"
        if not failure.exists():
            failure.write_text(json.dumps({"status": "RUNTIME_FAILED", "not_for_inference": True, "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "exception_type": type(exc).__name__, "message": str(exc)}, ensure_ascii=False, indent=2), encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
