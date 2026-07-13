* =============================================================================
* step8a_boundary.do — Boundary diagnostics for compound SR×D×H estimand
* Purpose: FE gradient, wild bootstrap, drop-2017, year-specific, lead test,
*          D-H support (density, SR variability, concentration, response surface)
* Author: YangSu / Claude Code
* Date: 2026-03-22
* Dependencies: step0_sample_and_macros.do (analysis_main_sample.dta)
* =============================================================================

* --- 0. Setup ---
global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global outdir  "$projdir/output/tables"
global figdir  "$projdir/output/figures"
global logdir  "$projdir/output/logs"

log using "$logdir/step8a_boundary.log", replace

di "============================================================"
di "step8a_boundary.do — Boundary diagnostics (compound SR×D×H)"
di "Date: $S_DATE $S_TIME"
di "============================================================"

* --- Load canonical dataset from Phase 0 ---
use "$projdir/data/processed/analysis_main_sample.dta", clear

* Verify sample integrity
count if main_sample == 1
local expected_N = 61795
assert r(N) == `expected_N'
di "Sample integrity verified: N = " r(N)

* Restore panel setting
xtset grid_id year

* Restore macros (not saved in .dta)
global CTRL irr_frac pre_sum et0_sum wd_aridity_et0divpre gdd_30
global RHS_COMPOUND D_season W_season hdd_tmax_ge32 ca ///
	SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat $CTRL
global SOIL_YEAR clay_0_5cm_01deg_y2017 clay_0_5cm_01deg_y2018 clay_0_5cm_01deg_y2019 ///
	sand_0_5cm_01deg_y2017 sand_0_5cm_01deg_y2018 sand_0_5cm_01deg_y2019 ///
	bdod_0_5cm_01deg_y2017 bdod_0_5cm_01deg_y2018 bdod_0_5cm_01deg_y2019 ///
	phh2o_0_5cm_01deg_y2017 phh2o_0_5cm_01deg_y2018 phh2o_0_5cm_01deg_y2019

* =============================================================================
* PART A: FE GRADIENT (grid+year → grid+regyr → grid+provyr)
* =============================================================================

di _n "============================================================"
di "PART A: FE GRADIENT"
di "============================================================"

eststo clear

* A1: Grid + Year FE (baseline)
eststo fe_yr: reghdfe ln_yield $RHS_COMPOUND if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE "Grid+Year"

* A2: Grid + Region×Year FE
eststo fe_regyr: reghdfe ln_yield $RHS_COMPOUND if main_sample == 1, ///
	absorb(grid_id regyr) vce(cluster grid_id)
estadd local FE "Grid+Reg×Year"

* A3: Grid + Province×Year FE
eststo fe_provyr: reghdfe ln_yield $RHS_COMPOUND if main_sample == 1, ///
	absorb(grid_id prov_year) vce(cluster grid_id)
estadd local FE "Grid+Prov×Year"

* A4: Grid + Year + Soil×Year (extended controls)
eststo fe_soil: reghdfe ln_yield $RHS_COMPOUND $SOIL_YEAR if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE "Grid+Year"
estadd local SoilYr "Yes"

esttab fe_yr fe_regyr fe_provyr fe_soil using "$outdir/step8a_fe_gradient.csv", ///
	replace cells(b(fmt(6)) se(par fmt(6)) p(fmt(4))) ///
	keep(SR_x_D_x_Heat SR_x_D SR_x_Heat D_x_Heat) ///
	stats(FE SoilYr N r2, labels("Fixed Effects" "Soil×Year" "N" "R²") ///
	fmt(%s %s %9.0fc %6.4f)) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	mtitles("Grid+Year" "Grid+Reg×Yr" "Grid+Prov×Yr" "Grid+Yr+Soil") ///
	title("FE Gradient: Compound Estimand")

di _n "=== FE Gradient: SR_x_D_x_Heat ==="
di "Grid+Year:    " %8.6f _b[SR_x_D_x_Heat] " (se=" %8.6f _se[SR_x_D_x_Heat] ")"

* Store fe_yr results for wild bootstrap (Part B)
estimates restore fe_yr

* =============================================================================
* PART B: WILD BOOTSTRAP
* Wild bootstrap on SR_x_D_x_Heat: corrects finite-sample cluster inference
* (grid_id), NOT few-cluster T problem. T=4 too few to cluster on year.
* =============================================================================

di _n "============================================================"
di "PART B: WILD BOOTSTRAP (cluster = grid_id)"
di "============================================================"

* First re-estimate with reghdfe (boottest needs last estimation stored)
reghdfe ln_yield $RHS_COMPOUND if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)

* boottest SR_x_D_x_Heat
di _n "--- boottest SR_x_D_x_Heat ---"
cap noi boottest SR_x_D_x_Heat, cluster(grid_id) boottype(wild) reps(999) seed(42) nograph
if _rc == 0 {
	local wb_p_triple = r(p)
	di "Wild bootstrap p-value (SR_x_D_x_Heat): " %6.4f `wb_p_triple'
}
else {
	local wb_p_triple = .
	di "boottest for SR_x_D_x_Heat failed (rc=" _rc ")"
}

