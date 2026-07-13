"""
s07_calc_compound.py - Compound stress indicators by phenological window
Purpose: Calculate hot-dry day counts using multi-source dry definitions
Author: Data Build Pipeline
Date: 2026-04-07
Input: data/intermediate/panel_windows.csv, daily temp + soil moisture + precipitation
Output: data/intermediate/compound_windows.csv
"""

import sys
import os
import time as timer

import netCDF4 as nc
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *
from s03_calc_precip_windows import build_chm_alignment, load_precip_year
from s04a_calc_sm_gleam import compute_sm_baseline_percentiles
from s04b_calc_sm_swsm import compute_swsm_baseline_percentiles
from s04c_calc_sm_era5land import (
    build_era5l_alignment,
    compute_era5l_baseline_percentiles,
    load_era5l_year,
)

np.random.seed(RANDOM_SEED)


def build_var_names(source_key):
    """Return all output variables for one dry-source family."""
    source_cfg = COMPOUND_DRY_SOURCE_REGISTRY[source_key]
    var_names = []

    for hot_t in COMPOUND_HOT_THRESHOLDS:
        if source_cfg["type"] == "soil_moisture":
            for pct in COMPOUND_SM_PERCENTILES:
                var_names.append(f"hotdrydays_ge{hot_t}_{source_key}_p{pct}")
        else:
            var_names.append(f"hotdrydays_ge{hot_t}_{source_key}")

    return var_names


def process_compound_window(
    panel_yr,
    tmax_3d,
    dry_3d,
    source_key,
    wname,
    suffix,
    p10_2d=None,
    p20_2d=None,
):
    """Calculate compound hot-dry days for one dry source and one window."""
    ndays = min(tmax_3d.shape[0], dry_3d.shape[0])
    n = len(panel_yr)
    var_names = build_var_names(source_key)
    result = {f"{v}{suffix}": np.full(n, np.nan, dtype=np.float32) for v in var_names}

    starts = panel_yr[f"win_{wname}_start"].values
    ends = panel_yr[f"win_{wname}_end"].values
    lat_idxs = panel_yr["lat_idx"].values.astype(int)
    lon_idxs = panel_yr["lon_idx"].values.astype(int)

    unique_pairs = np.unique(np.column_stack([starts, ends]), axis=0)

    for pair in unique_pairs:
        s_doy, e_doy = int(pair[0]), int(pair[1])
        si = max(0, s_doy - 1)
        ei = min(ndays, e_doy)
        if si >= ei:
            continue

        mask = (starts == s_doy) & (ends == e_doy)
        cell_indices = np.where(mask)[0]
        li = lat_idxs[cell_indices]
        lj = lon_idxs[cell_indices]

        tmax = tmax_3d[si:ei, li, lj]
        dry_data = dry_3d[si:ei, li, lj]
        valid = ~np.isnan(tmax) & ~np.isnan(dry_data)

        if p10_2d is not None:
            cell_p10 = p10_2d[li, lj]
            cell_p20 = p20_2d[li, lj]
            dry10 = (dry_data <= cell_p10[np.newaxis, :]) & valid
            dry20 = (dry_data <= cell_p20[np.newaxis, :]) & valid
        else:
            dry_bool = (dry_data < DRY_DAY_THRESHOLD) & valid

        for hot_t in COMPOUND_HOT_THRESHOLDS:
            hot = (tmax >= hot_t) & valid
            if p10_2d is not None:
                result[f"hotdrydays_ge{hot_t}_{source_key}_p10{suffix}"][cell_indices] = np.sum(
                    hot & dry10, axis=0
                )
                result[f"hotdrydays_ge{hot_t}_{source_key}_p20{suffix}"][cell_indices] = np.sum(
                    hot & dry20, axis=0
                )
            else:
                result[f"hotdrydays_ge{hot_t}_{source_key}{suffix}"][cell_indices] = np.sum(
                    hot & dry_bool, axis=0
                )

    return result


