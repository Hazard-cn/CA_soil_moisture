# 2026-04-07 Data Build V3 Capped GDD Plan

## Summary

- 在 `data_build` 链路内显式升版到 `v3`，不覆盖现有 `v2` 产物。
- 新增 4 组 capped GDD：`gdd_10_29`、`gdd_10_30`、`gdd_10_31`、`gdd_10_32`，并生成全部 6 个窗口版本。
- 公式固定为 `max(min(t2m_mean, cap) - 10, 0)` 日尺度求和。

## Implementation

- 修改 `s02_calc_temp_windows.py`，扩展温度窗口聚合和验证输出。
- 修改 `fix_pseudo_zeros.py`，把新 GDD 变量纳入温度派生缺失值传播。
- 修改 `s08/s09/s10`，统一切到 `data_v3_*` 命名，并显式生成 `phenowindows/main/noyield`。
- 修改 `gen_data_dictionary.py`，从 `data_v3_main.parquet` 自动生成 `VARIABLES_v3.md` 与 `data_dictionary_v3.csv`，补齐 `v3pre30` 和新 GDD 标签。
- 修改 `run_all.py`，把 pseudo-zero 修复和字典生成纳入完整流水线。

## Verification

- 检查 `data_v3_main.parquet` / `data_v3_phenowindows.parquet` 是否包含 24 个新 capped GDD 列。
- 检查单调性：`gdd_10_29 <= gdd_10_30 <= gdd_10_31 <= gdd_10_32 <= gdd_ge10`。
- 检查 `main/noyield` 行数与既有主样本划分是否一致。
- 检查 `VARIABLES_v3.md` 与 `data_dictionary_v3.csv` 的变量数是否与 `data_v3_main.parquet` 完全一致。
