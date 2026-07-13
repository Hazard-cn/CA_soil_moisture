# 数据资产与处理流程审计报告

> **日期:** 2026-03-28 (v2, 含修正)
> **目的:** 梳理现有原始数据、已处理数据、处理代码、附带文献，识别缺陷与缺口

---

## 一、原始数据清单

### 1. 降水 — `E:\CHM_PRE_0.1dg_19612022.nc`
| 属性 | 值 |
|------|-----|
| 格式 | NetCDF4 (HDF5) |
| 大小 | 20 GB |
| 空间分辨率 | 0.1° (360 lat × 640 lon) |
| 空间范围 | LAT 18.05-53.95°N, LON 72.05-135.95°E (全中国) |
| 时间范围 | 1961-2022, 逐日 (22,645 timesteps) |
| 变量 | `pre` (mm/day), fill_value=-99.9 |
| 附带文献 | 无 |

### 2. SPEI & VPD — `E:\CHM_prec`
| 属性 | 值 |
|------|-----|
| 格式 | NetCDF4 (HDF5) |
| 大小 | ~12 GB |
| SPEI 文件 | CHM_SPEI-1.nc ~ CHM_SPEI-12.nc (月累积尺度1-12个月), CHM_SPEI-2W.nc (2周) |
| VPD 文件 | CHM_VPD.nc (654 MB) |
| 空间分辨率 | 0.1° |
| 附带文献 | **Metadata for CHM_Drought.pdf** (384 KB), **essd-17-837-2025.pdf** (9.3 MB, ESSD论文) |
| 处理代码 | `code\regression\panel_data_gen.ipynb` Cell 16 (v1原始); `data_build/scripts/python/s06_calc_vpd_spei.py` (v2管线) |
| SPEI逻辑 | 按窗口(start_doy→end_doy)计算 scale=end_month-start_month+1，取 CHM_SPEI-{scale}.nc 在 end_month 的值（v1逻辑，2026-04-04同步至v2管线，与v1完全一致 r=1.0） |
| VPD逻辑 | 按窗口月度覆盖天数加权平均取 CHM_VPD.nc 均值 |

### 3. 温度 — 两个目录，同一全国数据 ✅

#### 3a. 完整版 — `E:\daily_temp_CN` (2013-2020, 8年)
| 属性 | 值 |
|------|-----|
| 格式 | NetCDF4 |
| 大小 | 1.6 GB (8文件) |
| 文件 | daily_temp_2013.nc ~ daily_temp_2020.nc |
| 空间分辨率 | 0.1° **(376 lat × 616 lon)** |
| 空间范围 | **LAT 16.03-53.53°N, LON 73.58-135.08°E (全中国 ✅)** |
| 时间范围 | 2013-2020, 逐日 |
| 变量 | t2m_max, t2m_min, t2m_mean |
| 来源 | ERA5 hourly → 逐日聚合 (ERA-temp-combine.ipynb) |
| 用途 | panel_data_gen.ipynb Cell 0 计算HDD/hotdays/百分位 + 长期基准(2013-2020) |

#### 3b. 4年子集 — `E:\Processed_Panel_CN_2016-2019\daily_temp_CN\` (2016-2019)
| 属性 | 值 |
|------|-----|
| 格式 | 与3a完全一致 |
| 文件 | daily_temp_2016.nc ~ daily_temp_2019.nc (3a的子集) |
| 用途 | main_code_CN_v2.ipynb 按物候窗口聚合 t2m_mean/max/min |

> **v3 修正:** 两个目录格点规格完全一致(376×616, 全国16-54°N)。v1审计误判为"仅东北"是因为参考了旧版JSON扫描报告。实测确认：南方(lat~22°N) hotdays_ge32=6-40天、西部(lon<100°E) 3798行均有值，物理合理。

### 4. 土壤水分 (GLEAM) — `E:\GLEAM_soil-mositure`
| 属性 | 值 |
|------|-----|
| 格式 | NetCDF4 |
| 大小 | 22 GB (14文件: 7年×2变量) |
| 文件 | SMrz_2013-2019_GLEAM_v4.2b.nc, SMs_2013-2019_GLEAM_v4.2b.nc |
| 空间分辨率 | 0.1° (全球 1800×3600) |
| 空间范围 | 全球 (裁剪后: 37.85-54.55°N, 114.95-136.15°E) |
| 时间范围 | 2013-2019, 逐日 |
| 变量 | SMrz (根区, m³/m³), SMs (表层, m³/m³), fill=-999.0 |
| 缺失率 | ~16% (海洋/非陆地) |
| 附带文献 | **README_GLEAM4.2.pdf**, **Log_file_GLEAM4.2.pdf**, **s41597-025-04610-y.pdf** (Scientific Data论文) |
| ⚠️ 注意 | GLEAM数据同化中使用了NDVI，可能与产量存在内生性 |

