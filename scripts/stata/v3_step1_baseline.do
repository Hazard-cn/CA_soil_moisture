* =============================================================================
* v3_step1_baseline.do
* Purpose: Full-season baseline — 4 specs x 3 SM sources + prov-year FE
* Author:  YangSu + Claude
* Date:    2026-04-04
* Input:   data/processed/v3_analysis_ready.dta
* Output:  output/tables/v3_step1_baseline.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3_macros_include.do"

log using "$logdir/v3_step1_baseline.log", replace

use "$outdata/v3_analysis_ready.dta", clear
xtset grid_id year

* =============================================================================
* POSTFILE: collect key coefficients for plotting
* =============================================================================
tempname pf
postfile `pf' str10 spec str10 sm_src ///
    b_SRD se_SRD p_SRD ///
    b_SRH se_SRH p_SRH ///
    b_DH se_DH p_DH ///
    b_SRDH se_SRDH p_SRDH ///
    b_D se_D p_D ///
    b_H se_H p_H ///
    r2 N ///
    using "$outdir/v3_step1_baseline.dta", replace

* =============================================================================
* M1: Spec(1) — Basic direct buffering
* =============================================================================
eststo clear
eststo m1: reghdfe ln_yield $RHS_spec1_full $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)

post `pf' ("spec1") ("none") ///
    (_b[SR_x_D_full]) (_se[SR_x_D_full]) ///
    (2*ttail(e(df_r), abs(_b[SR_x_D_full]/_se[SR_x_D_full]))) ///
    (_b[SR_x_Heat_full]) (_se[SR_x_Heat_full]) ///
    (2*ttail(e(df_r), abs(_b[SR_x_Heat_full]/_se[SR_x_Heat_full]))) ///
    (.) (.) (.) (.) (.) (.) ///
    (_b[D_full]) (_se[D_full]) ///
    (2*ttail(e(df_r), abs(_b[D_full]/_se[D_full]))) ///
    (_b[hdd_ge32]) (_se[hdd_ge32]) ///
    (2*ttail(e(df_r), abs(_b[hdd_ge32]/_se[hdd_ge32]))) ///
    (e(r2)) (e(N))

* =============================================================================
* M2: Spec(2) — Compound direct buffering
* =============================================================================
eststo m2: reghdfe ln_yield $RHS_spec2_full $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)

post `pf' ("spec2") ("none") ///
    (_b[SR_x_D_full]) (_se[SR_x_D_full]) ///
    (2*ttail(e(df_r), abs(_b[SR_x_D_full]/_se[SR_x_D_full]))) ///
    (_b[SR_x_Heat_full]) (_se[SR_x_Heat_full]) ///
    (2*ttail(e(df_r), abs(_b[SR_x_Heat_full]/_se[SR_x_Heat_full]))) ///
    (_b[D_x_Heat_full]) (_se[D_x_Heat_full]) ///
    (2*ttail(e(df_r), abs(_b[D_x_Heat_full]/_se[D_x_Heat_full]))) ///
    (_b[SR_x_D_x_Heat_full]) (_se[SR_x_D_x_Heat_full]) ///
    (2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat_full]/_se[SR_x_D_x_Heat_full]))) ///
    (_b[D_full]) (_se[D_full]) ///
    (2*ttail(e(df_r), abs(_b[D_full]/_se[D_full]))) ///
    (_b[hdd_ge32]) (_se[hdd_ge32]) ///
    (2*ttail(e(df_r), abs(_b[hdd_ge32]/_se[hdd_ge32]))) ///
    (e(r2)) (e(N))

* =============================================================================
* M3-M5: Spec(3) x 3 SM sources
* =============================================================================
local mi = 3
foreach slbl in gleam swsm era5l {
    eststo m`mi': reghdfe ln_yield ${RHS_spec3_full_`slbl'} $CTRL_full ///
        if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)

    post `pf' ("spec3") ("`slbl'") ///
        (_b[SR_x_D_full]) (_se[SR_x_D_full]) ///
        (2*ttail(e(df_r), abs(_b[SR_x_D_full]/_se[SR_x_D_full]))) ///
        (_b[SR_x_Heat_full]) (_se[SR_x_Heat_full]) ///
        (2*ttail(e(df_r), abs(_b[SR_x_Heat_full]/_se[SR_x_Heat_full]))) ///
        (.) (.) (.) (.) (.) (.) ///
        (_b[D_full]) (_se[D_full]) ///
        (2*ttail(e(df_r), abs(_b[D_full]/_se[D_full]))) ///
        (_b[hdd_ge32]) (_se[hdd_ge32]) ///
        (2*ttail(e(df_r), abs(_b[hdd_ge32]/_se[hdd_ge32]))) ///
        (e(r2)) (e(N))

    local mi = `mi' + 1
}

* =============================================================================
* M6-M8: Spec(4) x 3 SM sources
* =============================================================================
foreach slbl in gleam swsm era5l {
    eststo m`mi': reghdfe ln_yield ${RHS_spec4_full_`slbl'} $CTRL_full ///
        if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)

    post `pf' ("spec4") ("`slbl'") ///
        (_b[SR_x_D_full]) (_se[SR_x_D_full]) ///
        (2*ttail(e(df_r), abs(_b[SR_x_D_full]/_se[SR_x_D_full]))) ///
        (_b[SR_x_Heat_full]) (_se[SR_x_Heat_full]) ///
        (2*ttail(e(df_r), abs(_b[SR_x_Heat_full]/_se[SR_x_Heat_full]))) ///
        (_b[D_x_Heat_full]) (_se[D_x_Heat_full]) ///
        (2*ttail(e(df_r), abs(_b[D_x_Heat_full]/_se[D_x_Heat_full]))) ///
        (_b[SR_x_D_x_Heat_full]) (_se[SR_x_D_x_Heat_full]) ///
        (2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat_full]/_se[SR_x_D_x_Heat_full]))) ///
        (_b[D_full]) (_se[D_full]) ///
        (2*ttail(e(df_r), abs(_b[D_full]/_se[D_full]))) ///
        (_b[hdd_ge32]) (_se[hdd_ge32]) ///
        (2*ttail(e(df_r), abs(_b[hdd_ge32]/_se[hdd_ge32]))) ///
        (e(r2)) (e(N))

    local mi = `mi' + 1
}

* =============================================================================
* M9: Spec(2) with Province x Year FE
* =============================================================================
eststo m9: reghdfe ln_yield $RHS_spec2_full $CTRL_full ///
    if main_sample == 1, absorb(grid_id prov_year) vce(cluster grid_id)

post `pf' ("spec2_py") ("none") ///
    (_b[SR_x_D_full]) (_se[SR_x_D_full]) ///
    (2*ttail(e(df_r), abs(_b[SR_x_D_full]/_se[SR_x_D_full]))) ///
    (_b[SR_x_Heat_full]) (_se[SR_x_Heat_full]) ///
    (2*ttail(e(df_r), abs(_b[SR_x_Heat_full]/_se[SR_x_Heat_full]))) ///
    (_b[D_x_Heat_full]) (_se[D_x_Heat_full]) ///
    (2*ttail(e(df_r), abs(_b[D_x_Heat_full]/_se[D_x_Heat_full]))) ///
    (_b[SR_x_D_x_Heat_full]) (_se[SR_x_D_x_Heat_full]) ///
    (2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat_full]/_se[SR_x_D_x_Heat_full]))) ///
    (_b[D_full]) (_se[D_full]) ///
    (2*ttail(e(df_r), abs(_b[D_full]/_se[D_full]))) ///
    (_b[hdd_ge32]) (_se[hdd_ge32]) ///
    (2*ttail(e(df_r), abs(_b[hdd_ge32]/_se[hdd_ge32]))) ///
    (e(r2)) (e(N))

