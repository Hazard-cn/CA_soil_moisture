---
layout: default
title: 2026 年逐版本变化详表
---

# 2026 年逐版本变化详表

> 本页由 `scripts/python/version_lineage.py build-docs` 生成。每个版本分别说明数据、方法和结果呈现变化；Git 前版本是证据重建，不代表存在可 checkout 的同期提交。
> `sample_rules.csv` 的行数、grid 数和区域计数均指规则 mask 的原始支持；回归运行还可能因模型变量缺失形成更小的 complete-case 样本，两者不得混用。

## `design-2026-02` — RR research blueprint 2026-02-10

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-02-10；`design_only`；`design_document` |
| 父版/取代关系 | parent=`none`；supersedes=`none` |
| 当前用途 | Historical design context；truth role=`design_reference` |
| 证据 | `three-source-confirmed`；关联脱敏对话 2 个 |

### 数据变化

未生成或锁定分析数据；仅引用研究设想中的潜在数据类型；不把蓝图日期推定为数据构建日期

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `design-2026-02-blueprint-pdf` | research-design | present | 未记录 | `local://RR_blueprints20260210.pdf` |

### 方法变化

未执行估计；仅列出候选研究问题和方法方向；无固定效应、聚类、bootstrap或seed的可验证运行

### 结果呈现变化

载体为本地PDF研究蓝图；属于design-only参考；不作为实证结果或当前结论

### 相对前版与证据边界

- 综合变化：Recorded the pre-analysis research blueprint without treating it as an implemented method
- 证据限制：Design evidence only; it does not establish a dataset build or empirical run

## `data-v1` — V1 external master panel

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-03-12；`reference`；`logical_data_version` |
| 父版/取代关系 | parent=`none`；supersedes=`none` |
| 当前用途 | Reference data base；truth role=`historical_data_reference` |
| 证据 | `three-source-confirmed`；关联脱敏对话 14 个 |

### 数据变化

登记外部69038行、143列V1 grid-year家族；当前文件观测时间为2026-01-29，但本仓库内可验证的分析使用证据始于2026-03-12；V1-family定义为yield_tons_ha=maize_prod/maize_area_km2*10

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `data-v1-master` | data-base | present | 69038×143 | `external://CA_mechanism/data/master/data_v1_with_climate.csv` |

基于本版本数据形成、由下游节点使用的派生规则：

#### `sample-v1-full` — V1 full grid-year panel

- 谓词：`{"constant":true}`。
- 规则向量：`all_rows`。
- 样本规模：rows=69038；grids=22180；区域计数=`{}`。
- 规则代码：`未记录`；代码 SHA-256=`未记录`。
- 状态：`reference`；verified_at=`2026-07-14`；supersedes=`none`。

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `data-v1-county-city` | 2026-03-22 | `historical` | Added county and city identifiers through coordinate-to-polygon matching |

### 方法变化

不涉及估计方法；数据生成过程在本仓库Git前且无法由commit复核；仅登记schema和来源

### 结果呈现变化

仅公开README和DATA_SOURCES元数据；CSV/DTA保持local且不上传；作为历史数据参考

### 相对前版与证据边界

- 综合变化：Registered the 69038-row V1 grid-year family and its physical variants
- 证据限制：2026-01-29 is the observed file timestamp, not a confirmed build date; first repository analysis evidence is 2026-03-12; V1 uses maize_prod/maize_area_km2*10, whereas GGCP10 changes the area denominator

## `report-v1` — Complete report v1

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-03-13；`historical`；`report_version` |
| 父版/取代关系 | parent=`none`；supersedes=`none` |
| 当前用途 | Historical framework；truth role=`historical_framework` |
| 证据 | `single-source-inferred`；关联脱敏对话 1 个 |

### 数据变化

使用外部V1 69038行、143列grid-year面板；沿用V1 yield_tons_ha定义；未建立独立数据快照

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `report-v2` | 2026-03-13 | `superseded` | Added Step 7B, LOPO, winsorization, nonlinear checks, leave-year-out and Oster |

### 方法变化

汇总grid/year FE基准、placebo、SM attenuation、异质性、DML和敏感性；默认grid聚类；各脚本seed按项目规则为42

#### `method-report-v1`

- Outcome / estimand：ln_yield and annual SM outcomes；Baseline SR-associated hazard buffering and diagnostic attenuation。
- Exposure / mediator：SPEI drought; wetness; HDD heat; SR interactions；GLEAM surface or root-zone SM in selected steps。
- Controls / FE：Irrigation; precipitation; ET0; aridity; GDD; soil controls by step；Primarily grid FE plus year FE。
- Inference：Primarily grid-clustered standard errors; DML and sensitivity modules vary；bootstrap=Varies by included historical step；reps=none；seed=42。
- 代码入口：`local://output/reports/complete_report.Rmd`。
- 解释边界：Historical synthesis only; constituent scripts do not establish one unified causal estimand。

### 结果呈现变化

载体为complete_report.Rmd；首次综合Steps 1-7；仅作历史框架且v1编号由后续序列反推

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-report-v1-20260313` | `data-v1-master` | `未冻结` | `method-report-v1` | `local://output/reports/complete_report.Rmd` | `local://output/reports/complete_report.Rmd` | `未公开` | historical_static |

### 相对前版与证据边界

- 综合变化：Combined Steps 1-7 baseline FE, placebo, SM attenuation, heterogeneity, DML and sensitivity
- 证据限制：The v1 label is inferred from the later report sequence

## `report-v2` — Complete report v2

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-03-13；`superseded`；`report_version` |
| 父版/取代关系 | parent=`report-v1`；supersedes=`report-v1` |
| 当前用途 | Historical QA；truth role=`historical_qa` |
| 证据 | `two-source-supported`；关联脱敏对话 2 个 |

### 数据变化

相对report-v1继续使用外部V1面板；数据口径未发生已验证改变；没有新的冻结样本

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `report-v3` | 2026-03-17 | `superseded` | Reframed mechanism evidence around a-path, attenuation, bootstrap or Sobel and dose response |

### 方法变化

在既有FE主线增加LOPO、winsorization、非线性、leave-year-out、Oster和Step 7B；不改变核心estimand

#### `method-report-v2`

- Outcome / estimand：ln_yield and annual SM outcomes；report-v1 estimands plus robustness sensitivity。
- Exposure / mediator：Drought; wetness; heat; SR interactions；GLEAM SM in selected steps。
- Controls / FE：Baseline and extended climate or soil controls；Grid FE plus year FE with alternative robustness structures。
- Inference：Grid-clustered inference plus LOPO, leave-year-out, Oster and winsorization diagnostics；bootstrap=Varies by included historical step；reps=none；seed=42。
- 代码入口：`local://output/reports/complete_report_v2.Rmd`。
- 解释边界：Robustness expansion does not convert conditional associations into causal effects。

### 结果呈现变化

载体变为complete_report_v2.Rmd；扩充QA和稳健性章节；已被后续报告版取代

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-report-v2-20260313` | `data-v1-master` | `未冻结` | `method-report-v2` | `local://output/reports/complete_report_v2.Rmd` | `local://output/reports/complete_report_v2.Rmd` | `未公开` | historical_static |

### 相对前版与证据边界

- 综合变化：Added Step 7B, LOPO, winsorization, nonlinear checks, leave-year-out and Oster
- 证据限制：Pre-Git parent relation is reconstructed

## `report-v3` — Complete report v3

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-03-17；`superseded`；`report_version` |
| 父版/取代关系 | parent=`report-v2`；supersedes=`report-v2` |
| 当前用途 | Historical framework only；truth role=`historical_framework` |
| 证据 | `two-source-supported`；关联脱敏对话 2 个 |

### 数据变化

继续使用V1面板；未发现相对report-v2的独立数据构建；样本口径仍由各脚本决定

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `report-v4` | 2026-03-17 | `historical` | Shifted the main framing to D by H compound stress and SR by D by H |

### 方法变化

把机制叙述组织为a-path、attenuation、bootstrap或Sobel和dose response；当时仍采用历史中介措辞

#### `method-report-v3`

- Outcome / estimand：ln_yield and SM outcomes；Historical a-path, attenuation and conditional-effect diagnostics。
- Exposure / mediator：Drought; heat; SR by hazard interactions；Multiple annual SM measures。
- Controls / FE：Climate, irrigation and soil controls by module；Grid FE plus year FE; selected alternative FE。
- Inference：Clustered standard errors with historical Sobel or bootstrap diagnostics；bootstrap=Historical mixed procedures；reps=none；seed=42。
- 代码入口：`local://output/reports/complete_report_v3.Rmd`。
- 解释边界：Historical mediation terminology is superseded; retain only as reconstructed report logic。

### 结果呈现变化

载体为complete_report_v3.Rmd；机制章节成为主要叙事；其因果中介措辞已被后续代数组件口径取代

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-report-v3-20260317` | `data-v1-master` | `未冻结` | `method-report-v3` | `local://output/reports/complete_report_v3.Rmd` | `local://output/reports/complete_report_v3.Rmd` | `未公开` | historical_static |

### 相对前版与证据边界

- 综合变化：Reframed mechanism evidence around a-path, attenuation, bootstrap or Sobel and dose response
- 证据限制：Not analysis-v3 or data-v3-expanded

## `report-v4` — Complete report v4

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-03-17；`historical`；`report_version` |
| 父版/取代关系 | parent=`report-v3`；supersedes=`report-v3` |
| 当前用途 | Historical compound-stress framework；truth role=`historical_compound_framework` |
| 证据 | `two-source-supported`；关联脱敏对话 7 个 |

### 数据变化

继续使用V1面板；增加D、H及其复合暴露的分析变量；未改变基础outcome定义

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `report-v5` | 2026-03-22 | `superseded` | Locked the Phase 0 sample and added exposure frequency, support bounds, non-monotonicity and D-H corner interpretation |

### 方法变化

主estimand转为D×H超加性损失及SR×D×H斜率修饰；grid/year FE与grid聚类为主体；加入joint-stress诊断

#### `method-report-v4`

- Outcome / estimand：ln_yield；Drought by heat superadditivity and SR-associated change in the compound-damage slope。
- Exposure / mediator：Drought; wetness; HDD30/32/35; D by H; SR by D by H；SM is a state or control in selected diagnostics。
- Controls / FE：Irrigation; precipitation; ET0; aridity; GDD; soil controls；Grid FE plus year FE; region-year or province-year in robustness。
- Inference：Grid or two-way clustered standard errors depending on specification；bootstrap=Selected wild-cluster checks in boundary scripts；reps=none；seed=42。
- 代码入口：`local://output/reports/complete_report_v4.Rmd`。
- 解释边界：Compound-stress conditional association; not a causal adoption effect。

### 结果呈现变化

载体为complete_report_v4.Rmd和analysis_specification.md；主叙事从单通道机制转为联合胁迫；保留为历史框架

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-report-v4-20260317` | `data-v1-master` | `未冻结` | `method-report-v4` | `local://output/reports/complete_report_v4.Rmd` | `local://output/reports/complete_report_v4.Rmd` | `未公开` | historical_static |

### 相对前版与证据边界

- 综合变化：Shifted the main framing to D by H compound stress and SR by D by H
- 证据限制：Does not replace current G185 entries

## `data-v1-county-city` — V1 county-city enriched panel

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-03-22；`historical`；`physical_data_snapshot` |
| 父版/取代关系 | parent=`data-v1`；supersedes=`none` |
| 当前用途 | Input to the locked Phase 0 panel；truth role=`historical_data_component` |
| 证据 | `three-source-confirmed`；关联脱敏对话 5 个 |

### 数据变化

在V1基础上按经纬度匹配2019县市多边形；新增county_name/code和city_name/code；行数设计上保持V1 panel不变

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `data-v1-county-city` | data-sidecar | present | 69038×147 | `external://CA_mechanism/data/master/data_v1_with_climate_with_county_city.csv` |

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `data-v1-locked-panel` | 2026-03-22 | `historical` | Locked the main estimation sample and generated county or city FE identifiers |

### 方法变化

使用县界within匹配并对未匹配点采用市域约束最近县回退；不涉及回归estimand、FE或bootstrap

### 结果呈现变化

产出为外部local CSV及匹配日志；Git仅保留构建脚本；作为locked panel上游组件

### 相对前版与证据边界

- 综合变化：Added county and city identifiers through coordinate-to-polygon matching
- 证据限制：The CSV remains outside Git

## `data-v1-locked-panel` — V1 locked Phase 0 panel

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-03-22；`historical`；`physical_data_snapshot` |
| 父版/取代关系 | parent=`data-v1-county-city`；supersedes=`none` |
| 当前用途 | Input to late report-line and V2 build work；truth role=`historical_analysis_input` |
| 证据 | `three-source-confirmed`；关联脱敏对话 1 个 |

### 数据变化

由county-city V1构建analysis_main_sample.dta；冻结main_sample并新增county_id、county_year、city_id；本地文件存在

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `data-v1-locked-panel` | analysis-panel | present | 69038×181 | `local://data/processed/analysis_main_sample.dta` |

基于本版本数据形成、由下游节点使用的派生规则：

#### `sample-v1-locked-main` — V1 Phase 0 locked main sample

- 谓词：`{"column":"main_sample","operator":"==","value":1}`。
- 规则向量：`main_sample=1`。
- 样本规模：rows=61795；grids=17832；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/step0_sample_and_macros.do`；代码 SHA-256=`83faa097864cb40ab9ba9643110cde00f4f10a0c9a285c54c8e352b0e6645157`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`none`。

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `data-v2` | 2026-03-29 | `historical` | Built multi-window and multi-source climate inputs; SPEI extraction was corrected on 2026-04-04 |

### 方法变化

Stata预处理执行xtset grid_id year并以当时基准回归e(sample)定义主样本；set seed 42；不产生新的研究estimand

### 结果呈现变化

产出为local DTA和日志；供report-v5/v6及V2管线使用；不公开二进制数据

### 相对前版与证据边界

- 综合变化：Locked the main estimation sample and generated county or city FE identifiers
- 证据限制：The local panel is ignored by Git

## `report-v5` — Complete report v5

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-03-22；`superseded`；`report_version` |
| 父版/取代关系 | parent=`report-v4`；supersedes=`report-v4` |
| 当前用途 | Historical framework；truth role=`historical_framework` |
| 证据 | `two-source-supported`；关联脱敏对话 2 个 |

### 数据变化

改用2026-03-22生成的V1 county-city enriched locked panel；Phase 0样本通过analysis_main_sample.dta冻结；新增county/city标识

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `report-v6.1` | 2026-03-23 | `historical_latest` | Repositioned SM as a state variable and added Mundlak, conditioning sets, irrigation and two-equation decomposition |

### 方法变化

在report-v4联合胁迫框架上增加支持区间、暴露频率、非单调性和D-H corner诊断；部分规格使用county/year FE

#### `method-report-v5`

- Outcome / estimand：ln_yield on locked Phase 0 sample；Compound-damage and support-bounded SR interaction margins。
- Exposure / mediator：Drought; heat; compound exposure; SR interactions；SM state in selected models。
- Controls / FE：Climate, irrigation, aridity and soil controls；Grid/year FE and selected county/year FE。
- Inference：Clustered standard errors at the absorbed spatial unit；bootstrap=Selected bootstrap and leave-out diagnostics；reps=none；seed=42。
- 代码入口：`local://output/reports/complete_report_v5.Rmd`。
- 解释边界：Historical locked-sample framework; D-H corner anomalies remain a limitation。

### 结果呈现变化

载体为complete_report_v5.Rmd；明确锁样本和边界解释；后被report-v6.1取代

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-report-v5-20260322` | `data-v1-locked-panel` | `未冻结` | `method-report-v5` | `local://output/reports/complete_report_v5.Rmd` | `local://output/reports/complete_report_v5.Rmd` | `未公开` | historical_static |

### 相对前版与证据边界

- 综合变化：Locked the Phase 0 sample and added exposure frequency, support bounds, non-monotonicity and D-H corner interpretation
- 证据限制：A report label and not mechanism-v5drymed

## `report-v6.1` — Complete report v6.1

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-03-23；`historical_latest`；`report_version` |
| 父版/取代关系 | parent=`report-v5`；supersedes=`report-v5` |
| 当前用途 | Latest report-line framework；truth role=`historical_report_latest` |
| 证据 | `two-source-supported`；关联脱敏对话 3 个 |

### 数据变化

主要依赖V1 locked panel并沿用V1 outcome；不同章节仍可能使用不同common sample；未统一为GGCP10样本

### 方法变化

将SM改写为state variable；加入Mundlak、conditioning sets、灌溉边界和两方程分解；FE可含grid/year或county/year并按对应单位聚类

#### `method-report-v6.1`

- Outcome / estimand：ln_yield and SM state outcomes；State dependence, conditioning-set sensitivity and algebraic two-equation components。
- Exposure / mediator：Drought; wetness; heat; SR interactions; irrigation interactions；GLEAM surface or root-zone SM and state variables。
- Controls / FE：Climate, irrigation, aridity, soil and Mundlak controls by chain；Grid/year or county/year FE by chain。
- Inference：Clustered standard errors at grid or county level；bootstrap=Selected county-cluster bootstrap in historical scripts；reps=none；seed=42。
- 代码入口：`local://output/reports/complete_report_v6.Rmd`。
- 解释边界：Latest report-line framework only; not the current G185 truth source。

### 结果呈现变化

载体文件名为complete_report_v6.Rmd而显示版本为v6.1；是报告线最后历史版；不代表当前G185真值

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-report-v6.1-20260323` | `data-v1-locked-panel` | `未冻结` | `method-report-v6.1` | `local://output/reports/complete_report_v6.Rmd` | `local://output/reports/complete_report_v6.Rmd` | `未公开` | historical_static |

### 相对前版与证据边界

- 综合变化：Repositioned SM as a state variable and added Mundlak, conditioning sets, irrigation and two-equation decomposition
- 证据限制：Not the current G185 truth entry

## `data-v2` — V2 climate pipeline

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-03-29；`historical`；`logical_data_version` |
| 父版/取代关系 | parent=`data-v1-locked-panel`；supersedes=`none` |
| 当前用途 | Historical data family；truth role=`historical_data_family` |
| 证据 | `three-source-confirmed`；关联脱敏对话 10 个 |

### 数据变化

从V1 locked panel扩展多物候窗口、多气候源和SM变量；2026-04-04修正SPEI endpoint提取；逻辑版本包含两个不同schema快照

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `data-v2-main-pre-spei-fix` | 2026-03-29 | `missing_snapshot` | Produced the 69038-row and 523-column V2 main panel used by analysis-v2 |
| `data-v2-main-post-spei-fix` | 2026-04-04 | `missing_snapshot` | Corrected endpoint SPEI extraction and expanded the panel to 621 columns for the V3 systematic rerun |
| `data-v3-expanded` | 2026-04-07 | `current_data_base` | Added capped GDD; retained and expanded multi-source soil-moisture-threshold hot-dry; separately added precipitation-threshold hot-dry; stabilized Stata aliases |

### 方法变化

Python数据管线执行窗口计算、合并和质量检查；不涉及结果估计；修正改变D/W exposure输入而非回归器形式

### 结果呈现变化

载体为CHANGELOG和VARIABLES_v2.md；两个data_v2_main物理快照均已缺失；保留逻辑谱系

### 相对前版与证据边界

- 综合变化：Built multi-window and multi-source climate inputs; SPEI extraction was corrected on 2026-04-04
- 证据限制：The two same-path data_v2_main snapshots are represented separately

## `data-v2-main-pre-spei-fix` — V2 main pre-SPEI-fix snapshot

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-03-29；`missing_snapshot`；`missing_physical_snapshot` |
| 父版/取代关系 | parent=`data-v2`；supersedes=`none` |
| 当前用途 | Unavailable historical input snapshot；truth role=`historical_missing_input` |
| 证据 | `missing-snapshot`；关联脱敏对话 1 个 |

### 数据变化

69038行、523列；使用修正前window SPEI提取；曾位于data_build/data/processed/data_v2_main.dta；当前缺失

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `data-v2-main-initial-missing` | data-build-snapshot | missing | 69038×523 | `local://data_build/data/processed/data_v2_main.dta` |

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `data-v2-analysis-ready` | 2026-04-02 | `historical` | Constructed drought and wetness windows, interactions, controls and a locked V2 analysis sample |

### 方法变化

数据构建方法为V2初始多窗口管线；无估计、FE、cluster或bootstrap；其D/W变量输入后来被纠正

### 结果呈现变化

