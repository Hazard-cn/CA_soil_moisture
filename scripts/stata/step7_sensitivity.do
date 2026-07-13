* =============================================================================
* step7_sensitivity.do — Sensitivity Checks + SM Mechanism Fix
* Purpose: Test robustness across heat thresholds, FE, clustering, lag SR,
*          SR autocorrelation, and SM mechanism alternatives
* Author: YangSu / Claude Code
* Date: 2026-03-12
* Dependencies: 00_preamble.do, reghdfe, estout
* =============================================================================

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/00_preamble.do"

log using "$logdir/step7_sensitivity_20260312.log", replace

di "============================================================"
di "Step 7: Sensitivity Checks"
di "============================================================"

* =============================================================================
* Part A: Heat Threshold Sensitivity
* =============================================================================

di _n "=== Part 7A: Heat Threshold Sensitivity ==="

eststo clear

foreach thresh in 30 32 35 {
	cap drop SR_x_H`thresh'
	gen SR_x_H`thresh' = ca * hdd_tmax_ge`thresh'
	label var SR_x_H`thresh' "SR x HDD>=`thresh'"

	eststo ht`thresh': reghdfe ln_yield D_season W_season hdd_tmax_ge`thresh' ///
		ca SR_x_D SR_x_W SR_x_H`thresh' $CTRL, ///
		absorb(grid_id year) vce(cluster grid_id)
}

esttab ht30 ht32 ht35 ///
	using "$outdir/step7_heat_threshold.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("HDD>=30" "HDD>=32" "HDD>=35") ///
	title("Step 7A: Heat Threshold Sensitivity")

esttab ht30 ht32 ht35 ///
	using "$outdir/step7_heat_threshold.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("HDD>=30" "HDD>=32" "HDD>=35") booktabs

* =============================================================================
* Part B: FE Structure & Clustering
* =============================================================================

di _n "=== Part 7B: FE Structure & Clustering ==="

eststo clear

* (1) Baseline: grid + year FE, grid cluster
eststo fe_base: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

* (2) Province-year FE (replaces year FE)
eststo fe_provyr: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id prov_year) vce(cluster grid_id)

* (3) Two-way clustering: grid + year
eststo cl_2way: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id year)

* (4) Lagged SR (crc_lag1)
cap drop SR_lag_x_D SR_lag_x_W SR_lag_x_Heat
gen SR_lag_x_D    = crc_lag1 * D_season
gen SR_lag_x_W    = crc_lag1 * W_season
gen SR_lag_x_Heat = crc_lag1 * hdd_tmax_ge32
label var SR_lag_x_D    "SR(t-1) x Drought"
label var SR_lag_x_W    "SR(t-1) x Wetness"
label var SR_lag_x_Heat "SR(t-1) x Heat"

eststo lag_sr: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	crc_lag1 SR_lag_x_D SR_lag_x_W SR_lag_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

esttab fe_base fe_provyr cl_2way lag_sr ///
	using "$outdir/step7_fe_cluster.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("Baseline" "Prov-Year FE" "2-Way Cluster" "Lag SR") ///
	title("Step 7B: FE Structure, Clustering, and Lagged SR") ///
	addnote("Col 1: grid+year FE, grid cluster." ///
		"Col 2: grid+prov_year FE, grid cluster." ///
		"Col 3: grid+year FE, grid+year 2-way cluster." ///
		"Col 4: Uses crc_lag1 instead of ca.")

esttab fe_base fe_provyr cl_2way lag_sr ///
	using "$outdir/step7_fe_cluster.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("Baseline" "Prov-Year FE" "2-Way Cluster" "Lag SR") booktabs

* =============================================================================
* Part C: SR Autocorrelation Diagnostic
* =============================================================================

di _n "=== Part 7C: SR Autocorrelation ==="

* Generate lead SR
gen SR_lead1 = F.ca
label var SR_lead1 "SR(t+1)"

* Correlation table
corr ca SR_lead1

* Also compute for subsample with non-missing lead
corr ca SR_lead1 if !missing(SR_lead1)

di _n "--- If rho > 0.9, this explains why SR_f1 x D is significant in Step 2 ---"

* Save autocorrelation summary
preserve
	collapse (mean) ca_mean=ca (sd) ca_sd=ca, by(grid_id)
	gen cv_ca = ca_sd / ca_mean if ca_mean > 0
	sum cv_ca, detail
	di "CV of CA within-grid: mean = " r(mean) " median = " r(p50)
restore

* =============================================================================
* Part D: SM Mechanism Fix — Alternative Approaches
* =============================================================================

di _n "=== Part 7D: SM Mechanism Alternatives ==="

eststo clear

* --- D1: Baseline (for reference) ---
eststo sm_base: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

* --- D2: Province-year FE (preserves more SM variation) ---
eststo sm_provyr: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat gleam_smrz_mean $CTRL, ///
	absorb(grid_id prov_year) vce(cluster grid_id)

* --- D3: Province-year FE + SM tails ---
eststo sm_provyr_tails: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat ///
	gleam_smrz_mean drydays_gleam_smrz_le_basep10 $CTRL, ///
	absorb(grid_id prov_year) vce(cluster grid_id)

* --- D4: SM as dependent variable (SR → SM pathway) ---
di _n "--- D4: Does SR improve soil moisture? ---"
eststo sr_to_sm: reghdfe gleam_smrz_mean ca D_season W_season ///
	hdd_tmax_ge32 SR_x_D $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
di "   ca coef: SR effect on SM (expect > 0 if SR improves SM)"
di "   SR_x_D coef: SR x Drought effect on SM (expect > 0 if SR buffers SM under drought)"

* --- D5: SM as DV with prov-year FE ---
eststo sr_to_sm_prov: reghdfe gleam_smrz_mean ca D_season W_season ///
	hdd_tmax_ge32 SR_x_D $CTRL, ///
	absorb(grid_id prov_year) vce(cluster grid_id)

esttab sm_base sm_provyr sm_provyr_tails sr_to_sm sr_to_sm_prov ///
	using "$outdir/step7_sm_mechanism.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("Baseline" "ProvYr+SM" "ProvYr+Tails" "SR->SM" "SR->SM(prov)") ///
	title("Step 7D: SM Mechanism Fix — Alternative Specifications") ///
	addnote("Cols 1-3: DV = ln_yield. Cols 4-5: DV = gleam_smrz_mean." ///
		"Col 2-3 use prov_year FE to preserve more SM variation.")

esttab sm_base sm_provyr sm_provyr_tails sr_to_sm sr_to_sm_prov ///
	using "$outdir/step7_sm_mechanism.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("Baseline" "ProvYr+SM" "ProvYr+Tails" "SR->SM" "SR->SM(prov)") booktabs

di _n "============================================================"
di "Step 7 Summary"
di "============================================================"
di "Check: Core conclusions robust across specifications?"
di "Check: SR autocorrelation explains lead test anomaly?"
di "Check: SM mechanism shows anything under province-year FE?"
di "============================================================"

log close
di "=== Step 7 complete. Outputs in $outdir/step7_*.csv ==="
