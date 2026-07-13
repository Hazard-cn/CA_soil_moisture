"""
Fast cluster bootstrap for ggcp10 story S0 specifications.

This script consumes the frozen S0 panel produced by
scripts/stata/ggcp10_story_s0_spec_search_mean_drytop3.do and estimates the
same two fixed-effect equations with a matrix residualization routine. It is
used when Stata bootstrap with repeated reghdfe calls is too slow for the
spec-search workflow.
"""

from __future__ import annotations

import argparse
import math
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm


RUN_DIR = Path("temp/2026-06-02_story_s0_spec_search_mean_drytop3")
DATA_PATH = RUN_DIR / "story_s0_ready.dta"
GATE_PATH = RUN_DIR / "gate_scan_index.csv"


@dataclass(frozen=True)
class Spec:
    job_id: str
    branch: str
    mediator_tag: str
    mediator: str
    hazard: str
    transform: str = "raw"
    reps: int = 500
    stage: str = "promote"

    @property
    def set_id(self) -> str:
        transform_label = "winsor_1_99" if self.transform == "w" else self.transform
        return f"S0_fullnew_{transform_label}_{self.branch}_{self.mediator_tag}_{self.hazard}"


SPECS: tuple[Spec, ...] = (
    Spec("F101", "mean", "mean_root", "gleam_smrz_mean_raw", "drought"),
    Spec("F102", "mean", "mean_root", "gleam_smrz_mean_raw", "heat"),
    Spec("F103", "mean", "mean_root", "gleam_smrz_mean_raw", "hotdry"),
    Spec("F104", "dry", "dry_mdf_p10_sfc", "v6mdf_p10_fn_gss_raw", "drought"),
    Spec("F105", "dry", "dry_mdf_p10_sfc", "v6mdf_p10_fn_gss_raw", "hotdry"),
    Spec("F201", "mean", "mean_root", "gleam_smrz_mean_w", "drought", "w"),
    Spec("F204", "dry", "dry_mdf_p10_sfc", "v6mdf_p10_fn_gss_w", "drought", "w"),
)


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
    controls = [
        f"pr_sum_{sx}",
        f"et0_sum_{sx}",
        f"gdd_10_30_{sx}",
        f"irr_frac_{sx}",
        f"aridity_{sx}",
    ]
    if hazard == "drought":
        rhs_m = [d, ca, srd, w, h, *controls]
        rhs_y = [d, ca, srd, mediator, w, h, *controls]
        return y, ca, rhs_m, rhs_y, d, srd
    if hazard == "heat":
        rhs_m = [h, ca, srh, d, w, *controls]
        rhs_y = [h, ca, srh, mediator, d, w, *controls]
        return y, ca, rhs_m, rhs_y, h, srh
    if hazard == "hotdry":
        rhs_m = [hd, ca, srhd, d, h, w, *controls]
        rhs_y = [hd, ca, srhd, mediator, d, h, w, *controls]
        return y, ca, rhs_m, rhs_y, hd, srhd
    raise ValueError(f"unknown hazard: {hazard}")


def residualize_two_way(z: np.ndarray, gid: np.ndarray, year: np.ndarray, max_iter: int = 24) -> np.ndarray:
    """Residualize columns in z against group and year fixed effects."""
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
    yr = zr[:, 0]
    xr = zr[:, 1:]
    coef = np.linalg.lstsq(xr, yr, rcond=None)[0]
    return {x: float(coef[i]) for i, x in enumerate(xvars)}


def effects_from_coefs(
    coef_m: dict[str, float],
    coef_y: dict[str, float],
    main: str,
    inter: str,
    mediator: str,
    ca_values: dict[str, float],
) -> dict[tuple[str, str], float]:
    a1 = coef_m[main]
    a3 = coef_m[inter]
    b = coef_y[mediator]
    c1 = coef_y[main]
    c3 = coef_y[inter]
    out: dict[tuple[str, str], float] = {}
    for level, ca in ca_values.items():
        ie = (a1 + a3 * ca) * b
        de = c1 + c3 * ca
        out[("IE", level)] = float(ie)
        out[("DE", level)] = float(de)
        out[("TE", level)] = float(ie + de)
    return out


def bc_interval(samples: np.ndarray, point: float) -> tuple[float, float, float]:
    samples = samples[np.isfinite(samples)]
    if samples.size < 20:
        return math.nan, math.nan, math.nan
    se = float(np.std(samples, ddof=1))
    prop = float(np.mean(samples < point))
    prop = min(max(prop, 1.0 / (2.0 * samples.size)), 1.0 - 1.0 / (2.0 * samples.size))
    z0 = norm.ppf(prop)
    lo_pct = 100.0 * norm.cdf(2.0 * z0 + norm.ppf(0.025))
    hi_pct = 100.0 * norm.cdf(2.0 * z0 + norm.ppf(0.975))
    lo, hi = np.percentile(samples, [lo_pct, hi_pct])
    return se, float(lo), float(hi)


