"""
gen_data_dictionary.py -- Auto-generate versioned data dictionary
Purpose: Create VARIABLES_v3.md and data_dictionary_v3.csv from actual panel columns
Author: Data Build Pipeline
Date: 2026-04-22
Input: data/processed/data_v3_main.parquet
Output: docs/VARIABLES_v3.md, output/tables/data_dictionary_v3.csv
"""

import os
import re
import sys
from datetime import date

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

np.random.seed(RANDOM_SEED)


CATEGORY_ORDER = [
    "Identifiers",
    "Phenology",
    "Temperature",
    "Heat Indices",
    "Precipitation",
    "SM-GLEAM",
    "SM-SWSM",
    "SM-ERA5Land",
    "ET0/Water Balance",
    "VPD/SPEI",
    "Compound Stress",
    "Yield/SR",
    "Soil Properties",
    "Admin",
]

STATE_CLASS_ORDER = ["raw/core", "baseline-local", "pooled-state", "maize-zone-state"]
GLEAM_DOC_GROUP_ORDER = [
    "legacy baseline-local",
    "legacy pooled-state",
    "legacy maize-zone-state",
    "md-event family",
    "window-baseline family",
]

WINDOW_DISPLAY = {
    "": "Full",
    "_v3pre30": "V3pre30",
    "_v3pm10": "V3pm10",
    "_hepm10": "HEpm10",
    "_v3he": "V3HE",
    "_hema": "HEMA",
    FULLNEW_SUFFIX: FULLNEW_WINDOW_LABEL,
}

WINDOW_PROP_CN = {
    "full": "全生育期",
    "v3pre30": "V3前30天",
    "v3pm10": "V3前后10天",
    "hepm10": "HE前后10天",
    "v3he": "V3到HE",
    "hema": "HE到MA",
}

WINDOW_PROP_EN = {
    "full": "Full season",
    "v3pre30": "30 days before V3",
    "v3pm10": "V3 +/- 10 days",
    "hepm10": "HE +/- 10 days",
    "v3he": "V3 to HE",
    "hema": "HE to MA",
}

SM_SOURCE_CATEGORY_MAP = {
    "gleam_smrz": "SM-GLEAM",
    "gleam_sms": "SM-GLEAM",
    "swsm_l1": "SM-SWSM",
    "swsm_l3": "SM-SWSM",
    "era5l_swvl1": "SM-ERA5Land",
    "era5l_swvl3": "SM-ERA5Land",
}
SM_SOURCE_TOKENS = tuple(SM_SOURCE_CATEGORY_MAP.keys())

CURATED_LABELS = {
    "grid_id": ("格点ID", "Grid cell ID", "--"),
    "year": ("年份", "Year", "--"),
    "latitude": ("纬度", "Latitude", "degN"),
    "longitude": ("经度", "Longitude", "degE"),
    "lat_idx": ("纬度索引", "Latitude index", "--"),
    "lon_idx": ("经度索引", "Longitude index", "--"),
    "v3_doy": ("V3日期", "V3 day of year", "DOY"),
    "he_doy": ("HE日期", "HE day of year", "DOY"),
    "ma_doy": ("MA日期", "MA day of year", "DOY"),
    "maize_frac": ("玉米种植比例", "Maize planting fraction", "0-1"),
    "ca_ratio": ("CA比例", "Conservation agriculture ratio", "0-1"),
    "yield_tons_ha": ("玉米单产", "Maize yield", "t/ha"),
    "ln_yield": ("对数单产", "Log maize yield", "ln(t/ha)"),
    "ca": ("秸秆还田比例", "Straw return adoption rate", "0-1"),
    "crc_ca_ratio": ("CRC/CA比例", "CRC to CA ratio", "0-1"),
    "crc_lag1": ("滞后一期CRC", "Lagged CRC adoption", "0-1"),
    "irr_frac": ("灌溉比例", "Irrigation fraction", "0-1"),
    "maize_area_km2": ("玉米面积", "Maize planting area", "km2"),
    "bdod_0_5cm_01deg": ("容重(0-5 cm)", "Bulk density (0-5 cm)", "g/cm3"),
    "clay_0_5cm_01deg": ("黏粒含量(0-5 cm)", "Clay content (0-5 cm)", "%"),
    "sand_0_5cm_01deg": ("砂粒含量(0-5 cm)", "Sand content (0-5 cm)", "%"),
    "silt_0_5cm_01deg": ("粉粒含量(0-5 cm)", "Silt content (0-5 cm)", "%"),
    "phh2o_0_5cm_01deg": ("土壤pH(0-5 cm)", "Soil pH (0-5 cm)", "--"),
    "aridity": ("干旱度指数", "Aridity index", "--"),
    "pixel_area_km2": ("像元面积", "Pixel area", "km2"),
    "prov_id": ("省份ID", "Province ID", "--"),
    "prov_year": ("省份-年份", "Province-year", "--"),
    "prov_code": ("省份代码", "Province code", "--"),
    "province": ("省份名称", "Province name", "--"),
    "county_name": ("县名", "County name", "--"),
    "county_code": ("县代码", "County code", "--"),
    "city_name": ("地级市名称", "City name", "--"),
    "city_code": ("地级市代码", "City code", "--"),
}

