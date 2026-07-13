# V2 Data Dictionary (523 variables)

**Dataset:** `data_v2_main.parquet`  
**N:** 69,038 grid-year observations  
**Years:** 2016-2019  
**Spatial resolution:** 0.1° grid  
**Generated:** 2026-03-29 (SPEI method updated 2026-04-04)  

---

## 1. Identifiers (6 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `grid_id` | 栅格编号 | Grid cell ID | -- | -- | [84, 3.625e+04] | 0.0% |
| `lat_idx` | 纬度索引 | Latitude index | -- | -- | [24, 318] | 0.0% |
| `latitude` | 纬度 | Latitude | °N | -- | [21.73, 51.13] | 0.0% |
| `lon_idx` | 经度索引 | Longitude index | -- | -- | [20, 610] | 0.0% |
| `longitude` | 经度 | Longitude | °E | -- | [75.58, 134.6] | 0.0% |
| `year` | 年份 | Year | -- | -- | [2016, 2019] | 0.0% |

## 2. Phenology (20 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `ca_ratio` | CA覆盖比例 | Conservation agriculture ratio | 0-1 | -- | [0, 1] | 0.0% |
| `he_doy` | 抽穗期DOY | Heading day of year | DOY | -- | [116, 240] | 0.0% |
| `ma_doy` | 成熟期DOY | Maturity day of year | DOY | -- | [161, 305] | 0.0% |
| `maize_frac` | 玉米种植比例 | Maize planting fraction | 0-1 | -- | [0.02, 0.9793] | 0.0% |
| `v3_doy` | 三叶期DOY | V3 (three-leaf) day of year | DOY | -- | [59, 205] | 0.0% |
| `win_full_days` | 全生育期天数 | full window days | days | Full | [87, 220] | 0.0% |
| `win_full_end` | 全生育期结束DOY | full window end | DOY | Full | [161, 305] | 0.0% |
| `win_full_start` | 全生育期开始DOY | full window start | DOY | Full | [29, 175] | 0.0% |
| `win_hema_days` | HE→MA天数 | hema window days | days | HE→MA | [13, 119] | 0.0% |
| `win_hema_end` | HE→MA结束DOY | hema window end | DOY | HE→MA | [161, 305] | 0.0% |
| `win_hema_start` | HE→MA开始DOY | hema window start | DOY | HE→MA | [116, 240] | 0.0% |
| `win_hepm10_days` | HE±10天数 | hepm10 window days | days | HE±10 | [21, 21] | 0.0% |
| `win_hepm10_end` | HE±10结束DOY | hepm10 window end | DOY | HE±10 | [126, 250] | 0.0% |
| `win_hepm10_start` | HE±10开始DOY | hepm10 window start | DOY | HE±10 | [106, 230] | 0.0% |
| `win_v3he_days` | V3→HE天数 | v3he window days | days | V3→HE | [17, 113] | 0.0% |
| `win_v3he_end` | V3→HE结束DOY | v3he window end | DOY | V3→HE | [116, 240] | 0.0% |
| `win_v3he_start` | V3→HE开始DOY | v3he window start | DOY | V3→HE | [59, 205] | 0.0% |
| `win_v3pm10_days` | V3±10天数 | v3pm10 window days | days | V3±10 | [21, 21] | 0.0% |
| `win_v3pm10_end` | V3±10结束DOY | v3pm10 window end | DOY | V3±10 | [69, 215] | 0.0% |
| `win_v3pm10_start` | V3±10开始DOY | v3pm10 window start | DOY | V3±10 | [49, 195] | 0.0% |

## 3. Temperature (50 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `dtr_max` | 日温差最大值 | Diurnal temperature range max | °C | Full | [7.758, 26.97] | 6.1% |
| `dtr_max_hema` | 日温差最大值 | Diurnal temperature range max | °C | HE→MA | [6.15, 22.68] | 6.1% |
| `dtr_max_hepm10` | 日温差最大值 | Diurnal temperature range max | °C | HE±10 | [5.326, 22.68] | 6.1% |
| `dtr_max_v3he` | 日温差最大值 | Diurnal temperature range max | °C | V3→HE | [6.659, 26.86] | 6.1% |
| `dtr_max_v3pm10` | 日温差最大值 | Diurnal temperature range max | °C | V3±10 | [6.015, 26.97] | 6.1% |
| `dtr_mean` | 日温差均值 | Diurnal temperature range mean | °C | Full | [4.04, 15.61] | 6.1% |
| `dtr_mean_hema` | 日温差均值 | Diurnal temperature range mean | °C | HE→MA | [3.709, 16.48] | 6.1% |
| `dtr_mean_hepm10` | 日温差均值 | Diurnal temperature range mean | °C | HE±10 | [3.619, 17.58] | 6.1% |
| `dtr_mean_v3he` | 日温差均值 | Diurnal temperature range mean | °C | V3→HE | [3.841, 16.39] | 6.1% |
| `dtr_mean_v3pm10` | 日温差均值 | Diurnal temperature range mean | °C | V3±10 | [4.132, 17.58] | 6.1% |
| `t2m_max` | 日均温最大值 | Mean temperature max | °C | Full | [15.65, 41.09] | 6.1% |
| `t2m_max_hema` | 日均温最大值 | Mean temperature max | °C | HE→MA | [14.83, 37.54] | 6.1% |
| `t2m_max_hepm10` | 日均温最大值 | Mean temperature max | °C | HE±10 | [14.71, 39.45] | 6.1% |
| `t2m_max_v3he` | 日均温最大值 | Mean temperature max | °C | V3→HE | [13.69, 40.71] | 6.1% |
| `t2m_max_v3pm10` | 日均温最大值 | Mean temperature max | °C | V3±10 | [7.088, 41.09] | 6.1% |
| `t2m_mean` | 日均温均值 | Mean temperature mean | °C | Full | [9.546, 31.53] | 6.1% |
| `t2m_mean_hema` | 日均温均值 | Mean temperature mean | °C | HE→MA | [12.91, 31.1] | 6.1% |
| `t2m_mean_hepm10` | 日均温均值 | Mean temperature mean | °C | HE±10 | [12.98, 35.11] | 6.1% |
| `t2m_mean_v3he` | 日均温均值 | Mean temperature mean | °C | V3→HE | [8.69, 34.7] | 6.1% |
| `t2m_mean_v3pm10` | 日均温均值 | Mean temperature mean | °C | V3±10 | [4.082, 36.34] | 6.1% |
| `t2m_min` | 日均温最小值 | Mean temperature min | °C | Full | [-7.174, 23.13] | 6.1% |
| `t2m_min_hema` | 日均温最小值 | Mean temperature min | °C | HE→MA | [2.47, 27.11] | 6.1% |
| `t2m_min_hepm10` | 日均温最小值 | Mean temperature min | °C | HE±10 | [9.892, 31.91] | 6.1% |
| `t2m_min_v3he` | 日均温最小值 | Mean temperature min | °C | V3→HE | [-2.762, 30.92] | 6.1% |
| `t2m_min_v3pm10` | 日均温最小值 | Mean temperature min | °C | V3±10 | [-6.135, 32.53] | 6.1% |
| `t2m_sd` | 日均温标准差 | Mean temperature std dev | °C | Full | [1.04, 7.719] | 6.1% |
| `t2m_sd_hema` | 日均温标准差 | Mean temperature std dev | °C | HE→MA | [0.6201, 6.473] | 6.1% |
| `t2m_sd_hepm10` | 日均温标准差 | Mean temperature std dev | °C | HE±10 | [0.4272, 5.429] | 6.1% |
| `t2m_sd_v3he` | 日均温标准差 | Mean temperature std dev | °C | V3→HE | [0.7004, 6.066] | 6.1% |
| `t2m_sd_v3pm10` | 日均温标准差 | Mean temperature std dev | °C | V3±10 | [0.5276, 6.03] | 6.1% |
| `tmax_max` | 日最高温最大值 | Maximum temperature max | °C | Full | [20.4, 46.9] | 6.1% |
| `tmax_max_hema` | 日最高温最大值 | Maximum temperature max | °C | HE→MA | [19.37, 43.85] | 6.1% |
| `tmax_max_hepm10` | 日最高温最大值 | Maximum temperature max | °C | HE±10 | [19.02, 45.37] | 6.1% |
| `tmax_max_v3he` | 日最高温最大值 | Maximum temperature max | °C | V3→HE | [18.63, 46.9] | 6.1% |
| `tmax_max_v3pm10` | 日最高温最大值 | Maximum temperature max | °C | V3±10 | [12.06, 46.84] | 6.1% |
| `tmax_mean` | 日最高温均值 | Maximum temperature mean | °C | Full | [14.06, 37.07] | 6.1% |
| `tmax_mean_hema` | 日最高温均值 | Maximum temperature mean | °C | HE→MA | [16.87, 36.87] | 6.1% |
| `tmax_mean_hepm10` | 日最高温均值 | Maximum temperature mean | °C | HE±10 | [15.88, 41.05] | 6.1% |
| `tmax_mean_v3he` | 日最高温均值 | Maximum temperature mean | °C | V3→HE | [14.48, 40.37] | 6.1% |
| `tmax_mean_v3pm10` | 日最高温均值 | Maximum temperature mean | °C | V3±10 | [8.432, 42.13] | 6.1% |
| `tmin_mean` | 日最低温均值 | Minimum temperature mean | °C | Full | [1.181, 25.77] | 6.1% |
| `tmin_mean_hema` | 日最低温均值 | Minimum temperature mean | °C | HE→MA | [4.729, 27.6] | 6.1% |
| `tmin_mean_hepm10` | 日最低温均值 | Minimum temperature mean | °C | HE±10 | [3.47, 28.3] | 6.1% |
| `tmin_mean_v3he` | 日最低温均值 | Minimum temperature mean | °C | V3→HE | [-0.04508, 27.86] | 6.1% |
| `tmin_mean_v3pm10` | 日最低温均值 | Minimum temperature mean | °C | V3±10 | [-3.89, 28.23] | 6.1% |
| `tmin_min` | 日最低温最小值 | Minimum temperature min | °C | Full | [-16.33, 20.09] | 6.1% |
| `tmin_min_hema` | 日最低温最小值 | Minimum temperature min | °C | HE→MA | [-3.624, 25] | 6.1% |
| `tmin_min_hepm10` | 日最低温最小值 | Minimum temperature min | °C | HE±10 | [1.457, 26.45] | 6.1% |
| `tmin_min_v3he` | 日最低温最小值 | Minimum temperature min | °C | V3→HE | [-11.01, 25.21] | 6.1% |
| `tmin_min_v3pm10` | 日最低温最小值 | Minimum temperature min | °C | V3±10 | [-12.24, 25] | 6.1% |

