from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = ROOT / "quality_reports" / "agent_runs" / "2026-06-20_scale_specific_story_pack_v2"
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
        if all(row.get(key) == value for key, value in conds.items()):
            out.append(row)
    return out


def load_inputs() -> dict[str, list[dict[str, str]]]:
    return {
        "scale_cards": read_csv("quality_reports/agent_runs/2026-06-19_scale_story_cards_v2/scale_story_cards.csv"),
        "scale_desc": read_csv("quality_reports/agent_runs/2026-06-19_scale_story_cards_v2/descriptive_story_stats.csv"),
        "region": read_csv("temp/2026-06-18_story_empirical_review_match/selected_region_details.csv"),
        "irrigation": read_csv("temp/2026-06-18_story_followup_margins/irrigation_standardized_margins.csv"),
        "phenology": read_csv("temp/2026-06-18_story_followup_margins/phenology_srdh_margins.csv"),
        "b067_delta": read_csv("temp/2026-06-18_story_followup_margins/b067_iede_delta.csv"),
        "b067_levels": read_csv("temp/2026-06-18_story_followup_margins/b067_iede_levels.csv"),
        "b067_te": read_csv("temp/2026-06-18_story_empirical_review_match/b067_baseline_te_by_sr.csv"),
        "verify": read_csv("temp/2026-06-18_story_stata_verify/stata_python_verify_comparison.csv"),
        "rep_irrigation": read_csv("temp/2026-06-11_expanded_scale_story_search/representative_irrigation_cluster.csv"),
        "rep_phenology": read_csv("temp/2026-06-11_expanded_scale_story_search/representative_phenology_cluster.csv"),
        "rep_baseline": read_csv("temp/2026-06-11_expanded_scale_story_search/representative_baseline_cluster.csv"),
        "rep_compound": read_csv("temp/2026-06-11_expanded_scale_story_search/representative_compound_cluster.csv"),
        "selected_baseline": read_csv("temp/2026-06-11_expanded_scale_story_search/selected_baseline_cluster.csv"),
        "selected_irrigation": read_csv("temp/2026-06-11_expanded_scale_story_search/selected_irrigation_modifier_cluster.csv"),
        "selected_phenology": read_csv("temp/2026-06-11_expanded_scale_story_search/selected_phenology_compound_cluster.csv"),
        "selected_compound": read_csv("temp/2026-06-11_expanded_scale_story_search/selected_compound_cluster.csv"),
        "target_lit": read_csv("temp/2026-06-18_zotero_story_direction/target_journal_relevant_items.csv"),
        "included_lit": read_csv("temp/2026-06-18_zotero_story_direction/included_story_items.csv"),
    }


def scale_order(cards: list[dict[str, str]]) -> list[str]:
    priority = ["G057", "G185", "G049", "G177", "B067", "G195", "G255", "G256", "G001", "G009", "G017", "G033"]
    present = [row.get("scale_id", "") for row in cards if row.get("scale_id")]
    return [scale for scale in priority if scale in present] + [scale for scale in present if scale not in priority]


def by_scale(rows: list[dict[str, str]], key: str = "scale_id") -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in rows if row.get(key)}


def evidence_domains(data: dict[str, list[dict[str, str]]], scale: str) -> dict[str, str]:
    baseline_cluster = bool(rows_where(data["rep_baseline"], sample_id=scale) or rows_where(data["selected_baseline"], sample_id=scale))
    irrigation_cluster = bool(rows_where(data["rep_irrigation"], sample_id=scale) or rows_where(data["selected_irrigation"], sample_id=scale))
    phenology_cluster = bool(rows_where(data["rep_phenology"], sample_id=scale) or rows_where(data["selected_phenology"], sample_id=scale))
    return {
        "region": "yes" if rows_where(data["region"], sample_id=scale) else "no",
        "irrigation_margin": "yes" if rows_where(data["irrigation"], scale=scale) else "no",
        "phenology_margin": "yes" if rows_where(data["phenology"], scale=scale) else "no",
        "stata_verify": "yes" if rows_where(data["verify"], scale=scale) else "no",
        "baseline_cluster": "yes" if baseline_cluster else "no",
        "irrigation_cluster": "yes" if irrigation_cluster else "no",
        "phenology_cluster": "yes" if phenology_cluster else "no",
        "representative_irrigation": "yes" if rows_where(data["rep_irrigation"], sample_id=scale) else "no",
        "representative_phenology": "yes" if rows_where(data["rep_phenology"], sample_id=scale) else "no",
        "te_iede": "yes" if scale == "B067" and (data["b067_delta"] or data["b067_levels"] or data["b067_te"]) else "no",
    }


