* =============================================================================
* v2_step1_baseline_fullseason.do
* Purpose: Full-season 4 specs x 3 SM sources — v1->v2 bridge
* Author:  YangSu + Claude
* Date:    2026-04-02
* Input:   data/processed/v2_analysis_ready.dta
* Output:  output/tables/v2_step1_baseline.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global outdata  "$projdir/data/processed"
global outdir   "$projdir/output/tables"
global logdir   "$projdir/output/logs"

log using "$logdir/v2_step1_baseline_20260402.log", replace

use "$outdata/v2_analysis_ready.dta", clear
xtset grid_id year

* =============================================================================
* CONTROLS (full season)
* =============================================================================
global CTRL  irr_frac pr_sum et0_sum aridity gdd_ge10

* =============================================================================
* MODEL 1: Spec(1) — Basic direct buffering
*   ln_yield = D + H + SR + SR·D + SR·H + Controls + FE
* =============================================================================
eststo clear
eststo m1: reghdfe ln_yield ///
    D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    $CTRL if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

* =============================================================================
* MODEL 2: Spec(2) — Compound direct buffering
*   ln_yield = D + H + SR + SR·D + SR·H + D·H + SR·D·H + Controls + FE
* =============================================================================
eststo m2: reghdfe ln_yield ///
    D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    D_x_Heat_full SR_x_D_x_Heat_full ///
    $CTRL if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

* =============================================================================
* MODELS 3-5: Spec(3) — SM channel (3 sources)
*   ln_yield = D + H + SR + SR·D + SR·H + SM + SM·D + SM·H + SM·SR + Controls
* =============================================================================

* M3: GLEAM
eststo m3_gleam: reghdfe ln_yield ///
    D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    gleam_smrz_mean gsm_x_D_full gsm_x_H_full gsm_x_SR_full ///
    $CTRL if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

* M4: SWSM
eststo m4_swsm: reghdfe ln_yield ///
    D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    swsm_l3_mean ssm_x_D_full ssm_x_H_full ssm_x_SR_full ///
    $CTRL if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

* M5: ERA5-Land
eststo m5_era5l: reghdfe ln_yield ///
    D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    era5l_swvl3_mean esm_x_D_full esm_x_H_full esm_x_SR_full ///
    $CTRL if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

* =============================================================================
* MODELS 6-8: Spec(4) — Full model (compound + SM full suite)
*   ln_yield = ... + D·H + SR·D·H + SM + SM·D + SM·H + SM·SR + SM·D·H + SM·SR·D·H
* =============================================================================

* M6: GLEAM
eststo m6_gleam: reghdfe ln_yield ///
    D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    D_x_Heat_full SR_x_D_x_Heat_full ///
    gleam_smrz_mean gsm_x_D_full gsm_x_H_full gsm_x_SR_full ///
    gsm_x_DH_full gsm_x_SRDH_full ///
    $CTRL if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

* M7: SWSM
eststo m7_swsm: reghdfe ln_yield ///
    D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    D_x_Heat_full SR_x_D_x_Heat_full ///
    swsm_l3_mean ssm_x_D_full ssm_x_H_full ssm_x_SR_full ///
    ssm_x_DH_full ssm_x_SRDH_full ///
    $CTRL if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

* M8: ERA5-Land
eststo m8_era5l: reghdfe ln_yield ///
    D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    D_x_Heat_full SR_x_D_x_Heat_full ///
    era5l_swvl3_mean esm_x_D_full esm_x_H_full esm_x_SR_full ///
    esm_x_DH_full esm_x_SRDH_full ///
    $CTRL if main_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

* =============================================================================
* MODEL 9: Spec(2) with prov_year FE (robustness)
* =============================================================================
eststo m9_provyr: reghdfe ln_yield ///
    D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    D_x_Heat_full SR_x_D_x_Heat_full ///
    $CTRL if main_sample == 1, ///
    absorb(grid_id prov_year) vce(cluster grid_id)

