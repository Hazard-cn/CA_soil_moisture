* =============================================================================
* ggcp10_drought_sm_screen.do
* Purpose: Screen all six SM source-layer pairs for theory-consistent drought
*          baseline signs under the aggregated GGCP10 yield branch.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global suitedir "$projdir/temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite"
global builddir "$projdir/data_build/data/processed"
global statedir "$projdir/temp/2026-04-21_sm_state_audit"
global outcsv "$suitedir/ggcp10_drought_sm_screen_coefficients.csv"
global logdir "$suitedir/logs"

log using "$logdir/ggcp10_drought_sm_screen.log", replace

use "$suitedir/v3_analysis_ready_ggcp10_harvarea_agg.dta", clear
xtset grid_id year

merge 1:1 grid_id year using "$builddir/data_v3_main.dta", ///
    keepusing(gdd_10_30) keep(master match)
assert _merge == 3
drop _merge

merge 1:1 grid_id year using "$statedir/sm_state_panel_wide.dta", ///
    keepusing(ds_pl_gsms ws_pl_gsms ds_mz_gsms ws_mz_gsms ///
              ds_pl_gsmrz ws_pl_gsmrz ds_mz_gsmrz ws_mz_gsmrz ///
              ds_pl_ssl1 ws_pl_ssl1 ds_mz_ssl1 ws_mz_ssl1 ///
              ds_pl_ssl3 ws_pl_ssl3 ds_mz_ssl3 ws_mz_ssl3 ///
              ds_pl_esl1 ws_pl_esl1 ds_mz_esl1 ws_mz_esl1 ///
              ds_pl_esl3 ws_pl_esl3 ds_mz_esl3 ws_mz_esl3) ///
    keep(master match)
assert _merge == 3
drop _merge

global SCREEN_CTRL "hdd_ge32 pr_sum et0_sum gdd_10_30 irr_frac aridity"

tempname pf
postfile `pf' str16 mediator_type str20 threshold_scheme str20 source_layer ///
    str12 sm_label str24 mediator str24 paired_control str12 equation ///
    str16 term str28 regressor double(b se p) long(N) double(r2) ///
    using "$suitedir/ggcp10_drought_sm_screen_raw.dta", replace
global SCREEN_POST_HANDLE "`pf'"

