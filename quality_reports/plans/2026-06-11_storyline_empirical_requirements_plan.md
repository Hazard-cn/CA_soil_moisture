# 六条故事线的实证要求与物候期整合计划

日期：2026-06-11

## 目标

基于 `quality_reports/2026-06-11_candidate_storylines_from_zotero.md` 中的六条候选主线，逐条定义可检验的理论结果模式、反证标准和最小补充检验，并判断当前 F4-B067 全生育期、区域/灌溉异质性及 V3、HE、MA 物候窗口结构是否足以支撑相应命题。

## 核对材料

1. 当前图组说明：`output/figures/f4_b067_v2/figure_captions.md`。
2. 当前 B067 图形数据与绘图代码：`scripts/R/plot_f4_b067_coefficient_figures.R`。
3. 物候窗口构造：`data_build/scripts/python/config.py`、`data_build/scripts/python/s01_load_phenology.py`、`scripts/stata/v3_step0_preamble.do`。
4. 分期单窗口与 horse-race：`scripts/stata/v3_step2_stage_effects.do`、`output/tables/v3_step2_stage_single.csv`、`output/tables/v3_step2_stage_horserace.csv`。
5. 当前 B067 区域分期诊断：`quality_reports/2026-06-04_f4_b067_region_window_diagnostics.md`。
6. SM 时序与跨数据源审计：`quality_reports/2026-04-20_v3bpath_audit_results.md`。

## 判定方法

每条主线按四项判断：必要结果模式、现有覆盖度、最强反证、最多两个必要补充。物候期结果只作为生物时序一致性和反证层，不因某一窗口显著而自动升级为中心命题；窗口间差异必须使用共同样本和正式系数差异检验。

## 输出

保存为 `quality_reports/2026-06-11_storyline_empirical_requirements_and_phenology.md`。最终建议应区分：现有结构基本足够、补一项即可、需要重估后才能使用、只适合 Discussion/边界条件。