BASE_LABELS = {
    "t2m": ("平均气温", "Mean temperature", "degC"),
    "tmax": ("最高气温", "Maximum temperature", "degC"),
    "tmin": ("最低气温", "Minimum temperature", "degC"),
    "dtr": ("日较差", "Diurnal temperature range", "degC"),
    "pr": ("降水", "Precipitation", "mm"),
    "gleam_smrz": ("GLEAM根区土壤湿度", "GLEAM root-zone soil moisture", "m3/m3"),
    "gleam_sms": ("GLEAM表层土壤湿度", "GLEAM surface soil moisture", "m3/m3"),
    "swsm_l1": ("SWSM L1表层土壤湿度", "SWSM L1 surface soil moisture", "m3/m3"),
    "swsm_l3": ("SWSM L3深层土壤湿度", "SWSM L3 deep soil moisture", "m3/m3"),
    "era5l_swvl1": ("ERA5-Land swvl1表层土壤湿度", "ERA5-Land swvl1 surface soil moisture", "m3/m3"),
    "era5l_swvl3": ("ERA5-Land swvl3根区土壤湿度", "ERA5-Land swvl3 root-zone soil moisture", "m3/m3"),
    "et0": ("参考蒸散", "Reference evapotranspiration", "mm"),
    "vpd": ("水汽压亏缺", "Vapor pressure deficit", "hPa"),
    "wd_deficit": ("水分亏缺", "Water deficit (ET0-P)", "mm"),
}

SOURCE_LABELS = {
    "gleam_smrz": ("GLEAM根区土壤湿度", "GLEAM root-zone soil moisture"),
    "gleam_sms": ("GLEAM表层土壤湿度", "GLEAM surface soil moisture"),
    "swsm_l1": ("SWSM L1表层土壤湿度", "SWSM L1 surface soil moisture"),
    "swsm_l3": ("SWSM L3深层土壤湿度", "SWSM L3 deep soil moisture"),
    "era5l_swvl1": ("ERA5-Land swvl1表层土壤湿度", "ERA5-Land swvl1 surface soil moisture"),
    "era5l_swvl3": ("ERA5-Land swvl3根区土壤湿度", "ERA5-Land swvl3 root-zone soil moisture"),
    "smrz": ("GLEAM根区土壤湿度", "GLEAM root-zone soil moisture"),
    "sms": ("GLEAM表层土壤湿度", "GLEAM surface soil moisture"),
    "pr_lt1": ("日降水<1 mm", "Daily precipitation < 1 mm"),
}

STAT_LABELS = {
    "mean": ("均值", "mean"),
    "sum": ("总量", "sum"),
    "min": ("最小值", "min"),
    "max": ("最大值", "max"),
    "sd": ("标准差", "std dev"),
    "coverage": ("覆盖率", "temporal coverage fraction"),
    "intensity": ("强度", "intensity"),
}


def strip_window_suffix(col):
    suffixes = list(WINDOW_SUFFIXES[1:]) + [FULLNEW_SUFFIX]
    for suffix in sorted(suffixes, key=len, reverse=True):
        if col.endswith(suffix):
            return col[: -len(suffix)]
    return col


def _sm_unit(source):
    return BASE_LABELS[source][2]


