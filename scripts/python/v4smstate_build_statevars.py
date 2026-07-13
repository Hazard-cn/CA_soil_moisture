"""
v4smstate_build_statevars.py
Purpose: Build state-based soil moisture sidecar panel for the sm-state audit.
Author: YangSu + Codex
Date: 2026-04-21
"""

from __future__ import annotations

import gc
import logging
import os
import sys
from calendar import isleap, monthrange
from datetime import datetime
from typing import Dict, Iterable, Tuple

import netCDF4 as nc
import numpy as np
import pandas as pd

PROJ_DIR = r"C:/YangSu/00_Project/CA_mechanism/regression_SR"
TEMP_DIR = os.path.join(PROJ_DIR, "temp", "2026-04-21_sm_state_audit")
LOG_PATH = os.path.join(TEMP_DIR, "sm_state_build.log")

os.makedirs(TEMP_DIR, exist_ok=True)

sys.path.insert(0, os.path.join(PROJ_DIR, "data_build", "scripts", "python"))
from config import (  # type: ignore
    ERA5L_SM_DIR,
    GLEAM_DIR,
    RANDOM_SEED,
    REF_NLAT,
    REF_NLON,
    SWSM_DIR,
    TEMP_DIR as TEMP_GRID_DIR,
    WINDOWS as BUILD_WINDOWS,
    YEARS,
)

np.random.seed(RANDOM_SEED)

TARGET_WINDOWS = ("full", "v3pre30", "v3pm10")
ZONE_ORDER = ["NE", "HHH", "SW", "SH", "NW", "Other"]
THRESHOLD_SCHEMES = ("pooled", "maize_zone")
EPSILON = 1e-8

