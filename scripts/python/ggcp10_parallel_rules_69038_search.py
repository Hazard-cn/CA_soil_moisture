"""
Parallel rule-combination story search on the original 69,038-row GGCP10 panel.

This script differs from the earlier S0 workflow: it does not start from
main_sample==1 or a sequential S0 waterfall. Each quality rule is a parallel
toggle, and every sample variant is evaluated from the original panel scale.
"""

from __future__ import annotations

import argparse
import itertools
import math
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
BASE_DTA = PROJ / "temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_baseline_suite_analysis_ready.dta"
HOTDRY_DTA = PROJ / "data_build/data/processed/data_v3_main.dta"
RUN_DIR = PROJ / "temp/2026-06-02_parallel_rules_69038_story_search"

RULES = (
    "main_sample",
    "crop_mask",
    "zone_core",
    "yield_domain",
    "yield_jump",
    "sm_sd",
    "sm_coverage",
    "sr_within",
    "years_ge3",
    "stable_province",
)


@dataclass(frozen=True)
class Spec:
    branch: str
    mediator_tag: str
    mediator_base: str
    hazard: str

    def mediator(self, transform: str) -> str:
        return f"{self.mediator_base}_{transform}"

    def set_id(self, sample_id: str, transform: str) -> str:
        label = "winsor_1_99" if transform == "w" else "raw"
        return f"{sample_id}_{label}_{self.branch}_{self.mediator_tag}_{self.hazard}"


SPECS = (
    Spec("mean", "mean_root", "gleam_smrz_mean", "drought"),
    Spec("mean", "mean_root", "gleam_smrz_mean", "heat"),
    Spec("mean", "mean_root", "gleam_smrz_mean", "hotdry"),
    Spec("mean", "mean_surface", "gleam_sms_mean", "drought"),
    Spec("mean", "mean_surface", "gleam_sms_mean", "heat"),
    Spec("mean", "mean_surface", "gleam_sms_mean", "hotdry"),
    Spec("dry", "dry_mdf_p10_sfc", "v6mdf_p10_fn_gss", "drought"),
    Spec("dry", "dry_mdf_p10_sfc", "v6mdf_p10_fn_gss", "heat"),
    Spec("dry", "dry_mdf_p10_sfc", "v6mdf_p10_fn_gss", "hotdry"),
)


BASE_COLUMNS = [
    "grid_id",
    "year",
    "main_sample",
    "province",
    "maize_zone",
    "irr_group",
    "maize_frac",
    "ggcp10_maize_frac",
    "yield_tons_ha",
    "ln_yield",
    "ca",
    "ca_ratio",
    "D_full",
    "W_full",
    "hdd_ge32",
    "pr_sum",
    "et0_sum",
    "gdd_10_30",
    "irr_frac",
    "aridity",
    "gleam_smrz_mean",
    "gleam_sms_mean",
    "v6mdf_p10_fn_gss",
    "gleam_smrz_sd",
    "era5l_swvl3_coverage",
]

CONTINUOUS = [
    "ln_yield",
    "ca",
    "D_full",
    "W_full",
    "hdd_ge32",
    "HotDryPr_full",
    "pr_sum",
    "et0_sum",
    "gdd_10_30",
    "irr_frac",
    "aridity",
    "gleam_smrz_mean",
    "gleam_sms_mean",
    "v6mdf_p10_fn_gss",
]


def load_panel() -> pd.DataFrame:
    df = pd.read_stata(BASE_DTA, columns=BASE_COLUMNS)
    hd = pd.read_stata(HOTDRY_DTA, columns=["grid_id", "year", "hotdrydays_ge32_pr_lt1"])
    df = df.merge(hd, on=["grid_id", "year"], how="left", validate="one_to_one")
    df["HotDryPr_full"] = df["hotdrydays_ge32_pr_lt1"]
    df.drop(columns=["hotdrydays_ge32_pr_lt1"], inplace=True)
    df["grid_code"] = pd.Categorical(df["grid_id"]).codes.astype(np.int64)
    df["year_code"] = pd.Categorical(df["year"]).codes.astype(np.int64)

    df.sort_values(["grid_id", "year"], inplace=True)
    df["dln_prev"] = np.nan
    df["dln_next"] = np.nan
    prev_same = (df["grid_id"].eq(df["grid_id"].shift(1))) & (df["year"].eq(df["year"].shift(1) + 1))
    next_same = (df["grid_id"].eq(df["grid_id"].shift(-1))) & (df["year"].shift(-1).eq(df["year"] + 1))
    df.loc[prev_same, "dln_prev"] = df.loc[prev_same, "ln_yield"] - df["ln_yield"].shift(1).loc[prev_same]
    df.loc[next_same, "dln_next"] = df["ln_yield"].shift(-1).loc[next_same] - df.loc[next_same, "ln_yield"]

    for v in CONTINUOUS:
        df[f"{v}_raw"] = df[v]
        lo, hi = np.nanpercentile(df[v].to_numpy(dtype=np.float64), [1, 99])
        df[f"{v}_w"] = df[v].clip(lower=lo, upper=hi)
    for sx in ("raw", "w"):
        df[f"SR_x_D_full_{sx}"] = df[f"ca_{sx}"] * df[f"D_full_{sx}"]
        df[f"SR_x_W_full_{sx}"] = df[f"ca_{sx}"] * df[f"W_full_{sx}"]
        df[f"SR_x_Heat_full_{sx}"] = df[f"ca_{sx}"] * df[f"hdd_ge32_{sx}"]
        df[f"SR_x_HotDryPr_full_{sx}"] = df[f"ca_{sx}"] * df[f"HotDryPr_full_{sx}"]
    return df