无可发布数据载体；仅由v2_step0头部和CHANGELOG留痕；状态为missing-snapshot且不得用后版替代

### 相对前版与证据边界

- 综合变化：Produced the 69038-row and 523-column V2 main panel used by analysis-v2
- 证据限制：The former local data_build/data/processed/data_v2_main.dta is missing and cannot be substituted by a later file

## `analysis-v2` — V2 systematic analysis

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-02；`superseded`；`analysis_version` |
| 父版/取代关系 | parent=`none`；supersedes=`none` |
| 当前用途 | Historical diagnostic；truth role=`historical_diagnostic` |
| 证据 | `three-source-confirmed`；关联脱敏对话 5 个 |

### 数据变化

输入为pre-SPEI-fix的v2_analysis_ready；样本由V2 preamble定义；没有获得2026-04-04修正

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `analysis-v3` | 2026-04-04 | `historical` | Reran the systematic specifications after the SPEI correction and added period and bootstrap updates |

### 方法变化

约190个FE规格覆盖窗口、SM来源、stage和interaction grid；主要吸收grid/year并按grid聚类；seed 42

#### `method-analysis-v2`

- Outcome / estimand：ln_yield and six SM source-depth outcomes；Window-specific SR-associated buffering, stage responses and interaction-grid diagnostics。
- Exposure / mediator：SPEI drought/wetness; HDD heat; SR by hazard; compound interactions；Annual SM measures in mediation or attenuation models。
- Controls / FE：Window precipitation; ET0; GDD; irrigation; aridity; soil controls；Grid FE plus year FE。
- Inference：Grid-clustered standard errors；bootstrap=Selected historical bootstrap modules；reps=500；seed=42。
- 代码入口：`repo://scripts/stata/v2_step1_baseline_fullseason.do`。
- 解释边界：Uses the pre-SPEI-fix input; results cannot be treated as corrected V3 evidence。

### 结果呈现变化

载体为2026-04-02本地结果summary及表格；结论为SR×D不稳定和跨源SM混合；被analysis-v3取代

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-analysis-v2-20260402` | `data-v2-analysis-ready` | `未冻结` | `method-analysis-v2` | `repo://scripts/stata/v2_step1_baseline_fullseason.do` | `local://quality_reports/2026-04-02_v2_full_results_summary.md` | `未公开` | blocked_upstream_snapshot |

### 相对前版与证据边界

- 综合变化：Ran about 190 regressions and found unstable SR by D and mixed cross-source SM evidence
- 证据限制：Predates the SPEI correction

## `data-v2-analysis-ready` — V2 analysis-ready panel

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-02；`historical`；`physical_data_snapshot` |
| 父版/取代关系 | parent=`data-v2-main-pre-spei-fix`；supersedes=`none` |
| 当前用途 | Reproducible evidence for analysis-v2 conditional on the missing upstream snapshot；truth role=`historical_analysis_input` |
| 证据 | `three-source-confirmed`；关联脱敏对话 1 个 |

### 数据变化

从523列pre-fix快照生成本地v2_analysis_ready.dta；构造五窗口D/W、SR交互、SM交互和locked sample

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `data-v2-analysis-ready` | analysis-panel | present | 69038×649 | `local://data/processed/v2_analysis_ready.dta` |

基于本版本数据形成、由下游节点使用的派生规则：

#### `sample-v2-main` — V2 analysis main sample

- 谓词：`{"column":"main_sample","operator":"==","value":1}`。
- 规则向量：`main_sample=1`。
- 样本规模：rows=62018；grids=17898；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/v2_step0_preamble.do`；代码 SHA-256=`ae70539362534fc2fc36e25dd65ab14d283ac027ab5646f919a365b050d81bcf`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`none`。

### 方法变化

Stata xtset grid_id year；基准FE样本由回归e(sample)锁定；后续模型使用grid/year FE与grid聚类；seed 42

### 结果呈现变化

载体为local DTA和V2结果表；可复核下游但无法完整重建缺失的上游快照；历史输入

### 相对前版与证据边界

- 综合变化：Constructed drought and wetness windows, interactions, controls and a locked V2 analysis sample
- 证据限制：The physical output exists locally

## `analysis-v3` — V3 corrected systematic analysis

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-04；`historical`；`analysis_version` |
| 父版/取代关系 | parent=`analysis-v2`；supersedes=`analysis-v2` |
| 当前用途 | Historical foundation；truth role=`historical_foundation` |
| 证据 | `three-source-confirmed`；关联脱敏对话 1 个 |

### 数据变化

使用621列post-SPEI-fix快照构建v3_analysis_ready；加入V3pre30并统一修正后的SPEI endpoint；基础N仍为69038

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `data-v3-analysis-ready` | analysis-panel | present | 69038×772 | `local://data/processed/v3_analysis_ready.dta` |

基于本版本数据形成、由下游节点使用的派生规则：

#### `sample-v3-main` — V3 corrected analysis main sample

- 谓词：`{"column":"main_sample","operator":"==","value":1}`。
- 规则向量：`main_sample=1`。
- 样本规模：rows=62018；grids=17898；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/v3_step0_preamble.do`；代码 SHA-256=`d4a24cf9f7662da08b746924eb46ae17e3928b76ddfba817193affe78d37785b`。
- 状态：`reference`；verified_at=`2026-07-14`；supersedes=`sample-v2-main`。

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `analysis-v3-modules` | 2026-04-07 | `historical` | Added precipitation hot-dry, multi-source SM outcomes, algebraic decomposition, sample boundaries and b-path audit |

### 方法变化

在analysis-v2规格族上重跑baseline、stage、SM comparison、mediation和robustness；grid/year FE、grid cluster、seed 42

#### `method-analysis-v3`

- Outcome / estimand：ln_yield and six SM source-depth outcomes；Corrected-SPEI rerun of baseline, stage, interaction and two-equation diagnostics。
- Exposure / mediator：Corrected window SPEI drought/wetness; HDD heat; SR interactions；Multiple SM measures。
- Controls / FE：Window precipitation; ET0; GDD; irrigation; aridity; soil controls；Grid FE plus year FE。
- Inference：Grid-clustered standard errors；bootstrap=Selected cluster bootstrap modules；reps=1000；seed=42。
- 代码入口：`repo://scripts/stata/v3_step1_baseline.do`。
- 解释边界：Historical corrected rerun; module-specific samples and estimands must remain separate。

### 结果呈现变化

产出为local V3 DTA、表格和handoff；明确与report-v3及data-v3-expanded分离；作为后续模块历史基础

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-analysis-v3-20260404` | `data-v3-analysis-ready` | `未冻结` | `method-analysis-v3` | `repo://scripts/stata/v3_step1_baseline.do` | `local://quality_reports/handoffs/2026-04-15_v3_task_handoff.md` | `未公开` | blocked_upstream_snapshot |

### 相对前版与证据边界

- 综合变化：Reran the systematic specifications after the SPEI correction and added period and bootstrap updates
- 证据限制：Distinct from report-v3 and data-v3-expanded

## `data-v2-main-post-spei-fix` — V2 main post-SPEI-fix snapshot

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-04；`missing_snapshot`；`missing_physical_snapshot` |
| 父版/取代关系 | parent=`data-v2`；supersedes=`data-v2-main-pre-spei-fix` |
| 当前用途 | Unavailable corrected historical input snapshot；truth role=`historical_missing_input` |
| 证据 | `missing-snapshot`；关联脱敏对话 1 个 |

### 数据变化

69038行、621列；相对pre-fix纠正SPEI endpoint并增加V3pre30等字段；沿用同一历史文件名；当前缺失

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `data-v2-main-corrected-missing` | data-build-snapshot | missing | 69038×621 | `local://data_build/data/processed/data_v2_main.dta` |

### 方法变化

数据管线修正SPEI窗口提取并扩展字段；不涉及回归估计；成为analysis-v3上游输入

### 结果呈现变化

无现存物理快照；由v3_step0头部和CHANGELOG重建；状态为missing-snapshot

### 相对前版与证据边界

- 综合变化：Corrected endpoint SPEI extraction and expanded the panel to 621 columns for the V3 systematic rerun
- 证据限制：The same historical path named data_v2_main.dta referred to a structurally different file

## `analysis-v3-modules` — V3 analysis module family

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-07；`historical`；`analysis_family` |
| 父版/取代关系 | parent=`analysis-v3`；supersedes=`none` |
| 当前用途 | Container for completed historical modules；truth role=`historical_module_family` |
| 证据 | `three-source-confirmed`；关联脱敏对话 1 个 |

### 数据变化

共同依赖analysis-v3-ready或data-v3-main；各模块另建analysis-ready DTA且main_sample定义不完全一致

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `analysis-v3prhd` | 2026-04-07 | `historical` | Defined HotDryPr as temperature at least 32 C with daily precipitation below 1 mm and estimated yield interactions across six windows |
| `analysis-v3prhdsm` | 2026-04-07 | `historical` | Changed outcomes to six soil-moisture source and depth measures under matching interaction structures |
| `analysis-v3decomp` | 2026-04-09 | `historical` | Built common-sample two-equation direct and SM-associated algebraic components |
| `analysis-v3sub` | 2026-04-09 | `historical` | Reran structures by irrigation group and maize region after removing W from selected specifications |
| `analysis-v3med-model8` | 2026-04-16 | `historical` | Estimated drought and heat mediator and yield equations across six SM measures and conditional SR levels |
| `analysis-v3proxy` | 2026-04-16 | `historical` | Compared drought proxies, HotDryPr inclusion, cut definitions, controls and six SM measures |
| `analysis-v3bpath` | 2026-04-20 | `historical` | Audited timing alignment, controls, wet-side terms, nonlinearity, proxy competition, source depth and heat consistency |
| `mechanism-v4smstate` | 2026-04-21 | `exploratory` | Compared raw SM with pooled-local and maize-zone dry or wet state variables |
| `mechanism-v5drymed` | 2026-04-22 | `exploratory` | Tested drydays, dryshare and drydeficit families under baseline-local, pooled-state and maize-zone thresholds |
| `mechanism-v6gleambl` | 2026-04-23 | `historical` | Added four-window GLEAM surface and root-zone dry or wet mediator families plus heat and hot-dry variants |

### 方法变化

容纳HotDryPr、六SM outcome、两方程分解、subsample、proxy和b-path审计；通常grid/year FE、grid cluster、seed 42

### 结果呈现变化

由handoff、计划、脚本和多份local报告组成；这是模块家族而非单一结果版

### 相对前版与证据边界

- 综合变化：Added precipitation hot-dry, multi-source SM outcomes, algebraic decomposition, sample boundaries and b-path audit
- 证据限制：A module family rather than one replacement version

## `analysis-v3prhd` — V3 precipitation hot-dry yield module

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-07；`historical`；`analysis_component` |
| 父版/取代关系 | parent=`analysis-v3-modules`；supersedes=`none` |
| 当前用途 | Historical precipitation hot-dry module；truth role=`historical_module` |
| 证据 | `three-source-confirmed`；关联脱敏对话 12 个 |

### 数据变化

输入data-v3-main；构造六窗口D、H和HotDryPr；HotDryPr定义为Tmax≥32C且日降水<1mm；生成模块sample

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `analysis-v3prhd-ready-dta` | analysis-panel | present | 69038×898 | `local://data/processed/v3prhd_analysis_ready.dta` |

本版本运行使用或定义的样本规则：

#### `module-v3prhd-main-sample` — V3 precipitation hot-dry main sample

- 谓词：`{"column":"main_sample","operator":"==","value":1}`。
- 规则向量：`main_sample=1`。
- 样本规模：rows=62034；grids=17903；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/v3prhd_step0_preamble.do`；代码 SHA-256=`075d914c396b971368dfb5108c732084fec567477415f432611bb58882db8011`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`sample-v3-main`。

### 方法变化

以ln_yield为outcome估计SR×D、SR×H、D×H、SR×D×H及SR×HotDryPr；grid/year FE、grid cluster、seed 42

#### `method-v3prhd`

- Outcome / estimand：ln_yield；SR-associated change in drought, heat, compound and precipitation hot-dry slopes across six windows。
- Exposure / mediator：D; HDD32; D by H; HotDryPr; SR interactions；none。
- Controls / FE：Window precipitation; ET0; GDD; irrigation; selected wetness terms；Grid FE plus year FE。
- Inference：Grid-clustered standard errors；bootstrap=none；reps=0；seed=42。
- 代码入口：`repo://scripts/stata/v3prhd_step1_regressions.do`。
- 解释边界：HotDryPr means Tmax at least 32 C and precipitation below 1 mm; it is not SM-defined hot-dry。

### 结果呈现变化

产出v3prhd表、图和beamer多轮排版；主报告入口由handoff指定；属于历史模块

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-analysis-v3prhd-20260407` | `data-v3-expanded-main-dta` | `module-v3prhd-main-sample` | `method-v3prhd` | `repo://scripts/stata/v3prhd_step1_regressions.do` | `local://output/tables/v3prhd_results_long.csv` | `未公开` | reconstructed_executable |

### 相对前版与证据边界

- 综合变化：Defined HotDryPr as temperature at least 32 C with daily precipitation below 1 mm and estimated yield interactions across six windows
- 证据限制：Precipitation-defined HotDryPr is not the older low-soil-moisture hot-dry variable

## `analysis-v3prhdsm` — V3 precipitation hot-dry soil-moisture module

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-07；`historical`；`analysis_component` |
| 父版/取代关系 | parent=`analysis-v3-modules`；supersedes=`none` |
| 当前用途 | Historical SM response module；truth role=`historical_module` |
| 证据 | `three-source-confirmed`；关联脱敏对话 11 个 |

### 数据变化

复用data-v3-main及相同降水HotDryPr；outcome改为GLEAM、SWSM和ERA5-Land六个SM source-depth变量；单独定义main_sample

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `analysis-v3prhdsm-ready-dta` | analysis-panel | present | 69038×898 | `local://data/processed/v3prhdsm_analysis_ready.dta` |

本版本运行使用或定义的样本规则：

#### `module-v3prhdsm-main-sample` — V3 multisource SM main sample

- 谓词：`{"column":"main_sample","operator":"==","value":1}`。
- 规则向量：`main_sample=1`。
- 样本规模：rows=62034；grids=17903；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/v3prhdsm_step0_preamble.do`；代码 SHA-256=`272be77da1b474aa5061acb6919cfb50597034b3d46455140776282faf8f0b61`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`module-v3prhd-main-sample`。

### 方法变化

对六个SM outcome运行匹配的交互结构；grid/year FE、grid cluster、seed 42；用于跨源方向核对

#### `method-v3prhdsm`

- Outcome / estimand：GLEAM, SWSM and ERA5-Land SM at surface or root depth；Cross-source SM response to the same drought, heat and HotDryPr interaction structures。
- Exposure / mediator：D; HDD32; HotDryPr; SR interactions；not_applicable。
- Controls / FE：Window precipitation; ET0; GDD; irrigation；Grid FE plus year FE。
- Inference：Grid-clustered standard errors；bootstrap=none；reps=0；seed=42。
- 代码入口：`repo://scripts/stata/v3prhdsm_step1_regressions.do`。
- 解释边界：Cross-source directional diagnostic; not evidence that one latent SM outcome is measured without error。

### 结果呈现变化

产出六源SM表、图和spec234报告；结果呈现与yield模块分开；历史SM响应模块

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-analysis-v3prhdsm-20260407` | `data-v3-expanded-main-dta` | `module-v3prhdsm-main-sample` | `method-v3prhdsm` | `repo://scripts/stata/v3prhdsm_step1_regressions.do` | `local://output/tables/v3prhdsm_results_long.csv` | `未公开` | reconstructed_executable |

### 相对前版与证据边界

- 综合变化：Changed outcomes to six soil-moisture source and depth measures under matching interaction structures
- 证据限制：The main_sample rule differs from other V3 modules

## `data-v3-expanded` — V3 expanded panel family

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-07；`current_data_base`；`logical_data_version` |
| 父版/取代关系 | parent=`data-v2`；supersedes=`none` |
| 当前用途 | Current shared climate and state data family；truth role=`current_shared_data` |
| 证据 | `three-source-confirmed`；关联脱敏对话 1 个 |

### 数据变化

在V2已有GLEAM root-zone SM阈值hot-dry基础上，保留并扩展GLEAM、SWSM、ERA5-Land多源多深度SM阈值hot-dry；另行新增以pr_lt1定义的precipitation hot-dry；同时增加capped GDD、dry/wet state和稳定Stata aliases；生成phenowindows/main/no-yield三视图

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `data-v3-expanded-run-manifest` | result-manifest | present | 未记录 | `repo://docs/results/data-v3-expanded/run-manifest.md` |
| `data-v3-expanded-public-report` | public-result | present | 未记录 | `repo://docs/results/data-v3-expanded/report.md` |

本版本运行使用或定义的样本规则：

#### `sample-data-v3-expanded-main` — V3 expanded yield-present panel

- 谓词：`{"column":"yield_tons_ha","operator":"is_not_missing"}`。
- 规则向量：`yield_present=1`。
- 样本规模：rows=69038；grids=22180；区域计数=`{}`。
- 规则代码：`repo://data_build/scripts/python/s10_export.py`；代码 SHA-256=`未记录`。
- 状态：`reference`；verified_at=`2026-07-14`；supersedes=`none`。

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `data-v3-main` | 2026-04-23 | `reference` | Exported the analysis main view including yield fields |
| `data-v3-no-yield` | 2026-04-23 | `reference` | Exported the yield-missing row partition while retaining the full schema |
| `data-v3-phenowindows` | 2026-04-23 | `reference` | Preserved the full phenology-window table before export filtering |
| `area-ggcp10-harvarea` | 2026-05-18 | `historical` | Replaced area-related variables with GGCP10 harvested area while retaining original maize_frac |

### 方法变化

run_all.py串联窗口计算、合并、质量检查和导出；panel键为grid_id/year；不改变回归estimand；构建脚本采用确定性处理

#### `method-data-v3-build`

- Outcome / estimand：V3 physical data views；Deterministic construction of climate-window and state-variable panel views。
- Exposure / mediator：Phenology windows; temperature; precipitation; SM; ET0; VPD; SPEI; compound metrics；not_applicable。
- Controls / FE：Source QA rules and grid_id-year key checks；not_applicable。
- Inference：Schema, key, range and monotonicity assertions；bootstrap=none；reps=0；seed=none。
- 代码入口：`repo://data_build/scripts/python/run_all.py`。
- 解释边界：Data transformation provenance only; no empirical claim。

### 结果呈现变化

公开V3 expanded说明和运行manifest，列出三个物理视图的SHA、行列数和schema；物理CSV/Parquet/DTA保持local；两类hot-dry分开呈现

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-data-v3-expanded-20260423` | `data-v1-locked-panel` | `sample-data-v3-expanded-main` | `method-data-v3-build` | `repo://data_build/scripts/python/run_all.py` | `repo://docs/results/data-v3-expanded/run-manifest.md` | `repo://docs/results/data-v3-expanded/report.md` | historical_static |

### 相对前版与证据边界

- 综合变化：Added capped GDD; retained and expanded multi-source soil-moisture-threshold hot-dry; separately added precipitation-threshold hot-dry; stabilized Stata aliases
- 证据限制：Physical views remain local and untracked

## `analysis-v3decomp` — V3 FE decomposition module

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-09；`historical`；`analysis_component` |
| 父版/取代关系 | parent=`analysis-v3-modules`；supersedes=`none` |
| 当前用途 | Historical decomposition module；truth role=`historical_module` |
| 证据 | `three-source-confirmed`；关联脱敏对话 6 个 |

### 数据变化

输入v3_analysis_ready；以gleam_sms_mean为主mediator；创建严格common sample及SM×D、SM×H变量

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `analysis-v3decomp-ready-dta` | analysis-panel | present | 69038×775 | `local://data/processed/v3decomp_analysis_ready.dta` |

本版本运行使用或定义的样本规则：

#### `module-v3decomp-common-sample` — V3 decomposition common sample

