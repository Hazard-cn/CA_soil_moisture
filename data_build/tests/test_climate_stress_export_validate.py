from __future__ import annotations

import sys
from pathlib import Path

import netCDF4 as nc
import numpy as np
import pandas as pd
import pytest


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "python"
sys.path.insert(0, str(SCRIPT_DIR))

from climate_stress.export import (  # noqa: E402
    CANONICAL_WINDOWS,
    LONG_KEY_COLUMNS,
    WIDE_KEY_COLUMNS,
    build_manifest,
    build_material_passport,
    build_stata_alias_map,
    build_variable_dictionary,
    export_panel_bundle,
    export_panel_bundle_streaming,
    generate_variable_metadata,
    manifest_input_records_from_inventory,
    pivot_long_to_wide,
    sha256_file,
    write_cf_netcdf,
    write_json_exclusive,
    write_parquet_exclusive,
    write_stata_bundle,
    write_stata_bundle_from_partitions,
    write_variable_dictionary,
)
from climate_stress.grid import build_v3_crosswalk  # noqa: E402
from climate_stress.core import SPEI_2W_PENDING_STATUS  # noqa: E402
from climate_stress.validate import (  # noqa: E402
    PanelValidationError,
    validate_cf_netcdf,
    validate_dta_roundtrip,
    validate_export_bundle_full,
    validate_historical_occurrence_rates,
    validate_legacy_fields,
    validate_long_panel,
    validate_netcdf_roundtrip,
    validate_parquet_roundtrip,
    validate_v3_coordinate_year_match,
    validate_wide_panel,
)


YEARS = tuple(range(2010, 2020))
PARTIAL_SCOPE_ID = "non2w-dual-severity"
PARTIAL_SCOPE_STATUS = "PARTIAL_SCOPE"
FULL_SCOPE_ID = "full-spei2w-dual-severity"
FULL_SCOPE_STATUS = "FULL_SCOPE"


def _partial_2w_evidence() -> dict[str, object]:
    return {
        "status": SPEI_2W_PENDING_STATUS,
        "numeric_executed": False,
        "endpoint_decision_status": "PENDING_USER_DECISION",
        "release_count": 0,
        "cell_count": 0,
        "canonical_field_count": 0,
        "event_rows": 0,
        "bridge_rows": 0,
        "accumulation_support": (
            "development_candidate: [label-13 days, label] inclusive"
        ),
        "event_state_support": (
            "development_candidate: [label, label+6 days] inclusive"
        ),
    }


def _full_2w_evidence(*, field_count: int = 1) -> dict[str, object]:
    return {
        "status": "EXECUTED",
        "numeric_executed": True,
        "endpoint_decision_status": "CONFIRMED",
        "release_count": 4,
        "cell_count": 2,
        "canonical_field_count": field_count,
        "event_rows": 0,
        "bridge_rows": 0,
        "accumulation_support": "confirmed: [label-13 days, label] inclusive",
        "event_state_support": "confirmed: [label, label+6 days] inclusive",
    }


def _crosswalk() -> pd.DataFrame:
    source = pd.DataFrame(
        {
            "grid_id": [101, 102],
            "latitude": [53.53, 53.53],
            "longitude": [73.58, 73.68],
        }
    )
    return build_v3_crosswalk(source, expected_unique=2)


def _long_panel() -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    crosswalk = _crosswalk()
    for year in YEARS:
        for window_index, window in enumerate(CANONICAL_WINDOWS):
            for cell in crosswalk.itertuples(index=False):
                rows.append(
                    {
                        "era01_cell_id": cell.era01_cell_id,
                        "grid_id_v3": cell.grid_id_v3,
                        "lat_idx": cell.lat_idx,
                        "lon_idx": cell.lon_idx,
                        "latitude": cell.latitude,
                        "longitude": cell.longitude,
                        "lat10": cell.lat10,
                        "lon10": cell.lon10,
                        "year": year,
                        "window": window,
                        "era5u8_tmean": year + window_index / 10 + cell.era01_cell_id / 1000,
                    }
                )
    return pd.DataFrame(rows)


def test_long_to_wide_pivot_and_parquet_roundtrip(tmp_path: Path) -> None:
    long = _long_panel()
    wide = pivot_long_to_wide(
        long,
        years=YEARS,
        windows=CANONICAL_WINDOWS,
        expected_long_rows=120,
        expected_wide_rows=20,
    )
    assert len(wide) == 20
    assert "era5u8_tmean" in wide
    assert "era5u8_tmean_v3pre30" in wide
    first = wide.loc[(wide["era01_cell_id"] == 1) & (wide["year"] == 2010)].iloc[0]
    assert first["era5u8_tmean"] == pytest.approx(2010.001)
    assert first["era5u8_tmean_v3pre30"] == pytest.approx(2010.101)

    long_path = write_parquet_exclusive(long, tmp_path / "long.parquet")
    result = validate_parquet_roundtrip(
        long,
        long_path,
        keys=("era01_cell_id", "year", "window"),
        sample_size=120,
    )
    assert result["max_abs_difference"] == 0
    long_repeat = write_parquet_exclusive(long, tmp_path / "long_repeat.parquet")
    assert sha256_file(long_path) == sha256_file(long_repeat)
    with pytest.raises(FileExistsError):
        write_parquet_exclusive(long, long_path)


