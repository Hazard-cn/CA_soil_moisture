"""Core calculations for the regional-threshold daily-Tmax exposure design.

The functions in this module are deliberately independent of machine paths and
I/O.  They implement the frozen daily window semantics, exposure/soil-moisture
summaries, high-dimensional fixed-effect residualisation, and the five-zone
interaction designs used by ``regional-threshold-sr-override-v1``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
import statsmodels.api as sm


SEED = 42
ZONE_ORDER = ["NE", "HHH", "NW", "SH", "SW"]
ZONE_PROVINCES = {
    "NE": ["黑龙江省", "吉林省", "辽宁省", "内蒙古自治区"],
    "HHH": ["河南省", "山东省", "河北省", "安徽省", "江苏省"],
    "SW": ["四川省", "贵州省", "云南省", "广西壮族自治区", "重庆市"],
    "NW": ["甘肃省", "宁夏回族自治区", "新疆维吾尔自治区", "陕西省"],
    "SH": ["广东省", "福建省", "浙江省", "江西省", "海南省", "湖南省", "湖北省"],
}


@dataclass(frozen=True)
class WindowBounds:
    """Zero-based half-open window plus a stable public label."""

    start: int
    stop: int
    label: str

    @property
    def expected_days(self) -> int:
        return self.stop - self.start


def assign_zone(province: pd.Series) -> pd.Series:
    zone = pd.Series("Other", index=province.index, dtype="object")
    for name, provinces in ZONE_PROVINCES.items():
        zone.loc[province.isin(provinces)] = name
    return zone


def window_bounds(
    window: str, v3_doy: int, he_doy: int, ma_doy: int, days_in_year: int
) -> WindowBounds:
    """Return frozen DOY window semantics as zero-based half-open indices.

    ``full_ext`` is [V3-30, MA] (inclusive MA), ``v3he`` is [V3, HE),
    and ``hema`` is [HE, MA] (inclusive MA).  Thus the two phase windows do
    not overlap and their union is [V3, MA].
    """

    if not (1 <= v3_doy < he_doy < ma_doy <= days_in_year):
        raise ValueError(
            f"invalid phenology/order: V3={v3_doy}, HE={he_doy}, "
            f"MA={ma_doy}, days={days_in_year}"
        )
    if window == "full_ext":
        start_doy, stop_doy = max(1, v3_doy - 30), ma_doy + 1
        label = "expanded-v3-minus30-to-ma"
    elif window == "v3he":
        start_doy, stop_doy = v3_doy, he_doy
        label = "v3-to-he"
    elif window == "hema":
        start_doy, stop_doy = he_doy, ma_doy + 1
        label = "he-to-ma"
    else:
        raise KeyError(f"unknown window: {window}")
    start = start_doy - 1
    stop = min(stop_doy - 1, days_in_year)
    if start < 0 or stop <= start:
        raise ValueError(f"empty/out-of-range window: {window}, {start}:{stop}")
    return WindowBounds(start=start, stop=stop, label=label)


def containing_pixel_indices(
    longitude: np.ndarray,
    latitude: np.ndarray,
    *,
    west: float,
    north: float,
    resolution: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Map point coordinates to zero-based containing PixelIsArea indices."""

    cols = np.floor((np.asarray(longitude, dtype=float) - west) / resolution).astype(int)
    rows = np.floor((north - np.asarray(latitude, dtype=float)) / resolution).astype(int)
    return rows, cols


def daily_exposure(values: np.ndarray, threshold_c: float) -> dict[str, float | int | bool]:
    """Calculate complete-window daily Tmax exposure metrics."""

    x = np.asarray(values, dtype=np.float64)
    valid = np.isfinite(x)
    complete = bool(valid.all() and x.size > 0 and np.isfinite(threshold_c))
    result: dict[str, float | int | bool] = {
        "expected_days": int(x.size),
        "valid_days": int(valid.sum()),
        "complete": complete,
        "hdd_cday_daily": np.nan,
        "exceedance_days_daily": np.nan,
    }
    if complete:
        result["hdd_cday_daily"] = float(np.maximum(x - threshold_c, 0.0).sum())
        result["exceedance_days_daily"] = int((x >= threshold_c).sum())
    return result


