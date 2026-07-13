* =============================================================================
* v6gleambl_agg_fullfamily_run_all.do
* Purpose: Master runner for GGCP10 aggregated-area GLEAM full-family rerun.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global v6rundir "$projdir/temp/2026-05-18_ggcp10_harvarea_agg_v6gleambl_fullfamily"
global logdir "$v6rundir/logs"
cap mkdir "$v6rundir"
cap mkdir "$logdir"

cap log close master
log using "$logdir/v6gleambl_agg_fullfamily_run_all.log", replace text name(master)

global V6N_MACROS_INCLUDE "$projdir/scripts/stata/v6gleambl_agg_nomwet_macros_include.do"
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

global V6H_MACROS_INCLUDE "$projdir/scripts/stata/v6gleambl_agg_heatctrl_macros_include.do"
foreach step in ///
    v6gleambl_heatctrl_step0_preamble ///
    v6gleambl_heatctrl_step1_model8 {
    di _n ">>> Running `step'.do"
    capture noisily do "$projdir/scripts/stata/`step'.do"
    if _rc != 0 {
        di as error "FAILED: `step'.do returned rc = " _rc
        log close master
        exit _rc
    }
}

global V6Q_MACROS_INCLUDE "$projdir/scripts/stata/v6gleambl_agg_hotdryctrl_macros_include.do"
foreach step in ///
    v6gleambl_hotdryctrl_step0_preamble ///
    v6gleambl_hotdryctrl_step1_model8 {
    di _n ">>> Running `step'.do"
    capture noisily do "$projdir/scripts/stata/`step'.do"
    if _rc != 0 {
        di as error "FAILED: `step'.do returned rc = " _rc
        log close master
        exit _rc
    }
}

di "=== v6gleambl_agg_fullfamily_run_all.do COMPLETE ==="
log close master
