"""Cluster-validate the remaining region-first high-score candidates."""

from __future__ import annotations

import json
import time

import pandas as pd

from region_first_story_search import OUT_DIR, build_ranking, cluster_validate


def main() -> None:
    start = time.time()
    ranking_ols = pd.read_csv(OUT_DIR / "ranking_ols.csv")
    first_ranking = pd.read_csv(OUT_DIR / "ranking_cluster.csv")
    all_candidates = ranking_ols.loc[
        ranking_ols["region_score"].ge(
            ranking_ols["region_score"].max() - 1
        ),
        "sample_id",
    ].tolist()
    completed = set(first_ranking["sample_id"])
    remaining = [
        sample_id
        for sample_id in all_candidates
        if sample_id not in completed
    ]

    (
        index_new,
        regional_new,
        baseline_new,
        irrigation_new,
        phenology_new,
    ) = cluster_validate(remaining)

    regional = pd.concat(
        [
            pd.read_csv(OUT_DIR / "region_candidates_cluster.csv"),
            regional_new,
        ],
        ignore_index=True,
    ).drop_duplicates(["sample_id", "region", "hazard"])
    baseline = pd.concat(
        [
            pd.read_csv(OUT_DIR / "national_baseline_cluster.csv"),
            baseline_new,
        ],
        ignore_index=True,
    ).drop_duplicates(["sample_id", "hazard"])
    irrigation = pd.concat(
        [
            pd.read_csv(OUT_DIR / "national_irrigation_cluster.csv"),
            irrigation_new,
        ],
        ignore_index=True,
    ).drop_duplicates(["sample_id", "hazard"])
    phenology = pd.concat(
        [
            pd.read_csv(OUT_DIR / "national_phenology_cluster.csv"),
            phenology_new,
        ],
        ignore_index=True,
    ).drop_duplicates(["sample_id", "window"])
    index = (
        pd.concat(
            [
                first_ranking[
                    [
                        "sample_id",
                        "N_sample",
                        "N_grids_sample",
                        "active_rule_count",
                        "main_sample",
                        "zone_core",
                        "yield_domain",
                        "yield_jump",
                        "sm_sd",
                        "sm_coverage",
                        "sr_within",
                        "years_ge3",
                        "stable_province",
                    ]
                ],
                index_new,
            ],
            ignore_index=True,
        )
        .drop_duplicates("sample_id")
    )
    ranking = build_ranking(
        index, regional, baseline, irrigation, phenology
    )

    regional.to_csv(
        OUT_DIR / "all_highscore_region_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )
    baseline.to_csv(
        OUT_DIR / "all_highscore_baseline_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )
    irrigation.to_csv(
        OUT_DIR / "all_highscore_irrigation_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )
    phenology.to_csv(
        OUT_DIR / "all_highscore_phenology_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )
    ranking.to_csv(
        OUT_DIR / "all_highscore_ranking_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )

    manifest = {
        "n_candidates_total": len(all_candidates),
        "n_first_batch": len(completed),
        "n_remaining": len(remaining),
        "winner_cluster": str(ranking.iloc[0]["sample_id"]),
        "winner_region_score": int(ranking.iloc[0]["region_score"]),
        "elapsed_seconds": time.time() - start,
    }
    (OUT_DIR / "remaining_cluster_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(manifest)


if __name__ == "__main__":
    main()
