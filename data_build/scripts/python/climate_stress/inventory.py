"""Source inventory and metadata validation for the climate-stress panel."""

from __future__ import annotations

import calendar
import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from .config import PipelineConfig
from .runtime import atomic_output, ensure_within_run, sha256_file


FAST_HASH_BLOCK_BYTES = 1024 * 1024
FAST_HASH_ALGORITHM = "sha256-size-head-tail-v1"
FULL_HASH_ALGORITHM = "sha256-full-v1"


@dataclass(frozen=True)
class AssetSpec:
    asset_id: str
    family: str
    path: Path
    role: str
    year: int | None = None
    layer: str | None = None
    variable: str | None = None
    expected_sha256: str | None = None
    timestamp_semantics: str | None = None


@dataclass(frozen=True)
class Fingerprint:
    size_bytes: int
    mtime_utc: str
    sha256: str
    hash_algorithm: str
    hash_is_full: bool


@dataclass
class InventoryResult:
    records: pd.DataFrame
    checks: list[dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not any(check["status"] == "fail" for check in self.checks)

    @property
    def blocked(self) -> bool:
        return any(check["status"] == "blocked" for check in self.checks)

    @property
    def pipeline_blocked(self) -> bool:
        """Return whether a blocked check prevents non-scoped pipeline stages."""

        return any(
            check["status"] == "blocked"
            and check.get("evidence", {}).get("blocking_scope", "pipeline")
            == "pipeline"
            for check in self.checks
        )

    def to_jsonable(self) -> dict[str, Any]:
        records = json.loads(self.records.to_json(orient="records"))
        return {
            "schema_version": 1,
            "metadata": self.metadata,
            "summary": {
                "asset_count": len(records),
                "existing_count": sum(bool(row["exists"]) for row in records),
                "missing_count": sum(not bool(row["exists"]) for row in records),
                "total_size_bytes": sum(
                    int(row["size_bytes"] or 0) for row in records
                ),
                "ok": self.ok,
                "blocked": self.blocked,
                "pipeline_blocked": self.pipeline_blocked,
            },
            "checks": self.checks,
            "records": records,
        }


def _format_pattern(pattern: str, **values: Any) -> Path:
    return Path(pattern.format(**values))


def enumerate_assets(config: PipelineConfig) -> list[AssetSpec]:
    """Enumerate the frozen v1 input universe from configuration."""

    data = config.data
    inputs = data["inputs"]
    from .era5 import resolve_era_hourly_path
    specs: list[AssetSpec] = []

    manual = data.get("manual", {})
    if manual.get("path"):
        specs.append(
            AssetSpec(
                asset_id="manual.variable_construction_v1",
                family="manual",
                path=Path(manual["path"]),
                role="variable specification",
                expected_sha256=str(manual.get("sha256") or "") or None,
            )
        )

    specs.extend(
        [
            AssetSpec(
                "v3.main", "v3", Path(inputs["v3_main"]), "target footprint"
            ),
            AssetSpec(
                "v3.phenowindows",
                "v3",
                Path(inputs["v3_phenowindows"]),
                "legacy cross-check",
            ),
        ]
    )

    historical = config.historical_years
    target = config.target_years
    event_context = data["years"].get(
        "event_context", {"start": min(historical), "end": max(target) + 1}
    )
    event_start = int(event_context["start"])
    event_end = int(event_context["end"])
    era_years = range(event_start - 1, event_end + 1)
    for year in era_years:
        specs.append(
            AssetSpec(
                asset_id=f"era5.hourly.{year}",
                family="era5_hourly",
                path=resolve_era_hourly_path(
                    inputs["era5_hourly_pattern"],
                    year,
                    inputs.get("era5_hourly_overrides", {}),
                ),
                role="historical/target temperature plus UTC+8 boundary",
                year=year,
                variable=str(data["temperature"]["source_variable"]),
            )
        )

    for year in [int(value) for value in data["years"]["daily_validation"]]:
        specs.append(
            AssetSpec(
                asset_id=f"era5.daily_validation.{year}",
                family="era5_daily_validation",
                path=_format_pattern(
                    inputs["era5_daily_validation_pattern"], year=year
                ),
                role="legacy UTC daily validation only",
                year=year,
            )
        )

    gleam_years = range(event_start, event_end + 1)
    for year in gleam_years:
        for layer in data["gleam"]["layers"]:
            specs.append(
                AssetSpec(
                    asset_id=f"gleam43a.{layer}.{year}",
                    family="gleam",
                    path=_format_pattern(
                        inputs["gleam_pattern"], year=year, layer=layer
                    ),
                    role="soil-moisture history/target",
                    year=year,
                    layer=str(layer),
                    variable=str(layer),
                )
            )

    for scale in range(1, 13):
        specs.append(
            AssetSpec(
                asset_id=f"chm_spei.monthly.{scale}",
                family="spei_monthly",
                path=_format_pattern(
                    inputs["spei_monthly_pattern"], scale=scale
                ),
                role="native monthly SPEI",
                layer=str(scale),
                variable=f"SPEI-{scale}",
            )
        )
    endpoint_confirmed = (
        str(data["spei"]["two_week_endpoint_decision_status"])
        == "CONFIRMED"
    )
    specs.append(
        AssetSpec(
            asset_id="chm_spei.2w",
            family="spei_2w",
            path=Path(inputs["spei_2w"]),
            role=(
                "native trailing-14-day SPEI released every 7 days; "
                +
                (
                    "confirmed run mapping"
                    if endpoint_confirmed
                    else "partial-scope run mapping with endpoint disabled"
                )
            ),
            variable="SPEI-2W",
            timestamp_semantics=str(
                data["spei"]["two_week_timestamp_semantics"]
            ),
        )
    )

    for year in target:
        for stage in data["phenology"]["stages"]:
            specs.append(
                AssetSpec(
                    asset_id=f"phenology.maize.{stage}.{year}",
                    family="phenology",
                    path=_format_pattern(
                        inputs["phenology_pattern"], stage=stage, year=year
                    ),
                    role="annual maize phenology",
                    year=year,
                    layer=str(stage),
                )
            )

    identifiers = [spec.asset_id for spec in specs]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Inventory asset identifiers are not unique")
    return specs


def fingerprint_file(
    path: str | Path,
    *,
    mode: str = "pilot",
    sample_bytes: int = FAST_HASH_BLOCK_BYTES,
) -> Fingerprint:
    """Fingerprint a file using a fast pilot sample or a complete final hash."""

    source = Path(path)
    if mode not in {"pilot", "full"}:
        raise ValueError("hash mode must be 'pilot' or 'full'")
    stat = source.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )
    if mode == "full" or stat.st_size <= sample_bytes * 2:
        return Fingerprint(
            size_bytes=stat.st_size,
            mtime_utc=mtime,
            sha256=sha256_file(source),
            hash_algorithm=FULL_HASH_ALGORITHM,
            hash_is_full=True,
        )

    digest = hashlib.sha256()
    digest.update(FAST_HASH_ALGORITHM.encode("ascii") + b"\0")
    digest.update(stat.st_size.to_bytes(16, "big"))
    with source.open("rb") as handle:
        digest.update(handle.read(sample_bytes))
        handle.seek(-sample_bytes, os.SEEK_END)
        digest.update(handle.read(sample_bytes))
    return Fingerprint(
        size_bytes=stat.st_size,
        mtime_utc=mtime,
        sha256=digest.hexdigest(),
        hash_algorithm=FAST_HASH_ALGORITHM,
        hash_is_full=False,
    )


