* =============================================================================
* v3sub_step3_sm_response.do
* Purpose: Structure 3 subsample regressions, SM ~ SR + D + H without W terms
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3sub_macros_include.do"

log using "$logdir/v3sub_step3_sm_response.log", replace

use "$subdata", clear
xtset grid_id year

tempname pf
postfile `pf' str12 split_type str12 subgroup str10 window str10 sm_src ///
    b_D se_D p_D ///
    b_H se_H p_H ///
    b_SR se_SR p_SR ///
    b_SRD se_SRD p_SRD ///
    b_SRH se_SRH p_SRH ///
    N ///
    using "$outdir/v3sub_structure3.dta", replace

foreach split in zone irrigation {
    local svar = cond("`split'" == "zone", "maize_zone", "irr_group")
    local groups "NE HHH SW SH NW Other"
    if "`split'" == "irrigation" {
        local groups "low_irr high_irr"
    }

    foreach g in `groups' {
        foreach w in full v3pre30 v3pm10 hepm10 v3he hema {
            foreach slbl in gleam swsm era5l {
                local smvar ${SMVAR_sub_`w'_`slbl'}
                local hsfx = cond("`w'" == "full", "", "_`w'")

                cap noi reghdfe `smvar' ${RHS_sub_sm_`w'_`slbl'} ${CTRL_`w'} ///
                    if main_sample == 1 & `svar' == "`g'", absorb(grid_id year) vce(cluster grid_id)

                if _rc == 0 {
                    local dfr = e(df_r)
                    post `pf' ("`split'") ("`g'") ("`w'") ("`slbl'") ///
                        (_b[D_`w']) (_se[D_`w']) ///
                        (2*ttail(`dfr', abs(_b[D_`w']/_se[D_`w']))) ///
                        (_b[hdd_ge32`hsfx']) (_se[hdd_ge32`hsfx']) ///
                        (2*ttail(`dfr', abs(_b[hdd_ge32`hsfx']/_se[hdd_ge32`hsfx']))) ///
                        (_b[ca]) (_se[ca]) ///
                        (2*ttail(`dfr', abs(_b[ca]/_se[ca]))) ///
                        (_b[SR_x_D_`w']) (_se[SR_x_D_`w']) ///
                        (2*ttail(`dfr', abs(_b[SR_x_D_`w']/_se[SR_x_D_`w']))) ///
                        (_b[SR_x_Heat_`w']) (_se[SR_x_Heat_`w']) ///
                        (2*ttail(`dfr', abs(_b[SR_x_Heat_`w']/_se[SR_x_Heat_`w']))) ///
                        (e(N))
                }
                else {
                    post `pf' ("`split'") ("`g'") ("`w'") ("`slbl'") ///
                        (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (0)
                }
            }
        }
    }
}

postclose `pf'

preserve
use "$outdir/v3sub_structure3.dta", clear
export delimited using "$outdir/v3sub_structure3.csv", replace
restore

log close
di "=== v3sub_step3_sm_response.do COMPLETE ==="