def classify_placement(card: dict[str, str], domains: dict[str, str]) -> tuple[str, str]:
    scale = card.get("scale_id", "")
    support = card.get("support_level", "")
    placement = card.get("preferred_placement", "")
    if scale in {"G057", "G185"}:
        return support or "moderate", "main_candidate"
    if scale in {"B067", "G195", "G255", "G256", "G049", "G177"}:
        return support or "suggestive", "appendix_or_sensitivity"
    return support or "exploratory", "exploratory_appendix"


def card_claim(scale: str, card: dict[str, str]) -> str:
    name = card.get("story_name", "").strip()
    if name:
        return name
    if scale == "B067":
        return "TE/IE/DE association decomposition under SR quantiles"
    return "scale-specific SR buffering association"


SCALE_NARRATIVES: dict[str, dict[str, str]] = {
    "G057": {
        "story": "G057 可以独立讲成 region-first 展示版：在该口径内，NE 的可写重点是 drought buffering，HHH 的可写重点是 heat/hotdry buffering；irrigation margins 显示 heat/hotdry 的 SR 相关边际缓冲在高灌溉条件下收缩；HE±10 和 HE-MA 显示 D×H 斜率在较高 SR 下向零或正值移动。限制是 main_sample=0、zone_core=0、sr_within=0，因此它更适合展示区域定向格局，而不是作为最保守主样本。",
        "safe_cn": "G057 支持的结论是区域主导胁迫下的条件性损失斜率变化；NE 可写 drought-buffering，HHH 可写 heat/hotdry-buffering；NW 只能写方向性边界；drought irrigation 只能弱写。",
        "safe_en": "At the G057 scale, SR-related buffering is a region-specific association with climate-damage slopes, with NE aligned with drought and HHH aligned with heat or hot-dry exposure.",
    },
    "G185": {
        "story": "G185 可以独立讲成主样本候选版：在 main_sample=1 的口径下，region、irrigation 和 phenology 三类证据都能由同一 scale 承载。可写的中心句是 SR 相关缓冲不是全国统一平均增产，而是在区域主导胁迫、灌溉边界和关键物候窗口中表现为损失斜率变化。限制是 zone_core=0、sr_within=0，且物候和灌溉图仍需正式 CI 或回归表配套。",
        "safe_cn": "G185 支持 current main candidate：NE 侧重 drought，HHH 侧重 heat/hotdry；heat/hotdry 的边际缓冲空间随灌溉提高而收缩；HE±10 与 HE-MA 支持窗口化 D×H 斜率变化。",
        "safe_en": "At the G185 scale, SR-associated buffering is best framed as a current main-candidate association with region-specific stress slopes, irrigation boundaries, and phenology-windowed compound stress.",
    },
    "G049": {
        "story": "G049 是 region/irrigation/phenology 三类证据齐全的 appendix scale。它可以独立讲区域主导胁迫匹配，但因为 main_sample=0、zone_core=0、sr_within=0，只适合 sensitivity，不适合做唯一主版本。",
        "safe_cn": "G049 只能写成 scale-specific sensitivity：区域、灌溉和物候方向可见，但不是确认性主规格。",
        "safe_en": "G049 is a scale-specific sensitivity case with visible region, irrigation, and phenology patterns, not a confirmatory main specification.",
    },
    "G177": {
        "story": "G177 是 main_sample=1 的 near-twin appendix。它可以独立讲区域主导胁迫、heat/hotdry 灌溉边界和 HE±10/HE-MA 物候斜率变化，但缺少 Stata 复核和正式 CI，因此不替代 G185。",
        "safe_cn": "G177 可作为 main-sample sensitivity：三类图表承载齐全，但应放在 appendix 或 robustness。",
        "safe_en": "G177 is a main-sample sensitivity scale with region, irrigation, and phenology evidence, but it should remain appendix-level.",
    },
    "B067": {
        "story": "B067 可以独立讲 TE P75-P25 delta 的机制层故事：在 zone_core=1 且 sr_within=1 的口径下，P90 drought、heat 和 hotdry 的 TE delta 均向减损方向移动。IE/DE 只能作为 channel-consistent association，需要单独表格承载，不能写成因果中介，也不能承担 region-first 或物候主线。",
        "safe_cn": "B067 的主证据是 TE(P75)-TE(P25) delta；IE/DE 只能解释相关结构，不能写成因果中介。",
        "safe_en": "At the B067 scale, the preferred reporting object is the TE P75-minus-P25 contrast; IE/DE components remain association structure, not causal mediation.",
    },
    "G195": {
        "claim": "保守 within-grid appendix bridge",
        "story": "G195 是保守 within-grid appendix bridge。它可以独立讲 baseline stress-response slope buffering、HE±10/HE-MA 窗口和 heat-specific irrigation boundary，但没有 region-first 细节，full-season D×H 不支持，因此不能做主 scale。",
        "safe_cn": "G195 适合作为保守 within-grid appendix，不支持 region-first 主线。",
        "safe_en": "G195 is a conservative within-grid appendix scale for baseline slope and phenology-window evidence, not a region-first main scale.",
    },
    "G255": {
        "story": "G255 是 strict endpoint sensitivity。它保留 main_sample、zone_core 和 sr_within，能说明严格口径下方向仍可见，但灌溉和物候支持弱于主候选，HEMA 基础 D×H 不稳，因此只适合 appendix。",
        "safe_cn": "G255 只能写成 strict-sample appendix 中的方向性参考，不能写成主文中心证据。",
        "safe_en": "G255 should be used as strict-endpoint appendix evidence, not as the central scale.",
    },
    "G256": {
        "story": "G256 是更窄的 strict endpoint boundary。baseline、HE±10/HE-MA 和 heat irrigation boundary 有方向性结果，但 region/margin 明细不足，full-season D×H 与 V3HE 不支持，因此只能是 appendix。",
        "safe_cn": "G256 是严格样本端点边界，不进入主文主线。",
        "safe_en": "G256 is a narrow strict-endpoint boundary scale and should remain appendix-level.",
    },
    "G001": {
        "story": "G001 是 broad exploratory appendix。它没有 main_sample、zone_core、sr_within 和 region-first 细节，只能说明宽口径下 baseline、irrigation 和 phenology 的部分方向仍可见。",
        "safe_cn": "G001 只作为宽口径探索性背景，不进入主文确认性结论。",
        "safe_en": "G001 provides broad-sample exploratory background only.",
    },
    "G009": {
        "story": "G009 是只启用 sm_sd 的 exploratory appendix。它有 selected baseline、irrigation 和 phenology cluster 证据，但没有 region-first 细节，hotdry baseline 不适合写成损失缓冲，因此只能作为探索性边界。",
        "safe_cn": "G009 可写成宽口径探索性证据，但不能讲 region-first 或确认性主结果。",
        "safe_en": "G009 is an exploratory broad-sample scale, not a region-first or confirmatory specification.",
    },
    "G017": {
        "story": "G017 是只启用 yield_jump 的 exploratory appendix。baseline、irrigation 和 HE±10/HE-MA 方向可见，但没有 main_sample、zone_core、sr_within，也没有 region-first 细节，因此不进主文。",
        "safe_cn": "G017 只能作为宽口径 appendix compact evidence。",
        "safe_en": "G017 should remain compact appendix evidence.",
    },
    "G033": {
        "story": "G033 是只启用 yield_domain 的 exploratory appendix。它在 selected cluster 中有 baseline、irrigation 和 phenology 结果，但 region pattern 只有 score 而无可用估计细节，因此不能写区域故事。",
        "safe_cn": "G033 可说明宽口径下部分方向仍在，但不能替代主规格。",
        "safe_en": "G033 is exploratory evidence that some directions persist under weak restrictions, not a main specification.",
    },
}