def bootstrap_spec(df: pd.DataFrame, spec: Spec, rng: np.random.Generator) -> tuple[pd.DataFrame, dict[str, float]]:
    y, ca, rhs_m, rhs_y, main, inter = rhs_for(spec.hazard, spec.transform, spec.mediator)
    needed = [y, ca, spec.mediator, *rhs_m, *rhs_y, "grid_id", "year_code", "grid_code"]
    base = df.loc[:, list(dict.fromkeys(needed))].dropna().copy()
    ca_values = {
        "P25": float(np.percentile(base[ca], 25)),
        "P50": float(np.percentile(base[ca], 50)),
        "P75": float(np.percentile(base[ca], 75)),
    }
    coef_m = ols_fe_coef(base, spec.mediator, rhs_m)
    coef_y = ols_fe_coef(base, y, rhs_y)
    point = effects_from_coefs(coef_m, coef_y, main, inter, spec.mediator, ca_values)

    grid_values = base["grid_id"].drop_duplicates().to_numpy()
    grid_to_pos = {int(g): i for i, g in enumerate(grid_values)}
    row_groups = [[] for _ in range(len(grid_values))]
    for pos, g in enumerate(base["grid_id"].to_numpy()):
        row_groups[grid_to_pos[int(g)]].append(pos)
    row_groups = [np.asarray(x, dtype=np.int64) for x in row_groups]

    draws: dict[tuple[str, str], list[float]] = {key: [] for key in point}
    failures = 0
    for _ in range(spec.reps):
        sampled = rng.integers(0, len(row_groups), size=len(row_groups), endpoint=False)
        pieces = [row_groups[i] for i in sampled]
        boot_idx = np.concatenate(pieces)
        boot = base.iloc[boot_idx].copy()
        boot["boot_grid"] = np.repeat(np.arange(len(sampled), dtype=np.int64), [len(row_groups[i]) for i in sampled])
        try:
            bm = ols_fe_coef(boot, spec.mediator, rhs_m, gid_var="boot_grid")
            by = ols_fe_coef(boot, y, rhs_y, gid_var="boot_grid")
            vals = effects_from_coefs(bm, by, main, inter, spec.mediator, ca_values)
            for key, val in vals.items():
                draws[key].append(val)
        except (np.linalg.LinAlgError, ValueError, FloatingPointError):
            failures += 1

    rows = []
    for (effect, level), point_est in point.items():
        arr = np.asarray(draws[(effect, level)], dtype=np.float64)
        se, lo, hi = bc_interval(arr, point_est)
        rows.append(
            {
                "job_id": spec.job_id,
                "set_id": spec.set_id,
                "branch": spec.branch,
                "mediator_tag": spec.mediator_tag,
                "hazard": spec.hazard,
                "transform": spec.transform,
                "boot_stage": spec.stage,
                "effect": effect,
                "ca_level": level,
                "point_est": point_est,
                "bs_se": se,
                "ci_lo": lo,
                "ci_hi": hi,
                "N_boot": int(arr.size),
                "N_model": int(len(base)),
                "failed_reps": int(failures),
            }
        )
    diag = {
        "N_model": float(len(base)),
        "N_grids": float(len(grid_values)),
        "failed_reps": float(failures),
    }
    return pd.DataFrame(rows), diag