### 5. 参考蒸散 (ET0) — AgERA5 via CDS API
| 属性 | 值 |
|------|-----|
| 来源 | Copernicus Climate Data Store (AgERA5) |
| 变量 | reference_evapotranspiration |
| 时间范围 | 2016-2019, 月份 03-11 |
| 空间范围 | N54.5°, S3°, E136°, W73° |
| 下载脚本 | soil_var_CN.ipynb |

### 6. 土壤属性 — `E:\soilgrids_CN`
| 属性 | 值 |
|------|-----|
| 格式 | GeoTIFF |
| 大小 | 3.2 GB (10文件) |
| 变量 | bdod, clay, phh2o, sand, silt |
| 深度 | 0-5cm, 5-15cm (每变量2层) |
| 空间分辨率 | ~250m (原始), 聚合到 0.1° |
| 时间 | 静态 |
| 来源 | ISRIC SoilGrids |

### 7. 灌溉 — `E:\Irrimap500_irrigation`
| 属性 | 值 |
|------|-----|
| 格式 | GeoTIFF |
| 大小 | 105 MB (20文件) |
| 文件 | 2000.tif ~ 2019.tif |
| 空间分辨率 | 500m |
| 时间范围 | 2000-2019, 年度 |
| 变量 | 灌溉面积比例 |
| 附带文献 | **Published code.py** (7.2 KB), **s41597-022-01522-z.pdf** (Scientific Data论文, 加密) |

### 8. 秸秆还田 (CA/SR) — `E:\CA_CN_2016-2020`
| 属性 | 值 |
|------|-----|
| 格式 | GeoTIFF (uint8) |
| 大小 | 30 MB (5文件) |
| 文件 | classtill_2016.tif ~ classtill_2020.tif |
| 空间分辨率 | ~1km (~0.009°) |
| 空间范围 | 全中国 (67.80-136.52°E, 15.29-54.68°N) |
| 时间范围 | 2016-2020, 年度 |
| 分类值 | 0=背景, 1-2=保护性耕作(CA), 10=常规耕作 |
| 附带文献 | **1-s2.0-S0168169923008979-main.pdf**, **数据说明_2016-2020年全国保护性耕作常规耕作农田分类.docx** |
| 备注 | CA像元趋势递增: 352K(2017) → 672K(2020) |

### 9. 玉米物候 — `E:\ChinaCropPhen1km\maize`
| 属性 | 值 |
|------|-----|
| 格式 | GeoTIFF (uint8/float32/uint16, 因stage异) |
| 大小 | 3.2 GB (60文件: 3 stage × 20年) |
| 空间分辨率 | 1km (Albers ESRI:102025) |
| 时间范围 | 2000-2019, 年度 |
| 变量 | DOY (1-365), nodata=255 |
| 物候期 | V3(三叶期~145DOY), HE(抽穗期), MA(成熟期) |
| ⚠️ dtype不一致 | V3=float32, HE=uint8, MA=uint16 (需统一) |
| 子目录 | clip_N54.5_W115_S38_E136/ (裁剪版) |

### 10. 玉米产量 — `E:\CropProduction_CN_2010-2020_10km`
| 属性 | 值 |
|------|-----|
| 格式 | GeoTIFF |
| 大小 | 1.6 GB (44文件: 4作物×11年) |
| 作物 | 玉米/水稻/小麦/大豆 |
| 空间分辨率 | 10km |
| 时间范围 | 2010-2020 |
| 变量 | 产量 (kilotons/km²) |
| 附带文献 | **readme.txt** |

### 11. 玉米分布 — `E:\Distribution_CN_2001-2020_30m`
| 属性 | 值 |
|------|-----|
| 格式 | GeoTIFF (分省, ~22省/年) |
| 大小 | 5.1 GB (~440文件) |
| 空间分辨率 | 30m |
| 时间范围 | 2001-2020 |
| 坐标系 | WGS84 |

---

## 二、已处理数据

