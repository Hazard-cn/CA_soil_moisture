* =============================================================================
* step3_mechanism.do — Attenuation Test + Bootstrap Indirect Effect + Sobel
* Purpose: (A) Attenuation table (5 cols, grid+year and prov×year)
*          (B) Sobel test (delta method)
*          (C) Cluster bootstrap indirect effect (500 reps)
* Author: YangSu / Claude Code
* Date: 2026-03-17
* Dependencies: 00_preamble.do, reghdfe, estout
* =============================================================================

* --- Preamble ---
global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/00_preamble.do"

local today : di %tdCYND date(c(current_date), "DMY")
log using "$logdir/step3_mechanism_`today'.log", replace

* --- Mechanism controls (drop et0_sum) ---
global CTRL_mech "irr_frac pre_sum wd_aridity_et0divpre gdd_30"

di "============================================================"
di "  PART A: Attenuation Table (Table 4)"
di "============================================================"

eststo clear

* Col 1: Baseline, grid+year FE, no SM
eststo att_base: reghdfe ln_yield ///
    D_season W_season hdd_tmax_ge32 ///
    ca SR_x_D SR_x_W SR_x_Heat $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

* Col 2: + DryDays (primary mediator)
eststo att_dry: reghdfe ln_yield ///
    D_season W_season hdd_tmax_ge32 ///
    ca SR_x_D SR_x_W SR_x_Heat ///
    drydays_gleam_smrz_le_basep10 $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

* Col 3: + SM_rz + DryDays (full SM battery)
eststo att_both: reghdfe ln_yield ///
    D_season W_season hdd_tmax_ge32 ///
    ca SR_x_D SR_x_W SR_x_Heat ///
    drydays_gleam_smrz_le_basep10 gleam_smrz_mean $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

* Col 4: Prov×year FE, no SM
eststo att_prov: reghdfe ln_yield ///
    D_season W_season hdd_tmax_ge32 ///
    ca SR_x_D SR_x_W SR_x_Heat $CTRL_mech, ///
    absorb(grid_id prov_year) vce(cluster grid_id)

* Col 5: Prov×year FE + DryDays
eststo att_prov_dry: reghdfe ln_yield ///
    D_season W_season hdd_tmax_ge32 ///
    ca SR_x_D SR_x_W SR_x_Heat ///
    drydays_gleam_smrz_le_basep10 $CTRL_mech, ///
    absorb(grid_id prov_year) vce(cluster grid_id)

* Export Table 4
esttab att_base att_dry att_both att_prov att_prov_dry ///
    using "$outdir/step3_attenuation.csv", ///
    replace b(%9.4f) se(%9.4f) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(SR_x_D SR_x_W SR_x_Heat ca ///
         drydays_gleam_smrz_le_basep10 gleam_smrz_mean ///
         D_season W_season hdd_tmax_ge32) ///
    stats(r2 N, labels("R-squared" "N") fmt(%9.4f %9.0f)) ///
    mtitles("Base(G+Y)" "+DryDays" "+SM+Dry" "Base(P×Y)" "+DryDays(P×Y)") ///
    title("Table 4: Yield Attenuation Test")

esttab att_base att_dry att_both att_prov att_prov_dry ///
    using "$outdir/step3_attenuation.tex", ///
    replace b(%9.4f) se(%9.4f) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(SR_x_D SR_x_W SR_x_Heat ///
         drydays_gleam_smrz_le_basep10 gleam_smrz_mean) ///
    stats(r2 N, labels("R-squared" "N") fmt(%9.4f %9.0f)) ///
    mtitles("Base" "+DryDays" "+SM+Dry" "Prov×Yr" "+Dry(P×Y)") ///
    title("Yield Attenuation Test") booktabs

* --- Attenuation diagnostics ---
di ""
di "--- Attenuation Diagnostics ---"

estimates restore att_base
local theta_base = _b[SR_x_D]
local theta_base_se = _se[SR_x_D]
di "Grid+Year FE baseline: SR×D = " %9.4f `theta_base' " (" %9.4f `theta_base_se' ")"

