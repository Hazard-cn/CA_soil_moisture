* =============================================================================
* v3med_step5_bootstrap.do
* Purpose: Cluster bootstrap for conditional IE/DE/TE and Index of moderated
*          mediation. Two primary SM sources × two modules = 4 bootstrap runs.
*          Uses reduced controls (Version B) as main specification.
* Author:  YangSu + Claude
* Date:    2026-04-16
* Input:   data/processed/v3med_analysis_ready.dta
* Output:  output/tables/v3med_bootstrap_drought.csv
*          output/tables/v3med_bootstrap_heat.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3med_macros_include.do"

log using "$logdir/v3med_step5_bootstrap.log", replace

use "$datadir/v3med_analysis_ready.dta", clear
keep if v3med_common == 1
xtset, clear   // CRITICAL: must clear xtset before bootstrap

* ca percentiles
_pctile ca, p(25 50 75)
local ca_p25 = r(r1)
local ca_p50 = r(r2)
local ca_p75 = r(r3)
di "ca P25 = " %9.4f `ca_p25'
di "ca P50 = " %9.4f `ca_p50'
di "ca P75 = " %9.4f `ca_p75'

count
local N_boot = r(N)
di "Bootstrap sample N = `N_boot'"

* Save bootstrap working file
tempfile boot_data
save `boot_data', replace
global BOOT_DATA "`boot_data'"
global BOOT_CA_P25 = `ca_p25'
global BOOT_CA_P50 = `ca_p50'
global BOOT_CA_P75 = `ca_p75'

* Bootstrap settings
local reps 500

* =============================================================================
* PROGRAM: Drought module Model 8 bootstrap
* =============================================================================
capture program drop boot_drought_m8
program define boot_drought_m8, rclass
    args sm_var

    * Resample clusters
    use "$BOOT_DATA", clear
    bsample, cluster(grid_id) idcluster(boot_grid)

    * Mediator eq: SM = a1*D + a2*ca + a3*(D×ca) + rho*H + Z + FE
    capture quietly reghdfe `sm_var' D_full ca SR_x_D_full hdd_ge32 ///
        irr_frac gdd_ge10, absorb(boot_grid year) vce(cluster boot_grid)

    if _rc != 0 {
        return scalar a1 = .
        return scalar a3 = .
        return scalar b  = .
        return scalar c1 = .
        return scalar c3 = .
        exit
    }

    local a1 = _b[D_full]
    local a3 = _b[SR_x_D_full]

    * Outcome eq: lnY = c1*D + c2*ca + c3*(D×ca) + b*SM + rho*H + Z + FE
    capture quietly reghdfe ln_yield D_full ca SR_x_D_full `sm_var' hdd_ge32 ///
        irr_frac gdd_ge10, absorb(boot_grid year) vce(cluster boot_grid)

    if _rc != 0 {
        return scalar a1 = .
        return scalar a3 = .
        return scalar b  = .
        return scalar c1 = .
        return scalar c3 = .
        exit
    }

    local b_sm = _b[`sm_var']
    local c1   = _b[D_full]
    local c3   = _b[SR_x_D_full]

    * Return raw coefficients
    return scalar a1 = `a1'
    return scalar a3 = `a3'
    return scalar b  = `b_sm'
    return scalar c1 = `c1'
    return scalar c3 = `c3'

    * Conditional effects at P25/P50/P75
    foreach clbl in p25 p50 p75 {
        local r = ${BOOT_CA_`=upper("`clbl'")'}
        return scalar ie_`clbl' = (`a1' + `a3' * `r') * `b_sm'
        return scalar de_`clbl' = `c1' + `c3' * `r'
        return scalar te_`clbl' = (`c1' + `c3' * `r') + (`a1' + `a3' * `r') * `b_sm'
    }

    * Index of moderated mediation
    return scalar idx = `a3' * `b_sm'
end

