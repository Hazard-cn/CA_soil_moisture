* =============================================================================
* v3med_step3_heat_model8.do
* Purpose: Set 2 — Heat module Model 8 moderated mediation (mirror of Drought).
*          For each of 6 SM sources × 2 ctrl versions:
*            Mediator eq: SM = a1h*H + a2h*ca + a3h*(H×ca) + rho_d*D + Z + FE
*            Outcome eq:  lnY = c1h*H + c2h*ca + c3h*(H×ca) + b_h*SM + rho_dy*D + Z + FE
*          Then compute conditional effects at ca P25/P50/P75.
* Author:  YangSu + Claude
* Date:    2026-04-16
* Input:   data/processed/v3med_analysis_ready.dta
* Output:  output/tables/v3med_heat_model8_coefficients.csv
*          output/tables/v3med_heat_conditional_effects.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3med_macros_include.do"

log using "$logdir/v3med_step3_heat_model8.log", replace

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
    using "$outdir/v3med_heat_m8_coef_raw.dta", replace

* =============================================================================
* CONDITIONAL EFFECTS STORAGE
* =============================================================================
tempname pf_ce
postfile `pf_ce' str4 fe_level str10 ctrl_version str20 sm_source ///
    str12 sm_label str6 ca_level double(ca_value) ///
    str5 effect double(value) ///
    using "$outdir/v3med_heat_ce_raw.dta", replace

* =============================================================================
* MAIN LOOP: FE levels × ctrl versions × SM sources
* =============================================================================
local fe_list "L0"

foreach fe_tag of local fe_list {

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

        local si = 0
        foreach sm of global SM_SOURCES {
            local ++si
            local sm_lbl : word `si' of $SM_LABELS

            di _n "=============================================="
            di "FE=`fe_tag'  CTRL=`cv'  SM=`sm' (`sm_lbl')"
            di "=============================================="

            * ----- Mediator equation (a-path) -----
            di _n "--- Mediator eq: `sm' ~ H + ca + H×ca + D + Z ---"
            reghdfe `sm' hdd_ge32 ca SR_x_Heat_full D_full `ctrl_list', ///
                absorb(`abs_spec') vce(cluster `cl_spec')

            local nn_m = e(N)
            local rr_m = e(r2)

            foreach v in hdd_ge32 ca SR_x_Heat_full D_full {
                local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
                post `pf_coef' ("`fe_tag'") ("`cv'") ("`sm'") ///
                    ("`sm_lbl'") ("mediator") ("`v'") ///
                    (_b[`v']) (_se[`v']) (`pval') (`nn_m') (`rr_m')
            }

            local a1h = _b[hdd_ge32]
            local a3h = _b[SR_x_Heat_full]

            * ----- Outcome equation (c'-path + b-path) -----
            di _n "--- Outcome eq: lnY ~ H + ca + H×ca + SM + D + Z ---"
            reghdfe ln_yield hdd_ge32 ca SR_x_Heat_full `sm' D_full `ctrl_list', ///
                absorb(`abs_spec') vce(cluster `cl_spec')

            local nn_y = e(N)
            local rr_y = e(r2)

            foreach v in hdd_ge32 ca SR_x_Heat_full `sm' D_full {
                local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
                local tname = cond("`v'" == "`sm'", "SM", "`v'")
                post `pf_coef' ("`fe_tag'") ("`cv'") ("`sm'") ///
                    ("`sm_lbl'") ("outcome") ("`tname'") ///
                    (_b[`v']) (_se[`v']) (`pval') (`nn_y') (`rr_y')
            }

            local b_h  = _b[`sm']
            local c1h  = _b[hdd_ge32]
            local c3h  = _b[SR_x_Heat_full]

            * ----- Conditional effects at P25, P50, P75 -----
            foreach clbl in P25 P50 P75 {
                local r = ca_`=lower("`clbl'")'

                * IE_H(r) = (a1h + a3h*r) * b_h
                local ie = (`a1h' + `a3h' * `r') * `b_h'
                * DE_H(r) = c1h + c3h*r
                local de = `c1h' + `c3h' * `r'
                * TE_H(r) = DE + IE
                local te = `de' + `ie'

                post `pf_ce' ("`fe_tag'") ("`cv'") ("`sm'") ///
                    ("`sm_lbl'") ("`clbl'") (`r') ("IE") (`ie')
                post `pf_ce' ("`fe_tag'") ("`cv'") ("`sm'") ///
                    ("`sm_lbl'") ("`clbl'") (`r') ("DE") (`de')
                post `pf_ce' ("`fe_tag'") ("`cv'") ("`sm'") ///
                    ("`sm_lbl'") ("`clbl'") (`r') ("TE") (`te')
            }

            * Index of moderated mediation = a3h * b_h
            local idx = `a3h' * `b_h'
            post `pf_ce' ("`fe_tag'") ("`cv'") ("`sm'") ///
                ("`sm_lbl'") ("Index") (.) ("Index") (`idx')

        }
    }
}

postclose `pf_coef'
postclose `pf_ce'

* =============================================================================
* EXPORT
* =============================================================================
preserve
use "$outdir/v3med_heat_m8_coef_raw.dta", clear
export delimited using "$outdir/v3med_heat_model8_coefficients.csv", replace
restore

preserve
use "$outdir/v3med_heat_ce_raw.dta", clear
export delimited using "$outdir/v3med_heat_conditional_effects.csv", replace
restore

cap erase "$outdir/v3med_heat_m8_coef_raw.dta"
cap erase "$outdir/v3med_heat_ce_raw.dta"

* Quick check
di _n "=== Quick a3h significance check (grid FE, reduced ctrl) ==="
import delimited "$outdir/v3med_heat_model8_coefficients.csv", clear
list sm_label b se p if fe_level == "L0" & ctrl_version == "reduced" ///
    & equation == "mediator" & term == "SR_x_Heat_full", sep(0)

log close
di "=== v3med_step3_heat_model8.do COMPLETE ==="
