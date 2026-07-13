* =============================================================================
* v3decomp_step2_bootstrap.do
* Purpose: Cluster bootstrap for profile-specific decomposition statistics.
* Input:   data/processed/v3decomp_analysis_ready.dta
*          output/tables/v3decomp_profile_constants.dta
* Output:  output/tables/v3decomp_bootstrap_summary.csv
* =============================================================================

clear all
set more off
set seed 42

do "C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata/v3decomp_macros_include.do"

log using "$logdir/v3decomp_step2_bootstrap.log", replace

use "$decomp_panel", clear
keep if v3decomp_common_sample == 1
xtset, clear

count
local N_boot = r(N)
di "Bootstrap working sample N = `N_boot'"

tempfile boot_sample
save `boot_sample', replace
global DECOMP_BOOT_SAMPLE "`boot_sample'"

preserve
use "$decomp_profiles", clear
foreach p in $DECOMP_ALL_PROFILES {
    quietly summarize d if profile == "`p'", meanonly
    global DECOMP_D_`p' `=r(mean)'
    quietly summarize h if profile == "`p'", meanonly
    global DECOMP_H_`p' `=r(mean)'
    quietly summarize w if profile == "`p'", meanonly
    global DECOMP_W_`p' `=r(mean)'
}
restore

capture program drop run_v3decomp_bootstrap
program define run_v3decomp_bootstrap
    syntax, REPS(integer) RAWPATH(string) SUMMARYPATH(string) TAG(string)

    local med "$DECOMP_MEDIATOR"

    tempname raw_pf
    postfile `raw_pf' int rep str16 profile ///
        double a_hat b_hat DE DE_stress IE TE share ///
        using "`rawpath'", replace

    di "------------------------------------------------------------"
    di "Bootstrap tag = `tag' | reps = `reps'"
    di "------------------------------------------------------------"

    forvalues b = 1/`reps' {
        if mod(`b', 50) == 0 {
            di "." _continue
        }
        if mod(`b', 250) == 0 {
            di " `b'"
        }

        use "$DECOMP_BOOT_SAMPLE", clear
        bsample, cluster(grid_id) idcluster(boot_grid)

        capture quietly reghdfe `med' $DECOMP_L2_RHS $DECOMP_CTRL, ///
            absorb(boot_grid year) vce(cluster boot_grid)

        if _rc == 0 {
            local ok_l2 = 1
            local pi_sr = _b[ca]
            local lam_d = _b[SR_x_D_full]
            local lam_h = _b[SR_x_Heat_full]
            local lam_w = _b[SR_x_W_full]
            local lam_dh = _b[SR_x_D_x_Heat_full]
        }
        else {
            local ok_l2 = 0
        }

        capture quietly reghdfe ln_yield $DECOMP_L3_RHS $DECOMP_CTRL, ///
            absorb(boot_grid year) vce(cluster boot_grid)

        if _rc == 0 {
            local ok_l3 = 1
            local beta_sr = _b[ca]
            local th_d    = _b[SR_x_D_full]
            local th_h    = _b[SR_x_Heat_full]
            local th_w    = _b[SR_x_W_full]
            local th_dh   = _b[SR_x_D_x_Heat_full]
            local delta   = _b[`med']
            local phi_d   = _b[SM_x_D_full]
            local phi_h   = _b[SM_x_H_full]
        }
        else {
            local ok_l3 = 0
        }

        foreach p in $DECOMP_ALL_PROFILES {
            if `ok_l2' == 1 & `ok_l3' == 1 {
                local d = ${DECOMP_D_`p'}
                local h = ${DECOMP_H_`p'}
                local w = ${DECOMP_W_`p'}

                local a_hat = `pi_sr' + `lam_d' * `d' + `lam_h' * `h' + `lam_w' * `w' + `lam_dh' * `d' * `h'
                local b_hat = `delta' + `phi_d' * `d' + `phi_h' * `h'
                local DE = `beta_sr' + `th_d' * `d' + `th_h' * `h' + `th_w' * `w' + `th_dh' * `d' * `h'
                local DE_stress = `th_d' * `d' + `th_h' * `h' + `th_w' * `w' + `th_dh' * `d' * `h'
                local IE = `a_hat' * `b_hat'
                local TE = `DE' + `IE'
                local share = .
                if abs(`TE') >= 1e-8 {
                    local share = `IE' / `TE'
                }
            }
            else {
                local a_hat = .
                local b_hat = .
                local DE = .
                local DE_stress = .
                local IE = .
                local TE = .
                local share = .
            }

            post `raw_pf' (`b') ("`p'") (`a_hat') (`b_hat') (`DE') ///
                (`DE_stress') (`IE') (`TE') (`share')
        }
    }

    di ""
    postclose `raw_pf'

    preserve
    use "`rawpath'", clear

    tempname sum_pf
    postfile `sum_pf' str16 profile str16 stat ///
        double mean se ci_lo ci_hi reps ///
        using "`summarypath'", replace

    foreach p in $DECOMP_ALL_PROFILES {
        foreach s in a_hat b_hat DE DE_stress IE TE share {
            quietly count if profile == "`p'" & !missing(`s')
            local reps_ok = r(N)

            if `reps_ok' > 0 {
                quietly summarize `s' if profile == "`p'" & !missing(`s')
                local stat_mean = r(mean)
                local stat_se   = r(sd)
                quietly _pctile `s' if profile == "`p'" & !missing(`s'), p(2.5 97.5)
                local ci_lo = r(r1)
                local ci_hi = r(r2)
            }
            else {
                local stat_mean = .
                local stat_se   = .
                local ci_lo = .
                local ci_hi = .
            }

            post `sum_pf' ("`p'") ("`s'") (`stat_mean') (`stat_se') ///
                (`ci_lo') (`ci_hi') (`reps_ok')
        }
    }

    postclose `sum_pf'
    restore
end

run_v3decomp_bootstrap, reps(100) ///
    rawpath("$decomp_boot_dryrun_dta") ///
    summarypath("$decomp_boot_dryrun_sum") ///
    tag("dryrun")

run_v3decomp_bootstrap, reps(1000) ///
    rawpath("$decomp_boot_reps_dta") ///
    summarypath("$decomp_boot_summary_dta") ///
    tag("final")

preserve
use "$decomp_boot_dryrun_sum", clear
format mean se ci_lo ci_hi %9.6f
format reps %12.0f
export delimited using "$decomp_boot_dryrun_csv", replace
restore

preserve
use "$decomp_boot_summary_dta", clear
format mean se ci_lo ci_hi %9.6f
format reps %12.0f
sort profile stat
list if inlist(stat, "DE", "IE", "TE"), noobs sepby(profile)
export delimited using "$decomp_boot_summary_csv", replace
restore

log close
di "=== v3decomp_step2_bootstrap.do COMPLETE ==="
