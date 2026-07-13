# 2026-06-20 single-scale story pack review-revise plan

## 目标

本轮只解决一个核心问题：论文最终只能采用一版数据时，哪一个 scale 最适合作为唯一数据版本，以及在该 scale 内能讲哪些结论、每个结论由哪些结果和图支持、哪些不支持结果需要弱写或解释。

## 约束

- 不再把不同故事分散到多个主 scale；最终推荐必须给出一个 `recommended_single_scale`。
- 其他 scale 只能作为选择过程证据、反例解释或 appendix sensitivity，不进入主结果叙事。
- 每个候选 scale 的输出必须包含更完整的故事段落，不接受只有一句话的 claim。
- 对单个结论，不要求所有结果都支持，但必须区分 core support、secondary support、contradiction 和 explain-away boundary。
- 继续使用 Zotero 文献和 ARS 工作流；文献只读，不导入、不删除。
- 使用 sub-agent，并设置 reviewer agent；工作 agent 必须在 reviewer 反馈后完成一轮修订。

## Agent 分工

第一轮并行只读：

1. `Scale Decision Agent`：比较 `B067/G195`, `G185`, `G057`, `G255/G256`, `G049/G177`，判断哪个最适合作为唯一数据版本。
2. `Result Support Agent`：读取既有 CSV/Markdown/日志，按候选 scale 汇总 baseline、region、irrigation、phenology、TE/IE/DE、Stata verify 和 descriptive support。
3. `Literature-Zotero Agent`：基于 Zotero 元数据与既有导出，整理 Nature/Science/PNAS 及其子刊可借鉴的结论句式，输出可支持的 safe sentence。
4. `Figure Story Agent`：为每个候选 scale 设计并生成直观图表，优先使用既有结果 CSV，不重估模型。

第二轮：

5. `Reviewer Agent`：按 ARS reviewer + devil's advocate 规则审查第一版 single-scale story pack，重点检查样本切换、post-hoc scale 选择、TE/IE/DE 因果化、region claim 过强、灌溉异质性过度解释。

第三轮：

6. 主 orchestrator 整合 reviewer 反馈，修订输出并明确处理每条 reviewer comment；必要时将反馈发送回对应工作 agent 做补充判断。

## 输出文件

统一写入：

`quality_reports/agent_runs/2026-06-20_single_scale_story_pack_v1/`

必须生成：

- `single_scale_recommendation.md`：唯一推荐 scale、理由、不能选其他 scale 的原因。
- `single_scale_story_pack.md`：推荐 scale 内可讲的故事，每个故事含结论段落、中文/英文句子、结果支持、反例解释、图表。
- `candidate_scale_story_cards.md`：每个候选 scale 的完整故事卡。
- `candidate_scale_story_cards.csv`：机器可读版本。
- `story_support_matrix.csv`：story × result support 矩阵。
- `zotero_literature_support.md`：Zotero 文献支持与可用句式。
- `figures/`：候选 scale 和推荐 scale 的图。
- `review_round1.md`：reviewer 第一轮反馈。
- `revision_response_round1.md`：逐条说明如何处理 reviewer 反馈。
- `review_revised_story_pack.md`：修订后的最终版本。

## 单一 scale 判定标准

优先级从高到低：

1. 该 scale 能支撑最多核心结论，而不是只在一个维度最强。
2. 该 scale 的样本规则可解释，最好有 `main_sample=1`，若有 `zone_core=1` 和 `sr_within=1` 更优。
3. 该 scale 能承载用户关心的 TE/IE/DE 或能明确解释为什么 TE/IE/DE 只作为旧框架旁证。
4. 有足够的 region、irrigation、phenology、compound hazard 结果可画图。
5. 不依赖单一弱显著结果；反例可在边界条件中解释。
6. 不需要超过两个新增检验才能作为主文结论。

## 质量 gate

- 每条主结论必须至少有一个 core support 和一个 secondary support。
- 每条主结论必须有至少一个 boundary 或 counter-result 的处理。
- 所有因果表述必须替换为 `conditional association`, `state-dependent buffering`, `stress-response slope` 等非因果语言。
- reviewer 的所有 critical/major comments 必须在 `revision_response_round1.md` 中逐条处理。
