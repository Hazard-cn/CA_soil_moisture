"""ChinaCropPhen maize aggregation and frozen phenological windows.

Each year is geolocated independently.  V3, HE, and MA are aligned on their
shared 1 km pixel lattice, after which the validity and V3 < HE < MA rules are
applied to the same source pixels.  Pixel membership is defined by the source
pixel centre falling in a target 0.1 degree cell; target-cell edges are treated
as west/north inclusive and east/south exclusive so a pixel is never counted
twice.
"""

from __future__ import annotations

import calendar
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

import numpy as np
import pandas as pd
from PIL import Image
from pyproj import CRS, Transformer

from .grid import TARGET_GRID, TargetGridSpec, validate_v3_crosswalk


CHINA_MAIZE_ALBERS = (
    "+proj=aea +lat_1=15 +lat_2=65 +lat_0=30 +lon_0=95 "
    "+datum=WGS84 +units=m +no_defs"
)
PHENOLOGY_STAGES = ("v3", "he", "ma")
WINDOW_NAMES = ("full", "v3pre30", "v3pm10", "hepm10", "v3he", "hema")


@dataclass(frozen=True)
class GeoTiffGrid:
    """North-up pixel geometry extracted from GeoTIFF model tags."""

    width: int
    height: int
    x_origin: float
    y_origin: float
    pixel_width: float
    pixel_height: float
    nodata: float | None = None

    @property
    def x_end(self) -> float:
        return self.x_origin + self.width * self.pixel_width

    @property
    def y_end(self) -> float:
        return self.y_origin - self.height * self.pixel_height


@dataclass(frozen=True)
class PixelMembership:
    """Sparse mapping from raster pixels to rows of a selected-cell crosswalk."""

    pixel_index: np.ndarray
    cell_position: np.ndarray
    candidate_count: np.ndarray
    raster_shape: tuple[int, int]


def _parse_nodata(raw: object) -> float | None:
    if raw is None:
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def read_phenology_tiff(path: str | Path) -> tuple[np.ndarray, GeoTiffGrid]:
    """Read one stage and mask its tag-defined and frozen invalid values."""

    source = Path(path)
    with Image.open(source) as image:
        scale = image.tag_v2.get(33550)
        tie = image.tag_v2.get(33922)
        if scale is None or tie is None or len(scale) < 2 or len(tie) < 6:
            raise ValueError(f"GeoTIFF lacks ModelPixelScale/ModelTiepoint tags: {source}")
        pixel_width = float(scale[0])
        pixel_height = float(scale[1])
        if pixel_width <= 0 or pixel_height <= 0:
            raise ValueError(f"GeoTIFF pixel sizes must be positive: {source}")
        tie_col, tie_row = float(tie[0]), float(tie[1])
        x_origin = float(tie[3]) - tie_col * pixel_width
        y_origin = float(tie[4]) + tie_row * pixel_height
        nodata = _parse_nodata(image.tag_v2.get(42113))
        values = np.asarray(image, dtype=np.float32).copy()
        metadata = GeoTiffGrid(
            width=image.width,
            height=image.height,
            x_origin=x_origin,
            y_origin=y_origin,
            pixel_width=pixel_width,
            pixel_height=pixel_height,
            nodata=nodata,
        )

    invalid = ~np.isfinite(values) | (values <= 0) | (values > 366) | (values == 65535)
    if nodata is not None:
        invalid |= np.isclose(values, nodata, rtol=1e-6, atol=1e-6)
    values[invalid] = np.nan
    return values, metadata


def _aligned_offset(value: float, origin: float, step: float, label: str) -> int:
    raw = (value - origin) / step
    rounded = int(round(raw))
    if not math.isclose(raw, rounded, abs_tol=1e-6, rel_tol=0):
        raise ValueError(f"Phenology rasters are not aligned on the same {label} lattice")
    return rounded


