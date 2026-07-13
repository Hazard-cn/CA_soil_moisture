* =============================================================================
* ggcp10_story_s0_spec_search_mean_drytop3.do
* Purpose: S0 cleaning + fast story-oriented spec search for GGCP10 mean and
*          dry-top3 moderated mediation specifications.
* Outputs: temp/2026-06-02_story_s0_spec_search_mean_drytop3/
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global rundir "$projdir/temp/2026-06-02_story_s0_spec_search_mean_drytop3"
global logdir "$rundir/logs"
global basedta "$projdir/temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_baseline_suite_analysis_ready.dta"
global builddir "$projdir/data_build/data/processed"
global strict_rules "$projdir/quality_reports/specs/2026-06-02_story_acceptance_rules.md"
global relaxed_rules "$projdir/quality_reports/specs/2026-06-02_story_acceptance_rules_v1.md"
global FAST_GATE_ONLY "1"

cap mkdir "$projdir/temp"
cap mkdir "$rundir"
cap mkdir "$logdir"

cap log close master
log using "$logdir/ggcp10_story_s0_spec_search_mean_drytop3.log", replace text name(master)

di "=== story S0 spec search started ==="

file open pr using "$rundir/prereg.md", write replace
file write pr "# Preregistration snapshot" _n _n
file write pr "- Script: scripts/stata/ggcp10_story_s0_spec_search_mean_drytop3.do" _n
file write pr "- Strict rules: $strict_rules" _n
file write pr "- Relaxed fallback rules: $relaxed_rules" _n
file write pr "- Base data: $basedta" _n
file write pr "- S0: main_sample, crop mask, maize_zone != Other, yield domain, jump filter, SM quality, SR within variation, years >= 3, stable province" _n
file write pr "- Legal set: fullnew only; branches mean and dry_top3; hazards drought/heat/hotdry; transforms raw and winsor_1_99" _n
file write pr "- Bootstrap: failed sets skipped; near sets pilot 50; strict pass promote 500; primary strict anchors final 1000" _n
file close pr

* -----------------------------------------------------------------------------
* Load current GGCP10 base and required hot-dry precipitation exposure.
* -----------------------------------------------------------------------------
use "$basedta", clear
xtset grid_id year
xtset, clear

merge 1:1 grid_id year using "$builddir/data_v3_main.dta", ///
    keepusing(hotdrydays_ge32_pr_lt1) keep(master match)
assert _merge == 3
drop _merge

gen double HotDryPr_full = hotdrydays_ge32_pr_lt1
gen double SR_x_HotDryPr_full = ca * HotDryPr_full

confirm variable maize_frac
confirm variable ggcp10_maize_frac
confirm variable yield_tons_ha
confirm variable ln_yield
confirm variable gleam_smrz_sd
confirm variable era5l_swvl3_coverage
confirm variable ca_ratio
confirm variable maize_zone
confirm variable province
confirm variable prov_year

* -----------------------------------------------------------------------------
* S0 cleaning waterfall.
* -----------------------------------------------------------------------------
tempname pcln
postfile `pcln' str80 step long(N_before N_after N_drop grids_after) ///
    using "$rundir/cleaning_log_raw.dta", replace

gen byte s0 = (main_sample == 1)
count if s0 == 1
local n0 = r(N)
quietly levelsof grid_id if s0 == 1, local(g0)
local g0n : word count `g0'
post `pcln' ("start_main_sample") (`n0') (`n0') (0) (`g0n')

quietly count if s0 == 1
local before = r(N)
replace s0 = 0 if s0 == 1 & (maize_frac < 0.05 | ggcp10_maize_frac < 0.01 | missing(maize_frac) | missing(ggcp10_maize_frac))
quietly count if s0 == 1
local after = r(N)
quietly levelsof grid_id if s0 == 1, local(g1)
local g1n : word count `g1'
post `pcln' ("crop_mask_maize_frac_005_ggcp10_001") (`before') (`after') (`before' - `after') (`g1n')

