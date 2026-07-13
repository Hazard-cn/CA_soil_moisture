# Git 初始化与远端推送计划

日期：2026-07-13

## 目标

将当前工作库初始化为本地 Git 仓库，并将适合公开版本控制的代码、项目文档、质量计划、规格说明与交接文档首次推送至 `Hazard-cn/CA_soil_moisture` 的 `main` 分支。

## 公开范围

纳入版本控制的主要内容为 `scripts/`、`data_build/scripts/`、`docs/`、`templates/`，以及 `quality_reports/` 下的 `plans/`、`specs/`、`handoffs/`、`file_inventory/` 和版本登记文件。数据文件、模型输出、图表、运行日志、临时目录、本地虚拟环境、代理配置、会话记录、文献缓存与压缩包不进入首次公开提交。

## 执行步骤

1. 创建 `.gitignore` 与 `.gitattributes`，明确公开范围、行尾处理和二进制文件规则。
2. 使用 `main` 作为初始分支，在仓库范围内配置 GitHub noreply 提交身份，并设置 `origin`。
3. 暂存文件后检查文件数量、总体积、禁止路径、凭据模式和空白字符提示。
4. 创建首次提交，通过 Git Credential Manager 完成 GitHub 授权并推送 `main`。
5. 复核远端分支指向、提交哈希、上游跟踪关系与本地工作区状态。

## 验收标准

- 远端 `refs/heads/main` 与本地 `HEAD` 指向同一提交。
- 本地 `main` 跟踪 `origin/main`。
- 首次提交不包含 `data/`、`temp/`、`output/`、虚拟环境、会话日志和本地代理配置。
- 暂存内容未发现常见令牌、私钥或密码赋值模式。
- 推送完成后工作区无未提交的本次变更。
