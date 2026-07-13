"""
descriptive_stats.py — 生成 v2 面板数据的描述性统计表
Purpose: 分类别输出描述性统计 (全样本 + 有产量子样本), 导出 LaTeX / CSV
Author: Data Build Pipeline
Date: 2026-03-29
Input: data/processed/data_v2_phenowindows.parquet
Output: output/tables/descriptive_stats_*.csv, output/tables/descriptive_stats_*.tex
"""

import sys, os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

np.random.seed(RANDOM_SEED)

# ── Paths ──────────────────────────────────────────────────────────────
TABLE_DIR_OUT = os.path.join(PROJ_DIR, "output", "tables")
os.makedirs(TABLE_DIR_OUT, exist_ok=True)


# ── Variable Groups ────────────────────────────────────────────────────
# Define display names (Chinese + English) and variable grouping

VAR_GROUPS = {
    "1_outcome_sr": {
        "label": "产量与秸秆还田 (Yield & SR)",
        "vars": {
            "yield_tons_ha":  "产量 (t/ha)",
            "ln_yield":       "ln(产量)",
            "ca":             "秸秆还田率 CA",
            "crc_ca_ratio":   "残茬覆盖率 CRC/CA",
            "crc_lag1":       "滞后一期CRC",
            "irr_frac":       "灌溉比例",
            "maize_area_km2": "玉米面积 (km²)",
        },
    },
    "2_phenology": {
        "label": "物候 (Phenology)",
        "vars": {
            "v3_doy":         "三叶期 DOY",
            "he_doy":         "抽穗期 DOY",
            "ma_doy":         "成熟期 DOY",
            "ca_ratio":       "CA ratio (原始)",
            "maize_frac":     "玉米种植比例",
            "win_full_days":  "全生育期天数",
            "win_v3pre30_days":"V3前30天窗口天数",
            "win_v3pm10_days":"V3±10窗口天数",
            "win_hepm10_days":"HE±10窗口天数",
            "win_v3he_days":  "V3→HE天数",
            "win_hema_days":  "HE→MA天数",
        },
    },
    "3_temp_full": {
        "label": "温度 — 全生育期 (Temperature, Full Season)",
        "vars": {
            "t2m_mean":       "日均温均值 (°C)",
            "t2m_max":        "日均温最高 (°C)",
            "t2m_min":        "日均温最低 (°C)",
            "tmax_mean":      "日最高温均值 (°C)",
            "tmax_max":       "日最高温极值 (°C)",
            "tmin_mean":      "日最低温均值 (°C)",
            "tmin_min":       "日最低温极值 (°C)",
            "dtr_mean":       "日较差均值 (°C)",
        },
    },
    "4_heat_full": {
        "label": "高温指标 — 全生育期 (Heat Indicators, Full Season)",
        "vars": {
            "hotdays_ge29":   "高温天数 ≥29°C",
            "hotdays_ge32":   "高温天数 ≥32°C",
            "hotdays_ge35":   "高温天数 ≥35°C",
            "hotdays_ge38":   "高温天数 ≥38°C",
            "hdd_ge29":       "热度日 HDD≥29",
            "hdd_ge32":       "热度日 HDD≥32",
            "hdd_ge35":       "热度日 HDD≥35",
            "hotdays_ge_p90": "高温天数 ≥P90",
            "hotdays_ge_p95": "高温天数 ≥P95",
            "nightheat_ge20": "夜间高温天 ≥20°C",
            "nightheat_ge24": "夜间高温天 ≥24°C",
            "gdd_ge10":       "生长度日 GDD≥10",
        },
    },
    "5_precip_full": {
        "label": "降水 — 全生育期 (Precipitation, Full Season)",
        "vars": {
            "pr_sum":          "累积降水 (mm)",
            "pr_mean":         "日均降水 (mm/d)",
            "pr_max":          "最大日降水 (mm)",
            "pr_sd":           "日降水标准差",
            "drydays_lt1":     "干旱天 (<1mm)",
            "wetdays_ge10":    "强降水天 (≥10mm)",
            "wetdays_ge20":    "暴雨天 (≥20mm)",
            "max_cdd":         "最长连续干旱天",
            "max_cwd":         "最长连续湿润天",
            "pr_intensity":    "降水强度 (mm/wet day)",
        },
    },
    "6_sm_full": {
        "label": "土壤水分 — 全生育期 (Soil Moisture, Full Season)",
        "vars": {
            "gleam_smrz_mean":          "GLEAM 根区SM均值",
            "gleam_smrz_min":           "GLEAM 根区SM最低",
            "gleam_sms_mean":           "GLEAM 表层SM均值",
            "drydays_gleam_smrz_le_p10":"GLEAM SMrz干旱天 ≤P10",
            "drydays_gleam_smrz_le_p20":"GLEAM SMrz干旱天 ≤P20",
            "swsm_l1_mean":            "SWSM 表层(L1)均值",
            "swsm_l3_mean":            "SWSM 深层(L3)均值",
            "drydays_swsm_l3_le_p10":  "SWSM L3干旱天 ≤P10",
            "drydays_swsm_l3_le_p20":  "SWSM L3干旱天 ≤P20",
        },
    },
    "7_et0_vpd_spei": {
        "label": "蒸散/VPD/SPEI — 全生育期 (ET0/VPD/SPEI, Full Season)",
        "vars": {
            "et0_sum":         "ET0累积 (mm)",
            "et0_mean":        "ET0日均 (mm/d)",
            "wd_deficit":      "水分亏缺 ET0-P (mm)",
            "vpd_mean":        "VPD均值 (hPa)",
            "vpd_max":         "VPD月最大 (hPa)",
            "spei6_mean":      "SPEI-6均值",
            "spei6_max":       "SPEI-6最大",
        },
    },
    "8_compound_full": {
        "label": "复合胁迫 — 全生育期 (Compound Stress, Full Season)",
        "vars": {
            "hotdrydays_ge32_smrz_p10": "热干天 ≥32°C & SMrz≤P10",
            "hotdrydays_ge32_smrz_p20": "热干天 ≥32°C & SMrz≤P20",
            "hotdrydays_ge35_smrz_p10": "热干天 ≥35°C & SMrz≤P10",
            "hotdrydays_ge35_smrz_p20": "热干天 ≥35°C & SMrz≤P20",
        },
    },
    "9_soil_static": {
        "label": "土壤/地理 — 时不变 (Soil & Geography, Static)",
        "vars": {
            "bdod_0_5cm_01deg":  "容重 0-5cm",
            "clay_0_5cm_01deg":  "粘粒含量 0-5cm (%)",
            "sand_0_5cm_01deg":  "砂粒含量 0-5cm (%)",
            "silt_0_5cm_01deg":  "粉粒含量 0-5cm (%)",
            "phh2o_0_5cm_01deg": "pH (H₂O) 0-5cm",
            "aridity":           "干旱指数",
            "pixel_area_km2":    "像元面积 (km²)",
        },
    },
}