### A. 全国版 — `E:\Processed_Panel_CN_2016-2019` (用于当前回归分析)

所有数据已对齐到 **0.1° 全国ERA参考格网 (376 lat × 616 lon)**。

| 子目录 | 来源 | 变量 | 单文件大小 |
|--------|------|------|-----------|
| `PRE_0.1deg/` | CHM降水 | pre (mm/day) | ~47 MB |
| `daily_temp_CN/` | ERA5温度 | t2m_max, t2m_min | ~195 MB |
| `ET0_0.1deg/` | AgERA5 | ET0 (mm/day) | ~61 MB |
| `SWSM_L123_0.1deg_aligned/` | SWSM | L1/L2/L3 | ~54 MB |
| `GLEAM_SM_0.1deg_TEMPgrid/` | GLEAM | SMrz, SMs | ~400 MB |
| `IRR_0.1deg/` | CIrrMap250→Irrimap500 | irrig_frac (0-1) | ~193 KB |
| `SOIL_0.1deg/` | SoilGrids | bdod/clay/ph/sand/silt | ~230 KB |
| `ChinaCropPhen1km_0.1deg/` | 物候1km | V3/HE/MA DOY | ~420 KB |
| `MaizePheno_CA_0.1deg_v2/` | CA+物候 | CA_ratio + DOY | per year |

**最终面板:** `ML_STAGE_FEATURES_0.1deg_v4_Final/`
- 4个生育阶段: preV3(30天), V3→HE, HE→MA, 全生育期
- 每阶段~45个特征
- 格式: NetCDF + CSV (含 Cleaned_NoMissing 子集)
- **这是 regression_SR 目前使用的 `data_v1_with_climate.csv` 的来源**

### B. 东北版 — `E:\Processed_Panel` (早期版本，仅东北)

| 属性 | 值 |
|------|-----|
| 空间范围 | 39.33-52.33°N, 116.58-134.78°E (仅东北) |
| 格点数 | 7,065 (118 lat × 181 lon) |
| 时间范围 | 2013-2019 (7年) |
| 记录数 | 39,632 grid-years |
| 分辨率 | 0.1° 和 0.05° 两套 |
| 特征数 | ~56个变量 |

**东北版独有内容:**
- `ML_RF_CF_RESULTS/`: 因果森林(Causal Forest) ATE 结果
- `ML_RF_CF_RESULTS_Region/`: 分区域异质性 (黄淮海、北方春播、南方丘陵、西南山区)
- 多个版本迭代: V0, v2, ERA_GLEAM, ERA_SM_V2, FAST
- 两套土壤水分: SWSM + GLEAM
- CRC定义: value/1000 → fraction, 阈值≥0.3为CA

**东北版与全国版差异:**
| 维度 | 东北版 (Processed_Panel) | 全国版 (Processed_Panel_CN) |
|------|------------------------|---------------------------|
| 空间 | 东北 39-52°N | 全中国 16-54°N |
| 年份 | 2013-2019 (7年) | 2016-2019 (4年) |
| 格点 | ~7,000 | ~17,000+ |
| CA来源 | CA_NE_2013-2021_30m (NE only) | CA_CN_2016-2020 (全国) |
| ML分析 | 因果森林完整结果 | 无ML结果 |
| 分辨率 | 0.1° + 0.05° | 0.1° only |

---

## 三、处理代码清单

### A. 全国版流水线 — `code\CN_data_process_2016-2019\` (Jupyter Notebook)

| 脚本 | 输入 | 输出 | 处理内容 |
|------|------|------|---------|
| **Prec.ipynb** | CHM_PRE全球nc | PRE_0.1deg/ | 裁剪中国、对齐ERA格网、-99.9→NaN、排除川藏新 |
| **soil_var_CN.ipynb** | CDS API | ET0_0.1deg/ | 下载AgERA5参考蒸散 (03-11月) |
| **soil_moisture.ipynb** | SWSM 0.05° | SWSM_L123_0.1deg/ | L1/L2/L3, 0.05°→0.1°插值 |
| **Phop.ipynb** | ChinaCropPhen1km tif | ChinaCropPhen1km_0.1deg/ | Albers→WGS84, 1km→0.1°(最近邻), 玉米面积≥2% |
| **crc.ipynb** | CA tif + 物候 | MaizePheno_CA_0.1deg/ | 30m→0.1° 面积加权, CA_ratio = CA像元/玉米像元 |
| **irrigation.ipynb** | CIrrMap250 tif | IRR_0.1deg/ | 250m→0.1° 均值, 0-1缩放, 排除川藏新 |
| **main_code_CN_v2.ipynb** | 上述所有 | ML_STAGE_FEATURES/ | 按物候窗口聚合日数据, HDD/GDD, 合并静态变量 |
| **add_aridity.ipynb** | ML特征CSV | *_with_aridity.csv | 添加干旱指数, 5像素最近有效值填充 |
| **yield.ipynb** | GeoTIFF | 元数据 | 检查GeoTIFF属性 (辅助) |

