"""
Bootstrap selected parallel-rule variants from the 69,038-row search.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd
from scipy.stats import norm


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
SEARCH_SCRIPT = PROJ / "scripts/python/ggcp10_parallel_rules_69038_search.py"
RUN_DIR = PROJ / "temp/2026-06-02_parallel_rules_69038_story_search"


def load_search_module():
    spec = importlib.util.spec_from_file_location("parallel_search", SEARCH_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["parallel_search"] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def residualize_two_way(z: np.ndarray, gid: np.ndarray, year: np.ndarray, max_iter: int = 24) -> np.ndarray:
    r = z.astype(np.float64, copy=True)
    n_gid = int(gid.max()) + 1
    n_year = int(year.max()) + 1
    gid_count = np.bincount(gid, minlength=n_gid).astype(np.float64)
    year_count = np.bincount(year, minlength=n_year).astype(np.float64)
    previous = np.inf
    for _ in range(max_iter):
        gid_sum = np.vstack([np.bincount(gid, weights=r[:, j], minlength=n_gid) for j in range(r.shape[1])]).T
        r -= gid_sum[gid] / gid_count[gid, None]
        year_sum = np.vstack([np.bincount(year, weights=r[:, j], minlength=n_year) for j in range(r.shape[1])]).T
        r -= year_sum[year] / year_count[year, None]
        current = float(np.max(np.abs(year_sum)))
        if current < 1e-10 or abs(previous - current) < 1e-12:
            break
        previous = current
    return r


def ols_fe_coef(df: pd.DataFrame, yvar: str, xvars: list[str], gid_var: str = "grid_code") -> dict[str, float]:
    cols = [yvar, *xvars, gid_var, "year_code"]
    work = df.loc[:, cols].dropna()
    z = work[[yvar, *xvars]].to_numpy(dtype=np.float64)
    gid = work[gid_var].to_numpy(dtype=np.int64)
    year = work["year_code"].to_numpy(dtype=np.int64)
    zr = residualize_two_way(z, gid, year)
    beta = np.linalg.lstsq(zr[:, 1:], zr[:, 0], rcond=None)[0]
    return {x: float(beta[i]) for i, x in enumerate(xvars)}


def effects(coef_m, coef_y, main, inter, mediator, ca_values):
    a1 = coef_m[main]
    a3 = coef_m[inter]
    b = coef_y[mediator]
    c1 = coef_y[main]
    c3 = coef_y[inter]
    out = {}
    for level, ca in ca_values.items():
        ie = (a1 + a3 * ca) * b
        de = c1 + c3 * ca
        out[("IE", level)] = ie
        out[("DE", level)] = de
        out[("TE", level)] = ie + de
    return out


def bc_interval(samples: np.ndarray, point: float) -> tuple[float, float, float]:
    samples = samples[np.isfinite(samples)]
    se = float(np.std(samples, ddof=1))
    prop = float(np.mean(samples < point))
    prop = min(max(prop, 1.0 / (2 * len(samples))), 1 - 1.0 / (2 * len(samples)))
    z0 = norm.ppf(prop)
    lo_pct = 100 * norm.cdf(2 * z0 + norm.ppf(0.025))
    hi_pct = 100 * norm.cdf(2 * z0 + norm.ppf(0.975))
    lo, hi = np.percentile(samples, [lo_pct, hi_pct])
    return se, float(lo), float(hi)


def bootstrap_one(mod, base: pd.DataFrame, sample_id: str, transform: str, mediator_tag: str, reps: int, rng: np.random.Generator) -> tuple[pd.DataFrame, pd.DataFrame]:
    spec = [s for s in mod.SPECS if s.hazard == "drought" and s.mediator_tag == mediator_tag][0]
    mediator = spec.mediator(transform)
    y, ca, rhs_m, rhs_y, main, inter = mod.rhs_for("drought", transform, mediator)
    needed = list(dict.fromkeys([y, ca, mediator, *rhs_m, *rhs_y, "grid_id", "grid_code", "year", "year_code", "maize_zone"]))
    model = base.loc[:, needed].dropna().copy()
    ca_values = {
        "P25": float(np.percentile(model[ca], 25)),
        "P50": float(np.percentile(model[ca], 50)),
        "P75": float(np.percentile(model[ca], 75)),
    }
    cm = ols_fe_coef(model, mediator, rhs_m)
    cy = ols_fe_coef(model, y, rhs_y)
    point = effects(cm, cy, main, inter, mediator, ca_values)

    grid_values = model["grid_id"].drop_duplicates().to_numpy()
    grid_pos = {int(g): i for i, g in enumerate(grid_values)}
    row_groups = [[] for _ in range(len(grid_values))]
    for pos, g in enumerate(model["grid_id"].to_numpy()):
        row_groups[grid_pos[int(g)]].append(pos)
    row_groups = [np.asarray(x, dtype=np.int64) for x in row_groups]

    draws = {key: [] for key in point}
    failures = 0
    for _ in range(reps):
        sampled = rng.integers(0, len(row_groups), size=len(row_groups), endpoint=False)
        pieces = [row_groups[i] for i in sampled]
        boot_idx = np.concatenate(pieces)
        boot = model.iloc[boot_idx].copy()
        boot["boot_grid"] = np.repeat(np.arange(len(sampled), dtype=np.int64), [len(row_groups[i]) for i in sampled])
        try:
            bm = ols_fe_coef(boot, mediator, rhs_m, gid_var="boot_grid")
            by = ols_fe_coef(boot, y, rhs_y, gid_var="boot_grid")
            vals = effects(bm, by, main, inter, mediator, ca_values)
            for key, val in vals.items():
                draws[key].append(val)
        except (np.linalg.LinAlgError, ValueError, FloatingPointError):
            failures += 1

    transform_label = "winsor_1_99" if transform == "w" else "raw"
    set_id = f"{sample_id}_{transform_label}_{spec.branch}_{spec.mediator_tag}_drought"
    rows = []
    for (effect, level), point_est in point.items():
        arr = np.asarray(draws[(effect, level)], dtype=np.float64)
        se, lo, hi = bc_interval(arr, point_est)
        rows.append(
            {
                "sample_id": sample_id,
                "set_id": set_id,
                "branch": spec.branch,
                "mediator_tag": spec.mediator_tag,
                "hazard": "drought",
                "transform": transform_label,
                "effect": effect,
                "ca_level": level,
                "point_est": point_est,
                "bs_se": se,
                "ci_lo": lo,
                "ci_hi": hi,
                "N_boot": len(arr),
                "N_model": len(model),
                "N_grids": len(grid_values),
                "failed_reps": failures,
            }
        )

    holdout_rows = []
    for holdout_type, values in [("year", sorted(model["year"].dropna().unique())), ("zone", ["NE", "HHH", "SW", "SH", "NW"])]:
        var = "year" if holdout_type == "year" else "maize_zone"
        for value in values:
            sub = model[model[var] != value].copy()
            if len(sub) < 500:
                continue
            ca50 = {"P50": float(np.percentile(sub[ca], 50))}
            hm = ols_fe_coef(sub, mediator, rhs_m)
            hy = ols_fe_coef(sub, y, rhs_y)
            vals = effects(hm, hy, main, inter, mediator, ca50)
            for effect in ("IE", "DE", "TE"):
                holdout_rows.append(
                    {
                        "sample_id": sample_id,
                        "set_id": set_id,
                        "holdout_type": holdout_type,
                        "held_out": str(value),
                        "effect": effect,
                        "ca_level": "P50",
                        "estimate": vals[(effect, "P50")],
                        "N_model": len(sub),
                    }
                )
    return pd.DataFrame(rows), pd.DataFrame(holdout_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-id", default="V0001")
    parser.add_argument("--reps", type=int, default=500)
    parser.add_argument("--seed", type=int, default=45000)
    parser.add_argument("--transforms", default="raw,w")
    parser.add_argument("--mediator-tags", default="mean_root,dry_mdf_p10_sfc")
    args = parser.parse_args()

    start = time.time()
    mod = load_search_module()
    variants = pd.read_csv(RUN_DIR / "parallel_rule_variant_index.csv")
    row = variants.loc[variants["sample_id"].eq(args.sample_id)].iloc[0]
    flags = {k: bool(row[f"rule_{k}"]) for k in mod.RULES}
    panel = mod.load_panel()
    mask = mod.initial_mask(panel, flags)
    base = panel.loc[mask].copy()
    rng = np.random.default_rng(args.seed)
    boot_parts = []
    hold_parts = []
    for transform in [x.strip() for x in args.transforms.split(",") if x.strip()]:
        for mediator_tag in [x.strip() for x in args.mediator_tags.split(",") if x.strip()]:
            print(f"[BOOT] sample={args.sample_id} transform={transform} mediator={mediator_tag} reps={args.reps}", flush=True)
            t0 = time.time()
            boot, hold = bootstrap_one(mod, base, args.sample_id, transform, mediator_tag, args.reps, rng)
            boot_parts.append(boot)
            hold_parts.append(hold)
            pd.concat(boot_parts, ignore_index=True).to_csv(RUN_DIR / f"parallel_rule_bootstrap_{args.sample_id}.csv", index=False)
            pd.concat(hold_parts, ignore_index=True).to_csv(RUN_DIR / f"parallel_rule_holdout_{args.sample_id}.csv", index=False)
            print(f"[BOOT-DONE] seconds={time.time()-t0:.1f} N={int(boot.N_model.iloc[0])} failed={int(boot.failed_reps.max())}", flush=True)
    print(f"[COMPLETE] seconds={time.time()-start:.1f}", flush=True)


if __name__ == "__main__":
    main()
