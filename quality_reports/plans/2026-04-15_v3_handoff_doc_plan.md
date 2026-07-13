# V3 任务交接文档与目录清单计划

## Summary

- 生成一份“相关目录清单”，把代码、数据、变量说明、结果、图、报告、日志和质量文档的目录层级列清楚。
- 生成一份“任务交接文档”，说明当前任务链在做什么、四个主要模块分别对应什么问题、主数据和主报告在哪里、以及接手时最容易踩到的共性问题。
- 不修改任何现有回归结果，只新增文档。

## Deliverables

- `quality_reports/file_inventory/2026-04-15_v3_task_relevant_directories.md`
- `quality_reports/handoffs/2026-04-15_v3_task_handoff.md`

## Key Points

- 以当前有效的 `v3prhd / v3prhdsm / v3decomp / v3sub` 任务链为主，不把更早的 `v1 / v2` 混成同一条主线。
- 目录清单按“用途”而不是按时间排序，方便接手人快速定位。
- handoff 文档要明确写出变量定义口径的真实来源分散在脚本和报告里，而不是只靠 `docs/VARIABLES.md`。
- handoff 文档要总结共性问题：变量口径漂移、编码与中文显示、报告版本过多、RHS 是否含 `W`、以及最终主版本识别。

## Verification

- 新增的两个 Markdown 文件均能打开，路径无误。
- 文档中提到的关键文件路径均存在。
