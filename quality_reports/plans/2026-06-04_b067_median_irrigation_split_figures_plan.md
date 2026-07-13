# B067 median irrigation split figure plan

本次任务重新定义灌溉异质性，不沿用数据中已有 `irr_group`。切分变量为 `irr_frac`，在对应分析样本内用观测层面中位数切成：

- `low_irr_median`: `irr_frac < median(irr_frac)`
- `high_irr_median`: `irr_frac >= median(irr_frac)`

覆盖三套样本：

- B067 full sample: 用全 B067 样本内 `irr_frac` 中位数。
- AI>2 dry sample: 用 B067 且 `ai_pet_over_p_gridmean > 2` 样本内 `irr_frac` 中位数。
- AI<1 humid sample: 用 B067 且 `ai_pet_over_p_gridmean < 1` 样本内 `irr_frac` 中位数。

估计口径：

- 只保留最新主图口径：`transform=raw`，`mediator=mean`。
- hazard: `drought`, `heat`, `hotdry`。
- 每个 subgroup 重估 mediator 方程和 outcome 方程，并使用 cluster wild score bootstrap 计算 `IE/DE/TE` 在 SR `P25/P50/P75` 下的区间。
- 每个 subgroup 使用 500 bootstrap reps。

输出：

- `temp/2026-06-04_f4_b067_median_irrigation/f4_b067_median_irrigation_iede_summary.csv`
- `temp/2026-06-04_f4_b067_median_irrigation/f4_b067_median_irrigation_support.csv`
- `output/figures/f4_b067_v2/fig8_irr_median_high_irr_iede.png`
- `output/figures/f4_b067_v2/fig9_irr_median_low_irr_iede.png`
- `output/figures/f4_b067_v2/fig10_irr_median_combined_iede.png`
- `output/figures/f4_b067_v2/fig11_ai2_irr_median_combined_iede.png`
- `output/figures/f4_b067_v2/fig12_ai_lt1_irr_median_combined_iede.png`
- `quality_reports/2026-06-04_b067_median_irrigation_split_figures.md`

校验：

- 每套样本的 high/low obs 支持必须写入 support 表。
- 每个 `layer x subgroup x hazard x effect` 必须有 `P25/P50/P75` 三个 SR level。
- 所有图必须能被 PIL 打开且非空。