## 4. Heat Indices (130 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `gdd_ge10` | 生长度日(>=10°C) | Growing degree days (base 10°C) | °C·days | Full | [0, 3196] | 0.0% |
| `gdd_ge10_hema` | 生长度日(>=10°C) | Growing degree days (base 10°C) | °C·days | HE→MA | [0, 1658] | 0.0% |
| `gdd_ge10_hepm10` | 生长度日(>=10°C) | Growing degree days (base 10°C) | °C·days | HE±10 | [0, 527.3] | 0.0% |
| `gdd_ge10_v3he` | 生长度日(>=10°C) | Growing degree days (base 10°C) | °C·days | V3→HE | [0, 1880] | 0.0% |
| `gdd_ge10_v3pm10` | 生长度日(>=10°C) | Growing degree days (base 10°C) | °C·days | V3±10 | [0, 553.2] | 0.0% |
| `hdd_ge29` | 热度日(>=29°C) | Heating degree days (Tmax>=29°C) | °C·days | Full | [0, 1236] | 0.0% |
| `hdd_ge29_hema` | 热度日(>=29°C) | Heating degree days (Tmax>=29°C) | °C·days | HE→MA | [0, 406.7] | 0.0% |
| `hdd_ge29_hepm10` | 热度日(>=29°C) | Heating degree days (Tmax>=29°C) | °C·days | HE±10 | [0, 253] | 0.0% |
| `hdd_ge29_v3he` | 热度日(>=29°C) | Heating degree days (Tmax>=29°C) | °C·days | V3→HE | [0, 763.3] | 0.0% |
| `hdd_ge29_v3pm10` | 热度日(>=29°C) | Heating degree days (Tmax>=29°C) | °C·days | V3±10 | [0, 275.8] | 0.0% |
| `hdd_ge30` | 热度日(>=30°C) | Heating degree days (Tmax>=30°C) | °C·days | Full | [0, 1096] | 0.0% |
| `hdd_ge30_hema` | 热度日(>=30°C) | Heating degree days (Tmax>=30°C) | °C·days | HE→MA | [0, 359] | 0.0% |
| `hdd_ge30_hepm10` | 热度日(>=30°C) | Heating degree days (Tmax>=30°C) | °C·days | HE±10 | [0, 232] | 0.0% |
| `hdd_ge30_v3he` | 热度日(>=30°C) | Heating degree days (Tmax>=30°C) | °C·days | V3→HE | [0, 683.9] | 0.0% |
| `hdd_ge30_v3pm10` | 热度日(>=30°C) | Heating degree days (Tmax>=30°C) | °C·days | V3±10 | [0, 254.8] | 0.0% |
| `hdd_ge31` | 热度日(>=31°C) | Heating degree days (Tmax>=31°C) | °C·days | Full | [0, 957.8] | 0.0% |
| `hdd_ge31_hema` | 热度日(>=31°C) | Heating degree days (Tmax>=31°C) | °C·days | HE→MA | [0, 312.4] | 0.0% |
| `hdd_ge31_hepm10` | 热度日(>=31°C) | Heating degree days (Tmax>=31°C) | °C·days | HE±10 | [0, 211] | 0.0% |
| `hdd_ge31_v3he` | 热度日(>=31°C) | Heating degree days (Tmax>=31°C) | °C·days | V3→HE | [0, 614.1] | 0.0% |
| `hdd_ge31_v3pm10` | 热度日(>=31°C) | Heating degree days (Tmax>=31°C) | °C·days | V3±10 | [0, 233.8] | 0.0% |
| `hdd_ge32` | 热度日(>=32°C) | Heating degree days (Tmax>=32°C) | °C·days | Full | [0, 825.9] | 0.0% |
| `hdd_ge32_hema` | 热度日(>=32°C) | Heating degree days (Tmax>=32°C) | °C·days | HE→MA | [0, 267] | 0.0% |
| `hdd_ge32_hepm10` | 热度日(>=32°C) | Heating degree days (Tmax>=32°C) | °C·days | HE±10 | [0, 190] | 0.0% |
| `hdd_ge32_v3he` | 热度日(>=32°C) | Heating degree days (Tmax>=32°C) | °C·days | V3→HE | [0, 546.3] | 0.0% |
| `hdd_ge32_v3pm10` | 热度日(>=32°C) | Heating degree days (Tmax>=32°C) | °C·days | V3±10 | [0, 212.8] | 0.0% |
| `hdd_ge33` | 热度日(>=33°C) | Heating degree days (Tmax>=33°C) | °C·days | Full | [0, 702.2] | 0.0% |
| `hdd_ge33_hema` | 热度日(>=33°C) | Heating degree days (Tmax>=33°C) | °C·days | HE→MA | [0, 223.6] | 0.0% |
| `hdd_ge33_hepm10` | 热度日(>=33°C) | Heating degree days (Tmax>=33°C) | °C·days | HE±10 | [0, 169] | 0.0% |
| `hdd_ge33_v3he` | 热度日(>=33°C) | Heating degree days (Tmax>=33°C) | °C·days | V3→HE | [0, 480.7] | 0.0% |
| `hdd_ge33_v3pm10` | 热度日(>=33°C) | Heating degree days (Tmax>=33°C) | °C·days | V3±10 | [0, 191.8] | 0.0% |
| `hdd_ge34` | 热度日(>=34°C) | Heating degree days (Tmax>=34°C) | °C·days | Full | [0, 586.2] | 0.0% |
| `hdd_ge34_hema` | 热度日(>=34°C) | Heating degree days (Tmax>=34°C) | °C·days | HE→MA | [0, 182.8] | 0.0% |
| `hdd_ge34_hepm10` | 热度日(>=34°C) | Heating degree days (Tmax>=34°C) | °C·days | HE±10 | [0, 148] | 0.0% |
| `hdd_ge34_v3he` | 热度日(>=34°C) | Heating degree days (Tmax>=34°C) | °C·days | V3→HE | [0, 416.3] | 0.0% |
| `hdd_ge34_v3pm10` | 热度日(>=34°C) | Heating degree days (Tmax>=34°C) | °C·days | V3±10 | [0, 170.8] | 0.0% |
| `hdd_ge35` | 热度日(>=35°C) | Heating degree days (Tmax>=35°C) | °C·days | Full | [0, 478.6] | 0.0% |
| `hdd_ge35_hema` | 热度日(>=35°C) | Heating degree days (Tmax>=35°C) | °C·days | HE→MA | [0, 148] | 0.0% |
| `hdd_ge35_hepm10` | 热度日(>=35°C) | Heating degree days (Tmax>=35°C) | °C·days | HE±10 | [0, 127] | 0.0% |
| `hdd_ge35_v3he` | 热度日(>=35°C) | Heating degree days (Tmax>=35°C) | °C·days | V3→HE | [0, 352.7] | 0.0% |
| `hdd_ge35_v3pm10` | 热度日(>=35°C) | Heating degree days (Tmax>=35°C) | °C·days | V3±10 | [0, 149.8] | 0.0% |
| `hdd_ge38` | 热度日(>=38°C) | Heating degree days (Tmax>=38°C) | °C·days | Full | [0, 207.8] | 0.0% |
| `hdd_ge38_hema` | 热度日(>=38°C) | Heating degree days (Tmax>=38°C) | °C·days | HE→MA | [0, 58.91] | 0.0% |
| `hdd_ge38_hepm10` | 热度日(>=38°C) | Heating degree days (Tmax>=38°C) | °C·days | HE±10 | [0, 65.44] | 0.0% |
| `hdd_ge38_v3he` | 热度日(>=38°C) | Heating degree days (Tmax>=38°C) | °C·days | V3→HE | [0, 176.4] | 0.0% |
| `hdd_ge38_v3pm10` | 热度日(>=38°C) | Heating degree days (Tmax>=38°C) | °C·days | V3±10 | [0, 88.14] | 0.0% |
| `hdd_ge40` | 热度日(>=40°C) | Heating degree days (Tmax>=40°C) | °C·days | Full | [0, 94.13] | 0.0% |
| `hdd_ge40_hema` | 热度日(>=40°C) | Heating degree days (Tmax>=40°C) | °C·days | HE→MA | [0, 24.66] | 0.0% |
| `hdd_ge40_hepm10` | 热度日(>=40°C) | Heating degree days (Tmax>=40°C) | °C·days | HE±10 | [0, 30.39] | 0.0% |
| `hdd_ge40_v3he` | 热度日(>=40°C) | Heating degree days (Tmax>=40°C) | °C·days | V3→HE | [0, 87.79] | 0.0% |
| `hdd_ge40_v3pm10` | 热度日(>=40°C) | Heating degree days (Tmax>=40°C) | °C·days | V3±10 | [0, 48.94] | 0.0% |
| `hdd_ge_basep90` | 热度日(>=P90) | HDD (Tmax>=P90 baseline) | °C·days | Full | [0, 142.4] | 0.0% |
| `hdd_ge_basep90_hema` | 热度日(>=P90) | HDD (Tmax>=P90 baseline) | °C·days | HE→MA | [0, 80.65] | 0.0% |
| `hdd_ge_basep90_hepm10` | 热度日(>=P90) | HDD (Tmax>=P90 baseline) | °C·days | HE±10 | [0, 72.8] | 0.0% |
| `hdd_ge_basep90_v3he` | 热度日(>=P90) | HDD (Tmax>=P90 baseline) | °C·days | V3→HE | [0, 112.4] | 0.0% |
| `hdd_ge_basep90_v3pm10` | 热度日(>=P90) | HDD (Tmax>=P90 baseline) | °C·days | V3±10 | [0, 83.69] | 0.0% |
| `hdd_ge_basep95` | 热度日(>=P95) | HDD (Tmax>=P95 baseline) | °C·days | Full | [0, 84.74] | 0.0% |
| `hdd_ge_basep95_hema` | 热度日(>=P95) | HDD (Tmax>=P95 baseline) | °C·days | HE→MA | [0, 51.68] | 0.0% |
| `hdd_ge_basep95_hepm10` | 热度日(>=P95) | HDD (Tmax>=P95 baseline) | °C·days | HE±10 | [0, 49.9] | 0.0% |
| `hdd_ge_basep95_v3he` | 热度日(>=P95) | HDD (Tmax>=P95 baseline) | °C·days | V3→HE | [0, 63.13] | 0.0% |
| `hdd_ge_basep95_v3pm10` | 热度日(>=P95) | HDD (Tmax>=P95 baseline) | °C·days | V3±10 | [0, 56.09] | 0.0% |
| `hotdays_ge29` | 高温天数(>=29°C) | Hot days (Tmax>=29°C) | days | Full | [0, 151] | 0.0% |
| `hotdays_ge29_hema` | 高温天数(>=29°C) | Hot days (Tmax>=29°C) | days | HE→MA | [0, 81] | 0.0% |
| `hotdays_ge29_hepm10` | 高温天数(>=29°C) | Hot days (Tmax>=29°C) | days | HE±10 | [0, 21] | 0.0% |
| `hotdays_ge29_v3he` | 高温天数(>=29°C) | Hot days (Tmax>=29°C) | days | V3→HE | [0, 83] | 0.0% |
| `hotdays_ge29_v3pm10` | 高温天数(>=29°C) | Hot days (Tmax>=29°C) | days | V3±10 | [0, 21] | 0.0% |
| `hotdays_ge30` | 高温天数(>=30°C) | Hot days (Tmax>=30°C) | days | Full | [0, 140] | 0.0% |
| `hotdays_ge30_hema` | 高温天数(>=30°C) | Hot days (Tmax>=30°C) | days | HE→MA | [0, 69] | 0.0% |
| `hotdays_ge30_hepm10` | 高温天数(>=30°C) | Hot days (Tmax>=30°C) | days | HE±10 | [0, 21] | 0.0% |
| `hotdays_ge30_v3he` | 高温天数(>=30°C) | Hot days (Tmax>=30°C) | days | V3→HE | [0, 82] | 0.0% |
| `hotdays_ge30_v3pm10` | 高温天数(>=30°C) | Hot days (Tmax>=30°C) | days | V3±10 | [0, 21] | 0.0% |
| `hotdays_ge31` | 高温天数(>=31°C) | Hot days (Tmax>=31°C) | days | Full | [0, 134] | 0.0% |
| `hotdays_ge31_hema` | 高温天数(>=31°C) | Hot days (Tmax>=31°C) | days | HE→MA | [0, 60] | 0.0% |
| `hotdays_ge31_hepm10` | 高温天数(>=31°C) | Hot days (Tmax>=31°C) | days | HE±10 | [0, 21] | 0.0% |
| `hotdays_ge31_v3he` | 高温天数(>=31°C) | Hot days (Tmax>=31°C) | days | V3→HE | [0, 79] | 0.0% |
| `hotdays_ge31_v3pm10` | 高温天数(>=31°C) | Hot days (Tmax>=31°C) | days | V3±10 | [0, 21] | 0.0% |
| `hotdays_ge32` | 高温天数(>=32°C) | Hot days (Tmax>=32°C) | days | Full | [0, 128] | 0.0% |
| `hotdays_ge32_hema` | 高温天数(>=32°C) | Hot days (Tmax>=32°C) | days | HE→MA | [0, 55] | 0.0% |
| `hotdays_ge32_hepm10` | 高温天数(>=32°C) | Hot days (Tmax>=32°C) | days | HE±10 | [0, 21] | 0.0% |
| `hotdays_ge32_v3he` | 高温天数(>=32°C) | Hot days (Tmax>=32°C) | days | V3→HE | [0, 78] | 0.0% |
| `hotdays_ge32_v3pm10` | 高温天数(>=32°C) | Hot days (Tmax>=32°C) | days | V3±10 | [0, 21] | 0.0% |
| `hotdays_ge33` | 高温天数(>=33°C) | Hot days (Tmax>=33°C) | days | Full | [0, 120] | 0.0% |
| `hotdays_ge33_hema` | 高温天数(>=33°C) | Hot days (Tmax>=33°C) | days | HE→MA | [0, 45] | 0.0% |
| `hotdays_ge33_hepm10` | 高温天数(>=33°C) | Hot days (Tmax>=33°C) | days | HE±10 | [0, 21] | 0.0% |
| `hotdays_ge33_v3he` | 高温天数(>=33°C) | Hot days (Tmax>=33°C) | days | V3→HE | [0, 75] | 0.0% |
| `hotdays_ge33_v3pm10` | 高温天数(>=33°C) | Hot days (Tmax>=33°C) | days | V3±10 | [0, 21] | 0.0% |
| `hotdays_ge34` | 高温天数(>=34°C) | Hot days (Tmax>=34°C) | days | Full | [0, 111] | 0.0% |
| `hotdays_ge34_hema` | 高温天数(>=34°C) | Hot days (Tmax>=34°C) | days | HE→MA | [0, 40] | 0.0% |
| `hotdays_ge34_hepm10` | 高温天数(>=34°C) | Hot days (Tmax>=34°C) | days | HE±10 | [0, 21] | 0.0% |
| `hotdays_ge34_v3he` | 高温天数(>=34°C) | Hot days (Tmax>=34°C) | days | V3→HE | [0, 72] | 0.0% |
| `hotdays_ge34_v3pm10` | 高温天数(>=34°C) | Hot days (Tmax>=34°C) | days | V3±10 | [0, 21] | 0.0% |
| `hotdays_ge35` | 高温天数(>=35°C) | Hot days (Tmax>=35°C) | days | Full | [0, 106] | 0.0% |
| `hotdays_ge35_hema` | 高温天数(>=35°C) | Hot days (Tmax>=35°C) | days | HE→MA | [0, 37] | 0.0% |
| `hotdays_ge35_hepm10` | 高温天数(>=35°C) | Hot days (Tmax>=35°C) | days | HE±10 | [0, 21] | 0.0% |
| `hotdays_ge35_v3he` | 高温天数(>=35°C) | Hot days (Tmax>=35°C) | days | V3→HE | [0, 69] | 0.0% |
| `hotdays_ge35_v3pm10` | 高温天数(>=35°C) | Hot days (Tmax>=35°C) | days | V3±10 | [0, 21] | 0.0% |
| `hotdays_ge38` | 高温天数(>=38°C) | Hot days (Tmax>=38°C) | days | Full | [0, 71] | 0.0% |
| `hotdays_ge38_hema` | 高温天数(>=38°C) | Hot days (Tmax>=38°C) | days | HE→MA | [0, 25] | 0.0% |
| `hotdays_ge38_hepm10` | 高温天数(>=38°C) | Hot days (Tmax>=38°C) | days | HE±10 | [0, 19] | 0.0% |
| `hotdays_ge38_v3he` | 高温天数(>=38°C) | Hot days (Tmax>=38°C) | days | V3→HE | [0, 52] | 0.0% |
| `hotdays_ge38_v3pm10` | 高温天数(>=38°C) | Hot days (Tmax>=38°C) | days | V3±10 | [0, 20] | 0.0% |
| `hotdays_ge40` | 高温天数(>=40°C) | Hot days (Tmax>=40°C) | days | Full | [0, 43] | 0.0% |
| `hotdays_ge40_hema` | 高温天数(>=40°C) | Hot days (Tmax>=40°C) | days | HE→MA | [0, 15] | 0.0% |
| `hotdays_ge40_hepm10` | 高温天数(>=40°C) | Hot days (Tmax>=40°C) | days | HE±10 | [0, 16] | 0.0% |
| `hotdays_ge40_v3he` | 高温天数(>=40°C) | Hot days (Tmax>=40°C) | days | V3→HE | [0, 37] | 0.0% |
| `hotdays_ge40_v3pm10` | 高温天数(>=40°C) | Hot days (Tmax>=40°C) | days | V3±10 | [0, 17] | 0.0% |
| `hotdays_ge_basep90` | 高温天数(>=P90) | Hot days (Tmax>=P90 baseline) | days | Full | [0, 60] | 0.0% |
| `hotdays_ge_basep90_hema` | 高温天数(>=P90) | Hot days (Tmax>=P90 baseline) | days | HE→MA | [0, 38] | 0.0% |
| `hotdays_ge_basep90_hepm10` | 高温天数(>=P90) | Hot days (Tmax>=P90 baseline) | days | HE±10 | [0, 21] | 0.0% |
| `hotdays_ge_basep90_v3he` | 高温天数(>=P90) | Hot days (Tmax>=P90 baseline) | days | V3→HE | [0, 48] | 0.0% |
| `hotdays_ge_basep90_v3pm10` | 高温天数(>=P90) | Hot days (Tmax>=P90 baseline) | days | V3±10 | [0, 21] | 0.0% |
| `hotdays_ge_basep95` | 高温天数(>=P95) | Hot days (Tmax>=P95 baseline) | days | Full | [0, 41] | 0.0% |
| `hotdays_ge_basep95_hema` | 高温天数(>=P95) | Hot days (Tmax>=P95 baseline) | days | HE→MA | [0, 26] | 0.0% |
| `hotdays_ge_basep95_hepm10` | 高温天数(>=P95) | Hot days (Tmax>=P95 baseline) | days | HE±10 | [0, 19] | 0.0% |
| `hotdays_ge_basep95_v3he` | 高温天数(>=P95) | Hot days (Tmax>=P95 baseline) | days | V3→HE | [0, 32] | 0.0% |
| `hotdays_ge_basep95_v3pm10` | 高温天数(>=P95) | Hot days (Tmax>=P95 baseline) | days | V3±10 | [0, 21] | 0.0% |
| `nightheat_ge20` | 夜间高温(>=20°C) | Night heat days (Tmin>=20°C) | days | Full | [0, 161] | 0.0% |
| `nightheat_ge20_hema` | 夜间高温(>=20°C) | Night heat days (Tmin>=20°C) | days | HE→MA | [0, 97] | 0.0% |
| `nightheat_ge20_hepm10` | 夜间高温(>=20°C) | Night heat days (Tmin>=20°C) | days | HE±10 | [0, 21] | 0.0% |
| `nightheat_ge20_v3he` | 夜间高温(>=20°C) | Night heat days (Tmin>=20°C) | days | V3→HE | [0, 82] | 0.0% |
| `nightheat_ge20_v3pm10` | 夜间高温(>=20°C) | Night heat days (Tmin>=20°C) | days | V3±10 | [0, 21] | 0.0% |
| `nightheat_ge22` | 夜间高温(>=22°C) | Night heat days (Tmin>=22°C) | days | Full | [0, 130] | 0.0% |
| `nightheat_ge22_hema` | 夜间高温(>=22°C) | Night heat days (Tmin>=22°C) | days | HE→MA | [0, 92] | 0.0% |
| `nightheat_ge22_hepm10` | 夜间高温(>=22°C) | Night heat days (Tmin>=22°C) | days | HE±10 | [0, 21] | 0.0% |
| `nightheat_ge22_v3he` | 夜间高温(>=22°C) | Night heat days (Tmin>=22°C) | days | V3→HE | [0, 75] | 0.0% |
| `nightheat_ge22_v3pm10` | 夜间高温(>=22°C) | Night heat days (Tmin>=22°C) | days | V3±10 | [0, 21] | 0.0% |
| `nightheat_ge24` | 夜间高温(>=24°C) | Night heat days (Tmin>=24°C) | days | Full | [0, 95] | 0.0% |
| `nightheat_ge24_hema` | 夜间高温(>=24°C) | Night heat days (Tmin>=24°C) | days | HE→MA | [0, 82] | 0.0% |
| `nightheat_ge24_hepm10` | 夜间高温(>=24°C) | Night heat days (Tmin>=24°C) | days | HE±10 | [0, 21] | 0.0% |
| `nightheat_ge24_v3he` | 夜间高温(>=24°C) | Night heat days (Tmin>=24°C) | days | V3→HE | [0, 61] | 0.0% |
| `nightheat_ge24_v3pm10` | 夜间高温(>=24°C) | Night heat days (Tmin>=24°C) | days | V3±10 | [0, 21] | 0.0% |

