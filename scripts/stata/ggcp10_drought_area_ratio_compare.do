* =============================================================================
* ggcp10_drought_area_ratio_compare.do
* Purpose: Quantify how the area-ratio term explains old/new SR x D shifts.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global suitedir "$projdir/temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite"
global builddir "$projdir/data_build/data/processed"
global logdir "$suitedir/logs"
global outcsv "$suitedir/ggcp10_drought_area_ratio_compare.csv"
global COMP_CTRL "irr_frac pr_sum et0_sum aridity gdd_10_30"

log using "$logdir/ggcp10_drought_area_ratio_compare.log", replace

use "$suitedir/v3_analysis_ready_ggcp10_harvarea_agg.dta", clear
xtset grid_id year

merge 1:1 grid_id year using "$builddir/data_v3_main.dta", ///
    keepusing(gdd_10_30) keep(master match)
assert _merge == 3
drop _merge

gen ln_area_ratio_old_to_new = ln(orig_maize_area_km2 / maize_area_km2)

tempname pf
postfile `pf' str12 spec str20 source_layer str12 sm_label ///
    double(b se p) long(N) double(r2) ///
    using "$suitedir/ggcp10_drought_area_ratio_compare_raw.dta", replace

foreach source in gleam_surface gleam_rootzone swsm_surface swsm_rootzone era5l_surface era5l_rootzone {
    local sm ""
    local lbl ""
    if "`source'" == "gleam_surface" {
        local sm "gleam_sms_mean"
        local lbl "GLEAM-Sfc"
    }
    if "`source'" == "gleam_rootzone" {
        local sm "gleam_smrz_mean"
        local lbl "GLEAM-Root"
    }
    if "`source'" == "swsm_surface" {
        local sm "swsm_l1_mean"
        local lbl "SWSM-L1"
    }
    if "`source'" == "swsm_rootzone" {
        local sm "swsm_l3_mean"
        local lbl "SWSM-L3"
    }
    if "`source'" == "era5l_surface" {
        local sm "era5l_swvl1_mean"
        local lbl "ERA5L-L1"
    }
    if "`source'" == "era5l_rootzone" {
        local sm "era5l_swvl3_mean"
        local lbl "ERA5L-L3"
    }

    tempvar sample
    gen byte `sample' = (main_sample == 1)
    foreach v in ln_area_ratio_old_to_new D_full ca SR_x_D_full `sm' hdd_ge32 W_full $COMP_CTRL {
        replace `sample' = 0 if missing(`v') & `sample' == 1
    }

    foreach spec in oldspec currentspec {
        local rhs "D_full ca SR_x_D_full `sm' hdd_ge32 $COMP_CTRL"
        if "`spec'" == "currentspec" local rhs "D_full ca SR_x_D_full `sm' W_full hdd_ge32 $COMP_CTRL"
        reghdfe ln_area_ratio_old_to_new `rhs' if `sample' == 1, ///
            absorb(grid_id year) vce(cluster grid_id)
        local pval = 2 * ttail(e(df_r), abs(_b[SR_x_D_full] / _se[SR_x_D_full]))
        post `pf' ("`spec'") ("`source'") ("`lbl'") ///
            (_b[SR_x_D_full]) (_se[SR_x_D_full]) (`pval') (e(N)) (e(r2))
    }
}

postclose `pf'
use "$suitedir/ggcp10_drought_area_ratio_compare_raw.dta", clear
export delimited using "$outcsv", replace
cap erase "$suitedir/ggcp10_drought_area_ratio_compare_raw.dta"

log close
di "=== ggcp10_drought_area_ratio_compare.do COMPLETE ==="
