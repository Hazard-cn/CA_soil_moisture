# MEMORY.md -- SR Buffering Project

## 项目概况
- 研究问题：秸秆还田（SR）能否通过稳定土壤湿度缓冲极端气候（热害+干旱）对玉米产量的损失？
- 数据：grid-year 面板，0.1度格网，2016-2019，N=69,038，143列
- V1 主数据文件：`C:/YangSu/00_Project/CA_mechanism/data/master/data_v1_with_climate.csv`（项目外部共享路径；仓库内没有 `data/processed/data_v1_with_climate.csv`）
- 分析语言：Stata（主）、R/Python（辅）
- 文档语言：中文文档，英文代码

## 关键变量
- 结果变量：`yield_tons_ha`, `ln_yield`
- SR 杠杆：`ca`, `crc_ca_ratio`（当年），`crc_lag1`（滞后1年）
- 极端热害：`hdd_tmax_ge32/35/38`, `hotdays_tmax_ge*`
- 干旱/湿涝：`SPEI_season`（分解为 D=max(0,-SPEI), W=max(0,SPEI)）
- SM 通道：`gleam_smrz_mean`, `gleam_sms_mean`
- 面板键：`grid_id`（grid FE），`year`（year FE），`prov_year`

## Blueprint 7步路线
1. Baseline FE：SR x 极端交互（θ1>0 干旱缓冲，θ2≤0 湿涝边界，θ3>0 热害缓冲）
2. Placebo 窗口诊断：非关键期窗口交互应减弱
3. 机制 I（月度）：极端 → SM 异常（SR 缓冲 a5>0）
4. 机制 II（年度）：SM 尾部 → 产量 + θ 衰减检验
5. 边界条件与异质性：干旱区 SR 缓冲更强
6. DML 稳健性：交叉拟合双重机器学习
7. 敏感性检查：窗口宽度、热指标、阈值、SM 规格

## 用户偏好
- 计划优先工作流，非简单任务必须先计划
- 承包商模式：批准后自主执行，模糊时回来确认
- 发表级可视化：白背景、300DPI、sans-serif
- Stata 路径用 global 宏，聚类默认 grid_id

## 环境路径
- Stata: `C:/Sofewares/Stata/Stata18/StataMP-64.exe`
  - Windows 批处理：`"C:/Sofewares/Stata/Stata18/StataMP-64.exe" /e do script.do`
  - 注意：Windows Stata `/e` 会打开 GUI 窗口执行后退出（非纯 CLI），日志文件生成在工作目录
  - Stata 不在 PATH 中，必须用完整路径调用
- Python: `python`（3.14.2，已在 PATH）
- Python ML: `.venv-ml/Scripts/python.exe`（Python 3.12，G185 method upgrade 专用，不污染 `.venv`）
- R: `Rscript`（已在 PATH）
- Rscript for G185 ML report: `C:/Users/Lenovo/AppData/Local/Programs/R/bin/Rscript.exe`
- 项目根目录：`C:/YangSu/00_Project/CA_mechanism/regression_SR`
- Common lib：`C:/YangSu/00_Project/CA_mechanism/code/common_lib/`

## 当前 G185 旧方法区域 IE/DE/TE 修正版（2026-06-24）
- 完整包：`quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/g185_old_method_region_tiede_redraw_bundle.zip`
- 总览图：`quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/figures_png/contact_sheet_corrected_old_method.png`
- 核心表：`quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/tables/core_three_corrected_te_results.csv`
- 生成脚本：`scripts/python/export_g185_old_method_region_tiede_redraw.py`
- 真实输入：`temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_baseline_suite_analysis_ready.dta` 与 `data_build/data/processed/data_v3_main.dta`
- 核心 TE：东北干旱 1.85% [1.23, 2.56]；黄淮海高温 3.17% [2.07, 4.26]；黄淮海热干 2.43% [1.04, 3.87]。
- 解释边界：IE/DE/TE 是两方程代数组件；灌溉图是独立边界结果；不得混入 G057/G049、v3 响应面或无 SM reduced-form TE。

## G185 方法升级报告入口（2026-06-20）
- 报告入口：`quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/report.html`
- 可编辑版本：`quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/report.md`
- 交接文件：`quality_reports/handoffs/2026-06-21_g185_method_upgrade_report_handoff.md`
- 生成脚本：`scripts/python/build_g185_method_upgrade_report.py`
- 环境 wrapper：`scripts/env/g185_ml_env.ps1`
- 固定口径：该报告只采用 G185；G057/G049 只作为 scale-selection 背景，不并入 G185 claim 的证据。
- 写作边界：主结论由 fixed-effect G185 damage-avoidance margins 承载；`econml`、`DoubleML`、R `grf` 只作为异质性结构一致性检查。

## 工作流决策
- 2026-03-11: 从 claude-code-my-workflow-main 模板改造，移除所有 Beamer/Quarto/slides 组件
- 2026-03-11: 保留 plan-first + orchestrator-research + quality-gates + session-logging 核心规则
- 2026-03-11: 新建 stata-code-conventions 和 stata-reviewer
- 2026-03-11: 暂不初始化 git
- 2026-03-11: 文档文件移至 docs/ 子目录

## 学习记录
（纠正和经验将记录在此）
- [LEARN:estimand] 旧区域主图把 1.50%、3.27%、2.56% 称为 TE -> 这些数值是控制同期根区土壤水分后的 DE / residual component；按旧方程定义的区域 TE 必须计算 `IE + DE`，对应核心修正版为 1.85%、3.17%、2.43%。
- [LEARN:path] 仓库内 `data/processed/data_v1_with_climate.csv` 被当作真实入口 -> 当前真实 V1 入口是 `C:/YangSu/00_Project/CA_mechanism/data/master/data_v1_with_climate.csv`。
