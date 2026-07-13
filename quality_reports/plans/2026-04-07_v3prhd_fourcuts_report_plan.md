# V3 PR HotDry 四切分回归与 Beamer 报告计划

## Summary

- 分析入口切换到 `data_build/data/processed/data_v3_main.dta`，因为该数据包含 `gdd_10_30*` 和 `hotdrydays_ge32_pr_lt1*`。
- 本任务独立生成 `v3prhd_*` 产物，不覆盖现有 `v3_*` 脚本、表、图和报告。
- 模型固定为 4 个规格、4 个切分，使用 `grid_id` 与 `year` 双固定效应，`cluster(grid_id)`，并统一不纳入 `W`、`SR×W` 和 `aridity`。
- horse-race 切分沿用现有 repo 结构，气候变量按窗口进入，控制变量统一使用 full-season 版本的 `irr_frac pr_sum et0_sum gdd_10_30`。

## Key Changes

- 新建 `scripts/stata/v3prhd_macros_include.do`，集中定义路径、控制变量和 4 个切分的 RHS 宏。
- 新建 `scripts/stata/v3prhd_step0_preamble.do`，从 `data_v3_main.dta` 构造 `D_*`、`SR×D`、`SR×H`、`D×H`、`SR×D×H`、`HotDryPr` 和 `SR×HotDryPr`，并生成 `main_sample`。
- 新建 `scripts/stata/v3prhd_step1_regressions.do`，输出：
  - 长表：`v3prhd_results_long.csv`
  - 宽表：`v3prhd_spec1_table.*` 到 `v3prhd_spec4_table.*`
- 新建 `scripts/R/v3prhd_coefplots.R`，生成 4 张参数图和 2 张组合图。
- 新建 `output/reports/v3prhd_beamer_report.Rmd`，单独渲染 beamer PDF。

## Test Plan

- 校验 `data_v3_main.dta` 含有 `hdd_ge32*`、`hotdrydays_ge32_pr_lt1*`、`gdd_10_30*`、`spei6_mean`、`spei1_mean_*`、`spei2_mean_*`。
- 校验 `v3prhd_analysis_ready.dta` 中 `main_sample` 成功生成，且 `xtset grid_id year` 正常。
- 校验 16 个模型全部成功估计，长表包含每个 cut/spec/term 的系数、标准误、p 值、N 和 `r2`。
- 校验所有模型控制变量均不含 `aridity`。
- 校验参数图和 beamer PDF 完整生成，且只依赖 `v3prhd_*` 结果文件。

## Assumptions

- 热阈值固定为 `32°C`。
- Spec 4 采取真正缩减模型：只保留 `SR`、`HotDryPr` 和 `SR×HotDryPr`。
- multi-window cut 不叠加窗口级 controls，而是沿用 full-season controls。
