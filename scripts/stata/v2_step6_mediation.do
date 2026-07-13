* =============================================================================
* v2_step6_mediation.do
* Purpose: Formal mediation analysis — Baron-Kenny + bootstrap.
*          3 SM sources x key windows (full, v3he, hepm10, hema).
*          NOTE: Language discipline — "channel-consistent conditional
*          association", NOT causal mediation language.
* Author:  YangSu + Claude
* Date:    2026-04-02
* Input:   data/processed/v2_analysis_ready.dta
* Output:  output/tables/v2_step6_mediation.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global outdata  "$projdir/data/processed"
global outdir   "$projdir/output/tables"
global logdir   "$projdir/output/logs"

log using "$logdir/v2_step6_mediation_20260402.log", replace

use "$outdata/v2_analysis_ready.dta", clear
xtset grid_id year

* Controls
global CTRL_full    irr_frac pr_sum et0_sum aridity gdd_ge10
global CTRL_v3he    irr_frac pr_sum_v3he et0_sum_v3he aridity gdd_ge10_v3he
global CTRL_hepm10  irr_frac pr_sum_hepm10 et0_sum_hepm10 aridity gdd_ge10_hepm10
global CTRL_hema    irr_frac pr_sum_hema et0_sum_hema aridity gdd_ge10_hema

* =============================================================================
* Key windows for mediation: full, v3he, hepm10, hema
* SM sources: gleam_smrz, swsm_l3, era5l_swvl3
* =============================================================================

