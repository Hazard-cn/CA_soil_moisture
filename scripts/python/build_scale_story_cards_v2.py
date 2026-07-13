from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = ROOT / "quality_reports" / "agent_runs" / "2026-06-19_scale_story_cards_v2"
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
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def num(value: object, default: float | None = None) -> float | None:
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
    value_float = num(value)
    if value_float is None:
        return "NA"
    if abs(value_float) >= 100:
        return f"{value_float:,.1f}"
    if abs(value_float) >= 1:
        return f"{value_float:,.{digits}f}"
    return f"{value_float:.{digits}g}"


def pct(value: object, digits: int = 2) -> str:
    value_float = num(value)
    if value_float is None:
        return "NA"
    return f"{value_float:.{digits}f}%"


def by_id(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in rows}


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


def load_inputs() -> dict[str, list[dict[str, str]]]:
    return {
        "region_top": read_csv("temp/2026-06-18_story_empirical_review_match/region_first_top15.csv"),
        "region_details": read_csv("temp/2026-06-18_story_empirical_review_match/selected_region_details.csv"),
        "irrigation_margins": read_csv("temp/2026-06-18_story_followup_margins/irrigation_standardized_margins.csv"),
        "irrigation_triples": read_csv("temp/2026-06-18_story_empirical_review_match/selected_irrigation_triples.csv"),
        "phenology_margins": read_csv("temp/2026-06-18_story_followup_margins/phenology_srdh_margins.csv"),
        "phenology_summary": read_csv("temp/2026-06-18_story_empirical_review_match/representative_phenology_summary.csv"),
        "rep_phenology": read_csv("temp/2026-06-11_expanded_scale_story_search/representative_phenology_cluster.csv"),
        "rep_irrigation": read_csv("temp/2026-06-11_expanded_scale_story_search/representative_irrigation_cluster.csv"),
        "b067_te": read_csv("temp/2026-06-18_story_empirical_review_match/b067_baseline_te_by_sr.csv"),
        "b067_iede_delta": read_csv("temp/2026-06-18_story_followup_margins/b067_iede_delta.csv"),
        "b067_iede_levels": read_csv("temp/2026-06-18_story_followup_margins/b067_iede_levels.csv"),
        "all_highscore": read_csv("temp/2026-06-11_region_first_story_search/all_highscore_ranking_cluster.csv"),
        "expanded_rank": read_csv("temp/2026-06-11_expanded_scale_story_search/expanded_candidate_ranking.csv"),
        "expanded_index": read_csv("temp/2026-06-11_expanded_scale_story_search/expanded_scale_index.csv"),
        "stata_verify": read_csv("temp/2026-06-18_story_stata_verify/stata_python_verify_comparison.csv"),
    }


def scale_base(data: dict[str, list[dict[str, str]]], scale: str) -> dict[str, str]:
    candidates = [
        by_id(data["region_top"], "sample_id").get(scale, {}),
        by_id(data["all_highscore"], "sample_id").get(scale, {}),
        by_id(data["expanded_rank"], "sample_id").get(scale, {}),
        by_id(data["expanded_index"], "sample_id").get(scale, {}),
    ]
    out: dict[str, str] = {}
    for row in candidates:
        for key, value in row.items():
            if value != "" and key not in out:
                out[key] = value
    if scale == "B067":
        out.update(
            {
                "sample_id": "B067",
                "N_sample": "42187",
                "N_grids_sample": "11775",
                "main_sample": "1",
                "zone_core": "1",
                "sr_within": "1",
                "region_score": "10",
                "irrigation_score": "legacy",
                "phenology_score": "legacy",
            }
        )
    return out


def region_pattern(data: dict[str, list[dict[str, str]]], scale: str) -> str:
    row = scale_base(data, scale)
    if not row or not row.get("ne_dominant"):
        if scale in {"B067", "G195"}:
            return "legacy/within-grid 口径不适合承载 region-first 主故事；既有审计记录显示 region-first score 较低。"
        return "该 scale 未进入 region-first 细节表。"
    return (
        f"NE={row.get('ne_dominant')}, HHH={row.get('hhh_dominant')}, "
        f"NW={row.get('nw_dominant')}, SW={row.get('sw_dominant')}, SH={row.get('sh_dominant')}; "
        f"region_score={row.get('region_score')}/16, region_evidence={fmt(row.get('region_evidence'))}."
    )


def region_details_sentence(data: dict[str, list[dict[str, str]]], scale: str) -> str:
    pieces = []
    for region, hazard in [("NE", "drought"), ("HHH", "heat"), ("HHH", "hotdry"), ("NW", "hotdry"), ("SW", "hotdry"), ("SH", "hotdry")]:
        row = one(data["region_details"], sample_id=scale, region=region, hazard=hazard)
        if row:
            pieces.append(
                f"{region}-{hazard}: scaled_buffer={pct((num(row.get('scaled_buffer'), 0.0) or 0.0) * 100)}, "
                f"p={fmt(row.get('c3_p'))}, N={row.get('N_model')}"
            )
    return "；".join(pieces) if pieces else "未在 selected_region_details 中读取到该 scale 的区域细节。"


