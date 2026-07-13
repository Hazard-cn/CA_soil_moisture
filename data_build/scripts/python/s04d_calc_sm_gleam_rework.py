"""
s04d_calc_sm_gleam_rework.py -- Rebuild GLEAM dry/wet state variables
Purpose: Build new GLEAM-only md-event and window-baseline families
Author: Data Build Pipeline
Date: 2026-04-22
Input: data/intermediate/panel_windows.csv, GLEAM aligned NetCDF, ChinaCropPhen1km maize TIFFs
Output: data/intermediate/sm_gleam_rework_windows.csv
"""

import os
import sys
import time as timer
import warnings

import netCDF4 as nc
import numpy as np
import pandas as pd
from PIL import Image
from pyproj import Transformer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

np.random.seed(RANDOM_SEED)


FILE_PATTERN = "GLEAM_SM_0.1deg_TEMPgrid_{year}.nc"
PHENO_TIF_PATTERN = "CHN_Maize_{stage}_{year}.tif"
SOURCE_MAP = {
    "gleam_smrz": "SMrz",
    "gleam_sms": "SMs",
}
TARGET_WINDOW_NAMES = GLEAM_REWORK_WINDOWS
PHENO_STAGE_MAP = {
    "v3_doy": "V3",
    "he_doy": "HE",
    "ma_doy": "MA",
}


def load_gleam_year(year, var_name):
    fpath = os.path.join(GLEAM_DIR, FILE_PATTERN.format(year=year))
    ds = nc.Dataset(fpath)
    sm = np.ma.filled(ds.variables[var_name][:], np.nan).astype(np.float32)
    ds.close()
    return sm


def read_maize_tif(tif_path):
    img = Image.open(tif_path)
    arr = np.array(img, dtype=np.float32)
    nodata = img.tag_v2.get(42113)
    if nodata is not None:
        try:
            nodata = float(nodata)
            arr[np.isclose(arr, nodata)] = np.nan
        except (TypeError, ValueError):
            pass

    # Phenology rasters store DOY-like values; any value outside [1, 366]
    # is treated as missing even when the GeoTIFF nodata tag is incomplete.
    arr[(arr <= 0) | (arr > 366)] = np.nan

    scale = img.tag_v2[33550]
    tie = img.tag_v2[33922]
    meta = {
        "px_w": float(scale[0]),
        "px_h": float(scale[1]),
        "x0": float(tie[3]),
        "y0": float(tie[4]),
        "n_rows": arr.shape[0],
        "n_cols": arr.shape[1],
    }
    return arr, meta


def rect_sum(prefix_sum, rmin, cmin, rmax, cmax):
    return (
        prefix_sum[rmax + 1, cmax + 1]
        - prefix_sum[rmin, cmax + 1]
        - prefix_sum[rmax + 1, cmin]
        + prefix_sum[rmin, cmin]
    )


def build_grid_boxes(unique_grids, tif_meta):
    transformer = Transformer.from_crs("EPSG:4326", CHINA_MAIZE_PROJ4, always_xy=True)

    lon = unique_grids["longitude"].to_numpy(dtype=np.float64)
    lat = unique_grids["latitude"].to_numpy(dtype=np.float64)

    corners_lon = np.column_stack([lon - 0.05, lon + 0.05, lon + 0.05, lon - 0.05])
    corners_lat = np.column_stack([lat - 0.05, lat - 0.05, lat + 0.05, lat + 0.05])
    xs, ys = transformer.transform(corners_lon, corners_lat)

    cmin = np.floor((np.nanmin(xs, axis=1) - tif_meta["x0"]) / tif_meta["px_w"]).astype(np.int32)
    cmax = np.floor((np.nanmax(xs, axis=1) - tif_meta["x0"]) / tif_meta["px_w"]).astype(np.int32)
    rmin = np.floor((tif_meta["y0"] - np.nanmax(ys, axis=1)) / tif_meta["px_h"]).astype(np.int32)
    rmax = np.floor((tif_meta["y0"] - np.nanmin(ys, axis=1)) / tif_meta["px_h"]).astype(np.int32)

    cmin = np.clip(cmin, 0, tif_meta["n_cols"] - 1)
    cmax = np.clip(cmax, 0, tif_meta["n_cols"] - 1)
    rmin = np.clip(rmin, 0, tif_meta["n_rows"] - 1)
    rmax = np.clip(rmax, 0, tif_meta["n_rows"] - 1)

    return pd.DataFrame(
        {
            "grid_id": unique_grids["grid_id"].to_numpy(dtype=np.int32),
            "rmin": rmin,
            "rmax": rmax,
            "cmin": cmin,
            "cmax": cmax,
        }
    )


def sample_tif_to_grid_means(tif_path, boxes):
    arr, _ = read_maize_tif(tif_path)
    valid = ~np.isnan(arr)
    arr_filled = np.where(valid, arr, 0.0).astype(np.float64)

    sum_prefix = np.pad(arr_filled.cumsum(axis=0).cumsum(axis=1), ((1, 0), (1, 0)), constant_values=0.0)
    cnt_prefix = np.pad(valid.astype(np.int32).cumsum(axis=0).cumsum(axis=1), ((1, 0), (1, 0)), constant_values=0)

    rmin = boxes["rmin"].to_numpy(dtype=np.int32)
    rmax = boxes["rmax"].to_numpy(dtype=np.int32)
    cmin = boxes["cmin"].to_numpy(dtype=np.int32)
    cmax = boxes["cmax"].to_numpy(dtype=np.int32)

    sums = rect_sum(sum_prefix, rmin, cmin, rmax, cmax)
    counts = rect_sum(cnt_prefix, rmin, cmin, rmax, cmax)

    out = np.full(len(boxes), np.nan, dtype=np.float32)
    has_values = counts > 0
    out[has_values] = np.rint(sums[has_values] / counts[has_values]).astype(np.float32)
    return out


