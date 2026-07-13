* =============================================================================
* v3proxy_step2_heat_consistency.do
* Purpose: Append heat consistency models (±HotDryPr) to v3proxy results.
*          Heat module: lnY ~ H + ca + SR×H + DrySM + (±HDP) + ctrl + FE
* Author:  YangSu + Claude
* Date:    2026-04-16
* Input:   data/processed/v3proxy_analysis_ready.dta
*          output/tables/v3proxy_results_long.dta  (from step1)
* Output:  output/tables/v3proxy_results_long.dta  (appended)
*          output/tables/v3proxy_results_long.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3proxy_macros_include.do"

log using "$logdir/v3proxy_step2_heat_consistency.log", replace

use "$datadir/v3proxy_analysis_ready.dta", clear
xtset grid_id year
keep if v3proxy_common == 1
di "Working sample N = " _N

* =============================================================================
* Helper program (same schema as step1, includes hdp)
* =============================================================================
capture program drop post_proxy_coef
program define post_proxy_coef
    syntax, POST(name) MODULE(string) MODELSET(string) CTRL(string) SOURCE(string) ///
        LAYER(string) CUT(string) HDP(string) RAWWIN(string) TERM(string) ///
        TERMGROUP(string) VARNAME(name)

    local N = e(N)
    local r2 = e(r2)
    local dfr = e(df_r)

    capture scalar __b = _b[`varname']
    if _rc == 0 {
        scalar __se = _se[`varname']
        scalar __p = 2 * ttail(`dfr', abs(__b / __se))
        post `post' ("`module'") ("`modelset'") ("`ctrl'") ("`source'") ///
            ("`layer'") ("`cut'") ("`hdp'") ("`rawwin'") ("`term'") ///
            ("`termgroup'") (__b) (__se) (__p) (`N') (`r2') (1)
    }
    else {
        post `post' ("`module'") ("`modelset'") ("`ctrl'") ("`source'") ///
            ("`layer'") ("`cut'") ("`hdp'") ("`rawwin'") ("`term'") ///
            ("`termgroup'") (.) (.) (.) (`N') (`r2') (0)
    }
end

* =============================================================================
* Postfile (same schema as step1, writes to separate temp file then appends)
* =============================================================================
tempname pf_heat
postfile `pf_heat' str12 module str16 model_set str8 ctrl_version str12 source ///
    str10 layer str8 cut str3 hdp str10 raw_window str20 term str24 term_group ///
    double b se p N r2 byte coef_present ///
    using "$outdir/v3proxy_heat_results.dta", replace

* =============================================================================
* Main loop: ctrl × cut × hdp × source × layer
* =============================================================================
foreach cv in reduced full {
    foreach cut of global CUTS {
        local raw_windows "${CUT_`cut'_WINDOWS}"
        local ctrl_list "${CTRL_`cv'_`cut'}"

        * --- Build window-specific H/SR×H/HDP lists ---
        local h_list ""
        local hca_list ""
        local hdp_list ""

        foreach rw of local raw_windows {
            if "`rw'" == "full" {
                local h_var   "hdd_ge32"
                local hca_var "SR_x_Heat_full"
                local hdp_var "HotDryPr_full"
            }
            else {
                local h_var   "hdd_ge32_`rw'"
                local hca_var "SR_x_Heat_`rw'"
                local hdp_var "HotDryPr_`rw'"
            }

            local h_list   "`h_list' `h_var'"
            local hca_list "`hca_list' `hca_var'"
            local hdp_list "`hdp_list' `hdp_var'"
        }

        * --- HDP loop ---
        foreach hdp of global HDP_LEVELS {
            local hdp_vars ""
            if "`hdp'" == "on" {
                local hdp_vars "`hdp_list'"
            }

            foreach source of global SOURCES {
                foreach layer of global LAYERS {
                    local sm_base "era5l_swvl3_mean"
                    if "`source'" == "gleam" & "`layer'" == "surface"  local sm_base "gleam_sms_mean"
                    if "`source'" == "gleam" & "`layer'" == "rootzone" local sm_base "gleam_smrz_mean"
                    if "`source'" == "swsm"  & "`layer'" == "surface"  local sm_base "swsm_l1_mean"
                    if "`source'" == "swsm"  & "`layer'" == "rootzone" local sm_base "swsm_l3_mean"
                    if "`source'" == "era"   & "`layer'" == "surface"  local sm_base "era5l_swvl1_mean"

                    local dry_list ""

                    foreach rw of local raw_windows {
                        local hsfx = cond("`rw'" == "full", "", "_`rw'")
                        local dry_var "dry_`sm_base'`hsfx'"
                        local dry_list "`dry_list' `dry_var'"
                    }

                    di _n "=== Heat | ctrl=`cv' | cut=`cut' | hdp=`hdp' | `source' | `layer' ==="
                    reghdfe ln_yield `h_list' ca `hca_list' `dry_list' `hdp_vars' `ctrl_list', ///
                        absorb(grid_id year) vce(cluster grid_id)

                    foreach rw of local raw_windows {
                        local hsfx = cond("`rw'" == "full", "", "_`rw'")
                        if "`rw'" == "full" {
                            local h_var   "hdd_ge32"
                            local hca_var "SR_x_Heat_full"
                        }
                        else {
                            local h_var   "hdd_ge32_`rw'"
                            local hca_var "SR_x_Heat_`rw'"
                        }
                        local dry_var "dry_`sm_base'`hsfx'"

                        post_proxy_coef, post(`pf_heat') module("heat") ///
                            modelset("HeatCheck") ctrl("`cv'") source("`source'") ///
                            layer("`layer'") cut("`cut'") hdp("`hdp'") rawwin("`rw'") ///
                            term("H") termgroup("heat_shock") varname(`h_var')
                        post_proxy_coef, post(`pf_heat') module("heat") ///
                            modelset("HeatCheck") ctrl("`cv'") source("`source'") ///
                            layer("`layer'") cut("`cut'") hdp("`hdp'") rawwin("`rw'") ///
                            term("H_x_ca") termgroup("heat_buffer") varname(`hca_var')
                        post_proxy_coef, post(`pf_heat') module("heat") ///
                            modelset("HeatCheck") ctrl("`cv'") source("`source'") ///
                            layer("`layer'") cut("`cut'") hdp("`hdp'") rawwin("`rw'") ///
                            term("drysm") termgroup("drysm_background") ///
                            varname(`dry_var')
                    }

                    * Post HDP coefficients when on
                    if "`hdp'" == "on" {
                        foreach rw of local raw_windows {
                            if "`rw'" == "full" local hdp_var "HotDryPr_full"
                            else local hdp_var "HotDryPr_`rw'"

                            post_proxy_coef, post(`pf_heat') module("heat") ///
                                modelset("HeatCheck") ctrl("`cv'") source("`source'") ///
                                layer("`layer'") cut("`cut'") hdp("`hdp'") rawwin("`rw'") ///
                                term("HDP") termgroup("hdp_coef") varname(`hdp_var')
                        }
                    }

                }   // end layer
            }   // end source
        }   // end hdp
    }   // end cut
}   // end cv

postclose `pf_heat'

* =============================================================================
* Append heat results to step1 results
* =============================================================================
preserve
use "$outdir/v3proxy_results_long.dta", clear
append using "$outdir/v3proxy_heat_results.dta"
sort module model_set ctrl_version source layer cut hdp raw_window term
save "$outdir/v3proxy_results_long.dta", replace
export delimited using "$outdir/v3proxy_results_long.csv", replace
restore

log close
di "=== v3proxy_step2_heat_consistency.do COMPLETE ==="
