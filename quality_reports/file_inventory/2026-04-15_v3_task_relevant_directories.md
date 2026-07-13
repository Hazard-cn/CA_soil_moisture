# V3 任务相关目录清单

本清单列的是“目录”和“目录用途”，不是逐文件索引。逐文件索引继续看 [2026-04-09_dialogue_task_file_inventory.md](C:/YangSu/00_Project/CA_mechanism/regression_SR/quality_reports/file_inventory/2026-04-09_dialogue_task_file_inventory.md)。

## 项目根目录

- [regression_SR](C:/YangSu/00_Project/CA_mechanism/regression_SR)
  当前项目根目录。接手时所有相对路径都以这里为起点。

## 数据与变量说明

- [docs](C:/YangSu/00_Project/CA_mechanism/regression_SR/docs)
  项目级文档目录，含变量说明和数据来源。

- [VARIABLES.md](C:/YangSu/00_Project/CA_mechanism/regression_SR/docs/VARIABLES.md)
  旧版变量字典，主要对应更早的数据结构。接手时不能把它当成当前 `v3` 全部变量的唯一权威来源。

- [DATA_SOURCES.md](C:/YangSu/00_Project/CA_mechanism/regression_SR/docs/DATA_SOURCES.md)
  数据来源英文说明。

- [DATA_SOURCES_CN.md](C:/YangSu/00_Project/CA_mechanism/regression_SR/docs/DATA_SOURCES_CN.md)
  数据来源中文说明。

- [data/processed](C:/YangSu/00_Project/CA_mechanism/regression_SR/data/processed)
  当前分析面板和各任务链生成的 analysis-ready 数据所在目录。

## 代码目录

- [scripts](C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts)
  代码总目录。

- [scripts/stata](C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata)
  Stata 主代码目录，当前任务链的主回归都在这里。

- [scripts/R](C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/R)
  R 辅助代码目录，主要负责系数图和报告用图。

## 当前四个主任务链

- [scripts/stata](C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata)
  `v3prhd_*`：SR 与复合热干旱对产量的四规格四切分回归。

- [scripts/stata](C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata)
  `v3prhdsm_*`：把因变量换成 Soil Moisture 的 spec2/spec3/spec4 结果。

- [scripts/stata](C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata)
  `v3decomp_*`：FE decomposition equation，拆分 direct buffering 与 SM-mediated component。

- [scripts/stata](C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata)
  `v3sub_*`：按灌溉和玉米产区重跑的子样本结果。

## 结果目录

- [output](C:/YangSu/00_Project/CA_mechanism/regression_SR/output)
  结果总目录。

- [output/tables](C:/YangSu/00_Project/CA_mechanism/regression_SR/output/tables)
  回归长表、宽表、bootstrap summary、子样本结果表都在这里。

- [output/figures](C:/YangSu/00_Project/CA_mechanism/regression_SR/output/figures)
  当前可直接引用的核心图基本都在这里，尤其是 `v3prhd_*`、`v3prhdsm_*`、`v3decomp_*` 的主图。

- [output/reports](C:/YangSu/00_Project/CA_mechanism/regression_SR/output/reports)
  各阶段 beamer/Rmd/tex/pdf 都在这里。当前综合汇报也在这里。

- [output/logs](C:/YangSu/00_Project/CA_mechanism/regression_SR/output/logs)
  当前任务链对应的 Stata log 在这里。接手排错优先看这里，而不是项目根目录那些更早的旧 log。

## 质量与交接文档

- [quality_reports](C:/YangSu/00_Project/CA_mechanism/regression_SR/quality_reports)
  计划、交接、文件清单和 session 说明的目录。

- [quality_reports/plans](C:/YangSu/00_Project/CA_mechanism/regression_SR/quality_reports/plans)
  近期任务计划文件，接手前建议先看 2026-04-07 到 2026-04-15 这一段。

- [quality_reports/file_inventory](C:/YangSu/00_Project/CA_mechanism/regression_SR/quality_reports/file_inventory)
  文件级清单目录，包括本轮新增的目录清单和之前的逐文件清单。

- [quality_reports/handoffs](C:/YangSu/00_Project/CA_mechanism/regression_SR/quality_reports/handoffs)
  任务交接文档目录，本轮新增。
