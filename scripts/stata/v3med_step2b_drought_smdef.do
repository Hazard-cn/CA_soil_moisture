* =============================================================================
* v3med_step2b_drought_smdef.do
* Purpose: Path A repair of Model 8 drought module using SM_def as mediator.
*
*          Mediator eq: SMdef_s = a1*D + a2*ca + a3*(D×ca) + rho*H + Z + FE
*          Outcome eq:  lnY = c1*D + c2*ca + c3*(D×ca) + b*SMdef_s + rho_y*H + Z + FE
*
*          Sign expectations (repaired):
*             a1 > 0 (D increases deficit)
*             a3 < 0 (SR reduces deficit under drought)
*             b  < 0 (deficit hurts yield)
*             c3 > 0 (SR direct buffering, unchanged)
*             Index = a3*b > 0 (SR's deficit-shrinking translates to yield protection)
*
* Author:  YangSu + Claude
* Date:    2026-04-16
* Input:   data/processed/v3med_analysis_ready_plus.dta
* Output:  output/tables/v3med_smdef_drought_coefficients.csv
*          output/tables/v3med_smdef_drought_conditional_effects.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3med_macros_include.do"

log using "$logdir/v3med_step2b_drought_smdef.log", replace

use "$datadir/v3med_analysis_ready_plus.dta", clear
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
postfile `pf_coef' str4 fe_level str10 ctrl_version str25 sm_source ///
    str12 sm_label str12 equation str25 term ///
    double(b se p) long(N) double(r2) ///
    using "$outdir/v3med_smdef_drought_coef_raw.dta", replace

tempname pf_ce
postfile `pf_ce' str4 fe_level str10 ctrl_version str25 sm_source ///
    str12 sm_label str6 ca_level double(ca_value) ///
    str5 effect double(value) ///
    using "$outdir/v3med_smdef_drought_ce_raw.dta", replace

* =============================================================================
* MAIN LOOP
* =============================================================================
local fe_list "L0"

foreach fe_tag of local fe_list {

    if "`fe_tag'" == "L0" {
        local abs_spec "grid_id year"
        local cl_spec "grid_id"
    }

    foreach cv of global CTRL_VERSIONS {

        local ctrl_list "${CTRL_`cv'_med}"

        local si = 0
        foreach s of global SM_SOURCES {
            local ++si
            local sm_lbl : word `si' of $SM_LABELS

            di _n "=============================================="
            di "FE=`fe_tag'  CTRL=`cv'  SMdef_`s' (`sm_lbl')"
            di "=============================================="

            * ----- Mediator equation (SMdef_s ~ D + ca + D×ca + H + Z) -----
            di _n "--- Mediator eq: SMdef_`s' ~ D + ca + D×ca + H + Z ---"
            reghdfe SMdef_`s' D_full ca SR_x_D_full hdd_ge32 `ctrl_list', ///
                absorb(`abs_spec') vce(cluster `cl_spec')

            local nn_m = e(N)
            local rr_m = e(r2)

            foreach v in D_full ca SR_x_D_full hdd_ge32 {
                local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
                post `pf_coef' ("`fe_tag'") ("`cv'") ("`s'") ///
                    ("`sm_lbl'") ("mediator") ("`v'") ///
                    (_b[`v']) (_se[`v']) (`pval') (`nn_m') (`rr_m')
            }

            local a1 = _b[D_full]
            local a3 = _b[SR_x_D_full]

            * ----- Outcome equation (lnY ~ D + ca + D×ca + SMdef + H + Z) -----
            di _n "--- Outcome eq: lnY ~ D + ca + D×ca + SMdef_`s' + H + Z ---"
            reghdfe ln_yield D_full ca SR_x_D_full SMdef_`s' hdd_ge32 `ctrl_list', ///
                absorb(`abs_spec') vce(cluster `cl_spec')

            local nn_y = e(N)
            local rr_y = e(r2)

            foreach v in D_full ca SR_x_D_full SMdef_`s' hdd_ge32 {
                local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
                local tname = cond("`v'" == "SMdef_`s'", "SMdef", "`v'")
                post `pf_coef' ("`fe_tag'") ("`cv'") ("`s'") ///
                    ("`sm_lbl'") ("outcome") ("`tname'") ///
                    (_b[`v']) (_se[`v']) (`pval') (`nn_y') (`rr_y')
            }

            local b_sm = _b[SMdef_`s']
            local c1 = _b[D_full]
            local c3 = _b[SR_x_D_full]

            * ----- Conditional effects at P25, P50, P75 -----
            foreach clbl in P25 P50 P75 {
                local r = ca_`=lower("`clbl'")'
                local ie = (`a1' + `a3' * `r') * `b_sm'
                local de = `c1' + `c3' * `r'
                local te = `de' + `ie'
                post `pf_ce' ("`fe_tag'") ("`cv'") ("`s'") ///
                    ("`sm_lbl'") ("`clbl'") (`r') ("IE") (`ie')
                post `pf_ce' ("`fe_tag'") ("`cv'") ("`s'") ///
                    ("`sm_lbl'") ("`clbl'") (`r') ("DE") (`de')
                post `pf_ce' ("`fe_tag'") ("`cv'") ("`s'") ///
                    ("`sm_lbl'") ("`clbl'") (`r') ("TE") (`te')
            }

            local idx = `a3' * `b_sm'
            post `pf_ce' ("`fe_tag'") ("`cv'") ("`s'") ///
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
use "$outdir/v3med_smdef_drought_coef_raw.dta", clear
export delimited using "$outdir/v3med_smdef_drought_coefficients.csv", replace
restore

preserve
use "$outdir/v3med_smdef_drought_ce_raw.dta", clear
export delimited using "$outdir/v3med_smdef_drought_conditional_effects.csv", replace
restore

cap erase "$outdir/v3med_smdef_drought_coef_raw.dta"
cap erase "$outdir/v3med_smdef_drought_ce_raw.dta"

* =============================================================================
* QUICK SIGN CHECK (diagnostic)
* =============================================================================
di _n "=== Key sign check (L0, reduced ctrl): a3, b, Index across 6 sources ==="
import delimited "$outdir/v3med_smdef_drought_coefficients.csv", clear
gen tag = ""
replace tag = "a1"    if equation == "mediator" & term == "D_full"
replace tag = "a3"    if equation == "mediator" & term == "SR_x_D_full"
replace tag = "b"     if equation == "outcome"  & term == "SMdef"
replace tag = "c3"    if equation == "outcome"  & term == "SR_x_D_full"
keep if fe_level == "L0" & ctrl_version == "reduced" & tag != ""
sort sm_source tag
list sm_label tag b se p, sepby(sm_label) noobs

log close
di "=== v3med_step2b_drought_smdef.do COMPLETE ==="
