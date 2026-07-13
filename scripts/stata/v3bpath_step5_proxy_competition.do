* =============================================================================
* v3bpath_step5_proxy_competition.do
* Purpose: Compare SPEI drought vs DrySM proxy specifications across all 6
*          source-layer combinations under unified controls.
* Input:   data/processed/v3bpath_analysis_ready.dta
* Output:  output/tables/v3bpath_proxy_competition.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3bpath_macros_include.do"

log using "$logdir/v3bpath_step5_proxy_competition.log", replace

use "$datadir/v3bpath_analysis_ready.dta", clear
xtset grid_id year
keep if ${BPATH_FULL_SAMPLE} == 1

di "Working sample N = " _N

tempname pf
tempfile proxy
postfile `pf' str8 source str10 layer str12 sm_label str24 dry_var ///
    str8 control_version str80 controls ///
    double setA_d setA_d_se setA_d_p ///
    double setA_dca setA_dca_se setA_dca_p ///
    double setB_dry setB_dry_se setB_dry_p ///
    double setB_dryxca setB_dryxca_se setB_dryxca_p ///
    double setC_d setC_d_se setC_d_p ///
    double setC_dry setC_dry_se setC_dry_p ///
    double compete_d_dca compete_d_dca_se compete_d_dca_p ///
    double compete_sm_dryxca compete_sm_dryxca_se compete_sm_dryxca_p ///
    long setA_N long setB_N long setC_N long competeD_N long competeSM_N ///
    double setA_r2 double setB_r2 double setC_r2 double competeD_r2 double competeSM_r2 ///
    using `proxy', replace

local n_sm : word count $BPATH_SM_BASES

forvalues i = 1/`n_sm' {
    local sm      : word `i' of $BPATH_SM_BASES
    local source  : word `i' of $BPATH_SOURCES
    local layer   : word `i' of $BPATH_LAYERS
    local sm_lbl  : word `i' of $BPATH_SM_LABELS
    local dry_var "dry_`sm'"

    foreach cv in reduced full {
        local controls "$BPATH_CTRL_REDUCED"
        if "`cv'" == "full" local controls "$BPATH_CTRL_FULL"

        tempvar dryxca
        gen double `dryxca' = `dry_var' * ca if ${BPATH_FULL_SAMPLE} == 1

        di _n "=============================================="
        di "source=`source' | layer=`layer' | ctrl=`cv'"
        di "=============================================="

        reghdfe ln_yield D_full ca SR_x_D_full hdd_ge32 `controls', ///
            absorb(grid_id year) vce(cluster grid_id)
        local dfr_a = e(df_r)
        local setA_d_p = 2 * ttail(`dfr_a', abs(_b[D_full] / _se[D_full]))
        local setA_dca_p = 2 * ttail(`dfr_a', abs(_b[SR_x_D_full] / _se[SR_x_D_full]))
        local setA_N = e(N)
        local setA_r2 = e(r2)
        local setA_d = _b[D_full]
        local setA_d_se = _se[D_full]
        local setA_dca = _b[SR_x_D_full]
        local setA_dca_se = _se[SR_x_D_full]

        reghdfe ln_yield `dry_var' ca `dryxca' hdd_ge32 `controls', ///
            absorb(grid_id year) vce(cluster grid_id)
        local dfr_b = e(df_r)
        local setB_dry_p = 2 * ttail(`dfr_b', abs(_b[`dry_var'] / _se[`dry_var']))
        local setB_dryxca_p = 2 * ttail(`dfr_b', abs(_b[`dryxca'] / _se[`dryxca']))
        local setB_N = e(N)
        local setB_r2 = e(r2)
        local setB_dry = _b[`dry_var']
        local setB_dry_se = _se[`dry_var']
        local setB_dryxca = _b[`dryxca']
        local setB_dryxca_se = _se[`dryxca']

        reghdfe ln_yield D_full `dry_var' ca hdd_ge32 `controls', ///
            absorb(grid_id year) vce(cluster grid_id)
        local dfr_c = e(df_r)
        local setC_d_p = 2 * ttail(`dfr_c', abs(_b[D_full] / _se[D_full]))
        local setC_dry_p = 2 * ttail(`dfr_c', abs(_b[`dry_var'] / _se[`dry_var']))
        local setC_N = e(N)
        local setC_r2 = e(r2)
        local setC_d = _b[D_full]
        local setC_d_se = _se[D_full]
        local setC_dry = _b[`dry_var']
        local setC_dry_se = _se[`dry_var']

        reghdfe ln_yield D_full ca SR_x_D_full `dry_var' hdd_ge32 `controls', ///
            absorb(grid_id year) vce(cluster grid_id)
        local dfr_cd = e(df_r)
        local compete_d_dca_p = 2 * ttail(`dfr_cd', abs(_b[SR_x_D_full] / _se[SR_x_D_full]))
        local competeD_N = e(N)
        local competeD_r2 = e(r2)
        local compete_d_dca = _b[SR_x_D_full]
        local compete_d_dca_se = _se[SR_x_D_full]

        reghdfe ln_yield `dry_var' ca `dryxca' D_full hdd_ge32 `controls', ///
            absorb(grid_id year) vce(cluster grid_id)
        local dfr_cs = e(df_r)
        local compete_sm_dryxca_p = 2 * ttail(`dfr_cs', abs(_b[`dryxca'] / _se[`dryxca']))
        local competeSM_N = e(N)
        local competeSM_r2 = e(r2)
        local compete_sm_dryxca = _b[`dryxca']
        local compete_sm_dryxca_se = _se[`dryxca']

        post `pf' ("`source'") ("`layer'") ("`sm_lbl'") ("`dry_var'") ///
            ("`cv'") ("`controls'") ///
            (`setA_d') (`setA_d_se') (`setA_d_p') ///
            (`setA_dca') (`setA_dca_se') (`setA_dca_p') ///
            (`setB_dry') (`setB_dry_se') (`setB_dry_p') ///
            (`setB_dryxca') (`setB_dryxca_se') (`setB_dryxca_p') ///
            (`setC_d') (`setC_d_se') (`setC_d_p') ///
            (`setC_dry') (`setC_dry_se') (`setC_dry_p') ///
            (`compete_d_dca') (`compete_d_dca_se') (`compete_d_dca_p') ///
            (`compete_sm_dryxca') (`compete_sm_dryxca_se') (`compete_sm_dryxca_p') ///
            (`setA_N') (`setB_N') (`setC_N') (`competeD_N') (`competeSM_N') ///
            (`setA_r2') (`setB_r2') (`setC_r2') (`competeD_r2') (`competeSM_r2')

        drop `dryxca'
    }
}

postclose `pf'

preserve
use `proxy', clear
sort source layer control_version
export delimited using "$outdir/v3bpath_proxy_competition.csv", replace
restore

di "=== v3bpath_step5_proxy_competition.do COMPLETE ==="
log close
