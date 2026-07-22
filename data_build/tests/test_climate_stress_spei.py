from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import netCDF4 as nc
import numpy as np
import pandas as pd
import pytest


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "python"
sys.path.insert(0, str(SCRIPT_DIR))

from climate_stress.spei import (  # noqa: E402
    LEGACY_FIELD_MAP,
    WINDOW_NAMES,
    aggregate_manual_spei_event_six_windows,
    aggregate_manual_six_windows,
    build_chm_spatial_mapping,
    build_spei_caches,
    combine_parquet_partitions_new,
    detect_manual_spei_events,
    dynamic_ext_six_windows,
    extract_mapped_time_slices,
    iter_spei_aggregation_blocks,
    legacy_v3_exact_sidecar,
    load_cache_array,
    map_bilinear_renormalized,
    map_nearest,
    prepare_two_week_records,
    summarize_manual_window,
    summarize_spei_events_for_window,
    write_parquet_partition_new,
    write_two_week_audit,
)
import climate_stress.spei as spei_module  # noqa: E402


def _month_starts(year: int) -> list[datetime]:
    return [datetime(year, month, 1) for month in range(1, 13)]


def _write_small_chm(path: Path, scale: int, year: int = 2010) -> None:
    with nc.Dataset(path, "w") as dataset:
        dataset.createDimension("time", 12)
        dataset.createDimension("lat", 2)
        dataset.createDimension("lon", 2)
        time = dataset.createVariable("time", "i4", ("time",))
        time.units = "days since 1961-01-01"
        time.calendar = "standard"
        time[0:12] = nc.date2num(
            _month_starts(year), units=time.units, calendar=time.calendar
        )
        latitude = dataset.createVariable("lat", "f8", ("lat",))
        longitude = dataset.createVariable("lon", "f8", ("lon",))
        latitude[0:2] = [0.0, 1.0]
        longitude[0:2] = [10.0, 11.0]
        variable = dataset.createVariable(
            f"SPEI-{scale}", "f4", ("time", "lat", "lon"), fill_value=np.nan
        )
        for index in range(12):
            base = scale * 100.0 + index * 10.0
            variable[index, 0:2, 0:2] = np.asarray(
                [[base, base + 1], [base + 2, base + 3]], dtype=np.float32
            )


def _panel_row(year: int = 2010, start_doy: int = 15, end_doy: int = 64) -> dict[str, object]:
    row: dict[str, object] = {
        "grid_id": 1,
        "year": year,
        "latitude": 30.0,
        "longitude": 110.0,
        "spei_cell_index": 0,
    }
    for window in WINDOW_NAMES:
        row[f"win_{window}_start"] = start_doy
        row[f"win_{window}_end"] = end_doy
    return row


def test_mapping_is_derived_from_source_coordinates() -> None:
    mapping = build_chm_spatial_mapping(
        [0.0, 1.0],
        [10.0, 11.0],
        [0.25, 0.75],
        [10.25, 10.75],
    )
    source = np.asarray([[1.0, 2.0], [3.0, 4.0]])
    np.testing.assert_allclose(map_nearest(source, mapping), [1.0, 4.0])
    np.testing.assert_allclose(
        map_bilinear_renormalized(source, mapping), [1.75, 3.25]
    )
    assert mapping.bilinear_in_bounds.tolist() == [True, True]


def test_mapping_supports_descending_source_axes() -> None:
    mapping = build_chm_spatial_mapping(
        [1.0, 0.0],
        [11.0, 10.0],
        [0.25],
        [10.25],
    )
    source = np.asarray([[4.0, 3.0], [2.0, 1.0]])
    assert map_nearest(source, mapping)[0] == pytest.approx(1.0)
    assert map_bilinear_renormalized(source, mapping)[0] == pytest.approx(1.75)


