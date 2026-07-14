from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "python"
sys.path.insert(0, str(SCRIPT_DIR))

from g185_old_method_core import (  # noqa: E402
    AbsorbedFit,
    TEST_ORDER,
    absorb_fixed_effects,
    algebraic_components,
    apply_g185_predicate,
    conley_covariance,
    draw_wild_weights,
    ensure_new_output_dir,
    hazard_spec,
    holm_adjust,
    legacy_sample_key_sha256,
    romano_wolf_stepdown,
    sample_key_sha256,
    serialize_sample_keys,
)
import run_g185_old_method_smoke as smoke_runner  # noqa: E402
import run_g185_old_method_full as full_runner  # noqa: E402


class TestG185OldMethodCore(unittest.TestCase):
    def test_sample_key_serialization_is_lf_and_lexical(self) -> None:
        keys = pd.DataFrame({"grid_id": [10, 2, 2], "year": [2017, 2018, 2016]})
        raw = serialize_sample_keys(keys)
        self.assertEqual(raw, b"grid_id,year\n10,2017\n2,2016\n2,2018\n")
        self.assertEqual(len(sample_key_sha256(keys)), 64)
        self.assertEqual(
            legacy_sample_key_sha256(keys),
            "56ade01f95769a3147a7c63555b0f620955c197c9211432ebd6aa75ae1bf5040",
        )

    def test_jump_rule_excludes_both_adjacent_rows(self) -> None:
        frame = pd.DataFrame(
            {
                "grid_id": [1, 1, 1, 2],
                "year": [2016, 2017, 2019, 2016],
                "ggcp10_maize_frac": [0.1] * 4,
                "main_sample": [1] * 4,
                "yield_tons_ha": [2.0] * 4,
                "ln_yield": [0.0, 1.2, 3.0, 0.0],
                "gleam_smrz_sd": [0.01] * 4,
            }
        )
        sample, _ = apply_g185_predicate(frame)
        self.assertEqual(sample[["grid_id", "year"]].to_records(index=False).tolist(), [(1, 2019), (2, 2016)])

    def test_alternating_projection_absorbs_both_groups(self) -> None:
        rng = np.random.default_rng(42)
        grid = np.repeat(np.arange(12), 4)
        year = np.tile(np.arange(4), 12)
        z = rng.normal(size=(48, 3)) + grid[:, None] / 5 + year[:, None] / 7
        residual, max_mean, _ = absorb_fixed_effects(z, (grid, year))
        self.assertLess(max_mean, 1e-10)
        for group in (grid, year):
            for value in np.unique(group):
                self.assertLess(np.max(np.abs(residual[group == value].mean(axis=0))), 1e-10)

    def test_algebra_identity(self) -> None:
        spec = hazard_spec("drought")
        mb = np.arange(len(spec.mediator_rhs), dtype=float)[None, :] / 10
        yb = np.arange(len(spec.yield_rhs), dtype=float)[None, :] / 20
        indirect, direct, total = algebraic_components(
            mb, yb, spec.mediator_rhs, spec.yield_rhs, spec, 0.4
        )
        np.testing.assert_allclose(total, indirect + direct, atol=1e-14)

    def test_wild_weight_support(self) -> None:
        rad = draw_wild_weights(100, range(10), 42, "rademacher")
        self.assertTrue(set(np.unique(rad)).issubset({-1.0, 1.0}))
        webb = draw_wild_weights(200, range(10), 42, "webb")
        support = {-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)}
        self.assertTrue(all(any(np.isclose(value, target) for target in support) for value in np.unique(webb)))

    def test_conley_includes_ordered_pairs_and_diagonal(self) -> None:
        x = np.array([[1.0], [2.0]])
        residual = np.array([1.0, -0.5])
        fit = AbsorbedFit(
            yvar="y",
            xvars=("x",),
            beta=np.array([0.0]),
            bread=np.array([[0.2]]),
            residual=residual,
            absorbed_x=x,
            grid_labels=np.array([1, 2]),
            cluster_labels=np.array([1, 2]),
            cluster_scores=x * residual[:, None],
            nobs=2,
            k=1,
            rank=1,
            singleton_grids=2,
            zero_norm_rows=0,
            max_abs_group_mean=0.0,
        )
        work = pd.DataFrame(
            {"grid_id": [1, 2], "latitude": [30.0, 30.0], "longitude": [110.0, 110.1]}
        )
        covariance, diag = conley_covariance(fit, work, 100.0)
        self.assertEqual(diag["ordered_pairs"], 4)
        self.assertTrue(np.isfinite(covariance).all())
        np.testing.assert_allclose(covariance, covariance.T, atol=1e-14)

    def test_romano_wolf_and_holm_interfaces(self) -> None:
        rng = np.random.default_rng(42)
        estimate = np.linspace(-0.2, 0.2, 15)
        bootstrap = estimate[None, :] + rng.normal(scale=0.1, size=(39, 15))
        adjusted = romano_wolf_stepdown(estimate, bootstrap, TEST_ORDER)
        self.assertEqual(adjusted.shape, (15,))
        self.assertTrue(np.all((adjusted >= 0) & (adjusted <= 1)))
        holm = holm_adjust(np.array([0.01, 0.03, 0.02]))
        self.assertTrue(np.all((holm >= 0) & (holm <= 1)))

    def test_output_guard_rejects_existing_and_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "worktree"
            (root / "temp").mkdir(parents=True)
            created = ensure_new_output_dir(root, root / "temp" / "new-run")
            self.assertTrue(created.is_dir())
            with self.assertRaises(FileExistsError):
                ensure_new_output_dir(root, created)
            with self.assertRaises(ValueError):
                ensure_new_output_dir(root, root / "outside")

    def test_runner_never_writes_to_preexisting_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "worktree"
            existing = root / "temp" / "existing-run"
            existing.mkdir(parents=True)
            sentinel = existing / "sentinel.bin"
            sentinel.write_bytes(b"immutable-existing-run")
            before_names = sorted(path.name for path in existing.iterdir())
            before_hash = hashlib.sha256(sentinel.read_bytes()).hexdigest()
            before_file_mtime = sentinel.stat().st_mtime_ns
            before_dir_mtime = existing.stat().st_mtime_ns
            argv = [
                "run_g185_old_method_smoke.py",
                "--project-root",
                str(root),
                "--worktree-root",
                str(root),
                "--base-dta",
                str(root / "missing-base.dta"),
                "--hotdry-dta",
                str(root / "missing-hotdry.dta"),
                "--output-dir",
                str(existing),
            ]
            with mock.patch.object(sys, "argv", argv):
                with self.assertRaises(FileExistsError):
                    smoke_runner.main()
            self.assertEqual(sorted(path.name for path in existing.iterdir()), before_names)
            self.assertEqual(hashlib.sha256(sentinel.read_bytes()).hexdigest(), before_hash)
            self.assertEqual(sentinel.stat().st_mtime_ns, before_file_mtime)
            self.assertEqual(existing.stat().st_mtime_ns, before_dir_mtime)
            self.assertFalse((existing / "SMOKE_FAILED.json").exists())

    def test_cli_rejects_incomplete_frozen_combinations(self) -> None:
        base_args = [
            "--project-root",
            "project",
            "--worktree-root",
            "worktree",
            "--base-dta",
            "base.dta",
            "--hotdry-dta",
            "hotdry.dta",
            "--output-dir",
            "worktree/temp/run",
        ]
        complete = smoke_runner.parser().parse_args(base_args)
        self.assertEqual(
            smoke_runner.validate_cli_contract(complete),
            (smoke_runner.FROZEN_FES, smoke_runner.FROZEN_SCORE_CLUSTERS),
        )
        incomplete_fe = smoke_runner.parser().parse_args(base_args + ["--fe", "grid_year"])
        with self.assertRaises(ValueError):
            smoke_runner.validate_cli_contract(incomplete_fe)
        incomplete_cluster = smoke_runner.parser().parse_args(
            base_args + ["--score-cluster", "grid"]
        )
        with self.assertRaises(ValueError):
            smoke_runner.validate_cli_contract(incomplete_cluster)

    def test_full_cli_requires_frozen_repetitions_and_complete_sets(self) -> None:
        base_args = [
            "--project-root", "project", "--worktree-root", "worktree",
            "--base-dta", "base.dta", "--hotdry-dta", "hotdry.dta",
            "--output-dir", "worktree/temp/full",
        ]
        full_runner.validate_cli(full_runner.parser().parse_args(base_args))
        with self.assertRaises(ValueError):
            full_runner.validate_cli(
                full_runner.parser().parse_args(base_args + ["--grid-reps", "19"])
            )
        with self.assertRaises(ValueError):
            full_runner.validate_cli(
                full_runner.parser().parse_args(base_args + ["--fe", "grid_year"])
            )

    def test_full_stop_bundle_retains_complete_outputs_and_valid_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tables = root / "tables"
            tables.mkdir()
            methods = (
                "grid_year_grid_rademacher_999",
                "grid_provyear_block_rademacher_1999",
                "grid_provyear_block_webb_1999",
            )
            regional_rows = [
                {"method": method, "region": region, "hazard": hazard, "effect_type": effect}
                for method in methods
                for region, hazard in full_runner.TEST_ORDER
                for effect in ("IE_delta", "DE_delta", "TE_delta")
            ]
            pd.DataFrame(regional_rows).to_csv(tables / "regional_iede_matrix.csv", index=False)
            pd.DataFrame(
                [{"method": method, "region": region, "hazard": hazard} for method in methods for region, hazard in full_runner.TEST_ORDER]
            ).to_csv(tables / "regional_joint_tests.csv", index=False)
            pd.DataFrame(
                [{"method": method, "hazard": hazard} for method in methods for hazard in full_runner.HAZARDS]
            ).to_csv(tables / "regional_omnibus_tests.csv", index=False)
            pd.DataFrame(
                [{"finite": True, "row": index} for index in range(108)]
            ).to_csv(tables / "conley_diagnostics.csv", index=False)
            pd.DataFrame([{"row": index} for index in range(36)]).to_csv(
                tables / "model_registry.csv", index=False
            )
            for filename in (
                "all_component_estimates.csv",
                "all_endpoint_estimates.csv",
                "national_p90_endpoints.csv",
            ):
                pd.DataFrame([{"present": True}]).to_csv(tables / filename, index=False)
            manifest = {
                "contract_version": "run-manifest-v1",
                "canonical_id": "g185-old-method-unified-v1",
                "run_id": "fixture-stop",
                "created_utc": "2026-07-15T00:00:00+00:00",
                "status": "STOP",
                "not_for_inference": True,
                "design_version": "v2",
                "git_commit": "3da8a12",
                "data_family": "GGCP10-G185",
                "inputs": [{"role": "fixture", "path": "fixture", "bytes": 0, "sha256": "0" * 64}],
                "sample_predicate": "fixture predicate",
                "sample_key_serialization": "sample-key-csv-v1",
                "sample_key_sha256": "1" * 64,
                "outcome": "ln_yield_raw",
                "exposure_definition": "fixture exposures",
                "fixed_effects": ["grid_year", "grid_provyear"],
                "inference": {"primary": "fixture", "bootstrap_reps": 1999, "spatial_block_degrees": 2, "multiplicity": "RW/Holm"},
                "seed": 42,
                "claims": [],
                "stop_rules_triggered": ["fixture preset stop"],
                "verification": [{"check": "fixture", "status": "FAIL"}],
            }
            (root / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (root / "full_manifest.json").write_text(
                json.dumps({"status": "FULL_STOP", "validation": {"stop_reasons": ["fixture"]}}),
                encoding="utf-8",
            )
            (root / "historical_validation.json").write_text("{}", encoding="utf-8")
            (root / "bootstrap_diagnostics.json").write_text("{}", encoding="utf-8")
            (root / "run.log").write_text("PRESET_STOP\n", encoding="utf-8")
            (root / "README_REVIEW_PENDING.md").write_text("STOP\n", encoding="utf-8")
            schema = Path(__file__).resolve().parents[1] / "docs" / "contracts" / "run_manifest.schema.json"
            result = full_runner.validate_full_output_bundle(root, schema)
            self.assertEqual(result["regional_iede_rows"], 135)
            self.assertEqual(result["hac_rows"], 108)

    def test_run_level_completion_validator_binds_all_six_pairs(self) -> None:
        omnibus = [
            {"hazard": hazard, "rank": 4, "finite": True, "holm_finite": True}
            for hazard in smoke_runner.HAZARDS
        ]
        diagnostics = {}
        for fe in smoke_runner.FROZEN_FES:
            diagnostics[fe] = {
                "dimension": 15,
                "grid_rademacher_shape": [19, 15],
                "grid_rademacher_covariance_rank": 15,
                "romano_wolf_grid_rademacher_count": 15,
                "romano_wolf_grid_rademacher_finite_count": 15,
                "omnibus_grid_rademacher": copy.deepcopy(omnibus),
                "rademacher_shape": [19, 15],
                "rademacher_covariance_rank": 15,
                "romano_wolf_rademacher_count": 15,
                "romano_wolf_rademacher_finite_count": 15,
                "omnibus_rademacher": copy.deepcopy(omnibus),
                "webb_shape": [19, 15],
                "webb_covariance_rank": 15,
                "romano_wolf_webb_count": 15,
                "romano_wolf_webb_finite_count": 15,
                "omnibus_webb": copy.deepcopy(omnibus),
            }
        declaration = {
            "fixed_effects": list(smoke_runner.FROZEN_FES),
            "methods": list(smoke_runner.FROZEN_METHODS),
            "bootstrap_reps": 19,
            "test_dimension": 15,
        }
        result = smoke_runner.validate_completion_contract(declaration, diagnostics)
        self.assertEqual(result["pair_count"], 6)
        broken = copy.deepcopy(diagnostics)
        broken["grid_year"]["romano_wolf_webb_finite_count"] = 14
        with self.assertRaises(AssertionError):
            smoke_runner.validate_completion_contract(declaration, broken)

    def test_hac_summary_is_derived_from_all_180_status_items(self) -> None:
        status = json.dumps(
            {
                str(bandwidth): {"mediator_finite": True, "yield_finite": True}
                for bandwidth in (100, 200, 300)
            }
        )
        rows = [
            {"fe": fe, "region": region, "hazard": hazard, "hac_status": status}
            for fe in smoke_runner.FROZEN_FES
            for region, hazard in smoke_runner.TEST_ORDER
        ]
        registry = pd.DataFrame(rows)
        summary = smoke_runner.summarize_hac_status(registry)
        self.assertEqual(summary["finite_items"], 180)
        self.assertTrue(summary["all_finite"])
        broken = registry.copy()
        bad = json.loads(broken.loc[0, "hac_status"])
        bad["100"]["mediator_finite"] = False
        broken.loc[0, "hac_status"] = json.dumps(bad)
        with self.assertRaises(RuntimeError):
            smoke_runner.summarize_hac_status(broken)


if __name__ == "__main__":
    unittest.main()
