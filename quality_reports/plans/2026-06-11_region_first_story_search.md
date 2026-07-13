# 区域优先的故事匹配规格搜索计划

日期：2026-06-11

## 一、目标调整

本轮替代上一轮“物候期优先”的评分。新的主故事是：

> SR 的条件缓冲并非在各区域复制同一模式，而是随主要气候胁迫和水分管理背景发生区域性重新配置：NE 更突出 drought，HHH 更突出 heat/hotdry，NW 更突出 drought/hotdry，SW 和 SH 更突出 heat/hotdry；物候期集中性只作为后续加强证据。

区域差异是第一排序维度，全国共同缓冲与灌溉结构是第二维度，物候期为第三维度。不得使用物候结果弥补区域得分不足。

## 二、固定搜索空间

- 固定作物暴露门槛：`ggcp10_maize_frac >= 0.05`。
- 样本：256 个现有 `Gxxx` scale。
- 区域：`maize_zone` 的 NE、HHH、NW、SW、SH；`Other` 不进入主评分。
- 主模型：full-season baseline 两方程，grid fixed effects + year fixed effects。
- 第一阶段：全部 scale 使用 OLS 标准误扫描。
- 第二阶段：区域得分最高的候选使用 `grid_id` 聚类标准误复核。
- 全国 baseline、连续 irrigation 和物候结果复用既有全量 CSV。

## 三、区域主评分

所有区域-hazard 的可比指标定义为：

`scaled_buffer = c3 × [SR(P75)-SR(P25)] × hazard(P90)`

其中 `c3` 来自包含 SM 和完整控制变量的产量方程，hazard P90、SR P25/P75 均在当前 scale 的当前区域内重新计算。该指标统一换算为近似对数产量差，避免直接比较不同单位的 drought、heat 和 hotdry 原始系数。区域主扫描只估计产量方程；全国两方程结构继续作为第二层门槛，入选尺度再完整复核区域两方程。

### NE：drought specialization，最高 4 分

- drought `scaled_buffer > 0`：1 分；
- drought gain 大于 heat 和 hotdry：2 分；
- drought `c3 > 0, p < 0.10`：1 分。

### HHH：thermal/compound specialization，最高 3 分

- heat 和 hotdry buffer 均为正：1 分；
- `max(heat, hotdry) > drought`：1 分；
- heat 或 hotdry 的 `c3 > 0, p < 0.10`：1 分。

### NW：dry-compound specialization，最高 3 分

- drought 或 hotdry buffer 为正：1 分；
- `max(drought, hotdry) > heat`：1 分；
- 对应最大项 `c3 > 0, p < 0.10`：1 分。

### SW：thermal/compound specialization，最高 3 分

- heat 和 hotdry 至少一项 buffer 为正：1 分；
- `max(heat, hotdry) > drought`：1 分；
- heat 或 hotdry 的 `c3 > 0, p < 0.10`：1 分。

### SH：thermal/compound boundary，最高 1 分

- `max(heat, hotdry) > drought` 且最大项为正：1 分。

### 跨区域对比，最高 2 分

- NE 的主要 buffer 为 drought，同时 SW 的主要 buffer 为 heat/hotdry：1 分；
- HHH 的主要 buffer 为 heat/hotdry，同时 NW 的主要 buffer 为 drought/hotdry：1 分。

区域得分最高 16 分。

## 四、第二排序维度

### 全国状态依赖，最高 2 分

- drought、heat、hotdry 均满足 `a1 < 0, b > 0, c3 > 0, TE_slope > 0`：1 分；
- 三类 `c3 p < 0.10`：1 分。

### 全国灌溉重新配置，最高 3 分

- drought 三重项为正且 `p < 0.10`：1 分；
- heat 三重项为负且 `p < 0.10`：1 分；
- hotdry 三重项为负且 `p < 0.10`：1 分。

## 五、物候加分，最高 2 分

- `HE±10` 满足 `D × H < 0`、`SR × D × H > 0`，两项均 `p < 0.10`：1 分；
- `HE–MA` 满足同一严格门槛：1 分。

full 和 `V3–HE` 不进入本轮主评分，只在报告中用于说明边界。

## 六、排序与复核

按以下顺序排序：

1. 区域得分；
2. 全国 baseline + irrigation 得分；
3. 物候加分；
4. 区域目标项的截尾 `-log10(p)` 证据和；
5. 有效样本量。

先对全部 256 个 scale 做 OLS 区域扫描。随后对 OLS 区域最高分及次高一分的全部 scale 做 grid-cluster 复核；若候选超过 80 个，则先按区域证据和选前 80 个，并将该限制写入结果。

## 七、输出

- `temp/2026-06-11_region_first_story_search/region_all_scales_ols.csv`
- `temp/2026-06-11_region_first_story_search/ranking_ols.csv`
- `temp/2026-06-11_region_first_story_search/region_candidates_cluster.csv`
- `temp/2026-06-11_region_first_story_search/ranking_cluster.csv`
- `quality_reports/2026-06-11_region_first_story_search.md`

## 八、解释边界

该搜索按观察到的结果选择最符合区域故事的 scale，属于探索性规格搜索。分区域模型完成后，已经对 `G057` 和 `G185` 补充统一 pooled fully-interacted 模型中的区域 Wald 检验；该检验用于判断同一种 hazard 的 scaled buffer 是否存在区域异质性。

## 九、执行中追加批次

第一阶段产生 208 个 `region_score >= 14` 的 OLS 候选，原计划按区域证据与次级结果截取前 80 个聚类复核。首批复核得到 `G057` 为已验证候选第一名，但不足以确定 208 个区域高分尺度中的全局第一。

因此追加第二批次：对剩余 128 个候选运行完全相同的区域、全国 baseline、连续 irrigation 和两个生殖期模型，随后与首批 80 个结果合并并按原排序规则重排。该批次不改变任何门槛或权重。

## 十、执行状态

- [x] 256 个 scale 的 OLS 区域扫描。
- [x] 首批 80 个高分候选的 `grid_id` 聚类复核。
- [x] 剩余 128 个高分候选的 `grid_id` 聚类复核。
- [x] 合并全部 208 个候选并按原规则重排。
- [x] 核对全国 baseline、连续 irrigation 与两个物候窗口。
- [x] 更新最终报告并明确 NW、SH 和结果导向搜索的解释边界。
- [x] 对 `G057` 与 `G185` 补充 pooled fully-interacted `region × SR × hazard` Wald 检验。

最终入选 scale 为 `G057`，区域得分 15/16；若要求保留 `main_sample=1`，对应选择为 `G185`。