- 谓词：`{"column":"v3decomp_common_sample","operator":"==","value":1}`。
- 规则向量：`v3decomp_common_sample=1`。
- 样本规模：rows=62018；grids=17898；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/v3decomp_step0_profiles.do`；代码 SHA-256=`a4c0ddfbf3d67e90d03553d14bb8f7598608ed7f79041d850f4249cf714eea3e`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`sample-v3-main`。

### 方法变化

两方程FE代数分解direct和SM-associated components；grid/year FE、grid cluster、seed 42；不是因果中介

#### `method-v3decomp`

- Outcome / estimand：ln_yield with paired SM equation；Algebraic direct and SM-associated components on a strict common sample。
- Exposure / mediator：Drought; heat; wetness; SR by hazard interactions；gleam_sms_mean。
- Controls / FE：Precipitation; ET0; GDD; irrigation; aridity；Grid FE plus year FE。
- Inference：Grid-clustered standard errors；bootstrap=Cluster bootstrap in decomposition step；reps=100 dry-run;1000 final；seed=42。
- 代码入口：`repo://scripts/stata/v3decomp_step1_equations.do`。
- 解释边界：Components are associational algebra and not identified natural direct or indirect effects。

### 结果呈现变化

产出profile constants、方程表、bootstrap表和beamer；后续统一采用代数组件措辞

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-analysis-v3decomp-20260409` | `analysis-v3decomp-ready-dta` | `module-v3decomp-common-sample` | `method-v3decomp` | `repo://scripts/stata/v3decomp_step1_equations.do` | `local://output/tables/v3decomp_equation_results.csv` | `未公开` | reconstructed_executable |

### 相对前版与证据边界

- 综合变化：Built common-sample two-equation direct and SM-associated algebraic components
- 证据限制：Components are not identified causal mediation effects

## `analysis-v3sub` — V3 sample-boundary module

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-09；`historical`；`analysis_component` |
| 父版/取代关系 | parent=`analysis-v3-modules`；supersedes=`none` |
| 当前用途 | Historical sample-boundary module；truth role=`historical_module` |
| 证据 | `three-source-confirmed`；关联脱敏对话 9 个 |

### 数据变化

输入v3_analysis_ready；新增NE/HHH/SW/NW/SH/Other maize_zone和irr_group；按边界形成子样本

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `analysis-v3sub-ready-dta` | analysis-panel | present | 69038×774 | `local://data/processed/v3sub_analysis_ready.dta` |

本版本运行使用或定义的样本规则：

#### `module-v3sub-boundary-samples` — V3 boundary and subsample flag registry

- 谓词：`{"registry":"script-defined maize-zone irrigation and support flags"}`。
- 规则向量：`multiple_subsample_flags`。
- 样本规模：rows=未记录；grids=未记录；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/v3sub_step0_subsamples.do`；代码 SHA-256=`fcbd2973312db00d9935cc3b65ac2fcca11b5d21dd0cc534309c88ebe4bf6a5d`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`sample-v3-main`。

### 方法变化

按灌溉与玉米区重跑三结构和窗口模型；部分规格移除W；grid/year FE、grid cluster、seed 42

#### `method-v3sub`

- Outcome / estimand：ln_yield and SM response outcomes；Sample-boundary heterogeneity by irrigation group and maize region。
- Exposure / mediator：Drought; heat; precipitation hot-dry; SR interactions；SM in response specifications。
- Controls / FE：Window climate controls; selected specifications omit wetness；Grid FE plus year FE within subgroup。
- Inference：Grid-clustered standard errors；bootstrap=none；reps=0；seed=42。
- 代码入口：`repo://scripts/stata/v3sub_run_all.do`。
- 解释边界：Subgroup patterns do not redefine the full-sample estimand or imply causal targeting。

### 结果呈现变化

产出subsample表和综合beamer；用于边界诊断；不把子样本结果定义为新主样本

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-analysis-v3sub-20260409` | `analysis-v3sub-ready-dta` | `module-v3sub-boundary-samples` | `method-v3sub` | `repo://scripts/stata/v3sub_run_all.do` | `local://output/tables/v3sub_results_long.csv` | `未公开` | reconstructed_executable |

### 相对前版与证据边界

- 综合变化：Reran structures by irrigation group and maize region after removing W from selected specifications
- 证据限制：Subsample-specific results do not redefine the global main_sample

## `analysis-v3med-model8` — V3 moderated two-equation Model 8

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-16；`historical`；`analysis_component` |
| 父版/取代关系 | parent=`analysis-v3-modules`；supersedes=`none` |
| 当前用途 | Historical Model 8 module；truth role=`historical_module` |
| 证据 | `three-source-confirmed`；关联脱敏对话 10 个 |

### 数据变化

输入v3med common sample；覆盖六个SM source-depth mediator及drought/heat模块；样本与其他V3模块不同

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `analysis-v3med-ready-dta` | analysis-panel | present | 69038×777 | `local://data/processed/v3med_analysis_ready.dta` |

本版本运行使用或定义的样本规则：

#### `module-v3med-common-sample` — V3 Model-8 six-source common sample

- 谓词：`{"column":"v3med_common","operator":"==","value":1}`。
- 规则向量：`v3med_common=1`。
- 样本规模：rows=61887；grids=17856；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/v3med_step0_preamble.do`；代码 SHA-256=`ed4e785416c5350271690d53bba41b87d2e694bd45d688f9496a43f1bc97d0f6`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`sample-v3-main`。

### 方法变化

Model 8包含mediator方程SM~hazard+SR+SR×hazard和yield方程lnY~hazard+SR+SR×hazard+SM；grid/year FE、grid cluster、seed 42

#### `method-v3med-model8`

- Outcome / estimand：SM mediator equation and ln_yield outcome equation；Conditional two-equation hazard components at SR P25, P50 and P75。
- Exposure / mediator：Drought or heat; SR; SR by hazard；Six SM source-depth measures。
- Controls / FE：Reduced or full climate, irrigation and aridity controls；Grid FE plus year FE; lower-level FE only as diagnostics。
- Inference：Clustered standard errors at the FE spatial unit；bootstrap=Cluster bootstrap in dedicated steps；reps=500；seed=42。
- 代码入口：`repo://scripts/stata/v3med_step2_drought_model8.do`。
- 解释边界：Historical moderated-mediation label is retained only as a code name; no causal mediation identification。

### 结果呈现变化

产出coefficients、conditional effects、bootstrap和heterogeneity表；历史中介叙事已改为非因果两方程组件

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-analysis-v3med-model8-20260416` | `analysis-v3med-ready-dta` | `module-v3med-common-sample` | `method-v3med-model8` | `repo://scripts/stata/v3med_step2_drought_model8.do` | `local://output/tables/v3med_drought_model8_coefficients.csv` | `未公开` | reconstructed_executable |

### 相对前版与证据边界

- 综合变化：Estimated drought and heat mediator and yield equations across six SM measures and conditional SR levels
- 证据限制：The historical mediation wording is superseded by algebraic and associational language

## `analysis-v3proxy` — V3 drought-proxy competition module

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-16；`historical`；`analysis_component` |
| 父版/取代关系 | parent=`analysis-v3-modules`；supersedes=`none` |
| 当前用途 | Historical proxy audit；truth role=`historical_module` |
| 证据 | `three-source-confirmed`；关联脱敏对话 7 个 |

### 数据变化

输入v3proxy common sample；加入两类drought proxy、三种cut、HotDryPr开关及六SM来源

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `analysis-v3proxy-ready-dta` | analysis-panel | present | 69038×935 | `local://data/processed/v3proxy_analysis_ready.dta` |

本版本运行使用或定义的样本规则：

#### `module-v3proxy-common-sample` — V3 SM proxy common support

- 谓词：`{"column":"v3proxy_common","operator":"==","value":1}`。
- 规则向量：`v3proxy_common=1`。
- 样本规模：rows=61901；grids=17861；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/v3proxy_step0_preamble.do`；代码 SHA-256=`50dc1339e147d19abce87fee702a75e4b9a224cffd7abebf9dfe61a2d5261abd`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`module-v3prhdsm-main-sample`。

### 方法变化

运行2 proxy×2 HDP×3 cuts×2 controls×6 SM的factorial FE比较并做competition checks；grid/year FE、grid cluster、seed 42

#### `method-v3proxy`

- Outcome / estimand：ln_yield and SM equations；Sensitivity of drought and SM terms to proxy, cut, HotDryPr and control competition。
- Exposure / mediator：Two drought proxies; three cuts; HotDryPr on or off; heat；Six SM source-depth measures。
- Controls / FE：Reduced or full window-specific controls；Grid FE plus year FE。
- Inference：Grid-clustered standard errors；bootstrap=none；reps=0；seed=42。
- 代码入口：`repo://scripts/stata/v3proxy_step1_modelsets.do`。
- 解释边界：Factorial diagnostic intended to expose proxy sensitivity rather than select significance。

### 结果呈现变化

产出long-format系数表和审计报告；用于说明proxy选择敏感性；非主结果

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-analysis-v3proxy-20260416` | `analysis-v3proxy-ready-dta` | `module-v3proxy-common-sample` | `method-v3proxy` | `repo://scripts/stata/v3proxy_step1_modelsets.do` | `local://output/tables/v3proxy_results_long.csv` | `未公开` | reconstructed_executable |

### 相对前版与证据边界

- 综合变化：Compared drought proxies, HotDryPr inclusion, cut definitions, controls and six SM measures
- 证据限制：A diagnostic module and not a new data version

## `analysis-v3bpath` — V3 b-path audit module

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-20；`historical`；`analysis_component` |
| 父版/取代关系 | parent=`analysis-v3-modules`；supersedes=`none` |
| 当前用途 | Historical b-path audit；truth role=`historical_module` |
| 证据 | `three-source-confirmed`；关联脱敏对话 9 个 |

### 数据变化

输入v3bpath unified stage sample；对齐各窗口的六个SM变量并保留wet control、heat和D×SR

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `analysis-v3bpath-ready-dta` | analysis-panel | present | 69038×954 | `local://data/processed/v3bpath_analysis_ready.dta` |

本版本运行使用或定义的样本规则：

#### `sample-v3bpath-stage6` — V3 b-path six-source stage common support

- 谓词：`{"column":"bpath_stage6_sample","operator":"==","value":1}`。
- 规则向量：`bpath_stage6_sample=1`。
- 样本规模：rows=61901；grids=17861；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/v3bpath_step0_preamble.do`；代码 SHA-256=`6002228d8feeaf2c239845e4dd5edfeb974e2d1d8fac4596a890a2652fdfe75d`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`sample-v3bpath-main`。

基于本版本数据形成、由下游节点使用的派生规则：

#### `sample-v3bpath-main` — V3 b-path inherited main_sample

- 谓词：`{"column":"main_sample","operator":"==","value":1}`。
- 规则向量：`main_sample=1`。
- 样本规模：rows=62034；grids=17903；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/v3bpath_step0_preamble.do`；代码 SHA-256=`6002228d8feeaf2c239845e4dd5edfeb974e2d1d8fac4596a890a2652fdfe75d`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`sample-v3-main`。

#### `sample-v3bpath-full6` — V3 b-path six-source full-season common support

- 谓词：`{"column":"bpath_full6_sample","operator":"==","value":1}`。
- 规则向量：`bpath_full6_sample=1`。
- 样本规模：rows=61887；grids=17856；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/v3bpath_step0_preamble.do`；代码 SHA-256=`6002228d8feeaf2c239845e4dd5edfeb974e2d1d8fac4596a890a2652fdfe75d`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`sample-v3bpath-main`。

### 方法变化

依次审计timing、control ladder、wet control、nonlinear、proxy competition、source depth和heat consistency；grid/year FE、grid cluster、seed 42

#### `method-v3bpath`

- Outcome / estimand：ln_yield；Stability of the SM coefficient and SR by drought coefficient under timing and specification audits。
- Exposure / mediator：Window drought; heat; wetness; SR by drought；Six aligned SM source-depth measures。
- Controls / FE：Control ladders, nonlinear terms and proxy competition sets；Grid FE plus year FE。
- Inference：Grid-clustered standard errors；bootstrap=none；reps=0；seed=42。
- 代码入口：`repo://scripts/stata/v3bpath_run_all.do`。
- 解释边界：An audit of conditional coefficients; not an identified causal b-path。

### 结果呈现变化

产出八类审计CSV和2026-04-20汇总；重点呈现不一致和限制；不支持因果b-path

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-analysis-v3bpath-20260420` | `analysis-v3bpath-ready-dta` | `sample-v3bpath-stage6` | `method-v3bpath` | `repo://scripts/stata/v3bpath_run_all.do` | `local://quality_reports/2026-04-20_v3bpath_audit_results.md` | `未公开` | reconstructed_executable |

### 相对前版与证据边界

- 综合变化：Audited timing alignment, controls, wet-side terms, nonlinearity, proxy competition, source depth and heat consistency
- 证据限制：The audit constrains claims rather than establishing a causal b-path

## `mechanism-v4smstate` — V4 SM-state experiment

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-21；`exploratory`；`mechanism_experiment` |
| 父版/取代关系 | parent=`analysis-v3-modules`；supersedes=`none` |
| 当前用途 | Exploratory state-variable family；truth role=`exploratory_mechanism` |
| 证据 | `three-source-confirmed`；关联脱敏对话 14 个 |

### 数据变化

基于V3数据构建raw SM、pooled-local及maize-zone dry/wet state sidecar；六SM源和多个窗口使用common sample

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `mechanism-sm-state-wide-april-missing` | data-sidecar | missing | 未记录 | `local://temp/2026-04-21_sm_state_audit/sm_state_panel_wide.dta` |
| `mechanism-sm-state-wide-current` | data-sidecar | present | 122533×254 | `local://temp/2026-04-21_sm_state_audit/sm_state_panel_wide.dta` |
| `mechanism-sm-state-analysis-ready-missing` | analysis-panel | missing | 未记录 | `local://temp/2026-04-21_sm_state_audit/sm_state_analysis_ready.dta` |

本版本运行使用或定义的样本规则：

#### `module-v4smstate-common-sample` — V4 SM-state common-sample registry

- 谓词：`{"registry":"state_*_6_sample flags"}`。
- 规则向量：`multiple_state_common_flags`。
- 样本规模：rows=未记录；grids=未记录；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/v4smstate_step0_preamble.do`；代码 SHA-256=`aa1aded2e9159679848173eb92abccb299449c09d7424f49af0864826ef9f646`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`none`。

### 方法变化

比较raw-vs-state outcome方程及state mediator方程；grid/year FE、grid cluster、seed 42；相对V3 b-path改用状态阈值变量

#### `method-v4smstate`

- Outcome / estimand：ln_yield plus state-variable equations；Comparison of raw SM and threshold-state representations。
- Exposure / mediator：Drought; heat; wetness; SR by drought；Raw SM; pooled-local dry/wet states; maize-zone dry/wet states。
- Controls / FE：Irrigation; GDD; window controls；Grid FE plus year FE。
- Inference：Grid-clustered standard errors；bootstrap=none；reps=0；seed=42。
- 代码入口：`repo://scripts/stata/v4smstate_run_all.do`。
- 解释边界：Exploratory representation audit; state thresholds are not treatments。

### 结果呈现变化

产出state model CSV、分布图和audit计划；保持exploratory；不是report-v4

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-mechanism-v4smstate-20260421` | `data-v3-analysis-ready` | `module-v4smstate-common-sample` | `method-v4smstate` | `repo://scripts/stata/v4smstate_run_all.do` | `local://temp/2026-04-21_sm_state_audit/sm_state_model_all.csv` | `未公开` | reconstructed_executable |

### 相对前版与证据边界

- 综合变化：Compared raw SM with pooled-local and maize-zone dry or wet state variables
- 证据限制：Not report-v4 and not a strict successor node

## `mechanism-v5drymed` — V5 drought-only dry-mediator experiment

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-22；`exploratory`；`mechanism_experiment` |
| 父版/取代关系 | parent=`analysis-v3-modules`；supersedes=`none` |
| 当前用途 | Exploratory drought-only family；truth role=`exploratory_mechanism` |
| 证据 | `three-source-confirmed`；关联脱敏对话 7 个 |

### 数据变化

合并v3_analysis_ready、v3sub、SM-state sidecar和data-v3-main；构造drydays、dryshare、drydeficit及多阈值sample tags

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `mechanism-v5drymed-ready-dta` | analysis-panel | present | 69038×919 | `local://data/processed/v5drymed_analysis_ready.dta` |

本版本运行使用或定义的样本规则：

#### `module-v5drymed-sample-tags` — V5 drought-mediator sample flag registry

- 谓词：`{"registry":"script-defined dry-mediator sample flags"}`。
- 规则向量：`multiple_v5_sample_flags`。
- 样本规模：rows=未记录；grids=未记录；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/v5drymed_step0_preamble.do`；代码 SHA-256=`f96dac5de84076bfa55928a294ffbbc73a13a3ea465a021ca5fd21be9b258d4b`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`sample-v3-main`。

### 方法变化

drought-only Model 8；mediator和yield两方程；baseline-local、pooled-state、maize-zone阈值；grid/year FE、grid cluster、seed 42

#### `method-v5drymed`

- Outcome / estimand：Dry mediator equation and ln_yield outcome equation；Drought-only conditional two-equation components across dry metric families。
- Exposure / mediator：Drought; wetness; heat; SR by drought；drydays; dryshare; drydeficit。
- Controls / FE：Precipitation; ET0; GDD; irrigation; aridity；Grid FE plus year FE。
- Inference：Grid-clustered standard errors；bootstrap=Cluster bootstrap in dedicated step；reps=500 default；seed=42。
- 代码入口：`repo://scripts/stata/v5drymed_run_all.do`。
- 解释边界：Exploratory drought-only family; do not interpret coefficients as causal mediation effects。

### 结果呈现变化

产出coefficients、conditional effects、bootstrap和heterogeneity摘要；探索范围后被收窄；不是report-v5

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-mechanism-v5drymed-20260422` | `mechanism-v5drymed-ready-dta` | `module-v5drymed-sample-tags` | `method-v5drymed` | `repo://scripts/stata/v5drymed_run_all.do` | `local://output/tables/v5drymed_model8_coefficients.csv` | `未公开` | reconstructed_executable |

### 相对前版与证据边界

- 综合变化：Tested drydays, dryshare and drydeficit families under baseline-local, pooled-state and maize-zone thresholds
- 证据限制：Not report-v5 and not a strict successor to mechanism-v4smstate

## `data-v3-main` — V3 expanded main view

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-23；`reference`；`physical_data_snapshot` |
| 父版/取代关系 | parent=`data-v3-expanded`；supersedes=`none` |
| 当前用途 | Primary V3 module input；truth role=`current_data_component` |
| 证据 | `three-source-confirmed`；关联脱敏对话 13 个 |

### 数据变化

从phenowindows导出保留yield字段的主视图；V1-family结果变量明确为yield_tons_ha=maize_prod/maize_area_km2*10；用于V3模块

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `data-v3-expanded-main` | data-base | present | 69038×1679 | `local://data_build/data/processed/data_v3_main.parquet` |
| `data-v3-expanded-main-csv` | data-format-variant | present | 69038×1679 | `local://data_build/data/processed/data_v3_main.csv` |
| `data-v3-expanded-main-dta` | data-format-variant | present | 69038×1679 | `local://data_build/data/processed/data_v3_main.dta` |

基于本版本数据形成、由下游节点使用的派生规则：

#### `sample-data-v3-expanded-main` — V3 expanded yield-present panel

- 谓词：`{"column":"yield_tons_ha","operator":"is_not_missing"}`。
- 规则向量：`yield_present=1`。
- 样本规模：rows=69038；grids=22180；区域计数=`{}`。
- 规则代码：`repo://data_build/scripts/python/s10_export.py`；代码 SHA-256=`未记录`。
- 状态：`reference`；verified_at=`2026-07-14`；supersedes=`none`。

#### `sample-regional-threshold-pre-edd` — Five-zone pre-EDD complete-case support sample

- 谓词：`{"all":[{"column":"zone","operator":"in","values":["NE","HHH","NW","SH","SW"]},{"columns":["ln_yield","ca","gdd_10_29","pr_sum","v3_doy","he_doy","ma_doy","gleam_smrz_mean"],"operator":"all_not_missing"}]}`。
- 规则向量：`named_zones=1|ln_yield=1|ca=1|gdd_10_29=1|pr_sum=1|v3_doy=1|he_doy=1|ma_doy=1|gleam_smrz_mean=1`。
- 样本规模：rows=66396；grids=21337；区域计数=`{"HHH":{"rows":13165,"grids":3844},"NE":{"rows":25041,"grids":7365},"NW":{"rows":5540,"grids":2228},"SH":{"rows":4556,"grids":1692},"SW":{"rows":18094,"grids":6208}}`。
- 规则代码：`repo://scripts/python/audit_regional_threshold_coverage.py`；代码 SHA-256=`f8c84ce75aa0e29a1f59bdebb7f74cec5914de05ada6d39f4521d8462448a481`。
- 状态：`historical`；verified_at=`2026-07-15`；supersedes=`none`。