def test_manual_bilinear_requires_two_valid_positive_weight_neighbours() -> None:
    mapping = build_chm_spatial_mapping(
        [0.0, 1.0], [10.0, 11.0], [0.5], [10.5]
    )
    three_valid = np.asarray([[1.0, np.nan], [3.0, 4.0]])
    assert map_bilinear_renormalized(three_valid, mapping)[0] == pytest.approx(8 / 3)
    one_valid = np.asarray([[1.0, np.nan], [np.nan, np.nan]])
    assert np.isnan(map_bilinear_renormalized(one_valid, mapping)[0])
    outside = build_chm_spatial_mapping(
        [0.0, 1.0], [10.0, 11.0], [-0.1], [10.5]
    )
    assert np.isnan(map_bilinear_renormalized(three_valid, outside)[0])


def test_data_variable_is_read_one_explicit_time_slice_at_a_time() -> None:
    class RecordingVariable:
        ndim = 3
        shape = (3, 2, 2)

        def __init__(self) -> None:
            self.keys: list[object] = []

        def __getitem__(self, key: object) -> np.ndarray:
            self.keys.append(key)
            assert isinstance(key, tuple)
            assert isinstance(key[0], int)
            return np.full((2, 2), float(key[0]))

    class Dataset:
        def __init__(self) -> None:
            self.variable = RecordingVariable()
            self.variables = {"SPEI-1": self.variable}

    dataset = Dataset()
    mapping = build_chm_spatial_mapping(
        [0.0, 1.0], [10.0, 11.0], [0.25], [10.25]
    )
    result = extract_mapped_time_slices(
        dataset, "SPEI-1", [0, 2], mapping, method="nearest"
    )
    np.testing.assert_allclose(result[:, 0], [0.0, 2.0])
    assert len(dataset.variable.keys) == 2


