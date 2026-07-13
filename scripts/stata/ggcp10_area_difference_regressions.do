* =============================================================================
* ggcp10_area_difference_regressions.do
* Purpose: Regress log(old area / new area) on D, ca, and SR x D.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global suitedir "$projdir/temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite"
global builddir "$projdir/data_build/data/processed"
global logdir "$suitedir/logs"
global outcsv "$suitedir/ggcp10_area_difference_regressions.csv"
global CTRL "hdd_ge32 pr_sum et0_sum aridity gdd_10_30 irr_frac"

log using "$logdir/ggcp10_area_difference_regressions.log", replace

use "$suitedir/v3_analysis_ready_ggcp10_harvarea_agg.dta", clear
xtset grid_id year

merge 1:1 grid_id year using "$builddir/data_v3_main.dta", ///
    keepusing(gdd_10_30) keep(master match)
assert _merge == 3
drop _merge

gen ln_area_ratio_old_to_new = ln(orig_maize_area_km2 / maize_area_km2)
keep if main_sample == 1

tempname pf
postfile `pf' str16 spec str16 term double(b se p) long(N) double(r2) ///
    using "$suitedir/ggcp10_area_difference_regressions_raw.dta", replace

foreach spec in bare controls {
    local rhs "D_full ca SR_x_D_full"
    if "`spec'" == "controls" local rhs "D_full ca SR_x_D_full $CTRL"
    reghdfe ln_area_ratio_old_to_new `rhs', absorb(grid_id year) vce(cluster grid_id)
    local nn = e(N)
    local rr = e(r2)
    foreach term in D_full ca SR_x_D_full {
        local pval = 2 * ttail(e(df_r), abs(_b[`term'] / _se[`term']))
        post `pf' ("`spec'") ("`term'") (_b[`term']) (_se[`term']) (`pval') (`nn') (`rr')
    }
}

postclose `pf'
use "$suitedir/ggcp10_area_difference_regressions_raw.dta", clear
export delimited using "$outcsv", replace
cap erase "$suitedir/ggcp10_area_difference_regressions_raw.dta"

log close
di "=== ggcp10_area_difference_regressions.do COMPLETE ==="
