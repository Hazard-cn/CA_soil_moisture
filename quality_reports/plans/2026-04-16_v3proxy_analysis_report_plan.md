# `SM` 代理模型组与 Beamer 报告新线

## Summary
- 新开一条独立 `v3proxy_` 线，不改写现有 `v3med_` 或 `v3_smproxy_` 产物；核心规则固定为：同一 `SM` 在同一模块内只承担 drought proxy，不再承担 mediator。
- 主线只做 drought proxy 的 `Set A / Set B / Set C`，heat 只保留为“给定 `DrySM` 后 `H×ca` 是否仍成立”的一致性附录。
- 主展示使用 `reduced controls + strict common sample`，`full controls` 只做附录复跑。
- 窗口固定为 3 组：`full`、`v3pm10 + hepm10`、`v3pre30 + v3he + hema`；来源固定为 `GLEAM / SWSM / ERA5-Land`，每个来源都保留 `surface/rootzone` 两层。

## Key Changes
- 新增一套独立脚本与报告入口：`scripts/stata/v3proxy_macros_include.do`、`scripts/stata/v3proxy_step0_preamble.do`、`scripts/stata/v3proxy_step1_modelsets.do`、`scripts/stata/v3proxy_step2_heat_consistency.do`、`scripts/R/v3proxy_plots.R`、`output/reports/v3proxy_beamer_report.Rmd`，并新增 `.AGENT/agents/proxy-model-reporter.md`。
- `step0_preamble` 读取 `data/processed/v3prhdsm_analysis_ready.dta`，生成 `data/processed/v3proxy_analysis_ready.dta`，同时锁定单一 `v3proxy_common`：要求 `ln_yield`、`ca`、三组窗口涉及的 `D/H`、full-control 变量、以及 36 个 `SM` 变量全部非缺失；`reduced` 与 `full` 后续都使用这一个样本。
- 对每个 `source × layer × raw_window` 在 `v3proxy_common == 1` 上标准化并取反，生成 `drysm = -z(sm)`；`ii` 与 `iv` 不做窗口平均，而是沿用现有 cut 逻辑，把 constituent windows 联合放入同一方程。
- 回归结构固定为：
  - `Set A`：原始 drought baseline，`full` 用单窗口项，`ii/iv` 分别联合放入对应 `D_w`、`D_w×ca`、`H_w` 与窗口 controls。
  - `Set B`：把同窗口 `D_w` 全部替换成 `drysm_w` 与 `drysm_w×ca`，这是主规格。
  - `Set C`：只放 `D_w + drysm_w + ca + H_w + controls + FE`，不放交互，用于看解释权重叠。
  - reduced-only 附录再加两组 competition：`D_w×ca + drysm_w` 与 `drysm_w×ca + D_w`。
  - heat appendix 固定为 `H_w + H_w×ca + drysm_w + ca + controls + FE`。
- 所有模型统一 `absorb(grid_id year)`、`vce(cluster grid_id)`、`set seed 42`；控制变量默认沿用窗口化 `v3prhdsm` 体系，reduced 为 `irr_frac + gdd_10_30*`，full 在此基础上加 `pr_sum* + et0_sum*`，不再把 `aridity` 放进这条 proxy 线。
- 导出一个统一长表供绘图与报告使用，字段至少包含 `module`、`model_set`、`ctrl_version`、`source`、`layer`、`cut`、`raw_window`、`term`、`term_group`、`b`、`se`、`p`、`N`、`r2`。

## Report Design
- Beamer 报告单独成线，不覆盖现有 `v3med_beamer_report`；正文先给一页设计纪律，再给一页样本与 proxy 构造，随后正文只放图，不把大表放入主文。
- 主图最少 5 组：`Set A 基准`、`Set B shock coefficient`、`Set B buffering interaction`、`Set C overlap diagnostic`、`Heat consistency`；competition 和 full-controls 全部进附录。
- 所有数值图统一做横向系数图，系数与 95% CI 放在 x 轴，类别放在 y 轴；颜色固定映射数据源，点形固定映射层次，分面固定映射三组窗口。
- 每张图都必须同时有图例框和一句图例解释文字，明确“颜色代表什么、形状代表什么、分面代表什么”；主文文字全面禁用 mediator、a-path、b-path、indirect effect 等术语，统一改写为 `proxy baseline`、`buffering interaction`、`overlap diagnostic`、`competition check`、`conditional association`。

## Test Plan
- 预处理检查：确认三组窗口所需 `D/H/controls` 与 36 个 `SM` 变量全部存在；确认 `drysm` 是在 `v3proxy_common` 上生成；确认 `corr(drysm, z(sm)) = -1` 或数值等价。
- 结果完整性：reduced 主线至少产出 `Set A` 3 个模型、`Set B` 18 个模型、`Set C` 18 个模型、heat appendix 18 个模型；reduced-only competition 36 个模型；full appendix 至少复跑 `Set A/B/C + heat`。
- 日志检查：不得有 `r()` 报错、关键项系统性共线删除、空文件或 0 字节输出；输出时间戳必须晚于运行时间。
- 图报检查：所有主图与附录图白底、300 DPI、值轴在 x 轴、图例和图例解释齐全；Beamer PDF 编译成功，正文能直接回答三件事：`DrySM` 是否比 `D_full` 更像有效 drought state、`DrySM×ca` 是否更稳、`Set C` 是否显示 `D` 与 `SM` 在抢解释权。

## Assumptions
- `full / ii / iv` 是 3 个主窗口组，`v3he + hema` 不再单列成独立主组，只作为 `iv` 的组成部分。
- `strict common sample` 采用 full-controls 口径锁定，这样 reduced 与 full 的系数可直接比较，不再因缺失模式换样本。
- `.AGENT/agents` 采用新增专用 agent 文件，而不是改写现有 reviewer/verifier。
- 实施开始后，先把本计划保存到 `quality_reports/plans/`，再进入代码、绘图、报告与最终验证。
