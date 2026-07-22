from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from PIL import Image, TiffImagePlugin


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "python"
sys.path.insert(0, str(SCRIPT_DIR))

from climate_stress.grid import (  # noqa: E402
    TARGET_GRID,
    apply_bilinear,
    apply_nearest,
    build_balanced_grid_year,
    build_bilinear_mapping,
    build_nearest_mapping,
    build_v3_crosswalk,
    validate_target_axes,
)
from climate_stress.phenology import (  # noqa: E402
    add_phenology_windows,
    aggregate_phenology_year,
    read_phenology_tiff,
)


def _v3_source(cell_count: int = 2) -> pd.DataFrame:
    rows: list[dict[str, float | int]] = []
    for year in (2016, 2017):
        for lon_idx in range(cell_count):
            rows.append(
                {
                    "grid_id": 101 + lon_idx,
                    "year": year,
                    "latitude": 53.53,
                    "longitude": 73.58 + 0.1 * lon_idx,
                }
            )
    return pd.DataFrame(rows)


def _write_tiff(
    path: Path,
    values: np.ndarray,
    *,
    x_origin: float = 73.53,
    y_origin: float = 53.58,
    pixel_size: float = 0.05,
    nodata: float | None = None,
) -> None:
    tags = TiffImagePlugin.ImageFileDirectory_v2()
    tags[33550] = (pixel_size, pixel_size, 0.0)
    tags[33922] = (0.0, 0.0, 0.0, x_origin, y_origin, 0.0)
    if nodata is not None:
        tags[42113] = str(nodata)
    Image.fromarray(np.asarray(values, dtype=np.float32)).save(path, tiffinfo=tags)


def test_target_axes_crosswalk_and_balanced_years_are_stable() -> None:
    validate_target_axes(TARGET_GRID.latitudes, TARGET_GRID.longitudes)
    with pytest.raises(ValueError, match="Latitude axis"):
        validate_target_axes(TARGET_GRID.latitudes[::-1], TARGET_GRID.longitudes)

    crosswalk = build_v3_crosswalk(_v3_source(), expected_unique=2)
    assert crosswalk["grid_id_v3"].tolist() == [101, 102]
    assert crosswalk["era01_cell_id"].tolist() == [1, 2]
    assert crosswalk["lat_idx"].tolist() == [0, 0]
    assert crosswalk["lon_idx"].tolist() == [0, 1]
    assert crosswalk["lat10"].tolist() == [535, 535]
    assert crosswalk["lon10"].tolist() == [736, 737]

    panel = build_balanced_grid_year(crosswalk, years=(2010, 2011), expected_unique=2)
    assert len(panel) == 4
    assert not panel.duplicated(["era01_cell_id", "year"]).any()
    assert panel.groupby("era01_cell_id")["year"].apply(list).tolist() == [
        [2010, 2011],
        [2010, 2011],
    ]


def test_crosswalk_rejects_non_unique_v3_identifier() -> None:
    source = _v3_source()
    source.loc[source["grid_id"] == 102, "grid_id"] = 101
    with pytest.raises(ValueError, match="more than one target cell"):
        build_v3_crosswalk(source, expected_unique=None)


def test_v3_float32_coordinates_are_audited_then_canonicalized() -> None:
    source = pd.DataFrame(
        {
            "grid_id": [1, 2],
            "latitude": np.asarray([21.73, 51.13], dtype=np.float32),
            "longitude": np.asarray([134.58, 75.58], dtype=np.float32),
        }
    )
    crosswalk = build_v3_crosswalk(source, expected_unique=2)
    expected_lat = TARGET_GRID.latitudes[crosswalk["lat_idx"].to_numpy()]
    expected_lon = TARGET_GRID.longitudes[crosswalk["lon_idx"].to_numpy()]
    assert np.array_equal(crosswalk["latitude"].to_numpy(), expected_lat)
    assert np.array_equal(crosswalk["longitude"].to_numpy(), expected_lon)
    assert crosswalk["v3_lat_err_abs_deg"].max() <= 1e-5
    assert crosswalk["v3_lon_err_abs_deg"].max() <= 1e-5
    assert crosswalk["v3_lon_err_abs_deg"].max() > 1e-7


def test_v3_coordinate_beyond_entry_tolerance_is_rejected() -> None:
    source = _v3_source(cell_count=1)
    source["longitude"] = 73.58002
    with pytest.raises(ValueError, match="not on the frozen target axes"):
        build_v3_crosswalk(source, expected_unique=None)


def test_nearest_and_bilinear_mappings_handle_descending_axes_and_missing() -> None:
    latitude = np.array([2.0, 1.0, 0.0])
    longitude = np.array([0.0, 1.0, 2.0])
    base = latitude[:, None] + 2.0 * longitude[None, :]
    targets_lat = np.array([1.5, 3.0])
    targets_lon = np.array([0.5, 1.0])

    nearest = build_nearest_mapping(latitude, longitude, targets_lat, targets_lon)
    nearest_values = apply_nearest(base, nearest)
    assert nearest_values[0] == pytest.approx(1.0)
    assert np.isnan(nearest_values[1])

    one_missing = base.copy()
    one_missing[1, 0] = np.nan
    only_one = np.full_like(base, np.nan)
    only_one[0, 1] = base[0, 1]
    mapping = build_bilinear_mapping(latitude, longitude, targets_lat, targets_lon)
    interpolated = apply_bilinear(
        np.stack([base, one_missing, only_one]), mapping, min_valid_neighbors=2
    )
    assert interpolated[0, 0] == pytest.approx(2.5)
    assert interpolated[1, 0] == pytest.approx(3.0)
    assert np.isnan(interpolated[2, 0])
    assert np.isnan(interpolated[:, 1]).all()


