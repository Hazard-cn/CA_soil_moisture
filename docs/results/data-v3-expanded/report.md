---
layout: default
title: V3 expanded 数据版本说明
---

# V3 expanded 数据版本说明

## 数据变化

V3 expanded 以 `data-v1-locked-panel` 为基础输入，形成 phenowindows、yield-present main 和 yield-missing no-yield 三个物理视图。V2 已存在基于 GLEAM root-zone soil moisture 阈值的 hot-dry；V3 保留并扩展 GLEAM、SWSM、ERA5-Land 的多源、多深度 soil-moisture-threshold hot-dry，同时另行新增以 `pr_lt1` 为阈值的 precipitation hot-dry。两类变量的暴露定义不同，不能合并解释。

## 方法变化

构建方法从单一 analysis-ready 面板扩展为按物候窗口生成的多源气候与土壤水分特征流水线，并在导出阶段保留 yield-present 与 yield-missing 两个互斥视图。现存数据通过 SHA-256、行列数、ordered schema、`grid_id year` 无缺失及唯一性核验；历史环境锁缺失，因此不声称已经从头重跑复现。

## 结果呈现变化

本版本的公开结果不包含行级数据，而是以 [运行 manifest](run-manifest.md) 和谱系登记表呈现三个输出的精确哈希、结构与用途。no-yield 视图明确登记为 53,495 行、1,679 列，而不是删除 yield 列后的窄表。