# Period-specific representative variables (one per climate category)
PERIOD_VARS = {
    "10_temp_period": {
        "label": "温度 — 分时期 (Temperature by Period)",
        "vars": {
            "t2m_mean_v3pre30":  "日均温 V3pre30",
            "t2m_mean_v3pm10":   "日均温 V3±10",
            "t2m_mean_hepm10":   "日均温 HE±10",
            "t2m_mean_v3he":     "日均温 V3→HE",
            "t2m_mean_hema":     "日均温 HE→MA",
            "tmax_mean_v3pre30": "日最高温 V3pre30",
            "tmax_mean_v3pm10":  "日最高温 V3±10",
            "tmax_mean_hepm10":  "日最高温 HE±10",
            "tmax_mean_v3he":    "日最高温 V3→HE",
            "tmax_mean_hema":    "日最高温 HE→MA",
            "hotdays_ge32_v3pre30":"高温天≥32 V3pre30",
            "hotdays_ge32_v3pm10":"高温天≥32 V3±10",
            "hotdays_ge32_hepm10":"高温天≥32 HE±10",
            "hotdays_ge32_v3he": "高温天≥32 V3→HE",
            "hotdays_ge32_hema": "高温天≥32 HE→MA",
            "hdd_ge32_v3pre30":  "HDD≥32 V3pre30",
            "hdd_ge32_v3pm10":   "HDD≥32 V3±10",
            "hdd_ge32_hepm10":   "HDD≥32 HE±10",
            "hdd_ge32_v3he":     "HDD≥32 V3→HE",
            "hdd_ge32_hema":     "HDD≥32 HE→MA",
        },
    },
    "11_precip_period": {
        "label": "降水 — 分时期 (Precipitation by Period)",
        "vars": {
            "pr_sum_v3pre30":    "累积降水 V3pre30",
            "pr_sum_v3pm10":     "累积降水 V3±10",
            "pr_sum_hepm10":     "累积降水 HE±10",
            "pr_sum_v3he":       "累积降水 V3→HE",
            "pr_sum_hema":       "累积降水 HE→MA",
            "drydays_lt1_v3pre30":"干旱天 V3pre30",
            "drydays_lt1_v3pm10":"干旱天 V3±10",
            "drydays_lt1_hepm10":"干旱天 HE±10",
            "drydays_lt1_v3he":  "干旱天 V3→HE",
            "drydays_lt1_hema":  "干旱天 HE→MA",
            "max_cdd_v3pre30":   "最长连续干旱 V3pre30",
            "max_cdd_v3pm10":    "最长连续干旱 V3±10",
            "max_cdd_hepm10":    "最长连续干旱 HE±10",
            "max_cdd_v3he":      "最长连续干旱 V3→HE",
            "max_cdd_hema":      "最长连续干旱 HE→MA",
        },
    },
    "12_sm_period": {
        "label": "土壤水分 — 分时期 (SM by Period)",
        "vars": {
            "gleam_smrz_mean_v3pre30": "GLEAM SMrz V3pre30",
            "gleam_smrz_mean_v3pm10": "GLEAM SMrz V3±10",
            "gleam_smrz_mean_hepm10": "GLEAM SMrz HE±10",
            "gleam_smrz_mean_v3he":   "GLEAM SMrz V3→HE",
            "gleam_smrz_mean_hema":   "GLEAM SMrz HE→MA",
            "swsm_l3_mean_v3pre30":   "SWSM L3 V3pre30",
            "swsm_l3_mean_v3pm10":    "SWSM L3 V3±10",
            "swsm_l3_mean_hepm10":    "SWSM L3 HE±10",
            "swsm_l3_mean_v3he":      "SWSM L3 V3→HE",
            "swsm_l3_mean_hema":      "SWSM L3 HE→MA",
            "drydays_gleam_smrz_le_p10_v3pre30": "SMrz干旱天P10 V3pre30",
            "drydays_gleam_smrz_le_p10_v3pm10": "SMrz干旱天P10 V3±10",
            "drydays_gleam_smrz_le_p10_hepm10": "SMrz干旱天P10 HE±10",
            "drydays_gleam_smrz_le_p10_v3he":   "SMrz干旱天P10 V3→HE",
            "drydays_gleam_smrz_le_p10_hema":   "SMrz干旱天P10 HE→MA",
        },
    },
    "13_compound_period": {
        "label": "复合胁迫 — 分时期 (Compound by Period)",
        "vars": {
            "hotdrydays_ge32_smrz_p20_v3pre30": "热干天32P20 V3pre30",
            "hotdrydays_ge32_smrz_p20_v3pm10": "热干天32P20 V3±10",
            "hotdrydays_ge32_smrz_p20_hepm10": "热干天32P20 HE±10",
            "hotdrydays_ge32_smrz_p20_v3he":   "热干天32P20 V3→HE",
            "hotdrydays_ge32_smrz_p20_hema":   "热干天32P20 HE→MA",
            "hotdrydays_ge35_smrz_p20_v3pre30": "热干天35P20 V3pre30",
            "hotdrydays_ge35_smrz_p20_v3pm10": "热干天35P20 V3±10",
            "hotdrydays_ge35_smrz_p20_hepm10": "热干天35P20 HE±10",
            "hotdrydays_ge35_smrz_p20_v3he":   "热干天35P20 V3→HE",
            "hotdrydays_ge35_smrz_p20_hema":   "热干天35P20 HE→MA",
        },
    },
}