estimates restore att_dry
local theta_dry = _b[SR_x_D]
local b_dry = _b[drydays_gleam_smrz_le_basep10]
local b_dry_se = _se[drydays_gleam_smrz_le_basep10]
di "Grid+Year +DryDays:    SR×D = " %9.4f `theta_dry' " (attenuation = " ///
    %5.1f ((`theta_base' - `theta_dry') / `theta_base' * 100) "%)"
di "  DryDays → Yield: b = " %9.6f `b_dry' " (" %9.6f `b_dry_se' ")"

estimates restore att_both
local theta_both = _b[SR_x_D]
di "Grid+Year +SM+Dry:     SR×D = " %9.4f `theta_both' " (attenuation = " ///
    %5.1f ((`theta_base' - `theta_both') / `theta_base' * 100) "%)"

estimates restore att_prov
local theta_prov = _b[SR_x_D]
di "Prov×Year baseline:    SR×D = " %9.4f `theta_prov'

estimates restore att_prov_dry
local theta_prov_dry = _b[SR_x_D]
di "Prov×Year +DryDays:    SR×D = " %9.4f `theta_prov_dry'
if `theta_prov' != 0 {
    di "  Prov×Year attenuation = " ///
        %5.1f ((`theta_prov' - `theta_prov_dry') / `theta_prov' * 100) "%"
}


di ""
di "============================================================"
di "  PART B: Sobel Test (Delta Method)"
di "============================================================"

* a-path: SR_x_D → drydays (from step2, re-estimate here for consistency)
reghdfe drydays_gleam_smrz_le_basep10 ///
    D_season W_season hdd_tmax_ge32 ///
    ca SR_x_D SR_x_W SR_x_Heat $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)
local a_coef = _b[SR_x_D]
local a_se = _se[SR_x_D]

* b-path: drydays → yield (from attenuation col 2)
estimates restore att_dry
local b_coef = _b[drydays_gleam_smrz_le_basep10]
local b_se = _se[drydays_gleam_smrz_le_basep10]

* Indirect effect = a * b
local indirect = `a_coef' * `b_coef'

