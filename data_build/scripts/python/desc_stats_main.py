"""
desc_stats_main.py — Descriptive statistics for main sample (with yield)
Date: 2026-03-29
Input: data/processed/data_v2_main.parquet
Output: output/tables/desc_stats_main_sample.csv, .tex
"""
import sys, os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

TABLE_OUT = os.path.join(PROJ_DIR, "output", "tables")
os.makedirs(TABLE_OUT, exist_ok=True)

df = pd.read_parquet(os.path.join(PROCESSED_DIR, "data_v2_main.parquet"))
N = len(df)

# Add window days
for w in ['full', 'v3pre30', 'v3pm10', 'hepm10', 'v3he', 'hema']:
    col = f'win_{w}_days'
    if col not in df.columns:
        df[col] = df[f'win_{w}_end'] - df[f'win_{w}_start'] + 1

print("=" * 80)
print(f"  Descriptive Statistics -- Main Sample (N = {N:,})")
print("=" * 80)

# ── Variable groups ──
groups = [
    ("1. Yield & SR", [
        ("yield_tons_ha",  "Yield (t/ha)"),
        ("ln_yield",       "ln(Yield)"),
        ("ca",             "CA adoption"),
        ("crc_ca_ratio",   "CRC/CA ratio"),
        ("crc_lag1",       "CRC lag1"),
        ("irr_frac",       "Irrigation frac"),
        ("maize_area_km2", "Maize area km2"),
    ]),
    ("2. Phenology", [
        ("v3_doy",        "V3 DOY"),
        ("he_doy",        "HE DOY"),
        ("ma_doy",        "MA DOY"),
        ("maize_frac",    "Maize frac"),
        ("win_full_days",    "Full-season days"),
        ("win_v3pre30_days", "V3pre30 days"),
        ("win_v3he_days",    "V3-HE days"),
        ("win_hema_days",    "HE-MA days"),
    ]),
    ("3. Temperature -- Full", [
        ("t2m_mean",  "T mean"),
        ("tmax_mean", "Tmax mean"),
        ("tmax_max",  "Tmax max"),
        ("tmin_mean", "Tmin mean"),
        ("tmin_min",  "Tmin min"),
        ("dtr_mean",  "DTR mean"),
    ]),
    ("4. Heat -- Full", [
        ("hotdays_ge29",     "HotD >=29"),
        ("hotdays_ge32",     "HotD >=32"),
        ("hotdays_ge35",     "HotD >=35"),
        ("hotdays_ge38",     "HotD >=38"),
        ("hdd_ge29",         "HDD >=29"),
        ("hdd_ge32",         "HDD >=32"),
        ("hdd_ge35",         "HDD >=35"),
        ("hotdays_ge_basep90","HotD >=P90"),
        ("hotdays_ge_basep95","HotD >=P95"),
        ("nightheat_ge20",   "NightH >=20"),
        ("nightheat_ge24",   "NightH >=24"),
        ("gdd_ge10",         "GDD >=10"),
    ]),
    ("5. Precipitation -- Full", [
        ("pr_sum",       "Precip total mm"),
        ("pr_mean",      "Precip mm/d"),
        ("pr_max",       "Precip max mm"),
        ("drydays_lt1",  "Dry days <1mm"),
        ("wetdays_ge10", "Wet days >=10mm"),
        ("wetdays_ge20", "Wet days >=20mm"),
        ("max_cdd",      "Max CDD"),
        ("max_cwd",      "Max CWD"),
        ("pr_intensity", "Precip intensity"),
    ]),
    ("6. Soil Moisture -- Full", [
        ("gleam_smrz_mean",           "GLEAM SMrz mean"),
        ("gleam_smrz_min",            "GLEAM SMrz min"),
        ("gleam_sms_mean",            "GLEAM SMs mean"),
        ("drydays_gleam_smrz_le_p10", "GLEAM SMrz dryP10"),
        ("drydays_gleam_smrz_le_p20", "GLEAM SMrz dryP20"),
        ("swsm_l1_mean",             "SWSM L1 mean"),
        ("swsm_l3_mean",             "SWSM L3 mean"),
        ("drydays_swsm_l3_le_p10",   "SWSM L3 dryP10"),
        ("drydays_swsm_l3_le_p20",   "SWSM L3 dryP20"),
        ("era5l_swvl1_mean",         "ERA5L swvl1 mean"),
        ("era5l_swvl3_mean",         "ERA5L swvl3 mean"),
        ("drydays_era5l_swvl3_le_p10","ERA5L swvl3 dryP10"),
        ("drydays_era5l_swvl3_le_p20","ERA5L swvl3 dryP20"),
        ("era5l_swvl1_coverage",     "ERA5L swvl1 coverage"),
        ("era5l_swvl3_coverage",     "ERA5L swvl3 coverage"),
    ]),
    ("7. ET0/VPD/SPEI -- Full", [
        ("et0_sum",    "ET0 total mm"),
        ("et0_mean",   "ET0 mm/d"),
        ("wd_deficit", "Water deficit mm"),
        ("vpd_mean",   "VPD mean hPa"),
        ("vpd_max",    "VPD max hPa"),
        ("spei6_mean", "SPEI-6 mean"),
    ]),
    ("8. Compound -- Full", [
        ("hotdrydays_ge32_smrz_p10", "HotDry32 P10"),
        ("hotdrydays_ge32_smrz_p20", "HotDry32 P20"),
        ("hotdrydays_ge35_smrz_p10", "HotDry35 P10"),
        ("hotdrydays_ge35_smrz_p20", "HotDry35 P20"),
    ]),
    ("9. Soil (static)", [
        ("bdod_0_5cm_01deg",  "Bulk density"),
        ("clay_0_5cm_01deg",  "Clay %"),
        ("sand_0_5cm_01deg",  "Sand %"),
        ("silt_0_5cm_01deg",  "Silt %"),
        ("phh2o_0_5cm_01deg", "pH"),
        ("aridity",           "Aridity idx"),
    ]),
    ("10. Temp -- Period", [
        ("t2m_mean_v3pre30",   "T V3pre30"),
        ("t2m_mean_v3pm10",    "T V3pm10"),
        ("t2m_mean_hepm10",    "T HEpm10"),
        ("t2m_mean_v3he",      "T V3-HE"),
        ("t2m_mean_hema",      "T HE-MA"),
        ("tmax_mean_v3pre30",  "Tmax V3pre30"),
        ("tmax_mean_v3pm10",   "Tmax V3pm10"),
        ("tmax_mean_hepm10",   "Tmax HEpm10"),
        ("tmax_mean_v3he",     "Tmax V3-HE"),
        ("tmax_mean_hema",     "Tmax HE-MA"),
        ("hotdays_ge32_v3pre30","HD32 V3pre30"),
        ("hotdays_ge32_v3pm10","HD32 V3pm10"),
        ("hotdays_ge32_hepm10","HD32 HEpm10"),
        ("hotdays_ge32_v3he",  "HD32 V3-HE"),
        ("hotdays_ge32_hema",  "HD32 HE-MA"),
        ("hdd_ge32_v3pre30",   "HDD32 V3pre30"),
        ("hdd_ge32_v3pm10",    "HDD32 V3pm10"),
        ("hdd_ge32_hepm10",    "HDD32 HEpm10"),
        ("hdd_ge32_v3he",      "HDD32 V3-HE"),
        ("hdd_ge32_hema",      "HDD32 HE-MA"),
    ]),
    ("11. Precip -- Period", [
        ("pr_sum_v3pre30",     "P V3pre30"),
        ("pr_sum_v3pm10",      "P V3pm10"),
        ("pr_sum_hepm10",      "P HEpm10"),
        ("pr_sum_v3he",        "P V3-HE"),
        ("pr_sum_hema",        "P HE-MA"),
        ("drydays_lt1_v3pre30","DryD V3pre30"),
        ("drydays_lt1_v3pm10", "DryD V3pm10"),
        ("drydays_lt1_hepm10", "DryD HEpm10"),
        ("drydays_lt1_v3he",   "DryD V3-HE"),
        ("drydays_lt1_hema",   "DryD HE-MA"),
        ("max_cdd_v3pre30",    "CDD V3pre30"),
        ("max_cdd_v3pm10",     "CDD V3pm10"),
        ("max_cdd_hepm10",     "CDD HEpm10"),
        ("max_cdd_v3he",       "CDD V3-HE"),
        ("max_cdd_hema",       "CDD HE-MA"),
    ]),
    ("12. SM -- Period", [
        ("gleam_smrz_mean_v3pre30",          "SMrz V3pre30"),
        ("gleam_smrz_mean_v3pm10",           "SMrz V3pm10"),
        ("gleam_smrz_mean_hepm10",           "SMrz HEpm10"),
        ("gleam_smrz_mean_v3he",             "SMrz V3-HE"),
        ("gleam_smrz_mean_hema",             "SMrz HE-MA"),
        ("swsm_l3_mean_v3pre30",             "L3 V3pre30"),
        ("swsm_l3_mean_v3pm10",              "L3 V3pm10"),
        ("swsm_l3_mean_hepm10",              "L3 HEpm10"),
        ("swsm_l3_mean_v3he",               "L3 V3-HE"),
        ("swsm_l3_mean_hema",               "L3 HE-MA"),
        ("drydays_gleam_smrz_le_p10_v3pre30","SMrzDryP10 V3pre30"),
        ("drydays_gleam_smrz_le_p10_v3pm10", "SMrzDryP10 V3pm10"),
        ("drydays_gleam_smrz_le_p10_hepm10", "SMrzDryP10 HEpm10"),
        ("drydays_gleam_smrz_le_p10_v3he",   "SMrzDryP10 V3-HE"),
        ("drydays_gleam_smrz_le_p10_hema",   "SMrzDryP10 HE-MA"),
        ("era5l_swvl3_mean_v3pre30",         "E5L swvl3 V3pre30"),
        ("era5l_swvl3_mean_v3pm10",          "E5L swvl3 V3pm10"),
        ("era5l_swvl3_mean_hepm10",          "E5L swvl3 HEpm10"),
        ("era5l_swvl3_mean_v3he",            "E5L swvl3 V3-HE"),
        ("era5l_swvl3_mean_hema",            "E5L swvl3 HE-MA"),
        ("era5l_swvl3_coverage_v3pre30",     "E5L cov V3pre30"),
        ("era5l_swvl3_coverage_v3pm10",      "E5L cov V3pm10"),
        ("era5l_swvl3_coverage_hepm10",      "E5L cov HEpm10"),
        ("era5l_swvl3_coverage_v3he",        "E5L cov V3-HE"),
        ("era5l_swvl3_coverage_hema",        "E5L cov HE-MA"),
    ]),
    ("13. Compound -- Period", [
        ("hotdrydays_ge32_smrz_p20_v3pre30","HD32P20 V3pre30"),
        ("hotdrydays_ge32_smrz_p20_v3pm10", "HD32P20 V3pm10"),
        ("hotdrydays_ge32_smrz_p20_hepm10", "HD32P20 HEpm10"),
        ("hotdrydays_ge32_smrz_p20_v3he",   "HD32P20 V3-HE"),
        ("hotdrydays_ge32_smrz_p20_hema",   "HD32P20 HE-MA"),
        ("hotdrydays_ge35_smrz_p20_v3pre30","HD35P20 V3pre30"),
        ("hotdrydays_ge35_smrz_p20_v3pm10", "HD35P20 V3pm10"),
        ("hotdrydays_ge35_smrz_p20_hepm10", "HD35P20 HEpm10"),
        ("hotdrydays_ge35_smrz_p20_v3he",   "HD35P20 V3-HE"),
        ("hotdrydays_ge35_smrz_p20_hema",   "HD35P20 HE-MA"),
    ]),
]

