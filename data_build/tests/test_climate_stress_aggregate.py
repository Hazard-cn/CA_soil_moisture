from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "python"
sys.path.insert(0, str(SCRIPT_DIR))

from climate_stress.aggregate import aggregate_temperature_windows  # noqa: E402
from climate_stress.era5 import EPOCH, save_daily_cache  # noqa: E402


def test_temperature_window_and_full_event_bridge(tmp_path: Path) -> None:
    year = 2019
    dates = np.arange(
        np.datetime64("2019-01-01", "D"),
        np.datetime64("2020-01-01", "D"),
        np.timedelta64(1, "D"),
    )
    n_days = len(dates)
    tmax = np.full((n_days, 1), 20.0, dtype=np.float32)
    tmax[9:12, 0] = [31, 32, 33]
    arrays = {
        "era5u8_tmean_c": np.full((n_days, 1), 15.0, dtype=np.float32),
        "era5u8_tmax_c": tmax,
        "era5u8_tmin_c": np.full((n_days, 1), 10.0, dtype=np.float32),
        "era5u8_hour_count": np.full((n_days, 1), 24, dtype=np.uint8),
    }
    for name in (
        "era5u8_gdd_b8_u29",
        "era5u8_gdd_b8_u30",
        "era5u8_gdd_b10_u29",
        "era5u8_gdd_b10_u30",
        "era5u8_edd_t29",
        "era5u8_edd_t30",
        "era5u8_edd_t32",
        "era5u8_edd_t34",
        "era5u8_edd_t35",
    ):
        arrays[name] = np.ones((n_days, 1), dtype=np.float32)
    daily_root = tmp_path / "daily"
    save_daily_cache(
        daily_root,
        year,
        (dates - EPOCH).astype(np.int32),
        arrays,
        {"year": year},
    )
    threshold_root = tmp_path / "threshold"
    threshold_root.mkdir()
    np.save(threshold_root / "era5u8_tmax_p90_calendar.npy", np.full((366, 1), 30.0))
    np.save(threshold_root / "era5u8_tmin_p90_calendar.npy", np.full((366, 1), 9.0))
    panel = pd.DataFrame(
        {
            "era01_cell_id": [1],
            "grid_id_v3": [100],
            "lat_idx": [0],
            "lon_idx": [0],
            "latitude": [53.53],
            "longitude": [73.58],
            "lat10": [535],
            "lon10": [736],
            "year": [year],
            "win_full_start": [1],
            "win_full_end": [20],
            "win_full_days": [20],
        }
    )
    long, events, bridges = aggregate_temperature_windows(
        panel,
        daily_root,
        threshold_root,
        years=[year],
        windows=["full"],
        cell_block_size=1,
    )
    assert len(long) == 1
    row = long.iloc[0]
    assert row["era5u8_coverage"] == 1
    assert row["era5u8_tx90p_days"] == 3
    assert row["era5u8_hot_day_night_days"] == 3
    assert row["era5u8_hw_p90_any"] == 1
    assert row["era5u8_hw_p90_count"] == 1
    assert row["era5u8_hw_p90_total_duration_days"] == 3
    assert row["era5u8_hw_p90_cumulative_heat_cdays"] == 6
    assert len(events) == 1
    assert len(bridges) == 1
    assert events.iloc[0]["event_id"] == bridges.iloc[0]["event_id"]
    assert events.iloc[0]["severity"] == 6
    assert bridges.iloc[0]["severity"] == 6
    for frame in (events, bridges):
        severity_rows = frame["severity"].notna()
        assert frame.loc[severity_rows, "severity_measure"].notna().all()
        assert frame.loc[severity_rows, "severity_unit"].notna().all()
        assert (
            frame.loc[severity_rows, "severity_measure"]
            == "tmax_excess_above_calendar_p90"
        ).all()
        assert (
            frame.loc[severity_rows, "severity_unit"] == "degree-Celsius-day"
        ).all()

    tmax_threshold = np.full((366, 1), 30.0)
    tmax_threshold[:3, 0] = np.nan
    np.save(threshold_root / "era5u8_tmax_p90_calendar.npy", tmax_threshold)
    gated, gated_events, gated_bridges = aggregate_temperature_windows(
        panel,
        daily_root,
        threshold_root,
        years=[year],
        windows=["full"],
        cell_block_size=1,
    )
    gated_row = gated.iloc[0]
    assert gated_row["era5u8_coverage"] == 1
    assert gated_row["era5u8_tmax_coverage"] == 1
    assert gated_row["era5u8_tmax_mean_c"] == row["era5u8_tmax_mean_c"]
    assert gated_row["era5u8_tmax_p90_coverage"] == 0.85
    assert gated_row["era5u8_tx90p_coverage"] == 0.85
    assert np.isnan(gated_row["era5u8_tmax_p90_mean_c"])
    assert np.isnan(gated_row["era5u8_tx90p_days"])
    assert np.isnan(gated_row["era5u8_hw_p90_any"])
    assert len(gated_events) == 1
    assert gated_bridges.empty