## 5. Precipitation (50 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `drydays_lt1` | 干旱天(<1mm) | Dry days (precip<1mm) | days | Full | [0, 158] | 0.0% |
| `drydays_lt1_hema` | 干旱天(<1mm) | Dry days (precip<1mm) | days | HE→MA | [0, 67] | 0.0% |
| `drydays_lt1_hepm10` | 干旱天(<1mm) | Dry days (precip<1mm) | days | HE±10 | [0, 21] | 0.0% |
| `drydays_lt1_v3he` | 干旱天(<1mm) | Dry days (precip<1mm) | days | V3→HE | [0, 90] | 0.0% |
| `drydays_lt1_v3pm10` | 干旱天(<1mm) | Dry days (precip<1mm) | days | V3±10 | [0, 21] | 0.0% |
| `max_cdd` | 最大连续干旱天 | Maximum consecutive dry days | days | Full | [0, 114] | 0.0% |
| `max_cdd_hema` | 最大连续干旱天 | Maximum consecutive dry days | days | HE→MA | [0, 52] | 0.0% |
| `max_cdd_hepm10` | 最大连续干旱天 | Maximum consecutive dry days | days | HE±10 | [0, 21] | 0.0% |
| `max_cdd_v3he` | 最大连续干旱天 | Maximum consecutive dry days | days | V3→HE | [0, 83] | 0.0% |
| `max_cdd_v3pm10` | 最大连续干旱天 | Maximum consecutive dry days | days | V3±10 | [0, 21] | 0.0% |
| `max_cwd` | 最大连续湿润天 | Maximum consecutive wet days | days | Full | [0, 80] | 0.0% |
| `max_cwd_hema` | 最大连续湿润天 | Maximum consecutive wet days | days | HE→MA | [0, 62] | 0.0% |
| `max_cwd_hepm10` | 最大连续湿润天 | Maximum consecutive wet days | days | HE±10 | [0, 21] | 0.0% |
| `max_cwd_v3he` | 最大连续湿润天 | Maximum consecutive wet days | days | V3→HE | [0, 55] | 0.0% |
| `max_cwd_v3pm10` | 最大连续湿润天 | Maximum consecutive wet days | days | V3±10 | [0, 20] | 0.0% |
| `pr_intensity` | 降水强度 | Precipitation intensity | mm | Full | [0, 33.73] | 0.0% |
| `pr_intensity_hema` | 降水强度 | Precipitation intensity | mm | HE→MA | [0, 66.26] | 0.0% |
| `pr_intensity_hepm10` | 降水强度 | Precipitation intensity | mm | HE±10 | [0, 65.03] | 0.0% |
| `pr_intensity_v3he` | 降水强度 | Precipitation intensity | mm | V3→HE | [0, 39.39] | 0.0% |
| `pr_intensity_v3pm10` | 降水强度 | Precipitation intensity | mm | V3±10 | [0, 80.85] | 0.0% |
| `pr_max` | 降水最大值 | Precipitation max | mm | Full | [1.45, 679.6] | 0.0% |
| `pr_max_hema` | 降水最大值 | Precipitation max | mm | HE→MA | [0.03, 344.1] | 0.0% |
| `pr_max_hepm10` | 降水最大值 | Precipitation max | mm | HE±10 | [0, 344.1] | 0.0% |
| `pr_max_v3he` | 降水最大值 | Precipitation max | mm | V3→HE | [0.04, 313.2] | 0.0% |
| `pr_max_v3pm10` | 降水最大值 | Precipitation max | mm | V3±10 | [0, 191.9] | 0.0% |
| `pr_mean` | 降水均值 | Precipitation mean | mm | Full | [0.07098, 14.92] | 0.0% |
| `pr_mean_hema` | 降水均值 | Precipitation mean | mm | HE→MA | [0.002174, 30.47] | 0.0% |
| `pr_mean_hepm10` | 降水均值 | Precipitation mean | mm | HE±10 | [0, 42.48] | 0.0% |
| `pr_mean_v3he` | 降水均值 | Precipitation mean | mm | V3→HE | [0.006452, 19.15] | 0.0% |
| `pr_mean_v3pm10` | 降水均值 | Precipitation mean | mm | V3±10 | [0, 23.48] | 0.0% |
| `pr_sd` | 降水标准差 | Precipitation std dev | mm | Full | [0.1972, 48.86] | 0.0% |
| `pr_sd_hema` | 降水标准差 | Precipitation std dev | mm | HE→MA | [0.006964, 57.77] | 0.0% |
| `pr_sd_hepm10` | 降水标准差 | Precipitation std dev | mm | HE±10 | [0, 74.37] | 0.0% |
| `pr_sd_v3he` | 降水标准差 | Precipitation std dev | mm | V3→HE | [0.01305, 45.96] | 0.0% |
| `pr_sd_v3pm10` | 降水标准差 | Precipitation std dev | mm | V3±10 | [0, 42.23] | 0.0% |
| `pr_sum` | 降水累积 | Precipitation sum | mm | Full | [0, 2819] | 0.0% |
| `pr_sum_hema` | 降水累积 | Precipitation sum | mm | HE→MA | [0, 1797] | 0.0% |
| `pr_sum_hepm10` | 降水累积 | Precipitation sum | mm | HE±10 | [0, 892.1] | 0.0% |
| `pr_sum_v3he` | 降水累积 | Precipitation sum | mm | V3→HE | [0, 1283] | 0.0% |
| `pr_sum_v3pm10` | 降水累积 | Precipitation sum | mm | V3±10 | [0, 493] | 0.0% |
| `wetdays_ge10` | 强降水天(>=10mm) | Wet days (precip>=10mm) | days | Full | [0, 89] | 0.0% |
| `wetdays_ge10_hema` | 强降水天(>=10mm) | Wet days (precip>=10mm) | days | HE→MA | [0, 54] | 0.0% |
| `wetdays_ge10_hepm10` | 强降水天(>=10mm) | Wet days (precip>=10mm) | days | HE±10 | [0, 19] | 0.0% |
| `wetdays_ge10_v3he` | 强降水天(>=10mm) | Wet days (precip>=10mm) | days | V3→HE | [0, 46] | 0.0% |
| `wetdays_ge10_v3pm10` | 强降水天(>=10mm) | Wet days (precip>=10mm) | days | V3±10 | [0, 13] | 0.0% |
| `wetdays_ge20` | 强降水天(>=20mm) | Wet days (precip>=20mm) | days | Full | [0, 50] | 0.0% |
| `wetdays_ge20_hema` | 强降水天(>=20mm) | Wet days (precip>=20mm) | days | HE→MA | [0, 36] | 0.0% |
| `wetdays_ge20_hepm10` | 强降水天(>=20mm) | Wet days (precip>=20mm) | days | HE±10 | [0, 15] | 0.0% |
| `wetdays_ge20_v3he` | 强降水天(>=20mm) | Wet days (precip>=20mm) | days | V3→HE | [0, 24] | 0.0% |
| `wetdays_ge20_v3pm10` | 强降水天(>=20mm) | Wet days (precip>=20mm) | days | V3±10 | [0, 9] | 0.0% |

