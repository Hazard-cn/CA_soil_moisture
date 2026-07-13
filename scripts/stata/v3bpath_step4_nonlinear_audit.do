* =============================================================================
* v3bpath_step4_nonlinear_audit.do
* Purpose: Audit nonlinear b-path specifications across all 6 SM sources.
* Input:   data/processed/v3bpath_analysis_ready.dta
* Output:  output/tables/v3bpath_nonlinear_audit.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3bpath_macros_include.do"

log using "$logdir/v3bpath_step4_nonlinear_audit.log", replace

use "$datadir/v3bpath_analysis_ready.dta", clear
xtset grid_id year
keep if ${BPATH_FULL_SAMPLE} == 1

di "Working sample N = " _N

tempname pf
tempfile nonlinear
postfile `pf' str8 source str10 layer str12 sm_label str24 sm_var ///
    str10 spec ///
    double sm_linear se_sm_linear p_sm_linear ///
    double sm_squared se_sm_squared p_sm_squared ///
    double turning_point byte turning_in_support ///
    double dry_tail se_dry_tail p_dry_tail ///
    double wet_tail se_wet_tail p_wet_tail ///
    double c3 se_c3 p_c3 ///
    long N double r2 using `nonlinear', replace

local n_sm : word count $BPATH_SM_BASES

forvalues i = 1/`n_sm' {
    local sm      : word `i' of $BPATH_SM_BASES
    local source  : word `i' of $BPATH_SOURCES
    local layer   : word `i' of $BPATH_LAYERS
    local sm_lbl  : word `i' of $BPATH_SM_LABELS

    di _n "=============================================="
    di "source=`source' | layer=`layer'"
    di "=============================================="

    reghdfe ln_yield D_full ca SR_x_D_full `sm' hdd_ge32 W_full irr_frac gdd_10_30, ///
        absorb(grid_id year) vce(cluster grid_id)

    local dfr = e(df_r)
    local nn = e(N)
    local rr = e(r2)
    local p_sm = 2 * ttail(`dfr', abs(_b[`sm'] / _se[`sm']))
    local p_c3 = 2 * ttail(`dfr', abs(_b[SR_x_D_full] / _se[SR_x_D_full]))

    post `pf' ("`source'") ("`layer'") ("`sm_lbl'") ("`sm'") ///
        ("baseline") ///
        (_b[`sm']) (_se[`sm']) (`p_sm') ///
        (.) (.) (.) ///
        (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (_b[SR_x_D_full]) (_se[SR_x_D_full]) (`p_c3') ///
        (`nn') (`rr')

    quietly summarize `sm'
    local sm_mean = r(mean)
    local sm_min = r(min)
    local sm_max = r(max)

    tempvar sm_c sm_sq
    gen double `sm_c' = `sm' - `sm_mean'
    gen double `sm_sq' = (`sm_c')^2

    reghdfe ln_yield D_full ca SR_x_D_full `sm_c' `sm_sq' hdd_ge32 W_full irr_frac gdd_10_30, ///
        absorb(grid_id year) vce(cluster grid_id)

    local dfr = e(df_r)
    local nn = e(N)
    local rr = e(r2)
    local p_smc = 2 * ttail(`dfr', abs(_b[`sm_c'] / _se[`sm_c']))
    local p_smsq = 2 * ttail(`dfr', abs(_b[`sm_sq'] / _se[`sm_sq']))
    local p_c3 = 2 * ttail(`dfr', abs(_b[SR_x_D_full] / _se[SR_x_D_full]))
    local tp = .
    local tp_flag = 0
    if _b[`sm_sq'] != 0 {
        local tp = `sm_mean' - (_b[`sm_c'] / (2 * _b[`sm_sq']))
        local tp_flag = (`tp' >= `sm_min' & `tp' <= `sm_max')
    }

    post `pf' ("`source'") ("`layer'") ("`sm_lbl'") ("`sm'") ///
        ("quadratic") ///
        (_b[`sm_c']) (_se[`sm_c']) (`p_smc') ///
        (_b[`sm_sq']) (_se[`sm_sq']) (`p_smsq') ///
        (`tp') (`tp_flag') ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (_b[SR_x_D_full]) (_se[SR_x_D_full]) (`p_c3') ///
        (`nn') (`rr')

    tempvar p25 p75 sm_q1 sm_q4
    bysort grid_id: egen `p25' = pctile(`sm'), p(25)
    bysort grid_id: egen `p75' = pctile(`sm'), p(75)
    gen byte `sm_q1' = (`sm' < `p25') if !missing(`sm', `p25')
    gen byte `sm_q4' = (`sm' > `p75') if !missing(`sm', `p75')

    reghdfe ln_yield D_full ca SR_x_D_full `sm_q1' `sm_q4' hdd_ge32 W_full irr_frac gdd_10_30, ///
        absorb(grid_id year) vce(cluster grid_id)

    local dfr = e(df_r)
    local nn = e(N)
    local rr = e(r2)
    local p_q1 = 2 * ttail(`dfr', abs(_b[`sm_q1'] / _se[`sm_q1']))
    local p_q4 = 2 * ttail(`dfr', abs(_b[`sm_q4'] / _se[`sm_q4']))
    local p_c3 = 2 * ttail(`dfr', abs(_b[SR_x_D_full] / _se[SR_x_D_full]))

    post `pf' ("`source'") ("`layer'") ("`sm_lbl'") ("`sm'") ///
        ("tails") ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) ///
        (_b[`sm_q1']) (_se[`sm_q1']) (`p_q1') ///
        (_b[`sm_q4']) (_se[`sm_q4']) (`p_q4') ///
        (_b[SR_x_D_full]) (_se[SR_x_D_full]) (`p_c3') ///
        (`nn') (`rr')

    drop `sm_c' `sm_sq' `p25' `p75' `sm_q1' `sm_q4'
}

postclose `pf'

preserve
use `nonlinear', clear
sort source layer spec
export delimited using "$outdir/v3bpath_nonlinear_audit.csv", replace
restore

di "=== v3bpath_step4_nonlinear_audit.do COMPLETE ==="
log close
