* =============================================================================
* ggcp10_baseline_suite_step1_models.do
* Purpose: Run mediator and outcome baseline equations only for:
*          hazards = drought, heat, hotdry
*          mediators = raw_sm, sm_dry_state, sm_wet_state
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/ggcp10_baseline_suite_macros_include.do"

log using "$logdir/ggcp10_baseline_suite_step1_models.log", replace

use "$v6ready_dta", clear
xtset grid_id year

merge 1:1 grid_id year using "$builddir/data_v3_main.dta", ///
    keepusing(hotdrydays_ge32_pr_lt1 hotdrydays_ge32_pr_lt1_v3pre30 ///
              hotdrydays_ge32_pr_lt1_v3he hotdrydays_ge32_pr_lt1_hema) ///
    keep(master match)
assert _merge == 3
drop _merge

gen HotDryPr_full    = hotdrydays_ge32_pr_lt1
gen HotDryPr_v3pre30 = hotdrydays_ge32_pr_lt1_v3pre30
gen HotDryPr_v3he    = hotdrydays_ge32_pr_lt1_v3he
gen HotDryPr_hema    = hotdrydays_ge32_pr_lt1_hema

gen SR_x_HotDryPr_full    = ca * HotDryPr_full
gen SR_x_HotDryPr_v3pre30 = ca * HotDryPr_v3pre30
gen SR_x_HotDryPr_v3he    = ca * HotDryPr_v3he
gen SR_x_HotDryPr_hema    = ca * HotDryPr_hema

tempname pf
postfile `pf' str12 hazard str16 mediator_type str12 window str20 metric_family ///
    str4 dry_pct str4 wet_pct str16 source_layer str12 sm_label str20 sample_tag ///
    str12 equation str16 term str28 regressor double(b se p) long(N) double(r2) ///
    using "$outdir/ggcp10_baseline_suite_coef_raw.dta", replace
global SUITE_POST_HANDLE "`pf'"