def test_stata_aliases_are_order_independent_and_case_insensitively_unique() -> None:
    columns = [
        "foo",
        "FOO",
        "era01_cell_id",
        "a climate variable with punctuation and a name far beyond thirty two characters",
    ]
    forward = build_stata_alias_map(columns).set_index("original_name")["stata_name"].to_dict()
    reverse = build_stata_alias_map(reversed(columns)).set_index("original_name")["stata_name"].to_dict()
    assert forward == reverse
    assert forward["era01_cell_id"] == "era01_cell_id"
    assert len({value.casefold() for value in forward.values()}) == len(columns)
    assert all(len(value) <= 32 for value in forward.values())
    assert forward["foo"] != "foo"
    assert forward["FOO"] != "FOO"


def test_cf_netcdf_fixed_dimensions_mask_and_roundtrip(tmp_path: Path) -> None:
    long = _long_panel()
    path = write_cf_netcdf(
        long,
        tmp_path / "cube.nc",
        years=YEARS,
        windows=CANONICAL_WINDOWS,
        expected_rows=120,
        scope_id=PARTIAL_SCOPE_ID,
        scope_status=PARTIAL_SCOPE_STATUS,
    )
    crosswalk = long[
        [
            "era01_cell_id",
            "grid_id_v3",
            "lat_idx",
            "lon_idx",
            "latitude",
            "longitude",
            "lat10",
            "lon10",
        ]
    ].drop_duplicates()
    report = validate_cf_netcdf(
        path,
        crosswalk,
        years=YEARS,
        windows=CANONICAL_WINDOWS,
        metric_columns=("era5u8_tmean",),
    )
    assert report["selected_cells"] == 2
    with nc.Dataset(path) as dataset:
        assert {name: len(dataset.dimensions[name]) for name in dataset.dimensions} == {
            "time": 10,
            "window": 6,
            "latitude": 376,
            "longitude": 616,
        }
        mask = dataset.variables["selected_grid_mask"][:]
        assert int(mask.sum()) == 2
        assert mask[0, 0] == mask[0, 1] == 1
        assert mask[1, 0] == 0
        assert dataset.variables["era5u8_tmean"].dtype == np.dtype("float64")
        assert dataset.variables["era5u8_tmean"][0, 0, 0, 0] == pytest.approx(2010.001)
        assert np.ma.is_masked(dataset.variables["era5u8_tmean"][0, 0, 1, 0])
        assert "featureType" not in dataset.ncattrs()
        variable = dataset.variables["era5u8_tmean"]
        assert variable.source_product == "ERA5 hourly 2 m temperature"
        assert variable.threshold_rule
        assert variable.recovery_rule
        assert variable.calendar_rule
    roundtrip = validate_netcdf_roundtrip(
        long,
        path,
        sample_size=120,
        years=YEARS,
        windows=CANONICAL_WINDOWS,
    )
    assert roundtrip["max_abs_difference"] == 0
    repeated = write_cf_netcdf(
        long,
        tmp_path / "cube_repeat.nc",
        years=YEARS,
        windows=CANONICAL_WINDOWS,
        expected_rows=120,
        scope_id=PARTIAL_SCOPE_ID,
        scope_status=PARTIAL_SCOPE_STATUS,
    )
    assert sha256_file(path) == sha256_file(repeated)


def test_stata_bundle_is_grid_year_and_roundtrips_double_values(tmp_path: Path) -> None:
    long = _long_panel()
    wide = pivot_long_to_wide(
        long,
        years=YEARS,
        windows=CANONICAL_WINDOWS,
        expected_long_rows=120,
        expected_wide_rows=20,
    )
    dta, alias, merge_do, aliases = write_stata_bundle(
        wide,
        tmp_path / "panel.dta",
        tmp_path / "aliases.csv",
        tmp_path / "merge.do",
        expected_rows=20,
    )
    assert len(pd.read_stata(dta, convert_categoricals=False)) == 20
    assert aliases["stata_length"].le(32).all()
    assert "isid lat10 lon10 year" in merge_do.read_text(encoding="utf-8")
    report = validate_dta_roundtrip(wide, dta, alias, sample_size=20)
    assert report["max_abs_difference"] <= 1e-6
    dta_repeat, alias_repeat, merge_repeat, _ = write_stata_bundle(
        wide,
        tmp_path / "panel_repeat.dta",
        tmp_path / "aliases_repeat.csv",
        tmp_path / "merge_repeat.do",
        expected_rows=20,
    )
    assert sha256_file(dta) == sha256_file(dta_repeat)
    assert sha256_file(alias) == sha256_file(alias_repeat)
    assert sha256_file(merge_do) == sha256_file(merge_repeat)


