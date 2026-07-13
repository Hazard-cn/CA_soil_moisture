"""Data loading, sample assertions, and preflight tables for G185 v3."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from g185_v3_config import PREFLIGHT_DIR, REGIONS, REQUIRED_FIELDS, SCALE_ID


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
SCRIPT_DIR = PROJ / "scripts/python"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from ggcp10_parallel_rules_69038_search import BASE_DTA  # noqa: E402
from expanded_scale_story_search import add_full_interactions, load_panel, unique_variants  # noqa: E402


def load_g185_sample() -> tuple[pd.DataFrame, dict[str, object], pd.DataFrame]:
    panel = add_full_interactions(load_panel())
    if "latitude" not in panel.columns or "longitude" not in panel.columns:
        coords = pd.read_stata(BASE_DTA, columns=["grid_id", "year", "latitude", "longitude"])
        panel = panel.merge(coords, on=["grid_id", "year"], how="left", validate="one_to_one")
    variants = {str(meta["sample_id"]): meta for meta in unique_variants(panel)}
    if SCALE_ID not in variants:
        raise KeyError(SCALE_ID)
    meta = variants[SCALE_ID]
    sample = panel.loc[meta["mask"]].copy()
    sample["province_year_code"] = pd.factorize(
        pd.MultiIndex.from_arrays([sample["province"].astype(str), sample["year"].astype(int)]),
        sort=True,
    )[0]
    sample["year_fe_code"] = pd.factorize(sample["year"].astype(int), sort=True)[0]
    sample["irr_annual"] = sample["irr_frac_raw"]
    sample["irr_first"] = sample.groupby("grid_id", observed=True)["irr_frac_raw"].transform("first")
    sample["irr_grid_mean"] = sample.groupby("grid_id", observed=True)["irr_frac_raw"].transform("mean")
    return sample, meta, panel


def assert_g185(sample: pd.DataFrame, meta: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in sample.columns:
            errors.append(f"missing required field: {field}")
    expected_rules = {
        "main_sample": 1,
        "zone_core": 0,
        "yield_domain": 1,
        "yield_jump": 1,
        "sm_sd": 1,
        "sm_coverage": 0,
        "sr_within": 0,
        "years_ge3": 0,
        "stable_province": 0,
    }
    for key, expected in expected_rules.items():
        if int(meta.get(key, -1)) != expected:
            errors.append(f"{key} expected {expected}, got {meta.get(key)}")
    if len(sample) != 46299:
        errors.append(f"G185 N expected 46299, got {len(sample)}")
    if sample["grid_id"].nunique() != 13236:
        errors.append(f"G185 grids expected 13236, got {sample['grid_id'].nunique()}")
    years = tuple(int(x) for x in sorted(sample["year"].dropna().unique()))
    if years != (2016, 2017, 2018, 2019):
        errors.append(f"years expected 2016-2019, got {years}")
    named = sample.loc[sample["maize_zone"].astype(str).isin(REGIONS)]
    if len(named) != 44556:
        errors.append(f"named-region N expected 44556, got {len(named)}")
    if named["grid_id"].nunique() != 12745:
        errors.append(f"named-region grids expected 12745, got {named['grid_id'].nunique()}")
    expected_counts = {"NE": 20794, "HHH": 12213, "SW": 7232, "NW": 3414, "SH": 903, "Other": 1743}
    counts = sample["maize_zone"].astype(str).value_counts().to_dict()
    for region, expected in expected_counts.items():
        got = int(counts.get(region, 0))
        if got != expected:
            errors.append(f"{region} N expected {expected}, got {got}")
    range_checks = [
        ("ca_raw", 0, 1),
        ("irr_frac_raw", 0, 1),
        ("yield_tons_ha", 0.5, 18),
    ]
    for col, lo, hi in range_checks:
        if col in sample and not sample[col].between(lo, hi, inclusive="left" if col == "yield_tons_ha" else "both").all():
            errors.append(f"{col} outside expected range")
    for col in ("D_full_raw", "hdd_ge32_raw", "HotDryPr_full_raw"):
        if col in sample and sample[col].lt(0).any():
            errors.append(f"{col} contains negative values")
    if not sample["latitude"].between(15, 55).all() or not sample["longitude"].between(70, 140).all():
        errors.append("coordinates outside broad China/G185 documented range")
    if errors:
        raise AssertionError("; ".join(errors))
    return errors


def write_preflight(sample: pd.DataFrame, meta: dict[str, object]) -> None:
    PREFLIGHT_DIR.mkdir(parents=True, exist_ok=True)
    schema = []
    for col in REQUIRED_FIELDS:
        schema.append(
            {
                "field": col,
                "present": col in sample.columns,
                "dtype": str(sample[col].dtype) if col in sample.columns else "",
                "nonmissing": int(sample[col].notna().sum()) if col in sample.columns else 0,
            }
        )
    pd.DataFrame(schema).to_csv(PREFLIGHT_DIR / "input_schema.csv", index=False, encoding="utf-8-sig")
    miss = (
        sample[list(REQUIRED_FIELDS)]
        .isna()
        .sum()
        .reset_index()
        .rename(columns={"index": "field", 0: "missing"})
    )
    miss["missing_share"] = miss["missing"] / len(sample)
    miss.to_csv(PREFLIGHT_DIR / "missingness.csv", index=False, encoding="utf-8-sig")

    filter_text = [
        "# G185 filter definitions",
        "",
        "- Base eligibility: `ggcp10_maize_frac >= 0.05`.",
        "- Activated rules: `main_sample=1`, `yield_domain=1`, `yield_jump=1`, `sm_sd=1`.",
        "- Inactive rules: `zone_core`, `sm_coverage`, `sr_within`, `years_ge3`, `stable_province`.",
        "- `yield_domain=1`: `yield_tons_ha >= 0.5` and `yield_tons_ha < 18`, applied at grid-year level.",
        "- `yield_jump=1`: excludes observations with `abs(dln_prev) > 1` or `abs(dln_next) > 1`, applied at grid-year level.",
        "- `sm_sd=1`: requires `gleam_smrz_sd >= 0.001`, applied at grid-year level.",
        "",
        "Source implementation: `scripts/python/expanded_scale_story_search.py::build_mask`.",
    ]
    (PREFLIGHT_DIR / "filter_definitions.md").write_text("\n".join(filter_text) + "\n", encoding="utf-8")

    modifier_keywords = ("soil", "bdod", "clay", "sand", "silt", "phh2o", "terrain", "slope", "elevation", "aridity")
    rows = []
    for col in sample.columns:
        lower = col.lower()
        if any(key in lower for key in modifier_keywords):
            rows.append(
                {
                    "field": col,
                    "dtype": str(sample[col].dtype),
                    "nonmissing": int(sample[col].notna().sum()),
                    "approved_whitelist": 0,
                    "notes": "inventory only; MODIFIER_WHITELIST is empty in first v3 run",
                }
            )
    pd.DataFrame(rows).to_csv(PREFLIGHT_DIR / "modifier_inventory.csv", index=False, encoding="utf-8-sig")

    unresolved = [
        "# Unresolved timing and modifier items",
        "",
        "## SR timing",
        "",
        "The primary v3 run uses observed `ca_raw`. Current code and available local docs do not establish a separately documented lagged SR field for this v3 response-surface run. No lagged-SR sensitivity is promoted.",
        "",
        "## Irrigation timing",
        "",
        "`irr_frac_raw` is available as an annual/grid-year field. Because no documented pre-season/static irrigation field was located in the required v3 fields, primary irrigation-boundary estimates use `irr_first`, with `irr_annual` and `irr_grid_mean` retained as sensitivity definitions.",
        "",
        "## Predetermined modifiers",
        "",
        "Soil/topographic/long-run climate modifiers are inventoried in `modifier_inventory.csv`; `MODIFIER_WHITELIST=[]` for this first v3 run.",
        "",
        "## Filter definitions",
        "",
        "Exact operational definitions are recorded in `filter_definitions.md`.",
    ]
    (PREFLIGHT_DIR / "unresolved_items.md").write_text("\n".join(unresolved) + "\n", encoding="utf-8")

    py = sample.groupby("province_year_code").size().describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9])
    spatial = pd.DataFrame(
        {
            "metric": [
                "province_year_cells",
                "province_year_min",
                "province_year_p10",
                "province_year_p50",
                "province_year_p90",
                "province_year_max",
            ],
            "value": [
                int(sample["province_year_code"].nunique()),
                float(py["min"]),
                float(py["10%"]),
                float(py["50%"]),
                float(py["90%"]),
                float(py["max"]),
            ],
        }
    )
    spatial.to_csv(PREFLIGHT_DIR / "spatial_block_summary.csv", index=False, encoding="utf-8-sig")
    (PREFLIGHT_DIR / "g185_sample_meta.json").write_text(
        json.dumps({k: v for k, v in meta.items() if k != "mask"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
