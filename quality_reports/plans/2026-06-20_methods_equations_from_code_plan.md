# Methods and econometric equations extraction plan

## Goal

基于当前项目代码和 G185 draft 相关输出，整理本文实际用到的方法、样本定义、计量模型和方程，形成可进入 Methods/Appendix 的中文报告。

## Scope

优先覆盖当前 G185 story draft 中实际承载主线的模型：

1. G185 scale construction and scale-search transparency.
2. Baseline hazard-yield FE model.
3. Soil-moisture-associated algebraic component / residual component / combined slope contrast.
4. Region-specific hazard-buffering model.
5. Continuous irrigation heterogeneity model.
6. Phenology-window compound-stress model.
7. Grid/year FE, grid-cluster inference, and current bootstrap-linearized interval method.
8. Stata/Python verification and sample-scope caveats.

旧版 v1-v8、DML、placebo、sensitivity 等代码只作为 appendix 方法候选列出，除非当前 draft 或结果图明确使用。

## Outputs

- `quality_reports/2026-06-20_methods_and_model_equations_from_code.md`

## Verification

- 用 `rg` 定位模型实现。
- 对关键脚本和结果表进行直接读取。
- 明确每个方程对应的代码路径和输出文件。
- 最终检查报告是否包含所有主图对应模型。
