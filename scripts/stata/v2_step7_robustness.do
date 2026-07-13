* =============================================================================
* v2_step7_robustness.do
* Purpose: Robustness checks — FE sensitivity, clustering, heat thresholds,
*          SPEI scales, winsorization, year-drop, concordance matrix.
* Author:  YangSu + Claude
* Date:    2026-04-02
* Input:   data/processed/v2_analysis_ready.dta
* Output:  output/tables/v2_step7_*.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global outdata  "$projdir/data/processed"
global outdir   "$projdir/output/tables"
global logdir   "$projdir/output/logs"

log using "$logdir/v2_step7_robustness_20260402.log", replace

use "$outdata/v2_analysis_ready.dta", clear
xtset grid_id year

* Controls
global CTRL_full irr_frac pr_sum et0_sum aridity gdd_ge10

* =============================================================================
* TEST 1: FE Sensitivity — grid+year vs prov_year vs county_year
*   Run Spec(2) full-season under alternative FE structures
* =============================================================================
di "========================================================"
di "TEST 1: Fixed Effects Sensitivity"
di "========================================================"

eststo clear

* M1: grid + year (baseline)
eststo fe_gy: reghdfe ln_yield ///
	D_full W_full hdd_ge32 ca ///
	SR_x_D_full SR_x_W_full SR_x_Heat_full ///
	D_x_Heat_full SR_x_D_x_Heat_full ///
	$CTRL_full if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)

* M2: grid + prov_year
cap confirm variable prov_year
if _rc == 0 {
	eststo fe_py: reghdfe ln_yield ///
		D_full W_full hdd_ge32 ca ///
		SR_x_D_full SR_x_W_full SR_x_Heat_full ///
		D_x_Heat_full SR_x_D_x_Heat_full ///
		$CTRL_full if main_sample == 1, ///
		absorb(grid_id prov_year) vce(cluster grid_id)
}

* M3: grid + county_year (if county var exists)
cap confirm variable county_year
if _rc == 0 {
	eststo fe_cy: reghdfe ln_yield ///
		D_full W_full hdd_ge32 ca ///
		SR_x_D_full SR_x_W_full SR_x_Heat_full ///
		D_x_Heat_full SR_x_D_x_Heat_full ///
		$CTRL_full if main_sample == 1, ///
		absorb(grid_id county_year) vce(cluster grid_id)
}
else {
	* Try to construct county_year from county_code
	cap confirm variable county_code
	if _rc == 0 {
		cap drop county_year
		egen county_year = group(county_code year)
		eststo fe_cy: reghdfe ln_yield ///
			D_full W_full hdd_ge32 ca ///
			SR_x_D_full SR_x_W_full SR_x_Heat_full ///
			D_x_Heat_full SR_x_D_x_Heat_full ///
			$CTRL_full if main_sample == 1, ///
			absorb(grid_id county_year) vce(cluster grid_id)
	}
	else {
		di "WARNING: county_code not found — skipping county_year FE"
	}
}

esttab fe_* using "$outdir/v2_step7_fe_sensitivity.csv", replace ///
	cells(b(star fmt(4)) se(par fmt(4))) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	stats(r2 N, labels("R-squared" "N") fmt(4 0)) ///
	keep(SR_x_D_full SR_x_Heat_full D_x_Heat_full SR_x_D_x_Heat_full) ///
	title("Test 1: FE Sensitivity — Spec(2) Full Season") ///
	note("Cluster: grid_id.")

* =============================================================================
* TEST 2: Clustering Sensitivity
*   grid_id (baseline), two-way (grid_id year), province
* =============================================================================
di "========================================================"
di "TEST 2: Clustering Sensitivity"
di "========================================================"

eststo clear

* M1: cluster grid_id (baseline)
eststo cl_grid: reghdfe ln_yield ///
	D_full W_full hdd_ge32 ca ///
	SR_x_D_full SR_x_W_full SR_x_Heat_full ///
	D_x_Heat_full SR_x_D_x_Heat_full ///
	$CTRL_full if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)

* M2: two-way cluster (grid_id year)
eststo cl_2way: reghdfe ln_yield ///
	D_full W_full hdd_ge32 ca ///
	SR_x_D_full SR_x_W_full SR_x_Heat_full ///
	D_x_Heat_full SR_x_D_x_Heat_full ///
	$CTRL_full if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id year)

