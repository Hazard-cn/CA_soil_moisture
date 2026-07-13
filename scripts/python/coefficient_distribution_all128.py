"""
Coefficient sign/significance distribution for all 128 Bxxx sample scales.

Scope:
- fixed base rule: main_sample == 1 and ggcp10_maize_frac >= 0.05
- optional rules: the 8 remaining parallel cleaning rules, deduplicated to 128 scales
- equations: full-season baseline plus subgroup heterogeneity re-estimation
- outputs: detail coefficient rows, summary distribution rows, skipped specs, and a dictionary MD
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd

from ggcp10_parallel_rules_69038_search import fit_fe_ols, load_panel, rhs_for
from bio_window_filter_128 import OUT_DIR, unique_variants


PREFIX = "coefficient_distribution_all128"
HAZARDS = ("drought", "heat", "hotdry")
TRANSFORMS = ("raw", "w")
MEDIATORS = {
    "mean_root": ("mean", "gleam_smrz_mean"),
    "dry_mdf_p10_sfc": ("dry", "v6mdf_p10_fn_gss"),
}
HET_GROUPS = {
    "irr_group": ("high_irr", "low_irr"),
    "maize_zone": ("HHH", "NE", "NW", "Other", "SH", "SW"),
}
KEY_ROLES = ("a1", "a3", "b", "c1", "c3")


def transform_label(transform: str) -> tuple[str, str]:
    sx = "w" if transform == "w" else "raw"
    label = "winsor_1_99" if sx == "w" else "raw"
    return sx, label


def sign_value(coef: float) -> str:
    if coef > 0:
        return "positive"
    if coef < 0:
        return "negative"
    return "zero"


def sign_sig_value(coef: float, p: float, alpha: float) -> str:
    sign = sign_value(coef)
    if sign == "zero":
        return "zero"
    return f"{sign}_{'sig' if p < alpha else 'ns'}"


def spec_terms(
    hazard: str,
    transform: str,
    mediator_tag: str,
) -> tuple[str, str, str, str, str, list[dict[str, object]]]:
    sx, label = transform_label(transform)
    branch, mediator_base = MEDIATORS[mediator_tag]
    mediator = f"{mediator_base}_{sx}"
    y, ca, mediator_rhs, outcome_rhs, hazard_var, sr_var = rhs_for(hazard, sx, mediator)
    role_map_m = {hazard_var: "a1", sr_var: "a3", ca: "sr_main_in_mediator"}
    role_map_y = {mediator: "b", hazard_var: "c1", sr_var: "c3", ca: "sr_main_in_outcome"}
    terms: list[dict[str, object]] = []
    for equation, depvar, xvars, role_map in (
        ("mediator", mediator, mediator_rhs, role_map_m),
        ("outcome", y, outcome_rhs, role_map_y),
    ):
        for term in xvars:
            terms.append(
                {
                    "equation": equation,
                    "depvar": depvar,
                    "term": term,
                    "role": role_map.get(term, "control_or_covariate"),
                }
            )
    return sx, label, branch, mediator, y, terms


def spec_id_for(
    sample_id: str,
    layer: str,
    subgroup_dim: str,
    subgroup: str,
    transform: str,
    mediator_tag: str,
    hazard: str,
) -> str:
    return f"{sample_id}_{layer}_{subgroup_dim}_{subgroup}_{transform}_{mediator_tag}_{hazard}"


def attempt_rows_for_spec(
    sample_id: str,
    layer: str,
    subgroup_dim: str,
    subgroup: str,
    hazard: str,
    transform: str,
    mediator_tag: str,
    n_rows_before_dropna: int,
) -> list[dict[str, object]]:
    sx, label, branch, mediator, _y, terms = spec_terms(hazard, transform, mediator_tag)
    spec_id = spec_id_for(sample_id, layer, subgroup_dim, subgroup, label, mediator_tag, hazard)
    return [
        {
            "sample_id": sample_id,
            "spec_id": spec_id,
            "layer": layer,
            "subgroup_dim": subgroup_dim,
            "subgroup": subgroup,
            "hazard": hazard,
            "transform": label,
            "branch": branch,
            "mediator_tag": mediator_tag,
            "mediator": mediator,
            "equation": term_row["equation"],
            "depvar": term_row["depvar"],
            "term": term_row["term"],
            "role": term_row["role"],
            "N_rows_before_dropna": n_rows_before_dropna,
        }
        for term_row in terms
    ]


def fit_spec_rows(
    sub: pd.DataFrame,
    sample_id: str,
    layer: str,
    subgroup_dim: str,
    subgroup: str,
    hazard: str,
    transform: str,
    mediator_tag: str,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    sx, label, branch, mediator, y, terms = spec_terms(hazard, transform, mediator_tag)
    _y, _ca, mediator_rhs, outcome_rhs, hazard_var, sr_var = rhs_for(hazard, sx, mediator)
    spec_id = spec_id_for(sample_id, layer, subgroup_dim, subgroup, label, mediator_tag, hazard)

    if len(sub) == 0:
        return [], [
            {
                "sample_id": sample_id,
                "layer": layer,
                "subgroup_dim": subgroup_dim,
                "subgroup": subgroup,
                "hazard": hazard,
                "transform": label,
                "mediator_tag": mediator_tag,
                "reason": "missing_subgroup",
                "N_rows_before_dropna": 0,
            }
        ]

    try:
        mres = fit_fe_ols(sub, mediator, mediator_rhs)
        yres = fit_fe_ols(sub, y, outcome_rhs)
    except Exception as exc:
        return [], [
            {
                "sample_id": sample_id,
                "layer": layer,
                "subgroup_dim": subgroup_dim,
                "subgroup": subgroup,
                "hazard": hazard,
                "transform": label,
                "mediator_tag": mediator_tag,
                "reason": str(exc),
                "N_rows_before_dropna": len(sub),
            }
        ]

    result_by_equation = {"mediator": mres, "outcome": yres}
    rows: list[dict[str, object]] = []
    for term_row in terms:
        equation = str(term_row["equation"])
        term = str(term_row["term"])
        res = result_by_equation[equation]
        coef = float(res[f"b:{term}"])
        p = float(res[f"p:{term}"])
        rows.append(
            {
                "sample_id": sample_id,
                "spec_id": spec_id,
                "layer": layer,
                "subgroup_dim": subgroup_dim,
                "subgroup": subgroup,
                "hazard": hazard,
                "transform": label,
                "branch": branch,
                "mediator_tag": mediator_tag,
                "mediator": mediator,
                "equation": equation,
                "depvar": term_row["depvar"],
                "term": term,
                "role": term_row["role"],
                "coef": coef,
                "se": float(res[f"se:{term}"]),
                "p": p,
                "sign": sign_value(coef),
                "sig_005": bool(p < 0.05),
                "sig_010": bool(p < 0.10),
                "sign_sig_005": sign_sig_value(coef, p, 0.05),
                "sign_sig_010": sign_sig_value(coef, p, 0.10),
                "N_model": int(res["N"]),
                "N_grids": int(res["clusters"]),
                "r2_within": float(res["r2_within"]),
            }
        )
    return rows, []


def iter_spec_subsets(base: pd.DataFrame) -> list[tuple[str, str, str, pd.DataFrame]]:
    subsets: list[tuple[str, str, str, pd.DataFrame]] = [("baseline", "all", "all", base)]
    for dim, values in HET_GROUPS.items():
        col = dim
        col_as_str = base[col].astype(str)
        for subgroup in values:
            subsets.append(("heterogeneity", dim, subgroup, base.loc[col_as_str.eq(subgroup)].copy()))
    return subsets


def build_summary(attempts: pd.DataFrame, detail: pd.DataFrame) -> pd.DataFrame:
    key_cols = [
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
    attempts_count = attempts.groupby(key_cols, dropna=False).size().reset_index(name="n_attempted")
    if detail.empty:
        merged = attempts_count
        for col in [
            "n_estimated",
            "neg_sig_005",
            "pos_sig_005",
            "neg_ns_005",
            "pos_ns_005",
            "zero_005",
            "neg_sig_010",
            "pos_sig_010",
            "neg_ns_010",
            "pos_ns_010",
            "zero_010",
        ]:
            merged[col] = 0
        merged["n_not_estimated"] = merged["n_attempted"]
        return merged

    detail_work = detail.copy()
    detail_work["neg_sig_005"] = (detail_work["coef"] < 0) & (detail_work["p"] < 0.05)
    detail_work["pos_sig_005"] = (detail_work["coef"] > 0) & (detail_work["p"] < 0.05)
    detail_work["neg_ns_005"] = (detail_work["coef"] < 0) & ~(detail_work["p"] < 0.05)
    detail_work["pos_ns_005"] = (detail_work["coef"] > 0) & ~(detail_work["p"] < 0.05)
    detail_work["zero_005"] = detail_work["coef"].eq(0)
    detail_work["neg_sig_010"] = (detail_work["coef"] < 0) & (detail_work["p"] < 0.10)
    detail_work["pos_sig_010"] = (detail_work["coef"] > 0) & (detail_work["p"] < 0.10)
    detail_work["neg_ns_010"] = (detail_work["coef"] < 0) & ~(detail_work["p"] < 0.10)
    detail_work["pos_ns_010"] = (detail_work["coef"] > 0) & ~(detail_work["p"] < 0.10)
    detail_work["zero_010"] = detail_work["coef"].eq(0)
    dist_cols = [
        "neg_sig_005",
        "pos_sig_005",
        "neg_ns_005",
        "pos_ns_005",
        "zero_005",
        "neg_sig_010",
        "pos_sig_010",
        "neg_ns_010",
        "pos_ns_010",
        "zero_010",
    ]
    estimated = (
        detail_work.groupby(key_cols, dropna=False)
        .agg(n_estimated=("sample_id", "size"), **{col: (col, "sum") for col in dist_cols})
        .reset_index()
    )
    out = attempts_count.merge(estimated, on=key_cols, how="left", validate="one_to_one")
    fill_cols = ["n_estimated", *dist_cols]
    out[fill_cols] = out[fill_cols].fillna(0).astype(int)
    out["n_not_estimated"] = out["n_attempted"] - out["n_estimated"]
    ordered = [
        *key_cols,
        "n_attempted",
        "n_estimated",
        "n_not_estimated",
        "neg_sig_005",
        "pos_sig_005",
        "neg_ns_005",
        "pos_ns_005",
        "zero_005",
        "neg_sig_010",
        "pos_sig_010",
        "neg_ns_010",
        "pos_ns_010",
        "zero_010",
    ]
    return out[ordered].sort_values(key_cols).reset_index(drop=True)


def validate_distribution(summary: pd.DataFrame) -> None:
    lhs = summary["n_estimated"]
    rhs_005 = summary[["neg_sig_005", "pos_sig_005", "neg_ns_005", "pos_ns_005", "zero_005"]].sum(axis=1)
    rhs_010 = summary[["neg_sig_010", "pos_sig_010", "neg_ns_010", "pos_ns_010", "zero_010"]].sum(axis=1)
    if not lhs.equals(rhs_005.astype(lhs.dtype)):
        bad = summary.loc[~lhs.eq(rhs_005)].head()
        raise ValueError(f"alpha_005_distribution_mismatch:\n{bad}")
    if not lhs.equals(rhs_010.astype(lhs.dtype)):
        bad = summary.loc[~lhs.eq(rhs_010)].head()
        raise ValueError(f"alpha_010_distribution_mismatch:\n{bad}")


def write_dictionary_md(summary: pd.DataFrame, detail: pd.DataFrame, skipped: pd.DataFrame, output_prefix: str) -> None:
    n_scales = int(detail["sample_id"].nunique()) if not detail.empty else 0
    baseline_eq = int(
        detail.loc[detail["layer"].eq("baseline")]
        .drop_duplicates(["sample_id", "spec_id", "equation"])
        .shape[0]
    ) if not detail.empty else 0
    key_roles_present = sorted(set(summary["role"]).intersection(KEY_ROLES))
    skipped_n = len(skipped)

    lines = [
        "# 128 scale coefficient distribution dictionary",
        "",
        "本文件解释 `coefficient_distribution_all128_*.csv` 的字段、方程和单元格含义。",
        "",
        "## Scope",
        "",
        "- 样本 scale：固定 `main_sample == 1` 且 `ggcp10_maize_frac >= 0.05`，其余 8 个清洗规则平行组合去重得到 `B001` 到 `B128`。",
        "- 方程：full-season baseline 与 subgroup heterogeneity 重估；不包含窗口方程，不包含 bootstrap。",
        "- 推断：沿用 Python two-way FE residualized OLS 的 `coef/se/p`。",
        f"- 本次 detail 中成功估计的 scale 数：{n_scales}。",
        f"- baseline 成功估计方程数：{baseline_eq}。",
        f"- skipped spec 数：{skipped_n}。",
        f"- summary 中出现的关键 role：{', '.join(key_roles_present)}。",
        "",
        "## 方程定义",
        "",
        "baseline 方程在全样本 scale 内估计；heterogeneity 方程在 subgroup 内重估同一套方程。",
        "",
        "```text",
        "Mediator equation:",
        "M_it = a1 Hazard_it + gamma ca_it + a3 (ca_it x Hazard_it)",
        "       + companion hazard controls + climate controls",
        "       + grid_i FE + year_t FE + e_it",
        "",
        "Outcome equation:",
        "ln_yield_it = c1 Hazard_it + gamma ca_it + c3 (ca_it x Hazard_it)",
        "              + b M_it + companion hazard controls + climate controls",
        "              + grid_i FE + year_t FE + e_it",
        "```",
        "",
        "hazard 映射如下：`drought` 使用 `D_full`，`heat` 使用 `hdd_ge32`，`hotdry` 使用 `HotDryPr_full`。`raw` 与 `winsor_1_99` 分别对应原始变量和 1/99 缩尾变量。",
        "",
        "## Subgroup scale",
        "",
        "- `layer=baseline, subgroup_dim=all, subgroup=all`：该 `Bxxx` scale 的完整样本。",
        "- `layer=heterogeneity, subgroup_dim=irr_group, subgroup=high_irr/low_irr`：在灌溉分组内重估。",
        "- `layer=heterogeneity, subgroup_dim=maize_zone, subgroup=HHH/NE/NW/Other/SH/SW`：在玉米区分组内重估。",
        "- 若某 subgroup 在某个 `Bxxx` scale 内不存在，或 listwise 后 `N<500`，该 spec 进入 skipped 文件，并在 summary 中体现为 `n_not_estimated`。",
        "",
        "## Role 字段",
        "",
        "- `a1`：mediator 方程中的 hazard 主效应。",
        "- `a3`：mediator 方程中的 `ca x Hazard`，即 SR 对 hazard -> mediator 关系的调节项。",
        "- `b`：outcome 方程中的 mediator 项。",
        "- `c1`：outcome 方程中的 hazard 主效应。",
        "- `c3`：outcome 方程中的 `ca x Hazard`，即 SR 对 hazard -> yield 关系的调节项。",
        "- `sr_main_in_mediator` / `sr_main_in_outcome`：两条方程中的 `ca` 主效应。",
        "- `control_or_covariate`：伴随 hazard 控制变量、气候控制变量、灌溉和 aridity 等控制项。",
        "",
        "## Detail CSV 字段",
        "",
        "- `sample_id`：`Bxxx` 样本 scale。",
        "- `spec_id`：样本、层级、subgroup、transform、mediator、hazard 的唯一组合。",
        "- `layer/subgroup_dim/subgroup`：baseline 或 heterogeneity 的样本切片。",
        "- `hazard/transform/mediator_tag/equation/depvar/term/role`：方程和系数项身份。",
        "- `coef/se/p`：该 RHS 系数的点估计、标准误和 p 值。",
        "- `sign`：`positive`、`negative` 或 `zero`。",
        "- `sig_005/sig_010`：是否分别满足 `p<0.05`、`p<0.10`。",
        "- `sign_sig_005/sign_sig_010`：合并符号和显著性后的分类，如 `negative_sig`、`positive_ns`。",
        "- `N_model/N_grids/r2_within`：该回归实际使用的行数、grid 数和 within R2。",
        "",
        "## Summary CSV 单元格",
        "",
        "summary 每一行唯一对应 `layer + subgroup_dim + subgroup + hazard + transform + branch + mediator_tag + mediator + equation + depvar + term + role`。",
        "",
        "- `n_attempted`：理论上应该估计该系数的 scale 次数。",
        "- `n_estimated`：该系数实际成功估计的 scale 次数。",
        "- `n_not_estimated`：`n_attempted - n_estimated`。",
        "- `neg_sig_005`：成功估计中，系数为负且 `p<0.05` 的次数。",
        "- `pos_sig_005`：成功估计中，系数为正且 `p<0.05` 的次数。",
        "- `neg_ns_005`：成功估计中，系数为负且不满足 `p<0.05` 的次数。",
        "- `pos_ns_005`：成功估计中，系数为正且不满足 `p<0.05` 的次数。",
        "- `zero_005`：成功估计中，系数正好为 0 的次数。",
        "- `neg_sig_010/pos_sig_010/neg_ns_010/pos_ns_010/zero_010`：同上，但显著阈值改为 `p<0.10`。",
        "",
        "对每一行都应满足：`n_estimated = neg_sig_005 + pos_sig_005 + neg_ns_005 + pos_ns_005 + zero_005`，并且对 0.10 阈值同样成立。",
        "",
        "## Output files",
        "",
        f"- `temp/2026-06-02_parallel_rules_69038_story_search/{output_prefix}_detail.csv`",
        f"- `temp/2026-06-02_parallel_rules_69038_story_search/{output_prefix}_summary.csv`",
        f"- `temp/2026-06-02_parallel_rules_69038_story_search/{output_prefix}_skipped.csv`",
        "- `quality_reports/2026-06-03_coefficient_distribution_all128_dictionary.md`",
        "",
    ]
    (Path("C:/YangSu/00_Project/CA_mechanism/regression_SR") / "quality_reports/2026-06-03_coefficient_distribution_all128_dictionary.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit-scales", type=int, default=None)
    parser.add_argument("--prefix", default=PREFIX)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start = time.time()
    df = load_panel()
    variants = unique_variants(df)
    if args.limit_scales is not None:
        variants = variants[: args.limit_scales]
    print(f"loaded {len(variants)} sample scales")

    attempts: list[dict[str, object]] = []
    detail_rows: list[dict[str, object]] = []
    skipped_rows: list[dict[str, object]] = []
    for idx, meta in enumerate(variants, start=1):
        sample_id = str(meta["sample_id"])
        base = df.loc[meta["mask"]].copy()
        subsets = iter_spec_subsets(base)
        for layer, subgroup_dim, subgroup, sub in subsets:
            for transform in TRANSFORMS:
                for hazard in HAZARDS:
                    for mediator_tag in MEDIATORS:
                        attempts.extend(
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
                        detail_rows.extend(rows)
                        skipped_rows.extend(skipped)
        if idx % 4 == 0 or idx == len(variants):
            elapsed = time.time() - start
            print(
                f"processed {idx}/{len(variants)} scales; "
                f"detail_rows={len(detail_rows)} skipped_specs={len(skipped_rows)} elapsed={elapsed:.1f}s"
            )

    attempts_df = pd.DataFrame(attempts)
    detail_df = pd.DataFrame(detail_rows)
    skipped_df = pd.DataFrame(skipped_rows)
    summary_df = build_summary(attempts_df, detail_df)
    validate_distribution(summary_df)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    detail_df.to_csv(OUT_DIR / f"{args.prefix}_detail.csv", index=False, encoding="utf-8-sig")
    summary_df.to_csv(OUT_DIR / f"{args.prefix}_summary.csv", index=False, encoding="utf-8-sig")
    skipped_df.to_csv(OUT_DIR / f"{args.prefix}_skipped.csv", index=False, encoding="utf-8-sig")
    attempts_df.to_csv(OUT_DIR / f"{args.prefix}_attempts.csv", index=False, encoding="utf-8-sig")
    write_dictionary_md(summary_df, detail_df, skipped_df, args.prefix)
    print(f"wrote outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
