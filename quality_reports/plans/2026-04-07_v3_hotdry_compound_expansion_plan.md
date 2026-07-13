# V3 热干复合指标扩展计划

## Summary

当前仓库里，热干复合变量只存在 `hotdrydays_ge32_smrz_p10/p20` 和 `hotdrydays_ge35_smrz_p10/p20` 这两组及其 6 个窗口版本；没有 `ge30`，也没有不同 Soil Moisture 来源的 `hotdrydays_*`。但多源土壤水分的单独干旱日已经存在，因此本次在 `v3` 链路内把热干复合指标扩展为两类：一类是多源 Soil Moisture 版，覆盖 `ge30/32/35 × p10/p20 × 6个来源/层次`；另一类是降水版，定义为日尺度 `Tmax>=阈值 且 pr<1mm`。`v2` 产物不动，`v3` 产物原位重生成。

## Key Changes

- 在 `data_build/scripts/python/config.py` 中把复合高温阈值固定为 `30/32/35°C`，并新增 7 类复合干旱来源注册表：`smrz`、`sms`、`swsm_l1`、`swsm_l3`、`era5l_swvl1`、`era5l_swvl3`、`pr_lt1`。
- 在 `data_build/scripts/python/s07_calc_compound.py` 中把当前只支持 `SMrz p10/p20` 的逻辑改为通用框架，生成 `hotdrydays_ge{30|32|35}_{source}_{p10|p20}{suffix}` 和 `hotdrydays_ge{30|32|35}_pr_lt1{suffix}`，并复用现有各来源脚本的基线百分位、对齐方式和窗口体系。
- 继续沿用 `compound_windows.csv -> s08_merge_panel.py -> data_v3_phenowindows/main/noyield` 的合并链路，不新增新的 merge step。
- 在 `data_build/scripts/python/s09_quality_check.py` 中增加新复合变量的结构、阈值单调性、`p10<=p20`、以及 `hotdrydays <= drydays` 一致性检查，并把全部 `hotdrydays_*` 纳入摘要输出。
- 在 `data_build/scripts/python/gen_data_dictionary.py` 与 `data_build/docs/VARIABLES_v3.md` 中补齐新变量标签，明确区分 GLEAM、SWSM、ERA5-Land 与 `pr<1mm` 这几类干旱口径。

## Test Plan

- 结构检查：确认 `data_v3_phenowindows` 与 `data_v3_main` 中 `hotdrydays_*` 总列数为 `234`，并覆盖 `ge30/32/35`、6 类 Soil Moisture 来源、`pr_lt1`、`p10/p20` 与全部窗口后缀。
- 公式抽样：分别对 GLEAM、SWSM、ERA5-Land、降水版抽样逐日复算，验证 `Tmax>=阈值` 与对应干旱条件的同日交集。
- 逻辑约束：验证 `hotdrydays_ge35_* <= hotdrydays_ge32_* <= hotdrydays_ge30_*`，并验证 Soil Moisture 版同一热阈值下 `p10 <= p20`。
- 交叉一致性：验证 Soil Moisture 版 `hotdrydays_geT_source_p10/p20` 不大于对应 `drydays_source_le_p10/p20`，降水版 `hotdrydays_geT_pr_lt1` 不大于对应窗口 `drydays_lt1`。
- 导出与文档：确认 `data_v3_phenowindows/main/noyield` 行数不变，CSV/Parquet/DTA 列集合一致，`VARIABLES_v3.md` 与 `data_dictionary_v3.csv` 变量数和 `data_v3_main.parquet` 完全一致。

## Assumptions

- 本次只扩展 `data_build` 的 `v3` 数据与字典，不调整任何 `v3_*.do` 或控制变量宏。
- 降水版干旱定义固定为日降水 `<1.0 mm`，直接复用当前降水数据源。
- 多源 Soil Moisture 版固定同时保留 `p10` 和 `p20`。
- `v2` 产物保持不变，已有 `v3` 产物允许被本次重生成结果覆盖。
