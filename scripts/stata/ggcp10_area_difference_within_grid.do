* =============================================================================
* ggcp10_area_difference_within_grid.do
* Purpose: Test whether log(old area / new area) remains related to SR x D after
*          progressively tighter FE structures.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global suitedir "$projdir/temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite"
global builddir "$projdir/data_build/data/processed"
global logdir "$suitedir/logs"
global outcsv "$suitedir/ggcp10_area_difference_within_grid.csv"
global CTRL "hdd_ge32 pr_sum et0_sum aridity gdd_10_30 irr_frac"

log using "$logdir/ggcp10_area_difference_within_grid.log", replace

use "$suitedir/v3_analysis_ready_ggcp10_harvarea_agg.dta", clear
xtset grid_id year

merge 1:1 grid_id year using "$builddir/data_v3_main.dta", ///
    keepusing(gdd_10_30) keep(master match)
assert _merge == 3
drop _merge

gen ln_area_ratio_old_to_new = ln(orig_maize_area_km2 / maize_area_km2)
capture confirm variable prov_year
if _rc egen prov_year = group(province year)
keep if main_sample == 1

tempname pf
postfile `pf' str24 spec str24 absorbset str16 term double(b se p) long(N) double(r2) ///
    using "$suitedir/ggcp10_area_difference_within_grid_raw.dta", replace

foreach spec in bare controls {
    local rhs "D_full ca SR_x_D_full"
    if "`spec'" == "controls" local rhs "D_full ca SR_x_D_full $CTRL"

    foreach absorbset in grid_year grid_provyear {
        local absorbs "grid_id year"
        if "`absorbset'" == "grid_provyear" local absorbs "grid_id prov_year"

        reghdfe ln_area_ratio_old_to_new `rhs', absorb(`absorbs') vce(cluster grid_id)
        local nn = e(N)
        local rr = e(r2)
        foreach term in D_full ca SR_x_D_full {
            local pval = 2 * ttail(e(df_r), abs(_b[`term'] / _se[`term']))
            post `pf' ("`spec'") ("`absorbset'") ("`term'") ///
                (_b[`term']) (_se[`term']) (`pval') (`nn') (`rr')
        }
    }
}

postclose `pf'
use "$suitedir/ggcp10_area_difference_within_grid_raw.dta", clear
export delimited using "$outcsv", replace
cap erase "$suitedir/ggcp10_area_difference_within_grid_raw.dta"

log close
di "=== ggcp10_area_difference_within_grid.do COMPLETE ==="
