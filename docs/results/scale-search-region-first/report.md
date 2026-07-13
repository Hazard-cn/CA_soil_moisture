---
layout: default
title: GGCP10 区域优先 scale 搜索
---

# GGCP10 区域优先 scale 搜索

- Canonical ID：`scale-search-region-first`
- 数据基础：`area-ggcp10-aggregated` 与 `data-v3-expanded`
- 完成日期：2026-06-11
- 性质：探索性规格搜索与当前 scale 选择背景

## 搜索范围与排序规则

搜索对全部 256 个 Gxxx scale 完成 OLS 估计，并对 `region_score >= 14` 的 208 个候选全部完成 `grid_id` 聚类复核；其中 128 个候选的 `region_score=15`，80 个候选的 `region_score=14`，没有候选达到 16/16。最终排序采用区域证据、全国结果、灌溉和物候等分层规则，不是单按某一个未四舍五入分数排序。

| 排名 | Canonical ID | N | 网格数 | Region | National | Irrigation | Phenology | Region evidence |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `scale-g057` | 50,771 | 15,729 | 15/16 | 2/2 | 3/3 | 2/2 | 16.799008 |
| 2 | `scale-g185` | 46,299 | 13,236 | 15/16 | 2/2 | 3/3 | 2/2 | 16.797029 |
| 3 | `scale-g049` | 50,844 | 15,737 | — | — | — | — | — |

G057 与 G185 的打印分数均为 16.80，因此该搜索只能说明 G057 在预设分层规则下最终排序第一，不能据此写成统计上或实质上唯一最优。G185 比 G057 多保留 `main_sample=1` 规则；在继续使用既有主样本口径的条件下，G185 被选为当前主 scale。G049 与 G057 接近，但没有 `sm_sd` 规则。

原 B067 对应 G195，样本为 42,187 个 grid-year 和 11,775 个网格，`region_score=10/16`，未达到进入 208 个聚类复核候选的阈值；该规则只保留为全国与物候框架的历史参考。

## G057 区域证据示例

| 区域与预设胁迫 | Scaled buffer | p 值 | 解释 |
|---|---:|---:|---|
| 东北干旱 | 0.0150198 | 0.00000884 | 与预设方向一致 |
| 黄淮海高温 | 0.0319064 | 0.00000000695 | 与预设方向一致 |
| 西北热干 | 0.0088479 | 0.4885 | 点估计同向，统计证据不足 |
| 西南热干 | 0.0035834 | 0.03774 | 与预设方向一致 |
| 南方热干 | 0.0492054 | 0.01402 | 边界样本结果 |

`scaled_buffer` 是区域 SR 四分位距与胁迫 P90 的换算量，不是政策效应。南方单独模型只有 941 个 grid-year 和 322 个网格，只作为边界结果。

## 区域异质性复核

在 grid fixed effects、region-by-year fixed effects、grid clustering 且各斜率允许按区域变化的 pooled 模型中，G057 的 drought、heat 和 hot-dry 区域同质性 Wald 检验 p 值分别为 0.000152、0.000000617 和 0.006368；G185 对应 p 值分别为 0.000152、0.000000375 和 0.005979。这些检验支持同一 hazard 的 scaled buffer 存在区域异质性，但不检验每个区域内三种 hazard 的主导排序；该排序尚无联合协方差检验。

## 解释边界与复核入口

该流程是结果导向的探索性规格搜索，必须连同完整 256 个候选范围披露。西北结果不显著，G057 与 G185 的分数差异很小，不应把搜索排名解释为因果识别、正式模型选择检验或唯一最优证明。G057、G185 和 G049 的估计值不得在同一 G185 结论中混合。

- 搜索脚本：[`scripts/python/region_first_story_search.py`](../../../scripts/python/region_first_story_search.py)
- G057/G185 复核：[`scripts/stata/verify_story_g057_g185.do`](../../../scripts/stata/verify_story_g057_g185.do)
- 版本登记：[`quality_reports/version_registry.csv`](../../../quality_reports/version_registry.csv)

完整排名表、聚类候选表和 pooled Wald 机器表保留在本地忽略目录，不上传 GitHub；本页只发布汇总结果、方法限制和复现入口。