def _state_scope_labels(scope):
    if scope == "local":
        return "本地历史阈值", "local historical threshold"
    if scope == "pl":
        return "pooled窗口阈值", "pooled window-specific threshold"
    if scope == "mz":
        return "maize-zone窗口阈值", "maize-zone-specific threshold"
    raise ValueError(f"Unknown scope: {scope}")


def extract_sm_source_token(col_base):
    for source in SM_SOURCE_TOKENS:
        if col_base == source or col_base.startswith(source + "_"):
            return source

    patterns = [
        r"^(?:drydays|wetdays|dryshare|wetshare|drydeficit|wetexcess)_(?:pl_|mz_)?"
        r"(gleam_smrz|gleam_sms|swsm_l1|swsm_l3|era5l_swvl1|era5l_swvl3)_(?:le|ge)_p\d+$",
        r"^(?:mdduration|mddurshare|mdseverity)_(?:dry|wet)_(gleam_smrz|gleam_sms)$",
        r"^(?:blduration|bldurshare)_(?:dry|wet)_(gleam_smrz|gleam_sms)_p\d+$",
        r"^(?:blseveritymean|blseveritysum)_(?:ddf|wex)_(gleam_smrz|gleam_sms)_p\d+$",
    ]
    for pattern in patterns:
        match = re.match(pattern, col_base)
        if match:
            return match.group(1)
    return None


def detect_state_class(col):
    col_base = strip_window_suffix(col)

    if re.match(r"^(dryshare|wetshare|drydeficit|wetexcess)_pl_", col_base):
        return "pooled-state"
    if re.match(r"^(dryshare|wetshare|drydeficit|wetexcess)_mz_", col_base):
        return "maize-zone-state"
    if re.match(
        r"^(drydays|wetdays|dryshare|wetshare|drydeficit|wetexcess)_"
        r"(gleam_smrz|gleam_sms|swsm_l1|swsm_l3|era5l_swvl1|era5l_swvl3)_(?:le|ge)_p\d+$",
        col_base,
    ):
        return "baseline-local"
    return "raw/core"


def classify_column(col):
    col_base = strip_window_suffix(col)
    sm_source = extract_sm_source_token(col_base)

    if col in ("grid_id", "year", "latitude", "longitude", "lat_idx", "lon_idx"):
        return "Identifiers"
    if col in ("v3_doy", "he_doy", "ma_doy", "maize_frac", "ca_ratio") or col.startswith("win_"):
        return "Phenology"
    if col.startswith(("prov", "county", "city")):
        return "Admin"
    if col in ("yield_tons_ha", "ln_yield", "ca", "crc_ca_ratio", "crc_lag1", "irr_frac", "maize_area_km2"):
        return "Yield/SR"
    if col.startswith(("bdod_", "clay_", "sand_", "silt_", "phh2o_")) or col in ("aridity", "pixel_area_km2"):
        return "Soil Properties"
    if col.startswith("hotdrydays_"):
        return "Compound Stress"
    if sm_source is not None:
        return SM_SOURCE_CATEGORY_MAP[sm_source]
    if col.startswith(("t2m_", "tmax_", "tmin_", "dtr_")):
        return "Temperature"
    if col.startswith(("hotdays_", "hdd_", "nightheat_", "gdd_")):
        return "Heat Indices"
    if (
        col.startswith("pr_")
        or col.startswith("drydays_lt1")
        or re.match(r"^wetdays_ge\d+", col_base)
        or col.startswith("max_c")
        or col.startswith("pr_intensity")
        or col.startswith("pr_concentration")
    ):
        return "Precipitation"
    if col.startswith("et0_") or col.startswith("wd_"):
        return "ET0/Water Balance"
    if col.startswith("vpd_") or col.startswith("spei"):
        return "VPD/SPEI"
    return "Other"


def detect_sm_doc_group(col):
    category = classify_column(col)
    if category != "SM-GLEAM":
        return "--"

    col_base = strip_window_suffix(col)
    if re.match(r"^(mdduration|mddurshare|mdseverity)_(dry|wet)_", col_base):
        return "md-event family"
    if re.match(r"^(blduration|bldurshare)_(dry|wet)_", col_base):
        return "window-baseline family"
    if re.match(r"^(blseveritymean|blseveritysum)_(ddf|wex)_", col_base):
        return "window-baseline family"

    state_class = detect_state_class(col)
    if state_class in ("raw/core", "baseline-local"):
        return "legacy baseline-local"
    if state_class == "pooled-state":
        return "legacy pooled-state"
    if state_class == "maize-zone-state":
        return "legacy maize-zone-state"
    return "--"


