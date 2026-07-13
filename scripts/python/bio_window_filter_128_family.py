"""
Hazard-family version of the biological timing-window screen.

Compared with bio_window_filter_128.py, drought and heat are screened in their
own family equations. HotDryPr remains conditional on drought and heat because
its interpretation is compound hot-dry exposure beyond the two component
hazards.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from bio_window_filter_128 import (
    OUT_DIR,
    WINDOWS,
    decide_hazard,
    fit_fe_ols,
    hazard_coeff_rows,
    load_panel,
    unique_variants,
    var_for,
)


PREFIX = "bio_window_128_family"
SCREEN_WINDOWS = ("v3pre30", "v3pm10", "hepm10", "v3he", "hema")


def xvars_for_family(window: str, hazard: str) -> list[str]:
    controls = [
        "ca",
        var_for("P", window),
        var_for("ET0", window),
        var_for("GDD", window),
        "irr_frac",
        "aridity",
    ]
    if hazard == "drought":
        return [var_for("D", window), var_for("W", window), var_for("H", window), *controls]
    if hazard == "heat":
        return [var_for("H", window), var_for("D", window), var_for("W", window), *controls]
    if hazard == "hotdry":
        return [
            var_for("HD", window),
            var_for("D", window),
            var_for("H", window),
            var_for("W", window),
            *controls,
        ]
    raise ValueError(hazard)


def coeff_row(sample_meta: dict[str, object], hazard: str, window: str, res: dict[str, float]) -> dict[str, object]:
    xvar = {"drought": var_for("D", window), "heat": var_for("H", window), "hotdry": var_for("HD", window)}[hazard]
    b = res[f"b:{xvar}"]
    p = res[f"p:{xvar}"]
    return {
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


def write_family_summary(variant_df: pd.DataFrame, hazard_decisions: pd.DataFrame, sample_decisions: pd.DataFrame) -> None:
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
    hazard_counts.to_csv(OUT_DIR / f"{PREFIX}_filter_summary.csv", index=False, encoding="utf-8-sig")
    variant_df.to_csv(OUT_DIR / f"{PREFIX}_variant_index.csv", index=False, encoding="utf-8-sig")

    n_samples = len(sample_decisions)
    all_core_pass = int(sample_decisions["all_core_pass"].sum())
    all_strict_pass = int(sample_decisions["all_strict_pass"].sum())
    lines = [
        "# Biological timing-window filter, hazard-family equations",
        "",
        "固定样本前提：`main_sample == 1` 且 `ggcp10_maize_frac >= 0.05`。",
        "128 个唯一样本版本来自其余 8 个清洗规则的平行排列组合去重。",
        "",
        "模型口径：drought 和 heat 分别使用本 hazard 的 family 方程；",
        "HotDryPr 方程控制 drought 与 heat 分量。全部模型为 grid FE + year FE 残差化 OLS，",
        "只筛 hazard 主效应窗口，不纳入 SR 交互项。",
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
            f"- `{PREFIX}_variant_index.csv`",
            f"- `{PREFIX}_window_coefficients.csv`",
            f"- `{PREFIX}_hazard_decisions.csv`",
            f"- `{PREFIX}_sample_decisions.csv`",
            f"- `{PREFIX}_filter_summary.csv`",
            f"- `{PREFIX}_summary.md`",
            "",
        ]
    )
    (OUT_DIR / f"{PREFIX}_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    df = load_panel()
    variants = unique_variants(df)
    rows: list[dict[str, object]] = []
    for i, meta in enumerate(variants, start=1):
        sub = df.loc[meta["mask"]].copy()
        for window in WINDOWS:
            for hazard in ("drought", "heat", "hotdry"):
                res = fit_fe_ols(sub, "ln_yield", xvars_for_family(window, hazard))
                rows.append(coeff_row(meta, hazard, window, res))
        if i % 16 == 0:
            print(f"processed {i}/{len(variants)} variants")

    coef_df = pd.DataFrame(rows)
    coef_df.to_csv(OUT_DIR / f"{PREFIX}_window_coefficients.csv", index=False, encoding="utf-8-sig")

    decision_rows: list[dict[str, object]] = []
    for sample_id in coef_df["sample_id"].drop_duplicates():
        for hazard in ("drought", "heat", "hotdry"):
            decision_rows.append(decide_hazard(coef_df, str(sample_id), hazard))
    hazard_decisions = pd.DataFrame(decision_rows)
    hazard_decisions.to_csv(OUT_DIR / f"{PREFIX}_hazard_decisions.csv", index=False, encoding="utf-8-sig")

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
    sample_decisions.to_csv(OUT_DIR / f"{PREFIX}_sample_decisions.csv", index=False, encoding="utf-8-sig")
    write_family_summary(variant_df, hazard_decisions, sample_decisions)
    print(f"wrote outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