#### `sample-compound-event-smoke-v2` — Compound-event deterministic small-smoke interface sample

- 谓词：`{"all":[{"column":"zone","operator":"in","values":["NE","HHH","NW","SH","SW"]},{"rule":"first two eligible grid-year rows within each zone-year after deterministic sort","active":1}]}`。
- 规则向量：`named_zones=1|first_two_per_zone_year=1|interface_only=1`。
- 样本规模：rows=40；grids=20；区域计数=`{"HHH":{"rows":8,"grids":3},"NE":{"rows":8,"grids":3},"NW":{"rows":8,"grids":5},"SH":{"rows":8,"grids":6},"SW":{"rows":8,"grids":3}}`。
- 规则代码：`repo://scripts/python/run_hotdry_event_stage1.py`；代码 SHA-256=`e8adb78193a1358901048155e45a336e6cecdbe7ba33df0db68a2d3786b00b93`。
- 状态：`historical`；verified_at=`2026-07-15`；supersedes=`none`。

#### `sample-regional-threshold-override-model-v2` — Regional-threshold override final yield-model sample

- 谓词：`{"all":[{"column":"zone","operator":"in","values":["NE","HHH","NW","SH","SW"]},{"column":"external_threshold_valid","operator":"==","value":1},{"columns":["ln_yield","ca","gdd_10_29","pr_sum","province","year","daily_tmax_window"],"operator":"all_not_missing"}]}`。
- 规则向量：`named_zones=1|external_threshold_valid=1|daily_tmax_window_valid=1|yield_ca_controls_fe_complete=1`。
- 样本规模：rows=54890；grids=17450；区域计数=`{"HHH":{"rows":12922,"grids":3775},"NE":{"rows":23719,"grids":6966},"NW":{"rows":4681,"grids":1849},"SH":{"rows":4501,"grids":1668},"SW":{"rows":9067,"grids":3192}}`。
- 规则代码：`repo://scripts/python/run_regional_threshold_daily_override.py`；代码 SHA-256=`10b44b0242dc6397d1bcff37ef5a55396d250f0dc845fcab26c9e656db0e01fb`。
- 状态：`reference`；verified_at=`2026-07-15`；supersedes=`none`。

#### `sample-compound-event-override-model-v1` — Compound-event override complete-case yield-model sample

- 谓词：`{"all":[{"column":"zone","operator":"in","values":["NE","HHH","NW","SH","SW"]},{"columns":["ln_yield","ca","total_duration","mean_intensity","gdd_10_29","pr_sum","province","year"],"operator":"all_not_missing"}]}`。
- 规则向量：`named_zones=1|event_metrics_zero_when_no_event=1|yield_ca_controls_fe_complete=1`。
- 样本规模：rows=61918；grids=19749；区域计数=`{"HHH":{"rows":13165,"grids":3844},"NE":{"rows":24876,"grids":7314},"NW":{"rows":5534,"grids":2226},"SH":{"rows":4556,"grids":1692},"SW":{"rows":13787,"grids":4673}}`。
- 规则代码：`repo://scripts/python/run_hotdry_event_override_models.py`；代码 SHA-256=`fdb05bb78aeab0ccff17e6534ae0166b3129171646bbf92aedae3a98f05eaeae`。
- 状态：`current`；verified_at=`2026-07-15`；supersedes=`none`。

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `regional-threshold-sr-v1` | 2026-07-14 | `reference` | Audited the official continuous maize heat-damage threshold before any yield model and stopped at the frozen five-zone coverage gate |
| `compound-event-intensity-duration-v1` | 2026-07-15 | `reference` | Designed the hot-dry event intensity-duration and soil-moisture timing interface, then stopped after the second small-smoke review retained a reproducibility Major |

### 方法变化

s10_export执行字段筛选、别名和序列化；不涉及estimand、FE、cluster或bootstrap

### 结果呈现变化

载体为local CSV/Parquet/DTA；Git仅记录构建脚本和字典；当前模块级数据组件

### 相对前版与证据边界

- 综合变化：Exported the analysis main view including yield fields
- 证据限制：V1-family yield_tons_ha uses maize_prod/maize_area_km2*10 and must not be conflated with the GGCP10 definition that changes the area denominator

## `data-v3-no-yield` — V3 expanded no-yield view

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-23；`reference`；`physical_data_snapshot` |
| 父版/取代关系 | parent=`data-v3-expanded`；supersedes=`none` |
| 当前用途 | Yield-missing row partition for non-outcome data reuse；truth role=`current_data_component` |
| 证据 | `three-source-confirmed`；关联脱敏对话 0 个 |

### 数据变化

从phenowindows按yield_tons_ha缺失筛出53495行；保留全部1679列，yield字段仍存在但在该视图中全缺失；与main的69038行构成按yield是否缺失划分的行分区

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `data-v3-expanded-noyield` | data-base | present | 53495×1679 | `local://data_build/data/processed/data_v3_noyield.parquet` |

### 方法变化

s10_export分别以yield_tons_ha.notna()和isna()确定main与no-yield行分区并序列化；不删除字段且不运行产量模型

### 结果呈现变化

载体为local Parquet；不作为yield结果证据；仅登记为yield缺失行的数据共享组件

### 相对前版与证据边界

- 综合变化：Exported the yield-missing row partition while retaining the full schema
- 证据限制：Not an estimation input for yield models; no-yield means yield-missing rows, not removed columns

## `data-v3-phenowindows` — V3 phenology-window full view

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-23；`reference`；`physical_data_snapshot` |
| 父版/取代关系 | parent=`data-v3-expanded`；supersedes=`none` |
| 当前用途 | Local source for the V3 main and no-yield exports；truth role=`current_data_component` |
| 证据 | `three-source-confirmed`；关联脱敏对话 3 个 |

### 数据变化

保存完整物候窗口宽表；相对父级逻辑版本是全字段物理序列化；local Parquet、CSV、DTA同源

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `data-v3-expanded-phenowindows` | data-base | present | 122533×1679 | `local://data_build/data/processed/data_v3_phenowindows.parquet` |
| `data-v3-expanded-phenowindows-csv` | data-format-variant | present | 122533×1679 | `local://data_build/data/processed/data_v3_phenowindows.csv` |
| `data-v3-expanded-phenowindows-dta` | data-format-variant | present | 122533×1679 | `local://data_build/data/processed/data_v3_phenowindows.dta` |

### 方法变化

由s08_merge_panel合并各窗口sidecar；按grid_id/year校验；不涉及估计方法

### 结果呈现变化

载体为local大文件及构建脚本；作为data-v3-main和no-yield导出的上游组件；非独立逻辑版本

### 相对前版与证据边界

- 综合变化：Preserved the full phenology-window table before export filtering
- 证据限制：Not an independent logical data version

## `mechanism-v6gleambl` — V6 GLEAM baseline-local experiment

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-04-23；`historical`；`mechanism_experiment` |
| 父版/取代关系 | parent=`analysis-v3-modules`；supersedes=`none` |
| 当前用途 | Historical precursor to the GGCP10 suite；truth role=`historical_mechanism_precursor` |
| 证据 | `three-source-confirmed`；关联脱敏对话 10 个 |

### 数据变化

在V3与state sidecar上使用GLEAM surface/root-zone、四窗口、dry/wet配对mediator；相对v5减少到GLEAM重点来源

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `mechanism-v6-nowet-nop30-ready-missing` | analysis-panel | missing | 未记录 | `local://temp/2026-04-23_newSMsplit/v6gleambl_nowet_nop30_analysis_ready.dta` |
| `mechanism-v6gleambl-ready-dta` | analysis-panel | present | 69038×1171 | `local://temp/2026-04-23_newSMsplit/v6gleambl_analysis_ready.dta` |

本版本运行使用或定义的样本规则：

#### `module-v6gleambl-sample-tags` — V6 GLEAM baseline-local sample flag registry

- 谓词：`{"registry":"window source threshold-specific sample flags"}`。
- 规则向量：`multiple_v6_sample_flags`。
- 样本规模：rows=未记录；grids=未记录；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/v6gleambl_step0_preamble.do`；代码 SHA-256=`e08d6f7e54cda2b08db25adc354835dfa1190f8ccf5747597df0470d74479ade`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`sample-v3-main`。

### 方法变化

四窗口Model 8并扩展heat/hot-dry control variants；grid/year FE、grid cluster、seed 42；baseline-local阈值为主体

#### `method-v6gleambl`

- Outcome / estimand：GLEAM dry-mediator equation and ln_yield outcome equation；Four-window baseline-local two-equation components with paired wet controls。
- Exposure / mediator：Drought plus heat or precipitation hot-dry variants; SR interactions；GLEAM surface and root-zone dry or wet metrics。
- Controls / FE：Window wetness; precipitation; ET0; GDD; irrigation; aridity；Grid FE plus year FE。
- Inference：Grid-clustered standard errors；bootstrap=Cluster bootstrap in dedicated step；reps=500 default；seed=42。
- 代码入口：`repo://scripts/stata/v6gleambl_run_all.do`。
- 解释边界：Historical precursor; heat and hot-dry variants must not be pooled as one estimand。

### 结果呈现变化

产出local baseline、bootstrap、full-family表和图；成为GGCP10 baseline suite前身；不是report-v6.1

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-mechanism-v6gleambl-20260423` | `data-v3-analysis-ready\|data-v3-expanded-main-dta` | `module-v6gleambl-sample-tags` | `method-v6gleambl` | `repo://scripts/stata/v6gleambl_run_all.do` | `local://temp/2026-04-23_newSMsplit/v6gleambl_baseline_coefficients.csv` | `未公开` | reconstructed_executable |

### 相对前版与证据边界

- 综合变化：Added four-window GLEAM surface and root-zone dry or wet mediator families plus heat and hot-dry variants
- 证据限制：Not report-v6.1 and not a strict successor chain

## `analysis-ggcp10-baseline-suite` — GGCP10 aggregated baseline suite

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-05-18；`historical`；`analysis_component` |
| 父版/取代关系 | parent=`area-ggcp10-aggregated`；supersedes=`none` |
| 当前用途 | Input foundation for later GGCP10 scale work；truth role=`historical_ggcp10_baseline` |
| 证据 | `three-source-confirmed`；关联脱敏对话 12 个 |

### 数据变化

输入GGCP10 aggregated base和data-v3-main HotDryPr；使用raw SM、dry-state、wet-state mediator；按各模型形成sample tag

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `ggcp10-baseline-suite` | analysis-panel | present | 69038×1182 | `local://temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_baseline_suite_analysis_ready.dta` |

本版本运行使用或定义的样本规则：

#### `ggcp10-suite-model-specific-samples` — GGCP10 suite model-specific complete-case samples

- 谓词：`{"registry":"Stata model e(sample) by metric window and specification"}`。
- 规则向量：`model_specific_complete_cases`。
- 样本规模：rows=未记录；grids=未记录；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/ggcp10_baseline_suite_run_all.do`；代码 SHA-256=`7b31ebb4695bfdda5d2c016d3ae0d6fda1cf878a6e61d57b6cb8ca48845ea631`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`sample-ggcp10-baseline-main`。

基于本版本数据形成、由下游节点使用的派生规则：

#### `sample-ggcp10-baseline-all` — GGCP10 aggregated baseline full panel

- 谓词：`{"constant":true}`。
- 规则向量：`all_rows`。
- 样本规模：rows=69038；grids=22180；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/ggcp10_baseline_suite_run_all.do`；代码 SHA-256=`7b31ebb4695bfdda5d2c016d3ae0d6fda1cf878a6e61d57b6cb8ca48845ea631`。
- 状态：`reference`；verified_at=`2026-07-14`；supersedes=`none`。

#### `sample-ggcp10-baseline-main` — GGCP10 aggregated inherited main sample

- 谓词：`{"column":"main_sample","operator":"==","value":1}`。
- 规则向量：`main_sample=1`。
- 样本规模：rows=62018；grids=17898；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/v3_step0_preamble.do`；代码 SHA-256=`d4a24cf9f7662da08b746924eb46ae17e3928b76ddfba817193affe78d37785b`。
- 状态：`reference`；verified_at=`2026-07-14`；supersedes=`sample-v3-main`。

#### `ggcp10-extension-branch-samples` — GGCP10 mediation-extension branch samples

- 谓词：`{"registry":"mean wet_mirror and dry_top3 branch-specific flags"}`。
- 规则向量：`branch_specific_complete_cases`。
- 样本规模：rows=未记录；grids=未记录；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/ggcp10_mean_ext_run_all.do`；代码 SHA-256=`358a1a4c6131ccbf5501d5d404bf0745908647f7f4931835885ac42191672bd3`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`sample-ggcp10-baseline-main`。

#### `sample-g057` — G057 frozen scale

- 谓词：`{"all":[{"column":"ggcp10_maize_frac","operator":">=","value":0.05},{"rule":"main_sample","active":0},{"rule":"zone_core","active":0},{"rule":"yield_domain","active":1},{"rule":"yield_jump","active":1},{"rule":"sm_sd","active":1},{"rule":"sm_coverage","active":0},{"rule":"sr_within","active":0},{"rule":"years_ge3","active":0},{"rule":"stable_province","active":0}]}`。
- 规则向量：`crop_mask=ggcp10>=0.05|main_sample=0|zone_core=0|yield_domain=1|yield_jump=1|sm_sd=1|sm_coverage=0|sr_within=0|years_ge3=0|stable_province=0`。
- 样本规模：rows=50771；grids=15729；区域计数=`{"HHH":{"rows":12504,"grids":3615},"NE":{"rows":21116,"grids":6031},"NW":{"rows":3747,"grids":1524},"Other":{"rows":1818,"grids":566},"SH":{"rows":941,"grids":322},"SW":{"rows":10645,"grids":3671}}`。
- 规则代码：`repo://scripts/python/expanded_scale_story_search.py`；代码 SHA-256=`cabb1a038b1efb3b6ce88fd4f81c9eb3e086372554f2d43d3ea886f9626bb712`。
- 状态：`reference`；verified_at=`2026-07-14`；supersedes=`none`。

#### `sample-g049` — G049 frozen scale

- 谓词：`{"all":[{"column":"ggcp10_maize_frac","operator":">=","value":0.05},{"rule":"main_sample","active":0},{"rule":"zone_core","active":0},{"rule":"yield_domain","active":1},{"rule":"yield_jump","active":1},{"rule":"sm_sd","active":0},{"rule":"sm_coverage","active":0},{"rule":"sr_within","active":0},{"rule":"years_ge3","active":0},{"rule":"stable_province","active":0}]}`。
- 规则向量：`crop_mask=ggcp10>=0.05|main_sample=0|zone_core=0|yield_domain=1|yield_jump=1|sm_sd=0|sm_coverage=0|sr_within=0|years_ge3=0|stable_province=0`。
- 样本规模：rows=50844；grids=15737；区域计数=`{"HHH":{"rows":12504,"grids":3615},"NE":{"rows":21116,"grids":6031},"NW":{"rows":3820,"grids":1532},"Other":{"rows":1818,"grids":566},"SH":{"rows":941,"grids":322},"SW":{"rows":10645,"grids":3671}}`。
- 规则代码：`repo://scripts/python/expanded_scale_story_search.py`；代码 SHA-256=`cabb1a038b1efb3b6ce88fd4f81c9eb3e086372554f2d43d3ea886f9626bb712`。
- 状态：`reference`；verified_at=`2026-07-14`；supersedes=`none`。

#### `sample-b067-g195` — B067 and G195 identical frozen mask

- 谓词：`{"all":[{"column":"ggcp10_maize_frac","operator":">=","value":0.05},{"rule":"main_sample","active":1},{"rule":"zone_core","active":1},{"rule":"yield_domain","active":0},{"rule":"yield_jump","active":0},{"rule":"sm_sd","active":0},{"rule":"sm_coverage","active":0},{"rule":"sr_within","active":1},{"rule":"years_ge3","active":0},{"rule":"stable_province","active":0}]}`。
- 规则向量：`crop_mask=ggcp10>=0.05|main_sample=1|zone_core=1|yield_domain=0|yield_jump=0|sm_sd=0|sm_coverage=0|sr_within=1|years_ge3=0|stable_province=0`。
- 样本规模：rows=42187；grids=11775；区域计数=`{"HHH":{"rows":12198,"grids":3309},"NE":{"rows":20818,"grids":5655},"NW":{"rows":3381,"grids":1113},"SH":{"rows":835,"grids":244},"SW":{"rows":4955,"grids":1454}}`。
- 规则代码：`repo://scripts/python/expanded_scale_story_search.py`；代码 SHA-256=`cabb1a038b1efb3b6ce88fd4f81c9eb3e086372554f2d43d3ea886f9626bb712`。
- 状态：`reference`；verified_at=`2026-07-14`；supersedes=`none`。

#### `sample-g185` — G185 frozen scale

- 谓词：`{"all":[{"column":"ggcp10_maize_frac","operator":">=","value":0.05},{"rule":"main_sample","active":1},{"rule":"zone_core","active":0},{"rule":"yield_domain","active":1},{"rule":"yield_jump","active":1},{"rule":"sm_sd","active":1},{"rule":"sm_coverage","active":0},{"rule":"sr_within","active":0},{"rule":"years_ge3","active":0},{"rule":"stable_province","active":0}]}`。
- 规则向量：`crop_mask=ggcp10>=0.05|main_sample=1|zone_core=0|yield_domain=1|yield_jump=1|sm_sd=1|sm_coverage=0|sr_within=0|years_ge3=0|stable_province=0`。
- 样本规模：rows=46299；grids=13236；区域计数=`{"HHH":{"rows":12213},"NE":{"rows":20794},"NW":{"rows":3414},"Other":{"rows":1743},"SH":{"rows":903},"SW":{"rows":7232}}`。
- 规则代码：`repo://scripts/python/expanded_scale_story_search.py`；代码 SHA-256=`cabb1a038b1efb3b6ce88fd4f81c9eb3e086372554f2d43d3ea886f9626bb712`。
- 状态：`current`；verified_at=`2026-07-14`；supersedes=`none`。

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `ggcp10-mediation-ext` | 2026-05-19 | `exploratory` | Created SM mean, wet-state mirror and dry-state top-3 branches with baseline, bootstrap and heterogeneity outputs |
| `scale-search-region-first` | 2026-06-11 | `reference` | Scanned 256 Gxxx rules and cluster-revalidated 208 high-score candidates under a region-first ranking |

### 方法变化

对drought、heat、precipitation hot-dry分别估计mediator和ln_yield方程；grid/year FE、grid cluster、seed 42；不等同于因果中介

#### `method-ggcp10-baseline-suite`

- Outcome / estimand：SM mediator and ln_yield equations；Hazard-specific two-equation baseline coefficients for raw, dry-state and wet-state SM。
- Exposure / mediator：Drought; heat; precipitation hot-dry; SR by hazard；Raw SM; dry state; wet state。
- Controls / FE：Companion hazards; wetness; precipitation; ET0; GDD; irrigation; aridity；Grid FE plus year FE。
- Inference：Grid-clustered standard errors；bootstrap=none；reps=0；seed=42。
- 代码入口：`repo://scripts/stata/ggcp10_baseline_suite_run_all.do`。
- 解释边界：Baseline coefficient suite only; not identified causal mediation。

### 结果呈现变化

产出local baseline coefficient suite和analysis-ready DTA；作为后续extension与scale search基础；无独立公开主结论

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-analysis-ggcp10-baseline-suite-20260518` | `ggcp10-aggregated-base\|data-v3-expanded-main-dta` | `ggcp10-suite-model-specific-samples` | `method-ggcp10-baseline-suite` | `repo://scripts/stata/ggcp10_baseline_suite_run_all.do` | `local://temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_baseline_suite_coefficients.csv` | `未公开` | reconstructed_executable |

### 相对前版与证据边界

- 综合变化：Ran paired mediator and yield equations for drought, heat and precipitation hot-dry using raw, dry-state and wet-state SM mediators
- 证据限制：SM-defined and precipitation-defined hot-dry variables remain distinct

## `area-ggcp10-aggregated` — GGCP10 aggregated 0.1-degree area panel

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-05-18；`current_data_base`；`area_component` |
| 父版/取代关系 | parent=`area-ggcp10-harvarea`；supersedes=`none` |
| 当前用途 | Current GGCP10 area base；truth role=`current_ggcp10_area_data` |
| 证据 | `three-source-confirmed`；关联脱敏对话 13 个 |

