* =============================================================================
* v3bpath_run_all.do
* Purpose: Master runner for the v3bpath unified audit line.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3bpath_macros_include.do"

cap log close master
log using "$logdir/v3bpath_run_all.log", replace text name(master)

foreach step in ///
    v3bpath_step0_preamble ///
    v3bpath_step1_timing_audit ///
    v3bpath_step2_control_ladder ///
    v3bpath_step3_wet_control_audit ///
    v3bpath_step4_nonlinear_audit ///
    v3bpath_step5_proxy_competition ///
    v3bpath_step6_source_depth_audit ///
    v3bpath_step7_heat_consistency ///
    v3bpath_step8_sensitivity_claim_audit {

    di _n ">>> Running `step'.do"
    capture noisily do "$projdir/scripts/stata/`step'.do"
    if _rc != 0 {
        di "FAILED: `step'.do returned rc = " _rc
        log close master
        exit _rc
    }
}

di "=== v3bpath_run_all.do COMPLETE ==="
log close master