def summarize_region(data: dict[str, list[dict[str, str]]], scale: str) -> str:
    rows = rows_where(data["region"], sample_id=scale)
    if not rows:
        return ""
    chosen = []
    priority = {("NE", "drought"), ("HHH", "heat"), ("HHH", "hotdry"), ("NW", "hotdry"), ("SW", "hotdry"), ("SH", "hotdry")}
    for row in rows:
        if (row.get("region"), row.get("hazard")) in priority:
            val = n(row.get("scaled_buffer"))
            chosen.append(
                f"{row.get('region')}-{row.get('hazard')}: buffer={pct(val * 100 if val is not None else None)}, p={fmt(row.get('c3_p') or row.get('pvalue'), 3)}, N={row.get('N_model')}"
            )
    return "Region detail: " + "; ".join(chosen)


def summarize_irrigation_margin(data: dict[str, list[dict[str, str]]], scale: str) -> str:
    rows = rows_where(data["irrigation"], scale=scale)
    if not rows:
        return ""
    parts = []
    for hazard in ["drought", "heat", "hotdry"]:
        delta = next((row for row in rows if row.get("hazard") == hazard and row.get("irr_level") == "P75_minus_P25"), {})
        if delta:
            parts.append(
                f"{hazard}: P75-P25={pct(delta.get('pct_yield_buffer_at_hazard_p90'))}, triple={fmt(delta.get('triple'), 4)}, p={fmt(delta.get('triple_p') or delta.get('triple_pvalue'), 3)}"
            )
    return "Irrigation margin: " + "; ".join(parts)


