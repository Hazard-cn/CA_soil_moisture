# G185旧方法统一override稿独立方法与结果复审（Round 2）

## 复审结论

**判定：`PASS_ROUND2`，90/100。** 原Round 1的2项Major均已实质关闭；4项Minor中2项关闭，2项因详细说明仅写入Markdown图片alt文本而部分关闭并合并为一类可见caption问题，另发现1项不阻断的符号记法Minor。本轮无Critical、无Major，达到固定90分门槛，因此不触发“两轮后仍有Critical/Major即最终失败”的规则。该PASS表示修订稿可以进入下一候选门槛，不等于95分投稿完成状态，也不改变来源FULL_STOP、用户override边界或东北干旱84.1921%的事实。

本轮只读审查：

- `quality_reports/plans/2026-07-15_g185_override_method_review_round1.md`
- `quality_reports/plans/2026-07-15_g185_override_revision_response_round1.md`
- `quality_reports/plans/2026-07-15_g185_old_method_unified_override_draft_v1.md`
- `temp/2026-07-15_g185_old_method_unified_override_v1/`
- 来源机器包 `local://temp/2026-07-15_g185_old_method_unified_full_stop_v2/`（来自历史隔离worktree）

除本报告外，没有修改draft、代码、机器包、历史STOP或公共谱系。

## Round 1问题关闭矩阵

| Round 1问题 | 作者回应 | 独立核验 | 状态 |
|---|---|---|---|
| Major 1：对数斜率可加性与百分比端点非可加性混写 | 新增三尺度定义并删除错误转换句 | draft第58—70、88、110、150和160行已实际修改；数值例证与机器表一致 | **CLOSED** |
| Major 2：完整RHS、SM构念、推断身份和复现入口不足 | 新增方程/RHS/窗口/推断，并区分重估与导出入口 | draft第38—76、154—156行与冻结设计、代码CLI及Git blob身份一致 | **CLOSED** |
| Minor 1：图1无组件水平区间 | 选择保留锁定图并披露不显示区间 | 披露内容正确，但只存在于图片alt文本，标准Markdown渲染时不作为可见图注 | **PARTIAL；残余Minor** |
| Minor 2：图2/图3推断身份和低块数图注不足 | 在三个图片alt文本中补充FE、权重、seed及块数 | 正文邻近段落已覆盖大部分信息；HHH 25块/SH 13块的完整图注仍只在alt文本 | **PARTIAL；残余Minor** |
| Minor 3：15项多重检验未进入稿件 | 新增15行Rademacher主检验表并链接45行机器表 | 15行 `p_raw/p_RW/p_Holm` 与机器表逐行零误差 | **CLOSED** |
| Minor 4：高温IE下界被三位小数舍入为0.000 | 表格提高至四位并登记实值 | 0.000186%显示为0.0002%，与机器表一致 | **CLOSED** |

## Major 1关闭核验：estimand尺度

修订稿现在明确区分：

1. `IE_log(s)=(a1+a3s)b`、`DE_log(s)=c1+c3s`和`TE_log(s)=IE_log(s)+DE_log(s)`，可加性只属于 `ln(yield)` 对胁迫的斜率/线性预测尺度；
2. P75相对P25的对数斜率差 `delta_IE=a3*b*q`、`delta_DE=c3*q`和`delta_TE=delta_IE+delta_DE`；
3. 分别指数转换的百分比端点 `100{exp(delta_j*x)-1}`，并明确一般不满足百分比尺度加法。

全国干旱机器值独立复算为 `IE_pct+DE_pct=0.5767064177%`、`TE_pct=0.5768382689%`，稿件报告0.576706%和0.576838%，正确。原稿“P75与P25柱高之差经指数转换后对应端点”的错误句已经删除；draft第70行正确写明固定SR柱高不能通过相减恢复P75−P25端点。`3.47e-18`在第150行明确限定为对数斜率恒等式误差，并说明不是百分比端点加法误差。摘要、全国结果、图3邻近正文和结论均禁止把IE解释为TE份额。

