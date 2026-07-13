# 数据来源与定义

## 主分析数据集

文件：`data/processed/data_v1_with_climate.csv`  
观测单位：格网-年份（0.1 度格网，年度面板）  
时间范围：2016-2019（基于 `year` 字段全量扫描）  
空间范围/分辨率：中国玉米相关格网，约 0.1 度；纬度 21.73 至 51.13，经度 75.58 至 134.58

## 数据溯源（Provenance）

- 创建来源：仓库中未见单一“最终拼表脚本”；分析代码包位于 `references/code/*.R`（文件修改时间均为 2024-12-19）
- 原始输入：仓库内未给出一体化原始清单；从字段命名可识别为气象/再分析变量（`t2m_*`、`pre_sum`、`et0_*`、`gleam_*`）、管理变量（`crc_ca_ratio`、`crc_lag1`、`irr_frac`、`ca`）与玉米面积/产量变量的合并结果
- 处理步骤（高层）：
  1) 按 `year`、`latitude`、`longitude` 及派生键（`grid_id`、`prov_id`、`prov_year`）构建格网-年面板
  2) 生成生育期内气象/水分统计量（含 lag30 窗口与阈值极端指标）
  3) 合并管理采纳、灌溉与产量相关字段，形成分析就绪表

## 核心变量字典（简表）

字段：

- y：`yield_tons_ha`（玉米单产，tons/ha），`ln_yield`（`yield_tons_ha` 的自然对数）
- CA：`ca`（采纳比例，0-1），`crc_ca_ratio`（当年采纳比例，0-1），`crc_lag1`（滞后 1 年采纳比例，0-1）
- n_level：当前数据版本中未发现独立字段 `n_level`
- controls_*：控制变量主要由 `*_mean`、`*_sum`、`*_min`、`*_max`、`lag30_*`、阈值指标（`*basep10`、`*basep20`、`*basep90`、`*basep95`）构成；示例：`t2m_mean`、`pre_sum`、`gleam_smrz_mean`、`wd_deficit_et0minuspre`、`hotdays_tmax_ge32`、`drydays_gleam_smrz_le_basep20`、`SPEI_season`、`VPD_season_mean`
- id/time keys：`year`、`latitude`、`longitude`、`grid_id`、`prov_id`、`prov_year`

## 缺失值与筛选

- 缺失编码：实测缺失以空值/`NA` 表示；全表扫描未发现 `-999`/`-9999` 哨兵值
- 样本筛选：仓库文档未明确记录完整筛选规则；当前数据文件中 `yield_tons_ha` 全部大于 0
- 异常值处理：`docs/INDEX.md` 与 `docs/VARIABLES.md` 未记录 winsorize/trim 规则

## 复现说明

- 建议排序键：`grid_id`、`year`（或完整键 `year`、`latitude`、`longitude`）
- 预期行数：69,038 行；143 列
- 基础校验：
  - soc 取值范围：本文件无显式 `soc` 字段（N/A）
  - y 取值范围：`yield_tons_ha` 在 [0.2001, 19.9958]；`ln_yield` 在 [-1.6089, 2.9955]
  - 缺失率阈值：仓库未定义统一阈值；当前核心键 `year`、`latitude`、`longitude`、`grid_id`、`prov_id`、`prov_year` 缺失率均为 0%，核心结果变量 `yield_tons_ha`、`ln_yield` 缺失率均为 0%

## 异质性阈值规则（CA-CC GRF）

- 高温指标：
  - `hdd_tmax_ge32`：高温组定义为 `>= p75`
  - `hdd_tmax_ge35`：高温组定义为 `>= p75`
  - `hdd_tmax_ge38`：若 `p75 == 0`，则高温组定义为 `> 0`；否则为 `>= p75`
- 干旱指标：
  - `wd_deficit_et0minuspre`：干旱组定义为 `>= p75`
  - `SPEI_season`（稳健性）：干旱组定义为 `<= p25`
- 土壤水分指标：
  - `gleam_smrz_mean`：低土壤水分组定义为 `<= p25`
- 灌溉指标：
  - `irr_frac`：高灌溉组定义为 `>= p75`
