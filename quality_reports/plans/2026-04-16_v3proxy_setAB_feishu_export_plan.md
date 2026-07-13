# 2026-04-16 Set A / Set B 核心系数图表与 Feishu 导出计划

## 任务目标
围绕 `Set A` 与 `Set B` 的四个核心系数 `D`、`D×SR`、`DrySM`、`DrySM×SR`，补一条独立的整理与出图线，输出可直接放入 Feishu 表格的长表与图片，不改动既有 `v3proxy_` 主产物。

## 实施范围
1. 从 `output/tables/v3proxy_results_long.csv` 提取 `Set A` 与 `Set B`、`reduced controls`、`module == drought` 的目标系数。
2. 生成两类对比图：
   - shock coefficient：`D` 对 `DrySM`
   - buffering interaction：`D×SR` 对 `DrySM×SR`
3. 生成 Feishu-ready 数据表，至少包含 `cut`、`raw_window`、`model_set`、`term`、`source`、`layer`、`b`、`se`、`p`、`ci_lo`、`ci_hi`。
4. 检查本机是否存在可复用的 Feishu Bitable 写入链路；若链路或目标表缺失，则生成 `xlsx/csv` 作为直接导入件。

## 设计约束
- 图保持白底、300 DPI、横向系数图，值轴放在 x 轴。
- 只服务四个核心系数，不混入 `Set C`、competition、heat appendix。
- 图例必须完整，且另附一句图例解释。
- `Set A` 作为基准行；`Set B` 保留 `source × layer` 维度。

## 验证标准
- 至少产出 6 张图：`3 cuts × 2 coefficient families`。
- 至少产出 1 个长表 `csv` 和 1 个 `xlsx`。
- 若 Feishu API 可用，则完成一次写入或更新；若不可用，则给出明确阻塞点。
