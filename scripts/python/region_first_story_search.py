"""Region-first exploratory search across the 256 GGCP10 scales."""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd

from expanded_scale_story_search import (
    HAZARDS,
    add_full_interactions,
    add_window_terms,
    baseline_result,
    fit_fe_cluster,
    fit_fe_ols,
    load_panel,
    load_window_panel,
    moderator_result,
    rhs_for,
    unique_variants,
)
from results_first_story_fit_search import compound_window_result


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
SOURCE_DIR = PROJ / "temp/2026-06-11_expanded_scale_story_search"
PHENOLOGY_SOURCE = (
    PROJ
    / "temp/2026-06-11_results_first_story_fit"
    / "phenology_all_scales_ols.csv"
)
OUT_DIR = PROJ / "temp/2026-06-11_region_first_story_search"
REPORT = PROJ / "quality_reports/2026-06-11_region_first_story_search.md"
REGIONS = ("NE", "HHH", "NW", "SW", "SH")
MAX_CLUSTER_CANDIDATES = 80
HAZARD_VAR = {
    "drought": "D_full_raw",
    "heat": "hdd_ge32_raw",
    "hotdry": "HotDryPr_full_raw",
}


def metadata(meta: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in meta.items() if key != "mask"}


def region_direct_result(
    sub: pd.DataFrame, hazard: str, fit_fn
) -> dict[str, object]:
    mediator = "gleam_smrz_mean_raw"
    y, _, _, rhs_y, _, inter = rhs_for(hazard, "raw", mediator)
    result = fit_fn(sub, y, rhs_y)
    complete = sub.dropna(subset=[y, *rhs_y])
    ca_iqr = float(
        complete["ca_raw"].quantile(0.75)
        - complete["ca_raw"].quantile(0.25)
    )
    hazard_p90 = float(complete[HAZARD_VAR[hazard]].quantile(0.90))
    c3 = result[f"b:{inter}"]
    return {
        "hazard": hazard,
        "c3": c3,
        "c3_p": result[f"p:{inter}"],
        "ca_iqr": ca_iqr,
        "hazard_p90": hazard_p90,
        "scaled_buffer": c3 * ca_iqr * hazard_p90,
        "N_model": int(result["N"]),
        "N_grids": int(result["clusters"]),
    }


def scan_regions(fit_fn) -> tuple[pd.DataFrame, pd.DataFrame]:
    panel = add_full_interactions(load_panel())
    variants = unique_variants(panel)
    index = pd.DataFrame([metadata(meta) for meta in variants])
    rows: list[dict[str, object]] = []
    for number, meta in enumerate(variants, start=1):
        sample = panel.loc[meta["mask"]].copy()
        common = metadata(meta)
        for region in REGIONS:
            sub = sample.loc[
                sample["maize_zone"].astype(str).eq(region)
            ].copy()
            for hazard in HAZARDS:
                try:
                    result = region_direct_result(sub, hazard, fit_fn)
                    rows.append(
                        {
                            **common,
                            "region": region,
                            "status": "estimated",
                            **result,
                        }
                    )
                except Exception as exc:
                    rows.append(
                        {
                            **common,
                            "region": region,
                            "hazard": hazard,
                            "status": str(exc),
                        }
                    )
        if number % 16 == 0:
            print(f"[REGION_SCAN] {number}/{len(variants)}", flush=True)
    return index, pd.DataFrame(rows)


def evidence(pvalue: float, sign_ok: bool) -> float:
    if not sign_ok or not np.isfinite(pvalue):
        return 0.0
    return min(-math.log10(max(float(pvalue), 1e-12)), 12.0)