def compute_static_inputs():
    """Precompute baseline percentiles and alignments shared across years."""
    print("\nPreparing compound dry-source inputs...")

    gleam_pattern = "GLEAM_SM_0.1deg_TEMPgrid_{year}.nc"
    swsm_pattern = "SWSM_L123_0.1deg_{year}.nc"

    print("  GLEAM percentiles...")
    gleam_p10_smrz, gleam_p20_smrz = compute_sm_baseline_percentiles(GLEAM_DIR, "SMrz", gleam_pattern)
    gleam_p10_sms, gleam_p20_sms = compute_sm_baseline_percentiles(GLEAM_DIR, "SMs", gleam_pattern)

    print("\n  SWSM percentiles...")
    swsm_p10_l1, swsm_p20_l1 = compute_swsm_baseline_percentiles(SWSM_DIR, "L1", swsm_pattern)
    swsm_p10_l3, swsm_p20_l3 = compute_swsm_baseline_percentiles(SWSM_DIR, "L3", swsm_pattern)

    print("\n  ERA5-Land alignment and percentiles...")
    era5l_lat_map, era5l_lon_map = build_era5l_alignment()
    era5l_p10_swvl1, era5l_p20_swvl1 = compute_era5l_baseline_percentiles(era5l_lat_map, era5l_lon_map, 1)
    era5l_p10_swvl3, era5l_p20_swvl3 = compute_era5l_baseline_percentiles(era5l_lat_map, era5l_lon_map, 3)

    print("\n  Precipitation alignment...")
    chm_lat_map, chm_lon_map, _, _ = build_chm_alignment()

    return {
        "gleam_pattern": gleam_pattern,
        "swsm_pattern": swsm_pattern,
        "era5l_lat_map": era5l_lat_map,
        "era5l_lon_map": era5l_lon_map,
        "chm_lat_map": chm_lat_map,
        "chm_lon_map": chm_lon_map,
        "sm_thresholds": {
            "smrz": {"p10": gleam_p10_smrz, "p20": gleam_p20_smrz},
            "sms": {"p10": gleam_p10_sms, "p20": gleam_p20_sms},
            "swsm_l1": {"p10": swsm_p10_l1, "p20": swsm_p20_l1},
            "swsm_l3": {"p10": swsm_p10_l3, "p20": swsm_p20_l3},
            "era5l_swvl1": {"p10": era5l_p10_swvl1, "p20": era5l_p20_swvl1},
            "era5l_swvl3": {"p10": era5l_p10_swvl3, "p20": era5l_p20_swvl3},
        },
    }


def load_gleam_sources(year, gleam_pattern):
    """Load GLEAM daily SM arrays for one year."""
    fpath = os.path.join(GLEAM_DIR, gleam_pattern.format(year=year))
    ds = nc.Dataset(fpath)
    smrz_3d = np.ma.filled(ds.variables["SMrz"][:], np.nan).astype(np.float32)
    sms_3d = np.ma.filled(ds.variables["SMs"][:], np.nan).astype(np.float32)
    ds.close()
    print(f"    Loaded GLEAM: SMrz {smrz_3d.shape}, SMs {sms_3d.shape}")
    return {"smrz": smrz_3d, "sms": sms_3d}


def load_swsm_sources(year, swsm_pattern):
    """Load SWSM daily arrays for one year."""
    fpath = os.path.join(SWSM_DIR, swsm_pattern.format(year=year))
    ds = nc.Dataset(fpath)
    l1_3d = np.ma.filled(ds.variables["L1"][:], 0).astype(np.float32) / 100.0
    l3_3d = np.ma.filled(ds.variables["L3"][:], 0).astype(np.float32) / 100.0
    ds.close()
    l1_3d[l1_3d == 0] = np.nan
    l3_3d[l3_3d == 0] = np.nan
    print(f"    Loaded SWSM: L1 {l1_3d.shape}, L3 {l3_3d.shape}")
    return {"swsm_l1": l1_3d, "swsm_l3": l3_3d}


def load_era5l_sources(year, lat_map, lon_map):
    """Load ERA5-Land daily arrays for one year, aligned to reference grid."""
    swvl1_3d = load_era5l_year(year, 1, lat_map, lon_map)
    swvl3_3d = load_era5l_year(year, 3, lat_map, lon_map)
    print(f"    Loaded ERA5-Land: swvl1 {swvl1_3d.shape}, swvl3 {swvl3_3d.shape}")
    return {"era5l_swvl1": swvl1_3d, "era5l_swvl3": swvl3_3d}


