* =============================================================================
* v5drymed_run_all.do
* Purpose: Master runner for drought-only dry-side moderated mediation.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v5drymed_macros_include.do"

cap log close master
log using "$logdir/v5drymed_run_all.log", replace text name(master)

foreach step in ///
    v5drymed_step0_preamble ///
    v5drymed_step1_model8 ///
    v5drymed_step2_bootstrap ///
    v5drymed_step3_heterogeneity ///
    v5drymed_step4_summary {

    di _n ">>> Running `step'.do"
    capture noisily do "$projdir/scripts/stata/`step'.do"
    if _rc != 0 {
        di as error "FAILED: `step'.do returned rc = " _rc
        log close master
        exit _rc
    }
}

di "=== v5drymed_run_all.do COMPLETE ==="
log close master
