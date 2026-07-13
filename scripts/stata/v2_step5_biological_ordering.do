* =============================================================================
* v2_step5_biological_ordering.do
* Purpose: Cross-stage mechanism — early D (V3-HE) depletes SM during
*          grain-fill (HE-MA), which then reduces yield.
*          Tests biological ordering of the SR buffering mechanism.
* Author:  YangSu + Claude
* Date:    2026-04-02
* Input:   data/processed/v2_analysis_ready.dta
* Output:  output/tables/v2_step5_biological_ordering.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global outdata  "$projdir/data/processed"
global outdir   "$projdir/output/tables"
global logdir   "$projdir/output/logs"

log using "$logdir/v2_step5_biological_ordering_20260402.log", replace

use "$outdata/v2_analysis_ready.dta", clear
xtset grid_id year

* Controls
global CTRL  irr_frac pr_sum et0_sum aridity gdd_ge10

* =============================================================================
* PART A: Cross-stage a-path
*   Does early drought (V3-HE) deplete later SM (HE-MA)?
*   Does SR prevent this depletion?
*   Test for each SM source.
* =============================================================================
di "========================================================"
di "PART A: a-path — early D (v3he) -> late SM (hema)"
di "========================================================"

eststo clear

* A1: GLEAM
eststo a_gleam: reghdfe gleam_smrz_mean_hema ///
    D_v3he hdd_ge32_v3he ca SR_x_D_v3he SR_x_Heat_v3he ///
    $CTRL if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)
estimates store perm_a_gleam

* A2: SWSM
eststo a_swsm: reghdfe swsm_l3_mean_hema ///
    D_v3he hdd_ge32_v3he ca SR_x_D_v3he SR_x_Heat_v3he ///
    $CTRL if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)
estimates store perm_a_swsm

* A3: ERA5-Land
eststo a_era5l: reghdfe era5l_swvl3_mean_hema ///
    D_v3he hdd_ge32_v3he ca SR_x_D_v3he SR_x_Heat_v3he ///
    $CTRL if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)
estimates store perm_a_era5l

esttab a_gleam a_swsm a_era5l using "$outdir/v2_step5_apath.csv", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(r2 N, labels("R-squared" "N") fmt(4 0)) ///
    mtitles("GLEAM-hema" "SWSM-hema" "ERA5L-hema") ///
    title("Step 5A: a-path — Early D -> Late SM") ///
    note("DV = SM(HE-MA). FE: grid+year. Cluster: grid_id.")

* =============================================================================
* PART B: Cross-stage b-path
*   Does reproductive-phase SM predict yield?
* =============================================================================
di "========================================================"
di "PART B: b-path — late SM (hema) -> yield"
di "========================================================"

eststo clear

* B1: GLEAM
eststo b_gleam: reghdfe ln_yield ///
    D_hema hdd_ge32_hema gleam_smrz_mean_hema ///
    $CTRL if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)
estimates store perm_b_gleam

* B2: SWSM
eststo b_swsm: reghdfe ln_yield ///
    D_hema hdd_ge32_hema swsm_l3_mean_hema ///
    $CTRL if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)
estimates store perm_b_swsm

* B3: ERA5-Land
eststo b_era5l: reghdfe ln_yield ///
    D_hema hdd_ge32_hema era5l_swvl3_mean_hema ///
    $CTRL if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)
estimates store perm_b_era5l

esttab b_gleam b_swsm b_era5l using "$outdir/v2_step5_bpath.csv", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(r2 N, labels("R-squared" "N") fmt(4 0)) ///
    mtitles("GLEAM-hema" "SWSM-hema" "ERA5L-hema") ///
    title("Step 5B: b-path — Late SM -> Yield") ///
    note("DV = ln_yield. FE: grid+year. Cluster: grid_id.")

* =============================================================================
* PART C: Temporal precedence (falsification)
*   Reversed: late D (hema) -> early SM (v3he). Should NOT be significant.
* =============================================================================
di "========================================================"
di "PART C: Falsification — late D (hema) -> early SM (v3he)"
di "========================================================"

eststo clear

foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
    local slbl = cond("`src'" == "gleam_smrz", "gleam", ///
                 cond("`src'" == "swsm_l3", "swsm", "era5l"))
    eststo c_`slbl': reghdfe `src'_mean_v3he ///
        D_hema hdd_ge32_hema ca SR_x_D_hema SR_x_Heat_hema ///
        $CTRL if main_sample == 1, ///
        absorb(grid_id year) vce(cluster grid_id)
}

esttab c_gleam c_swsm c_era5l using "$outdir/v2_step5_falsification.csv", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(r2 N, labels("R-squared" "N") fmt(4 0)) ///
    mtitles("GLEAM-v3he" "SWSM-v3he" "ERA5L-v3he") ///
    title("Step 5C: Falsification — Late D -> Early SM (should be n.s.)") ///
    note("DV = SM(V3-HE). FE: grid+year. Cluster: grid_id.")

* =============================================================================
* PART D: Integrated model — attenuation test
*   Full model: early-stage extremes + late-stage SM + late-stage extremes
*   Check if SR_x_D_v3he attenuates when adding SM_hema
* =============================================================================
di "========================================================"
di "PART D: Integrated model — attenuation of SR_x_D_v3he"
di "========================================================"

eststo clear

