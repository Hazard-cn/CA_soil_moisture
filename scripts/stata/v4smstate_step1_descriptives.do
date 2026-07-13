* =============================================================================
* v4smstate_step1_descriptives.do
* Purpose: Export raw-SM descriptives, state descriptives, and wet-leaning summary.
* Input:   temp/2026-04-21_sm_state_audit/sm_state_analysis_ready.dta
* Output:  temp/2026-04-21_sm_state_audit/sm_raw_descriptives.csv
*          temp/2026-04-21_sm_state_audit/sm_state_descriptives.csv
*          temp/2026-04-21_sm_state_audit/sm_state_wet_leaning_summary.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v4smstate_macros_include.do"

log using "$tempdir/sm_state_step1_descriptives.log", replace

use "$state_ready_dta", clear
xtset grid_id year

local n_sm : word count $STATE_SM_BASES
local n_scheme : word count $STATE_SCHEMES

tempname pf_raw pf_state
tempfile rawdesc statedesc

postfile `pf_raw' str10 window str8 source str10 layer str12 sm_label str24 sm_var ///
    double mean sd p10 p25 p50 p75 p90 min max ///
    double corr_w corr_d share_w_positive share_d_positive ///
    long N using `rawdesc', replace

postfile `pf_state' str10 window str12 threshold_scheme str8 source str10 layer str12 sm_label ///
    str24 dry_var str24 wet_var ///
    double dry_mean dry_p25 dry_p50 dry_p75 ///
    double wet_mean wet_p25 wet_p50 wet_p75 ///
    double share_wet_gt_dry mean_wet_minus_dry ///
    byte wet_gt_dry_median mean_diff_positive ///
    long N using `statedesc', replace

forvalues i = 1/`n_sm' {
    local sm      : word `i' of $STATE_SM_BASES
    local source  : word `i' of $STATE_SOURCES
    local layer   : word `i' of $STATE_LAYERS
    local sm_lbl  : word `i' of $STATE_SM_LABELS
    local prefix  : word `i' of $STATE_PREFIXES

    foreach w of global STATE_WINDOWS {
        local sfx ""
        local sample_var "state_full_6_sample"
        local d_var "D_full"
        local w_var "W_full"
        if "`w'" != "full" {
            local sfx "_`w'"
            local sample_var "state_`w'_6_sample"
            local d_var "D_`w'"
            local w_var "W_`w'"
        }
        local raw_var "`sm'`sfx'"

        quietly summarize `raw_var' if `sample_var' == 1, detail
        local nn = r(N)
        local mean_v = r(mean)
        local sd_v = r(sd)
        local p10_v = r(p10)
        local p25_v = r(p25)
        local p50_v = r(p50)
        local p75_v = r(p75)
        local p90_v = r(p90)
        local min_v = r(min)
        local max_v = r(max)

        quietly corr `raw_var' `w_var' if `sample_var' == 1
        local corr_w = r(rho)
        quietly corr `raw_var' `d_var' if `sample_var' == 1
        local corr_d = r(rho)
        quietly count if `w_var' > 0 & `sample_var' == 1
        local share_w = r(N) / `nn'
        quietly count if `d_var' > 0 & `sample_var' == 1
        local share_d = r(N) / `nn'

        post `pf_raw' ("`w'") ("`source'") ("`layer'") ("`sm_lbl'") ("`raw_var'") ///
            (`mean_v') (`sd_v') (`p10_v') (`p25_v') (`p50_v') (`p75_v') (`p90_v') (`min_v') (`max_v') ///
            (`corr_w') (`corr_d') (`share_w') (`share_d') (`nn')

        forvalues s = 1/`n_scheme' {
            local scheme : word `s' of $STATE_SCHEMES
            local short  : word `s' of $STATE_SCHEME_SHORTS
            local dry_var "ds_`short'_`prefix'`sfx'"
            local wet_var "ws_`short'_`prefix'`sfx'"

            quietly summarize `dry_var' if `sample_var' == 1, detail
            local dry_mean = r(mean)
            local dry_p25 = r(p25)
            local dry_p50 = r(p50)
            local dry_p75 = r(p75)
            local nn_state = r(N)

            quietly summarize `wet_var' if `sample_var' == 1, detail
            local wet_mean = r(mean)
            local wet_p25 = r(p25)
            local wet_p50 = r(p50)
            local wet_p75 = r(p75)

            tempvar __diff
            gen double `__diff' = `wet_var' - `dry_var'
            quietly summarize `__diff' if `sample_var' == 1
            local mean_diff = r(mean)
            quietly count if `wet_var' > `dry_var' & `sample_var' == 1
            local share_gt = r(N) / `nn_state'
            drop `__diff'

            local med_flag = (`wet_p50' > `dry_p50')
            local mean_flag = (`mean_diff' > 0)

            post `pf_state' ("`w'") ("`scheme'") ("`source'") ("`layer'") ("`sm_lbl'") ///
                ("`dry_var'") ("`wet_var'") ///
                (`dry_mean') (`dry_p25') (`dry_p50') (`dry_p75') ///
                (`wet_mean') (`wet_p25') (`wet_p50') (`wet_p75') ///
                (`share_gt') (`mean_diff') (`med_flag') (`mean_flag') (`nn_state')
        }
    }
}

postclose `pf_raw'
postclose `pf_state'

preserve
use `rawdesc', clear
sort window source layer
export delimited using "$state_raw_csv", replace
save `rawdesc', replace
restore

preserve
use `statedesc', clear
sort threshold_scheme window source layer
export delimited using "$state_desc_csv", replace
save `statedesc', replace
restore

use `rawdesc', clear
keep window source layer corr_w
rename corr_w raw_corr_w
merge 1:m window source layer using `statedesc'
assert _merge == 3
drop _merge

gen byte criteria_flag = (wet_gt_dry_median == 1 & mean_diff_positive == 1 & raw_corr_w > 0)
bysort window threshold_scheme: egen criteria_n = total(criteria_flag)
gen byte wet_leaning_flag = (criteria_n >= 4)

preserve
keep window threshold_scheme source layer sm_label raw_corr_w criteria_flag criteria_n wet_leaning_flag
sort threshold_scheme window source layer
export delimited using "$state_wetlean_csv", replace
restore

log close
