* =============================================================================
* step4_mechanism_annual.do — Step 4: SM mechanism closure + attenuation test
* Purpose: Test whether SR buffering is mediated by soil moisture stabilization
* Author: YangSu / Claude Code
* Date: 2026-03-12
* Blueprint: Eq. (3) / Step ED5
*   Y = c1·D + c2·W + c3·Heat + b1·SM_proxy_dry + b2·SM_proxy_wet
*       + θ0·SR + θ1·SR×D + θ2·SR×W + θ3·SR×Heat + controls + FE + ε
* Diagnostic: Compare θ between Eq.(1) and Eq.(3). Attenuation → mediation.
* =============================================================================

* --- Load preamble ---
global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/00_preamble.do"

* --- Log ---
local today : di %tdCYND date(c(current_date), "DMY")
log using "$logdir/step4_mechanism_annual_`today'.log", replace

di "============================================================"
di "Step 4: SM Mechanism Closure — Attenuation Test"
di "Date: `c(current_date)' `c(current_time)'"
di "N = " _N
di "============================================================"

* =============================================================================
* Part A: SM proxy variable construction
* =============================================================================

* SM mean (root zone GLEAM)
label var gleam_smrz_mean "SM mean (root zone)"

* SM dry stress proxy: days with SM below baseline P10
label var drydays_gleam_smrz_le_basep10 "SM dry days (<=P10)"

* SM surface layer
label var gleam_sms_mean "SM mean (surface)"

* Compound: hot-dry days (heat + low SM simultaneously)
label var hotdrydays_tmax_ge32_smrz_le_bas "Hot-dry days (Tmax>=32 & SM<=P10)"

* Nonlinear SM term
gen SM_mean_sq = gleam_smrz_mean^2
label var SM_mean_sq "SM mean squared"

* SM on hot days (conditional SM when Tmax >= 32)
label var smrz_mean_onhot_ge32 "SM on hot days (Tmax>=32)"

di "SM proxy variables constructed"

* =============================================================================
* Part B: Attenuation test (core diagnostic)
* =============================================================================

eststo clear

* --- B1: Baseline (no SM) — replicates Step 1 full model ---
eststo m_base: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"
estadd local SM_spec "None"

* Store baseline θ for comparison
local theta1_base = _b[SR_x_D]
local theta2_base = _b[SR_x_W]
local theta3_base = _b[SR_x_Heat]

* --- B2: + SM mean ---
eststo m_sm_mean: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	gleam_smrz_mean ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"
estadd local SM_spec "SM mean"

* --- B3: + SM mean + SM dry days (two-tail proxy) ---
eststo m_sm_tails: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	gleam_smrz_mean drydays_gleam_smrz_le_basep10 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"
estadd local SM_spec "SM mean + dry days"

* --- B4: + SM nonlinear (SM + SM²) ---
eststo m_sm_nl: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	gleam_smrz_mean SM_mean_sq ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"
estadd local SM_spec "SM + SM sq"

* --- B5: + SM on hot days (direct mechanism) ---
eststo m_sm_hot: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	smrz_mean_onhot_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"
estadd local SM_spec "SM on hot days"

* --- B6: + hot-dry compound days ---
eststo m_compound: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	hotdrydays_tmax_ge32_smrz_le_bas ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"
estadd local SM_spec "Hot-dry days"

* =============================================================================
* Part C: Attenuation diagnostic
* =============================================================================

di ""
di "============================================================"
di "ATTENUATION DIAGNOSTIC"
di "============================================================"
di ""
di "Baseline θ (no SM controls):"
di "  θ1 (SR×D):    " %9.4f `theta1_base'
di "  θ2 (SR×W):    " %9.4f `theta2_base'
di "  θ3 (SR×Heat): " %9.4f `theta3_base'
di ""

foreach mname in m_sm_mean m_sm_tails m_sm_nl m_sm_hot m_compound {
	estimates restore `mname'
	local t1 = _b[SR_x_D]
	local t2 = _b[SR_x_W]
	local t3 = _b[SR_x_Heat]

	* Attenuation percentage
	local att1 = cond(`theta1_base' != 0, 100 * (1 - `t1'/`theta1_base'), .)
	local att3 = cond(`theta3_base' != 0, 100 * (1 - `t3'/`theta3_base'), .)

	di "Model `mname':"
	di "  θ1 (SR×D):    " %9.4f `t1' "  (attenuation: " %5.1f `att1' "%)"
	di "  θ3 (SR×Heat): " %9.4f `t3' "  (attenuation: " %5.1f `att3' "%)"
	di ""
}

* =============================================================================
* Part D: Export tables
* =============================================================================

esttab m_base m_sm_mean m_sm_tails m_sm_nl m_sm_hot m_compound ///
	using "$outdir/step4_mechanism_annual.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N SM_spec FE_grid FE_year, ///
		labels("R-squared" "Adj. R-squared" "Observations" "SM specification" "Grid FE" "Year FE") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	title("Step 4: SM Mechanism — Attenuation Test") ///
	mtitles("Baseline" "+SM_mean" "+SM_tails" "+SM_NL" "+SM_hot" "+Compound")

esttab m_base m_sm_mean m_sm_tails m_sm_nl m_sm_hot m_compound ///
	using "$outdir/step4_mechanism_annual.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) booktabs ///
	stats(r2 r2_a N SM_spec FE_grid FE_year, ///
		labels("R-squared" "Adj. R-squared" "Observations" "SM specification" "Grid FE" "Year FE") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	title("Step 4: SM Mechanism — Attenuation Test") ///
	mtitles("Baseline" "+SM_mean" "+SM_tails" "+SM_NL" "+SM_hot" "+Compound")

di ""
di "=== Step 4 complete ==="

log close
