"""Export the reviewed G185 full-result bundle under an explicit gate override.

This script does not re-estimate any model.  It verifies the immutable source
bundle byte-for-byte, derives review tables, and renders publication-format
figures.  The historical STOP status remains part of the source provenance;
the override only removes that STOP rule's blocking effect for drafting.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image


EXPECTED_SOURCE_MANIFEST_SHA256 = (
    "3a23e22b421f052a4afc5f83c6aa806dd5a8f081bdb83aded357b2af6ca8aaec"
)
CANONICAL_ID = "g185-old-method-unified-override-v1"
REGIONS = ("NE", "HHH", "NW", "SW", "SH")
HAZARDS = ("drought", "heat", "hotdry")
CORE_COMBOS = (("NE", "drought"), ("HHH", "heat"), ("HHH", "hotdry"))
HIST_METHOD = "grid_year_grid_rademacher_999"
PROVYEAR_METHOD = "grid_provyear_block_rademacher_1999"
REGION_LABEL = {
    "NE": "Northeast",
    "HHH": "Huang-Huai-Hai",
    "NW": "Northwest",
    "SW": "Southwest",
    "SH": "Southern Hills",
}
HAZARD_LABEL = {"drought": "Drought", "heat": "Heat", "hotdry": "Hot-dry"}
METHOD_LABEL = {
    HIST_METHOD: "Grid + year FE; grid wild",
    PROVYEAR_METHOD: "Grid + province-year FE; 2-degree wild",
    "grid_provyear_block_webb_1999": "Grid + province-year FE; 2-degree Webb",
    "grid_provyear_conley_100km": "Grid + province-year FE; HAC 100 km",
    "grid_provyear_conley_200km": "Grid + province-year FE; HAC 200 km",
    "grid_provyear_conley_300km": "Grid + province-year FE; HAC 300 km",
}


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit(root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def ensure_new_output_dir(worktree_root: Path, output_dir: Path) -> Path:
    root = worktree_root.resolve(strict=True)
    temp_root = (root / "temp").resolve(strict=True) if (root / "temp").exists() else root / "temp"
    if not temp_root.exists():
        temp_root.mkdir(exist_ok=False)
        temp_root = temp_root.resolve(strict=True)
    target = output_dir.absolute()
    if target.exists():
        raise FileExistsError(f"output directory already exists: {target}")
    if target.parent.resolve(strict=True) != temp_root:
        raise ValueError("output directory must be a direct child of worktree/temp")
    if target.is_symlink():
        raise ValueError("output directory must not be a link")
    target.mkdir(exist_ok=False)
    return target.resolve(strict=True)


def validate_source_bundle(source_run: Path) -> tuple[dict[str, object], dict[str, object]]:
    source_run = source_run.resolve(strict=True)
    manifest_path = source_run / "full_manifest.json"
    actual_manifest_hash = sha256_file(manifest_path)
    if actual_manifest_hash != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise AssertionError(
            f"source full_manifest hash mismatch: {actual_manifest_hash}"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("canonical_id") != "g185-old-method-unified-v1":
        raise AssertionError("unexpected source canonical ID")
    if manifest.get("status") != "FULL_STOP":
        raise AssertionError("source status must remain FULL_STOP")
    expected_hashes = manifest.get("output_hashes", {})
    if len(expected_hashes) != 20:
        raise AssertionError("source output hash registry must contain 20 files")
    verified: dict[str, str] = {}
    for relative, expected in expected_hashes.items():
        path = source_run / relative
        if not path.is_file():
            raise AssertionError(f"source output missing: {relative}")
        actual = sha256_file(path)
        if actual != expected:
            raise AssertionError(f"source output hash mismatch: {relative}")
        verified[relative] = actual
    validation = manifest.get("validation", {})
    if validation.get("stop_reasons") != [
        "province-year core sign/share STOP rule triggered"
    ]:
        raise AssertionError("source STOP reason differs from reviewed record")
    core = validation.get("core_direction", {})
    expected_share = 0.8419209604802401
    if abs(core["NE:drought"]["rademacher_same_direction_share"] - expected_share) > 1e-15:
        raise AssertionError("NE drought direction share differs from reviewed record")
    return manifest, {
        "source_full_manifest_sha256": actual_manifest_hash,
        "registered_outputs": len(verified),
        "registered_outputs_verified": len(verified),
        "all_registered_output_hashes_match": True,
        "registered_hashes": verified,
    }


def load_tables(source_run: Path) -> dict[str, pd.DataFrame]:
    table_root = source_run / "tables"
    names = (
        "national_components",
        "national_p90_endpoints",
        "regional_iede_matrix",
        "core_curve_data",
        "inference_robustness",
        "regional_joint_tests",
        "regional_omnibus_tests",
        "model_registry",
        "conley_diagnostics",
    )
    return {name: pd.read_csv(table_root / f"{name}.csv") for name in names}


def validate_table_contract(tables: dict[str, pd.DataFrame]) -> dict[str, int]:
    expected_rows = {
        "national_components": 81,
        "national_p90_endpoints": 27,
        "regional_iede_matrix": 135,
        "core_curve_data": 909,
        "inference_robustness": 198,
        "regional_joint_tests": 45,
        "regional_omnibus_tests": 9,
        "model_registry": 36,
        "conley_diagnostics": 108,
    }
    actual = {name: int(len(frame)) for name, frame in tables.items()}
    if actual != expected_rows:
        raise AssertionError(f"source table row counts changed: {actual}")
    regional = tables["regional_iede_matrix"]
    if regional[["region", "hazard"]].drop_duplicates().shape[0] != 15:
        raise AssertionError("five-zone by three-hazard matrix is incomplete")
    if not tables["conley_diagnostics"]["finite"].eq(True).all():
        raise AssertionError("non-finite Conley diagnostic found")
    return actual


def build_curated_tables(
    tables: dict[str, pd.DataFrame], output_dir: Path
) -> dict[str, int]:
    table_dir = output_dir / "tables"
    table_dir.mkdir(exist_ok=False)

    registry = tables["model_registry"]
    support = registry.loc[
        registry["scope"].eq("Region") & registry["fe"].eq("grid_year"),
        ["region", "hazard", "N", "grids", "spatial_blocks", "m_K", "y_K"],
    ].copy()
    support["low_block_count_note"] = np.where(
        support["spatial_blocks"].lt(30), "low_block_count", ""
    )
    support.to_csv(table_dir / "table1_sample_support.csv", index=False, encoding="utf-8")

    national = tables["national_p90_endpoints"]
    national = national.loc[
        national["method"].eq(HIST_METHOD),
        [
            "hazard",
            "effect_type",
            "sr_p25",
            "sr_p75",
            "hazard_p90",
            "estimate_pct",
            "ci_low_pct",
            "ci_high_pct",
            "N",
            "grids",
        ],
    ].copy()
    national.to_csv(
        table_dir / "table2_national_iede_endpoints.csv", index=False, encoding="utf-8"
    )

    regional = tables["regional_iede_matrix"]
    regional = regional.loc[
        regional["method"].isin((HIST_METHOD, PROVYEAR_METHOD)),
        [
            "region",
            "hazard",
            "fe",
            "method",
            "effect_type",
            "sr_p25",
            "sr_p75",
            "hazard_p90",
            "estimate_pct",
            "ci_low_pct",
            "ci_high_pct",
            "N",
            "grids",
            "spatial_blocks",
        ],
    ].copy()
    regional["method_label"] = regional["method"].map(METHOD_LABEL)
    regional.to_csv(
        table_dir / "table3_five_zone_iede_both_fe.csv", index=False, encoding="utf-8"
    )

    robustness = tables["inference_robustness"]
    keep_methods = tuple(METHOD_LABEL)
    core_mask = pd.Series(
        [(r, h) in CORE_COMBOS for r, h in zip(robustness["region"], robustness["hazard"], strict=True)],
        index=robustness.index,
    )
    core = robustness.loc[
        core_mask & robustness["method"].isin(keep_methods),
        [
            "region",
            "hazard",
            "fe",
            "method",
            "estimate_pct",
            "ci_low_pct",
            "ci_high_pct",
            "N",
            "grids",
        ],
    ].copy()
    core["method_label"] = core["method"].map(METHOD_LABEL)
    core.to_csv(
        table_dir / "table4_core_spatial_inference.csv", index=False, encoding="utf-8"
    )

    joint = tables["regional_joint_tests"].copy()
    joint["method_label"] = joint["method"].map(METHOD_LABEL)
    joint.to_csv(
        table_dir / "table5_complete_region_joint_tests.csv", index=False, encoding="utf-8"
    )
    omnibus = tables["regional_omnibus_tests"].copy()
    omnibus["method_label"] = omnibus["method"].map(METHOD_LABEL)
    omnibus.to_csv(
        table_dir / "table6_region_omnibus_tests.csv", index=False, encoding="utf-8"
    )
    return {
        "table1_sample_support.csv": len(support),
        "table2_national_iede_endpoints.csv": len(national),
        "table3_five_zone_iede_both_fe.csv": len(regional),
        "table4_core_spatial_inference.csv": len(core),
        "table5_complete_region_joint_tests.csv": len(joint),
        "table6_region_omnibus_tests.csv": len(omnibus),
    }


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
            "axes.titleweight": "semibold",
            "legend.frameon": False,
        }
    )


def save_figure(fig: plt.Figure, path: Path) -> None:
    fig.set_size_inches(12, 5)
    fig.savefig(path, dpi=300, facecolor="white")
    plt.close(fig)


def make_figures(tables: dict[str, pd.DataFrame], output_dir: Path) -> dict[str, dict[str, object]]:
    configure_plots()
    fig_dir = output_dir / "figures"
    fig_dir.mkdir(exist_ok=False)

    components = tables["national_components"]
    national = components.loc[components["method"].eq(HIST_METHOD)]
    colors = {"IE": "#6baed6", "DE": "#fdae6b", "TE": "#252525"}
    levels = ("P25", "P50", "P75")
    fig, axes = plt.subplots(1, 3, figsize=(12, 5), layout="constrained")
    for axis, hazard in zip(axes, HAZARDS, strict=True):
        sub = national.loc[national["hazard"].eq(hazard)]
        x = np.arange(3)
        for offset, effect in zip((-0.24, 0.0, 0.24), ("IE", "DE", "TE"), strict=True):
            rows = sub.loc[sub["effect_type"].eq(effect)].set_index("sr_level")
            values = np.array([rows.loc[level, "estimate_pct"] for level in levels], dtype=float)
            axis.bar(x + offset, values, width=0.22, color=colors[effect], label=effect)
        axis.axhline(0, color="#666666", linewidth=0.8)
        axis.set_xticks(x, levels)
        axis.set_title(HAZARD_LABEL[hazard])
        axis.set_ylabel("Component at hazard P90 (%)")
    axes[0].legend(ncol=3, loc="best")
    fig.suptitle("National G185 algebraic IE, DE and TE by observed SR quantile")
    save_figure(fig, fig_dir / "fig1_national_iede.png")

    curves = tables["core_curve_data"]
    curves = curves.loc[curves["method"].eq(HIST_METHOD)]
    fig, axes = plt.subplots(1, 3, figsize=(12, 5), layout="constrained")
    for axis, (region, hazard) in zip(axes, CORE_COMBOS, strict=True):
        sub = curves.loc[curves["region"].eq(region) & curves["hazard"].eq(hazard)]
        x = sub["exposure"].to_numpy(dtype=float)
        estimate = sub["estimate_pct"].to_numpy(dtype=float)
        low = sub["ci_low_pct"].to_numpy(dtype=float)
        high = sub["ci_high_pct"].to_numpy(dtype=float)
        axis.plot(x, estimate, color="#2171b5", linewidth=2)
        axis.fill_between(x, low, high, color="#9ecae1", alpha=0.5)
        axis.axhline(0, color="#666666", linewidth=0.8)
        axis.set_title(f"{REGION_LABEL[region]}: {HAZARD_LABEL[hazard]}")
        axis.set_xlabel("Exposure from 0 to regional P90")
        axis.set_ylabel("P75-P25 algebraic TE (%)")
    fig.suptitle("Continuous old-linear buffering contrasts")
    save_figure(fig, fig_dir / "fig2_core_linear_curves.png")

    regional = tables["regional_iede_matrix"]
    regional = regional.loc[regional["method"].eq(HIST_METHOD)]
    fig, axes = plt.subplots(1, 3, figsize=(12, 5), layout="constrained", sharey=False)
    x = np.arange(len(REGIONS))
    for axis, hazard in zip(axes, HAZARDS, strict=True):
        sub = regional.loc[regional["hazard"].eq(hazard)]
        for offset, effect in zip((-0.24, 0.0, 0.24), ("IE_delta", "DE_delta", "TE_delta"), strict=True):
            rows = sub.loc[sub["effect_type"].eq(effect)].set_index("region").reindex(REGIONS)
            values = rows["estimate_pct"].to_numpy(dtype=float)
            low = rows["ci_low_pct"].to_numpy(dtype=float)
            high = rows["ci_high_pct"].to_numpy(dtype=float)
            yerr = np.vstack((np.maximum(values - low, 0), np.maximum(high - values, 0)))
            label = effect.replace("_delta", "")
            axis.bar(x + offset, values, width=0.22, color=colors[label], label=label)
            axis.errorbar(x + offset, values, yerr=yerr, fmt="none", ecolor="#555555", capsize=2, linewidth=0.7)
        axis.axhline(0, color="#666666", linewidth=0.8)
        axis.set_xticks(x, REGIONS)
        axis.set_title(HAZARD_LABEL[hazard])
        axis.set_ylabel("P75-P25 endpoint at regional P90 (%)")
    axes[0].legend(ncol=3, loc="best")
    fig.suptitle("Five-zone algebraic IE, DE and TE decomposition")
    save_figure(fig, fig_dir / "fig3_five_zone_iede.png")

    metadata: dict[str, dict[str, object]] = {}
    for path in sorted(fig_dir.glob("*.png")):
        with Image.open(path) as image:
            dpi = image.info.get("dpi", (None, None))
            metadata[path.name] = {
                "width_px": image.width,
                "height_px": image.height,
                "dpi_x": None if dpi[0] is None else float(dpi[0]),
                "dpi_y": None if dpi[1] is None else float(dpi[1]),
                "mode": image.mode,
                "sha256": sha256_file(path),
            }
            if image.width != 3600 or image.height != 1500:
                raise AssertionError(f"figure dimensions are not 12x5 inches at 300 DPI: {path.name}")
            if dpi[0] is None or abs(float(dpi[0]) - 300.0) > 0.1:
                raise AssertionError(f"figure DPI is not 300: {path.name}")
    return metadata


def output_hashes(directory: Path, excluded: tuple[str, ...]) -> dict[str, str]:
    return {
        path.relative_to(directory).as_posix(): sha256_file(path)
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.name not in excluded
    }


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(description=__doc__)
    out.add_argument("--worktree-root", type=Path, required=True)
    out.add_argument("--source-run", type=Path, required=True)
    out.add_argument("--output-dir", type=Path, required=True)
    return out


def run(args: argparse.Namespace) -> Path:
    started = time.time()
    root = args.worktree_root.resolve(strict=True)
    source = args.source_run.resolve(strict=True)
    output = ensure_new_output_dir(root, args.output_dir)
    source_manifest, source_check = validate_source_bundle(source)
    tables = load_tables(source)
    source_rows = validate_table_contract(tables)
    curated_rows = build_curated_tables(tables, output)
    figure_metadata = make_figures(tables, output)

    verification = {
        "status": "PASS_DERIVED_OVERRIDE_PACKAGE_REVIEW_PENDING",
        "source_bundle": source_check,
        "source_table_rows": source_rows,
        "curated_table_rows": curated_rows,
        "figure_metadata": figure_metadata,
        "historical_status_preserved": source_manifest["status"] == "FULL_STOP",
        "estimand_changed": False,
        "model_reestimated": False,
        "selection_by_significance": False,
        "override_disclosure": {
            "removed_blocking_rule": "NE drought Rademacher same-direction share >= 0.90",
            "observed_share": 0.8419209604802401,
            "interpretation": "reported limitation; no longer execution blocker by explicit user authorization",
        },
    }
    (output / "source_verification.json").write_text(
        json.dumps(verification, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    readme = """# G185 old-method override derived package

