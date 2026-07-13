"""Expanded GGCP10 scale search beyond the fixed Bxxx sample base."""

from __future__ import annotations

import itertools
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from bio_window_filter_128 import load_panel as load_window_panel
from bio_window_filter_128 import var_for
from ggcp10_parallel_rules_69038_search import (
    fit_fe_cluster,
    fit_fe_ols,
    load_panel,
    rhs_for,
)


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
OUT_DIR = PROJ / "temp/2026-06-11_expanded_scale_story_search"
REPORT = PROJ / "quality_reports/2026-06-11_expanded_scale_story_search.md"

RULES = (
    "main_sample",
    "zone_core",
    "yield_domain",
    "yield_jump",
    "sm_sd",
    "sm_coverage",
    "sr_within",
    "years_ge3",
    "stable_province",
)
HAZARDS = ("drought", "heat", "hotdry")
WINDOWS = ("full", "v3he", "hepm10", "hema")
MIN_N = 500


def build_mask(df: pd.DataFrame, flags: dict[str, bool]) -> np.ndarray:
    mask = df["ggcp10_maize_frac"].ge(0.05).to_numpy().copy()
    if flags["main_sample"]:
        mask &= df["main_sample"].eq(1).to_numpy()
    if flags["zone_core"]:
        mask &= ~df["maize_zone"].astype(str).eq("Other").to_numpy()
    if flags["yield_domain"]:
        mask &= df["yield_tons_ha"].ge(0.5).to_numpy()
        mask &= df["yield_tons_ha"].lt(18).to_numpy()
    if flags["yield_jump"]:
        jump = df["dln_prev"].abs().gt(1).fillna(False)
        jump |= df["dln_next"].abs().gt(1).fillna(False)
        mask &= ~jump.to_numpy()
    if flags["sm_sd"]:
        mask &= df["gleam_smrz_sd"].ge(0.001).to_numpy()
    if flags["sm_coverage"]:
        mask &= df["era5l_swvl3_coverage"].ge(0.90).to_numpy()

    if flags["sr_within"] or flags["years_ge3"] or flags["stable_province"]:
        tmp = df.loc[mask, ["grid_id", "ca_ratio", "year", "province"]].copy()
        keep = pd.Series(True, index=tmp["grid_id"].drop_duplicates().to_numpy())
        if flags["sr_within"]:
            stats = tmp.groupby("grid_id")["ca_ratio"].agg(["count", "std"])
            valid = (stats["count"] >= 2) & stats["std"].gt(0)
            keep &= valid.reindex(keep.index, fill_value=False)
        if flags["years_ge3"]:
            valid = tmp.groupby("grid_id")["year"].nunique().ge(3)
            keep &= valid.reindex(keep.index, fill_value=False)
        if flags["stable_province"]:
            valid = tmp.groupby("grid_id")["province"].nunique(dropna=True).le(1)
            keep &= valid.reindex(keep.index, fill_value=False)
        mask &= df["grid_id"].isin(keep[keep].index).to_numpy()
    return mask


def unique_variants(df: pd.DataFrame) -> list[dict[str, object]]:
    variants: list[dict[str, object]] = []
    seen: set[bytes] = set()
    for bits in itertools.product([False, True], repeat=len(RULES)):
        flags = dict(zip(RULES, bits))
        mask = build_mask(df, flags)
        key = np.packbits(mask).tobytes()
        if key in seen:
            continue
        seen.add(key)
        variants.append(
            {
                "sample_id": f"G{len(variants) + 1:03d}",
                "mask": mask,
                "N_sample": int(mask.sum()),
                "N_grids_sample": int(df.loc[mask, "grid_id"].nunique()),
                "active_rule_count": int(sum(flags.values())),
                **{rule: int(flags[rule]) for rule in RULES},
            }
        )
    return variants


