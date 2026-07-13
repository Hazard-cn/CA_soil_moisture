* =============================================================================
* v5drymed_step0_preamble.do
* Purpose: Build drought-only analysis-ready data with dry-side mediator aliases.
* Input:   data/processed/v3_analysis_ready.dta
*          data/processed/v3sub_analysis_ready.dta
*          data_build/data/processed/data_v3_main.dta
*          temp/2026-04-21_sm_state_audit/sm_state_panel_wide.dta
* Output:  data/processed/v5drymed_analysis_ready.dta
*          output/tables/v5drymed_diagnostics.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v5drymed_macros_include.do"

cap mkdir "$outdir"
cap mkdir "$figdir"
cap mkdir "$logdir"

log using "$logdir/v5drymed_step0_preamble.log", replace

use "$datadir/v3_analysis_ready.dta", clear
xtset grid_id year

merge 1:1 grid_id year using "$datadir/v3sub_analysis_ready.dta", ///
    keepusing(maize_zone irr_group) keep(master match)
tab _merge
assert _merge == 3
drop _merge

local state_keep ""
foreach prefix of global DRY_PREFIXES {
    local state_keep "`state_keep' dd_pl_`prefix' dd_mz_`prefix'"
}

merge 1:1 grid_id year using "$tempdir/sm_state_panel_wide.dta", ///
    keepusing(`state_keep') keep(master match)
tab _merge
assert _merge == 3
drop _merge

local build_keep "gdd_10_30"
foreach src of global DRY_SOURCE_TOKENS {
    foreach pct in p10 p20 {
        local build_keep "`build_keep' drydays_`src'_le_`pct'"
        local build_keep "`build_keep' dryshare_`src'_le_`pct'"
        local build_keep "`build_keep' drydeficit_`src'_le_`pct'"
    }
    local build_keep "`build_keep' dryshare_pl_`src'_le_p25"
    local build_keep "`build_keep' dryshare_mz_`src'_le_p25"
    local build_keep "`build_keep' drydeficit_pl_`src'_le_p25"
    local build_keep "`build_keep' drydeficit_mz_`src'_le_p25"
}

merge 1:1 grid_id year using "$builddir/data_v3_main.dta", ///
    keepusing(`build_keep') keep(master match)
tab _merge
assert _merge == 3
drop _merge

capture confirm variable W_full
if _rc != 0 {
    confirm variable spei6_mean
    gen double W_full = max(0, spei6_mean)
}

capture confirm variable SR_x_W_full
if _rc != 0 {
    gen double SR_x_W_full = ca * W_full
}

confirm variable ln_yield D_full W_full ca SR_x_D_full SR_x_W_full hdd_ge32
confirm variable irr_frac pr_sum et0_sum aridity gdd_10_30
confirm variable grid_id year main_sample maize_zone irr_group

forvalues i = 1/6 {
    local src : word `i' of $DRY_SOURCE_TOKENS
    local prefix : word `i' of $DRY_PREFIXES

    gen double v5dd_bl_p10_`prefix' = drydays_`src'_le_p10
    gen double v5dd_bl_p20_`prefix' = drydays_`src'_le_p20
    gen double v5dd_pl_p25_`prefix' = dd_pl_`prefix'
    gen double v5dd_mz_p25_`prefix' = dd_mz_`prefix'

    gen double v5ds_bl_p10_`prefix' = dryshare_`src'_le_p10
    gen double v5ds_bl_p20_`prefix' = dryshare_`src'_le_p20
    gen double v5ds_pl_p25_`prefix' = dryshare_pl_`src'_le_p25
    gen double v5ds_mz_p25_`prefix' = dryshare_mz_`src'_le_p25

    gen double v5ddf_bl_p10_`prefix' = drydeficit_`src'_le_p10
    gen double v5ddf_bl_p20_`prefix' = drydeficit_`src'_le_p20
    gen double v5ddf_pl_p25_`prefix' = drydeficit_pl_`src'_le_p25
    gen double v5ddf_mz_p25_`prefix' = drydeficit_mz_`src'_le_p25
}

local n_tags : word count $V5_SAMPLE_TAGS
forvalues t = 1/`n_tags' {
    local tag : word `t' of $V5_SAMPLE_TAGS
    gen byte v5s_`tag' = (main_sample == 1) if !missing(main_sample)
    replace v5s_`tag' = 0 if missing(v5s_`tag')

    foreach v in ln_yield D_full W_full ca SR_x_D_full SR_x_W_full hdd_ge32 ///
        irr_frac pr_sum et0_sum aridity gdd_10_30 maize_zone irr_group {
        replace v5s_`tag' = 0 if missing(`v') & v5s_`tag' == 1
    }

    foreach prefix of global DRY_PREFIXES {
        local med_var "v5`tag'_`prefix'"
        confirm variable `med_var'
        replace v5s_`tag' = 0 if missing(`med_var') & v5s_`tag' == 1
    }

    label var v5s_`tag' "v5drymed common sample: `tag'"
}

tempname pf
tempfile diag
postfile `pf' str40 item str80 value using `diag', replace

quietly count if main_sample == 1
post `pf' ("N_main_sample") ("`r(N)'")

_pctile ca if main_sample == 1, p(25 50 75)
post `pf' ("ca_p25_main") (string(r(r1), "%9.4f"))
post `pf' ("ca_p50_main") (string(r(r2), "%9.4f"))
post `pf' ("ca_p75_main") (string(r(r3), "%9.4f"))

forvalues t = 1/`n_tags' {
    local tag : word `t' of $V5_SAMPLE_TAGS
    quietly count if v5s_`tag' == 1
    post `pf' ("N_v5s_`tag'") ("`r(N)'")
}

postclose `pf'

preserve
use `diag', clear
export delimited using "$v5diag_csv", replace
restore

compress
save "$v5ready_dta", replace

log close
di "=== v5drymed_step0_preamble.do COMPLETE ==="
