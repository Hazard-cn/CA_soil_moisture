"""Build a G185 method-upgrade report with embedded figures.

This script is intentionally report-oriented:
- fixed-effect G185 results come from the existing G185 bootstrap table;
- Python and R ML outputs are reported as heterogeneity concordance checks;
- all outputs are written to a separate run directory.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
SCRIPT_DIR = PROJ / "scripts/python"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_g185_draft_bootstrap_v1 import (  # noqa: E402
    HAZARD_LABEL,
    HAZARD_VAR,
    HAZARDS,
    REGIONS,
    add_full_interactions,
    pct_from_ln,
    residualize_two_way,
)
from expanded_scale_story_search import load_panel, unique_variants  # noqa: E402


RUN_DIR = PROJ / "quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report"
SOURCE_RUN = PROJ / "quality_reports/agent_runs/2026-06-20_g185_draft_bootstrap_v1"
BOOT_CSV = SOURCE_RUN / "g185_bootstrap_results.csv"
DESC_CSV = SOURCE_RUN / "g185_descriptive_stats.csv"
REGION_DESC_CSV = SOURCE_RUN / "g185_region_descriptive_stats.csv"
FIG_DIR = RUN_DIR / "figures"
TABLE_DIR = RUN_DIR / "tables"
LOG_DIR = RUN_DIR / "logs"
REVIEW_DIR = RUN_DIR / "review"
SCALE_ID = "G185"
PYTHON_ML = Path(os.environ.get("PYTHON_ML", PROJ / ".venv-ml/Scripts/python.exe"))
RSCRIPT_EXE = Path(
    os.environ.get("RSCRIPT_EXE", "C:/Users/Lenovo/AppData/Local/Programs/R/bin/Rscript.exe")
)

CENTRAL_REGION_HAZARDS = {
    ("NE", "drought"),
    ("HHH", "heat"),
    ("HHH", "hotdry"),
}
PROHIBITED_REPORT_STRINGS = (
    "causal effect",
    "causal mediation",
    "direct/indirect effect",
)


@dataclass
class MlRunConfig:
    smoke: bool
    seed: int
    bootstrap_reps: int
    ml_sample_cap: int
    econml_trees: int
    grf_trees: int


def ensure_dirs() -> None:
    for path in (RUN_DIR, FIG_DIR, TABLE_DIR, LOG_DIR, REVIEW_DIR):
        path.mkdir(parents=True, exist_ok=True)


def log_write(name: str, text: str) -> None:
    (LOG_DIR / name).write_text(text, encoding="utf-8")


def fmt_pct(x: float | int | None) -> str:
    if x is None or not math.isfinite(float(x)):
        return "NA"
    return f"{float(x):.2f}%"


def fmt_num(x: float | int | None, digits: int = 3) -> str:
    if x is None or not math.isfinite(float(x)):
        return "NA"
    return f"{float(x):.{digits}f}"


def read_existing_g185() -> tuple[pd.DataFrame, dict[str, str], pd.DataFrame]:
    if not BOOT_CSV.exists():
        raise FileNotFoundError(BOOT_CSV)
    boot = pd.read_csv(BOOT_CSV)
    desc = {}
    if DESC_CSV.exists():
        desc = dict(pd.read_csv(DESC_CSV).astype(str).values.tolist())
    region_desc = pd.read_csv(REGION_DESC_CSV) if REGION_DESC_CSV.exists() else pd.DataFrame()
    return boot, desc, region_desc


def select_g185_sample() -> pd.DataFrame:
    base = add_full_interactions(load_panel())
    variants = {str(meta["sample_id"]): meta for meta in unique_variants(base)}
    if SCALE_ID not in variants:
        raise KeyError(SCALE_ID)
    sample = base.loc[variants[SCALE_ID]["mask"]].copy()
    return sample


def save_csv(df: pd.DataFrame, name: str) -> Path:
    path = TABLE_DIR / name
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def plot_errorbar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    lo_col: str,
    hi_col: str,
    title: str,
    xlabel: str,
    ylabel: str,
    path: Path,
    color: str = "#2b6cb0",
) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(df))
    y = df[y_col].to_numpy(dtype=float)
    lo = df[lo_col].to_numpy(dtype=float)
    hi = df[hi_col].to_numpy(dtype=float)
    ax.axhline(0, color="#555555", linewidth=0.8)
    ax.errorbar(
        x,
        y,
        yerr=np.vstack([y - lo, hi - y]),
        fmt="o",
        color=color,
        ecolor=color,
        elinewidth=1.8,
        capsize=4,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(df[x_col].astype(str).tolist(), rotation=25, ha="right")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=300, facecolor="white")
    plt.close(fig)


def build_damage_tables_and_figures(boot: pd.DataFrame) -> dict[str, pd.DataFrame]:
    damage = boot.loc[
        (boot["family"].eq("te_iede"))
        & (boot["effect_type"].eq("TE_delta_P75_minus_P25"))
    ].copy()
    damage["hazard_label"] = damage["hazard"].map(HAZARD_LABEL)
    damage = damage[
        [
            "hazard",
            "hazard_label",
            "estimate",
            "ci_low",
            "ci_high",
            "hazard_p90",
            "N_model",
            "N_grids",
            "bootstrap_reps",
            "bootstrap_method",
        ]
    ]
    save_csv(damage, "g185_damage_avoidance_results.csv")
    plot_errorbar(
        damage,
        "hazard_label",
        "estimate",
        "ci_low",
        "ci_high",
        "G185 damage-avoidance margin by hazard",
        "Hazard",
        "P75-minus-P25 SR margin at P90 hazard (%)",
        FIG_DIR / "fig1_g185_damage_avoidance_margin.png",
    )

    region = boot.loc[boot["family"].eq("region")].copy()
    region["hazard_label"] = region["hazard"].map(HAZARD_LABEL)
    region["region_hazard"] = region["region"].astype(str) + " - " + region["hazard_label"].astype(str)
    region["central"] = [
        (str(r), str(h)) in CENTRAL_REGION_HAZARDS
        for r, h in zip(region["region"], region["hazard"])
    ]
    save_csv(region, "g185_region_targeted_margin.csv")
    central = region.loc[region["central"]].copy()
    plot_errorbar(
        central,
        "region_hazard",
        "estimate",
        "ci_low",
        "ci_high",
        "G185 central region-targeted buffering margins",
        "Region-hazard combination",
        "SR-associated margin at regional P90 hazard (%)",
        FIG_DIR / "fig2_g185_region_targeted_margin.png",
        color="#2f855a",
    )

    irrigation = boot.loc[
        (boot["family"].eq("irrigation"))
        & (boot["irr_level"].isin(["P25", "P50", "P75"]))
    ].copy()
    irrigation["hazard_label"] = irrigation["hazard"].map(HAZARD_LABEL)
    save_csv(irrigation, "g185_irrigation_conditioned_margin.csv")
    fig, ax = plt.subplots(figsize=(10, 5))
    for hazard, sub in irrigation.groupby("hazard", sort=False):
        sub = sub.sort_values("irr_value")
        ax.plot(
            sub["irr_value"],
            sub["estimate"],
            marker="o",
            linewidth=2,
            label=HAZARD_LABEL.get(hazard, hazard),
        )
        ax.fill_between(
            sub["irr_value"].to_numpy(dtype=float),
            sub["ci_low"].to_numpy(dtype=float),
            sub["ci_high"].to_numpy(dtype=float),
            alpha=0.15,
        )
    ax.axhline(0, color="#555555", linewidth=0.8)
    ax.set_title("G185 irrigation-conditioned SR-buffering margins")
    ax.set_xlabel("Irrigation fraction")
    ax.set_ylabel("SR-associated margin at P90 hazard (%)")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig3_g185_irrigation_conditioned_margin.png", dpi=300, facecolor="white")
    plt.close(fig)

    comp = boot.loc[
        (boot["family"].eq("te_iede")) & (boot["sr_level"].isin(["P25", "P50", "P75"]))
    ].copy()
    rename = {
        "IE": "SM-associated slope component",
        "DE": "residual hazard-yield component",
        "TE": "combined stress-response slope",
    }
    comp["component_label"] = comp["effect_type"].map(rename)
    comp["hazard_label"] = comp["hazard"].map(HAZARD_LABEL)
    save_csv(comp, "g185_component_diagnostics.csv")
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=False)
    colors = {
        "SM-associated slope component": "#6baed6",
        "residual hazard-yield component": "#fd8d3c",
        "combined stress-response slope": "#74c476",
    }
    for ax, hazard in zip(axes, HAZARDS):
        sub = comp.loc[comp["hazard"].eq(hazard)].copy()
        xpos = np.arange(3)
        width = 0.24
        for i, label in enumerate(rename.values()):
            ss = sub.loc[sub["component_label"].eq(label)].set_index("sr_level").reindex(["P25", "P50", "P75"])
            ax.bar(
                xpos + (i - 1) * width,
                ss["estimate"].to_numpy(dtype=float),
                width=width,
                color=colors[label],
                label=label if hazard == HAZARDS[0] else None,
            )
        ax.axhline(0, color="#555555", linewidth=0.8)
        ax.set_xticks(xpos)
        ax.set_xticklabels(["SR P25", "SR P50", "SR P75"], rotation=20)
        ax.set_title(HAZARD_LABEL[hazard])
        ax.grid(axis="y", alpha=0.2)
    axes[0].set_ylabel("Scaled slope component at P90 hazard (%)")
    fig.suptitle("G185 renamed component diagnostics")
    fig.legend(frameon=False, loc="lower center", ncol=3)
    fig.tight_layout(rect=[0, 0.08, 1, 0.95])
    fig.savefig(FIG_DIR / "fig4_g185_component_profile.png", dpi=300, facecolor="white")
    plt.close(fig)

    return {
        "damage": damage,
        "region": region,
        "central": central,
        "irrigation": irrigation,
        "component": comp,
    }


def prepare_ml_frame(sample: pd.DataFrame, cfg: MlRunConfig) -> pd.DataFrame:
    cols = [
        "grid_code",
        "year_code",
        "maize_zone",
        "ln_yield_raw",
        "ca_raw",
        "D_full_raw",
        "hdd_ge32_raw",
        "HotDryPr_full_raw",
        "W_full_raw",
        "irr_frac_raw",
        "aridity_raw",
        "pr_sum_raw",
        "et0_sum_raw",
        "gdd_10_30_raw",
        "gleam_smrz_mean_raw",
    ]
    work = sample.loc[:, cols].dropna().copy()
    rng = np.random.default_rng(cfg.seed)
    if len(work) > cfg.ml_sample_cap:
        pieces = []
        for _, sub in work.groupby("maize_zone", dropna=False):
            take = max(50, int(round(cfg.ml_sample_cap * len(sub) / len(work))))
            take = min(take, len(sub))
            pieces.append(sub.sample(n=take, random_state=int(rng.integers(1, 2_000_000_000))))
        work = pd.concat(pieces, ignore_index=True)
        if len(work) > cfg.ml_sample_cap:
            work = work.sample(n=cfg.ml_sample_cap, random_state=cfg.seed).copy()
    work["_gid"], _ = pd.factorize(work["grid_code"], sort=True)
    work["_year"], _ = pd.factorize(work["year_code"], sort=True)
    y = residualize_two_way(work[["ln_yield_raw"]].to_numpy(dtype=float), work["_gid"].to_numpy(), work["_year"].to_numpy())[:, 0]
    work["Y_res"] = y
    for hazard, hvar in HAZARD_VAR.items():
        treatment = (work["ca_raw"] * work[hvar]).to_numpy(dtype=float).reshape(-1, 1)
        work[f"T_{hazard}_raw"] = treatment[:, 0]
        work[f"T_{hazard}_res"] = residualize_two_way(treatment, work["_gid"].to_numpy(), work["_year"].to_numpy())[:, 0]
    work["irr_bin"] = pd.qcut(work["irr_frac_raw"], q=3, labels=["low", "mid", "high"], duplicates="drop").astype(str)
    return work


def feature_matrix(work: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    numeric_features = [
        "irr_frac_raw",
        "aridity_raw",
        "pr_sum_raw",
        "et0_sum_raw",
        "gdd_10_30_raw",
        "gleam_smrz_mean_raw",
        "D_full_raw",
        "hdd_ge32_raw",
        "HotDryPr_full_raw",
        "W_full_raw",
    ]
    region = pd.get_dummies(work["maize_zone"].astype(str), prefix="region", dtype=float)
    X = pd.concat([work[numeric_features].reset_index(drop=True), region.reset_index(drop=True)], axis=1)
    W = work[["ca_raw", "irr_frac_raw", "aridity_raw", "pr_sum_raw", "et0_sum_raw", "gdd_10_30_raw"]].copy()
    return X, W


def run_python_ml(work: pd.DataFrame, cfg: MlRunConfig) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str]]:
    messages: list[str] = []
    X, W = feature_matrix(work)
    region_rows = []
    irr_rows = []
    dml_rows = []
    try:
        from econml.dml import CausalForestDML
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import KFold
        from doubleml import DoubleMLData, DoubleMLPLR
    except Exception as exc:
        msg = f"Python ML import failed: {type(exc).__name__}: {exc}"
        messages.append(msg)
        log_write("python_ml_failure.log", msg)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), messages

    for h_idx, hazard in enumerate(HAZARDS):
        Y = work["Y_res"].to_numpy(dtype=float)
        T = work[f"T_{hazard}_res"].to_numpy(dtype=float)
        if np.nanstd(T) <= 1e-12:
            messages.append(f"{hazard}: residual treatment has near-zero variance")
            continue
        try:
            cf = CausalForestDML(
                model_y=RandomForestRegressor(
                    n_estimators=120 if cfg.smoke else 240,
                    min_samples_leaf=20,
                    max_depth=12,
                    random_state=cfg.seed + h_idx,
                    n_jobs=-1,
                ),
                model_t=RandomForestRegressor(
                    n_estimators=120 if cfg.smoke else 240,
                    min_samples_leaf=20,
                    max_depth=12,
                    random_state=cfg.seed + 10 + h_idx,
                    n_jobs=-1,
                ),
                n_estimators=cfg.econml_trees,
                min_samples_leaf=20,
                max_depth=14,
                cv=3,
                random_state=cfg.seed + 20 + h_idx,
                discrete_treatment=False,
                inference=False,
            )
            cf.fit(Y=Y, T=T, X=X, W=W)
            tau = np.ravel(cf.effect(X))
            tmp = work[["maize_zone", "irr_bin", "irr_frac_raw"]].copy()
            tmp["tau"] = tau
            tmp["hazard"] = hazard
            for region, sub in tmp.groupby("maize_zone"):
                region_rows.append(
                    {
                        "method": "econml_forest",
                        "hazard": hazard,
                        "region": str(region),
                        "tau_mean": float(sub["tau"].mean()),
                        "tau_median": float(sub["tau"].median()),
                        "n": int(len(sub)),
                    }
                )
            for irr_bin, sub in tmp.groupby("irr_bin"):
                irr_rows.append(
                    {
                        "method": "econml_forest",
                        "hazard": hazard,
                        "irr_bin": str(irr_bin),
                        "tau_mean": float(sub["tau"].mean()),
                        "tau_median": float(sub["tau"].median()),
                        "n": int(len(sub)),
                    }
                )
        except Exception as exc:
            messages.append(f"{hazard}: EconML forest failed: {type(exc).__name__}: {exc}")

        try:
            df_dml = pd.concat(
                [
                    pd.Series(Y, name="Y"),
                    pd.Series(T, name="D"),
                    W.reset_index(drop=True),
                    X.filter(regex="^region_").reset_index(drop=True),
                ],
                axis=1,
            )
            dml_data = DoubleMLData(df_dml, y_col="Y", d_cols="D")
            learner = RandomForestRegressor(
                n_estimators=100 if cfg.smoke else 200,
                min_samples_leaf=20,
                max_depth=12,
                random_state=cfg.seed + 30 + h_idx,
                n_jobs=-1,
            )
            dml = DoubleMLPLR(
                dml_data,
                ml_l=learner,
                ml_m=learner,
                n_folds=3,
                score="partialling out",
            )
            dml.fit()
            dml_rows.append(
                {
                    "method": "doubleml_plr",
                    "hazard": hazard,
                    "theta": float(dml.coef[0]),
                    "se": float(dml.se[0]),
                    "t_stat": float(dml.t_stat[0]),
                    "p_value": float(dml.pval[0]),
                    "n": int(len(df_dml)),
                }
            )
        except Exception as exc:
            messages.append(f"{hazard}: DoubleML PLR failed: {type(exc).__name__}: {exc}")

    region_df = pd.DataFrame(region_rows)
    irr_df = pd.DataFrame(irr_rows)
    dml_df = pd.DataFrame(dml_rows)
    if not region_df.empty:
        save_csv(region_df, "g185_python_ml_region_concordance.csv")
    if not irr_df.empty:
        save_csv(irr_df, "g185_python_ml_irrigation_concordance.csv")
    if not dml_df.empty:
        save_csv(dml_df, "g185_doubleml_plr_summary.csv")
    if messages:
        log_write("python_ml_messages.log", "\n".join(messages))
    return region_df, irr_df, dml_df, messages


def write_r_grf_script() -> Path:
    script = LOG_DIR / "run_g185_grf.R"
    script.write_text(
        r'''
args <- commandArgs(trailingOnly = TRUE)
input_csv <- args[[1]]
out_dir <- args[[2]]
trees <- as.integer(args[[3]])
seed <- as.integer(args[[4]])

suppressPackageStartupMessages(library(grf))
suppressPackageStartupMessages(library(data.table))

set.seed(seed)
d <- fread(input_csv)
feature_cols <- grep("^(irr_frac_raw|aridity_raw|pr_sum_raw|et0_sum_raw|gdd_10_30_raw|gleam_smrz_mean_raw|D_full_raw|hdd_ge32_raw|HotDryPr_full_raw|W_full_raw|region_)", names(d), value = TRUE)
X <- as.matrix(d[, ..feature_cols])

region_rows <- list()
irr_rows <- list()
hazards <- c("drought", "heat", "hotdry")
for (hazard in hazards) {
  y <- d[["Y_res"]]
  w <- d[[paste0("T_", hazard, "_res")]]
  cf <- causal_forest(X, y, w, num.trees = trees, min.node.size = 20, seed = seed + match(hazard, hazards))
  tau <- as.numeric(predict(cf)$predictions)
  tmp <- data.table(hazard = hazard, region = d$maize_zone, irr_bin = d$irr_bin, tau = tau)
  region_rows[[hazard]] <- tmp[, .(tau_mean = mean(tau), tau_median = median(tau), n = .N), by = .(hazard, region)]
  irr_rows[[hazard]] <- tmp[, .(tau_mean = mean(tau), tau_median = median(tau), n = .N), by = .(hazard, irr_bin)]
}
region <- rbindlist(region_rows, fill = TRUE)
region[, method := "r_grf"]
irr <- rbindlist(irr_rows, fill = TRUE)
irr[, method := "r_grf"]
fwrite(region, file.path(out_dir, "g185_r_grf_region_concordance.csv"))
fwrite(irr, file.path(out_dir, "g185_r_grf_irrigation_concordance.csv"))
meta <- data.table(package = c("grf", "data.table"), version = c(as.character(packageVersion("grf")), as.character(packageVersion("data.table"))), trees = trees)
fwrite(meta, file.path(out_dir, "g185_r_grf_meta.csv"))
cat("R grf complete\n")
'''.strip()
        + "\n",
        encoding="utf-8",
    )
    return script


def run_r_grf(work: pd.DataFrame, cfg: MlRunConfig) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    messages: list[str] = []
    X, _ = feature_matrix(work)
    export = pd.concat([work.reset_index(drop=True), X.filter(regex="^region_").reset_index(drop=True)], axis=1)
    export_path = TABLE_DIR / "g185_ml_frame_for_r.csv"
    export.to_csv(export_path, index=False, encoding="utf-8-sig")
    script = write_r_grf_script()
    if not RSCRIPT_EXE.exists():
        msg = f"Rscript not found: {RSCRIPT_EXE}"
        log_write("r_grf_failure.log", msg)
        return pd.DataFrame(), pd.DataFrame(), [msg]
    cmd = [
        str(RSCRIPT_EXE),
        str(script),
        str(export_path),
        str(TABLE_DIR),
        str(cfg.grf_trees),
        str(cfg.seed),
    ]
    proc = subprocess.run(cmd, cwd=str(PROJ), capture_output=True, text=True, timeout=600)
    log_write("r_grf_stdout.log", proc.stdout)
    log_write("r_grf_stderr.log", proc.stderr)
    if proc.returncode != 0:
        msg = f"R grf failed with return code {proc.returncode}"
        messages.append(msg)
        return pd.DataFrame(), pd.DataFrame(), messages
    region_path = TABLE_DIR / "g185_r_grf_region_concordance.csv"
    irr_path = TABLE_DIR / "g185_r_grf_irrigation_concordance.csv"
    region = pd.read_csv(region_path) if region_path.exists() else pd.DataFrame()
    irr = pd.read_csv(irr_path) if irr_path.exists() else pd.DataFrame()
    return region, irr, messages


def concordance_summary(
    boot_region: pd.DataFrame,
    python_region: pd.DataFrame,
    python_irr: pd.DataFrame,
    r_region: pd.DataFrame,
    r_irr: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for method, region_df, irr_df in (
        ("econml_forest", python_region, python_irr),
        ("r_grf", r_region, r_irr),
    ):
        for region, hazard in sorted(CENTRAL_REGION_HAZARDS):
            if region_df.empty:
                rows.append(
                    {
                        "method": method,
                        "check": f"{region}_{hazard}_positive",
                        "status": "not_available",
                        "value": math.nan,
                    }
                )
                continue
            hit = region_df.loc[(region_df["region"].astype(str).eq(region)) & (region_df["hazard"].eq(hazard))]
            value = float(hit["tau_mean"].iloc[0]) if not hit.empty else math.nan
            rows.append(
                {
                    "method": method,
                    "check": f"{region}_{hazard}_positive",
                    "status": "pass" if math.isfinite(value) and value > 0 else "not_pass",
                    "value": value,
                }
            )
        for hazard in ("heat", "hotdry"):
            value = math.nan
            status = "not_available"
            if not irr_df.empty:
                sub = irr_df.loc[irr_df["hazard"].eq(hazard)].copy()
                low = sub.loc[sub["irr_bin"].eq("low"), "tau_mean"]
                high = sub.loc[sub["irr_bin"].eq("high"), "tau_mean"]
                if not low.empty and not high.empty:
                    value = float(high.iloc[0] - low.iloc[0])
                    status = "pass" if value < 0 else "not_pass"
            rows.append(
                {
                    "method": method,
                    "check": f"{hazard}_high_minus_low_irrigation_negative",
                    "status": status,
                    "value": value,
                }
            )
    summary = pd.DataFrame(rows)
    save_csv(summary, "g185_ml_concordance_summary.csv")
    return summary


def plot_ml_figures(
    python_region: pd.DataFrame,
    python_irr: pd.DataFrame,
    r_region: pd.DataFrame,
    r_irr: pd.DataFrame,
    summary: pd.DataFrame,
) -> None:
    combined = pd.concat([python_region, r_region], ignore_index=True)
    if combined.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, "Python/R ML region outputs unavailable", ha="center", va="center")
        ax.axis("off")
        fig.savefig(FIG_DIR / "fig5_g185_python_ml_concordance.png", dpi=300, facecolor="white")
        plt.close(fig)
    else:
        sub = combined.loc[
            [
                (str(r), str(h)) in CENTRAL_REGION_HAZARDS
                for r, h in zip(combined["region"], combined["hazard"])
            ]
        ].copy()
        sub["region_hazard"] = sub["region"].astype(str) + " - " + sub["hazard"].map(HAZARD_LABEL)
        fig, ax = plt.subplots(figsize=(10, 5))
        methods = list(sub["method"].dropna().unique())
        xlabels = list(sub["region_hazard"].dropna().unique())
        xbase = np.arange(len(xlabels))
        width = 0.34
        for i, method in enumerate(methods):
            vals = []
            for label in xlabels:
                hit = sub.loc[(sub["method"].eq(method)) & (sub["region_hazard"].eq(label))]
                vals.append(float(hit["tau_mean"].iloc[0]) if not hit.empty else np.nan)
            ax.bar(xbase + (i - 0.5) * width, vals, width=width, label=method)
        ax.axhline(0, color="#555555", linewidth=0.8)
        ax.set_xticks(xbase)
        ax.set_xticklabels(xlabels, rotation=25, ha="right")
        ax.set_title("G185 ML concordance: central region-hazard combinations")
        ax.set_ylabel("Predicted heterogeneity slope contrast")
        ax.legend(frameon=False)
        ax.grid(axis="y", alpha=0.25)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "fig5_g185_python_ml_concordance.png", dpi=300, facecolor="white")
        plt.close(fig)

    r_plot = r_irr.copy()
    if r_plot.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, "R grf irrigation output unavailable", ha="center", va="center")
        ax.axis("off")
    else:
        fig, ax = plt.subplots(figsize=(10, 5))
        order = {"low": 0, "mid": 1, "high": 2}
        for hazard, sub in r_plot.groupby("hazard", sort=False):
            sub = sub.copy()
            sub["_order"] = sub["irr_bin"].map(order)
            sub = sub.sort_values("_order")
            ax.plot(sub["_order"], sub["tau_mean"], marker="o", linewidth=2, label=HAZARD_LABEL.get(hazard, hazard))
        ax.axhline(0, color="#555555", linewidth=0.8)
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(["Low irrigation", "Mid irrigation", "High irrigation"])
        ax.set_title("G185 R grf heterogeneity by irrigation bin")
        ax.set_ylabel("Predicted heterogeneity slope contrast")
        ax.legend(frameon=False)
        ax.grid(axis="y", alpha=0.25)
        fig.tight_layout()
    fig.savefig(FIG_DIR / "fig6_g185_r_grf_heterogeneity.png", dpi=300, facecolor="white")
    plt.close(fig)


def markdown_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "_No available rows._"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else fmt_num(float(x), 5))
    cols = [str(c) for c in view.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in view.columns) + " |")
    return "\n".join(lines)


def build_review_files(py_messages: list[str], r_messages: list[str], summary: pd.DataFrame) -> None:
    pass_count = int(summary["status"].eq("pass").sum()) if not summary.empty else 0
    total = int(len(summary)) if not summary.empty else 0
    risk = [
        "# G185 Method Upgrade Review Risk Report",
        "",
        "## Main risks",
        "",
        "1. G185 remains a scale-search-derived specification and must travel with the scale-selection transparency note.",
        "2. ML outputs are heterogeneity concordance checks and cannot replace the fixed-effect margin results.",
        "3. Renamed IE/DE/TE components are algebraic slope diagnostics, not mediation estimates.",
        "4. Python and R ML diagnostics use a deterministic G185 ML subsample for computational feasibility.",
        "5. If ML concordance fails for a hazard, that hazard remains supported only by the fixed-effect G185 margin evidence.",
        "",
        "## ML execution messages",
        "",
        "Python messages:",
        "",
        "\n".join(f"- {m}" for m in py_messages) if py_messages else "- none",
        "",
        "R messages:",
        "",
        "\n".join(f"- {m}" for m in r_messages) if r_messages else "- none",
        "",
        f"Concordance pass count: {pass_count}/{total}.",
    ]
    (REVIEW_DIR / "review_risk_report.md").write_text("\n".join(risk), encoding="utf-8")

    safe = [
        "# G185 Method Upgrade Safe Sentences",
        "",
        "中文：在 G185 口径下，高 SR 与低 SR 的差异更适合表达为 P90 胁迫暴露下的 damage-avoidance margin，而不是全国平均增产。",
        "",
        "English: At the G185 scale, the P75-minus-P25 SR contrast is best reported as a damage-avoidance margin at P90 hazard exposure rather than as a uniform national yield gain.",
        "",
        "中文：重命名后的土壤水分相关组件、残余 hazard-yield 组件和 combined stress-response slope 共同说明结果结构，但不构成正式中介识别。",
        "",
        "English: The renamed component diagnostics describe the structure of the fitted stress-response slope and should be interpreted as association components rather than mediation estimates.",
        "",
        "中文：ML 结果只用于检查区域和灌溉异质性结构是否在更灵活的模型中保持方向一致。",
        "",
        "English: The ML diagnostics are used only to assess whether the region and irrigation heterogeneity patterns are directionally reproduced under flexible learners.",
    ]
    (REVIEW_DIR / "safe_sentences_method_upgrade.md").write_text("\n".join(safe), encoding="utf-8")


def render_report(
    cfg: MlRunConfig,
    desc: dict[str, str],
    region_desc: pd.DataFrame,
    tables: dict[str, pd.DataFrame],
    python_region: pd.DataFrame,
    python_irr: pd.DataFrame,
    dml: pd.DataFrame,
    r_region: pd.DataFrame,
    r_irr: pd.DataFrame,
    summary: pd.DataFrame,
    py_messages: list[str],
    r_messages: list[str],
) -> None:
    damage = tables["damage"]
    central = tables["central"]
    irrigation = tables["irrigation"]
    comp = tables["component"]
    n_sample = desc.get("N_sample", "46299")
    n_grids = desc.get("N_grids_sample", "13236")
    ml_n = int(python_region["n"].sum() / max(1, python_region["hazard"].nunique())) if not python_region.empty else 0

    heat_irr = irrigation.loc[(irrigation["hazard"].eq("heat")) & (irrigation["irr_level"].eq("P75"))]
    lines = [
        "# G185 Method Upgrade Report",
        "",
        "## 1. Research question and G185 scale",
        "",
        f"This report evaluates whether the G185 story can be expressed more clearly through damage-avoidance margins and whether flexible ML diagnostics reproduce the main heterogeneity structure. The fixed-effect G185 sample contains N={n_sample} grid-year observations and {n_grids} grid clusters.",
        "",
        "Boundary: G185 is treated as the only reporting scale in this report. G057 and G049 remain scale-selection context, not additional evidence mixed into the G185 claims.",
        "",
        "## 2. Existing G185 story",
        "",
        "The current G185 story is region-targeted: NE carries the clearest drought margin, while HHH carries the clearest heat and hot-dry margins. Continuous irrigation remains a boundary condition because heat and hot-dry margins decline at higher irrigation levels.",
        "",
        "## 3. Damage-avoidance margin main result",
        "",
        "The main expression is the P75-minus-P25 SR contrast in the fitted combined stress-response slope, scaled to P90 hazard exposure. This is a reporting transformation of the fitted G185 slope contrast, not a new identification strategy.",
        "",
        "![G185 damage-avoidance margin](figures/fig1_g185_damage_avoidance_margin.png)",
        "",
        markdown_table(damage[["hazard_label", "estimate", "ci_low", "ci_high", "N_model", "N_grids"]]),
        "",
        "## 4. Region-targeted and irrigation-conditioned margins",
        "",
        "The central G185 region-hazard combinations remain NE drought, HHH heat and HHH hot-dry. These are the combinations that should carry the main Results text. Other region estimates can be retained as boundary or appendix evidence.",
        "",
        "![G185 region-targeted margin](figures/fig2_g185_region_targeted_margin.png)",
        "",
        markdown_table(central[["region", "hazard_label", "estimate", "ci_low", "ci_high", "N_model", "N_grids"]]),
        "",
        "The irrigation figure keeps the continuous `irr_frac` triple-interaction result visible. It supports a water-management boundary interpretation rather than a universal complementarity statement.",
        "",
        "![G185 irrigation-conditioned margin](figures/fig3_g185_irrigation_conditioned_margin.png)",
        "",
        markdown_table(irrigation[["hazard_label", "irr_level", "irr_value", "estimate", "ci_low", "ci_high"]]),
        "",
        "## 5. Renamed IE/DE/TE component diagnostics",
        "",
        "The component figure uses renamed labels: SM-associated slope component, residual hazard-yield component and combined stress-response slope. These diagnostics explain how the fitted slope is structured, but they should remain mechanism diagnostics or appendix material.",
        "",
        "![G185 component profile](figures/fig4_g185_component_profile.png)",
        "",
        markdown_table(comp[["hazard_label", "effect_type", "component_label", "sr_level", "estimate", "ci_low", "ci_high"]], max_rows=18),
        "",
        "## 6. ML heterogeneity concordance checks",
        "",
        f"Python `econml` and `DoubleML`, plus R `grf`, were run as auxiliary heterogeneity concordance checks. The ML diagnostics use a deterministic G185 ML subsample with n={ml_n if ml_n else 'NA'} for computational feasibility. These outputs are not used as the main identification design.",
        "",
        "![G185 Python/R ML concordance](figures/fig5_g185_python_ml_concordance.png)",
        "",
        markdown_table(summary),
        "",
        "The R `grf` plot reports heterogeneity by irrigation bin. Its role is to check whether the high-irrigation attenuation pattern is directionally reproduced.",
        "",
        "![G185 R grf heterogeneity](figures/fig6_g185_r_grf_heterogeneity.png)",
        "",
        "DoubleML PLR summary:",
        "",
        markdown_table(dml),
        "",
        "Python ML messages:",
        "",
        "\n".join(f"- {m}" for m in py_messages) if py_messages else "- none",
        "",
        "R ML messages:",
        "",
        "\n".join(f"- {m}" for m in r_messages) if r_messages else "- none",
        "",
        "## 7. Subjournal writing guidance and review risk",
        "",
        "Recommended main sentence: At the G185 scale, SR-associated buffering is best described as a region-targeted damage-avoidance margin under dominant regional stress, bounded by irrigation conditions and supported by component diagnostics.",
        "",
        "Recommended Discussion sentence: The ML diagnostics are consistent with using flexible learners as an appendix-level heterogeneity check, while the fixed-effect G185 margins remain the basis of the substantive claim.",
        "",
        "Do not write that ML validates the result as an adoption impact, that renamed components identify mediation, or that G185 is uniquely optimal.",
        "",
        "Risk files:",
        "",
        "- `review/review_risk_report.md`",
        "- `review/safe_sentences_method_upgrade.md`",
    ]
    report_md = "\n".join(lines) + "\n"
    lower = report_md.lower()
    found = [s for s in PROHIBITED_REPORT_STRINGS if s in lower]
    if found:
        raise ValueError(f"Prohibited report strings found: {found}")
    (RUN_DIR / "report.md").write_text(report_md, encoding="utf-8")

    body = simple_markdown_to_html(report_md)
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>G185 Method Upgrade Report</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 1100px; margin: 32px auto; line-height: 1.55; color: #222; }}
h1, h2 {{ color: #1a365d; }}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0 24px; font-size: 13px; }}
th, td {{ border: 1px solid #ddd; padding: 6px 8px; text-align: left; }}
th {{ background: #f2f4f7; }}
img {{ max-width: 100%; border: 1px solid #ddd; margin: 12px 0 22px; }}
code {{ background: #f6f8fa; padding: 1px 4px; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""
    (RUN_DIR / "report.html").write_text(html_doc, encoding="utf-8")


def simple_markdown_to_html(md: str) -> str:
    try:
        import markdown

        return markdown.markdown(md, extensions=["tables", "fenced_code"])
    except Exception:
        chunks = []
        for line in md.splitlines():
            if line.startswith("# "):
                chunks.append(f"<h1>{html.escape(line[2:])}</h1>")
            elif line.startswith("## "):
                chunks.append(f"<h2>{html.escape(line[3:])}</h2>")
            elif line.startswith("![") and "](" in line and line.endswith(")"):
                alt = line.split("](")[0][2:]
                src = line.split("](")[1][:-1]
                chunks.append(f'<img alt="{html.escape(alt)}" src="{html.escape(src)}">')
            elif line.strip():
                chunks.append(f"<p>{html.escape(line)}</p>")
        return "\n".join(chunks)


def write_manifest(cfg: MlRunConfig, extra: dict[str, object]) -> None:
    rows = {
        "scale": SCALE_ID,
        "source_g185_run": str(SOURCE_RUN),
        "run_dir": str(RUN_DIR),
        "smoke": cfg.smoke,
        "bootstrap_reps_requested": cfg.bootstrap_reps,
        "seed": cfg.seed,
        "ml_sample_cap": cfg.ml_sample_cap,
        "econml_trees": cfg.econml_trees,
        "grf_trees": cfg.grf_trees,
        "python_ml": str(PYTHON_ML),
        "rscript_exe": str(RSCRIPT_EXE),
        **extra,
    }
    pd.DataFrame([{"key": k, "value": v} for k, v in rows.items()]).to_csv(
        RUN_DIR / "run_manifest.csv", index=False, encoding="utf-8-sig"
    )


def verify_outputs() -> None:
    required = [
        RUN_DIR / "report.md",
        RUN_DIR / "report.html",
        FIG_DIR / "fig1_g185_damage_avoidance_margin.png",
        FIG_DIR / "fig2_g185_region_targeted_margin.png",
        FIG_DIR / "fig3_g185_irrigation_conditioned_margin.png",
        FIG_DIR / "fig4_g185_component_profile.png",
        FIG_DIR / "fig5_g185_python_ml_concordance.png",
        FIG_DIR / "fig6_g185_r_grf_heterogeneity.png",
        TABLE_DIR / "g185_damage_avoidance_results.csv",
        TABLE_DIR / "g185_ml_concordance_summary.csv",
        REVIEW_DIR / "review_risk_report.md",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing outputs: " + "; ".join(missing))
    html_text = (RUN_DIR / "report.html").read_text(encoding="utf-8").lower()
    found = [s for s in PROHIBITED_REPORT_STRINGS if s in html_text]
    if found:
        raise ValueError(f"Prohibited strings in report.html: {found}")


def run(cfg: MlRunConfig) -> None:
    ensure_dirs()
    boot, desc, region_desc = read_existing_g185()
    tables = build_damage_tables_and_figures(boot)
    sample = select_g185_sample()
    ml_frame = prepare_ml_frame(sample, cfg)
    save_csv(
        pd.DataFrame(
            [
                {
                    "scale": SCALE_ID,
                    "full_g185_n": int(len(sample)),
                    "full_g185_grids": int(sample["grid_code"].nunique()),
                    "ml_n": int(len(ml_frame)),
                    "ml_grids": int(ml_frame["grid_code"].nunique()),
                    "smoke": cfg.smoke,
                }
            ]
        ),
        "g185_ml_sample_manifest.csv",
    )
    py_region, py_irr, dml, py_messages = run_python_ml(ml_frame, cfg)
    r_region, r_irr, r_messages = run_r_grf(ml_frame, cfg)
    summary = concordance_summary(tables["region"], py_region, py_irr, r_region, r_irr)
    plot_ml_figures(py_region, py_irr, r_region, r_irr, summary)
    build_review_files(py_messages, r_messages, summary)
    render_report(
        cfg,
        desc,
        region_desc,
        tables,
        py_region,
        py_irr,
        dml,
        r_region,
        r_irr,
        summary,
        py_messages,
        r_messages,
    )
    write_manifest(
        cfg,
        {
            "report_md": str(RUN_DIR / "report.md"),
            "report_html": str(RUN_DIR / "report.html"),
            "figure_count": len(list(FIG_DIR.glob("*.png"))),
            "table_count": len(list(TABLE_DIR.glob("*.csv"))),
        },
    )
    verify_outputs()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--bootstrap-reps", type=int, default=999)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--ml-sample-cap", type=int, default=None)
    parser.add_argument("--econml-trees", type=int, default=None)
    parser.add_argument("--grf-trees", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = MlRunConfig(
        smoke=bool(args.smoke),
        seed=int(args.seed),
        bootstrap_reps=int(args.bootstrap_reps),
        ml_sample_cap=int(args.ml_sample_cap or (2500 if args.smoke else 12000)),
        econml_trees=int(args.econml_trees or (80 if args.smoke else 240)),
        grf_trees=int(args.grf_trees or (120 if args.smoke else 500)),
    )
    run(cfg)
    print(f"Report written: {RUN_DIR / 'report.html'}")


if __name__ == "__main__":
    main()
