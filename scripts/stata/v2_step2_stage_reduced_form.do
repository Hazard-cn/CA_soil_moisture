* =============================================================================
* v2_step2_stage_reduced_form.do
* Purpose: Stage-specific reduced form — identify which growth stage drives
*          SR buffering. Single-window models + horse-race specifications.
* Author:  YangSu + Claude
* Date:    2026-04-02
* Input:   data/processed/v2_analysis_ready.dta
* Output:  output/tables/v2_step2_stage_single.csv
*          output/tables/v2_step2_stage_horserace.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global outdata  "$projdir/data/processed"
global outdir   "$projdir/output/tables"
global logdir   "$projdir/output/logs"

log using "$logdir/v2_step2_stage_20260402.log", replace

use "$outdata/v2_analysis_ready.dta", clear
xtset grid_id year

* =============================================================================
* PART A: Single-window models (5 regressions, Spec(2) for each window)
*         Each window independently — which window shows strongest SR buffering?
* =============================================================================
di "========================================================"
di "PART A: Single-window Spec(2) models"
di "========================================================"

* --- Postfile for collecting coefficients ---
tempname pf
tempfile pfdata
postfile `pf' str10 window ///
    b_SRD se_SRD p_SRD ///
    b_SRH se_SRH p_SRH ///
    b_DH se_DH p_DH ///
    b_SRDH se_SRDH p_SRDH ///
    N r2 ///
    using `pfdata', replace

eststo clear

