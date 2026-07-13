"""
Summarize all RHS coefficient sign/significance patterns within four story families.

Inputs are existing coefficient inventories; this script does not rerun regressions.
Family membership is reproduced from the locked key-story 90% connected grouping:
key roles a1/a3/b/c1/c3, p<0.10 states, mean/dry theory orientation, and
mean/dry collapsed into a paired story-state.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
RUN_DIR = PROJ / "temp/2026-06-02_parallel_rules_69038_story_search"
DETAIL_CSV = RUN_DIR / "coefficient_distribution_all128_detail.csv"
VARIANT_CSV = RUN_DIR / "bio_window_128_variant_index.csv"
REPORT_MD = PROJ / "quality_reports/2026-06-04_story_family_all_coefficients_dictionary.md"

PREFIX = "story_family_all_coefficients"
KEY_ROLES = {"a1", "a3", "b", "c1", "c3"}
DRY_FLIP_ROLES = {"a1", "a3", "b"}
SIGN_STATES = ["neg_sig", "pos_sig", "neg_ns", "pos_ns", "zero"]
STATE_005 = {
    "negative_sig": "neg_sig_005",
    "positive_sig": "pos_sig_005",
    "negative_ns": "neg_ns_005",
    "positive_ns": "pos_ns_005",
    "zero": "zero_005",
}
STATE_010 = {
    "negative_sig": "neg_sig_010",
    "positive_sig": "pos_sig_010",
    "negative_ns": "neg_ns_010",
    "positive_ns": "pos_ns_010",
    "zero": "zero_010",
}

FAMILY_EXPECTED_SIZES = [48, 32, 32, 16]
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
FEATURE_COLS = [
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
SUMMARY_INDEX = ["family_id", *FEATURE_COLS]
ROLE_INDEX = [
    "family_id",
    "layer",
    "subgroup_dim",
    "subgroup",
    "hazard",
    "transform",
    "branch",
    "equation",
    "role",
]


def flip_state(state: str) -> str:
    return {
        "negative_sig": "positive_sig",
        "positive_sig": "negative_sig",
        "negative_ns": "positive_ns",
        "positive_ns": "negative_ns",
        "zero": "zero",
    }.get(state, state)


def oriented_state(row: pd.Series) -> str:
    state = str(row["sign_sig_010"])
    if row["branch"] == "dry" and row["role"] in DRY_FLIP_ROLES:
        return flip_state(state)
    return state


def build_story_signature(detail: pd.DataFrame) -> pd.DataFrame:
    key = detail.loc[detail["role"].isin(KEY_ROLES)].copy()
    key["state_oriented"] = key.apply(oriented_state, axis=1)
    key["feature_term"] = np.where(key["role"].eq("b"), key["role"], key["term"])
    pair_cols = [
        "layer",
        "subgroup_dim",
        "subgroup",
        "hazard",
        "transform",
        "equation",
        "feature_term",
        "role",
    ]

    rows: list[dict[str, object]] = []
    for keys, group in key.groupby(["sample_id", *pair_cols], dropna=False):
        states = sorted(set(group["state_oriented"].astype(str)))
        state = states[0] if len(states) == 1 else "mixed:" + "+".join(states)
        row = dict(zip(["sample_id", *pair_cols], keys))
        row["state"] = state
        rows.append(row)

    paired = pd.DataFrame(rows)
    paired["feature"] = paired[pair_cols].astype(str).agg("|".join, axis=1)
    return paired.pivot(index="sample_id", columns="feature", values="state").fillna("not_estimated")


def connected_components(signature: pd.DataFrame, threshold: float = 0.90) -> list[list[str]]:
    ids = list(signature.index)
    arr = signature.astype(str).to_numpy()
    n = len(ids)
    adjacent = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if float((arr[i] == arr[j]).mean()) >= threshold:
                adjacent[i].add(j)
                adjacent[j].add(i)

    seen = [False] * n
    components: list[list[str]] = []
    for i in range(n):
        if seen[i]:
            continue
        queue: deque[int] = deque([i])
        seen[i] = True
        comp: list[str] = []
        while queue:
            u = queue.popleft()
            comp.append(ids[u])
            for v in adjacent[u]:
                if not seen[v]:
                    seen[v] = True
                    queue.append(v)
        components.append(sorted(comp))
    return components


def family_sort_key(component: list[str], variants: pd.DataFrame) -> tuple[int, int, int, int]:
    sub = variants.loc[variants["sample_id"].isin(component)]
    z = int(sub["zone_core"].min())
    sr_min = int(sub["sr_within"].min())
    sr_max = int(sub["sr_within"].max())
    years_min = int(sub["years_ge3"].min())
    size_rank = {48: 1, 32: 2, 16: 4}.get(len(component), 9)
    if z == 0 and sr_min == 0 and sr_max == 0:
        return (2, size_rank, years_min, 0)
    if z == 0 and sr_min == 1 and sr_max == 1:
        return (3, size_rank, years_min, 0)
    if z == 1 and sr_min == 1 and sr_max == 1 and years_min == 0:
        return (4, size_rank, years_min, 0)
    return (1, size_rank, years_min, 0)


def build_membership(detail: pd.DataFrame, variants: pd.DataFrame) -> pd.DataFrame:
    signature = build_story_signature(detail)
    components = connected_components(signature)
    sizes = sorted((len(c) for c in components), reverse=True)
    if sizes != FAMILY_EXPECTED_SIZES:
        raise RuntimeError(f"Unexpected story family sizes: {sizes}; expected {FAMILY_EXPECTED_SIZES}")

    ordered = sorted(components, key=lambda comp: family_sort_key(comp, variants))
    rows: list[dict[str, object]] = []
    for family_num, comp in enumerate(ordered, start=1):
        for sample_id in comp:
            rows.append({"sample_id": sample_id, "family_id": f"F{family_num}", "family_size": len(comp)})

    membership = pd.DataFrame(rows)
    membership = membership.merge(variants, on="sample_id", how="left", validate="one_to_one")
    expected_cols = ["family_id", "sample_id", "family_size", "N_sample", "N_grids_sample", *RULE_COLS]
    membership = membership[expected_cols].sort_values(["family_id", "sample_id"]).reset_index(drop=True)

    if len(membership) != 128 or membership["sample_id"].nunique() != 128:
        raise RuntimeError("Family membership does not cover exactly 128 unique sample scales.")
    return membership


def count_states(series: pd.Series, mapping: dict[str, str]) -> dict[str, int]:
    counts = {v: 0 for v in mapping.values()}
    observed = series.dropna().astype(str)
    for state, value in observed.value_counts().items():
        if state in mapping:
            counts[mapping[state]] = int(value)
    return counts


def dominant_state(series: pd.Series) -> tuple[str, float]:
    observed = series.dropna().astype(str)
    if observed.empty:
        return "", np.nan
    vc = observed.value_counts()
    return str(vc.index[0]), float(vc.iloc[0] / len(observed))


def quantile_10(series: pd.Series) -> float:
    return float(series.quantile(0.10))


def quantile_90(series: pd.Series) -> float:
    return float(series.quantile(0.90))


def build_full_summary(detail_family: pd.DataFrame, membership: pd.DataFrame) -> pd.DataFrame:
    feature_universe = detail_family[FEATURE_COLS].drop_duplicates().reset_index(drop=True)
    family_universe = membership[["family_id", "family_size"]].drop_duplicates().reset_index(drop=True)
    full_index = family_universe.merge(feature_universe, how="cross")

    rows: list[dict[str, object]] = []
    grouped = detail_family.groupby(SUMMARY_INDEX, dropna=False, sort=False)
    for keys, group in grouped:
        row = dict(zip(SUMMARY_INDEX, keys))
        row["n_observed"] = int(len(group))
        row.update(count_states(group["sign_sig_005"], STATE_005))
        row.update(count_states(group["sign_sig_010"], STATE_010))
        dominant, share = dominant_state(group["sign_sig_010"])
        row["dominant_state_010"] = dominant
        row["dominant_share_010"] = share
        row["median_coef"] = float(group["coef"].median())
        row["mean_coef"] = float(group["coef"].mean())
        row["p10_coef"] = quantile_10(group["coef"])
        row["p90_coef"] = quantile_90(group["coef"])
        row["median_p"] = float(group["p"].median())
        row["min_p"] = float(group["p"].min())
        row["max_p"] = float(group["p"].max())
        row["median_N_model"] = float(group["N_model"].median())
        row["median_N_grids"] = float(group["N_grids"].median())
        rows.append(row)

    observed = pd.DataFrame(rows)
    summary = full_index.merge(observed, on=SUMMARY_INDEX, how="left")
    count_cols = [
        "n_observed",
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
    for col in count_cols:
        summary[col] = summary[col].fillna(0).astype(int)
    summary["n_family_scales"] = summary["family_size"].astype(int)
    summary["n_missing"] = summary["n_family_scales"] - summary["n_observed"]
    summary["dominant_state_010"] = summary["dominant_state_010"].fillna("")

    ordered = [
        "family_id",
        *FEATURE_COLS,
        "n_family_scales",
        "n_observed",
        "n_missing",
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
        "dominant_state_010",
        "dominant_share_010",
        "median_coef",
        "mean_coef",
        "p10_coef",
        "p90_coef",
        "median_p",
        "min_p",
        "max_p",
        "median_N_model",
        "median_N_grids",
    ]
    return summary[ordered].sort_values(SUMMARY_INDEX).reset_index(drop=True)


def build_role_summary(detail_family: pd.DataFrame, membership: pd.DataFrame) -> pd.DataFrame:
    tmp = detail_family.copy()
    tmp["coeff_cell"] = tmp[FEATURE_COLS].astype(str).agg("|".join, axis=1)
    cell_counts = tmp.groupby(ROLE_INDEX, dropna=False)["coeff_cell"].nunique().reset_index(name="n_coefficient_cells")
    fam_sizes = membership[["family_id", "family_size"]].drop_duplicates()
    role_base = cell_counts.merge(fam_sizes, on="family_id", how="left")

    rows: list[dict[str, object]] = []
    for keys, group in tmp.groupby(ROLE_INDEX, dropna=False, sort=False):
        row = dict(zip(ROLE_INDEX, keys))
        row["n_observed"] = int(len(group))
        row.update(count_states(group["sign_sig_005"], STATE_005))
        row.update(count_states(group["sign_sig_010"], STATE_010))
        dominant, share = dominant_state(group["sign_sig_010"])
        row["dominant_state_010"] = dominant
        row["dominant_share_010"] = share
        row["median_coef"] = float(group["coef"].median())
        row["mean_coef"] = float(group["coef"].mean())
        row["median_p"] = float(group["p"].median())
        rows.append(row)

    role_summary = role_base.merge(pd.DataFrame(rows), on=ROLE_INDEX, how="left")
    count_cols = [
        "n_observed",
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
    for col in count_cols:
        role_summary[col] = role_summary[col].fillna(0).astype(int)
    role_summary["n_expected_observations"] = (
        role_summary["family_size"].astype(int) * role_summary["n_coefficient_cells"].astype(int)
    )
    role_summary["n_missing"] = role_summary["n_expected_observations"] - role_summary["n_observed"]
    role_summary["dominant_state_010"] = role_summary["dominant_state_010"].fillna("")

    ordered = [
        *ROLE_INDEX,
        "family_size",
        "n_coefficient_cells",
        "n_expected_observations",
        "n_observed",
        "n_missing",
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
        "dominant_state_010",
        "dominant_share_010",
        "median_coef",
        "mean_coef",
        "median_p",
    ]
    return role_summary[ordered].sort_values(ROLE_INDEX).reset_index(drop=True)


def validate_outputs(
    detail: pd.DataFrame,
    membership: pd.DataFrame,
    detail_family: pd.DataFrame,
    summary: pd.DataFrame,
) -> None:
    sizes = sorted(membership.groupby("family_id")["sample_id"].nunique().tolist(), reverse=True)
    if sizes != FAMILY_EXPECTED_SIZES:
        raise RuntimeError(f"Output family sizes mismatch: {sizes}")
    if len(detail_family) != len(detail):
        raise RuntimeError(f"Detail row loss: {len(detail_family)} vs {len(detail)}")
    roles = set(summary["role"].dropna().astype(str))
    expected_roles = {
        "a1",
        "a3",
        "b",
        "c1",
        "c3",
        "sr_main_in_mediator",
        "sr_main_in_outcome",
        "control_or_covariate",
    }
    if roles != expected_roles:
        raise RuntimeError(f"Unexpected role coverage: {sorted(roles)}")

    if not (summary["n_family_scales"].eq(summary["n_observed"] + summary["n_missing"])).all():
        raise RuntimeError("Summary n_family_scales identity failed.")
    lhs_005 = summary[["neg_sig_005", "pos_sig_005", "neg_ns_005", "pos_ns_005", "zero_005"]].sum(axis=1)
    lhs_010 = summary[["neg_sig_010", "pos_sig_010", "neg_ns_010", "pos_ns_010", "zero_010"]].sum(axis=1)
    if not lhs_005.eq(summary["n_observed"]).all():
        raise RuntimeError("Summary p<0.05 sign distribution identity failed.")
    if not lhs_010.eq(summary["n_observed"]).all():
        raise RuntimeError("Summary p<0.10 sign distribution identity failed.")


def family_rule_text(membership: pd.DataFrame) -> str:
    lines: list[str] = []
    for family_id, group in membership.groupby("family_id", sort=True):
        fixed = []
        varying = []
        for col in RULE_COLS:
            vals = sorted(group[col].dropna().astype(int).unique().tolist())
            if len(vals) == 1:
                fixed.append(f"`{col}={vals[0]}`")
            else:
                varying.append(f"`{col}`")
        sample_ids = ", ".join(group["sample_id"].tolist())
        lines.append(
            f"- `{family_id}`: {len(group)} 个 scale; 固定项: "
            f"{'; '.join(fixed) if fixed else '无'}; 变动项: "
            f"{', '.join(varying) if varying else '无'}; sample_id: {sample_ids}."
        )
    return "\n".join(lines)


def write_dictionary(membership: pd.DataFrame, summary: pd.DataFrame, role_summary: pd.DataFrame) -> None:
    membership_path = RUN_DIR / f"{PREFIX}_membership.csv"
    detail_path = RUN_DIR / f"{PREFIX}_detail.csv"
    summary_path = RUN_DIR / f"{PREFIX}_summary.csv"
    role_path = RUN_DIR / f"{PREFIX}_role_summary.csv"
    text = f"""# 四类 Family 全部系数正负显著性字典

