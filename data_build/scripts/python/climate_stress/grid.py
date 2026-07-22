"""Stable target-grid keys and reusable one-dimensional rectilinear mappings.

The climate-stress panel uses the ERA 0.1 degree grid as its only spatial
namespace.  Source-product row/column numbers never become panel identifiers;
they are held only inside the mapping objects defined in this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class TargetGridSpec:
    """Frozen definition of the 376 x 616 ERA target grid."""

    nlat: int = 376
    nlon: int = 616
    north: float = 53.53
    south: float = 16.03
    west: float = 73.58
    east: float = 135.08
    step: float = 0.1
    crs: str = "EPSG:4326"

    @property
    def latitudes(self) -> np.ndarray:
        return np.round(self.north - np.arange(self.nlat) * self.step, 2)

    @property
    def longitudes(self) -> np.ndarray:
        return np.round(self.west + np.arange(self.nlon) * self.step, 2)

    @property
    def cell_count(self) -> int:
        return self.nlat * self.nlon

    def era01_cell_id(self, lat_idx: np.ndarray, lon_idx: np.ndarray) -> np.ndarray:
        return lat_idx.astype(np.int64) * self.nlon + lon_idx.astype(np.int64) + 1


TARGET_GRID = TargetGridSpec()


def validate_target_axes(
    latitudes: Iterable[float],
    longitudes: Iterable[float],
    *,
    spec: TargetGridSpec = TARGET_GRID,
    atol: float = 1e-8,
) -> None:
    """Require the exact frozen axes, including their orientation."""

    lat = np.asarray(tuple(latitudes), dtype=np.float64)
    lon = np.asarray(tuple(longitudes), dtype=np.float64)
    if lat.shape != (spec.nlat,) or not np.allclose(lat, spec.latitudes, atol=atol, rtol=0):
        raise ValueError(
            f"Latitude axis must be {spec.nlat} values from {spec.north:.2f} "
            f"to {spec.south:.2f}"
        )
    if lon.shape != (spec.nlon,) or not np.allclose(lon, spec.longitudes, atol=atol, rtol=0):
        raise ValueError(
            f"Longitude axis must be {spec.nlon} values from {spec.west:.2f} "
            f"to {spec.east:.2f}"
        )


def target_indices(
    latitude: Iterable[float] | np.ndarray,
    longitude: Iterable[float] | np.ndarray,
    *,
    spec: TargetGridSpec = TARGET_GRID,
    atol: float = 1e-7,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Map point coordinates to frozen target indices without snapping off-grid data."""

    lat = np.asarray(latitude, dtype=np.float64)
    lon = np.asarray(longitude, dtype=np.float64)
    if lat.shape != lon.shape:
        raise ValueError("latitude and longitude must have the same shape")

    raw_lat = (spec.north - lat) / spec.step
    raw_lon = (lon - spec.west) / spec.step
    safe_lat = np.where(np.isfinite(raw_lat), raw_lat, 0.0)
    safe_lon = np.where(np.isfinite(raw_lon), raw_lon, 0.0)
    lat_idx = np.rint(safe_lat).astype(np.int64)
    lon_idx = np.rint(safe_lon).astype(np.int64)
    valid = (
        np.isfinite(lat)
        & np.isfinite(lon)
        & (lat_idx >= 0)
        & (lat_idx < spec.nlat)
        & (lon_idx >= 0)
        & (lon_idx < spec.nlon)
        & np.isclose(raw_lat, lat_idx, atol=atol / spec.step, rtol=0)
        & np.isclose(raw_lon, lon_idx, atol=atol / spec.step, rtol=0)
    )
    return lat_idx, lon_idx, valid


def _rounded_tenth(values: np.ndarray) -> np.ndarray:
    """Project convention: positive coordinates rounded to integer tenths."""

    return np.floor(values.astype(np.float64) * 10.0 + 0.5).astype(np.int32)


def _read_v3_table(
    source: str | Path | pd.DataFrame,
    *,
    columns: Iterable[str] | None = None,
) -> pd.DataFrame:
    projected = None if columns is None else list(dict.fromkeys(columns))
    if isinstance(source, pd.DataFrame):
        return source.copy() if projected is None else source.loc[:, projected].copy()
    path = Path(source)
    suffix = path.suffix.lower()
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path, columns=projected)
    if suffix == ".dta":
        return pd.read_stata(
            path,
            convert_categoricals=False,
            columns=projected,
        )
    if suffix in {".csv", ".txt"}:
        return pd.read_csv(path, usecols=projected)
    raise ValueError(f"Unsupported V3 table format: {path.suffix}")


