"""Small inference utilities for G185 v3."""

from __future__ import annotations

import numpy as np
import pandas as pd


def benjamini_hochberg(values: pd.Series) -> pd.Series:
    p = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float)
    out = np.full(len(p), np.nan)
    valid = np.isfinite(p)
    if not valid.any():
        return pd.Series(out, index=values.index)
    idx = np.where(valid)[0]
    order = idx[np.argsort(p[idx])]
    ranked = p[order]
    m = len(ranked)
    adj = ranked * m / np.arange(1, m + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    out[order] = np.minimum(adj, 1.0)
    return pd.Series(out, index=values.index)

