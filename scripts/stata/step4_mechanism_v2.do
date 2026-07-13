* =============================================================================
* step4_mechanism_v2.do — SM Core Mechanism: Three-Chain Evidence Structure
* Purpose: State-variable consistency test for SM as the core mechanism pathway.
*          Chain 1: SM-centered loss function (SM explains yield beyond D/H)
*          Chain 2: SR shifts moisture state (SR -> wetter, fewer hot-dry days)
*          Chain 3: Compound under moisture-state conditioning
*          + County-year aggregation credibility page
*          + Diminishing returns (appendix)
* Author: YangSu / Claude Code
* Date: 2026-03-22
* Dependencies: analysis_main_sample.dta (from step0), reghdfe
* =============================================================================

clear all
set more off
set seed 42

* =============================================================================
* 0. Macros and data (self-contained, no globals from other scripts)
* =============================================================================
global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global outdir  "$projdir/output/tables"
global figdir  "$projdir/output/figures"
global logdir  "$projdir/output/logs"

global CTRL irr_frac pre_sum et0_sum wd_aridity_et0divpre gdd_30
global SOIL_CTRL clay_0_5cm_01deg sand_0_5cm_01deg bdod_0_5cm_01deg ///
	phh2o_0_5cm_01deg silt_0_5cm_01deg

* Full compound model RHS
global RHS_COMPOUND D_season W_season hdd_tmax_ge32 ca ///
	SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat $CTRL

log using "$logdir/step4_mechanism_v2.log", replace

di "============================================================"
di "step4_mechanism_v2.do — SM Core Mechanism (Three-Chain)"
di "Date: $S_DATE $S_TIME"
di "============================================================"

* Load canonical dataset
use "$projdir/data/processed/analysis_main_sample.dta", clear
count if main_sample == 1
local N_main = r(N)
di "Main sample N = `N_main'"

* Clean any leftover temp variables and re-set panel
cap drop __*
xtset grid_id year

* =============================================================================
* 1. Define county_sample (county+year FE effective sample)
* =============================================================================

di ""
di "============================================================"
di "DEFINING COUNTY_SAMPLE (county+year FE)"
di "============================================================"

* Run baseline compound model with county+year FE to define county_sample
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL if main_sample == 1, ///
	absorb(county_id year) vce(cluster county_id)

cap drop county_sample
gen county_sample = e(sample)
label var county_sample "County FE estimation sample"

local N_county = e(N)
di "County sample N = `N_county'"
di "Diff from main_sample: " `N_main' - `N_county'

* =============================================================================
* 2. Mundlak decomposition variables (for Chain 1b)
* =============================================================================

* Surface SM: between (grid time-mean) and within (deviation)
cap drop grid_mean_sms
bysort grid_id: egen grid_mean_sms = mean(gleam_sms_mean) if county_sample == 1
label var grid_mean_sms "Grid time-mean surface SM (between)"

cap drop sms_within
gen sms_within = gleam_sms_mean - grid_mean_sms if county_sample == 1
label var sms_within "Surface SM deviation from grid mean (within)"

* =============================================================================
* 3. Define chain1_common_sample (for R-squared comparison)
* =============================================================================

cap drop chain1_common_sample
gen chain1_common_sample = (county_sample == 1 & ///
	!missing(gleam_sms_mean) & !missing(gleam_smrz_mean) & ///
	!missing(D_season) & !missing(W_season) & !missing(hdd_tmax_ge32))
