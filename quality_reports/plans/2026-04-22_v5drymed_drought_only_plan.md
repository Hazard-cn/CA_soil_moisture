# 2026-04-22 v5drymed Drought-Only Plan

## 目标
- 仅实现 drought-only Model 8 baseline。
- dry-side mediator 纳入 `drydays`、`dryshare`、`drydeficit`。
- wet 端统一使用 SPEI 派生的 `W_full` 与 `SR_x_W_full`。
- 所有主回归、bootstrap、异质性统一使用全量控制：`irr_frac pr_sum et0_sum aridity gdd_10_30`。

## 数据入口
- 基础分析面板：`data/processed/v3_analysis_ready.dta`
- 异质性分组：`data/processed/v3sub_analysis_ready.dta`
- pooled / maize-zone drydays sidecar：`temp/2026-04-21_sm_state_audit/sm_state_panel_wide.dta`
- 其余 dry-side 长变量：`data_build/data/processed/data_v3_main.dta`

## 实施结构
- `v5drymed_step0_preamble.do`
  - 合并 dry-side 变量和异质性分组。
  - 标准化生成 `v5dd_*`、`v5ds_*`、`v5ddf_*` mediator alias。
  - 为 12 个规格组构造六源共样本 flag。
- `v5drymed_step1_model8.do`
  - 对全部规格组跑 drought-only moderated mediation。
  - 导出系数表与 `IE/DE/TE/Index` 表。
- `v5drymed_step2_bootstrap.do`
  - 仅对主规格 `ds/ddf × pl/mz` 跑 cluster bootstrap。
- `v5drymed_step3_heterogeneity.do`
  - 仅对主规格跑 `irr_group` 与 `maize_zone` 异质性。
- `v5drymed_step4_summary.do`
  - 整理 sign diagnostic。
- `v5drymed_run_all.do`
  - 串行执行全流程。

## 结果输出
- `output/tables/v5drymed_model8_coefficients.csv`
- `output/tables/v5drymed_conditional_effects.csv`
- `output/tables/v5drymed_bootstrap.csv`
- `output/tables/v5drymed_heterogeneity_coefficients.csv`
- `output/tables/v5drymed_heterogeneity_effects.csv`
- `output/tables/v5drymed_heterogeneity_skips.csv`
- `output/tables/v5drymed_sign_diagnostic.csv`

## 当前实现约束
- 当前任务窗口固定为 full-season。
- pooled / maize-zone `drydays` 来自 state sidecar 短变量。
- pooled / maize-zone `dryshare` 与 `drydeficit` 使用 `data_v3_main.dta` 中的 full-season 长变量。
