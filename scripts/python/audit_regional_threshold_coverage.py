"""Read-only Stage 1 coverage audit for the regional maize threshold raster.

This script maps each V3 grid centre to its containing PixelIsArea GeoTIFF cell.
It does not interpolate threshold NoData cells and does not estimate yield models.
All outputs are written to a new run directory; an existing directory is a hard
error and is never modified.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from PIL import Image
import jsonschema


EXPECTED_RASTER_MD5 = "0d9e6c21bf1b25f113e14315863372f2"
EXPECTED_RASTER_SHA256 = (
    "f05e634664c4c6c2e2df352702acd421507162bc54cc067649071521ab1285b0"
)
EXPECTED_DATA_SHA256 = (
    "3f3f045a8040b876565873febab3918d166b8bd6f6938669b48c634a46172517"
)
EXPECTED_WIDTH = 514
EXPECTED_HEIGHT = 76
EXPECTED_RESOLUTION = 0.5
EXPECTED_VALID_CELLS = 5_627
EXPECTED_GATE = 0.80
ZONE_ORDER = ["NE", "HHH", "NW", "SH", "SW"]
ZONE_PROVINCES = {
    "NE": ["黑龙江省", "吉林省", "辽宁省", "内蒙古自治区"],
    "HHH": ["河南省", "山东省", "河北省", "安徽省", "江苏省"],
    "SW": ["四川省", "贵州省", "云南省", "广西壮族自治区", "重庆市"],
    "NW": ["甘肃省", "宁夏回族自治区", "新疆维吾尔自治区", "陕西省"],
    "SH": ["广东省", "福建省", "浙江省", "江西省", "海南省", "湖南省", "湖北省"],
}
COMPLETE_CASE_FIELDS = [
    "ln_yield",
    "ca",
    "gdd_10_29",
    "pr_sum",
    "v3_doy",
    "he_doy",
    "ma_doy",
    "gleam_smrz_mean",
]


def file_hash(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def assign_zone(province: pd.Series) -> pd.Series:
    zone = pd.Series("Other", index=province.index, dtype="object")
    for name, provinces in ZONE_PROVINCES.items():
        zone.loc[province.isin(provinces)] = name
    return zone


def geokey_value(keys: tuple[int, ...], key_id: int) -> int | None:
    """Read a short inline GeoKey value from GeoKeyDirectoryTag."""
    for offset in range(4, len(keys), 4):
        key, location, count, value = keys[offset : offset + 4]
        if key == key_id and location == 0 and count == 1:
            return int(value)
    return None


def canonical_grid_id(value: Any) -> str:
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)) and math.isfinite(float(value)):
        if float(value).is_integer():
            return str(int(value))
    return str(value)


def sample_key_csv_v1(panel: pd.DataFrame) -> str:
    keys = panel.loc[:, ["grid_id", "year"]].copy()
    keys["grid_id"] = keys["grid_id"].map(canonical_grid_id)
    keys["year"] = keys["year"].map(lambda value: f"{int(value):04d}")
    keys = keys.sort_values(["grid_id", "year"], kind="stable")
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["grid_id", "year"])
    writer.writerows(keys.itertuples(index=False, name=None))
    return hashlib.sha256(stream.getvalue().encode("utf-8")).hexdigest()


def build_audit(
    data_path: Path, raster_path: Path
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any], dict[str, Any]]:
    project_root = Path(__file__).resolve().parents[2]
    execution_script = Path(__file__).resolve()
    threshold_schema_path = project_root / "docs/contracts/threshold_grid.schema.json"
    run_manifest_schema_path = project_root / "docs/contracts/run_manifest.schema.json"
    raster_md5 = file_hash(raster_path, "md5")
    raster_sha256 = file_hash(raster_path, "sha256")
    data_sha256 = file_hash(data_path, "sha256")
    if raster_md5 != EXPECTED_RASTER_MD5:
        raise AssertionError(f"raster MD5 mismatch: {raster_md5}")
    if raster_sha256 != EXPECTED_RASTER_SHA256:
        raise AssertionError(f"raster SHA-256 mismatch: {raster_sha256}")
    if data_sha256 != EXPECTED_DATA_SHA256:
        raise AssertionError(f"V3 SHA-256 mismatch: {data_sha256}")

    with Image.open(raster_path) as image:
        if image.size != (EXPECTED_WIDTH, EXPECTED_HEIGHT) or image.mode != "F":
            raise AssertionError(f"unexpected raster shape/mode: {image.size}, {image.mode}")
        scale = tuple(float(v) for v in image.tag_v2[33550])
        tiepoint = tuple(float(v) for v in image.tag_v2[33922])
        geokeys = tuple(int(v) for v in image.tag_v2[34735])
        nodata = float(image.tag_v2[42113])
        raster = np.asarray(image, dtype=np.float64)

    if scale[:2] != (EXPECTED_RESOLUTION, EXPECTED_RESOLUTION):
        raise AssertionError(f"unexpected raster resolution: {scale}")
    if geokey_value(geokeys, 1025) != 1:
        raise AssertionError("GeoTIFF is not PixelIsArea")
    if geokey_value(geokeys, 2048) != 4326:
        raise AssertionError("GeoTIFF geographic CRS is not EPSG:4326")
    valid_raster = np.isfinite(raster) & (raster != nodata) & (raster > -1e30)
    if int(valid_raster.sum()) != EXPECTED_VALID_CELLS:
        raise AssertionError(f"unexpected valid raster cell count: {valid_raster.sum()}")

    columns = [
        "grid_id",
        "year",
        "longitude",
        "latitude",
        "province",
        *COMPLETE_CASE_FIELDS,
        "irr_frac",
        "crc_lag1",
    ]
    panel = pd.read_stata(data_path, columns=columns, convert_categoricals=False)
    if panel.duplicated(["grid_id", "year"]).any():
        raise AssertionError("V3 grid_id-year key is not unique")
    panel["zone"] = assign_zone(panel["province"])
    panel["pre_edd_complete"] = panel[COMPLETE_CASE_FIELDS].notna().all(axis=1)

    x_origin = tiepoint[3] - tiepoint[0] * scale[0]
    y_origin = tiepoint[4] + tiepoint[1] * scale[1]
    source_col = np.floor((panel["longitude"].to_numpy() - x_origin) / scale[0]).astype(int)
    source_row = np.floor((y_origin - panel["latitude"].to_numpy()) / scale[1]).astype(int)
    inside = (
        (source_row >= 0)
        & (source_row < EXPECTED_HEIGHT)
        & (source_col >= 0)
        & (source_col < EXPECTED_WIDTH)
    )
    threshold = np.full(len(panel), np.nan, dtype=float)
    threshold[inside] = raster[source_row[inside], source_col[inside]]
    covered = inside & np.isfinite(threshold) & (threshold != nodata) & (threshold > -1e30)
    panel["source_row"] = source_row
    panel["source_col"] = source_col
    panel["threshold_c"] = np.where(covered, threshold, np.nan)
    panel["coverage_flag"] = covered

    named_complete = panel["zone"].isin(ZONE_ORDER) & panel["pre_edd_complete"]
    sample_key_sha256 = sample_key_csv_v1(panel.loc[named_complete])
    coverage_rows: list[dict[str, Any]] = []
    for zone_name in ZONE_ORDER:
        zone_mask = named_complete & panel["zone"].eq(zone_name)
        valid_mask = zone_mask & panel["coverage_flag"]
        total_rows = int(zone_mask.sum())
        valid_rows = int(valid_mask.sum())
        coverage_rows.append(
            {
                "zone": zone_name,
                "total_rows": total_rows,
                "valid_threshold_rows": valid_rows,
                "row_coverage": valid_rows / total_rows,
                "total_grids": int(panel.loc[zone_mask, "grid_id"].nunique()),
                "valid_threshold_grids": int(panel.loc[valid_mask, "grid_id"].nunique()),
                "gate": EXPECTED_GATE,
                "gate_pass": valid_rows / total_rows >= EXPECTED_GATE,
            }
        )
    coverage = pd.DataFrame(coverage_rows)

    expected_counts = {
        "NE": (25_041, 23_723, 7_365, 6_967),
        "HHH": (13_165, 12_922, 3_844, 3_775),
        "NW": (5_540, 4_681, 2_228, 1_849),
        "SH": (4_556, 4_501, 1_692, 1_668),
        "SW": (18_094, 12_637, 6_208, 4_487),
    }
    for row in coverage.itertuples(index=False):
        observed = (
            row.total_rows,
            row.valid_threshold_rows,
            row.total_grids,
            row.valid_threshold_grids,
        )
        if observed != expected_counts[row.zone]:
            raise AssertionError(f"coverage count mismatch for {row.zone}: {observed}")

    grid_source = panel.loc[
        :, ["grid_id", "longitude", "latitude", "source_row", "source_col", "threshold_c", "coverage_flag"]
    ].copy()
    grid_nunique = grid_source.groupby("grid_id", dropna=False)[["longitude", "latitude"]].nunique()
    if (grid_nunique > 1).any(axis=None):
        raise AssertionError("grid coordinates change across years")
    grid = grid_source.drop_duplicates("grid_id").copy()
    grid["contract_version"] = "threshold-grid-v1"
    grid["grid_id"] = grid["grid_id"].map(canonical_grid_id)
    grid["source_crs"] = "EPSG:4326"
    grid["source_resolution_degrees"] = EXPECTED_RESOLUTION
    grid["source_md5"] = raster_md5
    grid["source_sha256"] = raster_sha256
    grid["mapping_method"] = "center-in-pixel-pixel-is-area"
    inside_grid = (
        grid["source_row"].between(0, EXPECTED_HEIGHT - 1)
        & grid["source_col"].between(0, EXPECTED_WIDTH - 1)
    )
    grid["coverage_reason"] = np.where(
        grid["coverage_flag"],
        "valid",
        np.where(inside_grid, "source-nodata", "outside-raster"),
    )
    raw_row = grid["source_row"].to_numpy()
    raw_col = grid["source_col"].to_numpy()
    grid["source_pixel_id"] = [
        int(row * EXPECTED_WIDTH + col) if valid else None
        for row, col, valid in zip(raw_row, raw_col, inside_grid, strict=True)
    ]
    grid["source_cell_west"] = [
        float(x_origin + col * scale[0]) if valid else None
        for col, valid in zip(raw_col, inside_grid, strict=True)
    ]
    grid["source_cell_east"] = [
        float(x_origin + (col + 1) * scale[0]) if valid else None
        for col, valid in zip(raw_col, inside_grid, strict=True)
    ]
    grid["source_cell_north"] = [
        float(y_origin - row * scale[1]) if valid else None
        for row, valid in zip(raw_row, inside_grid, strict=True)
    ]
    grid["source_cell_south"] = [
        float(y_origin - (row + 1) * scale[1]) if valid else None
        for row, valid in zip(raw_row, inside_grid, strict=True)
    ]
    grid["source_row"] = [int(value) if valid else None for value, valid in zip(raw_row, inside_grid, strict=True)]
    grid["source_col"] = [int(value) if valid else None for value, valid in zip(raw_col, inside_grid, strict=True)]
    grid = grid[
        [
            "contract_version",
            "grid_id",
            "latitude",
            "longitude",
            "source_crs",
            "source_resolution_degrees",
            "source_md5",
            "source_sha256",
            "source_row",
            "source_col",
            "source_pixel_id",
            "source_cell_west",
            "source_cell_east",
            "source_cell_south",
            "source_cell_north",
            "threshold_c",
            "mapping_method",
            "coverage_flag",
            "coverage_reason",
        ]
    ].sort_values("grid_id", kind="stable")

    manifest = {
        "canonical_id": "regional-threshold-sr-v1",
        "run_id": None,
        "status": "STOP_DATA_SUPPORT_GATE",
        "not_for_inference": True,
        "decision_task_id": "019f60e3-a5a6-7f83-af78-26ac04e7cac2",
        "data_path": data_path.as_posix(),
        "data_sha256": data_sha256,
        "raster_path": raster_path.as_posix(),
        "raster_md5": raster_md5,
        "raster_sha256": raster_sha256,
        "mapping_method": "center-in-pixel-pixel-is-area",
        "complete_case_fields": COMPLETE_CASE_FIELDS,
        "coverage_gate": EXPECTED_GATE,
        "coverage": coverage.to_dict(orient="records"),
        "stop_reason": "SW row coverage is below the frozen 0.80 gate",
        "model_was_run": False,
    }
    run_manifest = {
        "contract_version": "run-manifest-v1",
        "canonical_id": "regional-threshold-sr-v1",
        "run_id": None,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "STOP",
        "not_for_inference": True,
        "design_version": "2026-07-14_threshold_design_audit_stop",
        "git_commit": "3da8a12f94c04f7d19b6153bb1691787340ba4a8",
        "data_family": "V3",
        "inputs": [
            {
                "role": "analysis_panel",
                "path": data_path.as_posix(),
                "bytes": data_path.stat().st_size,
                "md5": file_hash(data_path, "md5"),
                "sha256": data_sha256,
            },
            {
                "role": "external_continuous_maize_threshold",
                "path": raster_path.as_posix(),
                "bytes": raster_path.stat().st_size,
                "md5": raster_md5,
                "sha256": raster_sha256,
            },
            {
                "role": "execution_script",
                "path": execution_script.as_posix(),
                "bytes": execution_script.stat().st_size,
                "md5": file_hash(execution_script, "md5"),
                "sha256": file_hash(execution_script, "sha256"),
            },
            {
                "role": "threshold_grid_contract",
                "path": threshold_schema_path.as_posix(),
                "bytes": threshold_schema_path.stat().st_size,
                "md5": file_hash(threshold_schema_path, "md5"),
                "sha256": file_hash(threshold_schema_path, "sha256"),
            },
            {
                "role": "run_manifest_contract",
                "path": run_manifest_schema_path.as_posix(),
                "bytes": run_manifest_schema_path.stat().st_size,
                "md5": file_hash(run_manifest_schema_path, "md5"),
                "sha256": file_hash(run_manifest_schema_path, "sha256"),
            },
        ],
        "sample_predicate": (
            "zone in {NE,HHH,NW,SH,SW} and nonmissing "
            + ",".join(COMPLETE_CASE_FIELDS)
        ),
        "sample_key_serialization": "sample-key-csv-v1",
        "sample_key_sha256": sample_key_sha256,
        "sample_counts": {
            "panel_rows": int(len(panel)),
            "panel_grids": int(panel["grid_id"].nunique()),
            "named_complete_rows": int(named_complete.sum()),
            "named_complete_grids": int(panel.loc[named_complete, "grid_id"].nunique()),
        },
        "outcome": "ln_yield (support audit only; not estimated)",
        "exposure_definition": (
            "official 0.5-degree continuous maize threshold mapped by "
            "0.1-degree grid centre to containing PixelIsArea source cell; no interpolation"
        ),
        "soil_moisture_roles": [
            "gleam_smrz_mean used only in the pre-EDD complete-case support predicate"
        ],
        "fixed_effects": ["none; no yield model was run"],
        "inference": {
            "primary": "none; deterministic coverage audit",
            "bootstrap_reps": 0,
            "spatial_block_degrees": None,
            "spatial_hac_km": [],
            "multiplicity": "none",
        },
        "ca_quantiles": None,
        "exposure_endpoints": None,
        "seed": 42,
        "claims": [
            "SW valid-threshold row coverage is 12637/18094=69.8408%",
            "the frozen 80% five-zone support gate is not met",
            "no yield model or SR buffering coefficient was estimated",
        ],
        "stop_rules_triggered": [
            "at least one named maize zone has less than 80% valid external-threshold row coverage"
        ],
        "verification": [
            {"check": "raster MD5 and SHA-256", "status": "PASS", "detail": None},
            {"check": "V3 SHA-256", "status": "PASS", "detail": None},
            {"check": "grid_id-year uniqueness", "status": "PASS", "detail": None},
            {"check": "five-zone frozen coverage counts", "status": "PASS", "detail": None},
            {"check": "threshold_grid Draft202012 schema", "status": "PASS", "detail": None},
            {"check": "yield model", "status": "SKIP", "detail": "STOP occurred before smoke"},
        ],
    }
    return coverage, grid, manifest, run_manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        type=Path,
        required=True,
        help="Path to the V3 analysis panel",
    )
    parser.add_argument(
        "--raster",
        type=Path,
        required=True,
        help="Path to the externally supplied maize threshold GeoTIFF",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("temp/2026-07-14_regional_threshold_stage1_audit_v5"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output_dir.exists():
        raise FileExistsError(f"refusing to modify existing run directory: {args.output_dir}")
    coverage, grid, manifest, run_manifest = build_audit(args.data, args.raster)
    manifest["run_id"] = args.output_dir.name
    run_manifest["run_id"] = args.output_dir.name
    args.output_dir.mkdir(parents=True, exist_ok=False)
    coverage_path = args.output_dir / "threshold_coverage_by_zone.csv"
    grid_csv_path = args.output_dir / "threshold_grid.csv"
    grid_jsonl_path = args.output_dir / "threshold_grid.jsonl"
    run_manifest_path = args.output_dir / "run_manifest.json"
    manifest_path = args.output_dir / "audit_manifest.json"
    coverage.to_csv(coverage_path, index=False, lineterminator="\n")
    grid.to_csv(grid_csv_path, index=False, lineterminator="\n")
    project_root = Path(__file__).resolve().parents[2]
    threshold_schema = json.loads(
        (project_root / "docs/contracts/threshold_grid.schema.json").read_text(encoding="utf-8")
    )
    threshold_validator = jsonschema.Draft202012Validator(threshold_schema)
    with grid_jsonl_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in grid.to_dict(orient="records"):
            clean_record = {
                key: (
                    None
                    if pd.isna(value)
                    else value.item()
                    if isinstance(value, np.generic)
                    else value
                )
                for key, value in record.items()
            }
            threshold_validator.validate(clean_record)
            handle.write(json.dumps(clean_record, ensure_ascii=False, allow_nan=False) + "\n")
    run_manifest_schema = json.loads(
        (project_root / "docs/contracts/run_manifest.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(run_manifest_schema).validate(run_manifest)
    run_manifest_path.write_text(
        json.dumps(run_manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    manifest["outputs"] = {
        path.name: file_hash(path, "sha256")
        for path in [coverage_path, grid_csv_path, grid_jsonl_path, run_manifest_path]
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
