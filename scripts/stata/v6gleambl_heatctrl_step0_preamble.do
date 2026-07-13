* =============================================================================
* v6gleambl_heatctrl_step0_preamble.do
* Purpose: Build analysis-ready data for four-window GLEAM heat-main baseline.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
if "$V6H_MACROS_INCLUDE" == "" {
    global V6H_MACROS_INCLUDE "$projdir/scripts/stata/v6gleambl_heatctrl_macros_include.do"
}
do "$V6H_MACROS_INCLUDE"

log using "$logdir/v6gleambl_heatctrl_step0_preamble.log", replace

use "$v6hbase_dta", clear
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
confirm variable D_full D_v3pre30 D_v3he D_hema
confirm variable W_full W_v3pre30 W_v3he W_hema
confirm variable SR_x_Heat_full hdd_ge32 pr_sum et0_sum gdd_10_30 irr_frac aridity
confirm variable maize_zone irr_group

tempname pf
tempfile diag
postfile `pf' str48 item str120 value using `diag', replace

quietly count if main_sample == 1
post `pf' ("N_main_sample") ("`r(N)'")
post `pf' ("heat_main") ("hdd_ge32")
post `pf' ("heat_x_ca") ("SR_x_Heat_full = ca * hdd_ge32")
post `pf' ("map_D_v3pre30") ("D_v3pre30 = max(0,-spei1_mean_v3pre30)")
post `pf' ("map_D_v3he") ("D_v3he = max(0,-spei2_mean_v3he)")
post `pf' ("map_D_hema") ("D_hema = max(0,-spei2_mean_hema)")
post `pf' ("map_D_fullnew") ("D_full")
post `pf' ("map_W_v3pre30") ("W_v3pre30 = max(0,spei1_mean_v3pre30)")
post `pf' ("map_W_v3he") ("W_v3he = max(0,spei2_mean_v3he)")
post `pf' ("map_W_hema") ("W_hema = max(0,spei2_mean_hema)")
post `pf' ("map_W_fullnew") ("W_full")

forvalues m = 1/3 {
    local mcode : word `m' of $V6_MD_METRIC_CODES

    forvalues w = 1/4 {
        local wlbl : word `w' of $V6_WINDOWS
        local wc : word `w' of $V6_WINDOW_CODES
        local tag "`mcode'_`wc'"

        gen byte v6h_`tag' = (main_sample == 1) if !missing(main_sample)
        replace v6h_`tag' = 0 if missing(v6h_`tag')

        local d_var "D_v3pre30"
        local w_var "W_v3pre30"
        if "`wlbl'" == "v3he" {
            local d_var "D_v3he"
            local w_var "W_v3he"
        }
        if "`wlbl'" == "hema" {
            local d_var "D_hema"
            local w_var "W_hema"
        }
        if "`wlbl'" == "fullnew" {
            local d_var "D_full"
            local w_var "W_full"
        }

        foreach v in ln_yield ca hdd_ge32 SR_x_Heat_full `d_var' `w_var' $V6_CTRL_NOHEAT maize_zone irr_group {
            replace v6h_`tag' = 0 if missing(`v') & v6h_`tag' == 1
        }

        forvalues s = 1/2 {
            local src : word `s' of $V6_SOURCE_CODES
            local dry_stub : word `m' of $V6_MD_DRY_STUBS
            local vdry "`dry_stub'_`src'_`wc'"
            confirm variable `vdry'
            gen double v6h`tag'_`src' = `vdry'
            label var v6h`tag'_`src' "v6 heatctrl dry mediator `tag' / `src'"
            replace v6h_`tag' = 0 if missing(v6h`tag'_`src') & v6h_`tag' == 1
        }

        quietly count if v6h_`tag' == 1
        post `pf' ("N_v6h_`tag'") ("`r(N)'")
    }
}

forvalues m = 1/4 {
    local mcode : word `m' of $V6_METRIC_CODES

    forvalues p = 1/2 {
        local dp : word `p' of $V6_DRY_PCTS

        forvalues w = 1/4 {
            local wlbl : word `w' of $V6_WINDOWS
            local wc : word `w' of $V6_WINDOW_CODES
            local tag "`mcode'_`dp'_`wc'"

            gen byte v6h_`tag' = (main_sample == 1) if !missing(main_sample)
            replace v6h_`tag' = 0 if missing(v6h_`tag')

            local d_var "D_v3pre30"
            local w_var "W_v3pre30"
            if "`wlbl'" == "v3he" {
                local d_var "D_v3he"
                local w_var "W_v3he"
            }
            if "`wlbl'" == "hema" {
                local d_var "D_hema"
                local w_var "W_hema"
            }
            if "`wlbl'" == "fullnew" {
                local d_var "D_full"
                local w_var "W_full"
            }

            foreach v in ln_yield ca hdd_ge32 SR_x_Heat_full `d_var' `w_var' $V6_CTRL_NOHEAT maize_zone irr_group {
                replace v6h_`tag' = 0 if missing(`v') & v6h_`tag' == 1
            }

            forvalues s = 1/2 {
                local src : word `s' of $V6_SOURCE_CODES
                local dry_stub : word `m' of $V6_DRY_STUBS
                local vdry "`dry_stub'_`src'_`dp'_`wc'"
                confirm variable `vdry'
                gen double v6h`tag'_`src' = `vdry'
                label var v6h`tag'_`src' "v6 heatctrl dry mediator `tag' / `src'"
                replace v6h_`tag' = 0 if missing(v6h`tag'_`src') & v6h_`tag' == 1
            }

            quietly count if v6h_`tag' == 1
            post `pf' ("N_v6h_`tag'") ("`r(N)'")
        }
    }
}

postclose `pf'

preserve
use `diag', clear
export delimited using "$v6hdiag_csv", replace
restore

compress
save "$v6hready_dta", replace

log close
di "=== v6gleambl_heatctrl_step0_preamble.do COMPLETE ==="