def process_source_group(panel_yr, tmax_3d, source_arrays, sm_thresholds):
    """Process one source family across all windows."""
    all_results = {}
    for wname, wdef in WINDOWS.items():
        suffix = wdef["suffix"]
        for source_key, dry_3d in source_arrays.items():
            threshold_cfg = sm_thresholds.get(source_key)
            if threshold_cfg is None:
                result = process_compound_window(panel_yr, tmax_3d, dry_3d, source_key, wname, suffix)
            else:
                result = process_compound_window(
                    panel_yr,
                    tmax_3d,
                    dry_3d,
                    source_key,
                    wname,
                    suffix,
                    threshold_cfg["p10"],
                    threshold_cfg["p20"],
                )
            all_results.update(result)
    return all_results


def main():
    print("=" * 70)
    print(f"Step 07: Compound Stress Indicators ({DATA_VERSION.upper()})")
    print("=" * 70)

    panel = pd.read_csv(os.path.join(INTERMEDIATE_DIR, "panel_windows.csv"))
    print(f"Panel: {len(panel)} rows")

    static_inputs = compute_static_inputs()
    sm_thresholds = static_inputs["sm_thresholds"]

    all_dfs = []
    for year in YEARS:
        panel_yr = panel[panel["year"] == year].copy()
        print(f"\nYear {year}: {len(panel_yr)} rows")
        t0 = timer.time()

        fpath_t = os.path.join(TEMP_DIR, f"daily_temp_{year}.nc")
        ds = nc.Dataset(fpath_t)
        tmax_3d = np.ma.filled(ds.variables["t2m_max"][:], np.nan).astype(np.float32)
        ds.close()
        print(f"  Loaded Tmax: {tmax_3d.shape}")

        all_results = {}

        gleam_arrays = load_gleam_sources(year, static_inputs["gleam_pattern"])
        all_results.update(process_source_group(panel_yr, tmax_3d, gleam_arrays, sm_thresholds))
        del gleam_arrays

        swsm_arrays = load_swsm_sources(year, static_inputs["swsm_pattern"])
        all_results.update(process_source_group(panel_yr, tmax_3d, swsm_arrays, sm_thresholds))
        del swsm_arrays

        era5l_arrays = load_era5l_sources(
            year,
            static_inputs["era5l_lat_map"],
            static_inputs["era5l_lon_map"],
        )
        all_results.update(process_source_group(panel_yr, tmax_3d, era5l_arrays, sm_thresholds))
        del era5l_arrays

        precip_3d = load_precip_year(year, static_inputs["chm_lat_map"], static_inputs["chm_lon_map"])
        all_results.update(process_source_group(panel_yr, tmax_3d, {"pr_lt1": precip_3d}, sm_thresholds))
        del precip_3d, tmax_3d

        df_yr = pd.DataFrame(all_results, index=panel_yr.index)
        all_dfs.append(df_yr)
        print(f"  Total year runtime: {timer.time() - t0:.1f}s")

    df_comp = pd.concat(all_dfs).loc[panel.index]
    output = pd.concat(
        [panel[["grid_id", "year", "latitude", "longitude", "lat_idx", "lon_idx"]], df_comp],
        axis=1,
    )

    outpath = os.path.join(INTERMEDIATE_DIR, "compound_windows.csv")
    output.to_csv(outpath, index=False)
    print(f"\nSaved: {outpath} ({len(output)} rows, {len(output.columns)} cols)")

    full_cols = [col for col in output.columns if col.startswith("hotdrydays_") and not any(col.endswith(s) for s in WINDOW_SUFFIXES[1:])]
    print(f"Full-season hotdry columns: {len(full_cols)}")
    for sample_col in [
        "hotdrydays_ge30_smrz_p10",
        "hotdrydays_ge32_sms_p20",
        "hotdrydays_ge35_swsm_l3_p20",
        "hotdrydays_ge32_era5l_swvl3_p10",
        "hotdrydays_ge32_pr_lt1",
    ]:
        if sample_col in output.columns:
            print(
                f"  {sample_col}: mean={output[sample_col].mean():.4f}, "
                f"min={output[sample_col].min():.4f}, max={output[sample_col].max():.4f}"
            )


if __name__ == "__main__":
    main()
