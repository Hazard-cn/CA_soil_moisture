# 用 SM 替代 SPEI 的多源 H-SM-SR 系数图方案

日期：2026-04-15

## Summary

基于 `data/processed/v3prhdsm_analysis_ready.dta` 新增独立 Stata 脚本，完全移除原始 SPEI 派生的 `D/W` 变量，不再沿用 `D x H x SR` 框架，而是把各窗口的 SM 标准化后取反，定义为连续型干旱代理 `dry_sm = -z(SM)`，然后仅用 `H`、`dry_sm`、`SR` 及其层级完整交互估计产量方程。最终结果只输出系数图，保持 2 张主图：`surface` 一张、`rootzone` 一张；每张图内部按数据源分 3 个子面板，分别展示 GLEAM、SWSM、ERA 在 6 个时间窗口下的核心交互系数。

## Implementation Changes

- 新增独立脚本 `scripts/stata/v3_smproxy_multisource_coefplot.do`，直接读取 `data/processed/v3prhdsm_analysis_ready.dta`，不改现有 SPEI 主线脚本。
- 数据源与层次映射固定为：
  - `surface`: `gleam_sms_mean*`、`swsm_l1_mean*`、`era5l_swvl1_mean*`
  - `rootzone`: `gleam_smrz_mean*`、`swsm_l3_mean*`、`era5l_swvl3_mean*`
- 时间窗口保留 6 个全套：`full`、`v3pre30`、`v3pm10`、`hepm10`、`v3he`、`hema`。
- 对每个 `source x layer x window`，在 `main_sample == 1` 上单独构造标准化连续代理：
  - `sm_z = (SM - mean_main_sample) / sd_main_sample`
  - `dry_sm = -sm_z`
- 每个 `source x layer x window` 统一估计：

```stata
reghdfe ln_yield ///
    dry_sm H ca ///
    dry_sm_x_H ///
    SR_x_H ///
    SR_x_dry_sm ///
    SR_x_dry_sm_x_H ///
    controls_window ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
```

- 回归中明确排除所有旧 SPEI 口径变量与衍生交互，包括 `D_*`、`W_*`、`SR_x_D_*`、`SR_x_W_*`、`D_x_Heat_*`、`SR_x_D_x_Heat_*`。
- 每个模型只提取并汇总 4 类核心系数：
  - `dry_sm x H`
  - `SR x H`
  - `SR x dry_sm`
  - `SR x dry_sm x H`
- 结果整理为长表中间产物，字段至少包括：`source`、`layer`、`window`、`term`、`b`、`se`、`p`、`N`、`r2`。
- 图形组织固定为 2 张：
  - `surface` 图：3 个 source 子面板（GLEAM / SWSM / ERA）
  - `rootzone` 图：3 个 source 子面板（GLEAM / SWSM / ERA）
- 若本机缺少 `coefplot`，脚本先 `cap which coefplot` 检查；失败时改用长表手工绘制同样的系数图。

## Public Interfaces / Outputs

- 新增脚本：`scripts/stata/v3_smproxy_multisource_coefplot.do`
- 中间结果：`output/tables/v3_smproxy_multisource_long.csv`
- 最终图件：
  - `output/figures/v3_smproxy_surface_coefplot.png`
  - `output/figures/v3_smproxy_rootzone_coefplot.png`

## Test Plan

- 运行新脚本并检查日志无 `r()` 报错、无变量缺失、无主要交互项被系统性共线删除。
- 核对模型数量完整：`3 sources x 2 layers x 6 windows = 36` 个模型。
- 核对长表结果完整：每个模型都至少产出 4 个核心系数，总体应有 `36 x 4 = 144` 条核心结果记录。
- 核对 2 张图均成功输出，且每张图都包含 3 个 source 子面板；每个子面板内都有 6 个窗口对应的系数与置信区间。
- 做 3 组一致性检查：
  - `corr dry_sm SM` 为负且绝对值接近 1；
  - 各窗口确实调用对应窗口的 `hdd_ge32*` 与 `CTRL_*`；
  - 回归式中未重新引入任何 `D/W` 旧变量。

## Assumptions

- “Gleam、ERA和SWSM都要用”解释为三套来源都纳入同一套 H-SM-SR 代理框架，而不是只做稳健性附录。
- `surface/rootzone` 对三套来源的对应关系固定为 GLEAM `sms/smrz`、SWSM `l1/l3`、ERA `swvl1/swvl3`。
- 主图保持 2 张，不扩展为 6 张；多来源比较通过图内子面板完成。
- 系数图默认只展示交互项，不展示主效应。
- FE、聚类和样本锁定沿用项目规范：`absorb(grid_id year)`、`vce(cluster grid_id)`、`if main_sample == 1`。
