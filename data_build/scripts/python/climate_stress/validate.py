"""Fail-closed validation gates for canonical climate-stress exports."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping, Sequence

import netCDF4 as nc
import numpy as np
import pandas as pd

from .export import (
    CANONICAL_WINDOWS,
    LONG_KEY_COLUMNS,
    SPATIAL_COLUMNS,
    WINDOW_SUFFIXES,
    WIDE_KEY_COLUMNS,
    canonicalize_long_panel,
)
from .grid import TARGET_GRID, TargetGridSpec, validate_v3_crosswalk


class PanelValidationError(AssertionError):
    """Raised when an artifact violates a frozen acceptance criterion."""


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise PanelValidationError(message)


def _rounded_tenth(values: pd.Series) -> np.ndarray:
    numeric = pd.to_numeric(values, errors="raise").to_numpy(dtype=np.float64)
    return np.floor(numeric * 10.0 + 0.5).astype(np.int32)


def validate_long_panel(
    long_panel: pd.DataFrame,
    *,
    expected_cells: int = 22_180,
    expected_rows: int = 1_330_800,
    years: Sequence[int] = tuple(range(2010, 2020)),
    windows: Sequence[str] = CANONICAL_WINDOWS,
    spec: TargetGridSpec = TARGET_GRID,
) -> dict[str, int]:
    """Validate row support, keys, crosswalk, and closed-window arithmetic."""

    try:
        canonical = canonicalize_long_panel(
            long_panel, years=years, windows=windows, expected_rows=expected_rows
        )
    except (TypeError, ValueError) as exc:
        raise PanelValidationError(str(exc)) from exc
    crosswalk = canonical[list(SPATIAL_COLUMNS)].drop_duplicates()
    _check(len(crosswalk) == expected_cells, f"Expected {expected_cells:,} selected cells")
    try:
        validate_v3_crosswalk(crosswalk, expected_unique=expected_cells, spec=spec)
    except ValueError as exc:
        raise PanelValidationError(str(exc)) from exc
    counts = canonical.groupby(["year", "window"], observed=True)["era01_cell_id"].nunique()
    _check(len(counts) == len(years) * len(windows), "Missing year-window combinations")
    _check((counts == expected_cells).all(), "Every year-window must contain every selected cell")

    bounds = {"window_start_doy", "window_end_doy", "window_days"}
    if bounds.issubset(canonical.columns):
        start = pd.to_numeric(canonical["window_start_doy"], errors="coerce")
        end = pd.to_numeric(canonical["window_end_doy"], errors="coerce")
        days = pd.to_numeric(canonical["window_days"], errors="coerce")
        complete = start.notna() & end.notna() & days.notna()
        _check(
            ((end[complete] - start[complete] + 1) == days[complete]).all(),
            "window_days must be computed after clipping as a closed interval",
        )
        partial = start.notna().astype(int) + end.notna().astype(int) + days.notna().astype(int)
        _check(partial.isin([0, 3]).all(), "Window boundaries must be entirely present or absent")
    return {
        "rows": len(canonical),
        "selected_cells": len(crosswalk),
        "years": len(years),
        "windows": len(windows),
    }


def validate_wide_panel(
    wide_panel: pd.DataFrame,
    *,
    expected_cells: int = 22_180,
    expected_rows: int = 221_800,
    years: Sequence[int] = tuple(range(2010, 2020)),
    spec: TargetGridSpec = TARGET_GRID,
) -> dict[str, int]:
    missing = sorted(set(WIDE_KEY_COLUMNS).difference(wide_panel.columns))
    _check(not missing, f"Wide panel is missing keys: {missing}")
    _check(len(wide_panel) == expected_rows, f"Expected {expected_rows:,} wide rows")
    _check(
        not wide_panel.duplicated(["era01_cell_id", "year"]).any(),
        "Wide panel contains duplicate cell-years",
    )
    _check(
        set(pd.to_numeric(wide_panel["year"], errors="raise").astype(int))
        == {int(year) for year in years},
        "Wide panel year support is incorrect",
    )
    crosswalk = wide_panel[list(SPATIAL_COLUMNS)].drop_duplicates()
    try:
        validate_v3_crosswalk(crosswalk, expected_unique=expected_cells, spec=spec)
    except ValueError as exc:
        raise PanelValidationError(str(exc)) from exc
    counts = wide_panel.groupby("year")["era01_cell_id"].nunique()
    _check((counts == expected_cells).all(), "Every wide year must contain every selected cell")
    return {"rows": len(wide_panel), "selected_cells": len(crosswalk), "years": len(years)}


def _coordinate_year_keys(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"year"}
    _check(required.issubset(frame.columns), "Coordinate-year table lacks year")
    output = frame.copy()
    if "lat10" not in output:
        _check("latitude" in output, "Coordinate-year table lacks latitude/lat10")
        output["lat10"] = _rounded_tenth(output["latitude"])
    if "lon10" not in output:
        _check("longitude" in output, "Coordinate-year table lacks longitude/lon10")
        output["lon10"] = _rounded_tenth(output["longitude"])
    output["year"] = pd.to_numeric(output["year"], errors="raise").astype(np.int16)
    output["lat10"] = pd.to_numeric(output["lat10"], errors="raise").astype(np.int32)
    output["lon10"] = pd.to_numeric(output["lon10"], errors="raise").astype(np.int32)
    return output


def validate_v3_coordinate_year_match(
    climate_wide: pd.DataFrame,
    v3_main: pd.DataFrame,
    *,
    expected_v3_rows: int = 69_038,
    coordinate_tolerance: float = 1e-8,
) -> dict[str, int]:
    """Require all current V3 rows to match the new panel by coordinates/year."""

    climate = _coordinate_year_keys(climate_wide)
    v3 = _coordinate_year_keys(v3_main)
    keys = ["lat10", "lon10", "year"]
    _check(len(v3) == expected_v3_rows, f"Expected {expected_v3_rows:,} V3 rows")
    _check(not climate.duplicated(keys).any(), "Climate panel is not unique by coordinate-year")
    _check(not v3.duplicated(keys).any(), "V3 main is not unique by coordinate-year")
    climate_columns = keys + [column for column in ("latitude", "longitude") if column in climate]
    merged = v3.merge(
        climate[climate_columns], on=keys, how="left", suffixes=("_v3", "_climate"), indicator=True
    )
    unmatched = int(merged["_merge"].ne("both").sum())
    _check(unmatched == 0, f"V3 coordinate-year rows not matched: {unmatched}")
    for coordinate in ("latitude", "longitude"):
        left, right = f"{coordinate}_v3", f"{coordinate}_climate"
        if left in merged and right in merged:
            difference = np.abs(
                pd.to_numeric(merged[left], errors="coerce")
                - pd.to_numeric(merged[right], errors="coerce")
            )
            _check(
                bool((difference <= coordinate_tolerance).all()),
                f"{coordinate} differs beyond tolerance",
            )
    return {"v3_rows": len(v3), "matched_rows": len(v3), "unmatched_rows": unmatched}


def validate_legacy_fields(
    candidate: pd.DataFrame,
    reference: pd.DataFrame,
    fields: Sequence[str] | Mapping[str, str],
    *,
    keys: Sequence[str] = ("era01_cell_id", "year"),
    tolerance: float = 1e-6,
    required_field_count: int = 12,
    expected_rows: int | None = 69_038,
) -> pd.DataFrame:
    """Compare the isolated legacy SPEI sidecar in both key directions."""

    mapping = dict(fields) if isinstance(fields, Mapping) else {field: field for field in fields}
    _check(
        len(mapping) == required_field_count,
        f"Legacy comparison requires exactly {required_field_count} fields",
    )
    _check(
        len(set(mapping)) == len(mapping) and len(set(mapping.values())) == len(mapping),
        "Legacy field mapping must be one-to-one",
    )
    for label, frame in (("candidate", candidate), ("reference", reference)):
        missing_keys = sorted(set(keys).difference(frame.columns))
        _check(not missing_keys, f"{label} lacks legacy keys: {missing_keys}")
        _check(not frame.duplicated(list(keys)).any(), f"{label} legacy keys are not unique")
        if expected_rows is not None:
            _check(
                len(frame) == expected_rows,
                f"Expected {expected_rows:,} {label} legacy rows, found {len(frame):,}",
            )
    candidate_fields = list(mapping)
    reference_fields = list(mapping.values())
    _check(not set(candidate_fields).difference(candidate.columns), "Candidate legacy fields are missing")
    _check(not set(reference_fields).difference(reference.columns), "Reference legacy fields are missing")

    left = candidate[list(keys) + candidate_fields].copy()
    right = reference[list(keys) + reference_fields].copy()
    right = right.rename(columns={value: f"__reference_{key}" for key, value in mapping.items()})
    merged = left.merge(
        right,
        on=list(keys),
        how="outer",
        indicator=True,
        validate="one_to_one",
    )
    candidate_only = int(merged["_merge"].eq("left_only").sum())
    reference_only = int(merged["_merge"].eq("right_only").sum())
    _check(candidate_only == 0, "Legacy candidate rows do not all match reference")
    _check(reference_only == 0, "Legacy reference rows do not all match candidate")
    matched_rows = int(merged["_merge"].eq("both").sum())
    if expected_rows is not None:
        _check(matched_rows == expected_rows, "Legacy matched row count is incorrect")
    rows: list[dict[str, float | int | str]] = []
    for candidate_field in candidate_fields:
        observed = pd.to_numeric(merged[candidate_field], errors="coerce").to_numpy(dtype=np.float64)
        expected = pd.to_numeric(
            merged[f"__reference_{candidate_field}"], errors="coerce"
        ).to_numpy(dtype=np.float64)
        same_missing = np.isnan(observed) == np.isnan(expected)
        finite = np.isfinite(observed) & np.isfinite(expected)
        max_difference = float(np.max(np.abs(observed[finite] - expected[finite]))) if finite.any() else 0.0
        _check(bool(same_missing.all()), f"Legacy missingness differs for {candidate_field}")
        _check(max_difference <= tolerance, f"Legacy field {candidate_field} exceeds tolerance")
        rows.append(
            {
                "field": candidate_field,
                "reference_field": mapping[candidate_field],
                "candidate_rows": len(candidate),
                "reference_rows": len(reference),
                "matched_rows": matched_rows,
                "candidate_only_rows": candidate_only,
                "reference_only_rows": reference_only,
                "compared": int(finite.sum()),
                "max_abs_difference": max_difference,
            }
        )
    return pd.DataFrame(rows)


def _sample(frame: pd.DataFrame, sample_size: int, seed: int) -> pd.DataFrame:
    if sample_size <= 0:
        raise ValueError("sample_size must be positive")
    if len(frame) <= sample_size:
        return frame.copy()
    return frame.sample(n=sample_size, random_state=seed).copy()


def _compare_frame_sample(
    expected: pd.DataFrame,
    observed: pd.DataFrame,
    *,
    keys: Sequence[str],
    columns: Sequence[str] | None,
    sample_size: int,
    tolerance: float,
    seed: int,
) -> dict[str, int | float]:
    _check(not expected.duplicated(list(keys)).any(), "Expected roundtrip keys are not unique")
    _check(not observed.duplicated(list(keys)).any(), "Observed roundtrip keys are not unique")
    sample = _sample(expected, sample_size, seed)
    candidate_columns = list(columns) if columns is not None else [
        column
        for column in expected.columns
        if column in observed.columns and column not in keys and pd.api.types.is_numeric_dtype(expected[column])
    ]
    merged = sample[list(keys) + candidate_columns].merge(
        observed[list(keys) + candidate_columns],
        on=list(keys),
        how="left",
        suffixes=("_expected", "_observed"),
        indicator=True,
    )
    _check(merged["_merge"].eq("both").all(), "Roundtrip sample contains unmatched keys")
    max_difference = 0.0
    for column in candidate_columns:
        expected_values = pd.to_numeric(merged[f"{column}_expected"], errors="coerce").to_numpy(
            dtype=np.float64
        )
        observed_values = pd.to_numeric(merged[f"{column}_observed"], errors="coerce").to_numpy(
            dtype=np.float64
        )
        _check(
            bool((np.isnan(expected_values) == np.isnan(observed_values)).all()),
            f"Roundtrip missingness differs for {column}",
        )
        finite = np.isfinite(expected_values) & np.isfinite(observed_values)
        difference = (
            float(np.max(np.abs(expected_values[finite] - observed_values[finite])))
            if finite.any()
            else 0.0
        )
        max_difference = max(max_difference, difference)
        _check(difference <= tolerance, f"Roundtrip field {column} exceeds tolerance")
    return {
        "sample_rows": len(sample),
        "numeric_columns": len(candidate_columns),
        "max_abs_difference": max_difference,
    }


def _chunks(values: Sequence[str], size: int) -> Iterable[list[str]]:
    if size <= 0:
        raise ValueError("batch size must be positive")
    for start in range(0, len(values), size):
        yield list(values[start : start + size])


def _parquet_metric_columns(path: str | Path) -> list[str]:
    import pyarrow as pa
    import pyarrow.parquet as pq

    schema = pq.ParquetFile(path).schema_arrow
    metrics: list[str] = []
    unsupported: list[str] = []
    for field in schema:
        if field.name in LONG_KEY_COLUMNS:
            continue
        if (
            pa.types.is_integer(field.type)
            or pa.types.is_floating(field.type)
            or pa.types.is_boolean(field.type)
            or pa.types.is_decimal(field.type)
        ):
            metrics.append(field.name)
        else:
            unsupported.append(f"{field.name}:{field.type}")
    _check(not unsupported, f"Canonical source contains nonnumeric measures: {unsupported}")
    return metrics


def _parquet_partition(
    dataset: object,
    columns: Sequence[str],
    *,
    year: int,
    window: str | None = None,
) -> pd.DataFrame:
    import pyarrow.dataset as ds

    expression = ds.field("year") == int(year)
    if window is not None:
        expression = expression & (ds.field("window") == str(window))
    table = dataset.to_table(columns=list(columns), filter=expression)
    return table.to_pandas()


def _sort(frame: pd.DataFrame, keys: Sequence[str]) -> pd.DataFrame:
    return frame.sort_values(list(keys), kind="mergesort").reset_index(drop=True)


def _compare_keys(
    expected: pd.DataFrame,
    observed: pd.DataFrame,
    keys: Sequence[str],
    *,
    label: str,
) -> None:
    _check(len(expected) == len(observed), f"{label} key row count differs")
    for key in keys:
        _check(key in expected and key in observed, f"{label} lacks key {key}")
        left = expected[key]
        right = observed[key]
        _check(not left.isna().any() and not right.isna().any(), f"{label} key {key} is missing")
        if pd.api.types.is_numeric_dtype(left) and pd.api.types.is_numeric_dtype(right):
            equal = np.array_equal(
                pd.to_numeric(left, errors="raise").to_numpy(),
                pd.to_numeric(right, errors="raise").to_numpy(),
            )
        else:
            equal = np.array_equal(left.astype(str).to_numpy(), right.astype(str).to_numpy())
        _check(bool(equal), f"{label} key {key} differs")


def _compare_numeric_arrays(
    expected: pd.Series | np.ndarray,
    observed: pd.Series | np.ndarray,
    *,
    field: str,
    tolerance: float,
) -> dict[str, int | float]:
    left = pd.to_numeric(pd.Series(expected), errors="coerce").to_numpy(dtype=np.float64)
    right = pd.to_numeric(pd.Series(observed), errors="coerce").to_numpy(dtype=np.float64)
    _check(len(left) == len(right), f"Full roundtrip row count differs for {field}")
    left_missing = np.isnan(left)
    right_missing = np.isnan(right)
    _check(
        bool(np.array_equal(left_missing, right_missing)),
        f"Full roundtrip missingness differs for {field}",
    )
    left_infinite = np.isinf(left)
    right_infinite = np.isinf(right)
    _check(
        bool(np.array_equal(left_infinite, right_infinite)),
        f"Full roundtrip nonfinite values differ for {field}",
    )
    if left_infinite.any():
        _check(
            bool(np.array_equal(left[left_infinite], right[right_infinite])),
            f"Full roundtrip infinity signs differ for {field}",
        )
    finite = np.isfinite(left) & np.isfinite(right)
    difference = (
        float(np.max(np.abs(left[finite] - right[finite]))) if finite.any() else 0.0
    )
    _check(difference <= tolerance, f"Full roundtrip field {field} exceeds tolerance")
    return {
        "finite": int(finite.sum()),
        "missing": int(left_missing.sum()),
        "max_abs_difference": difference,
    }


def _compare_numeric_frames(
    expected: pd.DataFrame,
    observed: pd.DataFrame,
    columns: Sequence[str],
    *,
    tolerance: float,
) -> dict[str, int | float]:
    maximum = 0.0
    finite = 0
    missing = 0
    for field in columns:
        result = _compare_numeric_arrays(
            expected[field], observed[field], field=field, tolerance=tolerance
        )
        maximum = max(maximum, float(result["max_abs_difference"]))
        finite += int(result["finite"])
        missing += int(result["missing"])
    return {
        "finite_values_compared": finite,
        "missing_values_compared": missing,
        "max_abs_difference": maximum,
    }


def _expected_wide_for_year(
    source_dataset: object,
    *,
    year: int,
    metrics: Sequence[str],
    windows: Sequence[str],
) -> pd.DataFrame:
    columns = list(dict.fromkeys([*WIDE_KEY_COLUMNS, "window", *metrics]))
    source = _parquet_partition(source_dataset, columns, year=year)
    _check(not source.empty, f"Canonical source lacks year {year}")
    _check(
        not source.duplicated(["era01_cell_id", "window"]).any(),
        f"Canonical source has duplicate long keys in {year}",
    )
    _check(set(source["window"].astype(str)) == set(windows), f"Canonical source window support differs in {year}")
    cell_window_counts = source.groupby("era01_cell_id", observed=True)["window"].nunique()
    _check(
        bool((cell_window_counts == len(windows)).all()),
        f"Canonical source is not balanced across windows in {year}",
    )
    static = source[list(WIDE_KEY_COLUMNS)].drop_duplicates()
    _check(
        not static.duplicated(["era01_cell_id", "year"]).any(),
        f"Canonical spatial keys vary across windows in {year}",
    )
    output = static.set_index(["era01_cell_id", "year"]).sort_index()
    window_values = source["window"].astype(str)
    for metric in metrics:
        current = source.assign(__window=window_values).pivot(
            index=["era01_cell_id", "year"], columns="__window", values=metric
        )
        current = current.reindex(columns=list(windows))
        renamed = {
            window: f"{metric}{WINDOW_SUFFIXES[window]}" for window in windows
        }
        output = output.join(current.rename(columns=renamed), how="left")
    return output.reset_index().sort_values(["era01_cell_id", "year"]).reset_index(drop=True)


def validate_long_parquet_full(
    canonical_source_path: str | Path,
    exported_long_path: str | Path,
    *,
    years: Sequence[int],
    windows: Sequence[str] = CANONICAL_WINDOWS,
    tolerance: float = 1e-6,
    metric_batch_size: int = 8,
) -> dict[str, int | float]:
    """Compare every long-Parquet numeric value and missing-value indicator."""

    import pyarrow.dataset as ds
    import pyarrow.parquet as pq

    source_schema = pq.ParquetFile(canonical_source_path).schema_arrow
    exported_schema = pq.ParquetFile(exported_long_path).schema_arrow
    _check(
        set(source_schema.names) == set(exported_schema.names),
        "Exported long Parquet columns differ from canonical aggregate source",
    )
    metrics = _parquet_metric_columns(canonical_source_path)
    source_dataset = ds.dataset(str(canonical_source_path), format="parquet")
    observed_dataset = ds.dataset(str(exported_long_path), format="parquet")
    rows = 0
    finite = 0
    missing = 0
    maximum = 0.0
    partitions = 0
    for year in years:
        for window in windows:
            expected_keys = _sort(
                _parquet_partition(source_dataset, LONG_KEY_COLUMNS, year=year, window=window),
                ("era01_cell_id",),
            )
            observed_keys = _sort(
                _parquet_partition(observed_dataset, LONG_KEY_COLUMNS, year=year, window=window),
                ("era01_cell_id",),
            )
            _compare_keys(
                expected_keys,
                observed_keys,
                LONG_KEY_COLUMNS,
                label=f"long Parquet {year}/{window}",
            )
            rows += len(expected_keys)
            partitions += 1
            for batch in _chunks(metrics, metric_batch_size):
                columns = ["era01_cell_id", *batch]
                expected = _sort(
                    _parquet_partition(source_dataset, columns, year=year, window=window),
                    ("era01_cell_id",),
                )
                observed = _sort(
                    _parquet_partition(observed_dataset, columns, year=year, window=window),
                    ("era01_cell_id",),
                )
                _compare_keys(expected, observed, ("era01_cell_id",), label="long Parquet metric batch")
                report = _compare_numeric_frames(expected, observed, batch, tolerance=tolerance)
                finite += int(report["finite_values_compared"])
                missing += int(report["missing_values_compared"])
                maximum = max(maximum, float(report["max_abs_difference"]))
    return {
        "rows": rows,
        "partitions": partitions,
        "numeric_columns": len(metrics),
        "finite_values_compared": finite,
        "missing_values_compared": missing,
        "max_abs_difference": maximum,
    }


def validate_wide_parquet_full(
    canonical_source_path: str | Path,
    exported_wide_path: str | Path,
    *,
    years: Sequence[int],
    windows: Sequence[str] = CANONICAL_WINDOWS,
    tolerance: float = 1e-6,
    metric_batch_size: int = 8,
) -> dict[str, int | float]:
    """Derive each wide partition from the aggregate source and compare it fully."""

    import pyarrow.dataset as ds
    import pyarrow.parquet as pq

    metrics = _parquet_metric_columns(canonical_source_path)
    expected_columns = set(WIDE_KEY_COLUMNS)
    expected_columns.update(
        f"{metric}{WINDOW_SUFFIXES[window]}"
        for metric in metrics
        for window in windows
    )
    observed_schema = pq.ParquetFile(exported_wide_path).schema_arrow
    _check(
        set(observed_schema.names) == expected_columns,
        "Exported wide Parquet columns differ from canonical derived schema",
    )
    source_dataset = ds.dataset(str(canonical_source_path), format="parquet")
    observed_dataset = ds.dataset(str(exported_wide_path), format="parquet")
    rows = 0
    finite = 0
    missing = 0
    maximum = 0.0
    for year in years:
        expected_keys = _expected_wide_for_year(
            source_dataset, year=year, metrics=(), windows=windows
        )
        observed_keys = _sort(
            _parquet_partition(observed_dataset, WIDE_KEY_COLUMNS, year=year),
            ("era01_cell_id", "year"),
        )
        _compare_keys(
            expected_keys,
            observed_keys,
            WIDE_KEY_COLUMNS,
            label=f"wide Parquet {year}",
        )
        rows += len(expected_keys)
        for batch in _chunks(metrics, metric_batch_size):
            expected = _expected_wide_for_year(
                source_dataset, year=year, metrics=batch, windows=windows
            )
            wide_metrics = [
                f"{metric}{WINDOW_SUFFIXES[window]}"
                for metric in batch
                for window in windows
            ]
            observed = _sort(
                _parquet_partition(
                    observed_dataset,
                    ["era01_cell_id", "year", *wide_metrics],
                    year=year,
                ),
                ("era01_cell_id", "year"),
            )
            _compare_keys(expected, observed, ("era01_cell_id", "year"), label="wide Parquet metric batch")
            report = _compare_numeric_frames(
                expected, observed, wide_metrics, tolerance=tolerance
            )
            finite += int(report["finite_values_compared"])
            missing += int(report["missing_values_compared"])
            maximum = max(maximum, float(report["max_abs_difference"]))
    return {
        "rows": rows,
        "year_partitions": len(years),
        "numeric_columns": len(metrics) * len(windows),
        "finite_values_compared": finite,
        "missing_values_compared": missing,
        "max_abs_difference": maximum,
    }


def validate_parquet_roundtrip(
    expected: pd.DataFrame,
    path: str | Path,
    *,
    keys: Sequence[str],
    columns: Sequence[str] | None = None,
    sample_size: int = 1_000,
    tolerance: float = 1e-6,
    seed: int = 42,
) -> dict[str, int | float]:
    observed = pd.read_parquet(path)
    _check(len(observed) == len(expected), "Parquet row count changed on roundtrip")
    return _compare_frame_sample(
        expected,
        observed,
        keys=keys,
        columns=columns,
        sample_size=sample_size,
        tolerance=tolerance,
        seed=seed,
    )


def validate_dta_roundtrip(
    expected_wide: pd.DataFrame,
    dta_path: str | Path,
    alias_map_path: str | Path,
    *,
    sample_size: int = 1_000,
    tolerance: float = 1e-6,
    seed: int = 42,
) -> dict[str, int | float]:
    aliases = pd.read_csv(alias_map_path, encoding="utf-8-sig")
    _check(
        {"original_name", "stata_name"}.issubset(aliases.columns),
        "Alias map lacks original_name/stata_name",
    )
    reverse = aliases.set_index("stata_name")["original_name"].to_dict()
    observed = pd.read_stata(dta_path, convert_categoricals=False).rename(columns=reverse)
    _check(len(observed) == len(expected_wide), "DTA row count changed on roundtrip")
    return _compare_frame_sample(
        expected_wide,
        observed,
        keys=("era01_cell_id", "year"),
        columns=None,
        sample_size=sample_size,
        tolerance=tolerance,
        seed=seed,
    )


def validate_cf_netcdf(
    path: str | Path,
    crosswalk: pd.DataFrame,
    *,
    years: Sequence[int] = tuple(range(2010, 2020)),
    windows: Sequence[str] = CANONICAL_WINDOWS,
    metric_columns: Sequence[str] | None = None,
    spec: TargetGridSpec = TARGET_GRID,
    spatial_row_block: int = 32,
    check_nonselected: bool = True,
) -> dict[str, int]:
    if spatial_row_block <= 0:
        raise ValueError("spatial_row_block must be positive")
    dataset = nc.Dataset(path)
    try:
        expected_dimensions = {
            "time": len(years),
            "window": len(windows),
            "latitude": spec.nlat,
            "longitude": spec.nlon,
        }
        for name, length in expected_dimensions.items():
            _check(name in dataset.dimensions, f"NetCDF lacks {name} dimension")
            _check(len(dataset.dimensions[name]) == length, f"NetCDF {name} length is incorrect")
        _check(
            np.allclose(dataset.variables["latitude"][:], spec.latitudes, atol=1e-8, rtol=0),
            "NetCDF latitude axis differs from frozen axis",
        )
        _check(
            np.allclose(dataset.variables["longitude"][:], spec.longitudes, atol=1e-8, rtol=0),
            "NetCDF longitude axis differs from frozen axis",
        )
        raw_windows = dataset.variables["window"][:]
        decoded_windows = [
            value.decode("utf-8") if isinstance(value, (bytes, np.bytes_)) else str(value)
            for value in raw_windows
        ]
        _check(decoded_windows == list(windows), "NetCDF window labels are incorrect")
        time = dataset.variables["time"]
        dates = nc.num2date(time[:], time.units, time.calendar)
        _check(
            [(value.year, value.month, value.day) for value in dates]
            == [(int(year), 1, 1) for year in years],
            "NetCDF time dates are incorrect",
        )
        mask = np.asarray(dataset.variables["selected_grid_mask"][:], dtype=np.int8)
        expected_mask = np.zeros((spec.nlat, spec.nlon), dtype=np.int8)
        expected_mask[
            crosswalk["lat_idx"].to_numpy(dtype=np.int64),
            crosswalk["lon_idx"].to_numpy(dtype=np.int64),
        ] = 1
        _check(np.array_equal(mask, expected_mask), "NetCDF selected_grid_mask is incorrect")
        outside = expected_mask == 0
        for identifier in ("era01_cell_id", "grid_id_v3"):
            _check(identifier in dataset.variables, f"NetCDF lacks {identifier}")
            values = dataset.variables[identifier][:]
            masked = np.ma.getmaskarray(values)
            _check(bool(masked[outside].all()), f"{identifier} contains data outside selected grid")
        nonselected_values_checked = 0
        for metric in metric_columns or ():
            _check(metric in dataset.variables, f"NetCDF lacks metric {metric}")
            variable = dataset.variables[metric]
            _check(variable.dimensions == ("time", "window", "latitude", "longitude"), f"{metric} dimensions are incorrect")
            _check(variable.dtype == np.dtype("float64"), f"{metric} must be float64")
            required_metadata = (
                "long_name",
                "units",
                "source_product",
                "history_period",
                "threshold_rule",
                "minimum_duration",
                "gap_rule",
                "recovery_rule",
                "calendar_rule",
                "censor_rule",
                "confirmatory_status",
            )
            missing_metadata = [
                name
                for name in required_metadata
                if name not in variable.ncattrs() or str(variable.getncattr(name)).strip() == ""
            ]
            _check(not missing_metadata, f"{metric} lacks NetCDF metadata: {missing_metadata}")
            if check_nonselected:
                for start in range(0, spec.nlat, spatial_row_block):
                    stop = min(start + spatial_row_block, spec.nlat)
                    values = np.ma.filled(variable[:, :, start:stop, :], np.nan)
                    block_outside = outside[start:stop, :]
                    checked = values[:, :, block_outside]
                    nonselected_values_checked += int(checked.size)
                    _check(np.isnan(checked).all(), f"{metric} contains data outside selected grid")
        _check(getattr(dataset, "Conventions", "") == "CF-1.10", "NetCDF CF convention is missing")
        _check(
            "featureType" not in dataset.ncattrs(),
            "NetCDF featureType must be absent for a gridded coverage",
        )
    finally:
        dataset.close()
    return {
        "time": len(years),
        "windows": len(windows),
        "latitude": spec.nlat,
        "longitude": spec.nlon,
        "selected_cells": len(crosswalk),
        "nonselected_values_checked": nonselected_values_checked,
    }


def validate_netcdf_roundtrip(
    expected_long: pd.DataFrame,
    path: str | Path,
    *,
    sample_size: int = 1_000,
    tolerance: float = 1e-6,
    seed: int = 42,
    years: Sequence[int] = tuple(range(2010, 2020)),
    windows: Sequence[str] = CANONICAL_WINDOWS,
    spec: TargetGridSpec = TARGET_GRID,
) -> dict[str, int | float]:
    metrics = [
        column
        for column in expected_long.columns
        if column not in LONG_KEY_COLUMNS and pd.api.types.is_numeric_dtype(expected_long[column])
    ]
    crosswalk = expected_long[list(SPATIAL_COLUMNS)].drop_duplicates()
    validate_cf_netcdf(
        path,
        crosswalk,
        years=years,
        windows=windows,
        metric_columns=metrics,
        spec=spec,
    )
    sample = _sample(expected_long, sample_size, seed)
    year_lookup = {int(year): index for index, year in enumerate(years)}
    window_lookup = {window: index for index, window in enumerate(windows)}
    maximum = 0.0
    dataset = nc.Dataset(path)
    try:
        for metric in metrics:
            expected_values = pd.to_numeric(sample[metric], errors="coerce").to_numpy(dtype=np.float64)
            observed_values = np.full(len(sample), np.nan, dtype=np.float64)
            variable = dataset.variables[metric]
            for position, row in enumerate(sample.itertuples(index=False)):
                value = variable[
                    year_lookup[int(row.year)],
                    window_lookup[str(row.window)],
                    int(row.lat_idx),
                    int(row.lon_idx),
                ]
                observed_values[position] = np.nan if np.ma.is_masked(value) else float(value)
            _check(
                bool((np.isnan(expected_values) == np.isnan(observed_values)).all()),
                f"NetCDF missingness differs for {metric}",
            )
            finite = np.isfinite(expected_values) & np.isfinite(observed_values)
            difference = (
                float(np.max(np.abs(expected_values[finite] - observed_values[finite])))
                if finite.any()
                else 0.0
            )
            maximum = max(maximum, difference)
            _check(difference <= tolerance, f"NetCDF field {metric} exceeds tolerance")
    finally:
        dataset.close()
    return {
        "sample_rows": len(sample),
        "numeric_columns": len(metrics),
        "max_abs_difference": maximum,
    }


def validate_netcdf_full(
    canonical_source_path: str | Path,
    path: str | Path,
    *,
    years: Sequence[int],
    windows: Sequence[str] = CANONICAL_WINDOWS,
    tolerance: float = 1e-6,
    metric_batch_size: int = 8,
    spatial_row_block: int = 32,
    spec: TargetGridSpec = TARGET_GRID,
) -> dict[str, int | float]:
    """Compare all selected values and scan every nonselected NetCDF value."""

    import pyarrow.dataset as ds

    metrics = _parquet_metric_columns(canonical_source_path)
    source_dataset = ds.dataset(str(canonical_source_path), format="parquet")
    first = _parquet_partition(
        source_dataset,
        SPATIAL_COLUMNS,
        year=int(years[0]),
        window=str(windows[0]),
    )
    crosswalk = _sort(first.drop_duplicates(), ("era01_cell_id",))
    _check(
        not crosswalk.duplicated(["era01_cell_id"]).any(),
        "Canonical NetCDF crosswalk is not unique",
    )
    structure = validate_cf_netcdf(
        path,
        crosswalk,
        years=years,
        windows=windows,
        metric_columns=metrics,
        spec=spec,
        spatial_row_block=spatial_row_block,
        check_nonselected=False,
    )
    mask = np.zeros((spec.nlat, spec.nlon), dtype=bool)
    mask[
        crosswalk["lat_idx"].to_numpy(dtype=np.int64),
        crosswalk["lon_idx"].to_numpy(dtype=np.int64),
    ] = True
    year_lookup = {int(year): index for index, year in enumerate(years)}
    window_lookup = {str(window): index for index, window in enumerate(windows)}
    rows = 0
    finite = 0
    missing = 0
    maximum = 0.0
    nonselected_values_checked = 0
    dataset = nc.Dataset(path)
    try:
        cube_metrics = {
            name
            for name, variable in dataset.variables.items()
            if variable.dimensions == ("time", "window", "latitude", "longitude")
        }
        _check(cube_metrics == set(metrics), "NetCDF cube metric set differs from canonical source")
        for year in years:
            for window in windows:
                rows_in_partition: int | None = None
                for batch in _chunks(metrics, metric_batch_size):
                    expected = _sort(
                        _parquet_partition(
                            source_dataset,
                            ["era01_cell_id", "lat_idx", "lon_idx", *batch],
                            year=int(year),
                            window=str(window),
                        ),
                        ("era01_cell_id",),
                    )
                    if rows_in_partition is None:
                        rows_in_partition = len(expected)
                    lat_idx = expected["lat_idx"].to_numpy(dtype=np.int64)
                    lon_idx = expected["lon_idx"].to_numpy(dtype=np.int64)
                    for metric in batch:
                        layer = np.ma.filled(
                            dataset.variables[metric][
                                year_lookup[int(year)],
                                window_lookup[str(window)],
                                :,
                                :,
                            ],
                            np.nan,
                        ).astype(np.float64, copy=False)
                        outside = layer[~mask]
                        nonselected_values_checked += int(outside.size)
                        _check(
                            bool(np.isnan(outside).all()),
                            f"{metric} contains data outside selected grid in {year}/{window}",
                        )
                        report = _compare_numeric_arrays(
                            expected[metric],
                            layer[lat_idx, lon_idx],
                            field=f"{metric} ({year}/{window})",
                            tolerance=tolerance,
                        )
                        finite += int(report["finite"])
                        missing += int(report["missing"])
                        maximum = max(maximum, float(report["max_abs_difference"]))
                rows += int(rows_in_partition or 0)
    finally:
        dataset.close()
    return {
        **structure,
        "rows": rows,
        "numeric_columns": len(metrics),
        "finite_values_compared": finite,
        "missing_values_compared": missing,
        "nonselected_values_checked": nonselected_values_checked,
        "max_abs_difference": maximum,
    }


def validate_dta_full(
    canonical_source_path: str | Path,
    dta_path: str | Path,
    alias_map_path: str | Path,
    *,
    years: Sequence[int],
    windows: Sequence[str] = CANONICAL_WINDOWS,
    tolerance: float = 1e-6,
    metric_batch_size: int = 8,
    row_batch_size: int = 50_000,
) -> dict[str, int | float]:
    """Compare the complete DTA in bounded column and row batches."""

    import pyarrow.dataset as ds

    if row_batch_size <= 0:
        raise ValueError("row_batch_size must be positive")
    metrics = _parquet_metric_columns(canonical_source_path)
    expected_originals = set(WIDE_KEY_COLUMNS)
    expected_originals.update(
        f"{metric}{WINDOW_SUFFIXES[window]}"
        for metric in metrics
        for window in windows
    )
    aliases = pd.read_csv(alias_map_path, encoding="utf-8-sig")
    _check(
        {"original_name", "stata_name"}.issubset(aliases.columns),
        "Alias map lacks original_name/stata_name",
    )
    _check(not aliases["original_name"].duplicated().any(), "Alias originals are duplicated")
    _check(
        not aliases["stata_name"].astype(str).str.casefold().duplicated().any(),
        "Stata aliases are case-insensitively duplicated",
    )
    _check(set(aliases["original_name"].astype(str)) == expected_originals, "Alias map differs from canonical wide schema")
    alias_for = aliases.set_index("original_name")["stata_name"].astype(str).to_dict()
    reverse = {value: key for key, value in alias_for.items()}
    source_dataset = ds.dataset(str(canonical_source_path), format="parquet")
    finite = 0
    missing = 0
    maximum = 0.0
    rows_checked = 0
    batches_checked = 0
    for batch_index, batch in enumerate(_chunks(metrics, metric_batch_size)):
        expected_parts = [
            _expected_wide_for_year(
                source_dataset, year=int(year), metrics=batch, windows=windows
            )
            for year in years
        ]
        expected = pd.concat(expected_parts, ignore_index=True).sort_values(
            ["era01_cell_id", "year"]
        )
        wide_metrics = [
            f"{metric}{WINDOW_SUFFIXES[window]}"
            for metric in batch
            for window in windows
        ]
        requested_originals = [*WIDE_KEY_COLUMNS, *wide_metrics]
        requested_aliases = [alias_for[name] for name in requested_originals]
        seen_keys: list[pd.DataFrame] = []
        reader = pd.read_stata(
            dta_path,
            convert_categoricals=False,
            columns=requested_aliases,
            chunksize=row_batch_size,
        )
        with reader:
            for observed_chunk in reader:
                observed = observed_chunk.rename(columns=reverse)
                merged = observed.merge(
                    expected,
                    on=["era01_cell_id", "year"],
                    how="left",
                    suffixes=("_observed", "_expected"),
                    indicator=True,
                    validate="one_to_one",
                )
                _check(merged["_merge"].eq("both").all(), "DTA contains keys absent from canonical wide source")
                for key in WIDE_KEY_COLUMNS:
                    if key in {"era01_cell_id", "year"}:
                        continue
                    _compare_numeric_arrays(
                        merged[f"{key}_expected"],
                        merged[f"{key}_observed"],
                        field=f"DTA key {key}",
                        tolerance=0.0,
                    )
                observed_numeric = pd.DataFrame(
                    {field: merged[f"{field}_observed"] for field in wide_metrics}
                )
                expected_numeric = pd.DataFrame(
                    {field: merged[f"{field}_expected"] for field in wide_metrics}
                )
                report = _compare_numeric_frames(
                    expected_numeric, observed_numeric, wide_metrics, tolerance=tolerance
                )
                finite += int(report["finite_values_compared"])
                missing += int(report["missing_values_compared"])
                maximum = max(maximum, float(report["max_abs_difference"]))
                if batch_index == 0:
                    rows_checked += len(observed)
                    seen_keys.append(observed[["era01_cell_id", "year"]])
                batches_checked += 1
        if batch_index == 0:
            all_seen = pd.concat(seen_keys, ignore_index=True)
            _check(not all_seen.duplicated().any(), "DTA contains duplicate grid-year keys")
            expected_keys = expected[["era01_cell_id", "year"]]
            merged_keys = expected_keys.merge(
                all_seen,
                on=["era01_cell_id", "year"],
                how="outer",
                indicator=True,
                validate="one_to_one",
            )
            _check(merged_keys["_merge"].eq("both").all(), "DTA and canonical wide keys differ")
    return {
        "rows": rows_checked,
        "row_batches": batches_checked,
        "numeric_columns": len(metrics) * len(windows),
        "finite_values_compared": finite,
        "missing_values_compared": missing,
        "max_abs_difference": maximum,
    }


def validate_export_bundle_full(
    canonical_source_path: str | Path,
    exported_long_path: str | Path,
    exported_wide_path: str | Path,
    netcdf_path: str | Path,
    dta_path: str | Path,
    alias_map_path: str | Path,
    *,
    years: Sequence[int],
    windows: Sequence[str] = CANONICAL_WINDOWS,
    tolerance: float = 1e-6,
    metric_batch_size: int = 8,
    dta_row_batch_size: int = 50_000,
    spatial_row_block: int = 32,
    spec: TargetGridSpec = TARGET_GRID,
) -> dict[str, dict[str, int | float]]:
    """Run full, chunked, aggregate-source-based checks for every public format."""

    return {
        "long_parquet": validate_long_parquet_full(
            canonical_source_path,
            exported_long_path,
            years=years,
            windows=windows,
            tolerance=tolerance,
            metric_batch_size=metric_batch_size,
        ),
        "wide_parquet": validate_wide_parquet_full(
            canonical_source_path,
            exported_wide_path,
            years=years,
            windows=windows,
            tolerance=tolerance,
            metric_batch_size=metric_batch_size,
        ),
        "netcdf": validate_netcdf_full(
            canonical_source_path,
            netcdf_path,
            years=years,
            windows=windows,
            tolerance=tolerance,
            metric_batch_size=metric_batch_size,
            spatial_row_block=spatial_row_block,
            spec=spec,
        ),
        "dta": validate_dta_full(
            canonical_source_path,
            dta_path,
            alias_map_path,
            years=years,
            windows=windows,
            tolerance=tolerance,
            metric_batch_size=metric_batch_size,
            row_batch_size=dta_row_batch_size,
        ),
    }


def validate_historical_occurrence_rates(
    historical: pd.DataFrame,
    expectations: Mapping[str, tuple[float, float]],
    *,
    group_columns: Sequence[str] = (),
    minimum_valid: int = 1,
) -> pd.DataFrame:
    """Validate empirical indicator rates against documented rate/tolerance pairs."""

    if minimum_valid <= 0:
        raise ValueError("minimum_valid must be positive")
    missing = sorted(set(group_columns).union(expectations).difference(historical.columns))
    _check(not missing, f"Historical-rate columns are missing: {missing}")
    grouped: Iterable[tuple[object, pd.DataFrame]]
    if group_columns:
        grouped = historical.groupby(list(group_columns), dropna=False, observed=True)
    else:
        grouped = [((), historical)]
    rows: list[dict[str, object]] = []
    for group_key, group in grouped:
        group_tuple = group_key if isinstance(group_key, tuple) else (group_key,)
        for field, (expected_rate, tolerance) in expectations.items():
            values = pd.to_numeric(group[field], errors="coerce").dropna()
            _check(len(values) >= minimum_valid, f"Insufficient historical values for {field}")
            _check(values.isin([0, 1]).all(), f"Historical indicator {field} is not binary")
            rate = float(values.mean())
            _check(
                abs(rate - expected_rate) <= tolerance,
                f"Historical occurrence rate for {field} is outside tolerance",
            )
            row: dict[str, object] = {
                "field": field,
                "valid_count": len(values),
                "rate": rate,
                "expected_rate": float(expected_rate),
                "tolerance": float(tolerance),
            }
            row.update(dict(zip(group_columns, group_tuple)))
            rows.append(row)
    return pd.DataFrame(rows)
