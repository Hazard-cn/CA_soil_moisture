# G049 区域差异与故事线检验计划

日期：2026-06-11

## 一、固定对象

- Scale：`G049`。
- 样本规则：`ggcp10_maize_frac >= 0.05`、`yield_tons_ha ∈ [0.5,18)`、剔除相邻年份 `|Δln(yield)| > 1` 的跳变观测。
- 区域：使用 `maize_zone`，包括 NE、HHH、NW、SW、SH；`Other` 单独报告，不并入任何主要区域。
- 推断：grid fixed effects + year fixed effects，标准误按 `grid_id` 聚类。

本轮不允许为区域分别改变 scale、窗口、控制变量或显著性门槛。

## 二、故事支持门槛

### 单一胁迫状态依赖

对 drought、heat、hotdry 分别检查：

- `a1 < 0`；
- `b > 0`；
- `c3 > 0`；
- `TE slope > 0`。

区域三类 hazard 均保持方向，记为方向支持；至少两类 `c3 p < 0.10`，记为统计支持。

### 生殖期联合响应

分别检查 `HE±10` 和 `HE–MA`：

- `D × H < 0`；
- `SR × D × H > 0`。

两项方向均满足，记为方向支持；两项均 `p < 0.10`，记为严格支持。`V3–HE` 若表现为 `D × H > 0` 且三重项不为正，作为阶段定位的补充支持。

### 灌溉重新配置

区域模型中的连续灌溉三重项并非区域间正式差异检验，仅用于判断区域内条件结构：

- drought 三重项预期为正；
- heat 与 hotdry 三重项预期为负。

区域的灌溉中位数用于描述，不直接替代交互检验。区域间比较只解释为与故事一致或不一致，不称为区域因果差异。

## 三、输出

- `temp/2026-06-11_g049_region_story_test/region_support.csv`
- `temp/2026-06-11_g049_region_story_test/region_baseline_cluster.csv`
- `temp/2026-06-11_g049_region_story_test/region_phenology_cluster.csv`
- `temp/2026-06-11_g049_region_story_test/region_irrigation_cluster.csv`
- `quality_reports/2026-06-11_g049_region_story_test.md`

## 四、判定

- “支持故事”：主要区域中至少两个严格支持生殖期联合响应，且其余主要区域没有精确估计出的反向结果；单一胁迫方向在多数主要区域成立。
- “部分支持”：全国结果明确，但区域层面仅方向一致、显著性受支持量限制，或存在一个可解释的反向边界。
- “不支持”：多个有充分支持量的主要区域给出精确反向结果，或全国结果完全由单一区域驱动。
