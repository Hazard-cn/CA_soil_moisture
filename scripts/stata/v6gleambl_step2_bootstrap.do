* =============================================================================
* v6gleambl_step2_bootstrap.do
* Purpose: Simple cluster bootstrap for IE/DE/TE on four-window GLEAM specs.
* Output:  temp/2026-04-23_newSMsplit/v6gleambl_bootstrap_iede_te.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
if "$V6_MACROS_INCLUDE" == "" {
    global V6_MACROS_INCLUDE "$projdir/scripts/stata/v6gleambl_macros_include.do"
}
do "$V6_MACROS_INCLUDE"

log using "$logdir/v6gleambl_step2_bootstrap.log", replace

use "$v6ready_dta", clear
xtset grid_id year
xtset, clear

local reps 500
if "$V6_BOOT_REPS" != "" local reps = real("$V6_BOOT_REPS")

tempname pf
postfile `pf' str12 module str12 window str20 metric_family str4 dry_pct ///
    str4 wet_pct str16 source_layer str12 sm_label str20 sample_tag ///
    str2 effect str4 ca_level double(ca_value point_est bs_se ci_lo ci_hi) ///
    long(N_boot) using "$outdir/v6gleambl_boot_raw.dta", replace

capture program drop v6_boot_model8
program define v6_boot_model8, rclass
    args d_var srd_var w_var mediator wetmed

    local abs_id "grid_id"
    capture confirm variable boot_grid
    if _rc == 0 local abs_id "boot_grid"

    capture quietly reghdfe `mediator' `d_var' ca `srd_var' `wetmed' `w_var' ///
        $V6_CTRL_FULL, absorb(`abs_id' year) vce(cluster `abs_id')
    if _rc != 0 {
        foreach stub in ie25 ie50 ie75 de25 de50 de75 te25 te50 te75 {
            return scalar `stub' = .
        }
        exit
    }

    local a1 = _b[`d_var']
    local a3 = _b[`srd_var']

    capture quietly reghdfe ln_yield `d_var' ca `srd_var' `mediator' `wetmed' `w_var' ///
        $V6_CTRL_FULL, absorb(`abs_id' year) vce(cluster `abs_id')
    if _rc != 0 {
        foreach stub in ie25 ie50 ie75 de25 de50 de75 te25 te50 te75 {
            return scalar `stub' = .
        }
        exit
    }

    local b_m = _b[`mediator']
    local c1 = _b[`d_var']
    local c3 = _b[`srd_var']

    local r25 = $V6_CA_P25
    local r50 = $V6_CA_P50
    local r75 = $V6_CA_P75

    local ie25 = (`a1' + `a3' * `r25') * `b_m'
    local ie50 = (`a1' + `a3' * `r50') * `b_m'
    local ie75 = (`a1' + `a3' * `r75') * `b_m'
    local de25 = `c1' + `c3' * `r25'
    local de50 = `c1' + `c3' * `r50'
    local de75 = `c1' + `c3' * `r75'

    return scalar ie25 = `ie25'
    return scalar ie50 = `ie50'
    return scalar ie75 = `ie75'
    return scalar de25 = `de25'
    return scalar de50 = `de50'
    return scalar de75 = `de75'
    return scalar te25 = `ie25' + `de25'
    return scalar te50 = `ie50' + `de50'
    return scalar te75 = `ie75' + `de75'
end

forvalues m = 1/4 {
    local mcode : word `m' of $V6_METRIC_CODES
    local family : word `m' of $V6_METRIC_FAMILIES

    forvalues p = 1/2 {
        local dp : word `p' of $V6_DRY_PCTS
        local wp : word `p' of $V6_WET_PCTS

        forvalues w = 1/4 {
            local wlbl : word `w' of $V6_WINDOWS
            local wc : word `w' of $V6_WINDOW_CODES
            local tag "`mcode'_`dp'_`wc'"
            local sample_var "v6s_`tag'"

            local d_var "D_v3pre30"
            local w_var "W_v3pre30"
            local srd_var "SR_x_D_v3pre30"
            if "`wlbl'" == "v3he" {
                local d_var "D_v3he"
                local w_var "W_v3he"
                local srd_var "SR_x_D_v3he"
            }
            if "`wlbl'" == "hema" {
                local d_var "D_hema"
                local w_var "W_hema"
                local srd_var "SR_x_D_hema"
            }
            if "`wlbl'" == "fullnew" {
                local d_var "D_full"
                local w_var "W_full"
                local srd_var "SR_x_D_full"
            }

            preserve
            keep if `sample_var' == 1
            quietly count
            if r(N) == 0 {
                restore
                continue
            }

            _pctile ca, p(25 50 75)
            global V6_CA_P25 = r(r1)
            global V6_CA_P50 = r(r2)
            global V6_CA_P75 = r(r3)

            forvalues s = 1/2 {
                local src : word `s' of $V6_SOURCE_CODES
                local src_layer : word `s' of $V6_SOURCE_LAYERS
                local sm_label : word `s' of $V6_SOURCE_LABELS
                local mediator "v6`tag'_`src'"
                local wetmed "v6w_`tag'_`src'"

                di _n "Bootstrap `tag' / `src' / reps = `reps'"

                bootstrap ///
                    ie25=r(ie25) ie50=r(ie50) ie75=r(ie75) ///
                    de25=r(de25) de50=r(de50) de75=r(de75) ///
                    te25=r(te25) te50=r(te50) te75=r(te75), ///
                    reps(`reps') cluster(grid_id) idcluster(boot_grid) ///
                    seed(`=6200 + `m' * 100 + `p' * 20 + `w' * 5 + `s'') nodots: ///
                    v6_boot_model8 `d_var' `srd_var' `w_var' `mediator' `wetmed'

                estat bootstrap, bc
                matrix bcCI = r(ci_bc)
                matrix pe = e(b)
                matrix vv = e(V)

                local stat_names "ie25 ie50 ie75 de25 de50 de75 te25 te50 te75"
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
                    local effect = upper(substr("`sname'", 1, 2))
                    local ca_level "P25"
                    local ca_value = $V6_CA_P25
                    if inlist("`sname'", "ie50", "de50", "te50") {
                        local ca_level "P50"
                        local ca_value = $V6_CA_P50
                    }
                    if inlist("`sname'", "ie75", "de75", "te75") {
                        local ca_level "P75"
                        local ca_value = $V6_CA_P75
                    }
                    post `pf' ("drought") ("`wlbl'") ("`family'") ("`dp'") ///
                        ("`wp'") ("`src_layer'") ("`sm_label'") ("`tag'") ///
                        ("`effect'") ("`ca_level'") (`ca_value') ///
                        (`point') (`bs_se') (`ll') (`ul') (`reps')
                }
            }

            restore
        }
    }
}

postclose `pf'

preserve
use "$outdir/v6gleambl_boot_raw.dta", clear
export delimited using "$v6boot_csv", replace
restore

cap erase "$outdir/v6gleambl_boot_raw.dta"

log close
di "=== v6gleambl_step2_bootstrap.do COMPLETE ==="
