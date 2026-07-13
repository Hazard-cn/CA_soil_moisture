* =============================================================================
* v6gleambl_hotdryctrl_step0_preamble.do
* Purpose: Build analysis-ready data for four-window GLEAM hot-dry baseline.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
if "$V6Q_MACROS_INCLUDE" == "" {
    global V6Q_MACROS_INCLUDE "$projdir/scripts/stata/v6gleambl_hotdryctrl_macros_include.do"
}
do "$V6Q_MACROS_INCLUDE"

log using "$logdir/v6gleambl_hotdryctrl_step0_preamble.log", replace

use "$v6qbase_dta", clear
xtset grid_id year

merge 1:1 grid_id year using "$datadir/v3sub_analysis_ready.dta", ///
    keepusing(maize_zone irr_group) keep(master match)
tab _merge
assert _merge == 3
drop _merge

local build_keep "gdd_10_30 hotdrydays_ge32_pr_lt1 hotdrydays_ge32_pr_lt1_v3pre30 hotdrydays_ge32_pr_lt1_v3he hotdrydays_ge32_pr_lt1_hema"
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

gen HotDryPr_full    = hotdrydays_ge32_pr_lt1
gen HotDryPr_v3pre30 = hotdrydays_ge32_pr_lt1_v3pre30
gen HotDryPr_v3he    = hotdrydays_ge32_pr_lt1_v3he
gen HotDryPr_hema    = hotdrydays_ge32_pr_lt1_hema

gen SR_x_HotDryPr_full    = ca * HotDryPr_full
gen SR_x_HotDryPr_v3pre30 = ca * HotDryPr_v3pre30
gen SR_x_HotDryPr_v3he    = ca * HotDryPr_v3he
gen SR_x_HotDryPr_hema    = ca * HotDryPr_hema

confirm variable ln_yield ca main_sample grid_id year
confirm variable D_full D_v3pre30 D_v3he D_hema
confirm variable W_full W_v3pre30 W_v3he W_hema
confirm variable hdd_ge32 pr_sum et0_sum gdd_10_30 irr_frac aridity
confirm variable HotDryPr_full HotDryPr_v3pre30 HotDryPr_v3he HotDryPr_hema
confirm variable SR_x_HotDryPr_full SR_x_HotDryPr_v3pre30 SR_x_HotDryPr_v3he SR_x_HotDryPr_hema
confirm variable maize_zone irr_group

tempname pf
tempfile diag
postfile `pf' str48 item str120 value using `diag', replace

