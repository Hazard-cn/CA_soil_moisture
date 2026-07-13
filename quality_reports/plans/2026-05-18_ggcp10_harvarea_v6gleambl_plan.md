# GGCP10 种植面积独立分支更新方案

## Summary
- 保留现有 `v3/v6` 结果不动，新增基于 `GGCP10_HarvArea_2010-2020` 的独立 harvest-area 分支。
- 以 Python + `rasterio` 读取 `2016-2019` 年 `HarvArea_Maize_*.tif`，生成与现有 `grid_id-year` 面板对齐的面积 sidecar。
- 新回归结果统一写入 `temp/2026-05-18_ggcp10_harvarea_v6gleambl/`。

## Key Changes
- 新增 GGCP10 面积 sidecar，单位从 `thousand ha` 转为 `km2`。
- 新建 harvest-area 版 `v3_analysis_ready` 底座，并同步更新 `maize_area_km2`、`maize_yield_km2`、`yield_tons_ha`、`ln_yield`。
- 保留现有 `maize_frac` 原义，另增 `ggcp10_maize_frac`。
- 复制最近的 `v6gleambl` 链到独立分支，不覆盖旧结果。

## Tests
- 检查 GeoTIFF 存在、CRS、nodata、唯一键、单位换算和恒等式。
- 比较新旧样本、面积、产量分布。
- 重跑 harvest-area 版 `v6gleambl`，其中 bootstrap 仅做 `20 reps` smoke test；核对日志 `COMPLETE`、结果文件和新旧系数差异。
