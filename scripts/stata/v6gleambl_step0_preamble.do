* =============================================================================
* v6gleambl_step0_preamble.do
* Purpose: Build analysis-ready data for four-window GLEAM baseline-local
*          Model 8 rerun with dry/wet paired mediators.
* Output:  temp/2026-04-23_newSMsplit/v6gleambl_analysis_ready.dta
*          temp/2026-04-23_newSMsplit/v6gleambl_diagnostics.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
if "$V6_MACROS_INCLUDE" == "" {
    global V6_MACROS_INCLUDE "$projdir/scripts/stata/v6gleambl_macros_include.do"
}
do "$V6_MACROS_INCLUDE"

log using "$logdir/v6gleambl_step0_preamble.log", replace

use "$v6base_dta", clear
xtset grid_id year

merge 1:1 grid_id year using "$datadir/v3sub_analysis_ready.dta", ///
    keepusing(maize_zone irr_group) keep(master match)
tab _merge
assert _merge == 3
drop _merge

local build_keep "gdd_10_30"
forvalues m = 1/4 {
    local dry_stub : word `m' of $V6_DRY_STUBS
    local wet_stub : word `m' of $V6_WET_STUBS
    foreach src of global V6_SOURCE_CODES {
        foreach dp of global V6_DRY_PCTS {
            local wp "p90"
            if "`dp'" == "p20" local wp "p80"
            foreach wc of global V6_WINDOW_CODES {
                local build_keep "`build_keep' `dry_stub'_`src'_`dp'_`wc'"
                local build_keep "`build_keep' `wet_stub'_`src'_`wp'_`wc'"
            }
        }
    }
}

merge 1:1 grid_id year using "$builddir/data_v3_main.dta", ///
    keepusing(`build_keep') keep(master match)
tab _merge
assert _merge == 3
drop _merge

merge 1:1 grid_id year using "$v6mdsidecar", keep(master match)
tab _merge
assert _merge == 3
drop _merge

confirm variable ln_yield ca main_sample grid_id year
confirm variable D_full D_v3pre30 D_v3he D_hema
confirm variable W_full W_v3pre30 W_v3he W_hema
confirm variable SR_x_D_full SR_x_D_v3pre30 SR_x_D_v3he SR_x_D_hema
confirm variable hdd_ge32 pr_sum et0_sum gdd_10_30 irr_frac aridity
confirm variable maize_zone irr_group

tempname pf
tempfile diag
postfile `pf' str48 item str120 value using `diag', replace

quietly count if main_sample == 1
post `pf' ("N_main_sample") ("`r(N)'")

post `pf' ("map_D_v3pre30") ("D_v3pre30 = max(0,-spei1_mean_v3pre30)")
post `pf' ("map_D_v3he") ("D_v3he = max(0,-spei2_mean_v3he)")
post `pf' ("map_D_hema") ("D_hema = max(0,-spei2_mean_hema)")
post `pf' ("map_D_fullnew") ("D_full")
post `pf' ("map_W_v3pre30") ("W_v3pre30 = max(0,spei1_mean_v3pre30)")
post `pf' ("map_W_v3he") ("W_v3he = max(0,spei2_mean_v3he)")
post `pf' ("map_W_hema") ("W_hema = max(0,spei2_mean_hema)")
post `pf' ("map_W_fullnew") ("W_full")
post `pf' ("map_H_all_windows") ("hdd_ge32")

forvalues m = 1/3 {
    local mcode : word `m' of $V6_MD_METRIC_CODES
    local family : word `m' of $V6_MD_METRIC_FAMILIES

    forvalues w = 1/4 {
        local wlbl : word `w' of $V6_WINDOWS
        local wc : word `w' of $V6_WINDOW_CODES
        local tag "`mcode'_`wc'"

        gen byte v6s_`tag' = (main_sample == 1) if !missing(main_sample)
        replace v6s_`tag' = 0 if missing(v6s_`tag')

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

        foreach v in ln_yield ca `d_var' `w_var' `srd_var' $V6_CTRL_FULL ///
            maize_zone irr_group {
            replace v6s_`tag' = 0 if missing(`v') & v6s_`tag' == 1
        }

        forvalues s = 1/2 {
            local src : word `s' of $V6_SOURCE_CODES
            local dry_stub : word `m' of $V6_MD_DRY_STUBS
            local wet_stub : word `m' of $V6_MD_WET_STUBS
            local vdry "`dry_stub'_`src'_`wc'"
            local vwet "`wet_stub'_`src'_`wc'"

            confirm variable `vdry'
            confirm variable `vwet'

            gen double v6`tag'_`src' = `vdry'
            gen double v6w_`tag'_`src' = `vwet'
            label var v6`tag'_`src' "v6 dry mediator `tag' / `src'"
            label var v6w_`tag'_`src' "v6 wet control mediator `tag' / `src'"

            replace v6s_`tag' = 0 if missing(v6`tag'_`src') & v6s_`tag' == 1
            replace v6s_`tag' = 0 if missing(v6w_`tag'_`src') & v6s_`tag' == 1
        }

        quietly count if v6s_`tag' == 1
        post `pf' ("N_v6s_`tag'") ("`r(N)'")
    }
}

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

            gen byte v6s_`tag' = (main_sample == 1) if !missing(main_sample)
            replace v6s_`tag' = 0 if missing(v6s_`tag')

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

            foreach v in ln_yield ca `d_var' `w_var' `srd_var' $V6_CTRL_FULL ///
                maize_zone irr_group {
                replace v6s_`tag' = 0 if missing(`v') & v6s_`tag' == 1
            }

            forvalues s = 1/2 {
                local src : word `s' of $V6_SOURCE_CODES
                local dry_stub : word `m' of $V6_DRY_STUBS
                local wet_stub : word `m' of $V6_WET_STUBS
                local vdry "`dry_stub'_`src'_`dp'_`wc'"
                local vwet "`wet_stub'_`src'_`wp'_`wc'"

                confirm variable `vdry'
                confirm variable `vwet'

                gen double v6`tag'_`src' = `vdry'
                gen double v6w_`tag'_`src' = `vwet'
                label var v6`tag'_`src' "v6 dry mediator `tag' / `src'"
                label var v6w_`tag'_`src' "v6 wet control mediator `tag' / `src'"

                replace v6s_`tag' = 0 if missing(v6`tag'_`src') & v6s_`tag' == 1
                replace v6s_`tag' = 0 if missing(v6w_`tag'_`src') & v6s_`tag' == 1
            }

            quietly count if v6s_`tag' == 1
            post `pf' ("N_v6s_`tag'") ("`r(N)'")
        }
    }
}

postclose `pf'

preserve
use `diag', clear
export delimited using "$v6diag_csv", replace
restore

compress
save "$v6ready_dta", replace

log close
di "=== v6gleambl_step0_preamble.do COMPLETE ==="
