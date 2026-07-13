* =============================================================================
* v2_step3_sm_source_comparison.do
* Purpose: SM data source robustness — compare 3 SM sources across windows.
*          Tests: attenuation, a-path (SR×D→SM), SM state dependence,
*          dry-days alternative.
* Author:  YangSu + Claude
* Date:    2026-04-02
* Input:   data/processed/v2_analysis_ready.dta
* Output:  output/tables/v2_step3_sm_comparison.csv (+ sub-tables)
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global outdata  "$projdir/data/processed"
global outdir   "$projdir/output/tables"
global logdir   "$projdir/output/logs"

log using "$logdir/v2_step3_sm_comparison_20260402.log", replace

use "$outdata/v2_analysis_ready.dta", clear
xtset grid_id year

* Controls by window
global CTRL_full    irr_frac pr_sum et0_sum aridity gdd_ge10
global CTRL_v3pm10  irr_frac pr_sum_v3pm10 et0_sum_v3pm10 aridity gdd_ge10_v3pm10
global CTRL_hepm10  irr_frac pr_sum_hepm10 et0_sum_hepm10 aridity gdd_ge10_hepm10
global CTRL_v3he    irr_frac pr_sum_v3he et0_sum_v3he aridity gdd_ge10_v3he
global CTRL_hema    irr_frac pr_sum_hema et0_sum_hema aridity gdd_ge10_hema

* Focus windows: full + the two best (v3he, hepm10 based on Step 4 results)
* Will also do hema for biological ordering

* =============================================================================
* PART A: Attenuation test — 3 SM sources x 4 windows
*   Compare Spec(1) vs Spec(3) for each SM source in each window
*   This is a distillation from Step 4 focused on the SM channel
* =============================================================================
di "========================================================"
di "PART A: Attenuation across SM sources and windows"
di "========================================================"

