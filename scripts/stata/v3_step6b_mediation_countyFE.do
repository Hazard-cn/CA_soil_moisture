* =============================================================================
* v3_step6b_mediation_countyFE.do
* Purpose: Baron-Kenny mediation with relaxed FE structures:
*          M1: grid + county_year FE (strict, soil absorbed)
*          M2: county + year FE (soil controls enter regression)
*          6 windows x 3 SM sources x 2 FE models
* Author:  YangSu + Claude
* Date:    2026-04-05
* Input:   data/processed/v3_analysis_ready.dta
* Output:  output/tables/v3_step6b_mediation_countyFE.csv
* =============================================================================

clear all
set more off
set seed 42

* Load macros
do "C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata/v3_macros_include.do"

log using "$logdir/v3_step6b_mediation_countyFE_20260405.log", replace

use "$outdata/v3_analysis_ready.dta", clear
xtset grid_id year

* =============================================================================
* CONSTRUCT county_year FE
* =============================================================================
cap confirm variable county_code
if _rc != 0 {
    di as error "county_code not found — cannot proceed"
    log close
    exit 198
}

cap drop county_year
egen county_year = group(county_code year)
di "County-year groups: " r(max)
tab year if main_sample == 1, mi

* =============================================================================
* SOIL CONTROLS (for M2: county+year FE)
* Drop silt to avoid collinearity with clay+sand (~100%)
* =============================================================================
global SOIL clay_0_5cm_01deg sand_0_5cm_01deg bdod_0_5cm_01deg phh2o_0_5cm_01deg