quietly count if s0 == 1
local before = r(N)
replace s0 = 0 if s0 == 1 & maize_zone == "Other"
quietly count if s0 == 1
local after = r(N)
quietly levelsof grid_id if s0 == 1, local(g2)
local g2n : word count `g2'
post `pcln' ("drop_maize_zone_other") (`before') (`after') (`before' - `after') (`g2n')

quietly count if s0 == 1
local before = r(N)
replace s0 = 0 if s0 == 1 & (yield_tons_ha < 0.5 | yield_tons_ha >= 18 | missing(yield_tons_ha))
quietly count if s0 == 1
local after = r(N)
quietly levelsof grid_id if s0 == 1, local(g3)
local g3n : word count `g3'
post `pcln' ("yield_domain_0p5_to_lt18") (`before') (`after') (`before' - `after') (`g3n')

sort grid_id year
by grid_id: gen double __dln_prev = ln_yield - ln_yield[_n-1] if year == year[_n-1] + 1
by grid_id: gen double __dln_next = ln_yield[_n+1] - ln_yield if year[_n+1] == year + 1
quietly count if s0 == 1
local before = r(N)
replace s0 = 0 if s0 == 1 & ((abs(__dln_prev) > 1 & !missing(__dln_prev)) | (abs(__dln_next) > 1 & !missing(__dln_next)))
quietly count if s0 == 1
local after = r(N)
quietly levelsof grid_id if s0 == 1, local(g4)
local g4n : word count `g4'
post `pcln' ("yield_jump_adjacent_abs_dln_gt1") (`before') (`after') (`before' - `after') (`g4n')

quietly count if s0 == 1
local before = r(N)
replace s0 = 0 if s0 == 1 & (gleam_smrz_sd < 0.001 | missing(gleam_smrz_sd))
quietly count if s0 == 1
local after = r(N)
quietly levelsof grid_id if s0 == 1, local(g5)
local g5n : word count `g5'
post `pcln' ("sm_quality_gleam_smrz_sd_ge_0001") (`before') (`after') (`before' - `after') (`g5n')

quietly count if s0 == 1
local before = r(N)
replace s0 = 0 if s0 == 1 & (era5l_swvl3_coverage < 0.90 | missing(era5l_swvl3_coverage))
quietly count if s0 == 1
local after = r(N)
quietly levelsof grid_id if s0 == 1, local(g6)
local g6n : word count `g6'
post `pcln' ("sm_quality_era5l_swvl3_coverage_ge_090") (`before') (`after') (`before' - `after') (`g6n')

bysort grid_id: egen double __ca_sd = sd(ca_ratio) if s0 == 1
bysort grid_id: egen int __ca_n = count(ca_ratio) if s0 == 1
quietly count if s0 == 1
local before = r(N)
replace s0 = 0 if s0 == 1 & (__ca_n < 2 | missing(__ca_sd) | __ca_sd == 0)
quietly count if s0 == 1
local after = r(N)
quietly levelsof grid_id if s0 == 1, local(g7)
local g7n : word count `g7'
post `pcln' ("sr_within_variation_ca_ratio") (`before') (`after') (`before' - `after') (`g7n')

bysort grid_id: egen int __nyears = count(year) if s0 == 1
quietly count if s0 == 1
local before = r(N)
replace s0 = 0 if s0 == 1 & (__nyears < 3 | missing(__nyears))
quietly count if s0 == 1
local after = r(N)
quietly levelsof grid_id if s0 == 1, local(g8)
local g8n : word count `g8'
post `pcln' ("panel_years_ge_3") (`before') (`after') (`before' - `after') (`g8n')

sort grid_id province
by grid_id: gen byte __prov_change = (province != province[1]) if s0 == 1
bysort grid_id: egen int __nprov = total(__prov_change) if s0 == 1
replace __nprov = __nprov + 1 if !missing(__nprov)
quietly count if s0 == 1
local before = r(N)
replace s0 = 0 if s0 == 1 & (__nprov > 1 & !missing(__nprov))
quietly count if s0 == 1
local after = r(N)
quietly levelsof grid_id if s0 == 1, local(g9)
local g9n : word count `g9'
post `pcln' ("stable_province_within_grid") (`before') (`after') (`before' - `after') (`g9n')

postclose `pcln'
preserve
use "$rundir/cleaning_log_raw.dta", clear
export delimited using "$rundir/cleaning_log.csv", replace
restore

quietly count if s0 == 1
local s0N = r(N)
di "S0 final N = `s0N'"
if `s0N' < 35000 | `s0N' > 52000 {
    di as error "S0 final N outside expected guardrail; stopping before gate search."
    exit 459
}

