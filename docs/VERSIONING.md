---
layout: default
title: 版本体系与当前入口
---

# 版本体系与当前入口

## 版本体系的基本限制

本仓库的 Git 历史始于 2026-07-13。此前的 V1-V6、GGCP10、G057/G185 和 G185 内部方法版本在首次 Git 快照中同时出现，因此下述关系是依据文件日期、脚本、计划、报告和 handoff 重建的版本登记，不是可由历史 commit 验证的原始开发顺序。旧版本不会被伪造为过去的 Git commit；从当前状态开始，正式研究节点才使用 Git tag 和 GitHub Release。

## 为什么必须使用命名空间

仓库至少包含五套相互独立的版本或规格编号：

| 命名空间 | 含义 | 示例 |
|---|---|---|
| `report-*` | 2026 年 3 月完整报告和论文框架迭代 | `report-v4`, `report-v6.1` |
| `data-*` / `analysis-*` | 数据管线版本及相应实证重跑 | `data-v2`, `analysis-v3` |
| `mechanism-*` | 2026 年 4 月机制规格实验族 | `mechanism-v5drymed` |
| `area-*` / `scale-*` | GGCP10 面积口径与 Gxxx 样本规则 | `area-ggcp10-aggregated`, `scale-g185` |
| `g185-*` | G185 scale 内部的方法版本 | `g185-method-upgrade` |

`G057`、`G185` 和 `G049` 是 scale 或样本筛选规则，不是软件版本。`g185-response-surface-v3` 也不等于 `data-v3`、`analysis-v3` 或 `report-v3`。

## 当前有效入口

`data-v3-expanded` 是当前共享气候与状态面板；当前 G185 分析同时使用 `area-ggcp10-aggregated` 对应的 GGCP10 aggregated baseline panel 与 `data-v3-expanded`。当前分析 scale 是 `scale-g185`。G185 保留两个并行而不互相替代的入口：

- `g185-old-method-corrected`：旧线性两方程 IE/DE/TE 的当前修正版真值。
- `g185-method-upgrade`：固定效应 damage-avoidance margins 主结果和 ML 附录级异质性一致性检查。

`g185-response-surface-v3` 是已审阅的替代方法和敏感性包；它不替代上述旧方法修正版。`g185-region-irrigation-boundary` 是单独的连续灌溉三重交互结果，不属于 IE/DE/TE 分解。公开结果入口见 [`docs/results/README.md`](results/README.md)。

## 主要历史尝试与改变

### 报告框架线

`report-v1` 汇总 Steps 1-7 的基准固定效应、placebo、土壤湿度衰减、异质性、DML 和敏感性结果；`report-v2` 增加 LOPO、winsorization、非线性、逐年排除和 Oster；`report-v3` 将早期 Baron-Kenny 叙述改为 a-path、attenuation、bootstrap/Sobel 与剂量响应；`report-v4` 将论文主轴转为 D×H 联合胁迫和 SR×D×H；`report-v5` 锁定 Phase 0 分析样本，并增加支持区间、暴露频率、非单调性和 D-H corner 解释；`report-v6.1` 将土壤湿度重新定位为状态变量，并加入 Mundlak、conditioning sets、灌溉和正式两方程分解。该整条报告线是历史框架，不替代当前 G185 入口。

### 数据与 4 月分析线

`data-v1` 是外部共享的 69,038 行 V1 主数据。`data-v2` 建立多窗口、多气候源数据管线，但 2026-04-04 修正了 SPEI 提取方法；因此修正前生成的 `analysis-v2` 结果不能视为自动获得修正。`analysis-v3` 是修正后系统重跑，`data-v3-expanded` 随后增加 capped GDD、多源 hot-dry、旱湿状态和稳定 Stata aliases。`mechanism-v4smstate`、`mechanism-v5drymed` 与 `mechanism-v6gleambl` 是并列机制实验族，现有证据不足以把它们写成严格的逐版替代链。

### GGCP10 与 scale 搜索线

