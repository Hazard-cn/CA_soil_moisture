from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = ROOT / "quality_reports" / "agent_runs" / "2026-06-20_single_scale_story_pack_v1"
FIG_DIR = RUN_DIR / "figures"


def ensure_dirs() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def read_csv(rel_path: str) -> list[dict[str, str]]:
    path = ROOT / rel_path
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def n(value: object, default: float | None = None) -> float | None:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        out = float(value)
    else:
        text = str(value).strip()
        if text == "":
            return default
        try:
            out = float(text)
        except ValueError:
            return default
    return default if math.isnan(out) else out


def fmt(value: object, digits: int = 3) -> str:
    value = n(value)
    if value is None:
        return "NA"
    if abs(value) >= 100:
        return f"{value:,.0f}"
    if abs(value) >= 1:
        return f"{value:,.{digits}f}"
    return f"{value:.{digits}g}"


def pct(value: object, digits: int = 2) -> str:
    value = n(value)
    if value is None:
        return "NA"
    return f"{value:.{digits}f}%"


def rows_where(rows: list[dict[str, str]], **conds: str) -> list[dict[str, str]]:
    out = []
    for row in rows:
        ok = True
        for key, value in conds.items():
            if row.get(key) != value:
                ok = False
                break
        if ok:
            out.append(row)
    return out


def one(rows: list[dict[str, str]], **conds: str) -> dict[str, str]:
    matches = rows_where(rows, **conds)
    return matches[0] if matches else {}


def by_key(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in rows}


def load_inputs() -> dict[str, list[dict[str, str]]]:
    return {
        "scale_cards": read_csv("quality_reports/agent_runs/2026-06-19_scale_story_cards_v2/scale_story_cards.csv"),
        "scale_desc": read_csv("quality_reports/agent_runs/2026-06-19_scale_story_cards_v2/descriptive_story_stats.csv"),
        "region_details": read_csv("temp/2026-06-18_story_empirical_review_match/selected_region_details.csv"),
        "irrigation_margins": read_csv("temp/2026-06-18_story_followup_margins/irrigation_standardized_margins.csv"),
        "phenology_margins": read_csv("temp/2026-06-18_story_followup_margins/phenology_srdh_margins.csv"),
        "b067_te": read_csv("temp/2026-06-18_story_empirical_review_match/b067_baseline_te_by_sr.csv"),
        "b067_delta": read_csv("temp/2026-06-18_story_followup_margins/b067_iede_delta.csv"),
        "b067_iede": read_csv("temp/2026-06-18_story_followup_margins/b067_iede_levels.csv"),
        "rep_baseline": read_csv("temp/2026-06-11_expanded_scale_story_search/representative_baseline_cluster.csv"),
        "rep_compound": read_csv("temp/2026-06-11_expanded_scale_story_search/representative_compound_cluster.csv"),
        "rep_irrigation": read_csv("temp/2026-06-11_expanded_scale_story_search/representative_irrigation_cluster.csv"),
        "rep_phenology": read_csv("temp/2026-06-11_expanded_scale_story_search/representative_phenology_cluster.csv"),
        "expanded_rank": read_csv("temp/2026-06-11_expanded_scale_story_search/expanded_candidate_ranking.csv"),
        "stata_verify": read_csv("temp/2026-06-18_story_stata_verify/stata_python_verify_comparison.csv"),
        "target_lit": read_csv("temp/2026-06-18_zotero_story_direction/target_journal_relevant_items.csv"),
        "included_lit": read_csv("temp/2026-06-18_zotero_story_direction/included_story_items.csv"),
    }


def title_has(row: dict[str, str], *terms: str) -> bool:
    text = " ".join([row.get("title", ""), row.get("themes", ""), row.get("publicationTitle", "")]).lower()
    return all(term.lower() in text for term in terms)


def lit_pick(data: dict[str, list[dict[str, str]]], theme_terms: list[str], limit: int = 5) -> list[dict[str, str]]:
    rows = data["target_lit"] + data["included_lit"]
    seen = set()
    picked = []
    for row in sorted(rows, key=lambda r: n(r.get("relevance_score"), 0) or 0, reverse=True):
        key = row.get("item_key") or row.get("key")
        if not key or key in seen:
            continue
        text = " ".join([row.get("title", ""), row.get("themes", ""), row.get("publicationTitle", "")]).lower()
        if any(term.lower() in text for term in theme_terms):
            seen.add(key)
            picked.append(
                {
                    "item_key": key,
                    "citation_key": row.get("citation_key", "") or row.get("citationKey", "") or "NA",
                    "title": row.get("title", ""),
                    "journal": row.get("publicationTitle", ""),
                    "year": row.get("year", ""),
                    "doi": row.get("DOI", "") or row.get("doi", "") or "NA",
                    "themes": row.get("themes", ""),
                }
            )
        if len(picked) >= limit:
            break
    return picked