def build_records(
    specs: Sequence[AssetSpec], *, hash_mode: str = "pilot"
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for spec in specs:
        exists = spec.path.is_file()
        fingerprint = fingerprint_file(spec.path, mode=hash_mode) if exists else None
        rows.append(
            {
                "asset_id": spec.asset_id,
                "family": spec.family,
                "role": spec.role,
                "path": str(spec.path),
                "year": spec.year,
                "layer": spec.layer,
                "variable": spec.variable,
                "exists": exists,
                "size_bytes": fingerprint.size_bytes if fingerprint else None,
                "mtime_utc": fingerprint.mtime_utc if fingerprint else None,
                "sha256": fingerprint.sha256 if fingerprint else None,
                "hash_algorithm": (
                    fingerprint.hash_algorithm if fingerprint else None
                ),
                "hash_is_full": (
                    fingerprint.hash_is_full if fingerprint else False
                ),
                "expected_sha256": spec.expected_sha256,
                "timestamp_semantics": spec.timestamp_semantics,
            }
        )
    return pd.DataFrame(rows).sort_values("asset_id").reset_index(drop=True)


def _check(
    check_id: str, status: str, detail: Any, **evidence: Any
) -> dict[str, Any]:
    if status not in {"pass", "warn", "blocked", "fail"}:
        raise ValueError(f"Unsupported check status: {status}")
    return {
        "check_id": check_id,
        "status": status,
        "detail": detail,
        "evidence": evidence,
    }


def _records_for(records: pd.DataFrame, family: str) -> pd.DataFrame:
    return records.loc[records["family"] == family].copy()


def _year_continuity_check(
    records: pd.DataFrame, family: str, expected: Iterable[int]
) -> dict[str, Any]:
    subset = _records_for(records, family)
    existing = {
        int(value)
        for value in subset.loc[subset["exists"] & subset["year"].notna(), "year"]
    }
    wanted = set(int(value) for value in expected)
    missing = sorted(wanted - existing)
    extra = sorted(existing - wanted)
    return _check(
        f"{family}.year_continuity",
        "pass" if not missing and not extra else "fail",
        "year coverage matches" if not missing and not extra else "year coverage differs",
        expected=sorted(wanted),
        observed=sorted(existing),
        missing=missing,
        extra=extra,
    )


def target_grid_axes(config: PipelineConfig) -> tuple[np.ndarray, np.ndarray]:
    grid = config.data["grid"]
    latitude = float(grid["north"]) - np.arange(int(grid["nlat"])) * float(
        grid["step"]
    )
    longitude = float(grid["west"]) + np.arange(int(grid["nlon"])) * float(
        grid["step"]
    )
    return latitude, longitude


def exact_subgrid_indices(
    source_axis: Sequence[float],
    target_axis: Sequence[float],
    *,
    tolerance: float,
) -> np.ndarray:
    """Return source indices for an exact ordered target subset."""

    source = np.asarray(source_axis, dtype=float)
    target = np.asarray(target_axis, dtype=float)
    if source.ndim != 1 or target.ndim != 1 or not len(source) or not len(target):
        raise ValueError("source_axis and target_axis must be non-empty 1-D arrays")
    indices = np.asarray([int(np.argmin(np.abs(source - value))) for value in target])
    errors = np.abs(source[indices] - target)
    if np.any(errors > tolerance):
        raise ValueError(f"Target axis is not an exact subset; max error={errors.max()}")
    if len(indices) > 1:
        steps = np.diff(indices)
        if not np.all(steps == steps[0]) or abs(int(steps[0])) != 1:
            raise ValueError("Target axis is not a contiguous source subset")
    return indices


def spei_domain_covers(
    spei_latitude: Sequence[float],
    spei_longitude: Sequence[float],
    selected_latitude: Sequence[float],
    selected_longitude: Sequence[float],
    *,
    tolerance: float,
) -> bool:
    slat = np.asarray(spei_latitude, dtype=float)
    slon = np.asarray(spei_longitude, dtype=float)
    tlat = np.asarray(selected_latitude, dtype=float)
    tlon = np.asarray(selected_longitude, dtype=float)
    return bool(
        tlat.min() >= slat.min() - tolerance
        and tlat.max() <= slat.max() + tolerance
        and tlon.min() >= slon.min() - tolerance
        and tlon.max() <= slon.max() + tolerance
    )


def _axis_specs_for_family(family: str) -> tuple[str, str, str]:
    if family in {"era5_hourly", "era5_daily_validation"}:
        return "valid_time", "latitude", "longitude"
    return "time", "lat", "lon"


def _expected_time_count(spec: AssetSpec) -> int | None:
    if spec.year is None:
        if spec.family == "spei_monthly":
            return 744
        if spec.family == "spei_2w":
            return 3235
        return None
    days = 366 if calendar.isleap(spec.year) else 365
    return days * 24 if spec.family == "era5_hourly" else days


def _sample_specs(specs: Sequence[AssetSpec], mode: str) -> list[AssetSpec]:
    if mode == "all":
        return list(specs)
    if mode != "representative":
        raise ValueError("axis mode must be 'representative' or 'all'")
    selected: list[AssetSpec] = []
    groups: dict[tuple[str, str | None], list[AssetSpec]] = {}
    for spec in specs:
        groups.setdefault((spec.family, spec.layer), []).append(spec)
    for group in groups.values():
        ordered = sorted(group, key=lambda item: (item.year or -1, item.asset_id))
        selected.append(ordered[0])
        if ordered[-1] != ordered[0]:
            selected.append(ordered[-1])
    return selected


def _validate_netcdf_axes(
    config: PipelineConfig,
    specs: Sequence[AssetSpec],
    *,
    mode: str,
) -> tuple[list[dict[str, Any]], dict[str, tuple[np.ndarray, np.ndarray]]]:
    import xarray as xr

    from .era5 import validate_era_hourly_file

    checks: list[dict[str, Any]] = []
    axes: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    coordinate_tolerance = float(config.data["quality"]["coordinate_tolerance"])
    errors: list[str] = []
    era_time_errors: list[str] = []
    failed_era_years: list[int] = []
    available = [spec for spec in specs if spec.path.is_file()]
    # ERA annual files are a historical-threshold input, so even pilot mode
    # must inspect every configured year.  Representative sampling remains in
    # place only for the other NetCDF families.
    era_specs = sorted(
        (spec for spec in available if spec.family == "era5_hourly"),
        key=lambda item: (item.year or -1, item.asset_id),
    )
    gleam_specs = sorted(
        (spec for spec in available if spec.family == "gleam"),
        key=lambda item: (item.year or -1, item.layer or "", item.asset_id),
    )
    sampled = era_specs + gleam_specs + _sample_specs(
        [
            spec
            for spec in available
            if spec.family not in {"era5_hourly", "gleam"}
        ],
        mode,
    )
    for spec in sampled:
        time_name, lat_name, lon_name = _axis_specs_for_family(spec.family)
        try:
            with xr.open_dataset(spec.path, decode_times=False, cache=False) as dataset:
                if spec.variable and spec.variable not in dataset.data_vars:
                    raise ValueError(f"missing variable {spec.variable}")
                for name in (time_name, lat_name, lon_name):
                    if name not in dataset.variables:
                        raise ValueError(f"missing axis {name}")
                expected = _expected_time_count(spec)
                observed = int(dataset.sizes[time_name])
                if expected is not None and observed != expected:
                    raise ValueError(
                        f"{time_name} length {observed}, expected {expected}"
                    )
                if spec.family == "gleam":
                    if spec.year is None:
                        raise ValueError("GLEAM annual asset lacks its expected year")
                    from netCDF4 import num2date

                    time_variable = dataset[time_name]
                    units = time_variable.attrs.get("units")
                    if not units:
                        raise ValueError("GLEAM time axis lacks units")
                    decoded = num2date(
                        np.asarray(time_variable.values),
                        units=str(units),
                        calendar=str(
                            time_variable.attrs.get("calendar", "standard")
                        ),
                    )
                    observed_dates = tuple(
                        date(int(value.year), int(value.month), int(value.day))
                        for value in decoded
                    )
                    expected_dates = tuple(
                        date(int(spec.year), 1, 1) + timedelta(days=offset)
                        for offset in range(expected)
                    )
                    if observed_dates != expected_dates:
                        first = observed_dates[0] if observed_dates else None
                        last = observed_dates[-1] if observed_dates else None
                        raise ValueError(
                            "GLEAM time labels are not the complete named calendar "
                            f"year {int(spec.year)}: first={first}, last={last}"
                        )
                current_axes = (
                    np.asarray(dataset[lat_name].values, dtype=float),
                    np.asarray(dataset[lon_name].values, dtype=float),
                )
                previous_axes = axes.get(spec.family)
                axes_match = previous_axes is None or (
                    previous_axes[0].shape == current_axes[0].shape
                    and previous_axes[1].shape == current_axes[1].shape
                    and np.allclose(
                        previous_axes[0],
                        current_axes[0],
                        rtol=0.0,
                        atol=coordinate_tolerance,
                    )
                    and np.allclose(
                        previous_axes[1],
                        current_axes[1],
                        rtol=0.0,
                        atol=coordinate_tolerance,
                    )
                )
                if not axes_match:
                    raise ValueError(
                        f"{spec.family} spatial axes differ across source files"
                    )
                axes.setdefault(spec.family, current_axes)
                if spec.family == "spei_2w":
                    values = np.asarray(dataset[time_name].values, dtype=float)
                    differences = np.diff(values)
                    if np.any(differences < 7.0) or not np.allclose(
                        np.mod(differences, 7.0), 0.0
                    ):
                        raise ValueError(
                            "SPEI-2W timestamps overlap or are off the 7-day cadence"
                        )
        except Exception as exc:  # one record per corrupt header
            errors.append(f"{spec.asset_id}: {type(exc).__name__}: {exc}")
        if spec.family == "era5_hourly":
            try:
                if spec.year is None:
                    raise ValueError("ERA5 annual asset is missing its expected year")
                validate_era_hourly_file(spec.path, int(spec.year))
            except Exception as exc:
                if spec.year is not None:
                    failed_era_years.append(int(spec.year))
                era_time_errors.append(
                    f"{spec.asset_id}: {type(exc).__name__}: {exc}"
                )
    checks.append(
        _check(
            "netcdf.axes_variables",
            "pass" if not errors else "fail",
            f"inspected {len(sampled)} NetCDF headers",
            mode=mode,
            errors=errors,
        )
    )
    checks.append(
        _check(
            "era5.hourly_time_axis",
            "pass" if not era_time_errors else "fail",
            f"inspected all {len(era_specs)} configured ERA5 annual time axes",
            scan_policy="all configured ERA5 years in both pilot and full modes",
            inspected_years=[int(spec.year) for spec in era_specs if spec.year is not None],
            failed_years=sorted(set(failed_era_years)),
            errors=era_time_errors,
        )
    )

    if "era5_hourly" in axes:
        target_lat, target_lon = target_grid_axes(config)
        source_lat, source_lon = axes["era5_hourly"]
        tolerance = coordinate_tolerance
        try:
            lat_indices = exact_subgrid_indices(
                source_lat, target_lat, tolerance=tolerance
            )
            lon_indices = exact_subgrid_indices(
                source_lon, target_lon, tolerance=tolerance
            )
            checks.append(
                _check(
                    "era5.target_exact_subgrid",
                    "pass",
                    "target grid is a contiguous exact ERA5 subset",
                    latitude_indices=[int(lat_indices[0]), int(lat_indices[-1])],
                    longitude_indices=[int(lon_indices[0]), int(lon_indices[-1])],
                )
            )
        except ValueError as exc:
            checks.append(
                _check("era5.target_exact_subgrid", "fail", str(exc))
            )
    return checks, axes


def _validate_phenology(
    specs: Sequence[AssetSpec], *, mode: str
) -> dict[str, Any]:
    from PIL import Image

    sample = _sample_specs([spec for spec in specs if spec.path.is_file()], mode)
    errors: list[str] = []
    shapes: set[tuple[int, int]] = set()
    shapes_by_year: dict[int, set[tuple[int, int]]] = {}
    for spec in sample:
        try:
            with Image.open(spec.path) as dataset:
                if len(dataset.getbands()) != 1:
                    raise ValueError(
                        f"band count is {len(dataset.getbands())}, expected 1"
                    )
                for required_tag in (33550, 33922):
                    if required_tag not in dataset.tag_v2:
                        raise ValueError(f"GeoTIFF tag {required_tag} is missing")
                shape = (int(dataset.height), int(dataset.width))
                shapes.add(shape)
                if spec.year is not None:
                    shapes_by_year.setdefault(int(spec.year), set()).add(shape)
        except Exception as exc:
            errors.append(f"{spec.asset_id}: {type(exc).__name__}: {exc}")
    # Raster width legitimately changes across product years.  The three
    # phenological stages must nevertheless share a grid within each year.
    inconsistent_years = {
        year: sorted(values) for year, values in shapes_by_year.items() if len(values) > 1
    }
    if inconsistent_years:
        errors.append(f"stage grids differ within year: {inconsistent_years}")
    return _check(
        "phenology.raster_metadata",
        "pass" if not errors else "fail",
        f"inspected {len(sample)} GeoTIFF headers",
        mode=mode,
        shapes=[list(value) for value in sorted(shapes)],
        reader="Pillow GeoTIFF tags 33550/33922",
        errors=errors,
    )


def validate_inventory(
    config: PipelineConfig,
    specs: Sequence[AssetSpec],
    records: pd.DataFrame,
    *,
    inspect_axes: bool = True,
    axis_mode: str = "representative",
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    endpoint_confirmed = (
        str(config.data["spei"]["two_week_endpoint_decision_status"])
        == "CONFIRMED"
    )
    missing_rows = records.loc[~records["exists"]]
    scope_limited_missing = (
        []
        if endpoint_confirmed
        else missing_rows.loc[
            missing_rows["family"] == "spei_2w", "asset_id"
        ].tolist()
    )
    missing = missing_rows.loc[
        ~missing_rows["asset_id"].isin(scope_limited_missing), "asset_id"
    ].tolist()
    checks.append(
        _check(
            "assets.present",
            "pass" if not missing else "fail",
            "all configured assets are present" if not missing else "assets are missing",
            missing=missing,
            scope_limited_missing=scope_limited_missing,
        )
    )
    historical, target = config.historical_years, config.target_years
    event_context = config.data["years"].get(
        "event_context", {"start": min(historical), "end": max(target) + 1}
    )
    event_start = int(event_context["start"])
    event_end = int(event_context["end"])
    checks.extend(
        [
            _year_continuity_check(
                records,
                "era5_hourly",
                range(event_start - 1, event_end + 1),
            ),
            _year_continuity_check(
                records,
                "era5_daily_validation",
                config.data["years"]["daily_validation"],
            ),
            _year_continuity_check(
                records, "gleam", range(event_start, event_end + 1)
            ),
            _year_continuity_check(records, "phenology", target),
        ]
    )

    manual_rows = records.loc[records["family"] == "manual"]
    if not manual_rows.empty and bool(manual_rows.iloc[0]["exists"]):
        row = manual_rows.iloc[0]
        expected = row["expected_sha256"]
        if expected and bool(row["hash_is_full"]):
            checks.append(
                _check(
                    "manual.sha256",
                    "pass" if row["sha256"] == expected else "fail",
                    "manual content hash matches configuration",
                    expected=expected,
                    observed=row["sha256"],
                )
            )

    selected_latitude: np.ndarray | None = None
    selected_longitude: np.ndarray | None = None
    try:
        v3 = pd.read_parquet(
            Path(config.data["inputs"]["v3_main"]),
            columns=["grid_id", "year", "latitude", "longitude"],
        )
        expected_cells = int(config.data["grid"]["expected_cells"])
        unique_cells = int(v3["grid_id"].nunique())
        duplicate_keys = int(v3.duplicated(["grid_id", "year"]).sum())
        selected = v3[["latitude", "longitude"]].drop_duplicates()
        selected_latitude = selected["latitude"].to_numpy(dtype=float)
        selected_longitude = selected["longitude"].to_numpy(dtype=float)
        valid = unique_cells == expected_cells and duplicate_keys == 0
        checks.append(
            _check(
                "v3.target_footprint",
                "pass" if valid else "fail",
                "V3 target footprint and key are valid",
                rows=len(v3),
                unique_cells=unique_cells,
                expected_cells=expected_cells,
                duplicate_grid_year_keys=duplicate_keys,
            )
        )
    except Exception as exc:
        checks.append(
            _check(
                "v3.target_footprint",
                "fail",
                f"{type(exc).__name__}: {exc}",
            )
        )

    axes: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    if inspect_axes:
        netcdf_specs = [
            spec
            for spec in specs
            if spec.family
            in {
                "era5_hourly",
                "era5_daily_validation",
                "gleam",
                "spei_monthly",
                "spei_2w",
            }
        ]
        netcdf_checks, axes = _validate_netcdf_axes(
            config, netcdf_specs, mode=axis_mode
        )
        checks.extend(netcdf_checks)
        phenology_specs = [spec for spec in specs if spec.family == "phenology"]
        checks.append(_validate_phenology(phenology_specs, mode=axis_mode))

    if (
        selected_latitude is not None
        and selected_longitude is not None
        and ("spei_monthly" in axes or "spei_2w" in axes)
    ):
        spei_lat, spei_lon = axes.get("spei_monthly", axes["spei_2w"])
        tolerance = float(config.data["quality"]["coordinate_tolerance"])
        covered = spei_domain_covers(
            spei_lat,
            spei_lon,
            selected_latitude,
            selected_longitude,
            tolerance=tolerance,
        )
        checks.append(
            _check(
                "spei.selected_domain_coverage",
                "pass" if covered else "fail",
                "SPEI domain covers all selected V3 coordinates",
                selected_latitude_range=[
                    float(selected_latitude.min()),
                    float(selected_latitude.max()),
                ],
                selected_longitude_range=[
                    float(selected_longitude.min()),
                    float(selected_longitude.max()),
                ],
                spei_latitude_range=[float(spei_lat.min()), float(spei_lat.max())],
                spei_longitude_range=[float(spei_lon.min()), float(spei_lon.max())],
            )
        )

    endpoint_status = str(
        config.data["spei"]["two_week_endpoint_decision_status"]
    )
    endpoint_confirmed = endpoint_status == "CONFIRMED"
    checks.append(
        _check(
            "spei_2w.timestamp_semantics",
            "pass" if endpoint_confirmed else "blocked",
            (
                "endpoint convention confirmed for the explicit accumulation/state mapping"
                if endpoint_confirmed
                else "forward-state endpoint convention awaits explicit user decision"
            ),
            timestamp_semantics=config.data["spei"][
                "two_week_timestamp_semantics"
            ],
            accumulation_timestamp_position=config.data["spei"][
                "two_week_accumulation_timestamp_position"
            ],
            state_timestamp_position=config.data["spei"][
                "two_week_state_timestamp_position"
            ],
            accumulation_days=int(
                config.data["spei"]["two_week_accumulation_days"]
            ),
            state_days=int(config.data["spei"]["two_week_state_days"]),
            sampling_days=int(
                config.data["spei"]["two_week_sampling_days"]
            ),
            event_construction_allowed=endpoint_confirmed,
            endpoint_decision_status=endpoint_status,
            decision_basis=(
                "explicit_user_confirmation"
                if endpoint_confirmed
                else "partial_scope_counterexample"
            ),
            blocking_scope="none" if endpoint_confirmed else "spei_2w_only",
            numeric_executed_by_assets_stage=False,
            numeric_enabled_for_spei_stage=endpoint_confirmed,
            included_in_output_contract=endpoint_confirmed,
        )
    )
    return checks


def build_inventory(
    config: PipelineConfig,
    *,
    hash_mode: str = "pilot",
    inspect_axes: bool = True,
    axis_mode: str | None = None,
) -> InventoryResult:
    endpoint_status = str(
        config.data["spei"]["two_week_endpoint_decision_status"]
    )
    endpoint_confirmed = endpoint_status == "CONFIRMED"
    specs = enumerate_assets(config)
    records = build_records(specs, hash_mode=hash_mode)
    selected_axis_mode = axis_mode or (
        "representative" if hash_mode == "pilot" else "all"
    )
    checks = validate_inventory(
        config,
        specs,
        records,
        inspect_axes=inspect_axes,
        axis_mode=selected_axis_mode,
    )
    return InventoryResult(
        records=records,
        checks=checks,
        metadata={
            "inventory_schema_version": 1,
            "version_id": config.version_id,
            "config_sha256": config.sha256,
            "hash_mode": hash_mode,
            "axis_mode": selected_axis_mode if inspect_axes else "disabled",
            "spei_2w_timestamp_semantics": config.data["spei"][
                "two_week_timestamp_semantics"
            ],
            "spei_2w_event_construction_allowed": endpoint_confirmed,
            "spei_2w_endpoint_decision_status": endpoint_status,
            "spei_2w_numeric_executed": False,
            "spei_2w_numeric_stage": "spei",
            "spei_2w_output_contract_enabled": endpoint_confirmed,
        },
    )


def write_inventory(
    result: InventoryResult,
    run_dir: str | Path,
    *,
    basename: str = "source_inventory",
) -> tuple[Path, Path]:
    """Write JSON and Parquet inventory artifacts without replacement."""

    root = Path(run_dir).resolve(strict=False)
    destination = ensure_within_run(root / "audit" / "inventory", root)
    destination.mkdir(parents=True, exist_ok=True)
    json_path = ensure_within_run(destination / f"{basename}.json", root)
    parquet_path = ensure_within_run(destination / f"{basename}.parquet", root)
    if json_path.exists() or parquet_path.exists():
        existing = [str(path) for path in (json_path, parquet_path) if path.exists()]
        raise FileExistsError(f"Inventory output already exists: {existing}")

    payload = json.dumps(
        result.to_jsonable(),
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ).encode("utf-8")
    with atomic_output(parquet_path, root) as parquet_partial:
        result.records.to_parquet(parquet_partial, index=False)
    with atomic_output(json_path, root) as json_partial:
        with json_partial.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    return json_path, parquet_path
