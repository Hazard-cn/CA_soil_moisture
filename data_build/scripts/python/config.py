"""
config.py — 数据构建全局配置
Purpose: Define paths, parameters, thresholds for phenological window data build
Author: Data Build Pipeline
Date: 2026-03-28
"""

import os
import numpy as np

# ==============================================================================
# Paths
# ==============================================================================
PROJ_DIR = "C:/YangSu/00_Project/CA_mechanism/regression_SR/data_build"
PARENT_DIR = "C:/YangSu/00_Project/CA_mechanism/regression_SR"

# Raw data (E: drive)
TEMP_DIR = "E:/daily_temp_CN"                          # ERA5 daily temp, 376x616, 2013-2020
PRECIP_FILE = "E:/CHM_PRE_0.1dg_19612022.nc"           # CHM daily precip, 360x640, 1961-2022
VPD_FILE = "E:/CHM_prec/VPD/CHM_VPD.nc"                # Monthly VPD, 360x640
SPEI_DIR = "E:/CHM_prec/SPEI"                           # Monthly SPEI-1..12, 360x640

# Processed intermediates (already aligned to ERA grid unless noted)
GLEAM_DIR = "E:/Processed_Panel_CN_2016-2019/GLEAM_SM_0.1deg_TEMPgrid_2013_2019"  # 376x616
SWSM_DIR = "E:/Processed_Panel_CN_2016-2019/SWSM_L123_0.1deg_aligned_to_temp2019"  # 376x616
ET0_DIR = "E:/Processed_Panel_CN_2016-2019/ET0_0.1deg"  # 376x616
ERA5L_SM_DIR = "D:/Soil_data_sy/netCDF"                    # ERA5-Land SM, 386x631, 2016-2019
PHEN_CA_FILE = "E:/Processed_Panel_CN_2016-2019/MaizePheno_CA_0.1deg_v2/maizephenology_ca_ratio_2016_2019_0p1deg.nc"
CHINA_CROP_PHENO_DIR = "E:/ChinaCropPhen1km"
CHINA_MAIZE_PHENO_DIR = os.path.join(CHINA_CROP_PHENO_DIR, "maize")
CHINA_MAIZE_PROJ4 = (
    "+proj=aea +lat_1=15 +lat_2=65 +lat_0=30 +lon_0=95 "
    "+datum=WGS84 +units=m +no_defs"
)

# Parent v1 data (for comparison)
V1_DATA = os.path.join(PARENT_DIR, "data/processed/data_v1_with_climate.csv")
V1_ANALYSIS_MAIN_DTA = os.path.join(PARENT_DIR, "data/processed/analysis_main_sample.dta")

# Output directories
INTERMEDIATE_DIR = os.path.join(PROJ_DIR, "data/intermediate")
PROCESSED_DIR = os.path.join(PROJ_DIR, "data/processed")
LOG_DIR = os.path.join(PROJ_DIR, "output/logs")
TABLE_DIR = os.path.join(PROJ_DIR, "output/tables")
FIG_DIR = os.path.join(PROJ_DIR, "output/figures")

# ==============================================================================
# Analysis parameters
# ==============================================================================
YEARS = [2016, 2017, 2018, 2019]
BASELINE_YEARS = list(range(2013, 2021))  # 2013-2020 for percentile baselines
GLEAM_REWORK_BASELINE_YEARS = list(range(2013, 2020))  # 2013-2019 for new GLEAM state variables
RANDOM_SEED = 42

# Reference grid (ERA5 temperature)
REF_NLAT = 376
REF_NLON = 616

# ==============================================================================
# Phenological windows
# ==============================================================================
# Scheme A: ±10 days around phenological nodes
# Scheme B: Between-node intervals
WINDOW_PM_DAYS = 10  # ±10 days

WINDOWS = {
    "full":    {"type": "full_season", "suffix": ""},          # v3_doy-30 to ma_doy
    "v3pre30": {"type": "pre", "node": "v3_doy", "offset": -30, "suffix": "_v3pre30"},
    "v3pm10":  {"type": "pm", "node": "v3_doy", "suffix": "_v3pm10"},
    "hepm10":  {"type": "pm", "node": "he_doy", "suffix": "_hepm10"},
    "v3he":    {"type": "between", "start": "v3_doy", "end": "he_doy", "suffix": "_v3he"},
    "hema":    {"type": "between", "start": "he_doy", "end": "ma_doy", "suffix": "_hema"},
}
WINDOW_SUFFIXES = [wdef["suffix"] for wdef in WINDOWS.values()]
FULLNEW_SUFFIX = "_fullnew"
FULLNEW_WINDOW_LABEL = "FullNew"
GLEAM_REWORK_WINDOWS = ["v3pre30", "v3he", "hema"]

# ==============================================================================
# Temperature thresholds
# ==============================================================================
HOT_ABS_THRESHOLDS = [29, 30, 31, 32, 33, 34, 35, 38, 40]  # °C for hotdays/HDD
NIGHTHEAT_THRESHOLDS = [20, 22, 24]                          # °C for tmin-based
TMAX_PERCENTILES = [0.90, 0.95]                               # for baseline percentiles
GDD_BASE_TEMP = 10  # °C
GDD_UPPER_CAPS = [29, 30, 31, 32]
LEGACY_GDD_VAR = f"gdd_ge{GDD_BASE_TEMP}"
CAPPED_GDD_VARS = [f"gdd_{GDD_BASE_TEMP}_{cap}" for cap in GDD_UPPER_CAPS]

# ==============================================================================
# Soil moisture percentiles
# ==============================================================================
SM_DRY_PERCENTILES = [0.10, 0.20]  # for drydays counting
SM_WET_PERCENTILES = [0.80, 0.90]  # for wetdays counting
SM_STATE_PERCENTILES = {"dry": 0.25, "wet": 0.75}  # pooled/zone state thresholds

