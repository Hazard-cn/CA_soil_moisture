* =============================================================================
* v3_step4_full_coefs.do
* Purpose: Extract ALL coefficients from Spec(1)-(4) x 6 windows x 3 SM sources
*          Including main effects (D, W, H, SR) + all interactions
* Author:  YangSu + Claude
* Date:    2026-04-06
* Input:   data/processed/v3_analysis_ready.dta
* Output:  output/tables/v3_step4_full_coefs.csv
* =============================================================================

clear all
set more off
set seed 42

* Load macros (paths, controls, RHS)
do "C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata/v3_macros_include.do"

log using "$logdir/v3_step4_full_coefs_20260406.log", replace

use "$outdata/v3_analysis_ready.dta", clear
xtset grid_id year

* =============================================================================
* POSTFILE SETUP — ALL coefficients
* =============================================================================
tempname pf
postfile `pf' str10 window str6 spec str6 sm_src ///
    b_D se_D p_D ///
    b_W se_W p_W ///
    b_H se_H p_H ///
    b_SR se_SR p_SR ///
    b_SRD se_SRD p_SRD ///
    b_SRW se_SRW p_SRW ///
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
    using "$outdir/v3_step4_full_coefs.dta", replace

* =============================================================================
* LOOP OVER 6 WINDOWS
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

    * --- Variable names for this window ---
    local vD   "D`wlbl'"
    local vW   "W`wlbl'"
    local vH   "hdd_ge32`hsfx'"
    local vSR  "ca"
    local vSRD "SR_x_D`wlbl'"
    local vSRW "SR_x_W`wlbl'"
    local vSRH "SR_x_Heat`wlbl'"
    local vDH  "D_x_Heat`wlbl'"
    local vSRDH "SR_x_D_x_Heat`wlbl'"

    di "========================================================"
    di "WINDOW: `win'"
    di "========================================================"

    * ===================================================================
    * Spec(1): Basic direct buffering
    * ===================================================================
    reghdfe ln_yield ///
        `vD' `vW' `vH' `vSR' ///
        `vSRD' `vSRW' `vSRH' ///
        `ctrl' if main_sample == 1, ///
        absorb(grid_id year) vce(cluster grid_id)

    local dfr = e(df_r)
    post `pf' ("`win'") ("spec1") ("none") ///
        (_b[`vD']) (_se[`vD']) (2*ttail(`dfr', abs(_b[`vD']/_se[`vD']))) ///
        (_b[`vW']) (_se[`vW']) (2*ttail(`dfr', abs(_b[`vW']/_se[`vW']))) ///
        (_b[`vH']) (_se[`vH']) (2*ttail(`dfr', abs(_b[`vH']/_se[`vH']))) ///
        (_b[`vSR']) (_se[`vSR']) (2*ttail(`dfr', abs(_b[`vSR']/_se[`vSR']))) ///
        (_b[`vSRD']) (_se[`vSRD']) (2*ttail(`dfr', abs(_b[`vSRD']/_se[`vSRD']))) ///
        (_b[`vSRW']) (_se[`vSRW']) (2*ttail(`dfr', abs(_b[`vSRW']/_se[`vSRW']))) ///
        (_b[`vSRH']) (_se[`vSRH']) (2*ttail(`dfr', abs(_b[`vSRH']/_se[`vSRH']))) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (e(N)) (e(r2))

    * ===================================================================
    * Spec(2): Compound direct buffering
    * ===================================================================
    reghdfe ln_yield ///
        `vD' `vW' `vH' `vSR' ///
        `vSRD' `vSRW' `vSRH' ///
        `vDH' `vSRDH' ///
        `ctrl' if main_sample == 1, ///
        absorb(grid_id year) vce(cluster grid_id)

    local dfr = e(df_r)
    post `pf' ("`win'") ("spec2") ("none") ///
        (_b[`vD']) (_se[`vD']) (2*ttail(`dfr', abs(_b[`vD']/_se[`vD']))) ///
        (_b[`vW']) (_se[`vW']) (2*ttail(`dfr', abs(_b[`vW']/_se[`vW']))) ///
        (_b[`vH']) (_se[`vH']) (2*ttail(`dfr', abs(_b[`vH']/_se[`vH']))) ///
        (_b[`vSR']) (_se[`vSR']) (2*ttail(`dfr', abs(_b[`vSR']/_se[`vSR']))) ///
        (_b[`vSRD']) (_se[`vSRD']) (2*ttail(`dfr', abs(_b[`vSRD']/_se[`vSRD']))) ///
        (_b[`vSRW']) (_se[`vSRW']) (2*ttail(`dfr', abs(_b[`vSRW']/_se[`vSRW']))) ///
        (_b[`vSRH']) (_se[`vSRH']) (2*ttail(`dfr', abs(_b[`vSRH']/_se[`vSRH']))) ///
        (_b[`vDH']) (_se[`vDH']) (2*ttail(`dfr', abs(_b[`vDH']/_se[`vDH']))) ///
        (_b[`vSRDH']) (_se[`vSRDH']) (2*ttail(`dfr', abs(_b[`vSRDH']/_se[`vSRDH']))) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (.) (.) (.) ///
        (e(N)) (e(r2))

    * ===================================================================
    * Spec(3) and Spec(4): Loop over SM sources
    * ===================================================================
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

        * SM interaction variable names
        local smd  "`slbl'_x_D`wlbl'"
        local smh  "`slbl'_x_H`wlbl'"
        local smsr "`slbl'_x_SR`wlbl'"
        local smdh "`slbl'_x_DH`wlbl'"
        local smsrdh "`slbl'_x_SRDH`wlbl'"

        * ---------------------------------------------------------------
        * Spec(3): SM channel (no compound)
        * ---------------------------------------------------------------
        reghdfe ln_yield ///
            `vD' `vW' `vH' `vSR' ///
            `vSRD' `vSRW' `vSRH' ///
            `sm_mean' `smd' `smh' `smsr' ///
            `ctrl' if main_sample == 1, ///
            absorb(grid_id year) vce(cluster grid_id)

        local dfr = e(df_r)
        post `pf' ("`win'") ("spec3") ("`src'") ///
            (_b[`vD']) (_se[`vD']) (2*ttail(`dfr', abs(_b[`vD']/_se[`vD']))) ///
            (_b[`vW']) (_se[`vW']) (2*ttail(`dfr', abs(_b[`vW']/_se[`vW']))) ///
            (_b[`vH']) (_se[`vH']) (2*ttail(`dfr', abs(_b[`vH']/_se[`vH']))) ///
            (_b[`vSR']) (_se[`vSR']) (2*ttail(`dfr', abs(_b[`vSR']/_se[`vSR']))) ///
            (_b[`vSRD']) (_se[`vSRD']) (2*ttail(`dfr', abs(_b[`vSRD']/_se[`vSRD']))) ///
            (_b[`vSRW']) (_se[`vSRW']) (2*ttail(`dfr', abs(_b[`vSRW']/_se[`vSRW']))) ///
            (_b[`vSRH']) (_se[`vSRH']) (2*ttail(`dfr', abs(_b[`vSRH']/_se[`vSRH']))) ///
            (.) (.) (.) ///
            (.) (.) (.) ///
            (_b[`sm_mean']) (_se[`sm_mean']) (2*ttail(`dfr', abs(_b[`sm_mean']/_se[`sm_mean']))) ///
            (_b[`smd']) (_se[`smd']) (2*ttail(`dfr', abs(_b[`smd']/_se[`smd']))) ///
            (_b[`smh']) (_se[`smh']) (2*ttail(`dfr', abs(_b[`smh']/_se[`smh']))) ///
            (_b[`smsr']) (_se[`smsr']) (2*ttail(`dfr', abs(_b[`smsr']/_se[`smsr']))) ///
            (.) (.) (.) ///
            (.) (.) (.) ///
            (e(N)) (e(r2))

        * ---------------------------------------------------------------
        * Spec(4): Full model (compound + SM full suite)
        * ---------------------------------------------------------------
        reghdfe ln_yield ///
            `vD' `vW' `vH' `vSR' ///
            `vSRD' `vSRW' `vSRH' ///
            `vDH' `vSRDH' ///
            `sm_mean' `smd' `smh' `smsr' ///
            `smdh' `smsrdh' ///
            `ctrl' if main_sample == 1, ///
            absorb(grid_id year) vce(cluster grid_id)

        local dfr = e(df_r)
        post `pf' ("`win'") ("spec4") ("`src'") ///
            (_b[`vD']) (_se[`vD']) (2*ttail(`dfr', abs(_b[`vD']/_se[`vD']))) ///
            (_b[`vW']) (_se[`vW']) (2*ttail(`dfr', abs(_b[`vW']/_se[`vW']))) ///
            (_b[`vH']) (_se[`vH']) (2*ttail(`dfr', abs(_b[`vH']/_se[`vH']))) ///
            (_b[`vSR']) (_se[`vSR']) (2*ttail(`dfr', abs(_b[`vSR']/_se[`vSR']))) ///
            (_b[`vSRD']) (_se[`vSRD']) (2*ttail(`dfr', abs(_b[`vSRD']/_se[`vSRD']))) ///
            (_b[`vSRW']) (_se[`vSRW']) (2*ttail(`dfr', abs(_b[`vSRW']/_se[`vSRW']))) ///
            (_b[`vSRH']) (_se[`vSRH']) (2*ttail(`dfr', abs(_b[`vSRH']/_se[`vSRH']))) ///
            (_b[`vDH']) (_se[`vDH']) (2*ttail(`dfr', abs(_b[`vDH']/_se[`vDH']))) ///
            (_b[`vSRDH']) (_se[`vSRDH']) (2*ttail(`dfr', abs(_b[`vSRDH']/_se[`vSRDH']))) ///
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
use "$outdir/v3_step4_full_coefs.dta", clear
export delimited using "$outdir/v3_step4_full_coefs.csv", replace

di "=== SUMMARY ==="
list window spec sm_src b_D b_SRD b_SRH b_DH b_SRDH N, sep(8) noobs

log close
di "=== v3_step4_full_coefs.do COMPLETE ==="