def detect_window(col):
    for suffix, label in WINDOW_DISPLAY.items():
        if suffix and col.endswith(suffix):
            return label

    if col.startswith("win_"):
        match = re.match(r"win_(full|v3pre30|v3pm10|hepm10|v3he|hema)_(start|end|days)", col)
        if match:
            return WINDOW_PROP_EN.get(match.group(1), "--")

    if classify_column(col) in {
        "Temperature",
        "Heat Indices",
        "Precipitation",
        "SM-GLEAM",
        "SM-SWSM",
        "SM-ERA5Land",
        "ET0/Water Balance",
        "VPD/SPEI",
        "Compound Stress",
    }:
        return "Full"
    return "--"


def auto_label(col):
    col_base = strip_window_suffix(col)

    match = re.match(r"(hdd|hotdays)_ge(\d+)$", col_base)
    if match:
        metric, thresh = match.groups()
        if metric == "hdd":
            return f"高温积温(>= {thresh} degC)", f"Heating degree days (Tmax >= {thresh} degC)", "degC-days"
        return f"高温日数(>= {thresh} degC)", f"Hot days (Tmax >= {thresh} degC)", "days"

    match = re.match(r"(hdd|hotdays)_ge_basep(\d+)$", col_base)
    if match:
        metric, pct = match.groups()
        if metric == "hdd":
            return f"高温积温(>= P{pct})", f"HDD (Tmax >= P{pct} baseline)", "degC-days"
        return f"高温日数(>= P{pct})", f"Hot days (Tmax >= P{pct} baseline)", "days"

    match = re.match(r"nightheat_ge(\d+)$", col_base)
    if match:
        thresh = match.group(1)
        return f"夜间高温日数(>= {thresh} degC)", f"Night heat days (Tmin >= {thresh} degC)", "days"

    match = re.match(r"gdd_(\d+)_(\d+)$", col_base)
    if match:
        base, cap = match.groups()
        return (
            f"生长度日(基温{base} degC, 上限{cap} degC)",
            f"Growing degree days (base {base} degC, upper cap {cap} degC)",
            "degC-days",
        )

    match = re.match(r"gdd_ge(\d+)$", col_base)
    if match:
        base = match.group(1)
        return f"生长度日(基温{base} degC)", f"Growing degree days (base {base} degC)", "degC-days"

    match = re.match(r"drydays_lt(\d+)$", col_base)
    if match:
        thresh = match.group(1)
        return f"干日数(降水 < {thresh} mm)", f"Dry days (precipitation < {thresh} mm)", "days"

    match = re.match(r"wetdays_ge(\d+)$", col_base)
    if match:
        thresh = match.group(1)
        return f"湿日数(降水 >= {thresh} mm)", f"Wet days (precipitation >= {thresh} mm)", "days"

    match = re.match(
        r"^(drydays|wetdays|dryshare|wetshare|drydeficit|wetexcess)_"
        r"(gleam_smrz|gleam_sms|swsm_l1|swsm_l3|era5l_swvl1|era5l_swvl3)_(le|ge)_p(\d+)$",
        col_base,
    )
    if match:
        metric, source, _, pct = match.groups()
        cn_source, en_source = SOURCE_LABELS[source]
        unit = "days" if metric.endswith("days") else ("0-1" if "share" in metric else _sm_unit(source))
        if metric == "drydays":
            return f"{cn_source}低于本地历史P{pct}的日数", f"Days with {en_source} <= local historical P{pct}", unit
        if metric == "wetdays":
            return f"{cn_source}高于本地历史P{pct}的日数", f"Days with {en_source} >= local historical P{pct}", unit
        if metric == "dryshare":
            return f"{cn_source}低于本地历史P{pct}的日占比", f"Share of valid days with {en_source} <= local historical P{pct}", unit
        if metric == "wetshare":
            return f"{cn_source}高于本地历史P{pct}的日占比", f"Share of valid days with {en_source} >= local historical P{pct}", unit
        if metric == "drydeficit":
            return f"{cn_source}低于本地历史P{pct}的平均亏缺", f"Mean deficit below local historical P{pct} for {en_source}", unit
        return f"{cn_source}高于本地历史P{pct}的平均超额", f"Mean excess above local historical P{pct} for {en_source}", unit

    match = re.match(
        r"^(dryshare|wetshare|drydeficit|wetexcess)_(pl|mz)_"
        r"(gleam_smrz|gleam_sms|swsm_l1|swsm_l3|era5l_swvl1|era5l_swvl3)_(le|ge)_p(\d+)$",
        col_base,
    )
    if match:
        metric, scope, source, _, pct = match.groups()
        cn_source, en_source = SOURCE_LABELS[source]
        cn_scope, en_scope = _state_scope_labels(scope)
        unit = "0-1" if "share" in metric else _sm_unit(source)
        if metric == "dryshare":
            return f"{cn_source}低于{cn_scope}P{pct}的日占比", f"Share of valid days with {en_source} <= {en_scope} P{pct}", unit
        if metric == "wetshare":
            return f"{cn_source}高于{cn_scope}P{pct}的日占比", f"Share of valid days with {en_source} >= {en_scope} P{pct}", unit
        if metric == "drydeficit":
            return f"{cn_source}低于{cn_scope}P{pct}的平均亏缺", f"Mean deficit below {en_scope} P{pct} for {en_source}", unit
        return f"{cn_source}高于{cn_scope}P{pct}的平均超额", f"Mean excess above {en_scope} P{pct} for {en_source}", unit

    match = re.match(r"^mdduration_(dry|wet)_(gleam_smrz|gleam_sms)$", col_base)
    if match:
        side, source = match.groups()
        cn_source, en_source = SOURCE_LABELS[source]
        side_cn = "干旱" if side == "dry" else "过湿"
        side_en = "dry" if side == "dry" else "wet"
        return f"{cn_source}{side_cn}事件持续期总和", f"Season-total duration of {side_en} events for {en_source}", "days"

    match = re.match(r"^mddurshare_(dry|wet)_(gleam_smrz|gleam_sms)$", col_base)
    if match:
        side, source = match.groups()
        cn_source, en_source = SOURCE_LABELS[source]
        side_cn = "干旱" if side == "dry" else "过湿"
        side_en = "dry" if side == "dry" else "wet"
        return f"{cn_source}{side_cn}事件持续期占比", f"Share of season days in {side_en} events for {en_source}", "0-1"

    match = re.match(r"^mdseverity_(dry|wet)_(gleam_smrz|gleam_sms)$", col_base)
    if match:
        side, source = match.groups()
        cn_source, en_source = SOURCE_LABELS[source]
        side_cn = "干旱" if side == "dry" else "过湿"
        side_en = "dry" if side == "dry" else "wet"
        return f"{cn_source}{side_cn}事件严重度总和", f"Season-total event severity for {side_en} events in {en_source}", "percentile-points"

    match = re.match(r"^blduration_(dry|wet)_(gleam_smrz|gleam_sms)_p(\d+)$", col_base)
    if match:
        side, source, pct = match.groups()
        cn_source, en_source = SOURCE_LABELS[source]
        op_cn = "低于" if side == "dry" else "高于"
        op_en = "<=" if side == "dry" else ">="
        return f"{cn_source}{op_cn}本地窗口P{pct}的日数", f"Days with {en_source} {op_en} local window-specific P{pct}", "days"

    match = re.match(r"^bldurshare_(dry|wet)_(gleam_smrz|gleam_sms)_p(\d+)$", col_base)
    if match:
        side, source, pct = match.groups()
        cn_source, en_source = SOURCE_LABELS[source]
        op_cn = "低于" if side == "dry" else "高于"
        op_en = "<=" if side == "dry" else ">="
        return f"{cn_source}{op_cn}本地窗口P{pct}的日占比", f"Share of valid days with {en_source} {op_en} local window-specific P{pct}", "0-1"

    match = re.match(r"^blseveritymean_(ddf|wex)_(gleam_smrz|gleam_sms)_p(\d+)$", col_base)
    if match:
        metric, source, pct = match.groups()
        cn_source, en_source = SOURCE_LABELS[source]
        if metric == "ddf":
            return f"{cn_source}低于本地窗口P{pct}的平均亏缺", f"Mean deficit below local window-specific P{pct} for {en_source}", _sm_unit(source)
        return f"{cn_source}高于本地窗口P{pct}的平均超额", f"Mean excess above local window-specific P{pct} for {en_source}", _sm_unit(source)

    match = re.match(r"^blseveritysum_(ddf|wex)_(gleam_smrz|gleam_sms)_p(\d+)$", col_base)
    if match:
        metric, source, pct = match.groups()
        cn_source, en_source = SOURCE_LABELS[source]
        if metric == "ddf":
            return f"{cn_source}低于本地窗口P{pct}的累计亏缺", f"Sum deficit below local window-specific P{pct} for {en_source}", _sm_unit(source)
        return f"{cn_source}高于本地窗口P{pct}的累计超额", f"Sum excess above local window-specific P{pct} for {en_source}", _sm_unit(source)

    match = re.match(r"hotdrydays_ge(\d+)_(smrz|sms|swsm_l1|swsm_l3|era5l_swvl1|era5l_swvl3)_p(\d+)$", col_base)
    if match:
        thresh, source, pct = match.groups()
        cn_source, en_source = SOURCE_LABELS.get(source, (source, source))
        return (
            f"热干复合日数(Tmax >= {thresh} degC, {cn_source} <= P{pct})",
            f"Hot-dry days (Tmax >= {thresh} degC and {en_source} <= P{pct})",
            "days",
        )

    match = re.match(r"hotdrydays_ge(\d+)_pr_lt1$", col_base)
    if match:
        thresh = match.group(1)
        cn_source, en_source = SOURCE_LABELS["pr_lt1"]
        return (
            f"热干复合日数(Tmax >= {thresh} degC, {cn_source})",
            f"Hot-dry days (Tmax >= {thresh} degC and {en_source})",
            "days",
        )

    match = re.match(r"spei(\d+)_(mean|max|min)$", col_base)
    if match:
        scale, stat = match.groups()
        return f"SPEI-{scale}{STAT_LABELS[stat][0]}", f"SPEI-{scale} {STAT_LABELS[stat][1]}", "--"

    if col_base == "max_cdd":
        return "最长连续干日", "Maximum consecutive dry days", "days"
    if col_base == "max_cwd":
        return "最长连续湿日", "Maximum consecutive wet days", "days"

    match = re.match(r"win_(full|v3pre30|v3pm10|hepm10|v3he|hema)_(start|end|days)$", col)
    if match:
        window_name, prop = match.groups()
        prop_cn = {"start": "起始DOY", "end": "结束DOY", "days": "窗口天数"}[prop]
        prop_en = {"start": "window start", "end": "window end", "days": "window length"}[prop]
        unit = "days" if prop == "days" else "DOY"
        return f"{WINDOW_PROP_CN[window_name]}{prop_cn}", f"{WINDOW_PROP_EN[window_name]} {prop_en}", unit

    if col_base in BASE_LABELS:
        return BASE_LABELS[col_base]

    for base, (cn_base, en_base, unit) in BASE_LABELS.items():
        if col_base.startswith(base + "_"):
            stat = col_base[len(base) + 1 :]
            if stat in STAT_LABELS:
                cn_stat, en_stat = STAT_LABELS[stat]
                return f"{cn_base}{cn_stat}", f"{en_base} {en_stat}", unit
            if col_base == "pr_intensity":
                return "降水强度", "Precipitation intensity (rain-day mean)", "mm/day"
            if col_base == "pr_concentration":
                return "降水集中度", "Precipitation concentration", "--"

    return col, col, "--"


