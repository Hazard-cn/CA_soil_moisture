"""
Biological timing-window screen for the fixed 128 main+GGCP10 sample variants.

The screen evaluates hazard main effects only. SR interactions are deliberately
excluded so that this is a predeclared biology-matching filter rather than an
SR-result filter.
"""

from __future__ import annotations

import itertools
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
BASE_DTA = PROJ / "temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_baseline_suite_analysis_ready.dta"
HOTDRY_DTA = PROJ / "data_build/data/processed/data_v3_main.dta"
OUT_DIR = PROJ / "temp/2026-06-02_parallel_rules_69038_story_search"

WINDOWS = ("full", "v3pre30", "v3pm10", "hepm10", "v3he", "hema")
SCREEN_WINDOWS = ("v3pre30", "v3pm10", "hepm10", "v3he", "hema")
OPTIONAL_RULES = (
    "zone_core",
    "yield_domain",
    "yield_jump",
    "sm_sd",
    "sm_coverage",
    "sr_within",
    "years_ge3",
    "stable_province",
)


BASE_COLUMNS = [
    "grid_id",
    "year",
    "main_sample",
    "province",
    "maize_zone",
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
    "gleam_smrz_sd",
    "era5l_swvl3_coverage",
    "D_v3pre30",
    "D_v3pm10",
    "D_hepm10",
    "D_v3he",
    "D_hema",
    "W_v3pre30",
    "W_v3pm10",
    "W_hepm10",
    "W_v3he",
    "W_hema",
    "hdd_ge32_v3pre30",
    "hdd_ge32_v3pm10",
    "hdd_ge32_hepm10",
    "hdd_ge32_v3he",
    "hdd_ge32_hema",
    "pr_sum_v3pre30",
    "pr_sum_v3pm10",
    "pr_sum_hepm10",
    "pr_sum_v3he",
    "pr_sum_hema",
    "et0_sum_v3pre30",
    "et0_sum_v3pm10",
    "et0_sum_hepm10",
    "et0_sum_v3he",
    "et0_sum_hema",
    "gdd_ge10_v3pre30",
    "gdd_ge10_v3pm10",
    "gdd_ge10_hepm10",
    "gdd_ge10_v3he",
    "gdd_ge10_hema",
]

HOTDRY_COLUMNS = [
    "grid_id",
    "year",
    "hotdrydays_ge32_pr_lt1",
    "hotdrydays_ge32_pr_lt1_v3pre30",
    "hotdrydays_ge32_pr_lt1_v3pm10",
    "hotdrydays_ge32_pr_lt1_hepm10",
    "hotdrydays_ge32_pr_lt1_v3he",
    "hotdrydays_ge32_pr_lt1_hema",
]


def var_for(prefix: str, window: str) -> str:
    if prefix == "D":
        return "D_full" if window == "full" else f"D_{window}"
    if prefix == "W":
        return "W_full" if window == "full" else f"W_{window}"
    if prefix == "H":
        return "hdd_ge32" if window == "full" else f"hdd_ge32_{window}"
    if prefix == "HD":
        return "HotDryPr_full" if window == "full" else f"HotDryPr_{window}"
    if prefix == "P":
        return "pr_sum" if window == "full" else f"pr_sum_{window}"
    if prefix == "ET0":
        return "et0_sum" if window == "full" else f"et0_sum_{window}"
    if prefix == "GDD":
        return "gdd_10_30" if window == "full" else f"gdd_ge10_{window}"
    raise ValueError(prefix)


