* =============================================================================
* v3bpath_step1_timing_audit.do
* Purpose: Audit timing mismatch with aligned drought-window outcome equations
*          across all 6 SM source-layer combinations on the unified stage sample.
* Input:   data/processed/v3bpath_analysis_ready.dta
* Output:  output/tables/v3bpath_timing_audit.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3bpath_macros_include.do"

log using "$logdir/v3bpath_step1_timing_audit.log", replace

use "$datadir/v3bpath_analysis_ready.dta", clear
xtset grid_id year
keep if ${BPATH_STAGE_SAMPLE} == 1

di "Working sample N = " _N

tempname pf
tempfile timing
postfile `pf' str10 window str8 source str10 layer str12 sm_label str32 sm_var ///
    double b_sm se_sm p_sm ///
    double b_c3 se_c3 p_c3 ///
    double b_d se_d p_d ///
    double b_h se_h p_h ///
    long N double r2 long effective_N byte stage6_common_flag using `timing', replace

local n_sm : word count $BPATH_SM_BASES

foreach w of global BPATH_WINDOWS {
    local hsfx "_`w'"
    if "`w'" == "full" local hsfx ""
    local d_var  "D_`w'"
    local c3_var "SR_x_D_`w'"
    local w_var "W_`w'"
    if "`w'" == "full" {
        local d_var  "D_full"
        local c3_var "SR_x_D_full"
        local w_var "W_full"
    }
    local h_var "hdd_ge32`hsfx'"
    local gdd_var "gdd_10_30`hsfx'"

    forvalues i = 1/`n_sm' {
        local sm     : word `i' of $BPATH_SM_BASES
        local source : word `i' of $BPATH_SOURCES
        local layer  : word `i' of $BPATH_LAYERS
        local sm_lbl : word `i' of $BPATH_SM_LABELS
        local sm_var "`sm'`hsfx'"

        di _n "=============================================="
        di "window=`w' | source=`source' | layer=`layer'"
        di "=============================================="

        reghdfe ln_yield `d_var' ca `c3_var' `h_var' `sm_var' `w_var' irr_frac `gdd_var', ///
            absorb(grid_id year) vce(cluster grid_id)

        local dfr = e(df_r)
        local nn = e(N)
        local rr = e(r2)

        local p_sm = 2 * ttail(`dfr', abs(_b[`sm_var'] / _se[`sm_var']))
        local p_c3 = 2 * ttail(`dfr', abs(_b[`c3_var'] / _se[`c3_var']))
        local p_d  = 2 * ttail(`dfr', abs(_b[`d_var'] / _se[`d_var']))
        local p_h  = 2 * ttail(`dfr', abs(_b[`h_var'] / _se[`h_var']))

        post `pf' ("`w'") ("`source'") ("`layer'") ("`sm_lbl'") ("`sm_var'") ///
            (_b[`sm_var']) (_se[`sm_var']) (`p_sm') ///
            (_b[`c3_var']) (_se[`c3_var']) (`p_c3') ///
            (_b[`d_var']) (_se[`d_var']) (`p_d') ///
            (_b[`h_var']) (_se[`h_var']) (`p_h') ///
            (`nn') (`rr') (`nn') (1)
    }
}

postclose `pf'

preserve
use `timing', clear
sort window source layer
export delimited using "$outdir/v3bpath_timing_audit.csv", replace
restore

di "=== v3bpath_step1_timing_audit.do COMPLETE ==="
log close