def test_validation_failures_v3_match_legacy_and_historical_rate() -> None:
    long = _long_panel()
    duplicated = pd.concat([long, long.iloc[[0]]], ignore_index=True)
    with pytest.raises(PanelValidationError, match="duplicate"):
        validate_long_panel(
            duplicated,
            expected_cells=2,
            expected_rows=121,
            years=YEARS,
            windows=CANONICAL_WINDOWS,
        )

    wide = pivot_long_to_wide(
        long,
        years=YEARS,
        windows=CANONICAL_WINDOWS,
        expected_long_rows=120,
        expected_wide_rows=20,
    )
    validate_wide_panel(wide, expected_cells=2, expected_rows=20, years=YEARS)
    v3 = wide.loc[wide["year"].isin([2016, 2017]), list(WIDE_KEY_COLUMNS)].copy()
    matched = validate_v3_coordinate_year_match(wide, v3, expected_v3_rows=4)
    assert matched["matched_rows"] == 4
    missing_required = wide.loc[
        ~((wide["era01_cell_id"] == 1) & (wide["year"] == 2016))
    ]
    with pytest.raises(PanelValidationError, match="not matched"):
        validate_v3_coordinate_year_match(missing_required, v3, expected_v3_rows=4)

    keys = pd.DataFrame({"era01_cell_id": [1, 2], "year": [2016, 2016]})
    fields = [f"legacy_{index}" for index in range(12)]
    candidate = keys.assign(**{field: [0.0, 1.0] for field in fields})
    reference = candidate.copy()
    validate_legacy_fields(candidate, reference, fields, expected_rows=2)
    reference.loc[0, fields[0]] = 1e-4
    with pytest.raises(PanelValidationError, match="exceeds tolerance"):
        validate_legacy_fields(candidate, reference, fields, expected_rows=2)

    candidate_short = candidate.iloc[[0]].copy()
    with pytest.raises(PanelValidationError, match="reference rows"):
        validate_legacy_fields(candidate_short, candidate, fields, expected_rows=None)

    historical = pd.DataFrame({"hot": [1, 0] * 50})
    validate_historical_occurrence_rates(historical, {"hot": (0.5, 0.01)})
    with pytest.raises(PanelValidationError, match="outside tolerance"):
        validate_historical_occurrence_rates(historical, {"hot": (0.1, 0.01)})


def test_dictionary_passport_and_manifest_hashes(tmp_path: Path) -> None:
    long = _long_panel()
    dictionary = build_variable_dictionary(
        long,
        variable_metadata={
            "era5u8_tmean": {
                "units": "degC",
                "source_product": "ERA5",
                "history_period": "1981-2010",
            }
        },
        scope_id=PARTIAL_SCOPE_ID,
        scope_status=PARTIAL_SCOPE_STATUS,
    )
    metric = dictionary.set_index("variable").loc["era5u8_tmean"]
    assert metric["unit"] == "degC"
    dictionary_csv, dictionary_md = write_variable_dictionary(
        dictionary,
        tmp_path / "dictionary.csv",
        tmp_path / "dictionary.md",
    )
    assert dictionary_csv.is_file()
    assert "| variable | dtype |" in dictionary_md.read_text(encoding="utf-8")
    passport = build_material_passport(
        long,
        version_id="test-version",
        sources={"era5": "synthetic"},
        scope_id=PARTIAL_SCOPE_ID,
        scope_status=PARTIAL_SCOPE_STATUS,
        spei_2w_numeric_executed=False,
        spei_2w_output_included=False,
    )
    passport_path = write_json_exclusive(passport, tmp_path / "passport.json")
    config_path = tmp_path / "config.yaml"
    input_path = tmp_path / "input.txt"
    config_path.write_text("version: test\n", encoding="utf-8")
    input_path.write_text("input\n", encoding="utf-8")
    manifest = build_manifest(
        version_id="test-version",
        config_path=config_path,
        inputs={"input": input_path},
        outputs={"passport": passport_path},
    )
    assert manifest["config"]["sha256"] == sha256_file(config_path)
    assert manifest["inputs"]["input"]["sha256"] == sha256_file(input_path)
    assert manifest["outputs"]["passport"]["sha256"] == sha256_file(passport_path)
    assert set(LONG_KEY_COLUMNS).issubset(long.columns)


