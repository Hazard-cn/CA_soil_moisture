---
layout: default
title: G185 frozen sample 运行 manifest
---

# G185 frozen sample 运行 manifest

运行 ID：`run-scale-g185-freeze-20260611`。

| 项目 | 登记值 |
|---|---|
| 输入 artifacts | `ggcp10-baseline-suite`、`data-v3-expanded-main-dta` |
| 样本规则 | `sample-g185` |
| 规则向量 | `main_sample + yield_domain + yield_jump + sm_sd` |
| 固定计数 | 46,299 行；13,236 grids |
| 方法 | `method-scale-g185-freeze` |
| 代码入口 | `repo://scripts/python/expanded_scale_story_search.py` |
| 环境锁 | `repo://requirements-g185-lock.txt`；2026-07-14 当前核验快照，不冒充 2026-06-11 历史环境 |
| 公开结果 | `repo://docs/results/scale-search-region-first/report.md` |
| 可复现状态 | `verified_current`；规则和计数已重算，未导出行级样本 |

如规则向量或固定计数变化，必须创建新的 scale ID，不能覆盖 G185。