all_rows = []
for gname, var_list in groups:
    print(f"\n{gname}")
    hdr = f"  {'Variable':<25s} {'Label':<20s} {'N':>7s} {'Mean':>10s} {'SD':>10s} {'Min':>10s} {'P25':>10s} {'Med':>10s} {'P75':>10s} {'Max':>10s} {'Miss%':>6s}"
    print(hdr)
    print("  " + "-" * len(hdr))
    for var, label in var_list:
        if var not in df.columns:
            continue
        s = df[var]
        n = int(s.notna().sum())
        miss = s.isna().mean() * 100
        row = dict(
            Group=gname, Variable=var, Label=label,
            N=n, Mean=s.mean(), SD=s.std(),
            Min=s.min(), P25=s.quantile(0.25), Median=s.median(),
            P75=s.quantile(0.75), Max=s.max(), MissPct=miss,
        )
        all_rows.append(row)
        print(f"  {var:<25s} {label:<20s} {n:>7,} {row['Mean']:>10.3f} {row['SD']:>10.3f} "
              f"{row['Min']:>10.3f} {row['P25']:>10.3f} {row['Median']:>10.3f} "
              f"{row['P75']:>10.3f} {row['Max']:>10.3f} {miss:>5.1f}%")

stats = pd.DataFrame(all_rows)
stats.to_csv(os.path.join(TABLE_OUT, "desc_stats_main_sample.csv"), index=False, encoding="utf-8-sig")
print(f"\nSaved CSV: desc_stats_main_sample.csv ({len(stats)} vars)")

