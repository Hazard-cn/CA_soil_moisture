# 2026-06-19 结论导向 ARS Sub-Agent Storyline 运行计划

## 目标

本轮目标不是搭建通用 sub-agent 系统，而是产出可直接用于论文写作判断的故事线排序、对应数据 scale、核心结果、可写句子和边界条件。Sub-agent 仅作为只读审计、证据匹配和反证工具，最终排序由主 orchestrator 统一收口。

## 输入

- Zotero 本地库与既有 Zotero 导出结果。
- `quality_reports/2026-06-18_story_empirical_review_match.md`
- `quality_reports/2026-06-18_story_followup_margins.md`
- `quality_reports/2026-06-18_story_stata_verify.md`
- `quality_reports/2026-06-18_zotero_story_direction_review.md`
- `temp/2026-06-18_story_empirical_review_match/`
- `temp/2026-06-18_story_followup_margins/`
- `temp/2026-06-18_story_stata_verify/`
- `temp/2026-06-18_zotero_story_direction/`
- `temp/2026-06-11_region_first_story_search/`
- `output/figures/f4_b067_v2/figure_captions.md`

## 输出

所有最终交付物写入：

`quality_reports/agent_runs/2026-06-19_storyline_evidence_engine/60_synthesis/`

固定文件：

- `final_story_ranking.md`
- `final_story_ranking.csv`
- `safe_sentences.md`
- `figure_table_plan.md`
- `review_risk_report.md`

辅助文件写入同一 run 目录下的 `00_context/`、`20_descriptive/`、`50_review/`。

## 输出字段契约

每条故事必须包含：

- `story_id`
- `claim`
- `preferred_scale`
- `backup_scale`
- `core_result`
- `directional_pattern`
- `support_level`
- `zotero_evidence`
- `empirical_evidence`
- `counter_evidence`
- `missing_test`
- `safe_sentence_cn`
- `safe_sentence_en`
- `unsafe_sentence`
- `main_text_or_appendix`

`support_level` 只允许：`strong`、`moderate`、`suggestive`、`exploratory`、`not_supported`。

## Sub-Agent 分工

第一波只读并行：

1. Literature Agent：基于 Zotero 与既有文献导出，核对 Nature、Science、PNAS 及其子刊偏好的结论类型、DOI、Zotero item key 和可写句式。
2. Code Audit Agent：审查 scale search、FE、cluster、TE/IE/DE、灌溉异质性和 Stata 复核是否足以支撑结论。
3. Data Audit Agent：审查样本、变量、缺失、区域/灌溉/物候期支持量和 scale 的样本结构。
4. Result Matcher Agent：把候选故事匹配到 `G057/G185/B067/G195/G255` 等 scale，输出 story × scale 的证据表。

第二波由主 orchestrator 根据第一波结果执行描述统计、图表整理、故事分级和 critic 反证检查。

## 纳入标准

总主线必须同时满足：

- 至少一个主 scale 支持，优先 `G057/G185` 或已经 Stata 复核的 scale。
- 方向与文献命题一致。
- 有明确图表承载路径。
- 有反证或边界条件说明。
- 不依赖单一弱显著结果。
- 不需要超过两个新增检验才能成立。

支撑主线可以有一个维度较弱，但必须达到 `moderate`。机制线和边界条件可为 `suggestive`，但不得写成中心贡献。

## 验证

完成后执行：

1. Python 脚本语法检查。
2. 运行汇总脚本生成所有输出。
3. 检查五个固定交付文件是否存在。
4. 抽查 `final_story_ranking.csv` 的故事等级、scale、核心结果和安全句。
