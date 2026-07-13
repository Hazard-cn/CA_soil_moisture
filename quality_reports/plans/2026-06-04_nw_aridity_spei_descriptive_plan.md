# NW aridity and SPEI descriptive statistics plan

本次任务只做描述统计，不重估回归。

口径：

- 样本：当前最新 `B067` scale。
- 区域：`maize_zone == "NW"`。
- `ari`：按数据中的 `aridity` 变量处理。
- `SPEI`：当前 Python 面板未直接载入原始 `spei*` 字段，但窗口方程使用的 `D_*` 和 `W_*` 来自 `D=max(0,-SPEI)`、`W=max(0,SPEI)`，因此按 `SPEI = W - D` 精确还原各窗口 SPEI。
- 窗口：`full`, `v3pre30`, `v3pm10`, `hepm10`, `v3he`, `hema`。

输出：

- `output/figures/f4_b067_v2/table14_nw_aridity_spei_obs_descriptive.csv`
- `output/figures/f4_b067_v2/table14_nw_aridity_spei_gridmean_descriptive.csv`
- `output/figures/f4_b067_v2/table14_nw_aridity_spei_gridlevel.csv`
- `quality_reports/2026-06-04_nw_aridity_spei_descriptive.md`

校验：

- NW B067 样本应为 3,381 obs、1,113 grids。
- `spei_* = W_* - D_*` 后，变量应无系统性缺失。
- obs 层面和 gridmean 层面统计都应覆盖 aridity 与 6 个 SPEI 窗口。