* -----------------------------------------------------------------------------
* Analysis variables: raw and winsorized versions. Interactions are rebuilt after
* transformation. This keeps the legal transform dimension explicit.
* -----------------------------------------------------------------------------
global CTRL_BASE "pr_sum et0_sum gdd_10_30 irr_frac aridity"

local contvars ln_yield ca D_full W_full hdd_ge32 HotDryPr_full pr_sum et0_sum gdd_10_30 irr_frac aridity ///
    gleam_sms_mean gleam_smrz_mean v6mdf_p10_fn_gss v6sdf_p10_fn_gsr v6dur_p10_fn_gss

foreach v of local contvars {
    gen double `v'_raw = `v'
    gen double `v'_w = `v'
    quietly summarize `v' if s0 == 1, detail
    local p1 = r(p1)
    local p99 = r(p99)
    replace `v'_w = `p1' if s0 == 1 & `v'_w < `p1' & !missing(`v'_w)
    replace `v'_w = `p99' if s0 == 1 & `v'_w > `p99' & !missing(`v'_w)
}

foreach sx in raw w {
    gen double SR_x_D_full_`sx' = ca_`sx' * D_full_`sx'
    gen double SR_x_W_full_`sx' = ca_`sx' * W_full_`sx'
    gen double SR_x_Heat_full_`sx' = ca_`sx' * hdd_ge32_`sx'
    gen double SR_x_HotDryPr_full_`sx' = ca_`sx' * HotDryPr_full_`sx'
}

preserve
keep if s0 == 1
keep grid_id year province maize_zone irr_group s0 *_raw *_w SR_x_D_full_raw ///
    SR_x_W_full_raw SR_x_Heat_full_raw SR_x_HotDryPr_full_raw ///
    SR_x_D_full_w SR_x_W_full_w SR_x_Heat_full_w SR_x_HotDryPr_full_w
compress
save "$rundir/story_s0_ready.dta", replace
restore

