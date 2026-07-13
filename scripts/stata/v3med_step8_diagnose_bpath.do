* =============================================================================
* v3med_step8_diagnose_bpath.do
* Purpose: Path D diagnostic — investigate whether alternative specifications
*          can recover a theoretically consistent SM→Y relationship (b>0).
*          Representative source: GLEAM-Sfc only (to avoid spec explosion).
*
*          Four specifications:
*            1. Baseline  — reproduce original b<0 as control
*            2. prov×year FE — absorb province-year shocks
*            3. Quadratic SM — allow U-shaped (dry hurts + flood hurts)
*            4. SM tails — P25 dry + P75 wet dummies
*
* Author:  YangSu + Claude
* Date:    2026-04-16
* Input:   data/processed/v3med_analysis_ready_plus.dta
* Output:  output/tables/v3med_bpath_diagnostic.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3med_macros_include.do"

log using "$logdir/v3med_step8_diagnose_bpath.log", replace

use "$datadir/v3med_analysis_ready_plus.dta", clear
xtset grid_id year
keep if v3med_common == 1

local SM "gleam_sms_mean"
local SMdef "SMdef_gleam_sms_mean"
local SR_x_SMdef "SR_x_SMdef_gleam_sms_mean"
local CTRL "irr_frac gdd_ge10"

* ---- Construct quadratic and tail variables (GLEAM-Sfc only) ----
gen double sm_sq = (`SM')^2
label var sm_sq "GLEAM-Sfc SM squared"

* Grid-level P25/P75 for tails
bysort grid_id: egen p25_sm = pctile(`SM'), p(25)
bysort grid_id: egen p75_sm = pctile(`SM'), p(75)
gen sm_q1 = (`SM' < p25_sm) if !missing(`SM',p25_sm)
gen sm_q4 = (`SM' > p75_sm) if !missing(`SM',p75_sm)
label var sm_q1 "1[SM < grid P25] (dry tail)"
label var sm_q4 "1[SM > grid P75] (wet tail)"

tab sm_q1, missing
tab sm_q4, missing

* Prov_year FE
cap gen prov_year = prov_code * 10000 + year

* =============================================================================
* POSTFILE
* =============================================================================
tempname pf
postfile `pf' str30 spec str20 term double(b se p) long(N) double(r2) ///
    using "$outdir/v3med_bpath_diag_raw.dta", replace

local helper "qui post `pf'"

* --- Helper: post a coef ---
capture program drop _post_coef
program _post_coef, rclass
    syntax anything, pfname(string) spec(string) N(integer) R2(real)
    local term = "`1'"
    local pval = 2*ttail(e(df_r), abs(_b[`term']/_se[`term']))
    post `pfname' ("`spec'") ("`term'") (_b[`term']) (_se[`term']) (`pval') (`N') (`r2')
end

* =============================================================================
* SPEC 1: BASELINE (reproduce b<0, GLEAM-Sfc, reduced ctrl, grid+year FE)
* =============================================================================
di _n "=============================================="
di "SPEC 1: Baseline (raw SM, grid+year FE, reduced ctrl)"
di "=============================================="
reghdfe ln_yield D_full ca SR_x_D_full `SM' hdd_ge32 `CTRL', ///
    absorb(grid_id year) vce(cluster grid_id)
local nn = e(N)
local rr = e(r2)
foreach v in D_full ca SR_x_D_full `SM' hdd_ge32 {
    local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
    local term_label = cond("`v'" == "`SM'", "SM", "`v'")
    post `pf' ("S1_baseline") ("`term_label'") (_b[`v']) (_se[`v']) (`pval') (`nn') (`rr')
}

* =============================================================================
* SPEC 2: PROV×YEAR FE
* =============================================================================
di _n "=============================================="
di "SPEC 2: prov_year FE (raw SM)"
di "=============================================="
reghdfe ln_yield D_full ca SR_x_D_full `SM' hdd_ge32 `CTRL', ///
    absorb(grid_id prov_year) vce(cluster grid_id)
local nn = e(N)
local rr = e(r2)
foreach v in D_full ca SR_x_D_full `SM' hdd_ge32 {
    local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
    local term_label = cond("`v'" == "`SM'", "SM", "`v'")
    post `pf' ("S2_provyear_FE") ("`term_label'") (_b[`v']) (_se[`v']) (`pval') (`nn') (`rr')
}

* =============================================================================
* SPEC 3: QUADRATIC SM
* =============================================================================
di _n "=============================================="
di "SPEC 3: Quadratic SM (SM + SM²)"
di "=============================================="
reghdfe ln_yield D_full ca SR_x_D_full `SM' sm_sq hdd_ge32 `CTRL', ///
    absorb(grid_id year) vce(cluster grid_id)
local nn = e(N)
local rr = e(r2)
foreach v in D_full ca SR_x_D_full `SM' sm_sq hdd_ge32 {
    local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
    local term_label = cond("`v'" == "`SM'", "SM_linear", cond("`v'" == "sm_sq", "SM_squared", "`v'"))
    post `pf' ("S3_quadratic") ("`term_label'") (_b[`v']) (_se[`v']) (`pval') (`nn') (`rr')
}
* Joint test of SM + SM²
test `SM' sm_sq
local jointF = r(F)
local jointp = r(p)
post `pf' ("S3_quadratic") ("joint_F_SM_SM2") (`jointF') (.) (`jointp') (`nn') (`rr')

* =============================================================================
* SPEC 4: SM TAILS (P25 dry + P75 wet dummies)
* =============================================================================
di _n "=============================================="
di "SPEC 4: SM tails (1[SM<P25] + 1[SM>P75])"
di "=============================================="
reghdfe ln_yield D_full ca SR_x_D_full sm_q1 sm_q4 hdd_ge32 `CTRL', ///
    absorb(grid_id year) vce(cluster grid_id)
local nn = e(N)
local rr = e(r2)
foreach v in D_full ca SR_x_D_full sm_q1 sm_q4 hdd_ge32 {
    local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
    post `pf' ("S4_tails") ("`v'") (_b[`v']) (_se[`v']) (`pval') (`nn') (`rr')
}

* =============================================================================
* SPEC 5 (bonus): SMdef with prov×year FE
* =============================================================================
di _n "=============================================="
di "SPEC 5: SMdef under prov_year FE"
di "=============================================="
reghdfe ln_yield D_full ca SR_x_D_full `SMdef' hdd_ge32 `CTRL', ///
    absorb(grid_id prov_year) vce(cluster grid_id)
local nn = e(N)
local rr = e(r2)
foreach v in D_full ca SR_x_D_full `SMdef' hdd_ge32 {
    local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
    local term_label = cond("`v'" == "`SMdef'", "SMdef", "`v'")
    post `pf' ("S5_SMdef_provyear") ("`term_label'") (_b[`v']) (_se[`v']) (`pval') (`nn') (`rr')
}

postclose `pf'

preserve
use "$outdir/v3med_bpath_diag_raw.dta", clear
export delimited using "$outdir/v3med_bpath_diagnostic.csv", replace
list spec term b se p, sepby(spec) noobs
restore
cap erase "$outdir/v3med_bpath_diag_raw.dta"

log close
di "=== v3med_step8_diagnose_bpath.do COMPLETE ==="