def _v3_source_columns(source: str | Path | pd.DataFrame) -> tuple[str, ...] | None:
    """Read only schema metadata when a column projection is supported."""

    if isinstance(source, pd.DataFrame):
        return tuple(str(column) for column in source.columns)
    path = Path(source)
    if path.suffix.lower() in {".parquet", ".pq"}:
        import pyarrow.parquet as pq

        return tuple(str(column) for column in pq.read_schema(path).names)
    return None


def build_v3_crosswalk(
    source: str | Path | pd.DataFrame,
    *,
    latitude_col: str = "latitude",
    longitude_col: str = "longitude",
    grid_id_col: str | None = None,
    expected_unique: int | None = 22_180,
    spec: TargetGridSpec = TARGET_GRID,
    input_coordinate_tolerance: float = 1e-5,
) -> pd.DataFrame:
    """Build the stable coordinate crosswalk from the union of V3-main rows.

    Both directions are one-to-one: one V3 identifier may have only one target
    cell and one target cell may have only one V3 identifier.  Coordinates are
    canonicalized to the frozen ERA axes only after an exact on-axis check.
    """

    available = _v3_source_columns(source)
    if grid_id_col is None:
        if available is None:
            frame = _read_v3_table(source)
            grid_id_col = "grid_id_v3" if "grid_id_v3" in frame.columns else "grid_id"
        else:
            grid_id_col = "grid_id_v3" if "grid_id_v3" in available else "grid_id"
            frame = _read_v3_table(
                source,
                columns=(grid_id_col, latitude_col, longitude_col),
            )
    else:
        frame = _read_v3_table(
            source,
            columns=(grid_id_col, latitude_col, longitude_col),
        )
    required = {latitude_col, longitude_col, grid_id_col}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"V3 main is missing required columns: {missing}")

    raw = frame[[grid_id_col, latitude_col, longitude_col]].copy()
    if raw.isna().any().any():
        raise ValueError("V3 coordinate and grid-id columns must not contain missing values")

    numeric_id = pd.to_numeric(raw[grid_id_col], errors="raise").to_numpy(dtype=np.float64)
    if not np.isfinite(numeric_id).all() or not np.equal(numeric_id, np.rint(numeric_id)).all():
        raise ValueError("grid_id_v3 must contain finite integer values")
    raw["grid_id_v3"] = np.rint(numeric_id).astype(np.int64)

    lat = pd.to_numeric(raw[latitude_col], errors="raise").to_numpy(dtype=np.float64)
    lon = pd.to_numeric(raw[longitude_col], errors="raise").to_numpy(dtype=np.float64)
    lat_idx, lon_idx, valid = target_indices(
        lat,
        lon,
        spec=spec,
        atol=float(input_coordinate_tolerance),
    )
    if not valid.all():
        examples = np.flatnonzero(~valid)[:5].tolist()
        raise ValueError(f"V3 coordinates are not on the frozen target axes; row indices={examples}")

    raw["lat_idx"] = lat_idx.astype(np.int32)
    raw["lon_idx"] = lon_idx.astype(np.int32)
    raw["era01_cell_id"] = spec.era01_cell_id(lat_idx, lon_idx)
    raw["latitude"] = spec.latitudes[lat_idx]
    raw["longitude"] = spec.longitudes[lon_idx]
    raw["v3_lat_err_abs_deg"] = np.abs(lat - raw["latitude"].to_numpy())
    raw["v3_lon_err_abs_deg"] = np.abs(lon - raw["longitude"].to_numpy())

    if raw.groupby("grid_id_v3")["era01_cell_id"].nunique().max() != 1:
        raise ValueError("A grid_id_v3 maps to more than one target cell")
    if raw.groupby("era01_cell_id")["grid_id_v3"].nunique().max() != 1:
        raise ValueError("A target cell maps to more than one grid_id_v3")

    key_columns = [
        "grid_id_v3",
        "era01_cell_id",
        "lat_idx",
        "lon_idx",
        "latitude",
        "longitude",
    ]
    crosswalk = (
        raw.groupby(key_columns, as_index=False, sort=False)
        .agg(
            v3_lat_err_abs_deg=("v3_lat_err_abs_deg", "max"),
            v3_lon_err_abs_deg=("v3_lon_err_abs_deg", "max"),
        )
        .sort_values("era01_cell_id")
        .reset_index(drop=True)
    )
    crosswalk["lat10"] = _rounded_tenth(crosswalk["latitude"].to_numpy())
    crosswalk["lon10"] = _rounded_tenth(crosswalk["longitude"].to_numpy())
    if expected_unique is not None and len(crosswalk) != expected_unique:
        raise ValueError(f"Expected {expected_unique:,} V3 cells, found {len(crosswalk):,}")
    validate_v3_crosswalk(crosswalk, expected_unique=expected_unique, spec=spec)
    return crosswalk