* -----------------------------------------------------------------------------
* Model programs.
* -----------------------------------------------------------------------------
capture program drop story_fit_once
program define story_fit_once, rclass
    args hazard y ca d w h hd srd srw srh srhd mediator

    local rhs_m ""
    local rhs_y ""
    local main ""
    local inter ""
    if "`hazard'" == "drought" {
        local rhs_m "`d' `ca' `srd' `w' `h' pr_sum_`=substr("`y'",10,.)' et0_sum_`=substr("`y'",10,.)' gdd_10_30_`=substr("`y'",10,.)' irr_frac_`=substr("`y'",10,.)' aridity_`=substr("`y'",10,.)'"
        local rhs_y "`d' `ca' `srd' `mediator' `w' `h' pr_sum_`=substr("`y'",10,.)' et0_sum_`=substr("`y'",10,.)' gdd_10_30_`=substr("`y'",10,.)' irr_frac_`=substr("`y'",10,.)' aridity_`=substr("`y'",10,.)'"
        local main "`d'"
        local inter "`srd'"
    }
    if "`hazard'" == "heat" {
        local rhs_m "`h' `ca' `srh' `d' `w' pr_sum_`=substr("`y'",10,.)' et0_sum_`=substr("`y'",10,.)' gdd_10_30_`=substr("`y'",10,.)' irr_frac_`=substr("`y'",10,.)' aridity_`=substr("`y'",10,.)'"
        local rhs_y "`h' `ca' `srh' `mediator' `d' `w' pr_sum_`=substr("`y'",10,.)' et0_sum_`=substr("`y'",10,.)' gdd_10_30_`=substr("`y'",10,.)' irr_frac_`=substr("`y'",10,.)' aridity_`=substr("`y'",10,.)'"
        local main "`h'"
        local inter "`srh'"
    }
    if "`hazard'" == "hotdry" {
        local rhs_m "`hd' `ca' `srhd' `d' `h' `w' pr_sum_`=substr("`y'",10,.)' et0_sum_`=substr("`y'",10,.)' gdd_10_30_`=substr("`y'",10,.)' irr_frac_`=substr("`y'",10,.)' aridity_`=substr("`y'",10,.)'"
        local rhs_y "`hd' `ca' `srhd' `mediator' `d' `h' `w' pr_sum_`=substr("`y'",10,.)' et0_sum_`=substr("`y'",10,.)' gdd_10_30_`=substr("`y'",10,.)' irr_frac_`=substr("`y'",10,.)' aridity_`=substr("`y'",10,.)'"
        local main "`hd'"
        local inter "`srhd'"
    }

    quietly reghdfe `mediator' `rhs_m', absorb(grid_id year) vce(cluster grid_id)
    return scalar N_m = e(N)
    return scalar r2_m = e(r2)
    return scalar a1 = _b[`main']
    return scalar a1_se = _se[`main']
    return scalar a1_p = 2 * ttail(e(df_r), abs(_b[`main'] / _se[`main']))
    return scalar a3 = _b[`inter']
    return scalar a3_se = _se[`inter']
    return scalar a3_p = 2 * ttail(e(df_r), abs(_b[`inter'] / _se[`inter']))

    quietly reghdfe `y' `rhs_y', absorb(grid_id year) vce(cluster grid_id)
    return scalar N_y = e(N)
    return scalar r2_y = e(r2)
    return scalar b = _b[`mediator']
    return scalar b_se = _se[`mediator']
    return scalar b_p = 2 * ttail(e(df_r), abs(_b[`mediator'] / _se[`mediator']))
    return scalar c1 = _b[`main']
    return scalar c1_se = _se[`main']
    return scalar c1_p = 2 * ttail(e(df_r), abs(_b[`main'] / _se[`main']))
    return scalar c3 = _b[`inter']
    return scalar c3_se = _se[`inter']
    return scalar c3_p = 2 * ttail(e(df_r), abs(_b[`inter'] / _se[`inter']))
end

capture program drop story_boot
program define story_boot, rclass
    args hazard y ca d w h hd srd srw srh srhd mediator
    local abs_id "grid_id"
    capture confirm variable boot_grid
    if _rc == 0 local abs_id "boot_grid"

    local rhs_m ""
    local rhs_y ""
    local main ""
    local inter ""
    local sx = substr("`y'", 10, .)
    if "`hazard'" == "drought" {
        local rhs_m "`d' `ca' `srd' `w' `h' pr_sum_`sx' et0_sum_`sx' gdd_10_30_`sx' irr_frac_`sx' aridity_`sx'"
        local rhs_y "`d' `ca' `srd' `mediator' `w' `h' pr_sum_`sx' et0_sum_`sx' gdd_10_30_`sx' irr_frac_`sx' aridity_`sx'"
        local main "`d'"
        local inter "`srd'"
    }
    if "`hazard'" == "heat" {
        local rhs_m "`h' `ca' `srh' `d' `w' pr_sum_`sx' et0_sum_`sx' gdd_10_30_`sx' irr_frac_`sx' aridity_`sx'"
        local rhs_y "`h' `ca' `srh' `mediator' `d' `w' pr_sum_`sx' et0_sum_`sx' gdd_10_30_`sx' irr_frac_`sx' aridity_`sx'"
        local main "`h'"
        local inter "`srh'"
    }
    if "`hazard'" == "hotdry" {
        local rhs_m "`hd' `ca' `srhd' `d' `h' `w' pr_sum_`sx' et0_sum_`sx' gdd_10_30_`sx' irr_frac_`sx' aridity_`sx'"
        local rhs_y "`hd' `ca' `srhd' `mediator' `d' `h' `w' pr_sum_`sx' et0_sum_`sx' gdd_10_30_`sx' irr_frac_`sx' aridity_`sx'"
        local main "`hd'"
        local inter "`srhd'"
    }

    capture quietly reghdfe `mediator' `rhs_m', absorb(`abs_id' year) vce(cluster `abs_id')
    if _rc != 0 exit
    local a1 = _b[`main']
    local a3 = _b[`inter']
    capture quietly reghdfe `y' `rhs_y', absorb(`abs_id' year) vce(cluster `abs_id')
    if _rc != 0 exit
    local b = _b[`mediator']
    local c1 = _b[`main']
    local c3 = _b[`inter']
    foreach q in 25 50 75 {
        local r = $BOOT_CA_P`q'
        local ie = (`a1' + `a3' * `r') * `b'
        local de = `c1' + `c3' * `r'
        return scalar ie`q' = `ie'
        return scalar de`q' = `de'
        return scalar te`q' = `ie' + `de'
    }
end

* -----------------------------------------------------------------------------
* Gate scan and selective bootstrap.
* -----------------------------------------------------------------------------
tempname pg pb ph pi
postfile `pg' str100 set_id str12 branch str28 mediator_tag str32 mediator ///
    str12 hazard str16 transform str24 story str24 verdict_v2 str24 verdict_v1 ///
    double(a1 a1_se a1_p a3 a3_se a3_p b b_se b_p c1 c1_se c1_p c3 c3_se c3_p ///
           ca_p25 ca_p50 ca_p75 ie25 ie50 ie75 de25 de50 de75 te25 te50 te75 ///
           te_identity_error) long(N_m N_y) double(r2_m r2_y) str80 fail_reason ///
    using "$rundir/gate_scan_raw.dta", replace

postfile `pb' str100 set_id str12 branch str28 mediator_tag str12 hazard ///
    str16 transform str24 story str16 boot_stage str2 effect str4 ca_level ///
    double(point_est bs_se ci_lo ci_hi) long(N_boot) ///
    using "$rundir/bootstrap_raw.dta", replace

postfile `ph' str100 set_id str12 branch str28 mediator_tag str12 hazard ///
    str16 transform str10 split_type str12 subgroup str24 story str2 effect ///
    str4 ca_level double(ca_value value) long(N_sub) ///
    using "$rundir/heterogeneity_raw.dta", replace

postfile `pi' str100 set_id str12 branch str28 mediator_tag str12 hazard ///
    str16 transform double(resid_p99 resid_max) long(N_gt_p99 N_model) ///
    using "$rundir/influence_raw.dta", replace

local branches "mean mean dry dry dry"
local medtags "mean_surface mean_root dry_mdf_p10_sfc dry_sdf_p10_root dry_dur_p10_sfc"
local medvars "gleam_sms_mean gleam_smrz_mean v6mdf_p10_fn_gss v6sdf_p10_fn_gsr v6dur_p10_fn_gss"

local total_sets = 0
local boot_jobs = 0

foreach sx in raw w {
    local transform "raw"
    if "`sx'" == "w" local transform "winsor_1_99"

    forvalues m = 1/5 {
        local branch : word `m' of `branches'
        local medtag : word `m' of `medtags'
        local medbase : word `m' of `medvars'
        local mediator "`medbase'_`sx'"
        local y "ln_yield_`sx'"
        local ca_v "ca_`sx'"
        local d "D_full_`sx'"
        local w "W_full_`sx'"
        local h "hdd_ge32_`sx'"
        local hd "HotDryPr_full_`sx'"
        local srd "SR_x_D_full_`sx'"
        local srw "SR_x_W_full_`sx'"
        local srh "SR_x_Heat_full_`sx'"
        local srhd "SR_x_HotDryPr_full_`sx'"

        foreach haz in drought heat hotdry {
            local ++total_sets
            local set_id "S0_fullnew_`transform'_`branch'_`medtag'_`haz'"
            di _n "GATE `total_sets': `set_id'"

            preserve
            gen byte __model_sample = s0 == 1
            foreach v in `y' `ca_v' `d' `w' `h' `hd' `srd' `srh' `srhd' `mediator' pr_sum_`sx' et0_sum_`sx' gdd_10_30_`sx' irr_frac_`sx' aridity_`sx' {
                replace __model_sample = 0 if missing(`v') & __model_sample == 1
            }
            keep if __model_sample == 1
            count
            local modelN = r(N)
            if `modelN' < 500 {
                foreach story in A_common_pathway C_typology B_buffering {
                    post `pg' ("`set_id'") ("`branch'") ("`medtag'") ("`mediator'") ///
                        ("`haz'") ("`transform'") ("`story'") ("reject") ("reject") ///
                        (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) ///
                        (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) ///
                        (.) (`modelN') (`modelN') (.) (.) ("N_lt_500")
                }
                restore
                continue
            }

            _pctile `ca_v', p(25 50 75)
            local ca25 = r(r1)
            local ca50 = r(r2)
            local ca75 = r(r3)

            capture noisily story_fit_once `haz' `y' `ca_v' `d' `w' `h' `hd' `srd' `srw' `srh' `srhd' `mediator'
            if _rc != 0 {
                foreach story in A_common_pathway C_typology B_buffering {
                    post `pg' ("`set_id'") ("`branch'") ("`medtag'") ("`mediator'") ///
                        ("`haz'") ("`transform'") ("`story'") ("reject") ("reject") ///
                        (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) ///
                        (`ca25') (`ca50') (`ca75') (.) (.) (.) (.) (.) (.) (.) (.) (.) ///
                        (.) (`modelN') (`modelN') (.) (.) ("fit_failed")
                }
                restore
                continue
            }

            local a1 = r(a1)
            local a1_se = r(a1_se)
            local a1_p = r(a1_p)
            local a3 = r(a3)
            local a3_se = r(a3_se)
            local a3_p = r(a3_p)
            local bcoef = r(b)
            local b_se = r(b_se)
            local b_p = r(b_p)
            local c1 = r(c1)
            local c1_se = r(c1_se)
            local c1_p = r(c1_p)
            local c3 = r(c3)
            local c3_se = r(c3_se)
            local c3_p = r(c3_p)
            local Nm = r(N_m)
            local Ny = r(N_y)
            local r2m = r(r2_m)
            local r2y = r(r2_y)

            foreach q in 25 50 75 {
                local ie`q' = (`a1' + `a3' * `ca`q'') * `bcoef'
                local de`q' = `c1' + `c3' * `ca`q''
                local te`q' = `ie`q'' + `de`q''
            }
            local iderr = abs(`te50' - `ie50' - `de50')

            local phys = 0
            if "`branch'" == "mean" & `a1' < 0 & `bcoef' > 0 local phys = 1
            if "`branch'" == "dry" & `a1' > 0 & `bcoef' < 0 local phys = 1

            local A_v2 "reject"
            local A_v1 "reject"
            local C_v2 "reject"
            local C_v1 "reject"
            local B_v2 "reject"
            local B_v1 "reject"
            local reason "ok"

            if `phys' == 0 local reason "physical_sign_fail"
            if `phys' == 1 & `ie50' < 0 & `a1_p' < .05 & `b_p' < .10 {
                local A_v2 "suggestive_bounded"
                local A_v1 "headline_candidate"
            }
            else if `phys' == 1 & `ie50' < 0 {
                local A_v1 "suggestive"
            }

            if `phys' == 1 {
                if "`haz'" == "heat" & abs(`ie50') >= .5 * abs(`de50') local C_v2 "suggestive_bounded"
                if "`haz'" == "drought" & abs(`ie50') > 0 & abs(`de50') > 0 local C_v2 "suggestive_bounded"
                if "`haz'" == "hotdry" & abs(`de50') >= abs(`ie50') local C_v2 "suggestive_bounded"
                if "`C_v2'" == "suggestive_bounded" local C_v1 "headline_candidate"
                else local C_v1 "suggestive"
            }

            local idx = `a3' * `bcoef'
            if `idx' > 0 & `te75' > `te25' & `phys' == 1 {
                local B_v2 "suggestive_bounded"
                local B_v1 "headline_candidate"
            }
            else if `idx' > 0 & `phys' == 1 {
                local B_v1 "suggestive"
            }

            foreach story in A_common_pathway C_typology B_buffering {
                local vv2 "`A_v2'"
                local vv1 "`A_v1'"
                if "`story'" == "C_typology" {
                    local vv2 "`C_v2'"
                    local vv1 "`C_v1'"
                }
                if "`story'" == "B_buffering" {
                    local vv2 "`B_v2'"
                    local vv1 "`B_v1'"
                }
                local freason "`reason'"
                if "`vv2'" != "reject" local freason "passes_v2_gate_pending_universe_bootstrap"
                else if "`vv1'" != "reject" local freason "v2_fail_relaxed_v1_candidate"
                post `pg' ("`set_id'") ("`branch'") ("`medtag'") ("`mediator'") ///
                    ("`haz'") ("`transform'") ("`story'") ("`vv2'") ("`vv1'") ///
                    (`a1') (`a1_se') (`a1_p') (`a3') (`a3_se') (`a3_p') ///
                    (`bcoef') (`b_se') (`b_p') (`c1') (`c1_se') (`c1_p') ///
                    (`c3') (`c3_se') (`c3_p') ///
                    (`ca25') (`ca50') (`ca75') ///
                    (`ie25') (`ie50') (`ie75') (`de25') (`de50') (`de75') (`te25') (`te50') (`te75') ///
                    (`iderr') (`Nm') (`Ny') (`r2m') (`r2y') ("`freason'")
            }

            * Influence diagnostics for any v2 candidate, without deleting points.
            if "`A_v2'" != "reject" | "`C_v2'" != "reject" | "`B_v2'" != "reject" {
                local sx2 = "`sx'"
                local rhs_y ""
                if "`haz'" == "drought" local rhs_y "`d' `ca_v' `srd' `mediator' `w' `h' pr_sum_`sx2' et0_sum_`sx2' gdd_10_30_`sx2' irr_frac_`sx2' aridity_`sx2'"
                if "`haz'" == "heat" local rhs_y "`h' `ca_v' `srh' `mediator' `d' `w' pr_sum_`sx2' et0_sum_`sx2' gdd_10_30_`sx2' irr_frac_`sx2' aridity_`sx2'"
                if "`haz'" == "hotdry" local rhs_y "`hd' `ca_v' `srhd' `mediator' `d' `h' `w' pr_sum_`sx2' et0_sum_`sx2' gdd_10_30_`sx2' irr_frac_`sx2' aridity_`sx2'"
                capture drop __resid
                quietly reghdfe `y' `rhs_y', absorb(grid_id year) vce(cluster grid_id) resid(__resid)
                quietly summarize __resid, detail
                local rp99 = r(p99)
                local rmax = r(max)
                quietly count if __resid > `rp99' & !missing(__resid)
                local nrp99 = r(N)
                post `pi' ("`set_id'") ("`branch'") ("`medtag'") ("`haz'") ///
                    ("`transform'") (`rp99') (`rmax') (`nrp99') (`Ny')
            }

            * Selective bootstrap.
            local bootstage "none"
            local reps = 0
            if "`A_v2'" != "reject" | "`C_v2'" != "reject" | "`B_v2'" != "reject" {
                local bootstage "promote"
                local reps = 500
            }
            else if "`A_v1'" != "reject" | "`C_v1'" != "reject" | "`B_v1'" != "reject" {
                local bootstage "pilot"
                local reps = 50
            }
            local primary_anchor = 0
            if "`transform'" == "raw" & "`branch'" == "mean" & "`medtag'" == "mean_root" local primary_anchor = 1
            if "`transform'" == "raw" & "`branch'" == "dry" & "`medtag'" == "dry_mdf_p10_sfc" local primary_anchor = 1
            if `primary_anchor' == 1 & ("`A_v2'" != "reject" | "`C_v2'" != "reject" | "`B_v2'" != "reject") {
                local bootstage "final"
                local reps = 1000
            }
            if "$FAST_GATE_ONLY" == "1" {
                local bootstage "queued_after_gate"
                local reps = 0
            }

            if `reps' > 0 {
                local ++boot_jobs
                di "BOOT `boot_jobs': `set_id' stage=`bootstage' reps=`reps'"
                local bseed = 42000 + `boot_jobs'
                global BOOT_CA_P25 = `ca25'
                global BOOT_CA_P50 = `ca50'
                global BOOT_CA_P75 = `ca75'
                bootstrap ie25=r(ie25) ie50=r(ie50) ie75=r(ie75) ///
                    de25=r(de25) de50=r(de50) de75=r(de75) ///
                    te25=r(te25) te50=r(te50) te75=r(te75), ///
                    reps(`reps') cluster(grid_id) idcluster(boot_grid) seed(`bseed') nodots: ///
                    story_boot `haz' `y' `ca_v' `d' `w' `h' `hd' `srd' `srw' `srh' `srhd' `mediator'
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
                    scalar __ll = .
                    scalar __ul = .
                    capture scalar __ll = bcCI[`j',1]
                    capture scalar __ul = bcCI[`j',2]
                    local ll = scalar(__ll)
                    local ul = scalar(__ul)
                    if missing(`ll') | missing(`ul') {
                        local ll = `point' - 1.96 * `bs'
                        local ul = `point' + 1.96 * `bs'
                    }
                    local eff = upper(substr("`sname'",1,2))
                    local lvl = substr("`sname'",3,.)
                    foreach story in A_common_pathway C_typology B_buffering {
                        local include_story = 0
                        if "`story'" == "A_common_pathway" & ("`A_v2'" != "reject" | "`A_v1'" != "reject") local include_story = 1
                        if "`story'" == "C_typology" & ("`C_v2'" != "reject" | "`C_v1'" != "reject") local include_story = 1
                        if "`story'" == "B_buffering" & ("`B_v2'" != "reject" | "`B_v1'" != "reject") local include_story = 1
                        if `include_story' == 1 {
                            post `pb' ("`set_id'") ("`branch'") ("`medtag'") ("`haz'") ///
                                ("`transform'") ("`story'") ("`bootstage'") ("`eff'") ("P`lvl'") ///
                                (`point') (`bs') (`ll') (`ul') (`reps')
                        }
                    }
                }

                * Heterogeneity point estimates only for bootstrapped v2 candidates.
                if "`bootstage'" == "promote" | "`bootstage'" == "final" {
                    foreach split in irr zone {
                        local splitvar "irr_group"
                        local groups "low_irr high_irr"
                        if "`split'" == "zone" {
                            local splitvar "maize_zone"
                            local groups "NE HHH SW SH NW"
                        }
                        foreach grp of local groups {
                            preserve
                            keep if `splitvar' == "`grp'"
                            keep if __model_sample == 1
                            count
                            local nsub = r(N)
                            if `nsub' >= 500 {
                                _pctile `ca_v', p(50)
                                local subca50 = r(r1)
                                capture noisily story_fit_once `haz' `y' `ca_v' `d' `w' `h' `hd' `srd' `srw' `srh' `srhd' `mediator'
                                if _rc == 0 {
                                    local sa1 = r(a1)
                                    local sa3 = r(a3)
                                    local sb = r(b)
                                    local sc1 = r(c1)
                                    local sc3 = r(c3)
                                    local sie = (`sa1' + `sa3' * `subca50') * `sb'
                                    local sde = `sc1' + `sc3' * `subca50'
                                    local ste = `sie' + `sde'
                                    foreach story in A_common_pathway C_typology B_buffering {
                                        local include_story = 0
                                        if "`story'" == "A_common_pathway" & "`A_v2'" != "reject" local include_story = 1
                                        if "`story'" == "C_typology" & "`C_v2'" != "reject" local include_story = 1
                                        if "`story'" == "B_buffering" & "`B_v2'" != "reject" local include_story = 1
                                        if `include_story' == 1 {
                                            post `ph' ("`set_id'") ("`branch'") ("`medtag'") ("`haz'") ///
                                                ("`transform'") ("`split'") ("`grp'") ("`story'") ("IE") ("P50") (`subca50') (`sie') (`nsub')
                                            post `ph' ("`set_id'") ("`branch'") ("`medtag'") ("`haz'") ///
                                                ("`transform'") ("`split'") ("`grp'") ("`story'") ("DE") ("P50") (`subca50') (`sde') (`nsub')
                                            post `ph' ("`set_id'") ("`branch'") ("`medtag'") ("`haz'") ///
                                                ("`transform'") ("`split'") ("`grp'") ("`story'") ("TE") ("P50") (`subca50') (`ste') (`nsub')
                                        }
                                    }
                                }
                            }
                            restore
                        }
                    }
                }
            }
            restore
        }
    }
}

postclose `pg'
postclose `pb'
postclose `ph'
postclose `pi'

preserve
use "$rundir/gate_scan_raw.dta", clear
export delimited using "$rundir/gate_scan_index.csv", replace
export delimited using "$rundir/scorecard_v2.csv" if verdict_v2 != "reject", replace
export delimited using "$rundir/scorecard_v1_fallback.csv" if verdict_v2 == "reject" & verdict_v1 != "reject", replace
export delimited using "$rundir/passed_sets.csv" if verdict_v2 != "reject" | verdict_v1 != "reject", replace
export delimited using "$rundir/failed_sets.csv" if verdict_v2 == "reject" & verdict_v1 == "reject", replace
restore

preserve
use "$rundir/bootstrap_raw.dta", clear
export delimited using "$rundir/bootstrap_all.csv", replace
export delimited using "$rundir/bootstrap_pilot.csv" if boot_stage == "pilot", replace
export delimited using "$rundir/bootstrap_promote.csv" if boot_stage == "promote", replace
export delimited using "$rundir/bootstrap_final.csv" if boot_stage == "final", replace
restore

preserve
use "$rundir/heterogeneity_raw.dta", clear
export delimited using "$rundir/heterogeneity_effects.csv", replace
restore

preserve
use "$rundir/influence_raw.dta", clear
export delimited using "$rundir/influence_diagnostics.csv", replace
restore

di "TOTAL_GATE_SETS = `total_sets'"
di "TOTAL_BOOT_JOBS = `boot_jobs'"
di "=== ggcp10_story_s0_spec_search_mean_drytop3.do COMPLETE ==="
log close master
