---
layout: default
title: 当前数据资产、面板与实证入口
---

# 当前数据资产、面板与实证入口

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate
- Origin Date: 2026-07-14
- Verification Status: VERIFIED
- Version Label: data_asset_inventory_v1
- Verification Scope: 当前机器上的文件存在性、结构、关键哈希、样本规则和代码引用；未重跑完整 V1/V3 数据构建流水线
- Historical Full ETL Replay: CANNOT_VERIFY；缺失历史 V2 快照且 V1 最终 notebook 不在当前仓库

## 一、用途与结论

本文件是后续数据读取、合并、样本筛选和实证分析的首要入口。项目中的数据资产分为四层：L0 是外部原始栅格或 NetCDF；L1 是裁剪、重投影或对齐后的气象、水分和物候数据；L2 是按格网—年份与物候窗口聚合的中间表；L3 是可以直接进入 Stata、R 或 Python 的面板。数据本体均为本地资产，不进入 Git；Git 只保存代码、结构说明、血缘元数据和不含行级数据的结果说明。

截至 2026-07-14，后续操作应按研究问题选择数据入口：历史 V1 分析使用外部 V1 或 `data/processed/analysis_main_sample.dta`；共享的 V3 气候与状态变量优先使用 `data_build/data/processed/data_v3_main.parquet`，Stata 使用同目录的 DTA；当前 GGCP10/G185 分析从 `temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_baseline_suite_analysis_ready.dta` 开始，并从 V3 main 合并 precipitation-defined hot-dry 字段。G185 是规则生成的虚拟样本，不是单独保存的 DTA。

## 二、面板的共同结构

有产量的 V1、V2、V3 和 GGCP10 基础面板均包含 69,038 个格网—年份观测、22,180 个格网和 2016—2019 四年，`grid_id year` 在各自数据内部均无重复，年度观测数分别为 16,432、17,578、17,443 和 17,585。该面板不是 22,180 个格网的四年完全平衡面板，回归前仍须按所用变量检查 complete case 和固定效应支持。

跨版本不能直接假定 `grid_id` 或 `prov_year` 可比较。外部 V1 和 V1 locked panel 的 `grid_id` 范围为 1—26,587；V2/V3 expanded、V3 analysis-ready 和 GGCP10 的 `grid_id` 范围为 84—36,246。两套 69,038 行面板按 `year + round(latitude*10) + round(longitude*10)` 可以一对一完全匹配，并形成 22,180 对一对一 grid crosswalk，但对应行的数值型 `grid_id` 没有一项相同。`prov_year` 在 V3 expanded 与 `v3_analysis_ready.dta` 中也采用不同的分组编码，虽然两者均有 102 个省份—年份组。因此，跨 V1/V2/V3/GGCP10 合并必须使用坐标—年份键或经过验证的 crosswalk；跨分支使用省份—年份固定效应时，应由稳定省份标识与 `year` 在目标样本中重新生成，不得直接复用另一分支的整数编码。

## 三、当前 V3 构建直接使用的源数据

本表不新增机器绝对路径。实际机器定位由 `data_build/scripts/python/config.py` 中列出的配置常量提供；文件大小、维度和可访问状态已经在当前机器上重新读取。`source://` 表示本地外部源数据的逻辑标识。

