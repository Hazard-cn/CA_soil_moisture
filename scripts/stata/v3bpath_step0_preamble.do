* =============================================================================
* v3bpath_step0_preamble.do
* Purpose: Prepare unified analysis-ready data, common samples, SMdef, and
*          DrySM proxies for the v3bpath unified audit line.
* Input:   data/processed/v3prhdsm_analysis_ready.dta
*          data/processed/v3_analysis_ready.dta
* Output:  data/processed/v3bpath_analysis_ready.dta
*          output/tables/v3bpath_diagnostics.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3bpath_macros_include.do"

log using "$logdir/v3bpath_step0_preamble.log", replace

use "$datadir/v3prhdsm_analysis_ready.dta", clear
xtset grid_id year

merge 1:1 grid_id year using "$datadir/v3_analysis_ready.dta", ///
    keepusing(W_full W_v3pre30 W_v3pm10 W_v3he W_hepm10 W_hema) ///
    keep(master match)
tab _merge
assert _merge == 3
drop _merge

confirm variable ln_yield ca main_sample grid_id year irr_frac prov_code
confirm variable D_full SR_x_D_full hdd_ge32 gdd_10_30 W_full pr_sum et0_sum aridity
confirm variable SR_x_Heat_full

foreach w of global BPATH_WINDOWS {
    local hsfx "_`w'"
    if "`w'" == "full" local hsfx ""
    local d_var  "D_`w'"
    local dca_var "SR_x_D_`w'"
    local w_var "W_`w'"
    if "`w'" == "full" {
        local d_var "D_full"
        local dca_var "SR_x_D_full"
        local w_var "W_full"
    }
    local h_var  "hdd_ge32`hsfx'"
    local gdd_var "gdd_10_30`hsfx'"

    confirm variable `d_var'
    confirm variable `dca_var'
    confirm variable `h_var'
    confirm variable `gdd_var'
    confirm variable `w_var'
}

cap confirm variable prov_year
if _rc != 0 {
    egen prov_year = group(prov_code year)
    label var prov_year "Province x Year FE"
}

gen byte ${BPATH_FULL_SAMPLE} = (main_sample == 1) if !missing(main_sample)
replace ${BPATH_FULL_SAMPLE} = 0 if missing(${BPATH_FULL_SAMPLE})

foreach v in ln_yield ca D_full SR_x_D_full hdd_ge32 gdd_10_30 W_full ///
    irr_frac pr_sum et0_sum aridity {
    replace ${BPATH_FULL_SAMPLE} = 0 if missing(`v') & ${BPATH_FULL_SAMPLE} == 1
}

foreach sm of global BPATH_SM_BASES {
    confirm variable `sm'
    replace ${BPATH_FULL_SAMPLE} = 0 if missing(`sm') & ${BPATH_FULL_SAMPLE} == 1
}

gen byte ${BPATH_STAGE_SAMPLE} = (main_sample == 1) if !missing(main_sample)
replace ${BPATH_STAGE_SAMPLE} = 0 if missing(${BPATH_STAGE_SAMPLE})

foreach v in ln_yield ca irr_frac {
    replace ${BPATH_STAGE_SAMPLE} = 0 if missing(`v') & ${BPATH_STAGE_SAMPLE} == 1
}

foreach w of global BPATH_WINDOWS {
    local hsfx "_`w'"
    if "`w'" == "full" local hsfx ""
    local d_var  "D_`w'"
    local dca_var "SR_x_D_`w'"
    local w_var "W_`w'"
    if "`w'" == "full" {
        local d_var "D_full"
        local dca_var "SR_x_D_full"
        local w_var "W_full"
    }
    local h_var  "hdd_ge32`hsfx'"
    local gdd_var "gdd_10_30`hsfx'"

    foreach v in `d_var' `dca_var' `h_var' `gdd_var' `w_var' {
        replace ${BPATH_STAGE_SAMPLE} = 0 if missing(`v') & ${BPATH_STAGE_SAMPLE} == 1
    }

    foreach sm of global BPATH_SM_BASES {
        local sm_var "`sm'`hsfx'"
        confirm variable `sm_var'
        replace ${BPATH_STAGE_SAMPLE} = 0 if missing(`sm_var') & ${BPATH_STAGE_SAMPLE} == 1
    }
}

label var ${BPATH_FULL_SAMPLE}  "v3bpath full-season common sample across 6 SM sources"
label var ${BPATH_STAGE_SAMPLE} "v3bpath stage-window common sample across 6 SM sources and 6 windows"

foreach sm of global BPATH_SM_BASES {
    bysort grid_id: egen mean_`sm' = mean(cond(${BPATH_FULL_SAMPLE} == 1, `sm', .))
    gen double SMdef_`sm' = max(0, mean_`sm' - `sm') if ${BPATH_FULL_SAMPLE} == 1
    label var mean_`sm' "Grid mean of `sm' on bpath full-season common sample"
    label var SMdef_`sm' "One-sided soil moisture deficit from `sm'"
}

foreach sm of global BPATH_SM_BASES {
    foreach w of global BPATH_WINDOWS {
        local hsfx "_`w'"
        if "`w'" == "full" local hsfx ""
        local sm_var "`sm'`hsfx'"
        local sample_var "${BPATH_STAGE_SAMPLE}"
        if "`w'" == "full" local sample_var "${BPATH_FULL_SAMPLE}"
        tempvar z_sm
        egen `z_sm' = std(`sm_var') if `sample_var' == 1
        gen double dry_`sm_var' = -`z_sm' if `sample_var' == 1
        label var dry_`sm_var' "DrySM proxy from `sm_var'"
        drop `z_sm'
    }
}

tempname pf
tempfile diag
postfile `pf' str80 item double value using `diag', replace

quietly count if main_sample == 1
local n_main = r(N)
quietly count if ${BPATH_FULL_SAMPLE} == 1
local n_full = r(N)
quietly count if ${BPATH_STAGE_SAMPLE} == 1
local n_stage = r(N)

post `pf' ("N_main_sample") (`n_main')
post `pf' ("N_bpath_full6_sample") (`n_full')
post `pf' ("N_bpath_stage6_sample") (`n_stage')
post `pf' ("share_bpath_full6_sample") (`n_full' / `n_main')
post `pf' ("share_bpath_stage6_sample") (`n_stage' / `n_main')

foreach sm of global BPATH_SM_BASES {
    quietly count if ${BPATH_FULL_SAMPLE} == 1 & SMdef_`sm' > 0
    post `pf' ("N_smdef_positive_`sm'") (r(N))

    quietly summarize SMdef_`sm' if ${BPATH_FULL_SAMPLE} == 1
    post `pf' ("mean_smdef_`sm'") (r(mean))
    post `pf' ("sd_smdef_`sm'")   (r(sd))
}

postclose `pf'

preserve
use `diag', clear
export delimited using "$outdir/v3bpath_diagnostics.csv", replace
restore

compress
save "$datadir/v3bpath_analysis_ready.dta", replace

di "main_sample N       = " `n_main'
di "bpath_full6_sample  = " `n_full'
di "bpath_stage6_sample = " `n_stage'
di "=== v3bpath_step0_preamble.do COMPLETE ==="
log close