def irrigation_sentence(data: dict[str, list[dict[str, str]]], scale: str) -> str:
    rows = rows_where(data["irrigation_margins"], scale=scale)
    pieces = []
    if rows:
        for hazard in ["drought", "heat", "hotdry"]:
            p25 = one(rows, hazard=hazard, irr_level="P25")
            p75 = one(rows, hazard=hazard, irr_level="P75")
            delta = one(rows, hazard=hazard, irr_level="P75_minus_P25")
            if p25 and p75:
                pieces.append(
                    f"{hazard}: low={pct(p25.get('pct_yield_buffer_at_hazard_p90'))}, "
                    f"high={pct(p75.get('pct_yield_buffer_at_hazard_p90'))}, "
                    f"high-low={pct(delta.get('pct_yield_buffer_at_hazard_p90'))}, "
                    f"triple p={fmt(p25.get('triple_p'))}"
                )
    else:
        rep_rows = rows_where(data["rep_irrigation"], sample_id=scale)
        for hazard in ["drought", "heat", "hotdry"]:
            rep = one(rep_rows, hazard=hazard)
            if rep:
                pieces.append(
                    f"{hazard}: triple={fmt(rep.get('triple'))} (p={fmt(rep.get('triple_p'))}), "
                    f"base={fmt(rep.get('base_c3'))} (p={fmt(rep.get('base_c3_p'))}), "
                    f"N={rep.get('N_model')}"
                )
    if not pieces:
        return "未读取到该 scale 的 irrigation margins 或 representative irrigation triple。"
    return "；".join(pieces)


def phenology_sentence(data: dict[str, list[dict[str, str]]], scale: str) -> str:
    rows = rows_where(data["phenology_margins"], scale=scale)
    pieces = []
    if rows:
        for window in ["hepm10", "hema", "v3he"]:
            p25 = one(rows, window=window, ca_level="P25")
            p75 = one(rows, window=window, ca_level="P75")
            delta = one(rows, window=window, ca_level="P75_minus_P25")
            if p25 and p75:
                pieces.append(
                    f"{window}: D×H={fmt(p25.get('beta_DH'))} (p={fmt(p25.get('beta_DH_p'))}), "
                    f"SR×D×H={fmt(p25.get('gamma_SRDH'))} (p={fmt(p25.get('gamma_SRDH_p'))}), "
                    f"slope shift={fmt(delta.get('dh_slope_at_ca'))}"
                )
    else:
        rep_rows = rows_where(data["rep_phenology"], sample_id=scale)
        for window in ["hepm10", "hema", "v3he", "full"]:
            rep = one(rep_rows, window=window)
            if rep:
                pieces.append(
                    f"{window}: D×H={fmt(rep.get('beta_DH'))} (p={fmt(rep.get('beta_DH_p'))}), "
                    f"SR×D×H={fmt(rep.get('gamma_SRDH'))} (p={fmt(rep.get('gamma_SRDH_p'))}), "
                    f"N={rep.get('N_model')}"
                )
    if not pieces:
        return "未读取到该 scale 的 phenology margins 或 representative phenology cluster。"
    return "；".join(pieces)


def expanded_sentence(data: dict[str, list[dict[str, str]]], scale: str) -> str:
    row = by_id(data["expanded_rank"], "sample_id").get(scale, {})
    if not row:
        return "未读取到 expanded candidate ranking。"
    return (
        f"story_score={row.get('story_score')}, min_te_slope={fmt(row.get('min_te_slope'))}, "
        f"irrigation triples: drought={fmt(row.get('triple_drought'))} (p={fmt(row.get('triple_p_drought'))}), "
        f"heat={fmt(row.get('triple_heat'))} (p={fmt(row.get('triple_p_heat'))}), "
        f"hotdry={fmt(row.get('triple_hotdry'))} (p={fmt(row.get('triple_p_hotdry'))}); "
        f"full D×H={fmt(row.get('beta_DH'))} (p={fmt(row.get('beta_DH_p'))}), "
        f"SR×D×H={fmt(row.get('gamma_SRDH'))} (p={fmt(row.get('gamma_SRDH_p'))})."
    )


def b067_te_sentence(data: dict[str, list[dict[str, str]]]) -> str:
    pieces = []
    for hazard in ["drought", "heat", "hotdry"]:
        p25 = one(data["b067_te"], hazard=hazard, ca_level="P25")
        p75 = one(data["b067_te"], hazard=hazard, ca_level="P75")
        delta = one(data["b067_iede_delta"], hazard=hazard)
        rel = None
        if p25 and p75:
            te25 = num(p25.get("estimate"))
            te75 = num(p75.get("estimate"))
            if te25 and te25 != 0:
                rel = ((te75 or 0.0) - te25) / abs(te25) * 100
        pieces.append(
            f"{hazard}: TE P25={fmt(p25.get('estimate'))}, P75={fmt(p75.get('estimate'))}, "
            f"P75-P25={pct(delta.get('pct_delta_point_percent'))} "
            f"[{pct(delta.get('pct_delta_ci_lo_percent'))}, {pct(delta.get('pct_delta_ci_hi_percent'))}], "
            f"relative attenuation={pct(rel) if rel is not None else 'NA'}"
        )
    return "；".join(pieces)