* Sobel SE = sqrt(a² * se_b² + b² * se_a²)
* CAVEAT: This first-order delta method assumes a_hat and b_hat are independently
* estimated. Since a-path and b-path share the same sample and covariates, the
* cross-equation covariance term cov(a_hat, b_hat) is omitted. The bootstrap CI
* in Part C is the definitive test; this Sobel result is an approximation only.
* NOTE: Must parenthesize locals before ^2 to avoid -(x^2) when x is negative
local se_indirect = sqrt((`a_coef')^2 * (`b_se')^2 + (`b_coef')^2 * (`a_se')^2)

* z-statistic
local z_sobel = `indirect' / `se_indirect'
local p_sobel = 2 * normal(-abs(`z_sobel'))

di ""
di "--- Sobel Test Results (Dry Days Mediator) ---"
di "  a-path (SR×D → DryDays): " %9.4f `a_coef' " (SE=" %9.4f `a_se' ")"
di "  b-path (DryDays → Yield): " %9.6f `b_coef' " (SE=" %9.6f `b_se' ")"
di "  Indirect effect (a×b): " %9.6f `indirect'
di "  SE (Sobel): " %9.6f `se_indirect'
di "  z-statistic: " %7.3f `z_sobel'
di "  p-value: " %7.5f `p_sobel'
di "  Total effect (SR×D): " %9.4f `theta_base'
di "  % of total: " %5.1f (`indirect' / `theta_base' * 100) "%"
di ""
if `p_sobel' < 0.01 {
    di "  ==> Indirect effect SIGNIFICANT at 1% level"
}
else if `p_sobel' < 0.05 {
    di "  ==> Indirect effect SIGNIFICANT at 5% level"
}
else {
    di "  ==> Indirect effect NOT significant"
}


di ""
di "============================================================"
di "  PART C: Cluster Bootstrap Indirect Effect"
di "============================================================"
di "  Mediator: drydays_gleam_smrz_le_basep10"
di "  Treatment: SR_x_D"
di "  FE: grid + year"
di "  Cluster: grid_id"
di ""

* --- Define bootstrap program ---
capture program drop mediation_ab
program define mediation_ab, rclass
    version 18

    * a-path: SR_x_D → drydays
    quietly reghdfe drydays_gleam_smrz_le_basep10 ///
        D_season W_season hdd_tmax_ge32 ///
        ca SR_x_D SR_x_W SR_x_Heat ///
        irr_frac pre_sum wd_aridity_et0divpre gdd_30, ///
        absorb(newgrid year) vce(robust)
    local a_coef = _b[SR_x_D]

    * b-path: drydays → yield (controlling SR_x_D)
    quietly reghdfe ln_yield ///
        D_season W_season hdd_tmax_ge32 ///
        ca SR_x_D SR_x_W SR_x_Heat ///
        drydays_gleam_smrz_le_basep10 ///
        irr_frac pre_sum wd_aridity_et0divpre gdd_30, ///
        absorb(newgrid year) vce(robust)
    local b_coef = _b[drydays_gleam_smrz_le_basep10]
    local direct = _b[SR_x_D]

    return scalar indirect = `a_coef' * `b_coef'
    return scalar a_path = `a_coef'
    return scalar b_path = `b_coef'
    return scalar direct = `direct'
end

* --- First: test with 10 reps to verify program works ---
di "--- Testing bootstrap program (10 reps) ---"

* CRITICAL: Clear xtset before bootstrap — cluster bootstrap resamples
* grid_id with replacement, causing repeated year values within same grid_id.
* Without clearing, bootstrap gets r(451) "repeated time values within panel".
xtset, clear

bootstrap ///
    indirect=r(indirect) ///
    a_path=r(a_path) ///
    b_path=r(b_path) ///
    direct=r(direct), ///
    reps(10) seed(42) ///
    cluster(grid_id) idcluster(newgrid) nodots: mediation_ab

di "Test bootstrap complete. Proceeding to full run."
di ""

* --- Full bootstrap: 1000 reps (BC/BCa CIs need >=1000; Efron & Tibshirani 1993) ---
di "--- Full bootstrap (1000 reps, cluster by grid_id) ---"
di "  Start time: $S_TIME"

* Clear xtset again (bootstrap may restore it)
xtset, clear

bootstrap ///
    indirect=r(indirect) ///
    a_path=r(a_path) ///
    b_path=r(b_path) ///
    direct=r(direct), ///
    reps(1000) seed(42) ///
    cluster(grid_id) idcluster(newgrid) nodots: mediation_ab

di "  End time: $S_TIME"
di ""

* --- Bootstrap results ---
di "--- Bootstrap Results (1000 reps) ---"
* NOTE: BCa requires jackknife acceleration constant, not available with Stata's
* bootstrap prefix command. BC is sufficient (prior run showed negligible bias).
estat bootstrap, percentile bc

* Store bootstrap estimates
matrix bs_b = e(b)
matrix bs_ci_p = e(ci_percentile)
matrix bs_ci_bc = e(ci_bc)

di ""
di "--- Summary ---"
di "  Indirect effect (a×b): " %9.6f bs_b[1,1]
di "  95% CI (percentile): [" %9.6f bs_ci_p[1,1] ", " %9.6f bs_ci_p[2,1] "]"
local bc_lo = bs_ci_bc[1,1]
local bc_hi = bs_ci_bc[2,1]
di "  95% CI (bias-corrected): [" %9.6f `bc_lo' ", " %9.6f `bc_hi' "]"
di ""

* Check if CI excludes zero
if `bc_lo' > 0 | `bc_hi' < 0 {
    di "  ==> Bootstrap 95% CI (BC) EXCLUDES ZERO — indirect effect significant"
}
else {
    di "  ==> Bootstrap 95% CI (BC) includes zero — indirect effect NOT significant"
}

di ""
di "  a-path mean: " %9.4f bs_b[1,2]
di "  b-path mean: " %9.6f bs_b[1,3]
di "  Direct effect mean: " %9.4f bs_b[1,4]


di ""
di "============================================================"
di "  Step 3 Complete"
di "============================================================"

log close
