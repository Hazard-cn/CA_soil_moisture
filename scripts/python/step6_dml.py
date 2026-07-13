"""
step6_dml.py — Double Machine Learning Robustness Check
Purpose: PLR-DML to verify FE regression results for SR buffering
Author: YangSu / Claude Code
Date: 2026-03-12
Dependencies: econml, sklearn, pandas, numpy
"""

import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

# ============================================================================
# Paths
# ============================================================================
PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
DATA = Path("C:/YangSu/00_Project/CA_mechanism/data/master/data_v1_with_climate.csv")
OUTDIR = PROJ / "output" / "tables"
LOGDIR = PROJ / "output" / "logs"
OUTDIR.mkdir(parents=True, exist_ok=True)
LOGDIR.mkdir(parents=True, exist_ok=True)

# Redirect stdout to log
log_path = LOGDIR / "step6_dml_20260312.log"
log_file = open(log_path, "w", encoding="utf-8")

def log(msg):
    print(msg)
    log_file.write(msg + "\n")
    log_file.flush()

log("=" * 60)
log("Step 6: DML Robustness Check")
log("=" * 60)

# ============================================================================
# 1. Load and prepare data (same filters as 00_preamble.do)
# ============================================================================
log("\n--- Loading data ---")
df = pd.read_csv(DATA, encoding="gbk")
log(f"Raw: {len(df)} rows, {len(df.columns)} cols")

# Sample filters
df = df[df["china_mask"] == 1]
df = df[df["yield_tons_ha"] > 0]
df = df[df["maize_area_km2"] > 0]
df = df.dropna(subset=["ln_yield", "ca", "SPEI_season"])
log(f"After filters: {len(df)} rows")

# Construct variables
df["D_season"] = np.maximum(0, -df["SPEI_season"])
df["W_season"] = np.maximum(0, df["SPEI_season"])
df["SR_x_D"] = df["ca"] * df["D_season"]
df["SR_x_Heat"] = df["ca"] * df["hdd_tmax_ge32"]

# ============================================================================
# 2. Within-demean (remove grid + year FE)
# ============================================================================
log("\n--- Within-demeaning (grid + year FE) ---")

outcome_var = "ln_yield"
treatment_vars = ["SR_x_D", "SR_x_Heat"]
control_vars = [
    "D_season", "W_season", "hdd_tmax_ge32", "ca",
    "irr_frac", "pre_sum", "et0_sum", "wd_aridity_et0divpre", "gdd_30",
    "gleam_smrz_mean",
]

all_vars = [outcome_var] + treatment_vars + control_vars
df_model = df[["grid_id", "year"] + all_vars].dropna().copy()
log(f"Complete cases: {len(df_model)} rows")

# Demean by grid
grid_means = df_model.groupby("grid_id")[all_vars].transform("mean")
df_dm = df_model[all_vars] - grid_means

# Demean by year (on residuals)
df_dm["year"] = df_model["year"].values
year_means = df_dm.groupby("year")[all_vars].transform("mean")
df_dm[all_vars] = df_dm[all_vars] - year_means

df_dm["grid_id"] = df_model["grid_id"].values
log(f"Demeaned: {len(df_dm)} rows, {len(all_vars)} vars")

# ============================================================================
# 3. PLR-DML: Interaction-as-Treatment
# ============================================================================
log("\n--- PLR-DML estimation ---")

try:
    from econml.dml import LinearDML
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    HAS_ECONML = True
    log("econml loaded successfully")
except ImportError:
    HAS_ECONML = False
    log("WARNING: econml not available, using manual cross-fitting")

results = []

