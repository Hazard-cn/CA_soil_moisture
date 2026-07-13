from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = ROOT / "quality_reports" / "agent_runs" / "2026-06-19_storyline_evidence_engine"
CONTEXT_DIR = RUN_DIR / "00_context"
DESCRIPTIVE_DIR = RUN_DIR / "20_descriptive"
FIGURE_DIR = DESCRIPTIVE_DIR / "figures"
REVIEW_DIR = RUN_DIR / "50_review"
SYNTHESIS_DIR = RUN_DIR / "60_synthesis"


def ensure_dirs() -> None:
    for path in [CONTEXT_DIR, DESCRIPTIVE_DIR, FIGURE_DIR, REVIEW_DIR, SYNTHESIS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def read_csv(rel_path: str) -> list[dict[str, str]]:
    path = ROOT / rel_path
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def num(value: object, default: float | None = None) -> float | None:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if text == "":
        return default
    try:
        value_float = float(text)
    except ValueError:
        return default
    if math.isnan(value_float):
        return default
    return value_float


def fmt(value: object, digits: int = 3) -> str:
    value_float = num(value)
    if value_float is None:
        return "NA"
    if abs(value_float) >= 100:
        return f"{value_float:,.1f}"
    if abs(value_float) >= 1:
        return f"{value_float:,.{digits}f}"
    return f"{value_float:.{digits}g}"


def fmt_pct(value: object, digits: int = 2) -> str:
    value_float = num(value)
    if value_float is None:
        return "NA"
    return f"{value_float:.{digits}f}%"


def by_key(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in rows}


def filter_rows(rows: list[dict[str, str]], **conditions: str) -> list[dict[str, str]]:
    out = []
    for row in rows:
        ok = True
        for key, value in conditions.items():
            if row.get(key) != value:
                ok = False
                break
        if ok:
            out.append(row)
    return out


def first_row(rows: list[dict[str, str]], **conditions: str) -> dict[str, str]:
    matched = filter_rows(rows, **conditions)
    return matched[0] if matched else {}


def supplemental_lit_rows() -> list[dict[str, str]]:
    """Sub-agent verified Zotero entries not all present in story_literature_support.csv."""
    return [
        {
            "story_id": "S1",
            "item_key": "58E9GZYN",
            "citation_key": "",
            "year": "2025",
            "title": "Impacts of climate change on global agriculture accounting for adaptation",
            "publicationTitle": "Nature",
            "DOI": "10.1038/s41586-025-09085-w",
        },
        {
            "story_id": "S1",
            "item_key": "XKWMKJSA",
            "citation_key": "",
            "year": "2015",
            "title": "Productivity limits and potentials of the principles of conservation agriculture",
            "publicationTitle": "Nature",
            "DOI": "",
        },
        {
            "story_id": "S2",
            "item_key": "ATWKWYN2",
            "citation_key": "",
            "year": "2020",
            "title": "Combined influence of soil moisture and atmospheric evaporative demand is important for accurately predicting US maize yields",
            "publicationTitle": "Nature Food",
            "DOI": "10.1038/s43016-020-0028-7",
        },
        {
            "story_id": "S2",
            "item_key": "T79SQWVL",
            "citation_key": "",
            "year": "2023",
            "title": "Disentangling the effects of vapor pressure deficit on northern terrestrial vegetation productivity",
            "publicationTitle": "Science Advances",
            "DOI": "10.1126/sciadv.adf3166",
        },
        {
            "story_id": "S3",
            "item_key": "RYJCGIPT",
            "citation_key": "",
            "year": "2024",
            "title": "Observational evidence for groundwater influence on crop yields in the United States",
            "publicationTitle": "Proceedings of the National Academy of Sciences",
            "DOI": "10.1073/pnas.2400085121",
        },
        {
            "story_id": "S3",
            "item_key": "GB4X6D6G",
            "citation_key": "",
            "year": "2021",
            "title": "Global irrigation contribution to wheat and maize yield",
            "publicationTitle": "Nature Communications",
            "DOI": "10.1038/s41467-021-21498-5",
        },
        {
            "story_id": "S5",
            "item_key": "D6QXTQ78",
            "citation_key": "",
            "year": "2025",
            "title": "Conservation agriculture raises crop nitrogen acquisition by amplifying plant-microbe synergy under climate warming",
            "publicationTitle": "Nature Communications",
            "DOI": "10.1038/s41467-025-65999-z",
        },
    ]


def make_lit_formatter(lit_rows: list[dict[str, str]]):
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()
    for row in lit_rows + supplemental_lit_rows():
        key = (row.get("story_id", ""), row.get("item_key", ""))
        if key in seen:
            continue
        seen.add(key)
        grouped[row.get("story_id", "")].append(row)

    def format_story(story_id: str, fallback: list[str] | None = None, limit: int = 4) -> str:
        rows = grouped.get(story_id, [])
        if not rows and fallback:
            rows = []
            seen = set()
            for sid in fallback:
                for item in grouped.get(sid, []):
                    item_key = item.get("item_key", "")
                    if item_key and item_key not in seen:
                        rows.append(item)
                        seen.add(item_key)
                    if len(rows) >= limit:
                        break
                if len(rows) >= limit:
                    break
        parts = []
        for row in rows[:limit]:
            citation_key = row.get("citation_key", "").strip() or "未提供"
            doi = row.get("DOI", "").strip() or "未提供"
            parts.append(
                f"{row.get('title', 'Untitled')} ({row.get('year', 'NA')}; "
                f"{row.get('publicationTitle', 'NA')}; DOI={doi}; "
                f"item_key={row.get('item_key', 'NA')}; citation_key={citation_key})"
            )
        return "；".join(parts) if parts else "当前 Zotero 支持表中未形成独立三文献证据链。"

    return format_story


def collect_inputs() -> dict[str, list[dict[str, str]]]:
    return {
        "story_scale": read_csv("temp/2026-06-18_story_empirical_review_match/story_scale_match.csv"),
        "lit": read_csv("temp/2026-06-18_story_empirical_review_match/story_literature_support.csv"),
        "region": read_csv("temp/2026-06-18_story_empirical_review_match/region_first_top15.csv"),
        "irrigation": read_csv("temp/2026-06-18_story_followup_margins/irrigation_standardized_margins.csv"),
        "phenology": read_csv("temp/2026-06-18_story_followup_margins/phenology_srdh_margins.csv"),
        "phenology_summary": read_csv("temp/2026-06-18_story_empirical_review_match/representative_phenology_summary.csv"),
        "iede_delta": read_csv("temp/2026-06-18_story_followup_margins/b067_iede_delta.csv"),
        "iede_levels": read_csv("temp/2026-06-18_story_followup_margins/b067_iede_levels.csv"),
        "stata_verify": read_csv("temp/2026-06-18_story_stata_verify/stata_python_verify_comparison.csv"),
    }


def build_context_files(data: dict[str, list[dict[str, str]]]) -> None:
    story_rows = data["story_scale"]
    region_rows = data["region"]
    verify_rows = data["stata_verify"]

    inventory = [
        "# Project Inventory for Storyline Evidence Engine",
        "",
        "## 已读取的核心输入",
        "",
        "- `story_scale_match.csv`: 既有候选故事、主 scale、证据和风险。",
        "- `story_literature_support.csv`: Zotero 文献证据、DOI、item key 与目标刊物主题标签。",
        "- `region_first_top15.csv`: region-first scale 排名与区域主导胁迫。",
        "- `irrigation_standardized_margins.csv`: 灌溉分位数下 P90 hazard 的 SR IQR buffer margin。",
        "- `phenology_srdh_margins.csv`: 物候窗口 D×H 与 SR×D×H 的 SR 分位数 slope。",
        "- `b067_iede_delta.csv`: B067 中 TE 在 SR P75-P25 的 P90 hazard 差异。",
        "- `b067_iede_levels.csv`: B067 中 DE/IE/TE 在 SR P25/P50/P75 的水平与 bootstrap CI。",
        "- `stata_python_verify_comparison.csv`: G057/G185 Python 与 Stata 系数复核。",
        "",
        "## 既有候选故事",
        "",
    ]
    for row in story_rows:
        inventory.append(f"- `{row.get('story_id')}`: {row.get('title')}；primary_scale={row.get('primary_scale')}；use_as={row.get('use_as')}")
    inventory.extend(["", "## Region-first top scales", ""])
    for row in region_rows[:8]:
        inventory.append(
            f"- `{row.get('sample_id')}`: N={row.get('N_sample')}, region_score={row.get('region_score')}, "
            f"NE={row.get('ne_dominant')}, HHH={row.get('hhh_dominant')}, NW={row.get('nw_dominant')}, "
            f"SW={row.get('sw_dominant')}, SH={row.get('sh_dominant')}"
        )
    if verify_rows:
        max_coef_diff = max(abs(num(row.get("coef_diff"), 0.0) or 0.0) for row in verify_rows)
        max_p_diff = max(abs(num(row.get("p_diff"), 0.0) or 0.0) for row in verify_rows)
        inventory.extend(
            [
                "",
                "## Stata verification",
                "",
                f"- 对 G057/G185 baseline 与 irrigation 结果，最大系数差为 {max_coef_diff:.3g}，最大 p 值差为 {max_p_diff:.3g}。",
            ]
        )
    write_text(CONTEXT_DIR / "project_inventory.md", "\n".join(inventory))

    write_text(
        CONTEXT_DIR / "evidence_rule.md",
        """
        # Evidence Rule

        `strong`：至少一个主 scale 和一个备选 scale 支持，方向与文献一致，有 Stata 或等价复核，存在明确图表承载，并已列出边界。

        `moderate`：核心方向清楚，能进入主文支撑线，但至少存在一个限制，例如只在特定物候窗口、灌溉维度或机制分解中成立。

        `suggestive`：方向与理论一致，但只能作为机制解释、边界条件或 appendix，不得写为中心贡献。

        `exploratory`：当前主要来自探索性匹配，缺少复核、样本支持或反证检查。

        `not_supported`：现有结果不支持作为论文结论，最多用于说明不得采用的叙事。
        """,
    )

    write_text(
        CONTEXT_DIR / "output_contract.md",
        """
        # Output Contract

        每条故事固定包含：`story_id`, `claim`, `preferred_scale`, `backup_scale`, `core_result`, `directional_pattern`, `support_level`, `zotero_evidence`, `empirical_evidence`, `counter_evidence`, `missing_test`, `safe_sentence_cn`, `safe_sentence_en`, `unsafe_sentence`, `main_text_or_appendix`。

        最终判断采用 conditional association、state-dependent buffering、stress-response slope 等表述，不使用 causal effect、robust finding、causal mediation 或无条件推广语句。
        """,
    )

    model_registry_rows = [
        {
            "model_id": "region_first_G057_G185",
            "script_or_output": "temp/2026-06-18_story_empirical_review_match/region_first_top15.csv",
            "role": "main regional targeting evidence",
            "stories": "S1",
        },
        {
            "model_id": "irrigation_margins_G057_G185",
            "script_or_output": "temp/2026-06-18_story_followup_margins/irrigation_standardized_margins.csv",
            "role": "irrigation heterogeneity margins",
            "stories": "S3,S5",
        },
        {
            "model_id": "phenology_srdh_G057_G185",
            "script_or_output": "temp/2026-06-18_story_followup_margins/phenology_srdh_margins.csv",
            "role": "phenology-specific compound D-H response",
            "stories": "S2,S6",
        },
        {
            "model_id": "B067_TE_IE_DE",
            "script_or_output": "temp/2026-06-18_story_followup_margins/b067_iede_delta.csv; temp/2026-06-18_story_followup_margins/b067_iede_levels.csv",
            "role": "baseline stress-response slope and mechanism-consistent decomposition",
            "stories": "S4,S5",
        },
        {
            "model_id": "stata_verify_G057_G185",
            "script_or_output": "temp/2026-06-18_story_stata_verify/stata_python_verify_comparison.csv",
            "role": "Stata verification for coefficients and p-values",
            "stories": "S1,S3",
        },
    ]
    write_csv(CONTEXT_DIR / "model_registry.csv", model_registry_rows, ["model_id", "script_or_output", "role", "stories"])


def summarize_region(data: dict[str, list[dict[str, str]]]) -> tuple[str, str]:
    region_by_id = by_key(data["region"], "sample_id")
    g057 = region_by_id.get("G057", {})
    g185 = region_by_id.get("G185", {})
    core = (
        f"G057: N={g057.get('N_sample', 'NA')}, grids={g057.get('N_grids_sample', 'NA')}, "
        f"region_score={g057.get('region_score', 'NA')}/16, region_evidence={fmt(g057.get('region_evidence'))}; "
        f"G185: N={g185.get('N_sample', 'NA')}, grids={g185.get('N_grids_sample', 'NA')}, "
        f"region_score={g185.get('region_score', 'NA')}/16, main_sample={g185.get('main_sample', 'NA')}."
    )
    pattern = (
        f"NE={g057.get('ne_dominant', 'NA')}, HHH={g057.get('hhh_dominant', 'NA')}, "
        f"NW={g057.get('nw_dominant', 'NA')}, SW={g057.get('sw_dominant', 'NA')}, "
        f"SH={g057.get('sh_dominant', 'NA')}."
    )
    return core, pattern


def summarize_stata(data: dict[str, list[dict[str, str]]]) -> str:
    verify = data["stata_verify"]
    if not verify:
        return "未读取到 Stata 复核表。"
    max_coef_diff = max(abs(num(row.get("coef_diff"), 0.0) or 0.0) for row in verify)
    max_p_diff = max(abs(num(row.get("p_diff"), 0.0) or 0.0) for row in verify)
    scales = sorted(set(row.get("scale", "") for row in verify if row.get("scale")))
    models = sorted(set(row.get("model", "") for row in verify if row.get("model")))
    return f"Stata 复核覆盖 {','.join(scales)} 的 {','.join(models)}；最大系数差 {max_coef_diff:.3g}，最大 p 值差 {max_p_diff:.3g}。"


def summarize_irrigation(data: dict[str, list[dict[str, str]]], scale: str = "G057") -> str:
    rows = data["irrigation"]
    pieces = []
    for hazard in ["drought", "heat", "hotdry"]:
        p25 = first_row(rows, scale=scale, hazard=hazard, irr_level="P25")
        p75 = first_row(rows, scale=scale, hazard=hazard, irr_level="P75")
        delta = first_row(rows, scale=scale, hazard=hazard, irr_level="P75_minus_P25")
        pieces.append(
            f"{hazard}: irr P25 {fmt_pct(p25.get('pct_yield_buffer_at_hazard_p90'))}, "
            f"irr P75 {fmt_pct(p75.get('pct_yield_buffer_at_hazard_p90'))}, "
            f"P75-P25 {fmt_pct(delta.get('pct_yield_buffer_at_hazard_p90'))}, "
            f"triple p={fmt(p25.get('triple_p'))}"
        )
    return f"{scale} P90 hazard standardized margins: " + "；".join(pieces) + "."


def summarize_phenology(data: dict[str, list[dict[str, str]]], scale: str = "G057") -> str:
    rows = data["phenology"]
    pieces = []
    for window in ["hepm10", "hema", "v3he"]:
        p25 = first_row(rows, scale=scale, window=window, ca_level="P25")
        p75 = first_row(rows, scale=scale, window=window, ca_level="P75")
        delta = first_row(rows, scale=scale, window=window, ca_level="P75_minus_P25")
        if not p25 and not p75:
            continue
        pieces.append(
            f"{window}: beta_DH={fmt(p25.get('beta_DH'))} (p={fmt(p25.get('beta_DH_p'))}), "
            f"SR×D×H={fmt(p25.get('gamma_SRDH'))} (p={fmt(p25.get('gamma_SRDH_p'))}), "
            f"slope P25={fmt(p25.get('dh_slope_at_ca'))}, P75={fmt(p75.get('dh_slope_at_ca'))}, "
            f"shift={fmt(delta.get('dh_slope_at_ca'))}"
        )
    return f"{scale} phenology D×H slope: " + "；".join(pieces) + "."


def summarize_iede(data: dict[str, list[dict[str, str]]]) -> str:
    rows = data["iede_delta"]
    pieces = []
    for row in rows:
        pieces.append(
            f"{row.get('hazard')}: TE(P75-P25)={fmt_pct(row.get('pct_delta_point_percent'))}, "
            f"CI [{fmt_pct(row.get('pct_delta_ci_lo_percent'))}, {fmt_pct(row.get('pct_delta_ci_hi_percent'))}], "
            f"N_boot={fmt(row.get('N_boot'), 0)}"
        )
    return "B067 P90 hazard 下 SR P75-P25 的 TE 差异：" + "；".join(pieces) + "."


def summarize_stress_specific_iede(data: dict[str, list[dict[str, str]]]) -> str:
    rows = data["iede_levels"]
    if not rows:
        return "未读取到 B067 IE/DE/TE level 表。"
    pieces = []
    for hazard, effect in [("drought", "IE"), ("hotdry", "IE"), ("heat", "DE")]:
        p25 = first_row(rows, hazard=hazard, effect=effect, ca_level="P25")
        p75 = first_row(rows, hazard=hazard, effect=effect, ca_level="P75")
        pieces.append(
            f"{hazard} {effect}: P25={fmt(p25.get('estimate'))} "
            f"[{fmt(p25.get('bs_ci_lo_95'))}, {fmt(p25.get('bs_ci_hi_95'))}], "
            f"P75={fmt(p75.get('estimate'))} "
            f"[{fmt(p75.get('bs_ci_lo_95'))}, {fmt(p75.get('bs_ci_hi_95'))}]"
        )
    return "B067 association decomposition levels: " + "；".join(pieces) + "."


def build_story_rows(data: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    lit = make_lit_formatter(data["lit"])
    region_core, region_pattern = summarize_region(data)
    stata_summary = summarize_stata(data)
    irrigation_core_g057 = summarize_irrigation(data, "G057")
    irrigation_core_g185 = summarize_irrigation(data, "G185")
    phenology_core_g057 = summarize_phenology(data, "G057")
    phenology_core_g185 = summarize_phenology(data, "G185")
    iede_core = summarize_iede(data)
    stress_specific_core = summarize_stress_specific_iede(data)

    return [
        {
            "story_id": "S1_main_region_targeting",
            "claim": "秸秆还田更适合被写成区域定向的气候风险缓冲技术，而不是全国统一的平均增产技术。",
            "preferred_scale": "G185 main table; G057 region-first display",
            "backup_scale": "G049/G177 near-twin sensitivity; G255 strict sensitivity",
            "core_result": f"{region_core} {stata_summary}",
            "directional_pattern": region_pattern,
            "support_level": "moderate",
            "zotero_evidence": lit("S1"),
            "empirical_evidence": "region-first ranking 显示 G057/G185 均为 region_score=15/16；区域主导 hazard 类型一致。G185 启用 main_sample=1 且核心变量更干净，适合主文表格；G057 是最大 region-first 支持版本，适合图示或并列展示。",
            "counter_evidence": "G057 不是 main_sample=1，存在 irr_frac_raw 缺失和 zone_core=0；G057/G185 均未启用 sr_within；NW 没有 p<0.10 的区域支持，SH 样本偏小；region-first 来自多 scale 评分排序，不是确认性预设 scale。",
            "missing_test": "补 region×SR×hazard 的 Stata/pooled Wald 正式表、完整 high-score candidates 分布和 FDR/Holm 或等价多重检验说明。",
            "safe_sentence_cn": "在明确披露 scale search 和区域样本边界后，当前结果最适合写成区域定向的气候风险缓冲，即 SR 相关损失斜率变化取决于不同玉米区的主导胁迫。",
            "safe_sentence_en": "Conditional on transparent scale-search reporting, the evidence is best framed as region-targeted climate-risk buffering, where SR-related slope changes depend on the dominant stress regime of each maize region.",
            "unsafe_sentence": "SR 在所有地区都稳定提高产量，或西北/任一区域的效果统计上最强。",
            "main_text_or_appendix": "main: total storyline",
        },
        {
            "story_id": "S2_support_phenology_compound",
            "claim": "SR 对联合热旱损失的缓冲更适合写成物候期定位的响应，而不是全年均匀存在的复合胁迫保护。",
            "preferred_scale": "G057",
            "backup_scale": "G185; G195/B067; G255 strict endpoint",
            "core_result": f"{phenology_core_g057} Backup: {phenology_core_g185}",
            "directional_pattern": "HE±10 和 HE-MA 中 D×H 为负、SR×D×H 为正，SR P75 的 D×H slope 相比 P25 明显趋平；V3-HE 不支持同一方向。",
            "support_level": "moderate",
            "zotero_evidence": lit("S2"),
            "empirical_evidence": "representative_phenology_summary 显示 HE±10 为 8/8 D×H<0 且 8/8 SR×D×H>0，HE-MA 也基本同向；G057/G185 的 margins 明确给出 P25 到 P75 的 slope shift。",
            "counter_evidence": "full season 不支持严格联合损失；V3-HE 方向相反；窗口选择存在 post-hoc 叙事风险，因此不能把 HE±10 外推为全生育期机制。",
            "missing_test": "补 β_DH+γ_SRDH×SR_q 的 cluster CI 或 lincom/delta-method 图；在 appendix 报告全部窗口的方向分布和 V3-HE 边界。",
            "safe_sentence_cn": "联合热旱故事应限定在抽雄至成熟附近的关键窗口，写作对象是生育期定位的损失斜率变化，而不是全年统一保护效应。",
            "safe_sentence_en": "The compound-stress signal is phenology-specific, with SR-related slope flattening concentrated around the flowering-to-maturity windows rather than across the entire season.",
            "unsafe_sentence": "SR 稳健缓解全年所有联合热旱损失。",
            "main_text_or_appendix": "main: supporting storyline",
        },
        {
            "story_id": "S3_support_irrigation_reallocation",
            "claim": "灌溉会重新配置 SR 的边际保护价值；最稳妥的写法是高灌溉降低 heat/hotdry buffering 的边际空间，而 drought 互补只能弱写。",
            "preferred_scale": "G057",
            "backup_scale": "G185; B067/G195 comparability",
            "core_result": f"{irrigation_core_g057} Backup: {irrigation_core_g185}",
            "directional_pattern": "在 P90 heat 和 hotdry 情景下，SR IQR 的 buffer margin 从低灌溉到高灌溉下降；drought 的连续 triple 为正但统计强度弱于 heat/hotdry。",
            "support_level": "moderate",
            "zotero_evidence": lit("S3", fallback=["S1", "S2"]),
            "empirical_evidence": "G057/G185 的 heat triple<0 且 p<0.001，hotdry triple<0 且 p≈0.012；P90 标准化 margins 显示 heat/hotdry buffer 从低灌溉到高灌溉明显收缩。",
            "counter_evidence": "drought triple p≈0.089，只能写 suggestive complement；G255 的 hotdry 边界更弱；不能用灌溉高低组单独显著性替代连续 triple。",
            "missing_test": "主文使用连续 irr_frac margins 图；补 irrigation overlap/support range 和排除极低灌溉样本的 sensitivity。",
            "safe_sentence_cn": "灌溉异质性支持的不是简单的灌溉越多越好，而是灌溉会压缩 SR 在热和热旱风险下的额外边际缓冲空间。",
            "safe_sentence_en": "Irrigation appears to reallocate the marginal value of SR, narrowing the additional buffering space under heat and hot-dry exposure while providing only suggestive evidence for drought complementarity.",
            "unsafe_sentence": "灌溉越充分，SR 越有效；或 SR 与灌溉在所有灾害上均显著互补。",
            "main_text_or_appendix": "main: supporting storyline",
        },
        {
            "story_id": "S4_mechanism_stress_slope",
            "claim": "在单一和复合胁迫下，更高 SR 与更平缓的产量损失斜率相关；这可以作为结果层和机制一致性证据，而不应单独作为中心贡献。",
            "preferred_scale": "B067",
            "backup_scale": "G195; G057/G185 as region-first alternatives",
            "core_result": iede_core,
            "directional_pattern": "drought、heat、hotdry 的 TE 在 SR P75 相比 P25 均向减损方向移动，IE/DE 仅用于说明 channel-consistent correlation structure。",
            "support_level": "moderate",
            "zotero_evidence": lit("S4", fallback=["S1", "S2"]),
            "empirical_evidence": "B067 bootstrap delta 显示 P90 drought、heat、hotdry 下 TE(P75-P25) 均为正且 CI 不跨 0；该结果适合承载 baseline slope flattening。",
            "counter_evidence": "TE/IE/DE 不是因果中介；B067 不是 region-first 最优 scale；不能把斜率缓冲写成正常年份平均增产。",
            "missing_test": "补一张低/中/高 hazard 下 SR marginal association 图；正文明确 IE/DE 为 association decomposition。",
            "safe_sentence_cn": "B067 的分解结果可写为与机制一致的相关结构，即更高 SR 对应更平缓的胁迫-产量损失斜率，但不能写成因果中介。",
            "safe_sentence_en": "The B067 decomposition provides channel-consistent association evidence that higher SR is linked to flatter stress-yield loss slopes, without identifying a causal mediation pathway.",
            "unsafe_sentence": "土壤水分是 SR 提高产量的因果中介，或 TE/IE/DE 证明了因果机制。",
            "main_text_or_appendix": "mechanism/results layer; not standalone central contribution",
        },
        {
            "story_id": "S5_mechanism_stress_specific_channels",
            "claim": "不同胁迫对应的机制相关结构不同；drought/hotdry 更接近土壤水分通道一致性，heat 更像非当前根区土壤水分通道或直接调制。",
            "preferred_scale": "B067",
            "backup_scale": "G195 if same decomposition is generated",
            "core_result": stress_specific_core,
            "directional_pattern": "drought 和 hotdry 的 IE 为负且 bootstrap 区间不跨 0；heat 的 IE 变化很小，而 P75 的 DE 为正且区间不跨 0。",
            "support_level": "suggestive",
            "zotero_evidence": lit("S5", fallback=["S2", "S4"]),
            "empirical_evidence": "B067 IE/DE/TE levels 显示 drought/hotdry 更符合 SM-pathway-consistent buffering，heat 不适合写成通过当前年度根区 SM 的同一机制。",
            "counter_evidence": "该结果是 association decomposition，不是 a-path/b-path/Sobel，也没有直接观测 soil health、microbiome、N acquisition 或 VPD pathway。",
            "missing_test": "若要进入主文机制图，需补 IE slope 与 DE slope 的跨 hazard bootstrap difference；否则保留为 Discussion/appendix 机制解释。",
            "safe_sentence_cn": "不同胁迫下的分解结果只能说明通道一致性不同：drought 和 hotdry 更接近土壤水分相关结构，heat 不能被写成同一土壤水分中介通道。",
            "safe_sentence_en": "The decomposition suggests stress-specific channel consistency: drought and hot-dry responses are more aligned with soil-moisture-related structure, whereas heat should not be attributed to the same soil-moisture mediation channel.",
            "unsafe_sentence": "SR 通过土壤水分因果性地缓解所有类型的气候损失，或 heat 主要通过根区土壤水分中介。",
            "main_text_or_appendix": "discussion/appendix mechanism",
        },
        {
            "story_id": "S6_boundary_nonuniversal_adoption",
            "claim": "SR 的政策含义应写成条件采用和区域定向，而不是普遍推广；湿润、高灌溉或非关键物候窗口是边界条件。",
            "preferred_scale": "G057/G185 synthesis",
            "backup_scale": "B067/G195 mechanism checks",
            "core_result": "来自 S1-S5 的共同边界：高灌溉 heat/hotdry margins 收缩，V3-HE 不支持联合热旱缓冲，NW/SH 统计强度受限，B067 只支持相关分解。",
            "directional_pattern": "可写方向是 targeting and boundary，而不是 universal benefit。",
            "support_level": "suggestive",
            "zotero_evidence": lit("S6", fallback=["S1", "S3", "S5"]),
            "empirical_evidence": "现有强结果均依赖区域、灌溉或物候条件；这本身支持条件采用的讨论，但不是一个独立模型结果。",
            "counter_evidence": "边界条件来自多个结果的综合，不是单一预注册假设；需避免写成强政策处方。",
            "missing_test": "可补一张 story-level evidence map；若要写政策建议，需报告各区域样本量和灌溉覆盖。",
            "safe_sentence_cn": "政策含义应限定为基于区域主导胁迫和灌溉条件的定向采用，而不是把 SR 描述为无条件适用的平均增产技术。",
            "safe_sentence_en": "The policy implication is targeted adoption conditional on regional stress regimes and irrigation context, not a universal yield-gain prescription.",
            "unsafe_sentence": "SR 应在所有区域同等推广，或任一地区在所有条件下都应优先采用。",
            "main_text_or_appendix": "discussion boundary condition",
        },
        {
            "story_id": "S7_not_supported_universal_compound",
            "claim": "全年、所有区域、所有灌溉条件下的统一联合热旱保护故事当前不能讲。",
            "preferred_scale": "not applicable",
            "backup_scale": "not applicable",
            "core_result": "full season D×H 不满足严格联合损失，V3-HE 与 HE±10/HE-MA 方向不一致，灌溉结果显示 heat/hotdry 的 SR margin 在高灌溉下收缩。",
            "directional_pattern": "证据支持条件性和窗口性，不支持 universal compound protection。",
            "support_level": "not_supported",
            "zotero_evidence": lit("S6", fallback=["S2", "S1"]),
            "empirical_evidence": "代表性物候汇总显示 full season 和 V3-HE 不能支撑与 HE±10/HE-MA 同样的结论；灌溉与区域结果也不支持统一方向。",
            "counter_evidence": "HE±10 和 HE-MA 可以作为局部支持，但不能外推到全年和所有条件。",
            "missing_test": "若未来要重启该故事，需要重新定义 compound exposure、做窗口敏感性和事前阈值设定。",
            "safe_sentence_cn": "当前结果不支持把 SR 写成全年统一的联合热旱保护技术。",
            "safe_sentence_en": "The current evidence does not support a universal season-wide compound heat-drought protection claim for SR.",
            "unsafe_sentence": "SR 在所有季节窗口均能稳健缓解联合热旱损失。",
            "main_text_or_appendix": "do not use as storyline; use as review-risk warning",
        },
    ]


def write_final_story_ranking(rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "story_id",
        "claim",
        "preferred_scale",
        "backup_scale",
        "core_result",
        "directional_pattern",
        "support_level",
        "zotero_evidence",
        "empirical_evidence",
        "counter_evidence",
        "missing_test",
        "safe_sentence_cn",
        "safe_sentence_en",
        "unsafe_sentence",
        "main_text_or_appendix",
    ]
    write_csv(SYNTHESIS_DIR / "final_story_ranking.csv", rows, fieldnames)

    lines = [
        "# Final Story Ranking",
        "",
        "## 推荐结构",
        "",
        "总主线：`S1_main_region_targeting`，即区域定向的气候风险缓冲，而不是全国统一平均增产。该线当前等级为 `moderate`，原因是 region-first 来自 scale search，必须披露候选分布和多重检验风险；但它仍是最适合承载全文的总叙事。",
        "",
        "两条支撑主线：`S2_support_phenology_compound` 与 `S3_support_irrigation_reallocation`。前者说明复合热旱响应集中在关键物候窗口，后者说明灌溉改变 SR 的边际保护空间。",
        "",
        "机制线：`S4_mechanism_stress_slope` 可进入结果或机制解释，`S5_mechanism_stress_specific_channels` 只能作为 Discussion/appendix 的 stress-specific mechanism context；两者都必须使用 association decomposition 表述。",
        "",
        "边界线：`S6_boundary_nonuniversal_adoption` 适合 Discussion；`S7_not_supported_universal_compound` 只用于提醒不能写的中心故事。",
        "",
        "## 排序表",
        "",
        "| rank | story_id | support | preferred scale | role | claim |",
        "|---:|---|---|---|---|---|",
    ]
    for idx, row in enumerate(rows, start=1):
        lines.append(
            f"| {idx} | `{row['story_id']}` | {row['support_level']} | {row['preferred_scale']} | "
            f"{row['main_text_or_appendix']} | {row['claim']} |"
        )
    lines.extend(["", "## 分故事证据链", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['story_id']}",
                "",
                f"**中心命题：** {row['claim']}",
                "",
                f"**首选 scale：** {row['preferred_scale']}；**备选 scale：** {row['backup_scale']}",
                "",
                f"**核心结果：** {row['core_result']}",
                "",
                f"**方向性模式：** {row['directional_pattern']}",
                "",
                f"**文献证据：** {row['zotero_evidence']}",
                "",
                f"**经验依据：** {row['empirical_evidence']}",
                "",
                f"**反证或边界：** {row['counter_evidence']}",
                "",
                f"**缺失检验：** {row['missing_test']}",
                "",
                f"**可写中文句：** {row['safe_sentence_cn']}",
                "",
                f"**可写英文句：** {row['safe_sentence_en']}",
                "",
                f"**不得写：** {row['unsafe_sentence']}",
                "",
                f"**定位：** {row['main_text_or_appendix']}",
                "",
            ]
        )
    write_text(SYNTHESIS_DIR / "final_story_ranking.md", "\n".join(lines))


def write_safe_sentences(rows: list[dict[str, str]]) -> None:
    lines = ["# Safe Sentences", ""]
    lines.extend(["## Results 可用句", ""])
    for row in rows[:4]:
        lines.append(f"- CN `{row['story_id']}`: {row['safe_sentence_cn']}")
        lines.append(f"- EN `{row['story_id']}`: {row['safe_sentence_en']}")
    lines.extend(
        [
            "",
            "## Discussion / Conclusion 可用句",
            "",
            "- CN: 这些结果共同支持条件性采用逻辑，即 SR 的经验含义取决于区域主导胁迫、灌溉背景和关键物候窗口。",
            "- EN: Taken together, the results support a conditional-adoption interpretation in which the empirical relevance of SR depends on regional stress regimes, irrigation context, and phenological timing.",
            "- CN: 因此，论文结论应强调 targeting 和 boundary，而不是把 SR 写成无条件增产技术。",
            "- EN: The conclusion should therefore emphasize targeting and boundary conditions rather than presenting SR as an unconditional yield-increasing technology.",
            "",
            "## 不得使用的句子",
            "",
        ]
    )
    for row in rows:
        lines.append(f"- `{row['story_id']}`: {row['unsafe_sentence']}")
    write_text(SYNTHESIS_DIR / "safe_sentences.md", "\n".join(lines))


def write_figure_table_plan(rows: list[dict[str, str]]) -> None:
    lines = [
        "# Figure and Table Plan",
        "",
        "## 主文图表",
        "",
        "| order | story | figure/table | scale | required content |",
        "|---:|---|---|---|---|",
        "| 1 | S1 region targeting | Main Figure 1 + Table 1 | G057 main, G185 sensitivity | 区域主导 hazard map 或 coefficient panel；region_score、N、dominant hazard；appendix 报告 G185/G049/G177。 |",
        "| 2 | S3 irrigation reallocation | Main Figure 2 | G057 main, G185 sensitivity | P90 heat/hotdry/drought 下 SR IQR buffer margin，按 irr_frac P25/P50/P75 展示；突出 heat/hotdry 高灌溉边际空间收缩。 |",
        "| 3 | S2 phenology compound | Main Figure 3 | G057 main, G185/G195/B067 sensitivity | HE±10、HE-MA、V3-HE 的 D×H slope at SR P25/P50/P75；V3-HE 作为边界。 |",
        "| 4 | S4 stress slope mechanism | Main Figure 4 or Appendix Figure | B067 main | drought/heat/hotdry 的 TE(P75-P25) 与 CI；IE/DE 只作 association decomposition。 |",
        "| 5 | S5 stress-specific mechanism | Appendix Figure/Table | B067 | drought/hotdry 的 IE 与 heat 的 DE 并列展示；标题只写 channel-consistent association，不写 mediation。 |",
        "| 6 | Review risk | Appendix Table | all | 每条 story 的 safe/unsafe sentence、counter evidence、missing test。 |",
        "",
        "## 本轮生成的辅助图",
        "",
        f"- `{FIGURE_DIR / 'fig_irrigation_margins.png'}`",
        f"- `{FIGURE_DIR / 'fig_phenology_srdh_slopes.png'}`",
        f"- `{FIGURE_DIR / 'fig_b067_te_delta.png'}`",
        "",
        "## 图表写法纪律",
        "",
        "- region 图主文表格优先使用 `G185`，`G057` 用于展示 region-first 最大支持版本；标题只写 dominant stress pattern，不写任一区域统计上绝对最强。",
        "- irrigation 图必须使用连续 `irr_frac` 的标准化 margins，不用简单高低组显著性差异替代 triple。",
        "- phenology 图必须把 V3-HE 或 full-season 作为边界展示，防止过度外推。",
        "- TE/IE/DE 图标题不得使用 mediation、pathway identification 或 causal channel。",
    ]
    write_text(SYNTHESIS_DIR / "figure_table_plan.md", "\n".join(lines))


def write_review_risk_report(rows: list[dict[str, str]]) -> None:
    lines = [
        "# Review Risk Report",
        "",
        "## 总体判断",
        "",
        "最稳妥的论文结构是 1 条总主线、2 条支撑主线、2 条机制/解释线和 1 条边界线。总主线不应写成 SR 平均增产，而应写成区域定向的气候风险缓冲。由于 region-first 来自多 scale 评分搜索，总主线可以作为全文叙事，但当前证据等级应保持为 `moderate`，不是确认性 `strong`。所有机制相关表述必须使用 conditional association、state-dependent buffering、stress-response slope 和 channel-consistent correlation structure。",
        "",
        "## 高风险表述",
        "",
        "- 不得写 causal effect、robust finding、causal mediation、universal benefit。",
        "- 不得写 SR 在所有区域或所有物候窗口均有效。",
        "- 不得把 G057 的 region-first 结果写成预注册唯一 scale。",
        "- 不得把 CA、no-till、residue retention、straw return 和本研究的 SR 变量直接互换。",
        "- 不得省略 256 scale、多 hazard、多区域、多物候窗口带来的 multiple testing 与 post-hoc 风险。",
        "- 不得把 drought 的灌溉互补写成强结论；当前 p 值只支持弱表述。",
        "- 不得把 B067 TE/IE/DE 写成因果中介。",
        "",
        "## 分故事风险",
        "",
        "| story_id | risk | action |",
        "|---|---|---|",
    ]
    for row in rows:
        if row["story_id"] == "S1_main_region_targeting":
            risk = "medium-high"
            action = "可作总主线，但必须同时报告 G185 主表、G057 展示、候选分布和多重检验风险。"
        elif row["support_level"] == "strong":
            risk = "medium"
            action = "主文可写，但需同时报告 backup scale 和边界。"
        elif row["support_level"] == "moderate":
            risk = "medium-high" if "irrigation" in row["story_id"] else "medium"
            action = "主文支撑线可写，句子需限定到对应维度。"
        elif row["support_level"] == "suggestive":
            risk = "high"
            action = "只放 Discussion 或 appendix，不能写成中心贡献。"
        else:
            risk = "critical"
            action = "不能作为正向故事，只能作为不得过度解释的提醒。"
        lines.append(f"| `{row['story_id']}` | {risk} | {action} |")
    lines.extend(
        [
            "",
            "## 必补但不超过两项的检验",
            "",
            "- 对 S1：补 G057/G185/G049/G177 的共同支持样本表或 appendix scale sensitivity。",
            "- 对 S1：补 region×SR×hazard 的 Stata/pooled Wald 正式表、完整 high-score candidate distribution 和 FDR/Holm 或等价多重检验说明。",
            "- 对 S2：补 SR P25/P50/P75 下 D×H slope 的 cluster CI 图。",
            "- 对 S3：补连续 `irr_frac` margins 图、overlap/support range，并报告 drought 只为 suggestive complement。",
            "- 对 S4：补一张低/中/高 hazard 下 SR marginal association 图，或将 B067 TE/IE/DE 移入 appendix。",
            "- 对 S5：若要进入主文机制图，补 IE/DE 跨 hazard bootstrap difference；否则留在 Discussion/appendix。",
            "",
            "## 建议降级项",
            "",
            "- NW/SH 的区域差异：可作为方向性区域边界，不宜作为强异质性结论。",
            "- V3-HE：作为 phenology boundary，不宜作为支撑主线。",
            "- full-season D×H：当前不能支撑严格联合热旱保护。",
            "- drought × irrigation complement：只写可能互补或 suggestive，不写显著互补。",
        ]
    )
    write_text(SYNTHESIS_DIR / "review_risk_report.md", "\n".join(lines))


def write_descriptive_outputs(data: dict[str, list[dict[str, str]]], rows: list[dict[str, str]]) -> None:
    support_rows = []
    for row in rows:
        support_rows.append(
            {
                "story_id": row["story_id"],
                "support_level": row["support_level"],
                "preferred_scale": row["preferred_scale"],
                "backup_scale": row["backup_scale"],
                "main_text_or_appendix": row["main_text_or_appendix"],
            }
        )
    write_csv(
        DESCRIPTIVE_DIR / "story_support_summary.csv",
        support_rows,
        ["story_id", "support_level", "preferred_scale", "backup_scale", "main_text_or_appendix"],
    )

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover
        write_text(DESCRIPTIVE_DIR / "plot_generation_status.txt", f"matplotlib 不可用，未生成 PNG：{exc}")
        return

    # Irrigation margins
    irrigation = data["irrigation"]
    hazards = ["drought", "heat", "hotdry"]
    scales = ["G057", "G185"]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    x_positions = []
    labels = []
    values = []
    colors = []
    for s_idx, scale in enumerate(scales):
        for h_idx, hazard in enumerate(hazards):
            row = first_row(irrigation, scale=scale, hazard=hazard, irr_level="P75_minus_P25")
            x_positions.append(s_idx * (len(hazards) + 1) + h_idx)
            labels.append(f"{scale}\n{hazard}")
            values.append(num(row.get("pct_yield_buffer_at_hazard_p90"), 0.0) or 0.0)
            colors.append("#4C78A8" if hazard == "drought" else "#F58518" if hazard == "heat" else "#E45756")
    ax.bar(x_positions, values, color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("P75-P25 irrigation change in SR buffer margin (pp)")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels)
    ax.set_title("Irrigation reallocates SR marginal buffering space")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "fig_irrigation_margins.png", dpi=300)
    plt.close(fig)

    # Phenology slopes
    phenology = data["phenology"]
    windows = ["hepm10", "hema", "v3he"]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    x_positions = []
    labels = []
    values = []
    for s_idx, scale in enumerate(scales):
        for w_idx, window in enumerate(windows):
            row = first_row(phenology, scale=scale, window=window, ca_level="P75_minus_P25")
            x_positions.append(s_idx * (len(windows) + 1) + w_idx)
            labels.append(f"{scale}\n{window}")
            values.append(num(row.get("dh_slope_at_ca"), 0.0) or 0.0)
    ax.bar(x_positions, values, color="#54A24B")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("D-H slope shift from SR P25 to P75")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels)
    ax.set_title("Phenology-specific compound-stress slope shift")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "fig_phenology_srdh_slopes.png", dpi=300)
    plt.close(fig)

    # B067 TE delta
    iede = data["iede_delta"]
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    labels = [row.get("hazard", "") for row in iede]
    values = [num(row.get("pct_delta_point_percent"), 0.0) or 0.0 for row in iede]
    lows = [num(row.get("pct_delta_ci_lo_percent"), 0.0) or 0.0 for row in iede]
    highs = [num(row.get("pct_delta_ci_hi_percent"), 0.0) or 0.0 for row in iede]
    yerr_low = [v - lo for v, lo in zip(values, lows)]
    yerr_high = [hi - v for v, hi in zip(values, highs)]
    ax.bar(range(len(labels)), values, color="#72B7B2")
    ax.errorbar(range(len(labels)), values, yerr=[yerr_low, yerr_high], fmt="none", color="black", capsize=4)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_ylabel("TE(P75-P25) at P90 hazard (%)")
    ax.set_title("B067 stress-response slope flattening")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "fig_b067_te_delta.png", dpi=300)
    plt.close(fig)

    write_text(DESCRIPTIVE_DIR / "plot_generation_status.txt", "PNG figures generated successfully.")


def main() -> None:
    ensure_dirs()
    data = collect_inputs()
    build_context_files(data)
    rows = build_story_rows(data)
    write_descriptive_outputs(data, rows)
    write_final_story_ranking(rows)
    write_safe_sentences(rows)
    write_figure_table_plan(rows)
    write_review_risk_report(rows)
    print(f"Wrote outputs to {SYNTHESIS_DIR}")


if __name__ == "__main__":
    main()
