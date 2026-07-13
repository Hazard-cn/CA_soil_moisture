"""Summarize story-line fit, empirical vulnerabilities, and scale matches.

This script is read-only with respect to existing empirical outputs. It builds
one compact CSV and one Markdown report from already generated Zotero and
regression result artifacts.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
OUT_DIR = PROJ / "temp/2026-06-18_story_empirical_review_match"
REPORT = PROJ / "quality_reports/2026-06-18_story_empirical_review_match.md"

ZOTERO_DIR = PROJ / "temp/2026-06-18_zotero_story_direction"
REGION_DIR = PROJ / "temp/2026-06-11_region_first_story_search"
EXPANDED_DIR = PROJ / "temp/2026-06-11_expanded_scale_story_search"
F4_DIR = PROJ / "output/figures/f4_b067_v2"
F4_BOOT_DIR = PROJ / "temp/2026-06-04_f4_b067_full_bootstrap_counterfactual"


@dataclass(frozen=True)
class Story:
    story_id: str
    title: str
    conclusion: str
    primary_scale: str
    evidence: str
    gaps: str
    use_as: str
    risk: str


def pct(x: float | int | None) -> str:
    if x is None or not math.isfinite(float(x)):
        return ""
    return f"{100 * float(x):.2f}%"


def sig(pvalue: float | int | None, alpha: float = 0.10) -> str:
    if pvalue is None or not math.isfinite(float(pvalue)):
        return "n/a"
    return "yes" if float(pvalue) < alpha else "no"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def zotero_theme_summary() -> tuple[pd.DataFrame, dict[str, int]]:
    target = read_csv(ZOTERO_DIR / "target_journal_exact_dedup.csv")
    counts: dict[str, int] = {}
    for themes in target["themes"].fillna(""):
        for theme in str(themes).split(";"):
            theme = theme.strip()
            if theme:
                counts[theme] = counts.get(theme, 0) + 1
    return target, counts


def region_top() -> pd.DataFrame:
    ranking = read_csv(REGION_DIR / "all_highscore_ranking_cluster.csv")
    cols = [
        "sample_id",
        "N_sample",
        "N_grids_sample",
        "active_rule_count",
        "main_sample",
        "zone_core",
        "yield_domain",
        "yield_jump",
        "sm_sd",
        "sr_within",
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
    return ranking.loc[:, cols].head(15).copy()


def region_detail(scales: list[str]) -> pd.DataFrame:
    regional = read_csv(REGION_DIR / "all_highscore_region_cluster.csv")
    return regional.loc[regional["sample_id"].isin(scales)].copy()


def irrigation_detail(scales: list[str]) -> pd.DataFrame:
    irrigation = read_csv(REGION_DIR / "all_highscore_irrigation_cluster.csv")
    return irrigation.loc[irrigation["sample_id"].isin(scales)].copy()


def phenology_detail(scales: list[str]) -> pd.DataFrame:
    phenology = read_csv(REGION_DIR / "all_highscore_phenology_cluster.csv")
    return phenology.loc[phenology["sample_id"].isin(scales)].copy()


def representative_phenology() -> pd.DataFrame:
    return read_csv(EXPANDED_DIR / "representative_phenology_cluster.csv")


def representative_irrigation() -> pd.DataFrame:
    return read_csv(EXPANDED_DIR / "representative_irrigation_cluster.csv")


def b067_iede() -> pd.DataFrame:
    unified = read_csv(F4_BOOT_DIR / "f4_b067_mean_raw_unified_coefficients_effects.csv")
    mask = (
        unified["sample_id"].eq("B067")
        & unified["branch"].eq("mean")
        & unified["transform"].eq("raw")
        & unified["record_type"].eq("iede_effect")
        & unified["ca_level"].isin(["P25", "P50", "P75"])
    )
    return unified.loc[mask].copy()


def summarize_b067_te() -> pd.DataFrame:
    dat = b067_iede()
    base = dat.loc[
        dat["layer"].eq("baseline") & dat["effect"].eq("TE"),
        ["hazard", "ca_level", "estimate", "bs_ci_lo_95", "bs_ci_hi_95"],
    ].copy()
    return base.sort_values(["hazard", "ca_level"])


def summarize_irrigation_patterns(scale: str) -> pd.DataFrame:
    irr = irrigation_detail([scale])
    rows = []
    for _, row in irr.iterrows():
        hazard = row["hazard"]
        triple = float(row["triple"])
        p = float(row["triple_p"])
        expected = "positive" if hazard == "drought" else "negative"
        direction_ok = triple > 0 if expected == "positive" else triple < 0
        rows.append(
            {
                "scale": scale,
                "hazard": hazard,
                "triple": triple,
                "p": p,
                "expected_direction": expected,
                "direction_ok": int(direction_ok),
                "p_lt_010": int(p < 0.10),
            }
        )
    return pd.DataFrame(rows)


def summarize_representative_phenology() -> pd.DataFrame:
    ph = representative_phenology()
    rows = []
    for window, sub in ph.groupby("window"):
        rows.append(
            {
                "window": window,
                "n_scales": int(len(sub)),
                "dh_negative": int((sub["beta_DH"] < 0).sum()),
                "dh_negative_p10": int(((sub["beta_DH"] < 0) & (sub["beta_DH_p"] < 0.10)).sum()),
                "srdh_positive": int((sub["gamma_SRDH"] > 0).sum()),
                "srdh_positive_p10": int(((sub["gamma_SRDH"] > 0) & (sub["gamma_SRDH_p"] < 0.10)).sum()),
            }
        )
    return pd.DataFrame(rows).sort_values("window")


def literature_support(target: pd.DataFrame) -> pd.DataFrame:
    """Select representative Zotero target-journal items for each story."""

    mapping = {
        "S1": [
            "IUZH8WDN",  # climate change in agricultural regions
            "JJY74242",  # irrigation and heat sensitivity
            "PWYXU7WH",  # CA resilience under extremes
            "Q4MZYF9B",  # arid loess plateau
        ],
        "S2": [
            "28M3GU42",  # concurrent soil drought and atmospheric aridity
            "JJY74242",  # irrigation and heat sensitivity
            "K2HANYSG",  # CA after long-term warming
            "T79SQWVL",  # VPD and productivity
        ],
        "S3": [
            "JJY74242",  # irrigation and heat sensitivity
            "28M3GU42",  # soil drought and atmospheric aridity
            "Q4MZYF9B",  # conservation tillage in arid region
            "VHR2TSHM",  # deficit irrigation, residue mulch
        ],
        "S4": [
            "XKWMKJSA",  # productivity limits of CA
            "PWYXU7WH",  # resilience and yield stability
            "Q4MZYF9B",  # soil properties and yield in arid loess plateau
            "K2HANYSG",  # long-term warming
        ],
        "S5": [
            "PV443DJ6",  # residue and soil temperature
            "28M3GU42",  # soil drought and aridity coupling
            "T79SQWVL",  # VPD productivity
            "MVSLCSCJ",  # soil moisture observations
        ],
        "S6": [
            "XKWMKJSA",  # limits and context dependence
            "BJFIJVZ3",  # soil health vs persistent SOC boundary
            "PWYXU7WH",  # resilience in extremes
            "Q4MZYF9B",  # arid-region CA response
        ],
    }

    records = []
    indexed = target.drop_duplicates("item_key").set_index("item_key", drop=False)
    for story_id, keys in mapping.items():
        for order, key in enumerate(keys, start=1):
            if key not in indexed.index:
                records.append(
                    {
                        "story_id": story_id,
                        "rank": order,
                        "item_key": key,
                        "citation_key": "",
                        "year": "",
                        "title": "NOT_FOUND_IN_TARGET_EXPORT",
                        "publicationTitle": "",
                        "target_family": "",
                        "DOI": "",
                        "themes": "",
                    }
                )
                continue
            row = indexed.loc[key]
            records.append(
                {
                    "story_id": story_id,
                    "rank": order,
                    "item_key": key,
                    "citation_key": row.get("citation_key", ""),
                    "year": row.get("year", ""),
                    "title": row.get("title", ""),
                    "publicationTitle": row.get("publicationTitle", ""),
                    "target_family": row.get("target_family", ""),
                    "DOI": row.get("DOI", ""),
                    "themes": row.get("themes", ""),
                }
            )
    return pd.DataFrame.from_records(records)


def build_story_rows(theme_counts: dict[str, int]) -> list[Story]:
    return [
        Story(
            story_id="S1",
            title="区域定向的气候缓冲，而非全国平均增产",
            conclusion=(
                "秸秆还田应优先解释为区域主导约束下的气候风险缓冲技术；"
                "NE 更适合讲 drought buffering，HHH 更适合讲 heat/hotdry，"
                "SW/SH 更适合讲热或复合风险边界，NW 只能写方向性支持。"
            ),
            primary_scale="G057; G185 as main_sample alternative",
            evidence=(
                f"Zotero target themes: adaptation_region={theme_counts.get('adaptation_region', 0)}; "
                "G057/G185 region_score=15/16, region_evidence≈16.8; "
                "NE=drought, HHH=heat, NW=hotdry, SW=hotdry, SH=hotdry."
            ),
            gaps="需要把 G057 的探索性 region-first 选择与 B067/G195 的旧主框架区分；NW 不能写显著。",
            use_as="总主线",
            risk="medium",
        ),
        Story(
            story_id="S2",
            title="生育期定位的联合热旱响应",
            conclusion=(
                "SR 与较弱联合热旱损失之间的关联主要出现在 HE±10 和 HE-MA，"
                "不是全年均匀出现的复合胁迫保护。"
            ),
            primary_scale="G195/B067; G255 strict endpoint; representative G envelope",
            evidence=(
                f"Zotero target themes: compound_climate_risk={theme_counts.get('compound_climate_risk', 0)}; "
                "representative scales show HE±10 has 8/8 D×H<0 p<0.10 and 8/8 SR×D×H>0 p<0.10; "
                "B067 HE±10 D×H=-0.000362, SR×D×H=0.002390."
            ),
            gaps="需要补 β_DH+γ_SRDH×SR_q 的 cluster CI；full season 不能写严格联合损失。",
            use_as="第一支撑主线",
            risk="medium",
        ),
        Story(
            story_id="S3",
            title="灌溉重新配置 SR 的边际保护价值",
            conclusion=(
                "灌溉越充分，SR 的 heat buffering 边际空间越小；"
                "drought 方向上可能互补，但统计强度弱于 heat 替代证据。"
            ),
            primary_scale="G057/G185 for region-first; G195/B067 for old-frame comparability",
            evidence=(
                f"Zotero target themes: water_mediated_buffering={theme_counts.get('water_mediated_buffering', 0)}; "
                "G057 irrigation_score=3/3; B067/G195 continuous irrigation: heat triple<0 and p≈0.008."
            ),
            gaps="不能用高低组显著性差异替代连续 triple；三类 hazard 单位不同，必须换算为 P90 情景或标准化 margins。",
            use_as="第二支撑主线，若连续交互图完成",
            risk="high",
        ),
        Story(
            story_id="S4",
            title="单一胁迫下的状态依赖损失斜率",
            conclusion=(
                "更高 SR 与三类单一或复合指标下更平缓的产量损失斜率相关，"
                "但结论对象是 stress-response slope，不是无条件产量水平。"
            ),
            primary_scale="G195/B067 with F4 envelope; G057 as region-first alternative",
            evidence=(
                "B067 baseline TE moves toward zero from P25 to P75 for drought, heat, and hotdry; "
                "expanded scales show three-hazard positive TE slopes across all 256 scales."
            ),
            gaps="需要并列报告低胁迫/正常状态下的 SR marginal association，防止被理解成平均增产。",
            use_as="基础结果层",
            risk="low",
        ),
        Story(
            story_id="S5",
            title="不同胁迫对应不同 association decomposition",
            conclusion=(
                "drought 和 hotdry 更接近 SM-pathway-consistent buffering，"
                "heat 的 SR 调制主要不通过当前年度根区 SM 指标表现。"
            ),
            primary_scale="B067/G195",
            evidence=(
                "B067: drought a3>0 p<0.05, hotdry a3>0 p<0.01, heat a3 not significant; "
                "IE/DE/TE gradients differ by hazard."
            ),
            gaps="不能称为因果中介；需要 bootstrap difference for IE slope and DE slope across hazards。",
            use_as="机制解释和结果组织",
            risk="medium",
        ),
        Story(
            story_id="S6",
            title="定向采用规则：水分约束有管理弹性时优先采用",
            conclusion=(
                "SR 的优先采用条件不是越干越好，而是主导气候约束明确、损失斜率较陡，"
                "且水分状态或地表覆盖仍能被管理改变。"
            ),
            primary_scale="Synthesis across G057/G185, G195/B067, irrigation and phenology outputs",
            evidence=(
                f"Zotero target themes: boundary_or_tradeoff={theme_counts.get('boundary_or_tradeoff', 0)}; "
                "region, irrigation and phenology results all imply boundary conditions rather than universal benefit."
            ),
            gaps="属于政策含义，不是单一回归结论；需要明确 observational conditional association。",
            use_as="结论和 Discussion",
            risk="medium",
        ),
    ]


def markdown_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "_empty_"
    view = df.head(max_rows).copy()
    cols = list(view.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "|" + "|".join("---" for _ in cols) + "|",
    ]
    for _, row in view.iterrows():
        values = []
        for col in cols:
            val = row[col]
            if isinstance(val, float):
                if math.isfinite(val):
                    values.append(f"{val:.6g}")
                else:
                    values.append("")
            else:
                text = str(val)
                text = text.replace("\n", " ").replace("|", "/")
                values.append(text)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_outputs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    target, theme_counts = zotero_theme_summary()
    top = region_top()
    scales = ["G057", "G185", "G195", "G255", "G049", "G177"]
    reg = region_detail(scales)
    irr_g057 = summarize_irrigation_patterns("G057")
    irr_g185 = summarize_irrigation_patterns("G185")
    pheno_summary = summarize_representative_phenology()
    b067_te = summarize_b067_te()
    lit = literature_support(target)
    stories = build_story_rows(theme_counts)

    story_df = pd.DataFrame([s.__dict__ for s in stories])
    story_df.to_csv(OUT_DIR / "story_scale_match.csv", index=False, encoding="utf-8-sig")
    lit.to_csv(OUT_DIR / "story_literature_support.csv", index=False, encoding="utf-8-sig")
    top.to_csv(OUT_DIR / "region_first_top15.csv", index=False, encoding="utf-8-sig")
    reg.to_csv(OUT_DIR / "selected_region_details.csv", index=False, encoding="utf-8-sig")
    pd.concat([irr_g057, irr_g185], ignore_index=True).to_csv(
        OUT_DIR / "selected_irrigation_triples.csv", index=False, encoding="utf-8-sig"
    )
    pheno_summary.to_csv(OUT_DIR / "representative_phenology_summary.csv", index=False, encoding="utf-8-sig")
    b067_te.to_csv(OUT_DIR / "b067_baseline_te_by_sr.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# 故事线、实证漏洞审查与 scale 匹配",
        "",
        "日期：2026-06-18",
        "",
        "## 一、材料与入口",
        "",
        "本报告使用 `academic-research-suite` 的 pipeline 路由：Zotero 文献综合对应 deep-research，"
        "实证结构审查对应 academic-paper-reviewer，既有结果验证和 story-scale 匹配对应 experiment-agent validate。"
        "所有数值来自既有本地 CSV，本轮脚本不重估模型。",
        "",
        f"Zotero 精确目标刊物族去重条目：{len(target)}；"
        f"主题计数为 adaptation_region={theme_counts.get('adaptation_region', 0)}、"
        f"compound_climate_risk={theme_counts.get('compound_climate_risk', 0)}、"
        f"conservation_agriculture_sr={theme_counts.get('conservation_agriculture_sr', 0)}、"
        f"water_mediated_buffering={theme_counts.get('water_mediated_buffering', 0)}、"
        f"boundary_or_tradeoff={theme_counts.get('boundary_or_tradeoff', 0)}。",
        "",
        "## 二、可以讲的故事",
        "",
        markdown_table(story_df[["story_id", "title", "primary_scale", "use_as", "risk"]], 10),
        "",
        "推荐组合：`S1` 作为总主线，`S2` 和 `S3` 作为两条支撑主线；`S4` 放入基础结果层，`S5` 放入机制解释，`S6` 放入 Discussion 或 Conclusion 的采用条件。",
        "",
        markdown_table(story_df[["story_id", "conclusion", "evidence", "gaps"]], 10),
        "",
        "## 三、region-first scale 排名",
        "",
        markdown_table(top, 15),
        "",
        "## 四、故事线对应的 Zotero 文献支持",
        "",
        "当前 Zotero 导出中多数条目的 `citation_key` 为空，因此本表以 `item_key` 和 DOI 作为可追溯标识。",
        "",
        markdown_table(
            lit[
                [
                    "story_id",
                    "item_key",
                    "year",
                    "title",
                    "publicationTitle",
                    "target_family",
                    "DOI",
                    "themes",
                ]
            ],
            30,
        ),
        "",
        "## 五、G057/G185 灌溉三重项",
        "",
        markdown_table(pd.concat([irr_g057, irr_g185], ignore_index=True), 10),
        "",
        "## 六、代表 scale 物候期响应面摘要",
        "",
        markdown_table(pheno_summary, 10),
        "",
        "## 七、B067 baseline TE by SR",
        "",
        markdown_table(b067_te, 20),
        "",
        "## 八、主要漏洞与改进",
        "",
        "1. `G057/G185` 更适合承载 region-first 故事，但它们不是原 B067 主框架；正式论文需要将 `G057` 标为结果导向主展示或将 `G185` 作为 main_sample 口径替代，并把 `B067/G195` 保留为旧框架可比性。",
        "2. `G057` 没有启用 `sr_within` 和 `zone_core`，因此 national/irrigation 结果会包含非核心区，并且 SR 交互部分包含跨网格 SR 水平差异所定义的斜率异质性；不能写成纯 within-grid adoption effect。",
        "3. 灌溉异质性应以连续 `irr_frac` 三重项为主检验，中位数或既有 `irr_group` 分组只适合可视化；三类 hazard 原始单位不同，必须用 P90 情景效应或标准化后比较。",
        "4. IE/DE/TE 的 `IE=(a1+a3×SR)×b`、`DE=c1+c3×SR` 是 association decomposition，不是因果中介；使用时应报告 SR P25/P50/P75 的支持范围和 bootstrap CI。",
        "5. 物候期结果应服务联合热旱响应面和生理时序一致性；`V3–HE` 与 `HE±10/HE–MA` 方向相反，不能只挑选正向窗口而不报告反向窗口。",
        "6. `region_first_story_search.py` 和 `expanded_scale_story_search.py` 的最终筛选大量依赖 Python FE、cluster SE 与正态近似；正式表格中应对 G057/G185/G195 的最终模型做 Stata `reghdfe, vce(cluster grid_id)` 复核。",
        "7. 旧 `step5_heterogeneity.do` 使用省份手工生成区域，且没有 SH 口径；当前 region-first 结论应以 `maize_zone` 口径为准，旧表不应作为正式区域异质性证据。",
        "8. NW 和 SH 支持度不足，适合作为 power-limited boundary，不适合写成确定性区域采用结论。",
        "",
        "## 九、直接可用的结论句",
        "",
        "主结论：秸秆还田更适合被定位为区域定向的气候风险缓冲技术，而不是全国统一的平均增产技术；其优先采用场景是主导气候约束明确、产量损失斜率较陡，且土壤水分或地表覆盖仍具有管理弹性的地区。",
        "",
        "区域句：在东北玉米区，SR 的适用价值更接近 drought-buffering；在黄淮海及部分南方区域，SR 的适用价值更接近 heat 或 hotdry buffering；西北只能写为方向性支持且受样本功率限制。",
        "",
        "物候句：SR 与联合热旱损失减弱之间的关联集中在抽雄前后和抽雄至成熟阶段，而不是一个全年均匀存在的复合胁迫保护。",
        "",
        "灌溉句：灌溉条件改变 SR 的边际保护类型；现有结果最稳的是灌溉越充分，SR 的 heat-buffering 边际空间越小，而 drought 上的互补方向需要更谨慎表述。",
        "",
        "方法句：本文识别的是 conditional association with climate-damage slopes，不是 SR 的无条件因果增产效应，也不是 soil-moisture causal mediation。",
        "",
        "## 十、输出文件",
        "",
        "- `story_scale_match.csv`：故事线与推荐 scale。",
        "- `story_literature_support.csv`：每条故事线对应的 Zotero 文献支持。",
        "- `region_first_top15.csv`：region-first 排名前 15。",
        "- `selected_region_details.csv`：G057/G185/G195/G255/G049/G177 区域细节。",
        "- `selected_irrigation_triples.csv`：G057/G185 灌溉三重项。",
        "- `representative_phenology_summary.csv`：代表 scale 的物候响应摘要。",
        "- `b067_baseline_te_by_sr.csv`：B067 baseline TE 分位数。",
        "- follow-up margins 报告：`quality_reports/2026-06-18_story_followup_margins.md`。",
        "- Stata 复核报告：`quality_reports/2026-06-18_story_stata_verify.md`。",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    write_outputs()
