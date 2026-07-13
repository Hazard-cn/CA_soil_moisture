"""
F4-B067 full coefficients, fast bootstrap IE/DE/TE, and scenario contrasts.

The default bootstrap is a cluster wild score approximation after one
two-way-FE residualization per equation. It is designed for the frozen B067
sample, not for a new specification search.
"""

from __future__ import annotations

import argparse
import math
import time
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

from bio_window_filter_128 import unique_variants
from ggcp10_parallel_rules_69038_search import load_panel, residualize_two_way, rhs_for


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
OUT_DIR = PROJ / "temp/2026-06-04_f4_b067_full_bootstrap_counterfactual"
FIG_DIR = OUT_DIR / "figures"
REPORT_MD = PROJ / "quality_reports/2026-06-04_f4_b067_full_bootstrap_counterfactual.md"

SAMPLE_ID = "B067"
MIN_N = 500
SEED = 420604

HAZARDS = ("drought", "heat", "hotdry")
TRANSFORMS = ("raw", "w")
MEDIATORS = {
    "mean": ("mean", "gleam_smrz_mean"),
    "dry_state_top3": ("dry", "v6mdf_p10_fn_gss"),
}
KEY_ROLES = {"a1", "a3", "b", "c1", "c3"}


@dataclass(frozen=True)
class Spec:
    hazard: str
    transform: str
    mediator_tag: str
    branch: str
    mediator_base: str

    @property
    def transform_label(self) -> str:
        return "winsor_1_99" if self.transform == "w" else "raw"

    @property
    def mediator(self) -> str:
        return f"{self.mediator_base}_{self.transform}"

    @property
    def spec_id(self) -> str:
        return f"{self.hazard}_{self.transform_label}_{self.mediator_tag}"


@dataclass
class FitResult:
    yvar: str
    xvars: list[str]
    beta: np.ndarray
    se: np.ndarray
    p: np.ndarray
    resid: np.ndarray
    xtx_inv: np.ndarray
    score_by_cluster: np.ndarray
    n_model: int
    n_grids: int
    r2_within: float

    def coef(self, term: str) -> float:
        return float(self.beta[self.xvars.index(term)])

    def se_for(self, term: str) -> float:
        return float(self.se[self.xvars.index(term)])

    def p_for(self, term: str) -> float:
        return float(self.p[self.xvars.index(term)])


def transform_label(transform: str) -> str:
    return "winsor_1_99" if transform == "w" else "raw"


def sign_value(x: float) -> str:
    if x > 0:
        return "positive"
    if x < 0:
        return "negative"
    return "zero"


def sign_sig_value(coef: float, p: float, alpha: float) -> str:
    sign = sign_value(coef)
    if sign == "zero":
        return "zero"
    return f"{sign}_{'sig' if p < alpha else 'ns'}"


def all_specs() -> list[Spec]:
    specs: list[Spec] = []
    for hazard in HAZARDS:
        for transform in TRANSFORMS:
            for mediator_tag, (branch, mediator_base) in MEDIATORS.items():
                specs.append(Spec(hazard, transform, mediator_tag, branch, mediator_base))
    return specs


