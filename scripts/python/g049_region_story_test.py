"""Test whether G049 regional heterogeneity supports the selected story."""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from expanded_scale_story_search import (
    HAZARDS,
    WINDOWS,
    add_full_interactions,
    add_window_terms,
    baseline_result,
    fit_fe_cluster,
    load_panel,
    load_window_panel,
    moderator_result,
    unique_variants,
)
from results_first_story_fit_search import compound_window_result


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
OUT_DIR = PROJ / "temp/2026-06-11_g049_region_story_test"
REPORT = PROJ / "quality_reports/2026-06-11_g049_region_story_test.md"
SAMPLE_ID = "G049"
REGION_ORDER = ("NE", "HHH", "NW", "SW", "SH", "Other")


def get_variant(panel: pd.DataFrame) -> dict[str, object]:
    variants = {str(meta["sample_id"]): meta for meta in unique_variants(panel)}
    return variants[SAMPLE_ID]


def support_rows(panel: pd.DataFrame, mask: np.ndarray) -> list[dict[str, object]]:
    sample = panel.loc[mask].copy()
    rows: list[dict[str, object]] = []
    for region in REGION_ORDER:
        sub = sample.loc[sample["maize_zone"].astype(str).eq(region)]
        if sub.empty:
            continue
        rows.append(
            {
                "region": region,
                "N_sample": int(len(sub)),
                "N_grids_sample": int(sub["grid_id"].nunique()),
                "ca_p25": float(sub["ca_raw"].quantile(0.25)),
                "ca_median": float(sub["ca_raw"].median()),
                "ca_p75": float(sub["ca_raw"].quantile(0.75)),
                "irr_median": float(sub["irr_frac_raw"].median()),
                "aridity_median": float(sub["aridity_raw"].median()),
                "drought_p90": float(sub["D_full_raw"].quantile(0.90)),
                "heat_p90": float(sub["hdd_ge32_raw"].quantile(0.90)),
                "hotdry_p90": float(
                    sub["HotDryPr_full_raw"].quantile(0.90)
                ),
            }
        )
    return rows


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    full_panel = add_full_interactions(load_panel())
    full_meta = get_variant(full_panel)
    full_sample = full_panel.loc[full_meta["mask"]].copy()

    window_panel = add_window_terms(load_window_panel())
    window_meta = get_variant(window_panel)
    window_sample = window_panel.loc[window_meta["mask"]].copy()

    support = pd.DataFrame(support_rows(full_panel, full_meta["mask"]))
    baseline_rows: list[dict[str, object]] = []
    irrigation_rows: list[dict[str, object]] = []
    phenology_rows: list[dict[str, object]] = []

    for region in REGION_ORDER:
        full_sub = full_sample.loc[
            full_sample["maize_zone"].astype(str).eq(region)
        ].copy()
        window_sub = window_sample.loc[
            window_sample["maize_zone"].astype(str).eq(region)
        ].copy()
        if full_sub.empty:
            continue
        for hazard in HAZARDS:
            try:
                result = baseline_result(
                    full_sub, hazard, fit_fe_cluster
                )
                baseline_rows.append(
                    {"region": region, "status": "estimated", **result}
                )
            except Exception as exc:
                baseline_rows.append(
                    {
                        "region": region,
                        "hazard": hazard,
                        "status": str(exc),
                    }
                )
            try:
                result = moderator_result(
                    full_sub,
                    hazard,
                    "irr_frac_raw",
                    fit_fe_cluster,
                )
                irrigation_rows.append(
                    {"region": region, "status": "estimated", **result}
                )
            except Exception as exc:
                irrigation_rows.append(
                    {
                        "region": region,
                        "hazard": hazard,
                        "status": str(exc),
                    }
                )

        for window in WINDOWS:
            try:
                result = compound_window_result(
                    window_sub, window, fit_fe_cluster
                )
                phenology_rows.append(
                    {"region": region, "status": "estimated", **result}
                )
            except Exception as exc:
                phenology_rows.append(
                    {
                        "region": region,
                        "window": window,
                        "status": str(exc),
                    }
                )
        print(f"[REGION] {region}", flush=True)

    baseline = pd.DataFrame(baseline_rows)
    irrigation = pd.DataFrame(irrigation_rows)
    phenology = pd.DataFrame(phenology_rows)
    support.to_csv(
        OUT_DIR / "region_support.csv", index=False, encoding="utf-8-sig"
    )
    baseline.to_csv(
        OUT_DIR / "region_baseline_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )
    irrigation.to_csv(
        OUT_DIR / "region_irrigation_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )
    phenology.to_csv(
        OUT_DIR / "region_phenology_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )

    manifest = {
        "sample_id": SAMPLE_ID,
        "regions": support["region"].tolist(),
        "elapsed_seconds": time.time() - start,
        "baseline_rows": len(baseline),
        "phenology_rows": len(phenology),
        "irrigation_rows": len(irrigation),
    }
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(manifest)


if __name__ == "__main__":
    main()