* D1: Without late SM (baseline for attenuation)
eststo d_base: reghdfe ln_yield ///
    D_v3he D_hema hdd_ge32_v3he hdd_ge32_hema ca ///
    SR_x_D_v3he SR_x_Heat_v3he ///
    SR_x_D_hema SR_x_Heat_hema ///
    $CTRL if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

* D2-D4: With late SM from each source
foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
    local slbl = cond("`src'" == "gleam_smrz", "gleam", ///
                 cond("`src'" == "swsm_l3", "swsm", "era5l"))
    eststo d_`slbl': reghdfe ln_yield ///
        D_v3he D_hema hdd_ge32_v3he hdd_ge32_hema ca ///
        SR_x_D_v3he SR_x_Heat_v3he ///
        SR_x_D_hema SR_x_Heat_hema ///
        `src'_mean_hema ///
        $CTRL if main_sample == 1, ///
        absorb(grid_id year) vce(cluster grid_id)
}

esttab d_base d_gleam d_swsm d_era5l ///
    using "$outdir/v2_step5_integrated.csv", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(r2 N, labels("R-squared" "N") fmt(4 0)) ///
    mtitles("No SM" "+GLEAM" "+SWSM" "+ERA5L") ///
    title("Step 5D: Integrated Cross-Stage Model") ///
    note("DV = ln_yield. FE: grid+year. Cluster: grid_id.") ///
    keep(SR_x_D_v3he SR_x_Heat_v3he SR_x_D_hema SR_x_Heat_hema ///
         gleam_smrz_mean_hema swsm_l3_mean_hema era5l_swvl3_mean_hema)

* Attenuation computation
estimates restore d_base
local b_base = _b[SR_x_D_v3he]
foreach slbl in gleam swsm era5l {
    estimates restore d_`slbl'
    local b_with_sm = _b[SR_x_D_v3he]
    local attn = 100 * (1 - `b_with_sm' / `b_base')
    di "`slbl': SR_x_D_v3he attenuation = " %5.1f `attn' ///
       "% (base=" %7.4f `b_base' " -> +SM=" %7.4f `b_with_sm' ")"
}

* =============================================================================
* PART E: Scheme A pathway (v3pm10 -> hepm10)
*   Emergence SM depletion affecting heading period
* =============================================================================
di "========================================================"
di "PART E: Scheme A pathway (v3pm10 -> hepm10)"
di "========================================================"

eststo clear

* E-a-path: early D (v3pm10) -> mid SM (hepm10)
foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
    local slbl = cond("`src'" == "gleam_smrz", "gleam", ///
                 cond("`src'" == "swsm_l3", "swsm", "era5l"))
    eststo ea_`slbl': reghdfe `src'_mean_hepm10 ///
        D_v3pm10 hdd_ge32_v3pm10 ca SR_x_D_v3pm10 SR_x_Heat_v3pm10 ///
        $CTRL if main_sample == 1, ///
        absorb(grid_id year) vce(cluster grid_id)
}

esttab ea_gleam ea_swsm ea_era5l ///
    using "$outdir/v2_step5_schemeA_apath.csv", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(r2 N, labels("R-squared" "N") fmt(4 0)) ///
    mtitles("GLEAM-hepm10" "SWSM-hepm10" "ERA5L-hepm10") ///
    title("Step 5E: Scheme A a-path — V3pm10 D -> HEpm10 SM") ///
    note("DV = SM(HE+/-10). FE: grid+year. Cluster: grid_id.")

* =============================================================================
* SUMMARY: Collect key coefficients for all pathways
* =============================================================================
di "========================================================"
di "SUMMARY: Biological Ordering Evidence"
di "========================================================"

tempname pf
postfile `pf' str10 pathway str10 sm_source str20 coefficient ///
    b se p N using "$outdir/v2_step5_summary.dta", replace

* A-path: D_v3he -> SM_hema
foreach src in gleam swsm era5l {
    estimates restore perm_a_`src'
    post `pf' ("a_v3he") ("`src'") ("D_v3he") ///
        (_b[D_v3he]) (_se[D_v3he]) (2*ttail(e(df_r), abs(_b[D_v3he]/_se[D_v3he]))) (e(N))
    post `pf' ("a_v3he") ("`src'") ("SR_x_D_v3he") ///
        (_b[SR_x_D_v3he]) (_se[SR_x_D_v3he]) (2*ttail(e(df_r), abs(_b[SR_x_D_v3he]/_se[SR_x_D_v3he]))) (e(N))
}

* B-path: SM_hema -> yield
foreach src in gleam swsm era5l {
    estimates restore perm_b_`src'
    local sm_var = cond("`src'" == "gleam", "gleam_smrz_mean_hema", ///
                   cond("`src'" == "swsm", "swsm_l3_mean_hema", "era5l_swvl3_mean_hema"))
    post `pf' ("b_hema") ("`src'") ("SM_hema") ///
        (_b[`sm_var']) (_se[`sm_var']) (2*ttail(e(df_r), abs(_b[`sm_var']/_se[`sm_var']))) (e(N))
}

postclose `pf'

preserve
use "$outdir/v2_step5_summary.dta", clear
list, sep(0) noobs
export delimited using "$outdir/v2_step5_summary.csv", replace
restore

log close
di "=== v2_step5_biological_ordering.do COMPLETE ==="