def b067_sample(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    variants = unique_variants(df)
    variant = next(v for v in variants if v["sample_id"] == SAMPLE_ID)
    base = df.loc[variant["mask"]].copy()
    base["ai_pet_over_p_year"] = base["et0_sum"] / base["pr_sum"].replace(0, np.nan)
    grid_ai = (
        base.groupby("grid_id", as_index=False)["ai_pet_over_p_year"]
        .mean()
        .rename(columns={"ai_pet_over_p_year": "ai_pet_over_p_gridmean"})
    )
    base = base.merge(grid_ai, on="grid_id", how="left", validate="many_to_one")
    if int(base.groupby("grid_id")["ai_pet_over_p_gridmean"].nunique(dropna=False).max()) != 1:
        raise RuntimeError("ai_pet_over_p_gridmean is not grid-fixed")
    return base, {k: v for k, v in variant.items() if k != "mask"}


def subset_jobs(base: pd.DataFrame) -> list[tuple[str, str, str, pd.DataFrame, int]]:
    jobs: list[tuple[str, str, str, pd.DataFrame, int]] = []
    jobs.append(("baseline", "all", "all", base, 1000))
    for group in ("high_irr", "low_irr"):
        sub = base.loc[base["irr_group"].astype(str).eq(group)].copy()
        jobs.append(("heterogeneity", "irr_group", group, sub, 500))
    for group in ("HHH", "NE", "NW", "SH", "SW"):
        sub = base.loc[base["maize_zone"].astype(str).eq(group)].copy()
        jobs.append(("heterogeneity", "maize_zone", group, sub, 500))
    dry2 = base.loc[base["ai_pet_over_p_gridmean"].gt(2)].copy()
    for group in ("high_irr", "low_irr"):
        sub = dry2.loc[dry2["irr_group"].astype(str).eq(group)].copy()
        jobs.append(("ai_gt2_irrigation", "irr_group", group, sub, 500))
    dry5 = base.loc[base["ai_pet_over_p_gridmean"].gt(5)].copy()
    jobs.append(("ai_gt5_pooled", "all", "all", dry5, 1000))
    return jobs


def spec_roles(spec: Spec) -> tuple[str, str, list[str], list[str], str, str, dict[str, str], dict[str, str]]:
    y, ca, rhs_m, rhs_y, main, inter = rhs_for(spec.hazard, spec.transform, spec.mediator)
    role_m = {main: "a1", inter: "a3", ca: "sr_main_in_mediator"}
    role_y = {main: "c1", inter: "c3", ca: "sr_main_in_outcome", spec.mediator: "b"}
    return y, ca, rhs_m, rhs_y, main, inter, role_m, role_y


def prepare_model_frame(df: pd.DataFrame, spec: Spec) -> tuple[pd.DataFrame, dict[str, object]]:
    y, ca, rhs_m, rhs_y, main, inter, _role_m, _role_y = spec_roles(spec)
    needed = list(dict.fromkeys([y, ca, spec.mediator, *rhs_m, *rhs_y, "grid_id", "year"]))
    work = df.loc[:, needed].dropna().copy()
    if len(work) < MIN_N:
        raise ValueError("N_lt_500")
    work["cluster_code"] = pd.Categorical(work["grid_id"]).codes.astype(np.int64)
    work["year_code_local"] = pd.Categorical(work["year"]).codes.astype(np.int64)
    ca_values = {
        "P25": float(np.percentile(work[ca].to_numpy(dtype=np.float64), 25)),
        "P50": float(np.percentile(work[ca].to_numpy(dtype=np.float64), 50)),
        "P75": float(np.percentile(work[ca].to_numpy(dtype=np.float64), 75)),
    }
    hazard_values = {
        "P50": float(np.percentile(work[main].to_numpy(dtype=np.float64), 50)),
        "P90": float(np.percentile(work[main].to_numpy(dtype=np.float64), 90)),
    }
    meta = {
        "y": y,
        "ca": ca,
        "rhs_m": rhs_m,
        "rhs_y": rhs_y,
        "main": main,
        "inter": inter,
        "ca_values": ca_values,
        "hazard_values": hazard_values,
    }
    return work, meta


def fit_fe_from_frame(work: pd.DataFrame, yvar: str, xvars: list[str]) -> FitResult:
    z = work[[yvar, *xvars]].to_numpy(dtype=np.float64)
    gid = work["cluster_code"].to_numpy(dtype=np.int64)
    year = work["year_code_local"].to_numpy(dtype=np.int64)
    zr = residualize_two_way(z, gid, year)
    y = zr[:, 0]
    x = zr[:, 1:]
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    resid = y - x @ beta
    xtx_inv = np.linalg.pinv(x.T @ x)

    n = len(work)
    gcount = int(np.max(gid)) + 1
    k = x.shape[1]
    score = np.zeros((gcount, k), dtype=np.float64)
    for j in range(k):
        score[:, j] = np.bincount(gid, weights=x[:, j] * resid, minlength=gcount)
    meat = score.T @ score
    scale = (gcount / max(gcount - 1, 1)) * ((n - 1) / max(n - k, 1))
    cov = scale * xtx_inv @ meat @ xtx_inv
    se = np.sqrt(np.maximum(np.diag(cov), 0))
    zstat = np.divide(np.abs(beta), se, out=np.full_like(beta, np.inf), where=se > 0)
    p = 2 * (1 - norm.cdf(zstat))
    rss = float(resid @ resid)
    tss = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - rss / tss if tss > 0 else math.nan
    return FitResult(yvar, xvars, beta, se, p, resid, xtx_inv, score, n, gcount, r2)


def effects_from_arrays(
    beta_m: np.ndarray,
    xvars_m: list[str],
    beta_y: np.ndarray,
    xvars_y: list[str],
    main: str,
    inter: str,
    mediator: str,
    ca_values: dict[str, float],
) -> dict[tuple[str, str], float]:
    a1 = float(beta_m[xvars_m.index(main)])
    a3 = float(beta_m[xvars_m.index(inter)])
    b = float(beta_y[xvars_y.index(mediator)])
    c1 = float(beta_y[xvars_y.index(main)])
    c3 = float(beta_y[xvars_y.index(inter)])
    out: dict[tuple[str, str], float] = {}
    for level, r in ca_values.items():
        ie = (a1 + a3 * r) * b
        de = c1 + c3 * r
        out[("IE", level)] = float(ie)
        out[("DE", level)] = float(de)
        out[("TE", level)] = float(ie + de)
    return out


def percentile_ci(samples: np.ndarray) -> tuple[float, float, float]:
    samples = samples[np.isfinite(samples)]
    if samples.size < 2:
        return math.nan, math.nan, math.nan
    return (
        float(np.std(samples, ddof=1)),
        float(np.percentile(samples, 2.5)),
        float(np.percentile(samples, 97.5)),
    )


def score_bootstrap(
    fit_m: FitResult,
    fit_y: FitResult,
    spec: Spec,
    main: str,
    inter: str,
    ca_values: dict[str, float],
    reps: int,
    rng: np.random.Generator,
    batch_size: int = 250,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    point = effects_from_arrays(fit_m.beta, fit_m.xvars, fit_y.beta, fit_y.xvars, main, inter, spec.mediator, ca_values)
    path_terms = {
        "a1": (fit_m, main),
        "a3": (fit_m, inter),
        "b": (fit_y, spec.mediator),
        "c1": (fit_y, main),
        "c3": (fit_y, inter),
    }
    effect_draws: dict[tuple[str, str], list[float]] = {k: [] for k in point}
    path_draws: dict[str, list[float]] = {k: [] for k in path_terms}
    g = fit_m.score_by_cluster.shape[0]
    done = 0
    while done < reps:
        bsz = min(batch_size, reps - done)
        weights = rng.choice(np.array([-1.0, 1.0]), size=(bsz, g))
        delta_m = (weights @ fit_m.score_by_cluster) @ fit_m.xtx_inv.T
        delta_y = (weights @ fit_y.score_by_cluster) @ fit_y.xtx_inv.T
        bm = fit_m.beta[None, :] + delta_m
        by = fit_y.beta[None, :] + delta_y
        idx_a1 = fit_m.xvars.index(main)
        idx_a3 = fit_m.xvars.index(inter)
        idx_b = fit_y.xvars.index(spec.mediator)
        idx_c1 = fit_y.xvars.index(main)
        idx_c3 = fit_y.xvars.index(inter)
        path_draws["a1"].extend(bm[:, idx_a1].tolist())
        path_draws["a3"].extend(bm[:, idx_a3].tolist())
        path_draws["b"].extend(by[:, idx_b].tolist())
        path_draws["c1"].extend(by[:, idx_c1].tolist())
        path_draws["c3"].extend(by[:, idx_c3].tolist())
        for level, r in ca_values.items():
            ie = (bm[:, idx_a1] + bm[:, idx_a3] * r) * by[:, idx_b]
            de = by[:, idx_c1] + by[:, idx_c3] * r
            te = ie + de
            effect_draws[("IE", level)].extend(ie.tolist())
            effect_draws[("DE", level)].extend(de.tolist())
            effect_draws[("TE", level)].extend(te.tolist())
        done += bsz

    effect_summary_rows = []
    effect_draw_rows = []
    for (effect, level), point_est in point.items():
        arr = np.asarray(effect_draws[(effect, level)], dtype=np.float64)
        se, lo, hi = percentile_ci(arr)
        effect_summary_rows.append(
            {
                "effect": effect,
                "ca_level": level,
                "ca_value": ca_values[level],
                "point_est": point_est,
                "bs_se": se,
                "ci_lo_pct": lo,
                "ci_hi_pct": hi,
                "N_boot": int(arr.size),
            }
        )
        effect_draw_rows.extend({"draw": i + 1, "effect": effect, "ca_level": level, "value": float(v)} for i, v in enumerate(arr))

    path_summary_rows = []
    path_draw_rows = []
    for role, values in path_draws.items():
        arr = np.asarray(values, dtype=np.float64)
        fit, term = path_terms[role]
        point_est = fit.coef(term)
        se, lo, hi = percentile_ci(arr)
        path_summary_rows.append(
            {
                "role": role,
                "term": term,
                "point_est": point_est,
                "bs_se": se,
                "ci_lo_pct": lo,
                "ci_hi_pct": hi,
                "N_boot": int(arr.size),
            }
        )
        path_draw_rows.extend({"draw": i + 1, "role": role, "term": term, "value": float(v)} for i, v in enumerate(arr))
    return (
        pd.DataFrame(effect_summary_rows),
        pd.DataFrame(effect_draw_rows),
        pd.DataFrame(path_summary_rows),
        pd.DataFrame(path_draw_rows),
    )


def pairs_refit_check(
    work: pd.DataFrame,
    spec: Spec,
    rhs_m: list[str],
    rhs_y: list[str],
    main: str,
    inter: str,
    ca_values: dict[str, float],
    reps: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    clusters = np.arange(int(work["cluster_code"].max()) + 1, dtype=np.int64)
    row_groups = [np.flatnonzero(work["cluster_code"].to_numpy(dtype=np.int64) == g) for g in clusters]
    rows = []
    for draw in range(1, reps + 1):
        sampled = rng.integers(0, len(row_groups), size=len(row_groups), endpoint=False)
        counts = [len(row_groups[i]) for i in sampled]
        boot_idx = np.concatenate([row_groups[i] for i in sampled])
        boot = work.iloc[boot_idx].copy()
        boot["cluster_code"] = np.repeat(np.arange(len(sampled), dtype=np.int64), counts)
        boot["year_code_local"] = pd.Categorical(boot["year"]).codes.astype(np.int64)
        try:
            fm = fit_fe_from_frame(boot, spec.mediator, rhs_m)
            fy = fit_fe_from_frame(boot, next(col for col in work.columns if col.startswith("ln_yield_")), rhs_y)
            vals = effects_from_arrays(fm.beta, fm.xvars, fy.beta, fy.xvars, main, inter, spec.mediator, ca_values)
            for (effect, level), value in vals.items():
                rows.append({"draw": draw, "effect": effect, "ca_level": level, "value": value, "method": "pairs_cluster_refit"})
        except Exception as exc:  # noqa: BLE001
            rows.append({"draw": draw, "effect": "failed", "ca_level": "", "value": math.nan, "method": "pairs_cluster_refit", "reason": str(exc)})
    return pd.DataFrame(rows)


def coefficient_rows(
    spec: Spec,
    fit_m: FitResult,
    fit_y: FitResult,
    role_m: dict[str, str],
    role_y: dict[str, str],
    context: dict[str, object],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for equation, fit, role_map in (("mediator", fit_m, role_m), ("outcome", fit_y, role_y)):
        for i, term in enumerate(fit.xvars):
            coef = float(fit.beta[i])
            p = float(fit.p[i])
            rows.append(
                {
                    **context,
                    "hazard": spec.hazard,
                    "transform": spec.transform_label,
                    "branch": spec.branch,
                    "mediator_tag": spec.mediator_tag,
                    "mediator": spec.mediator,
                    "equation": equation,
                    "depvar": fit.yvar,
                    "term": term,
                    "role": role_map.get(term, "control_or_covariate"),
                    "coef": coef,
                    "se": float(fit.se[i]),
                    "p": p,
                    "sign": sign_value(coef),
                    "sig_005": bool(p < 0.05),
                    "sig_010": bool(p < 0.10),
                    "sign_sig_005": sign_sig_value(coef, p, 0.05),
                    "sign_sig_010": sign_sig_value(coef, p, 0.10),
                    "N_model": fit.n_model,
                    "N_grids": fit.n_grids,
                    "r2_within": fit.r2_within,
                }
            )
    return rows


def add_context(df: pd.DataFrame, context: dict[str, object], spec: Spec) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    for k, v in reversed(list(context.items())):
        out.insert(0, k, v)
    out.insert(len(context), "hazard", spec.hazard)
    out.insert(len(context) + 1, "transform", spec.transform_label)
    out.insert(len(context) + 2, "branch", spec.branch)
    out.insert(len(context) + 3, "mediator_tag", spec.mediator_tag)
    out.insert(len(context) + 4, "mediator", spec.mediator)
    return out


def counterfactual_rows(effect_draws: pd.DataFrame, effect_summary: pd.DataFrame, hazard_values: dict[str, float], context: dict[str, object], spec: Spec) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    te = effect_summary.loc[effect_summary["effect"].eq("TE")].set_index("ca_level")
    draw_te = effect_draws.loc[effect_draws["effect"].eq("TE")]
    wide = draw_te.pivot_table(index="draw", columns="ca_level", values="value", aggfunc="first")
    if not {"P25", "P75"}.issubset(te.index) or not {"P25", "P75"}.issubset(wide.columns):
        return rows
    point_delta_te = float(te.loc["P75", "point_est"] - te.loc["P25", "point_est"])
    draw_delta_te = wide["P75"].to_numpy(dtype=np.float64) - wide["P25"].to_numpy(dtype=np.float64)
    for scenario, hazard_level in hazard_values.items():
        draw_ln = draw_delta_te * hazard_level
        draw_pct = np.exp(draw_ln) - 1
        _se_ln, lo_ln, hi_ln = percentile_ci(draw_ln)
        se_pct, lo_pct, hi_pct = percentile_ci(draw_pct)
        point_ln = point_delta_te * hazard_level
        point_pct = math.exp(point_ln) - 1
        rows.append(
            {
                **context,
                "hazard": spec.hazard,
                "transform": spec.transform_label,
                "branch": spec.branch,
                "mediator_tag": spec.mediator_tag,
                "mediator": spec.mediator,
                "scenario": f"hazard_{scenario}_ca_P75_minus_P25",
                "hazard_level": hazard_level,
                "delta_te_point": point_delta_te,
                "delta_ln_yield_point": point_ln,
                "delta_ln_yield_ci_lo": lo_ln,
                "delta_ln_yield_ci_hi": hi_ln,
                "pct_delta_point": point_pct,
                "pct_delta_bs_se": se_pct,
                "pct_delta_ci_lo": lo_pct,
                "pct_delta_ci_hi": hi_pct,
                "N_boot": int(draw_pct.size),
            }
        )
    return rows


def write_parquet_or_csv(df: pd.DataFrame, parquet_path: Path) -> Path:
    try:
        df.to_parquet(parquet_path, index=False)
        return parquet_path
    except Exception:
        csv_path = parquet_path.with_suffix(".csv.gz")
        df.to_csv(csv_path, index=False, encoding="utf-8", compression="gzip")
        return csv_path


def plot_coefficients(coef: pd.DataFrame) -> list[Path]:
    paths: list[Path] = []
    if coef.empty:
        return paths
    plot_df = coef.copy()
    plot_df["lo"] = plot_df["coef"] - 1.96 * plot_df["se"]
    plot_df["hi"] = plot_df["coef"] + 1.96 * plot_df["se"]
    for (layer, subgroup_dim, subgroup), sub in plot_df.groupby(["layer", "subgroup_dim", "subgroup"], sort=False):
        for equation, eq in sub.groupby("equation", sort=False):
            eq = eq.sort_values(["hazard", "transform", "mediator_tag", "role", "term"]).copy()
            labels = eq["hazard"] + " | " + eq["transform"] + " | " + eq["mediator_tag"] + " | " + eq["role"] + " | " + eq["term"]
            height = max(6, min(24, 0.22 * len(eq) + 2))
            fig, ax = plt.subplots(figsize=(12, height))
            y = np.arange(len(eq))
            ax.errorbar(eq["coef"], y, xerr=[eq["coef"] - eq["lo"], eq["hi"] - eq["coef"]], fmt="o", markersize=3, linewidth=0.8)
            ax.axvline(0, color="black", linewidth=0.8)
            ax.set_yticks(y)
            ax.set_yticklabels(labels, fontsize=7)
            ax.set_title(f"{layer} / {subgroup_dim}={subgroup} / {equation}")
            ax.set_xlabel("Coefficient with model 95% CI")
            fig.tight_layout()
            path = FIG_DIR / f"coefficients_{layer}_{subgroup_dim}_{subgroup}_{equation}.png"
            fig.savefig(path, dpi=180)
            plt.close(fig)
            paths.append(path)
    return paths


def plot_effects(iede: pd.DataFrame, cf: pd.DataFrame, path_bs: pd.DataFrame, runtime: pd.DataFrame) -> list[Path]:
    paths: list[Path] = []
    if not iede.empty:
        for effect in ("IE", "DE", "TE"):
            sub = iede.loc[iede["effect"].eq(effect)].copy()
            sub = sub.sort_values(["layer", "subgroup_dim", "subgroup", "hazard", "transform", "mediator_tag", "ca_level"])
            labels = sub["layer"] + "/" + sub["subgroup"] + "/" + sub["hazard"] + "/" + sub["transform"] + "/" + sub["mediator_tag"] + "/" + sub["ca_level"]
            height = max(6, min(28, 0.18 * len(sub) + 2))
            fig, ax = plt.subplots(figsize=(12, height))
            y = np.arange(len(sub))
            ax.errorbar(sub["point_est"], y, xerr=[sub["point_est"] - sub["ci_lo_pct"], sub["ci_hi_pct"] - sub["point_est"]], fmt="o", markersize=3, linewidth=0.8)
            ax.axvline(0, color="black", linewidth=0.8)
            ax.set_yticks(y)
            ax.set_yticklabels(labels, fontsize=6)
            ax.set_title(f"{effect} bootstrap percentile CI")
            ax.set_xlabel("Effect")
            fig.tight_layout()
            path = FIG_DIR / f"bootstrap_{effect}.png"
            fig.savefig(path, dpi=180)
            plt.close(fig)
            paths.append(path)
    if not path_bs.empty:
        sub = path_bs.sort_values(["layer", "subgroup_dim", "subgroup", "hazard", "transform", "mediator_tag", "role"])
        labels = sub["layer"] + "/" + sub["subgroup"] + "/" + sub["hazard"] + "/" + sub["transform"] + "/" + sub["mediator_tag"] + "/" + sub["role"]
        fig, ax = plt.subplots(figsize=(12, max(6, min(28, 0.18 * len(sub) + 2))))
        y = np.arange(len(sub))
        ax.errorbar(sub["point_est"], y, xerr=[sub["point_est"] - sub["ci_lo_pct"], sub["ci_hi_pct"] - sub["point_est"]], fmt="o", markersize=3, linewidth=0.8)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=6)
        ax.set_title("Path coefficients score bootstrap percentile CI")
        ax.set_xlabel("Coefficient")
        fig.tight_layout()
        path = FIG_DIR / "bootstrap_path_coefficients.png"
        fig.savefig(path, dpi=180)
        plt.close(fig)
        paths.append(path)
    if not cf.empty:
        sub = cf.sort_values(["layer", "subgroup_dim", "subgroup", "hazard", "transform", "mediator_tag", "scenario"])
        labels = sub["layer"] + "/" + sub["subgroup"] + "/" + sub["hazard"] + "/" + sub["transform"] + "/" + sub["mediator_tag"] + "/" + sub["scenario"]
        fig, ax = plt.subplots(figsize=(12, max(6, min(28, 0.18 * len(sub) + 2))))
        y = np.arange(len(sub))
        ax.errorbar(sub["pct_delta_point"], y, xerr=[sub["pct_delta_point"] - sub["pct_delta_ci_lo"], sub["pct_delta_ci_hi"] - sub["pct_delta_point"]], fmt="o", markersize=3, linewidth=0.8)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=6)
        ax.set_title("Scenario contrast: TE(P75)-TE(P25) times hazard level")
        ax.set_xlabel("Percent yield contrast")
        fig.tight_layout()
        path = FIG_DIR / "counterfactual_scenario_contrasts.png"
        fig.savefig(path, dpi=180)
        plt.close(fig)
        paths.append(path)
    if not runtime.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        rt = runtime.copy()
        ax.bar(np.arange(len(rt)), rt["elapsed_seconds"])
        ax.set_xticks(np.arange(len(rt)))
        ax.set_xticklabels(rt["job_label"], rotation=60, ha="right", fontsize=7)
        ax.set_ylabel("Seconds")
        ax.set_title("Runtime by estimated spec/subgroup job")
        fig.tight_layout()
        path = FIG_DIR / "runtime_by_job.png"
        fig.savefig(path, dpi=180)
        plt.close(fig)
        paths.append(path)
    return paths


def run_pipeline(args: argparse.Namespace) -> dict[str, object]:
    start_all = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    df = load_panel()
    base, meta = b067_sample(df)
    jobs = subset_jobs(base)
    specs = all_specs()
    if args.mode == "smoke":
        specs = specs[: args.limit_specs]
        keep = {("baseline", "all", "all"), ("heterogeneity", "irr_group", "high_irr"), ("heterogeneity", "maize_zone", "NE")}
        jobs = [job for job in jobs if (job[0], job[1], job[2]) in keep]

    support_rows = []
    for layer, subgroup_dim, subgroup, sub, reps_default in jobs:
        support_rows.append(
            {
                "sample_id": SAMPLE_ID,
                "layer": layer,
                "subgroup_dim": subgroup_dim,
                "subgroup": subgroup,
                "N_rows_before_dropna": int(len(sub)),
                "N_grids_before_dropna": int(sub["grid_id"].nunique()) if len(sub) else 0,
                "default_reps": reps_default,
            }
        )
    support = pd.DataFrame(support_rows)

    coef_rows_all: list[dict[str, object]] = []
    iede_summary_all: list[pd.DataFrame] = []
    iede_draws_all: list[pd.DataFrame] = []
    path_summary_all: list[pd.DataFrame] = []
    path_draws_all: list[pd.DataFrame] = []
    cf_rows_all: list[dict[str, object]] = []
    skipped_rows: list[dict[str, object]] = []
    method_rows: list[pd.DataFrame] = []
    runtime_rows: list[dict[str, object]] = []

    total = len(jobs) * len(specs)
    done = 0
    for layer, subgroup_dim, subgroup, sub, reps_default in jobs:
        for spec in specs:
            done += 1
            job_start = time.time()
            reps = args.smoke_reps if args.mode == "smoke" else reps_default
            context = {
                "sample_id": SAMPLE_ID,
                "layer": layer,
                "subgroup_dim": subgroup_dim,
                "subgroup": subgroup,
                "bootstrap_method": "cluster_wild_score",
                "bootstrap_reps_requested": reps,
            }
            try:
                work, smeta = prepare_model_frame(sub, spec)
                y = str(smeta["y"])
                rhs_m = list(smeta["rhs_m"])
                rhs_y = list(smeta["rhs_y"])
                main = str(smeta["main"])
                inter = str(smeta["inter"])
                ca_values = dict(smeta["ca_values"])
                hazard_values = dict(smeta["hazard_values"])
                _y, _ca, _rhs_m, _rhs_y, _main, _inter, role_m, role_y = spec_roles(spec)
                fm = fit_fe_from_frame(work, spec.mediator, rhs_m)
                fy = fit_fe_from_frame(work, y, rhs_y)
                coef_rows_all.extend(coefficient_rows(spec, fm, fy, role_m, role_y, context))
                effect_summary, effect_draws, path_summary, path_draws = score_bootstrap(
                    fm,
                    fy,
                    spec,
                    main,
                    inter,
                    ca_values,
                    reps,
                    rng,
                    batch_size=args.batch_size,
                )
                effect_summary = add_context(effect_summary, context, spec)
                effect_draws = add_context(effect_draws, context, spec)
                path_summary = add_context(path_summary, context, spec)
                path_draws = add_context(path_draws, context, spec)
                iede_summary_all.append(effect_summary)
                iede_draws_all.append(effect_draws)
                path_summary_all.append(path_summary)
                path_draws_all.append(path_draws)
                cf_rows_all.extend(counterfactual_rows(effect_draws, effect_summary, hazard_values, context, spec))
                if args.mode == "smoke" and args.pairs_check_reps > 0:
                    pairs = pairs_refit_check(work, spec, rhs_m, rhs_y, main, inter, ca_values, args.pairs_check_reps, rng)
                    pairs = add_context(pairs, {**context, "bootstrap_method": "pairs_cluster_refit", "bootstrap_reps_requested": args.pairs_check_reps}, spec)
                    method_rows.append(pairs)
                elapsed = time.time() - job_start
                runtime_rows.append(
                    {
                        **context,
                        "hazard": spec.hazard,
                        "transform": spec.transform_label,
                        "mediator_tag": spec.mediator_tag,
                        "job_label": f"{layer}/{subgroup}/{spec.spec_id}",
                        "status": "estimated",
                        "N_model": int(fm.n_model),
                        "N_grids": int(fm.n_grids),
                        "elapsed_seconds": elapsed,
                        "seconds_per_rep": elapsed / max(reps, 1),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                elapsed = time.time() - job_start
                skipped_rows.append(
                    {
                        **context,
                        "hazard": spec.hazard,
                        "transform": spec.transform_label,
                        "branch": spec.branch,
                        "mediator_tag": spec.mediator_tag,
                        "mediator": spec.mediator,
                        "reason": str(exc),
                        "N_rows_before_dropna": int(len(sub)),
                    }
                )
                runtime_rows.append(
                    {
                        **context,
                        "hazard": spec.hazard,
                        "transform": spec.transform_label,
                        "mediator_tag": spec.mediator_tag,
                        "job_label": f"{layer}/{subgroup}/{spec.spec_id}",
                        "status": "skipped",
                        "elapsed_seconds": elapsed,
                        "seconds_per_rep": math.nan,
                    }
                )
            if done == 1 or done % args.progress_every == 0 or done == total:
                print(f"[PROGRESS] {done}/{total} jobs; elapsed={time.time() - start_all:.1f}s", flush=True)

    coef = pd.DataFrame(coef_rows_all)
    iede_summary = pd.concat(iede_summary_all, ignore_index=True) if iede_summary_all else pd.DataFrame()
    iede_draws = pd.concat(iede_draws_all, ignore_index=True) if iede_draws_all else pd.DataFrame()
    path_summary = pd.concat(path_summary_all, ignore_index=True) if path_summary_all else pd.DataFrame()
    path_draws = pd.concat(path_draws_all, ignore_index=True) if path_draws_all else pd.DataFrame()
    cf = pd.DataFrame(cf_rows_all)
    skipped = pd.DataFrame(skipped_rows)
    if skipped.empty:
        skipped = pd.DataFrame(
            columns=[
                "sample_id",
                "layer",
                "subgroup_dim",
                "subgroup",
                "bootstrap_method",
                "bootstrap_reps_requested",
                "hazard",
                "transform",
                "branch",
                "mediator_tag",
                "mediator",
                "reason",
                "N_rows_before_dropna",
            ]
        )
    method_check = pd.concat(method_rows, ignore_index=True) if method_rows else pd.DataFrame()
    runtime = pd.DataFrame(runtime_rows)

    suffix = "_smoke" if args.mode == "smoke" else ""
    support.to_csv(OUT_DIR / f"f4_b067_support{suffix}.csv", index=False, encoding="utf-8")
    coef.to_csv(OUT_DIR / f"f4_b067_coefficients_detail{suffix}.csv", index=False, encoding="utf-8")
    iede_summary.to_csv(OUT_DIR / f"f4_b067_iede_bootstrap_summary{suffix}.csv", index=False, encoding="utf-8")
    path_summary.to_csv(OUT_DIR / f"f4_b067_path_bootstrap_summary{suffix}.csv", index=False, encoding="utf-8")
    cf.to_csv(OUT_DIR / f"f4_b067_counterfactual_summary{suffix}.csv", index=False, encoding="utf-8")
    skipped.to_csv(OUT_DIR / f"f4_b067_skipped{suffix}.csv", index=False, encoding="utf-8")
    runtime.to_csv(OUT_DIR / f"f4_b067_runtime{suffix}.csv", index=False, encoding="utf-8")
    draw_path = write_parquet_or_csv(iede_draws, OUT_DIR / f"f4_b067_iede_bootstrap_draws{suffix}.parquet")
    path_draw_path = write_parquet_or_csv(path_draws, OUT_DIR / f"f4_b067_path_bootstrap_draws{suffix}.parquet")
    if not method_check.empty:
        method_check.to_csv(OUT_DIR / "f4_b067_bootstrap_method_check.csv", index=False, encoding="utf-8")

    fig_paths = plot_coefficients(coef)
    fig_paths.extend(plot_effects(iede_summary, cf, path_summary, runtime))

    total_elapsed = time.time() - start_all
    write_runtime_estimate(args, runtime, total_elapsed, support, meta, len(fig_paths), draw_path, path_draw_path)
    write_report(args, support, coef, iede_summary, path_summary, cf, skipped, runtime, meta, fig_paths)
    return {
        "elapsed": total_elapsed,
        "n_coefficients": len(coef),
        "n_iede": len(iede_summary),
        "n_counterfactual": len(cf),
        "n_skipped": len(skipped),
        "n_figures": len(fig_paths),
        "draw_path": str(draw_path),
        "path_draw_path": str(path_draw_path),
    }


def write_runtime_estimate(
    args: argparse.Namespace,
    runtime: pd.DataFrame,
    total_elapsed: float,
    support: pd.DataFrame,
    meta: dict[str, object],
    n_figures: int,
    draw_path: Path,
    path_draw_path: Path,
) -> None:
    estimated = runtime.loc[runtime["status"].eq("estimated")].copy()
    avg_fit_job = float(estimated["elapsed_seconds"].mean()) if not estimated.empty else math.nan
    avg_sec_per_rep = float(estimated["seconds_per_rep"].median()) if not estimated.empty else math.nan
    full_jobs = len(subset_jobs(pd.DataFrame({"grid_id": [], "irr_group": [], "maize_zone": [], "ai_pet_over_p_gridmean": []}))) * len(all_specs())
    full_reps = 12 * 1000 + (2 + 5 + 2) * 12 * 500 + 12 * 1000
    if args.mode == "smoke" and np.isfinite(avg_sec_per_rep):
        projected = avg_sec_per_rep * full_reps
    else:
        projected = total_elapsed
    lines = [
        "# F4-B067 runtime estimate",
        "",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Mode: {args.mode}",
        f"Sample: {SAMPLE_ID}; N_sample={meta['N_sample']}; N_grids={meta['N_grids_sample']}",
        f"Smoke/actual elapsed seconds: {total_elapsed:.2f}",
        f"Estimated jobs in full run: {full_jobs}",
        f"Estimated bootstrap rep-equations in full run: {full_reps}",
        f"Median smoke seconds per requested bootstrap rep-job: {avg_sec_per_rep:.6f}",
        f"Projected full runtime seconds from smoke: {projected:.1f}",
        f"Projected full runtime minutes from smoke: {projected / 60:.1f}",
        f"Figures generated in this run: {n_figures}",
        f"IEDE draw file: {draw_path}",
        f"Path draw file: {path_draw_path}",
        "",
        "Interpretation: this estimate is based on score bootstrap runtime. It is not a Stata reghdfe repeated-refit estimate.",
        "",
        "Support rows:",
        support.to_csv(index=False),
    ]
    (OUT_DIR / "f4_b067_runtime_estimate.md").write_text("\n".join(lines), encoding="utf-8")


def write_report(
    args: argparse.Namespace,
    support: pd.DataFrame,
    coef: pd.DataFrame,
    iede: pd.DataFrame,
    path_bs: pd.DataFrame,
    cf: pd.DataFrame,
    skipped: pd.DataFrame,
    runtime: pd.DataFrame,
    meta: dict[str, object],
    fig_paths: list[Path],
) -> None:
    support_block = "```csv\n" + support.to_csv(index=False) + "```"
    if not runtime.empty and {"job_label", "status", "N_model", "N_grids", "elapsed_seconds"}.issubset(runtime.columns):
        runtime_block = "```csv\n" + runtime[["job_label", "status", "N_model", "N_grids", "elapsed_seconds"]].to_csv(index=False) + "```"
    else:
        runtime_block = ""
    lines = [
        "# F4-B067 完整系数、IE/DE/TE Bootstrap 与情景反事实",
        "",
        f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"运行模式: `{args.mode}`",
        f"样本: `{SAMPLE_ID}`; N={meta['N_sample']}; grids={meta['N_grids_sample']}",
        "样本规则: zone_core=1, sr_within=1, years_ge3=0, stable_province=0; yield_domain/yield_jump/sm_sd/sm_coverage 均不启用。",
        "",
        "## 输出文件",
        "",
        f"- support: `{OUT_DIR / ('f4_b067_support_smoke.csv' if args.mode == 'smoke' else 'f4_b067_support.csv')}`",
        f"- coefficients: `{OUT_DIR / ('f4_b067_coefficients_detail_smoke.csv' if args.mode == 'smoke' else 'f4_b067_coefficients_detail.csv')}`",
        f"- IEDE bootstrap summary: `{OUT_DIR / ('f4_b067_iede_bootstrap_summary_smoke.csv' if args.mode == 'smoke' else 'f4_b067_iede_bootstrap_summary.csv')}`",
        f"- path bootstrap summary: `{OUT_DIR / ('f4_b067_path_bootstrap_summary_smoke.csv' if args.mode == 'smoke' else 'f4_b067_path_bootstrap_summary.csv')}`",
        f"- counterfactual summary: `{OUT_DIR / ('f4_b067_counterfactual_summary_smoke.csv' if args.mode == 'smoke' else 'f4_b067_counterfactual_summary.csv')}`",
        f"- runtime estimate: `{OUT_DIR / 'f4_b067_runtime_estimate.md'}`",
        "",
        "## 完成度",
        "",
        f"- coefficient rows: {len(coef)}",
        f"- IE/DE/TE summary rows: {len(iede)}",
        f"- path bootstrap summary rows: {len(path_bs)}",
        f"- counterfactual rows: {len(cf)}",
        f"- skipped rows: {len(skipped)}",
        f"- figure files: {len(fig_paths)}",
        "",
        "## 样本支持",
        "",
        support_block,
        "",
        "## Runtime",
        "",
        runtime_block,
        "",
        "## 说明",
        "",
        "IE/DE/TE 先在每个成功估计的 spec/subgroup 内计算，再用同一组 cluster wild score bootstrap 权重获得不确定性。情景反事实只从 TE(P75)-TE(P25) 和 hazard 的 P50/P90 暴露水平派生，不单独重估模型。",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    parser.add_argument("--smoke-reps", type=int, default=20)
    parser.add_argument("--pairs-check-reps", type=int, default=20)
    parser.add_argument("--limit-specs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=250)
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    result = run_pipeline(args)
    print("[DONE]", result, flush=True)


if __name__ == "__main__":
    main()
