"""Risk-set construction and separation checks for the frozen recovery design."""

from __future__ import annotations

import numpy as np
import pandas as pd


def build_recovery_risk_set(events: pd.DataFrame) -> pd.DataFrame:
    required = {
        "recovery_days",
        "recovery_observed",
        "right_censored",
        "event_id",
    }
    missing = sorted(required - set(events.columns))
    if missing:
        raise ValueError(f"event records lack recovery fields: {missing}")
    if events[list(required - {"event_id"})].isna().any().any():
        raise ValueError("recovery risk-set input contains incomplete states")
    follow_time = events["recovery_days"].astype(int).to_numpy()
    if np.any((follow_time < 0) | (follow_time > 30)):
        raise ValueError("recovery_days must be in 0..30")
    lengths = follow_time + 1
    event_index = np.repeat(np.arange(len(events)), lengths)
    starts = np.repeat(np.cumsum(lengths) - lengths, lengths)
    follow_day = np.arange(int(lengths.sum())) - starts
    risk = events.iloc[event_index].reset_index(drop=True).copy()
    risk["follow_day"] = follow_day
    risk["recovered_now"] = (
        risk["recovery_observed"].astype(bool)
        & (risk["follow_day"] == risk["recovery_days"].astype(int))
    ).astype(int)
    risk["censored_now"] = (
        risk["right_censored"].astype(bool)
        & (risk["follow_day"] == risk["recovery_days"].astype(int))
    ).astype(int)
    if (risk["recovered_now"] + risk["censored_now"] > 1).any():
        raise ValueError("a risk row cannot recover and censor simultaneously")
    return risk


def separated_day_cells(risk: pd.DataFrame) -> list[dict[str, int | str]]:
    """Return day indicators that perfectly predict no/all censoring."""

    grouped = risk.groupby("follow_day", sort=True)["censored_now"].agg(["size", "sum"])
    values: list[dict[str, int | str]] = []
    for day, row in grouped.iterrows():
        total = int(row["size"])
        censored = int(row["sum"])
        if censored == 0 or censored == total:
            values.append(
                {
                    "follow_day": int(day),
                    "risk_rows": total,
                    "censored_rows": censored,
                    "separation_type": "zero-censor" if censored == 0 else "all-censor",
                }
            )
    return values