| 层级 | Source ID / 配置入口 | 当前资产 | 时间与空间结构 | 主要变量与用途 |
|---|---|---:|---|---|
| L1 | `source://phenology-ca-0p1deg` / `PHEN_CA_FILE` | 1 个 NC，2.20 MB | 4×376×616；2016—2019 | `v3_doy`、`he_doy`、`ma_doy`、`maize_frac`、`cropland_frac`、`ca_frac`、`ca_ratio`；V3 索引底板 |
| L1 | `source://daily-temp-cn` / `TEMP_DIR` | 8 个 NC，1.65 GB | 2013—2020 逐日；376×616；16.03—53.53°N、73.58—135.08°E | `t2m_max`、`t2m_min`、`t2m_mean`；温度、HDD、GDD 与高温日 |
| L0 | `source://chm-precip` / `PRECIP_FILE` | 1 个 NC，21.21 GB | 22,645×360×640；1961—2022 逐日 | `pre`，mm/day；降水、干日和 precipitation-defined hot-dry |
| L1 | `source://gleam-aligned` / `GLEAM_DIR` | 7 个 NC，2.94 GB | 2013—2019 逐日；376×616 | `SMrz`、`SMs`，m³/m³；根区和表层土壤水分 |
| L1 | `source://swsm-aligned` / `SWSM_DIR` | 4 个 NC，0.224 GB | 2016—2019；376×616 | `L1`、`L2`、`L3`；脚本将 0—100 转为 0—1；存在下述日期坐标风险 |
| L0/L1 | `source://era5land-sm` / `ERA5L_SM_DIR` | 384 个 NC、6 个 ZIP，4.95 GB | 代表月为 31×386×631；16—54.5°N、73—136°E | `swvl1` 等；ERA5-Land 多层土壤水分 |
| L1 | `source://et0-aligned` / `ET0_DIR` | 4 个 NC，0.254 GB | 2016—2019 逐日；376×616 | `ET0`，mm/day；蒸散和水分亏缺 |
| L0 | `source://chm-vpd` / `VPD_FILE` | 1 个 NC，0.686 GB | 744×360×640；1961-01 至 2022-12 | `VPD`，hPa |
| L0 | `source://chm-spei` / `SPEI_DIR` | 13 个 NC，11.21 GB | SPEI-1 至 SPEI-12 及 2W；代表文件 744×360×640 | 按窗口终止月与动态尺度生成 SPEI |
| L0 | `source://china-maize-phenology` / `CHINA_MAIZE_PHENO_DIR` | 121 个 TIFF 及辅助文件，3.25 GB | V3、HE、MA；2000—2019；1 km Albers | GLEAM rework 的物候窗口与阈值基准 |
| L3 上游 | `data/processed/analysis_main_sample.dta` | 69,038×181，46.17 MB | 2016—2019；V1 `grid_id` 编码空间 | 向 V3 合并产量、SR、灌溉、土壤属性和管理字段 |

物候—CA 底板按 `data_build/scripts/python/s01_load_phenology.py` 的 DOY 与阶段顺序条件筛选后，各年有效格点为 29,852、30,747、30,698 和 31,236，共 122,533 个格网—年份。各气象和水分脚本都在这套索引上聚合，随后由 `data_build/scripts/python/s08_merge_panel.py` 合并有产量的 69,038 行上游面板。

## 四、已确认存在的上游原始或存档数据

这些数据已经完成文件存在性、代表文件结构和代码或历史审计引用核验，但并非全部由当前 V3 构建脚本直接读取。机器定位和原始 notebook 证据见 `data_build/docs/DATA_AUDIT_20260328.md` 及相应上游 notebook；其中部分 notebook 位于仓库外，不能从当前 Git 快照端到端重建。

