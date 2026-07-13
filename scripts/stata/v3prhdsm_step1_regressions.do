* =============================================================================
* v3prhdsm_step1_regressions.do
* Purpose: Estimate Soil Moisture spec2/spec3/spec4 models and export long results
* Input:   data/processed/v3prhdsm_analysis_ready.dta
* Output:  output/tables/v3prhdsm_results_long.csv
* =============================================================================

clear all
set more off
set seed 42

do "C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata/v3prhdsm_macros_include.do"

log using "$logdir/v3prhdsm_step1_regressions.log", replace

use "$outdata/v3prhdsm_analysis_ready.dta", clear
xtset grid_id year

capture program drop post_terms_v3prhdsm
program define post_terms_v3prhdsm
    syntax anything(name=terms), POST(name) OUTCOME(string) SOURCE(string) ///
        LAYER(string) CUT(string) SPEC(string)

    local dfr = e(df_r)
    local N   = e(N)
    local r2  = e(r2)

    foreach v of local terms {
        local window "overall"
        if "`v'" == "ca" local window "overall"
        else if inlist("`v'", "D_full", "SR_x_D_full", "SR_x_Heat_full", ///
            "D_x_Heat_full", "SR_x_D_x_Heat_full", ///
            "HotDryPr_full", "SR_x_HotDryPr_full", "hdd_ge32") local window "full"
        else if strpos("`v'", "_v3pre30") local window "v3pre30"
        else if strpos("`v'", "_v3pm10")  local window "v3pm10"
        else if strpos("`v'", "_hepm10")  local window "hepm10"
        else if strpos("`v'", "_v3he")    local window "v3he"
        else if strpos("`v'", "_hema")    local window "hema"

        local p = 2 * ttail(`dfr', abs(_b[`v'] / _se[`v']))
        post `post' ("`outcome'") ("`source'") ("`layer'") ///
            ("`cut'") ("`spec'") ("`window'") ("`v'") ///
            (_b[`v']) (_se[`v']) (`p') (`N') (`r2')
    }
end

local spec2_keep ca ///
    D_full hdd_ge32 SR_x_D_full SR_x_Heat_full D_x_Heat_full SR_x_D_x_Heat_full ///
    D_v3pm10 hdd_ge32_v3pm10 SR_x_D_v3pm10 SR_x_Heat_v3pm10 D_x_Heat_v3pm10 SR_x_D_x_Heat_v3pm10 ///
    D_hepm10 hdd_ge32_hepm10 SR_x_D_hepm10 SR_x_Heat_hepm10 D_x_Heat_hepm10 SR_x_D_x_Heat_hepm10 ///
    D_v3he hdd_ge32_v3he SR_x_D_v3he SR_x_Heat_v3he D_x_Heat_v3he SR_x_D_x_Heat_v3he ///
    D_hema hdd_ge32_hema SR_x_D_hema SR_x_Heat_hema D_x_Heat_hema SR_x_D_x_Heat_hema ///
    D_v3pre30 hdd_ge32_v3pre30 SR_x_D_v3pre30 SR_x_Heat_v3pre30 D_x_Heat_v3pre30 SR_x_D_x_Heat_v3pre30

local spec3_keep ca ///
    D_full hdd_ge32 SR_x_D_full SR_x_Heat_full HotDryPr_full SR_x_HotDryPr_full ///
    D_v3pm10 hdd_ge32_v3pm10 SR_x_D_v3pm10 SR_x_Heat_v3pm10 HotDryPr_v3pm10 SR_x_HotDryPr_v3pm10 ///
    D_hepm10 hdd_ge32_hepm10 SR_x_D_hepm10 SR_x_Heat_hepm10 HotDryPr_hepm10 SR_x_HotDryPr_hepm10 ///
    D_v3he hdd_ge32_v3he SR_x_D_v3he SR_x_Heat_v3he HotDryPr_v3he SR_x_HotDryPr_v3he ///
    D_hema hdd_ge32_hema SR_x_D_hema SR_x_Heat_hema HotDryPr_hema SR_x_HotDryPr_hema ///
    D_v3pre30 hdd_ge32_v3pre30 SR_x_D_v3pre30 SR_x_Heat_v3pre30 HotDryPr_v3pre30 SR_x_HotDryPr_v3pre30

local spec4_keep ca ///
    HotDryPr_full SR_x_HotDryPr_full ///
    HotDryPr_v3pm10 SR_x_HotDryPr_v3pm10 ///
    HotDryPr_hepm10 SR_x_HotDryPr_hepm10 ///
    HotDryPr_v3he SR_x_HotDryPr_v3he ///
    HotDryPr_hema SR_x_HotDryPr_hema ///
    HotDryPr_v3pre30 SR_x_HotDryPr_v3pre30

tempname pf
postfile `pf' str24 outcome str12 source str12 layer str8 cut str6 spec ///
    str10 window str32 term double b se p N r2 ///
    using "$outdir/v3prhdsm_results_long.dta", replace

foreach outcome in gleam_sms_mean gleam_smrz_mean swsm_l1_mean swsm_l3_mean ///
    era5l_swvl1_mean era5l_swvl3_mean {

    local source = cond(strpos("`outcome'", "gleam") > 0, "gleam", ///
                   cond(strpos("`outcome'", "swsm") > 0, "swsm", "era5l"))
    local layer = cond(strpos("`outcome'", "sms") > 0, "surface", ///
                  cond(strpos("`outcome'", "smrz") > 0, "rootzone", ///
                  cond(strpos("`outcome'", "l1") > 0 | strpos("`outcome'", "swvl1") > 0, "layer1", "layer3")))

    di _n "========================================================"
    di "Outcome: `outcome' | source=`source' | layer=`layer'"
    di "========================================================"

    * -----------------------------------------------------------------------
    * Spec 2
    * -----------------------------------------------------------------------
    quietly reghdfe `outcome' $RHS_spec2_cut_i $CTRL_full ///
        if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
    post_terms_v3prhdsm $RHS_spec2_cut_i, post(`pf') outcome("`outcome'") ///
        source("`source'") layer("`layer'") cut("i") spec("spec2")

    quietly reghdfe `outcome' $RHS_spec2_cut_ii $CTRL_full ///
        if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
    post_terms_v3prhdsm $RHS_spec2_cut_ii, post(`pf') outcome("`outcome'") ///
        source("`source'") layer("`layer'") cut("ii") spec("spec2")

    quietly reghdfe `outcome' $RHS_spec2_cut_iii $CTRL_full ///
        if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
    post_terms_v3prhdsm $RHS_spec2_cut_iii, post(`pf') outcome("`outcome'") ///
        source("`source'") layer("`layer'") cut("iii") spec("spec2")

    quietly reghdfe `outcome' $RHS_spec2_cut_iv $CTRL_full ///
        if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
    post_terms_v3prhdsm $RHS_spec2_cut_iv, post(`pf') outcome("`outcome'") ///
        source("`source'") layer("`layer'") cut("iv") spec("spec2")

    * -----------------------------------------------------------------------
    * Spec 3
    * -----------------------------------------------------------------------
    quietly reghdfe `outcome' $RHS_spec3_cut_i $CTRL_full ///
        if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
    post_terms_v3prhdsm $RHS_spec3_cut_i, post(`pf') outcome("`outcome'") ///
        source("`source'") layer("`layer'") cut("i") spec("spec3")

    quietly reghdfe `outcome' $RHS_spec3_cut_ii $CTRL_full ///
        if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
    post_terms_v3prhdsm $RHS_spec3_cut_ii, post(`pf') outcome("`outcome'") ///
        source("`source'") layer("`layer'") cut("ii") spec("spec3")

    quietly reghdfe `outcome' $RHS_spec3_cut_iii $CTRL_full ///
        if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
    post_terms_v3prhdsm $RHS_spec3_cut_iii, post(`pf') outcome("`outcome'") ///
        source("`source'") layer("`layer'") cut("iii") spec("spec3")

    quietly reghdfe `outcome' $RHS_spec3_cut_iv $CTRL_full ///
        if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
    post_terms_v3prhdsm $RHS_spec3_cut_iv, post(`pf') outcome("`outcome'") ///
        source("`source'") layer("`layer'") cut("iv") spec("spec3")

    * -----------------------------------------------------------------------
    * Spec 4
    * -----------------------------------------------------------------------
    quietly reghdfe `outcome' $RHS_spec4_cut_i $CTRL_full ///
        if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
    post_terms_v3prhdsm $RHS_spec4_cut_i, post(`pf') outcome("`outcome'") ///
        source("`source'") layer("`layer'") cut("i") spec("spec4")

    quietly reghdfe `outcome' $RHS_spec4_cut_ii $CTRL_full ///
        if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
    post_terms_v3prhdsm $RHS_spec4_cut_ii, post(`pf') outcome("`outcome'") ///
        source("`source'") layer("`layer'") cut("ii") spec("spec4")

    quietly reghdfe `outcome' $RHS_spec4_cut_iii $CTRL_full ///
        if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
    post_terms_v3prhdsm $RHS_spec4_cut_iii, post(`pf') outcome("`outcome'") ///
        source("`source'") layer("`layer'") cut("iii") spec("spec4")

    quietly reghdfe `outcome' $RHS_spec4_cut_iv $CTRL_full ///
        if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
    post_terms_v3prhdsm $RHS_spec4_cut_iv, post(`pf') outcome("`outcome'") ///
        source("`source'") layer("`layer'") cut("iv") spec("spec4")
}

postclose `pf'

preserve
use "$outdir/v3prhdsm_results_long.dta", clear
format b se %9.6f
format p %7.4f
format N %12.0f
format r2 %7.4f
sort outcome spec cut window term
export delimited using "$outdir/v3prhdsm_results_long.csv", replace
restore

log close
di "=== v3prhdsm_step1_regressions.do COMPLETE ==="