* boottest SR_x_D
di _n "--- boottest SR_x_D ---"
cap noi boottest SR_x_D, cluster(grid_id) boottype(wild) reps(999) seed(42) nograph
if _rc == 0 {
	local wb_p_drought = r(p)
}
else {
	local wb_p_drought = .
}

* boottest SR_x_Heat
di _n "--- boottest SR_x_Heat ---"
cap noi boottest SR_x_Heat, cluster(grid_id) boottype(wild) reps(999) seed(42) nograph
if _rc == 0 {
	local wb_p_heat = r(p)
}
else {
	local wb_p_heat = .
}

* Export wild bootstrap results
tempname fh
file open `fh' using "$outdir/step8a_wild_bootstrap.csv", write replace
file write `fh' "coefficient,wb_pvalue" _n
file write `fh' "SR_x_D_x_Heat," %8.4f (`wb_p_triple') _n
file write `fh' "SR_x_D," %8.4f (`wb_p_drought') _n
file write `fh' "SR_x_Heat," %8.4f (`wb_p_heat') _n
file close `fh'

* =============================================================================
* PART C: DROP-2017 + YEAR-SPECIFIC
* =============================================================================

di _n "============================================================"
di "PART C: DROP-2017 + YEAR-SPECIFIC"
di "============================================================"

eststo clear

* C1: Full sample (reference)
eststo full_comp: reghdfe ln_yield $RHS_COMPOUND if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local Sample "Full"

* C2: Drop 2017
eststo drop17: reghdfe ln_yield $RHS_COMPOUND if main_sample == 1 & year != 2017, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local Sample "Drop2017"

* C3: Year-specific triple interactions
* Generate year-specific interaction dummies for SR×D×H, SR×D, SR×Heat
foreach v in SR_x_D_x_Heat SR_x_D SR_x_Heat {
	forvalues y = 2016/2019 {
		cap drop `v'_y`y'
		gen `v'_y`y' = `v' * (year == `y')
	}
}

eststo yr_triple: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca ///
	SR_x_D SR_x_W SR_x_Heat D_x_Heat ///
	SR_x_D_x_Heat_y2016 SR_x_D_x_Heat_y2017 SR_x_D_x_Heat_y2018 SR_x_D_x_Heat_y2019 ///
	$CTRL if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local Sample "YrSpecific"

* Report year-specific triple coefficients
di _n "=== Year-specific SR_x_D_x_Heat ==="
forvalues y = 2016/2019 {
	di "`y': " %8.6f _b[SR_x_D_x_Heat_y`y'] ///
		" (se=" %8.6f _se[SR_x_D_x_Heat_y`y'] ///
		", t=" %6.2f (_b[SR_x_D_x_Heat_y`y']/_se[SR_x_D_x_Heat_y`y']) ")"
}

esttab full_comp drop17 yr_triple using "$outdir/step8a_year_specific.csv", ///
	replace cells(b(fmt(6)) se(par fmt(6)) p(fmt(4))) ///
	keep(SR_x_D_x_Heat SR_x_D SR_x_Heat ///
		SR_x_D_x_Heat_y2016 SR_x_D_x_Heat_y2017 SR_x_D_x_Heat_y2018 SR_x_D_x_Heat_y2019) ///
	stats(Sample N r2, labels("Sample" "N" "R²") fmt(%s %9.0fc %6.4f)) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	mtitles("Full" "Drop2017" "YrSpecific") ///
	title("Year-specific and drop-2017 diagnostics")

* =============================================================================
* PART D: TRIPLE LEAD TEST
* =============================================================================

di _n "============================================================"
di "PART D: TRIPLE LEAD TEST"
di "============================================================"

* Generate future SR (ca_{t+1})
cap drop ca_f1
bysort grid_id (year): gen ca_f1 = ca[_n+1]
label var ca_f1 "Future SR (ca_{t+1})"