def build_rework_phenology(panel):
    print("  Building 2013-2019 phenology windows from ChinaCropPhen1km maize TIFFs...")

    unique_grids = (
        panel[["grid_id", "latitude", "longitude", "lat_idx", "lon_idx"]]
        .drop_duplicates(subset=["grid_id"])
        .sort_values("grid_id")
        .reset_index(drop=True)
    )

    sample_tif = os.path.join(CHINA_MAIZE_PHENO_DIR, PHENO_TIF_PATTERN.format(stage="V3", year=2016))
    _, tif_meta = read_maize_tif(sample_tif)
    boxes = build_grid_boxes(unique_grids, tif_meta)

    fallback = panel[["grid_id", "year", "v3_doy", "he_doy", "ma_doy"]].copy()
    yearly_frames = []

    for year in GLEAM_REWORK_BASELINE_YEARS:
        year_df = unique_grids.copy()
        year_df["year"] = year
        print(f"    Sampling maize phenology TIFFs for {year}...")

        for doy_col, stage in PHENO_STAGE_MAP.items():
            tif_path = os.path.join(CHINA_MAIZE_PHENO_DIR, PHENO_TIF_PATTERN.format(stage=stage, year=year))
            year_df[doy_col] = sample_tif_to_grid_means(tif_path, boxes)

        yearly_frames.append(year_df)

    phen = pd.concat(yearly_frames, axis=0, ignore_index=True)
    phen = phen.merge(
        fallback.rename(
            columns={
                "v3_doy": "v3_doy_panel",
                "he_doy": "he_doy_panel",
                "ma_doy": "ma_doy_panel",
            }
        ),
        on=["grid_id", "year"],
        how="left",
    )

    for col in ("v3_doy", "he_doy", "ma_doy"):
        panel_col = f"{col}_panel"
        phen[col] = phen[col].fillna(phen[panel_col])
        phen[col] = phen[col].astype(np.float32)

    phen["valid_pheno"] = (
        phen["v3_doy"].notna()
        & phen["he_doy"].notna()
        & phen["ma_doy"].notna()
        & (phen["v3_doy"] < phen["he_doy"])
        & (phen["he_doy"] < phen["ma_doy"])
        & (phen["v3_doy"] > 0)
        & (phen["ma_doy"] < 366)
    )

    for wname in TARGET_WINDOW_NAMES:
        start_col = f"win_{wname}_start"
        end_col = f"win_{wname}_end"

        phen[start_col] = np.nan
        phen[end_col] = np.nan

    valid = phen["valid_pheno"]
    phen.loc[valid, "win_v3pre30_start"] = (phen.loc[valid, "v3_doy"] - 30).clip(lower=1, upper=366)
    phen.loc[valid, "win_v3pre30_end"] = phen.loc[valid, "v3_doy"].clip(lower=1, upper=366)
    phen.loc[valid, "win_v3he_start"] = phen.loc[valid, "v3_doy"].clip(lower=1, upper=366)
    phen.loc[valid, "win_v3he_end"] = phen.loc[valid, "he_doy"].clip(lower=1, upper=366)
    phen.loc[valid, "win_hema_start"] = phen.loc[valid, "he_doy"].clip(lower=1, upper=366)
    phen.loc[valid, "win_hema_end"] = phen.loc[valid, "ma_doy"].clip(lower=1, upper=366)

    for wname in TARGET_WINDOW_NAMES:
        start_col = f"win_{wname}_start"
        end_col = f"win_{wname}_end"
        days_col = f"win_{wname}_days"
        phen[days_col] = np.nan
        valid_window = phen["valid_pheno"] & phen[start_col].notna() & phen[end_col].notna()
        phen.loc[valid_window, days_col] = phen.loc[valid_window, end_col] - phen.loc[valid_window, start_col] + 1

    phen["win_fullnew_days"] = np.nan
    valid_fullnew = (
        phen["valid_pheno"]
        & phen["win_v3pre30_days"].notna()
        & phen["win_v3he_days"].notna()
        & phen["win_hema_days"].notna()
    )
    phen.loc[valid_fullnew, "win_fullnew_days"] = (
        phen.loc[valid_fullnew, "win_v3pre30_days"]
        + phen.loc[valid_fullnew, "win_v3he_days"]
        + phen.loc[valid_fullnew, "win_hema_days"]
        - 2
    )

    keep_cols = [
        "grid_id",
        "year",
        "lat_idx",
        "lon_idx",
        "latitude",
        "longitude",
        "v3_doy",
        "he_doy",
        "ma_doy",
        "valid_pheno",
        "win_v3pre30_start",
        "win_v3pre30_end",
        "win_v3pre30_days",
        "win_v3he_start",
        "win_v3he_end",
        "win_v3he_days",
        "win_hema_start",
        "win_hema_end",
        "win_hema_days",
        "win_fullnew_days",
    ]
    return phen[keep_cols].copy()