def summarize_phenology_margin(data: dict[str, list[dict[str, str]]], scale: str) -> str:
    rows = rows_where(data["phenology"], scale=scale)
    if not rows:
        return ""
    parts = []
    for window in ["hepm10", "hema"]:
        delta = next((row for row in rows if row.get("window") == window and row.get("ca_level") == "P75_minus_P25"), {})
        p25 = next((row for row in rows if row.get("window") == window and row.get("ca_level") == "P25"), {})
        if delta or p25:
            parts.append(
                f"{window}: D×H={fmt(p25.get('beta_DH'), 4)} (p={fmt(p25.get('beta_DH_p'), 3)}), SR×D×H={fmt(p25.get('gamma_SRDH'), 4)} (p={fmt(p25.get('gamma_SRDH_p'), 3)}), shift={fmt(delta.get('dh_slope_at_ca'), 4)}"
            )
    return "Phenology margin: " + "; ".join(parts)


def summarize_cluster(data: dict[str, list[dict[str, str]]], scale: str, kind: str) -> str:
    rows = scale_rows(data, scale, kind)
    if not rows:
        return ""
    if kind == "baseline":
        parts = [
            f"{row.get('hazard')}: te_slope={fmt(row.get('te_slope'), 4)}, c3={fmt(row.get('c3'), 4)}, p={fmt(row.get('c3_p'), 3)}"
            for row in rows
        ]
        return "Cluster baseline: " + "; ".join(parts)
    if kind == "irrigation":
        parts = [
            f"{row.get('hazard')}: triple={fmt(row.get('triple'), 4)}, p={fmt(row.get('triple_p'), 3)}"
            for row in rows
        ]
        return "Cluster irrigation: " + "; ".join(parts)
    if kind == "phenology":
        parts = [
            f"{row.get('window')}: D×H={fmt(row.get('beta_DH'), 4)} (p={fmt(row.get('beta_DH_p'), 3)}), SR×D×H={fmt(row.get('gamma_SRDH'), 4)} (p={fmt(row.get('gamma_SRDH_p'), 3)})"
            for row in rows
        ]
        return "Cluster phenology: " + "; ".join(parts)
    return ""


def summarize_b067(data: dict[str, list[dict[str, str]]]) -> str:
    if not data["b067_delta"]:
        return ""
    parts = []
    for row in data["b067_delta"]:
        hazard = row.get("hazard") or row.get("effect_type")
        point = row.get("pct_delta_point_percent") or row.get("p75_minus_p25")
        low = row.get("pct_delta_ci_lo_percent")
        high = row.get("pct_delta_ci_hi_percent")
        ci = f" [{pct(low)}, {pct(high)}]" if low and high else ""
        parts.append(f"{hazard}: TE P75-P25={pct(point)}{ci}")
    return "B067 TE delta: " + "; ".join(parts)


def scale_core_results(data: dict[str, list[dict[str, str]]], scale: str, card: dict[str, str]) -> str:
    pieces = [
        summarize_region(data, scale),
        summarize_irrigation_margin(data, scale),
        summarize_phenology_margin(data, scale),
        summarize_cluster(data, scale, "baseline"),
        summarize_cluster(data, scale, "irrigation"),
        summarize_cluster(data, scale, "phenology"),
        summarize_b067(data) if scale == "B067" else "",
    ]
    out = " | ".join(piece for piece in pieces if piece)
    return out or card.get("key_results", "")


