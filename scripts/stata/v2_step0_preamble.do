* =============================================================================
* v2_step0_preamble.do
* Purpose: Load v2 data, construct D/W variables, interaction terms,
*          SM interactions, define control macros, lock sample, save .dta
* Author:  YangSu + Claude
* Date:    2026-04-02
* Input:   data_build/data/processed/data_v2_main.dta (69,038 rows, 523 cols)
* Output:  data/processed/v2_analysis_ready.dta
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

log using "$logdir/v2_step0_preamble_20260402.log", replace

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

* =============================================================================
* 2. CONSTRUCT D/W VARIABLES
*    Full season: v1 style (SPEI-6)
*    Sub-season windows: v2 style (window-specific SPEI-1 or SPEI-2)
* =============================================================================

* Full season: SPEI-6 (v1 construction)
gen D_full = max(0, -spei6_mean)
gen W_full = max(0,  spei6_mean)
label var D_full "Drought index (full season, SPEI-6)"
label var W_full "Wetness index (full season, SPEI-6)"

* V3 +/- 10 days: SPEI-1 (v2 window-specific)
gen D_v3pm10 = max(0, -spei1_mean_v3pm10)
gen W_v3pm10 = max(0,  spei1_mean_v3pm10)
label var D_v3pm10 "Drought index (V3 +/-10d, SPEI-1)"
label var W_v3pm10 "Wetness index (V3 +/-10d, SPEI-1)"

* HE +/- 10 days: SPEI-1 (v2 window-specific)
gen D_hepm10 = max(0, -spei1_mean_hepm10)
gen W_hepm10 = max(0,  spei1_mean_hepm10)
label var D_hepm10 "Drought index (HE +/-10d, SPEI-1)"
label var W_hepm10 "Wetness index (HE +/-10d, SPEI-1)"

* V3 -> HE (vegetative): SPEI-2 (v2 window-specific)
gen D_v3he = max(0, -spei2_mean_v3he)
gen W_v3he = max(0,  spei2_mean_v3he)
label var D_v3he "Drought index (V3-HE vegetative, SPEI-2)"
label var W_v3he "Wetness index (V3-HE vegetative, SPEI-2)"

* HE -> MA (reproductive/grain-fill): SPEI-2 (v2 window-specific)
gen D_hema = max(0, -spei2_mean_hema)
gen W_hema = max(0,  spei2_mean_hema)
label var D_hema "Drought index (HE-MA grain-fill, SPEI-2)"
label var W_hema "Wetness index (HE-MA grain-fill, SPEI-2)"

* Verify
sum D_full D_v3pm10 D_hepm10 D_v3he D_hema
sum W_full W_v3pm10 W_hepm10 W_v3he W_hema

* =============================================================================
* 3. CONSTRUCT SR x CLIMATE INTERACTION TERMS (5 windows x 5 = 25 vars)
* =============================================================================

* --- Full season ---
gen SR_x_D_full         = ca * D_full
gen SR_x_W_full         = ca * W_full
gen SR_x_Heat_full      = ca * hdd_ge32
gen D_x_Heat_full       = D_full * hdd_ge32
gen SR_x_D_x_Heat_full  = ca * D_full * hdd_ge32

label var SR_x_D_full        "SR x Drought (full)"
label var SR_x_W_full        "SR x Wetness (full)"
label var SR_x_Heat_full     "SR x Heat (full)"
label var D_x_Heat_full      "Drought x Heat (full)"
label var SR_x_D_x_Heat_full "SR x D x Heat (full)"

* --- V3 +/- 10 ---
gen SR_x_D_v3pm10         = ca * D_v3pm10
gen SR_x_W_v3pm10         = ca * W_v3pm10
gen SR_x_Heat_v3pm10      = ca * hdd_ge32_v3pm10
gen D_x_Heat_v3pm10       = D_v3pm10 * hdd_ge32_v3pm10
gen SR_x_D_x_Heat_v3pm10  = ca * D_v3pm10 * hdd_ge32_v3pm10

label var SR_x_D_v3pm10        "SR x Drought (V3pm10)"
label var SR_x_W_v3pm10        "SR x Wetness (V3pm10)"
label var SR_x_Heat_v3pm10     "SR x Heat (V3pm10)"
label var D_x_Heat_v3pm10      "Drought x Heat (V3pm10)"
label var SR_x_D_x_Heat_v3pm10 "SR x D x Heat (V3pm10)"

* --- HE +/- 10 ---
gen SR_x_D_hepm10         = ca * D_hepm10
gen SR_x_W_hepm10         = ca * W_hepm10
gen SR_x_Heat_hepm10      = ca * hdd_ge32_hepm10
gen D_x_Heat_hepm10       = D_hepm10 * hdd_ge32_hepm10
gen SR_x_D_x_Heat_hepm10  = ca * D_hepm10 * hdd_ge32_hepm10

