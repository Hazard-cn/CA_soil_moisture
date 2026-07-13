* =============================================================================
* step4_mediation_formal.do — Formal Single-Channel Mediation Analysis
* Purpose: Formal indirect-path decomposition for SM_surface as mediator.
*          Path 1 (Drought-water): SR×D → gleam_sms_mean → ln_yield
*          Path 2 (Compound-water): SR×D×H → gleam_sms_mean → ln_yield
*          Supporting mediator: drydays_gleam_sms_le_basep10 (surface tail)
*          All equations retain full compound RHS.
*          Bootstrap: cluster on county_id, 1000 reps.
* Author: YangSu / Claude Code
* Date: 2026-03-23
* Dependencies: analysis_main_sample.dta (from step0), reghdfe
* =============================================================================

clear all
set more off
set seed 42

* =============================================================================
* 0. Macros and data (self-contained)
* =============================================================================
global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global outdir  "$projdir/output/tables"
global logdir  "$projdir/output/logs"

* Controls — hardcoded, not from preamble
global CTRL irr_frac pre_sum et0_sum wd_aridity_et0divpre gdd_30
global SOIL_CTRL clay_0_5cm_01deg sand_0_5cm_01deg bdod_0_5cm_01deg ///
	phh2o_0_5cm_01deg silt_0_5cm_01deg

* Full compound model RHS (everything except mediator)
global RHS_COMPOUND D_season W_season hdd_tmax_ge32 ca ///
	SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat $CTRL

cap log close
log using "$logdir/step4_mediation_formal_20260323.log", replace

di "============================================================"
di "step4_mediation_formal.do — Formal Single-Channel Mediation"
di "Date: $S_DATE $S_TIME"
di "============================================================"

* Load data
use "$projdir/data/processed/analysis_main_sample.dta", clear
cap drop __*
xtset grid_id year

* =============================================================================
* 1. DEFINE STRICT COMMON MEDIATION SAMPLE
* =============================================================================
* All equations (total, mediator, outcome) must use identical observations.

* 1a. County FE baseline to get feasible sample
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL if main_sample == 1, ///
	absorb(county_id year) vce(cluster county_id)
gen med_sample_cty = e(sample)
* Require non-missing SM and drydays on this sample
replace med_sample_cty = 0 if missing(gleam_sms_mean)
replace med_sample_cty = 0 if missing(drydays_gleam_sms_le_basep10)

count if med_sample_cty == 1
local N_med_cty = r(N)
di "Mediation sample (county FE): N = `N_med_cty'"

* 1b. Grid FE baseline
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL gleam_sms_mean if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)
gen med_sample_grid = e(sample)
replace med_sample_grid = 0 if missing(drydays_gleam_sms_le_basep10)

count if med_sample_grid == 1
local N_med_grid = r(N)
di "Mediation sample (grid FE): N = `N_med_grid'"


* =============================================================================
* 2. PART A: PRIMARY MEDIATOR — gleam_sms_mean, COUNTY FE
* =============================================================================
di _n "============================================================"
di "PART A: Primary Mediator (gleam_sms_mean) — County FE"
di "============================================================"

* --- A1. Total Effect (without mediator) ---
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL if med_sample_cty == 1, ///
	absorb(county_id year) vce(cluster county_id)

local total_SRxD_c     = _b[SR_x_D]
local total_SRxD_se_c  = _se[SR_x_D]
local total_SRxDxH_c   = _b[SR_x_D_x_Heat]
local total_SRxDxH_se_c = _se[SR_x_D_x_Heat]
local N_c = e(N)
local r2_total_c = e(r2)

di "Total SR×D:     " %10.6f `total_SRxD_c' " (" %9.6f `total_SRxD_se_c' ")"
di "Total SR×D×H:   " %10.6f `total_SRxDxH_c' " (" %9.6f `total_SRxDxH_se_c' ")"

* --- A2. Mediator Equation: gleam_sms_mean = f(RHS_COMPOUND) ---
reghdfe gleam_sms_mean $RHS_COMPOUND $SOIL_CTRL if med_sample_cty == 1, ///
	absorb(county_id year) vce(cluster county_id)

