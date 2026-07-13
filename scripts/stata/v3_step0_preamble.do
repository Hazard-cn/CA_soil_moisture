* =============================================================================
* v3_step0_preamble.do
* Purpose: Load v2 data (corrected SPEI), construct D/W for 6 windows
*          (including V3pre30), interaction terms, SM interactions,
*          define control macros and RHS macros, lock sample, save .dta
* Author:  YangSu + Claude
* Date:    2026-04-04
* Input:   data_build/data/processed/data_v2_main.dta (69,038 rows, 621 cols)
* Output:  data/processed/v3_analysis_ready.dta
* =============================================================================

clear all
set more off
set seed 42

* --- Paths ---
global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global datadir  "$projdir/data_build/data/processed"
global outdata  "$projdir/data/processed"
global outdir   "$projdir/output/tables"
global figdir   "$projdir/output/figures"
global logdir   "$projdir/output/logs"

cap mkdir "$outdata"
cap mkdir "$outdir"
cap mkdir "$figdir"
cap mkdir "$logdir"

log using "$logdir/v3_step0_preamble.log", replace

* =============================================================================
* 1. LOAD DATA
* =============================================================================
use "$datadir/data_v2_main.dta", clear
desc, short
di "N = " _N
assert _N == 69038

* Panel setup
xtset grid_id year
di "Panel: " r(panelvar) " x " r(timevar)

* Verify V3pre30 variables exist
confirm variable spei1_mean_v3pre30 hdd_ge32_v3pre30 gleam_smrz_mean_v3pre30
confirm variable pr_sum_v3pre30 et0_sum_v3pre30 gdd_ge10_v3pre30

* =============================================================================
* 2. CONSTRUCT D/W VARIABLES (6 windows)
*    All SPEI now use v1 endpoint extraction method.
*    Window-specific scales: SPEI-6 (full), SPEI-1 (±10, pre30), SPEI-2 (stages)
* =============================================================================

* Full season: SPEI-6
gen D_full = max(0, -spei6_mean)
gen W_full = max(0,  spei6_mean)
label var D_full "Drought index (full season, SPEI-6)"
label var W_full "Wetness index (full season, SPEI-6)"

* V3 +/- 10 days: SPEI-1
gen D_v3pm10 = max(0, -spei1_mean_v3pm10)
gen W_v3pm10 = max(0,  spei1_mean_v3pm10)
label var D_v3pm10 "Drought index (V3 +/-10d, SPEI-1)"
label var W_v3pm10 "Wetness index (V3 +/-10d, SPEI-1)"

* HE +/- 10 days: SPEI-1
gen D_hepm10 = max(0, -spei1_mean_hepm10)
gen W_hepm10 = max(0,  spei1_mean_hepm10)
label var D_hepm10 "Drought index (HE +/-10d, SPEI-1)"
label var W_hepm10 "Wetness index (HE +/-10d, SPEI-1)"

* V3 -> HE (vegetative): SPEI-2
gen D_v3he = max(0, -spei2_mean_v3he)
gen W_v3he = max(0,  spei2_mean_v3he)
label var D_v3he "Drought index (V3-HE vegetative, SPEI-2)"
label var W_v3he "Wetness index (V3-HE vegetative, SPEI-2)"

* HE -> MA (grain-fill): SPEI-2
gen D_hema = max(0, -spei2_mean_hema)
gen W_hema = max(0,  spei2_mean_hema)
label var D_hema "Drought index (HE-MA grain-fill, SPEI-2)"
label var W_hema "Wetness index (HE-MA grain-fill, SPEI-2)"

* V3 pre-30 days (establishment): SPEI-1
gen D_v3pre30 = max(0, -spei1_mean_v3pre30)
gen W_v3pre30 = max(0,  spei1_mean_v3pre30)
label var D_v3pre30 "Drought index (V3-pre30, SPEI-1)"
label var W_v3pre30 "Wetness index (V3-pre30, SPEI-1)"

* Verify
sum D_full D_v3pm10 D_hepm10 D_v3he D_hema D_v3pre30
sum W_full W_v3pm10 W_hepm10 W_v3he W_hema W_v3pre30

* =============================================================================
* 3. CONSTRUCT SR x CLIMATE INTERACTION TERMS (6 windows x 5 = 30 vars)
* =============================================================================

