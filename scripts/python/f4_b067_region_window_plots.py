"""
Region-by-time-window diagnostics for the current F4-B067 scale.

Scope:
- sample scale: B067, i.e. zone_core=1, sr_within=1, years_ge3=0,
  stable_province=0, with the other optional rules off
- regions: NE, HHH, NW, SW
- windows: full, v3pre30, v3pm10, hepm10, v3he, hema
- outputs: coefficient table and two coefficient plots for c1 and c3

The outcome equation is a window-level extension of the current mean/raw
outcome leg:
    ln_yield = hazard_window + ca + ca*hazard_window
               + companion hazards + window climate controls
               + grid FE + year FE
"""

from __future__ import annotations

import math
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from bio_window_filter_128 import fit_fe_ols, load_panel, unique_variants, var_for


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
OUT_DIR = PROJ / "temp/2026-06-04_f4_b067_region_window"
FIG_DIR = PROJ / "output/figures" / ("0604" + chr(0x6C47) + chr(0x62A5))
REPORT_MD = PROJ / "quality_reports/2026-06-04_f4_b067_region_window_diagnostics.md"

SAMPLE_ID = "B067"
REGIONS = ("NE", "HHH", "NW", "SW")
WINDOWS = ("full", "v3pre30", "v3pm10", "hepm10", "v3he", "hema")
HAZARDS = ("drought", "heat", "hotdry")
HAZARD_LABELS = {"drought": "Drought", "heat": "Heat", "hotdry": "Hot-dry"}
WINDOW_LABELS = {
    "full": "Full",
    "v3pre30": "V3-30",
    "v3pm10": "V3±10",
    "hepm10": "Flowering",
    "v3he": "V3-HE",
    "hema": "HE-MA",
}
REGION_LABELS = {"NE": "NE", "HHH": "HHH", "NW": "NW", "SW": "SW"}


def hazard_var(hazard: str, window: str) -> str:
    if hazard == "drought":
        return var_for("D", window)
    if hazard == "heat":
        return var_for("H", window)
    if hazard == "hotdry":
        return var_for("HD", window)
    raise ValueError(hazard)


def companion_hazards(hazard: str, window: str) -> list[str]:
    d = var_for("D", window)
    h = var_for("H", window)
    hd = var_for("HD", window)
    w = var_for("W", window)
    if hazard == "drought":
        return [w, h, hd]
    if hazard == "heat":
        return [d, w, hd]
    if hazard == "hotdry":
        return [d, h, w]
    raise ValueError(hazard)


def window_controls(window: str) -> list[str]:
    return [
        var_for("P", window),
        var_for("ET0", window),
        var_for("GDD", window),
        "irr_frac",
        "aridity",
    ]