因此，Round 1 Major 1已关闭，没有残余的中介份额或百分比可加性错误。

## Major 2关闭核验：模型、SM、推断与复现身份

### 模型与SM构念

draft第38—56行已经给出两条完整方程和三类胁迫RHS表。独立对照冻结设计确认：

- `M=gleam_smrz_mean_raw`，单位m3/m3，窗口 `v3_doy-30` 至 `ma_doy`；
- 共同控制向量为 `pr_sum_raw, et0_sum_raw, gdd_10_30_raw, irr_frac_raw, aridity_raw`；
- 干旱、高温和热干的附加胁迫控制与冻结设计逐项一致；
- 产量方程只在对应SM方程RHS上增加同期M；
- 每个全国或区域—胁迫模型对两方程结果和全部RHS实施同一联合complete-case。

第76行继续明确M与胁迫和产量同期、可能位于胁迫之后；IE/DE/TE只作为同期代数组件。旧1.50%、3.27%和2.56%仍只标为DE，未重新混写为TE。

### 推断身份

draft第72—74行已经登记历史grid Rademacher 999次、空间块Rademacher/Webb各1,999次、seed 42、全球原点2°块公式、151个全国块/149个命名区非零块、区域同步权重、percentile区间、Bartlett核、100/200/300 km和Romano–Wolf/Holm检验对象。内容与冻结设计和来源manifest一致。

### 重估与派生入口

draft第154—156行已把模型重估入口和派生图表导出入口分开。当前Git `HEAD`中的两个模型代码blob SHA-256分别为：

- `scripts/python/run_g185_old_method_full.py`：`d7dc1d472fd52e5712d17e3391c1eed67891050d9e9319d44655e95a7fdee7f3`
- `scripts/python/g185_old_method_core.py`：`1e4dc830e25771670f10e4328c7e7025c009aaeaf909dcd5367af42790575f83`

二者与来源 `full_manifest.execution_file_hashes` 完全一致。Windows工作树可因CRLF checkout呈现不同的文件字节哈希，本轮使用Git blob字节复核，排除了把换行差异误判为代码变更。CLI独立检查确认五个路径参数为必需项；两类FE、两类score cluster、2°、999/1,999次和seed 42均由 `validate_cli()`强制冻结。`export_g185_old_method_override.py`则明确只验证来源20项哈希并生成六表三图，draft没有再称其为模型重估入口。

因此，Round 1 Major 2已关闭。

## 数值、哈希、图和测试复核

### 哈希与运行身份

- 修订稿实算SHA-256为 `c7cb977eac3a808033c653a2cf1ecd1a6e1593152c198e6a8158ddcfc733affa`，与修订回应登记值一致。
- 来源 `full_manifest.json` 实算SHA-256仍为 `3a23e22b421f052a4afc5f83c6aa806dd5a8f081bdb83aded357b2af6ca8aaec`；20项来源输出为20/20匹配。
- override manifest登记的12项派生输出为12/12匹配，没有因文稿修订而重写机器表或PNG。
- `python -m unittest tests.test_export_g185_old_method_override tests.test_g185_old_method_core -v` 共16项全部通过，包括来源身份、冻结CLI、代数恒等式、Romano–Wolf/Holm接口、Conley有序对/对角项、非覆盖输出和完整STOP包验证。

### 数值表

- 全国9项端点的四位小数、区间和高温IE下界与 `table2_national_iede_endpoints.csv` 一致。
- 五区15项province×year TE及区间继续与 `table3_five_zone_iede_both_fe.csv` 一致。
- 新增15项主多重检验与 `table5_complete_region_joint_tests.csv` 中 `grid_provyear_block_rademacher_1999` 层逐行比较，45个p值的最大绝对误差为0。
- 核心空间推断、同向比例、omnibus和HAC数值没有改动；NE干旱仍为1683/1999，即84.1921%，并继续明确不是方法学通过。SH仍为903行、284个grids和13个2°块，只作低块数描述。

### 三幅图

