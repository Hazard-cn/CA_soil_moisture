"""Build G185-only draft assets with wild cluster bootstrap CIs.

The script creates a self-contained G185 manuscript draft pack:
- descriptive statistics
- TE/IE/DE, region, irrigation, and phenology bootstrap tables
- publication-style figures
- a preliminary manuscript draft

Bootstrap method: two-way FE absorption followed by grid-level wild cluster
score bootstrap on the absorbed design matrix. This is intentionally reported
as a within-transformed wild cluster bootstrap, not as a Stata bsample rerun.
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
SCRIPT_DIR = PROJ / "scripts/python"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from expanded_scale_story_search import (  # noqa: E402
    add_full_interactions,
    add_window_terms,
    load_panel,
    load_window_panel,
    rhs_for,
    unique_variants,
)
from bio_window_filter_128 import var_for  # noqa: E402


RUN_DIR = PROJ / "quality_reports/agent_runs/2026-06-20_g185_draft_bootstrap_v1"
FIG_DIR = RUN_DIR / "figures"
SCALE_ID = "G185"
REGIONS = ("NE", "HHH", "NW", "SW", "SH")
HAZARDS = ("drought", "heat", "hotdry")
HAZARD_VAR = {
    "drought": "D_full_raw",
    "heat": "hdd_ge32_raw",
    "hotdry": "HotDryPr_full_raw",
}
HAZARD_LABEL = {
    "drought": "Drought",
    "heat": "Heat",
    "hotdry": "Hot-dry",
}
PHENO_WINDOWS = ("hepm10", "hema")
SR_LEVELS = ("P25", "P50", "P75")
IRR_LEVELS = ("P25", "P50", "P75")
EFFECT_TYPES = ("IE", "DE", "TE")


@dataclass
class AbsorbedModel:
    xvars: list[str]
    beta: np.ndarray
    xtx_inv: np.ndarray
    scores: np.ndarray
    nobs: int
    clusters: int


def pct_from_ln(x: np.ndarray | float) -> np.ndarray | float:
    return np.expm1(x) * 100.0


def q(values: pd.Series | np.ndarray, probs: list[float]) -> list[float]:
    arr = pd.Series(values).dropna().to_numpy(dtype=np.float64)
    return [float(v) for v in np.nanpercentile(arr, probs)]


def fmt_num(value: float, digits: int = 3) -> str:
    if not math.isfinite(value):
        return "NA"
    if abs(value) >= 100:
        return f"{value:.1f}"
    if abs(value) >= 10:
        return f"{value:.2f}"
    return f"{value:.{digits}f}"


def fmt_pct(value: float) -> str:
    return f"{fmt_num(value, 2)}%"


def residualize_two_way(z: np.ndarray, gid: np.ndarray, year: np.ndarray, max_iter: int = 24) -> np.ndarray:
    r = z.astype(np.float64, copy=True)
    n_gid = int(gid.max()) + 1
    n_year = int(year.max()) + 1
    gid_count = np.bincount(gid, minlength=n_gid).astype(np.float64)
    year_count = np.bincount(year, minlength=n_year).astype(np.float64)
    previous = np.inf
    for _ in range(max_iter):
        gid_sum = np.vstack(
            [np.bincount(gid, weights=r[:, j], minlength=n_gid) for j in range(r.shape[1])]
        ).T
        r -= gid_sum[gid] / gid_count[gid, None]
        year_sum = np.vstack(
            [np.bincount(year, weights=r[:, j], minlength=n_year) for j in range(r.shape[1])]
        ).T
        r -= year_sum[year] / year_count[year, None]
        current = float(np.max(np.abs(year_sum)))
        if current < 1e-10 or abs(previous - current) < 1e-12:
            break
        previous = current
    return r


def common_work(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    unique_cols = list(dict.fromkeys([*cols, "grid_code", "year_code"]))
    work = df.loc[:, unique_cols].dropna().copy()
    if len(work) < 500:
        raise ValueError(f"N_lt_500 for {cols}")
    work["_gid_boot"], _ = pd.factorize(work["grid_code"], sort=True)
    work["_year_boot"], _ = pd.factorize(work["year_code"], sort=True)
    return work


def fit_absorbed_from_work(work: pd.DataFrame, yvar: str, xvars: list[str]) -> AbsorbedModel:
    z = work[[yvar, *xvars]].to_numpy(dtype=np.float64)
    gid = work["_gid_boot"].to_numpy(dtype=np.int64)
    year = work["_year_boot"].to_numpy(dtype=np.int64)
    zr = residualize_two_way(z, gid, year)
    y = zr[:, 0]
    x = zr[:, 1:]
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    resid = y - x @ beta
    xtx_inv = np.linalg.pinv(x.T @ x)
    scores = np.zeros((int(gid.max()) + 1, x.shape[1]), dtype=np.float64)
    np.add.at(scores, gid, x * resid[:, None])
    return AbsorbedModel(
        xvars=list(xvars),
        beta=beta,
        xtx_inv=xtx_inv,
        scores=scores,
        nobs=int(len(work)),
        clusters=int(scores.shape[0]),
    )


def wild_boot_betas(model: AbsorbedModel, rng: np.random.Generator, reps: int, chunk: int = 200) -> np.ndarray:
    out = np.empty((reps, len(model.xvars)), dtype=np.float64)
    done = 0
    while done < reps:
        take = min(chunk, reps - done)
        weights = rng.choice(np.array([-1.0, 1.0], dtype=np.float64), size=(take, model.clusters))
        summed_scores = weights @ model.scores
        out[done : done + take, :] = model.beta[None, :] + summed_scores @ model.xtx_inv.T
        done += take
    return out


def ci_from_boot(values: np.ndarray) -> tuple[float, float]:
    vals = values[np.isfinite(values)]
    if len(vals) == 0:
        return math.nan, math.nan
    lo, hi = np.nanpercentile(vals, [2.5, 97.5])
    return float(lo), float(hi)


def add_ci_row(
    rows: list[dict[str, object]],
    family: str,
    label: dict[str, object],
    estimate: float,
    boot_values: np.ndarray,
    unit: str,
    nobs: int,
    clusters: int,
    reps: int,
) -> None:
    lo, hi = ci_from_boot(boot_values)
    rows.append(
        {
            "family": family,
            **label,
            "estimate": float(estimate),
            "ci_low": lo,
            "ci_high": hi,
            "unit": unit,
            "N_model": int(nobs),
            "N_grids": int(clusters),
            "bootstrap_reps": int(reps),
            "bootstrap_method": "wild_cluster_score_bootstrap_linearized_after_grid_year_fe_absorption",
        }
    )


def scale_meta(panel: pd.DataFrame) -> dict[str, object]:
    variants = {str(meta["sample_id"]): meta for meta in unique_variants(panel)}
    if SCALE_ID not in variants:
        raise KeyError(SCALE_ID)
    return variants[SCALE_ID]


def build_descriptives(panel: pd.DataFrame, sample: pd.DataFrame, meta: dict[str, object]) -> tuple[pd.DataFrame, pd.DataFrame]:
    ca_p25, ca_p50, ca_p75 = q(sample["ca_raw"], [25, 50, 75])
    irr_p25, irr_p50, irr_p75 = q(sample["irr_frac_raw"], [25, 50, 75])
    rows = [
        {"metric": "scale_id", "value": SCALE_ID},
        {"metric": "N_sample", "value": int(len(sample))},
        {"metric": "N_grids_sample", "value": int(sample["grid_code"].nunique())},
        {"metric": "year_min", "value": int(sample["year"].min()) if "year" in sample else ""},
        {"metric": "year_max", "value": int(sample["year"].max()) if "year" in sample else ""},
        {"metric": "rule_main_sample", "value": int(meta["main_sample"])},
        {"metric": "rule_zone_core", "value": int(meta["zone_core"])},
        {"metric": "rule_yield_domain", "value": int(meta["yield_domain"])},
        {"metric": "rule_yield_jump", "value": int(meta["yield_jump"])},
        {"metric": "rule_sm_sd", "value": int(meta["sm_sd"])},
        {"metric": "rule_sm_coverage", "value": int(meta["sm_coverage"])},
        {"metric": "rule_sr_within", "value": int(meta["sr_within"])},
        {"metric": "rule_years_ge3", "value": int(meta["years_ge3"])},
        {"metric": "rule_stable_province", "value": int(meta["stable_province"])},
        {"metric": "ca_P25", "value": ca_p25},
        {"metric": "ca_P50", "value": ca_p50},
        {"metric": "ca_P75", "value": ca_p75},
        {"metric": "ca_IQR", "value": ca_p75 - ca_p25},
        {"metric": "irr_frac_P25", "value": irr_p25},
        {"metric": "irr_frac_P50", "value": irr_p50},
        {"metric": "irr_frac_P75", "value": irr_p75},
    ]
    for hazard, hvar in HAZARD_VAR.items():
        rows.append({"metric": f"{hazard}_P90", "value": float(np.nanpercentile(sample[hvar], 90))})
    region = (
        sample.groupby("maize_zone", observed=True)
        .agg(
            N=("ln_yield_raw", "size"),
            grids=("grid_code", "nunique"),
            ca_mean=("ca_raw", "mean"),
            ca_p25=("ca_raw", lambda s: np.nanpercentile(s, 25)),
            ca_p75=("ca_raw", lambda s: np.nanpercentile(s, 75)),
            irr_mean=("irr_frac_raw", "mean"),
            drought_p90=("D_full_raw", lambda s: np.nanpercentile(s, 90)),
            heat_p90=("hdd_ge32_raw", lambda s: np.nanpercentile(s, 90)),
            hotdry_p90=("HotDryPr_full_raw", lambda s: np.nanpercentile(s, 90)),
        )
        .reset_index()
        .rename(columns={"maize_zone": "region"})
    )
    named = region.loc[region["region"].astype(str).isin(REGIONS)].copy()
    other = region.loc[~region["region"].astype(str).isin(REGIONS)].copy()
    rows.extend(
        [
            {"metric": "five_region_N_sample", "value": int(named["N"].sum())},
            {"metric": "five_region_N_grids", "value": int(named["grids"].sum())},
            {"metric": "other_region_N_sample", "value": int(other["N"].sum())},
            {"metric": "region_set", "value": "NE, HHH, NW, SW, SH; Other excluded from region-specific regressions"},
        ]
    )
    desc = pd.DataFrame(rows)
    return desc, region


def xvars_for_irrigation(hazard: str) -> tuple[list[str], str, str]:
    if hazard == "drought":
        main = "D_full_raw"
        inter = "SR_x_D_full_raw"
        companions = ["W_full_raw", "hdd_ge32_raw"]
        xirr = "drought_x_irr"
        triple = "SR_x_drought_x_irr"
    elif hazard == "heat":
        main = "hdd_ge32_raw"
        inter = "SR_x_Heat_full_raw"
        companions = ["D_full_raw", "W_full_raw"]
        xirr = "heat_x_irr"
        triple = "SR_x_heat_x_irr"
    else:
        main = "HotDryPr_full_raw"
        inter = "SR_x_HotDryPr_full_raw"
        companions = ["D_full_raw", "hdd_ge32_raw", "W_full_raw"]
        xirr = "hotdry_x_irr"
        triple = "SR_x_hotdry_x_irr"
    xvars = [
        main,
        "ca_raw",
        "irr_frac_raw",
        inter,
        xirr,
        "SR_x_irr",
        triple,
        *companions,
        "pr_sum_raw",
        "et0_sum_raw",
        "gdd_10_30_raw",
        "aridity_raw",
    ]
    return list(dict.fromkeys(xvars)), inter, triple


def bootstrap_te_iede(sample: pd.DataFrame, reps: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []
    mediator = "gleam_smrz_mean_raw"
    for hazard in HAZARDS:
        yvar, _, rhs_m, rhs_y, main, inter = rhs_for(hazard, "raw", mediator)
        hvar = HAZARD_VAR[hazard]
        work = common_work(sample, [yvar, mediator, *rhs_m, *rhs_y, hvar, "ca_raw"])
        m_model = fit_absorbed_from_work(work, mediator, rhs_m)
        y_model = fit_absorbed_from_work(work, yvar, rhs_y)
        weights_rng = np.random.default_rng(seed + 100 + HAZARDS.index(hazard))
        m_boot = wild_boot_betas(m_model, weights_rng, reps)
        weights_rng = np.random.default_rng(seed + 100 + HAZARDS.index(hazard))
        y_boot = wild_boot_betas(y_model, weights_rng, reps)

        m_idx = {name: i for i, name in enumerate(rhs_m)}
        y_idx = {name: i for i, name in enumerate(rhs_y)}
        ca_vals = dict(zip(SR_LEVELS, q(work["ca_raw"], [25, 50, 75])))
        hazard_p90 = float(np.nanpercentile(work[hvar], 90))

        a1 = m_model.beta[m_idx[main]]
        a3 = m_model.beta[m_idx[inter]]
        b = y_model.beta[y_idx[mediator]]
        c1 = y_model.beta[y_idx[main]]
        c3 = y_model.beta[y_idx[inter]]

        a1_b = m_boot[:, m_idx[main]]
        a3_b = m_boot[:, m_idx[inter]]
        b_b = y_boot[:, y_idx[mediator]]
        c1_b = y_boot[:, y_idx[main]]
        c3_b = y_boot[:, y_idx[inter]]

        for level, ca_value in ca_vals.items():
            ie = (a1 + a3 * ca_value) * b
            de = c1 + c3 * ca_value
            te = ie + de
            ie_b = (a1_b + a3_b * ca_value) * b_b
            de_b = c1_b + c3_b * ca_value
            te_b = ie_b + de_b
            for effect, estimate, boot in (
                ("IE", ie, ie_b),
                ("DE", de, de_b),
                ("TE", te, te_b),
            ):
                add_ci_row(
                    rows,
                    "te_iede",
                    {"hazard": hazard, "effect_type": effect, "sr_level": level, "hazard_p90": hazard_p90},
                    float(pct_from_ln(estimate * hazard_p90)),
                    pct_from_ln(boot * hazard_p90),
                    "pct_yield_at_hazard_p90",
                    y_model.nobs,
                    y_model.clusters,
                    reps,
                )
        p25, p75 = ca_vals["P25"], ca_vals["P75"]
        ie_delta = ((a1 + a3 * p75) * b) - ((a1 + a3 * p25) * b)
        de_delta = (c1 + c3 * p75) - (c1 + c3 * p25)
        te_delta = ie_delta + de_delta
        ie_delta_b = ((a1_b + a3_b * p75) * b_b) - ((a1_b + a3_b * p25) * b_b)
        de_delta_b = (c1_b + c3_b * p75) - (c1_b + c3_b * p25)
        te_delta_b = ie_delta_b + de_delta_b
        for effect, estimate, boot in (
            ("IE_delta_P75_minus_P25", ie_delta, ie_delta_b),
            ("DE_delta_P75_minus_P25", de_delta, de_delta_b),
            ("TE_delta_P75_minus_P25", te_delta, te_delta_b),
        ):
            add_ci_row(
                rows,
                "te_iede",
                {"hazard": hazard, "effect_type": effect, "sr_level": "P75_minus_P25", "hazard_p90": hazard_p90},
                float(pct_from_ln(estimate * hazard_p90)),
                pct_from_ln(boot * hazard_p90),
                "pct_yield_at_hazard_p90",
                y_model.nobs,
                y_model.clusters,
                reps,
            )
    return pd.DataFrame(rows)


def bootstrap_region(sample: pd.DataFrame, reps: int, seed: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    mediator = "gleam_smrz_mean_raw"
    for r_idx, region in enumerate(REGIONS):
        rsub = sample.loc[sample["maize_zone"].astype(str).eq(region)].copy()
        for h_idx, hazard in enumerate(HAZARDS):
            yvar, _, _, rhs_y, _, inter = rhs_for(hazard, "raw", mediator)
            hvar = HAZARD_VAR[hazard]
            try:
                work = common_work(rsub, [yvar, *rhs_y, hvar, "ca_raw"])
                model = fit_absorbed_from_work(work, yvar, rhs_y)
            except Exception:
                continue
            boot = wild_boot_betas(model, np.random.default_rng(seed + 300 + r_idx * 10 + h_idx), reps)
            idx = {name: i for i, name in enumerate(rhs_y)}
            ca_iqr = q(work["ca_raw"], [75])[0] - q(work["ca_raw"], [25])[0]
            hazard_p90 = float(np.nanpercentile(work[hvar], 90))
            ln_est = model.beta[idx[inter]] * ca_iqr * hazard_p90
            ln_boot = boot[:, idx[inter]] * ca_iqr * hazard_p90
            add_ci_row(
                rows,
                "region",
                {
                    "region": region,
                    "hazard": hazard,
                    "coefficient": float(model.beta[idx[inter]]),
                    "ca_iqr": ca_iqr,
                    "hazard_p90": hazard_p90,
                },
                float(pct_from_ln(ln_est)),
                pct_from_ln(ln_boot),
                "pct_yield_buffer_at_region_hazard_p90",
                model.nobs,
                model.clusters,
                reps,
            )
    return pd.DataFrame(rows)


def bootstrap_irrigation(sample: pd.DataFrame, reps: int, seed: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for h_idx, hazard in enumerate(HAZARDS):
        xvars, inter, triple = xvars_for_irrigation(hazard)
        hvar = HAZARD_VAR[hazard]
        work = common_work(sample, ["ln_yield_raw", *xvars, hvar, "ca_raw", "irr_frac_raw"])
        model = fit_absorbed_from_work(work, "ln_yield_raw", xvars)
        boot = wild_boot_betas(model, np.random.default_rng(seed + 500 + h_idx), reps)
        idx = {name: i for i, name in enumerate(xvars)}
        ca_p25, ca_p75 = q(work["ca_raw"], [25, 75])
        irr_p25, irr_p50, irr_p75 = q(work["irr_frac_raw"], [25, 50, 75])
        ca_iqr = ca_p75 - ca_p25
        hazard_p90 = float(np.nanpercentile(work[hvar], 90))
        base = model.beta[idx[inter]]
        tri = model.beta[idx[triple]]
        base_b = boot[:, idx[inter]]
        tri_b = boot[:, idx[triple]]
        for level, irr_value in zip(IRR_LEVELS, (irr_p25, irr_p50, irr_p75)):
            ln_est = (base + tri * irr_value) * ca_iqr * hazard_p90
            ln_boot = (base_b + tri_b * irr_value) * ca_iqr * hazard_p90
            add_ci_row(
                rows,
                "irrigation",
                {
                    "hazard": hazard,
                    "irr_level": level,
                    "irr_value": irr_value,
                    "ca_iqr": ca_iqr,
                    "hazard_p90": hazard_p90,
                    "base_c3": float(base),
                    "triple": float(tri),
                },
                float(pct_from_ln(ln_est)),
                pct_from_ln(ln_boot),
                "pct_yield_buffer_at_hazard_p90",
                model.nobs,
                model.clusters,
                reps,
            )
        ln_diff = tri * (irr_p75 - irr_p25) * ca_iqr * hazard_p90
        ln_diff_b = tri_b * (irr_p75 - irr_p25) * ca_iqr * hazard_p90
        add_ci_row(
            rows,
            "irrigation",
            {
                "hazard": hazard,
                "irr_level": "P75_minus_P25",
                "irr_value": irr_p75 - irr_p25,
                "ca_iqr": ca_iqr,
                "hazard_p90": hazard_p90,
                "base_c3": float(base),
                "triple": float(tri),
            },
            float(pct_from_ln(ln_diff)),
            pct_from_ln(ln_diff_b),
            "pct_yield_buffer_at_hazard_p90",
            model.nobs,
            model.clusters,
            reps,
        )
    return pd.DataFrame(rows)


def bootstrap_phenology(window_sample: pd.DataFrame, reps: int, seed: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for w_idx, window in enumerate(PHENO_WINDOWS):
        d = var_for("D", window)
        h = var_for("H", window)
        dh = f"D_x_H_{window}"
        srdh = f"SR_x_D_x_H_{window}"
        xvars = [
            d,
            h,
            dh,
            "ca",
            f"SR_x_{d}",
            f"SR_x_{h}",
            srdh,
            var_for("W", window),
            var_for("P", window),
            var_for("ET0", window),
            var_for("GDD", window),
            "irr_frac",
            "aridity",
        ]
        work = common_work(window_sample, ["ln_yield", *xvars])
        model = fit_absorbed_from_work(work, "ln_yield", xvars)
        boot = wild_boot_betas(model, np.random.default_rng(seed + 700 + w_idx), reps)
        idx = {name: i for i, name in enumerate(xvars)}
        ca_p25, ca_p50, ca_p75 = q(work["ca"], [25, 50, 75])
        beta = model.beta[idx[dh]]
        gamma = model.beta[idx[srdh]]
        beta_b = boot[:, idx[dh]]
        gamma_b = boot[:, idx[srdh]]
        for level, ca_value in zip(SR_LEVELS, (ca_p25, ca_p50, ca_p75)):
            est = beta + gamma * ca_value
            boot_values = beta_b + gamma_b * ca_value
            add_ci_row(
                rows,
                "phenology",
                {"window": window, "sr_level": level, "ca_value": ca_value, "beta_DH": float(beta), "gamma_SRDH": float(gamma)},
                float(est),
                boot_values,
                "D_x_H_slope_at_SR_quantile",
                model.nobs,
                model.clusters,
                reps,
            )
        shift = gamma * (ca_p75 - ca_p25)
        shift_b = gamma_b * (ca_p75 - ca_p25)
        add_ci_row(
            rows,
            "phenology",
            {"window": window, "sr_level": "P75_minus_P25", "ca_value": ca_p75 - ca_p25, "beta_DH": float(beta), "gamma_SRDH": float(gamma)},
            float(shift),
            shift_b,
            "D_x_H_slope_shift_P75_minus_P25",
            model.nobs,
            model.clusters,
            reps,
        )
    return pd.DataFrame(rows)


def save_markdown_table(df: pd.DataFrame, path: Path, title: str) -> None:
    view = df.copy()
    float_cols = view.select_dtypes(include=[np.number]).columns
    for col in float_cols:
        def _fmt_cell(x: object) -> str:
            if pd.isna(x):
                return ""
            val = float(x)
            if math.isfinite(val) and abs(val - round(val)) < 1e-9:
                return str(int(round(val)))
            return fmt_num(val, 5)

        view[col] = view[col].map(_fmt_cell)
    cols = [str(c) for c in view.columns]
    lines = [
        f"# {title}",
        "",
        "| " + " | ".join(cols) + " |",
        "|" + "|".join("---" for _ in cols) + "|",
    ]
    for _, row in view.iterrows():
        vals = []
        for col in view.columns:
            val = "" if pd.isna(row[col]) else str(row[col])
            vals.append(val.replace("\n", " ").replace("|", "/"))
        lines.append("| " + " | ".join(vals) + " |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def plot_te_iede(df: pd.DataFrame) -> None:
    data = df.loc[(df["family"].eq("te_iede")) & (df["sr_level"].isin(SR_LEVELS))].copy()
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.3), sharey=False)
    colors = {"IE": "#9ecae1", "DE": "#fdae6b", "TE": "#74c476"}
    legend_labels = {
        "IE": "IE (SM-linked component)",
        "DE": "DE (residual component)",
        "TE": "TE (combined contrast)",
    }
    width = 0.22
    x = np.arange(len(SR_LEVELS))
    for ax, hazard in zip(axes, HAZARDS):
        sub = data.loc[data["hazard"].eq(hazard)]
        for offset, effect in zip((-width, 0, width), EFFECT_TYPES):
            e = sub.loc[sub["effect_type"].eq(effect)].set_index("sr_level").reindex(SR_LEVELS)
            y = e["estimate"].to_numpy(dtype=float)
            lo = e["ci_low"].to_numpy(dtype=float)
            hi = e["ci_high"].to_numpy(dtype=float)
            yerr = np.vstack([y - lo, hi - y])
            ax.bar(x + offset, y, width=width, label=legend_labels[effect], color=colors[effect], edgecolor="white")
            ax.errorbar(x + offset, y, yerr=yerr, fmt="none", ecolor="black", capsize=2, linewidth=0.8)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xticks(x, SR_LEVELS)
        ax.set_title(HAZARD_LABEL[hazard])
        ax.set_ylabel("Yield change at P90 hazard (%)")
    axes[0].legend(frameon=False, loc="best")
    fig.suptitle("G185: TE/IE/DE slope components across SR quantiles")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig1_g185_te_iede_bootstrap.png", dpi=300, facecolor="white")
    plt.close(fig)


def plot_region(df: pd.DataFrame) -> None:
    data = df.loc[df["family"].eq("region")].copy()
    data["label"] = data["region"].astype(str) + "-" + data["hazard"].map(HAZARD_LABEL)
    data["order"] = data["region"].map({r: i for i, r in enumerate(REGIONS)}) * 10 + data["hazard"].map({h: i for i, h in enumerate(HAZARDS)})
    data.sort_values("order", ascending=False, inplace=True)
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    y = np.arange(len(data))
    est = data["estimate"].to_numpy(dtype=float)
    lo = data["ci_low"].to_numpy(dtype=float)
    hi = data["ci_high"].to_numpy(dtype=float)
    colors = data["hazard"].map({"drought": "#756bb1", "heat": "#e6550d", "hotdry": "#31a354"}).to_numpy()
    ax.scatter(est, y, color=colors, s=40, zorder=3)
    ax.hlines(y, lo, hi, color="0.25", linewidth=1.1)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_yticks(y, data["label"])
    ax.set_xlabel("SR-associated buffer at region-specific P90 hazard (%)")
    ax.set_title("G185: region-specific hazard buffering")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig2_g185_region_bootstrap.png", dpi=300, facecolor="white")
    plt.close(fig)


def plot_irrigation(df: pd.DataFrame) -> None:
    data = df.loc[(df["family"].eq("irrigation")) & (df["irr_level"].isin(IRR_LEVELS))].copy()
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    x = np.arange(len(IRR_LEVELS))
    colors = {"drought": "#756bb1", "heat": "#e6550d", "hotdry": "#31a354"}
    for hazard in HAZARDS:
        sub = data.loc[data["hazard"].eq(hazard)].set_index("irr_level").reindex(IRR_LEVELS)
        y = sub["estimate"].to_numpy(dtype=float)
        lo = sub["ci_low"].to_numpy(dtype=float)
        hi = sub["ci_high"].to_numpy(dtype=float)
        ax.plot(x, y, marker="o", label=HAZARD_LABEL[hazard], color=colors[hazard])
        ax.fill_between(x, lo, hi, color=colors[hazard], alpha=0.14)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x, IRR_LEVELS)
    ax.set_ylabel("SR-associated buffer at P90 hazard (%)")
    ax.set_xlabel("Irrigation fraction quantile")
    ax.set_title("G185: irrigation-conditioned buffering margins")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig3_g185_irrigation_bootstrap.png", dpi=300, facecolor="white")
    plt.close(fig)


def plot_phenology(df: pd.DataFrame) -> None:
    data = df.loc[(df["family"].eq("phenology")) & (df["sr_level"].isin(SR_LEVELS))].copy()
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    x = np.arange(len(SR_LEVELS))
    colors = {"hepm10": "#3182bd", "hema": "#de2d26"}
    labels = {"hepm10": "HE +/- 10", "hema": "HE-MA"}
    for window in PHENO_WINDOWS:
        sub = data.loc[data["window"].eq(window)].set_index("sr_level").reindex(SR_LEVELS)
        y = sub["estimate"].to_numpy(dtype=float)
        lo = sub["ci_low"].to_numpy(dtype=float)
        hi = sub["ci_high"].to_numpy(dtype=float)
        ax.plot(x, y, marker="o", label=labels[window], color=colors[window])
        ax.fill_between(x, lo, hi, color=colors[window], alpha=0.14)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x, SR_LEVELS)
    ax.set_ylabel("D x H slope at SR quantile")
    ax.set_xlabel("SR quantile")
    ax.set_title("G185: phenology-windowed compound-stress slopes")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig4_g185_phenology_bootstrap.png", dpi=300, facecolor="white")
    plt.close(fig)


def top_value(df: pd.DataFrame, family: str, **filters: str) -> dict[str, object]:
    sub = df.loc[df["family"].eq(family)].copy()
    for key, value in filters.items():
        if key in sub.columns:
            sub = sub.loc[sub[key].astype(str).eq(str(value))]
    if sub.empty:
        return {}
    return sub.iloc[0].to_dict()


def literature_block() -> str:
    rows = reference_anchor_rows()
    lines = []
    for row in rows:
        lines.append(
            f"- {row['item_key']}; {row['publicationTitle']}; DOI {row['DOI']}; {row['title']} [{row['use']}]"
        )
    return "\n".join(lines)


def reference_anchor_rows() -> list[dict[str, object]]:
    path = PROJ / "temp/2026-06-18_zotero_story_direction/target_journal_exact_dedup.csv"
    metadata = {}
    if path.exists():
        ref = pd.read_csv(path)
        metadata = {str(row["item_key"]): row.to_dict() for _, row in ref.iterrows()}
    wanted = [
        ("58E9GZYN", "regional adaptation and climate damage accounting"),
        ("IUZH8WDN", "regional climate surprises and agricultural impacts"),
        ("JJY74242", "irrigation boundary for heat sensitivity"),
        ("28M3GU42", "compound soil drought and atmospheric aridity"),
        ("T79SQWVL", "atmospheric dryness and productivity stress"),
        ("3BAXRP6J", "breadbasket-scale compound drought risk"),
        ("PWYXU7WH", "conservation agriculture and yield stability under climate extremes"),
        ("Q4MZYF9B", "conservation tillage in arid Loess Plateau"),
        ("K2HANYSG", "conservation agriculture under warming"),
        ("RYJCGIPT", "water management and crop-yield boundary conditions"),
        ("AKASZ7GL", "agricultural climate tradeoffs"),
    ]
    rows: list[dict[str, object]] = []
    for item_key, use in wanted:
        meta = metadata.get(item_key, {})
        doi = meta.get("DOI", "")
        if isinstance(doi, float) and math.isnan(doi):
            doi = ""
        if not doi:
            continue
        rows.append(
            {
                "item_key": item_key,
                "year": meta.get("year", ""),
                "title": meta.get("title", ""),
                "publicationTitle": meta.get("publicationTitle", ""),
                "DOI": doi,
                "use": use,
            }
        )
    return rows


def write_reference_anchors() -> None:
    refs = pd.DataFrame(reference_anchor_rows())
    refs.to_csv(RUN_DIR / "g185_reference_anchors.csv", index=False, encoding="utf-8-sig")
    save_markdown_table(refs, RUN_DIR / "g185_reference_anchors.md", "G185 reference anchors")


def scale_selection_rows() -> tuple[pd.DataFrame, dict[str, int]]:
    expanded_path = PROJ / "temp/2026-06-11_expanded_scale_story_search/expanded_scale_index.csv"
    high_path = PROJ / "temp/2026-06-11_region_first_story_search/all_highscore_ranking_cluster.csv"
    expanded = pd.read_csv(expanded_path) if expanded_path.exists() else pd.DataFrame()
    high = pd.read_csv(high_path) if high_path.exists() else pd.DataFrame()
    meta = {
        "n_expanded_scales": int(len(expanded)),
        "n_highscore_scales": int(len(high)),
    }
    if high.empty:
        return pd.DataFrame(), meta
    view = high.head(12).copy()
    view.insert(0, "rank", np.arange(1, len(view) + 1))
    keep_cols = [
        "rank",
        "sample_id",
        "N_sample",
        "N_grids_sample",
        "active_rule_count",
        "main_sample",
        "region_score",
        "region_evidence",
        "national_score",
        "irrigation_score",
        "phenology_score",
        "buffer_NE_drought",
        "buffer_HHH_heat",
        "buffer_HHH_hotdry",
    ]
    return view[[c for c in keep_cols if c in view.columns]], meta


def write_scale_selection_transparency() -> dict[str, int]:
    table, meta = scale_selection_rows()
    table.to_csv(RUN_DIR / "g185_scale_selection_transparency.csv", index=False, encoding="utf-8-sig")
    save_markdown_table(table, RUN_DIR / "g185_scale_selection_transparency.md", "G185 scale-selection transparency")
    return meta


def write_draft(boot: pd.DataFrame, desc: pd.DataFrame, region_desc: pd.DataFrame, reps: int) -> None:
    desc_map = {str(row.metric): row.value for row in desc.itertuples(index=False)}
    scale_table, scale_counts = scale_selection_rows()
    g185_rank = "NA"
    if not scale_table.empty and SCALE_ID in set(scale_table["sample_id"].astype(str)):
        g185_rank = str(int(scale_table.loc[scale_table["sample_id"].astype(str).eq(SCALE_ID), "rank"].iloc[0]))
    ne_d = top_value(boot, "region", region="NE", hazard="drought")
    hhh_h = top_value(boot, "region", region="HHH", hazard="heat")
    hhh_hd = top_value(boot, "region", region="HHH", hazard="hotdry")
    heat_irr_delta = top_value(boot, "irrigation", hazard="heat", irr_level="P75_minus_P25")
    hotdry_irr_delta = top_value(boot, "irrigation", hazard="hotdry", irr_level="P75_minus_P25")
    drought_irr_delta = top_value(boot, "irrigation", hazard="drought", irr_level="P75_minus_P25")
    hepm_shift = top_value(boot, "phenology", window="hepm10", sr_level="P75_minus_P25")
    hema_shift = top_value(boot, "phenology", window="hema", sr_level="P75_minus_P25")
    te_drought_delta = top_value(boot, "te_iede", hazard="drought", effect_type="TE_delta_P75_minus_P25")
    te_heat_delta = top_value(boot, "te_iede", hazard="heat", effect_type="TE_delta_P75_minus_P25")
    te_hotdry_delta = top_value(boot, "te_iede", hazard="hotdry", effect_type="TE_delta_P75_minus_P25")

    total_n = int(float(desc_map["N_sample"]))
    total_grids = int(float(desc_map["N_grids_sample"]))
    region_n = int(float(desc_map["five_region_N_sample"]))
    region_grids = int(float(desc_map["five_region_N_grids"]))
    other_n = int(float(desc_map["other_region_N_sample"]))

    lines = [
        "# G185 Manuscript Draft: Region-targeted SR buffering under compound climate stress",
        "",
        "## Working title",
        "",
        "Targeted straw-return buffering of maize yield losses under region-specific drought, heat and hot-dry stress in China",
        "",
        "## Abstract draft",
        "",
        (
            f"Straw return (SR) is widely discussed as a soil-conservation practice, but its yield-loss buffering association under climate stress is unlikely to be spatially uniform. "
            f"Using the G185 grid-year maize panel (N={total_n:,}; grids={total_grids:,}), this draft evaluates whether SR-associated yield buffering appears as a state-dependent association across hazards, maize zones, irrigation exposure and phenology windows. "
            f"G185 is a `main_sample=1` alternative selected from a scale-search workflow, ranking {g185_rank} among the high-score region-first candidates; this choice is reported as a transparent specification decision rather than a pre-registered design. "
            f"The strongest five-region evidence (N={region_n:,}; grids={region_grids:,}; `Other` excluded, N={other_n:,}) is region-targeted: NE shows a drought-buffering margin of {fmt_pct(ne_d.get('estimate', math.nan))} [{fmt_pct(ne_d.get('ci_low', math.nan))}, {fmt_pct(ne_d.get('ci_high', math.nan))}], whereas HHH shows heat and hot-dry margins of {fmt_pct(hhh_h.get('estimate', math.nan))} and {fmt_pct(hhh_hd.get('estimate', math.nan))}. "
            f"Higher irrigation is associated with lower heat and hot-dry SR-buffering margins, with P75-P25 contrasts of {fmt_pct(heat_irr_delta.get('estimate', math.nan))} and {fmt_pct(hotdry_irr_delta.get('estimate', math.nan))}; the drought contrast is weaker at {fmt_pct(drought_irr_delta.get('estimate', math.nan))}. "
            f"HE±10 and HE-MA windows provide auxiliary D x H slope evidence, with P75-P25 slope shifts of {fmt_num(hepm_shift.get('estimate', math.nan), 5)} and {fmt_num(hema_shift.get('estimate', math.nan), 5)}. "
            f"Uncertainty intervals use {reps} within-transformed wild-cluster score/bootstrap-linearized draws after grid and year fixed-effect absorption. "
            f"All results are framed as conditional associations with climate-damage slopes, not as causal adoption effects."
        ),
        "",
        "## One-sentence contribution",
        "",
        "G185 支持的中心贡献不是“SR 普遍增产”，而是“SR 相关缓冲以区域主导胁迫为中心，并受到灌溉边界和关键物候窗口约束”。",
        "",
        "English take-home sentence: At the G185 scale, straw-return-associated buffering is best described as region-targeted and state-dependent, with the strongest support appearing where the dominant regional stress aligns with the relevant SR-modified loss slope.",
        "",
        "## Scale-selection transparency",
        "",
        (
            f"The expanded search generated {scale_counts.get('n_expanded_scales', 0)} unique Gxxx scale variants. "
            f"The region-first table retained {scale_counts.get('n_highscore_scales', 0)} high-score candidates. "
            f"G057 is the top region-first scale, but it does not activate `main_sample`; G185 is the closest high-ranked alternative that keeps `main_sample=1` while preserving the same region-evidence profile. "
            f"Accordingly, all figures and statements in this draft use G185 only, and cross-scale evidence is not mixed into the G185 claims."
        ),
        "",
        "## Results draft",
        "",
        "### Result 1. National slope components show buffering, but the national average is not the final story",
        "",
        (
            f"Figure 1 reports three non-causal slope components at SR P25, P50 and P75 after scaling each hazard slope to its within-scale P90 exposure. "
            f"`IE` denotes the soil-moisture-associated algebraic component, `DE` denotes the residual hazard-yield component, and `TE` denotes their combined slope contrast. "
            f"The P75-minus-P25 TE contrasts are {fmt_pct(te_drought_delta.get('estimate', math.nan))} for drought, {fmt_pct(te_heat_delta.get('estimate', math.nan))} for heat and {fmt_pct(te_hotdry_delta.get('estimate', math.nan))} for hot-dry exposure. "
            f"This pattern is useful as a national diagnostic: higher SR is aligned with flatter climate-loss slopes, but the component structure differs by hazard and should not be written as causal mediation or a universal mechanism."
        ),
        "",
        "![G185 TE IE DE bootstrap](figures/fig1_g185_te_iede_bootstrap.png)",
        "",
        "### Result 2. The main G185 story is region-targeted buffering",
        "",
        (
            f"Figure 2 uses the five named maize zones and excludes `Other`. "
            f"In NE, the drought-buffering statistic is {fmt_pct(ne_d.get('estimate', math.nan))} with a bootstrap-linearized interval of [{fmt_pct(ne_d.get('ci_low', math.nan))}, {fmt_pct(ne_d.get('ci_high', math.nan))}]. "
            f"In HHH, the heat-buffering statistic is {fmt_pct(hhh_h.get('estimate', math.nan))} [{fmt_pct(hhh_h.get('ci_low', math.nan))}, {fmt_pct(hhh_h.get('ci_high', math.nan))}], and the hot-dry statistic is {fmt_pct(hhh_hd.get('estimate', math.nan))} [{fmt_pct(hhh_hd.get('ci_low', math.nan))}, {fmt_pct(hhh_hd.get('ci_high', math.nan))}]. "
            f"These are central because they combine sample support, regional stress interpretation and interval support. "
            f"SW and SH positive estimates are reported as boundary/support evidence because SW has very low SR IQR and SH has small sample support; NW remains a weaker boundary because its intervals cross zero."
        ),
        "",
        "![G185 region bootstrap](figures/fig2_g185_region_bootstrap.png)",
        "",
        "### Result 3. Irrigation is a boundary condition rather than a monotonic amplifier",
        "",
        (
            f"Figure 3 uses continuous `irr_frac` margins. "
            f"For heat, moving from irrigation P25 to P75 changes the SR-buffering margin by {fmt_pct(heat_irr_delta.get('estimate', math.nan))} [{fmt_pct(heat_irr_delta.get('ci_low', math.nan))}, {fmt_pct(heat_irr_delta.get('ci_high', math.nan))}]. "
            f"For hot-dry exposure, the corresponding contrast is {fmt_pct(hotdry_irr_delta.get('estimate', math.nan))} [{fmt_pct(hotdry_irr_delta.get('ci_low', math.nan))}, {fmt_pct(hotdry_irr_delta.get('ci_high', math.nan))}]. "
            f"The drought contrast is positive but weaker ({fmt_pct(drought_irr_delta.get('estimate', math.nan))}) and should be described as suggestive. "
            f"The safe interpretation is that heat and hot-dry SR-buffering margins are smaller at higher irrigation levels; this is a water-management boundary condition, not proof of technological substitution."
        ),
        "",
        "![G185 irrigation bootstrap](figures/fig3_g185_irrigation_bootstrap.png)",
        "",
        "### Result 4. Phenology windows provide auxiliary consistency evidence",
        "",
        (
            f"Figure 4 reports D x H slopes at SR P25, P50 and P75 for HE±10 and HE-MA windows. "
            f"The P75-minus-P25 shift is {fmt_num(hepm_shift.get('estimate', math.nan), 5)} for HE±10 and {fmt_num(hema_shift.get('estimate', math.nan), 5)} for HE-MA. "
            f"These results should be treated as auxiliary consistency evidence because they come from the Python phenology-window model and do not yet have an independent Stata replication. "
            f"They support a temporally localized slope-pattern interpretation, not a standalone mechanism claim."
        ),
        "",
        "![G185 phenology bootstrap](figures/fig4_g185_phenology_bootstrap.png)",
        "",
        "## Discussion draft",
        "",
        (
            "The G185 evidence supports a targeted conditional-association framing. SR is not written as a universally beneficial intervention; it is written as a management condition whose association with yield-loss slopes varies across the stress regime, water-management context and crop stage. "
            "The implication is therefore not a blanket adoption rule, but a more bounded statement: SR-related buffering is most defensible where the dominant regional stress and the relevant loss slope are aligned, and where water-management conditions leave room for that margin to appear."
        ),
        "",
        "## Methods draft",
        "",
        (
            f"The G185 scale was constructed from the GGCP10 maize panel by fixing `ggcp10_maize_frac >= 0.05` and activating `main_sample`, `yield_domain`, `yield_jump` and `sm_sd`; `zone_core`, `sm_coverage`, `sr_within`, `years_ge3` and `stable_province` were not activated. "
            f"The resulting estimation sample contains {total_n:,} grid-year observations and {total_grids:,} grid clusters. "
            f"Region-specific models use the five named maize zones (`NE`, `HHH`, `NW`, `SW`, `SH`) and exclude `Other`, giving {region_n:,} observations and {region_grids:,} grid clusters. "
            "All reported models absorb grid and year fixed effects. The original scale-search tables use grid-level clustered inference; this draft adds comparable figure-level intervals using a within-transformed wild-cluster score/bootstrap-linearized procedure with Rademacher grid weights. "
            "Because this is a first-order score update around the absorbed model, it should not be described as a full pairs cluster bootstrap, Stata `bootstrap`, or `boottest` replication."
        ),
        "",
        "## Literature anchors from local Zotero-derived table",
        "",
        literature_block(),
        "",
        "## Figure plan",
        "",
        "- Figure 1: G185 national TE/IE/DE slope components by SR quantile, scaled to P90 hazard exposure.",
        "- Figure 2: G185 five-region SR-buffering margins by hazard.",
        "- Figure 3: G185 continuous irrigation margins for drought, heat and hot-dry exposure.",
        "- Figure 4: G185 phenology-window D x H slope at SR quantiles.",
        "",
        "## Current limitations that must remain visible",
        "",
        "- G185 is a scale-search-derived, result-oriented main-sample alternative; the scale-selection appendix must travel with the draft.",
        "- Region evidence is centered on NE drought and HHH heat/hot-dry; SW/SH positive estimates are boundary/support evidence and NW is not a central positive result.",
        "- Irrigation evidence supports heat/hot-dry boundary conditions more strongly than drought.",
        "- Phenology evidence is auxiliary until a Stata or independent replication is added.",
        "- IE/DE/TE labels are algebraic slope components, not causal mediation estimates.",
        "- All causal terms should be avoided unless a later design adds stronger identification.",
        "",
    ]
    (RUN_DIR / "g185_manuscript_draft.md").write_text("\n".join(lines), encoding="utf-8")

    region_desc.to_csv(RUN_DIR / "g185_region_descriptive_stats.csv", index=False, encoding="utf-8-sig")


def write_figure_captions(reps: int) -> None:
    lines = [
        "# G185 Figure Captions",
        "",
        "Figure 1. TE/IE/DE slope components across SR quantiles at the G185 scale. `IE` is the soil-moisture-associated algebraic component, `DE` is the residual hazard-yield component, and `TE` is the combined slope contrast; these labels are not causal mediation estimates. Bars show yield changes after scaling hazard-slope estimates to the within-scale P90 exposure. Error bars are 95% within-transformed wild-cluster score/bootstrap-linearized intervals with grid clusters.",
        "",
        "Figure 2. Region-specific SR-associated buffering margins by hazard. Points show the percent yield buffer implied by `SR x hazard coefficient x region-specific SR IQR x region-specific hazard P90`; horizontal lines are 95% bootstrap-linearized intervals. Region-specific models use NE, HHH, NW, SW and SH and exclude `Other`.",
        "",
        "Figure 3. Continuous-irrigation margins. Lines show SR-associated buffering at irrigation P25/P50/P75; shaded bands are 95% bootstrap-linearized intervals. The P75-minus-P25 rows in the bootstrap table quantify the irrigation boundary condition.",
        "",
        "Figure 4. Phenology-window D x H slopes. Lines show the estimated D x H slope at SR P25/P50/P75 for HE±10 and HE-MA windows; shaded bands are 95% bootstrap-linearized intervals. These rows are auxiliary consistency evidence until independent Stata replication is added.",
        "",
        f"Bootstrap note: all figures use {reps} Rademacher wild-cluster score/bootstrap-linearized draws after grid and year fixed-effect absorption; cluster unit is `grid_code`. The procedure is not a full pairs cluster bootstrap and not Stata `bootstrap` or `boottest` output.",
        "",
    ]
    (RUN_DIR / "g185_figure_captions.md").write_text("\n".join(lines), encoding="utf-8")


def write_safe_sentences() -> None:
    lines = [
        "# G185 Safe Sentences",
        "",
        "## Main claim",
        "",
        "中文：在 G185 口径下，SR 相关缓冲更适合写成区域定向的气候损失斜率变化，而不是全国统一的平均增产效应。",
        "",
        "English: At the G185 scale, SR-associated buffering is best described as a region-targeted change in climate-damage slopes rather than as a uniform national yield gain.",
        "",
        "## Region",
        "",
        "中文：五个命名玉米区的结果显示，NE 的可写重点是 drought buffering，HHH 的可写重点是 heat 和 hot-dry buffering；NW、SW 和 SH 更适合作为边界或支持性证据处理。",
        "",
        "English: Across the five named maize zones, the central G185 evidence aligns NE with drought-related buffering and HHH with heat and hot-dry buffering, while the remaining zones define support and boundary conditions.",
        "",
        "## Irrigation",
        "",
        "中文：连续灌溉异质性显示，高灌溉条件下 heat 和 hot-dry 的 SR-buffering margin 更小，因此灌溉应写作边界条件，而不是所有胁迫下的单调互补因素。",
        "",
        "English: Continuous-irrigation margins show smaller heat and hot-dry SR-buffering margins at higher irrigation levels, supporting a water-management boundary interpretation rather than a universal complementarity claim.",
        "",
        "## Phenology",
        "",
        "中文：HE±10 和 HE-MA 的窗口结果与关键物候期斜率缓冲相一致，但在 Stata 复核前只能作为辅助一致性证据。",
        "",
        "English: The HE±10 and HE-MA window results are consistent with phenology-localized slope attenuation, but they should remain auxiliary evidence until independently replicated.",
        "",
        "## Unsafe sentences",
        "",
        "- SR causally protects maize yields everywhere in China.",
        "- SR and irrigation are causal complements under all climate hazards.",
        "- TE/IE/DE prove a causal soil-moisture mediation mechanism.",
        "- G185 is a pre-registered or uniquely optimal scale.",
        "- The phenology-window result confirms the mechanism.",
        "",
    ]
    (RUN_DIR / "g185_safe_sentences.md").write_text("\n".join(lines), encoding="utf-8")


def write_review_risk_report() -> None:
    lines = [
        "# G185 Review Risk Report",
        "",
        "## High-risk points",
        "",
        "1. Scale-search risk: G185 is a `main_sample=1` alternative within a result-oriented region-first search. The draft must carry `g185_scale_selection_transparency.csv/md`.",
        "2. Bootstrap wording risk: the current intervals are within-transformed wild-cluster score/bootstrap-linearized intervals, not full pairs cluster bootstrap, Stata `bootstrap`, or `boottest`.",
        "3. Component-label risk: IE/DE/TE are algebraic slope components, not causal direct/indirect effects.",
        "4. Region support risk: five-region models exclude `Other`; total G185 N is 46,299, whereas five-region analytic N is 44,556.",
        "5. Phenology replication risk: phenology results come from Python window models and remain auxiliary until independent replication.",
        "",
        "## Main-text downgrades",
        "",
        "- Use `conditional association`, `SR-associated buffering`, `damage-slope attenuation`, `water-management boundary`, and `auxiliary consistency evidence`.",
        "- Avoid `causal effect`, `robust finding`, `causal mediation`, `universal yield benefit`, and `mechanism confirmed`.",
        "",
    ]
    (RUN_DIR / "g185_review_risk_report.md").write_text("\n".join(lines), encoding="utf-8")


def run(reps: int, seed: int) -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    panel = add_full_interactions(load_panel())
    meta = scale_meta(panel)
    sample = panel.loc[meta["mask"]].copy()
    desc, region_desc = build_descriptives(panel, sample, meta)

    window_panel = add_window_terms(load_window_panel())
    window_meta = scale_meta(window_panel)
    window_sample = window_panel.loc[window_meta["mask"]].copy()

    desc.to_csv(RUN_DIR / "g185_descriptive_stats.csv", index=False, encoding="utf-8-sig")
    region_desc.to_csv(RUN_DIR / "g185_region_descriptive_stats.csv", index=False, encoding="utf-8-sig")
    save_markdown_table(desc, RUN_DIR / "g185_descriptive_stats.md", "G185 descriptive statistics")
    save_markdown_table(region_desc, RUN_DIR / "g185_region_descriptive_stats.md", "G185 region descriptive statistics")

    parts = [
        bootstrap_te_iede(sample, reps, seed),
        bootstrap_region(sample, reps, seed),
        bootstrap_irrigation(sample, reps, seed),
        bootstrap_phenology(window_sample, reps, seed),
    ]
    boot = pd.concat(parts, ignore_index=True, sort=False)
    boot.to_csv(RUN_DIR / "g185_bootstrap_results.csv", index=False, encoding="utf-8-sig")
    save_markdown_table(boot, RUN_DIR / "g185_bootstrap_results.md", "G185 bootstrap results")

    plot_te_iede(boot)
    plot_region(boot)
    plot_irrigation(boot)
    plot_phenology(boot)
    write_scale_selection_transparency()
    write_reference_anchors()
    write_figure_captions(reps)
    write_draft(boot, desc, region_desc, reps)
    write_safe_sentences()
    write_review_risk_report()

    manifest = pd.DataFrame(
        [
            {"key": "scale", "value": SCALE_ID},
            {"key": "bootstrap_reps", "value": reps},
            {"key": "bootstrap_seed", "value": seed},
            {"key": "N_sample", "value": int(len(sample))},
            {"key": "N_grids", "value": int(sample["grid_code"].nunique())},
            {"key": "run_dir", "value": str(RUN_DIR)},
        ]
    )
    manifest.to_csv(RUN_DIR / "run_manifest.csv", index=False, encoding="utf-8-sig")
    print(
        {
            "run_dir": str(RUN_DIR),
            "bootstrap_reps": reps,
            "rows": int(len(boot)),
            "figures": sorted(p.name for p in FIG_DIR.glob("*.png")),
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap-reps", type=int, default=999)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    run(args.bootstrap_reps, args.seed)


if __name__ == "__main__":
    main()
