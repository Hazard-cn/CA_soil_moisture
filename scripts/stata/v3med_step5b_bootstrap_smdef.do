* =============================================================================
* v3med_step5b_bootstrap_smdef.do
* Purpose: Cluster bootstrap (500 reps) for Model 8 drought module using
*          SMdef as mediator. 2 primary SM sources: GLEAM-Sfc and GLEAM-Root.
*          Provides honest CIs for IE, DE, TE, Index under the Path-A repair.
*
*          Key context: Path A does NOT rescue the mediation framework
*          (b on SMdef > 0 is mathematically equivalent to b on raw SM < 0).
*          This bootstrap produces CIs so the report can formally acknowledge
*          the failure rather than assert a substantively meaningful mediation.
*
* Author:  YangSu + Claude
* Date:    2026-04-16
* Input:   data/processed/v3med_analysis_ready_plus.dta
* Output:  output/tables/v3med_smdef_bootstrap.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3med_macros_include.do"

log using "$logdir/v3med_step5b_bootstrap_smdef.log", replace

use "$datadir/v3med_analysis_ready_plus.dta", clear
keep if v3med_common == 1
xtset, clear

_pctile ca, p(25 50 75)
global BOOT_CA_P25 = r(r1)
global BOOT_CA_P50 = r(r2)
global BOOT_CA_P75 = r(r3)
di "ca P25=" $BOOT_CA_P25 " P50=" $BOOT_CA_P50 " P75=" $BOOT_CA_P75

tempfile boot_data
save `boot_data', replace
global BOOT_DATA "`boot_data'"

local reps 500

* =============================================================================
* PROGRAM: Drought Model 8 with SMdef
* =============================================================================
capture program drop boot_smdef_drought
program define boot_smdef_drought, rclass
    args sm_var

    use "$BOOT_DATA", clear
    bsample, cluster(grid_id) idcluster(boot_grid)

    capture quietly reghdfe SMdef_`sm_var' D_full ca SR_x_D_full hdd_ge32 ///
        irr_frac gdd_ge10, absorb(boot_grid year) vce(cluster boot_grid)
    if _rc != 0 {
        return scalar a1 = .
        return scalar a3 = .
        return scalar b  = .
        return scalar idx= .
        return scalar ie25 = .
        return scalar ie50 = .
        return scalar ie75 = .
        return scalar de25 = .
        return scalar de50 = .
        return scalar de75 = .
        return scalar te25 = .
        return scalar te50 = .
        return scalar te75 = .
        exit
    }
    local a1 = _b[D_full]
    local a3 = _b[SR_x_D_full]

    capture quietly reghdfe ln_yield D_full ca SR_x_D_full SMdef_`sm_var' hdd_ge32 ///
        irr_frac gdd_ge10, absorb(boot_grid year) vce(cluster boot_grid)
    if _rc != 0 {
        return scalar a1 = `a1'
        return scalar a3 = `a3'
        return scalar b  = .
        return scalar idx= .
        return scalar ie25 = .
        return scalar ie50 = .
        return scalar ie75 = .
        return scalar de25 = .
        return scalar de50 = .
        return scalar de75 = .
        return scalar te25 = .
        return scalar te50 = .
        return scalar te75 = .
        exit
    }

    local bsm = _b[SMdef_`sm_var']
    local c1 = _b[D_full]
    local c3 = _b[SR_x_D_full]

    return scalar a1 = `a1'
    return scalar a3 = `a3'
    return scalar b  = `bsm'
    return scalar idx = `a3' * `bsm'

    local r25 = $BOOT_CA_P25
    local r50 = $BOOT_CA_P50
    local r75 = $BOOT_CA_P75

    return scalar ie25 = (`a1' + `a3'*`r25') * `bsm'
    return scalar ie50 = (`a1' + `a3'*`r50') * `bsm'
    return scalar ie75 = (`a1' + `a3'*`r75') * `bsm'
    return scalar de25 = `c1' + `c3'*`r25'
    return scalar de50 = `c1' + `c3'*`r50'
    return scalar de75 = `c1' + `c3'*`r75'
    return scalar te25 = `c1' + `c3'*`r25' + (`a1' + `a3'*`r25') * `bsm'
    return scalar te50 = `c1' + `c3'*`r50' + (`a1' + `a3'*`r50') * `bsm'
    return scalar te75 = `c1' + `c3'*`r75' + (`a1' + `a3'*`r75') * `bsm'
end

* =============================================================================
* RUN BOOTSTRAP: 2 sources
* =============================================================================
tempname pf
postfile `pf' str20 source str10 estimand double(point ll95 ul95) ///
    using "$outdir/v3med_smdef_bootstrap_raw.dta", replace

foreach src in gleam_sms_mean gleam_smrz_mean {
    di _n "=============================================="
    di "Bootstrap SMdef drought: `src' (500 reps)"
    di "=============================================="

    use "$BOOT_DATA", clear

    bootstrap ///
        a1=r(a1) a3=r(a3) b=r(b) idx=r(idx) ///
        ie25=r(ie25) ie50=r(ie50) ie75=r(ie75) ///
        de25=r(de25) de50=r(de50) de75=r(de75) ///
        te25=r(te25) te50=r(te50) te75=r(te75), ///
        reps(`reps') cluster(grid_id) seed(42) nodots: ///
        boot_smdef_drought `src'

    estat bootstrap, bc
    mat bcCI = r(ci_bc)

    mat pe = e(b)
    local stubs "a1 a3 b idx ie25 ie50 ie75 de25 de50 de75 te25 te50 te75"
    local i = 0
    foreach stub of local stubs {
        local ++i
        local pe_val = pe[1, `i']
        local ll = bcCI[1, `i']
        local ul = bcCI[2, `i']
        post `pf' ("`src'") ("`stub'") (`pe_val') (`ll') (`ul')
    }
}

postclose `pf'

preserve
use "$outdir/v3med_smdef_bootstrap_raw.dta", clear
export delimited using "$outdir/v3med_smdef_bootstrap.csv", replace
list source estimand point ll95 ul95, sepby(source) noobs
restore
cap erase "$outdir/v3med_smdef_bootstrap_raw.dta"

log close
di "=== v3med_step5b_bootstrap_smdef.do COMPLETE ==="
