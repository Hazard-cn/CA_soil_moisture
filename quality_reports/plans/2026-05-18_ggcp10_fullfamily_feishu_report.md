# 2026-05-18 GGCP10 full-family Feishu report plan

## Goal

在 GGCP10 聚合面积版底座上，重跑参考 PDF 对应的 GLEAM dry-side full-family baseline 结果，并生成只保留系数图的飞书在线文档。

## Scope

- 数据底座：`temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/v3_analysis_ready_ggcp10_harvarea_agg.dta`
- 变量体系：参考 PDF 对应的 7 个 GLEAM dry-side metric family
  - `mdduration_dry`
  - `mddurshare_dry`
  - `mdseverity_dry`
  - `blduration_dry`
  - `bldurshare_dry`
  - `blseveritymean_ddf`
  - `blseveritysum_ddf`
- 三组外生胁迫：
  - `Drought`
  - `Heat`
  - `HotDry`
- 文档只展示图，不放系数数字表、显著性汇总表或逐项文字解读。

## Deliverables

1. 新的独立输出目录：
   - `temp/2026-05-18_ggcp10_harvarea_agg_v6gleambl_fullfamily/`
2. 三组 baseline 结果：
   - `*_analysis_ready.dta`
   - `*_diagnostics.csv`
   - `*_baseline_coefficients.csv`
   - 日志文件
3. 12 张 fullnew 系数图：
   - 每组外生胁迫各 `a1 / a3 / c3 / b`
4. 一份新的飞书在线文档：
   - 标题层级清晰
   - 公式单独成段
   - 使用三级标题组织每一组图
   - 正文不放数字表

## Verification

- 所有 Stata 日志含 `COMPLETE`
- `grid_id-year` 仍可 `xtset`
- 三组结果均覆盖 `fullnew` 下 22 个 spec cell
- 飞书文档已创建，标题正确，12 张图均成功插入