* Full season
local wsfx ""
local wlbl "_full"
local ctrl "$CTRL_full"
eststo w_full: reghdfe ln_yield ///
    D`wlbl' W`wlbl' hdd_ge32`wsfx' ca ///
    SR_x_D`wlbl' SR_x_W`wlbl' SR_x_Heat`wlbl' ///
    D_x_Heat`wlbl' SR_x_D_x_Heat`wlbl' ///
    `ctrl' if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)
post `pf' ("full") ///
    (_b[SR_x_D`wlbl']) (_se[SR_x_D`wlbl']) (2*ttail(e(df_r), abs(_b[SR_x_D`wlbl']/_se[SR_x_D`wlbl']))) ///
    (_b[SR_x_Heat`wlbl']) (_se[SR_x_Heat`wlbl']) (2*ttail(e(df_r), abs(_b[SR_x_Heat`wlbl']/_se[SR_x_Heat`wlbl']))) ///
    (_b[D_x_Heat`wlbl']) (_se[D_x_Heat`wlbl']) (2*ttail(e(df_r), abs(_b[D_x_Heat`wlbl']/_se[D_x_Heat`wlbl']))) ///
    (_b[SR_x_D_x_Heat`wlbl']) (_se[SR_x_D_x_Heat`wlbl']) (2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat`wlbl']/_se[SR_x_D_x_Heat`wlbl']))) ///
    (e(N)) (e(r2))

* V3 +/- 10
local wsfx "_v3pm10"
local wlbl "_v3pm10"
local ctrl "$CTRL_v3pm10"
eststo w_v3pm10: reghdfe ln_yield ///
    D`wlbl' W`wlbl' hdd_ge32`wsfx' ca ///
    SR_x_D`wlbl' SR_x_W`wlbl' SR_x_Heat`wlbl' ///
    D_x_Heat`wlbl' SR_x_D_x_Heat`wlbl' ///
    `ctrl' if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)
post `pf' ("v3pm10") ///
    (_b[SR_x_D`wlbl']) (_se[SR_x_D`wlbl']) (2*ttail(e(df_r), abs(_b[SR_x_D`wlbl']/_se[SR_x_D`wlbl']))) ///
    (_b[SR_x_Heat`wlbl']) (_se[SR_x_Heat`wlbl']) (2*ttail(e(df_r), abs(_b[SR_x_Heat`wlbl']/_se[SR_x_Heat`wlbl']))) ///
    (_b[D_x_Heat`wlbl']) (_se[D_x_Heat`wlbl']) (2*ttail(e(df_r), abs(_b[D_x_Heat`wlbl']/_se[D_x_Heat`wlbl']))) ///
    (_b[SR_x_D_x_Heat`wlbl']) (_se[SR_x_D_x_Heat`wlbl']) (2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat`wlbl']/_se[SR_x_D_x_Heat`wlbl']))) ///
    (e(N)) (e(r2))

* HE +/- 10
local wsfx "_hepm10"
local wlbl "_hepm10"
local ctrl "$CTRL_hepm10"
eststo w_hepm10: reghdfe ln_yield ///
    D`wlbl' W`wlbl' hdd_ge32`wsfx' ca ///
    SR_x_D`wlbl' SR_x_W`wlbl' SR_x_Heat`wlbl' ///
    D_x_Heat`wlbl' SR_x_D_x_Heat`wlbl' ///
    `ctrl' if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)
post `pf' ("hepm10") ///
    (_b[SR_x_D`wlbl']) (_se[SR_x_D`wlbl']) (2*ttail(e(df_r), abs(_b[SR_x_D`wlbl']/_se[SR_x_D`wlbl']))) ///
    (_b[SR_x_Heat`wlbl']) (_se[SR_x_Heat`wlbl']) (2*ttail(e(df_r), abs(_b[SR_x_Heat`wlbl']/_se[SR_x_Heat`wlbl']))) ///
    (_b[D_x_Heat`wlbl']) (_se[D_x_Heat`wlbl']) (2*ttail(e(df_r), abs(_b[D_x_Heat`wlbl']/_se[D_x_Heat`wlbl']))) ///
    (_b[SR_x_D_x_Heat`wlbl']) (_se[SR_x_D_x_Heat`wlbl']) (2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat`wlbl']/_se[SR_x_D_x_Heat`wlbl']))) ///
    (e(N)) (e(r2))

* V3 -> HE
local wsfx "_v3he"
local wlbl "_v3he"
local ctrl "$CTRL_v3he"
eststo w_v3he: reghdfe ln_yield ///
    D`wlbl' W`wlbl' hdd_ge32`wsfx' ca ///
    SR_x_D`wlbl' SR_x_W`wlbl' SR_x_Heat`wlbl' ///
    D_x_Heat`wlbl' SR_x_D_x_Heat`wlbl' ///
    `ctrl' if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)
post `pf' ("v3he") ///
    (_b[SR_x_D`wlbl']) (_se[SR_x_D`wlbl']) (2*ttail(e(df_r), abs(_b[SR_x_D`wlbl']/_se[SR_x_D`wlbl']))) ///
    (_b[SR_x_Heat`wlbl']) (_se[SR_x_Heat`wlbl']) (2*ttail(e(df_r), abs(_b[SR_x_Heat`wlbl']/_se[SR_x_Heat`wlbl']))) ///
    (_b[D_x_Heat`wlbl']) (_se[D_x_Heat`wlbl']) (2*ttail(e(df_r), abs(_b[D_x_Heat`wlbl']/_se[D_x_Heat`wlbl']))) ///
    (_b[SR_x_D_x_Heat`wlbl']) (_se[SR_x_D_x_Heat`wlbl']) (2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat`wlbl']/_se[SR_x_D_x_Heat`wlbl']))) ///
    (e(N)) (e(r2))

* HE -> MA
local wsfx "_hema"
local wlbl "_hema"
local ctrl "$CTRL_hema"
eststo w_hema: reghdfe ln_yield ///
    D`wlbl' W`wlbl' hdd_ge32`wsfx' ca ///
    SR_x_D`wlbl' SR_x_W`wlbl' SR_x_Heat`wlbl' ///
    D_x_Heat`wlbl' SR_x_D_x_Heat`wlbl' ///
    `ctrl' if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)
post `pf' ("hema") ///
    (_b[SR_x_D`wlbl']) (_se[SR_x_D`wlbl']) (2*ttail(e(df_r), abs(_b[SR_x_D`wlbl']/_se[SR_x_D`wlbl']))) ///
    (_b[SR_x_Heat`wlbl']) (_se[SR_x_Heat`wlbl']) (2*ttail(e(df_r), abs(_b[SR_x_Heat`wlbl']/_se[SR_x_Heat`wlbl']))) ///
    (_b[D_x_Heat`wlbl']) (_se[D_x_Heat`wlbl']) (2*ttail(e(df_r), abs(_b[D_x_Heat`wlbl']/_se[D_x_Heat`wlbl']))) ///
    (_b[SR_x_D_x_Heat`wlbl']) (_se[SR_x_D_x_Heat`wlbl']) (2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat`wlbl']/_se[SR_x_D_x_Heat`wlbl']))) ///
    (e(N)) (e(r2))

postclose `pf'

* Export single-window table
esttab w_full w_v3pm10 w_hepm10 w_v3he w_hema ///
    using "$outdir/v2_step2_stage_single.csv", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(r2 N, labels("R-squared" "N") fmt(4 0)) ///
    mtitles("Full" "V3pm10" "HEpm10" "V3-HE" "HE-MA") ///
    title("V2 Step 2A: Single-Window Spec(2) — Stage Comparison") ///
    note("FE: grid+year. Cluster: grid_id. Each column uses window-specific D, H, controls.")

* Display postfile results
preserve
use `pfdata', clear
list, sep(0) noobs
export delimited using "$outdir/v2_step2_stage_postfile.csv", replace
restore

* =============================================================================
* PART B: Scheme A Horse-Race (v3pm10 + hepm10 simultaneously)
* =============================================================================
di "========================================================"
di "PART B: Scheme A Horse-Race (v3pm10 + hepm10)"
di "========================================================"

eststo clear
eststo hr_schA: reghdfe ln_yield ///
    D_v3pm10 W_v3pm10 hdd_ge32_v3pm10 ///
    SR_x_D_v3pm10 SR_x_W_v3pm10 SR_x_Heat_v3pm10 ///
    D_x_Heat_v3pm10 SR_x_D_x_Heat_v3pm10 ///
    D_hepm10 W_hepm10 hdd_ge32_hepm10 ///
    SR_x_D_hepm10 SR_x_W_hepm10 SR_x_Heat_hepm10 ///
    D_x_Heat_hepm10 SR_x_D_x_Heat_hepm10 ///
    ca $CTRL_full if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

* =============================================================================
* PART C: Scheme B Horse-Race (v3he + hema simultaneously)
* =============================================================================
di "========================================================"
di "PART C: Scheme B Horse-Race (v3he + hema)"
di "========================================================"

eststo hr_schB: reghdfe ln_yield ///
    D_v3he W_v3he hdd_ge32_v3he ///
    SR_x_D_v3he SR_x_W_v3he SR_x_Heat_v3he ///
    D_x_Heat_v3he SR_x_D_x_Heat_v3he ///
    D_hema W_hema hdd_ge32_hema ///
    SR_x_D_hema SR_x_W_hema SR_x_Heat_hema ///
    D_x_Heat_hema SR_x_D_x_Heat_hema ///
    ca $CTRL_full if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

* =============================================================================
* PART D: Focused Horse-Race (only SR interactions, base D/W/H from full season)
*         Reduces multicollinearity by not doubling base climate variables
* =============================================================================
di "========================================================"
di "PART D: Focused Horse-Race — SR interactions only per stage"
di "========================================================"

* D1: Scheme A focused
eststo hr_focA: reghdfe ln_yield ///
    D_full W_full hdd_ge32 ca ///
    D_x_Heat_full ///
    SR_x_D_v3pm10 SR_x_Heat_v3pm10 SR_x_D_x_Heat_v3pm10 ///
    SR_x_D_hepm10 SR_x_Heat_hepm10 SR_x_D_x_Heat_hepm10 ///
    $CTRL_full if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

* D2: Scheme B focused
eststo hr_focB: reghdfe ln_yield ///
    D_full W_full hdd_ge32 ca ///
    D_x_Heat_full ///
    SR_x_D_v3he SR_x_Heat_v3he SR_x_D_x_Heat_v3he ///
    SR_x_D_hema SR_x_Heat_hema SR_x_D_x_Heat_hema ///
    $CTRL_full if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

* D3: All 4 sub-windows focused
eststo hr_focAll: reghdfe ln_yield ///
    D_full W_full hdd_ge32 ca ///
    D_x_Heat_full ///
    SR_x_D_v3pm10 SR_x_Heat_v3pm10 SR_x_D_x_Heat_v3pm10 ///
    SR_x_D_hepm10 SR_x_Heat_hepm10 SR_x_D_x_Heat_hepm10 ///
    SR_x_D_v3he SR_x_Heat_v3he SR_x_D_x_Heat_v3he ///
    SR_x_D_hema SR_x_Heat_hema SR_x_D_x_Heat_hema ///
    $CTRL_full if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

* Export horse-race tables
esttab hr_schA hr_schB hr_focA hr_focB hr_focAll ///
    using "$outdir/v2_step2_stage_horserace.csv", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(r2 N, labels("R-squared" "N") fmt(4 0)) ///
    mtitles("SchA-Full" "SchB-Full" "SchA-Focused" "SchB-Focused" "All-Focused") ///
    title("V2 Step 2B-D: Horse-Race Specifications") ///
    note("FE: grid+year. Cluster: grid_id.") ///
    keep(SR_x_D_v3pm10 SR_x_Heat_v3pm10 SR_x_D_x_Heat_v3pm10 ///
         SR_x_D_hepm10 SR_x_Heat_hepm10 SR_x_D_x_Heat_hepm10 ///
         SR_x_D_v3he SR_x_Heat_v3he SR_x_D_x_Heat_v3he ///
         SR_x_D_hema SR_x_Heat_hema SR_x_D_x_Heat_hema)

log close
di "=== v2_step2_stage_reduced_form.do COMPLETE ==="
