"""
Create a four-row family-level coefficient brief from all RHS coefficient summaries.

This is a compression layer on top of story_family_all_coefficients_summary.csv.
It does not rerun regressions and does not alter raw sign/significance states.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
RUN_DIR = PROJ / "temp/2026-06-02_parallel_rules_69038_story_search"
SUMMARY_CSV = RUN_DIR / "story_family_all_coefficients_summary.csv"
MEMBERSHIP_CSV = RUN_DIR / "story_family_all_coefficients_membership.csv"
OUT_CSV = RUN_DIR / "story_family_four_row_coefficient_brief.csv"
OUT_MD = PROJ / "quality_reports/2026-06-04_story_family_four_row_coefficient_brief.md"

STABLE_SHARE = 0.90
VOLATILE_SHARE = 0.75
OPPOSITE_SIGN_SHARE = 0.20

RULE_COLS = [
    "zone_core",
    "yield_domain",
    "yield_jump",
    "sm_sd",
    "sm_coverage",
    "sr_within",
    "years_ge3",
    "stable_province",
]


def compact_counts(series: pd.Series, max_items: int = 8) -> str:
    counts = series.astype(str).value_counts()
    parts = [f"{idx}:{int(val)}" for idx, val in counts.head(max_items).items()]
    if len(counts) > max_items:
        parts.append(f"other:{int(counts.iloc[max_items:].sum())}")
    return "; ".join(parts)


def compact_terms(df: pd.DataFrame, max_items: int = 12) -> str:
    if df.empty:
        return ""
    labels = (
        df["role"].astype(str)
        + "|"
        + df["equation"].astype(str)
        + "|"
        + df["hazard"].astype(str)
        + "|"
        + df["branch"].astype(str)
        + "|"
        + df["subgroup_dim"].astype(str)
        + ":"
        + df["subgroup"].astype(str)
        + "|"
        + df["term"].astype(str)
    )
    counts = labels.value_counts()
    parts = [f"{idx}({int(val)})" for idx, val in counts.head(max_items).items()]
    if len(counts) > max_items:
        parts.append(f"other({int(counts.iloc[max_items:].sum())})")
    return "; ".join(parts)


def rule_profile(group: pd.DataFrame) -> str:
    fixed: list[str] = []
    varying: list[str] = []
    for col in RULE_COLS:
        vals = sorted(group[col].dropna().astype(int).unique().tolist())
        if len(vals) == 1:
            fixed.append(f"{col}={vals[0]}")
        else:
            varying.append(col)
    return f"fixed: {', '.join(fixed) if fixed else 'none'}; varying: {', '.join(varying) if varying else 'none'}"


def add_shares(summary: pd.DataFrame) -> pd.DataFrame:
    s = summary.copy()
    n = s["n_observed"].astype(float).replace(0.0, float("nan"))
    for col in [
        "neg_sig_010",
        "pos_sig_010",
        "neg_ns_010",
        "pos_ns_010",
        "zero_010",
    ]:
        s[f"{col}_share"] = s[col].astype(float).div(n).fillna(0.0)
    s["positive_total_share"] = s["pos_sig_010_share"] + s["pos_ns_010_share"]
    s["negative_total_share"] = s["neg_sig_010_share"] + s["neg_ns_010_share"]
    s["sig_total_share"] = s["pos_sig_010_share"] + s["neg_sig_010_share"]
    return s


def family_row(family_id: str, summary: pd.DataFrame, membership: pd.DataFrame) -> dict[str, object]:
    sf = summary.loc[summary["family_id"].eq(family_id)].copy()
    mf = membership.loc[membership["family_id"].eq(family_id)].copy()

    stable = sf.loc[sf["dominant_share_010"].ge(STABLE_SHARE) & sf["n_observed"].gt(0)].copy()
    stable_pos_sig = stable.loc[stable["dominant_state_010"].eq("positive_sig")]
    stable_neg_sig = stable.loc[stable["dominant_state_010"].eq("negative_sig")]
    stable_ns = stable.loc[stable["dominant_state_010"].isin(["positive_ns", "negative_ns", "zero"])]

    volatile = sf.loc[
        sf["n_observed"].gt(0)
        & (
            sf["dominant_share_010"].lt(VOLATILE_SHARE)
            | (
                sf["positive_total_share"].ge(OPPOSITE_SIGN_SHARE)
                & sf["negative_total_share"].ge(OPPOSITE_SIGN_SHARE)
            )
        )
    ].copy()
    sign_flip = volatile.loc[
        volatile["positive_total_share"].ge(OPPOSITE_SIGN_SHARE)
        & volatile["negative_total_share"].ge(OPPOSITE_SIGN_SHARE)
    ]
    sig_mixed = sf.loc[
        sf["n_observed"].gt(0)
        & sf["sig_total_share"].between(0.25, 0.75, inclusive="both")
    ]
    missing = sf.loc[sf["n_missing"].gt(0)]

    stable_share = len(stable) / len(sf) if len(sf) else 0.0
    volatile_share = len(volatile) / len(sf) if len(sf) else 0.0

    return {
        "family_id": family_id,
        "n_scales": int(mf["sample_id"].nunique()),
        "sample_ids": ", ".join(mf["sample_id"].tolist()),
        "rule_profile": rule_profile(mf),
        "n_coefficient_cells": int(len(sf)),
        "stable_cells_010": int(len(stable)),
        "stable_cell_share_010": round(stable_share, 4),
        "stable_positive_sig_010": f"n={len(stable_pos_sig)}; roles={compact_counts(stable_pos_sig['role'])}; examples={compact_terms(stable_pos_sig)}",
        "stable_negative_sig_010": f"n={len(stable_neg_sig)}; roles={compact_counts(stable_neg_sig['role'])}; examples={compact_terms(stable_neg_sig)}",
        "stable_non_sig_or_zero_010": f"n={len(stable_ns)}; states={compact_counts(stable_ns['dominant_state_010'])}; roles={compact_counts(stable_ns['role'])}; examples={compact_terms(stable_ns)}",
        "volatile_cells_010": int(len(volatile)),
        "volatile_cell_share_010": round(volatile_share, 4),
        "variation_mark": (
            f"large_change={len(volatile)}; sign_flip_like={len(sign_flip)}; "
            f"sig_mixed={len(sig_mixed)}; missing_cells={len(missing)}"
        ),
        "variation_by_role": compact_counts(volatile["role"]),
        "variation_by_layer_subgroup": compact_counts(
            volatile["layer"].astype(str) + "|" + volatile["subgroup_dim"].astype(str) + ":" + volatile["subgroup"].astype(str)
        ),
        "variation_by_hazard_branch": compact_counts(
            volatile["hazard"].astype(str) + "|" + volatile["branch"].astype(str) + "|" + volatile["equation"].astype(str)
        ),
        "variation_examples": compact_terms(volatile),
        "missing_mark": compact_counts(
            missing["layer"].astype(str) + "|" + missing["subgroup_dim"].astype(str) + ":" + missing["subgroup"].astype(str)
        ),
        "story_use_note": (
            "先使用 stable_positive/negative_sig 作为该 family 的可陈述系数背景；"
            "variation_mark 中的项只能写成 family 内分化或不稳定，不能写成统一结论。"
        ),
    }


def write_md(out: pd.DataFrame) -> None:
    lines: list[str] = [
        "# 四类 Family 全系数四行摘要",
        "",
        "生成日期: 2026-06-04",
        "",
        "## 口径",
        "",
        f"输入文件为 `{SUMMARY_CSV}`，没有重新回归。每行 family 摘要都覆盖全部 RHS 系数，包括关键机制项、SR 主效应、companion hazard、气候控制变量和其他协变量。`dominant_share_010 >= {STABLE_SHARE}` 记为稳定；`dominant_share_010 < {VOLATILE_SHARE}` 或正负方向两侧占比都不低于 `{OPPOSITE_SIGN_SHARE}` 记为变化较大。显著性口径为 `p<0.10`。",
        "",
        "## 输出文件",
        "",
        f"- `{OUT_CSV}`: 四行 CSV，每行一个 family。",
        "",
        "## 字段阅读",
        "",
        "`stable_positive_sig_010`、`stable_negative_sig_010` 和 `stable_non_sig_or_zero_010` 是把非常一致的系数压缩成一格；其中 `roles=` 给出 role 分布，`examples=` 给出最常出现的系数标签。`variation_mark` 给出变化大单元数量、近似正负翻转数量、显著性混合数量和缺失单元数量。`variation_by_role`、`variation_by_layer_subgroup`、`variation_by_hazard_branch` 用于定位变化来自哪类方程、异质性组、hazard 或 mediator branch。",
        "",
        "## 四类摘要",
        "",
    ]
    for _, row in out.iterrows():
        lines.extend(
            [
                f"### {row['family_id']}",
                "",
                f"- scale 数: {row['n_scales']}",
                f"- 规则特征: {row['rule_profile']}",
                f"- 稳定单元: {row['stable_cells_010']} / {row['n_coefficient_cells']} ({row['stable_cell_share_010']})",
                f"- 变化较大单元: {row['variation_mark']}",
                f"- 变化来源 role: {row['variation_by_role']}",
                f"- 变化来源 subgroup: {row['variation_by_layer_subgroup']}",
                f"- 变化来源 hazard/branch/equation: {row['variation_by_hazard_branch']}",
                "",
            ]
        )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    summary = pd.read_csv(SUMMARY_CSV)
    membership = pd.read_csv(MEMBERSHIP_CSV)
    summary = add_shares(summary)
    rows = [family_row(fid, summary, membership) for fid in sorted(membership["family_id"].unique())]
    out = pd.DataFrame(rows)
    if len(out) != 4:
        raise RuntimeError(f"Expected four family rows, got {len(out)}")
    out.to_csv(OUT_CSV, index=False, encoding="utf-8")
    write_md(out)
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")
    print(out[["family_id", "n_scales", "stable_cells_010", "volatile_cells_010", "variation_mark"]].to_string(index=False))


if __name__ == "__main__":
    main()
