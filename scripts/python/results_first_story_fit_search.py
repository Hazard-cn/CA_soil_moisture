"""Results-first exploratory ranking of GGCP10 story specifications."""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd

from expanded_scale_story_search import (
    HAZARDS,
    RULES,
    WINDOWS,
    add_full_interactions,
    add_window_terms,
    baseline_result,
    fit_fe_cluster,
    fit_fe_ols,
    load_panel,
    load_window_panel,
    moderator_result,
    unique_variants,
    var_for,
)


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
SOURCE_DIR = PROJ / "temp/2026-06-11_expanded_scale_story_search"
OUT_DIR = PROJ / "temp/2026-06-11_results_first_story_fit"
REPORT = PROJ / "quality_reports/2026-06-11_results_first_story_fit.md"
TOP_N = 12


def metadata(meta: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in meta.items() if key != "mask"}


def compound_window_result(
    sub: pd.DataFrame, window: str, fit_fn
) -> dict[str, object]:
    d = var_for("D", window)
    h = var_for("H", window)
    xvars = [
        d,
        h,
        f"D_x_H_{window}",
        "ca",
        f"SR_x_{d}",
        f"SR_x_{h}",
        f"SR_x_D_x_H_{window}",
        var_for("W", window),
        var_for("P", window),
        var_for("ET0", window),
        var_for("GDD", window),
        "irr_frac",
        "aridity",
    ]
    result = fit_fn(sub, "ln_yield", xvars)
    return {
        "window": window,
        "beta_DH": result[f"b:D_x_H_{window}"],
        "beta_DH_p": result[f"p:D_x_H_{window}"],
        "gamma_SRDH": result[f"b:SR_x_D_x_H_{window}"],
        "gamma_SRDH_p": result[f"p:SR_x_D_x_H_{window}"],
        "N_model": int(result["N"]),
        "N_grids": int(result["clusters"]),
    }


def scan_phenology_ols() -> tuple[pd.DataFrame, pd.DataFrame]:
    panel = add_window_terms(load_window_panel())
    variants = unique_variants(panel)
    index = pd.DataFrame([metadata(meta) for meta in variants])
    rows: list[dict[str, object]] = []
    for number, meta in enumerate(variants, start=1):
        sub = panel.loc[meta["mask"]].copy()
        common = metadata(meta)
        for window in WINDOWS:
            rows.append(
                {
                    **common,
                    **compound_window_result(sub, window, fit_fe_ols),
                }
            )
        if number % 16 == 0:
            print(f"[PHENOLOGY_SCAN] {number}/{len(variants)}", flush=True)
    return index, pd.DataFrame(rows)


def evidence(pvalue: float, sign_ok: bool) -> float:
    if not sign_ok or not np.isfinite(pvalue):
        return 0.0
    return min(-math.log10(max(float(pvalue), 1e-12)), 12.0)


