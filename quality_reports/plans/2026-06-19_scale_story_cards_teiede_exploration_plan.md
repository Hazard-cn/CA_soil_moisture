# 2026-06-19 Scale-Level Story Cards and TE/IE/DE Exploration Plan

## 目标

本轮目标是把上一版“候选故事排序”改造成更直观的 `scale -> story -> 可写句子 -> 核心结果 -> 描述统计 -> 风险边界` 输出。用户需要看到每个可用 scale 到底能讲什么、能写哪几句话、对应结果是什么，以及为什么该 scale 适合或不适合进入主文。

## 输出目录

`quality_reports/agent_runs/2026-06-19_scale_story_cards_v2/`

## 固定输出

- `scale_story_cards.md`：每个 scale 的故事卡，包含中文解释、英文可写句、核心结果、描述统计、图表承载和风险边界。
- `scale_story_cards.csv`：机器可读版本，每行对应一个 scale-story。
- `scale_story_matrix.md`：scale × story 的支持矩阵，直观标注主文、支撑、机制、appendix、不能讲。
- `te_iede_exploration.md`：围绕 TE/IE/DE 的现有方式和替代方式，包括 TE delta、level、share、slope flattening、hazard quantile contrast 和 decomposition consistency。
- `scale_selection_strategy.md`：如何处理 G057/G185/B067/G195/G255/G049/G177 等 scale，哪些做主文、哪些做 sensitivity、哪些只做 appendix。
- `descriptive_story_stats.csv`：每个 scale 的样本量、grid 数、region score、irrigation/phenology 支持、核心 margin 和 TE/IE/DE 指标。
- `review_limitations.md`：不能写的表述、必须补的检验和审稿风险。

## Sub-Agent 分工

1. Scale Story Agent：把已有结果重构为每个 scale 的故事卡，重点回答每个 scale 能讲什么。
2. TE/IE/DE Exploration Agent：探索除了看 TE/IE/DE level 之外，还可以如何评价 SR 效果，例如 P75-P25 delta、hazard quantile contrast、relative attenuation、decomposition consistency。
3. Scale Selection Agent：审查 scale 选择逻辑，判断主文 scale、backup scale、legacy scale、strict sensitivity scale 的分工。
4. Critic Agent：只负责降级过强表述，检查 multiple testing、post-hoc window selection、causal language 和 concept substitution。

## 本轮判断规则

- 主文 scale 应优先具备 clean sample、可解释性和复核路径；`G185` 可优先用于主表，`G057` 可用于 region-first 展示。
- `B067/G195` 主要用于 legacy within-grid reference 与 TE/IE/DE 机制解释，不承担 region-first 总主线。
- `G255` 主要作为 strict endpoint sensitivity，不承担主文核心论证。
- `G049/G177` 用于 near-twin scale sensitivity，说明 region-first 不是单一 scale 偶然结果。
- TE/IE/DE 不写因果中介，只写 association decomposition 和 stress-response slope。

## 验收标准

- 每个核心 scale 至少有一段具体故事解释，而不是一句笼统 claim。
- 每个 scale 至少列出一个可以直接写入论文的中文句子和英文句子。
- 每个主文候选 scale 必须列出 N、grid 数、核心结果和至少一个边界。
- TE/IE/DE 必须给出至少三种可尝试的评价方式，并标注当前数据是否已经支持。
- 所有最终文件必须由脚本生成并通过存在性检查。