quietly count if main_sample == 1
post `pf' ("N_main_sample") ("`r(N)'")
post `pf' ("hotdry_main_full") ("HotDryPr_full = hotdrydays_ge32_pr_lt1")
post `pf' ("hotdry_main_v3pre30") ("HotDryPr_v3pre30 = hotdrydays_ge32_pr_lt1_v3pre30")
post `pf' ("hotdry_main_v3he") ("HotDryPr_v3he = hotdrydays_ge32_pr_lt1_v3he")
post `pf' ("hotdry_main_hema") ("HotDryPr_hema = hotdrydays_ge32_pr_lt1_hema")
post `pf' ("map_D_v3pre30") ("D_v3pre30 = max(0,-spei1_mean_v3pre30)")
post `pf' ("map_D_v3he") ("D_v3he = max(0,-spei2_mean_v3he)")
post `pf' ("map_D_hema") ("D_hema = max(0,-spei2_mean_hema)")
post `pf' ("map_D_fullnew") ("D_full")
post `pf' ("map_W_v3pre30") ("W_v3pre30 = max(0,spei1_mean_v3pre30)")
post `pf' ("map_W_v3he") ("W_v3he = max(0,spei2_mean_v3he)")
post `pf' ("map_W_hema") ("W_hema = max(0,spei2_mean_hema)")
post `pf' ("map_W_fullnew") ("W_full")
post `pf' ("map_H_ctrl") ("hdd_ge32")

forvalues m = 1/3 {
    local mcode : word `m' of $V6_MD_METRIC_CODES

    forvalues w = 1/4 {
        local wlbl : word `w' of $V6_WINDOWS
        local wc : word `w' of $V6_WINDOW_CODES
        local tag "`mcode'_`wc'"

        gen byte v6q_`tag' = (main_sample == 1) if !missing(main_sample)
        replace v6q_`tag' = 0 if missing(v6q_`tag')

        local d_var "D_v3pre30"
        local w_var "W_v3pre30"
        local hd_var "HotDryPr_v3pre30"
        local srhd_var "SR_x_HotDryPr_v3pre30"
        if "`wlbl'" == "v3he" {
            local d_var "D_v3he"
            local w_var "W_v3he"
            local hd_var "HotDryPr_v3he"
            local srhd_var "SR_x_HotDryPr_v3he"
        }
        if "`wlbl'" == "hema" {
            local d_var "D_hema"
            local w_var "W_hema"
            local hd_var "HotDryPr_hema"
            local srhd_var "SR_x_HotDryPr_hema"
        }
        if "`wlbl'" == "fullnew" {
            local d_var "D_full"
            local w_var "W_full"
            local hd_var "HotDryPr_full"
            local srhd_var "SR_x_HotDryPr_full"
        }

        foreach v in ln_yield ca `hd_var' `srhd_var' `d_var' `w_var' hdd_ge32 $V6_CTRL_NOHEAT maize_zone irr_group {
            replace v6q_`tag' = 0 if missing(`v') & v6q_`tag' == 1
        }

        forvalues s = 1/2 {
            local src : word `s' of $V6_SOURCE_CODES
            local dry_stub : word `m' of $V6_MD_DRY_STUBS
            local vdry "`dry_stub'_`src'_`wc'"
            confirm variable `vdry'
            gen double v6q`tag'_`src' = `vdry'
            label var v6q`tag'_`src' "v6 hotdryctrl dry mediator `tag' / `src'"
            replace v6q_`tag' = 0 if missing(v6q`tag'_`src') & v6q_`tag' == 1
        }

        quietly count if v6q_`tag' == 1
        post `pf' ("N_v6q_`tag'") ("`r(N)'")
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

            gen byte v6q_`tag' = (main_sample == 1) if !missing(main_sample)
            replace v6q_`tag' = 0 if missing(v6q_`tag')

            local d_var "D_v3pre30"
            local w_var "W_v3pre30"
            local hd_var "HotDryPr_v3pre30"
            local srhd_var "SR_x_HotDryPr_v3pre30"
            if "`wlbl'" == "v3he" {
                local d_var "D_v3he"
                local w_var "W_v3he"
                local hd_var "HotDryPr_v3he"
                local srhd_var "SR_x_HotDryPr_v3he"
            }
            if "`wlbl'" == "hema" {
                local d_var "D_hema"
                local w_var "W_hema"
                local hd_var "HotDryPr_hema"
                local srhd_var "SR_x_HotDryPr_hema"
            }
            if "`wlbl'" == "fullnew" {
                local d_var "D_full"
                local w_var "W_full"
                local hd_var "HotDryPr_full"
                local srhd_var "SR_x_HotDryPr_full"
            }

            foreach v in ln_yield ca `hd_var' `srhd_var' `d_var' `w_var' hdd_ge32 $V6_CTRL_NOHEAT maize_zone irr_group {
                replace v6q_`tag' = 0 if missing(`v') & v6q_`tag' == 1
            }

            forvalues s = 1/2 {
                local src : word `s' of $V6_SOURCE_CODES
                local dry_stub : word `m' of $V6_DRY_STUBS
                local vdry "`dry_stub'_`src'_`dp'_`wc'"
                confirm variable `vdry'
                gen double v6q`tag'_`src' = `vdry'
                label var v6q`tag'_`src' "v6 hotdryctrl dry mediator `tag' / `src'"
                replace v6q_`tag' = 0 if missing(v6q`tag'_`src') & v6q_`tag' == 1
            }

            quietly count if v6q_`tag' == 1
            post `pf' ("N_v6q_`tag'") ("`r(N)'")
        }
    }
}

postclose `pf'

preserve
use `diag', clear
export delimited using "$v6qdiag_csv", replace
restore

compress
save "$v6qready_dta", replace

log close
di "=== v6gleambl_hotdryctrl_step0_preamble.do COMPLETE ==="
