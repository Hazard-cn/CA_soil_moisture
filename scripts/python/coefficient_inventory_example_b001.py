"""
Coefficient inventory for one fixed data version.

Example version:
- B001 = main_sample == 1 and ggcp10_maize_frac >= 0.05
- no optional cleaning rules

The script separates baseline equations from subgroup heterogeneity equations
and counts original regression coefficients, not derived IE/DE/TE quantities.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ggcp10_parallel_rules_69038_search import fit_fe_ols, load_panel, rhs_for
from bio_window_filter_128 import OUT_DIR, unique_variants


PREFIX = "coefficient_inventory_B001"
SAMPLE_ID = "B001"
HAZARDS = ("drought", "heat", "hotdry")
TRANSFORMS = ("raw", "w")
MEDIATORS = {
    "mean_root": ("mean", "gleam_smrz_mean"),
    "dry_mdf_p10_sfc": ("dry", "v6mdf_p10_fn_gss"),
}
HET_DIMS = {
    "maize_zone": "maize_zone",
    "irr_group": "irr_group",
}
KEY_ROLES = ("a1", "a3", "b", "c1", "c3")


def get_b001(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    variants = unique_variants(df)
    meta = next(v for v in variants if v["sample_id"] == SAMPLE_ID)
    return df.loc[meta["mask"]].copy(), {k: v for k, v in meta.items() if k != "mask"}


def fit_spec_rows(
    sub: pd.DataFrame,
    layer: str,
    subgroup_dim: str,
    subgroup: str,
    hazard: str,
    transform: str,
    mediator_tag: str,
    branch: str,
    mediator_base: str,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    sx = "w" if transform == "w" else "raw"
    transform_label = "winsor_1_99" if sx == "w" else "raw"
    mediator = f"{mediator_base}_{sx}"
    y, ca, mediator_rhs, outcome_rhs, hazard_var, sr_var = rhs_for(hazard, sx, mediator)

    rows: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    try:
        mres = fit_fe_ols(sub, mediator, mediator_rhs)
        yres = fit_fe_ols(sub, y, outcome_rhs)
    except Exception as exc:
        skipped.append(
            {
                "sample_id": SAMPLE_ID,
                "layer": layer,
                "subgroup_dim": subgroup_dim,
                "subgroup": subgroup,
                "hazard": hazard,
                "transform": transform_label,
                "mediator_tag": mediator_tag,
                "reason": str(exc),
                "N_rows_before_dropna": len(sub),
            }
        )
        return rows, skipped

    spec_id = f"{SAMPLE_ID}_{layer}_{subgroup_dim}_{subgroup}_{transform_label}_{mediator_tag}_{hazard}"
    common = {
        "sample_id": SAMPLE_ID,
        "spec_id": spec_id,
        "layer": layer,
        "subgroup_dim": subgroup_dim,
        "subgroup": subgroup,
        "hazard": hazard,
        "transform": transform_label,
        "branch": branch,
        "mediator_tag": mediator_tag,
        "mediator": mediator,
    }
    role_map_m = {hazard_var: "a1", sr_var: "a3", ca: "sr_main_in_mediator"}
    role_map_y = {mediator: "b", hazard_var: "c1", sr_var: "c3", ca: "sr_main_in_outcome"}
    for eq_name, yvar, xvars, res, role_map in (
        ("mediator", mediator, mediator_rhs, mres, role_map_m),
        ("outcome", y, outcome_rhs, yres, role_map_y),
    ):
        for x in xvars:
            rows.append(
                {
                    **common,
                    "equation": eq_name,
                    "depvar": yvar,
                    "term": x,
                    "role": role_map.get(x, "control_or_covariate"),
                    "coef": res[f"b:{x}"],
                    "se": res[f"se:{x}"],
                    "p": res[f"p:{x}"],
                    "N_model": int(res["N"]),
                    "N_grids": int(res["clusters"]),
                    "r2_within": res["r2_within"],
                }
            )
    return rows, skipped


def main() -> None:
    df = load_panel()
    base, meta = get_b001(df)

    rows: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    for transform in TRANSFORMS:
        for hazard in HAZARDS:
            for mediator_tag, (branch, mediator_base) in MEDIATORS.items():
                r, s = fit_spec_rows(
                    base,
                    "baseline",
                    "all",
                    "all",
                    hazard,
                    transform,
                    mediator_tag,
                    branch,
                    mediator_base,
                )
                rows.extend(r)
                skipped.extend(s)

    for dim_name, col in HET_DIMS.items():
        values = [v for v in sorted(base[col].dropna().astype(str).unique()) if v.lower() not in ("", "nan")]
        for value in values:
            sub = base.loc[base[col].astype(str).eq(value)].copy()
            for transform in TRANSFORMS:
                for hazard in HAZARDS:
                    for mediator_tag, (branch, mediator_base) in MEDIATORS.items():
                        r, s = fit_spec_rows(
                            sub,
                            "heterogeneity",
                            dim_name,
                            value,
                            hazard,
                            transform,
                            mediator_tag,
                            branch,
                            mediator_base,
                        )
                        rows.extend(r)
                        skipped.extend(s)

    coef = pd.DataFrame(rows)
    skip = pd.DataFrame(skipped)
    coef.to_csv(OUT_DIR / f"{PREFIX}_coefficients.csv", index=False, encoding="utf-8-sig")
    skip.to_csv(OUT_DIR / f"{PREFIX}_skipped.csv", index=False, encoding="utf-8-sig")

    spec_count = coef.drop_duplicates(
        ["layer", "subgroup_dim", "subgroup", "hazard", "transform", "mediator_tag"]
    )
    eq_count = coef.drop_duplicates(
        ["layer", "subgroup_dim", "subgroup", "hazard", "transform", "mediator_tag", "equation"]
    )
    summary = (
        coef.assign(is_key=coef["role"].isin(KEY_ROLES))
        .groupby(["layer", "subgroup_dim"])
        .agg(
            regression_specs=("spec_id", "nunique"),
            equations=("equation", "count"),
            coefficient_rows=("term", "count"),
            key_coefficient_rows=("is_key", "sum"),
            min_N_model=("N_model", "min"),
            max_N_model=("N_model", "max"),
        )
        .reset_index()
    )
    # The previous equations count counted terms; replace with distinct equation ids.
    eq_summary = (
        eq_count.groupby(["layer", "subgroup_dim"]).size().reset_index(name="equations_distinct")
    )
    summary = summary.drop(columns=["equations"]).merge(eq_summary, on=["layer", "subgroup_dim"], how="left")
    summary = summary[
        [
            "layer",
            "subgroup_dim",
            "regression_specs",
            "equations_distinct",
            "coefficient_rows",
            "key_coefficient_rows",
            "min_N_model",
            "max_N_model",
        ]
    ]
    summary.to_csv(OUT_DIR / f"{PREFIX}_summary.csv", index=False, encoding="utf-8-sig")

    by_equation = (
        coef.assign(is_key=coef["role"].isin(KEY_ROLES))
        .groupby(["layer", "subgroup_dim", "equation"])
        .agg(
            equations=("spec_id", "nunique"),
            coefficient_rows=("term", "count"),
            key_coefficient_rows=("is_key", "sum"),
        )
        .reset_index()
    )
    by_equation.to_csv(OUT_DIR / f"{PREFIX}_by_equation.csv", index=False, encoding="utf-8-sig")

    by_spec = (
        coef.assign(is_key=coef["role"].isin(KEY_ROLES))
        .groupby(["layer", "subgroup_dim", "subgroup", "hazard", "transform", "mediator_tag"])
        .agg(
            equations=("equation", "nunique"),
            coefficient_rows=("term", "count"),
            key_coefficient_rows=("is_key", "sum"),
            N_model_min=("N_model", "min"),
            N_model_max=("N_model", "max"),
        )
        .reset_index()
    )
    by_spec.to_csv(OUT_DIR / f"{PREFIX}_by_spec.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# Coefficient inventory for B001",
        "",
        "B001 定义：`main_sample == 1` 且 `ggcp10_maize_frac >= 0.05`，其余 8 个平行清洗规则均不启用。",
        f"样本规模：N={int(meta['N_sample'])}，grid={int(meta['N_grids_sample'])}。",
        "",
        "baseline 方程：full-season hazard，两条机制方程，hazard × transform × mediator。",
        "heterogeneity 方程：同一机制方程在 `maize_zone` 与 `irr_group` 的 subgroup 内重估。",
        "这里计数的是原始回归 RHS 系数；IE/DE/TE、bootstrap CI 不算作回归系数。",
        "",
        "## Summary",
        "",
        "| layer | subgroup dim | regression specs | equations | all coefficients | key coefficients | N range |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in summary.to_dict("records"):
        lines.append(
            f"| {r['layer']} | {r['subgroup_dim']} | {int(r['regression_specs'])} | "
            f"{int(r['equations_distinct'])} | {int(r['coefficient_rows'])} | "
            f"{int(r['key_coefficient_rows'])} | {int(r['min_N_model'])}-{int(r['max_N_model'])} |"
        )
    lines.extend(
        [
            "",
            "## Equation templates",
            "",
            "Mediator equation: `M = hazard + ca + SRxHazard + companion hazard controls + climate controls + grid FE + year FE`。",
            "Outcome equation: `ln_yield = hazard + ca + SRxHazard + M + companion hazard controls + climate controls + grid FE + year FE`。",
            "关键系数定义：mediator 方程中的 `a1=hazard`、`a3=SRxHazard`；outcome 方程中的 `b=M`、`c1=hazard`、`c3=SRxHazard`。",
            "",
            "## Output files",
            "",
            f"- `{PREFIX}_coefficients.csv`",
            f"- `{PREFIX}_summary.csv`",
            f"- `{PREFIX}_by_equation.csv`",
            f"- `{PREFIX}_by_spec.csv`",
            f"- `{PREFIX}_skipped.csv`",
            f"- `{PREFIX}_summary.md`",
            "",
        ]
    )
    (OUT_DIR / f"{PREFIX}_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