* Also need SOIL_CTRL non-missing
foreach v of global SOIL_CTRL {
	replace chain1_common_sample = 0 if missing(`v')
}
label var chain1_common_sample "Common sample for Chain 1 R-sq comparison"

count if chain1_common_sample == 1
di "Chain 1 common sample N = " r(N)

* #########################################################################
* CHAIN 1: SM-Centered Loss Function
* #########################################################################

di ""
di "============================================================"
di "CHAIN 1: SM-CENTERED LOSS FUNCTION"
di "============================================================"

* =============================================================================
* Chain 1a: FE Ladder — SM coefficient envelope
* =============================================================================

di ""
di "--- Chain 1a: FE Ladder ---"

eststo clear

* A1: Grid+Year FE (tightest, least SM variation)
eststo A1: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca ///
	SR_x_D SR_x_W SR_x_Heat gleam_sms_mean $CTRL ///
	if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)

* A2: County+Year FE (releases within-county spatial variation)
eststo A2: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca ///
	SR_x_D SR_x_W SR_x_Heat gleam_sms_mean $CTRL ///
	if county_sample == 1, absorb(county_id year) vce(cluster county_id)

* A3: County+Year + Soil controls
eststo A3: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca ///
	SR_x_D SR_x_W SR_x_Heat gleam_sms_mean $CTRL $SOIL_CTRL ///
	if county_sample == 1, absorb(county_id year) vce(cluster county_id)

* A4: County+Year + Soil, rootzone SM (comparison)
eststo A4: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca ///
	SR_x_D SR_x_W SR_x_Heat gleam_smrz_mean $CTRL $SOIL_CTRL ///
	if county_sample == 1, absorb(county_id year) vce(cluster county_id)

* Export FE ladder
esttab A1 A2 A3 A4 using "$outdir/step4v2_chain1_fe_ladder.csv", replace ///
	cells(b(star fmt(6)) se(par fmt(6)) p(fmt(4))) ///
	keep(gleam_sms_mean gleam_smrz_mean) ///
	stats(N r2, labels("N" "R-sq") fmt(0 4)) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	mtitles("Grid+Year" "County+Year" "County+Year+Soil" "County+Year+Soil(smrz)") ///
	title("Chain 1a: SM FE Ladder")

* =============================================================================
* Chain 1b: Mundlak between/within decomposition
* =============================================================================

di ""
di "--- Chain 1b: Mundlak between/within ---"

eststo clear

* A5: Mundlak decomposition under county+year FE
eststo A5: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca ///
	SR_x_D SR_x_W SR_x_Heat grid_mean_sms sms_within $CTRL $SOIL_CTRL ///
	if county_sample == 1, absorb(county_id year) vce(cluster county_id)

esttab A5 using "$outdir/step4v2_chain1_mundlak.csv", replace ///
	cells(b(star fmt(6)) se(par fmt(6)) p(fmt(4))) ///
	keep(grid_mean_sms sms_within) ///
	stats(N r2, labels("N" "R-sq") fmt(0 4)) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	mtitles("County+Year+Soil (Mundlak)") ///
	title("Chain 1b: Mundlak Between/Within Decomposition")

* Report key results
di ""
di "=== MUNDLAK RESULTS ==="
di "Between (grid_mean_sms): b = " _b[grid_mean_sms] ", se = " _se[grid_mean_sms]
local p_between = 2 * ttail(e(df_r), abs(_b[grid_mean_sms] / _se[grid_mean_sms]))
di "  p = " `p_between'
di "Within (sms_within):     b = " _b[sms_within] ", se = " _se[sms_within]
local p_within = 2 * ttail(e(df_r), abs(_b[sms_within] / _se[sms_within]))
di "  p = " `p_within'

if `p_between' < 0.05 & `p_within' >= 0.10 {
	di "CONCLUSION: SM association mainly from spatial comparison (between), "
	di "  not strong temporal identification (within). T=4 limitation."
}
else if `p_between' < 0.05 & `p_within' < 0.10 {
	di "CONCLUSION: Both spatial and temporal variation contribute to SM-yield association."
}
else {
	di "CONCLUSION: Neither between nor within strongly significant — weak SM signal."
}

* =============================================================================
* Chain 1d: Explanatory power comparison (R-squared, common sample)
* =============================================================================

di ""
di "--- Chain 1d: Explanatory power comparison (common sample) ---"

eststo clear

* F0: D/H only (no SM)
eststo F0: reghdfe ln_yield D_season W_season hdd_tmax_ge32 $CTRL $SOIL_CTRL ///
	if chain1_common_sample == 1, absorb(county_id year) vce(cluster county_id)
local r2_F0 = e(r2)

* F1: + SM_surface
eststo F1: reghdfe ln_yield D_season W_season hdd_tmax_ge32 gleam_sms_mean ///
	$CTRL $SOIL_CTRL ///
	if chain1_common_sample == 1, absorb(county_id year) vce(cluster county_id)
local r2_F1 = e(r2)

* F2: + SM_rootzone
eststo F2: reghdfe ln_yield D_season W_season hdd_tmax_ge32 gleam_smrz_mean ///
	$CTRL $SOIL_CTRL ///
	if chain1_common_sample == 1, absorb(county_id year) vce(cluster county_id)
local r2_F2 = e(r2)

di ""
di "=== R-SQUARED COMPARISON (chain1_common_sample) ==="
di "F0 (D/H only):    R2 = " %8.6f `r2_F0'
di "F1 (+SM_surface):  R2 = " %8.6f `r2_F1' "  deltaR2 = " %8.6f (`r2_F1' - `r2_F0')
di "F2 (+SM_rootzone): R2 = " %8.6f `r2_F2' "  deltaR2 = " %8.6f (`r2_F2' - `r2_F0')

esttab F0 F1 F2 using "$outdir/step4v2_chain1_r2_comparison.csv", replace ///
	cells(b(star fmt(6)) se(par fmt(6)) p(fmt(4))) ///
	keep(gleam_sms_mean gleam_smrz_mean D_season W_season hdd_tmax_ge32) ///
	stats(N r2, labels("N" "R-sq") fmt(0 6)) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	mtitles("D/H only" "+SM_surface" "+SM_rootzone") ///
	title("Chain 1d: Explanatory Power Comparison (Common Sample)")

* =============================================================================
* Chain 1 LOYO: Leave-one-year-out diagnostics for key SM coefficient
* =============================================================================

di ""
di "--- Chain 1 LOYO: SM surface coefficient stability ---"

* Store full-sample coefficient from A3
qui reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca ///
	SR_x_D SR_x_W SR_x_Heat gleam_sms_mean $CTRL $SOIL_CTRL ///
	if county_sample == 1, absorb(county_id year) vce(cluster county_id)
local b_full = _b[gleam_sms_mean]
local se_full = _se[gleam_sms_mean]

tempname fh_loyo
file open `fh_loyo' using "$outdir/step4v2_chain1_loyo.csv", write replace
file write `fh_loyo' "drop_year,b_sms,se_sms,p_sms,N" _n
file write `fh_loyo' "full," %10.6f (`b_full') "," %10.6f (`se_full') "," ///
	%6.4f (2*ttail(e(df_r), abs(`b_full'/`se_full'))) "," (e(N)) _n