def test_complete_metadata_and_manifest_inventory_audit_api(tmp_path: Path) -> None:
    long = _long_panel()
    metadata = generate_variable_metadata(
        long.columns,
        scope_id=PARTIAL_SCOPE_ID,
        scope_status=PARTIAL_SCOPE_STATUS,
    )
    required = {
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
    }
    assert set(metadata) == set(long.columns)
    assert all(required == set(details) for details in metadata.values())
    assert metadata["era5u8_tmean"]["units"] == "degree_Celsius"

    source_metadata = generate_variable_metadata(
        [
            "chm_spei_s1_valid_days",
            "chm_spei_s1_event_expected_days",
            "chm_spei_s1_window_total_duration_periods_equiv",
            "gleam43a_smrz_fd_main_mean_onset_speed",
            "gleam43a_sms_fd_strict_coverage",
            "compound_sms_hot_p10_strict_count",
            "compound_smrz_hot_p10_sensitivity_gap2_count",
        ],
        gleam_layer_roles={"SMrz": "primary", "SMs": "supplementary"},
        scope_id=PARTIAL_SCOPE_ID,
        scope_status=PARTIAL_SCOPE_STATUS,
    )
    assert source_metadata["chm_spei_s1_valid_days"]["units"] == "day"
    assert source_metadata["chm_spei_s1_event_expected_days"]["units"] == "day"
    assert (
        source_metadata["chm_spei_s1_window_total_duration_periods_equiv"]["units"]
        == "month equivalent"
    )
    assert source_metadata["chm_spei_s1_valid_days"]["version"] == "V1.0"
    assert "CHM_Drought" in source_metadata["chm_spei_s1_valid_days"]["reference_id"]
    assert "PET=Penman" in source_metadata["chm_spei_s1_valid_days"]["reference_id"]
    assert "1961-2022" in source_metadata["chm_spei_s1_valid_days"]["reference_id"]
    assert "unknown" in source_metadata["chm_spei_s1_valid_days"]["history_period"]
    assert (
        source_metadata["gleam43a_smrz_fd_main_mean_onset_speed"]["units"]
        == "percentile points per pentad"
    )
    assert source_metadata["gleam43a_sms_fd_strict_coverage"]["layer_role"] == "supplementary"
    assert source_metadata["gleam43a_sms_fd_strict_coverage"]["variant_status"] == "quality_or_audit"
    assert source_metadata["compound_sms_hot_p10_strict_count"]["layer_role"] == "supplementary"
    assert source_metadata["compound_sms_hot_p10_strict_count"]["variant_status"] == "strict"
    assert source_metadata["compound_smrz_hot_p10_sensitivity_gap2_count"]["layer_role"] == "primary"
    assert source_metadata["compound_smrz_hot_p10_sensitivity_gap2_count"]["variant_status"] == "sensitivity"

    overridden = generate_variable_metadata(
        ["chm_spei_s1_mean"],
        source_overrides={"chm_spei_": {"reference_id": "custom-source"}},
        scope_id=PARTIAL_SCOPE_ID,
        scope_status=PARTIAL_SCOPE_STATUS,
    )
    assert overridden["chm_spei_s1_mean"]["reference_id"] == "custom-source"

    event_metadata = generate_variable_metadata(
        [
            "era5u8_hw_p90_total_duration_days",
            "gleam43a_smrz_fd_main_total_duration_days",
            "gleam43a_smrz_fd_strict_total_duration_days",
            "gleam43a_smrz_p10_event_main_gap0_total_duration_days",
            "gleam43a_smrz_p10_event_sensitivity_gap2_total_duration_days",
            "compound_smrz_hot_p10_main_gap0_total_duration_days",
            "compound_smrz_hot_p10_sensitivity_gap2_total_duration_days",
        ],
        scope_id=PARTIAL_SCOPE_ID,
        scope_status=PARTIAL_SCOPE_STATUS,
    )
    heatwave = event_metadata["era5u8_hw_p90_total_duration_days"]
    assert heatwave["minimum_duration"] == "3 consecutive valid days"
    assert "no gap merge" in heatwave["gap_rule"]
    fd_main = event_metadata["gleam43a_smrz_fd_main_total_duration_days"]
    assert fd_main["minimum_duration"] == "3 consecutive pentads"
    assert "first pentad" in fd_main["recovery_rule"]
    assert fd_main["history_period"] == "1981-2010 (30 years)"
    fd_strict = event_metadata["gleam43a_smrz_fd_strict_total_duration_days"]
    assert fd_strict["minimum_duration"] == "4 consecutive pentads"
    assert "2 consecutive" in fd_strict["recovery_rule"]
    daily_gap0 = event_metadata[
        "gleam43a_smrz_p10_event_main_gap0_total_duration_days"
    ]
    assert daily_gap0["minimum_duration"] == "5 consecutive valid days for daily P10 events"
    assert "no gap merge" in daily_gap0["gap_rule"]
    daily_gap2 = event_metadata[
        "gleam43a_smrz_p10_event_sensitivity_gap2_total_duration_days"
    ]
    assert "at most 2 days" in daily_gap2["gap_rule"]
    compound_gap0 = event_metadata[
        "compound_smrz_hot_p10_main_gap0_total_duration_days"
    ]
    assert compound_gap0["minimum_duration"] == "5 consecutive valid days"
    assert "no gap merge" in compound_gap0["gap_rule"]
    compound_gap2 = event_metadata[
        "compound_smrz_hot_p10_sensitivity_gap2_total_duration_days"
    ]
    assert "at most 2 days" in compound_gap2["gap_rule"]

    raw_path = tmp_path / "raw.bin"
    raw_path.write_bytes(b"raw-input")
    inventory = pd.DataFrame(
        {
            "asset_id": ["era5_2010"],
            "family": ["era5"],
            "role": ["hourly_temperature"],
            "path": [str(raw_path)],
            "exists": [True],
            "size_bytes": [raw_path.stat().st_size],
            "sha256": [sha256_file(raw_path)],
            "hash_algorithm": ["sha256-full-v1"],
            "hash_is_full": [True],
        }
    )
    inventory_path = tmp_path / "inventory.parquet"
    inventory.to_parquet(inventory_path, index=False)
    input_records = manifest_input_records_from_inventory(inventory_path)
    assert input_records["era5_2010"]["hash_is_full"] is True

    config_path = tmp_path / "config.yaml"
    config_path.write_text("version: test\n", encoding="utf-8")
    output_path = tmp_path / "output.bin"
    output_path.write_bytes(b"output")
    audit_path = tmp_path / "audit.json"
    audit_path.write_text("{}\n", encoding="utf-8")
    audit_directory = tmp_path / "audit_cache"
    audit_directory.mkdir()
    (audit_directory / "part-01.bin").write_bytes(b"one")
    (audit_directory / "part-02.bin").write_bytes(b"two")
    manifest = build_manifest(
        version_id="test-version",
        config_path=config_path,
        inputs=None,
        input_records=input_records,
        outputs={"output": output_path},
        output_record_paths={"output": "stages/export/bundle/output.bin"},
        audit_artifacts={"inventory": audit_path, "era_daily_cache": audit_directory},
        audit_record_paths={
            "inventory": "stages/assets/source_inventory.json",
            "era_daily_cache": "stages/era_daily/daily_cache",
        },
    )
    assert manifest["inputs"]["era5_2010"]["sha256"] == sha256_file(raw_path)
    assert manifest["outputs"]["output"]["path"] == "stages/export/bundle/output.bin"
    assert manifest["audit_artifacts"]["inventory"]["sha256"] == sha256_file(audit_path)
    assert manifest["audit_artifacts"]["era_daily_cache"]["kind"] == "directory"
    assert manifest["audit_artifacts"]["era_daily_cache"]["file_count"] == 2
    assert manifest["audit_artifacts"]["era_daily_cache"]["bytes"] == 6
    assert ".partial" not in str(manifest)


