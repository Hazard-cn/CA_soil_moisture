* =============================================================================
* ggcp10_core_baseline_step1_models.do
* Purpose: Run full-season baseline equations for three hazards and three
*          mediator families: raw SM, DryShare, WetShare.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/ggcp10_core_baseline_macros_include.do"

log using "$logdir/ggcp10_core_baseline_step1_models.log", replace

use "$core_ready_dta", clear
xtset grid_id year

tempname pf
postfile `pf' str12 hazard str16 mediator_type str20 threshold_scheme ///
    str16 source_layer str12 sm_label str20 mediator str20 paired_control ///
    str12 equation str16 term str28 regressor double(b se p) long(N) double(r2) ///
    using "$suitedir/ggcp10_core_baseline_coef_raw.dta", replace
global CORE_POST_HANDLE "`pf'"

capture program drop run_core_model
program define run_core_model
    syntax, HAZARD(string) MTYPE(string) SCHEME(string) SLAYER(string) SMLABEL(string) ///
        MEDIATOR(name) [PAIR(name)]

    gen byte core_sample = (main_sample == 1)
    foreach v in ln_yield ca D_full W_full SR_x_D_full hdd_ge32 SR_x_Heat_full ///
        HotDryPr_full SR_x_HotDryPr_full pr_sum et0_sum gdd_10_30 irr_frac aridity ///
        `mediator' `pair' {
        replace core_sample = 0 if missing(`v') & core_sample == 1
    }

    local rhs_m ""
    local rhs_y ""
    local post_pairs ""
    if "`hazard'" == "drought" {
        local rhs_m "D_full ca SR_x_D_full W_full $CORE_CTRL_FULL"
        local rhs_y "D_full ca SR_x_D_full `mediator' `pair' W_full $CORE_CTRL_FULL"
        local post_pairs `" "Main D_full" "ca ca" "SR_x_Main SR_x_D_full" "W_ctrl W_full" "H_ctrl hdd_ge32" "'
    }
    if "`hazard'" == "heat" {
        local rhs_m "hdd_ge32 ca SR_x_Heat_full D_full W_full $CORE_CTRL_NOHEAT"
        local rhs_y "hdd_ge32 ca SR_x_Heat_full `mediator' `pair' D_full W_full $CORE_CTRL_NOHEAT"
        local post_pairs `" "Main hdd_ge32" "ca ca" "SR_x_Main SR_x_Heat_full" "D_ctrl D_full" "W_ctrl W_full" "'
    }
    if "`hazard'" == "hotdry" {
        local rhs_m "HotDryPr_full ca SR_x_HotDryPr_full D_full hdd_ge32 W_full $CORE_CTRL_NOHEAT"
        local rhs_y "HotDryPr_full ca SR_x_HotDryPr_full `mediator' `pair' D_full hdd_ge32 W_full $CORE_CTRL_NOHEAT"
        local post_pairs `" "Main HotDryPr_full" "ca ca" "SR_x_Main SR_x_HotDryPr_full" "D_ctrl D_full" "H_ctrl hdd_ge32" "W_ctrl W_full" "'
    }

    reghdfe `mediator' `rhs_m' if core_sample == 1, absorb(grid_id year) vce(cluster grid_id)
    local nn_m = e(N)
    local rr_m = e(r2)
    foreach pairinfo of local post_pairs {
        gettoken term reg : pairinfo
        local pval = 2 * ttail(e(df_r), abs(_b[`reg'] / _se[`reg']))
        post ${CORE_POST_HANDLE} ("`hazard'") ("`mtype'") ("`scheme'") ("`slayer'") ///
            ("`smlabel'") ("`mediator'") ("`pair'") ("mediator") ("`term'") ("`reg'") ///
            (_b[`reg']) (_se[`reg']) (`pval') (`nn_m') (`rr_m')
    }

    reghdfe ln_yield `rhs_y' if core_sample == 1, absorb(grid_id year) vce(cluster grid_id)
    local nn_y = e(N)
    local rr_y = e(r2)
    foreach pairinfo of local post_pairs {
        gettoken term reg : pairinfo
        local pval = 2 * ttail(e(df_r), abs(_b[`reg'] / _se[`reg']))
        post ${CORE_POST_HANDLE} ("`hazard'") ("`mtype'") ("`scheme'") ("`slayer'") ///
            ("`smlabel'") ("`mediator'") ("`pair'") ("outcome") ("`term'") ("`reg'") ///
            (_b[`reg']) (_se[`reg']) (`pval') (`nn_y') (`rr_y')
    }
    local p_m = 2 * ttail(e(df_r), abs(_b[`mediator'] / _se[`mediator']))
    post ${CORE_POST_HANDLE} ("`hazard'") ("`mtype'") ("`scheme'") ("`slayer'") ///
        ("`smlabel'") ("`mediator'") ("`pair'") ("outcome") ("M") ("`mediator'") ///
        (_b[`mediator']) (_se[`mediator']) (`p_m') (`nn_y') (`rr_y')

    drop core_sample
end

* raw SM
foreach hazard in drought heat hotdry {
    run_core_model, hazard(`hazard') mtype(raw_sm) scheme(native) ///
        slayer(gleam_surface) smlabel(GLEAM-Sfc) mediator(gleam_sms_mean)
    run_core_model, hazard(`hazard') mtype(raw_sm) scheme(native) ///
        slayer(gleam_rootzone) smlabel(GLEAM-Root) mediator(gleam_smrz_mean)
}

* dry-state and wet-state, pooled-state and maize-zone-state
foreach hazard in drought heat hotdry {
    run_core_model, hazard(`hazard') mtype(sm_dry_state) scheme(pooled_state) ///
        slayer(gleam_surface) smlabel(GLEAM-Sfc) mediator(ds_pl_gsms) pair(ws_pl_gsms)
    run_core_model, hazard(`hazard') mtype(sm_dry_state) scheme(pooled_state) ///
        slayer(gleam_rootzone) smlabel(GLEAM-Root) mediator(ds_pl_gsmrz) pair(ws_pl_gsmrz)
    run_core_model, hazard(`hazard') mtype(sm_dry_state) scheme(maize_zone_state) ///
        slayer(gleam_surface) smlabel(GLEAM-Sfc) mediator(ds_mz_gsms) pair(ws_mz_gsms)
    run_core_model, hazard(`hazard') mtype(sm_dry_state) scheme(maize_zone_state) ///
        slayer(gleam_rootzone) smlabel(GLEAM-Root) mediator(ds_mz_gsmrz) pair(ws_mz_gsmrz)

    run_core_model, hazard(`hazard') mtype(sm_wet_state) scheme(pooled_state) ///
        slayer(gleam_surface) smlabel(GLEAM-Sfc) mediator(ws_pl_gsms) pair(ds_pl_gsms)
    run_core_model, hazard(`hazard') mtype(sm_wet_state) scheme(pooled_state) ///
        slayer(gleam_rootzone) smlabel(GLEAM-Root) mediator(ws_pl_gsmrz) pair(ds_pl_gsmrz)
    run_core_model, hazard(`hazard') mtype(sm_wet_state) scheme(maize_zone_state) ///
        slayer(gleam_surface) smlabel(GLEAM-Sfc) mediator(ws_mz_gsms) pair(ds_mz_gsms)
    run_core_model, hazard(`hazard') mtype(sm_wet_state) scheme(maize_zone_state) ///
        slayer(gleam_rootzone) smlabel(GLEAM-Root) mediator(ws_mz_gsmrz) pair(ds_mz_gsmrz)
}

postclose `pf'

preserve
use "$suitedir/ggcp10_core_baseline_coef_raw.dta", clear
export delimited using "$core_coef_csv", replace
restore

cap erase "$suitedir/ggcp10_core_baseline_coef_raw.dta"

log close
di "=== ggcp10_core_baseline_step1_models.do COMPLETE ==="