def generate_dictionary(df):
    rows = []
    for col in df.columns:
        if col in CURATED_LABELS:
            cn_label, en_label, unit = CURATED_LABELS[col]
        else:
            cn_label, en_label, unit = auto_label(col)

        if np.issubdtype(df[col].dtype, np.number):
            vmin = df[col].min()
            vmax = df[col].max()
            range_str = f"[{vmin:.4g}, {vmax:.4g}]"
        elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            range_str = f"{df[col].nunique()} unique"
        else:
            range_str = "--"

        rows.append(
            {
                "Variable": col,
                "Category": classify_column(col),
                "State_Class": detect_state_class(col),
                "SM_Doc_Group": detect_sm_doc_group(col),
                "Window": detect_window(col),
                "Label_CN": cn_label,
                "Label_EN": en_label,
                "Unit": unit,
                "Dtype": str(df[col].dtype),
                "N_valid": int(df[col].notna().sum()),
                "Missing_pct": round(df[col].isna().mean() * 100, 2),
                "Range": range_str,
            }
        )

    dict_df = pd.DataFrame(rows)
    cat_order = {cat: idx for idx, cat in enumerate(CATEGORY_ORDER + ["Other"])}
    state_order = {state: idx for idx, state in enumerate(STATE_CLASS_ORDER)}
    sm_group_order = {group: idx for idx, group in enumerate(GLEAM_DOC_GROUP_ORDER)}

    dict_df["_cat_order"] = dict_df["Category"].map(cat_order).fillna(99)
    dict_df["_state_order"] = dict_df["State_Class"].map(state_order).fillna(99)
    dict_df["_sm_group_order"] = dict_df["SM_Doc_Group"].map(sm_group_order).fillna(99)
    dict_df = dict_df.sort_values(["_cat_order", "_sm_group_order", "_state_order", "Variable"]).drop(
        columns=["_cat_order", "_sm_group_order", "_state_order"]
    )
    return dict_df


