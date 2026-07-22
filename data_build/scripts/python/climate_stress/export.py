"""Canonical, non-overwriting exports for the climate-stress panel."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import netCDF4 as nc
import numpy as np
import pandas as pd

from .grid import TARGET_GRID, TargetGridSpec, validate_v3_crosswalk


CANONICAL_WINDOWS = ("full", "v3pre30", "v3pm10", "hepm10", "v3he", "hema")
OUTPUT_SCOPE_ID = "non2w-dual-severity"
OUTPUT_SCOPE_STATUS = "PARTIAL_SCOPE"
WINDOW_SUFFIXES = {
    "full": "",
    "v3pre30": "_v3pre30",
    "v3pm10": "_v3pm10",
    "hepm10": "_hepm10",
    "v3he": "_v3he",
    "hema": "_hema",
}
SPATIAL_COLUMNS = (
    "era01_cell_id",
    "grid_id_v3",
    "lat_idx",
    "lon_idx",
    "latitude",
    "longitude",
    "lat10",
    "lon10",
)
LONG_KEY_COLUMNS = SPATIAL_COLUMNS + ("year", "window")
WIDE_KEY_COLUMNS = SPATIAL_COLUMNS + ("year",)
STATA_PUBLIC_KEYS = frozenset(WIDE_KEY_COLUMNS)
STATA_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,31}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
VARIABLE_METADATA_FIELDS = (
    "long_name",
    "units",
    "source_product",
    "version",
    "reference_id",
    "history_period",
    "time_window",
    "layer_role",
    "variant_status",
    "scope_id",
    "scope_status",
    "threshold_rule",
    "minimum_duration",
    "gap_rule",
    "recovery_rule",
    "calendar_rule",
    "censor_rule",
    "confirmatory_status",
)


def _humanize_variable_name(name: str) -> str:
    return re.sub(r"_+", " ", name).strip()


def _infer_units(name: str) -> str:
    lower = name.casefold()
    if name in {"latitude", "longitude"}:
        return "degrees"
    if name in {"lat10", "lon10"}:
        return "0.1 degree integer coordinate"
    if name == "year":
        return "year"
    if name == "window":
        return "1"
    if name.endswith("_doy") or "window_start_doy" in lower or "window_end_doy" in lower:
        return "day of year"
    if lower.startswith("chm_spei_"):
        if "window_total_duration_periods_equiv" in lower:
            return "month equivalent"
        if "valid_days" in lower or "event_expected_days" in lower:
            return "day"
        if "duration_month" in lower:
            return "month"
        if "duration_day" in lower:
            return "day"
        if "period" in lower or "severity" in lower:
            return "standardized-index period"
        if any(token in lower for token in ("actual_scale", "end_month")):
            return "month"
        if "count" in lower:
            return "count"
        return "1"
    if lower.startswith("gleam43a_"):
        if "mean_onset_speed" in lower or "max_onset_speed" in lower:
            return "percentile points per pentad"
        if "pctdays" in lower:
            return "percentile point day"
        if "m3m3_days" in lower:
            return "m3 m-3 day"
        if "pentad" in lower and any(token in lower for token in ("duration", "count", "run")):
            return "pentad"
        if any(token in lower for token in ("duration", "_days", "spell")):
            return "day"
        if "count" in lower:
            return "count"
        if any(token in lower for token in ("percentile", "_pct", "_q", "dryness", "speed")):
            return "percentile point"
        if any(token in lower for token in ("deficit_area", "severity")):
            return "m3 m-3 day"
        if any(token in lower for token in ("_any", "_flag", "censored", "coverage")):
            return "1"
        return "m3 m-3"
    if lower.startswith("compound_"):
        if "heat_excess_cdays" in lower:
            return "degree_Celsius day"
        if "sm_deficit_m3m3_days" in lower:
            return "m3 m-3 day"
        if any(token in lower for token in ("duration", "_days", "valid_days")):
            return "day"
        if "count" in lower:
            return "count"
        return "1"
    if lower.startswith("era5u8_") or "heat" in lower or "hot" in lower:
        if any(token in lower for token in ("gdd", "edd", "excess", "degree_day", "cum_", "cumulative")):
            return "degree_Celsius day"
        if any(token in lower for token in ("duration", "_days", "valid_days")):
            return "day"
        if "count" in lower:
            return "count"
        if any(token in lower for token in ("tmean", "tmax", "tmin", "intensity", "temperature")):
            return "degree_Celsius"
    if "coverage" in lower or lower.endswith("_fraction") or lower.endswith("_share"):
        return "1"
    if any(token in lower for token in ("_any", "_flag", "censored", "_valid")):
        return "1"
    if any(token in lower for token in ("_count", "events", "event_count", "pixel_count")):
        return "count"
    if any(token in lower for token in ("duration", "_days", "valid_days", "window_days", "run_length")):
        return "day"
    return "1"


def _infer_source_product(name: str) -> str:
    lower = name.casefold()
    if lower.startswith("era5u8_"):
        return "ERA5 hourly 2 m temperature"
    if lower.startswith("chm_spei_"):
        return "CHM_Drought precomputed SPEI (PET=Penman)"
    if lower.startswith("gleam43a_smrz_"):
        return "GLEAM 4.3a root-zone soil moisture (SMrz)"
    if lower.startswith("gleam43a_sms_"):
        return "GLEAM 4.3a surface soil moisture (SMs)"
    if lower.startswith("compound_") or lower.startswith("hot_flash_"):
        return "ERA5 and GLEAM 4.3a derived compound measure"
    if name in LONG_KEY_COLUMNS:
        return "target-grid and V3 coordinate crosswalk"
    if any(token in lower for token in ("window_", "phenology", "v3_doy", "he_doy", "ma_doy")):
        return "CHN maize phenology TIFF aggregation"
    return "derived climate-stress panel measure"


def _infer_history_period(name: str) -> str:
    lower = name.casefold()
    if lower.startswith("chm_spei_"):
        return "unknown (CHM product fitting/reference period not disclosed)"
    percentile_tokens = (
        "p10",
        "p20",
        "p40",
        "p90",
        "q10",
        "q20",
        "q40",
        "tx90",
        "tn90",
        "heatwave",
        "flash_drought",
        "_fd_",
        "hot_flash",
        "percentile",
        "dryness",
    )
    if lower.startswith(("era5u8_", "gleam43a_", "compound_")) and any(
        token in lower for token in percentile_tokens
    ):
        return "1981-2010 (30 years)"
    return "not applicable"


def _infer_version(name: str) -> str:
    lower = name.casefold()
    if lower.startswith("era5u8_"):
        return "ERA5"
    if lower.startswith("chm_spei_"):
        return "V1.0"
    if lower.startswith("gleam43a_") or lower.startswith("compound_"):
        return "GLEAM 4.3a and/or ERA5 as encoded by source_product"
    if name in LONG_KEY_COLUMNS:
        return "data-climate-stress-2010-2019-v1 target grid"
    return "not specified"


def _infer_reference_id(name: str) -> str:
    lower = name.casefold()
    if lower.startswith("era5u8_"):
        return "Copernicus Climate Data Store: reanalysis-era5-single-levels"
    if lower.startswith("chm_spei_"):
        return (
            "CHM_Drought V1.0; PET=Penman; product coverage=1961-2022; "
            "fit/reference period=unknown"
        )
    if lower.startswith("gleam43a_smrz_"):
        return "GLEAM v4.3a SMrz"
    if lower.startswith("gleam43a_sms_"):
        return "GLEAM v4.3a SMs"
    if lower.startswith("compound_") or lower.startswith("hot_flash_"):
        return "derived from ERA5 and GLEAM v4.3a"
    if name in LONG_KEY_COLUMNS:
        return "EPSG:4326 frozen 0.1-degree target grid and V3 coordinate crosswalk"
    return "documented in material passport"


def _infer_time_window(name: str) -> str:
    lower = name.casefold()
    if name == "year":
        return "calendar year label"
    if name == "window" or "window_" in lower:
        return "closed phenological interval clipped to the calendar year"
    if lower.startswith("era5u8_"):
        return "Beijing civil day (UTC+8), then closed phenological interval"
    if lower.startswith("chm_spei_"):
        if "2w" in lower:
            return "native 2-week accumulation released every 7 days"
        if "s1" in lower or "spei1" in lower:
            return "native monthly SPEI-1 allocated by actual interval overlap"
        if "s3" in lower or "spei3" in lower:
            return "native monthly SPEI-3 allocated by actual interval overlap"
        return "native monthly CHM support; accumulation scale encoded by variable"
    if lower.startswith("gleam43a_"):
        if "_fd_" in lower or "pentad" in lower or "pct" in lower:
            return "fixed 73 calendar pentads; February 29 excluded"
        return "daily GLEAM; February 29 retained"
    if lower.startswith("compound_") or lower.startswith("hot_flash_"):
        return "daily or calendar-pentad overlap as encoded by variable"
    return "not applicable"


def _infer_layer_role(
    name: str,
    gleam_layer_roles: Mapping[str, str] | None,
) -> str:
    lower = name.casefold()
    roles = {"smrz": "primary", "sms": "supplementary"}
    roles.update(
        {
            str(layer).casefold(): str(role)
            for layer, role in (gleam_layer_roles or {}).items()
        }
    )
    for layer, role in sorted(roles.items(), key=lambda item: -len(item[0])):
        if lower.startswith(f"gleam43a_{layer}_") or lower.startswith(
            f"compound_{layer}_"
        ):
            return role
    return "not_applicable"


def _infer_variant_status(name: str) -> str:
    """Assign one status using quality > sensitivity > strict > primary."""

    lower = name.casefold()
    if any(
        token in lower
        for token in ("audit", "coverage", "valid_days", "expected_days", "censored")
    ):
        return "quality_or_audit"
    if any(token in lower for token in ("sensitivity", "gap2", "k15")):
        return "sensitivity"
    if any(token in lower for token in ("strict", "p10_overlap")):
        return "strict"
    return "primary"


def _infer_rules(name: str) -> dict[str, str]:
    lower = name.casefold()
    threshold = "not applicable"
    minimum = "not applicable"
    gap = "not applicable"
    recovery = "not applicable"
    calendar = "calendar-year clipped phenological window; closed interval"
    censor = "event overlap is window-truncated; full-event identifier and boundary censoring retained where applicable"
    status = "primary"
    if any(token in lower for token in ("tx90", "tn90", "p90", "heatwave", "hot_")):
        threshold = "strictly greater than the empirical Type 7 P90 threshold"
    if lower.startswith("gleam43a_") and any(token in lower for token in ("p10", "q10")):
        threshold = "strictly below the empirical Type 7 P10 threshold"
    elif lower.startswith("gleam43a_") and any(token in lower for token in ("p20", "q20", "dryness")):
        threshold = "strictly below the empirical Type 7 P20 threshold"
    if lower.startswith("era5u8_"):
        calendar = "Beijing civil day (UTC+8), clipped to the closed phenological window"
    if lower.startswith("chm_spei_"):
        if any(token in lower for token in ("k10", "k15", "event", "run")):
            threshold = "SPEI K=-1 primary threshold or K=-1.5 strict threshold, as encoded in the variable name"
        calendar = "native CHM monthly or 2-week product support allocated by actual overlap"
    if lower.startswith("compound_"):
        soil_threshold = "P10" if any(token in lower for token in ("p10", "sm10")) else "P20"
        threshold = f"strict Tmax>P90 and soil moisture<{soil_threshold} overlap"
    if "heatwave" in lower or "_hw_p90_" in lower:
        minimum = "3 consecutive valid days"
        gap = "missing days interrupt runs; no gap merge"
    elif lower.startswith("compound_") and "hot_p10" in lower:
        minimum = "5 consecutive valid days"
        gap = (
            "merge interruptions of at most 2 days"
            if "gap2" in lower
            else "missing days interrupt runs; no gap merge"
        )
        calendar = "daily ERA5 UTC+8 and GLEAM overlap, clipped to the closed phenological window"
    elif lower.startswith("gleam43a_") and "_fd_" in lower:
        minimum = "4 consecutive pentads" if "_fd_strict_" in lower else "3 consecutive pentads"
        gap = "pentads must be consecutive"
        recovery = (
            "ends after 2 consecutive pentads at or above P20"
            if "_fd_strict_" in lower
            else "ends at the first pentad at or above P20"
        )
        threshold = "most recent q>40 start; q<20 within 5 pentads; mean decline at least 5 percentile points per pentad"
        calendar = "fixed 73 calendar pentads; February 29 excluded from pentad construction"
    elif lower.startswith("gleam43a_") and any(
        token in lower for token in ("p10_event", "daily_p10")
    ):
        minimum = "5 consecutive valid days for daily P10 events"
        gap = (
            "merge interruptions of at most 2 days"
            if "gap2" in lower
            else "missing days interrupt runs; no gap merge"
        )
        calendar = "daily GLEAM sequence; February 29 retained"
    elif lower.startswith("chm_spei_") and any(
        token in lower for token in ("k10", "k15", "event", "run")
    ):
        minimum = "3 consecutive native months" if "strict" in lower else "1 native month"
        gap = "native periods must be consecutive"
    if any(token in lower for token in ("strict", "sensitivity", "gap2", "k15", "p10_overlap")):
        status = "sensitivity"
    if any(token in lower for token in ("audit", "coverage", "valid_days", "censored")):
        status = "quality_or_audit"
    return {
        "threshold_rule": threshold,
        "minimum_duration": minimum,
        "gap_rule": gap,
        "recovery_rule": recovery,
        "calendar_rule": calendar,
        "censor_rule": censor,
        "confirmatory_status": status,
    }


def generate_variable_metadata(
    columns: Iterable[str],
    *,
    overrides: Mapping[str, Mapping[str, Any]] | None = None,
    source_overrides: Mapping[str, Mapping[str, Any]] | None = None,
    gleam_layer_roles: Mapping[str, str] | None = None,
) -> dict[str, dict[str, str]]:
    """Generate complete, deterministic metadata for every canonical column."""

    names = [str(column) for column in columns]
    if len(names) != len(set(names)):
        raise ValueError("Variable metadata columns must be unique")
    override_map = overrides or {}
    unknown = sorted(set(override_map).difference(names))
    if unknown:
        raise ValueError(f"Variable metadata overrides name absent columns: {unknown}")
    output: dict[str, dict[str, str]] = {}
    for name in names:
        details: dict[str, Any] = {
            "long_name": _humanize_variable_name(name),
            "units": _infer_units(name),
            "source_product": _infer_source_product(name),
            "version": _infer_version(name),
            "reference_id": _infer_reference_id(name),
            "history_period": _infer_history_period(name),
            "time_window": _infer_time_window(name),
            "layer_role": _infer_layer_role(name, gleam_layer_roles),
            "variant_status": _infer_variant_status(name),
            "scope_id": OUTPUT_SCOPE_ID,
            "scope_status": OUTPUT_SCOPE_STATUS,
            **_infer_rules(name),
        }
        matching_source_overrides = [
            (str(prefix), dict(values))
            for prefix, values in (source_overrides or {}).items()
            if name.casefold().startswith(str(prefix).casefold())
        ]
        for _prefix, values in sorted(
            matching_source_overrides, key=lambda item: len(item[0])
        ):
            details.update(values)
        details.update(dict(override_map.get(name, {})))
        missing = [
            field
            for field in VARIABLE_METADATA_FIELDS
            if field not in details or str(details[field]).strip() == ""
        ]
        if missing:
            raise ValueError(f"Variable metadata for {name} lacks fields: {missing}")
        output[name] = {
            field: str(details[field]) for field in VARIABLE_METADATA_FIELDS
        }
    return output


@dataclass(frozen=True)
class ExportPaths:
    long_parquet: Path
    wide_parquet: Path
    netcdf: Path
    stata: Path
    alias_map: Path
    merge_do: Path
    variable_dictionary_csv: Path
    variable_dictionary_md: Path
    material_passport: Path
    manifest: Path

    @classmethod
    def in_directory(cls, directory: str | Path) -> "ExportPaths":
        root = Path(directory)
        return cls(
            long_parquet=root / "climate_stress_long.parquet",
            wide_parquet=root / "climate_stress_wide.parquet",
            netcdf=root / "climate_stress_cube.nc",
            stata=root / "climate_stress_merge_ready.dta",
            alias_map=root / "stata_alias_map.csv",
            merge_do=root / "merge_climate_stress.do",
            variable_dictionary_csv=root / "variable_dictionary.csv",
            variable_dictionary_md=root / "variable_dictionary.md",
            material_passport=root / "material_passport.json",
            manifest=root / "manifest.json",
        )

    def all(self) -> tuple[Path, ...]:
        return tuple(getattr(self, field) for field in self.__dataclass_fields__)


def _require_absent(path: str | Path) -> Path:
    target = Path(path)
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite existing target: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _metric_columns(frame: pd.DataFrame) -> list[str]:
    return [column for column in frame.columns if column not in LONG_KEY_COLUMNS]


def canonicalize_long_panel(
    frame: pd.DataFrame,
    *,
    years: Sequence[int] = tuple(range(2010, 2020)),
    windows: Sequence[str] = CANONICAL_WINDOWS,
    expected_rows: int | None = 1_330_800,
) -> pd.DataFrame:
    """Validate and deterministically order a canonical grid-year-window table."""

    missing = sorted(set(LONG_KEY_COLUMNS).difference(frame.columns))
    if missing:
        raise ValueError(f"Long panel is missing keys: {missing}")
    output = frame.copy()
    if output[list(LONG_KEY_COLUMNS)].isna().any().any():
        raise ValueError("Canonical long keys must not be missing")
    output["year"] = pd.to_numeric(output["year"], errors="raise").astype(np.int16)
    output["window"] = output["window"].astype(str)
    if output.duplicated(["era01_cell_id", "year", "window"]).any():
        raise ValueError("Long panel contains duplicate cell-year-window keys")
    if set(output["year"].unique()) != {int(year) for year in years}:
        raise ValueError("Long panel year support differs from the frozen target years")
    if set(output["window"].unique()) != set(windows):
        raise ValueError("Long panel window support differs from the frozen six windows")
    if expected_rows is not None and len(output) != expected_rows:
        raise ValueError(f"Expected {expected_rows:,} long rows, found {len(output):,}")

    order = {window: position for position, window in enumerate(windows)}
    output["_window_order"] = output["window"].map(order)
    output = output.sort_values(["year", "_window_order", "era01_cell_id"]).drop(
        columns="_window_order"
    )
    output = output.reset_index(drop=True)
    for column in _metric_columns(output):
        if not pd.api.types.is_numeric_dtype(output[column]):
            raise TypeError(f"Canonical climate variable must be numeric: {column}")
        if pd.api.types.is_float_dtype(output[column]):
            output[column] = pd.to_numeric(output[column], errors="coerce").astype(np.float64)
    return output


def pivot_long_to_wide(
    long_panel: pd.DataFrame,
    *,
    years: Sequence[int] = tuple(range(2010, 2020)),
    windows: Sequence[str] = CANONICAL_WINDOWS,
    expected_long_rows: int | None = 1_330_800,
    expected_wide_rows: int | None = 221_800,
) -> pd.DataFrame:
    """Pivot window rows to deterministic suffix columns at grid-year level."""

    long = canonicalize_long_panel(
        long_panel, years=years, windows=windows, expected_rows=expected_long_rows
    )
    metrics = _metric_columns(long)
    if not metrics:
        raise ValueError("Long panel contains no climate variables to pivot")

    static = long[list(WIDE_KEY_COLUMNS)].drop_duplicates()
    if static.duplicated(["era01_cell_id", "year"]).any():
        raise ValueError("Spatial identifiers are not stable within grid-year")
    static = static.sort_values(["era01_cell_id", "year"]).set_index(
        ["era01_cell_id", "year"]
    )
    parts = [static]
    emitted = set(static.columns)
    for window in windows:
        suffix = WINDOW_SUFFIXES.get(window)
        if suffix is None:
            raise ValueError(f"No frozen suffix for window: {window}")
        current = long.loc[long["window"].eq(window), ["era01_cell_id", "year", *metrics]]
        current = current.set_index(["era01_cell_id", "year"]).sort_index()
        renamed = {column: f"{column}{suffix}" for column in metrics}
        collision = emitted.intersection(renamed.values())
        if collision:
            raise ValueError(f"Window suffixes create duplicate wide columns: {sorted(collision)}")
        emitted.update(renamed.values())
        parts.append(current.rename(columns=renamed))

    wide = pd.concat(parts, axis=1, join="inner").reset_index()
    wide = wide[list(WIDE_KEY_COLUMNS) + [c for c in wide.columns if c not in WIDE_KEY_COLUMNS]]
    wide = wide.sort_values(["era01_cell_id", "year"]).reset_index(drop=True)
    if expected_wide_rows is not None and len(wide) != expected_wide_rows:
        raise ValueError(f"Expected {expected_wide_rows:,} wide rows, found {len(wide):,}")
    if wide.duplicated(["era01_cell_id", "year"]).any():
        raise AssertionError("Wide panel is not unique by cell-year")
    return wide


def write_parquet_exclusive(
    frame: pd.DataFrame,
    path: str | Path,
    *,
    compression: str = "zstd",
    row_group_size: int = 262_144,
) -> Path:
    target = _require_absent(path)
    frame.to_parquet(
        target,
        engine="pyarrow",
        compression=compression,
        index=False,
        row_group_size=row_group_size,
    )
    return target


def _static_crosswalk(long_panel: pd.DataFrame, spec: TargetGridSpec) -> pd.DataFrame:
    crosswalk = long_panel[list(SPATIAL_COLUMNS)].drop_duplicates().sort_values("era01_cell_id")
    validate_v3_crosswalk(crosswalk, expected_unique=None, spec=spec)
    return crosswalk.reset_index(drop=True)


def write_cf_netcdf(
    long_panel: pd.DataFrame,
    path: str | Path,
    *,
    years: Sequence[int] = tuple(range(2010, 2020)),
    windows: Sequence[str] = CANONICAL_WINDOWS,
    expected_rows: int | None = 1_330_800,
    spec: TargetGridSpec = TARGET_GRID,
    complevel: int = 4,
    version_id: str = "data-climate-stress-2010-2019-v1",
    variable_metadata: Mapping[str, Mapping[str, Any]] | None = None,
    global_attributes: Mapping[str, Any] | None = None,
) -> Path:
    """Write the sparse selected-cell panel as a full-grid CF NetCDF cube."""

    if not 0 <= complevel <= 9:
        raise ValueError("complevel must lie in 0..9")
    target = _require_absent(path)
    long = canonicalize_long_panel(
        long_panel, years=years, windows=windows, expected_rows=expected_rows
    )
    crosswalk = _static_crosswalk(long, spec)
    metrics = _metric_columns(long)
    metadata = generate_variable_metadata(long.columns, overrides=variable_metadata)
    year_lookup = {int(year): index for index, year in enumerate(years)}
    window_lookup = {window: index for index, window in enumerate(windows)}

    dataset = nc.Dataset(target, "w", format="NETCDF4")
    try:
        dataset.createDimension("time", len(years))
        dataset.createDimension("window", len(windows))
        dataset.createDimension("latitude", spec.nlat)
        dataset.createDimension("longitude", spec.nlon)

        time = dataset.createVariable("time", "i4", ("time",))
        time.standard_name = "time"
        time.long_name = "start of target calendar year"
        time.axis = "T"
        time.units = "days since 1970-01-01 00:00:00"
        time.calendar = "proleptic_gregorian"
        time[:] = nc.date2num(
            [datetime(int(year), 1, 1) for year in years], time.units, time.calendar
        ).astype(np.int32)
        year_variable = dataset.createVariable("year", "i2", ("time",))
        year_variable.long_name = "calendar year"
        year_variable[:] = np.asarray(years, dtype=np.int16)

        window_variable = dataset.createVariable("window", str, ("window",))
        window_variable.long_name = "phenological aggregation window"
        window_variable[:] = np.asarray(tuple(windows), dtype=object)
        latitude = dataset.createVariable("latitude", "f8", ("latitude",))
        latitude.standard_name = "latitude"
        latitude.long_name = "target grid-cell centre latitude"
        latitude.units = "degrees_north"
        latitude.axis = "Y"
        latitude[:] = spec.latitudes
        longitude = dataset.createVariable("longitude", "f8", ("longitude",))
        longitude.standard_name = "longitude"
        longitude.long_name = "target grid-cell centre longitude"
        longitude.units = "degrees_east"
        longitude.axis = "X"
        longitude[:] = spec.longitudes
        crs = dataset.createVariable("crs", "i4")
        crs.assignValue(0)
        crs.grid_mapping_name = "latitude_longitude"
        crs.epsg_code = "EPSG:4326"
        crs.semi_major_axis = 6378137.0
        crs.inverse_flattening = 298.257223563

        compression = {"zlib": True, "complevel": complevel, "shuffle": True}
        selected_mask = dataset.createVariable(
            "selected_grid_mask", "i1", ("latitude", "longitude"), **compression
        )
        selected_mask.long_name = "V3-main coordinate-union selection mask"
        selected_mask.flag_values = np.asarray([0, 1], dtype=np.int8)
        selected_mask.flag_meanings = "not_selected selected"
        mask = np.zeros((spec.nlat, spec.nlon), dtype=np.int8)
        cross_lat = crosswalk["lat_idx"].to_numpy(dtype=np.int64)
        cross_lon = crosswalk["lon_idx"].to_numpy(dtype=np.int64)
        mask[cross_lat, cross_lon] = 1
        selected_mask[:] = mask

        integer_fill = np.int32(-2_147_483_647)
        era_grid = dataset.createVariable(
            "era01_cell_id",
            "i4",
            ("latitude", "longitude"),
            fill_value=integer_fill,
            **compression,
        )
        era_grid.long_name = "stable row-major selected-cell identifier"
        v3_grid = dataset.createVariable(
            "grid_id_v3",
            "i4",
            ("latitude", "longitude"),
            fill_value=integer_fill,
            **compression,
        )
        v3_grid.long_name = "V3 panel identifier; valid only where selected_grid_mask=1"
        era_values = np.full((spec.nlat, spec.nlon), integer_fill, dtype=np.int32)
        v3_values = np.full((spec.nlat, spec.nlon), integer_fill, dtype=np.int32)
        era_values[cross_lat, cross_lon] = crosswalk["era01_cell_id"].to_numpy(dtype=np.int32)
        v3_values[cross_lat, cross_lon] = crosswalk["grid_id_v3"].to_numpy(dtype=np.int32)
        era_grid[:] = era_values
        v3_grid[:] = v3_values

        data_variables: dict[str, nc.Variable] = {}
        chunks = (1, 1, min(64, spec.nlat), min(64, spec.nlon))
        for metric in metrics:
            variable = dataset.createVariable(
                metric,
                "f8",
                ("time", "window", "latitude", "longitude"),
                fill_value=np.nan,
                chunksizes=chunks,
                **compression,
            )
            details = metadata.get(metric, {})
            variable.long_name = str(details.get("long_name", metric))
            variable.units = str(details.get("units", "1"))
            variable.source_product = str(details.get("source_product", "documented in manifest"))
            variable.source_version = str(details["version"])
            variable.reference_id = str(details["reference_id"])
            variable.history_period = str(details.get("history_period", "not_applicable_or_manifest"))
            variable.time_window = str(details["time_window"])
            variable.layer_role = str(details["layer_role"])
            variable.variant_status = str(details["variant_status"])
            variable.output_scope_id = str(details["scope_id"])
            variable.output_scope_status = str(details["scope_status"])
            variable.threshold_rule = str(details["threshold_rule"])
            variable.minimum_duration = str(details["minimum_duration"])
            variable.gap_rule = str(details["gap_rule"])
            variable.recovery_rule = str(details["recovery_rule"])
            variable.calendar_rule = str(details["calendar_rule"])
            variable.censor_rule = str(details["censor_rule"])
            variable.confirmatory_status = str(details["confirmatory_status"])
            variable.coordinates = "time window latitude longitude"
            variable.grid_mapping = "crs"
            data_variables[metric] = variable

        for (raw_year, window), group in long.groupby(["year", "window"], sort=False):
            time_index = year_lookup[int(raw_year)]
            window_index = window_lookup[str(window)]
            lat_idx = group["lat_idx"].to_numpy(dtype=np.int64)
            lon_idx = group["lon_idx"].to_numpy(dtype=np.int64)
            for metric in metrics:
                layer = np.full((spec.nlat, spec.nlon), np.nan, dtype=np.float64)
                layer[lat_idx, lon_idx] = pd.to_numeric(group[metric], errors="coerce").to_numpy(
                    dtype=np.float64
                )
                data_variables[metric][time_index, window_index, :, :] = layer

        dataset.Conventions = "CF-1.10"
        dataset.title = "China maize climate and soil-moisture stress panel"
        dataset.summary = "Six phenological windows on the selected 0.1 degree V3-main grid union"
        dataset.version_id = version_id
        dataset.output_scope_id = OUTPUT_SCOPE_ID
        dataset.output_scope_status = OUTPUT_SCOPE_STATUS
        dataset.time_coverage_start = f"{min(years):04d}-01-01"
        dataset.time_coverage_end = f"{max(years):04d}-12-31"
        dataset.geospatial_lat_min = float(spec.south)
        dataset.geospatial_lat_max = float(spec.north)
        dataset.geospatial_lon_min = float(spec.west)
        dataset.geospatial_lon_max = float(spec.east)
        dataset.geospatial_lat_resolution = float(spec.step)
        dataset.geospatial_lon_resolution = float(spec.step)
        for name, value in (global_attributes or {}).items():
            dataset.setncattr(name, value)
    finally:
        dataset.close()
    return target


def parquet_partition_files(path: str | Path) -> tuple[Path, ...]:
    """Return deterministic, visible Parquet files from a file or dataset."""

    source = Path(path)
    files = (source,) if source.is_file() else tuple(sorted(source.rglob("*.parquet")))
    visible = tuple(item for item in files if not item.name.startswith("."))
    if not visible:
        raise ValueError(f"No Parquet partitions found: {source}")
    return visible


def inspect_partitioned_long_panel(
    partition_source: str | Path,
    *,
    years: Sequence[int],
    windows: Sequence[str],
    expected_rows: int | None,
    expected_cells: int | None,
) -> dict[str, Any]:
    """Validate canonical keys and schema without reading all climate values."""

    import pyarrow as pa
    import pyarrow.parquet as pq

    files = parquet_partition_files(partition_source)
    schemas = [pq.ParquetFile(path).schema_arrow.remove_metadata() for path in files]
    reference = schemas[0]
    for path, schema in zip(files[1:], schemas[1:]):
        if not reference.equals(schema, check_metadata=False):
            raise ValueError(f"Canonical long partition schema differs: {path}")
    missing = sorted(set(LONG_KEY_COLUMNS).difference(reference.names))
    if missing:
        raise ValueError(f"Canonical long partitions lack keys: {missing}")
    metrics = [name for name in reference.names if name not in LONG_KEY_COLUMNS]
    if not metrics:
        raise ValueError("Canonical long partitions contain no climate metrics")
    for name in metrics:
        field = reference.field(name)
        if not (
            pa.types.is_integer(field.type)
            or pa.types.is_floating(field.type)
            or pa.types.is_boolean(field.type)
        ):
            raise TypeError(f"Canonical climate variable must be numeric: {name}")

    target_years = {int(value) for value in years}
    target_windows = {str(value) for value in windows}
    seen_cells: set[int] = set()
    rows = 0
    max_rows = 0
    for path in files:
        parquet = pq.ParquetFile(path)
        current_rows = int(parquet.metadata.num_rows)
        keys = pd.read_parquet(path, columns=list(LONG_KEY_COLUMNS))
        if len(keys) != current_rows:
            raise AssertionError("Parquet footer and decoded key row counts differ")
        if keys[list(LONG_KEY_COLUMNS)].isna().any().any():
            raise ValueError(f"Canonical long partition has missing keys: {path}")
        if keys.duplicated(["era01_cell_id", "year", "window"]).any():
            raise ValueError(f"Canonical long partition has duplicate keys: {path}")
        observed_years = set(pd.to_numeric(keys["year"], errors="raise").astype(int))
        observed_windows = set(keys["window"].astype(str))
        if observed_years != target_years or observed_windows != target_windows:
            raise ValueError(f"Canonical long partition support differs: {path}")
        cells = set(
            pd.to_numeric(keys["era01_cell_id"], errors="raise")
            .astype(np.int64)
            .unique()
            .tolist()
        )
        if seen_cells.intersection(cells):
            raise ValueError("Canonical long spatial partitions overlap")
        expected_partition_rows = len(cells) * len(years) * len(windows)
        if current_rows != expected_partition_rows:
            raise ValueError(
                f"Canonical long partition has {current_rows:,} rows; expected "
                f"{expected_partition_rows:,}"
            )
        seen_cells.update(cells)
        rows += current_rows
        max_rows = max(max_rows, current_rows)
    if expected_rows is not None and rows != int(expected_rows):
        raise ValueError(f"Expected {expected_rows:,} long rows, found {rows:,}")
    if expected_cells is not None and len(seen_cells) != int(expected_cells):
        raise ValueError(
            f"Expected {expected_cells:,} selected cells, found {len(seen_cells):,}"
        )
    return {
        "files": files,
        "schema": reference,
        "columns": tuple(reference.names),
        "metrics": tuple(metrics),
        "rows": rows,
        "selected_cells": len(seen_cells),
        "max_partition_rows": max_rows,
    }


def write_cf_netcdf_from_partitions(
    partition_source: str | Path,
    crosswalk: pd.DataFrame,
    path: str | Path,
    *,
    years: Sequence[int],
    windows: Sequence[str],
    expected_rows: int,
    spec: TargetGridSpec = TARGET_GRID,
    complevel: int = 4,
    version_id: str = "data-climate-stress-2010-2019-v1",
    variable_metadata: Mapping[str, Mapping[str, Any]] | None = None,
    global_attributes: Mapping[str, Any] | None = None,
) -> Path:
    """Write CF NetCDF while holding at most one spatial Parquet block."""

    if not 0 <= complevel <= 9:
        raise ValueError("complevel must lie in 0..9")
    target = _require_absent(path)
    contract = inspect_partitioned_long_panel(
        partition_source,
        years=years,
        windows=windows,
        expected_rows=expected_rows,
        expected_cells=len(crosswalk),
    )
    ordered_crosswalk = (
        crosswalk[list(SPATIAL_COLUMNS)]
        .drop_duplicates()
        .sort_values("era01_cell_id")
        .reset_index(drop=True)
    )
    validate_v3_crosswalk(ordered_crosswalk, expected_unique=None, spec=spec)
    metrics = list(contract["metrics"])
    metadata = generate_variable_metadata(contract["columns"], overrides=variable_metadata)
    year_lookup = {int(year): index for index, year in enumerate(years)}
    window_lookup = {str(window): index for index, window in enumerate(windows)}

    dataset = nc.Dataset(target, "w", format="NETCDF4")
    try:
        dataset.createDimension("time", len(years))
        dataset.createDimension("window", len(windows))
        dataset.createDimension("latitude", spec.nlat)
        dataset.createDimension("longitude", spec.nlon)
        time = dataset.createVariable("time", "i4", ("time",))
        time.standard_name = "time"
        time.long_name = "start of target calendar year"
        time.axis = "T"
        time.units = "days since 1970-01-01 00:00:00"
        time.calendar = "proleptic_gregorian"
        time[:] = nc.date2num(
            [datetime(int(year), 1, 1) for year in years], time.units, time.calendar
        ).astype(np.int32)
        year_variable = dataset.createVariable("year", "i2", ("time",))
        year_variable.long_name = "calendar year"
        year_variable[:] = np.asarray(years, dtype=np.int16)
        window_variable = dataset.createVariable("window", str, ("window",))
        window_variable.long_name = "phenological aggregation window"
        window_variable[:] = np.asarray(tuple(windows), dtype=object)
        latitude = dataset.createVariable("latitude", "f8", ("latitude",))
        latitude.standard_name = "latitude"
        latitude.long_name = "target grid-cell centre latitude"
        latitude.units = "degrees_north"
        latitude.axis = "Y"
        latitude[:] = spec.latitudes
        longitude = dataset.createVariable("longitude", "f8", ("longitude",))
        longitude.standard_name = "longitude"
        longitude.long_name = "target grid-cell centre longitude"
        longitude.units = "degrees_east"
        longitude.axis = "X"
        longitude[:] = spec.longitudes
        crs = dataset.createVariable("crs", "i4")
        crs.assignValue(0)
        crs.grid_mapping_name = "latitude_longitude"
        crs.epsg_code = "EPSG:4326"
        crs.semi_major_axis = 6378137.0
        crs.inverse_flattening = 298.257223563

        compression = {"zlib": True, "complevel": complevel, "shuffle": True}
        selected_mask = dataset.createVariable(
            "selected_grid_mask", "i1", ("latitude", "longitude"), **compression
        )
        selected_mask.long_name = "V3-main coordinate-union selection mask"
        selected_mask.flag_values = np.asarray([0, 1], dtype=np.int8)
        selected_mask.flag_meanings = "not_selected selected"
        cross_lat = ordered_crosswalk["lat_idx"].to_numpy(dtype=np.int64)
        cross_lon = ordered_crosswalk["lon_idx"].to_numpy(dtype=np.int64)
        mask = np.zeros((spec.nlat, spec.nlon), dtype=np.int8)
        mask[cross_lat, cross_lon] = 1
        selected_mask[:] = mask

        integer_fill = np.int32(-2_147_483_647)
        era_grid = dataset.createVariable(
            "era01_cell_id", "i4", ("latitude", "longitude"),
            fill_value=integer_fill, **compression
        )
        era_grid.long_name = "stable row-major selected-cell identifier"
        v3_grid = dataset.createVariable(
            "grid_id_v3", "i4", ("latitude", "longitude"),
            fill_value=integer_fill, **compression
        )
        v3_grid.long_name = "V3 panel identifier; valid only where selected_grid_mask=1"
        era_values = np.full((spec.nlat, spec.nlon), integer_fill, dtype=np.int32)
        v3_values = np.full((spec.nlat, spec.nlon), integer_fill, dtype=np.int32)
        era_values[cross_lat, cross_lon] = ordered_crosswalk["era01_cell_id"].to_numpy(
            dtype=np.int32
        )
        v3_values[cross_lat, cross_lon] = ordered_crosswalk["grid_id_v3"].to_numpy(
            dtype=np.int32
        )
        era_grid[:] = era_values
        v3_grid[:] = v3_values

        data_variables: dict[str, nc.Variable] = {}
        chunks = (1, 1, min(64, spec.nlat), min(64, spec.nlon))
        for metric in metrics:
            variable = dataset.createVariable(
                metric, "f8", ("time", "window", "latitude", "longitude"),
                fill_value=np.nan, chunksizes=chunks, **compression
            )
            details = metadata[metric]
            variable.long_name = details["long_name"]
            variable.units = details["units"]
            variable.source_product = details["source_product"]
            variable.source_version = details["version"]
            variable.reference_id = details["reference_id"]
            variable.history_period = details["history_period"]
            variable.time_window = details["time_window"]
            variable.layer_role = details["layer_role"]
            variable.variant_status = details["variant_status"]
            variable.output_scope_id = details["scope_id"]
            variable.output_scope_status = details["scope_status"]
            variable.threshold_rule = details["threshold_rule"]
            variable.minimum_duration = details["minimum_duration"]
            variable.gap_rule = details["gap_rule"]
            variable.recovery_rule = details["recovery_rule"]
            variable.calendar_rule = details["calendar_rule"]
            variable.censor_rule = details["censor_rule"]
            variable.confirmatory_status = details["confirmatory_status"]
            variable.coordinates = "time window latitude longitude"
            variable.grid_mapping = "crs"
            data_variables[metric] = variable

        for partition in contract["files"]:
            frame = pd.read_parquet(partition)
            if len(frame) > int(contract["max_partition_rows"]):
                raise AssertionError("Decoded Parquet block exceeds inspected contract")
            for (raw_year, raw_window), group in frame.groupby(
                ["year", "window"], sort=False, observed=True
            ):
                time_index = year_lookup[int(raw_year)]
                window_index = window_lookup[str(raw_window)]
                for lat_index, latitude_group in group.groupby("lat_idx", sort=False):
                    lon_indices = latitude_group["lon_idx"].to_numpy(dtype=np.int64)
                    for metric in metrics:
                        values = pd.to_numeric(
                            latitude_group[metric], errors="coerce"
                        ).to_numpy(dtype=np.float64)
                        data_variables[metric][
                            time_index, window_index, int(lat_index), lon_indices
                        ] = values

        dataset.Conventions = "CF-1.10"
        dataset.title = "China maize climate and soil-moisture stress panel"
        dataset.summary = "Six phenological windows on the selected 0.1 degree V3-main grid union"
        dataset.version_id = version_id
        dataset.output_scope_id = OUTPUT_SCOPE_ID
        dataset.output_scope_status = OUTPUT_SCOPE_STATUS
        dataset.time_coverage_start = f"{min(years):04d}-01-01"
        dataset.time_coverage_end = f"{max(years):04d}-12-31"
        dataset.geospatial_lat_min = float(spec.south)
        dataset.geospatial_lat_max = float(spec.north)
        dataset.geospatial_lon_min = float(spec.west)
        dataset.geospatial_lon_max = float(spec.east)
        dataset.geospatial_lat_resolution = float(spec.step)
        dataset.geospatial_lon_resolution = float(spec.step)
        for name, value in (global_attributes or {}).items():
            dataset.setncattr(name, value)
    finally:
        dataset.close()
    return target


def _sanitize_stata_name(name: str) -> str:
    candidate = re.sub(r"[^A-Za-z0-9_]", "_", name)
    candidate = re.sub(r"_+", "_", candidate).strip("_")
    if not candidate or candidate[0].isdigit():
        candidate = f"v_{candidate}"
    return candidate


def _hashed_stata_name(name: str) -> str:
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]
    stem = _sanitize_stata_name(name).lower()
    return f"{stem[:23]}_{digest}"[:32]


def build_stata_alias_map(columns: Iterable[str]) -> pd.DataFrame:
    """Create order-independent, case-insensitively unique Stata aliases."""

    originals = [str(column) for column in columns]
    if len(set(originals)) != len(originals):
        raise ValueError("Input columns must be unique")
    provisional: dict[str, str] = {}
    methods: dict[str, str] = {}
    for original in originals:
        if STATA_NAME.fullmatch(original):
            provisional[original] = original
            methods[original] = "identity"
        else:
            provisional[original] = _hashed_stata_name(original)
            methods[original] = "sha256"

    groups: dict[str, list[str]] = {}
    for original, alias in provisional.items():
        groups.setdefault(alias.casefold(), []).append(original)
    for members in groups.values():
        if len(members) <= 1:
            continue
        protected = [member for member in members if member in STATA_PUBLIC_KEYS]
        if len(protected) > 1:
            raise ValueError(f"Public Stata key collision: {protected}")
        for member in members:
            if member not in protected:
                provisional[member] = _hashed_stata_name(member)
                methods[member] = "collision_sha256"

    aliases = [provisional[original] for original in originals]
    if any(not STATA_NAME.fullmatch(alias) for alias in aliases):
        raise AssertionError("Generated invalid Stata alias")
    if len({alias.casefold() for alias in aliases}) != len(aliases):
        raise ValueError("Unable to resolve a deterministic Stata alias collision")
    return pd.DataFrame(
        {
            "original_name": originals,
            "stata_name": aliases,
            "changed": [int(original != alias) for original, alias in zip(originals, aliases)],
            "alias_method": [methods[original] for original in originals],
            "original_length": [len(original) for original in originals],
            "stata_length": [len(alias) for alias in aliases],
            "name_sha256": [hashlib.sha256(original.encode("utf-8")).hexdigest() for original in originals],
        }
    )


def _stata_ready(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    for column in output.columns:
        series = output[column]
        if pd.api.types.is_bool_dtype(series.dtype):
            output[column] = series.astype(np.int8) if not series.isna().any() else series.astype(float)
        elif pd.api.types.is_integer_dtype(series.dtype) and series.isna().any():
            output[column] = series.astype(np.float64)
        elif pd.api.types.is_float_dtype(series.dtype):
            output[column] = pd.to_numeric(series, errors="coerce").astype(np.float64)
    return output


def write_stata_merge_script(path: str | Path) -> Path:
    target = _require_absent(path)
    script = """version 18.0