* Generate future-SR interactions
cap drop SR_f1_D SR_f1_Heat SR_f1_DxH
gen SR_f1_D    = ca_f1 * D_season
gen SR_f1_Heat = ca_f1 * hdd_tmax_ge32
gen SR_f1_DxH  = ca_f1 * D_season * hdd_tmax_ge32
label var SR_f1_D    "Future SR × Drought"
label var SR_f1_Heat "Future SR × Heat"
label var SR_f1_DxH  "Future SR × D × H"

eststo clear

* D1: Current SR only (reference)
eststo lead_curr: reghdfe ln_yield $RHS_COMPOUND if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local LeadTerms "None"

* D2: Future SR only (falsification)
eststo lead_fut: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca_f1 ///
	SR_f1_D SR_f1_Heat SR_f1_DxH D_x_Heat $CTRL ///
	if main_sample == 1 & !missing(ca_f1), ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local LeadTerms "Future only"

* D3: Both current + future (horse race)
eststo lead_both: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca ca_f1 ///
	SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat ///
	SR_f1_D SR_f1_Heat SR_f1_DxH $CTRL ///
	if main_sample == 1 & !missing(ca_f1), ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local LeadTerms "Both"

esttab lead_curr lead_fut lead_both using "$outdir/step8a_triple_lead.csv", ///
	replace cells(b(fmt(6)) se(par fmt(6)) p(fmt(4))) ///
	keep(SR_x_D_x_Heat SR_x_D SR_x_Heat SR_f1_DxH SR_f1_D SR_f1_Heat) ///
	stats(LeadTerms N r2, labels("Lead Terms" "N" "R²") fmt(%s %9.0fc %6.4f)) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	mtitles("Current" "Future" "Both") ///
	title("Triple lead test: current vs future SR interactions")

di _n "=== Lead test summary ==="
estimates restore lead_both
di "Current SR×D×H: " %8.6f _b[SR_x_D_x_Heat] " (p=" %6.4f (2*normal(-abs(_b[SR_x_D_x_Heat]/_se[SR_x_D_x_Heat]))) ")"
di "Future  SR×D×H: " %8.6f _b[SR_f1_DxH] " (p=" %6.4f (2*normal(-abs(_b[SR_f1_DxH]/_se[SR_f1_DxH]))) ")"
di "Current SR×D:   " %8.6f _b[SR_x_D] " (p=" %6.4f (2*normal(-abs(_b[SR_x_D]/_se[SR_x_D]))) ")"
di "Future  SR×D:   " %8.6f _b[SR_f1_D] " (p=" %6.4f (2*normal(-abs(_b[SR_f1_D]/_se[SR_f1_D]))) ")"

* =============================================================================
* PART E: D-H SUPPORT (density, SR variability, concentration, response surface)
* =============================================================================

di _n "============================================================"
di "PART E: D-H SUPPORT"
di "============================================================"

* --- E1: D×H density ---
di _n "=== E1: D × H cross-tabulation ==="
tab D_bin3 H_bin3 if main_sample == 1

* --- E2: Stress-corner SR variability ---
di _n "=== E2: Stress corner SR variability ==="
sum ca if stress_corner == 1 & main_sample == 1, detail
local corner_N    = r(N)
local corner_mean = r(mean)
local corner_sd   = r(sd)
local corner_cv   = `corner_sd' / `corner_mean'

di "Stress corner (D_bin3==3 & H_bin3==3):"
di "  N = `corner_N'"
di "  ca mean = " %6.4f `corner_mean'
di "  ca SD   = " %6.4f `corner_sd'
di "  ca CV   = " %6.4f `corner_cv'

sum ca if main_sample == 1
local full_mean = r(mean)
local full_sd   = r(sd)

* --- E3: Province-year concentration in stress corner ---
di _n "=== E3: Province-year concentration ==="

* Count obs per province-year in stress corner
preserve
keep if stress_corner == 1 & main_sample == 1

* Create province-year label
cap drop provyr_label
egen provyr_label = concat(province year), punct("_")

* Count and sort
contract provyr_label, freq(n_corner)
gsort -n_corner
gen cum_n = sum(n_corner)
local total_corner = cum_n[_N]
gen share_pct = 100 * cum_n / `total_corner'

di "Total stress corner obs: `total_corner'"
di ""
di "Top 5 province-years in stress corner:"
list provyr_label n_corner share_pct in 1/5, noobs clean

* Export concentration table
export delimited provyr_label n_corner share_pct using ///
	"$outdir/step8a_corner_provyr.csv" in 1/10, replace
restore

