* =============================================================================
* v3med_step1_set0_baseline.do
* Purpose: Set 0 — Confirm total buffering exists (no SM in the model).
*          Drought baseline: lnY ~ D + H + ca + SR×D + controls + FE
*          Heat baseline:    lnY ~ H + D + ca + SR×H + controls + FE
*          Two control versions × two modules = 4 regressions.
* Author:  YangSu + Claude
* Date:    2026-04-16
* Input:   data/processed/v3med_analysis_ready.dta
* Output:  output/tables/v3med_set0_baseline.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3med_macros_include.do"

log using "$logdir/v3med_step1_set0_baseline.log", replace

use "$datadir/v3med_analysis_ready.dta", clear
xtset grid_id year

* Sample
keep if v3med_common == 1
di "Working sample N = " _N

* =============================================================================
* Set up output file
* =============================================================================
tempname pf
postfile `pf' str10 ctrl_version str10 module str25 term ///
    double(b se p) long(N) double(r2) ///
    using "$outdir/v3med_set0_raw.dta", replace

* =============================================================================
* Loop: 2 control versions × 2 modules
* =============================================================================
foreach cv of global CTRL_VERSIONS {

    local ctrl_list "${CTRL_`cv'_med}"
    di _n "========================================"
    di "Control version: `cv' — `ctrl_list'"
    di "========================================"

    * --- Drought baseline ---
    di _n "--- Drought baseline (ctrl=`cv') ---"
    reghdfe ln_yield D_full hdd_ge32 ca SR_x_D_full `ctrl_list', ///
        absorb(grid_id year) vce(cluster grid_id)

    local nn = e(N)
    local rr = e(r2)

    foreach v in D_full hdd_ge32 ca SR_x_D_full {
        post `pf' ("`cv'") ("drought") ("`v'") ///
            (_b[`v']) (_se[`v']) (2*ttail(e(df_r), abs(_b[`v']/_se[`v']))) ///
            (`nn') (`rr')
    }

    * --- Heat baseline ---
    di _n "--- Heat baseline (ctrl=`cv') ---"
    reghdfe ln_yield hdd_ge32 D_full ca SR_x_Heat_full `ctrl_list', ///
        absorb(grid_id year) vce(cluster grid_id)

    local nn = e(N)
    local rr = e(r2)

    foreach v in hdd_ge32 D_full ca SR_x_Heat_full {
        post `pf' ("`cv'") ("heat") ("`v'") ///
            (_b[`v']) (_se[`v']) (2*ttail(e(df_r), abs(_b[`v']/_se[`v']))) ///
            (`nn') (`rr')
    }
}

postclose `pf'

* Export to CSV
use "$outdir/v3med_set0_raw.dta", clear
export delimited using "$outdir/v3med_set0_baseline.csv", replace
erase "$outdir/v3med_set0_raw.dta"

* Quick summary
di _n "=== Set 0 Results Summary ==="
import delimited "$outdir/v3med_set0_baseline.csv", clear
list, sep(4)

log close
di "=== v3med_step1_set0_baseline.do COMPLETE ==="
