* =============================================================================
* step_moderated_mediation.do — Moderated Mediation Analysis
* Purpose: Apply Preacher (2007) and Muller et al. (2005) frameworks to test
*          whether SR moderates the indirect pathway D → SM → Yield.
*          Model 2: SR moderates a-path (D→SM)
*          Model 5: SR moderates both a-path (D→SM) and b-path (SM→Y)
*          Extensions: compound stress (D×H), supporting mediator (drydays)
* Author: YangSu / Claude Code
* Date: 2026-03-23
* Dependencies: analysis_main_sample.dta (from step0), reghdfe
* References: Preacher, Rucker & Hayes (2007); Muller, Judd & Yzerbyt (2005)
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
global figdir  "$projdir/output/figures"

* Controls — hardcoded
global CTRL irr_frac pre_sum et0_sum wd_aridity_et0divpre gdd_30
global SOIL_CTRL clay_0_5cm_01deg sand_0_5cm_01deg bdod_0_5cm_01deg ///
	phh2o_0_5cm_01deg silt_0_5cm_01deg

* Full compound model RHS (without mediator)
global RHS_COMPOUND D_season W_season hdd_tmax_ge32 ca ///
	SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat $CTRL

cap log close
log using "$logdir/step_moderated_mediation_20260323.log", replace

di "============================================================"
di "step_moderated_mediation.do — Moderated Mediation Analysis"
di "Preacher (2007) + Muller et al. (2005)"
di "Date: $S_DATE $S_TIME"
di "============================================================"

* Load data
use "$projdir/data/processed/analysis_main_sample.dta", clear
cap drop __*
xtset grid_id year

* =============================================================================
* 1. SAMPLE DEFINITION + NEW VARIABLE GENERATION
* =============================================================================

* 1a. County FE mediation sample
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL if main_sample == 1, ///
	absorb(county_id year) vce(cluster county_id)
gen med_sample_cty = e(sample)
replace med_sample_cty = 0 if missing(gleam_sms_mean)
replace med_sample_cty = 0 if missing(drydays_gleam_sms_le_basep10)

count if med_sample_cty == 1
local N_med_cty = r(N)
di "Mediation sample (county FE): N = `N_med_cty'"

* 1b. Grid FE mediation sample
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL gleam_sms_mean if main_sample == 1, ///
	absorb(grid_id year) vce(cluster grid_id)
gen med_sample_grid = e(sample)
replace med_sample_grid = 0 if missing(drydays_gleam_sms_le_basep10)

count if med_sample_grid == 1
local N_med_grid = r(N)
di "Mediation sample (grid FE): N = `N_med_grid'"

* 1c. Generate interaction terms for Model 5
cap drop SM_x_SR
gen SM_x_SR = gleam_sms_mean * ca
label var SM_x_SR "SM_surface x SR (Model 5 b-path moderation)"

cap drop drydays_x_SR
gen drydays_x_SR = drydays_gleam_sms_le_basep10 * ca
label var drydays_x_SR "DryDays x SR (Model 5 b-path moderation)"

* 1d. SR percentiles on county sample
_pctile ca if med_sample_cty == 1, p(10 25 50 75 90)
local sr_p10 = r(r1)
local sr_p25 = r(r2)
local sr_p50 = r(r3)
local sr_p75 = r(r4)
local sr_p90 = r(r5)