clear all
set more off

args master_panel climate_panel output_panel
if `\"`master_panel'\"' == \"\" | `\"`climate_panel'\"' == \"\" | `\"`output_panel'\"' == \"\" {
    display as error \"Usage: do merge_climate_stress.do master_panel climate_panel output_panel\"
    exit 198
}

capture confirm file `\"`output_panel'\"'
if !_rc {
    display as error \"Refusing to overwrite existing output: `output_panel'\"
    exit 602
}

use `\"`master_panel'\"', clear
capture confirm variable lat10
if _rc generate int lat10 = round(latitude * 10)
capture confirm variable lon10
if _rc generate int lon10 = round(longitude * 10)
isid lat10 lon10 year
merge 1:1 lat10 lon10 year using `\"`climate_panel'\"', keep(master match)
assert _merge == 3
drop _merge
isid lat10 lon10 year
save `\"`output_panel'\"'
"""
    target.write_text(script, encoding="utf-8", newline="\n")
    return target


def write_stata_bundle(
    wide_panel: pd.DataFrame,
    dta_path: str | Path,
    alias_map_path: str | Path,
    merge_do_path: str | Path,
    *,
    expected_rows: int | None = 221_800,
) -> tuple[Path, Path, Path, pd.DataFrame]:
    if expected_rows is not None and len(wide_panel) != expected_rows:
        raise ValueError(f"Expected {expected_rows:,} Stata rows, found {len(wide_panel):,}")
    if wide_panel.duplicated(["lat10", "lon10", "year"]).any():
        raise ValueError("Stata merge table must be unique by lat10 lon10 year")
    dta_target = _require_absent(dta_path)
    alias_target = _require_absent(alias_map_path)
    do_target = _require_absent(merge_do_path)
    aliases = build_stata_alias_map(wide_panel.columns)
    rename = aliases.set_index("original_name")["stata_name"].to_dict()
    stata = _stata_ready(wide_panel.rename(columns=rename))
    variable_labels = {
        row.stata_name: row.original_name[:80]
        for row in aliases.itertuples()
        if row.changed
    }
    stata.to_stata(
        dta_target,
        write_index=False,
        version=118,
        variable_labels=variable_labels,
        # Stata headers otherwise embed the wall-clock write time, which makes
        # byte-identical reruns impossible even when every data value matches.
        time_stamp=datetime(2000, 1, 1, 0, 0, 0),
    )
    aliases.to_csv(alias_target, index=False, encoding="utf-8-sig")
    write_stata_merge_script(do_target)
    return dta_target, alias_target, do_target, aliases


def _unique_partial_path(target: Path) -> Path:
    while True:
        candidate = target.with_name(f".{target.name}.{uuid.uuid4().hex}.partial")
        if not candidate.exists():
            return candidate


class _PartitionedStataWriter:
    """Adapter around pandas' release-118 writer with chunked data records."""

    def __init__(
        self,
        target: Path,
        template: pd.DataFrame,
        partition_paths: Sequence[Path],
        rename: Mapping[str, str],
        *,
        nobs: int,
        variable_labels: Mapping[str, str],
    ) -> None:
        from pandas.io.stata import StataWriter117, StataWriterUTF8

        outer = self

        class Writer(StataWriterUTF8):
            def __init__(self) -> None:
                super().__init__(
                    target,
                    template,
                    write_index=False,
                    version=118,
                    variable_labels=dict(variable_labels),
                    time_stamp=datetime(2000, 1, 1, 0, 0, 0),
                )
                self.nobs = int(nobs)
                empty = StataWriter117._prepare_data(self)
                self._record_dtypes = {
                    name: empty.dtype.fields[name][0] for name in self.varlist
                }

            def _prepare_data(self) -> None:
                return None

            def _write_data(self, _records: object) -> None:
                from pandas.io.stata import _cast_to_stata_types

                self._update_map("data")
                self._write_bytes(b"<data>")
                rows = 0
                for path in partition_paths:
                    frame = pd.read_parquet(path).rename(columns=dict(rename))
                    if list(frame.columns) != list(self.varlist):
                        raise ValueError(f"Wide partition schema/order differs: {path}")
                    frame = _cast_to_stata_types(_stata_ready(frame))
                    frame = self._replace_nans(frame)
                    records = frame.to_records(
                        index=False, column_dtypes=self._record_dtypes
                    )
                    self._write_bytes(records.tobytes())
                    rows += len(frame)
                if rows != self.nobs:
                    raise ValueError(
                        f"Chunked Stata writer saw {rows:,} rows; expected {self.nobs:,}"
                    )
                self._write_bytes(b"</data>")

            def write_file(self) -> None:
                """Write without deleting a failed partial artifact."""

                from pandas.io.common import get_handle

                with get_handle(
                    self._fname,
                    "wb",
                    compression=self._compression,
                    is_text=False,
                    storage_options=self.storage_options,
                ) as self.handles:
                    if self.handles.compression["method"] is not None:
                        self._output_file, self.handles.handle = (
                            self.handles.handle,
                            BytesIO(),
                        )
                        self.handles.created_handles.append(self.handles.handle)
                    try:
                        self._write_header(
                            data_label=self._data_label,
                            time_stamp=self._time_stamp,
                        )
                        self._write_map()
                        self._write_variable_types()
                        self._write_varnames()
                        self._write_sortlist()
                        self._write_formats()
                        self._write_value_label_names()
                        self._write_variable_labels()
                        self._write_expansion_fields()
                        self._write_characteristics()
                        self._write_data(None)
                        self._write_strls()
                        self._write_value_labels()
                        self._write_file_close_tag()
                        self._write_map()
                        self._close()
                    except BaseException:
                        self.handles.close()
                        raise

        outer.writer = Writer()

    def write_file(self) -> None:
        self.writer.write_file()


