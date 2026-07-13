# G185 region-specific old irrigation-boundary plan

## Scope

本轮执行 old G185 continuous-irrigation boundary region-specific rerun。严格使用 old G185 method，不使用 v3 response surface、RCS、GAM、CausalForest、DML、province-year FE、no-SM reduced-form 模型，也不使用 `g185_v3_review_bundle` 输出。

## Required implementation

1. 读取并复用 `scripts/python/build_g185_draft_bootstrap_v1.py` 中的 old irrigation model 逻辑，尤其是 `xvars_for_irrigation(hazard)` 与 `bootstrap_irrigation()` 的变量构造、grid/year FE 和 cluster/bootstrap 处理方式。
2. 使用 `scripts/python/expanded_scale_story_search.py` 恢复 old G185 样本，并断言：
   - full G185 N = 46,299
   - full G185 grids = 13,236
   - named-region N = 44,556
   - region-specific models exclude Other
3. 新增脚本：
   - `scripts/python/export_g185_region_specific_irrigation_boundary.py`
4. 新建输出目录：
   - `quality_reports/agent_runs/2026-06-24_g185_region_specific_irrigation_boundary/`
5. 对 `NE/HHH/NW/SW/SH` × `drought/heat/hotdry` 估计 region-specific old irrigation triple-interaction FE model。
6. 生成 required tables、plot_data、diagnostics、README、manifest、scripts_used copy，并打包：
   - `quality_reports/agent_runs/2026-06-24_g185_region_specific_irrigation_boundary/g185_region_specific_irrigation_boundary_bundle.zip`

## Figure contract

参考用户给定三联图样式，创建 preliminary figures：

- `figures/region_irrigation_key_panels.png`
- `figures/region_irrigation_boundary_heatmap.png`
- `figures/hhh_heat_hotdry_irrigation_boundary.png`

图形使用真实 irrigation fraction 横轴，显示 95% CI band、P25/P50/P75 reference lines 或标注点，并标注 “Old G185 FE model; region-specific estimates; conditional associations.”。

## Verification

1. `py_compile` 新脚本。
2. 运行脚本成功，stop conditions 不触发。
3. 检查 required files 均存在于 zip。
4. 检查 `assertions.json` overall_status 为 `PASS`。
5. 检查 zip integrity `testzip() == None`。
6. 检查 no raw grid-year exports：无 `grid_id/grid_code/latitude/longitude/province`、无 `.dta`、无 row-level grid-year data。
