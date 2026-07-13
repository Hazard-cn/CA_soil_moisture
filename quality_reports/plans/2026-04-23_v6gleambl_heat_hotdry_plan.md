## 任务
在现有四窗 GLEAM、11 类 `M_dry`、保留 `W_w` 且去掉 `M_wet` 的口径上，再各跑两套独立 baseline。

## 规格一：Heat 替代 Drought 主位置
- 主暴露：`hdd_ge32`
- 交互项：`SR_x_Heat_full = ca * hdd_ge32`
- `D_w` 仅作 control，不保留 `SR_x_D_w`
- `W_w` 保留为 control
- full-season controls 继续保留：`pr_sum et0_sum gdd_10_30 irr_frac aridity`
- 输出独立保存为 `v6gleambl_heatctrl_*`

## 规格二：HotDryPr 替代 Drought 主位置
- 主暴露：`HotDryPr_w`
- 其中：
  - `v3pre30 -> HotDryPr_v3pre30 = hotdrydays_ge32_pr_lt1_v3pre30`
  - `v3he -> HotDryPr_v3he = hotdrydays_ge32_pr_lt1_v3he`
  - `hema -> HotDryPr_hema = hotdrydays_ge32_pr_lt1_hema`
  - `fullnew -> HotDryPr_full = hotdrydays_ge32_pr_lt1`
- 交互项：`SR_x_HotDryPr_w = ca * HotDryPr_w`
- controls 中加入 `D_w`、`hdd_ge32`、`W_w`
- full-season controls 继续保留：`pr_sum et0_sum gdd_10_30 irr_frac aridity`
- 输出独立保存为 `v6gleambl_hotdryctrl_*`

## 共通设置
- `M_dry` 仍覆盖 11 类，规格总数仍为 `88`
- 方程仍分 `mediator` 与 `outcome`
- 固定效应：`absorb(grid_id year)`
- 聚类：`vce(cluster grid_id)`
- 本轮不跑 bootstrap

## 验证
- `heatctrl` 与 `hotdryctrl` 各自产生独立的 analysis-ready、diagnostics、baseline coefficients
- 两套结果都应为 `88` 个规格
- `heatctrl` 结果中不应出现 `M_wet` 或 `SR_x_D_w`
- `hotdryctrl` 结果中不应出现 `M_wet`，且主暴露应为 `HotDryPr_*` 与 `SR_x_HotDryPr_*`
