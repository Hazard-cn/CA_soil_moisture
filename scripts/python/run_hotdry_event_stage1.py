"""Run the frozen interface smoke or full Stage-1 support audit.

This script builds event/soil-moisture records only.  It never estimates the
yield model.  A failing named-zone support gate produces a STOP manifest and
does not change any threshold, event duration, window, or mapping rule.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable

import numpy as np
import pandas as pd
import xarray as xr


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

from hotdry_event_core import (  # noqa: E402
    HotDryEvent,
    aggregate_grid_year_events,
    calculate_sm_recovery,
    identify_hotdry_events,
)
from hotdry_event_validators import (  # noqa: E402
    NAMED_ZONES,
    validate_event_panel,
    validate_event_run_manifest,
)


YEARS = (2016, 2017, 2018, 2019)
ZONE_PROVINCES = {
    "NE": {"黑龙江省", "吉林省", "辽宁省", "内蒙古自治区"},
    "HHH": {"河南省", "山东省", "河北省", "安徽省", "江苏省"},
    "SW": {"四川省", "贵州省", "云南省", "广西壮族自治区", "重庆市"},
    "NW": {"甘肃省", "宁夏回族自治区", "新疆维吾尔自治区", "陕西省"},
    "SH": {"广东省", "福建省", "浙江省", "江西省", "海南省", "湖南省", "湖北省"},
}
REQUIRED_PANEL_FIELDS = (
    "grid_id",
    "year",
    "province",
    "latitude",
    "longitude",
    "ln_yield",
    "ca",
    "gdd_10_29",
    "pr_sum",
    "v3_doy",
    "ma_doy",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("smoke", "stage1"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--tmax-dir", type=Path, required=True)
    parser.add_argument("--precip-dir", type=Path, required=True)
    parser.add_argument("--smrz-dir", type=Path, required=True)
    parser.add_argument("--hash-cache", type=Path)
    return parser.parse_args()


def file_digest(path: Path) -> dict[str, Any]:
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            md5.update(chunk)
            sha256.update(chunk)
    return {
        "path": str(path).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "md5": md5.hexdigest(),
        "sha256": sha256.hexdigest(),
    }


def year_input_paths(
    year: int,
    *,
    tmax_dir: Path,
    precip_dir: Path,
    smrz_dir: Path,
) -> tuple[Path, Path, Path]:
    return (
        tmax_dir / f"daily_temp_{year}.nc",
        precip_dir / f"CHM_PRE_0.1deg_{year}.nc",
        smrz_dir / f"GLEAM_SM_0.1deg_TEMPgrid_{year}.nc",
    )


def input_paths(
    panel_path: Path,
    *,
    tmax_dir: Path,
    precip_dir: Path,
    smrz_dir: Path,
) -> list[tuple[str, Path]]:
    values: list[tuple[str, Path]] = [
        ("v3_panel", panel_path),
        ("zone_mapping", PROJECT_ROOT / "scripts/stata/v3sub_step0_subsamples.do"),
    ]
    for year in YEARS:
        temp_path, pre_path, sm_path = year_input_paths(
            year,
            tmax_dir=tmax_dir,
            precip_dir=precip_dir,
            smrz_dir=smrz_dir,
        )
        values.extend(
            [
                (f"tmax_{year}", temp_path),
                (f"precipitation_{year}", pre_path),
                (f"smrz_{year}", sm_path),
            ]
        )
    values.extend(
        [
            ("implementation_core", PROJECT_ROOT / "scripts/python/hotdry_event_core.py"),
            ("implementation_validators", PROJECT_ROOT / "scripts/python/hotdry_event_validators.py"),
            ("implementation_runner", PROJECT_ROOT / "scripts/python/run_hotdry_event_stage1.py"),
            ("contract_event_panel", PROJECT_ROOT / "docs/contracts/event_panel.schema.json"),
            ("contract_run_manifest", PROJECT_ROOT / "docs/contracts/run_manifest.schema.json"),
            (
                "frozen_design",
                PROJECT_ROOT / "quality_reports/plans/2026-07-15_hotdry_event_duration_intensity_design_v1.md",
            ),
            (
                "design_review_round2_pass",
                PROJECT_ROOT / "quality_reports/plans/2026-07-15_hotdry_event_design_review_round2_pass.md",
            ),
            ("test_core", PROJECT_ROOT / "tests/test_hotdry_event_core.py"),
            ("test_validators", PROJECT_ROOT / "tests/test_hotdry_event_validators.py"),
        ]
    )
    return values


def inventory_inputs(
    panel_path: Path,
    *,
    tmax_dir: Path,
    precip_dir: Path,
    smrz_dir: Path,
    cache_path: Path | None,
) -> list[dict[str, Any]]:
    expected = input_paths(
        panel_path,
        tmax_dir=tmax_dir,
        precip_dir=precip_dir,
        smrz_dir=smrz_dir,
    )
    by_path: dict[str, dict[str, Any]] = {}
    if cache_path is not None and cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        by_path = {item["path"]: item for item in cached}

    output: list[dict[str, Any]] = []
    for role, path in expected:
        if not path.is_file():
            raise FileNotFoundError(path)
        key = str(path).replace("\\", "/")
        cached_item = by_path.get(key)
        if cached_item is not None and cached_item["bytes"] == path.stat().st_size:
            output.append({"role": role, **cached_item})
        else:
            output.append({"role": role, **file_digest(path)})
    if cache_path is not None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            json.dumps([{key: value for key, value in item.items() if key != "role"} for item in output], indent=2),
            encoding="utf-8",
        )
    return output


def zone_for_province(province: Any) -> str:
    value = str(province)
    for zone, provinces in ZONE_PROVINCES.items():
        if value in provinces:
            return zone
    return "Other"


def canonical_grid_id(value: Any) -> str:
    numeric = float(value)
    return str(int(numeric)) if numeric.is_integer() else format(numeric, ".17g")


def sample_key_sha256(panel: pd.DataFrame) -> str:
    keys = sorted(
        (canonical_grid_id(row.grid_id), int(row.year))
        for row in panel[["grid_id", "year"]].itertuples(index=False)
    )
    payload = "".join(f"{grid_id}|{year:04d}\n" for grid_id, year in keys).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_panel_inventory(panel: pd.DataFrame) -> None:
    missing = [field for field in REQUIRED_PANEL_FIELDS if field not in panel.columns]
    if missing:
        raise ValueError(f"V3 missing fields: {missing}")
    if len(panel) != 69_038:
        raise ValueError(f"V3 rows {len(panel)} != 69038")
    if panel["grid_id"].nunique() != 22_180:
        raise ValueError(f"V3 grids {panel['grid_id'].nunique()} != 22180")
    if panel.duplicated(["grid_id", "year"]).any():
        raise ValueError("V3 grid_id-year is not unique")


def select_smoke_panel(panel: pd.DataFrame) -> pd.DataFrame:
    selected: list[pd.DataFrame] = []
    named = panel[panel["zone"].isin(NAMED_ZONES)]
    for zone in NAMED_ZONES:
        for year in YEARS:
            part = named[(named["zone"] == zone) & (named["year"] == year)].sort_values("grid_id")
            selected.append(part.head(2))
    return pd.concat(selected, ignore_index=False).sort_values(["year", "zone", "grid_id"])


def map_grid_indices(
    panel: pd.DataFrame, latitude: np.ndarray, longitude: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    lat_values = panel["latitude"].to_numpy(dtype=float)
    lon_values = panel["longitude"].to_numpy(dtype=float)
    lat_index = np.rint((float(latitude[0]) - lat_values) / 0.1).astype(int)
    lon_index = np.rint((lon_values - float(longitude[0])) / 0.1).astype(int)
    if (
        np.any(lat_index < 0)
        or np.any(lat_index >= latitude.size)
        or np.any(lon_index < 0)
        or np.any(lon_index >= longitude.size)
    ):
        raise ValueError("V3 coordinate lies outside the aligned reference grid")
    lat_error = np.abs(latitude[lat_index] - lat_values)
    lon_error = np.abs(longitude[lon_index] - lon_values)
    if float(lat_error.max(initial=0.0)) > 1e-5 or float(lon_error.max(initial=0.0)) > 1e-5:
        raise ValueError(
            f"coordinate tolerance failed: lat={lat_error.max()}, lon={lon_error.max()}"
        )
    paired = pd.DataFrame(
        {
            "lat_index": lat_index,
            "lon_index": lon_index,
            "grid_id": panel["grid_id"].map(canonical_grid_id).to_numpy(),
        }
    )
    if any(
        group["grid_id"].nunique() > 1
        for _, group in paired.groupby(["lat_index", "lon_index"], sort=False)
    ):
        raise ValueError("multiple grid_ids map to one reference-grid center")
    return lat_index, lon_index, lat_error, lon_error


def daily_values(variable: xr.DataArray, lat_index: np.ndarray, lon_index: np.ndarray) -> np.ndarray:
    if len(lat_index) >= 1_000:
        full = np.asarray(variable.values)
        return np.asarray(full[:, lat_index, lon_index], dtype=float)
    selected = variable.isel(
        latitude=xr.DataArray(lat_index, dims="point"),
        longitude=xr.DataArray(lon_index, dims="point"),
    )
    return np.asarray(selected.transpose(variable.dims[0], "point").values, dtype=float)


def verify_calendar_and_grid(
    temp: xr.Dataset, precipitation: xr.Dataset, sm: xr.Dataset, year: int
) -> tuple[np.ndarray, np.ndarray]:
    expected = pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D").to_numpy()
    dates = (
        np.asarray(temp["valid_time"].values),
        np.asarray(precipitation["time"].values),
        np.asarray(sm["time"].values),
    )
    for values in dates:
        if not np.array_equal(values.astype("datetime64[ns]"), expected.astype("datetime64[ns]")):
            raise ValueError(f"{year} calendar is incomplete, duplicated, or misaligned")
    latitude = np.asarray(temp["latitude"].values, dtype=float)
    longitude = np.asarray(temp["longitude"].values, dtype=float)
    for dataset in (precipitation, sm):
        if not np.array_equal(latitude, np.asarray(dataset["latitude"].values, dtype=float)):
            raise ValueError(f"{year} latitude arrays differ")
        if not np.array_equal(longitude, np.asarray(dataset["longitude"].values, dtype=float)):
            raise ValueError(f"{year} longitude arrays differ")
    if latitude.shape != (376,) or longitude.shape != (616,):
        raise ValueError(f"{year} aligned grid is not 376x616")
    return latitude, longitude


def build_records_for_year(
    year_panel: pd.DataFrame,
    year: int,
    *,
    tmax_dir: Path,
    precip_dir: Path,
    smrz_dir: Path,
    coordinate_audit: list[dict[str, Any]],
    rng: np.random.Generator,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    temp_path, pre_path, sm_path = year_input_paths(
        year,
        tmax_dir=tmax_dir,
        precip_dir=precip_dir,
        smrz_dir=smrz_dir,
    )
    with xr.open_dataset(temp_path) as temp, xr.open_dataset(pre_path) as pre, xr.open_dataset(sm_path) as sm:
        latitude, longitude = verify_calendar_and_grid(temp, pre, sm, year)
        lat_index, lon_index, lat_error, lon_error = map_grid_indices(
            year_panel, latitude, longitude
        )
        tmax = daily_values(temp["t2m_max"], lat_index, lon_index)
        precipitation = daily_values(pre["pre"], lat_index, lon_index)
        smrz = daily_values(sm["SMrz"], lat_index, lon_index)

    records: list[dict[str, Any]] = []
    grid_year_status: list[dict[str, Any]] = []
    rows = list(year_panel.itertuples(index=False))
    for point, row in enumerate(rows):
        start = int(row.v3_doy) - 30 if pd.notna(row.v3_doy) else -1
        end = int(row.ma_doy) if pd.notna(row.ma_doy) else -1
        window_valid = 1 <= start <= end <= tmax.shape[0]
        complete_case = all(
            pd.notna(getattr(row, field))
            for field in REQUIRED_PANEL_FIELDS
            if field != "province"
        ) and bool(str(row.province).strip())
        if not window_valid:
            temp_valid = pre_valid = 0
            daily_complete = False
        else:
            temp_valid = int(np.isfinite(tmax[start - 1 : end, point]).sum())
            pre_valid = int(np.isfinite(precipitation[start - 1 : end, point]).sum())
            daily_complete = temp_valid == end - start + 1 and pre_valid == end - start + 1
        analysis_ready = bool(window_valid and complete_case and daily_complete)
        status = {
            "grid_id": canonical_grid_id(row.grid_id),
            "year": year,
            "zone": row.zone,
            "analysis_ready": analysis_ready,
            "event_positive": False,
            "event_count": 0,
            "antecedent_complete_events": 0,
            "recovery_risk_events": 0,
            "right_censored_events": 0,
            "drawdown_complete_events": 0,
        }
        if not analysis_ready:
            grid_year_status.append(status)
            continue

        daily_tmax = tmax[:, point]
        daily_pre = precipitation[:, point]
        daily_sm = smrz[:, point]
        events = identify_hotdry_events(daily_tmax, daily_pre, start, end)
        aggregate = aggregate_grid_year_events(events, daily_tmax, daily_pre, start, end)
        status["event_positive"] = bool(events)
        status["event_count"] = len(events)

        base = {
            "contract_version": "event-panel-v1",
            "grid_id": canonical_grid_id(row.grid_id),
            "year": year,
            "zone": row.zone,
            "latitude": float(row.latitude),
            "longitude": float(row.longitude),
            "window_start_doy": start,
            "window_end_doy": end,
            "window_total_days": end - start + 1,
            "temp_valid_days": temp_valid,
            "pre_valid_days": pre_valid,
            "daily_complete_flag": daily_complete,
            "event_count": int(aggregate["event_count"]),
            "total_duration_days": int(aggregate["total_duration_days"]),
            "longest_duration_days": int(aggregate["longest_duration_days"]),
            "mean_event_intensity_c": float(aggregate["mean_event_intensity_c"]),
            "cumulative_excess_cday": float(aggregate["cumulative_excess_cday"]),
            "compound_share_of_heat_days": aggregate["compound_share_of_heat_days"],
        }
        if not events:
            records.append(
                {
                    **base,
                    "event_seq": 0,
                    "event_id": None,
                    "event_indicator": False,
                    "is_grid_year_representative": True,
                    "onset_doy": None,
                    "end_doy": None,
                    "duration_days": None,
                    "event_mean_excess_c": None,
                    "event_cumulative_excess_cday": None,
                    "antecedent_smrz": None,
                    "antecedent_valid_days": None,
                    "sm_channel_complete_flag": None,
                    "event_min_smrz": None,
                    "drawdown_smrz": None,
                    "drawdown_overlap_next_event": None,
                    "recovery_days": None,
                    "recovery_observed": None,
                    "right_censored": None,
                    "censor_reason": None,
                }
            )
        else:
            for event_index, event in enumerate(events):
                next_onset = (
                    events[event_index + 1].onset_doy
                    if event_index + 1 < len(events)
                    else None
                )
                recovery = calculate_sm_recovery(
                    daily_sm,
                    event,
                    ma_doy=end,
                    next_event_onset_doy=next_onset,
                )
                sm_complete = bool(
                    recovery.antecedent_valid_days == 14
                    and recovery.antecedent_smrz is not None
                    and recovery.event_min_smrz is not None
                    and recovery.drawdown_smrz is not None
                )
                if recovery.antecedent_valid_days == 14:
                    status["antecedent_complete_events"] += 1
                if recovery.drawdown_smrz is not None:
                    status["drawdown_complete_events"] += 1
                if recovery.recovery_observed is not None:
                    status["recovery_risk_events"] += 1
                    status["right_censored_events"] += int(bool(recovery.right_censored))
                seq = event_index + 1
                records.append(
                    {
                        **base,
                        "event_seq": seq,
                        "event_id": f"{canonical_grid_id(row.grid_id)}|{year:04d}|{seq}",
                        "event_indicator": True,
                        "is_grid_year_representative": seq == 1,
                        "onset_doy": event.onset_doy,
                        "end_doy": event.end_doy,
                        "duration_days": event.duration_days,
                        "event_mean_excess_c": event.mean_excess_c,
                        "event_cumulative_excess_cday": event.cumulative_excess_cday,
                        "antecedent_smrz": recovery.antecedent_smrz,
                        "antecedent_valid_days": recovery.antecedent_valid_days,
                        "sm_channel_complete_flag": sm_complete,
                        "event_min_smrz": recovery.event_min_smrz,
                        "drawdown_smrz": recovery.drawdown_smrz,
                        "drawdown_overlap_next_event": recovery.drawdown_overlap_next_event,
                        "recovery_days": recovery.recovery_days,
                        "recovery_observed": recovery.recovery_observed,
                        "right_censored": recovery.right_censored,
                        "censor_reason": recovery.censor_reason,
                    }
                )
        grid_year_status.append(status)

    for zone in NAMED_ZONES:
        candidates = [index for index, row in enumerate(rows) if row.zone == zone]
        if not candidates:
            continue
        for draw_number in range(20):
            point = int(rng.choice(candidates))
            row = rows[point]
            start = max(1, int(row.v3_doy) - 30) if pd.notna(row.v3_doy) else 1
            end = min(tmax.shape[0], int(row.ma_doy)) if pd.notna(row.ma_doy) else tmax.shape[0]
            doy = int(rng.integers(start, end + 1))
            coordinate_audit.append(
                {
                    "year": year,
                    "zone": zone,
                    "draw_number": draw_number + 1,
                    "grid_id": canonical_grid_id(row.grid_id),
                    "panel_latitude": float(row.latitude),
                    "panel_longitude": float(row.longitude),
                    "latitude_index": int(lat_index[point]),
                    "longitude_index": int(lon_index[point]),
                    "reference_latitude": float(latitude[lat_index[point]]),
                    "reference_longitude": float(longitude[lon_index[point]]),
                    "latitude_abs_error": float(lat_error[point]),
                    "longitude_abs_error": float(lon_error[point]),
                    "doy": doy,
                    "tmax_c": float(tmax[doy - 1, point]),
                    "precipitation_mm": float(precipitation[doy - 1, point]),
                    "smrz": float(smrz[doy - 1, point]),
                }
            )
    return records, grid_year_status


def support_tables(status: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    named = status[status["zone"].isin(NAMED_ZONES)].copy()
    rows: list[dict[str, Any]] = []
    for zone in NAMED_ZONES:
        for year in YEARS:
            part = named[(named["zone"] == zone) & (named["year"] == year)]
            ready = part[part["analysis_ready"]]
            risk = int(ready["recovery_risk_events"].sum())
            censored = int(ready["right_censored_events"].sum())
            rows.append(
                {
                    "zone": zone,
                    "year": year,
                    "analysis_ready_grids": int(ready["grid_id"].nunique()),
                    "analysis_ready_grid_years": int(len(ready)),
                    "event_positive_grid_years": int(ready["event_positive"].sum()),
                    "event_count": int(ready["event_count"].sum()),
                    "antecedent_complete_events": int(ready["antecedent_complete_events"].sum()),
                    "drawdown_complete_events": int(ready["drawdown_complete_events"].sum()),
                    "recovery_risk_events": risk,
                    "right_censored_events": censored,
                    "right_censoring_rate": censored / risk if risk else np.nan,
                }
            )
    by_year = pd.DataFrame(rows)
    zones: list[dict[str, Any]] = []
    stop_reasons: list[str] = []
    for zone in NAMED_ZONES:
        annual = by_year[by_year["zone"] == zone]
        ready_rows = named[(named["zone"] == zone) & named["analysis_ready"]]
        antecedent_total = int(annual["antecedent_complete_events"].sum())
        annual_max_share = (
            float(annual["antecedent_complete_events"].max() / antecedent_total)
            if antecedent_total
            else np.nan
        )
        event_years = int((annual["event_count"] > 0).sum())
        risk = int(annual["recovery_risk_events"].sum())
        censored = int(annual["right_censored_events"].sum())
        censor_rate = censored / risk if risk else np.nan
        values = {
            "zone": zone,
            "analysis_ready_grids": int(ready_rows["grid_id"].nunique()),
            "analysis_ready_grid_years": int(len(ready_rows)),
            "event_positive_grid_years": int(ready_rows["event_positive"].sum()),
            "event_count": int(annual["event_count"].sum()),
            "antecedent_complete_events": antecedent_total,
            "drawdown_complete_events": int(annual["drawdown_complete_events"].sum()),
            "recovery_risk_events": risk,
            "right_censored_events": censored,
            "right_censoring_rate": censor_rate,
            "event_years": event_years,
            "max_annual_antecedent_event_share": annual_max_share,
        }
        gates = {
            "pass_grids_ge_50": values["analysis_ready_grids"] >= 50,
            "pass_grid_years_ge_150": values["analysis_ready_grid_years"] >= 150,
            "pass_antecedent_events_ge_100": antecedent_total >= 100,
            "pass_event_years_ge_3": event_years >= 3,
            "pass_max_annual_share_le_0_5": bool(
                np.isfinite(annual_max_share) and annual_max_share <= 0.5
            ),
            "pass_right_censoring_le_0_3": bool(
                np.isfinite(censor_rate) and censor_rate <= 0.3
            ),
            "pass_drawdown_evidence": values["drawdown_complete_events"] > 0,
        }
        for gate, passed in gates.items():
            if not passed:
                stop_reasons.append(f"{zone}: {gate} failed")
        zones.append({**values, **gates, "pass_all": all(gates.values())})
    return by_year, pd.DataFrame(zones), stop_reasons


def write_csv(path: Path, rows: Iterable[dict[str, Any]] | pd.DataFrame) -> None:
    frame = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(list(rows))
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def hash_artifacts(paths: Iterable[Path], root: Path) -> list[dict[str, Any]]:
    artifacts = []
    for path in paths:
        digest = file_digest(path)
        artifacts.append(
            {
                "path": str(path.relative_to(root)).replace("\\", "/"),
                "bytes": digest["bytes"],
                "sha256": digest["sha256"],
            }
        )
    return artifacts


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite nonempty run directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    panel_path = args.panel.resolve()
    tmax_dir = args.tmax_dir.resolve()
    precip_dir = args.precip_dir.resolve()
    smrz_dir = args.smrz_dir.resolve()
    inputs = inventory_inputs(
        panel_path,
        tmax_dir=tmax_dir,
        precip_dir=precip_dir,
        smrz_dir=smrz_dir,
        cache_path=args.hash_cache.resolve() if args.hash_cache else None,
    )
    panel = pd.read_stata(panel_path, convert_categoricals=False)
    validate_panel_inventory(panel)
    panel["zone"] = panel["province"].map(zone_for_province)
    analysis_panel = select_smoke_panel(panel) if args.mode == "smoke" else panel

    records: list[dict[str, Any]] = []
    statuses: list[dict[str, Any]] = []
    coordinate_audit: list[dict[str, Any]] = []
    rng = np.random.default_rng(42)
    for year in YEARS:
        year_panel = analysis_panel[analysis_panel["year"] == year].copy()
        year_records, year_statuses = build_records_for_year(
            year_panel,
            year,
            tmax_dir=tmax_dir,
            precip_dir=precip_dir,
            smrz_dir=smrz_dir,
            coordinate_audit=coordinate_audit,
            rng=rng,
        )
        records.extend(year_records)
        statuses.extend(year_statuses)

    event_schema = json.loads(
        (PROJECT_ROOT / "docs/contracts/event_panel.schema.json").read_text(encoding="utf-8")
    )
    run_schema = json.loads(
        (PROJECT_ROOT / "docs/contracts/run_manifest.schema.json").read_text(encoding="utf-8")
    )
    validate_event_panel(records, event_schema)

    event_panel_path = output_dir / "event_panel.csv.gz"
    pd.DataFrame(records).to_csv(event_panel_path, index=False, compression="gzip", encoding="utf-8")
    status_path = output_dir / "grid_year_support.csv"
    write_csv(status_path, statuses)
    coordinate_path = output_dir / "coordinate_value_audit.csv"
    write_csv(coordinate_path, coordinate_audit)
    input_path = output_dir / "input_inventory.json"
    input_path.write_text(json.dumps(inputs, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.mode == "stage1":
        by_year, by_zone, stop_reasons = support_tables(pd.DataFrame(statuses))
    else:
        by_year = pd.DataFrame()
        by_zone = pd.DataFrame()
        stop_reasons = []
    by_year_path = output_dir / "support_by_zone_year.csv"
    by_zone_path = output_dir / "support_by_zone.csv"
    write_csv(by_year_path, by_year)
    write_csv(by_zone_path, by_zone)

    status = "STOP" if stop_reasons else "SMOKE"
    decision = {
        "stage": "interface_smoke" if args.mode == "smoke" else "stage1_support",
        "status": "STOP" if stop_reasons else ("PASS_SMOKE" if args.mode == "smoke" else "PASS_STAGE1"),
        "not_for_inference": True,
        "yield_model_run": False,
        "stop_reasons": stop_reasons,
        "record_count": len(records),
        "grid_year_status_count": len(statuses),
    }
    decision_path = output_dir / "stage_decision.json"
    decision_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")

    artifact_paths = [
        event_panel_path,
        status_path,
        coordinate_path,
        input_path,
        by_year_path,
        by_zone_path,
        decision_path,
    ]
    completed_artifacts = hash_artifacts(artifact_paths, output_dir)
    extension = {
        "contract_version": "compound-event-run-extension-v1",
        "stage": decision["stage"],
        "failure_stage": decision["stage"] if stop_reasons else None,
        "failure_reasons": stop_reasons,
        "completed_artifacts": completed_artifacts,
        "yield_model_run": False,
    }
    extension_path = output_dir / "event_run_extension.json"
    extension_path.write_text(json.dumps(extension, ensure_ascii=False, indent=2), encoding="utf-8")

    git_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True
    ).strip()
    ready_panel = pd.DataFrame(statuses)
    ready_keys = ready_panel[ready_panel["analysis_ready"]][["grid_id", "year"]].copy()
    manifest = {
        "contract_version": "run-manifest-v1",
        "canonical_id": "compound-event-intensity-duration-v1",
        "run_id": output_dir.name,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": status,
        "not_for_inference": True,
        "design_version": "v2",
        "git_commit": git_commit,
        "data_family": "V3",
        "inputs": inputs,
        "sample_predicate": (
            "deterministic first two grid_ids per named zone-year; interface only"
            if args.mode == "smoke"
            else "weather window 100% complete and all frozen yield-model fields complete-case"
        ),
        "sample_key_serialization": "sort(grid_id string,year); UTF-8 grid_id|YYYY\\n",
        "sample_key_sha256": sample_key_sha256(ready_keys),
        "sample_counts": {
            "source_rows": int(len(panel)),
            "selected_grid_years": int(len(statuses)),
            "analysis_ready_grid_years": int(ready_panel["analysis_ready"].sum()),
            "event_panel_rows": int(len(records)),
        },
        "outcome": "ln_yield (not estimated in smoke or Stage 1)",
        "exposure_definition": "Tmax>=32C and precipitation<1mm/day for >=3 consecutive days inside v3_doy-30..ma_doy",
        "soil_moisture_roles": ["antecedent SMrz", "drawdown SMrz", "recovery/censoring"],
        "fixed_effects": ["grid FE (preregistered; not estimated)", "province-year FE (preregistered; not estimated)"],
        "inference": {
            "primary": "not run before Stage 1 and independent smoke review",
            "bootstrap_reps": 0,
            "spatial_block_degrees": 2,
            "spatial_hac_km": [100, 200, 300],
            "multiplicity": "not run",
        },
        "ca_quantiles": None,
        "exposure_endpoints": None,
        "seed": 42,
        "claims": [],
        "stop_rules_triggered": stop_reasons,
        "verification": [
            {"check": "event row and cross-record validators", "status": "PASS", "detail": f"{len(records)} rows"},
            {"check": "yield model not run", "status": "PASS", "detail": "Stage gate enforced"},
            {
                "check": "Stage 1 named-zone support gates",
                "status": "FAIL" if stop_reasons else ("SKIP" if args.mode == "smoke" else "PASS"),
                "detail": "; ".join(stop_reasons) if stop_reasons else None,
            },
        ],
    }
    validate_event_run_manifest(
        manifest,
        run_schema,
        extension=extension if status in {"STOP", "FAILED"} else None,
    )
    manifest_path = output_dir / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False))
    return 2 if stop_reasons else 0


if __name__ == "__main__":
    raise SystemExit(main())