def add_window_interactions(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for hazard in HAZARDS:
        for window in WINDOWS:
            hv = hazard_var(hazard, window)
            out[f"SR_x_{hv}"] = out["ca"] * out[hv]
    return out


def b067_sample(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    variants = unique_variants(df)
    meta = next(v for v in variants if v["sample_id"] == SAMPLE_ID)
    sub = df.loc[meta["mask"]].copy()
    return sub, {k: v for k, v in meta.items() if k != "mask"}


def fit_region_window(base: pd.DataFrame, meta: dict[str, object]) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    for region in REGIONS:
        reg = base.loc[base["maize_zone"].astype(str).eq(region)].copy()
        for hazard in HAZARDS:
            for window in WINDOWS:
                hv = hazard_var(hazard, window)
                inter = f"SR_x_{hv}"
                xvars = [hv, "ca", inter, *companion_hazards(hazard, window), *window_controls(window)]
                xvars = list(dict.fromkeys(xvars))
                try:
                    res = fit_fe_ols(reg, "ln_yield", xvars)
                except Exception as exc:  # noqa: BLE001
                    skipped.append(
                        {
                            "sample_id": SAMPLE_ID,
                            "region": region,
                            "hazard": hazard,
                            "window": window,
                            "reason": str(exc),
                            "N_rows_before_dropna": int(len(reg)),
                            "N_grids_before_dropna": int(reg["grid_id"].nunique()),
                        }
                    )
                    continue
                for term, role in ((hv, "c1"), (inter, "c3")):
                    coef = float(res[f"b:{term}"])
                    se = float(res[f"se:{term}"])
                    p = float(res[f"p:{term}"])
                    rows.append(
                        {
                            "sample_id": SAMPLE_ID,
                            "region": region,
                            "region_label": REGION_LABELS[region],
                            "hazard": hazard,
                            "hazard_label": HAZARD_LABELS[hazard],
                            "window": window,
                            "window_label": WINDOW_LABELS[window],
                            "term": term,
                            "role": role,
                            "coef": coef,
                            "se": se,
                            "p": p,
                            "ci_lo_95": coef - 1.96 * se,
                            "ci_hi_95": coef + 1.96 * se,
                            "sign": "positive" if coef > 0 else ("negative" if coef < 0 else "zero"),
                            "sig_005": bool(p < 0.05),
                            "sig_010": bool(p < 0.10),
                            "sign_sig_005": f"{'positive' if coef > 0 else 'negative' if coef < 0 else 'zero'}_{'sig' if p < 0.05 else 'ns'}",
                            "sign_sig_010": f"{'positive' if coef > 0 else 'negative' if coef < 0 else 'zero'}_{'sig' if p < 0.10 else 'ns'}",
                            "N_sample_B067": int(meta["N_sample"]),
                            "N_grids_B067": int(meta["N_grids_sample"]),
                            "N_region_rows_before_dropna": int(len(reg)),
                            "N_region_grids_before_dropna": int(reg["grid_id"].nunique()),
                            "N_model": int(res["N_model"]),
                            "N_grids_model": int(res["N_grids_model"]),
                            "r2_within": float(res["r2_within"]),
                        }
                    )
    return pd.DataFrame(rows), pd.DataFrame(skipped)


def plot_role(coef: pd.DataFrame, role: str, path: Path) -> None:
    sub = coef.loc[coef["role"].eq(role)].copy()
    if sub.empty:
        raise RuntimeError(f"no rows for {role}")

    fig, axes = plt.subplots(
        nrows=len(HAZARDS),
        ncols=len(REGIONS),
        figsize=(13.5, 8.2),
        sharex=False,
        sharey=False,
        constrained_layout=True,
    )
    role_title = {
        "c1": "Hazard main effect by region and time window",
        "c3": "SR x hazard buffering slope by region and time window",
    }[role]
    y_label = {"c1": "c1 coefficient", "c3": "c3 coefficient"}[role]
    for i, hazard in enumerate(HAZARDS):
        for j, region in enumerate(REGIONS):
            ax = axes[i, j]
            cell = sub.loc[sub["hazard"].eq(hazard) & sub["region"].eq(region)].copy()
            cell["window"] = pd.Categorical(cell["window"], categories=WINDOWS, ordered=True)
            cell.sort_values("window", inplace=True)
            x = np.arange(len(cell))
            y = cell["coef"].to_numpy(dtype=float)
            lo = cell["ci_lo_95"].to_numpy(dtype=float)
            hi = cell["ci_hi_95"].to_numpy(dtype=float)
            sig = cell["sig_005"].to_numpy(dtype=bool)
            ax.axhline(0, color="#666666", linewidth=0.8, linestyle="--", zorder=1)
            ax.plot(x, y, color="#2F5597", linewidth=1.2, zorder=2)
            ax.vlines(x, lo, hi, color="#2F5597", linewidth=1.0, alpha=0.8, zorder=2)
            ax.scatter(
                x[sig],
                y[sig],
                s=28,
                color="#2F5597",
                edgecolor="#2F5597",
                linewidth=0.8,
                zorder=3,
                label="p<0.05" if i == 0 and j == 0 else None,
            )
            ax.scatter(
                x[~sig],
                y[~sig],
                s=28,
                facecolor="white",
                edgecolor="#2F5597",
                linewidth=0.9,
                zorder=3,
                label="p>=0.05" if i == 0 and j == 0 else None,
            )
            ax.set_xticks(x)
            ax.set_xticklabels([WINDOW_LABELS[w] for w in cell["window"].astype(str)], rotation=35, ha="right", fontsize=7)
            ax.tick_params(axis="y", labelsize=7)
            ax.grid(axis="y", color="#DDDDDD", linewidth=0.6)
            ax.grid(axis="x", visible=False)
            if i == 0:
                ax.set_title(REGION_LABELS[region], fontsize=10, fontweight="bold")
            if j == 0:
                ax.set_ylabel(f"{HAZARD_LABELS[hazard]}\n{y_label}", fontsize=9)
            else:
                ax.set_ylabel("")
            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)
            ax.spines["left"].set_color("#BBBBBB")
            ax.spines["bottom"].set_color("#BBBBBB")

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False, fontsize=9)
    fig.suptitle(role_title, fontsize=13, fontweight="bold")
    fig.text(0.5, 0.035, "Time window", ha="center", fontsize=10)
    fig.savefig(path, dpi=300, facecolor="white")
    plt.close(fig)