`area-ggcp10-harvarea` 用 GGCP10 harvested area 替换面积相关变量；`area-ggcp10-aggregated` 成为后续面积基础。`ggcp10-mediation-ext` 分为 SM mean、wet-state mirror 和 dry-state top-3 三条探索分支。2026-06-11 的 `scale-search-region-first` 扫描 256 个 Gxxx 规则并复核 208 个高分候选：`scale-g057` 在探索性区域优先搜索中最终排序第一，但不据此写成唯一最优；`scale-g185` 因保留 `main_sample=1` 成为当前主工作流，`scale-g049` 是近似参考，`scale-b067-g195` 保留为历史对照。各 scale 的估计结果不得混用。

### G185 方法线

`g185-draft-bootstrap-v1` 是区域、灌溉和物候的初稿；`g185-method-upgrade` 将固定效应损失规避边际作为主证据，econml、DoubleML 和 R grf 只用于附录级异质性一致性检查；`g185-response-surface-v3` 引入低自由度 drought-heat response surface 和空间 block 推断，其审阅结论包含不支持与敏感项；`g185-old-method-corrected` 纠正了旧图把 DE/residual component 当作 TE 的解释错误；`g185-region-irrigation-boundary` 单独报告区域连续灌溉边界。

## 登记字段与状态词表

Canonical ID 仅使用小写字母、数字、点号和连字符；显示名称单独记录在 `display_name`。`date_start`、`date_updated`、`first_evidence_date` 与 `result_run_date` 使用 ISO `YYYY-MM-DD`，无法确认的日期留空。`parent_id` 表示直接继承，`supersedes_ids` 表示明确取代，`context_ids` 只表示相关背景，三者不得混用。

每个版本必须分别填写 `data_change`、`method_change` 和 `result_presentation_change`。数据字段应说明输入 artifact、样本规则、行数或变量定义变化；方法字段应说明 estimand、exposure、mediator、controls、固定效应、聚类或空间块、bootstrap 和 seed；结果呈现字段应说明表图或报告载体、数值或叙事口径、公开位置及被取代状态。没有变化时也必须明确写明“未变化”或“不适用”，不得留空。逐版本展开结果见 [`VERSION_CHANGELOG.md`](VERSION_CHANGELOG.md)。

物理数据、代码和结果文件登记在 `artifact_registry.csv`，输入输出转换登记在 `data_lineage.csv`，虚拟样本登记在 `sample_rules.csv`，估计方法与运行分别登记在 `method_registry.csv` 和 `analysis_runs.csv`。对话和修改证据只保存脱敏 thread 元数据与命令哈希，不保存原始内容。

`status` 使用受控值：`design_only` 表示未执行的研究设计；`current`、`current_parallel` 和 `current_data_base` 分别表示当前主入口、并行入口和数据基础；`historical_latest`、`historical`、`superseded` 表示历史状态；`exploratory`、`reviewed_sensitivity`、`reference` 表示探索、敏感性和参考用途；`missing_snapshot` 表示明确引用但物理快照缺失；`umbrella` 只用于组织组件，不能直接挂数值结论。

## 后续版本规则

每个改变正式估计对象或公开结论的 PR 都应使用新的 canonical ID 或更新既有 ID，并同步版本登记和公开结果。工作分支使用 `work/<canonical-id>-<topic>`；正式标签使用 `research-<canonical-id>-YYYY.MM.DD`。GitHub Release 只在对应的 Markdown/HTML 结果已经进入 `docs/results/<canonical-id>/` 且 CI 通过后创建。

完整逻辑版本登记位于 [`quality_reports/version_registry.csv`](../quality_reports/version_registry.csv)，规范化明细位于 `quality_reports/lineage/`。`lineage_confidence` 使用 `three-source-confirmed`、`two-source-supported`、`single-source-inferred`、`missing-snapshot` 或 `git-native`；证据等级描述谱系关系的可核验程度，不等同于因果识别或数值复现已经通过。
