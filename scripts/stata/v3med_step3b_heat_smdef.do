* =============================================================================
* v3med_step3b_heat_smdef.do
* Purpose: Path A repair of Model 8 heat module using SM_def as mediator.
*
*          Mediator eq: SMdef_s = a1h*H + a2h*ca + a3h*(H×ca) + rho_d*D + Z + FE
*          Outcome eq:  lnY = c1h*H + c2h*ca + c3h*(H×ca) + b_h*SMdef_s + rho_dy*D + Z + FE
*
* Author:  YangSu + Claude
* Date:    2026-04-16
* Input:   data/processed/v3med_analysis_ready_plus.dta
* Output:  output/tables/v3med_smdef_heat_coefficients.csv
*          output/tables/v3med_smdef_heat_conditional_effects.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3med_macros_include.do"

log using "$logdir/v3med_step3b_heat_smdef.log", replace

use "$datadir/v3med_analysis_ready_plus.dta", clear
xtset grid_id year
keep if v3med_common == 1
di "Working sample N = " _N

_pctile ca, p(25 50 75)
scalar ca_p25 = r(r1)
scalar ca_p50 = r(r2)
scalar ca_p75 = r(r3)

tempname pf_coef
postfile `pf_coef' str4 fe_level str10 ctrl_version str25 sm_source ///
    str12 sm_label str12 equation str25 term ///
    double(b se p) long(N) double(r2) ///
    using "$outdir/v3med_smdef_heat_coef_raw.dta", replace

tempname pf_ce
postfile `pf_ce' str4 fe_level str10 ctrl_version str25 sm_source ///
    str12 sm_label str6 ca_level double(ca_value) ///
    str5 effect double(value) ///
    using "$outdir/v3med_smdef_heat_ce_raw.dta", replace

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
            di "FE=`fe_tag'  CTRL=`cv'  HEAT SMdef_`s' (`sm_lbl')"
            di "=============================================="

            * Mediator eq (H causal path on SM deficit)
            reghdfe SMdef_`s' hdd_ge32 ca SR_x_Heat_full D_full `ctrl_list', ///
                absorb(`abs_spec') vce(cluster `cl_spec')

            local nn_m = e(N)
            local rr_m = e(r2)

            foreach v in hdd_ge32 ca SR_x_Heat_full D_full {
                local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
                post `pf_coef' ("`fe_tag'") ("`cv'") ("`s'") ///
                    ("`sm_lbl'") ("mediator") ("`v'") ///
                    (_b[`v']) (_se[`v']) (`pval') (`nn_m') (`rr_m')
            }

            local a1h = _b[hdd_ge32]
            local a3h = _b[SR_x_Heat_full]

            * Outcome eq
            reghdfe ln_yield hdd_ge32 ca SR_x_Heat_full SMdef_`s' D_full `ctrl_list', ///
                absorb(`abs_spec') vce(cluster `cl_spec')

            local nn_y = e(N)
            local rr_y = e(r2)

            foreach v in hdd_ge32 ca SR_x_Heat_full SMdef_`s' D_full {
                local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
                local tname = cond("`v'" == "SMdef_`s'", "SMdef", "`v'")
                post `pf_coef' ("`fe_tag'") ("`cv'") ("`s'") ///
                    ("`sm_lbl'") ("outcome") ("`tname'") ///
                    (_b[`v']) (_se[`v']) (`pval') (`nn_y') (`rr_y')
            }

            local bh = _b[SMdef_`s']
            local c1h = _b[hdd_ge32]
            local c3h = _b[SR_x_Heat_full]

            foreach clbl in P25 P50 P75 {
                local r = ca_`=lower("`clbl'")'
                local ie = (`a1h' + `a3h' * `r') * `bh'
                local de = `c1h' + `c3h' * `r'
                local te = `de' + `ie'
                post `pf_ce' ("`fe_tag'") ("`cv'") ("`s'") ///
                    ("`sm_lbl'") ("`clbl'") (`r') ("IE") (`ie')
                post `pf_ce' ("`fe_tag'") ("`cv'") ("`s'") ///
                    ("`sm_lbl'") ("`clbl'") (`r') ("DE") (`de')
                post `pf_ce' ("`fe_tag'") ("`cv'") ("`s'") ///
                    ("`sm_lbl'") ("`clbl'") (`r') ("TE") (`te')
            }

            local idx = `a3h' * `bh'
            post `pf_ce' ("`fe_tag'") ("`cv'") ("`s'") ///
                ("`sm_lbl'") ("Index") (.) ("Index") (`idx')

        }
    }
}

postclose `pf_coef'
postclose `pf_ce'

preserve
use "$outdir/v3med_smdef_heat_coef_raw.dta", clear
export delimited using "$outdir/v3med_smdef_heat_coefficients.csv", replace
restore

preserve
use "$outdir/v3med_smdef_heat_ce_raw.dta", clear
export delimited using "$outdir/v3med_smdef_heat_conditional_effects.csv", replace
restore

cap erase "$outdir/v3med_smdef_heat_coef_raw.dta"
cap erase "$outdir/v3med_smdef_heat_ce_raw.dta"

log close
di "=== v3med_step3b_heat_smdef.do COMPLETE ==="