def test_tiff_reader_masks_frozen_invalid_values_and_tag_nodata(tmp_path: Path) -> None:
    path = tmp_path / "invalid.tif"
    _write_tiff(path, np.array([[0, 1, 255, 367, 65535]], dtype=np.float32), nodata=255)
    values, _ = read_phenology_tiff(path)
    assert np.flatnonzero(np.isfinite(values)).tolist() == [1]
    assert values[0, 1] == pytest.approx(1.0)


def test_joint_pixel_mask_variable_width_and_candidate_denominator(tmp_path: Path) -> None:
    crosswalk = build_v3_crosswalk(_v3_source(), expected_unique=2)
    v3 = np.array(
        [
            [100, 170, 120, 122],
            [102, 104, 124, 126],
        ],
        dtype=np.float32,
    )
    he = np.array(
        [
            [150, 150, 160],
            [152, 154, 162],
        ],
        dtype=np.float32,
    )
    ma = np.array(
        [
            [200, 200, 210, 212],
            [202, 204, 214, 216],
        ],
        dtype=np.float32,
    )
    _write_tiff(tmp_path / "CHN_Maize_V3_2010.tif", v3)
    _write_tiff(tmp_path / "CHN_Maize_HE_2010.tif", he)
    _write_tiff(tmp_path / "CHN_Maize_MA_2010.tif", ma)

    result = aggregate_phenology_year(
        crosswalk,
        2010,
        tmp_path,
        source_crs="EPSG:4326",
        row_chunk_size=1,
    ).set_index("era01_cell_id")

    assert result["pheno_candidate_pixel_count"].tolist() == [4, 4]
    assert result["pheno_valid_pixel_count"].tolist() == [3, 2]
    assert result.loc[1, "pheno_coverage"] == pytest.approx(0.75)
    assert result.loc[2, "pheno_coverage"] == pytest.approx(0.50)
    assert result.loc[1, "v3_doy"] == 102
    assert result.loc[1, "v3_doy_mean"] == pytest.approx(102.0)
    assert result.loc[1, "v3_doy_median"] == pytest.approx(102.0)
    assert result.loc[1, "v3_doy_std"] == pytest.approx(np.sqrt(8.0 / 3.0))
    assert result.loc[1, "v3_doy_iqr"] == pytest.approx(2.0)
    assert result.loc[2, "v3_doy"] == 122
    assert result.loc[2, "he_doy"] == 161
    assert result.loc[2, "ma_doy"] == 212
    assert result.loc[1, "win_full_start"] == 72
    assert result.loc[1, "win_full_end"] == 202
    assert result.loc[1, "win_full_days"] == 131


def test_windows_clip_before_closed_interval_length_and_preserve_na() -> None:
    frame = pd.DataFrame(
        {
            "year": [2012, 2012],
            "v3_doy": pd.array([5, pd.NA], dtype="Int16"),
            "he_doy": pd.array([10, pd.NA], dtype="Int16"),
            "ma_doy": pd.array([366, pd.NA], dtype="Int16"),
        }
    )
    result = add_phenology_windows(frame)
    assert result.loc[0, ["win_full_start", "win_full_end", "win_full_days"]].tolist() == [
        1,
        366,
        366,
    ]
    assert result.loc[
        0, ["win_v3pre30_start", "win_v3pre30_end", "win_v3pre30_days"]
    ].tolist() == [1, 5, 5]
    assert result.loc[0, "win_v3pm10_days"] == 15
    assert pd.isna(result.loc[1, "win_full_start"])
    assert pd.isna(result.loc[1, "win_hema_days"])


def test_windows_keep_doy_366_in_non_leap_year_then_clip_to_365() -> None:
    frame = pd.DataFrame(
        {
            "year": [2019],
            "v3_doy": pd.array([300], dtype="Int16"),
            "he_doy": pd.array([350], dtype="Int16"),
            "ma_doy": pd.array([366], dtype="Int16"),
        }
    )
    result = add_phenology_windows(frame)
    assert result.loc[0, ["win_full_start", "win_full_end", "win_full_days"]].tolist() == [
        270,
        365,
        96,
    ]
    assert result.loc[0, ["win_hema_start", "win_hema_end", "win_hema_days"]].tolist() == [
        350,
        365,
        16,
    ]


def test_v3_parquet_crosswalk_projects_only_id_and_coordinates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "v3.parquet"
    pd.DataFrame(
        {
            "grid_id": [10],
            "latitude": [53.53],
            "longitude": [73.58],
            "unused_large_payload": [999.0],
        }
    ).to_parquet(source, index=False)
    original = pd.read_parquet
    observed: list[tuple[str, ...] | None] = []

    def guarded_read(path, *args, **kwargs):
        columns = kwargs.get("columns")
        observed.append(None if columns is None else tuple(columns))
        assert columns == ["grid_id", "latitude", "longitude"]
        return original(path, *args, **kwargs)

    monkeypatch.setattr(pd, "read_parquet", guarded_read)
    result = build_v3_crosswalk(source, expected_unique=1)
    assert observed == [("grid_id", "latitude", "longitude")]
    assert result.loc[0, "grid_id_v3"] == 10
    assert "unused_large_payload" not in result.columns
