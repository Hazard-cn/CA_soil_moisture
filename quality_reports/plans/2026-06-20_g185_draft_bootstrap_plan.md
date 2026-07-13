# G185 draft and bootstrap execution plan

## Goal

基于单一数据 scale `G185` 生成一版初步 manuscript draft，并补齐可承载主线的实证结果图与 bootstrap 置信区间。所有故事、图和句子只使用 G185，不在同一结论内混用其他 scale。

## Outputs

- `quality_reports/agent_runs/2026-06-20_g185_draft_bootstrap_v1/g185_manuscript_draft.md`
- `quality_reports/agent_runs/2026-06-20_g185_draft_bootstrap_v1/g185_bootstrap_results.csv`
- `quality_reports/agent_runs/2026-06-20_g185_draft_bootstrap_v1/g185_bootstrap_results.md`
- `quality_reports/agent_runs/2026-06-20_g185_draft_bootstrap_v1/figures/*.png`
- `quality_reports/agent_runs/2026-06-20_g185_draft_bootstrap_v1/review_round1.md`
- `quality_reports/agent_runs/2026-06-20_g185_draft_bootstrap_v1/revision_response_round1.md`
- `quality_reports/agent_runs/2026-06-20_g185_draft_bootstrap_v1/review_round2.md`

## ARS sub-agent roles

1. `Empirical Bootstrap/Figure Agent`: 只读数据和现有结果，确认 G185 的可重建变量、模型对象、图形清单和 bootstrap 统计量。
2. `Subjournal Writing Agent`: 只基于 G185 结果和本地 Zotero/既有文献摘要，生成适配 Nature/Science/PNAS 子刊风格的 draft 结构和可写句子。
3. `Reviewer Agent`: 在 draft、图和 bootstrap 完成后进行 independent review，重点检查过强表述、post-hoc scale 选择、bootstrap 可解释性、灌溉/region/phenology 的证据等级。创作和实证工作需要根据反馈至少修订一轮，并接受第二轮复核。

## Empirical scope

主图优先覆盖三组 G185 结果：

1. Region heterogeneity: region × hazard 的 SR buffering magnitude。
2. Irrigation heterogeneity: `irr_frac` 分位点下的 SR buffering margins。
3. Phenology compound stress: HE±10 与 HE-MA 的 D×H slope under low/high SR。

Bootstrap 优先采用 grid-cluster resampling 或基于 grid fixed-effect residualized regression 的 cluster bootstrap。若某些旧结果无法从当前数据列完整重建，则不强行写成主结论，而是标注为 result-table-only evidence 或 appendix candidate。

## Review gates

- Gate 1: G185 样本量、变量列、筛选条件和原结果表对应关系必须写入 run log。
- Gate 2: 每张主图必须有对应 CSV，并注明 bootstrap B、cluster unit、统计量定义。
- Gate 3: Draft 中每个强结论必须对应一张图或一项 bootstrap 表格结果。
- Gate 4: Reviewer 至少两轮；第一轮提出问题，revision response 逐项处理，第二轮给出通过/降级结论。

## Language discipline

写作使用 `conditional association`、`state-dependent buffering`、`targeted adoption` 等非因果表述。避免使用 `causal effect`、`robust mechanism`、`universal benefit`、`mediation proof` 等过强表述。