def load_panel() -> pd.DataFrame:
    df = pd.read_stata(BASE_DTA, columns=BASE_COLUMNS)
    hd = pd.read_stata(HOTDRY_DTA, columns=HOTDRY_COLUMNS)
    df = df.merge(hd, on=["grid_id", "year"], how="left", validate="one_to_one")
    df.rename(
        columns={
            "hotdrydays_ge32_pr_lt1": "HotDryPr_full",
            "hotdrydays_ge32_pr_lt1_v3pre30": "HotDryPr_v3pre30",
            "hotdrydays_ge32_pr_lt1_v3pm10": "HotDryPr_v3pm10",
            "hotdrydays_ge32_pr_lt1_hepm10": "HotDryPr_hepm10",
            "hotdrydays_ge32_pr_lt1_v3he": "HotDryPr_v3he",
            "hotdrydays_ge32_pr_lt1_hema": "HotDryPr_hema",
        },
        inplace=True,
    )
    df["grid_code"] = pd.Categorical(df["grid_id"]).codes.astype(np.int64)
    df["year_code"] = pd.Categorical(df["year"]).codes.astype(np.int64)

    df.sort_values(["grid_id", "year"], inplace=True)
    df["dln_prev"] = np.nan
    df["dln_next"] = np.nan
    prev_same = (df["grid_id"].eq(df["grid_id"].shift(1))) & (df["year"].eq(df["year"].shift(1) + 1))
    next_same = (df["grid_id"].eq(df["grid_id"].shift(-1))) & (df["year"].shift(-1).eq(df["year"] + 1))
    df.loc[prev_same, "dln_prev"] = df.loc[prev_same, "ln_yield"] - df["ln_yield"].shift(1).loc[prev_same]
    df.loc[next_same, "dln_next"] = df["ln_yield"].shift(-1).loc[next_same] - df.loc[next_same, "ln_yield"]
    return df


def build_mask(df: pd.DataFrame, flags: dict[str, bool]) -> np.ndarray:
    mask = df["main_sample"].eq(1).to_numpy() & df["ggcp10_maize_frac"].ge(0.05).to_numpy()
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


def unique_variants(df: pd.DataFrame) -> list[dict[str, object]]:
    variants: list[dict[str, object]] = []
    seen: set[bytes] = set()
    for bits in itertools.product([False, True], repeat=len(OPTIONAL_RULES)):
        flags = dict(zip(OPTIONAL_RULES, bits))
        mask = build_mask(df, flags)
        key = np.packbits(mask).tobytes()
        if key in seen:
            continue
        seen.add(key)
        variants.append(
            {
                "sample_id": f"B{len(variants) + 1:03d}",
                "mask": mask,
                "N_sample": int(mask.sum()),
                "N_grids_sample": int(df.loc[mask, "grid_id"].nunique()),
                **{r: int(flags[r]) for r in OPTIONAL_RULES},
            }
        )
    return variants


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
    out: dict[str, float] = {"N_model": float(n), "N_grids_model": float(len(np.unique(gid)))}
    for i, xvar in enumerate(xvars):
        out[f"b:{xvar}"] = float(beta[i])
        out[f"se:{xvar}"] = float(se[i])
        zstat = abs(beta[i] / se[i]) if se[i] > 0 else np.inf
        out[f"p:{xvar}"] = float(2 * (1 - norm.cdf(zstat)))
    rss = float(np.sum(resid * resid))
    tss = float(np.sum((y - y.mean()) ** 2))
    out["r2_within"] = 1.0 - rss / tss if tss > 0 else math.nan
    return out


def xvars_for_window(window: str) -> list[str]:
    return [
        var_for("D", window),
        var_for("H", window),
        var_for("HD", window),
        var_for("W", window),
        "ca",
        var_for("P", window),
        var_for("ET0", window),
        var_for("GDD", window),
        "irr_frac",
        "aridity",
    ]


def hazard_coeff_rows(sample_meta: dict[str, object], window: str, res: dict[str, float]) -> list[dict[str, object]]:
    mapping = {
        "drought": var_for("D", window),
        "heat": var_for("H", window),
        "hotdry": var_for("HD", window),
    }
    rows: list[dict[str, object]] = []
    for hazard, xvar in mapping.items():
        b = res[f"b:{xvar}"]
        p = res[f"p:{xvar}"]
        rows.append(
            {
                "sample_id": sample_meta["sample_id"],
                "hazard": hazard,
                "window": window,
                "xvar": xvar,
                "coef": b,
                "se": res[f"se:{xvar}"],
                "p": p,
                "neg_sig_005": bool(b < 0 and p < 0.05),
                "N_sample": sample_meta["N_sample"],
                "N_model": int(res["N_model"]),
                "N_grids_sample": sample_meta["N_grids_sample"],
                "N_grids_model": int(res["N_grids_model"]),
                "r2_within": res["r2_within"],
            }
        )
    return rows


