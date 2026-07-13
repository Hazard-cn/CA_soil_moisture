"""
Build a program-readable mean/raw unified table for the F4-B067 full run.

The table keeps only branch=mean and transform=raw from the completed full
bootstrap pipeline. It combines RHS coefficients, IE/DE/TE effects, and
scenario contrasts in one long CSV with stable locator columns.
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
RUN_DIR = PROJ / "temp/2026-06-04_f4_b067_full_bootstrap_counterfactual"
OUT_CSV = RUN_DIR / "f4_b067_mean_raw_unified_coefficients_effects.csv"
DICT_MD = PROJ / "quality_reports/2026-06-04_f4_b067_mean_raw_unified_table_dictionary.md"

FILTER_BRANCH = "mean"
FILTER_TRANSFORM = "raw"

LOCATOR_COLS = [
    "sample_id",
    "layer",
    "subgroup_dim",
    "subgroup",
    "hazard",
    "transform",
    "branch",
    "mediator_tag",
    "mediator",
    "record_type",
    "equation",
    "depvar",
    "term",
    "role",
    "effect",
    "ca_level",
    "scenario",
]

VALUE_COLS = [
    "estimate",
    "model_se",
    "model_p",
    "model_ci_lo_95",
    "model_ci_hi_95",
    "bs_se",
    "bs_ci_lo_95",
    "bs_ci_hi_95",
    "sign",
    "sig_005",
    "sig_010",
    "sign_sig_005",
    "sign_sig_010",
    "N_model",
    "N_grids",
    "N_boot",
    "r2_within",
    "ca_value",
    "hazard_level",
    "delta_te_point",
    "delta_ln_yield_point",
    "delta_ln_yield_ci_lo",
    "delta_ln_yield_ci_hi",
    "pct_delta_point",
    "pct_delta_bs_se",
    "pct_delta_ci_lo",
    "pct_delta_ci_hi",
]


def empty_str_cols(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        if col not in out.columns:
            out[col] = ""
    return out


def load_filtered(name: str) -> pd.DataFrame:
    path = RUN_DIR / name
    df = pd.read_csv(path)
    return df.loc[df["branch"].eq(FILTER_BRANCH) & df["transform"].eq(FILTER_TRANSFORM)].copy()


def build_rhs_rows() -> pd.DataFrame:
    coef = load_filtered("f4_b067_coefficients_detail.csv")
    path_bs = load_filtered("f4_b067_path_bootstrap_summary.csv")
    key = [
        "sample_id",
        "layer",
        "subgroup_dim",
        "subgroup",
        "hazard",
        "transform",
        "branch",
        "mediator_tag",
        "mediator",
        "role",
        "term",
    ]
    path_keep = path_bs[key + ["bs_se", "ci_lo_pct", "ci_hi_pct", "N_boot"]].rename(
        columns={"ci_lo_pct": "bs_ci_lo_95", "ci_hi_pct": "bs_ci_hi_95"}
    )
    merged = coef.merge(path_keep, on=key, how="left")
    merged["record_type"] = "rhs_coefficient"
    merged["effect"] = ""
    merged["ca_level"] = ""
    merged["scenario"] = ""
    merged["estimate"] = merged["coef"]
    merged["model_se"] = merged["se"]
    merged["model_p"] = merged["p"]
    merged["model_ci_lo_95"] = merged["coef"] - 1.96 * merged["se"]
    merged["model_ci_hi_95"] = merged["coef"] + 1.96 * merged["se"]
    for col in [
        "ca_value",
        "hazard_level",
        "delta_te_point",
        "delta_ln_yield_point",
        "delta_ln_yield_ci_lo",
        "delta_ln_yield_ci_hi",
        "pct_delta_point",
        "pct_delta_bs_se",
        "pct_delta_ci_lo",
        "pct_delta_ci_hi",
    ]:
        merged[col] = np.nan
    return empty_str_cols(merged, LOCATOR_COLS + VALUE_COLS)[LOCATOR_COLS + VALUE_COLS]


def build_iede_rows() -> pd.DataFrame:
    iede = load_filtered("f4_b067_iede_bootstrap_summary.csv")
    iede["record_type"] = "iede_effect"
    iede["equation"] = "derived"
    iede["depvar"] = "ln_yield"
    iede["term"] = iede["effect"]
    iede["role"] = iede["effect"]
    iede["scenario"] = ""
    iede["estimate"] = iede["point_est"]
    iede["model_se"] = np.nan
    iede["model_p"] = np.nan
    iede["model_ci_lo_95"] = np.nan
    iede["model_ci_hi_95"] = np.nan
    iede["bs_ci_lo_95"] = iede["ci_lo_pct"]
    iede["bs_ci_hi_95"] = iede["ci_hi_pct"]
    iede["sign"] = np.where(iede["estimate"].gt(0), "positive", np.where(iede["estimate"].lt(0), "negative", "zero"))
    iede["sig_005"] = ""
    iede["sig_010"] = ""
    iede["sign_sig_005"] = ""
    iede["sign_sig_010"] = ""
    for col in ["N_model", "N_grids", "r2_within"]:
        iede[col] = np.nan
    for col in [
        "hazard_level",
        "delta_te_point",
        "delta_ln_yield_point",
        "delta_ln_yield_ci_lo",
        "delta_ln_yield_ci_hi",
        "pct_delta_point",
        "pct_delta_bs_se",
        "pct_delta_ci_lo",
        "pct_delta_ci_hi",
    ]:
        iede[col] = np.nan
    return empty_str_cols(iede, LOCATOR_COLS + VALUE_COLS)[LOCATOR_COLS + VALUE_COLS]


def build_counterfactual_rows() -> pd.DataFrame:
    cf = load_filtered("f4_b067_counterfactual_summary.csv")
    cf["record_type"] = "counterfactual"
    cf["equation"] = "derived"
    cf["depvar"] = "ln_yield"
    cf["term"] = "TE_P75_minus_P25_times_hazard"
    cf["role"] = "counterfactual_contrast"
    cf["effect"] = "pct_delta"
    cf["ca_level"] = "P75_minus_P25"
    cf["estimate"] = cf["pct_delta_point"]
    cf["model_se"] = np.nan
    cf["model_p"] = np.nan
    cf["model_ci_lo_95"] = np.nan
    cf["model_ci_hi_95"] = np.nan
    cf["bs_se"] = cf["pct_delta_bs_se"]
    cf["bs_ci_lo_95"] = cf["pct_delta_ci_lo"]
    cf["bs_ci_hi_95"] = cf["pct_delta_ci_hi"]
    cf["sign"] = np.where(cf["estimate"].gt(0), "positive", np.where(cf["estimate"].lt(0), "negative", "zero"))
    cf["sig_005"] = ""
    cf["sig_010"] = ""
    cf["sign_sig_005"] = ""
    cf["sign_sig_010"] = ""
    for col in ["N_model", "N_grids", "r2_within", "ca_value"]:
        cf[col] = np.nan
    return empty_str_cols(cf, LOCATOR_COLS + VALUE_COLS)[LOCATOR_COLS + VALUE_COLS]


def write_dictionary(table: pd.DataFrame) -> None:
    rhs = table.loc[table["record_type"].eq("rhs_coefficient")]
    iede = table.loc[table["record_type"].eq("iede_effect")]
    cf = table.loc[table["record_type"].eq("counterfactual")]
    lines = [
        "# F4-B067 mean/raw 统一系数与效应表说明",
        "",
        f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 数据来源与筛选",
        "",
        f"本表来自 `{RUN_DIR}` 下已经完成的 F4-B067 full run 输出，不重新估计模型。筛选条件固定为 `branch=mean` 且 `transform=raw`。样本 scale 只有 `B067`。",
        "",
        "## 主输出",
        "",
        f"- 统一长表: `{OUT_CSV}`",
        f"- 行数: {len(table)}",
        f"- RHS coefficient 行数: {len(rhs)}",
        f"- IE/DE/TE 行数: {len(iede)}",
        f"- counterfactual 行数: {len(cf)}",
        "",
        "## record_type",
        "",
        "`rhs_coefficient` 表示回归右侧变量的系数。该类行包含 `estimate/model_se/model_p/model_ci_lo_95/model_ci_hi_95`。如果 `role` 是 `a1/a3/b/c1/c3`，还会包含 `bs_se/bs_ci_lo_95/bs_ci_hi_95/N_boot`；控制变量没有 bootstrap 区间。",
        "",
        "`iede_effect` 表示由两方程系数派生的 `IE/DE/TE`。该类行使用 `effect` 和 `ca_level` 定位，例如 `effect=TE, ca_level=P75`。该类行没有模型 p 值，主要读取 `estimate/bs_se/bs_ci_lo_95/bs_ci_hi_95/N_boot`。",
        "",
        "`counterfactual` 表示情景差异，定义为 `[TE(P75)-TE(P25)] * hazard_level`，并转换为百分比差异 `pct_delta`。该类行的主要读数是 `estimate`，等于 `pct_delta_point`。",
        "",
        "## 定位字段",
        "",
        "`sample_id/layer/subgroup_dim/subgroup/hazard/transform/branch/mediator_tag/mediator` 用于定位样本层、子组、hazard 和 mediator。当前 `transform` 全部为 `raw`，`branch` 全部为 `mean`。",
        "",
        "`equation` 区分 `mediator`、`outcome` 与 `derived`。`depvar` 是对应被解释变量。`term` 是 RHS 变量名或派生效应名。`role` 是理论角色。",
        "",
        "## role",
        "",
        "`a1` 是 mediator 方程中 hazard 主效应系数。`a3` 是 mediator 方程中 SR×hazard 交互项系数。`b` 是 outcome 方程中 mediator 系数。`c1` 是 outcome 方程中 hazard 主效应系数。`c3` 是 outcome 方程中 SR×hazard 交互项系数。`sr_main_in_mediator` 和 `sr_main_in_outcome` 是 SR 主效应。`control_or_covariate` 是伴随 hazard 或气候控制变量。",
        "",
        "## 显著性与区间",
        "",
        "`model_se/model_p/model_ci_lo_95/model_ci_hi_95` 来自原 FE-OLS 模型的系数标准误、p 值和 95% 常规区间。`sig_005` 和 `sig_010` 分别表示 `p<0.05` 与 `p<0.10`。`sign_sig_005/sign_sig_010` 同时编码正负号和显著性。",
        "",
        "`bs_se/bs_ci_lo_95/bs_ci_hi_95` 来自 cluster wild score bootstrap 的百分位区间。对 RHS 系数，仅 `a1/a3/b/c1/c3` 有 bootstrap 区间；对 `IE/DE/TE` 和 counterfactual，区间来自 bootstrap draws。",
        "",
        "## 程序读取建议",
        "",
        "若要提取某个回归系数，筛选 `record_type=rhs_coefficient`，再用 `layer/subgroup/hazard/equation/term` 定位。若要判断显著性，读取 `model_p/sig_005/sig_010/sign_sig_010`。若要读取机制效应，筛选 `record_type=iede_effect`，再用 `effect` 与 `ca_level` 定位。若要读取情景差异，筛选 `record_type=counterfactual`，再用 `scenario` 定位。",
    ]
    DICT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    table = pd.concat([build_rhs_rows(), build_iede_rows(), build_counterfactual_rows()], ignore_index=True)
    table.sort_values(
        [
            "record_type",
            "layer",
            "subgroup_dim",
            "subgroup",
            "hazard",
            "equation",
            "role",
            "term",
            "effect",
            "ca_level",
            "scenario",
        ],
        inplace=True,
        kind="stable",
    )
    table.to_csv(OUT_CSV, index=False, encoding="utf-8")
    write_dictionary(table)
    print(
        {
            "output": str(OUT_CSV),
            "dictionary": str(DICT_MD),
            "rows": int(len(table)),
            "rhs_rows": int(table["record_type"].eq("rhs_coefficient").sum()),
            "iede_rows": int(table["record_type"].eq("iede_effect").sum()),
            "counterfactual_rows": int(table["record_type"].eq("counterfactual").sum()),
        },
        flush=True,
    )


if __name__ == "__main__":
    main()
