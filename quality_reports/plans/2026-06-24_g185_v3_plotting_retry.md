# G185 v3/v3.1 plotting retry plan

## Scope

本轮只复核并重跑 G185 v3/v3.1 图形输出，不改变 v3 统计模型、样本定义、估计量定义、bootstrap 设置或 claim adjudication 规则。v3.1 仍仅覆盖 figure list 和 figure requirements。

## Steps

1. 确认现有 final run 目录、`figure_data/`、`figures/`、`21_figure_manifest.csv` 与 `24_visual_qc.md` 是否存在。
2. 使用 `scripts/python/make_g185_v3_figures.py --run-dir quality_reports/agent_runs/2026-06-20_g185_response_surface_v3 --language en` 从已保存的 fitted climate-loss contrast CSV 重新生成 PNG/PDF 图形。
3. 重新生成中文 reviewer summary，并确认主图 contact sheet 与 captioned PDF 可创建。
4. 检查 figure manifest、visual QC、PNG/PDF 文件大小、图像可打开性，并确认每个 figure_data 文件仍存在。
5. 重新构建或验证 `g185_v3_review_bundle.zip`，确保 visual outputs 仍包含在 bundle 中。

## Verification

通过条件包括：绘图脚本退出码为 0；`24_visual_qc.md` 不含 `FAIL`；`21_figure_manifest.csv` 中所有行 `status=OK`；zip integrity test 返回 `None`；必要时抽样打开 PNG 检查非空图像。
