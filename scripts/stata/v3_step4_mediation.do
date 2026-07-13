* =============================================================================
* v3_step4_mediation.do
* Purpose: Formal mediation — Baron-Kenny + OPTIMIZED bootstrap (pre-demean).
*          Language discipline: "channel-consistent conditional association"
* Author:  YangSu + Claude
* Date:    2026-04-04
* Input:   data/processed/v3_analysis_ready.dta
* Output:  output/tables/v3_step4_mediation_bk.csv
*          output/tables/v3_step4_mediation_bootstrap.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3_macros_include.do"

log using "$logdir/v3_step4_mediation.log", replace

use "$outdata/v3_analysis_ready.dta", clear
xtset grid_id year

* =============================================================================
* PART A: Baron-Kenny point estimates + Sobel SE
*   6 windows x 3 SM sources = 18 combinations
* =============================================================================
di "========================================================"
di "PART A: Baron-Kenny Mediation"
di "========================================================"

tempname pf
postfile `pf' str10 window str10 sm_src ///
    b_total se_total p_total ///
    b_a se_a p_a ///
    b_b se_b p_b ///
    b_direct se_direct p_direct ///
    b_indirect se_indirect ///
    pct_mediated N ///
    using "$outdir/v3_step4_mediation_bk.dta", replace

foreach w in full v3pre30 v3pm10 hepm10 v3he hema {
    local wsfx = cond("`w'" == "full", "", "_`w'")
    local h_var = cond("`w'" == "full", "hdd_ge32", "hdd_ge32_`w'")

    di _n "========================================================"
    di "WINDOW: `w'"
    di "========================================================"

    foreach src in gleam_smrz swsm_l3 era5l_swvl3 {
        local slbl = cond("`src'" == "gleam_smrz", "gleam", ///
                     cond("`src'" == "swsm_l3", "swsm", "era5l"))
        local smvar = cond("`src'" == "gleam_smrz", "gsm", ///
                      cond("`src'" == "swsm_l3", "ssm", "esm"))

        di _n "--- `w' x `slbl' ---"

        * Step 1: Total effect (Y on D, no SM)
        qui reghdfe ln_yield D_`w' W_`w' `h_var' ca ///
            SR_x_D_`w' SR_x_W_`w' SR_x_Heat_`w' ///
            ${CTRL_`w'} if main_sample == 1, ///
            absorb(grid_id year) vce(cluster grid_id)

        local b_total = _b[D_`w']
        local se_total = _se[D_`w']
        local p_total = 2*ttail(e(df_r), abs(`b_total'/`se_total'))
        local N_obs = e(N)

        * Step 2: a-path (SM on D)
        qui reghdfe `src'_mean`wsfx' ///
            D_`w' W_`w' `h_var' ca ///
            SR_x_D_`w' SR_x_Heat_`w' ///
            ${CTRL_`w'} if main_sample == 1, ///
            absorb(grid_id year) vce(cluster grid_id)

        local b_a = _b[D_`w']
        local se_a = _se[D_`w']
        local p_a = 2*ttail(e(df_r), abs(`b_a'/`se_a'))

        * Step 3: b-path + direct effect (Y on D + SM)
        qui reghdfe ln_yield D_`w' W_`w' `h_var' ca ///
            SR_x_D_`w' SR_x_W_`w' SR_x_Heat_`w' ///
            `src'_mean`wsfx' `smvar'_x_D_`w' `smvar'_x_H_`w' `smvar'_x_SR_`w' ///
            ${CTRL_`w'} if main_sample == 1, ///
            absorb(grid_id year) vce(cluster grid_id)

        local b_b = _b[`src'_mean`wsfx']
        local se_b = _se[`src'_mean`wsfx']
        local p_b = 2*ttail(e(df_r), abs(`b_b'/`se_b'))
        local b_direct = _b[D_`w']
        local se_direct = _se[D_`w']
        local p_direct = 2*ttail(e(df_r), abs(`b_direct'/`se_direct'))

        * Indirect = a * b, Sobel SE
        local b_indirect = `b_a' * `b_b'
        local se_indirect = sqrt((`b_a')^2 * (`se_b')^2 + (`b_b')^2 * (`se_a')^2)
        local pct_med = cond(`b_total' != 0, 100 * `b_indirect' / `b_total', .)

        di "Total=" %7.4f `b_total' " a=" %7.4f `b_a' " b=" %7.4f `b_b' ///
           " indirect=" %7.4f `b_indirect' " pct=" %5.1f `pct_med' "%"

        post `pf' ("`w'") ("`slbl'") ///
            (`b_total') (`se_total') (`p_total') ///
            (`b_a') (`se_a') (`p_a') ///
            (`b_b') (`se_b') (`p_b') ///
            (`b_direct') (`se_direct') (`p_direct') ///
            (`b_indirect') (`se_indirect') ///
            (`pct_med') (`N_obs')
    }
}

postclose `pf'

preserve
use "$outdir/v3_step4_mediation_bk.dta", clear
format b_* se_* %9.4f
format p_* %7.4f
format pct_mediated %5.1f
list, sep(3) noobs
export delimited using "$outdir/v3_step4_mediation_bk.csv", replace
restore

* =============================================================================
* PART B: Optimized Bootstrap — Pre-demean + fast regress
*   Strategy: FWL theorem — demean all vars by grid_id + year, then OLS
*   Expected speedup: 200x (regress ~0.01s vs reghdfe ~2s per call)
* =============================================================================
di _n "========================================================"
di "PART B: Optimized Bootstrap Mediation"
di "========================================================"

* Keep main sample only for efficiency
keep if main_sample == 1
local N_main = _N
di "Working sample: N = `N_main'"

* --- Step B1: Check panel balance ---
bysort grid_id: gen n_years = _N
tab n_years
sum n_years, detail
local min_yrs = r(min)
local max_yrs = r(max)
di "Panel balance: min years = `min_yrs', max years = `max_yrs'"
drop n_years

* --- Step B2: Pre-demean all variables ---
di "Pre-demeaning variables..."
timer on 1

* Collect all variables that need demeaning
local dm_vars ln_yield ca

* D/W/H for each window
foreach w in full v3pre30 v3pm10 hepm10 v3he hema {
    local dm_vars `dm_vars' D_`w' W_`w'
}
local dm_vars `dm_vars' hdd_ge32 hdd_ge32_v3pre30 hdd_ge32_v3pm10 ///
    hdd_ge32_hepm10 hdd_ge32_v3he hdd_ge32_hema

* SR interactions for each window
foreach w in full v3pre30 v3pm10 hepm10 v3he hema {
    local dm_vars `dm_vars' SR_x_D_`w' SR_x_W_`w' SR_x_Heat_`w'
}

* SM variables (ERA5L only for bootstrap — primary source)
foreach w in full v3pre30 v3he hema {
    local wsfx = cond("`w'" == "full", "", "_`w'")
    local dm_vars `dm_vars' era5l_swvl3_mean`wsfx' ///
        esm_x_D_`w' esm_x_H_`w' esm_x_SR_`w'
}

* Controls (full season for all bootstrap runs)
local dm_vars `dm_vars' irr_frac pr_sum et0_sum aridity gdd_ge10
* Window-specific controls
foreach w in v3pre30 v3he hema {
    local dm_vars `dm_vars' pr_sum_`w' et0_sum_`w' gdd_ge10_`w'
}

* Two-way within transformation
foreach v of local dm_vars {
    cap drop gm_`v' ym_`v'
    bysort grid_id: egen double gm_`v' = mean(`v')
    bysort year: egen double ym_`v' = mean(`v')
    qui sum `v', meanonly
    cap drop dm_`v'
    gen double dm_`v' = `v' - gm_`v' - ym_`v' + r(mean)
    drop gm_`v' ym_`v'
}

timer off 1
timer list 1
di "Pre-demeaning complete."

* --- Step B3: Validate demeaning ---
di _n "--- Validation: reghdfe vs demeaned regress ---"

* Test with full-season Spec(1)
qui reghdfe ln_yield D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    irr_frac pr_sum et0_sum aridity gdd_ge10, ///
    absorb(grid_id year) vce(cluster grid_id)
local b_fe_SRD = _b[SR_x_D_full]
local b_fe_D   = _b[D_full]

qui regress dm_ln_yield dm_D_full dm_W_full dm_hdd_ge32 dm_ca ///
    dm_SR_x_D_full dm_SR_x_W_full dm_SR_x_Heat_full ///
    dm_irr_frac dm_pr_sum dm_et0_sum dm_aridity dm_gdd_ge10, nocons
local b_dm_SRD = _b[dm_SR_x_D_full]
local b_dm_D   = _b[dm_D_full]

local diff_SRD = abs(`b_fe_SRD' - `b_dm_SRD')
local diff_D   = abs(`b_fe_D' - `b_dm_D')
di "Validation SRxD: reghdfe=" %10.6f `b_fe_SRD' " regress=" %10.6f `b_dm_SRD' ///
   " diff=" %12.8f `diff_SRD'
di "Validation D:    reghdfe=" %10.6f `b_fe_D'   " regress=" %10.6f `b_dm_D' ///
   " diff=" %12.8f `diff_D'

if `diff_SRD' > 0.001 | `diff_D' > 0.001 {
    di as error "WARNING: Demeaning validation FAILED — diff > 0.001"
    di as error "Consider iterative demeaning for unbalanced panel"
}
else {
    di as result "Validation PASSED: demeaning accurate to 3 decimals"
}

* --- Step B4: Define fast bootstrap program ---
xtset, clear

cap program drop med_boot_fast
program define med_boot_fast, rclass
    syntax, window(string) ctrl_dm(string)

    local wsfx = cond("`window'" == "full", "", "_`window'")

    * a-path: D -> SM (ERA5L)
    qui regress dm_era5l_swvl3_mean`wsfx' ///
        dm_D_`window' dm_W_`window' ///
        dm_hdd_ge32`=cond("`window'"=="full","","_`window'")' dm_ca ///
        dm_SR_x_D_`window' dm_SR_x_Heat_`window' ///
        `ctrl_dm', nocons
    local a = _b[dm_D_`window']

    * b-path: SM -> Y (controlling for D)
    qui regress dm_ln_yield ///
        dm_D_`window' dm_W_`window' ///
        dm_hdd_ge32`=cond("`window'"=="full","","_`window'")' dm_ca ///
        dm_SR_x_D_`window' dm_SR_x_W_`window' dm_SR_x_Heat_`window' ///
        dm_era5l_swvl3_mean`wsfx' ///
        dm_esm_x_D_`window' dm_esm_x_H_`window' dm_esm_x_SR_`window' ///
        `ctrl_dm', nocons
    local b = _b[dm_era5l_swvl3_mean`wsfx']

    return scalar indirect = `a' * `b'
    return scalar a_path = `a'
    return scalar b_path = `b'
end

* --- Step B5: Run bootstrap for key combinations ---
tempname pf_bs
postfile `pf_bs' str10 window str10 sm_src ///
    b_indirect ci_lo ci_hi ///
    b_a b_b ///
    bs_se_indirect bs_se_a bs_se_b ///
    using "$outdir/v3_step4_mediation_bootstrap.dta", replace

foreach w in full v3pre30 v3he hema {
    di _n "Bootstrap: `w' x ERA5L (1000 reps)"
    timer on 2

    * Set up control macro for demeaned variables
    if "`w'" == "full" {
        local ctrl_dm "dm_irr_frac dm_pr_sum dm_et0_sum dm_aridity dm_gdd_ge10"
    }
    else {
        local ctrl_dm "dm_irr_frac dm_pr_sum_`w' dm_et0_sum_`w' dm_aridity dm_gdd_ge10_`w'"
    }

    bootstrap indirect=r(indirect) a_path=r(a_path) b_path=r(b_path), ///
        reps(1000) seed(42) cluster(grid_id) nodots: ///
        med_boot_fast, window(`w') ctrl_dm(`ctrl_dm')

    * Extract bootstrap results
    matrix bs = e(b)
    matrix bs_se = e(se)
    local b_ind = bs[1,1]
    local b_a   = bs[1,2]
    local b_b   = bs[1,3]
    local se_ind = bs_se[1,1]
    local se_a   = bs_se[1,2]
    local se_b   = bs_se[1,3]

    * BC confidence interval
    estat bootstrap, bc
    matrix ci = r(ci_bc)
    local ci_lo = ci[1,1]
    local ci_hi = ci[2,1]

    di "`w': indirect = " %7.4f `b_ind' " [" %7.4f `ci_lo' ", " %7.4f `ci_hi' "]"

    post `pf_bs' ("`w'") ("era5l") ///
        (`b_ind') (`ci_lo') (`ci_hi') ///
        (`b_a') (`b_b') ///
        (`se_ind') (`se_a') (`se_b')

    timer off 2
    timer list 2
}

postclose `pf_bs'

preserve
use "$outdir/v3_step4_mediation_bootstrap.dta", clear
format b_* ci_* bs_* %9.4f
list, sep(0) noobs
export delimited using "$outdir/v3_step4_mediation_bootstrap.csv", replace
restore

* =============================================================================
* PART C: Moderated mediation — conditional indirect at SR=0 vs SR=1
* =============================================================================
di _n "========================================================"
di "PART C: Moderated Mediation — ERA5L"
di "========================================================"

xtset grid_id year

foreach w in full v3pre30 v3he hema {
    local wsfx = cond("`w'" == "full", "", "_`w'")
    local h_var = cond("`w'" == "full", "hdd_ge32", "hdd_ge32_`w'")

    di _n "--- `w': Conditional indirect at SR=0 vs SR=1 ---"

    * a-path with SR moderation
    qui reghdfe era5l_swvl3_mean`wsfx' ///
        D_`w' `h_var' ca SR_x_D_`w' SR_x_Heat_`w' ///
        ${CTRL_`w'}, ///
        absorb(grid_id year) vce(cluster grid_id)

    local a0 = _b[D_`w']
    local a1 = _b[D_`w'] + _b[SR_x_D_`w']

    * b-path
    qui reghdfe ln_yield D_`w' W_`w' `h_var' ca ///
        SR_x_D_`w' SR_x_W_`w' SR_x_Heat_`w' ///
        era5l_swvl3_mean`wsfx' esm_x_D_`w' esm_x_H_`w' esm_x_SR_`w' ///
        ${CTRL_`w'}, ///
        absorb(grid_id year) vce(cluster grid_id)

    local b_sm = _b[era5l_swvl3_mean`wsfx']

    local ind0 = `a0' * `b_sm'
    local ind1 = `a1' * `b_sm'

    di "`w': indirect(SR=0)=" %7.4f `ind0' ///
       "  indirect(SR=1)=" %7.4f `ind1' ///
       "  diff=" %7.4f (`ind1' - `ind0')
}

log close
di "=== v3_step4_mediation.do COMPLETE ==="
