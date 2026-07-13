* =============================================================================
* v4smstate_step2_state_models.do
* Purpose: Run comparable raw-vs-state outcome models and state mediator models.
* Input:   temp/2026-04-21_sm_state_audit/sm_state_analysis_ready.dta
* Output:  temp/2026-04-21_sm_state_audit/sm_state_model_all.csv
*          temp/2026-04-21_sm_state_audit/sm_state_model_main.csv
*          temp/2026-04-21_sm_state_audit/sm_state_model_v3pm10.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v4smstate_macros_include.do"

log using "$tempdir/sm_state_step2_models.log", replace

use "$state_ready_dta", clear
xtset grid_id year

local n_sm : word count $STATE_SM_BASES
local n_scheme : word count $STATE_SCHEMES

tempname pf
tempfile results
postfile `pf' str10 window str12 threshold_scheme str8 source str10 layer str12 sm_label ///
    str14 spec str24 raw_sm_var str24 dry_var str24 wet_var ///
    double a1 se_a1 p_a1 ///
    double a3 se_a3 p_a3 ///
    double c1 se_c1 p_c1 ///
    double c3 se_c3 p_c3 ///
    double b_main se_b_main p_b_main ///
    double b_wet se_b_wet p_b_wet ///
    double b_h se_b_h p_b_h ///
    long N_m long N_y double r2_m double r2_y ///
    byte n_match_state using `results', replace

