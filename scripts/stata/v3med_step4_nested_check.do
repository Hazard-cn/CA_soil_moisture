* =============================================================================
* v3med_step4_nested_check.do
* Purpose: Set 3 — Nested/restricted check. Drop X×RR from outcome eq.
*          If Set 3 ≈ Set 1/2 → pure indirect channel; if worse → need direct.
*          Uses primary SM source (gleam_sms_mean) only, both ctrl versions.
* Author:  YangSu + Claude
* Date:    2026-04-16
* Input:   data/processed/v3med_analysis_ready.dta
* Output:  output/tables/v3med_nested_check.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3med_macros_include.do"

log using "$logdir/v3med_step4_nested_check.log", replace

use "$datadir/v3med_analysis_ready.dta", clear
xtset grid_id year
keep if v3med_common == 1
di "Working sample N = " _N

* =============================================================================
* OUTPUT STORAGE
* =============================================================================
tempname pf
postfile `pf' str10 ctrl_version str10 module str10 model_type ///
    str12 equation str25 term ///
    double(b se p) long(N) double(r2) ///
    using "$outdir/v3med_nested_raw.dta", replace

* Primary SM for nested check
local sm "gleam_sms_mean"
local sm_lbl "GLEAM-Sfc"

foreach cv of global CTRL_VERSIONS {

    local ctrl_list "${CTRL_`cv'_med}"

    di _n "========================================"
    di "Nested check: ctrl=`cv'"
    di "========================================"

    * ===================== DROUGHT MODULE =====================

    * --- Mediator eq (same in both unrestricted and restricted) ---
    di _n "--- Drought mediator eq ---"
    reghdfe `sm' D_full ca SR_x_D_full hdd_ge32 `ctrl_list', ///
        absorb(grid_id year) vce(cluster grid_id)

    local nn = e(N)
    local rr = e(r2)
    foreach v in D_full ca SR_x_D_full hdd_ge32 {
        local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
        post `pf' ("`cv'") ("drought") ("nested") ("mediator") ("`v'") ///
            (_b[`v']) (_se[`v']) (`pval') (`nn') (`rr')
    }

    * --- Unrestricted outcome eq (with D×ca) ---
    di _n "--- Drought outcome UNRESTRICTED ---"
    reghdfe ln_yield D_full ca SR_x_D_full `sm' hdd_ge32 `ctrl_list', ///
        absorb(grid_id year) vce(cluster grid_id)

    local nn = e(N)
    local rr = e(r2)
    foreach v in D_full ca SR_x_D_full `sm' hdd_ge32 {
        local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
        local tname = cond("`v'" == "`sm'", "SM", "`v'")
        post `pf' ("`cv'") ("drought") ("unrestr") ("outcome") ("`tname'") ///
            (_b[`v']) (_se[`v']) (`pval') (`nn') (`rr')
    }

    * --- Restricted outcome eq (DROP D×ca = SR_x_D_full) ---
    di _n "--- Drought outcome RESTRICTED (no D x ca) ---"
    reghdfe ln_yield D_full ca `sm' hdd_ge32 `ctrl_list', ///
        absorb(grid_id year) vce(cluster grid_id)

    local nn = e(N)
    local rr = e(r2)
    foreach v in D_full ca `sm' hdd_ge32 {
        local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
        local tname = cond("`v'" == "`sm'", "SM", "`v'")
        post `pf' ("`cv'") ("drought") ("restr") ("outcome") ("`tname'") ///
            (_b[`v']) (_se[`v']) (`pval') (`nn') (`rr')
    }

    * ===================== HEAT MODULE =====================

    * --- Mediator eq ---
    di _n "--- Heat mediator eq ---"
    reghdfe `sm' hdd_ge32 ca SR_x_Heat_full D_full `ctrl_list', ///
        absorb(grid_id year) vce(cluster grid_id)

    local nn = e(N)
    local rr = e(r2)
    foreach v in hdd_ge32 ca SR_x_Heat_full D_full {
        local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
        post `pf' ("`cv'") ("heat") ("nested") ("mediator") ("`v'") ///
            (_b[`v']) (_se[`v']) (`pval') (`nn') (`rr')
    }

    * --- Unrestricted outcome eq (with H×ca) ---
    di _n "--- Heat outcome UNRESTRICTED ---"
    reghdfe ln_yield hdd_ge32 ca SR_x_Heat_full `sm' D_full `ctrl_list', ///
        absorb(grid_id year) vce(cluster grid_id)

    local nn = e(N)
    local rr = e(r2)
    foreach v in hdd_ge32 ca SR_x_Heat_full `sm' D_full {
        local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
        local tname = cond("`v'" == "`sm'", "SM", "`v'")
        post `pf' ("`cv'") ("heat") ("unrestr") ("outcome") ("`tname'") ///
            (_b[`v']) (_se[`v']) (`pval') (`nn') (`rr')
    }

    * --- Restricted outcome eq (DROP H×ca = SR_x_Heat_full) ---
    di _n "--- Heat outcome RESTRICTED (no H x ca) ---"
    reghdfe ln_yield hdd_ge32 ca `sm' D_full `ctrl_list', ///
        absorb(grid_id year) vce(cluster grid_id)

    local nn = e(N)
    local rr = e(r2)
    foreach v in hdd_ge32 ca `sm' D_full {
        local pval = 2*ttail(e(df_r), abs(_b[`v']/_se[`v']))
        local tname = cond("`v'" == "`sm'", "SM", "`v'")
        post `pf' ("`cv'") ("heat") ("restr") ("outcome") ("`tname'") ///
            (_b[`v']) (_se[`v']) (`pval') (`nn') (`rr')
    }
}

postclose `pf'

* =============================================================================
* EXPORT
* =============================================================================
use "$outdir/v3med_nested_raw.dta", clear
export delimited using "$outdir/v3med_nested_check.csv", replace
cap erase "$outdir/v3med_nested_raw.dta"

* Summary
di _n "=== R2 comparison: unrestricted vs restricted ==="
import delimited "$outdir/v3med_nested_check.csv", clear
keep if equation == "outcome" & term == "D_full"
list ctrl_version module model_type r2, sep(0)

log close
di "=== v3med_step4_nested_check.do COMPLETE ==="
