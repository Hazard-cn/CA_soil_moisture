"""
Run grid-mean AI dry-sample regressions for the locked 128 Bxxx scales.

AI definition:
    ai_pet_over_p_year = et0_sum / pr_sum
    ai_pet_over_p_gridmean = mean(ai_pet_over_p_year) by grid_id

Runs:
    - AI > 2: irrigation heterogeneity within dry grids.
    - AI > 5: pooled extreme-dry baseline only.

This script reuses the existing two-way FE OLS regression functions and the
existing four-family membership. It does not redo story-family clustering.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd

from bio_window_filter_128 import unique_variants
from coefficient_distribution_all128 import HAZARDS, MEDIATORS, TRANSFORMS, attempt_rows_for_spec, fit_spec_rows
from ggcp10_parallel_rules_69038_search import load_panel
from story_family_all_coefficients import build_full_summary, validate_outputs
from story_family_coefficient_grouped_list import annotate, build_grouped


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
RUN_DIR = PROJ / "temp/2026-06-02_parallel_rules_69038_story_search"
MEMBERSHIP_CSV = RUN_DIR / "story_family_all_coefficients_membership.csv"
EXISTING_SUMMARY_CSV = RUN_DIR / "story_family_all_coefficients_summary.csv"
REPORT_MD = PROJ / "quality_reports/2026-06-04_gridmean_ai_dry_sample_runs.md"

PREFIX_SUPPORT = "gridmean_ai_dry_support"
PREFIX_GT2 = "gridmean_ai_gt2_irrigation"
PREFIX_GT5 = "gridmean_ai_gt5_pooled"
COMPARE_NAME = "gridmean_ai_compare_vs_existing"

GT2_THRESHOLD = 2.0
GT5_THRESHOLD = 5.0
SUBGROUPS_GT2 = ("high_irr", "low_irr")


def add_gridmean_ai(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ai_pet_over_p_year"] = out["et0_sum"] / out["pr_sum"]
    grid_ai = (
        out.groupby("grid_id", as_index=False)["ai_pet_over_p_year"]
        .mean()
        .rename(columns={"ai_pet_over_p_year": "ai_pet_over_p_gridmean"})
    )
    out = out.merge(grid_ai, on="grid_id", how="left", validate="many_to_one")
    max_within = out.groupby("grid_id")["ai_pet_over_p_gridmean"].nunique(dropna=False).max()
    if int(max_within) != 1:
        raise RuntimeError("ai_pet_over_p_gridmean is not grid-fixed.")
    return out


def build_variant_table(df: pd.DataFrame, limit_scales: int | None = None) -> pd.DataFrame:
    variants = unique_variants(df)
    if limit_scales is not None:
        variants = variants[:limit_scales]
    rows = []
    for variant in variants:
        row = {k: v for k, v in variant.items() if k != "mask"}
        row["_mask"] = variant["mask"]
        rows.append(row)
    return pd.DataFrame(rows)


def build_support(df: pd.DataFrame, variants: pd.DataFrame, membership: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    family_lookup = membership.set_index("sample_id")[["family_id", "family_size"]].to_dict("index")
    for _, variant in variants.iterrows():
        sample_id = str(variant["sample_id"])
        base = df.loc[variant["_mask"]].copy()
        for label, threshold in (("gt2", GT2_THRESHOLD), ("gt5", GT5_THRESHOLD)):
            sub = base.loc[base["ai_pet_over_p_gridmean"].gt(threshold)].copy()
            high = sub.loc[sub["irr_group"].astype(str).eq("high_irr")]
            low = sub.loc[sub["irr_group"].astype(str).eq("low_irr")]
            rows.append(
                {
                    "sample_id": sample_id,
                    "family_id": family_lookup[sample_id]["family_id"],
                    "family_size": family_lookup[sample_id]["family_size"],
                    "threshold_label": label,
                    "threshold_rule": f"ai_pet_over_p_gridmean > {threshold:g}",
                    "threshold_value": threshold,
                    "N_rows": int(len(sub)),
                    "N_grids": int(sub["grid_id"].nunique()),
                    "high_irr_rows": int(len(high)),
                    "high_irr_grids": int(high["grid_id"].nunique()),
                    "low_irr_rows": int(len(low)),
                    "low_irr_grids": int(low["grid_id"].nunique()),
                }
            )
    return pd.DataFrame(rows)


def run_specs_for_subset(
    sub: pd.DataFrame,
    sample_id: str,
    layer: str,
    subgroup_dim: str,
    subgroup: str,
    threshold_label: str,
    threshold_value: float,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    detail_rows: list[dict[str, object]] = []
    skipped_rows: list[dict[str, object]] = []
    attempt_rows: list[dict[str, object]] = []
    for hazard in HAZARDS:
        for transform in TRANSFORMS:
            for mediator_tag in MEDIATORS:
                attempt_rows.extend(
                    attempt_rows_for_spec(
                        sample_id,
                        layer,
                        subgroup_dim,
                        subgroup,
                        hazard,
                        transform,
                        mediator_tag,
                        len(sub),
                    )
                )
                rows, skipped = fit_spec_rows(
                    sub,
                    sample_id,
                    layer,
                    subgroup_dim,
                    subgroup,
                    hazard,
                    transform,
                    mediator_tag,
                )
                for row in rows:
                    row["threshold_label"] = threshold_label
                    row["threshold_value"] = threshold_value
                    row["threshold_rule"] = f"ai_pet_over_p_gridmean > {threshold_value:g}"
                for row in skipped:
                    row["threshold_label"] = threshold_label
                    row["threshold_value"] = threshold_value
                    row["threshold_rule"] = f"ai_pet_over_p_gridmean > {threshold_value:g}"
                detail_rows.extend(rows)
                skipped_rows.extend(skipped)
    return detail_rows, skipped_rows, attempt_rows


def run_all(df: pd.DataFrame, variants: pd.DataFrame, membership: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    family_lookup = membership.set_index("sample_id")[["family_id", "family_size"]].to_dict("index")
    gt2_rows: list[dict[str, object]] = []
    gt5_rows: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    attempts: list[dict[str, object]] = []
    started = time.time()

    for i, (_, variant) in enumerate(variants.iterrows(), start=1):
        sample_id = str(variant["sample_id"])
        base = df.loc[variant["_mask"]].copy()

        dry2 = base.loc[base["ai_pet_over_p_gridmean"].gt(GT2_THRESHOLD)].copy()
        for subgroup in SUBGROUPS_GT2:
            sub = dry2.loc[dry2["irr_group"].astype(str).eq(subgroup)].copy()
            rows, skip, att = run_specs_for_subset(
                sub,
                sample_id,
                "heterogeneity",
                "irr_group",
                subgroup,
                "gt2",
                GT2_THRESHOLD,
            )
            gt2_rows.extend(rows)
            skipped.extend(skip)
            attempts.extend(att)

        dry5 = base.loc[base["ai_pet_over_p_gridmean"].gt(GT5_THRESHOLD)].copy()
        rows, skip, att = run_specs_for_subset(
            dry5,
            sample_id,
            "baseline",
            "all",
            "all",
            "gt5",
            GT5_THRESHOLD,
        )
        gt5_rows.extend(rows)
        skipped.extend(skip)
        attempts.extend(att)

        if i == 1 or i % 8 == 0 or i == len(variants):
            elapsed = time.time() - started
            print(
                f"processed {i}/{len(variants)} scales; "
                f"gt2_rows={len(gt2_rows)} gt5_rows={len(gt5_rows)} skipped={len(skipped)} elapsed={elapsed:.1f}s",
                flush=True,
            )

    gt2 = pd.DataFrame(gt2_rows)
    gt5 = pd.DataFrame(gt5_rows)
    skipped_df = pd.DataFrame(skipped)
    attempts_df = pd.DataFrame(attempts)
    for data in (gt2, gt5):
        if data.empty:
            continue
        data["family_id"] = data["sample_id"].map(lambda x: family_lookup[x]["family_id"])
        data["family_size"] = data["sample_id"].map(lambda x: family_lookup[x]["family_size"])
        ordered = ["family_id", "family_size", "threshold_label", "threshold_value", "threshold_rule", *[c for c in data.columns if c not in {"family_id", "family_size", "threshold_label", "threshold_value", "threshold_rule"}]]
        data = data[ordered]
    if not gt2.empty:
        gt2 = gt2[["family_id", "family_size", "threshold_label", "threshold_value", "threshold_rule", *[c for c in gt2.columns if c not in {"family_id", "family_size", "threshold_label", "threshold_value", "threshold_rule"}]]]
    if not gt5.empty:
        gt5 = gt5[["family_id", "family_size", "threshold_label", "threshold_value", "threshold_rule", *[c for c in gt5.columns if c not in {"family_id", "family_size", "threshold_label", "threshold_value", "threshold_rule"}]]]
    return gt2, gt5, skipped_df, attempts_df


def summarize(detail: pd.DataFrame, membership: pd.DataFrame) -> pd.DataFrame:
    if detail.empty:
        return pd.DataFrame()
    summary = build_full_summary(detail, membership)
    return summary


def write_grouped(summary: pd.DataFrame, prefix: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    annotated = annotate(summary)
    grouped = build_grouped(annotated)
    annotated.to_csv(RUN_DIR / f"{prefix}_annotated_cells.csv", index=False, encoding="utf-8")
    grouped.to_csv(RUN_DIR / f"{prefix}_grouped_list.csv", index=False, encoding="utf-8")
    return annotated, grouped


def compare_with_existing(gt2_summary: pd.DataFrame, gt5_summary: pd.DataFrame) -> pd.DataFrame:
    existing = pd.read_csv(EXISTING_SUMMARY_CSV)
    rows = []
    compare_jobs = [
        ("gt2_irrigation_vs_all_region_irrigation", gt2_summary, {"layer": "heterogeneity", "subgroup_dim": "irr_group"}),
        ("gt5_pooled_vs_full_sample_baseline", gt5_summary, {"layer": "baseline", "subgroup_dim": "all", "subgroup": "all"}),
    ]
    key_cols = [
        "family_id",
        "layer",
        "subgroup_dim",
        "subgroup",
        "hazard",
        "transform",
        "branch",
        "mediator_tag",
        "mediator",
        "equation",
        "depvar",
        "term",
        "role",
    ]
    for comparison, new, filters in compare_jobs:
        old = existing.copy()
        for col, value in filters.items():
            old = old.loc[old[col].astype(str).eq(str(value))]
        merged = new.merge(
            old[key_cols + ["dominant_state_010", "dominant_share_010", "median_coef", "n_observed"]],
            on=key_cols,
            how="left",
            suffixes=("_new", "_old"),
        )
        for _, row in merged.iterrows():
            old_state = "" if pd.isna(row["dominant_state_010_old"]) else str(row["dominant_state_010_old"])
            new_state = "" if pd.isna(row["dominant_state_010_new"]) else str(row["dominant_state_010_new"])
            if old_state == "":
                change = "old_missing"
            elif old_state == new_state:
                change = "same_state"
            elif old_state.split("_")[0] != new_state.split("_")[0]:
                change = "sign_changed"
            elif old_state.split("_")[-1] != new_state.split("_")[-1]:
                change = "sig_changed"
            else:
                change = "state_changed"
            rows.append(
                {
                    "comparison": comparison,
                    **{col: row[col] for col in key_cols},
                    "old_dominant_state_010": old_state,
                    "new_dominant_state_010": new_state,
                    "old_dominant_share_010": row["dominant_share_010_old"],
                    "new_dominant_share_010": row["dominant_share_010_new"],
                    "old_median_coef": row["median_coef_old"],
                    "new_median_coef": row["median_coef_new"],
                    "old_n_observed": row["n_observed_old"],
                    "new_n_observed": row["n_observed_new"],
                    "change_type": change,
                }
            )
    return pd.DataFrame(rows)


def validate_summary(
    summary: pd.DataFrame,
    expected_subgroup_dim: str,
    expected_layer: str,
    expected_families: set[str],
) -> None:
    if summary.empty:
        raise RuntimeError("summary is empty")
    if set(summary["family_id"].unique()) != expected_families:
        raise RuntimeError(f"family coverage mismatch: {sorted(summary['family_id'].unique())}")
    if set(summary["subgroup_dim"].unique()) != {expected_subgroup_dim}:
        raise RuntimeError(f"subgroup_dim mismatch: {summary['subgroup_dim'].unique()}")
    if set(summary["layer"].unique()) != {expected_layer}:
        raise RuntimeError(f"layer mismatch: {summary['layer'].unique()}")
    if not summary["n_family_scales"].eq(summary["n_observed"] + summary["n_missing"]).all():
        raise RuntimeError("n_family_scales identity failed")
    rhs_005 = summary[["neg_sig_005", "pos_sig_005", "neg_ns_005", "pos_ns_005", "zero_005"]].sum(axis=1)
    rhs_010 = summary[["neg_sig_010", "pos_sig_010", "neg_ns_010", "pos_ns_010", "zero_010"]].sum(axis=1)
    if not rhs_005.eq(summary["n_observed"]).all():
        raise RuntimeError("p<0.05 distribution identity failed")
    if not rhs_010.eq(summary["n_observed"]).all():
        raise RuntimeError("p<0.10 distribution identity failed")


def write_report(
    support: pd.DataFrame,
    gt2_detail: pd.DataFrame,
    gt5_detail: pd.DataFrame,
    gt2_summary: pd.DataFrame,
    gt5_summary: pd.DataFrame,
    gt2_grouped: pd.DataFrame,
    gt5_grouped: pd.DataFrame,
    compare: pd.DataFrame,
) -> None:
    support_gt2 = support.loc[support["threshold_label"].eq("gt2")]
    support_gt5 = support.loc[support["threshold_label"].eq("gt5")]
    lines = [
        "# Grid-mean AI dry sample runs",
        "",
        "生成日期: 2026-06-04",
        "",
        "## 变量定义",
        "",
        "`ai_pet_over_p_year = et0_sum / pr_sum`，`ai_pet_over_p_gridmean` 是同一 `grid_id` 在可载入面板中的多年平均值。`AI>2` 用于干旱地区内灌溉异质性，`AI>5` 用于极干旱 pooled baseline，不拆灌溉组。",
        "",
        "## 样本支持",
        "",
        f"- `AI>2` 总样本行数范围: {int(support_gt2['N_rows'].min())}-{int(support_gt2['N_rows'].max())}; high_irr 行数范围: {int(support_gt2['high_irr_rows'].min())}-{int(support_gt2['high_irr_rows'].max())}; low_irr 行数范围: {int(support_gt2['low_irr_rows'].min())}-{int(support_gt2['low_irr_rows'].max())}.",
        f"- `AI>5` pooled 行数范围: {int(support_gt5['N_rows'].min())}-{int(support_gt5['N_rows'].max())}; high_irr 行数范围: {int(support_gt5['high_irr_rows'].min())}-{int(support_gt5['high_irr_rows'].max())}; low_irr 行数范围: {int(support_gt5['low_irr_rows'].min())}-{int(support_gt5['low_irr_rows'].max())}.",
        "",
        "## 输出文件",
        "",
        f"- `{RUN_DIR / (PREFIX_SUPPORT + '.csv')}`",
        f"- `{RUN_DIR / (PREFIX_GT2 + '_detail.csv')}`",
        f"- `{RUN_DIR / (PREFIX_GT2 + '_summary.csv')}`",
        f"- `{RUN_DIR / (PREFIX_GT2 + '_grouped_list.csv')}`",
        f"- `{RUN_DIR / (PREFIX_GT5 + '_detail.csv')}`",
        f"- `{RUN_DIR / (PREFIX_GT5 + '_summary.csv')}`",
        f"- `{RUN_DIR / (PREFIX_GT5 + '_grouped_list.csv')}`",
        f"- `{RUN_DIR / (COMPARE_NAME + '.csv')}`",
        "",
        "## 规模校验",
        "",
        f"- `AI>2` detail 行数: {len(gt2_detail)}; summary 行数: {len(gt2_summary)}; grouped 行数: {len(gt2_grouped)}.",
        f"- `AI>5` detail 行数: {len(gt5_detail)}; summary 行数: {len(gt5_summary)}; grouped 行数: {len(gt5_grouped)}.",
        f"- compare 行数: {len(compare)}.",
        "",
        "## 使用说明",
        "",
        "写故事时优先读取 grouped list，并把 compare 表作为变化方向索引。`AI>2` 回答干旱地区内灌溉异质性是否改变；`AI>5` 回答极干旱样本 pooled baseline 是否仍支持同一机制。控制变量保留在表中，但故事判断优先看 `a1/a3/b/c1/c3`。",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit-scales", type=int, default=None)
    args = parser.parse_args()

    df = add_gridmean_ai(load_panel())
    membership_all = pd.read_csv(MEMBERSHIP_CSV)
    variants = build_variant_table(df, args.limit_scales)
    membership = membership_all.loc[membership_all["sample_id"].isin(set(variants["sample_id"]))].copy()
    if membership["sample_id"].nunique() != len(variants):
        raise RuntimeError("membership does not cover selected variants")

    support = build_support(df, variants, membership)
    gt2_support = support.loc[support["threshold_label"].eq("gt2")]
    gt5_support = support.loc[support["threshold_label"].eq("gt5")]
    if (gt2_support["low_irr_rows"] < 500).any():
        raise RuntimeError("AI>2 low_irr support falls below 500 in at least one scale")
    if (gt5_support["N_rows"] < 500).any():
        raise RuntimeError("AI>5 pooled support falls below 500 in at least one scale")

    gt2_detail, gt5_detail, skipped, attempts = run_all(df, variants, membership)
    gt2_summary = summarize(gt2_detail, membership)
    gt5_summary = summarize(gt5_detail, membership)
    expected_families = set(membership["family_id"].astype(str).unique())
    validate_summary(gt2_summary, "irr_group", "heterogeneity", expected_families)
    validate_summary(gt5_summary, "all", "baseline", expected_families)

    gt2_annotated, gt2_grouped = write_grouped(gt2_summary, PREFIX_GT2)
    gt5_annotated, gt5_grouped = write_grouped(gt5_summary, PREFIX_GT5)
    compare = compare_with_existing(gt2_summary, gt5_summary)

    support.to_csv(RUN_DIR / f"{PREFIX_SUPPORT}.csv", index=False, encoding="utf-8")
    gt2_detail.to_csv(RUN_DIR / f"{PREFIX_GT2}_detail.csv", index=False, encoding="utf-8")
    gt2_summary.to_csv(RUN_DIR / f"{PREFIX_GT2}_summary.csv", index=False, encoding="utf-8")
    gt5_detail.to_csv(RUN_DIR / f"{PREFIX_GT5}_detail.csv", index=False, encoding="utf-8")
    gt5_summary.to_csv(RUN_DIR / f"{PREFIX_GT5}_summary.csv", index=False, encoding="utf-8")
    if not skipped.empty:
        skipped.to_csv(RUN_DIR / "gridmean_ai_dry_skipped.csv", index=False, encoding="utf-8")
    attempts.to_csv(RUN_DIR / "gridmean_ai_dry_attempts.csv", index=False, encoding="utf-8")
    compare.to_csv(RUN_DIR / f"{COMPARE_NAME}.csv", index=False, encoding="utf-8")
    write_report(support, gt2_detail, gt5_detail, gt2_summary, gt5_summary, gt2_grouped, gt5_grouped, compare)

    print(f"wrote outputs to {RUN_DIR}")
    print(f"gt2_detail={len(gt2_detail)} gt2_summary={len(gt2_summary)} gt2_grouped={len(gt2_grouped)}")
    print(f"gt5_detail={len(gt5_detail)} gt5_summary={len(gt5_summary)} gt5_grouped={len(gt5_grouped)}")
    print(f"skipped={len(skipped)} compare={len(compare)}")


if __name__ == "__main__":
    main()
