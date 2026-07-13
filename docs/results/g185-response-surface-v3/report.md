---
layout: default
title: G185 响应面 v3 审阅摘要
---

# G185 响应面 v3 审阅摘要

- Canonical ID：`g185-response-surface-v3`
- 分析 scale：`scale-g185`
- 数据基础：`area-ggcp10-aggregated` 与 `data-v3-expanded`
- 审阅完成：2026-06-21
- 状态：`reviewed_sensitivity`

## 主规格

主模型 `RS_REG_PYFE_NOSM_C0` 使用规则型 G185 样本；全样本包含 46,299 个 grid-year 和 13,236 个网格，五个命名区域的主模型样本包含 44,556 个 grid-year、12,745 个网格和 19 个省份。因变量为 `ln_yield_raw`。模型包含 grid fixed effects、province-by-year fixed effects、区域特定的四结点 restricted cubic spline drought-heat response surface、`SR_c × surface` 交互，以及 `W_full_raw` 和 `gdd_10_30_raw` 两项 C0 控制，不加入同期土壤湿度。

主推断使用 2° 空间块、149 个块和 1,999 次 Rademacher wild-score linearized draws，随机种子为 20260620。残差化 normal-equation 内部复核的最大绝对误差和相对误差均为 0，状态为 `PASS`。

## 预设结论判定

| Claim | 点估计及 95% 区间 | p / q | 正式状态 |
|---|---:|---:|---|
| 东北干旱 | -0.0999% [-0.7916%, 0.6294%] | 0.7834 / 0.9793 | `NOT_SUPPORTED` |
| 黄淮海高温 | 0.2083% [-0.3727%, 0.7910%] | 0.5001 / 0.9793 | `SUPPORTED_BUT_SENSITIVE` |
| 黄淮海联合干旱—高温 | 0.0911% [-0.4775%, 0.6615%] | 0.7717 / 0.9793 | `SUPPORTED_BUT_SENSITIVE` |
| 黄淮海热干方向验证 | total 0.2625% [0.0401%, 0.4854%]；incremental 0.0865% [-0.0614%, 0.2346%] | 0.0207；0.2519 | `SUPPORTED_BUT_SENSITIVE` |
| 土壤湿度一致性 | 无单一总估计 | — | `NOT_SUPPORTED` |

黄淮海高温和联合情景的主区间均跨零，只能表述为敏感的条件相关；热干结果只作为方向性验证，不能替代 drought-heat tensor 支持诊断。稳健性矩阵中，黄淮海高温为 22/26 项通过，联合情景为 23/26 项通过，东北干旱仅 4/26 项通过。

区域差异的 omnibus Wald 检验均不显著：drought `p=0.4379`、heat `p=0.1046`、joint `p=0.7783`。黄淮海与东北 heat pairwise test 的原始 `p=0.0328`，多重校正后 `q=0.1311`，不能表述为校正后显著的区域差异。

## 灌溉与土壤湿度诊断

v3 C4 灌溉诊断中，黄淮海高温从 P25 的 0.6916% 降至 P75 的 0.3950%，差值约 -0.2965 个百分点；联合情景从 -0.1223% 升至 0.6660%，差值约 +0.7884 个百分点。两个情景方向相反，综合边界判定敏感，未形成统一方向；该结果也不同于 old-method 区域连续三重交互。

土壤湿度方向同样不一致。黄淮海高温的 root-zone 和 surface soil moisture 变化分别约为 +0.00019 SD 和 -0.00020 SD，区间均跨零；联合情景两项均为负且区间跨零。加入同期土壤湿度后，高温缓冲由约 0.2083% 变为 0.1984%，联合情景由约 0.0903% 变为 0.1587%，不存在一致衰减。因此，该版本不支持 mediation 或已确认 pathway 的表述。

## 复核入口

- 执行入口：[`scripts/python/run_all_g185_v3.py`](../../../scripts/python/run_all_g185_v3.py)
- 执行计划：[`quality_reports/plans/2026-06-21_g185_response_surface_v3_execution_plan.md`](../../../quality_reports/plans/2026-06-21_g185_response_surface_v3_execution_plan.md)
- 版本登记：[`quality_reports/version_registry.csv`](../../../quality_reports/version_registry.csv)

审阅 README、claim adjudication、key estimands、模型注册、稳健性矩阵和机器表保留在本地忽略目录，不上传 GitHub。本页不替代 `g185-old-method-corrected` 的区域 TE 口径。