def decide_hazard(rows: pd.DataFrame, sample_id: str, hazard: str) -> dict[str, object]:
    h = rows[(rows["sample_id"].eq(sample_id)) & (rows["hazard"].eq(hazard))].set_index("window")
    b = h["coef"].to_dict()
    neg_sig = h["neg_sig_005"].to_dict()

    if hazard == "drought":
        placebo = ("v3pre30", "v3pm10")
        flowering_signal = bool(neg_sig["hepm10"])
        placebo_clean = not any(bool(neg_sig[w]) for w in placebo)
        rank_pass = bool(b["hepm10"] <= b["hema"] <= b["v3he"])
    elif hazard == "heat":
        placebo = ("v3pre30", "v3pm10", "v3he")
        flowering_signal = bool(neg_sig["hepm10"])
        placebo_clean = not any(bool(neg_sig[w]) for w in placebo)
        rank_pass = bool(b["hepm10"] <= b["hema"] and b["hepm10"] <= b["v3he"])
    elif hazard == "hotdry":
        placebo = ("v3pre30", "v3pm10")
        flowering_signal = bool(neg_sig["hepm10"])
        placebo_clean = not any(bool(neg_sig[w]) for w in placebo)
        rank_pass = bool(b["hepm10"] <= b["hema"])
    else:
        raise ValueError(hazard)

    core_pass = flowering_signal and placebo_clean
    strict_pass = core_pass and rank_pass
    if not flowering_signal:
        fail_reason = "hepm10_not_negative_significant"
    elif not placebo_clean:
        bad = [w for w in placebo if bool(neg_sig[w])]
        fail_reason = "placebo_negative_significant:" + ",".join(bad)
    elif not rank_pass:
        fail_reason = "biological_ordering_fail"
    else:
        fail_reason = "pass"
    return {
        "sample_id": sample_id,
        "hazard": hazard,
        "flowering_signal": flowering_signal,
        "placebo_clean": placebo_clean,
        "rank_pass": rank_pass,
        "core_pass": core_pass,
        "strict_pass": strict_pass,
        "fail_reason": fail_reason,
        "b_v3pre30": b["v3pre30"],
        "p_v3pre30": float(h.loc["v3pre30", "p"]),
        "b_v3pm10": b["v3pm10"],
        "p_v3pm10": float(h.loc["v3pm10", "p"]),
        "b_hepm10": b["hepm10"],
        "p_hepm10": float(h.loc["hepm10", "p"]),
        "b_v3he": b["v3he"],
        "p_v3he": float(h.loc["v3he", "p"]),
        "b_hema": b["hema"],
        "p_hema": float(h.loc["hema", "p"]),
    }