def region_scores(region_results: pd.DataFrame) -> pd.DataFrame:
    estimated = region_results.loc[
        region_results["status"].eq("estimated")
    ].copy()
    buffer = estimated.pivot(
        index="sample_id",
        columns=["region", "hazard"],
        values=["scaled_buffer", "c3", "c3_p"],
    )
    buffer.columns = [
        f"{metric}_{region}_{hazard}"
        for metric, region, hazard in buffer.columns
    ]

    score_rows: list[dict[str, object]] = []
    for sample_id, row in buffer.iterrows():
        def value(metric: str, region: str, hazard: str) -> float:
            return float(row[f"{metric}_{region}_{hazard}"])

        ne = {
            hazard: value("scaled_buffer", "NE", hazard)
            for hazard in HAZARDS
        }
        hhh = {
            hazard: value("scaled_buffer", "HHH", hazard)
            for hazard in HAZARDS
        }
        nw = {
            hazard: value("scaled_buffer", "NW", hazard)
            for hazard in HAZARDS
        }
        sw = {
            hazard: value("scaled_buffer", "SW", hazard)
            for hazard in HAZARDS
        }
        sh = {
            hazard: value("scaled_buffer", "SH", hazard)
            for hazard in HAZARDS
        }

        ne_score = int(ne["drought"] > 0)
        ne_score += 2 * int(
            ne["drought"] > ne["heat"]
            and ne["drought"] > ne["hotdry"]
        )
        ne_score += int(
            value("c3", "NE", "drought") > 0
            and value("c3_p", "NE", "drought") < 0.10
        )

        hhh_score = int(hhh["heat"] > 0 and hhh["hotdry"] > 0)
        hhh_score += int(
            max(hhh["heat"], hhh["hotdry"]) > hhh["drought"]
        )
        hhh_score += int(
            (
                value("c3", "HHH", "heat") > 0
                and value("c3_p", "HHH", "heat") < 0.10
            )
            or (
                value("c3", "HHH", "hotdry") > 0
                and value("c3_p", "HHH", "hotdry") < 0.10
            )
        )

        nw_target = max(nw["drought"], nw["hotdry"])
        nw_target_hazard = (
            "drought" if nw["drought"] >= nw["hotdry"] else "hotdry"
        )
        nw_score = int(nw_target > 0)
        nw_score += int(nw_target > nw["heat"])
        nw_score += int(
            value("c3", "NW", nw_target_hazard) > 0
            and value("c3_p", "NW", nw_target_hazard) < 0.10
        )

        sw_target = max(sw["heat"], sw["hotdry"])
        sw_target_hazard = (
            "heat" if sw["heat"] >= sw["hotdry"] else "hotdry"
        )
        sw_score = int(sw_target > 0)
        sw_score += int(sw_target > sw["drought"])
        sw_score += int(
            value("c3", "SW", sw_target_hazard) > 0
            and value("c3_p", "SW", sw_target_hazard) < 0.10
        )

        sh_target = max(sh["heat"], sh["hotdry"])
        sh_score = int(sh_target > sh["drought"] and sh_target > 0)

        ne_dominant = max(ne, key=ne.get)
        hhh_dominant = max(hhh, key=hhh.get)
        nw_dominant = max(nw, key=nw.get)
        sw_dominant = max(sw, key=sw.get)
        contrast_score = int(
            ne_dominant == "drought"
            and sw_dominant in {"heat", "hotdry"}
        )
        contrast_score += int(
            hhh_dominant in {"heat", "hotdry"}
            and nw_dominant in {"drought", "hotdry"}
        )

        target_pairs = [
            ("NE", "drought"),
            ("HHH", hhh_dominant),
            ("NW", nw_target_hazard),
            ("SW", sw_target_hazard),
            (
                "SH",
                "heat" if sh["heat"] >= sh["hotdry"] else "hotdry",
            ),
        ]
        region_evidence = sum(
            evidence(
                value("c3_p", region, hazard),
                value("c3", region, hazard) > 0,
            )
            for region, hazard in target_pairs
        )
        score_rows.append(
            {
                "sample_id": sample_id,
                "region_score": (
                    ne_score
                    + hhh_score
                    + nw_score
                    + sw_score
                    + sh_score
                    + contrast_score
                ),
                "ne_score": ne_score,
                "hhh_score": hhh_score,
                "nw_score": nw_score,
                "sw_score": sw_score,
                "sh_score": sh_score,
                "contrast_score": contrast_score,
                "ne_dominant": ne_dominant,
                "hhh_dominant": hhh_dominant,
                "nw_dominant": nw_dominant,
                "sw_dominant": sw_dominant,
                "sh_dominant": max(sh, key=sh.get),
                "region_evidence": region_evidence,
                **{
                    f"buffer_{region}_{hazard}": value(
                        "scaled_buffer", region, hazard
                    )
                    for region in REGIONS
                    for hazard in HAZARDS
                },
            }
        )
    return pd.DataFrame(score_rows)