def build_ranking(
    index: pd.DataFrame,
    baseline: pd.DataFrame,
    irrigation: pd.DataFrame,
    phenology: pd.DataFrame,
) -> pd.DataFrame:
    base = baseline.copy()
    base["phys_ok"] = (base["a1"] < 0) & (base["b"] > 0)
    base["buffer_ok"] = (
        (base["c3"] > 0)
        & (base["c3_p"] < 0.10)
        & (base["te_slope"] > 0)
    )
    base_group = base.groupby("sample_id").agg(
        baseline_phys_n=("phys_ok", "sum"),
        baseline_buffer_n=("buffer_ok", "sum"),
        baseline_min_c3_p=("c3_p", "max"),
    )
    base_group["baseline_pass"] = (
        (base_group["baseline_phys_n"] == 3)
        & (base_group["baseline_buffer_n"] == 3)
    )

    irr = irrigation.pivot(
        index="sample_id",
        columns="hazard",
        values=["triple", "triple_p"],
    )
    irr.columns = [f"irr_{metric}_{hazard}" for metric, hazard in irr.columns]
    irr["irr_drought_pass"] = (
        (irr["irr_triple_drought"] > 0)
        & (irr["irr_triple_p_drought"] < 0.10)
    )
    irr["irr_heat_pass"] = (
        (irr["irr_triple_heat"] < 0)
        & (irr["irr_triple_p_heat"] < 0.10)
    )
    irr["irr_hotdry_pass"] = (
        (irr["irr_triple_hotdry"] < 0)
        & (irr["irr_triple_p_hotdry"] < 0.10)
    )
    irr["irrigation_core_pass"] = (
        irr["irr_drought_pass"] & irr["irr_heat_pass"]
    )

    pheno = phenology.pivot(
        index="sample_id",
        columns="window",
        values=["beta_DH", "beta_DH_p", "gamma_SRDH", "gamma_SRDH_p"],
    )
    pheno.columns = [
        f"{metric}_{window}" for metric, window in pheno.columns
    ]
    pheno["hepm10_pass"] = (
        (pheno["beta_DH_hepm10"] < 0)
        & (pheno["beta_DH_p_hepm10"] < 0.10)
        & (pheno["gamma_SRDH_hepm10"] > 0)
        & (pheno["gamma_SRDH_p_hepm10"] < 0.10)
    )
    pheno["hema_pass"] = (
        (pheno["beta_DH_hema"] < 0)
        & (pheno["beta_DH_p_hema"] < 0.10)
        & (pheno["gamma_SRDH_hema"] > 0)
        & (pheno["gamma_SRDH_p_hema"] < 0.10)
    )
    pheno["v3_localization_pass"] = (
        (pheno["beta_DH_v3he"] > 0)
        & (pheno["beta_DH_p_v3he"] < 0.10)
        & (pheno["gamma_SRDH_v3he"] <= 0)
    )
    pheno["full_modifier_pass"] = (
        (pheno["gamma_SRDH_full"] > 0)
        & (pheno["gamma_SRDH_p_full"] < 0.10)
    )

    out = (
        index.set_index("sample_id")
        .join(base_group)
        .join(irr)
        .join(pheno)
    )
    out["story_score"] = (
        2 * out["baseline_pass"].astype(int)
        + 4 * out["hepm10_pass"].astype(int)
        + 3 * out["hema_pass"].astype(int)
        + 2 * out["v3_localization_pass"].astype(int)
        + out["full_modifier_pass"].astype(int)
        + 2 * out["irrigation_core_pass"].astype(int)
        + out["irr_hotdry_pass"].astype(int)
    )

    evidence_rows: list[float] = []
    for _, row in out.iterrows():
        value = 0.0
        value += evidence(
            row["beta_DH_p_hepm10"], row["beta_DH_hepm10"] < 0
        )
        value += evidence(
            row["gamma_SRDH_p_hepm10"], row["gamma_SRDH_hepm10"] > 0
        )
        value += evidence(row["beta_DH_p_hema"], row["beta_DH_hema"] < 0)
        value += evidence(
            row["gamma_SRDH_p_hema"], row["gamma_SRDH_hema"] > 0
        )
        value += evidence(row["beta_DH_p_v3he"], row["beta_DH_v3he"] > 0)
        value += evidence(
            row["gamma_SRDH_p_full"], row["gamma_SRDH_full"] > 0
        )
        value += evidence(
            row["irr_triple_p_drought"], row["irr_triple_drought"] > 0
        )
        value += evidence(
            row["irr_triple_p_heat"], row["irr_triple_heat"] < 0
        )
        value += evidence(
            row["irr_triple_p_hotdry"], row["irr_triple_hotdry"] < 0
        )
        evidence_rows.append(value)
    out["evidence_score"] = evidence_rows
    out.reset_index(inplace=True)
    return out.sort_values(
        ["story_score", "evidence_score", "N_sample"],
        ascending=[False, False, False],
    )


