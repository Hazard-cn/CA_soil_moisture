* =============================================================================
* v3_step5_robustness.do
* Purpose: Simplified robustness — FE, heat threshold, year-drop, prov-yr windows
* Author:  YangSu + Claude
* Date:    2026-04-04
* Input:   data/processed/v3_analysis_ready.dta
* Output:  output/tables/v3_step5_robustness.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3_macros_include.do"

log using "$logdir/v3_step5_robustness.log", replace

use "$outdata/v3_analysis_ready.dta", clear
xtset grid_id year

* =============================================================================
* POSTFILE: all robustness results in one file
* =============================================================================
tempname pf
postfile `pf' str20 test str10 variant str10 window ///
    b_SRD se_SRD p_SRD ///
    b_SRH se_SRH p_SRH ///
    b_DH se_DH p_DH ///
    b_SRDH se_SRDH p_SRDH ///
    r2 N ///
    using "$outdir/v3_step5_robustness.dta", replace

* =============================================================================
* TEST 1: FE Sensitivity — grid+year vs prov_year (full season, Spec 2)
* =============================================================================
di "========================================================"
di "TEST 1: FE Sensitivity"
di "========================================================"

* Baseline: grid + year
eststo fe_gy: reghdfe ln_yield $RHS_spec2_full $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)

post `pf' ("fe_sensitivity") ("grid_yr") ("full") ///
    (_b[SR_x_D_full]) (_se[SR_x_D_full]) ///
    (2*ttail(e(df_r), abs(_b[SR_x_D_full]/_se[SR_x_D_full]))) ///
    (_b[SR_x_Heat_full]) (_se[SR_x_Heat_full]) ///
    (2*ttail(e(df_r), abs(_b[SR_x_Heat_full]/_se[SR_x_Heat_full]))) ///
    (_b[D_x_Heat_full]) (_se[D_x_Heat_full]) ///
    (2*ttail(e(df_r), abs(_b[D_x_Heat_full]/_se[D_x_Heat_full]))) ///
    (_b[SR_x_D_x_Heat_full]) (_se[SR_x_D_x_Heat_full]) ///
    (2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat_full]/_se[SR_x_D_x_Heat_full]))) ///
    (e(r2)) (e(N))

* Province x Year FE
eststo fe_py: reghdfe ln_yield $RHS_spec2_full $CTRL_full ///
    if main_sample == 1, absorb(grid_id prov_year) vce(cluster grid_id)