def test_small_netcdf_builds_nearest_target_and_full_bilinear_caches(
    tmp_path: Path,
) -> None:
    for scale in (1, 3):
        _write_small_chm(tmp_path / f"CHM_SPEI-{scale}.nc", scale)
    paths = build_spei_caches(
        str(tmp_path / "CHM_SPEI-{scale}.nc"),
        [0.2],
        [10.2],
        tmp_path / "cache",
        target_years=(2010,),
        target_scales=(1, 3),
        full_years=(2010,),
        manual_scales=(1, 3),
    )
    target_1 = load_cache_array(paths.target_nearest[1], mmap=False)
    manual_1 = load_cache_array(paths.full_manual[1], mmap=False)
    target_3 = load_cache_array(paths.target_nearest[3], mmap=False)
    assert target_1.shape == manual_1.shape == target_3.shape == (12, 1)
    assert target_1[0, 0] == pytest.approx(100.0)
    assert manual_1[0, 0] == pytest.approx(100.6)
    assert target_3[0, 0] == pytest.approx(300.0)
    metadata = json.loads(paths.metadata.read_text(encoding="utf-8"))
    assert metadata["read_policy"] == "one explicit time index per source read"
    assert metadata["target_interpolation"] == "nearest"
    assert metadata["manual_interpolation"] == "bilinear_renormalized"
    assert len(metadata["signature_sha256"]) == 64
    with pytest.raises(FileExistsError):
        build_spei_caches(
            str(tmp_path / "CHM_SPEI-{scale}.nc"),
            [0.2],
            [10.2],
            tmp_path / "cache",
            target_years=(2010,),
            target_scales=(1, 3),
            full_years=(2010,),
            manual_scales=(1, 3),
        )

    untouched_scale_three = paths.target_nearest[3].read_bytes()
    resumed = build_spei_caches(
        str(tmp_path / "CHM_SPEI-{scale}.nc"),
        [0.2],
        [10.2],
        tmp_path / "cache",
        target_years=(2010,),
        target_scales=(1, 3),
        full_years=(2010,),
        manual_scales=(1, 3),
        resume=True,
    )
    assert resumed.target_nearest[3].read_bytes() == untouched_scale_three
    assert not list((tmp_path / "cache").rglob("*.incomplete.*"))

    paths.target_nearest[1].write_bytes(b"truncated-npy")
    repaired = build_spei_caches(
        str(tmp_path / "CHM_SPEI-{scale}.nc"),
        [0.2],
        [10.2],
        tmp_path / "cache",
        target_years=(2010,),
        target_scales=(1, 3),
        full_years=(2010,),
        manual_scales=(1, 3),
        resume=True,
    )
    np.testing.assert_allclose(
        load_cache_array(repaired.target_nearest[1], mmap=False), target_1
    )
    quarantined = list(
        repaired.target_nearest[1].parent.glob("scale=01.npy.incomplete.*")
    )
    assert len(quarantined) == 1
    assert quarantined[0].read_bytes() == b"truncated-npy"
    assert repaired.target_nearest[3].read_bytes() == untouched_scale_three

    tampered_metadata = json.loads(repaired.metadata.read_text(encoding="utf-8"))
    tampered_metadata["signature_sha256"] = "0" * 64
    repaired.metadata.write_text(
        json.dumps(tampered_metadata, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    signed = build_spei_caches(
        str(tmp_path / "CHM_SPEI-{scale}.nc"),
        [0.2],
        [10.2],
        tmp_path / "cache",
        target_years=(2010,),
        target_scales=(1, 3),
        full_years=(2010,),
        manual_scales=(1, 3),
        resume=True,
    )
    rebuilt_metadata = json.loads(signed.metadata.read_text(encoding="utf-8"))
    assert rebuilt_metadata["signature_sha256"] != "0" * 64
    assert list(signed.metadata.parent.glob("metadata.json.incomplete.*"))


def test_manual_window_uses_overlap_day_weights_min_end_and_coverage() -> None:
    codes = [201901, 201902]
    summary = summarize_manual_window(
        codes,
        [-2.0, -1.5],
        window_start=date(2019, 1, 15),
        window_end=date(2019, 2, 10),
    )
    assert summary.expected_days == summary.valid_days == 27
    assert summary.coverage == pytest.approx(1.0)
    assert summary.mean == pytest.approx((-2.0 * 17 - 1.5 * 10) / 27)
    assert summary.min_spei == pytest.approx(-2.0)
    assert summary.end == pytest.approx(-1.5)
    assert summary.peak_threshold_deficit == pytest.approx(1.0)


def test_manual_window_below_ninety_percent_is_numeric_missing() -> None:
    summary = summarize_manual_window(
        [201901, 201902],
        [-2.0, np.nan],
        window_start=date(2019, 1, 15),
        window_end=date(2019, 2, 10),
    )
    assert summary.valid_days == 17
    assert summary.coverage == pytest.approx(17 / 27)
    assert np.isnan(summary.mean)
    assert np.isnan(summary.min_spei)
    assert np.isnan(summary.end)
    assert np.isnan(summary.peak_threshold_deficit)


def test_manual_window_visits_only_overlapping_months(monkeypatch) -> None:
    codes = np.asarray(
        [year * 100 + month for year in range(1961, 2023) for month in range(1, 13)],
        dtype=np.int32,
    )
    calls: list[int] = []
    original = spei_module._month_start

    def recording_month_start(code: int) -> date:
        calls.append(int(code))
        return original(code)

    monkeypatch.setattr(spei_module, "_month_start", recording_month_start)
    summary = summarize_manual_window(
        codes,
        np.zeros(codes.size, dtype=float),
        window_start=date(2019, 1, 15),
        window_end=date(2019, 2, 10),
    )
    assert summary.coverage == 1.0
    assert calls == [201901, 201902]


def test_manual_aggregation_emits_both_scales_for_all_six_windows() -> None:
    panel = pd.DataFrame([_panel_row(start_doy=1, end_doy=31)])
    codes = np.asarray([201000 + month for month in range(1, 13)])
    scale_values = {
        1: np.arange(1, 13, dtype=float)[:, None],
        3: (np.arange(1, 13, dtype=float) * 10)[:, None],
    }
    result = aggregate_manual_six_windows(
        panel,
        codes,
        scale_values,
        cell_index_column="spei_cell_index",
    )
    assert result["window"].tolist() == list(WINDOW_NAMES)
    assert len(result) == 6
    assert (result["chm_spei_s1_mean"] == 1.0).all()
    assert (result["chm_spei_s3_end"] == 10.0).all()
    assert (result["chm_spei_s1_coverage"] == 1.0).all()


def test_manual_event_api_detects_full_series_then_bridges_all_six_windows() -> None:
    panel = pd.DataFrame([_panel_row(year=2019, start_doy=32, end_doy=105)])
    codes = np.asarray([201900 + month for month in range(1, 7)], dtype=np.int32)
    scale_values = {
        1: np.asarray([-1.2, -1.3, 0.0, -2.0, -2.0, -2.0])[:, None],
        3: np.zeros((6, 1), dtype=float),
    }
    long, events, bridges = aggregate_manual_spei_event_six_windows(
        panel,
        codes,
        scale_values,
        cell_index_column="spei_cell_index",
    )

    assert len(long) == 6
    assert long[["source_row", "window"]].duplicated().sum() == 0
    main = long.iloc[0]
    assert main["chm_spei_s1_k10_main_any"] == 1
    assert main["chm_spei_s1_k10_main_count"] == 2
    assert main["chm_spei_s1_k10_main_window_total_duration_days"] == 43
    assert main["chm_spei_s1_k10_main_window_total_duration_periods_equiv"] == pytest.approx(
        1.5
    )
    assert main["chm_spei_s1_k10_main_complete_total_duration_days"] == 150
    assert main["chm_spei_s1_k10_main_complete_total_duration_months"] == 5
    assert main["chm_spei_s1_k10_main_severity_spei_periods"] == pytest.approx(0.8)
    assert main["chm_spei_s1_k10_main_peak_threshold_deficit"] == pytest.approx(1.0)
    assert main["chm_spei_s3_k10_main_any"] == 0
    assert len(events) == 3
    assert events["event_id"].is_unique
    assert set(events["severity_spei_periods"].round(6)) == {0.5, 1.5, 3.0}
    assert len(bridges) == 18
    assert bridges["event_id"].isin(events["event_id"]).all()
    assert bridges["window_coverage_ok"].all()


def test_strict_event_peak_is_na_for_isolated_threshold_month() -> None:
    panel = pd.DataFrame([_panel_row(year=2019, start_doy=1, end_doy=90)])
    codes = np.asarray([201901, 201902, 201903], dtype=np.int32)
    long, events, _bridges = aggregate_manual_spei_event_six_windows(
        panel,
        codes,
        {
            1: np.asarray([-2.0, 0.0, 0.0], dtype=float)[:, None],
            3: np.zeros((3, 1), dtype=float),
        },
        cell_index_column="spei_cell_index",
    )

    full = long.loc[long["window"] == "full"].iloc[0]
    assert full["chm_spei_s1_k15_strict_any"] == 0
    assert full["chm_spei_s1_k15_strict_count"] == 0
    assert full["chm_spei_s1_k15_strict_window_min_spei"] == pytest.approx(-2.0)
    assert np.isnan(full["chm_spei_s1_k15_strict_event_min_spei"])
    assert np.isnan(full["chm_spei_s1_k15_strict_peak_threshold_deficit"])
    assert not (events["variant"] == "k15_strict").any()


def test_manual_event_api_fails_closed_below_window_coverage() -> None:
    panel = pd.DataFrame([_panel_row(year=2019, start_doy=32, end_doy=105)])
    codes = np.asarray([201900 + month for month in range(1, 7)], dtype=np.int32)
    scale_one = np.asarray([-1.2, -1.3, np.nan, -2.0, -2.0, -2.0])[:, None]
    long, _events, bridges = aggregate_manual_spei_event_six_windows(
        panel,
        codes,
        {1: scale_one, 3: np.zeros((6, 1), dtype=float)},
        cell_index_column="spei_cell_index",
    )

    assert long["chm_spei_s1_event_coverage"].iloc[0] == pytest.approx(43 / 74)
    assert long["chm_spei_s1_k10_main_any"].isna().all()
    assert not bridges.loc[bridges["scale_months"].eq(1), "window_coverage_ok"].any()


def _nearest_scale_fixture() -> tuple[np.ndarray, dict[int, np.ndarray]]:
    codes = np.asarray([201000 + month for month in range(1, 13)], dtype=np.int32)
    values = {
        scale: np.asarray(
            [[scale * 100.0 + month] for month in range(1, 13)], dtype=float
        )
        for scale in range(1, 13)
    }
    return codes, values


def test_dynamic_ext_reports_value_actual_scale_and_end_month() -> None:
    codes, values = _nearest_scale_fixture()
    panel = pd.DataFrame([_panel_row(start_doy=15, end_doy=64)])  # Jan 15 - Mar 5
    result = dynamic_ext_six_windows(
        panel,
        codes,
        values,
        cell_index_column="spei_cell_index",
    )
    assert len(result) == 6
    assert (result["chm_spei_dynamic_ext_actual_scale"] == 3).all()
    assert (result["chm_spei_dynamic_ext_end_month"] == 3).all()
    assert (result["chm_spei_dynamic_ext_value"] == 303.0).all()


def test_spatial_blocks_match_unblocked_values_ids_and_slice_contract() -> None:
    panel_rows = []
    for cell_index in range(4):
        row = _panel_row(year=2019, start_doy=15, end_doy=105)
        row.update(
            {
                "spei_cell_index": cell_index,
                "era01_cell_id": 1001 + cell_index,
                "grid_id": 2001 + cell_index,
            }
        )
        panel_rows.append(row)
    panel = pd.DataFrame(panel_rows)
    full_codes = np.asarray(
        [year * 100 + month for year in (2018, 2019) for month in range(1, 13)],
        dtype=np.int32,
    )
    full_values = {
        1: np.zeros((24, 4), dtype=float),
        3: np.zeros((24, 4), dtype=float),
    }
    full_values[1][12:15, :] = np.asarray(
        [[-1.2, -1.3, -2.0, -1.1], [-1.4, -1.6, -2.1, -1.2], [-1.7, 0.0, -2.2, -1.3]]
    )
    full_values[3][12:15, :] = -1.2
    target_codes = np.asarray([201900 + month for month in range(1, 13)], dtype=np.int32)
    target_values = {
        scale: np.full((12, 4), scale / 10.0, dtype=float)
        for scale in range(1, 13)
    }

    expected_manual = aggregate_manual_six_windows(
        panel,
        full_codes,
        full_values,
        cell_index_column="spei_cell_index",
    )
    expected_dynamic = dynamic_ext_six_windows(
        panel,
        target_codes,
        target_values,
        cell_index_column="spei_cell_index",
    )
    expected_long, expected_events, expected_bridges = (
        aggregate_manual_spei_event_six_windows(
            panel,
            full_codes,
            full_values,
            cell_index_column="spei_cell_index",
        )
    )

    class TrackingArray:
        def __init__(self, values: np.ndarray) -> None:
            self.values = values
            self.shape = values.shape
            self.ndim = values.ndim
            self.keys: list[object] = []

        def __getitem__(self, key: object) -> np.ndarray:
            self.keys.append(key)
            return self.values[key]

        def __array__(self, *args, **kwargs):
            raise AssertionError("The complete cache must not be converted to an ndarray")

    tracked_full = {scale: TrackingArray(values) for scale, values in full_values.items()}
    tracked_target = {
        scale: TrackingArray(values) for scale, values in target_values.items()
    }
    blocks = list(
        iter_spei_aggregation_blocks(
            panel,
            full_codes,
            tracked_full,
            target_codes,
            tracked_target,
            cell_index_column="spei_cell_index",
            cell_count=4,
            cell_block_size=2,
        )
    )
    assert [(block.cell_start, block.cell_stop) for block in blocks] == [(0, 2), (2, 4)]
    for tracked in (*tracked_full.values(), *tracked_target.values()):
        assert len(tracked.keys) == 2
        for key in tracked.keys:
            assert isinstance(key, tuple)
            assert key[0] == slice(None)
            assert isinstance(key[1], slice)
            assert key[1].stop - key[1].start <= 2

    actual_manual = pd.concat([block.manual for block in blocks], ignore_index=True)
    actual_dynamic = pd.concat([block.dynamic for block in blocks], ignore_index=True)
    actual_long = pd.concat([block.event_long for block in blocks], ignore_index=True)
    actual_events = pd.concat([block.events for block in blocks], ignore_index=True)
    actual_bridges = pd.concat([block.event_bridges for block in blocks], ignore_index=True)
    pd.testing.assert_frame_equal(actual_manual, expected_manual, check_dtype=False)
    pd.testing.assert_frame_equal(actual_dynamic, expected_dynamic, check_dtype=False)
    pd.testing.assert_frame_equal(actual_long, expected_long, check_dtype=False)
    pd.testing.assert_frame_equal(actual_events, expected_events, check_dtype=False)
    pd.testing.assert_frame_equal(actual_bridges, expected_bridges, check_dtype=False)
    assert actual_events["event_id"].is_unique


def test_parquet_partition_merge_streams_rows_without_pandas_concat(
    tmp_path: Path, monkeypatch
) -> None:
    first = tmp_path / "part-000.parquet"
    second = tmp_path / "part-001.parquet"
    write_parquet_partition_new(first, pd.DataFrame({"key": [1], "value": [1]}))
    write_parquet_partition_new(second, pd.DataFrame({"key": [2], "value": [2.5]}))
    monkeypatch.setattr(
        pd,
        "concat",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("Full-table pandas concat is forbidden")
        ),
    )
    target, rows = combine_parquet_partitions_new(
        [first, second],
        tmp_path / "canonical.parquet",
        row_group_size=1,
    )
    assert rows == 2
    result = pd.read_parquet(target)
    assert result.to_dict("list") == {"key": [1, 2], "value": [1.0, 2.5]}
    assert first.exists() and second.exists()
    with pytest.raises(FileExistsError):
        combine_parquet_partitions_new([first, second], target, row_group_size=1)


def test_legacy_v3_exact_validates_twelve_fields_and_tolerance() -> None:
    codes, values = _nearest_scale_fixture()
    row = _panel_row(start_doy=15, end_doy=64)
    for fields in LEGACY_FIELD_MAP.values():
        row[fields[0]] = 303.0
        row[fields[1]] = 303.0
    frame = pd.DataFrame([row])
    sidecar = legacy_v3_exact_sidecar(
        frame,
        codes,
        values,
        cell_index_column="spei_cell_index",
        expected_rows=1,
    )
    assert len(sidecar) == 1
    assert all(sidecar[column].iloc[0] == 303.0 for pair in LEGACY_FIELD_MAP.values() for column in pair)
    assert sidecar.attrs["fields"] == 12
    assert sidecar.attrs["max_absolute_difference"] == 0.0
    broken = frame.copy()
    broken.loc[0, "spei6_mean"] += 1e-5
    with pytest.raises(AssertionError, match="max abs difference"):
        legacy_v3_exact_sidecar(
            broken,
            codes,
            values,
            cell_index_column="spei_cell_index",
            expected_rows=1,
        )


def test_legacy_v3_exact_enforces_row_count_and_nan_parity() -> None:
    codes, values = _nearest_scale_fixture()
    row = _panel_row(start_doy=15, end_doy=64)
    for fields in LEGACY_FIELD_MAP.values():
        row[fields[0]] = 303.0
        row[fields[1]] = 303.0
    frame = pd.DataFrame([row])
    with pytest.raises(AssertionError, match="row count"):
        legacy_v3_exact_sidecar(
            frame,
            codes,
            values,
            cell_index_column="spei_cell_index",
            expected_rows=2,
        )
    frame.loc[0, "spei6_mean"] = np.nan
    with pytest.raises(AssertionError, match="missingness"):
        legacy_v3_exact_sidecar(
            frame,
            codes,
            values,
            cell_index_column="spei_cell_index",
            expected_rows=1,
        )


def test_monthly_runs_are_detected_on_full_series_then_day_weighted_to_window() -> None:
    codes = [201901, 201902, 201903, 201904, 201905, 201906]
    values = [-1.2, -1.3, 0.0, -2.0, -2.0, -2.0]
    events = detect_manual_spei_events(codes, values, threshold=-1.0, min_months=1)
    assert len(events) == 2
    summary = summarize_spei_events_for_window(
        events,
        window_start=date(2019, 2, 1),
        window_end=date(2019, 4, 15),
    )
    assert summary.any_event
    assert summary.event_count == 2
    assert summary.window_duration_days == 43
    assert summary.window_duration_periods == pytest.approx(1.0 + 15 / 30)
    assert summary.window_max_duration_days == 28
    assert summary.complete_duration_days == 150
    assert summary.complete_duration_periods == 5
    assert summary.complete_max_duration_days == 91
    assert summary.severity == pytest.approx(0.3 + 1.0 * 15 / 30)
    assert summary.mean_intensity == pytest.approx(
        summary.severity / summary.window_duration_periods
    )
    assert summary.min_spei == pytest.approx(-2.0)
    assert summary.peak_threshold_deficit == pytest.approx(1.0)
    assert summary.left_censored_events == 1
    assert summary.right_censored_events == 1


def test_strict_monthly_run_requires_three_months_below_minus_one_point_five() -> None:
    codes = [201901, 201902, 201903, 201904]
    assert detect_manual_spei_events(
        codes, [-2.0, -2.0, 0.0, -2.0], threshold=-1.5, min_months=3
    ) == []
    events = detect_manual_spei_events(
        codes, [-2.0, -2.0, -2.0, 0.0], threshold=-1.5, min_months=3
    )
    assert len(events) == 1
    summary = summarize_spei_events_for_window(
        events,
        window_start=date(2019, 1, 1),
        window_end=date(2019, 3, 31),
    )
    assert summary.window_duration_days == 90
    assert summary.min_spei == pytest.approx(-2.0)
    assert summary.peak_threshold_deficit == pytest.approx(0.5)


def test_two_week_unresolved_skips_numeric_and_writes_audit(tmp_path: Path) -> None:
    records, audit = prepare_two_week_records(
        [date(2019, 1, 1), date(2019, 1, 8)],
        [-1.2, -1.3],
        config_semantics="unresolved",
        timestamp_position=None,
        state_days=None,
    )
    assert records is None
    assert not audit.numeric_executed
    assert audit.status == "SKIPPED_UNRESOLVED_TIME_SEMANTICS"
    path = write_two_week_audit(tmp_path / "spei_2w_audit.json", audit)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["numeric_executed"] is False
    with pytest.raises(FileExistsError):
        write_two_week_audit(path, audit)


def test_two_week_requires_all_explicit_parameters_before_execution() -> None:
    timestamps = [date(2019, 1, 1), date(2019, 1, 8)]
    records, audit = prepare_two_week_records(
        timestamps,
        [-1.2, -1.3],
        config_semantics="period_start",
        timestamp_position=None,
        state_days=7,
    )
    assert records is None
    assert audit.status == "SKIPPED_INCOMPLETE_TIME_PARAMETERS"
    records, audit = prepare_two_week_records(
        timestamps,
        [-1.2, -1.3],
        config_semantics="period_start",
        timestamp_position="start",
        state_days=7,
    )
    assert audit.numeric_executed
    assert records is not None and len(records) == 2
    assert records[0].support_start == date(2019, 1, 1)
    assert records[0].support_end_exclusive == date(2019, 1, 8)
