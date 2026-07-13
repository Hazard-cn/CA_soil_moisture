* =============================================================================
* v5drymed_step2_bootstrap.do
* Purpose: Cluster bootstrap for main drought-only dry-side specifications.
* Output:  output/tables/v5drymed_bootstrap.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v5drymed_macros_include.do"

log using "$logdir/v5drymed_step2_bootstrap.log", replace

use "$v5ready_dta", clear
xtset grid_id year
xtset, clear

local reps 500
if "$V5_BOOT_REPS" != "" local reps = real("$V5_BOOT_REPS")

tempname pf
postfile `pf' str10 module str12 family str18 threshold_scheme str4 percentile ///
    str20 source_depth str12 sm_label str16 sample_tag str8 estimand ///
    str4 ca_level double(point_est bs_se ci_lo ci_hi) long(N_boot) ///
    using "$outdir/v5drymed_bootstrap_raw.dta", replace

capture program drop v5_boot_drought
program define v5_boot_drought, rclass
    args mediator

    local abs_id "grid_id"
    capture confirm variable boot_grid
    if _rc == 0 local abs_id "boot_grid"

    capture quietly reghdfe `mediator' D_full ca SR_x_D_full W_full SR_x_W_full hdd_ge32 ///
        $CTRL_full_drymed, absorb(`abs_id' year) vce(cluster `abs_id')
    if _rc != 0 {
        foreach stub in a1 a3 b idx ie25 ie50 ie75 de25 de50 de75 te25 te50 te75 {
            return scalar `stub' = .
        }
        exit
    }

    local a1 = _b[D_full]
    local a3 = _b[SR_x_D_full]

    capture quietly reghdfe ln_yield D_full ca SR_x_D_full `mediator' W_full SR_x_W_full hdd_ge32 ///
        $CTRL_full_drymed, absorb(`abs_id' year) vce(cluster `abs_id')
    if _rc != 0 {
        foreach stub in b idx ie25 ie50 ie75 de25 de50 de75 te25 te50 te75 {
            return scalar `stub' = .
        }
        return scalar a1 = `a1'
        return scalar a3 = `a3'
        exit
    }

    local b_m = _b[`mediator']
    local c1 = _b[D_full]
    local c3 = _b[SR_x_D_full]

    return scalar a1 = `a1'
    return scalar a3 = `a3'
    return scalar b = `b_m'
    return scalar idx = `a3' * `b_m'

    local r25 = $V5_CA_P25
    local r50 = $V5_CA_P50
    local r75 = $V5_CA_P75

    return scalar ie25 = (`a1' + `a3' * `r25') * `b_m'
    return scalar ie50 = (`a1' + `a3' * `r50') * `b_m'
    return scalar ie75 = (`a1' + `a3' * `r75') * `b_m'
    return scalar de25 = `c1' + `c3' * `r25'
    return scalar de50 = `c1' + `c3' * `r50'
    return scalar de75 = `c1' + `c3' * `r75'
    return scalar te25 = `c1' + `c3' * `r25' + (`a1' + `a3' * `r25') * `b_m'
    return scalar te50 = `c1' + `c3' * `r50' + (`a1' + `a3' * `r50') * `b_m'
    return scalar te75 = `c1' + `c3' * `r75' + (`a1' + `a3' * `r75') * `b_m'
end

local n_tags : word count $V5_MAIN_TAGS
forvalues t = 1/`n_tags' {
    local tag : word `t' of $V5_MAIN_TAGS
    local family_code : word `t' of $V5_MAIN_FAMILIES
    local scheme_code : word `t' of $V5_MAIN_SCHEMES
    local pct : word `t' of $V5_MAIN_PCTS
    local sample_var "v5s_`tag'"

    local family "dryshare"
    if "`family_code'" == "ddf" local family "drydeficit"

    local threshold_scheme "pooled_state"
    if "`scheme_code'" == "mz" local threshold_scheme "maize_zone_state"

    preserve
    keep if `sample_var' == 1
    _pctile ca, p(25 50 75)
    global V5_CA_P25 = r(r1)
    global V5_CA_P50 = r(r2)
    global V5_CA_P75 = r(r3)
    restore

    forvalues i = 1/6 {
        local prefix : word `i' of $DRY_PREFIXES
        local source_depth : word `i' of $DRY_SOURCE_DEPTHS
        local sm_label : word `i' of $DRY_SM_LABELS
        local mediator "v5`tag'_`prefix'"

        di _n "Bootstrap `tag' / `sm_label' / reps=`reps'"

        preserve
        keep if `sample_var' == 1

        bootstrap ///
            a1=r(a1) a3=r(a3) b=r(b) idx=r(idx) ///
            ie25=r(ie25) ie50=r(ie50) ie75=r(ie75) ///
            de25=r(de25) de50=r(de50) de75=r(de75) ///
            te25=r(te25) te50=r(te50) te75=r(te75), ///
            reps(`reps') cluster(grid_id) idcluster(boot_grid) ///
            seed(`=4200 + `t' * 10 + `i'') nodots: ///
            v5_boot_drought `mediator'

        estat bootstrap, bc
        matrix bcCI = r(ci_bc)
        matrix pe = e(b)
        matrix vv = e(V)

        local stat_names "a1 a3 b idx ie25 ie50 ie75 de25 de50 de75 te25 te50 te75"
        local j = 0
        foreach sname of local stat_names {
            local ++j
            local point = pe[1, `j']
            local bs_se = sqrt(vv[`j', `j'])
            scalar __ll = .
            scalar __ul = .
            capture scalar __ll = bcCI[`j', 1]
            capture scalar __ul = bcCI[`j', 2]
            local ll = scalar(__ll)
            local ul = scalar(__ul)
            if missing(`ll') | missing(`ul') {
                local ll = `point' - 1.96 * `bs_se'
                local ul = `point' + 1.96 * `bs_se'
            }
            local ca_level "all"
            if inlist("`sname'", "ie25", "de25", "te25") local ca_level "P25"
            if inlist("`sname'", "ie50", "de50", "te50") local ca_level "P50"
            if inlist("`sname'", "ie75", "de75", "te75") local ca_level "P75"
            post `pf' ("drought") ("`family'") ("`threshold_scheme'") ("`pct'") ///
                ("`source_depth'") ("`sm_label'") ("`tag'") ("`sname'") ///
                ("`ca_level'") (`point') (`bs_se') (`ll') (`ul') (`reps')
        }

        restore
    }
}

postclose `pf'

preserve
use "$outdir/v5drymed_bootstrap_raw.dta", clear
export delimited using "$v5boot_csv", replace
restore

cap erase "$outdir/v5drymed_bootstrap_raw.dta"

log close
di "=== v5drymed_step2_bootstrap.do COMPLETE ==="