def initial_mask(df: pd.DataFrame, flags: dict[str, bool]) -> np.ndarray:
    mask = np.ones(len(df), dtype=bool)
    if flags["main_sample"]:
        mask &= df["main_sample"].eq(1).to_numpy()
    if flags["crop_mask"]:
        mask &= df["maize_frac"].ge(0.05).to_numpy() & df["ggcp10_maize_frac"].ge(0.01).to_numpy()
    if flags["zone_core"]:
        mask &= ~df["maize_zone"].astype(str).eq("Other").to_numpy()
    if flags["yield_domain"]:
        mask &= df["yield_tons_ha"].ge(0.5).to_numpy() & df["yield_tons_ha"].lt(18).to_numpy()
    if flags["yield_jump"]:
        jump = (df["dln_prev"].abs().gt(1).fillna(False)) | (df["dln_next"].abs().gt(1).fillna(False))
        mask &= ~jump.to_numpy()
    if flags["sm_sd"]:
        mask &= df["gleam_smrz_sd"].ge(0.001).to_numpy()
    if flags["sm_coverage"]:
        mask &= df["era5l_swvl3_coverage"].ge(0.90).to_numpy()

    if flags["sr_within"] or flags["years_ge3"] or flags["stable_province"]:
        tmp = df.loc[mask, ["grid_id", "ca_ratio", "year", "province"]].copy()
        keep_grid = pd.Series(True, index=tmp["grid_id"].drop_duplicates().to_numpy())
        if flags["sr_within"]:
            sr = tmp.groupby("grid_id")["ca_ratio"].agg(["count", "std"])
            keep_grid = keep_grid & ((sr["count"] >= 2) & sr["std"].gt(0)).reindex(keep_grid.index, fill_value=False)
        if flags["years_ge3"]:
            yy = tmp.groupby("grid_id")["year"].nunique()
            keep_grid = keep_grid & yy.ge(3).reindex(keep_grid.index, fill_value=False)
        if flags["stable_province"]:
            pp = tmp.groupby("grid_id")["province"].nunique(dropna=True)
            keep_grid = keep_grid & pp.le(1).reindex(keep_grid.index, fill_value=False)
        mask &= df["grid_id"].isin(keep_grid[keep_grid].index).to_numpy()
    return mask


def rhs_for(hazard: str, transform: str, mediator: str) -> tuple[str, str, list[str], list[str], str, str]:
    sx = transform
    y = f"ln_yield_{sx}"
    ca = f"ca_{sx}"
    d = f"D_full_{sx}"
    w = f"W_full_{sx}"
    h = f"hdd_ge32_{sx}"
    hd = f"HotDryPr_full_{sx}"
    srd = f"SR_x_D_full_{sx}"
    srh = f"SR_x_Heat_full_{sx}"
    srhd = f"SR_x_HotDryPr_full_{sx}"
    controls = [f"pr_sum_{sx}", f"et0_sum_{sx}", f"gdd_10_30_{sx}", f"irr_frac_{sx}", f"aridity_{sx}"]
    if hazard == "drought":
        return y, ca, [d, ca, srd, w, h, *controls], [d, ca, srd, mediator, w, h, *controls], d, srd
    if hazard == "heat":
        return y, ca, [h, ca, srh, d, w, *controls], [h, ca, srh, mediator, d, w, *controls], h, srh
    if hazard == "hotdry":
        return y, ca, [hd, ca, srhd, d, h, w, *controls], [hd, ca, srhd, mediator, d, h, w, *controls], hd, srhd
    raise ValueError(hazard)


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