| Source ID | 当前资产与代表结构 | 与当前面板的关系 |
|---|---|---|
| `source://era5-hourly-temperature` | 约 140 个 NC/辅助项，约 879 GB；代表年为 8,760×510×630，`t2m`，K | 生成 L1 全国逐日温度；当前 V3 不直接读取小时文件 |
| `source://gleam-original` | 14 个主 NC，约 22.82 GB；全球 1,800×3,600，2013—2019 逐日，`SMrz/SMs` | 当前 V3 读取其 0.1° 对齐版本 |
| `source://swsm-original` | 33 个 NC，约 30.58 GB；代表文件 366×751×1,230，`L1/L2/L3` | 当前 V3 读取其 376×616 对齐版本 |
| `source://soilgrids-cn` | 10 个 TIFF，约 3.35 GB；bdod、clay、phh2o、sand、silt，各含 0—5 cm 和 5—15 cm | 通过 0.1° 汇总字段和 locked panel 间接进入 V3 |
| `source://cirrmap250-irrigation` | 21 个 TIFF，约 2.76 GB；2000—2020，float32，0.00225°，EPSG:4326 | 当前全国灌溉 notebook 明确读取 2016—2019 并生成 0.1° `irr_frac` |
| `source://irrimap500-archive` | 20 个 TIFF及文档，约 0.091 GB；2000—2019，uint8，约 0.004617° | 只确认存档存在，未确认进入当前全国主面板；不得与 CIrrMap250 混写 |
| `source://sr-ca-classification` | 5 个年度 TIFF及文档，约 0.022 GB；2016—2020，约 1 km；分类值 0、1、2、10 | 上游 notebook 读取 2016—2019，生成物候—CA 底板中的 `ca_frac/ca_ratio` |
| `source://ggcp10-production-maize` | 2010—2020 玉米栅格；4,320×2,160，1/12°，float32，nodata -9999 | 上游 V1 生产量来源；GGCP10 当前面积分支沿用 V1 `maize_prod` |
| `source://maize-distribution-30m` | 440 个分省年度 TIFF，约 5.19 GB；2001—2020，EPSG:4326 | 只确认资产和结构存在；当前 V1/V3 主流水线中未找到直接读取语句 |
| `local://data_build/data/raw/GGCP10_HarvArea_2010-2020/` | 44 个真实 TIFF、AppleDouble 辅助项和说明；单栅格 4,320×2,160，1/12°，千公顷，nodata -9999 | 当前 GGCP10 aggregated 分支只读取 2016—2019 四张玉米收获面积栅格 |

## 五、V3 中间表与最终视图

| 文件 | 行×列 | 作用 |
|---|---:|---|
| `data_build/data/intermediate/panel_windows.csv` | 122,533×29 | 物候窗口索引底板 |
| `temp_windows.csv` | 122,533×246 | 温度与热量指标 |
| `precip_windows.csv` | 122,533×66 | 降水指标 |
| `sm_gleam_windows.csv` | 122,533×294 | GLEAM 土壤水分指标 |
| `sm_gleam_rework_windows.csv` | 122,533×182 | GLEAM 事件与窗口基准指标 |
| `sm_swsm_windows.csv` | 122,533×294 | SWSM 土壤水分指标 |
| `sm_era5land_windows.csv` | 122,533×306 | ERA5-Land 土壤水分指标 |
| `et0_windows.csv` | 122,533×24 | ET0 与水分亏缺 |
| `vpd_spei_windows.csv` | 122,533×30 | VPD 与 SPEI |
| `compound_windows.csv` | 122,533×240 | 温度×干燥联合胁迫指标 |

最终 V3 共有三个逻辑视图。`data_v3_phenowindows` 为 122,533×1,679，覆盖 36,340 个格网，其中 53,495 行没有产量、SR 或灌溉字段；`data_v3_main` 为有产量的 69,038×1,679 主视图，覆盖 22,180 个格网；`data_v3_noyield.parquet` 为 53,495×1,679 的无产量视图，主要用于气候和物候覆盖扩展，不得直接作为产量回归样本。

`data_v3_main` 同时保存为 Parquet、CSV 和 DTA，当前大小分别为 350,946,854、800,718,842 和 927,979,303 bytes。三种格式的 69,038 个 `grid_id year` 键和抽查的核心变量值一致；Parquet 与 DTA 的键值也完全一致，读取后仅整数存储 dtype 不同。Python/R 优先读取 Parquet，Stata 读取 DTA，CSV 只用于兼容或人工检查。`data_build/docs/VARIABLES_v3.md` 是 1,679 个逻辑字段的字典，适用于 Parquet/CSV；DTA 中有 592 个字段因 Stata 的 32 字符限制使用短 alias，完整映射在 `data_build/output/tables/stata_alias_map_v3.csv`，生成规则在 `data_build/scripts/python/stata_alias_utils.py`。

