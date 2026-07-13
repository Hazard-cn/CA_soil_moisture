* =============================================================================
* step8_joint_stress.do — Joint stress mechanism: SM state-dependence + compound
* Purpose: SM×Heat interaction in yield regression (Type I evidence),
*          compound slope by SM quartile (Type II evidence),
*          state-dependence summary table + gradient figure
* Author: YangSu / Claude Code
* Date: 2026-03-22
* Dependencies: step0_sample_and_macros.do (analysis_main_sample.dta)
* =============================================================================

* --- 0. Setup ---
global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global outdir  "$projdir/output/tables"
global figdir  "$projdir/output/figures"
global logdir  "$projdir/output/logs"

log using "$logdir/step8_joint_stress.log", replace

di "============================================================"
di "step8_joint_stress.do — Joint stress / SM gap"
di "Date: $S_DATE $S_TIME"
di "============================================================"

* --- Load canonical dataset ---
use "$projdir/data/processed/analysis_main_sample.dta", clear

* Verify sample integrity
count if main_sample == 1
local expected_N = 61795
assert r(N) == `expected_N'
di "Sample integrity verified: N = " r(N)

xtset grid_id year

* Restore macros
global CTRL irr_frac pre_sum et0_sum wd_aridity_et0divpre gdd_30
global RHS_COMPOUND D_season W_season hdd_tmax_ge32 ca ///
	SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat $CTRL

* =============================================================================
* PART A: SM × Heat STATE-DEPENDENCE SUMMARY
* Three SM expressions in one summary table (not three isolated results)
* =============================================================================

di _n "============================================================"
di "PART A: SM × Heat state-dependence (3 measures)"
di "============================================================"

* --- A1: Continuous SM × Heat ---
cap drop sm_x_heat_cont
gen sm_x_heat_cont = gleam_smrz_mean * hdd_tmax_ge32
label var sm_x_heat_cont "SM(continuous) × Heat"

eststo clear
eststo sm_cont: reghdfe ln_yield $RHS_COMPOUND sm_x_heat_cont ///
	if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
local b_cont  = _b[sm_x_heat_cont]
local se_cont = _se[sm_x_heat_cont]
local p_cont  = 2 * normal(-abs(`b_cont'/`se_cont'))

di "SM(continuous) × Heat: b=" %8.6f `b_cont' " se=" %8.6f `se_cont' " p=" %6.4f `p_cont'

* --- A2: Binary P25 SM × Heat ---
cap drop sm_x_heat_p25
gen sm_x_heat_p25 = sm_low * hdd_tmax_ge32
label var sm_x_heat_p25 "SM(below P25) × Heat"

eststo sm_p25: reghdfe ln_yield $RHS_COMPOUND sm_x_heat_p25 ///
	if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