## 6. SM-GLEAM (60 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `drydays_gleam_smrz_le_p10` | GLEAM SMRZ干旱天(<=P10) | GLEAM SMRZ dry days (SM<=P10) | days | Full | [0, 126] | 0.0% |
| `drydays_gleam_smrz_le_p10_hema` | GLEAM SMRZ干旱天(<=P10) | GLEAM SMRZ dry days (SM<=P10) | days | HE→MA | [0, 52] | 0.0% |
| `drydays_gleam_smrz_le_p10_hepm10` | GLEAM SMRZ干旱天(<=P10) | GLEAM SMRZ dry days (SM<=P10) | days | HE±10 | [0, 21] | 0.0% |
| `drydays_gleam_smrz_le_p10_v3he` | GLEAM SMRZ干旱天(<=P10) | GLEAM SMRZ dry days (SM<=P10) | days | V3→HE | [0, 81] | 0.0% |
| `drydays_gleam_smrz_le_p10_v3pm10` | GLEAM SMRZ干旱天(<=P10) | GLEAM SMRZ dry days (SM<=P10) | days | V3±10 | [0, 21] | 0.0% |
| `drydays_gleam_smrz_le_p20` | GLEAM SMRZ干旱天(<=P20) | GLEAM SMRZ dry days (SM<=P20) | days | Full | [0, 175] | 0.0% |
| `drydays_gleam_smrz_le_p20_hema` | GLEAM SMRZ干旱天(<=P20) | GLEAM SMRZ dry days (SM<=P20) | days | HE→MA | [0, 73] | 0.0% |
| `drydays_gleam_smrz_le_p20_hepm10` | GLEAM SMRZ干旱天(<=P20) | GLEAM SMRZ dry days (SM<=P20) | days | HE±10 | [0, 21] | 0.0% |
| `drydays_gleam_smrz_le_p20_v3he` | GLEAM SMRZ干旱天(<=P20) | GLEAM SMRZ dry days (SM<=P20) | days | V3→HE | [0, 93] | 0.0% |
| `drydays_gleam_smrz_le_p20_v3pm10` | GLEAM SMRZ干旱天(<=P20) | GLEAM SMRZ dry days (SM<=P20) | days | V3±10 | [0, 21] | 0.0% |
| `drydays_gleam_sms_le_p10` | GLEAM SMS干旱天(<=P10) | GLEAM SMS dry days (SM<=P10) | days | Full | [0, 89] | 0.0% |
| `drydays_gleam_sms_le_p10_hema` | GLEAM SMS干旱天(<=P10) | GLEAM SMS dry days (SM<=P10) | days | HE→MA | [0, 37] | 0.0% |
| `drydays_gleam_sms_le_p10_hepm10` | GLEAM SMS干旱天(<=P10) | GLEAM SMS dry days (SM<=P10) | days | HE±10 | [0, 21] | 0.0% |
| `drydays_gleam_sms_le_p10_v3he` | GLEAM SMS干旱天(<=P10) | GLEAM SMS dry days (SM<=P10) | days | V3→HE | [0, 54] | 0.0% |
| `drydays_gleam_sms_le_p10_v3pm10` | GLEAM SMS干旱天(<=P10) | GLEAM SMS dry days (SM<=P10) | days | V3±10 | [0, 21] | 0.0% |
| `drydays_gleam_sms_le_p20` | GLEAM SMS干旱天(<=P20) | GLEAM SMS dry days (SM<=P20) | days | Full | [0, 120] | 0.0% |
| `drydays_gleam_sms_le_p20_hema` | GLEAM SMS干旱天(<=P20) | GLEAM SMS dry days (SM<=P20) | days | HE→MA | [0, 43] | 0.0% |
| `drydays_gleam_sms_le_p20_hepm10` | GLEAM SMS干旱天(<=P20) | GLEAM SMS dry days (SM<=P20) | days | HE±10 | [0, 21] | 0.0% |
| `drydays_gleam_sms_le_p20_v3he` | GLEAM SMS干旱天(<=P20) | GLEAM SMS dry days (SM<=P20) | days | V3→HE | [0, 73] | 0.0% |
| `drydays_gleam_sms_le_p20_v3pm10` | GLEAM SMS干旱天(<=P20) | GLEAM SMS dry days (SM<=P20) | days | V3±10 | [0, 21] | 0.0% |
| `gleam_smrz_max` | GLEAM根区SM最大值 | GLEAM root-zone soil moisture max | m³/m³ | Full | [0.06779, 0.4687] | 0.0% |
| `gleam_smrz_max_hema` | GLEAM根区SM最大值 | GLEAM root-zone soil moisture max | m³/m³ | HE→MA | [0.05752, 0.4671] | 0.0% |
| `gleam_smrz_max_hepm10` | GLEAM根区SM最大值 | GLEAM root-zone soil moisture max | m³/m³ | HE±10 | [0.05631, 0.4668] | 0.0% |
| `gleam_smrz_max_v3he` | GLEAM根区SM最大值 | GLEAM root-zone soil moisture max | m³/m³ | V3→HE | [0.05798, 0.4687] | 0.0% |
| `gleam_smrz_max_v3pm10` | GLEAM根区SM最大值 | GLEAM root-zone soil moisture max | m³/m³ | V3±10 | [0.06128, 0.4571] | 0.0% |
| `gleam_smrz_mean` | GLEAM根区SM均值 | GLEAM root-zone soil moisture mean | m³/m³ | Full | [0.05526, 0.4484] | 0.0% |
| `gleam_smrz_mean_hema` | GLEAM根区SM均值 | GLEAM root-zone soil moisture mean | m³/m³ | HE→MA | [0.05626, 0.4528] | 0.0% |
| `gleam_smrz_mean_hepm10` | GLEAM根区SM均值 | GLEAM root-zone soil moisture mean | m³/m³ | HE±10 | [0.05604, 0.458] | 0.0% |
| `gleam_smrz_mean_v3he` | GLEAM根区SM均值 | GLEAM root-zone soil moisture mean | m³/m³ | V3→HE | [0.0554, 0.4548] | 0.0% |
| `gleam_smrz_mean_v3pm10` | GLEAM根区SM均值 | GLEAM root-zone soil moisture mean | m³/m³ | V3±10 | [0.05472, 0.4455] | 0.0% |
| `gleam_smrz_min` | GLEAM根区SM最小值 | GLEAM root-zone soil moisture min | m³/m³ | Full | [0.05169, 0.4289] | 0.0% |
| `gleam_smrz_min_hema` | GLEAM根区SM最小值 | GLEAM root-zone soil moisture min | m³/m³ | HE→MA | [0.05574, 0.4429] | 0.0% |
| `gleam_smrz_min_hepm10` | GLEAM根区SM最小值 | GLEAM root-zone soil moisture min | m³/m³ | HE±10 | [0.05584, 0.4508] | 0.0% |
| `gleam_smrz_min_v3he` | GLEAM根区SM最小值 | GLEAM root-zone soil moisture min | m³/m³ | V3→HE | [0.05307, 0.4433] | 0.0% |
| `gleam_smrz_min_v3pm10` | GLEAM根区SM最小值 | GLEAM root-zone soil moisture min | m³/m³ | V3±10 | [0.05307, 0.4405] | 0.0% |
| `gleam_smrz_sd` | GLEAM根区SM标准差 | GLEAM root-zone soil moisture std dev | m³/m³ | Full | [0.0003467, 0.1065] | 0.0% |
| `gleam_smrz_sd_hema` | GLEAM根区SM标准差 | GLEAM root-zone soil moisture std dev | m³/m³ | HE→MA | [6.143e-05, 0.07996] | 0.0% |
| `gleam_smrz_sd_hepm10` | GLEAM根区SM标准差 | GLEAM root-zone soil moisture std dev | m³/m³ | HE±10 | [4.376e-05, 0.07857] | 0.0% |
| `gleam_smrz_sd_v3he` | GLEAM根区SM标准差 | GLEAM root-zone soil moisture std dev | m³/m³ | V3→HE | [0.0001631, 0.09669] | 0.0% |
| `gleam_smrz_sd_v3pm10` | GLEAM根区SM标准差 | GLEAM root-zone soil moisture std dev | m³/m³ | V3±10 | [0.0001013, 0.04468] | 0.0% |
| `gleam_sms_max` | GLEAM表层SM最大值 | GLEAM surface soil moisture max | m³/m³ | Full | [0.06167, 0.5239] | 0.0% |
| `gleam_sms_max_hema` | GLEAM表层SM最大值 | GLEAM surface soil moisture max | m³/m³ | HE→MA | [0.05543, 0.5239] | 0.0% |
| `gleam_sms_max_hepm10` | GLEAM表层SM最大值 | GLEAM surface soil moisture max | m³/m³ | HE±10 | [0.05258, 0.5239] | 0.0% |
| `gleam_sms_max_v3he` | GLEAM表层SM最大值 | GLEAM surface soil moisture max | m³/m³ | V3→HE | [0.05444, 0.523] | 0.0% |
| `gleam_sms_max_v3pm10` | GLEAM表层SM最大值 | GLEAM surface soil moisture max | m³/m³ | V3±10 | [0.04997, 0.4932] | 0.0% |
| `gleam_sms_mean` | GLEAM表层SM均值 | GLEAM surface soil moisture mean | m³/m³ | Full | [0.04949, 0.4622] | 0.0% |
| `gleam_sms_mean_hema` | GLEAM表层SM均值 | GLEAM surface soil moisture mean | m³/m³ | HE→MA | [0.05211, 0.4817] | 0.0% |
| `gleam_sms_mean_hepm10` | GLEAM表层SM均值 | GLEAM surface soil moisture mean | m³/m³ | HE±10 | [0.05074, 0.4873] | 0.0% |
| `gleam_sms_mean_v3he` | GLEAM表层SM均值 | GLEAM surface soil moisture mean | m³/m³ | V3→HE | [0.04953, 0.4667] | 0.0% |
| `gleam_sms_mean_v3pm10` | GLEAM表层SM均值 | GLEAM surface soil moisture mean | m³/m³ | V3±10 | [0.04582, 0.4553] | 0.0% |
| `gleam_sms_min` | GLEAM表层SM最小值 | GLEAM surface soil moisture min | m³/m³ | Full | [0.04363, 0.4042] | 0.0% |
| `gleam_sms_min_hema` | GLEAM表层SM最小值 | GLEAM surface soil moisture min | m³/m³ | HE→MA | [0.04904, 0.4632] | 0.0% |
| `gleam_sms_min_hepm10` | GLEAM表层SM最小值 | GLEAM surface soil moisture min | m³/m³ | HE±10 | [0.04904, 0.4681] | 0.0% |
| `gleam_sms_min_v3he` | GLEAM表层SM最小值 | GLEAM surface soil moisture min | m³/m³ | V3→HE | [0.04472, 0.4293] | 0.0% |
| `gleam_sms_min_v3pm10` | GLEAM表层SM最小值 | GLEAM surface soil moisture min | m³/m³ | V3±10 | [0.04412, 0.4231] | 0.0% |
| `gleam_sms_sd` | GLEAM表层SM标准差 | GLEAM surface soil moisture std dev | m³/m³ | Full | [0.001928, 0.1264] | 0.0% |
| `gleam_sms_sd_hema` | GLEAM表层SM标准差 | GLEAM surface soil moisture std dev | m³/m³ | HE→MA | [0.0005494, 0.0733] | 0.0% |
| `gleam_sms_sd_hepm10` | GLEAM表层SM标准差 | GLEAM surface soil moisture std dev | m³/m³ | HE±10 | [0.000415, 0.1034] | 0.0% |
| `gleam_sms_sd_v3he` | GLEAM表层SM标准差 | GLEAM surface soil moisture std dev | m³/m³ | V3→HE | [0.00129, 0.1138] | 0.0% |
| `gleam_sms_sd_v3pm10` | GLEAM表层SM标准差 | GLEAM surface soil moisture std dev | m³/m³ | V3±10 | [0.0008525, 0.07953] | 0.0% |

