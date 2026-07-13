* =============================================================================
* v3proxy_step1_modelsets.do
* Purpose: Run drought proxy model sets with ±HotDryPr and competition checks.
*          Full factorial: 2 proxy × 2 HDP × 3 cuts × 2 ctrl × 6 SM sources
*          Plus overlap (Set C), competition (CompeteD / CompeteSM).
* Author:  YangSu + Claude
* Date:    2026-04-16
* Input:   data/processed/v3proxy_analysis_ready.dta
* Output:  output/tables/v3proxy_results_long.dta
*          output/tables/v3proxy_results_long.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3proxy_macros_include.do"

log using "$logdir/v3proxy_step1_modelsets.log", replace

use "$datadir/v3proxy_analysis_ready.dta", clear
xtset grid_id year
keep if v3proxy_common == 1
di "Working sample N = " _N

* =============================================================================
* Helper program: post one coefficient from e() results
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
* Set up postfile
* =============================================================================
tempname pf
postfile `pf' str12 module str16 model_set str8 ctrl_version str12 source ///
    str10 layer str8 cut str3 hdp str10 raw_window str20 term str24 term_group ///
    double b se p N r2 byte coef_present ///
    using "$outdir/v3proxy_results_long.dta", replace

* =============================================================================
* Main loop: ctrl × cut × hdp × proxy
* =============================================================================
foreach cv in reduced full {
    foreach cut of global CUTS {
        local raw_windows "${CUT_`cut'_WINDOWS}"
        local ctrl_list "${CTRL_`cv'_`cut'}"

        * --- Build window-specific variable lists ---
        local d_list ""
        local dca_list ""
        local h_list ""
        local hdp_list ""
        local hdpca_list ""

        foreach rw of local raw_windows {
            if "`rw'" == "full" {
                local d_var   "D_full"
                local dca_var "SR_x_D_full"
                local h_var   "hdd_ge32"
                local hdp_var "HotDryPr_full"
                local hdpca_var "SR_x_HotDryPr_full"
            }
            else {
                local d_var   "D_`rw'"
                local dca_var "SR_x_D_`rw'"
                local h_var   "hdd_ge32_`rw'"
                local hdp_var "HotDryPr_`rw'"
                local hdpca_var "SR_x_HotDryPr_`rw'"
            }

            local d_list    "`d_list' `d_var'"
            local dca_list  "`dca_list' `dca_var'"
            local h_list    "`h_list' `h_var'"
            local hdp_list  "`hdp_list' `hdp_var'"
            local hdpca_list "`hdpca_list' `hdpca_var'"
        }

        * --- HDP loop ---
        foreach hdp of global HDP_LEVELS {
            local hdp_vars ""
            if "`hdp'" == "on" {
                local hdp_vars "`hdp_list' `hdpca_list'"
            }

            * =============================================
            * Set A: Original D as drought proxy
            * =============================================
            di _n "=== Set A | ctrl=`cv' | cut=`cut' | hdp=`hdp' ==="
            reghdfe ln_yield `d_list' ca `dca_list' `h_list' `hdp_vars' `ctrl_list', ///
                absorb(grid_id year) vce(cluster grid_id)

            foreach rw of local raw_windows {
                if "`rw'" == "full" {
                    local d_var   "D_full"
                    local dca_var "SR_x_D_full"
                }
                else {
                    local d_var   "D_`rw'"
                    local dca_var "SR_x_D_`rw'"
                }

                post_proxy_coef, post(`pf') module("drought") modelset("SetA") ///
                    ctrl("`cv'") source("baseline") layer("baseline") cut("`cut'") ///
                    hdp("`hdp'") rawwin("`rw'") term("D") termgroup("shock_coef") ///
                    varname(`d_var')
                post_proxy_coef, post(`pf') module("drought") modelset("SetA") ///
                    ctrl("`cv'") source("baseline") layer("baseline") cut("`cut'") ///
                    hdp("`hdp'") rawwin("`rw'") term("D_x_ca") termgroup("buffer_interaction") ///
                    varname(`dca_var')
            }

            * Post HotDryPr coefficients when hdp == on
            if "`hdp'" == "on" {
                foreach rw of local raw_windows {
                    if "`rw'" == "full" {
                        local hdp_var   "HotDryPr_full"
                        local hdpca_var "SR_x_HotDryPr_full"
                    }
                    else {
                        local hdp_var   "HotDryPr_`rw'"
                        local hdpca_var "SR_x_HotDryPr_`rw'"
                    }

                    post_proxy_coef, post(`pf') module("drought") modelset("SetA") ///
                        ctrl("`cv'") source("baseline") layer("baseline") cut("`cut'") ///
                        hdp("`hdp'") rawwin("`rw'") term("HDP") termgroup("hdp_coef") ///
                        varname(`hdp_var')
                    post_proxy_coef, post(`pf') module("drought") modelset("SetA") ///
                        ctrl("`cv'") source("baseline") layer("baseline") cut("`cut'") ///
                        hdp("`hdp'") rawwin("`rw'") term("HDP_x_ca") termgroup("hdp_buffer") ///
                        varname(`hdpca_var')
                }
            }

            * =============================================
            * Set B: DrySM as drought proxy (6 SM sources)
            * =============================================
            foreach source of global SOURCES {
                foreach layer of global LAYERS {
                    local sm_base "era5l_swvl3_mean"
                    if "`source'" == "gleam" & "`layer'" == "surface"  local sm_base "gleam_sms_mean"
                    if "`source'" == "gleam" & "`layer'" == "rootzone" local sm_base "gleam_smrz_mean"
                    if "`source'" == "swsm"  & "`layer'" == "surface"  local sm_base "swsm_l1_mean"
                    if "`source'" == "swsm"  & "`layer'" == "rootzone" local sm_base "swsm_l3_mean"
                    if "`source'" == "era"   & "`layer'" == "surface"  local sm_base "era5l_swvl1_mean"

                    local dry_list ""
                    local dryxca_list ""

                    foreach rw of local raw_windows {
                        local hsfx = cond("`rw'" == "full", "", "_`rw'")
                        local dry_var "dry_`sm_base'`hsfx'"
                        local dryxca_var "`dry_var'_xca"

                        capture confirm variable `dryxca_var'
                        if _rc != 0 {
                            gen `dryxca_var' = `dry_var' * ca
                            label var `dryxca_var' "`dry_var' x ca"
                        }

                        local dry_list    "`dry_list' `dry_var'"
                        local dryxca_list "`dryxca_list' `dryxca_var'"
                    }

                    di _n "=== Set B | ctrl=`cv' | cut=`cut' | hdp=`hdp' | `source' | `layer' ==="
                    reghdfe ln_yield `dry_list' ca `dryxca_list' `h_list' `hdp_vars' `ctrl_list', ///
                        absorb(grid_id year) vce(cluster grid_id)

                    foreach rw of local raw_windows {
                        local hsfx = cond("`rw'" == "full", "", "_`rw'")
                        local dry_var "dry_`sm_base'`hsfx'"
                        local dryxca_var "`dry_var'_xca"

                        post_proxy_coef, post(`pf') module("drought") modelset("SetB") ///
                            ctrl("`cv'") source("`source'") layer("`layer'") ///
                            cut("`cut'") hdp("`hdp'") rawwin("`rw'") term("drysm") ///
                            termgroup("shock_coef") varname(`dry_var')
                        post_proxy_coef, post(`pf') module("drought") modelset("SetB") ///
                            ctrl("`cv'") source("`source'") layer("`layer'") ///
                            cut("`cut'") hdp("`hdp'") rawwin("`rw'") term("drysm_x_ca") ///
                            termgroup("buffer_interaction") varname(`dryxca_var')
                    }

                    * Post HotDryPr coefficients when hdp == on
                    if "`hdp'" == "on" {
                        foreach rw of local raw_windows {
                            if "`rw'" == "full" {
                                local hdp_var   "HotDryPr_full"
                                local hdpca_var "SR_x_HotDryPr_full"
                            }
                            else {
                                local hdp_var   "HotDryPr_`rw'"
                                local hdpca_var "SR_x_HotDryPr_`rw'"
                            }

                            post_proxy_coef, post(`pf') module("drought") modelset("SetB") ///
                                ctrl("`cv'") source("`source'") layer("`layer'") cut("`cut'") ///
                                hdp("`hdp'") rawwin("`rw'") term("HDP") termgroup("hdp_coef") ///
                                varname(`hdp_var')
                            post_proxy_coef, post(`pf') module("drought") modelset("SetB") ///
                                ctrl("`cv'") source("`source'") layer("`layer'") cut("`cut'") ///
                                hdp("`hdp'") rawwin("`rw'") term("HDP_x_ca") termgroup("hdp_buffer") ///
                                varname(`hdpca_var')
                        }
                    }

                    * =============================================
                    * Set C: Overlap diagnostic (D + DrySM, no interactions)
                    * =============================================
                    di _n "=== Set C | ctrl=`cv' | cut=`cut' | hdp=`hdp' | `source' | `layer' ==="
                    reghdfe ln_yield `d_list' `dry_list' ca `h_list' `hdp_vars' `ctrl_list', ///
                        absorb(grid_id year) vce(cluster grid_id)

                    foreach rw of local raw_windows {
                        if "`rw'" == "full" local d_var "D_full"
                        else local d_var "D_`rw'"
                        local hsfx = cond("`rw'" == "full", "", "_`rw'")
                        local dry_var "dry_`sm_base'`hsfx'"

                        post_proxy_coef, post(`pf') module("drought") modelset("SetC") ///
                            ctrl("`cv'") source("`source'") layer("`layer'") ///
                            cut("`cut'") hdp("`hdp'") rawwin("`rw'") term("D") ///
                            termgroup("overlap_d") varname(`d_var')
                        post_proxy_coef, post(`pf') module("drought") modelset("SetC") ///
                            ctrl("`cv'") source("`source'") layer("`layer'") ///
                            cut("`cut'") hdp("`hdp'") rawwin("`rw'") term("drysm") ///
                            termgroup("overlap_drysm") varname(`dry_var')
                    }

                    * =============================================
                    * Competition: only for reduced controls
                    * =============================================
                    if "`cv'" == "reduced" {
                        * Competition D: D interaction + DrySM control
                        di _n "=== CompeteD | cut=`cut' | hdp=`hdp' | `source' | `layer' ==="
                        reghdfe ln_yield `d_list' ca `dca_list' `dry_list' `h_list' `hdp_vars' `ctrl_list', ///
                            absorb(grid_id year) vce(cluster grid_id)

                        foreach rw of local raw_windows {
                            if "`rw'" == "full" local dca_var "SR_x_D_full"
                            else local dca_var "SR_x_D_`rw'"

                            post_proxy_coef, post(`pf') module("drought") ///
                                modelset("CompeteD") ctrl("`cv'") source("`source'") ///
                                layer("`layer'") cut("`cut'") hdp("`hdp'") rawwin("`rw'") ///
                                term("D_x_ca") termgroup("competition_d") ///
                                varname(`dca_var')
                        }

                        * Competition SM: DrySM interaction + D control
                        di _n "=== CompeteSM | cut=`cut' | hdp=`hdp' | `source' | `layer' ==="
                        reghdfe ln_yield `dry_list' ca `dryxca_list' `d_list' `h_list' `hdp_vars' `ctrl_list', ///
                            absorb(grid_id year) vce(cluster grid_id)

                        foreach rw of local raw_windows {
                            local hsfx = cond("`rw'" == "full", "", "_`rw'")
                            local dryxca_var "dry_`sm_base'`hsfx'_xca"

                            post_proxy_coef, post(`pf') module("drought") ///
                                modelset("CompeteSM") ctrl("`cv'") source("`source'") ///
                                layer("`layer'") cut("`cut'") hdp("`hdp'") rawwin("`rw'") ///
                                term("drysm_x_ca") termgroup("competition_sm") ///
                                varname(`dryxca_var')
                        }
                    }

                }   // end layer
            }   // end source
        }   // end hdp
    }   // end cut
}   // end cv

postclose `pf'

* Export to CSV
preserve
use "$outdir/v3proxy_results_long.dta", clear
sort module model_set ctrl_version source layer cut hdp raw_window term
export delimited using "$outdir/v3proxy_results_long.csv", replace
restore

log close
di "=== v3proxy_step1_modelsets.do COMPLETE ==="