def scale_figure_use(scale: str, domains: dict[str, str]) -> str:
    plans = []
    if domains["region"] == "yes":
        plans.append(f"fig_{scale.lower()}_region_hazard_buffer.png")
    if domains["irrigation_margin"] == "yes":
        plans.append(f"fig_{scale.lower()}_irrigation_margins.png")
    if domains["phenology_margin"] == "yes":
        plans.append(f"fig_{scale.lower()}_phenology_slopes.png")
    if domains["te_iede"] == "yes":
        plans.append("fig_b067_te_delta.png")
    if domains["baseline_cluster"] == "yes" or domains["irrigation_cluster"] == "yes" or domains["phenology_cluster"] == "yes":
        plans.append(f"fig_{scale.lower()}_compact_evidence.png")
    if not plans:
        return "No standalone figure; use scale card/table only."
    return "Use only scale-specific figures: " + ", ".join(plans) + "."


def make_story_rows(data: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    cards = by_scale(data["scale_cards"])
    rows: list[dict[str, object]] = []
    for scale in scale_order(data["scale_cards"]):
        card = cards[scale]
        domains = evidence_domains(data, scale)
        support_level, placement = classify_placement(card, domains)
        domain_count = sum(1 for value in domains.values() if value == "yes")
        narrative = SCALE_NARRATIVES.get(scale, {})
        core_results = scale_core_results(data, scale, card)
        rows.append(
            {
                "scale": scale,
                "claim": narrative.get("claim", card_claim(scale, card)),
                "story_paragraph_cn": narrative.get("story", card.get("story_paragraph_cn", "")),
                "safe_sentences_cn": narrative.get("safe_cn", card.get("safe_sentences_cn", "")),
                "safe_sentences_en": narrative.get("safe_en", card.get("safe_sentences_en", "")),
                "N_sample": card.get("N_sample", ""),
                "N_grids_sample": card.get("N_grids_sample", ""),
                "main_sample": card.get("main_sample", ""),
                "zone_core": card.get("zone_core", ""),
                "sr_within": card.get("sr_within", ""),
                "region_score": card.get("region_score", ""),
                "irrigation_score": card.get("irrigation_score", ""),
                "phenology_score": card.get("phenology_score", ""),
                "support_level": support_level,
                "main_text_or_appendix": placement,
                "domain_count": domain_count,
                "domain_region": domains["region"],
                "domain_irrigation_margin": domains["irrigation_margin"],
                "domain_phenology_margin": domains["phenology_margin"],
                "domain_stata_verify": domains["stata_verify"],
                "domain_baseline_cluster": domains["baseline_cluster"],
                "domain_irrigation_cluster": domains["irrigation_cluster"],
                "domain_phenology_cluster": domains["phenology_cluster"],
                "domain_representative_irrigation": domains["representative_irrigation"],
                "domain_representative_phenology": domains["representative_phenology"],
                "domain_te_iede": domains["te_iede"],
                "core_results": core_results,
                "unsupported_or_weak_results": card.get("risk_boundary", ""),
                "missing_checks": card.get("missing_test", ""),
                "figure_table_use": scale_figure_use(scale, domains),
            }
        )
    return rows


def make_md(rows: list[dict[str, object]]) -> str:
    lines = [
        "# Scale-specific story cards",
        "",
        "本文件按 scale 独立组织。每个小节中的故事、结果和图表建议只允许使用该 scale 的数据；跨 scale 信息只在最终推荐中比较，不进入单个 scale 的故事内部。",
    ]
    for row in rows:
        scale = str(row["scale"])
        lines.extend(
            [
                "",
                f"## {scale}",
                "",
                f"**Claim.** {row['claim']}",
                "",
                f"**Placement.** {row['main_text_or_appendix']}；support={row['support_level']}；domain_count={row['domain_count']}",
                "",
                f"**Story.** {row['story_paragraph_cn']}",
                "",
                f"**可用中文句子.** {row['safe_sentences_cn']}",
                "",
                f"**English sentences.** {row['safe_sentences_en']}",
                "",
                f"**描述统计.** N={row['N_sample']}；grids={row['N_grids_sample']}；main_sample={row['main_sample']}；zone_core={row['zone_core']}；sr_within={row['sr_within']}；region_score={row['region_score']}；irrigation_score={row['irrigation_score']}；phenology_score={row['phenology_score']}",
                "",
                f"**核心结果.** {row['core_results']}",
                "",
                f"**图表承载.** {row['figure_table_use']}",
                "",
                f"**弱结果和边界.** {row['unsupported_or_weak_results']}",
                "",
                f"**最多补充检验.** {row['missing_checks']}",
            ]
        )
    return "\n".join(lines)


def make_figure_plan(rows: list[dict[str, object]]) -> str:
    lines = [
        "# Scale-specific figure plan",
        "",
        "每个 scale 只画该 scale 自己的结果。comparison 图只放在最终推荐部分，不能作为某个 scale 的内部证据。",
    ]
    for row in rows:
        scale = str(row["scale"])
        plans = []
        if row["domain_region"] == "yes":
            plans.append(f"`fig_{scale.lower()}_region_hazard_buffer.png`: region × hazard heatmap/dot matrix, fields `region`, `hazard`, `scaled_buffer`, `c3_p`, `N_model`.")
        if row["domain_irrigation_margin"] == "yes":
            plans.append(f"`fig_{scale.lower()}_irrigation_margins.png`: P25/P50/P75 irrigation margin line chart, fields `irr_level`, `pct_yield_buffer_at_hazard_p90`, `triple_p`.")
        if row["domain_phenology_margin"] == "yes":
            plans.append(f"`fig_{scale.lower()}_phenology_slopes.png`: SR quantile by D×H slope line chart, fields `window`, `ca_level`, `dh_slope_at_ca`, `gamma_SRDH_p`.")
        if row["domain_te_iede"] == "yes":
            plans.append("`fig_b067_te_delta.png`: TE P75-P25 delta with bootstrap interval. IE/DE components require separate table or figure.")
        if row["domain_baseline_cluster"] == "yes" or row["domain_irrigation_cluster"] == "yes" or row["domain_phenology_cluster"] == "yes":
            plans.append(f"`fig_{scale.lower()}_compact_evidence.png`: compact cluster/selected evidence panel using only {scale} rows.")
        if not plans:
            plans.append("No standalone figure beyond curated card/table; keep as appendix text only.")
        lines.extend(["", f"## {scale}", "", *[f"- {plan}" for plan in plans]])
    return "\n".join(lines)


def make_final_recommendation(rows: list[dict[str, object]]) -> str:
    lines = [
        "# Final scale recommendation draft",
        "",
        "本文件是自动生成初稿，后续需要用 scale agents 与 reviewer 的反馈更新。当前规则是：最终只能选一个 scale；候选故事内部不得混入其他 scale 结果。",
        "",
        "## Current ranking logic",
        "",
        "`G185` 与 `G057` 是主文候选；若最终只能选一个 scale，优先选 `G185`，因为它在 main_sample=1 下同时承载 region、irrigation、phenology 和 Stata verify。`G057` 是最接近的 region-first 展示对照。`B067` 可以独立讲 TE delta 和机制层 association structure，但不能承载 region/irrigation/phenology 主故事。`G195/G255/G256/G177/G049` 更适合作为 appendix 或 sensitivity。宽口径 `G001/G009/G017/G033` 只适合 exploratory appendix。",
        "",
        "| rank | scale | support | placement | reason |",
        "|---:|---|---|---|---|",
    ]
    fixed_order = ["G185", "G057", "G177", "G049", "G255", "B067", "G195", "G256", "G001", "G033", "G017", "G009"]
    by = {row["scale"]: row for row in rows}
    ranking = [by[scale] for scale in fixed_order if scale in by] + [row for row in rows if row["scale"] not in fixed_order]
    for idx, row in enumerate(ranking, 1):
        reason = f"domain_count={row['domain_count']}; main_sample={row['main_sample']}; region_score={row['region_score']}; irrigation_score={row['irrigation_score']}; phenology_score={row['phenology_score']}"
        lines.append(f"| {idx} | {row['scale']} | {row['support_level']} | {row['main_text_or_appendix']} | {reason} |")
    return "\n".join(lines)


def plot_region(data: dict[str, list[dict[str, str]]], scale: str, plt) -> None:
    rows = rows_where(data["region"], sample_id=scale)
    if not rows:
        return
    regions = sorted({row.get("region", "") for row in rows if row.get("region")})
    hazards = ["drought", "heat", "hotdry"]
    values = [[math.nan for _ in hazards] for _ in regions]
    labels = [["" for _ in hazards] for _ in regions]
    for row in rows:
        if row.get("region") in regions and row.get("hazard") in hazards:
            i = regions.index(row["region"])
            j = hazards.index(row["hazard"])
            val = n(row.get("scaled_buffer"))
            values[i][j] = math.nan if val is None else val * 100
            labels[i][j] = fmt(row.get("c3_p"), 2)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    im = ax.imshow(values, cmap="YlGnBu")
    ax.set_xticks(range(len(hazards)), hazards)
    ax.set_yticks(range(len(regions)), regions)
    ax.set_title(f"{scale}: region x hazard buffer")
    for i in range(len(regions)):
        for j in range(len(hazards)):
            val = values[i][j]
            if not math.isnan(val):
                ax.text(j, i, f"{val:.2f}%\np={labels[i][j]}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="Scaled buffer (% yield)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"fig_{scale.lower()}_region_hazard_buffer.png", dpi=300)
    plt.close(fig)


def plot_irrigation(data: dict[str, list[dict[str, str]]], scale: str, plt) -> None:
    rows = rows_where(data["irrigation"], scale=scale)
    if not rows:
        return
    levels = ["P25", "P50", "P75"]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for hazard in ["drought", "heat", "hotdry"]:
        by_level = {row.get("irr_level"): row for row in rows if row.get("hazard") == hazard}
        vals = [n(by_level.get(level, {}).get("pct_yield_buffer_at_hazard_p90")) for level in levels]
        ax.plot(levels, vals, marker="o", label=hazard)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("P90 hazard buffer (% yield)")
    ax.set_title(f"{scale}: irrigation margins")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"fig_{scale.lower()}_irrigation_margins.png", dpi=300)
    plt.close(fig)