# ── LaTeX ──
tex_path = os.path.join(TABLE_OUT, "desc_stats_main_sample.tex")
with open(tex_path, "w", encoding="utf-8") as f:
    f.write(r"""\begin{table}[htbp]
\centering
\caption{Descriptive Statistics -- Main Analysis Sample (N = 69,038)}
\label{tab:desc_main}
\footnotesize
\begin{tabular}{llrrrrrrrrr}
\hline\hline
 & Variable & N & Mean & SD & Min & P25 & Median & P75 & Max & Miss\% \\
\hline
""")
    cur_group = ""
    for _, r in stats.iterrows():
        if r["Group"] != cur_group:
            cur_group = r["Group"]
            f.write(f"\\multicolumn{{11}}{{l}}{{\\textit{{{cur_group}}}}} \\\\\n")
        f.write(f"  & {r['Label']} & {r['N']:,.0f} & {r['Mean']:.3f} & {r['SD']:.3f} & "
                f"{r['Min']:.3f} & {r['P25']:.3f} & {r['Median']:.3f} & "
                f"{r['P75']:.3f} & {r['Max']:.3f} & {r['MissPct']:.1f} \\\\\n")
    f.write(r"""\hline\hline
\end{tabular}
\begin{tablenotes}\small
\item Note: Main sample = grid-years with non-missing maize yield (69,038 of 122,533 total).
\item Temperature in $^\circ$C, precipitation in mm, soil moisture in m$^3$/m$^3$.
\item V3$\pm$10 = trifoliate $\pm$10 days; HE$\pm$10 = heading $\pm$10 days;
      V3-HE = vegetative; HE-MA = grain filling.
\end{tablenotes}
\end{table}
""")
print(f"Saved LaTeX: {tex_path}")

