* =============================================================================
* v3prhdsm_step0_preamble.do
* Purpose: Build analysis-ready panel for Soil Moisture spec3/spec4 report
* Input:   data_build/data/processed/data_v3_main.dta
* Output:  data/processed/v3prhdsm_analysis_ready.dta
* =============================================================================

clear all
set more off
set seed 42

do "C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata/v3prhdsm_macros_include.do"

log using "$logdir/v3prhdsm_step0_preamble.log", replace

use "$builddir/data_v3_main.dta", clear
xtset grid_id year

* ---------------------------------------------------------------------------
* Variable checks
* ---------------------------------------------------------------------------
confirm variable ln_yield ca grid_id year
confirm variable spei6_mean spei1_mean_v3pre30 spei1_mean_v3pm10 spei1_mean_hepm10
confirm variable spei2_mean_v3he spei2_mean_hema
confirm variable hdd_ge32 hdd_ge32_v3pre30 hdd_ge32_v3pm10 hdd_ge32_hepm10 hdd_ge32_v3he hdd_ge32_hema
confirm variable hotdrydays_ge32_pr_lt1 hotdrydays_ge32_pr_lt1_v3pre30 ///
    hotdrydays_ge32_pr_lt1_v3pm10 hotdrydays_ge32_pr_lt1_hepm10 ///
    hotdrydays_ge32_pr_lt1_v3he hotdrydays_ge32_pr_lt1_hema
confirm variable irr_frac pr_sum et0_sum gdd_10_30
confirm variable pr_sum_v3pre30 et0_sum_v3pre30 gdd_10_30_v3pre30
confirm variable pr_sum_v3pm10 et0_sum_v3pm10 gdd_10_30_v3pm10
confirm variable pr_sum_hepm10 et0_sum_hepm10 gdd_10_30_hepm10
confirm variable pr_sum_v3he et0_sum_v3he gdd_10_30_v3he
confirm variable pr_sum_hema et0_sum_hema gdd_10_30_hema

foreach dv in gleam_sms_mean gleam_smrz_mean swsm_l1_mean swsm_l3_mean ///
    era5l_swvl1_mean era5l_swvl3_mean {
    confirm variable `dv'
}

* ---------------------------------------------------------------------------
* Core regressors
* ---------------------------------------------------------------------------
cap drop D_full D_v3pre30 D_v3pm10 D_hepm10 D_v3he D_hema

gen D_full = max(0, -spei6_mean)
gen D_v3pre30 = max(0, -spei1_mean_v3pre30)
gen D_v3pm10  = max(0, -spei1_mean_v3pm10)
gen D_hepm10  = max(0, -spei1_mean_hepm10)
gen D_v3he    = max(0, -spei2_mean_v3he)
gen D_hema    = max(0, -spei2_mean_hema)

label var D_full "Drought index (full season, SPEI-6)"
label var D_v3pre30 "Drought index (V3-pre30, SPEI-1)"
label var D_v3pm10 "Drought index (V3 +/-10d, SPEI-1)"
label var D_hepm10 "Drought index (HE +/-10d, SPEI-1)"
label var D_v3he "Drought index (V3-HE, SPEI-2)"
label var D_hema "Drought index (HE-MA, SPEI-2)"

foreach w in full v3pre30 v3pm10 hepm10 v3he hema {
    local hsfx = cond("`w'" == "full", "", "_`w'")
    local hotdry = cond("`w'" == "full", "hotdrydays_ge32_pr_lt1", "hotdrydays_ge32_pr_lt1_`w'")

    cap drop SR_x_D_`w'
    cap drop SR_x_Heat_`w'
    cap drop D_x_Heat_`w'
    cap drop SR_x_D_x_Heat_`w'
    cap drop HotDryPr_`w'
    cap drop SR_x_HotDryPr_`w'

    gen SR_x_D_`w'        = ca * D_`w'
    gen SR_x_Heat_`w'     = ca * hdd_ge32`hsfx'
    gen D_x_Heat_`w'      = D_`w' * hdd_ge32`hsfx'
    gen SR_x_D_x_Heat_`w' = ca * D_`w' * hdd_ge32`hsfx'
    gen HotDryPr_`w'      = `hotdry'
    gen SR_x_HotDryPr_`w' = ca * HotDryPr_`w'
}

label var HotDryPr_full "Compound hot-dry days (precip, full season)"
label var SR_x_HotDryPr_full "SR x compound hot-dry days (precip, full season)"

* ---------------------------------------------------------------------------
* Estimation sample
* ---------------------------------------------------------------------------
reghdfe ln_yield ca D_full hdd_ge32 SR_x_D_full SR_x_Heat_full $CTRL_full, ///
    absorb(grid_id year) vce(cluster grid_id)

cap drop main_sample
gen main_sample = e(sample)
label var main_sample "Main estimation sample for v3prhdsm"

* ---------------------------------------------------------------------------
* Diagnostics
* ---------------------------------------------------------------------------
tab main_sample
sum ln_yield ca D_full hdd_ge32 HotDryPr_full if main_sample == 1
sum gleam_sms_mean gleam_smrz_mean swsm_l1_mean swsm_l3_mean ///
    era5l_swvl1_mean era5l_swvl3_mean if main_sample == 1
sum gdd_10_30 pr_sum et0_sum irr_frac if main_sample == 1

quietly compress
save "$outdata/v3prhdsm_analysis_ready.dta", replace
di "Saved: $outdata/v3prhdsm_analysis_ready.dta"

log close
di "=== v3prhdsm_step0_preamble.do COMPLETE ==="
