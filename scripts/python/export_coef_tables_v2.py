"""Export coefficient tables matching v2 figures to output/figures/f4_b067_v2/."""
import csv, os

projdir = "C:/YangSu/00_Project/CA_mechanism/regression_SR"
infile = os.path.join(projdir, "temp/2026-06-04_f4_b067_full_bootstrap_counterfactual",
                      "f4_b067_mean_raw_unified_coefficients_effects.csv")
outdir = os.path.join(projdir, "output/figures/f4_b067_v2")

rows = []
with open(infile, "r") as f:
    for r in csv.DictReader(f):
        if r["sample_id"] == "B067" and r["branch"] == "mean" and r["transform"] == "raw":
            rows.append(r)

hazard_order = {"drought": 0, "heat": 1, "hotdry": 2}
effect_order = {"IE": 0, "DE": 1, "TE": 2}
ca_order = {"P25": 0, "P50": 1, "P75": 2}
role_order = {"a1": 0, "a3": 1, "b": 2, "c1": 3, "c3": 4}
path_labels = {"a1": "Hazard -> SM", "a3": "SR*Hazard -> SM", "b": "SM -> Yield",
               "c1": "Hazard -> Yield", "c3": "SR*Hazard -> Yield"}

def sort_key_coef(r):
    return hazard_order.get(r["hazard"], 9) * 10 + role_order.get(r["role"], 9)

def sort_key_iede(r):
    return (hazard_order.get(r["hazard"], 9) * 100
            + effect_order.get(r["effect"], 9) * 10
            + ca_order.get(r["ca_level"], 9))

def ci_excludes_zero(r):
    try:
        lo, hi = float(r["bs_ci_lo_95"]), float(r["bs_ci_hi_95"])
        return "1" if lo * hi > 0 else "0"
    except (ValueError, TypeError):
        return ""

def write_coef_table(data, fname, extra_cols=None):
    header = (extra_cols or []) + [
        "hazard", "effect", "ca_level", "ca_value",
        "estimate", "bs_se", "ci_lo_95", "ci_hi_95", "ci_excludes_zero",
        "N_boot", "N_model"
    ]
    path = os.path.join(outdir, fname)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in sorted(data, key=sort_key_iede):
            extra = [r.get(c, "") for c in (extra_cols or [])]
            w.writerow(extra + [
                r["hazard"], r["effect"], r["ca_level"], r.get("ca_value", ""),
                r["estimate"], r["bs_se"], r["bs_ci_lo_95"], r["bs_ci_hi_95"],
                ci_excludes_zero(r), r["N_boot"], r["N_model"]
            ])
    print(f"  {fname}: {len(data)} rows")

# === Table 1: Baseline 5 key mechanism coefficients (matches fig1) ===
t1 = [r for r in rows if r["record_type"] == "rhs_coefficient"
      and r["layer"] == "baseline" and r["role"] in role_order]
fname1 = "table1_baseline_mechanism.csv"
with open(os.path.join(outdir, fname1), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["hazard", "path", "role", "equation", "term",
                "estimate", "se", "p", "ci_lo_95", "ci_hi_95", "ci_source",
                "sig_005", "N_model"])
    for r in sorted(t1, key=sort_key_coef):
        ci_src = "bootstrap" if r["bs_ci_lo_95"] else "model"
        ci_lo = r["bs_ci_lo_95"] or r["model_ci_lo_95"]
        ci_hi = r["bs_ci_hi_95"] or r["model_ci_hi_95"]
        se = r["bs_se"] or r["model_se"]
        w.writerow([r["hazard"], path_labels[r["role"]], r["role"], r["equation"],
                    r["term"], r["estimate"], se, r["model_p"],
                    ci_lo, ci_hi, ci_src, r["sig_005"], r["N_model"]])
print(f"  {fname1}: {len(t1)} rows")

# === Table 2: Baseline IE/DE/TE (matches fig2) ===
t2 = [r for r in rows if r["record_type"] == "iede_effect" and r["layer"] == "baseline"]
write_coef_table(t2, "table2_baseline_iede.csv")

# === Tables 3-7: Zone IE/DE/TE (matches fig3-7) ===
for zone in ["NE", "HHH", "NW", "SW", "SH"]:
    tz = [r for r in rows if r["record_type"] == "iede_effect"
          and r["layer"] == "heterogeneity" and r["subgroup"] == zone]
    write_coef_table(tz, f"table_zone_{zone}_iede.csv", extra_cols=["subgroup"])

# === Tables 8-9: Irrigation IE/DE/TE (matches fig8-9) ===
for irr in ["high_irr", "low_irr"]:
    ti = [r for r in rows if r["record_type"] == "iede_effect"
          and r["layer"] == "heterogeneity" and r["subgroup"] == irr]
    write_coef_table(ti, f"table_irr_{irr}_iede.csv", extra_cols=["subgroup"])

# === Table 10: Irrigation combined (matches fig10) ===
t10 = [r for r in rows if r["record_type"] == "iede_effect"
       and r["layer"] == "heterogeneity" and r["subgroup"] in ("high_irr", "low_irr")]
write_coef_table(t10, "table10_irr_combined_iede.csv", extra_cols=["subgroup"])

# === Table 11: AI>2 irrigation combined (matches fig11) ===
t11 = [r for r in rows if r["record_type"] == "iede_effect"
       and r["layer"] == "ai_gt2_irrigation"]
write_coef_table(t11, "table11_ai2_irr_combined_iede.csv", extra_cols=["subgroup"])

# === Table counterfactual (matches fig8 in old numbering) ===
tc = [r for r in rows if r["record_type"] == "counterfactual"]
fname_cf = "table_counterfactual.csv"
with open(os.path.join(outdir, fname_cf), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["layer", "subgroup", "hazard", "scenario", "ca_level",
                "hazard_level", "delta_te", "delta_lnY",
                "delta_lnY_ci_lo", "delta_lnY_ci_hi",
                "pct_delta", "pct_ci_lo", "pct_ci_hi", "N_boot"])
    for r in sorted(tc, key=lambda x: x["layer"] + x["subgroup"] + x["hazard"] + x["scenario"]):
        w.writerow([r["layer"], r["subgroup"], r["hazard"], r["scenario"],
                    r["ca_level"], r.get("hazard_level", ""),
                    r.get("delta_te_point", ""), r.get("delta_ln_yield_point", ""),
                    r.get("delta_ln_yield_ci_lo", ""), r.get("delta_ln_yield_ci_hi", ""),
                    r.get("pct_delta_point", ""), r.get("pct_delta_ci_lo", ""),
                    r.get("pct_delta_ci_hi", ""), r["N_boot"]])
print(f"  {fname_cf}: {len(tc)} rows")

print(f"\nAll tables saved to: {outdir}")
