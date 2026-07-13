# 2026-06-18 故事线、实证审查与 scale 匹配计划

## 任务目标

本轮使用 `academic-research-suite` 的 pipeline 路由，将 Zotero 文献、现有实证代码和上百条 scale 结果合并审查，形成可以直接用于论文叙事的故事线，并找出每条故事线最匹配的数据 scale、结果证据和现有漏洞。

## 输入材料

- Zotero 最新本地备份：`C:\Users\Lenovo\Zotero\zotero.sqlite.codex-backup-20260618-152113`
- 既有文献整理输出：`temp/2026-06-18_zotero_story_direction/`
- 既有故事线报告：`quality_reports/2026-06-18_zotero_story_direction_review.md`
- 现有 figure framework：`output/figures/f4_b067_v2/figure_captions.md`
- 现有 region-first 搜索与 scale 结果：`temp/2026-06-11_region_first_story_search/` 及相关脚本
- 实证代码目录：`scripts/stata/`、`scripts/python/`、`scripts/R/`

## ARS 路由

由于任务同时包含文献综合、方法审查和结果验证，入口采用 `academic-pipeline`。实质阶段按以下最小 workflow 执行：

1. `deep-research`：从 Zotero 文献建立故事线和反论点。
2. `academic-paper-reviewer`：按 methodology-focus 和 devil's advocate 逻辑审查实证结构、代码与可投稿漏洞。
3. `experiment-agent validate`：验证既有结果、构建 story-scale 匹配评分并识别最小补充检验。

## 工作步骤

1. 复核 Zotero 目标刊物族和本项目核心文献，整理每条故事线的文献支持、反证和可写结论。
2. 读取 figure captions、主要 Stata/Python 脚本、结果表和 scale search 输出，建立可检索的结果索引。
3. 针对灌溉异质性、SR 分位数下的 `te`/`ie`/`de` 解释、region-first 选择、物候期锦上添花定位，逐项查找潜在漏洞。
4. 构建故事线与 scale 的匹配规则：区域一致性、胁迫类型一致性、SR 分位数梯度、水分/灌溉边界、物候期支持、反证风险。
5. 输出一个综合 Markdown 报告，并导出 story-scale 匹配 CSV。

## 产出文件

- `quality_reports/2026-06-18_story_empirical_review_match.md`
- `temp/2026-06-18_story_empirical_review_match/story_scale_match.csv`
- 如需要新增脚本，放在 `scripts/python/`，只读现有结果，不删除或覆盖既有文件。

## 质量边界

- 不把 scale search 写成因果识别。
- 不把 NW 写成显著支持，除非结果文件中确有独立统计支持。
- 不把土壤健康、氮吸收、微生物机制写成本文已识别机制。
- 灌溉处理必须区分控制变量、异质性边界和可能的替代/互补关系。
- `te`/`ie`/`de` 在 SR 分位数中的解释必须先确认变量定义和脚本生成逻辑。