本目录逐字节核验已审查的历史FULL_STOP机器包，并在用户明确取消90%稳定性门槛阻断效力后生成派生表图。没有重新估计模型，没有修改估计量，没有按显著性筛选。原FULL_STOP状态和东北干旱84.19%的方向稳定性均保留为来源事实与核心局限。本包在独立结果/稿件审查前状态为REVIEW_PENDING_NOT_FOR_PUBLIC_CLAIM。
"""
    (output / "README_REVIEW_PENDING.md").write_text(readme, encoding="utf-8")
    log = [
        "REVIEW_PENDING_NOT_FOR_PUBLIC_CLAIM",
        f"created_utc={dt.datetime.now(dt.timezone.utc).isoformat()}",
        f"source_full_manifest_sha256={EXPECTED_SOURCE_MANIFEST_SHA256}",
        "source_registered_hashes=20/20",
        "model_reestimated=false",
        "estimand_changed=false",
        "selection_by_significance=false",
        "removed_blocking_rule=NE drought Rademacher same-direction share >= 0.90",
        "observed_share=0.8419209604802401",
        f"elapsed_seconds={time.time() - started:.3f}",
    ]
    (output / "run.log").write_text("\n".join(log) + "\n", encoding="utf-8")

    script_path = Path(__file__).resolve()
    manifest = {
        "canonical_id": CANONICAL_ID,
        "run_id": output.name,
        "status": "DERIVED_OVERRIDE_REVIEW_PENDING",
        "not_for_public_claim": True,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "git_commit_baseline": git_commit(root),
        "source": {
            "canonical_id": source_manifest["canonical_id"],
            "run_id": source_manifest["run_id"],
            "historical_status": source_manifest["status"],
            "full_manifest_sha256": EXPECTED_SOURCE_MANIFEST_SHA256,
            "registered_outputs_verified": 20,
        },
        "execution": {
            "script": "scripts/python/export_g185_old_method_override.py",
            "script_sha256": sha256_file(script_path),
            "python": platform.python_version(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "matplotlib": matplotlib.__version__,
            "model_reestimated": False,
            "estimand_changed": False,
        },
        "sample": {
            "rows": 46299,
            "grids": 13236,
            "named_rows": 44556,
            "named_grids": 12745,
            "canonical_sample_key_sha256": "36029c5f8ba689a1cbf6a14b688e8a43342ab8b7acd9b704136cb152fa170bcb",
            "legacy_sample_key_sha256": "5474250d140bef9a8fc0957158ed815f635220e0c0df7080d7a1b5f7d4469b89",
        },
        "override": verification["override_disclosure"],
        "interpretation_boundary": "IE/DE/TE are contemporaneous algebraic two-equation components, not identified causal mediation effects",
        "outputs": output_hashes(output, excluded=("override_manifest.json",)),
    }
    (output / "override_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "output_dir": str(output),
                "source_hashes": "20/20",
                "figures": len(figure_metadata),
                "tables": len(curated_rows),
                "elapsed_seconds": time.time() - started,
            },
            ensure_ascii=False,
        )
    )
    return output


def main() -> None:
    run(parser().parse_args())


if __name__ == "__main__":
    main()
