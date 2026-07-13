"""Follow-up margins for story-line matching.

This script does not re-estimate regressions. It converts existing coefficient
outputs into scenario quantities that are easier to interpret in the manuscript.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

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
    unique_variants,
)


OUT_DIR = PROJ / "temp/2026-06-18_story_followup_margins"
REPORT = PROJ / "quality_reports/2026-06-18_story_followup_margins.md"
REGION_DIR = PROJ / "temp/2026-06-11_region_first_story_search"
F4_BOOT_DIR = PROJ / "temp/2026-06-04_f4_b067_full_bootstrap_counterfactual"

HAZARD_VAR = {
    "drought": "D_full_raw",
    "heat": "hdd_ge32_raw",
    "hotdry": "HotDryPr_full_raw",
}
IRR_SCALES = ("G057", "G185", "G049", "G177")
PHENO_SCALES = ("G057", "G185", "G255", "G049", "G177")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def pct_from_ln(x: float) -> float:
    if not math.isfinite(x):
        return math.nan
    return math.expm1(x) * 100.0


def fmt_float(value: object, digits: int = 4) -> str:
    try:
        x = float(value)
    except Exception:
        return str(value)
    if not math.isfinite(x):
        return ""
    if abs(x) >= 100:
        return f"{x:.1f}"
    if abs(x) >= 1:
        return f"{x:.3f}"
    return f"{x:.{digits}f}"


def markdown_table(df: pd.DataFrame, max_rows: int = 30) -> str:
    if df.empty:
        return "_empty_"
    view = df.head(max_rows).copy()
    cols = list(view.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "|" + "|".join("---" for _ in cols) + "|",
    ]
    for _, row in view.iterrows():
        vals = []
        for col in cols:
            val = row[col]
            if isinstance(val, (float, int, np.floating, np.integer)):
                vals.append(fmt_float(val))
            else:
                vals.append(str(val).replace("\n", " ").replace("|", "/"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def variant_index(panel: pd.DataFrame) -> dict[str, dict[str, object]]:
    return {str(meta["sample_id"]): meta for meta in unique_variants(panel)}


def irrigation_margins() -> pd.DataFrame:
    panel = add_full_interactions(load_panel())
    variants = variant_index(panel)
    coeff = read_csv(REGION_DIR / "all_highscore_irrigation_cluster.csv")
    coeff = coeff.loc[coeff["sample_id"].isin(IRR_SCALES)].copy()
    rows: list[dict[str, object]] = []
    for scale in IRR_SCALES:
        if scale not in variants:
            continue
        sub = panel.loc[variants[scale]["mask"]].copy()
        complete_base = sub.dropna(subset=["ca_raw", "irr_frac_raw"]).copy()
        ca_p25, ca_p50, ca_p75 = np.nanpercentile(complete_base["ca_raw"], [25, 50, 75])
        irr_p25, irr_p50, irr_p75 = np.nanpercentile(complete_base["irr_frac_raw"], [25, 50, 75])
        for hazard, hvar in HAZARD_VAR.items():
            c = coeff.loc[(coeff["sample_id"].eq(scale)) & (coeff["hazard"].eq(hazard))]
            if c.empty:
                continue
            c = c.iloc[0]
            complete = sub.dropna(subset=["ca_raw", "irr_frac_raw", hvar]).copy()
            hazard_p90 = float(np.nanpercentile(complete[hvar], 90))
            ca_iqr = float(ca_p75 - ca_p25)
            base_c3 = float(c["base_c3"])
            triple = float(c["triple"])
            for irr_label, irr_value in (
                ("P25", float(irr_p25)),
                ("P50", float(irr_p50)),
                ("P75", float(irr_p75)),
            ):
                marginal_c3 = base_c3 + triple * irr_value
                ln_buffer = marginal_c3 * ca_iqr * hazard_p90
                rows.append(
                    {
                        "scale": scale,
                        "hazard": hazard,
                        "irr_level": irr_label,
                        "irr_value": irr_value,
                        "ca_p25": ca_p25,
                        "ca_p50": ca_p50,
                        "ca_p75": ca_p75,
                        "ca_iqr": ca_iqr,
                        "hazard_p90": hazard_p90,
                        "base_c3": base_c3,
                        "triple": triple,
                        "triple_p": float(c["triple_p"]),
                        "marginal_c3": marginal_c3,
                        "ln_yield_buffer_at_hazard_p90": ln_buffer,
                        "pct_yield_buffer_at_hazard_p90": pct_from_ln(ln_buffer),
                    }
                )
            ln_diff = triple * (float(irr_p75) - float(irr_p25)) * ca_iqr * hazard_p90
            rows.append(
                {
                    "scale": scale,
                    "hazard": hazard,
                    "irr_level": "P75_minus_P25",
                    "irr_value": float(irr_p75 - irr_p25),
                    "ca_p25": ca_p25,
                    "ca_p50": ca_p50,
                    "ca_p75": ca_p75,
                    "ca_iqr": ca_iqr,
                    "hazard_p90": hazard_p90,
                    "base_c3": base_c3,
                    "triple": triple,
                    "triple_p": float(c["triple_p"]),
                    "marginal_c3": math.nan,
                    "ln_yield_buffer_at_hazard_p90": ln_diff,
                    "pct_yield_buffer_at_hazard_p90": pct_from_ln(ln_diff),
                }
            )
    return pd.DataFrame(rows)


def phenology_margins() -> pd.DataFrame:
    window_panel = add_window_terms(load_window_panel())
    variants = variant_index(window_panel)
    pheno = read_csv(REGION_DIR / "all_highscore_phenology_cluster.csv")
    pheno = pheno.loc[pheno["sample_id"].isin(PHENO_SCALES)].copy()
    rows: list[dict[str, object]] = []
    for scale in PHENO_SCALES:
        if scale not in variants:
            continue
        sub = window_panel.loc[variants[scale]["mask"]].copy()
        ca_p25, ca_p50, ca_p75 = np.nanpercentile(sub["ca"].dropna(), [25, 50, 75])
        for _, row in pheno.loc[pheno["sample_id"].eq(scale)].iterrows():
            beta = float(row["beta_DH"])
            gamma = float(row["gamma_SRDH"])
            for ca_label, ca_value in (
                ("P25", float(ca_p25)),
                ("P50", float(ca_p50)),
                ("P75", float(ca_p75)),
            ):
                slope = beta + gamma * ca_value
                rows.append(
                    {
                        "scale": scale,
                        "window": row["window"],
                        "ca_level": ca_label,
                        "ca_value": ca_value,
                        "beta_DH": beta,
                        "beta_DH_p": float(row["beta_DH_p"]),
                        "gamma_SRDH": gamma,
                        "gamma_SRDH_p": float(row["gamma_SRDH_p"]),
                        "dh_slope_at_ca": slope,
                        "slope_sign": "negative" if slope < 0 else "positive",
                        "N_model": int(row["N_model"]),
                    }
                )
            rows.append(
                {
                    "scale": scale,
                    "window": row["window"],
                    "ca_level": "P75_minus_P25",
                    "ca_value": float(ca_p75 - ca_p25),
                    "beta_DH": beta,
                    "beta_DH_p": float(row["beta_DH_p"]),
                    "gamma_SRDH": gamma,
                    "gamma_SRDH_p": float(row["gamma_SRDH_p"]),
                    "dh_slope_at_ca": gamma * float(ca_p75 - ca_p25),
                    "slope_sign": "less_negative_shift" if gamma > 0 else "more_negative_shift",
                    "N_model": int(row["N_model"]),
                }
            )
    return pd.DataFrame(rows)


def b067_iede_delta() -> tuple[pd.DataFrame, pd.DataFrame]:
    unified = read_csv(F4_BOOT_DIR / "f4_b067_mean_raw_unified_coefficients_effects.csv")
    levels = unified.loc[
        unified["sample_id"].eq("B067")
        & unified["layer"].eq("baseline")
        & unified["subgroup_dim"].eq("all")
        & unified["subgroup"].eq("all")
        & unified["transform"].eq("raw")
        & unified["branch"].eq("mean")
        & unified["mediator_tag"].eq("mean")
        & unified["record_type"].eq("iede_effect")
        & unified["effect"].isin(["IE", "DE", "TE"])
        & unified["ca_level"].isin(["P25", "P50", "P75"])
    ].copy()
    levels = levels[
        [
            "hazard",
            "effect",
            "ca_level",
            "estimate",
            "bs_ci_lo_95",
            "bs_ci_hi_95",
            "N_boot",
        ]
    ].sort_values(["hazard", "effect", "ca_level"])

    cf = unified.loc[
        unified["sample_id"].eq("B067")
        & unified["layer"].eq("baseline")
        & unified["subgroup_dim"].eq("all")
        & unified["subgroup"].eq("all")
        & unified["transform"].eq("raw")
        & unified["branch"].eq("mean")
        & unified["mediator_tag"].eq("mean")
        & unified["record_type"].eq("counterfactual")
        & unified["scenario"].eq("hazard_P90_ca_P75_minus_P25")
        & unified["effect"].eq("pct_delta")
    ].copy()
    cf = cf[
        [
            "hazard",
            "delta_te_point",
            "hazard_level",
            "delta_ln_yield_point",
            "delta_ln_yield_ci_lo",
            "delta_ln_yield_ci_hi",
            "pct_delta_point",
            "pct_delta_ci_lo",
            "pct_delta_ci_hi",
            "N_boot",
        ]
    ].sort_values(["hazard"])
    for col in ["pct_delta_point", "pct_delta_ci_lo", "pct_delta_ci_hi"]:
        cf[f"{col}_percent"] = cf[col].astype(float) * 100.0
    return levels, cf


def write_report(irr: pd.DataFrame, pheno: pd.DataFrame, levels: pd.DataFrame, cf: pd.DataFrame) -> None:
    irr_focus = irr.loc[
        irr["scale"].isin(["G057", "G185"])
        & irr["irr_level"].isin(["P25", "P75", "P75_minus_P25"])
    ].copy()
    pheno_focus = pheno.loc[
        pheno["scale"].isin(["G057", "G185", "G255"])
        & pheno["window"].isin(["hepm10", "hema"])
        & pheno["ca_level"].isin(["P25", "P75", "P75_minus_P25"])
    ].copy()
    cf_focus = cf.copy()
    lines = [
        "# Story follow-up margins",
        "",
        "日期：2026-06-18",
        "",
        "## 结论",
        "",
        "本轮没有重新估计模型，只把既有 coefficient 输出转换为可解释的 margins。最适合进入正文的结果是：`G057/G185` 的 region-first 故事仍然成立，灌溉连续异质性最强的可写结论是 heat/hotdry buffering 随 irrigation 上升而减弱，物候期联合热旱结论集中在 `HE±10` 和 `HE-MA`。",
        "",
        "## 灌溉连续异质性 margins",
        "",
        "表中 `pct_yield_buffer_at_hazard_p90` 表示在该 scale 内，从 SR P25 到 SR P75、hazard=P90 时对应的 ln yield 变化换算百分比。`P75_minus_P25` 行表示灌溉从 P25 到 P75 对该 SR-buffering margin 的改变。",
        "",
        markdown_table(
            irr_focus[
                [
                    "scale",
                    "hazard",
                    "irr_level",
                    "irr_value",
                    "triple",
                    "triple_p",
                    "marginal_c3",
                    "pct_yield_buffer_at_hazard_p90",
                ]
            ],
            40,
        ),
        "",
        "解读：heat 和 hotdry 的 `P75_minus_P25` 为负，说明高灌溉条件下 SR 的边际缓冲空间下降；drought 的 `P75_minus_P25` 为正，但 p 值在 0.10 附近，适合谨慎写作。",
        "",
        "## 物候期联合热旱斜率",
        "",
        "`dh_slope_at_ca = beta_DH + gamma_SRDH × SR_q`。负值表示 D×H 联合项仍对应损失斜率，`P75_minus_P25` 表示从低 SR 到高 SR 后 D×H 损失斜率向零移动的幅度。",
        "",
        markdown_table(
            pheno_focus[
                [
                    "scale",
                    "window",
                    "ca_level",
                    "ca_value",
                    "beta_DH",
                    "gamma_SRDH",
                    "dh_slope_at_ca",
                    "slope_sign",
                ]
            ],
            40,
        ),
        "",
        "解读：`HE±10` 的 D×H 基础损失和 SR×D×H 缓冲最稳定；`HE-MA` 在 `G057/G185` 下也符合方向。`G255` 是严格 endpoint 的候选，但 `HEMA` 的 beta_DH 本身不显著，因此更适合作为 sensitivity。",
        "",
        "## B067 baseline IE/DE/TE",
        "",
        markdown_table(
            levels[
                [
                    "hazard",
                    "effect",
                    "ca_level",
                    "estimate",
                    "bs_ci_lo_95",
                    "bs_ci_hi_95",
                ]
            ],
            40,
        ),
        "",
        "## B067 TE(P75)-TE(P25) at hazard P90",
        "",
        markdown_table(
            cf_focus[
                [
                    "hazard",
                    "delta_te_point",
                    "hazard_level",
                    "delta_ln_yield_point",
                    "pct_delta_point_percent",
                    "pct_delta_ci_lo_percent",
                    "pct_delta_ci_hi_percent",
                    "N_boot",
                ]
            ],
            20,
        ),
        "",
        "写作边界：B067 的 TE/IE/DE 只能作为 association decomposition；灌溉连续 triple 和物候期 D×H 模型是更适合支撑主线的异质性证据。最终正式表格仍建议用 Stata `reghdfe` 对 G057/G185/G195 的少数最终规格复核。",
        "",
        "## 输出",
        "",
        "- `irrigation_standardized_margins.csv`",
        "- `phenology_srdh_margins.csv`",
        "- `b067_iede_levels.csv`",
        "- `b067_iede_delta.csv`",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    irr = irrigation_margins()
    pheno = phenology_margins()
    levels, cf = b067_iede_delta()
    irr.to_csv(OUT_DIR / "irrigation_standardized_margins.csv", index=False, encoding="utf-8-sig")
    pheno.to_csv(OUT_DIR / "phenology_srdh_margins.csv", index=False, encoding="utf-8-sig")
    levels.to_csv(OUT_DIR / "b067_iede_levels.csv", index=False, encoding="utf-8-sig")
    cf.to_csv(OUT_DIR / "b067_iede_delta.csv", index=False, encoding="utf-8-sig")
    write_report(irr, pheno, levels, cf)


if __name__ == "__main__":
    main()
