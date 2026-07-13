# B067 region SR descriptive statistics plan

本次补充只做描述统计，不重估回归，不改变现有 B067 bootstrap、window 或 AI 图形结果。

执行口径：

- 样本：当前最新 `B067` scale，即 `zone_core=1, sr_within=1, years_ge3=0, stable_province=0`，其他清洗规则不启用。
- region：使用 `maize_zone`，覆盖 `HHH/NE/NW/SH/SW`。
- SR 变量：使用 `ca`。
- 输出：按 region 给出 grid-year 层面的 `ca` 分布、grid-level 平均 SR 和 grid 内 SR 时间变异，并生成一张描述性统计图。

目标文件：

- `output/figures/f4_b067_v2/table13_region_sr_descriptive.csv`
- `output/figures/f4_b067_v2/table13_region_sr_gridlevel.csv`
- `output/figures/f4_b067_v2/fig13_region_sr_descriptive.png`
- `quality_reports/2026-06-04_region_sr_descriptive_stats.md`

校验：

- B067 样本应为 42,187 行、11,775 个 grid。
- region 汇总的 N 加总应等于 B067 样本行数。
- 图文件应非空，且能被 PIL 打开。