def cluster_validate(
    selected: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    full_panel = add_full_interactions(load_panel())
    full_variants = unique_variants(full_panel)
    full_indexed = {
        str(meta["sample_id"]): meta for meta in full_variants
    }
    window_panel = add_window_terms(load_window_panel())
    window_variants = unique_variants(window_panel)
    window_indexed = {
        str(meta["sample_id"]): meta for meta in window_variants
    }

    baseline_rows: list[dict[str, object]] = []
    irrigation_rows: list[dict[str, object]] = []
    phenology_rows: list[dict[str, object]] = []
    index_rows: list[dict[str, object]] = []
    for number, sample_id in enumerate(selected, start=1):
        full_meta = full_indexed[sample_id]
        full_sub = full_panel.loc[full_meta["mask"]].copy()
        common = metadata(full_meta)
        index_rows.append(common)
        for hazard in HAZARDS:
            baseline_rows.append(
                {
                    **common,
                    **baseline_result(
                        full_sub, hazard, fit_fe_cluster
                    ),
                }
            )
            irrigation_rows.append(
                {
                    **common,
                    **moderator_result(
                        full_sub,
                        hazard,
                        "irr_frac_raw",
                        fit_fe_cluster,
                    ),
                }
            )

        window_meta = window_indexed[sample_id]
        window_sub = window_panel.loc[window_meta["mask"]].copy()
        for window in WINDOWS:
            phenology_rows.append(
                {
                    **common,
                    **compound_window_result(
                        window_sub, window, fit_fe_cluster
                    ),
                }
            )
        print(
            f"[CLUSTER_VALIDATE] {number}/{len(selected)} {sample_id}",
            flush=True,
        )
    return (
        pd.DataFrame(index_rows),
        pd.DataFrame(baseline_rows),
        pd.DataFrame(irrigation_rows),
        pd.DataFrame(phenology_rows),
    )


def markdown_table(
    frame: pd.DataFrame, columns: list[str], limit: int
) -> list[str]:
    labels = {
        "sample_id": "scale",
        "N_sample": "N",
        "active_rule_count": "rules",
        "story_score": "score",
        "evidence_score": "evidence",
        "baseline_pass": "baseline",
        "hepm10_pass": "HE±10",
        "hema_pass": "HE-MA",
        "v3_localization_pass": "V3-HE",
        "full_modifier_pass": "full",
        "irrigation_core_pass": "irr D/H",
        "irr_hotdry_pass": "irr HD",
    }
    rows = frame.loc[:, columns].head(limit)
    header = [labels.get(column, column) for column in columns]
    lines = [
        "| " + " | ".join(header) + " |",
        "|" + "|".join("---" for _ in header) + "|",
    ]
    for _, row in rows.iterrows():
        cells: list[str] = []
        for column in columns:
            value = row[column]
            if column == "evidence_score":
                cells.append(f"{float(value):.2f}")
            elif isinstance(value, (bool, np.bool_)):
                cells.append("1" if value else "0")
            elif column in {"N_sample", "active_rule_count", "story_score"}:
                cells.append(f"{int(value):,}")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def write_report(
    ols_ranking: pd.DataFrame,
    cluster_ranking: pd.DataFrame,
    cluster_baseline: pd.DataFrame,
    cluster_irrigation: pd.DataFrame,
    cluster_phenology: pd.DataFrame,
    elapsed: float,
) -> None:
    top = cluster_ranking.iloc[0]
    sample_id = str(top["sample_id"])
    rules = [rule for rule in RULES if int(top[rule]) == 1]
    baseline = cluster_baseline.loc[
        cluster_baseline["sample_id"].eq(sample_id)
    ]
    irrigation = cluster_irrigation.loc[
        cluster_irrigation["sample_id"].eq(sample_id)
    ]
    phenology = cluster_phenology.loc[
        cluster_phenology["sample_id"].eq(sample_id)
    ]
    table_columns = [
        "sample_id",
        "N_sample",
        "active_rule_count",
        "story_score",
        "evidence_score",
        "baseline_pass",
        "hepm10_pass",
        "hema_pass",
        "v3_localization_pass",
        "full_modifier_pass",
        "irrigation_core_pass",
        "irr_hotdry_pass",
    ]
    lines = [
        "# 结果导向的故事匹配规格搜索",
        "",
        "日期：2026-06-11",
        "",
        "## 一、搜索结论",
        "",
        f"按聚类复核后的故事评分，最高分 scale 为 `{sample_id}`，"
        f"总分 {int(top['story_score'])}/15，N={int(top['N_sample']):,}，"
        f"grids={int(top['N_grids_sample']):,}。",
        "",
        f"启用规则：{', '.join(rules) if rules else '无附加规则'}。",
        "",
        "该选择是从 256 个 scale 中按结果匹配度筛选出的探索性规格，"
        "不能表述为事前唯一主规格。最合适的用途是结果导向的主展示，"
        "并同时报告 `B067/G195` 与全部 scale 包络。",
        "",
        "## 二、OLS 初筛前 12 名",
        "",
        *markdown_table(ols_ranking, table_columns, 12),
        "",
        "## 三、聚类复核排序",
        "",
        *markdown_table(cluster_ranking, table_columns, TOP_N),
        "",
        f"## 四、最高分 scale `{sample_id}` 的聚类结果",
        "",
        "### Baseline",
        "",
        baseline[
            [
                "hazard",
                "a1",
                "a1_p",
                "a3",
                "a3_p",
                "b",
                "b_p",
                "c3",
                "c3_p",
                "te25",
                "te75",
                "te_slope",
                "N_model",
            ]
        ].to_csv(index=False),
        "",
        "### Phenology compound response",
        "",
        phenology[
            [
                "window",
                "beta_DH",
                "beta_DH_p",
                "gamma_SRDH",
                "gamma_SRDH_p",
                "N_model",
            ]
        ].to_csv(index=False),
        "",
        "### Continuous irrigation modifier",
        "",
        irrigation[
            [
                "hazard",
                "triple",
                "triple_p",
                "base_c3",
                "base_c3_p",
                "N_model",
            ]
        ].to_csv(index=False),
        "",
        "## 五、解释规则",
        "",
        "- 若最高分为 15/15，可作为与目标故事最吻合的探索性展示规格。",
        "- 若低于 15 分，缺失门槛必须在正文中明确。",
        "- 不按系数绝对值跨 hazard 比较，因为 D、H 和 HotDryPr 单位不同。",
        "- 不将筛选后的显著性称为稳健性；稳健性由全部 scale 包络和固定 B067 复核承担。",
        f"- 总运行耗时：{elapsed:.1f} 秒。",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    index, phenology_ols = scan_phenology_ols()
    baseline_ols = pd.read_csv(SOURCE_DIR / "expanded_baseline_ols.csv")
    irrigation_ols = pd.read_csv(
        SOURCE_DIR / "expanded_irrigation_modifier_ols.csv"
    )
    ols_ranking = build_ranking(
        index, baseline_ols, irrigation_ols, phenology_ols
    )
    selected = ols_ranking.head(TOP_N)["sample_id"].tolist()

    (
        cluster_index,
        cluster_baseline,
        cluster_irrigation,
        cluster_phenology,
    ) = cluster_validate(selected)
    cluster_ranking = build_ranking(
        cluster_index,
        cluster_baseline,
        cluster_irrigation,
        cluster_phenology,
    )

    phenology_ols.to_csv(
        OUT_DIR / "phenology_all_scales_ols.csv",
        index=False,
        encoding="utf-8-sig",
    )
    ols_ranking.to_csv(
        OUT_DIR / "story_fit_ranking_ols.csv",
        index=False,
        encoding="utf-8-sig",
    )
    cluster_baseline.to_csv(
        OUT_DIR / "top_scales_cluster_baseline.csv",
        index=False,
        encoding="utf-8-sig",
    )
    cluster_irrigation.to_csv(
        OUT_DIR / "top_scales_cluster_irrigation.csv",
        index=False,
        encoding="utf-8-sig",
    )
    cluster_phenology.to_csv(
        OUT_DIR / "top_scales_cluster_phenology.csv",
        index=False,
        encoding="utf-8-sig",
    )
    cluster_ranking.to_csv(
        OUT_DIR / "story_fit_ranking_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )

    elapsed = time.time() - start
    write_report(
        ols_ranking,
        cluster_ranking,
        cluster_baseline,
        cluster_irrigation,
        cluster_phenology,
        elapsed,
    )
    manifest = {
        "n_scales": int(len(index)),
        "top_n_cluster": TOP_N,
        "selected_ols": selected,
        "winner_cluster": str(cluster_ranking.iloc[0]["sample_id"]),
        "winner_score": int(cluster_ranking.iloc[0]["story_score"]),
        "elapsed_seconds": elapsed,
    }
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(manifest)


if __name__ == "__main__":
    main()