* M3: cluster province
cap confirm variable province_code
if _rc == 0 {
	eststo cl_prov: reghdfe ln_yield ///
		D_full W_full hdd_ge32 ca ///
		SR_x_D_full SR_x_W_full SR_x_Heat_full ///
		D_x_Heat_full SR_x_D_x_Heat_full ///
		$CTRL_full if main_sample == 1, ///
		absorb(grid_id year) vce(cluster province_code)
}
else {
	di "WARNING: province_code not found — skipping province clustering"
}

esttab cl_* using "$outdir/v2_step7_cluster_sensitivity.csv", replace ///
	cells(b(star fmt(4)) se(par fmt(4))) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	stats(r2 N, labels("R-squared" "N") fmt(4 0)) ///
	keep(SR_x_D_full SR_x_Heat_full D_x_Heat_full SR_x_D_x_Heat_full) ///
	title("Test 2: Clustering Sensitivity — Spec(2) Full Season") ///
	note("FE: grid+year.")

* =============================================================================
* TEST 3: Heat Threshold Sensitivity (30/32/35°C)
* =============================================================================
di "========================================================"
di "TEST 3: Heat Threshold Sensitivity"
di "========================================================"

eststo clear

foreach thresh in 30 32 35 {
	cap confirm variable hdd_ge`thresh'
	if _rc == 0 {
		* Construct interactions for this threshold
		cap drop SR_x_H`thresh'
		cap drop D_x_H`thresh'
		cap drop SR_x_DxH`thresh'
		gen SR_x_H`thresh' = ca * hdd_ge`thresh'
		gen D_x_H`thresh' = D_full * hdd_ge`thresh'
		gen SR_x_DxH`thresh' = ca * D_full * hdd_ge`thresh'

		eststo ht_`thresh': reghdfe ln_yield ///
			D_full W_full hdd_ge`thresh' ca ///
			SR_x_D_full SR_x_W_full SR_x_H`thresh' ///
			D_x_H`thresh' SR_x_DxH`thresh' ///
			$CTRL_full if main_sample == 1, ///
			absorb(grid_id year) vce(cluster grid_id)

		di "Threshold `thresh'C: SR×H=" %7.4f _b[SR_x_H`thresh'] ///
		   " SR×D×H=" %7.4f _b[SR_x_DxH`thresh']
	}
	else {
		di "WARNING: hdd_ge`thresh' not found — skipping"
	}
}

cap esttab ht_* using "$outdir/v2_step7_heat_threshold.csv", replace ///
	cells(b(star fmt(4)) se(par fmt(4))) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	stats(r2 N, labels("R-squared" "N") fmt(4 0)) ///
	title("Test 3: Heat Threshold Sensitivity — 30/32/35°C") ///
	note("FE: grid+year. Cluster: grid_id.")

* =============================================================================
* TEST 4: SPEI Scale Sensitivity (full season: spei1 vs spei2 vs spei6)
* =============================================================================
di "========================================================"
di "TEST 4: SPEI Scale Sensitivity"
di "========================================================"

eststo clear

foreach spei_scale in 1 2 6 {
	local spei_var "spei`spei_scale'_mean"
	cap confirm variable `spei_var'
	if _rc == 0 {
		cap drop D_spei`spei_scale'
		cap drop W_spei`spei_scale'
		cap drop SRxD_spei`spei_scale'
		cap drop SRxW_spei`spei_scale'
		gen D_spei`spei_scale' = max(0, -`spei_var')
		gen W_spei`spei_scale' = max(0, `spei_var')
		gen SRxD_spei`spei_scale' = ca * D_spei`spei_scale'
		gen SRxW_spei`spei_scale' = ca * W_spei`spei_scale'

		eststo sp_`spei_scale': reghdfe ln_yield ///
			D_spei`spei_scale' W_spei`spei_scale' hdd_ge32 ca ///
			SRxD_spei`spei_scale' SRxW_spei`spei_scale' SR_x_Heat_full ///
			$CTRL_full if main_sample == 1, ///
			absorb(grid_id year) vce(cluster grid_id)

		di "SPEI-`spei_scale': SR×D=" %7.4f _b[SRxD_spei`spei_scale'] ///
		   " (SE=" %7.4f _se[SRxD_spei`spei_scale'] ")"
	}
	else {
		di "WARNING: `spei_var' not found — skipping"
	}
}

cap esttab sp_* using "$outdir/v2_step7_spei_scale.csv", replace ///
	cells(b(star fmt(4)) se(par fmt(4))) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	stats(r2 N, labels("R-squared" "N") fmt(4 0)) ///
	title("Test 4: SPEI Scale Sensitivity (Full Season)") ///
	note("FE: grid+year. Cluster: grid_id.")