local loyo_min = `b_full'
local loyo_max = `b_full'

forvalues y = 2016/2019 {
	qui reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca ///
		SR_x_D SR_x_W SR_x_Heat gleam_sms_mean $CTRL $SOIL_CTRL ///
		if county_sample == 1 & year != `y', absorb(county_id year) vce(cluster county_id)
	local b_loyo = _b[gleam_sms_mean]
	local se_loyo = _se[gleam_sms_mean]
	local p_loyo = 2 * ttail(e(df_r), abs(`b_loyo'/`se_loyo'))

	file write `fh_loyo' "`y'," %10.6f (`b_loyo') "," %10.6f (`se_loyo') "," ///
		%6.4f (`p_loyo') "," (e(N)) _n

	if `b_loyo' < `loyo_min' local loyo_min = `b_loyo'
	if `b_loyo' > `loyo_max' local loyo_max = `b_loyo'

	di "  drop `y': b = " %8.6f `b_loyo' " (p = " %6.4f `p_loyo' ")"
}
file close `fh_loyo'

di ""
di "LOYO summary: full = " %8.6f `b_full' ///
	", drop-2017 shown above, range [" %8.6f `loyo_min' ", " %8.6f `loyo_max' "]"


* #########################################################################
* CHAIN 2: SR Shifts Moisture State
* #########################################################################

di ""
di "============================================================"
di "CHAIN 2: SR SHIFTS MOISTURE STATE"
di "============================================================"

* Open CSV for combined Chain 2 results
tempname fh2
file open `fh2' using "$outdir/step4v2_chain2_sr_shifts_sm.csv", write replace
file write `fh2' "DV,FE,b_ca,se_ca,p_ca,b_SR_x_D,se_SR_x_D,p_SR_x_D,N,r2" _n

* --- DV 1: gleam_sms_mean (surface SM) ---
* County FE
qui reghdfe gleam_sms_mean ca D_season W_season hdd_tmax_ge32 SR_x_D ///
	$CTRL $SOIL_CTRL if county_sample == 1, ///
	absorb(county_id year) vce(cluster county_id)