### 数据变化

将native 1/12度GGCP10 raster按面积守恒聚合到0.1度grid；结果变量明确重算为yield_tons_ha=maize_prod/ggcp10_maize_area_km2*10；分子仍为maize_prod，变化的是相对V1的面积分母

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `ggcp10-aggregated-sidecar` | data-sidecar | present | 69038×10 | `local://temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_harvarea_agg_sidecar.dta` |
| `ggcp10-aggregated-base` | analysis-panel | present | 69038×783 | `local://temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/v3_analysis_ready_ggcp10_harvarea_agg.dta` |
| `area-ggcp10-aggregated-run-manifest` | result-manifest | present | 未记录 | `repo://docs/results/area-ggcp10-aggregated/run-manifest.md` |
| `area-ggcp10-aggregated-public-report` | public-result | present | 未记录 | `repo://docs/results/area-ggcp10-aggregated/report.md` |

本版本运行使用或定义的样本规则：

#### `sample-data-v3-expanded-main` — V3 expanded yield-present panel

- 谓词：`{"column":"yield_tons_ha","operator":"is_not_missing"}`。
- 规则向量：`yield_present=1`。
- 样本规模：rows=69038；grids=22180；区域计数=`{}`。
- 规则代码：`repo://data_build/scripts/python/s10_export.py`；代码 SHA-256=`未记录`。
- 状态：`reference`；verified_at=`2026-07-14`；supersedes=`none`。

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `analysis-ggcp10-baseline-suite` | 2026-05-18 | `historical` | Ran paired mediator and yield equations for drought, heat and precipitation hot-dry using raw, dry-state and wet-state SM mediators |

### 方法变化

按经纬边界重叠权重执行area-preserving aggregation并合并grid/year；无回归推断；构建过程含面积守恒诊断

#### `method-ggcp10-aggregate-build`

- Outcome / estimand：Aggregated harvested area and area-weighted yield panel；Area-preserving overlap aggregation from native 1/12-degree raster to 0.1-degree grid。
- Exposure / mediator：GGCP10 maize harvested-area rasters for 2016-2019；not_applicable。
- Controls / FE：Grid overlap, area conservation and merge assertions；not_applicable。
- Inference：Deterministic diagnostics and conservation checks；bootstrap=none；reps=0；seed=none。
- 代码入口：`repo://scripts/python/ggcp10_build_harvarea_agg_branch.py`。
- 解释边界：Data-construction method; its area-weighted yield definition differs from V1。

### 结果呈现变化

公开数据版本说明和运行manifest，登记aggregated sidecar、V3 base、环境缺口及结构校验；二进制数据不上传

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-area-ggcp10-aggregated-20260518` | `ggcp10-raw-harvarea-raster-series\|data-v3-analysis-ready\|data-v1-county-city` | `sample-data-v3-expanded-main` | `method-ggcp10-aggregate-build` | `repo://scripts/python/ggcp10_build_harvarea_agg_branch.py` | `repo://docs/results/area-ggcp10-aggregated/run-manifest.md` | `repo://docs/results/area-ggcp10-aggregated/report.md` | historical_static |

### 相对前版与证据边界

- 综合变化：Area-preserving aggregation from the native raster grid to the 0.1-degree panel and recomputed area-weighted yield
- 证据限制：GGCP10 yield_tons_ha uses maize_prod/ggcp10_maize_area_km2*10; V1 uses maize_prod/maize_area_km2*10

## `area-ggcp10-harvarea` — GGCP10 harvested-area branch family

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-05-18；`historical`；`area_family` |
| 父版/取代关系 | parent=`data-v3-expanded`；supersedes=`none` |
| 当前用途 | Container for point-sample and aggregated branches；truth role=`historical_area_family` |
| 证据 | `three-source-confirmed`；关联脱敏对话 37 个 |

### 数据变化

引入2016-2019 GGCP10 maize harvested-area rasters；保持原maize_frac供比较；形成point与aggregated两条物理分支

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `ggcp10-raw-harvarea-raster-series` | raw-input | present | 未记录 | `local://data_build/data/raw/GGCP10_HarvArea_2010-2020/GGCP10_HarvArea_2010-2020/HarvArea_Maize_{year}.tif` |

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `area-ggcp10-aggregated` | 2026-05-18 | `current_data_base` | Area-preserving aggregation from the native raster grid to the 0.1-degree panel and recomputed area-weighted yield |
| `area-ggcp10-point-sample` | 2026-05-18 | `historical` | Sampled native GGCP10 harvested area at panel grid coordinates |

### 方法变化

数据构建家族同时记录coordinate point sample和area-preserving aggregation；不涉及回归estimand

### 结果呈现变化

公开分支文档；具体数据产物保持local；作为area命名空间父节点

### 相对前版与证据边界

- 综合变化：Replaced area-related variables with GGCP10 harvested area while retaining original maize_frac
- 证据限制：The two physical area constructions are separate components

## `area-ggcp10-point-sample` — GGCP10 point-sampled area panel

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-05-18；`historical`；`area_component` |
| 父版/取代关系 | parent=`area-ggcp10-harvarea`；supersedes=`none` |
| 当前用途 | Historical point-sample comparison branch；truth role=`historical_area_component` |
| 证据 | `three-source-confirmed`；关联脱敏对话 2 个 |

### 数据变化

把native GGCP10栅格在0.1度panel中心点取值并并入V3；相对父级选择point sampling；保留V1 outcome口径用于比较

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `ggcp10-point-base` | analysis-panel | present | 69038×781 | `local://temp/2026-05-18_ggcp10_harvarea_v6gleambl/v3_analysis_ready_ggcp10_harvarea.dta` |
| `ggcp10-point-v6-base` | analysis-panel | present | 69038×1180 | `local://temp/2026-05-18_ggcp10_harvarea_v6gleambl/v6gleambl_harvarea_analysis_ready.dta` |

本版本运行使用或定义的样本规则：

#### `sample-data-v3-expanded-main` — V3 expanded yield-present panel

- 谓词：`{"column":"yield_tons_ha","operator":"is_not_missing"}`。
- 规则向量：`yield_present=1`。
- 样本规模：rows=69038；grids=22180；区域计数=`{}`。
- 规则代码：`repo://data_build/scripts/python/s10_export.py`；代码 SHA-256=`未记录`。
- 状态：`reference`；verified_at=`2026-07-14`；supersedes=`none`。

### 方法变化

Python按坐标读取栅格值并合并grid/year；无FE、cluster或bootstrap；该构造不保面积总量

#### `method-ggcp10-point-build`

- Outcome / estimand：Point-sampled GGCP10 harvested area panel；Coordinate point sampling of native GGCP10 raster values。
- Exposure / mediator：GGCP10 maize harvested-area rasters for 2016-2019；not_applicable。
- Controls / FE：Coordinate and year matching checks；not_applicable。
- Inference：Data merge and coverage diagnostics；bootstrap=none；reps=0；seed=none。
- 代码入口：`repo://scripts/python/ggcp10_build_harvarea_branch.py`。
- 解释边界：Data-construction comparator; point values do not preserve area totals。

### 结果呈现变化

产出local point-sample V3/V6 DTA和诊断；仅作历史对照；未选为当前面积基础

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-area-ggcp10-point-20260518` | `ggcp10-raw-harvarea-raster-series\|data-v3-analysis-ready` | `sample-data-v3-expanded-main` | `method-ggcp10-point-build` | `repo://scripts/python/ggcp10_build_harvarea_branch.py` | `local://temp/2026-05-18_ggcp10_harvarea_v6gleambl/v3_analysis_ready_ggcp10_harvarea.dta` | `repo://docs/GGCP10_HARVAREA_BRANCH.md` | reconstructed_executable |

### 相对前版与证据边界

- 综合变化：Sampled native GGCP10 harvested area at panel grid coordinates
- 证据限制：Not equivalent to area-preserving aggregation

## `ggcp10-mediation-ext` — GGCP10 two-equation extensions

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-05-19；`exploratory`；`analysis_family` |
| 父版/取代关系 | parent=`analysis-ggcp10-baseline-suite`；supersedes=`none` |
| 当前用途 | Completed exploratory family；truth role=`exploratory_ggcp10_family` |
| 证据 | `three-source-confirmed`；关联脱敏对话 10 个 |

### 数据变化

基于aggregated baseline suite分成SM mean、wet mirror、dry top3；GLEAM-only；各分支有独立sample与表数

本版本运行使用或定义的样本规则：

#### `ggcp10-extension-branch-samples` — GGCP10 mediation-extension branch samples

- 谓词：`{"registry":"mean wet_mirror and dry_top3 branch-specific flags"}`。
- 规则向量：`branch_specific_complete_cases`。
- 样本规模：rows=未记录；grids=未记录；区域计数=`{}`。
- 规则代码：`repo://scripts/stata/ggcp10_mean_ext_run_all.do`；代码 SHA-256=`358a1a4c6131ccbf5501d5d404bf0745908647f7f4931835885ac42191672bd3`。
- 状态：`historical`；verified_at=`2026-07-14`；supersedes=`sample-ggcp10-baseline-main`。

### 方法变化

两方程baseline、bootstrap和region/irrigation heterogeneity；grid/year FE与grid cluster；原mean分支bootstrap 80 reps，seed 42

#### `method-ggcp10-mediation-ext`

- Outcome / estimand：SM mediator and ln_yield equations；Baseline, conditional two-equation components and heterogeneity across three extension branches。
- Exposure / mediator：Drought; heat; precipitation hot-dry; SR by hazard；GLEAM mean; wet-state mirror; dry-state top-three。
- Controls / FE：Companion hazards and climate or irrigation controls；Grid FE plus year FE; subgroup FE models。
- Inference：Grid-clustered standard errors；bootstrap=Historical branch-specific cluster bootstrap; mean branch initially 80 reps；reps=80；seed=42。
- 代码入口：`repo://scripts/stata/ggcp10_mean_ext_run_all.do`。
- 解释边界：Reps differ across branch outputs; components remain associational。

### 结果呈现变化

产出三分支CSV、21/12/21组图及handoff；属于exploratory family；不写成identified causal mediation

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-ggcp10-mediation-ext-20260519` | `ggcp10-baseline-suite\|data-v3-expanded-main-dta` | `ggcp10-extension-branch-samples` | `method-ggcp10-mediation-ext` | `repo://scripts/stata/ggcp10_mean_ext_run_all.do` | `local://temp/2026-05-19_ggcp10_mediation_extensions/mean/ggcp10_mean_baseline_coefficients.csv` | `未公开` | reconstructed_executable |

### 相对前版与证据边界

- 综合变化：Created SM mean, wet-state mirror and dry-state top-3 branches with baseline, bootstrap and heterogeneity outputs
- 证据限制：Two-equation components are not identified causal mediation

## `scale-b067-g195` — B067 and G195 legacy scales

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-06-04；`reference`；`sample_rule_alias_group` |
| 父版/取代关系 | parent=`scale-search-region-first`；supersedes=`none` |
| 当前用途 | Legacy comparison reference；truth role=`legacy_scale_reference` |
| 证据 | `two-source-supported`；关联脱敏对话 25 个 |

### 数据变化

登记旧B067样本及其在256规则枚举中的G195映射；原始形成日期未知；不推定与G185相同样本

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `g195-b067-virtual-sample` | derived-sample | virtual | 42187 | `local://virtual/g195-b067-sample` |

本版本运行使用或定义的样本规则：

#### `sample-b067-g195` — B067 and G195 identical frozen mask

- 谓词：`{"all":[{"column":"ggcp10_maize_frac","operator":">=","value":0.05},{"rule":"main_sample","active":1},{"rule":"zone_core","active":1},{"rule":"yield_domain","active":0},{"rule":"yield_jump","active":0},{"rule":"sm_sd","active":0},{"rule":"sm_coverage","active":0},{"rule":"sr_within","active":1},{"rule":"years_ge3","active":0},{"rule":"stable_province","active":0}]}`。
- 规则向量：`crop_mask=ggcp10>=0.05|main_sample=1|zone_core=1|yield_domain=0|yield_jump=0|sm_sd=0|sm_coverage=0|sr_within=1|years_ge3=0|stable_province=0`。
- 样本规模：rows=42187；grids=11775；区域计数=`{"HHH":{"rows":12198,"grids":3309},"NE":{"rows":20818,"grids":5655},"NW":{"rows":3381,"grids":1113},"SH":{"rows":835,"grids":244},"SW":{"rows":4955,"grids":1454}}`。
- 规则代码：`repo://scripts/python/expanded_scale_story_search.py`；代码 SHA-256=`cabb1a038b1efb3b6ce88fd4f81c9eb3e086372554f2d43d3ea886f9626bb712`。
- 状态：`reference`；verified_at=`2026-07-14`；supersedes=`none`。

### 方法变化

历史national/phenology规则映射；方法细节仅由现存scale search材料部分恢复；不作为当前estimand

### 结果呈现变化

以legacy mapping形式出现在scale报告；不发布为当前结果；lineage confidence为mixed

### 相对前版与证据边界

- 综合变化：Registered the historical national B067 rule and its G195 mapping in the expanded scale enumeration
- 证据限制：Original formation date remains unknown

## `scale-g049` — G049 scale

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-06-11；`reference`；`sample_rule` |
| 父版/取代关系 | parent=`scale-search-region-first`；supersedes=`none` |
| 当前用途 | Selection reference；truth role=`scale_reference` |
| 证据 | `three-source-confirmed`；关联脱敏对话 14 个 |

### 数据变化

以G049独立规则mask形成近似G057的样本；相对G057少一项SM质量规则；样本不等同G185

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `g049-virtual-sample` | derived-sample | virtual | 50844 | `local://virtual/g049-sample` |

本版本运行使用或定义的样本规则：

#### `sample-g049` — G049 frozen scale

- 谓词：`{"all":[{"column":"ggcp10_maize_frac","operator":">=","value":0.05},{"rule":"main_sample","active":0},{"rule":"zone_core","active":0},{"rule":"yield_domain","active":1},{"rule":"yield_jump","active":1},{"rule":"sm_sd","active":0},{"rule":"sm_coverage","active":0},{"rule":"sr_within","active":0},{"rule":"years_ge3","active":0},{"rule":"stable_province","active":0}]}`。
- 规则向量：`crop_mask=ggcp10>=0.05|main_sample=0|zone_core=0|yield_domain=1|yield_jump=1|sm_sd=0|sm_coverage=0|sr_within=0|years_ge3=0|stable_province=0`。
- 样本规模：rows=50844；grids=15737；区域计数=`{"HHH":{"rows":12504,"grids":3615},"NE":{"rows":21116,"grids":6031},"NW":{"rows":3820,"grids":1532},"Other":{"rows":1818,"grids":566},"SH":{"rows":941,"grids":322},"SW":{"rows":10645,"grids":3671}}`。
- 规则代码：`repo://scripts/python/expanded_scale_story_search.py`；代码 SHA-256=`cabb1a038b1efb3b6ce88fd4f81c9eb3e086372554f2d43d3ea886f9626bb712`。
- 状态：`reference`；verified_at=`2026-07-14`；supersedes=`none`。

### 方法变化

使用同一region-first评估和grid-cluster FE复核框架；单独脚本测试区域故事

### 结果呈现变化

仅作为near-twin敏感性参考；结果不进入G185 claim；公开报告标注selection context

### 相对前版与证据边界

- 综合变化：Registered the near-twin of G057 with one fewer SM quality rule
- 证据限制：Do not mix its estimates into G185 claims

## `scale-g057` — G057 scale

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-06-11；`reference`；`sample_rule` |
| 父版/取代关系 | parent=`scale-search-region-first`；supersedes=`none` |
| 当前用途 | Selection reference；truth role=`scale_reference` |
| 证据 | `three-source-confirmed`；关联脱敏对话 26 个 |

### 数据变化

从候选规则生成G057 mask；相对其他scale使用其独立规则向量和样本；不能共享估计结果

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `g057-virtual-sample` | derived-sample | virtual | 50771 | `local://virtual/g057-sample` |

本版本运行使用或定义的样本规则：

#### `sample-g057` — G057 frozen scale

- 谓词：`{"all":[{"column":"ggcp10_maize_frac","operator":">=","value":0.05},{"rule":"main_sample","active":0},{"rule":"zone_core","active":0},{"rule":"yield_domain","active":1},{"rule":"yield_jump","active":1},{"rule":"sm_sd","active":1},{"rule":"sm_coverage","active":0},{"rule":"sr_within","active":0},{"rule":"years_ge3","active":0},{"rule":"stable_province","active":0}]}`。
- 规则向量：`crop_mask=ggcp10>=0.05|main_sample=0|zone_core=0|yield_domain=1|yield_jump=1|sm_sd=1|sm_coverage=0|sr_within=0|years_ge3=0|stable_province=0`。
- 样本规模：rows=50771；grids=15729；区域计数=`{"HHH":{"rows":12504,"grids":3615},"NE":{"rows":21116,"grids":6031},"NW":{"rows":3747,"grids":1524},"Other":{"rows":1818,"grids":566},"SH":{"rows":941,"grids":322},"SW":{"rows":10645,"grids":3671}}`。
- 规则代码：`repo://scripts/python/expanded_scale_story_search.py`；代码 SHA-256=`cabb1a038b1efb3b6ce88fd4f81c9eb3e086372554f2d43d3ea886f9626bb712`。
- 状态：`reference`；verified_at=`2026-07-14`；supersedes=`none`。

### 方法变化

沿用region-first FE和scaled-buffer评估；grid/year FE、grid cluster；pooled Wald用于区域差异核对

### 结果呈现变化

作为探索排名第一的参考scale呈现；公开报告保留方向和显著性限制；不称唯一最优

### 相对前版与证据边界

- 综合变化：Ranked first in the exploratory region-first search with a region-specific hazard pattern
- 证据限制：NW evidence remains directional and G057 is not uniquely optimal

## `scale-g185` — G185 scale

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-06-11；`current`；`sample_rule` |
| 父版/取代关系 | parent=`scale-search-region-first`；supersedes=`none` |
| 当前用途 | Current G185 analysis sample；truth role=`current_analysis_scale` |
| 证据 | `three-source-confirmed`；关联脱敏对话 29 个 |

### 数据变化

规则固定为ggcp10_maize_frac≥0.05且main_sample、yield_domain、yield_jump、sm_sd为1，其余可选规则为0；N=46299、grids=13236

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `g185-virtual-sample` | derived-sample | virtual | 46299 | `local://virtual/g185-sample` |
| `scale-g185-run-manifest` | result-manifest | present | 未记录 | `repo://docs/results/scale-g185/run-manifest.md` |

本版本运行使用或定义的样本规则：

#### `sample-g185` — G185 frozen scale

- 谓词：`{"all":[{"column":"ggcp10_maize_frac","operator":">=","value":0.05},{"rule":"main_sample","active":1},{"rule":"zone_core","active":0},{"rule":"yield_domain","active":1},{"rule":"yield_jump","active":1},{"rule":"sm_sd","active":1},{"rule":"sm_coverage","active":0},{"rule":"sr_within","active":0},{"rule":"years_ge3","active":0},{"rule":"stable_province","active":0}]}`。
- 规则向量：`crop_mask=ggcp10>=0.05|main_sample=1|zone_core=0|yield_domain=1|yield_jump=1|sm_sd=1|sm_coverage=0|sr_within=0|years_ge3=0|stable_province=0`。
- 样本规模：rows=46299；grids=13236；区域计数=`{"HHH":{"rows":12213},"NE":{"rows":20794},"NW":{"rows":3414},"Other":{"rows":1743},"SH":{"rows":903},"SW":{"rows":7232}}`。
- 规则代码：`repo://scripts/python/expanded_scale_story_search.py`；代码 SHA-256=`cabb1a038b1efb3b6ce88fd4f81c9eb3e086372554f2d43d3ea886f9626bb712`。
- 状态：`current`；verified_at=`2026-07-14`；supersedes=`none`。

#### `sample-g185-named-regions` — G185 named maize-zone subset

