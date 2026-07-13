# 四窗 GLEAM baseline-local Model 8 重跑计划

## 1. 任务范围
本轮只做 `GLEAM` 的 `window-baseline family`，只保留 `gleam_sms` 与 `gleam_smrz` 两层，不做 `pooled-state`、`maize-zone-state`、异质性，也不扩展到其他 SM 数据源。四个时间窗固定为 `v3pre30`、`v3he`、`hema`、`fullnew`。dry-side mediator 固定覆盖 `blduration_dry`、`bldurshare_dry`、`blseveritymean_ddf`、`blseveritysum_ddf` 四个 family 在 `p10/p20` 下的全部组合。

## 2. 规格矩阵
baseline 规格总数固定为 `4 个 mediator family × 2 个 dry threshold × 2 个 source-layer × 4 个窗口 = 64`。每个 baseline 规格都包含 mediator equation 与 outcome equation 两条方程，因此总回归方程数固定为 `128`。每个 `metric × threshold × window` 共享一个跨两层共同样本，因此样本标记总数固定为 `4 × 2 × 4 = 32`。

## 3. 方程口径
`D_w` 固定定义为：`v3pre30 -> D_v3pre30 = max(0,-spei1_mean_v3pre30)`，`v3he -> D_v3he = max(0,-spei2_mean_v3he)`，`hema -> D_hema = max(0,-spei2_mean_hema)`，`fullnew -> D_full = max(0,-spei6_mean)`。`W_w` 固定定义为同窗 wet 指标：`v3pre30 -> W_v3pre30`，`v3he -> W_v3he`，`hema -> W_hema`，`fullnew -> W_full`。热控制统一使用 full-season `hdd_ge32`，不切换到分窗版。其余 controls 统一为 `pr_sum et0_sum gdd_10_30 irr_frac aridity`。

mediator equation 固定为：

`M_dry = a1*D_w + a2*ca + a3*(ca×D_w) + rho1*M_wet + rho2*W_w + gamma*hdd_ge32/pr_sum/et0_sum/gdd_10_30/irr_frac/aridity + FE`

outcome equation 固定为：

`ln_yield = c1*D_w + c2*ca + c3*(ca×D_w) + b*M_dry + phi1*M_wet + phi2*W_w + gamma*hdd_ge32/pr_sum/et0_sum/gdd_10_30/irr_frac/aridity + FE`

## 4. dry-wet 配对
`M_dry` 与 `M_wet` 固定按同源、同窗、同 family 配对：`p10 -> p90`，`p20 -> p80`。对应关系为：`blduration_dry -> blduration_wet`，`bldurshare_dry -> bldurshare_wet`，`blseveritymean_ddf -> blseveritymean_wex`，`blseveritysum_ddf -> blseveritysum_wex`。Stata 中长变量名统一使用 `temp/stata_alias_map_v3.md` 对应的 alias。

## 5. 输出与验证
输出文件固定写到 `temp/2026-04-23_newSMsplit/`：`v6gleambl_analysis_ready.dta`、`v6gleambl_diagnostics.csv`、`v6gleambl_baseline_coefficients.csv`、`v6gleambl_bootstrap_iede_te.csv` 与 `logs/*.log`。bootstrap 只输出 `IE/DE/TE` 在 `ca P25/P50/P75` 下的结果，每个 baseline 规格 9 行，总计 `64 × 9 = 576` 行。实现后至少核对：128 个新变量存在、32 个样本标记生成、64 个 baseline 规格完整、bootstrap 表结构完整。
