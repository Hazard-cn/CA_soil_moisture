* =============================================================================
* v3_step2_stage_effects.do
* Purpose: Stage-specific effects — 6 single-window Spec(2) + 3 horse-race
*          schemes + focused horse-race
* Author:  YangSu + Claude
* Date:    2026-04-04
* Input:   data/processed/v3_analysis_ready.dta
* Output:  output/tables/v3_step2_stage_single.csv
*          output/tables/v3_step2_stage_horserace.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3_macros_include.do"

log using "$logdir/v3_step2_stage_effects.log", replace

use "$outdata/v3_analysis_ready.dta", clear
xtset grid_id year

* =============================================================================
* PART A: Single-window Spec(2) — 6 windows
* =============================================================================
di "========================================================"
di "PART A: Single-window Spec(2)"
di "========================================================"

tempname pf
postfile `pf' str10 window ///
    b_SRD se_SRD p_SRD ///
    b_SRH se_SRH p_SRH ///
    b_DH se_DH p_DH ///
    b_SRDH se_SRDH p_SRDH ///
    b_D se_D p_D ///
    b_H se_H p_H ///
    r2 N ///
    using "$outdir/v3_step2_stage_single.dta", replace

eststo clear

foreach w in full v3pre30 v3pm10 hepm10 v3he hema {
    di _n "--- Window: `w' ---"

    eststo sw_`w': reghdfe ln_yield ${RHS_spec2_`w'} ${CTRL_`w'} ///
        if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)

    post `pf' ("`w'") ///
        (_b[SR_x_D_`w']) (_se[SR_x_D_`w']) ///
        (2*ttail(e(df_r), abs(_b[SR_x_D_`w']/_se[SR_x_D_`w']))) ///
        (_b[SR_x_Heat_`w']) (_se[SR_x_Heat_`w']) ///
        (2*ttail(e(df_r), abs(_b[SR_x_Heat_`w']/_se[SR_x_Heat_`w']))) ///
        (_b[D_x_Heat_`w']) (_se[D_x_Heat_`w']) ///
        (2*ttail(e(df_r), abs(_b[D_x_Heat_`w']/_se[D_x_Heat_`w']))) ///
        (_b[SR_x_D_x_Heat_`w']) (_se[SR_x_D_x_Heat_`w']) ///
        (2*ttail(e(df_r), abs(_b[SR_x_D_x_Heat_`w']/_se[SR_x_D_x_Heat_`w']))) ///
        (_b[D_`w']) (_se[D_`w']) ///
        (2*ttail(e(df_r), abs(_b[D_`w']/_se[D_`w']))) ///
        (_b[hdd_ge32`=cond("`w'"=="full","","_`w'")']) ///
        (_se[hdd_ge32`=cond("`w'"=="full","","_`w'")']) ///
        (2*ttail(e(df_r), abs(_b[hdd_ge32`=cond("`w'"=="full","","_`w'")'] ///
            /_se[hdd_ge32`=cond("`w'"=="full","","_`w'")']))) ///
        (e(r2)) (e(N))
}

postclose `pf'

* Export single-window table
esttab sw_full sw_v3pre30 sw_v3pm10 sw_hepm10 sw_v3he sw_hema ///
    using "$outdir/v3_step2_single_table.csv", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(r2 r2_a N, labels("R-squared" "Adj R-squared" "N") fmt(4 4 0)) ///
    mtitles("Full" "V3pre30" "V3pm10" "HEpm10" "V3-HE" "HE-MA") ///
    title("V3 Step 2A: Single-Window Spec(2)") ///
    nonotes addnotes("Clustered SE at grid_id level")

* Export postfile CSV
preserve
use "$outdir/v3_step2_stage_single.dta", clear
format b_* se_* %9.4f
format p_* %7.4f
list, sep(0) noobs
export delimited using "$outdir/v3_step2_stage_single.csv", replace
restore

* =============================================================================
* PART B: 3-Scheme Horse-Race (Spec 2)
* =============================================================================
di _n "========================================================"
di "PART B: 3-Scheme Horse-Race"
di "========================================================"

tempname pf2
postfile `pf2' str10 scheme str10 window str10 coef_type ///
    b se p ///
    using "$outdir/v3_step2_stage_horserace.dta", replace

* --- Scheme i: V3pm10 + HEpm10 ---
di _n "--- Scheme i: V3pm10 + HEpm10 ---"
eststo hr_i: reghdfe ln_yield $RHS_hr_scheme_i $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)

foreach w in v3pm10 hepm10 {
    foreach ctype in SR_x_D SR_x_Heat D_x_Heat SR_x_D_x_Heat {
        post `pf2' ("i") ("`w'") ("`ctype'") ///
            (_b[`ctype'_`w']) (_se[`ctype'_`w']) ///
            (2*ttail(e(df_r), abs(_b[`ctype'_`w']/_se[`ctype'_`w'])))
    }
}

* --- Scheme ii: V3HE + HEMA ---
di _n "--- Scheme ii: V3HE + HEMA ---"
eststo hr_ii: reghdfe ln_yield $RHS_hr_scheme_ii $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)

foreach w in v3he hema {
    foreach ctype in SR_x_D SR_x_Heat D_x_Heat SR_x_D_x_Heat {
        post `pf2' ("ii") ("`w'") ("`ctype'") ///
            (_b[`ctype'_`w']) (_se[`ctype'_`w']) ///
            (2*ttail(e(df_r), abs(_b[`ctype'_`w']/_se[`ctype'_`w'])))
    }
}

* --- Scheme iii: V3pre30 + V3HE + HEMA ---
di _n "--- Scheme iii: V3pre30 + V3HE + HEMA ---"
eststo hr_iii: reghdfe ln_yield $RHS_hr_scheme_iii $CTRL_full ///
    if main_sample == 1, absorb(grid_id year) vce(cluster grid_id)

foreach w in v3pre30 v3he hema {
    foreach ctype in SR_x_D SR_x_Heat D_x_Heat SR_x_D_x_Heat {
        post `pf2' ("iii") ("`w'") ("`ctype'") ///
            (_b[`ctype'_`w']) (_se[`ctype'_`w']) ///
            (2*ttail(e(df_r), abs(_b[`ctype'_`w']/_se[`ctype'_`w'])))
    }
}

postclose `pf2'

* Export horse-race table
esttab hr_i hr_ii hr_iii ///
    using "$outdir/v3_step2_horserace_table.csv", replace ///
    cells(b(star fmt(4)) se(par fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(r2 r2_a N, labels("R-squared" "Adj R-squared" "N") fmt(4 4 0)) ///
    mtitles("Scheme-i" "Scheme-ii" "Scheme-iii") ///
    title("V3 Step 2B: Horse-Race Spec(2)") ///
    nonotes addnotes("Clustered SE at grid_id level")

* Export postfile CSV
preserve
use "$outdir/v3_step2_stage_horserace.dta", clear
format b se %9.4f
format p %7.4f
list, sep(4) noobs
export delimited using "$outdir/v3_step2_stage_horserace.csv", replace
restore

log close
di "=== v3_step2_stage_effects.do COMPLETE ==="
