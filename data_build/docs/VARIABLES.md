# Variables

本文件给出 `data/processed/data_v1_with_climate.csv` 的变量字典。若后续数据版本更新，请以同名清单文件同步更新本表。

| 变量名 | 含义/口径 |
|---|---|
| `year` | 年份 |
| `latitude` | 格网中心纬度（度） |
| `longitude` | 格网中心经度（度） |
| `t2m_mean` | 阶段内日均温的平均值（t2m_mean） |
| `lag30_t2m_mean` | 滞后30天窗口的阶段内日均温的平均值（t2m_mean） |
| `t2m_min` | 阶段内日均温的最小值（t2m_min） |
| `lag30_t2m_min` | 滞后30天窗口的阶段内日均温的最小值（t2m_min） |
| `t2m_max` | 阶段内日均温的最大值（t2m_max） |
| `lag30_t2m_max` | 滞后30天窗口的阶段内日均温的最大值（t2m_max） |
| `tmax_mean` | 阶段内日最高温的平均值（tmax_mean） |
| `lag30_tmax_mean` | 滞后30天窗口的阶段内日最高温的平均值（tmax_mean） |
| `tmax_min` | 阶段内日最高温的最小值（tmax_min） |
| `lag30_tmax_min` | 滞后30天窗口的阶段内日最高温的最小值（tmax_min） |
| `tmax_max` | 阶段内日最高温的最大值（tmax_max） |
| `lag30_tmax_max` | 滞后30天窗口的阶段内日最高温的最大值（tmax_max） |
| `tmin_mean` | 阶段内日最低温的平均值（tmin_mean） |
| `lag30_tmin_mean` | 滞后30天窗口的阶段内日最低温的平均值（tmin_mean） |
| `tmin_min` | 阶段内日最低温的最小值（tmin_min） |
| `lag30_tmin_min` | 滞后30天窗口的阶段内日最低温的最小值（tmin_min） |
| `tmin_max` | 阶段内日最低温的最大值（tmin_max） |
| `lag30_tmin_max` | 滞后30天窗口的阶段内日最低温的最大值（tmin_max） |
| `pr_sum` | 阶段内降水累计（pr_sum） |
| `lag30_pr_sum` | 滞后30天窗口的阶段内降水累计（pr_sum） |
| `vpd_mean` | 阶段内VPD均值（vpd_mean） |
| `lag30_vpd_mean` | 滞后30天窗口的阶段内VPD均值（vpd_mean） |
| `gleam_smrz_mean` | 阶段内根区土壤水分均值（SMrz, mean） |
| `lag30_gleam_smrz_mean` | 滞后30天窗口的阶段内根区土壤水分均值（SMrz, mean） |
| `gleam_sms_mean` | 阶段内表层土壤水分均值（SMs, mean） |
| `lag30_gleam_sms_mean` | 滞后30天窗口的阶段内表层土壤水分均值（SMs, mean） |
| `days_in_stage` | 本阶段窗口天数（用于聚合的日数） |
| `et0_sum` | 阶段内潜在蒸散ET0累计（ET0，sum） |
| `wd_deficit_et0minuspre` | 水分亏缺指标（ET0累计减降水累计） |
| `wd_aridity_et0divpre` | 干旱度指标（ET0累计除以降水累计） |
| `hotdays_tmax_ge29` | 高温天数（Tmax≥29，天） |
| `hotdays_tmax_ge30` | 高温天数（Tmax≥30，天） |
| `hotdays_tmax_ge31` | 高温天数（Tmax≥31，天） |
| `hotdays_tmax_ge32` | 高温天数（Tmax≥32，天） |
| `hotdays_tmax_ge33` | 高温天数（Tmax≥33，天） |
| `hotdays_tmax_ge34` | 高温天数（Tmax≥34，天） |
| `hotdays_tmax_ge35` | 高温天数（Tmax≥35，天） |
| `hotdays_tmax_ge38` | 高温天数（Tmax≥38，天） |
| `hotdays_tmax_ge40` | 高温天数（Tmax≥40，天） |
| `hdd_tmax_ge29` | 高温强度HDD（∑max(Tmax-29,0)，度日） |
| `hdd_tmax_ge30` | 高温强度HDD（∑max(Tmax-30,0)，度日） |
| `hdd_tmax_ge31` | 高温强度HDD（∑max(Tmax-31,0)，度日） |
| `hdd_tmax_ge32` | 高温强度HDD（∑max(Tmax-32,0)，度日） |
| `hdd_tmax_ge33` | 高温强度HDD（∑max(Tmax-33,0)，度日） |
| `hdd_tmax_ge34` | 高温强度HDD（∑max(Tmax-34,0)，度日） |
| `hdd_tmax_ge35` | 高温强度HDD（∑max(Tmax-35,0)，度日） |
| `hotdays_tmax_ge_basep90` | 高温天数（Tmax≥基准期p90阈值，天） |
| `hdd_tmax_ge_basep90` | 高温强度HDD（∑max(Tmax?基准期p90,0)，度日） |
| `hotdays_tmax_ge_basep95` | 高温天数（Tmax≥基准期p95阈值，天） |
| `hdd_tmax_ge_basep95` | 高温强度HDD（∑max(Tmax?基准期p95,0)，度日） |
| `drydays_pre_lt1` | 干旱日数：降水小于1mm（天） |
| `drydays_gleam_smrz_le_basep10` | 干旱日数：根区土壤水分SMrz低于等于基准p10阈值（天） |
| `drydays_gleam_sms_le_basep10` | 干旱日数：表层土壤水分SMs低于等于基准p10阈值（天） |
| `drydays_gleam_smrz_le_basep20` | 干旱日数：根区土壤水分SMrz低于等于基准p20阈值（天） |
| `drydays_gleam_sms_le_basep20` | 干旱日数：表层土壤水分SMs低于等于基准p20阈值（天） |
| `hotdrydays_tmax_ge32_and_smrz_le_basep20` | 复合极端日数：高温(Tmax≥32)且干旱(SMrz≤基准p20)（天） |
| `hotdrydays_tmax_ge32_and_smrz_le_basep10` | 复合极端日数：高温(Tmax≥32)且干旱(SMrz≤基准p10)（天） |
| `gdd_t2m_ge10` | 生长度日GDD（∑max(T2m-10,0)，度日） |
| `v3_doy` | V3物候日序（DOY） |
| `he_doy` | HE物候日序（DOY） |
| `ma_doy` | MA物候日序（DOY） |
| `crc_ca_ratio` | 保护性耕作采纳比例（CA ratio，当年） |
| `crc_lag1` | 保护性耕作采纳比例（CA ratio，滞后1年） |
| `irr_frac` | 灌溉比例或灌溉覆盖（IRR_frac） |
| `bdod_01deg` | 土壤容重（Bulk Density, 0.1度） |
| `clay_01deg` | 土壤粘粒含量（Clay, 0.1度） |
| `sand_01deg` | 土壤砂粒含量（Sand, 0.1度） |
| `silt_01deg` | 土壤粉粒含量（Silt, 0.1度） |
| `phh2o_01deg` | 土壤pH（pH in H2O, 0.1度） |
| `aridity_01deg` | 干旱指数（Aridity, 0.1度） |
| `pixel_mask` | 像元掩膜（有效像元标记） |
| `maizepix_full` | 0.1度格内玉米像元数：全生育期有效像元计数（1km像元个数） |
| `maizefrac_full` | 0.1度格内玉米覆盖比例：全生育期有效像元占比 |
| `maizepix_v3` | 0.1度格内玉米像元数：V3阶段有效像元计数（1km像元个数） |
| `maizefrac_v3` | 0.1度格内玉米覆盖比例：V3阶段有效像元占比 |
| `maizepix_he` | 0.1度格内玉米像元数：HE阶段有效像元计数（1km像元个数） |
| `maizefrac_he` | 0.1度格内玉米覆盖比例：HE阶段有效像元占比 |
| `maizepix_ma` | 0.1度格内玉米像元数：MA阶段有效像元计数（1km像元个数） |
| `maizefrac_ma` | 0.1度格内玉米覆盖比例：MA阶段有效像元占比 |
| `maizepix_minv3hema` | 保守玉米像元数：min(V3,HE,MA)有效像元计数（1km像元个数） |
| `maizefrac_minv3hema` | 保守玉米覆盖比例：min(V3,HE,MA)有效像元占比 |
| `china_prod` | 待补充 |
| `pixel_code` | 待补充 |
| `grid_id` | group(latitude longitude) |
| `prov_id` | group(province) |
| `prov_year` | group(prov_id year) |
| `ca` | CA采纳比率 |
| `maize_area_km2` | maize种植面积 |
| `maize_yield_km2` | 待补充 |
| `yield_tons_ha` | Maize Yield (tons/ha) |
| `ln_yield` | ln Maize Yield (tons/ha) |
| `SPEI_season` | SPEI |
| `VPD_season_mean` | VPD |
