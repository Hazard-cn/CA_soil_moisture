# v3prhd beamer 重构计划

日期：2026-04-07

## 目标

重做 `v3prhd` 独立 beamer，使表页与系数图页都具备可读版式，不再出现裁切、拥挤和信息层级混乱的问题；系数图的视觉效果参考 `output/reports/v3_beamer_interaction_report.tex` 的单图单页展示方式。

## 问题诊断

当前版本的问题不是结果文件缺失，而是版式策略不适合 beamer 页面约束：

1. 系数表把过多窗口和过多参数放进同一页，导致纵向超出页面；
2. 系数图把两张 forest plot 合并到一页，导致字体、坐标和置信区间被同时压缩；
3. 报告逻辑仍偏“结果导出”，而不是“演示文稿”，缺少面向口头汇报的页面分组；
4. appendix 页使用 markdown 表，长字符串在 beamer 中自动断行控制较弱。

## 重构原则

1. 保留现有 16 个模型与结果数据，不改估计结果；
2. PPT 结构按“定义页 - 结果表页 - 系数图页 - appendix”重排；
3. 系数图统一改为单图单页，图宽控制在 `0.95\\linewidth` 左右；
4. 表页按 cut 组拆分，只保留对应列，避免空列占位；
5. appendix 改成更稳的 LaTeX 表格或简洁文本块，不继续依赖 markdown 长表；
6. 所有标题、注释和术语统一使用当前任务定义：`HotDryPr`、`gdd_10_30`、不含 `aridity`。

## 实施步骤

1. 检查 `preamble.tex` 与现有 beamer 头部设置，确认是否沿用；
2. 重构 `scripts/R/v3prhd_coefplots.R`，提高单图页面展示清晰度；
3. 重写 `output/reports/v3prhd_beamer_report.Rmd` 的页面结构与文本；
4. 重新渲染 PDF；
5. 用 `pdftoppm` 导出每页图像做视觉核验，确认无裁切、无明显拥挤。

## 验收标准

1. 每页表格完整可见；
2. 每页系数图文字、点和置信区间肉眼可读；
3. PDF 编译成功；
4. 只依赖本任务 `v3prhd_*` 结果文件；
5. 不引入 `aridity`、`W` 或 `SR x W`。
