* =============================================================================
* v3bpath_step8_sensitivity_claim_audit.do
* Purpose: Audit claim boundaries under fixed FE/window sensitivity specs and
*          generate the cross-SM comparison summary.
* Input:   data/processed/v3bpath_analysis_ready.dta
* Output:  output/tables/v3bpath_sensitivity_claim_audit.csv
*          output/tables/v3bpath_sm_comparison_summary.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3bpath_macros_include.do"

log using "$logdir/v3bpath_step8_sensitivity_claim_audit.log", replace

use "$datadir/v3bpath_analysis_ready.dta", clear
xtset grid_id year

tempname pf
tempfile sens
postfile `pf' str8 source str10 layer str12 sm_label ///
    str24 sm_var str24 mediator_var str24 spec ///
    double a3 se_a3 p_a3 ///
    double b_sm se_b_sm p_b_sm ///
    double c3 se_c3 p_c3 ///
    double index_ab byte sign_pattern_ok ///
    str28 claim_level long effective_N byte stage6_common_flag ///
    long N_m long N_y double r2_m double r2_y using `sens', replace

local n_sm : word count $BPATH_SM_BASES

forvalues i = 1/`n_sm' {
    local sm      : word `i' of $BPATH_SM_BASES
    local source  : word `i' of $BPATH_SOURCES
    local layer   : word `i' of $BPATH_LAYERS
    local sm_lbl  : word `i' of $BPATH_SM_LABELS
    local smdef   "SMdef_`sm'"

    foreach spec in raw_full_L0 raw_full_provyear smdef_full_L0 smdef_full_provyear stage_v3pre30_L0 {
        local use_stage = 0
        local mediator_var "`sm'"
        local d_var "D_full"
        local dca_var "SR_x_D_full"
        local h_var "hdd_ge32"
        local gdd_var "gdd_10_30"
        local w_var "W_full"
        local abs_spec "grid_id year"
        local sample_flag "${BPATH_FULL_SAMPLE}"

        if strpos("`spec'", "smdef") > 0 local mediator_var "`smdef'"
        if strpos("`spec'", "provyear") > 0 local abs_spec "grid_id prov_year"
        if "`spec'" == "stage_v3pre30_L0" {
            local use_stage = 1
            local mediator_var "`sm'_v3pre30"
            local d_var "D_v3pre30"
            local dca_var "SR_x_D_v3pre30"
            local h_var "hdd_ge32_v3pre30"
            local gdd_var "gdd_10_30_v3pre30"
            local w_var "W_v3pre30"
            local abs_spec "grid_id year"
            local sample_flag "${BPATH_STAGE_SAMPLE}"
        }

        preserve
        keep if `sample_flag' == 1

        di _n "=============================================="
        di "source=`source' | layer=`layer' | spec=`spec'"
        di "=============================================="

        reghdfe `mediator_var' `d_var' ca `dca_var' `h_var' `w_var' irr_frac `gdd_var', ///
            absorb(`abs_spec') vce(cluster grid_id)

        local dfr_m = e(df_r)
        local n_m = e(N)
        local r2_m = e(r2)
        local p_a3 = 2 * ttail(`dfr_m', abs(_b[`dca_var'] / _se[`dca_var']))
        local a3 = _b[`dca_var']
        local a3_se = _se[`dca_var']

        reghdfe ln_yield `d_var' ca `dca_var' `mediator_var' `h_var' `w_var' irr_frac `gdd_var', ///
            absorb(`abs_spec') vce(cluster grid_id)

        local dfr_y = e(df_r)
        local n_y = e(N)
        local r2_y = e(r2)
        local p_b = 2 * ttail(`dfr_y', abs(_b[`mediator_var'] / _se[`mediator_var']))
        local p_c3 = 2 * ttail(`dfr_y', abs(_b[`dca_var'] / _se[`dca_var']))
        local b_sm = _b[`mediator_var']
        local b_sm_se = _se[`mediator_var']
        local c3 = _b[`dca_var']
        local c3_se = _se[`dca_var']
        local idx = `a3' * `b_sm'
        local sign_ok = 0
        local claim_level "not_mediation"

        if strpos("`spec'", "smdef") > 0 {
            local sign_ok = (`a3' < 0 & `b_sm' < 0 & `c3' > 0 & `idx' > 0)
            if `sign_ok' local claim_level "mechanism_consistent_only"
        }
        else {
            local sign_ok = (`a3' > 0 & `b_sm' > 0 & `c3' > 0 & `idx' > 0)
            if `sign_ok' local claim_level "source_sensitive"
        }

        post `pf' ("`source'") ("`layer'") ("`sm_lbl'") ///
            ("`sm'") ("`mediator_var'") ("`spec'") ///
            (`a3') (`a3_se') (`p_a3') ///
            (`b_sm') (`b_sm_se') (`p_b') ///
            (`c3') (`c3_se') (`p_c3') ///
            (`idx') (`sign_ok') ("`claim_level'") (`n_y') (`use_stage') ///
            (`n_m') (`n_y') (`r2_m') (`r2_y')

        restore
    }
}

postclose `pf'

preserve
use `sens', clear
sort source layer spec
export delimited using "$outdir/v3bpath_sensitivity_claim_audit.csv", replace
restore

tempfile timing ladder wet nonlinear proxy sourcedepth heat sensraw summary

import delimited using "$outdir/v3bpath_timing_audit.csv", clear
keep if inlist(window, "full", "v3pre30")
keep source layer window b_sm effective_n stage6_common_flag
reshape wide b_sm effective_n stage6_common_flag, i(source layer) j(window) string
rename b_smfull timing_full_b
rename b_smv3pre30 timing_v3pre30_b
rename effective_nv3pre30 timing_stage_effective_N
rename stage6_common_flagv3pre30 timing_stage6_common_flag
keep source layer timing_full_b timing_v3pre30_b timing_stage_effective_N timing_stage6_common_flag
save `timing'

import delimited using "$outdir/v3bpath_control_ladder.csv", clear
keep if ladder == "L0"
keep source layer b_sm
rename b_sm ladder_L0_b
save `ladder'

import delimited using "$outdir/v3bpath_wet_control_audit.csv", clear
keep if inlist(spec, "N0", "N1", "N2")
keep source layer spec b_sm
reshape wide b_sm, i(source layer) j(spec) string
gen wet_delta_b = b_smN1 - b_smN0
gen smdef_b = b_smN2
keep source layer wet_delta_b smdef_b
save `wet'

import delimited using "$outdir/v3bpath_nonlinear_audit.csv", clear
keep if spec == "quadratic"
keep source layer turning_in_support
rename turning_in_support quadratic_turning_in_support
save `nonlinear'

import delimited using "$outdir/v3bpath_proxy_competition.csv", clear
keep if control_version == "reduced"
gen proxy_compete_gap = compete_sm_dryxca - compete_d_dca
keep source layer proxy_compete_gap
save `proxy'

import delimited using "$outdir/v3bpath_source_depth_audit.csv", clear
keep if control_version == "reduced"
keep source layer a3 b_sm
rename a3 source_a3_reduced
rename b_sm source_b_reduced
save `sourcedepth'

import delimited using "$outdir/v3bpath_heat_consistency.csv", clear
keep if control_version == "reduced" & background_role == "rawSM_bg"
keep source layer b_hxca
rename b_hxca heat_Hxca_raw
save `heat'

import delimited using "$outdir/v3bpath_sensitivity_claim_audit.csv", clear
keep if spec == "raw_full_L0"
keep source layer claim_level
rename claim_level claim_level_raw
save `sensraw'

use `timing', clear
merge 1:1 source layer using `ladder'
assert _merge == 3
drop _merge
merge 1:1 source layer using `wet'
assert _merge == 3
drop _merge
merge 1:1 source layer using `nonlinear'
assert _merge == 3
drop _merge
merge 1:1 source layer using `proxy'
assert _merge == 3
drop _merge
merge 1:1 source layer using `sourcedepth'
assert _merge == 3
drop _merge
merge 1:1 source layer using `heat'
assert _merge == 3
drop _merge
merge 1:1 source layer using `sensraw'
assert _merge == 3
drop _merge
sort source layer
save `summary', replace
export delimited using "$outdir/v3bpath_sm_comparison_summary.csv", replace

di "=== v3bpath_step8_sensitivity_claim_audit.do COMPLETE ==="
log close