def soil_moisture_metrics(
    values: np.ndarray, bounds: WindowBounds, antecedent_days: int = 14
) -> dict[str, float | int | bool]:
    """Summarise antecedent and in-window SM without causal language."""

    x = np.asarray(values, dtype=np.float64)
    ant_start = max(0, bounds.start - antecedent_days)
    antecedent = x[ant_start : bounds.start]
    current = x[bounds.start : bounds.stop]
    ant_complete = bool(
        antecedent.size == antecedent_days
        and antecedent.size > 0
        and np.isfinite(antecedent).all()
    )
    win_complete = bool(current.size == bounds.expected_days and np.isfinite(current).all())
    result: dict[str, float | int | bool] = {
        "antecedent_expected_days": antecedent_days,
        "antecedent_valid_days": int(np.isfinite(antecedent).sum()),
        "window_valid_days": int(np.isfinite(current).sum()),
        "complete": ant_complete and win_complete,
        "antecedent_mean": np.nan,
        "window_mean": np.nan,
        "window_min": np.nan,
        "mean_change": np.nan,
        "min_drawdown": np.nan,
    }
    if ant_complete and win_complete:
        ant_mean = float(antecedent.mean())
        win_mean = float(current.mean())
        win_min = float(current.min())
        result.update(
            {
                "antecedent_mean": ant_mean,
                "window_mean": win_mean,
                "window_min": win_min,
                "mean_change": win_mean - ant_mean,
                "min_drawdown": win_min - ant_mean,
            }
        )
    return result


def _group_codes(values: Iterable[object]) -> tuple[np.ndarray, int]:
    codes, uniques = pd.factorize(values, sort=True)
    if (codes < 0).any():
        raise ValueError("fixed-effect group contains missing values")
    return codes.astype(np.int64), len(uniques)


def _subtract_group_means(values: np.ndarray, codes: np.ndarray, n_groups: int) -> None:
    counts = np.bincount(codes, minlength=n_groups).astype(np.float64)
    for col in range(values.shape[1]):
        sums = np.bincount(codes, weights=values[:, col], minlength=n_groups)
        values[:, col] -= (sums / counts)[codes]


def two_way_residualize(
    values: np.ndarray,
    first_group: Iterable[object],
    second_group: Iterable[object],
    *,
    tolerance: float = 1e-10,
    max_iter: int = 1_000,
) -> tuple[np.ndarray, int, float]:
    """Residualise columns against two additive fixed-effect families."""

    residual = np.asarray(values, dtype=np.float64).copy()
    first_codes, first_n = _group_codes(first_group)
    second_codes, second_n = _group_codes(second_group)
    if residual.ndim != 2 or residual.shape[0] != first_codes.size:
        raise ValueError("values and fixed-effect groups have incompatible shapes")
    last_delta = np.inf
    for iteration in range(1, max_iter + 1):
        previous = residual.copy()
        _subtract_group_means(residual, first_codes, first_n)
        _subtract_group_means(residual, second_codes, second_n)
        last_delta = float(np.max(np.abs(residual - previous)))
        if last_delta < tolerance:
            return residual, iteration, last_delta
    raise RuntimeError(
        f"two-way FE residualisation did not converge in {max_iter} iterations; "
        f"last delta={last_delta}"
    )