## 7. SM-SWSM (60 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `drydays_swsm_l1_le_p10` | SWSM L1干旱天(<=P10) | SWSM L1 dry days (SM<=P10) | days | Full | [0, 101] | 0.0% |
| `drydays_swsm_l1_le_p10_hema` | SWSM L1干旱天(<=P10) | SWSM L1 dry days (SM<=P10) | days | HE→MA | [0, 51] | 0.0% |
| `drydays_swsm_l1_le_p10_hepm10` | SWSM L1干旱天(<=P10) | SWSM L1 dry days (SM<=P10) | days | HE±10 | [0, 21] | 0.0% |
| `drydays_swsm_l1_le_p10_v3he` | SWSM L1干旱天(<=P10) | SWSM L1 dry days (SM<=P10) | days | V3→HE | [0, 66] | 0.0% |
| `drydays_swsm_l1_le_p10_v3pm10` | SWSM L1干旱天(<=P10) | SWSM L1 dry days (SM<=P10) | days | V3±10 | [0, 21] | 0.0% |
| `drydays_swsm_l1_le_p20` | SWSM L1干旱天(<=P20) | SWSM L1 dry days (SM<=P20) | days | Full | [0, 145] | 0.0% |
| `drydays_swsm_l1_le_p20_hema` | SWSM L1干旱天(<=P20) | SWSM L1 dry days (SM<=P20) | days | HE→MA | [0, 83] | 0.0% |
| `drydays_swsm_l1_le_p20_hepm10` | SWSM L1干旱天(<=P20) | SWSM L1 dry days (SM<=P20) | days | HE±10 | [0, 21] | 0.0% |
| `drydays_swsm_l1_le_p20_v3he` | SWSM L1干旱天(<=P20) | SWSM L1 dry days (SM<=P20) | days | V3→HE | [0, 73] | 0.0% |
| `drydays_swsm_l1_le_p20_v3pm10` | SWSM L1干旱天(<=P20) | SWSM L1 dry days (SM<=P20) | days | V3±10 | [0, 21] | 0.0% |
| `drydays_swsm_l3_le_p10` | SWSM L3干旱天(<=P10) | SWSM L3 dry days (SM<=P10) | days | Full | [0, 146] | 0.0% |
| `drydays_swsm_l3_le_p10_hema` | SWSM L3干旱天(<=P10) | SWSM L3 dry days (SM<=P10) | days | HE→MA | [0, 84] | 0.0% |
| `drydays_swsm_l3_le_p10_hepm10` | SWSM L3干旱天(<=P10) | SWSM L3 dry days (SM<=P10) | days | HE±10 | [0, 21] | 0.0% |
| `drydays_swsm_l3_le_p10_v3he` | SWSM L3干旱天(<=P10) | SWSM L3 dry days (SM<=P10) | days | V3→HE | [0, 93] | 0.0% |
| `drydays_swsm_l3_le_p10_v3pm10` | SWSM L3干旱天(<=P10) | SWSM L3 dry days (SM<=P10) | days | V3±10 | [0, 21] | 0.0% |
| `drydays_swsm_l3_le_p20` | SWSM L3干旱天(<=P20) | SWSM L3 dry days (SM<=P20) | days | Full | [0, 195] | 0.0% |
| `drydays_swsm_l3_le_p20_hema` | SWSM L3干旱天(<=P20) | SWSM L3 dry days (SM<=P20) | days | HE→MA | [0, 104] | 0.0% |
| `drydays_swsm_l3_le_p20_hepm10` | SWSM L3干旱天(<=P20) | SWSM L3 dry days (SM<=P20) | days | HE±10 | [0, 21] | 0.0% |
| `drydays_swsm_l3_le_p20_v3he` | SWSM L3干旱天(<=P20) | SWSM L3 dry days (SM<=P20) | days | V3→HE | [0, 93] | 0.0% |
| `drydays_swsm_l3_le_p20_v3pm10` | SWSM L3干旱天(<=P20) | SWSM L3 dry days (SM<=P20) | days | V3±10 | [0, 21] | 0.0% |
| `swsm_l1_max` | SWSM表层SM最大值 | SWSM L1 surface soil moisture max | m³/m³ | Full | [0.07, 0.57] | 6.3% |
| `swsm_l1_max_hema` | SWSM表层SM最大值 | SWSM L1 surface soil moisture max | m³/m³ | HE→MA | [0.01, 0.57] | 6.3% |
| `swsm_l1_max_hepm10` | SWSM表层SM最大值 | SWSM L1 surface soil moisture max | m³/m³ | HE±10 | [0.04, 0.56] | 6.3% |
| `swsm_l1_max_v3he` | SWSM表层SM最大值 | SWSM L1 surface soil moisture max | m³/m³ | V3→HE | [0.04, 0.57] | 6.3% |
| `swsm_l1_max_v3pm10` | SWSM表层SM最大值 | SWSM L1 surface soil moisture max | m³/m³ | V3±10 | [0.03, 0.56] | 6.3% |
| `swsm_l1_mean` | SWSM表层SM均值 | SWSM L1 surface soil moisture mean | m³/m³ | Full | [0.03403, 0.489] | 6.3% |
| `swsm_l1_mean_hema` | SWSM表层SM均值 | SWSM L1 surface soil moisture mean | m³/m³ | HE→MA | [0.01, 0.508] | 6.3% |
| `swsm_l1_mean_hepm10` | SWSM表层SM均值 | SWSM L1 surface soil moisture mean | m³/m³ | HE±10 | [0.02357, 0.5119] | 6.3% |
| `swsm_l1_mean_v3he` | SWSM表层SM均值 | SWSM L1 surface soil moisture mean | m³/m³ | V3→HE | [0.03205, 0.5069] | 6.3% |
| `swsm_l1_mean_v3pm10` | SWSM表层SM均值 | SWSM L1 surface soil moisture mean | m³/m³ | V3±10 | [0.0175, 0.5148] | 6.3% |
| `swsm_l1_min` | SWSM表层SM最小值 | SWSM L1 surface soil moisture min | m³/m³ | Full | [0.01, 0.4] | 6.3% |
| `swsm_l1_min_hema` | SWSM表层SM最小值 | SWSM L1 surface soil moisture min | m³/m³ | HE→MA | [0.01, 0.46] | 6.3% |
| `swsm_l1_min_hepm10` | SWSM表层SM最小值 | SWSM L1 surface soil moisture min | m³/m³ | HE±10 | [0.01, 0.48] | 6.3% |
| `swsm_l1_min_v3he` | SWSM表层SM最小值 | SWSM L1 surface soil moisture min | m³/m³ | V3→HE | [0.01, 0.44] | 6.3% |
| `swsm_l1_min_v3pm10` | SWSM表层SM最小值 | SWSM L1 surface soil moisture min | m³/m³ | V3±10 | [0.01, 0.48] | 6.3% |
| `swsm_l1_sd` | SWSM表层SM标准差 | SWSM L1 surface soil moisture std dev | m³/m³ | Full | [0.005561, 0.1397] | 6.3% |
| `swsm_l1_sd_hema` | SWSM表层SM标准差 | SWSM L1 surface soil moisture std dev | m³/m³ | HE→MA | [0.003873, 0.1329] | 6.3% |
| `swsm_l1_sd_hepm10` | SWSM表层SM标准差 | SWSM L1 surface soil moisture std dev | m³/m³ | HE±10 | [0.002182, 0.1206] | 6.3% |
| `swsm_l1_sd_v3he` | SWSM表层SM标准差 | SWSM L1 surface soil moisture std dev | m³/m³ | V3→HE | [0.004743, 0.1431] | 6.3% |
| `swsm_l1_sd_v3pm10` | SWSM表层SM标准差 | SWSM L1 surface soil moisture std dev | m³/m³ | V3±10 | [0.004024, 0.1262] | 6.3% |
| `swsm_l3_max` | SWSM深层SM最大值 | SWSM L3 deep soil moisture max | m³/m³ | Full | [0.02, 0.62] | 6.3% |
| `swsm_l3_max_hema` | SWSM深层SM最大值 | SWSM L3 deep soil moisture max | m³/m³ | HE→MA | [0.02, 0.61] | 6.3% |
| `swsm_l3_max_hepm10` | SWSM深层SM最大值 | SWSM L3 deep soil moisture max | m³/m³ | HE±10 | [0.02, 0.61] | 6.3% |
| `swsm_l3_max_v3he` | SWSM深层SM最大值 | SWSM L3 deep soil moisture max | m³/m³ | V3→HE | [0.02, 0.62] | 6.3% |
| `swsm_l3_max_v3pm10` | SWSM深层SM最大值 | SWSM L3 deep soil moisture max | m³/m³ | V3±10 | [0.02, 0.61] | 6.3% |
| `swsm_l3_mean` | SWSM深层SM均值 | SWSM L3 deep soil moisture mean | m³/m³ | Full | [0.01325, 0.5303] | 6.3% |
| `swsm_l3_mean_hema` | SWSM深层SM均值 | SWSM L3 deep soil moisture mean | m³/m³ | HE→MA | [0.01296, 0.5837] | 6.3% |
| `swsm_l3_mean_hepm10` | SWSM深层SM均值 | SWSM L3 deep soil moisture mean | m³/m³ | HE±10 | [0.011, 0.5729] | 6.3% |
| `swsm_l3_mean_v3he` | SWSM深层SM均值 | SWSM L3 deep soil moisture mean | m³/m³ | V3→HE | [0.01341, 0.5568] | 6.3% |
| `swsm_l3_mean_v3pm10` | SWSM深层SM均值 | SWSM L3 deep soil moisture mean | m³/m³ | V3±10 | [0.011, 0.5133] | 6.3% |
| `swsm_l3_min` | SWSM深层SM最小值 | SWSM L3 deep soil moisture min | m³/m³ | Full | [0.01, 0.49] | 6.3% |
| `swsm_l3_min_hema` | SWSM深层SM最小值 | SWSM L3 deep soil moisture min | m³/m³ | HE→MA | [0.01, 0.55] | 6.3% |
| `swsm_l3_min_hepm10` | SWSM深层SM最小值 | SWSM L3 deep soil moisture min | m³/m³ | HE±10 | [0.01, 0.52] | 6.3% |
| `swsm_l3_min_v3he` | SWSM深层SM最小值 | SWSM L3 deep soil moisture min | m³/m³ | V3→HE | [0.01, 0.51] | 6.3% |
| `swsm_l3_min_v3pm10` | SWSM深层SM最小值 | SWSM L3 deep soil moisture min | m³/m³ | V3±10 | [0.01, 0.49] | 6.3% |
| `swsm_l3_sd` | SWSM深层SM标准差 | SWSM L3 deep soil moisture std dev | m³/m³ | Full | [0.002599, 0.1277] | 6.3% |
| `swsm_l3_sd_hema` | SWSM深层SM标准差 | SWSM L3 deep soil moisture std dev | m³/m³ | HE→MA | [0.001443, 0.08489] | 6.3% |
| `swsm_l3_sd_hepm10` | SWSM深层SM标准差 | SWSM L3 deep soil moisture std dev | m³/m³ | HE±10 | [0, 0.1053] | 6.3% |
| `swsm_l3_sd_v3he` | SWSM深层SM标准差 | SWSM L3 deep soil moisture std dev | m³/m³ | V3→HE | [0.001179, 0.1156] | 6.3% |
| `swsm_l3_sd_v3pm10` | SWSM深层SM标准差 | SWSM L3 deep soil moisture std dev | m³/m³ | V3±10 | [0, 0.07497] | 6.3% |

