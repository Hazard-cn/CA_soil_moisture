* =============================================================================
* ggcp10_wet_mirror_run_all.do
* Purpose: GLEAM wet-state full-family baseline mirror, fullnew only.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global rundir "$projdir/temp/2026-05-19_ggcp10_mediation_extensions/wet_mirror"
global logdir "$rundir/logs"
global basedta "$projdir/temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_baseline_suite_analysis_ready.dta"
global builddir "$projdir/data_build/data/processed"
global coefcsv "$rundir/ggcp10_wet_mirror_baseline_coefficients.csv"
global V6_CTRL_FULL "hdd_ge32 pr_sum et0_sum gdd_10_30 irr_frac aridity"
global CTRL_NOHEAT "pr_sum et0_sum gdd_10_30 irr_frac aridity"
global MD_CODES "mdd mds mdv"
global MD_FAMILIES `" "mdduration_wet" "mddurshare_wet" "mdseverity_wet" "'
global BASE_CODES "dur shr mdf sdf"
global BASE_FAMILIES `" "blduration_wet" "bldurshare_wet" "blseveritymean_wet" "blseveritysum_wet" "'
global DRY_PCTS "p10 p20"
global WET_PCTS "p90 p80"
global SOURCE_CODES "gss gsr"
global SOURCE_LAYERS "gleam_surface gleam_rootzone"
global SOURCE_LABELS `" "GLEAM-Sfc" "GLEAM-Root" "'

cap mkdir "$projdir/temp/2026-05-19_ggcp10_mediation_extensions"
cap mkdir "$rundir"
cap mkdir "$logdir"

cap log close master
log using "$logdir/ggcp10_wet_mirror_run_all.log", replace text name(master)

use "$basedta", clear
xtset grid_id year

merge 1:1 grid_id year using "$builddir/data_v3_main.dta", ///
    keepusing(hotdrydays_ge32_pr_lt1) keep(master match)
assert _merge == 3
drop _merge

gen HotDryPr_full = hotdrydays_ge32_pr_lt1
gen SR_x_HotDryPr_full = ca * HotDryPr_full

tempname pf
postfile `pf' str12 hazard str20 metric_family str4 dry_pct str4 wet_pct ///
    str16 source_layer str12 sm_label str20 sample_tag str12 equation ///
    str16 term str28 regressor double(b se p) long(N) double(r2) ///
    using "$rundir/wet_coef_raw.dta", replace
global WET_POST_HANDLE "`pf'"

capture program drop wet_fit
program define wet_fit
    syntax, HAZARD(string) MEDIATOR(name) FAMILY(string) DP(string) WP(string) ///
        SLAYER(string) SMLABEL(string) TAG(string) SAMPLEVAR(name)

    local rhs_m ""
    local rhs_y ""
    local pairs ""
    if "`hazard'" == "drought" {
        local rhs_m "D_full ca SR_x_D_full W_full $V6_CTRL_FULL"
        local rhs_y "D_full ca SR_x_D_full `mediator' W_full $V6_CTRL_FULL"
        local pairs `" "Main D_full" "SR_x_Main SR_x_D_full" "M `mediator'" "'
    }
    if "`hazard'" == "heat" {
        local rhs_m "hdd_ge32 ca SR_x_Heat_full D_full W_full $CTRL_NOHEAT"
        local rhs_y "hdd_ge32 ca SR_x_Heat_full `mediator' D_full W_full $CTRL_NOHEAT"
        local pairs `" "Main hdd_ge32" "SR_x_Main SR_x_Heat_full" "M `mediator'" "'
    }
    if "`hazard'" == "hotdry" {
        local rhs_m "HotDryPr_full ca SR_x_HotDryPr_full D_full hdd_ge32 W_full $CTRL_NOHEAT"
        local rhs_y "HotDryPr_full ca SR_x_HotDryPr_full `mediator' D_full hdd_ge32 W_full $CTRL_NOHEAT"
        local pairs `" "Main HotDryPr_full" "SR_x_Main SR_x_HotDryPr_full" "M `mediator'" "'
    }

    reghdfe `mediator' `rhs_m' if `samplevar' == 1, absorb(grid_id year) vce(cluster grid_id)
    local nn_m = e(N)
    local rr_m = e(r2)
    foreach pair of local pairs {
        gettoken term reg : pair
        if "`term'" != "M" {
            local pval = 2 * ttail(e(df_r), abs(_b[`reg'] / _se[`reg']))
            post $WET_POST_HANDLE ("`hazard'") ("`family'") ("`dp'") ("`wp'") ///
                ("`slayer'") ("`smlabel'") ("`tag'") ("mediator") ("`term'") ///
                ("`reg'") (_b[`reg']) (_se[`reg']) (`pval') (`nn_m') (`rr_m')
        }
    }

    reghdfe ln_yield `rhs_y' if `samplevar' == 1, absorb(grid_id year) vce(cluster grid_id)
    local nn_y = e(N)
    local rr_y = e(r2)
    foreach pair of local pairs {
        gettoken term reg : pair
        local pval = 2 * ttail(e(df_r), abs(_b[`reg'] / _se[`reg']))
        post $WET_POST_HANDLE ("`hazard'") ("`family'") ("`dp'") ("`wp'") ///
            ("`slayer'") ("`smlabel'") ("`tag'") ("outcome") ("`term'") ///
            ("`reg'") (_b[`reg']) (_se[`reg']) (`pval') (`nn_y') (`rr_y')
    }
end

forvalues m = 1/3 {
    local mcode : word `m' of $MD_CODES
    local family : word `m' of $MD_FAMILIES
    local tag "`mcode'_fn"
    local sample_var "v6s_`tag'"
    forvalues s = 1/2 {
        local src : word `s' of $SOURCE_CODES
        local src_layer : word `s' of $SOURCE_LAYERS
        local sm_label : word `s' of $SOURCE_LABELS
        local mediator "v6w_`tag'_`src'"
        foreach haz in drought heat hotdry {
            wet_fit, hazard(`haz') mediator(`mediator') family(`family') dp(.) wp(.) ///
                slayer(`src_layer') smlabel(`sm_label') tag(`tag') samplevar(`sample_var')
        }
    }
}

forvalues m = 1/4 {
    local mcode : word `m' of $BASE_CODES
    local family : word `m' of $BASE_FAMILIES
    forvalues p = 1/2 {
        local dp : word `p' of $DRY_PCTS
        local wp : word `p' of $WET_PCTS
        local tag "`mcode'_`dp'_fn"
        local sample_var "v6s_`tag'"
        forvalues s = 1/2 {
            local src : word `s' of $SOURCE_CODES
            local src_layer : word `s' of $SOURCE_LAYERS
            local sm_label : word `s' of $SOURCE_LABELS
            local mediator "v6w_`tag'_`src'"
            foreach haz in drought heat hotdry {
                wet_fit, hazard(`haz') mediator(`mediator') family(`family') dp(`dp') wp(`wp') ///
                    slayer(`src_layer') smlabel(`sm_label') tag(`tag') samplevar(`sample_var')
            }
        }
    }
}

postclose `pf'
preserve
use "$rundir/wet_coef_raw.dta", clear
export delimited using "$coefcsv", replace
restore

di "=== ggcp10_wet_mirror_run_all.do COMPLETE ==="
log close master
