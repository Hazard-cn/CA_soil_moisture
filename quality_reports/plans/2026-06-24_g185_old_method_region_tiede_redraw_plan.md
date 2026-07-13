# 2026-06-24 G185 Old-Method Region IE/DE/TE Redraw Plan

## Scope

重跑旧 G185 方法下的 region-specific IE/DE/TE 代数分解，并重做用户给出的五张旧方法教师图。新结果只服务于旧线性中介-调节口径，不使用 v3 response surface、RCS、GAM、CausalForest、DML 或 `g185_v3` 输出。

## Estimation Contract

- Sample: G185 old-method sample, named maize regions only: NE, HHH, NW, SW, SH; exclude Other.
- Hazards: drought, heat, hotdry.
- Fixed effects: grid fixed effects plus year fixed effects.
- Cluster/bootstrap unit: grid.
- Equations per region-hazard:
  - SM equation: `SM ~ H + SR + SR:H + controls + grid FE + year FE`.
  - Yield equation: `ln_yield_raw ~ H + SR + SR:H + SM + controls + grid FE + year FE`.
- Decomposition:
  - `IE(s) = (a1 + a3*s) * b`.
  - `DE(s) = c1 + c3*s`.
  - `TE(s) = IE(s) + DE(s)`.
  - Main contrast: `100 * (exp((TE(SR75)-TE(SR25)) * Q90(H)) - 1)`.
- Confidence intervals: wild-cluster score/bootstrap linearized draws, seed 42, default reps 999 unless runtime requires a documented fallback.

## Visual Contract

- Figure 1: corrected core three buffers, now labeled as region-specific total buffering association from IE+DE.
- Figure 2: corrected core buffer curves over hazard exposure, using TE contrast rather than residual-only DE.
- Figure 3: all 15 region-hazard combinations as heatmap, using corrected TE contrast.
- Figure 4: retain old continuous-irrigation boundary figure as a separate boundary result, not TE/IE/DE.
- Figure 5: corrected component decomposition for core combinations, showing SM-linked component, residual component, and combined TE contrast.

## Deliverables

- New output directory: `quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/`.
- Required subfolders: `tables/`, `plot_data/`, `figures_png/`, `figures_svg/`, `diagnostics/`, `scripts_used/`.
- Required archive: `g185_old_method_region_tiede_redraw_bundle.zip`.
- Required verification: sample assertions, no v3 input dependency, no exported coordinate/grid identifiers in plot CSVs, ZIP integrity check, image open/read check.