def test_full_chunked_bundle_validation_uses_aggregate_source(tmp_path: Path) -> None:
    long = _long_panel()
    long.loc[long.index[-1], "era5u8_tmean"] = np.nan
    aggregate_source = tmp_path / "aggregate.parquet"
    long.sample(frac=1, random_state=7).to_parquet(aggregate_source, index=False)
    canonical = long.sort_values(["year", "window", "era01_cell_id"]).reset_index(drop=True)
    exported_long = tmp_path / "long.parquet"
    canonical.to_parquet(exported_long, index=False)
    wide = pivot_long_to_wide(
        long,
        years=YEARS,
        windows=CANONICAL_WINDOWS,
        expected_long_rows=120,
        expected_wide_rows=20,
    )
    exported_wide = tmp_path / "wide.parquet"
    wide.to_parquet(exported_wide, index=False)
    netcdf = write_cf_netcdf(
        long,
        tmp_path / "cube.nc",
        years=YEARS,
        windows=CANONICAL_WINDOWS,
        expected_rows=120,
        scope_id=PARTIAL_SCOPE_ID,
        scope_status=PARTIAL_SCOPE_STATUS,
    )
    dta, aliases, _, _ = write_stata_bundle(
        wide,
        tmp_path / "panel.dta",
        tmp_path / "aliases.csv",
        tmp_path / "merge.do",
        expected_rows=20,
    )
    report = validate_export_bundle_full(
        aggregate_source,
        exported_long,
        exported_wide,
        netcdf,
        dta,
        aliases,
        years=YEARS,
        windows=CANONICAL_WINDOWS,
        metric_batch_size=1,
        dta_row_batch_size=7,
        spatial_row_block=31,
    )
    assert report["long_parquet"]["rows"] == 120
    assert report["wide_parquet"]["rows"] == 20
    assert report["netcdf"]["nonselected_values_checked"] > 0
    assert report["dta"]["rows"] == 20
    assert all(value["max_abs_difference"] <= 1e-6 for value in report.values())

    corrupted = canonical.copy()
    corrupted.loc[corrupted.index[-2], "era5u8_tmean"] += 0.5
    corrupted_path = tmp_path / "long_corrupted.parquet"
    corrupted.to_parquet(corrupted_path, index=False)
    with pytest.raises(PanelValidationError, match="exceeds tolerance"):
        from climate_stress.validate import validate_long_parquet_full

        validate_long_parquet_full(
            aggregate_source,
            corrupted_path,
            years=YEARS,
            windows=CANONICAL_WINDOWS,
            metric_batch_size=1,
        )