def iede_channel_sentence(data: dict[str, list[dict[str, str]]]) -> str:
    pieces = []
    for hazard, effect in [("drought", "IE"), ("hotdry", "IE"), ("heat", "DE")]:
        p25 = one(data["b067_iede_levels"], hazard=hazard, effect=effect, ca_level="P25")
        p75 = one(data["b067_iede_levels"], hazard=hazard, effect=effect, ca_level="P75")
        if p25 and p75:
            pieces.append(
                f"{hazard}-{effect}: P25={fmt(p25.get('estimate'))} "
                f"[{fmt(p25.get('bs_ci_lo_95'))}, {fmt(p25.get('bs_ci_hi_95'))}], "
                f"P75={fmt(p75.get('estimate'))} "
                f"[{fmt(p75.get('bs_ci_lo_95'))}, {fmt(p75.get('bs_ci_hi_95'))}]"
            )
    return "；".join(pieces)


def scale_role(scale: str) -> tuple[str, str, str, str]:
    roles = {
        "G185": ("主文主表 scale", "moderate", "main", "main_sample=1，核心变量更干净，region_score 与 G057 一致。"),
        "G057": ("region-first 展示 scale", "moderate", "main/display", "region-first 支持最强，但不是 main_sample=1，需披露缺失和 scale search。"),
        "G049": ("near-twin 展示 sensitivity", "suggestive", "appendix", "与 G057 区域模式接近，用于说明 G057 不是单一偶然。"),
        "G177": ("near-twin clean sensitivity", "suggestive", "appendix", "与 G185 区域模式接近，用于 main_sample 替代 sensitivity。"),
        "B067": ("legacy within-grid 机制 scale", "moderate", "mechanism/appendix", "用于 TE/IE/DE bootstrap 和旧框架可比性，不承担 region-first。"),
        "G195": ("legacy G-code reference", "suggestive", "appendix", "与 B067 样本口径对应，可连接 expanded scale search 与 B067 机制结果。"),
        "G255": ("strict endpoint sensitivity", "suggestive", "appendix", "规则最严格，适合证明结果不是只在宽口径出现，但 phenology/irrigation 支持较弱。"),
        "G256": ("narrow strict endpoint sensitivity", "suggestive", "appendix", "比 G255 更窄，适合做 strict appendix 的端点边界，不适合主文。"),
    }
    if scale in roles:
        return roles[scale]
    return ("expanded exploratory scale", "exploratory", "appendix/exploration", "宽口径探索结果，用于说明往前退一步时故事是否仍存在。")


