* =============================================================================
* v3prhd_step1_regressions.do
* Purpose: Estimate 4 specs x 4 cuts and export tables/long results
* Input:   data/processed/v3prhd_analysis_ready.dta
* Output:  output/tables/v3prhd_results_long.csv
*          output/tables/v3prhd_spec1_table.{csv,tex}
*          output/tables/v3prhd_spec2_table.{csv,tex}
*          output/tables/v3prhd_spec3_table.{csv,tex}
*          output/tables/v3prhd_spec4_table.{csv,tex}
* =============================================================================

clear all
set more off
set seed 42

do "C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata/v3prhd_macros_include.do"

log using "$logdir/v3prhd_step1_regressions.log", replace

use "$outdata/v3prhd_analysis_ready.dta", clear
xtset grid_id year

capture program drop post_terms_v3prhd
program define post_terms_v3prhd
    syntax anything(name=terms), POST(name) CUT(string) SPEC(string)

    local dfr = e(df_r)
    local N   = e(N)
    local r2  = e(r2)

    foreach v of local terms {
        local window "overall"
        if "`v'" == "ca" local window "overall"
        else if inlist("`v'", "D_full", "SR_x_D_full", "SR_x_Heat_full", ///
            "D_x_Heat_full", "SR_x_D_x_Heat_full", "HotDryPr_full", ///
            "SR_x_HotDryPr_full", "hdd_ge32") local window "full"
        else if strpos("`v'", "_v3pre30") local window "v3pre30"
        else if strpos("`v'", "_v3pm10")  local window "v3pm10"
        else if strpos("`v'", "_hepm10")  local window "hepm10"
        else if strpos("`v'", "_v3he")    local window "v3he"
        else if strpos("`v'", "_hema")    local window "hema"

        local p = 2 * ttail(`dfr', abs(_b[`v'] / _se[`v']))
        post `post' ("`cut'") ("`spec'") ("`window'") ("`v'") ///
            (_b[`v']) (_se[`v']) (`p') (`N') (`r2')
    }
end

local spec1_keep ca ///
    D_full hdd_ge32 SR_x_D_full SR_x_Heat_full ///
    D_v3pm10 hdd_ge32_v3pm10 SR_x_D_v3pm10 SR_x_Heat_v3pm10 ///
    D_hepm10 hdd_ge32_hepm10 SR_x_D_hepm10 SR_x_Heat_hepm10 ///
    D_v3he hdd_ge32_v3he SR_x_D_v3he SR_x_Heat_v3he ///
    D_hema hdd_ge32_hema SR_x_D_hema SR_x_Heat_hema ///
    D_v3pre30 hdd_ge32_v3pre30 SR_x_D_v3pre30 SR_x_Heat_v3pre30

local spec2_keep `spec1_keep' ///
    D_x_Heat_full SR_x_D_x_Heat_full ///
    D_x_Heat_v3pm10 SR_x_D_x_Heat_v3pm10 ///
    D_x_Heat_hepm10 SR_x_D_x_Heat_hepm10 ///
    D_x_Heat_v3he SR_x_D_x_Heat_v3he ///
    D_x_Heat_hema SR_x_D_x_Heat_hema ///
    D_x_Heat_v3pre30 SR_x_D_x_Heat_v3pre30

local spec3_keep `spec1_keep' ///
    HotDryPr_full SR_x_HotDryPr_full ///
    HotDryPr_v3pm10 SR_x_HotDryPr_v3pm10 ///
    HotDryPr_hepm10 SR_x_HotDryPr_hepm10 ///
    HotDryPr_v3he SR_x_HotDryPr_v3he ///
    HotDryPr_hema SR_x_HotDryPr_hema ///
    HotDryPr_v3pre30 SR_x_HotDryPr_v3pre30

local spec4_keep ca ///
    HotDryPr_full SR_x_HotDryPr_full ///
    HotDryPr_v3pm10 SR_x_HotDryPr_v3pm10 ///
    HotDryPr_hepm10 SR_x_HotDryPr_hepm10 ///
    HotDryPr_v3he SR_x_HotDryPr_v3he ///
    HotDryPr_hema SR_x_HotDryPr_hema ///
    HotDryPr_v3pre30 SR_x_HotDryPr_v3pre30

tempname pf
postfile `pf' str8 cut str6 spec str10 window str32 term ///
    double b se p N r2 using "$outdir/v3prhd_results_long.dta", replace

eststo clear

* ---------------------------------------------------------------------------
* Spec 1
* ---------------------------------------------------------------------------
eststo s1_i: reghdfe ln_yield $RHS_spec1_cut_i $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
post_terms_v3prhd $RHS_spec1_cut_i, post(`pf') cut("i") spec("spec1")

eststo s1_ii: reghdfe ln_yield $RHS_spec1_cut_ii $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
post_terms_v3prhd $RHS_spec1_cut_ii, post(`pf') cut("ii") spec("spec1")

eststo s1_iii: reghdfe ln_yield $RHS_spec1_cut_iii $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
post_terms_v3prhd $RHS_spec1_cut_iii, post(`pf') cut("iii") spec("spec1")

eststo s1_iv: reghdfe ln_yield $RHS_spec1_cut_iv $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
post_terms_v3prhd $RHS_spec1_cut_iv, post(`pf') cut("iv") spec("spec1")

esttab s1_i s1_ii s1_iii s1_iv using "$outdir/v3prhd_spec1_table.csv", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`spec1_keep') order(`spec1_keep') ///
    stats(r2 r2_a N, labels("R-squared" "Adj R-squared" "N") fmt(4 4 0)) ///
    mtitles("i Full" "ii V3pm10+HEpm10" "iii V3HE+HEMA" "iv V3pre30+V3HE+HEMA") ///
    title("V3PRHD Spec 1") nonotes addnotes("FE: grid + year; Cluster: grid_id")

esttab s1_i s1_ii s1_iii s1_iv using "$outdir/v3prhd_spec1_table.tex", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) booktabs ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`spec1_keep') order(`spec1_keep') ///
    stats(r2 r2_a N, labels("R-squared" "Adj R-squared" "N") fmt(4 4 0)) ///
    mtitles("i Full" "ii V3pm10+HEpm10" "iii V3HE+HEMA" "iv V3pre30+V3HE+HEMA") ///
    title("V3PRHD Spec 1") nonotes addnotes("FE: grid + year; Cluster: grid_id")

* ---------------------------------------------------------------------------
* Spec 2
* ---------------------------------------------------------------------------
eststo s2_i: reghdfe ln_yield $RHS_spec2_cut_i $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
post_terms_v3prhd $RHS_spec2_cut_i, post(`pf') cut("i") spec("spec2")

eststo s2_ii: reghdfe ln_yield $RHS_spec2_cut_ii $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
post_terms_v3prhd $RHS_spec2_cut_ii, post(`pf') cut("ii") spec("spec2")

eststo s2_iii: reghdfe ln_yield $RHS_spec2_cut_iii $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
post_terms_v3prhd $RHS_spec2_cut_iii, post(`pf') cut("iii") spec("spec2")

eststo s2_iv: reghdfe ln_yield $RHS_spec2_cut_iv $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
post_terms_v3prhd $RHS_spec2_cut_iv, post(`pf') cut("iv") spec("spec2")

esttab s2_i s2_ii s2_iii s2_iv using "$outdir/v3prhd_spec2_table.csv", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`spec2_keep') order(`spec2_keep') ///
    stats(r2 r2_a N, labels("R-squared" "Adj R-squared" "N") fmt(4 4 0)) ///
    mtitles("i Full" "ii V3pm10+HEpm10" "iii V3HE+HEMA" "iv V3pre30+V3HE+HEMA") ///
    title("V3PRHD Spec 2") nonotes addnotes("FE: grid + year; Cluster: grid_id")

esttab s2_i s2_ii s2_iii s2_iv using "$outdir/v3prhd_spec2_table.tex", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) booktabs ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`spec2_keep') order(`spec2_keep') ///
    stats(r2 r2_a N, labels("R-squared" "Adj R-squared" "N") fmt(4 4 0)) ///
    mtitles("i Full" "ii V3pm10+HEpm10" "iii V3HE+HEMA" "iv V3pre30+V3HE+HEMA") ///
    title("V3PRHD Spec 2") nonotes addnotes("FE: grid + year; Cluster: grid_id")

* ---------------------------------------------------------------------------
* Spec 3
* ---------------------------------------------------------------------------
eststo s3_i: reghdfe ln_yield $RHS_spec3_cut_i $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
post_terms_v3prhd $RHS_spec3_cut_i, post(`pf') cut("i") spec("spec3")

eststo s3_ii: reghdfe ln_yield $RHS_spec3_cut_ii $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
post_terms_v3prhd $RHS_spec3_cut_ii, post(`pf') cut("ii") spec("spec3")

eststo s3_iii: reghdfe ln_yield $RHS_spec3_cut_iii $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
post_terms_v3prhd $RHS_spec3_cut_iii, post(`pf') cut("iii") spec("spec3")

eststo s3_iv: reghdfe ln_yield $RHS_spec3_cut_iv $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
post_terms_v3prhd $RHS_spec3_cut_iv, post(`pf') cut("iv") spec("spec3")

esttab s3_i s3_ii s3_iii s3_iv using "$outdir/v3prhd_spec3_table.csv", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`spec3_keep') order(`spec3_keep') ///
    stats(r2 r2_a N, labels("R-squared" "Adj R-squared" "N") fmt(4 4 0)) ///
    mtitles("i Full" "ii V3pm10+HEpm10" "iii V3HE+HEMA" "iv V3pre30+V3HE+HEMA") ///
    title("V3PRHD Spec 3") nonotes addnotes("FE: grid + year; Cluster: grid_id")

esttab s3_i s3_ii s3_iii s3_iv using "$outdir/v3prhd_spec3_table.tex", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) booktabs ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`spec3_keep') order(`spec3_keep') ///
    stats(r2 r2_a N, labels("R-squared" "Adj R-squared" "N") fmt(4 4 0)) ///
    mtitles("i Full" "ii V3pm10+HEpm10" "iii V3HE+HEMA" "iv V3pre30+V3HE+HEMA") ///
    title("V3PRHD Spec 3") nonotes addnotes("FE: grid + year; Cluster: grid_id")

* ---------------------------------------------------------------------------
* Spec 4
* ---------------------------------------------------------------------------
eststo s4_i: reghdfe ln_yield $RHS_spec4_cut_i $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
post_terms_v3prhd $RHS_spec4_cut_i, post(`pf') cut("i") spec("spec4")

eststo s4_ii: reghdfe ln_yield $RHS_spec4_cut_ii $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
post_terms_v3prhd $RHS_spec4_cut_ii, post(`pf') cut("ii") spec("spec4")

eststo s4_iii: reghdfe ln_yield $RHS_spec4_cut_iii $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
post_terms_v3prhd $RHS_spec4_cut_iii, post(`pf') cut("iii") spec("spec4")

eststo s4_iv: reghdfe ln_yield $RHS_spec4_cut_iv $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)
post_terms_v3prhd $RHS_spec4_cut_iv, post(`pf') cut("iv") spec("spec4")

esttab s4_i s4_ii s4_iii s4_iv using "$outdir/v3prhd_spec4_table.csv", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`spec4_keep') order(`spec4_keep') ///
    stats(r2 r2_a N, labels("R-squared" "Adj R-squared" "N") fmt(4 4 0)) ///
    mtitles("i Full" "ii V3pm10+HEpm10" "iii V3HE+HEMA" "iv V3pre30+V3HE+HEMA") ///
    title("V3PRHD Spec 4") nonotes addnotes("FE: grid + year; Cluster: grid_id")

esttab s4_i s4_ii s4_iii s4_iv using "$outdir/v3prhd_spec4_table.tex", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) booktabs ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`spec4_keep') order(`spec4_keep') ///
    stats(r2 r2_a N, labels("R-squared" "Adj R-squared" "N") fmt(4 4 0)) ///
    mtitles("i Full" "ii V3pm10+HEpm10" "iii V3HE+HEMA" "iv V3pre30+V3HE+HEMA") ///
    title("V3PRHD Spec 4") nonotes addnotes("FE: grid + year; Cluster: grid_id")

postclose `pf'

preserve
use "$outdir/v3prhd_results_long.dta", clear
format b se %9.6f
format p %7.4f
format N %12.0f
format r2 %7.4f
sort spec cut window term
export delimited using "$outdir/v3prhd_results_long.csv", replace
restore

log close
di "=== v3prhd_step1_regressions.do COMPLETE ==="