foreach w of global STATE_WINDOWS {
    local sfx ""
    local d_var "D_full"
    local dca_var "SR_x_D_full"
    local h_var "hdd_ge32"
    local g_var "gdd_10_30"
    local w_var "W_full"
    local sample_var "state_full_6_sample"

    if "`w'" != "full" {
        local sfx "_`w'"
        local d_var "D_`w'"
        local dca_var "SR_x_D_`w'"
        local h_var "hdd_ge32_`w'"
        local g_var "gdd_10_30_`w'"
        local w_var "W_`w'"
        local sample_var "state_`w'_6_sample"
    }

    forvalues i = 1/`n_sm' {
        local sm      : word `i' of $STATE_SM_BASES
        local source  : word `i' of $STATE_SOURCES
        local layer   : word `i' of $STATE_LAYERS
        local sm_lbl  : word `i' of $STATE_SM_LABELS
        local prefix  : word `i' of $STATE_PREFIXES
        local raw_var "`sm'`sfx'"

        reghdfe ln_yield `d_var' ca `dca_var' `raw_var' `w_var' `h_var' irr_frac `g_var' ///
            if `sample_var' == 1, absorb(grid_id year) vce(cluster grid_id)

        local legacy_df = e(df_r)
        local legacy_n = e(N)
        local legacy_r2 = e(r2)
        local legacy_p_c1 = 2 * ttail(`legacy_df', abs(_b[`d_var'] / _se[`d_var']))
        local legacy_p_c3 = 2 * ttail(`legacy_df', abs(_b[`dca_var'] / _se[`dca_var']))
        local legacy_p_b = 2 * ttail(`legacy_df', abs(_b[`raw_var'] / _se[`raw_var']))
        local legacy_p_w = 2 * ttail(`legacy_df', abs(_b[`w_var'] / _se[`w_var']))
        local legacy_p_h = 2 * ttail(`legacy_df', abs(_b[`h_var'] / _se[`h_var']))

        local legacy_c1 = _b[`d_var']
        local legacy_se_c1 = _se[`d_var']
        local legacy_c3 = _b[`dca_var']
        local legacy_se_c3 = _se[`dca_var']
        local legacy_b = _b[`raw_var']
        local legacy_se_b = _se[`raw_var']
        local legacy_w = _b[`w_var']
        local legacy_se_w = _se[`w_var']
        local legacy_h = _b[`h_var']
        local legacy_se_h = _se[`h_var']

        forvalues s = 1/`n_scheme' {
            local scheme : word `s' of $STATE_SCHEMES
            local short  : word `s' of $STATE_SCHEME_SHORTS
            local dry_var "ds_`short'_`prefix'`sfx'"
            local wet_var "ws_`short'_`prefix'`sfx'"

            reghdfe ln_yield `d_var' ca `dca_var' `raw_var' `wet_var' `h_var' irr_frac `g_var' ///
                if `sample_var' == 1, absorb(grid_id year) vce(cluster grid_id)

            local rsc_df = e(df_r)
            local rsc_n = e(N)
            local rsc_r2 = e(r2)
            local rsc_p_c1 = 2 * ttail(`rsc_df', abs(_b[`d_var'] / _se[`d_var']))
            local rsc_p_c3 = 2 * ttail(`rsc_df', abs(_b[`dca_var'] / _se[`dca_var']))
            local rsc_p_b = 2 * ttail(`rsc_df', abs(_b[`raw_var'] / _se[`raw_var']))
            local rsc_p_w = 2 * ttail(`rsc_df', abs(_b[`wet_var'] / _se[`wet_var']))
            local rsc_p_h = 2 * ttail(`rsc_df', abs(_b[`h_var'] / _se[`h_var']))
            local rsc_c1 = _b[`d_var']
            local rsc_se_c1 = _se[`d_var']
            local rsc_c3 = _b[`dca_var']
            local rsc_se_c3 = _se[`dca_var']
            local rsc_b = _b[`raw_var']
            local rsc_se_b = _se[`raw_var']
            local rsc_w = _b[`wet_var']
            local rsc_se_w = _se[`wet_var']
            local rsc_h = _b[`h_var']
            local rsc_se_h = _se[`h_var']

            reghdfe `dry_var' `d_var' ca `dca_var' `h_var' irr_frac `g_var' ///
                if `sample_var' == 1, absorb(grid_id year) vce(cluster grid_id)

            local state_df_m = e(df_r)
            local state_n_m = e(N)
            local state_r2_m = e(r2)
            local state_p_a1 = 2 * ttail(`state_df_m', abs(_b[`d_var'] / _se[`d_var']))
            local state_p_a3 = 2 * ttail(`state_df_m', abs(_b[`dca_var'] / _se[`dca_var']))
            local state_a1 = _b[`d_var']
            local state_se_a1 = _se[`d_var']
            local state_a3 = _b[`dca_var']
            local state_se_a3 = _se[`dca_var']

            reghdfe ln_yield `d_var' ca `dca_var' `dry_var' `wet_var' `h_var' irr_frac `g_var' ///
                if `sample_var' == 1, absorb(grid_id year) vce(cluster grid_id)

            local state_df_y = e(df_r)
            local state_n_y = e(N)
            local state_r2_y = e(r2)
            local state_p_c1 = 2 * ttail(`state_df_y', abs(_b[`d_var'] / _se[`d_var']))
            local state_p_c3 = 2 * ttail(`state_df_y', abs(_b[`dca_var'] / _se[`dca_var']))
            local state_p_b = 2 * ttail(`state_df_y', abs(_b[`dry_var'] / _se[`dry_var']))
            local state_p_w = 2 * ttail(`state_df_y', abs(_b[`wet_var'] / _se[`wet_var']))
            local state_p_h = 2 * ttail(`state_df_y', abs(_b[`h_var'] / _se[`h_var']))
            local state_c1 = _b[`d_var']
            local state_se_c1 = _se[`d_var']
            local state_c3 = _b[`dca_var']
            local state_se_c3 = _se[`dca_var']
            local state_b = _b[`dry_var']
            local state_se_b = _se[`dry_var']
            local state_w = _b[`wet_var']
            local state_se_w = _se[`wet_var']
            local state_h = _b[`h_var']
            local state_se_h = _se[`h_var']

            local n_match = (`rsc_n' == `state_n_y')
            if `n_match' == 0 {
                di as error "N mismatch: `w' / `scheme' / `sm_lbl' raw-statectrl N=`rsc_n', state-main N=`state_n_y'"
                exit 459
            }

            post `pf' ("`w'") ("`scheme'") ("`source'") ("`layer'") ("`sm_lbl'") ///
                ("Raw-Legacy") ("`raw_var'") ("") ("`w_var'") ///
                (.) (.) (.) ///
                (.) (.) (.) ///
                (`legacy_c1') (`legacy_se_c1') (`legacy_p_c1') ///
                (`legacy_c3') (`legacy_se_c3') (`legacy_p_c3') ///
                (`legacy_b') (`legacy_se_b') (`legacy_p_b') ///
                (`legacy_w') (`legacy_se_w') (`legacy_p_w') ///
                (`legacy_h') (`legacy_se_h') (`legacy_p_h') ///
                (.) (`legacy_n') (.) (`legacy_r2') (1)

            post `pf' ("`w'") ("`scheme'") ("`source'") ("`layer'") ("`sm_lbl'") ///
                ("Raw-StateCtrl") ("`raw_var'") ("") ("`wet_var'") ///
                (.) (.) (.) ///
                (.) (.) (.) ///
                (`rsc_c1') (`rsc_se_c1') (`rsc_p_c1') ///
                (`rsc_c3') (`rsc_se_c3') (`rsc_p_c3') ///
                (`rsc_b') (`rsc_se_b') (`rsc_p_b') ///
                (`rsc_w') (`rsc_se_w') (`rsc_p_w') ///
                (`rsc_h') (`rsc_se_h') (`rsc_p_h') ///
                (.) (`rsc_n') (.) (`rsc_r2') (`n_match')

            post `pf' ("`w'") ("`scheme'") ("`source'") ("`layer'") ("`sm_lbl'") ///
                ("State-Main") ("`raw_var'") ("`dry_var'") ("`wet_var'") ///
                (`state_a1') (`state_se_a1') (`state_p_a1') ///
                (`state_a3') (`state_se_a3') (`state_p_a3') ///
                (`state_c1') (`state_se_c1') (`state_p_c1') ///
                (`state_c3') (`state_se_c3') (`state_p_c3') ///
                (`state_b') (`state_se_b') (`state_p_b') ///
                (`state_w') (`state_se_w') (`state_p_w') ///
                (`state_h') (`state_se_h') (`state_p_h') ///
                (`state_n_m') (`state_n_y') (`state_r2_m') (`state_r2_y') (`n_match')
        }
    }
}

postclose `pf'

use `results', clear
sort threshold_scheme window source layer spec
export delimited using "$state_model_all_csv", replace

preserve
keep if inlist(window, "full", "v3pre30")
export delimited using "$state_model_main_csv", replace
restore

preserve
keep if window == "v3pm10"
export delimited using "$state_model_neg_csv", replace
restore

log close
