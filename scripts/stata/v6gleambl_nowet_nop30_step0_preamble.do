* =============================================================================
* v6gleambl_nowet_nop30_step0_preamble.do
* Purpose: Build analysis-ready data without paired M_wet/W_w controls and
*          excluding v3pre30.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v6gleambl_nowet_nop30_macros_include.do"

log using "$logdir/v6gleambl_nowet_nop30_step0_preamble.log", replace

use "$datadir/v3_analysis_ready.dta", clear
xtset grid_id year

merge 1:1 grid_id year using "$datadir/v3sub_analysis_ready.dta", ///
    keepusing(maize_zone irr_group) keep(master match)
tab _merge
assert _merge == 3
drop _merge

local build_keep "gdd_10_30"
forvalues m = 1/4 {
    local dry_stub : word `m' of $V6_DRY_STUBS
    foreach src of global V6_SOURCE_CODES {
        foreach dp of global V6_DRY_PCTS {
            foreach wc of global V6_WINDOW_CODES {
                local build_keep "`build_keep' `dry_stub'_`src'_`dp'_`wc'"
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
confirm variable D_full D_v3he D_hema
confirm variable SR_x_D_full SR_x_D_v3he SR_x_D_hema
confirm variable hdd_ge32 pr_sum et0_sum gdd_10_30 irr_frac aridity
confirm variable maize_zone irr_group

tempname pf
tempfile diag
postfile `pf' str48 item str120 value using `diag', replace

quietly count if main_sample == 1
post `pf' ("N_main_sample") ("`r(N)'")
post `pf' ("windows_included") ("v3he hema fullnew")
post `pf' ("map_D_v3he") ("D_v3he = max(0,-spei2_mean_v3he)")
post `pf' ("map_D_hema") ("D_hema = max(0,-spei2_mean_hema)")
post `pf' ("map_D_fullnew") ("D_full")
post `pf' ("control_Ww") ("excluded")
post `pf' ("control_Mwet") ("excluded")
post `pf' ("map_H_all_windows") ("hdd_ge32")

forvalues m = 1/3 {
    local mcode : word `m' of $V6_MD_METRIC_CODES

    forvalues w = 1/3 {
        local wlbl : word `w' of $V6_WINDOWS
        local wc : word `w' of $V6_WINDOW_CODES
        local tag "`mcode'_`wc'"

        gen byte v6x_`tag' = (main_sample == 1) if !missing(main_sample)
        replace v6x_`tag' = 0 if missing(v6x_`tag')

        local d_var "D_v3he"
        local srd_var "SR_x_D_v3he"
        if "`wlbl'" == "hema" {
            local d_var "D_hema"
            local srd_var "SR_x_D_hema"
        }
        if "`wlbl'" == "fullnew" {
            local d_var "D_full"
            local srd_var "SR_x_D_full"
        }

        foreach v in ln_yield ca `d_var' `srd_var' $V6_CTRL_FULL maize_zone irr_group {
            replace v6x_`tag' = 0 if missing(`v') & v6x_`tag' == 1
        }

        forvalues s = 1/2 {
            local src : word `s' of $V6_SOURCE_CODES
            local dry_stub : word `m' of $V6_MD_DRY_STUBS
            local vdry "`dry_stub'_`src'_`wc'"
            confirm variable `vdry'
            gen double v6x`tag'_`src' = `vdry'
            label var v6x`tag'_`src' "v6 nowet nop30 dry mediator `tag' / `src'"
            replace v6x_`tag' = 0 if missing(v6x`tag'_`src') & v6x_`tag' == 1
        }

        quietly count if v6x_`tag' == 1
        post `pf' ("N_v6x_`tag'") ("`r(N)'")
    }
}

forvalues m = 1/4 {
    local mcode : word `m' of $V6_METRIC_CODES

    forvalues p = 1/2 {
        local dp : word `p' of $V6_DRY_PCTS

        forvalues w = 1/3 {
            local wlbl : word `w' of $V6_WINDOWS
            local wc : word `w' of $V6_WINDOW_CODES
            local tag "`mcode'_`dp'_`wc'"

            gen byte v6x_`tag' = (main_sample == 1) if !missing(main_sample)
            replace v6x_`tag' = 0 if missing(v6x_`tag')

            local d_var "D_v3he"
            local srd_var "SR_x_D_v3he"
            if "`wlbl'" == "hema" {
                local d_var "D_hema"
                local srd_var "SR_x_D_hema"
            }
            if "`wlbl'" == "fullnew" {
                local d_var "D_full"
                local srd_var "SR_x_D_full"
            }

            foreach v in ln_yield ca `d_var' `srd_var' $V6_CTRL_FULL maize_zone irr_group {
                replace v6x_`tag' = 0 if missing(`v') & v6x_`tag' == 1
            }

            forvalues s = 1/2 {
                local src : word `s' of $V6_SOURCE_CODES
                local dry_stub : word `m' of $V6_DRY_STUBS
                local vdry "`dry_stub'_`src'_`dp'_`wc'"
                confirm variable `vdry'
                gen double v6x`tag'_`src' = `vdry'
                label var v6x`tag'_`src' "v6 nowet nop30 dry mediator `tag' / `src'"
                replace v6x_`tag' = 0 if missing(v6x`tag'_`src') & v6x_`tag' == 1
            }

            quietly count if v6x_`tag' == 1
            post `pf' ("N_v6x_`tag'") ("`r(N)'")
        }
    }
}

postclose `pf'

preserve
use `diag', clear
export delimited using "$v6xdiag_csv", replace
restore

compress
save "$v6xready_dta", replace

log close
di "=== v6gleambl_nowet_nop30_step0_preamble.do COMPLETE ==="