### A2. 面板生成流水线 — `code\regression\panel_data_gen.ipynb` (17 cells, 关键!)

**这是生成 `data_v1_with_climate.csv` 的最终脚本。** 整体流程：

| Cell | 内容 | 输入 → 输出 |
|------|------|-------------|
| 0 | **主计算** | stage CSV + 逐日temp/GLEAM → HDD/hotdays/SM极端/复合天数/Tmax分位数 |
| 1-3 | 缺失值补充 | 用xarray nearest对齐补缺失 |
| 4-5 | 产量合并 | 合并10km产量数据 |
| 6-7 | 玉米面积 | 添加maizepix/maizefrac |
| 8-9 | 省份信息 | 添加province/prov_id/prov_year |
| 10-11 | 变量标签 | 添加中文label |
| 12-13 | 干旱指数 | 计算aridity_01deg |
| 14 | 合并检查 | 合并所有产量/省份/面积到面板 |
| **15-16** | **SPEI & VPD** | CHM_SPEI-{scale}.nc → SPEI_season; CHM_VPD.nc → VPD_season_mean |

**关键参数 (Cell 0):**
- `TEMP_LONG_DIR`: `E:\daily_temp_CN` (东北版! 2013-2020)
- `GLEAM_PROC_DIR`: `E:\Processed_Panel_CN_2016-2019\GLEAM_SM_0.1deg_TEMPgrid_2013_2019`
- `HOT_ABS_THRESH`: [29, 30, 31, 32, 33, 34, 35, 38, 40]
- `TMAX_Q_LIST`: [0.90, 0.95] (百分位阈值)
- `SM_Q_LIST`: [0.10, 0.20] (SM百分位)
- `COND_HOT_THRESH`: [32, 35] (复合热干天)
- `TMAX_BIN_EDGES`: -5 到 46°C, 3°C间隔

**✅ 已确认:** Cell 0 的 `TEMP_LONG_DIR = E:\daily_temp_CN` 实际是**全国数据**(376×616, 16-54°N, 73-135°E)，目录名有误导但内容正确。

### B. 额外代码 — `code\` (根目录)

| 脚本 | 用途 | 关键发现 |
|------|------|---------|
| **ERA-temp-combine.ipynb** | ERA5 hourly → daily min/max/mean | 按月分块处理避免内存溢出; K→°C; 可输出全国或东北版本 |
| **main_code.ipynb** | **东北版主流水线** (NE master pipeline) | CA 30m 对齐/标准化 + 全部数据扫描 + 面板构建; 输出到 E:\Processed_Panel\ |
| **phen_var.ipynb** | 物候验证 & 抽样 | V3/HE/MA跨年一致性检查; VGP(V3→HE)~70-100天, RGP(HE→MA)~50-80天; 20点抽样 |
| **玉米区位置获取-全国CA数据.ipynb** | 全国玉米区+CA数据探索 | CA分类值计数; 玉米连通域分析; 密度可视化 |

### C. 关键参数对照

| 参数 | 东北版 (main_code) | 全国版 (main_code_CN_v2) |
|------|-------------------|------------------------|
| 参考格网 | daily_temp_2019.nc (NE) | daily_temp_2019.nc (CN) |
| 分析年份 | 2013-2019 | 2016-2019 |
| V3前窗口 | 30天 | 30天 |
| 滞后窗口 | 30天 | 30天 |
| GDD基温 | 10°C | 10°C |
| HDD阈值 | 29-34°C (6个) | 29-34°C (6个) |
| 玉米面积阈值 | 2% | 2% |
| CA来源 | CA_NE_2013-2021 (30m, NE) | CA_CN_2016-2020 (~1km, 全国) |
| CA标准化 | value/1000→fraction, 阈值0.3 | CA像元/玉米像元 ratio |
| 排除省份 | — | 四川、西藏、新疆 |
| 土壤水分 | ESA CCI + SWSM + GLEAM | SWSM + GLEAM |