## 8. SM-ERA5Land (70 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `drydays_era5l_swvl1_le_p10` | ERA5L SWVL1干旱天(<=P10) | ERA5L SWVL1 dry days (SM<=P10) | days | Full | [0, 156] | 0.0% |
| `drydays_era5l_swvl1_le_p10_hema` | ERA5L SWVL1干旱天(<=P10) | ERA5L SWVL1 dry days (SM<=P10) | days | HE→MA | [0, 48] | 0.0% |
| `drydays_era5l_swvl1_le_p10_hepm10` | ERA5L SWVL1干旱天(<=P10) | ERA5L SWVL1 dry days (SM<=P10) | days | HE±10 | [0, 21] | 0.0% |
| `drydays_era5l_swvl1_le_p10_v3he` | ERA5L SWVL1干旱天(<=P10) | ERA5L SWVL1 dry days (SM<=P10) | days | V3→HE | [0, 86] | 0.0% |
| `drydays_era5l_swvl1_le_p10_v3pm10` | ERA5L SWVL1干旱天(<=P10) | ERA5L SWVL1 dry days (SM<=P10) | days | V3±10 | [0, 21] | 0.0% |
| `drydays_era5l_swvl1_le_p20` | ERA5L SWVL1干旱天(<=P20) | ERA5L SWVL1 dry days (SM<=P20) | days | Full | [0, 156] | 0.0% |
| `drydays_era5l_swvl1_le_p20_hema` | ERA5L SWVL1干旱天(<=P20) | ERA5L SWVL1 dry days (SM<=P20) | days | HE→MA | [0, 55] | 0.0% |
| `drydays_era5l_swvl1_le_p20_hepm10` | ERA5L SWVL1干旱天(<=P20) | ERA5L SWVL1 dry days (SM<=P20) | days | HE±10 | [0, 21] | 0.0% |
| `drydays_era5l_swvl1_le_p20_v3he` | ERA5L SWVL1干旱天(<=P20) | ERA5L SWVL1 dry days (SM<=P20) | days | V3→HE | [0, 86] | 0.0% |
| `drydays_era5l_swvl1_le_p20_v3pm10` | ERA5L SWVL1干旱天(<=P20) | ERA5L SWVL1 dry days (SM<=P20) | days | V3±10 | [0, 21] | 0.0% |
| `drydays_era5l_swvl3_le_p10` | ERA5L SWVL3干旱天(<=P10) | ERA5L SWVL3 dry days (SM<=P10) | days | Full | [0, 160] | 0.0% |
| `drydays_era5l_swvl3_le_p10_hema` | ERA5L SWVL3干旱天(<=P10) | ERA5L SWVL3 dry days (SM<=P10) | days | HE→MA | [0, 66] | 0.0% |
| `drydays_era5l_swvl3_le_p10_hepm10` | ERA5L SWVL3干旱天(<=P10) | ERA5L SWVL3 dry days (SM<=P10) | days | HE±10 | [0, 21] | 0.0% |
| `drydays_era5l_swvl3_le_p10_v3he` | ERA5L SWVL3干旱天(<=P10) | ERA5L SWVL3 dry days (SM<=P10) | days | V3→HE | [0, 94] | 0.0% |
| `drydays_era5l_swvl3_le_p10_v3pm10` | ERA5L SWVL3干旱天(<=P10) | ERA5L SWVL3 dry days (SM<=P10) | days | V3±10 | [0, 21] | 0.0% |
| `drydays_era5l_swvl3_le_p20` | ERA5L SWVL3干旱天(<=P20) | ERA5L SWVL3 dry days (SM<=P20) | days | Full | [0, 165] | 0.0% |
| `drydays_era5l_swvl3_le_p20_hema` | ERA5L SWVL3干旱天(<=P20) | ERA5L SWVL3 dry days (SM<=P20) | days | HE→MA | [0, 91] | 0.0% |
| `drydays_era5l_swvl3_le_p20_hepm10` | ERA5L SWVL3干旱天(<=P20) | ERA5L SWVL3 dry days (SM<=P20) | days | HE±10 | [0, 21] | 0.0% |
| `drydays_era5l_swvl3_le_p20_v3he` | ERA5L SWVL3干旱天(<=P20) | ERA5L SWVL3 dry days (SM<=P20) | days | V3→HE | [0, 98] | 0.0% |
| `drydays_era5l_swvl3_le_p20_v3pm10` | ERA5L SWVL3干旱天(<=P20) | ERA5L SWVL3 dry days (SM<=P20) | days | V3±10 | [0, 21] | 0.0% |
| `era5l_swvl1_coverage` | ERA5L表层SM覆盖率 | ERA5-Land swvl1 (0-7cm) soil moisture temporal coverage fraction | m³/m³ | Full | [0.7943, 1] | 0.0% |
| `era5l_swvl1_coverage_hema` | ERA5L表层SM覆盖率 | ERA5-Land swvl1 (0-7cm) soil moisture temporal coverage fraction | m³/m³ | HE→MA | [0.989, 1] | 0.0% |
| `era5l_swvl1_coverage_hepm10` | ERA5L表层SM覆盖率 | ERA5-Land swvl1 (0-7cm) soil moisture temporal coverage fraction | m³/m³ | HE±10 | [1, 1] | 0.0% |
| `era5l_swvl1_coverage_v3he` | ERA5L表层SM覆盖率 | ERA5-Land swvl1 (0-7cm) soil moisture temporal coverage fraction | m³/m³ | V3→HE | [0.9828, 1] | 0.0% |
| `era5l_swvl1_coverage_v3pm10` | ERA5L表层SM覆盖率 | ERA5-Land swvl1 (0-7cm) soil moisture temporal coverage fraction | m³/m³ | V3±10 | [0.4762, 1] | 0.0% |
| `era5l_swvl1_max` | ERA5L表层SM最大值 | ERA5-Land swvl1 (0-7cm) soil moisture max | m³/m³ | Full | [0, 0.7469] | 0.0% |
| `era5l_swvl1_max_hema` | ERA5L表层SM最大值 | ERA5-Land swvl1 (0-7cm) soil moisture max | m³/m³ | HE→MA | [0, 0.7469] | 0.0% |
| `era5l_swvl1_max_hepm10` | ERA5L表层SM最大值 | ERA5-Land swvl1 (0-7cm) soil moisture max | m³/m³ | HE±10 | [0, 0.7469] | 0.0% |
| `era5l_swvl1_max_v3he` | ERA5L表层SM最大值 | ERA5-Land swvl1 (0-7cm) soil moisture max | m³/m³ | V3→HE | [0, 0.7451] | 0.0% |
| `era5l_swvl1_max_v3pm10` | ERA5L表层SM最大值 | ERA5-Land swvl1 (0-7cm) soil moisture max | m³/m³ | V3±10 | [0, 0.6686] | 0.0% |
| `era5l_swvl1_mean` | ERA5L表层SM均值 | ERA5-Land swvl1 (0-7cm) soil moisture mean | m³/m³ | Full | [0, 0.5136] | 0.0% |
| `era5l_swvl1_mean_hema` | ERA5L表层SM均值 | ERA5-Land swvl1 (0-7cm) soil moisture mean | m³/m³ | HE→MA | [0, 0.6231] | 0.0% |
| `era5l_swvl1_mean_hepm10` | ERA5L表层SM均值 | ERA5-Land swvl1 (0-7cm) soil moisture mean | m³/m³ | HE±10 | [0, 0.6167] | 0.0% |
| `era5l_swvl1_mean_v3he` | ERA5L表层SM均值 | ERA5-Land swvl1 (0-7cm) soil moisture mean | m³/m³ | V3→HE | [0, 0.5251] | 0.0% |
| `era5l_swvl1_mean_v3pm10` | ERA5L表层SM均值 | ERA5-Land swvl1 (0-7cm) soil moisture mean | m³/m³ | V3±10 | [0, 0.5652] | 0.0% |
| `era5l_swvl1_min` | ERA5L表层SM最小值 | ERA5-Land swvl1 (0-7cm) soil moisture min | m³/m³ | Full | [-1.466e-20, 0.4538] | 0.0% |
| `era5l_swvl1_min_hema` | ERA5L表层SM最小值 | ERA5-Land swvl1 (0-7cm) soil moisture min | m³/m³ | HE→MA | [-1.466e-20, 0.4967] | 0.0% |
| `era5l_swvl1_min_hepm10` | ERA5L表层SM最小值 | ERA5-Land swvl1 (0-7cm) soil moisture min | m³/m³ | HE±10 | [-1.2e-20, 0.5022] | 0.0% |
| `era5l_swvl1_min_v3he` | ERA5L表层SM最小值 | ERA5-Land swvl1 (0-7cm) soil moisture min | m³/m³ | V3→HE | [-1.448e-20, 0.4649] | 0.0% |
| `era5l_swvl1_min_v3pm10` | ERA5L表层SM最小值 | ERA5-Land swvl1 (0-7cm) soil moisture min | m³/m³ | V3±10 | [-1.455e-20, 0.5003] | 0.0% |
| `era5l_swvl1_sd` | ERA5L表层SM标准差 | ERA5-Land swvl1 (0-7cm) soil moisture std dev | m³/m³ | Full | [0, 0.2412] | 0.0% |
| `era5l_swvl1_sd_hema` | ERA5L表层SM标准差 | ERA5-Land swvl1 (0-7cm) soil moisture std dev | m³/m³ | HE→MA | [0, 0.2381] | 0.0% |
| `era5l_swvl1_sd_hepm10` | ERA5L表层SM标准差 | ERA5-Land swvl1 (0-7cm) soil moisture std dev | m³/m³ | HE±10 | [0, 0.1985] | 0.0% |
| `era5l_swvl1_sd_v3he` | ERA5L表层SM标准差 | ERA5-Land swvl1 (0-7cm) soil moisture std dev | m³/m³ | V3→HE | [0, 0.2338] | 0.0% |
| `era5l_swvl1_sd_v3pm10` | ERA5L表层SM标准差 | ERA5-Land swvl1 (0-7cm) soil moisture std dev | m³/m³ | V3±10 | [0, 0.1674] | 0.0% |
| `era5l_swvl3_coverage` | ERA5L根区SM覆盖率 | ERA5-Land swvl3 (28-100cm) soil moisture temporal coverage fraction | m³/m³ | Full | [0.7943, 1] | 0.0% |
| `era5l_swvl3_coverage_hema` | ERA5L根区SM覆盖率 | ERA5-Land swvl3 (28-100cm) soil moisture temporal coverage fraction | m³/m³ | HE→MA | [0.989, 1] | 0.0% |
| `era5l_swvl3_coverage_hepm10` | ERA5L根区SM覆盖率 | ERA5-Land swvl3 (28-100cm) soil moisture temporal coverage fraction | m³/m³ | HE±10 | [1, 1] | 0.0% |
| `era5l_swvl3_coverage_v3he` | ERA5L根区SM覆盖率 | ERA5-Land swvl3 (28-100cm) soil moisture temporal coverage fraction | m³/m³ | V3→HE | [0.9828, 1] | 0.0% |
| `era5l_swvl3_coverage_v3pm10` | ERA5L根区SM覆盖率 | ERA5-Land swvl3 (28-100cm) soil moisture temporal coverage fraction | m³/m³ | V3±10 | [0.4762, 1] | 0.0% |
| `era5l_swvl3_max` | ERA5L根区SM最大值 | ERA5-Land swvl3 (28-100cm) soil moisture max | m³/m³ | Full | [-6.647e-23, 0.6484] | 0.0% |
| `era5l_swvl3_max_hema` | ERA5L根区SM最大值 | ERA5-Land swvl3 (28-100cm) soil moisture max | m³/m³ | HE→MA | [-1.446e-22, 0.6484] | 0.0% |
| `era5l_swvl3_max_hepm10` | ERA5L根区SM最大值 | ERA5-Land swvl3 (28-100cm) soil moisture max | m³/m³ | HE±10 | [-1.106e-21, 0.6108] | 0.0% |
| `era5l_swvl3_max_v3he` | ERA5L根区SM最大值 | ERA5-Land swvl3 (28-100cm) soil moisture max | m³/m³ | V3→HE | [-9.347e-23, 0.5882] | 0.0% |
| `era5l_swvl3_max_v3pm10` | ERA5L根区SM最大值 | ERA5-Land swvl3 (28-100cm) soil moisture max | m³/m³ | V3±10 | [-9.347e-23, 0.5569] | 0.0% |
| `era5l_swvl3_mean` | ERA5L根区SM均值 | ERA5-Land swvl3 (28-100cm) soil moisture mean | m³/m³ | Full | [-7.61e-21, 0.5671] | 0.0% |
| `era5l_swvl3_mean_hema` | ERA5L根区SM均值 | ERA5-Land swvl3 (28-100cm) soil moisture mean | m³/m³ | HE→MA | [-7.212e-21, 0.6244] | 0.0% |
| `era5l_swvl3_mean_hepm10` | ERA5L根区SM均值 | ERA5-Land swvl3 (28-100cm) soil moisture mean | m³/m³ | HE±10 | [-1.955e-20, 0.5857] | 0.0% |
| `era5l_swvl3_mean_v3he` | ERA5L根区SM均值 | ERA5-Land swvl3 (28-100cm) soil moisture mean | m³/m³ | V3→HE | [-1.351e-20, 0.5413] | 0.0% |
| `era5l_swvl3_mean_v3pm10` | ERA5L根区SM均值 | ERA5-Land swvl3 (28-100cm) soil moisture mean | m³/m³ | V3±10 | [-1.163e-21, 0.5505] | 0.0% |
| `era5l_swvl3_min` | ERA5L根区SM最小值 | ERA5-Land swvl3 (28-100cm) soil moisture min | m³/m³ | Full | [-7.633e-20, 0.5204] | 0.0% |
| `era5l_swvl3_min_hema` | ERA5L根区SM最小值 | ERA5-Land swvl3 (28-100cm) soil moisture min | m³/m³ | HE→MA | [-2.789e-20, 0.5839] | 0.0% |
| `era5l_swvl3_min_hepm10` | ERA5L根区SM最小值 | ERA5-Land swvl3 (28-100cm) soil moisture min | m³/m³ | HE±10 | [-7.633e-20, 0.567] | 0.0% |
| `era5l_swvl3_min_v3he` | ERA5L根区SM最小值 | ERA5-Land swvl3 (28-100cm) soil moisture min | m³/m³ | V3→HE | [-7.633e-20, 0.5204] | 0.0% |
| `era5l_swvl3_min_v3pm10` | ERA5L根区SM最小值 | ERA5-Land swvl3 (28-100cm) soil moisture min | m³/m³ | V3±10 | [-4.531e-21, 0.5463] | 0.0% |
| `era5l_swvl3_sd` | ERA5L根区SM标准差 | ERA5-Land swvl3 (28-100cm) soil moisture std dev | m³/m³ | Full | [0, 0.1119] | 0.0% |
| `era5l_swvl3_sd_hema` | ERA5L根区SM标准差 | ERA5-Land swvl3 (28-100cm) soil moisture std dev | m³/m³ | HE→MA | [0, 0.08486] | 0.0% |
| `era5l_swvl3_sd_hepm10` | ERA5L根区SM标准差 | ERA5-Land swvl3 (28-100cm) soil moisture std dev | m³/m³ | HE±10 | [0, 0.1176] | 0.0% |
| `era5l_swvl3_sd_v3he` | ERA5L根区SM标准差 | ERA5-Land swvl3 (28-100cm) soil moisture std dev | m³/m³ | V3→HE | [0, 0.1109] | 0.0% |
| `era5l_swvl3_sd_v3pm10` | ERA5L根区SM标准差 | ERA5-Land swvl3 (28-100cm) soil moisture std dev | m³/m³ | V3±10 | [0, 0.06295] | 0.0% |