def validate_v3_crosswalk(
    crosswalk: pd.DataFrame,
    *,
    expected_unique: int | None = 22_180,
    spec: TargetGridSpec = TARGET_GRID,
) -> None:
    """Validate all public crosswalk keys and formulas."""

    required = {
        "grid_id_v3",
        "era01_cell_id",
        "lat_idx",
        "lon_idx",
        "latitude",
        "longitude",
        "lat10",
        "lon10",
    }
    missing = sorted(required.difference(crosswalk.columns))
    if missing:
        raise ValueError(f"Crosswalk is missing columns: {missing}")
    if crosswalk[list(required)].isna().any().any():
        raise ValueError("Crosswalk keys must not be missing")
    if expected_unique is not None and len(crosswalk) != expected_unique:
        raise ValueError(f"Expected {expected_unique:,} crosswalk rows, found {len(crosswalk):,}")
    if crosswalk["grid_id_v3"].duplicated().any():
        raise ValueError("grid_id_v3 must be unique")
    if crosswalk["era01_cell_id"].duplicated().any():
        raise ValueError("era01_cell_id must be unique")

    lat_idx = crosswalk["lat_idx"].to_numpy(dtype=np.int64)
    lon_idx = crosswalk["lon_idx"].to_numpy(dtype=np.int64)
    expected_cell = spec.era01_cell_id(lat_idx, lon_idx)
    if not np.array_equal(crosswalk["era01_cell_id"].to_numpy(dtype=np.int64), expected_cell):
        raise ValueError("era01_cell_id does not satisfy lat_idx*nlon+lon_idx+1")
    if not np.allclose(
        crosswalk["latitude"].to_numpy(dtype=np.float64), spec.latitudes[lat_idx], rtol=0, atol=1e-8
    ):
        raise ValueError("latitude does not match lat_idx on the frozen axis")
    if not np.allclose(
        crosswalk["longitude"].to_numpy(dtype=np.float64), spec.longitudes[lon_idx], rtol=0, atol=1e-8
    ):
        raise ValueError("longitude does not match lon_idx on the frozen axis")
    if not np.array_equal(
        crosswalk["lat10"].to_numpy(dtype=np.int32),
        _rounded_tenth(crosswalk["latitude"].to_numpy()),
    ):
        raise ValueError("lat10 does not use the frozen rounded-tenth rule")
    if not np.array_equal(
        crosswalk["lon10"].to_numpy(dtype=np.int32),
        _rounded_tenth(crosswalk["longitude"].to_numpy()),
    ):
        raise ValueError("lon10 does not use the frozen rounded-tenth rule")
    if crosswalk.duplicated(["lat10", "lon10"]).any():
        raise ValueError("Rounded-tenth coordinate keys must be unique")


def build_balanced_grid_year(
    crosswalk: pd.DataFrame,
    years: Iterable[int] = range(2010, 2020),
    *,
    expected_unique: int | None = 22_180,
    spec: TargetGridSpec = TARGET_GRID,
) -> pd.DataFrame:
    """Cross the V3 coordinate union with target years without dropping cells."""

    validate_v3_crosswalk(crosswalk, expected_unique=expected_unique, spec=spec)
    year_values = np.asarray(tuple(int(year) for year in years), dtype=np.int16)
    if year_values.size == 0 or np.unique(year_values).size != year_values.size:
        raise ValueError("years must be a non-empty unique sequence")
    if np.any(np.diff(year_values) <= 0):
        raise ValueError("years must be strictly increasing")

    panel = crosswalk.assign(_join_key=1).merge(
        pd.DataFrame({"year": year_values, "_join_key": 1}), on="_join_key", how="inner"
    ).drop(columns="_join_key")
    panel = panel.sort_values(["era01_cell_id", "year"]).reset_index(drop=True)
    expected_rows = len(crosswalk) * len(year_values)
    if len(panel) != expected_rows or panel.duplicated(["era01_cell_id", "year"]).any():
        raise AssertionError("Balanced grid-year construction failed")
    return panel


