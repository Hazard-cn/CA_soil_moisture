---
layout: default
title: G185 方法升级结果
---

# G185 方法升级结果

- Canonical ID：`g185-method-upgrade`
- 分析 scale：`scale-g185`
- 数据基础：`area-ggcp10-aggregated` 与 `data-v3-expanded`
- 主报告完成：2026-06-20
- 解释边界更新：2026-07-10

## 固定效应主结果

主样本包含 46,299 个 grid-year 和 13,236 个 `grid_id` clusters。全国 damage-avoidance margin 定义为拟合 combined stress-response slope 在 SR P75 与 P25 之间的差，并在 hazard P90 处换算为百分比。推断在吸收 grid 和 year fixed effects 后使用 999 次 wild-cluster score/bootstrap-linearized draws，随机种子为 42。该换算是结果报告方式，不构成新的识别策略。

| 胁迫 | Hazard P90 | Damage-avoidance margin | 95% 区间 |
|---|---:|---:|---:|
| 干旱 | 0.918 | 0.57684% | [0.18681%, 0.97725%] |
| 高温 | 143.966644 | 1.15798% | [0.72343%, 1.57217%] |
| 热干 | 44 | 1.14644% | [0.66533%, 1.65052%] |

报告中的区域旧方法值 1.50%、3.27% 和 2.56% 是控制同期根区土壤湿度后的 DE/residual-component contrast，不是总效应。当前重新计算的 TE 分别为东北干旱 1.85022% [1.23153%, 2.55532%]、黄淮海高温 3.16837% [2.06713%, 4.25891%] 和黄淮海热干 2.42543% [1.03896%, 3.87132%]；完整解释见 [`g185-old-method-corrected`](../g185-old-method-corrected/report.md)。

## 连续灌溉交互

该部分是单独的连续三重交互边界，不属于 IE/DE/TE 分解。全国 P75 相对 P25 的拟合缓冲差异为：干旱 +0.66145% [-0.08076%, 1.42547%]，证据较弱；高温 -2.35487% [-3.68410%, -0.95893%]；热干 -1.77556% [-3.15160%, -0.43795%]。区域内 old-method 灌溉结果另见 [`g185-region-irrigation-boundary`](../g185-region-irrigation-boundary/report.md)，两者不能直接替换。

## 机器学习附录边界

机器学习使用确定性子样本 11,999 个 grid-year 和 8,432 个网格；econml 使用 240 棵树，R grf 使用 500 棵树。预设的 10 项 concordance 中只有 2 项通过：econml 五项均未通过，R grf 只有黄淮海高温和热干方向通过。DoubleML PLR 也不能替代固定效应主结果。因此，econml、DoubleML 和 grf 只作为附录级异质性诊断，不能写成机器学习验证 SR adoption impact 或整体复现固定效应结构。

## 解释与复核入口

固定效应 G185 margin 承担本版本的实质陈述。IE、DE 和 TE 是两条方程形成的代数组件，不是已识别的因果中介效应；所有结果应表述为特定样本和规格下的 fitted 或 conditional association。G185 来自探索性 scale 搜索，不能称为唯一最优，也不能混入 G057 或 G049 的估计值。

- 报告生成脚本：[`scripts/python/build_g185_method_upgrade_report.py`](../../../scripts/python/build_g185_method_upgrade_report.py)
- 旧方法修正脚本：[`scripts/python/export_g185_old_method_region_tiede_redraw.py`](../../../scripts/python/export_g185_old_method_region_tiede_redraw.py)
- 当前交接：[`quality_reports/handoffs/2026-06-21_g185_method_upgrade_report_handoff.md`](../../../quality_reports/handoffs/2026-06-21_g185_method_upgrade_report_handoff.md)
- Python 环境：[`requirements-ml.txt`](../../../requirements-ml.txt)

完整机器表、模型对象、图件和审阅包保留在本地忽略目录，不上传 GitHub。
