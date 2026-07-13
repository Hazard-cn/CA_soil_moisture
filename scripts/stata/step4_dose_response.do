* =============================================================================
* step4_dose_response.do — Dose-Response: SR marginal effect by drought intensity
* Purpose: Full-sample interaction model with drought deciles
* Author: YangSu / Claude Code
* Date: 2026-03-17
* Dependencies: 00_preamble.do, reghdfe, estout
* =============================================================================

* --- Preamble ---
global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/00_preamble.do"

local today : di %tdCYND date(c(current_date), "DMY")
log using "$logdir/step4_dose_response_`today'.log", replace

* --- Mechanism controls (drop et0_sum = bad control, consistent with step2/3) ---
global CTRL_mech "irr_frac pre_sum wd_aridity_et0divpre gdd_30"

di "============================================================"
di "  Dose-Response: SR Marginal Effect by Drought Intensity"
di "============================================================"

* -------------------------------------------------------------------------
* Create drought quintiles (full sample, not subsample)
* -------------------------------------------------------------------------
* D_season = max(0, -SPEI), so D_season > 0 means some drought
* Create 5 bins among drought observations + 1 bin for no drought

gen D_q5 = 0 if D_season == 0
xtile temp_q = D_season if D_season > 0, nq(5)
replace D_q5 = temp_q if temp_q != .
drop temp_q
label define D_q5_lbl 0 "No drought" 1 "Q1 (mild)" 2 "Q2" 3 "Q3" 4 "Q4" 5 "Q5 (severe)"
label values D_q5 D_q5_lbl

tab D_q5, m
bysort D_q5: sum D_season

* -------------------------------------------------------------------------
* Full-sample interaction model: D_q5 × SR
* -------------------------------------------------------------------------
* Use ibn. (no base) to get all coefficients
* Include D_season and hdd as continuous controls

reghdfe ln_yield ibn.D_q5#c.ca ///
    D_season W_season hdd_tmax_ge32 SR_x_W SR_x_Heat $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