def write_table(handle, subset):
    handle.write("| Variable | Label (CN) | Label (EN) | Unit | Window | Range | Missing% |\n")
    handle.write("|----------|-----------|-----------|------|--------|-------|----------|\n")
    for _, row in subset.iterrows():
        handle.write(
            f"| `{row['Variable']}` | {row['Label_CN']} | {row['Label_EN']} "
            f"| {row['Unit']} | {row['Window']} | {row['Range']} | {row['Missing_pct']:.1f}% |\n"
        )
    handle.write("\n")


def write_markdown(dict_df, outpath, dataset_name, n_rows):
    generated = date.today().isoformat()
    version_tag = DATA_VERSION.upper()
    sm_categories = {"SM-GLEAM", "SM-SWSM", "SM-ERA5Land"}

    with open(outpath, "w", encoding="utf-8") as handle:
        handle.write(f"# {version_tag} Data Dictionary ({len(dict_df)} variables)\n\n")
        handle.write(f"**Dataset:** `{dataset_name}.parquet`  \n")
        handle.write(f"**N:** {n_rows:,} grid-year observations  \n")
        handle.write(f"**Years:** {YEARS[0]}-{YEARS[-1]}  \n")
        handle.write("**Spatial resolution:** 0.1 degree grid  \n")
        handle.write(f"**Generated:** {generated}  \n\n")
        handle.write("---\n\n")

        for idx, category in enumerate(CATEGORY_ORDER + ["Other"], start=1):
            subset = dict_df[dict_df["Category"] == category]
            if len(subset) == 0:
                continue

            handle.write(f"## {idx}. {category} ({len(subset)} vars)\n\n")

            if category == "SM-GLEAM":
                for group_name in GLEAM_DOC_GROUP_ORDER:
                    subgroup = subset[subset["SM_Doc_Group"] == group_name]
                    if len(subgroup) == 0:
                        continue
                    handle.write(f"### {group_name}\n\n")
                    write_table(handle, subgroup.sort_values("Variable"))
            elif category in sm_categories:
                subgroups = [
                    ("baseline-local", subset[subset["State_Class"].isin(["raw/core", "baseline-local"])]),
                    ("pooled-state", subset[subset["State_Class"] == "pooled-state"]),
                    ("maize-zone-state", subset[subset["State_Class"] == "maize-zone-state"]),
                ]
                for subgroup_name, subgroup_df in subgroups:
                    if len(subgroup_df) == 0:
                        continue
                    handle.write(f"### {subgroup_name}\n\n")
                    write_table(handle, subgroup_df.sort_values("Variable"))
            else:
                write_table(handle, subset.sort_values("Variable"))

        handle.write("---\n\n")
        handle.write("## Notes\n\n")
        handle.write(
            "- **Window abbreviations:** Full=full season, V3pre30=30 days before V3, "
            "V3pm10=V3 +/- 10 days, HEpm10=HE +/- 10 days, V3HE=V3 to HE, HEMA=HE to MA, "
            "FullNew=v3pre30 + v3he + hema with duplicated V3 and HE boundary days removed.\n"
        )
        handle.write(
            "- **Capped GDD:** `gdd_10_29` to `gdd_10_32` use `max(min(t2m_mean, upper_cap)-10, 0)` "
            "at the daily scale and then aggregate by window.\n"
        )
        handle.write("- **SM sources:** GLEAM, SWSM, ERA5-Land.\n")
        handle.write("- **SM depth:** Surface corresponds to 0-7/10 cm; root-zone/deep layers correspond to 28-100 cm where applicable.\n")
        handle.write("- **Compound hot-dry sources:** GLEAM root/surface SM, SWSM L1/L3, ERA5-Land swvl1/swvl3, and `pr_lt1`.\n")
        handle.write(
            "- **Legacy baseline-local SM thresholds:** grid-cell historical percentiles; dry-side variables use local P10/P20 and wet-side variables use local P80/P90. "
            "Legacy GLEAM baselines use 2013-2020, and SWSM/ERA5-Land baselines use 2016-2019, all over DOY 90-300.\n"
        )
        handle.write(
            "- **GLEAM rework phenology windows:** new GLEAM `md-event family` and `window-baseline family` variables use "
            "ChinaCropPhen1km maize V3/HE/MA rasters sampled to the 0.1 degree panel grid, with threshold years 2013-2019 and output years 2016-2019.\n"
        )
        handle.write(
            "- **GLEAM md-event family:** daily GLEAM SM is first converted to 5-day rolling means, then transformed into local pooled-within-window percentiles; "
            "dry events use >P40 to <P20 with a minimum drop of 5 percentile-points per 5 days, and wet events mirror this with <P60 to >P80.\n"
        )
        handle.write(
            "- **GLEAM window-baseline family:** thresholds are local, grid-specific, and window-specific, estimated separately for `v3pre30`, `v3he`, and `hema`; "
            "`severitymean_*` is the window-average deficit/excess over all valid days, while `severitysum_*` is the cumulative deficit/excess within the window.\n"
        )
        handle.write(
            "- **Pooled-state SM thresholds:** pooled window-specific P25/P75, estimated separately for each source-layer and window.\n"
        )
        handle.write(
            "- **Maize-zone-state SM thresholds:** maize-zone-specific P25/P75, estimated separately for each source-layer, window, and maize zone.\n"
        )
        handle.write(
            "- **Interpretation rule:** legacy `baseline-local`, `pooled-state`, and `maize-zone-state` variables should not be treated as default robustness substitutes for one another.\n"
        )
        handle.write(
            "- **GLEAM rework interpretation rule:** `legacy GLEAM`, `md-event family`, and `window-baseline family` should not be treated as interchangeable definitions by default.\n"
        )
        handle.write("- **Temperature:** ERA5 reanalysis aligned to the 376x616 reference grid.\n")
        handle.write("- **Precipitation:** CHM_PRE aligned to the ERA reference grid by nearest-neighbor mapping.\n")

    print(f"  Saved: {outpath}")