def plot_phenology(data: dict[str, list[dict[str, str]]], scale: str, plt) -> None:
    rows = rows_where(data["phenology"], scale=scale)
    if not rows:
        return
    levels = ["P25", "P50", "P75"]
    windows = sorted({row.get("window", "") for row in rows if row.get("ca_level") in levels})
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for window in windows:
        by_level = {row.get("ca_level"): row for row in rows if row.get("window") == window}
        vals = [n(by_level.get(level, {}).get("dh_slope_at_ca")) for level in levels]
        ax.plot(levels, vals, marker="o", label=window)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("D x H slope at SR quantile")
    ax.set_title(f"{scale}: phenology D x H slope")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"fig_{scale.lower()}_phenology_slopes.png", dpi=300)
    plt.close(fig)


def plot_b067(data: dict[str, list[dict[str, str]]], plt) -> None:
    rows = data["b067_delta"]
    if not rows:
        return
    labels = [row.get("hazard", row.get("effect_type", "")) for row in rows]
    vals = [n(row.get("pct_delta_point_percent"), n(row.get("p75_minus_p25"), 0)) for row in rows]
    lows = [n(row.get("pct_delta_ci_lo_percent")) for row in rows]
    highs = [n(row.get("pct_delta_ci_hi_percent")) for row in rows]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(labels, vals)
    for idx, (val, low, high) in enumerate(zip(vals, lows, highs)):
        if val is not None and low is not None and high is not None:
            ax.errorbar(idx, val, yerr=[[val - low], [high - val]], color="black", capsize=3)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("P75 - P25 delta (% yield)")
    ax.set_title("B067: TE P75-P25 delta, appendix-only scale")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_b067_te_delta.png", dpi=300)
    fig.savefig(FIG_DIR / "fig_b067_te_iede_delta.png", dpi=300)
    plt.close(fig)