## 六、已构建的分析面板

### 6.1 核心和历史主面板

| Canonical role / 文件 | 行×列 | 样本或用途 | 当前状态 |
|---|---:|---|---|
| `external://CA_mechanism/data/master/data_v1_with_climate.csv`，工作区相对定位 `../data/master/data_v1_with_climate.csv` | 69,038×143 | 历史 V1；22,180 grids；V1 结果变量口径 | 存在；GB18030 编码；参考数据 |
| `external://CA_mechanism/data/master/data_v1_with_climate_with_county_city.csv` | 69,038×147 | V1 增加 county/city 字段 | 存在；GGCP10 构建上游 |
| `data/processed/analysis_main_sample.dta` | 69,038×181 | V1 Phase 0 locked panel；`main_sample=1` 为 61,795 行、17,832 grids | 存在；历史主分析入口与 V3 合并上游 |
| `data/processed/v2_analysis_ready.dta` | 69,038×649 | V2 analysis；`main_sample=1` 为 62,018 行、17,898 grids | 存在；仅代表修正前历史 V2 分析面板 |
| `data/processed/v3_analysis_ready.dta` | 69,038×772 | corrected V3 analysis；`main_sample=1` 为 62,018 行、17,898 grids | 存在；GGCP10 构建的气候上游之一 |
| `data_build/data/processed/data_v3_main.{parquet,csv,dta}` | 69,038×1,679 | V3 expanded 有产量主视图 | 存在；当前共享气候与状态数据 |
| `data_build/data/processed/data_v3_phenowindows.{parquet,csv,dta}` | 122,533×1,679 | 全部有效物候格网—年份 | 存在；含 53,495 行无产量观测 |
| `data_build/data/processed/data_v3_noyield.parquet` | 53,495×1,679 | 无产量扩展视图 | 存在；不可直接用于产量回归 |

### 6.2 `data/processed/` 中的模块面板

下列文件均实际存在且可读取，每个文件均有 69,038 行。它们是特定历史模块的 analysis-ready 载体，不应因文件名带 `v3` 而与 `data-v3-expanded` 视为同一 schema。

| 文件 | 列数 | 主要模块 |
|---|---:|---|
| `v3prhd_analysis_ready.dta` | 898 | precipitation-defined hot-dry |
| `v3prhdsm_analysis_ready.dta` | 898 | multisource soil-moisture hot-dry |
| `v3decomp_analysis_ready.dta` | 775 | 两方程代数组件/分解 |
| `v3sub_analysis_ready.dta` | 774 | 区域、灌溉和支持样本标签 |
| `v3med_analysis_ready.dta` | 777 | Model-8 两方程实验 |
| `v3med_analysis_ready_plus.dta` | 795 | 增加 soil-moisture definition 字段的 Model-8 面板 |
| `v3proxy_analysis_ready.dta` | 935 | 多源 SM proxy common support |
| `v3bpath_analysis_ready.dta` | 954 | b-path 审计；其 `main_sample` 计数与 V3 base 不同 |
| `v5drymed_analysis_ready.dta` | 919 | drought-only mediator 实验 |

### 6.3 GGCP10 与 G185 面板链

`local://temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_harvarea_agg_sidecar.dta` 为 69,038×10 的面积聚合 sidecar；`v3_analysis_ready_ggcp10_harvarea_agg.dta` 为 69,038×783 的 canonical aggregated base；`ggcp10_core_baseline_analysis_ready.dta` 为 69,038×795 的 full-season compact baseline；`ggcp10_baseline_suite_analysis_ready.dta` 为 69,038×1,182 的当前 GGCP10/G185 基础面板。这些文件内部的 `grid_id year` 均无重复。

