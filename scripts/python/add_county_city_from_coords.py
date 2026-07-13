from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

try:
    import geopandas as gpd
    import pandas as pd
except ImportError as exc:  # pragma: no cover - dependency validation happens at runtime
    missing = exc.name or "unknown"
    raise SystemExit(
        "Missing dependency: "
        f"{missing}. Install pandas/geopandas/pyogrio/shapely/pyproj/rtree in the project .venv first."
    ) from exc


PROJ = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = Path(r"C:\YangSu\00_Project\CA_mechanism\data\master\data_v1_with_climate.csv")
DEFAULT_COUNTY_SHP = Path(
    r"C:\YangSu\00_Project\county-temp-rain\data\raw\2019年中国各级行政区划\2019年中国各级行政区划\2019行政区划\县.shp"
)
DEFAULT_CITY_SHP = Path(
    r"C:\YangSu\00_Project\county-temp-rain\data\raw\2019年中国各级行政区划\2019年中国各级行政区划\2019行政区划\市.shp"
)
DEFAULT_OUTPUT = Path(
    r"C:\YangSu\00_Project\CA_mechanism\data\master\data_v1_with_climate_with_county_city.csv"
)
LOGDIR = PROJ / "output" / "logs"

CSV_ENCODING = "gb18030"
SHP_ENCODING = "utf-8"
POINT_CRS = "EPSG:4326"
DISTANCE_CRS = "EPSG:3857"
NEW_FIELDS = ["county_name", "county_code", "city_name", "city_code"]


@dataclass
class MatchStats:
    total_rows: int
    unique_coords: int
    exact_county_matches: int
    city_hint_matches: int
    nearest_within_city_matches: int
    nearest_global_matches: int
    unmatched_count: int