# ── Year-by-year ──
print("\n" + "=" * 80)
print("  Year-by-Year Summary")
print("=" * 80)
yvars = ["yield_tons_ha", "ca", "t2m_mean", "tmax_mean", "pr_sum",
         "gleam_smrz_mean", "era5l_swvl3_mean", "hotdays_ge32", "hdd_ge32", "drydays_lt1",
         "hotdrydays_ge32_smrz_p20", "et0_sum", "vpd_mean", "spei6_mean"]
print(f"  {'Variable':<32s}  {'2016':>10s}  {'2017':>10s}  {'2018':>10s}  {'2019':>10s}")
print("  " + "-" * 78)
for v in yvars:
    if v in df.columns:
        yr = df.groupby("year")[v].mean()
        vals = "  ".join(f"{yr.get(y, np.nan):>10.3f}" for y in [2016, 2017, 2018, 2019])
        print(f"  {v:<32s}  {vals}")

# Save year-by-year
yr_stats = df.groupby("year")[[v for v in yvars if v in df.columns]].agg(["mean", "std", "count"])
yr_stats.to_csv(os.path.join(TABLE_OUT, "desc_stats_main_by_year.csv"), encoding="utf-8-sig")

# ── Window comparison ──
print("\n" + "=" * 80)
print("  Window Comparison (Mean Values)")
print("=" * 80)
wvars = [
    ("t2m_mean",        "T mean (C)"),
    ("tmax_mean",       "Tmax (C)"),
    ("pr_sum",          "Precip (mm)"),
    ("gleam_smrz_mean", "GLEAM SMrz"),
    ("era5l_swvl3_mean","ERA5L swvl3"),
    ("hotdays_ge32",    "HotDays>=32"),
    ("hdd_ge32",        "HDD>=32"),
    ("drydays_lt1",     "DryDays"),
    ("et0_sum",         "ET0 (mm)"),
    ("vpd_mean",        "VPD (hPa)"),
    ("spei6_mean",      "SPEI-6"),
]
print(f"  {'Variable':<20s} {'Full':>10s} {'V3pre30':>10s} {'V3pm10':>10s} {'HEpm10':>10s} {'V3-HE':>10s} {'HE-MA':>10s}")
print("  " + "-" * 85)
wrows = []
for var, lbl in wvars:
    cols = {
        "Full": var,
        "V3pre30": f"{var}_v3pre30",
        "V3pm10": f"{var}_v3pm10",
        "HEpm10": f"{var}_hepm10",
        "V3-HE": f"{var}_v3he",
        "HE-MA": f"{var}_hema",
    }
    row = {"Variable": lbl}
    parts = []
    for wlabel, c in cols.items():
        if c in df.columns:
            m = df[c].mean()
            row[wlabel] = m
            parts.append(f"{m:>10.3f}")
        else:
            row[wlabel] = np.nan
            parts.append(f"{'--':>10s}")
    wrows.append(row)
    print(f"  {lbl:<20s} {' '.join(parts)}")

