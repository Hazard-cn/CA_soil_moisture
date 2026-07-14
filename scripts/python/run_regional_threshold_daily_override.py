"""Execute ``regional-threshold-sr-override-v1`` using daily-Tmax exposure.

This runner never interpolates the external threshold raster.  It refuses to
overwrite an existing run directory and writes all row-level or binary outputs
only below the caller-supplied run directory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from netCDF4 import Dataset, num2date
from PIL import Image
from scipy import stats

from regional_threshold_daily_core import (
    SEED,
    ZONE_ORDER,
    assign_zone,
    build_three_way_state_design,
    build_two_way_design,
    containing_pixel_indices,
    daily_exposure,
    fit_two_way_fe_cluster,
    soil_moisture_metrics,
    standardized_within_collinearity,
    window_bounds,
)
from regional_threshold_inference import (
    block_score_contributions,
    contrast_from_covariance,
    joint_wild_bootstrap,
    spatial_block_labels,
    spatial_hac_covariances,
)


CANONICAL_ID = "regional-threshold-sr-override-v1"
EXPECTED_PANEL_SHA256 = "1aed2f71427d379bf1a71fdce58904d806061842d644dc45d65638e763bab948"
EXPECTED_RASTER_MD5 = "0d9e6c21bf1b25f113e14315863372f2"
EXPECTED_RASTER_SHA256 = "f05e634664c4c6c2e2df352702acd421507162bc54cc067649071521ab1285b0"
WINDOWS = ["full_ext", "v3he", "hema"]
PANEL_COLUMNS = [
    "grid_id",
    "year",
    "lat_idx",
    "lon_idx",
    "latitude",
    "longitude",
    "province",
    "ln_yield",
    "ca",
    "gdd_10_29",
    "pr_sum",
    "v3_doy",
    "he_doy",
    "ma_doy",
    "gleam_smrz_mean",
]


def file_hash(path: Path, algorithm: str = "sha256") -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def geokey_value(keys: tuple[int, ...], key_id: int) -> int | None:
    for offset in range(4, len(keys), 4):
        key, location, count, value = keys[offset : offset + 4]
        if key == key_id and location == 0 and count == 1:
            return int(value)
    return None


def map_external_threshold(panel: pd.DataFrame, raster_path: Path) -> tuple[pd.Series, dict[str, Any]]:
    md5 = file_hash(raster_path, "md5")
    sha256 = file_hash(raster_path, "sha256")
    if md5 != EXPECTED_RASTER_MD5 or sha256 != EXPECTED_RASTER_SHA256:
        raise AssertionError(f"external raster hash mismatch: md5={md5}, sha256={sha256}")
    with Image.open(raster_path) as image:
        if image.size != (514, 76) or image.mode != "F":
            raise AssertionError(f"unexpected raster shape/mode: {image.size}/{image.mode}")
        scale = tuple(float(v) for v in image.tag_v2[33550])
        tiepoint = tuple(float(v) for v in image.tag_v2[33922])
        geokeys = tuple(int(v) for v in image.tag_v2[34735])
        nodata = float(image.tag_v2[42113])
        raster = np.asarray(image, dtype=np.float64)
    if scale[:2] != (0.5, 0.5):
        raise AssertionError(f"unexpected raster resolution: {scale}")
    if geokey_value(geokeys, 1025) != 1 or geokey_value(geokeys, 2048) != 4326:
        raise AssertionError("raster is not EPSG:4326 PixelIsArea")
    x_origin = tiepoint[3] - tiepoint[0] * scale[0]
    y_origin = tiepoint[4] + tiepoint[1] * scale[1]
    rows, cols = containing_pixel_indices(
        panel["longitude"].to_numpy(),
        panel["latitude"].to_numpy(),
        west=x_origin,
        north=y_origin,
        resolution=scale[0],
    )
    inside = (rows >= 0) & (rows < raster.shape[0]) & (cols >= 0) & (cols < raster.shape[1])
    values = np.full(len(panel), np.nan, dtype=np.float64)
    values[inside] = raster[rows[inside], cols[inside]]
    valid = inside & np.isfinite(values) & (values != nodata) & (values > -1e30)
    values[~valid] = np.nan
    valid_raster = np.isfinite(raster) & (raster != nodata) & (raster > -1e30)
    metadata = {
        "md5": md5,
        "sha256": sha256,
        "driver": "GTiff",
        "dtype": "float32",
        "width": int(raster.shape[1]),
        "height": int(raster.shape[0]),
        "crs": "EPSG:4326",
        "pixel_interpretation": "PixelIsArea",
        "resolution_degrees": 0.5,
        "bounds": {
            "west": x_origin,
            "south": y_origin - raster.shape[0] * scale[1],
            "east": x_origin + raster.shape[1] * scale[0],
            "north": y_origin,
        },
        "nodata": nodata,
        "valid_cells": int(valid_raster.sum()),
        "valid_min_c": float(raster[valid_raster].min()),
        "valid_max_c": float(raster[valid_raster].max()),
        "mapping_method": "grid-centre-in-containing-PixelIsArea-cell",
        "interpolation": "none",
    }
    return pd.Series(values, index=panel.index, name="threshold_c"), metadata


def expected_dates(year: int) -> list[tuple[int, int, int]]:
    return [(d.year, d.month, d.day) for d in pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D")]


def read_daily_cube(
    path: Path,
    variable: str,
    time_name: str,
    year: int,
    *,
    expected_units: set[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    with Dataset(path) as ds:
        variable_object = ds.variables[variable]
        expected_dimensions = (time_name, "latitude", "longitude")
        if variable_object.dimensions != expected_dimensions:
            raise AssertionError(
                f"unexpected dimensions for {variable}: {variable_object.dimensions}, expected {expected_dimensions}"
            )
        units = str(getattr(variable_object, "units", ""))
        if units not in expected_units:
            raise AssertionError(f"unexpected units for {variable}: {units!r}, expected {sorted(expected_units)}")
        time_var = ds.variables[time_name]
        dates = num2date(
            time_var[:],
            units=time_var.units,
            calendar=getattr(time_var, "calendar", "standard"),
            only_use_cftime_datetimes=False,
            only_use_python_datetimes=True,
        )
        observed = [(d.year, d.month, d.day) for d in dates]
        if observed != expected_dates(year):
            raise AssertionError(f"non-contiguous or wrong daily axis: {path}")
        values = np.ma.filled(variable_object[:], np.nan).astype(np.float64)
        latitude = np.asarray(ds.variables["latitude"][:], dtype=np.float64)
        longitude = np.asarray(ds.variables["longitude"][:], dtype=np.float64)
    metadata = {
        "variable": variable,
        "units": units,
        "dimensions": list(expected_dimensions),
        "shape": list(values.shape),
        "date_axis_complete": True,
    }
    return values, latitude, longitude, metadata


def verify_phenology(panel: pd.DataFrame, phenology_path: Path) -> dict[str, Any]:
    with Dataset(phenology_path) as ds:
        years = np.asarray(ds.variables["year"][:], dtype=int)
        latitude = np.asarray(ds.variables["latitude"][:], dtype=np.float64)
        longitude = np.asarray(ds.variables["longitude"][:], dtype=np.float64)
        year_lookup = {int(year): idx for idx, year in enumerate(years)}
        year_idx = panel["year"].map(year_lookup).to_numpy(dtype=int)
        lat_idx = panel["lat_idx"].to_numpy(dtype=int)
        lon_idx = panel["lon_idx"].to_numpy(dtype=int)
        mismatches: dict[str, int] = {}
        for variable in ("v3_doy", "he_doy", "ma_doy"):
            raw = np.ma.filled(ds.variables[variable][:], np.nan)
            expected = raw[year_idx, lat_idx, lon_idx]
            observed = panel[variable].to_numpy(dtype=float)
            mismatches[variable] = int((~np.isclose(expected, observed, equal_nan=True)).sum())
    if any(mismatches.values()):
        raise AssertionError(f"V3 phenology differs from source cube: {mismatches}")
    return {
        "years": years.tolist(),
        "shape": [len(years), len(latitude), len(longitude)],
        "v3_panel_mismatches": mismatches,
    }


def support_table(panel: pd.DataFrame) -> pd.DataFrame:
    essential = [
        "ln_yield",
        "ca",
        "gdd_10_29",
        "pr_sum",
        "v3_doy",
        "he_doy",
        "ma_doy",
        "gleam_smrz_mean",
    ]
    named = panel["zone"].isin(ZONE_ORDER) & panel[essential].notna().all(axis=1)
    rows = []
    for zone in ZONE_ORDER:
        zone_mask = named & panel["zone"].eq(zone)
        valid = zone_mask & panel["threshold_c"].notna()
        rows.append(
            {
                "zone": zone,
                "pre_threshold_rows": int(zone_mask.sum()),
                "valid_threshold_rows": int(valid.sum()),
                "row_coverage": float(valid.sum() / zone_mask.sum()),
                "pre_threshold_grids": int(panel.loc[zone_mask, "grid_id"].nunique()),
                "valid_threshold_grids": int(panel.loc[valid, "grid_id"].nunique()),
                "historical_gate": 0.80,
                "historical_gate_pass": bool(valid.sum() / zone_mask.sum() >= 0.80),
                "historical_gate_is_blocking": False,
            }
        )
    return pd.DataFrame(rows)


def aggregate_year(
    panel_year: pd.DataFrame,
    tmax: np.ndarray,
    smrz: np.ndarray,
) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    days = tmax.shape[0]
    for row in panel_year.itertuples(index=False):
        lat_idx, lon_idx = int(row.lat_idx), int(row.lon_idx)
        tseries = tmax[:, lat_idx, lon_idx]
        smseries = smrz[:, lat_idx, lon_idx]
        for window in WINDOWS:
            bounds = window_bounds(window, int(row.v3_doy), int(row.he_doy), int(row.ma_doy), days)
            external = daily_exposure(tseries[bounds.start : bounds.stop], float(row.threshold_c))
            fixed32 = daily_exposure(tseries[bounds.start : bounds.stop], 32.0)
            sm = soil_moisture_metrics(smseries, bounds, antecedent_days=14)
            records.append(
                {
                    "grid_id": int(row.grid_id),
                    "year": int(row.year),
                    "window": window,
                    "window_label": bounds.label,
                    "window_start_index": bounds.start,
                    "window_stop_index": bounds.stop,
                    "window_expected_days": bounds.expected_days,
                    "threshold_c": float(row.threshold_c),
                    "threshold_hdd_cday_daily": external["hdd_cday_daily"],
                    "threshold_exceedance_days_daily": external["exceedance_days_daily"],
                    "threshold_temperature_complete": external["complete"],
                    "fixed32_hdd_cday_daily": fixed32["hdd_cday_daily"],
                    "fixed32_exceedance_days_daily": fixed32["exceedance_days_daily"],
                    "fixed32_temperature_complete": fixed32["complete"],
                    "sm_complete": sm["complete"],
                    "sm_antecedent_mean": sm["antecedent_mean"],
                    "sm_window_mean": sm["window_mean"],
                    "sm_window_min": sm["window_min"],
                    "sm_mean_change": sm["mean_change"],
                    "sm_min_drawdown": sm["min_drawdown"],
                    "sm_antecedent_valid_days": sm["antecedent_valid_days"],
                    "sm_window_valid_days": sm["window_valid_days"],
                }
            )
    return pd.DataFrame.from_records(records)


def linear_combination(fit: Any, weights: dict[str, float]) -> dict[str, float]:
    names = fit.model.data.xnames
    vector = np.zeros(len(names), dtype=np.float64)
    for name, value in weights.items():
        vector[names.index(name)] = value
    estimate = float(vector @ np.asarray(fit.params))
    variance = float(vector @ np.asarray(fit.cov_params()) @ vector)
    se = math.sqrt(max(variance, 0.0))
    groups = np.asarray(fit.cov_kwds["groups"])
    df = max(int(np.unique(groups).size) - 1, 1)
    critical = float(stats.t.ppf(0.975, df=df))
    pvalue = float(2 * stats.t.sf(abs(estimate / se), df=df)) if se > 0 else float(estimate != 0)
    return {
        "estimate": estimate,
        "se": se,
        "p": pvalue,
        "df_cluster": df,
        "ci_low": estimate - critical * se,
        "ci_high": estimate + critical * se,
    }


def run_yield_models(
    analysis: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    result_rows: list[dict[str, Any]] = []
    coefficient_rows: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    fit_bundles: dict[tuple[str, str], dict[str, Any]] = {}
    exposure_map = {
        "external_continuous": "threshold_hdd_cday_daily",
        "fixed_32c": "fixed32_hdd_cday_daily",
    }
    required_base = ["ln_yield", "ca", "gdd_10_29", "pr_sum", "grid_id", "province", "year", "zone"]
    for exposure_label, exposure in exposure_map.items():
        for window in WINDOWS:
            frame = analysis.loc[analysis["window"].eq(window)].dropna(subset=[*required_base, exposure]).copy()
            design, ca_points, endpoints = build_two_way_design(frame, exposure)
            fit, diag = fit_two_way_fe_cluster(frame, "ln_yield", design)
            diagnostics.append({"family": "yield", "exposure": exposure_label, "window": window, **diag})
            for term, estimate, se, pvalue in zip(
                fit.model.data.xnames,
                np.asarray(fit.params),
                np.asarray(fit.bse),
                np.asarray(fit.pvalues),
                strict=True,
            ):
                coefficient_rows.append(
                    {
                        "exposure": exposure_label,
                        "window": window,
                        "term": term,
                        "estimate": float(estimate),
                        "se_cluster_grid": float(se),
                        "p_cluster_grid": float(pvalue),
                    }
                )
            dca = ca_points["p75"] - ca_points["p25"]
            contrast_weights: dict[str, dict[str, float]] = {}
            for zone in ZONE_ORDER:
                de = endpoints[zone]["p90"] - endpoints[zone]["p50"]
                contrast_id = f"{window}::{zone}"
                contrast_weights[contrast_id] = {f"{zone}_ca_exposure": dca * de}
                contrast = linear_combination(fit, contrast_weights[contrast_id])
                low = linear_combination(
                    fit,
                    {
                        f"{zone}_exposure": de,
                        f"{zone}_ca_exposure": (ca_points["p25"] - ca_points["p50"]) * de,
                    },
                )
                high = linear_combination(
                    fit,
                    {
                        f"{zone}_exposure": de,
                        f"{zone}_ca_exposure": (ca_points["p75"] - ca_points["p50"]) * de,
                    },
                )
                zone_ca = frame.loc[frame["zone"].eq(zone), "ca"].quantile([0.25, 0.75]).to_dict()
                region_specific = linear_combination(
                    fit,
                    {
                        f"{zone}_ca_exposure": (float(zone_ca[0.75]) - float(zone_ca[0.25])) * de
                    },
                )
                result_rows.append(
                    {
                        "exposure": exposure_label,
                        "window": window,
                        "zone": zone,
                        "nobs_model": len(frame),
                        "n_grids_model": int(frame["grid_id"].nunique()),
                        "ca_p25": ca_points["p25"],
                        "ca_p50": ca_points["p50"],
                        "ca_p75": ca_points["p75"],
                        "exposure_p50": endpoints[zone]["p50"],
                        "exposure_p90": endpoints[zone]["p90"],
                        "conditional_yield_change_low_sr": low["estimate"],
                        "conditional_yield_change_low_sr_se_cluster_grid": low["se"],
                        "conditional_yield_change_low_sr_p_cluster_grid": low["p"],
                        "conditional_yield_change_low_sr_ci_low": low["ci_low"],
                        "conditional_yield_change_low_sr_ci_high": low["ci_high"],
                        "conditional_yield_change_high_sr": high["estimate"],
                        "conditional_yield_change_high_sr_se_cluster_grid": high["se"],
                        "conditional_yield_change_high_sr_p_cluster_grid": high["p"],
                        "conditional_yield_change_high_sr_ci_low": high["ci_low"],
                        "conditional_yield_change_high_sr_ci_high": high["ci_high"],
                        "high_minus_low_sr_slope_contrast": contrast["estimate"],
                        "high_minus_low_sr_slope_contrast_se_cluster_grid": contrast["se"],
                        "high_minus_low_sr_slope_contrast_p_cluster_grid": contrast["p"],
                        "high_minus_low_sr_slope_contrast_ci_low": contrast["ci_low"],
                        "high_minus_low_sr_slope_contrast_ci_high": contrast["ci_high"],
                        "high_minus_low_sr_slope_contrast_percent": 100.0 * (math.exp(contrast["estimate"]) - 1.0),
                        "high_minus_low_sr_slope_contrast_percent_ci_low": 100.0 * (math.exp(contrast["ci_low"]) - 1.0),
                        "high_minus_low_sr_slope_contrast_percent_ci_high": 100.0 * (math.exp(contrast["ci_high"]) - 1.0),
                        "zone_ca_p25": float(zone_ca[0.25]),
                        "zone_ca_p75": float(zone_ca[0.75]),
                        "region_specific_ca_contrast": region_specific["estimate"],
                        "region_specific_ca_contrast_ci_low": region_specific["ci_low"],
                        "region_specific_ca_contrast_ci_high": region_specific["ci_high"],
                    }
                )
            fit_bundles[(exposure_label, window)] = {
                "frame": frame,
                "design": design,
                "fit": fit,
                "ca_points": ca_points,
                "endpoints": endpoints,
                "contrast_weights": contrast_weights,
            }
    return pd.DataFrame(result_rows), pd.DataFrame(coefficient_rows), diagnostics, fit_bundles


def run_loyo(analysis: pd.DataFrame, yield_results: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame0 = analysis.loc[analysis["window"].eq("full_ext")].dropna(
        subset=["ln_yield", "ca", "gdd_10_29", "pr_sum", "threshold_hdd_cday_daily", "grid_id", "province", "year", "zone"]
    )
    rows = []
    for left_out in sorted(frame0["year"].unique()):
        frame = frame0.loc[frame0["year"].ne(left_out)].copy()
        design, ca_points, endpoints = build_two_way_design(frame, "threshold_hdd_cday_daily")
        fit, diag = fit_two_way_fe_cluster(frame, "ln_yield", design)
        dca = ca_points["p75"] - ca_points["p25"]
        for zone in ZONE_ORDER:
            de = endpoints[zone]["p90"] - endpoints[zone]["p50"]
            value = linear_combination(fit, {f"{zone}_ca_exposure": dca * de})
            rows.append(
                {
                    "left_out_year": int(left_out),
                    "zone": zone,
                    "high_minus_low_sr_slope_contrast": value["estimate"],
                    "se_cluster_grid": value["se"],
                    "p_cluster_grid": value["p"],
                    "contrast_sign": int(np.sign(value["estimate"])),
                    "nobs_model": diag["nobs"],
                    "n_grids_model": diag["n_grids"],
                }
            )
    detail = pd.DataFrame(rows)
    full = yield_results.loc[
        yield_results["exposure"].eq("external_continuous")
        & yield_results["window"].eq("full_ext"),
        ["zone", "high_minus_low_sr_slope_contrast"],
    ].copy()
    full["full_sample_sign"] = np.sign(full["high_minus_low_sr_slope_contrast"]).astype(int)
    detail = detail.merge(full[["zone", "full_sample_sign"]], on="zone", how="left", validate="many_to_one")
    detail["same_direction_as_full"] = detail["contrast_sign"].eq(detail["full_sample_sign"])
    summary = (
        detail.groupby("zone", sort=False)
        .agg(
            full_sample_sign=("full_sample_sign", "first"),
            same_direction_folds=("same_direction_as_full", "sum"),
            total_folds=("same_direction_as_full", "size"),
        )
        .reset_index()
    )
    summary["same_direction_share"] = summary["same_direction_folds"] / summary["total_folds"]
    return detail, summary


def run_sm_models(
    analysis: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[dict[str, Any]]]:
    base_required = [
        "ca",
        "gdd_10_29",
        "pr_sum",
        "threshold_hdd_cday_daily",
        "sm_antecedent_mean",
        "grid_id",
        "province",
        "year",
        "zone",
    ]
    frame = analysis.loc[analysis["window"].eq("full_ext")].dropna(subset=base_required).copy()
    state_design, ca_points, endpoints = build_three_way_state_design(
        frame, "threshold_hdd_cday_daily", "sm_antecedent_mean"
    )
    state_fit, state_diag = fit_two_way_fe_cluster(frame, "ln_yield", state_design)
    vif_table, collinearity = standardized_within_collinearity(frame, state_design)
    dca = ca_points["p75"] - ca_points["p25"]
    state_rows = []
    for zone in ZONE_ORDER:
        de = endpoints[zone]["exposure_p90_cday"] - endpoints[zone]["exposure_p50_cday"]
        for state_label in ("state_p25_m3m3", "state_p75_m3m3"):
            state_delta = endpoints[zone][state_label] - endpoints[zone]["state_p50_m3m3"]
            value = linear_combination(
                state_fit,
                {
                    f"{zone}_ca_exposure": dca * de,
                    f"{zone}_ca_exposure_state": dca * de * state_delta,
                },
            )
            state_rows.append(
                {
                    "zone": zone,
                    "state_endpoint": state_label,
                    "antecedent_smrz_m3m3": endpoints[zone][state_label],
                    "exposure_p50_cday": endpoints[zone]["exposure_p50_cday"],
                    "exposure_p90_cday": endpoints[zone]["exposure_p90_cday"],
                    "high_minus_low_sr_slope_contrast": value["estimate"],
                    "se_cluster_grid": value["se"],
                    "p_cluster_grid": value["p"],
                    "ci_low": value["ci_low"],
                    "ci_high": value["ci_high"],
                    "contrast_percent": 100.0 * (math.exp(value["estimate"]) - 1.0),
                    "contrast_percent_ci_low": 100.0 * (math.exp(value["ci_low"]) - 1.0),
                    "contrast_percent_ci_high": 100.0 * (math.exp(value["ci_high"]) - 1.0),
                    "nobs_model": len(frame),
                    "n_grids_model": int(frame["grid_id"].nunique()),
                }
            )
    channel_rows = []
    diagnostics: list[dict[str, Any]] = [
        {"family": "sm_state_yield", **state_diag, **collinearity}
    ]
    for outcome in ("sm_mean_change", "sm_min_drawdown"):
        channel = frame.dropna(subset=[outcome]).copy()
        design, channel_ca, channel_endpoints = build_two_way_design(channel, "threshold_hdd_cday_daily")
        fit, diag = fit_two_way_fe_cluster(channel, outcome, design)
        diagnostics.append({"family": "sm_channel", "outcome": outcome, **diag})
        channel_dca = channel_ca["p75"] - channel_ca["p25"]
        for zone in ZONE_ORDER:
            de = channel_endpoints[zone]["p90"] - channel_endpoints[zone]["p50"]
            value = linear_combination(fit, {f"{zone}_ca_exposure": channel_dca * de})
            channel_rows.append(
                {
                    "outcome": outcome,
                    "zone": zone,
                    "conditional_smrz_response_contrast": value["estimate"],
                    "se_cluster_grid": value["se"],
                    "p_cluster_grid": value["p"],
                    "ci_low": value["ci_low"],
                    "ci_high": value["ci_high"],
                    "nobs_model": len(channel),
                    "n_grids_model": int(channel["grid_id"].nunique()),
                }
            )
    return pd.DataFrame(state_rows), pd.DataFrame(channel_rows), vif_table, diagnostics


def run_spatial_inference(
    fit_bundles: dict[tuple[str, str], dict[str, Any]],
    *,
    bootstrap_reps: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, list[dict[str, Any]]]:
    contribution_parts: list[pd.DataFrame] = []
    estimates: dict[str, float] = {}
    hac_rows: list[dict[str, Any]] = []
    hac_diagnostics: list[dict[str, Any]] = []
    for window in WINDOWS:
        bundle = fit_bundles[("external_continuous", window)]
        fit, frame = bundle["fit"], bundle["frame"]
        blocks = spatial_block_labels(frame["latitude"], frame["longitude"], degrees=2.0)
        contributions = block_score_contributions(fit, blocks, bundle["contrast_weights"])
        contribution_parts.append(contributions)
        for contrast_id, weights in bundle["contrast_weights"].items():
            estimates[contrast_id] = linear_combination(fit, weights)["estimate"]
        if window == "full_ext":
            covariances, window_hac_diagnostics = spatial_hac_covariances(
                fit, frame, (100.0, 200.0, 300.0)
            )
            hac_diagnostics.extend(
                [{"window": window, **item} for item in window_hac_diagnostics]
            )
            for bandwidth, covariance in covariances.items():
                for contrast_id, weights in bundle["contrast_weights"].items():
                    zone = contrast_id.split("::", maxsplit=1)[1]
                    value = contrast_from_covariance(fit, covariance, weights)
                    hac_rows.append(
                        {
                            "contrast_id": contrast_id,
                            "window": window,
                            "zone": zone,
                            "bandwidth_km": bandwidth,
                            "estimate": value["estimate"],
                            "spatial_hac_se": value["se"],
                            "spatial_hac_ci_low": value["ci_low"],
                            "spatial_hac_ci_high": value["ci_high"],
                            "spatial_hac_p": value["p"],
                        }
                    )
    contributions = pd.concat(contribution_parts, axis=1).fillna(0.0)
    bootstrap, covariance, draws = joint_wild_bootstrap(
        contributions,
        pd.Series(estimates),
        reps=bootstrap_reps,
        seed=SEED,
    )
    bootstrap[["window", "zone"]] = bootstrap["contrast_id"].str.split("::", expand=True)
    return bootstrap, covariance, draws, pd.DataFrame(hac_rows), hac_diagnostics


def make_figures(yield_results: pd.DataFrame, sm_channel: pd.DataFrame, output_dir: Path) -> None:
    plt.rcParams.update({"font.family": "sans-serif", "axes.facecolor": "white", "figure.facecolor": "white"})
    colours = {"NE": "#4477AA", "HHH": "#EE6677", "NW": "#228833", "SH": "#CCBB44", "SW": "#66CCEE"}

    full = yield_results.loc[yield_results["window"].eq("full_ext")].copy()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, exposure, label in zip(
        axes,
        ["external_continuous", "fixed_32c"],
        ["External continuous threshold", "Fixed 32°C"],
        strict=True,
    ):
        block = full.loc[full["exposure"].eq(exposure)].set_index("zone").reindex(ZONE_ORDER)
        x = np.arange(len(ZONE_ORDER))
        for offset, endpoint, marker, endpoint_label in [
            (-0.08, "low_sr", "o", "Common SR P25"),
            (0.08, "high_sr", "s", "Common SR P75"),
        ]:
            estimate = block[f"conditional_yield_change_{endpoint}"].to_numpy()
            low = block[f"conditional_yield_change_{endpoint}_ci_low"].to_numpy()
            high = block[f"conditional_yield_change_{endpoint}_ci_high"].to_numpy()
            ax.errorbar(
                x + offset,
                estimate,
                yerr=[estimate - low, high - estimate],
                fmt=marker,
                capsize=3,
                label=endpoint_label,
            )
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xticks(x, ZONE_ORDER)
        ax.set_title(label)
        ax.set_xlabel("Maize production zone")
        ax.legend(frameon=False)
    axes[0].set_ylabel("Conditional ln-yield change, exposure P50→P90")
    fig.suptitle("Expanded V3−30 to maturity daily-Tmax HDD (preliminary grid-cluster CI)")
    fig.tight_layout()
    fig.savefig(output_dir / "fig1_conditional_yield_changes.png", dpi=300, facecolor="white")
    plt.close(fig)

    external = yield_results.loc[yield_results["exposure"].eq("external_continuous")].copy()
    fig, axes = plt.subplots(1, 3, figsize=(12, 5), sharey=True)
    window_labels = {
        "full_ext": "V3−30 to maturity",
        "v3he": "V3 to heading",
        "hema": "Heading to maturity",
    }
    for ax, window in zip(axes, WINDOWS, strict=True):
        block = external.loc[external["window"].eq(window)].set_index("zone").reindex(ZONE_ORDER)
        x = np.arange(len(ZONE_ORDER))
        for offset, endpoint, marker, endpoint_label in [
            (-0.08, "low_sr", "o", "SR P25"),
            (0.08, "high_sr", "s", "SR P75"),
        ]:
            estimate = block[f"conditional_yield_change_{endpoint}"].to_numpy()
            low = block[f"conditional_yield_change_{endpoint}_ci_low"].to_numpy()
            high = block[f"conditional_yield_change_{endpoint}_ci_high"].to_numpy()
            ax.errorbar(x + offset, estimate, yerr=[estimate - low, high - estimate], fmt=marker, capsize=3, label=endpoint_label)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xticks(x, ZONE_ORDER)
        ax.set_title(window_labels[window])
        ax.set_xlabel("Zone")
    axes[0].set_ylabel("Conditional ln-yield change, daily-Tmax HDD P50→P90")
    axes[-1].legend(frameon=False)
    fig.suptitle("External continuous threshold by phenological window (preliminary grid-cluster CI)")
    fig.tight_layout()
    fig.savefig(output_dir / "fig2_conditional_yield_changes_by_window.png", dpi=300, facecolor="white")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
    for ax, outcome in zip(axes, ["sm_mean_change", "sm_min_drawdown"], strict=True):
        block = sm_channel.loc[sm_channel["outcome"].eq(outcome)].set_index("zone").reindex(ZONE_ORDER)
        y = np.arange(len(ZONE_ORDER))
        est = block["conditional_smrz_response_contrast"].to_numpy()
        ax.errorbar(
            est,
            y,
            xerr=[est - block["ci_low"].to_numpy(), block["ci_high"].to_numpy() - est],
            fmt="o",
            capsize=3,
            color="#4477AA",
        )
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_yticks(y, ZONE_ORDER)
        ax.set_title(outcome)
        ax.set_xlabel("Conditional SMrz difference")
    fig.suptitle("Conditional GLEAM SMrz response contrasts")
    fig.tight_layout()
    fig.savefig(output_dir / "fig3_conditional_smrz_responses.png", dpi=300, facecolor="white")
    plt.close(fig)


def exposure_quantiles(analysis: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for window in WINDOWS:
        for zone in ZONE_ORDER:
            block = analysis.loc[analysis["window"].eq(window) & analysis["zone"].eq(zone)]
            for label, column in {
                "external_hdd": "threshold_hdd_cday_daily",
                "external_days": "threshold_exceedance_days_daily",
                "fixed32_hdd": "fixed32_hdd_cday_daily",
                "fixed32_days": "fixed32_exceedance_days_daily",
            }.items():
                q = block[column].quantile([0.0, 0.25, 0.50, 0.75, 0.90, 1.0])
                rows.append(
                    {
                        "window": window,
                        "zone": zone,
                        "metric": label,
                        "n": int(block[column].notna().sum()),
                        **{f"p{int(p * 100):02d}": float(value) for p, value in q.items()},
                    }
                )
    return pd.DataFrame(rows)


def daily_support(analysis: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for window in WINDOWS:
        for zone in ZONE_ORDER:
            block = analysis.loc[analysis["window"].eq(window) & analysis["zone"].eq(zone)]
            temp_complete = block["threshold_hdd_cday_daily"].notna()
            sm_complete = block["sm_complete"].astype(bool)
            rows.append(
                {
                    "window": window,
                    "zone": zone,
                    "external_threshold_rows": int(len(block)),
                    "external_threshold_grids": int(block["grid_id"].nunique()),
                    "temperature_complete_rows": int(temp_complete.sum()),
                    "temperature_complete_grids": int(block.loc[temp_complete, "grid_id"].nunique()),
                    "sm_complete_rows": int(sm_complete.sum()),
                    "sm_complete_grids": int(block.loc[sm_complete, "grid_id"].nunique()),
                    "temperature_complete_share": float(temp_complete.mean()),
                    "sm_complete_share": float(sm_complete.mean()),
                }
            )
    return pd.DataFrame(rows)


def sample_selection_audit(
    panel: pd.DataFrame, analysis: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build zone/province funnels and included/excluded covariate comparisons."""

    essential = [
        "ln_yield",
        "ca",
        "gdd_10_29",
        "pr_sum",
        "v3_doy",
        "he_doy",
        "ma_doy",
        "gleam_smrz_mean",
    ]
    audit = panel.loc[panel["zone"].isin(ZONE_ORDER)].copy()
    audit["pre_threshold_complete"] = audit[essential].notna().all(axis=1)
    audit["threshold_valid"] = audit["pre_threshold_complete"] & audit["threshold_c"].notna()
    temp = analysis.loc[
        analysis["window"].eq("full_ext"), ["grid_id", "year", "threshold_temperature_complete"]
    ].drop_duplicates(["grid_id", "year"])
    audit = audit.merge(temp, on=["grid_id", "year"], how="left", validate="one_to_one")
    audit["temperature_complete"] = audit["threshold_temperature_complete"].fillna(False).astype(bool)
    audit["model_complete"] = audit["threshold_valid"] & audit["temperature_complete"]
    audit["selection_status"] = np.select(
        [
            ~audit["pre_threshold_complete"],
            audit["pre_threshold_complete"] & ~audit["threshold_valid"],
            audit["threshold_valid"] & ~audit["temperature_complete"],
            audit["model_complete"],
        ],
        ["excluded_pre_threshold", "excluded_threshold", "excluded_tmax", "included_model"],
        default="unclassified",
    )

    def funnel(group_fields: list[str]) -> pd.DataFrame:
        rows: list[dict[str, Any]] = []
        for keys, block in audit.groupby(group_fields, sort=False, dropna=False):
            if not isinstance(keys, tuple):
                keys = (keys,)
            base = {field: key for field, key in zip(group_fields, keys, strict=True)}
            denominator = int(block["pre_threshold_complete"].sum())
            for stage, flag in [
                ("pre_threshold_complete", "pre_threshold_complete"),
                ("external_threshold_valid", "threshold_valid"),
                ("daily_tmax_complete", "temperature_complete"),
                ("model_complete_case", "model_complete"),
            ]:
                selected = block[flag]
                rows.append(
                    {
                        **base,
                        "stage": stage,
                        "rows": int(selected.sum()),
                        "grids": int(block.loc[selected, "grid_id"].nunique()),
                        "share_of_pre_threshold_rows": float(selected.sum() / denominator) if denominator else np.nan,
                    }
                )
        return pd.DataFrame(rows)

    comparison_rows: list[dict[str, Any]] = []
    for (zone, province, status), block in audit.groupby(
        ["zone", "province", "selection_status"], sort=False, dropna=False
    ):
        q = block["ca"].quantile([0.25, 0.50, 0.75])
        comparison_rows.append(
            {
                "zone": zone,
                "province": province,
                "selection_status": status,
                "rows": len(block),
                "grids": int(block["grid_id"].nunique()),
                "ca_mean": float(block["ca"].mean()),
                "ca_p25": float(q.loc[0.25]),
                "ca_p50": float(q.loc[0.50]),
                "ca_p75": float(q.loc[0.75]),
                "ln_yield_mean": float(block["ln_yield"].mean()),
                "ln_yield_sd": float(block["ln_yield"].std()),
                "gdd_10_29_mean": float(block["gdd_10_29"].mean()),
                "pr_sum_mean": float(block["pr_sum"].mean()),
                "threshold_c_mean": float(block["threshold_c"].mean()),
            }
        )
    return funnel(["zone"]), funnel(["zone", "province"]), pd.DataFrame(comparison_rows), audit


