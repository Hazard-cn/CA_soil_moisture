"""
Build a readable per-family coefficient list.

The output keeps every family-by-coefficient cell in an annotated file, then
groups only highly stable cells for a compact reading layer. Non-stable and
missing cells remain listed individually with variation marks.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
RUN_DIR = PROJ / "temp/2026-06-02_parallel_rules_69038_story_search"
SUMMARY_CSV = RUN_DIR / "story_family_all_coefficients_summary.csv"
MEMBERSHIP_CSV = RUN_DIR / "story_family_all_coefficients_membership.csv"
ANNOTATED_CSV = RUN_DIR / "story_family_coefficient_annotated_cells.csv"
GROUPED_CSV = RUN_DIR / "story_family_coefficient_grouped_list.csv"
REPORT_MD = PROJ / "quality_reports/2026-06-04_story_family_coefficient_grouped_list.md"

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

CELL_COLS = [
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

STABLE_GROUP_COLS = [
    "family_id",
    "status_class",
    "mark",
    "equation",
    "role",
    "dominant_state_010",
]

NONSTABLE_GROUP_COLS = [
    "family_id",
    "status_class",
    "mark",
    "layer",
    "subgroup_dim",
    "subgroup",
    "hazard",
    "branch",
    "equation",
    "role",
    "dominant_state_010",
]


def add_shares(summary: pd.DataFrame) -> pd.DataFrame:
    s = summary.copy()
    denom = s["n_observed"].astype(float).replace(0.0, float("nan"))
    for col in ["neg_sig_010", "pos_sig_010", "neg_ns_010", "pos_ns_010", "zero_010"]:
        s[f"{col}_share"] = s[col].astype(float).div(denom).fillna(0.0)
    s["positive_total_share"] = s["pos_sig_010_share"] + s["pos_ns_010_share"]
    s["negative_total_share"] = s["neg_sig_010_share"] + s["neg_ns_010_share"]
    s["sig_total_share"] = s["pos_sig_010_share"] + s["neg_sig_010_share"]
    return s


def classify_row(row: pd.Series) -> tuple[str, str, str]:
    if int(row["n_observed"]) == 0:
        return "missing_only", "MARK_MISSING", "this coefficient cell is not estimated in this family"

    dominant = str(row["dominant_state_010"])
    dominant_share = float(row["dominant_share_010"])
    sign_flip_like = (
        float(row["positive_total_share"]) >= OPPOSITE_SIGN_SHARE
        and float(row["negative_total_share"]) >= OPPOSITE_SIGN_SHARE
    )
    sig_mixed = 0.25 <= float(row["sig_total_share"]) <= 0.75

    if dominant_share >= STABLE_SHARE:
        if dominant == "positive_sig":
            return "stable_positive_sig", "STABLE", "dominant state is positive_sig in at least 90 percent of observed scales"
        if dominant == "negative_sig":
            return "stable_negative_sig", "STABLE", "dominant state is negative_sig in at least 90 percent of observed scales"
        return "stable_non_sig_or_zero", "STABLE", "dominant state is non-significant or zero in at least 90 percent of observed scales"

    if sign_flip_like:
        return "variable_sign_change", "MARK_SIGN_CHANGE", "positive and negative signs both have material shares"
    if sig_mixed:
        return "variable_significance", "MARK_SIG_MIXED", "significance and non-significance are mixed"
    if dominant_share < VOLATILE_SHARE:
        return "variable_other", "MARK_OTHER_VARIATION", "dominant state share is below 75 percent"
    return "moderate_variation", "MARK_MODERATE", "dominant state is between 75 and 90 percent"


def coefficient_label(row: pd.Series) -> str:
    return (
        f"{row['layer']}|{row['subgroup_dim']}:{row['subgroup']}|"
        f"{row['hazard']}|{row['transform']}|{row['branch']}|{row['equation']}|"
        f"{row['mediator_tag']}|dep={row['depvar']}|term={row['term']}"
        f"|n={int(row['n_observed'])}/{int(row['n_family_scales'])}"
        f"|010={row['dominant_state_010']}:{float(row['dominant_share_010']):.2f}"
    )


def distribution_text(row: pd.Series, suffix: str) -> str:
    return (
        f"neg_sig={int(row[f'neg_sig_{suffix}'])}, "
        f"pos_sig={int(row[f'pos_sig_{suffix}'])}, "
        f"neg_ns={int(row[f'neg_ns_{suffix}'])}, "
        f"pos_ns={int(row[f'pos_ns_{suffix}'])}, "
        f"zero={int(row[f'zero_{suffix}'])}"
    )


def rule_profile(membership: pd.DataFrame, family_id: str) -> str:
    group = membership.loc[membership["family_id"].eq(family_id)]
    fixed: list[str] = []
    varying: list[str] = []
    for col in RULE_COLS:
        vals = sorted(group[col].dropna().astype(int).unique().tolist())
        if len(vals) == 1:
            fixed.append(f"{col}={vals[0]}")
        else:
            varying.append(col)
    return f"fixed: {', '.join(fixed) if fixed else 'none'}; varying: {', '.join(varying) if varying else 'none'}"


def annotate(summary: pd.DataFrame) -> pd.DataFrame:
    s = add_shares(summary)
    classes = s.apply(classify_row, axis=1, result_type="expand")
    classes.columns = ["status_class", "mark", "mark_reason"]
    s = pd.concat([s, classes], axis=1)
    s["coefficient_label"] = s.apply(coefficient_label, axis=1)
    s["distribution_010"] = s.apply(lambda row: distribution_text(row, "010"), axis=1)
    s["distribution_005"] = s.apply(lambda row: distribution_text(row, "005"), axis=1)
    s["coef_summary"] = (
        "median="
        + s["median_coef"].map(lambda x: "" if pd.isna(x) else f"{x:.6g}")
        + "; p10="
        + s["p10_coef"].map(lambda x: "" if pd.isna(x) else f"{x:.6g}")
        + "; p90="
        + s["p90_coef"].map(lambda x: "" if pd.isna(x) else f"{x:.6g}")
    )
    return s


def build_grouped(annotated: pd.DataFrame) -> pd.DataFrame:
    stable = annotated.loc[annotated["mark"].eq("STABLE")].copy()
    nonstable = annotated.loc[~annotated["mark"].eq("STABLE")].copy()

    grouped_rows: list[dict[str, object]] = []
    for keys, group in stable.groupby(STABLE_GROUP_COLS, dropna=False, sort=True):
        row = dict(zip(STABLE_GROUP_COLS, keys))
        row["layer"] = "multiple"
        row["subgroup_dim"] = "multiple"
        row["subgroup"] = "multiple"
        row["hazard"] = "multiple"
        row["transform"] = "multiple"
        row["branch"] = "multiple"
        row["row_type"] = "stable_group"
        row["n_coefficient_cells"] = int(len(group))
        row["n_observed_total"] = int(group["n_observed"].sum())
        row["n_missing_total"] = int(group["n_missing"].sum())
        row["dominant_share_min"] = float(group["dominant_share_010"].min())
        row["dominant_share_median"] = float(group["dominant_share_010"].median())
        row["distribution_010_summary"] = (
            "neg_sig="
            + str(int(group["neg_sig_010"].sum()))
            + ", pos_sig="
            + str(int(group["pos_sig_010"].sum()))
            + ", neg_ns="
            + str(int(group["neg_ns_010"].sum()))
            + ", pos_ns="
            + str(int(group["pos_ns_010"].sum()))
            + ", zero="
            + str(int(group["zero_010"].sum()))
        )
        row["coefficient_labels"] = " ; ".join(group["coefficient_label"].tolist())
        row["note"] = "stable coefficients are grouped because their p<0.10 sign/significance state is highly consistent"
        grouped_rows.append(row)

    for keys, group in nonstable.groupby(NONSTABLE_GROUP_COLS, dropna=False, sort=True):
        row = dict(zip(NONSTABLE_GROUP_COLS, keys))
        row["transform"] = "multiple" if group["transform"].nunique() > 1 else str(group["transform"].iloc[0])
        row["row_type"] = "marked_group"
        row["n_coefficient_cells"] = int(len(group))
        row["n_observed_total"] = int(group["n_observed"].sum())
        row["n_missing_total"] = int(group["n_missing"].sum())
        if group["dominant_share_010"].notna().any():
            row["dominant_share_min"] = float(group["dominant_share_010"].min())
            row["dominant_share_median"] = float(group["dominant_share_010"].median())
        else:
            row["dominant_share_min"] = float("nan")
            row["dominant_share_median"] = float("nan")
        row["distribution_010_summary"] = (
            "neg_sig="
            + str(int(group["neg_sig_010"].sum()))
            + ", pos_sig="
            + str(int(group["pos_sig_010"].sum()))
            + ", neg_ns="
            + str(int(group["neg_ns_010"].sum()))
            + ", pos_ns="
            + str(int(group["pos_ns_010"].sum()))
            + ", zero="
            + str(int(group["zero_010"].sum()))
        )
        row["coefficient_labels"] = " ; ".join(group["coefficient_label"].tolist())
        row["note"] = " ; ".join(sorted(set(group["mark_reason"].astype(str))))
        grouped_rows.append(row)

    cols = [
        "family_id",
        "row_type",
        "status_class",
        "mark",
        "layer",
        "subgroup_dim",
        "subgroup",
        "hazard",
        "transform",
        "branch",
        "equation",
        "role",
        "dominant_state_010",
        "n_coefficient_cells",
        "n_observed_total",
        "n_missing_total",
        "dominant_share_min",
        "dominant_share_median",
        "distribution_010_summary",
        "coefficient_labels",
        "note",
    ]
    return pd.DataFrame(grouped_rows)[cols].sort_values(
        ["family_id", "mark", "layer", "subgroup_dim", "subgroup", "hazard", "branch", "equation", "role"]
    )


def write_report(annotated: pd.DataFrame, grouped: pd.DataFrame, membership: pd.DataFrame) -> None:
    lines = [
        "# 四类 Family 系数情况分组清单",
        "",
        "生成日期: 2026-06-04",
        "",
        "## 口径",
        "",
        f"输入文件为 `{SUMMARY_CSV}`，没有重新回归。`{ANNOTATED_CSV}` 逐个列出所有 family×系数单元；`{GROUPED_CSV}` 把 `dominant_share_010 >= {STABLE_SHARE}` 的稳定系数合并成组，把变化较大、显著性混合、正负变化或缺失的单元逐条列出并打 mark。",
        "",
        "## Mark 定义",
        "",
        "- `STABLE`: `p<0.10` 下同一 `sign_sig_010` 状态占已观测 scale 的比例不低于 90%。",
        "- `MARK_SIGN_CHANGE`: 正号总占比和负号总占比都不低于 20%。",
        "- `MARK_SIG_MIXED`: 显著状态和不显著状态明显混合，显著总占比在 25% 到 75% 之间。",
        "- `MARK_OTHER_VARIATION`: 最大状态占比低于 75%，但不属于前两类。",
        "- `MARK_MODERATE`: 最大状态占比在 75% 到 90% 之间。",
        "- `MARK_MISSING`: 该 family 中该系数单元没有成功估计。",
        "",
        "## Family 概览",
        "",
    ]
    for family_id in sorted(membership["family_id"].unique()):
        a = annotated.loc[annotated["family_id"].eq(family_id)]
        g = grouped.loc[grouped["family_id"].eq(family_id)]
        mark_counts = a["mark"].value_counts().to_dict()
        lines.extend(
            [
                f"### {family_id}",
                "",
                f"- scale 数: {membership.loc[membership['family_id'].eq(family_id), 'sample_id'].nunique()}",
                f"- 规则特征: {rule_profile(membership, family_id)}",
                f"- 系数单元数: {len(a)}",
                f"- grouped_list 行数: {len(g)}",
                f"- mark 分布: {mark_counts}",
                "",
            ]
        )
    lines.extend(
        [
            "## 使用方法",
            "",
            "写故事时先读 `grouped_list`。`row_type=stable_group` 的行表示稳定系数已经按 role/equation/dominant_state 合并；`row_type=marked_group` 的行表示正负或显著性变化较大的系数已经按变化来源合并。`coefficient_labels` 列保留该行覆盖的所有具体系数标签。若需要追溯完整分布，回到 `annotated_cells` 中按 `family_id/layer/subgroup/hazard/branch/equation/term/role` 定位。",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    summary = pd.read_csv(SUMMARY_CSV)
    membership = pd.read_csv(MEMBERSHIP_CSV)
    annotated = annotate(summary)
    grouped = build_grouped(annotated)

    if len(annotated) != len(summary):
        raise RuntimeError("Annotated output row count differs from summary input.")
    if annotated["family_id"].nunique() != 4 or grouped["family_id"].nunique() != 4:
        raise RuntimeError("Expected exactly four families.")
    if not set(annotated["mark"]).issubset(
        {"STABLE", "MARK_SIGN_CHANGE", "MARK_SIG_MIXED", "MARK_OTHER_VARIATION", "MARK_MODERATE", "MARK_MISSING"}
    ):
        raise RuntimeError("Unexpected mark value.")

    annotated.to_csv(ANNOTATED_CSV, index=False, encoding="utf-8")
    grouped.to_csv(GROUPED_CSV, index=False, encoding="utf-8")
    write_report(annotated, grouped, membership)

    print(f"wrote {ANNOTATED_CSV}")
    print(f"wrote {GROUPED_CSV}")
    print(f"wrote {REPORT_MD}")
    print("annotated rows", len(annotated), "grouped rows", len(grouped))
    print(grouped.groupby(["family_id", "row_type"]).size().to_string())
    print(annotated.groupby(["family_id", "mark"]).size().to_string())


if __name__ == "__main__":
    main()