GGCP10 重新定义 `yield_tons_ha = maize_prod / ggcp10_maize_area_km2 * 10`，并同时保存 `orig_yield_tons_ha` 等对照字段。未筛选的 GGCP10 aggregated base 因极小收获面积可出现最高约 808 t/ha 的机械高值，因此不能把 69,038 行基础面板直接当作估计样本。当前 G185 mask 包含 `ggcp10_maize_frac >= 0.05`、`main_sample=1`、`0.5 <= yield_tons_ha < 18`、相邻年对数单产跳变排除和 `gleam_smrz_sd >= 0.001`；不启用 `zone_core`、`sm_coverage`、`sr_within`、`years_ge3` 或 `stable_province`。

本轮通过当前统一入口 `scripts/python/g185_v3_data.py::load_g185_sample()` 及其底层 `load_panel`、`unique_variants` 重建后，`assert_g185()` 通过，G185 仍为 46,299 行、13,236 grids，年度观测数为 11,238、11,841、11,677 和 11,543，`grid_id year` 无重复。五个命名区域合计 44,556 行、12,745 grids：NE 20,794/5,715，HHH 12,213/3,324，NW 3,414/1,191，SW 7,232/2,231，SH 903/284；另有 Other 1,743 行、491 grids。G185 的 `yield_tons_ha`、`ln_yield`、`ca`、`irr_frac`、`maize_zone`、`ggcp10_maize_frac`、`gleam_smrz_mean`、`hdd_ge32`、`D_full` 和合并后的 `HotDryPr_full` 均无缺失。上述 46,299 是规则 mask 的 raw support，不是任一具体模型的 complete-case `e(sample)`。

G185 的两个直接物理输入是 GGCP10 baseline suite DTA 和 V3 main DTA；后者提供 `hotdrydays_ge32_pr_lt1`，按同一 V2/V3 `grid_id year` 命名空间一对一合并。任何 G185 行数、规则向量或输入哈希变化都必须创建新的 scale/artifact/run ID，不得覆盖 `scale-g185`。

## 七、变量与结果口径

V1 CSV 的实际 header 是该文件的字段真值，`docs/VARIABLES.md` 只能作为历史部分字典：该文档登记的 96 个字段中有 31 个不在当前 V1，当前 V1 另有 78 列未登记，典型差异是文档写 `pr_sum` 而 V1 实际使用 `pre_sum`。因此，新代码不得只依据 `docs/VARIABLES.md` 猜测字段。

V3 logical schema 使用 `data_build/docs/VARIABLES_v3.md`，DTA 名称再通过 Stata alias map 解析。GGCP10 新增和重定义字段使用 `docs/VARIABLES_GGCP10_HARVAREA.md`。V1 常见极端变量名包括 `hdd_tmax_ge*`、`hotdays_tmax_ge*` 和 `SPEI_season`；当前 G185 基础面板使用 `hdd_ge32`、`hotdays_ge32`、`D_full/W_full`，V3 precipitation hot-dry 使用 `hotdrydays_ge32_pr_lt1`，V3 SPEI 族使用 `spei6_mean` 等命名。不同 schema 的变量名和定义不得互换。

SR/CA 常用字段为 `ca`、`crc_ca_ratio`、`crc_lag1`；V1 中 `crc_lag1` 缺失 5,682 行，`irr_frac` 缺失 4,232 行。69,038 行 V1-family 面板的 `yield_tons_ha` 与 `ln_yield` 无缺失，范围分别为 0.2001—19.9958 和 -1.6089—2.9955。GGCP10 的结果变量分母已经改变，不能与 V1 系数或描述统计直接混合。

## 八、已确认的缺口与风险

1. `data_build/scripts/python/config.py` 中 `V1_DATA` 指向的仓库内 V1 CSV 副本不存在；真正的 V1 CSV 使用 `../data/master/`，但当前 V3 合并脚本实际读取 `data/processed/analysis_main_sample.dta`。后续代码不得把该配置常量当作已验证入口。

2. V2 的 523 列 pre-SPEI-fix 和 621 列 post-SPEI-fix `data_v2_main.dta` 历史快照均已缺失；现存 `v2_analysis_ready.dta` 只能证明历史分析载体，不可替代缺失的上游快照。

