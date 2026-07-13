* =============================================================================
* v4smstate_step0_preamble.do
* Purpose: Build merged analysis-ready panel for the state-based SM sidecar.
* Input:   data/processed/v3prhdsm_analysis_ready.dta
*          data/processed/v3_analysis_ready.dta
*          temp/2026-04-21_sm_state_audit/sm_state_panel_wide.dta
* Output:  temp/2026-04-21_sm_state_audit/sm_state_analysis_ready.dta
*          temp/2026-04-21_sm_state_audit/sm_state_diagnostics.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v4smstate_macros_include.do"

log using "$tempdir/sm_state_step0_preamble.log", replace

use "$datadir/v3prhdsm_analysis_ready.dta", clear
xtset grid_id year

merge 1:1 grid_id year using "$datadir/v3_analysis_ready.dta", ///
    keepusing(W_full W_v3pre30 W_v3pm10) keep(master match)
tab _merge
assert _merge == 3
drop _merge

merge 1:1 grid_id year using "$state_wide_dta", keep(master match)
tab _merge
assert _merge == 3
drop _merge

confirm variable ln_yield ca main_sample grid_id year irr_frac
confirm variable D_full SR_x_D_full hdd_ge32 gdd_10_30 W_full
confirm variable D_v3pre30 SR_x_D_v3pre30 hdd_ge32_v3pre30 gdd_10_30_v3pre30 W_v3pre30
confirm variable D_v3pm10 SR_x_D_v3pm10 hdd_ge32_v3pm10 gdd_10_30_v3pm10 W_v3pm10

local n_sm : word count $STATE_SM_BASES

foreach w of global STATE_WINDOWS {
    local sfx ""
    local d_var "D_full"
    local dca_var "SR_x_D_full"
    local h_var "hdd_ge32"
    local g_var "gdd_10_30"
    local w_var "W_full"

    if "`w'" != "full" {
        local sfx "_`w'"
        local d_var "D_`w'"
        local dca_var "SR_x_D_`w'"
        local h_var "hdd_ge32_`w'"
        local g_var "gdd_10_30_`w'"
        local w_var "W_`w'"
    }

    local sample_var "state_`w'_6_sample"
    gen byte `sample_var' = (main_sample == 1) if !missing(main_sample)
    replace `sample_var' = 0 if missing(`sample_var')

    foreach v in ln_yield ca irr_frac `d_var' `dca_var' `h_var' `g_var' `w_var' {
        replace `sample_var' = 0 if missing(`v') & `sample_var' == 1
    }

    forvalues i = 1/`n_sm' {
        local sm     : word `i' of $STATE_SM_BASES
        local prefix : word `i' of $STATE_PREFIXES
        local raw_var "`sm'`sfx'"

        confirm variable `raw_var'
        replace `sample_var' = 0 if missing(`raw_var') & `sample_var' == 1

        foreach short in pl mz {
            foreach kind in ds ws {
                local state_var "`kind'_`short'_`prefix'`sfx'"
                confirm variable `state_var'
                replace `sample_var' = 0 if missing(`state_var') & `sample_var' == 1
            }
        }

        local vd_var "vd_`prefix'`sfx'"
        confirm variable `vd_var'
        replace `sample_var' = 0 if missing(`vd_var') & `sample_var' == 1
    }

    label var `sample_var' "State-sidecar common sample across 6 SM sources (`w')"
}

tempname pf
tempfile diag
postfile `pf' str40 item double value using `diag', replace

quietly count if main_sample == 1
post `pf' ("N_main_sample") (r(N))

foreach w of global STATE_WINDOWS {
    quietly count if state_`w'_6_sample == 1
    post `pf' ("N_state_`w'_6_sample") (r(N))
}

postclose `pf'

preserve
use `diag', clear
export delimited using "$state_diag_csv", replace
restore

compress
save "$state_ready_dta", replace

di "Saved merged analysis-ready file: $state_ready_dta"
log close