label var SR_x_D_hepm10        "SR x Drought (HEpm10)"
label var SR_x_W_hepm10        "SR x Wetness (HEpm10)"
label var SR_x_Heat_hepm10     "SR x Heat (HEpm10)"
label var D_x_Heat_hepm10      "Drought x Heat (HEpm10)"
label var SR_x_D_x_Heat_hepm10 "SR x D x Heat (HEpm10)"

* --- V3 -> HE ---
gen SR_x_D_v3he         = ca * D_v3he
gen SR_x_W_v3he         = ca * W_v3he
gen SR_x_Heat_v3he      = ca * hdd_ge32_v3he
gen D_x_Heat_v3he       = D_v3he * hdd_ge32_v3he
gen SR_x_D_x_Heat_v3he  = ca * D_v3he * hdd_ge32_v3he

label var SR_x_D_v3he        "SR x Drought (V3-HE)"
label var SR_x_W_v3he        "SR x Wetness (V3-HE)"
label var SR_x_Heat_v3he     "SR x Heat (V3-HE)"
label var D_x_Heat_v3he      "Drought x Heat (V3-HE)"
label var SR_x_D_x_Heat_v3he "SR x D x Heat (V3-HE)"

* --- HE -> MA ---
gen SR_x_D_hema         = ca * D_hema
gen SR_x_W_hema         = ca * W_hema
gen SR_x_Heat_hema      = ca * hdd_ge32_hema
gen D_x_Heat_hema       = D_hema * hdd_ge32_hema
gen SR_x_D_x_Heat_hema  = ca * D_hema * hdd_ge32_hema

label var SR_x_D_hema        "SR x Drought (HE-MA)"
label var SR_x_W_hema        "SR x Wetness (HE-MA)"
label var SR_x_Heat_hema     "SR x Heat (HE-MA)"
label var D_x_Heat_hema      "Drought x Heat (HE-MA)"
label var SR_x_D_x_Heat_hema "SR x D x Heat (HE-MA)"

* =============================================================================
* 4. CONSTRUCT SM INTERACTION TERMS (3 sources x 5 windows x 6 types)
*    Spec(3): SM_x_D, SM_x_H, SM_x_SR
*    Spec(4): SM_x_D_x_H, SM_x_SR_x_D_x_H
* =============================================================================

* We use a loop structure with locals for SM variable names
* SM sources (rootzone): gleam_smrz, swsm_l3, era5l_swvl3
* Window suffixes: "" "_v3pm10" "_hepm10" "_v3he" "_hema"

foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
    foreach wsfx in "" "_v3pm10" "_hepm10" "_v3he" "_hema" {

        * Determine window label for variable names
        local wlbl = cond("`wsfx'" == "", "_full", "`wsfx'")

        * SM variable name in the dataset
        local sm_var "`src'_mean`wsfx'"

        * D and H variable names for this window
        local d_var  "D`wlbl'"
        local h_var  = cond("`wsfx'" == "", "hdd_ge32", "hdd_ge32`wsfx'")

        * Short source label for generated var names
        local slbl = cond("`src'" == "gleam_smrz", "gsm", ///
                     cond("`src'" == "swsm_l3", "ssm", "esm"))

        * --- Spec(3) interactions ---
        * SM x D
        cap drop `slbl'_x_D`wlbl'
        gen `slbl'_x_D`wlbl' = `sm_var' * `d_var'
        label var `slbl'_x_D`wlbl' "`src' x Drought (`wlbl')"

        * SM x H
        cap drop `slbl'_x_H`wlbl'
        gen `slbl'_x_H`wlbl' = `sm_var' * `h_var'
        label var `slbl'_x_H`wlbl' "`src' x Heat (`wlbl')"

        * SM x SR
        cap drop `slbl'_x_SR`wlbl'
        gen `slbl'_x_SR`wlbl' = `sm_var' * ca
        label var `slbl'_x_SR`wlbl' "`src' x SR (`wlbl')"

        * --- Spec(4) interactions ---
        * SM x D x H
        cap drop `slbl'_x_DH`wlbl'
        gen `slbl'_x_DH`wlbl' = `sm_var' * `d_var' * `h_var'
        label var `slbl'_x_DH`wlbl' "`src' x D x H (`wlbl')"

        * SM x SR x D x H
        cap drop `slbl'_x_SRDH`wlbl'
        gen `slbl'_x_SRDH`wlbl' = `sm_var' * ca * `d_var' * `h_var'
        label var `slbl'_x_SRDH`wlbl' "`src' x SR x D x H (`wlbl')"
    }
}

* Verify a few key SM interactions
sum gsm_x_D_full gsm_x_H_full gsm_x_SR_full gsm_x_DH_full gsm_x_SRDH_full
sum ssm_x_D_full esm_x_D_full
sum gsm_x_D_v3he gsm_x_D_hema

* =============================================================================
* 5. DEFINE CONTROL VARIABLE MACROS
* =============================================================================

* Full season controls
global CTRL_full    irr_frac pr_sum et0_sum aridity gdd_ge10

* V3 +/- 10
global CTRL_v3pm10  irr_frac pr_sum_v3pm10 et0_sum_v3pm10 aridity gdd_ge10_v3pm10

* HE +/- 10
global CTRL_hepm10  irr_frac pr_sum_hepm10 et0_sum_hepm10 aridity gdd_ge10_hepm10

* V3 -> HE
global CTRL_v3he    irr_frac pr_sum_v3he et0_sum_v3he aridity gdd_ge10_v3he

* HE -> MA
global CTRL_hema    irr_frac pr_sum_hema et0_sum_hema aridity gdd_ge10_hema

* =============================================================================
* 6. DEFINE RHS MACROS FOR 4 SPECS (full-season version)
*    These will be used as templates; window-specific versions built in loops
* =============================================================================

* Spec(1): Basic direct buffering
global RHS_spec1_full  D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full

* Spec(2): Compound direct buffering
global RHS_spec2_full  D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    D_x_Heat_full SR_x_D_x_Heat_full

* Spec(3): SM channel (template for GLEAM; SWSM/ERA5 substitute SM vars)
global RHS_spec3_full_gleam  D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    gleam_smrz_mean gsm_x_D_full gsm_x_H_full gsm_x_SR_full

global RHS_spec3_full_swsm   D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    swsm_l3_mean ssm_x_D_full ssm_x_H_full ssm_x_SR_full

global RHS_spec3_full_era5l  D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    era5l_swvl3_mean esm_x_D_full esm_x_H_full esm_x_SR_full

* Spec(4): Full model (compound + SM full suite)
global RHS_spec4_full_gleam  D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    D_x_Heat_full SR_x_D_x_Heat_full ///
    gleam_smrz_mean gsm_x_D_full gsm_x_H_full gsm_x_SR_full ///
    gsm_x_DH_full gsm_x_SRDH_full

global RHS_spec4_full_swsm   D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    D_x_Heat_full SR_x_D_x_Heat_full ///
    swsm_l3_mean ssm_x_D_full ssm_x_H_full ssm_x_SR_full ///
    ssm_x_DH_full ssm_x_SRDH_full

global RHS_spec4_full_era5l  D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    D_x_Heat_full SR_x_D_x_Heat_full ///
    era5l_swvl3_mean esm_x_D_full esm_x_H_full esm_x_SR_full ///
    esm_x_DH_full esm_x_SRDH_full

* =============================================================================
* 7. SM QUARTILES (for state-dependence analysis)
* =============================================================================
foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
    foreach wsfx in "" "_v3pm10" "_hepm10" "_v3he" "_hema" {
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
* 8. LOCK SAMPLE (run baseline, save e(sample))
* =============================================================================
* Run Spec(1) full-season to define the estimation sample
reghdfe ln_yield $RHS_spec1_full $CTRL_full, ///
    absorb(grid_id year) vce(cluster grid_id)

gen main_sample = e(sample)
label var main_sample "Main estimation sample (from Spec1 full-season)"
tab main_sample
di "Effective N = " e(N)

* =============================================================================
* 9. SUMMARY STATISTICS
* =============================================================================
sum ln_yield ca D_full W_full hdd_ge32 if main_sample == 1
sum gleam_smrz_mean swsm_l3_mean era5l_swvl3_mean if main_sample == 1
sum D_v3pm10 D_hepm10 D_v3he D_hema if main_sample == 1
sum hdd_ge32_v3pm10 hdd_ge32_hepm10 hdd_ge32_v3he hdd_ge32_hema if main_sample == 1

* Within-variation comparison: full vs sub-season SM
di "=== Within-variation of SM (full vs sub-season) ==="
foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
    foreach wsfx in "" "_v3pm10" "_hepm10" "_v3he" "_hema" {
        local sm_var "`src'_mean`wsfx'"
        qui xtreg `sm_var' if main_sample == 1, fe
        local wvar = e(sigma_e)
        local bvar = e(sigma_u)
        local wlbl = cond("`wsfx'" == "", "full", substr("`wsfx'", 2, .))
        di "`src' `wlbl': within=" %6.4f `wvar' " between=" %6.4f `bvar' ///
           " ratio=" %6.4f `wvar'/`bvar'
    }
}

* =============================================================================
* 10. SAVE
* =============================================================================
compress
save "$outdata/v2_analysis_ready.dta", replace
di "Saved: $outdata/v2_analysis_ready.dta"
desc, short

log close
di "=== v2_step0_preamble.do COMPLETE ==="
