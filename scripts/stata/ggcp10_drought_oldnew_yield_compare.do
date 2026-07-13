* =============================================================================
* ggcp10_drought_oldnew_yield_compare.do
* Purpose: Compare SR x D under old vs new yield and old vs current spec.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global suitedir "$projdir/temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite"
global builddir "$projdir/data_build/data/processed"
global logdir "$suitedir/logs"
global outcsv "$suitedir/ggcp10_drought_oldnew_yield_compare.csv"
global COMP_CTRL "irr_frac pr_sum et0_sum aridity gdd_10_30"

log using "$logdir/ggcp10_drought_oldnew_yield_compare.log", replace

use "$suitedir/v3_analysis_ready_ggcp10_harvarea_agg.dta", clear
xtset grid_id year

merge 1:1 grid_id year using "$builddir/data_v3_main.dta", ///
    keepusing(gdd_10_30) keep(master match)
assert _merge == 3
drop _merge

tempname pf
postfile `pf' str12 spec str12 outcome str20 source_layer str12 sm_label ///
    str12 term double(b se p) long(N) double(r2) ///
    using "$suitedir/ggcp10_drought_oldnew_yield_compare_raw.dta", replace

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
    foreach v in orig_ln_yield ln_yield D_full ca SR_x_D_full `sm' hdd_ge32 W_full $COMP_CTRL {
        replace `sample' = 0 if missing(`v') & `sample' == 1
    }

    foreach spec in oldspec currentspec {
        local rhs "D_full ca SR_x_D_full `sm' hdd_ge32 $COMP_CTRL"
        if "`spec'" == "currentspec" local rhs "D_full ca SR_x_D_full `sm' W_full hdd_ge32 $COMP_CTRL"

        foreach y in orig_ln_yield ln_yield {
            reghdfe `y' `rhs' if `sample' == 1, absorb(grid_id year) vce(cluster grid_id)
            local nn = e(N)
            local rr = e(r2)
            foreach term in D_full SR_x_D_full `sm' {
                local pval = 2 * ttail(e(df_r), abs(_b[`term'] / _se[`term']))
                post `pf' ("`spec'") ("`y'") ("`source'") ("`lbl'") ("`term'") ///
                    (_b[`term']) (_se[`term']) (`pval') (`nn') (`rr')
            }
        }
    }
}

postclose `pf'

use "$suitedir/ggcp10_drought_oldnew_yield_compare_raw.dta", clear
export delimited using "$outcsv", replace
cap erase "$suitedir/ggcp10_drought_oldnew_yield_compare_raw.dta"

log close
di "=== ggcp10_drought_oldnew_yield_compare.do COMPLETE ==="