class RunLogger:
    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.log_path.open("w", encoding="utf-8", newline="")

    def log(self, message: str) -> None:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{stamp}] {message}"
        print(line)
        self._fh.write(line + "\n")
        self._fh.flush()

    def close(self) -> None:
        self._fh.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Match latitude/longitude points to 2019 Chinese county and city polygons."
    )
    parser.add_argument("--input-csv", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--county-shp", type=Path, default=DEFAULT_COUNTY_SHP)
    parser.add_argument("--city-shp", type=Path, default=DEFAULT_CITY_SHP)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def normalize_text(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    text = str(value).strip()
    return text if text else pd.NA


def normalize_code(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    text = str(value).strip()
    if not text:
        return pd.NA
    try:
        number = float(text)
    except ValueError:
        return text
    if number.is_integer():
        return str(int(number))
    return text.rstrip("0").rstrip(".")


def require_paths(paths: Iterable[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Required path(s) not found:\n" + "\n".join(missing))


def dedupe_spatial_result(df: pd.DataFrame, stage: str, logger: RunLogger) -> pd.DataFrame:
    if df.empty:
        return df
    if "distance_m" in df.columns:
        sort_cols = ["coord_key", "distance_m", "county_code"]
    else:
        sort_cols = ["coord_key", "county_code"] if "county_code" in df.columns else ["coord_key"]
    df = df.sort_values(sort_cols, na_position="last").copy()
    duplicate_rows = int(df.duplicated(subset=["coord_key"], keep=False).sum())
    if duplicate_rows:
        logger.log(
            f"{stage}: detected {duplicate_rows} duplicated join rows; retaining the first match per coord_key."
        )
    return df.drop_duplicates(subset=["coord_key"], keep="first").copy()


def load_unique_coords(input_csv: Path, logger: RunLogger) -> tuple[pd.DataFrame, int]:
    logger.log(f"Loading coordinate columns from {input_csv}")
    header = pd.read_csv(input_csv, encoding=CSV_ENCODING, nrows=0).columns.tolist()
    required = {"latitude", "longitude"}
    missing = sorted(required - set(header))
    if missing:
        raise ValueError(f"Input CSV is missing required columns: {missing}")

    coords = pd.read_csv(
        input_csv,
        encoding=CSV_ENCODING,
        usecols=["latitude", "longitude"],
        dtype={"latitude": "string", "longitude": "string"},
        low_memory=False,
    ).rename(columns={"latitude": "latitude_str", "longitude": "longitude_str"})

    total_rows = len(coords)
    coords["latitude_str"] = coords["latitude_str"].astype("string").str.strip()
    coords["longitude_str"] = coords["longitude_str"].astype("string").str.strip()

    missing_mask = (
        coords["latitude_str"].isna()
        | coords["longitude_str"].isna()
        | coords["latitude_str"].eq("")
        | coords["longitude_str"].eq("")
    )
    if missing_mask.any():
        raise ValueError(f"Found {int(missing_mask.sum())} rows with missing latitude/longitude.")

    unique_coords = coords.drop_duplicates(subset=["latitude_str", "longitude_str"]).copy()
    unique_coords["latitude"] = pd.to_numeric(unique_coords["latitude_str"], errors="coerce")
    unique_coords["longitude"] = pd.to_numeric(unique_coords["longitude_str"], errors="coerce")

    invalid_mask = unique_coords["latitude"].isna() | unique_coords["longitude"].isna()
    if invalid_mask.any():
        bad_rows = unique_coords.loc[invalid_mask, ["latitude_str", "longitude_str"]].head(5)
        raise ValueError(
            "Found non-numeric latitude/longitude values in unique coordinates. "
            f"Sample:\n{bad_rows.to_string(index=False)}"
        )

    unique_coords["coord_key"] = unique_coords["latitude_str"] + "|" + unique_coords["longitude_str"]
    logger.log(f"Input rows: {total_rows}; unique coordinates: {len(unique_coords)}")
    return unique_coords[["coord_key", "latitude_str", "longitude_str", "latitude", "longitude"]], total_rows


def load_admin_layers(
    county_shp: Path,
    city_shp: Path,
    logger: RunLogger,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    logger.log(f"Loading county polygons from {county_shp}")
    county = gpd.read_file(county_shp, encoding=SHP_ENCODING, engine="pyogrio")
    logger.log(f"Loading city polygons from {city_shp}")
    city = gpd.read_file(city_shp, encoding=SHP_ENCODING, engine="pyogrio")

    county_required = ["PAC", "NAME", "市代码", "市", "geometry"]
    city_required = ["市代码", "市", "geometry"]
    county_missing = [col for col in county_required if col not in county.columns]
    city_missing = [col for col in city_required if col not in city.columns]
    if county_missing:
        raise ValueError(f"County shapefile is missing fields: {county_missing}")
    if city_missing:
        raise ValueError(f"City shapefile is missing fields: {city_missing}")

    county = county[county_required].copy().rename(
        columns={"PAC": "county_code", "NAME": "county_name", "市代码": "city_code", "市": "city_name"}
    )
    city = city[city_required].copy().rename(columns={"市代码": "city_code", "市": "city_name"})

    county["county_code"] = county["county_code"].map(normalize_code)
    county["city_code"] = county["city_code"].map(normalize_code)
    county["county_name"] = county["county_name"].map(normalize_text)
    county["city_name"] = county["city_name"].map(normalize_text)

    city["city_code"] = city["city_code"].map(normalize_code)
    city["city_name"] = city["city_name"].map(normalize_text)

    county = county[county["geometry"].notna()].copy()
    city = city[city["geometry"].notna()].copy()

    county = county.to_crs(POINT_CRS)
    city = city.to_crs(POINT_CRS)

    logger.log(f"County polygons loaded: {len(county)}")
    logger.log(f"City polygons loaded: {len(city)}")
    return county, city


def build_points_gdf(unique_coords: pd.DataFrame) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        unique_coords.copy(),
        geometry=gpd.points_from_xy(unique_coords["longitude"], unique_coords["latitude"]),
        crs=POINT_CRS,
    )


def match_points(
    points: gpd.GeoDataFrame,
    county: gpd.GeoDataFrame,
    city: gpd.GeoDataFrame,
    logger: RunLogger,
) -> tuple[pd.DataFrame, MatchStats]:
    logger.log("Running exact county polygon match with predicate=within")
    county_join = gpd.sjoin(
        points[["coord_key", "geometry"]],
        county,
        how="left",
        predicate="within",
    )
    county_join = dedupe_spatial_result(county_join, "county within", logger)
    exact_matches = county_join[county_join["county_code"].notna()][
        ["coord_key", "county_name", "county_code", "city_name", "city_code"]
    ].copy()
    exact_matches["match_method"] = "county_within"

    matched_keys = set(exact_matches["coord_key"])
    unmatched_points = points[~points["coord_key"].isin(matched_keys)].copy()
    logger.log(
        f"Exact county matches: {len(exact_matches)}; county-unmatched coordinates: {len(unmatched_points)}"
    )

    city_hint_count = 0
    nearest_city_count = 0
    nearest_global_count = 0
    fallback_matches = pd.DataFrame(
        columns=["coord_key", "county_name", "county_code", "city_name", "city_code", "match_method", "distance_m"]
    )

    if not unmatched_points.empty:
        logger.log("Running city polygon match to constrain nearest-county fallback")
        city_join = gpd.sjoin(
            unmatched_points[["coord_key", "geometry"]],
            city,
            how="left",
            predicate="within",
        )
        city_join = dedupe_spatial_result(city_join, "city within", logger)
        city_hints = city_join[["coord_key", "city_code", "city_name"]].copy()
        city_hint_count = int(city_hints["city_code"].notna().sum())
        logger.log(
            f"City hints available for county-unmatched coordinates: {city_hint_count} / {len(unmatched_points)}"
        )

        fallback_points = unmatched_points.merge(city_hints, on="coord_key", how="left")
        fallback_points = gpd.GeoDataFrame(fallback_points, geometry="geometry", crs=POINT_CRS)

        county_3857 = county.to_crs(DISTANCE_CRS)
        fallback_points_3857 = fallback_points.to_crs(DISTANCE_CRS)

        nearest_frames: list[pd.DataFrame] = []

        city_scoped_points = fallback_points_3857[fallback_points_3857["city_code"].notna()].copy()
        global_points = fallback_points_3857[fallback_points_3857["city_code"].isna()].copy()

        for hint_city_code, group in city_scoped_points.groupby("city_code", dropna=False):
            candidate_counties = county_3857[county_3857["city_code"] == hint_city_code].copy()
            if candidate_counties.empty:
                global_points = pd.concat([global_points, group], ignore_index=False)
                continue
            joined = gpd.sjoin_nearest(
                group[["coord_key", "geometry"]],
                candidate_counties,
                how="left",
                distance_col="distance_m",
            )
            joined = dedupe_spatial_result(joined, f"nearest county within city {hint_city_code}", logger)
            joined["match_method"] = "nearest_within_city"
            nearest_frames.append(
                joined[["coord_key", "county_name", "county_code", "city_name", "city_code", "match_method", "distance_m"]]
            )

        if not global_points.empty:
            joined = gpd.sjoin_nearest(
                global_points[["coord_key", "geometry"]],
                county_3857,
                how="left",
                distance_col="distance_m",
            )
            joined = dedupe_spatial_result(joined, "nearest county global", logger)
            joined["match_method"] = "nearest_global"
            nearest_frames.append(
                joined[["coord_key", "county_name", "county_code", "city_name", "city_code", "match_method", "distance_m"]]
            )

        if nearest_frames:
            fallback_matches = pd.concat(nearest_frames, ignore_index=True)
            fallback_matches = dedupe_spatial_result(fallback_matches, "fallback combined", logger)
            nearest_city_count = int((fallback_matches["match_method"] == "nearest_within_city").sum())
            nearest_global_count = int((fallback_matches["match_method"] == "nearest_global").sum())
            logger.log(
                "Fallback matches completed: "
                f"nearest_within_city={nearest_city_count}, nearest_global={nearest_global_count}"
            )

    all_matches = pd.concat([exact_matches, fallback_matches], ignore_index=True)
    all_matches = dedupe_spatial_result(all_matches, "all matches", logger)

    for field in NEW_FIELDS:
        if field not in all_matches.columns:
            all_matches[field] = pd.NA

    all_matches["county_code"] = all_matches["county_code"].map(normalize_code)
    all_matches["city_code"] = all_matches["city_code"].map(normalize_code)
    all_matches["county_name"] = all_matches["county_name"].map(normalize_text)
    all_matches["city_name"] = all_matches["city_name"].map(normalize_text)

    unmatched_keys = sorted(set(points["coord_key"]) - set(all_matches["coord_key"]))
    unmatched_count = len(unmatched_keys)
    if unmatched_keys:
        logger.log(f"Unmatched coordinates after fallback: {unmatched_count}")
        for sample_key in unmatched_keys[:10]:
            logger.log(f"Unmatched sample: {sample_key}")
    else:
        logger.log("All unique coordinates received a county/city match.")

    incomplete_matches = all_matches[NEW_FIELDS].isna().any(axis=1)
    if incomplete_matches.any():
        sample = all_matches.loc[incomplete_matches, ["coord_key"] + NEW_FIELDS].head(5)
        raise ValueError(
            "Matched rows contain incomplete county/city fields. "
            f"Sample:\n{sample.to_string(index=False)}"
        )

    stats = MatchStats(
        total_rows=0,
        unique_coords=len(points),
        exact_county_matches=len(exact_matches),
        city_hint_matches=city_hint_count,
        nearest_within_city_matches=nearest_city_count,
        nearest_global_matches=nearest_global_count,
        unmatched_count=unmatched_count,
    )
    return all_matches[["coord_key"] + NEW_FIELDS], stats


def write_output(
    input_csv: Path,
    output_csv: Path,
    matches: pd.DataFrame,
    total_rows: int,
    logger: RunLogger,
) -> int:
    logger.log(f"Writing augmented CSV to {output_csv}")
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    match_lookup = (
        matches.set_index("coord_key")[NEW_FIELDS]
        .where(pd.notna(matches.set_index("coord_key")[NEW_FIELDS]), "")
        .to_dict(orient="index")
    )

    with input_csv.open("r", encoding=CSV_ENCODING, newline="") as src, output_csv.open(
        "w", encoding=CSV_ENCODING, newline=""
    ) as dst:
        reader = csv.DictReader(src)
        if reader.fieldnames is None:
            raise ValueError("Input CSV header is empty.")
        output_fields = reader.fieldnames[:]
        for field in NEW_FIELDS:
            if field not in output_fields:
                output_fields.append(field)

        writer = csv.DictWriter(dst, fieldnames=output_fields)
        writer.writeheader()

        written_rows = 0
        for row in reader:
            coord_key = f"{row['latitude'].strip()}|{row['longitude'].strip()}"
            match = match_lookup.get(coord_key, {})
            for field in NEW_FIELDS:
                row[field] = match.get(field, "")
            writer.writerow(row)
            written_rows += 1

    if written_rows != total_rows:
        raise ValueError(f"Written row count mismatch: expected {total_rows}, got {written_rows}")
    logger.log(f"CSV write complete; rows written: {written_rows}")
    return written_rows


def log_summary(stats: MatchStats, written_rows: int, logger: RunLogger) -> None:
    logger.log("Summary")
    logger.log(f"  total_rows={written_rows}")
    logger.log(f"  unique_coords={stats.unique_coords}")
    logger.log(f"  exact_county_matches={stats.exact_county_matches}")
    logger.log(f"  city_hint_matches={stats.city_hint_matches}")
    logger.log(f"  nearest_within_city_matches={stats.nearest_within_city_matches}")
    logger.log(f"  nearest_global_matches={stats.nearest_global_matches}")
    logger.log(f"  unmatched_count={stats.unmatched_count}")


def main() -> int:
    args = parse_args()
    require_paths([args.input_csv, args.county_shp, args.city_shp])

    LOGDIR.mkdir(parents=True, exist_ok=True)
    log_name = f"add_county_city_from_coords_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger = RunLogger(LOGDIR / log_name)

    try:
        logger.log("Starting county/city coordinate matching")
        logger.log(f"pandas version: {pd.__version__}")
        logger.log(f"geopandas version: {gpd.__version__}")

        unique_coords, total_rows = load_unique_coords(args.input_csv, logger)
        county, city = load_admin_layers(args.county_shp, args.city_shp, logger)
        points = build_points_gdf(unique_coords)
        matches, stats = match_points(points, county, city, logger)
        written_rows = write_output(args.input_csv, args.output_csv, matches, total_rows, logger)

        stats.total_rows = written_rows
        log_summary(stats, written_rows, logger)
        logger.log(f"Log saved to {logger.log_path}")
        return 0
    except Exception as exc:
        logger.log(f"ERROR: {type(exc).__name__}: {exc}")
        logger.log(f"Log saved to {logger.log_path}")
        raise
    finally:
        logger.close()


if __name__ == "__main__":
    sys.exit(main())