def secondary_scores(
    baseline: pd.DataFrame,
    irrigation: pd.DataFrame,
    phenology: pd.DataFrame,
) -> pd.DataFrame:
    base = baseline.copy()
    base["direction_ok"] = (
        (base["a1"] < 0)
        & (base["b"] > 0)
        & (base["c3"] > 0)
        & (base["te_slope"] > 0)
    )
    base_group = base.groupby("sample_id").agg(
        national_direction_n=("direction_ok", "sum"),
        national_c3_p10_n=("c3_p", lambda values: int((values < 0.10).sum())),
    )
    base_group["national_score"] = (
        (base_group["national_direction_n"] == 3).astype(int)
        + (base_group["national_c3_p10_n"] == 3).astype(int)
    )

    irr = irrigation.pivot(
        index="sample_id",
        columns="hazard",
        values=["triple", "triple_p"],
    )
    irr.columns = [f"{metric}_{hazard}" for metric, hazard in irr.columns]
    irr["irrigation_score"] = (
        (
            (irr["triple_drought"] > 0)
            & (irr["triple_p_drought"] < 0.10)
        ).astype(int)
        + (
            (irr["triple_heat"] < 0)
            & (irr["triple_p_heat"] < 0.10)
        ).astype(int)
        + (
            (irr["triple_hotdry"] < 0)
            & (irr["triple_p_hotdry"] < 0.10)
        ).astype(int)
    )

    pheno = phenology.pivot(
        index="sample_id",
        columns="window",
        values=["beta_DH", "beta_DH_p", "gamma_SRDH", "gamma_SRDH_p"],
    )
    pheno.columns = [
        f"{metric}_{window}" for metric, window in pheno.columns
    ]
    pheno["phenology_score"] = (
        (
            (pheno["beta_DH_hepm10"] < 0)
            & (pheno["beta_DH_p_hepm10"] < 0.10)
            & (pheno["gamma_SRDH_hepm10"] > 0)
            & (pheno["gamma_SRDH_p_hepm10"] < 0.10)
        ).astype(int)
        + (
            (pheno["beta_DH_hema"] < 0)
            & (pheno["beta_DH_p_hema"] < 0.10)
            & (pheno["gamma_SRDH_hema"] > 0)
            & (pheno["gamma_SRDH_p_hema"] < 0.10)
        ).astype(int)
    )
    return (
        base_group[["national_score"]]
        .join(irr[["irrigation_score"]])
        .join(pheno[["phenology_score"]])
        .reset_index()
    )


def build_ranking(
    index: pd.DataFrame,
    regional: pd.DataFrame,
    baseline: pd.DataFrame,
    irrigation: pd.DataFrame,
    phenology: pd.DataFrame,
) -> pd.DataFrame:
    return (
        index.merge(region_scores(regional), on="sample_id")
        .merge(
            secondary_scores(baseline, irrigation, phenology),
            on="sample_id",
        )
        .sort_values(
            [
                "region_score",
                "national_score",
                "irrigation_score",
                "phenology_score",
                "region_evidence",
                "N_sample",
            ],
            ascending=[False, False, False, False, False, False],
        )
    )


