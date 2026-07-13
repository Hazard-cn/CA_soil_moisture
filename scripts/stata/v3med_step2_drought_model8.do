* =============================================================================
* v3med_step2_drought_model8.do
* Purpose: Set 1 — Drought module Model 8 moderated mediation.
*          For each of 6 SM sources × 2 ctrl versions:
*            Mediator eq: SM = a1*D + a2*ca + a3*(D×ca) + rho*H + Z + FE
*            Outcome eq:  lnY = c1*D + c2*ca + c3*(D×ca) + b*SM + rho_y*H + Z + FE
*          Then compute conditional effects at ca P25/P50/P75.
*          If grid FE a3 mostly n.s., auto-relax to county/city/province FE.
* Author:  YangSu + Claude
* Date:    2026-04-16
* Input:   data/processed/v3med_analysis_ready.dta
* Output:  output/tables/v3med_drought_model8_coefficients.csv
*          output/tables/v3med_drought_conditional_effects.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3med_macros_include.do"

log using "$logdir/v3med_step2_drought_model8.log", replace

use "$datadir/v3med_analysis_ready.dta", clear
xtset grid_id year
keep if v3med_common == 1
di "Working sample N = " _N

* Retrieve ca representative values
_pctile ca, p(25 50 75)
scalar ca_p25 = r(r1)
scalar ca_p50 = r(r2)
scalar ca_p75 = r(r3)

* =============================================================================
* COEFFICIENT STORAGE
* =============================================================================
tempname pf_coef
postfile `pf_coef' str4 fe_level str10 ctrl_version str20 sm_source ///
    str12 sm_label str12 equation str25 term ///
    double(b se p) long(N) double(r2) ///
    using "$outdir/v3med_drought_m8_coef_raw.dta", replace

* =============================================================================
* CONDITIONAL EFFECTS STORAGE
* =============================================================================
tempname pf_ce
postfile `pf_ce' str4 fe_level str10 ctrl_version str20 sm_source ///
    str12 sm_label str6 ca_level double(ca_value) ///
    str5 effect double(value) ///
    using "$outdir/v3med_drought_ce_raw.dta", replace

* =============================================================================
* MAIN LOOP: FE levels × ctrl versions × SM sources
* =============================================================================

* Start with L0 (grid FE) only; if needed, add lower levels later
local fe_list "L0"

