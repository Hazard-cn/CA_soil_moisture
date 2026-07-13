# V3 任务交接文档

## 1. 这条任务链现在在做什么

当前这条任务链不是在维护最早的 `v1` 或 `v2` 结果，而是在 `v3` 面板上围绕四个连续扩展模块推进：

1. `v3prhd`
   研究 SR 是否改变“复合热干旱”条件下的产量损失斜率。这里的核心已经从早期 `D × H` 扩展成了基于降水定义的 `HotDryPr`。

2. `v3prhdsm`
   把因变量从 `Yield` 换成 `Soil Moisture`，用 6 个 SM outcome 检查前面那套交互结构在不同数据源和层级上是否存在对应关系。

3. `v3decomp`
   在 panel FE 框架下，把 `SR` 对产量损失缓解拆成两部分：
   - direct buffering component
   - SM-mediated component

4. `v3sub`
   按灌溉和玉米产区分组，重跑三结构和窗口分析，检查结果是否依赖样本边界。

当前已经完成的“综合汇总入口”是 [v3_dialogue_integrated_beamer.pdf](C:/YangSu/00_Project/CA_mechanism/regression_SR/output/reports/v3_dialogue_integrated_beamer.pdf)。如果接手人只想先看一份总览，先从这里开始。

## 2. 当前主文件和主版本怎么认

### 主数据

- 基础 `v3` 面板： [v3_analysis_ready.dta](C:/YangSu/00_Project/CA_mechanism/regression_SR/data/processed/v3_analysis_ready.dta)
- 模块级 analysis-ready：
  - [v3prhd_analysis_ready.dta](C:/YangSu/00_Project/CA_mechanism/regression_SR/data/processed/v3prhd_analysis_ready.dta)
  - [v3prhdsm_analysis_ready.dta](C:/YangSu/00_Project/CA_mechanism/regression_SR/data/processed/v3prhdsm_analysis_ready.dta)
  - [v3decomp_analysis_ready.dta](C:/YangSu/00_Project/CA_mechanism/regression_SR/data/processed/v3decomp_analysis_ready.dta)
  - [v3sub_analysis_ready.dta](C:/YangSu/00_Project/CA_mechanism/regression_SR/data/processed/v3sub_analysis_ready.dta)

### 主代码

- `v3prhd`： [scripts/stata](C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata) 下的 `v3prhd_*`
- `v3prhdsm`： [scripts/stata](C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata) 下的 `v3prhdsm_*`
- `v3decomp`： [scripts/stata](C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata) 下的 `v3decomp_*`
- `v3sub`： [scripts/stata](C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata) 下的 `v3sub_*`
- 图脚本： [scripts/R](C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/R)

### 当前优先看的报告版本

- `v3prhd`： [v3prhd_beamer_report_compare_v3.pdf](C:/YangSu/00_Project/CA_mechanism/regression_SR/output/reports/v3prhd_beamer_report_compare_v3.pdf)
- `v3prhdsm`： [v3prhdsm_beamer_report_spec234_v5.pdf](C:/YangSu/00_Project/CA_mechanism/regression_SR/output/reports/v3prhdsm_beamer_report_spec234_v5.pdf)
- `v3decomp`： [v3decomp_beamer_report.pdf](C:/YangSu/00_Project/CA_mechanism/regression_SR/output/reports/v3decomp_beamer_report.pdf)
- 综合汇总： [v3_dialogue_integrated_beamer.pdf](C:/YangSu/00_Project/CA_mechanism/regression_SR/output/reports/v3_dialogue_integrated_beamer.pdf)

### 最近计划文件

接手前优先看这几份：

- [2026-04-07_v3prhd_fourcuts_report_plan.md](C:/YangSu/00_Project/CA_mechanism/regression_SR/quality_reports/plans/2026-04-07_v3prhd_fourcuts_report_plan.md)
- [2026-04-07_v3prhdsm_report_plan.md](C:/YangSu/00_Project/CA_mechanism/regression_SR/quality_reports/plans/2026-04-07_v3prhdsm_report_plan.md)
- [2026-04-09_v3_decomposition_equation_plan.md](C:/YangSu/00_Project/CA_mechanism/regression_SR/quality_reports/plans/2026-04-09_v3_decomposition_equation_plan.md)
- [2026-04-09_v3sub_subsample_rerun_plan.md](C:/YangSu/00_Project/CA_mechanism/regression_SR/quality_reports/plans/2026-04-09_v3sub_subsample_rerun_plan.md)

## 3. 当前口径里最容易混淆的变量定义

这一部分是最重要的，因为接手时最容易把“旧定义”和“当前定义”混在一起。

### Drought

当前 `D` 不是一个原始降水变量，而是由 `SPEI` 单边拆分得到的干旱暴露：

\[
D = \max(0, -SPEI)
\]

对应 `D_full`、`D_v3pre30`、`D_v3pm10` 等不同时间窗口版本。

### Heat

当前 `H` 用的是高温强度 `HDD`，不是简单高温天数：

\[
H = \sum \max(T_{\max} - 32^\circ C, 0)
\]

对应变量是 `hdd_ge32*`。

### HotDryPr

这是当前 `v3prhd / v3prhdsm` 主线里的复合热干旱日定义，口径是：

\[
\text{HotDryPr} = \sum 1(T_{\max} \ge 32^\circ C \ \text{and} \ pr < 1mm)
\]

也就是“热阈值用 32°C，干阈值用日降水小于 1 mm”。它和更早那套“高温 + 低土壤水分”的 hot-dry 变量不是同一口径。

### Soil Moisture 变量

当前对话里真正被反复用到的 SM 变量有三类：

- `gleam_sms_mean` / `gleam_smrz_mean`
- `swsm_l3_mean`
- `era5l_swvl1_mean` / `era5l_swvl3_mean`