ZONE_MAP = {
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

SOURCE_META = [
    {
        "source": "gleam",
        "layer": "surface",
        "sm_label": "GLEAM-Sfc",
        "sm_base": "gleam_sms_mean",
        "prefix": "gsms",
        "family": "gleam",
        "var_name": "SMs",
        "drydays_base": "gleam_sms",
    },
    {
        "source": "gleam",
        "layer": "rootzone",
        "sm_label": "GLEAM-Root",
        "sm_base": "gleam_smrz_mean",
        "prefix": "gsmrz",
        "family": "gleam",
        "var_name": "SMrz",
        "drydays_base": "gleam_smrz",
    },
    {
        "source": "swsm",
        "layer": "surface",
        "sm_label": "SWSM-L1",
        "sm_base": "swsm_l1_mean",
        "prefix": "ssl1",
        "family": "swsm",
        "var_name": "L1",
        "drydays_base": "swsm_l1",
    },
    {
        "source": "swsm",
        "layer": "rootzone",
        "sm_label": "SWSM-L3",
        "sm_base": "swsm_l3_mean",
        "prefix": "ssl3",
        "family": "swsm",
        "var_name": "L3",
        "drydays_base": "swsm_l3",
    },
    {
        "source": "era",
        "layer": "surface",
        "sm_label": "ERA5L-L1",
        "sm_base": "era5l_swvl1_mean",
        "prefix": "esl1",
        "family": "era5l",
        "var_name": "swvl1",
        "era_layer": 1,
        "drydays_base": "era5l_swvl1",
    },
    {
        "source": "era",
        "layer": "rootzone",
        "sm_label": "ERA5L-L3",
        "sm_base": "era5l_swvl3_mean",
        "prefix": "esl3",
        "family": "era5l",
        "var_name": "swvl3",
        "era_layer": 3,
        "drydays_base": "era5l_swvl3",
    },
]


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("sm_state_build")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    f_handler = logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8")
    f_handler.setFormatter(fmt)
    logger.addHandler(f_handler)

    s_handler = logging.StreamHandler(sys.stdout)
    s_handler.setFormatter(fmt)
    logger.addHandler(s_handler)
    return logger


LOGGER = setup_logging()


def window_suffix(window: str) -> str:
    return BUILD_WINDOWS[window]["suffix"]


def stata_suffix(window: str) -> str:
    return "" if window == "full" else BUILD_WINDOWS[window]["suffix"]


def assign_maize_zone(province: str) -> str:
    return ZONE_MAP.get(province, "Other")


def load_panel() -> pd.DataFrame:
    panel_path = os.path.join(PROJ_DIR, "data_build", "data", "intermediate", "panel_windows.csv")
    meta_path = os.path.join(PROJ_DIR, "data_build", "data", "processed", "data_v3_phenowindows.dta")

    panel = pd.read_csv(panel_path)
    meta = pd.read_stata(meta_path, columns=["grid_id", "year", "province"], convert_categoricals=False)
    meta["maize_zone"] = meta["province"].map(assign_maize_zone).fillna("Other")
    meta = meta.drop_duplicates(subset=["grid_id", "year"])

    panel = panel.merge(meta, on=["grid_id", "year"], how="left", validate="1:1")
    if panel["maize_zone"].isna().any():
        missing_n = int(panel["maize_zone"].isna().sum())
        raise RuntimeError(f"maize_zone merge failed for {missing_n} rows")

    panel = panel.sort_values(["year", "grid_id"]).reset_index(drop=True)
    return panel


def doy_from_month_day(year: int, month: int, day: int) -> int:
    return datetime(year, month, day).timetuple().tm_yday


def build_era5_alignment() -> Tuple[np.ndarray, np.ndarray]:
    sample_path = os.path.join(
        ERA5L_SM_DIR,
        "SoilWater_2016_03",
        "volumetric_soil_water_layer_1_0_daily-mean.nc",
    )
    ds = nc.Dataset(sample_path)
    era_lat = ds.variables["latitude"][:].astype(np.float64)
    era_lon = ds.variables["longitude"][:].astype(np.float64)
    ds.close()

    import glob

    temp_files = glob.glob(os.path.join(TEMP_GRID_DIR, "*.nc"))
    ds_ref = nc.Dataset(temp_files[0])
    ref_lat = ds_ref.variables["latitude"][:].astype(np.float64)
    ref_lon = ds_ref.variables["longitude"][:].astype(np.float64)
    ds_ref.close()

    lat_map = np.array([np.argmin(np.abs(era_lat - val)) for val in ref_lat])
    lon_map = np.array([np.argmin(np.abs(era_lon - val)) for val in ref_lon])
    return lat_map, lon_map


def load_gleam_year(year: int, var_name: str) -> np.ndarray:
    path = os.path.join(GLEAM_DIR, f"GLEAM_SM_0.1deg_TEMPgrid_{year}.nc")
    ds = nc.Dataset(path)
    arr = np.ma.filled(ds.variables[var_name][:], np.nan).astype(np.float32)
    ds.close()
    return arr


def load_swsm_year(year: int, var_name: str) -> np.ndarray:
    path = os.path.join(SWSM_DIR, f"SWSM_L123_0.1deg_{year}.nc")
    ds = nc.Dataset(path)
    raw = ds.variables[var_name][:]
    ds.close()
    arr = np.ma.filled(raw, 0).astype(np.float32) / 100.0
    arr[arr == 0] = np.nan
    return arr


def load_era5l_year(year: int, layer: int, lat_map: np.ndarray, lon_map: np.ndarray) -> np.ndarray:
    ndays = 366 if isleap(year) else 365
    sm_3d = np.full((ndays, REF_NLAT, REF_NLON), np.nan, dtype=np.float32)
    var_name = f"swvl{layer}"

    for month in range(3, 11):
        dirname = f"SoilWater_{year}_{month:02d}"
        fname = f"volumetric_soil_water_layer_{layer}_0_daily-mean.nc"
        path = os.path.join(ERA5L_SM_DIR, dirname, fname)
        if not os.path.exists(path):
            continue

        ds = nc.Dataset(path)
        data = np.ma.filled(ds.variables[var_name][:], np.nan).astype(np.float32)
        ds.close()

        data_aligned = data[:, lat_map, :][:, :, lon_map]
        start_idx = doy_from_month_day(year, month, 1) - 1
        ndays_month = monthrange(year, month)[1]
        sm_3d[start_idx:start_idx + ndays_month] = data_aligned

    return sm_3d


def compute_baseline_p20(source: Dict[str, str], lat_map: np.ndarray | None = None, lon_map: np.ndarray | None = None) -> np.ndarray:
    LOGGER.info("Computing validation baseline p20 for %s", source["sm_label"])

    if source["family"] == "gleam":
        all_sm = []
        for year in range(2013, 2021):
            path = os.path.join(GLEAM_DIR, f"GLEAM_SM_0.1deg_TEMPgrid_{year}.nc")
            if not os.path.exists(path):
                continue
            ds = nc.Dataset(path)
            arr = np.ma.filled(ds.variables[source["var_name"]][:], np.nan).astype(np.float32)
            ds.close()
            all_sm.append(arr[89:300, :, :])
        stacked = np.concatenate(all_sm, axis=0)
        p20 = np.nanpercentile(stacked, 20, axis=0).astype(np.float32)
        del stacked, all_sm
        gc.collect()
        return p20

    if source["family"] == "swsm":
        all_sm = []
        for year in YEARS:
            arr = load_swsm_year(year, source["var_name"])
            all_sm.append(arr[89:300, :, :])
        stacked = np.concatenate(all_sm, axis=0)
        p20 = np.nanpercentile(stacked, 20, axis=0).astype(np.float32)
        del stacked, all_sm
        gc.collect()
        return p20

    if source["family"] == "era5l":
        if lat_map is None or lon_map is None:
            raise ValueError("ERA5-Land validation requires alignment maps")
        all_sm = []
        for year in YEARS:
            arr = load_era5l_year(year, int(source["era_layer"]), lat_map, lon_map)
            all_sm.append(arr[89:300, :, :])
        stacked = np.concatenate(all_sm, axis=0)
        p20 = np.nanpercentile(stacked, 20, axis=0).astype(np.float32)
        del stacked, all_sm
        gc.collect()
        return p20

    raise ValueError(f"Unsupported family: {source['family']}")


def load_source_year(source: Dict[str, str], year: int, lat_map: np.ndarray | None, lon_map: np.ndarray | None) -> np.ndarray:
    if source["family"] == "gleam":
        return load_gleam_year(year, source["var_name"])
    if source["family"] == "swsm":
        return load_swsm_year(year, source["var_name"])
    if source["family"] == "era5l":
        if lat_map is None or lon_map is None:
            raise ValueError("ERA5-Land requires alignment maps")
        return load_era5l_year(year, int(source["era_layer"]), lat_map, lon_map)
    raise ValueError(f"Unsupported family: {source['family']}")


def collect_threshold_buffers(
    panel_yr: pd.DataFrame,
    sm_3d: np.ndarray,
    window: str,
    pooled_store: list[np.ndarray],
    zone_store: Dict[str, list[np.ndarray]],
) -> None:
    starts = panel_yr[f"win_{window}_start"].to_numpy(dtype=np.int32)
    ends = panel_yr[f"win_{window}_end"].to_numpy(dtype=np.int32)
    lat_idxs = panel_yr["lat_idx"].to_numpy(dtype=np.int32)
    lon_idxs = panel_yr["lon_idx"].to_numpy(dtype=np.int32)
    zones = panel_yr["maize_zone"].to_numpy(dtype=object)

    unique_pairs = np.unique(np.column_stack([starts, ends]), axis=0)
    for s_doy, e_doy in unique_pairs:
        start_idx = max(0, int(s_doy) - 1)
        end_idx = min(sm_3d.shape[0], int(e_doy))
        if start_idx >= end_idx:
            continue

        pair_mask = (starts == s_doy) & (ends == e_doy)
        cell_idx = np.where(pair_mask)[0]
        if cell_idx.size == 0:
            continue

        li = lat_idxs[cell_idx]
        lj = lon_idxs[cell_idx]
        sm = sm_3d[start_idx:end_idx, li, lj]
        valid = ~np.isnan(sm)
        pooled_values = sm[valid]
        if pooled_values.size > 0:
            pooled_store.append(pooled_values.astype(np.float32))

        pair_zones = zones[cell_idx]
        for zone in np.unique(pair_zones):
            zone_mask = pair_zones == zone
            sm_zone = sm[:, zone_mask]
            values = sm_zone[~np.isnan(sm_zone)]
            if values.size > 0:
                zone_store[str(zone)].append(values.astype(np.float32))


def compute_thresholds_for_source(
    source: Dict[str, str],
    panel: pd.DataFrame,
    lat_map: np.ndarray | None,
    lon_map: np.ndarray | None,
) -> pd.DataFrame:
    LOGGER.info("Computing pooled and maize-zone thresholds for %s", source["sm_label"])

    pooled_buffers = {w: [] for w in TARGET_WINDOWS}
    zone_buffers = {(w, z): [] for w in TARGET_WINDOWS for z in ZONE_ORDER}

    for year in YEARS:
        panel_yr = panel.loc[panel["year"] == year].copy()
        sm_3d = load_source_year(source, year, lat_map, lon_map)
        for window in TARGET_WINDOWS:
            collect_threshold_buffers(
                panel_yr=panel_yr,
                sm_3d=sm_3d,
                window=window,
                pooled_store=pooled_buffers[window],
                zone_store={z: zone_buffers[(window, z)] for z in ZONE_ORDER},
            )
        del sm_3d
        gc.collect()

    rows = []
    for window in TARGET_WINDOWS:
        pooled_arr = np.concatenate(pooled_buffers[window]) if pooled_buffers[window] else np.array([], dtype=np.float32)
        if pooled_arr.size == 0:
            raise RuntimeError(f"No pooled threshold support for {source['sm_label']} / {window}")
        rows.append(
            {
                "threshold_scheme": "pooled",
                "zone_group": "ALL",
                "window": window,
                "source": source["source"],
                "layer": source["layer"],
                "sm_label": source["sm_label"],
                "sm_base": source["sm_base"],
                "prefix": source["prefix"],
                "p25": float(np.nanpercentile(pooled_arr, 25)),
                "p75": float(np.nanpercentile(pooled_arr, 75)),
                "n_valid_days": int(pooled_arr.size),
            }
        )

        for zone in ZONE_ORDER:
            zone_arr = np.concatenate(zone_buffers[(window, zone)]) if zone_buffers[(window, zone)] else np.array([], dtype=np.float32)
            if zone_arr.size == 0:
                raise RuntimeError(f"No zone threshold support for {source['sm_label']} / {window} / {zone}")
            rows.append(
                {
                    "threshold_scheme": "maize_zone",
                    "zone_group": zone,
                    "window": window,
                    "source": source["source"],
                    "layer": source["layer"],
                    "sm_label": source["sm_label"],
                    "sm_base": source["sm_base"],
                    "prefix": source["prefix"],
                    "p25": float(np.nanpercentile(zone_arr, 25)),
                    "p75": float(np.nanpercentile(zone_arr, 75)),
                    "n_valid_days": int(zone_arr.size),
                }
            )

    return pd.DataFrame(rows)


def init_result_columns(prefix: str) -> Dict[str, np.ndarray]:
    result: Dict[str, np.ndarray] = {}
    for window in TARGET_WINDOWS:
        sfx = stata_suffix(window)
        result[f"vd_{prefix}{sfx}"] = np.full(0, np.nan, dtype=np.float32)
        result[f"rav_{prefix}{sfx}"] = np.full(0, np.nan, dtype=np.float32)
        result[f"rmi_{prefix}{sfx}"] = np.full(0, np.nan, dtype=np.float32)
        result[f"rma_{prefix}{sfx}"] = np.full(0, np.nan, dtype=np.float32)
        result[f"rsd_{prefix}{sfx}"] = np.full(0, np.nan, dtype=np.float32)
        result[f"dp20_{prefix}{sfx}"] = np.full(0, np.nan, dtype=np.float32)
        for scheme_prefix in ("pl", "mz"):
            result[f"dd_{scheme_prefix}_{prefix}{sfx}"] = np.full(0, np.nan, dtype=np.float32)
            result[f"wd_{scheme_prefix}_{prefix}{sfx}"] = np.full(0, np.nan, dtype=np.float32)
            result[f"ds_{scheme_prefix}_{prefix}{sfx}"] = np.full(0, np.nan, dtype=np.float32)
            result[f"ws_{scheme_prefix}_{prefix}{sfx}"] = np.full(0, np.nan, dtype=np.float32)
    return result


def allocate_result_columns(prefix: str, n: int) -> Dict[str, np.ndarray]:
    allocated: Dict[str, np.ndarray] = {}
    for window in TARGET_WINDOWS:
        sfx = stata_suffix(window)
        allocated[f"vd_{prefix}{sfx}"] = np.full(n, np.nan, dtype=np.float32)
        allocated[f"rav_{prefix}{sfx}"] = np.full(n, np.nan, dtype=np.float32)
        allocated[f"rmi_{prefix}{sfx}"] = np.full(n, np.nan, dtype=np.float32)
        allocated[f"rma_{prefix}{sfx}"] = np.full(n, np.nan, dtype=np.float32)
        allocated[f"rsd_{prefix}{sfx}"] = np.full(n, np.nan, dtype=np.float32)
        allocated[f"dp20_{prefix}{sfx}"] = np.full(n, np.nan, dtype=np.float32)
        for scheme_prefix in ("pl", "mz"):
            allocated[f"dd_{scheme_prefix}_{prefix}{sfx}"] = np.full(n, np.nan, dtype=np.float32)
            allocated[f"wd_{scheme_prefix}_{prefix}{sfx}"] = np.full(n, np.nan, dtype=np.float32)
            allocated[f"ds_{scheme_prefix}_{prefix}{sfx}"] = np.full(n, np.nan, dtype=np.float32)
            allocated[f"ws_{scheme_prefix}_{prefix}{sfx}"] = np.full(n, np.nan, dtype=np.float32)
    return allocated


def get_threshold_lookup(threshold_df: pd.DataFrame) -> Tuple[Dict[str, Dict[str, float]], Dict[Tuple[str, str], Dict[str, float]]]:
    pooled_lookup: Dict[str, Dict[str, float]] = {}
    zone_lookup: Dict[Tuple[str, str], Dict[str, float]] = {}
    for row in threshold_df.itertuples():
        if row.threshold_scheme == "pooled":
            pooled_lookup[row.window] = {"p25": row.p25, "p75": row.p75}
        else:
            zone_lookup[(row.window, row.zone_group)] = {"p25": row.p25, "p75": row.p75}
    return pooled_lookup, zone_lookup


def populate_window_metrics(
    result: Dict[str, np.ndarray],
    panel_yr: pd.DataFrame,
    sm_3d: np.ndarray,
    window: str,
    prefix: str,
    pooled_lookup: Dict[str, Dict[str, float]],
    zone_lookup: Dict[Tuple[str, str], Dict[str, float]],
    p20_2d: np.ndarray,
) -> None:
    sfx = stata_suffix(window)
    starts = panel_yr[f"win_{window}_start"].to_numpy(dtype=np.int32)
    ends = panel_yr[f"win_{window}_end"].to_numpy(dtype=np.int32)
    lat_idxs = panel_yr["lat_idx"].to_numpy(dtype=np.int32)
    lon_idxs = panel_yr["lon_idx"].to_numpy(dtype=np.int32)
    zones = panel_yr["maize_zone"].to_numpy(dtype=object)

    unique_pairs = np.unique(np.column_stack([starts, ends]), axis=0)
    for s_doy, e_doy in unique_pairs:
        start_idx = max(0, int(s_doy) - 1)
        end_idx = min(sm_3d.shape[0], int(e_doy))
        if start_idx >= end_idx:
            continue

        pair_mask = (starts == s_doy) & (ends == e_doy)
        cell_idx = np.where(pair_mask)[0]
        if cell_idx.size == 0:
            continue

        li = lat_idxs[cell_idx]
        lj = lon_idxs[cell_idx]
        pair_zones = zones[cell_idx]

        sm = sm_3d[start_idx:end_idx, li, lj]
        valid = ~np.isnan(sm)
        valid_days = np.sum(valid, axis=0).astype(np.float32)
        result[f"vd_{prefix}{sfx}"][cell_idx] = valid_days

        has_data = valid_days > 0
        if not has_data.any():
            continue

        out_idx = cell_idx[has_data]
        sm_data = sm[:, has_data]
        valid_data = valid[:, has_data]
        li_data = li[has_data]
        lj_data = lj[has_data]
        zone_data = pair_zones[has_data]
        valid_days_data = valid_days[has_data]

        result[f"rav_{prefix}{sfx}"][out_idx] = np.nanmean(sm_data, axis=0).astype(np.float32)
        result[f"rmi_{prefix}{sfx}"][out_idx] = np.nanmin(sm_data, axis=0).astype(np.float32)
        result[f"rma_{prefix}{sfx}"][out_idx] = np.nanmax(sm_data, axis=0).astype(np.float32)
        if sm_data.shape[0] > 1:
            result[f"rsd_{prefix}{sfx}"][out_idx] = np.nanstd(sm_data, axis=0, ddof=1).astype(np.float32)

        cell_p20 = p20_2d[li_data, lj_data]
        dry_p20 = (sm_data <= cell_p20[np.newaxis, :]) & valid_data
        result[f"dp20_{prefix}{sfx}"][out_idx] = np.sum(dry_p20, axis=0).astype(np.float32)

        pooled_p25 = pooled_lookup[window]["p25"]
        pooled_p75 = pooled_lookup[window]["p75"]
        dry_pl = (sm_data <= pooled_p25) & valid_data
        wet_pl = (sm_data >= pooled_p75) & valid_data
        dd_pl = np.sum(dry_pl, axis=0).astype(np.float32)
        wd_pl = np.sum(wet_pl, axis=0).astype(np.float32)
        result[f"dd_pl_{prefix}{sfx}"][out_idx] = dd_pl
        result[f"wd_pl_{prefix}{sfx}"][out_idx] = wd_pl
        result[f"ds_pl_{prefix}{sfx}"][out_idx] = dd_pl / valid_days_data
        result[f"ws_pl_{prefix}{sfx}"][out_idx] = wd_pl / valid_days_data

        local_p25 = np.array([zone_lookup[(window, str(z))]["p25"] for z in zone_data], dtype=np.float32)
        local_p75 = np.array([zone_lookup[(window, str(z))]["p75"] for z in zone_data], dtype=np.float32)
        dry_mz = (sm_data <= local_p25[np.newaxis, :]) & valid_data
        wet_mz = (sm_data >= local_p75[np.newaxis, :]) & valid_data
        dd_mz = np.sum(dry_mz, axis=0).astype(np.float32)
        wd_mz = np.sum(wet_mz, axis=0).astype(np.float32)
        result[f"dd_mz_{prefix}{sfx}"][out_idx] = dd_mz
        result[f"wd_mz_{prefix}{sfx}"][out_idx] = wd_mz
        result[f"ds_mz_{prefix}{sfx}"][out_idx] = dd_mz / valid_days_data
        result[f"ws_mz_{prefix}{sfx}"][out_idx] = wd_mz / valid_days_data


def build_source_frame(
    source: Dict[str, str],
    panel: pd.DataFrame,
    threshold_df: pd.DataFrame,
    lat_map: np.ndarray | None,
    lon_map: np.ndarray | None,
) -> pd.DataFrame:
    LOGGER.info("Building state panel columns for %s", source["sm_label"])
    p20_2d = compute_baseline_p20(source, lat_map=lat_map, lon_map=lon_map)
    pooled_lookup, zone_lookup = get_threshold_lookup(threshold_df)

    all_frames = []
    for year in YEARS:
        panel_yr = panel.loc[panel["year"] == year].copy()
        panel_yr = panel_yr.reset_index(drop=True)
        source_year = load_source_year(source, year, lat_map, lon_map)
        result = allocate_result_columns(source["prefix"], len(panel_yr))
        for window in TARGET_WINDOWS:
            populate_window_metrics(
                result=result,
                panel_yr=panel_yr,
                sm_3d=source_year,
                window=window,
                prefix=source["prefix"],
                pooled_lookup=pooled_lookup,
                zone_lookup=zone_lookup,
                p20_2d=p20_2d,
            )
        frame = pd.DataFrame(result)
        frame.insert(0, "year", panel_yr["year"].to_numpy())
        frame.insert(0, "grid_id", panel_yr["grid_id"].to_numpy())
        all_frames.append(frame)
        del source_year, frame, result
        gc.collect()

    source_frame = pd.concat(all_frames, ignore_index=True)
    return source_frame


def validate_p20_replay(panel_wide: pd.DataFrame) -> pd.DataFrame:
    LOGGER.info("Validating replayed p20 drydays against data_v3_main.dta")
    main_path = os.path.join(PROJ_DIR, "data_build", "data", "processed", "data_v3_main.dta")

    existing_cols = set(pd.read_stata(main_path, iterator=True).variable_labels().keys())
    compare_cols = ["grid_id", "year"]
    mapping_rows = []
    for meta in SOURCE_META:
        for window in TARGET_WINDOWS:
            sfx = stata_suffix(window)
            data_sfx = BUILD_WINDOWS[window]["suffix"]
            new_col = f"dp20_{meta['prefix']}{sfx}"
            old_col = f"drydays_{meta['drydays_base']}_le_p20{data_sfx}"[:32]
            if old_col in existing_cols:
                compare_cols.append(old_col)
                mapping_rows.append(
                    (meta["source"], meta["layer"], meta["sm_label"], window, new_col, old_col)
                )
            else:
                LOGGER.warning(
                    "Skipping p20 replay validation for missing historical column: %s",
                    old_col,
                )

    compare_cols = list(dict.fromkeys(compare_cols))
    existing = pd.read_stata(main_path, columns=compare_cols, convert_categoricals=False)
    merged = panel_wide.merge(existing, on=["grid_id", "year"], how="left", validate="1:1")

    rows = []
    for source, layer, sm_label, window, new_col, old_col in mapping_rows:
        sub = merged[[new_col, old_col]].dropna()
        if sub.empty:
            raise RuntimeError(f"Validation merge produced empty comparison for {sm_label} / {window}")
        diff = sub[new_col].to_numpy(dtype=np.float32) - sub[old_col].to_numpy(dtype=np.float32)
        mismatch_n = int(np.count_nonzero(diff))
        row = {
            "source": source,
            "layer": layer,
            "sm_label": sm_label,
            "window": window,
            "new_col": new_col,
            "old_col": old_col,
            "total_n": int(sub.shape[0]),
            "mismatch_n": mismatch_n,
            "max_abs_diff": float(np.max(np.abs(diff))),
            "mean_new": float(sub[new_col].mean()),
            "mean_old": float(sub[old_col].mean()),
            "exact_match": int(mismatch_n == 0),
        }
        rows.append(row)
        if mismatch_n != 0:
            raise RuntimeError(f"P20 replay mismatch for {sm_label} / {window}: {mismatch_n} rows")

    return pd.DataFrame(rows)


def build_long_state_table(panel_wide: pd.DataFrame, threshold_df: pd.DataFrame) -> pd.DataFrame:
    base_cols = ["grid_id", "year"]
    panel_base = panel_wide[base_cols].drop_duplicates().sort_values(base_cols).reset_index(drop=True)
    records = []

    for meta in SOURCE_META:
        for window in TARGET_WINDOWS:
            sfx = stata_suffix(window)
            valid_col = f"vd_{meta['prefix']}{sfx}"
            raw_cols = {
                "rawSM_mean": f"rav_{meta['prefix']}{sfx}",
                "rawSM_min": f"rmi_{meta['prefix']}{sfx}",
                "rawSM_max": f"rma_{meta['prefix']}{sfx}",
                "rawSM_sd": f"rsd_{meta['prefix']}{sfx}",
            }
            for scheme in THRESHOLD_SCHEMES:
                short = "pl" if scheme == "pooled" else "mz"
                sub_cols = [
                    valid_col,
                    f"dd_{short}_{meta['prefix']}{sfx}",
                    f"wd_{short}_{meta['prefix']}{sfx}",
                    f"ds_{short}_{meta['prefix']}{sfx}",
                    f"ws_{short}_{meta['prefix']}{sfx}",
                ] + list(raw_cols.values())

                sub = panel_wide[base_cols + sub_cols].copy()
                rename_map = {
                    valid_col: "valid_days",
                    f"dd_{short}_{meta['prefix']}{sfx}": "drydays_p25",
                    f"wd_{short}_{meta['prefix']}{sfx}": "wetdays_p75",
                    f"ds_{short}_{meta['prefix']}{sfx}": "DryShare",
                    f"ws_{short}_{meta['prefix']}{sfx}": "WetShare",
                    raw_cols["rawSM_mean"]: "rawSM_mean",
                    raw_cols["rawSM_min"]: "rawSM_min",
                    raw_cols["rawSM_max"]: "rawSM_max",
                    raw_cols["rawSM_sd"]: "rawSM_sd",
                }
                sub = sub.rename(columns=rename_map)
                sub["threshold_scheme"] = scheme
                sub["window"] = window
                sub["source"] = meta["source"]
                sub["layer"] = meta["layer"]
                sub["sm_label"] = meta["sm_label"]
                sub["sm_base"] = meta["sm_base"]
                sub["prefix"] = meta["prefix"]
                records.append(sub)

    long_df = pd.concat(records, ignore_index=True)

    if ((long_df["DryShare"] < -EPSILON) | (long_df["WetShare"] < -EPSILON)).any():
        raise RuntimeError("Negative state shares detected")
    if ((long_df["DryShare"] > 1 + EPSILON) | (long_df["WetShare"] > 1 + EPSILON)).any():
        raise RuntimeError("State share above 1 detected")
    if ((long_df["DryShare"] + long_df["WetShare"]) > 1 + EPSILON).any():
        raise RuntimeError("DryShare + WetShare exceeds 1 + epsilon")

    dup_n = int(long_df.duplicated(subset=["grid_id", "year", "threshold_scheme", "window", "source", "layer"]).sum())
    if dup_n != 0:
        raise RuntimeError(f"Duplicate long state keys detected: {dup_n}")

    threshold_counts = (
        threshold_df.groupby("threshold_scheme")
        .size()
        .to_dict()
    )
    if threshold_counts.get("pooled", 0) != 18:
        raise RuntimeError(f"Pooled threshold row count mismatch: {threshold_counts.get('pooled', 0)}")
    if threshold_counts.get("maize_zone", 0) != 108:
        raise RuntimeError(f"maize_zone threshold row count mismatch: {threshold_counts.get('maize_zone', 0)}")

    return long_df


def export_outputs(panel_wide: pd.DataFrame, panel_long: pd.DataFrame, threshold_df: pd.DataFrame, validation_df: pd.DataFrame) -> None:
    wide_csv = os.path.join(TEMP_DIR, "sm_state_panel_wide.csv")
    wide_dta = os.path.join(TEMP_DIR, "sm_state_panel_wide.dta")
    long_csv = os.path.join(TEMP_DIR, "sm_state_panel_long.csv")
    threshold_csv = os.path.join(TEMP_DIR, "sm_state_thresholds.csv")
    validation_csv = os.path.join(TEMP_DIR, "sm_state_validation.csv")

    panel_wide.to_csv(wide_csv, index=False)
    panel_wide.to_stata(wide_dta, write_index=False, version=118)
    panel_long.to_csv(long_csv, index=False)
    threshold_df.to_csv(threshold_csv, index=False)
    validation_df.to_csv(validation_csv, index=False)

    LOGGER.info("Saved %s", wide_csv)
    LOGGER.info("Saved %s", wide_dta)
    LOGGER.info("Saved %s", long_csv)
    LOGGER.info("Saved %s", threshold_csv)
    LOGGER.info("Saved %s", validation_csv)


def main() -> None:
    LOGGER.info("=== Starting v4smstate_build_statevars.py ===")
    panel = load_panel()
    LOGGER.info("Panel rows: %s", len(panel))

    lat_map, lon_map = build_era5_alignment()

    source_frames = []
    threshold_frames = []
    for source in SOURCE_META:
        threshold_df = compute_thresholds_for_source(source, panel, lat_map, lon_map)
        source_frame = build_source_frame(source, panel, threshold_df, lat_map, lon_map)
        source_frames.append(source_frame)
        threshold_frames.append(threshold_df)

    panel_wide = panel[["grid_id", "year"]].drop_duplicates().sort_values(["grid_id", "year"]).reset_index(drop=True)
    for frame in source_frames:
        panel_wide = panel_wide.merge(frame, on=["grid_id", "year"], how="left", validate="1:1")

    threshold_all = pd.concat(threshold_frames, ignore_index=True)
    threshold_all = threshold_all.sort_values(
        ["threshold_scheme", "window", "source", "layer", "zone_group"]
    ).reset_index(drop=True)

    validation_df = validate_p20_replay(panel_wide)
    panel_long = build_long_state_table(panel_wide, threshold_all)
    export_outputs(panel_wide, panel_long, threshold_all, validation_df)

    LOGGER.info("Validation exact-match rows: %s", int(validation_df["exact_match"].sum()))
    LOGGER.info("Threshold rows: pooled=%s, maize_zone=%s",
                int((threshold_all["threshold_scheme"] == "pooled").sum()),
                int((threshold_all["threshold_scheme"] == "maize_zone").sum()))
    LOGGER.info("=== v4smstate_build_statevars.py COMPLETE ===")


if __name__ == "__main__":
    main()