local a_SRxD_c     = _b[SR_x_D]
local a_SRxD_se_c  = _se[SR_x_D]
local a_SRxD_p_c   = 2 * ttail(e(df_r), abs(_b[SR_x_D] / _se[SR_x_D]))
local a_SRxDxH_c   = _b[SR_x_D_x_Heat]
local a_SRxDxH_se_c = _se[SR_x_D_x_Heat]
local a_SRxDxH_p_c = 2 * ttail(e(df_r), abs(_b[SR_x_D_x_Heat] / _se[SR_x_D_x_Heat]))

di "a-path SR×D→SM:   " %10.6f `a_SRxD_c' " (" %9.6f `a_SRxD_se_c' ") p=" %6.4f `a_SRxD_p_c'
di "a-path SR×D×H→SM:  " %10.6f `a_SRxDxH_c' " (" %9.6f `a_SRxDxH_se_c' ") p=" %6.4f `a_SRxDxH_p_c'

* --- A3. Outcome Equation with Mediator ---
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL gleam_sms_mean if med_sample_cty == 1, ///
	absorb(county_id year) vce(cluster county_id)

local lam_c     = _b[gleam_sms_mean]
local lam_se_c  = _se[gleam_sms_mean]
local lam_p_c   = 2 * ttail(e(df_r), abs(_b[gleam_sms_mean] / _se[gleam_sms_mean]))
local dir_SRxD_c     = _b[SR_x_D]
local dir_SRxD_se_c  = _se[SR_x_D]
local dir_SRxDxH_c   = _b[SR_x_D_x_Heat]
local dir_SRxDxH_se_c = _se[SR_x_D_x_Heat]
local r2_dir_c = e(r2)

di "lambda (SM→Y):    " %10.6f `lam_c' " (" %9.6f `lam_se_c' ") p=" %6.4f `lam_p_c'
di "Direct SR×D:      " %10.6f `dir_SRxD_c' " (" %9.6f `dir_SRxD_se_c' ")"
di "Direct SR×D×H:    " %10.6f `dir_SRxDxH_c' " (" %9.6f `dir_SRxDxH_se_c' ")"