local b_p25  = _b[sm_x_heat_p25]
local se_p25 = _se[sm_x_heat_p25]
local p_p25  = 2 * normal(-abs(`b_p25'/`se_p25'))

di "SM(P25 binary) × Heat: b=" %8.6f `b_p25' " se=" %8.6f `se_p25' " p=" %6.4f `p_p25'

* --- A3: Quartile-specific heat slopes ---
* Interact heat with SM quartile dummies
cap drop heat_smq1 heat_smq2 heat_smq3 heat_smq4
forvalues q = 1/4 {
	gen heat_smq`q' = hdd_tmax_ge32 * (sm_quartile == `q') if main_sample == 1
	label var heat_smq`q' "Heat × SM Q`q'"
}

eststo sm_qslope: reghdfe ln_yield D_season W_season ca ///
	SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat ///
	heat_smq1 heat_smq2 heat_smq3 heat_smq4 ///
	i.sm_quartile $CTRL if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)

* Extract quartile-specific heat slopes
local b_q1  = _b[heat_smq1]
local se_q1 = _se[heat_smq1]
local b_q4  = _b[heat_smq4]
local se_q4 = _se[heat_smq4]
local p_q1  = 2 * normal(-abs(`b_q1'/`se_q1'))
local p_q4  = 2 * normal(-abs(`b_q4'/`se_q4'))

di "Heat slope in SM Q1 (driest): b=" %8.6f `b_q1' " se=" %8.6f `se_q1' " p=" %6.4f `p_q1'
di "Heat slope in SM Q4 (wettest): b=" %8.6f `b_q4' " se=" %8.6f `se_q4' " p=" %6.4f `p_q4'

* --- Export state-dependence summary ---
esttab sm_cont sm_p25 sm_qslope using "$outdir/step8_sm_heat_state_dependence.csv", ///
	replace cells(b(fmt(6)) se(par fmt(6)) p(fmt(4))) ///
	keep(sm_x_heat_cont sm_x_heat_p25 heat_smq1 heat_smq2 heat_smq3 heat_smq4 ///
		SR_x_D_x_Heat SR_x_D SR_x_Heat D_x_Heat) ///
	stats(N r2, labels("N" "R²") fmt(%9.0fc %6.4f)) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	mtitles("Continuous" "Binary P25" "Q-slope") ///
	title("SM × Heat State-Dependence Summary")

* Also export compact CSV for report
* Determine direction labels first
local dir_cont = cond(`b_cont' < 0, "Negative", "Positive")
local dir_p25  = cond(`b_p25' < 0, "Negative", "Positive")

tempname fh
file open `fh' using "$outdir/step8_sm_summary_compact.csv", write replace
file write `fh' "sm_measure,coef,se,pvalue,direction" _n
file write `fh' "Continuous," %8.6f (`b_cont') "," %8.6f (`se_cont') ///
	"," %6.4f (`p_cont') ",`dir_cont'" _n
file write `fh' "Binary_P25," %8.6f (`b_p25') "," %8.6f (`se_p25') ///
	"," %6.4f (`p_p25') ",`dir_p25'" _n
file write `fh' "Q1_slope," %8.6f (`b_q1') "," %8.6f (`se_q1') ///
	"," %6.4f (`p_q1') ",Q1(driest)" _n
file write `fh' "Q4_slope," %8.6f (`b_q4') "," %8.6f (`se_q4') ///
	"," %6.4f (`p_q4') ",Q4(wettest)" _n
file close `fh'

* =============================================================================
* PART B: COMPOUND SLOPE BY SM QUARTILE
* SR×D×H coefficient in each SM quartile subsample
* =============================================================================

di _n "============================================================"
di "PART B: Compound slope by SM quartile"
di "============================================================"

eststo clear

* Store results for gradient figure
tempname fh3
file open `fh3' using "$outdir/step8_compound_by_sm.csv", write replace
file write `fh3' "sm_quartile,b_triple,se_triple,p_triple,b_heat,se_heat,N" _n

forvalues q = 1/4 {
	di _n "--- SM Quartile `q' ---"
	count if sm_quartile == `q' & main_sample == 1
	local nq = r(N)

	eststo comp_smq`q': reghdfe ln_yield $RHS_COMPOUND ///
		if sm_quartile == `q' & main_sample == 1, ///
		absorb(grid_id year) vce(cluster grid_id)

	local b_t`q'  = _b[SR_x_D_x_Heat]
	local se_t`q' = _se[SR_x_D_x_Heat]
	local p_t`q'  = 2 * normal(-abs(`b_t`q''/`se_t`q''))
	local b_h`q'  = _b[hdd_tmax_ge32]
	local se_h`q' = _se[hdd_tmax_ge32]

	di "SR×D×H: b=" %8.6f `b_t`q'' " se=" %8.6f `se_t`q'' " p=" %6.4f `p_t`q''
	di "Heat main: b=" %8.6f `b_h`q'' " se=" %8.6f `se_h`q''

	file write `fh3' "`q'," %8.6f (`b_t`q'') "," %8.6f (`se_t`q'') ///
		"," %6.4f (`p_t`q'') "," %8.6f (`b_h`q'') "," %8.6f (`se_h`q'') ///
		"," (`nq') _n
}

file close `fh3'

esttab comp_smq1 comp_smq2 comp_smq3 comp_smq4 ///
	using "$outdir/step8_compound_by_sm_full.csv", ///
	replace cells(b(fmt(6)) se(par fmt(6)) p(fmt(4))) ///
	keep(SR_x_D_x_Heat SR_x_D SR_x_Heat D_x_Heat hdd_tmax_ge32 D_season) ///
	stats(N r2, labels("N" "R²") fmt(%9.0fc %6.4f)) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	mtitles("Q1(Driest)" "Q2" "Q3" "Q4(Wettest)") ///
	title("Compound model by SM quartile")

* =============================================================================
* PART C: SM QUARTILE HEAT GRADIENT FIGURE
* Heat damage slope (hdd_tmax_ge32 coefficient) by SM quartile
* =============================================================================

di _n "============================================================"
di "PART C: SM quartile heat gradient figure"
di "============================================================"

* Extract heat coefficients from quartile models for plotting
* Use coefplot if available, otherwise manual Stata graph
cap which coefplot
if _rc == 0 {
	coefplot (comp_smq1, label("Q1 Driest")) ///
		(comp_smq2, label("Q2")) ///
		(comp_smq3, label("Q3")) ///
		(comp_smq4, label("Q4 Wettest")), ///
		keep(hdd_tmax_ge32) ///
		xline(0, lcolor(gs10) lpattern(dash)) ///
		title("Heat damage slope by SM quartile") ///
		subtitle("Coefficient on hdd_tmax_ge32 in compound model") ///
		note("Each bar: separate compound model estimated within SM quartile" ///
			"Model: ln_yield ~ D W H ca SR×D SR×W SR×H D×H SR×D×H + controls" ///
			"FE: grid + year; Cluster: grid_id") ///
		graphregion(color(white)) plotregion(color(white)) ///
		ciopts(recast(rcap))
	graph export "$figdir/step8_sm_heat_gradient.png", replace width(3600)
}
else {
	* Manual graph from stored coefficients
	preserve
	clear
	set obs 4
	gen sm_q = _n
	gen b_heat = .
	gen se_heat = .

	forvalues q = 1/4 {
		replace b_heat = `b_h`q'' in `q'
		replace se_heat = `se_h`q'' in `q'
	}

	gen ci_lo = b_heat - 1.96 * se_heat
	gen ci_hi = b_heat + 1.96 * se_heat

	label define smq_lbl 1 "Q1(Driest)" 2 "Q2" 3 "Q3" 4 "Q4(Wettest)"
	label values sm_q smq_lbl

	twoway (bar b_heat sm_q, barwidth(0.6) color(navy%60)) ///
		(rcap ci_lo ci_hi sm_q, lcolor(black) lwidth(medthick)), ///
		yline(0, lcolor(gs10) lpattern(dash)) ///
		xlabel(1 "Q1(Driest)" 2 "Q2" 3 "Q3" 4 "Q4(Wettest)") ///
		xtitle("Soil Moisture Quartile") ///
		ytitle("Heat damage slope (coef on HDD≥32°C)") ///
		title("Heat damage by soil moisture state") ///
		subtitle("Within-quartile compound model estimates") ///
		note("Model: ln_yield ~ RHS_COMPOUND, absorb(grid_id year), cluster(grid_id)" ///
			"Bars: coefficient on hdd_tmax_ge32; whiskers: 95% CI") ///
		legend(off) ///
		graphregion(color(white)) plotregion(color(white))
	graph export "$figdir/step8_sm_heat_gradient.png", replace width(3600)
	restore
}

* =============================================================================
* SUMMARY
* =============================================================================

di _n "============================================================"
di "STEP 8 COMPLETE"
di "============================================================"
di "Output files:"
di "  $outdir/step8_sm_heat_state_dependence.csv"
di "  $outdir/step8_sm_summary_compact.csv"
di "  $outdir/step8_compound_by_sm.csv"
di "  $outdir/step8_compound_by_sm_full.csv"
di "  $figdir/step8_sm_heat_gradient.png"
di "============================================================"

log close
