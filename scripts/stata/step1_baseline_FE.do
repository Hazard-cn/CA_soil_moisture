* =============================================================================
* step1_baseline_FE.do — Step 1: Baseline FE regression with SR buffering
* Purpose: Estimate SR buffering of yield losses under drought, wetness, heat
* Author: YangSu / Claude Code
* Date: 2026-03-12
* Blueprint: Eq. (1) / Step ED1
*   Y = β1·D + β2·W + β3·Heat + θ0·SR + θ1·SR×D + θ2·SR×W + θ3·SR×Heat
*       + controls + grid_FE + year_FE + ε
* Expected signs: θ1>0 (drought buffering), θ2≤0 (wet boundary), θ3>0 (heat)
* =============================================================================

* --- Load preamble ---
global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/00_preamble.do"

* --- Log ---
local today : di %tdCYND date(c(current_date), "DMY")
log using "$logdir/step1_baseline_FE_`today'.log", replace

di "============================================================"
di "Step 1: Baseline FE — SR Buffering of Extreme Yield Losses"
di "Date: `c(current_date)' `c(current_time)'"
di "N = " _N
di "============================================================"

* =============================================================================
* Part A: Progressive specification (Table 1 — main result)
* =============================================================================

eststo clear

* (1) Extremes only (no SR)
eststo m1: reghdfe ln_yield D_season W_season hdd_tmax_ge32 $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"

* (2) + SR level effect
eststo m2: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"

* (3) + SR × Drought (buffering)
eststo m3: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca SR_x_D $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"

* (4) + SR × Wetness (boundary)
eststo m4: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"

* (5) Full specification: + SR × Heat
eststo m5: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"

* --- Export Table 1 ---
esttab m1 m2 m3 m4 m5 using "$outdir/step1_baseline_FE.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N FE_grid FE_year, ///
		labels("R-squared" "Adj. R-squared" "Observations" "Grid FE" "Year FE") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	title("Step 1: Baseline FE — SR Buffering of Extreme Yield Losses") ///
	mtitles("Extremes" "+SR" "+SR×D" "+SR×W" "Full")

esttab m1 m2 m3 m4 m5 using "$outdir/step1_baseline_FE.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) booktabs ///
	stats(r2 r2_a N FE_grid FE_year, ///
		labels("R-squared" "Adj. R-squared" "Observations" "Grid FE" "Year FE") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	title("Step 1: Baseline FE — SR Buffering of Extreme Yield Losses") ///
	mtitles("Extremes" "+SR" "+SR×D" "+SR×W" "Full")

* --- Report key coefficients from full model ---
di ""
di "=== Key Results from Full Model (m5) ==="
estimates restore m5
di "θ1 (SR×D):    " _b[SR_x_D]    " (SE: " _se[SR_x_D]    ")"
di "θ2 (SR×W):    " _b[SR_x_W]    " (SE: " _se[SR_x_W]    ")"
di "θ3 (SR×Heat): " _b[SR_x_Heat] " (SE: " _se[SR_x_Heat] ")"
di "N = " e(N) ", R2 = " e(r2)

* =============================================================================
* Part B: Heat metric sensitivity (multiple heat indicators)
* =============================================================================

eststo clear
local hcount = 0

foreach hvar in hdd_tmax_ge32 hdd_tmax_ge35 hotdays_tmax_ge32 hotdays_tmax_ge_basep95 {
	local hcount = `hcount' + 1

	* Build interaction
	cap drop sr_x_h_tmp
	gen sr_x_h_tmp = ca * `hvar'

	eststo h`hcount': reghdfe ln_yield D_season W_season `hvar' ///
		ca SR_x_D SR_x_W sr_x_h_tmp $CTRL, ///
		absorb(grid_id year) vce(cluster grid_id)
	estadd local Heat_var "`hvar'"
	estadd local FE_grid "Yes"
	estadd local FE_year "Yes"

	di ""
	di "--- Heat metric: `hvar' ---"
	di "SR×Heat: " _b[sr_x_h_tmp] " (SE: " _se[sr_x_h_tmp] ")"
}

esttab h1 h2 h3 h4 using "$outdir/step1_heat_sensitivity.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N Heat_var FE_grid FE_year, ///
		labels("R-squared" "Adj. R-squared" "Observations" "Heat variable" "Grid FE" "Year FE") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	title("Step 1B: Heat Metric Sensitivity") ///
	mtitles("HDD32" "HDD35" "HotDays32" "HDD_P95")

esttab h1 h2 h3 h4 using "$outdir/step1_heat_sensitivity.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) booktabs ///
	stats(r2 r2_a N Heat_var FE_grid FE_year, ///
		labels("R-squared" "Adj. R-squared" "Observations" "Heat variable" "Grid FE" "Year FE") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	title("Step 1B: Heat Metric Sensitivity") ///
	mtitles("HDD32" "HDD35" "HotDays32" "HDD_P95")

cap drop sr_x_h_tmp

* =============================================================================
* Part C: Prov×year FE robustness + Pure SR total effect
* =============================================================================

di ""
di "============================================================"
di "  Part C: Province×Year FE + Pure SR Total Effect"
di "============================================================"

eststo clear

* (1) Pure SR total effect (no interactions) — grid+year FE
eststo sr_total: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca $CTRL, ///
    absorb(grid_id year) vce(cluster grid_id)
estadd local FE "Grid+Year"

* (2) Full interactions — grid+year FE (same as m5, re-estimated for this table)
eststo sr_full: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
    ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
    absorb(grid_id year) vce(cluster grid_id)
estadd local FE "Grid+Year"

* (3) Full interactions — prov×year FE
eststo sr_prov: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
    ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
    absorb(grid_id prov_year) vce(cluster grid_id)
estadd local FE "Grid+Prov×Year"

esttab sr_total sr_full sr_prov ///
    using "$outdir/step1_FE_robustness.csv", replace ///
    b(%9.4f) se(%9.4f) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(ca SR_x_D SR_x_W SR_x_Heat D_season W_season hdd_tmax_ge32) ///
    stats(r2 N FE, labels("R-squared" "N" "Fixed Effects") fmt(%9.4f %9.0f)) ///
    mtitles("SR Total" "Full(G+Y)" "Full(P×Y)") ///
    title("Table 1C: Total Effect and FE Robustness")

esttab sr_total sr_full sr_prov ///
    using "$outdir/step1_FE_robustness.tex", replace ///
    b(%9.4f) se(%9.4f) booktabs ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(ca SR_x_D SR_x_W SR_x_Heat D_season W_season hdd_tmax_ge32) ///
    stats(r2 N FE, labels("R-squared" "N" "Fixed Effects") fmt(%9.4f %9.0f)) ///
    mtitles("SR Total" "Full(G+Y)" "Full(P×Y)") ///
    title("Total Effect and FE Robustness")

di ""
di "--- Part C Key Results ---"
estimates restore sr_total
di "Pure SR total effect: ca = " %9.4f _b[ca] " (SE=" %9.4f _se[ca] ")"
estimates restore sr_prov
di "Prov×Year FE: SR×D = " %9.4f _b[SR_x_D] " (SE=" %9.4f _se[SR_x_D] ")"
di "  SR×Heat = " %9.4f _b[SR_x_Heat] " (SE=" %9.4f _se[SR_x_Heat] ")"
di "  NOTE: Prov×year FE absorbs province-level climate shocks."
di "  With T=4, limited within-province temporal variation remains."
di "  SR×D weakens but SR×Heat stays robust (more within-province spatial variation in HDD)."

di ""
di "=== Step 1 complete ==="

log close