---

## 四、附带文献汇总

| 数据源 | 文献 | 类型 |
|--------|------|------|
| SPEI/VPD | essd-17-837-2025.pdf | ESSD数据描述论文 |
| SPEI/VPD | Metadata for CHM_Drought.pdf | 元数据说明 |
| GLEAM SM | s41597-025-04610-y.pdf | Scientific Data论文 |
| GLEAM SM | README_GLEAM4.2.pdf + Log_file | 官方文档 |
| CA/SR | 1-s2.0-S0168169923008979-main.pdf | Computers & Electronics in Agriculture |
| CA/SR | 数据说明_2016-2020年…docx | 中文数据说明 |
| 灌溉 | s41597-022-01522-z.pdf (加密) | Scientific Data论文 |
| 灌溉 | Published code.py | 原始处理代码 |
| 产量 | readme.txt | 数据说明 |

---

## 五、数据流全景图

```
原始数据 (E:盘)                          处理代码                           已处理数据
─────────────────────────────────────────────────────────────────────────────────────
D:\ERA5\ERA*.nc                    ──→  ERA-temp-combine.ipynb  ──→  daily_temp_CN/ (全国0.1°)
E:\CHM_PRE_0.1dg_19612022.nc      ──→  Prec.ipynb              ──→  PRE_0.1deg/
AgERA5 (CDS API)                   ──→  soil_var_CN.ipynb       ──→  ET0_0.1deg/
E:\SWSM_soil_moisture/             ──→  soil_moisture.ipynb     ──→  SWSM_L123_0.1deg/
E:\GLEAM_soil-mositure/            ──→  [直接对齐]              ──→  GLEAM_SM_0.1deg/
E:\Irrimap500_irrigation/          ──→  irrigation.ipynb        ──→  IRR_0.1deg/
E:\soilgrids_CN/                   ──→  [直接摄入]              ──→  SOIL_0.1deg/
E:\ChinaCropPhen1km\maize/         ──→  Phop.ipynb              ──→  ChinaCropPhen1km_0.1deg/
E:\CA_CN_2016-2020/                ──→  crc.ipynb               ──→  MaizePheno_CA_0.1deg/
E:\CropProduction_CN_2010-2020_10km ──→ [?? 路径不明]           ──→  产量合并到面板

                                        ↓
                                   main_code_CN_v2.ipynb (主聚合)
                                        ↓
                                   ML_STAGE_FEATURES_0.1deg_v4_Final/ (4 stage CSV)
                                        ↓
                                   ===== 以下在 code\regression\panel_data_gen.ipynb =====
                                        ↓
                                   Cell 0:  读取stage CSV + 逐日temp/GLEAM
                                           → 计算HDD/hotdays/SM极端/复合天数
                                   Cell 1-9: 缺失值/产量/玉米面积/省份合并
                                   Cell 12-13: 干旱指数 (aridity)
                                        ↓
                                   data_v1(with aridity).dta
                                        ↓
E:\CHM_prec/SPEI/ ─────────────→   Cell 16 Part A: SPEI匹配 → SPEI_season
E:\CHM_prec/VPD/  ─────────────→   Cell 16 Part B: VPD窗口均值 → VPD_season_mean
                                        ↓
                                   data_v1_with_climate.csv (69,038行, 143列)
```

---

## 六、缺陷与问题

### ~~A. 空间覆盖不一致~~ ✅ 已排除

温度数据 `E:\daily_temp_CN` 实际覆盖全中国(16-54°N, 73-135°E)，目录名有误导。已验证最终数据中南方/西部格点的HDD/hotdays值物理合理。

### B. 时间窗口过于粗糙 🔴 核心缺陷（本次重构主要动机）

| 现状 | 缺失 |
|------|------|
| 仅4个阶段: preV3(30天), V3→HE, HE→MA, 全生育期 | **V3±10天、HE±10天** 窗口 |
| lag窗口固定30天 | 灵活lag窗口 |
| 无月度/旬级聚合 | 多尺度时间聚合 |

### B. 降水指标极度匮乏 🔴

| 已有 | 缺失 |
|------|------|
| PRE_sum (阶段累积) | 均值、最大日降水、降水强度 |
| — | 干旱天数 (< 1mm)、强降水天数 (≥ 10/20mm) |
| — | 连续干旱天 (CDD) / 连续湿润天 (CWD) |
| — | SPI (不同时间尺度) |
| — | 水分亏缺 (ET0-P deficit) per window |
| — | 降水集中度 |

