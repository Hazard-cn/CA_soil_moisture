# Soil Moisture Spec2/Spec3/Spec4 Beamer Report Plan

日期：2026-04-07

## 任务定义
- 因变量从 `ln_yield` 切换为 Soil Moisture。
- Soil Moisture outcome 固定为 6 个 full-season 均值变量：
  - `gleam_sms_mean`
  - `gleam_smrz_mean`
  - `swsm_l1_mean`
  - `swsm_l3_mean`
  - `era5l_swvl1_mean`
  - `era5l_swvl3_mean`
- 估计 `spec2`、`spec3` 与 `spec4`。
- 保持四个 cut 结构不变：
  - `i` Full
  - `ii` `v3pm10 + hepm10`
  - `iii` `v3he + hema`
  - `iv` `v3pre30 + v3he + hema`
- 单独输出一套 beamer 报告，不覆盖现有 `v3prhd_*` 产物。

## 建模假设
- DV 使用 6 个 full-season Soil Moisture outcome；四个 cut 仅改变 RHS 暴露分解，不改变 DV 定义。
- 样本纪律保持与前序任务一致：`if main_sample == 1`，`absorb(grid_id year)`，`vce(cluster grid_id)`。
- `main_sample` 仍由 `ln_yield` 基准模型 `ca + D_full + hdd_ge32 + SR_x_D_full + SR_x_Heat_full + CTRL_full` 定义。
- 控制变量不放 `aridity`，统一保留 `irr_frac + pr_sum + et0_sum + gdd_10_30`。
- `HotDryPr` 继续使用基于降水阈值的 `hotdrydays_ge32_pr_lt1*`。
- `spec2` 定义为 `SR + D + H + SR×D + SR×H + D×H + SR×D×H + X + FE`。

## 代码产物
- `scripts/stata/v3prhdsm_macros_include.do`
- `scripts/stata/v3prhdsm_step0_preamble.do`
- `scripts/stata/v3prhdsm_step1_regressions.do`
- `scripts/R/v3prhdsm_coefplots.R`
- `output/reports/v3prhdsm_beamer_report.Rmd`

## 输出产物
- `data/processed/v3prhdsm_analysis_ready.dta`
- `output/tables/v3prhdsm_results_long.csv`
- `output/figures/v3prhdsm_plot_spec3_srpaths.png`
- `output/figures/v3prhdsm_plot_hotdry_compare.png`
- `output/figures/v3prhdsm_plot_sr_compare.png`
- `output/reports/v3prhdsm_beamer_report.pdf`

## 回归组织
- 模型总数：`6 outcomes × 3 specs × 4 cuts = 72`
- 长表字段：
  - `outcome`
  - `source`
  - `layer`
  - `cut`
  - `spec`
  - `window`
  - `term`
  - `b`
  - `se`
  - `p`
  - `N`
  - `r2`

## 报告结构
- 标题页
- 1 页设计说明
- 1 页 six-outcome 映射
- Spec 2 表页
- Spec 3 表页
- Spec 4 表页
- 5 页系数图
- 1 页 appendix

## 验证
- 校验 6 个 SM outcome 和 `HotDryPr*`、`SR_x_HotDryPr*`、`gdd_10_30*` 均存在。
- 校验 72 个模型全部落到结果长表。
- 校验 `spec2` 含 `D_x_Heat` 与 `SR_x_D_x_Heat`。
- 校验 `spec3` 含 `SR_x_D`、`SR_x_Heat`、`HotDryPr`、`SR_x_HotDryPr`。
- 校验 `spec4` 只含 `ca`、`HotDryPr`、`SR_x_HotDryPr`。
- 校验 beamer PDF 成功生成且表页、图页无重叠。