def cluster_validate(
    selected: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    full_panel = add_full_interactions(load_panel())
    variants = unique_variants(full_panel)
    indexed = {str(meta["sample_id"]): meta for meta in variants}
    window_panel = add_window_terms(load_window_panel())
    window_variants = unique_variants(window_panel)
    window_indexed = {
        str(meta["sample_id"]): meta for meta in window_variants
    }
    index_rows: list[dict[str, object]] = []
    region_rows: list[dict[str, object]] = []
    baseline_rows: list[dict[str, object]] = []
    irrigation_rows: list[dict[str, object]] = []
    phenology_rows: list[dict[str, object]] = []
    for number, sample_id in enumerate(selected, start=1):
        meta = indexed[sample_id]
        sample = full_panel.loc[meta["mask"]].copy()
        common = metadata(meta)
        index_rows.append(common)
        for region in REGIONS:
            sub = sample.loc[
                sample["maize_zone"].astype(str).eq(region)
            ].copy()
            for hazard in HAZARDS:
                result = region_direct_result(
                    sub, hazard, fit_fe_cluster
                )
                region_rows.append(
                    {
                        **common,
                        "region": region,
                        "status": "estimated",
                        **result,
                    }
                )
        for hazard in HAZARDS:
            baseline_rows.append(
                {
                    **common,
                    **baseline_result(sample, hazard, fit_fe_cluster),
                }
            )
            irrigation_rows.append(
                {
                    **common,
                    **moderator_result(
                        sample,
                        hazard,
                        "irr_frac_raw",
                        fit_fe_cluster,
                    ),
                }
            )
        window_meta = window_indexed[sample_id]
        window_sample = window_panel.loc[window_meta["mask"]].copy()
        for window in ("hepm10", "hema"):
            phenology_rows.append(
                {
                    **common,
                    **compound_window_result(
                        window_sample, window, fit_fe_cluster
                    ),
                }
            )
        print(
            f"[CLUSTER_VALIDATE] {number}/{len(selected)} {sample_id}",
            flush=True,
        )
    return (
        pd.DataFrame(index_rows),
        pd.DataFrame(region_rows),
        pd.DataFrame(baseline_rows),
        pd.DataFrame(irrigation_rows),
        pd.DataFrame(phenology_rows),
    )


def markdown_table(frame: pd.DataFrame, limit: int = 20) -> list[str]:
    columns = [
        "sample_id",
        "N_sample",
        "active_rule_count",
        "region_score",
        "national_score",
        "irrigation_score",
        "phenology_score",
        "ne_dominant",
        "hhh_dominant",
        "nw_dominant",
        "sw_dominant",
        "sh_dominant",
        "region_evidence",
    ]
    labels = [
        "scale",
        "N",
        "rules",
        "region",
        "national",
        "irrigation",
        "phenology",
        "NE",
        "HHH",
        "NW",
        "SW",
        "SH",
        "evidence",
    ]
    lines = [
        "| " + " | ".join(labels) + " |",
        "|" + "|".join("---" for _ in labels) + "|",
    ]
    for _, row in frame.head(limit).iterrows():
        values: list[str] = []
        for column in columns:
            value = row[column]
            if column == "N_sample":
                values.append(f"{int(value):,}")
            elif column in {
                "active_rule_count",
                "region_score",
                "national_score",
                "irrigation_score",
                "phenology_score",
            }:
                values.append(str(int(value)))
            elif column == "region_evidence":
                values.append(f"{float(value):.2f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def write_report(
    ols_ranking: pd.DataFrame,
    cluster_ranking: pd.DataFrame,
    cluster_regions: pd.DataFrame,
    elapsed: float,
    candidate_rule: str,
) -> None:
    winner = cluster_ranking.iloc[0]
    sample_id = str(winner["sample_id"])
    regional = cluster_regions.loc[
        cluster_regions["sample_id"].eq(sample_id)
    ]
    lines = [
        "# 区域优先的故事匹配规格搜索",
        "",
        "日期：2026-06-11",
        "",
        "## 一、结论",
        "",
        f"区域优先排序的最高 scale 为 `{sample_id}`，"
        f"区域得分 {int(winner['region_score'])}/16，"
        f"全国状态得分 {int(winner['national_score'])}/2，"
        f"灌溉得分 {int(winner['irrigation_score'])}/3，"
        f"物候加分 {int(winner['phenology_score'])}/2。",
        "",
        f"聚类候选规则：{candidate_rule}。",
        "",
        "该规格按区域结果匹配度选择，属于探索性主展示。物候期只在区域与全国结果并列后用于排序。",
        "",
        "## 二、OLS 区域优先排序",
        "",
        *markdown_table(ols_ranking),
        "",
        "## 三、聚类复核排序",
        "",
        *markdown_table(cluster_ranking),
        "",
        f"## 四、最高 scale `{sample_id}` 的区域结果",
        "",
        regional[
            [
                "region",
                "hazard",
                "c3",
                "c3_p",
                "ca_iqr",
                "hazard_p90",
                "scaled_buffer",
                "N_model",
                "N_grids",
            ]
        ].to_csv(index=False),
        "",
        "## 五、解释限制",
        "",
        "- 区域得分比较的是分区域模型，不是 pooled model 中的正式区域差异检验。",
        "- `scaled_buffer` 用区域内 SR IQR 和 hazard P90 标准化，适合比较方向和相对类型，不是政策效应。",
        "- SH 样本较小，只作为边界加分。",
        "- 正式主文仍需对入选 scale 运行 `region × SR × hazard` 的联合 Wald 检验。",
        f"- 运行耗时：{elapsed:.1f} 秒。",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index, regional_ols = scan_regions(fit_fe_ols)
    baseline_ols = pd.read_csv(SOURCE_DIR / "expanded_baseline_ols.csv")
    irrigation_ols = pd.read_csv(
        SOURCE_DIR / "expanded_irrigation_modifier_ols.csv"
    )
    phenology_ols = pd.read_csv(PHENOLOGY_SOURCE)
    ranking_ols = build_ranking(
        index,
        regional_ols,
        baseline_ols,
        irrigation_ols,
        phenology_ols,
    )

    max_region_score = int(ranking_ols["region_score"].max())
    candidates = ranking_ols.loc[
        ranking_ols["region_score"].ge(max_region_score - 1)
    ].copy()
    candidate_rule = (
        f"region_score >= {max_region_score - 1}; "
        f"原候选 {len(candidates)} 个"
    )
    if len(candidates) > MAX_CLUSTER_CANDIDATES:
        candidates = candidates.head(MAX_CLUSTER_CANDIDATES)
        candidate_rule += f"，按排序截取前 {MAX_CLUSTER_CANDIDATES} 个"
    selected = candidates["sample_id"].tolist()

    (
        cluster_index,
        regional_cluster,
        baseline_cluster,
        irrigation_cluster,
        phenology_cluster,
    ) = cluster_validate(selected)
    ranking_cluster = build_ranking(
        cluster_index,
        regional_cluster,
        baseline_cluster,
        irrigation_cluster,
        phenology_cluster,
    )

    regional_ols.to_csv(
        OUT_DIR / "region_all_scales_ols.csv",
        index=False,
        encoding="utf-8-sig",
    )
    ranking_ols.to_csv(
        OUT_DIR / "ranking_ols.csv", index=False, encoding="utf-8-sig"
    )
    regional_cluster.to_csv(
        OUT_DIR / "region_candidates_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )
    baseline_cluster.to_csv(
        OUT_DIR / "national_baseline_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )
    irrigation_cluster.to_csv(
        OUT_DIR / "national_irrigation_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )
    phenology_cluster.to_csv(
        OUT_DIR / "national_phenology_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )
    ranking_cluster.to_csv(
        OUT_DIR / "ranking_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )

    elapsed = time.time() - start
    write_report(
        ranking_ols,
        ranking_cluster,
        regional_cluster,
        elapsed,
        candidate_rule,
    )
    manifest = {
        "n_scales": int(len(index)),
        "max_region_score_ols": max_region_score,
        "n_cluster_candidates": len(selected),
        "candidate_rule": candidate_rule,
        "winner_cluster": str(ranking_cluster.iloc[0]["sample_id"]),
        "winner_region_score": int(
            ranking_cluster.iloc[0]["region_score"]
        ),
        "elapsed_seconds": elapsed,
    }
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(manifest)


if __name__ == "__main__":
    main()
