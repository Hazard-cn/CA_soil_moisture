version 18.0
clear all
set more off
set seed 42

args input_path output_csv log_path

capture log close
log using "`log_path'", text replace

use "`input_path'", clear
isid grid_id year

local model_terms ///
    NE_exposure NE_ca NE_ca_exposure ///
    HHH_exposure HHH_ca HHH_ca_exposure ///
    NW_exposure NW_ca NW_ca_exposure ///
    SH_exposure SH_ca SH_ca_exposure ///
    SW_exposure SW_ca SW_ca_exposure ///
    gdd_10_29_per100 pr_sum_per100 pr_sum_sq_per10000

reghdfe ln_yield `model_terms', absorb(grid_id province_year_id) vce(cluster grid_id)

tempname results
tempfile coefficient_dta
postfile `results' str32 term double estimate se_cluster_grid using `coefficient_dta', replace
foreach term of local model_terms {
    post `results' ("`term'") (_b[`term']) (_se[`term'])
}
postclose `results'

use `coefficient_dta', clear
gen str20 software = "Stata 18 reghdfe"
export delimited using "`output_csv'", replace

log close
exit, clear