local b_ca = _b[ca]
local se_ca = _se[ca]
local p_ca = 2*ttail(e(df_r), abs(`b_ca'/`se_ca'))
local b_srd = _b[SR_x_D]
local se_srd = _se[SR_x_D]
local p_srd = 2*ttail(e(df_r), abs(`b_srd'/`se_srd'))
file write `fh2' "gleam_sms_mean,county+year," ///
	%10.6f (`b_ca') "," %10.6f (`se_ca') "," %6.4f (`p_ca') "," ///
	%10.6f (`b_srd') "," %10.6f (`se_srd') "," %6.4f (`p_srd') "," ///
	(e(N)) "," %6.4f (e(r2)) _n

di "sms_mean (county FE): ca = " %8.6f `b_ca' " (p=" %5.4f `p_ca' ")" ///
	", SR_x_D = " %8.6f `b_srd' " (p=" %5.4f `p_srd' ")"

* Grid FE (comparison)
qui reghdfe gleam_sms_mean ca D_season W_season hdd_tmax_ge32 SR_x_D ///
	$CTRL if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)
local b_ca = _b[ca]
local se_ca = _se[ca]
local p_ca = 2*ttail(e(df_r), abs(`b_ca'/`se_ca'))
local b_srd = _b[SR_x_D]
local se_srd = _se[SR_x_D]
local p_srd = 2*ttail(e(df_r), abs(`b_srd'/`se_srd'))
file write `fh2' "gleam_sms_mean,grid+year," ///
	%10.6f (`b_ca') "," %10.6f (`se_ca') "," %6.4f (`p_ca') "," ///
	%10.6f (`b_srd') "," %10.6f (`se_srd') "," %6.4f (`p_srd') "," ///
	(e(N)) "," %6.4f (e(r2)) _n

* --- DV 2: gleam_smrz_mean (rootzone SM) ---
* County FE
qui reghdfe gleam_smrz_mean ca D_season W_season hdd_tmax_ge32 SR_x_D ///
	$CTRL $SOIL_CTRL if county_sample == 1, ///
	absorb(county_id year) vce(cluster county_id)
local b_ca = _b[ca]
local se_ca = _se[ca]
local p_ca = 2*ttail(e(df_r), abs(`b_ca'/`se_ca'))
local b_srd = _b[SR_x_D]
local se_srd = _se[SR_x_D]
local p_srd = 2*ttail(e(df_r), abs(`b_srd'/`se_srd'))
file write `fh2' "gleam_smrz_mean,county+year," ///
	%10.6f (`b_ca') "," %10.6f (`se_ca') "," %6.4f (`p_ca') "," ///
	%10.6f (`b_srd') "," %10.6f (`se_srd') "," %6.4f (`p_srd') "," ///
	(e(N)) "," %6.4f (e(r2)) _n

di "smrz_mean (county FE): ca = " %8.6f `b_ca' " (p=" %5.4f `p_ca' ")" ///
	", SR_x_D = " %8.6f `b_srd' " (p=" %5.4f `p_srd' ")"

* Grid FE
qui reghdfe gleam_smrz_mean ca D_season W_season hdd_tmax_ge32 SR_x_D ///
	$CTRL if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)
local b_ca = _b[ca]
local se_ca = _se[ca]
local p_ca = 2*ttail(e(df_r), abs(`b_ca'/`se_ca'))
local b_srd = _b[SR_x_D]
local se_srd = _se[SR_x_D]
local p_srd = 2*ttail(e(df_r), abs(`b_srd'/`se_srd'))
file write `fh2' "gleam_smrz_mean,grid+year," ///
	%10.6f (`b_ca') "," %10.6f (`se_ca') "," %6.4f (`p_ca') "," ///
	%10.6f (`b_srd') "," %10.6f (`se_srd') "," %6.4f (`p_srd') "," ///
	(e(N)) "," %6.4f (e(r2)) _n

* --- DV 3: hotdrydays (compound, smrz threshold) ---
* Compound-aware RHS: include D_x_Heat and SR_x_D_x_Heat
* County FE
qui reghdfe hotdrydays_tmax_ge32_smrz_le_bas ca D_season W_season hdd_tmax_ge32 ///
	SR_x_D D_x_Heat SR_x_D_x_Heat $CTRL $SOIL_CTRL if county_sample == 1, ///
	absorb(county_id year) vce(cluster county_id)
local b_ca = _b[ca]
local se_ca = _se[ca]
local p_ca = 2*ttail(e(df_r), abs(`b_ca'/`se_ca'))
local b_srd = _b[SR_x_D]
local se_srd = _se[SR_x_D]
local p_srd = 2*ttail(e(df_r), abs(`b_srd'/`se_srd'))
file write `fh2' "hotdrydays_ge32_smrz,county+year," ///
	%10.6f (`b_ca') "," %10.6f (`se_ca') "," %6.4f (`p_ca') "," ///
	%10.6f (`b_srd') "," %10.6f (`se_srd') "," %6.4f (`p_srd') "," ///
	(e(N)) "," %6.4f (e(r2)) _n

di "hotdrydays (county FE): ca = " %8.6f `b_ca' " (p=" %5.4f `p_ca' ")" ///
	", SR_x_D = " %8.6f `b_srd' " (p=" %5.4f `p_srd' ")"

* Also report SR_x_D_x_Heat for compound-aware model
di "  SR_x_D_x_Heat = " %8.6f _b[SR_x_D_x_Heat] ///
	" (p=" %5.4f (2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat]/_se[SR_x_D_x_Heat]))) ")"

* Grid FE
qui reghdfe hotdrydays_tmax_ge32_smrz_le_bas ca D_season W_season hdd_tmax_ge32 ///
	SR_x_D D_x_Heat SR_x_D_x_Heat $CTRL if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)
local b_ca = _b[ca]
local se_ca = _se[ca]
local p_ca = 2*ttail(e(df_r), abs(`b_ca'/`se_ca'))
local b_srd = _b[SR_x_D]
local se_srd = _se[SR_x_D]
local p_srd = 2*ttail(e(df_r), abs(`b_srd'/`se_srd'))
file write `fh2' "hotdrydays_ge32_smrz,grid+year," ///
	%10.6f (`b_ca') "," %10.6f (`se_ca') "," %6.4f (`p_ca') "," ///
	%10.6f (`b_srd') "," %10.6f (`se_srd') "," %6.4f (`p_srd') "," ///
	(e(N)) "," %6.4f (e(r2)) _n

* --- DV 4: drydays (surface SM threshold) ---
* County FE
qui reghdfe drydays_gleam_sms_le_basep10 ca D_season W_season hdd_tmax_ge32 ///
	SR_x_D $CTRL $SOIL_CTRL if county_sample == 1, ///
	absorb(county_id year) vce(cluster county_id)
local b_ca = _b[ca]
local se_ca = _se[ca]
local p_ca = 2*ttail(e(df_r), abs(`b_ca'/`se_ca'))
local b_srd = _b[SR_x_D]
local se_srd = _se[SR_x_D]
local p_srd = 2*ttail(e(df_r), abs(`b_srd'/`se_srd'))
file write `fh2' "drydays_sms_p10,county+year," ///
	%10.6f (`b_ca') "," %10.6f (`se_ca') "," %6.4f (`p_ca') "," ///
	%10.6f (`b_srd') "," %10.6f (`se_srd') "," %6.4f (`p_srd') "," ///
	(e(N)) "," %6.4f (e(r2)) _n

di "drydays_sms (county FE): ca = " %8.6f `b_ca' " (p=" %5.4f `p_ca' ")" ///
	", SR_x_D = " %8.6f `b_srd' " (p=" %5.4f `p_srd' ")"

* Grid FE
qui reghdfe drydays_gleam_sms_le_basep10 ca D_season W_season hdd_tmax_ge32 ///
	SR_x_D $CTRL if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)
local b_ca = _b[ca]
local se_ca = _se[ca]
local p_ca = 2*ttail(e(df_r), abs(`b_ca'/`se_ca'))
local b_srd = _b[SR_x_D]
local se_srd = _se[SR_x_D]
local p_srd = 2*ttail(e(df_r), abs(`b_srd'/`se_srd'))
file write `fh2' "drydays_sms_p10,grid+year," ///
	%10.6f (`b_ca') "," %10.6f (`se_ca') "," %6.4f (`p_ca') "," ///
	%10.6f (`b_srd') "," %10.6f (`se_srd') "," %6.4f (`p_srd') "," ///
	(e(N)) "," %6.4f (e(r2)) _n

file close `fh2'

di ""
di "Chain 2 results exported to: $outdir/step4v2_chain2_sr_shifts_sm.csv"

* =============================================================================
* Chain 2 LOYO: SR -> SM_surface stability
* =============================================================================

di ""
di "--- Chain 2 LOYO: SR -> SM_surface ---"

qui reghdfe gleam_sms_mean ca D_season W_season hdd_tmax_ge32 SR_x_D ///
	$CTRL $SOIL_CTRL if county_sample == 1, ///
	absorb(county_id year) vce(cluster county_id)
local b_ca_full = _b[ca]
local b_srd_full = _b[SR_x_D]

tempname fh2l
file open `fh2l' using "$outdir/step4v2_chain2_loyo.csv", write replace
file write `fh2l' "drop_year,b_ca,se_ca,p_ca,b_SR_x_D,se_SR_x_D,p_SR_x_D,N" _n
file write `fh2l' "full," %10.6f (`b_ca_full') "," %10.6f (_se[ca]) "," ///
	%6.4f (2*ttail(e(df_r), abs(_b[ca]/_se[ca]))) "," ///
	%10.6f (`b_srd_full') "," %10.6f (_se[SR_x_D]) "," ///
	%6.4f (2*ttail(e(df_r), abs(_b[SR_x_D]/_se[SR_x_D]))) "," (e(N)) _n

forvalues y = 2016/2019 {
	qui reghdfe gleam_sms_mean ca D_season W_season hdd_tmax_ge32 SR_x_D ///
		$CTRL $SOIL_CTRL if county_sample == 1 & year != `y', ///
		absorb(county_id year) vce(cluster county_id)
	file write `fh2l' "`y'," ///
		%10.6f (_b[ca]) "," %10.6f (_se[ca]) "," ///
		%6.4f (2*ttail(e(df_r), abs(_b[ca]/_se[ca]))) "," ///
		%10.6f (_b[SR_x_D]) "," %10.6f (_se[SR_x_D]) "," ///
		%6.4f (2*ttail(e(df_r), abs(_b[SR_x_D]/_se[SR_x_D]))) "," (e(N)) _n

	di "  drop `y': ca = " %8.6f _b[ca] ", SR_x_D = " %8.6f _b[SR_x_D]
}
file close `fh2l'


* #########################################################################
* CHAIN 3: Compound Stress Under Moisture-State Conditioning
* #########################################################################

di ""
di "============================================================"
di "CHAIN 3: COMPOUND UNDER MOISTURE-STATE CONDITIONING"
di "============================================================"

* =============================================================================
* Chain 3a: Conditioning Sets 0/1/2
* =============================================================================

di ""
di "--- Chain 3a: Conditioning Sets ---"

eststo clear

* --- County+Year FE panel ---

* Conditioning Set 0: no moisture-state vars
eststo C0_cty: reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL ///
	if county_sample == 1, absorb(county_id year) vce(cluster county_id)

* Conditioning Set 1: + SM_surface
eststo C1_cty: reghdfe ln_yield $RHS_COMPOUND gleam_sms_mean $SOIL_CTRL ///
	if county_sample == 1, absorb(county_id year) vce(cluster county_id)

* Conditioning Set 2: + conditional SM proxies
eststo C2_cty: reghdfe ln_yield $RHS_COMPOUND ///
	hotdrydays_tmax_ge32_smrz_le_bas drydays_gleam_sms_le_basep10 $SOIL_CTRL ///
	if county_sample == 1, absorb(county_id year) vce(cluster county_id)

* --- Grid+Year FE panel (comparison) ---

* Conditioning Set 0: grid FE
eststo C0_grid: reghdfe ln_yield $RHS_COMPOUND ///
	if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)

* Conditioning Set 1: grid FE + SM_surface
eststo C1_grid: reghdfe ln_yield $RHS_COMPOUND gleam_sms_mean ///
	if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)

* Conditioning Set 2: grid FE + conditional SM proxies
eststo C2_grid: reghdfe ln_yield $RHS_COMPOUND ///
	hotdrydays_tmax_ge32_smrz_le_bas drydays_gleam_sms_le_basep10 ///
	if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)

* Export: focus on compound terms
esttab C0_cty C1_cty C2_cty C0_grid C1_grid C2_grid ///
	using "$outdir/step4v2_chain3_compound_sm.csv", replace ///
	cells(b(star fmt(6)) se(par fmt(6)) p(fmt(4))) ///
	keep(SR_x_D_x_Heat D_x_Heat SR_x_Heat SR_x_D ///
		gleam_sms_mean hotdrydays_tmax_ge32_smrz_le_bas drydays_gleam_sms_le_basep10) ///
	stats(N r2, labels("N" "R-sq") fmt(0 4)) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	mtitles("Set0_cty" "Set1_cty" "Set2_cty" "Set0_grid" "Set1_grid" "Set2_grid") ///
	title("Chain 3a: Compound Term Under Different Moisture-State Conditioning")

* Report key compound terms
di ""
di "=== CONDITIONING SET COMPARISON (County FE) ==="
di "SR_x_D_x_Heat:"
qui est restore C0_cty
di "  Set 0: " %8.6f _b[SR_x_D_x_Heat] " (se=" %8.6f _se[SR_x_D_x_Heat] ")"
qui est restore C1_cty
di "  Set 1: " %8.6f _b[SR_x_D_x_Heat] " (se=" %8.6f _se[SR_x_D_x_Heat] ")"
qui est restore C2_cty
di "  Set 2: " %8.6f _b[SR_x_D_x_Heat] " (se=" %8.6f _se[SR_x_D_x_Heat] ")"

di ""
di "D_x_Heat:"
qui est restore C0_cty
di "  Set 0: " %8.6f _b[D_x_Heat] " (se=" %8.6f _se[D_x_Heat] ")"
qui est restore C1_cty
di "  Set 1: " %8.6f _b[D_x_Heat] " (se=" %8.6f _se[D_x_Heat] ")"
qui est restore C2_cty
di "  Set 2: " %8.6f _b[D_x_Heat] " (se=" %8.6f _se[D_x_Heat] ")"

* =============================================================================
* Chain 3a LOYO
* =============================================================================

di ""
di "--- Chain 3 LOYO: SR_x_D_x_Heat under Set 0 (county FE) ---"

tempname fh3l
file open `fh3l' using "$outdir/step4v2_chain3_loyo.csv", write replace
file write `fh3l' "drop_year,conditioning_set,b_SR_x_D_x_Heat,se,p,N" _n

foreach cset in 0 1 {
	if `cset' == 0 local sm_vars ""
	if `cset' == 1 local sm_vars "gleam_sms_mean"

	qui reghdfe ln_yield $RHS_COMPOUND `sm_vars' $SOIL_CTRL ///
		if county_sample == 1, absorb(county_id year) vce(cluster county_id)
	local b = _b[SR_x_D_x_Heat]
	local se = _se[SR_x_D_x_Heat]
	local p = 2*ttail(e(df_r), abs(`b'/`se'))
	file write `fh3l' "full,Set`cset'," %10.6f (`b') "," %10.6f (`se') "," ///
		%6.4f (`p') "," (e(N)) _n

	forvalues y = 2016/2019 {
		qui reghdfe ln_yield $RHS_COMPOUND `sm_vars' $SOIL_CTRL ///
			if county_sample == 1 & year != `y', ///
			absorb(county_id year) vce(cluster county_id)
		local b = _b[SR_x_D_x_Heat]
		local se = _se[SR_x_D_x_Heat]
		local p = 2*ttail(e(df_r), abs(`b'/`se'))
		file write `fh3l' "`y',Set`cset'," %10.6f (`b') "," %10.6f (`se') "," ///
			%6.4f (`p') "," (e(N)) _n
	}
}
file close `fh3l'

* =============================================================================
* Chain 3b: Irrigation Split — VZ2025 State-Contrast
* =============================================================================

di ""
di "--- Chain 3b: Irrigation Split (VZ2025 state-contrast) ---"

eststo clear

* Full compound model, high irrigation
eststo irr_hi: reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL ///
	if county_sample == 1 & irr_high == 1, ///
	absorb(county_id year) vce(cluster county_id)

* Full compound model, low irrigation
eststo irr_lo: reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL ///
	if county_sample == 1 & irr_high == 0, ///
	absorb(county_id year) vce(cluster county_id)

esttab irr_hi irr_lo using "$outdir/step4v2_chain3_irrigation_split.csv", replace ///
	cells(b(star fmt(6)) se(par fmt(6)) p(fmt(4))) ///
	keep(hdd_tmax_ge32 SR_x_Heat D_x_Heat SR_x_D_x_Heat SR_x_D) ///
	stats(N r2, labels("N" "R-sq") fmt(0 4)) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	mtitles("High_Irrigation" "Low_Irrigation") ///
	title("Chain 3b: Irrigation Split (VZ2025 State-Contrast)")

di ""
di "=== IRRIGATION SPLIT RESULTS ==="
di "VZ2025 prediction: Heat damage larger in low-irr; SR buffering stronger in low-irr"
qui est restore irr_hi
di "High irr: hdd = " %8.6f _b[hdd_tmax_ge32] ", SR_x_Heat = " %8.6f _b[SR_x_Heat] ///
	", SR_x_D_x_Heat = " %8.6f _b[SR_x_D_x_Heat]
qui est restore irr_lo
di "Low irr:  hdd = " %8.6f _b[hdd_tmax_ge32] ", SR_x_Heat = " %8.6f _b[SR_x_Heat] ///
	", SR_x_D_x_Heat = " %8.6f _b[SR_x_D_x_Heat]


* #########################################################################
* COUNTY-YEAR AGGREGATION (Credibility Page)
* #########################################################################

di ""
di "============================================================"
di "COUNTY-YEAR AGGREGATION (CREDIBILITY PAGE)"
di "============================================================"

preserve

* --- Record grid distribution before collapse ---
bysort county_id year: gen _grids_cy = _N if county_sample == 1
bysort county_id year: gen _first_cy = (_n == 1) if county_sample == 1

di ""
di "--- Grids per county-year (county_sample) ---"
sum _grids_cy if _first_cy == 1, detail
local cy_mean_grids = r(mean)
local cy_med_grids  = r(p50)
local cy_p25_grids  = r(p25)
local cy_p75_grids  = r(p75)

di "Mean grids/county-year: " %5.1f `cy_mean_grids'
di "Median: " %5.1f `cy_med_grids' ", P25: " %5.1f `cy_p25_grids' ", P75: " %5.1f `cy_p75_grids'

drop _grids_cy _first_cy

* --- Collapse base variables only (NOT interactions) ---
keep if county_sample == 1

collapse (mean) ln_yield gleam_sms_mean gleam_smrz_mean ca D_season W_season ///
	hdd_tmax_ge32 irr_frac pre_sum et0_sum wd_aridity_et0divpre gdd_30 ///
	clay_0_5cm_01deg sand_0_5cm_01deg bdod_0_5cm_01deg phh2o_0_5cm_01deg ///
	silt_0_5cm_01deg hotdrydays_tmax_ge32_smrz_le_bas drydays_gleam_sms_le_basep10 ///
	[aw=maize_area_km2], by(county_id year)

* --- Regenerate interactions at county-year level ---
gen SR_x_D = ca * D_season
gen SR_x_W = ca * W_season
gen SR_x_Heat = ca * hdd_tmax_ge32
gen D_x_Heat = D_season * hdd_tmax_ge32
gen SR_x_D_x_Heat = ca * D_season * hdd_tmax_ge32

label var SR_x_D "SR x Drought (county-year level)"
label var SR_x_W "SR x Wetness (county-year level)"
label var SR_x_Heat "SR x Heat (county-year level)"
label var D_x_Heat "D x Heat (county-year level)"
label var SR_x_D_x_Heat "SR x D x Heat (county-year level)"

xtset county_id year
local N_agg = _N
di ""
di "County-year aggregated N = `N_agg'"

* Open CSV for aggregated results
tempname fh_agg
file open `fh_agg' using "$outdir/step4v2_county_aggregated.csv", write replace
file write `fh_agg' "model,variable,b,se,p,N,r2" _n

* --- Chain 1 core: SM -> yield ---
eststo clear
eststo agg_c1: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca ///
	SR_x_D SR_x_W SR_x_Heat gleam_sms_mean $CTRL $SOIL_CTRL, ///
	absorb(county_id year) vce(cluster county_id)

file write `fh_agg' "chain1_sm_yield,gleam_sms_mean," ///
	%10.6f (_b[gleam_sms_mean]) "," %10.6f (_se[gleam_sms_mean]) "," ///
	%6.4f (2*ttail(e(df_r), abs(_b[gleam_sms_mean]/_se[gleam_sms_mean]))) "," ///
	(e(N)) "," %6.4f (e(r2)) _n

di "Agg Chain 1: SM_sfc = " %8.6f _b[gleam_sms_mean] ///
	" (p=" %5.4f (2*ttail(e(df_r), abs(_b[gleam_sms_mean]/_se[gleam_sms_mean]))) ")"

* --- Chain 2 core: SR -> SM ---
eststo agg_c2: reghdfe gleam_sms_mean ca D_season W_season hdd_tmax_ge32 SR_x_D ///
	$CTRL $SOIL_CTRL, absorb(county_id year) vce(cluster county_id)

file write `fh_agg' "chain2_sr_sm,ca," ///
	%10.6f (_b[ca]) "," %10.6f (_se[ca]) "," ///
	%6.4f (2*ttail(e(df_r), abs(_b[ca]/_se[ca]))) "," ///
	(e(N)) "," %6.4f (e(r2)) _n
file write `fh_agg' "chain2_sr_sm,SR_x_D," ///
	%10.6f (_b[SR_x_D]) "," %10.6f (_se[SR_x_D]) "," ///
	%6.4f (2*ttail(e(df_r), abs(_b[SR_x_D]/_se[SR_x_D]))) "," ///
	(e(N)) "," %6.4f (e(r2)) _n

di "Agg Chain 2: ca = " %8.6f _b[ca] ", SR_x_D = " %8.6f _b[SR_x_D]

* --- Chain 3 core: Compound Set 0 ---
eststo agg_c3_s0: reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL, ///
	absorb(county_id year) vce(cluster county_id)

file write `fh_agg' "chain3_set0,SR_x_D_x_Heat," ///
	%10.6f (_b[SR_x_D_x_Heat]) "," %10.6f (_se[SR_x_D_x_Heat]) "," ///
	%6.4f (2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat]/_se[SR_x_D_x_Heat]))) "," ///
	(e(N)) "," %6.4f (e(r2)) _n

di "Agg Chain 3 Set0: SR_x_D_x_Heat = " %8.6f _b[SR_x_D_x_Heat]

* --- Chain 3 core: Compound Set 1 (+SM_surface) ---
eststo agg_c3_s1: reghdfe ln_yield $RHS_COMPOUND gleam_sms_mean $SOIL_CTRL, ///
	absorb(county_id year) vce(cluster county_id)

file write `fh_agg' "chain3_set1,SR_x_D_x_Heat," ///
	%10.6f (_b[SR_x_D_x_Heat]) "," %10.6f (_se[SR_x_D_x_Heat]) "," ///
	%6.4f (2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat]/_se[SR_x_D_x_Heat]))) "," ///
	(e(N)) "," %6.4f (e(r2)) _n

di "Agg Chain 3 Set1: SR_x_D_x_Heat = " %8.6f _b[SR_x_D_x_Heat]

* --- Grid distribution metadata ---
file write `fh_agg' "metadata,grids_per_cy_mean," %6.2f (`cy_mean_grids') ",,,," _n
file write `fh_agg' "metadata,grids_per_cy_median," %6.2f (`cy_med_grids') ",,,," _n
file write `fh_agg' "metadata,grids_per_cy_p25," %6.2f (`cy_p25_grids') ",,,," _n
file write `fh_agg' "metadata,grids_per_cy_p75," %6.2f (`cy_p75_grids') ",,,," _n

file close `fh_agg'

esttab agg_c1 agg_c2 agg_c3_s0 agg_c3_s1 ///
	using "$outdir/step4v2_county_aggregated_full.csv", replace ///
	cells(b(star fmt(6)) se(par fmt(6)) p(fmt(4))) ///
	keep(gleam_sms_mean ca SR_x_D SR_x_D_x_Heat D_x_Heat SR_x_Heat) ///
	stats(N r2, labels("N" "R-sq") fmt(0 4)) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	mtitles("SM->Yield" "SR->SM" "Compound_Set0" "Compound_Set1") ///
	title("County-Year Aggregated Results")

restore

di ""
di "County-year aggregation exported to: $outdir/step4v2_county_aggregated.csv"


* #########################################################################
* APPENDIX: Diminishing Returns
* #########################################################################

di ""
di "============================================================"
di "APPENDIX: DIMINISHING RETURNS"
di "============================================================"

* G1: SR x D quadratic
cap drop SR_x_D_sq
gen SR_x_D_sq = ca * D_season^2 if county_sample == 1
label var SR_x_D_sq "SR x D-squared"

eststo clear

eststo dim_g1: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca ///
	SR_x_D SR_x_D_sq SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat ///
	$CTRL $SOIL_CTRL if county_sample == 1, ///
	absorb(county_id year) vce(cluster county_id)

di "Diminishing returns: SR_x_D = " %8.6f _b[SR_x_D] ///
	", SR_x_D_sq = " %8.6f _b[SR_x_D_sq] ///
	" (p=" %5.4f (2*ttail(e(df_r), abs(_b[SR_x_D_sq]/_se[SR_x_D_sq]))) ")"

* G2: SR x D by SM surface quartile
di ""
di "--- SR x D by SM surface quartile ---"

tempname fh_dim
file open `fh_dim' using "$outdir/step4v2_diminishing_returns.csv", write replace
file write `fh_dim' "model,variable,b,se,p,N,r2" _n

* Quadratic
file write `fh_dim' "quadratic,SR_x_D," %10.6f (_b[SR_x_D]) "," ///
	%10.6f (_se[SR_x_D]) "," ///
	%6.4f (2*ttail(e(df_r), abs(_b[SR_x_D]/_se[SR_x_D]))) "," ///
	(e(N)) "," %6.4f (e(r2)) _n
file write `fh_dim' "quadratic,SR_x_D_sq," %10.6f (_b[SR_x_D_sq]) "," ///
	%10.6f (_se[SR_x_D_sq]) "," ///
	%6.4f (2*ttail(e(df_r), abs(_b[SR_x_D_sq]/_se[SR_x_D_sq]))) "," ///
	(e(N)) "," %6.4f (e(r2)) _n

* By SM surface quartile
forvalues q = 1/4 {
	qui reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca ///
		SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat ///
		$CTRL $SOIL_CTRL if county_sample == 1 & sms_quartile == `q', ///
		absorb(county_id year) vce(cluster county_id)

	local b_srd = _b[SR_x_D]
	local se_srd = _se[SR_x_D]
	local p_srd = 2*ttail(e(df_r), abs(`b_srd'/`se_srd'))

	file write `fh_dim' "sms_Q`q',SR_x_D," %10.6f (`b_srd') "," ///
		%10.6f (`se_srd') "," %6.4f (`p_srd') "," (e(N)) "," %6.4f (e(r2)) _n

	di "  SMS Q`q': SR_x_D = " %8.6f `b_srd' " (p=" %5.4f `p_srd' ")"
}

file close `fh_dim'

di ""
di "Diminishing returns exported to: $outdir/step4v2_diminishing_returns.csv"


* #########################################################################
* SUMMARY
* #########################################################################

di ""
di "============================================================"
di "STEP 4 MECHANISM V2 COMPLETE"
di "============================================================"
di ""
di "Chain 1 outputs:"
di "  $outdir/step4v2_chain1_fe_ladder.csv"
di "  $outdir/step4v2_chain1_mundlak.csv"
di "  $outdir/step4v2_chain1_r2_comparison.csv"
di "  $outdir/step4v2_chain1_loyo.csv"
di ""
di "Chain 2 outputs:"
di "  $outdir/step4v2_chain2_sr_shifts_sm.csv"
di "  $outdir/step4v2_chain2_loyo.csv"
di ""
di "Chain 3 outputs:"
di "  $outdir/step4v2_chain3_compound_sm.csv"
di "  $outdir/step4v2_chain3_irrigation_split.csv"
di "  $outdir/step4v2_chain3_loyo.csv"
di ""
di "Aggregation:"
di "  $outdir/step4v2_county_aggregated.csv"
di "  $outdir/step4v2_county_aggregated_full.csv"
di ""
di "Appendix:"
di "  $outdir/step4v2_diminishing_returns.csv"
di "============================================================"

log close