def rolling_mean_5day(values_2d):
    """Trailing 5-day mean with NaN propagation. Shape preserved."""
    if values_2d.shape[0] < 5:
        return np.full(values_2d.shape, np.nan, dtype=np.float32)

    filled = np.nan_to_num(values_2d, nan=0.0).astype(np.float64)
    valid = (~np.isnan(values_2d)).astype(np.int32)
    n_cols = values_2d.shape[1]

    csum = np.vstack([np.zeros((1, n_cols), dtype=np.float64), np.cumsum(filled, axis=0)])
    ccount = np.vstack([np.zeros((1, n_cols), dtype=np.int32), np.cumsum(valid, axis=0)])

    sum5 = csum[5:] - csum[:-5]
    count5 = ccount[5:] - ccount[:-5]

    out = np.full(values_2d.shape, np.nan, dtype=np.float32)
    valid5 = count5 == 5
    mean5 = np.full(sum5.shape, np.nan, dtype=np.float32)
    mean5[valid5] = (sum5[valid5] / 5.0).astype(np.float32)
    out[4:] = mean5
    return out


def percentile_against_baseline(current_roll, baseline_roll):
    """Percentile of current rolling values against baseline rolling distribution."""
    out = np.full(current_roll.shape, np.nan, dtype=np.float32)

    for col_idx in range(current_roll.shape[1]):
        baseline = baseline_roll[:, col_idx]
        baseline = baseline[~np.isnan(baseline)]
        if baseline.size == 0:
            continue

        baseline_sorted = np.sort(baseline.astype(np.float64))
        current = current_roll[:, col_idx]
        valid = ~np.isnan(current)
        if not valid.any():
            continue

        current_valid = current[valid].astype(np.float64)
        left = np.searchsorted(baseline_sorted, current_valid, side="left")
        right = np.searchsorted(baseline_sorted, current_valid, side="right")
        out[valid, col_idx] = ((left + right) * 0.5 / baseline_sorted.size * 100.0).astype(np.float32)

    return out


def contiguous_segments(valid_mask):
    start = None
    for idx, flag in enumerate(valid_mask):
        if flag and start is None:
            start = idx
        if not flag and start is not None:
            yield start, idx
            start = None
    if start is not None:
        yield start, len(valid_mask)


def detect_events(percentiles_1d, side):
    events = []
    valid_mask = ~np.isnan(percentiles_1d)

    for seg_start, seg_end in contiguous_segments(valid_mask):
        p = percentiles_1d[seg_start:seg_end]
        seg_len = len(p)
        cursor = 0

        while cursor < seg_len:
            found = False

            if side == "dry":
                start_threshold = 40.0
                target_threshold = 20.0
                severity_anchor = 40.0

                for start_idx in range(cursor, seg_len - 1):
                    if p[start_idx] <= start_threshold:
                        continue
                    for hit_idx in range(start_idx + 1, seg_len):
                        day_gap = hit_idx - start_idx
                        if p[hit_idx] < target_threshold and (p[start_idx] - p[hit_idx]) >= day_gap:
                            end_idx = hit_idx
                            while end_idx + 1 < seg_len and p[end_idx + 1] <= target_threshold:
                                end_idx += 1
                            duration = end_idx - start_idx + 1
                            severity = float(np.nansum(np.maximum(severity_anchor - p[start_idx : end_idx + 1], 0.0)))
                            events.append((duration, severity))
                            cursor = end_idx + 1
                            found = True
                            break
                    if found:
                        break
            else:
                start_threshold = 60.0
                target_threshold = 80.0
                severity_anchor = 60.0

                for start_idx in range(cursor, seg_len - 1):
                    if p[start_idx] >= start_threshold:
                        continue
                    for hit_idx in range(start_idx + 1, seg_len):
                        day_gap = hit_idx - start_idx
                        if p[hit_idx] > target_threshold and (p[hit_idx] - p[start_idx]) >= day_gap:
                            end_idx = hit_idx
                            while end_idx + 1 < seg_len and p[end_idx + 1] >= target_threshold:
                                end_idx += 1
                            duration = end_idx - start_idx + 1
                            severity = float(np.nansum(np.maximum(p[start_idx : end_idx + 1] - severity_anchor, 0.0)))
                            events.append((duration, severity))
                            cursor = end_idx + 1
                            found = True
                            break
                    if found:
                        break

            if not found:
                break

    return events


def compute_md_metrics(current_sm, baseline_chunks, calendar_days):
    n_cells = current_sm.shape[1]
    outputs = {
        "mdduration_dry": np.full(n_cells, np.nan, dtype=np.float32),
        "mddurshare_dry": np.full(n_cells, np.nan, dtype=np.float32),
        "mdseverity_dry": np.full(n_cells, np.nan, dtype=np.float32),
        "mdduration_wet": np.full(n_cells, np.nan, dtype=np.float32),
        "mddurshare_wet": np.full(n_cells, np.nan, dtype=np.float32),
        "mdseverity_wet": np.full(n_cells, np.nan, dtype=np.float32),
    }

    baseline_roll = np.concatenate([rolling_mean_5day(chunk) for chunk in baseline_chunks], axis=0)
    current_roll = rolling_mean_5day(current_sm)
    current_pct = percentile_against_baseline(current_roll, baseline_roll)
    baseline_counts = np.sum(~np.isnan(baseline_roll), axis=0)

    for col_idx in range(n_cells):
        current_valid = np.sum(~np.isnan(current_sm[:, col_idx]))
        has_baseline = baseline_counts[col_idx] > 0
        if current_valid == 0 or not has_baseline:
            continue

        dry_events = detect_events(current_pct[:, col_idx], side="dry")
        wet_events = detect_events(current_pct[:, col_idx], side="wet")

        dry_duration = float(sum(event[0] for event in dry_events))
        wet_duration = float(sum(event[0] for event in wet_events))
        dry_severity = float(sum(event[1] for event in dry_events))
        wet_severity = float(sum(event[1] for event in wet_events))

        outputs["mdduration_dry"][col_idx] = dry_duration
        outputs["mddurshare_dry"][col_idx] = dry_duration / calendar_days if calendar_days > 0 else np.nan
        outputs["mdseverity_dry"][col_idx] = dry_severity
        outputs["mdduration_wet"][col_idx] = wet_duration
        outputs["mddurshare_wet"][col_idx] = wet_duration / calendar_days if calendar_days > 0 else np.nan
        outputs["mdseverity_wet"][col_idx] = wet_severity

    return outputs