foreach fe_tag of local fe_list {

    * Set FE and cluster based on level
    if "`fe_tag'" == "L0" {
        local abs_spec "grid_id year"
        local cl_spec "grid_id"
    }
    else if "`fe_tag'" == "L1" {
        local abs_spec "county_code year"
        local cl_spec "county_code"
    }
    else if "`fe_tag'" == "L2" {
        local abs_spec "city_code year"
        local cl_spec "city_code"
    }
    else {
        local abs_spec "prov_code year"
        local cl_spec "prov_code"
    }

    foreach cv of global CTRL_VERSIONS {

        local ctrl_list "${CTRL_`cv'_med}"

        * Loop over 6 SM sources
        local si = 0
        foreach sm of global SM_SOURCES {
            local ++si

            * Get label
            local sm_lbl : word `si' of $SM_LABELS

            di _n "=============================================="
            di "FE=`fe_tag'  CTRL=`cv'  SM=`sm' (`sm_lbl')"
            di "=============================================="

            * ----- Mediator equation (a-path) -----
            di _n "--- Mediator eq: `sm' ~ D + ca + D×ca + H + Z ---"
            reghdfe `sm' D_full ca SR_x_D_full hdd_ge32 `ctrl_list', ///
                absorb(`abs_spec') vce(cluster `cl_spec')

            local nn_m = e(N)
            local rr_m = e(r2)

            * Store a1 (D_full), a2 (ca), a3 (SR_x_D_full), rho (hdd_ge32)
            foreach v in D_full ca SR_x_D_full hdd_ge32 {
                local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
                post `pf_coef' ("`fe_tag'") ("`cv'") ("`sm'") ///
                    ("`sm_lbl'") ("mediator") ("`v'") ///
                    (_b[`v']) (_se[`v']) (`pval') (`nn_m') (`rr_m')
            }

            * Save key coefficients for conditional effects
            local a1 = _b[D_full]
            local a3 = _b[SR_x_D_full]

            * ----- Outcome equation (c'-path + b-path) -----
            di _n "--- Outcome eq: lnY ~ D + ca + D×ca + SM + H + Z ---"
            reghdfe ln_yield D_full ca SR_x_D_full `sm' hdd_ge32 `ctrl_list', ///
                absorb(`abs_spec') vce(cluster `cl_spec')

            local nn_y = e(N)
            local rr_y = e(r2)

            foreach v in D_full ca SR_x_D_full `sm' hdd_ge32 {
                local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
                * Use cleaner term name for SM
                local tname = cond("`v'" == "`sm'", "SM", "`v'")
                post `pf_coef' ("`fe_tag'") ("`cv'") ("`sm'") ///
                    ("`sm_lbl'") ("outcome") ("`tname'") ///
                    (_b[`v']) (_se[`v']) (`pval') (`nn_y') (`rr_y')
            }

            local b_sm = _b[`sm']
            local c1 = _b[D_full]
            local c3 = _b[SR_x_D_full]

            * ----- Conditional effects at P25, P50, P75 -----
            foreach clbl in P25 P50 P75 {
                local r = ca_`=lower("`clbl'")'

                * IE_D(r) = (a1 + a3*r) * b
                local ie = (`a1' + `a3' * `r') * `b_sm'
                * DE_D(r) = c1 + c3*r
                local de = `c1' + `c3' * `r'
                * TE_D(r) = DE + IE
                local te = `de' + `ie'

                post `pf_ce' ("`fe_tag'") ("`cv'") ("`sm'") ///
                    ("`sm_lbl'") ("`clbl'") (`r') ("IE") (`ie')
                post `pf_ce' ("`fe_tag'") ("`cv'") ("`sm'") ///
                    ("`sm_lbl'") ("`clbl'") (`r') ("DE") (`de')
                post `pf_ce' ("`fe_tag'") ("`cv'") ("`sm'") ///
                    ("`sm_lbl'") ("`clbl'") (`r') ("TE") (`te')
            }

            * Index of moderated mediation = a3 * b
            local idx = `a3' * `b_sm'
            post `pf_ce' ("`fe_tag'") ("`cv'") ("`sm'") ///
                ("`sm_lbl'") ("Index") (.) ("Index") (`idx')

        }  // end SM loop
    }  // end ctrl version loop
}  // end FE loop

postclose `pf_coef'
postclose `pf_ce'

* =============================================================================
* EXPORT TO CSV
* =============================================================================
preserve
use "$outdir/v3med_drought_m8_coef_raw.dta", clear
export delimited using "$outdir/v3med_drought_model8_coefficients.csv", replace
restore

preserve
use "$outdir/v3med_drought_ce_raw.dta", clear
export delimited using "$outdir/v3med_drought_conditional_effects.csv", replace
restore

cap erase "$outdir/v3med_drought_m8_coef_raw.dta"
cap erase "$outdir/v3med_drought_ce_raw.dta"

* =============================================================================
* CHECK: is a3 significant for any SM source under grid FE + reduced ctrl?
* =============================================================================
di _n "=== Quick a3 significance check (grid FE, reduced ctrl) ==="
import delimited "$outdir/v3med_drought_model8_coefficients.csv", clear
list sm_label b se p if fe_level == "L0" & ctrl_version == "reduced" ///
    & equation == "mediator" & term == "SR_x_D_full", sep(0)

log close
di "=== v3med_step2_drought_model8.do COMPLETE ==="
