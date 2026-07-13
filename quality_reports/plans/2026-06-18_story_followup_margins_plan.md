# 2026-06-18 故事线 follow-up margins 计划

## 目标

在不重新估计模型的前提下，将上一轮识别出的故事线转成更可写入论文正文的结果量，重点补足灌溉连续异质性、物候期联合热旱响应和 SR 分位数下的 TE/IE/DE。

## 输入

- `temp/2026-06-11_region_first_story_search/all_highscore_irrigation_cluster.csv`
- `temp/2026-06-11_region_first_story_search/all_highscore_phenology_cluster.csv`
- `temp/2026-06-04_f4_b067_full_bootstrap_counterfactual/f4_b067_mean_raw_unified_coefficients_effects.csv`
- GGCP10 面板读取函数：`scripts/python/expanded_scale_story_search.py`

## 处理

1. 对 `G057/G185/G049/G177` 计算 `SR P75-P25`、`irr_frac P25/P50/P75` 和 hazard P90 情景下的 SR buffering margins。
2. 对 `G057/G185/G255/G049/G177` 计算 `beta_DH + gamma_SRDH × SR_q` 在 `P25/P50/P75` 下的物候期联合热旱斜率。
3. 从 B067 bootstrap 汇总中抽取 baseline TE/IE/DE 分位数，并计算 `TE(P75)-TE(P25)`。
4. 生成中文 follow-up 报告，明确哪些结论可以写、哪些只能作为边界条件。

## 输出

- `quality_reports/2026-06-18_story_followup_margins.md`
- `temp/2026-06-18_story_followup_margins/irrigation_standardized_margins.csv`
- `temp/2026-06-18_story_followup_margins/phenology_srdh_margins.csv`
- `temp/2026-06-18_story_followup_margins/b067_iede_delta.csv`

## 质量边界

本轮只做情景换算，不新增回归估计；正式投稿表格仍应对最终少数模型做 Stata `reghdfe` 复核。

## 追加复核

在 margins 完成后，补充导出 `G057/G185` 的 Stata 复核面板和 do-file，复核 baseline SR×hazard 与连续 irrigation triple 两类核心系数。该复核只覆盖最终候选 scale，不重新搜索 scale。
