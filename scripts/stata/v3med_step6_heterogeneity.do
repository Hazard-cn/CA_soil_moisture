* =============================================================================
* v3med_step6_heterogeneity.do
* Purpose: Subsample heterogeneity for Model 8 moderated mediation.
*          8 subsamples (6 maize_zone + 2 irr_group).
*          Primary SM = gleam_sms_mean, reduced controls only.
*          For each subsample: Set 0 baseline + Model 8 (Drought + Heat).
* Author:  YangSu + Claude
* Date:    2026-04-16
* Input:   data/processed/v3med_analysis_ready.dta
* Output:  output/tables/v3med_heterogeneity_results.csv
*          output/tables/v3med_heterogeneity_conditional_effects.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3med_macros_include.do"

log using "$logdir/v3med_step6_heterogeneity.log", replace

use "$datadir/v3med_analysis_ready.dta", clear
xtset grid_id year
keep if v3med_common == 1
di "Full working sample N = " _N

* Primary SM source
local sm "gleam_sms_mean"
local sm_lbl "GLEAM-Sfc"

* Reduced controls only
local ctrl_list "$CTRL_reduced_med"

* =============================================================================
* BUILD SUBSAMPLE INDICATORS
* =============================================================================
* Create a unified split variable for looping
gen str15 split_type = ""
gen str15 subgroup   = ""

* We'll loop by constructing a dataset-level indicator
* But for heterogeneity, we loop over subsamples externally

* =============================================================================
* COEFFICIENT STORAGE
* =============================================================================
tempname pf_coef
postfile `pf_coef' str10 split_type str10 subgroup str10 module ///
    str12 equation str25 term ///
    double(b se p) long(N) double(r2) ///
    using "$outdir/v3med_het_coef_raw.dta", replace

* =============================================================================
* CONDITIONAL EFFECTS STORAGE
* =============================================================================
tempname pf_ce
postfile `pf_ce' str10 split_type str10 subgroup str10 module ///
    str6 ca_level double(ca_value) ///
    str5 effect double(value) ///
    using "$outdir/v3med_het_ce_raw.dta", replace

* =============================================================================
* SUBSAMPLE LOOP
* =============================================================================

* Build subsample list: zone_NE zone_HHH ... irr_low_irr irr_high_irr
* We process them one at a time with an if-condition

local sub_count = 0