wdf = pd.DataFrame(wrows)
wdf.to_csv(os.path.join(TABLE_OUT, "desc_stats_main_window_comparison.csv"), index=False, encoding="utf-8-sig")

# ── Missing values ──
print("\n" + "=" * 80)
print("  Missing Values Summary (Main Sample)")
print("=" * 80)
mvars = [
    "yield_tons_ha", "ca", "crc_lag1", "t2m_mean", "tmax_mean",
    "hotdays_ge32", "hdd_ge32", "pr_sum", "pr_mean",
    "gleam_smrz_mean", "drydays_gleam_smrz_le_p10",
    "swsm_l1_mean", "swsm_l3_mean", "drydays_swsm_l3_le_p10",
    "era5l_swvl1_mean", "era5l_swvl3_mean", "era5l_swvl1_coverage",
    "et0_sum", "et0_mean", "wd_deficit",
    "vpd_mean", "spei6_mean",
    "hotdrydays_ge32_smrz_p20",
    "irr_frac", "bdod_0_5cm_01deg", "aridity",
    "t2m_mean_v3pm10", "t2m_mean_v3he",
    "gleam_smrz_mean_v3he", "pr_sum_v3he",
]
print(f"  {'Variable':<42s} {'Missing':>8s} {'Rate':>7s}")
print("  " + "-" * 60)
for v in mvars:
    if v in df.columns:
        n = df[v].isna().sum()
        r = n / N * 100
        print(f"  {v:<42s} {n:>8,} {r:>6.1f}%")

# Complete case
core = ["yield_tons_ha", "ca", "t2m_mean", "pr_sum", "gleam_smrz_mean", "hotdays_ge32", "hdd_ge32"]
n_core = df[core].dropna().shape[0]
print(f"\n  Complete-case (core):   {n_core:,} / {N:,} ({n_core/N*100:.1f}%)")
core_swsm = ["yield_tons_ha", "ca", "t2m_mean", "pr_sum", "swsm_l3_mean", "hotdays_ge32"]
n_swsm = df[core_swsm].dropna().shape[0]
print(f"  Complete-case (+SWSM):  {n_swsm:,} / {N:,} ({n_swsm/N*100:.1f}%)")
core_all = core + ["et0_sum", "vpd_mean", "spei6_mean", "bdod_0_5cm_01deg", "aridity"]
n_all = df[[c for c in core_all if c in df.columns]].dropna().shape[0]
print(f"  Complete-case (+full):  {n_all:,} / {N:,} ({n_all/N*100:.1f}%)")
core_era5l = ["yield_tons_ha", "ca", "t2m_mean", "pr_sum", "era5l_swvl3_mean", "hotdays_ge32"]
n_era5l = df[core_era5l].dropna().shape[0]
print(f"  Complete-case (+ERA5L): {n_era5l:,} / {N:,} ({n_era5l/N*100:.1f}%)")

print("\n" + "=" * 80)
print("  Done!")
print("=" * 80)
