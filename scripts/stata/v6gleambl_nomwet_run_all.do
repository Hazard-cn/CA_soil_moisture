* =============================================================================
* v6gleambl_nomwet_run_all.do
* Purpose: Master runner for four-window GLEAM baseline rerun without M_wet.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v6gleambl_nomwet_macros_include.do"

cap log close master
log using "$logdir/v6gleambl_nomwet_run_all.log", replace text name(master)

foreach step in ///
    v6gleambl_nomwet_step0_preamble ///
    v6gleambl_nomwet_step1_model8 {
    di _n ">>> Running `step'.do"
    capture noisily do "$projdir/scripts/stata/`step'.do"
    if _rc != 0 {
        di as error "FAILED: `step'.do returned rc = " _rc
        log close master
        exit _rc
    }
}

di "=== v6gleambl_nomwet_run_all.do COMPLETE ==="
log close master