def write_stata_bundle_from_partitions(
    wide_partition_source: str | Path,
    dta_path: str | Path,
    alias_map_path: str | Path,
    merge_do_path: str | Path,
    *,
    expected_rows: int,
) -> tuple[Path, Path, Path, pd.DataFrame, dict[str, int]]:
    """Write one DTA while retaining at most one wide spatial block."""

    import pyarrow.parquet as pq

    partitions = parquet_partition_files(wide_partition_source)
    schemas = [pq.ParquetFile(path).schema_arrow.remove_metadata() for path in partitions]
    reference = schemas[0]
    for path, schema in zip(partitions[1:], schemas[1:]):
        if not reference.equals(schema, check_metadata=False):
            raise ValueError(f"Wide partition schema differs: {path}")
    rows = sum(int(pq.ParquetFile(path).metadata.num_rows) for path in partitions)
    if rows != int(expected_rows):
        raise ValueError(f"Expected {expected_rows:,} Stata rows, found {rows:,}")
    dta_target = _require_absent(dta_path)
    alias_target = _require_absent(alias_map_path)
    do_target = _require_absent(merge_do_path)
    aliases = build_stata_alias_map(reference.names)
    rename = aliases.set_index("original_name")["stata_name"].to_dict()
    first = pd.read_parquet(partitions[0]).rename(columns=rename)
    template = _stata_ready(first.iloc[0:0].copy())
    variable_labels = {
        row.stata_name: row.original_name[:80]
        for row in aliases.itertuples()
        if row.changed
    }
    partial = _unique_partial_path(dta_target)
    writer = _PartitionedStataWriter(
        partial,
        template,
        partitions,
        rename,
        nobs=rows,
        variable_labels=variable_labels,
    )
    writer.write_file()
    if dta_target.exists():
        raise FileExistsError(dta_target)
    os.rename(partial, dta_target)
    aliases.to_csv(alias_target, index=False, encoding="utf-8-sig")
    write_stata_merge_script(do_target)
    return (
        dta_target,
        alias_target,
        do_target,
        aliases,
        {
            "rows": rows,
            "partitions": len(partitions),
            "max_partition_rows": max(
                int(pq.ParquetFile(path).metadata.num_rows) for path in partitions
            ),
        },
    )