def fit_fe_cluster(df: pd.DataFrame, yvar: str, xvars: list[str]) -> dict[str, float]:
    cols = [yvar, *xvars, "grid_code", "year_code"]
    work = df.loc[:, cols].dropna()
    if len(work) < 500:
        raise ValueError("N_lt_500")
    z = work[[yvar, *xvars]].to_numpy(dtype=np.float64)
    gid = work["grid_code"].to_numpy(dtype=np.int64)
    year = work["year_code"].to_numpy(dtype=np.int64)
    zr = residualize_two_way(z, gid, year)
    y = zr[:, 0]
    x = zr[:, 1:]
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    resid = y - x @ beta
    xtx_inv = np.linalg.pinv(x.T @ x)
    meat = np.zeros((x.shape[1], x.shape[1]), dtype=np.float64)
    for g in np.unique(gid):
        idx = gid == g
        xu = x[idx].T @ resid[idx]
        meat += np.outer(xu, xu)
    n = len(work)
    gcount = len(np.unique(gid))
    k = x.shape[1]
    scale = (gcount / max(gcount - 1, 1)) * ((n - 1) / max(n - k, 1))
    cov = scale * xtx_inv @ meat @ xtx_inv
    se = np.sqrt(np.maximum(np.diag(cov), 0))
    out: dict[str, float] = {"N": float(n), "clusters": float(gcount)}
    for i, xvar in enumerate(xvars):
        out[f"b:{xvar}"] = float(beta[i])
        out[f"se:{xvar}"] = float(se[i])
        zstat = abs(beta[i] / se[i]) if se[i] > 0 else np.inf
        out[f"p:{xvar}"] = float(2 * (1 - norm.cdf(zstat)))
    rss = float(np.sum(resid * resid))
    tss = float(np.sum((y - y.mean()) ** 2))
    out["r2_within"] = 1.0 - rss / tss if tss > 0 else math.nan
    return out


def fit_fe_ols(df: pd.DataFrame, yvar: str, xvars: list[str]) -> dict[str, float]:
    cols = [yvar, *xvars, "grid_code", "year_code"]
    work = df.loc[:, cols].dropna()
    if len(work) < 500:
        raise ValueError("N_lt_500")
    z = work[[yvar, *xvars]].to_numpy(dtype=np.float64)
    gid = work["grid_code"].to_numpy(dtype=np.int64)
    year = work["year_code"].to_numpy(dtype=np.int64)
    zr = residualize_two_way(z, gid, year)
    y = zr[:, 0]
    x = zr[:, 1:]
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    resid = y - x @ beta
    n = len(work)
    k = x.shape[1]
    xtx_inv = np.linalg.pinv(x.T @ x)
    sigma2 = float(resid @ resid) / max(n - k, 1)
    se = np.sqrt(np.maximum(np.diag(xtx_inv) * sigma2, 0))
    out: dict[str, float] = {"N": float(n), "clusters": float(len(np.unique(gid)))}
    for i, xvar in enumerate(xvars):
        out[f"b:{xvar}"] = float(beta[i])
        out[f"se:{xvar}"] = float(se[i])
        zstat = abs(beta[i] / se[i]) if se[i] > 0 else np.inf
        out[f"p:{xvar}"] = float(2 * (1 - norm.cdf(zstat)))
    rss = float(np.sum(resid * resid))
    tss = float(np.sum((y - y.mean()) ** 2))
    out["r2_within"] = 1.0 - rss / tss if tss > 0 else math.nan
    return out


def classify_v1(branch: str, hazard: str, a1: float, a1_p: float, a3: float, b: float, b_p: float, c1: float, c3: float, ca_values: dict[str, float]) -> dict[str, str]:
    ie = {q: (a1 + a3 * r) * b for q, r in ca_values.items()}
    de = {q: c1 + c3 * r for q, r in ca_values.items()}
    te = {q: ie[q] + de[q] for q in ca_values}
    phys = (branch == "mean" and a1 < 0 and b > 0) or (branch == "dry" and a1 > 0 and b < 0)
    out = {"A_common_pathway": "reject", "B_buffering": "reject", "C_typology": "reject"}
    if not phys:
        return out
    if ie["P50"] < 0 and a1_p < 0.05 and b_p < 0.10:
        out["A_common_pathway"] = "headline_candidate"
    elif ie["P50"] < 0:
        out["A_common_pathway"] = "suggestive"
    if hazard == "heat" and abs(ie["P50"]) >= 0.5 * abs(de["P50"]):
        out["C_typology"] = "headline_candidate"
    elif hazard == "drought" and abs(ie["P50"]) > 0 and abs(de["P50"]) > 0:
        out["C_typology"] = "headline_candidate"
    elif hazard == "hotdry" and abs(de["P50"]) >= abs(ie["P50"]):
        out["C_typology"] = "headline_candidate"
    else:
        out["C_typology"] = "suggestive"
    if (a3 * b) > 0 and te["P75"] > te["P25"]:
        out["B_buffering"] = "headline_candidate"
    return out