def test_netcdf_rejects_any_nonselected_value(tmp_path: Path) -> None:
    long = _long_panel()
    path = write_cf_netcdf(
        long,
        tmp_path / "cube.nc",
        years=YEARS,
        windows=CANONICAL_WINDOWS,
        expected_rows=120,
        scope_id=PARTIAL_SCOPE_ID,
        scope_status=PARTIAL_SCOPE_STATUS,
    )
    with nc.Dataset(path, "r+") as dataset:
        dataset.variables["era5u8_tmean"][9, 5, 375, 615] = 1.0
    crosswalk = long[list(LONG_KEY_COLUMNS[:-2])].drop_duplicates()
    with pytest.raises(PanelValidationError, match="outside selected grid"):
        validate_cf_netcdf(
            path,
            crosswalk,
            years=YEARS,
            windows=CANONICAL_WINDOWS,
            metric_columns=("era5u8_tmean",),
            spatial_row_block=17,
        )


def _partition_long_by_cells(long: pd.DataFrame, root: Path, cells_per_file: int) -> Path:
    root.mkdir()
    cells = sorted(long["era01_cell_id"].unique())
    for index, start in enumerate(range(0, len(cells), cells_per_file)):
        selected = cells[start : start + cells_per_file]
        current = long.loc[long["era01_cell_id"].isin(selected)].copy()
        current.to_parquet(root / f"part-{index:03d}.parquet", index=False)
    return root


def _streaming_bundle(
    tmp_path: Path,
    partition_root: Path,
    output_name: str,
    *,
    scope_id: str = PARTIAL_SCOPE_ID,
    scope_status: str = PARTIAL_SCOPE_STATUS,
    spei_2w_evidence: dict[str, object] | None = None,
) -> tuple[object, dict[str, object]]:
    config = tmp_path / f"{output_name}.yaml"
    raw = tmp_path / f"{output_name}.raw"
    config.write_text("version_id: test\n", encoding="utf-8")
    raw.write_text("synthetic\n", encoding="utf-8")
    return export_panel_bundle_streaming(
        partition_root,
        _crosswalk(),
        tmp_path / output_name,
        config_path=config,
        inputs={"synthetic": raw},
        years=YEARS,
        windows=CANONICAL_WINDOWS,
        expected_long_rows=120,
        expected_wide_rows=20,
        version_id="streaming-test",
        gleam_layer_roles={"SMrz": "primary", "SMs": "supplementary"},
        scope_id=scope_id,
        scope_status=scope_status,
        spei_2w_numeric_executed=scope_status == FULL_SCOPE_STATUS,
        spei_2w_output_included=scope_status == FULL_SCOPE_STATUS,
        spei_2w_evidence=(
            spei_2w_evidence
            if spei_2w_evidence is not None
            else _partial_2w_evidence()
        ),
    )


def test_streaming_bundle_is_block_bounded_and_value_equivalent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    long = _long_panel()
    partitions = _partition_long_by_cells(long, tmp_path / "parts-one", 1)
    real_read = pd.read_parquet
    reads: list[tuple[str, object, int]] = []

    def monitored_read(path, *args, **kwargs):
        frame = real_read(path, *args, **kwargs)
        reads.append((str(path), kwargs.get("columns"), len(frame)))
        return frame

    monkeypatch.setattr(pd, "read_parquet", monitored_read)
    paths, report = _streaming_bundle(tmp_path, partitions, "bundle-one")
    assert report["streaming_contract"]["long_partition_rows_max"] == 60
    assert report["streaming_contract"]["wide_partition_rows_max"] == 10
    assert report["streaming_contract"]["dta_partition_rows_max"] == 10
    assert report["streaming_contract"]["full_long_dataframe_forbidden"] is True
    output_contract = __import__("json").loads(
        Path(report["output_contract"]).read_text(encoding="utf-8")
    )
    assert output_contract["scope_id"] == "non2w-dual-severity"
    assert output_contract["status"] == "PARTIAL_SCOPE"
    assert output_contract["spei_2w"]["numeric_executed"] is False
    assert output_contract["spei_2w"]["output_included"] is False
    assert not any(
        column.startswith("chm_spei_2w_")
        for column in pd.read_parquet(paths.long_parquet).columns
    )
    assert output_contract["compound_severity"]["mixed_unit_scalar_included"] is False
    assert max(
        rows
        for path, columns, rows in reads
        if str(partitions) in path and columns is None
    ) == 60
    observed_long = real_read(paths.long_parquet).sort_values(
        ["era01_cell_id", "year", "window"]
    ).reset_index(drop=True)
    expected_long = long.sort_values(
        ["era01_cell_id", "year", "window"]
    ).reset_index(drop=True)
    pd.testing.assert_frame_equal(observed_long, expected_long, check_dtype=False)
    observed_wide = real_read(paths.wide_parquet)
    expected_wide = pivot_long_to_wide(
        long,
        years=YEARS,
        windows=CANONICAL_WINDOWS,
        expected_long_rows=120,
        expected_wide_rows=20,
    )
    pd.testing.assert_frame_equal(observed_wide, expected_wide, check_dtype=False)
    aliases = pd.read_csv(paths.alias_map, encoding="utf-8-sig")
    reverse = aliases.set_index("stata_name")["original_name"].to_dict()
    observed_dta = pd.read_stata(paths.stata, convert_categoricals=False).rename(
        columns=reverse
    )
    pd.testing.assert_frame_equal(
        observed_dta[expected_wide.columns],
        expected_wide,
        check_dtype=False,
        check_exact=False,
        atol=1e-10,
        rtol=0,
    )


