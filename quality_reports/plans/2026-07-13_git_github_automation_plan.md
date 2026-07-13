# Git 与 GitHub 自动化治理实施计划

日期：2026-07-13

## 目标

在不上传任何具体数据的前提下，将仓库配置为可自动执行分支、提交、推送、Pull Request、合并、标签和发布的单人研究仓库。正式结果仅允许使用 GitHub 可直接审阅的 Markdown，或无外部本地依赖的自包含 HTML。

## 已确认决策

- 数据、运行缓存、中间产物和二进制分析文件不进入 Git。
- `docs/results/` 是唯一正式结果发布目录。
- Markdown 是默认结果格式；需要保留完整样式或交互内容时使用自包含 HTML。
- `main` 保存稳定状态；后续任务默认使用 `work/<topic>` 分支，通过 PR 和自动检查后 squash 合并。
- 非破坏性 Git/GitHub 操作可自动执行；文件删除、历史改写和 force push 继续遵守项目的明确授权规则。
- 历史 V1-V6、GGCP10、G057/G185 等版本依据现有文件证据登记，不伪造历史 Git commit。

## 实施步骤

1. 创建工作分支并补强 `.gitignore`，增加本地凭据、更多数据格式及 `docs/results/` 白名单。
2. 新增仓库政策检查脚本，拒绝数据目录、数据扩展、过大文件、目录外 HTML 和常见凭据模式。
3. 新增 GitHub Actions，对发布政策、Python AST 和 R 语法进行无数据检查；不在托管 runner 上运行依赖数据和 Stata 许可证的完整分析。
4. 新增 Dependabot、CODEOWNERS、PR 模板和 Issue Forms。
5. 新增 `docs/VERSIONING.md` 与 `quality_reports/version_registry.csv`，将报告版、数据版、分析版、机制实验、面积/样本 scale 和 G185 方法版分开登记。
6. 新增 `docs/results/README.md`，更新根 README 和 AGENTS 中的 Git 自动化、结果发布和版本规则。
7. 在本地运行政策检查、Python/R 语法检查、Git 范围检查和空白检查。
8. 提交并推送工作分支，确认首次 CI 成功后创建并合并 PR。
9. 配置 GitHub 仓库说明、topics、squash-only、自动合并、保留远端工作分支、Issues/Projects/Wiki、安全更新和 Pages。
10. 创建 `main` ruleset，要求 PR、线性历史和 `integrity` 检查，并禁止分支删除和 force push。
11. 建立当前治理基线标签，复核本地 HEAD、远端 main、GitHub API、Actions、Pages 和 ruleset。

## 验收标准

- `git ls-files` 中不存在数据目录、运行目录、数据格式或发布目录外 HTML。
- `docs/results/` 中只有 `.md` 和 `.html`，HTML 不引用本地绝对路径或被忽略的本地资源。
- Python 和 R 源文件均能完成语法解析；CI `integrity` 成功。
- `main` 只能通过满足检查的 PR 更新，并禁止删除和 force push。
- 远端仓库设置与本地治理文档一致。
- 历史版本登记明确区分已确认、混合证据和推断关系。
