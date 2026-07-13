"""
Shared helpers for soil-moisture state variables.
"""

import numpy as np
import pandas as pd

from config import MAIZE_ZONE_MAP, MAIZE_ZONE_ORDER, SM_STATE_PERCENTILES, V1_ANALYSIS_MAIN_DTA, WINDOWS


def assign_maize_zone(province):
    return MAIZE_ZONE_MAP.get(province, "Other")


def attach_maize_zone(panel):
    meta = pd.read_stata(
        V1_ANALYSIS_MAIN_DTA,
        columns=["latitude", "longitude", "year", "province"],
        convert_categoricals=False,
    )
    meta["lat_int"] = (meta["latitude"] * 10).round().astype(int)
    meta["lon_int"] = (meta["longitude"] * 10).round().astype(int)
    meta = meta[["lat_int", "lon_int", "year", "province"]].drop_duplicates(
        subset=["lat_int", "lon_int", "year"]
    )
    meta["maize_zone"] = meta["province"].map(assign_maize_zone).fillna("Other")

    panel = panel.copy()
    panel["lat_int"] = (panel["latitude"] * 10).round().astype(int)
    panel["lon_int"] = (panel["longitude"] * 10).round().astype(int)
    panel = panel.merge(meta, on=["lat_int", "lon_int", "year"], how="left")
    panel.drop(columns=["lat_int", "lon_int"], inplace=True)
    panel["maize_zone"] = panel["maize_zone"].fillna("Other")
    return panel


def build_state_thresholds(panel, years, load_year_func):
    pooled_buffers = {wname: [] for wname in WINDOWS}
    zone_buffers = {(wname, zone): [] for wname in WINDOWS for zone in MAIZE_ZONE_ORDER}

    for year in years:
        panel_yr = panel.loc[panel["year"] == year].copy()
        sm_3d = load_year_func(year)

        starts_map = {
            wname: panel_yr[f"win_{wname}_start"].to_numpy(dtype=np.int32)
            for wname in WINDOWS
        }
        ends_map = {
            wname: panel_yr[f"win_{wname}_end"].to_numpy(dtype=np.int32)
            for wname in WINDOWS
        }
        lat_idxs = panel_yr["lat_idx"].to_numpy(dtype=np.int32)
        lon_idxs = panel_yr["lon_idx"].to_numpy(dtype=np.int32)
        zones = panel_yr["maize_zone"].to_numpy(dtype=object)

        for wname in WINDOWS:
            unique_pairs = np.unique(np.column_stack([starts_map[wname], ends_map[wname]]), axis=0)
            for s_doy, e_doy in unique_pairs:
                si = max(0, int(s_doy) - 1)
                ei = min(sm_3d.shape[0], int(e_doy))
                if si >= ei:
                    continue

                mask = (starts_map[wname] == s_doy) & (ends_map[wname] == e_doy)
                cell_indices = np.where(mask)[0]
                if cell_indices.size == 0:
                    continue

                sm = sm_3d[si:ei, lat_idxs[cell_indices], lon_idxs[cell_indices]]
                pooled_values = sm[~np.isnan(sm)]
                if pooled_values.size > 0:
                    pooled_buffers[wname].append(pooled_values.astype(np.float32))

                pair_zones = zones[cell_indices]
                for zone in np.unique(pair_zones):
                    zone_mask = pair_zones == zone
                    sm_zone = sm[:, zone_mask]
                    zone_values = sm_zone[~np.isnan(sm_zone)]
                    if zone_values.size > 0:
                        zone_buffers[(wname, str(zone))].append(zone_values.astype(np.float32))

    pooled_lookup = {}
    zone_lookup = {}
    for wname in WINDOWS:
        pooled_arr = np.concatenate(pooled_buffers[wname]) if pooled_buffers[wname] else np.array([], dtype=np.float32)
        if pooled_arr.size == 0:
            raise RuntimeError(f"Missing pooled state support for {wname}")
        pooled_lookup[wname] = {
            "p25": float(np.nanpercentile(pooled_arr, SM_STATE_PERCENTILES["dry"] * 100)),
            "p75": float(np.nanpercentile(pooled_arr, SM_STATE_PERCENTILES["wet"] * 100)),
            "n_valid_days": int(pooled_arr.size),
        }

        for zone in MAIZE_ZONE_ORDER:
            zone_arr = (
                np.concatenate(zone_buffers[(wname, zone)])
                if zone_buffers[(wname, zone)]
                else np.array([], dtype=np.float32)
            )
            if zone_arr.size == 0:
                raise RuntimeError(f"Missing maize-zone state support for {wname} / {zone}")
            zone_lookup[(wname, zone)] = {
                "p25": float(np.nanpercentile(zone_arr, SM_STATE_PERCENTILES["dry"] * 100)),
                "p75": float(np.nanpercentile(zone_arr, SM_STATE_PERCENTILES["wet"] * 100)),
                "n_valid_days": int(zone_arr.size),
            }

    return pooled_lookup, zone_lookup
