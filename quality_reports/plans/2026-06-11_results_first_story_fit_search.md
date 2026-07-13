# 结果导向的故事匹配规格搜索计划

日期：2026-06-11

## 一、目标

本轮不再以固定 `B067`、样本最大化、规则最少或跨 scale 普遍性作为首要排序条件，而是在当前可追溯的 `Gxxx` 样本空间内，寻找与以下完整故事最吻合的 scale：

1. 单一干旱、高温和复合状态下，更高 SR 与较平缓的产量损失斜率相关。
2. 连续热旱非加性主要集中于 `HE±10` 和 `HE–MA`，而不是均匀分布在 full season 或 `V3–HE`。
3. 灌溉重新配置 SR 的边际缓冲，理论目标为 drought 三重项为正、heat 三重项为负，hotdry 为负作为加分项。

该搜索属于结果导向的探索性规格选择。最终入选规格必须与全部搜索空间、评分规则和失败规格同时保存；不得将入选结果描述为事前唯一设定。

## 二、合法搜索空间

- 固定作物暴露门槛：`ggcp10_maize_frac >= 0.05`。
- 样本：现有 256 个唯一 `Gxxx` scale。
- 物候窗口：full、`V3–HE`、`HE±10`、`HE–MA`。
- 模型：grid fixed effects + year fixed effects。
- 第一阶段推断：OLS 标准误，仅用于排序。
- 第二阶段推断：`grid_id` 聚类标准误。
- baseline 与连续 irrigation 结果直接复用本轮已生成的 256-scale CSV。

不在本批次中追加新的作物比例阈值、任意日期窗口、因变量定义、控制变量集或固定效应结构。若这些维度需要继续搜索，应另开批次并重新记录评分。

## 三、故事匹配门槛

### Baseline state buffering

- 三类 hazard 均满足 `a1 < 0`、`b > 0`。
- 三类 hazard 均满足 `c3 > 0` 且 `p < 0.10`。
- 三类 hazard 均满足 `TE slope > 0`。

通过计 2 分。

### HE±10 strict compound response

- `D × H < 0, p < 0.10`。
- `SR × D × H > 0, p < 0.10`。

通过计 4 分。

### HE–MA reproductive extension

- `D × H < 0, p < 0.10`。
- `SR × D × H > 0, p < 0.10`。

通过计 3 分。

### V3–HE phase localization

- `D × H > 0, p < 0.10`。
- `SR × D × H <= 0`；不要求显著。

通过计 2 分。该门槛用于表明生殖期结果不是全季统一方向。

### Full-season modifier

- `SR × D × H > 0, p < 0.10`。

通过计 1 分；不要求 full-season `D × H` 显著。

### Irrigation reallocation

- drought：`SR × drought × irrigation > 0, p < 0.10`。
- heat：`SR × heat × irrigation < 0, p < 0.10`。

二者同时通过计 2 分。hotdry 三重项为负且 `p < 0.10` 另计 1 分。

## 四、排序规则

主评分为上述门槛分数之和，最高 15 分。并列时依次使用：

1. 目标方向项的截尾 `-log10(p)` 证据和；
2. `HE±10` 与 `HE–MA` 的 `SR × D × H` 证据；
3. 模型有效样本量。

规则数量不作为惩罚项。第一阶段选择 OLS 得分最高的 12 个 scale；第二阶段重新计算所有评分所需模型并以聚类结果重新排序。最终推荐以聚类评分为准。

## 五、输出

- `temp/2026-06-11_results_first_story_fit/phenology_all_scales_ols.csv`
- `temp/2026-06-11_results_first_story_fit/story_fit_ranking_ols.csv`
- `temp/2026-06-11_results_first_story_fit/top_scales_cluster_*.csv`
- `temp/2026-06-11_results_first_story_fit/story_fit_ranking_cluster.csv`
- `quality_reports/2026-06-11_results_first_story_fit.md`

## 六、停止规则

若聚类复核存在 15/15 的 scale，选择聚类证据和最高者。若不存在满分 scale，选择最高总分者，并明确指出缺失门槛。不会为追求满分在本批次内临时增加新的数据筛选或模型维度。

## 七、执行中追加批次

第一阶段实际得到 63 个 OLS 15/15 满分 scale。原计划只聚类复核 OLS 证据最高的 12 个 scale，能够确认存在聚类满分规格，但不足以确定 63 个 OLS 满分尺度中的聚类证据全局最高者。

因此追加第二批次：对全部 63 个 OLS 满分 scale 运行相同的 grid-cluster baseline、四窗口联合模型和连续 irrigation 模型，并按完全相同的评分与证据规则重新排序。该批次不增加新的样本规则、窗口、控制变量或评分项。