def align_stage_rasters(
    arrays: Mapping[str, np.ndarray], metadata: Mapping[str, GeoTiffGrid]
) -> tuple[dict[str, np.ndarray], GeoTiffGrid]:
    """Place different stage extents on one common pixel lattice for a year."""

    if set(arrays) != set(PHENOLOGY_STAGES) or set(metadata) != set(PHENOLOGY_STAGES):
        raise ValueError(f"arrays and metadata must contain exactly {PHENOLOGY_STAGES}")
    metas = [metadata[stage] for stage in PHENOLOGY_STAGES]
    pixel_width = metas[0].pixel_width
    pixel_height = metas[0].pixel_height
    if any(
        not math.isclose(meta.pixel_width, pixel_width, rel_tol=0, abs_tol=1e-6)
        or not math.isclose(meta.pixel_height, pixel_height, rel_tol=0, abs_tol=1e-6)
        for meta in metas[1:]
    ):
        raise ValueError("Phenology stage rasters must use the same pixel size")

    x_origin = min(meta.x_origin for meta in metas)
    y_origin = max(meta.y_origin for meta in metas)
    x_end = max(meta.x_end for meta in metas)
    y_end = min(meta.y_end for meta in metas)
    width = _aligned_offset(x_end, x_origin, pixel_width, "x")
    height = _aligned_offset(y_origin - y_end, 0.0, pixel_height, "y")
    union = GeoTiffGrid(
        width=width,
        height=height,
        x_origin=x_origin,
        y_origin=y_origin,
        pixel_width=pixel_width,
        pixel_height=pixel_height,
    )

    aligned: dict[str, np.ndarray] = {}
    for stage in PHENOLOGY_STAGES:
        source = arrays[stage]
        meta = metadata[stage]
        if source.shape != (meta.height, meta.width):
            raise ValueError(f"{stage} array shape does not match its GeoTIFF metadata")
        col_start = _aligned_offset(meta.x_origin, x_origin, pixel_width, "x")
        row_start = _aligned_offset(y_origin - meta.y_origin, 0.0, pixel_height, "y")
        target = np.full((height, width), np.nan, dtype=np.float32)
        target[
            row_start : row_start + meta.height,
            col_start : col_start + meta.width,
        ] = source
        aligned[stage] = target
    return aligned, union


def _scan_bounds(
    metadata: GeoTiffGrid,
    crosswalk: pd.DataFrame,
    *,
    source_crs: str | CRS,
    spec: TargetGridSpec,
) -> tuple[int, int, int, int]:
    half = spec.step / 2.0
    lon = crosswalk["longitude"].to_numpy(dtype=np.float64)
    lat = crosswalk["latitude"].to_numpy(dtype=np.float64)
    corner_lon = np.concatenate([lon - half, lon + half, lon + half, lon - half])
    corner_lat = np.concatenate([lat - half, lat - half, lat + half, lat + half])
    to_source = Transformer.from_crs(spec.crs, source_crs, always_xy=True)
    x, y = to_source.transform(corner_lon, corner_lat)
    finite = np.isfinite(x) & np.isfinite(y)
    if not finite.any():
        return 0, 0, 0, 0
    x_min, x_max = float(np.min(np.asarray(x)[finite])), float(np.max(np.asarray(x)[finite]))
    y_min, y_max = float(np.min(np.asarray(y)[finite])), float(np.max(np.asarray(y)[finite]))
    col_start = max(0, int(math.floor((x_min - metadata.x_origin) / metadata.pixel_width)) - 1)
    col_end = min(
        metadata.width,
        int(math.ceil((x_max - metadata.x_origin) / metadata.pixel_width)) + 1,
    )
    row_start = max(0, int(math.floor((metadata.y_origin - y_max) / metadata.pixel_height)) - 1)
    row_end = min(
        metadata.height,
        int(math.ceil((metadata.y_origin - y_min) / metadata.pixel_height)) + 1,
    )
    return row_start, row_end, col_start, col_end