def build_variable_dictionary(
    long_panel: pd.DataFrame,
    *,
    variable_metadata: Mapping[str, Mapping[str, Any]] | None = None,
) -> pd.DataFrame:
    metadata = generate_variable_metadata(long_panel.columns, overrides=variable_metadata)
    rows: list[dict[str, Any]] = []
    for column in long_panel.columns:
        details = metadata.get(column, {})
        rows.append(
            {
                "variable": column,
                "dtype": str(long_panel[column].dtype),
                "role": "key" if column in LONG_KEY_COLUMNS else "climate_measure",
                "unit": details["units"],
                "description": details["long_name"],
                "source_product": details["source_product"],
                "version": details["version"],
                "reference_id": details["reference_id"],
                "history_period": details["history_period"],
                "time_window": details["time_window"],
                "layer_role": details["layer_role"],
                "variant_status": details["variant_status"],
                "scope_id": details["scope_id"],
                "scope_status": details["scope_status"],
                "threshold_rule": details["threshold_rule"],
                "minimum_duration": details["minimum_duration"],
                "gap_rule": details["gap_rule"],
                "recovery_rule": details["recovery_rule"],
                "calendar_rule": details["calendar_rule"],
                "censor_rule": details["censor_rule"],
                "confirmatory_status": details["confirmatory_status"],
            }
        )
    return pd.DataFrame(rows)