def scale_rows(data: dict[str, list[dict[str, str]]], scale: str, preferred: str) -> list[dict[str, str]]:
    if preferred == "baseline":
        selected = rows_where(data["selected_baseline"], sample_id=scale)
        representative = rows_where(data["rep_baseline"], sample_id=scale)
    elif preferred == "irrigation":
        selected = rows_where(data["selected_irrigation"], sample_id=scale)
        representative = rows_where(data["rep_irrigation"], sample_id=scale)
    elif preferred == "phenology":
        selected = rows_where(data["selected_phenology"], sample_id=scale)
        representative = rows_where(data["rep_phenology"], sample_id=scale)
    else:
        selected = []
        representative = []
    return selected or representative


def plot_compact_evidence(data: dict[str, list[dict[str, str]]], scale: str, plt) -> None:
    baseline = scale_rows(data, scale, "baseline")
    irrigation = scale_rows(data, scale, "irrigation")
    phenology = scale_rows(data, scale, "phenology")
    if not baseline and not irrigation and not phenology:
        return

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    hazards = ["drought", "heat", "hotdry"]

    ax = axes[0]
    if baseline:
        by_hazard = {row.get("hazard"): row for row in baseline}
        vals = [n(by_hazard.get(h, {}).get("te_slope")) for h in hazards]
        colors = ["#2ca25f" if (v or 0) >= 0 else "#de2d26" for v in vals]
        ax.bar(hazards, vals, color=colors)
        for idx, h in enumerate(hazards):
            pval = by_hazard.get(h, {}).get("c3_p")
            ax.text(idx, vals[idx] or 0, f"p={fmt(pval, 2)}", ha="center", va="bottom", fontsize=7)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title("Baseline TE slope")
    else:
        ax.text(0.5, 0.5, "No baseline rows", ha="center", va="center")
        ax.set_axis_off()

    ax = axes[1]
    if irrigation:
        by_hazard = {row.get("hazard"): row for row in irrigation}
        vals = [n(by_hazard.get(h, {}).get("triple")) for h in hazards]
        colors = ["#3182bd" if (v or 0) < 0 else "#756bb1" for v in vals]
        ax.bar(hazards, vals, color=colors)
        for idx, h in enumerate(hazards):
            pval = by_hazard.get(h, {}).get("triple_p")
            ax.text(idx, vals[idx] or 0, f"p={fmt(pval, 2)}", ha="center", va="bottom", fontsize=7)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title("Irrigation triple")
    else:
        ax.text(0.5, 0.5, "No irrigation rows", ha="center", va="center")
        ax.set_axis_off()

    ax = axes[2]
    if phenology:
        windows = ["full", "v3he", "hepm10", "hema"]
        by_window = {row.get("window"): row for row in phenology}
        beta = [n(by_window.get(w, {}).get("beta_DH")) for w in windows]
        gamma = [n(by_window.get(w, {}).get("gamma_SRDH")) for w in windows]
        x = list(range(len(windows)))
        ax.bar([i - 0.18 for i in x], beta, width=0.36, label="D x H")
        ax.bar([i + 0.18 for i in x], gamma, width=0.36, label="SR x D x H")
        ax.set_xticks(x, windows, rotation=30)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title("Phenology compound")
        ax.legend(fontsize=7)
    else:
        ax.text(0.5, 0.5, "No phenology rows", ha="center", va="center")
        ax.set_axis_off()

    fig.suptitle(f"{scale}: compact scale-specific evidence", y=1.03)
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"fig_{scale.lower()}_compact_evidence.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_figures(data: dict[str, list[dict[str, str]]], rows: list[dict[str, object]]) -> None:
    import matplotlib.pyplot as plt

    plt.style.use("default")
    for row in rows:
        scale = str(row["scale"])
        plot_region(data, scale, plt)
        plot_irrigation(data, scale, plt)
        plot_phenology(data, scale, plt)
        plot_compact_evidence(data, scale, plt)
    plot_b067(data, plt)
    write_text(
        RUN_DIR / "figure_status.txt",
        "Generated scale-specific figures only from each scale's own rows. Cross-scale comparison figures are intentionally omitted from story evidence.",
    )