def build_two_way_design(
    frame: pd.DataFrame, exposure: str
) -> tuple[pd.DataFrame, dict[str, float], dict[str, dict[str, float]]]:
    """Build the frozen five-zone CA-by-exposure design in original units."""

    ca_raw = frame["ca"].quantile([0.25, 0.50, 0.75]).to_dict()
    ca_points = {"p25": float(ca_raw[0.25]), "p50": float(ca_raw[0.50]), "p75": float(ca_raw[0.75])}
    endpoints: dict[str, dict[str, float]] = {}
    design: dict[str, np.ndarray] = {}
    for zone in ZONE_ORDER:
        mask = frame["zone"].eq(zone).to_numpy(dtype=np.float64)
        zone_values = frame.loc[frame["zone"].eq(zone), exposure]
        quantiles = zone_values.quantile([0.50, 0.90]).to_dict()
        endpoints[zone] = {"p50": float(quantiles[0.50]), "p90": float(quantiles[0.90])}
        e_center = frame[exposure].to_numpy(dtype=np.float64) - endpoints[zone]["p50"]
        ca_center = frame["ca"].to_numpy(dtype=np.float64) - ca_points["p50"]
        design[f"{zone}_exposure"] = mask * e_center
        design[f"{zone}_ca"] = mask * ca_center
        design[f"{zone}_ca_exposure"] = mask * ca_center * e_center
    gdd = frame["gdd_10_29"].to_numpy(dtype=np.float64)
    precip = frame["pr_sum"].to_numpy(dtype=np.float64)
    design["gdd_10_29_per100"] = (gdd - np.mean(gdd)) / 100.0
    design["pr_sum_per100"] = (precip - np.mean(precip)) / 100.0
    design["pr_sum_sq_per10000"] = (precip**2 - np.mean(precip**2)) / 10_000.0
    return pd.DataFrame(design, index=frame.index), ca_points, endpoints


def build_three_way_state_design(
    frame: pd.DataFrame, exposure: str, state: str
) -> tuple[pd.DataFrame, dict[str, float], dict[str, dict[str, float]]]:
    """Build zone-specific complete low-order CA-by-exposure-by-SM terms."""

    two_way, ca_points, endpoints = build_two_way_design(frame, exposure)
    controls = two_way[["gdd_10_29_per100", "pr_sum_per100", "pr_sum_sq_per10000"]]
    design: dict[str, np.ndarray] = {}
    state_points: dict[str, dict[str, float]] = {}
    for zone in ZONE_ORDER:
        mask_bool = frame["zone"].eq(zone)
        mask = mask_bool.to_numpy(dtype=np.float64)
        q = frame.loc[mask_bool, state].quantile([0.25, 0.50, 0.75]).to_dict()
        state_points[zone] = {"p25": float(q[0.25]), "p50": float(q[0.50]), "p75": float(q[0.75])}
        e = frame[exposure].to_numpy(dtype=np.float64) - endpoints[zone]["p50"]
        c = frame["ca"].to_numpy(dtype=np.float64) - ca_points["p50"]
        s = frame[state].to_numpy(dtype=np.float64) - state_points[zone]["p50"]
        design[f"{zone}_exposure"] = mask * e
        design[f"{zone}_ca"] = mask * c
        design[f"{zone}_state"] = mask * s
        design[f"{zone}_ca_exposure"] = mask * c * e
        design[f"{zone}_ca_state"] = mask * c * s
        design[f"{zone}_exposure_state"] = mask * e * s
        design[f"{zone}_ca_exposure_state"] = mask * c * e * s
    result = pd.DataFrame(design, index=frame.index)
    explicit_endpoints = {
        zone: {
            "exposure_p50_cday": endpoints[zone]["p50"],
            "exposure_p90_cday": endpoints[zone]["p90"],
            "state_p25_m3m3": state_points[zone]["p25"],
            "state_p50_m3m3": state_points[zone]["p50"],
            "state_p75_m3m3": state_points[zone]["p75"],
        }
        for zone in ZONE_ORDER
    }
    return pd.concat([result, controls], axis=1), ca_points, explicit_endpoints


