"""
Build the independent GGCP10 harvested-area branch used by the v6gleambl rerun.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import rasterio


PROJ_DIR = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
RUN_DIR = PROJ_DIR / "temp" / "2026-05-18_ggcp10_harvarea_v6gleambl"
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
SIDE_CAR_CSV = RUN_DIR / "ggcp10_harvarea_sidecar.csv"
SIDE_CAR_DTA = RUN_DIR / "ggcp10_harvarea_sidecar.dta"
HARV_READY_DTA = RUN_DIR / "v3_analysis_ready_ggcp10_harvarea.dta"
DIAG_CSV = RUN_DIR / "ggcp10_harvarea_diagnostics.csv"
SAMPLE_COMPARE_CSV = RUN_DIR / "ggcp10_harvarea_sample_comparison.csv"


def add_coord_keys(df: pd.DataFrame) -> pd.DataFrame:
    keyed = df.copy()
    keyed["lat_key"] = (keyed["latitude"] * 100).round().astype("int64")
    keyed["lon_key"] = (keyed["longitude"] * 100).round().astype("int64")
    return keyed


def sample_year_area(panel_year: pd.DataFrame, year: int) -> tuple[np.ndarray, dict[str, object]]:
    tif_path = RAW_DIR / TIFF_TEMPLATE.format(year=year)
    if not tif_path.exists():
        raise FileNotFoundError(f"Missing GGCP10 GeoTIFF: {tif_path}")

    with rasterio.open(tif_path) as src:
        if src.crs is None or src.crs.to_string() != "EPSG:4326":
            raise ValueError(f"Unexpected CRS for {tif_path}: {src.crs}")
        if src.nodata != -9999:
            raise ValueError(f"Unexpected nodata for {tif_path}: {src.nodata}")

        coords = list(zip(panel_year["longitude"], panel_year["latitude"]))
        sampled = np.fromiter(
            (float(value[0]) for value in src.sample(coords)),
            dtype="float64",
            count=len(coords),
        )
        sampled[np.isclose(sampled, src.nodata)] = np.nan

        meta = {
            "year": year,
            "tif_name": tif_path.name,
            "raster_width": src.width,
            "raster_height": src.height,
            "raster_res_x": src.res[0],
            "raster_res_y": src.res[1],
            "raster_nodata": src.nodata,
            "raw_min_thousand_ha": float(np.nanmin(sampled)),
            "raw_max_thousand_ha": float(np.nanmax(sampled)),
        }

    return sampled, meta


def build_sidecar(base: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    parts: list[pd.DataFrame] = []
    diagnostics: list[dict[str, object]] = []

    for year in YEARS:
        panel_year = base.loc[
            base["year"] == year,
            ["grid_id", "year", "latitude", "longitude"],
        ].copy()
        sampled, meta = sample_year_area(panel_year, year)
        panel_year["ggcp10_harvarea_thousand_ha"] = sampled
        panel_year["ggcp10_maize_area_km2"] = sampled * 10.0
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


def build_branch(base: pd.DataFrame, sidecar: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    branch = add_coord_keys(base)
    source_prod = load_maize_prod()
    branch = branch.merge(
        sidecar[["grid_id", "year", "ggcp10_maize_area_km2"]],
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
                "new_area_mean_km2": float(grp["maize_area_km2"].mean()),
                "old_yield_mean_tons_ha": float(grp["orig_yield_tons_ha"].mean()),
                "new_yield_mean_tons_ha": float(grp["yield_tons_ha"].mean()),
            }
        )

    compare = pd.DataFrame(compare_rows)
    branch = branch.drop(columns=["lat_key", "lon_key"])
    return branch, compare


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
        raise ValueError(f"GGCP10 branch validation failed: {failed}")


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
    branch, sample_compare = build_branch(base, sidecar)
    validate_branch(branch)

    sidecar.to_csv(SIDE_CAR_CSV, index=False)
    diagnostics.to_csv(DIAG_CSV, index=False)
    sample_compare.to_csv(SAMPLE_COMPARE_CSV, index=False)
    write_stata(sidecar, SIDE_CAR_DTA)
    write_stata(branch, HARV_READY_DTA)

    print(f"Saved sidecar: {SIDE_CAR_CSV}")
    print(f"Saved sidecar dta: {SIDE_CAR_DTA}")
    print(f"Saved branch dta: {HARV_READY_DTA}")
    print(f"Saved diagnostics: {DIAG_CSV}")
    print(f"Saved sample comparison: {SAMPLE_COMPARE_CSV}")
    print(
        f"Rows: {len(branch):,}; "
        f"main sample after GGCP10 update: {int(branch['main_sample'].sum()):,}"
    )


if __name__ == "__main__":
    main()