capture program drop run_screen
program define run_screen
    syntax, MTYPE(string) SCHEME(string) SLAYER(string) SMLABEL(string) MEDIATOR(name) [PAIR(name)]

    tempvar sample
    gen byte `sample' = (main_sample == 1)
    foreach v in ln_yield ca D_full SR_x_D_full W_full hdd_ge32 pr_sum et0_sum gdd_10_30 irr_frac aridity ///
        `mediator' `pair' {
        replace `sample' = 0 if missing(`v') & `sample' == 1
    }

    reghdfe `mediator' D_full ca SR_x_D_full W_full $SCREEN_CTRL if `sample' == 1, ///
        absorb(grid_id year) vce(cluster grid_id)
    local nn_m = e(N)
    local rr_m = e(r2)
    foreach pairinfo in "Main D_full" "SR_x_Main SR_x_D_full" {
        gettoken term reg : pairinfo
        local pval = 2 * ttail(e(df_r), abs(_b[`reg'] / _se[`reg']))
        post ${SCREEN_POST_HANDLE} ("`mtype'") ("`scheme'") ("`slayer'") ("`smlabel'") ///
            ("`mediator'") ("`pair'") ("mediator") ("`term'") ("`reg'") ///
            (_b[`reg']) (_se[`reg']) (`pval') (`nn_m') (`rr_m')
    }

    reghdfe ln_yield D_full ca SR_x_D_full `mediator' `pair' W_full $SCREEN_CTRL if `sample' == 1, ///
        absorb(grid_id year) vce(cluster grid_id)
    local nn_y = e(N)
    local rr_y = e(r2)
    foreach pairinfo in "Main D_full" "SR_x_Main SR_x_D_full" {
        gettoken term reg : pairinfo
        local pval = 2 * ttail(e(df_r), abs(_b[`reg'] / _se[`reg']))
        post ${SCREEN_POST_HANDLE} ("`mtype'") ("`scheme'") ("`slayer'") ("`smlabel'") ///
            ("`mediator'") ("`pair'") ("outcome") ("`term'") ("`reg'") ///
            (_b[`reg']) (_se[`reg']) (`pval') (`nn_y') (`rr_y')
    }
    local p_m = 2 * ttail(e(df_r), abs(_b[`mediator'] / _se[`mediator']))
    post ${SCREEN_POST_HANDLE} ("`mtype'") ("`scheme'") ("`slayer'") ("`smlabel'") ///
        ("`mediator'") ("`pair'") ("outcome") ("M") ("`mediator'") ///
        (_b[`mediator']) (_se[`mediator']) (`p_m') (`nn_y') (`rr_y')
end

* raw means
run_screen, mtype(raw_sm) scheme(native) slayer(gleam_surface) smlabel(GLEAM-Sfc) mediator(gleam_sms_mean)
run_screen, mtype(raw_sm) scheme(native) slayer(gleam_rootzone) smlabel(GLEAM-Root) mediator(gleam_smrz_mean)
run_screen, mtype(raw_sm) scheme(native) slayer(swsm_surface) smlabel(SWSM-L1) mediator(swsm_l1_mean)
run_screen, mtype(raw_sm) scheme(native) slayer(swsm_rootzone) smlabel(SWSM-L3) mediator(swsm_l3_mean)
run_screen, mtype(raw_sm) scheme(native) slayer(era5l_surface) smlabel(ERA5L-L1) mediator(era5l_swvl1_mean)
run_screen, mtype(raw_sm) scheme(native) slayer(era5l_rootzone) smlabel(ERA5L-L3) mediator(era5l_swvl3_mean)

* dry states
foreach scheme in pl mz {
    local scheme_name "pooled_state"
    if "`scheme'" == "mz" local scheme_name "maize_zone_state"
    run_screen, mtype(sm_dry_state) scheme(`scheme_name') slayer(gleam_surface) smlabel(GLEAM-Sfc) ///
        mediator(ds_`scheme'_gsms) pair(ws_`scheme'_gsms)
    run_screen, mtype(sm_dry_state) scheme(`scheme_name') slayer(gleam_rootzone) smlabel(GLEAM-Root) ///
        mediator(ds_`scheme'_gsmrz) pair(ws_`scheme'_gsmrz)
    run_screen, mtype(sm_dry_state) scheme(`scheme_name') slayer(swsm_surface) smlabel(SWSM-L1) ///
        mediator(ds_`scheme'_ssl1) pair(ws_`scheme'_ssl1)
    run_screen, mtype(sm_dry_state) scheme(`scheme_name') slayer(swsm_rootzone) smlabel(SWSM-L3) ///
        mediator(ds_`scheme'_ssl3) pair(ws_`scheme'_ssl3)
    run_screen, mtype(sm_dry_state) scheme(`scheme_name') slayer(era5l_surface) smlabel(ERA5L-L1) ///
        mediator(ds_`scheme'_esl1) pair(ws_`scheme'_esl1)
    run_screen, mtype(sm_dry_state) scheme(`scheme_name') slayer(era5l_rootzone) smlabel(ERA5L-L3) ///
        mediator(ds_`scheme'_esl3) pair(ws_`scheme'_esl3)
}

postclose `pf'

use "$suitedir/ggcp10_drought_sm_screen_raw.dta", clear
export delimited using "$outcsv", replace
cap erase "$suitedir/ggcp10_drought_sm_screen_raw.dta"

log close
di "=== ggcp10_drought_sm_screen.do COMPLETE ==="
