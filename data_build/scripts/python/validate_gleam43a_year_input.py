"""Validate one year of official daily GLEAM 4.3a soil-moisture inputs.

The validator is read-only.  It computes a complete SHA-256 digest for each
NetCDF file, checks the complete calendar-day axis and native 0.1-degree
global grid, and inspects the variable metadata used by the climate-stress
pipeline.  It intentionally samples, rather than materializes, the global
soil-moisture data array.
"""

from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Sequence

import netCDF4 as nc
import numpy as np


LAYERS = ("SMrz", "SMs")
EXPECTED_LATITUDE = 89.95 - np.arange(1800, dtype=np.float64) * 0.1
EXPECTED_LONGITUDE = -179.95 + np.arange(3600, dtype=np.float64) * 0.1


def sha256_file(path: Path, *, block_bytes: int = 8 * 1024 * 1024) -> str:
    """Return a full-file SHA-256 digest without loading the file at once."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(block_bytes):
            digest.update(block)
    return digest.hexdigest().upper()


def expected_dates(year: int) -> tuple[date, ...]:
    """Return every calendar date in *year*, including February 29."""

    count = 366 if calendar.isleap(year) else 365
    first = date(year, 1, 1)
    return tuple(first + timedelta(days=offset) for offset in range(count))


def _decode_dates(time_variable: Any) -> tuple[date, ...]:
    units = str(time_variable.getncattr("units"))
    calendar_name = str(time_variable.getncattr("calendar"))
    decoded = nc.num2date(
        time_variable[:],
        units=units,
        calendar=calendar_name,
        only_use_cftime_datetimes=False,
        only_use_python_datetimes=True,
    )
    return tuple(value.date() for value in decoded)


def _sample_summary(variable: Any) -> dict[str, Any]:
    time_indices = np.asarray(
        sorted({0, max(0, variable.shape[0] // 2), variable.shape[0] - 1}),
        dtype=int,
    )
    latitude_indices = np.linspace(0, variable.shape[1] - 1, 19, dtype=int)
    longitude_indices = np.linspace(0, variable.shape[2] - 1, 37, dtype=int)
    sampled = np.ma.asarray(
        variable[time_indices, latitude_indices, longitude_indices]
    )
    values = np.asarray(sampled.filled(np.nan), dtype=np.float64)
    finite = values[np.isfinite(values)]
    return {
        "sample_shape": [int(value) for value in sampled.shape],
        "sample_masked_count": int(np.ma.getmaskarray(sampled).sum()),
        "sample_finite_count": int(finite.size),
        "sample_finite_min": float(finite.min()) if finite.size else None,
        "sample_finite_max": float(finite.max()) if finite.size else None,
    }


def validate_file(path: Path, *, layer: str, year: int) -> dict[str, Any]:
    """Validate one daily GLEAM 4.3a layer and return audit metadata."""

    if not path.is_file():
        raise FileNotFoundError(path)
    wanted_dates = expected_dates(year)
    with nc.Dataset(path) as dataset:
        dimensions = {name: len(value) for name, value in dataset.dimensions.items()}
        expected_dimensions = {
            "time": len(wanted_dates),
            "lat": 1800,
            "lon": 3600,
        }
        if dimensions != expected_dimensions:
            raise ValueError(
                f"{path}: dimensions {dimensions!r} do not equal "
                f"{expected_dimensions!r}"
            )
        required_variables = {layer, "time", "lat", "lon"}
        missing_variables = sorted(required_variables.difference(dataset.variables))
        if missing_variables:
            raise ValueError(f"{path}: missing variables {missing_variables!r}")

        soil = dataset.variables[layer]
        if soil.dimensions != ("time", "lat", "lon"):
            raise ValueError(f"{path}: unexpected {layer} dimensions {soil.dimensions!r}")
        if np.dtype(soil.dtype) != np.dtype("float32"):
            raise ValueError(f"{path}: unexpected {layer} dtype {soil.dtype!r}")
        fill_value = float(soil.getncattr("_FillValue"))
        if fill_value != -999.0:
            raise ValueError(f"{path}: unexpected {layer} _FillValue {fill_value!r}")
        units = str(soil.getncattr("units"))
        if units != "m3.m-3":
            raise ValueError(f"{path}: unexpected {layer} units {units!r}")

        time_variable = dataset.variables["time"]
        time_units = str(time_variable.getncattr("units"))
        time_calendar = str(time_variable.getncattr("calendar"))
        if time_units != "days since 1900-01-01":
            raise ValueError(f"{path}: unexpected time units {time_units!r}")
        if time_calendar != "proleptic_gregorian":
            raise ValueError(f"{path}: unexpected calendar {time_calendar!r}")
        observed_dates = _decode_dates(time_variable)
        if observed_dates != wanted_dates:
            raise ValueError(
                f"{path}: time axis is not the complete calendar year {year}"
            )

        latitude = np.asarray(dataset.variables["lat"][:], dtype=np.float64)
        longitude = np.asarray(dataset.variables["lon"][:], dtype=np.float64)
        if not np.allclose(latitude, EXPECTED_LATITUDE, rtol=0, atol=1e-10):
            raise ValueError(f"{path}: latitude axis differs from GLEAM 0.1-degree grid")
        if not np.allclose(longitude, EXPECTED_LONGITUDE, rtol=0, atol=1e-10):
            raise ValueError(f"{path}: longitude axis differs from GLEAM 0.1-degree grid")

        version = str(dataset.getncattr("Version"))
        if version != "4.3a":
            raise ValueError(f"{path}: unexpected GLEAM version {version!r}")
        sample = _sample_summary(soil)
        report: dict[str, Any] = {
            "path": str(path.resolve()),
            "layer": layer,
            "year": year,
            "size_bytes": int(path.stat().st_size),
            "sha256": sha256_file(path),
            "dimensions": expected_dimensions,
            "variable_dimensions": list(soil.dimensions),
            "variable_dtype": str(soil.dtype),
            "variable_units": units,
            "fill_value": fill_value,
            "time_units": time_units,
            "calendar": time_calendar,
            "time_start": observed_dates[0].isoformat(),
            "time_end": observed_dates[-1].isoformat(),
            "time_count": len(observed_dates),
            "latitude_start": float(latitude[0]),
            "latitude_end": float(latitude[-1]),
            "latitude_step": float(latitude[1] - latitude[0]),
            "longitude_start": float(longitude[0]),
            "longitude_end": float(longitude[-1]),
            "longitude_step": float(longitude[1] - longitude[0]),
            "dataset": str(dataset.getncattr("Dataset")),
            "version": version,
            **sample,
        }
    return report


def _local_baseline_hashes(values: Sequence[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError("--local-baseline-sha256 must use LAYER=HEX format")
        layer, digest = value.split("=", 1)
        if layer not in LAYERS or len(digest) != 64:
            raise ValueError(f"invalid expected digest {value!r}")
        parsed[layer] = digest.upper()
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=(Path(os.environ["GLEAM_ROOT"]) if os.environ.get("GLEAM_ROOT") else None),
        required=not bool(os.environ.get("GLEAM_ROOT")),
        help="GLEAM root containing YEAR/LAYER_YEAR_GLEAM_v4.3a.nc",
    )
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument(
        "--local-baseline-sha256",
        action="append",
        default=[],
        metavar="LAYER=HEX",
        help=(
            "optional previously recorded local digest; may be repeated and "
            "must not be interpreted as an upstream-published checksum"
        ),
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="optional new audit JSON path; existing files are never replaced",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    local_baselines = _local_baseline_hashes(args.local_baseline_sha256)
    reports = []
    for layer in LAYERS:
        path = args.root / str(args.year) / f"{layer}_{args.year}_GLEAM_v4.3a.nc"
        report = validate_file(path, layer=layer, year=args.year)
        baseline = local_baselines.get(layer)
        if baseline is not None and report["sha256"] != baseline:
            raise ValueError(
                f"{path}: SHA-256 {report['sha256']} does not equal local "
                f"baseline {baseline}"
            )
        report["local_baseline_sha256_matched"] = baseline is not None
        reports.append(report)

    payload = {
        "schema_version": 1,
        "validator": "validate_gleam43a_year_input.py",
        "year": args.year,
        "remote_checksum_available": False,
        "sha256_semantics": "local baseline only; no upstream checksum available",
        "layers": reports,
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        with args.output_json.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(serialized)
    print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