- 谓词：`{"column":"maize_zone","operator":"in","values":["NE","HHH","NW","SW","SH"]}`。
- 规则向量：`G185|maize_zone=NE,HHH,NW,SW,SH`。
- 样本规模：rows=44556；grids=12745；区域计数=`{"HHH":{"rows":12213,"grids":3324},"NE":{"rows":20794,"grids":5715},"NW":{"rows":3414,"grids":1191},"SH":{"rows":903,"grids":284},"SW":{"rows":7232,"grids":2231}}`。
- 规则代码：`repo://scripts/python/g185_v3_data.py`；代码 SHA-256=`eeb9cebc3b650b4bfc0c4d5cb622b4911500d98b17252c84e0c620c570cdac1a`。
- 状态：`current`；verified_at=`2026-07-14`；supersedes=`sample-g185`。

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `g185-draft-bootstrap-v1` | 2026-06-20 | `superseded` | Built G185-only two-equation, region, continuous irrigation and phenology results with wild-score bootstrap intervals |
| `g185-response-surface-v3` | 2026-06-21 | `reviewed_sensitivity` | Added restricted-cubic low-degree drought-heat surfaces, spatial-block inference and explicit claim adjudication |
| `g185-old-method-corrected` | 2026-06-24 | `current` | Recomputed regional IE, DE and TE and corrected the earlier DE-as-TE interpretation |
| `g185-region-irrigation-boundary` | 2026-06-24 | `current_parallel` | Estimated region-specific continuous irrigation triple interactions and support-aware margins |

### 方法变化

样本选择由region-first search透明产生；后续方法必须在同一G185 mask上运行；规则或计数变化即创建新scale ID

#### `method-scale-g185-freeze`

- Outcome / estimand：Binary G185 analytical-sample mask；Exact rule-vector application and count invariance。
- Exposure / mediator：ggcp10_maize_frac and nine candidate quality rules；not_applicable。
- Controls / FE：Rule vector, N equals 46299 and grid count equals 13236 assertions；not_applicable。
- Inference：Deterministic sample-count assertions；bootstrap=none；reps=0；seed=42。
- 代码入口：`repo://scripts/python/expanded_scale_story_search.py`。
- 解释边界：Changing any rule, row count or grid count requires a new scale ID。

### 结果呈现变化

公开scale-search报告、G185运行manifest和Stata复核；固定规则向量、46299行与13236 grids；严禁混入G057/G049数值

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-scale-g185-freeze-20260611` | `ggcp10-baseline-suite\|data-v3-expanded-main-dta` | `sample-g185` | `method-scale-g185-freeze` | `repo://scripts/python/expanded_scale_story_search.py` | `repo://docs/results/scale-g185/run-manifest.md` | `repo://docs/results/scale-search-region-first/report.md` | verified_current |

### 相对前版与证据边界

- 综合变化：Retained main_sample, yield-domain, yield-jump and SM-SD rules while omitting the other optional rules
- 证据限制：Frozen rule yields 46299 rows and 13236 grids; any rule or count change requires a new scale ID

## `scale-search-region-first` — Region-first scale search

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-06-11；`reference`；`scale_search` |
| 父版/取代关系 | parent=`analysis-ggcp10-baseline-suite`；supersedes=`none` |
| 当前用途 | Exploratory selection context；truth role=`scale_selection_context` |
| 证据 | `three-source-confirmed`；关联脱敏对话 26 个 |

### 数据变化

以GGCP10 aggregated panel和V3变量构造256个布尔scale；统一最低ggcp10_maize_frac≥0.05；208个高分候选进入cluster复核

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `scale-b067-g195` | 2026-06-04 | `reference` | Registered the historical national B067 rule and its G195 mapping in the expanded scale enumeration |
| `scale-g049` | 2026-06-11 | `reference` | Registered the near-twin of G057 with one fewer SM quality rule |
| `scale-g057` | 2026-06-11 | `reference` | Ranked first in the exploratory region-first search with a region-specific hazard pattern |
| `scale-g185` | 2026-06-11 | `current` | Retained main_sample, yield-domain, yield-jump and SM-SD rules while omitting the other optional rules |

### 方法变化

先OLS扫描region-specific scaled buffer再以grid-cluster FE复核；region-first评分结合NE drought、HHH heat/hot-dry和辅助分数；seed按脚本固定

#### `method-scale-region-first`

- Outcome / estimand：Region-hazard scaled buffering score；Ranking of candidate sample-rule masks by region-first evidence and support。
- Exposure / mediator：Drought; heat; precipitation hot-dry; SR by hazard；gleam_smrz_mean as yield-equation control in direct models。
- Controls / FE：Companion hazards; precipitation; ET0; GDD; irrigation; aridity；Grid FE plus year FE in cluster validation; pooled region-year FE in Wald checks。
- Inference：Initial OLS scan followed by grid-clustered covariance for 208 high-score candidates；bootstrap=none；reps=0；seed=42。
- 代码入口：`repo://scripts/python/region_first_story_search.py`。
- 解释边界：Exploratory transparent selection; ranking is not preregistration or proof of unique optimality。

### 结果呈现变化

产出ranking CSV、story cards、公开Markdown和本地详细报告；用于透明selection context而非预注册

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-scale-region-first-20260611` | `ggcp10-baseline-suite\|data-v3-expanded-main-dta` | `未冻结` | `method-scale-region-first` | `repo://scripts/python/region_first_story_search.py` | `local://temp/2026-06-11_region_first_story_search/ranking_cluster.csv` | `repo://docs/results/scale-search-region-first/report.md` | reconstructed_executable |

### 相对前版与证据边界

- 综合变化：Scanned 256 Gxxx rules and cluster-revalidated 208 high-score candidates under a region-first ranking
- 证据限制：Scale selection is transparent exploratory analysis and not preregistration

## `g185-draft-bootstrap-v1` — G185 draft bootstrap v1

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-06-20；`superseded`；`analysis_release` |
| 父版/取代关系 | parent=`scale-g185`；supersedes=`none` |
| 当前用途 | Historical construction logic；truth role=`historical_g185_construction` |
| 证据 | `three-source-confirmed`；关联脱敏对话 8 个 |

### 数据变化

输入GGCP10 aggregated base、data-v3变量和冻结G185 mask；N=46299、grids=13236；五命名区模型排除Other

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `g185-draft-bootstrap-run-manifest` | result-manifest | present | 6×2 | `local://quality_reports/agent_runs/2026-06-20_g185_draft_bootstrap_v1/run_manifest.csv` |

本版本运行使用或定义的样本规则：

#### `sample-g185` — G185 frozen scale

- 谓词：`{"all":[{"column":"ggcp10_maize_frac","operator":">=","value":0.05},{"rule":"main_sample","active":1},{"rule":"zone_core","active":0},{"rule":"yield_domain","active":1},{"rule":"yield_jump","active":1},{"rule":"sm_sd","active":1},{"rule":"sm_coverage","active":0},{"rule":"sr_within","active":0},{"rule":"years_ge3","active":0},{"rule":"stable_province","active":0}]}`。
- 规则向量：`crop_mask=ggcp10>=0.05|main_sample=1|zone_core=0|yield_domain=1|yield_jump=1|sm_sd=1|sm_coverage=0|sr_within=0|years_ge3=0|stable_province=0`。
- 样本规模：rows=46299；grids=13236；区域计数=`{"HHH":{"rows":12213},"NE":{"rows":20794},"NW":{"rows":3414},"Other":{"rows":1743},"SH":{"rows":903},"SW":{"rows":7232}}`。
- 规则代码：`repo://scripts/python/expanded_scale_story_search.py`；代码 SHA-256=`cabb1a038b1efb3b6ce88fd4f81c9eb3e086372554f2d43d3ea886f9626bb712`。
- 状态：`current`；verified_at=`2026-07-14`；supersedes=`none`。

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `g185-method-upgrade` | 2026-06-20 | `current_parallel` | Made fixed-effect damage-avoidance margins the main evidence and retained econml, DoubleML and R grf as appendix heterogeneity concordance checks |

### 方法变化

grid/year FE两方程IE/DE/TE、region FE、continuous irrigation triple及phenology compound模型；grid wild-score linearized bootstrap 999 reps；seed 42

#### `method-g185-draft`

- Outcome / estimand：ln_yield and gleam_smrz_mean_raw；Hazard-specific algebraic IE, DE, TE; regional scaled buffer; irrigation and phenology margins。
- Exposure / mediator：D_full_raw; hdd_ge32_raw; HotDryPr_full_raw; SR interactions；gleam_smrz_mean_raw。
- Controls / FE：Companion hazards; precipitation; ET0; GDD; irrigation; aridity；Grid FE plus year FE; separate region models。
- Inference：Grid-cluster covariance and absorbed-design uncertainty；bootstrap=Grid-level Rademacher wild-score bootstrap-linearized intervals；reps=999；seed=42。
- 代码入口：`repo://scripts/python/build_g185_draft_bootstrap_v1.py`。
- 解释边界：Initial pack; later regional DE values were incorrectly narrated as TE and are superseded。

### 结果呈现变化

产出本地manuscript、描述统计、表和四图；早期将部分DE数值写成TE；解释已由2026-06-24修正版取代

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-g185-draft-bootstrap-v1-20260620` | `g185-virtual-sample\|ggcp10-baseline-suite\|data-v3-expanded-main-dta` | `sample-g185` | `method-g185-draft` | `repo://scripts/python/build_g185_draft_bootstrap_v1.py` | `local://quality_reports/agent_runs/2026-06-20_g185_draft_bootstrap_v1/run_manifest.csv` | `未公开` | verified_superseded_interpretation |

### 相对前版与证据边界

- 综合变化：Built G185-only two-equation, region, continuous irrigation and phenology results with wild-score bootstrap intervals
- 证据限制：Regional DE values were later mislabelled as TE and are superseded

## `g185-method-upgrade` — G185 method-upgrade report

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-06-20；`current_parallel`；`analysis_release` |
| 父版/取代关系 | parent=`g185-draft-bootstrap-v1`；supersedes=`none` |
| 当前用途 | Current parallel method entry；truth role=`current_fixed_effects_and_ml_appendix` |
| 证据 | `three-source-confirmed`；关联脱敏对话 7 个 |

### 数据变化

继续使用完全相同的G185输入和sample；不引入G057/G049数据；FE主表直接读取draft-bootstrap输出

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `g185-method-upgrade-run-manifest` | result-manifest | present | 15×2 | `local://quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/run_manifest.csv` |
| `g185-method-upgrade-public-report` | public-result | present | 未记录 | `repo://docs/results/g185-method-upgrade/report.md` |

本版本运行使用或定义的样本规则：

#### `sample-g185` — G185 frozen scale

- 谓词：`{"all":[{"column":"ggcp10_maize_frac","operator":">=","value":0.05},{"rule":"main_sample","active":1},{"rule":"zone_core","active":0},{"rule":"yield_domain","active":1},{"rule":"yield_jump","active":1},{"rule":"sm_sd","active":1},{"rule":"sm_coverage","active":0},{"rule":"sr_within","active":0},{"rule":"years_ge3","active":0},{"rule":"stable_province","active":0}]}`。
- 规则向量：`crop_mask=ggcp10>=0.05|main_sample=1|zone_core=0|yield_domain=1|yield_jump=1|sm_sd=1|sm_coverage=0|sr_within=0|years_ge3=0|stable_province=0`。
- 样本规模：rows=46299；grids=13236；区域计数=`{"HHH":{"rows":12213},"NE":{"rows":20794},"NW":{"rows":3414},"Other":{"rows":1743},"SH":{"rows":903},"SW":{"rows":7232}}`。
- 规则代码：`repo://scripts/python/expanded_scale_story_search.py`；代码 SHA-256=`cabb1a038b1efb3b6ce88fd4f81c9eb3e086372554f2d43d3ea886f9626bb712`。
- 状态：`current`；verified_at=`2026-07-14`；supersedes=`none`。

### 方法变化

固定效应damage-avoidance margins作为主estimand；econml、DoubleML和R grf仅作异质性concordance；FE bootstrap 999 reps、seed 42，ML参数由requirements和run config锁定

#### `method-g185-upgrade`

- Outcome / estimand：ln_yield_raw；Fixed-effect damage-avoidance margins with ML heterogeneity concordance checks。
- Exposure / mediator：Drought; heat; hot-dry; SR interactions；gleam_smrz_mean_raw in relevant FE equations。
- Controls / FE：Companion hazards; precipitation; ET0; GDD; irrigation; aridity；Grid FE plus year FE for substantive FE results。
- Inference：Grid-cluster FE inference; econml, DoubleML and grf are appendix checks；bootstrap=Reuses draft within-transformed wild-score intervals；reps=999；seed=42。
- 代码入口：`repo://scripts/python/build_g185_method_upgrade_report.py`。
- 解释边界：ML does not validate an adoption effect; FE tables are read from the draft-bootstrap run。

### 结果呈现变化

新增自包含HTML、Markdown、ML附录图表和公开摘要；叙事改为conditional association；作为当前并行方法入口

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-g185-method-upgrade-20260620` | `g185-virtual-sample\|ggcp10-baseline-suite\|data-v3-expanded-main-dta\|g185-draft-bootstrap-run-manifest` | `sample-g185` | `method-g185-upgrade` | `repo://scripts/python/build_g185_method_upgrade_report.py` | `local://quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/run_manifest.csv` | `repo://docs/results/g185-method-upgrade/report.md` | verified_current |

### 相对前版与证据边界

- 综合变化：Made fixed-effect damage-avoidance margins the main evidence and retained econml, DoubleML and R grf as appendix heterogeneity concordance checks
- 证据限制：The fixed-effect main tables are read from the draft-bootstrap run; ML does not validate an adoption impact

## `g185-response-surface-v3` — G185 response-surface v3

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-06-21；`reviewed_sensitivity`；`analysis_release` |
| 父版/取代关系 | parent=`scale-g185`；supersedes=`none` |
| 当前用途 | Reviewed alternative-method sensitivity；truth role=`reviewed_alternative_method` |
| 证据 | `three-source-confirmed`；关联脱敏对话 5 个 |

### 数据变化

使用同一G185 mask但为surface模型重新构造complete-case与区域样本；N规则不变；不替代旧方法输入

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `g185-response-surface-run-manifest` | result-manifest | present | 1×9 | `local://quality_reports/agent_runs/2026-06-20_g185_response_surface_v3/01_run_manifest.json` |
| `g185-response-surface-public-report` | public-result | present | 未记录 | `repo://docs/results/g185-response-surface-v3/report.md` |

本版本运行使用或定义的样本规则：

#### `sample-g185` — G185 frozen scale

- 谓词：`{"all":[{"column":"ggcp10_maize_frac","operator":">=","value":0.05},{"rule":"main_sample","active":1},{"rule":"zone_core","active":0},{"rule":"yield_domain","active":1},{"rule":"yield_jump","active":1},{"rule":"sm_sd","active":1},{"rule":"sm_coverage","active":0},{"rule":"sr_within","active":0},{"rule":"years_ge3","active":0},{"rule":"stable_province","active":0}]}`。
- 规则向量：`crop_mask=ggcp10>=0.05|main_sample=1|zone_core=0|yield_domain=1|yield_jump=1|sm_sd=1|sm_coverage=0|sr_within=0|years_ge3=0|stable_province=0`。
- 样本规模：rows=46299；grids=13236；区域计数=`{"HHH":{"rows":12213},"NE":{"rows":20794},"NW":{"rows":3414},"Other":{"rows":1743},"SH":{"rows":903},"SW":{"rows":7232}}`。
- 规则代码：`repo://scripts/python/expanded_scale_story_search.py`；代码 SHA-256=`cabb1a038b1efb3b6ce88fd4f81c9eb3e086372554f2d43d3ea886f9626bb712`。
- 状态：`current`；verified_at=`2026-07-14`；supersedes=`none`。

### 方法变化

四结点restricted cubic drought-heat surface、region-specific SR×surface；grid FE加province-year FE；2度spatial-block Rademacher wild-score final 1999 reps；seed 20260620

#### `method-g185-response-surface-v3`

- Outcome / estimand：ln_yield_raw；Region-specific SR-associated changes over a restricted-cubic drought-heat response surface。
- Exposure / mediator：Restricted-cubic drought and heat surface; region by surface; SR by surface；SM included only in designated sensitivity models。
- Controls / FE：C0 or C1 climate controls; optional SM control；Grid FE plus province-by-year FE in the primary model。
- Inference：Synchronous 2-degree spatial-block inference for region contrasts；bootstrap=Rademacher spatial-block wild-score linearized draws；reps=1999；seed=20260620。
- 代码入口：`repo://scripts/python/run_all_g185_v3.py`。
- 解释边界：Different estimand from old-method IE-DE-TE; reviewed non-support and sensitivity findings must be retained。

### 结果呈现变化

产出review bundle、claim adjudication、surface图和公开Markdown；明确NE drought/SM consistency不支持及其他敏感项；仅作reviewed sensitivity

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-g185-response-surface-v3-20260621` | `g185-virtual-sample\|ggcp10-baseline-suite\|data-v3-expanded-main-dta` | `sample-g185` | `method-g185-response-surface-v3` | `repo://scripts/python/run_all_g185_v3.py` | `local://quality_reports/agent_runs/2026-06-20_g185_response_surface_v3/01_run_manifest.json` | `repo://docs/results/g185-response-surface-v3/report.md` | verified_sensitivity |

### 相对前版与证据边界

- 综合变化：Added restricted-cubic low-degree drought-heat surfaces, spatial-block inference and explicit claim adjudication
- 证据限制：Different estimand from the old-method decomposition; it cannot be described as validation of that result

## `g185-old-method-corrected` — G185 corrected old-method IE-DE-TE

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-06-24；`current`；`analysis_release` |
| 父版/取代关系 | parent=`scale-g185`；supersedes=`g185-draft-bootstrap-v1` |
| 当前用途 | Current truth for old-method regional TE；truth role=`current_old_method_te` |
| 证据 | `three-source-confirmed`；关联脱敏对话 5 个 |

### 数据变化

使用同一G185 mask、root-zone GLEAM mediator和raw hazard变量；区域内P25/P75 SR及P90 hazard重新计算；不改变数据版本

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `g185-old-method-corrected-manifest` | result-manifest | present | 1×16 | `local://quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/manifest.json` |
| `g185-old-method-corrected-public-report` | public-result | present | 未记录 | `repo://docs/results/g185-old-method-corrected/report.md` |

本版本运行使用或定义的样本规则：

#### `sample-g185` — G185 frozen scale

- 谓词：`{"all":[{"column":"ggcp10_maize_frac","operator":">=","value":0.05},{"rule":"main_sample","active":1},{"rule":"zone_core","active":0},{"rule":"yield_domain","active":1},{"rule":"yield_jump","active":1},{"rule":"sm_sd","active":1},{"rule":"sm_coverage","active":0},{"rule":"sr_within","active":0},{"rule":"years_ge3","active":0},{"rule":"stable_province","active":0}]}`。
- 规则向量：`crop_mask=ggcp10>=0.05|main_sample=1|zone_core=0|yield_domain=1|yield_jump=1|sm_sd=1|sm_coverage=0|sr_within=0|years_ge3=0|stable_province=0`。
- 样本规模：rows=46299；grids=13236；区域计数=`{"HHH":{"rows":12213},"NE":{"rows":20794},"NW":{"rows":3414},"Other":{"rows":1743},"SH":{"rows":903},"SW":{"rows":7232}}`。
- 规则代码：`repo://scripts/python/expanded_scale_story_search.py`；代码 SHA-256=`cabb1a038b1efb3b6ce88fd4f81c9eb3e086372554f2d43d3ea886f9626bb712`。
- 状态：`current`；verified_at=`2026-07-14`；supersedes=`none`。

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `g185-old-method-unified-v1` | 2026-07-14 | `reference` | Unified the historical linear two-equation evidence and added province-by-year fixed effects, spatial-block inference and explicit stability adjudication |

### 方法变化

旧线性grid/year FE两方程；IE=(a1+a3s)b、DE=c1+c3s、TE=IE+DE；grid wild-score linearized bootstrap 999 reps；seed 42

#### `method-g185-old-corrected`

- Outcome / estimand：ln_yield_raw paired with gleam_smrz_mean_raw equation；IE=(a1+a3s)b, DE=c1+c3s and TE=IE+DE at regional SR and hazard quantiles。
- Exposure / mediator：D_full_raw; hdd_ge32_raw; HotDryPr_full_raw; SR by hazard；gleam_smrz_mean_raw。
- Controls / FE：Companion hazards; precipitation; ET0; GDD; irrigation; aridity；Grid FE plus year FE within region。
- Inference：Absorbed-design grid-cluster inference；bootstrap=Grid-level Rademacher wild-score bootstrap-linearized intervals；reps=999；seed=42。
- 代码入口：`repo://scripts/python/export_g185_old_method_region_tiede_redraw.py`。
- 解释边界：Algebraic two-equation components only; corrected TE must replace the former DE-as-TE narrative。

### 结果呈现变化

