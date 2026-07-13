---
layout: default
title: G185 区域连续灌溉边界
---

# G185 区域连续灌溉边界

- Canonical ID：`g185-region-irrigation-boundary`
- 分析 scale：`scale-g185`
- 数据基础：`area-ggcp10-aggregated` 与 `data-v3-expanded`
- 完成日期：2026-06-24
- 状态：`current_parallel`

## 规格与估计量

该包在东北、黄淮海、西北、西南和南方区域内分别重估 old G185 continuous-irrigation model，并排除 `Other`。模型使用 grid fixed effects、year fixed effects、grid-level clustering，以及 999 次 wild-cluster score/bootstrap-linearized draws，随机种子为 42。模型包含焦点胁迫、`ca_raw`、`irr_frac_raw`、全部低阶交互、`SR × hazard × irrigation` 三重交互，以及 companion hazards、降水、ET0、GDD 和 aridity。

主边界为区域灌溉 P75 与 P25 之间的拟合缓冲差异，按 `100 × [exp(triple × (irr_P75 − irr_P25) × regional SR IQR × regional hazard P90) − 1]` 换算。

## 预设主结果

| 区域与胁迫 | P75−P25 边界及 95% 区间 | 判定 |
|---|---:|---|
| 东北干旱 | 1.4738% [0.6862%, 2.3123%] | 支持较高灌溉下拟合缓冲更大 |
| 黄淮海高温 | 0.6488% [-1.2086%, 2.6554%] | 区间跨零，不支持预设边界 |
| 黄淮海热干 | 1.8819% [-0.0457%, 3.7239%] | 区间跨零，不支持预设边界 |

东北干旱在灌溉 P25、P50 和 P75 处的拟合缓冲分别为 0.7487%、1.1869% 和 2.2335%。黄淮海高温在 P25 和 P75 处分别为 3.2317% 和 3.9014%；黄淮海热干分别为 1.9505% 和 3.8691%，但两项 P75−P25 主边界区间均跨零。

其他区域—胁迫组合在本地结果表中作为补充行，`main_story_flag=0`，不作为预设主结论。

## 解释边界与复核入口

这些量是固定效应模型中的条件相关，不是灌溉或 SR adoption 的因果效应。旧的全国灌溉图不能直接作为黄淮海证据。本页的 old-method 区域连续三重交互与 `g185-response-surface-v3` 的 C4 规格不同，二者不能互相替代，也都不属于 IE/DE/TE 分解。

- 生成脚本：[`scripts/python/export_g185_region_specific_irrigation_boundary.py`](../../../scripts/python/export_g185_region_specific_irrigation_boundary.py)
- 执行计划：[`quality_reports/plans/2026-06-24_g185_region_specific_irrigation_boundary_plan.md`](../../../quality_reports/plans/2026-06-24_g185_region_specific_irrigation_boundary_plan.md)
- 旧方法 TE 口径：[`g185-old-method-corrected`](../g185-old-method-corrected/report.md)

本地导出断言已确认不含 `grid_id`、`grid_code`、经纬度、省份、逐 grid-year 数据或 DTA 文件。完整 bootstrap 表格、诊断 JSON、图件和审阅包不上传 GitHub。