* =============================================================================
* PROGRAM: Heat module Model 8 bootstrap
* =============================================================================
capture program drop boot_heat_m8
program define boot_heat_m8, rclass
    args sm_var

    use "$BOOT_DATA", clear
    bsample, cluster(grid_id) idcluster(boot_grid)

    * Mediator eq: SM = a1h*H + a2h*ca + a3h*(H×ca) + rho_d*D + Z + FE
    capture quietly reghdfe `sm_var' hdd_ge32 ca SR_x_Heat_full D_full ///
        irr_frac gdd_ge10, absorb(boot_grid year) vce(cluster boot_grid)

    if _rc != 0 {
        return scalar a1h = .
        return scalar a3h = .
        return scalar b_h = .
        return scalar c1h = .
        return scalar c3h = .
        exit
    }

    local a1h = _b[hdd_ge32]
    local a3h = _b[SR_x_Heat_full]

    * Outcome eq
    capture quietly reghdfe ln_yield hdd_ge32 ca SR_x_Heat_full `sm_var' D_full ///
        irr_frac gdd_ge10, absorb(boot_grid year) vce(cluster boot_grid)

    if _rc != 0 {
        return scalar a1h = .
        return scalar a3h = .
        return scalar b_h = .
        return scalar c1h = .
        return scalar c3h = .
        exit
    }

    local b_h  = _b[`sm_var']
    local c1h  = _b[hdd_ge32]
    local c3h  = _b[SR_x_Heat_full]

    return scalar a1h = `a1h'
    return scalar a3h = `a3h'
    return scalar b_h = `b_h'
    return scalar c1h = `c1h'
    return scalar c3h = `c3h'

    foreach clbl in p25 p50 p75 {
        local r = ${BOOT_CA_`=upper("`clbl'")'}
        return scalar ie_`clbl' = (`a1h' + `a3h' * `r') * `b_h'
        return scalar de_`clbl' = `c1h' + `c3h' * `r'
        return scalar te_`clbl' = (`c1h' + `c3h' * `r') + (`a1h' + `a3h' * `r') * `b_h'
    }

    return scalar idx = `a3h' * `b_h'
end

* =============================================================================
* RUN BOOTSTRAP: Drought module
* =============================================================================
di _n "************************************************************"
di "DROUGHT MODULE BOOTSTRAP"
di "************************************************************"

tempname pf_d
postfile `pf_d' str20 sm_source str6 stat str4 ca_level ///
    double(point_est bs_se ci_lo ci_hi) ///
    using "$outdir/v3med_bs_drought_raw.dta", replace

foreach sm in gleam_sms_mean gleam_smrz_mean {

    di _n "=== Bootstrap: Drought × `sm' (`reps' reps) ==="

    * Run manual bootstrap loop
    tempname bs_mat
    matrix `bs_mat' = J(`reps', 13, .)
    * Columns: a1 a3 b c1 c3 ie_p25 de_p25 te_p25 ie_p50 de_p50 te_p50 ie_p75 ... idx
    * Actually let's do: ie_p25 ie_p50 ie_p75 de_p25 de_p50 de_p75 te_p25 te_p50 te_p75 idx a1 a3 b

    forvalues rep = 1/`reps' {
        if mod(`rep', 50) == 0 {
            di "." _continue
        }
        if mod(`rep', 250) == 0 {
            di " rep `rep'"
        }

        quietly boot_drought_m8 `sm'

        if !missing(r(a1)) {
            matrix `bs_mat'[`rep', 1]  = r(ie_p25)
            matrix `bs_mat'[`rep', 2]  = r(ie_p50)
            matrix `bs_mat'[`rep', 3]  = r(ie_p75)
            matrix `bs_mat'[`rep', 4]  = r(de_p25)
            matrix `bs_mat'[`rep', 5]  = r(de_p50)
            matrix `bs_mat'[`rep', 6]  = r(de_p75)
            matrix `bs_mat'[`rep', 7]  = r(te_p25)
            matrix `bs_mat'[`rep', 8]  = r(te_p50)
            matrix `bs_mat'[`rep', 9]  = r(te_p75)
            matrix `bs_mat'[`rep', 10] = r(idx)
            matrix `bs_mat'[`rep', 11] = r(a1)
            matrix `bs_mat'[`rep', 12] = r(a3)
            matrix `bs_mat'[`rep', 13] = r(b)
        }
    }
    di _n "Done."

    * Compute point estimates from original data
    quietly boot_drought_m8 `sm'

    * For each statistic, compute BS SE and percentile CI
    local stat_names "IE_P25 IE_P50 IE_P75 DE_P25 DE_P50 DE_P75 TE_P25 TE_P50 TE_P75 Index a1 a3 b"
    local pt_ests "r(ie_p25) r(ie_p50) r(ie_p75) r(de_p25) r(de_p50) r(de_p75) r(te_p25) r(te_p50) r(te_p75) r(idx) r(a1) r(a3) r(b)"

    * Re-run on original to get point estimates
    use "$BOOT_DATA", clear
    quietly reghdfe `sm' D_full ca SR_x_D_full hdd_ge32 irr_frac gdd_ge10, ///
        absorb(grid_id year) vce(cluster grid_id)
    local pt_a1 = _b[D_full]
    local pt_a3 = _b[SR_x_D_full]

    quietly reghdfe ln_yield D_full ca SR_x_D_full `sm' hdd_ge32 irr_frac gdd_ge10, ///
        absorb(grid_id year) vce(cluster grid_id)
    local pt_b  = _b[`sm']
    local pt_c1 = _b[D_full]
    local pt_c3 = _b[SR_x_D_full]

    local stat_idx = 0
    foreach sname in IE_P25 IE_P50 IE_P75 DE_P25 DE_P50 DE_P75 TE_P25 TE_P50 TE_P75 Index a1 a3 b {
        local ++stat_idx

        * Extract column from matrix
        mata: st_matrix("__col", st_matrix("`bs_mat'")[., `stat_idx'])
        svmat double __col, names(__bs)

        * Remove missing
        qui count if !missing(__bs1)
        local n_valid = r(N)

        * Compute point estimate
        if "`sname'" == "IE_P25" local pt = (`pt_a1' + `pt_a3' * `ca_p25') * `pt_b'
        else if "`sname'" == "IE_P50" local pt = (`pt_a1' + `pt_a3' * `ca_p50') * `pt_b'
        else if "`sname'" == "IE_P75" local pt = (`pt_a1' + `pt_a3' * `ca_p75') * `pt_b'
        else if "`sname'" == "DE_P25" local pt = `pt_c1' + `pt_c3' * `ca_p25'
        else if "`sname'" == "DE_P50" local pt = `pt_c1' + `pt_c3' * `ca_p50'
        else if "`sname'" == "DE_P75" local pt = `pt_c1' + `pt_c3' * `ca_p75'
        else if "`sname'" == "TE_P25" local pt = (`pt_c1' + `pt_c3' * `ca_p25') + (`pt_a1' + `pt_a3' * `ca_p25') * `pt_b'
        else if "`sname'" == "TE_P50" local pt = (`pt_c1' + `pt_c3' * `ca_p50') + (`pt_a1' + `pt_a3' * `ca_p50') * `pt_b'
        else if "`sname'" == "TE_P75" local pt = (`pt_c1' + `pt_c3' * `ca_p75') + (`pt_a1' + `pt_a3' * `ca_p75') * `pt_b'
        else if "`sname'" == "Index" local pt = `pt_a3' * `pt_b'
        else if "`sname'" == "a1" local pt = `pt_a1'
        else if "`sname'" == "a3" local pt = `pt_a3'
        else if "`sname'" == "b"  local pt = `pt_b'

        * SE and percentile CI
        qui sum __bs1 if !missing(__bs1)
        local bs_se = r(sd)

        sort __bs1
        local lo_idx = max(1, round(`n_valid' * 0.025))
        local hi_idx = min(`n_valid', round(`n_valid' * 0.975))
        local ci_lo = __bs1[`lo_idx']
        local ci_hi = __bs1[`hi_idx']

        * Parse ca_level from stat name
        local ca_lbl = ""
        if strpos("`sname'", "P25") local ca_lbl = "P25"
        else if strpos("`sname'", "P50") local ca_lbl = "P50"
        else if strpos("`sname'", "P75") local ca_lbl = "P75"
        else local ca_lbl = "all"

        * Clean stat name (remove P25 etc)
        local clean_stat = "`sname'"
        if "`ca_lbl'" != "all" {
            local clean_stat = subinstr("`sname'", "_`ca_lbl'", "", 1)
        }

        post `pf_d' ("`sm'") ("`clean_stat'") ("`ca_lbl'") ///
            (`pt') (`bs_se') (`ci_lo') (`ci_hi')

        drop __bs1
        cap matrix drop __col
    }
}

postclose `pf_d'

* Export
preserve
use "$outdir/v3med_bs_drought_raw.dta", clear
export delimited using "$outdir/v3med_bootstrap_drought.csv", replace
restore
cap erase "$outdir/v3med_bs_drought_raw.dta"

* =============================================================================
* RUN BOOTSTRAP: Heat module
* =============================================================================
di _n "************************************************************"
di "HEAT MODULE BOOTSTRAP"
di "************************************************************"

tempname pf_h
postfile `pf_h' str20 sm_source str6 stat str4 ca_level ///
    double(point_est bs_se ci_lo ci_hi) ///
    using "$outdir/v3med_bs_heat_raw.dta", replace

foreach sm in gleam_sms_mean gleam_smrz_mean {

    di _n "=== Bootstrap: Heat × `sm' (`reps' reps) ==="

    tempname bs_mat_h
    matrix `bs_mat_h' = J(`reps', 13, .)

    forvalues rep = 1/`reps' {
        if mod(`rep', 50) == 0 di "." _continue
        if mod(`rep', 250) == 0 di " rep `rep'"

        quietly boot_heat_m8 `sm'

        if !missing(r(a1h)) {
            matrix `bs_mat_h'[`rep', 1]  = r(ie_p25)
            matrix `bs_mat_h'[`rep', 2]  = r(ie_p50)
            matrix `bs_mat_h'[`rep', 3]  = r(ie_p75)
            matrix `bs_mat_h'[`rep', 4]  = r(de_p25)
            matrix `bs_mat_h'[`rep', 5]  = r(de_p50)
            matrix `bs_mat_h'[`rep', 6]  = r(de_p75)
            matrix `bs_mat_h'[`rep', 7]  = r(te_p25)
            matrix `bs_mat_h'[`rep', 8]  = r(te_p50)
            matrix `bs_mat_h'[`rep', 9]  = r(te_p75)
            matrix `bs_mat_h'[`rep', 10] = r(idx)
            matrix `bs_mat_h'[`rep', 11] = r(a1h)
            matrix `bs_mat_h'[`rep', 12] = r(a3h)
            matrix `bs_mat_h'[`rep', 13] = r(b_h)
        }
    }
    di _n "Done."

    * Point estimates from original
    use "$BOOT_DATA", clear
    quietly reghdfe `sm' hdd_ge32 ca SR_x_Heat_full D_full irr_frac gdd_ge10, ///
        absorb(grid_id year) vce(cluster grid_id)
    local pt_a1h = _b[hdd_ge32]
    local pt_a3h = _b[SR_x_Heat_full]

    quietly reghdfe ln_yield hdd_ge32 ca SR_x_Heat_full `sm' D_full irr_frac gdd_ge10, ///
        absorb(grid_id year) vce(cluster grid_id)
    local pt_b_h = _b[`sm']
    local pt_c1h = _b[hdd_ge32]
    local pt_c3h = _b[SR_x_Heat_full]

    local stat_idx = 0
    foreach sname in IE_P25 IE_P50 IE_P75 DE_P25 DE_P50 DE_P75 TE_P25 TE_P50 TE_P75 Index a1h a3h b_h {
        local ++stat_idx

        mata: st_matrix("__col", st_matrix("`bs_mat_h'")[., `stat_idx'])
        svmat double __col, names(__bs)

        qui count if !missing(__bs1)
        local n_valid = r(N)

        if "`sname'" == "IE_P25" local pt = (`pt_a1h' + `pt_a3h' * `ca_p25') * `pt_b_h'
        else if "`sname'" == "IE_P50" local pt = (`pt_a1h' + `pt_a3h' * `ca_p50') * `pt_b_h'
        else if "`sname'" == "IE_P75" local pt = (`pt_a1h' + `pt_a3h' * `ca_p75') * `pt_b_h'
        else if "`sname'" == "DE_P25" local pt = `pt_c1h' + `pt_c3h' * `ca_p25'
        else if "`sname'" == "DE_P50" local pt = `pt_c1h' + `pt_c3h' * `ca_p50'
        else if "`sname'" == "DE_P75" local pt = `pt_c1h' + `pt_c3h' * `ca_p75'
        else if "`sname'" == "TE_P25" local pt = (`pt_c1h' + `pt_c3h' * `ca_p25') + (`pt_a1h' + `pt_a3h' * `ca_p25') * `pt_b_h'
        else if "`sname'" == "TE_P50" local pt = (`pt_c1h' + `pt_c3h' * `ca_p50') + (`pt_a1h' + `pt_a3h' * `ca_p50') * `pt_b_h'
        else if "`sname'" == "TE_P75" local pt = (`pt_c1h' + `pt_c3h' * `ca_p75') + (`pt_a1h' + `pt_a3h' * `ca_p75') * `pt_b_h'
        else if "`sname'" == "Index" local pt = `pt_a3h' * `pt_b_h'
        else if "`sname'" == "a1h" local pt = `pt_a1h'
        else if "`sname'" == "a3h" local pt = `pt_a3h'
        else if "`sname'" == "b_h" local pt = `pt_b_h'

        qui sum __bs1 if !missing(__bs1)
        local bs_se = r(sd)

        sort __bs1
        local lo_idx = max(1, round(`n_valid' * 0.025))
        local hi_idx = min(`n_valid', round(`n_valid' * 0.975))
        local ci_lo = __bs1[`lo_idx']
        local ci_hi = __bs1[`hi_idx']

        local ca_lbl = ""
        if strpos("`sname'", "P25") local ca_lbl = "P25"
        else if strpos("`sname'", "P50") local ca_lbl = "P50"
        else if strpos("`sname'", "P75") local ca_lbl = "P75"
        else local ca_lbl = "all"

        local clean_stat = "`sname'"
        if "`ca_lbl'" != "all" {
            local clean_stat = subinstr("`sname'", "_`ca_lbl'", "", 1)
        }

        post `pf_h' ("`sm'") ("`clean_stat'") ("`ca_lbl'") ///
            (`pt') (`bs_se') (`ci_lo') (`ci_hi')

        drop __bs1
        cap matrix drop __col
    }
}

postclose `pf_h'

preserve
use "$outdir/v3med_bs_heat_raw.dta", clear
export delimited using "$outdir/v3med_bootstrap_heat.csv", replace
restore
cap erase "$outdir/v3med_bs_heat_raw.dta"

log close
di "=== v3med_step5_bootstrap.do COMPLETE ==="
