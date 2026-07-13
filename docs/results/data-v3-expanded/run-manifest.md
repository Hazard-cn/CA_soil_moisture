---
layout: default
title: V3 expanded 运行 manifest
---

# V3 expanded 运行 manifest

运行 ID：`run-data-v3-expanded-20260423`。该节点为 `reconstructed/pre-git`，登记的是 2026-04-23 现存输出及 2026-07-14 的结构核验，不是伪造的历史 Git 快照。

| 项目 | 登记值 |
|---|---|
| 输入 artifact | `data-v1-locked-panel` |
| 样本规则 | `sample-data-v3-expanded-main`；主视图为 yield-present 69,038 行，完整构建另保留 no-yield 53,495 行 |
| 方法 | `method-data-v3-build` |
| 代码入口 | `repo://data_build/scripts/python/run_all.py` |
| 环境证据 | `repo://quality_reports/lineage/ENVIRONMENTS.md`；历史锁缺失，当前默认解释器缺少 rasterio |
| 可复现状态 | `historical_static`；验证现存文件，不重跑后冒充原始结果 |

## 输出清单

| Artifact | 物理视图 | SHA-256 | Rows | Columns | Ordered-schema SHA-256 |
|---|---|---|---:|---:|---|
| `data-v3-expanded-phenowindows` | 全部 phenology-window 行 | `8462ca3c10e8e15a7999de0b96937aef25c8ede031ec1e8cf268724b0fa36a15` | 122,533 | 1,679 | `cc1f4f5ec04628b12bb6d208634848008c5feff59f10235ef7e852aa15a36cd3` |
| `data-v3-expanded-main` | yield-present 主视图 | `1aed2f71427d379bf1a71fdce58904d806061842d644dc45d65638e763bab948` | 69,038 | 1,679 | `cc1f4f5ec04628b12bb6d208634848008c5feff59f10235ef7e852aa15a36cd3` |
| `data-v3-expanded-noyield` | yield-missing 视图；仍保留 1,679 列 | `13607be28e75a6846c412958851814dcbda4da200ee40d89c5ac3a340483f1ef` | 53,495 | 1,679 | `cc1f4f5ec04628b12bb6d208634848008c5feff59f10235ef7e852aa15a36cd3` |

三类输出只提交元数据，不提交 Parquet、DTA 或 CSV 数据文件。
