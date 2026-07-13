* =============================================================================
* ggcp10_core_baseline_step0_preamble.do
* Purpose: Build compact full-season baseline-only analysis data.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/ggcp10_core_baseline_macros_include.do"

log using "$logdir/ggcp10_core_baseline_step0_preamble.log", replace

use "$corebase_dta", clear
xtset grid_id year

merge 1:1 grid_id year using "$builddir/data_v3_main.dta", ///
    keepusing(gdd_10_30 hotdrydays_ge32_pr_lt1) keep(master match)
assert _merge == 3
drop _merge

merge 1:1 grid_id year using "$statedir/sm_state_panel_wide.dta", ///
    keepusing(ds_pl_gsms ws_pl_gsms ds_mz_gsms ws_mz_gsms ///
              ds_pl_gsmrz ws_pl_gsmrz ds_mz_gsmrz ws_mz_gsmrz) ///
    keep(master match)
assert _merge == 3
drop _merge

gen HotDryPr_full = hotdrydays_ge32_pr_lt1
gen SR_x_HotDryPr_full = ca * HotDryPr_full

tempname pf
tempfile diag
postfile `pf' str48 item str120 value using `diag', replace

quietly count if main_sample == 1
post `pf' ("N_main_sample") ("`r(N)'")

foreach v in ln_yield ca D_full W_full SR_x_D_full hdd_ge32 SR_x_Heat_full ///
    HotDryPr_full SR_x_HotDryPr_full pr_sum et0_sum gdd_10_30 irr_frac aridity ///
    gleam_sms_mean gleam_smrz_mean ///
    ds_pl_gsms ws_pl_gsms ds_mz_gsms ws_mz_gsms ///
    ds_pl_gsmrz ws_pl_gsmrz ds_mz_gsmrz ws_mz_gsmrz {
    confirm variable `v'
}

foreach v in gleam_sms_mean gleam_smrz_mean ///
    ds_pl_gsms ws_pl_gsms ds_mz_gsms ws_mz_gsms ///
    ds_pl_gsmrz ws_pl_gsmrz ds_mz_gsmrz ws_mz_gsmrz {
    quietly count if main_sample == 1 & missing(`v')
    post `pf' ("missing_`v'_in_main") ("`r(N)'")
}

postclose `pf'
preserve
use `diag', clear
export delimited using "$core_diag_csv", replace
restore

compress
save "$core_ready_dta", replace

log close
di "=== ggcp10_core_baseline_step0_preamble.do COMPLETE ==="