capture program drop do_hazard_models
program define do_hazard_models
    syntax, HAZARD(string) MEDIATOR(name) MTYPE(string) WINDOW(string) FAMILY(string) ///
        DP(string) WP(string) SLAYER(string) SMLABEL(string) TAG(string) SAMPLEVAR(name) ///
        DVAR(name) WVAR(name) SRDVAR(name) HDVAR(name) SRHDVAR(name)

    local rhs_m ""
    local rhs_y ""
    local post_pairs ""
    if "`hazard'" == "drought" {
        local rhs_m "`dvar' ca `srdvar' `wvar' $V6_CTRL_FULL"
        local rhs_y "`dvar' ca `srdvar' `mediator' `wvar' $V6_CTRL_FULL"
        local post_pairs `" "Main `dvar'" "ca ca" "SR_x_Main `srdvar'" "W_ctrl `wvar'" "H_ctrl hdd_ge32" "'
    }
    if "`hazard'" == "heat" {
        local rhs_m "hdd_ge32 ca SR_x_Heat_full `dvar' `wvar' $SUITE_CTRL_NOHEAT"
        local rhs_y "hdd_ge32 ca SR_x_Heat_full `mediator' `dvar' `wvar' $SUITE_CTRL_NOHEAT"
        local post_pairs `" "Main hdd_ge32" "ca ca" "SR_x_Main SR_x_Heat_full" "D_ctrl `dvar'" "W_ctrl `wvar'" "'
    }
    if "`hazard'" == "hotdry" {
        local rhs_m "`hdvar' ca `srhdvar' `dvar' hdd_ge32 `wvar' $SUITE_CTRL_NOHEAT"
        local rhs_y "`hdvar' ca `srhdvar' `mediator' `dvar' hdd_ge32 `wvar' $SUITE_CTRL_NOHEAT"
        local post_pairs `" "Main `hdvar'" "ca ca" "SR_x_Main `srhdvar'" "D_ctrl `dvar'" "H_ctrl hdd_ge32" "W_ctrl `wvar'" "'
    }

    reghdfe `mediator' `rhs_m' if `samplevar' == 1, absorb(grid_id year) vce(cluster grid_id)
    local nn_m = e(N)
    local rr_m = e(r2)
    foreach pair of local post_pairs {
        gettoken term reg : pair
        local pval = 2 * ttail(e(df_r), abs(_b[`reg'] / _se[`reg']))
        post ${SUITE_POST_HANDLE} ("`hazard'") ("`mtype'") ("`window'") ("`family'") ///
            ("`dp'") ("`wp'") ("`slayer'") ("`smlabel'") ("`tag'") ///
            ("mediator") ("`term'") ("`reg'") (_b[`reg']) (_se[`reg']) (`pval') (`nn_m') (`rr_m')
    }

    reghdfe ln_yield `rhs_y' if `samplevar' == 1, absorb(grid_id year) vce(cluster grid_id)
    local nn_y = e(N)
    local rr_y = e(r2)
    foreach pair of local post_pairs {
        gettoken term reg : pair
        local pval = 2 * ttail(e(df_r), abs(_b[`reg'] / _se[`reg']))
        post ${SUITE_POST_HANDLE} ("`hazard'") ("`mtype'") ("`window'") ("`family'") ///
            ("`dp'") ("`wp'") ("`slayer'") ("`smlabel'") ("`tag'") ///
            ("outcome") ("`term'") ("`reg'") (_b[`reg']) (_se[`reg']) (`pval') (`nn_y') (`rr_y')
    }
    local p_m = 2 * ttail(e(df_r), abs(_b[`mediator'] / _se[`mediator']))
    post ${SUITE_POST_HANDLE} ("`hazard'") ("`mtype'") ("`window'") ("`family'") ///
        ("`dp'") ("`wp'") ("`slayer'") ("`smlabel'") ("`tag'") ///
        ("outcome") ("M") ("`mediator'") (_b[`mediator']) (_se[`mediator']) (`p_m') (`nn_y') (`rr_y')
end

* -------------------------------------------------------------------------
* Raw SM means: same hazard structure, GLEAM surface/rootzone only.
* -------------------------------------------------------------------------
forvalues w = 1/4 {
    local wlbl : word `w' of $V6_WINDOWS
    local wc : word `w' of $V6_WINDOW_CODES

    local d_var "D_v3pre30"
    local w_var "W_v3pre30"
    local srd_var "SR_x_D_v3pre30"
    local hd_var "HotDryPr_v3pre30"
    local srhd_var "SR_x_HotDryPr_v3pre30"
    local raw_sfx "_v3pre30"
    if "`wlbl'" == "v3he" {
        local d_var "D_v3he"
        local w_var "W_v3he"
        local srd_var "SR_x_D_v3he"
        local hd_var "HotDryPr_v3he"
        local srhd_var "SR_x_HotDryPr_v3he"
        local raw_sfx "_v3he"
    }
    if "`wlbl'" == "hema" {
        local d_var "D_hema"
        local w_var "W_hema"
        local srd_var "SR_x_D_hema"
        local hd_var "HotDryPr_hema"
        local srhd_var "SR_x_HotDryPr_hema"
        local raw_sfx "_hema"
    }
    if "`wlbl'" == "fullnew" {
        local d_var "D_full"
        local w_var "W_full"
        local srd_var "SR_x_D_full"
        local hd_var "HotDryPr_full"
        local srhd_var "SR_x_HotDryPr_full"
        local raw_sfx ""
    }

    forvalues s = 1/2 {
        local src : word `s' of $SUITE_RAW_CODES
        local src_layer : word `s' of $SUITE_RAW_LAYERS
        local sm_label : word `s' of $SUITE_RAW_LABELS
        local mediator "gleam_sms_mean`raw_sfx'"
        if "`src'" == "gsr" local mediator "gleam_smrz_mean`raw_sfx'"
        local tag "raw_`wc'_`src'"

        gen byte sample_`tag' = (main_sample == 1)
        foreach v in ln_yield ca `mediator' `d_var' `w_var' `srd_var' ///
            hdd_ge32 SR_x_Heat_full `hd_var' `srhd_var' ///
            pr_sum et0_sum gdd_10_30 irr_frac aridity {
            replace sample_`tag' = 0 if missing(`v') & sample_`tag' == 1
        }

        do_hazard_models, hazard(drought) mediator(`mediator') mtype(raw_sm) ///
            window(`wlbl') family(raw_mean) dp(.) wp(.) slayer(`src_layer') ///
            smlabel(`sm_label') tag(`tag') samplevar(sample_`tag') ///
            dvar(`d_var') wvar(`w_var') srdvar(`srd_var') hdvar(`hd_var') srhdvar(`srhd_var')
        do_hazard_models, hazard(heat) mediator(`mediator') mtype(raw_sm) ///
            window(`wlbl') family(raw_mean) dp(.) wp(.) slayer(`src_layer') ///
            smlabel(`sm_label') tag(`tag') samplevar(sample_`tag') ///
            dvar(`d_var') wvar(`w_var') srdvar(`srd_var') hdvar(`hd_var') srhdvar(`srhd_var')
        do_hazard_models, hazard(hotdry) mediator(`mediator') mtype(raw_sm) ///
            window(`wlbl') family(raw_mean) dp(.) wp(.) slayer(`src_layer') ///
            smlabel(`sm_label') tag(`tag') samplevar(sample_`tag') ///
            dvar(`d_var') wvar(`w_var') srdvar(`srd_var') hdvar(`hd_var') srhdvar(`srhd_var')
    }
}

* -------------------------------------------------------------------------
* Dry and wet state mediators: reuse the latest v6 GLEAM metric space.
* -------------------------------------------------------------------------
forvalues block = 1/2 {
    local mediator_type "sm_dry_state"
    if `block' == 2 local mediator_type "sm_wet_state"

    forvalues m = 1/3 {
        local mcode : word `m' of $V6_MD_METRIC_CODES
        local family : word `m' of $V6_MD_METRIC_FAMILIES
        forvalues w = 1/4 {
            local wlbl : word `w' of $V6_WINDOWS
            local wc : word `w' of $V6_WINDOW_CODES
            local tag "`mcode'_`wc'"
            local sample_var "v6s_`tag'"
            local d_var "D_v3pre30"
            local w_var "W_v3pre30"
            local srd_var "SR_x_D_v3pre30"
            local hd_var "HotDryPr_v3pre30"
            local srhd_var "SR_x_HotDryPr_v3pre30"
            if "`wlbl'" == "v3he" {
                local d_var "D_v3he"
                local w_var "W_v3he"
                local srd_var "SR_x_D_v3he"
                local hd_var "HotDryPr_v3he"
                local srhd_var "SR_x_HotDryPr_v3he"
            }
            if "`wlbl'" == "hema" {
                local d_var "D_hema"
                local w_var "W_hema"
                local srd_var "SR_x_D_hema"
                local hd_var "HotDryPr_hema"
                local srhd_var "SR_x_HotDryPr_hema"
            }
            if "`wlbl'" == "fullnew" {
                local d_var "D_full"
                local w_var "W_full"
                local srd_var "SR_x_D_full"
                local hd_var "HotDryPr_full"
                local srhd_var "SR_x_HotDryPr_full"
            }
            forvalues s = 1/2 {
                local src : word `s' of $V6_SOURCE_CODES
                local src_layer : word `s' of $V6_SOURCE_LAYERS
                local sm_label : word `s' of $V6_SOURCE_LABELS
                local mediator "v6`tag'_`src'"
                if `block' == 2 local mediator "v6w_`tag'_`src'"
                do_hazard_models, hazard(drought) mediator(`mediator') mtype(`mediator_type') ///
                    window(`wlbl') family(`family') dp(.) wp(.) slayer(`src_layer') ///
                    smlabel(`sm_label') tag(`tag') samplevar(`sample_var') ///
                    dvar(`d_var') wvar(`w_var') srdvar(`srd_var') hdvar(`hd_var') srhdvar(`srhd_var')
                do_hazard_models, hazard(heat) mediator(`mediator') mtype(`mediator_type') ///
                    window(`wlbl') family(`family') dp(.) wp(.) slayer(`src_layer') ///
                    smlabel(`sm_label') tag(`tag') samplevar(`sample_var') ///
                    dvar(`d_var') wvar(`w_var') srdvar(`srd_var') hdvar(`hd_var') srhdvar(`srhd_var')
                do_hazard_models, hazard(hotdry) mediator(`mediator') mtype(`mediator_type') ///
                    window(`wlbl') family(`family') dp(.) wp(.) slayer(`src_layer') ///
                    smlabel(`sm_label') tag(`tag') samplevar(`sample_var') ///
                    dvar(`d_var') wvar(`w_var') srdvar(`srd_var') hdvar(`hd_var') srhdvar(`srhd_var')
            }
        }
    }

    forvalues m = 1/4 {
        local mcode : word `m' of $V6_METRIC_CODES
        local family : word `m' of $V6_METRIC_FAMILIES
        forvalues p = 1/2 {
            local dp : word `p' of $V6_DRY_PCTS
            local wp : word `p' of $V6_WET_PCTS
            forvalues w = 1/4 {
                local wlbl : word `w' of $V6_WINDOWS
                local wc : word `w' of $V6_WINDOW_CODES
                local tag "`mcode'_`dp'_`wc'"
                local sample_var "v6s_`tag'"
                local d_var "D_v3pre30"
                local w_var "W_v3pre30"
                local srd_var "SR_x_D_v3pre30"
                local hd_var "HotDryPr_v3pre30"
                local srhd_var "SR_x_HotDryPr_v3pre30"
                if "`wlbl'" == "v3he" {
                    local d_var "D_v3he"
                    local w_var "W_v3he"
                    local srd_var "SR_x_D_v3he"
                    local hd_var "HotDryPr_v3he"
                    local srhd_var "SR_x_HotDryPr_v3he"
                }
                if "`wlbl'" == "hema" {
                    local d_var "D_hema"
                    local w_var "W_hema"
                    local srd_var "SR_x_D_hema"
                    local hd_var "HotDryPr_hema"
                    local srhd_var "SR_x_HotDryPr_hema"
                }
                if "`wlbl'" == "fullnew" {
                    local d_var "D_full"
                    local w_var "W_full"
                    local srd_var "SR_x_D_full"
                    local hd_var "HotDryPr_full"
                    local srhd_var "SR_x_HotDryPr_full"
                }
                forvalues s = 1/2 {
                    local src : word `s' of $V6_SOURCE_CODES
                    local src_layer : word `s' of $V6_SOURCE_LAYERS
                    local sm_label : word `s' of $V6_SOURCE_LABELS
                    local mediator "v6`tag'_`src'"
                    if `block' == 2 local mediator "v6w_`tag'_`src'"
                    do_hazard_models, hazard(drought) mediator(`mediator') mtype(`mediator_type') ///
                        window(`wlbl') family(`family') dp(`dp') wp(`wp') slayer(`src_layer') ///
                        smlabel(`sm_label') tag(`tag') samplevar(`sample_var') ///
                        dvar(`d_var') wvar(`w_var') srdvar(`srd_var') hdvar(`hd_var') srhdvar(`srhd_var')
                    do_hazard_models, hazard(heat) mediator(`mediator') mtype(`mediator_type') ///
                        window(`wlbl') family(`family') dp(`dp') wp(`wp') slayer(`src_layer') ///
                        smlabel(`sm_label') tag(`tag') samplevar(`sample_var') ///
                        dvar(`d_var') wvar(`w_var') srdvar(`srd_var') hdvar(`hd_var') srhdvar(`srhd_var')
                    do_hazard_models, hazard(hotdry) mediator(`mediator') mtype(`mediator_type') ///
                        window(`wlbl') family(`family') dp(`dp') wp(`wp') slayer(`src_layer') ///
                        smlabel(`sm_label') tag(`tag') samplevar(`sample_var') ///
                        dvar(`d_var') wvar(`w_var') srdvar(`srd_var') hdvar(`hd_var') srhdvar(`srhd_var')
                }
            }
        }
    }
}

postclose `pf'

preserve
use "$outdir/ggcp10_baseline_suite_coef_raw.dta", clear
export delimited using "$suitecoef_csv", replace
restore

cap erase "$outdir/ggcp10_baseline_suite_coef_raw.dta"

log close
di "=== ggcp10_baseline_suite_step1_models.do COMPLETE ==="