postclose `pf'

* =============================================================================
* EXPORT TABLE
* =============================================================================
esttab m1 m2 m3 m4 m5 m6 m7 m8 m9 ///
    using "$outdir/v3_step1_baseline_full.csv", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(r2 r2_a N, labels("R-squared" "Adj R-squared" "N") fmt(4 4 0)) ///
    mtitles("Spec1" "Spec2" "Spec3-G" "Spec3-S" "Spec3-E" ///
            "Spec4-G" "Spec4-S" "Spec4-E" "Spec2-ProvYr") ///
    title("V3 Step 1: Full-Season Baseline") ///
    nonotes addnotes("Clustered SE at grid_id level") ///
    drop($CTRL_full)

* =============================================================================
* ATTENUATION ANALYSIS
* =============================================================================
di _n "=== ATTENUATION: Spec(1) -> Spec(3) ==="
estimates restore m1
local b1_SRD = _b[SR_x_D_full]
local b1_SRH = _b[SR_x_Heat_full]

foreach slbl in gleam swsm era5l {
    local mnum = cond("`slbl'" == "gleam", 3, cond("`slbl'" == "swsm", 4, 5))
    estimates restore m`mnum'
    local b3_SRD = _b[SR_x_D_full]
    local b3_SRH = _b[SR_x_Heat_full]
    local att_SRD = 100 * (1 - `b3_SRD'/`b1_SRD')
    local att_SRH = 100 * (1 - `b3_SRH'/`b1_SRH')
    di "`slbl': SRxD attenuation = " %5.1f `att_SRD' "%, SRxH attenuation = " %5.1f `att_SRH' "%"
}

di _n "=== ATTENUATION: Spec(2) -> Spec(4) ==="
estimates restore m2
local b2_SRD = _b[SR_x_D_full]
local b2_SRH = _b[SR_x_Heat_full]
local b2_SRDH = _b[SR_x_D_x_Heat_full]

foreach slbl in gleam swsm era5l {
    local mnum = cond("`slbl'" == "gleam", 6, cond("`slbl'" == "swsm", 7, 8))
    estimates restore m`mnum'
    local b4_SRD = _b[SR_x_D_full]
    local b4_SRH = _b[SR_x_Heat_full]
    local b4_SRDH = _b[SR_x_D_x_Heat_full]
    local att_SRD = 100 * (1 - `b4_SRD'/`b2_SRD')
    local att_SRH = 100 * (1 - `b4_SRH'/`b2_SRH')
    local att_SRDH = 100 * (1 - `b4_SRDH'/`b2_SRDH')
    di "`slbl': SRxD att = " %5.1f `att_SRD' "%, SRxH att = " %5.1f `att_SRH' ///
       "%, SRxDxH att = " %5.1f `att_SRDH' "%"
}

* Export postfile as CSV
preserve
use "$outdir/v3_step1_baseline.dta", clear
format b_* se_* %9.4f
format p_* %7.4f
format r2 %6.4f
list, sep(0) noobs
export delimited using "$outdir/v3_step1_baseline.csv", replace
restore

log close
di "=== v3_step1_baseline.do COMPLETE ==="
