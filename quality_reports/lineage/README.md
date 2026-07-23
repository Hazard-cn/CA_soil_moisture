# 版本谱系登记接口

本目录保存 2026-07-13 以前研究版本的非破坏性重建索引，也允许人工登记Git后的范围化用户授权决策。CSV只包含元数据和脱敏证据，不包含数据、用户原话、原始对话、完整命令、日志或二进制结果；Git后决策不得由Git前会话收集器自动生成。

## 表间关系

- `version_aliases.csv`：把容易混淆的显示名映射到 canonical ID。
- `artifact_registry.csv`：登记数据、代码、结果、报告、计划等物理或逻辑 artifact。
- `data_lineage.csv`：登记数据 artifact 之间的输入—输出转换。
- `sample_rules.csv`：冻结 `main_sample` 和 Gxxx 等虚拟样本的谓词、规则向量与计数。
- `method_registry.csv`：登记 estimand、outcome、exposure、mediator、controls、固定效应和推断方式。
- `analysis_runs.csv`：把输入 artifact、sample rule、method、代码入口和结果 manifest 绑定为一次运行。
- `conversation_registry.csv`：保存与项目相关任务的thread元数据、决策摘要和evidence level；Git后授权必须使用`included:post-git-user-decision;decision_id=...`并标记`direct-user-confirmed`。
- `change_events.csv`：保存脱敏修改事件、规范化目标和完整命令的 SHA-256，不保存命令原文。

逻辑版本主表仍位于 `quality_reports/version_registry.csv`。每个版本必须分别填写数据变化、方法变化和结果呈现变化；详细的人类可读展开由 `docs/VERSION_CHANGELOG.md` 自动生成。

`analysis_runs.csv` 的 `planned_not_run` 表示尚未开始的计划运行，其 `result_manifest`、`public_result`、`code_git_sha`、`run_started_at`、`run_completed_at` 必须全部为空。`failed_quality_gate` 表示由已登记 Git 代码启动并留下物理运行证据，但未通过独立质量门；它要求合法的 `code_git_sha` 和带时区的 ISO `run_started_at`，同时要求 `result_manifest`、`public_result`、`run_completed_at` 为空。该状态不等于某个 pipeline stage 执行失败，也不构成可发布结果。

`sample_rules.csv` 中的行数、grid 数和区域计数统一表示规则 mask 的原始支持，不是某一回归的 `e(sample)` 或 Python complete-case 数。模型因 exposure、mediator、control 或固定效应变量缺失而进一步删减的样本，应登记在运行 manifest 或结果表中，不得回写覆盖冻结的规则计数。G057 和 G049 的区域回归 complete-case 尤其小于其 raw support；B067/G195 的 42,187 行和 11,775 grids 也是 `before_dropna` 口径。

## URI 和证据规则

- `repo://`：相对于仓库根目录的路径；可以是 tracked 文件，也可以是按政策忽略的数据位置。
- `local://`：仅本机保存、不会进入 Git 的项目内运行产物。
- `external://`：项目目录之外的数据或资料逻辑标识，不保存机器绝对路径。
- `three-source-confirmed`：至少三类独立证据一致。
- `two-source-supported`：两类独立证据一致。
- `single-source-inferred`：只有一类直接证据或文件时间。
- `missing-snapshot`：历史材料明确引用，但当前快照缺失或已被同名覆盖。

## 命令

```powershell
python scripts/python/version_lineage.py validate --strict
python scripts/python/version_lineage.py validate --strict --verify-local
python scripts/python/version_lineage.py build-docs
python scripts/python/version_lineage.py build-docs --check
```

对话候选收集必须写入 Git 忽略目录，并经过脱敏审阅后才能更新正式登记：

```powershell
python scripts/python/version_lineage.py collect-conversations `
  --sessions-root "$HOME/.codex/sessions" `
  --output-dir "quality_reports/scratch/pre_git_conversation_candidates"
```