生成日期: 2026-06-04

## 数据来源

本批文件来自 `{DETAIL_CSV}`，没有重新估计回归。输入 detail 表每行是一个 `sample_id` 中某个 RHS 系数的估计结果，包含系数、标准误、p 值、正负号和 `p<0.05` / `p<0.10` 显著性状态。

四类 family 的划分沿用已经锁定的故事聚类口径: 只用 `a1/a3/b/c1/c3`，纳入 baseline 与 heterogeneity，采用 `p<0.10` 的 `sign_sig_010`，用 90% 相似的连通分组；mean/dry 只在 family 生成阶段按理论方向折算。生成本批 CSV 时，所有 RHS 系数的原始 `sign_sig_005` 和 `sign_sig_010` 都保持不变，没有对控制变量或 dry 分支重写方向。

## 输出文件

- `{membership_path}`: 每个 `sample_id` 的 family 归属、样本量、网格数和 8 个平行清洗规则。
- `{detail_path}`: 原 detail 表追加 `family_id` 和 `family_size` 后的完整逐 scale 逐系数长表。
- `{summary_path}`: family 内逐系数分布表。每行是 `family_id + layer + subgroup_dim + subgroup + hazard + transform + branch + mediator_tag + mediator + equation + depvar + term + role` 的唯一组合。
- `{role_path}`: family 内按 role 汇总的导航表。该表用于快速定位大类模式，不能替代逐系数 summary。

