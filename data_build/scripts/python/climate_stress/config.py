"""Configuration loading and deterministic run identifiers."""

from __future__ import annotations

import hashlib
import json
import os
import re
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


_ENVIRONMENT_REFERENCE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")

# These v1 method switches are implemented as code-frozen semantics rather than
# dynamic algorithm parameters.  Requiring their sole supported value prevents
# a YAML edit from silently claiming behavior that the implementation does not
# provide.  Dynamically wired settings are intentionally absent from this map.
_FROZEN_V1_VALUES: dict[tuple[str, ...], Any] = {
    ("grid", "crs"): "EPSG:4326",
    ("grid", "nlat"): 376,
    ("grid", "nlon"): 616,
    ("grid", "north"): 53.53,
    ("grid", "west"): 73.58,
    ("grid", "step"): 0.1,
    ("grid", "footprint"): "v3_main_union",
    ("grid", "stable_id_formula"): "lat_idx * 616 + lon_idx + 1",
    ("phenology", "stages"): ["V3", "HE", "MA"],
    ("phenology", "source_crs"): (
        "+proj=aea +lat_1=15 +lat_2=65 +lat_0=30 +lon_0=95 "
        "+datum=WGS84 +units=m +no_defs"
    ),
    ("phenology", "minimum_common_pixels"): 1,
    ("phenology", "valid_doy_min"): 1,
    ("phenology", "valid_doy_max"): 366,
    ("phenology", "no_data_values"): [0, 65535],
    ("phenology", "impute"): False,
    ("phenology", "aggregate"): "rounded_mean",
    ("temperature", "source_variable"): "t2m",
    ("temperature", "source_unit"): "K",
    ("temperature", "output_unit"): "degC",
    ("temperature", "timezone"): "Asia/Shanghai",
    ("temperature", "hours_required_per_day"): 24,
    ("temperature", "quantile_method"): "linear",
    ("temperature", "strict_comparison"): True,
    ("spei", "monthly_scales"): [1, 3],
    ("spei", "thresholds"): [-1.0, -1.5],
    ("spei", "primary_min_units"): 1,
    ("spei", "strict_min_units"): 3,
    ("spei", "dynamic_interpolation"): "nearest",
    ("spei", "manual_interpolation"): "bilinear_renormalized",
    ("spei", "two_week_sampling_days"): 7,
    ("spei", "two_week_timestamp_semantics"): "unresolved",
    ("spei", "two_week_label"): "run",
    ("spei", "legacy_alignment"): "nearest",
    ("spei", "product_standardization"): "native_unknown_fit_period",
    ("gleam", "interpolation"): "bilinear_renormalized",
    ("gleam", "pentads_per_year"): 73,
    ("gleam", "remove_feb29_from_pentad"): True,
    ("gleam", "percentiles"): [10, 20, 40],
    ("gleam", "daily_event_min_days"): 5,
    ("gleam", "daily_gap_main"): 0,
    ("gleam", "daily_gap_sensitivity"): 2,
    ("gleam", "flash_start_above"): 40,
    ("gleam", "flash_end_below"): 20,
    ("gleam", "flash_min_speed_per_pentad"): 5,
    ("gleam", "flash_max_onset_pentads"): 5,
    ("gleam", "flash_primary_min_pentads"): 3,
    ("gleam", "flash_strict_min_pentads"): 4,
    ("gleam", "flash_primary_recovery_confirm"): 1,
    ("gleam", "flash_strict_recovery_confirm"): 2,
    ("compound", "sm_tail_primary"): 20,
    ("compound", "sm_tail_strict"): 10,
    ("compound", "hot_pentad_mean_temperature_percentile"): 90,
    ("compound", "hot_flash_primary"): "any_hot_pentad",
    ("compound", "hot_flash_strict"): "majority_hot_pentads",
    ("compound", "daily_hot_sm_min_days"): 5,
    ("scope", "profile"): "non2w-dual-severity",
    ("scope", "completion_scope_status"): "PARTIAL_SCOPE",
    ("scope", "spei_2w_numeric"): False,
    ("scope", "spei_2w_output"): False,
    ("scope", "compound_mode"): "dual_independent_severity",
    ("quality", "random_seed"): 42,
}

