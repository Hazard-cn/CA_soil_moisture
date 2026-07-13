* =============================================================================
* v2_spei_comparison.do
* Purpose: Compare v1-SPEI (all windows use SPEI-6/D_full) vs v2-SPEI
*          (sub-windows use SPEI-1/2) across all key specifications.
* Author:  YangSu + Claude
* Date:    2026-04-03
* Input:   data/processed/v2_analysis_ready.dta
* Output:  output/tables/v2_spei_comparison_*.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global outdata  "$projdir/data/processed"
global outdir   "$projdir/output/tables"
global logdir   "$projdir/output/logs"

log using "$logdir/v2_spei_comparison_20260403.log", replace

use "$outdata/v2_analysis_ready.dta", clear
xtset grid_id year

* Controls by window (Heat and controls still window-specific in both versions)
global CTRL_full    irr_frac pr_sum et0_sum aridity gdd_ge10
global CTRL_v3pm10  irr_frac pr_sum_v3pm10 et0_sum_v3pm10 aridity gdd_ge10_v3pm10
global CTRL_hepm10  irr_frac pr_sum_hepm10 et0_sum_hepm10 aridity gdd_ge10_hepm10
global CTRL_v3he    irr_frac pr_sum_v3he et0_sum_v3he aridity gdd_ge10_v3he
global CTRL_hema    irr_frac pr_sum_hema et0_sum_hema aridity gdd_ge10_hema

* =============================================================================
* 1. CONSTRUCT v1-SPEI INTERACTIONS FOR SUB-WINDOWS
*    v1-SPEI: all windows use D_full (from spei6_mean) and W_full
*    Heat is still window-specific
* =============================================================================
di "========================================================"
di "1. Constructing v1-SPEI interaction terms"
di "========================================================"

