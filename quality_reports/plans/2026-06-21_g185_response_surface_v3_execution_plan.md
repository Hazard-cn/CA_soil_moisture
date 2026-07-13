# 2026-06-21 G185 response-surface v3 execution plan

本轮执行对象是 `CODEX_G185_RESPONSE_SURFACE_V3.md` 与 `CODEX_G185_VISUALIZATION_ADDENDUM_V3_1.md`。读取顺序已经固定为先 v3、后 v3.1；v3.1 只覆盖 figure list 与 figure requirements，统计模型、样本断言、推断、支持度、robustness 和 claim adjudication 仍按 v3 执行。

## 约束

- 只使用 G185 analytical sample，不把 G057/G049/G185 估计混合作为证据。
- 不覆盖 v1/v2 脚本或输出；本轮新增 `scripts/python/g185_v3_*.py`、`scripts/python/run_*_v3.py`、`scripts/python/make_g185_v3_figures.py`，输出只进入 `quality_reports/agent_runs/2026-06-20_g185_response_surface_v3/`。
- 主模型为固定 0.1-degree grid、rule-based G185 analytical sample 上的低自由度 drought-heat response surface；所有 substantive claim 来自 fitted scenario contrasts and fitted losses，不解释孤立 spline coefficients。
- 图形脚本只从 machine-readable CSV 重建图形，不重新拟合模型。
- 所有文本使用 conditional association、SR-associated climate-loss buffering、pathway consistency 等边界语言，不写 causal effect、causal mediation 或 G185 uniquely optimal。

## 执行顺序

1. 实现配置、数据、FE、spline、estimand、inference helper。
2. 实现 `run_all_g185_v3.py`，支持 `--mode quick` 与 `--mode final`。
3. 实现 v3.1 图形脚本与 review bundle builder。
4. 先运行 quick 检查样本断言、模型收敛、CSV schema、图形重建和 zip 构造。
5. 再运行 final，使用 1,999 组 primary 2-degree spatial-block wild-score draws；robustness rows 记录对应模型和推断设置。
6. 验证 `g185_v3_review_bundle.zip` 可解压、checksums 可核对、图形 QC 无 FAIL。

## 验收

最终至少生成 v3 指定的 `00_README_FOR_REVIEW.md` 至 `20_limitations_autotext.md`、v3.1 指定的 `21_figure_manifest.csv` 至 `24_visual_qc.md`、所有 `figure_data/` 与 `figures/` 文件，以及根目录 `g185_v3_review_bundle.zip`。若某个非主模块因样本支持、可用字段或数值秩问题无法生成可解释估计，输出中必须显式记录 `NOT_RUN`、`NOT_EVALUABLE_SUPPORT` 或 `SUPPORTED_BUT_SENSITIVE`，不得补造结果。