def build_pixel_membership(
    metadata: GeoTiffGrid,
    crosswalk: pd.DataFrame,
    *,
    source_crs: str | CRS = CHINA_MAIZE_ALBERS,
    spec: TargetGridSpec = TARGET_GRID,
    row_chunk_size: int = 128,
) -> PixelMembership:
    """Assign source pixels by centre to selected target cells."""

    if row_chunk_size <= 0:
        raise ValueError("row_chunk_size must be positive")
    validate_v3_crosswalk(crosswalk, expected_unique=None, spec=spec)
    n_cells = len(crosswalk)
    lookup = np.full(spec.cell_count + 1, -1, dtype=np.int32)
    selected_ids = crosswalk["era01_cell_id"].to_numpy(dtype=np.int64)
    lookup[selected_ids] = np.arange(n_cells, dtype=np.int32)
    row_start, row_end, col_start, col_end = _scan_bounds(
        metadata, crosswalk, source_crs=source_crs, spec=spec
    )
    if row_start >= row_end or col_start >= col_end:
        return PixelMembership(
            pixel_index=np.empty(0, dtype=np.int64),
            cell_position=np.empty(0, dtype=np.int32),
            candidate_count=np.zeros(n_cells, dtype=np.int32),
            raster_shape=(metadata.height, metadata.width),
        )

    columns = np.arange(col_start, col_end, dtype=np.int64)
    x_centres = metadata.x_origin + (columns + 0.5) * metadata.pixel_width
    to_wgs84 = Transformer.from_crs(source_crs, spec.crs, always_xy=True)
    pixel_parts: list[np.ndarray] = []
    cell_parts: list[np.ndarray] = []
    north_edge = spec.north + spec.step / 2.0
    west_edge = spec.west - spec.step / 2.0
    tolerance = 1e-9

    for first_row in range(row_start, row_end, row_chunk_size):
        last_row = min(first_row + row_chunk_size, row_end)
        rows = np.arange(first_row, last_row, dtype=np.int64)
        y_centres = metadata.y_origin - (rows + 0.5) * metadata.pixel_height
        xx, yy = np.meshgrid(x_centres, y_centres)
        longitude, latitude = to_wgs84.transform(xx, yy)
        scaled_lat = (north_edge - np.asarray(latitude)) / spec.step
        scaled_lon = (np.asarray(longitude) - west_edge) / spec.step
        lat_idx = np.floor(scaled_lat + tolerance).astype(np.int64)
        lon_idx = np.floor(scaled_lon + tolerance).astype(np.int64)
        inside = (
            np.isfinite(scaled_lat)
            & np.isfinite(scaled_lon)
            & (scaled_lat >= -tolerance)
            & (scaled_lat < spec.nlat - tolerance)
            & (scaled_lon >= -tolerance)
            & (scaled_lon < spec.nlon - tolerance)
            & (lat_idx >= 0)
            & (lat_idx < spec.nlat)
            & (lon_idx >= 0)
            & (lon_idx < spec.nlon)
        )
        safe_lat = np.where(inside, lat_idx, 0)
        safe_lon = np.where(inside, lon_idx, 0)
        era_id = spec.era01_cell_id(safe_lat, safe_lon)
        local_position = lookup[era_id]
        selected = inside & (local_position >= 0)
        if not selected.any():
            continue
        raster_rows = np.broadcast_to(rows[:, None], selected.shape)
        raster_cols = np.broadcast_to(columns[None, :], selected.shape)
        pixel_parts.append(
            (raster_rows[selected] * metadata.width + raster_cols[selected]).astype(np.int64)
        )
        cell_parts.append(local_position[selected].astype(np.int32))

    if pixel_parts:
        pixel_index = np.concatenate(pixel_parts)
        cell_position = np.concatenate(cell_parts)
        candidate_count = np.bincount(cell_position, minlength=n_cells).astype(np.int32)
    else:
        pixel_index = np.empty(0, dtype=np.int64)
        cell_position = np.empty(0, dtype=np.int32)
        candidate_count = np.zeros(n_cells, dtype=np.int32)
    return PixelMembership(
        pixel_index=pixel_index,
        cell_position=cell_position,
        candidate_count=candidate_count,
        raster_shape=(metadata.height, metadata.width),
    )


