"""
Single-hazard grouped-window screen for the fixed 128 main+GGCP10 variants.

Each regression includes multiple windows of one hazard family at a time. This
tests whether window ordering changes once neighboring windows of the same
hazard are controlled jointly.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from bio_window_filter_128 import (
    BASE_DTA,
    OUT_DIR,
    fit_fe_ols,
    load_panel,
    unique_variants,
    var_for,
)


PREFIX = "bio_window_128_grouped_single_hazard"
GROUPS = {
    "v3pm10_hepm10": ("v3pm10", "hepm10"),
    "v3pre30_v3he_hema": ("v3pre30", "v3he", "hema"),
    "v3he_hema": ("v3he", "hema"),
}
HAZARDS = ("drought", "heat32", "heat35", "hotdry")
H35_COLUMNS = [
    "grid_id",
    "year",
    "hdd_ge35",
    "hdd_ge35_v3pre30",
    "hdd_ge35_v3pm10",
    "hdd_ge35_hepm10",
    "hdd_ge35_v3he",
    "hdd_ge35_hema",
]


def h35_var(window: str) -> str:
    return "hdd_ge35" if window == "full" else f"hdd_ge35_{window}"


def hazard_var(hazard: str, window: str) -> str:
    if hazard == "drought":
        return var_for("D", window)
    if hazard == "heat32":
        return var_for("H", window)
    if hazard == "heat35":
        return h35_var(window)
    if hazard == "hotdry":
        return var_for("HD", window)
    raise ValueError(hazard)


def add_hdd35(df: pd.DataFrame) -> pd.DataFrame:
    h35 = pd.read_stata(BASE_DTA, columns=H35_COLUMNS)
    return df.merge(h35, on=["grid_id", "year"], how="left", validate="one_to_one")


def grouped_controls(windows: tuple[str, ...]) -> list[str]:
    controls: list[str] = ["ca", "irr_frac", "aridity"]
    for w in windows:
        controls.extend([var_for("P", w), var_for("ET0", w), var_for("GDD", w)])
    return list(dict.fromkeys(controls))


def xvars_for_group(hazard: str, windows: tuple[str, ...]) -> list[str]:
    hazard_terms = [hazard_var(hazard, w) for w in windows]
    return hazard_terms + grouped_controls(windows)


def row_for_term(meta: dict[str, object], group: str, hazard: str, window: str, res: dict[str, float]) -> dict[str, object]:
    xvar = hazard_var(hazard, window)
    b = res[f"b:{xvar}"]
    p = res[f"p:{xvar}"]
    return {
        "sample_id": meta["sample_id"],
        "group": group,
        "hazard": hazard,
        "window": window,
        "xvar": xvar,
        "coef": b,
        "se": res[f"se:{xvar}"],
        "p": p,
        "neg_sig_005": bool(b < 0 and p < 0.05),
        "N_sample": meta["N_sample"],
        "N_model": int(res["N_model"]),
        "N_grids_sample": meta["N_grids_sample"],
        "N_grids_model": int(res["N_grids_model"]),
        "r2_within": res["r2_within"],
    }


def decide_group(coef_df: pd.DataFrame, sample_id: str, group: str, hazard: str) -> dict[str, object]:
    sub = coef_df[
        coef_df["sample_id"].eq(sample_id) & coef_df["group"].eq(group) & coef_df["hazard"].eq(hazard)
    ].copy()
    sub["is_most_negative"] = sub["coef"].eq(sub["coef"].min())
    b = dict(zip(sub["window"], sub["coef"]))
    p = dict(zip(sub["window"], sub["p"]))
    neg = dict(zip(sub["window"], sub["neg_sig_005"]))
    best_window = str(sub.loc[sub["coef"].idxmin(), "window"])

    hepm10_neg = bool(neg.get("hepm10", False))
    hepm10_most_negative = bool(best_window == "hepm10")
    hema_neg = bool(neg.get("hema", False))
    hema_most_negative = bool(best_window == "hema")
    v3he_neg = bool(neg.get("v3he", False))
    v3pm10_neg = bool(neg.get("v3pm10", False))
    v3pre30_neg = bool(neg.get("v3pre30", False))

    if group == "v3pm10_hepm10":
        target_signal = hepm10_neg
        target_order = hepm10_most_negative
        placebo_redflag = v3pm10_neg
    elif group == "v3pre30_v3he_hema":
        if hazard == "drought":
            target_signal = bool(hema_neg or v3he_neg)
            target_order = bool(b.get("hema", np.inf) <= b.get("v3he", np.inf))
            placebo_redflag = v3pre30_neg
        elif hazard in ("heat32", "heat35", "hotdry"):
            target_signal = hema_neg
            target_order = hema_most_negative
            placebo_redflag = bool(v3pre30_neg or v3he_neg)
        else:
            raise ValueError(hazard)
    elif group == "v3he_hema":
        if hazard == "drought":
            target_signal = bool(hema_neg or v3he_neg)
            target_order = bool(b.get("hema", np.inf) <= b.get("v3he", np.inf))
            placebo_redflag = False
        elif hazard in ("heat32", "heat35", "hotdry"):
            target_signal = hema_neg
            target_order = hema_most_negative
            placebo_redflag = v3he_neg
        else:
            raise ValueError(hazard)
    else:
        raise ValueError(group)

    core_no_placebo = bool(target_signal)
    core_with_placebo = bool(target_signal and not placebo_redflag)
    strict_no_placebo = bool(target_signal and target_order)
    strict_with_placebo = bool(target_signal and target_order and not placebo_redflag)

    out: dict[str, object] = {
        "sample_id": sample_id,
        "group": group,
        "hazard": hazard,
        "best_window": best_window,
        "target_signal": target_signal,
        "target_order": target_order,
        "placebo_redflag": placebo_redflag,
        "core_no_placebo": core_no_placebo,
        "core_with_placebo": core_with_placebo,
        "strict_no_placebo": strict_no_placebo,
        "strict_with_placebo": strict_with_placebo,
    }
    for w in GROUPS[group]:
        out[f"b_{w}"] = float(b[w])
        out[f"p_{w}"] = float(p[w])
        out[f"neg_sig_{w}"] = bool(neg[w])
    return out


def write_summary(coef_df: pd.DataFrame, dec_df: pd.DataFrame) -> None:
    window_summary = (
        coef_df.groupby(["group", "hazard", "window"])
        .agg(
            coef_median=("coef", "median"),
            coef_min=("coef", "min"),
            coef_max=("coef", "max"),
            p_median=("p", "median"),
            neg_sig_count=("neg_sig_005", "sum"),
            n=("sample_id", "count"),
        )
        .reset_index()
    )
    decision_summary = (
        dec_df.groupby(["group", "hazard"])
        .agg(
            n=("sample_id", "size"),
            target_signal=("target_signal", "sum"),
            target_order=("target_order", "sum"),
            placebo_redflag=("placebo_redflag", "sum"),
            core_no_placebo=("core_no_placebo", "sum"),
            core_with_placebo=("core_with_placebo", "sum"),
            strict_no_placebo=("strict_no_placebo", "sum"),
            strict_with_placebo=("strict_with_placebo", "sum"),
        )
        .reset_index()
    )
    best_counts = dec_df.groupby(["group", "hazard", "best_window"]).size().reset_index(name="n")
    window_summary.to_csv(OUT_DIR / f"{PREFIX}_window_summary.csv", index=False, encoding="utf-8-sig")
    decision_summary.to_csv(OUT_DIR / f"{PREFIX}_decision_summary.csv", index=False, encoding="utf-8-sig")
    best_counts.to_csv(OUT_DIR / f"{PREFIX}_best_window_counts.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# Single-hazard grouped-window screen",
        "",
        "固定样本前提：`main_sample == 1` 且 `ggcp10_maize_frac >= 0.05`；其余 8 个规则平行组合去重为 128 个样本版本。",
        "每个方程只放一个 hazard family 的多个窗口变量，不放 SR 交互项。",
        "",
        "## Decision summary",
        "",
        "| group | hazard | target signal | target order | placebo redflag | core no placebo | core with placebo | strict no placebo | strict with placebo |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in decision_summary.to_dict("records"):
        lines.append(
            f"| {r['group']} | {r['hazard']} | {int(r['target_signal'])}/128 | "
            f"{int(r['target_order'])}/128 | {int(r['placebo_redflag'])}/128 | "
            f"{int(r['core_no_placebo'])}/128 | {int(r['core_with_placebo'])}/128 | "
            f"{int(r['strict_no_placebo'])}/128 | {int(r['strict_with_placebo'])}/128 |"
        )
    lines.extend(
        [
            "",
            "## Best-window counts",
            "",
            "| group | hazard | best window | n |",
            "|---|---|---|---:|",
        ]
    )
    for r in best_counts.to_dict("records"):
        lines.append(f"| {r['group']} | {r['hazard']} | {r['best_window']} | {int(r['n'])} |")
    lines.extend(
        [
            "",
            "## Output files",
            "",
            f"- `{PREFIX}_coefficients.csv`",
            f"- `{PREFIX}_decisions.csv`",
            f"- `{PREFIX}_window_summary.csv`",
            f"- `{PREFIX}_decision_summary.csv`",
            f"- `{PREFIX}_best_window_counts.csv`",
            f"- `{PREFIX}_summary.md`",
            "",
        ]
    )
    (OUT_DIR / f"{PREFIX}_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    df = add_hdd35(load_panel())
    variants = unique_variants(df)
    rows: list[dict[str, object]] = []
    for i, meta in enumerate(variants, start=1):
        sub = df.loc[meta["mask"]].copy()
        for group, windows in GROUPS.items():
            for hazard in HAZARDS:
                res = fit_fe_ols(sub, "ln_yield", xvars_for_group(hazard, windows))
                for window in windows:
                    rows.append(row_for_term(meta, group, hazard, window, res))
        if i % 16 == 0:
            print(f"processed {i}/{len(variants)} variants")

    coef_df = pd.DataFrame(rows)
    coef_df.to_csv(OUT_DIR / f"{PREFIX}_coefficients.csv", index=False, encoding="utf-8-sig")
    dec_rows: list[dict[str, object]] = []
    for sample_id in coef_df["sample_id"].drop_duplicates():
        for group in GROUPS:
            for hazard in HAZARDS:
                dec_rows.append(decide_group(coef_df, str(sample_id), group, hazard))
    dec_df = pd.DataFrame(dec_rows)
    dec_df.to_csv(OUT_DIR / f"{PREFIX}_decisions.csv", index=False, encoding="utf-8-sig")
    write_summary(coef_df, dec_df)
    print(f"wrote outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
