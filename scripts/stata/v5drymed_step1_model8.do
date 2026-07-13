* =============================================================================
* v5drymed_step1_model8.do
* Purpose: Run drought-only Model 8 using dry-side mediators.
* Output:  output/tables/v5drymed_model8_coefficients.csv
*          output/tables/v5drymed_conditional_effects.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v5drymed_macros_include.do"

log using "$logdir/v5drymed_step1_model8.log", replace

use "$v5ready_dta", clear
xtset grid_id year

tempname pf_coef
postfile `pf_coef' str10 module str12 family str18 threshold_scheme str4 percentile ///
    str20 source_depth str12 sm_label str16 sample_tag str12 equation str16 term ///
    double(b se p) long(N) double(r2) using "$outdir/v5drymed_coef_raw.dta", replace

tempname pf_ce
postfile `pf_ce' str10 module str12 family str18 threshold_scheme str4 percentile ///
    str20 source_depth str12 sm_label str16 sample_tag str8 effect ///
    str4 ca_level double(ca_value) double(value) ///
    using "$outdir/v5drymed_ce_raw.dta", replace

local n_tags : word count $V5_SAMPLE_TAGS

forvalues t = 1/`n_tags' {
    local tag : word `t' of $V5_SAMPLE_TAGS
    local family_code : word `t' of $V5_SAMPLE_FAMILIES
    local scheme_code : word `t' of $V5_SAMPLE_SCHEMES
    local pct : word `t' of $V5_SAMPLE_PCTS
    local sample_var "v5s_`tag'"

    local family "drydays"
    if "`family_code'" == "ds" local family "dryshare"
    if "`family_code'" == "ddf" local family "drydeficit"

    local threshold_scheme "baseline_local"
    if "`scheme_code'" == "pl" local threshold_scheme "pooled_state"
    if "`scheme_code'" == "mz" local threshold_scheme "maize_zone_state"

    quietly count if `sample_var' == 1
    local n_work = r(N)
    if `n_work' == 0 {
        continue
    }

    _pctile ca if `sample_var' == 1, p(25 50 75)
    local ca_p25 = r(r1)
    local ca_p50 = r(r2)
    local ca_p75 = r(r3)

    forvalues i = 1/6 {
        local prefix : word `i' of $DRY_PREFIXES
        local source_depth : word `i' of $DRY_SOURCE_DEPTHS
        local sm_label : word `i' of $DRY_SM_LABELS
        local mediator "v5`tag'_`prefix'"

        di _n "============================================================"
        di "Running `tag' / `sm_label' / N=`n_work'"
        di "============================================================"

        reghdfe `mediator' D_full ca SR_x_D_full W_full SR_x_W_full hdd_ge32 ///
            $CTRL_full_drymed if `sample_var' == 1, ///
            absorb(grid_id year) vce(cluster grid_id)

        local nn_m = e(N)
        local rr_m = e(r2)
        foreach v in D_full ca SR_x_D_full W_full SR_x_W_full hdd_ge32 {
            local pval = 2 * ttail(e(df_r), abs(_b[`v'] / _se[`v']))
            post `pf_coef' ("drought") ("`family'") ("`threshold_scheme'") ("`pct'") ///
                ("`source_depth'") ("`sm_label'") ("`tag'") ("mediator") ("`v'") ///
                (_b[`v']) (_se[`v']) (`pval') (`nn_m') (`rr_m')
        }

        local a1 = _b[D_full]
        local a3 = _b[SR_x_D_full]

        reghdfe ln_yield D_full ca SR_x_D_full `mediator' W_full SR_x_W_full hdd_ge32 ///
            $CTRL_full_drymed if `sample_var' == 1, ///
            absorb(grid_id year) vce(cluster grid_id)

        local nn_y = e(N)
        local rr_y = e(r2)
        foreach v in D_full ca SR_x_D_full W_full SR_x_W_full hdd_ge32 {
            local pval = 2 * ttail(e(df_r), abs(_b[`v'] / _se[`v']))
            post `pf_coef' ("drought") ("`family'") ("`threshold_scheme'") ("`pct'") ///
                ("`source_depth'") ("`sm_label'") ("`tag'") ("outcome") ("`v'") ///
                (_b[`v']) (_se[`v']) (`pval') (`nn_y') (`rr_y')
        }

        local pval_m = 2 * ttail(e(df_r), abs(_b[`mediator'] / _se[`mediator']))
        post `pf_coef' ("drought") ("`family'") ("`threshold_scheme'") ("`pct'") ///
            ("`source_depth'") ("`sm_label'") ("`tag'") ("outcome") ("M") ///
            (_b[`mediator']) (_se[`mediator']) (`pval_m') (`nn_y') (`rr_y')

        local b_m = _b[`mediator']
        local c1 = _b[D_full]
        local c3 = _b[SR_x_D_full]

        foreach clbl in P25 P50 P75 {
            local rval = `ca_p25'
            if "`clbl'" == "P50" local rval = `ca_p50'
            if "`clbl'" == "P75" local rval = `ca_p75'

            local ie = (`a1' + `a3' * `rval') * `b_m'
            local de = `c1' + `c3' * `rval'
            local te = `de' + `ie'

            post `pf_ce' ("drought") ("`family'") ("`threshold_scheme'") ("`pct'") ///
                ("`source_depth'") ("`sm_label'") ("`tag'") ("IE") ("`clbl'") (`rval') (`ie')
            post `pf_ce' ("drought") ("`family'") ("`threshold_scheme'") ("`pct'") ///
                ("`source_depth'") ("`sm_label'") ("`tag'") ("DE") ("`clbl'") (`rval') (`de')
            post `pf_ce' ("drought") ("`family'") ("`threshold_scheme'") ("`pct'") ///
                ("`source_depth'") ("`sm_label'") ("`tag'") ("TE") ("`clbl'") (`rval') (`te')
        }

        local idx = `a3' * `b_m'
        post `pf_ce' ("drought") ("`family'") ("`threshold_scheme'") ("`pct'") ///
            ("`source_depth'") ("`sm_label'") ("`tag'") ("Index") ("all") (.) (`idx')
    }
}

postclose `pf_coef'
postclose `pf_ce'

preserve
use "$outdir/v5drymed_coef_raw.dta", clear
export delimited using "$v5coef_csv", replace
restore

preserve
use "$outdir/v5drymed_ce_raw.dta", clear
export delimited using "$v5ce_csv", replace
restore

cap erase "$outdir/v5drymed_coef_raw.dta"
cap erase "$outdir/v5drymed_ce_raw.dta"

log close
di "=== v5drymed_step1_model8.do COMPLETE ==="