def ca_hdd_joint_support(analysis: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    model = analysis.dropna(
        subset=["threshold_hdd_cday_daily", "ca", "zone", "grid_id"]
    ).copy()
    common = model["ca"].quantile([0.25, 0.75]).to_dict()
    for window in WINDOWS:
        for zone in ZONE_ORDER:
            block = model.loc[model["window"].eq(window) & model["zone"].eq(zone)].copy()
            exposure_q = block["threshold_hdd_cday_daily"].quantile([0.50, 0.90]).to_dict()
            zone_ca_q = block["ca"].quantile([0.25, 0.75]).to_dict()
            low_ca = block["ca"] <= common[0.25]
            high_ca = block["ca"] >= common[0.75]
            low_hdd = block["threshold_hdd_cday_daily"] <= exposure_q[0.50]
            high_hdd = block["threshold_hdd_cday_daily"] >= exposure_q[0.90]
            high_decile = block.loc[high_hdd]
            rows.append(
                {
                    "window": window,
                    "zone": zone,
                    "rows": len(block),
                    "grids": int(block["grid_id"].nunique()),
                    "common_ca_p25": float(common[0.25]),
                    "common_ca_p75": float(common[0.75]),
                    "common_ca_p25_within_zone_percentile": float((block["ca"] <= common[0.25]).mean()),
                    "common_ca_p75_within_zone_percentile": float((block["ca"] <= common[0.75]).mean()),
                    "zone_ca_p25": float(zone_ca_q[0.25]),
                    "zone_ca_p75": float(zone_ca_q[0.75]),
                    "hdd_p50": float(exposure_q[0.50]),
                    "hdd_p90": float(exposure_q[0.90]),
                    "low_ca_low_hdd_rows": int((low_ca & low_hdd).sum()),
                    "low_ca_high_hdd_rows": int((low_ca & high_hdd).sum()),
                    "high_ca_low_hdd_rows": int((high_ca & low_hdd).sum()),
                    "high_ca_high_hdd_rows": int((high_ca & high_hdd).sum()),
                    "high_ca_high_hdd_grids": int(block.loc[high_ca & high_hdd, "grid_id"].nunique()),
                    "high_hdd_rows": len(high_decile),
                    "high_hdd_rows_at_or_above_common_ca_p75": int((high_decile["ca"] >= common[0.75]).sum()),
                }
            )
    return pd.DataFrame(rows)


def make_coverage_map(audit: pd.DataFrame, output_path: Path) -> None:
    grid = (
        audit.sort_values(["grid_id", "year"])
        .groupby("grid_id", as_index=False)
        .agg(
            longitude=("longitude", "first"),
            latitude=("latitude", "first"),
            threshold_ever_valid=("threshold_valid", "max"),
            tmax_ever_complete=("temperature_complete", "max"),
            model_ever_included=("model_complete", "max"),
        )
    )
    grid["coverage_status"] = np.select(
        [~grid["threshold_ever_valid"], grid["threshold_ever_valid"] & ~grid["tmax_ever_complete"], grid["model_ever_included"]],
        ["External threshold unavailable", "Daily Tmax unavailable", "Included in at least one model year"],
        default="Other incomplete",
    )
    colours = {
        "External threshold unavailable": "#BBBBBB",
        "Daily Tmax unavailable": "#CC6677",
        "Included in at least one model year": "#4477AA",
        "Other incomplete": "#DDCC77",
    }
    fig, ax = plt.subplots(figsize=(12, 5))
    for status in colours:
        block = grid.loc[grid["coverage_status"].eq(status)]
        ax.scatter(block["longitude"], block["latitude"], s=3, alpha=0.55, c=colours[status], label=f"{status} (n={len(block):,})")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("External-threshold and daily-Tmax model support")
    ax.legend(frameon=False, markerscale=3, loc="lower left")
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, facecolor="white")
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--raster", type=Path, required=True)
    parser.add_argument("--temperature-dir", type=Path, required=True)
    parser.add_argument("--smrz-dir", type=Path, required=True)
    parser.add_argument("--phenology", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--smoke-grids-per-zone", type=int, default=0)
    parser.add_argument("--bootstrap-reps", type=int, default=1_999)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output_dir.exists():
        raise FileExistsError(f"refusing to modify existing run directory: {args.output_dir}")
    required_paths = [args.panel, args.raster, args.phenology]
    required_paths.extend(args.temperature_dir / f"daily_temp_{year}.nc" for year in range(2016, 2020))
    required_paths.extend(args.smrz_dir / f"GLEAM_SM_0.1deg_TEMPgrid_{year}.nc" for year in range(2016, 2020))
    missing = [str(path) for path in required_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing required inputs: {missing}")

    panel_sha256 = file_hash(args.panel)
    if panel_sha256 != EXPECTED_PANEL_SHA256:
        raise AssertionError(f"V3 Parquet hash mismatch: {panel_sha256}")
    panel = pd.read_parquet(args.panel, columns=PANEL_COLUMNS)
    if len(panel) != 69_038 or panel["grid_id"].nunique() != 22_180:
        raise AssertionError(f"unexpected V3 dimensions: {len(panel)}/{panel['grid_id'].nunique()}")
    if panel.duplicated(["grid_id", "year"]).any():
        raise AssertionError("V3 grid_id-year is not unique")
    if (panel.groupby("grid_id")["province"].nunique() > 1).any():
        raise AssertionError("province changes within grid")
    panel["zone"] = assign_zone(panel["province"])
    panel["threshold_c"], raster_metadata = map_external_threshold(panel, args.raster)
    phenology_metadata = verify_phenology(panel, args.phenology)
    support = support_table(panel)

    essential = [
        "ln_yield",
        "ca",
        "gdd_10_29",
        "pr_sum",
        "v3_doy",
        "he_doy",
        "ma_doy",
        "gleam_smrz_mean",
        "threshold_c",
    ]
    work = panel.loc[panel["zone"].isin(ZONE_ORDER) & panel[essential].notna().all(axis=1)].copy()
    if args.smoke_grids_per_zone:
        rng = np.random.default_rng(SEED)
        chosen: list[int] = []
        for zone in ZONE_ORDER:
            grids = work.loc[work["zone"].eq(zone)].groupby("grid_id").filter(lambda x: len(x) >= 3)["grid_id"].unique()
            chosen.extend(rng.choice(grids, size=min(args.smoke_grids_per_zone, len(grids)), replace=False).tolist())
        work = work.loc[work["grid_id"].isin(chosen)].copy()
    work = work.sort_values(["year", "grid_id"], kind="stable")

    exposure_parts = []
    coordinate_checks = []
    cube_metadata: list[dict[str, Any]] = []
    for year in range(2016, 2020):
        temp_path = args.temperature_dir / f"daily_temp_{year}.nc"
        sm_path = args.smrz_dir / f"GLEAM_SM_0.1deg_TEMPgrid_{year}.nc"
        tmax, temp_lat, temp_lon, temp_metadata = read_daily_cube(
            temp_path,
            "t2m_max",
            "valid_time",
            year,
            expected_units={"°C", "degC", "degree_Celsius"},
        )
        smrz, sm_lat, sm_lon, sm_metadata = read_daily_cube(
            sm_path,
            "SMrz",
            "time",
            year,
            expected_units={"m3.m-3", "m3 m-3", "m3/m3"},
        )
        cube_metadata.extend(
            [
                {"year": year, "source": "daily_tmax", **temp_metadata},
                {"year": year, "source": "gleam_smrz", **sm_metadata},
            ]
        )
        if tmax.shape != smrz.shape or not np.allclose(temp_lat, sm_lat) or not np.allclose(temp_lon, sm_lon):
            raise AssertionError(f"temperature/GLEAM grid mismatch in {year}")
        year_panel = work.loc[work["year"].eq(year)]
        lat_idx = year_panel["lat_idx"].to_numpy(dtype=int)
        lon_idx = year_panel["lon_idx"].to_numpy(dtype=int)
        lat_error = float(np.max(np.abs(temp_lat[lat_idx] - year_panel["latitude"].to_numpy())))
        lon_error = float(np.max(np.abs(temp_lon[lon_idx] - year_panel["longitude"].to_numpy())))
        if lat_error > 1e-4 or lon_error > 1e-4:
            raise AssertionError(f"V3/NetCDF coordinate mismatch in {year}: {lat_error}/{lon_error}")
        coordinate_checks.append({"year": year, "lat_max_abs_error": lat_error, "lon_max_abs_error": lon_error})
        exposure_parts.append(aggregate_year(year_panel, tmax, smrz))
        del tmax, smrz
    exposure = pd.concat(exposure_parts, ignore_index=True)
    analysis = exposure.merge(
        work[["grid_id", "year", "zone", "province", "ln_yield", "ca", "gdd_10_29", "pr_sum", "latitude", "longitude"]],
        on=["grid_id", "year"],
        how="left",
        validate="many_to_one",
    )
    if len(analysis) != 3 * len(work):
        raise AssertionError("exposure output is not exactly three rows per grid-year")

    funnel_zone, funnel_province, selection_comparison, selection_audit = sample_selection_audit(
        panel if not args.smoke_grids_per_zone else panel.loc[panel["grid_id"].isin(work["grid_id"].unique())],
        analysis,
    )
    joint_support = ca_hdd_joint_support(analysis)

    yield_results, coefficient_results, yield_diagnostics, fit_bundles = run_yield_models(analysis)
    loyo, loyo_summary = run_loyo(analysis, yield_results)
    sm_state, sm_channel, sm_vif, sm_diagnostics = run_sm_models(analysis)
    bootstrap, joint_covariance, bootstrap_draws, spatial_hac, hac_diagnostics = run_spatial_inference(
        fit_bundles,
        bootstrap_reps=args.bootstrap_reps,
    )

    args.output_dir.mkdir(parents=True, exist_ok=False)
    support.to_csv(args.output_dir / "sample_support_by_zone.csv", index=False, lineterminator="\n")
    exposure.to_parquet(args.output_dir / "daily_exposure_panel.parquet", index=False)
    daily_support_table = daily_support(analysis)
    daily_support_table.to_csv(args.output_dir / "daily_support_by_zone_window.csv", index=False, lineterminator="\n")
    quantiles = exposure_quantiles(analysis)
    quantiles.to_csv(args.output_dir / "exposure_quantiles.csv", index=False, lineterminator="\n")
    funnel_zone.to_csv(args.output_dir / "sample_funnel_zone.csv", index=False, lineterminator="\n")
    funnel_province.to_csv(args.output_dir / "sample_funnel_province.csv", index=False, lineterminator="\n")
    selection_comparison.to_csv(args.output_dir / "sample_selection_comparison.csv", index=False, lineterminator="\n")
    joint_support.to_csv(args.output_dir / "ca_hdd_joint_support.csv", index=False, lineterminator="\n")
    yield_results.to_csv(args.output_dir / "yield_results.csv", index=False, lineterminator="\n")
    coefficient_results.to_csv(args.output_dir / "model_coefficients.csv", index=False, lineterminator="\n")
    loyo.to_csv(args.output_dir / "loyo_results.csv", index=False, lineterminator="\n")
    loyo_summary.to_csv(args.output_dir / "loyo_direction_summary.csv", index=False, lineterminator="\n")
    sm_state.to_csv(args.output_dir / "sm_state_results.csv", index=False, lineterminator="\n")
    sm_channel.to_csv(args.output_dir / "sm_channel_results.csv", index=False, lineterminator="\n")
    sm_vif.to_csv(args.output_dir / "sm_state_vif.csv", index=False, lineterminator="\n")
    bootstrap.to_csv(args.output_dir / "wild_bootstrap_primary_results.csv", index=False, lineterminator="\n")
    joint_covariance.to_csv(args.output_dir / "wild_bootstrap_joint_covariance.csv", index=True, index_label="contrast_id", lineterminator="\n")
    bootstrap_draws.to_parquet(args.output_dir / "wild_bootstrap_centered_draws.parquet", index=False)
    spatial_hac.to_csv(args.output_dir / "spatial_hac_primary_results.csv", index=False, lineterminator="\n")
    make_figures(yield_results, sm_channel, args.output_dir)
    make_coverage_map(selection_audit, args.output_dir / "fig4_sample_coverage_map.png")

    stata_bundle = fit_bundles[("external_continuous", "full_ext")]
    stata_frame = stata_bundle["frame"]
    stata_design = stata_bundle["design"]
    stata_input = pd.concat(
        [
            stata_frame[["ln_yield", "grid_id", "year"]].reset_index(drop=True),
            pd.Series(
                pd.factorize(stata_frame["province"].astype(str) + "::" + stata_frame["year"].astype(str), sort=True)[0] + 1,
                name="province_year_id",
            ),
            stata_design.reset_index(drop=True),
        ],
        axis=1,
    )
    stata_input.to_stata(args.output_dir / "stata_replication_input.dta", write_index=False, version=118)

    input_records = []
    for path in required_paths:
        input_records.append(
            {
                "path": path.as_posix(),
                "bytes": path.stat().st_size,
                "sha256": file_hash(path),
            }
        )
    script_paths = [
        Path(__file__).resolve(),
        Path(__file__).resolve().with_name("regional_threshold_daily_core.py"),
        Path(__file__).resolve().with_name("regional_threshold_inference.py"),
    ]
    manifest = {
        "canonical_id": CANONICAL_ID,
        "run_id": args.output_dir.name,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "COMPLETED_DAILY_TMAX_EXPOSURE",
        "smoke_grids_per_zone": args.smoke_grids_per_zone,
        "not_hourly_replication": True,
        "hourly_consistency_validation": "NOT_PERFORMED_NO_COMMON_HOURLY_SAMPLE",
        "historical_coverage_gate_is_blocking": False,
        "seed": SEED,
        "inputs": input_records,
        "execution_code": [
            {"path": path.as_posix(), "bytes": path.stat().st_size, "sha256": file_hash(path)} for path in script_paths
        ],
        "panel": {
            "rows": int(len(panel)),
            "grids": int(panel["grid_id"].nunique()),
            "key_unique": True,
            "analysis_rows_before_window_expansion": int(len(work)),
            "analysis_grids": int(work["grid_id"].nunique()),
        },
        "raster": raster_metadata,
        "phenology": phenology_metadata,
        "coordinate_checks": coordinate_checks,
        "cube_metadata": cube_metadata,
        "windows": {
            "full_ext": "[V3-30, MA] inclusive endpoints",
            "v3he": "[V3, HE)",
            "hema": "[HE, MA] inclusive MA",
        },
        "exposure": {
            "primary": "sum(max(daily Tmax - external continuous threshold, 0))",
            "secondary": "count(daily Tmax >= external continuous threshold)",
            "comparison": "same daily metrics at fixed 32C",
            "interpolation": "none",
            "measurement_role": "independent daily-Tmax exposure; not an approximation to CalExposure hourly duration",
        },
        "fixed_effects": ["grid", "province-by-year recomputed from province and year"],
        "inference": {
            "preliminary": "grid-clustered covariance",
            "primary": "2-degree Rademacher spatial-block multiplier wild bootstrap",
            "bootstrap_reps": args.bootstrap_reps,
            "bootstrap_seed": SEED,
            "joint_family": "15 external-threshold zone-by-phenology high-minus-low SR slope contrasts",
            "multiplicity": ["Romano-Wolf stepdown", "Holm"],
            "spatial_hac": "Conley Bartlett within year plus arbitrary serial correlation within grid; full_ext primary window at 100/200/300 km",
        },
        "yield_model_diagnostics": yield_diagnostics,
        "sm_model_diagnostics": sm_diagnostics,
        "spatial_hac_diagnostics": hac_diagnostics,
        "loyo_direction_summary": loyo_summary.to_dict(orient="records"),
        "outputs": {},
    }
    for path in sorted(args.output_dir.iterdir()):
        if path.is_file():
            manifest["outputs"][path.name] = {"bytes": path.stat().st_size, "sha256": file_hash(path)}
    manifest_path = args.output_dir / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": manifest["run_id"], "status": manifest["status"], "analysis_rows": len(work)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