def compute_stats(df, var_dict):
    """Compute descriptive stats for a group of variables."""
    rows = []
    for var, label in var_dict.items():
        if var not in df.columns:
            continue
        s = df[var]
        rows.append({
            "Variable":   var,
            "Label":      label,
            "N":          int(s.notna().sum()),
            "Mean":       s.mean(),
            "SD":         s.std(),
            "Min":        s.min(),
            "P25":        s.quantile(0.25),
            "Median":     s.median(),
            "P75":        s.quantile(0.75),
            "Max":        s.max(),
            "Missing%":   s.isna().mean() * 100,
        })
    return pd.DataFrame(rows)


def to_latex_panel(stats_df, panel_label, note=""):
    """Format one panel of a LaTeX table."""
    lines = []
    lines.append(f"\\multicolumn{{10}}{{l}}{{\\textit{{{panel_label}}}}} \\\\")
    lines.append("\\hline")
    for _, r in stats_df.iterrows():
        lines.append(
            f"  {r['Label']} & {r['N']:,.0f} & {r['Mean']:.3f} & {r['SD']:.3f} & "
            f"{r['Min']:.3f} & {r['P25']:.3f} & {r['Median']:.3f} & "
            f"{r['P75']:.3f} & {r['Max']:.3f} & {r['Missing%']:.1f} \\\\"
        )
    return "\n".join(lines)


