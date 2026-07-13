---
title: 2026 年 Git 前版本谱系重建与治理
status: active
created: 2026-07-14
scope_start: 2026-01-01
scope_end_exclusive: 2026-07-13
---

# 2026 年 Git 前版本谱系重建与治理

本任务采用非破坏性索引层：不删除、不移动、不改名历史文件，不上传数据或原始对话，只提交脱敏证据摘要、机器可读登记表和 Markdown 文档。2026-07-13 以前的版本统一标记为 `reconstructed/pre-git`，不伪造历史提交、tag 或 Release。

## 执行清单

- [x] 按 thread ID 去重并筛选 2026 年项目相关主任务与 sub-agent，生成脱敏对话和修改事件登记。
- [x] 迁移逻辑版本表，并建立 alias、artifact、data lineage、sample rule、method、analysis run 等规范化登记表。
- [x] 覆盖研究蓝图、V1/V2/V3、历史报告、机制分支、GGCP10、scale 搜索和 G185 方法线。
- [x] 为每个 canonical version 分别详细登记数据变化、方法变化和结果呈现变化，并生成逐版本变化说明。
- [x] 生成版本地图、数据谱系和不可恢复缺口文档，并更新项目入口和治理规则。
- [x] 实现 `version_lineage.py`、单元测试、CI schema/外键/发布边界校验和生成文档漂移检查。
- [ ] 完成两轮审查、验证、提交、推送、PR、CI、squash merge 和本地 fast-forward 同步。

## 证据纪律

- `three-source-confirmed`：至少三类独立证据一致，例如代码、结果或运行清单、对话或计划。
- `two-source-supported`：两类独立证据一致。
- `single-source-inferred`：只有一类直接证据或仅有文件时间。
- `missing-snapshot`：历史材料明确引用，但当前物理文件缺失或已被同名覆盖。
- 原始对话、JSONL、数据、日志、PDF、ZIP 和二进制结果不进入 Git。

## Git 交付

工作分支为 `work/reconstruct-2026-pre-git-lineage`。历史登记与文档、校验与 CI 分成两个逻辑提交；通过 PR 的 `integrity` 检查后 squash merge。工作分支、现有 tag、Release 和 Dependabot PR 均不删除或改写。

## 审查修正记录

提交前独立审查要求并已落实以下修正：按北京时间移除早于版本首证据日期的对话映射；excluded 任务不关联版本；采集器逐事件执行截止日过滤；补丁正文、完整命令和绝对路径不进入登记表；URI 解析限制在允许根目录；歧义 alias 不再静默解析；六个 current 类节点补齐输入、样本、方法、入口、manifest、环境证据和 GitHub 可读结果；V3 两类 hot-dry、V1/GGCP10 yield 分母、bootstrap 次数及 layout-only v5 后缀分别登记。

## Post-Deploy Monitoring & Validation

本仓库没有在线生产服务。合并后只需验证 GitHub Actions `integrity` 仍为成功、GitHub Markdown 链接可打开、本地 `main`/`origin/main`/GitHub 默认分支 SHA 一致、工作树清洁、工作分支仍保留，并确认 Dependabot PR #2/#3、既有 tag 和 Release 未发生变化。