注意，`v3prhdsm` 里因变量可以是 6 个 SM outcome，而 `v3decomp` 里主 mediator 先锚定的是 `gleam_sms_mean`。

## 4. 接手时建议的阅读顺序

如果是第一次接手，建议严格按下面顺序看，不要一上来就读所有脚本。

1. 先看综合汇报  
   [v3_dialogue_integrated_beamer.pdf](C:/YangSu/00_Project/CA_mechanism/regression_SR/output/reports/v3_dialogue_integrated_beamer.pdf)

2. 再看逐文件清单  
   [2026-04-09_dialogue_task_file_inventory.md](C:/YangSu/00_Project/CA_mechanism/regression_SR/quality_reports/file_inventory/2026-04-09_dialogue_task_file_inventory.md)

3. 再看各模块计划  
   从 `v3prhd`、`v3prhdsm`、`v3decomp`、`v3sub` 四份计划开始

4. 再看各模块主结果表和主报告  
   不要先从 log 入手，除非当前有报错要查

5. 最后才看具体脚本  
   尤其是 `*_macros_include.do` 和 `*_step0_preamble.do`

## 5. 之前反复出现的共性问题

### 5.1 变量口径漂移

这是最大的问题。项目里“同一概念”的定义并不总是稳定：

- `D × H` 曾经是主结构，后来被 `HotDryPr` 替换
- hot-dry 既有“高温 + 低土壤水分”定义，也有“高温 + 低降水”定义
- `Heat` 既有 `hotdays_tmax_ge32` 天数口径，也有 `hdd_ge32` 强度口径，但当前主线用的是后者

所以接手时不要只看变量名，要先确认这一轮脚本到底在引用哪一组字段。

### 5.2 `docs/VARIABLES.md` 不是当前 v3 的完整权威字典

这个文件有用，但它主要反映更早的变量结构。当前 `v3` 新增的很多派生变量、窗口变量、交互项和 `HotDryPr_*` 口径，并没有都在这里完整更新。

当前真正的权威来源是三类文件一起看：

- `*_macros_include.do`
- `*_step0_preamble.do`
- 模块对应的 beamer/Rmd 报告

### 5.3 是否包含 `W` 不是固定的

早期 `v3` 主规格里，RHS 包含 `W` 和 `SR × W`。但后面几条任务链并不完全一致：

- `v3prhd` 主线已经按任务要求移除了 `W`
- `v3sub` 也移除了 `W`
- `v3decomp` 的主方案里保留过 `W` 的层，但解释逻辑又刻意不扩展成 `SR × SM` 那条线

因此接手时不能默认所有 `v3` 结果都共享同一个 RHS。

### 5.4 报告版本很多，容易认错主版本

`output/reports` 里有很多 `v2`、`v3`、`compare_v2/v3/v4/v5`、`check` 文件。真正接手时容易把检查截图、过渡版 PDF、旧版 tex 当成主成果。

当前建议只把下面几份当主版本：

- `v3prhd_beamer_report_compare_v3.pdf`
- `v3prhdsm_beamer_report_spec234_v5.pdf`
- `v3decomp_beamer_report.pdf`
- `v3_dialogue_integrated_beamer.pdf`

### 5.5 中文编码和终端显示会误导判断

在 PowerShell 和部分日志查看场景里，中文经常会乱码；这并不一定是文件本身坏了。有几类情况要区分：

- 文件内容本身是好的，只是终端编码显示错
- Rmd 标题或日志元数据里显示乱码，但 PDF 编译正常
- 真正的编码问题通常出现在复制旧文件或混用不同编辑器时

所以判断文件是否损坏，不要只看终端输出，优先看：

- 原始 `.Rmd / .md` 文件
- 渲染后的 PDF
- 是否能成功编译

### 5.6 `output/logs` 和项目根目录旧 log 并存

项目根目录下残留了很多旧 log，但当前任务链真正应该优先看的，是 [output/logs](C:/YangSu/00_Project/CA_mechanism/regression_SR/output/logs) 下的模块 log。接手排错时，先从 `output/logs/v3*` 看，不要先从根目录的老 log 开始。

### 5.7 图和报告不是一一自动同步的

有些模块是“先生成结果表，再生成系数图，再人工调 beamer”；因此：

- 更新了表，不代表图自动更新
- 更新了图，不代表旧 beamer 自动替换
- 某些 PDF 文件名里带 `v2/v3/v5`，其实是人工多轮排版结果，不是同一脚本单步产物

接手时要确认“当前图”和“当前 PDF”是不是同一轮生成的。

## 6. 如果下一位接手人要继续做什么

最可能继续的方向有三类：

1. 在现有 `v3sub_*` 结果上继续做图和 beamer，而不是再重跑 Stata
2. 把当前变量定义整理成一份真正同步到 `v3` 的变量字典，替换掉旧 `docs/VARIABLES.md` 的缺口
3. 进一步压缩 `output/reports` 中的主版本与中间版本，减少版本识别成本

## 7. 本轮新增的交接材料

- 目录清单： [2026-04-15_v3_task_relevant_directories.md](C:/YangSu/00_Project/CA_mechanism/regression_SR/quality_reports/file_inventory/2026-04-15_v3_task_relevant_directories.md)
- 文件级清单： [2026-04-09_dialogue_task_file_inventory.md](C:/YangSu/00_Project/CA_mechanism/regression_SR/quality_reports/file_inventory/2026-04-09_dialogue_task_file_inventory.md)
- 本交接文档： [2026-04-15_v3_task_handoff.md](C:/YangSu/00_Project/CA_mechanism/regression_SR/quality_reports/handoffs/2026-04-15_v3_task_handoff.md)