def main():
    print("=" * 70)
    print("Descriptive Statistics for v2 Panel")
    print("=" * 70)

    # Load data
    df = pd.read_parquet(os.path.join(PROCESSED_DIR, "data_v2_phenowindows.parquet"))
    print(f"Full panel: {len(df)} rows, {len(df.columns)} cols")

    # Compute window days if not present
    if 'win_full_days' not in df.columns:
        df['win_full_days'] = df['win_full_end'] - df['win_full_start'] + 1
    if 'win_v3pre30_days' not in df.columns:
        df['win_v3pre30_days'] = df['win_v3pre30_end'] - df['win_v3pre30_start'] + 1
    if 'win_v3pm10_days' not in df.columns:
        df['win_v3pm10_days'] = df['win_v3pm10_end'] - df['win_v3pm10_start'] + 1
    if 'win_hepm10_days' not in df.columns:
        df['win_hepm10_days'] = df['win_hepm10_end'] - df['win_hepm10_start'] + 1
    if 'win_v3he_days' not in df.columns:
        df['win_v3he_days'] = df['win_v3he_end'] - df['win_v3he_start'] + 1
    if 'win_hema_days' not in df.columns:
        df['win_hema_days'] = df['win_hema_end'] - df['win_hema_start'] + 1

    # Yield subsample
    df_yield = df[df['yield_tons_ha'].notna()].copy()
    print(f"Yield subsample: {len(df_yield)} rows")

    # ── A. Full-season + static stats ──────────────────────────────────
    all_groups = {**VAR_GROUPS, **PERIOD_VARS}

    all_stats_full = []
    all_stats_yield = []
    latex_panels_full = []
    latex_panels_yield = []

    for gkey in sorted(all_groups.keys()):
        ginfo = all_groups[gkey]
        label = ginfo['label']
        var_dict = ginfo['vars']

        st_full = compute_stats(df, var_dict)
        st_yield = compute_stats(df_yield, var_dict)

        if len(st_full) == 0:
            continue

        st_full.insert(0, 'Group', label)
        st_yield.insert(0, 'Group', label)
        all_stats_full.append(st_full)
        all_stats_yield.append(st_yield)

        latex_panels_full.append(to_latex_panel(st_full, label))
        latex_panels_yield.append(to_latex_panel(st_yield, label))

        print(f"\n  [{gkey}] {label}: {len(st_full)} vars")
        print(st_full[['Variable', 'N', 'Mean', 'SD', 'Min', 'Max']].to_string(index=False))

    # ── Combine and save ───────────────────────────────────────────────
    combined_full = pd.concat(all_stats_full, ignore_index=True)
    combined_yield = pd.concat(all_stats_yield, ignore_index=True)

    # CSV
    csv_full = os.path.join(TABLE_DIR_OUT, "desc_stats_full_panel.csv")
    csv_yield = os.path.join(TABLE_DIR_OUT, "desc_stats_yield_subsample.csv")
    combined_full.to_csv(csv_full, index=False, encoding='utf-8-sig')
    combined_yield.to_csv(csv_yield, index=False, encoding='utf-8-sig')
    print(f"\nSaved CSV: {csv_full}")
    print(f"Saved CSV: {csv_yield}")

    # LaTeX
    header = r"""\begin{table}[htbp]
\centering
\caption{Descriptive Statistics -- v2 Panel (%SAMPLE%)}
\label{tab:desc_stats_%TAG%}
\small
\begin{tabular}{lrrrrrrrrr}
\hline\hline
Variable & N & Mean & SD & Min & P25 & Median & P75 & Max & Miss\% \\
\hline
"""
    footer = r"""\hline\hline
\end{tabular}
\begin{tablenotes}
\small
\item 注: 全面板 N=122,533 (36,340 grids × 4 years); 有产量子样本 N=69,038.
\item 温度单位°C, 降水单位mm, 土壤水分为体积含水率 (m³/m³).
\item V3±10 = 三叶期前后10天; HE±10 = 抽穗期前后10天; V3→HE = 营养生长; HE→MA = 灌浆期.
\end{tablenotes}
\end{table}
"""

    tex_full_path = os.path.join(TABLE_DIR_OUT, "desc_stats_full_panel.tex")
    tex_yield_path = os.path.join(TABLE_DIR_OUT, "desc_stats_yield_subsample.tex")

    with open(tex_full_path, 'w', encoding='utf-8') as f:
        f.write(header.replace('%SAMPLE%', 'Full Panel, N=122,533').replace('%TAG%', 'full'))
        f.write("\n".join(latex_panels_full))
        f.write("\n")
        f.write(footer)

    with open(tex_yield_path, 'w', encoding='utf-8') as f:
        f.write(header.replace('%SAMPLE%', 'Yield Subsample, N=69,038').replace('%TAG%', 'yield'))
        f.write("\n".join(latex_panels_yield))
        f.write("\n")
        f.write(footer)

    print(f"Saved LaTeX: {tex_full_path}")
    print(f"Saved LaTeX: {tex_yield_path}")

    # ── B. Year-by-year summary ────────────────────────────────────────
    print("\n\n" + "=" * 70)
    print("Year-by-Year Summary")
    print("=" * 70)
    key_vars_yearly = ['yield_tons_ha', 'ca', 't2m_mean', 'tmax_mean', 'pr_sum',
                       'gleam_smrz_mean', 'hotdays_ge32', 'hdd_ge32',
                       'drydays_lt1', 'hotdrydays_ge32_smrz_p20', 'et0_sum', 'vpd_mean']
    existing = [v for v in key_vars_yearly if v in df.columns]
    yearly = df.groupby('year')[existing].agg(['mean', 'std', 'count']).round(4)
    yearly_path = os.path.join(TABLE_DIR_OUT, "desc_stats_by_year.csv")
    yearly.to_csv(yearly_path, encoding='utf-8-sig')
    print(f"Saved: {yearly_path}")

    # Print compact year summary
    for var in existing:
        yr_means = df.groupby('year')[var].mean()
        print(f"  {var:30s}  " + "  ".join(f"{y}: {v:.3f}" for y, v in yr_means.items()))

    # ── C. Window comparison ───────────────────────────────────────────
    print("\n\n" + "=" * 70)
    print("Window Comparison (mean values)")
    print("=" * 70)
    compare_vars = {
        't2m_mean': ['t2m_mean', 't2m_mean_v3pre30', 't2m_mean_v3pm10', 't2m_mean_hepm10', 't2m_mean_v3he', 't2m_mean_hema'],
        'pr_sum':   ['pr_sum', 'pr_sum_v3pre30', 'pr_sum_v3pm10', 'pr_sum_hepm10', 'pr_sum_v3he', 'pr_sum_hema'],
        'gleam_smrz_mean': ['gleam_smrz_mean', 'gleam_smrz_mean_v3pre30', 'gleam_smrz_mean_v3pm10', 'gleam_smrz_mean_hepm10',
                            'gleam_smrz_mean_v3he', 'gleam_smrz_mean_hema'],
        'hotdays_ge32': ['hotdays_ge32', 'hotdays_ge32_v3pre30', 'hotdays_ge32_v3pm10', 'hotdays_ge32_hepm10',
                         'hotdays_ge32_v3he', 'hotdays_ge32_hema'],
        'hdd_ge32': ['hdd_ge32', 'hdd_ge32_v3pre30', 'hdd_ge32_v3pm10', 'hdd_ge32_hepm10',
                     'hdd_ge32_v3he', 'hdd_ge32_hema'],
    }
    window_rows = []
    for base, cols in compare_vars.items():
        existing_cols = [c for c in cols if c in df.columns]
        if not existing_cols:
            continue
        means = df[existing_cols].mean()
        row = {'Variable': base}
        for c in existing_cols:
            if c == base:
                row['Full'] = means[c]
            elif c.endswith('_v3pre30'):
                row['V3pre30'] = means[c]
            elif c.endswith('_v3pm10'):
                row['V3±10'] = means[c]
            elif c.endswith('_hepm10'):
                row['HE±10'] = means[c]
            elif c.endswith('_v3he'):
                row['V3→HE'] = means[c]
            elif c.endswith('_hema'):
                row['HE→MA'] = means[c]
        window_rows.append(row)
    window_df = pd.DataFrame(window_rows)
    window_path = os.path.join(TABLE_DIR_OUT, "desc_stats_window_comparison.csv")
    window_df.to_csv(window_path, index=False, encoding='utf-8-sig')
    print(window_df.to_string(index=False))
    print(f"\nSaved: {window_path}")

    print("\n" + "=" * 70)
    print("Done! All descriptive statistics saved.")
    print("=" * 70)


if __name__ == "__main__":
    main()
