version 18.0
clear all
set more off
set seed 42
args input_file output_file
use "`input_file'", clear
capture which reghdfe
if _rc {
    di as error "reghdfe is required"
    exit 499
}
reghdfe ln_yield x01-x28, absorb(grid_id prov_year) vce(cluster grid_id)
tempname handle
postfile `handle' str8 term double coefficient cluster_se using "`output_file'", replace
foreach variable of varlist x01-x28 {
    post `handle' ("`variable'") (_b[`variable']) (_se[`variable'])
}
postclose `handle'
exit, clear