_UNSUPPORTED_RUNTIME_KEYS = {
    "era_time_chunk_hours",
    "gleam_time_chunk_days",
    "compute_dtype",
}

CODE_FROZEN_RUNTIME_CONSTANTS: dict[str, Any] = {
    "gleam_native_time_chunk_days": 12,
    "era_source_read_dtype": "float64",
    "era_daily_output_dtype": "float32",
    "era_time_chunk_policy": "full_time_axis_by_native_spatial_tile",
}


def frozen_v1_method_fragment() -> dict[str, Any]:
    """Return the complete required method fragment for isolated test configs."""

    fragment: dict[str, Any] = {}
    for path, expected in _FROZEN_V1_VALUES.items():
        current = fragment
        for component in path[:-1]:
            current = current.setdefault(component, {})
        current[path[-1]] = deepcopy(expected)
    return fragment


def _expand_environment(value: Any) -> Any:
    """Recursively expand explicit ``${NAME}`` references without defaults."""

    if isinstance(value, dict):
        return {key: _expand_environment(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_expand_environment(item) for item in value]
    if not isinstance(value, str):
        return value

    def replace(match: re.Match[str]) -> str:
        return os.environ[match.group(1)]

    return _ENVIRONMENT_REFERENCE.sub(replace, value)


def _environment_references(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set().union(*(_environment_references(item) for item in value.values()))
    if isinstance(value, list):
        return set().union(*(_environment_references(item) for item in value))
    if isinstance(value, str):
        return set(_ENVIRONMENT_REFERENCE.findall(value))
    return set()


def _iter_path_values(value: Any, prefix: str) -> list[tuple[str, str]]:
    if isinstance(value, dict):
        result: list[tuple[str, str]] = []
        for key, item in value.items():
            result.extend(_iter_path_values(item, f"{prefix}.{key}"))
        return result
    if isinstance(value, str):
        return [(prefix, value)]
    return []


def _repository_root(config_path: Path) -> Path | None:
    for candidate in (config_path.parent, *config_path.parents):
        if (candidate / ".git").exists():
            return candidate.resolve()
    return None


def _validate_resolved_paths(data: dict[str, Any], config_path: Path) -> None:
    path_values: list[tuple[str, str]] = []
    manual = data.get("manual")
    if not isinstance(manual, dict) or not isinstance(manual.get("path"), str):
        raise ValueError("manual.path is required")
    path_values.append(("manual.path", str(manual["path"])))
    path_values.extend(_iter_path_values(data["inputs"], "inputs"))
    output_root = str(data["output"]["root"])
    path_values.append(("output.root", output_root))
    for label, raw_path in path_values:
        if not Path(raw_path).is_absolute():
            raise ValueError(f"Resolved path must be absolute: {label}={raw_path!r}")

    output = Path(output_root).resolve(strict=False)
    anchor = Path(output.anchor).resolve(strict=False)
    user_home = Path.home().resolve(strict=False)
    if (
        output == anchor
        or output.parent == anchor
        or user_home == output
        or user_home.is_relative_to(output)
    ):
        raise ValueError(f"output.root is an unsafe broad directory: {output}")
    repo_root = _repository_root(config_path)
    if repo_root is not None and output.is_relative_to(repo_root):
        raise ValueError(
            f"output.root must be outside the repository/worktree: {output}"
        )


def _validate_frozen_v1_values(data: dict[str, Any]) -> None:
    for path, expected in _FROZEN_V1_VALUES.items():
        current: Any = data
        for component in path:
            if not isinstance(current, dict) or component not in current:
                raise ValueError(
                    f"Frozen v1 config key is required: {'.'.join(path)}"
                )
            current = current[component]
        if current != expected or type(current) is not type(expected):
            raise ValueError(
                f"Unsupported value for code-frozen {'.'.join(path)}: "
                f"expected {expected!r}, received {current!r}"
            )


def _validate_resource_budgets(data: dict[str, Any]) -> None:
    runtime = data.get("runtime")
    if not isinstance(runtime, dict):
        raise ValueError("Missing config section: runtime")
    unsupported = sorted(_UNSUPPORTED_RUNTIME_KEYS.intersection(runtime))
    if unsupported:
        raise ValueError(
            "Unsupported runtime config keys are code-frozen and must be absent: "
            + ", ".join(unsupported)
        )
    budgets: dict[str, int] = {}
    for key in ("pilot_peak_rss_budget_bytes", "full_peak_rss_budget_bytes"):
        value = runtime.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"runtime.{key} must be a positive integer")
        budgets[key] = value
    if budgets["full_peak_rss_budget_bytes"] < budgets["pilot_peak_rss_budget_bytes"]:
        raise ValueError(
            "runtime.full_peak_rss_budget_bytes must be at least the pilot budget"
        )


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class PipelineConfig:
    """Validated configuration plus its source path and content hash."""

    path: Path
    data: dict[str, Any]
    sha256: str
    template_sha256: str | None = None

    @property
    def version_id(self) -> str:
        return str(self.data["version_id"])

    @property
    def output_root(self) -> Path:
        return Path(self.data["output"]["root"])

    @property
    def scope_profile(self) -> str:
        return str(
            self.data.get("scope", {}).get("profile", "non2w-dual-severity")
        )

    @property
    def completion_scope_status(self) -> str:
        return str(
            self.data.get("scope", {}).get(
                "completion_scope_status", "PARTIAL_SCOPE"
            )
        )

    def peak_rss_budget_bytes(self, mode: str) -> int:
        if mode not in {"pilot", "full"}:
            raise ValueError(f"Unknown execution mode: {mode}")
        return int(self.data["runtime"][f"{mode}_peak_rss_budget_bytes"])

    @property
    def target_years(self) -> list[int]:
        return [int(v) for v in self.data["years"]["target"]]

    @property
    def historical_years(self) -> list[int]:
        return [int(v) for v in self.data["years"]["historical"]]

    @property
    def windows(self) -> tuple[str, ...]:
        return tuple(self.data["phenology"]["windows"].keys())

    def make_run_id(self, label: str | None = None) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        suffix = f"-{label}" if label else ""
        return f"{timestamp}-{self.sha256[:10]}{suffix}"

    def as_manifest_fragment(self) -> dict[str, Any]:
        return {
            "config_path": str(self.path),
            "config_sha256": self.sha256,
            "template_config_sha256": self.template_sha256 or self.sha256,
            "effective_config_sha256": self.sha256,
            "version_id": self.version_id,
            "config": self.data,
            "resolved_paths": self.resolved_paths(),
            "code_frozen_runtime_constants": CODE_FROZEN_RUNTIME_CONSTANTS,
        }

    def resolved_paths(self) -> dict[str, str]:
        values = _iter_path_values(self.data["inputs"], "inputs")
        values.append(("manual.path", str(self.data["manual"]["path"])))
        values.append(("output.root", str(self.data["output"]["root"])))
        return dict(sorted(values))


def load_config(path: str | Path) -> PipelineConfig:
    source = Path(path).resolve()
    raw = source.read_bytes()
    parsed = yaml.safe_load(raw.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("Pipeline config must be a YAML mapping")
    references = sorted(_environment_references(parsed))
    invalid_references = [
        name for name in references if not os.environ.get(name, "").strip()
    ]
    if invalid_references:
        raise ValueError(
            "Required environment variables are missing or empty: "
            + ", ".join(invalid_references)
        )
    data = _expand_environment(parsed)
    required = {"version_id", "inputs", "output", "years", "grid", "phenology", "quality"}
    missing = sorted(required.difference(data))
    if missing:
        raise ValueError(f"Missing config sections: {missing}")
    _validate_frozen_v1_values(data)
    _validate_resource_budgets(data)
    _validate_resolved_paths(data, source)
    template_digest = hashlib.sha256(
        _canonical_json(parsed).encode("utf-8")
    ).hexdigest()
    canonical = _canonical_json(data).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()
    return PipelineConfig(
        path=source,
        data=data,
        sha256=digest,
        template_sha256=template_digest,
    )