MAIZE_ZONE_ORDER = ["NE", "HHH", "SW", "SH", "NW", "Other"]
MAIZE_ZONE_MAP = {
    "黑龙江省": "NE",
    "吉林省": "NE",
    "辽宁省": "NE",
    "内蒙古自治区": "NE",
    "河南省": "HHH",
    "山东省": "HHH",
    "河北省": "HHH",
    "安徽省": "HHH",
    "江苏省": "HHH",
    "四川省": "SW",
    "贵州省": "SW",
    "云南省": "SW",
    "广西壮族自治区": "SW",
    "重庆市": "SW",
    "甘肃省": "NW",
    "宁夏回族自治区": "NW",
    "新疆维吾尔自治区": "NW",
    "陕西省": "NW",
    "广东省": "SH",
    "福建省": "SH",
    "浙江省": "SH",
    "江西省": "SH",
    "海南省": "SH",
    "湖南省": "SH",
    "湖北省": "SH",
}

# Compound stress: hotdry days
COMPOUND_HOT_THRESHOLDS = [30, 32, 35]  # Tmax thresholds for compound days
COMPOUND_SM_PERCENTILES = [int(p * 100) for p in SM_DRY_PERCENTILES]

# ==============================================================================
# Precipitation thresholds
# ==============================================================================
DRY_DAY_THRESHOLD = 1.0   # mm, pr < 1mm = dry day
WET_DAY_THRESHOLDS = [10, 20]  # mm, pr >= threshold = wet day
COMPOUND_DRY_SOURCE_REGISTRY = {
    "smrz": {"type": "soil_moisture", "family": "gleam", "field": "SMrz"},
    "sms": {"type": "soil_moisture", "family": "gleam", "field": "SMs"},
    "swsm_l1": {"type": "soil_moisture", "family": "swsm", "field": "L1"},
    "swsm_l3": {"type": "soil_moisture", "family": "swsm", "field": "L3"},
    "era5l_swvl1": {"type": "soil_moisture", "family": "era5l", "field": "swvl1"},
    "era5l_swvl3": {"type": "soil_moisture", "family": "era5l", "field": "swvl3"},
    "pr_lt1": {"type": "precip", "family": "chm", "field": "pre", "threshold_mm": DRY_DAY_THRESHOLD},
}

# ==============================================================================
# Data source grid info (for alignment)
# ==============================================================================
# CHM precipitation/VPD/SPEI grid (different from ERA)
CHM_GRID = {
    "nlat": 360, "nlon": 640,
    "lat_range": (18.05, 53.95),
    "lon_range": (72.05, 135.95),
    "step": 0.1
}

# ==============================================================================
# Output naming
# ==============================================================================
DATA_VERSION = "v3"
OUTPUT_PREFIX = f"data_{DATA_VERSION}_phenowindows"
MAIN_OUTPUT_PREFIX = f"data_{DATA_VERSION}_main"
NOYIELD_OUTPUT_PREFIX = f"data_{DATA_VERSION}_noyield"
DICT_MARKDOWN_NAME = f"VARIABLES_{DATA_VERSION}.md"
DICT_TABLE_NAME = f"data_dictionary_{DATA_VERSION}.csv"
QUALITY_TABLE_NAME = f"descriptive_stats_{DATA_VERSION}.csv"
STATA_ALIAS_TABLE_NAME = f"stata_alias_map_{DATA_VERSION}.csv"
STATA_ALIAS_MARKDOWN_NAME = f"stata_alias_map_{DATA_VERSION}.md"

PHENOWINDOWS_CSV = os.path.join(PROCESSED_DIR, f"{OUTPUT_PREFIX}.csv")
PHENOWINDOWS_PARQUET = os.path.join(PROCESSED_DIR, f"{OUTPUT_PREFIX}.parquet")
PHENOWINDOWS_DTA = os.path.join(PROCESSED_DIR, f"{OUTPUT_PREFIX}.dta")
MAIN_CSV = os.path.join(PROCESSED_DIR, f"{MAIN_OUTPUT_PREFIX}.csv")
MAIN_PARQUET = os.path.join(PROCESSED_DIR, f"{MAIN_OUTPUT_PREFIX}.parquet")
MAIN_DTA = os.path.join(PROCESSED_DIR, f"{MAIN_OUTPUT_PREFIX}.dta")
NOYIELD_PARQUET = os.path.join(PROCESSED_DIR, f"{NOYIELD_OUTPUT_PREFIX}.parquet")
DICT_MARKDOWN_PATH = os.path.join(PROJ_DIR, "docs", DICT_MARKDOWN_NAME)
DICT_TABLE_PATH = os.path.join(TABLE_DIR, DICT_TABLE_NAME)
QUALITY_TABLE_PATH = os.path.join(TABLE_DIR, QUALITY_TABLE_NAME)
STATA_ALIAS_TABLE_PATH = os.path.join(TABLE_DIR, STATA_ALIAS_TABLE_NAME)
STATA_ALIAS_MARKDOWN_PATH = os.path.join(PARENT_DIR, "temp", STATA_ALIAS_MARKDOWN_NAME)
GLEAM_REWORK_INTERMEDIATE = os.path.join(INTERMEDIATE_DIR, "sm_gleam_rework_windows.csv")

# ==============================================================================
# Ensure output directories exist
# ==============================================================================
for d in [INTERMEDIATE_DIR, PROCESSED_DIR, LOG_DIR, TABLE_DIR, FIG_DIR, os.path.dirname(STATA_ALIAS_MARKDOWN_PATH)]:
    os.makedirs(d, exist_ok=True)