def heterogeneity_points(df: pd.DataFrame, specs: tuple[Spec, ...], gate: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    splits = {
        "irr": ("irr_group", ["low_irr", "high_irr"]),
        "zone": ("maize_zone", ["NE", "HHH", "SW", "SH", "NW"]),
    }
    for spec in specs:
        y, ca, rhs_m, rhs_y, main, inter = rhs_for(spec.hazard, spec.transform, spec.mediator)
        stories = gate.loc[(gate["set_id"] == spec.set_id) & (gate["verdict_v2"] != "reject"), "story"].drop_duplicates().tolist()
        for split_name, (split_var, groups) in splits.items():
            for group in groups:
                sub = df.loc[df[split_var].astype(str) == group].copy()
                needed = [y, ca, spec.mediator, *rhs_m, *rhs_y, "grid_code", "year_code"]
                sub = sub.loc[:, list(dict.fromkeys(needed))].dropna()
                if len(sub) < 500:
                    continue
                ca50 = float(np.percentile(sub[ca], 50))
                coef_m = ols_fe_coef(sub, spec.mediator, rhs_m)
                coef_y = ols_fe_coef(sub, y, rhs_y)
                vals = effects_from_coefs(coef_m, coef_y, main, inter, spec.mediator, {"P50": ca50})
                for story in stories:
                    for effect in ("IE", "DE", "TE"):
                        rows.append(
                            {
                                "set_id": spec.set_id,
                                "branch": spec.branch,
                                "mediator_tag": spec.mediator_tag,
                                "hazard": spec.hazard,
                                "transform": spec.transform,
                                "split": split_name,
                                "group": group,
                                "story": story,
                                "effect": effect,
                                "ca_level": "P50",
                                "ca_value": ca50,
                                "estimate": vals[(effect, "P50")],
                                "N_model": int(len(sub)),
                            }
                        )
    return pd.DataFrame(rows)


def write_summary(run_dir: Path, boot: pd.DataFrame, hetero: pd.DataFrame, elapsed: float) -> None:
    clean = pd.read_csv(run_dir / "cleaning_log.csv")
    gate = pd.read_csv(run_dir / "gate_scan_index.csv")
    lines = [
        "# story S0 fast bootstrap recommendation",
        "",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Runtime seconds: {elapsed:.1f}",
        "",
        "## S0 cleaning waterfall",
        "",
    ]
    for row in clean.itertuples(index=False):
        lines.append(f"- {row.step}: {int(row.N_before)} -> {int(row.N_after)}; drop={int(row.N_drop)}; grids={int(row.grids_after)}")
    lines.extend(["", "## Gate scan", ""])
    verdict = gate.groupby(["story", "verdict_v2"]).size().reset_index(name="n")
    for row in verdict.itertuples(index=False):
        lines.append(f"- {row.story} / {row.verdict_v2}: {int(row.n)}")
    lines.extend(["", "## Bootstrap completed", ""])
    for sid, sub in boot.groupby("set_id", sort=False):
        lines.append(f"- {sid}: reps={int(sub['N_boot'].min())}, N={int(sub['N_model'].iloc[0])}, failed_reps={int(sub['failed_reps'].max())}")
        p50 = sub[sub["ca_level"] == "P50"].set_index("effect")
        if {"IE", "DE", "TE"}.issubset(set(p50.index)):
            lines.append(
                "  "
                + "; ".join(
                    f"{eff}={p50.loc[eff, 'point_est']:.6g} [{p50.loc[eff, 'ci_lo']:.6g}, {p50.loc[eff, 'ci_hi']:.6g}]"
                    for eff in ("IE", "DE", "TE")
                )
            )
    lines.extend(["", "## Story reading", ""])
    lines.append("严格 v2 规则下，当前结果只能进入 suggestive_bounded / exploratory-only，不应标为 headline；原因是这些候选仍来自同一探索批次，且 1000 次 final bootstrap 与留出年/留出产区确认尚未完成。")
    lines.append("较完整的可讲线索集中在 mean_root 的 drought 与 hotdry，以及 dry_mdf_p10_sfc 的 drought/hotdry；heat 的 mean_root 更适合作为 A_common_pathway 的补充，不宜单独承担 buffering 故事。")
    lines.extend(["", "## Heterogeneity file", ""])
    lines.append(f"heterogeneity rows: {len(hetero)}")
    (run_dir / "story_recommendation_fast.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=RUN_DIR)
    parser.add_argument("--reps", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42000)
    parser.add_argument("--jobs", default="", help="Comma-separated job ids to run, for example F101,F104.")
    parser.add_argument("--stage", default="promote", help="Bootstrap stage label written to output.")
    parser.add_argument("--output", default="bootstrap_fast_promote.csv", help="Output CSV name under run-dir.")
    args = parser.parse_args()

    start = time.time()
    run_dir = args.run_dir
    df = pd.read_stata(run_dir / DATA_PATH.name)
    df = df[df["s0"] == 1].copy()
    df["year_code"] = pd.Categorical(df["year"]).codes.astype(np.int64)
    df["grid_code"] = pd.Categorical(df["grid_id"]).codes.astype(np.int64)
    gate = pd.read_csv(run_dir / GATE_PATH.name)
    requested = {x.strip() for x in args.jobs.split(",") if x.strip()}
    source_specs = tuple(s for s in SPECS if not requested or s.job_id in requested)
    specs = tuple(Spec(s.job_id, s.branch, s.mediator_tag, s.mediator, s.hazard, s.transform, args.reps, args.stage) for s in source_specs)
    if not specs:
        raise SystemExit("No matching jobs requested.")

    out_parts = []
    rng = np.random.default_rng(args.seed)
    for spec in specs:
        spec_start = time.time()
        print(f"[BOOT] {spec.job_id} {spec.set_id} reps={spec.reps}", flush=True)
        boot, diag = bootstrap_spec(df, spec, rng)
        out_parts.append(boot)
        print(
            f"[BOOT-DONE] {spec.job_id} seconds={time.time() - spec_start:.1f} "
            f"N={int(diag['N_model'])} grids={int(diag['N_grids'])} failed={int(diag['failed_reps'])}",
            flush=True,
        )
        pd.concat(out_parts, ignore_index=True).to_csv(run_dir / args.output, index=False)

    boot_all = pd.concat(out_parts, ignore_index=True)
    hetero = heterogeneity_points(df, specs, gate)
    hetero.to_csv(run_dir / "heterogeneity_fast.csv", index=False)
    write_summary(run_dir, boot_all, hetero, time.time() - start)
    print(f"[COMPLETE] seconds={time.time() - start:.1f}", flush=True)


if __name__ == "__main__":
    main()