* Macro: window suffixes and their labels
local win_list `" "" "_v3pm10" "_hepm10" "_v3he" "_hema" "_v3pre30" "'

foreach wsfx in `win_list' {
    local wlbl = cond("`wsfx'" == "", "_full", "`wsfx'")
    local h_var = cond("`wsfx'" == "", "hdd_ge32", "hdd_ge32`wsfx'")

    cap drop SR_x_D`wlbl'
    gen SR_x_D`wlbl'         = ca * D`wlbl'
    label var SR_x_D`wlbl'   "SR x Drought (`wlbl')"

    cap drop SR_x_W`wlbl'
    gen SR_x_W`wlbl'         = ca * W`wlbl'
    label var SR_x_W`wlbl'   "SR x Wetness (`wlbl')"

    cap drop SR_x_Heat`wlbl'
    gen SR_x_Heat`wlbl'      = ca * `h_var'
    label var SR_x_Heat`wlbl' "SR x Heat (`wlbl')"

    cap drop D_x_Heat`wlbl'
    gen D_x_Heat`wlbl'       = D`wlbl' * `h_var'
    label var D_x_Heat`wlbl' "Drought x Heat (`wlbl')"

    cap drop SR_x_D_x_Heat`wlbl'
    gen SR_x_D_x_Heat`wlbl'  = ca * D`wlbl' * `h_var'
    label var SR_x_D_x_Heat`wlbl' "SR x D x Heat (`wlbl')"
}

* Verify key interactions
sum SR_x_D_full SR_x_Heat_full D_x_Heat_full SR_x_D_x_Heat_full
sum SR_x_D_v3pre30 SR_x_Heat_v3pre30

* =============================================================================
* 4. CONSTRUCT SM INTERACTION TERMS (3 sources x 6 windows x 5 types = 90 vars)
*    Spec(3): SM_x_D, SM_x_H, SM_x_SR
*    Spec(4): SM_x_D_x_H, SM_x_SR_x_D_x_H
* =============================================================================

foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
    foreach wsfx in `win_list' {

        local wlbl = cond("`wsfx'" == "", "_full", "`wsfx'")
        local sm_var "`src'_mean`wsfx'"
        local d_var  "D`wlbl'"
        local h_var  = cond("`wsfx'" == "", "hdd_ge32", "hdd_ge32`wsfx'")

        local slbl = cond("`src'" == "gleam_smrz", "gsm", ///
                     cond("`src'" == "swsm_l3", "ssm", "esm"))

        * --- Spec(3) interactions ---
        cap drop `slbl'_x_D`wlbl'
        gen `slbl'_x_D`wlbl' = `sm_var' * `d_var'
        label var `slbl'_x_D`wlbl' "`src' x Drought (`wlbl')"

        cap drop `slbl'_x_H`wlbl'
        gen `slbl'_x_H`wlbl' = `sm_var' * `h_var'
        label var `slbl'_x_H`wlbl' "`src' x Heat (`wlbl')"

        cap drop `slbl'_x_SR`wlbl'
        gen `slbl'_x_SR`wlbl' = `sm_var' * ca
        label var `slbl'_x_SR`wlbl' "`src' x SR (`wlbl')"

        * --- Spec(4) interactions ---
        cap drop `slbl'_x_DH`wlbl'
        gen `slbl'_x_DH`wlbl' = `sm_var' * `d_var' * `h_var'
        label var `slbl'_x_DH`wlbl' "`src' x D x H (`wlbl')"

        cap drop `slbl'_x_SRDH`wlbl'
        gen `slbl'_x_SRDH`wlbl' = `sm_var' * ca * `d_var' * `h_var'
        label var `slbl'_x_SRDH`wlbl' "`src' x SR x D x H (`wlbl')"
    }
}

* Verify
sum gsm_x_D_full gsm_x_H_full gsm_x_SR_full gsm_x_DH_full gsm_x_SRDH_full
sum gsm_x_D_v3pre30 ssm_x_D_v3pre30 esm_x_D_v3pre30

* =============================================================================
* 5. DEFINE CONTROL VARIABLE MACROS (6 windows)
* =============================================================================

global CTRL_full    irr_frac pr_sum et0_sum aridity gdd_ge10
global CTRL_v3pm10  irr_frac pr_sum_v3pm10 et0_sum_v3pm10 aridity gdd_ge10_v3pm10
global CTRL_hepm10  irr_frac pr_sum_hepm10 et0_sum_hepm10 aridity gdd_ge10_hepm10
global CTRL_v3he    irr_frac pr_sum_v3he et0_sum_v3he aridity gdd_ge10_v3he
global CTRL_hema    irr_frac pr_sum_hema et0_sum_hema aridity gdd_ge10_hema
global CTRL_v3pre30 irr_frac pr_sum_v3pre30 et0_sum_v3pre30 aridity gdd_ge10_v3pre30

* =============================================================================
* 6. DEFINE RHS MACROS FOR 4 SPECS (per-window templates)
* =============================================================================

* --- Full season ---
global RHS_spec1_full  D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full

global RHS_spec2_full  D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    D_x_Heat_full SR_x_D_x_Heat_full

* Spec(3)/(4) per SM source — full season
foreach slbl in gleam swsm era5l {
    local sv = cond("`slbl'" == "gleam", "gleam_smrz_mean", ///
               cond("`slbl'" == "swsm", "swsm_l3_mean", "era5l_swvl3_mean"))
    local sp = cond("`slbl'" == "gleam", "gsm", ///
               cond("`slbl'" == "swsm", "ssm", "esm"))

    global RHS_spec3_full_`slbl'  D_full W_full hdd_ge32 ca ///
        SR_x_D_full SR_x_W_full SR_x_Heat_full ///
        `sv' `sp'_x_D_full `sp'_x_H_full `sp'_x_SR_full

    global RHS_spec4_full_`slbl'  D_full W_full hdd_ge32 ca ///
        SR_x_D_full SR_x_W_full SR_x_Heat_full ///
        D_x_Heat_full SR_x_D_x_Heat_full ///
        `sv' `sp'_x_D_full `sp'_x_H_full `sp'_x_SR_full ///
        `sp'_x_DH_full `sp'_x_SRDH_full
}

* --- Sub-window Spec(1)/(2) macros ---
foreach wsfx in v3pm10 hepm10 v3he hema v3pre30 {
    local h "hdd_ge32_`wsfx'"

    global RHS_spec1_`wsfx'  D_`wsfx' W_`wsfx' `h' ca ///
        SR_x_D_`wsfx' SR_x_W_`wsfx' SR_x_Heat_`wsfx'

    global RHS_spec2_`wsfx'  D_`wsfx' W_`wsfx' `h' ca ///
        SR_x_D_`wsfx' SR_x_W_`wsfx' SR_x_Heat_`wsfx' ///
        D_x_Heat_`wsfx' SR_x_D_x_Heat_`wsfx'

    * Spec(3)/(4) per SM source — sub-windows
    foreach slbl in gleam swsm era5l {
        local sv = cond("`slbl'" == "gleam", "gleam_smrz_mean_`wsfx'", ///
                   cond("`slbl'" == "swsm", "swsm_l3_mean_`wsfx'", ///
                        "era5l_swvl3_mean_`wsfx'"))
        local sp = cond("`slbl'" == "gleam", "gsm", ///
                   cond("`slbl'" == "swsm", "ssm", "esm"))

        global RHS_spec3_`wsfx'_`slbl'  D_`wsfx' W_`wsfx' `h' ca ///
            SR_x_D_`wsfx' SR_x_W_`wsfx' SR_x_Heat_`wsfx' ///
            `sv' `sp'_x_D_`wsfx' `sp'_x_H_`wsfx' `sp'_x_SR_`wsfx'

        global RHS_spec4_`wsfx'_`slbl'  D_`wsfx' W_`wsfx' `h' ca ///
            SR_x_D_`wsfx' SR_x_W_`wsfx' SR_x_Heat_`wsfx' ///
            D_x_Heat_`wsfx' SR_x_D_x_Heat_`wsfx' ///
            `sv' `sp'_x_D_`wsfx' `sp'_x_H_`wsfx' `sp'_x_SR_`wsfx' ///
            `sp'_x_DH_`wsfx' `sp'_x_SRDH_`wsfx'
    }
}

* --- Horse-Race Scheme RHS macros (Spec 2) ---
* Scheme i: V3pm10 + HEpm10
global RHS_hr_scheme_i  ///
    D_v3pm10 W_v3pm10 hdd_ge32_v3pm10 ///
    SR_x_D_v3pm10 SR_x_W_v3pm10 SR_x_Heat_v3pm10 ///
    D_x_Heat_v3pm10 SR_x_D_x_Heat_v3pm10 ///
    D_hepm10 W_hepm10 hdd_ge32_hepm10 ///
    SR_x_D_hepm10 SR_x_W_hepm10 SR_x_Heat_hepm10 ///
    D_x_Heat_hepm10 SR_x_D_x_Heat_hepm10 ///
    ca

* Scheme ii: V3HE + HEMA
global RHS_hr_scheme_ii  ///
    D_v3he W_v3he hdd_ge32_v3he ///
    SR_x_D_v3he SR_x_W_v3he SR_x_Heat_v3he ///
    D_x_Heat_v3he SR_x_D_x_Heat_v3he ///
    D_hema W_hema hdd_ge32_hema ///
    SR_x_D_hema SR_x_W_hema SR_x_Heat_hema ///
    D_x_Heat_hema SR_x_D_x_Heat_hema ///
    ca

* Scheme iii: V3pre30 + V3HE + HEMA
global RHS_hr_scheme_iii  ///
    D_v3pre30 W_v3pre30 hdd_ge32_v3pre30 ///
    SR_x_D_v3pre30 SR_x_W_v3pre30 SR_x_Heat_v3pre30 ///
    D_x_Heat_v3pre30 SR_x_D_x_Heat_v3pre30 ///
    D_v3he W_v3he hdd_ge32_v3he ///
    SR_x_D_v3he SR_x_W_v3he SR_x_Heat_v3he ///
    D_x_Heat_v3he SR_x_D_x_Heat_v3he ///
    D_hema W_hema hdd_ge32_hema ///
    SR_x_D_hema SR_x_W_hema SR_x_Heat_hema ///
    D_x_Heat_hema SR_x_D_x_Heat_hema ///
    ca

* =============================================================================
* 7. SM QUARTILES (3 sources x 6 windows)
* =============================================================================
foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
    foreach wsfx in `win_list' {
        local wlbl = cond("`wsfx'" == "", "_full", "`wsfx'")
        local slbl = cond("`src'" == "gleam_smrz", "gsm", ///
                     cond("`src'" == "swsm_l3", "ssm", "esm"))
        local sm_var "`src'_mean`wsfx'"

        cap drop `slbl'_q`wlbl'
        xtile `slbl'_q`wlbl' = `sm_var', nq(4)
        label var `slbl'_q`wlbl' "`src' quartile (`wlbl')"
    }
}

* =============================================================================
* 8. PROVINCE-YEAR FE VARIABLE
* =============================================================================
cap drop prov_year
egen prov_year = group(prov_code year)
label var prov_year "Province x Year FE"

* =============================================================================
* 9. LOCK SAMPLE (run Spec(1) full-season to define estimation sample)
* =============================================================================
reghdfe ln_yield $RHS_spec1_full $CTRL_full, ///
    absorb(grid_id year) vce(cluster grid_id)

gen main_sample = e(sample)
label var main_sample "Main estimation sample (from Spec1 full-season)"
tab main_sample
di "Effective N = " e(N)

* =============================================================================
* 10. SUMMARY STATISTICS
* =============================================================================
sum ln_yield ca D_full W_full hdd_ge32 if main_sample == 1
sum gleam_smrz_mean swsm_l3_mean era5l_swvl3_mean if main_sample == 1
sum D_v3pm10 D_hepm10 D_v3he D_hema D_v3pre30 if main_sample == 1
sum hdd_ge32_v3pm10 hdd_ge32_hepm10 hdd_ge32_v3he hdd_ge32_hema hdd_ge32_v3pre30 ///
    if main_sample == 1

* Cross-window D correlations (for multicollinearity check)
di "=== Drought correlations across windows ==="
corr D_full D_v3pre30 D_v3pm10 D_v3he D_hepm10 D_hema if main_sample == 1

* =============================================================================
* 11. SAVE
* =============================================================================
compress
save "$outdata/v3_analysis_ready.dta", replace
di "Saved: $outdata/v3_analysis_ready.dta"
desc, short

log close
di "=== v3_step0_preamble.do COMPLETE ==="
