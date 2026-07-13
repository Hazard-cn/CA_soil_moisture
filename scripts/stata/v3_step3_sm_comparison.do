* =============================================================================
* v3_step3_sm_comparison.do
* Purpose: SM source comparison — attenuation + a-path (3 SM x 6 windows)
* Author:  YangSu + Claude
* Date:    2026-04-04
* Input:   data/processed/v3_analysis_ready.dta
* Output:  output/tables/v3_step3_attenuation.csv
*          output/tables/v3_step3_apath.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3_macros_include.do"

log using "$logdir/v3_step3_sm_comparison.log", replace

use "$outdata/v3_analysis_ready.dta", clear
xtset grid_id year

* =============================================================================
* PART A: Attenuation — Spec(1) vs Spec(3) across 6 windows x 3 SM sources
* =============================================================================
di "========================================================"
di "PART A: Attenuation Matrix"
di "========================================================"

tempname pf
postfile `pf' str10 window str10 sm_src ///
    b1_SRD se1_SRD b3_SRD se3_SRD att_SRD ///
    b1_SRH se1_SRH b3_SRH se3_SRH att_SRH ///
    N ///
    using "$outdir/v3_step3_attenuation.dta", replace

foreach w in full v3pre30 v3pm10 hepm10 v3he hema {
    di _n "--- Window: `w' ---"

    * Spec(1) baseline for this window
    qui reghdfe ln_yield ${RHS_spec1_`w'} ${CTRL_`w'} ///
        if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)

    local b1_SRD = _b[SR_x_D_`w']
    local se1_SRD = _se[SR_x_D_`w']
    local b1_SRH = _b[SR_x_Heat_`w']
    local se1_SRH = _se[SR_x_Heat_`w']
    local N_obs = e(N)

    * Spec(3) for each SM source
    foreach slbl in gleam swsm era5l {
        qui reghdfe ln_yield ${RHS_spec3_`w'_`slbl'} ${CTRL_`w'} ///
            if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)

        local b3_SRD = _b[SR_x_D_`w']
        local se3_SRD = _se[SR_x_D_`w']
        local b3_SRH = _b[SR_x_Heat_`w']
        local se3_SRH = _se[SR_x_Heat_`w']

        local att_SRD = cond(`b1_SRD' != 0, 100 * (1 - `b3_SRD'/`b1_SRD'), .)
        local att_SRH = cond(`b1_SRH' != 0, 100 * (1 - `b3_SRH'/`b1_SRH'), .)

        di "`w' x `slbl': SRxD att=" %5.1f `att_SRD' "%, SRxH att=" %5.1f `att_SRH' "%"

        post `pf' ("`w'") ("`slbl'") ///
            (`b1_SRD') (`se1_SRD') (`b3_SRD') (`se3_SRD') (`att_SRD') ///
            (`b1_SRH') (`se1_SRH') (`b3_SRH') (`se3_SRH') (`att_SRH') ///
            (`N_obs')
    }
}

postclose `pf'

preserve
use "$outdir/v3_step3_attenuation.dta", clear
format b* se* %9.4f
format att* %6.1f
list, sep(3) noobs
export delimited using "$outdir/v3_step3_attenuation.csv", replace
restore

* =============================================================================
* PART B: a-path — D -> SM (with SR moderation)
*   SM_it = alpha*D + beta*H + gamma*SR + delta*SR_x_D + lambda*SR_x_H + Z + FE
* =============================================================================
di _n "========================================================"
di "PART B: a-path (Drought -> SM)"
di "========================================================"

tempname pf2
postfile `pf2' str10 window str10 sm_src ///
    b_D se_D p_D ///
    b_SRD se_SRD p_SRD ///
    b_SR se_SR p_SR ///
    N ///
    using "$outdir/v3_step3_apath.dta", replace

foreach w in full v3pre30 v3pm10 hepm10 v3he hema {
    local wsfx = cond("`w'" == "full", "", "_`w'")
    local h_var = cond("`w'" == "full", "hdd_ge32", "hdd_ge32_`w'")

    di _n "--- a-path window: `w' ---"

    foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
        local slbl = cond("`src'" == "gleam_smrz", "gleam", ///
                     cond("`src'" == "swsm_l3", "swsm", "era5l"))

        qui reghdfe `src'_mean`wsfx' ///
            D_`w' W_`w' `h_var' ca ///
            SR_x_D_`w' SR_x_Heat_`w' ///
            ${CTRL_`w'} if main_sample == 1, ///
            absorb(grid_id year) vce(cluster grid_id)

        local b_D = _b[D_`w']
        local se_D = _se[D_`w']
        local p_D = 2*ttail(e(df_r), abs(`b_D'/`se_D'))

        local b_SRD = _b[SR_x_D_`w']
        local se_SRD = _se[SR_x_D_`w']
        local p_SRD = 2*ttail(e(df_r), abs(`b_SRD'/`se_SRD'))

        local b_SR = _b[ca]
        local se_SR = _se[ca]
        local p_SR = 2*ttail(e(df_r), abs(`b_SR'/`se_SR'))

        di "`w' x `slbl': D->SM = " %7.4f `b_D' " (" %7.4f `se_D' "), " ///
           "SRxD->SM = " %7.4f `b_SRD' " (" %7.4f `se_SRD' ")"

        post `pf2' ("`w'") ("`slbl'") ///
            (`b_D') (`se_D') (`p_D') ///
            (`b_SRD') (`se_SRD') (`p_SRD') ///
            (`b_SR') (`se_SR') (`p_SR') ///
            (e(N))
    }
}

postclose `pf2'

preserve
use "$outdir/v3_step3_apath.dta", clear
format b_* se_* %9.4f
format p_* %7.4f
list, sep(3) noobs
export delimited using "$outdir/v3_step3_apath.csv", replace
restore

log close
di "=== v3_step3_sm_comparison.do COMPLETE ==="
