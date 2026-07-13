* =============================================================================
* step2_placebo.do — Step 2: Placebo window diagnostic + lead test
* Purpose: Verify SR buffering is agronomically grounded, not spurious
* Author: YangSu / Claude Code
* Date: 2026-03-12
* Blueprint: Step ED3 (placebo) + identification test
*   2a. Lead test: SR(t+1) × Heat should be insignificant
*   2b. Placebo heat: lag30 heat (pre-season) should show weaker buffering
* =============================================================================

* --- Load preamble ---
global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/00_preamble.do"

* --- Log ---
local today : di %tdCYND date(c(current_date), "DMY")
log using "$logdir/step2_placebo_`today'.log", replace

di "============================================================"
di "Step 2: Placebo Window Diagnostic + Lead Test"
di "Date: `c(current_date)' `c(current_time)'"
di "N = " _N
di "============================================================"

* =============================================================================
* Part A: Lead Test (future SR should not buffer current heat)
* =============================================================================

* Generate lead SR (t+1)
sort grid_id year
by grid_id: gen SR_f1 = ca[_n+1] if year[_n+1] == year + 1
label var SR_f1 "SR lead (t+1)"

* Lead interactions
gen SR_f1_x_D    = SR_f1 * D_season
gen SR_f1_x_Heat = SR_f1 * hdd_tmax_ge32
label var SR_f1_x_D    "SR(t+1) x Drought"
label var SR_f1_x_Heat "SR(t+1) x Heat"

eststo clear

* Main specification (baseline from Step 1)
eststo m_main: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"
estadd local Test "Main"

* + Lead SR level
eststo m_lead1: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat SR_f1 $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"
estadd local Test "+Lead SR"

* + Lead SR × Heat interaction (key placebo)
eststo m_lead2: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat SR_f1 SR_f1_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"
estadd local Test "+Lead SR×Heat"

* + Lead SR × D interaction
eststo m_lead3: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat SR_f1 SR_f1_x_D SR_f1_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"
estadd local Test "+Lead all"

di ""
di "=== Lead Test Results ==="
estimates restore m_lead2
di "SR_f1×Heat (should be NS): " _b[SR_f1_x_Heat] " (SE: " _se[SR_f1_x_Heat] ")"
di "SR×Heat (should remain):   " _b[SR_x_Heat]    " (SE: " _se[SR_x_Heat]    ")"

* =============================================================================
* Part B: Placebo heat window (pre-season heat as placebo)
* =============================================================================

* Use lag30_hdd_32 as placebo heat (pre-tasseling window heat)
* This variable represents HDD from a different (earlier) time window
cap confirm variable lag30_hdd_32
if !_rc {
	rename lag30_hdd_32 Heat_placebo
	label var Heat_placebo "Placebo heat (lag30 HDD >= 32C)"

	gen SR_x_Heat_placebo = ca * Heat_placebo
	label var SR_x_Heat_placebo "SR x Placebo Heat"

	* Placebo specification — keep real Heat + add PlaceboHeat simultaneously
	* Logic: SR buffers real heat (SR×Heat ***) but NOT pre-season heat (SR×PlaceboHeat n.s.)
	eststo m_placebo: reghdfe ln_yield D_season W_season ///
		hdd_tmax_ge32 Heat_placebo ///
		ca SR_x_D SR_x_W SR_x_Heat SR_x_Heat_placebo $CTRL, ///
		absorb(grid_id year) vce(cluster grid_id)
	estadd local FE_grid "Yes"
	estadd local FE_year "Yes"
	estadd local Test "Placebo heat"

	di ""
	di "=== Placebo Heat Results (both Heat vars in model) ==="
	di "SR×Heat (should remain ***):      " _b[SR_x_Heat] ///
		" (SE: " _se[SR_x_Heat] ")"
	di "SR×PlaceboHeat (should be NS):    " _b[SR_x_Heat_placebo] ///
		" (SE: " _se[SR_x_Heat_placebo] ")"
	di "Heat_placebo (direct):            " _b[Heat_placebo] ///
		" (SE: " _se[Heat_placebo] ")"
}
else {
	di "NOTE: lag30_hdd_32 not available, skipping placebo heat test"
}

* --- Export ---
esttab m_main m_lead1 m_lead2 m_lead3 m_placebo ///
	using "$outdir/step2_placebo_lead.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N Test FE_grid FE_year, ///
		labels("R-squared" "Adj. R-squared" "Observations" "Specification" "Grid FE" "Year FE") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	title("Step 2: Placebo Window Diagnostic + Lead Test") ///
	mtitles("Main" "+Lead" "+Lead×H" "+Lead all" "Placebo")

esttab m_main m_lead1 m_lead2 m_lead3 m_placebo ///
	using "$outdir/step2_placebo_lead.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) booktabs ///
	stats(r2 r2_a N Test FE_grid FE_year, ///
		labels("R-squared" "Adj. R-squared" "Observations" "Specification" "Grid FE" "Year FE") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	title("Step 2: Placebo Window Diagnostic + Lead Test") ///
	mtitles("Main" "+Lead" "+Lead×H" "+Lead all" "Placebo")

di ""
di "=== Step 2 complete ==="

log close