3. SWSM 对齐文件的日期坐标存在结构异常：2016 文件缺少 9 月 30 日并多出下一年 1 月 1 日；2017—2019 文件各重复一个 4 月 1 日并缺少 9 月 30 日。`s04b_calc_sm_swsm.py` 当前按数组位置而不是实际日期坐标截取 DOY，因此新的日期敏感 SWSM 结论在使用前必须专项核验或重建。

4. 当前配置使用的全国逐日温度已经实测覆盖 16.03—53.53°N，不是旧审计注释中的东北子集。

5. 当前全国灌溉上游是 CIrrMap250；Irrimap500 只确认存档存在，未确认进入当前面板。30 m 玉米分布也只确认存在，未确认由当前 V1/V3 主流水线直接读取。

6. `temp/2026-04-21_sm_state_audit/sm_state_panel_wide.dta` 当前文件为 122,533×254，但其修改时间晚于历史 v4/v5 使用的 April snapshot；当前文件不能作为该缺失历史快照的替代证据。

7. `docs/DATA_LINEAGE.md` 的 GGCP10 baseline-suite 边目前没有完整列出实际 preamble 合并的 `v3sub_analysis_ready.dta`、V3 main 和 md-event sidecar；执行重建时必须以 `scripts/stata/v6gleambl_step0_preamble.do` 和 `ggcp10_baseline_suite_run_all.do` 的实际输入为准，不能只依赖图中的单条边。

8. V1 的上游流程和 notebook 已被历史审计识别，但最终 notebook 不在当前仓库中，V1 不能从当前 Git 快照单命令端到端重建。其外部 CSV 的当前 SHA-256 和 schema 已验证，形成日期仍不得由文件 mtime 推断。

## 九、完整性核验结果

本轮对 V1 master、V1 county/city、V1 locked panel、V3 main Parquet、V3 main DTA 和 GGCP10 baseline suite 重新计算 SHA-256，六项均与 `quality_reports/lineage/artifact_registry.csv` 完全一致。V3 main 的 Parquet、CSV 和 DTA 均为 69,038 行，键和值检查一致；G185 规则和固定计数已经从当前输入重新计算。证据同时来自文件系统元数据、格式读取器和构建脚本/血缘登记，达到三类来源交叉核验。

进一步的版本与样本真值入口如下：

- `docs/VERSIONING.md`：版本命名和当前入口。
- `docs/DATA_LINEAGE.md`：人类可读数据血缘图；已知缺口见上文。
- `quality_reports/lineage/artifact_registry.csv`：物理文件、哈希、行列数和状态。
- `quality_reports/lineage/sample_rules.csv`：`main_sample`、G185 和其他虚拟样本规则。
- `docs/results/data-v3-expanded/run-manifest.md`、`docs/results/area-ggcp10-aggregated/run-manifest.md`、`docs/results/scale-g185/run-manifest.md`：当前三个关键运行 manifest。

## 十、后续操作规则

每次实证操作开始前，必须记录 canonical data ID、实际读取文件、SHA-256、行列数、键命名空间、样本谓词和结果变量定义；在读入后断言本数据内部的 `grid_id year` 唯一性，并单独报告模型 complete-case 数。跨 V1 与 V2/V3/GGCP10 时使用坐标—年份 crosswalk；跨分支使用 province-year fixed effects 时重新编码。Python 优先使用 Parquet，Stata 使用 DTA 和 alias map。输入哈希、样本规则、结果变量分母、估计对象或公开主张发生变化时，创建新的 artifact/run ID 并更新版本登记；不得覆盖历史 run，也不得把任何数据、日志、模型对象或二进制结果加入 Git。

本文件的最小复核命令为：

```powershell
python scripts/python/version_lineage.py validate --strict
python scripts/python/version_lineage.py build-docs --check
python -m unittest tests.test_version_lineage -v
python .github/scripts/check_repository_policy.py --source index
```