def test_streaming_bundle_is_equivalent_across_spatial_block_sizes(
    tmp_path: Path,
) -> None:
    long = _long_panel()
    one = _partition_long_by_cells(long, tmp_path / "parts-a", 1)
    two = _partition_long_by_cells(long, tmp_path / "parts-b", 2)
    paths_a, _report_a = _streaming_bundle(tmp_path, one, "bundle-a")
    paths_b, _report_b = _streaming_bundle(tmp_path, two, "bundle-b")
    left = pd.read_parquet(paths_a.long_parquet).sort_values(
        ["era01_cell_id", "year", "window"]
    ).reset_index(drop=True)
    right = pd.read_parquet(paths_b.long_parquet).sort_values(
        ["era01_cell_id", "year", "window"]
    ).reset_index(drop=True)
    pd.testing.assert_frame_equal(left, right, check_dtype=False)
    wide_a = pd.read_parquet(paths_a.wide_parquet).sort_values(
        ["era01_cell_id", "year"]
    ).reset_index(drop=True)
    wide_b = pd.read_parquet(paths_b.wide_parquet).sort_values(
        ["era01_cell_id", "year"]
    ).reset_index(drop=True)
    pd.testing.assert_frame_equal(wide_a, wide_b, check_dtype=False)
    with nc.Dataset(paths_a.netcdf) as first, nc.Dataset(paths_b.netcdf) as second:
        assert set(first.variables) == set(second.variables)
        for name in first.variables:
            first_masked = np.ma.asarray(first.variables[name][:])
            second_masked = np.ma.asarray(second.variables[name][:])
            np.testing.assert_array_equal(
                np.ma.getmaskarray(first_masked), np.ma.getmaskarray(second_masked)
            )
            first_values = np.asarray(first_masked.data)
            second_values = np.asarray(second_masked.data)
            if first_values.dtype.kind in "SUO":
                assert first_values.tolist() == second_values.tolist()
            else:
                np.testing.assert_allclose(
                    first_values, second_values, rtol=0, atol=0, equal_nan=True
                )
    aliases_a = pd.read_csv(paths_a.alias_map, encoding="utf-8-sig")
    aliases_b = pd.read_csv(paths_b.alias_map, encoding="utf-8-sig")
    pd.testing.assert_frame_equal(aliases_a, aliases_b)
    reverse = aliases_a.set_index("stata_name")["original_name"].to_dict()
    dta_a = pd.read_stata(paths_a.stata, convert_categoricals=False).rename(
        columns=reverse
    )
    dta_b = pd.read_stata(paths_b.stata, convert_categoricals=False).rename(
        columns=reverse
    )
    pd.testing.assert_frame_equal(dta_a, dta_b, check_dtype=False)


def test_full_scope_streaming_export_requires_and_describes_2w_fields(
    tmp_path: Path,
) -> None:
    long = _long_panel()
    long["chm_spei_2w_k10_main_count"] = 0.0
    long["chm_spei_2w_k15_strict_count"] = 0.0
    long["chm_spei_2w_k10_main_window_total_duration_releases_equiv"] = 0.0
    long["chm_spei_2w_k10_main_severity_spei_releases"] = 0.0
    partitions = _partition_long_by_cells(long, tmp_path / "full-parts", 1)
    evidence = _full_2w_evidence(field_count=4)
    paths, report = _streaming_bundle(
        tmp_path,
        partitions,
        "full-bundle",
        scope_id=FULL_SCOPE_ID,
        scope_status=FULL_SCOPE_STATUS,
        spei_2w_evidence=evidence,
    )
    contract = __import__("json").loads(
        Path(report["output_contract"]).read_text(encoding="utf-8")
    )
    assert contract["scope_id"] == FULL_SCOPE_ID
    assert contract["status"] == FULL_SCOPE_STATUS
    assert contract["spei_2w"]["numeric_executed"] is True
    assert contract["spei_2w"]["output_included"] is True
    assert contract["spei_2w"]["stage_evidence"] == evidence
    dictionary = pd.read_csv(paths.variable_dictionary_csv, encoding="utf-8-sig").set_index(
        "variable"
    )
    main = dictionary.loc["chm_spei_2w_k10_main_count"]
    strict = dictionary.loc["chm_spei_2w_k15_strict_count"]
    assert main["unit"] == "count"
    assert "K=-1 primary" in main["threshold_rule"]
    assert main["minimum_duration"] == "1 observed 7-day release-state unit"
    assert "K=-1.5 strict" in strict["threshold_rule"]
    assert strict["minimum_duration"] == "3 consecutive 7-day release-state units"
    assert "confirmed:" in main["time_window"]
    assert "[label-13 days, label]" in main["time_window"]
    assert "[label, label+6 days]" in main["time_window"]
    assert (
        dictionary.loc[
            "chm_spei_2w_k10_main_window_total_duration_releases_equiv",
            "unit",
        ]
        == "7-day state unit equivalent"
    )
    assert (
        dictionary.loc[
            "chm_spei_2w_k10_main_severity_spei_releases", "unit"
        ]
        == "standardized-index release"
    )
    with nc.Dataset(paths.netcdf) as dataset:
        assert dataset.getncattr("output_scope_id") == FULL_SCOPE_ID
        assert dataset.getncattr("output_scope_status") == FULL_SCOPE_STATUS
    manifest = __import__("json").loads(paths.manifest.read_text(encoding="utf-8"))
    assert manifest["metadata"]["spei_2w_stage_evidence"] == evidence


