---
layout: default
title: G185 旧方法区域 IE/DE/TE 修正版
---

# G185 旧方法区域 IE/DE/TE 修正版

- Canonical ID：`g185-old-method-corrected`
- 分析 scale：`scale-g185`
- 数据基础：`data-v3-expanded` 与 GGCP10 aggregated harvested-area panel
- 首次完成：2026-06-24
- 当前说明更新：2026-07-10

## 估计对象

该版本在每个 region-hazard 组合内分别估计土壤湿度方程和产量方程，并定义 `IE(s) = (a1 + a3*s)b`、`DE(s) = c1 + c3*s`、`TE(s) = IE(s) + DE(s)`。报告对比 SR 从区域 P25 变化到 P75、胁迫固定在区域 P90 时的 TE 差异。

IE、DE 和 TE 是两条方程形成的代数组件，不是已识别的因果中介效应。区域灌溉边界使用单独的连续三重交互规格，不属于该分解。

## 当前核心结果

| 区域与胁迫 | TE 缓冲关联 | 95% 区间 |
|---|---:|---:|
| 东北干旱 | 1.85% | [1.23%, 2.56%] |
| 黄淮海高温 | 3.17% | [2.07%, 4.26%] |
| 黄淮海热干 | 2.43% | [1.04%, 3.87%] |

旧图报告的 1.50%、3.27% 和 2.56% 是控制同期根区土壤湿度后的 `SR × hazard` 差异，属于 DE/residual component；它们不是 `TE = IE + DE` 定义下的 TE。

## 复核入口

- 生成脚本：[`scripts/python/export_g185_old_method_region_tiede_redraw.py`](../../../scripts/python/export_g185_old_method_region_tiede_redraw.py)
- 当前交接：[`quality_reports/handoffs/2026-06-21_g185_method_upgrade_report_handoff.md`](../../../quality_reports/handoffs/2026-06-21_g185_method_upgrade_report_handoff.md)
- 版本定义：[`docs/VERSIONING.md`](../../VERSIONING.md)

完整 bootstrap 表格、图件、压缩审阅包和分析输入保留在本地忽略目录，不上传 GitHub。仓库只发布该可审阅摘要和复现代码；重新估计需要使用者在本地准备相应面板输入。