def main() -> None:
    ensure_dirs()
    data = load_inputs()
    rows = make_story_rows(data)
    fieldnames = [
        "scale",
        "claim",
        "story_paragraph_cn",
        "safe_sentences_cn",
        "safe_sentences_en",
        "N_sample",
        "N_grids_sample",
        "main_sample",
        "zone_core",
        "sr_within",
        "region_score",
        "irrigation_score",
        "phenology_score",
        "support_level",
        "main_text_or_appendix",
        "domain_count",
        "domain_region",
        "domain_irrigation_margin",
        "domain_phenology_margin",
        "domain_stata_verify",
        "domain_baseline_cluster",
        "domain_irrigation_cluster",
        "domain_phenology_cluster",
        "domain_representative_irrigation",
        "domain_representative_phenology",
        "domain_te_iede",
        "core_results",
        "unsupported_or_weak_results",
        "missing_checks",
        "figure_table_use",
    ]
    write_csv(RUN_DIR / "scale_specific_story_cards.csv", rows, fieldnames)
    write_text(RUN_DIR / "scale_specific_story_cards.md", make_md(rows))
    write_text(RUN_DIR / "scale_specific_figure_plan.md", make_figure_plan(rows))
    write_text(RUN_DIR / "final_scale_recommendation.md", make_final_recommendation(rows))
    make_figures(data, rows)
    print(f"Wrote scale-specific story pack to {RUN_DIR}")


if __name__ == "__main__":
    main()