## Family 组成

{family_rule_text(membership)}

## 字段说明

`family_id` 表示四类故事家族，`family_size` 或 `n_family_scales` 表示该家族包含多少个 scale。`layer` 区分 `baseline` 和 `heterogeneity`，`subgroup_dim/subgroup` 表示全样本或异质性子样本。`hazard` 包括 `drought/heat/hotdry`，`transform` 包括 `raw/winsor_1_99`，`branch` 包括 `mean/dry`，`equation` 包括 `mediator/outcome`。

`term` 是 RHS 系数项，`role` 是该项在方程里的解释位置: `a1` 是 hazard 到 mediator，`a3` 是 SR×hazard 到 mediator，`b` 是 mediator 到产量，`c1` 是 hazard 到产量，`c3` 是 SR×hazard 到产量，`sr_main_in_mediator` 和 `sr_main_in_outcome` 是 `ca` 主效应，`control_or_covariate` 是 companion hazard、气候控制和其他协变量。

`sign_sig_005/sign_sig_010` 的取值为 `negative_sig/positive_sig/negative_ns/positive_ns/zero`，分别表示负显著、正显著、负不显著、正不显著和零系数。`neg_sig_005` 等列表示在该 family 的已观测 scale 中，该状态出现的次数。`dominant_state_010` 是 `p<0.10` 口径下最常见状态，`dominant_share_010` 是该状态占 `n_observed` 的比例。