foreach wsfx in "_v3pm10" "_hepm10" "_v3he" "_hema" {
	local h_var "hdd_ge32`wsfx'"

	* SR interactions (v1: use D_full for all windows)
	cap drop SR_x_D_v1`wsfx'
	gen SR_x_D_v1`wsfx' = ca * D_full
	cap drop SR_x_W_v1`wsfx'
	gen SR_x_W_v1`wsfx' = ca * W_full
	* SR_x_Heat stays window-specific (same in both versions)

	* Compound interactions (v1)
	cap drop D_x_Heat_v1`wsfx'
	gen D_x_Heat_v1`wsfx' = D_full * `h_var'
	cap drop SR_x_D_x_Heat_v1`wsfx'
	gen SR_x_D_x_Heat_v1`wsfx' = ca * D_full * `h_var'

	* SM interactions with v1-D (for Spec 3/4)
	foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
		local slbl = cond("`src'" == "gleam_smrz", "gsm", ///
					 cond("`src'" == "swsm_l3", "ssm", "esm"))
		local sm_var "`src'_mean`wsfx'"

		cap drop `slbl'_x_Dv1`wsfx'
		gen `slbl'_x_Dv1`wsfx' = `sm_var' * D_full

		cap drop `slbl'_x_DHv1`wsfx'
		gen `slbl'_x_DHv1`wsfx' = `sm_var' * D_full * `h_var'

		cap drop `slbl'_x_SRDHv1`wsfx'
		gen `slbl'_x_SRDHv1`wsfx' = `sm_var' * ca * D_full * `h_var'
	}
}

* =============================================================================
* 2. CORE COMPARISON: Spec(2) x 5 windows x 2 SPEI versions
* =============================================================================
di "========================================================"
di "2. Spec(2) comparison: v1-SPEI vs v2-SPEI"
di "========================================================"

tempname pf
postfile `pf' str10 window str10 spei_ver ///
	b_SRD se_SRD p_SRD ///
	b_SRH se_SRH p_SRH ///
	b_DH se_DH p_DH ///
	b_SRDH se_SRDH p_SRDH ///
	N r2 ///
	using "$outdir/v2_spei_comparison_spec2.dta", replace

foreach wsfx in "" "_v3pm10" "_hepm10" "_v3he" "_hema" {
	local wlbl = cond("`wsfx'" == "", "full", substr("`wsfx'", 2, .))
	local wlbl2 = cond("`wsfx'" == "", "_full", "`wsfx'")
	local h_var = cond("`wsfx'" == "", "hdd_ge32", "hdd_ge32`wsfx'")
	local ctrl_mac = cond("`wsfx'" == "", "CTRL_full", "CTRL`wsfx'")

	* === v2-SPEI (current: window-specific D) ===
	qui reghdfe ln_yield D`wlbl2' W`wlbl2' `h_var' ca ///
		SR_x_D`wlbl2' SR_x_W`wlbl2' SR_x_Heat`wlbl2' ///
		D_x_Heat`wlbl2' SR_x_D_x_Heat`wlbl2' ///
		$`ctrl_mac' if main_sample == 1, ///
		absorb(grid_id year) vce(cluster grid_id)

	post `pf' ("`wlbl'") ("v2") ///
		(_b[SR_x_D`wlbl2']) (_se[SR_x_D`wlbl2']) ///
		(2*ttail(e(df_r), abs(_b[SR_x_D`wlbl2']/_se[SR_x_D`wlbl2']))) ///
		(_b[SR_x_Heat`wlbl2']) (_se[SR_x_Heat`wlbl2']) ///
		(2*ttail(e(df_r), abs(_b[SR_x_Heat`wlbl2']/_se[SR_x_Heat`wlbl2']))) ///
		(_b[D_x_Heat`wlbl2']) (_se[D_x_Heat`wlbl2']) ///
		(2*ttail(e(df_r), abs(_b[D_x_Heat`wlbl2']/_se[D_x_Heat`wlbl2']))) ///
		(_b[SR_x_D_x_Heat`wlbl2']) (_se[SR_x_D_x_Heat`wlbl2']) ///
		(2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat`wlbl2']/_se[SR_x_D_x_Heat`wlbl2']))) ///
		(e(N)) (e(r2))

	* === v1-SPEI (all windows use D_full) ===
	if "`wsfx'" == "" {
		* Full season: identical to v2 — post same results
		post `pf' ("`wlbl'") ("v1") ///
			(_b[SR_x_D_full]) (_se[SR_x_D_full]) ///
			(2*ttail(e(df_r), abs(_b[SR_x_D_full]/_se[SR_x_D_full]))) ///
			(_b[SR_x_Heat_full]) (_se[SR_x_Heat_full]) ///
			(2*ttail(e(df_r), abs(_b[SR_x_Heat_full]/_se[SR_x_Heat_full]))) ///
			(_b[D_x_Heat_full]) (_se[D_x_Heat_full]) ///
			(2*ttail(e(df_r), abs(_b[D_x_Heat_full]/_se[D_x_Heat_full]))) ///
			(_b[SR_x_D_x_Heat_full]) (_se[SR_x_D_x_Heat_full]) ///
			(2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat_full]/_se[SR_x_D_x_Heat_full]))) ///
			(e(N)) (e(r2))
	}
	else {
		* Sub-window: use D_full/W_full + window-specific H
		qui reghdfe ln_yield D_full W_full `h_var' ca ///
			SR_x_D_v1`wsfx' SR_x_W_v1`wsfx' SR_x_Heat`wlbl2' ///
			D_x_Heat_v1`wsfx' SR_x_D_x_Heat_v1`wsfx' ///
			$`ctrl_mac' if main_sample == 1, ///
			absorb(grid_id year) vce(cluster grid_id)

		post `pf' ("`wlbl'") ("v1") ///
			(_b[SR_x_D_v1`wsfx']) (_se[SR_x_D_v1`wsfx']) ///
			(2*ttail(e(df_r), abs(_b[SR_x_D_v1`wsfx']/_se[SR_x_D_v1`wsfx']))) ///
			(_b[SR_x_Heat`wlbl2']) (_se[SR_x_Heat`wlbl2']) ///
			(2*ttail(e(df_r), abs(_b[SR_x_Heat`wlbl2']/_se[SR_x_Heat`wlbl2']))) ///
			(_b[D_x_Heat_v1`wsfx']) (_se[D_x_Heat_v1`wsfx']) ///
			(2*ttail(e(df_r), abs(_b[D_x_Heat_v1`wsfx']/_se[D_x_Heat_v1`wsfx']))) ///
			(_b[SR_x_D_x_Heat_v1`wsfx']) (_se[SR_x_D_x_Heat_v1`wsfx']) ///
			(2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat_v1`wsfx']/_se[SR_x_D_x_Heat_v1`wsfx']))) ///
			(e(N)) (e(r2))
	}

	di "`wlbl': done"
}

postclose `pf'

preserve
use "$outdir/v2_spei_comparison_spec2.dta", clear
list, sep(2) noobs
export delimited using "$outdir/v2_spei_comparison_spec2.csv", replace
restore

* =============================================================================
* 3. EXTENDED: Spec(1) + Spec(3) for attenuation comparison
*    v1-SPEI vs v2-SPEI, 3 SM sources, key windows
* =============================================================================
di "========================================================"
di "3. Attenuation comparison: v1-SPEI vs v2-SPEI"
di "========================================================"

tempname pf2
postfile `pf2' str10 window str10 spei_ver str10 sm_src ///
	b_SRD_s1 se_SRD_s1 p_SRD_s1 ///
	b_SRD_s3 se_SRD_s3 p_SRD_s3 ///
	attn_SRD N ///
	using "$outdir/v2_spei_comparison_attenuation.dta", replace

foreach wsfx in "" "_v3he" "_hepm10" "_hema" {
	local wlbl = cond("`wsfx'" == "", "full", substr("`wsfx'", 2, .))
	local wlbl2 = cond("`wsfx'" == "", "_full", "`wsfx'")
	local h_var = cond("`wsfx'" == "", "hdd_ge32", "hdd_ge32`wsfx'")
	local ctrl_mac = cond("`wsfx'" == "", "CTRL_full", "CTRL`wsfx'")

	foreach ver in v1 v2 {

		* Determine D/W/interaction variable names
		if "`ver'" == "v2" | "`wsfx'" == "" {
			local d_var "D`wlbl2'"
			local w_var "W`wlbl2'"
			local srd_var "SR_x_D`wlbl2'"
			local srw_var "SR_x_W`wlbl2'"
		}
		else {
			local d_var "D_full"
			local w_var "W_full"
			local srd_var "SR_x_D_v1`wsfx'"
			local srw_var "SR_x_W_v1`wsfx'"
		}

		* --- Spec(1) ---
		qui reghdfe ln_yield `d_var' `w_var' `h_var' ca ///
			`srd_var' `srw_var' SR_x_Heat`wlbl2' ///
			$`ctrl_mac' if main_sample == 1, ///
			absorb(grid_id year) vce(cluster grid_id)

		local b1 = _b[`srd_var']
		local se1 = _se[`srd_var']
		local p1 = 2*ttail(e(df_r), abs(`b1'/`se1'))

		* --- Spec(3) for each SM source ---
		foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
			local slbl = cond("`src'" == "gleam_smrz", "gleam", ///
						 cond("`src'" == "swsm_l3", "swsm", "era5l"))
			local smvar = cond("`src'" == "gleam_smrz", "gsm", ///
						  cond("`src'" == "swsm_l3", "ssm", "esm"))

			* SM interaction D variable depends on version
			if "`ver'" == "v2" | "`wsfx'" == "" {
				local smxd "`smvar'_x_D`wlbl2'"
			}
			else {
				local smxd "`smvar'_x_Dv1`wsfx'"
			}

			qui reghdfe ln_yield `d_var' `w_var' `h_var' ca ///
				`srd_var' `srw_var' SR_x_Heat`wlbl2' ///
				`src'_mean`wsfx' `smxd' `smvar'_x_H`wlbl2' `smvar'_x_SR`wlbl2' ///
				$`ctrl_mac' if main_sample == 1, ///
				absorb(grid_id year) vce(cluster grid_id)

			local b3 = _b[`srd_var']
			local se3 = _se[`srd_var']
			local p3 = 2*ttail(e(df_r), abs(`b3'/`se3'))
			local att = cond(`b1' != 0, 100*(1 - `b3'/`b1'), .)

			post `pf2' ("`wlbl'") ("`ver'") ("`slbl'") ///
				(`b1') (`se1') (`p1') ///
				(`b3') (`se3') (`p3') ///
				(`att') (e(N))

			di "`wlbl' `ver' `slbl': attn=" %5.1f `att' "% (s1=" %7.4f `b1' " s3=" %7.4f `b3' ")"
		}
	}
}

postclose `pf2'

preserve
use "$outdir/v2_spei_comparison_attenuation.dta", clear
list, sep(6) noobs
export delimited using "$outdir/v2_spei_comparison_attenuation.csv", replace
restore

* =============================================================================
* 4. Spec(4) comparison for key windows: v1-SPEI vs v2-SPEI x 3SM
* =============================================================================
di "========================================================"
di "4. Spec(4) comparison: v1-SPEI vs v2-SPEI"
di "========================================================"

tempname pf3
postfile `pf3' str10 window str10 spei_ver str10 sm_src ///
	b_SRD se_SRD p_SRD ///
	b_SRDH se_SRDH p_SRDH ///
	b_SMSRDH se_SMSRDH p_SMSRDH ///
	N r2 ///
	using "$outdir/v2_spei_comparison_spec4.dta", replace

foreach wsfx in "" "_v3he" "_hepm10" {
	local wlbl = cond("`wsfx'" == "", "full", substr("`wsfx'", 2, .))
	local wlbl2 = cond("`wsfx'" == "", "_full", "`wsfx'")
	local h_var = cond("`wsfx'" == "", "hdd_ge32", "hdd_ge32`wsfx'")
	local ctrl_mac = cond("`wsfx'" == "", "CTRL_full", "CTRL`wsfx'")

	foreach ver in v1 v2 {
		* Determine variable names based on version
		if "`ver'" == "v2" | "`wsfx'" == "" {
			local d_var "D`wlbl2'"
			local w_var "W`wlbl2'"
			local srd "SR_x_D`wlbl2'"
			local srw "SR_x_W`wlbl2'"
			local dxh "D_x_Heat`wlbl2'"
			local srdxh "SR_x_D_x_Heat`wlbl2'"
		}
		else {
			local d_var "D_full"
			local w_var "W_full"
			local srd "SR_x_D_v1`wsfx'"
			local srw "SR_x_W_v1`wsfx'"
			local dxh "D_x_Heat_v1`wsfx'"
			local srdxh "SR_x_D_x_Heat_v1`wsfx'"
		}

		foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
			local slbl = cond("`src'" == "gleam_smrz", "gleam", ///
						 cond("`src'" == "swsm_l3", "swsm", "era5l"))
			local smvar = cond("`src'" == "gleam_smrz", "gsm", ///
						  cond("`src'" == "swsm_l3", "ssm", "esm"))

			* SM-D and SM-DH interactions depend on version
			if "`ver'" == "v2" | "`wsfx'" == "" {
				local smxd "`smvar'_x_D`wlbl2'"
				local smxdh "`smvar'_x_DH`wlbl2'"
				local smxsrdh "`smvar'_x_SRDH`wlbl2'"
			}
			else {
				local smxd "`smvar'_x_Dv1`wsfx'"
				local smxdh "`smvar'_x_DHv1`wsfx'"
				local smxsrdh "`smvar'_x_SRDHv1`wsfx'"
			}

			qui reghdfe ln_yield `d_var' `w_var' `h_var' ca ///
				`srd' `srw' SR_x_Heat`wlbl2' ///
				`dxh' `srdxh' ///
				`src'_mean`wsfx' `smxd' `smvar'_x_H`wlbl2' `smvar'_x_SR`wlbl2' ///
				`smxdh' `smxsrdh' ///
				$`ctrl_mac' if main_sample == 1, ///
				absorb(grid_id year) vce(cluster grid_id)

			post `pf3' ("`wlbl'") ("`ver'") ("`slbl'") ///
				(_b[`srd']) (_se[`srd']) ///
				(2*ttail(e(df_r), abs(_b[`srd']/_se[`srd']))) ///
				(_b[`srdxh']) (_se[`srdxh']) ///
				(2*ttail(e(df_r), abs(_b[`srdxh']/_se[`srdxh']))) ///
				(_b[`smxsrdh']) (_se[`smxsrdh']) ///
				(2*ttail(e(df_r), abs(_b[`smxsrdh']/_se[`smxsrdh']))) ///
				(e(N)) (e(r2))

			di "`wlbl' `ver' `slbl': SR×D=" %7.4f _b[`srd'] ///
			   " SR×D×H=" %7.4f _b[`srdxh']
		}
	}
}

postclose `pf3'

preserve
use "$outdir/v2_spei_comparison_spec4.dta", clear
list, sep(6) noobs
export delimited using "$outdir/v2_spei_comparison_spec4.csv", replace
restore

* =============================================================================
* 5. Focused horse-race comparison: v1-SPEI vs v2-SPEI
* =============================================================================
di "========================================================"
di "5. Horse-race: v1-SPEI (Scheme B focused)"
di "========================================================"

eststo clear

* v1-SPEI horse-race: v3he + hema, using D_full for both
eststo hr_v1: reghdfe ln_yield D_full W_full hdd_ge32_v3he hdd_ge32_hema ca ///
	SR_x_D_v1_v3he SR_x_Heat_v3he SR_x_D_x_Heat_v1_v3he ///
	SR_x_D_v1_hema SR_x_Heat_hema SR_x_D_x_Heat_v1_hema ///
	$CTRL_full if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)

* v2-SPEI horse-race: same as existing Step 2 Part D SchB-Focused
eststo hr_v2: reghdfe ln_yield D_full W_full hdd_ge32_v3he hdd_ge32_hema ca ///
	SR_x_D_v3he SR_x_Heat_v3he SR_x_D_x_Heat_v3he ///
	SR_x_D_hema SR_x_Heat_hema SR_x_D_x_Heat_hema ///
	$CTRL_full if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)

esttab hr_v1 hr_v2 using "$outdir/v2_spei_comparison_horserace.csv", replace ///
	cells(b(star fmt(4)) se(par fmt(4))) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	stats(r2 N, labels("R-squared" "N") fmt(4 0)) ///
	mtitles("v1-SPEI" "v2-SPEI") ///
	title("Horse-Race: v1-SPEI vs v2-SPEI (Scheme B Focused)") ///
	note("FE: grid+year. Cluster: grid_id. D_full used as base drought.")

* =============================================================================
* SUMMARY
* =============================================================================
di "========================================================"
di "SUMMARY: v1-SPEI vs v2-SPEI"
di "========================================================"

preserve
use "$outdir/v2_spei_comparison_spec2.dta", clear
di "=== Spec(2) ==="
list, sep(2) noobs
restore

log close
di "=== v2_spei_comparison.do COMPLETE ==="