def write_variable_dictionary(
    dictionary: pd.DataFrame, csv_path: str | Path, markdown_path: str | Path
) -> tuple[Path, Path]:
    csv_target = _require_absent(csv_path)
    markdown_target = _require_absent(markdown_path)
    dictionary.to_csv(csv_target, index=False, encoding="utf-8-sig")
    columns = [str(column) for column in dictionary.columns]

    def markdown_cell(value: Any) -> str:
        if pd.isna(value):
            return ""
        return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")

    lines = [
        "# Climate-stress variable dictionary",
        "",
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    lines.extend(
        "| " + " | ".join(markdown_cell(value) for value in row) + " |"
        for row in dictionary.itertuples(index=False, name=None)
    )
    lines.append("")
    markdown_target.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return csv_target, markdown_target


def sha256_file(path: str | Path, *, block_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(block_size), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_dataframe(frame: pd.DataFrame) -> str:
    digest = hashlib.sha256()
    digest.update(
        json.dumps(
            [(column, str(frame[column].dtype)) for column in frame.columns],
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    digest.update(pd.util.hash_pandas_object(frame, index=True, categorize=True).values.tobytes())
    return digest.hexdigest()


def sha256_path(path: str | Path) -> str:
    """Hash a file or directory tree using stable relative names and file hashes."""

    source = Path(path)
    if source.is_file():
        return sha256_file(source)
    if not source.is_dir():
        raise FileNotFoundError(source)
    digest = hashlib.sha256()
    for item in sorted(candidate for candidate in source.rglob("*") if candidate.is_file()):
        relative = item.relative_to(source).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(bytes.fromhex(sha256_file(item)))
    return digest.hexdigest()


def _path_record(
    path: str | Path,
    *,
    recorded_path: str | Path | None = None,
) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file() and not source.is_dir():
        raise FileNotFoundError(source)
    if source.is_file():
        size = source.stat().st_size
        file_count = 1
        kind = "file"
    else:
        files = [candidate for candidate in source.rglob("*") if candidate.is_file()]
        size = sum(candidate.stat().st_size for candidate in files)
        file_count = len(files)
        kind = "directory"
    return {
        "path": (
            str(source.resolve())
            if recorded_path is None
            else Path(recorded_path).as_posix()
        ),
        "kind": kind,
        "bytes": size,
        "file_count": file_count,
        "sha256": sha256_path(source),
    }


def build_file_records(
    paths: Mapping[str, str | Path],
    *,
    recorded_paths: Mapping[str, str | Path] | None = None,
) -> dict[str, dict[str, Any]]:
    """Hash a named file collection and optionally record stable published paths."""

    if recorded_paths is not None and set(recorded_paths) != set(paths):
        raise ValueError("recorded_paths must have exactly the path keys")
    return {
        name: _path_record(
            path,
            recorded_path=None if recorded_paths is None else recorded_paths[name],
        )
        for name, path in sorted(paths.items())
    }


def _validate_precomputed_records(
    records: Mapping[str, Mapping[str, Any]],
    *,
    label: str,
) -> dict[str, dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}
    for raw_name, raw_record in sorted(records.items()):
        name = str(raw_name)
        record = dict(raw_record)
        missing = sorted({"path", "bytes", "sha256"}.difference(record))
        if missing:
            raise ValueError(f"{label} record {name} lacks fields: {missing}")
        digest = str(record["sha256"]).casefold()
        if not SHA256_PATTERN.fullmatch(digest):
            raise ValueError(f"{label} record {name} has an invalid SHA-256")
        size = int(record["bytes"])
        if size < 0:
            raise ValueError(f"{label} record {name} has negative bytes")
        record["path"] = str(record["path"])
        record["bytes"] = size
        record["sha256"] = digest
        normalized[name] = record
    return normalized


def manifest_input_records_from_inventory(
    inventory_path: str | Path,
    *,
    require_full_hash: bool = True,
) -> dict[str, dict[str, Any]]:
    """Convert the validated source inventory into manifest-ready raw-input records."""

    source = Path(inventory_path)
    if source.suffix.casefold() == ".parquet":
        inventory = pd.read_parquet(source)
    else:
        payload = json.loads(source.read_text(encoding="utf-8"))
        inventory = pd.DataFrame(payload.get("records", []))
    required = {
        "asset_id",
        "family",
        "role",
        "path",
        "exists",
        "size_bytes",
        "sha256",
        "hash_algorithm",
        "hash_is_full",
    }
    missing = sorted(required.difference(inventory.columns))
    if missing:
        raise ValueError(f"Source inventory lacks manifest fields: {missing}")
    if inventory.empty:
        raise ValueError("Source inventory is empty")
    if inventory["asset_id"].astype(str).duplicated().any():
        raise ValueError("Source inventory asset_id values are not unique")
    if not inventory["exists"].astype(bool).all():
        absent = inventory.loc[~inventory["exists"].astype(bool), "asset_id"].astype(str).tolist()
        raise ValueError(f"Source inventory contains missing raw inputs: {absent}")
    if require_full_hash and not inventory["hash_is_full"].astype(bool).all():
        partial = inventory.loc[
            ~inventory["hash_is_full"].astype(bool), "asset_id"
        ].astype(str).tolist()
        raise ValueError(f"Full run requires full raw-input hashes: {partial}")
    records: dict[str, dict[str, Any]] = {}
    optional = ("year", "layer", "variable", "mtime_utc", "timestamp_semantics")
    for row in inventory.sort_values("asset_id").to_dict(orient="records"):
        record: dict[str, Any] = {
            "path": str(row["path"]),
            "bytes": int(row["size_bytes"]),
            "sha256": str(row["sha256"]),
            "hash_algorithm": str(row["hash_algorithm"]),
            "hash_is_full": bool(row["hash_is_full"]),
            "family": str(row["family"]),
            "role": str(row["role"]),
        }
        for field in optional:
            value = row.get(field)
            if value is not None and not (isinstance(value, float) and math.isnan(value)):
                record[field] = value
        records[str(row["asset_id"])] = record
    return _validate_precomputed_records(records, label="raw input")


def build_material_passport(
    long_panel: pd.DataFrame,
    *,
    version_id: str,
    sources: Mapping[str, Any],
    transformations: Mapping[str, Any] | None = None,
    quality: Mapping[str, Any] | None = None,
    exclusions: Sequence[str] | None = None,
    spec: TargetGridSpec = TARGET_GRID,
) -> dict[str, Any]:
    return {
        "material_passport_version": "1.0",
        "artifact_id": version_id,
        "entity": "selected 0.1-degree grid x calendar year x phenological window",
        "primary_keys": list(LONG_KEY_COLUMNS),
        "rows": int(len(long_panel)),
        "selected_cells": int(long_panel["era01_cell_id"].nunique()),
        "years": sorted(int(value) for value in long_panel["year"].unique()),
        "windows": list(CANONICAL_WINDOWS),
        "grid": {
            "crs": spec.crs,
            "shape": [spec.nlat, spec.nlon],
            "resolution_degrees": spec.step,
            "latitude_centres": [spec.north, spec.south],
            "longitude_centres": [spec.west, spec.east],
            "stable_id_formula": "lat_idx * 616 + lon_idx + 1",
        },
        "sources": dict(sources),
        "transformations": dict(transformations or {}),
        "quality": dict(quality or {}),
        "excluded_manual_families": list(exclusions or []),
        "dataframe_sha256": sha256_dataframe(long_panel),
    }


def write_json_exclusive(value: Mapping[str, Any], path: str | Path) -> Path:
    target = _require_absent(path)
    target.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, default=str) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return target


def build_manifest(
    *,
    version_id: str,
    config_path: str | Path,
    outputs: Mapping[str, str | Path],
    inputs: Mapping[str, str | Path] | None = None,
    input_records: Mapping[str, Mapping[str, Any]] | None = None,
    output_record_paths: Mapping[str, str | Path] | None = None,
    audit_artifacts: Mapping[str, str | Path] | None = None,
    audit_record_paths: Mapping[str, str | Path] | None = None,
    config_sha256: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    config = Path(config_path)
    if (inputs is None) == (input_records is None):
        raise ValueError("Provide exactly one of inputs or input_records")
    manifest_inputs = (
        build_file_records(inputs or {})
        if input_records is None
        else _validate_precomputed_records(input_records, label="raw input")
    )
    manifest_outputs = build_file_records(outputs, recorded_paths=output_record_paths)
    manifest_audit = build_file_records(
        audit_artifacts or {}, recorded_paths=audit_record_paths
    )
    return {
        "manifest_version": "1.0",
        "version_id": version_id,
        "config": {
            "path": str(config.resolve()),
            "bytes": config.stat().st_size,
            "sha256": config_sha256 or sha256_file(config),
        },
        "inputs": manifest_inputs,
        "outputs": manifest_outputs,
        "audit_artifacts": manifest_audit,
        "metadata": dict(metadata or {}),
    }


def export_panel_bundle(
    long_panel: pd.DataFrame,
    output_directory: str | Path,
    *,
    config_path: str | Path,
    inputs: Mapping[str, str | Path] | None = None,
    input_records: Mapping[str, Mapping[str, Any]] | None = None,
    audit_artifacts: Mapping[str, str | Path] | None = None,
    audit_record_paths: Mapping[str, str | Path] | None = None,
    years: Sequence[int] = tuple(range(2010, 2020)),
    windows: Sequence[str] = CANONICAL_WINDOWS,
    expected_long_rows: int | None = 1_330_800,
    expected_wide_rows: int | None = 221_800,
    version_id: str = "data-climate-stress-2010-2019-v1",
    variable_metadata: Mapping[str, Mapping[str, Any]] | None = None,
    sources: Mapping[str, Any] | None = None,
    transformations: Mapping[str, Any] | None = None,
    quality: Mapping[str, Any] | None = None,
    exclusions: Sequence[str] | None = None,
    compression: str = "zstd",
    row_group_size: int = 262_144,
    netcdf_complevel: int = 4,
    published_output_directory: str | Path | None = None,
) -> tuple[ExportPaths, pd.DataFrame, pd.DataFrame]:
    """Write the complete canonical package after a no-overwrite preflight."""

    paths = ExportPaths.in_directory(output_directory)
    conflicts = [path for path in paths.all() if path.exists()]
    if conflicts:
        raise FileExistsError(f"Refusing to overwrite existing targets: {conflicts}")
    long = canonicalize_long_panel(
        long_panel, years=years, windows=windows, expected_rows=expected_long_rows
    )
    wide = pivot_long_to_wide(
        long,
        years=years,
        windows=windows,
        expected_long_rows=expected_long_rows,
        expected_wide_rows=expected_wide_rows,
    )
    write_parquet_exclusive(
        long, paths.long_parquet, compression=compression, row_group_size=row_group_size
    )
    write_parquet_exclusive(
        wide, paths.wide_parquet, compression=compression, row_group_size=row_group_size
    )
    complete_metadata = generate_variable_metadata(
        long.columns, overrides=variable_metadata
    )
    write_cf_netcdf(
        long,
        paths.netcdf,
        years=years,
        windows=windows,
        expected_rows=expected_long_rows,
        complevel=netcdf_complevel,
        version_id=version_id,
        variable_metadata=complete_metadata,
    )
    write_stata_bundle(
        wide,
        paths.stata,
        paths.alias_map,
        paths.merge_do,
        expected_rows=expected_wide_rows,
    )
    dictionary = build_variable_dictionary(long, variable_metadata=complete_metadata)
    write_variable_dictionary(
        dictionary, paths.variable_dictionary_csv, paths.variable_dictionary_md
    )
    passport = build_material_passport(
        long,
        version_id=version_id,
        sources=sources or inputs,
        transformations=transformations,
        quality=quality,
        exclusions=exclusions,
    )
    write_json_exclusive(passport, paths.material_passport)
    output_records = {
        field: path
        for field, path in ((name, getattr(paths, name)) for name in paths.__dataclass_fields__)
        if field != "manifest"
    }
    output_record_paths = None
    if published_output_directory is not None:
        output_root = Path(output_directory)
        published_root = Path(published_output_directory)
        output_record_paths = {
            name: published_root / Path(path).relative_to(output_root)
            for name, path in output_records.items()
        }
    manifest = build_manifest(
        version_id=version_id,
        config_path=config_path,
        inputs=inputs,
        input_records=input_records,
        outputs=output_records,
        output_record_paths=output_record_paths,
        audit_artifacts=audit_artifacts,
        audit_record_paths=audit_record_paths,
        metadata={
            "long_rows": len(long),
            "wide_rows": len(wide),
            "selected_cells": int(long["era01_cell_id"].nunique()),
            "windows": list(windows),
            "years": [int(year) for year in years],
            "quality": dict(quality or {}),
        },
    )
    write_json_exclusive(manifest, paths.manifest)
    return paths, long, wide


def _variable_dictionary_from_arrow_schema(
    schema: Any,
    *,
    variable_metadata: Mapping[str, Mapping[str, Any]] | None = None,
) -> pd.DataFrame:
    metadata = generate_variable_metadata(schema.names, overrides=variable_metadata)
    return pd.DataFrame(
        [
            {
                "variable": field.name,
                "dtype": str(field.type),
                "role": "key" if field.name in LONG_KEY_COLUMNS else "climate_measure",
                "unit": metadata[field.name]["units"],
                "description": metadata[field.name]["long_name"],
                "source_product": metadata[field.name]["source_product"],
                "version": metadata[field.name]["version"],
                "reference_id": metadata[field.name]["reference_id"],
                "history_period": metadata[field.name]["history_period"],
                "time_window": metadata[field.name]["time_window"],
                "layer_role": metadata[field.name]["layer_role"],
                "variant_status": metadata[field.name]["variant_status"],
                "scope_id": metadata[field.name]["scope_id"],
                "scope_status": metadata[field.name]["scope_status"],
                "threshold_rule": metadata[field.name]["threshold_rule"],
                "minimum_duration": metadata[field.name]["minimum_duration"],
                "gap_rule": metadata[field.name]["gap_rule"],
                "recovery_rule": metadata[field.name]["recovery_rule"],
                "calendar_rule": metadata[field.name]["calendar_rule"],
                "censor_rule": metadata[field.name]["censor_rule"],
                "confirmatory_status": metadata[field.name]["confirmatory_status"],
            }
            for field in schema
        ]
    )


def export_panel_bundle_streaming(
    long_partition_source: str | Path,
    crosswalk: pd.DataFrame,
    output_directory: str | Path,
    *,
    config_path: str | Path,
    inputs: Mapping[str, str | Path] | None = None,
    input_records: Mapping[str, Mapping[str, Any]] | None = None,
    audit_artifacts: Mapping[str, str | Path] | None = None,
    audit_record_paths: Mapping[str, str | Path] | None = None,
    years: Sequence[int] = tuple(range(2010, 2020)),
    windows: Sequence[str] = CANONICAL_WINDOWS,
    expected_long_rows: int = 1_330_800,
    expected_wide_rows: int = 221_800,
    version_id: str = "data-climate-stress-2010-2019-v1",
    variable_metadata: Mapping[str, Mapping[str, Any]] | None = None,
    gleam_layer_roles: Mapping[str, str] | None = None,
    sources: Mapping[str, Any] | None = None,
    transformations: Mapping[str, Any] | None = None,
    quality: Mapping[str, Any] | None = None,
    exclusions: Sequence[str] | None = None,
    compression: str = "zstd",
    row_group_size: int = 262_144,
    netcdf_complevel: int = 4,
    published_output_directory: str | Path | None = None,
) -> tuple[ExportPaths, dict[str, Any]]:
    """Export the complete package with a bounded spatial working set."""

    from .spei import combine_parquet_partitions_new

    if compression.casefold() != "zstd":
        raise ValueError("Streaming bundle currently requires zstd Parquet compression")
    paths = ExportPaths.in_directory(output_directory)
    wide_partition_root = Path(output_directory) / "wide_partitions"
    output_contract_path = Path(output_directory) / "output_contract.json"
    conflicts = [
        path
        for path in (*paths.all(), wide_partition_root, output_contract_path)
        if path.exists()
    ]
    if conflicts:
        raise FileExistsError(f"Refusing to overwrite existing targets: {conflicts}")
    contract = inspect_partitioned_long_panel(
        long_partition_source,
        years=years,
        windows=windows,
        expected_rows=expected_long_rows,
        expected_cells=len(crosswalk),
    )
    if int(contract["selected_cells"]) * len(years) != int(expected_wide_rows):
        raise ValueError("Expected wide rows differ from canonical cell/year support")

    _target, long_rows = combine_parquet_partitions_new(
        contract["files"],
        paths.long_parquet,
        row_group_size=row_group_size,
    )
    if long_rows != expected_long_rows:
        raise AssertionError("Streamed long Parquet row count changed")

    wide_partition_root.mkdir(parents=True, exist_ok=False)
    wide_partitions: list[Path] = []
    max_wide_rows = 0
    wide_rows = 0
    for index, source_path in enumerate(contract["files"]):
        long_block = pd.read_parquet(source_path)
        block_cells = int(long_block["era01_cell_id"].nunique())
        block_expected_long = block_cells * len(years) * len(windows)
        block_expected_wide = block_cells * len(years)
        wide_block = pivot_long_to_wide(
            long_block,
            years=years,
            windows=windows,
            expected_long_rows=block_expected_long,
            expected_wide_rows=block_expected_wide,
        )
        partition = wide_partition_root / f"part-{index:06d}.parquet"
        write_parquet_exclusive(
            wide_block,
            partition,
            compression=compression,
            row_group_size=min(row_group_size, max(len(wide_block), 1)),
        )
        wide_partitions.append(partition)
        wide_rows += len(wide_block)
        max_wide_rows = max(max_wide_rows, len(wide_block))
    if wide_rows != expected_wide_rows:
        raise AssertionError("Wide partition rows differ from the frozen contract")
    _target, combined_wide_rows = combine_parquet_partitions_new(
        wide_partitions,
        paths.wide_parquet,
        row_group_size=row_group_size,
    )
    if combined_wide_rows != expected_wide_rows:
        raise AssertionError("Streamed wide Parquet row count changed")

    complete_metadata = generate_variable_metadata(
        contract["columns"],
        overrides=variable_metadata,
        gleam_layer_roles=gleam_layer_roles,
    )
    write_cf_netcdf_from_partitions(
        long_partition_source,
        crosswalk,
        paths.netcdf,
        years=years,
        windows=windows,
        expected_rows=expected_long_rows,
        complevel=netcdf_complevel,
        version_id=version_id,
        variable_metadata=complete_metadata,
    )
    _dta, _aliases, _merge, alias_frame, dta_report = (
        write_stata_bundle_from_partitions(
            wide_partition_root,
            paths.stata,
            paths.alias_map,
            paths.merge_do,
            expected_rows=expected_wide_rows,
        )
    )
    dictionary = _variable_dictionary_from_arrow_schema(
        contract["schema"], variable_metadata=complete_metadata
    )
    write_variable_dictionary(
        dictionary, paths.variable_dictionary_csv, paths.variable_dictionary_md
    )
    streaming_contract = {
        "long_partition_count": len(contract["files"]),
        "long_partition_rows_max": int(contract["max_partition_rows"]),
        "wide_partition_count": len(wide_partitions),
        "wide_partition_rows_max": max_wide_rows,
        "dta_partition_rows_max": int(dta_report["max_partition_rows"]),
        "netcdf_spatial_layer_cells_max": TARGET_GRID.nlat * TARGET_GRID.nlon,
        "full_long_dataframe_forbidden": True,
        "full_wide_dataframe_forbidden": True,
    }
    scope_contract = {
        "contract_version": 1,
        "version_id": version_id,
        "scope_id": OUTPUT_SCOPE_ID,
        "status": OUTPUT_SCOPE_STATUS,
        "spei_2w": {
            "numeric_executed": False,
            "output_included": False,
        },
        "compound_severity": {
            "heat_excess_field_suffix": "heat_excess_cdays",
            "soil_deficit_field_suffix": "sm_deficit_m3m3_days",
            "mixed_unit_scalar_included": False,
        },
        "streaming_contract": streaming_contract,
    }
    write_json_exclusive(scope_contract, output_contract_path)
    passport = {
        "material_passport_version": "1.0",
        "artifact_id": version_id,
        "scope_id": OUTPUT_SCOPE_ID,
        "status": OUTPUT_SCOPE_STATUS,
        "entity": "selected 0.1-degree grid x calendar year x phenological window",
        "primary_keys": list(LONG_KEY_COLUMNS),
        "rows": int(expected_long_rows),
        "selected_cells": int(contract["selected_cells"]),
        "years": [int(value) for value in years],
        "windows": list(windows),
        "grid": {
            "crs": TARGET_GRID.crs,
            "shape": [TARGET_GRID.nlat, TARGET_GRID.nlon],
            "resolution_degrees": TARGET_GRID.step,
            "latitude_centres": [TARGET_GRID.north, TARGET_GRID.south],
            "longitude_centres": [TARGET_GRID.west, TARGET_GRID.east],
            "stable_id_formula": "lat_idx * 616 + lon_idx + 1",
        },
        "sources": dict(sources or inputs or {}),
        "transformations": dict(transformations or {}),
        "quality": {**dict(quality or {}), "streaming_contract": streaming_contract},
        "excluded_manual_families": list(exclusions or []),
        "spei_2w_numeric_executed": False,
        "spei_2w_output_included": False,
        "compound_mixed_unit_severity_scalar_included": False,
        "dataframe_sha256": sha256_file(paths.long_parquet),
        "dataframe_hash_semantics": "SHA-256 of deterministic canonical long Parquet",
    }
    write_json_exclusive(passport, paths.material_passport)

    output_records = {
        field: path
        for field, path in (
            (name, getattr(paths, name)) for name in paths.__dataclass_fields__
        )
        if field != "manifest"
    }
    output_records["wide_partitions"] = wide_partition_root
    output_records["output_contract"] = output_contract_path
    output_record_paths = None
    if published_output_directory is not None:
        output_root = Path(output_directory)
        published_root = Path(published_output_directory)
        output_record_paths = {
            name: published_root / Path(path).relative_to(output_root)
            for name, path in output_records.items()
        }
    manifest = build_manifest(
        version_id=version_id,
        config_path=config_path,
        inputs=inputs,
        input_records=input_records,
        outputs=output_records,
        output_record_paths=output_record_paths,
        audit_artifacts=audit_artifacts,
        audit_record_paths=audit_record_paths,
        metadata={
            "scope_id": OUTPUT_SCOPE_ID,
            "status": OUTPUT_SCOPE_STATUS,
            "spei_2w_numeric_executed": False,
            "spei_2w_output_included": False,
            "compound_mixed_unit_severity_scalar_included": False,
            "long_rows": expected_long_rows,
            "wide_rows": expected_wide_rows,
            "selected_cells": int(contract["selected_cells"]),
            "windows": list(windows),
            "years": [int(year) for year in years],
            "quality": {**dict(quality or {}), "streaming_contract": streaming_contract},
            "stata_aliases": len(alias_frame),
        },
    )
    write_json_exclusive(manifest, paths.manifest)
    return paths, {
        "long_rows": expected_long_rows,
        "wide_rows": expected_wide_rows,
        "selected_cells": int(contract["selected_cells"]),
        "wide_partitions": wide_partition_root,
        "output_contract": output_contract_path,
        "streaming_contract": streaming_contract,
    }