def build_scale_cards(data: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    scales = ["G185", "G057", "G049", "G177", "B067", "G195", "G255", "G256", "G001", "G009", "G017", "G033"]
    cards: list[dict[str, str]] = []
    b067_story = b067_te_sentence(data)
    b067_channels = iede_channel_sentence(data)
    for scale in scales:
        base = scale_base(data, scale)
        role, support, placement, role_reason = scale_role(scale)
        region = region_pattern(data, scale)
        region_detail = region_details_sentence(data, scale)
        irrigation = irrigation_sentence(data, scale)
        phenology = phenology_sentence(data, scale)
        expanded = expanded_sentence(data, scale)
        if scale == "B067":
            story_name = "TE/IE/DE 下的 stress-response slope flattening"
            story = (
                "B067 最适合回答用户原本关心的问题：不同 SR 水平下 TE、IE、DE 是否显示 SR 的缓冲作用。"
                "在该 within-grid 口径中，核心可写结果不是区域排序，而是当 SR 从 P25 到 P75 提高时，"
                "drought、heat 和 hotdry 的 TE 均向减损方向移动。这个故事适合放在机制或基础结果层，"
                "说明 SR 与更平缓的胁迫-产量损失斜率相关，但不能写成因果中介。"
            )
            key_results = f"{b067_story}；{b067_channels}"
            sentences_cn = (
                "在 B067 口径下，SR 从 P25 到 P75 的变化对应 P90 drought、heat 和 hotdry 情景下 TE 的减损方向移动。"
                "；B067 的 IE/DE/TE 结果更适合作为 association decomposition，而不是因果中介证据。"
                "；该 scale 能讲的是 stress-response slope flattening，不是无条件增产。"
            )
            sentences_en = (
                "At the B067 scale, moving from low to high SR is associated with attenuated total stress-response losses under P90 drought, heat, and hot-dry exposure."
                " The IE/DE/TE decomposition should be interpreted as association structure, not causal mediation."
            )
            risks = "不能写 causal mediation；不能用 B067 承担 region-first 总主线；heat/hotdry 的 TE level 单点 CI 部分跨 0。"
            missing = "若机制线进主文，补 IE/DE slope difference 的 bootstrap 检验和低/中/高 hazard 的 SR marginal association。"
        elif scale == "G195":
            story_name = "B067 的 G-code 对照与 expanded search 连接"
            story = (
                "G195 适合把 B067 的 legacy 机制故事与 G-code scale search 连接起来。"
                "它保留 main_sample、zone_core 和 sr_within，因此解释口径清楚，但 region-first 得分不足，"
                "不应承担区域定向总主线。它的用途是说明：即使回到更保守的 within-grid 口径，"
                "单一胁迫 slope 和灌溉边界仍能作为基础或 appendix 证据存在。"
            )
            key_results = f"Irrigation: {irrigation} Phenology: {phenology} Expanded: {expanded}"
            sentences_cn = (
                "G195 可以作为 B067 的 G-code 对照，用来说明旧框架下的机制性结果并没有与扩展 scale 搜索完全脱节。"
                "；但 G195 不适合承载 region-first 主线，因为它的区域异质性得分明显弱于 G057/G185。"
            )
            sentences_en = (
                "G195 connects the legacy B067 mechanism frame to the broader G-scale search, but it should remain a reference scale rather than the main region-first specification."
            )
            risks = "不能把 G195 写成 region-first 主 scale；需要明确其与 B067 的样本对应关系。"
            missing = "如要用 G195 进主表，应补最终 Stata reghdfe 复核和与 B067 的口径对照表。"
        elif scale in {"G185", "G057", "G049", "G177"}:
            story_name = "区域定向气候风险缓冲与灌溉边界"
            if scale == "G185":
                story = (
                    "G185 是当前最适合进入主文表格的 scale。它保留 main_sample=1，核心变量更干净，"
                    "同时复制 G057 的 region-first 方向：NE 更适合讲 drought buffering，HHH 更适合讲 heat/hotdry，"
                    "SW/SH 只能写热旱或复合风险边界，NW 只能写方向性支持。"
                    "这个 scale 的故事不是“SR 在某一地区一定更好”，而是“SR 的缓冲对象随区域主导胁迫改变”。"
                )
            elif scale == "G057":
                story = (
                    "G057 是 region-first 信号最完整、最适合做图示展示的 scale。"
                    "它的区域模式与 G185 几乎一致，而且已经有 baseline 和 irrigation triple 的 Stata 复核。"
                    "但它不是 main_sample=1，且存在 irrigation 缺失和 zone_core=0 的边界，因此更适合作为主图展示或与 G185 并列，"
                    "不宜单独写成确认性主规格。"
                )
            elif scale == "G049":
                story = (
                    "G049 是 G057 的宽口径 near-twin，主要作用是说明 region-first 结果不完全依赖 `sm_sd=1` 这条规则。"
                    "它可以放在 appendix 里支撑同一方向的区域定向故事，但由于不是 main_sample，也没有更强的解释优势，"
                    "不应替代 G185 或 G057。"
                )
            else:
                story = (
                    "G177 是 G185 的 near-twin，可作为 main_sample 口径下的 sensitivity。"
                    "它与 G185 的区域主导类型一致，适合说明区域定向故事不是由 `sm_sd=1` 单一筛选条件决定。"
                    "但它的角色仍是稳健性而不是新的中心故事。"
                )
            key_results = f"{region} Region details: {region_detail} Irrigation: {irrigation} Phenology: {phenology} Expanded: {expanded}"
            sentences_cn = (
                f"在 {scale} 口径下，SR 相关缓冲更适合写成区域主导胁迫下的损失斜率变化，而不是全国统一平均增产。"
                f"；{scale} 支持 NE-drought 与 HHH-heat/hotdry 的差异化叙事，但 NW/SH 只能作为方向性或低功效边界。"
                "；灌溉结果支持 heat/hotdry 下边际缓冲空间随灌溉提高而收缩，drought 互补只能弱写。"
            )
            sentences_en = (
                f"At the {scale} scale, SR-related buffering is better framed as a region-specific change in stress-response slopes than as a uniform yield gain."
                " The strongest narrative is that the relevant buffered stress differs by regional exposure and water-management context."
            )
            risks = "region-first 来自 scale search；NW 不显著，SH 样本小；不能把灌溉高低组图替代连续 triple。"
            missing = "补 high-score candidates 分布、FDR/Holm 或等价多重检验说明、region×SR×hazard 的正式 Stata/pooled Wald 表。"
        elif scale in {"G255", "G256"}:
            story_name = "strict endpoint sensitivity"
            strict_label = "G255" if scale == "G255" else "G256"
            story = (
                f"{strict_label} 是 strict endpoint sensitivity，适合回答审稿人可能提出的“是不是只有宽口径才成立”的问题。"
                "它保留 main_sample、zone_core、sr_within、yield 和 soil-moisture 相关限制，样本更小但口径更干净。"
                "它可以支持区域定向故事的存在性，但标准化 region-first、irrigation 和 phenology 得分较弱，尤其 HE-MA 的 D×H 基础损失不稳定，"
                "因此不适合做主文核心 scale。"
            )
            key_results = f"{region} Region details: {region_detail} Irrigation: {irrigation} Phenology: {phenology} Expanded: {expanded}"
            sentences_cn = (
                f"{strict_label} 适合写作 strict sensitivity：在更严格样本口径下，区域定向缓冲仍有方向性支持，但物候和灌溉证据不如 G057/G185。"
                f"；因此 {strict_label} 的作用是限定结论边界，而不是替代主文 scale。"
            )
            sentences_en = (
                f"{strict_label} is best used as a strict endpoint sensitivity: it preserves the direction of the regional-targeting story but does not provide the strongest phenology or irrigation evidence."
            )
            risks = "样本更小；irrigation_score=2、phenology_score=1；HEMA beta_DH 不显著。"
            missing = "只需 appendix 展示；若进入主文需补同口径 irrigation margins 和 phenology CI。"
        else:
            story_name = "broader exploratory scale"
            story = (
                f"{scale} 是 expanded search 中的宽口径探索 scale。它说明如果把范围放宽、退回到更少筛选规则，"
                "state buffering 与 irrigation reallocation 的方向仍然存在。这个层面的作用是探索性地证明故事不完全依赖严格筛选，"
                "但因为缺少 main_sample、zone_core 或 sr_within 等限制，不适合直接进入主文结论。"
            )
            key_results = expanded
            sentences_cn = (
                f"{scale} 可以作为探索性背景：宽口径样本中仍能看到 SR 与损失斜率趋平、灌溉重新配置边际价值的方向。"
                "；这类 scale 只能说明故事的方向存在更大样本支持，不能写成确认性结果。"
            )
            sentences_en = (
                f"{scale} provides exploratory evidence that the broad-sample direction is consistent with state-dependent buffering and irrigation reallocation, but it should not be treated as a confirmatory specification."
            )
            risks = "宽口径没有 main_sample/zone_core/sr_within 限制，容易被质疑为样本混杂或结果导向选择。"
            missing = "只作为 appendix distribution 或探索表；不建议增加主文负担。"

        cards.append(
            {
                "scale_id": scale,
                "scale_role": role,
                "support_level": support,
                "preferred_placement": placement,
                "role_reason": role_reason,
                "story_name": story_name,
                "story_paragraph_cn": story,
                "safe_sentences_cn": sentences_cn,
                "safe_sentences_en": sentences_en,
                "N_sample": base.get("N_sample", "NA"),
                "N_grids_sample": base.get("N_grids_sample", "NA"),
                "main_sample": base.get("main_sample", "NA"),
                "zone_core": base.get("zone_core", "NA"),
                "sr_within": base.get("sr_within", "NA"),
                "region_score": base.get("region_score", "NA"),
                "national_score": base.get("national_score", "NA"),
                "irrigation_score": base.get("irrigation_score", "NA"),
                "phenology_score": base.get("phenology_score", "NA"),
                "key_region_pattern": region,
                "key_region_stats": region_detail,
                "key_irrigation_stats": irrigation,
                "key_phenology_stats": phenology,
                "key_te_iede_stats": b067_story if scale == "B067" else "",
                "key_results": key_results,
                "figure_table_use": figure_plan_for_scale(scale),
                "risk_boundary": risks,
                "missing_test": missing,
            }
        )
    return cards


def figure_plan_for_scale(scale: str) -> str:
    if scale == "G185":
        return "Main Table 1: clean main-sample region-first results; Appendix compare G057/G177."
    if scale == "G057":
        return "Main Figure 1: region map or region-hazard panel; main table should pair with G185."
    if scale in {"G049", "G177"}:
        return "Appendix sensitivity: near-twin region-first scale comparison."
    if scale == "B067":
        return "Mechanism Figure: TE/IE/DE by SR quantile and TE(P75-P25) at P90 hazards."
    if scale == "G195":
        return "Appendix bridge table: B067/G195 legacy-to-G-code comparison."
    if scale == "G255":
        return "Appendix strict endpoint sensitivity."
    if scale == "G256":
        return "Appendix narrow strict endpoint sensitivity; use only as endpoint boundary."
    return "Appendix exploratory scale distribution."


def build_descriptive_stats(cards: list[dict[str, str]]) -> list[dict[str, str]]:
    fields = [
        "scale_id",
        "scale_role",
        "support_level",
        "preferred_placement",
        "N_sample",
        "N_grids_sample",
        "main_sample",
        "zone_core",
        "sr_within",
        "region_score",
        "national_score",
        "irrigation_score",
        "phenology_score",
        "key_region_pattern",
        "key_irrigation_stats",
        "key_phenology_stats",
    ]
    return [{key: card.get(key, "") for key in fields} for card in cards]


def write_scale_story_cards(cards: list[dict[str, str]]) -> None:
    fields = [
        "scale_id",
        "scale_role",
        "support_level",
        "preferred_placement",
        "role_reason",
        "story_name",
        "story_paragraph_cn",
        "safe_sentences_cn",
        "safe_sentences_en",
        "N_sample",
        "N_grids_sample",
        "main_sample",
        "zone_core",
        "sr_within",
        "region_score",
        "national_score",
        "irrigation_score",
        "phenology_score",
        "key_region_pattern",
        "key_region_stats",
        "key_irrigation_stats",
        "key_phenology_stats",
        "key_te_iede_stats",
        "key_results",
        "figure_table_use",
        "risk_boundary",
        "missing_test",
    ]
    write_csv(RUN_DIR / "scale_story_cards.csv", cards, fields)
    descriptive_fields = [
        "scale_id",
        "scale_role",
        "support_level",
        "preferred_placement",
        "N_sample",
        "N_grids_sample",
        "main_sample",
        "zone_core",
        "sr_within",
        "region_score",
        "national_score",
        "irrigation_score",
        "phenology_score",
        "key_region_pattern",
        "key_irrigation_stats",
        "key_phenology_stats",
    ]
    write_csv(RUN_DIR / "descriptive_story_stats.csv", build_descriptive_stats(cards), descriptive_fields)

    lines = [
        "# Scale Story Cards v2",
        "",
        "本文件以 scale 为单位组织故事。每张卡片回答：这个 scale 能讲什么、可写哪些句子、结果和描述统计是什么、应该放主文还是 appendix、最容易被审稿人攻击的边界是什么。",
        "",
        "## Recommended Use",
        "",
        "- 主文主表：`G185`。",
        "- 主文展示：`G057`。",
        "- 支撑/敏感性：`G049`, `G177`, `G255`, `G256`。",
        "- 机制/旧框架：`B067`, `G195`。",
        "- 探索性宽口径：`G001`, `G009`, `G017`, `G033`。",
        "",
    ]
    for card in cards:
        lines.extend(
            [
                f"## {card['scale_id']} | {card['scale_role']}",
                "",
                f"**定位：** {card['preferred_placement']}；**支持等级：** {card['support_level']}。",
                "",
                f"**为什么这个 scale 有用：** {card['role_reason']}",
                "",
                f"**具体故事：** {card['story_paragraph_cn']}",
                "",
                f"**可写中文句：** {card['safe_sentences_cn']}",
                "",
                f"**可写英文句：** {card['safe_sentences_en']}",
                "",
                f"**描述统计：** N={card['N_sample']}，grids={card['N_grids_sample']}，main_sample={card['main_sample']}，zone_core={card['zone_core']}，sr_within={card['sr_within']}，region_score={card['region_score']}，irrigation_score={card['irrigation_score']}，phenology_score={card['phenology_score']}。",
                "",
                f"**关键结果：** {card['key_results']}",
                "",
                f"**图表承载：** {card['figure_table_use']}",
                "",
                f"**边界：** {card['risk_boundary']}",
                "",
                f"**需要补的检验：** {card['missing_test']}",
                "",
            ]
        )
    write_text(RUN_DIR / "scale_story_cards.md", "\n".join(lines))


def write_scale_story_matrix(cards: list[dict[str, str]]) -> None:
    lines = [
        "# Scale × Story Matrix",
        "",
        "| scale | role | main story | irrigation | phenology | TE/IE/DE | placement | main risk |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for card in cards:
        scale = card["scale_id"]
        main_story = "region targeting" if scale in {"G185", "G057", "G049", "G177", "G255"} else "legacy/mechanism" if scale in {"B067", "G195"} else "exploratory broad support"
        irrigation = "yes" if "Irrigation:" in card["key_results"] and "未读取" not in card["key_irrigation_stats"] else "partial/no"
        phenology = "yes" if "Phenology:" in card["key_results"] and "未读取" not in card["key_phenology_stats"] else "partial/no"
        teiede = "core" if scale == "B067" else "bridge" if scale == "G195" else "not core"
        lines.append(
            f"| `{scale}` | {card['scale_role']} | {main_story} | {irrigation} | {phenology} | {teiede} | {card['preferred_placement']} | {card['risk_boundary']} |"
        )
    write_text(RUN_DIR / "scale_story_matrix.md", "\n".join(lines))


def build_te_iede_exploration(data: dict[str, list[dict[str, str]]]) -> None:
    b067_story = b067_te_sentence(data)
    channels = iede_channel_sentence(data)
    methods = [
        {
            "method": "TE level by SR quantile",
            "current_support": "已支持，B067 b067_baseline_te_by_sr.csv 有 P25/P50/P75 TE 和 bootstrap CI。",
            "what_it_tells": "直接回答不同 SR 水平下 stress-yield association 是否变弱。",
            "sentence": "At higher SR quantiles, total stress-response losses are less negative under P90 hazards.",
            "risk": "heat/hotdry 的单个 TE level CI 部分跨 0；不能写平均增产。",
            "new_test": "不需要新模型，但建议主文同时报告 delta。"
        },
        {
            "method": "TE(P75)-TE(P25) delta",
            "current_support": "已支持，b067_iede_delta.csv 给出 drought +0.69%、heat +1.30%、hotdry +1.20%，CI 均为正。",
            "what_it_tells": "比 level 更直观，直接表示从低 SR 到高 SR 的减损方向。",
            "sentence": "The P75-minus-P25 contrast indicates an attenuation of P90 stress losses across drought, heat, and hot-dry exposure.",
            "risk": "这是 association contrast，不是处理效应。",
            "new_test": "可直接使用；若进入主图，补公式说明。"
        },
        {
            "method": "Relative attenuation ratio",
            "current_support": "可由 TE level 直接计算；drought 约 40.7%，hotdry 约 76.0%，heat 因跨零更适合谨慎解释。",
            "what_it_tells": "把 TE delta 转成相对减损幅度，便于 Discussion 写 magnitude。",
            "sentence": "Relative attenuation offers a scale-free description of how much of the low-SR stress loss is offset at higher SR.",
            "risk": "当 TE 接近 0 或跨 0 时比例会不稳定，heat 不宜作为强比例证据。",
            "new_test": "不需要新模型，但需要在表注中说明分母和跨零处理。"
        },
        {
            "method": "IE/DE share and sign consistency",
            "current_support": f"已支持但只适合机制解释：{channels}",
            "what_it_tells": "判断某个 hazard 是否更接近 soil-moisture-consistent channel。",
            "sentence": "The decomposition is channel-consistent for drought and hot-dry exposure, but not sufficient to identify a common soil-moisture mediation pathway for heat.",
            "risk": "IE/TE share 在 TE 接近 0 或 DE 与 IE 抵消时不稳定，不能写因果中介。",
            "new_test": "若要强写，补 IE/DE slope difference 的 bootstrap。"
        },
        {
            "method": "Hazard quantile contrast",
            "current_support": "部分支持；B067 有 P90 hazard delta，G057/G185 有 P90 irrigation margins。",
            "what_it_tells": "把不同单位 hazard 转换到同一风险分位点，使 drought/heat/hotdry 可比较。",
            "sentence": "P90 hazard contrasts show where SR-related buffering is largest under comparable stress intensity.",
            "risk": "P90 是情景标准化，不是自然单位效应；需要说明 hazard 单位差异。",
            "new_test": "可扩展到 P75/P95 做 sensitivity。"
        },
        {
            "method": "Stress-response slope flattening across scales",
            "current_support": "已支持；expanded_candidate_ranking.csv 中多 scale 的 min_te_slope 为正，G195/G255 也为正。",
            "what_it_tells": "用于说明故事不是只靠一个 B067 bootstrap 结果，而是跨 scale 的斜率方向。",
            "sentence": "Across candidate scales, the stress-response slope is consistently flatter at higher SR.",
            "risk": "跨 scale 搜索有 multiple testing 和选择性展示风险。",
            "new_test": "需要展示全部 scale 分布和 FDR/Holm 或 family-level 说明。"
        },
    ]
    write_csv(RUN_DIR / "te_iede_exploration.csv", methods, ["method", "current_support", "what_it_tells", "sentence", "risk", "new_test"])
    lines = [
        "# TE/IE/DE Exploration",
        "",
        "用户原始直觉是看不同 SR 水平下的 TE、IE、DE 来评价 SR 效果。这个方向可以保留，但建议不要只看 level，而是形成一组互补指标。",
        "",
        f"## Current B067 Summary\n\n{b067_story}\n\n{channels}",
        "",
        "## Candidate Metrics",
        "",
    ]
    for item in methods:
        lines.extend(
            [
                f"### {item['method']}",
                "",
                f"**当前是否支持：** {item['current_support']}",
                "",
                f"**能说明什么：** {item['what_it_tells']}",
                "",
                f"**可写句：** {item['sentence']}",
                "",
                f"**风险：** {item['risk']}",
                "",
                f"**是否需要新检验：** {item['new_test']}",
                "",
            ]
        )
    write_text(RUN_DIR / "te_iede_exploration.md", "\n".join(lines))


def write_scale_selection_strategy(cards: list[dict[str, str]]) -> None:
    lines = [
        "# Scale Selection Strategy",
        "",
        "## 建议结构",
        "",
        "主文不建议把单一 scale 写成唯一正确 scale，而应写成分工：`G185` 做主表，`G057` 做 region-first 展示，`G049/G177` 做 near-twin sensitivity，`B067/G195` 做 legacy/TE-IE-DE 机制，`G255/G256` 做 strict endpoint appendix，expanded broad scales 做探索性背景。",
        "",
        "## Scale 分工",
        "",
        "| scale | role | reason | risk | required check |",
        "|---|---|---|---|---|",
    ]
    for card in cards:
        lines.append(
            f"| `{card['scale_id']}` | {card['scale_role']} | {card['role_reason']} | {card['risk_boundary']} | {card['missing_test']} |"
        )
    lines.extend(
        [
            "",
        "## 实际写法",
        "",
        "正文中可以说：主结果使用 `G185` 的 clean main-sample 口径，并用 `G057` 展示 region-first 图，因为 G057 的区域分异信号最完整；附录用 `G049/G177/G255/G256` 说明这一结论不是单一 scale 偶然；机制部分使用 `B067/G195`，因为该口径最适合 TE/IE/DE 与旧框架可比性。",
        "",
        "Critic agent 的限制需要同步写入正文策略：`G057/G185` 来自同一搜索空间，不能写成独立外部验证；`B067/G195` 和 `G057/G185` 的任务目标不同，不能把 TE/IE/DE 当作 region-first 机制证明；full-season 联合热旱不应作为主命题，物候期窗口尤其 `HE±10` 和部分 `HE-MA` 才是可写窗口。",
        "",
        "不得说：本研究自动发现了唯一最优 scale；不得把 G057 的显著性当作预注册结果；不得把 B067/G195 的机制结果直接外推为 region-first 主线。",
        ]
    )
    write_text(RUN_DIR / "scale_selection_strategy.md", "\n".join(lines))


def write_review_limitations() -> None:
    write_text(
        RUN_DIR / "review_limitations.md",
        """
        # Review Limitations and Unsafe Claims

        ## 不能写的表述

        - 不能写 `SR causally improves yield`。
        - 不能写 `SR robustly buffers all drought-heat compound losses across the full season`。
        - 不能写 `NW is statistically the strongest region`。
        - 不能写 `TE/IE/DE proves soil moisture mediation`。
        - 不能写 `CA, no-till, residue retention and straw return are interchangeable treatments`。
        - 不能写 `G057 is the pre-specified optimal scale`。

        ## 必须写清楚的边界

        - `G185` 是更适合主表的 clean main-sample scale，`G057` 是 region-first 展示 scale。
        - `B067/G195` 是 legacy/within-grid 机制 scale，不承担 region-first 总主线。
        - `G255` 是 strict sensitivity，不是主文中心 scale。
        - `HE±10` 和 `HE-MA` 支持物候期窗口故事，`full` 和 `V3-HE` 是边界或反例。
        - drought × irrigation 只支持 suggestive complement；heat/hotdry 的替代边界更强。

        ## 必须补的检验

        - region-first family-level 候选分布和 FDR/Holm 或等价多重检验说明。
        - pairwise region claims 必须做多重检验校正；现有审查指出 60 个 pairwise Wald 中未校正 p<0.05 为 24 个，BH 5% 后只有 8 个，Bonferroni 后只有 4 个。
        - scale 桥接表必须并排报告 `G057/G185/G195(B067)/G255(B127)`，同一模型、同一窗口、同一 bootstrap 或 cluster 口径，避免样本口径切换造成解释风险。
        - region×SR×hazard 的正式 Stata/pooled Wald 表。
        - phenology `β_DH + γ_SRDH × SR_q` 的 cluster CI。
        - irrigation overlap/support range。
        - IE/DE slope difference bootstrap，若 stress-specific channel 要进入主文机制图。
        - selection-adjusted 或 quasi-confirmatory 检验至少覆盖 leave-one-year、leave-one-region、province-year FE，在 B067/B127 的同一物候模型中执行。
        """,
    )


def make_figures(cards: list[dict[str, str]], data: dict[str, list[dict[str, str]]]) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        write_text(RUN_DIR / "figure_status.txt", f"matplotlib unavailable: {exc}")
        return

    plot_cards = [c for c in cards if c["scale_id"] in {"G185", "G057", "G049", "G177", "B067", "G195", "G255", "G256"}]
    x = list(range(len(plot_cards)))
    n_values = [num(c.get("N_sample"), 0.0) or 0.0 for c in plot_cards]
    labels = [c["scale_id"] for c in plot_cards]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(x, n_values, color="#4C78A8")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Sample rows")
    ax.set_title("Core scale sample sizes")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_core_scale_sample_sizes.png", dpi=300)
    plt.close(fig)

    hazards = ["drought", "heat", "hotdry"]
    te25 = [num(one(data["b067_te"], hazard=h, ca_level="P25").get("estimate"), 0.0) or 0.0 for h in hazards]
    te75 = [num(one(data["b067_te"], hazard=h, ca_level="P75").get("estimate"), 0.0) or 0.0 for h in hazards]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    width = 0.35
    xs = list(range(len(hazards)))
    ax.bar([i - width / 2 for i in xs], te25, width=width, label="SR P25", color="#E45756")
    ax.bar([i + width / 2 for i in xs], te75, width=width, label="SR P75", color="#54A24B")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(xs)
    ax.set_xticklabels(hazards)
    ax.set_ylabel("TE estimate")
    ax.set_title("B067 TE by SR quantile")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_b067_te_by_sr_quantile.png", dpi=300)
    plt.close(fig)

    region_rows = [r for r in data["region_details"] if r.get("sample_id") in {"G185", "G057"}]
    labels = []
    vals = []
    for row in region_rows:
        if row.get("hazard") in {"drought", "heat", "hotdry"}:
            labels.append(f"{row.get('sample_id')}-{row.get('region')}-{row.get('hazard')}")
            vals.append((num(row.get("scaled_buffer"), 0.0) or 0.0) * 100)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(range(len(vals)), vals, color="#F58518")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels, rotation=70, ha="right", fontsize=7)
    ax.set_ylabel("Scaled buffer (%)")
    ax.set_title("G185/G057 region-hazard scaled buffers")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_g185_g057_region_hazard_buffers.png", dpi=300)
    plt.close(fig)
    write_text(RUN_DIR / "figure_status.txt", "Figures generated successfully.")


def main() -> None:
    ensure_dirs()
    data = load_inputs()
    cards = build_scale_cards(data)
    write_scale_story_cards(cards)
    write_scale_story_matrix(cards)
    build_te_iede_exploration(data)
    write_scale_selection_strategy(cards)
    write_review_limitations()
    make_figures(cards, data)
    print(f"Wrote scale story outputs to {RUN_DIR}")


if __name__ == "__main__":
    main()