* Now compute loss metrics for stress corner
* Model-adjusted predictions (not raw means)

* --- E4: Full support metrics ---
di _n "=== E4: Support metrics ==="

* Mean ln_yield in corner vs full sample (FE-adjusted)
sum ln_yield if stress_corner == 1 & main_sample == 1
local corner_yield = r(mean)
sum ln_yield if main_sample == 1
local full_yield = r(mean)
local raw_loss = `corner_yield' - `full_yield'

di "Raw mean ln_yield (corner):  " %6.4f `corner_yield'
di "Raw mean ln_yield (full):    " %6.4f `full_yield'
di "Raw difference:              " %6.4f `raw_loss'
di "(NOTE: raw means confound location effects — use adjusted predictions below)"

* Export support summary
tempname fh2
file open `fh2' using "$outdir/step8a_dh_support.csv", write replace
file write `fh2' "metric,value" _n
file write `fh2' "corner_N," (`corner_N') _n
file write `fh2' "corner_SR_mean," %8.6f (`corner_mean') _n
file write `fh2' "corner_SR_sd," %8.6f (`corner_sd') _n
file write `fh2' "corner_SR_cv," %8.6f (`corner_cv') _n
file write `fh2' "full_SR_mean," %8.6f (`full_mean') _n
file write `fh2' "full_SR_sd," %8.6f (`full_sd') _n
file write `fh2' "corner_raw_lnyield," %8.6f (`corner_yield') _n
file write `fh2' "full_raw_lnyield," %8.6f (`full_yield') _n
file write `fh2' "raw_loss_diff," %8.6f (`raw_loss') _n
file close `fh2'

* =============================================================================
* PART F: RESPONSE SURFACE (model-adjusted predictions, NOT raw means)
* Figure caption: "FE-adjusted binned predictions; main estimand is continuous triple."
* =============================================================================

di _n "============================================================"
di "PART F: RESPONSE SURFACE (model-adjusted predictions)"
di "============================================================"

* Use areg + margins for adjusted predictions
* Include D_bin3 × H_bin3 × SR_high full interaction + controls + year FE
areg ln_yield i.D_bin3##i.H_bin3##i.SR_high $CTRL i.year ///
	if main_sample == 1, absorb(grid_id) vce(cluster grid_id)

margins D_bin3#H_bin3#SR_high, post

* Extract 18 cells (3 D × 3 H × 2 SR)
* Build dataset for export
preserve
clear
set obs 18

gen D_bin = .
gen H_bin = .
gen SR_group = .
gen adj_mean = .
gen adj_se = .

local row = 1
forvalues d = 1/3 {
	forvalues h = 1/3 {
		forvalues s = 0/1 {
			replace D_bin = `d' in `row'
			replace H_bin = `h' in `row'
			replace SR_group = `s' in `row'
			* margins stores results as _b and _se after post
			* Naming: _b[`d'.D_bin3#`h'.H_bin3#`s'.SR_high]
			replace adj_mean = _b[`d'.D_bin3#`h'.H_bin3#`s'.SR_high] in `row'
			replace adj_se   = _se[`d'.D_bin3#`h'.H_bin3#`s'.SR_high] in `row'
			local row = `row' + 1
		}
	}
}

* Labels
label define D_lbl 1 "Normal" 2 "Moderate" 3 "Severe"
label define H_lbl 1 "Cool" 2 "Moderate" 3 "Hot"
label define SR_lbl 0 "Low SR" 1 "High SR"
label values D_bin D_lbl
label values H_bin H_lbl
label values SR_group SR_lbl

* Check stress corner (D=3, H=3): adjusted predictions should show loss
di _n "=== Stress corner adjusted predictions ==="
list D_bin H_bin SR_group adj_mean adj_se if D_bin == 3 & H_bin == 3, noobs clean

di _n "=== Full adjusted predictions ==="
list D_bin H_bin SR_group adj_mean adj_se, noobs clean

export delimited using "$outdir/step8a_response_surface.csv", replace
restore

* =============================================================================
* SUMMARY
* =============================================================================

di _n "============================================================"
di "STEP 8A COMPLETE"
di "============================================================"
di "Output files:"
di "  $outdir/step8a_fe_gradient.csv"
di "  $outdir/step8a_wild_bootstrap.csv"
di "  $outdir/step8a_year_specific.csv"
di "  $outdir/step8a_triple_lead.csv"
di "  $outdir/step8a_dh_support.csv"
di "  $outdir/step8a_corner_provyr.csv"
di "  $outdir/step8a_response_surface.csv"
di "============================================================"

log close
