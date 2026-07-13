* =============================================================================
* step8b_spec_curve.do — Specification Curve (Transparency Tool)
* Purpose: 72 specs × 3 estimands (SR×D×H, SR×Heat, SR×D)
*          Main panel: SR×D×H; parallel: SR×Heat; secondary: SR×D
*          Sign flip diagnosis for SR×Heat
* Author: YangSu / Claude Code
* Date: 2026-03-22
* Dependencies: step0_sample_and_macros.do (analysis_main_sample.dta)
* =============================================================================

* --- 0. Setup ---
global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global outdir  "$projdir/output/tables"
global figdir  "$projdir/output/figures"
global logdir  "$projdir/output/logs"

log using "$logdir/step8b_spec_curve.log", replace

di "============================================================"
di "step8b_spec_curve.do — Specification Curve (72 specs)"
di "Date: $S_DATE $S_TIME"
di "============================================================"

* --- Load canonical dataset ---
use "$projdir/data/processed/analysis_main_sample.dta", clear

count if main_sample == 1
local expected_N = 61795
assert r(N) == `expected_N'
di "Sample integrity verified: N = " r(N)

xtset grid_id year

* Restore macros
global CTRL irr_frac pre_sum et0_sum wd_aridity_et0divpre gdd_30
global SOIL_YEAR clay_0_5cm_01deg_y2017 clay_0_5cm_01deg_y2018 clay_0_5cm_01deg_y2019 ///
	sand_0_5cm_01deg_y2017 sand_0_5cm_01deg_y2018 sand_0_5cm_01deg_y2019 ///
	bdod_0_5cm_01deg_y2017 bdod_0_5cm_01deg_y2018 bdod_0_5cm_01deg_y2019 ///
	phh2o_0_5cm_01deg_y2017 phh2o_0_5cm_01deg_y2018 phh2o_0_5cm_01deg_y2019

* =============================================================================
* SPECIFICATION LOOP: 72 = 3 heat × 3 FE × 2 cluster × 2 controls × 2 SR
* =============================================================================

* Generate lag SR (needed for sr_measure dimension)
cap drop crc_lag1
bysort grid_id (year): gen crc_lag1 = ca[_n-1]
label var crc_lag1 "Lagged SR (ca_{t-1})"

* Open postfile for results
tempname pf
tempfile spec_results
postfile `pf' spec_id str5 heat_thresh str8 fe_struct str5 cluster ///
	str8 controls str8 sr_measure ///
	b_triple se_triple p_triple ///
	b_heat se_heat p_heat ///
	b_drought se_drought p_drought ///
	N r2 ///
	using `spec_results'

local spec = 0

* Loop over all 72 specifications
foreach heat_t in 30 32 35 {
	foreach fe_t in yr regyr provyr {
		foreach clust in grid 2way {
			foreach ctrl in base extended {
				foreach sr_m in ca lag {

					local spec = `spec' + 1

					* --- Build variable names ---
					* Heat variable
					local hvar hdd_tmax_ge`heat_t'

					* SR variable
					if "`sr_m'" == "ca" {
						local srvar ca
					}
					else {
						local srvar crc_lag1
					}

					* Generate spec-specific interactions
					cap drop _sr_x_d _sr_x_w _sr_x_heat _d_x_heat _sr_x_d_x_heat
					gen _sr_x_d       = `srvar' * D_season
					gen _sr_x_w       = `srvar' * W_season
					gen _sr_x_heat    = `srvar' * `hvar'
					gen _d_x_heat     = D_season * `hvar'
					gen _sr_x_d_x_heat = `srvar' * D_season * `hvar'

					* RHS
					local rhs D_season W_season `hvar' `srvar' ///
						_sr_x_d _sr_x_w _sr_x_heat _d_x_heat _sr_x_d_x_heat $CTRL
					if "`ctrl'" == "extended" {
						local rhs `rhs' $SOIL_YEAR
					}

					* FE
					if "`fe_t'" == "yr" {
						local absorb "grid_id year"
					}
					else if "`fe_t'" == "regyr" {
						local absorb "grid_id regyr"
					}
					else {
						local absorb "grid_id prov_year"
					}

					* Clustering
					if "`clust'" == "grid" {
						local vce "vce(cluster grid_id)"
					}
					else {
						local vce "vce(cluster grid_id year)"
					}

					* --- Estimate ---
					cap noi reghdfe ln_yield `rhs' if main_sample == 1, ///
						absorb(`absorb') `vce'

					if _rc == 0 {
						local b_t  = _b[_sr_x_d_x_heat]
						local se_t = _se[_sr_x_d_x_heat]
						local p_t  = 2 * normal(-abs(`b_t'/`se_t'))

						local b_h  = _b[_sr_x_heat]
						local se_h = _se[_sr_x_heat]
						local p_h  = 2 * normal(-abs(`b_h'/`se_h'))

						local b_d  = _b[_sr_x_d]
						local se_d = _se[_sr_x_d]
						local p_d  = 2 * normal(-abs(`b_d'/`se_d'))

						local n_spec = e(N)
						local r2_spec = e(r2)
					}
					else {
						local b_t = .
						local se_t = .
						local p_t = .
						local b_h = .
						local se_h = .
						local p_h = .
						local b_d = .
						local se_d = .
						local p_d = .
						local n_spec = .
						local r2_spec = .
					}

					post `pf' (`spec') ("`heat_t'C") ("`fe_t'") ("`clust'") ///
						("`ctrl'") ("`sr_m'") ///
						(`b_t') (`se_t') (`p_t') ///
						(`b_h') (`se_h') (`p_h') ///
						(`b_d') (`se_d') (`p_d') ///
						(`n_spec') (`r2_spec')

					* Progress
					if mod(`spec', 12) == 0 {
						di "Spec `spec' / 72 done"
					}

					cap drop _sr_x_d _sr_x_w _sr_x_heat _d_x_heat _sr_x_d_x_heat
				}
			}
		}
	}
}

postclose `pf'

* --- Load and export results ---
use `spec_results', clear

di _n "============================================================"
di "SPECIFICATION CURVE RESULTS SUMMARY"
di "============================================================"

* How many specs ran successfully
count if !missing(b_triple)
local n_success = r(N)
di "Specs completed: `n_success' / 72"

* SR×D×H sign summary
count if b_triple > 0 & !missing(b_triple)
local n_pos_t = r(N)
count if b_triple > 0 & p_triple < 0.10 & !missing(b_triple)
local n_possig_t = r(N)
count if b_triple < 0 & p_triple < 0.10 & !missing(b_triple)
local n_negsig_t = r(N)

di "SR×D×H: `n_pos_t'/`n_success' positive, `n_possig_t' positive-sig, `n_negsig_t' negative-sig"

* SR×Heat sign summary
count if b_heat > 0 & !missing(b_heat)
local n_pos_h = r(N)
count if b_heat > 0 & p_heat < 0.10 & !missing(b_heat)
local n_possig_h = r(N)
count if b_heat < 0 & p_heat < 0.10 & !missing(b_heat)
local n_negsig_h = r(N)

di "SR×Heat: `n_pos_h'/`n_success' positive, `n_possig_h' positive-sig, `n_negsig_h' negative-sig"

* SR×D sign summary
count if b_drought > 0 & !missing(b_drought)
local n_pos_d = r(N)
count if b_drought > 0 & p_drought < 0.10 & !missing(b_drought)
local n_possig_d = r(N)
count if b_drought < 0 & p_drought < 0.10 & !missing(b_drought)
local n_negsig_d = r(N)

di "SR×D:   `n_pos_d'/`n_success' positive, `n_possig_d' positive-sig, `n_negsig_d' negative-sig"

export delimited using "$outdir/step8b_spec_curve.csv", replace

* =============================================================================
* SIGN FLIP DIAGNOSIS (for SR×Heat)
* Which spec dimensions drive the sign flips?
* =============================================================================

di _n "============================================================"
di "SIGN FLIP DIAGNOSIS (SR×Heat)"
di "============================================================"

* By heat threshold
di _n "--- By heat threshold ---"
forvalues i = 1/3 {
	local thresh : word `i' of "30C" "32C" "35C"
	count if heat_thresh == "`thresh'" & b_heat < 0 & !missing(b_heat)
	local n_neg = r(N)
	count if heat_thresh == "`thresh'" & !missing(b_heat)
	local n_tot = r(N)
	di "`thresh': `n_neg'/`n_tot' negative"
}

* By FE
di _n "--- By FE structure ---"
foreach fe in yr regyr provyr {
	count if fe_struct == "`fe'" & b_heat < 0 & !missing(b_heat)
	local n_neg = r(N)
	count if fe_struct == "`fe'" & !missing(b_heat)
	local n_tot = r(N)
	di "`fe': `n_neg'/`n_tot' negative"
}

* By SR measure
di _n "--- By SR measure ---"
foreach sr in ca lag {
	count if sr_measure == "`sr'" & b_heat < 0 & !missing(b_heat)
	local n_neg = r(N)
	count if sr_measure == "`sr'" & !missing(b_heat)
	local n_tot = r(N)
	di "`sr': `n_neg'/`n_tot' negative"
}

* By clustering
di _n "--- By clustering ---"
foreach cl in grid 2way {
	count if cluster == "`cl'" & b_heat < 0 & !missing(b_heat)
	local n_neg = r(N)
	count if cluster == "`cl'" & !missing(b_heat)
	local n_tot = r(N)
	di "`cl': `n_neg'/`n_tot' negative"
}

* By controls
di _n "--- By controls ---"
foreach ct in base extended {
	count if controls == "`ct'" & b_heat < 0 & !missing(b_heat)
	local n_neg = r(N)
	count if controls == "`ct'" & !missing(b_heat)
	local n_tot = r(N)
	di "`ct': `n_neg'/`n_tot' negative"
}

* Export sign flip diagnosis
preserve
gen heat_neg = (b_heat < 0) if !missing(b_heat)
gen heat_negsig = (b_heat < 0 & p_heat < 0.10) if !missing(b_heat)

collapse (mean) heat_neg heat_negsig, by(heat_thresh fe_struct sr_measure cluster controls)
export delimited using "$outdir/step8b_sign_flip_diagnosis.csv", replace
restore

di _n "============================================================"
di "STEP 8B COMPLETE"
di "============================================================"
di "Output files:"
di "  $outdir/step8b_spec_curve.csv (72 rows)"
di "  $outdir/step8b_sign_flip_diagnosis.csv"
di "============================================================"

log close
