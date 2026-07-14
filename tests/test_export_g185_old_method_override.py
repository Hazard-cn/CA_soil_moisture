from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "python" / "export_g185_old_method_override.py"
SPEC = importlib.util.spec_from_file_location("g185_override_export", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TestG185OverrideExport(unittest.TestCase):
    def test_curated_table_contract_keeps_all_core_spatial_methods(self) -> None:
        methods = tuple(MODULE.METHOD_LABEL)
        tables = {
        "model_registry": pd.DataFrame(
            [{"scope": "Region", "region": "NE", "hazard": "drought", "fe": "grid_year", "N": 4, "grids": 1, "spatial_blocks": 1, "m_K": 2, "y_K": 3}]
        ),
        "national_p90_endpoints": pd.DataFrame(
            [{"method": MODULE.HIST_METHOD, "hazard": "drought", "effect_type": "TE_delta", "sr_p25": 0.1, "sr_p75": 0.5, "hazard_p90": 1.0, "estimate_pct": 1.0, "ci_low_pct": 0.0, "ci_high_pct": 2.0, "N": 4, "grids": 1}]
        ),
        "regional_iede_matrix": pd.DataFrame(
            [
                {"method": method, "region": "NE", "hazard": "drought", "fe": "grid_year" if method == MODULE.HIST_METHOD else "grid_provyear", "effect_type": "TE_delta", "sr_p25": 0.1, "sr_p75": 0.5, "hazard_p90": 1.0, "estimate_pct": 1.0, "ci_low_pct": 0.0, "ci_high_pct": 2.0, "N": 4, "grids": 1, "spatial_blocks": 1}
                for method in (MODULE.HIST_METHOD, MODULE.PROVYEAR_METHOD)
            ]
        ),
        "inference_robustness": pd.DataFrame(
            [{"region": "NE", "hazard": "drought", "fe": "grid_year" if method == MODULE.HIST_METHOD else "grid_provyear", "method": method, "estimate_pct": 1.0, "ci_low_pct": 0.0, "ci_high_pct": 2.0, "N": 4, "grids": 1} for method in methods]
        ),
        "regional_joint_tests": pd.DataFrame([{"method": MODULE.HIST_METHOD, "region": "NE", "hazard": "drought"}]),
        "regional_omnibus_tests": pd.DataFrame([{"method": MODULE.HIST_METHOD, "hazard": "drought"}]),
        }
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            rows = MODULE.build_curated_tables(tables, tmp_path)
            self.assertEqual(rows["table4_core_spatial_inference.csv"], 6)
            output = pd.read_csv(tmp_path / "tables" / "table4_core_spatial_inference.csv")
            self.assertEqual(set(output["method"]), set(methods))

    def test_source_manifest_identity_is_frozen(self) -> None:
        self.assertEqual(
            MODULE.EXPECTED_SOURCE_MANIFEST_SHA256,
            "3a23e22b421f052a4afc5f83c6aa806dd5a8f081bdb83aded357b2af6ca8aaec",
        )
        self.assertEqual(MODULE.CANONICAL_ID, "g185-old-method-unified-override-v1")


if __name__ == "__main__":
    unittest.main()
