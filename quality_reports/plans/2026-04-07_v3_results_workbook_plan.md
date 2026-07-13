# 2026-04-07 v3 非中介日志结果汇总计划

## 任务目标
- 生成 `output/tables/v3_report_results_equation_first.xlsx`。
- 尽量把 `v3` 系列日志对应的非中介结果全部列入工作簿。
- 明确排除中介相关日志与输出。

## 纳入范围
- `v3_step1_baseline.log`
- `v3_step2_stage_effects.log`
- `v3_step3_sm_comparison.log`
- `v3_step4_full_coefs_20260406.log`
- `v3_step4_interaction_grid_20260405.log`
- `v3_step5_robustness.log`
- `v3_step8_heterogeneity_20260405.log`

## 排除范围
- `v3_step4_mediation.log`
- `v3_step6b_mediation_countyFE_20260405.log`
- `v3_step0_preamble.log` 仅做数据准备，不含经验结果

## 工作簿结构
- `00_log_map`
- `01_step1_baseline`
- `02_step2_stage_effects`
- `03_step3_sm_comparison`
- `04_step4_nonmediation`
- `05_step5_robustness`
- `06_step8_heterogeneity`

## 实现原则
- 每个块先写标题和方程/说明，再写结果表。
- 优先使用日志对应的现成 `csv` 输出，不重跑回归。
- 对 `esttab` 导出的原始表按原样保留，避免丢失日志中的列。
- 为避免 Excel 把 `=` 开头单元格当成公式，导入时统一转义。

## 验证要求
- `Rscript scripts/R/v3_results_workbook.R` 能成功生成 `.xlsx`。
- `00_log_map` 中纳入/排除关系清楚。
- 每个纳入日志至少对应一个结果块。
- 中介相关日志与表不出现在最终工作簿。