def aggregate_phenology_arrays(
    arrays: Mapping[str, np.ndarray],
    membership: PixelMembership,
    crosswalk: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate jointly valid source pixels to all selected target cells."""

    if set(arrays) != set(PHENOLOGY_STAGES):
        raise ValueError(f"arrays must contain exactly {PHENOLOGY_STAGES}")
    for stage, values in arrays.items():
        if values.shape != membership.raster_shape:
            raise ValueError(f"{stage} array shape does not match membership raster shape")
    if len(membership.candidate_count) != len(crosswalk):
        raise ValueError("membership and crosswalk cell counts differ")

    n_cells = len(crosswalk)
    pixel_index = membership.pixel_index
    cell_position = membership.cell_position
    sampled = {
        stage: np.asarray(arrays[stage], dtype=np.float64).reshape(-1)[pixel_index]
        for stage in PHENOLOGY_STAGES
    }
    joint_valid = np.ones(pixel_index.size, dtype=bool)
    for values in sampled.values():
        joint_valid &= np.isfinite(values) & (values >= 1) & (values <= 366) & (values != 65535)
    joint_valid &= (sampled["v3"] < sampled["he"]) & (sampled["he"] < sampled["ma"])
    groups = cell_position[joint_valid]
    valid_count = np.bincount(groups, minlength=n_cells).astype(np.int32)

    result = crosswalk.copy().reset_index(drop=True)
    result["pheno_candidate_pixel_count"] = membership.candidate_count
    result["pheno_valid_pixel_count"] = valid_count
    coverage = np.full(n_cells, np.nan, dtype=np.float64)
    np.divide(
        valid_count,
        membership.candidate_count,
        out=coverage,
        where=membership.candidate_count > 0,
    )
    result["pheno_coverage"] = coverage.astype(np.float32)

    if groups.size:
        order = np.argsort(groups, kind="stable")
        sorted_groups = groups[order]
        unique_groups, starts = np.unique(sorted_groups, return_index=True)
        ends = np.r_[starts[1:], sorted_groups.size]
    else:
        order = np.empty(0, dtype=np.int64)
        unique_groups = np.empty(0, dtype=np.int32)
        starts = np.empty(0, dtype=np.int64)
        ends = np.empty(0, dtype=np.int64)

    for stage in PHENOLOGY_STAGES:
        values = sampled[stage][joint_valid]
        counts = valid_count.astype(np.float64)
        sums = np.bincount(groups, weights=values, minlength=n_cells)
        sum_squares = np.bincount(groups, weights=values * values, minlength=n_cells)
        means = np.full(n_cells, np.nan, dtype=np.float64)
        np.divide(sums, counts, out=means, where=counts > 0)
        variance = np.full(n_cells, np.nan, dtype=np.float64)
        variance[counts > 0] = np.maximum(
            sum_squares[counts > 0] / counts[counts > 0] - means[counts > 0] ** 2,
            0.0,
        )
        medians = np.full(n_cells, np.nan, dtype=np.float64)
        iqrs = np.full(n_cells, np.nan, dtype=np.float64)
        sorted_values = values[order]
        for group, start, end in zip(unique_groups, starts, ends):
            group_values = sorted_values[start:end]
            medians[group] = np.median(group_values)
            q25, q75 = np.quantile(group_values, [0.25, 0.75], method="linear")
            iqrs[group] = q75 - q25

        rounded = np.full(n_cells, np.nan, dtype=np.float64)
        rounded[counts > 0] = np.floor(means[counts > 0] + 0.5)
        result[f"{stage}_doy"] = pd.array(rounded, dtype="Int16")
        result[f"{stage}_doy_mean"] = means.astype(np.float32)
        result[f"{stage}_doy_median"] = medians.astype(np.float32)
        result[f"{stage}_doy_std"] = np.sqrt(variance).astype(np.float32)
        result[f"{stage}_doy_iqr"] = iqrs.astype(np.float32)
    return result


def phenology_year_paths(
    directory: str | Path,
    year: int,
    *,
    pattern: str = "CHN_Maize_{stage}_{year}.tif",
) -> dict[str, Path]:
    root = Path(directory)
    return {
        stage.lower(): root / pattern.format(stage=stage.upper(), year=int(year))
        for stage in PHENOLOGY_STAGES
    }


def aggregate_phenology_year(
    crosswalk: pd.DataFrame,
    year: int,
    directory: str | Path,
    *,
    source_crs: str | CRS = CHINA_MAIZE_ALBERS,
    pattern: str = "CHN_Maize_{stage}_{year}.tif",
    spec: TargetGridSpec = TARGET_GRID,
    row_chunk_size: int = 128,
) -> pd.DataFrame:
    """Read, geolocate, jointly validate, and aggregate one phenology year."""

    paths = phenology_year_paths(directory, year, pattern=pattern)
    arrays: dict[str, np.ndarray] = {}
    metadata: dict[str, GeoTiffGrid] = {}
    for stage, path in paths.items():
        if not path.is_file():
            raise FileNotFoundError(path)
        arrays[stage], metadata[stage] = read_phenology_tiff(path)
    aligned, union_metadata = align_stage_rasters(arrays, metadata)
    membership = build_pixel_membership(
        union_metadata,
        crosswalk,
        source_crs=source_crs,
        spec=spec,
        row_chunk_size=row_chunk_size,
    )
    output = aggregate_phenology_arrays(aligned, membership, crosswalk)
    output.insert(output.columns.get_loc("grid_id_v3") + 1, "year", int(year))
    return add_phenology_windows(output)


def build_phenology_panel(
    crosswalk: pd.DataFrame,
    years: Iterable[int],
    directory: str | Path,
    *,
    source_crs: str | CRS = CHINA_MAIZE_ALBERS,
    pattern: str = "CHN_Maize_{stage}_{year}.tif",
    spec: TargetGridSpec = TARGET_GRID,
    row_chunk_size: int = 128,
) -> pd.DataFrame:
    """Build a balanced selected-cell phenology panel without temporal filling."""

    year_values = tuple(int(year) for year in years)
    if not year_values or len(set(year_values)) != len(year_values):
        raise ValueError("years must be a non-empty unique sequence")
    frames = [
        aggregate_phenology_year(
            crosswalk,
            year,
            directory,
            source_crs=source_crs,
            pattern=pattern,
            spec=spec,
            row_chunk_size=row_chunk_size,
        )
        for year in year_values
    ]
    panel = pd.concat(frames, ignore_index=True)
    panel = panel.sort_values(["era01_cell_id", "year"]).reset_index(drop=True)
    if len(panel) != len(crosswalk) * len(year_values):
        raise AssertionError("Phenology panel is not balanced")
    if panel.duplicated(["era01_cell_id", "year"]).any():
        raise AssertionError("Phenology panel contains duplicate grid-years")
    return panel


def add_phenology_windows(frame: pd.DataFrame) -> pd.DataFrame:
    """Add six clipped closed windows and compute lengths after clipping."""

    required = {"year", "v3_doy", "he_doy", "ma_doy"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Phenology frame is missing columns: {missing}")
    output = frame.copy()
    n_rows = len(output)
    for window in WINDOW_NAMES:
        for part in ("start", "end", "days"):
            output[f"win_{window}_{part}"] = pd.array([pd.NA] * n_rows, dtype="Int16")

    years = pd.to_numeric(output["year"], errors="raise").to_numpy(dtype=np.int64)
    v3 = pd.to_numeric(output["v3_doy"], errors="coerce").to_numpy(dtype=np.float64)
    he = pd.to_numeric(output["he_doy"], errors="coerce").to_numpy(dtype=np.float64)
    ma = pd.to_numeric(output["ma_doy"], errors="coerce").to_numpy(dtype=np.float64)

    for year in np.unique(years):
        positions = np.flatnonzero(years == year)
        final_day = 366 if calendar.isleap(int(year)) else 365
        valid = (
            np.isfinite(v3[positions])
            & np.isfinite(he[positions])
            & np.isfinite(ma[positions])
            & (v3[positions] >= 1)
            & (ma[positions] <= 366)
            & (v3[positions] < he[positions])
            & (he[positions] < ma[positions])
        )
        valid_positions = positions[valid]
        if valid_positions.size == 0:
            continue
        local_v3 = v3[valid_positions].astype(np.int64)
        local_he = he[valid_positions].astype(np.int64)
        local_ma = ma[valid_positions].astype(np.int64)
        definitions = {
            "full": (local_v3 - 30, local_ma),
            "v3pre30": (local_v3 - 30, local_v3),
            "v3pm10": (local_v3 - 10, local_v3 + 10),
            "hepm10": (local_he - 10, local_he + 10),
            "v3he": (local_v3, local_he),
            "hema": (local_he, local_ma),
        }
        for window, (raw_start, raw_end) in definitions.items():
            start = np.clip(raw_start, 1, final_day).astype(np.int16)
            end = np.clip(raw_end, 1, final_day).astype(np.int16)
            days = (end.astype(np.int32) - start.astype(np.int32) + 1).astype(np.int16)
            output.loc[output.index[valid_positions], f"win_{window}_start"] = start
            output.loc[output.index[valid_positions], f"win_{window}_end"] = end
            output.loc[output.index[valid_positions], f"win_{window}_days"] = days
    return output