* =============================================================================
* TEST 5: Winsorization (1st/99th percentile)
* =============================================================================
di "========================================================"
di "TEST 5: Winsorization"
di "========================================================"

preserve

* Winsorize key continuous variables at 1/99
foreach var of varlist ln_yield D_full W_full hdd_ge32 {
	qui sum `var' if main_sample == 1, detail
	local p1 = r(p1)
	local p99 = r(p99)
	replace `var' = `p1' if `var' < `p1' & main_sample == 1
	replace `var' = `p99' if `var' > `p99' & main_sample == 1 & !missing(`var')
}

* Reconstruct interactions with winsorized values
replace SR_x_D_full = ca * D_full
replace SR_x_W_full = ca * W_full
replace SR_x_Heat_full = ca * hdd_ge32
replace D_x_Heat_full = D_full * hdd_ge32
replace SR_x_D_x_Heat_full = ca * D_full * hdd_ge32

eststo clear
eststo win: reghdfe ln_yield ///
	D_full W_full hdd_ge32 ca ///
	SR_x_D_full SR_x_W_full SR_x_Heat_full ///
	D_x_Heat_full SR_x_D_x_Heat_full ///
	$CTRL_full if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)

esttab win using "$outdir/v2_step7_winsorized.csv", replace ///
	cells(b(star fmt(4)) se(par fmt(4))) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	stats(r2 N, labels("R-squared" "N") fmt(4 0)) ///
	title("Test 5: Winsorized (1/99) Spec(2)") ///
	note("FE: grid+year. Cluster: grid_id.")

restore

* =============================================================================
* TEST 6: Year-Drop Sensitivity (leave-one-year-out)
* =============================================================================
di "========================================================"
di "TEST 6: Year-Drop Sensitivity"
di "========================================================"

tempname pf
postfile `pf' dropped_year ///
	b_SRD se_SRD p_SRD ///
	b_SRH se_SRH p_SRH ///
	b_DH se_DH p_DH ///
	b_SRDH se_SRDH p_SRDH ///
	N ///
	using "$outdir/v2_step7_yeardrop.dta", replace

forvalues yr = 2016/2019 {
	qui reghdfe ln_yield ///
		D_full W_full hdd_ge32 ca ///
		SR_x_D_full SR_x_W_full SR_x_Heat_full ///
		D_x_Heat_full SR_x_D_x_Heat_full ///
		$CTRL_full if main_sample == 1 & year != `yr', ///
		absorb(grid_id year) vce(cluster grid_id)

	post `pf' (`yr') ///
		(_b[SR_x_D_full]) (_se[SR_x_D_full]) ///
		(2*ttail(e(df_r), abs(_b[SR_x_D_full]/_se[SR_x_D_full]))) ///
		(_b[SR_x_Heat_full]) (_se[SR_x_Heat_full]) ///
		(2*ttail(e(df_r), abs(_b[SR_x_Heat_full]/_se[SR_x_Heat_full]))) ///
		(_b[D_x_Heat_full]) (_se[D_x_Heat_full]) ///
		(2*ttail(e(df_r), abs(_b[D_x_Heat_full]/_se[D_x_Heat_full]))) ///
		(_b[SR_x_D_x_Heat_full]) (_se[SR_x_D_x_Heat_full]) ///
		(2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat_full]/_se[SR_x_D_x_Heat_full]))) ///
		(e(N))

	di "Drop `yr': SR×D=" %7.4f _b[SR_x_D_full] ///
	   " SR×H=" %7.4f _b[SR_x_Heat_full] ///
	   " SR×D×H=" %7.4f _b[SR_x_D_x_Heat_full]
}

