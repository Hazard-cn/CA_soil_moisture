# Data Build Changelog

---

## 2026-04-04 — SPEI 计算方法修正

**改动文件:** `scripts/python/s06_calc_vpd_spei.py`

**问题:** 原 v2 实现对 SPEI 做月度加权平均（同 VPD 的处理方式），在统计上错误——SPEI-N 本身已是过去 N 个月的累积水分亏缺标准化指标，对相邻月份的 SPEI-N 取均值会混合重叠时间窗口，破坏指标原始语义。

**修正:** 改为 v1 终止月单点提取法。对每个格点-年份-窗口：
1. `start_month = doy_to_month(win_start_doy)`
2. `end_month = doy_to_month(win_end_doy)`
3. `scale = end_month - start_month + 1`（per grid-year 动态计算）
4. 取 `CHM_SPEI-{scale}.nc` 在 `end_month` 的值

**验证:** 新 v2 `spei6_mean` 与 v1 `SPEI_season` 完全一致（r=1.0000, MAE=0.0000, N=69,038）。

**影响范围:**
- 所有 SPEI 变量值已更新（full / v3pm10 / hepm10 / v3he / hema / v3pre30）
- `_max = _mean`（单点提取，_max 列保留以兼容下游）
- VPD 计算不变，列名不变，下游脚本无需修改

**更新的数据文件:**
- `data/intermediate/vpd_spei_windows.csv`
- `data/processed/data_v2_phenowindows.*` (.csv / .parquet / .dta)
- `data/processed/data_v2_main.*` (.csv / .parquet / .dta)

---

## 2026-03-29 — v2 数据管线初始构建

初始构建 v2 数据管线，生成 `data_v2_main.parquet`（69,038 行，523 列）。
涵盖 6 个物候窗口 × 多气候变量，来源包括 ERA5、GLEAM、SWSM、CHM_SPEI/VPD/PRE。
