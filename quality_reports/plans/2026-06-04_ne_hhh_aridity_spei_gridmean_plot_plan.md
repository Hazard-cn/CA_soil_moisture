# NE and HHH aridity/SPEI grid-mean distribution plot plan

本次任务只补图和描述统计，不重估回归。

口径：

- 样本：当前最新 `B067` scale。
- 区域：`maize_zone in {NE, HHH}`。
- `aridity`：使用数据中的 `aridity` 变量。
- `SPEI`：按 `SPEI = W - D` 从窗口 `D_*` 与 `W_*` 还原。
- 分布单位：先在每个 `grid_id` 内对年份取均值，再按 region 画分布。
- 窗口：`full`, `v3pre30`, `v3pm10`, `hepm10`, `v3he`, `hema`。

输出：

- `output/figures/f4_b067_v2/fig15_ne_hhh_aridity_spei_gridmean_distribution.png`
- `output/figures/f4_b067_v2/table15_ne_hhh_aridity_spei_gridlevel.csv`
- `output/figures/f4_b067_v2/table15_ne_hhh_aridity_spei_gridmean_descriptive.csv`
- `quality_reports/2026-06-04_ne_hhh_aridity_spei_gridmean_distribution.md`

校验：

- `NE` 应覆盖 20,818 obs、5,655 grids。
- `HHH` 应覆盖 12,198 obs、3,309 grids。
- 图文件必须能被 PIL 打开且非空。