def compute_window_baseline_metrics(current_sm, baseline_chunks):
    n_cells = current_sm.shape[1]
    valid = ~np.isnan(current_sm)
    valid_days = np.sum(valid, axis=0).astype(np.float32)
    baseline_daily = np.concatenate(baseline_chunks, axis=0)
    baseline_counts = np.sum(~np.isnan(baseline_daily), axis=0)
    eligible = (valid_days > 0) & (baseline_counts > 0)

    p10 = np.full(n_cells, np.nan, dtype=np.float32)
    p20 = np.full(n_cells, np.nan, dtype=np.float32)
    p80 = np.full(n_cells, np.nan, dtype=np.float32)
    p90 = np.full(n_cells, np.nan, dtype=np.float32)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        if eligible.any():
            p10[eligible] = np.nanpercentile(baseline_daily[:, eligible], 10, axis=0).astype(np.float32)
            p20[eligible] = np.nanpercentile(baseline_daily[:, eligible], 20, axis=0).astype(np.float32)
            p80[eligible] = np.nanpercentile(baseline_daily[:, eligible], 80, axis=0).astype(np.float32)
            p90[eligible] = np.nanpercentile(baseline_daily[:, eligible], 90, axis=0).astype(np.float32)

    dry10 = np.where(valid & ~np.isnan(p10[np.newaxis, :]), current_sm <= p10[np.newaxis, :], False)
    dry20 = np.where(valid & ~np.isnan(p20[np.newaxis, :]), current_sm <= p20[np.newaxis, :], False)
    wet80 = np.where(valid & ~np.isnan(p80[np.newaxis, :]), current_sm >= p80[np.newaxis, :], False)
    wet90 = np.where(valid & ~np.isnan(p90[np.newaxis, :]), current_sm >= p90[np.newaxis, :], False)

    dur_dry10 = np.full(n_cells, np.nan, dtype=np.float32)
    dur_dry20 = np.full(n_cells, np.nan, dtype=np.float32)
    dur_wet80 = np.full(n_cells, np.nan, dtype=np.float32)
    dur_wet90 = np.full(n_cells, np.nan, dtype=np.float32)

    dur_dry10[eligible] = np.sum(dry10[:, eligible], axis=0).astype(np.float32)
    dur_dry20[eligible] = np.sum(dry20[:, eligible], axis=0).astype(np.float32)
    dur_wet80[eligible] = np.sum(wet80[:, eligible], axis=0).astype(np.float32)
    dur_wet90[eligible] = np.sum(wet90[:, eligible], axis=0).astype(np.float32)

    dry_gap10 = np.where(valid & ~np.isnan(p10[np.newaxis, :]), np.maximum(p10[np.newaxis, :] - current_sm, 0.0), 0.0)
    dry_gap20 = np.where(valid & ~np.isnan(p20[np.newaxis, :]), np.maximum(p20[np.newaxis, :] - current_sm, 0.0), 0.0)
    wet_gap80 = np.where(valid & ~np.isnan(p80[np.newaxis, :]), np.maximum(current_sm - p80[np.newaxis, :], 0.0), 0.0)
    wet_gap90 = np.where(valid & ~np.isnan(p90[np.newaxis, :]), np.maximum(current_sm - p90[np.newaxis, :], 0.0), 0.0)

    sum_gap10 = np.full(n_cells, np.nan, dtype=np.float32)
    sum_gap20 = np.full(n_cells, np.nan, dtype=np.float32)
    sum_gap80 = np.full(n_cells, np.nan, dtype=np.float32)
    sum_gap90 = np.full(n_cells, np.nan, dtype=np.float32)
    sum_gap10[eligible] = np.sum(dry_gap10[:, eligible], axis=0).astype(np.float32)
    sum_gap20[eligible] = np.sum(dry_gap20[:, eligible], axis=0).astype(np.float32)
    sum_gap80[eligible] = np.sum(wet_gap80[:, eligible], axis=0).astype(np.float32)
    sum_gap90[eligible] = np.sum(wet_gap90[:, eligible], axis=0).astype(np.float32)

    mean_gap10 = np.full(n_cells, np.nan, dtype=np.float32)
    mean_gap20 = np.full(n_cells, np.nan, dtype=np.float32)
    mean_gap80 = np.full(n_cells, np.nan, dtype=np.float32)
    mean_gap90 = np.full(n_cells, np.nan, dtype=np.float32)
    mean_gap10[eligible] = sum_gap10[eligible] / valid_days[eligible]
    mean_gap20[eligible] = sum_gap20[eligible] / valid_days[eligible]
    mean_gap80[eligible] = sum_gap80[eligible] / valid_days[eligible]
    mean_gap90[eligible] = sum_gap90[eligible] / valid_days[eligible]

    durshare_dry10 = np.full(n_cells, np.nan, dtype=np.float32)
    durshare_dry20 = np.full(n_cells, np.nan, dtype=np.float32)
    durshare_wet80 = np.full(n_cells, np.nan, dtype=np.float32)
    durshare_wet90 = np.full(n_cells, np.nan, dtype=np.float32)
    durshare_dry10[eligible] = dur_dry10[eligible] / valid_days[eligible]
    durshare_dry20[eligible] = dur_dry20[eligible] / valid_days[eligible]
    durshare_wet80[eligible] = dur_wet80[eligible] / valid_days[eligible]
    durshare_wet90[eligible] = dur_wet90[eligible] / valid_days[eligible]

    return {
        "valid_days": valid_days,
        "has_baseline": eligible,
        "blduration_dry_p10": dur_dry10,
        "blduration_dry_p20": dur_dry20,
        "blduration_wet_p80": dur_wet80,
        "blduration_wet_p90": dur_wet90,
        "bldurshare_dry_p10": durshare_dry10,
        "bldurshare_dry_p20": durshare_dry20,
        "bldurshare_wet_p80": durshare_wet80,
        "bldurshare_wet_p90": durshare_wet90,
        "blseveritymean_ddf_p10": mean_gap10,
        "blseveritymean_ddf_p20": mean_gap20,
        "blseveritymean_wex_p80": mean_gap80,
        "blseveritymean_wex_p90": mean_gap90,
        "blseveritysum_ddf_p10": sum_gap10,
        "blseveritysum_ddf_p20": sum_gap20,
        "blseveritysum_wex_p80": sum_gap80,
        "blseveritysum_wex_p90": sum_gap90,
        "p10": p10,
        "p20": p20,
        "p80": p80,
        "p90": p90,
    }


