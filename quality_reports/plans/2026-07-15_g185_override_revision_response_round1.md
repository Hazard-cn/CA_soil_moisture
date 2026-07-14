# G185 override draft：Round 1审查回应

- 审查来源：`quality_reports/plans/2026-07-15_g185_override_method_review_round1.md`
- 修订对象：`quality_reports/plans/2026-07-15_g185_old_method_unified_override_draft_v1.md`
- 修订状态：`ROUND1_REVISED_ROUND2_REVIEW_PENDING`
- 数值边界：未修改机器估计、随机权重、样本、历史STOP、override manifest或公共谱系

## Major 1：对数尺度恒等式与百分比端点非可加性

**审查项。** 原稿没有区分对数斜率组件、固定SR百分比组件水平和P75−P25百分比端点，并错误写成“P75与P25柱高之差经指数转换后对应端点”；`3.47e-18`的尺度也未说明。

**修订。** 已在draft“第三节：模型、估计量与推断”分别定义`IE_log(s)`、`DE_log(s)`、`TE_log(s)`，明确`TE_log=IE_log+DE_log`只在对数斜率/线性预测尺度成立；进一步定义`δ_IE=a3×b×IQR(SR)`、`δ_DE=c3×IQR(SR)`和各自的`100{exp(δ_jx)-1}`百分比端点，明确一般有`Δ_TE_pct≠Δ_IE_pct+Δ_DE_pct`。原错误图1转换句已经删除，并明确固定SR柱高与P75−P25端点是不同estimand。摘要、全国结果、图1、图3和结论均增加“分别转换、非严格可加、不得解释为份额”的约束。draft“第七节”已把`3.47e-18`限定为对数斜率恒等式误差，并明确它不是百分比端点加法误差。全国结果另给出干旱示例：IE+DE为0.576706%，TE为0.576838%。

**修改位置。** draft第12、58—70、88—90、110—112、150及160行附近。

## Major 2：模型RHS、SM构念、推断身份及复现入口

**审查项。** 原稿缺少完整两方程RHS、SM单位与窗口、共同控制、联合complete-case、bootstrap/2°块定义；同时误把派生导出脚本称为模型复现入口。

**修订。** draft第三节新增两条回归方程和三胁迫完整RHS表，明确`M=gleam_smrz_mean_raw`、单位m³/m³、窗口`v3_doy-30`至`ma_doy`、共同控制`Z=(pr_sum_raw, et0_sum_raw, gdd_10_30_raw, irr_frac_raw, aridity_raw)`，以及每个区域—胁迫两方程使用同一联合complete-case。推断部分补充：全国13,236个grid的999次同步Rademacher、2°块全球原点公式、全国151块与命名区149个非零块、Rademacher/Webb各1,999次、seed 42、同步权重、percentile区间、Bartlett Conley核和100/200/300 km固定带宽，以及Romano–Wolf检验的是单位SR—胁迫对数斜率而非百分比端点。

draft第七节现将`scripts/python/run_g185_old_method_full.py`和`scripts/python/g185_old_method_core.py`标为模型重估入口，并列出所需参数、冻结重复次数和不可覆盖输出边界；`scripts/python/export_g185_old_method_override.py`明确标为来源20项哈希验证及六表三图派生入口，并列出其三个参数和来源manifest完整SHA-256。

**修改位置。** draft第38—76及154—156行附近。

## Minor 1：图1没有组件水平区间

**审查项。** 图1的27个组件水平没有误差棒，正文端点区间不能被当成柱高区间。

**修订。** 保留已经锁定哈希的图1，不重绘机器图；图注明确写明图中不显示27个组件水平各自区间，正文表报告的是不同estimand，即P75相对P25端点区间，不能替代柱高区间。该处理避免把两类不确定性混写。

**修改位置。** draft图1图注，第90行附近。

## Minor 2：图2/图3推断身份和低块数标识

**审查项。** 图2、图3脱离正文时不能辨认FE、统一权重和HHH/SH低块数限制。

**修订。** 图2图注增加历史grid+year FE、全国统一999次grid Rademacher、seed 42、非历史独立区域seed以及非线性响应面禁读说明。图3图注增加相同FE/权重身份、百分比非可加说明，并直接标出HHH为25个2°块、SH为13块且SH空间块结果仅作描述。

**修改位置。** draft图2和图3图注，第96及112行附近。

## Minor 3：完整15项多重检验未进入稿件

**审查项。** 原稿正文只点名HHH高温和SH高温，可能造成选择性阅读。

**修订。** draft第六节新增“完整15项主要多重检验”，逐行列出province×year加2°Rademacher层五区×三胁迫的`p_raw/p_RW/p_Holm`。同时提供补充机器表`table5_complete_region_joint_tests.csv`链接，该表保留历史grid wild、province×year Rademacher和Webb三个推断层的全部45行。

**修改位置。** draft第124—146行附近。

## Minor 4：全国高温IE下界舍入

**审查项。** 三位小数将高温IE区间正下界0.000186%显示为0.000%。

**修订。** 全国表统一提高至四位小数，高温IE显示为`0.0374 [0.0002, 0.0771]`；正文同时登记实值0.000186%，明确其不是零。

**修改位置。** draft全国表及其后说明，第83—88行附近。

## 修订后验证

Round 1只修改稿件与本回应文件；六张派生机器表、三幅PNG、来源FULL_STOP、override manifest及导出README均保持原字节。复核结果为：新增导出2项unittest全部通过；既有G185数值核心14项unittest全部通过；Python语法检查通过；来源20/20输出哈希和override 12/12输出哈希全部匹配；正文全国9项端点、五区15项province×year TE和15项主要多重检验共39行与机器表逐值一致；三幅图哈希均与override manifest一致；Markdown差异检查无错误。修订后draft SHA-256为`c7cb977eac3a808033c653a2cf1ecd1a6e1593152c198e6a8158ddcfc733affa`。