postclose `pf'

preserve
use "$outdir/v2_step7_yeardrop.dta", clear
list, sep(0) noobs
export delimited using "$outdir/v2_step7_yeardrop.csv", replace
restore

* =============================================================================
* TEST 7: SM Source Concordance Matrix
*   For each key coefficient, report sign and significance across
*   3 SM sources x 5 windows — used for heatmap visualization
* =============================================================================
di "========================================================"
di "TEST 7: SM Source Concordance Matrix"
di "========================================================"

* This data already exists in v2_step4_interaction_grid.dta
* Summarize key patterns from Step 4 results
preserve
use "$outdir/v2_step4_interaction_grid.dta", clear

* Compute sign-significance indicators
gen sig_SRD = cond(p_SRD < 0.01, "***", cond(p_SRD < 0.05, "**", ///
			  cond(p_SRD < 0.10, "*", "n.s.")))
gen sign_SRD = cond(b_SRD > 0, "+", "-")

gen sig_SRH = cond(p_SRH < 0.01, "***", cond(p_SRH < 0.05, "**", ///
			  cond(p_SRH < 0.10, "*", "n.s.")))
gen sign_SRH = cond(b_SRH > 0, "+", "-")

gen sig_SRDH = cond(p_SRDH < 0.01, "***", cond(p_SRDH < 0.05, "**", ///
			   cond(p_SRDH < 0.10, "*", "n.s.")))
gen sign_SRDH = cond(b_SRDH > 0, "+", "-")

* Display concordance
list window spec sm_src sign_SRD sig_SRD sign_SRH sig_SRH sign_SRDH sig_SRDH ///
	if spec == "spec2" | spec == "spec4", sep(5) noobs

export delimited using "$outdir/v2_step7_concordance.csv", replace

restore

* =============================================================================
* TEST 8: Spec(2) across all 5 windows with prov_year FE
*   Strongest robustness test for all windows
* =============================================================================
di "========================================================"
di "TEST 8: Prov-Year FE across windows"
di "========================================================"

cap confirm variable prov_year
if _rc == 0 {
	tempname pf2
	postfile `pf2' str10 window ///
		b_SRD se_SRD p_SRD ///
		b_SRH se_SRH p_SRH ///
		b_SRDH se_SRDH p_SRDH ///
		N ///
		using "$outdir/v2_step7_provyr_windows.dta", replace

	foreach wsfx in "" "_v3pm10" "_hepm10" "_v3he" "_hema" {
		local wlbl = cond("`wsfx'" == "", "full", substr("`wsfx'", 2, .))
		local wlbl2 = cond("`wsfx'" == "", "_full", "`wsfx'")
		local h_var = cond("`wsfx'" == "", "hdd_ge32", "hdd_ge32`wsfx'")
		local ctrl "CTRL`wlbl2'"

		* Redefine controls for each window
		local ctrl_vars = cond("`wsfx'" == "", ///
			"irr_frac pr_sum et0_sum aridity gdd_ge10", ///
			cond("`wsfx'" == "_v3pm10", ///
			"irr_frac pr_sum_v3pm10 et0_sum_v3pm10 aridity gdd_ge10_v3pm10", ///
			cond("`wsfx'" == "_hepm10", ///
			"irr_frac pr_sum_hepm10 et0_sum_hepm10 aridity gdd_ge10_hepm10", ///
			cond("`wsfx'" == "_v3he", ///
			"irr_frac pr_sum_v3he et0_sum_v3he aridity gdd_ge10_v3he", ///
			"irr_frac pr_sum_hema et0_sum_hema aridity gdd_ge10_hema"))))

		qui reghdfe ln_yield ///
			D`wlbl2' W`wlbl2' `h_var' ca ///
			SR_x_D`wlbl2' SR_x_W`wlbl2' SR_x_Heat`wlbl2' ///
			D_x_Heat`wlbl2' SR_x_D_x_Heat`wlbl2' ///
			`ctrl_vars' if main_sample == 1, ///
			absorb(grid_id prov_year) vce(cluster grid_id)

		post `pf2' ("`wlbl'") ///
			(_b[SR_x_D`wlbl2']) (_se[SR_x_D`wlbl2']) ///
			(2*ttail(e(df_r), abs(_b[SR_x_D`wlbl2']/_se[SR_x_D`wlbl2']))) ///
			(_b[SR_x_Heat`wlbl2']) (_se[SR_x_Heat`wlbl2']) ///
			(2*ttail(e(df_r), abs(_b[SR_x_Heat`wlbl2']/_se[SR_x_Heat`wlbl2']))) ///
			(_b[SR_x_D_x_Heat`wlbl2']) (_se[SR_x_D_x_Heat`wlbl2']) ///
			(2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat`wlbl2']/_se[SR_x_D_x_Heat`wlbl2']))) ///
			(e(N))

		di "ProvYr `wlbl': SR×D=" %7.4f _b[SR_x_D`wlbl2'] ///
		   " SR×H=" %7.4f _b[SR_x_Heat`wlbl2'] ///
		   " SR×D×H=" %7.4f _b[SR_x_D_x_Heat`wlbl2']
	}

	postclose `pf2'

	preserve
	use "$outdir/v2_step7_provyr_windows.dta", clear
	list, sep(0) noobs
	export delimited using "$outdir/v2_step7_provyr_windows.csv", replace
	restore
}
else {
	di "WARNING: prov_year not found — skipping Test 8"
}

log close
di "=== v2_step7_robustness.do COMPLETE ==="