重新绘制region IE/DE/TE表和图；纠正1.50%、3.27%、2.56%为DE而非TE；当前旧方法真值由公开Markdown呈现

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-g185-old-method-corrected-20260624` | `g185-virtual-sample\|ggcp10-baseline-suite\|data-v3-expanded-main-dta` | `sample-g185` | `method-g185-old-corrected` | `repo://scripts/python/export_g185_old_method_region_tiede_redraw.py` | `local://quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/manifest.json` | `repo://docs/results/g185-old-method-corrected/report.md` | verified_current |

### 相对前版与证据边界

- 综合变化：Recomputed regional IE, DE and TE and corrected the earlier DE-as-TE interpretation
- 证据限制：IE、DE和TE是两方程代数组件，不是已识别因果中介；现有research-g185-old-method-corrected-2026.07.13 tag与同名Release对应包含多个公开结果族的Git复合基线，不是本运行的同期历史快照

## `g185-region-irrigation-boundary` — G185 regional irrigation boundary

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-06-24；`current_parallel`；`analysis_release` |
| 父版/取代关系 | parent=`scale-g185`；supersedes=`none` |
| 当前用途 | Current separate boundary result；truth role=`current_irrigation_boundary` |
| 证据 | `three-source-confirmed`；关联脱敏对话 2 个 |

### 数据变化

使用同一G185 mask并在五区域内计算连续irr_frac支持、SR IQR和hazard P90；与IE/DE/TE共用数据但不共用estimand

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `g185-region-irrigation-manifest` | result-manifest | present | 1×13 | `local://quality_reports/agent_runs/2026-06-24_g185_region_specific_irrigation_boundary/manifest.json` |
| `g185-region-irrigation-public-report` | public-result | present | 未记录 | `repo://docs/results/g185-region-irrigation-boundary/report.md` |

本版本运行使用或定义的样本规则：

#### `sample-g185` — G185 frozen scale

- 谓词：`{"all":[{"column":"ggcp10_maize_frac","operator":">=","value":0.05},{"rule":"main_sample","active":1},{"rule":"zone_core","active":0},{"rule":"yield_domain","active":1},{"rule":"yield_jump","active":1},{"rule":"sm_sd","active":1},{"rule":"sm_coverage","active":0},{"rule":"sr_within","active":0},{"rule":"years_ge3","active":0},{"rule":"stable_province","active":0}]}`。
- 规则向量：`crop_mask=ggcp10>=0.05|main_sample=1|zone_core=0|yield_domain=1|yield_jump=1|sm_sd=1|sm_coverage=0|sr_within=0|years_ge3=0|stable_province=0`。
- 样本规模：rows=46299；grids=13236；区域计数=`{"HHH":{"rows":12213},"NE":{"rows":20794},"NW":{"rows":3414},"Other":{"rows":1743},"SH":{"rows":903},"SW":{"rows":7232}}`。
- 规则代码：`repo://scripts/python/expanded_scale_story_search.py`；代码 SHA-256=`cabb1a038b1efb3b6ce88fd4f81c9eb3e086372554f2d43d3ea886f9626bb712`。
- 状态：`current`；verified_at=`2026-07-14`；supersedes=`none`。

### 方法变化

region-specific hazard×SR×irrigation triple interaction；grid/year FE；grid wild-score linearized bootstrap 999 reps；seed 42；报告P5-P95支持与P25/P50/P75 margins

#### `method-g185-irrigation-boundary`

- Outcome / estimand：ln_yield_raw；Region-specific change in the SR-associated hazard slope over continuous irrigation support。
- Exposure / mediator：Hazard; SR; irrigation; all two-way terms; SR by hazard by irrigation；none。
- Controls / FE：Companion hazards; precipitation; ET0; GDD; aridity；Grid FE plus year FE within region。
- Inference：Absorbed-design grid-cluster inference with support diagnostics；bootstrap=Grid-level Rademacher wild-score bootstrap-linearized intervals；reps=999；seed=42。
- 代码入口：`repo://scripts/python/export_g185_region_specific_irrigation_boundary.py`。
- 解释边界：Separate estimand from IE-DE-TE; report intervals crossing zero without directional overstatement。

### 结果呈现变化

产出区域灌溉边界图、tables、assertions和公开Markdown；NE drought支持，HHH heat/hot-dry区间跨零；作为当前独立并行结果

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-g185-region-irrigation-20260624` | `g185-virtual-sample\|ggcp10-baseline-suite\|data-v3-expanded-main-dta` | `sample-g185` | `method-g185-irrigation-boundary` | `repo://scripts/python/export_g185_region_specific_irrigation_boundary.py` | `local://quality_reports/agent_runs/2026-06-24_g185_region_specific_irrigation_boundary/manifest.json` | `repo://docs/results/g185-region-irrigation-boundary/report.md` | verified_current |

### 相对前版与证据边界

- 综合变化：Estimated region-specific continuous irrigation triple interactions and support-aware margins
- 证据限制：Separate estimand from IE-DE-TE; HHH heat and hot-dry intervals cross zero while NE drought is supported

## `g185-old-method-unified-v1` — G185 old-method unified direction v1

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-07-14；`reference`；`reviewed_failure_record` |
| 父版/取代关系 | parent=`g185-old-method-corrected`；supersedes=`none` |
| 当前用途 | Reviewed failure evidence only; not a submission candidate；truth role=`reviewed_failure_stop_stability` |
| 证据 | `git-native`；关联脱敏对话 0 个 |

### 数据变化

沿用冻结G185虚拟样本46,299行、13,236 grids；五命名区44,556行、12,745 grids；输入哈希与双样本键哈希均登记

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `g185-old-method-unified-run-manifest-v2` | result-manifest | present | 未记录 | `local://temp/2026-07-15_g185_old_method_unified_full_stop_v2/run_manifest.json` |
| `g185-old-method-unified-full-manifest-v2` | audit-manifest | present | 未记录 | `local://temp/2026-07-15_g185_old_method_unified_full_stop_v2/full_manifest.json` |
| `g185-old-method-unified-public-stop-report` | public-result | present | 未记录 | `repo://docs/results/g185-old-method-unified-v1/report.md` |
| `g185-old-method-unified-package-review-round2` | review-record | present | 未记录 | `repo://quality_reports/plans/2026-07-15_g185_full_stop_v2_package_review_round2.md` |
| `g185-old-method-unified-public-review-round2` | review-record | present | 未记录 | `repo://quality_reports/plans/2026-07-15_g185_public_failure_report_review_round2_pass.md` |

本版本运行使用或定义的样本规则：

#### `sample-g185` — G185 frozen scale

- 谓词：`{"all":[{"column":"ggcp10_maize_frac","operator":">=","value":0.05},{"rule":"main_sample","active":1},{"rule":"zone_core","active":0},{"rule":"yield_domain","active":1},{"rule":"yield_jump","active":1},{"rule":"sm_sd","active":1},{"rule":"sm_coverage","active":0},{"rule":"sr_within","active":0},{"rule":"years_ge3","active":0},{"rule":"stable_province","active":0}]}`。
- 规则向量：`crop_mask=ggcp10>=0.05|main_sample=1|zone_core=0|yield_domain=1|yield_jump=1|sm_sd=1|sm_coverage=0|sr_within=0|years_ge3=0|stable_province=0`。
- 样本规模：rows=46299；grids=13236；区域计数=`{"HHH":{"rows":12213},"NE":{"rows":20794},"NW":{"rows":3414},"Other":{"rows":1743},"SH":{"rows":903},"SW":{"rows":7232}}`。
- 规则代码：`repo://scripts/python/expanded_scale_story_search.py`；代码 SHA-256=`cabb1a038b1efb3b6ce88fd4f81c9eb3e086372554f2d43d3ea886f9626bb712`。
- 状态：`current`；verified_at=`2026-07-14`；supersedes=`none`。

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `g185-old-method-unified-override-v1` | 2026-07-15 | `reference` | Continued the previously stopped G185 branch under the user-authorized nonblocking stability gate and assembled the historical national, continuous regional and five-zone algebraic evidence into one reviewed candidate |

### 方法变化

复现IE=(a1+a3s)b、DE=c1+c3s、TE=IE+DE，并新增grid FE+province-year FE、2度Rademacher/Webb 1,999次、Romano-Wolf、Holm及100/200/300 km HAC

#### `method-g185-old-method-unified-stop`

- Outcome / estimand：ln_yield_raw paired with gleam_smrz_mean_raw equation；Historical IE=(a1+a3s)b, DE=c1+c3s and TE=IE+DE plus province-year stability adjudication。
- Exposure / mediator：D_full_raw; hdd_ge32_raw; HotDryPr_full_raw; ca_raw interactions；Contemporaneous gleam_smrz_mean_raw algebraic component。
- Controls / FE：Companion hazards; precipitation; ET0; GDD; irrigation; aridity；Grid FE plus year FE historically; grid FE plus province-by-year FE for the added stability layer。
- Inference：Synchronous 2-degree spatial-block inference; 15-test Romano-Wolf stepdown; Holm and 100/200/300 km HAC checks；bootstrap=Grid Rademacher 999 and 2-degree Rademacher or Webb 1999；reps=1999；seed=42。
- 代码入口：`repo://scripts/python/run_g185_old_method_full.py`。
- 解释边界：FULL_STOP because NE drought same-direction nonlinear endpoint draws were 84.1921%, below the frozen 90% gate; components are not causal mediation。

### 结果呈现变化

发布包含全部15组区域结果的完整失败报告；东北干旱同向draw 84.1921%低于90%门槛，因此不生成投稿图或候选小稿

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-g185-old-method-unified-stop-v2-20260715` | `g185-virtual-sample\|ggcp10-baseline-suite\|data-v3-expanded-main-dta` | `sample-g185` | `method-g185-old-method-unified-stop` | `repo://scripts/python/run_g185_old_method_full.py` | `local://temp/2026-07-15_g185_old_method_unified_full_stop_v2/run_manifest.json\|local://temp/2026-07-15_g185_old_method_unified_full_stop_v2/full_manifest.json` | `repo://docs/results/g185-old-method-unified-v1/report.md` | verified_current |

### 相对前版与证据边界

- 综合变化：Unified the historical linear two-equation evidence and added province-by-year fixed effects, spatial-block inference and explicit stability adjudication
- 证据限制：PASS_FAILURE_PACKAGE does not lift FULL_STOP; the historical corrected result remains a context version rather than a successful descendant claim

## `regional-threshold-sr-v1` — Regional heterogeneous temperature threshold SR direction v1

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-07-14；`reference`；`reviewed_failure_record` |
| 父版/取代关系 | parent=`data-v3-main`；supersedes=`none` |
| 当前用途 | Reviewed failure evidence only; not a submission candidate；truth role=`reviewed_failure_stop_data_support` |
| 证据 | `git-native`；关联脱敏对话 0 个 |

### 数据变化

使用69,038行V3 Stata面板与官方0.5度maize.tif；五区pre-EDD complete-case为66,396行、21,337 grids；西南有效阈值覆盖12,637/18,094=69.8408%

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `regional-threshold-maize-raster` | raw-input | present | 未记录 | `external://zenodo/records/17142122/maize.tif` |
| `regional-threshold-grid-v1` | threshold-map | present | 22180×19 | `local://temp/2026-07-14_regional_threshold_stage1_audit_v5/threshold_grid.csv` |
| `regional-threshold-run-manifest-v5` | result-manifest | present | 未记录 | `local://temp/2026-07-14_regional_threshold_stage1_audit_v5/run_manifest.json` |
| `regional-threshold-audit-manifest-v5` | audit-manifest | present | 未记录 | `local://temp/2026-07-14_regional_threshold_stage1_audit_v5/audit_manifest.json` |
| `regional-threshold-public-stop-report` | public-result | present | 未记录 | `repo://docs/results/regional-threshold-sr-v1/report.md` |
| `regional-threshold-review-round3` | review-record | present | 未记录 | `repo://quality_reports/plans/2026-07-14_threshold_review_round3_pass.md` |

本版本运行使用或定义的样本规则：

#### `sample-regional-threshold-pre-edd` — Five-zone pre-EDD complete-case support sample

- 谓词：`{"all":[{"column":"zone","operator":"in","values":["NE","HHH","NW","SH","SW"]},{"columns":["ln_yield","ca","gdd_10_29","pr_sum","v3_doy","he_doy","ma_doy","gleam_smrz_mean"],"operator":"all_not_missing"}]}`。
- 规则向量：`named_zones=1|ln_yield=1|ca=1|gdd_10_29=1|pr_sum=1|v3_doy=1|he_doy=1|ma_doy=1|gleam_smrz_mean=1`。
- 样本规模：rows=66396；grids=21337；区域计数=`{"HHH":{"rows":13165,"grids":3844},"NE":{"rows":25041,"grids":7365},"NW":{"rows":5540,"grids":2228},"SH":{"rows":4556,"grids":1692},"SW":{"rows":18094,"grids":6208}}`。
- 规则代码：`repo://scripts/python/audit_regional_threshold_coverage.py`；代码 SHA-256=`f8c84ce75aa0e29a1f59bdebb7f74cec5914de05ada6d39f4521d8462448a481`。
- 状态：`historical`；verified_at=`2026-07-15`；supersedes=`none`。

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `regional-threshold-sr-override-v1` | 2026-07-15 | `reference` | Continued past the historical coverage gate without imputing thresholds, executed the frozen external-threshold daily exposure model and retained the independent Round 2 failure decision |

### 方法变化

仅执行原始PixelIsArea单元中心映射和确定性覆盖审计；未执行EDD、固定效应、bootstrap、物候窗口或产量模型

#### `method-regional-threshold-stage1`

- Outcome / estimand：No outcome model；Five-zone share of pre-EDD complete-case rows receiving an unmodified official continuous maize threshold。
- Exposure / mediator：Official 0.5-degree continuous maize threshold mapped to the containing PixelIsArea cell；GLEAM SMrz appears only in the frozen support predicate。
- Controls / FE：No regression controls; support denominator requires ln_yield, ca, GDD10-29, precipitation, phenology dates and GLEAM SMrz；None。
- Inference：Deterministic coverage counts and schema or semantic validation only；bootstrap=none；reps=0；seed=42。
- 代码入口：`repo://scripts/python/audit_regional_threshold_coverage.py`。
- 解释边界：STOP before EDD construction or yield estimation because SW coverage is below 80%; no SR effect may be inferred。

### 结果呈现变化

发布Stage 1失败报告、机器manifest和独立Round 3审查；报告完整五区覆盖及不得用插值解除STOP的边界

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-regional-threshold-stage1-v5-20260714` | `data-v3-expanded-main-dta\|regional-threshold-maize-raster` | `sample-regional-threshold-pre-edd` | `method-regional-threshold-stage1` | `repo://scripts/python/audit_regional_threshold_coverage.py` | `local://temp/2026-07-14_regional_threshold_stage1_audit_v5/run_manifest.json\|local://temp/2026-07-14_regional_threshold_stage1_audit_v5/audit_manifest.json` | `repo://docs/results/regional-threshold-sr-v1/report.md` | verified_current |

### 相对前版与证据边界

- 综合变化：Audited the official continuous maize heat-damage threshold before any yield model and stopped at the frozen five-zone coverage gate
- 证据限制：PASS_PUBLIC_STOP_REPORT 97/100; STOP_DATA_SUPPORT_GATE; no SR buffering coefficient exists

## `compound-event-intensity-duration-override-v1` — Compound-event intensity-duration SR override v1

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-07-15；`reference`；`analysis_release` |
| 父版/取代关系 | parent=`compound-event-intensity-duration-v1`；supersedes=`none` |
| 当前用途 | Historical internal candidate record with unresolved event-model Critical; not a current submission candidate；truth role=`historical_internal_candidate_under_event_structure_revision` |
| 证据 | `git-native`；关联脱敏对话 0 个 |

### 数据变化

使用V3五区61,918个grid-years、19,749个grids以及147,648行完整事件panel；同时保留扩展窗口、严格V3-MA窗口、重叠事件支持和恢复样本

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `compound-event-override-full-event-panel-v1` | event-panel | present | 147648×37 | `local://temp/2026-07-15_compound_event_override_stage1_v1/event_panel.csv.gz` |
| `compound-event-override-model-manifest-v3` | result-manifest | present | 未记录 | `local://temp/2026-07-15_compound_event_override_round1_revision_v3/run_manifest.json` |
| `compound-event-override-recovery-manifest-v2` | result-manifest | present | 未记录 | `local://temp/2026-07-15_compound_event_override_recovery_v2/run_manifest.json` |
| `compound-event-override-report-manifest-v3` | result-manifest | present | 未记录 | `local://temp/2026-07-15_compound_event_override_report_v3/report_run_manifest.json` |
| `compound-event-override-public-markdown` | public-result | present | 未记录 | `repo://docs/results/compound-event-intensity-duration-override-v1/report.md` |
| `compound-event-override-public-figures-html` | public-result | present | 未记录 | `repo://docs/results/compound-event-intensity-duration-override-v1/figures.html` |
| `compound-event-override-review-round2` | review-record | present | 未记录 | `repo://quality_reports/plans/2026-07-15_hotdry_event_override_method_review_round2.md` |

本版本运行使用或定义的样本规则：

#### `sample-compound-event-override-model-v1` — Compound-event override complete-case yield-model sample

- 谓词：`{"all":[{"column":"zone","operator":"in","values":["NE","HHH","NW","SH","SW"]},{"columns":["ln_yield","ca","total_duration","mean_intensity","gdd_10_29","pr_sum","province","year"],"operator":"all_not_missing"}]}`。
- 规则向量：`named_zones=1|event_metrics_zero_when_no_event=1|yield_ca_controls_fe_complete=1`。
- 样本规模：rows=61918；grids=19749；区域计数=`{"HHH":{"rows":13165,"grids":3844},"NE":{"rows":24876,"grids":7314},"NW":{"rows":5534,"grids":2226},"SH":{"rows":4556,"grids":1692},"SW":{"rows":13787,"grids":4673}}`。
- 规则代码：`repo://scripts/python/run_hotdry_event_override_models.py`；代码 SHA-256=`fdb05bb78aeab0ccff17e6534ae0166b3129171646bbf92aedae3a98f05eaeae`。
- 状态：`current`；verified_at=`2026-07-15`；supersedes=`none`。

### 方法变化

联合估计duration与mean intensity并保留分别模型；grid与province-year FE；2度同步Rademacher/Webb 1,999次、Romano-Wolf/Holm、100/200/300 km HAC、R/Stata复算，以及antecedent/drawdown和固定IPCW/RMST

#### `method-compound-event-override-v1`

- Outcome / estimand：ln_yield at grid-year level; separate event-level GLEAM SMrz drawdown and recovery outcomes；Joint duration and mean-intensity conditional yield-change contrast from zone P50 to P90 exposure at common-sample CA P25 versus P75; separate models and strict V3-MA window retained as checks。
- Exposure / mediator：Events require Tmax>=32C and precipitation<1 mm/day for at least three consecutive days; total duration and mean exceedance intensity enter the joint main model；Antecedent SMrz, drawdown with overlapping-event sensitivity and 30-day fixed-IPCW or RMST recovery; descriptive channel evidence only。
- Controls / FE：GDD10-29, seasonal precipitation and precipitation squared with zone, CA, exposure and required lower-order interactions；Grid FE and province-by-year FE。
- Inference：Synchronous 2-degree Rademacher and Webb inference with joint covariance; Romano-Wolf, Holm, 100/200/300 km HAC, strict-window checks and R or Stata replication；bootstrap=2-degree spatial-block Rademacher and Webb wild bootstrap；reps=1999；seed=42。
- 代码入口：`repo://scripts/python/run_hotdry_event_round1_revision.py`。
- 解释边界：Only the HHH duration conditional-change difference may be highlighted and its low-SR negative to high-SR positive transition must be disclosed; no nationwide buffering, causal effect, causal mediation, independently robust intensity result or confirmed SM recovery channel may be claimed。

### 结果呈现变化

保留2026-07-15内部候选小稿和自包含三图；2026-07-18增加主设计缺少事件指示变量的结构审计，明确现有结果是含无事件0值的季节聚合暴露关系；未重新估计模型

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-compound-event-override-round1-revision-v3-20260715` | `data-v3-expanded-main-dta\|compound-event-tmax-aligned-series\|compound-event-precip-aligned-series\|compound-event-smrz-aligned-series\|compound-event-override-full-event-panel-v1` | `sample-compound-event-override-model-v1` | `method-compound-event-override-v1` | `repo://scripts/python/run_hotdry_event_round1_revision.py` | `local://temp/2026-07-15_compound_event_override_report_v3/report_run_manifest.json` | `repo://docs/results/compound-event-intensity-duration-override-v1/report.md` | verified_current |