def build_aligned_windows_by_year(rework_windows, grid_ids):
    keep_cols = [
        "grid_id",
        "valid_pheno",
        "win_v3pre30_start",
        "win_v3pre30_end",
        "win_v3pre30_days",
        "win_v3he_start",
        "win_v3he_end",
        "win_v3he_days",
        "win_hema_start",
        "win_hema_end",
        "win_hema_days",
        "win_fullnew_days",
    ]
    out = {}
    for year in GLEAM_REWORK_BASELINE_YEARS:
        subset = rework_windows[rework_windows["year"] == year][keep_cols].set_index("grid_id")
        aligned = subset.reindex(grid_ids).reset_index()
        out[year] = aligned
    return out


def get_pair_records(aligned_windows, panel_yr, wname):
    starts = aligned_windows[f"win_{wname}_start"].to_numpy(dtype=np.float32)
    ends = aligned_windows[f"win_{wname}_end"].to_numpy(dtype=np.float32)
    days = aligned_windows[f"win_{wname}_days"].to_numpy(dtype=np.float32)
    lat_idxs = panel_yr["lat_idx"].to_numpy(dtype=np.int32)
    lon_idxs = panel_yr["lon_idx"].to_numpy(dtype=np.int32)

    valid = ~np.isnan(starts) & ~np.isnan(ends) & (days > 0)
    pair_records = {}
    if not valid.any():
        return pair_records

    valid_pairs = np.column_stack([starts[valid].astype(np.int32), ends[valid].astype(np.int32)])
    for s_doy, e_doy in np.unique(valid_pairs, axis=0):
        mask = valid & (starts.astype(np.int32) == s_doy) & (ends.astype(np.int32) == e_doy)
        out_idx = np.where(mask)[0]
        pair_records[(int(s_doy), int(e_doy))] = {
            "out_idx": out_idx,
            "li": lat_idxs[out_idx],
            "lj": lon_idxs[out_idx],
            "starts": starts[out_idx],
            "ends": ends[out_idx],
            "window_days": float(days[out_idx][0]),
        }
    return pair_records


def extract_padded_chunk(sm_3d, starts, ends, li, lj):
    n_cells = len(starts)
    out = np.empty((0, n_cells), dtype=np.float32)
    valid = ~np.isnan(starts) & ~np.isnan(ends)
    if n_cells == 0 or not valid.any():
        return out

    starts_safe = np.where(valid, starts, -9999).astype(np.int32)
    ends_safe = np.where(valid, ends, -9999).astype(np.int32)
    starts_i = starts_safe[valid]
    ends_i = ends_safe[valid]
    valid_pairs = np.column_stack([starts_i, ends_i])

    max_len = 0
    for s_doy, e_doy in np.unique(valid_pairs, axis=0):
        si = max(0, int(s_doy) - 1)
        ei = min(sm_3d.shape[0], int(e_doy))
        max_len = max(max_len, max(0, ei - si))

    if max_len == 0:
        return out

    out = np.full((max_len, n_cells), np.nan, dtype=np.float32)

    for s_doy, e_doy in np.unique(valid_pairs, axis=0):
        local_mask = valid & (starts_safe == s_doy) & (ends_safe == e_doy)
        pos = np.where(local_mask)[0]
        si = max(0, int(s_doy) - 1)
        ei = min(sm_3d.shape[0], int(e_doy))
        if si >= ei:
            continue
        chunk = sm_3d[si:ei, li[pos], lj[pos]].astype(np.float32)
        out[: chunk.shape[0], pos] = chunk

    return out


def trim_first_day(chunk):
    if chunk.shape[0] <= 1:
        return np.empty((0, chunk.shape[1]), dtype=np.float32)
    return chunk[1:, :]