def write_report(coef: pd.DataFrame, skipped: pd.DataFrame, meta: dict[str, object]) -> None:
    support = (
        coef.groupby(["region", "region_label"], as_index=False)
        .agg(
            N_region_rows=("N_region_rows_before_dropna", "max"),
            N_region_grids=("N_region_grids_before_dropna", "max"),
            min_N_model=("N_model", "min"),
            max_N_model=("N_model", "max"),
        )
        .sort_values("region")
    )
    strongest = (
        coef.loc[coef["role"].eq("c3")]
        .assign(abs_coef=lambda x: x["coef"].abs())
        .sort_values(["hazard", "region", "abs_coef"], ascending=[True, True, False])
        .groupby(["hazard", "region"], as_index=False)
        .head(1)
        [["hazard", "region", "window", "coef", "p", "sig_005"]]
    )
    lines = [
        "# F4-B067 region-window diagnostics",
        "",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Sample scale: `{SAMPLE_ID}`; N={meta['N_sample']}; grids={meta['N_grids_sample']}.",
        "Regions: NE, HHH, NW, SW.",
        "Windows: full, v3pre30, v3pm10, hepm10, v3he, hema.",
        "",
        "Model: region-specific outcome FE regression with grid FE and year FE. Each hazard-window equation includes hazard, ca, ca x hazard, same-window companion hazards, same-window climate controls, irr_frac, and aridity.",
        "",
        "Outputs:",
        f"- Coefficients: `{OUT_DIR / 'f4_b067_region_window_coefficients.csv'}`",
        f"- Skipped: `{OUT_DIR / 'f4_b067_region_window_skipped.csv'}`",
        f"- c1 plot: `{FIG_DIR / 'fig9_region_window_c1_hazard_main.png'}`",
        f"- c3 plot: `{FIG_DIR / 'fig10_region_window_c3_sr_buffering.png'}`",
        "",
        "Region support:",
        "```csv",
        support.to_csv(index=False),
        "```",
        "",
        "Largest absolute c3 window within each hazard-region:",
        "```csv",
        strongest.to_csv(index=False),
        "```",
        "",
        f"Skipped rows: {len(skipped)}",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    df = add_window_interactions(load_panel())
    base, meta = b067_sample(df)
    coef, skipped = fit_region_window(base, meta)
    if skipped.empty:
        skipped = pd.DataFrame(
            columns=[
                "sample_id",
                "region",
                "hazard",
                "window",
                "reason",
                "N_rows_before_dropna",
                "N_grids_before_dropna",
            ]
        )
    coef.to_csv(OUT_DIR / "f4_b067_region_window_coefficients.csv", index=False, encoding="utf-8")
    skipped.to_csv(OUT_DIR / "f4_b067_region_window_skipped.csv", index=False, encoding="utf-8")
    plot_role(coef, "c1", FIG_DIR / "fig9_region_window_c1_hazard_main.png")
    plot_role(coef, "c3", FIG_DIR / "fig10_region_window_c3_sr_buffering.png")
    write_report(coef, skipped, meta)
    print(
        {
            "coef_rows": int(len(coef)),
            "skipped_rows": int(len(skipped)),
            "figure_c1": str(FIG_DIR / "fig9_region_window_c1_hazard_main.png"),
            "figure_c3": str(FIG_DIR / "fig10_region_window_c3_sr_buffering.png"),
            "report": str(REPORT_MD),
        },
        flush=True,
    )


if __name__ == "__main__":
    main()