### 相对前版与证据边界

- 综合变化：Continued the stopped smoke branch to full five-zone event, yield and soil-moisture analyses and made the triggered joint duration-intensity model the reviewed main specification
- 证据限制：内部91分记录不再代表当前投稿就绪度；修正后的事件发生与严重程度两部分模型必须使用新canonical ID

## `compound-event-intensity-duration-v1` — Compound-event intensity-duration SR direction v1

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-07-15；`reference`；`reviewed_failure_record` |
| 父版/取代关系 | parent=`data-v3-main`；supersedes=`none` |
| 当前用途 | Reviewed failure evidence only; not a submission candidate；truth role=`reviewed_failure_stop_smoke_review` |
| 证据 | `git-native`；关联脱敏对话 0 个 |

### 数据变化

small smoke使用V3面板及2016-2019对齐Tmax、降水、GLEAM SMrz；仅40个grid-years和75条事件接口记录；全量五区支持审计未完成

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `compound-event-tmax-aligned-series` | raw-input | present | 未记录 | `external://daily-temp-cn/daily_temp_{year}.nc` |
| `compound-event-precip-aligned-series` | raw-input | present | 未记录 | `external://processed-panel-cn/pre-0.1deg/chm-pre-0.1deg-{year}.nc` |
| `compound-event-smrz-aligned-series` | raw-input | present | 未记录 | `external://processed-panel-cn/gleam-sm-0.1deg-tempgrid-{year}.nc` |
| `compound-event-smoke-panel-v2` | smoke-interface-output | present | 75×37 | `local://temp/2026-07-15_compound_event_interface_smoke_v2/event_panel.csv.gz` |
| `compound-event-input-inventory-v2` | input-manifest | present | 未记录 | `local://temp/2026-07-15_compound_event_interface_smoke_v2/input_inventory.json` |
| `compound-event-run-manifest-v2` | result-manifest | present | 未记录 | `local://temp/2026-07-15_compound_event_interface_smoke_v2/run_manifest.json` |
| `compound-event-extension-v2` | audit-manifest | present | 未记录 | `local://temp/2026-07-15_compound_event_interface_smoke_v2/event_run_extension.json` |
| `compound-event-public-stop-report` | public-result | present | 未记录 | `repo://docs/results/compound-event-intensity-duration-v1/report.md` |
| `compound-event-smoke-review-round2` | review-record | present | 未记录 | `repo://quality_reports/plans/2026-07-15_hotdry_event_smoke_review_round2_stop.md` |
| `compound-event-public-review` | review-record | present | 未记录 | `repo://quality_reports/plans/2026-07-15_hotdry_event_public_stop_review_pass.md` |

本版本运行使用或定义的样本规则：

#### `sample-compound-event-smoke-v2` — Compound-event deterministic small-smoke interface sample

- 谓词：`{"all":[{"column":"zone","operator":"in","values":["NE","HHH","NW","SH","SW"]},{"rule":"first two eligible grid-year rows within each zone-year after deterministic sort","active":1}]}`。
- 规则向量：`named_zones=1|first_two_per_zone_year=1|interface_only=1`。
- 样本规模：rows=40；grids=20；区域计数=`{"HHH":{"rows":8,"grids":3},"NE":{"rows":8,"grids":3},"NW":{"rows":8,"grids":5},"SH":{"rows":8,"grids":6},"SW":{"rows":8,"grids":3}}`。
- 规则代码：`repo://scripts/python/run_hotdry_event_stage1.py`；代码 SHA-256=`e8adb78193a1358901048155e45a336e6cecdbe7ba33df0db68a2d3786b00b93`。
- 状态：`historical`；verified_at=`2026-07-15`；supersedes=`none`。

直接子版本或组件：

| 子节点 | 日期 | 状态 | 相对变化摘要 |
|---|---|---|---|
| `compound-event-intensity-duration-override-v1` | 2026-07-15 | `reference` | Continued the stopped smoke branch to full five-zone event, yield and soil-moisture analyses and made the triggered joint duration-intensity model the reviewed main specification |

### 方法变化

事件定义固定为窗口内Tmax>=32C且降水<1 mm连续至少3天；仅测试事件、antecedent SM、drawdown和recovery接口；未估计FE、IPCW/RMST或产量模型

#### `method-compound-event-smoke-v2`

- Outcome / estimand：No outcome model in reviewed smoke; ln_yield was preregistered but not estimated；Deterministic event, antecedent SM, drawdown and recovery interface reproducibility only。
- Exposure / mediator：Tmax>=32C and precipitation<1 mm/day for at least three consecutive days within v3_doy-30 through ma_doy；GLEAM SMrz antecedent state, drawdown and recovery or censoring fields。
- Controls / FE：GDD10-29 and precipitation controls were preregistered but not used in smoke；Grid and province-by-year FE were preregistered but not estimated。
- Inference：No empirical inference; row, contract, hash and point-versus-bulk index checks only；bootstrap=none；reps=0；seed=42。
- 代码入口：`repo://scripts/python/run_hotdry_event_stage1.py`。
- 解释边界：STOP_AT_SMOKE_REVIEW after Round 2 retained an unregistered-test identity Major; full support, IPCW/RMST and yield models were not run。

### 结果呈现变化

发布两轮small-smoke审查失败报告；Round 2因第三个runner测试文件未锁定输入身份而STOP_AT_SMOKE_REVIEW

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-compound-event-interface-smoke-v2-20260715` | `data-v3-expanded-main-dta\|compound-event-tmax-aligned-series\|compound-event-precip-aligned-series\|compound-event-smrz-aligned-series` | `sample-compound-event-smoke-v2` | `method-compound-event-smoke-v2` | `repo://scripts/python/run_hotdry_event_stage1.py` | `local://temp/2026-07-15_compound_event_interface_smoke_v2/run_manifest.json\|local://temp/2026-07-15_compound_event_interface_smoke_v2/event_run_extension.json` | `repo://docs/results/compound-event-intensity-duration-v1/report.md` | verified_sensitivity |

### 相对前版与证据边界

- 综合变化：Designed the hot-dry event intensity-duration and soil-moisture timing interface, then stopped after the second small-smoke review retained a reproducibility Major
- 证据限制：Design review passed 92/100, but smoke review stopped at 89/100 after the frozen two-round limit; no support counts or empirical coefficients may be claimed

## `g185-old-method-unified-override-v1` — G185 old-method unified override v1

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-07-15；`reference`；`analysis_release` |
| 父版/取代关系 | parent=`g185-old-method-unified-v1`；supersedes=`none` |
| 当前用途 | Historical internal candidate record with unresolved external method Major; not a current submission candidate；truth role=`historical_internal_candidate_under_external_method_revision` |
| 证据 | `git-native`；关联脱敏对话 0 个 |

### 数据变化

沿用冻结G185规则的46,299行、13,236 grids及五命名区44,556行、12,745 grids；未改变G185规则、输入哈希或结果变量口径

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `g185-old-method-unified-override-manifest-v1` | result-manifest | present | 未记录 | `local://temp/2026-07-15_g185_old_method_unified_override_v1/override_manifest.json` |
| `g185-old-method-unified-override-public-markdown` | public-result | present | 未记录 | `repo://docs/results/g185-old-method-unified-override-v1/report.md` |
| `g185-old-method-unified-override-public-html` | public-result | present | 未记录 | `repo://docs/results/g185-old-method-unified-override-v1/report.html` |
| `g185-old-method-unified-override-review-round2` | review-record | present | 未记录 | `repo://quality_reports/plans/2026-07-15_g185_override_method_review_round2.md` |
| `g185-old-method-unified-override-html-final-review` | review-record | present | 未记录 | `repo://quality_reports/plans/2026-07-15_g185_override_selfcontained_html_final_review.md` |

本版本运行使用或定义的样本规则：

#### `sample-g185` — G185 frozen scale

- 谓词：`{"all":[{"column":"ggcp10_maize_frac","operator":">=","value":0.05},{"rule":"main_sample","active":1},{"rule":"zone_core","active":0},{"rule":"yield_domain","active":1},{"rule":"yield_jump","active":1},{"rule":"sm_sd","active":1},{"rule":"sm_coverage","active":0},{"rule":"sr_within","active":0},{"rule":"years_ge3","active":0},{"rule":"stable_province","active":0}]}`。
- 规则向量：`crop_mask=ggcp10>=0.05|main_sample=1|zone_core=0|yield_domain=1|yield_jump=1|sm_sd=1|sm_coverage=0|sr_within=0|years_ge3=0|stable_province=0`。
- 样本规模：rows=46299；grids=13236；区域计数=`{"HHH":{"rows":12213},"NE":{"rows":20794},"NW":{"rows":3414},"Other":{"rows":1743},"SH":{"rows":903},"SW":{"rows":7232}}`。
- 规则代码：`repo://scripts/python/expanded_scale_story_search.py`；代码 SHA-256=`cabb1a038b1efb3b6ce88fd4f81c9eb3e086372554f2d43d3ea886f9626bb712`。
- 状态：`current`；verified_at=`2026-07-14`；supersedes=`none`。

### 方法变化

复现IE=(a1+a3s)b、DE=c1+c3s、TE=IE+DE；报告grid/year与grid/province-year FE、2度空间块Rademacher/Webb 1,999次、Romano-Wolf/Holm及100/200/300 km HAC

#### `method-g185-old-method-unified-override`

- Outcome / estimand：ln_yield_raw paired with gleam_smrz_mean_raw equation；Historical IE=(a1+a3s)b, DE=c1+c3s and TE=IE+DE evaluated at fixed or regional stress endpoints and SR P25, P50 or P75。
- Exposure / mediator：D_full_raw; hdd_ge32_raw; HotDryPr_full_raw; ca_raw and stress-by-ca interactions；Contemporaneous gleam_smrz_mean_raw algebraic component only。
- Controls / FE：Companion hazards; precipitation; ET0; GDD; irrigation and aridity；Grid and year FE for historical estimator; grid and province-by-year FE for added robustness。
- Inference：Synchronous 2-degree spatial-block covariance for 15 zone-stress contrasts; Romano-Wolf stepdown, Holm and 100/200/300 km spatial HAC checks；bootstrap=2-degree Rademacher and Webb wild bootstrap；reps=1999；seed=42。
- 代码入口：`repo://scripts/python/export_g185_old_method_override.py`。
- 解释边界：IE, DE and TE are algebraic two-equation components rather than identified causal mediation; 84.1921% NE drought direction stability and all adverse or nonsignificant results remain disclosed; do not claim uniquely optimal G185 or robust buffering。

### 结果呈现变化

保留2026-07-15内部候选小稿和自包含HTML；2026-07-18增加外部方法审阅提示、低高SR端点分类和强固定效应解释边界；未重新估计模型

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-g185-old-method-unified-override-20260715` | `g185-old-method-unified-full-manifest-v2\|g185-virtual-sample\|ggcp10-baseline-suite\|data-v3-expanded-main-dta` | `sample-g185` | `method-g185-old-method-unified-override` | `repo://scripts/python/export_g185_old_method_override.py` | `local://temp/2026-07-15_g185_old_method_unified_override_v1/override_manifest.json` | `repo://docs/results/g185-old-method-unified-override-v1/report.html` | verified_current |

### 相对前版与证据边界

- 综合变化：Continued the previously stopped G185 branch under the user-authorized nonblocking stability gate and assembled the historical national, continuous regional and five-zone algebraic evidence into one reviewed candidate
- 证据限制：内部92分记录不再代表当前投稿就绪度；全国结果必须同时报告P25和P75端点，IE、DE和TE仅为两方程代数组件

## `regional-threshold-sr-override-v1` — Regional heterogeneous temperature threshold SR override v1

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-07-15；`reference`；`reviewed_failure_record` |
| 父版/取代关系 | parent=`regional-threshold-sr-v1`；supersedes=`none` |
| 当前用途 | Reviewed failure evidence only; not a submission candidate；truth role=`reviewed_failure_not_candidate_external_threshold` |
| 证据 | `git-native`；关联脱敏对话 0 个 |

### 数据变化

使用V3主面板、官方连续maize.tif、2016-2019对齐Tmax与SMrz及实际物候NetCDF；阈值有效58,464行，最终模型54,890行、17,450 grids；未插值、外推或回填固定阈值

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `regional-threshold-override-phenology-netcdf` | raw-input | present | 未记录 | `external://maize-phenology-ca-0.1deg-v2/maizephenology-ca-ratio-2016-2019-0p1deg.nc` |
| `regional-threshold-override-exposure-panel-v2` | exposure-panel | present | 175392×22 | `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/daily_exposure_panel.parquet` |
| `regional-threshold-override-run-manifest-v2` | result-manifest | present | 未记录 | `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/run_manifest.json` |
| `regional-threshold-override-post-validation-v2` | audit-manifest | present | 未记录 | `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/round1_post_validation_manifest.json` |
| `regional-threshold-override-public-failure-report` | public-result | present | 未记录 | `repo://docs/results/regional-threshold-sr-override-v1/report.md` |
| `regional-threshold-override-review-round2` | review-record | present | 未记录 | `repo://quality_reports/plans/2026-07-15_regional_threshold_override_method_review_round2.md` |
| `regional-threshold-override-public-final-review` | review-record | present | 未记录 | `repo://quality_reports/plans/2026-07-15_regional_threshold_override_failure_public_final_review.md` |

本版本运行使用或定义的样本规则：

#### `sample-regional-threshold-override-model-v2` — Regional-threshold override final yield-model sample

- 谓词：`{"all":[{"column":"zone","operator":"in","values":["NE","HHH","NW","SH","SW"]},{"column":"external_threshold_valid","operator":"==","value":1},{"columns":["ln_yield","ca","gdd_10_29","pr_sum","province","year","daily_tmax_window"],"operator":"all_not_missing"}]}`。
- 规则向量：`named_zones=1|external_threshold_valid=1|daily_tmax_window_valid=1|yield_ca_controls_fe_complete=1`。
- 样本规模：rows=54890；grids=17450；区域计数=`{"HHH":{"rows":12922,"grids":3775},"NE":{"rows":23719,"grids":6966},"NW":{"rows":4681,"grids":1849},"SH":{"rows":4501,"grids":1668},"SW":{"rows":9067,"grids":3192}}`。
- 规则代码：`repo://scripts/python/run_regional_threshold_daily_override.py`；代码 SHA-256=`10b44b0242dc6397d1bcff37ef5a55396d250f0dc845fcab26c9e656db0e01fb`。
- 状态：`reference`；verified_at=`2026-07-15`；supersedes=`none`。

### 方法变化

构造外生连续阈值EDD并估计五区完全交互、共同CA P25/P75、全季及V3-HE和HE-MA窗口；grid与province-year FE；2度空间块wild bootstrap 1,999次及空间HAC复核

#### `method-regional-threshold-override-v2`

- Outcome / estimand：ln_yield; separate GLEAM SMrz state and channel outcomes；Five-zone conditional yield-change difference when external-threshold EDD moves from zone P50 to P90 and CA moves from common-sample P25 to P75。
- Exposure / mediator：Continuous external-threshold EDD for full growing season, V3-HE and HE-MA with zone, CA and all required lower-order interactions；GLEAM SMrz antecedent day -14 to -1, within-window mean or minimum and change from antecedent; not entered as a causal mediator in the main yield equation。
- Controls / FE：Fixed GDD10-29, seasonal precipitation and precipitation squared plus frozen lower-order terms；Grid FE and province-by-year FE。
- Inference：Synchronous 2-degree spatial-block wild inference across zones and windows; Romano-Wolf stepdown, Holm, grid-cluster comparison and spatial HAC；bootstrap=2-degree Rademacher wild bootstrap；reps=1999；seed=42。
- 代码入口：`repo://scripts/python/run_regional_threshold_daily_override.py`。
- 解释边界：Final reviewed result does not support a buffering manuscript; SM lacks primary spatial joint inference and phenology joint Wald or boundary sensitivity remains incomplete; no interpolation, best-threshold search, best-window search or Round 3 is authorized。

### 结果呈现变化

发布完整失败报告及全部五区、SM和物候边界；Round 2为72/100、0 Critical、3 Major、4 Minor；公共失败报告最终核验PASS只确认披露准确

关联运行与结果载体：

| Run | 输入 artifact | 样本规则 | 方法 | 入口 | 结果 manifest | 公开结果 | 可复现状态 |
|---|---|---|---|---|---|---|---|
| `run-regional-threshold-override-full-v2-20260715` | `data-v3-expanded-main\|regional-threshold-maize-raster\|regional-threshold-override-phenology-netcdf\|compound-event-tmax-aligned-series\|compound-event-smrz-aligned-series` | `sample-regional-threshold-override-model-v2` | `method-regional-threshold-override-v2` | `repo://scripts/python/run_regional_threshold_daily_override.py` | `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/run_manifest.json\|local://temp/2026-07-15_regional_threshold_daily_override_full_v2/round1_post_validation_manifest.json` | `repo://docs/results/regional-threshold-sr-override-v1/report.md` | verified_sensitivity |

### 相对前版与证据边界

- 综合变化：Continued past the historical coverage gate without imputing thresholds, executed the frozen external-threshold daily exposure model and retained the independent Round 2 failure decision
- 证据限制：FAIL/REVIEWED_NOT_CANDIDATE；公共报告PASS不改变失败状态，不授权Round 3或更有利的阈值、窗口、样本与函数形式搜索

## `report-sr-method-portfolio-web-reader-v1` — SR method portfolio GPT web reader v1

| 项目 | 内容 |
|---|---|
| 时间与状态 | 2026-07-17；`umbrella`；`public_report_umbrella` |
| 父版/取代关系 | parent=`none`；supersedes=`none` |
| 当前用途 | Public web-reader and review entry; it does not produce a new empirical estimate；truth role=`public_web_reader_portfolio_index` |
| 证据 | `git-native`；关联脱敏对话 0 个 |

### 数据变化

未改变数据、样本、变量口径或任何本地机器资产；仅发布脱敏Markdown摘要

关联 artifact：

| Artifact | 角色 | 状态 | 规模 | 路径或逻辑 URI |
|---|---|---|---|---|
| `report-sr-method-portfolio-web-reader-v1-public-report` | public-result | present | 未记录 | `repo://docs/results/report-sr-method-portfolio-web-reader-v1/report.md` |
| `report-sr-method-portfolio-web-reader-v1-gpt-prompt` | review-prompt | present | 未记录 | `repo://docs/results/report-sr-method-portfolio-web-reader-v1/GPT_WEB_PROMPT.md` |
| `report-sr-method-portfolio-web-reader-v1-portfolio-status` | public-result | present | 未记录 | `repo://docs/results/report-sr-method-portfolio-web-reader-v1/portfolio/portfolio_status.md` |
| `report-sr-method-portfolio-web-reader-v1-g185-endpoints` | public-result | present | 未记录 | `repo://docs/results/report-sr-method-portfolio-web-reader-v1/portfolio/g185_endpoint_slopes.md` |
| `report-sr-method-portfolio-web-reader-v1-external-review` | review-record | present | 未记录 | `repo://docs/results/report-sr-method-portfolio-web-reader-v1/review/external_review_synthesis.md` |
| `report-sr-method-portfolio-web-reader-v1-event-audit` | review-record | present | 未记录 | `repo://docs/results/report-sr-method-portfolio-web-reader-v1/methods/event_model_structure_audit.md` |
| `report-sr-method-portfolio-web-reader-v1-literature-readme` | literature-index | present | 未记录 | `repo://docs/results/report-sr-method-portfolio-web-reader-v1/literature/README.md` |
| `report-sr-method-portfolio-web-reader-v1-literature-ranked` | literature-index | present | 未记录 | `repo://docs/results/report-sr-method-portfolio-web-reader-v1/literature/final_ranked_literature.md` |

### 方法变化

未改变estimand、模型、固定效应、推断或数值；仅汇总既有结果和后续方法审阅边界

### 结果呈现变化

新增GitHub网页端阅读顺序、G185端点表、事件模型结构审计、37篇文献公开索引和可直接提交网页端的任务说明

### 相对前版与证据边界

- 综合变化：Published a GitHub-native reading entry for the three empirical directions, the 37-paper method inventory and the later external-review corrections
- 证据限制：This umbrella does not restore the threshold direction as a candidate and does not convert internal candidate scores into current submission readiness