def all_rule_flags(max_rules: int | None = None) -> list[dict[str, bool]]:
    combos = []
    for bits in itertools.product([False, True], repeat=len(RULES)):
        flags = dict(zip(RULES, bits))
        if max_rules is not None and sum(bits) > max_rules:
            continue
        combos.append(flags)
    return combos


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-rules", type=int, default=None, help="Optional cap on active rules for smoke tests.")
    parser.add_argument("--limit-variants", type=int, default=None)
    parser.add_argument("--transforms", default="raw,w")
    parser.add_argument("--hazards", default="drought,heat,hotdry")
    parser.add_argument("--mediator-tags", default="mean_root,mean_surface,dry_mdf_p10_sfc")
    parser.add_argument("--se-mode", choices=["ols", "cluster"], default="ols")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    np.random.seed(args.seed)
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    logs = RUN_DIR / "logs"
    logs.mkdir(exist_ok=True)
    start = time.time()
    df = load_panel()
    variants = all_rule_flags(args.max_rules)
    if args.limit_variants:
        variants = variants[: args.limit_variants]
    transforms = [x.strip() for x in args.transforms.split(",") if x.strip()]
    hazards = {x.strip() for x in args.hazards.split(",") if x.strip()}
    mediator_tags = {x.strip() for x in args.mediator_tags.split(",") if x.strip()}
    specs = tuple(sp for sp in SPECS if sp.hazard in hazards and sp.mediator_tag in mediator_tags)

    variant_rows = []
    gate_rows = []
    fit_fn = fit_fe_ols if args.se_mode == "ols" else fit_fe_cluster
    print(f"[START] rows={len(df)} variants={len(variants)} transforms={transforms} specs={len(specs)} se_mode={args.se_mode}", flush=True)
    for vi, flags in enumerate(variants, start=1):
        sample_id = "V" + format(vi - 1, "04d")
        mask = initial_mask(df, flags)
        n = int(mask.sum())
        grids = int(df.loc[mask, "grid_id"].nunique())
        row = {"sample_id": sample_id, "N_sample": n, "grids_sample": grids, "active_rule_count": int(sum(flags.values()))}
        row.update({f"rule_{k}": int(v) for k, v in flags.items()})
        variant_rows.append(row)
        if n < 500:
            continue
        sample = df.loc[mask].copy()
        for transform in transforms:
            for sp in specs:
                mediator = sp.mediator(transform)
                y, ca, rhs_m, rhs_y, main, inter = rhs_for(sp.hazard, transform, mediator)
                needed = list(dict.fromkeys([y, ca, mediator, *rhs_m, *rhs_y, "grid_code", "year_code"]))
                model = sample.loc[:, needed].dropna()
                if len(model) < 500:
                    continue
                try:
                    ca_values = {
                        "P25": float(np.percentile(model[ca], 25)),
                        "P50": float(np.percentile(model[ca], 50)),
                        "P75": float(np.percentile(model[ca], 75)),
                    }
                    fm = fit_fn(model, mediator, rhs_m)
                    fy = fit_fn(model, y, rhs_y)
                    a1 = fm[f"b:{main}"]
                    a3 = fm[f"b:{inter}"]
                    b = fy[f"b:{mediator}"]
                    c1 = fy[f"b:{main}"]
                    c3 = fy[f"b:{inter}"]
                    ie = {q: (a1 + a3 * r) * b for q, r in ca_values.items()}
                    de = {q: c1 + c3 * r for q, r in ca_values.items()}
                    te = {q: ie[q] + de[q] for q in ca_values}
                    verdicts = classify_v1(sp.branch, sp.hazard, a1, fm[f"p:{main}"], a3, b, fy[f"p:{mediator}"], c1, c3, ca_values)
                    for story, verdict in verdicts.items():
                        gate_rows.append(
                            {
                                "sample_id": sample_id,
                                "set_id": sp.set_id(sample_id, transform),
                                "branch": sp.branch,
                                "mediator_tag": sp.mediator_tag,
                                "mediator": mediator,
                                "hazard": sp.hazard,
                                "transform": "winsor_1_99" if transform == "w" else "raw",
                                "story": story,
                                "verdict_v1": verdict,
                                "N_sample": n,
                                "grids_sample": grids,
                                "N_model": int(fm["N"]),
                                "clusters_model": int(fm["clusters"]),
                                "a1": a1,
                                "a1_se": fm[f"se:{main}"],
                                "a1_p": fm[f"p:{main}"],
                                "a3": a3,
                                "a3_se": fm[f"se:{inter}"],
                                "a3_p": fm[f"p:{inter}"],
                                "b": b,
                                "b_se": fy[f"se:{mediator}"],
                                "b_p": fy[f"p:{mediator}"],
                                "c1": c1,
                                "c1_se": fy[f"se:{main}"],
                                "c1_p": fy[f"p:{main}"],
                                "c3": c3,
                                "c3_se": fy[f"se:{inter}"],
                                "c3_p": fy[f"p:{inter}"],
                                "ca_p25": ca_values["P25"],
                                "ca_p50": ca_values["P50"],
                                "ca_p75": ca_values["P75"],
                                "ie25": ie["P25"],
                                "ie50": ie["P50"],
                                "ie75": ie["P75"],
                                "de25": de["P25"],
                                "de50": de["P50"],
                                "de75": de["P75"],
                                "te25": te["P25"],
                                "te50": te["P50"],
                                "te75": te["P75"],
                                **{f"rule_{k}": int(v) for k, v in flags.items()},
                            }
                        )
                except (np.linalg.LinAlgError, ValueError, FloatingPointError) as exc:
                    gate_rows.append(
                        {
                            "sample_id": sample_id,
                            "set_id": sp.set_id(sample_id, transform),
                            "branch": sp.branch,
                            "mediator_tag": sp.mediator_tag,
                            "mediator": mediator,
                            "hazard": sp.hazard,
                            "transform": "winsor_1_99" if transform == "w" else "raw",
                            "story": "fit_failed",
                            "verdict_v1": "reject",
                            "N_sample": n,
                            "grids_sample": grids,
                            "fail_reason": str(exc),
                            **{f"rule_{k}": int(v) for k, v in flags.items()},
                        }
                    )
        if vi % 25 == 0 or vi == len(variants):
            pd.DataFrame(variant_rows).to_csv(RUN_DIR / "parallel_rule_variant_index.csv", index=False)
            pd.DataFrame(gate_rows).to_csv(RUN_DIR / "parallel_rule_gate_scan.csv", index=False)
            print(f"[PROGRESS] variant={vi}/{len(variants)} gate_rows={len(gate_rows)} elapsed={time.time()-start:.1f}s", flush=True)

    variant_df = pd.DataFrame(variant_rows)
    gate_df = pd.DataFrame(gate_rows)
    variant_df.to_csv(RUN_DIR / "parallel_rule_variant_index.csv", index=False)
    gate_df.to_csv(RUN_DIR / "parallel_rule_gate_scan.csv", index=False)
    if not gate_df.empty:
        story_summary = gate_df.groupby(["story", "verdict_v1"]).size().reset_index(name="n")
        story_summary.to_csv(RUN_DIR / "parallel_rule_story_counts.csv", index=False)
        candidate = gate_df[gate_df["verdict_v1"].eq("headline_candidate")].copy()
        candidate.sort_values(["story", "hazard", "transform", "N_model"], ascending=[True, True, True, False], inplace=True)
        candidate.to_csv(RUN_DIR / "parallel_rule_headline_candidates.csv", index=False)
    (RUN_DIR / "prereg_parallel_rules.md").write_text(
        "\n".join(
            [
                "# Parallel Rules Preregistration",
                "",
                f"Base data: {BASE_DTA}",
                "Starting scale: all rows in the base panel, not main_sample-only.",
                f"Rules: {', '.join(RULES)}",
                "Rules are treated as parallel toggles; sample_id identifies each rule combination.",
                "Transforms: raw and winsor_1_99 computed on the original 69,038-row panel.",
                "Specs: mean_root, mean_surface, dry_mdf_p10_sfc across drought/heat/hotdry.",
                "Inference at gate stage: two-way FE with grid-cluster robust standard errors.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"[COMPLETE] variants={len(variant_df)} gate_rows={len(gate_df)} elapsed={time.time()-start:.1f}s", flush=True)


if __name__ == "__main__":
    main()
