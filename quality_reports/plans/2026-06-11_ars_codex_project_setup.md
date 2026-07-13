# ARS Codex 项目配置计划

日期：2026-06-11

## 目标

在 `C:\YangSu\00_Project\CA_mechanism\regression_SR` 根项目中配置 Codex 原生 Academic Research Skills，使当前项目可发现并调用 `academic-research-suite`，同时保留已有 Claude Code ARS 配置。

## 实施步骤

1. 核对 ARS Codex 官方仓库、发布标签和技能目录结构。
2. 将 `Imbad0202/academic-research-skills-codex` 的 `skills/academic-research-suite` 安装至项目根目录 `.agents/skills/`。
3. 检查 `SKILL.md`、引用文件和脚本是否完整。
4. 执行技能自带验证或最小结构检查，并记录版本与安装路径。

## 边界

- 不删除或覆盖 `.claude/skills/` 中的现有 ARS 配置。
- 不修改研究数据、脚本或既有分析输出。
- 不执行 ARS 研究流水线，仅验证项目级技能安装和发现条件。

## 验收标准

- `.agents/skills/academic-research-suite/SKILL.md` 存在且可读取。
- 安装内容对应官方 Codex 发行版 `v0.1.11`。
- 技能所需的本地引用和脚本通过结构检查。
- 明确记录重新启动 Codex 后的发现要求。
