* =============================================================================
* v3bpath_step3_wet_control_audit.do
* Purpose: Audit how much explicit wetness-as-control absorbs the inverted
*          b-path across all 6 SM source-layer combinations.
* Input:   data/processed/v3bpath_analysis_ready.dta
* Output:  output/tables/v3bpath_wet_control_audit.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3bpath_macros_include.do"

log using "$logdir/v3bpath_step3_wet_control_audit.log", replace

use "$datadir/v3bpath_analysis_ready.dta", clear
xtset grid_id year
keep if ${BPATH_FULL_SAMPLE} == 1

di "Working sample N = " _N

tempname pf
tempfile wet
postfile `pf' str8 source str10 layer str12 sm_label ///
    str2 spec str24 mediator_var str24 outcome_sm_var str80 controls ///
    double a1 se_a1 p_a1 ///
    double a3 se_a3 p_a3 ///
    double w_m se_w_m p_w_m ///
    double c1 se_c1 p_c1 ///
    double c3 se_c3 p_c3 ///
    double b_sm se_b_sm p_b_sm ///
    double w_y se_w_y p_w_y ///
    double h_y se_h_y p_h_y ///
    long N_m long N_y double r2_m double r2_y using `wet', replace

local n_sm : word count $BPATH_SM_BASES

forvalues i = 1/`n_sm' {
    local sm      : word `i' of $BPATH_SM_BASES
    local source  : word `i' of $BPATH_SOURCES
    local layer   : word `i' of $BPATH_LAYERS
    local sm_lbl  : word `i' of $BPATH_SM_LABELS
    local smdef   "SMdef_`sm'"

    foreach spec in N0 N1 N2 {
        local mediator_var "`sm'"
        if "`spec'" == "N2" local mediator_var "`smdef'"

        local controls "irr_frac gdd_10_30"
        if inlist("`spec'", "N1", "N2") local controls "`controls' W_full"

        di _n "=============================================="
        di "source=`source' | layer=`layer' | spec=`spec'"
        di "=============================================="

        reghdfe `mediator_var' D_full ca SR_x_D_full hdd_ge32 `controls', ///
            absorb(grid_id year) vce(cluster grid_id)

        local dfr_m = e(df_r)
        local n_m = e(N)
        local r2_m = e(r2)
        local p_a1 = 2 * ttail(`dfr_m', abs(_b[D_full] / _se[D_full]))
        local p_a3 = 2 * ttail(`dfr_m', abs(_b[SR_x_D_full] / _se[SR_x_D_full]))
        local a1_m = _b[D_full]
        local se_a1_m = _se[D_full]
        local a3_m = _b[SR_x_D_full]
        local se_a3_m = _se[SR_x_D_full]

        local w_m = .
        local se_w_m = .
        local p_w_m = .
        if inlist("`spec'", "N1", "N2") {
            local w_m = _b[W_full]
            local se_w_m = _se[W_full]
            local p_w_m = 2 * ttail(`dfr_m', abs(_b[W_full] / _se[W_full]))
        }

        reghdfe ln_yield D_full ca SR_x_D_full `mediator_var' hdd_ge32 `controls', ///
            absorb(grid_id year) vce(cluster grid_id)

        local dfr_y = e(df_r)
        local n_y = e(N)
        local r2_y = e(r2)
        local p_c1 = 2 * ttail(`dfr_y', abs(_b[D_full] / _se[D_full]))
        local p_c3 = 2 * ttail(`dfr_y', abs(_b[SR_x_D_full] / _se[SR_x_D_full]))
        local p_b_sm = 2 * ttail(`dfr_y', abs(_b[`mediator_var'] / _se[`mediator_var']))
        local p_h_y = 2 * ttail(`dfr_y', abs(_b[hdd_ge32] / _se[hdd_ge32]))

        local w_y = .
        local se_w_y = .
        local p_w_y = .
        if inlist("`spec'", "N1", "N2") {
            local w_y = _b[W_full]
            local se_w_y = _se[W_full]
            local p_w_y = 2 * ttail(`dfr_y', abs(_b[W_full] / _se[W_full]))
        }

        post `pf' ("`source'") ("`layer'") ("`sm_lbl'") ///
            ("`spec'") ("`mediator_var'") ("`mediator_var'") ("`controls'") ///
            (`a1_m') (`se_a1_m') (`p_a1') ///
            (`a3_m') (`se_a3_m') (`p_a3') ///
            (`w_m') (`se_w_m') (`p_w_m') ///
            (_b[D_full]) (_se[D_full]) (`p_c1') ///
            (_b[SR_x_D_full]) (_se[SR_x_D_full]) (`p_c3') ///
            (_b[`mediator_var']) (_se[`mediator_var']) (`p_b_sm') ///
            (`w_y') (`se_w_y') (`p_w_y') ///
            (_b[hdd_ge32]) (_se[hdd_ge32]) (`p_h_y') ///
            (`n_m') (`n_y') (`r2_m') (`r2_y')
    }
}

postclose `pf'

preserve
use `wet', clear
sort source layer spec
export delimited using "$outdir/v3bpath_wet_control_audit.csv", replace
restore

di "=== v3bpath_step3_wet_control_audit.do COMPLETE ==="
log close