def initialize_output(n_rows):
    output = {}
    for prefix in SOURCE_MAP:
        for wname in TARGET_WINDOW_NAMES:
            suffix = WINDOWS[wname]["suffix"]
            for side in ("dry", "wet"):
                output[f"mdduration_{side}_{prefix}{suffix}"] = np.full(n_rows, np.nan, dtype=np.float32)
                output[f"mddurshare_{side}_{prefix}{suffix}"] = np.full(n_rows, np.nan, dtype=np.float32)
                output[f"mdseverity_{side}_{prefix}{suffix}"] = np.full(n_rows, np.nan, dtype=np.float32)

            for pct in ("p10", "p20"):
                output[f"blduration_dry_{prefix}_{pct}{suffix}"] = np.full(n_rows, np.nan, dtype=np.float32)
                output[f"bldurshare_dry_{prefix}_{pct}{suffix}"] = np.full(n_rows, np.nan, dtype=np.float32)
                output[f"blseveritymean_ddf_{prefix}_{pct}{suffix}"] = np.full(n_rows, np.nan, dtype=np.float32)
                output[f"blseveritysum_ddf_{prefix}_{pct}{suffix}"] = np.full(n_rows, np.nan, dtype=np.float32)

            for pct in ("p80", "p90"):
                output[f"blduration_wet_{prefix}_{pct}{suffix}"] = np.full(n_rows, np.nan, dtype=np.float32)
                output[f"bldurshare_wet_{prefix}_{pct}{suffix}"] = np.full(n_rows, np.nan, dtype=np.float32)
                output[f"blseveritymean_wex_{prefix}_{pct}{suffix}"] = np.full(n_rows, np.nan, dtype=np.float32)
                output[f"blseveritysum_wex_{prefix}_{pct}{suffix}"] = np.full(n_rows, np.nan, dtype=np.float32)

        for side in ("dry", "wet"):
            output[f"mdduration_{side}_{prefix}{FULLNEW_SUFFIX}"] = np.full(n_rows, np.nan, dtype=np.float32)
            output[f"mddurshare_{side}_{prefix}{FULLNEW_SUFFIX}"] = np.full(n_rows, np.nan, dtype=np.float32)
            output[f"mdseverity_{side}_{prefix}{FULLNEW_SUFFIX}"] = np.full(n_rows, np.nan, dtype=np.float32)

        for pct in ("p10", "p20"):
            output[f"blduration_dry_{prefix}_{pct}{FULLNEW_SUFFIX}"] = np.full(n_rows, np.nan, dtype=np.float32)
            output[f"bldurshare_dry_{prefix}_{pct}{FULLNEW_SUFFIX}"] = np.full(n_rows, np.nan, dtype=np.float32)
            output[f"blseveritymean_ddf_{prefix}_{pct}{FULLNEW_SUFFIX}"] = np.full(n_rows, np.nan, dtype=np.float32)
            output[f"blseveritysum_ddf_{prefix}_{pct}{FULLNEW_SUFFIX}"] = np.full(n_rows, np.nan, dtype=np.float32)

        for pct in ("p80", "p90"):
            output[f"blduration_wet_{prefix}_{pct}{FULLNEW_SUFFIX}"] = np.full(n_rows, np.nan, dtype=np.float32)
            output[f"bldurshare_wet_{prefix}_{pct}{FULLNEW_SUFFIX}"] = np.full(n_rows, np.nan, dtype=np.float32)
            output[f"blseveritymean_wex_{prefix}_{pct}{FULLNEW_SUFFIX}"] = np.full(n_rows, np.nan, dtype=np.float32)
            output[f"blseveritysum_wex_{prefix}_{pct}{FULLNEW_SUFFIX}"] = np.full(n_rows, np.nan, dtype=np.float32)

    return output


def initialize_fullnew_accumulators(n_rows):
    acc = {}
    for prefix in SOURCE_MAP:
        acc[prefix] = {
            "full_valid_days": np.zeros(n_rows, dtype=np.float32),
            "has_baseline": np.zeros(n_rows, dtype=bool),
            "md_dry_duration": np.zeros(n_rows, dtype=np.float32),
            "md_wet_duration": np.zeros(n_rows, dtype=np.float32),
            "md_dry_severity": np.zeros(n_rows, dtype=np.float32),
            "md_wet_severity": np.zeros(n_rows, dtype=np.float32),
        }
        for pct in ("p10", "p20"):
            acc[prefix][f"dur_dry_{pct}"] = np.zeros(n_rows, dtype=np.float32)
            acc[prefix][f"sum_ddf_{pct}"] = np.zeros(n_rows, dtype=np.float32)
        for pct in ("p80", "p90"):
            acc[prefix][f"dur_wet_{pct}"] = np.zeros(n_rows, dtype=np.float32)
            acc[prefix][f"sum_wex_{pct}"] = np.zeros(n_rows, dtype=np.float32)
    return acc


