# 2026-04-21 Soil Moisture 状态化审计计划

## 目标
在不改写现有 `v3_analysis_ready.dta`、`v3bpath_analysis_ready.dta` 和 beamer 输出的前提下，新增一条 sidecar exploratory 线，用统一 wet-side control 比较 raw `SM` 与状态化 `SM` 在 drought-side mechanism 框架中的可解释性。

## 实施范围
- 结果窗口：`full`、`v3pre30`
- 负面对照窗口：`v3pm10`
- 阈值方案：
  - `pooled`：`source-layer × window` pooled daily `P25/P75`
  - `maize_zone`：`source-layer × window × maize_zone` local daily `P25/P75`
- 输出目录：`temp/2026-04-21_sm_state_audit/`

## 关键实现
- Python builder 复用 `data_build/scripts/python/s04a_calc_sm_gleam.py`、`s04b_calc_sm_swsm.py`、`s04c_calc_sm_era5land.py` 的窗口聚合逻辑，生成 `DryShare`、`WetShare`、`valid_days`、raw window stats 和阈值表。
- builder 先执行 `P20` 回放校验，对齐 `data_build/data/processed/data_v3_main.dta` 中现有 `drydays_*_le_p20`。
- Stata sidecar 线拆成：
  - `step0_preamble`：合并 `v3prhdsm_analysis_ready.dta`、`v3_analysis_ready.dta`、state panel，并锁定 `state_*_6_sample`
  - `step1_descriptives`：输出 raw-SM 表、state 表、wet-leaning 判定所需统计
  - `step2_state_models`：运行 `Raw-Legacy`、`Raw-StateCtrl`、`State-Main`
- 主比较只在 `Raw-StateCtrl` 与 `State-Main` 之间进行；`Raw-Legacy` 仅作为与现有 `W_w` 口径接轨的 benchmark。

## 验收
- pooled 阈值表 18 行，`maize_zone` 阈值表 108 行
- `grid_id year threshold_scheme window source-layer` 唯一
- `0 <= DryShare, WetShare <= 1` 且 `DryShare + WetShare <= 1 + 1e-8`
- `Raw-StateCtrl` 与 `State-Main` 同组 `N` 一致
- 结果说明能够直接回答：
  - 窗口是否呈 wet-leaning
  - state model 是否比 raw model 更接近可解释方向
  - 这种改善是否出现在 `v3pm10`
