# 贡献与 Git 工作流

本仓库采用单人维护、自动化 Git/GitHub 工作流。`main` 只保存通过仓库检查的稳定状态；常规变更使用 `work/<topic>` 分支，通过 Pull Request 以 squash 方式合并。

## 提交范围

代码、项目文档、版本登记和公开结果可以进入 Git。任何原始数据、中间数据、缓存、日志、模型对象、图片、压缩包、Office/PDF 文件和运行目录均不得提交。正式结果只允许放在 `docs/results/`，默认使用 Markdown；只有在 CSS、JavaScript 和图片均内嵌、不依赖本地文件时才使用 HTML。

## 版本要求

涉及数据口径、样本、估计量、固定效应、聚类层级、核心结论或解释边界的变更，必须同时检查 `docs/VERSIONING.md` 和 `quality_reports/version_registry.csv`。`report-v3`、`data-v3`、`analysis-v3` 和 `g185-response-surface-v3` 属于不同命名空间，不得简写为无法区分含义的 `v3`。

## 提交与合并

提交信息使用 `type(scope): subject`，例如 `analysis(g185): 修正区域TE口径`、`docs(versioning): 登记G185并行方法线` 或 `ci(policy): 阻止数据文件进入Git`。Pull Request 必须通过 `integrity` 检查；单人仓库不要求外部审批，但未通过检查的 PR 不合并。合并后的远端工作分支默认保留，删除仍按项目的单独明确授权规则执行。

## 本地检查

首次使用本工作树时执行 `git config core.hooksPath .githooks`，此后 pre-commit 钩子检查暂存快照，pre-push 钩子检查当前 `HEAD`。钩子和 CI 读取 Git 对象，不读取可能与暂存内容不同的工作树版本。

```powershell
python .github/scripts/check_repository_policy.py --source index
git diff --cached --check
git status --short --branch
```

完整 Stata 回归依赖本地许可和未公开数据，因此不在 GitHub-hosted runner 上执行；GitHub Actions 只执行发布政策、Python AST 和 R 语法检查。
