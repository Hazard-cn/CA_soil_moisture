# 秸秆还田与玉米气候损失缓冲分析

本仓库包含 V1-V6、GGCP10、G185 以及联合胁迫响应面等多个历史和并行分析分支。不同分支的样本、固定效应、估计量和图表不能直接混合引用；当前 G185 工作应从下列入口开始。

## 当前 G185 入口

截至 2026-07-10，旧线性两方程口径下的区域 IE/DE/TE 修正版是：

- 完整审阅包：`quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/g185_old_method_region_tiede_redraw_bundle.zip`
- 五图总览：`quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/figures_png/contact_sheet_corrected_old_method.png`
- 核心结果表：`quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/tables/core_three_corrected_te_results.csv`
- 15 个区域-胁迫组合及组件表：`quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/tables/region_tiede_delta_components.csv`
- 生成脚本：`scripts/python/export_g185_old_method_region_tiede_redraw.py`
- 当前交接：`quality_reports/handoffs/2026-06-21_g185_method_upgrade_report_handoff.md`

修正后的区域总缓冲关联为：东北干旱 1.85% [1.23, 2.56]、黄淮海高温 3.17% [2.07, 4.26]、黄淮海热干 2.43% [1.04, 3.87]。旧图中的 1.50%、3.27%、2.56% 来自控制同期根区土壤水分后的 `SR x hazard` 差异，属于 DE / residual component，不是 `TE = IE + DE` 定义下的 TE。

2026-06-20 的方法升级报告仍保留为方法比较和异质性一致性检查入口：`quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/report.html`。其中机器学习结果只用于附录级结构一致性检查，不替代固定效应主结果。

## 估计量边界

区域旧方法在每个 region-hazard 组合内估计土壤水分方程与产量方程，并定义 `IE(s) = (a1 + a3*s)b`、`DE(s) = c1 + c3*s`、`TE(s) = IE(s) + DE(s)`。主图报告 `SR` 从区域 P25 到 P75、胁迫取区域 P90 时的 TE 对比。IE/DE/TE 是两条方程形成的代数组件，不能写成已识别的因果中介效应。灌溉边界图是单独的连续三重交互结果，不属于 IE/DE/TE 分解。

## 复现

在项目根目录运行：

```powershell
& .\.venv-ml\Scripts\python.exe .\scripts\python\export_g185_old_method_region_tiede_redraw.py --reps 999 --seed 42
```

脚本当前读取两个实际存在的面板输入：

- `temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_baseline_suite_analysis_ready.dta`
- `data_build/data/processed/data_v3_main.dta`

V1 主数据位于项目外部共享目录 `C:/YangSu/00_Project/CA_mechanism/data/master/data_v1_with_climate.csv`；仓库内不存在 `data/processed/data_v1_with_climate.csv`。仓库内可直接使用的 V2 分析就绪文件是 `data/processed/v2_analysis_ready.dta`，而早期脚本所指的 `data_build/data/processed/data_v2_main.dta` 当前不存在。

## 文档索引

- `docs/DATA_SOURCES_CN.md`：数据来源、样本键和基础校验
- `docs/VARIABLES.md`：V1 变量字典
- `docs/analysis_specification.md`：历史 V1/V4/V6 联合胁迫框架说明，不能代替当前 G185 交接
- `docs/GGCP10_HARVAREA_BRANCH.md`：GGCP10 收获面积分支
- `docs/GGCP10_MEDIATION_EXTENSIONS.md`：2026-05 GGCP10 两方程扩展索引
- `quality_reports/handoffs/2026-06-21_g185_method_upgrade_report_handoff.md`：当前 G185 真值位置、复现命令与解释边界

项目已于 2026-07-13 初始化 Git，默认分支为 `main`，远端仓库为 `Hazard-cn/CA_soil_moisture`。任何删除文件、目录、输出、日志、计划或中间产物的操作都需要用户明确允许。
