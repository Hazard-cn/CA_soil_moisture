"""Frozen recovery-v2 risk, weight, and standardization utilities."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from patsy import build_design_matrices

from hotdry_event_override_recovery import build_recovery_risk_set


EARLY_CENSOR_REASONS = {"next-event", "ma-end", "data-end"}


def build_recovery_v2_risk(events: pd.DataFrame) -> pd.DataFrame:
    """Create t=0..29 risk rows and distinguish early from administrative censoring."""

    risk = build_recovery_risk_set(events)
    risk = risk[risk["follow_day"] < 30].copy()
    risk["time"] = risk["follow_day"].astype(float) / 30.0
    risk["time_sq"] = np.square(risk["time"])
    risk["early_censor"] = (
        risk["censored_now"].astype(bool)
        & risk["censor_reason"].isin(EARLY_CENSOR_REASONS)
    ).astype(int)
    if (
        risk.loc[risk["censor_reason"] == "thirty-day-limit", "early_censor"] != 0
    ).any():
        raise ValueError("administrative day-30 censoring entered early-censor hazard")
    return risk


def stabilized_ipcw(
    risk: pd.DataFrame,
    numerator_censor_probability: np.ndarray,
    denominator_censor_probability: np.ndarray,
) -> tuple[np.ndarray, dict[str, float]]:
    """Calculate cumulative stabilized IPCW with frozen 1/99 truncation."""

    numerator = np.asarray(numerator_censor_probability, dtype=float)
    denominator = np.asarray(denominator_censor_probability, dtype=float)
    if numerator.shape != (len(risk),) or denominator.shape != (len(risk),):
        raise ValueError("censoring predictions do not match risk rows")
    if np.any(~np.isfinite(numerator)) or np.any(~np.isfinite(denominator)):
        raise ValueError("censoring predictions are not finite")
    if np.any((numerator <= 0) | (numerator >= 1)) or np.any(
        (denominator <= 0) | (denominator >= 1)
    ):
        raise ValueError("censoring probabilities must lie strictly inside (0,1)")
    daily_ratio = (1.0 - numerator) / (1.0 - denominator)
    raw = pd.Series(daily_ratio, index=risk.index).groupby(
        risk["event_id"], sort=False
    ).cumprod().to_numpy(dtype=float)
    lower, upper = np.quantile(raw, [0.01, 0.99])
    clipped = np.clip(raw, lower, upper)

    def ess(weights: np.ndarray) -> float:
        return float(np.square(weights.sum()) / np.square(weights).sum())

    diagnostics = {
        "lower_p01": float(lower),
        "upper_p99": float(upper),
        "raw_min": float(raw.min()),
        "raw_mean": float(raw.mean()),
        "raw_max": float(raw.max()),
        "raw_ess": ess(raw),
        "clipped_min": float(clipped.min()),
        "clipped_mean": float(clipped.mean()),
        "clipped_max": float(clipped.max()),
        "clipped_ess": ess(clipped),
    }
    return clipped, diagnostics


def standardized_survival(
    params: np.ndarray,
    design_info: Any,
    events: pd.DataFrame,
    ca_value: float,
    *,
    horizon: int = 30,
) -> tuple[np.ndarray, np.ndarray, float, np.ndarray]:
    """Event-equal survival curve, gradients, RMST30, and RMST gradient."""

    beta = np.asarray(params, dtype=float)
    survival_event = np.ones(len(events), dtype=float)
    cumulative_zx = np.zeros((len(events), beta.size), dtype=float)
    curve = np.empty(horizon, dtype=float)
    curve_gradient = np.empty((horizon, beta.size), dtype=float)
    base = events.copy()
    base["ca"] = float(ca_value)
    for day in range(horizon):
        base["follow_day"] = day
        base["time"] = day / 30.0
        base["time_sq"] = np.square(base["time"])
        x = np.asarray(build_design_matrices([design_info], base)[0], dtype=float)
        eta = x @ beta
        z = np.exp(np.clip(eta, -40.0, 40.0))
        survival_event *= np.exp(-z)
        cumulative_zx += z[:, None] * x
        curve[day] = float(survival_event.mean())
        curve_gradient[day] = np.mean(
            -survival_event[:, None] * cumulative_zx,
            axis=0,
        )
    return curve, curve_gradient, float(curve.sum()), curve_gradient.sum(axis=0)
