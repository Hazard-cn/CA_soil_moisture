* =============================================================================
* ggcp10_mean_ext_run_all.do
* Purpose: GLEAM SM mean extension: baseline, bootstrap, heterogeneity.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global rundir "$projdir/temp/2026-05-19_ggcp10_mediation_extensions/mean"
global logdir "$rundir/logs"
global basedta "$projdir/temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_baseline_suite_analysis_ready.dta"
global builddir "$projdir/data_build/data/processed"
global coefcsv "$rundir/ggcp10_mean_baseline_coefficients.csv"
global bootcsv "$rundir/ggcp10_mean_bootstrap_iede.csv"
global hetcoefcsv "$rundir/ggcp10_mean_heterogeneity_coefficients.csv"
global heteffcsv "$rundir/ggcp10_mean_heterogeneity_effects.csv"
global V6_CTRL_FULL "hdd_ge32 pr_sum et0_sum gdd_10_30 irr_frac aridity"
global CTRL_NOHEAT "pr_sum et0_sum gdd_10_30 irr_frac aridity"
global ZONE_LIST "NE HHH SW SH NW Other"
global IRR_LIST "low_irr high_irr"
global BOOT_REPS "80"

cap mkdir "$projdir/temp/2026-05-19_ggcp10_mediation_extensions"
cap mkdir "$rundir"
cap mkdir "$logdir"

cap log close master
log using "$logdir/ggcp10_mean_ext_run_all.log", replace text name(master)

use "$basedta", clear
xtset grid_id year
xtset, clear

merge 1:1 grid_id year using "$builddir/data_v3_main.dta", ///
    keepusing(hotdrydays_ge32_pr_lt1 hotdrydays_ge32_pr_lt1_v3pre30 ///
              hotdrydays_ge32_pr_lt1_v3he hotdrydays_ge32_pr_lt1_hema) ///
    keep(master match)
assert _merge == 3
drop _merge

gen HotDryPr_full = hotdrydays_ge32_pr_lt1
gen HotDryPr_v3pre30 = hotdrydays_ge32_pr_lt1_v3pre30
gen HotDryPr_v3he = hotdrydays_ge32_pr_lt1_v3he
gen HotDryPr_hema = hotdrydays_ge32_pr_lt1_hema
gen SR_x_HotDryPr_full = ca * HotDryPr_full
gen SR_x_HotDryPr_v3pre30 = ca * HotDryPr_v3pre30
gen SR_x_HotDryPr_v3he = ca * HotDryPr_v3he
gen SR_x_HotDryPr_hema = ca * HotDryPr_hema

tempname pf
postfile `pf' str12 hazard str12 window str16 source_layer str12 sm_label ///
    str20 mediator str12 equation str16 term str28 regressor ///
    double(b se p) long(N) double(r2) using "$rundir/mean_coef_raw.dta", replace
global MEAN_COEF_POST_HANDLE "`pf'"