di _n "SR percentiles on county FE sample:"
di "  P10 = " %6.4f `sr_p10'
di "  P25 = " %6.4f `sr_p25'
di "  P50 = " %6.4f `sr_p50'
di "  P75 = " %6.4f `sr_p75'
di "  P90 = " %6.4f `sr_p90'

* Also compute on grid sample
_pctile ca if med_sample_grid == 1, p(10 25 50 75 90)
local sr_g_p10 = r(r1)
local sr_g_p25 = r(r2)
local sr_g_p50 = r(r3)
local sr_g_p75 = r(r4)
local sr_g_p90 = r(r5)


* =============================================================================
* 2. PART A: MULLER ET AL. (2005) THREE-STEP DIAGNOSTIC
* =============================================================================
di _n "============================================================"
di "PART A: Muller et al. (2005) Three-Step Diagnostic"
di "============================================================"

* Open output CSV
tempname fh_muller
file open `fh_muller' using "$outdir/step_muller_3step.csv", write replace
file write `fh_muller' "step,FE,variable,b,se,p,N,r2" _n

* --- County FE ---
di _n "--- County + Year FE ---"

* Step 1: Total effect (no mediator)
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL if med_sample_cty == 1, ///
	absorb(county_id year) vce(cluster county_id)
local s1_SRxD_b = _b[SR_x_D]
local s1_SRxD_se = _se[SR_x_D]
local s1_SRxD_p = 2*ttail(e(df_r), abs(`s1_SRxD_b'/`s1_SRxD_se'))
local s1_SRxDxH_b = _b[SR_x_D_x_Heat]
local s1_SRxDxH_se = _se[SR_x_D_x_Heat]
local s1_SRxDxH_p = 2*ttail(e(df_r), abs(`s1_SRxDxH_b'/`s1_SRxDxH_se'))
local s1_N = e(N)
local s1_r2 = e(r2)
di "Step 1 (Total): SR_x_D = " %10.6f `s1_SRxD_b' " (" %8.6f `s1_SRxD_se' ") p=" %6.4f `s1_SRxD_p'
file write `fh_muller' "1_total,county,SR_x_D," %12.8f (`s1_SRxD_b') "," ///
	%12.8f (`s1_SRxD_se') "," %8.6f (`s1_SRxD_p') "," (`s1_N') "," %8.6f (`s1_r2') _n
file write `fh_muller' "1_total,county,SR_x_D_x_Heat," %12.8f (`s1_SRxDxH_b') "," ///
	%12.8f (`s1_SRxDxH_se') "," %8.6f (`s1_SRxDxH_p') "," (`s1_N') "," %8.6f (`s1_r2') _n

* Step 2: Mediator equation (SM = f(D, SR, D×SR, ...))
reghdfe gleam_sms_mean $RHS_COMPOUND $SOIL_CTRL if med_sample_cty == 1, ///
	absorb(county_id year) vce(cluster county_id)
local a1_c = _b[D_season]
local a1_se_c = _se[D_season]
local a1_p_c = 2*ttail(e(df_r), abs(`a1_c'/`a1_se_c'))
local a2_c = _b[ca]
local a2_se_c = _se[ca]
local a3_c = _b[SR_x_D]
local a3_se_c = _se[SR_x_D]
local a3_p_c = 2*ttail(e(df_r), abs(`a3_c'/`a3_se_c'))
local a1c_c = _b[D_x_Heat]
local a1c_se_c = _se[D_x_Heat]
local a3c_c = _b[SR_x_D_x_Heat]
local a3c_se_c = _se[SR_x_D_x_Heat]
local a3c_p_c = 2*ttail(e(df_r), abs(`a3c_c'/`a3c_se_c'))
local s2_N = e(N)
local s2_r2 = e(r2)

* Extract cov(a1, a3) from V matrix
matrix V_med_c = e(V)
local cov_a1_a3_c = V_med_c["D_season", "SR_x_D"]
local cov_a1c_a3c_c = V_med_c["D_x_Heat", "SR_x_D_x_Heat"]

di "Step 2 (Mediator): a1(D)=" %10.6f `a1_c' " a3(SR_x_D)=" %10.6f `a3_c' " p=" %6.4f `a3_p_c'
di "  a1c(DxH)=" %12.8f `a1c_c' " a3c(SRxDxH)=" %12.8f `a3c_c' " p=" %6.4f `a3c_p_c'

file write `fh_muller' "2_mediator,county,D_season," %12.8f (`a1_c') "," ///
	%12.8f (`a1_se_c') "," %8.6f (`a1_p_c') "," (`s2_N') "," %8.6f (`s2_r2') _n
file write `fh_muller' "2_mediator,county,ca," %12.8f (`a2_c') "," ///
	%12.8f (`a2_se_c') "," %8.6f (2*ttail(e(df_r), abs(`a2_c'/`a2_se_c'))) "," (`s2_N') "," %8.6f (`s2_r2') _n
file write `fh_muller' "2_mediator,county,SR_x_D," %12.8f (`a3_c') "," ///
	%12.8f (`a3_se_c') "," %8.6f (`a3_p_c') "," (`s2_N') "," %8.6f (`s2_r2') _n
file write `fh_muller' "2_mediator,county,D_x_Heat," %12.8f (`a1c_c') "," ///
	%12.8f (`a1c_se_c') "," %8.6f (2*ttail(e(df_r), abs(`a1c_c'/`a1c_se_c'))) "," (`s2_N') "," %8.6f (`s2_r2') _n
file write `fh_muller' "2_mediator,county,SR_x_D_x_Heat," %12.8f (`a3c_c') "," ///
	%12.8f (`a3c_se_c') "," %8.6f (`a3c_p_c') "," (`s2_N') "," %8.6f (`s2_r2') _n

* Step 3: Outcome with mediator + SM×SR (Model 5 test)
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL gleam_sms_mean SM_x_SR ///
	if med_sample_cty == 1, absorb(county_id year) vce(cluster county_id)
local b1_c = _b[gleam_sms_mean]
local b1_se_c = _se[gleam_sms_mean]
local b1_p_c = 2*ttail(e(df_r), abs(`b1_c'/`b1_se_c'))
local b5_c = _b[SM_x_SR]
local b5_se_c = _se[SM_x_SR]
local b5_p_c = 2*ttail(e(df_r), abs(`b5_c'/`b5_se_c'))
local s3_SRxD_b = _b[SR_x_D]
local s3_SRxD_se = _se[SR_x_D]
local s3_SRxD_p = 2*ttail(e(df_r), abs(`s3_SRxD_b'/`s3_SRxD_se'))
local s3_N = e(N)
local s3_r2 = e(r2)

* Also get b1 variance for delta-method
local var_b1_c = `b1_se_c'^2
local var_b5_c = `b5_se_c'^2
matrix V_out_c = e(V)
local cov_b1_b5_c = V_out_c["gleam_sms_mean", "SM_x_SR"]

di "Step 3 (Full): b1(SM)=" %10.6f `b1_c' " p=" %6.4f `b1_p_c'
di "  b5(SM_x_SR)=" %10.6f `b5_c' " p=" %6.4f `b5_p_c'
di "  Direct SR_x_D=" %10.6f `s3_SRxD_b' " (total=" %10.6f `s1_SRxD_b' ")"
di "  Attenuation = " %6.2f ((`s1_SRxD_b' - `s3_SRxD_b')/`s1_SRxD_b' * 100) "%"

file write `fh_muller' "3_full,county,gleam_sms_mean," %12.8f (`b1_c') "," ///
	%12.8f (`b1_se_c') "," %8.6f (`b1_p_c') "," (`s3_N') "," %8.6f (`s3_r2') _n
file write `fh_muller' "3_full,county,SM_x_SR," %12.8f (`b5_c') "," ///
	%12.8f (`b5_se_c') "," %8.6f (`b5_p_c') "," (`s3_N') "," %8.6f (`s3_r2') _n
file write `fh_muller' "3_full,county,SR_x_D," %12.8f (`s3_SRxD_b') "," ///
	%12.8f (`s3_SRxD_se') "," %8.6f (`s3_SRxD_p') "," (`s3_N') "," %8.6f (`s3_r2') _n

* --- Grid FE (repeat) ---
di _n "--- Grid + Year FE ---"

* Step 1
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL if med_sample_grid == 1, ///
	absorb(grid_id year) vce(cluster grid_id)
local gs1_SRxD = _b[SR_x_D]
local gs1_N = e(N)
local gs1_r2 = e(r2)
file write `fh_muller' "1_total,grid,SR_x_D," %12.8f (_b[SR_x_D]) "," ///
	%12.8f (_se[SR_x_D]) "," %8.6f (2*ttail(e(df_r), abs(_b[SR_x_D]/_se[SR_x_D]))) ///
	"," (e(N)) "," %8.6f (e(r2)) _n

* Step 2
reghdfe gleam_sms_mean $RHS_COMPOUND $SOIL_CTRL if med_sample_grid == 1, ///
	absorb(grid_id year) vce(cluster grid_id)
local a1_g = _b[D_season]
local a1_se_g = _se[D_season]
local a3_g = _b[SR_x_D]
local a3_se_g = _se[SR_x_D]
local a3_p_g = 2*ttail(e(df_r), abs(`a3_g'/`a3_se_g'))
local a1c_g = _b[D_x_Heat]
local a3c_g = _b[SR_x_D_x_Heat]
local a3c_se_g = _se[SR_x_D_x_Heat]
matrix V_med_g = e(V)
local cov_a1_a3_g = V_med_g["D_season", "SR_x_D"]

file write `fh_muller' "2_mediator,grid,D_season," %12.8f (`a1_g') "," ///
	%12.8f (`a1_se_g') "," %8.6f (2*ttail(e(df_r), abs(`a1_g'/`a1_se_g'))) ///
	"," (e(N)) "," %8.6f (e(r2)) _n
file write `fh_muller' "2_mediator,grid,SR_x_D," %12.8f (`a3_g') "," ///
	%12.8f (`a3_se_g') "," %8.6f (`a3_p_g') "," (e(N)) "," %8.6f (e(r2)) _n

* Step 3
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL gleam_sms_mean SM_x_SR ///
	if med_sample_grid == 1, absorb(grid_id year) vce(cluster grid_id)
local b1_g = _b[gleam_sms_mean]
local b1_se_g = _se[gleam_sms_mean]
local b1_p_g = 2*ttail(e(df_r), abs(`b1_g'/`b1_se_g'))
local b5_g = _b[SM_x_SR]
local b5_se_g = _se[SM_x_SR]
local b5_p_g = 2*ttail(e(df_r), abs(`b5_g'/`b5_se_g'))
local var_b1_g = `b1_se_g'^2
matrix V_out_g = e(V)
local cov_b1_b5_g = V_out_g["gleam_sms_mean", "SM_x_SR"]

file write `fh_muller' "3_full,grid,gleam_sms_mean," %12.8f (`b1_g') "," ///
	%12.8f (`b1_se_g') "," %8.6f (`b1_p_g') "," (e(N)) "," %8.6f (e(r2)) _n
file write `fh_muller' "3_full,grid,SM_x_SR," %12.8f (`b5_g') "," ///
	%12.8f (`b5_se_g') "," %8.6f (`b5_p_g') "," (e(N)) "," %8.6f (e(r2)) _n
file write `fh_muller' "3_full,grid,SR_x_D," %12.8f (_b[SR_x_D]) "," ///
	%12.8f (_se[SR_x_D]) "," %8.6f (2*ttail(e(df_r), abs(_b[SR_x_D]/_se[SR_x_D]))) ///
	"," (e(N)) "," %8.6f (e(r2)) _n

file close `fh_muller'
di _n "Exported: step_muller_3step.csv"


* =============================================================================
* 3. PART B: PREACHER MODEL 2 — CONDITIONAL INDIRECT EFFECTS
* =============================================================================
di _n "============================================================"
di "PART B: Preacher Model 2 — W moderates a-path"
di "============================================================"

* Model 2 uses b1 from outcome eq WITHOUT SM_x_SR
* County FE: re-estimate outcome without SM_x_SR
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL gleam_sms_mean ///
	if med_sample_cty == 1, absorb(county_id year) vce(cluster county_id)
local b1_m2_c = _b[gleam_sms_mean]
local b1_m2_se_c = _se[gleam_sms_mean]
local var_b1_m2_c = `b1_m2_se_c'^2

di "Model 2 (County FE): b1 = " %10.6f `b1_m2_c' " (" %8.6f `b1_m2_se_c' ")"
di "  a1(D_season) = " %10.6f `a1_c' ", a3(SR_x_D) = " %10.6f `a3_c'

* Compute IMM (Index of Moderated Mediation) = a3 * b1
local IMM_drought_c = `a3_c' * `b1_m2_c'
local IMM_se_c = sqrt((`a3_c')^2 * `var_b1_m2_c' + (`b1_m2_c')^2 * (`a3_se_c')^2)
local IMM_z_c = `IMM_drought_c' / `IMM_se_c'
local IMM_p_c = 2 * normal(-abs(`IMM_z_c'))

di _n "=== INDEX OF MODERATED MEDIATION (Drought, County FE) ==="
di "  IMM = a3 * b1 = " %12.8f `IMM_drought_c' " (SE=" %10.8f `IMM_se_c' " p=" %6.4f `IMM_p_c' ")"

* Open output CSV
tempname fh_m2
file open `fh_m2' using "$outdir/step_preacher_model2.csv", write replace
file write `fh_m2' "path,FE,sr_pctl,sr_value,cond_indirect,delta_se,ci_lo,ci_hi,a1,a3,b1,IMM,IMM_se,IMM_p" _n

* Conditional indirect at each SR percentile — Drought path
foreach pctl in p10 p25 p50 p75 p90 {
	local w = `sr_`pctl''
	local ci = `b1_m2_c' * (`a1_c' + `a3_c' * `w')
	* Delta-method SE
	local var_ci = (`a1_c' + `a3_c' * `w')^2 * `var_b1_m2_c' + ///
		(`b1_m2_c')^2 * ((`a1_se_c')^2 + (`w')^2 * (`a3_se_c')^2 + ///
		2 * `w' * `cov_a1_a3_c')
	local se_ci = sqrt(max(`var_ci', 0))
	local lo_ci = `ci' - 1.96 * `se_ci'
	local hi_ci = `ci' + 1.96 * `se_ci'

	di "`pctl' (SR=" %6.4f `w' "): theta=" %12.8f `ci' " SE=" %10.8f `se_ci' ///
		" CI=[" %12.8f `lo_ci' "," %12.8f `hi_ci' "]"

	file write `fh_m2' "drought,county,`pctl'," %8.6f (`w') "," %12.8f (`ci') "," ///
		%12.8f (`se_ci') "," %12.8f (`lo_ci') "," %12.8f (`hi_ci') "," ///
		%12.8f (`a1_c') "," %12.8f (`a3_c') "," %12.8f (`b1_m2_c') "," ///
		%12.8f (`IMM_drought_c') "," %12.8f (`IMM_se_c') "," %8.6f (`IMM_p_c') _n
}

* Compound path conditional indirect
local IMM_comp_c = `a3c_c' * `b1_m2_c'
local IMM_comp_se_c = sqrt((`a3c_c')^2 * `var_b1_m2_c' + (`b1_m2_c')^2 * (`a3c_se_c')^2)
local IMM_comp_p_c = 2 * normal(-abs(`IMM_comp_c' / `IMM_comp_se_c'))

di _n "=== INDEX OF MODERATED MEDIATION (Compound, County FE) ==="
di "  IMM_compound = a3c * b1 = " %12.8f `IMM_comp_c'

foreach pctl in p10 p25 p50 p75 p90 {
	local w = `sr_`pctl''
	local ci = `b1_m2_c' * (`a1c_c' + `a3c_c' * `w')
	local var_ci = (`a1c_c' + `a3c_c' * `w')^2 * `var_b1_m2_c' + ///
		(`b1_m2_c')^2 * ((`a1c_se_c')^2 + (`w')^2 * (`a3c_se_c')^2 + ///
		2 * `w' * `cov_a1c_a3c_c')
	local se_ci = sqrt(max(`var_ci', 0))
	local lo_ci = `ci' - 1.96 * `se_ci'
	local hi_ci = `ci' + 1.96 * `se_ci'

	file write `fh_m2' "compound,county,`pctl'," %8.6f (`w') "," %12.8f (`ci') "," ///
		%12.8f (`se_ci') "," %12.8f (`lo_ci') "," %12.8f (`hi_ci') "," ///
		%12.8f (`a1c_c') "," %12.8f (`a3c_c') "," %12.8f (`b1_m2_c') "," ///
		%12.8f (`IMM_comp_c') "," %12.8f (`IMM_comp_se_c') "," %8.6f (`IMM_comp_p_c') _n
}

* --- Grid FE ---
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL gleam_sms_mean ///
	if med_sample_grid == 1, absorb(grid_id year) vce(cluster grid_id)
local b1_m2_g = _b[gleam_sms_mean]
local b1_m2_se_g = _se[gleam_sms_mean]
local var_b1_m2_g = `b1_m2_se_g'^2

local IMM_drought_g = `a3_g' * `b1_m2_g'
local IMM_se_g = sqrt((`a3_g')^2 * `var_b1_m2_g' + (`b1_m2_g')^2 * (`a3_se_g')^2)
local IMM_p_g = 2 * normal(-abs(`IMM_drought_g' / `IMM_se_g'))

di _n "=== Grid FE: IMM_drought = " %12.8f `IMM_drought_g' " (p=" %6.4f `IMM_p_g' ")"

foreach pctl in p10 p25 p50 p75 p90 {
	local w = `sr_g_`pctl''
	local ci = `b1_m2_g' * (`a1_g' + `a3_g' * `w')
	local var_ci = (`a1_g' + `a3_g' * `w')^2 * `var_b1_m2_g' + ///
		(`b1_m2_g')^2 * ((`a1_se_g')^2 + (`w')^2 * (`a3_se_g')^2 + ///
		2 * `w' * `cov_a1_a3_g')
	local se_ci = sqrt(max(`var_ci', 0))
	local lo_ci = `ci' - 1.96 * `se_ci'
	local hi_ci = `ci' + 1.96 * `se_ci'

	file write `fh_m2' "drought,grid,`pctl'," %8.6f (`w') "," %12.8f (`ci') "," ///
		%12.8f (`se_ci') "," %12.8f (`lo_ci') "," %12.8f (`hi_ci') "," ///
		%12.8f (`a1_g') "," %12.8f (`a3_g') "," %12.8f (`b1_m2_g') "," ///
		%12.8f (`IMM_drought_g') "," %12.8f (`IMM_se_g') "," %8.6f (`IMM_p_g') _n
}

file close `fh_m2'
di "Exported: step_preacher_model2.csv"


* =============================================================================
* 4. PART C: PREACHER MODEL 5 — W MODERATES BOTH PATHS
* =============================================================================
di _n "============================================================"
di "PART C: Preacher Model 5 — W moderates a-path AND b-path"
di "============================================================"

tempname fh_m5
file open `fh_m5' using "$outdir/step_preacher_model5.csv", write replace
file write `fh_m5' "path,FE,sr_pctl,sr_value,cond_indirect,b1,b5,b5_p,model_preferred" _n

* Model 5 outcome eq (County FE) — already have b1_c, b5_c from Muller Step 3
di "Model 5 (County FE): b1=" %10.6f `b1_c' " b5(SM_x_SR)=" %10.6f `b5_c' " p=" %6.4f `b5_p_c'
local model_pref_c = cond(`b5_p_c' < 0.10, "Model5", "Model2")
di "  Preferred model: `model_pref_c'"

* Drought path conditional indirect: (a1 + a3*w) * (b1 + b5*w)
foreach pctl in p10 p25 p50 p75 p90 {
	local w = `sr_`pctl''
	local apath = `a1_c' + `a3_c' * `w'
	local bpath = `b1_c' + `b5_c' * `w'
	local ci = `apath' * `bpath'

	file write `fh_m5' "drought,county,`pctl'," %8.6f (`w') "," %12.8f (`ci') "," ///
		%12.8f (`b1_c') "," %12.8f (`b5_c') "," %8.6f (`b5_p_c') ",`model_pref_c'" _n
}

* Compound path
foreach pctl in p10 p25 p50 p75 p90 {
	local w = `sr_`pctl''
	local apath = `a1c_c' + `a3c_c' * `w'
	local bpath = `b1_c' + `b5_c' * `w'
	local ci = `apath' * `bpath'

	file write `fh_m5' "compound,county,`pctl'," %8.6f (`w') "," %12.8f (`ci') "," ///
		%12.8f (`b1_c') "," %12.8f (`b5_c') "," %8.6f (`b5_p_c') ",`model_pref_c'" _n
}

* Grid FE Model 5
local model_pref_g = cond(`b5_p_g' < 0.10, "Model5", "Model2")
di _n "Model 5 (Grid FE): b1=" %10.6f `b1_g' " b5=" %10.6f `b5_g' " p=" %6.4f `b5_p_g'
di "  Preferred: `model_pref_g'"

foreach pctl in p10 p25 p50 p75 p90 {
	local w = `sr_g_`pctl''
	local apath = `a1_g' + `a3_g' * `w'
	local bpath = `b1_g' + `b5_g' * `w'
	local ci = `apath' * `bpath'

	file write `fh_m5' "drought,grid,`pctl'," %8.6f (`w') "," %12.8f (`ci') "," ///
		%12.8f (`b1_g') "," %12.8f (`b5_g') "," %8.6f (`b5_p_g') ",`model_pref_g'" _n
}

file close `fh_m5'
di "Exported: step_preacher_model5.csv"


* =============================================================================
* 5. PART D: SUPPORTING MEDIATOR — drydays
* =============================================================================
di _n "============================================================"
di "PART D: Supporting Mediator (drydays_gleam_sms_le_basep10)"
di "============================================================"

tempname fh_dry
file open `fh_dry' using "$outdir/step_preacher_drydays.csv", write replace
file write `fh_dry' "model,path,FE,sr_pctl,sr_value,cond_indirect,delta_se,ci_lo,ci_hi,a1,a3,b1,b5,IMM,IMM_se" _n

* --- County FE ---
* Mediator eq: drydays = f(D, SR, D×SR, ...)
reghdfe drydays_gleam_sms_le_basep10 $RHS_COMPOUND $SOIL_CTRL ///
	if med_sample_cty == 1, absorb(county_id year) vce(cluster county_id)
local da1_c = _b[D_season]
local da1_se_c = _se[D_season]
local da3_c = _b[SR_x_D]
local da3_se_c = _se[SR_x_D]
matrix V_dmed_c = e(V)
local dcov_a1_a3_c = V_dmed_c["D_season", "SR_x_D"]

di "Drydays mediator eq: a1(D)=" %10.4f `da1_c' " a3(SR_x_D)=" %10.4f `da3_c'

* Model 2 outcome with drydays
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL drydays_gleam_sms_le_basep10 ///
	if med_sample_cty == 1, absorb(county_id year) vce(cluster county_id)
local db1_m2_c = _b[drydays_gleam_sms_le_basep10]
local db1_m2_se_c = _se[drydays_gleam_sms_le_basep10]
local dvar_b1_m2_c = `db1_m2_se_c'^2

local dIMM_c = `da3_c' * `db1_m2_c'
local dIMM_se_c = sqrt((`da3_c')^2 * `dvar_b1_m2_c' + (`db1_m2_c')^2 * (`da3_se_c')^2)

di "Model 2 drydays: b1=" %12.8f `db1_m2_c' " IMM=" %12.8f `dIMM_c'

foreach pctl in p10 p25 p50 p75 p90 {
	local w = `sr_`pctl''
	local ci = `db1_m2_c' * (`da1_c' + `da3_c' * `w')
	local var_ci = (`da1_c' + `da3_c' * `w')^2 * `dvar_b1_m2_c' + ///
		(`db1_m2_c')^2 * ((`da1_se_c')^2 + (`w')^2 * (`da3_se_c')^2 + ///
		2 * `w' * `dcov_a1_a3_c')
	local se_ci = sqrt(max(`var_ci', 0))

	file write `fh_dry' "Model2,drought,county,`pctl'," %8.6f (`w') "," ///
		%12.8f (`ci') "," %12.8f (`se_ci') "," ///
		%12.8f (`ci' - 1.96*`se_ci') "," %12.8f (`ci' + 1.96*`se_ci') "," ///
		%12.8f (`da1_c') "," %12.8f (`da3_c') "," %12.8f (`db1_m2_c') ",," ///
		%12.8f (`dIMM_c') "," %12.8f (`dIMM_se_c') _n
}

* Model 5 drydays (+ drydays_x_SR)
reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL drydays_gleam_sms_le_basep10 drydays_x_SR ///
	if med_sample_cty == 1, absorb(county_id year) vce(cluster county_id)
local db1_m5_c = _b[drydays_gleam_sms_le_basep10]
local db5_m5_c = _b[drydays_x_SR]
local db5_m5_se_c = _se[drydays_x_SR]
local db5_m5_p_c = 2*ttail(e(df_r), abs(`db5_m5_c'/`db5_m5_se_c'))

di "Model 5 drydays: b1=" %12.8f `db1_m5_c' " b5=" %12.8f `db5_m5_c' " p=" %6.4f `db5_m5_p_c'

foreach pctl in p10 p25 p50 p75 p90 {
	local w = `sr_`pctl''
	local ci = (`da1_c' + `da3_c' * `w') * (`db1_m5_c' + `db5_m5_c' * `w')

	file write `fh_dry' "Model5,drought,county,`pctl'," %8.6f (`w') "," ///
		%12.8f (`ci') ",,,,," ///
		%12.8f (`da1_c') "," %12.8f (`da3_c') "," %12.8f (`db1_m5_c') "," ///
		%12.8f (`db5_m5_c') ",," _n
}

* --- Grid FE drydays ---
reghdfe drydays_gleam_sms_le_basep10 $RHS_COMPOUND $SOIL_CTRL ///
	if med_sample_grid == 1, absorb(grid_id year) vce(cluster grid_id)
local da1_g = _b[D_season]
local da1_se_g = _se[D_season]
local da3_g = _b[SR_x_D]
local da3_se_g = _se[SR_x_D]
matrix V_dmed_g = e(V)
local dcov_a1_a3_g = V_dmed_g["D_season", "SR_x_D"]

reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL drydays_gleam_sms_le_basep10 ///
	if med_sample_grid == 1, absorb(grid_id year) vce(cluster grid_id)
local db1_m2_g = _b[drydays_gleam_sms_le_basep10]
local db1_m2_se_g = _se[drydays_gleam_sms_le_basep10]
local dvar_b1_m2_g = `db1_m2_se_g'^2

local dIMM_g = `da3_g' * `db1_m2_g'
local dIMM_se_g = sqrt((`da3_g')^2 * `dvar_b1_m2_g' + (`db1_m2_g')^2 * (`da3_se_g')^2)

di _n "Grid FE drydays: b1=" %12.8f `db1_m2_g' " IMM=" %12.8f `dIMM_g'

foreach pctl in p10 p25 p50 p75 p90 {
	local w = `sr_g_`pctl''
	local ci = `db1_m2_g' * (`da1_g' + `da3_g' * `w')
	local var_ci = (`da1_g' + `da3_g' * `w')^2 * `dvar_b1_m2_g' + ///
		(`db1_m2_g')^2 * ((`da1_se_g')^2 + (`w')^2 * (`da3_se_g')^2 + ///
		2 * `w' * `dcov_a1_a3_g')
	local se_ci = sqrt(max(`var_ci', 0))

	file write `fh_dry' "Model2,drought,grid,`pctl'," %8.6f (`w') "," ///
		%12.8f (`ci') "," %12.8f (`se_ci') "," ///
		%12.8f (`ci' - 1.96*`se_ci') "," %12.8f (`ci' + 1.96*`se_ci') "," ///
		%12.8f (`da1_g') "," %12.8f (`da3_g') "," %12.8f (`db1_m2_g') ",," ///
		%12.8f (`dIMM_g') "," %12.8f (`dIMM_se_g') _n
}

file close `fh_dry'
di "Exported: step_preacher_drydays.csv"


* =============================================================================
* 6. PART E: CLUSTER BOOTSTRAP — CONDITIONAL INDIRECT CIs
* =============================================================================
di _n "============================================================"
di "PART E: Cluster Bootstrap (1000 reps, county_id)"
di "============================================================"

* Save filtered data to tempfile (avoid nested preserve)
preserve
keep if med_sample_cty == 1
gen SM_x_SR_boot = gleam_sms_mean * ca
gen drydays_x_SR_boot = drydays_gleam_sms_le_basep10 * ca
tempfile meddata_boot
save `meddata_boot'
restore

* Postfile: store raw coefficients per rep
tempfile bootraw
tempname bh
postfile `bh' rep double(a1_d a3_d a1c a3c b1_m2 b1_m5 b5_m5 ///
	da1 da3 db1_m2) using `bootraw', replace

local B = 1000
local dot_interval = 50

di "Starting `B' bootstrap replications..."
di "Each dot = `dot_interval' reps"

forvalues b = 1/`B' {
	if mod(`b', `dot_interval') == 0 {
		di "." _continue
	}
	if mod(`b', 500) == 0 {
		di " `b'"
	}

	preserve
	use `meddata_boot', clear
	bsample, cluster(county_id)

	* --- Mediator eq: SM ---
	cap reghdfe gleam_sms_mean D_season W_season hdd_tmax_ge32 ca ///
		SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat ///
		irr_frac pre_sum et0_sum wd_aridity_et0divpre gdd_30 ///
		clay_0_5cm_01deg sand_0_5cm_01deg bdod_0_5cm_01deg ///
		phh2o_0_5cm_01deg silt_0_5cm_01deg, absorb(county_id year)
	if _rc == 0 {
		local ba1 = _b[D_season]
		local ba3 = _b[SR_x_D]
		local ba1c = _b[D_x_Heat]
		local ba3c = _b[SR_x_D_x_Heat]
	}
	else {
		local ba1 = .
		local ba3 = .
		local ba1c = .
		local ba3c = .
	}

	* --- Outcome eq Model 2: Y = ... + b1*SM ---
	cap reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca ///
		SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat ///
		gleam_sms_mean ///
		irr_frac pre_sum et0_sum wd_aridity_et0divpre gdd_30 ///
		clay_0_5cm_01deg sand_0_5cm_01deg bdod_0_5cm_01deg ///
		phh2o_0_5cm_01deg silt_0_5cm_01deg, absorb(county_id year)
	if _rc == 0 {
		local bb1_m2 = _b[gleam_sms_mean]
	}
	else {
		local bb1_m2 = .
	}

	* --- Outcome eq Model 5: Y = ... + b1*SM + b5*SM_x_SR ---
	cap reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca ///
		SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat ///
		gleam_sms_mean SM_x_SR_boot ///
		irr_frac pre_sum et0_sum wd_aridity_et0divpre gdd_30 ///
		clay_0_5cm_01deg sand_0_5cm_01deg bdod_0_5cm_01deg ///
		phh2o_0_5cm_01deg silt_0_5cm_01deg, absorb(county_id year)
	if _rc == 0 {
		local bb1_m5 = _b[gleam_sms_mean]
		local bb5_m5 = _b[SM_x_SR_boot]
	}
	else {
		local bb1_m5 = .
		local bb5_m5 = .
	}

	* --- Mediator eq: drydays ---
	cap reghdfe drydays_gleam_sms_le_basep10 D_season W_season hdd_tmax_ge32 ca ///
		SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat ///
		irr_frac pre_sum et0_sum wd_aridity_et0divpre gdd_30 ///
		clay_0_5cm_01deg sand_0_5cm_01deg bdod_0_5cm_01deg ///
		phh2o_0_5cm_01deg silt_0_5cm_01deg, absorb(county_id year)
	if _rc == 0 {
		local bda1 = _b[D_season]
		local bda3 = _b[SR_x_D]
	}
	else {
		local bda1 = .
		local bda3 = .
	}

	* --- Outcome eq with drydays (Model 2) ---
	cap reghdfe ln_yield D_season W_season hdd_tmax_ge32 ca ///
		SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat ///
		drydays_gleam_sms_le_basep10 ///
		irr_frac pre_sum et0_sum wd_aridity_et0divpre gdd_30 ///
		clay_0_5cm_01deg sand_0_5cm_01deg bdod_0_5cm_01deg ///
		phh2o_0_5cm_01deg silt_0_5cm_01deg, absorb(county_id year)
	if _rc == 0 {
		local bdb1 = _b[drydays_gleam_sms_le_basep10]
	}
	else {
		local bdb1 = .
	}

	post `bh' (`b') (`ba1') (`ba3') (`ba1c') (`ba3c') (`bb1_m2') ///
		(`bb1_m5') (`bb5_m5') (`bda1') (`bda3') (`bdb1')

	restore
}

di _n "Bootstrap complete."
postclose `bh'

* --- Extract bootstrap CIs ---
preserve
use `bootraw', clear

* Drop failed reps
drop if missing(a1_d) | missing(b1_m2)
local B_valid = _N
di "Valid bootstrap reps: `B_valid' / `B'"

* Compute conditional indirects at each SR percentile
foreach pctl in p10 p25 p50 p75 p90 {
	local w = `sr_`pctl''
	* Model 2 drought
	gen ci_m2_d_`pctl' = b1_m2 * (a1_d + a3_d * `w')
	* Model 2 compound
	gen ci_m2_c_`pctl' = b1_m2 * (a1c + a3c * `w')
	* Model 5 drought
	gen ci_m5_d_`pctl' = (a1_d + a3_d * `w') * (b1_m5 + b5_m5 * `w')
	* Drydays Model 2 drought
	gen ci_dry_d_`pctl' = db1_m2 * (da1 + da3 * `w')
}

* Index of moderated mediation
gen IMM_m2_d = a3_d * b1_m2
gen IMM_m2_c = a3c * b1_m2
gen IMM_dry_d = da3 * db1_m2

* Open output CSV
tempname fh_boot
file open `fh_boot' using "$outdir/step_modmed_bootstrap.csv", write replace
file write `fh_boot' "model,mediator,path,sr_pctl,sr_value,boot_mean,boot_se,ci_lo_025,ci_hi_975,B_valid" _n

* Extract CIs for each
foreach pctl in p10 p25 p50 p75 p90 {
	local w = `sr_`pctl''

	* M2 drought
	sum ci_m2_d_`pctl'
	local mn = r(mean)
	local sd = r(sd)
	_pctile ci_m2_d_`pctl', p(2.5 97.5)
	file write `fh_boot' "Model2,SM_sfc,drought,`pctl'," %8.6f (`w') "," ///
		%12.8f (`mn') "," %12.8f (`sd') "," %12.8f (r(r1)) "," %12.8f (r(r2)) ///
		",`B_valid'" _n

	* M2 compound
	sum ci_m2_c_`pctl'
	local mn = r(mean)
	local sd = r(sd)
	_pctile ci_m2_c_`pctl', p(2.5 97.5)
	file write `fh_boot' "Model2,SM_sfc,compound,`pctl'," %8.6f (`w') "," ///
		%12.8f (`mn') "," %12.8f (`sd') "," %12.8f (r(r1)) "," %12.8f (r(r2)) ///
		",`B_valid'" _n

	* M5 drought
	sum ci_m5_d_`pctl'
	local mn = r(mean)
	local sd = r(sd)
	_pctile ci_m5_d_`pctl', p(2.5 97.5)
	file write `fh_boot' "Model5,SM_sfc,drought,`pctl'," %8.6f (`w') "," ///
		%12.8f (`mn') "," %12.8f (`sd') "," %12.8f (r(r1)) "," %12.8f (r(r2)) ///
		",`B_valid'" _n

	* Drydays M2 drought
	drop if missing(db1_m2)
	sum ci_dry_d_`pctl'
	local mn = r(mean)
	local sd = r(sd)
	_pctile ci_dry_d_`pctl', p(2.5 97.5)
	file write `fh_boot' "Model2,drydays,drought,`pctl'," %8.6f (`w') "," ///
		%12.8f (`mn') "," %12.8f (`sd') "," %12.8f (r(r1)) "," %12.8f (r(r2)) ///
		",`B_valid'" _n
}

* IMM bootstrap CIs
foreach imm in IMM_m2_d IMM_m2_c IMM_dry_d {
	sum `imm'
	local mn = r(mean)
	local sd = r(sd)
	_pctile `imm', p(2.5 97.5)
	local lo = r(r1)
	local hi = r(r2)

	if "`imm'" == "IMM_m2_d" {
		file write `fh_boot' "Model2,SM_sfc,drought_IMM,all,," ///
			%12.8f (`mn') "," %12.8f (`sd') "," %12.8f (`lo') "," %12.8f (`hi') ///
			",`B_valid'" _n
	}
	if "`imm'" == "IMM_m2_c" {
		file write `fh_boot' "Model2,SM_sfc,compound_IMM,all,," ///
			%12.8f (`mn') "," %12.8f (`sd') "," %12.8f (`lo') "," %12.8f (`hi') ///
			",`B_valid'" _n
	}
	if "`imm'" == "IMM_dry_d" {
		file write `fh_boot' "Model2,drydays,drought_IMM,all,," ///
			%12.8f (`mn') "," %12.8f (`sd') "," %12.8f (`lo') "," %12.8f (`hi') ///
			",`B_valid'" _n
	}
}

file close `fh_boot'
restore
di "Exported: step_modmed_bootstrap.csv"


* =============================================================================
* 7. PART F: LOYO DIAGNOSTICS
* =============================================================================
di _n "============================================================"
di "PART F: Leave-One-Year-Out Diagnostics"
di "============================================================"

tempname fh_loyo
file open `fh_loyo' using "$outdir/step_modmed_loyo.csv", write replace
file write `fh_loyo' "drop_year,FE,mediator,model,IMM,IMM_se,cond_ind_p50,delta_se_p50,N" _n

forvalues y = 2016/2019 {
	di _n "--- Drop year `y' ---"

	* SM mediator eq (county FE)
	reghdfe gleam_sms_mean $RHS_COMPOUND $SOIL_CTRL ///
		if med_sample_cty == 1 & year != `y', absorb(county_id year) vce(cluster county_id)
	local ly_a1 = _b[D_season]
	local ly_a3 = _b[SR_x_D]
	local ly_a3_se = _se[SR_x_D]

	* SM outcome eq Model 2 (county FE)
	reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL gleam_sms_mean ///
		if med_sample_cty == 1 & year != `y', absorb(county_id year) vce(cluster county_id)
	local ly_b1 = _b[gleam_sms_mean]
	local ly_b1_se = _se[gleam_sms_mean]
	local ly_N = e(N)

	local ly_IMM = `ly_a3' * `ly_b1'
	local ly_IMM_se = sqrt((`ly_a3')^2 * (`ly_b1_se')^2 + (`ly_b1')^2 * (`ly_a3_se')^2)
	local ly_ci_p50 = `ly_b1' * (`ly_a1' + `ly_a3' * `sr_p50')

	di "  SM Model 2: IMM=" %12.8f `ly_IMM' " cond_ind(P50)=" %12.8f `ly_ci_p50'

	file write `fh_loyo' "`y',county,SM_sfc,Model2," %12.8f (`ly_IMM') "," ///
		%12.8f (`ly_IMM_se') "," %12.8f (`ly_ci_p50') ",,`ly_N'" _n

	* Drydays mediator eq (county FE)
	reghdfe drydays_gleam_sms_le_basep10 $RHS_COMPOUND $SOIL_CTRL ///
		if med_sample_cty == 1 & year != `y', absorb(county_id year) vce(cluster county_id)
	local ly_da1 = _b[D_season]
	local ly_da3 = _b[SR_x_D]
	local ly_da3_se = _se[SR_x_D]

	reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL drydays_gleam_sms_le_basep10 ///
		if med_sample_cty == 1 & year != `y', absorb(county_id year) vce(cluster county_id)
	local ly_db1 = _b[drydays_gleam_sms_le_basep10]
	local ly_db1_se = _se[drydays_gleam_sms_le_basep10]

	local ly_dIMM = `ly_da3' * `ly_db1'
	local ly_dIMM_se = sqrt((`ly_da3')^2 * (`ly_db1_se')^2 + (`ly_db1')^2 * (`ly_da3_se')^2)
	local ly_dci_p50 = `ly_db1' * (`ly_da1' + `ly_da3' * `sr_p50')

	di "  Drydays Model 2: IMM=" %12.8f `ly_dIMM' " cond_ind(P50)=" %12.8f `ly_dci_p50'

	file write `fh_loyo' "`y',county,drydays,Model2," %12.8f (`ly_dIMM') "," ///
		%12.8f (`ly_dIMM_se') "," %12.8f (`ly_dci_p50') ",,`ly_N'" _n
}

file close `fh_loyo'
di "Exported: step_modmed_loyo.csv"


* =============================================================================
* 8. SUMMARY
* =============================================================================
di _n "============================================================"
di "SUMMARY: Moderated Mediation Results"
di "============================================================"

di _n "--- SM Surface (gleam_sms_mean) ---"
di "County FE Model 2:"
di "  a3 (SR moderates D→SM) = " %10.6f `a3_c' " (p=" %6.4f `a3_p_c' ")"
di "  b1 (SM→Yield)          = " %10.6f `b1_m2_c' " (p=" %6.4f (2*normal(-abs(`b1_m2_c'/`b1_m2_se_c'))) ")"
di "  IMM (drought)           = " %12.8f `IMM_drought_c' " (p=" %6.4f `IMM_p_c' ")"
di "  Cond indirect at P10    = " %12.8f (`b1_m2_c' * (`a1_c' + `a3_c' * `sr_p10'))
di "  Cond indirect at P50    = " %12.8f (`b1_m2_c' * (`a1_c' + `a3_c' * `sr_p50'))
di "  Cond indirect at P90    = " %12.8f (`b1_m2_c' * (`a1_c' + `a3_c' * `sr_p90'))
di ""
di "County FE Model 5:"
di "  b5 (SM×SR→Yield) = " %10.6f `b5_c' " (p=" %6.4f `b5_p_c' ")"
di "  Model preferred: `model_pref_c'"
di ""
di "--- Drydays (drydays_gleam_sms_le_basep10) ---"
di "County FE Model 2:"
di "  IMM (drought) = " %12.8f `dIMM_c'
di ""
di "--- Simple Mediation Comparison ---"
di "  Old approach: constant indirect = a*b ≈ 0.003, boot CI includes 0"
di "  New approach: conditional indirect varies by SR level"
di "  The indirect effect at HIGH SR should be stronger than at LOW SR"

di _n "============================================================"
di "All done. Check output/tables/step_*.csv for results."
di "============================================================"

log close