## 9. ET0/Water Balance (15 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `et0_mean` | 参考蒸散均值 | Reference evapotranspiration mean | mm | Full | [2.203, 8.531] | 6.1% |
| `et0_mean_hema` | 参考蒸散均值 | Reference evapotranspiration mean | mm | HE→MA | [2.15, 8.698] | 6.1% |
| `et0_mean_hepm10` | 参考蒸散均值 | Reference evapotranspiration mean | mm | HE±10 | [1.966, 9.813] | 6.1% |
| `et0_mean_v3he` | 参考蒸散均值 | Reference evapotranspiration mean | mm | V3→HE | [2.059, 9.545] | 6.1% |
| `et0_mean_v3pm10` | 参考蒸散均值 | Reference evapotranspiration mean | mm | V3±10 | [1.213, 10.62] | 6.1% |
| `et0_sum` | 参考蒸散累积 | Reference evapotranspiration sum | mm | Full | [0, 1374] | 0.0% |
| `et0_sum_hema` | 参考蒸散累积 | Reference evapotranspiration sum | mm | HE→MA | [0, 454.1] | 0.0% |
| `et0_sum_hepm10` | 参考蒸散累积 | Reference evapotranspiration sum | mm | HE±10 | [0, 206.1] | 0.0% |
| `et0_sum_v3he` | 参考蒸散累积 | Reference evapotranspiration sum | mm | V3→HE | [0, 809.9] | 0.0% |
| `et0_sum_v3pm10` | 参考蒸散累积 | Reference evapotranspiration sum | mm | V3±10 | [0, 223.1] | 0.0% |
| `wd_deficit` | 水分亏缺 | Water deficit (ET0-P) | mm | Full | [-2186, 1327] | 0.0% |
| `wd_deficit_hema` | 水分亏缺 | Water deficit (ET0-P) | mm | HE→MA | [-1531, 367.5] | 0.0% |
| `wd_deficit_hepm10` | 水分亏缺 | Water deficit (ET0-P) | mm | HE±10 | [-836, 205.9] | 0.0% |
| `wd_deficit_v3he` | 水分亏缺 | Water deficit (ET0-P) | mm | V3→HE | [-1075, 791] | 0.0% |
| `wd_deficit_v3pm10` | 水分亏缺 | Water deficit (ET0-P) | mm | V3±10 | [-428, 220.8] | 0.0% |

## 10. VPD/SPEI (20 vars)