三图均保持3600×1500像素、299.9994 DPI、RGBA模式，实算哈希与override manifest一致。图1数据仍为27个历史组件水平；图2三条曲线及带状区间仍使用统一999次grid权重；图3仍为历史层5区×3胁迫×3组件共45行及统一999次grid权重区间。未发现重绘后换用更有利区间、删除负结果或改变随机序列。

## 结果完整性与语言边界

- 修订稿保留全部15项province×year TE、15项Rademacher主检验及45行三层机器表链接，没有只保留显著组合。
- HHH高温的percentile端点区间未跨零，但Romano–Wolf值0.1950；稿件仍将二者区分。SH高温 `p_RW=0.0005` 与13块局限同时报告，没有让其单独承担全国或五区主结论。
- 标题、摘要和结论仍使用“相关”“有限表述”“精度不足”，没有使用causal effect、identified mediation或robust buffering。
- G185选择历史、G057综合排序更高、四年面板限制、同期SM时序、未观测管理混杂和低块数均保留。未发现因Round 1修订而改变样本、估计量、固定效应、空间带宽、随机权重或公开主张。
- 引用列表和正文文献主张未改变；Round 1已完成37篇索引、Crossref和出版社/PubMed三层核验。本轮未发现修订引入新的未核实来源或错误作者信息。

## 残余Minor

### Minor A：图片详细说明位于alt文本，不是可见caption

draft第90、96和112行的三个Markdown图片链接把长说明全部放在 `![...](...)` 的alt字段。标准CommonMark/GitHub渲染在图片正常加载时不会把alt字段显示为图下注释，因此“图1不显示组件水平区间”、图2的seed和图3的HHH/SH块数不能依赖这些文字作为可见caption。正文邻近段落已覆盖核心解释，故不构成Major；进入公开稿时应在第90、96和112行各图片之后另写可见说明段落，或在HTML稿中使用 `figcaption`。

### Minor B：`delta`符号同时用于IQR差与单位SR斜率

draft第64行的 `delta_IE/delta_DE/delta_TE`包含SR IQR `q`，而第74行又以 `delta_rk=a3*b+c3`表示不含q的单位SR—胁迫斜率检验量。文字已经区分两者，计算没有错误，但同符号复用容易使读者误认为Romano–Wolf检验的是区域百分比端点。应在第74行把单位斜率改记为 `theta_rk`，或在第64行把IQR差改记为 `Delta_log`，并同步修改第126行的检验对象说明。

## 固定六维评分

| 维度 | 得分 | Round 2依据 |
|---|---:|---|
| 创新与期刊匹配 | 16/20 | 仍是既有G185旧估计量的统一组织与推断核验，适合综合性期刊但方法增量有限。 |
| 数据和五区支持 | 19/20 | 全国与五区样本、双哈希和15组合完整；SH 13块等支持限制被如实保留。 |
| estimand与识别边界 | 19/20 | 对数尺度、IQR差和百分比端点已正确分开，因果/中介边界清楚；仅余符号复用Minor。 |
| SM构念及时序 | 15/15 | SM变量、单位、窗口、RHS、联合complete-case和同期时序均明确。 |
| 精度与稳定性 | 12/15 | 推断层完整且不选择性报告；NE 84.19%、SH 13块和多数空间区间跨零仍限制精度。 |
| 可复现性和图表完整性 | 9/10 | 模型重估与派生入口、Git blob身份、机器表和图哈希均可复核；可见caption仍需整理。 |
| **合计** | **90/100** | 不按显著性加分；满足本阶段PASS下限，未达到95分投稿完成门槛。 |

## 最终门槛判定

本轮没有Critical或Major，原两项Major均由正文、代码身份和机器结果独立证据关闭，故判定 `PASS_ROUND2`。残余两类Minor分别是合并后的可见caption问题和符号清晰度问题，不授权改变模型或结果；应在从计划稿转入公开Markdown/HTML稿时修正。若后续稿件引入新数值、重绘图、改变estimand或更新公开主张，必须建立新的审查轮次，不能沿用本PASS。
