* =============================================================================
* ggcp10_dry_top3_ext_run_all.do
* Purpose: Three selected GLEAM dry-state mediators: baseline, bootstrap, het.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global rundir "$projdir/temp/2026-05-19_ggcp10_mediation_extensions/dry_top3"
global logdir "$rundir/logs"
global basedta "$projdir/temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_baseline_suite_analysis_ready.dta"
global builddir "$projdir/data_build/data/processed"
global coefcsv "$rundir/ggcp10_dry_top3_baseline_coefficients.csv"
global bootcsv "$rundir/ggcp10_dry_top3_bootstrap_iede.csv"
global hetcoefcsv "$rundir/ggcp10_dry_top3_heterogeneity_coefficients.csv"
global heteffcsv "$rundir/ggcp10_dry_top3_heterogeneity_effects.csv"
global V6_CTRL_FULL "hdd_ge32 pr_sum et0_sum gdd_10_30 irr_frac aridity"
global CTRL_NOHEAT "pr_sum et0_sum gdd_10_30 irr_frac aridity"
global ZONE_LIST "NE HHH SW SH NW Other"
global IRR_LIST "low_irr high_irr"
global BOOT_REPS "80"

cap mkdir "$projdir/temp/2026-05-19_ggcp10_mediation_extensions"
cap mkdir "$rundir"
cap mkdir "$logdir"

cap log close master
log using "$logdir/ggcp10_dry_top3_ext_run_all.log", replace text name(master)

use "$basedta", clear
xtset grid_id year
xtset, clear

merge 1:1 grid_id year using "$builddir/data_v3_main.dta", ///
    keepusing(hotdrydays_ge32_pr_lt1) keep(master match)
assert _merge == 3
drop _merge

gen HotDryPr_full = hotdrydays_ge32_pr_lt1
gen SR_x_HotDryPr_full = ca * HotDryPr_full

tempname ps pf pb ph pe
postfile `ps' int(rank) str24 metric_family str4 dry_pct str16 source_layer ///
    str12 sm_label str20 sample_tag str24 mediator str40 selection_basis ///
    using "$rundir/dry_top3_selection_raw.dta", replace
postfile `pf' str12 hazard str24 metric_family str4 dry_pct str16 source_layer ///
    str12 sm_label str20 sample_tag str24 mediator str12 equation str16 term ///
    str28 regressor double(b se p) long(N) double(r2) ///
    using "$rundir/dry_top3_coef_raw.dta", replace
postfile `pb' str12 hazard str24 metric_family str4 dry_pct str16 source_layer ///
    str12 sm_label str20 sample_tag str2 effect str4 ca_level ///
    double(point_est bs_se ci_lo ci_hi) long(N_boot) ///
    using "$rundir/dry_top3_boot_raw.dta", replace
postfile `ph' str12 hazard str10 split_type str12 subgroup str24 metric_family ///
    str4 dry_pct str16 source_layer str12 sm_label str20 sample_tag str12 equation ///
    str16 term double(b se p) long(N) double(r2) ///
    using "$rundir/dry_top3_hetcoef_raw.dta", replace
postfile `pe' str12 hazard str10 split_type str12 subgroup str24 metric_family ///
    str4 dry_pct str16 source_layer str12 sm_label str20 sample_tag str2 effect ///
    str4 ca_level double(ca_value value) ///
    using "$rundir/dry_top3_heteff_raw.dta", replace
global DRY_TOP3_POST_HANDLE "`pf'"

post `ps' (1) ("blseveritymean_ddf") ("p10") ("gleam_surface") ///
    ("GLEAM-Sfc") ("mdf_p10_fn") ("v6mdf_p10_fn_gss") ("expected_sign_stability_9of9")
post `ps' (2) ("blseveritysum_ddf") ("p10") ("gleam_rootzone") ///
    ("GLEAM-Root") ("sdf_p10_fn") ("v6sdf_p10_fn_gsr") ("expected_sign_stability_9of9")
