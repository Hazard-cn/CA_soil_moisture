# SR方法组合GitHub网页端阅读包发布计划

- 日期：2026-07-17
- 工作分支：`work/sr-github-web-reader`
- 基线：最新`origin/main`
- 拟新增canonical ID：`report-sr-method-portfolio-web-reader-v1`
- 目标：在公开GitHub仓库提供一个可由GPT网页端直接读取的统一入口，集中呈现三个实证方向、37篇文献的方法索引、外部审阅修正、数据与estimand边界及后续brainstorm任务。

## 发布范围

发布内容限于Markdown和既有自包含HTML。入口目录为`docs/results/report-sr-method-portfolio-web-reader-v1/`，并更新`docs/results/index.md`、`docs/results/README.md`和仓库文档入口。三个既有方向的完整报告继续保留在各自canonical目录；新入口提供状态总览、外部审阅后的解释更新和相对链接，不覆盖历史报告。

37篇文献只发布已核验的书目排序、方法学习点、代码状态、Zotero核验边界和方法模块映射。第三方全文、第三方代码、原始RIS、Zotero数据库和浏览器会话不进入Git。

## 数据与安全边界

不提交原始或处理中间数据、CSV/DTA/Parquet、PNG/PDF、压缩包、日志、模型对象、bootstrap draws、缓存、原始对话、完整命令或机器绝对路径。机器结果只以既有公共报告和新建Markdown摘要呈现。现有观察性结果继续限定为条件关联；IE、DE、TE继续限定为两方程代数组件。

## 版本与谱系

新增报告呈现版本，但不改变数据、样本、estimand、模型、推断或任何机器结果。同步更新`quality_reports/version_registry.csv`和必要的artifact元数据，并使用`version_lineage.py build-docs`重建`VERSION_MAP.md`、`VERSION_CHANGELOG.md`和`DATA_LINEAGE.md`。本版本的context IDs为三个override方向，不取代任何方向性canonical结果。

## 审核与验收

1. 核验所有相对链接、Markdown编码和自包含HTML资源。
2. 核验37篇条目数、代码状态计数和关键结果数字与来源材料一致。
3. 执行仓库政策检查、版本谱系严格校验、文档重建check和相关Python测试。
4. 由独立代理分别完成研究事实审核、GitHub可读性审核和仓库政策审核；Critical或Major未关闭前不提交。
5. 提交后推送分支、创建PR、等待CI通过并squash merge；最后从公开GitHub URL重新读取入口文件。

## 停止条件

若发现待发布内容含未脱敏路径、不可公开材料、无法追溯的关键数值、失效内部链接、仓库政策失败或版本谱系不一致，则停止发布并修正；不以删除历史报告或降低检查标准作为解决方式。