foreach z of global ZONE_LIST {
    local ++sub_count
    local split_`sub_count' "zone"
    local group_`sub_count' "`z'"
    local cond_`sub_count'  `"maize_zone == "`z'""'
}

foreach g of global IRR_LIST {
    local ++sub_count
    local split_`sub_count' "irr"
    local group_`sub_count' "`g'"
    local cond_`sub_count'  `"irr_group == "`g'""'
}

di "Total subsamples: `sub_count'"

* =============================================================================
* MAIN LOOP
* =============================================================================

forvalues s = 1/`sub_count' {

    local stype  "`split_`s''"
    local sgroup "`group_`s''"
    local scond  `"`cond_`s''"'

    * Count subsample size
    qui count if `scond'
    local sub_n = r(N)

    if `sub_n' < 500 {
        di _n "SKIP: `stype' / `sgroup' — only `sub_n' obs (< 500)"
        continue
    }

    di _n "################################################################"
    di "Subsample: `stype' / `sgroup' (N=`sub_n')"
    di "################################################################"

    * Compute ca percentiles for this subsample
    _pctile ca if `scond', p(25 50 75)
    scalar ca_p25 = r(r1)
    scalar ca_p50 = r(r2)
    scalar ca_p75 = r(r3)
    di "  ca P25=" %6.4f ca_p25 " P50=" %6.4f ca_p50 " P75=" %6.4f ca_p75

    * =====================================================================
    * SET 0: BASELINE (no SM)
    * =====================================================================

    * --- Drought baseline ---
    di _n "--- Set 0: Drought baseline ---"
    cap reghdfe ln_yield D_full hdd_ge32 ca SR_x_D_full `ctrl_list' ///
        if `scond', absorb(grid_id year) vce(cluster grid_id)

    if _rc == 0 {
        local nn = e(N)
        local rr = e(r2)
        foreach v in D_full hdd_ge32 ca SR_x_D_full {
            local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
            post `pf_coef' ("`stype'") ("`sgroup'") ("drought") ///
                ("baseline") ("`v'") ///
                (_b[`v']) (_se[`v']) (`pval') (`nn') (`rr')
        }
    }
    else {
        di "  WARNING: Drought baseline failed for `sgroup' (rc=" _rc ")"
    }

    * --- Heat baseline ---
    di _n "--- Set 0: Heat baseline ---"
    cap reghdfe ln_yield hdd_ge32 D_full ca SR_x_Heat_full `ctrl_list' ///
        if `scond', absorb(grid_id year) vce(cluster grid_id)

    if _rc == 0 {
        local nn = e(N)
        local rr = e(r2)
        foreach v in hdd_ge32 D_full ca SR_x_Heat_full {
            local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
            post `pf_coef' ("`stype'") ("`sgroup'") ("heat") ///
                ("baseline") ("`v'") ///
                (_b[`v']) (_se[`v']) (`pval') (`nn') (`rr')
        }
    }
    else {
        di "  WARNING: Heat baseline failed for `sgroup' (rc=" _rc ")"
    }

    * =====================================================================
    * MODEL 8: DROUGHT MODULE
    * =====================================================================

    * --- Mediator eq ---
    di _n "--- Drought mediator: `sm' ~ D + ca + D×ca + H + Z ---"
    cap reghdfe `sm' D_full ca SR_x_D_full hdd_ge32 `ctrl_list' ///
        if `scond', absorb(grid_id year) vce(cluster grid_id)

    local drought_ok = (_rc == 0)

    if `drought_ok' {
        local nn_m = e(N)
        local rr_m = e(r2)
        foreach v in D_full ca SR_x_D_full hdd_ge32 {
            local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
            post `pf_coef' ("`stype'") ("`sgroup'") ("drought") ///
                ("mediator") ("`v'") ///
                (_b[`v']) (_se[`v']) (`pval') (`nn_m') (`rr_m')
        }
        local a1 = _b[D_full]
        local a3 = _b[SR_x_D_full]
    }
    else {
        di "  WARNING: Drought mediator eq failed for `sgroup'"
    }

    * --- Outcome eq ---
    di _n "--- Drought outcome: lnY ~ D + ca + D×ca + SM + H + Z ---"
    cap reghdfe ln_yield D_full ca SR_x_D_full `sm' hdd_ge32 `ctrl_list' ///
        if `scond', absorb(grid_id year) vce(cluster grid_id)

    if _rc == 0 & `drought_ok' {
        local nn_y = e(N)
        local rr_y = e(r2)
        foreach v in D_full ca SR_x_D_full `sm' hdd_ge32 {
            local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
            local tname = cond("`v'" == "`sm'", "SM", "`v'")
            post `pf_coef' ("`stype'") ("`sgroup'") ("drought") ///
                ("outcome") ("`tname'") ///
                (_b[`v']) (_se[`v']) (`pval') (`nn_y') (`rr_y')
        }
        local b_sm = _b[`sm']
        local c1   = _b[D_full]
        local c3   = _b[SR_x_D_full]

        * Conditional effects
        foreach clbl in P25 P50 P75 {
            local r = ca_`=lower("`clbl'")'
            local ie = (`a1' + `a3' * `r') * `b_sm'
            local de = `c1' + `c3' * `r'
            local te = `de' + `ie'

            post `pf_ce' ("`stype'") ("`sgroup'") ("drought") ///
                ("`clbl'") (`r') ("IE") (`ie')
            post `pf_ce' ("`stype'") ("`sgroup'") ("drought") ///
                ("`clbl'") (`r') ("DE") (`de')
            post `pf_ce' ("`stype'") ("`sgroup'") ("drought") ///
                ("`clbl'") (`r') ("TE") (`te')
        }

        * Index
        local idx = `a3' * `b_sm'
        post `pf_ce' ("`stype'") ("`sgroup'") ("drought") ///
            ("Index") (.) ("Index") (`idx')
    }
    else if _rc != 0 {
        di "  WARNING: Drought outcome eq failed for `sgroup'"
    }

    * =====================================================================
    * MODEL 8: HEAT MODULE
    * =====================================================================

    * --- Mediator eq ---
    di _n "--- Heat mediator: `sm' ~ H + ca + H×ca + D + Z ---"
    cap reghdfe `sm' hdd_ge32 ca SR_x_Heat_full D_full `ctrl_list' ///
        if `scond', absorb(grid_id year) vce(cluster grid_id)

    local heat_ok = (_rc == 0)

    if `heat_ok' {
        local nn_m = e(N)
        local rr_m = e(r2)
        foreach v in hdd_ge32 ca SR_x_Heat_full D_full {
            local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
            post `pf_coef' ("`stype'") ("`sgroup'") ("heat") ///
                ("mediator") ("`v'") ///
                (_b[`v']) (_se[`v']) (`pval') (`nn_m') (`rr_m')
        }
        local a1h = _b[hdd_ge32]
        local a3h = _b[SR_x_Heat_full]
    }
    else {
        di "  WARNING: Heat mediator eq failed for `sgroup'"
    }

    * --- Outcome eq ---
    di _n "--- Heat outcome: lnY ~ H + ca + H×ca + SM + D + Z ---"
    cap reghdfe ln_yield hdd_ge32 ca SR_x_Heat_full `sm' D_full `ctrl_list' ///
        if `scond', absorb(grid_id year) vce(cluster grid_id)

    if _rc == 0 & `heat_ok' {
        local nn_y = e(N)
        local rr_y = e(r2)
        foreach v in hdd_ge32 ca SR_x_Heat_full `sm' D_full {
            local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
            local tname = cond("`v'" == "`sm'", "SM", "`v'")
            post `pf_coef' ("`stype'") ("`sgroup'") ("heat") ///
                ("outcome") ("`tname'") ///
                (_b[`v']) (_se[`v']) (`pval') (`nn_y') (`rr_y')
        }
        local b_h  = _b[`sm']
        local c1h  = _b[hdd_ge32]
        local c3h  = _b[SR_x_Heat_full]

        * Conditional effects
        foreach clbl in P25 P50 P75 {
            local r = ca_`=lower("`clbl'")'
            local ie = (`a1h' + `a3h' * `r') * `b_h'
            local de = `c1h' + `c3h' * `r'
            local te = `de' + `ie'

            post `pf_ce' ("`stype'") ("`sgroup'") ("heat") ///
                ("`clbl'") (`r') ("IE") (`ie')
            post `pf_ce' ("`stype'") ("`sgroup'") ("heat") ///
                ("`clbl'") (`r') ("DE") (`de')
            post `pf_ce' ("`stype'") ("`sgroup'") ("heat") ///
                ("`clbl'") (`r') ("TE") (`te')
        }

        * Index
        local idx = `a3h' * `b_h'
        post `pf_ce' ("`stype'") ("`sgroup'") ("heat") ///
            ("Index") (.) ("Index") (`idx')
    }
    else if _rc != 0 {
        di "  WARNING: Heat outcome eq failed for `sgroup'"
    }
}

postclose `pf_coef'
postclose `pf_ce'

* =============================================================================
* EXPORT
* =============================================================================
preserve
use "$outdir/v3med_het_coef_raw.dta", clear
export delimited using "$outdir/v3med_heterogeneity_results.csv", replace
restore

preserve
use "$outdir/v3med_het_ce_raw.dta", clear
export delimited using "$outdir/v3med_heterogeneity_conditional_effects.csv", replace
restore

cap erase "$outdir/v3med_het_coef_raw.dta"
cap erase "$outdir/v3med_het_ce_raw.dta"

* =============================================================================
* SUMMARY: Key a3 coefficients across subsamples
* =============================================================================
di _n "=== Drought a3 (SR_x_D_full) by subsample ==="
import delimited "$outdir/v3med_heterogeneity_results.csv", clear
list split_type subgroup b se p n if module == "drought" ///
    & equation == "mediator" & term == "SR_x_D_full", sep(0) noobs

di _n "=== Heat a3h (SR_x_Heat_full) by subsample ==="
list split_type subgroup b se p n if module == "heat" ///
    & equation == "mediator" & term == "SR_x_Heat_full", sep(0) noobs

di _n "=== Drought c3 (SR_x_D_full in outcome) by subsample ==="
list split_type subgroup b se p n if module == "drought" ///
    & equation == "outcome" & term == "SR_x_D_full", sep(0) noobs

di _n "=== Heat c3h (SR_x_Heat_full in outcome) by subsample ==="
list split_type subgroup b se p n if module == "heat" ///
    & equation == "outcome" & term == "SR_x_Heat_full", sep(0) noobs

log close
di "=== v3med_step6_heterogeneity.do COMPLETE ==="