def test_full_scope_export_fails_closed_on_2w_evidence_or_schema_drift(
    tmp_path: Path,
) -> None:
    without_2w = _partition_long_by_cells(
        _long_panel(), tmp_path / "missing-2w-parts", 1
    )
    with pytest.raises(ValueError, match="requires canonical chm_spei_2w"):
        _streaming_bundle(
            tmp_path,
            without_2w,
            "missing-2w-bundle",
            scope_id=FULL_SCOPE_ID,
            scope_status=FULL_SCOPE_STATUS,
            spei_2w_evidence=_full_2w_evidence(field_count=1),
        )

    invalid_audit = _full_2w_evidence(field_count=1)
    invalid_audit.update(
        {
            "status": SPEI_2W_PENDING_STATUS,
            "numeric_executed": False,
            "endpoint_decision_status": "PENDING_USER_DECISION",
        }
    )
    with pytest.raises(ValueError, match="numeric status differ"):
        _streaming_bundle(
            tmp_path,
            without_2w,
            "false-audit-bundle",
            scope_id=FULL_SCOPE_ID,
            scope_status=FULL_SCOPE_STATUS,
            spei_2w_evidence=invalid_audit,
        )

    long = _long_panel()
    long["chm_spei_2w_k10_main_count"] = 0.0
    one_field = _partition_long_by_cells(long, tmp_path / "field-drift-parts", 1)
    with pytest.raises(ValueError, match="field count differs"):
        _streaming_bundle(
            tmp_path,
            one_field,
            "field-drift-bundle",
            scope_id=FULL_SCOPE_ID,
            scope_status=FULL_SCOPE_STATUS,
            spei_2w_evidence=_full_2w_evidence(field_count=2),
        )

    with pytest.raises(TypeError):
        generate_variable_metadata(["chm_spei_2w_k10_main_count"])


def test_nonstreaming_export_rejects_partial_leak_and_full_field_drift(
    tmp_path: Path,
) -> None:
    config = tmp_path / "nonstreaming.yaml"
    raw = tmp_path / "nonstreaming.raw"
    config.write_text("version_id: test\n", encoding="utf-8")
    raw.write_text("synthetic\n", encoding="utf-8")
    long = _long_panel()
    long["chm_spei_2w_k10_main_count"] = 0.0
    with pytest.raises(ValueError, match="field count differs"):
        export_panel_bundle(
            long,
            tmp_path / "partial-leak",
            config_path=config,
            inputs={"synthetic": raw},
            years=YEARS,
            windows=CANONICAL_WINDOWS,
            expected_long_rows=120,
            expected_wide_rows=20,
            scope_id=PARTIAL_SCOPE_ID,
            scope_status=PARTIAL_SCOPE_STATUS,
            spei_2w_numeric_executed=False,
            spei_2w_output_included=False,
            spei_2w_evidence=_partial_2w_evidence(),
        )

    paths, exported_long, _wide = export_panel_bundle(
        long,
        tmp_path / "full-match",
        config_path=config,
        inputs={"synthetic": raw},
        years=YEARS,
        windows=CANONICAL_WINDOWS,
        expected_long_rows=120,
        expected_wide_rows=20,
        scope_id=FULL_SCOPE_ID,
        scope_status=FULL_SCOPE_STATUS,
        spei_2w_numeric_executed=True,
        spei_2w_output_included=True,
        spei_2w_evidence=_full_2w_evidence(field_count=1),
    )
    assert paths.long_parquet.is_file()
    assert "chm_spei_2w_k10_main_count" in exported_long

    with pytest.raises(ValueError, match="field count differs"):
        export_panel_bundle(
            long,
            tmp_path / "full-mismatch",
            config_path=config,
            inputs={"synthetic": raw},
            years=YEARS,
            windows=CANONICAL_WINDOWS,
            expected_long_rows=120,
            expected_wide_rows=20,
            scope_id=FULL_SCOPE_ID,
            scope_status=FULL_SCOPE_STATUS,
            spei_2w_numeric_executed=True,
            spei_2w_output_included=True,
            spei_2w_evidence=_full_2w_evidence(field_count=2),
        )
