* =============================================================================
* v3proxy_step0_preamble.do
* Purpose: Prepare common sample and DrySM variables for the v3proxy line.
* Input:   data/processed/v3prhdsm_analysis_ready.dta
* Output:  data/processed/v3proxy_analysis_ready.dta
*          output/tables/v3proxy_sample_diagnostics.csv
*          output/tables/v3proxy_proxy_checks.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3proxy_macros_include.do"

log using "$logdir/v3proxy_step0_preamble.log", replace

use "$datadir/v3prhdsm_analysis_ready.dta", clear
xtset grid_id year

confirm variable ln_yield ca grid_id year main_sample irr_frac
confirm variable D_full D_v3pm10 D_hepm10 D_v3pre30 D_v3he D_hema
confirm variable hdd_ge32 hdd_ge32_v3pm10 hdd_ge32_hepm10
confirm variable hdd_ge32_v3pre30 hdd_ge32_v3he hdd_ge32_hema
confirm variable HotDryPr_full HotDryPr_v3pm10 HotDryPr_hepm10
confirm variable HotDryPr_v3pre30 HotDryPr_v3he HotDryPr_hema
confirm variable SR_x_HotDryPr_full SR_x_HotDryPr_v3pm10 SR_x_HotDryPr_hepm10
confirm variable SR_x_HotDryPr_v3pre30 SR_x_HotDryPr_v3he SR_x_HotDryPr_hema

foreach v in pr_sum et0_sum gdd_10_30 ///
    pr_sum_v3pm10 et0_sum_v3pm10 gdd_10_30_v3pm10 ///
    pr_sum_hepm10 et0_sum_hepm10 gdd_10_30_hepm10 ///
    pr_sum_v3pre30 et0_sum_v3pre30 gdd_10_30_v3pre30 ///
    pr_sum_v3he et0_sum_v3he gdd_10_30_v3he ///
    pr_sum_hema et0_sum_hema gdd_10_30_hema {
    confirm variable `v'
}

foreach sm of global SM_BASES {
    foreach rw of global RAW_WINDOWS {
        local hsfx = cond("`rw'" == "full", "", "_`rw'")
        confirm variable `sm'`hsfx'
    }
}

gen v3proxy_common = (main_sample == 1) if !missing(main_sample)
replace v3proxy_common = 0 if missing(v3proxy_common)

foreach v in ln_yield ca irr_frac ///
    D_full D_v3pm10 D_hepm10 D_v3pre30 D_v3he D_hema ///
    hdd_ge32 hdd_ge32_v3pm10 hdd_ge32_hepm10 hdd_ge32_v3pre30 hdd_ge32_v3he hdd_ge32_hema ///
    pr_sum et0_sum gdd_10_30 ///
    pr_sum_v3pm10 et0_sum_v3pm10 gdd_10_30_v3pm10 ///
    pr_sum_hepm10 et0_sum_hepm10 gdd_10_30_hepm10 ///
    pr_sum_v3pre30 et0_sum_v3pre30 gdd_10_30_v3pre30 ///
    pr_sum_v3he et0_sum_v3he gdd_10_30_v3he ///
    pr_sum_hema et0_sum_hema gdd_10_30_hema {
    replace v3proxy_common = 0 if missing(`v') & v3proxy_common == 1
}

foreach sm of global SM_BASES {
    foreach rw of global RAW_WINDOWS {
        local hsfx = cond("`rw'" == "full", "", "_`rw'")
        replace v3proxy_common = 0 if missing(`sm'`hsfx') & v3proxy_common == 1
    }
}

* HotDryPr variables
foreach rw of global RAW_WINDOWS {
    replace v3proxy_common = 0 if missing(HotDryPr_`rw') & v3proxy_common == 1
    replace v3proxy_common = 0 if missing(SR_x_HotDryPr_`rw') & v3proxy_common == 1
}

label var v3proxy_common "Strict common sample for v3proxy (incl HotDryPr)"

qui count if main_sample == 1
local n_main = r(N)
qui count if v3proxy_common == 1
local n_common = r(N)

tempname pf_diag
postfile `pf_diag' str32 metric double value using ///
    "$outdir/v3proxy_sample_diagnostics.dta", replace
post `pf_diag' ("N_main_sample") (`n_main')
post `pf_diag' ("N_v3proxy_common") (`n_common')
post `pf_diag' ("share_common") (`n_common' / `n_main')
postclose `pf_diag'

tempname pf_proxy
postfile `pf_proxy' str8 source str10 layer str8 raw_window ///
    str32 sm_var str32 dry_var double N sm_mean sm_sd dry_mean dry_sd corr_sm ///
    using "$outdir/v3proxy_proxy_checks.dta", replace

foreach sm of global SM_BASES {
    local source = "era"
    local layer  = "rootzone"
    if strpos("`sm'", "gleam") > 0 local source = "gleam"
    if strpos("`sm'", "swsm")  > 0 local source = "swsm"
    if strpos("`sm'", "sms")   > 0 local layer  = "surface"
    if strpos("`sm'", "l1")    > 0 local layer  = "surface"
    if strpos("`sm'", "swvl1") > 0 local layer  = "surface"

    foreach rw of global RAW_WINDOWS {
        local hsfx = cond("`rw'" == "full", "", "_`rw'")
        local sm_var `sm'`hsfx'
        local dry_var dry_`sm'`hsfx'

        tempvar z_sm
        egen `z_sm' = std(`sm_var') if v3proxy_common == 1
        gen `dry_var' = -`z_sm' if v3proxy_common == 1
        label var `dry_var' "DrySM proxy from `sm_var'"

        qui summarize `sm_var' if v3proxy_common == 1
        local sm_mean = r(mean)
        local sm_sd   = r(sd)
        qui summarize `dry_var' if v3proxy_common == 1
        local dry_mean = r(mean)
        local dry_sd   = r(sd)
        qui correlate `dry_var' `sm_var' if v3proxy_common == 1
        local corr_sm = r(rho)
        qui count if v3proxy_common == 1 & !missing(`dry_var')
        local n_proxy = r(N)

        post `pf_proxy' ("`source'") ("`layer'") ("`rw'") ///
            ("`sm_var'") ("`dry_var'") (`n_proxy') (`sm_mean') (`sm_sd') ///
            (`dry_mean') (`dry_sd') (`corr_sm')

        drop `z_sm'
    }
}
postclose `pf_proxy'

preserve
use "$outdir/v3proxy_sample_diagnostics.dta", clear
export delimited using "$outdir/v3proxy_sample_diagnostics.csv", replace
restore

preserve
use "$outdir/v3proxy_proxy_checks.dta", clear
export delimited using "$outdir/v3proxy_proxy_checks.csv", replace
restore

compress
save "$datadir/v3proxy_analysis_ready.dta", replace

log close
di "=== v3proxy_step0_preamble.do COMPLETE ==="
