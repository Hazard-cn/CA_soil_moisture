"""
Build the GGCP10 harvested-area branch using area-preserving aggregation from
the native 1/12-degree raster grid to the existing 0.1-degree panel grid.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import rasterio


PROJ_DIR = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
RUN_DIR = PROJ_DIR / "temp" / "2026-05-18_ggcp10_harvarea_agg_baseline_suite"
RAW_DIR = (
    PROJ_DIR
    / "data_build"
    / "data"
    / "raw"
    / "GGCP10_HarvArea_2010-2020"
    / "GGCP10_HarvArea_2010-2020"
)
V3_READY = PROJ_DIR / "data" / "processed" / "v3_analysis_ready.dta"
MASTER_CSV = Path(
    "C:/YangSu/00_Project/CA_mechanism/data/master/"
    "data_v1_with_climate_with_county_city.csv"
)

YEARS = [2016, 2017, 2018, 2019]
TIFF_TEMPLATE = "HarvArea_Maize_{year}.tif"
TARGET_RES = 0.1

SIDE_CAR_CSV = RUN_DIR / "ggcp10_harvarea_agg_sidecar.csv"
SIDE_CAR_DTA = RUN_DIR / "ggcp10_harvarea_agg_sidecar.dta"
HARV_READY_DTA = RUN_DIR / "v3_analysis_ready_ggcp10_harvarea_agg.dta"
DIAG_CSV = RUN_DIR / "ggcp10_harvarea_agg_diagnostics.csv"
YIELD_DIAG_CSV = RUN_DIR / "ggcp10_yield_aggregation_diagnostics.csv"
SAMPLE_COMPARE_CSV = RUN_DIR / "ggcp10_harvarea_agg_sample_comparison.csv"


def add_coord_keys(df: pd.DataFrame) -> pd.DataFrame:
    keyed = df.copy()
    keyed["lat_key"] = (keyed["latitude"] * 100).round().astype("int64")
    keyed["lon_key"] = (keyed["longitude"] * 100).round().astype("int64")
    return keyed


def overlap_weights(
    target_centers: np.ndarray,
    source_edges: np.ndarray,
    axis: str,
) -> tuple[np.ndarray, np.ndarray]:
    target_edges_lo = target_centers - TARGET_RES / 2
    target_edges_hi = target_centers + TARGET_RES / 2
    used = np.where(
        (source_edges[1:] > target_edges_lo.min())
        & (source_edges[:-1] < target_edges_hi.max())
    )[0]
    src_lo = source_edges[used]
    src_hi = source_edges[used + 1]

    weights = np.zeros((len(target_centers), len(used)), dtype="float64")
    for i, (lo, hi) in enumerate(zip(target_edges_lo, target_edges_hi)):
        overlap_lo = np.maximum(lo, src_lo)
        overlap_hi = np.minimum(hi, src_hi)
        valid = overlap_hi > overlap_lo
        if axis == "lon":
            numer = overlap_hi[valid] - overlap_lo[valid]
            denom = src_hi[valid] - src_lo[valid]
        elif axis == "lat":
            numer = (
                np.sin(np.deg2rad(overlap_hi[valid]))
                - np.sin(np.deg2rad(overlap_lo[valid]))
            )
            denom = (
                np.sin(np.deg2rad(src_hi[valid]))
                - np.sin(np.deg2rad(src_lo[valid]))
            )
        else:
            raise ValueError(f"Unsupported axis: {axis}")
        weights[i, valid] = numer / denom

    return used, weights


def build_grid_weights(
    base: pd.DataFrame,
    src_width: int,
    src_height: int,
) -> dict[str, object]:
    target_lons = np.sort(base["longitude"].drop_duplicates().to_numpy(dtype="float64"))
    target_lats = np.sort(base["latitude"].drop_duplicates().to_numpy(dtype="float64"))
    src_lon_edges = np.linspace(-180.0, 180.0, src_width + 1)
    src_lat_edges = np.linspace(-90.0, 90.0, src_height + 1)

    lon_used, lon_weights = overlap_weights(target_lons, src_lon_edges, "lon")
    lat_used, lat_weights = overlap_weights(target_lats, src_lat_edges, "lat")

    lon_lookup = {round(float(v), 6): i for i, v in enumerate(target_lons)}
    lat_lookup = {round(float(v), 6): i for i, v in enumerate(target_lats)}

    return {
        "target_lons": target_lons,
        "target_lats": target_lats,
        "lon_used": lon_used,
        "lat_used": lat_used,
        "lon_weights": lon_weights,
        "lat_weights": lat_weights,
        "lon_lookup": lon_lookup,
        "lat_lookup": lat_lookup,
    }


def aggregate_year_area(
    panel_year: pd.DataFrame,
    year: int,
    grid_weights: dict[str, object],
) -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    tif_path = RAW_DIR / TIFF_TEMPLATE.format(year=year)
    if not tif_path.exists():
        raise FileNotFoundError(f"Missing GGCP10 GeoTIFF: {tif_path}")

    with rasterio.open(tif_path) as src:
        if src.crs is None or src.crs.to_string() != "EPSG:4326":
            raise ValueError(f"Unexpected CRS for {tif_path}: {src.crs}")
        if src.nodata != -9999:
            raise ValueError(f"Unexpected nodata for {tif_path}: {src.nodata}")

        raw = src.read(1).astype("float64")
        raw[np.isclose(raw, src.nodata)] = np.nan
        raw_bottom_up = raw[::-1, :]

        lat_used = grid_weights["lat_used"]
        lon_used = grid_weights["lon_used"]
        lat_weights = grid_weights["lat_weights"]
        lon_weights = grid_weights["lon_weights"]

        subset = raw_bottom_up[np.ix_(lat_used, lon_used)]
        valid = np.isfinite(subset).astype("float64")
        subset0 = np.nan_to_num(subset, nan=0.0)

        agg_grid = lat_weights @ subset0 @ lon_weights.T
        coverage_grid = lat_weights @ valid @ lon_weights.T

        lat_lookup = grid_weights["lat_lookup"]
        lon_lookup = grid_weights["lon_lookup"]
        row_idx = np.array(
            [lat_lookup[round(float(v), 6)] for v in panel_year["latitude"]],
            dtype="int64",
        )
        col_idx = np.array(
            [lon_lookup[round(float(v), 6)] for v in panel_year["longitude"]],
            dtype="int64",
        )
        aggregated = agg_grid[row_idx, col_idx]
        coverage = coverage_grid[row_idx, col_idx]
        aggregated[coverage <= 0] = np.nan

        point_sampled = np.fromiter(
            (float(value[0]) for value in src.sample(zip(panel_year["longitude"], panel_year["latitude"]))),
            dtype="float64",
            count=len(panel_year),
        )
        point_sampled[np.isclose(point_sampled, src.nodata)] = np.nan

        meta = {
            "year": year,
            "tif_name": tif_path.name,
            "raster_width": src.width,
            "raster_height": src.height,
            "raster_res_x": src.res[0],
            "raster_res_y": src.res[1],
            "raster_nodata": src.nodata,
            "source_subset_rows": int(len(lat_used)),
            "source_subset_cols": int(len(lon_used)),
            "target_unique_lats": int(len(grid_weights["target_lats"])),
            "target_unique_lons": int(len(grid_weights["target_lons"])),
        }

    return aggregated, point_sampled, meta


def build_sidecar(base: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    with rasterio.open(RAW_DIR / TIFF_TEMPLATE.format(year=YEARS[0])) as src:
        grid_weights = build_grid_weights(base, src.width, src.height)

    parts: list[pd.DataFrame] = []
    diagnostics: list[dict[str, object]] = []

    for year in YEARS:
        panel_year = base.loc[
            base["year"] == year,
            ["grid_id", "year", "latitude", "longitude"],
        ].copy()
        aggregated, point_sampled, meta = aggregate_year_area(panel_year, year, grid_weights)
        panel_year["ggcp10_harvarea_thousand_ha"] = aggregated
        panel_year["ggcp10_point_harvarea_thousand_ha"] = point_sampled
        panel_year["ggcp10_maize_area_km2"] = aggregated * 10.0
        panel_year["ggcp10_point_maize_area_km2"] = point_sampled * 10.0
        panel_year["ggcp10_area_valid"] = panel_year["ggcp10_maize_area_km2"].notna()
        panel_year["ggcp10_area_positive"] = panel_year["ggcp10_maize_area_km2"] > 0

        diagnostics.append(
            {
                **meta,
                "rows": int(len(panel_year)),
                "valid_area_rows": int(panel_year["ggcp10_area_valid"].sum()),
                "positive_area_rows": int(panel_year["ggcp10_area_positive"].sum()),
                "missing_area_rows": int(panel_year["ggcp10_maize_area_km2"].isna().sum()),
                "zero_area_rows": int((panel_year["ggcp10_maize_area_km2"] == 0).sum()),
                "agg_area_mean_km2": float(panel_year["ggcp10_maize_area_km2"].mean()),
                "point_area_mean_km2": float(panel_year["ggcp10_point_maize_area_km2"].mean()),
                "agg_to_point_mean_ratio": float(
                    panel_year["ggcp10_maize_area_km2"].mean()
                    / panel_year["ggcp10_point_maize_area_km2"].mean()
                ),
                "agg_area_sum_km2": float(panel_year["ggcp10_maize_area_km2"].sum()),
                "point_area_sum_km2": float(panel_year["ggcp10_point_maize_area_km2"].sum()),
                "min_area_km2": float(panel_year["ggcp10_maize_area_km2"].min()),
                "max_area_km2": float(panel_year["ggcp10_maize_area_km2"].max()),
            }
        )
        parts.append(panel_year)

    sidecar = pd.concat(parts, ignore_index=True)
    if sidecar.duplicated(["grid_id", "year"]).any():
        dup_n = int(sidecar.duplicated(["grid_id", "year"]).sum())
        raise ValueError(f"Duplicate grid-year keys in GGCP10 sidecar: {dup_n}")

    return sidecar, pd.DataFrame(diagnostics)


def load_maize_prod() -> pd.DataFrame:
    source = pd.read_csv(
        MASTER_CSV,
        encoding="gbk",
        usecols=["year", "latitude", "longitude", "maize_prod"],
    )
    source = add_coord_keys(source)
    if source.duplicated(["year", "lat_key", "lon_key"]).any():
        dup_n = int(source.duplicated(["year", "lat_key", "lon_key"]).sum())
        raise ValueError(f"Duplicate source maize_prod keys: {dup_n}")
    return source[["year", "lat_key", "lon_key", "maize_prod"]]


def build_branch(
    base: pd.DataFrame,
    sidecar: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    branch = add_coord_keys(base)
    source_prod = load_maize_prod()
    branch = branch.merge(
        sidecar[
            [
                "grid_id",
                "year",
                "ggcp10_maize_area_km2",
                "ggcp10_point_maize_area_km2",
            ]
        ],
        on=["grid_id", "year"],
        how="left",
        validate="1:1",
    )
    branch = branch.merge(
        source_prod,
        on=["year", "lat_key", "lon_key"],
        how="left",
        validate="1:1",
    )

    branch["orig_maize_area_km2"] = branch["maize_area_km2"]
    branch["orig_yield_tons_ha"] = branch["yield_tons_ha"]
    branch["orig_ln_yield"] = branch["ln_yield"]
    branch["orig_main_sample"] = branch["main_sample"]
    branch["point_yield_tons_ha"] = (
        branch["maize_prod"] / branch["ggcp10_point_maize_area_km2"] * 10.0
    )

    branch["maize_area_km2"] = branch["ggcp10_maize_area_km2"]
    branch["ggcp10_maize_frac"] = branch["maize_area_km2"] / branch["pixel_area_km2"]
    branch["maize_yield_km2"] = branch["maize_prod"] / branch["maize_area_km2"]
    branch.loc[branch["maize_area_km2"] <= 0, "maize_yield_km2"] = np.nan
    branch["yield_tons_ha"] = branch["maize_yield_km2"] * 10.0
    branch.loc[branch["yield_tons_ha"] <= 0, "yield_tons_ha"] = np.nan
    branch["ln_yield"] = np.log(branch["yield_tons_ha"])
    branch["ggcp10_harvarea_valid"] = (
        branch["maize_area_km2"].notna()
        & (branch["maize_area_km2"] > 0)
        & branch["maize_prod"].notna()
        & branch["yield_tons_ha"].notna()
    )
    branch["main_sample"] = (
        (branch["orig_main_sample"] == 1) & branch["ggcp10_harvarea_valid"]
    ).astype("int8")

    if branch["maize_prod"].isna().any():
        missing_prod = int(branch["maize_prod"].isna().sum())
        raise ValueError(f"Missing maize_prod after source merge: {missing_prod}")

    compare_rows: list[dict[str, object]] = []
    yield_rows: list[dict[str, object]] = []
    for year, grp in branch.groupby("year", sort=True):
        compare_rows.append(
            {
                "year": int(year),
                "rows": int(len(grp)),
                "old_main_sample_rows": int((grp["orig_main_sample"] == 1).sum()),
                "new_main_sample_rows": int((grp["main_sample"] == 1).sum()),
                "positive_ggcp10_area_rows": int((grp["maize_area_km2"] > 0).sum()),
                "missing_ggcp10_area_rows": int(grp["maize_area_km2"].isna().sum()),
                "old_area_mean_km2": float(grp["orig_maize_area_km2"].mean()),
                "agg_area_mean_km2": float(grp["maize_area_km2"].mean()),
                "point_area_mean_km2": float(grp["ggcp10_point_maize_area_km2"].mean()),
                "old_yield_mean_tons_ha": float(grp["orig_yield_tons_ha"].mean()),
                "agg_yield_mean_tons_ha": float(grp["yield_tons_ha"].mean()),
                "point_yield_mean_tons_ha": float(grp["point_yield_tons_ha"].mean()),
            }
        )

        for label, col in [
            ("old", "orig_yield_tons_ha"),
            ("point_sample", "point_yield_tons_ha"),
            ("aggregated", "yield_tons_ha"),
        ]:
            vals = grp[col].dropna()
            yield_rows.append(
                {
                    "year": int(year),
                    "series": label,
                    "n": int(vals.shape[0]),
                    "mean": float(vals.mean()),
                    "p50": float(vals.quantile(0.50)),
                    "p90": float(vals.quantile(0.90)),
                    "p99": float(vals.quantile(0.99)),
                    "p999": float(vals.quantile(0.999)),
                    "max": float(vals.max()),
                    "gt20_tons_ha": int((vals > 20).sum()),
                    "gt50_tons_ha": int((vals > 50).sum()),
                    "gt100_tons_ha": int((vals > 100).sum()),
                }
            )

    compare = pd.DataFrame(compare_rows)
    yield_diag = pd.DataFrame(yield_rows)
    branch = branch.drop(columns=["lat_key", "lon_key"])
    return branch, compare, yield_diag


def validate_branch(branch: pd.DataFrame) -> None:
    frac_diff = (
        branch["ggcp10_maize_frac"]
        - branch["maize_area_km2"] / branch["pixel_area_km2"]
    ).abs()
    yield_km2_diff = (
        branch["maize_yield_km2"]
        - branch["maize_prod"] / branch["maize_area_km2"]
    ).abs()
    yield_diff = (branch["yield_tons_ha"] - branch["maize_yield_km2"] * 10.0).abs()
    log_diff = (branch["ln_yield"] - np.log(branch["yield_tons_ha"])).abs()

    checks = {
        "grid_year_unique": not branch.duplicated(["grid_id", "year"]).any(),
        "frac_identity": float(frac_diff.max(skipna=True)) < 1e-12,
        "yield_km2_identity": float(yield_km2_diff.max(skipna=True)) < 1e-12,
        "yield_identity": float(yield_diff.max(skipna=True)) < 1e-12,
        "log_identity": float(log_diff.max(skipna=True)) < 1e-12,
        "main_sample_requires_valid_area": bool(
            ((branch["main_sample"] == 1) <= branch["ggcp10_harvarea_valid"]).all()
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"GGCP10 aggregated branch validation failed: {failed}")


def write_stata(df: pd.DataFrame, path: Path) -> None:
    out = df.copy()
    object_cols = out.select_dtypes(include=["object"]).columns
    for col in object_cols:
        out[col] = out[col].fillna("").astype(str)
    out.to_stata(path, write_index=False, version=118)


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    base = pd.read_stata(V3_READY, convert_categoricals=False)
    sidecar, diagnostics = build_sidecar(base)
    branch, sample_compare, yield_diag = build_branch(base, sidecar)
    validate_branch(branch)

    sidecar.to_csv(SIDE_CAR_CSV, index=False)
    diagnostics.to_csv(DIAG_CSV, index=False)
    sample_compare.to_csv(SAMPLE_COMPARE_CSV, index=False)
    yield_diag.to_csv(YIELD_DIAG_CSV, index=False)
    write_stata(sidecar, SIDE_CAR_DTA)
    write_stata(branch, HARV_READY_DTA)

    print(f"Saved sidecar: {SIDE_CAR_CSV}")
    print(f"Saved sidecar dta: {SIDE_CAR_DTA}")
    print(f"Saved branch dta: {HARV_READY_DTA}")
    print(f"Saved diagnostics: {DIAG_CSV}")
    print(f"Saved sample comparison: {SAMPLE_COMPARE_CSV}")
    print(f"Saved yield diagnostics: {YIELD_DIAG_CSV}")
    print(
        f"Rows: {len(branch):,}; "
        f"main sample after GGCP10 aggregation: {int(branch['main_sample'].sum()):,}"
    )


if __name__ == "__main__":
    main()
