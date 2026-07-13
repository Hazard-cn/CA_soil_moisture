# V3 Data Dictionary (1679 variables)

**Dataset:** `data_v3_main.parquet`  
**N:** 69,038 grid-year observations  
**Years:** 2016-2019  
**Spatial resolution:** 0.1 degree grid  
**Generated:** 2026-04-23  

---

## 1. Identifiers (6 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `grid_id` | 格点ID | Grid cell ID | -- | -- | [84, 3.625e+04] | 0.0% |
| `lat_idx` | 纬度索引 | Latitude index | -- | -- | [24, 318] | 0.0% |
| `latitude` | 纬度 | Latitude | degN | -- | [21.73, 51.13] | 0.0% |
| `lon_idx` | 经度索引 | Longitude index | -- | -- | [20, 610] | 0.0% |
| `longitude` | 经度 | Longitude | degE | -- | [75.58, 134.6] | 0.0% |
| `year` | 年份 | Year | -- | -- | [2016, 2019] | 0.0% |

## 2. Phenology (23 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `ca_ratio` | CA比例 | Conservation agriculture ratio | 0-1 | -- | [0, 1] | 0.0% |
| `he_doy` | HE日期 | HE day of year | DOY | -- | [116, 240] | 0.0% |
| `ma_doy` | MA日期 | MA day of year | DOY | -- | [161, 305] | 0.0% |
| `maize_frac` | 玉米种植比例 | Maize planting fraction | 0-1 | -- | [0.02, 0.9793] | 0.0% |
| `v3_doy` | V3日期 | V3 day of year | DOY | -- | [59, 205] | 0.0% |
| `win_full_days` | 全生育期窗口天数 | Full season window length | days | Full season | [87, 220] | 0.0% |
| `win_full_end` | 全生育期结束DOY | Full season window end | DOY | Full season | [161, 305] | 0.0% |
| `win_full_start` | 全生育期起始DOY | Full season window start | DOY | Full season | [29, 175] | 0.0% |
| `win_hema_days` | HE到MA窗口天数 | HE to MA window length | days | HE to MA | [13, 119] | 0.0% |
| `win_hema_end` | HE到MA结束DOY | HE to MA window end | DOY | HE to MA | [161, 305] | 0.0% |
| `win_hema_start` | HE到MA起始DOY | HE to MA window start | DOY | HE to MA | [116, 240] | 0.0% |
| `win_hepm10_days` | HE前后10天窗口天数 | HE +/- 10 days window length | days | HE +/- 10 days | [21, 21] | 0.0% |
| `win_hepm10_end` | HE前后10天结束DOY | HE +/- 10 days window end | DOY | HE +/- 10 days | [126, 250] | 0.0% |
| `win_hepm10_start` | HE前后10天起始DOY | HE +/- 10 days window start | DOY | HE +/- 10 days | [106, 230] | 0.0% |
| `win_v3he_days` | V3到HE窗口天数 | V3 to HE window length | days | V3 to HE | [17, 113] | 0.0% |
| `win_v3he_end` | V3到HE结束DOY | V3 to HE window end | DOY | V3 to HE | [116, 240] | 0.0% |
| `win_v3he_start` | V3到HE起始DOY | V3 to HE window start | DOY | V3 to HE | [59, 205] | 0.0% |
| `win_v3pm10_days` | V3前后10天窗口天数 | V3 +/- 10 days window length | days | V3 +/- 10 days | [21, 21] | 0.0% |
| `win_v3pm10_end` | V3前后10天结束DOY | V3 +/- 10 days window end | DOY | V3 +/- 10 days | [69, 215] | 0.0% |
| `win_v3pm10_start` | V3前后10天起始DOY | V3 +/- 10 days window start | DOY | V3 +/- 10 days | [49, 195] | 0.0% |
| `win_v3pre30_days` | V3前30天窗口天数 | 30 days before V3 window length | days | 30 days before V3 | [31, 31] | 0.0% |
| `win_v3pre30_end` | V3前30天结束DOY | 30 days before V3 window end | DOY | 30 days before V3 | [59, 205] | 0.0% |
| `win_v3pre30_start` | V3前30天起始DOY | 30 days before V3 window start | DOY | 30 days before V3 | [29, 175] | 0.0% |

## 3. Temperature (60 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `dtr_max` | 日较差最大值 | Diurnal temperature range max | degC | Full | [7.758, 26.97] | 6.1% |
| `dtr_max_hema` | 日较差最大值 | Diurnal temperature range max | degC | HEMA | [6.15, 22.68] | 6.1% |
| `dtr_max_hepm10` | 日较差最大值 | Diurnal temperature range max | degC | HEpm10 | [5.326, 22.68] | 6.1% |
| `dtr_max_v3he` | 日较差最大值 | Diurnal temperature range max | degC | V3HE | [6.659, 26.86] | 6.1% |
| `dtr_max_v3pm10` | 日较差最大值 | Diurnal temperature range max | degC | V3pm10 | [6.015, 26.97] | 6.1% |
| `dtr_max_v3pre30` | 日较差最大值 | Diurnal temperature range max | degC | V3pre30 | [7.758, 26.97] | 6.1% |
| `dtr_mean` | 日较差均值 | Diurnal temperature range mean | degC | Full | [4.04, 15.61] | 6.1% |
| `dtr_mean_hema` | 日较差均值 | Diurnal temperature range mean | degC | HEMA | [3.709, 16.48] | 6.1% |
| `dtr_mean_hepm10` | 日较差均值 | Diurnal temperature range mean | degC | HEpm10 | [3.619, 17.58] | 6.1% |
| `dtr_mean_v3he` | 日较差均值 | Diurnal temperature range mean | degC | V3HE | [3.841, 16.39] | 6.1% |
| `dtr_mean_v3pm10` | 日较差均值 | Diurnal temperature range mean | degC | V3pm10 | [4.132, 17.58] | 6.1% |
| `dtr_mean_v3pre30` | 日较差均值 | Diurnal temperature range mean | degC | V3pre30 | [4.17, 17.55] | 6.1% |
| `t2m_max` | 平均气温最大值 | Mean temperature max | degC | Full | [15.65, 41.09] | 6.1% |
| `t2m_max_hema` | 平均气温最大值 | Mean temperature max | degC | HEMA | [14.83, 37.54] | 6.1% |
| `t2m_max_hepm10` | 平均气温最大值 | Mean temperature max | degC | HEpm10 | [14.71, 39.45] | 6.1% |
| `t2m_max_v3he` | 平均气温最大值 | Mean temperature max | degC | V3HE | [13.69, 40.71] | 6.1% |
| `t2m_max_v3pm10` | 平均气温最大值 | Mean temperature max | degC | V3pm10 | [7.088, 41.09] | 6.1% |
| `t2m_max_v3pre30` | 平均气温最大值 | Mean temperature max | degC | V3pre30 | [4.435, 41.09] | 6.1% |
| `t2m_mean` | 平均气温均值 | Mean temperature mean | degC | Full | [9.546, 31.53] | 6.1% |
| `t2m_mean_hema` | 平均气温均值 | Mean temperature mean | degC | HEMA | [12.91, 31.1] | 6.1% |
| `t2m_mean_hepm10` | 平均气温均值 | Mean temperature mean | degC | HEpm10 | [12.98, 35.11] | 6.1% |
| `t2m_mean_v3he` | 平均气温均值 | Mean temperature mean | degC | V3HE | [8.69, 34.7] | 6.1% |
| `t2m_mean_v3pm10` | 平均气温均值 | Mean temperature mean | degC | V3pm10 | [4.082, 36.34] | 6.1% |
| `t2m_mean_v3pre30` | 平均气温均值 | Mean temperature mean | degC | V3pre30 | [1.125, 35.99] | 6.1% |
| `t2m_min` | 平均气温最小值 | Mean temperature min | degC | Full | [-7.174, 23.13] | 6.1% |
| `t2m_min_hema` | 平均气温最小值 | Mean temperature min | degC | HEMA | [2.47, 27.11] | 6.1% |
| `t2m_min_hepm10` | 平均气温最小值 | Mean temperature min | degC | HEpm10 | [9.892, 31.91] | 6.1% |
| `t2m_min_v3he` | 平均气温最小值 | Mean temperature min | degC | V3HE | [-2.762, 30.92] | 6.1% |
| `t2m_min_v3pm10` | 平均气温最小值 | Mean temperature min | degC | V3pm10 | [-6.135, 32.53] | 6.1% |
| `t2m_min_v3pre30` | 平均气温最小值 | Mean temperature min | degC | V3pre30 | [-7.174, 32.62] | 6.1% |
| `t2m_sd` | 平均气温标准差 | Mean temperature std dev | degC | Full | [1.04, 7.719] | 6.1% |
| `t2m_sd_hema` | 平均气温标准差 | Mean temperature std dev | degC | HEMA | [0.6201, 6.473] | 6.1% |
| `t2m_sd_hepm10` | 平均气温标准差 | Mean temperature std dev | degC | HEpm10 | [0.4272, 5.429] | 6.1% |
| `t2m_sd_v3he` | 平均气温标准差 | Mean temperature std dev | degC | V3HE | [0.7004, 6.066] | 6.1% |
| `t2m_sd_v3pm10` | 平均气温标准差 | Mean temperature std dev | degC | V3pm10 | [0.5276, 6.03] | 6.1% |
| `t2m_sd_v3pre30` | 平均气温标准差 | Mean temperature std dev | degC | V3pre30 | [0.7369, 6.601] | 6.1% |
| `tmax_max` | 最高气温最大值 | Maximum temperature max | degC | Full | [20.4, 46.9] | 6.1% |
| `tmax_max_hema` | 最高气温最大值 | Maximum temperature max | degC | HEMA | [19.37, 43.85] | 6.1% |
| `tmax_max_hepm10` | 最高气温最大值 | Maximum temperature max | degC | HEpm10 | [19.02, 45.37] | 6.1% |
| `tmax_max_v3he` | 最高气温最大值 | Maximum temperature max | degC | V3HE | [18.63, 46.9] | 6.1% |
| `tmax_max_v3pm10` | 最高气温最大值 | Maximum temperature max | degC | V3pm10 | [12.06, 46.84] | 6.1% |
| `tmax_max_v3pre30` | 最高气温最大值 | Maximum temperature max | degC | V3pre30 | [8.812, 46.84] | 6.1% |
| `tmax_mean` | 最高气温均值 | Maximum temperature mean | degC | Full | [14.06, 37.07] | 6.1% |
| `tmax_mean_hema` | 最高气温均值 | Maximum temperature mean | degC | HEMA | [16.87, 36.87] | 6.1% |
| `tmax_mean_hepm10` | 最高气温均值 | Maximum temperature mean | degC | HEpm10 | [15.88, 41.05] | 6.1% |
| `tmax_mean_v3he` | 最高气温均值 | Maximum temperature mean | degC | V3HE | [14.48, 40.37] | 6.1% |
| `tmax_mean_v3pm10` | 最高气温均值 | Maximum temperature mean | degC | V3pm10 | [8.432, 42.13] | 6.1% |
| `tmax_mean_v3pre30` | 最高气温均值 | Maximum temperature mean | degC | V3pre30 | [5.115, 41.54] | 6.1% |
| `tmin_mean` | 最低气温均值 | Minimum temperature mean | degC | Full | [1.181, 25.77] | 6.1% |
| `tmin_mean_hema` | 最低气温均值 | Minimum temperature mean | degC | HEMA | [4.729, 27.6] | 6.1% |
| `tmin_mean_hepm10` | 最低气温均值 | Minimum temperature mean | degC | HEpm10 | [3.47, 28.3] | 6.1% |
| `tmin_mean_v3he` | 最低气温均值 | Minimum temperature mean | degC | V3HE | [-0.04508, 27.86] | 6.1% |
| `tmin_mean_v3pm10` | 最低气温均值 | Minimum temperature mean | degC | V3pm10 | [-3.89, 28.23] | 6.1% |
| `tmin_mean_v3pre30` | 最低气温均值 | Minimum temperature mean | degC | V3pre30 | [-5.791, 28.16] | 6.1% |
| `tmin_min` | 最低气温最小值 | Minimum temperature min | degC | Full | [-16.33, 20.09] | 6.1% |
| `tmin_min_hema` | 最低气温最小值 | Minimum temperature min | degC | HEMA | [-3.624, 25] | 6.1% |
| `tmin_min_hepm10` | 最低气温最小值 | Minimum temperature min | degC | HEpm10 | [1.457, 26.45] | 6.1% |
| `tmin_min_v3he` | 最低气温最小值 | Minimum temperature min | degC | V3HE | [-11.01, 25.21] | 6.1% |
| `tmin_min_v3pm10` | 最低气温最小值 | Minimum temperature min | degC | V3pm10 | [-12.24, 25] | 6.1% |
| `tmin_min_v3pre30` | 最低气温最小值 | Minimum temperature min | degC | V3pre30 | [-16.33, 24.8] | 6.1% |

## 4. Heat Indices (180 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `gdd_10_29` | 生长度日(基温10 degC, 上限29 degC) | Growing degree days (base 10 degC, upper cap 29 degC) | degC-days | Full | [0, 2994] | 0.0% |
| `gdd_10_29_hema` | 生长度日(基温10 degC, 上限29 degC) | Growing degree days (base 10 degC, upper cap 29 degC) | degC-days | HEMA | [0, 1658] | 0.0% |
| `gdd_10_29_hepm10` | 生长度日(基温10 degC, 上限29 degC) | Growing degree days (base 10 degC, upper cap 29 degC) | degC-days | HEpm10 | [0, 399] | 0.0% |
| `gdd_10_29_v3he` | 生长度日(基温10 degC, 上限29 degC) | Growing degree days (base 10 degC, upper cap 29 degC) | degC-days | V3HE | [0, 1585] | 0.0% |
| `gdd_10_29_v3pm10` | 生长度日(基温10 degC, 上限29 degC) | Growing degree days (base 10 degC, upper cap 29 degC) | degC-days | V3pm10 | [0, 399] | 0.0% |
| `gdd_10_29_v3pre30` | 生长度日(基温10 degC, 上限29 degC) | Growing degree days (base 10 degC, upper cap 29 degC) | degC-days | V3pre30 | [0, 589] | 0.0% |
| `gdd_10_30` | 生长度日(基温10 degC, 上限30 degC) | Growing degree days (base 10 degC, upper cap 30 degC) | degC-days | Full | [0, 3014] | 0.0% |
| `gdd_10_30_hema` | 生长度日(基温10 degC, 上限30 degC) | Growing degree days (base 10 degC, upper cap 30 degC) | degC-days | HEMA | [0, 1658] | 0.0% |
| `gdd_10_30_hepm10` | 生长度日(基温10 degC, 上限30 degC) | Growing degree days (base 10 degC, upper cap 30 degC) | degC-days | HEpm10 | [0, 420] | 0.0% |
| `gdd_10_30_v3he` | 生长度日(基温10 degC, 上限30 degC) | Growing degree days (base 10 degC, upper cap 30 degC) | degC-days | V3HE | [0, 1650] | 0.0% |
| `gdd_10_30_v3pm10` | 生长度日(基温10 degC, 上限30 degC) | Growing degree days (base 10 degC, upper cap 30 degC) | degC-days | V3pm10 | [0, 420] | 0.0% |
| `gdd_10_30_v3pre30` | 生长度日(基温10 degC, 上限30 degC) | Growing degree days (base 10 degC, upper cap 30 degC) | degC-days | V3pre30 | [0, 620] | 0.0% |
| `gdd_10_31` | 生长度日(基温10 degC, 上限31 degC) | Growing degree days (base 10 degC, upper cap 31 degC) | degC-days | Full | [0, 3025] | 0.0% |
| `gdd_10_31_hema` | 生长度日(基温10 degC, 上限31 degC) | Growing degree days (base 10 degC, upper cap 31 degC) | degC-days | HEMA | [0, 1658] | 0.0% |
| `gdd_10_31_hepm10` | 生长度日(基温10 degC, 上限31 degC) | Growing degree days (base 10 degC, upper cap 31 degC) | degC-days | HEpm10 | [0, 441] | 0.0% |
| `gdd_10_31_v3he` | 生长度日(基温10 degC, 上限31 degC) | Growing degree days (base 10 degC, upper cap 31 degC) | degC-days | V3HE | [0, 1710] | 0.0% |
| `gdd_10_31_v3pm10` | 生长度日(基温10 degC, 上限31 degC) | Growing degree days (base 10 degC, upper cap 31 degC) | degC-days | V3pm10 | [0, 441] | 0.0% |
| `gdd_10_31_v3pre30` | 生长度日(基温10 degC, 上限31 degC) | Growing degree days (base 10 degC, upper cap 31 degC) | degC-days | V3pre30 | [0, 651] | 0.0% |
| `gdd_10_32` | 生长度日(基温10 degC, 上限32 degC) | Growing degree days (base 10 degC, upper cap 32 degC) | degC-days | Full | [0, 3028] | 0.0% |
| `gdd_10_32_hema` | 生长度日(基温10 degC, 上限32 degC) | Growing degree days (base 10 degC, upper cap 32 degC) | degC-days | HEMA | [0, 1658] | 0.0% |
| `gdd_10_32_hepm10` | 生长度日(基温10 degC, 上限32 degC) | Growing degree days (base 10 degC, upper cap 32 degC) | degC-days | HEpm10 | [0, 461.9] | 0.0% |
| `gdd_10_32_v3he` | 生长度日(基温10 degC, 上限32 degC) | Growing degree days (base 10 degC, upper cap 32 degC) | degC-days | V3HE | [0, 1761] | 0.0% |
| `gdd_10_32_v3pm10` | 生长度日(基温10 degC, 上限32 degC) | Growing degree days (base 10 degC, upper cap 32 degC) | degC-days | V3pm10 | [0, 462] | 0.0% |
| `gdd_10_32_v3pre30` | 生长度日(基温10 degC, 上限32 degC) | Growing degree days (base 10 degC, upper cap 32 degC) | degC-days | V3pre30 | [0, 682] | 0.0% |
| `gdd_ge10` | 生长度日(基温10 degC) | Growing degree days (base 10 degC) | degC-days | Full | [0, 3196] | 0.0% |
| `gdd_ge10_hema` | 生长度日(基温10 degC) | Growing degree days (base 10 degC) | degC-days | HEMA | [0, 1658] | 0.0% |
| `gdd_ge10_hepm10` | 生长度日(基温10 degC) | Growing degree days (base 10 degC) | degC-days | HEpm10 | [0, 527.3] | 0.0% |
| `gdd_ge10_v3he` | 生长度日(基温10 degC) | Growing degree days (base 10 degC) | degC-days | V3HE | [0, 1880] | 0.0% |
| `gdd_ge10_v3pm10` | 生长度日(基温10 degC) | Growing degree days (base 10 degC) | degC-days | V3pm10 | [0, 553.2] | 0.0% |
| `gdd_ge10_v3pre30` | 生长度日(基温10 degC) | Growing degree days (base 10 degC) | degC-days | V3pre30 | [0, 805.6] | 0.0% |
| `hdd_ge29` | 高温积温(>= 29 degC) | Heating degree days (Tmax >= 29 degC) | degC-days | Full | [0, 1236] | 0.0% |
| `hdd_ge29_hema` | 高温积温(>= 29 degC) | Heating degree days (Tmax >= 29 degC) | degC-days | HEMA | [0, 406.7] | 0.0% |
| `hdd_ge29_hepm10` | 高温积温(>= 29 degC) | Heating degree days (Tmax >= 29 degC) | degC-days | HEpm10 | [0, 253] | 0.0% |
| `hdd_ge29_v3he` | 高温积温(>= 29 degC) | Heating degree days (Tmax >= 29 degC) | degC-days | V3HE | [0, 763.3] | 0.0% |
| `hdd_ge29_v3pm10` | 高温积温(>= 29 degC) | Heating degree days (Tmax >= 29 degC) | degC-days | V3pm10 | [0, 275.8] | 0.0% |
| `hdd_ge29_v3pre30` | 高温积温(>= 29 degC) | Heating degree days (Tmax >= 29 degC) | degC-days | V3pre30 | [0, 388.7] | 0.0% |
| `hdd_ge30` | 高温积温(>= 30 degC) | Heating degree days (Tmax >= 30 degC) | degC-days | Full | [0, 1096] | 0.0% |
| `hdd_ge30_hema` | 高温积温(>= 30 degC) | Heating degree days (Tmax >= 30 degC) | degC-days | HEMA | [0, 359] | 0.0% |
| `hdd_ge30_hepm10` | 高温积温(>= 30 degC) | Heating degree days (Tmax >= 30 degC) | degC-days | HEpm10 | [0, 232] | 0.0% |
| `hdd_ge30_v3he` | 高温积温(>= 30 degC) | Heating degree days (Tmax >= 30 degC) | degC-days | V3HE | [0, 683.9] | 0.0% |
| `hdd_ge30_v3pm10` | 高温积温(>= 30 degC) | Heating degree days (Tmax >= 30 degC) | degC-days | V3pm10 | [0, 254.8] | 0.0% |
| `hdd_ge30_v3pre30` | 高温积温(>= 30 degC) | Heating degree days (Tmax >= 30 degC) | degC-days | V3pre30 | [0, 357.7] | 0.0% |
| `hdd_ge31` | 高温积温(>= 31 degC) | Heating degree days (Tmax >= 31 degC) | degC-days | Full | [0, 957.8] | 0.0% |
| `hdd_ge31_hema` | 高温积温(>= 31 degC) | Heating degree days (Tmax >= 31 degC) | degC-days | HEMA | [0, 312.4] | 0.0% |
| `hdd_ge31_hepm10` | 高温积温(>= 31 degC) | Heating degree days (Tmax >= 31 degC) | degC-days | HEpm10 | [0, 211] | 0.0% |
| `hdd_ge31_v3he` | 高温积温(>= 31 degC) | Heating degree days (Tmax >= 31 degC) | degC-days | V3HE | [0, 614.1] | 0.0% |
| `hdd_ge31_v3pm10` | 高温积温(>= 31 degC) | Heating degree days (Tmax >= 31 degC) | degC-days | V3pm10 | [0, 233.8] | 0.0% |
| `hdd_ge31_v3pre30` | 高温积温(>= 31 degC) | Heating degree days (Tmax >= 31 degC) | degC-days | V3pre30 | [0, 326.7] | 0.0% |
| `hdd_ge32` | 高温积温(>= 32 degC) | Heating degree days (Tmax >= 32 degC) | degC-days | Full | [0, 825.9] | 0.0% |
| `hdd_ge32_hema` | 高温积温(>= 32 degC) | Heating degree days (Tmax >= 32 degC) | degC-days | HEMA | [0, 267] | 0.0% |
| `hdd_ge32_hepm10` | 高温积温(>= 32 degC) | Heating degree days (Tmax >= 32 degC) | degC-days | HEpm10 | [0, 190] | 0.0% |
| `hdd_ge32_v3he` | 高温积温(>= 32 degC) | Heating degree days (Tmax >= 32 degC) | degC-days | V3HE | [0, 546.3] | 0.0% |
| `hdd_ge32_v3pm10` | 高温积温(>= 32 degC) | Heating degree days (Tmax >= 32 degC) | degC-days | V3pm10 | [0, 212.8] | 0.0% |
| `hdd_ge32_v3pre30` | 高温积温(>= 32 degC) | Heating degree days (Tmax >= 32 degC) | degC-days | V3pre30 | [0, 295.7] | 0.0% |
| `hdd_ge33` | 高温积温(>= 33 degC) | Heating degree days (Tmax >= 33 degC) | degC-days | Full | [0, 702.2] | 0.0% |
| `hdd_ge33_hema` | 高温积温(>= 33 degC) | Heating degree days (Tmax >= 33 degC) | degC-days | HEMA | [0, 223.6] | 0.0% |
| `hdd_ge33_hepm10` | 高温积温(>= 33 degC) | Heating degree days (Tmax >= 33 degC) | degC-days | HEpm10 | [0, 169] | 0.0% |
| `hdd_ge33_v3he` | 高温积温(>= 33 degC) | Heating degree days (Tmax >= 33 degC) | degC-days | V3HE | [0, 480.7] | 0.0% |
| `hdd_ge33_v3pm10` | 高温积温(>= 33 degC) | Heating degree days (Tmax >= 33 degC) | degC-days | V3pm10 | [0, 191.8] | 0.0% |
| `hdd_ge33_v3pre30` | 高温积温(>= 33 degC) | Heating degree days (Tmax >= 33 degC) | degC-days | V3pre30 | [0, 264.7] | 0.0% |
| `hdd_ge34` | 高温积温(>= 34 degC) | Heating degree days (Tmax >= 34 degC) | degC-days | Full | [0, 586.2] | 0.0% |
| `hdd_ge34_hema` | 高温积温(>= 34 degC) | Heating degree days (Tmax >= 34 degC) | degC-days | HEMA | [0, 182.8] | 0.0% |
| `hdd_ge34_hepm10` | 高温积温(>= 34 degC) | Heating degree days (Tmax >= 34 degC) | degC-days | HEpm10 | [0, 148] | 0.0% |
| `hdd_ge34_v3he` | 高温积温(>= 34 degC) | Heating degree days (Tmax >= 34 degC) | degC-days | V3HE | [0, 416.3] | 0.0% |
| `hdd_ge34_v3pm10` | 高温积温(>= 34 degC) | Heating degree days (Tmax >= 34 degC) | degC-days | V3pm10 | [0, 170.8] | 0.0% |
| `hdd_ge34_v3pre30` | 高温积温(>= 34 degC) | Heating degree days (Tmax >= 34 degC) | degC-days | V3pre30 | [0, 233.7] | 0.0% |
| `hdd_ge35` | 高温积温(>= 35 degC) | Heating degree days (Tmax >= 35 degC) | degC-days | Full | [0, 478.6] | 0.0% |
| `hdd_ge35_hema` | 高温积温(>= 35 degC) | Heating degree days (Tmax >= 35 degC) | degC-days | HEMA | [0, 148] | 0.0% |
| `hdd_ge35_hepm10` | 高温积温(>= 35 degC) | Heating degree days (Tmax >= 35 degC) | degC-days | HEpm10 | [0, 127] | 0.0% |
| `hdd_ge35_v3he` | 高温积温(>= 35 degC) | Heating degree days (Tmax >= 35 degC) | degC-days | V3HE | [0, 352.7] | 0.0% |
| `hdd_ge35_v3pm10` | 高温积温(>= 35 degC) | Heating degree days (Tmax >= 35 degC) | degC-days | V3pm10 | [0, 149.8] | 0.0% |
| `hdd_ge35_v3pre30` | 高温积温(>= 35 degC) | Heating degree days (Tmax >= 35 degC) | degC-days | V3pre30 | [0, 202.7] | 0.0% |
| `hdd_ge38` | 高温积温(>= 38 degC) | Heating degree days (Tmax >= 38 degC) | degC-days | Full | [0, 207.8] | 0.0% |
| `hdd_ge38_hema` | 高温积温(>= 38 degC) | Heating degree days (Tmax >= 38 degC) | degC-days | HEMA | [0, 58.91] | 0.0% |
| `hdd_ge38_hepm10` | 高温积温(>= 38 degC) | Heating degree days (Tmax >= 38 degC) | degC-days | HEpm10 | [0, 65.44] | 0.0% |
| `hdd_ge38_v3he` | 高温积温(>= 38 degC) | Heating degree days (Tmax >= 38 degC) | degC-days | V3HE | [0, 176.4] | 0.0% |
| `hdd_ge38_v3pm10` | 高温积温(>= 38 degC) | Heating degree days (Tmax >= 38 degC) | degC-days | V3pm10 | [0, 88.14] | 0.0% |
| `hdd_ge38_v3pre30` | 高温积温(>= 38 degC) | Heating degree days (Tmax >= 38 degC) | degC-days | V3pre30 | [0, 111] | 0.0% |
| `hdd_ge40` | 高温积温(>= 40 degC) | Heating degree days (Tmax >= 40 degC) | degC-days | Full | [0, 94.13] | 0.0% |
| `hdd_ge40_hema` | 高温积温(>= 40 degC) | Heating degree days (Tmax >= 40 degC) | degC-days | HEMA | [0, 24.66] | 0.0% |
| `hdd_ge40_hepm10` | 高温积温(>= 40 degC) | Heating degree days (Tmax >= 40 degC) | degC-days | HEpm10 | [0, 30.39] | 0.0% |
| `hdd_ge40_v3he` | 高温积温(>= 40 degC) | Heating degree days (Tmax >= 40 degC) | degC-days | V3HE | [0, 87.79] | 0.0% |
| `hdd_ge40_v3pm10` | 高温积温(>= 40 degC) | Heating degree days (Tmax >= 40 degC) | degC-days | V3pm10 | [0, 48.94] | 0.0% |
| `hdd_ge40_v3pre30` | 高温积温(>= 40 degC) | Heating degree days (Tmax >= 40 degC) | degC-days | V3pre30 | [0, 58.02] | 0.0% |
| `hdd_ge_basep90` | 高温积温(>= P90) | HDD (Tmax >= P90 baseline) | degC-days | Full | [0, 142.4] | 0.0% |
| `hdd_ge_basep90_hema` | 高温积温(>= P90) | HDD (Tmax >= P90 baseline) | degC-days | HEMA | [0, 80.65] | 0.0% |
| `hdd_ge_basep90_hepm10` | 高温积温(>= P90) | HDD (Tmax >= P90 baseline) | degC-days | HEpm10 | [0, 72.8] | 0.0% |
| `hdd_ge_basep90_v3he` | 高温积温(>= P90) | HDD (Tmax >= P90 baseline) | degC-days | V3HE | [0, 112.4] | 0.0% |
| `hdd_ge_basep90_v3pm10` | 高温积温(>= P90) | HDD (Tmax >= P90 baseline) | degC-days | V3pm10 | [0, 83.69] | 0.0% |
| `hdd_ge_basep90_v3pre30` | 高温积温(>= P90) | HDD (Tmax >= P90 baseline) | degC-days | V3pre30 | [0, 92.01] | 0.0% |
| `hdd_ge_basep95` | 高温积温(>= P95) | HDD (Tmax >= P95 baseline) | degC-days | Full | [0, 84.74] | 0.0% |
| `hdd_ge_basep95_hema` | 高温积温(>= P95) | HDD (Tmax >= P95 baseline) | degC-days | HEMA | [0, 51.68] | 0.0% |
| `hdd_ge_basep95_hepm10` | 高温积温(>= P95) | HDD (Tmax >= P95 baseline) | degC-days | HEpm10 | [0, 49.9] | 0.0% |
| `hdd_ge_basep95_v3he` | 高温积温(>= P95) | HDD (Tmax >= P95 baseline) | degC-days | V3HE | [0, 63.13] | 0.0% |
| `hdd_ge_basep95_v3pm10` | 高温积温(>= P95) | HDD (Tmax >= P95 baseline) | degC-days | V3pm10 | [0, 56.09] | 0.0% |
| `hdd_ge_basep95_v3pre30` | 高温积温(>= P95) | HDD (Tmax >= P95 baseline) | degC-days | V3pre30 | [0, 59.59] | 0.0% |
| `hotdays_ge29` | 高温日数(>= 29 degC) | Hot days (Tmax >= 29 degC) | days | Full | [0, 151] | 0.0% |
| `hotdays_ge29_hema` | 高温日数(>= 29 degC) | Hot days (Tmax >= 29 degC) | days | HEMA | [0, 81] | 0.0% |
| `hotdays_ge29_hepm10` | 高温日数(>= 29 degC) | Hot days (Tmax >= 29 degC) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdays_ge29_v3he` | 高温日数(>= 29 degC) | Hot days (Tmax >= 29 degC) | days | V3HE | [0, 83] | 0.0% |
| `hotdays_ge29_v3pm10` | 高温日数(>= 29 degC) | Hot days (Tmax >= 29 degC) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdays_ge29_v3pre30` | 高温日数(>= 29 degC) | Hot days (Tmax >= 29 degC) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdays_ge30` | 高温日数(>= 30 degC) | Hot days (Tmax >= 30 degC) | days | Full | [0, 140] | 0.0% |
| `hotdays_ge30_hema` | 高温日数(>= 30 degC) | Hot days (Tmax >= 30 degC) | days | HEMA | [0, 69] | 0.0% |
| `hotdays_ge30_hepm10` | 高温日数(>= 30 degC) | Hot days (Tmax >= 30 degC) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdays_ge30_v3he` | 高温日数(>= 30 degC) | Hot days (Tmax >= 30 degC) | days | V3HE | [0, 82] | 0.0% |
| `hotdays_ge30_v3pm10` | 高温日数(>= 30 degC) | Hot days (Tmax >= 30 degC) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdays_ge30_v3pre30` | 高温日数(>= 30 degC) | Hot days (Tmax >= 30 degC) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdays_ge31` | 高温日数(>= 31 degC) | Hot days (Tmax >= 31 degC) | days | Full | [0, 134] | 0.0% |
| `hotdays_ge31_hema` | 高温日数(>= 31 degC) | Hot days (Tmax >= 31 degC) | days | HEMA | [0, 60] | 0.0% |
| `hotdays_ge31_hepm10` | 高温日数(>= 31 degC) | Hot days (Tmax >= 31 degC) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdays_ge31_v3he` | 高温日数(>= 31 degC) | Hot days (Tmax >= 31 degC) | days | V3HE | [0, 79] | 0.0% |
| `hotdays_ge31_v3pm10` | 高温日数(>= 31 degC) | Hot days (Tmax >= 31 degC) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdays_ge31_v3pre30` | 高温日数(>= 31 degC) | Hot days (Tmax >= 31 degC) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdays_ge32` | 高温日数(>= 32 degC) | Hot days (Tmax >= 32 degC) | days | Full | [0, 128] | 0.0% |
| `hotdays_ge32_hema` | 高温日数(>= 32 degC) | Hot days (Tmax >= 32 degC) | days | HEMA | [0, 55] | 0.0% |
| `hotdays_ge32_hepm10` | 高温日数(>= 32 degC) | Hot days (Tmax >= 32 degC) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdays_ge32_v3he` | 高温日数(>= 32 degC) | Hot days (Tmax >= 32 degC) | days | V3HE | [0, 78] | 0.0% |
| `hotdays_ge32_v3pm10` | 高温日数(>= 32 degC) | Hot days (Tmax >= 32 degC) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdays_ge32_v3pre30` | 高温日数(>= 32 degC) | Hot days (Tmax >= 32 degC) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdays_ge33` | 高温日数(>= 33 degC) | Hot days (Tmax >= 33 degC) | days | Full | [0, 120] | 0.0% |
| `hotdays_ge33_hema` | 高温日数(>= 33 degC) | Hot days (Tmax >= 33 degC) | days | HEMA | [0, 45] | 0.0% |
| `hotdays_ge33_hepm10` | 高温日数(>= 33 degC) | Hot days (Tmax >= 33 degC) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdays_ge33_v3he` | 高温日数(>= 33 degC) | Hot days (Tmax >= 33 degC) | days | V3HE | [0, 75] | 0.0% |
| `hotdays_ge33_v3pm10` | 高温日数(>= 33 degC) | Hot days (Tmax >= 33 degC) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdays_ge33_v3pre30` | 高温日数(>= 33 degC) | Hot days (Tmax >= 33 degC) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdays_ge34` | 高温日数(>= 34 degC) | Hot days (Tmax >= 34 degC) | days | Full | [0, 111] | 0.0% |
| `hotdays_ge34_hema` | 高温日数(>= 34 degC) | Hot days (Tmax >= 34 degC) | days | HEMA | [0, 40] | 0.0% |
| `hotdays_ge34_hepm10` | 高温日数(>= 34 degC) | Hot days (Tmax >= 34 degC) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdays_ge34_v3he` | 高温日数(>= 34 degC) | Hot days (Tmax >= 34 degC) | days | V3HE | [0, 72] | 0.0% |
| `hotdays_ge34_v3pm10` | 高温日数(>= 34 degC) | Hot days (Tmax >= 34 degC) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdays_ge34_v3pre30` | 高温日数(>= 34 degC) | Hot days (Tmax >= 34 degC) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdays_ge35` | 高温日数(>= 35 degC) | Hot days (Tmax >= 35 degC) | days | Full | [0, 106] | 0.0% |
| `hotdays_ge35_hema` | 高温日数(>= 35 degC) | Hot days (Tmax >= 35 degC) | days | HEMA | [0, 37] | 0.0% |
| `hotdays_ge35_hepm10` | 高温日数(>= 35 degC) | Hot days (Tmax >= 35 degC) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdays_ge35_v3he` | 高温日数(>= 35 degC) | Hot days (Tmax >= 35 degC) | days | V3HE | [0, 69] | 0.0% |
| `hotdays_ge35_v3pm10` | 高温日数(>= 35 degC) | Hot days (Tmax >= 35 degC) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdays_ge35_v3pre30` | 高温日数(>= 35 degC) | Hot days (Tmax >= 35 degC) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdays_ge38` | 高温日数(>= 38 degC) | Hot days (Tmax >= 38 degC) | days | Full | [0, 71] | 0.0% |
| `hotdays_ge38_hema` | 高温日数(>= 38 degC) | Hot days (Tmax >= 38 degC) | days | HEMA | [0, 25] | 0.0% |
| `hotdays_ge38_hepm10` | 高温日数(>= 38 degC) | Hot days (Tmax >= 38 degC) | days | HEpm10 | [0, 19] | 0.0% |
| `hotdays_ge38_v3he` | 高温日数(>= 38 degC) | Hot days (Tmax >= 38 degC) | days | V3HE | [0, 52] | 0.0% |
| `hotdays_ge38_v3pm10` | 高温日数(>= 38 degC) | Hot days (Tmax >= 38 degC) | days | V3pm10 | [0, 20] | 0.0% |
| `hotdays_ge38_v3pre30` | 高温日数(>= 38 degC) | Hot days (Tmax >= 38 degC) | days | V3pre30 | [0, 29] | 0.0% |
| `hotdays_ge40` | 高温日数(>= 40 degC) | Hot days (Tmax >= 40 degC) | days | Full | [0, 43] | 0.0% |
| `hotdays_ge40_hema` | 高温日数(>= 40 degC) | Hot days (Tmax >= 40 degC) | days | HEMA | [0, 15] | 0.0% |
| `hotdays_ge40_hepm10` | 高温日数(>= 40 degC) | Hot days (Tmax >= 40 degC) | days | HEpm10 | [0, 16] | 0.0% |
| `hotdays_ge40_v3he` | 高温日数(>= 40 degC) | Hot days (Tmax >= 40 degC) | days | V3HE | [0, 37] | 0.0% |
| `hotdays_ge40_v3pm10` | 高温日数(>= 40 degC) | Hot days (Tmax >= 40 degC) | days | V3pm10 | [0, 17] | 0.0% |
| `hotdays_ge40_v3pre30` | 高温日数(>= 40 degC) | Hot days (Tmax >= 40 degC) | days | V3pre30 | [0, 22] | 0.0% |
| `hotdays_ge_basep90` | 高温日数(>= P90) | Hot days (Tmax >= P90 baseline) | days | Full | [0, 60] | 0.0% |
| `hotdays_ge_basep90_hema` | 高温日数(>= P90) | Hot days (Tmax >= P90 baseline) | days | HEMA | [0, 38] | 0.0% |
| `hotdays_ge_basep90_hepm10` | 高温日数(>= P90) | Hot days (Tmax >= P90 baseline) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdays_ge_basep90_v3he` | 高温日数(>= P90) | Hot days (Tmax >= P90 baseline) | days | V3HE | [0, 48] | 0.0% |
| `hotdays_ge_basep90_v3pm10` | 高温日数(>= P90) | Hot days (Tmax >= P90 baseline) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdays_ge_basep90_v3pre30` | 高温日数(>= P90) | Hot days (Tmax >= P90 baseline) | days | V3pre30 | [0, 30] | 0.0% |
| `hotdays_ge_basep95` | 高温日数(>= P95) | Hot days (Tmax >= P95 baseline) | days | Full | [0, 41] | 0.0% |
| `hotdays_ge_basep95_hema` | 高温日数(>= P95) | Hot days (Tmax >= P95 baseline) | days | HEMA | [0, 26] | 0.0% |
| `hotdays_ge_basep95_hepm10` | 高温日数(>= P95) | Hot days (Tmax >= P95 baseline) | days | HEpm10 | [0, 19] | 0.0% |
| `hotdays_ge_basep95_v3he` | 高温日数(>= P95) | Hot days (Tmax >= P95 baseline) | days | V3HE | [0, 32] | 0.0% |
| `hotdays_ge_basep95_v3pm10` | 高温日数(>= P95) | Hot days (Tmax >= P95 baseline) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdays_ge_basep95_v3pre30` | 高温日数(>= P95) | Hot days (Tmax >= P95 baseline) | days | V3pre30 | [0, 28] | 0.0% |
| `nightheat_ge20` | 夜间高温日数(>= 20 degC) | Night heat days (Tmin >= 20 degC) | days | Full | [0, 161] | 0.0% |
| `nightheat_ge20_hema` | 夜间高温日数(>= 20 degC) | Night heat days (Tmin >= 20 degC) | days | HEMA | [0, 97] | 0.0% |
| `nightheat_ge20_hepm10` | 夜间高温日数(>= 20 degC) | Night heat days (Tmin >= 20 degC) | days | HEpm10 | [0, 21] | 0.0% |
| `nightheat_ge20_v3he` | 夜间高温日数(>= 20 degC) | Night heat days (Tmin >= 20 degC) | days | V3HE | [0, 82] | 0.0% |
| `nightheat_ge20_v3pm10` | 夜间高温日数(>= 20 degC) | Night heat days (Tmin >= 20 degC) | days | V3pm10 | [0, 21] | 0.0% |
| `nightheat_ge20_v3pre30` | 夜间高温日数(>= 20 degC) | Night heat days (Tmin >= 20 degC) | days | V3pre30 | [0, 31] | 0.0% |
| `nightheat_ge22` | 夜间高温日数(>= 22 degC) | Night heat days (Tmin >= 22 degC) | days | Full | [0, 130] | 0.0% |
| `nightheat_ge22_hema` | 夜间高温日数(>= 22 degC) | Night heat days (Tmin >= 22 degC) | days | HEMA | [0, 92] | 0.0% |
| `nightheat_ge22_hepm10` | 夜间高温日数(>= 22 degC) | Night heat days (Tmin >= 22 degC) | days | HEpm10 | [0, 21] | 0.0% |
| `nightheat_ge22_v3he` | 夜间高温日数(>= 22 degC) | Night heat days (Tmin >= 22 degC) | days | V3HE | [0, 75] | 0.0% |
| `nightheat_ge22_v3pm10` | 夜间高温日数(>= 22 degC) | Night heat days (Tmin >= 22 degC) | days | V3pm10 | [0, 21] | 0.0% |
| `nightheat_ge22_v3pre30` | 夜间高温日数(>= 22 degC) | Night heat days (Tmin >= 22 degC) | days | V3pre30 | [0, 31] | 0.0% |
| `nightheat_ge24` | 夜间高温日数(>= 24 degC) | Night heat days (Tmin >= 24 degC) | days | Full | [0, 95] | 0.0% |
| `nightheat_ge24_hema` | 夜间高温日数(>= 24 degC) | Night heat days (Tmin >= 24 degC) | days | HEMA | [0, 82] | 0.0% |
| `nightheat_ge24_hepm10` | 夜间高温日数(>= 24 degC) | Night heat days (Tmin >= 24 degC) | days | HEpm10 | [0, 21] | 0.0% |
| `nightheat_ge24_v3he` | 夜间高温日数(>= 24 degC) | Night heat days (Tmin >= 24 degC) | days | V3HE | [0, 61] | 0.0% |
| `nightheat_ge24_v3pm10` | 夜间高温日数(>= 24 degC) | Night heat days (Tmin >= 24 degC) | days | V3pm10 | [0, 21] | 0.0% |
| `nightheat_ge24_v3pre30` | 夜间高温日数(>= 24 degC) | Night heat days (Tmin >= 24 degC) | days | V3pre30 | [0, 31] | 0.0% |

## 5. Precipitation (60 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `drydays_lt1` | 干日数(降水 < 1 mm) | Dry days (precipitation < 1 mm) | days | Full | [0, 158] | 0.0% |
| `drydays_lt1_hema` | 干日数(降水 < 1 mm) | Dry days (precipitation < 1 mm) | days | HEMA | [0, 67] | 0.0% |
| `drydays_lt1_hepm10` | 干日数(降水 < 1 mm) | Dry days (precipitation < 1 mm) | days | HEpm10 | [0, 21] | 0.0% |
| `drydays_lt1_v3he` | 干日数(降水 < 1 mm) | Dry days (precipitation < 1 mm) | days | V3HE | [0, 90] | 0.0% |
| `drydays_lt1_v3pm10` | 干日数(降水 < 1 mm) | Dry days (precipitation < 1 mm) | days | V3pm10 | [0, 21] | 0.0% |
| `drydays_lt1_v3pre30` | 干日数(降水 < 1 mm) | Dry days (precipitation < 1 mm) | days | V3pre30 | [0, 31] | 0.0% |
| `max_cdd` | 最长连续干日 | Maximum consecutive dry days | days | Full | [0, 114] | 0.0% |
| `max_cdd_hema` | 最长连续干日 | Maximum consecutive dry days | days | HEMA | [0, 52] | 0.0% |
| `max_cdd_hepm10` | 最长连续干日 | Maximum consecutive dry days | days | HEpm10 | [0, 21] | 0.0% |
| `max_cdd_v3he` | 最长连续干日 | Maximum consecutive dry days | days | V3HE | [0, 83] | 0.0% |
| `max_cdd_v3pm10` | 最长连续干日 | Maximum consecutive dry days | days | V3pm10 | [0, 21] | 0.0% |
| `max_cdd_v3pre30` | 最长连续干日 | Maximum consecutive dry days | days | V3pre30 | [0, 31] | 0.0% |
| `max_cwd` | 最长连续湿日 | Maximum consecutive wet days | days | Full | [0, 80] | 0.0% |
| `max_cwd_hema` | 最长连续湿日 | Maximum consecutive wet days | days | HEMA | [0, 62] | 0.0% |
| `max_cwd_hepm10` | 最长连续湿日 | Maximum consecutive wet days | days | HEpm10 | [0, 21] | 0.0% |
| `max_cwd_v3he` | 最长连续湿日 | Maximum consecutive wet days | days | V3HE | [0, 55] | 0.0% |
| `max_cwd_v3pm10` | 最长连续湿日 | Maximum consecutive wet days | days | V3pm10 | [0, 20] | 0.0% |
| `max_cwd_v3pre30` | 最长连续湿日 | Maximum consecutive wet days | days | V3pre30 | [0, 18] | 0.0% |
| `pr_intensity` | 降水强度 | Precipitation intensity | mm | Full | [0, 33.73] | 0.0% |
| `pr_intensity_hema` | 降水强度 | Precipitation intensity | mm | HEMA | [0, 66.26] | 0.0% |
| `pr_intensity_hepm10` | 降水强度 | Precipitation intensity | mm | HEpm10 | [0, 65.03] | 0.0% |
| `pr_intensity_v3he` | 降水强度 | Precipitation intensity | mm | V3HE | [0, 39.39] | 0.0% |
| `pr_intensity_v3pm10` | 降水强度 | Precipitation intensity | mm | V3pm10 | [0, 80.85] | 0.0% |
| `pr_intensity_v3pre30` | 降水强度 | Precipitation intensity | mm | V3pre30 | [0, 82.46] | 0.0% |
| `pr_max` | 降水最大值 | Precipitation max | mm | Full | [1.45, 679.6] | 0.0% |
| `pr_max_hema` | 降水最大值 | Precipitation max | mm | HEMA | [0.03, 344.1] | 0.0% |
| `pr_max_hepm10` | 降水最大值 | Precipitation max | mm | HEpm10 | [0, 344.1] | 0.0% |
| `pr_max_v3he` | 降水最大值 | Precipitation max | mm | V3HE | [0.04, 313.2] | 0.0% |
| `pr_max_v3pm10` | 降水最大值 | Precipitation max | mm | V3pm10 | [0, 191.9] | 0.0% |
| `pr_max_v3pre30` | 降水最大值 | Precipitation max | mm | V3pre30 | [0.01, 679.6] | 0.0% |
| `pr_mean` | 降水均值 | Precipitation mean | mm | Full | [0.07098, 14.92] | 0.0% |
| `pr_mean_hema` | 降水均值 | Precipitation mean | mm | HEMA | [0.002174, 30.47] | 0.0% |
| `pr_mean_hepm10` | 降水均值 | Precipitation mean | mm | HEpm10 | [0, 42.48] | 0.0% |
| `pr_mean_v3he` | 降水均值 | Precipitation mean | mm | V3HE | [0.006452, 19.15] | 0.0% |
| `pr_mean_v3pm10` | 降水均值 | Precipitation mean | mm | V3pm10 | [0, 23.48] | 0.0% |
| `pr_mean_v3pre30` | 降水均值 | Precipitation mean | mm | V3pre30 | [0.0003226, 24] | 0.0% |
| `pr_sd` | 降水标准差 | Precipitation std dev | mm | Full | [0.1972, 48.86] | 0.0% |
| `pr_sd_hema` | 降水标准差 | Precipitation std dev | mm | HEMA | [0.006964, 57.77] | 0.0% |
| `pr_sd_hepm10` | 降水标准差 | Precipitation std dev | mm | HEpm10 | [0, 74.37] | 0.0% |
| `pr_sd_v3he` | 降水标准差 | Precipitation std dev | mm | V3HE | [0.01305, 45.96] | 0.0% |
| `pr_sd_v3pm10` | 降水标准差 | Precipitation std dev | mm | V3pm10 | [0, 42.23] | 0.0% |
| `pr_sd_v3pre30` | 降水标准差 | Precipitation std dev | mm | V3pre30 | [0.001796, 121.8] | 0.0% |
| `pr_sum` | 降水总量 | Precipitation sum | mm | Full | [0, 2819] | 0.0% |
| `pr_sum_hema` | 降水总量 | Precipitation sum | mm | HEMA | [0, 1797] | 0.0% |
| `pr_sum_hepm10` | 降水总量 | Precipitation sum | mm | HEpm10 | [0, 892.1] | 0.0% |
| `pr_sum_v3he` | 降水总量 | Precipitation sum | mm | V3HE | [0, 1283] | 0.0% |
| `pr_sum_v3pm10` | 降水总量 | Precipitation sum | mm | V3pm10 | [0, 493] | 0.0% |
| `pr_sum_v3pre30` | 降水总量 | Precipitation sum | mm | V3pre30 | [0, 744.1] | 0.0% |
| `wetdays_ge10` | 湿日数(降水 >= 10 mm) | Wet days (precipitation >= 10 mm) | days | Full | [0, 89] | 0.0% |
| `wetdays_ge10_hema` | 湿日数(降水 >= 10 mm) | Wet days (precipitation >= 10 mm) | days | HEMA | [0, 54] | 0.0% |
| `wetdays_ge10_hepm10` | 湿日数(降水 >= 10 mm) | Wet days (precipitation >= 10 mm) | days | HEpm10 | [0, 19] | 0.0% |
| `wetdays_ge10_v3he` | 湿日数(降水 >= 10 mm) | Wet days (precipitation >= 10 mm) | days | V3HE | [0, 46] | 0.0% |
| `wetdays_ge10_v3pm10` | 湿日数(降水 >= 10 mm) | Wet days (precipitation >= 10 mm) | days | V3pm10 | [0, 13] | 0.0% |
| `wetdays_ge10_v3pre30` | 湿日数(降水 >= 10 mm) | Wet days (precipitation >= 10 mm) | days | V3pre30 | [0, 13] | 0.0% |
| `wetdays_ge20` | 湿日数(降水 >= 20 mm) | Wet days (precipitation >= 20 mm) | days | Full | [0, 50] | 0.0% |
| `wetdays_ge20_hema` | 湿日数(降水 >= 20 mm) | Wet days (precipitation >= 20 mm) | days | HEMA | [0, 36] | 0.0% |
| `wetdays_ge20_hepm10` | 湿日数(降水 >= 20 mm) | Wet days (precipitation >= 20 mm) | days | HEpm10 | [0, 15] | 0.0% |
| `wetdays_ge20_v3he` | 湿日数(降水 >= 20 mm) | Wet days (precipitation >= 20 mm) | days | V3HE | [0, 24] | 0.0% |
| `wetdays_ge20_v3pm10` | 湿日数(降水 >= 20 mm) | Wet days (precipitation >= 20 mm) | days | V3pm10 | [0, 9] | 0.0% |
| `wetdays_ge20_v3pre30` | 湿日数(降水 >= 20 mm) | Wet days (precipitation >= 20 mm) | days | V3pre30 | [0, 10] | 0.0% |

## 6. SM-GLEAM (464 vars)

### legacy baseline-local

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `drydays_gleam_smrz_le_p10` | GLEAM根区土壤湿度低于本地历史P10的日数 | Days with GLEAM root-zone soil moisture <= local historical P10 | days | Full | [0, 126] | 0.0% |
| `drydays_gleam_smrz_le_p10_hema` | GLEAM根区土壤湿度低于本地历史P10的日数 | Days with GLEAM root-zone soil moisture <= local historical P10 | days | HEMA | [0, 52] | 0.0% |
| `drydays_gleam_smrz_le_p10_hepm10` | GLEAM根区土壤湿度低于本地历史P10的日数 | Days with GLEAM root-zone soil moisture <= local historical P10 | days | HEpm10 | [0, 21] | 0.0% |
| `drydays_gleam_smrz_le_p10_v3he` | GLEAM根区土壤湿度低于本地历史P10的日数 | Days with GLEAM root-zone soil moisture <= local historical P10 | days | V3HE | [0, 81] | 0.0% |
| `drydays_gleam_smrz_le_p10_v3pm10` | GLEAM根区土壤湿度低于本地历史P10的日数 | Days with GLEAM root-zone soil moisture <= local historical P10 | days | V3pm10 | [0, 21] | 0.0% |
| `drydays_gleam_smrz_le_p10_v3pre30` | GLEAM根区土壤湿度低于本地历史P10的日数 | Days with GLEAM root-zone soil moisture <= local historical P10 | days | V3pre30 | [0, 31] | 0.0% |
| `drydays_gleam_smrz_le_p20` | GLEAM根区土壤湿度低于本地历史P20的日数 | Days with GLEAM root-zone soil moisture <= local historical P20 | days | Full | [0, 175] | 0.0% |
| `drydays_gleam_smrz_le_p20_hema` | GLEAM根区土壤湿度低于本地历史P20的日数 | Days with GLEAM root-zone soil moisture <= local historical P20 | days | HEMA | [0, 73] | 0.0% |
| `drydays_gleam_smrz_le_p20_hepm10` | GLEAM根区土壤湿度低于本地历史P20的日数 | Days with GLEAM root-zone soil moisture <= local historical P20 | days | HEpm10 | [0, 21] | 0.0% |
| `drydays_gleam_smrz_le_p20_v3he` | GLEAM根区土壤湿度低于本地历史P20的日数 | Days with GLEAM root-zone soil moisture <= local historical P20 | days | V3HE | [0, 93] | 0.0% |
| `drydays_gleam_smrz_le_p20_v3pm10` | GLEAM根区土壤湿度低于本地历史P20的日数 | Days with GLEAM root-zone soil moisture <= local historical P20 | days | V3pm10 | [0, 21] | 0.0% |
| `drydays_gleam_smrz_le_p20_v3pre30` | GLEAM根区土壤湿度低于本地历史P20的日数 | Days with GLEAM root-zone soil moisture <= local historical P20 | days | V3pre30 | [0, 31] | 0.0% |
| `drydays_gleam_sms_le_p10` | GLEAM表层土壤湿度低于本地历史P10的日数 | Days with GLEAM surface soil moisture <= local historical P10 | days | Full | [0, 89] | 0.0% |
| `drydays_gleam_sms_le_p10_hema` | GLEAM表层土壤湿度低于本地历史P10的日数 | Days with GLEAM surface soil moisture <= local historical P10 | days | HEMA | [0, 37] | 0.0% |
| `drydays_gleam_sms_le_p10_hepm10` | GLEAM表层土壤湿度低于本地历史P10的日数 | Days with GLEAM surface soil moisture <= local historical P10 | days | HEpm10 | [0, 21] | 0.0% |
| `drydays_gleam_sms_le_p10_v3he` | GLEAM表层土壤湿度低于本地历史P10的日数 | Days with GLEAM surface soil moisture <= local historical P10 | days | V3HE | [0, 54] | 0.0% |
| `drydays_gleam_sms_le_p10_v3pm10` | GLEAM表层土壤湿度低于本地历史P10的日数 | Days with GLEAM surface soil moisture <= local historical P10 | days | V3pm10 | [0, 21] | 0.0% |
| `drydays_gleam_sms_le_p10_v3pre30` | GLEAM表层土壤湿度低于本地历史P10的日数 | Days with GLEAM surface soil moisture <= local historical P10 | days | V3pre30 | [0, 31] | 0.0% |
| `drydays_gleam_sms_le_p20` | GLEAM表层土壤湿度低于本地历史P20的日数 | Days with GLEAM surface soil moisture <= local historical P20 | days | Full | [0, 120] | 0.0% |
| `drydays_gleam_sms_le_p20_hema` | GLEAM表层土壤湿度低于本地历史P20的日数 | Days with GLEAM surface soil moisture <= local historical P20 | days | HEMA | [0, 43] | 0.0% |
| `drydays_gleam_sms_le_p20_hepm10` | GLEAM表层土壤湿度低于本地历史P20的日数 | Days with GLEAM surface soil moisture <= local historical P20 | days | HEpm10 | [0, 21] | 0.0% |
| `drydays_gleam_sms_le_p20_v3he` | GLEAM表层土壤湿度低于本地历史P20的日数 | Days with GLEAM surface soil moisture <= local historical P20 | days | V3HE | [0, 73] | 0.0% |
| `drydays_gleam_sms_le_p20_v3pm10` | GLEAM表层土壤湿度低于本地历史P20的日数 | Days with GLEAM surface soil moisture <= local historical P20 | days | V3pm10 | [0, 21] | 0.0% |
| `drydays_gleam_sms_le_p20_v3pre30` | GLEAM表层土壤湿度低于本地历史P20的日数 | Days with GLEAM surface soil moisture <= local historical P20 | days | V3pre30 | [0, 31] | 0.0% |
| `drydeficit_gleam_smrz_le_p10` | GLEAM根区土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for GLEAM root-zone soil moisture | m3/m3 | Full | [0, 0.0455] | 0.0% |
| `drydeficit_gleam_smrz_le_p10_hema` | GLEAM根区土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for GLEAM root-zone soil moisture | m3/m3 | HEMA | [0, 0.04372] | 0.0% |
| `drydeficit_gleam_smrz_le_p10_hepm10` | GLEAM根区土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for GLEAM root-zone soil moisture | m3/m3 | HEpm10 | [0, 0.05747] | 0.0% |
| `drydeficit_gleam_smrz_le_p10_v3he` | GLEAM根区土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for GLEAM root-zone soil moisture | m3/m3 | V3HE | [0, 0.06586] | 0.0% |
| `drydeficit_gleam_smrz_le_p10_v3pm10` | GLEAM根区土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for GLEAM root-zone soil moisture | m3/m3 | V3pm10 | [0, 0.09284] | 0.0% |
| `drydeficit_gleam_smrz_le_p10_v3pre30` | GLEAM根区土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for GLEAM root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.08121] | 0.0% |
| `drydeficit_gleam_smrz_le_p20` | GLEAM根区土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for GLEAM root-zone soil moisture | m3/m3 | Full | [0, 0.06721] | 0.0% |
| `drydeficit_gleam_smrz_le_p20_hema` | GLEAM根区土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for GLEAM root-zone soil moisture | m3/m3 | HEMA | [0, 0.07164] | 0.0% |
| `drydeficit_gleam_smrz_le_p20_hepm10` | GLEAM根区土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for GLEAM root-zone soil moisture | m3/m3 | HEpm10 | [0, 0.07732] | 0.0% |
| `drydeficit_gleam_smrz_le_p20_v3he` | GLEAM根区土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for GLEAM root-zone soil moisture | m3/m3 | V3HE | [0, 0.0946] | 0.0% |
| `drydeficit_gleam_smrz_le_p20_v3pm10` | GLEAM根区土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for GLEAM root-zone soil moisture | m3/m3 | V3pm10 | [0, 0.1239] | 0.0% |
| `drydeficit_gleam_smrz_le_p20_v3pre30` | GLEAM根区土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for GLEAM root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.1183] | 0.0% |
| `drydeficit_gleam_sms_le_p10` | GLEAM表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for GLEAM surface soil moisture | m3/m3 | Full | [0, 0.03625] | 0.0% |
| `drydeficit_gleam_sms_le_p10_hema` | GLEAM表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for GLEAM surface soil moisture | m3/m3 | HEMA | [0, 0.01941] | 0.0% |
| `drydeficit_gleam_sms_le_p10_hepm10` | GLEAM表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for GLEAM surface soil moisture | m3/m3 | HEpm10 | [0, 0.02778] | 0.0% |
| `drydeficit_gleam_sms_le_p10_v3he` | GLEAM表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for GLEAM surface soil moisture | m3/m3 | V3HE | [0, 0.05212] | 0.0% |
| `drydeficit_gleam_sms_le_p10_v3pm10` | GLEAM表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for GLEAM surface soil moisture | m3/m3 | V3pm10 | [0, 0.09986] | 0.0% |
| `drydeficit_gleam_sms_le_p10_v3pre30` | GLEAM表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for GLEAM surface soil moisture | m3/m3 | V3pre30 | [0, 0.1242] | 0.0% |
| `drydeficit_gleam_sms_le_p20` | GLEAM表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for GLEAM surface soil moisture | m3/m3 | Full | [0, 0.0562] | 0.0% |
| `drydeficit_gleam_sms_le_p20_hema` | GLEAM表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for GLEAM surface soil moisture | m3/m3 | HEMA | [0, 0.03631] | 0.0% |
| `drydeficit_gleam_sms_le_p20_hepm10` | GLEAM表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for GLEAM surface soil moisture | m3/m3 | HEpm10 | [0, 0.05504] | 0.0% |
| `drydeficit_gleam_sms_le_p20_v3he` | GLEAM表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for GLEAM surface soil moisture | m3/m3 | V3HE | [0, 0.07832] | 0.0% |
| `drydeficit_gleam_sms_le_p20_v3pm10` | GLEAM表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for GLEAM surface soil moisture | m3/m3 | V3pm10 | [0, 0.1396] | 0.0% |
| `drydeficit_gleam_sms_le_p20_v3pre30` | GLEAM表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for GLEAM surface soil moisture | m3/m3 | V3pre30 | [0, 0.1475] | 0.0% |
| `dryshare_gleam_smrz_le_p10` | GLEAM根区土壤湿度低于本地历史P10的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local historical P10 | 0-1 | Full | [0, 0.9474] | 0.0% |
| `dryshare_gleam_smrz_le_p10_hema` | GLEAM根区土壤湿度低于本地历史P10的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local historical P10 | 0-1 | HEMA | [0, 1] | 0.0% |
| `dryshare_gleam_smrz_le_p10_hepm10` | GLEAM根区土壤湿度低于本地历史P10的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local historical P10 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `dryshare_gleam_smrz_le_p10_v3he` | GLEAM根区土壤湿度低于本地历史P10的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local historical P10 | 0-1 | V3HE | [0, 1] | 0.0% |
| `dryshare_gleam_smrz_le_p10_v3pm10` | GLEAM根区土壤湿度低于本地历史P10的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local historical P10 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `dryshare_gleam_smrz_le_p10_v3pre30` | GLEAM根区土壤湿度低于本地历史P10的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local historical P10 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `dryshare_gleam_smrz_le_p20` | GLEAM根区土壤湿度低于本地历史P20的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local historical P20 | 0-1 | Full | [0, 1] | 0.0% |
| `dryshare_gleam_smrz_le_p20_hema` | GLEAM根区土壤湿度低于本地历史P20的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local historical P20 | 0-1 | HEMA | [0, 1] | 0.0% |
| `dryshare_gleam_smrz_le_p20_hepm10` | GLEAM根区土壤湿度低于本地历史P20的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local historical P20 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `dryshare_gleam_smrz_le_p20_v3he` | GLEAM根区土壤湿度低于本地历史P20的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local historical P20 | 0-1 | V3HE | [0, 1] | 0.0% |
| `dryshare_gleam_smrz_le_p20_v3pm10` | GLEAM根区土壤湿度低于本地历史P20的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local historical P20 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `dryshare_gleam_smrz_le_p20_v3pre30` | GLEAM根区土壤湿度低于本地历史P20的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local historical P20 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `dryshare_gleam_sms_le_p10` | GLEAM表层土壤湿度低于本地历史P10的日占比 | Share of valid days with GLEAM surface soil moisture <= local historical P10 | 0-1 | Full | [0, 0.622] | 0.0% |
| `dryshare_gleam_sms_le_p10_hema` | GLEAM表层土壤湿度低于本地历史P10的日占比 | Share of valid days with GLEAM surface soil moisture <= local historical P10 | 0-1 | HEMA | [0, 0.74] | 0.0% |
| `dryshare_gleam_sms_le_p10_hepm10` | GLEAM表层土壤湿度低于本地历史P10的日占比 | Share of valid days with GLEAM surface soil moisture <= local historical P10 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `dryshare_gleam_sms_le_p10_v3he` | GLEAM表层土壤湿度低于本地历史P10的日占比 | Share of valid days with GLEAM surface soil moisture <= local historical P10 | 0-1 | V3HE | [0, 0.8033] | 0.0% |
| `dryshare_gleam_sms_le_p10_v3pm10` | GLEAM表层土壤湿度低于本地历史P10的日占比 | Share of valid days with GLEAM surface soil moisture <= local historical P10 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `dryshare_gleam_sms_le_p10_v3pre30` | GLEAM表层土壤湿度低于本地历史P10的日占比 | Share of valid days with GLEAM surface soil moisture <= local historical P10 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `dryshare_gleam_sms_le_p20` | GLEAM表层土壤湿度低于本地历史P20的日占比 | Share of valid days with GLEAM surface soil moisture <= local historical P20 | 0-1 | Full | [0, 0.8031] | 0.0% |
| `dryshare_gleam_sms_le_p20_hema` | GLEAM表层土壤湿度低于本地历史P20的日占比 | Share of valid days with GLEAM surface soil moisture <= local historical P20 | 0-1 | HEMA | [0, 0.86] | 0.0% |
| `dryshare_gleam_sms_le_p20_hepm10` | GLEAM表层土壤湿度低于本地历史P20的日占比 | Share of valid days with GLEAM surface soil moisture <= local historical P20 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `dryshare_gleam_sms_le_p20_v3he` | GLEAM表层土壤湿度低于本地历史P20的日占比 | Share of valid days with GLEAM surface soil moisture <= local historical P20 | 0-1 | V3HE | [0, 1] | 0.0% |
| `dryshare_gleam_sms_le_p20_v3pm10` | GLEAM表层土壤湿度低于本地历史P20的日占比 | Share of valid days with GLEAM surface soil moisture <= local historical P20 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `dryshare_gleam_sms_le_p20_v3pre30` | GLEAM表层土壤湿度低于本地历史P20的日占比 | Share of valid days with GLEAM surface soil moisture <= local historical P20 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `gleam_smrz_max` | GLEAM根区土壤湿度最大值 | GLEAM root-zone soil moisture max | m3/m3 | Full | [0.06779, 0.4687] | 0.0% |
| `gleam_smrz_max_hema` | GLEAM根区土壤湿度最大值 | GLEAM root-zone soil moisture max | m3/m3 | HEMA | [0.05752, 0.4671] | 0.0% |
| `gleam_smrz_max_hepm10` | GLEAM根区土壤湿度最大值 | GLEAM root-zone soil moisture max | m3/m3 | HEpm10 | [0.05631, 0.4668] | 0.0% |
| `gleam_smrz_max_v3he` | GLEAM根区土壤湿度最大值 | GLEAM root-zone soil moisture max | m3/m3 | V3HE | [0.05798, 0.4687] | 0.0% |
| `gleam_smrz_max_v3pm10` | GLEAM根区土壤湿度最大值 | GLEAM root-zone soil moisture max | m3/m3 | V3pm10 | [0.06128, 0.4571] | 0.0% |
| `gleam_smrz_max_v3pre30` | GLEAM根区土壤湿度最大值 | GLEAM root-zone soil moisture max | m3/m3 | V3pre30 | [0.06128, 0.4527] | 0.0% |
| `gleam_smrz_mean` | GLEAM根区土壤湿度均值 | GLEAM root-zone soil moisture mean | m3/m3 | Full | [0.05526, 0.4484] | 0.0% |
| `gleam_smrz_mean_hema` | GLEAM根区土壤湿度均值 | GLEAM root-zone soil moisture mean | m3/m3 | HEMA | [0.05626, 0.4528] | 0.0% |
| `gleam_smrz_mean_hepm10` | GLEAM根区土壤湿度均值 | GLEAM root-zone soil moisture mean | m3/m3 | HEpm10 | [0.05604, 0.458] | 0.0% |
| `gleam_smrz_mean_v3he` | GLEAM根区土壤湿度均值 | GLEAM root-zone soil moisture mean | m3/m3 | V3HE | [0.0554, 0.4548] | 0.0% |
| `gleam_smrz_mean_v3pm10` | GLEAM根区土壤湿度均值 | GLEAM root-zone soil moisture mean | m3/m3 | V3pm10 | [0.05472, 0.4455] | 0.0% |
| `gleam_smrz_mean_v3pre30` | GLEAM根区土壤湿度均值 | GLEAM root-zone soil moisture mean | m3/m3 | V3pre30 | [0.05369, 0.4431] | 0.0% |
| `gleam_smrz_min` | GLEAM根区土壤湿度最小值 | GLEAM root-zone soil moisture min | m3/m3 | Full | [0.05169, 0.4289] | 0.0% |
| `gleam_smrz_min_hema` | GLEAM根区土壤湿度最小值 | GLEAM root-zone soil moisture min | m3/m3 | HEMA | [0.05574, 0.4429] | 0.0% |
| `gleam_smrz_min_hepm10` | GLEAM根区土壤湿度最小值 | GLEAM root-zone soil moisture min | m3/m3 | HEpm10 | [0.05584, 0.4508] | 0.0% |
| `gleam_smrz_min_v3he` | GLEAM根区土壤湿度最小值 | GLEAM root-zone soil moisture min | m3/m3 | V3HE | [0.05307, 0.4433] | 0.0% |
| `gleam_smrz_min_v3pm10` | GLEAM根区土壤湿度最小值 | GLEAM root-zone soil moisture min | m3/m3 | V3pm10 | [0.05307, 0.4405] | 0.0% |
| `gleam_smrz_min_v3pre30` | GLEAM根区土壤湿度最小值 | GLEAM root-zone soil moisture min | m3/m3 | V3pre30 | [0.05169, 0.4326] | 0.0% |
| `gleam_smrz_sd` | GLEAM根区土壤湿度标准差 | GLEAM root-zone soil moisture std dev | m3/m3 | Full | [0.0003467, 0.1065] | 0.0% |
| `gleam_smrz_sd_hema` | GLEAM根区土壤湿度标准差 | GLEAM root-zone soil moisture std dev | m3/m3 | HEMA | [6.143e-05, 0.07996] | 0.0% |
| `gleam_smrz_sd_hepm10` | GLEAM根区土壤湿度标准差 | GLEAM root-zone soil moisture std dev | m3/m3 | HEpm10 | [4.376e-05, 0.07857] | 0.0% |
| `gleam_smrz_sd_v3he` | GLEAM根区土壤湿度标准差 | GLEAM root-zone soil moisture std dev | m3/m3 | V3HE | [0.0001631, 0.09669] | 0.0% |
| `gleam_smrz_sd_v3pm10` | GLEAM根区土壤湿度标准差 | GLEAM root-zone soil moisture std dev | m3/m3 | V3pm10 | [0.0001013, 0.04468] | 0.0% |
| `gleam_smrz_sd_v3pre30` | GLEAM根区土壤湿度标准差 | GLEAM root-zone soil moisture std dev | m3/m3 | V3pre30 | [0.0002101, 0.04372] | 0.0% |
| `gleam_sms_max` | GLEAM表层土壤湿度最大值 | GLEAM surface soil moisture max | m3/m3 | Full | [0.06167, 0.5239] | 0.0% |
| `gleam_sms_max_hema` | GLEAM表层土壤湿度最大值 | GLEAM surface soil moisture max | m3/m3 | HEMA | [0.05543, 0.5239] | 0.0% |
| `gleam_sms_max_hepm10` | GLEAM表层土壤湿度最大值 | GLEAM surface soil moisture max | m3/m3 | HEpm10 | [0.05258, 0.5239] | 0.0% |
| `gleam_sms_max_v3he` | GLEAM表层土壤湿度最大值 | GLEAM surface soil moisture max | m3/m3 | V3HE | [0.05444, 0.523] | 0.0% |
| `gleam_sms_max_v3pm10` | GLEAM表层土壤湿度最大值 | GLEAM surface soil moisture max | m3/m3 | V3pm10 | [0.04997, 0.4932] | 0.0% |
| `gleam_sms_max_v3pre30` | GLEAM表层土壤湿度最大值 | GLEAM surface soil moisture max | m3/m3 | V3pre30 | [0.05069, 0.4838] | 0.0% |
| `gleam_sms_mean` | GLEAM表层土壤湿度均值 | GLEAM surface soil moisture mean | m3/m3 | Full | [0.04949, 0.4622] | 0.0% |
| `gleam_sms_mean_hema` | GLEAM表层土壤湿度均值 | GLEAM surface soil moisture mean | m3/m3 | HEMA | [0.05211, 0.4817] | 0.0% |
| `gleam_sms_mean_hepm10` | GLEAM表层土壤湿度均值 | GLEAM surface soil moisture mean | m3/m3 | HEpm10 | [0.05074, 0.4873] | 0.0% |
| `gleam_sms_mean_v3he` | GLEAM表层土壤湿度均值 | GLEAM surface soil moisture mean | m3/m3 | V3HE | [0.04953, 0.4667] | 0.0% |
| `gleam_sms_mean_v3pm10` | GLEAM表层土壤湿度均值 | GLEAM surface soil moisture mean | m3/m3 | V3pm10 | [0.04582, 0.4553] | 0.0% |
| `gleam_sms_mean_v3pre30` | GLEAM表层土壤湿度均值 | GLEAM surface soil moisture mean | m3/m3 | V3pre30 | [0.04584, 0.4465] | 0.0% |
| `gleam_sms_min` | GLEAM表层土壤湿度最小值 | GLEAM surface soil moisture min | m3/m3 | Full | [0.04363, 0.4042] | 0.0% |
| `gleam_sms_min_hema` | GLEAM表层土壤湿度最小值 | GLEAM surface soil moisture min | m3/m3 | HEMA | [0.04904, 0.4632] | 0.0% |
| `gleam_sms_min_hepm10` | GLEAM表层土壤湿度最小值 | GLEAM surface soil moisture min | m3/m3 | HEpm10 | [0.04904, 0.4681] | 0.0% |
| `gleam_sms_min_v3he` | GLEAM表层土壤湿度最小值 | GLEAM surface soil moisture min | m3/m3 | V3HE | [0.04472, 0.4293] | 0.0% |
| `gleam_sms_min_v3pm10` | GLEAM表层土壤湿度最小值 | GLEAM surface soil moisture min | m3/m3 | V3pm10 | [0.04412, 0.4231] | 0.0% |
| `gleam_sms_min_v3pre30` | GLEAM表层土壤湿度最小值 | GLEAM surface soil moisture min | m3/m3 | V3pre30 | [0.04363, 0.4157] | 0.0% |
| `gleam_sms_sd` | GLEAM表层土壤湿度标准差 | GLEAM surface soil moisture std dev | m3/m3 | Full | [0.001928, 0.1264] | 0.0% |
| `gleam_sms_sd_hema` | GLEAM表层土壤湿度标准差 | GLEAM surface soil moisture std dev | m3/m3 | HEMA | [0.0005494, 0.0733] | 0.0% |
| `gleam_sms_sd_hepm10` | GLEAM表层土壤湿度标准差 | GLEAM surface soil moisture std dev | m3/m3 | HEpm10 | [0.000415, 0.1034] | 0.0% |
| `gleam_sms_sd_v3he` | GLEAM表层土壤湿度标准差 | GLEAM surface soil moisture std dev | m3/m3 | V3HE | [0.00129, 0.1138] | 0.0% |
| `gleam_sms_sd_v3pm10` | GLEAM表层土壤湿度标准差 | GLEAM surface soil moisture std dev | m3/m3 | V3pm10 | [0.0008525, 0.07953] | 0.0% |
| `gleam_sms_sd_v3pre30` | GLEAM表层土壤湿度标准差 | GLEAM surface soil moisture std dev | m3/m3 | V3pre30 | [0.001061, 0.07262] | 0.0% |
| `wetdays_gleam_smrz_ge_p80` | GLEAM根区土壤湿度高于本地历史P80的日数 | Days with GLEAM root-zone soil moisture >= local historical P80 | days | Full | [0, 173] | 0.0% |
| `wetdays_gleam_smrz_ge_p80_hema` | GLEAM根区土壤湿度高于本地历史P80的日数 | Days with GLEAM root-zone soil moisture >= local historical P80 | days | HEMA | [0, 113] | 0.0% |
| `wetdays_gleam_smrz_ge_p80_hepm10` | GLEAM根区土壤湿度高于本地历史P80的日数 | Days with GLEAM root-zone soil moisture >= local historical P80 | days | HEpm10 | [0, 21] | 0.0% |
| `wetdays_gleam_smrz_ge_p80_v3he` | GLEAM根区土壤湿度高于本地历史P80的日数 | Days with GLEAM root-zone soil moisture >= local historical P80 | days | V3HE | [0, 92] | 0.0% |
| `wetdays_gleam_smrz_ge_p80_v3pm10` | GLEAM根区土壤湿度高于本地历史P80的日数 | Days with GLEAM root-zone soil moisture >= local historical P80 | days | V3pm10 | [0, 21] | 0.0% |
| `wetdays_gleam_smrz_ge_p80_v3pre30` | GLEAM根区土壤湿度高于本地历史P80的日数 | Days with GLEAM root-zone soil moisture >= local historical P80 | days | V3pre30 | [0, 31] | 0.0% |
| `wetdays_gleam_smrz_ge_p90` | GLEAM根区土壤湿度高于本地历史P90的日数 | Days with GLEAM root-zone soil moisture >= local historical P90 | days | Full | [0, 141] | 0.0% |
| `wetdays_gleam_smrz_ge_p90_hema` | GLEAM根区土壤湿度高于本地历史P90的日数 | Days with GLEAM root-zone soil moisture >= local historical P90 | days | HEMA | [0, 102] | 0.0% |
| `wetdays_gleam_smrz_ge_p90_hepm10` | GLEAM根区土壤湿度高于本地历史P90的日数 | Days with GLEAM root-zone soil moisture >= local historical P90 | days | HEpm10 | [0, 21] | 0.0% |
| `wetdays_gleam_smrz_ge_p90_v3he` | GLEAM根区土壤湿度高于本地历史P90的日数 | Days with GLEAM root-zone soil moisture >= local historical P90 | days | V3HE | [0, 82] | 0.0% |
| `wetdays_gleam_smrz_ge_p90_v3pm10` | GLEAM根区土壤湿度高于本地历史P90的日数 | Days with GLEAM root-zone soil moisture >= local historical P90 | days | V3pm10 | [0, 21] | 0.0% |
| `wetdays_gleam_smrz_ge_p90_v3pre30` | GLEAM根区土壤湿度高于本地历史P90的日数 | Days with GLEAM root-zone soil moisture >= local historical P90 | days | V3pre30 | [0, 31] | 0.0% |
| `wetdays_gleam_sms_ge_p80` | GLEAM表层土壤湿度高于本地历史P80的日数 | Days with GLEAM surface soil moisture >= local historical P80 | days | Full | [0, 141] | 0.0% |
| `wetdays_gleam_sms_ge_p80_hema` | GLEAM表层土壤湿度高于本地历史P80的日数 | Days with GLEAM surface soil moisture >= local historical P80 | days | HEMA | [0, 95] | 0.0% |
| `wetdays_gleam_sms_ge_p80_hepm10` | GLEAM表层土壤湿度高于本地历史P80的日数 | Days with GLEAM surface soil moisture >= local historical P80 | days | HEpm10 | [0, 21] | 0.0% |
| `wetdays_gleam_sms_ge_p80_v3he` | GLEAM表层土壤湿度高于本地历史P80的日数 | Days with GLEAM surface soil moisture >= local historical P80 | days | V3HE | [0, 80] | 0.0% |
| `wetdays_gleam_sms_ge_p80_v3pm10` | GLEAM表层土壤湿度高于本地历史P80的日数 | Days with GLEAM surface soil moisture >= local historical P80 | days | V3pm10 | [0, 21] | 0.0% |
| `wetdays_gleam_sms_ge_p80_v3pre30` | GLEAM表层土壤湿度高于本地历史P80的日数 | Days with GLEAM surface soil moisture >= local historical P80 | days | V3pre30 | [0, 31] | 0.0% |
| `wetdays_gleam_sms_ge_p90` | GLEAM表层土壤湿度高于本地历史P90的日数 | Days with GLEAM surface soil moisture >= local historical P90 | days | Full | [0, 104] | 0.0% |
| `wetdays_gleam_sms_ge_p90_hema` | GLEAM表层土壤湿度高于本地历史P90的日数 | Days with GLEAM surface soil moisture >= local historical P90 | days | HEMA | [0, 75] | 0.0% |
| `wetdays_gleam_sms_ge_p90_hepm10` | GLEAM表层土壤湿度高于本地历史P90的日数 | Days with GLEAM surface soil moisture >= local historical P90 | days | HEpm10 | [0, 21] | 0.0% |
| `wetdays_gleam_sms_ge_p90_v3he` | GLEAM表层土壤湿度高于本地历史P90的日数 | Days with GLEAM surface soil moisture >= local historical P90 | days | V3HE | [0, 61] | 0.0% |
| `wetdays_gleam_sms_ge_p90_v3pm10` | GLEAM表层土壤湿度高于本地历史P90的日数 | Days with GLEAM surface soil moisture >= local historical P90 | days | V3pm10 | [0, 21] | 0.0% |
| `wetdays_gleam_sms_ge_p90_v3pre30` | GLEAM表层土壤湿度高于本地历史P90的日数 | Days with GLEAM surface soil moisture >= local historical P90 | days | V3pre30 | [0, 31] | 0.0% |
| `wetexcess_gleam_smrz_ge_p80` | GLEAM根区土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for GLEAM root-zone soil moisture | m3/m3 | Full | [0, 0.06339] | 0.0% |
| `wetexcess_gleam_smrz_ge_p80_hema` | GLEAM根区土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for GLEAM root-zone soil moisture | m3/m3 | HEMA | [0, 0.1476] | 0.0% |
| `wetexcess_gleam_smrz_ge_p80_hepm10` | GLEAM根区土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for GLEAM root-zone soil moisture | m3/m3 | HEpm10 | [0, 0.1153] | 0.0% |
| `wetexcess_gleam_smrz_ge_p80_v3he` | GLEAM根区土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for GLEAM root-zone soil moisture | m3/m3 | V3HE | [0, 0.0801] | 0.0% |
| `wetexcess_gleam_smrz_ge_p80_v3pm10` | GLEAM根区土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for GLEAM root-zone soil moisture | m3/m3 | V3pm10 | [0, 0.09012] | 0.0% |
| `wetexcess_gleam_smrz_ge_p80_v3pre30` | GLEAM根区土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for GLEAM root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.107] | 0.0% |
| `wetexcess_gleam_smrz_ge_p90` | GLEAM根区土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for GLEAM root-zone soil moisture | m3/m3 | Full | [0, 0.03963] | 0.0% |
| `wetexcess_gleam_smrz_ge_p90_hema` | GLEAM根区土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for GLEAM root-zone soil moisture | m3/m3 | HEMA | [0, 0.1284] | 0.0% |
| `wetexcess_gleam_smrz_ge_p90_hepm10` | GLEAM根区土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for GLEAM root-zone soil moisture | m3/m3 | HEpm10 | [0, 0.08854] | 0.0% |
| `wetexcess_gleam_smrz_ge_p90_v3he` | GLEAM根区土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for GLEAM root-zone soil moisture | m3/m3 | V3HE | [0, 0.04306] | 0.0% |
| `wetexcess_gleam_smrz_ge_p90_v3pm10` | GLEAM根区土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for GLEAM root-zone soil moisture | m3/m3 | V3pm10 | [0, 0.05914] | 0.0% |
| `wetexcess_gleam_smrz_ge_p90_v3pre30` | GLEAM根区土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for GLEAM root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.07727] | 0.0% |
| `wetexcess_gleam_sms_ge_p80` | GLEAM表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for GLEAM surface soil moisture | m3/m3 | Full | [0, 0.05532] | 0.0% |
| `wetexcess_gleam_sms_ge_p80_hema` | GLEAM表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for GLEAM surface soil moisture | m3/m3 | HEMA | [0, 0.1329] | 0.0% |
| `wetexcess_gleam_sms_ge_p80_hepm10` | GLEAM表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for GLEAM surface soil moisture | m3/m3 | HEpm10 | [0, 0.1197] | 0.0% |
| `wetexcess_gleam_sms_ge_p80_v3he` | GLEAM表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for GLEAM surface soil moisture | m3/m3 | V3HE | [0, 0.06614] | 0.0% |
| `wetexcess_gleam_sms_ge_p80_v3pm10` | GLEAM表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for GLEAM surface soil moisture | m3/m3 | V3pm10 | [0, 0.06942] | 0.0% |
| `wetexcess_gleam_sms_ge_p80_v3pre30` | GLEAM表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for GLEAM surface soil moisture | m3/m3 | V3pre30 | [0, 0.05324] | 0.0% |
| `wetexcess_gleam_sms_ge_p90` | GLEAM表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for GLEAM surface soil moisture | m3/m3 | Full | [0, 0.03746] | 0.0% |
| `wetexcess_gleam_sms_ge_p90_hema` | GLEAM表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for GLEAM surface soil moisture | m3/m3 | HEMA | [0, 0.1066] | 0.0% |
| `wetexcess_gleam_sms_ge_p90_hepm10` | GLEAM表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for GLEAM surface soil moisture | m3/m3 | HEpm10 | [0, 0.08883] | 0.0% |
| `wetexcess_gleam_sms_ge_p90_v3he` | GLEAM表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for GLEAM surface soil moisture | m3/m3 | V3HE | [0, 0.04565] | 0.0% |
| `wetexcess_gleam_sms_ge_p90_v3pm10` | GLEAM表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for GLEAM surface soil moisture | m3/m3 | V3pm10 | [0, 0.05169] | 0.0% |
| `wetexcess_gleam_sms_ge_p90_v3pre30` | GLEAM表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for GLEAM surface soil moisture | m3/m3 | V3pre30 | [0, 0.03699] | 0.0% |
| `wetshare_gleam_smrz_ge_p80` | GLEAM根区土壤湿度高于本地历史P80的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local historical P80 | 0-1 | Full | [0, 1] | 0.0% |
| `wetshare_gleam_smrz_ge_p80_hema` | GLEAM根区土壤湿度高于本地历史P80的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local historical P80 | 0-1 | HEMA | [0, 1] | 0.0% |
| `wetshare_gleam_smrz_ge_p80_hepm10` | GLEAM根区土壤湿度高于本地历史P80的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local historical P80 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `wetshare_gleam_smrz_ge_p80_v3he` | GLEAM根区土壤湿度高于本地历史P80的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local historical P80 | 0-1 | V3HE | [0, 1] | 0.0% |
| `wetshare_gleam_smrz_ge_p80_v3pm10` | GLEAM根区土壤湿度高于本地历史P80的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local historical P80 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `wetshare_gleam_smrz_ge_p80_v3pre30` | GLEAM根区土壤湿度高于本地历史P80的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local historical P80 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `wetshare_gleam_smrz_ge_p90` | GLEAM根区土壤湿度高于本地历史P90的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local historical P90 | 0-1 | Full | [0, 0.8769] | 0.0% |
| `wetshare_gleam_smrz_ge_p90_hema` | GLEAM根区土壤湿度高于本地历史P90的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local historical P90 | 0-1 | HEMA | [0, 1] | 0.0% |
| `wetshare_gleam_smrz_ge_p90_hepm10` | GLEAM根区土壤湿度高于本地历史P90的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local historical P90 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `wetshare_gleam_smrz_ge_p90_v3he` | GLEAM根区土壤湿度高于本地历史P90的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local historical P90 | 0-1 | V3HE | [0, 1] | 0.0% |
| `wetshare_gleam_smrz_ge_p90_v3pm10` | GLEAM根区土壤湿度高于本地历史P90的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local historical P90 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `wetshare_gleam_smrz_ge_p90_v3pre30` | GLEAM根区土壤湿度高于本地历史P90的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local historical P90 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `wetshare_gleam_sms_ge_p80` | GLEAM表层土壤湿度高于本地历史P80的日占比 | Share of valid days with GLEAM surface soil moisture >= local historical P80 | 0-1 | Full | [0, 0.8696] | 0.0% |
| `wetshare_gleam_sms_ge_p80_hema` | GLEAM表层土壤湿度高于本地历史P80的日占比 | Share of valid days with GLEAM surface soil moisture >= local historical P80 | 0-1 | HEMA | [0, 1] | 0.0% |
| `wetshare_gleam_sms_ge_p80_hepm10` | GLEAM表层土壤湿度高于本地历史P80的日占比 | Share of valid days with GLEAM surface soil moisture >= local historical P80 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `wetshare_gleam_sms_ge_p80_v3he` | GLEAM表层土壤湿度高于本地历史P80的日占比 | Share of valid days with GLEAM surface soil moisture >= local historical P80 | 0-1 | V3HE | [0, 1] | 0.0% |
| `wetshare_gleam_sms_ge_p80_v3pm10` | GLEAM表层土壤湿度高于本地历史P80的日占比 | Share of valid days with GLEAM surface soil moisture >= local historical P80 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `wetshare_gleam_sms_ge_p80_v3pre30` | GLEAM表层土壤湿度高于本地历史P80的日占比 | Share of valid days with GLEAM surface soil moisture >= local historical P80 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `wetshare_gleam_sms_ge_p90` | GLEAM表层土壤湿度高于本地历史P90的日占比 | Share of valid days with GLEAM surface soil moisture >= local historical P90 | 0-1 | Full | [0, 0.6957] | 0.0% |
| `wetshare_gleam_sms_ge_p90_hema` | GLEAM表层土壤湿度高于本地历史P90的日占比 | Share of valid days with GLEAM surface soil moisture >= local historical P90 | 0-1 | HEMA | [0, 1] | 0.0% |
| `wetshare_gleam_sms_ge_p90_hepm10` | GLEAM表层土壤湿度高于本地历史P90的日占比 | Share of valid days with GLEAM surface soil moisture >= local historical P90 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `wetshare_gleam_sms_ge_p90_v3he` | GLEAM表层土壤湿度高于本地历史P90的日占比 | Share of valid days with GLEAM surface soil moisture >= local historical P90 | 0-1 | V3HE | [0, 0.7922] | 0.0% |
| `wetshare_gleam_sms_ge_p90_v3pm10` | GLEAM表层土壤湿度高于本地历史P90的日占比 | Share of valid days with GLEAM surface soil moisture >= local historical P90 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `wetshare_gleam_sms_ge_p90_v3pre30` | GLEAM表层土壤湿度高于本地历史P90的日占比 | Share of valid days with GLEAM surface soil moisture >= local historical P90 | 0-1 | V3pre30 | [0, 1] | 0.0% |

### legacy pooled-state

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `drydeficit_pl_gleam_smrz_le_p25` | GLEAM根区土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for GLEAM root-zone soil moisture | m3/m3 | Full | [0, 0.1053] | 0.0% |
| `drydeficit_pl_gleam_smrz_le_p25_hema` | GLEAM根区土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for GLEAM root-zone soil moisture | m3/m3 | HEMA | [0, 0.1886] | 0.0% |
| `drydeficit_pl_gleam_smrz_le_p25_hepm10` | GLEAM根区土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for GLEAM root-zone soil moisture | m3/m3 | HEpm10 | [0, 0.1316] | 0.0% |
| `drydeficit_pl_gleam_smrz_le_p25_v3he` | GLEAM根区土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for GLEAM root-zone soil moisture | m3/m3 | V3HE | [0, 0.08546] | 0.0% |
| `drydeficit_pl_gleam_smrz_le_p25_v3pm10` | GLEAM根区土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for GLEAM root-zone soil moisture | m3/m3 | V3pm10 | [0, 0.07647] | 0.0% |
| `drydeficit_pl_gleam_smrz_le_p25_v3pre30` | GLEAM根区土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for GLEAM root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.07772] | 0.0% |
| `drydeficit_pl_gleam_sms_le_p25` | GLEAM表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for GLEAM surface soil moisture | m3/m3 | Full | [0, 0.1102] | 0.0% |
| `drydeficit_pl_gleam_sms_le_p25_hema` | GLEAM表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for GLEAM surface soil moisture | m3/m3 | HEMA | [0, 0.1979] | 0.0% |
| `drydeficit_pl_gleam_sms_le_p25_hepm10` | GLEAM表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for GLEAM surface soil moisture | m3/m3 | HEpm10 | [0, 0.1532] | 0.0% |
| `drydeficit_pl_gleam_sms_le_p25_v3he` | GLEAM表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for GLEAM surface soil moisture | m3/m3 | V3HE | [0, 0.101] | 0.0% |
| `drydeficit_pl_gleam_sms_le_p25_v3pm10` | GLEAM表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for GLEAM surface soil moisture | m3/m3 | V3pm10 | [0, 0.07294] | 0.0% |
| `drydeficit_pl_gleam_sms_le_p25_v3pre30` | GLEAM表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for GLEAM surface soil moisture | m3/m3 | V3pre30 | [0, 0.06485] | 0.0% |
| `dryshare_pl_gleam_smrz_le_p25` | GLEAM根区土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with GLEAM root-zone soil moisture <= pooled window-specific threshold P25 | 0-1 | Full | [0, 1] | 0.0% |
| `dryshare_pl_gleam_smrz_le_p25_hema` | GLEAM根区土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with GLEAM root-zone soil moisture <= pooled window-specific threshold P25 | 0-1 | HEMA | [0, 1] | 0.0% |
| `dryshare_pl_gleam_smrz_le_p25_hepm10` | GLEAM根区土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with GLEAM root-zone soil moisture <= pooled window-specific threshold P25 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `dryshare_pl_gleam_smrz_le_p25_v3he` | GLEAM根区土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with GLEAM root-zone soil moisture <= pooled window-specific threshold P25 | 0-1 | V3HE | [0, 1] | 0.0% |
| `dryshare_pl_gleam_smrz_le_p25_v3pm10` | GLEAM根区土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with GLEAM root-zone soil moisture <= pooled window-specific threshold P25 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `dryshare_pl_gleam_smrz_le_p25_v3pre30` | GLEAM根区土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with GLEAM root-zone soil moisture <= pooled window-specific threshold P25 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `dryshare_pl_gleam_sms_le_p25` | GLEAM表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with GLEAM surface soil moisture <= pooled window-specific threshold P25 | 0-1 | Full | [0, 1] | 0.0% |
| `dryshare_pl_gleam_sms_le_p25_hema` | GLEAM表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with GLEAM surface soil moisture <= pooled window-specific threshold P25 | 0-1 | HEMA | [0, 1] | 0.0% |
| `dryshare_pl_gleam_sms_le_p25_hepm10` | GLEAM表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with GLEAM surface soil moisture <= pooled window-specific threshold P25 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `dryshare_pl_gleam_sms_le_p25_v3he` | GLEAM表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with GLEAM surface soil moisture <= pooled window-specific threshold P25 | 0-1 | V3HE | [0, 1] | 0.0% |
| `dryshare_pl_gleam_sms_le_p25_v3pm10` | GLEAM表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with GLEAM surface soil moisture <= pooled window-specific threshold P25 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `dryshare_pl_gleam_sms_le_p25_v3pre30` | GLEAM表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with GLEAM surface soil moisture <= pooled window-specific threshold P25 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `wetexcess_pl_gleam_smrz_ge_p75` | GLEAM根区土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for GLEAM root-zone soil moisture | m3/m3 | Full | [0, 0.07291] | 0.0% |
| `wetexcess_pl_gleam_smrz_ge_p75_hema` | GLEAM根区土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for GLEAM root-zone soil moisture | m3/m3 | HEMA | [0, 0.06587] | 0.0% |
| `wetexcess_pl_gleam_smrz_ge_p75_hepm10` | GLEAM根区土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for GLEAM root-zone soil moisture | m3/m3 | HEpm10 | [0, 0.07778] | 0.0% |
| `wetexcess_pl_gleam_smrz_ge_p75_v3he` | GLEAM根区土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for GLEAM root-zone soil moisture | m3/m3 | V3HE | [0, 0.08233] | 0.0% |
| `wetexcess_pl_gleam_smrz_ge_p75_v3pm10` | GLEAM根区土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for GLEAM root-zone soil moisture | m3/m3 | V3pm10 | [0, 0.08576] | 0.0% |
| `wetexcess_pl_gleam_smrz_ge_p75_v3pre30` | GLEAM根区土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for GLEAM root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.08769] | 0.0% |
| `wetexcess_pl_gleam_sms_ge_p75` | GLEAM表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for GLEAM surface soil moisture | m3/m3 | Full | [0, 0.09442] | 0.0% |
| `wetexcess_pl_gleam_sms_ge_p75_hema` | GLEAM表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for GLEAM surface soil moisture | m3/m3 | HEMA | [0, 0.08432] | 0.0% |
| `wetexcess_pl_gleam_sms_ge_p75_hepm10` | GLEAM表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for GLEAM surface soil moisture | m3/m3 | HEpm10 | [0, 0.1031] | 0.0% |
| `wetexcess_pl_gleam_sms_ge_p75_v3he` | GLEAM表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for GLEAM surface soil moisture | m3/m3 | V3HE | [0, 0.1054] | 0.0% |
| `wetexcess_pl_gleam_sms_ge_p75_v3pm10` | GLEAM表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for GLEAM surface soil moisture | m3/m3 | V3pm10 | [0, 0.1478] | 0.0% |
| `wetexcess_pl_gleam_sms_ge_p75_v3pre30` | GLEAM表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for GLEAM surface soil moisture | m3/m3 | V3pre30 | [0, 0.1671] | 0.0% |
| `wetshare_pl_gleam_smrz_ge_p75` | GLEAM根区土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with GLEAM root-zone soil moisture >= pooled window-specific threshold P75 | 0-1 | Full | [0, 1] | 0.0% |
| `wetshare_pl_gleam_smrz_ge_p75_hema` | GLEAM根区土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with GLEAM root-zone soil moisture >= pooled window-specific threshold P75 | 0-1 | HEMA | [0, 1] | 0.0% |
| `wetshare_pl_gleam_smrz_ge_p75_hepm10` | GLEAM根区土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with GLEAM root-zone soil moisture >= pooled window-specific threshold P75 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `wetshare_pl_gleam_smrz_ge_p75_v3he` | GLEAM根区土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with GLEAM root-zone soil moisture >= pooled window-specific threshold P75 | 0-1 | V3HE | [0, 1] | 0.0% |
| `wetshare_pl_gleam_smrz_ge_p75_v3pm10` | GLEAM根区土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with GLEAM root-zone soil moisture >= pooled window-specific threshold P75 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `wetshare_pl_gleam_smrz_ge_p75_v3pre30` | GLEAM根区土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with GLEAM root-zone soil moisture >= pooled window-specific threshold P75 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `wetshare_pl_gleam_sms_ge_p75` | GLEAM表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with GLEAM surface soil moisture >= pooled window-specific threshold P75 | 0-1 | Full | [0, 1] | 0.0% |
| `wetshare_pl_gleam_sms_ge_p75_hema` | GLEAM表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with GLEAM surface soil moisture >= pooled window-specific threshold P75 | 0-1 | HEMA | [0, 1] | 0.0% |
| `wetshare_pl_gleam_sms_ge_p75_hepm10` | GLEAM表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with GLEAM surface soil moisture >= pooled window-specific threshold P75 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `wetshare_pl_gleam_sms_ge_p75_v3he` | GLEAM表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with GLEAM surface soil moisture >= pooled window-specific threshold P75 | 0-1 | V3HE | [0, 1] | 0.0% |
| `wetshare_pl_gleam_sms_ge_p75_v3pm10` | GLEAM表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with GLEAM surface soil moisture >= pooled window-specific threshold P75 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `wetshare_pl_gleam_sms_ge_p75_v3pre30` | GLEAM表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with GLEAM surface soil moisture >= pooled window-specific threshold P75 | 0-1 | V3pre30 | [0, 1] | 0.0% |

### legacy maize-zone-state

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `drydeficit_mz_gleam_smrz_le_p25` | GLEAM根区土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for GLEAM root-zone soil moisture | m3/m3 | Full | [0, 0.1803] | 0.0% |
| `drydeficit_mz_gleam_smrz_le_p25_hema` | GLEAM根区土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for GLEAM root-zone soil moisture | m3/m3 | HEMA | [0, 0.1811] | 0.0% |
| `drydeficit_mz_gleam_smrz_le_p25_hepm10` | GLEAM根区土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for GLEAM root-zone soil moisture | m3/m3 | HEpm10 | [0, 0.2149] | 0.0% |
| `drydeficit_mz_gleam_smrz_le_p25_v3he` | GLEAM根区土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for GLEAM root-zone soil moisture | m3/m3 | V3HE | [0, 0.1794] | 0.0% |
| `drydeficit_mz_gleam_smrz_le_p25_v3pm10` | GLEAM根区土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for GLEAM root-zone soil moisture | m3/m3 | V3pm10 | [0, 0.179] | 0.0% |
| `drydeficit_mz_gleam_smrz_le_p25_v3pre30` | GLEAM根区土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for GLEAM root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.1717] | 0.0% |
| `drydeficit_mz_gleam_sms_le_p25` | GLEAM表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for GLEAM surface soil moisture | m3/m3 | Full | [0, 0.1556] | 0.0% |
| `drydeficit_mz_gleam_sms_le_p25_hema` | GLEAM表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for GLEAM surface soil moisture | m3/m3 | HEMA | [0, 0.1654] | 0.0% |
| `drydeficit_mz_gleam_sms_le_p25_hepm10` | GLEAM表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for GLEAM surface soil moisture | m3/m3 | HEpm10 | [0, 0.1883] | 0.0% |
| `drydeficit_mz_gleam_sms_le_p25_v3he` | GLEAM表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for GLEAM surface soil moisture | m3/m3 | V3HE | [0, 0.1833] | 0.0% |
| `drydeficit_mz_gleam_sms_le_p25_v3pm10` | GLEAM表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for GLEAM surface soil moisture | m3/m3 | V3pm10 | [0, 0.1321] | 0.0% |
| `drydeficit_mz_gleam_sms_le_p25_v3pre30` | GLEAM表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for GLEAM surface soil moisture | m3/m3 | V3pre30 | [0, 0.1223] | 0.0% |
| `dryshare_mz_gleam_smrz_le_p25` | GLEAM根区土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with GLEAM root-zone soil moisture <= maize-zone-specific threshold P25 | 0-1 | Full | [0, 1] | 0.0% |
| `dryshare_mz_gleam_smrz_le_p25_hema` | GLEAM根区土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with GLEAM root-zone soil moisture <= maize-zone-specific threshold P25 | 0-1 | HEMA | [0, 1] | 0.0% |
| `dryshare_mz_gleam_smrz_le_p25_hepm10` | GLEAM根区土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with GLEAM root-zone soil moisture <= maize-zone-specific threshold P25 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `dryshare_mz_gleam_smrz_le_p25_v3he` | GLEAM根区土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with GLEAM root-zone soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3HE | [0, 1] | 0.0% |
| `dryshare_mz_gleam_smrz_le_p25_v3pm10` | GLEAM根区土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with GLEAM root-zone soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `dryshare_mz_gleam_smrz_le_p25_v3pre30` | GLEAM根区土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with GLEAM root-zone soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `dryshare_mz_gleam_sms_le_p25` | GLEAM表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with GLEAM surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | Full | [0, 1] | 0.0% |
| `dryshare_mz_gleam_sms_le_p25_hema` | GLEAM表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with GLEAM surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | HEMA | [0, 1] | 0.0% |
| `dryshare_mz_gleam_sms_le_p25_hepm10` | GLEAM表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with GLEAM surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `dryshare_mz_gleam_sms_le_p25_v3he` | GLEAM表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with GLEAM surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3HE | [0, 1] | 0.0% |
| `dryshare_mz_gleam_sms_le_p25_v3pm10` | GLEAM表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with GLEAM surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `dryshare_mz_gleam_sms_le_p25_v3pre30` | GLEAM表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with GLEAM surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `wetexcess_mz_gleam_smrz_ge_p75` | GLEAM根区土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for GLEAM root-zone soil moisture | m3/m3 | Full | [0, 0.216] | 0.0% |
| `wetexcess_mz_gleam_smrz_ge_p75_hema` | GLEAM根区土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for GLEAM root-zone soil moisture | m3/m3 | HEMA | [0, 0.1985] | 0.0% |
| `wetexcess_mz_gleam_smrz_ge_p75_hepm10` | GLEAM根区土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for GLEAM root-zone soil moisture | m3/m3 | HEpm10 | [0, 0.2106] | 0.0% |
| `wetexcess_mz_gleam_smrz_ge_p75_v3he` | GLEAM根区土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for GLEAM root-zone soil moisture | m3/m3 | V3HE | [0, 0.2338] | 0.0% |
| `wetexcess_mz_gleam_smrz_ge_p75_v3pm10` | GLEAM根区土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for GLEAM root-zone soil moisture | m3/m3 | V3pm10 | [0, 0.2156] | 0.0% |
| `wetexcess_mz_gleam_smrz_ge_p75_v3pre30` | GLEAM根区土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for GLEAM root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.2127] | 0.0% |
| `wetexcess_mz_gleam_sms_ge_p75` | GLEAM表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for GLEAM surface soil moisture | m3/m3 | Full | [0, 0.2264] | 0.0% |
| `wetexcess_mz_gleam_sms_ge_p75_hema` | GLEAM表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for GLEAM surface soil moisture | m3/m3 | HEMA | [0, 0.1986] | 0.0% |
| `wetexcess_mz_gleam_sms_ge_p75_hepm10` | GLEAM表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for GLEAM surface soil moisture | m3/m3 | HEpm10 | [0, 0.2187] | 0.0% |
| `wetexcess_mz_gleam_sms_ge_p75_v3he` | GLEAM表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for GLEAM surface soil moisture | m3/m3 | V3HE | [0, 0.2429] | 0.0% |
| `wetexcess_mz_gleam_sms_ge_p75_v3pm10` | GLEAM表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for GLEAM surface soil moisture | m3/m3 | V3pm10 | [0, 0.2422] | 0.0% |
| `wetexcess_mz_gleam_sms_ge_p75_v3pre30` | GLEAM表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for GLEAM surface soil moisture | m3/m3 | V3pre30 | [0, 0.2263] | 0.0% |
| `wetshare_mz_gleam_smrz_ge_p75` | GLEAM根区土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with GLEAM root-zone soil moisture >= maize-zone-specific threshold P75 | 0-1 | Full | [0, 1] | 0.0% |
| `wetshare_mz_gleam_smrz_ge_p75_hema` | GLEAM根区土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with GLEAM root-zone soil moisture >= maize-zone-specific threshold P75 | 0-1 | HEMA | [0, 1] | 0.0% |
| `wetshare_mz_gleam_smrz_ge_p75_hepm10` | GLEAM根区土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with GLEAM root-zone soil moisture >= maize-zone-specific threshold P75 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `wetshare_mz_gleam_smrz_ge_p75_v3he` | GLEAM根区土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with GLEAM root-zone soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3HE | [0, 1] | 0.0% |
| `wetshare_mz_gleam_smrz_ge_p75_v3pm10` | GLEAM根区土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with GLEAM root-zone soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `wetshare_mz_gleam_smrz_ge_p75_v3pre30` | GLEAM根区土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with GLEAM root-zone soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `wetshare_mz_gleam_sms_ge_p75` | GLEAM表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with GLEAM surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | Full | [0, 1] | 0.0% |
| `wetshare_mz_gleam_sms_ge_p75_hema` | GLEAM表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with GLEAM surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | HEMA | [0, 1] | 0.0% |
| `wetshare_mz_gleam_sms_ge_p75_hepm10` | GLEAM表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with GLEAM surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `wetshare_mz_gleam_sms_ge_p75_v3he` | GLEAM表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with GLEAM surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3HE | [0, 1] | 0.0% |
| `wetshare_mz_gleam_sms_ge_p75_v3pm10` | GLEAM表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with GLEAM surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `wetshare_mz_gleam_sms_ge_p75_v3pre30` | GLEAM表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with GLEAM surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3pre30 | [0, 1] | 0.0% |

### md-event family

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `mdduration_dry_gleam_smrz_fullnew` | GLEAM根区土壤湿度干旱事件持续期总和 | Season-total duration of dry events for GLEAM root-zone soil moisture | days | FullNew | [0, 150] | 0.0% |
| `mdduration_dry_gleam_smrz_hema` | GLEAM根区土壤湿度干旱事件持续期总和 | Season-total duration of dry events for GLEAM root-zone soil moisture | days | HEMA | [0, 100] | 0.0% |
| `mdduration_dry_gleam_smrz_v3he` | GLEAM根区土壤湿度干旱事件持续期总和 | Season-total duration of dry events for GLEAM root-zone soil moisture | days | V3HE | [0, 97] | 0.0% |
| `mdduration_dry_gleam_smrz_v3pre30` | GLEAM根区土壤湿度干旱事件持续期总和 | Season-total duration of dry events for GLEAM root-zone soil moisture | days | V3pre30 | [0, 27] | 0.0% |
| `mdduration_dry_gleam_sms_fullnew` | GLEAM表层土壤湿度干旱事件持续期总和 | Season-total duration of dry events for GLEAM surface soil moisture | days | FullNew | [0, 135] | 0.0% |
| `mdduration_dry_gleam_sms_hema` | GLEAM表层土壤湿度干旱事件持续期总和 | Season-total duration of dry events for GLEAM surface soil moisture | days | HEMA | [0, 104] | 0.0% |
| `mdduration_dry_gleam_sms_v3he` | GLEAM表层土壤湿度干旱事件持续期总和 | Season-total duration of dry events for GLEAM surface soil moisture | days | V3HE | [0, 84] | 0.0% |
| `mdduration_dry_gleam_sms_v3pre30` | GLEAM表层土壤湿度干旱事件持续期总和 | Season-total duration of dry events for GLEAM surface soil moisture | days | V3pre30 | [0, 27] | 0.0% |
| `mdduration_wet_gleam_smrz_fullnew` | GLEAM根区土壤湿度过湿事件持续期总和 | Season-total duration of wet events for GLEAM root-zone soil moisture | days | FullNew | [0, 172] | 0.0% |
| `mdduration_wet_gleam_smrz_hema` | GLEAM根区土壤湿度过湿事件持续期总和 | Season-total duration of wet events for GLEAM root-zone soil moisture | days | HEMA | [0, 110] | 0.0% |
| `mdduration_wet_gleam_smrz_v3he` | GLEAM根区土壤湿度过湿事件持续期总和 | Season-total duration of wet events for GLEAM root-zone soil moisture | days | V3HE | [0, 94] | 0.0% |
| `mdduration_wet_gleam_smrz_v3pre30` | GLEAM根区土壤湿度过湿事件持续期总和 | Season-total duration of wet events for GLEAM root-zone soil moisture | days | V3pre30 | [0, 27] | 0.0% |
| `mdduration_wet_gleam_sms_fullnew` | GLEAM表层土壤湿度过湿事件持续期总和 | Season-total duration of wet events for GLEAM surface soil moisture | days | FullNew | [0, 183] | 0.0% |
| `mdduration_wet_gleam_sms_hema` | GLEAM表层土壤湿度过湿事件持续期总和 | Season-total duration of wet events for GLEAM surface soil moisture | days | HEMA | [0, 91] | 0.0% |
| `mdduration_wet_gleam_sms_v3he` | GLEAM表层土壤湿度过湿事件持续期总和 | Season-total duration of wet events for GLEAM surface soil moisture | days | V3HE | [0, 99] | 0.0% |
| `mdduration_wet_gleam_sms_v3pre30` | GLEAM表层土壤湿度过湿事件持续期总和 | Season-total duration of wet events for GLEAM surface soil moisture | days | V3pre30 | [0, 27] | 0.0% |
| `mddurshare_dry_gleam_smrz_fullnew` | GLEAM根区土壤湿度干旱事件持续期占比 | Share of season days in dry events for GLEAM root-zone soil moisture | 0-1 | FullNew | [0, 0.8571] | 0.0% |
| `mddurshare_dry_gleam_smrz_hema` | GLEAM根区土壤湿度干旱事件持续期占比 | Share of season days in dry events for GLEAM root-zone soil moisture | 0-1 | HEMA | [0, 0.9565] | 0.0% |
| `mddurshare_dry_gleam_smrz_v3he` | GLEAM根区土壤湿度干旱事件持续期占比 | Share of season days in dry events for GLEAM root-zone soil moisture | 0-1 | V3HE | [0, 0.9556] | 0.0% |
| `mddurshare_dry_gleam_smrz_v3pre30` | GLEAM根区土壤湿度干旱事件持续期占比 | Share of season days in dry events for GLEAM root-zone soil moisture | 0-1 | V3pre30 | [0, 0.871] | 0.0% |
| `mddurshare_dry_gleam_sms_fullnew` | GLEAM表层土壤湿度干旱事件持续期占比 | Share of season days in dry events for GLEAM surface soil moisture | 0-1 | FullNew | [0, 0.8793] | 0.0% |
| `mddurshare_dry_gleam_sms_hema` | GLEAM表层土壤湿度干旱事件持续期占比 | Share of season days in dry events for GLEAM surface soil moisture | 0-1 | HEMA | [0, 0.9583] | 0.0% |
| `mddurshare_dry_gleam_sms_v3he` | GLEAM表层土壤湿度干旱事件持续期占比 | Share of season days in dry events for GLEAM surface soil moisture | 0-1 | V3HE | [0, 0.9518] | 0.0% |
| `mddurshare_dry_gleam_sms_v3pre30` | GLEAM表层土壤湿度干旱事件持续期占比 | Share of season days in dry events for GLEAM surface soil moisture | 0-1 | V3pre30 | [0, 0.871] | 0.0% |
| `mddurshare_wet_gleam_smrz_fullnew` | GLEAM根区土壤湿度过湿事件持续期占比 | Share of season days in wet events for GLEAM root-zone soil moisture | 0-1 | FullNew | [0, 0.9149] | 0.0% |
| `mddurshare_wet_gleam_smrz_hema` | GLEAM根区土壤湿度过湿事件持续期占比 | Share of season days in wet events for GLEAM root-zone soil moisture | 0-1 | HEMA | [0, 0.9649] | 0.0% |
| `mddurshare_wet_gleam_smrz_v3he` | GLEAM根区土壤湿度过湿事件持续期占比 | Share of season days in wet events for GLEAM root-zone soil moisture | 0-1 | V3HE | [0, 0.9592] | 0.0% |
| `mddurshare_wet_gleam_smrz_v3pre30` | GLEAM根区土壤湿度过湿事件持续期占比 | Share of season days in wet events for GLEAM root-zone soil moisture | 0-1 | V3pre30 | [0, 0.871] | 0.0% |
| `mddurshare_wet_gleam_sms_fullnew` | GLEAM表层土壤湿度过湿事件持续期占比 | Share of season days in wet events for GLEAM surface soil moisture | 0-1 | FullNew | [0, 0.9305] | 0.0% |
| `mddurshare_wet_gleam_sms_hema` | GLEAM表层土壤湿度过湿事件持续期占比 | Share of season days in wet events for GLEAM surface soil moisture | 0-1 | HEMA | [0, 0.9574] | 0.0% |
| `mddurshare_wet_gleam_sms_v3he` | GLEAM表层土壤湿度过湿事件持续期占比 | Share of season days in wet events for GLEAM surface soil moisture | 0-1 | V3HE | [0, 0.9612] | 0.0% |
| `mddurshare_wet_gleam_sms_v3pre30` | GLEAM表层土壤湿度过湿事件持续期占比 | Share of season days in wet events for GLEAM surface soil moisture | 0-1 | V3pre30 | [0, 0.871] | 0.0% |
| `mdseverity_dry_gleam_smrz_fullnew` | GLEAM根区土壤湿度干旱事件严重度总和 | Season-total event severity for dry events in GLEAM root-zone soil moisture | percentile-points | FullNew | [0, 2676] | 0.0% |
| `mdseverity_dry_gleam_smrz_hema` | GLEAM根区土壤湿度干旱事件严重度总和 | Season-total event severity for dry events in GLEAM root-zone soil moisture | percentile-points | HEMA | [0, 1861] | 0.0% |
| `mdseverity_dry_gleam_smrz_v3he` | GLEAM根区土壤湿度干旱事件严重度总和 | Season-total event severity for dry events in GLEAM root-zone soil moisture | percentile-points | V3HE | [0, 2019] | 0.0% |
| `mdseverity_dry_gleam_smrz_v3pre30` | GLEAM根区土壤湿度干旱事件严重度总和 | Season-total event severity for dry events in GLEAM root-zone soil moisture | percentile-points | V3pre30 | [0, 833.1] | 0.0% |
| `mdseverity_dry_gleam_sms_fullnew` | GLEAM表层土壤湿度干旱事件严重度总和 | Season-total event severity for dry events in GLEAM surface soil moisture | percentile-points | FullNew | [0, 2767] | 0.0% |
| `mdseverity_dry_gleam_sms_hema` | GLEAM表层土壤湿度干旱事件严重度总和 | Season-total event severity for dry events in GLEAM surface soil moisture | percentile-points | HEMA | [0, 2084] | 0.0% |
| `mdseverity_dry_gleam_sms_v3he` | GLEAM表层土壤湿度干旱事件严重度总和 | Season-total event severity for dry events in GLEAM surface soil moisture | percentile-points | V3HE | [0, 1726] | 0.0% |
| `mdseverity_dry_gleam_sms_v3pre30` | GLEAM表层土壤湿度干旱事件严重度总和 | Season-total event severity for dry events in GLEAM surface soil moisture | percentile-points | V3pre30 | [0, 779.1] | 0.0% |
| `mdseverity_wet_gleam_smrz_fullnew` | GLEAM根区土壤湿度过湿事件严重度总和 | Season-total event severity for wet events in GLEAM root-zone soil moisture | percentile-points | FullNew | [0, 3918] | 0.0% |
| `mdseverity_wet_gleam_smrz_hema` | GLEAM根区土壤湿度过湿事件严重度总和 | Season-total event severity for wet events in GLEAM root-zone soil moisture | percentile-points | HEMA | [0, 2712] | 0.0% |
| `mdseverity_wet_gleam_smrz_v3he` | GLEAM根区土壤湿度过湿事件严重度总和 | Season-total event severity for wet events in GLEAM root-zone soil moisture | percentile-points | V3HE | [0, 2288] | 0.0% |
| `mdseverity_wet_gleam_smrz_v3pre30` | GLEAM根区土壤湿度过湿事件严重度总和 | Season-total event severity for wet events in GLEAM root-zone soil moisture | percentile-points | V3pre30 | [0, 839.5] | 0.0% |
| `mdseverity_wet_gleam_sms_fullnew` | GLEAM表层土壤湿度过湿事件严重度总和 | Season-total event severity for wet events in GLEAM surface soil moisture | percentile-points | FullNew | [0, 3230] | 0.0% |
| `mdseverity_wet_gleam_sms_hema` | GLEAM表层土壤湿度过湿事件严重度总和 | Season-total event severity for wet events in GLEAM surface soil moisture | percentile-points | HEMA | [0, 2049] | 0.0% |
| `mdseverity_wet_gleam_sms_v3he` | GLEAM表层土壤湿度过湿事件严重度总和 | Season-total event severity for wet events in GLEAM surface soil moisture | percentile-points | V3HE | [0, 2043] | 0.0% |
| `mdseverity_wet_gleam_sms_v3pre30` | GLEAM表层土壤湿度过湿事件严重度总和 | Season-total event severity for wet events in GLEAM surface soil moisture | percentile-points | V3pre30 | [0, 847.4] | 0.0% |

### window-baseline family

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `blduration_dry_gleam_smrz_p10_fullnew` | GLEAM根区土壤湿度低于本地窗口P10的日数 | Days with GLEAM root-zone soil moisture <= local window-specific P10 | days | FullNew | [0, 125] | 0.0% |
| `blduration_dry_gleam_smrz_p10_hema` | GLEAM根区土壤湿度低于本地窗口P10的日数 | Days with GLEAM root-zone soil moisture <= local window-specific P10 | days | HEMA | [0, 52] | 0.0% |
| `blduration_dry_gleam_smrz_p10_v3he` | GLEAM根区土壤湿度低于本地窗口P10的日数 | Days with GLEAM root-zone soil moisture <= local window-specific P10 | days | V3HE | [0, 61] | 0.0% |
| `blduration_dry_gleam_smrz_p10_v3pre30` | GLEAM根区土壤湿度低于本地窗口P10的日数 | Days with GLEAM root-zone soil moisture <= local window-specific P10 | days | V3pre30 | [0, 22] | 0.0% |
| `blduration_dry_gleam_smrz_p20_fullnew` | GLEAM根区土壤湿度低于本地窗口P20的日数 | Days with GLEAM root-zone soil moisture <= local window-specific P20 | days | FullNew | [0, 181] | 0.0% |
| `blduration_dry_gleam_smrz_p20_hema` | GLEAM根区土壤湿度低于本地窗口P20的日数 | Days with GLEAM root-zone soil moisture <= local window-specific P20 | days | HEMA | [0, 86] | 0.0% |
| `blduration_dry_gleam_smrz_p20_v3he` | GLEAM根区土壤湿度低于本地窗口P20的日数 | Days with GLEAM root-zone soil moisture <= local window-specific P20 | days | V3HE | [0, 93] | 0.0% |
| `blduration_dry_gleam_smrz_p20_v3pre30` | GLEAM根区土壤湿度低于本地窗口P20的日数 | Days with GLEAM root-zone soil moisture <= local window-specific P20 | days | V3pre30 | [0, 31] | 0.0% |
| `blduration_dry_gleam_sms_p10_fullnew` | GLEAM表层土壤湿度低于本地窗口P10的日数 | Days with GLEAM surface soil moisture <= local window-specific P10 | days | FullNew | [0, 91] | 0.0% |
| `blduration_dry_gleam_sms_p10_hema` | GLEAM表层土壤湿度低于本地窗口P10的日数 | Days with GLEAM surface soil moisture <= local window-specific P10 | days | HEMA | [0, 55] | 0.0% |
| `blduration_dry_gleam_sms_p10_v3he` | GLEAM表层土壤湿度低于本地窗口P10的日数 | Days with GLEAM surface soil moisture <= local window-specific P10 | days | V3HE | [0, 42] | 0.0% |
| `blduration_dry_gleam_sms_p10_v3pre30` | GLEAM表层土壤湿度低于本地窗口P10的日数 | Days with GLEAM surface soil moisture <= local window-specific P10 | days | V3pre30 | [0, 22] | 0.0% |
| `blduration_dry_gleam_sms_p20_fullnew` | GLEAM表层土壤湿度低于本地窗口P20的日数 | Days with GLEAM surface soil moisture <= local window-specific P20 | days | FullNew | [0, 147] | 0.0% |
| `blduration_dry_gleam_sms_p20_hema` | GLEAM表层土壤湿度低于本地窗口P20的日数 | Days with GLEAM surface soil moisture <= local window-specific P20 | days | HEMA | [0, 83] | 0.0% |
| `blduration_dry_gleam_sms_p20_v3he` | GLEAM表层土壤湿度低于本地窗口P20的日数 | Days with GLEAM surface soil moisture <= local window-specific P20 | days | V3HE | [0, 60] | 0.0% |
| `blduration_dry_gleam_sms_p20_v3pre30` | GLEAM表层土壤湿度低于本地窗口P20的日数 | Days with GLEAM surface soil moisture <= local window-specific P20 | days | V3pre30 | [0, 31] | 0.0% |
| `blduration_wet_gleam_smrz_p80_fullnew` | GLEAM根区土壤湿度高于本地窗口P80的日数 | Days with GLEAM root-zone soil moisture >= local window-specific P80 | days | FullNew | [0, 190] | 0.0% |
| `blduration_wet_gleam_smrz_p80_hema` | GLEAM根区土壤湿度高于本地窗口P80的日数 | Days with GLEAM root-zone soil moisture >= local window-specific P80 | days | HEMA | [0, 100] | 0.0% |
| `blduration_wet_gleam_smrz_p80_v3he` | GLEAM根区土壤湿度高于本地窗口P80的日数 | Days with GLEAM root-zone soil moisture >= local window-specific P80 | days | V3HE | [0, 98] | 0.0% |
| `blduration_wet_gleam_smrz_p80_v3pre30` | GLEAM根区土壤湿度高于本地窗口P80的日数 | Days with GLEAM root-zone soil moisture >= local window-specific P80 | days | V3pre30 | [0, 31] | 0.0% |
| `blduration_wet_gleam_smrz_p90_fullnew` | GLEAM根区土壤湿度高于本地窗口P90的日数 | Days with GLEAM root-zone soil moisture >= local window-specific P90 | days | FullNew | [0, 129] | 0.0% |
| `blduration_wet_gleam_smrz_p90_hema` | GLEAM根区土壤湿度高于本地窗口P90的日数 | Days with GLEAM root-zone soil moisture >= local window-specific P90 | days | HEMA | [0, 63] | 0.0% |
| `blduration_wet_gleam_smrz_p90_v3he` | GLEAM根区土壤湿度高于本地窗口P90的日数 | Days with GLEAM root-zone soil moisture >= local window-specific P90 | days | V3HE | [0, 67] | 0.0% |
| `blduration_wet_gleam_smrz_p90_v3pre30` | GLEAM根区土壤湿度高于本地窗口P90的日数 | Days with GLEAM root-zone soil moisture >= local window-specific P90 | days | V3pre30 | [0, 22] | 0.0% |
| `blduration_wet_gleam_sms_p80_fullnew` | GLEAM表层土壤湿度高于本地窗口P80的日数 | Days with GLEAM surface soil moisture >= local window-specific P80 | days | FullNew | [0, 147] | 0.0% |
| `blduration_wet_gleam_sms_p80_hema` | GLEAM表层土壤湿度高于本地窗口P80的日数 | Days with GLEAM surface soil moisture >= local window-specific P80 | days | HEMA | [0, 68] | 0.0% |
| `blduration_wet_gleam_sms_p80_v3he` | GLEAM表层土壤湿度高于本地窗口P80的日数 | Days with GLEAM surface soil moisture >= local window-specific P80 | days | V3HE | [0, 87] | 0.0% |
| `blduration_wet_gleam_sms_p80_v3pre30` | GLEAM表层土壤湿度高于本地窗口P80的日数 | Days with GLEAM surface soil moisture >= local window-specific P80 | days | V3pre30 | [0, 31] | 0.0% |
| `blduration_wet_gleam_sms_p90_fullnew` | GLEAM表层土壤湿度高于本地窗口P90的日数 | Days with GLEAM surface soil moisture >= local window-specific P90 | days | FullNew | [0, 89] | 0.0% |
| `blduration_wet_gleam_sms_p90_hema` | GLEAM表层土壤湿度高于本地窗口P90的日数 | Days with GLEAM surface soil moisture >= local window-specific P90 | days | HEMA | [0, 37] | 0.0% |
| `blduration_wet_gleam_sms_p90_v3he` | GLEAM表层土壤湿度高于本地窗口P90的日数 | Days with GLEAM surface soil moisture >= local window-specific P90 | days | V3HE | [0, 52] | 0.0% |
| `blduration_wet_gleam_sms_p90_v3pre30` | GLEAM表层土壤湿度高于本地窗口P90的日数 | Days with GLEAM surface soil moisture >= local window-specific P90 | days | V3pre30 | [0, 22] | 0.0% |
| `bldurshare_dry_gleam_smrz_p10_fullnew` | GLEAM根区土壤湿度低于本地窗口P10的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local window-specific P10 | 0-1 | FullNew | [0, 0.7702] | 0.0% |
| `bldurshare_dry_gleam_smrz_p10_hema` | GLEAM根区土壤湿度低于本地窗口P10的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local window-specific P10 | 0-1 | HEMA | [0, 0.931] | 0.0% |
| `bldurshare_dry_gleam_smrz_p10_v3he` | GLEAM根区土壤湿度低于本地窗口P10的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local window-specific P10 | 0-1 | V3HE | [0, 0.8868] | 0.0% |
| `bldurshare_dry_gleam_smrz_p10_v3pre30` | GLEAM根区土壤湿度低于本地窗口P10的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local window-specific P10 | 0-1 | V3pre30 | [0, 0.7097] | 0.0% |
| `bldurshare_dry_gleam_smrz_p20_fullnew` | GLEAM根区土壤湿度低于本地窗口P20的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local window-specific P20 | 0-1 | FullNew | [0, 1] | 0.0% |
| `bldurshare_dry_gleam_smrz_p20_hema` | GLEAM根区土壤湿度低于本地窗口P20的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local window-specific P20 | 0-1 | HEMA | [0, 1] | 0.0% |
| `bldurshare_dry_gleam_smrz_p20_v3he` | GLEAM根区土壤湿度低于本地窗口P20的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local window-specific P20 | 0-1 | V3HE | [0, 1] | 0.0% |
| `bldurshare_dry_gleam_smrz_p20_v3pre30` | GLEAM根区土壤湿度低于本地窗口P20的日占比 | Share of valid days with GLEAM root-zone soil moisture <= local window-specific P20 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `bldurshare_dry_gleam_sms_p10_fullnew` | GLEAM表层土壤湿度低于本地窗口P10的日占比 | Share of valid days with GLEAM surface soil moisture <= local window-specific P10 | 0-1 | FullNew | [0, 0.5659] | 0.0% |
| `bldurshare_dry_gleam_sms_p10_hema` | GLEAM表层土壤湿度低于本地窗口P10的日占比 | Share of valid days with GLEAM surface soil moisture <= local window-specific P10 | 0-1 | HEMA | [0, 0.75] | 0.0% |
| `bldurshare_dry_gleam_sms_p10_v3he` | GLEAM表层土壤湿度低于本地窗口P10的日占比 | Share of valid days with GLEAM surface soil moisture <= local window-specific P10 | 0-1 | V3HE | [0, 0.6833] | 0.0% |
| `bldurshare_dry_gleam_sms_p10_v3pre30` | GLEAM表层土壤湿度低于本地窗口P10的日占比 | Share of valid days with GLEAM surface soil moisture <= local window-specific P10 | 0-1 | V3pre30 | [0, 0.7097] | 0.0% |
| `bldurshare_dry_gleam_sms_p20_fullnew` | GLEAM表层土壤湿度低于本地窗口P20的日占比 | Share of valid days with GLEAM surface soil moisture <= local window-specific P20 | 0-1 | FullNew | [0, 0.8777] | 0.0% |
| `bldurshare_dry_gleam_sms_p20_hema` | GLEAM表层土壤湿度低于本地窗口P20的日占比 | Share of valid days with GLEAM surface soil moisture <= local window-specific P20 | 0-1 | HEMA | [0, 0.9697] | 0.0% |
| `bldurshare_dry_gleam_sms_p20_v3he` | GLEAM表层土壤湿度低于本地窗口P20的日占比 | Share of valid days with GLEAM surface soil moisture <= local window-specific P20 | 0-1 | V3HE | [0, 0.9344] | 0.0% |
| `bldurshare_dry_gleam_sms_p20_v3pre30` | GLEAM表层土壤湿度低于本地窗口P20的日占比 | Share of valid days with GLEAM surface soil moisture <= local window-specific P20 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `bldurshare_wet_gleam_smrz_p80_fullnew` | GLEAM根区土壤湿度高于本地窗口P80的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local window-specific P80 | 0-1 | FullNew | [0, 1] | 0.0% |
| `bldurshare_wet_gleam_smrz_p80_hema` | GLEAM根区土壤湿度高于本地窗口P80的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local window-specific P80 | 0-1 | HEMA | [0, 1] | 0.0% |
| `bldurshare_wet_gleam_smrz_p80_v3he` | GLEAM根区土壤湿度高于本地窗口P80的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local window-specific P80 | 0-1 | V3HE | [0, 1] | 0.0% |
| `bldurshare_wet_gleam_smrz_p80_v3pre30` | GLEAM根区土壤湿度高于本地窗口P80的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local window-specific P80 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `bldurshare_wet_gleam_smrz_p90_fullnew` | GLEAM根区土壤湿度高于本地窗口P90的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local window-specific P90 | 0-1 | FullNew | [0, 0.8252] | 0.0% |
| `bldurshare_wet_gleam_smrz_p90_hema` | GLEAM根区土壤湿度高于本地窗口P90的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local window-specific P90 | 0-1 | HEMA | [0, 0.96] | 0.0% |
| `bldurshare_wet_gleam_smrz_p90_v3he` | GLEAM根区土壤湿度高于本地窗口P90的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local window-specific P90 | 0-1 | V3HE | [0, 0.8571] | 0.0% |
| `bldurshare_wet_gleam_smrz_p90_v3pre30` | GLEAM根区土壤湿度高于本地窗口P90的日占比 | Share of valid days with GLEAM root-zone soil moisture >= local window-specific P90 | 0-1 | V3pre30 | [0, 0.7097] | 0.0% |
| `bldurshare_wet_gleam_sms_p80_fullnew` | GLEAM表层土壤湿度高于本地窗口P80的日占比 | Share of valid days with GLEAM surface soil moisture >= local window-specific P80 | 0-1 | FullNew | [0, 0.9245] | 0.0% |
| `bldurshare_wet_gleam_sms_p80_hema` | GLEAM表层土壤湿度高于本地窗口P80的日占比 | Share of valid days with GLEAM surface soil moisture >= local window-specific P80 | 0-1 | HEMA | [0, 1] | 0.0% |
| `bldurshare_wet_gleam_sms_p80_v3he` | GLEAM表层土壤湿度高于本地窗口P80的日占比 | Share of valid days with GLEAM surface soil moisture >= local window-specific P80 | 0-1 | V3HE | [0, 1] | 0.0% |
| `bldurshare_wet_gleam_sms_p80_v3pre30` | GLEAM表层土壤湿度高于本地窗口P80的日占比 | Share of valid days with GLEAM surface soil moisture >= local window-specific P80 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `bldurshare_wet_gleam_sms_p90_fullnew` | GLEAM表层土壤湿度高于本地窗口P90的日占比 | Share of valid days with GLEAM surface soil moisture >= local window-specific P90 | 0-1 | FullNew | [0, 0.594] | 0.0% |
| `bldurshare_wet_gleam_sms_p90_hema` | GLEAM表层土壤湿度高于本地窗口P90的日占比 | Share of valid days with GLEAM surface soil moisture >= local window-specific P90 | 0-1 | HEMA | [0, 0.8182] | 0.0% |
| `bldurshare_wet_gleam_sms_p90_v3he` | GLEAM表层土壤湿度高于本地窗口P90的日占比 | Share of valid days with GLEAM surface soil moisture >= local window-specific P90 | 0-1 | V3HE | [0, 0.6308] | 0.0% |
| `bldurshare_wet_gleam_sms_p90_v3pre30` | GLEAM表层土壤湿度高于本地窗口P90的日占比 | Share of valid days with GLEAM surface soil moisture >= local window-specific P90 | 0-1 | V3pre30 | [0, 0.7097] | 0.0% |
| `blseveritymean_ddf_gleam_smrz_p10_fullnew` | GLEAM根区土壤湿度低于本地窗口P10的平均亏缺 | Mean deficit below local window-specific P10 for GLEAM root-zone soil moisture | m3/m3 | FullNew | [0, 0.01957] | 0.0% |
| `blseveritymean_ddf_gleam_smrz_p10_hema` | GLEAM根区土壤湿度低于本地窗口P10的平均亏缺 | Mean deficit below local window-specific P10 for GLEAM root-zone soil moisture | m3/m3 | HEMA | [0, 0.02442] | 0.0% |
| `blseveritymean_ddf_gleam_smrz_p10_v3he` | GLEAM根区土壤湿度低于本地窗口P10的平均亏缺 | Mean deficit below local window-specific P10 for GLEAM root-zone soil moisture | m3/m3 | V3HE | [0, 0.03714] | 0.0% |
| `blseveritymean_ddf_gleam_smrz_p10_v3pre30` | GLEAM根区土壤湿度低于本地窗口P10的平均亏缺 | Mean deficit below local window-specific P10 for GLEAM root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.01623] | 0.0% |
| `blseveritymean_ddf_gleam_smrz_p20_fullnew` | GLEAM根区土壤湿度低于本地窗口P20的平均亏缺 | Mean deficit below local window-specific P20 for GLEAM root-zone soil moisture | m3/m3 | FullNew | [0, 0.06145] | 0.0% |
| `blseveritymean_ddf_gleam_smrz_p20_hema` | GLEAM根区土壤湿度低于本地窗口P20的平均亏缺 | Mean deficit below local window-specific P20 for GLEAM root-zone soil moisture | m3/m3 | HEMA | [0, 0.09904] | 0.0% |
| `blseveritymean_ddf_gleam_smrz_p20_v3he` | GLEAM根区土壤湿度低于本地窗口P20的平均亏缺 | Mean deficit below local window-specific P20 for GLEAM root-zone soil moisture | m3/m3 | V3HE | [0, 0.09721] | 0.0% |
| `blseveritymean_ddf_gleam_smrz_p20_v3pre30` | GLEAM根区土壤湿度低于本地窗口P20的平均亏缺 | Mean deficit below local window-specific P20 for GLEAM root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.07289] | 0.0% |
| `blseveritymean_ddf_gleam_sms_p10_fullnew` | GLEAM表层土壤湿度低于本地窗口P10的平均亏缺 | Mean deficit below local window-specific P10 for GLEAM surface soil moisture | m3/m3 | FullNew | [0, 0.02232] | 0.0% |
| `blseveritymean_ddf_gleam_sms_p10_hema` | GLEAM表层土壤湿度低于本地窗口P10的平均亏缺 | Mean deficit below local window-specific P10 for GLEAM surface soil moisture | m3/m3 | HEMA | [0, 0.04234] | 0.0% |
| `blseveritymean_ddf_gleam_sms_p10_v3he` | GLEAM表层土壤湿度低于本地窗口P10的平均亏缺 | Mean deficit below local window-specific P10 for GLEAM surface soil moisture | m3/m3 | V3HE | [0, 0.03419] | 0.0% |
| `blseveritymean_ddf_gleam_sms_p10_v3pre30` | GLEAM表层土壤湿度低于本地窗口P10的平均亏缺 | Mean deficit below local window-specific P10 for GLEAM surface soil moisture | m3/m3 | V3pre30 | [0, 0.02504] | 0.0% |
| `blseveritymean_ddf_gleam_sms_p20_fullnew` | GLEAM表层土壤湿度低于本地窗口P20的平均亏缺 | Mean deficit below local window-specific P20 for GLEAM surface soil moisture | m3/m3 | FullNew | [0, 0.04174] | 0.0% |
| `blseveritymean_ddf_gleam_sms_p20_hema` | GLEAM表层土壤湿度低于本地窗口P20的平均亏缺 | Mean deficit below local window-specific P20 for GLEAM surface soil moisture | m3/m3 | HEMA | [0, 0.07192] | 0.0% |
| `blseveritymean_ddf_gleam_sms_p20_v3he` | GLEAM表层土壤湿度低于本地窗口P20的平均亏缺 | Mean deficit below local window-specific P20 for GLEAM surface soil moisture | m3/m3 | V3HE | [0, 0.0566] | 0.0% |
| `blseveritymean_ddf_gleam_sms_p20_v3pre30` | GLEAM表层土壤湿度低于本地窗口P20的平均亏缺 | Mean deficit below local window-specific P20 for GLEAM surface soil moisture | m3/m3 | V3pre30 | [0, 0.0508] | 0.0% |
| `blseveritymean_wex_gleam_smrz_p80_fullnew` | GLEAM根区土壤湿度高于本地窗口P80的平均超额 | Mean excess above local window-specific P80 for GLEAM root-zone soil moisture | m3/m3 | FullNew | [0, 0.06177] | 0.0% |
| `blseveritymean_wex_gleam_smrz_p80_hema` | GLEAM根区土壤湿度高于本地窗口P80的平均超额 | Mean excess above local window-specific P80 for GLEAM root-zone soil moisture | m3/m3 | HEMA | [0, 0.1281] | 0.0% |
| `blseveritymean_wex_gleam_smrz_p80_v3he` | GLEAM根区土壤湿度高于本地窗口P80的平均超额 | Mean excess above local window-specific P80 for GLEAM root-zone soil moisture | m3/m3 | V3HE | [0, 0.09046] | 0.0% |
| `blseveritymean_wex_gleam_smrz_p80_v3pre30` | GLEAM根区土壤湿度高于本地窗口P80的平均超额 | Mean excess above local window-specific P80 for GLEAM root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.09225] | 0.0% |
| `blseveritymean_wex_gleam_smrz_p90_fullnew` | GLEAM根区土壤湿度高于本地窗口P90的平均超额 | Mean excess above local window-specific P90 for GLEAM root-zone soil moisture | m3/m3 | FullNew | [0, 0.0282] | 0.0% |
| `blseveritymean_wex_gleam_smrz_p90_hema` | GLEAM根区土壤湿度高于本地窗口P90的平均超额 | Mean excess above local window-specific P90 for GLEAM root-zone soil moisture | m3/m3 | HEMA | [0, 0.04155] | 0.0% |
| `blseveritymean_wex_gleam_smrz_p90_v3he` | GLEAM根区土壤湿度高于本地窗口P90的平均超额 | Mean excess above local window-specific P90 for GLEAM root-zone soil moisture | m3/m3 | V3HE | [0, 0.06137] | 0.0% |
| `blseveritymean_wex_gleam_smrz_p90_v3pre30` | GLEAM根区土壤湿度高于本地窗口P90的平均超额 | Mean excess above local window-specific P90 for GLEAM root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.02449] | 0.0% |
| `blseveritymean_wex_gleam_sms_p80_fullnew` | GLEAM表层土壤湿度高于本地窗口P80的平均超额 | Mean excess above local window-specific P80 for GLEAM surface soil moisture | m3/m3 | FullNew | [0, 0.04254] | 0.0% |
| `blseveritymean_wex_gleam_sms_p80_hema` | GLEAM表层土壤湿度高于本地窗口P80的平均超额 | Mean excess above local window-specific P80 for GLEAM surface soil moisture | m3/m3 | HEMA | [0, 0.08198] | 0.0% |
| `blseveritymean_wex_gleam_sms_p80_v3he` | GLEAM表层土壤湿度高于本地窗口P80的平均超额 | Mean excess above local window-specific P80 for GLEAM surface soil moisture | m3/m3 | V3HE | [0, 0.0518] | 0.0% |
| `blseveritymean_wex_gleam_sms_p80_v3pre30` | GLEAM表层土壤湿度高于本地窗口P80的平均超额 | Mean excess above local window-specific P80 for GLEAM surface soil moisture | m3/m3 | V3pre30 | [0, 0.05297] | 0.0% |
| `blseveritymean_wex_gleam_sms_p90_fullnew` | GLEAM表层土壤湿度高于本地窗口P90的平均超额 | Mean excess above local window-specific P90 for GLEAM surface soil moisture | m3/m3 | FullNew | [0, 0.01805] | 0.0% |
| `blseveritymean_wex_gleam_sms_p90_hema` | GLEAM表层土壤湿度高于本地窗口P90的平均超额 | Mean excess above local window-specific P90 for GLEAM surface soil moisture | m3/m3 | HEMA | [0, 0.03792] | 0.0% |
| `blseveritymean_wex_gleam_sms_p90_v3he` | GLEAM表层土壤湿度高于本地窗口P90的平均超额 | Mean excess above local window-specific P90 for GLEAM surface soil moisture | m3/m3 | V3HE | [0, 0.02955] | 0.0% |
| `blseveritymean_wex_gleam_sms_p90_v3pre30` | GLEAM表层土壤湿度高于本地窗口P90的平均超额 | Mean excess above local window-specific P90 for GLEAM surface soil moisture | m3/m3 | V3pre30 | [0, 0.02672] | 0.0% |
| `blseveritysum_ddf_gleam_smrz_p10_fullnew` | GLEAM根区土壤湿度低于本地窗口P10的累计亏缺 | Sum deficit below local window-specific P10 for GLEAM root-zone soil moisture | m3/m3 | FullNew | [0, 2.721] | 0.0% |
| `blseveritysum_ddf_gleam_smrz_p10_hema` | GLEAM根区土壤湿度低于本地窗口P10的累计亏缺 | Sum deficit below local window-specific P10 for GLEAM root-zone soil moisture | m3/m3 | HEMA | [0, 1.853] | 0.0% |
| `blseveritysum_ddf_gleam_smrz_p10_v3he` | GLEAM根区土壤湿度低于本地窗口P10的累计亏缺 | Sum deficit below local window-specific P10 for GLEAM root-zone soil moisture | m3/m3 | V3HE | [0, 2.377] | 0.0% |
| `blseveritysum_ddf_gleam_smrz_p10_v3pre30` | GLEAM根区土壤湿度低于本地窗口P10的累计亏缺 | Sum deficit below local window-specific P10 for GLEAM root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.503] | 0.0% |
| `blseveritysum_ddf_gleam_smrz_p20_fullnew` | GLEAM根区土壤湿度低于本地窗口P20的累计亏缺 | Sum deficit below local window-specific P20 for GLEAM root-zone soil moisture | m3/m3 | FullNew | [0, 8.542] | 0.0% |
| `blseveritysum_ddf_gleam_smrz_p20_hema` | GLEAM根区土壤湿度低于本地窗口P20的累计亏缺 | Sum deficit below local window-specific P20 for GLEAM root-zone soil moisture | m3/m3 | HEMA | [0, 4.358] | 0.0% |
| `blseveritysum_ddf_gleam_smrz_p20_v3he` | GLEAM根区土壤湿度低于本地窗口P20的累计亏缺 | Sum deficit below local window-specific P20 for GLEAM root-zone soil moisture | m3/m3 | V3HE | [0, 5.833] | 0.0% |
| `blseveritysum_ddf_gleam_smrz_p20_v3pre30` | GLEAM根区土壤湿度低于本地窗口P20的累计亏缺 | Sum deficit below local window-specific P20 for GLEAM root-zone soil moisture | m3/m3 | V3pre30 | [0, 2.26] | 0.0% |
| `blseveritysum_ddf_gleam_sms_p10_fullnew` | GLEAM表层土壤湿度低于本地窗口P10的累计亏缺 | Sum deficit below local window-specific P10 for GLEAM surface soil moisture | m3/m3 | FullNew | [0, 3.36] | 0.0% |
| `blseveritysum_ddf_gleam_sms_p10_hema` | GLEAM表层土壤湿度低于本地窗口P10的累计亏缺 | Sum deficit below local window-specific P10 for GLEAM surface soil moisture | m3/m3 | HEMA | [0, 1.898] | 0.0% |
| `blseveritysum_ddf_gleam_sms_p10_v3he` | GLEAM表层土壤湿度低于本地窗口P10的累计亏缺 | Sum deficit below local window-specific P10 for GLEAM surface soil moisture | m3/m3 | V3HE | [0, 2.558] | 0.0% |
| `blseveritysum_ddf_gleam_sms_p10_v3pre30` | GLEAM表层土壤湿度低于本地窗口P10的累计亏缺 | Sum deficit below local window-specific P10 for GLEAM surface soil moisture | m3/m3 | V3pre30 | [0, 0.7762] | 0.0% |
| `blseveritysum_ddf_gleam_sms_p20_fullnew` | GLEAM表层土壤湿度低于本地窗口P20的累计亏缺 | Sum deficit below local window-specific P20 for GLEAM surface soil moisture | m3/m3 | FullNew | [0, 6.206] | 0.0% |
| `blseveritysum_ddf_gleam_sms_p20_hema` | GLEAM表层土壤湿度低于本地窗口P20的累计亏缺 | Sum deficit below local window-specific P20 for GLEAM surface soil moisture | m3/m3 | HEMA | [0, 3.57] | 0.0% |
| `blseveritysum_ddf_gleam_sms_p20_v3he` | GLEAM表层土壤湿度低于本地窗口P20的累计亏缺 | Sum deficit below local window-specific P20 for GLEAM surface soil moisture | m3/m3 | V3HE | [0, 4.667] | 0.0% |
| `blseveritysum_ddf_gleam_sms_p20_v3pre30` | GLEAM表层土壤湿度低于本地窗口P20的累计亏缺 | Sum deficit below local window-specific P20 for GLEAM surface soil moisture | m3/m3 | V3pre30 | [0, 1.575] | 0.0% |
| `blseveritysum_wex_gleam_smrz_p80_fullnew` | GLEAM根区土壤湿度高于本地窗口P80的累计超额 | Sum excess above local window-specific P80 for GLEAM root-zone soil moisture | m3/m3 | FullNew | [0, 9.822] | 0.0% |
| `blseveritysum_wex_gleam_smrz_p80_hema` | GLEAM根区土壤湿度高于本地窗口P80的累计超额 | Sum excess above local window-specific P80 for GLEAM root-zone soil moisture | m3/m3 | HEMA | [0, 4.227] | 0.0% |
| `blseveritysum_wex_gleam_smrz_p80_v3he` | GLEAM根区土壤湿度高于本地窗口P80的累计超额 | Sum excess above local window-specific P80 for GLEAM root-zone soil moisture | m3/m3 | V3HE | [0, 7.327] | 0.0% |
| `blseveritysum_wex_gleam_smrz_p80_v3pre30` | GLEAM根区土壤湿度高于本地窗口P80的累计超额 | Sum excess above local window-specific P80 for GLEAM root-zone soil moisture | m3/m3 | V3pre30 | [0, 2.86] | 0.0% |
| `blseveritysum_wex_gleam_smrz_p90_fullnew` | GLEAM根区土壤湿度高于本地窗口P90的累计超额 | Sum excess above local window-specific P90 for GLEAM root-zone soil moisture | m3/m3 | FullNew | [0, 3.356] | 0.0% |
| `blseveritysum_wex_gleam_smrz_p90_hema` | GLEAM根区土壤湿度高于本地窗口P90的累计超额 | Sum excess above local window-specific P90 for GLEAM root-zone soil moisture | m3/m3 | HEMA | [0, 1.776] | 0.0% |
| `blseveritysum_wex_gleam_smrz_p90_v3he` | GLEAM根区土壤湿度高于本地窗口P90的累计超额 | Sum excess above local window-specific P90 for GLEAM root-zone soil moisture | m3/m3 | V3HE | [0, 2.826] | 0.0% |
| `blseveritysum_wex_gleam_smrz_p90_v3pre30` | GLEAM根区土壤湿度高于本地窗口P90的累计超额 | Sum excess above local window-specific P90 for GLEAM root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.7593] | 0.0% |
| `blseveritysum_wex_gleam_sms_p80_fullnew` | GLEAM表层土壤湿度高于本地窗口P80的累计超额 | Sum excess above local window-specific P80 for GLEAM surface soil moisture | m3/m3 | FullNew | [0, 6.764] | 0.0% |
| `blseveritysum_wex_gleam_sms_p80_hema` | GLEAM表层土壤湿度高于本地窗口P80的累计超额 | Sum excess above local window-specific P80 for GLEAM surface soil moisture | m3/m3 | HEMA | [0, 2.704] | 0.0% |
| `blseveritysum_wex_gleam_sms_p80_v3he` | GLEAM表层土壤湿度高于本地窗口P80的累计超额 | Sum excess above local window-specific P80 for GLEAM surface soil moisture | m3/m3 | V3HE | [0, 4.453] | 0.0% |
| `blseveritysum_wex_gleam_sms_p80_v3pre30` | GLEAM表层土壤湿度高于本地窗口P80的累计超额 | Sum excess above local window-specific P80 for GLEAM surface soil moisture | m3/m3 | V3pre30 | [0, 1.642] | 0.0% |
| `blseveritysum_wex_gleam_sms_p90_fullnew` | GLEAM表层土壤湿度高于本地窗口P90的累计超额 | Sum excess above local window-specific P90 for GLEAM surface soil moisture | m3/m3 | FullNew | [0, 2.32] | 0.0% |
| `blseveritysum_wex_gleam_sms_p90_hema` | GLEAM表层土壤湿度高于本地窗口P90的累计超额 | Sum excess above local window-specific P90 for GLEAM surface soil moisture | m3/m3 | HEMA | [0, 1.307] | 0.0% |
| `blseveritysum_wex_gleam_sms_p90_v3he` | GLEAM表层土壤湿度高于本地窗口P90的累计超额 | Sum excess above local window-specific P90 for GLEAM surface soil moisture | m3/m3 | V3HE | [0, 1.713] | 0.0% |
| `blseveritysum_wex_gleam_sms_p90_v3pre30` | GLEAM表层土壤湿度高于本地窗口P90的累计超额 | Sum excess above local window-specific P90 for GLEAM surface soil moisture | m3/m3 | V3pre30 | [0, 0.8282] | 0.0% |

## 7. SM-SWSM (288 vars)

### baseline-local

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `drydays_swsm_l1_le_p10` | SWSM L1表层土壤湿度低于本地历史P10的日数 | Days with SWSM L1 surface soil moisture <= local historical P10 | days | Full | [0, 101] | 6.3% |
| `drydays_swsm_l1_le_p10_hema` | SWSM L1表层土壤湿度低于本地历史P10的日数 | Days with SWSM L1 surface soil moisture <= local historical P10 | days | HEMA | [0, 51] | 6.3% |
| `drydays_swsm_l1_le_p10_hepm10` | SWSM L1表层土壤湿度低于本地历史P10的日数 | Days with SWSM L1 surface soil moisture <= local historical P10 | days | HEpm10 | [0, 21] | 6.3% |
| `drydays_swsm_l1_le_p10_v3he` | SWSM L1表层土壤湿度低于本地历史P10的日数 | Days with SWSM L1 surface soil moisture <= local historical P10 | days | V3HE | [0, 66] | 6.3% |
| `drydays_swsm_l1_le_p10_v3pm10` | SWSM L1表层土壤湿度低于本地历史P10的日数 | Days with SWSM L1 surface soil moisture <= local historical P10 | days | V3pm10 | [0, 21] | 6.3% |
| `drydays_swsm_l1_le_p10_v3pre30` | SWSM L1表层土壤湿度低于本地历史P10的日数 | Days with SWSM L1 surface soil moisture <= local historical P10 | days | V3pre30 | [0, 31] | 6.3% |
| `drydays_swsm_l1_le_p20` | SWSM L1表层土壤湿度低于本地历史P20的日数 | Days with SWSM L1 surface soil moisture <= local historical P20 | days | Full | [0, 145] | 6.3% |
| `drydays_swsm_l1_le_p20_hema` | SWSM L1表层土壤湿度低于本地历史P20的日数 | Days with SWSM L1 surface soil moisture <= local historical P20 | days | HEMA | [0, 83] | 6.3% |
| `drydays_swsm_l1_le_p20_hepm10` | SWSM L1表层土壤湿度低于本地历史P20的日数 | Days with SWSM L1 surface soil moisture <= local historical P20 | days | HEpm10 | [0, 21] | 6.3% |
| `drydays_swsm_l1_le_p20_v3he` | SWSM L1表层土壤湿度低于本地历史P20的日数 | Days with SWSM L1 surface soil moisture <= local historical P20 | days | V3HE | [0, 73] | 6.3% |
| `drydays_swsm_l1_le_p20_v3pm10` | SWSM L1表层土壤湿度低于本地历史P20的日数 | Days with SWSM L1 surface soil moisture <= local historical P20 | days | V3pm10 | [0, 21] | 6.3% |
| `drydays_swsm_l1_le_p20_v3pre30` | SWSM L1表层土壤湿度低于本地历史P20的日数 | Days with SWSM L1 surface soil moisture <= local historical P20 | days | V3pre30 | [0, 31] | 6.3% |
| `drydays_swsm_l3_le_p10` | SWSM L3深层土壤湿度低于本地历史P10的日数 | Days with SWSM L3 deep soil moisture <= local historical P10 | days | Full | [0, 146] | 6.3% |
| `drydays_swsm_l3_le_p10_hema` | SWSM L3深层土壤湿度低于本地历史P10的日数 | Days with SWSM L3 deep soil moisture <= local historical P10 | days | HEMA | [0, 84] | 6.3% |
| `drydays_swsm_l3_le_p10_hepm10` | SWSM L3深层土壤湿度低于本地历史P10的日数 | Days with SWSM L3 deep soil moisture <= local historical P10 | days | HEpm10 | [0, 21] | 6.3% |
| `drydays_swsm_l3_le_p10_v3he` | SWSM L3深层土壤湿度低于本地历史P10的日数 | Days with SWSM L3 deep soil moisture <= local historical P10 | days | V3HE | [0, 93] | 6.3% |
| `drydays_swsm_l3_le_p10_v3pm10` | SWSM L3深层土壤湿度低于本地历史P10的日数 | Days with SWSM L3 deep soil moisture <= local historical P10 | days | V3pm10 | [0, 21] | 6.3% |
| `drydays_swsm_l3_le_p10_v3pre30` | SWSM L3深层土壤湿度低于本地历史P10的日数 | Days with SWSM L3 deep soil moisture <= local historical P10 | days | V3pre30 | [0, 31] | 6.3% |
| `drydays_swsm_l3_le_p20` | SWSM L3深层土壤湿度低于本地历史P20的日数 | Days with SWSM L3 deep soil moisture <= local historical P20 | days | Full | [0, 195] | 6.3% |
| `drydays_swsm_l3_le_p20_hema` | SWSM L3深层土壤湿度低于本地历史P20的日数 | Days with SWSM L3 deep soil moisture <= local historical P20 | days | HEMA | [0, 104] | 6.3% |
| `drydays_swsm_l3_le_p20_hepm10` | SWSM L3深层土壤湿度低于本地历史P20的日数 | Days with SWSM L3 deep soil moisture <= local historical P20 | days | HEpm10 | [0, 21] | 6.3% |
| `drydays_swsm_l3_le_p20_v3he` | SWSM L3深层土壤湿度低于本地历史P20的日数 | Days with SWSM L3 deep soil moisture <= local historical P20 | days | V3HE | [0, 93] | 6.3% |
| `drydays_swsm_l3_le_p20_v3pm10` | SWSM L3深层土壤湿度低于本地历史P20的日数 | Days with SWSM L3 deep soil moisture <= local historical P20 | days | V3pm10 | [0, 21] | 6.3% |
| `drydays_swsm_l3_le_p20_v3pre30` | SWSM L3深层土壤湿度低于本地历史P20的日数 | Days with SWSM L3 deep soil moisture <= local historical P20 | days | V3pre30 | [0, 31] | 6.3% |
| `drydeficit_swsm_l1_le_p10` | SWSM L1表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for SWSM L1 surface soil moisture | m3/m3 | Full | [0, 0.03184] | 6.3% |
| `drydeficit_swsm_l1_le_p10_hema` | SWSM L1表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for SWSM L1 surface soil moisture | m3/m3 | HEMA | [0, 0.05273] | 6.3% |
| `drydeficit_swsm_l1_le_p10_hepm10` | SWSM L1表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for SWSM L1 surface soil moisture | m3/m3 | HEpm10 | [0, 0.0619] | 6.3% |
| `drydeficit_swsm_l1_le_p10_v3he` | SWSM L1表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for SWSM L1 surface soil moisture | m3/m3 | V3HE | [0, 0.04565] | 6.3% |
| `drydeficit_swsm_l1_le_p10_v3pm10` | SWSM L1表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for SWSM L1 surface soil moisture | m3/m3 | V3pm10 | [0, 0.1429] | 6.3% |
| `drydeficit_swsm_l1_le_p10_v3pre30` | SWSM L1表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for SWSM L1 surface soil moisture | m3/m3 | V3pre30 | [0, 0.1045] | 6.3% |
| `drydeficit_swsm_l1_le_p20` | SWSM L1表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for SWSM L1 surface soil moisture | m3/m3 | Full | [0, 0.06132] | 6.3% |
| `drydeficit_swsm_l1_le_p20_hema` | SWSM L1表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for SWSM L1 surface soil moisture | m3/m3 | HEMA | [0, 0.07564] | 6.3% |
| `drydeficit_swsm_l1_le_p20_hepm10` | SWSM L1表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for SWSM L1 surface soil moisture | m3/m3 | HEpm10 | [0, 0.1133] | 6.3% |
| `drydeficit_swsm_l1_le_p20_v3he` | SWSM L1表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for SWSM L1 surface soil moisture | m3/m3 | V3HE | [0, 0.07304] | 6.3% |
| `drydeficit_swsm_l1_le_p20_v3pm10` | SWSM L1表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for SWSM L1 surface soil moisture | m3/m3 | V3pm10 | [0, 0.2024] | 6.3% |
| `drydeficit_swsm_l1_le_p20_v3pre30` | SWSM L1表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for SWSM L1 surface soil moisture | m3/m3 | V3pre30 | [0, 0.1823] | 6.3% |
| `drydeficit_swsm_l3_le_p10` | SWSM L3深层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for SWSM L3 deep soil moisture | m3/m3 | Full | [0, 0.02959] | 6.3% |
| `drydeficit_swsm_l3_le_p10_hema` | SWSM L3深层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for SWSM L3 deep soil moisture | m3/m3 | HEMA | [0, 0.05524] | 6.3% |
| `drydeficit_swsm_l3_le_p10_hepm10` | SWSM L3深层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for SWSM L3 deep soil moisture | m3/m3 | HEpm10 | [0, 0.07714] | 6.3% |
| `drydeficit_swsm_l3_le_p10_v3he` | SWSM L3深层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for SWSM L3 deep soil moisture | m3/m3 | V3HE | [0, 0.05764] | 6.3% |
| `drydeficit_swsm_l3_le_p10_v3pm10` | SWSM L3深层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for SWSM L3 deep soil moisture | m3/m3 | V3pm10 | [0, 0.09857] | 6.3% |
| `drydeficit_swsm_l3_le_p10_v3pre30` | SWSM L3深层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for SWSM L3 deep soil moisture | m3/m3 | V3pre30 | [0, 0.06613] | 6.3% |
| `drydeficit_swsm_l3_le_p20` | SWSM L3深层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for SWSM L3 deep soil moisture | m3/m3 | Full | [0, 0.07491] | 6.3% |
| `drydeficit_swsm_l3_le_p20_hema` | SWSM L3深层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for SWSM L3 deep soil moisture | m3/m3 | HEMA | [0, 0.07919] | 6.3% |
| `drydeficit_swsm_l3_le_p20_hepm10` | SWSM L3深层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for SWSM L3 deep soil moisture | m3/m3 | HEpm10 | [0, 0.1029] | 6.3% |
| `drydeficit_swsm_l3_le_p20_v3he` | SWSM L3深层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for SWSM L3 deep soil moisture | m3/m3 | V3HE | [0, 0.09298] | 6.3% |
| `drydeficit_swsm_l3_le_p20_v3pm10` | SWSM L3深层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for SWSM L3 deep soil moisture | m3/m3 | V3pm10 | [0, 0.1386] | 6.3% |
| `drydeficit_swsm_l3_le_p20_v3pre30` | SWSM L3深层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for SWSM L3 deep soil moisture | m3/m3 | V3pre30 | [0, 0.1058] | 6.3% |
| `dryshare_swsm_l1_le_p10` | SWSM L1表层土壤湿度低于本地历史P10的日占比 | Share of valid days with SWSM L1 surface soil moisture <= local historical P10 | 0-1 | Full | [0, 0.6667] | 6.3% |
| `dryshare_swsm_l1_le_p10_hema` | SWSM L1表层土壤湿度低于本地历史P10的日占比 | Share of valid days with SWSM L1 surface soil moisture <= local historical P10 | 0-1 | HEMA | [0, 1] | 6.3% |
| `dryshare_swsm_l1_le_p10_hepm10` | SWSM L1表层土壤湿度低于本地历史P10的日占比 | Share of valid days with SWSM L1 surface soil moisture <= local historical P10 | 0-1 | HEpm10 | [0, 1] | 6.3% |
| `dryshare_swsm_l1_le_p10_v3he` | SWSM L1表层土壤湿度低于本地历史P10的日占比 | Share of valid days with SWSM L1 surface soil moisture <= local historical P10 | 0-1 | V3HE | [0, 0.9167] | 6.3% |
| `dryshare_swsm_l1_le_p10_v3pm10` | SWSM L1表层土壤湿度低于本地历史P10的日占比 | Share of valid days with SWSM L1 surface soil moisture <= local historical P10 | 0-1 | V3pm10 | [0, 1] | 6.3% |
| `dryshare_swsm_l1_le_p10_v3pre30` | SWSM L1表层土壤湿度低于本地历史P10的日占比 | Share of valid days with SWSM L1 surface soil moisture <= local historical P10 | 0-1 | V3pre30 | [0, 1] | 6.3% |
| `dryshare_swsm_l1_le_p20` | SWSM L1表层土壤湿度低于本地历史P20的日占比 | Share of valid days with SWSM L1 surface soil moisture <= local historical P20 | 0-1 | Full | [0, 0.8739] | 6.3% |
| `dryshare_swsm_l1_le_p20_hema` | SWSM L1表层土壤湿度低于本地历史P20的日占比 | Share of valid days with SWSM L1 surface soil moisture <= local historical P20 | 0-1 | HEMA | [0, 1] | 6.3% |
| `dryshare_swsm_l1_le_p20_hepm10` | SWSM L1表层土壤湿度低于本地历史P20的日占比 | Share of valid days with SWSM L1 surface soil moisture <= local historical P20 | 0-1 | HEpm10 | [0, 1] | 6.3% |
| `dryshare_swsm_l1_le_p20_v3he` | SWSM L1表层土壤湿度低于本地历史P20的日占比 | Share of valid days with SWSM L1 surface soil moisture <= local historical P20 | 0-1 | V3HE | [0, 1] | 6.3% |
| `dryshare_swsm_l1_le_p20_v3pm10` | SWSM L1表层土壤湿度低于本地历史P20的日占比 | Share of valid days with SWSM L1 surface soil moisture <= local historical P20 | 0-1 | V3pm10 | [0, 1] | 6.3% |
| `dryshare_swsm_l1_le_p20_v3pre30` | SWSM L1表层土壤湿度低于本地历史P20的日占比 | Share of valid days with SWSM L1 surface soil moisture <= local historical P20 | 0-1 | V3pre30 | [0, 1] | 6.3% |
| `dryshare_swsm_l3_le_p10` | SWSM L3深层土壤湿度低于本地历史P10的日占比 | Share of valid days with SWSM L3 deep soil moisture <= local historical P10 | 0-1 | Full | [0, 0.9429] | 6.3% |
| `dryshare_swsm_l3_le_p10_hema` | SWSM L3深层土壤湿度低于本地历史P10的日占比 | Share of valid days with SWSM L3 deep soil moisture <= local historical P10 | 0-1 | HEMA | [0, 1] | 6.3% |
| `dryshare_swsm_l3_le_p10_hepm10` | SWSM L3深层土壤湿度低于本地历史P10的日占比 | Share of valid days with SWSM L3 deep soil moisture <= local historical P10 | 0-1 | HEpm10 | [0, 1] | 6.3% |
| `dryshare_swsm_l3_le_p10_v3he` | SWSM L3深层土壤湿度低于本地历史P10的日占比 | Share of valid days with SWSM L3 deep soil moisture <= local historical P10 | 0-1 | V3HE | [0, 1] | 6.3% |
| `dryshare_swsm_l3_le_p10_v3pm10` | SWSM L3深层土壤湿度低于本地历史P10的日占比 | Share of valid days with SWSM L3 deep soil moisture <= local historical P10 | 0-1 | V3pm10 | [0, 1] | 6.3% |
| `dryshare_swsm_l3_le_p10_v3pre30` | SWSM L3深层土壤湿度低于本地历史P10的日占比 | Share of valid days with SWSM L3 deep soil moisture <= local historical P10 | 0-1 | V3pre30 | [0, 1] | 6.3% |
| `dryshare_swsm_l3_le_p20` | SWSM L3深层土壤湿度低于本地历史P20的日占比 | Share of valid days with SWSM L3 deep soil moisture <= local historical P20 | 0-1 | Full | [0, 1] | 6.3% |
| `dryshare_swsm_l3_le_p20_hema` | SWSM L3深层土壤湿度低于本地历史P20的日占比 | Share of valid days with SWSM L3 deep soil moisture <= local historical P20 | 0-1 | HEMA | [0, 1] | 6.3% |
| `dryshare_swsm_l3_le_p20_hepm10` | SWSM L3深层土壤湿度低于本地历史P20的日占比 | Share of valid days with SWSM L3 deep soil moisture <= local historical P20 | 0-1 | HEpm10 | [0, 1] | 6.3% |
| `dryshare_swsm_l3_le_p20_v3he` | SWSM L3深层土壤湿度低于本地历史P20的日占比 | Share of valid days with SWSM L3 deep soil moisture <= local historical P20 | 0-1 | V3HE | [0, 1] | 6.3% |
| `dryshare_swsm_l3_le_p20_v3pm10` | SWSM L3深层土壤湿度低于本地历史P20的日占比 | Share of valid days with SWSM L3 deep soil moisture <= local historical P20 | 0-1 | V3pm10 | [0, 1] | 6.3% |
| `dryshare_swsm_l3_le_p20_v3pre30` | SWSM L3深层土壤湿度低于本地历史P20的日占比 | Share of valid days with SWSM L3 deep soil moisture <= local historical P20 | 0-1 | V3pre30 | [0, 1] | 6.3% |
| `swsm_l1_max` | SWSM L1表层土壤湿度最大值 | SWSM L1 surface soil moisture max | m3/m3 | Full | [0.07, 0.57] | 6.3% |
| `swsm_l1_max_hema` | SWSM L1表层土壤湿度最大值 | SWSM L1 surface soil moisture max | m3/m3 | HEMA | [0.01, 0.57] | 6.3% |
| `swsm_l1_max_hepm10` | SWSM L1表层土壤湿度最大值 | SWSM L1 surface soil moisture max | m3/m3 | HEpm10 | [0.04, 0.56] | 6.3% |
| `swsm_l1_max_v3he` | SWSM L1表层土壤湿度最大值 | SWSM L1 surface soil moisture max | m3/m3 | V3HE | [0.04, 0.57] | 6.3% |
| `swsm_l1_max_v3pm10` | SWSM L1表层土壤湿度最大值 | SWSM L1 surface soil moisture max | m3/m3 | V3pm10 | [0.03, 0.56] | 6.3% |
| `swsm_l1_max_v3pre30` | SWSM L1表层土壤湿度最大值 | SWSM L1 surface soil moisture max | m3/m3 | V3pre30 | [0.03, 0.57] | 6.3% |
| `swsm_l1_mean` | SWSM L1表层土壤湿度均值 | SWSM L1 surface soil moisture mean | m3/m3 | Full | [0.03403, 0.489] | 6.3% |
| `swsm_l1_mean_hema` | SWSM L1表层土壤湿度均值 | SWSM L1 surface soil moisture mean | m3/m3 | HEMA | [0.01, 0.508] | 6.3% |
| `swsm_l1_mean_hepm10` | SWSM L1表层土壤湿度均值 | SWSM L1 surface soil moisture mean | m3/m3 | HEpm10 | [0.02357, 0.5119] | 6.3% |
| `swsm_l1_mean_v3he` | SWSM L1表层土壤湿度均值 | SWSM L1 surface soil moisture mean | m3/m3 | V3HE | [0.03205, 0.5069] | 6.3% |
| `swsm_l1_mean_v3pm10` | SWSM L1表层土壤湿度均值 | SWSM L1 surface soil moisture mean | m3/m3 | V3pm10 | [0.0175, 0.5148] | 6.3% |
| `swsm_l1_mean_v3pre30` | SWSM L1表层土壤湿度均值 | SWSM L1 surface soil moisture mean | m3/m3 | V3pre30 | [0.01304, 0.5152] | 6.3% |
| `swsm_l1_min` | SWSM L1表层土壤湿度最小值 | SWSM L1 surface soil moisture min | m3/m3 | Full | [0.01, 0.4] | 6.3% |
| `swsm_l1_min_hema` | SWSM L1表层土壤湿度最小值 | SWSM L1 surface soil moisture min | m3/m3 | HEMA | [0.01, 0.46] | 6.3% |
| `swsm_l1_min_hepm10` | SWSM L1表层土壤湿度最小值 | SWSM L1 surface soil moisture min | m3/m3 | HEpm10 | [0.01, 0.48] | 6.3% |
| `swsm_l1_min_v3he` | SWSM L1表层土壤湿度最小值 | SWSM L1 surface soil moisture min | m3/m3 | V3HE | [0.01, 0.44] | 6.3% |
| `swsm_l1_min_v3pm10` | SWSM L1表层土壤湿度最小值 | SWSM L1 surface soil moisture min | m3/m3 | V3pm10 | [0.01, 0.48] | 6.3% |
| `swsm_l1_min_v3pre30` | SWSM L1表层土壤湿度最小值 | SWSM L1 surface soil moisture min | m3/m3 | V3pre30 | [0.01, 0.46] | 6.3% |
| `swsm_l1_sd` | SWSM L1表层土壤湿度标准差 | SWSM L1 surface soil moisture std dev | m3/m3 | Full | [0.005561, 0.1397] | 6.3% |
| `swsm_l1_sd_hema` | SWSM L1表层土壤湿度标准差 | SWSM L1 surface soil moisture std dev | m3/m3 | HEMA | [0.003873, 0.1329] | 6.3% |
| `swsm_l1_sd_hepm10` | SWSM L1表层土壤湿度标准差 | SWSM L1 surface soil moisture std dev | m3/m3 | HEpm10 | [0.002182, 0.1206] | 6.3% |
| `swsm_l1_sd_v3he` | SWSM L1表层土壤湿度标准差 | SWSM L1 surface soil moisture std dev | m3/m3 | V3HE | [0.004743, 0.1431] | 6.3% |
| `swsm_l1_sd_v3pm10` | SWSM L1表层土壤湿度标准差 | SWSM L1 surface soil moisture std dev | m3/m3 | V3pm10 | [0.004024, 0.1262] | 6.3% |
| `swsm_l1_sd_v3pre30` | SWSM L1表层土壤湿度标准差 | SWSM L1 surface soil moisture std dev | m3/m3 | V3pre30 | [0.003962, 0.1198] | 6.3% |
| `swsm_l3_max` | SWSM L3深层土壤湿度最大值 | SWSM L3 deep soil moisture max | m3/m3 | Full | [0.02, 0.62] | 6.3% |
| `swsm_l3_max_hema` | SWSM L3深层土壤湿度最大值 | SWSM L3 deep soil moisture max | m3/m3 | HEMA | [0.02, 0.61] | 6.3% |
| `swsm_l3_max_hepm10` | SWSM L3深层土壤湿度最大值 | SWSM L3 deep soil moisture max | m3/m3 | HEpm10 | [0.02, 0.61] | 6.3% |
| `swsm_l3_max_v3he` | SWSM L3深层土壤湿度最大值 | SWSM L3 deep soil moisture max | m3/m3 | V3HE | [0.02, 0.62] | 6.3% |
| `swsm_l3_max_v3pm10` | SWSM L3深层土壤湿度最大值 | SWSM L3 deep soil moisture max | m3/m3 | V3pm10 | [0.02, 0.61] | 6.3% |
| `swsm_l3_max_v3pre30` | SWSM L3深层土壤湿度最大值 | SWSM L3 deep soil moisture max | m3/m3 | V3pre30 | [0.02, 0.55] | 6.3% |
| `swsm_l3_mean` | SWSM L3深层土壤湿度均值 | SWSM L3 deep soil moisture mean | m3/m3 | Full | [0.01325, 0.5303] | 6.3% |
| `swsm_l3_mean_hema` | SWSM L3深层土壤湿度均值 | SWSM L3 deep soil moisture mean | m3/m3 | HEMA | [0.01296, 0.5837] | 6.3% |
| `swsm_l3_mean_hepm10` | SWSM L3深层土壤湿度均值 | SWSM L3 deep soil moisture mean | m3/m3 | HEpm10 | [0.011, 0.5729] | 6.3% |
| `swsm_l3_mean_v3he` | SWSM L3深层土壤湿度均值 | SWSM L3 deep soil moisture mean | m3/m3 | V3HE | [0.01341, 0.5568] | 6.3% |
| `swsm_l3_mean_v3pm10` | SWSM L3深层土壤湿度均值 | SWSM L3 deep soil moisture mean | m3/m3 | V3pm10 | [0.011, 0.5133] | 6.3% |
| `swsm_l3_mean_v3pre30` | SWSM L3深层土壤湿度均值 | SWSM L3 deep soil moisture mean | m3/m3 | V3pre30 | [0.013, 0.5177] | 6.3% |
| `swsm_l3_min` | SWSM L3深层土壤湿度最小值 | SWSM L3 deep soil moisture min | m3/m3 | Full | [0.01, 0.49] | 6.3% |
| `swsm_l3_min_hema` | SWSM L3深层土壤湿度最小值 | SWSM L3 deep soil moisture min | m3/m3 | HEMA | [0.01, 0.55] | 6.3% |
| `swsm_l3_min_hepm10` | SWSM L3深层土壤湿度最小值 | SWSM L3 deep soil moisture min | m3/m3 | HEpm10 | [0.01, 0.52] | 6.3% |
| `swsm_l3_min_v3he` | SWSM L3深层土壤湿度最小值 | SWSM L3 deep soil moisture min | m3/m3 | V3HE | [0.01, 0.51] | 6.3% |
| `swsm_l3_min_v3pm10` | SWSM L3深层土壤湿度最小值 | SWSM L3 deep soil moisture min | m3/m3 | V3pm10 | [0.01, 0.49] | 6.3% |
| `swsm_l3_min_v3pre30` | SWSM L3深层土壤湿度最小值 | SWSM L3 deep soil moisture min | m3/m3 | V3pre30 | [0.01, 0.5] | 6.3% |
| `swsm_l3_sd` | SWSM L3深层土壤湿度标准差 | SWSM L3 deep soil moisture std dev | m3/m3 | Full | [0.002599, 0.1277] | 6.3% |
| `swsm_l3_sd_hema` | SWSM L3深层土壤湿度标准差 | SWSM L3 deep soil moisture std dev | m3/m3 | HEMA | [0.001443, 0.08489] | 6.3% |
| `swsm_l3_sd_hepm10` | SWSM L3深层土壤湿度标准差 | SWSM L3 deep soil moisture std dev | m3/m3 | HEpm10 | [0, 0.1053] | 6.3% |
| `swsm_l3_sd_v3he` | SWSM L3深层土壤湿度标准差 | SWSM L3 deep soil moisture std dev | m3/m3 | V3HE | [0.001179, 0.1156] | 6.3% |
| `swsm_l3_sd_v3pm10` | SWSM L3深层土壤湿度标准差 | SWSM L3 deep soil moisture std dev | m3/m3 | V3pm10 | [0, 0.07497] | 6.3% |
| `swsm_l3_sd_v3pre30` | SWSM L3深层土壤湿度标准差 | SWSM L3 deep soil moisture std dev | m3/m3 | V3pre30 | [0, 0.06676] | 6.3% |
| `wetdays_swsm_l1_ge_p80` | SWSM L1表层土壤湿度高于本地历史P80的日数 | Days with SWSM L1 surface soil moisture >= local historical P80 | days | Full | [0, 163] | 6.3% |
| `wetdays_swsm_l1_ge_p80_hema` | SWSM L1表层土壤湿度高于本地历史P80的日数 | Days with SWSM L1 surface soil moisture >= local historical P80 | days | HEMA | [0, 91] | 6.3% |
| `wetdays_swsm_l1_ge_p80_hepm10` | SWSM L1表层土壤湿度高于本地历史P80的日数 | Days with SWSM L1 surface soil moisture >= local historical P80 | days | HEpm10 | [0, 21] | 6.3% |
| `wetdays_swsm_l1_ge_p80_v3he` | SWSM L1表层土壤湿度高于本地历史P80的日数 | Days with SWSM L1 surface soil moisture >= local historical P80 | days | V3HE | [0, 77] | 6.3% |
| `wetdays_swsm_l1_ge_p80_v3pm10` | SWSM L1表层土壤湿度高于本地历史P80的日数 | Days with SWSM L1 surface soil moisture >= local historical P80 | days | V3pm10 | [0, 21] | 6.3% |
| `wetdays_swsm_l1_ge_p80_v3pre30` | SWSM L1表层土壤湿度高于本地历史P80的日数 | Days with SWSM L1 surface soil moisture >= local historical P80 | days | V3pre30 | [0, 31] | 6.3% |
| `wetdays_swsm_l1_ge_p90` | SWSM L1表层土壤湿度高于本地历史P90的日数 | Days with SWSM L1 surface soil moisture >= local historical P90 | days | Full | [0, 103] | 6.3% |
| `wetdays_swsm_l1_ge_p90_hema` | SWSM L1表层土壤湿度高于本地历史P90的日数 | Days with SWSM L1 surface soil moisture >= local historical P90 | days | HEMA | [0, 72] | 6.3% |
| `wetdays_swsm_l1_ge_p90_hepm10` | SWSM L1表层土壤湿度高于本地历史P90的日数 | Days with SWSM L1 surface soil moisture >= local historical P90 | days | HEpm10 | [0, 21] | 6.3% |
| `wetdays_swsm_l1_ge_p90_v3he` | SWSM L1表层土壤湿度高于本地历史P90的日数 | Days with SWSM L1 surface soil moisture >= local historical P90 | days | V3HE | [0, 62] | 6.3% |
| `wetdays_swsm_l1_ge_p90_v3pm10` | SWSM L1表层土壤湿度高于本地历史P90的日数 | Days with SWSM L1 surface soil moisture >= local historical P90 | days | V3pm10 | [0, 21] | 6.3% |
| `wetdays_swsm_l1_ge_p90_v3pre30` | SWSM L1表层土壤湿度高于本地历史P90的日数 | Days with SWSM L1 surface soil moisture >= local historical P90 | days | V3pre30 | [0, 31] | 6.3% |
| `wetdays_swsm_l3_ge_p80` | SWSM L3深层土壤湿度高于本地历史P80的日数 | Days with SWSM L3 deep soil moisture >= local historical P80 | days | Full | [0, 183] | 6.3% |
| `wetdays_swsm_l3_ge_p80_hema` | SWSM L3深层土壤湿度高于本地历史P80的日数 | Days with SWSM L3 deep soil moisture >= local historical P80 | days | HEMA | [0, 93] | 6.3% |
| `wetdays_swsm_l3_ge_p80_hepm10` | SWSM L3深层土壤湿度高于本地历史P80的日数 | Days with SWSM L3 deep soil moisture >= local historical P80 | days | HEpm10 | [0, 21] | 6.3% |
| `wetdays_swsm_l3_ge_p80_v3he` | SWSM L3深层土壤湿度高于本地历史P80的日数 | Days with SWSM L3 deep soil moisture >= local historical P80 | days | V3HE | [0, 99] | 6.3% |
| `wetdays_swsm_l3_ge_p80_v3pm10` | SWSM L3深层土壤湿度高于本地历史P80的日数 | Days with SWSM L3 deep soil moisture >= local historical P80 | days | V3pm10 | [0, 21] | 6.3% |
| `wetdays_swsm_l3_ge_p80_v3pre30` | SWSM L3深层土壤湿度高于本地历史P80的日数 | Days with SWSM L3 deep soil moisture >= local historical P80 | days | V3pre30 | [0, 31] | 6.3% |
| `wetdays_swsm_l3_ge_p90` | SWSM L3深层土壤湿度高于本地历史P90的日数 | Days with SWSM L3 deep soil moisture >= local historical P90 | days | Full | [0, 162] | 6.3% |
| `wetdays_swsm_l3_ge_p90_hema` | SWSM L3深层土壤湿度高于本地历史P90的日数 | Days with SWSM L3 deep soil moisture >= local historical P90 | days | HEMA | [0, 83] | 6.3% |
| `wetdays_swsm_l3_ge_p90_hepm10` | SWSM L3深层土壤湿度高于本地历史P90的日数 | Days with SWSM L3 deep soil moisture >= local historical P90 | days | HEpm10 | [0, 21] | 6.3% |
| `wetdays_swsm_l3_ge_p90_v3he` | SWSM L3深层土壤湿度高于本地历史P90的日数 | Days with SWSM L3 deep soil moisture >= local historical P90 | days | V3HE | [0, 87] | 6.3% |
| `wetdays_swsm_l3_ge_p90_v3pm10` | SWSM L3深层土壤湿度高于本地历史P90的日数 | Days with SWSM L3 deep soil moisture >= local historical P90 | days | V3pm10 | [0, 21] | 6.3% |
| `wetdays_swsm_l3_ge_p90_v3pre30` | SWSM L3深层土壤湿度高于本地历史P90的日数 | Days with SWSM L3 deep soil moisture >= local historical P90 | days | V3pre30 | [0, 31] | 6.3% |
| `wetexcess_swsm_l1_ge_p80` | SWSM L1表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for SWSM L1 surface soil moisture | m3/m3 | Full | [0, 0.05073] | 6.3% |
| `wetexcess_swsm_l1_ge_p80_hema` | SWSM L1表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for SWSM L1 surface soil moisture | m3/m3 | HEMA | [0, 0.1406] | 6.3% |
| `wetexcess_swsm_l1_ge_p80_hepm10` | SWSM L1表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for SWSM L1 surface soil moisture | m3/m3 | HEpm10 | [0, 0.1136] | 6.3% |
| `wetexcess_swsm_l1_ge_p80_v3he` | SWSM L1表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for SWSM L1 surface soil moisture | m3/m3 | V3HE | [0, 0.07683] | 6.3% |
| `wetexcess_swsm_l1_ge_p80_v3pm10` | SWSM L1表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for SWSM L1 surface soil moisture | m3/m3 | V3pm10 | [0, 0.1057] | 6.3% |
| `wetexcess_swsm_l1_ge_p80_v3pre30` | SWSM L1表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for SWSM L1 surface soil moisture | m3/m3 | V3pre30 | [0, 0.08645] | 6.3% |
| `wetexcess_swsm_l1_ge_p90` | SWSM L1表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for SWSM L1 surface soil moisture | m3/m3 | Full | [0, 0.04273] | 6.3% |
| `wetexcess_swsm_l1_ge_p90_hema` | SWSM L1表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for SWSM L1 surface soil moisture | m3/m3 | HEMA | [0, 0.1068] | 6.3% |
| `wetexcess_swsm_l1_ge_p90_hepm10` | SWSM L1表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for SWSM L1 surface soil moisture | m3/m3 | HEpm10 | [0, 0.07095] | 6.3% |
| `wetexcess_swsm_l1_ge_p90_v3he` | SWSM L1表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for SWSM L1 surface soil moisture | m3/m3 | V3HE | [0, 0.04171] | 6.3% |
| `wetexcess_swsm_l1_ge_p90_v3pm10` | SWSM L1表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for SWSM L1 surface soil moisture | m3/m3 | V3pm10 | [0, 0.05952] | 6.3% |
| `wetexcess_swsm_l1_ge_p90_v3pre30` | SWSM L1表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for SWSM L1 surface soil moisture | m3/m3 | V3pre30 | [0, 0.06032] | 6.3% |
| `wetexcess_swsm_l3_ge_p80` | SWSM L3深层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for SWSM L3 deep soil moisture | m3/m3 | Full | [0, 0.06685] | 6.3% |
| `wetexcess_swsm_l3_ge_p80_hema` | SWSM L3深层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for SWSM L3 deep soil moisture | m3/m3 | HEMA | [0, 0.1353] | 6.3% |
| `wetexcess_swsm_l3_ge_p80_hepm10` | SWSM L3深层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for SWSM L3 deep soil moisture | m3/m3 | HEpm10 | [0, 0.1257] | 6.3% |
| `wetexcess_swsm_l3_ge_p80_v3he` | SWSM L3深层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for SWSM L3 deep soil moisture | m3/m3 | V3HE | [0, 0.09366] | 6.3% |
| `wetexcess_swsm_l3_ge_p80_v3pm10` | SWSM L3深层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for SWSM L3 deep soil moisture | m3/m3 | V3pm10 | [0, 0.0681] | 6.3% |
| `wetexcess_swsm_l3_ge_p80_v3pre30` | SWSM L3深层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for SWSM L3 deep soil moisture | m3/m3 | V3pre30 | [0, 0.08484] | 6.3% |
| `wetexcess_swsm_l3_ge_p90` | SWSM L3深层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for SWSM L3 deep soil moisture | m3/m3 | Full | [0, 0.03825] | 6.3% |
| `wetexcess_swsm_l3_ge_p90_hema` | SWSM L3深层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for SWSM L3 deep soil moisture | m3/m3 | HEMA | [0, 0.09941] | 6.3% |
| `wetexcess_swsm_l3_ge_p90_hepm10` | SWSM L3深层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for SWSM L3 deep soil moisture | m3/m3 | HEpm10 | [0, 0.07776] | 6.3% |
| `wetexcess_swsm_l3_ge_p90_v3he` | SWSM L3深层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for SWSM L3 deep soil moisture | m3/m3 | V3HE | [0, 0.074] | 6.3% |
| `wetexcess_swsm_l3_ge_p90_v3pm10` | SWSM L3深层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for SWSM L3 deep soil moisture | m3/m3 | V3pm10 | [0, 0.0581] | 6.3% |
| `wetexcess_swsm_l3_ge_p90_v3pre30` | SWSM L3深层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for SWSM L3 deep soil moisture | m3/m3 | V3pre30 | [0, 0.04484] | 6.3% |
| `wetshare_swsm_l1_ge_p80` | SWSM L1表层土壤湿度高于本地历史P80的日占比 | Share of valid days with SWSM L1 surface soil moisture >= local historical P80 | 0-1 | Full | [0, 0.8865] | 6.3% |
| `wetshare_swsm_l1_ge_p80_hema` | SWSM L1表层土壤湿度高于本地历史P80的日占比 | Share of valid days with SWSM L1 surface soil moisture >= local historical P80 | 0-1 | HEMA | [0, 1] | 6.3% |
| `wetshare_swsm_l1_ge_p80_hepm10` | SWSM L1表层土壤湿度高于本地历史P80的日占比 | Share of valid days with SWSM L1 surface soil moisture >= local historical P80 | 0-1 | HEpm10 | [0, 1] | 6.3% |
| `wetshare_swsm_l1_ge_p80_v3he` | SWSM L1表层土壤湿度高于本地历史P80的日占比 | Share of valid days with SWSM L1 surface soil moisture >= local historical P80 | 0-1 | V3HE | [0, 1] | 6.3% |
| `wetshare_swsm_l1_ge_p80_v3pm10` | SWSM L1表层土壤湿度高于本地历史P80的日占比 | Share of valid days with SWSM L1 surface soil moisture >= local historical P80 | 0-1 | V3pm10 | [0, 1] | 6.3% |
| `wetshare_swsm_l1_ge_p80_v3pre30` | SWSM L1表层土壤湿度高于本地历史P80的日占比 | Share of valid days with SWSM L1 surface soil moisture >= local historical P80 | 0-1 | V3pre30 | [0, 1] | 6.3% |
| `wetshare_swsm_l1_ge_p90` | SWSM L1表层土壤湿度高于本地历史P90的日占比 | Share of valid days with SWSM L1 surface soil moisture >= local historical P90 | 0-1 | Full | [0, 0.7845] | 6.3% |
| `wetshare_swsm_l1_ge_p90_hema` | SWSM L1表层土壤湿度高于本地历史P90的日占比 | Share of valid days with SWSM L1 surface soil moisture >= local historical P90 | 0-1 | HEMA | [0, 1] | 6.3% |
| `wetshare_swsm_l1_ge_p90_hepm10` | SWSM L1表层土壤湿度高于本地历史P90的日占比 | Share of valid days with SWSM L1 surface soil moisture >= local historical P90 | 0-1 | HEpm10 | [0, 1] | 6.3% |
| `wetshare_swsm_l1_ge_p90_v3he` | SWSM L1表层土壤湿度高于本地历史P90的日占比 | Share of valid days with SWSM L1 surface soil moisture >= local historical P90 | 0-1 | V3HE | [0, 0.878] | 6.3% |
| `wetshare_swsm_l1_ge_p90_v3pm10` | SWSM L1表层土壤湿度高于本地历史P90的日占比 | Share of valid days with SWSM L1 surface soil moisture >= local historical P90 | 0-1 | V3pm10 | [0, 1] | 6.3% |
| `wetshare_swsm_l1_ge_p90_v3pre30` | SWSM L1表层土壤湿度高于本地历史P90的日占比 | Share of valid days with SWSM L1 surface soil moisture >= local historical P90 | 0-1 | V3pre30 | [0, 1] | 6.3% |
| `wetshare_swsm_l3_ge_p80` | SWSM L3深层土壤湿度高于本地历史P80的日占比 | Share of valid days with SWSM L3 deep soil moisture >= local historical P80 | 0-1 | Full | [0, 1] | 6.3% |
| `wetshare_swsm_l3_ge_p80_hema` | SWSM L3深层土壤湿度高于本地历史P80的日占比 | Share of valid days with SWSM L3 deep soil moisture >= local historical P80 | 0-1 | HEMA | [0, 1] | 6.3% |
| `wetshare_swsm_l3_ge_p80_hepm10` | SWSM L3深层土壤湿度高于本地历史P80的日占比 | Share of valid days with SWSM L3 deep soil moisture >= local historical P80 | 0-1 | HEpm10 | [0, 1] | 6.3% |
| `wetshare_swsm_l3_ge_p80_v3he` | SWSM L3深层土壤湿度高于本地历史P80的日占比 | Share of valid days with SWSM L3 deep soil moisture >= local historical P80 | 0-1 | V3HE | [0, 1] | 6.3% |
| `wetshare_swsm_l3_ge_p80_v3pm10` | SWSM L3深层土壤湿度高于本地历史P80的日占比 | Share of valid days with SWSM L3 deep soil moisture >= local historical P80 | 0-1 | V3pm10 | [0, 1] | 6.3% |
| `wetshare_swsm_l3_ge_p80_v3pre30` | SWSM L3深层土壤湿度高于本地历史P80的日占比 | Share of valid days with SWSM L3 deep soil moisture >= local historical P80 | 0-1 | V3pre30 | [0, 1] | 6.3% |
| `wetshare_swsm_l3_ge_p90` | SWSM L3深层土壤湿度高于本地历史P90的日占比 | Share of valid days with SWSM L3 deep soil moisture >= local historical P90 | 0-1 | Full | [0, 0.9661] | 6.3% |
| `wetshare_swsm_l3_ge_p90_hema` | SWSM L3深层土壤湿度高于本地历史P90的日占比 | Share of valid days with SWSM L3 deep soil moisture >= local historical P90 | 0-1 | HEMA | [0, 1] | 6.3% |
| `wetshare_swsm_l3_ge_p90_hepm10` | SWSM L3深层土壤湿度高于本地历史P90的日占比 | Share of valid days with SWSM L3 deep soil moisture >= local historical P90 | 0-1 | HEpm10 | [0, 1] | 6.3% |
| `wetshare_swsm_l3_ge_p90_v3he` | SWSM L3深层土壤湿度高于本地历史P90的日占比 | Share of valid days with SWSM L3 deep soil moisture >= local historical P90 | 0-1 | V3HE | [0, 1] | 6.3% |
| `wetshare_swsm_l3_ge_p90_v3pm10` | SWSM L3深层土壤湿度高于本地历史P90的日占比 | Share of valid days with SWSM L3 deep soil moisture >= local historical P90 | 0-1 | V3pm10 | [0, 1] | 6.3% |
| `wetshare_swsm_l3_ge_p90_v3pre30` | SWSM L3深层土壤湿度高于本地历史P90的日占比 | Share of valid days with SWSM L3 deep soil moisture >= local historical P90 | 0-1 | V3pre30 | [0, 1] | 6.3% |

### pooled-state

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `drydeficit_pl_swsm_l1_le_p25` | SWSM L1表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for SWSM L1 surface soil moisture | m3/m3 | Full | [0, 0.126] | 6.3% |
| `drydeficit_pl_swsm_l1_le_p25_hema` | SWSM L1表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for SWSM L1 surface soil moisture | m3/m3 | HEMA | [0, 0.17] | 6.3% |
| `drydeficit_pl_swsm_l1_le_p25_hepm10` | SWSM L1表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for SWSM L1 surface soil moisture | m3/m3 | HEpm10 | [0, 0.1564] | 6.3% |
| `drydeficit_pl_swsm_l1_le_p25_v3he` | SWSM L1表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for SWSM L1 surface soil moisture | m3/m3 | V3HE | [0, 0.128] | 6.3% |
| `drydeficit_pl_swsm_l1_le_p25_v3pm10` | SWSM L1表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for SWSM L1 surface soil moisture | m3/m3 | V3pm10 | [0, 0.1325] | 6.3% |
| `drydeficit_pl_swsm_l1_le_p25_v3pre30` | SWSM L1表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for SWSM L1 surface soil moisture | m3/m3 | V3pre30 | [0, 0.127] | 6.3% |
| `drydeficit_pl_swsm_l3_le_p25` | SWSM L3深层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for SWSM L3 deep soil moisture | m3/m3 | Full | [0, 0.1968] | 6.3% |
| `drydeficit_pl_swsm_l3_le_p25_hema` | SWSM L3深层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for SWSM L3 deep soil moisture | m3/m3 | HEMA | [0, 0.217] | 6.3% |
| `drydeficit_pl_swsm_l3_le_p25_hepm10` | SWSM L3深层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for SWSM L3 deep soil moisture | m3/m3 | HEpm10 | [0, 0.199] | 6.3% |
| `drydeficit_pl_swsm_l3_le_p25_v3he` | SWSM L3深层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for SWSM L3 deep soil moisture | m3/m3 | V3HE | [0, 0.1866] | 6.3% |
| `drydeficit_pl_swsm_l3_le_p25_v3pm10` | SWSM L3深层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for SWSM L3 deep soil moisture | m3/m3 | V3pm10 | [0, 0.189] | 6.3% |
| `drydeficit_pl_swsm_l3_le_p25_v3pre30` | SWSM L3深层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for SWSM L3 deep soil moisture | m3/m3 | V3pre30 | [0, 0.187] | 6.3% |
| `dryshare_pl_swsm_l1_le_p25` | SWSM L1表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with SWSM L1 surface soil moisture <= pooled window-specific threshold P25 | 0-1 | Full | [0, 1] | 6.3% |
| `dryshare_pl_swsm_l1_le_p25_hema` | SWSM L1表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with SWSM L1 surface soil moisture <= pooled window-specific threshold P25 | 0-1 | HEMA | [0, 1] | 6.3% |
| `dryshare_pl_swsm_l1_le_p25_hepm10` | SWSM L1表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with SWSM L1 surface soil moisture <= pooled window-specific threshold P25 | 0-1 | HEpm10 | [0, 1] | 6.3% |
| `dryshare_pl_swsm_l1_le_p25_v3he` | SWSM L1表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with SWSM L1 surface soil moisture <= pooled window-specific threshold P25 | 0-1 | V3HE | [0, 1] | 6.3% |
| `dryshare_pl_swsm_l1_le_p25_v3pm10` | SWSM L1表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with SWSM L1 surface soil moisture <= pooled window-specific threshold P25 | 0-1 | V3pm10 | [0, 1] | 6.3% |
| `dryshare_pl_swsm_l1_le_p25_v3pre30` | SWSM L1表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with SWSM L1 surface soil moisture <= pooled window-specific threshold P25 | 0-1 | V3pre30 | [0, 1] | 6.3% |
| `dryshare_pl_swsm_l3_le_p25` | SWSM L3深层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with SWSM L3 deep soil moisture <= pooled window-specific threshold P25 | 0-1 | Full | [0, 1] | 6.3% |
| `dryshare_pl_swsm_l3_le_p25_hema` | SWSM L3深层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with SWSM L3 deep soil moisture <= pooled window-specific threshold P25 | 0-1 | HEMA | [0, 1] | 6.3% |
| `dryshare_pl_swsm_l3_le_p25_hepm10` | SWSM L3深层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with SWSM L3 deep soil moisture <= pooled window-specific threshold P25 | 0-1 | HEpm10 | [0, 1] | 6.3% |
| `dryshare_pl_swsm_l3_le_p25_v3he` | SWSM L3深层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with SWSM L3 deep soil moisture <= pooled window-specific threshold P25 | 0-1 | V3HE | [0, 1] | 6.3% |
| `dryshare_pl_swsm_l3_le_p25_v3pm10` | SWSM L3深层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with SWSM L3 deep soil moisture <= pooled window-specific threshold P25 | 0-1 | V3pm10 | [0, 1] | 6.3% |
| `dryshare_pl_swsm_l3_le_p25_v3pre30` | SWSM L3深层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with SWSM L3 deep soil moisture <= pooled window-specific threshold P25 | 0-1 | V3pre30 | [0, 1] | 6.3% |
| `wetexcess_pl_swsm_l1_ge_p75` | SWSM L1表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for SWSM L1 surface soil moisture | m3/m3 | Full | [0, 0.199] | 6.3% |
| `wetexcess_pl_swsm_l1_ge_p75_hema` | SWSM L1表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for SWSM L1 surface soil moisture | m3/m3 | HEMA | [0, 0.198] | 6.3% |
| `wetexcess_pl_swsm_l1_ge_p75_hepm10` | SWSM L1表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for SWSM L1 surface soil moisture | m3/m3 | HEpm10 | [0, 0.2219] | 6.3% |
| `wetexcess_pl_swsm_l1_ge_p75_v3he` | SWSM L1表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for SWSM L1 surface soil moisture | m3/m3 | V3HE | [0, 0.2169] | 6.3% |
| `wetexcess_pl_swsm_l1_ge_p75_v3pm10` | SWSM L1表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for SWSM L1 surface soil moisture | m3/m3 | V3pm10 | [0, 0.2448] | 6.3% |
| `wetexcess_pl_swsm_l1_ge_p75_v3pre30` | SWSM L1表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for SWSM L1 surface soil moisture | m3/m3 | V3pre30 | [0, 0.2452] | 6.3% |
| `wetexcess_pl_swsm_l3_ge_p75` | SWSM L3深层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for SWSM L3 deep soil moisture | m3/m3 | Full | [0, 0.2103] | 6.3% |
| `wetexcess_pl_swsm_l3_ge_p75_hema` | SWSM L3深层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for SWSM L3 deep soil moisture | m3/m3 | HEMA | [0, 0.2537] | 6.3% |
| `wetexcess_pl_swsm_l3_ge_p75_hepm10` | SWSM L3深层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for SWSM L3 deep soil moisture | m3/m3 | HEpm10 | [0, 0.2429] | 6.3% |
| `wetexcess_pl_swsm_l3_ge_p75_v3he` | SWSM L3深层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for SWSM L3 deep soil moisture | m3/m3 | V3HE | [0, 0.2368] | 6.3% |
| `wetexcess_pl_swsm_l3_ge_p75_v3pm10` | SWSM L3深层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for SWSM L3 deep soil moisture | m3/m3 | V3pm10 | [0, 0.1933] | 6.3% |
| `wetexcess_pl_swsm_l3_ge_p75_v3pre30` | SWSM L3深层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for SWSM L3 deep soil moisture | m3/m3 | V3pre30 | [0, 0.1977] | 6.3% |
| `wetshare_pl_swsm_l1_ge_p75` | SWSM L1表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with SWSM L1 surface soil moisture >= pooled window-specific threshold P75 | 0-1 | Full | [0, 1] | 6.3% |
| `wetshare_pl_swsm_l1_ge_p75_hema` | SWSM L1表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with SWSM L1 surface soil moisture >= pooled window-specific threshold P75 | 0-1 | HEMA | [0, 1] | 6.3% |
| `wetshare_pl_swsm_l1_ge_p75_hepm10` | SWSM L1表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with SWSM L1 surface soil moisture >= pooled window-specific threshold P75 | 0-1 | HEpm10 | [0, 1] | 6.3% |
| `wetshare_pl_swsm_l1_ge_p75_v3he` | SWSM L1表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with SWSM L1 surface soil moisture >= pooled window-specific threshold P75 | 0-1 | V3HE | [0, 1] | 6.3% |
| `wetshare_pl_swsm_l1_ge_p75_v3pm10` | SWSM L1表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with SWSM L1 surface soil moisture >= pooled window-specific threshold P75 | 0-1 | V3pm10 | [0, 1] | 6.3% |
| `wetshare_pl_swsm_l1_ge_p75_v3pre30` | SWSM L1表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with SWSM L1 surface soil moisture >= pooled window-specific threshold P75 | 0-1 | V3pre30 | [0, 1] | 6.3% |
| `wetshare_pl_swsm_l3_ge_p75` | SWSM L3深层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with SWSM L3 deep soil moisture >= pooled window-specific threshold P75 | 0-1 | Full | [0, 1] | 6.3% |
| `wetshare_pl_swsm_l3_ge_p75_hema` | SWSM L3深层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with SWSM L3 deep soil moisture >= pooled window-specific threshold P75 | 0-1 | HEMA | [0, 1] | 6.3% |
| `wetshare_pl_swsm_l3_ge_p75_hepm10` | SWSM L3深层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with SWSM L3 deep soil moisture >= pooled window-specific threshold P75 | 0-1 | HEpm10 | [0, 1] | 6.3% |
| `wetshare_pl_swsm_l3_ge_p75_v3he` | SWSM L3深层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with SWSM L3 deep soil moisture >= pooled window-specific threshold P75 | 0-1 | V3HE | [0, 1] | 6.3% |
| `wetshare_pl_swsm_l3_ge_p75_v3pm10` | SWSM L3深层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with SWSM L3 deep soil moisture >= pooled window-specific threshold P75 | 0-1 | V3pm10 | [0, 1] | 6.3% |
| `wetshare_pl_swsm_l3_ge_p75_v3pre30` | SWSM L3深层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with SWSM L3 deep soil moisture >= pooled window-specific threshold P75 | 0-1 | V3pre30 | [0, 1] | 6.3% |

### maize-zone-state

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `drydeficit_mz_swsm_l1_le_p25` | SWSM L1表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for SWSM L1 surface soil moisture | m3/m3 | Full | [0, 0.1659] | 6.3% |
| `drydeficit_mz_swsm_l1_le_p25_hema` | SWSM L1表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for SWSM L1 surface soil moisture | m3/m3 | HEMA | [0, 0.1511] | 6.3% |
| `drydeficit_mz_swsm_l1_le_p25_hepm10` | SWSM L1表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for SWSM L1 surface soil moisture | m3/m3 | HEpm10 | [0, 0.16] | 6.3% |
| `drydeficit_mz_swsm_l1_le_p25_v3he` | SWSM L1表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for SWSM L1 surface soil moisture | m3/m3 | V3HE | [0, 0.1913] | 6.3% |
| `drydeficit_mz_swsm_l1_le_p25_v3pm10` | SWSM L1表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for SWSM L1 surface soil moisture | m3/m3 | V3pm10 | [0, 0.2125] | 6.3% |
| `drydeficit_mz_swsm_l1_le_p25_v3pre30` | SWSM L1表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for SWSM L1 surface soil moisture | m3/m3 | V3pre30 | [0, 0.217] | 6.3% |
| `drydeficit_mz_swsm_l3_le_p25` | SWSM L3深层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for SWSM L3 deep soil moisture | m3/m3 | Full | [0, 0.2128] | 6.3% |
| `drydeficit_mz_swsm_l3_le_p25_hema` | SWSM L3深层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for SWSM L3 deep soil moisture | m3/m3 | HEMA | [0, 0.1942] | 6.3% |
| `drydeficit_mz_swsm_l3_le_p25_hepm10` | SWSM L3深层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for SWSM L3 deep soil moisture | m3/m3 | HEpm10 | [0, 0.2181] | 6.3% |
| `drydeficit_mz_swsm_l3_le_p25_v3he` | SWSM L3深层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for SWSM L3 deep soil moisture | m3/m3 | V3HE | [0, 0.2424] | 6.3% |
| `drydeficit_mz_swsm_l3_le_p25_v3pm10` | SWSM L3深层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for SWSM L3 deep soil moisture | m3/m3 | V3pm10 | [0, 0.2675] | 6.3% |
| `drydeficit_mz_swsm_l3_le_p25_v3pre30` | SWSM L3深层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for SWSM L3 deep soil moisture | m3/m3 | V3pre30 | [0, 0.2664] | 6.3% |
| `dryshare_mz_swsm_l1_le_p25` | SWSM L1表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with SWSM L1 surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | Full | [0, 1] | 6.3% |
| `dryshare_mz_swsm_l1_le_p25_hema` | SWSM L1表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with SWSM L1 surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | HEMA | [0, 1] | 6.3% |
| `dryshare_mz_swsm_l1_le_p25_hepm10` | SWSM L1表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with SWSM L1 surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | HEpm10 | [0, 1] | 6.3% |
| `dryshare_mz_swsm_l1_le_p25_v3he` | SWSM L1表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with SWSM L1 surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3HE | [0, 1] | 6.3% |
| `dryshare_mz_swsm_l1_le_p25_v3pm10` | SWSM L1表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with SWSM L1 surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3pm10 | [0, 1] | 6.3% |
| `dryshare_mz_swsm_l1_le_p25_v3pre30` | SWSM L1表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with SWSM L1 surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3pre30 | [0, 1] | 6.3% |
| `dryshare_mz_swsm_l3_le_p25` | SWSM L3深层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with SWSM L3 deep soil moisture <= maize-zone-specific threshold P25 | 0-1 | Full | [0, 1] | 6.3% |
| `dryshare_mz_swsm_l3_le_p25_hema` | SWSM L3深层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with SWSM L3 deep soil moisture <= maize-zone-specific threshold P25 | 0-1 | HEMA | [0, 1] | 6.3% |
| `dryshare_mz_swsm_l3_le_p25_hepm10` | SWSM L3深层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with SWSM L3 deep soil moisture <= maize-zone-specific threshold P25 | 0-1 | HEpm10 | [0, 1] | 6.3% |
| `dryshare_mz_swsm_l3_le_p25_v3he` | SWSM L3深层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with SWSM L3 deep soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3HE | [0, 1] | 6.3% |
| `dryshare_mz_swsm_l3_le_p25_v3pm10` | SWSM L3深层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with SWSM L3 deep soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3pm10 | [0, 1] | 6.3% |
| `dryshare_mz_swsm_l3_le_p25_v3pre30` | SWSM L3深层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with SWSM L3 deep soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3pre30 | [0, 1] | 6.3% |
| `wetexcess_mz_swsm_l1_ge_p75` | SWSM L1表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for SWSM L1 surface soil moisture | m3/m3 | Full | [0, 0.1386] | 6.3% |
| `wetexcess_mz_swsm_l1_ge_p75_hema` | SWSM L1表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for SWSM L1 surface soil moisture | m3/m3 | HEMA | [0, 0.1769] | 6.3% |
| `wetexcess_mz_swsm_l1_ge_p75_hepm10` | SWSM L1表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for SWSM L1 surface soil moisture | m3/m3 | HEpm10 | [0, 0.17] | 6.3% |
| `wetexcess_mz_swsm_l1_ge_p75_v3he` | SWSM L1表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for SWSM L1 surface soil moisture | m3/m3 | V3HE | [0, 0.1671] | 6.3% |
| `wetexcess_mz_swsm_l1_ge_p75_v3pm10` | SWSM L1表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for SWSM L1 surface soil moisture | m3/m3 | V3pm10 | [0, 0.1729] | 6.3% |
| `wetexcess_mz_swsm_l1_ge_p75_v3pre30` | SWSM L1表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for SWSM L1 surface soil moisture | m3/m3 | V3pre30 | [0, 0.1661] | 6.3% |
| `wetexcess_mz_swsm_l3_ge_p75` | SWSM L3深层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for SWSM L3 deep soil moisture | m3/m3 | Full | [0, 0.2203] | 6.3% |
| `wetexcess_mz_swsm_l3_ge_p75_hema` | SWSM L3深层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for SWSM L3 deep soil moisture | m3/m3 | HEMA | [0, 0.2637] | 6.3% |
| `wetexcess_mz_swsm_l3_ge_p75_hepm10` | SWSM L3深层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for SWSM L3 deep soil moisture | m3/m3 | HEpm10 | [0, 0.2529] | 6.3% |
| `wetexcess_mz_swsm_l3_ge_p75_v3he` | SWSM L3深层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for SWSM L3 deep soil moisture | m3/m3 | V3HE | [0, 0.2568] | 6.3% |
| `wetexcess_mz_swsm_l3_ge_p75_v3pm10` | SWSM L3深层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for SWSM L3 deep soil moisture | m3/m3 | V3pm10 | [0, 0.2233] | 6.3% |
| `wetexcess_mz_swsm_l3_ge_p75_v3pre30` | SWSM L3深层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for SWSM L3 deep soil moisture | m3/m3 | V3pre30 | [0, 0.2277] | 6.3% |
| `wetshare_mz_swsm_l1_ge_p75` | SWSM L1表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with SWSM L1 surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | Full | [0, 1] | 6.3% |
| `wetshare_mz_swsm_l1_ge_p75_hema` | SWSM L1表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with SWSM L1 surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | HEMA | [0, 1] | 6.3% |
| `wetshare_mz_swsm_l1_ge_p75_hepm10` | SWSM L1表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with SWSM L1 surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | HEpm10 | [0, 1] | 6.3% |
| `wetshare_mz_swsm_l1_ge_p75_v3he` | SWSM L1表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with SWSM L1 surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3HE | [0, 1] | 6.3% |
| `wetshare_mz_swsm_l1_ge_p75_v3pm10` | SWSM L1表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with SWSM L1 surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3pm10 | [0, 1] | 6.3% |
| `wetshare_mz_swsm_l1_ge_p75_v3pre30` | SWSM L1表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with SWSM L1 surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3pre30 | [0, 1] | 6.3% |
| `wetshare_mz_swsm_l3_ge_p75` | SWSM L3深层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with SWSM L3 deep soil moisture >= maize-zone-specific threshold P75 | 0-1 | Full | [0, 1] | 6.3% |
| `wetshare_mz_swsm_l3_ge_p75_hema` | SWSM L3深层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with SWSM L3 deep soil moisture >= maize-zone-specific threshold P75 | 0-1 | HEMA | [0, 1] | 6.3% |
| `wetshare_mz_swsm_l3_ge_p75_hepm10` | SWSM L3深层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with SWSM L3 deep soil moisture >= maize-zone-specific threshold P75 | 0-1 | HEpm10 | [0, 1] | 6.3% |
| `wetshare_mz_swsm_l3_ge_p75_v3he` | SWSM L3深层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with SWSM L3 deep soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3HE | [0, 1] | 6.3% |
| `wetshare_mz_swsm_l3_ge_p75_v3pm10` | SWSM L3深层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with SWSM L3 deep soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3pm10 | [0, 1] | 6.3% |
| `wetshare_mz_swsm_l3_ge_p75_v3pre30` | SWSM L3深层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with SWSM L3 deep soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3pre30 | [0, 1] | 6.3% |

## 8. SM-ERA5Land (300 vars)

### baseline-local

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `drydays_era5l_swvl1_le_p10` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的日数 | Days with ERA5-Land swvl1 surface soil moisture <= local historical P10 | days | Full | [0, 156] | 0.0% |
| `drydays_era5l_swvl1_le_p10_hema` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的日数 | Days with ERA5-Land swvl1 surface soil moisture <= local historical P10 | days | HEMA | [0, 48] | 0.0% |
| `drydays_era5l_swvl1_le_p10_hepm10` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的日数 | Days with ERA5-Land swvl1 surface soil moisture <= local historical P10 | days | HEpm10 | [0, 21] | 0.0% |
| `drydays_era5l_swvl1_le_p10_v3he` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的日数 | Days with ERA5-Land swvl1 surface soil moisture <= local historical P10 | days | V3HE | [0, 86] | 0.0% |
| `drydays_era5l_swvl1_le_p10_v3pm10` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的日数 | Days with ERA5-Land swvl1 surface soil moisture <= local historical P10 | days | V3pm10 | [0, 21] | 0.0% |
| `drydays_era5l_swvl1_le_p10_v3pre30` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的日数 | Days with ERA5-Land swvl1 surface soil moisture <= local historical P10 | days | V3pre30 | [0, 31] | 0.0% |
| `drydays_era5l_swvl1_le_p20` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的日数 | Days with ERA5-Land swvl1 surface soil moisture <= local historical P20 | days | Full | [0, 156] | 0.0% |
| `drydays_era5l_swvl1_le_p20_hema` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的日数 | Days with ERA5-Land swvl1 surface soil moisture <= local historical P20 | days | HEMA | [0, 55] | 0.0% |
| `drydays_era5l_swvl1_le_p20_hepm10` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的日数 | Days with ERA5-Land swvl1 surface soil moisture <= local historical P20 | days | HEpm10 | [0, 21] | 0.0% |
| `drydays_era5l_swvl1_le_p20_v3he` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的日数 | Days with ERA5-Land swvl1 surface soil moisture <= local historical P20 | days | V3HE | [0, 86] | 0.0% |
| `drydays_era5l_swvl1_le_p20_v3pm10` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的日数 | Days with ERA5-Land swvl1 surface soil moisture <= local historical P20 | days | V3pm10 | [0, 21] | 0.0% |
| `drydays_era5l_swvl1_le_p20_v3pre30` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的日数 | Days with ERA5-Land swvl1 surface soil moisture <= local historical P20 | days | V3pre30 | [0, 31] | 0.0% |
| `drydays_era5l_swvl3_le_p10` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的日数 | Days with ERA5-Land swvl3 root-zone soil moisture <= local historical P10 | days | Full | [0, 160] | 0.0% |
| `drydays_era5l_swvl3_le_p10_hema` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的日数 | Days with ERA5-Land swvl3 root-zone soil moisture <= local historical P10 | days | HEMA | [0, 66] | 0.0% |
| `drydays_era5l_swvl3_le_p10_hepm10` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的日数 | Days with ERA5-Land swvl3 root-zone soil moisture <= local historical P10 | days | HEpm10 | [0, 21] | 0.0% |
| `drydays_era5l_swvl3_le_p10_v3he` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的日数 | Days with ERA5-Land swvl3 root-zone soil moisture <= local historical P10 | days | V3HE | [0, 94] | 0.0% |
| `drydays_era5l_swvl3_le_p10_v3pm10` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的日数 | Days with ERA5-Land swvl3 root-zone soil moisture <= local historical P10 | days | V3pm10 | [0, 21] | 0.0% |
| `drydays_era5l_swvl3_le_p10_v3pre30` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的日数 | Days with ERA5-Land swvl3 root-zone soil moisture <= local historical P10 | days | V3pre30 | [0, 31] | 0.0% |
| `drydays_era5l_swvl3_le_p20` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的日数 | Days with ERA5-Land swvl3 root-zone soil moisture <= local historical P20 | days | Full | [0, 165] | 0.0% |
| `drydays_era5l_swvl3_le_p20_hema` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的日数 | Days with ERA5-Land swvl3 root-zone soil moisture <= local historical P20 | days | HEMA | [0, 91] | 0.0% |
| `drydays_era5l_swvl3_le_p20_hepm10` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的日数 | Days with ERA5-Land swvl3 root-zone soil moisture <= local historical P20 | days | HEpm10 | [0, 21] | 0.0% |
| `drydays_era5l_swvl3_le_p20_v3he` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的日数 | Days with ERA5-Land swvl3 root-zone soil moisture <= local historical P20 | days | V3HE | [0, 98] | 0.0% |
| `drydays_era5l_swvl3_le_p20_v3pm10` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的日数 | Days with ERA5-Land swvl3 root-zone soil moisture <= local historical P20 | days | V3pm10 | [0, 21] | 0.0% |
| `drydays_era5l_swvl3_le_p20_v3pre30` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的日数 | Days with ERA5-Land swvl3 root-zone soil moisture <= local historical P20 | days | V3pre30 | [0, 31] | 0.0% |
| `drydeficit_era5l_swvl1_le_p10` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for ERA5-Land swvl1 surface soil moisture | m3/m3 | Full | [0, 0.04381] | 0.0% |
| `drydeficit_era5l_swvl1_le_p10_hema` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for ERA5-Land swvl1 surface soil moisture | m3/m3 | HEMA | [0, 0.06445] | 0.0% |
| `drydeficit_era5l_swvl1_le_p10_hepm10` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for ERA5-Land swvl1 surface soil moisture | m3/m3 | HEpm10 | [0, 0.06622] | 0.0% |
| `drydeficit_era5l_swvl1_le_p10_v3he` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3HE | [0, 0.0478] | 0.0% |
| `drydeficit_era5l_swvl1_le_p10_v3pm10` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3pm10 | [0, 0.1604] | 0.0% |
| `drydeficit_era5l_swvl1_le_p10_v3pre30` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3pre30 | [0, 0.1574] | 0.0% |
| `drydeficit_era5l_swvl1_le_p20` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for ERA5-Land swvl1 surface soil moisture | m3/m3 | Full | [0, 0.07793] | 0.0% |
| `drydeficit_era5l_swvl1_le_p20_hema` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for ERA5-Land swvl1 surface soil moisture | m3/m3 | HEMA | [0, 0.08765] | 0.0% |
| `drydeficit_era5l_swvl1_le_p20_hepm10` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for ERA5-Land swvl1 surface soil moisture | m3/m3 | HEpm10 | [0, 0.1286] | 0.0% |
| `drydeficit_era5l_swvl1_le_p20_v3he` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3HE | [0, 0.09301] | 0.0% |
| `drydeficit_era5l_swvl1_le_p20_v3pm10` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3pm10 | [0, 0.2298] | 0.0% |
| `drydeficit_era5l_swvl1_le_p20_v3pre30` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3pre30 | [0, 0.2187] | 0.0% |
| `drydeficit_era5l_swvl3_le_p10` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | Full | [0, 0.02884] | 0.0% |
| `drydeficit_era5l_swvl3_le_p10_hema` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | HEMA | [0, 0.0445] | 0.0% |
| `drydeficit_era5l_swvl3_le_p10_hepm10` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | HEpm10 | [0, 0.05505] | 0.0% |
| `drydeficit_era5l_swvl3_le_p10_v3he` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3HE | [0, 0.04653] | 0.0% |
| `drydeficit_era5l_swvl3_le_p10_v3pm10` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3pm10 | [0, 0.07292] | 0.0% |
| `drydeficit_era5l_swvl3_le_p10_v3pre30` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的平均亏缺 | Mean deficit below local historical P10 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.07875] | 0.0% |
| `drydeficit_era5l_swvl3_le_p20` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | Full | [0, 0.04451] | 0.0% |
| `drydeficit_era5l_swvl3_le_p20_hema` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | HEMA | [0, 0.05746] | 0.0% |
| `drydeficit_era5l_swvl3_le_p20_hepm10` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | HEpm10 | [0, 0.07104] | 0.0% |
| `drydeficit_era5l_swvl3_le_p20_v3he` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3HE | [0, 0.08164] | 0.0% |
| `drydeficit_era5l_swvl3_le_p20_v3pm10` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3pm10 | [0, 0.1121] | 0.0% |
| `drydeficit_era5l_swvl3_le_p20_v3pre30` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的平均亏缺 | Mean deficit below local historical P20 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.1083] | 0.0% |
| `dryshare_era5l_swvl1_le_p10` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= local historical P10 | 0-1 | Full | [0, 1] | 0.0% |
| `dryshare_era5l_swvl1_le_p10_hema` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= local historical P10 | 0-1 | HEMA | [0, 1] | 0.0% |
| `dryshare_era5l_swvl1_le_p10_hepm10` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= local historical P10 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `dryshare_era5l_swvl1_le_p10_v3he` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= local historical P10 | 0-1 | V3HE | [0, 1] | 0.0% |
| `dryshare_era5l_swvl1_le_p10_v3pm10` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= local historical P10 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `dryshare_era5l_swvl1_le_p10_v3pre30` | ERA5-Land swvl1表层土壤湿度低于本地历史P10的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= local historical P10 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `dryshare_era5l_swvl1_le_p20` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= local historical P20 | 0-1 | Full | [0, 1] | 0.0% |
| `dryshare_era5l_swvl1_le_p20_hema` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= local historical P20 | 0-1 | HEMA | [0, 1] | 0.0% |
| `dryshare_era5l_swvl1_le_p20_hepm10` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= local historical P20 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `dryshare_era5l_swvl1_le_p20_v3he` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= local historical P20 | 0-1 | V3HE | [0, 1] | 0.0% |
| `dryshare_era5l_swvl1_le_p20_v3pm10` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= local historical P20 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `dryshare_era5l_swvl1_le_p20_v3pre30` | ERA5-Land swvl1表层土壤湿度低于本地历史P20的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= local historical P20 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `dryshare_era5l_swvl3_le_p10` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= local historical P10 | 0-1 | Full | [0, 1] | 0.0% |
| `dryshare_era5l_swvl3_le_p10_hema` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= local historical P10 | 0-1 | HEMA | [0, 1] | 0.0% |
| `dryshare_era5l_swvl3_le_p10_hepm10` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= local historical P10 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `dryshare_era5l_swvl3_le_p10_v3he` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= local historical P10 | 0-1 | V3HE | [0, 1] | 0.0% |
| `dryshare_era5l_swvl3_le_p10_v3pm10` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= local historical P10 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `dryshare_era5l_swvl3_le_p10_v3pre30` | ERA5-Land swvl3根区土壤湿度低于本地历史P10的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= local historical P10 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `dryshare_era5l_swvl3_le_p20` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= local historical P20 | 0-1 | Full | [0, 1] | 0.0% |
| `dryshare_era5l_swvl3_le_p20_hema` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= local historical P20 | 0-1 | HEMA | [0, 1] | 0.0% |
| `dryshare_era5l_swvl3_le_p20_hepm10` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= local historical P20 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `dryshare_era5l_swvl3_le_p20_v3he` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= local historical P20 | 0-1 | V3HE | [0, 1] | 0.0% |
| `dryshare_era5l_swvl3_le_p20_v3pm10` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= local historical P20 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `dryshare_era5l_swvl3_le_p20_v3pre30` | ERA5-Land swvl3根区土壤湿度低于本地历史P20的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= local historical P20 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `era5l_swvl1_coverage` | ERA5-Land swvl1表层土壤湿度覆盖率 | ERA5-Land swvl1 surface soil moisture temporal coverage fraction | m3/m3 | Full | [0.7943, 1] | 0.0% |
| `era5l_swvl1_coverage_hema` | ERA5-Land swvl1表层土壤湿度覆盖率 | ERA5-Land swvl1 surface soil moisture temporal coverage fraction | m3/m3 | HEMA | [0.989, 1] | 0.0% |
| `era5l_swvl1_coverage_hepm10` | ERA5-Land swvl1表层土壤湿度覆盖率 | ERA5-Land swvl1 surface soil moisture temporal coverage fraction | m3/m3 | HEpm10 | [1, 1] | 0.0% |
| `era5l_swvl1_coverage_v3he` | ERA5-Land swvl1表层土壤湿度覆盖率 | ERA5-Land swvl1 surface soil moisture temporal coverage fraction | m3/m3 | V3HE | [0.9828, 1] | 0.0% |
| `era5l_swvl1_coverage_v3pm10` | ERA5-Land swvl1表层土壤湿度覆盖率 | ERA5-Land swvl1 surface soil moisture temporal coverage fraction | m3/m3 | V3pm10 | [0.4762, 1] | 0.0% |
| `era5l_swvl1_coverage_v3pre30` | ERA5-Land swvl1表层土壤湿度覆盖率 | ERA5-Land swvl1 surface soil moisture temporal coverage fraction | m3/m3 | V3pre30 | [0, 1] | 0.0% |
| `era5l_swvl1_max` | ERA5-Land swvl1表层土壤湿度最大值 | ERA5-Land swvl1 surface soil moisture max | m3/m3 | Full | [0, 0.7469] | 0.0% |
| `era5l_swvl1_max_hema` | ERA5-Land swvl1表层土壤湿度最大值 | ERA5-Land swvl1 surface soil moisture max | m3/m3 | HEMA | [0, 0.7469] | 0.0% |
| `era5l_swvl1_max_hepm10` | ERA5-Land swvl1表层土壤湿度最大值 | ERA5-Land swvl1 surface soil moisture max | m3/m3 | HEpm10 | [0, 0.7469] | 0.0% |
| `era5l_swvl1_max_v3he` | ERA5-Land swvl1表层土壤湿度最大值 | ERA5-Land swvl1 surface soil moisture max | m3/m3 | V3HE | [0, 0.7451] | 0.0% |
| `era5l_swvl1_max_v3pm10` | ERA5-Land swvl1表层土壤湿度最大值 | ERA5-Land swvl1 surface soil moisture max | m3/m3 | V3pm10 | [0, 0.6686] | 0.0% |
| `era5l_swvl1_max_v3pre30` | ERA5-Land swvl1表层土壤湿度最大值 | ERA5-Land swvl1 surface soil moisture max | m3/m3 | V3pre30 | [0, 0.6686] | 0.0% |
| `era5l_swvl1_mean` | ERA5-Land swvl1表层土壤湿度均值 | ERA5-Land swvl1 surface soil moisture mean | m3/m3 | Full | [0, 0.5136] | 0.0% |
| `era5l_swvl1_mean_hema` | ERA5-Land swvl1表层土壤湿度均值 | ERA5-Land swvl1 surface soil moisture mean | m3/m3 | HEMA | [0, 0.6231] | 0.0% |
| `era5l_swvl1_mean_hepm10` | ERA5-Land swvl1表层土壤湿度均值 | ERA5-Land swvl1 surface soil moisture mean | m3/m3 | HEpm10 | [0, 0.6167] | 0.0% |
| `era5l_swvl1_mean_v3he` | ERA5-Land swvl1表层土壤湿度均值 | ERA5-Land swvl1 surface soil moisture mean | m3/m3 | V3HE | [0, 0.5251] | 0.0% |
| `era5l_swvl1_mean_v3pm10` | ERA5-Land swvl1表层土壤湿度均值 | ERA5-Land swvl1 surface soil moisture mean | m3/m3 | V3pm10 | [0, 0.5652] | 0.0% |
| `era5l_swvl1_mean_v3pre30` | ERA5-Land swvl1表层土壤湿度均值 | ERA5-Land swvl1 surface soil moisture mean | m3/m3 | V3pre30 | [0, 0.5159] | 0.0% |
| `era5l_swvl1_min` | ERA5-Land swvl1表层土壤湿度最小值 | ERA5-Land swvl1 surface soil moisture min | m3/m3 | Full | [-1.466e-20, 0.4538] | 0.0% |
| `era5l_swvl1_min_hema` | ERA5-Land swvl1表层土壤湿度最小值 | ERA5-Land swvl1 surface soil moisture min | m3/m3 | HEMA | [-1.466e-20, 0.4967] | 0.0% |
| `era5l_swvl1_min_hepm10` | ERA5-Land swvl1表层土壤湿度最小值 | ERA5-Land swvl1 surface soil moisture min | m3/m3 | HEpm10 | [-1.2e-20, 0.5022] | 0.0% |
| `era5l_swvl1_min_v3he` | ERA5-Land swvl1表层土壤湿度最小值 | ERA5-Land swvl1 surface soil moisture min | m3/m3 | V3HE | [-1.448e-20, 0.4649] | 0.0% |
| `era5l_swvl1_min_v3pm10` | ERA5-Land swvl1表层土壤湿度最小值 | ERA5-Land swvl1 surface soil moisture min | m3/m3 | V3pm10 | [-1.455e-20, 0.5003] | 0.0% |
| `era5l_swvl1_min_v3pre30` | ERA5-Land swvl1表层土壤湿度最小值 | ERA5-Land swvl1 surface soil moisture min | m3/m3 | V3pre30 | [-1.455e-20, 0.4775] | 0.0% |
| `era5l_swvl1_sd` | ERA5-Land swvl1表层土壤湿度标准差 | ERA5-Land swvl1 surface soil moisture std dev | m3/m3 | Full | [0, 0.2412] | 0.0% |
| `era5l_swvl1_sd_hema` | ERA5-Land swvl1表层土壤湿度标准差 | ERA5-Land swvl1 surface soil moisture std dev | m3/m3 | HEMA | [0, 0.2381] | 0.0% |
| `era5l_swvl1_sd_hepm10` | ERA5-Land swvl1表层土壤湿度标准差 | ERA5-Land swvl1 surface soil moisture std dev | m3/m3 | HEpm10 | [0, 0.1985] | 0.0% |
| `era5l_swvl1_sd_v3he` | ERA5-Land swvl1表层土壤湿度标准差 | ERA5-Land swvl1 surface soil moisture std dev | m3/m3 | V3HE | [0, 0.2338] | 0.0% |
| `era5l_swvl1_sd_v3pm10` | ERA5-Land swvl1表层土壤湿度标准差 | ERA5-Land swvl1 surface soil moisture std dev | m3/m3 | V3pm10 | [0, 0.1674] | 0.0% |
| `era5l_swvl1_sd_v3pre30` | ERA5-Land swvl1表层土壤湿度标准差 | ERA5-Land swvl1 surface soil moisture std dev | m3/m3 | V3pre30 | [0, 0.1507] | 0.0% |
| `era5l_swvl3_coverage` | ERA5-Land swvl3根区土壤湿度覆盖率 | ERA5-Land swvl3 root-zone soil moisture temporal coverage fraction | m3/m3 | Full | [0.7943, 1] | 0.0% |
| `era5l_swvl3_coverage_hema` | ERA5-Land swvl3根区土壤湿度覆盖率 | ERA5-Land swvl3 root-zone soil moisture temporal coverage fraction | m3/m3 | HEMA | [0.989, 1] | 0.0% |
| `era5l_swvl3_coverage_hepm10` | ERA5-Land swvl3根区土壤湿度覆盖率 | ERA5-Land swvl3 root-zone soil moisture temporal coverage fraction | m3/m3 | HEpm10 | [1, 1] | 0.0% |
| `era5l_swvl3_coverage_v3he` | ERA5-Land swvl3根区土壤湿度覆盖率 | ERA5-Land swvl3 root-zone soil moisture temporal coverage fraction | m3/m3 | V3HE | [0.9828, 1] | 0.0% |
| `era5l_swvl3_coverage_v3pm10` | ERA5-Land swvl3根区土壤湿度覆盖率 | ERA5-Land swvl3 root-zone soil moisture temporal coverage fraction | m3/m3 | V3pm10 | [0.4762, 1] | 0.0% |
| `era5l_swvl3_coverage_v3pre30` | ERA5-Land swvl3根区土壤湿度覆盖率 | ERA5-Land swvl3 root-zone soil moisture temporal coverage fraction | m3/m3 | V3pre30 | [0, 1] | 0.0% |
| `era5l_swvl3_max` | ERA5-Land swvl3根区土壤湿度最大值 | ERA5-Land swvl3 root-zone soil moisture max | m3/m3 | Full | [-6.647e-23, 0.6484] | 0.0% |
| `era5l_swvl3_max_hema` | ERA5-Land swvl3根区土壤湿度最大值 | ERA5-Land swvl3 root-zone soil moisture max | m3/m3 | HEMA | [-1.446e-22, 0.6484] | 0.0% |
| `era5l_swvl3_max_hepm10` | ERA5-Land swvl3根区土壤湿度最大值 | ERA5-Land swvl3 root-zone soil moisture max | m3/m3 | HEpm10 | [-1.106e-21, 0.6108] | 0.0% |
| `era5l_swvl3_max_v3he` | ERA5-Land swvl3根区土壤湿度最大值 | ERA5-Land swvl3 root-zone soil moisture max | m3/m3 | V3HE | [-9.347e-23, 0.5882] | 0.0% |
| `era5l_swvl3_max_v3pm10` | ERA5-Land swvl3根区土壤湿度最大值 | ERA5-Land swvl3 root-zone soil moisture max | m3/m3 | V3pm10 | [-9.347e-23, 0.5569] | 0.0% |
| `era5l_swvl3_max_v3pre30` | ERA5-Land swvl3根区土壤湿度最大值 | ERA5-Land swvl3 root-zone soil moisture max | m3/m3 | V3pre30 | [-6.833e-23, 0.5683] | 0.0% |
| `era5l_swvl3_mean` | ERA5-Land swvl3根区土壤湿度均值 | ERA5-Land swvl3 root-zone soil moisture mean | m3/m3 | Full | [-7.61e-21, 0.5671] | 0.0% |
| `era5l_swvl3_mean_hema` | ERA5-Land swvl3根区土壤湿度均值 | ERA5-Land swvl3 root-zone soil moisture mean | m3/m3 | HEMA | [-7.212e-21, 0.6244] | 0.0% |
| `era5l_swvl3_mean_hepm10` | ERA5-Land swvl3根区土壤湿度均值 | ERA5-Land swvl3 root-zone soil moisture mean | m3/m3 | HEpm10 | [-1.955e-20, 0.5857] | 0.0% |
| `era5l_swvl3_mean_v3he` | ERA5-Land swvl3根区土壤湿度均值 | ERA5-Land swvl3 root-zone soil moisture mean | m3/m3 | V3HE | [-1.351e-20, 0.5413] | 0.0% |
| `era5l_swvl3_mean_v3pm10` | ERA5-Land swvl3根区土壤湿度均值 | ERA5-Land swvl3 root-zone soil moisture mean | m3/m3 | V3pm10 | [-1.163e-21, 0.5505] | 0.0% |
| `era5l_swvl3_mean_v3pre30` | ERA5-Land swvl3根区土壤湿度均值 | ERA5-Land swvl3 root-zone soil moisture mean | m3/m3 | V3pre30 | [-3.884e-22, 0.56] | 0.0% |
| `era5l_swvl3_min` | ERA5-Land swvl3根区土壤湿度最小值 | ERA5-Land swvl3 root-zone soil moisture min | m3/m3 | Full | [-7.633e-20, 0.5204] | 0.0% |
| `era5l_swvl3_min_hema` | ERA5-Land swvl3根区土壤湿度最小值 | ERA5-Land swvl3 root-zone soil moisture min | m3/m3 | HEMA | [-2.789e-20, 0.5839] | 0.0% |
| `era5l_swvl3_min_hepm10` | ERA5-Land swvl3根区土壤湿度最小值 | ERA5-Land swvl3 root-zone soil moisture min | m3/m3 | HEpm10 | [-7.633e-20, 0.567] | 0.0% |
| `era5l_swvl3_min_v3he` | ERA5-Land swvl3根区土壤湿度最小值 | ERA5-Land swvl3 root-zone soil moisture min | m3/m3 | V3HE | [-7.633e-20, 0.5204] | 0.0% |
| `era5l_swvl3_min_v3pm10` | ERA5-Land swvl3根区土壤湿度最小值 | ERA5-Land swvl3 root-zone soil moisture min | m3/m3 | V3pm10 | [-4.531e-21, 0.5463] | 0.0% |
| `era5l_swvl3_min_v3pre30` | ERA5-Land swvl3根区土壤湿度最小值 | ERA5-Land swvl3 root-zone soil moisture min | m3/m3 | V3pre30 | [-1.665e-21, 0.5494] | 0.0% |
| `era5l_swvl3_sd` | ERA5-Land swvl3根区土壤湿度标准差 | ERA5-Land swvl3 root-zone soil moisture std dev | m3/m3 | Full | [0, 0.1119] | 0.0% |
| `era5l_swvl3_sd_hema` | ERA5-Land swvl3根区土壤湿度标准差 | ERA5-Land swvl3 root-zone soil moisture std dev | m3/m3 | HEMA | [0, 0.08486] | 0.0% |
| `era5l_swvl3_sd_hepm10` | ERA5-Land swvl3根区土壤湿度标准差 | ERA5-Land swvl3 root-zone soil moisture std dev | m3/m3 | HEpm10 | [0, 0.1176] | 0.0% |
| `era5l_swvl3_sd_v3he` | ERA5-Land swvl3根区土壤湿度标准差 | ERA5-Land swvl3 root-zone soil moisture std dev | m3/m3 | V3HE | [0, 0.1109] | 0.0% |
| `era5l_swvl3_sd_v3pm10` | ERA5-Land swvl3根区土壤湿度标准差 | ERA5-Land swvl3 root-zone soil moisture std dev | m3/m3 | V3pm10 | [0, 0.06295] | 0.0% |
| `era5l_swvl3_sd_v3pre30` | ERA5-Land swvl3根区土壤湿度标准差 | ERA5-Land swvl3 root-zone soil moisture std dev | m3/m3 | V3pre30 | [0, 0.05769] | 0.0% |
| `wetdays_era5l_swvl1_ge_p80` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的日数 | Days with ERA5-Land swvl1 surface soil moisture >= local historical P80 | days | Full | [0, 156] | 0.0% |
| `wetdays_era5l_swvl1_ge_p80_hema` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的日数 | Days with ERA5-Land swvl1 surface soil moisture >= local historical P80 | days | HEMA | [0, 57] | 0.0% |
| `wetdays_era5l_swvl1_ge_p80_hepm10` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的日数 | Days with ERA5-Land swvl1 surface soil moisture >= local historical P80 | days | HEpm10 | [0, 21] | 0.0% |
| `wetdays_era5l_swvl1_ge_p80_v3he` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的日数 | Days with ERA5-Land swvl1 surface soil moisture >= local historical P80 | days | V3HE | [0, 86] | 0.0% |
| `wetdays_era5l_swvl1_ge_p80_v3pm10` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的日数 | Days with ERA5-Land swvl1 surface soil moisture >= local historical P80 | days | V3pm10 | [0, 21] | 0.0% |
| `wetdays_era5l_swvl1_ge_p80_v3pre30` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的日数 | Days with ERA5-Land swvl1 surface soil moisture >= local historical P80 | days | V3pre30 | [0, 31] | 0.0% |
| `wetdays_era5l_swvl1_ge_p90` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的日数 | Days with ERA5-Land swvl1 surface soil moisture >= local historical P90 | days | Full | [0, 156] | 0.0% |
| `wetdays_era5l_swvl1_ge_p90_hema` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的日数 | Days with ERA5-Land swvl1 surface soil moisture >= local historical P90 | days | HEMA | [0, 48] | 0.0% |
| `wetdays_era5l_swvl1_ge_p90_hepm10` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的日数 | Days with ERA5-Land swvl1 surface soil moisture >= local historical P90 | days | HEpm10 | [0, 21] | 0.0% |
| `wetdays_era5l_swvl1_ge_p90_v3he` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的日数 | Days with ERA5-Land swvl1 surface soil moisture >= local historical P90 | days | V3HE | [0, 86] | 0.0% |
| `wetdays_era5l_swvl1_ge_p90_v3pm10` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的日数 | Days with ERA5-Land swvl1 surface soil moisture >= local historical P90 | days | V3pm10 | [0, 21] | 0.0% |
| `wetdays_era5l_swvl1_ge_p90_v3pre30` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的日数 | Days with ERA5-Land swvl1 surface soil moisture >= local historical P90 | days | V3pre30 | [0, 31] | 0.0% |
| `wetdays_era5l_swvl3_ge_p80` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的日数 | Days with ERA5-Land swvl3 root-zone soil moisture >= local historical P80 | days | Full | [0, 165] | 0.0% |
| `wetdays_era5l_swvl3_ge_p80_hema` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的日数 | Days with ERA5-Land swvl3 root-zone soil moisture >= local historical P80 | days | HEMA | [0, 80] | 0.0% |
| `wetdays_era5l_swvl3_ge_p80_hepm10` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的日数 | Days with ERA5-Land swvl3 root-zone soil moisture >= local historical P80 | days | HEpm10 | [0, 21] | 0.0% |
| `wetdays_era5l_swvl3_ge_p80_v3he` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的日数 | Days with ERA5-Land swvl3 root-zone soil moisture >= local historical P80 | days | V3HE | [0, 96] | 0.0% |
| `wetdays_era5l_swvl3_ge_p80_v3pm10` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的日数 | Days with ERA5-Land swvl3 root-zone soil moisture >= local historical P80 | days | V3pm10 | [0, 21] | 0.0% |
| `wetdays_era5l_swvl3_ge_p80_v3pre30` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的日数 | Days with ERA5-Land swvl3 root-zone soil moisture >= local historical P80 | days | V3pre30 | [0, 31] | 0.0% |
| `wetdays_era5l_swvl3_ge_p90` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的日数 | Days with ERA5-Land swvl3 root-zone soil moisture >= local historical P90 | days | Full | [0, 156] | 0.0% |
| `wetdays_era5l_swvl3_ge_p90_hema` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的日数 | Days with ERA5-Land swvl3 root-zone soil moisture >= local historical P90 | days | HEMA | [0, 69] | 0.0% |
| `wetdays_era5l_swvl3_ge_p90_hepm10` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的日数 | Days with ERA5-Land swvl3 root-zone soil moisture >= local historical P90 | days | HEpm10 | [0, 21] | 0.0% |
| `wetdays_era5l_swvl3_ge_p90_v3he` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的日数 | Days with ERA5-Land swvl3 root-zone soil moisture >= local historical P90 | days | V3HE | [0, 86] | 0.0% |
| `wetdays_era5l_swvl3_ge_p90_v3pm10` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的日数 | Days with ERA5-Land swvl3 root-zone soil moisture >= local historical P90 | days | V3pm10 | [0, 21] | 0.0% |
| `wetdays_era5l_swvl3_ge_p90_v3pre30` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的日数 | Days with ERA5-Land swvl3 root-zone soil moisture >= local historical P90 | days | V3pre30 | [0, 31] | 0.0% |
| `wetexcess_era5l_swvl1_ge_p80` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for ERA5-Land swvl1 surface soil moisture | m3/m3 | Full | [0, 0.0941] | 0.0% |
| `wetexcess_era5l_swvl1_ge_p80_hema` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for ERA5-Land swvl1 surface soil moisture | m3/m3 | HEMA | [0, 0.2736] | 0.0% |
| `wetexcess_era5l_swvl1_ge_p80_hepm10` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for ERA5-Land swvl1 surface soil moisture | m3/m3 | HEpm10 | [0, 0.1823] | 0.0% |
| `wetexcess_era5l_swvl1_ge_p80_v3he` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3HE | [0, 0.07642] | 0.0% |
| `wetexcess_era5l_swvl1_ge_p80_v3pm10` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3pm10 | [0, 0.1401] | 0.0% |
| `wetexcess_era5l_swvl1_ge_p80_v3pre30` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3pre30 | [0, 0.1081] | 0.0% |
| `wetexcess_era5l_swvl1_ge_p90` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for ERA5-Land swvl1 surface soil moisture | m3/m3 | Full | [0, 0.08851] | 0.0% |
| `wetexcess_era5l_swvl1_ge_p90_hema` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for ERA5-Land swvl1 surface soil moisture | m3/m3 | HEMA | [0, 0.2586] | 0.0% |
| `wetexcess_era5l_swvl1_ge_p90_hepm10` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for ERA5-Land swvl1 surface soil moisture | m3/m3 | HEpm10 | [0, 0.1265] | 0.0% |
| `wetexcess_era5l_swvl1_ge_p90_v3he` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3HE | [0, 0.05802] | 0.0% |
| `wetexcess_era5l_swvl1_ge_p90_v3pm10` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3pm10 | [0, 0.08242] | 0.0% |
| `wetexcess_era5l_swvl1_ge_p90_v3pre30` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3pre30 | [0, 0.06578] | 0.0% |
| `wetexcess_era5l_swvl3_ge_p80` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | Full | [0, 0.0718] | 0.0% |
| `wetexcess_era5l_swvl3_ge_p80_hema` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | HEMA | [0, 0.1435] | 0.0% |
| `wetexcess_era5l_swvl3_ge_p80_hepm10` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | HEpm10 | [0, 0.1423] | 0.0% |
| `wetexcess_era5l_swvl3_ge_p80_v3he` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3HE | [0, 0.07251] | 0.0% |
| `wetexcess_era5l_swvl3_ge_p80_v3pm10` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3pm10 | [0, 0.07559] | 0.0% |
| `wetexcess_era5l_swvl3_ge_p80_v3pre30` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的平均超额 | Mean excess above local historical P80 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.0865] | 0.0% |
| `wetexcess_era5l_swvl3_ge_p90` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | Full | [0, 0.03807] | 0.0% |
| `wetexcess_era5l_swvl3_ge_p90_hema` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | HEMA | [0, 0.09494] | 0.0% |
| `wetexcess_era5l_swvl3_ge_p90_hepm10` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | HEpm10 | [0, 0.09282] | 0.0% |
| `wetexcess_era5l_swvl3_ge_p90_v3he` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3HE | [0, 0.03625] | 0.0% |
| `wetexcess_era5l_swvl3_ge_p90_v3pm10` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3pm10 | [0, 0.04673] | 0.0% |
| `wetexcess_era5l_swvl3_ge_p90_v3pre30` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的平均超额 | Mean excess above local historical P90 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.0523] | 0.0% |
| `wetshare_era5l_swvl1_ge_p80` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= local historical P80 | 0-1 | Full | [0, 1] | 0.0% |
| `wetshare_era5l_swvl1_ge_p80_hema` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= local historical P80 | 0-1 | HEMA | [0, 1] | 0.0% |
| `wetshare_era5l_swvl1_ge_p80_hepm10` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= local historical P80 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `wetshare_era5l_swvl1_ge_p80_v3he` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= local historical P80 | 0-1 | V3HE | [0, 1] | 0.0% |
| `wetshare_era5l_swvl1_ge_p80_v3pm10` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= local historical P80 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `wetshare_era5l_swvl1_ge_p80_v3pre30` | ERA5-Land swvl1表层土壤湿度高于本地历史P80的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= local historical P80 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `wetshare_era5l_swvl1_ge_p90` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= local historical P90 | 0-1 | Full | [0, 1] | 0.0% |
| `wetshare_era5l_swvl1_ge_p90_hema` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= local historical P90 | 0-1 | HEMA | [0, 1] | 0.0% |
| `wetshare_era5l_swvl1_ge_p90_hepm10` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= local historical P90 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `wetshare_era5l_swvl1_ge_p90_v3he` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= local historical P90 | 0-1 | V3HE | [0, 1] | 0.0% |
| `wetshare_era5l_swvl1_ge_p90_v3pm10` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= local historical P90 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `wetshare_era5l_swvl1_ge_p90_v3pre30` | ERA5-Land swvl1表层土壤湿度高于本地历史P90的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= local historical P90 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `wetshare_era5l_swvl3_ge_p80` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= local historical P80 | 0-1 | Full | [0, 1] | 0.0% |
| `wetshare_era5l_swvl3_ge_p80_hema` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= local historical P80 | 0-1 | HEMA | [0, 1] | 0.0% |
| `wetshare_era5l_swvl3_ge_p80_hepm10` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= local historical P80 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `wetshare_era5l_swvl3_ge_p80_v3he` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= local historical P80 | 0-1 | V3HE | [0, 1] | 0.0% |
| `wetshare_era5l_swvl3_ge_p80_v3pm10` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= local historical P80 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `wetshare_era5l_swvl3_ge_p80_v3pre30` | ERA5-Land swvl3根区土壤湿度高于本地历史P80的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= local historical P80 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `wetshare_era5l_swvl3_ge_p90` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= local historical P90 | 0-1 | Full | [0, 1] | 0.0% |
| `wetshare_era5l_swvl3_ge_p90_hema` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= local historical P90 | 0-1 | HEMA | [0, 1] | 0.0% |
| `wetshare_era5l_swvl3_ge_p90_hepm10` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= local historical P90 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `wetshare_era5l_swvl3_ge_p90_v3he` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= local historical P90 | 0-1 | V3HE | [0, 1] | 0.0% |
| `wetshare_era5l_swvl3_ge_p90_v3pm10` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= local historical P90 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `wetshare_era5l_swvl3_ge_p90_v3pre30` | ERA5-Land swvl3根区土壤湿度高于本地历史P90的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= local historical P90 | 0-1 | V3pre30 | [0, 1] | 0.0% |

### pooled-state

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `drydeficit_pl_era5l_swvl1_le_p25` | ERA5-Land swvl1表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for ERA5-Land swvl1 surface soil moisture | m3/m3 | Full | [0, 0.2463] | 0.0% |
| `drydeficit_pl_era5l_swvl1_le_p25_hema` | ERA5-Land swvl1表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for ERA5-Land swvl1 surface soil moisture | m3/m3 | HEMA | [0, 0.2985] | 0.0% |
| `drydeficit_pl_era5l_swvl1_le_p25_hepm10` | ERA5-Land swvl1表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for ERA5-Land swvl1 surface soil moisture | m3/m3 | HEpm10 | [0, 0.2859] | 0.0% |
| `drydeficit_pl_era5l_swvl1_le_p25_v3he` | ERA5-Land swvl1表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3HE | [0, 0.238] | 0.0% |
| `drydeficit_pl_era5l_swvl1_le_p25_v3pm10` | ERA5-Land swvl1表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3pm10 | [0, 0.2069] | 0.0% |
| `drydeficit_pl_era5l_swvl1_le_p25_v3pre30` | ERA5-Land swvl1表层土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3pre30 | [0, 0.196] | 0.0% |
| `drydeficit_pl_era5l_swvl3_le_p25` | ERA5-Land swvl3根区土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | Full | [0, 0.2261] | 0.0% |
| `drydeficit_pl_era5l_swvl3_le_p25_hema` | ERA5-Land swvl3根区土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | HEMA | [0, 0.2611] | 0.0% |
| `drydeficit_pl_era5l_swvl3_le_p25_hepm10` | ERA5-Land swvl3根区土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | HEpm10 | [0, 0.2188] | 0.0% |
| `drydeficit_pl_era5l_swvl3_le_p25_v3he` | ERA5-Land swvl3根区土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3HE | [0, 0.2121] | 0.0% |
| `drydeficit_pl_era5l_swvl3_le_p25_v3pm10` | ERA5-Land swvl3根区土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3pm10 | [0, 0.2123] | 0.0% |
| `drydeficit_pl_era5l_swvl3_le_p25_v3pre30` | ERA5-Land swvl3根区土壤湿度低于pooled窗口阈值P25的平均亏缺 | Mean deficit below pooled window-specific threshold P25 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.2153] | 0.0% |
| `dryshare_pl_era5l_swvl1_le_p25` | ERA5-Land swvl1表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= pooled window-specific threshold P25 | 0-1 | Full | [0, 1] | 0.0% |
| `dryshare_pl_era5l_swvl1_le_p25_hema` | ERA5-Land swvl1表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= pooled window-specific threshold P25 | 0-1 | HEMA | [0, 1] | 0.0% |
| `dryshare_pl_era5l_swvl1_le_p25_hepm10` | ERA5-Land swvl1表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= pooled window-specific threshold P25 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `dryshare_pl_era5l_swvl1_le_p25_v3he` | ERA5-Land swvl1表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= pooled window-specific threshold P25 | 0-1 | V3HE | [0, 1] | 0.0% |
| `dryshare_pl_era5l_swvl1_le_p25_v3pm10` | ERA5-Land swvl1表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= pooled window-specific threshold P25 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `dryshare_pl_era5l_swvl1_le_p25_v3pre30` | ERA5-Land swvl1表层土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= pooled window-specific threshold P25 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `dryshare_pl_era5l_swvl3_le_p25` | ERA5-Land swvl3根区土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= pooled window-specific threshold P25 | 0-1 | Full | [0, 1] | 0.0% |
| `dryshare_pl_era5l_swvl3_le_p25_hema` | ERA5-Land swvl3根区土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= pooled window-specific threshold P25 | 0-1 | HEMA | [0, 1] | 0.0% |
| `dryshare_pl_era5l_swvl3_le_p25_hepm10` | ERA5-Land swvl3根区土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= pooled window-specific threshold P25 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `dryshare_pl_era5l_swvl3_le_p25_v3he` | ERA5-Land swvl3根区土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= pooled window-specific threshold P25 | 0-1 | V3HE | [0, 1] | 0.0% |
| `dryshare_pl_era5l_swvl3_le_p25_v3pm10` | ERA5-Land swvl3根区土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= pooled window-specific threshold P25 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `dryshare_pl_era5l_swvl3_le_p25_v3pre30` | ERA5-Land swvl3根区土壤湿度低于pooled窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= pooled window-specific threshold P25 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `wetexcess_pl_era5l_swvl1_ge_p75` | ERA5-Land swvl1表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for ERA5-Land swvl1 surface soil moisture | m3/m3 | Full | [0, 0.1097] | 0.0% |
| `wetexcess_pl_era5l_swvl1_ge_p75_hema` | ERA5-Land swvl1表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for ERA5-Land swvl1 surface soil moisture | m3/m3 | HEMA | [0, 0.1983] | 0.0% |
| `wetexcess_pl_era5l_swvl1_ge_p75_hepm10` | ERA5-Land swvl1表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for ERA5-Land swvl1 surface soil moisture | m3/m3 | HEpm10 | [0, 0.1982] | 0.0% |
| `wetexcess_pl_era5l_swvl1_ge_p75_v3he` | ERA5-Land swvl1表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3HE | [0, 0.1102] | 0.0% |
| `wetexcess_pl_era5l_swvl1_ge_p75_v3pm10` | ERA5-Land swvl1表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3pm10 | [0, 0.1757] | 0.0% |
| `wetexcess_pl_era5l_swvl1_ge_p75_v3pre30` | ERA5-Land swvl1表层土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3pre30 | [0, 0.1358] | 0.0% |
| `wetexcess_pl_era5l_swvl3_ge_p75` | ERA5-Land swvl3根区土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | Full | [0, 0.1577] | 0.0% |
| `wetexcess_pl_era5l_swvl3_ge_p75_hema` | ERA5-Land swvl3根区土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | HEMA | [0, 0.1995] | 0.0% |
| `wetexcess_pl_era5l_swvl3_ge_p75_hepm10` | ERA5-Land swvl3根区土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | HEpm10 | [0, 0.1697] | 0.0% |
| `wetexcess_pl_era5l_swvl3_ge_p75_v3he` | ERA5-Land swvl3根区土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3HE | [0, 0.1366] | 0.0% |
| `wetexcess_pl_era5l_swvl3_ge_p75_v3pm10` | ERA5-Land swvl3根区土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3pm10 | [0, 0.1777] | 0.0% |
| `wetexcess_pl_era5l_swvl3_ge_p75_v3pre30` | ERA5-Land swvl3根区土壤湿度高于pooled窗口阈值P75的平均超额 | Mean excess above pooled window-specific threshold P75 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.194] | 0.0% |
| `wetshare_pl_era5l_swvl1_ge_p75` | ERA5-Land swvl1表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= pooled window-specific threshold P75 | 0-1 | Full | [0, 1] | 0.0% |
| `wetshare_pl_era5l_swvl1_ge_p75_hema` | ERA5-Land swvl1表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= pooled window-specific threshold P75 | 0-1 | HEMA | [0, 1] | 0.0% |
| `wetshare_pl_era5l_swvl1_ge_p75_hepm10` | ERA5-Land swvl1表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= pooled window-specific threshold P75 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `wetshare_pl_era5l_swvl1_ge_p75_v3he` | ERA5-Land swvl1表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= pooled window-specific threshold P75 | 0-1 | V3HE | [0, 1] | 0.0% |
| `wetshare_pl_era5l_swvl1_ge_p75_v3pm10` | ERA5-Land swvl1表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= pooled window-specific threshold P75 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `wetshare_pl_era5l_swvl1_ge_p75_v3pre30` | ERA5-Land swvl1表层土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= pooled window-specific threshold P75 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `wetshare_pl_era5l_swvl3_ge_p75` | ERA5-Land swvl3根区土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= pooled window-specific threshold P75 | 0-1 | Full | [0, 1] | 0.0% |
| `wetshare_pl_era5l_swvl3_ge_p75_hema` | ERA5-Land swvl3根区土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= pooled window-specific threshold P75 | 0-1 | HEMA | [0, 1] | 0.0% |
| `wetshare_pl_era5l_swvl3_ge_p75_hepm10` | ERA5-Land swvl3根区土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= pooled window-specific threshold P75 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `wetshare_pl_era5l_swvl3_ge_p75_v3he` | ERA5-Land swvl3根区土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= pooled window-specific threshold P75 | 0-1 | V3HE | [0, 1] | 0.0% |
| `wetshare_pl_era5l_swvl3_ge_p75_v3pm10` | ERA5-Land swvl3根区土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= pooled window-specific threshold P75 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `wetshare_pl_era5l_swvl3_ge_p75_v3pre30` | ERA5-Land swvl3根区土壤湿度高于pooled窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= pooled window-specific threshold P75 | 0-1 | V3pre30 | [0, 1] | 0.0% |

### maize-zone-state

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `drydeficit_mz_era5l_swvl1_le_p25` | ERA5-Land swvl1表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for ERA5-Land swvl1 surface soil moisture | m3/m3 | Full | [0, 0.2367] | 0.0% |
| `drydeficit_mz_era5l_swvl1_le_p25_hema` | ERA5-Land swvl1表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for ERA5-Land swvl1 surface soil moisture | m3/m3 | HEMA | [0, 0.2952] | 0.0% |
| `drydeficit_mz_era5l_swvl1_le_p25_hepm10` | ERA5-Land swvl1表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for ERA5-Land swvl1 surface soil moisture | m3/m3 | HEpm10 | [0, 0.2845] | 0.0% |
| `drydeficit_mz_era5l_swvl1_le_p25_v3he` | ERA5-Land swvl1表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3HE | [0, 0.2238] | 0.0% |
| `drydeficit_mz_era5l_swvl1_le_p25_v3pm10` | ERA5-Land swvl1表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3pm10 | [0, 0.2624] | 0.0% |
| `drydeficit_mz_era5l_swvl1_le_p25_v3pre30` | ERA5-Land swvl1表层土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3pre30 | [0, 0.2512] | 0.0% |
| `drydeficit_mz_era5l_swvl3_le_p25` | ERA5-Land swvl3根区土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | Full | [0, 0.2273] | 0.0% |
| `drydeficit_mz_era5l_swvl3_le_p25_hema` | ERA5-Land swvl3根区土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | HEMA | [0, 0.255] | 0.0% |
| `drydeficit_mz_era5l_swvl3_le_p25_hepm10` | ERA5-Land swvl3根区土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | HEpm10 | [0, 0.2194] | 0.0% |
| `drydeficit_mz_era5l_swvl3_le_p25_v3he` | ERA5-Land swvl3根区土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3HE | [0, 0.2161] | 0.0% |
| `drydeficit_mz_era5l_swvl3_le_p25_v3pm10` | ERA5-Land swvl3根区土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3pm10 | [0, 0.2214] | 0.0% |
| `drydeficit_mz_era5l_swvl3_le_p25_v3pre30` | ERA5-Land swvl3根区土壤湿度低于maize-zone窗口阈值P25的平均亏缺 | Mean deficit below maize-zone-specific threshold P25 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.2236] | 0.0% |
| `dryshare_mz_era5l_swvl1_le_p25` | ERA5-Land swvl1表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | Full | [0, 1] | 0.0% |
| `dryshare_mz_era5l_swvl1_le_p25_hema` | ERA5-Land swvl1表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | HEMA | [0, 1] | 0.0% |
| `dryshare_mz_era5l_swvl1_le_p25_hepm10` | ERA5-Land swvl1表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `dryshare_mz_era5l_swvl1_le_p25_v3he` | ERA5-Land swvl1表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3HE | [0, 1] | 0.0% |
| `dryshare_mz_era5l_swvl1_le_p25_v3pm10` | ERA5-Land swvl1表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `dryshare_mz_era5l_swvl1_le_p25_v3pre30` | ERA5-Land swvl1表层土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `dryshare_mz_era5l_swvl3_le_p25` | ERA5-Land swvl3根区土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= maize-zone-specific threshold P25 | 0-1 | Full | [0, 1] | 0.0% |
| `dryshare_mz_era5l_swvl3_le_p25_hema` | ERA5-Land swvl3根区土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= maize-zone-specific threshold P25 | 0-1 | HEMA | [0, 1] | 0.0% |
| `dryshare_mz_era5l_swvl3_le_p25_hepm10` | ERA5-Land swvl3根区土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= maize-zone-specific threshold P25 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `dryshare_mz_era5l_swvl3_le_p25_v3he` | ERA5-Land swvl3根区土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3HE | [0, 1] | 0.0% |
| `dryshare_mz_era5l_swvl3_le_p25_v3pm10` | ERA5-Land swvl3根区土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `dryshare_mz_era5l_swvl3_le_p25_v3pre30` | ERA5-Land swvl3根区土壤湿度低于maize-zone窗口阈值P25的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture <= maize-zone-specific threshold P25 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `wetexcess_mz_era5l_swvl1_ge_p75` | ERA5-Land swvl1表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for ERA5-Land swvl1 surface soil moisture | m3/m3 | Full | [0, 0.1489] | 0.0% |
| `wetexcess_mz_era5l_swvl1_ge_p75_hema` | ERA5-Land swvl1表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for ERA5-Land swvl1 surface soil moisture | m3/m3 | HEMA | [0, 0.2642] | 0.0% |
| `wetexcess_mz_era5l_swvl1_ge_p75_hepm10` | ERA5-Land swvl1表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for ERA5-Land swvl1 surface soil moisture | m3/m3 | HEpm10 | [0, 0.3112] | 0.0% |
| `wetexcess_mz_era5l_swvl1_ge_p75_v3he` | ERA5-Land swvl1表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3HE | [0, 0.2033] | 0.0% |
| `wetexcess_mz_era5l_swvl1_ge_p75_v3pm10` | ERA5-Land swvl1表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3pm10 | [0, 0.2945] | 0.0% |
| `wetexcess_mz_era5l_swvl1_ge_p75_v3pre30` | ERA5-Land swvl1表层土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for ERA5-Land swvl1 surface soil moisture | m3/m3 | V3pre30 | [0, 0.2425] | 0.0% |
| `wetexcess_mz_era5l_swvl3_ge_p75` | ERA5-Land swvl3根区土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | Full | [0, 0.2328] | 0.0% |
| `wetexcess_mz_era5l_swvl3_ge_p75_hema` | ERA5-Land swvl3根区土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | HEMA | [0, 0.2612] | 0.0% |
| `wetexcess_mz_era5l_swvl3_ge_p75_hepm10` | ERA5-Land swvl3根区土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | HEpm10 | [0, 0.2575] | 0.0% |
| `wetexcess_mz_era5l_swvl3_ge_p75_v3he` | ERA5-Land swvl3根区土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3HE | [0, 0.228] | 0.0% |
| `wetexcess_mz_era5l_swvl3_ge_p75_v3pm10` | ERA5-Land swvl3根区土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3pm10 | [0, 0.244] | 0.0% |
| `wetexcess_mz_era5l_swvl3_ge_p75_v3pre30` | ERA5-Land swvl3根区土壤湿度高于maize-zone窗口阈值P75的平均超额 | Mean excess above maize-zone-specific threshold P75 for ERA5-Land swvl3 root-zone soil moisture | m3/m3 | V3pre30 | [0, 0.2367] | 0.0% |
| `wetshare_mz_era5l_swvl1_ge_p75` | ERA5-Land swvl1表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | Full | [0, 1] | 0.0% |
| `wetshare_mz_era5l_swvl1_ge_p75_hema` | ERA5-Land swvl1表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | HEMA | [0, 1] | 0.0% |
| `wetshare_mz_era5l_swvl1_ge_p75_hepm10` | ERA5-Land swvl1表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `wetshare_mz_era5l_swvl1_ge_p75_v3he` | ERA5-Land swvl1表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3HE | [0, 1] | 0.0% |
| `wetshare_mz_era5l_swvl1_ge_p75_v3pm10` | ERA5-Land swvl1表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `wetshare_mz_era5l_swvl1_ge_p75_v3pre30` | ERA5-Land swvl1表层土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl1 surface soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3pre30 | [0, 1] | 0.0% |
| `wetshare_mz_era5l_swvl3_ge_p75` | ERA5-Land swvl3根区土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= maize-zone-specific threshold P75 | 0-1 | Full | [0, 1] | 0.0% |
| `wetshare_mz_era5l_swvl3_ge_p75_hema` | ERA5-Land swvl3根区土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= maize-zone-specific threshold P75 | 0-1 | HEMA | [0, 1] | 0.0% |
| `wetshare_mz_era5l_swvl3_ge_p75_hepm10` | ERA5-Land swvl3根区土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= maize-zone-specific threshold P75 | 0-1 | HEpm10 | [0, 1] | 0.0% |
| `wetshare_mz_era5l_swvl3_ge_p75_v3he` | ERA5-Land swvl3根区土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3HE | [0, 1] | 0.0% |
| `wetshare_mz_era5l_swvl3_ge_p75_v3pm10` | ERA5-Land swvl3根区土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3pm10 | [0, 1] | 0.0% |
| `wetshare_mz_era5l_swvl3_ge_p75_v3pre30` | ERA5-Land swvl3根区土壤湿度高于maize-zone窗口阈值P75的日占比 | Share of valid days with ERA5-Land swvl3 root-zone soil moisture >= maize-zone-specific threshold P75 | 0-1 | V3pre30 | [0, 1] | 0.0% |

## 9. ET0/Water Balance (18 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `et0_mean` | 参考蒸散均值 | Reference evapotranspiration mean | mm | Full | [2.203, 8.531] | 6.1% |
| `et0_mean_hema` | 参考蒸散均值 | Reference evapotranspiration mean | mm | HEMA | [2.15, 8.698] | 6.1% |
| `et0_mean_hepm10` | 参考蒸散均值 | Reference evapotranspiration mean | mm | HEpm10 | [1.966, 9.813] | 6.1% |
| `et0_mean_v3he` | 参考蒸散均值 | Reference evapotranspiration mean | mm | V3HE | [2.059, 9.545] | 6.1% |
| `et0_mean_v3pm10` | 参考蒸散均值 | Reference evapotranspiration mean | mm | V3pm10 | [1.213, 10.62] | 6.1% |
| `et0_mean_v3pre30` | 参考蒸散均值 | Reference evapotranspiration mean | mm | V3pre30 | [1.148, 10.81] | 6.1% |
| `et0_sum` | 参考蒸散总量 | Reference evapotranspiration sum | mm | Full | [0, 1374] | 0.0% |
| `et0_sum_hema` | 参考蒸散总量 | Reference evapotranspiration sum | mm | HEMA | [0, 454.1] | 0.0% |
| `et0_sum_hepm10` | 参考蒸散总量 | Reference evapotranspiration sum | mm | HEpm10 | [0, 206.1] | 0.0% |
| `et0_sum_v3he` | 参考蒸散总量 | Reference evapotranspiration sum | mm | V3HE | [0, 809.9] | 0.0% |
| `et0_sum_v3pm10` | 参考蒸散总量 | Reference evapotranspiration sum | mm | V3pm10 | [0, 223.1] | 0.0% |
| `et0_sum_v3pre30` | 参考蒸散总量 | Reference evapotranspiration sum | mm | V3pre30 | [0, 335.1] | 0.0% |
| `wd_deficit` | 水分亏缺 | Water deficit (ET0-P) | mm | Full | [-2186, 1327] | 0.0% |
| `wd_deficit_hema` | 水分亏缺 | Water deficit (ET0-P) | mm | HEMA | [-1531, 367.5] | 0.0% |
| `wd_deficit_hepm10` | 水分亏缺 | Water deficit (ET0-P) | mm | HEpm10 | [-836, 205.9] | 0.0% |
| `wd_deficit_v3he` | 水分亏缺 | Water deficit (ET0-P) | mm | V3HE | [-1075, 791] | 0.0% |
| `wd_deficit_v3pm10` | 水分亏缺 | Water deficit (ET0-P) | mm | V3pm10 | [-428, 220.8] | 0.0% |
| `wd_deficit_v3pre30` | 水分亏缺 | Water deficit (ET0-P) | mm | V3pre30 | [-744.1, 322.3] | 0.0% |

## 10. VPD/SPEI (24 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `spei1_max_hepm10` | SPEI-1最大值 | SPEI-1 max | -- | HEpm10 | [-3.288, 2.904] | 0.0% |
| `spei1_max_v3pm10` | SPEI-1最大值 | SPEI-1 max | -- | V3pm10 | [-2.728, 2.918] | 0.0% |
| `spei1_max_v3pre30` | SPEI-1最大值 | SPEI-1 max | -- | V3pre30 | [-2.765, 2.95] | 0.0% |
| `spei1_mean_hepm10` | SPEI-1均值 | SPEI-1 mean | -- | HEpm10 | [-3.288, 2.904] | 0.0% |
| `spei1_mean_v3pm10` | SPEI-1均值 | SPEI-1 mean | -- | V3pm10 | [-2.728, 2.918] | 0.0% |
| `spei1_mean_v3pre30` | SPEI-1均值 | SPEI-1 mean | -- | V3pre30 | [-2.765, 2.95] | 0.0% |
| `spei2_max_hema` | SPEI-2最大值 | SPEI-2 max | -- | HEMA | [-2.24, 2.814] | 0.0% |
| `spei2_max_v3he` | SPEI-2最大值 | SPEI-2 max | -- | V3HE | [-2.767, 2.95] | 0.0% |
| `spei2_mean_hema` | SPEI-2均值 | SPEI-2 mean | -- | HEMA | [-2.24, 2.814] | 0.0% |
| `spei2_mean_v3he` | SPEI-2均值 | SPEI-2 mean | -- | V3HE | [-2.767, 2.95] | 0.0% |
| `spei6_max` | SPEI-6最大值 | SPEI-6 max | -- | Full | [-2.912, 2.851] | 0.0% |
| `spei6_mean` | SPEI-6均值 | SPEI-6 mean | -- | Full | [-2.912, 2.851] | 0.0% |
| `vpd_max` | 水汽压亏缺最大值 | Vapor pressure deficit max | hPa | Full | [3.135, 59.14] | 0.0% |
| `vpd_max_hema` | 水汽压亏缺最大值 | Vapor pressure deficit max | hPa | HEMA | [3.044, 59.14] | 0.0% |
| `vpd_max_hepm10` | 水汽压亏缺最大值 | Vapor pressure deficit max | hPa | HEpm10 | [2.497, 59.14] | 0.0% |
| `vpd_max_v3he` | 水汽压亏缺最大值 | Vapor pressure deficit max | hPa | V3HE | [3.119, 59.14] | 0.0% |
| `vpd_max_v3pm10` | 水汽压亏缺最大值 | Vapor pressure deficit max | hPa | V3pm10 | [1.931, 55.89] | 0.0% |
| `vpd_max_v3pre30` | 水汽压亏缺最大值 | Vapor pressure deficit max | hPa | V3pre30 | [1.919, 55.89] | 0.0% |
| `vpd_mean` | 水汽压亏缺均值 | Vapor pressure deficit mean | hPa | Full | [2.495, 44.67] | 0.0% |
| `vpd_mean_hema` | 水汽压亏缺均值 | Vapor pressure deficit mean | hPa | HEMA | [2.39, 41.74] | 0.0% |
| `vpd_mean_hepm10` | 水汽压亏缺均值 | Vapor pressure deficit mean | hPa | HEpm10 | [2.497, 52.6] | 0.0% |
| `vpd_mean_v3he` | 水汽压亏缺均值 | Vapor pressure deficit mean | hPa | V3HE | [2.743, 52.64] | 0.0% |
| `vpd_mean_v3pm10` | 水汽压亏缺均值 | Vapor pressure deficit mean | hPa | V3pm10 | [1.815, 53.31] | 0.0% |
| `vpd_mean_v3pre30` | 水汽压亏缺均值 | Vapor pressure deficit mean | hPa | V3pre30 | [1.331, 49.66] | 0.0% |

## 11. Compound Stress (234 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `hotdrydays_ge30_era5l_swvl1_p10` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | Full | [0, 66] | 0.0% |
| `hotdrydays_ge30_era5l_swvl1_p10_hema` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | HEMA | [0, 42] | 0.0% |
| `hotdrydays_ge30_era5l_swvl1_p10_hepm10` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_era5l_swvl1_p10_v3he` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | V3HE | [0, 41] | 0.0% |
| `hotdrydays_ge30_era5l_swvl1_p10_v3pm10` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_era5l_swvl1_p10_v3pre30` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge30_era5l_swvl1_p20` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | Full | [0, 80] | 0.0% |
| `hotdrydays_ge30_era5l_swvl1_p20_hema` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | HEMA | [0, 47] | 0.0% |
| `hotdrydays_ge30_era5l_swvl1_p20_hepm10` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_era5l_swvl1_p20_v3he` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | V3HE | [0, 45] | 0.0% |
| `hotdrydays_ge30_era5l_swvl1_p20_v3pm10` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_era5l_swvl1_p20_v3pre30` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge30_era5l_swvl3_p10` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | Full | [0, 111] | 0.0% |
| `hotdrydays_ge30_era5l_swvl3_p10_hema` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | HEMA | [0, 50] | 0.0% |
| `hotdrydays_ge30_era5l_swvl3_p10_hepm10` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_era5l_swvl3_p10_v3he` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | V3HE | [0, 68] | 0.0% |
| `hotdrydays_ge30_era5l_swvl3_p10_v3pm10` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_era5l_swvl3_p10_v3pre30` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge30_era5l_swvl3_p20` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | Full | [0, 129] | 0.0% |
| `hotdrydays_ge30_era5l_swvl3_p20_hema` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | HEMA | [0, 58] | 0.0% |
| `hotdrydays_ge30_era5l_swvl3_p20_hepm10` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_era5l_swvl3_p20_v3he` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | V3HE | [0, 73] | 0.0% |
| `hotdrydays_ge30_era5l_swvl3_p20_v3pm10` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_era5l_swvl3_p20_v3pre30` | 热干复合日数(Tmax >= 30 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge30_pr_lt1` | 热干复合日数(Tmax >= 30 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 30 degC and Daily precipitation < 1 mm) | days | Full | [0, 136] | 0.0% |
| `hotdrydays_ge30_pr_lt1_hema` | 热干复合日数(Tmax >= 30 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 30 degC and Daily precipitation < 1 mm) | days | HEMA | [0, 51] | 0.0% |
| `hotdrydays_ge30_pr_lt1_hepm10` | 热干复合日数(Tmax >= 30 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 30 degC and Daily precipitation < 1 mm) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_pr_lt1_v3he` | 热干复合日数(Tmax >= 30 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 30 degC and Daily precipitation < 1 mm) | days | V3HE | [0, 81] | 0.0% |
| `hotdrydays_ge30_pr_lt1_v3pm10` | 热干复合日数(Tmax >= 30 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 30 degC and Daily precipitation < 1 mm) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_pr_lt1_v3pre30` | 热干复合日数(Tmax >= 30 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 30 degC and Daily precipitation < 1 mm) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge30_smrz_p10` | 热干复合日数(Tmax >= 30 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and GLEAM root-zone soil moisture <= P10) | days | Full | [0, 65] | 0.0% |
| `hotdrydays_ge30_smrz_p10_hema` | 热干复合日数(Tmax >= 30 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and GLEAM root-zone soil moisture <= P10) | days | HEMA | [0, 35] | 0.0% |
| `hotdrydays_ge30_smrz_p10_hepm10` | 热干复合日数(Tmax >= 30 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and GLEAM root-zone soil moisture <= P10) | days | HEpm10 | [0, 20] | 0.0% |
| `hotdrydays_ge30_smrz_p10_v3he` | 热干复合日数(Tmax >= 30 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and GLEAM root-zone soil moisture <= P10) | days | V3HE | [0, 44] | 0.0% |
| `hotdrydays_ge30_smrz_p10_v3pm10` | 热干复合日数(Tmax >= 30 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and GLEAM root-zone soil moisture <= P10) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_smrz_p10_v3pre30` | 热干复合日数(Tmax >= 30 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and GLEAM root-zone soil moisture <= P10) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge30_smrz_p20` | 热干复合日数(Tmax >= 30 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and GLEAM root-zone soil moisture <= P20) | days | Full | [0, 86] | 0.0% |
| `hotdrydays_ge30_smrz_p20_hema` | 热干复合日数(Tmax >= 30 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and GLEAM root-zone soil moisture <= P20) | days | HEMA | [0, 53] | 0.0% |
| `hotdrydays_ge30_smrz_p20_hepm10` | 热干复合日数(Tmax >= 30 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and GLEAM root-zone soil moisture <= P20) | days | HEpm10 | [0, 20] | 0.0% |
| `hotdrydays_ge30_smrz_p20_v3he` | 热干复合日数(Tmax >= 30 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and GLEAM root-zone soil moisture <= P20) | days | V3HE | [0, 57] | 0.0% |
| `hotdrydays_ge30_smrz_p20_v3pm10` | 热干复合日数(Tmax >= 30 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and GLEAM root-zone soil moisture <= P20) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_smrz_p20_v3pre30` | 热干复合日数(Tmax >= 30 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and GLEAM root-zone soil moisture <= P20) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge30_sms_p10` | 热干复合日数(Tmax >= 30 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and GLEAM surface soil moisture <= P10) | days | Full | [0, 58] | 0.0% |
| `hotdrydays_ge30_sms_p10_hema` | 热干复合日数(Tmax >= 30 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and GLEAM surface soil moisture <= P10) | days | HEMA | [0, 18] | 0.0% |
| `hotdrydays_ge30_sms_p10_hepm10` | 热干复合日数(Tmax >= 30 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and GLEAM surface soil moisture <= P10) | days | HEpm10 | [0, 17] | 0.0% |
| `hotdrydays_ge30_sms_p10_v3he` | 热干复合日数(Tmax >= 30 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and GLEAM surface soil moisture <= P10) | days | V3HE | [0, 36] | 0.0% |
| `hotdrydays_ge30_sms_p10_v3pm10` | 热干复合日数(Tmax >= 30 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and GLEAM surface soil moisture <= P10) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_sms_p10_v3pre30` | 热干复合日数(Tmax >= 30 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and GLEAM surface soil moisture <= P10) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge30_sms_p20` | 热干复合日数(Tmax >= 30 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and GLEAM surface soil moisture <= P20) | days | Full | [0, 70] | 0.0% |
| `hotdrydays_ge30_sms_p20_hema` | 热干复合日数(Tmax >= 30 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and GLEAM surface soil moisture <= P20) | days | HEMA | [0, 29] | 0.0% |
| `hotdrydays_ge30_sms_p20_hepm10` | 热干复合日数(Tmax >= 30 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and GLEAM surface soil moisture <= P20) | days | HEpm10 | [0, 18] | 0.0% |
| `hotdrydays_ge30_sms_p20_v3he` | 热干复合日数(Tmax >= 30 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and GLEAM surface soil moisture <= P20) | days | V3HE | [0, 45] | 0.0% |
| `hotdrydays_ge30_sms_p20_v3pm10` | 热干复合日数(Tmax >= 30 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and GLEAM surface soil moisture <= P20) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_sms_p20_v3pre30` | 热干复合日数(Tmax >= 30 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and GLEAM surface soil moisture <= P20) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge30_swsm_l1_p10` | 热干复合日数(Tmax >= 30 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and SWSM L1 surface soil moisture <= P10) | days | Full | [0, 83] | 0.0% |
| `hotdrydays_ge30_swsm_l1_p10_hema` | 热干复合日数(Tmax >= 30 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and SWSM L1 surface soil moisture <= P10) | days | HEMA | [0, 36] | 0.0% |
| `hotdrydays_ge30_swsm_l1_p10_hepm10` | 热干复合日数(Tmax >= 30 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and SWSM L1 surface soil moisture <= P10) | days | HEpm10 | [0, 20] | 0.0% |
| `hotdrydays_ge30_swsm_l1_p10_v3he` | 热干复合日数(Tmax >= 30 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and SWSM L1 surface soil moisture <= P10) | days | V3HE | [0, 55] | 0.0% |
| `hotdrydays_ge30_swsm_l1_p10_v3pm10` | 热干复合日数(Tmax >= 30 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and SWSM L1 surface soil moisture <= P10) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_swsm_l1_p10_v3pre30` | 热干复合日数(Tmax >= 30 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and SWSM L1 surface soil moisture <= P10) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge30_swsm_l1_p20` | 热干复合日数(Tmax >= 30 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and SWSM L1 surface soil moisture <= P20) | days | Full | [0, 101] | 0.0% |
| `hotdrydays_ge30_swsm_l1_p20_hema` | 热干复合日数(Tmax >= 30 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and SWSM L1 surface soil moisture <= P20) | days | HEMA | [0, 46] | 0.0% |
| `hotdrydays_ge30_swsm_l1_p20_hepm10` | 热干复合日数(Tmax >= 30 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and SWSM L1 surface soil moisture <= P20) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_swsm_l1_p20_v3he` | 热干复合日数(Tmax >= 30 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and SWSM L1 surface soil moisture <= P20) | days | V3HE | [0, 65] | 0.0% |
| `hotdrydays_ge30_swsm_l1_p20_v3pm10` | 热干复合日数(Tmax >= 30 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and SWSM L1 surface soil moisture <= P20) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_swsm_l1_p20_v3pre30` | 热干复合日数(Tmax >= 30 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and SWSM L1 surface soil moisture <= P20) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge30_swsm_l3_p10` | 热干复合日数(Tmax >= 30 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and SWSM L3 deep soil moisture <= P10) | days | Full | [0, 89] | 0.0% |
| `hotdrydays_ge30_swsm_l3_p10_hema` | 热干复合日数(Tmax >= 30 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and SWSM L3 deep soil moisture <= P10) | days | HEMA | [0, 54] | 0.0% |
| `hotdrydays_ge30_swsm_l3_p10_hepm10` | 热干复合日数(Tmax >= 30 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and SWSM L3 deep soil moisture <= P10) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_swsm_l3_p10_v3he` | 热干复合日数(Tmax >= 30 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and SWSM L3 deep soil moisture <= P10) | days | V3HE | [0, 51] | 0.0% |
| `hotdrydays_ge30_swsm_l3_p10_v3pm10` | 热干复合日数(Tmax >= 30 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and SWSM L3 deep soil moisture <= P10) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_swsm_l3_p10_v3pre30` | 热干复合日数(Tmax >= 30 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 30 degC and SWSM L3 deep soil moisture <= P10) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge30_swsm_l3_p20` | 热干复合日数(Tmax >= 30 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and SWSM L3 deep soil moisture <= P20) | days | Full | [0, 105] | 0.0% |
| `hotdrydays_ge30_swsm_l3_p20_hema` | 热干复合日数(Tmax >= 30 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and SWSM L3 deep soil moisture <= P20) | days | HEMA | [0, 62] | 0.0% |
| `hotdrydays_ge30_swsm_l3_p20_hepm10` | 热干复合日数(Tmax >= 30 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and SWSM L3 deep soil moisture <= P20) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_swsm_l3_p20_v3he` | 热干复合日数(Tmax >= 30 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and SWSM L3 deep soil moisture <= P20) | days | V3HE | [0, 69] | 0.0% |
| `hotdrydays_ge30_swsm_l3_p20_v3pm10` | 热干复合日数(Tmax >= 30 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and SWSM L3 deep soil moisture <= P20) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge30_swsm_l3_p20_v3pre30` | 热干复合日数(Tmax >= 30 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 30 degC and SWSM L3 deep soil moisture <= P20) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge32_era5l_swvl1_p10` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | Full | [0, 50] | 0.0% |
| `hotdrydays_ge32_era5l_swvl1_p10_hema` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | HEMA | [0, 37] | 0.0% |
| `hotdrydays_ge32_era5l_swvl1_p10_hepm10` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_era5l_swvl1_p10_v3he` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | V3HE | [0, 39] | 0.0% |
| `hotdrydays_ge32_era5l_swvl1_p10_v3pm10` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_era5l_swvl1_p10_v3pre30` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge32_era5l_swvl1_p20` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | Full | [0, 75] | 0.0% |
| `hotdrydays_ge32_era5l_swvl1_p20_hema` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | HEMA | [0, 42] | 0.0% |
| `hotdrydays_ge32_era5l_swvl1_p20_hepm10` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_era5l_swvl1_p20_v3he` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | V3HE | [0, 43] | 0.0% |
| `hotdrydays_ge32_era5l_swvl1_p20_v3pm10` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_era5l_swvl1_p20_v3pre30` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge32_era5l_swvl3_p10` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | Full | [0, 94] | 0.0% |
| `hotdrydays_ge32_era5l_swvl3_p10_hema` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | HEMA | [0, 45] | 0.0% |
| `hotdrydays_ge32_era5l_swvl3_p10_hepm10` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_era5l_swvl3_p10_v3he` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | V3HE | [0, 58] | 0.0% |
| `hotdrydays_ge32_era5l_swvl3_p10_v3pm10` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_era5l_swvl3_p10_v3pre30` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge32_era5l_swvl3_p20` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | Full | [0, 121] | 0.0% |
| `hotdrydays_ge32_era5l_swvl3_p20_hema` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | HEMA | [0, 50] | 0.0% |
| `hotdrydays_ge32_era5l_swvl3_p20_hepm10` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_era5l_swvl3_p20_v3he` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | V3HE | [0, 64] | 0.0% |
| `hotdrydays_ge32_era5l_swvl3_p20_v3pm10` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_era5l_swvl3_p20_v3pre30` | 热干复合日数(Tmax >= 32 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge32_pr_lt1` | 热干复合日数(Tmax >= 32 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 32 degC and Daily precipitation < 1 mm) | days | Full | [0, 124] | 0.0% |
| `hotdrydays_ge32_pr_lt1_hema` | 热干复合日数(Tmax >= 32 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 32 degC and Daily precipitation < 1 mm) | days | HEMA | [0, 45] | 0.0% |
| `hotdrydays_ge32_pr_lt1_hepm10` | 热干复合日数(Tmax >= 32 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 32 degC and Daily precipitation < 1 mm) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_pr_lt1_v3he` | 热干复合日数(Tmax >= 32 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 32 degC and Daily precipitation < 1 mm) | days | V3HE | [0, 77] | 0.0% |
| `hotdrydays_ge32_pr_lt1_v3pm10` | 热干复合日数(Tmax >= 32 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 32 degC and Daily precipitation < 1 mm) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_pr_lt1_v3pre30` | 热干复合日数(Tmax >= 32 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 32 degC and Daily precipitation < 1 mm) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge32_smrz_p10` | 热干复合日数(Tmax >= 32 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and GLEAM root-zone soil moisture <= P10) | days | Full | [0, 57] | 0.0% |
| `hotdrydays_ge32_smrz_p10_hema` | 热干复合日数(Tmax >= 32 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and GLEAM root-zone soil moisture <= P10) | days | HEMA | [0, 28] | 0.0% |
| `hotdrydays_ge32_smrz_p10_hepm10` | 热干复合日数(Tmax >= 32 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and GLEAM root-zone soil moisture <= P10) | days | HEpm10 | [0, 15] | 0.0% |
| `hotdrydays_ge32_smrz_p10_v3he` | 热干复合日数(Tmax >= 32 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and GLEAM root-zone soil moisture <= P10) | days | V3HE | [0, 36] | 0.0% |
| `hotdrydays_ge32_smrz_p10_v3pm10` | 热干复合日数(Tmax >= 32 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and GLEAM root-zone soil moisture <= P10) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_smrz_p10_v3pre30` | 热干复合日数(Tmax >= 32 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and GLEAM root-zone soil moisture <= P10) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge32_smrz_p20` | 热干复合日数(Tmax >= 32 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and GLEAM root-zone soil moisture <= P20) | days | Full | [0, 71] | 0.0% |
| `hotdrydays_ge32_smrz_p20_hema` | 热干复合日数(Tmax >= 32 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and GLEAM root-zone soil moisture <= P20) | days | HEMA | [0, 35] | 0.0% |
| `hotdrydays_ge32_smrz_p20_hepm10` | 热干复合日数(Tmax >= 32 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and GLEAM root-zone soil moisture <= P20) | days | HEpm10 | [0, 19] | 0.0% |
| `hotdrydays_ge32_smrz_p20_v3he` | 热干复合日数(Tmax >= 32 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and GLEAM root-zone soil moisture <= P20) | days | V3HE | [0, 48] | 0.0% |
| `hotdrydays_ge32_smrz_p20_v3pm10` | 热干复合日数(Tmax >= 32 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and GLEAM root-zone soil moisture <= P20) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_smrz_p20_v3pre30` | 热干复合日数(Tmax >= 32 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and GLEAM root-zone soil moisture <= P20) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge32_sms_p10` | 热干复合日数(Tmax >= 32 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and GLEAM surface soil moisture <= P10) | days | Full | [0, 56] | 0.0% |
| `hotdrydays_ge32_sms_p10_hema` | 热干复合日数(Tmax >= 32 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and GLEAM surface soil moisture <= P10) | days | HEMA | [0, 15] | 0.0% |
| `hotdrydays_ge32_sms_p10_hepm10` | 热干复合日数(Tmax >= 32 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and GLEAM surface soil moisture <= P10) | days | HEpm10 | [0, 13] | 0.0% |
| `hotdrydays_ge32_sms_p10_v3he` | 热干复合日数(Tmax >= 32 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and GLEAM surface soil moisture <= P10) | days | V3HE | [0, 32] | 0.0% |
| `hotdrydays_ge32_sms_p10_v3pm10` | 热干复合日数(Tmax >= 32 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and GLEAM surface soil moisture <= P10) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_sms_p10_v3pre30` | 热干复合日数(Tmax >= 32 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and GLEAM surface soil moisture <= P10) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge32_sms_p20` | 热干复合日数(Tmax >= 32 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and GLEAM surface soil moisture <= P20) | days | Full | [0, 65] | 0.0% |
| `hotdrydays_ge32_sms_p20_hema` | 热干复合日数(Tmax >= 32 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and GLEAM surface soil moisture <= P20) | days | HEMA | [0, 19] | 0.0% |
| `hotdrydays_ge32_sms_p20_hepm10` | 热干复合日数(Tmax >= 32 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and GLEAM surface soil moisture <= P20) | days | HEpm10 | [0, 16] | 0.0% |
| `hotdrydays_ge32_sms_p20_v3he` | 热干复合日数(Tmax >= 32 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and GLEAM surface soil moisture <= P20) | days | V3HE | [0, 37] | 0.0% |
| `hotdrydays_ge32_sms_p20_v3pm10` | 热干复合日数(Tmax >= 32 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and GLEAM surface soil moisture <= P20) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_sms_p20_v3pre30` | 热干复合日数(Tmax >= 32 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and GLEAM surface soil moisture <= P20) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge32_swsm_l1_p10` | 热干复合日数(Tmax >= 32 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and SWSM L1 surface soil moisture <= P10) | days | Full | [0, 73] | 0.0% |
| `hotdrydays_ge32_swsm_l1_p10_hema` | 热干复合日数(Tmax >= 32 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and SWSM L1 surface soil moisture <= P10) | days | HEMA | [0, 32] | 0.0% |
| `hotdrydays_ge32_swsm_l1_p10_hepm10` | 热干复合日数(Tmax >= 32 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and SWSM L1 surface soil moisture <= P10) | days | HEpm10 | [0, 19] | 0.0% |
| `hotdrydays_ge32_swsm_l1_p10_v3he` | 热干复合日数(Tmax >= 32 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and SWSM L1 surface soil moisture <= P10) | days | V3HE | [0, 48] | 0.0% |
| `hotdrydays_ge32_swsm_l1_p10_v3pm10` | 热干复合日数(Tmax >= 32 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and SWSM L1 surface soil moisture <= P10) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_swsm_l1_p10_v3pre30` | 热干复合日数(Tmax >= 32 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and SWSM L1 surface soil moisture <= P10) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge32_swsm_l1_p20` | 热干复合日数(Tmax >= 32 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and SWSM L1 surface soil moisture <= P20) | days | Full | [0, 93] | 0.0% |
| `hotdrydays_ge32_swsm_l1_p20_hema` | 热干复合日数(Tmax >= 32 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and SWSM L1 surface soil moisture <= P20) | days | HEMA | [0, 40] | 0.0% |
| `hotdrydays_ge32_swsm_l1_p20_hepm10` | 热干复合日数(Tmax >= 32 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and SWSM L1 surface soil moisture <= P20) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_swsm_l1_p20_v3he` | 热干复合日数(Tmax >= 32 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and SWSM L1 surface soil moisture <= P20) | days | V3HE | [0, 63] | 0.0% |
| `hotdrydays_ge32_swsm_l1_p20_v3pm10` | 热干复合日数(Tmax >= 32 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and SWSM L1 surface soil moisture <= P20) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_swsm_l1_p20_v3pre30` | 热干复合日数(Tmax >= 32 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and SWSM L1 surface soil moisture <= P20) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge32_swsm_l3_p10` | 热干复合日数(Tmax >= 32 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and SWSM L3 deep soil moisture <= P10) | days | Full | [0, 71] | 0.0% |
| `hotdrydays_ge32_swsm_l3_p10_hema` | 热干复合日数(Tmax >= 32 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and SWSM L3 deep soil moisture <= P10) | days | HEMA | [0, 44] | 0.0% |
| `hotdrydays_ge32_swsm_l3_p10_hepm10` | 热干复合日数(Tmax >= 32 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and SWSM L3 deep soil moisture <= P10) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_swsm_l3_p10_v3he` | 热干复合日数(Tmax >= 32 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and SWSM L3 deep soil moisture <= P10) | days | V3HE | [0, 42] | 0.0% |
| `hotdrydays_ge32_swsm_l3_p10_v3pm10` | 热干复合日数(Tmax >= 32 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and SWSM L3 deep soil moisture <= P10) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_swsm_l3_p10_v3pre30` | 热干复合日数(Tmax >= 32 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 32 degC and SWSM L3 deep soil moisture <= P10) | days | V3pre30 | [0, 30] | 0.0% |
| `hotdrydays_ge32_swsm_l3_p20` | 热干复合日数(Tmax >= 32 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and SWSM L3 deep soil moisture <= P20) | days | Full | [0, 96] | 0.0% |
| `hotdrydays_ge32_swsm_l3_p20_hema` | 热干复合日数(Tmax >= 32 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and SWSM L3 deep soil moisture <= P20) | days | HEMA | [0, 48] | 0.0% |
| `hotdrydays_ge32_swsm_l3_p20_hepm10` | 热干复合日数(Tmax >= 32 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and SWSM L3 deep soil moisture <= P20) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_swsm_l3_p20_v3he` | 热干复合日数(Tmax >= 32 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and SWSM L3 deep soil moisture <= P20) | days | V3HE | [0, 58] | 0.0% |
| `hotdrydays_ge32_swsm_l3_p20_v3pm10` | 热干复合日数(Tmax >= 32 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and SWSM L3 deep soil moisture <= P20) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge32_swsm_l3_p20_v3pre30` | 热干复合日数(Tmax >= 32 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 32 degC and SWSM L3 deep soil moisture <= P20) | days | V3pre30 | [0, 31] | 0.0% |
| `hotdrydays_ge35_era5l_swvl1_p10` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | Full | [0, 39] | 0.0% |
| `hotdrydays_ge35_era5l_swvl1_p10_hema` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | HEMA | [0, 26] | 0.0% |
| `hotdrydays_ge35_era5l_swvl1_p10_hepm10` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | HEpm10 | [0, 20] | 0.0% |
| `hotdrydays_ge35_era5l_swvl1_p10_v3he` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | V3HE | [0, 29] | 0.0% |
| `hotdrydays_ge35_era5l_swvl1_p10_v3pm10` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | V3pm10 | [0, 17] | 0.0% |
| `hotdrydays_ge35_era5l_swvl1_p10_v3pre30` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl1 surface soil moisture <= P10) | days | V3pre30 | [0, 20] | 0.0% |
| `hotdrydays_ge35_era5l_swvl1_p20` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | Full | [0, 60] | 0.0% |
| `hotdrydays_ge35_era5l_swvl1_p20_hema` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | HEMA | [0, 31] | 0.0% |
| `hotdrydays_ge35_era5l_swvl1_p20_hepm10` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge35_era5l_swvl1_p20_v3he` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | V3HE | [0, 32] | 0.0% |
| `hotdrydays_ge35_era5l_swvl1_p20_v3pm10` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge35_era5l_swvl1_p20_v3pre30` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl1 surface soil moisture <= P20) | days | V3pre30 | [0, 22] | 0.0% |
| `hotdrydays_ge35_era5l_swvl3_p10` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | Full | [0, 61] | 0.0% |
| `hotdrydays_ge35_era5l_swvl3_p10_hema` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | HEMA | [0, 33] | 0.0% |
| `hotdrydays_ge35_era5l_swvl3_p10_hepm10` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | HEpm10 | [0, 20] | 0.0% |
| `hotdrydays_ge35_era5l_swvl3_p10_v3he` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | V3HE | [0, 36] | 0.0% |
| `hotdrydays_ge35_era5l_swvl3_p10_v3pm10` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | V3pm10 | [0, 17] | 0.0% |
| `hotdrydays_ge35_era5l_swvl3_p10_v3pre30` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl3根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl3 root-zone soil moisture <= P10) | days | V3pre30 | [0, 24] | 0.0% |
| `hotdrydays_ge35_era5l_swvl3_p20` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | Full | [0, 98] | 0.0% |
| `hotdrydays_ge35_era5l_swvl3_p20_hema` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | HEMA | [0, 33] | 0.0% |
| `hotdrydays_ge35_era5l_swvl3_p20_hepm10` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge35_era5l_swvl3_p20_v3he` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | V3HE | [0, 58] | 0.0% |
| `hotdrydays_ge35_era5l_swvl3_p20_v3pm10` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | V3pm10 | [0, 20] | 0.0% |
| `hotdrydays_ge35_era5l_swvl3_p20_v3pre30` | 热干复合日数(Tmax >= 35 degC, ERA5-Land swvl3根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and ERA5-Land swvl3 root-zone soil moisture <= P20) | days | V3pre30 | [0, 27] | 0.0% |
| `hotdrydays_ge35_pr_lt1` | 热干复合日数(Tmax >= 35 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 35 degC and Daily precipitation < 1 mm) | days | Full | [0, 103] | 0.0% |
| `hotdrydays_ge35_pr_lt1_hema` | 热干复合日数(Tmax >= 35 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 35 degC and Daily precipitation < 1 mm) | days | HEMA | [0, 35] | 0.0% |
| `hotdrydays_ge35_pr_lt1_hepm10` | 热干复合日数(Tmax >= 35 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 35 degC and Daily precipitation < 1 mm) | days | HEpm10 | [0, 21] | 0.0% |
| `hotdrydays_ge35_pr_lt1_v3he` | 热干复合日数(Tmax >= 35 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 35 degC and Daily precipitation < 1 mm) | days | V3HE | [0, 68] | 0.0% |
| `hotdrydays_ge35_pr_lt1_v3pm10` | 热干复合日数(Tmax >= 35 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 35 degC and Daily precipitation < 1 mm) | days | V3pm10 | [0, 21] | 0.0% |
| `hotdrydays_ge35_pr_lt1_v3pre30` | 热干复合日数(Tmax >= 35 degC, 日降水<1 mm) | Hot-dry days (Tmax >= 35 degC and Daily precipitation < 1 mm) | days | V3pre30 | [0, 29] | 0.0% |
| `hotdrydays_ge35_smrz_p10` | 热干复合日数(Tmax >= 35 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and GLEAM root-zone soil moisture <= P10) | days | Full | [0, 38] | 0.0% |
| `hotdrydays_ge35_smrz_p10_hema` | 热干复合日数(Tmax >= 35 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and GLEAM root-zone soil moisture <= P10) | days | HEMA | [0, 18] | 0.0% |
| `hotdrydays_ge35_smrz_p10_hepm10` | 热干复合日数(Tmax >= 35 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and GLEAM root-zone soil moisture <= P10) | days | HEpm10 | [0, 10] | 0.0% |
| `hotdrydays_ge35_smrz_p10_v3he` | 热干复合日数(Tmax >= 35 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and GLEAM root-zone soil moisture <= P10) | days | V3HE | [0, 27] | 0.0% |
| `hotdrydays_ge35_smrz_p10_v3pm10` | 热干复合日数(Tmax >= 35 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and GLEAM root-zone soil moisture <= P10) | days | V3pm10 | [0, 17] | 0.0% |
| `hotdrydays_ge35_smrz_p10_v3pre30` | 热干复合日数(Tmax >= 35 degC, GLEAM根区土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and GLEAM root-zone soil moisture <= P10) | days | V3pre30 | [0, 22] | 0.0% |
| `hotdrydays_ge35_smrz_p20` | 热干复合日数(Tmax >= 35 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and GLEAM root-zone soil moisture <= P20) | days | Full | [0, 42] | 0.0% |
| `hotdrydays_ge35_smrz_p20_hema` | 热干复合日数(Tmax >= 35 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and GLEAM root-zone soil moisture <= P20) | days | HEMA | [0, 24] | 0.0% |
| `hotdrydays_ge35_smrz_p20_hepm10` | 热干复合日数(Tmax >= 35 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and GLEAM root-zone soil moisture <= P20) | days | HEpm10 | [0, 12] | 0.0% |
| `hotdrydays_ge35_smrz_p20_v3he` | 热干复合日数(Tmax >= 35 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and GLEAM root-zone soil moisture <= P20) | days | V3HE | [0, 35] | 0.0% |
| `hotdrydays_ge35_smrz_p20_v3pm10` | 热干复合日数(Tmax >= 35 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and GLEAM root-zone soil moisture <= P20) | days | V3pm10 | [0, 17] | 0.0% |
| `hotdrydays_ge35_smrz_p20_v3pre30` | 热干复合日数(Tmax >= 35 degC, GLEAM根区土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and GLEAM root-zone soil moisture <= P20) | days | V3pre30 | [0, 22] | 0.0% |
| `hotdrydays_ge35_sms_p10` | 热干复合日数(Tmax >= 35 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and GLEAM surface soil moisture <= P10) | days | Full | [0, 38] | 0.0% |
| `hotdrydays_ge35_sms_p10_hema` | 热干复合日数(Tmax >= 35 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and GLEAM surface soil moisture <= P10) | days | HEMA | [0, 11] | 0.0% |
| `hotdrydays_ge35_sms_p10_hepm10` | 热干复合日数(Tmax >= 35 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and GLEAM surface soil moisture <= P10) | days | HEpm10 | [0, 9] | 0.0% |
| `hotdrydays_ge35_sms_p10_v3he` | 热干复合日数(Tmax >= 35 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and GLEAM surface soil moisture <= P10) | days | V3HE | [0, 23] | 0.0% |
| `hotdrydays_ge35_sms_p10_v3pm10` | 热干复合日数(Tmax >= 35 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and GLEAM surface soil moisture <= P10) | days | V3pm10 | [0, 17] | 0.0% |
| `hotdrydays_ge35_sms_p10_v3pre30` | 热干复合日数(Tmax >= 35 degC, GLEAM表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and GLEAM surface soil moisture <= P10) | days | V3pre30 | [0, 22] | 0.0% |
| `hotdrydays_ge35_sms_p20` | 热干复合日数(Tmax >= 35 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and GLEAM surface soil moisture <= P20) | days | Full | [0, 40] | 0.0% |
| `hotdrydays_ge35_sms_p20_hema` | 热干复合日数(Tmax >= 35 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and GLEAM surface soil moisture <= P20) | days | HEMA | [0, 13] | 0.0% |
| `hotdrydays_ge35_sms_p20_hepm10` | 热干复合日数(Tmax >= 35 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and GLEAM surface soil moisture <= P20) | days | HEpm10 | [0, 11] | 0.0% |
| `hotdrydays_ge35_sms_p20_v3he` | 热干复合日数(Tmax >= 35 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and GLEAM surface soil moisture <= P20) | days | V3HE | [0, 25] | 0.0% |
| `hotdrydays_ge35_sms_p20_v3pm10` | 热干复合日数(Tmax >= 35 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and GLEAM surface soil moisture <= P20) | days | V3pm10 | [0, 17] | 0.0% |
| `hotdrydays_ge35_sms_p20_v3pre30` | 热干复合日数(Tmax >= 35 degC, GLEAM表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and GLEAM surface soil moisture <= P20) | days | V3pre30 | [0, 22] | 0.0% |
| `hotdrydays_ge35_swsm_l1_p10` | 热干复合日数(Tmax >= 35 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and SWSM L1 surface soil moisture <= P10) | days | Full | [0, 53] | 0.0% |
| `hotdrydays_ge35_swsm_l1_p10_hema` | 热干复合日数(Tmax >= 35 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and SWSM L1 surface soil moisture <= P10) | days | HEMA | [0, 22] | 0.0% |
| `hotdrydays_ge35_swsm_l1_p10_hepm10` | 热干复合日数(Tmax >= 35 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and SWSM L1 surface soil moisture <= P10) | days | HEpm10 | [0, 17] | 0.0% |
| `hotdrydays_ge35_swsm_l1_p10_v3he` | 热干复合日数(Tmax >= 35 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and SWSM L1 surface soil moisture <= P10) | days | V3HE | [0, 34] | 0.0% |
| `hotdrydays_ge35_swsm_l1_p10_v3pm10` | 热干复合日数(Tmax >= 35 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and SWSM L1 surface soil moisture <= P10) | days | V3pm10 | [0, 17] | 0.0% |
| `hotdrydays_ge35_swsm_l1_p10_v3pre30` | 热干复合日数(Tmax >= 35 degC, SWSM L1表层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and SWSM L1 surface soil moisture <= P10) | days | V3pre30 | [0, 20] | 0.0% |
| `hotdrydays_ge35_swsm_l1_p20` | 热干复合日数(Tmax >= 35 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and SWSM L1 surface soil moisture <= P20) | days | Full | [0, 80] | 0.0% |
| `hotdrydays_ge35_swsm_l1_p20_hema` | 热干复合日数(Tmax >= 35 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and SWSM L1 surface soil moisture <= P20) | days | HEMA | [0, 25] | 0.0% |
| `hotdrydays_ge35_swsm_l1_p20_hepm10` | 热干复合日数(Tmax >= 35 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and SWSM L1 surface soil moisture <= P20) | days | HEpm10 | [0, 20] | 0.0% |
| `hotdrydays_ge35_swsm_l1_p20_v3he` | 热干复合日数(Tmax >= 35 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and SWSM L1 surface soil moisture <= P20) | days | V3HE | [0, 58] | 0.0% |
| `hotdrydays_ge35_swsm_l1_p20_v3pm10` | 热干复合日数(Tmax >= 35 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and SWSM L1 surface soil moisture <= P20) | days | V3pm10 | [0, 17] | 0.0% |
| `hotdrydays_ge35_swsm_l1_p20_v3pre30` | 热干复合日数(Tmax >= 35 degC, SWSM L1表层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and SWSM L1 surface soil moisture <= P20) | days | V3pre30 | [0, 22] | 0.0% |
| `hotdrydays_ge35_swsm_l3_p10` | 热干复合日数(Tmax >= 35 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and SWSM L3 deep soil moisture <= P10) | days | Full | [0, 50] | 0.0% |
| `hotdrydays_ge35_swsm_l3_p10_hema` | 热干复合日数(Tmax >= 35 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and SWSM L3 deep soil moisture <= P10) | days | HEMA | [0, 22] | 0.0% |
| `hotdrydays_ge35_swsm_l3_p10_hepm10` | 热干复合日数(Tmax >= 35 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and SWSM L3 deep soil moisture <= P10) | days | HEpm10 | [0, 19] | 0.0% |
| `hotdrydays_ge35_swsm_l3_p10_v3he` | 热干复合日数(Tmax >= 35 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and SWSM L3 deep soil moisture <= P10) | days | V3HE | [0, 31] | 0.0% |
| `hotdrydays_ge35_swsm_l3_p10_v3pm10` | 热干复合日数(Tmax >= 35 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and SWSM L3 deep soil moisture <= P10) | days | V3pm10 | [0, 17] | 0.0% |
| `hotdrydays_ge35_swsm_l3_p10_v3pre30` | 热干复合日数(Tmax >= 35 degC, SWSM L3深层土壤湿度 <= P10) | Hot-dry days (Tmax >= 35 degC and SWSM L3 deep soil moisture <= P10) | days | V3pre30 | [0, 21] | 0.0% |
| `hotdrydays_ge35_swsm_l3_p20` | 热干复合日数(Tmax >= 35 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and SWSM L3 deep soil moisture <= P20) | days | Full | [0, 77] | 0.0% |
| `hotdrydays_ge35_swsm_l3_p20_hema` | 热干复合日数(Tmax >= 35 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and SWSM L3 deep soil moisture <= P20) | days | HEMA | [0, 30] | 0.0% |
| `hotdrydays_ge35_swsm_l3_p20_hepm10` | 热干复合日数(Tmax >= 35 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and SWSM L3 deep soil moisture <= P20) | days | HEpm10 | [0, 20] | 0.0% |
| `hotdrydays_ge35_swsm_l3_p20_v3he` | 热干复合日数(Tmax >= 35 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and SWSM L3 deep soil moisture <= P20) | days | V3HE | [0, 46] | 0.0% |
| `hotdrydays_ge35_swsm_l3_p20_v3pm10` | 热干复合日数(Tmax >= 35 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and SWSM L3 deep soil moisture <= P20) | days | V3pm10 | [0, 17] | 0.0% |
| `hotdrydays_ge35_swsm_l3_p20_v3pre30` | 热干复合日数(Tmax >= 35 degC, SWSM L3深层土壤湿度 <= P20) | Hot-dry days (Tmax >= 35 degC and SWSM L3 deep soil moisture <= P20) | days | V3pre30 | [0, 24] | 0.0% |

## 12. Yield/SR (7 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `ca` | 秸秆还田比例 | Straw return adoption rate | 0-1 | -- | [0, 1] | 0.0% |
| `crc_ca_ratio` | CRC/CA比例 | CRC to CA ratio | 0-1 | -- | [0, 1] | 0.0% |
| `crc_lag1` | 滞后一期CRC | Lagged CRC adoption | 0-1 | -- | [0, 1] | 8.2% |
| `irr_frac` | 灌溉比例 | Irrigation fraction | 0-1 | -- | [0, 0.9889] | 6.1% |
| `ln_yield` | 对数单产 | Log maize yield | ln(t/ha) | -- | [-1.609, 2.996] | 0.0% |
| `maize_area_km2` | 玉米面积 | Maize planting area | km2 | -- | [0.8479, 98.97] | 0.0% |
| `yield_tons_ha` | 玉米单产 | Maize yield | t/ha | -- | [0.2001, 20] | 0.0% |

## 13. Soil Properties (7 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `aridity` | 干旱度指数 | Aridity index | -- | -- | [0.0123, 5.512] | 0.0% |
| `bdod_0_5cm_01deg` | 容重(0-5 cm) | Bulk density (0-5 cm) | g/cm3 | -- | [0.8933, 1.473] | 6.1% |
| `clay_0_5cm_01deg` | 黏粒含量(0-5 cm) | Clay content (0-5 cm) | % | -- | [9.976, 44.34] | 6.1% |
| `phh2o_0_5cm_01deg` | 土壤pH(0-5 cm) | Soil pH (0-5 cm) | -- | -- | [5.003, 8.975] | 6.2% |
| `pixel_area_km2` | 像元面积 | Pixel area | km2 | -- | [77.59, 114.9] | 0.0% |
| `sand_0_5cm_01deg` | 砂粒含量(0-5 cm) | Sand content (0-5 cm) | % | -- | [7.861, 70.7] | 6.1% |
| `silt_0_5cm_01deg` | 粉粒含量(0-5 cm) | Silt content (0-5 cm) | % | -- | [16.05, 67.24] | 6.1% |

## 14. Admin (8 vars)

| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |
|----------|-----------|-----------|------|--------|-------|----------|
| `city_code` | 地级市代码 | City code | -- | -- | [1.1e+05, 6.59e+05] | 0.0% |
| `city_name` | 地级市名称 | City name | -- | -- | 282 unique | 0.0% |
| `county_code` | 县代码 | County code | -- | -- | [1.101e+05, 6.59e+05] | 0.0% |
| `county_name` | 县名 | County name | -- | -- | 1822 unique | 0.0% |
| `prov_code` | 省份代码 | Province code | -- | -- | [1.1e+05, 6.5e+05] | 0.0% |
| `prov_id` | 省份ID | Province ID | -- | -- | 26 unique | 0.0% |
| `prov_year` | 省份-年份 | Province-year | -- | -- | [1, 102] | 0.0% |
| `province` | 省份名称 | Province name | -- | -- | 26 unique | 0.0% |

---

## Notes

- **Window abbreviations:** Full=full season, V3pre30=30 days before V3, V3pm10=V3 +/- 10 days, HEpm10=HE +/- 10 days, V3HE=V3 to HE, HEMA=HE to MA, FullNew=v3pre30 + v3he + hema with duplicated V3 and HE boundary days removed.
- **Capped GDD:** `gdd_10_29` to `gdd_10_32` use `max(min(t2m_mean, upper_cap)-10, 0)` at the daily scale and then aggregate by window.
- **SM sources:** GLEAM, SWSM, ERA5-Land.
- **SM depth:** Surface corresponds to 0-7/10 cm; root-zone/deep layers correspond to 28-100 cm where applicable.
- **Compound hot-dry sources:** GLEAM root/surface SM, SWSM L1/L3, ERA5-Land swvl1/swvl3, and `pr_lt1`.
- **Legacy baseline-local SM thresholds:** grid-cell historical percentiles; dry-side variables use local P10/P20 and wet-side variables use local P80/P90. Legacy GLEAM baselines use 2013-2020, and SWSM/ERA5-Land baselines use 2016-2019, all over DOY 90-300.
- **GLEAM rework phenology windows:** new GLEAM `md-event family` and `window-baseline family` variables use ChinaCropPhen1km maize V3/HE/MA rasters sampled to the 0.1 degree panel grid, with threshold years 2013-2019 and output years 2016-2019.
- **GLEAM md-event family:** daily GLEAM SM is first converted to 5-day rolling means, then transformed into local pooled-within-window percentiles; dry events use >P40 to <P20 with a minimum drop of 5 percentile-points per 5 days, and wet events mirror this with <P60 to >P80.
- **GLEAM window-baseline family:** thresholds are local, grid-specific, and window-specific, estimated separately for `v3pre30`, `v3he`, and `hema`; `severitymean_*` is the window-average deficit/excess over all valid days, while `severitysum_*` is the cumulative deficit/excess within the window.
- **Pooled-state SM thresholds:** pooled window-specific P25/P75, estimated separately for each source-layer and window.
- **Maize-zone-state SM thresholds:** maize-zone-specific P25/P75, estimated separately for each source-layer, window, and maize zone.
- **Interpretation rule:** legacy `baseline-local`, `pooled-state`, and `maize-zone-state` variables should not be treated as default robustness substitutes for one another.
- **GLEAM rework interpretation rule:** `legacy GLEAM`, `md-event family`, and `window-baseline family` should not be treated as interchangeable definitions by default.
- **Temperature:** ERA5 reanalysis aligned to the 376x616 reference grid.
- **Precipitation:** CHM_PRE aligned to the ERA reference grid by nearest-neighbor mapping.