post `pf' ("fe_sensitivity") ("prov_yr") ("full") ///
    (_b[SR_x_D_full]) (_se[SR_x_D_full]) ///
    (2*ttail(e(df_r), abs(_b[SR_x_D_full]/_se[SR_x_D_full]))) ///
    (_b[SR_x_Heat_full]) (_se[SR_x_Heat_full]) ///
    (2*ttail(e(df_r), abs(_b[SR_x_Heat_full]/_se[SR_x_Heat_full]))) ///
    (_b[D_x_Heat_full]) (_se[D_x_Heat_full]) ///
    (2*ttail(e(df_r), abs(_b[D_x_Heat_full]/_se[D_x_Heat_full]))) ///
    (_b[SR_x_D_x_Heat_full]) (_se[SR_x_D_x_Heat_full]) ///
    (2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat_full]/_se[SR_x_D_x_Heat_full]))) ///
    (e(r2)) (e(N))

* =============================================================================
* TEST 2: Heat Threshold (30/32/35°C, full season, Spec 2)
* =============================================================================
di _n "========================================================"
di "TEST 2: Heat Threshold Sensitivity"
di "========================================================"

foreach thr in 30 32 35 {
    di _n "--- Threshold: `thr'°C ---"

    * Construct temporary interactions for this threshold
    tempvar h_thr sr_h d_h sr_d_h
    gen `h_thr' = hdd_ge`thr'
    gen `sr_h' = ca * hdd_ge`thr'
    gen `d_h' = D_full * hdd_ge`thr'
    gen `sr_d_h' = ca * D_full * hdd_ge`thr'

    eststo ht_`thr': reghdfe ln_yield D_full W_full `h_thr' ca ///
        SR_x_D_full SR_x_W_full `sr_h' ///
        `d_h' `sr_d_h' ///
        $CTRL_full if main_sample == 1, ///
        absorb(grid_id year) vce(cluster grid_id)

    post `pf' ("heat_threshold") ("`thr'C") ("full") ///
        (_b[SR_x_D_full]) (_se[SR_x_D_full]) ///
        (2*ttail(e(df_r), abs(_b[SR_x_D_full]/_se[SR_x_D_full]))) ///
        (_b[`sr_h']) (_se[`sr_h']) ///
        (2*ttail(e(df_r), abs(_b[`sr_h']/_se[`sr_h']))) ///
        (_b[`d_h']) (_se[`d_h']) ///
        (2*ttail(e(df_r), abs(_b[`d_h']/_se[`d_h']))) ///
        (_b[`sr_d_h']) (_se[`sr_d_h']) ///
        (2*ttail(e(df_r), abs(_b[`sr_d_h']/_se[`sr_d_h']))) ///
        (e(r2)) (e(N))
}

* =============================================================================
* TEST 3: Year-Drop (leave-one-year-out, Spec 2, full season)
* =============================================================================
di _n "========================================================"
di "TEST 3: Year-Drop Sensitivity"
di "========================================================"

forvalues yr = 2016/2019 {
    di _n "--- Dropping `yr' ---"

    eststo yd_`yr': reghdfe ln_yield $RHS_spec2_full $CTRL_full ///
        if main_sample == 1 & year != `yr', ///
        absorb(grid_id year) vce(cluster grid_id)

    post `pf' ("year_drop") ("drop`yr'") ("full") ///
        (_b[SR_x_D_full]) (_se[SR_x_D_full]) ///
        (2*ttail(e(df_r), abs(_b[SR_x_D_full]/_se[SR_x_D_full]))) ///
        (_b[SR_x_Heat_full]) (_se[SR_x_Heat_full]) ///
        (2*ttail(e(df_r), abs(_b[SR_x_Heat_full]/_se[SR_x_Heat_full]))) ///
        (_b[D_x_Heat_full]) (_se[D_x_Heat_full]) ///
        (2*ttail(e(df_r), abs(_b[D_x_Heat_full]/_se[D_x_Heat_full]))) ///
        (_b[SR_x_D_x_Heat_full]) (_se[SR_x_D_x_Heat_full]) ///
        (2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat_full]/_se[SR_x_D_x_Heat_full]))) ///
        (e(r2)) (e(N))
}

* =============================================================================
* TEST 4: Province-Year FE across 6 windows (Spec 2)
* =============================================================================
di _n "========================================================"
di "TEST 4: Province-Year FE x 6 Windows"
di "========================================================"

foreach w in full v3pre30 v3pm10 hepm10 v3he hema {
    di _n "--- Prov-Year FE: `w' ---"

    eststo py_`w': reghdfe ln_yield ${RHS_spec2_`w'} ${CTRL_`w'} ///
        if main_sample == 1, absorb(grid_id prov_year) vce(cluster grid_id)

    post `pf' ("provyr_windows") ("`w'") ("`w'") ///
        (_b[SR_x_D_`w']) (_se[SR_x_D_`w']) ///
        (2*ttail(e(df_r), abs(_b[SR_x_D_`w']/_se[SR_x_D_`w']))) ///
        (_b[SR_x_Heat_`w']) (_se[SR_x_Heat_`w']) ///
        (2*ttail(e(df_r), abs(_b[SR_x_Heat_`w']/_se[SR_x_Heat_`w']))) ///
        (_b[D_x_Heat_`w']) (_se[D_x_Heat_`w']) ///
        (2*ttail(e(df_r), abs(_b[D_x_Heat_`w']/_se[D_x_Heat_`w']))) ///
        (_b[SR_x_D_x_Heat_`w']) (_se[SR_x_D_x_Heat_`w']) ///
        (2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat_`w']/_se[SR_x_D_x_Heat_`w']))) ///
        (e(r2)) (e(N))
}

postclose `pf'

* =============================================================================
* EXPORT
* =============================================================================
preserve
use "$outdir/v3_step5_robustness.dta", clear
format b_* se_* %9.4f
format p_* %7.4f
format r2 %6.4f
list, sep(0) noobs
export delimited using "$outdir/v3_step5_robustness.csv", replace
restore

log close
di "=== v3_step5_robustness.do COMPLETE ==="
