# 扩展 Scale 故事线搜索计划

日期：2026-06-11

## 搜索层级

本轮从当前 128 个 `Bxxx` scale 向外退一步，但不恢复已经弃用的 legacy crop mask 作为主口径。

1. 固定唯一硬边界：`ggcp10_maize_frac >= 0.05`。
2. 取消 `main_sample == 1` 的固定要求。
3. 将 `main_sample`、`zone_core`、`yield_domain`、`yield_jump`、`sm_sd`、`sm_coverage`、`sr_within`、`years_ge3`、`stable_province` 作为平行开关。
4. 去除产生相同样本掩膜的重复组合，形成新的 `Gxxx` scale。
5. 旧 1,024 个 `Vxxxx` scale 只用于历史比较；其中 `crop_mask` 是 legacy `maize_frac >= 0.05` 与 `ggcp10_maize_frac >= 0.01` 的组合，不作为当前推荐定义。

## 预先固定的故事门槛

### 状态依赖缓冲

- 三类 hazard 的 `a1 < 0`、`b > 0`。
- `TE(P75) - TE(P25) > 0`。
- 至少两类 hazard 的 `c3 > 0` 且 `p < 0.10`。

### 热损失的水分条件性

- heat 的 `a1 < 0`、`b > 0`。
- 若主张 SR 保水通道，还要求 heat `a3 > 0` 且 `p < 0.10`。
- 否则只允许保留水分条件性的弱版本。

### 灌溉重新配置

- 使用连续 `irr_frac` 的层级完整交互。
- drought 的 `SR × hazard × irrigation` 预期为正。
- heat 的对应交互预期为负。
- 至少一项达到 `p < 0.10`，并报告另一项的区间，不用分组显著性替代差异检验。

### 联合热旱响应面

- 同一层级完整模型保留 D、H、SR 及全部低阶交互。
- `D × H < 0` 且 `SR × D × H > 0`。
- 优先要求两项均 `p < 0.10`；只满足后一项时降级为 joint-surface modification。

### 胁迫特异通道

- drought、heat、hotdry 的 `a3` 或 IE/DE slope 至少形成两种不同类型。
- 差异必须在规则包络内重复，不能只依赖单一 scale。

### 环境定向

- 使用连续 aridity 或 irrigation modifier。
- 区域结果仅作边界，不以区域排序作为通过条件。

## 执行顺序

1. 生成并审计 `Gxxx` scale 索引。
2. 在全部 G-scale 上运行 full-season baseline 两方程、连续 irrigation modifier 和连续 `D × H × SR` 扫描。
3. 按上述门槛筛选候选，优先选择样本最大且规则最少的版本，不按 p 值最大化选择。
4. 仅对入选候选运行 full、`V3-HE`、`HE±10`、`HE-MA` 物候复核和必要 bootstrap。
5. 输出通过、近似通过和失败 scale，不隐藏相反结果。

## 输出

- `temp/2026-06-11_expanded_scale_story_search/`
- `quality_reports/2026-06-11_expanded_scale_story_search.md`