* Results postfile
tempname pf
postfile `pf' str10 window str10 sm_src ///
	b_total se_total p_total ///
	b_a se_a p_a ///
	b_b se_b p_b ///
	b_direct se_direct p_direct ///
	b_indirect se_indirect ///
	pct_mediated N ///
	using "$outdir/v2_step6_mediation.dta", replace

* =============================================================================
* Loop over windows and SM sources
* =============================================================================
foreach wsfx in "" "_v3he" "_hepm10" "_hema" {
	local wlbl = cond("`wsfx'" == "", "full", substr("`wsfx'", 2, .))
	local wlbl2 = cond("`wsfx'" == "", "_full", "`wsfx'")
	local h_var = cond("`wsfx'" == "", "hdd_ge32", "hdd_ge32`wsfx'")
	local ctrl "CTRL`wlbl2'"

	di _n "========================================================"
	di "WINDOW: `wlbl'"
	di "========================================================"

	foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
		local slbl = cond("`src'" == "gleam_smrz", "gleam", ///
					 cond("`src'" == "swsm_l3", "swsm", "era5l"))
		local smvar = cond("`src'" == "gleam_smrz", "gsm", ///
					  cond("`src'" == "swsm_l3", "ssm", "esm"))

		di _n "--- `wlbl' x `slbl' ---"

		* ============================================================
		* Step 1: Total effect (Y on D, no SM)
		* ============================================================
		qui reghdfe ln_yield D`wlbl2' W`wlbl2' `h_var' ca ///
			SR_x_D`wlbl2' SR_x_W`wlbl2' SR_x_Heat`wlbl2' ///
			$`ctrl' if main_sample == 1, ///
			absorb(grid_id year) vce(cluster grid_id)

		local b_total = _b[D`wlbl2']
		local se_total = _se[D`wlbl2']
		local p_total = 2*ttail(e(df_r), abs(`b_total'/`se_total'))
		local N_obs = e(N)
		di "Total effect of D: " %7.4f `b_total' " (SE=" %7.4f `se_total' ")"

		* ============================================================
		* Step 2: a-path (SM on D)
		* ============================================================
		qui reghdfe `src'_mean`wsfx' ///
			D`wlbl2' W`wlbl2' `h_var' ca ///
			SR_x_D`wlbl2' SR_x_Heat`wlbl2' ///
			$`ctrl' if main_sample == 1, ///
			absorb(grid_id year) vce(cluster grid_id)

		local b_a = _b[D`wlbl2']
		local se_a = _se[D`wlbl2']
		local p_a = 2*ttail(e(df_r), abs(`b_a'/`se_a'))
		di "a-path (D -> SM): " %7.4f `b_a' " (SE=" %7.4f `se_a' ")"

		* ============================================================
		* Step 3: b-path + direct effect (Y on D + SM)
		* ============================================================
		qui reghdfe ln_yield D`wlbl2' W`wlbl2' `h_var' ca ///
			SR_x_D`wlbl2' SR_x_W`wlbl2' SR_x_Heat`wlbl2' ///
			`src'_mean`wsfx' `smvar'_x_D`wlbl2' `smvar'_x_H`wlbl2' `smvar'_x_SR`wlbl2' ///
			$`ctrl' if main_sample == 1, ///
			absorb(grid_id year) vce(cluster grid_id)

		local b_b = _b[`src'_mean`wsfx']
		local se_b = _se[`src'_mean`wsfx']
		local p_b = 2*ttail(e(df_r), abs(`b_b'/`se_b'))
		local b_direct = _b[D`wlbl2']
		local se_direct = _se[D`wlbl2']
		local p_direct = 2*ttail(e(df_r), abs(`b_direct'/`se_direct'))
		di "b-path (SM -> Y): " %7.4f `b_b' " (SE=" %7.4f `se_b' ")"
		di "Direct effect of D: " %7.4f `b_direct' " (SE=" %7.4f `se_direct' ")"

		* ============================================================
		* Step 4: Indirect effect = a * b (Sobel approximation)
		* ============================================================
		local b_indirect = `b_a' * `b_b'
		local se_indirect = sqrt((`b_a')^2 * (`se_b')^2 + (`b_b')^2 * (`se_a')^2)
		local pct_med = cond(`b_total' != 0, 100 * `b_indirect' / `b_total', .)

		di "Indirect (a*b): " %7.4f `b_indirect' " (SE=" %7.4f `se_indirect' ")"
		di "Pct mediated: " %5.1f `pct_med' "%"

		post `pf' ("`wlbl'") ("`slbl'") ///
			(`b_total') (`se_total') (`p_total') ///
			(`b_a') (`se_a') (`p_a') ///
			(`b_b') (`se_b') (`p_b') ///
			(`b_direct') (`se_direct') (`p_direct') ///
			(`b_indirect') (`se_indirect') ///
			(`pct_med') (`N_obs')
	}
}

postclose `pf'

* =============================================================================
* Export mediation summary
* =============================================================================
preserve
use "$outdir/v2_step6_mediation.dta", clear
format b_* se_* %9.4f
format p_* %7.4f
format pct_mediated %5.1f
list, sep(3) noobs
export delimited using "$outdir/v2_step6_mediation.csv", replace
restore

* =============================================================================
* PART B: Bootstrap mediation for key window-SM combinations
*   Focus on full x ERA5L (lowest endogeneity) and v3he x ERA5L
*   NOTE: Must xtset,clear before bootstrap (panel + resample conflict)
* =============================================================================
di "========================================================"
di "PART B: Bootstrap mediation — ERA5-Land"
di "========================================================"

* Keep only main sample for bootstrap efficiency
keep if main_sample == 1

* Need to clear panel setting for bootstrap
xtset, clear

* --- Bootstrap program ---
cap program drop med_boot
program define med_boot, rclass
	syntax, window(string) src(string) smvar(string) ctrl(string)

	local wlbl2 = cond("`window'" == "full", "_full", "_`window'")
	local wsfx = cond("`window'" == "full", "", "_`window'")
	local h_var = cond("`window'" == "full", "hdd_ge32", "hdd_ge32`wsfx'")

	* a-path
	qui reghdfe `src'_mean`wsfx' ///
		D`wlbl2' W`wlbl2' `h_var' ca ///
		SR_x_D`wlbl2' SR_x_Heat`wlbl2' ///
		`ctrl', ///
		absorb(grid_id year) vce(cluster grid_id)
	local a = _b[D`wlbl2']

	* b-path
	qui reghdfe ln_yield D`wlbl2' W`wlbl2' `h_var' ca ///
		SR_x_D`wlbl2' SR_x_W`wlbl2' SR_x_Heat`wlbl2' ///
		`src'_mean`wsfx' `smvar'_x_D`wlbl2' `smvar'_x_H`wlbl2' `smvar'_x_SR`wlbl2' ///
		`ctrl', ///
		absorb(grid_id year) vce(cluster grid_id)
	local b = _b[`src'_mean`wsfx']

	return scalar indirect = `a' * `b'
	return scalar a_path = `a'
	return scalar b_path = `b'
end

* --- Bootstrap for full x ERA5L ---
di "Bootstrap: full x ERA5L (500 reps)"
bootstrap indirect=r(indirect) a_path=r(a_path) b_path=r(b_path), ///
	reps(500) seed(42) cluster(grid_id) nodots: ///
	med_boot, window(full) src(era5l_swvl3) smvar(esm) ///
	ctrl(irr_frac pr_sum et0_sum aridity gdd_ge10)
estat bootstrap, bc

* --- Bootstrap for v3he x ERA5L ---
di "Bootstrap: v3he x ERA5L (500 reps)"
bootstrap indirect=r(indirect) a_path=r(a_path) b_path=r(b_path), ///
	reps(500) seed(42) cluster(grid_id) nodots: ///
	med_boot, window(v3he) src(era5l_swvl3) smvar(esm) ///
	ctrl(irr_frac pr_sum_v3he et0_sum_v3he aridity gdd_ge10_v3he)
estat bootstrap, bc

* =============================================================================
* PART C: Moderated mediation — conditional indirect at SR=0 vs SR=1
*   The a-path includes SR×D → SM, so indirect effect differs by SR level
* =============================================================================
di "========================================================"
di "PART C: Moderated mediation — conditional indirect effect"
di "========================================================"

* Re-set panel
xtset grid_id year

foreach wsfx in "" "_v3he" {
	local wlbl = cond("`wsfx'" == "", "full", "v3he")
	local wlbl2 = cond("`wsfx'" == "", "_full", "`wsfx'")
	local h_var = cond("`wsfx'" == "", "hdd_ge32", "hdd_ge32`wsfx'")
	local ctrl = cond("`wsfx'" == "", "CTRL_full", "CTRL_v3he")

	di _n "--- `wlbl': Conditional indirect at SR=0 vs SR=1 ---"

	foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
		local slbl = cond("`src'" == "gleam_smrz", "gleam", ///
					 cond("`src'" == "swsm_l3", "swsm", "era5l"))
		local smvar = cond("`src'" == "gleam_smrz", "gsm", ///
					  cond("`src'" == "swsm_l3", "ssm", "esm"))

		* a-path with SR moderation
		qui reghdfe `src'_mean`wsfx' ///
			D`wlbl2' `h_var' ca SR_x_D`wlbl2' SR_x_Heat`wlbl2' ///
			$`ctrl' if main_sample == 1, ///
			absorb(grid_id year) vce(cluster grid_id)

		local a0 = _b[D`wlbl2']
		local a1 = _b[D`wlbl2'] + _b[SR_x_D`wlbl2']

		* b-path
		qui reghdfe ln_yield D`wlbl2' W`wlbl2' `h_var' ca ///
			SR_x_D`wlbl2' SR_x_W`wlbl2' SR_x_Heat`wlbl2' ///
			`src'_mean`wsfx' `smvar'_x_D`wlbl2' `smvar'_x_H`wlbl2' `smvar'_x_SR`wlbl2' ///
			$`ctrl' if main_sample == 1, ///
			absorb(grid_id year) vce(cluster grid_id)

		local b_sm = _b[`src'_mean`wsfx']

		local ind0 = `a0' * `b_sm'
		local ind1 = `a1' * `b_sm'

		di "`wlbl' x `slbl': indirect(SR=0)=" %7.4f `ind0' ///
		   "  indirect(SR=1)=" %7.4f `ind1' ///
		   "  diff=" %7.4f (`ind1' - `ind0')
	}
}

log close
di "=== v2_step6_mediation.do COMPLETE ==="