* Check missing
foreach v of global SOIL {
    qui count if missing(`v') & main_sample == 1
    di "Missing `v': " r(N) " of " _N
}

* =============================================================================
* POSTFILE SETUP
* =============================================================================
tempname pf
postfile `pf' str10 fe_type str10 window str10 sm_src ///
    b_total se_total p_total ///
    b_a se_a p_a ///
    b_b se_b p_b ///
    b_direct se_direct p_direct ///
    b_indirect se_indirect ///
    pct_mediated N ///
    using "$outdir/v3_step6b_mediation_countyFE.dta", replace

* =============================================================================
* LOOP: 2 FE models x 6 windows x 3 SM sources
* =============================================================================

foreach fe_type in M1 M2 {

    * M1: grid + county_year (strict, soil absorbed by grid FE)
    * M2: county + year (soil enters regression)
    if "`fe_type'" == "M1" {
        local abs_spec "grid_id county_year"
        local soil_ctrl ""
        di _n "==============================="
        di "FE MODEL M1: grid + county_year"
        di "==============================="
    }
    else {
        local abs_spec "county_code year"
        local soil_ctrl "$SOIL"
        di _n "==============================="
        di "FE MODEL M2: county + year + soil"
        di "==============================="
    }

    foreach wsfx in "" "_v3pre30" "_v3pm10" "_hepm10" "_v3he" "_hema" {
        local wlbl = cond("`wsfx'" == "", "full", substr("`wsfx'", 2, .))
        local wlbl2 = cond("`wsfx'" == "", "_full", "`wsfx'")
        local h_var = cond("`wsfx'" == "", "hdd_ge32", "hdd_ge32`wsfx'")
        local ctrl "CTRL`wlbl2'"

        di _n "========================================================"
        di "`fe_type' — WINDOW: `wlbl'"
        di "========================================================"

        foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
            local slbl = cond("`src'" == "gleam_smrz", "gleam", ///
                         cond("`src'" == "swsm_l3", "swsm", "era5l"))
            local smvar = cond("`src'" == "gleam_smrz", "gsm", ///
                          cond("`src'" == "swsm_l3", "ssm", "esm"))

            di "--- `fe_type' x `wlbl' x `slbl' ---"

            * ============================================================
            * Step 1: Total effect (Y on D, no SM)
            * ============================================================
            cap noi reghdfe ln_yield D`wlbl2' W`wlbl2' `h_var' ca ///
                SR_x_D`wlbl2' SR_x_W`wlbl2' SR_x_Heat`wlbl2' ///
                $`ctrl' `soil_ctrl' if main_sample == 1, ///
                absorb(`abs_spec') vce(cluster grid_id)

            if _rc != 0 {
                di "WARNING: Step 1 failed for `fe_type' x `wlbl' x `slbl'"
                post `pf' ("`fe_type'") ("`wlbl'") ("`slbl'") ///
                    (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (0)
                continue
            }

            local b_total = _b[D`wlbl2']
            local se_total = _se[D`wlbl2']
            local dfr = e(df_r)
            local p_total = 2*ttail(`dfr', abs(`b_total'/`se_total'))
            local N_obs = e(N)
            di "Total effect of D: " %7.4f `b_total' " (SE=" %7.4f `se_total' ")"

            * ============================================================
            * Step 2: a-path (SM on D)
            * ============================================================
            cap noi reghdfe `src'_mean`wsfx' ///
                D`wlbl2' W`wlbl2' `h_var' ca ///
                SR_x_D`wlbl2' SR_x_Heat`wlbl2' ///
                $`ctrl' `soil_ctrl' if main_sample == 1, ///
                absorb(`abs_spec') vce(cluster grid_id)

            if _rc != 0 {
                di "WARNING: Step 2 failed for `fe_type' x `wlbl' x `slbl'"
                post `pf' ("`fe_type'") ("`wlbl'") ("`slbl'") ///
                    (`b_total') (`se_total') (`p_total') ///
                    (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (`N_obs')
                continue
            }

            local b_a = _b[D`wlbl2']
            local se_a = _se[D`wlbl2']
            local p_a = 2*ttail(e(df_r), abs(`b_a'/`se_a'))
            di "a-path (D -> SM): " %7.4f `b_a' " (SE=" %7.4f `se_a' ")"

            * ============================================================
            * Step 3: b-path + direct effect (Y on D + SM)
            * ============================================================
            cap noi reghdfe ln_yield D`wlbl2' W`wlbl2' `h_var' ca ///
                SR_x_D`wlbl2' SR_x_W`wlbl2' SR_x_Heat`wlbl2' ///
                `src'_mean`wsfx' `smvar'_x_D`wlbl2' `smvar'_x_H`wlbl2' `smvar'_x_SR`wlbl2' ///
                $`ctrl' `soil_ctrl' if main_sample == 1, ///
                absorb(`abs_spec') vce(cluster grid_id)

            if _rc != 0 {
                di "WARNING: Step 3 failed for `fe_type' x `wlbl' x `slbl'"
                post `pf' ("`fe_type'") ("`wlbl'") ("`slbl'") ///
                    (`b_total') (`se_total') (`p_total') ///
                    (`b_a') (`se_a') (`p_a') ///
                    (.) (.) (.) (.) (.) (.) (.) (.) (.) (`N_obs')
                continue
            }

            local b_b = _b[`src'_mean`wsfx']
            local se_b = _se[`src'_mean`wsfx']
            local p_b = 2*ttail(e(df_r), abs(`b_b'/`se_b'))
            local b_direct = _b[D`wlbl2']
            local se_direct = _se[D`wlbl2']
            local p_direct = 2*ttail(e(df_r), abs(`b_direct'/`se_direct'))
            di "b-path (SM -> Y): " %7.4f `b_b' " (SE=" %7.4f `se_b' ")"
            di "Direct effect of D: " %7.4f `b_direct' " (SE=" %7.4f `se_direct' ")"

            * ============================================================
            * Step 4: Indirect effect = a * b (Sobel approximation)
            * ============================================================
            local b_indirect = `b_a' * `b_b'
            local se_indirect = sqrt((`b_a')^2 * (`se_b')^2 + (`b_b')^2 * (`se_a')^2)
            local pct_med = cond(`b_total' != 0, 100 * `b_indirect' / `b_total', .)

            di "Indirect (a*b): " %7.4f `b_indirect' " (SE=" %7.4f `se_indirect' ")"
            di "Pct mediated: " %5.1f `pct_med' "%"

            post `pf' ("`fe_type'") ("`wlbl'") ("`slbl'") ///
                (`b_total') (`se_total') (`p_total') ///
                (`b_a') (`se_a') (`p_a') ///
                (`b_b') (`se_b') (`p_b') ///
                (`b_direct') (`se_direct') (`p_direct') ///
                (`b_indirect') (`se_indirect') ///
                (`pct_med') (`N_obs')
        }
    }
}

postclose `pf'

* =============================================================================
* EXPORT
* =============================================================================
preserve
use "$outdir/v3_step6b_mediation_countyFE.dta", clear
format b_* se_* %9.4f
format p_* %7.4f
format pct_mediated %5.1f

di _n "=== M1: grid + county_year FE ==="
list if fe_type == "M1", sep(3) noobs

di _n "=== M2: county + year FE (with soil controls) ==="
list if fe_type == "M2", sep(3) noobs

export delimited using "$outdir/v3_step6b_mediation_countyFE.csv", replace
restore

log close
di "=== v3_step6b_mediation_countyFE.do COMPLETE ==="