capture program drop mean_fit
program define mean_fit
    syntax, HAZARD(string) WINDOW(string) SLAYER(string) SMLABEL(string) ///
        MEDIATOR(name) DVAR(name) WVAR(name) SRDVAR(name) HDVAR(name) SRHDVAR(name)

    gen byte __sample = (main_sample == 1)
    foreach v in ln_yield ca `mediator' `dvar' `wvar' `srdvar' hdd_ge32 ///
        SR_x_Heat_full `hdvar' `srhdvar' pr_sum et0_sum gdd_10_30 irr_frac aridity {
        replace __sample = 0 if missing(`v') & __sample == 1
    }

    local rhs_m ""
    local rhs_y ""
    local pairs ""
    if "`hazard'" == "drought" {
        local rhs_m "`dvar' ca `srdvar' `wvar' $V6_CTRL_FULL"
        local rhs_y "`dvar' ca `srdvar' `mediator' `wvar' $V6_CTRL_FULL"
        local pairs `" "Main `dvar'" "SR_x_Main `srdvar'" "M `mediator'" "'
    }
    if "`hazard'" == "heat" {
        local rhs_m "hdd_ge32 ca SR_x_Heat_full `dvar' `wvar' $CTRL_NOHEAT"
        local rhs_y "hdd_ge32 ca SR_x_Heat_full `mediator' `dvar' `wvar' $CTRL_NOHEAT"
        local pairs `" "Main hdd_ge32" "SR_x_Main SR_x_Heat_full" "M `mediator'" "'
    }
    if "`hazard'" == "hotdry" {
        local rhs_m "`hdvar' ca `srhdvar' `dvar' hdd_ge32 `wvar' $CTRL_NOHEAT"
        local rhs_y "`hdvar' ca `srhdvar' `mediator' `dvar' hdd_ge32 `wvar' $CTRL_NOHEAT"
        local pairs `" "Main `hdvar'" "SR_x_Main `srhdvar'" "M `mediator'" "'
    }

    reghdfe `mediator' `rhs_m' if __sample == 1, absorb(grid_id year) vce(cluster grid_id)
    local nn_m = e(N)
    local rr_m = e(r2)
    foreach pair of local pairs {
        gettoken term reg : pair
        if "`term'" != "M" {
            local pval = 2 * ttail(e(df_r), abs(_b[`reg'] / _se[`reg']))
            post $MEAN_COEF_POST_HANDLE ("`hazard'") ("`window'") ("`slayer'") ("`smlabel'") ///
                ("`mediator'") ("mediator") ("`term'") ("`reg'") ///
                (_b[`reg']) (_se[`reg']) (`pval') (`nn_m') (`rr_m')
        }
    }

    reghdfe ln_yield `rhs_y' if __sample == 1, absorb(grid_id year) vce(cluster grid_id)
    local nn_y = e(N)
    local rr_y = e(r2)
    foreach pair of local pairs {
        gettoken term reg : pair
        local pval = 2 * ttail(e(df_r), abs(_b[`reg'] / _se[`reg']))
        post $MEAN_COEF_POST_HANDLE ("`hazard'") ("`window'") ("`slayer'") ("`smlabel'") ///
            ("`mediator'") ("outcome") ("`term'") ("`reg'") ///
            (_b[`reg']) (_se[`reg']) (`pval') (`nn_y') (`rr_y')
    }
    drop __sample
end

foreach w in v3pre30 v3he hema fullnew {
    local raw_sfx "_v3pre30"
    local dvar "D_v3pre30"
    local wvar "W_v3pre30"
    local srdvar "SR_x_D_v3pre30"
    local hdvar "HotDryPr_v3pre30"
    local srhdvar "SR_x_HotDryPr_v3pre30"
    if "`w'" == "v3he" {
        local raw_sfx "_v3he"
        local dvar "D_v3he"
        local wvar "W_v3he"
        local srdvar "SR_x_D_v3he"
        local hdvar "HotDryPr_v3he"
        local srhdvar "SR_x_HotDryPr_v3he"
    }
    if "`w'" == "hema" {
        local raw_sfx "_hema"
        local dvar "D_hema"
        local wvar "W_hema"
        local srdvar "SR_x_D_hema"
        local hdvar "HotDryPr_hema"
        local srhdvar "SR_x_HotDryPr_hema"
    }
    if "`w'" == "fullnew" {
        local raw_sfx ""
        local dvar "D_full"
        local wvar "W_full"
        local srdvar "SR_x_D_full"
        local hdvar "HotDryPr_full"
        local srhdvar "SR_x_HotDryPr_full"
    }
    foreach src in surface rootzone {
        local med "gleam_sms_mean`raw_sfx'"
        local slayer "gleam_surface"
        local sm "GLEAM-Sfc"
        if "`src'" == "rootzone" {
            local med "gleam_smrz_mean`raw_sfx'"
            local slayer "gleam_rootzone"
            local sm "GLEAM-Root"
        }
        foreach haz in drought heat hotdry {
            mean_fit, hazard(`haz') window(`w') slayer(`slayer') smlabel(`sm') ///
                mediator(`med') dvar(`dvar') wvar(`wvar') srdvar(`srdvar') ///
                hdvar(`hdvar') srhdvar(`srhdvar')
        }
    }
}
postclose `pf'
preserve
use "$rundir/mean_coef_raw.dta", clear
export delimited using "$coefcsv", replace
restore

* Bootstrap and heterogeneity for full equations.
tempname pb ph pe
postfile `pb' str12 hazard str12 window str16 source_layer str12 sm_label ///
    str2 effect str4 ca_level double(point_est bs_se ci_lo ci_hi) long(N_boot) ///
    using "$rundir/mean_boot_raw.dta", replace
postfile `ph' str12 hazard str10 split_type str12 subgroup str12 window ///
    str16 source_layer str12 sm_label str12 equation str16 term ///
    double(b se p) long(N) double(r2) using "$rundir/mean_hetcoef_raw.dta", replace
postfile `pe' str12 hazard str10 split_type str12 subgroup str12 window ///
    str16 source_layer str12 sm_label str2 effect str4 ca_level ///
    double(ca_value value) using "$rundir/mean_heteff_raw.dta", replace

capture program drop mean_boot
program define mean_boot, rclass
    args hazard mediator dvar wvar srdvar hdvar srhdvar
    local abs_id "grid_id"
    capture confirm variable boot_grid
    if _rc == 0 local abs_id "boot_grid"
    local rhs_m ""
    local rhs_y ""
    local main ""
    local inter ""
    if "`hazard'" == "drought" {
        local rhs_m "`dvar' ca `srdvar' `wvar' $V6_CTRL_FULL"
        local rhs_y "`dvar' ca `srdvar' `mediator' `wvar' $V6_CTRL_FULL"
        local main "`dvar'"
        local inter "`srdvar'"
    }
    if "`hazard'" == "heat" {
        local rhs_m "hdd_ge32 ca SR_x_Heat_full `dvar' `wvar' $CTRL_NOHEAT"
        local rhs_y "hdd_ge32 ca SR_x_Heat_full `mediator' `dvar' `wvar' $CTRL_NOHEAT"
        local main "hdd_ge32"
        local inter "SR_x_Heat_full"
    }
    if "`hazard'" == "hotdry" {
        local rhs_m "`hdvar' ca `srhdvar' `dvar' hdd_ge32 `wvar' $CTRL_NOHEAT"
        local rhs_y "`hdvar' ca `srhdvar' `mediator' `dvar' hdd_ge32 `wvar' $CTRL_NOHEAT"
        local main "`hdvar'"
        local inter "`srhdvar'"
    }
    capture quietly reghdfe `mediator' `rhs_m', absorb(`abs_id' year) vce(cluster `abs_id')
    if _rc != 0 exit
    local a1 = _b[`main']
    local a3 = _b[`inter']
    capture quietly reghdfe ln_yield `rhs_y', absorb(`abs_id' year) vce(cluster `abs_id')
    if _rc != 0 exit
    local b = _b[`mediator']
    local c1 = _b[`main']
    local c3 = _b[`inter']
    foreach q in 25 50 75 {
        local r = $MEAN_CA_P`q'
        local ie = (`a1' + `a3' * `r') * `b'
        local de = `c1' + `c3' * `r'
        return scalar ie`q' = `ie'
        return scalar de`q' = `de'
        return scalar te`q' = `ie' + `de'
    }
end

foreach w in v3pre30 v3he hema fullnew {
    local raw_sfx "_v3pre30"
    local dvar "D_v3pre30"
    local wvar "W_v3pre30"
    local srdvar "SR_x_D_v3pre30"
    local hdvar "HotDryPr_v3pre30"
    local srhdvar "SR_x_HotDryPr_v3pre30"
    if "`w'" == "v3he" {
        local raw_sfx "_v3he"
        local dvar "D_v3he"
        local wvar "W_v3he"
        local srdvar "SR_x_D_v3he"
        local hdvar "HotDryPr_v3he"
        local srhdvar "SR_x_HotDryPr_v3he"
    }
    if "`w'" == "hema" {
        local raw_sfx "_hema"
        local dvar "D_hema"
        local wvar "W_hema"
        local srdvar "SR_x_D_hema"
        local hdvar "HotDryPr_hema"
        local srhdvar "SR_x_HotDryPr_hema"
    }
    if "`w'" == "fullnew" {
        local raw_sfx ""
        local dvar "D_full"
        local wvar "W_full"
        local srdvar "SR_x_D_full"
        local hdvar "HotDryPr_full"
        local srhdvar "SR_x_HotDryPr_full"
    }
    foreach src in surface rootzone {
        local med "gleam_sms_mean`raw_sfx'"
        local slayer "gleam_surface"
        local sm "GLEAM-Sfc"
        if "`src'" == "rootzone" {
            local med "gleam_smrz_mean`raw_sfx'"
            local slayer "gleam_rootzone"
            local sm "GLEAM-Root"
        }
        foreach haz in drought heat hotdry {
            preserve
            gen byte __sample = (main_sample == 1)
            foreach v in ln_yield ca `med' `dvar' `wvar' `srdvar' hdd_ge32 ///
                SR_x_Heat_full `hdvar' `srhdvar' pr_sum et0_sum gdd_10_30 irr_frac aridity {
                replace __sample = 0 if missing(`v') & __sample == 1
            }
            keep if __sample == 1
            _pctile ca, p(25 50 75)
            global MEAN_CA_P25 = r(r1)
            global MEAN_CA_P50 = r(r2)
            global MEAN_CA_P75 = r(r3)
            bootstrap ie25=r(ie25) ie50=r(ie50) ie75=r(ie75) ///
                de25=r(de25) de50=r(de50) de75=r(de75) ///
                te25=r(te25) te50=r(te50) te75=r(te75), ///
                reps($BOOT_REPS) cluster(grid_id) idcluster(boot_grid) nodots: ///
                mean_boot `haz' `med' `dvar' `wvar' `srdvar' `hdvar' `srhdvar'
            estat bootstrap, bc
            matrix bcCI = r(ci_bc)
            matrix pe = e(b)
            matrix vv = e(V)
            local stats "ie25 ie50 ie75 de25 de50 de75 te25 te50 te75"
            local j = 0
            foreach sname of local stats {
                local ++j
                local point = pe[1,`j']
                local bs = sqrt(vv[`j',`j'])
                local effect = upper(substr("`sname'",1,2))
                local lvl = substr("`sname'",3,.)
                scalar __ll = .
                scalar __ul = .
                capture scalar __ll = bcCI[`j',1]
                capture scalar __ul = bcCI[`j',2]
                local ll = scalar(__ll)
                local ul = scalar(__ul)
                if missing(`ll') | missing(`ul') {
                    local ll = `point' - 1.96*`bs'
                    local ul = `point' + 1.96*`bs'
                }
                post `pb' ("`haz'") ("`w'") ("`slayer'") ("`sm'") ///
                    ("`effect'") ("P`lvl'") (`point') (`bs') ///
                    (`ll') (`ul') ($BOOT_REPS)
            }
            restore

            foreach split in irr zone {
                local groups "$IRR_LIST"
                local splitvar "irr_group"
                if "`split'" == "zone" {
                    local groups "$ZONE_LIST"
                    local splitvar "maize_zone"
                }
                foreach g of local groups {
                    preserve
                    keep if `splitvar' == "`g'"
                    gen byte __sample = (main_sample == 1)
                    foreach v in ln_yield ca `med' `dvar' `wvar' `srdvar' hdd_ge32 ///
                        SR_x_Heat_full `hdvar' `srhdvar' pr_sum et0_sum gdd_10_30 irr_frac aridity {
                        replace __sample = 0 if missing(`v') & __sample == 1
                    }
                    keep if __sample == 1
                    count
                    if r(N) < 500 {
                        restore
                        continue
                    }
                    _pctile ca, p(50)
                    local cap50 = r(r1)
                    local rhs_m ""
                    local rhs_y ""
                    local main ""
                    local inter ""
                    if "`haz'" == "drought" {
                        local rhs_m "`dvar' ca `srdvar' `wvar' $V6_CTRL_FULL"
                        local rhs_y "`dvar' ca `srdvar' `med' `wvar' $V6_CTRL_FULL"
                        local main "`dvar'"
                        local inter "`srdvar'"
                    }
                    if "`haz'" == "heat" {
                        local rhs_m "hdd_ge32 ca SR_x_Heat_full `dvar' `wvar' $CTRL_NOHEAT"
                        local rhs_y "hdd_ge32 ca SR_x_Heat_full `med' `dvar' `wvar' $CTRL_NOHEAT"
                        local main "hdd_ge32"
                        local inter "SR_x_Heat_full"
                    }
                    if "`haz'" == "hotdry" {
                        local rhs_m "`hdvar' ca `srhdvar' `dvar' hdd_ge32 `wvar' $CTRL_NOHEAT"
                        local rhs_y "`hdvar' ca `srhdvar' `med' `dvar' hdd_ge32 `wvar' $CTRL_NOHEAT"
                        local main "`hdvar'"
                        local inter "`srhdvar'"
                    }
                    reghdfe `med' `rhs_m', absorb(grid_id year) vce(cluster grid_id)
                    local a1 = _b[`main']
                    local a3 = _b[`inter']
                    foreach pair in "Main `main'" "SR_x_Main `inter'" {
                        gettoken term reg : pair
                        local pval = 2 * ttail(e(df_r), abs(_b[`reg']/_se[`reg']))
                        post `ph' ("`haz'") ("`split'") ("`g'") ("`w'") ("`slayer'") ("`sm'") ///
                            ("mediator") ("`term'") (_b[`reg']) (_se[`reg']) (`pval') (e(N)) (e(r2))
                    }
                    reghdfe ln_yield `rhs_y', absorb(grid_id year) vce(cluster grid_id)
                    local b = _b[`med']
                    local c1 = _b[`main']
                    local c3 = _b[`inter']
                    foreach pair in "Main `main'" "SR_x_Main `inter'" "M `med'" {
                        gettoken term reg : pair
                        local pval = 2 * ttail(e(df_r), abs(_b[`reg']/_se[`reg']))
                        post `ph' ("`haz'") ("`split'") ("`g'") ("`w'") ("`slayer'") ("`sm'") ///
                            ("outcome") ("`term'") (_b[`reg']) (_se[`reg']) (`pval') (e(N)) (e(r2))
                    }
                    local ie = (`a1' + `a3' * `cap50') * `b'
                    local de = `c1' + `c3' * `cap50'
                    post `pe' ("`haz'") ("`split'") ("`g'") ("`w'") ("`slayer'") ("`sm'") ///
                        ("IE") ("P50") (`cap50') (`ie')
                    post `pe' ("`haz'") ("`split'") ("`g'") ("`w'") ("`slayer'") ("`sm'") ///
                        ("DE") ("P50") (`cap50') (`de')
                    restore
                }
            }
        }
    }
}

postclose `pb'
postclose `ph'
postclose `pe'
preserve
use "$rundir/mean_boot_raw.dta", clear
export delimited using "$bootcsv", replace
restore
preserve
use "$rundir/mean_hetcoef_raw.dta", clear
export delimited using "$hetcoefcsv", replace
restore
preserve
use "$rundir/mean_heteff_raw.dta", clear
export delimited using "$heteffcsv", replace
restore

di "=== ggcp10_mean_ext_run_all.do COMPLETE ==="
log close master
