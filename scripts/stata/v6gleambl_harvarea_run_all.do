* =============================================================================
* v6gleambl_harvarea_run_all.do
* Purpose: Master runner for GGCP10 harvested-area v6gleambl rerun.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global V6_MACROS_INCLUDE "$projdir/scripts/stata/v6gleambl_harvarea_macros_include.do"
global V6_BOOT_REPS "20"
do "$V6_MACROS_INCLUDE"

cap log close master
log using "$logdir/v6gleambl_harvarea_run_all.log", replace text name(master)

foreach step in ///
    v6gleambl_step0_preamble ///
    v6gleambl_step1_model8 ///
    v6gleambl_step2_bootstrap {

    di _n ">>> Running `step'.do"
    capture noisily do "$projdir/scripts/stata/`step'.do"
    if _rc != 0 {
        di as error "FAILED: `step'.do returned rc = " _rc
        log close master
        exit _rc
    }
}

di "=== v6gleambl_harvarea_run_all.do COMPLETE ==="
log close master