def main():
    print("=" * 70)
    print("Step 04d: GLEAM SM Rework (md-event + window-baseline)")
    print("=" * 70)

    panel = pd.read_csv(os.path.join(INTERMEDIATE_DIR, "panel_windows.csv"))
    print(f"Panel: {len(panel)} rows")

    rework_windows = build_rework_phenology(panel)
    print(
        "  Rework phenology coverage by year: "
        + ", ".join(
            [
                f"{year}={rework_windows.loc[rework_windows['year'] == year, 'valid_pheno'].mean():.1%}"
                for year in GLEAM_REWORK_BASELINE_YEARS
            ]
        )
    )

    all_year_frames = []

    for year in YEARS:
        panel_yr = panel[panel["year"] == year].copy().reset_index(drop=True)
        n_rows = len(panel_yr)
        grid_ids = panel_yr["grid_id"].to_numpy(dtype=np.int32)
        aligned_windows = build_aligned_windows_by_year(rework_windows, grid_ids)

        print(f"\n  Year {year}: {n_rows} cells")
        t0 = timer.time()

        output = initialize_output(n_rows)
        fullnew_acc = initialize_fullnew_accumulators(n_rows)
        fullnew_days = aligned_windows[year]["win_fullnew_days"].to_numpy(dtype=np.float32)

        for prefix, var_name in SOURCE_MAP.items():
            print(f"    Processing {prefix}...")
            current_sm = load_gleam_year(year, var_name)

            for wname in TARGET_WINDOW_NAMES:
                print(f"      Window {wname}...")
                current_win = aligned_windows[year]
                pair_records = get_pair_records(current_win, panel_yr, wname)
                drop_first = wname in ("v3he", "hema")

                for pair in pair_records.values():
                    pair["current_orig"] = extract_padded_chunk(
                        current_sm, pair["starts"], pair["ends"], pair["li"], pair["lj"]
                    )
                    pair["current_adj"] = trim_first_day(pair["current_orig"]) if drop_first else pair["current_orig"]
                    pair["baseline_chunks"] = []
                    pair["baseline_chunks_adj"] = []

                for baseline_year in GLEAM_REWORK_BASELINE_YEARS:
                    sm_3d = load_gleam_year(baseline_year, var_name)
                    base_win = aligned_windows[baseline_year]
                    base_starts_all = base_win[f"win_{wname}_start"].to_numpy(dtype=np.float32)
                    base_ends_all = base_win[f"win_{wname}_end"].to_numpy(dtype=np.float32)

                    for pair in pair_records.values():
                        out_idx = pair["out_idx"]
                        chunk = extract_padded_chunk(
                            sm_3d,
                            base_starts_all[out_idx],
                            base_ends_all[out_idx],
                            pair["li"],
                            pair["lj"],
                        )
                        pair["baseline_chunks"].append(chunk)
                        pair["baseline_chunks_adj"].append(trim_first_day(chunk) if drop_first else chunk)

                for pair in pair_records.values():
                    out_idx = pair["out_idx"]
                    current_orig = pair["current_orig"]
                    current_adj = pair["current_adj"]
                    baseline_chunks = pair["baseline_chunks"]
                    baseline_chunks_adj = pair["baseline_chunks_adj"]

                    suffix = WINDOWS[wname]["suffix"]
                    md_metrics = compute_md_metrics(current_orig, baseline_chunks, pair["window_days"])
                    for side in ("dry", "wet"):
                        output[f"mdduration_{side}_{prefix}{suffix}"][out_idx] = md_metrics[f"mdduration_{side}"]
                        output[f"mddurshare_{side}_{prefix}{suffix}"][out_idx] = md_metrics[f"mddurshare_{side}"]
                        output[f"mdseverity_{side}_{prefix}{suffix}"][out_idx] = md_metrics[f"mdseverity_{side}"]

                    bl_metrics = compute_window_baseline_metrics(current_orig, baseline_chunks)
                    for pct in ("p10", "p20"):
                        output[f"blduration_dry_{prefix}_{pct}{suffix}"][out_idx] = bl_metrics[f"blduration_dry_{pct}"]
                        output[f"bldurshare_dry_{prefix}_{pct}{suffix}"][out_idx] = bl_metrics[f"bldurshare_dry_{pct}"]
                        output[f"blseveritymean_ddf_{prefix}_{pct}{suffix}"][out_idx] = bl_metrics[f"blseveritymean_ddf_{pct}"]
                        output[f"blseveritysum_ddf_{prefix}_{pct}{suffix}"][out_idx] = bl_metrics[f"blseveritysum_ddf_{pct}"]
                    for pct in ("p80", "p90"):
                        output[f"blduration_wet_{prefix}_{pct}{suffix}"][out_idx] = bl_metrics[f"blduration_wet_{pct}"]
                        output[f"bldurshare_wet_{prefix}_{pct}{suffix}"][out_idx] = bl_metrics[f"bldurshare_wet_{pct}"]
                        output[f"blseveritymean_wex_{prefix}_{pct}{suffix}"][out_idx] = bl_metrics[f"blseveritymean_wex_{pct}"]
                        output[f"blseveritysum_wex_{prefix}_{pct}{suffix}"][out_idx] = bl_metrics[f"blseveritysum_wex_{pct}"]

                    if current_adj.shape[0] == 0:
                        continue

                    md_adj = compute_md_metrics(current_adj, baseline_chunks_adj, current_adj.shape[0])
                    bl_adj = compute_window_baseline_metrics(current_adj, baseline_chunks_adj)

                    fullnew_acc[prefix]["has_baseline"][out_idx] |= bl_adj["has_baseline"]
                    fullnew_acc[prefix]["full_valid_days"][out_idx] += np.where(
                        bl_adj["has_baseline"], bl_adj["valid_days"], 0.0
                    )
                    fullnew_acc[prefix]["md_dry_duration"][out_idx] += np.where(
                        np.isnan(md_adj["mdduration_dry"]), 0.0, md_adj["mdduration_dry"]
                    )
                    fullnew_acc[prefix]["md_wet_duration"][out_idx] += np.where(
                        np.isnan(md_adj["mdduration_wet"]), 0.0, md_adj["mdduration_wet"]
                    )
                    fullnew_acc[prefix]["md_dry_severity"][out_idx] += np.where(
                        np.isnan(md_adj["mdseverity_dry"]), 0.0, md_adj["mdseverity_dry"]
                    )
                    fullnew_acc[prefix]["md_wet_severity"][out_idx] += np.where(
                        np.isnan(md_adj["mdseverity_wet"]), 0.0, md_adj["mdseverity_wet"]
                    )

                    for pct in ("p10", "p20"):
                        fullnew_acc[prefix][f"dur_dry_{pct}"][out_idx] += np.where(
                            np.isnan(bl_adj[f"blduration_dry_{pct}"]), 0.0, bl_adj[f"blduration_dry_{pct}"]
                        )
                        fullnew_acc[prefix][f"sum_ddf_{pct}"][out_idx] += np.where(
                            np.isnan(bl_adj[f"blseveritysum_ddf_{pct}"]), 0.0, bl_adj[f"blseveritysum_ddf_{pct}"]
                        )
                    for pct in ("p80", "p90"):
                        fullnew_acc[prefix][f"dur_wet_{pct}"][out_idx] += np.where(
                            np.isnan(bl_adj[f"blduration_wet_{pct}"]), 0.0, bl_adj[f"blduration_wet_{pct}"]
                        )
                        fullnew_acc[prefix][f"sum_wex_{pct}"][out_idx] += np.where(
                            np.isnan(bl_adj[f"blseveritysum_wex_{pct}"]), 0.0, bl_adj[f"blseveritysum_wex_{pct}"]
                        )

            has_baseline = fullnew_acc[prefix]["has_baseline"]
            positive_valid = has_baseline & (fullnew_acc[prefix]["full_valid_days"] > 0)
            valid_calendar = has_baseline & (fullnew_days > 0)

            output[f"mdduration_dry_{prefix}{FULLNEW_SUFFIX}"][has_baseline] = fullnew_acc[prefix]["md_dry_duration"][has_baseline]
            output[f"mdduration_wet_{prefix}{FULLNEW_SUFFIX}"][has_baseline] = fullnew_acc[prefix]["md_wet_duration"][has_baseline]
            output[f"mdseverity_dry_{prefix}{FULLNEW_SUFFIX}"][has_baseline] = fullnew_acc[prefix]["md_dry_severity"][has_baseline]
            output[f"mdseverity_wet_{prefix}{FULLNEW_SUFFIX}"][has_baseline] = fullnew_acc[prefix]["md_wet_severity"][has_baseline]
            output[f"mddurshare_dry_{prefix}{FULLNEW_SUFFIX}"][valid_calendar] = (
                fullnew_acc[prefix]["md_dry_duration"][valid_calendar] / fullnew_days[valid_calendar]
            )
            output[f"mddurshare_wet_{prefix}{FULLNEW_SUFFIX}"][valid_calendar] = (
                fullnew_acc[prefix]["md_wet_duration"][valid_calendar] / fullnew_days[valid_calendar]
            )

            for pct in ("p10", "p20"):
                output[f"blduration_dry_{prefix}_{pct}{FULLNEW_SUFFIX}"][has_baseline] = fullnew_acc[prefix][f"dur_dry_{pct}"][has_baseline]
                output[f"blseveritysum_ddf_{prefix}_{pct}{FULLNEW_SUFFIX}"][has_baseline] = fullnew_acc[prefix][f"sum_ddf_{pct}"][has_baseline]
                output[f"bldurshare_dry_{prefix}_{pct}{FULLNEW_SUFFIX}"][positive_valid] = (
                    fullnew_acc[prefix][f"dur_dry_{pct}"][positive_valid] / fullnew_acc[prefix]["full_valid_days"][positive_valid]
                )
                output[f"blseveritymean_ddf_{prefix}_{pct}{FULLNEW_SUFFIX}"][positive_valid] = (
                    fullnew_acc[prefix][f"sum_ddf_{pct}"][positive_valid] / fullnew_acc[prefix]["full_valid_days"][positive_valid]
                )

            for pct in ("p80", "p90"):
                output[f"blduration_wet_{prefix}_{pct}{FULLNEW_SUFFIX}"][has_baseline] = fullnew_acc[prefix][f"dur_wet_{pct}"][has_baseline]
                output[f"blseveritysum_wex_{prefix}_{pct}{FULLNEW_SUFFIX}"][has_baseline] = fullnew_acc[prefix][f"sum_wex_{pct}"][has_baseline]
                output[f"bldurshare_wet_{prefix}_{pct}{FULLNEW_SUFFIX}"][positive_valid] = (
                    fullnew_acc[prefix][f"dur_wet_{pct}"][positive_valid] / fullnew_acc[prefix]["full_valid_days"][positive_valid]
                )
                output[f"blseveritymean_wex_{prefix}_{pct}{FULLNEW_SUFFIX}"][positive_valid] = (
                    fullnew_acc[prefix][f"sum_wex_{pct}"][positive_valid] / fullnew_acc[prefix]["full_valid_days"][positive_valid]
                )

        df_yr = pd.concat(
            [
                panel_yr[["grid_id", "year", "latitude", "longitude", "lat_idx", "lon_idx"]],
                pd.DataFrame(output),
            ],
            axis=1,
        )
        all_year_frames.append(df_yr)
        print(f"    Year total: {timer.time() - t0:.1f}s")

    output = pd.concat(all_year_frames, axis=0, ignore_index=True)
    output.to_csv(GLEAM_REWORK_INTERMEDIATE, index=False)
    print(f"\nSaved: {GLEAM_REWORK_INTERMEDIATE} ({len(output)} rows, {len(output.columns)} cols)")

    print("\nValidation:")
    sample_vars = [
        "mdduration_dry_gleam_smrz_v3pre30",
        "mdseverity_wet_gleam_sms_fullnew",
        "blduration_dry_gleam_smrz_p20_v3he",
        "bldurshare_wet_gleam_sms_p80_hema",
        "blseveritymean_ddf_gleam_smrz_p10_fullnew",
        "blseveritysum_wex_gleam_sms_p90_fullnew",
    ]
    for var in sample_vars:
        if var in output.columns:
            vals = output[var]
            print(
                f"  {var}: mean={vals.mean():.4f}, min={vals.min():.4f}, "
                f"max={vals.max():.4f}, missing={vals.isna().mean()*100:.1f}%"
            )


if __name__ == "__main__":
    main()