post `ps' (3) ("blduration_dry") ("p10") ("gleam_surface") ///
    ("GLEAM-Sfc") ("dur_p10_fn") ("v6dur_p10_fn_gss") ("expected_sign_stability_8of9")
postclose `ps'

capture program drop dry_top3_fit
program define dry_top3_fit
    syntax, HAZARD(string) MEDIATOR(name) FAMILY(string) DP(string) ///
        SLAYER(string) SMLABEL(string) TAG(string) SAMPLEVAR(name)

    local rhs_m ""
    local rhs_y ""
    local pairs ""
    if "`hazard'" == "drought" {
        local rhs_m "D_full ca SR_x_D_full W_full $V6_CTRL_FULL"
        local rhs_y "D_full ca SR_x_D_full `mediator' W_full $V6_CTRL_FULL"
        local pairs `" "Main D_full" "SR_x_Main SR_x_D_full" "M `mediator'" "'
    }
    if "`hazard'" == "heat" {
        local rhs_m "hdd_ge32 ca SR_x_Heat_full D_full W_full $CTRL_NOHEAT"
        local rhs_y "hdd_ge32 ca SR_x_Heat_full `mediator' D_full W_full $CTRL_NOHEAT"
        local pairs `" "Main hdd_ge32" "SR_x_Main SR_x_Heat_full" "M `mediator'" "'
    }
    if "`hazard'" == "hotdry" {
        local rhs_m "HotDryPr_full ca SR_x_HotDryPr_full D_full hdd_ge32 W_full $CTRL_NOHEAT"
        local rhs_y "HotDryPr_full ca SR_x_HotDryPr_full `mediator' D_full hdd_ge32 W_full $CTRL_NOHEAT"
        local pairs `" "Main HotDryPr_full" "SR_x_Main SR_x_HotDryPr_full" "M `mediator'" "'
    }

    reghdfe `mediator' `rhs_m' if `samplevar' == 1, absorb(grid_id year) vce(cluster grid_id)
    local nn_m = e(N)
    local rr_m = e(r2)
    foreach pair of local pairs {
        gettoken term reg : pair
        if "`term'" != "M" {
            local pval = 2 * ttail(e(df_r), abs(_b[`reg'] / _se[`reg']))
            post $DRY_TOP3_POST_HANDLE ("`hazard'") ("`family'") ("`dp'") ("`slayer'") ///
                ("`smlabel'") ("`tag'") ("`mediator'") ("mediator") ("`term'") ///
                ("`reg'") (_b[`reg']) (_se[`reg']) (`pval') (`nn_m') (`rr_m')
        }
    }

    reghdfe ln_yield `rhs_y' if `samplevar' == 1, absorb(grid_id year) vce(cluster grid_id)
    local nn_y = e(N)
    local rr_y = e(r2)
    foreach pair of local pairs {
        gettoken term reg : pair
        local pval = 2 * ttail(e(df_r), abs(_b[`reg'] / _se[`reg']))
        post $DRY_TOP3_POST_HANDLE ("`hazard'") ("`family'") ("`dp'") ("`slayer'") ///
            ("`smlabel'") ("`tag'") ("`mediator'") ("outcome") ("`term'") ///
            ("`reg'") (_b[`reg']) (_se[`reg']) (`pval') (`nn_y') (`rr_y')
    }
end

capture program drop dry_top3_boot
program define dry_top3_boot, rclass
    args hazard mediator
    local abs_id "grid_id"
    capture confirm variable boot_grid
    if _rc == 0 local abs_id "boot_grid"
    local rhs_m ""
    local rhs_y ""
    local main ""
    local inter ""
    if "`hazard'" == "drought" {
        local rhs_m "D_full ca SR_x_D_full W_full $V6_CTRL_FULL"
        local rhs_y "D_full ca SR_x_D_full `mediator' W_full $V6_CTRL_FULL"
        local main "D_full"
        local inter "SR_x_D_full"
    }
    if "`hazard'" == "heat" {
        local rhs_m "hdd_ge32 ca SR_x_Heat_full D_full W_full $CTRL_NOHEAT"
        local rhs_y "hdd_ge32 ca SR_x_Heat_full `mediator' D_full W_full $CTRL_NOHEAT"
        local main "hdd_ge32"
        local inter "SR_x_Heat_full"
    }
    if "`hazard'" == "hotdry" {
        local rhs_m "HotDryPr_full ca SR_x_HotDryPr_full D_full hdd_ge32 W_full $CTRL_NOHEAT"
        local rhs_y "HotDryPr_full ca SR_x_HotDryPr_full `mediator' D_full hdd_ge32 W_full $CTRL_NOHEAT"
        local main "HotDryPr_full"
        local inter "SR_x_HotDryPr_full"
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
        local r = $DRY_TOP3_CA_P`q'
        return scalar ie`q' = (`a1' + `a3' * `r') * `b'
        return scalar de`q' = `c1' + `c3' * `r'
    }
end

local fam1 "blseveritymean_ddf"
local dp1 "p10"
local layer1 "gleam_surface"
local sm1 "GLEAM-Sfc"
local tag1 "mdf_p10_fn"
local med1 "v6mdf_p10_fn_gss"
local sample1 "v6s_mdf_p10_fn"
local fam2 "blseveritysum_ddf"
local dp2 "p10"
local layer2 "gleam_rootzone"
local sm2 "GLEAM-Root"
local tag2 "sdf_p10_fn"
local med2 "v6sdf_p10_fn_gsr"
local sample2 "v6s_sdf_p10_fn"
local fam3 "blduration_dry"
local dp3 "p10"
local layer3 "gleam_surface"
local sm3 "GLEAM-Sfc"
local tag3 "dur_p10_fn"
local med3 "v6dur_p10_fn_gss"
local sample3 "v6s_dur_p10_fn"

forvalues i = 1/3 {
    local fam "`fam`i''"
    local dp "`dp`i''"
    local layer "`layer`i''"
    local sm "`sm`i''"
    local tag "`tag`i''"
    local med "`med`i''"
    local sample "`sample`i''"

    foreach haz in drought heat hotdry {
        dry_top3_fit, hazard(`haz') mediator(`med') family(`fam') dp(`dp') ///
            slayer(`layer') smlabel(`sm') tag(`tag') samplevar(`sample')

        preserve
        keep if `sample' == 1
        _pctile ca, p(25 50 75)
        global DRY_TOP3_CA_P25 = r(r1)
        global DRY_TOP3_CA_P50 = r(r2)
        global DRY_TOP3_CA_P75 = r(r3)
        bootstrap ie25=r(ie25) ie50=r(ie50) ie75=r(ie75) ///
            de25=r(de25) de50=r(de50) de75=r(de75), ///
            reps($BOOT_REPS) cluster(grid_id) idcluster(boot_grid) nodots: ///
            dry_top3_boot `haz' `med'
        estat bootstrap, bc
        matrix bcCI = r(ci_bc)
        matrix pe = e(b)
        matrix vv = e(V)
        local stats "ie25 ie50 ie75 de25 de50 de75"
        local j = 0
        foreach sname of local stats {
            local ++j
            local point = pe[1,`j']
            local bs = sqrt(vv[`j',`j'])
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
            local effect = upper(substr("`sname'",1,2))
            local lvl = substr("`sname'",3,.)
            post `pb' ("`haz'") ("`fam'") ("`dp'") ("`layer'") ("`sm'") ///
                ("`tag'") ("`effect'") ("P`lvl'") (`point') (`bs') (`ll') (`ul') ($BOOT_REPS)
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
                keep if `splitvar' == "`g'" & `sample' == 1
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
                    local rhs_m "D_full ca SR_x_D_full W_full $V6_CTRL_FULL"
                    local rhs_y "D_full ca SR_x_D_full `med' W_full $V6_CTRL_FULL"
                    local main "D_full"
                    local inter "SR_x_D_full"
                }
                if "`haz'" == "heat" {
                    local rhs_m "hdd_ge32 ca SR_x_Heat_full D_full W_full $CTRL_NOHEAT"
                    local rhs_y "hdd_ge32 ca SR_x_Heat_full `med' D_full W_full $CTRL_NOHEAT"
                    local main "hdd_ge32"
                    local inter "SR_x_Heat_full"
                }
                if "`haz'" == "hotdry" {
                    local rhs_m "HotDryPr_full ca SR_x_HotDryPr_full D_full hdd_ge32 W_full $CTRL_NOHEAT"
                    local rhs_y "HotDryPr_full ca SR_x_HotDryPr_full `med' D_full hdd_ge32 W_full $CTRL_NOHEAT"
                    local main "HotDryPr_full"
                    local inter "SR_x_HotDryPr_full"
                }
                reghdfe `med' `rhs_m', absorb(grid_id year) vce(cluster grid_id)
                local a1 = _b[`main']
                local a3 = _b[`inter']
                foreach pair in "Main `main'" "SR_x_Main `inter'" {
                    gettoken term reg : pair
                    local pval = 2 * ttail(e(df_r), abs(_b[`reg']/_se[`reg']))
                    post `ph' ("`haz'") ("`split'") ("`g'") ("`fam'") ("`dp'") ///
                        ("`layer'") ("`sm'") ("`tag'") ("mediator") ("`term'") ///
                        (_b[`reg']) (_se[`reg']) (`pval') (e(N)) (e(r2))
                }
                reghdfe ln_yield `rhs_y', absorb(grid_id year) vce(cluster grid_id)
                local b = _b[`med']
                local c1 = _b[`main']
                local c3 = _b[`inter']
                foreach pair in "Main `main'" "SR_x_Main `inter'" "M `med'" {
                    gettoken term reg : pair
                    local pval = 2 * ttail(e(df_r), abs(_b[`reg']/_se[`reg']))
                    post `ph' ("`haz'") ("`split'") ("`g'") ("`fam'") ("`dp'") ///
                        ("`layer'") ("`sm'") ("`tag'") ("outcome") ("`term'") ///
                        (_b[`reg']) (_se[`reg']) (`pval') (e(N)) (e(r2))
                }
                local ie = (`a1' + `a3' * `cap50') * `b'
                local de = `c1' + `c3' * `cap50'
                post `pe' ("`haz'") ("`split'") ("`g'") ("`fam'") ("`dp'") ///
                    ("`layer'") ("`sm'") ("`tag'") ("IE") ("P50") (`cap50') (`ie')
                post `pe' ("`haz'") ("`split'") ("`g'") ("`fam'") ("`dp'") ///
                    ("`layer'") ("`sm'") ("`tag'") ("DE") ("P50") (`cap50') (`de')
                restore
            }
        }
    }
}

postclose `pf'
postclose `pb'
postclose `ph'
postclose `pe'

preserve
use "$rundir/dry_top3_selection_raw.dta", clear
export delimited using "$rundir/ggcp10_dry_top3_selection.csv", replace
restore
preserve
use "$rundir/dry_top3_coef_raw.dta", clear
export delimited using "$coefcsv", replace
restore
preserve
use "$rundir/dry_top3_boot_raw.dta", clear
export delimited using "$bootcsv", replace
restore
preserve
use "$rundir/dry_top3_hetcoef_raw.dta", clear
export delimited using "$hetcoefcsv", replace
restore
preserve
use "$rundir/dry_top3_heteff_raw.dta", clear
export delimited using "$heteffcsv", replace
restore

di "=== ggcp10_dry_top3_ext_run_all.do COMPLETE ==="
log close master
