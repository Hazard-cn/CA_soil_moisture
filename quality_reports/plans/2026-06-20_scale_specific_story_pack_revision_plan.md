# Scale-specific story pack revision plan

## 目标

本轮目标改为：每个候选数据 scale 独立形成一套完整故事，故事内部不得混用其他 scale 的结果。最终再比较各 scale 的故事完整度、证据强度、图表承载能力和审稿风险，推荐唯一可采纳的主版本。

## 候选 scale

本轮按当前候选池处理：`G057`、`G185`、`B067`、`G195`、`G255`、`G256`。若某个 scale 缺少某类结果，不用其他 scale 填补，而是明确写为该 scale 的限制。

## Sub-agent 分工

每个 scale 派一个只读 agent，统一输出：

- `scale`
- `claim`
- `story_paragraph_cn`
- `safe_sentences_cn`
- `safe_sentences_en`
- `core_results`
- `descriptive_stats`
- `figure_plan`
- `unsupported_or_weak_results`
- `explanation_strategy`
- `missing_checks`
- `support_level`
- `main_text_or_appendix`

## Review-revise

第一轮 scale agents 完成后，启动 reviewer agent。Reviewer 只检查三件事：

1. 每条 story 是否混用了其他 scale 的结果。
2. 结论是否超过该 scale 的实证支持。
3. 图表方案是否足以让读者直观看到该 scale 的故事。

随后把 reviewer feedback 发回对应 scale agent，要求它们逐条修正。最终输出由主 orchestrator 只基于修正后的 scale-specific 结果综合。

## 输出

保存到 `quality_reports/agent_runs/2026-06-20_scale_specific_story_pack_v2/`：

- `scale_specific_story_cards.md`
- `scale_specific_story_cards.csv`
- `scale_specific_figure_plan.md`
- `scale_specific_review_round1.md`
- `scale_specific_revision_response_round1.md`
- `final_scale_recommendation.md`

## 约束

不得把 `B067` 的 TE/IE/DE 写进 `G185` 或 `G057` story；不得把 `G057` 的 region-first 结果写进 `G185` story；不得用其他 scale 的显著结果补足本 scale 的弱结果。跨 scale 信息只能出现在最终 comparison 和 recommendation 中。
