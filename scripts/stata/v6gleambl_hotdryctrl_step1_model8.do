* =============================================================================
* v6gleambl_hotdryctrl_step1_model8.do
* Purpose: Run four-window GLEAM baseline regressions with hot-dry in main slot.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
if "$V6Q_MACROS_INCLUDE" == "" {
    global V6Q_MACROS_INCLUDE "$projdir/scripts/stata/v6gleambl_hotdryctrl_macros_include.do"
}
do "$V6Q_MACROS_INCLUDE"

log using "$logdir/v6gleambl_hotdryctrl_step1_model8.log", replace

use "$v6qready_dta", clear
xtset grid_id year

tempname pf
postfile `pf' str12 module str12 window str20 metric_family str4 dry_pct ///
    str4 wet_pct str16 source_layer str12 sm_label str20 sample_tag ///
    str12 equation str12 term str24 regressor ///
    double(b se p) long(N) double(r2) ///
    using "$outdir/v6gleambl_hotdryctrl_coef_raw.dta", replace

forvalues m = 1/3 {
    local mcode : word `m' of $V6_MD_METRIC_CODES
    local family : word `m' of $V6_MD_METRIC_FAMILIES

    forvalues w = 1/4 {
        local wlbl : word `w' of $V6_WINDOWS
        local wc : word `w' of $V6_WINDOW_CODES
        local tag "`mcode'_`wc'"
        local sample_var "v6q_`tag'"

        local d_var "D_v3pre30"
        local w_var "W_v3pre30"
        local hd_var "HotDryPr_v3pre30"
        local srhd_var "SR_x_HotDryPr_v3pre30"
        if "`wlbl'" == "v3he" {
            local d_var "D_v3he"
            local w_var "W_v3he"
            local hd_var "HotDryPr_v3he"
            local srhd_var "SR_x_HotDryPr_v3he"
        }
        if "`wlbl'" == "hema" {
            local d_var "D_hema"
            local w_var "W_hema"
            local hd_var "HotDryPr_hema"
            local srhd_var "SR_x_HotDryPr_hema"
        }
        if "`wlbl'" == "fullnew" {
            local d_var "D_full"
            local w_var "W_full"
            local hd_var "HotDryPr_full"
            local srhd_var "SR_x_HotDryPr_full"
        }

        quietly count if `sample_var' == 1
        if r(N) == 0 continue

        forvalues s = 1/2 {
            local src : word `s' of $V6_SOURCE_CODES
            local src_layer : word `s' of $V6_SOURCE_LAYERS
            local sm_label : word `s' of $V6_SOURCE_LABELS
            local mediator "v6q`tag'_`src'"

            reghdfe `mediator' `hd_var' ca `srhd_var' `d_var' hdd_ge32 `w_var' ///
                $V6_CTRL_NOHEAT if `sample_var' == 1, ///
                absorb(grid_id year) vce(cluster grid_id)

            local nn_m = e(N)
            local rr_m = e(r2)
            foreach pair in ///
                "HotDry_main `hd_var'" ///
                "ca ca" ///
                "SR_x_HotDry `srhd_var'" ///
                "D_ctrl `d_var'" ///
                "H_ctrl hdd_ge32" ///
                "W_w `w_var'" ///
                "pr_sum pr_sum" ///
                "et0_sum et0_sum" ///
                "gdd_10_30 gdd_10_30" ///
                "irr_frac irr_frac" ///
                "aridity aridity" {
                gettoken term reg : pair
                local pval = 2 * ttail(e(df_r), abs(_b[`reg'] / _se[`reg']))
                post `pf' ("hotdry") ("`wlbl'") ("`family'") (".") ///
                    (".") ("`src_layer'") ("`sm_label'") ("`tag'") ///
                    ("mediator") ("`term'") ("`reg'") ///
                    (_b[`reg']) (_se[`reg']) (`pval') (`nn_m') (`rr_m')
            }

            reghdfe ln_yield `hd_var' ca `srhd_var' `mediator' `d_var' hdd_ge32 `w_var' ///
                $V6_CTRL_NOHEAT if `sample_var' == 1, ///
                absorb(grid_id year) vce(cluster grid_id)

            local nn_y = e(N)
            local rr_y = e(r2)
            foreach pair in ///
                "HotDry_main `hd_var'" ///
                "ca ca" ///
                "SR_x_HotDry `srhd_var'" ///
                "M_dry `mediator'" ///
                "D_ctrl `d_var'" ///
                "H_ctrl hdd_ge32" ///
                "W_w `w_var'" ///
                "pr_sum pr_sum" ///
                "et0_sum et0_sum" ///
                "gdd_10_30 gdd_10_30" ///
                "irr_frac irr_frac" ///
                "aridity aridity" {
                gettoken term reg : pair
                local pval = 2 * ttail(e(df_r), abs(_b[`reg'] / _se[`reg']))
                post `pf' ("hotdry") ("`wlbl'") ("`family'") (".") ///
                    (".") ("`src_layer'") ("`sm_label'") ("`tag'") ///
                    ("outcome") ("`term'") ("`reg'") ///
                    (_b[`reg']) (_se[`reg']) (`pval') (`nn_y') (`rr_y')
            }
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
            local sample_var "v6q_`tag'"

            local d_var "D_v3pre30"
            local w_var "W_v3pre30"
            local hd_var "HotDryPr_v3pre30"
            local srhd_var "SR_x_HotDryPr_v3pre30"
            if "`wlbl'" == "v3he" {
                local d_var "D_v3he"
                local w_var "W_v3he"
                local hd_var "HotDryPr_v3he"
                local srhd_var "SR_x_HotDryPr_v3he"
            }
            if "`wlbl'" == "hema" {
                local d_var "D_hema"
                local w_var "W_hema"
                local hd_var "HotDryPr_hema"
                local srhd_var "SR_x_HotDryPr_hema"
            }
            if "`wlbl'" == "fullnew" {
                local d_var "D_full"
                local w_var "W_full"
                local hd_var "HotDryPr_full"
                local srhd_var "SR_x_HotDryPr_full"
            }

            quietly count if `sample_var' == 1
            if r(N) == 0 continue

            forvalues s = 1/2 {
                local src : word `s' of $V6_SOURCE_CODES
                local src_layer : word `s' of $V6_SOURCE_LAYERS
                local sm_label : word `s' of $V6_SOURCE_LABELS
                local mediator "v6q`tag'_`src'"

                reghdfe `mediator' `hd_var' ca `srhd_var' `d_var' hdd_ge32 `w_var' ///
                    $V6_CTRL_NOHEAT if `sample_var' == 1, ///
                    absorb(grid_id year) vce(cluster grid_id)

                local nn_m = e(N)
                local rr_m = e(r2)
                foreach pair in ///
                    "HotDry_main `hd_var'" ///
                    "ca ca" ///
                    "SR_x_HotDry `srhd_var'" ///
                    "D_ctrl `d_var'" ///
                    "H_ctrl hdd_ge32" ///
                    "W_w `w_var'" ///
                    "pr_sum pr_sum" ///
                    "et0_sum et0_sum" ///
                    "gdd_10_30 gdd_10_30" ///
                    "irr_frac irr_frac" ///
                    "aridity aridity" {
                    gettoken term reg : pair
                    local pval = 2 * ttail(e(df_r), abs(_b[`reg'] / _se[`reg']))
                    post `pf' ("hotdry") ("`wlbl'") ("`family'") ("`dp'") ///
                        ("`wp'") ("`src_layer'") ("`sm_label'") ("`tag'") ///
                        ("mediator") ("`term'") ("`reg'") ///
                        (_b[`reg']) (_se[`reg']) (`pval') (`nn_m') (`rr_m')
                }

                reghdfe ln_yield `hd_var' ca `srhd_var' `mediator' `d_var' hdd_ge32 `w_var' ///
                    $V6_CTRL_NOHEAT if `sample_var' == 1, ///
                    absorb(grid_id year) vce(cluster grid_id)

                local nn_y = e(N)
                local rr_y = e(r2)
                foreach pair in ///
                    "HotDry_main `hd_var'" ///
                    "ca ca" ///
                    "SR_x_HotDry `srhd_var'" ///
                    "M_dry `mediator'" ///
                    "D_ctrl `d_var'" ///
                    "H_ctrl hdd_ge32" ///
                    "W_w `w_var'" ///
                    "pr_sum pr_sum" ///
                    "et0_sum et0_sum" ///
                    "gdd_10_30 gdd_10_30" ///
                    "irr_frac irr_frac" ///
                    "aridity aridity" {
                    gettoken term reg : pair
                    local pval = 2 * ttail(e(df_r), abs(_b[`reg'] / _se[`reg']))
                    post `pf' ("hotdry") ("`wlbl'") ("`family'") ("`dp'") ///
                        ("`wp'") ("`src_layer'") ("`sm_label'") ("`tag'") ///
                        ("outcome") ("`term'") ("`reg'") ///
                        (_b[`reg']) (_se[`reg']) (`pval') (`nn_y') (`rr_y')
                }
            }
        }
    }
}

postclose `pf'

preserve
use "$outdir/v6gleambl_hotdryctrl_coef_raw.dta", clear
export delimited using "$v6qcoef_csv", replace
restore

cap erase "$outdir/v6gleambl_hotdryctrl_coef_raw.dta"

log close
di "=== v6gleambl_hotdryctrl_step1_model8.do COMPLETE ==="
