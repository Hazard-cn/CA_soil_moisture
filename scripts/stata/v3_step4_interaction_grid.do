* =============================================================================
* v3_step4_interaction_grid.do
* Purpose: 4 specs x 3 SM sources x 6 windows = 48 regressions
*          Complete evidence matrix with postfile output
*          Extends v2_step4 by adding v3pre30 window
* Author:  YangSu + Claude
* Date:    2026-04-05
* Input:   data/processed/v3_analysis_ready.dta
* Output:  output/tables/v3_step4_interaction_grid.csv
* =============================================================================

clear all
set more off
set seed 42

* Load macros (paths, controls, RHS)
do "C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata/v3_macros_include.do"

log using "$logdir/v3_step4_interaction_grid_20260405.log", replace

use "$outdata/v3_analysis_ready.dta", clear
xtset grid_id year

* =============================================================================
* POSTFILE SETUP
* =============================================================================
tempname pf
postfile `pf' str10 window str6 spec str6 sm_src ///
    b_SRD se_SRD p_SRD ///
    b_SRH se_SRH p_SRH ///
    b_DH se_DH p_DH ///
    b_SRDH se_SRDH p_SRDH ///
    b_SM se_SM p_SM ///
    b_SMD se_SMD p_SMD ///
    b_SMH se_SMH p_SMH ///
    b_SMSR se_SMSR p_SMSR ///
    b_SMDH se_SMDH p_SMDH ///
    b_SMSRDH se_SMSRDH p_SMSRDH ///
    N r2 ///
    using "$outdir/v3_step4_interaction_grid.dta", replace

* =============================================================================
* LOOP OVER 6 WINDOWS x SPECS x SM SOURCES
* =============================================================================

foreach win in full v3pre30 v3pm10 hepm10 v3he hema {

    * --- Determine variable suffixes ---
    local wlbl "_`win'"
    if "`win'" == "full" {
        local hsfx ""
        local ctrl "$CTRL_full"
    }
    else {
        local hsfx "_`win'"
        local ctrl "${CTRL_`win'}"
    }

    di "========================================================"
    di "WINDOW: `win'"
    di "========================================================"

    * --- Spec(1): Basic direct buffering ---
    reghdfe ln_yield ///
        D`wlbl' W`wlbl' hdd_ge32`hsfx' ca ///
        SR_x_D`wlbl' SR_x_W`wlbl' SR_x_Heat`wlbl' ///
        `ctrl' if main_sample == 1, ///
        absorb(grid_id year) vce(cluster grid_id)

    local dfr = e(df_r)
    post `pf' ("`win'") ("spec1") ("none") ///
        (_b[SR_x_D`wlbl']) (_se[SR_x_D`wlbl']) (2*ttail(`dfr', abs(_b[SR_x_D`wlbl']/_se[SR_x_D`wlbl']))) ///
        (_b[SR_x_Heat`wlbl']) (_se[SR_x_Heat`wlbl']) (2*ttail(`dfr', abs(_b[SR_x_Heat`wlbl']/_se[SR_x_Heat`wlbl']))) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (e(N)) (e(r2))

    * --- Spec(2): Compound direct buffering ---
    reghdfe ln_yield ///
        D`wlbl' W`wlbl' hdd_ge32`hsfx' ca ///
        SR_x_D`wlbl' SR_x_W`wlbl' SR_x_Heat`wlbl' ///
        D_x_Heat`wlbl' SR_x_D_x_Heat`wlbl' ///
        `ctrl' if main_sample == 1, ///
        absorb(grid_id year) vce(cluster grid_id)

    local dfr = e(df_r)
    post `pf' ("`win'") ("spec2") ("none") ///
        (_b[SR_x_D`wlbl']) (_se[SR_x_D`wlbl']) (2*ttail(`dfr', abs(_b[SR_x_D`wlbl']/_se[SR_x_D`wlbl']))) ///
        (_b[SR_x_Heat`wlbl']) (_se[SR_x_Heat`wlbl']) (2*ttail(`dfr', abs(_b[SR_x_Heat`wlbl']/_se[SR_x_Heat`wlbl']))) ///
        (_b[D_x_Heat`wlbl']) (_se[D_x_Heat`wlbl']) (2*ttail(`dfr', abs(_b[D_x_Heat`wlbl']/_se[D_x_Heat`wlbl']))) ///
        (_b[SR_x_D_x_Heat`wlbl']) (_se[SR_x_D_x_Heat`wlbl']) (2*ttail(`dfr', abs(_b[SR_x_D_x_Heat`wlbl']/_se[SR_x_D_x_Heat`wlbl']))) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (e(N)) (e(r2))

    * --- Spec(3) and Spec(4): Loop over SM sources ---
    foreach src in gleam swsm era5l {

        * SM variable names
        if "`src'" == "gleam" {
            local sm_mean "gleam_smrz_mean`hsfx'"
            local slbl "gsm"
        }
        else if "`src'" == "swsm" {
            local sm_mean "swsm_l3_mean`hsfx'"
            local slbl "ssm"
        }
        else {
            local sm_mean "era5l_swvl3_mean`hsfx'"
            local slbl "esm"
        }

        * Interaction variable names
        local smd  "`slbl'_x_D`wlbl'"
        local smh  "`slbl'_x_H`wlbl'"
        local smsr "`slbl'_x_SR`wlbl'"
        local smdh "`slbl'_x_DH`wlbl'"
        local smsrdh "`slbl'_x_SRDH`wlbl'"

        * --- Spec(3): SM channel (no compound) ---
        reghdfe ln_yield ///
            D`wlbl' W`wlbl' hdd_ge32`hsfx' ca ///
            SR_x_D`wlbl' SR_x_W`wlbl' SR_x_Heat`wlbl' ///
            `sm_mean' `smd' `smh' `smsr' ///
            `ctrl' if main_sample == 1, ///
            absorb(grid_id year) vce(cluster grid_id)

        local dfr = e(df_r)
        post `pf' ("`win'") ("spec3") ("`src'") ///
            (_b[SR_x_D`wlbl']) (_se[SR_x_D`wlbl']) (2*ttail(`dfr', abs(_b[SR_x_D`wlbl']/_se[SR_x_D`wlbl']))) ///
            (_b[SR_x_Heat`wlbl']) (_se[SR_x_Heat`wlbl']) (2*ttail(`dfr', abs(_b[SR_x_Heat`wlbl']/_se[SR_x_Heat`wlbl']))) ///
            (.) (.) (.) ///
            (.) (.) (.) ///
            (_b[`sm_mean']) (_se[`sm_mean']) (2*ttail(`dfr', abs(_b[`sm_mean']/_se[`sm_mean']))) ///
            (_b[`smd']) (_se[`smd']) (2*ttail(`dfr', abs(_b[`smd']/_se[`smd']))) ///
            (_b[`smh']) (_se[`smh']) (2*ttail(`dfr', abs(_b[`smh']/_se[`smh']))) ///
            (_b[`smsr']) (_se[`smsr']) (2*ttail(`dfr', abs(_b[`smsr']/_se[`smsr']))) ///
            (.) (.) (.) ///
            (.) (.) (.) ///
            (e(N)) (e(r2))

        * --- Spec(4): Full model (compound + SM full suite) ---
        reghdfe ln_yield ///
            D`wlbl' W`wlbl' hdd_ge32`hsfx' ca ///
            SR_x_D`wlbl' SR_x_W`wlbl' SR_x_Heat`wlbl' ///
            D_x_Heat`wlbl' SR_x_D_x_Heat`wlbl' ///
            `sm_mean' `smd' `smh' `smsr' ///
            `smdh' `smsrdh' ///
            `ctrl' if main_sample == 1, ///
            absorb(grid_id year) vce(cluster grid_id)

        local dfr = e(df_r)
        post `pf' ("`win'") ("spec4") ("`src'") ///
            (_b[SR_x_D`wlbl']) (_se[SR_x_D`wlbl']) (2*ttail(`dfr', abs(_b[SR_x_D`wlbl']/_se[SR_x_D`wlbl']))) ///
            (_b[SR_x_Heat`wlbl']) (_se[SR_x_Heat`wlbl']) (2*ttail(`dfr', abs(_b[SR_x_Heat`wlbl']/_se[SR_x_Heat`wlbl']))) ///
            (_b[D_x_Heat`wlbl']) (_se[D_x_Heat`wlbl']) (2*ttail(`dfr', abs(_b[D_x_Heat`wlbl']/_se[D_x_Heat`wlbl']))) ///
            (_b[SR_x_D_x_Heat`wlbl']) (_se[SR_x_D_x_Heat`wlbl']) (2*ttail(`dfr', abs(_b[SR_x_D_x_Heat`wlbl']/_se[SR_x_D_x_Heat`wlbl']))) ///
            (_b[`sm_mean']) (_se[`sm_mean']) (2*ttail(`dfr', abs(_b[`sm_mean']/_se[`sm_mean']))) ///
            (_b[`smd']) (_se[`smd']) (2*ttail(`dfr', abs(_b[`smd']/_se[`smd']))) ///
            (_b[`smh']) (_se[`smh']) (2*ttail(`dfr', abs(_b[`smh']/_se[`smh']))) ///
            (_b[`smsr']) (_se[`smsr']) (2*ttail(`dfr', abs(_b[`smsr']/_se[`smsr']))) ///
            (_b[`smdh']) (_se[`smdh']) (2*ttail(`dfr', abs(_b[`smdh']/_se[`smdh']))) ///
            (_b[`smsrdh']) (_se[`smsrdh']) (2*ttail(`dfr', abs(_b[`smsrdh']/_se[`smsrdh']))) ///
            (e(N)) (e(r2))

    }  // end sm source loop
}  // end window loop

postclose `pf'

* =============================================================================
* EXPORT TO CSV
* =============================================================================
use "$outdir/v3_step4_interaction_grid.dta", clear
list window spec sm_src b_SRD p_SRD b_SRH p_SRH b_SRDH p_SRDH N, sep(8) noobs
export delimited using "$outdir/v3_step4_interaction_grid.csv", replace

* =============================================================================
* COMPUTE ATTENUATION MATRIX
* =============================================================================
di "========================================================"
di "ATTENUATION MATRIX: (1)->(3) for SR_x_D and SR_x_H"
di "========================================================"

preserve
gen attn_SRD = .
gen attn_SRH = .

levelsof window, local(wins)
foreach w of local wins {
    * Get Spec(1) baseline
    sum b_SRD if window == "`w'" & spec == "spec1", meanonly
    local base_SRD = r(mean)
    sum b_SRH if window == "`w'" & spec == "spec1", meanonly
    local base_SRH = r(mean)

    * Compute attenuation for Spec(3)
    replace attn_SRD = 100 * (1 - b_SRD / `base_SRD') if window == "`w'" & spec == "spec3"
    replace attn_SRH = 100 * (1 - b_SRH / `base_SRH') if window == "`w'" & spec == "spec3"
}

di "=== Attenuation (1)->(3): SM channel share of SR buffering ==="
list window sm_src attn_SRD attn_SRH if spec == "spec3", sep(3) noobs

di "========================================================"
di "ATTENUATION MATRIX: (2)->(4) for SR_x_D_x_H"
di "========================================================"

gen attn_SRDH = .
foreach w of local wins {
    sum b_SRDH if window == "`w'" & spec == "spec2", meanonly
    local base_SRDH = r(mean)
    if `base_SRDH' != 0 {
        replace attn_SRDH = 100 * (1 - b_SRDH / `base_SRDH') if window == "`w'" & spec == "spec4"
    }
}

di "=== Attenuation (2)->(4): SM channel share of compound buffering ==="
list window sm_src attn_SRDH if spec == "spec4", sep(3) noobs

export delimited using "$outdir/v3_step4_attenuation.csv", replace
restore

log close
di "=== v3_step4_interaction_grid.do COMPLETE ==="