for t_var in treatment_vars:
    log(f"\n--- Treatment: {t_var} ---")

    Y = df_dm[outcome_var].values
    T = df_dm[t_var].values
    X_cols = [c for c in control_vars if c != t_var.replace("SR_x_", "").lower()]
    X = df_dm[X_cols].values

    if HAS_ECONML:
        # econml LinearDML with cross-fitting
        est = LinearDML(
            model_y=RandomForestRegressor(
                n_estimators=500, max_depth=10, min_samples_leaf=20,
                random_state=42, n_jobs=-1
            ),
            model_t=RandomForestRegressor(
                n_estimators=500, max_depth=10, min_samples_leaf=20,
                random_state=43, n_jobs=-1
            ),
            cv=5,
            random_state=42,
        )
        est.fit(Y=Y, T=T.reshape(-1, 1), X=None, W=X)

        theta = est.const_marginal_effect()[0]
        ci = est.const_marginal_effect_interval(alpha=0.05)
        se = (ci[1][0] - ci[0][0]) / (2 * 1.96)
        p_approx = 2 * (1 - __import__("scipy").stats.norm.cdf(abs(theta / se)))

        log(f"  theta = {theta:.6f}")
        log(f"  SE    = {se:.6f}")
        log(f"  95%CI = [{ci[0][0]:.6f}, {ci[1][0]:.6f}]")
        log(f"  p     ~ {p_approx:.4f}")

        results.append({
            "treatment": t_var,
            "method": "DML-PLR",
            "theta": theta,
            "se": se,
            "ci_low": ci[0][0],
            "ci_high": ci[1][0],
            "p_value": p_approx,
            "n": len(Y),
        })
    else:
        # Manual cross-fitting fallback
        from sklearn.model_selection import KFold
        from sklearn.ensemble import RandomForestRegressor

        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        theta_folds = []

        for fold_idx, (train_idx, test_idx) in enumerate(kf.split(X)):
            # Fit nuisance models on train
            rf_y = RandomForestRegressor(n_estimators=300, max_depth=10,
                                         min_samples_leaf=20, random_state=42, n_jobs=-1)
            rf_t = RandomForestRegressor(n_estimators=300, max_depth=10,
                                         min_samples_leaf=20, random_state=43, n_jobs=-1)

            rf_y.fit(X[train_idx], Y[train_idx])
            rf_t.fit(X[train_idx], T[train_idx])

            # Residualize on test
            Y_res = Y[test_idx] - rf_y.predict(X[test_idx])
            T_res = T[test_idx] - rf_t.predict(X[test_idx])

            # OLS on residuals
            theta_k = np.sum(T_res * Y_res) / np.sum(T_res ** 2)
            theta_folds.append(theta_k)
            log(f"  Fold {fold_idx+1}: theta = {theta_k:.6f}")

        theta = np.mean(theta_folds)
        se = np.std(theta_folds, ddof=1) / np.sqrt(len(theta_folds))

        log(f"  Average theta = {theta:.6f}")
        log(f"  SE (across folds) = {se:.6f}")

        results.append({
            "treatment": t_var,
            "method": "Manual-PLR",
            "theta": theta,
            "se": se,
            "ci_low": theta - 1.96 * se,
            "ci_high": theta + 1.96 * se,
            "p_value": np.nan,
            "n": len(Y),
        })

# ============================================================================
# 4. Compare with FE results
# ============================================================================
log("\n--- Comparison: DML vs FE ---")

# FE results from Step 1 (hardcoded from CSV)
fe_results = {
    "SR_x_D": {"theta": 0.0422, "se": 0.0203},
    "SR_x_Heat": {"theta": 0.0011, "se": 0.0002},
}

comparison = []
for r in results:
    t = r["treatment"]
    fe = fe_results.get(t, {})
    row = {
        "Variable": t,
        "FE_theta": fe.get("theta", np.nan),
        "FE_se": fe.get("se", np.nan),
        "DML_theta": r["theta"],
        "DML_se": r["se"],
        "DML_ci_low": r["ci_low"],
        "DML_ci_high": r["ci_high"],
        "Same_sign": "Yes" if np.sign(r["theta"]) == np.sign(fe.get("theta", 0)) else "No",
        "N": r["n"],
    }
    comparison.append(row)
    log(f"  {t}: FE={fe.get('theta', 'N/A'):.4f} vs DML={r['theta']:.4f} | Same sign: {row['Same_sign']}")

# ============================================================================
# 5. Export
# ============================================================================
df_out = pd.DataFrame(comparison)
out_path = OUTDIR / "step6_dml_results.csv"
df_out.to_csv(out_path, index=False)
log(f"\nResults saved to: {out_path}")

# Also save detailed results
df_detail = pd.DataFrame(results)
df_detail.to_csv(OUTDIR / "step6_dml_detailed.csv", index=False)

log("\n" + "=" * 60)
log("Step 6 Complete")
log("=" * 60)

log_file.close()
print(f"Done. Log: {log_path}")
