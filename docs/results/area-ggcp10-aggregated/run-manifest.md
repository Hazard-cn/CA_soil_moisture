---
layout: default
title: GGCP10 aggregated 运行 manifest
---

# GGCP10 aggregated 运行 manifest

运行 ID：`run-area-ggcp10-aggregated-20260518`。原始数据与输出仅登记元数据，不进入 Git。

| 项目 | 登记值 |
|---|---|
| 输入 artifacts | `ggcp10-raw-harvarea-raster-series`、`data-v3-analysis-ready`、`data-v1-county-city` |
| 样本规则 | `sample-data-v3-expanded-main`；基于 69,038 行 yield-present 主面板连接面积信息 |
| 方法 | `method-ggcp10-aggregate-build` |
| 代码入口 | `repo://scripts/python/ggcp10_build_harvarea_agg_branch.py` |
| 环境证据 | `repo://quality_reports/lineage/ENVIRONMENTS.md`；历史锁缺失，当前默认解释器缺少 rasterio |
| 可复现状态 | `historical_static` |

| Artifact | SHA-256 | Rows | Columns | Ordered-schema SHA-256 |
|---|---|---:|---:|---|
| `ggcp10-aggregated-sidecar` | `09839e53ce0c2aad6455abc9abf788059a3fb8083cc8905cb554f368de335e2c` | 69,038 | 10 | `21758f77d77a96d5885618bfb90b0c492f2a520a30a8a7d0d196834adf1151cc` |
| `ggcp10-aggregated-base` | `be86cba153311b354d5b5c2a2cadf7618ebb64532f24a645a9eee0b8b8a548b4` | 69,038 | 783 | `bc6312c27f225b194b74477865cb8a8ce200f67d972ee019503afc180c372bf5` |
