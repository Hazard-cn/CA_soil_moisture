"""Single complete frozen-v1 config helper shared by climate-stress tests."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from climate_stress.config import frozen_v1_method_fragment


def complete_frozen_v1_fixture(
    data: dict[str, Any],
    tmp_path: Path,
) -> dict[str, Any]:
    """Fill every required code-frozen method key without overriding a test."""

    result = deepcopy(data)
    for section, values in frozen_v1_method_fragment().items():
        target = result.setdefault(section, {})
        for key, value in values.items():
            target.setdefault(key, value)
    result.setdefault("spei", {}).setdefault(
        "two_week_endpoint_decision_status", "PENDING_USER_DECISION"
    )
    scope = result.setdefault("scope", {})
    scope.setdefault("profile", "non2w-dual-severity")
    scope.setdefault("completion_scope_status", "PARTIAL_SCOPE")
    scope.setdefault("spei_2w_numeric", False)
    scope.setdefault("spei_2w_output", False)
    result.setdefault(
        "manual",
        {"path": str((tmp_path / "manual.docx").resolve()), "sha256": "0" * 64},
    )
    runtime = result.setdefault("runtime", {})
    runtime.setdefault("gleam_cell_block_size", 128)
    runtime.setdefault("validation_cell_block_size", 128)
    runtime.setdefault("parquet_row_group_size", 262_144)
    runtime.setdefault("storage_dtype", "float64")
    runtime.setdefault("pilot_peak_rss_budget_bytes", 16 * 1024**3)
    runtime.setdefault("full_peak_rss_budget_bytes", 32 * 1024**3)
    return result