* --- A4. Sobel (Delta Method) ---
local ind_d_c = `a_SRxD_c' * `lam_c'
local sobel_d_c = sqrt((`a_SRxD_c')^2 * (`lam_se_c')^2 + ///
	(`lam_c')^2 * (`a_SRxD_se_c')^2)

local ind_t_c = `a_SRxDxH_c' * `lam_c'
local sobel_t_c = sqrt((`a_SRxDxH_c')^2 * (`lam_se_c')^2 + ///
	(`lam_c')^2 * (`a_SRxDxH_se_c')^2)

di _n "=== COUNTY FE: Drought-Water Path (SR×D) ==="
di "Total:    " %10.6f `total_SRxD_c'
di "Direct:   " %10.6f `dir_SRxD_c'
di "Indirect: " %10.6f `ind_d_c' " (Sobel SE=" %9.6f `sobel_d_c' ")"

di _n "=== COUNTY FE: Compound-Water Path (SR×D×H) ==="
di "Total:    " %10.6f `total_SRxDxH_c'
di "Direct:   " %10.6f `dir_SRxDxH_c'
di "Indirect: " %10.6f `ind_t_c' " (Sobel SE=" %9.6f `sobel_t_c' ")"


* =============================================================================
* 3. PART B: PRIMARY MEDIATOR — gleam_sms_mean, GRID FE
* =============================================================================
di _n "============================================================"
di "PART B: Primary Mediator (gleam_sms_mean) — Grid FE"
di "============================================================"

* B1. Total Effect
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL if med_sample_grid == 1, ///
	absorb(grid_id year) vce(cluster grid_id)

local total_SRxD_g     = _b[SR_x_D]
local total_SRxD_se_g  = _se[SR_x_D]
local total_SRxDxH_g   = _b[SR_x_D_x_Heat]
local total_SRxDxH_se_g = _se[SR_x_D_x_Heat]
local N_g = e(N)
local r2_total_g = e(r2)

* B2. Mediator Equation
reghdfe gleam_sms_mean $RHS_COMPOUND $SOIL_CTRL if med_sample_grid == 1, ///
	absorb(grid_id year) vce(cluster grid_id)

local a_SRxD_g     = _b[SR_x_D]
local a_SRxD_se_g  = _se[SR_x_D]
local a_SRxD_p_g   = 2 * ttail(e(df_r), abs(_b[SR_x_D] / _se[SR_x_D]))
local a_SRxDxH_g   = _b[SR_x_D_x_Heat]
local a_SRxDxH_se_g = _se[SR_x_D_x_Heat]
local a_SRxDxH_p_g = 2 * ttail(e(df_r), abs(_b[SR_x_D_x_Heat] / _se[SR_x_D_x_Heat]))

* B3. Outcome Equation with Mediator
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL gleam_sms_mean if med_sample_grid == 1, ///
	absorb(grid_id year) vce(cluster grid_id)

local lam_g     = _b[gleam_sms_mean]
local lam_se_g  = _se[gleam_sms_mean]
local lam_p_g   = 2 * ttail(e(df_r), abs(_b[gleam_sms_mean] / _se[gleam_sms_mean]))
local dir_SRxD_g     = _b[SR_x_D]
local dir_SRxD_se_g  = _se[SR_x_D]
local dir_SRxDxH_g   = _b[SR_x_D_x_Heat]
local dir_SRxDxH_se_g = _se[SR_x_D_x_Heat]
local r2_dir_g = e(r2)

* B4. Sobel
local ind_d_g = `a_SRxD_g' * `lam_g'
local sobel_d_g = sqrt((`a_SRxD_g')^2 * (`lam_se_g')^2 + ///
	(`lam_g')^2 * (`a_SRxD_se_g')^2)

local ind_t_g = `a_SRxDxH_g' * `lam_g'
local sobel_t_g = sqrt((`a_SRxDxH_g')^2 * (`lam_se_g')^2 + ///
	(`lam_g')^2 * (`a_SRxDxH_se_g')^2)

di _n "=== GRID FE: Drought-Water Path (SR×D) ==="
di "Total:    " %10.6f `total_SRxD_g'
di "Direct:   " %10.6f `dir_SRxD_g'
di "Indirect: " %10.6f `ind_d_g' " (Sobel SE=" %9.6f `sobel_d_g' ")"

di _n "=== GRID FE: Compound-Water Path (SR×D×H) ==="
di "Total:    " %10.6f `total_SRxDxH_g'
di "Direct:   " %10.6f `dir_SRxDxH_g'
di "Indirect: " %10.6f `ind_t_g' " (Sobel SE=" %9.6f `sobel_t_g' ")"


* =============================================================================
* 4. EXPORT POINT ESTIMATES + SOBEL
* =============================================================================

* --- Primary mediation table ---
tempname fh
file open `fh' using "$outdir/step4v2_mediation_primary.csv", write replace

* Header
file write `fh' "path,FE,component,b,se,p,N,r2" _n

* --- County FE: Drought path ---
file write `fh' "drought,county,total_SRxD,"         %10.6f (`total_SRxD_c') ","  %10.6f (`total_SRxD_se_c') ",," (`N_c') "," %6.4f (`r2_total_c') _n
file write `fh' "drought,county,a_path_SRxD,"         %10.6f (`a_SRxD_c') ","       %10.6f (`a_SRxD_se_c') ","   %6.4f (`a_SRxD_p_c') ",,," _n
file write `fh' "drought,county,lambda_SM,"            %10.6f (`lam_c') ","          %10.6f (`lam_se_c') ","      %6.4f (`lam_p_c') ",,," _n
file write `fh' "drought,county,direct_SRxD,"          %10.6f (`dir_SRxD_c') ","     %10.6f (`dir_SRxD_se_c') ",," (`N_c') "," %6.4f (`r2_dir_c') _n
file write `fh' "drought,county,indirect_sobel_SRxD,"  %10.6f (`ind_d_c') ","        %10.6f (`sobel_d_c') ",,,,," _n

* --- County FE: Compound path ---
file write `fh' "compound,county,total_SRxDxH,"        %10.6f (`total_SRxDxH_c') "," %10.6f (`total_SRxDxH_se_c') ",," (`N_c') "," %6.4f (`r2_total_c') _n
file write `fh' "compound,county,a_path_SRxDxH,"       %10.6f (`a_SRxDxH_c') ","     %10.6f (`a_SRxDxH_se_c') "," %6.4f (`a_SRxDxH_p_c') ",,," _n
file write `fh' "compound,county,lambda_SM,"            %10.6f (`lam_c') ","          %10.6f (`lam_se_c') ","      %6.4f (`lam_p_c') ",,," _n
file write `fh' "compound,county,direct_SRxDxH,"        %10.6f (`dir_SRxDxH_c') ","   %10.6f (`dir_SRxDxH_se_c') ",," (`N_c') "," %6.4f (`r2_dir_c') _n
file write `fh' "compound,county,indirect_sobel_SRxDxH," %10.6f (`ind_t_c') ","       %10.6f (`sobel_t_c') ",,,,," _n

* --- Grid FE: Drought path ---
file write `fh' "drought,grid,total_SRxD,"              %10.6f (`total_SRxD_g') ","   %10.6f (`total_SRxD_se_g') ",," (`N_g') "," %6.4f (`r2_total_g') _n
file write `fh' "drought,grid,a_path_SRxD,"              %10.6f (`a_SRxD_g') ","      %10.6f (`a_SRxD_se_g') ","   %6.4f (`a_SRxD_p_g') ",,," _n
file write `fh' "drought,grid,lambda_SM,"                 %10.6f (`lam_g') ","         %10.6f (`lam_se_g') ","      %6.4f (`lam_p_g') ",,," _n
file write `fh' "drought,grid,direct_SRxD,"               %10.6f (`dir_SRxD_g') ","    %10.6f (`dir_SRxD_se_g') ",," (`N_g') "," %6.4f (`r2_dir_g') _n
file write `fh' "drought,grid,indirect_sobel_SRxD,"       %10.6f (`ind_d_g') ","       %10.6f (`sobel_d_g') ",,,,," _n

* --- Grid FE: Compound path ---
file write `fh' "compound,grid,total_SRxDxH,"             %10.6f (`total_SRxDxH_g') "," %10.6f (`total_SRxDxH_se_g') ",," (`N_g') "," %6.4f (`r2_total_g') _n
file write `fh' "compound,grid,a_path_SRxDxH,"            %10.6f (`a_SRxDxH_g') ","    %10.6f (`a_SRxDxH_se_g') "," %6.4f (`a_SRxDxH_p_g') ",,," _n
file write `fh' "compound,grid,lambda_SM,"                 %10.6f (`lam_g') ","         %10.6f (`lam_se_g') ","      %6.4f (`lam_p_g') ",,," _n
file write `fh' "compound,grid,direct_SRxDxH,"             %10.6f (`dir_SRxDxH_g') "," %10.6f (`dir_SRxDxH_se_g') ",," (`N_g') "," %6.4f (`r2_dir_g') _n
file write `fh' "compound,grid,indirect_sobel_SRxDxH,"     %10.6f (`ind_t_g') ","      %10.6f (`sobel_t_g') ",,,,," _n

file close `fh'
di "Exported: step4v2_mediation_primary.csv"


* =============================================================================
* 5. CLUSTER BOOTSTRAP — COUNTY FE (PRIMARY)
* =============================================================================
di _n "============================================================"
di "PART C: Cluster Bootstrap — County FE, 1000 reps"
di "============================================================"

* Prepare bootstrap results file
tempfile bootresults
tempname memhold
postfile `memhold' rep double(ind_drought ind_compound a_drought a_compound lambda) ///
	using `bootresults', replace

* Save filtered data to tempfile (avoids nested preserve)
preserve
keep if med_sample_cty == 1
tempfile meddata_cty
save `meddata_cty'
restore

local B = 1000
local dot_interval = 50

di "Starting `B' bootstrap replications..."
di "Each dot = `dot_interval' replications"

forvalues b = 1/`B' {
	if mod(`b', `dot_interval') == 0 {
		di "." _continue
	}
	if mod(`b', 500) == 0 {
		di " `b'"
	}

	preserve
	use `meddata_cty', clear
	bsample, cluster(county_id)

	* Mediator equation
	cap reghdfe gleam_sms_mean D_season W_season hdd_tmax_ge32 ca ///
		SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat ///
		irr_frac pre_sum et0_sum wd_aridity_et0divpre gdd_30 ///
		clay_0_5cm_01deg sand_0_5cm_01deg bdod_0_5cm_01deg ///
		phh2o_0_5cm_01deg silt_0_5cm_01deg, ///
		absorb(county_id year)
	if _rc == 0 {
		local ba = _b[SR_x_D]
		local ba2 = _b[SR_x_D_x_Heat]
	}
	else {
		local ba = .
		local ba2 = .
	}

	* Outcome equation with mediator
	cap reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca ///
		SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat ///
		gleam_sms_mean ///
		irr_frac pre_sum et0_sum wd_aridity_et0divpre gdd_30 ///
		clay_0_5cm_01deg sand_0_5cm_01deg bdod_0_5cm_01deg ///
		phh2o_0_5cm_01deg silt_0_5cm_01deg, ///
		absorb(county_id year)
	if _rc == 0 {
		local blam = _b[gleam_sms_mean]
	}
	else {
		local blam = .
	}

	local bind_d = `ba' * `blam'
	local bind_t = `ba2' * `blam'

	post `memhold' (`b') (`bind_d') (`bind_t') (`ba') (`ba2') (`blam')

	restore
}

di _n "Bootstrap complete."

postclose `memhold'

* --- Extract percentile CIs ---
preserve
use `bootresults', clear

* Drop failed replications
drop if missing(ind_drought) | missing(ind_compound)
local B_valid = _N
di "Valid bootstrap replications: `B_valid' / `B'"

* Drought path CI
_pctile ind_drought, p(2.5 97.5)
local boot_d_lo = r(r1)
local boot_d_hi = r(r2)
sum ind_drought, meanonly
local boot_d_mean = r(mean)
local boot_d_se = r(sd)

* Compound path CI
_pctile ind_compound, p(2.5 97.5)
local boot_t_lo = r(r1)
local boot_t_hi = r(r2)
sum ind_compound, meanonly
local boot_t_mean = r(mean)
local boot_t_se = r(sd)

* Bias-corrected point estimates
di _n "=== BOOTSTRAP RESULTS (County FE) ==="
di "Drought indirect: point=" %10.6f `ind_d_c' " boot_mean=" %10.6f `boot_d_mean' ///
	" boot_SE=" %10.6f `boot_d_se'
di "  95% percentile CI: [" %10.6f `boot_d_lo' ", " %10.6f `boot_d_hi' "]"
di ""
di "Compound indirect: point=" %10.6f `ind_t_c' " boot_mean=" %10.6f `boot_t_mean' ///
	" boot_SE=" %10.6f `boot_t_se'
di "  95% percentile CI: [" %10.6f `boot_t_lo' ", " %10.6f `boot_t_hi' "]"

restore

* --- Append bootstrap CIs to export ---
tempname fh2
file open `fh2' using "$outdir/step4v2_mediation_bootstrap.csv", write replace
file write `fh2' "path,FE,b_indirect,boot_se,ci_lo_p025,ci_hi_p975,B_valid" _n
file write `fh2' "drought,county," %10.6f (`ind_d_c') "," %10.6f (`boot_d_se') ///
	"," %10.6f (`boot_d_lo') "," %10.6f (`boot_d_hi') "," (`B_valid') _n
file write `fh2' "compound,county," %10.6f (`ind_t_c') "," %10.6f (`boot_t_se') ///
	"," %10.6f (`boot_t_lo') "," %10.6f (`boot_t_hi') "," (`B_valid') _n
file close `fh2'
di "Exported: step4v2_mediation_bootstrap.csv"


* =============================================================================
* 6. SUPPORTING MEDIATOR — drydays_gleam_sms_le_basep10
* =============================================================================
di _n "============================================================"
di "PART D: Supporting Mediator (drydays_gleam_sms_le_basep10)"
di "============================================================"

* --- County FE ---
* Mediator equation: drydays = f(RHS)
reghdfe drydays_gleam_sms_le_basep10 $RHS_COMPOUND $SOIL_CTRL ///
	if med_sample_cty == 1, absorb(county_id year) vce(cluster county_id)

local s_a_SRxD_c     = _b[SR_x_D]
local s_a_SRxD_se_c  = _se[SR_x_D]
local s_a_SRxD_p_c   = 2 * ttail(e(df_r), abs(_b[SR_x_D] / _se[SR_x_D]))
local s_a_SRxDxH_c   = _b[SR_x_D_x_Heat]
local s_a_SRxDxH_se_c = _se[SR_x_D_x_Heat]
local s_a_SRxDxH_p_c = 2 * ttail(e(df_r), abs(_b[SR_x_D_x_Heat] / _se[SR_x_D_x_Heat]))

* Outcome equation with drydays
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL drydays_gleam_sms_le_basep10 ///
	if med_sample_cty == 1, absorb(county_id year) vce(cluster county_id)

local s_lam_c     = _b[drydays_gleam_sms_le_basep10]
local s_lam_se_c  = _se[drydays_gleam_sms_le_basep10]
local s_lam_p_c   = 2 * ttail(e(df_r), abs(_b[drydays_gleam_sms_le_basep10] / _se[drydays_gleam_sms_le_basep10]))

* Sobel
local s_ind_d_c = `s_a_SRxD_c' * `s_lam_c'
local s_sobel_d_c = sqrt((`s_a_SRxD_c')^2 * (`s_lam_se_c')^2 + ///
	(`s_lam_c')^2 * (`s_a_SRxD_se_c')^2)

local s_ind_t_c = `s_a_SRxDxH_c' * `s_lam_c'
local s_sobel_t_c = sqrt((`s_a_SRxDxH_c')^2 * (`s_lam_se_c')^2 + ///
	(`s_lam_c')^2 * (`s_a_SRxDxH_se_c')^2)

di "Supporting (drydays, county FE):"
di "  Drought indirect:  " %10.6f `s_ind_d_c'  " (SE=" %10.6f `s_sobel_d_c' ")"
di "  Compound indirect: " %10.6f `s_ind_t_c'  " (SE=" %10.6f `s_sobel_t_c' ")"

* --- Grid FE ---
reghdfe drydays_gleam_sms_le_basep10 $RHS_COMPOUND $SOIL_CTRL ///
	if med_sample_grid == 1, absorb(grid_id year) vce(cluster grid_id)

local s_a_SRxD_g     = _b[SR_x_D]
local s_a_SRxD_se_g  = _se[SR_x_D]
local s_a_SRxD_p_g   = 2 * ttail(e(df_r), abs(_b[SR_x_D] / _se[SR_x_D]))
local s_a_SRxDxH_g   = _b[SR_x_D_x_Heat]
local s_a_SRxDxH_se_g = _se[SR_x_D_x_Heat]
local s_a_SRxDxH_p_g = 2 * ttail(e(df_r), abs(_b[SR_x_D_x_Heat] / _se[SR_x_D_x_Heat]))

reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL drydays_gleam_sms_le_basep10 ///
	if med_sample_grid == 1, absorb(grid_id year) vce(cluster grid_id)

local s_lam_g     = _b[drydays_gleam_sms_le_basep10]
local s_lam_se_g  = _se[drydays_gleam_sms_le_basep10]
local s_lam_p_g   = 2 * ttail(e(df_r), abs(_b[drydays_gleam_sms_le_basep10] / _se[drydays_gleam_sms_le_basep10]))

local s_ind_d_g = `s_a_SRxD_g' * `s_lam_g'
local s_sobel_d_g = sqrt((`s_a_SRxD_g')^2 * (`s_lam_se_g')^2 + ///
	(`s_lam_g')^2 * (`s_a_SRxD_se_g')^2)

local s_ind_t_g = `s_a_SRxDxH_g' * `s_lam_g'
local s_sobel_t_g = sqrt((`s_a_SRxDxH_g')^2 * (`s_lam_se_g')^2 + ///
	(`s_lam_g')^2 * (`s_a_SRxDxH_se_g')^2)

* --- Export supporting mediator ---
tempname fh3
file open `fh3' using "$outdir/step4v2_mediation_supporting.csv", write replace
file write `fh3' "mediator,path,FE,a_path,a_se,a_p,lambda,lambda_se,lambda_p,indirect,sobel_se" _n

file write `fh3' "drydays_sms_p10,drought,county," ///
	%10.6f (`s_a_SRxD_c') "," %10.6f (`s_a_SRxD_se_c') "," %6.4f (`s_a_SRxD_p_c') "," ///
	%10.6f (`s_lam_c') "," %10.6f (`s_lam_se_c') "," %6.4f (`s_lam_p_c') "," ///
	%10.6f (`s_ind_d_c') "," %10.6f (`s_sobel_d_c') _n

file write `fh3' "drydays_sms_p10,compound,county," ///
	%10.6f (`s_a_SRxDxH_c') "," %10.6f (`s_a_SRxDxH_se_c') "," %6.4f (`s_a_SRxDxH_p_c') "," ///
	%10.6f (`s_lam_c') "," %10.6f (`s_lam_se_c') "," %6.4f (`s_lam_p_c') "," ///
	%10.6f (`s_ind_t_c') "," %10.6f (`s_sobel_t_c') _n

file write `fh3' "drydays_sms_p10,drought,grid," ///
	%10.6f (`s_a_SRxD_g') "," %10.6f (`s_a_SRxD_se_g') "," %6.4f (`s_a_SRxD_p_g') "," ///
	%10.6f (`s_lam_g') "," %10.6f (`s_lam_se_g') "," %6.4f (`s_lam_p_g') "," ///
	%10.6f (`s_ind_d_g') "," %10.6f (`s_sobel_d_g') _n

file write `fh3' "drydays_sms_p10,compound,grid," ///
	%10.6f (`s_a_SRxDxH_g') "," %10.6f (`s_a_SRxDxH_se_g') "," %6.4f (`s_a_SRxDxH_p_g') "," ///
	%10.6f (`s_lam_g') "," %10.6f (`s_lam_se_g') "," %6.4f (`s_lam_p_g') "," ///
	%10.6f (`s_ind_t_g') "," %10.6f (`s_sobel_t_g') _n

file close `fh3'
di "Exported: step4v2_mediation_supporting.csv"


* =============================================================================
* 7. LOYO DIAGNOSTICS — Sobel indirect (no bootstrap per year)
* =============================================================================
di _n "============================================================"
di "PART E: Leave-One-Year-Out (Sobel indirect)"
di "============================================================"

tempname fh4
file open `fh4' using "$outdir/step4v2_mediation_loyo.csv", write replace
file write `fh4' "drop_year,mediator,path,FE,a_path,lambda,indirect,sobel_se,N" _n

foreach med in gleam_sms_mean drydays_gleam_sms_le_basep10 {
	local medlabel = cond("`med'" == "gleam_sms_mean", "sms_mean", "drydays_p10")

	forvalues y = 2016/2019 {
		* === County FE ===
		qui reghdfe `med' $RHS_COMPOUND $SOIL_CTRL ///
			if med_sample_cty == 1 & year != `y', ///
			absorb(county_id year) vce(cluster county_id)
		local la_d = _b[SR_x_D]
		local la_t = _b[SR_x_D_x_Heat]
		local la_d_se = _se[SR_x_D]
		local la_t_se = _se[SR_x_D_x_Heat]

		qui reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL `med' ///
			if med_sample_cty == 1 & year != `y', ///
			absorb(county_id year) vce(cluster county_id)
		local llam = _b[`med']
		local llam_se = _se[`med']
		local lN = e(N)

		local lind_d = `la_d' * `llam'
		local lsob_d = sqrt((`la_d')^2 * (`llam_se')^2 + (`llam')^2 * (`la_d_se')^2)
		local lind_t = `la_t' * `llam'
		local lsob_t = sqrt((`la_t')^2 * (`llam_se')^2 + (`llam')^2 * (`la_t_se')^2)

		file write `fh4' "`y',`medlabel',drought,county," ///
			%10.6f (`la_d') "," %10.6f (`llam') "," %10.6f (`lind_d') "," ///
			%10.6f (`lsob_d') "," (`lN') _n
		file write `fh4' "`y',`medlabel',compound,county," ///
			%10.6f (`la_t') "," %10.6f (`llam') "," %10.6f (`lind_t') "," ///
			%10.6f (`lsob_t') "," (`lN') _n

		* === Grid FE ===
		qui reghdfe `med' $RHS_COMPOUND $SOIL_CTRL ///
			if med_sample_grid == 1 & year != `y', ///
			absorb(grid_id year) vce(cluster grid_id)
		local la_d = _b[SR_x_D]
		local la_t = _b[SR_x_D_x_Heat]
		local la_d_se = _se[SR_x_D]
		local la_t_se = _se[SR_x_D_x_Heat]

		qui reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL `med' ///
			if med_sample_grid == 1 & year != `y', ///
			absorb(grid_id year) vce(cluster grid_id)
		local llam = _b[`med']
		local llam_se = _se[`med']
		local lN = e(N)

		local lind_d = `la_d' * `llam'
		local lsob_d = sqrt((`la_d')^2 * (`llam_se')^2 + (`llam')^2 * (`la_d_se')^2)
		local lind_t = `la_t' * `llam'
		local lsob_t = sqrt((`la_t')^2 * (`llam_se')^2 + (`llam')^2 * (`la_t_se')^2)

		file write `fh4' "`y',`medlabel',drought,grid," ///
			%10.6f (`la_d') "," %10.6f (`llam') "," %10.6f (`lind_d') "," ///
			%10.6f (`lsob_d') "," (`lN') _n
		file write `fh4' "`y',`medlabel',compound,grid," ///
			%10.6f (`la_t') "," %10.6f (`llam') "," %10.6f (`lind_t') "," ///
			%10.6f (`lsob_t') "," (`lN') _n

		di "LOYO drop `y', `medlabel': done"
	}
}

file close `fh4'
di "Exported: step4v2_mediation_loyo.csv"


* =============================================================================
* 8. SUMMARY
* =============================================================================
di _n "============================================================"
di "SUMMARY: Formal Single-Channel Mediation"
di "============================================================"
di ""
di "Primary Mediator: gleam_sms_mean (surface SM)"
di "Supporting Mediator: drydays_gleam_sms_le_basep10 (surface dry days)"
di ""
di "--- County FE ---"
di "Drought path (SR×D):"
di "  a-path (SR×D→SM):   " %10.6f `a_SRxD_c' " (p=" %5.3f `a_SRxD_p_c' ")"
di "  lambda (SM→Yield):  " %10.6f `lam_c' " (p=" %5.3f `lam_p_c' ")"
di "  Total:              " %10.6f `total_SRxD_c'
di "  Direct:             " %10.6f `dir_SRxD_c'
di "  Indirect (Sobel):   " %10.6f `ind_d_c' " ± " %10.6f `sobel_d_c'
di "  Bootstrap 95% CI:   [" %10.6f `boot_d_lo' ", " %10.6f `boot_d_hi' "]"
di ""
di "Compound path (SR×D×H):"
di "  a-path (SR×D×H→SM): " %10.6f `a_SRxDxH_c' " (p=" %5.3f `a_SRxDxH_p_c' ")"
di "  lambda (SM→Yield):  " %10.6f `lam_c' " (p=" %5.3f `lam_p_c' ")"
di "  Total:              " %10.6f `total_SRxDxH_c'
di "  Direct:             " %10.6f `dir_SRxDxH_c'
di "  Indirect (Sobel):   " %10.6f `ind_t_c' " ± " %10.6f `sobel_t_c'
di "  Bootstrap 95% CI:   [" %10.6f `boot_t_lo' ", " %10.6f `boot_t_hi' "]"
di ""
di "--- Grid FE ---"
di "Drought indirect:    " %10.6f `ind_d_g' " (Sobel SE=" %10.6f `sobel_d_g' ")"
di "Compound indirect:   " %10.6f `ind_t_g' " (Sobel SE=" %10.6f `sobel_t_g' ")"
di ""
di "--- Supporting: drydays_sms_p10 ---"
di "County FE drought:   " %10.6f `s_ind_d_c'
di "County FE compound:  " %10.6f `s_ind_t_c'
di "Grid FE drought:     " %10.6f `s_ind_d_g'
di "Grid FE compound:    " %10.6f `s_ind_t_g'
di ""
di "Output files:"
di "  $outdir/step4v2_mediation_primary.csv"
di "  $outdir/step4v2_mediation_bootstrap.csv"
di "  $outdir/step4v2_mediation_supporting.csv"
di "  $outdir/step4v2_mediation_loyo.csv"

log close
