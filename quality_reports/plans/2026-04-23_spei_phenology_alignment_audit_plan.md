# 2026-04-23 SPEI 物候对应性检查计划

## 任务

检查 `data_build/scripts/python` 中 SPEI 相关变量的生成逻辑，并判断其时间窗口是否与实际物候期对应。

## 范围

- 物候窗口定义：`data_build/scripts/python/s01_load_phenology.py`
- SPEI 生成逻辑：`data_build/scripts/python/s06_calc_vpd_spei.py`
- 佐证文档：`data_build/docs/CHANGELOG.md`
- 实际核验对象：`data_build/data/intermediate/panel_windows.csv`

## 执行步骤

1. 读取 `s01_load_phenology.py`，确认窗口边界是否由逐格点逐年份的 `v3_doy`、`he_doy`、`ma_doy` 生成。
2. 读取 `s06_calc_vpd_spei.py`，确认 SPEI 是否按日权重聚合，还是按起止月与累计尺度做终止月提取。
3. 基于 `panel_windows.csv` 统计每个窗口的实际 DOY 长度、对应月份跨度、整月包络长度与额外覆盖天数。
4. 对照 `CHANGELOG.md`，确认当前实现是否刻意追平旧版 `SPEI_season` 口径。

## 核验结果

- 窗口边界与实际物候期对应。`full`、`v3pre30`、`v3pm10`、`hepm10`、`v3he`、`hema` 均直接由逐格点逐年份的 `V3/HE/MA` DOY 定义。
- SPEI 取值不是按实际窗口天数聚合，而是把每个窗口先映射到起止月份，再用 `scale = end_month - start_month + 1` 提取 `end_month` 的 `SPEI-scale` 单点值。
- 因此，SPEI 的“中心时间范围”与物候阶段方向一致，但“覆盖边界”通常宽于真实物候窗口，因为它包含起始月月初到终止月月末的整月累计信息。

## 量化摘要

基于 `panel_windows.csv` 的统计结果：

- `full` 实际平均 146.18 天，但对应整月包络平均 178.58 天，平均多覆盖 32.40 天。
- `v3pre30` 实际平均 31.00 天，整月包络平均 60.58 天，平均多覆盖 29.58 天。
- `v3pm10` 实际固定 21 天，整月包络平均 51.64 天，平均多覆盖 30.64 天。
- `hepm10` 实际固定 21 天，整月包络平均 54.92 天，平均多覆盖 33.92 天。
- `v3he` 实际平均 67.69 天，整月包络平均 100.10 天，平均多覆盖 32.41 天。
- `hema` 实际平均 49.49 天，整月包络平均 79.31 天，平均多覆盖 29.82 天。

补充检查：

- 各窗口起点恰好落在月初的占比仅约 1.9% 至 4.2%。
- 各窗口终点恰好落在月末的占比仅约 1.5% 至 3.6%。
- 窗口起止同时严格贴合整月边界的占比接近 0；例如 `full` 仅 0.08%，`v3pm10` 与 `hepm10` 为 0。

## 当前判断

当前脚本在“是否使用实际物候信息定义窗口”这一层面是对应的；但在“是否严格按实际物候天数生成 SPEI 暴露”这一层面并不严格对应，而是采用了与旧版 `SPEI_season` 一致的月尺度近似口径。
