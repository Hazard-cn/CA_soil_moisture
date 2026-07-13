"""
Check whether replacing heat HDD32 with HDD35 improves the biological window
screen for the fixed 128 main+GGCP10 sample variants.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from bio_window_filter_128 import (
    BASE_DTA,
    OUT_DIR,
    WINDOWS,
    fit_fe_ols,
    load_panel,
    unique_variants,
    var_for,
)


PREFIX = "bio_window_128_heat35"
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


def add_hdd35(df: pd.DataFrame) -> pd.DataFrame:
    h35 = pd.read_stata(BASE_DTA, columns=H35_COLUMNS)
    return df.merge(h35, on=["grid_id", "year"], how="left", validate="one_to_one")


def xvars_for_heat35(window: str) -> list[str]:
    return [
        h35_var(window),
        var_for("D", window),
        var_for("W", window),
        "ca",
        var_for("P", window),
        var_for("ET0", window),
        var_for("GDD", window),
        "irr_frac",
        "aridity",
    ]


def decision(rows: pd.DataFrame, sample_id: str) -> dict[str, object]:
    h = rows[rows["sample_id"].eq(sample_id)].set_index("window")
    b = h["coef"].to_dict()
    neg_sig = h["neg_sig_005"].to_dict()
    flowering_signal = bool(neg_sig["hepm10"])
    placebo_clean = not any(bool(neg_sig[w]) for w in ("v3pre30", "v3pm10", "v3he"))
    rank_pass = bool(b["hepm10"] <= b["hema"] and b["hepm10"] <= b["v3he"])
    core_pass = flowering_signal and placebo_clean
    strict_pass = core_pass and rank_pass
    if not flowering_signal:
        fail_reason = "hepm10_not_negative_significant"
    elif not placebo_clean:
        bad = [w for w in ("v3pre30", "v3pm10", "v3he") if bool(neg_sig[w])]
        fail_reason = "placebo_negative_significant:" + ",".join(bad)
    elif not rank_pass:
        fail_reason = "biological_ordering_fail"
    else:
        fail_reason = "pass"
    return {
        "sample_id": sample_id,
        "hazard": "heat35",
        "flowering_signal": flowering_signal,
        "placebo_clean": placebo_clean,
        "rank_pass": rank_pass,
        "core_pass": core_pass,
        "strict_pass": strict_pass,
        "no_placebo_core": flowering_signal,
        "no_placebo_strict": flowering_signal and rank_pass,
        "fail_reason": fail_reason,
        "b_v3pre30": b["v3pre30"],
        "p_v3pre30": float(h.loc["v3pre30", "p"]),
        "b_v3pm10": b["v3pm10"],
        "p_v3pm10": float(h.loc["v3pm10", "p"]),
        "b_hepm10": b["hepm10"],
        "p_hepm10": float(h.loc["hepm10", "p"]),
        "b_v3he": b["v3he"],
        "p_v3he": float(h.loc["v3he", "p"]),
        "b_hema": b["hema"],
        "p_hema": float(h.loc["hema", "p"]),
    }


def write_summary(coef_df: pd.DataFrame, dec_df: pd.DataFrame) -> None:
    by_window = (
        coef_df[coef_df["window"].isin(["v3pre30", "v3pm10", "hepm10", "v3he", "hema"])]
        .groupby("window")
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
    by_window.to_csv(OUT_DIR / f"{PREFIX}_window_summary.csv", index=False, encoding="utf-8-sig")

    old = pd.read_csv(OUT_DIR / "bio_window_128_family_hazard_decisions.csv")
    old_heat = old[old["hazard"].eq("heat")]
    lines = [
        "# Heat HDD35 biological-window check",
        "",
        "固定样本前提：`main_sample == 1` 且 `ggcp10_maize_frac >= 0.05`。",
        "只替换 heat 主效应变量：`hdd_ge32_*` -> `hdd_ge35_*`。",
        "",
        "| metric | HDD32 heat | HDD35 heat |",
        "|---|---:|---:|",
        f"| hepm10 negative significant | {int(old_heat['flowering_signal'].sum())}/128 | {int(dec_df['flowering_signal'].sum())}/128 |",
        f"| placebo clean | {int(old_heat['placebo_clean'].sum())}/128 | {int(dec_df['placebo_clean'].sum())}/128 |",
        f"| ordering pass | {int(old_heat['rank_pass'].sum())}/128 | {int(dec_df['rank_pass'].sum())}/128 |",
        f"| core pass | {int(old_heat['core_pass'].sum())}/128 | {int(dec_df['core_pass'].sum())}/128 |",
        f"| strict pass | {int(old_heat['strict_pass'].sum())}/128 | {int(dec_df['strict_pass'].sum())}/128 |",
        "",
        "## HDD35 by window",
        "",
        "| window | median coef | min coef | max coef | median p | negative significant n |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in by_window.to_dict("records"):
        lines.append(
            f"| {r['window']} | {r['coef_median']:.6g} | {r['coef_min']:.6g} | "
            f"{r['coef_max']:.6g} | {r['p_median']:.6g} | {int(r['neg_sig_count'])} |"
        )
    lines.extend(
        [
            "",
            "## Output files",
            "",
            f"- `{PREFIX}_window_coefficients.csv`",
            f"- `{PREFIX}_decisions.csv`",
            f"- `{PREFIX}_window_summary.csv`",
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
        for window in WINDOWS:
            xvar = h35_var(window)
            res = fit_fe_ols(sub, "ln_yield", xvars_for_heat35(window))
            b = res[f"b:{xvar}"]
            p = res[f"p:{xvar}"]
            rows.append(
                {
                    "sample_id": meta["sample_id"],
                    "hazard": "heat35",
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
            )
        if i % 16 == 0:
            print(f"processed {i}/{len(variants)} variants")
    coef_df = pd.DataFrame(rows)
    coef_df.to_csv(OUT_DIR / f"{PREFIX}_window_coefficients.csv", index=False, encoding="utf-8-sig")
    dec_df = pd.DataFrame([decision(coef_df, str(s)) for s in coef_df["sample_id"].drop_duplicates()])
    dec_df.to_csv(OUT_DIR / f"{PREFIX}_decisions.csv", index=False, encoding="utf-8-sig")
    write_summary(coef_df, dec_df)
    print(f"wrote outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