def add_full_interactions(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["D_x_H"] = out["D_full_raw"] * out["hdd_ge32_raw"]
    out["SR_x_D_x_H"] = out["ca_raw"] * out["D_x_H"]
    for moderator in ("irr_frac_raw", "aridity_raw"):
        suffix = "irr" if moderator.startswith("irr") else "ari"
        out[f"SR_x_{suffix}"] = out["ca_raw"] * out[moderator]
        for hazard, hvar in (
            ("drought", "D_full_raw"),
            ("heat", "hdd_ge32_raw"),
            ("hotdry", "HotDryPr_full_raw"),
        ):
            out[f"{hazard}_x_{suffix}"] = out[hvar] * out[moderator]
            out[f"SR_x_{hazard}_x_{suffix}"] = out["ca_raw"] * out[hvar] * out[moderator]
    return out


def baseline_result(sub: pd.DataFrame, hazard: str, fit_fn) -> dict[str, object]:
    mediator = "gleam_smrz_mean_raw"
    y, ca, rhs_m, rhs_y, main, inter = rhs_for(hazard, "raw", mediator)
    fm = fit_fn(sub, mediator, rhs_m)
    fy = fit_fn(sub, y, rhs_y)
    ca25, ca75 = np.nanpercentile(sub[ca], [25, 75])
    a1 = fm[f"b:{main}"]
    a3 = fm[f"b:{inter}"]
    b = fy[f"b:{mediator}"]
    c1 = fy[f"b:{main}"]
    c3 = fy[f"b:{inter}"]
    te25 = (a1 + a3 * ca25) * b + c1 + c3 * ca25
    te75 = (a1 + a3 * ca75) * b + c1 + c3 * ca75
    return {
        "hazard": hazard,
        "a1": a1,
        "a1_p": fm[f"p:{main}"],
        "a3": a3,
        "a3_p": fm[f"p:{inter}"],
        "b": b,
        "b_p": fy[f"p:{mediator}"],
        "c1": c1,
        "c1_p": fy[f"p:{main}"],
        "c3": c3,
        "c3_p": fy[f"p:{inter}"],
        "te25": te25,
        "te75": te75,
        "te_slope": a3 * b + c3,
        "N_model": int(fm["N"] if "N" in fm else fm["N_model"]),
        "N_grids": int(fm["clusters"] if "clusters" in fm else fm["N_grids_model"]),
    }


def compound_result(sub: pd.DataFrame, fit_fn) -> dict[str, object]:
    xvars = [
        "D_full_raw",
        "hdd_ge32_raw",
        "D_x_H",
        "ca_raw",
        "SR_x_D_full_raw",
        "SR_x_Heat_full_raw",
        "SR_x_D_x_H",
        "W_full_raw",
        "pr_sum_raw",
        "et0_sum_raw",
        "gdd_10_30_raw",
        "irr_frac_raw",
        "aridity_raw",
    ]
    res = fit_fn(sub, "ln_yield_raw", xvars)
    return {
        "beta_DH": res["b:D_x_H"],
        "beta_DH_p": res["p:D_x_H"],
        "gamma_SRDH": res["b:SR_x_D_x_H"],
        "gamma_SRDH_p": res["p:SR_x_D_x_H"],
        "N_model": int(res["N"] if "N" in res else res["N_model"]),
        "N_grids": int(res["clusters"] if "clusters" in res else res["N_grids_model"]),
    }


def moderator_result(sub: pd.DataFrame, hazard: str, moderator: str, fit_fn) -> dict[str, object]:
    suffix = "irr" if moderator == "irr_frac_raw" else "ari"
    if hazard == "drought":
        main = "D_full_raw"
        inter = "SR_x_D_full_raw"
        companions = ["W_full_raw", "hdd_ge32_raw"]
    elif hazard == "heat":
        main = "hdd_ge32_raw"
        inter = "SR_x_Heat_full_raw"
        companions = ["D_full_raw", "W_full_raw"]
    else:
        main = "HotDryPr_full_raw"
        inter = "SR_x_HotDryPr_full_raw"
        companions = ["D_full_raw", "hdd_ge32_raw", "W_full_raw"]
    triple = f"SR_x_{hazard}_x_{suffix}"
    xvars = [
        main,
        "ca_raw",
        moderator,
        inter,
        f"{hazard}_x_{suffix}",
        f"SR_x_{suffix}",
        triple,
        *companions,
        "pr_sum_raw",
        "et0_sum_raw",
        "gdd_10_30_raw",
    ]
    if moderator != "irr_frac_raw":
        xvars.append("irr_frac_raw")
    if moderator != "aridity_raw":
        xvars.append("aridity_raw")
    res = fit_fn(sub, "ln_yield_raw", list(dict.fromkeys(xvars)))
    return {
        "hazard": hazard,
        "moderator": suffix,
        "triple": res[f"b:{triple}"],
        "triple_p": res[f"p:{triple}"],
        "base_c3": res[f"b:{inter}"],
        "base_c3_p": res[f"p:{inter}"],
        "N_model": int(res["N"] if "N" in res else res["N_model"]),
        "N_grids": int(res["clusters"] if "clusters" in res else res["N_grids_model"]),
    }


def hazard_window_vars(hazard: str, window: str) -> tuple[str, str, list[str]]:
    d = var_for("D", window)
    h = var_for("H", window)
    w = var_for("W", window)
    if hazard == "drought":
        return d, f"SR_x_{d}", [w, h]
    if hazard == "heat":
        return h, f"SR_x_{h}", [d, w]
    hd = var_for("HD", window)
    return hd, f"SR_x_{hd}", [d, h, w]


def add_window_terms(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for window in WINDOWS:
        d = var_for("D", window)
        h = var_for("H", window)
        out[f"D_x_H_{window}"] = out[d] * out[h]
        out[f"SR_x_D_x_H_{window}"] = out["ca"] * out[f"D_x_H_{window}"]
        for hazard in HAZARDS:
            main, inter, _ = hazard_window_vars(hazard, window)
            out[inter] = out["ca"] * out[main]
    return out


def phenology_rows(window_df: pd.DataFrame, variants: list[dict[str, object]], selected: list[str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    indexed = {v["sample_id"]: v for v in variants}
    for sample_id in selected:
        meta = indexed[sample_id]
        sub = window_df.loc[meta["mask"]].copy()
        for window in WINDOWS:
            d = var_for("D", window)
            h = var_for("H", window)
            xvars = [
                d,
                h,
                f"D_x_H_{window}",
                "ca",
                f"SR_x_{d}",
                f"SR_x_{h}",
                f"SR_x_D_x_H_{window}",
                var_for("W", window),
                var_for("P", window),
                var_for("ET0", window),
                var_for("GDD", window),
                "irr_frac",
                "aridity",
            ]
            try:
                res = fit_fe_cluster(sub, "ln_yield", xvars)
            except Exception as exc:
                rows.append({"sample_id": sample_id, "window": window, "status": str(exc)})
                continue
            rows.append(
                {
                    "sample_id": sample_id,
                    "window": window,
                    "status": "estimated",
                    "beta_DH": res[f"b:D_x_H_{window}"],
                    "beta_DH_p": res[f"p:D_x_H_{window}"],
                    "gamma_SRDH": res[f"b:SR_x_D_x_H_{window}"],
                    "gamma_SRDH_p": res[f"p:SR_x_D_x_H_{window}"],
                    "N_model": int(res["N"]),
                    "N_grids": int(res["clusters"]),
                }
            )
    return rows


def scan() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base = add_full_interactions(load_panel())
    variants = unique_variants(base)
    index_rows = [{k: v for k, v in meta.items() if k != "mask"} for meta in variants]
    baseline_rows: list[dict[str, object]] = []
    compound_rows: list[dict[str, object]] = []
    modifier_rows: list[dict[str, object]] = []
    for i, meta in enumerate(variants, start=1):
        sub = base.loc[meta["mask"]].copy()
        common = {k: v for k, v in meta.items() if k != "mask"}
        for hazard in HAZARDS:
            baseline_rows.append({**common, **baseline_result(sub, hazard, fit_fe_ols)})
            modifier_rows.append(
                {**common, **moderator_result(sub, hazard, "irr_frac_raw", fit_fe_ols)}
            )
        compound_rows.append({**common, **compound_result(sub, fit_fe_ols)})
        if i % 16 == 0:
            print(f"[SCAN] {i}/{len(variants)}", flush=True)
    return (
        pd.DataFrame(index_rows),
        pd.DataFrame(baseline_rows),
        pd.DataFrame(compound_rows),
        pd.DataFrame(modifier_rows),
    )


def select_candidates(index: pd.DataFrame, baseline: pd.DataFrame, compound: pd.DataFrame, modifier: pd.DataFrame) -> pd.DataFrame:
    b = baseline.copy()
    b["phys_ok"] = (b["a1"] < 0) & (b["b"] > 0)
    b["buffer_ok"] = (b["te_slope"] > 0) & (b["c3"] > 0) & (b["c3_p"] < 0.10)
    bg = b.groupby("sample_id").agg(
        phys_n=("phys_ok", "sum"),
        buffer_n=("buffer_ok", "sum"),
        min_te_slope=("te_slope", "min"),
    )
    cg = compound.set_index("sample_id").copy()
    cg["compound_strict"] = (
        (cg["beta_DH"] < 0)
        & (cg["beta_DH_p"] < 0.10)
        & (cg["gamma_SRDH"] > 0)
        & (cg["gamma_SRDH_p"] < 0.10)
    )
    cg["compound_modifier"] = (cg["gamma_SRDH"] > 0) & (cg["gamma_SRDH_p"] < 0.10)
    iw = modifier.pivot(index="sample_id", columns="hazard", values=["triple", "triple_p"])
    iw.columns = [f"{a}_{b}" for a, b in iw.columns]
    iw["irrigation_reallocation"] = (
        (iw["triple_drought"] > 0)
        & (iw["triple_heat"] < 0)
        & ((iw["triple_p_drought"] < 0.10) | (iw["triple_p_heat"] < 0.10))
    )
    out = index.set_index("sample_id").join(bg).join(
        cg[["beta_DH", "beta_DH_p", "gamma_SRDH", "gamma_SRDH_p", "compound_strict", "compound_modifier"]]
    ).join(iw)
    out["state_buffering"] = (out["phys_n"] == 3) & (out["buffer_n"] >= 2)
    out["story_score"] = (
        out["state_buffering"].astype(int)
        + out["compound_strict"].astype(int)
        + out["irrigation_reallocation"].astype(int)
    )
    out.reset_index(inplace=True)
    return out.sort_values(
        ["story_score", "N_sample", "active_rule_count"],
        ascending=[False, False, True],
    )


def chosen_ids(candidates: pd.DataFrame) -> list[str]:
    selected: list[str] = []
    gates = (
        candidates["state_buffering"] & candidates["compound_strict"] & candidates["irrigation_reallocation"],
        candidates["state_buffering"] & candidates["compound_strict"],
        candidates["state_buffering"] & candidates["irrigation_reallocation"],
        candidates["state_buffering"],
    )
    for gate in gates:
        match = candidates.loc[gate].sort_values(
            ["N_sample", "active_rule_count"], ascending=[False, True]
        )
        if not match.empty and match.iloc[0]["sample_id"] not in selected:
            selected.append(str(match.iloc[0]["sample_id"]))
    for sample_id in candidates.head(6)["sample_id"]:
        if sample_id not in selected:
            selected.append(str(sample_id))
        if len(selected) >= 6:
            break
    return selected


def cluster_validate(
    base: pd.DataFrame,
    variants: list[dict[str, object]],
    selected: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    indexed = {v["sample_id"]: v for v in variants}
    baseline_rows: list[dict[str, object]] = []
    compound_rows: list[dict[str, object]] = []
    modifier_rows: list[dict[str, object]] = []
    for sample_id in selected:
        meta = indexed[sample_id]
        sub = base.loc[meta["mask"]].copy()
        common = {k: v for k, v in meta.items() if k != "mask"}
        for hazard in HAZARDS:
            baseline_rows.append({**common, **baseline_result(sub, hazard, fit_fe_cluster)})
            modifier_rows.append(
                {**common, **moderator_result(sub, hazard, "irr_frac_raw", fit_fe_cluster)}
            )
        compound_rows.append({**common, **compound_result(sub, fit_fe_cluster)})
    return pd.DataFrame(baseline_rows), pd.DataFrame(compound_rows), pd.DataFrame(modifier_rows)


def write_report(
    index: pd.DataFrame,
    candidates: pd.DataFrame,
    selected: list[str],
    cb: pd.DataFrame,
    cc: pd.DataFrame,
    cm: pd.DataFrame,
    pheno: pd.DataFrame,
    elapsed: float,
) -> None:
    top = candidates.head(12)
    lines = [
        "# 扩展 Scale 故事线搜索",
        "",
        "日期：2026-06-11",
        "",
        "## 搜索范围",
        "",
        f"- 固定 `ggcp10_maize_frac >= 0.05` 后形成 {len(index)} 个唯一 `Gxxx` scale。",
        f"- 最大 scale 为 {index.loc[index.N_sample.idxmax(), 'sample_id']}，N={int(index.N_sample.max()):,}。",
        "- 全量门槛扫描使用两向固定效应 OLS；入选 scale 另用 `grid_id` 聚类标准误复核。",
        "",
        "## OLS 门槛排序前 12 个 scale",
        "",
        "| scale | N | grids | rules | score | state | compound | irrigation |",
        "|---|---:|---:|---:|---:|---|---|---|",
    ]
    for _, row in top.iterrows():
        lines.append(
            f"| {row.sample_id} | {int(row.N_sample):,} | {int(row.N_grids_sample):,} | "
            f"{int(row.active_rule_count)} | {int(row.story_score)} | "
            f"{bool(row.state_buffering)} | {bool(row.compound_strict)} | "
            f"{bool(row.irrigation_reallocation)} |"
        )
    lines += [
        "",
        "## 聚类复核候选",
        "",
        f"候选 scale：{', '.join(selected)}。",
        "",
        "### Baseline",
        "",
        cb.to_csv(index=False),
        "",
        "### Compound",
        "",
        cc.to_csv(index=False),
        "",
        "### Continuous irrigation modifier",
        "",
        cm.to_csv(index=False),
        "",
        "### Phenology compound model",
        "",
        pheno.to_csv(index=False),
        "",
        "## 说明",
        "",
        "- `HotDryPr` 与连续 `D × H` 分开报告。",
        "- OLS 门槛只用于缩小候选范围，最终判断以聚类复核为准。",
        "- 若聚类复核未保留同方向和区间，本轮扩展 scale 不升级为主结果。",
        f"- 运行耗时：{elapsed:.1f} 秒。",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index, baseline, compound, modifier = scan()
    candidates = select_candidates(index, baseline, compound, modifier)
    selected = chosen_ids(candidates)

    index.to_csv(OUT_DIR / "expanded_scale_index.csv", index=False, encoding="utf-8-sig")
    baseline.to_csv(OUT_DIR / "expanded_baseline_ols.csv", index=False, encoding="utf-8-sig")
    compound.to_csv(OUT_DIR / "expanded_compound_ols.csv", index=False, encoding="utf-8-sig")
    modifier.to_csv(OUT_DIR / "expanded_irrigation_modifier_ols.csv", index=False, encoding="utf-8-sig")
    candidates.to_csv(OUT_DIR / "expanded_candidate_ranking.csv", index=False, encoding="utf-8-sig")

    base = add_full_interactions(load_panel())
    variants = unique_variants(base)
    cb, cc, cm = cluster_validate(base, variants, selected)
    cb.to_csv(OUT_DIR / "selected_baseline_cluster.csv", index=False, encoding="utf-8-sig")
    cc.to_csv(OUT_DIR / "selected_compound_cluster.csv", index=False, encoding="utf-8-sig")
    cm.to_csv(OUT_DIR / "selected_irrigation_modifier_cluster.csv", index=False, encoding="utf-8-sig")

    window_df = add_window_terms(load_window_panel())
    window_variants = unique_variants(window_df)
    pheno = pd.DataFrame(phenology_rows(window_df, window_variants, selected))
    pheno.to_csv(OUT_DIR / "selected_phenology_compound_cluster.csv", index=False, encoding="utf-8-sig")

    elapsed = time.time() - start
    write_report(index, candidates, selected, cb, cc, cm, pheno, elapsed)
    manifest = {
        "n_unique_scales": int(len(index)),
        "selected": selected,
        "elapsed_seconds": elapsed,
        "outputs": sorted(p.name for p in OUT_DIR.iterdir() if p.is_file()),
    }
    (OUT_DIR / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(manifest)


if __name__ == "__main__":
    main()
