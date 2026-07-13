* =============================================================================
* v3bpath_step7_heat_consistency.do
* Purpose: Check whether heat-buffering estimates remain stable when different
*          SM backgrounds are controlled.
* Input:   data/processed/v3bpath_analysis_ready.dta
* Output:  output/tables/v3bpath_heat_consistency.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3bpath_macros_include.do"

log using "$logdir/v3bpath_step7_heat_consistency.log", replace

use "$datadir/v3bpath_analysis_ready.dta", clear
xtset grid_id year
keep if ${BPATH_FULL_SAMPLE} == 1

di "Working sample N = " _N

tempname pf
tempfile heat
postfile `pf' str8 source str10 layer str12 sm_label ///
    str12 background_role str24 background_var ///
    str8 control_version str80 controls ///
    double b_h se_h p_h ///
    double b_hxca se_hxca p_hxca ///
    double b_d se_d p_d ///
    double b_bg se_bg p_bg ///
    long N double r2 using `heat', replace

local n_sm : word count $BPATH_SM_BASES

forvalues i = 1/`n_sm' {
    local sm      : word `i' of $BPATH_SM_BASES
    local source  : word `i' of $BPATH_SOURCES
    local layer   : word `i' of $BPATH_LAYERS
    local sm_lbl  : word `i' of $BPATH_SM_LABELS
    local dry_var "dry_`sm'"

    foreach role in rawSM_bg DrySM_bg {
        local bg_var "`sm'"
        if "`role'" == "DrySM_bg" local bg_var "`dry_var'"

        foreach cv in reduced full {
            local controls "$BPATH_CTRL_REDUCED"
            if "`cv'" == "full" local controls "$BPATH_CTRL_FULL"

            di _n "=============================================="
            di "source=`source' | layer=`layer' | role=`role' | ctrl=`cv'"
            di "=============================================="

            reghdfe ln_yield hdd_ge32 ca SR_x_Heat_full D_full `bg_var' `controls', ///
                absorb(grid_id year) vce(cluster grid_id)

            local dfr = e(df_r)
            local nn = e(N)
            local rr = e(r2)
            local p_h = 2 * ttail(`dfr', abs(_b[hdd_ge32] / _se[hdd_ge32]))
            local p_hxca = 2 * ttail(`dfr', abs(_b[SR_x_Heat_full] / _se[SR_x_Heat_full]))
            local p_d = 2 * ttail(`dfr', abs(_b[D_full] / _se[D_full]))
            local p_bg = 2 * ttail(`dfr', abs(_b[`bg_var'] / _se[`bg_var']))

            post `pf' ("`source'") ("`layer'") ("`sm_lbl'") ///
                ("`role'") ("`bg_var'") ///
                ("`cv'") ("`controls'") ///
                (_b[hdd_ge32]) (_se[hdd_ge32]) (`p_h') ///
                (_b[SR_x_Heat_full]) (_se[SR_x_Heat_full]) (`p_hxca') ///
                (_b[D_full]) (_se[D_full]) (`p_d') ///
                (_b[`bg_var']) (_se[`bg_var']) (`p_bg') ///
                (`nn') (`rr')
        }
    }
}

postclose `pf'

preserve
use `heat', clear
sort source layer background_role control_version
export delimited using "$outdir/v3bpath_heat_consistency.csv", replace
restore

di "=== v3bpath_step7_heat_consistency.do COMPLETE ==="
log close