> **SPEI 计算方法 (2026-04-04更新):** 采用 v1 终止月单点提取法。对每个格点-年份-窗口，计算
> `scale = end_month - start_month + 1`，然后取 `CHM_SPEI-{scale}.nc` 在 `end_month` 的值。
> 此方法正确利用了 SPEI 的内置时间累积语义（SPEI-N 在 M 月 = M-N+1 到 M 月的累积水分亏缺）。
> `_max = _mean`（单点提取，无分布最大值概念；保留 _max 列名以兼容下游脚本）。
> VPD 仍采用月度加权平均。

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `spei1_max_hepm10` | SPEI-1 终止月值 | SPEI-1 end-month value | -- | HE±10 | [-3.288, 2.904] | 0.0% |
| `spei1_max_v3pm10` | SPEI-1 终止月值 | SPEI-1 end-month value | -- | V3±10 | [-2.728, 2.918] | 0.0% |
| `spei1_mean_hepm10` | SPEI-1 终止月值 | SPEI-1 end-month value | -- | HE±10 | [-3.288, 2.904] | 0.0% |
| `spei1_mean_v3pm10` | SPEI-1 终止月值 | SPEI-1 end-month value | -- | V3±10 | [-2.728, 2.918] | 0.0% |
| `spei2_max_hema` | SPEI-2 终止月值 | SPEI-2 end-month value | -- | HE→MA | [-2.240, 2.814] | 0.0% |
| `spei2_max_v3he` | SPEI-2 终止月值 | SPEI-2 end-month value | -- | V3→HE | [-2.767, 2.950] | 0.0% |
| `spei2_mean_hema` | SPEI-2 终止月值 | SPEI-2 end-month value | -- | HE→MA | [-2.240, 2.814] | 0.0% |
| `spei2_mean_v3he` | SPEI-2 终止月值 | SPEI-2 end-month value | -- | V3→HE | [-2.767, 2.950] | 0.0% |
| `spei6_max` | SPEI-6 终止月值 | SPEI-6 end-month value | -- | Full | [-2.912, 2.851] | 0.0% |
| `spei6_mean` | SPEI-6 终止月值 | SPEI-6 end-month value | -- | Full | [-2.912, 2.851] | 0.0% |
| `vpd_max` | 饱和水汽压差最大值 | Vapor pressure deficit max | hPa | Full | [3.135, 59.14] | 0.0% |
| `vpd_max_hema` | 饱和水汽压差最大值 | Vapor pressure deficit max | hPa | HE→MA | [3.044, 59.14] | 0.0% |
| `vpd_max_hepm10` | 饱和水汽压差最大值 | Vapor pressure deficit max | hPa | HE±10 | [2.497, 59.14] | 0.0% |
| `vpd_max_v3he` | 饱和水汽压差最大值 | Vapor pressure deficit max | hPa | V3→HE | [3.119, 59.14] | 0.0% |
| `vpd_max_v3pm10` | 饱和水汽压差最大值 | Vapor pressure deficit max | hPa | V3±10 | [1.931, 55.89] | 0.0% |
| `vpd_mean` | 饱和水汽压差均值 | Vapor pressure deficit mean | hPa | Full | [2.495, 44.67] | 0.0% |
| `vpd_mean_hema` | 饱和水汽压差均值 | Vapor pressure deficit mean | hPa | HE→MA | [2.39, 41.74] | 0.0% |
| `vpd_mean_hepm10` | 饱和水汽压差均值 | Vapor pressure deficit mean | hPa | HE±10 | [2.497, 52.6] | 0.0% |
| `vpd_mean_v3he` | 饱和水汽压差均值 | Vapor pressure deficit mean | hPa | V3→HE | [2.743, 52.64] | 0.0% |
| `vpd_mean_v3pm10` | 饱和水汽压差均值 | Vapor pressure deficit mean | hPa | V3±10 | [1.815, 53.31] | 0.0% |

## 11. Compound Stress (20 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `hotdrydays_ge32_smrz_p10` | 热干复合天(>=32°C, SM<=P10) | Hot-dry days (Tmax>=32°C & SMrz<=P10) | days | Full | [0, 57] | 0.0% |
| `hotdrydays_ge32_smrz_p10_hema` | 热干复合天(>=32°C, SM<=P10) | Hot-dry days (Tmax>=32°C & SMrz<=P10) | days | HE→MA | [0, 28] | 0.0% |
| `hotdrydays_ge32_smrz_p10_hepm10` | 热干复合天(>=32°C, SM<=P10) | Hot-dry days (Tmax>=32°C & SMrz<=P10) | days | HE±10 | [0, 15] | 0.0% |
| `hotdrydays_ge32_smrz_p10_v3he` | 热干复合天(>=32°C, SM<=P10) | Hot-dry days (Tmax>=32°C & SMrz<=P10) | days | V3→HE | [0, 36] | 0.0% |
| `hotdrydays_ge32_smrz_p10_v3pm10` | 热干复合天(>=32°C, SM<=P10) | Hot-dry days (Tmax>=32°C & SMrz<=P10) | days | V3±10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_smrz_p20` | 热干复合天(>=32°C, SM<=P20) | Hot-dry days (Tmax>=32°C & SMrz<=P20) | days | Full | [0, 71] | 0.0% |
| `hotdrydays_ge32_smrz_p20_hema` | 热干复合天(>=32°C, SM<=P20) | Hot-dry days (Tmax>=32°C & SMrz<=P20) | days | HE→MA | [0, 35] | 0.0% |
| `hotdrydays_ge32_smrz_p20_hepm10` | 热干复合天(>=32°C, SM<=P20) | Hot-dry days (Tmax>=32°C & SMrz<=P20) | days | HE±10 | [0, 19] | 0.0% |
| `hotdrydays_ge32_smrz_p20_v3he` | 热干复合天(>=32°C, SM<=P20) | Hot-dry days (Tmax>=32°C & SMrz<=P20) | days | V3→HE | [0, 48] | 0.0% |
| `hotdrydays_ge32_smrz_p20_v3pm10` | 热干复合天(>=32°C, SM<=P20) | Hot-dry days (Tmax>=32°C & SMrz<=P20) | days | V3±10 | [0, 21] | 0.0% |
| `hotdrydays_ge35_smrz_p10` | 热干复合天(>=35°C, SM<=P10) | Hot-dry days (Tmax>=35°C & SMrz<=P10) | days | Full | [0, 38] | 0.0% |
| `hotdrydays_ge35_smrz_p10_hema` | 热干复合天(>=35°C, SM<=P10) | Hot-dry days (Tmax>=35°C & SMrz<=P10) | days | HE→MA | [0, 18] | 0.0% |
| `hotdrydays_ge35_smrz_p10_hepm10` | 热干复合天(>=35°C, SM<=P10) | Hot-dry days (Tmax>=35°C & SMrz<=P10) | days | HE±10 | [0, 10] | 0.0% |
| `hotdrydays_ge35_smrz_p10_v3he` | 热干复合天(>=35°C, SM<=P10) | Hot-dry days (Tmax>=35°C & SMrz<=P10) | days | V3→HE | [0, 27] | 0.0% |
| `hotdrydays_ge35_smrz_p10_v3pm10` | 热干复合天(>=35°C, SM<=P10) | Hot-dry days (Tmax>=35°C & SMrz<=P10) | days | V3±10 | [0, 17] | 0.0% |
| `hotdrydays_ge35_smrz_p20` | 热干复合天(>=35°C, SM<=P20) | Hot-dry days (Tmax>=35°C & SMrz<=P20) | days | Full | [0, 42] | 0.0% |
| `hotdrydays_ge35_smrz_p20_hema` | 热干复合天(>=35°C, SM<=P20) | Hot-dry days (Tmax>=35°C & SMrz<=P20) | days | HE→MA | [0, 24] | 0.0% |
| `hotdrydays_ge35_smrz_p20_hepm10` | 热干复合天(>=35°C, SM<=P20) | Hot-dry days (Tmax>=35°C & SMrz<=P20) | days | HE±10 | [0, 12] | 0.0% |
| `hotdrydays_ge35_smrz_p20_v3he` | 热干复合天(>=35°C, SM<=P20) | Hot-dry days (Tmax>=35°C & SMrz<=P20) | days | V3→HE | [0, 35] | 0.0% |
| `hotdrydays_ge35_smrz_p20_v3pm10` | 热干复合天(>=35°C, SM<=P20) | Hot-dry days (Tmax>=35°C & SMrz<=P20) | days | V3±10 | [0, 17] | 0.0% |

## 12. Yield/SR (7 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `ca` | 秸秆还田比例 | Straw return (CA) adoption rate | 0-1 | -- | [0, 1] | 0.0% |
| `crc_ca_ratio` | CRC/CA比例 | CRC to CA ratio | 0-1 | -- | [0, 1] | 0.0% |
| `crc_lag1` | 前一年CRC | Lagged CRC adoption | 0-1 | -- | [0, 1] | 8.2% |
| `irr_frac` | 灌溉比例 | Irrigation fraction | 0-1 | -- | [0, 0.9889] | 6.1% |
| `ln_yield` | 对数单产 | Log maize yield | ln(t/ha) | -- | [-1.609, 2.996] | 0.0% |
| `maize_area_km2` | 玉米面积 | Maize planting area | km² | -- | [0.8479, 98.97] | 0.0% |
| `yield_tons_ha` | 单产 | Maize yield | t/ha | -- | [0.2001, 20] | 0.0% |

## 13. Soil Properties (7 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `aridity` | 干旱指数 | Aridity index (ET0/P) | -- | -- | [0.0123, 5.512] | 0.0% |
| `bdod_0_5cm_01deg` | 容重 | Bulk density (0-5cm) | g/cm³ | -- | [0.8933, 1.473] | 6.1% |
| `clay_0_5cm_01deg` | 粘土含量 | Clay content (0-5cm) | % | -- | [9.976, 44.34] | 6.1% |
| `phh2o_0_5cm_01deg` | 土壤pH | Soil pH (0-5cm) | -- | -- | [5.003, 8.975] | 6.2% |
| `pixel_area_km2` | 像元面积 | Pixel area | km² | -- | [77.59, 114.9] | 0.0% |
| `sand_0_5cm_01deg` | 砂粒含量 | Sand content (0-5cm) | % | -- | [7.861, 70.7] | 6.1% |
| `silt_0_5cm_01deg` | 粉粒含量 | Silt content (0-5cm) | % | -- | [16.05, 67.24] | 6.1% |

## 14. Admin (8 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `city_code` | 地市代码 | City code | -- | -- | [1.1e+05, 6.59e+05] | 0.0% |
| `city_name` | 地市名称 | City name | -- | -- | 282 unique | 0.0% |
| `county_code` | 区县代码 | County code | -- | -- | [1.101e+05, 6.59e+05] | 0.0% |
| `county_name` | 区县名称 | County name | -- | -- | 1822 unique | 0.0% |
| `prov_code` | 省份代码 | Province code | -- | -- | [1.1e+05, 6.5e+05] | 0.0% |
| `prov_id` | 省份ID | Province ID | -- | -- | 26 unique | 0.0% |
| `prov_year` | 省份-年份 | Province-year | -- | -- | [1, 102] | 0.0% |
| `province` | 省份名称 | Province name | -- | -- | 26 unique | 0.0% |

---

## Notes

- **Window abbreviations:** Full=全生育期(V3-30→MA), V3±10=三叶期±10天, HE±10=抽穗期±10天, V3→HE=营养生长期, HE→MA=灌浆成熟期
- **SM sources:** GLEAM (同化NDVI, 内生性风险最高), SWSM (XGBoost ML), ERA5-Land (仅气候态LAI, 内生性最低)
- **SM depth:** Surface=0-7/10cm, Root zone=28-100cm
- **Baseline percentiles:** GLEAM 2013-2020, SWSM/ERA5-Land 2016-2019 (DOY 90-300)
- **Temperature:** ERA5 reanalysis, 376×616 grid
- **Precipitation:** CHM_PRE (中国区域融合降水), 360×640 grid, nearest-neighbor aligned
- **Missing ~6.1%:** 约4,239行(1,512个grid)在ERA5温度边缘区域缺失，同时影响SWSM和部分v1变量