def _axis_and_original_indices(values: Iterable[float], name: str) -> tuple[np.ndarray, np.ndarray]:
    axis = np.asarray(tuple(values), dtype=np.float64)
    if axis.ndim != 1 or axis.size < 2 or not np.isfinite(axis).all():
        raise ValueError(f"{name} must be a finite one-dimensional axis with at least two values")
    differences = np.diff(axis)
    if np.all(differences > 0):
        return axis, np.arange(axis.size, dtype=np.int64)
    if np.all(differences < 0):
        return axis[::-1], np.arange(axis.size - 1, -1, -1, dtype=np.int64)
    raise ValueError(f"{name} must be strictly monotonic")


def _target_points(
    latitude: Iterable[float] | np.ndarray, longitude: Iterable[float] | np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    lat = np.asarray(latitude, dtype=np.float64)
    lon = np.asarray(longitude, dtype=np.float64)
    if lat.shape != lon.shape:
        raise ValueError("target latitude and longitude must have the same shape")
    return lat.reshape(-1), lon.reshape(-1)


@dataclass(frozen=True)
class NearestMapping:
    lat_index: np.ndarray
    lon_index: np.ndarray
    valid: np.ndarray
    source_shape: tuple[int, int]
    target_shape: tuple[int, ...]


def build_nearest_mapping(
    source_latitude: Iterable[float],
    source_longitude: Iterable[float],
    target_latitude: Iterable[float] | np.ndarray,
    target_longitude: Iterable[float] | np.ndarray,
    *,
    allow_extrapolation: bool = False,
) -> NearestMapping:
    """Build deterministic nearest-neighbour indices for rectilinear axes."""

    source_lat, lat_original = _axis_and_original_indices(source_latitude, "source_latitude")
    source_lon, lon_original = _axis_and_original_indices(source_longitude, "source_longitude")
    target_shape = np.asarray(target_latitude).shape
    target_lat, target_lon = _target_points(target_latitude, target_longitude)

    def nearest(axis: np.ndarray, original: np.ndarray, target: np.ndarray) -> np.ndarray:
        right = np.searchsorted(axis, target, side="left")
        right = np.clip(right, 0, axis.size - 1)
        left = np.clip(right - 1, 0, axis.size - 1)
        use_left = np.abs(target - axis[left]) <= np.abs(axis[right] - target)
        return original[np.where(use_left, left, right)]

    valid = np.isfinite(target_lat) & np.isfinite(target_lon)
    if not allow_extrapolation:
        valid &= (
            (target_lat >= source_lat[0])
            & (target_lat <= source_lat[-1])
            & (target_lon >= source_lon[0])
            & (target_lon <= source_lon[-1])
        )
    lat_index = nearest(source_lat, lat_original, np.where(valid, target_lat, source_lat[0]))
    lon_index = nearest(source_lon, lon_original, np.where(valid, target_lon, source_lon[0]))
    lat_index = np.where(valid, lat_index, -1).astype(np.int64)
    lon_index = np.where(valid, lon_index, -1).astype(np.int64)
    return NearestMapping(
        lat_index=lat_index,
        lon_index=lon_index,
        valid=valid,
        source_shape=(source_lat.size, source_lon.size),
        target_shape=target_shape,
    )


def apply_nearest(values: np.ndarray, mapping: NearestMapping) -> np.ndarray:
    """Apply a nearest mapping to arrays whose final dimensions are lat/lon."""

    data = np.ma.filled(np.asanyarray(values), np.nan)
    if data.shape[-2:] != mapping.source_shape:
        raise ValueError(f"Expected source shape {mapping.source_shape}, found {data.shape[-2:]}")
    data = data.astype(np.result_type(data.dtype, np.float32), copy=False)
    safe_lat = np.where(mapping.valid, mapping.lat_index, 0)
    safe_lon = np.where(mapping.valid, mapping.lon_index, 0)
    selected = data[..., safe_lat, safe_lon]
    selected = np.where(mapping.valid, selected, np.nan)
    return selected.reshape(data.shape[:-2] + mapping.target_shape)


@dataclass(frozen=True)
class BilinearMapping:
    lat_index: np.ndarray
    lon_index: np.ndarray
    weights: np.ndarray
    valid: np.ndarray
    source_shape: tuple[int, int]
    target_shape: tuple[int, ...]


def _brackets(
    axis: np.ndarray, original: np.ndarray, targets: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    upper = np.searchsorted(axis, targets, side="right")
    upper = np.clip(upper, 1, axis.size - 1)
    lower = upper - 1
    fraction = (targets - axis[lower]) / (axis[upper] - axis[lower])
    return original[lower], original[upper], np.clip(fraction, 0.0, 1.0)


def build_bilinear_mapping(
    source_latitude: Iterable[float],
    source_longitude: Iterable[float],
    target_latitude: Iterable[float] | np.ndarray,
    target_longitude: Iterable[float] | np.ndarray,
) -> BilinearMapping:
    """Build SW/SE/NW/NE indices and weights without spatial extrapolation."""

    source_lat, lat_original = _axis_and_original_indices(source_latitude, "source_latitude")
    source_lon, lon_original = _axis_and_original_indices(source_longitude, "source_longitude")
    target_shape = np.asarray(target_latitude).shape
    target_lat, target_lon = _target_points(target_latitude, target_longitude)
    valid = (
        np.isfinite(target_lat)
        & np.isfinite(target_lon)
        & (target_lat >= source_lat[0])
        & (target_lat <= source_lat[-1])
        & (target_lon >= source_lon[0])
        & (target_lon <= source_lon[-1])
    )
    safe_lat = np.where(valid, target_lat, source_lat[0])
    safe_lon = np.where(valid, target_lon, source_lon[0])
    lat_low, lat_high, y_fraction = _brackets(source_lat, lat_original, safe_lat)
    lon_low, lon_high, x_fraction = _brackets(source_lon, lon_original, safe_lon)

    lat_index = np.column_stack([lat_low, lat_low, lat_high, lat_high]).astype(np.int64)
    lon_index = np.column_stack([lon_low, lon_high, lon_low, lon_high]).astype(np.int64)
    weights = np.column_stack(
        [
            (1.0 - x_fraction) * (1.0 - y_fraction),
            x_fraction * (1.0 - y_fraction),
            (1.0 - x_fraction) * y_fraction,
            x_fraction * y_fraction,
        ]
    )
    lat_index[~valid] = -1
    lon_index[~valid] = -1
    weights[~valid] = np.nan
    return BilinearMapping(
        lat_index=lat_index,
        lon_index=lon_index,
        weights=weights,
        valid=valid,
        source_shape=(source_lat.size, source_lon.size),
        target_shape=target_shape,
    )


def apply_bilinear(
    values: np.ndarray,
    mapping: BilinearMapping,
    *,
    min_valid_neighbors: int = 2,
) -> np.ndarray:
    """Interpolate and renormalize weights when at least two corners are valid."""

    if not 1 <= min_valid_neighbors <= 4:
        raise ValueError("min_valid_neighbors must lie in 1..4")
    data = np.ma.filled(np.asanyarray(values), np.nan)
    if data.shape[-2:] != mapping.source_shape:
        raise ValueError(f"Expected source shape {mapping.source_shape}, found {data.shape[-2:]}")
    data = data.astype(np.result_type(data.dtype, np.float32), copy=False)
    safe_lat = np.where(mapping.valid[:, None], mapping.lat_index, 0)
    safe_lon = np.where(mapping.valid[:, None], mapping.lon_index, 0)
    neighbours = np.stack(
        [data[..., safe_lat[:, corner], safe_lon[:, corner]] for corner in range(4)], axis=-1
    )
    finite = np.isfinite(neighbours)
    weight_shape = (1,) * (neighbours.ndim - 2) + mapping.weights.shape
    weights = np.broadcast_to(
        np.where(mapping.valid[:, None], mapping.weights, 0.0).reshape(weight_shape),
        neighbours.shape,
    )
    denominator = np.sum(np.where(finite, weights, 0.0), axis=-1)
    numerator = np.sum(np.where(finite, neighbours * weights, 0.0), axis=-1)
    valid_count = np.sum(finite, axis=-1)
    support = (
        np.broadcast_to(mapping.valid.reshape((1,) * (denominator.ndim - 1) + (-1,)), denominator.shape)
        & (valid_count >= min_valid_neighbors)
        & (denominator > 0)
    )
    result = np.full(denominator.shape, np.nan, dtype=np.result_type(data.dtype, np.float64))
    np.divide(numerator, denominator, out=result, where=support)
    return result.reshape(data.shape[:-2] + mapping.target_shape)