* Extract coefficients for each drought quintile
matrix coefs = J(6, 4, .)  // rows: q0-q5; cols: q, coef, se, t
forvalues q = 0/5 {
    local row = `q' + 1
    matrix coefs[`row', 1] = `q'
    matrix coefs[`row', 2] = _b[`q'.D_q5#c.ca]
    matrix coefs[`row', 3] = _se[`q'.D_q5#c.ca]
    matrix coefs[`row', 4] = _b[`q'.D_q5#c.ca] / _se[`q'.D_q5#c.ca]
}

di ""
di "--- SR Marginal Effect by Drought Quintile ---"
di "  Q  |  Coef     |  SE       |  t-stat"
di "-----+-----------+-----------+---------"
forvalues q = 0/5 {
    local row = `q' + 1
    di "  " `q' "  |  " %9.4f coefs[`row',2] "  |  " %9.4f coefs[`row',3] ///
       "  |  " %7.2f coefs[`row',4]
}

* -------------------------------------------------------------------------
* Export coefficient matrix for plotting (CSV)
* -------------------------------------------------------------------------
preserve
clear
svmat coefs, names(col)
rename c1 drought_quintile
rename c2 sr_effect
rename c3 se
rename c4 tstat
gen ci_lo = sr_effect - 1.96 * se
gen ci_hi = sr_effect + 1.96 * se
export delimited using "$outdir/step4_dose_response_coefs.csv", replace
restore

* -------------------------------------------------------------------------
* Create figure using Stata graph
* -------------------------------------------------------------------------
preserve
clear
svmat coefs, names(col)
rename c1 dq
rename c2 coef
rename c3 se
rename c4 tstat
gen ci_lo = coef - 1.96 * se
gen ci_hi = coef + 1.96 * se

twoway (bar coef dq, barwidth(0.6) color(navy%60)) ///
       (rcap ci_lo ci_hi dq, lcolor(black)), ///
    xlabel(0 "No drought" 1 "Q1" 2 "Q2" 3 "Q3" 4 "Q4" 5 "Q5(severe)", ///
           labsize(small)) ///
    ylabel(, format(%9.3f)) ///
    yline(0, lcolor(red) lpattern(dash)) ///
    xtitle("Drought Intensity Quintile") ///
    ytitle("SR Marginal Effect on ln(Yield)") ///
    title("Straw Return Buffering by Drought Intensity") ///
    legend(off) ///
    graphregion(color(white)) plotregion(color(white)) ///
    note("Grid + Year FE. 95% CI shown. N = `=e(N)'")

graph export "$figdir/step4_dose_response.png", replace width(3600)
restore

* -------------------------------------------------------------------------
* Same for heat quintiles
* -------------------------------------------------------------------------
di ""
di "============================================================"
di "  Dose-Response: SR Marginal Effect by Heat Intensity"
di "============================================================"

gen Heat_q5 = 0 if hdd_tmax_ge32 == 0
xtile temp_hq = hdd_tmax_ge32 if hdd_tmax_ge32 > 0, nq(5)
replace Heat_q5 = temp_hq if temp_hq != .
drop temp_hq
label define Heat_q5_lbl 0 "No heat" 1 "Q1 (mild)" 2 "Q2" 3 "Q3" 4 "Q4" 5 "Q5 (severe)"
label values Heat_q5 Heat_q5_lbl

tab Heat_q5, m

reghdfe ln_yield ibn.Heat_q5#c.ca ///
    D_season W_season hdd_tmax_ge32 SR_x_D SR_x_W $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

matrix hcoefs = J(6, 4, .)
forvalues q = 0/5 {
    local row = `q' + 1
    matrix hcoefs[`row', 1] = `q'
    matrix hcoefs[`row', 2] = _b[`q'.Heat_q5#c.ca]
    matrix hcoefs[`row', 3] = _se[`q'.Heat_q5#c.ca]
    matrix hcoefs[`row', 4] = _b[`q'.Heat_q5#c.ca] / _se[`q'.Heat_q5#c.ca]
}

di ""
di "--- SR Marginal Effect by Heat Quintile ---"
di "  Q  |  Coef     |  SE       |  t-stat"
di "-----+-----------+-----------+---------"
forvalues q = 0/5 {
    local row = `q' + 1
    di "  " `q' "  |  " %9.4f hcoefs[`row',2] "  |  " %9.4f hcoefs[`row',3] ///
       "  |  " %7.2f hcoefs[`row',4]
}

* Export heat dose-response
preserve
clear
svmat hcoefs, names(col)
rename c1 heat_quintile
rename c2 sr_effect
rename c3 se
rename c4 tstat
gen ci_lo = sr_effect - 1.96 * se
gen ci_hi = sr_effect + 1.96 * se
export delimited using "$outdir/step4_dose_response_heat_coefs.csv", replace

twoway (bar sr_effect heat_quintile, barwidth(0.6) color(cranberry%60)) ///
       (rcap ci_lo ci_hi heat_quintile, lcolor(black)), ///
    xlabel(0 "No heat" 1 "Q1" 2 "Q2" 3 "Q3" 4 "Q4" 5 "Q5(severe)", ///
           labsize(small)) ///
    ylabel(, format(%9.3f)) ///
    yline(0, lcolor(red) lpattern(dash)) ///
    xtitle("Heat Intensity Quintile (HDD >= 32C)") ///
    ytitle("SR Marginal Effect on ln(Yield)") ///
    title("Straw Return Buffering by Heat Intensity") ///
    legend(off) ///
    graphregion(color(white)) plotregion(color(white)) ///
    note("Grid + Year FE. 95% CI shown.")

graph export "$figdir/step4_dose_response_heat.png", replace width(3600)
restore

di ""
di "============================================================"
di "  Step 4 Complete"
di "============================================================"

log close