* =============================================================================
* EXPORT TABLE
* =============================================================================
esttab m1 m2 m3_gleam m4_swsm m5_era5l m6_gleam m7_swsm m8_era5l m9_provyr ///
    using "$outdir/v2_step1_baseline.csv", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "N") fmt(4 4 0)) ///
    mtitles("Spec1" "Spec2" "Spec3-GLEAM" "Spec3-SWSM" "Spec3-ERA5L" ///
            "Spec4-GLEAM" "Spec4-SWSM" "Spec4-ERA5L" "Spec2-ProvYr") ///
    title("V2 Step 1: Full-Season Baseline — 4 Specs x 3 SM Sources") ///
    note("FE: grid+year (M1-M8), grid+prov_year (M9). Cluster: grid_id.") ///
    keep(SR_x_D_full SR_x_W_full SR_x_Heat_full ///
         D_x_Heat_full SR_x_D_x_Heat_full ///
         gleam_smrz_mean gsm_x_D_full gsm_x_H_full gsm_x_SR_full ///
         gsm_x_DH_full gsm_x_SRDH_full ///
         swsm_l3_mean ssm_x_D_full ssm_x_H_full ssm_x_SR_full ///
         ssm_x_DH_full ssm_x_SRDH_full ///
         era5l_swvl3_mean esm_x_D_full esm_x_H_full esm_x_SR_full ///
         esm_x_DH_full esm_x_SRDH_full) ///
    order(SR_x_D_full SR_x_W_full SR_x_Heat_full ///
          D_x_Heat_full SR_x_D_x_Heat_full)

* =============================================================================
* ATTENUATION COMPARISON
* =============================================================================
di "========================================="
di "ATTENUATION ANALYSIS: Spec(1) -> Spec(3)"
di "========================================="

* Store Spec(1) coefficients
estimates restore m1
local b_SRD_s1   = _b[SR_x_D_full]
local b_SRH_s1   = _b[SR_x_Heat_full]

* For each SM source, compute attenuation
* Note: eststo names are m3_gleam, m4_swsm, m5_era5l
foreach sm in gleam swsm era5l {
    local mnum = cond("`sm'" == "gleam", "3", cond("`sm'" == "swsm", "4", "5"))
    estimates restore m`mnum'_`sm'
    local b_SRD_s3   = _b[SR_x_D_full]
    local b_SRH_s3   = _b[SR_x_Heat_full]
    local attn_D     = 100 * (1 - `b_SRD_s3' / `b_SRD_s1')
    local attn_H     = 100 * (1 - `b_SRH_s3' / `b_SRH_s1')
    di "`sm': SR_x_D attenuation = " %5.1f `attn_D' "% (Spec1=" ///
       %7.4f `b_SRD_s1' " -> Spec3=" %7.4f `b_SRD_s3' ")"
    di "`sm': SR_x_H attenuation = " %5.1f `attn_H' "% (Spec1=" ///
       %7.4f `b_SRH_s1' " -> Spec3=" %7.4f `b_SRH_s3' ")"
}

di "========================================="
di "ATTENUATION ANALYSIS: Spec(2) -> Spec(4)"
di "========================================="

estimates restore m2
local b_SRDH_s2 = _b[SR_x_D_x_Heat_full]
local b_SRD_s2  = _b[SR_x_D_full]
local b_SRH_s2  = _b[SR_x_Heat_full]

* Note: eststo names are m6_gleam, m7_swsm, m8_era5l
foreach sm in gleam swsm era5l {
    local mnum = cond("`sm'" == "gleam", "6", cond("`sm'" == "swsm", "7", "8"))
    estimates restore m`mnum'_`sm'
    local b_SRDH_s4 = _b[SR_x_D_x_Heat_full]
    local b_SRD_s4  = _b[SR_x_D_full]
    local b_SRH_s4  = _b[SR_x_Heat_full]
    local attn_DH  = 100 * (1 - `b_SRDH_s4' / `b_SRDH_s2')
    local attn_D   = 100 * (1 - `b_SRD_s4' / `b_SRD_s2')
    local attn_H   = 100 * (1 - `b_SRH_s4' / `b_SRH_s2')
    di "`sm': SR_x_D_x_H attenuation = " %5.1f `attn_DH' "%"
    di "`sm': SR_x_D attenuation = " %5.1f `attn_D' "%"
    di "`sm': SR_x_H attenuation = " %5.1f `attn_H' "%"
}

log close
di "=== v2_step1_baseline_fullseason.do COMPLETE ==="