def main():
    print("=" * 70)
    print(f"Generate {DATA_VERSION.upper()} Data Dictionary")
    print("=" * 70)

    df = pd.read_parquet(MAIN_PARQUET)
    n_rows = len(df)
    print(f"Loaded: {n_rows:,} rows, {len(df.columns)} cols")

    dict_df = generate_dictionary(df)

    print("\n  Category summary:")
    cat_counts = dict_df["Category"].value_counts().reindex(CATEGORY_ORDER + ["Other"]).dropna()
    for category, count in cat_counts.items():
        print(f"    {category}: {int(count)} vars")

    auto_labeled = dict_df[dict_df["Label_EN"] == dict_df["Variable"]]
    if len(auto_labeled) > 0:
        print(f"\n  WARNING: {len(auto_labeled)} columns without proper labels:")
        for var in auto_labeled["Variable"].values[:20]:
            print(f"    {var}")

    dict_df.to_csv(DICT_TABLE_PATH, index=False, encoding="utf-8-sig")
    print(f"  Saved: {DICT_TABLE_PATH}")

    os.makedirs(os.path.dirname(DICT_MARKDOWN_PATH), exist_ok=True)
    write_markdown(dict_df, DICT_MARKDOWN_PATH, MAIN_OUTPUT_PREFIX, n_rows)

    print(f"\n  Total: {len(dict_df)} variables documented")
    print("=" * 70)


if __name__ == "__main__":
    main()
