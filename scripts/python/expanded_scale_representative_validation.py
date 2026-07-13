"""Cluster validation for representative expanded GGCP10 scales."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pandas as pd

from expanded_scale_story_search import (
    HAZARDS,
    OUT_DIR,
    add_full_interactions,
    add_window_terms,
    baseline_result,
    compound_result,
    fit_fe_cluster,
    load_panel,
    load_window_panel,
    moderator_result,
    phenology_rows,
    unique_variants,
)


REPRESENTATIVE_IDS = (
    "G001",
    "G065",
    "G003",
    "G129",
    "G002",
    "G195",
    "G255",
    "G256",
)


def metadata(meta: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in meta.items() if key != "mask"}


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    panel = add_full_interactions(load_panel())
    variants = unique_variants(panel)
    indexed = {str(variant["sample_id"]): variant for variant in variants}

    baseline_rows: list[dict[str, object]] = []
    compound_rows: list[dict[str, object]] = []
    irrigation_rows: list[dict[str, object]] = []
    for sample_id in REPRESENTATIVE_IDS:
        meta = indexed[sample_id]
        sub = panel.loc[meta["mask"]].copy()
        for hazard in HAZARDS:
            baseline_rows.append(
                {**metadata(meta), **baseline_result(sub, hazard, fit_fe_cluster)}
            )
            irrigation_rows.append(
                {
                    **metadata(meta),
                    **moderator_result(
                        sub, hazard, "irr_frac_raw", fit_fe_cluster
                    ),
                }
            )
        compound_rows.append(
            {**metadata(meta), **compound_result(sub, fit_fe_cluster)}
        )

    window_panel = add_window_terms(load_window_panel())
    window_variants = unique_variants(window_panel)
    phenology = phenology_rows(
        window_panel, window_variants, list(REPRESENTATIVE_IDS)
    )

    pd.DataFrame(baseline_rows).to_csv(
        OUT_DIR / "representative_baseline_cluster.csv", index=False
    )
    pd.DataFrame(compound_rows).to_csv(
        OUT_DIR / "representative_compound_cluster.csv", index=False
    )
    pd.DataFrame(irrigation_rows).to_csv(
        OUT_DIR / "representative_irrigation_cluster.csv", index=False
    )
    pd.DataFrame(phenology).to_csv(
        OUT_DIR / "representative_phenology_cluster.csv", index=False
    )

    manifest = {
        "representative_ids": list(REPRESENTATIVE_IDS),
        "elapsed_seconds": time.time() - start,
        "outputs": [
            "representative_baseline_cluster.csv",
            "representative_compound_cluster.csv",
            "representative_irrigation_cluster.csv",
            "representative_phenology_cluster.csv",
        ],
    }
    (OUT_DIR / "representative_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(manifest)


if __name__ == "__main__":
    main()
