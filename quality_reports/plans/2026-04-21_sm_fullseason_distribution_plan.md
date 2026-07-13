# 2026-04-21 Full-Season SM 分布图计划

## 目标
基于 `temp/2026-04-21_sm_state_audit/sm_state_analysis_ready.dta`，在 `state_full_6_sample==1` 的共同样本上，按数据源与层级分别绘制 6 个 full-season raw soil moisture 分布图。

## 口径
- 样本：`state_full_6_sample==1`
- 变量：
  - `gleam_sms_mean`
  - `gleam_smrz_mean`
  - `swsm_l1_mean`
  - `swsm_l3_mean`
  - `era5l_swvl1_mean`
  - `era5l_swvl3_mean`
- 输出目录：`temp/2026-04-21_sm_state_audit/`

## 实施
- 新增 `scripts/python/v4smstate_plot_fullseason_distributions.py`
- 生成 6 张单图，文件名按 `sm_full_dist_<source-layer>.png`
- 额外生成 1 张 `2x3` 面板图，文件名为 `sm_full_dist_6panel.png`
- 图内显示 histogram、density-normalized y-axis、mean、P25/P50/P75 参考线

## 验证
- 读取后确认 6 个变量在 `state_full_6_sample==1` 下无缺失
- 脚本运行成功并写出 7 张 PNG
- 文件存在且大小非零