tempname pf
postfile `pf' str10 window str10 sm_src ///
	b_SRD_noSM se_SRD_noSM p_SRD_noSM ///
	b_SRD_wSM se_SRD_wSM p_SRD_wSM ///
	b_SRH_noSM se_SRH_noSM p_SRH_noSM ///
	b_SRH_wSM se_SRH_wSM p_SRH_wSM ///
	attn_SRD attn_SRH N ///
	using "$outdir/v2_step3_attenuation_detail.dta", replace

foreach wsfx in "" "_v3pm10" "_hepm10" "_v3he" "_hema" {
	local wlbl = cond("`wsfx'" == "", "full", substr("`wsfx'", 2, .))
	local wlbl2 = cond("`wsfx'" == "", "_full", "`wsfx'")
	local h_var = cond("`wsfx'" == "", "hdd_ge32", "hdd_ge32`wsfx'")
	local ctrl "CTRL`wlbl2'"

	* --- Spec(1) baseline (no SM) ---
	qui reghdfe ln_yield D`wlbl2' W`wlbl2' `h_var' ca ///
		SR_x_D`wlbl2' SR_x_W`wlbl2' SR_x_Heat`wlbl2' ///
		$`ctrl' if main_sample == 1, ///
		absorb(grid_id year) vce(cluster grid_id)

	local b1_SRD = _b[SR_x_D`wlbl2']
	local se1_SRD = _se[SR_x_D`wlbl2']
	local p1_SRD = 2*ttail(e(df_r), abs(`b1_SRD'/`se1_SRD'))
	local b1_SRH = _b[SR_x_Heat`wlbl2']
	local se1_SRH = _se[SR_x_Heat`wlbl2']
	local p1_SRH = 2*ttail(e(df_r), abs(`b1_SRH'/`se1_SRH'))

	* --- Spec(3) with each SM source ---
	foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
		local slbl = cond("`src'" == "gleam_smrz", "gleam", ///
					 cond("`src'" == "swsm_l3", "swsm", "era5l"))
		local smvar = cond("`src'" == "gleam_smrz", "gsm", ///
					  cond("`src'" == "swsm_l3", "ssm", "esm"))

		qui reghdfe ln_yield D`wlbl2' W`wlbl2' `h_var' ca ///
			SR_x_D`wlbl2' SR_x_W`wlbl2' SR_x_Heat`wlbl2' ///
			`src'_mean`wsfx' `smvar'_x_D`wlbl2' `smvar'_x_H`wlbl2' `smvar'_x_SR`wlbl2' ///
			$`ctrl' if main_sample == 1, ///
			absorb(grid_id year) vce(cluster grid_id)

		local b3_SRD = _b[SR_x_D`wlbl2']
		local se3_SRD = _se[SR_x_D`wlbl2']
		local p3_SRD = 2*ttail(e(df_r), abs(`b3_SRD'/`se3_SRD'))
		local b3_SRH = _b[SR_x_Heat`wlbl2']
		local se3_SRH = _se[SR_x_Heat`wlbl2']
		local p3_SRH = 2*ttail(e(df_r), abs(`b3_SRH'/`se3_SRH'))

		local att_SRD = cond(`b1_SRD' != 0, 100*(1 - `b3_SRD'/`b1_SRD'), .)
		local att_SRH = cond(`b1_SRH' != 0, 100*(1 - `b3_SRH'/`b1_SRH'), .)

		post `pf' ("`wlbl'") ("`slbl'") ///
			(`b1_SRD') (`se1_SRD') (`p1_SRD') ///
			(`b3_SRD') (`se3_SRD') (`p3_SRD') ///
			(`b1_SRH') (`se1_SRH') (`p1_SRH') ///
			(`b3_SRH') (`se3_SRH') (`p3_SRH') ///
			(`att_SRD') (`att_SRH') (e(N))

		di "`wlbl' x `slbl': SRD attn=" %5.1f `att_SRD' "%, SRH attn=" %5.1f `att_SRH' "%"
	}
}

postclose `pf'

preserve
use "$outdir/v2_step3_attenuation_detail.dta", clear
list, sep(3) noobs
export delimited using "$outdir/v2_step3_attenuation_detail.csv", replace
restore

* =============================================================================
* PART B: a-path — SM regressed on compound RHS
*   SM = D + H + SR + SR×D + SR×H + Controls + FE
*   Key: SR×D > 0 means SR protects SM under drought
* =============================================================================
di "========================================================"
di "PART B: a-path — SR -> SM under drought"
di "========================================================"

tempname pf2
postfile `pf2' str10 window str10 sm_src ///
	b_D se_D p_D b_SRD se_SRD p_SRD ///
	b_H se_H p_H b_SRH se_SRH p_SRH ///
	b_SR se_SR p_SR N r2 ///
	using "$outdir/v2_step3_apath.dta", replace

foreach wsfx in "" "_v3pm10" "_hepm10" "_v3he" "_hema" {
	local wlbl = cond("`wsfx'" == "", "full", substr("`wsfx'", 2, .))
	local wlbl2 = cond("`wsfx'" == "", "_full", "`wsfx'")
	local h_var = cond("`wsfx'" == "", "hdd_ge32", "hdd_ge32`wsfx'")
	local ctrl "CTRL`wlbl2'"

	foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
		local slbl = cond("`src'" == "gleam_smrz", "gleam", ///
					 cond("`src'" == "swsm_l3", "swsm", "era5l"))

		qui reghdfe `src'_mean`wsfx' ///
			D`wlbl2' `h_var' ca SR_x_D`wlbl2' SR_x_Heat`wlbl2' ///
			$`ctrl' if main_sample == 1, ///
			absorb(grid_id year) vce(cluster grid_id)

		post `pf2' ("`wlbl'") ("`slbl'") ///
			(_b[D`wlbl2']) (_se[D`wlbl2']) ///
			(2*ttail(e(df_r), abs(_b[D`wlbl2']/_se[D`wlbl2']))) ///
			(_b[SR_x_D`wlbl2']) (_se[SR_x_D`wlbl2']) ///
			(2*ttail(e(df_r), abs(_b[SR_x_D`wlbl2']/_se[SR_x_D`wlbl2']))) ///
			(_b[`h_var']) (_se[`h_var']) ///
			(2*ttail(e(df_r), abs(_b[`h_var']/_se[`h_var']))) ///
			(_b[SR_x_Heat`wlbl2']) (_se[SR_x_Heat`wlbl2']) ///
			(2*ttail(e(df_r), abs(_b[SR_x_Heat`wlbl2']/_se[SR_x_Heat`wlbl2']))) ///
			(_b[ca]) (_se[ca]) ///
			(2*ttail(e(df_r), abs(_b[ca]/_se[ca]))) ///
			(e(N)) (e(r2))

		di "`wlbl' x `slbl': D→SM=" %7.4f _b[D`wlbl2'] ///
		   ", SR×D→SM=" %7.4f _b[SR_x_D`wlbl2']
	}
}

postclose `pf2'

preserve
use "$outdir/v2_step3_apath.dta", clear
list, sep(3) noobs
export delimited using "$outdir/v2_step3_apath.csv", replace
restore

* =============================================================================
* PART C: SM state dependence — SM × Heat interaction
*   Does low SM amplify heat damage? (SM x H < 0 means yes)
*   3 SM sources x 5 windows
* =============================================================================
di "========================================================"
di "PART C: SM state dependence — SM x Heat"
di "========================================================"

tempname pf3
postfile `pf3' str10 window str10 sm_src ///
	b_SM se_SM p_SM b_SMxH se_SMxH p_SMxH ///
	b_SMxD se_SMxD p_SMxD N ///
	using "$outdir/v2_step3_state_dep.dta", replace

foreach wsfx in "" "_v3pm10" "_hepm10" "_v3he" "_hema" {
	local wlbl = cond("`wsfx'" == "", "full", substr("`wsfx'", 2, .))
	local wlbl2 = cond("`wsfx'" == "", "_full", "`wsfx'")
	local h_var = cond("`wsfx'" == "", "hdd_ge32", "hdd_ge32`wsfx'")
	local ctrl "CTRL`wlbl2'"

	foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
		local slbl = cond("`src'" == "gleam_smrz", "gleam", ///
					 cond("`src'" == "swsm_l3", "swsm", "era5l"))
		local smvar = cond("`src'" == "gleam_smrz", "gsm", ///
					  cond("`src'" == "swsm_l3", "ssm", "esm"))

		qui reghdfe ln_yield D`wlbl2' W`wlbl2' `h_var' ca ///
			SR_x_D`wlbl2' SR_x_W`wlbl2' SR_x_Heat`wlbl2' ///
			`src'_mean`wsfx' `smvar'_x_D`wlbl2' `smvar'_x_H`wlbl2' ///
			$`ctrl' if main_sample == 1, ///
			absorb(grid_id year) vce(cluster grid_id)

		post `pf3' ("`wlbl'") ("`slbl'") ///
			(_b[`src'_mean`wsfx']) (_se[`src'_mean`wsfx']) ///
			(2*ttail(e(df_r), abs(_b[`src'_mean`wsfx']/_se[`src'_mean`wsfx']))) ///
			(_b[`smvar'_x_H`wlbl2']) (_se[`smvar'_x_H`wlbl2']) ///
			(2*ttail(e(df_r), abs(_b[`smvar'_x_H`wlbl2']/_se[`smvar'_x_H`wlbl2']))) ///
			(_b[`smvar'_x_D`wlbl2']) (_se[`smvar'_x_D`wlbl2']) ///
			(2*ttail(e(df_r), abs(_b[`smvar'_x_D`wlbl2']/_se[`smvar'_x_D`wlbl2']))) ///
			(e(N))

		di "`wlbl' x `slbl': SM×H=" %7.4f _b[`smvar'_x_H`wlbl2'] ///
		   ", SM×D=" %7.4f _b[`smvar'_x_D`wlbl2']
	}
}

postclose `pf3'

preserve
use "$outdir/v2_step3_state_dep.dta", clear
list, sep(3) noobs
export delimited using "$outdir/v2_step3_state_dep.csv", replace
restore

* =============================================================================
* PART D: Dry-days alternative — use SM dry-days instead of SPEI-based D
*   Tests whether SM-defined drought gives similar SR buffering results
* =============================================================================
di "========================================================"
di "PART D: SM dry-days as alternative drought measure"
di "========================================================"

eststo clear

* Full season only — drydays p10 thresholds
* Check if variables exist first
foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
	local slbl = cond("`src'" == "gleam_smrz", "gleam", ///
				 cond("`src'" == "swsm_l3", "swsm", "era5l"))
	cap confirm variable drydays_`src'_le_p10
	if _rc == 0 {
		* Construct SR × drydays interactions
		cap drop SR_x_drydays_`slbl'
		gen SR_x_drydays_`slbl' = ca * drydays_`src'_le_p10

		eststo dd_`slbl': reghdfe ln_yield ///
			drydays_`src'_le_p10 W_full hdd_ge32 ca ///
			SR_x_drydays_`slbl' SR_x_W_full SR_x_Heat_full ///
			$CTRL_full if main_sample == 1, ///
			absorb(grid_id year) vce(cluster grid_id)

		di "`slbl': SR×drydays = " %7.4f _b[SR_x_drydays_`slbl'] ///
		   " (se=" %7.4f _se[SR_x_drydays_`slbl'] ")"
	}
	else {
		di "WARNING: drydays_`src'_le_p10 not found — skipping"
	}
}

* Export if any models estimated
local n_models : word count `e(cmdline)'
cap esttab dd_gleam dd_swsm dd_era5l ///
	using "$outdir/v2_step3_drydays.csv", replace ///
	cells(b(star fmt(4)) se(par fmt(4))) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	stats(r2 N, labels("R-squared" "N") fmt(4 0)) ///
	mtitles("GLEAM-drydays" "SWSM-drydays" "ERA5L-drydays") ///
	title("Step 3D: SM Dry-Days as Alternative D") ///
	note("DV = ln_yield. FE: grid+year. Cluster: grid_id.")

* =============================================================================
* SUMMARY: Concordance matrix across SM sources
* =============================================================================
di "========================================================"
di "SUMMARY: SM Source Concordance"
di "========================================================"

* Display a compact summary of sign/significance across all combinations
di "  Window | SM_src | SRD_attn% | SRH_attn% | a-path_SRD | SMxH"
di "  -------+--------+-----------+-----------+------------+-----"

preserve
use "$outdir/v2_step3_attenuation_detail.dta", clear
list window sm_src attn_SRD attn_SRH, sep(3) noobs
restore

log close
di "=== v2_step3_sm_source_comparison.do COMPLETE ==="