`n_observed` 是该 family 内成功估计出该系数的 scale 数，`n_missing` 是该 family 内没有该系数估计结果的 scale 数。若 `zone_core=1` 导致 `maize_zone=Other` 不存在，则相关行可能出现 `n_observed=0` 和 `n_missing=n_family_scales`。

`median_coef/mean_coef/p10_coef/p90_coef` 描述 family 内该系数估计值分布。`median_p/min_p/max_p` 描述 p 值分布。`median_N_model/median_N_grids` 描述该系数对应模型的样本量和网格数。

## AI 使用方法

后续 AI 写每类故事时，应先从 membership 判断 family 的样本清洗规则，再从 summary 读取每个方程、每个 subgroup、每个 hazard、每个 mediator branch 的全部 RHS 系数状态。若一个系数 `dominant_share_010` 高且 `n_missing=0`，说明该 family 内该系数方向和显著性较稳定；若 `dominant_share_010` 低或 mixed 状态分散，应写成不稳定或分组依赖。控制变量系数可用于理解背景相关结构，但不应直接写成 SR 机制主线。

## 文件规模校验

- membership 行数: {len(membership)}
- summary 行数: {len(summary)}
- role_summary 行数: {len(role_summary)}
- family 规模: {membership.groupby("family_id")["sample_id"].nunique().to_dict()}
"""
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text(text, encoding="utf-8")


def main() -> None:
    detail = pd.read_csv(DETAIL_CSV)
    variants = pd.read_csv(VARIANT_CSV)
    membership = build_membership(detail, variants)
    detail_family = detail.merge(
        membership[["sample_id", "family_id", "family_size"]],
        on="sample_id",
        how="left",
        validate="many_to_one",
    )
    detail_family = detail_family[["family_id", "family_size", *detail.columns.tolist()]]
    summary = build_full_summary(detail_family, membership)
    role_summary = build_role_summary(detail_family, membership)
    validate_outputs(detail, membership, detail_family, summary)

    membership.to_csv(RUN_DIR / f"{PREFIX}_membership.csv", index=False, encoding="utf-8")
    detail_family.to_csv(RUN_DIR / f"{PREFIX}_detail.csv", index=False, encoding="utf-8")
    summary.to_csv(RUN_DIR / f"{PREFIX}_summary.csv", index=False, encoding="utf-8")
    role_summary.to_csv(RUN_DIR / f"{PREFIX}_role_summary.csv", index=False, encoding="utf-8")
    write_dictionary(membership, summary, role_summary)

    print(f"wrote {RUN_DIR / (PREFIX + '_membership.csv')}")
    print(f"wrote {RUN_DIR / (PREFIX + '_detail.csv')}")
    print(f"wrote {RUN_DIR / (PREFIX + '_summary.csv')}")
    print(f"wrote {RUN_DIR / (PREFIX + '_role_summary.csv')}")
    print(f"wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