def write_summary(variant_df: pd.DataFrame, hazard_decisions: pd.DataFrame, sample_decisions: pd.DataFrame) -> None:
    hazard_counts = (
        hazard_decisions.groupby("hazard")
        .agg(
            n=("sample_id", "size"),
            flowering_fail=("flowering_signal", lambda s: int((~s).sum())),
            placebo_fail=("placebo_clean", lambda s: int((~s).sum())),
            rank_fail=("rank_pass", lambda s: int((~s).sum())),
            core_pass=("core_pass", "sum"),
            strict_pass=("strict_pass", "sum"),
        )
        .reset_index()
    )
    all_core_pass = int(sample_decisions["all_core_pass"].sum())
    all_strict_pass = int(sample_decisions["all_strict_pass"].sum())
    n_samples = len(sample_decisions)
    lines = [
        "# Biological timing-window filter for 128 main+GGCP10 sample variants",
        "",
        "固定样本前提：`main_sample == 1` 且 `ggcp10_maize_frac >= 0.05`；",
        "其余 8 个清洗规则平行排列组合后去重，得到 128 个唯一样本版本。",
        "",
        "模型口径：`ln_yield` 对同一窗口的 drought、heat、HotDryPr、wetness、`ca`、",
        "降水、ET0、GDD、灌溉和 aridity 做 grid FE + year FE 残差化 OLS；",
        "只检验 hazard 主效应，不纳入 SR 交互项。",
        "",
        "核心筛：`hepm10` 负向且 p<0.05，同时 placebo 窗口不能负向显著。",
        "严格筛：核心筛通过，并且窗口损伤排序符合生物学预期。",
        "",
        f"- 样本版本数：{n_samples}",
        f"- 全部三类 hazard 都通过核心筛：{all_core_pass}，筛掉 {n_samples - all_core_pass}",
        f"- 全部三类 hazard 都通过严格筛：{all_strict_pass}，筛掉 {n_samples - all_strict_pass}",
        "",
        "## By hazard",
        "",
        "| hazard | n | hepm10 fail | placebo fail | ordering fail | core pass | strict pass | strict drop |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in hazard_counts.to_dict("records"):
        strict_drop = int(row["n"] - row["strict_pass"])
        lines.append(
            f"| {row['hazard']} | {int(row['n'])} | {int(row['flowering_fail'])} | "
            f"{int(row['placebo_fail'])} | {int(row['rank_fail'])} | {int(row['core_pass'])} | "
            f"{int(row['strict_pass'])} | {strict_drop} |"
        )
    lines.extend(
        [
            "",
            "## Output files",
            "",
            "- `bio_window_128_variant_index.csv`",
            "- `bio_window_128_window_coefficients.csv`",
            "- `bio_window_128_hazard_decisions.csv`",
            "- `bio_window_128_sample_decisions.csv`",
            "- `bio_window_128_summary.md`",
            "",
        ]
    )
    (OUT_DIR / "bio_window_128_summary.md").write_text("\n".join(lines), encoding="utf-8")
    hazard_counts.to_csv(OUT_DIR / "bio_window_128_filter_summary.csv", index=False, encoding="utf-8-sig")
    variant_df.to_csv(OUT_DIR / "bio_window_128_variant_index.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_panel()
    variants = unique_variants(df)

    coef_rows: list[dict[str, object]] = []
    for i, meta in enumerate(variants, start=1):
        sub = df.loc[meta["mask"]].copy()
        for window in WINDOWS:
            res = fit_fe_ols(sub, "ln_yield", xvars_for_window(window))
            coef_rows.extend(hazard_coeff_rows(meta, window, res))
        if i % 16 == 0:
            print(f"processed {i}/{len(variants)} variants")

    coef_df = pd.DataFrame(coef_rows)
    coef_df.to_csv(OUT_DIR / "bio_window_128_window_coefficients.csv", index=False, encoding="utf-8-sig")

    decision_rows: list[dict[str, object]] = []
    for sample_id in coef_df["sample_id"].drop_duplicates():
        for hazard in ("drought", "heat", "hotdry"):
            decision_rows.append(decide_hazard(coef_df, str(sample_id), hazard))
    hazard_decisions = pd.DataFrame(decision_rows)
    hazard_decisions.to_csv(OUT_DIR / "bio_window_128_hazard_decisions.csv", index=False, encoding="utf-8-sig")

    sample_decisions = (
        hazard_decisions.groupby("sample_id")
        .agg(
            all_core_pass=("core_pass", "all"),
            all_strict_pass=("strict_pass", "all"),
            n_hazards_core_pass=("core_pass", "sum"),
            n_hazards_strict_pass=("strict_pass", "sum"),
        )
        .reset_index()
    )
    variant_df = pd.DataFrame([{k: v for k, v in meta.items() if k != "mask"} for meta in variants])
    sample_decisions = sample_decisions.merge(variant_df, on="sample_id", how="left", validate="one_to_one")
    sample_decisions.to_csv(OUT_DIR / "bio_window_128_sample_decisions.csv", index=False, encoding="utf-8-sig")
    write_summary(variant_df, hazard_decisions, sample_decisions)
    print(f"wrote outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
