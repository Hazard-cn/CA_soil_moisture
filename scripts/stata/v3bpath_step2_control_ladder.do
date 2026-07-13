* =============================================================================
* v3bpath_step2_control_ladder.do
* Purpose: Audit whether control stacking absorbs the drought-side b-path
*          across all 6 SM source-layer combinations.
* Input:   data/processed/v3bpath_analysis_ready.dta
* Output:  output/tables/v3bpath_control_ladder.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3bpath_macros_include.do"

log using "$logdir/v3bpath_step2_control_ladder.log", replace

use "$datadir/v3bpath_analysis_ready.dta", clear
xtset grid_id year
keep if ${BPATH_FULL_SAMPLE} == 1

di "Working sample N = " _N

tempname pf
tempfile ladder_results
postfile `pf' str8 source str10 layer str12 sm_label str24 sm_var ///
    str2 ladder str80 controls ///
    double a1 se_a1 p_a1 ///
    double a3 se_a3 p_a3 ///
    double rho_m se_rho_m p_rho_m ///
    double c1 se_c1 p_c1 ///
    double c3 se_c3 p_c3 ///
    double b_sm se_b_sm p_b_sm ///
    double rho_y se_rho_y p_rho_y ///
    long N_m long N_y double r2_m double r2_y using `ladder_results', replace

local n_sm : word count $BPATH_SM_BASES

forvalues i = 1/`n_sm' {
    local sm     : word `i' of $BPATH_SM_BASES
    local source : word `i' of $BPATH_SOURCES
    local layer  : word `i' of $BPATH_LAYERS
    local sm_lbl : word `i' of $BPATH_SM_LABELS

    foreach ladder of global BPATH_LADDERS {
        local controls "$BPATH_CTRL_REDUCED"
        if "`ladder'" == "L1" local controls "$BPATH_CTRL_REDUCED pr_sum"
        if "`ladder'" == "L2" local controls "$BPATH_CTRL_REDUCED pr_sum et0_sum"
        if "`ladder'" == "L3" local controls "$BPATH_CTRL_FULL"

        di _n "=============================================="
        di "source=`source' | layer=`layer' | ladder=`ladder'"
        di "=============================================="

        reghdfe `sm' D_full ca SR_x_D_full hdd_ge32 `controls', ///
            absorb(grid_id year) vce(cluster grid_id)

        local dfr_m = e(df_r)
        local n_m = e(N)
        local r2_m = e(r2)
        local p_a1 = 2 * ttail(`dfr_m', abs(_b[D_full] / _se[D_full]))
        local p_a3 = 2 * ttail(`dfr_m', abs(_b[SR_x_D_full] / _se[SR_x_D_full]))
        local p_rho_m = 2 * ttail(`dfr_m', abs(_b[hdd_ge32] / _se[hdd_ge32]))

        local a1 = _b[D_full]
        local se_a1 = _se[D_full]
        local a3 = _b[SR_x_D_full]
        local se_a3 = _se[SR_x_D_full]
        local rho_m = _b[hdd_ge32]
        local se_rho_m = _se[hdd_ge32]

        reghdfe ln_yield D_full ca SR_x_D_full `sm' hdd_ge32 `controls', ///
            absorb(grid_id year) vce(cluster grid_id)

        local dfr_y = e(df_r)
        local n_y = e(N)
        local r2_y = e(r2)
        local p_c1 = 2 * ttail(`dfr_y', abs(_b[D_full] / _se[D_full]))
        local p_c3 = 2 * ttail(`dfr_y', abs(_b[SR_x_D_full] / _se[SR_x_D_full]))
        local p_b_sm = 2 * ttail(`dfr_y', abs(_b[`sm'] / _se[`sm']))
        local p_rho_y = 2 * ttail(`dfr_y', abs(_b[hdd_ge32] / _se[hdd_ge32]))

        post `pf' ("`source'") ("`layer'") ("`sm_lbl'") ("`sm'") ///
            ("`ladder'") ("`controls'") ///
            (`a1') (`se_a1') (`p_a1') ///
            (`a3') (`se_a3') (`p_a3') ///
            (`rho_m') (`se_rho_m') (`p_rho_m') ///
            (_b[D_full]) (_se[D_full]) (`p_c1') ///
            (_b[SR_x_D_full]) (_se[SR_x_D_full]) (`p_c3') ///
            (_b[`sm']) (_se[`sm']) (`p_b_sm') ///
            (_b[hdd_ge32]) (_se[hdd_ge32]) (`p_rho_y') ///
            (`n_m') (`n_y') (`r2_m') (`r2_y')
    }
}

postclose `pf'

preserve
use `ladder_results', clear
sort source layer ladder
export delimited using "$outdir/v3bpath_control_ladder.csv", replace
restore

di "=== v3bpath_step2_control_ladder.do COMPLETE ==="
log close
