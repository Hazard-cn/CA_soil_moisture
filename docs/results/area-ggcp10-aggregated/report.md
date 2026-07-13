---
layout: default
title: GGCP10 aggregated 数据版本说明
---

# GGCP10 aggregated 数据版本说明

## 数据变化

该版本将 GGCP10 原生 1/12° maize harvested-area raster 按面积守恒方式聚合到 0.1° grid-year 面板，并生成 10 列 sidecar 与 783 列分析面板。`yield_tons_ha` 的分子仍为 `maize_prod`，但分母改为 `ggcp10_maize_area_km2`，即 `maize_prod / ggcp10_maize_area_km2 * 10`；V1-family 使用 `maize_area_km2`，两者不是同一结果变量快照。

## 方法变化

方法从 point-sample 面积值改为 overlap-area aggregation，减少像元中心抽样对边界 grid 的依赖。连接键为 `grid_id year`，当前仅对既有 sidecar 和分析面板做结构与哈希核验；原始 2026-05-18 环境锁缺失。

## 结果呈现变化

公开材料以 [运行 manifest](run-manifest.md) 呈现输入、样本、方法、代码入口、环境缺口及输出校验值，不发布 raster、DTA 或行级 sidecar。