def fit_two_way_fe_cluster(
    frame: pd.DataFrame,
    outcome: str,
    design: pd.DataFrame,
) -> tuple[sm.regression.linear_model.RegressionResultsWrapper, dict[str, float | int]]:
    """Fit OLS after grid and province-year FE removal, clustered by grid."""

    y = frame[outcome].to_numpy(dtype=np.float64)
    x = design.to_numpy(dtype=np.float64)
    if not np.isfinite(y).all() or not np.isfinite(x).all():
        raise ValueError("model inputs contain non-finite values")
    stacked, iterations, delta = two_way_residualize(
        np.column_stack([y, x]),
        frame["grid_id"],
        frame["province"].astype(str) + "::" + frame["year"].astype(str),
    )
    y_within, x_within = stacked[:, 0], stacked[:, 1:]
    variances = np.var(x_within, axis=0)
    if (variances <= 1e-16).any():
        bad = design.columns[variances <= 1e-16].tolist()
        raise np.linalg.LinAlgError(f"within-design zero-variance columns: {bad}")
    rank = int(np.linalg.matrix_rank(x_within))
    if rank != x_within.shape[1]:
        raise np.linalg.LinAlgError(f"within-design rank deficient: {rank}/{x_within.shape[1]}")
    fit = sm.OLS(y_within, x_within).fit(
        cov_type="cluster",
        cov_kwds={"groups": frame["grid_id"].to_numpy(), "use_correction": True},
        use_t=True,
    )
    fit.model.data.xnames = design.columns.tolist()
    diagnostics: dict[str, float | int] = {
        "nobs": int(fit.nobs),
        "n_grids": int(frame["grid_id"].nunique()),
        "n_province_year": int((frame["province"].astype(str) + "::" + frame["year"].astype(str)).nunique()),
        "rank": rank,
        "columns": int(x_within.shape[1]),
        "fe_iterations": iterations,
        "fe_last_delta": delta,
        "condition_number": float(np.linalg.cond(x_within)),
    }
    return fit, diagnostics


def standardized_within_collinearity(
    frame: pd.DataFrame, design: pd.DataFrame
) -> tuple[pd.DataFrame, dict[str, float | int]]:
    """Return standardized within-design VIFs and condition diagnostics."""

    within, iterations, delta = two_way_residualize(
        design.to_numpy(dtype=float),
        frame["grid_id"],
        frame["province"].astype(str) + "::" + frame["year"].astype(str),
    )
    sd = within.std(axis=0, ddof=0)
    if (sd <= 1e-12).any():
        raise np.linalg.LinAlgError(
            f"zero-variance standardized columns: {design.columns[sd <= 1e-12].tolist()}"
        )
    standardized = within / sd
    correlation = np.corrcoef(standardized, rowvar=False)
    inverse = np.linalg.inv(correlation)
    vif = np.diag(inverse)
    eigenvalues = np.linalg.eigvalsh(correlation)
    condition_index = np.sqrt(float(eigenvalues.max()) / np.maximum(eigenvalues, 1e-15))
    table = pd.DataFrame(
        {
            "term": design.columns,
            "within_sd": sd,
            "vif": vif,
        }
    ).sort_values("vif", ascending=False, kind="stable")
    diagnostics: dict[str, float | int] = {
        "fe_iterations": iterations,
        "fe_last_delta": delta,
        "standardized_condition_number": float(np.linalg.cond(standardized)),
        "max_condition_index": float(condition_index.max()),
        "min_correlation_eigenvalue": float(eigenvalues.min()),
        "max_vif": float(vif.max()),
    }
    return table, diagnostics


def coefficient_table(
    fit: sm.regression.linear_model.RegressionResultsWrapper,
    names: list[str],
) -> pd.DataFrame:
    params = pd.Series(np.asarray(fit.params), index=fit.model.data.xnames)
    bse = pd.Series(np.asarray(fit.bse), index=fit.model.data.xnames)
    pvalues = pd.Series(np.asarray(fit.pvalues), index=fit.model.data.xnames)
    conf = np.asarray(fit.conf_int(alpha=0.05))
    rows = []
    for name in names:
        rows.append(
            {
                "term": name,
                "estimate": float(params[name]),
                "se_cluster_grid": float(bse[name]),
                "p_cluster_grid": float(pvalues[name]),
                "ci_low": float(conf[fit.model.data.xnames.index(name), 0]),
                "ci_high": float(conf[fit.model.data.xnames.index(name), 1]),
            }
        )
    return pd.DataFrame(rows)