def make_candidate_cards(data: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    cards = by_key(data["scale_cards"], "scale_id")
    groups = [
        ("G195(B067)", ["B067", "G195"], "single-scale recommended candidate"),
        ("G255", ["G255"], "strict one-scale alternative"),
        ("G256", ["G256"], "narrow strict endpoint"),
        ("G185", ["G185"], "clean region-first alternative"),
        ("G057", ["G057"], "region-first display alternative"),
        ("G049/G177", ["G049", "G177"], "near-twin sensitivity envelope"),
        ("broad G001/G009/G017/G033", ["G001", "G009", "G017", "G033"], "broad exploratory envelope"),
    ]
    rows: list[dict[str, object]] = []
    for label, members, role in groups:
        member_rows = [cards[m] for m in members if m in cards]
        n_sample = "; ".join([f"{m}:{cards[m].get('N_sample', 'NA')}" for m in members if m in cards])
        domains = {
            "baseline": any(rows_where(data["rep_baseline"], sample_id=m) for m in members),
            "region": any(rows_where(data["region_details"], sample_id=m) for m in members),
            "irrigation": any(rows_where(data["irrigation_margins"], scale=m) or rows_where(data["rep_irrigation"], sample_id=m) for m in members),
            "phenology": any(rows_where(data["phenology_margins"], scale=m) or rows_where(data["rep_phenology"], sample_id=m) for m in members),
            "te_iede": "B067" in members,
            "stata_verify": any((row.get("scale") in members or row.get("sample_id") in members) for row in data["stata_verify"]),
        }
        domain_count = sum(1 for value in domains.values() if value)
        rows.append(
            {
                "candidate_scale": label,
                "role": role,
                "N_sample": n_sample,
                "main_sample": "; ".join([f"{m}:{cards[m].get('main_sample', 'NA')}" for m in members if m in cards]),
                "zone_core": "; ".join([f"{m}:{cards[m].get('zone_core', 'NA')}" for m in members if m in cards]),
                "sr_within": "; ".join([f"{m}:{cards[m].get('sr_within', 'NA')}" for m in members if m in cards]),
                "domain_count": domain_count,
                "baseline": domains["baseline"],
                "region": domains["region"],
                "irrigation": domains["irrigation"],
                "phenology": domains["phenology"],
                "te_iede": domains["te_iede"],
                "stata_verify": domains["stata_verify"],
                "initial_decision": "recommend" if label == "G195(B067)" else "alternative",
            }
        )
    return rows


def build_story_support(data: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for hazard in ["drought", "heat", "hotdry"]:
        delta = one(data["b067_delta"], hazard=hazard)
        p25 = one(data["b067_te"], hazard=hazard, ca_level="P25")
        p75 = one(data["b067_te"], hazard=hazard, ca_level="P75")
        rows.append(
            {
                "story_id": "S1",
                "story": "high-SR stress-loss attenuation",
                "scale": "G195(B067)",
                "result_domain": "TE delta",
                "hazard": hazard,
                "core_or_secondary": "core",
                "estimate": delta.get("pct_delta_point_percent", ""),
                "ci_low": delta.get("pct_delta_ci_lo_percent", ""),
                "ci_high": delta.get("pct_delta_ci_hi_percent", ""),
                "support_sentence": f"{hazard}: TE P25={fmt(p25.get('estimate'))}, P75={fmt(p75.get('estimate'))}, P75-P25={pct(delta.get('pct_delta_point_percent'))}.",
                "counter_result": "heat TE level crosses zero" if hazard == "heat" else "",
                "explanation_strategy": "interpret delta as high-stress association contrast, not average treatment effect",
            }
        )
    for hazard in ["drought", "heat", "hotdry"]:
        base = one(data["rep_baseline"], sample_id="G195", hazard=hazard)
        rows.append(
            {
                "story_id": "S1",
                "story": "high-SR stress-loss attenuation",
                "scale": "G195",
                "result_domain": "baseline decomposition",
                "hazard": hazard,
                "core_or_secondary": "secondary",
                "estimate": base.get("te_slope", ""),
                "ci_low": "",
                "ci_high": "",
                "support_sentence": f"{hazard}: c3={fmt(base.get('c3'))} (p={fmt(base.get('c3_p'))}), te_slope={fmt(base.get('te_slope'))}.",
                "counter_result": "heat a3 is not significant" if hazard == "heat" else "",
                "explanation_strategy": "separate heat buffering from current root-zone soil moisture channel",
            }
        )
    for hazard in ["drought", "heat", "hotdry"]:
        irr = one(data["rep_irrigation"], sample_id="G195", hazard=hazard)
        rows.append(
            {
                "story_id": "S2",
                "story": "irrigation boundary",
                "scale": "G195",
                "result_domain": "continuous irrigation triple",
                "hazard": hazard,
                "core_or_secondary": "core" if hazard == "heat" else "secondary",
                "estimate": irr.get("triple", ""),
                "ci_low": "",
                "ci_high": "",
                "support_sentence": f"{hazard}: SR x hazard x irr triple={fmt(irr.get('triple'))} (p={fmt(irr.get('triple_p'))}).",
                "counter_result": "drought and hotdry triples are not conventionally significant" if hazard in {"drought", "hotdry"} else "",
                "explanation_strategy": "write heat as core boundary; drought/hotdry as directional or appendix",
            }
        )
    for window in ["hepm10", "hema", "v3he", "full"]:
        ph = one(data["rep_phenology"], sample_id="G195", window=window)
        rows.append(
            {
                "story_id": "S3",
                "story": "phenology-windowed compound buffering",
                "scale": "G195",
                "result_domain": "D x H and SR x D x H by window",
                "hazard": window,
                "core_or_secondary": "core" if window == "hepm10" else "secondary",
                "estimate": ph.get("gamma_SRDH", ""),
                "ci_low": "",
                "ci_high": "",
                "support_sentence": f"{window}: D x H={fmt(ph.get('beta_DH'))} (p={fmt(ph.get('beta_DH_p'))}), SR x D x H={fmt(ph.get('gamma_SRDH'))} (p={fmt(ph.get('gamma_SRDH_p'))}).",
                "counter_result": "full-season D x H is not negative/significant" if window == "full" else "V3-HE has opposite SR x D x H direction" if window == "v3he" else "",
                "explanation_strategy": "make the claim phenology-windowed, not full-season",
            }
        )
    return rows


def make_literature_support(data: dict[str, list[dict[str, str]]]) -> tuple[str, list[dict[str, str]]]:
    groups = [
        (
            "状态依赖的气候风险缓冲",
            ["adaptation_region", "water_mediated_buffering", "climate"],
            "中文可写句：秸秆还田不应被写作普遍增产技术，而应被写作在高风险状态下改变损失斜率的条件性管理。英文可写句：The value of SR is best framed as state-dependent buffering under climate stress rather than a uniform yield gain.",
        ),
        (
            "水分和热旱耦合",
            ["water_mediated_buffering", "soil moisture", "dryness"],
            "中文可写句：水分状态可以解释部分 drought/hot-dry 损失结构，但 heat 不应被简化为单一根区土壤水分机制。英文可写句：Soil-water state provides a mechanism-consistent explanation for drought and hot-dry losses, while heat responses should be treated as stress-specific.",
        ),
        (
            "物候期窗口",
            ["maize yield", "growing season", "phenology"],
            "中文可写句：复合热旱的可写窗口应收窄到抽雄前后和生殖期，而不是全年平均响应面。英文可写句：The compound-stress claim is strongest when anchored to phenology windows rather than the full growing season.",
        ),
        (
            "灌溉边界条件",
            ["irrigation", "water", "heat"],
            "中文可写句：灌溉不是简单的控制变量，而是决定 SR 边际缓冲空间的管理背景。英文可写句：Irrigation should be treated as a boundary condition that changes the marginal buffering space associated with SR.",
        ),
        (
            "保护性管理的边界和取舍",
            ["conservation_agriculture_sr", "boundary_or_tradeoff", "conservation"],
            "中文可写句：保护性管理的强结论应落在适用条件和风险边界上，而不是无条件收益。英文可写句：The contribution is a bounded targeting rule for conservation management, not a universal-benefit claim.",
        ),
    ]
    source_rows: list[dict[str, str]] = []
    lines = ["# Zotero Literature Support", ""]
    for label, terms, sentence in groups:
        picked = lit_pick(data, terms, limit=5)
        lines.extend([f"## {label}", "", sentence, "", "| item_key | citation_key | year | journal | DOI | title |", "|---|---|---:|---|---|---|"])
        for item in picked:
            source_rows.append({"claim_type": label, **item})
            lines.append(
                f"| {item['item_key']} | {item['citation_key']} | {item['year']} | {item['journal']} | {item['doi']} | {item['title']} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Unsafe Sentences",
            "",
            "- 不写 `SR causally mitigates climate losses`。",
            "- 不写 `TE/IE/DE proves soil-moisture mediation`。",
            "- 不写 `SR works best in one region`，除非同一 single scale 的 region 结果被放入主文并经过多重检验处理。",
            "- 不把 `ca` 直接等同于 no-till、residue retention 或完整 conservation agriculture package。",
        ]
    )
    return "\n".join(lines), source_rows


def make_candidate_cards_md(candidate_rows: list[dict[str, object]]) -> str:
    lines = ["# Candidate Scale Story Cards", ""]
    for row in candidate_rows:
        label = str(row["candidate_scale"])
        if label == "G195(B067)":
            story = (
                "该 scale 能讲的故事是：在一个主样本、核心作物区并具有 SR within-grid variation 的数据版本中，"
                "较高 SR 与高胁迫下更小的产量损失相关；该结论由 TE delta、baseline decomposition、灌溉边界和物候窗口共同支撑。"
                "它的代价是 region-first 不强，因此区域差异只能作为边界或 appendix，不能成为总主线。"
            )
        elif label == "G255":
            story = (
                "该 scale 能讲的故事是：在更严格样本规则下，stress-loss attenuation 和 HE±10 物候窗口仍存在，"
                "并且 region_score 更高。它的代价是没有 B067 级别的 TE/IE/DE bootstrap，部分 phenology 和 irrigation 结果较弱。"
            )
        elif label in {"G185", "G057"}:
            story = (
                "该 scale 能讲的故事是：SR 相关缓冲对象具有 region-first 分化，适合讲区域定向管理。"
                "它的代价是不能承载 TE/IE/DE 主评价，也缺少 zone_core 和 sr_within 规则，因此不适合作为唯一数据版本。"
            )
        else:
            story = (
                "该 scale 适合作为敏感性或探索范围，不能替代唯一数据版本；它的价值是解释为什么最终 scale 选择不是单一结果导向。"
            )
        lines.extend(
            [
                f"## {label}",
                "",
                f"**定位：** {row['role']}。",
                "",
                f"**样本：** {row['N_sample']}；main_sample={row['main_sample']}；zone_core={row['zone_core']}；sr_within={row['sr_within']}。",
                "",
                f"**结果域覆盖：** baseline={row['baseline']}，region={row['region']}，irrigation={row['irrigation']}，phenology={row['phenology']}，TE/IE/DE={row['te_iede']}，Stata verify={row['stata_verify']}。",
                "",
                f"**完整故事：** {story}",
                "",
                f"**初始判定：** {row['initial_decision']}。",
                "",
            ]
        )
    return "\n".join(lines)


def make_recommendation_md(candidate_rows: list[dict[str, object]]) -> str:
    lines = [
        "# Single Scale Recommendation",
        "",
        "## Recommended single scale",
        "",
        "`G195(B067)`。这里的含义是：用 B067/G195 这一版样本作为唯一主数据版本；B067 承载既有 TE/IE/DE bootstrap，G195 是同一口径在 G-code scale search 中的对应标签。主文不得再把 G057/G185 的 region-first 结果混入主结果，只能在 appendix 作为为何没有采用 region-first scale 的选择过程说明。",
        "",
        "## 判定理由",
        "",
        "第一，`G195(B067)` 同时满足 `main_sample=1`, `zone_core=1`, `sr_within=1`，比 G057/G185 更适合回答“同一数据版本下 SR 变化与高胁迫产量损失斜率”的问题。",
        "",
        "第二，用户关心的 TE/IE/DE 评价只在 B067 上已经有 1000 次 bootstrap 的完整输出；若选择 G185/G057，就必须放弃这个评价体系或新增重估。",
        "",
        "第三，`G195` 上还有 representative baseline、continuous irrigation triple、phenology D×H/SR×D×H 结果，可在同一数据版本内支撑多条结论。",
        "",
        "第四，代价是 region-first 不再是主线。这个代价可以接受，因为本轮约束是只能采用一版数据，而 region-first scale 与 TE/IE/DE scale 的目标函数不同；强行混用会比放弃 region-first 更容易被审稿人攻击。",
        "",
        "## 其他 scale 不作为唯一主数据版本的原因",
        "",
        "| scale | 不选为唯一数据版本的原因 | 可保留用途 |",
        "|---|---|---|",
    ]
    reasons = {
        "G255": ("严格规则更强，region_score 也可用，但没有 B067 级别的 TE/IE/DE bootstrap；HEMA 和 irrigation 支持弱。", "appendix strict sensitivity"),
        "G256": ("比 G255 更窄，样本进一步收缩，适合作为端点边界而不是主文。", "appendix endpoint"),
        "G185": ("region-first 主表较强，但没有 zone_core/sr_within，不能承载 TE/IE/DE 主评价。", "appendix region-first alternative"),
        "G057": ("region-first 展示最强，但不是 main_sample，且来自 scale search winner。", "appendix/display-only sensitivity"),
        "G049/G177": ("near-twin 作用是说明 region-first 不是单一偶然，不能作为主 scale。", "appendix near-twin"),
        "broad G001/G009/G017/G033": ("宽口径探索 scale，没有足够样本规则约束。", "exploratory appendix"),
    }
    for row in candidate_rows:
        label = str(row["candidate_scale"])
        if label == "G195(B067)":
            continue
        reason, use = reasons.get(label, ("不适合作为唯一主数据版本。", "appendix"))
        lines.append(f"| `{label}` | {reason} | {use} |")
    lines.extend(
        [
            "",
            "## 不得写",
            "",
            "- 不写 `G195(B067) proves the region-first story`。",
            "- 不写 `SR has a causal mediation effect through soil moisture`。",
            "- 不写 `SR universally increases maize yield`。",
            "- 不写 `full-season compound heat-drought buffering is robust`。",
        ]
    )
    return "\n".join(lines)


def make_story_pack_md(data: dict[str, list[dict[str, str]]], support_rows: list[dict[str, str]]) -> str:
    by_story: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in support_rows:
        by_story[row["story_id"]].append(row)

    s1 = "\n".join([f"- {r['support_sentence']} Counter: {r['counter_result'] or 'NA'}" for r in by_story["S1"]])
    s2 = "\n".join([f"- {r['support_sentence']} Counter: {r['counter_result'] or 'NA'}" for r in by_story["S2"]])
    s3 = "\n".join([f"- {r['support_sentence']} Counter: {r['counter_result'] or 'NA'}" for r in by_story["S3"]])

    return f"""
# Single Scale Story Pack: G195(B067)

## 总主线

在同一个 `G195(B067)` 数据版本中，SR 不适合被写成无条件增产技术，而更适合被写成一种 `state-dependent buffering`：较高 SR 与高胁迫状态下更平缓的 stress-yield loss slope 相关；这种关联在 drought、heat 和 hotdry 的 TE delta 中同时出现，但对应的机制和边界不同。

英文 take-home sentence：Using a single conservative crop-core scale, SR is best interpreted as a state-dependent buffer that flattens high-stress yield-loss slopes rather than as a uniform yield-enhancing treatment.

## Story 1: 高 SR 对高胁迫损失斜率的削弱

**可写结论：** 在 `G195(B067)` 中，SR 从 P25 到 P75 的变化对应 P90 drought、heat 和 hotdry 情景下 TE 均向减损方向移动；这支持“高胁迫下的 slope flattening”，但不支持“平均状态下普遍增产”。

**中文结果句：** 在 B067 口径下，SR P75 相对 SR P25 的 TE 差值在 drought、heat 和 hotdry 下均为正，说明高 SR 与高胁迫损失减弱相关。

**英文结果句：** At the B067/G195 scale, the P75-minus-P25 TE contrast is positive under P90 drought, heat, and hot-dry exposure, indicating an attenuation of high-stress yield losses at higher SR.

**结果支持：**

{s1}

**解释边界：** heat 的 TE level 跨零，因此 heat 的相对减损比例只能用于描述点估计，不能作为强 magnitude claim；主文应优先报告 TE delta 和 CI。

## Story 2: 灌溉是 SR 边际缓冲空间的边界条件

**可写结论：** 在 `G195` 中，heat 的 `SR × heat × irr_frac` 为负且显著，说明灌溉较高时 SR 的额外 heat-buffering association 变小；drought 和 hotdry 的连续灌溉三重项不稳定，因此不能写成通用的 SR-灌溉替代关系。

**中文结果句：** 灌溉异质性最稳的可写结论是 heat 边界：高灌溉条件下，SR 对 heat loss 的额外缓冲空间收缩。

**英文结果句：** The clearest irrigation boundary is observed for heat: higher irrigation is associated with a smaller additional SR-related heat-buffering margin.

**结果支持：**

{s2}

**解释边界：** drought 的三重项方向为正但 p 值不足，适合写成方向性互补或 appendix，不应写成稳定协同。

## Story 3: 联合热旱结论应限定到物候期窗口

**可写结论：** `G195` 的 full-season D×H 不支持强结论，但 HE±10 和 HE-MA 显示更清晰的负 D×H 与正 SR×D×H 结构；因此联合热旱故事必须写成物候期定位，而不是全年响应面。

**中文结果句：** 联合热旱缓冲的可写窗口集中在 HE±10，并可弱写 HE-MA；full-season 结果是边界条件，不是主结果。

**英文结果句：** The compound hot-dry buffering claim should be anchored to phenology windows, especially HE±10, rather than to the full-season specification.

**结果支持：**

{s3}

**解释边界：** V3-HE 的 SR×D×H 方向相反，说明早期窗口不能被纳入同一个强结论。

## Story 4: 机制只能写 stress-specific association decomposition

**可写结论：** drought 和 hotdry 的 IE 结果更接近土壤水分通道一致性，heat 不应被写成同一根区土壤水分机制；因此机制部分应写成 stress-specific association decomposition。

**中文结果句：** TE/IE/DE 的价值不是证明因果中介，而是说明不同胁迫下 SR 相关缓冲的组成不同。

**英文结果句：** The IE/DE/TE decomposition is useful as a stress-specific association decomposition, not as evidence of causal soil-moisture mediation.

## 图表安排

1. `fig_g195_te_delta.png`：主图，展示 drought/heat/hotdry 的 TE(P75-P25) 和 bootstrap CI。
2. `fig_g195_te_levels.png`：支撑图，展示 P25/P50/P75 下 TE level。
3. `fig_g195_irrigation_triples.png`：边界图，展示 continuous irrigation triple。
4. `fig_g195_phenology_compound.png`：物候图，展示不同窗口的 D×H 与 SR×D×H。

## 不能进入主文的内容

`G057/G185` 的 region-first 结果不能进入主文主结果，因为它不是同一数据版本；可以在 appendix 说明“如果优先寻找区域异质性，会得到另一组结果，但本研究最终选择保留 TE/IE/DE 可解释性更强的 conservative crop-core scale”。
"""


def make_figures(data: dict[str, list[dict[str, str]]]) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        write_text(RUN_DIR / "figure_status.txt", f"matplotlib unavailable: {exc}")
        return

    hazards = ["drought", "heat", "hotdry"]
    deltas = [n(one(data["b067_delta"], hazard=h).get("pct_delta_point_percent"), 0) or 0 for h in hazards]
    lo = [n(one(data["b067_delta"], hazard=h).get("pct_delta_ci_lo_percent"), 0) or 0 for h in hazards]
    hi = [n(one(data["b067_delta"], hazard=h).get("pct_delta_ci_hi_percent"), 0) or 0 for h in hazards]
    yerr = [[d - l for d, l in zip(deltas, lo)], [h - d for h, d in zip(hi, deltas)]]
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.bar(hazards, deltas, yerr=yerr, capsize=4, color=["#4C78A8", "#F58518", "#54A24B"])
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("TE(P75) - TE(P25), percentage points")
    ax.set_title("G195(B067): high-SR attenuation of P90 stress losses")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_g195_te_delta.png", dpi=300)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    levels = ["P25", "P50", "P75"]
    for hazard in hazards:
        values = [n(one(data["b067_te"], hazard=hazard, ca_level=level).get("estimate"), 0) or 0 for level in levels]
        ax.plot(levels, values, marker="o", label=hazard)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("TE estimate")
    ax.set_title("G195(B067): TE levels by SR quantile")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_g195_te_levels.png", dpi=300)
    plt.close(fig)

    irr_rows = [one(data["rep_irrigation"], sample_id="G195", hazard=h) for h in hazards]
    triples = [n(row.get("triple"), 0) or 0 for row in irr_rows]
    pvals = [n(row.get("triple_p"), 1) or 1 for row in irr_rows]
    colors = ["#4C78A8" if p <= 0.1 else "#BAB0AC" for p in pvals]
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.bar(hazards, triples, color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("SR x hazard x irr_frac")
    ax.set_title("G195: irrigation as a boundary condition")
    for i, p in enumerate(pvals):
        ax.text(i, triples[i], f"p={p:.3g}", ha="center", va="bottom" if triples[i] >= 0 else "top")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_g195_irrigation_triples.png", dpi=300)
    plt.close(fig)

    windows = ["hepm10", "hema", "v3he", "full"]
    beta = [n(one(data["rep_phenology"], sample_id="G195", window=w).get("beta_DH"), 0) or 0 for w in windows]
    gamma = [n(one(data["rep_phenology"], sample_id="G195", window=w).get("gamma_SRDH"), 0) or 0 for w in windows]
    xs = range(len(windows))
    width = 0.38
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar([x - width / 2 for x in xs], beta, width=width, label="D x H", color="#E45756")
    ax.bar([x + width / 2 for x in xs], gamma, width=width, label="SR x D x H", color="#54A24B")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(list(xs))
    ax.set_xticklabels(windows)
    ax.set_ylabel("Coefficient")
    ax.set_title("G195: compound stress is phenology-windowed")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_g195_phenology_compound.png", dpi=300)
    plt.close(fig)

    write_text(RUN_DIR / "figure_status.txt", "Figures generated successfully.")


# ---------------------------------------------------------------------------
# G185 single-scale override
#
# The earlier draft in this file was written before the first sub-agent round
# converged on G185.  The definitions below intentionally shadow the draft
# functions above so `main()` emits one coherent G185-centered package while
# preserving the older exploratory code for traceability.


def make_candidate_cards(data: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    scale_info = by_key(data["scale_cards"], "candidate_scale")
    desc_info = by_key(data["scale_desc"], "scale")
    verify_scales = {row.get("scale", "") for row in data["stata_verify"] if row.get("scale")}
    b067_has_te = bool(data["b067_delta"] or data["b067_iede"] or data["b067_te"])

    ordered = ["G185", "G057", "B067", "G195", "G255", "G256"]
    roles = {
        "G185": "recommended single-scale main-sample version",
        "G057": "region-first sensitivity scale",
        "B067": "legacy TE/IE/DE appendix evidence",
        "G195": "legacy TE/IE/DE and phenology appendix evidence",
        "G255": "strict-support appendix evidence",
        "G256": "strict-support appendix evidence",
    }
    decisions = {
        "G185": "recommend",
        "G057": "sensitivity_only",
        "B067": "appendix_only",
        "G195": "appendix_only",
        "G255": "appendix_only",
        "G256": "appendix_only",
    }

    rows: list[dict[str, object]] = []
    for scale in ordered:
        info = scale_info.get(scale, {})
        desc = desc_info.get(scale, {})
        domains = {
            "baseline": "yes" if rows_where(data["stata_verify"], scale=scale, model="baseline") else ("yes" if scale in scale_info else "no"),
            "region": "yes" if rows_where(data["region_details"], sample_id=scale) else "no",
            "irrigation": "yes" if rows_where(data["irrigation_margins"], scale=scale) else ("yes" if rows_where(data["stata_verify"], scale=scale, model="irrigation") else "no"),
            "phenology": "yes" if rows_where(data["phenology_margins"], scale=scale) else "no",
            "te_iede": "yes" if scale == "B067" and b067_has_te else "no",
            "stata_verify": "yes" if scale in verify_scales else "no",
        }
        rows.append(
            {
                "candidate_scale": scale,
                "role": roles[scale],
                "N_sample": desc.get("N_sample") or info.get("N_sample") or "",
                "main_sample": desc.get("main_sample") or info.get("main_sample") or ("1" if scale == "G185" else ""),
                "zone_core": desc.get("zone_core") or info.get("zone_core") or "",
                "sr_within": desc.get("sr_within") or info.get("sr_within") or "",
                "domain_count": sum(1 for value in domains.values() if value == "yes"),
                **domains,
                "initial_decision": decisions[scale],
            }
        )
    return rows


def build_story_support(data: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    def add(
        story_id: str,
        story: str,
        scale: str,
        result_domain: str,
        hazard: str,
        core_or_secondary: str,
        estimate: object = "",
        ci_low: object = "",
        ci_high: object = "",
        support_sentence: str = "",
        counter_result: str = "",
        explanation_strategy: str = "",
    ) -> None:
        rows.append(
            {
                "story_id": story_id,
                "story": story,
                "scale": scale,
                "result_domain": result_domain,
                "hazard": hazard,
                "core_or_secondary": core_or_secondary,
                "estimate": "" if estimate is None else str(estimate),
                "ci_low": "" if ci_low is None else str(ci_low),
                "ci_high": "" if ci_high is None else str(ci_high),
                "support_sentence": support_sentence,
                "counter_result": counter_result,
                "explanation_strategy": explanation_strategy,
            }
        )

    region_rows = rows_where(data["region_details"], sample_id="G185")
    core_region = {
        ("NE", "drought"): "core",
        ("HHH", "heat"): "core",
        ("HHH", "hotdry"): "core",
    }
    for row in region_rows:
        region = row.get("region", "")
        hazard = row.get("hazard", "")
        if not region or not hazard:
            continue
        support = n(row.get("scaled_buffer"))
        pvalue = n(row.get("pvalue"))
        label = core_region.get((region, hazard), "secondary")
        if pvalue is not None and pvalue >= 0.1:
            label = "boundary"
        add(
            "S1",
            "regional_constraint_matching",
            "G185",
            "region_hazard",
            f"{region}-{hazard}",
            label,
            pct(support * 100 if support is not None else None),
            support_sentence=(
                f"G185 中 {region}-{hazard} 的 SR 相关缓冲幅度为 {pct(support * 100 if support is not None else None)}"
                f"，p={fmt(pvalue, 3)}；该结果用于表达风险类型随区域重新分配。"
            ),
            counter_result="NW、SW 或 SH 的部分 hazard 不显著，不能写成所有地区均存在缓冲。",
            explanation_strategy="把 region 作为风险约束条件，而不是把所有区域排序成固定优劣。",
        )

    for hazard in ["drought", "heat", "hotdry"]:
        hazard_rows = rows_where(data["irrigation_margins"], scale="G185", hazard=hazard)
        by_level = {row.get("irr_level"): row for row in hazard_rows}
        p25 = by_level.get("P25", {})
        p75 = by_level.get("P75", {})
        delta = by_level.get("P75_minus_P25", {})
        p25_val = n(p25.get("pct_yield_buffer_at_hazard_p90"))
        p75_val = n(p75.get("pct_yield_buffer_at_hazard_p90"))
        delta_val = n(delta.get("pct_yield_buffer_at_hazard_p90"))
        triple = n(delta.get("triple_coef"))
        pvalue = n(delta.get("triple_pvalue"))
        level = "core" if hazard in ["heat", "hotdry"] else "secondary"
        if hazard == "drought":
            level = "suggestive" if pvalue is None or pvalue >= 0.05 else "secondary"
        add(
            "S2",
            "irrigation_boundary",
            "G185",
            "irrigation_margin",
            hazard,
            level,
            pct(delta_val),
            support_sentence=(
                f"{hazard} 在灌溉 P25 与 P75 之间的 P90 hazard 缓冲差为 {pct(delta_val)}"
                f"（P25={pct(p25_val)}, P75={pct(p75_val)}, triple={fmt(triple, 4)}, p={fmt(pvalue, 3)}）。"
            ),
            counter_result="drought 的灌溉异质性只达到弱显著，不能作为主结论。",
            explanation_strategy="将 irrigation 写为 heat/hot-dry 边界条件；drought 只作为补充说明。",
        )

    for window in ["hepm10", "hema"]:
        win_rows = rows_where(data["phenology_margins"], scale="G185", window=window)
        if not win_rows:
            continue
        by_level = {row.get("ca_level"): row for row in win_rows}
        p25 = by_level.get("P25", {})
        p75 = by_level.get("P75", {})
        delta = by_level.get("P75_minus_P25", {})
        beta = n(p25.get("beta_DH"))
        beta_p = n(p25.get("beta_DH_pvalue"))
        gamma = n(p25.get("gamma_SRDH"))
        gamma_p = n(p25.get("gamma_SRDH_pvalue"))
        shift = n(delta.get("dh_slope_at_ca"))
        add(
            "S3",
            "phenology_windowed_compound_buffer",
            "G185",
            "phenology_srdh_margin",
            window,
            "core" if window in ["hepm10", "hema"] else "secondary",
            fmt(shift, 4),
            support_sentence=(
                f"G185 的 {window} 窗口中，D×H 基准斜率为 {fmt(beta, 4)}（p={fmt(beta_p, 3)}），"
                f"SR×D×H 为 {fmt(gamma, 4)}（p={fmt(gamma_p, 3)}），P75-P25 斜率变化为 {fmt(shift, 4)}。"
            ),
            counter_result="该证据来自特定物候窗口，不能替代全季节平均结论。",
            explanation_strategy="把物候期作为机制窗口和锦上添花证据，而不是主版本筛选标准。",
        )

    for row in rows_where(data["stata_verify"], scale="G185"):
        model = row.get("model", "")
        hazard = row.get("hazard", "")
        if model == "baseline":
            add(
                "S4",
                "verified_single_scale_main_effect",
                "G185",
                "stata_python_verify_baseline",
                hazard,
                "core",
                row.get("stata_coef"),
                support_sentence=(
                    f"G185 baseline {hazard} 的 Stata 复核系数为 {fmt(row.get('stata_coef'), 4)}，"
                    f"p={fmt(row.get('stata_pvalue'), 3)}，Stata/Python 系数差为 {fmt(row.get('coef_diff'), 3)}。"
                ),
                counter_result="baseline 只说明 SR 与 hazard 斜率相关，不能直接说明 TE/IE/DE。",
                explanation_strategy="作为单版本可信度证据，不单独构成机制结论。",
            )
        elif model == "irrigation":
            add(
                "S4",
                "verified_single_scale_irrigation",
                "G185",
                "stata_python_verify_irrigation",
                hazard,
                "secondary" if hazard == "drought" else "core",
                row.get("stata_coef"),
                support_sentence=(
                    f"G185 irrigation {hazard} triple 的 Stata 复核系数为 {fmt(row.get('stata_coef'), 4)}，"
                    f"p={fmt(row.get('stata_pvalue'), 3)}。"
                ),
                counter_result="drought triple p≈0.09，不能写成确定性的灌溉互补。",
                explanation_strategy="Stata 复核用于保护 heat/hot-dry irrigation boundary 结论。",
            )

    for row in data["b067_delta"]:
        effect_type = row.get("effect_type", "")
        add(
            "S5",
            "legacy_te_iede_appendix",
            "B067",
            "te_iede_delta",
            effect_type,
            "appendix_only",
            row.get("p75_minus_p25"),
            support_sentence=(
                f"B067 {effect_type} 的 P75-P25 差异为 {fmt(row.get('p75_minus_p25'), 4)}；"
                "该结果只能作为 TE/IE/DE 探索性附录。"
            ),
            counter_result="B067 不是本轮推荐的单版本主 scale，不能与 G185 主文结果混用。",
            explanation_strategy="若需要讨论 TE/IE/DE，可明确标注为 legacy appendix，不作为中心贡献。",
        )

    return rows


def make_candidate_cards_md(candidate_rows: list[dict[str, object]]) -> str:
    lines = [
        "# Candidate scale story cards",
        "",
        "本轮按“只能采纳一版数据”的约束排序。排序标准不是单项显著性最多，而是同一 scale 是否同时承载 region、irrigation、phenology、Stata 复核和主样本解释。",
        "",
        "| scale | role | decision | domains | N | main_sample | comment |",
        "|---|---|---|---:|---:|---|---|",
    ]
    comments = {
        "G185": "推荐作为唯一主版本；region-first 结构接近 G057，同时具备 main_sample=1、baseline/irrigation Stata 复核和物候期承载。",
        "G057": "region-first 最强敏感性版本；可放 appendix 或 robustness，但不宜与 G185 混合成主文。",
        "B067": "有 TE/IE/DE 结果，但不适合作为主版本；只能用于说明旧机制探索或附录。",
        "G195": "可支持部分 legacy 机制和物候结果，但单版本综合性弱于 G185。",
        "G255": "严格支持版本，适合展示边界和稳健性，不建议作为主故事版本。",
        "G256": "严格支持版本，适合展示边界和稳健性，不建议作为主故事版本。",
    }
    for row in candidate_rows:
        scale = str(row["candidate_scale"])
        lines.append(
            f"| {scale} | {row['role']} | {row['initial_decision']} | {row['domain_count']} | "
            f"{row.get('N_sample', '')} | {row.get('main_sample', '')} | {comments.get(scale, '')} |"
        )
    return "\n".join(lines)


def make_recommendation_md(candidate_rows: list[dict[str, object]]) -> str:
    g185 = next(row for row in candidate_rows if row["candidate_scale"] == "G185")
    return f"""
# Single scale recommendation

## Recommendation

本轮建议将 `G185` 作为唯一主版本。该选择不是因为 `G185` 在所有单项指标上都排名第一，而是因为它在“单版本论文故事”约束下同时满足四个条件：第一，`main_sample=1`，样本口径更容易向审稿人解释；第二，保留了 region-first 的核心格局；第三，baseline 和 irrigation 已有 Stata/Python 复核；第四，同一 scale 内可以承载 region、irrigation 和 phenology 三组结果。

`G185` 的候选卡片字段为：N={g185.get('N_sample', '')}，domain_count={g185.get('domain_count', '')}，region={g185.get('region', '')}，irrigation={g185.get('irrigation', '')}，phenology={g185.get('phenology', '')}，stata_verify={g185.get('stata_verify', '')}。

## Main claim that G185 can support

SR 相关缓冲不适合写成全国统一的平均增产结论，更适合写成“区域风险类型约束下的状态依赖型损失斜率缓冲”：在同一 G185 数据版本中，区域维度显示不同玉米区对应不同主导 hazard，灌溉维度显示 heat/hot-dry 缓冲空间在高灌溉条件下收缩，物候维度显示 compound stress 的斜率缓冲集中在 HE±10 和 HE-MA 窗口。

## What must not be done

不得把 `B067` 的 TE/IE/DE 结果混入 `G185` 主文结果后写成同一套主结论。若保留 TE/IE/DE，只能作为 appendix 或 exploratory mechanism，且必须明确它来自旧 scale。不得写 “SR universally increases maize yield” 或 “SR causally mediates climate stress through soil moisture”。当前可写的是 conditional association、state-dependent buffering 和 regionally targeted association。

## Minimal additional checks

1. 对 `G185` 的 region × hazard 家族做 pooled Wald 或 Holm/FDR 调整，目标是证明 region-first 图不是单点挑选。
2. 对 `G185` irrigation 与 phenology 的核心 margin 做 overlap/support 和 cluster CI 检查，目标是保护 heat/hot-dry irrigation boundary 与 HE-window conclusion。
""".strip()


def make_story_pack_md(data: dict[str, list[dict[str, str]]], support_rows: list[dict[str, str]]) -> str:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in support_rows:
        grouped[row["story_id"]].append(row)

    def bullet_rows(story_id: str, keep: set[str] | None = None) -> list[str]:
        out = []
        for row in grouped.get(story_id, []):
            if keep is not None and row.get("core_or_secondary") not in keep:
                continue
            out.append(f"- {row['support_sentence']}")
        return out or ["- 当前没有可写入主文的支持结果。"]

    lines = [
        "# G185 single-scale story pack",
        "",
        "## Overall story",
        "",
        "在只能采纳一版数据的约束下，`G185` 最适合承载当前论文主线。可写的中心结论不是“SR 在所有地方都提高产量”，而是“SR 相关缓冲表现为区域风险类型约束下的状态依赖型损失斜率关联”。这个表述能够同时容纳三个事实：不同区域对应不同主导 hazard；灌溉条件改变 heat/hot-dry 缓冲空间；compound stress 的斜率变化在关键物候窗口更清楚。",
        "",
        "English take-home sentence: `Straw-return-associated buffering is not a spatially uniform yield gain; in the G185 main-sample version, it appears as a regionally targeted and state-dependent association with climate-damage slopes.`",
        "",
        "中文可用句：`秸秆还田相关缓冲并非全国一致的平均增产效应，而是在不同玉米区随主导水热风险重新配置的条件性损失斜率关联。`",
        "",
        "## Story 1. Regionally targeted stress buffering",
        "",
        "这条故事是主线。G185 中更适合写“不同区域承载不同风险类型”，而不是写“某一个区域绝对最好”。可写的几句话是：东北更清楚地承载 drought buffer，黄淮海更清楚地承载 heat 和 hot-dry buffer，西北或南方的弱结果作为边界条件处理。这样的写法保留 region 差异，但避免把 region 排序写成机制结论。",
        "",
        *bullet_rows("S1", {"core"}),
        "",
        "Safe sentence EN: `The regional heterogeneity is best interpreted as stress-specific targeting: drought buffering is concentrated in the Northeast signal, whereas heat and hot-dry buffering are more visible in the Huang-Huai-Hai signal.`",
        "",
        "Unsafe sentence: `SR works best in Northwest China`，当前结果不能支持这种地域排序。",
        "",
        "## Story 2. Irrigation as a boundary condition",
        "",
        "这条故事适合作为第一支撑线。G185 的 irrigation margin 结果显示，heat 和 hot-dry 的 SR 相关缓冲在低灌溉条件下更大，在高灌溉条件下收缩；drought 的 irrigation 方向只能弱写。它可以解释为什么 SR 不是简单的投入叠加，而是与已有水分管理条件共同决定边际缓冲空间。",
        "",
        *bullet_rows("S2", {"core", "suggestive"}),
        "",
        "Safe sentence EN: `Irrigation acts as a boundary condition rather than a universal amplifier: the marginal SR-associated buffer is larger under low-irrigation heat and hot-dry exposure, while the drought pattern is weaker and should be treated as suggestive.`",
        "",
        "Unsafe sentence: `SR and irrigation are causal complements for all hazards`，当前 G185 只支持 heat/hot-dry 的边界条件，不支持 all-hazard 互补。",
        "",
        "## Story 3. Compound stress buffering is phenology-windowed",
        "",
        "这条故事适合作为第二支撑线或机制线。G185 的 HE±10 与 HE-MA 窗口显示，D×H 的负斜率在较高 SR 下被压平；这可以写成 compound heat-water stress 的窗口化缓冲，而不是把所有物候期都要求显著。V3-HE 若没有同等支持，可作为不稳定窗口或 appendix。",
        "",
        *bullet_rows("S3", {"core"}),
        "",
        "Safe sentence EN: `The compound-stress evidence is temporally localized: in the G185 version, higher SR is associated with a flatter D×H damage slope around HE±10 and HE-MA, indicating a phenology-windowed buffering pattern.`",
        "",
        "Unsafe sentence: `SR buffers compound stress across all phenological stages`，当前结果只能支持特定窗口。",
        "",
        "## Story 4. Single-version credibility",
        "",
        "G185 的优势还在于可复核性。baseline 与 irrigation 的核心系数已有 Stata/Python 对照，主文可以说明所有核心图表使用同一数据版本，其他 scale 只作为 sensitivity 或 appendix。这比把 G057、B067、G195 的局部强项混成一条主线更容易通过方法审查。",
        "",
        *bullet_rows("S4", {"core"}),
        "",
        "## Appendix-only mechanism: TE/IE/DE",
        "",
        "用户原先希望用不同 SR 下的 TE、IE、DE 评价 SR 效果，这个方向可以保留，但在单版本约束下不应进入 G185 主文主线。当前 TE/IE/DE 明确来自 B067 或旧机制结果，因此只能写成 exploratory appendix：它可以说明曾经尝试把 total、indirect 和 direct components 拆开，但不能作为 G185 主结论的证据。",
        "",
        *bullet_rows("S5", {"appendix_only"}),
        "",
        "Safe sentence EN: `The TE/IE/DE decomposition is retained as exploratory appendix evidence because it comes from a legacy B067 scale and is not part of the G185 main-sample story.`",
    ]
    return "\n".join(lines)


def make_figures(data: dict[str, list[dict[str, str]]]) -> None:
    import matplotlib.pyplot as plt

    plt.style.use("default")

    # Figure 1: G185 region-hazard buffer matrix.
    region_rows = rows_where(data["region_details"], sample_id="G185")
    regions = ["NE", "HHH", "NW", "SW", "SH"]
    hazards = ["drought", "heat", "hotdry"]
    values = [[math.nan for _ in hazards] for _ in regions]
    pvals = [["" for _ in hazards] for _ in regions]
    for row in region_rows:
        if row.get("region") in regions and row.get("hazard") in hazards:
            i = regions.index(row["region"])
            j = hazards.index(row["hazard"])
            val = n(row.get("scaled_buffer"))
            values[i][j] = math.nan if val is None else val * 100
            pvals[i][j] = fmt(row.get("pvalue"), 2)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    image = ax.imshow(values, cmap="YlGnBu")
    ax.set_xticks(range(len(hazards)), hazards)
    ax.set_yticks(range(len(regions)), regions)
    ax.set_title("G185 region x hazard SR-associated buffer")
    for i, region in enumerate(regions):
        for j, hazard in enumerate(hazards):
            val = values[i][j]
            if not math.isnan(val):
                ax.text(j, i, f"{val:.2f}%\np={pvals[i][j]}", ha="center", va="center", fontsize=8)
    cbar = fig.colorbar(image, ax=ax)
    cbar.set_label("Scaled buffer (% yield)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_g185_region_hazard_buffer.png", dpi=300)
    plt.close(fig)

    # Figure 2: G185 irrigation margins.
    irr_rows = rows_where(data["irrigation_margins"], scale="G185")
    levels = ["P25", "P50", "P75"]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for hazard in ["drought", "heat", "hotdry"]:
        by_level = {row.get("irr_level"): row for row in irr_rows if row.get("hazard") == hazard}
        y = [n(by_level.get(level, {}).get("pct_yield_buffer_at_hazard_p90")) for level in levels]
        ax.plot(levels, y, marker="o", label=hazard)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("P90 hazard buffer (% yield)")
    ax.set_title("G185 irrigation boundary: standardized margins")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_g185_irrigation_margins.png", dpi=300)
    plt.close(fig)

    # Figure 3: G185 phenology D x H slopes by SR quantile.
    pheno_rows = rows_where(data["phenology_margins"], scale="G185")
    levels = ["P25", "P50", "P75"]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for window in ["hepm10", "hema"]:
        by_level = {row.get("ca_level"): row for row in pheno_rows if row.get("window") == window}
        y = [n(by_level.get(level, {}).get("dh_slope_at_ca")) for level in levels]
        ax.plot(levels, y, marker="o", label=window)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("D x H slope at SR quantile")
    ax.set_title("G185 compound stress slope flattening by phenology window")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_g185_phenology_slopes.png", dpi=300)
    plt.close(fig)

    # Figure 4: candidate scale domain coverage.
    cards = make_candidate_cards(data)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar([str(row["candidate_scale"]) for row in cards], [n(row["domain_count"], 0) for row in cards])
    ax.set_ylabel("Supported result domains")
    ax.set_title("Candidate scale coverage under single-version constraint")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_candidate_scale_domain_coverage.png", dpi=300)
    plt.close(fig)

    # Appendix figure: B067 TE/IE/DE delta, kept separate from G185.
    b067_rows = data["b067_delta"]
    if b067_rows:
        fig, ax = plt.subplots(figsize=(7, 4.5))
        ax.bar([row.get("effect_type", "") for row in b067_rows], [n(row.get("p75_minus_p25"), 0) for row in b067_rows])
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_ylabel("P75 - P25 difference")
        ax.set_title("Appendix only: B067 TE/IE/DE delta")
        fig.tight_layout()
        fig.savefig(FIG_DIR / "fig_appendix_b067_te_iede_delta.png", dpi=300)
        plt.close(fig)

    write_text(
        RUN_DIR / "figure_status.txt",
        "\n".join(
            [
                "Figures generated successfully.",
                "Main figures use G185 only.",
                "B067 TE/IE/DE figure is appendix-only and must not be mixed into the G185 main text.",
            ]
        ),
    )


def main() -> None:
    ensure_dirs()
    data = load_inputs()
    candidate_rows = make_candidate_cards(data)
    support_rows = build_story_support(data)
    lit_md, lit_rows = make_literature_support(data)

    write_csv(
        RUN_DIR / "candidate_scale_story_cards.csv",
        candidate_rows,
        [
            "candidate_scale",
            "role",
            "N_sample",
            "main_sample",
            "zone_core",
            "sr_within",
            "domain_count",
            "baseline",
            "region",
            "irrigation",
            "phenology",
            "te_iede",
            "stata_verify",
            "initial_decision",
        ],
    )
    write_csv(
        RUN_DIR / "story_support_matrix.csv",
        support_rows,
        [
            "story_id",
            "story",
            "scale",
            "result_domain",
            "hazard",
            "core_or_secondary",
            "estimate",
            "ci_low",
            "ci_high",
            "support_sentence",
            "counter_result",
            "explanation_strategy",
        ],
    )
    write_csv(RUN_DIR / "zotero_literature_support.csv", lit_rows, ["claim_type", "item_key", "citation_key", "title", "journal", "year", "doi", "themes"])
    write_text(RUN_DIR / "candidate_scale_story_cards.md", make_candidate_cards_md(candidate_rows))
    write_text(RUN_DIR / "single_scale_recommendation.md", make_recommendation_md(candidate_rows))
    write_text(RUN_DIR / "single_scale_story_pack.md", make_story_pack_md(data, support_rows))
    write_text(RUN_DIR / "zotero_literature_support.md", lit_md)
    make_figures(data)
    print(f"Wrote single-scale story pack to {RUN_DIR}")


if __name__ == "__main__":
    main()
