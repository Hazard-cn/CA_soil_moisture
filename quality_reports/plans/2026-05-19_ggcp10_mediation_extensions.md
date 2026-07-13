# 2026-05-19 GGCP10 mediation extensions plan

## Goal

在 GGCP10 聚合面积版底座上，继续扩展三条相互独立的中介分析分支：

1. `SM mean`
2. `SM wet-state mirror`
3. `SM dry-state top-3`

## Shared conventions

- 数据源只使用 GLEAM。
- 外生胁迫继续分为：
  - `Drought`
  - `Heat`
  - `HotDry`
- 固定效应维持 `grid_id + year`。
- 标准误按 `grid_id` 聚类。
- 三条分支独立落地在：
  - `temp/2026-05-19_ggcp10_mediation_extensions/mean/`
  - `temp/2026-05-19_ggcp10_mediation_extensions/wet_mirror/`
  - `temp/2026-05-19_ggcp10_mediation_extensions/dry_top3/`

## Branch A: SM mean

- GLEAM-Sfc 与 GLEAM-Root。
- 四个窗口：
  - `v3pre30`
  - `v3he`
  - `hema`
  - `fullnew`
- 产出：
  - baseline coefficients
  - IE / DE / TE bootstrap
  - irrigation heterogeneity
  - maize-zone heterogeneity
  - 单独在线文档

## Branch B: SM wet-state mirror

- 镜像当前 dry full-family 文档结构。
- 使用 wet-side GLEAM metric family。
- fullnew only。
- 产出：
  - baseline coefficients
  - 单独在线文档

## Branch C: SM dry-state top-3

- 先基于 full-family baseline 结果按理论符号稳定性筛选最优变量。
- 初始评分规则：
  - `a1` 预期为正
  - `a3` 预期为负
  - `b` 预期为负
  - 同时统计跨 `Drought / Heat / HotDry` 的显著性与符号一致性
- 产出：
  - top-3 selection table
  - top-3 bootstrap
  - irrigation heterogeneity
  - maize-zone heterogeneity
  - 单独在线文档

## Verification

- 所有日志以 `COMPLETE` 结束。
- 每条分支的结果表、图和文档地址齐全。
- `SM mean` 四窗口均完整覆盖。
- `wet-state mirror` 与 dry 文档在结构上可一一对应。
- `dry top-3` 的入选变量有可复核的评分表。
