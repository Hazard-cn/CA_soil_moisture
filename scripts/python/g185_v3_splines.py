"""Restricted cubic spline helpers for G185 v3."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RcsSpec:
    var: str
    basis_id: str
    raw_positive_median: float
    raw_positive_iqr: float
    raw_knots: tuple[float, ...]
    std_knots: tuple[float, ...]
    column_names: tuple[str, ...]


def _positive_distribution(values: pd.Series) -> np.ndarray:
    arr = pd.Series(values).dropna().to_numpy(dtype=float)
    arr = arr[arr > 0]
    if arr.size < 10:
        raise ValueError("positive exposure distribution has fewer than 10 observations")
    return arr


def make_rcs_spec(values: pd.Series, var: str, basis_id: str, quantiles: tuple[float, ...]) -> RcsSpec:
    positive = _positive_distribution(values)
    median = float(np.percentile(positive, 50))
    q25, q75 = np.percentile(positive, [25, 75])
    iqr = float(q75 - q25)
    if not np.isfinite(iqr) or iqr <= 0:
        raise ValueError(f"{var}: positive exposure IQR is zero")
    raw_knots = tuple(float(x) for x in np.percentile(positive, quantiles))
    if len(set(round(k, 12) for k in raw_knots)) != len(raw_knots):
        raise ValueError(f"{var}: duplicated spline knots")
    std_knots = tuple(float((k - median) / iqr) for k in raw_knots)
    ncols = len(raw_knots) - 1
    prefix = "D" if var.startswith("D_") else "H" if var.startswith("hdd") else "HD"
    names = tuple([f"{prefix}_rcs1", *[f"{prefix}_rcs{i}" for i in range(2, ncols + 1)]])
    return RcsSpec(
        var=var,
        basis_id=basis_id,
        raw_positive_median=median,
        raw_positive_iqr=iqr,
        raw_knots=raw_knots,
        std_knots=std_knots,
        column_names=names,
    )


def _truncated_cube(x: np.ndarray, knot: float) -> np.ndarray:
    return np.maximum(x - knot, 0.0) ** 3


def rcs_basis(values: np.ndarray | pd.Series | float, spec: RcsSpec) -> pd.DataFrame:
    arr = np.asarray(values, dtype=float)
    scalar = arr.ndim == 0
    arr = np.atleast_1d(arr)
    x = (arr - spec.raw_positive_median) / spec.raw_positive_iqr
    knots = np.asarray(spec.std_knots, dtype=float)
    last = knots[-1]
    penult = knots[-2]
    denom = last - penult
    if denom <= 0:
        raise ValueError(f"{spec.var}: invalid knot order")
    cols = [x]
    scale = (last - knots[0]) ** 2
    if scale <= 0:
        scale = 1.0
    for j in range(len(knots) - 2):
        kj = knots[j]
        col = (
            _truncated_cube(x, kj)
            - _truncated_cube(x, penult) * ((last - kj) / denom)
            + _truncated_cube(x, last) * ((penult - kj) / denom)
        ) / scale
        cols.append(col)
    out = pd.DataFrame(np.column_stack(cols), columns=list(spec.column_names))
    if scalar:
        return out.iloc[[0]].reset_index(drop=True)
    return out


def surface_basis(D: np.ndarray | pd.Series | float, H: np.ndarray | pd.Series | float, d_spec: RcsSpec, h_spec: RcsSpec) -> pd.DataFrame:
    bd = rcs_basis(D, d_spec)
    bh = rcs_basis(H, h_spec)
    if len(bd) != len(bh):
        raise ValueError("D and H basis lengths differ")
    cols = [bd, bh]
    tensor = {}
    for d_name in bd.columns:
        for h_name in bh.columns:
            tensor[f"{d_name}_x_{h_name}"] = bd[d_name].to_numpy(dtype=float) * bh[h_name].to_numpy(dtype=float)
    cols.append(pd.DataFrame(tensor))
    return pd.concat(cols, axis=1)


def write_basis_spec(path: Path, specs: dict[str, RcsSpec], extra: dict[str, object]) -> None:
    payload = {
        "basis": {
            key: {
                "var": spec.var,
                "basis_id": spec.basis_id,
                "raw_positive_median": spec.raw_positive_median,
                "raw_positive_iqr": spec.raw_positive_iqr,
                "raw_knots": list(spec.raw_knots),
                "std_knots": list(spec.std_knots),
                "column_names": list(spec.column_names),
                "formula": "restricted cubic spline with linear tails; columns are linear standardized x plus Harrell-style nonlinear terms",
            }
            for key, spec in specs.items()
        },
        **extra,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