### C. SPEI和VPD仅有全生育期聚合 🟡 (修正: 非"未使用")

SPEI和VPD已在 `panel_data_gen.ipynb` Cell 16 中处理，但**仅做了全生育期(v3_doy-30→ma_doy)的单一聚合**：
- SPEI: 按月跨度选文件→取end_month nearest值 → `SPEI_season`（1个值/grid-year）
- VPD: 按月份范围取均值 → `VPD_season_mean`（1个值/grid-year）
- **缺失:** 无分阶段/分窗口的SPEI和VPD指标

### D. 温度指标不全 🟡

| 已有 | 缺失 |
|------|------|
| HDD (29-34°C, 6阈值) | 35°C, 38°C, 40°C 阈值 |
| GDD (base 10°C) | 高温天数 (hotdays) |
| t2m_mean/max/min | 基于百分位的极端 (p90/p95) |
| — | 日较差 (DTR = max-min) |
| — | 夜间高温天数 (tmin ≥ threshold) |

### E. 土壤水分处理问题 🟡

| 问题 | 详情 |
|------|------|
| SWSM vs GLEAM 并存 | 两套SM数据源，面板中两套都有 |
| GLEAM含NDVI | 数据同化使用NDVI，可能与产量内生 |
| 无SM极端指标 | 缺少百分位干旱/湿润天数 |

### F. 格网对齐问题 🟡

| 问题 | 详情 |
|------|------|
| CHM降水格网偏移 | CHM与ERA格网最大偏差0.48°，用最近邻对齐 |
| 物候重采样 | 1km→0.1° 最近邻，丢失空间变异性 |
| 物候dtype不一致 | V3=float32, HE=uint8, MA=uint16 |

### G. 产量数据合并路径不明 🟡

yield.ipynb 仅为检查工具，产量如何从10km GeoTIFF合并到0.1°面板的完整路径**未在代码中记录**。

### H. 处理流水线工程问题 🟡

| 问题 | 详情 |
|------|------|
| Jupyter非可复现 | 所有代码为.ipynb，执行顺序不保证 |
| 硬编码路径 | 多处绝对路径 |
| 无单元测试 | 无数据质量自动化检查 |
| 两套独立流水线 | 东北版(main_code) vs 全国版(main_code_CN_v2) 逻辑重复 |

---

## 七、本次 data_build 需要做的事

### 必须做（🔴 高优先级）

| 任务 | 说明 |
|------|------|
| **两套新时间窗口** | 方案A: V3±10天, HE±10天; 方案B: V3→HE, HE→MA |
| **所有气象变量按新窗口重算** | 温度/降水/VPD/SM/ET0 的 mean/sum/min/max/sd |
| **降水全套指标** | CDD/CWD/强降水天/最大日降水/SPI/降水强度/水分亏缺 |
| **VPD窗口聚合** | 数据已有(CHM_VPD.nc)，只缺处理 |
| **SPEI窗口提取** | 已有多尺度SPEI，按窗口匹配提取 |

### 应该做（🟡 中优先级）

| 任务 | 说明 |
|------|------|
| 温度补充指标 | hotdays/夜间高温/DTR/35-40°C HDD/百分位极端 |
| SM极端指标 | 基于百分位的干湿天数 |
| 处理流水线现代化 | Jupyter → .R/.py 可复现脚本 |
| 格网对齐标准化 | 统一所有数据源到同一参考格网 |
| 数据质量自动检查 | 行数/范围/缺失/覆盖率校验 |

### 待定（🟠）

| 任务 | 说明 |
|------|------|
| 更细空间尺度 | < 0.1° 具体多细待定 |
| 产量数据合并文档 | 理清10km→0.1°的产量分配方法 |

---

## 八、JSON扫描报告清单 — `C:\...\data\master\data json`

| 文件 | 对应数据 |
|------|---------|
| chm_pre_scan_report.json | CHM降水 |
| era_daily_temp_scan_report.json | ERA5温度 |
| agera5_et_scan_report.json | AgERA5蒸散 |
| crc_scan_report.json | CA/SR分类 |
| chinacropphen1km_maize_phenology_scan_report.json | 玉米物候 |
| swsm_layer1_scan_report.json | SWSM土壤水分 |
| irrigation_cirrmap250_scan_report.json | 灌溉 |
