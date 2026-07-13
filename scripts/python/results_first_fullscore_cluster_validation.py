"""Cluster validation of every OLS full-score story specification."""

from __future__ import annotations

import json
import time

import pandas as pd

from results_first_story_fit_search import (
    OUT_DIR,
    build_ranking,
    cluster_validate,
)


def main() -> None:
    start = time.time()
    ols_ranking = pd.read_csv(OUT_DIR / "story_fit_ranking_ols.csv")
    selected = ols_ranking.loc[
        ols_ranking["story_score"].eq(15), "sample_id"
    ].tolist()

    index, baseline, irrigation, phenology = cluster_validate(selected)
    ranking = build_ranking(index, baseline, irrigation, phenology)

    baseline.to_csv(
        OUT_DIR / "fullscore_cluster_baseline.csv",
        index=False,
        encoding="utf-8-sig",
    )
    irrigation.to_csv(
        OUT_DIR / "fullscore_cluster_irrigation.csv",
        index=False,
        encoding="utf-8-sig",
    )
    phenology.to_csv(
        OUT_DIR / "fullscore_cluster_phenology.csv",
        index=False,
        encoding="utf-8-sig",
    )
    ranking.to_csv(
        OUT_DIR / "fullscore_cluster_ranking.csv",
        index=False,
        encoding="utf-8-sig",
    )

    manifest = {
        "n_ols_fullscore": len(selected),
        "winner_cluster": str(ranking.iloc[0]["sample_id"]),
        "winner_score": int(ranking.iloc[0]["story_score"]),
        "winner_evidence": float(ranking.iloc[0]["evidence_score"]),
        "elapsed_seconds": time.time() - start,
    }
    (OUT_DIR / "fullscore_cluster_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(manifest)


if __name__ == "__main__":
    main()
