# v3bpath 统一重跑执行计划

## 1. 执行目标
本轮把 brainstorm 1-8 全部收回到同一条 `v3bpath_*` 审计线中统一重跑，不再以旧 `v3med`、`v3proxy` 结果作为主答案。新增跨 SM 数据比较作为显式模块和显式汇总表输出。`wet` 变量统一作为普通 control 进入模型，任何 wet × SR 交互都不进入新回归。全套结果最终整体替换 `temp` 中的旧最小增量包。

## 2. 统一规格
数据底座改为以 `data/processed/v3prhdsm_analysis_ready.dta` 为主表，再按 `grid_id year` 从 `data/processed/v3_analysis_ready.dta` 合并 `W_full`、`W_v3pre30`、`W_v3pm10`、`W_v3he`、`W_hepm10`、`W_hema`。样本统一锁成两套：`bpath_full6_sample` 用于 full-season 模块，`bpath_stage6_sample` 用于 stage/full 对齐 timing 模块。两套样本都要求 6 个 source-layer 的 SM 变量完整，因此跨源比较在同一共同支持上完成。

所有新回归统一使用 `gdd_10_30*`。full-season 回归一律使用 `W_full` 作为 wet control，stage 回归一律使用对齐窗口的 `W_w` 作为 wet control。hot-dry 类指标不进入本轮任何新增回归。

## 3. 新的 v3bpath 模块
`step0_preamble` 负责生成 `v3bpath_analysis_ready.dta`、`bpath_full6_sample`、`bpath_stage6_sample`、6 个 `SMdef_*` 和 6 源 × full/stage 窗口 `dry_*` proxy，并输出诊断表。

`step1_timing_audit` 使用 6 个 source-layer × 6 个窗口统一跑  
`ln_yield ~ D_w + ca + SR_x_D_w + hdd_ge32_w + SM_w + W_w + irr_frac + gdd_10_30_w + FE`，  
输出 `v3bpath_timing_audit.csv`。该表新增 `effective_N` 与 `stage6_common_flag` 两列，且 full 窗口也固定在 `bpath_stage6_sample` 上估计，以保证跨窗可比。

`step2_control_ladder` 使用 6 个 source-layer × 4 级 ladder 统一跑 mediator 和 outcome 两条方程。Ladder 固定为：`L0 = irr_frac + gdd_10_30 + W_full`，`L1 = L0 + pr_sum`，`L2 = L1 + et0_sum`，`L3 = L2 + aridity`。

`step3_wet_control_audit` 使用 6 个 source-layer × 3 个规格：`N0 = no-W + raw SM`，`N1 = +W_full + raw SM`，`N2 = +W_full + SMdef`，只诊断 wetness 作为普通 control 后负 b 吸收了多少。

`step4_nonlinear_audit` 使用 6 个 source-layer × `baseline / quadratic / tails` 三种规格，统一包含 `W_full`、`irr_frac`、`gdd_10_30`。

`step5_proxy_competition` 使用 6 个 source-layer × `reduced/full` 两版 controls，统一重跑 `SetA / SetB / SetC / CompeteD / CompeteSM`，不带 hot-dry 指标。

`step6_source_depth_audit` 使用 6 个 source-layer × `reduced/full` 两版 controls，统一输出 `a3`、`b`、`c3` 及相关控制项系数。

`step7_heat_consistency` 使用 6 个 source-layer × `rawSM_bg / DrySM_bg` × `reduced/full`，统一检验 `SR_x_Heat_full` 在不同 SM background control 下是否稳定。

`step8_sensitivity_claim_audit` 使用 6 个 source-layer × 5 个固定规格：`raw_full_L0`、`raw_full_provyear`、`smdef_full_L0`、`smdef_full_provyear`、`stage_v3pre30_L0`，并生成 `v3bpath_sm_comparison_summary.csv`。`step8` 表中同样带 `effective_N` 与 `stage6_common_flag` 两列。

## 4. 固定输出
日志固定为：`v3bpath_run_all.log` 与 `v3bpath_step0-8*.log`。结果表固定为：

- `v3bpath_diagnostics.csv`
- `v3bpath_timing_audit.csv`
- `v3bpath_control_ladder.csv`
- `v3bpath_wet_control_audit.csv`
- `v3bpath_nonlinear_audit.csv`
- `v3bpath_proxy_competition.csv`
- `v3bpath_source_depth_audit.csv`
- `v3bpath_heat_consistency.csv`
- `v3bpath_sensitivity_claim_audit.csv`
- `v3bpath_sm_comparison_summary.csv`

## 5. 验收标准
Stata batch 统一由 `scripts/stata/v3bpath_run_all.do` 顺序调用 `step0 -> step8`，任一步非零返回码即 fail-fast 退出。新结果表覆盖数固定为：timing 36 行，control ladder 24 行，wet control audit 18 行，nonlinear audit 18 行，proxy competition 12 行，source-depth 12 行，heat consistency 24 行，sensitivity claim audit 30 行，SM comparison summary 6 行。

所有新脚本、日志和说明文档都只使用新版 GDD 口径，不引入 wet × SR 交互，也不引入新的 hot-dry 指标回归。`output/figures` 与现有 beamer `.tex` 文件不允许新增或覆写。
