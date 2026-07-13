* =============================================================================
* v4smstate_run_all.do
* Purpose: Master runner for the state-based SM sidecar audit.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v4smstate_macros_include.do"

cap log close master
log using "$tempdir/sm_state_run_all.log", replace text name(master)

foreach step in ///
    v4smstate_step0_preamble ///
    v4smstate_step1_descriptives ///
    v4smstate_step2_state_models {

    di _n ">>> Running `step'.do"
    capture noisily do "$projdir/scripts/stata/`step'.do"
    if _rc != 0 {
        di as error "FAILED: `step'.do returned rc = " _rc
        log close master
        exit _rc
    }
}

di "=== v4smstate_run_all.do COMPLETE ==="
log close master
