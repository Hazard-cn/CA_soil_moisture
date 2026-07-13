version 18
clear all
set more off

global root "C:/YangSu/00_Project/CA_mechanism/regression_SR"
cd "$root"

cap log close
log using "output/logs/verify_story_g057_g185_20260618.log", replace text

capture which reghdfe
if _rc {
    di as error "reghdfe is not installed or not on adopath."
    exit 499
}

use "temp/2026-06-18_story_stata_verify/story_verify_panel.dta", clear

tempname handle
postfile `handle' str4 scale str10 model str8 hazard str28 term double coef se p N df_r using ///
    "temp/2026-06-18_story_stata_verify/stata_verify_results.dta", replace

foreach scale in G057 G185 {
    foreach hazard in drought heat hotdry {
        if "`hazard'" == "drought" {
            local main D_full_raw
            local inter SR_x_D_full_raw
            local companions W_full_raw hdd_ge32_raw
        }
        if "`hazard'" == "heat" {
            local main hdd_ge32_raw
            local inter SR_x_Heat_full_raw
            local companions D_full_raw W_full_raw
        }
        if "`hazard'" == "hotdry" {
            local main HotDryPr_full_raw
            local inter SR_x_HotDryPr_full_raw
            local companions D_full_raw hdd_ge32_raw W_full_raw
        }

        quietly reghdfe ln_yield_raw `main' ca_raw `inter' gleam_smrz_mean_raw ///
            `companions' pr_sum_raw et0_sum_raw gdd_10_30_raw irr_frac_raw aridity_raw ///
            if sample_`scale' == 1, absorb(grid_code year_code) vce(cluster grid_code)
        local t = _b[`inter'] / _se[`inter']
        local p = 2 * ttail(e(df_r), abs(`t'))
        post `handle' ("`scale'") ("baseline") ("`hazard'") ("`inter'") ///
            (_b[`inter']) (_se[`inter']) (`p') (e(N)) (e(df_r))

        if "`hazard'" == "drought" {
            local xirr drought_x_irr
            local triple SR_x_drought_x_irr
        }
        if "`hazard'" == "heat" {
            local xirr heat_x_irr
            local triple SR_x_heat_x_irr
        }
        if "`hazard'" == "hotdry" {
            local xirr hotdry_x_irr
            local triple SR_x_hotdry_x_irr
        }

        quietly reghdfe ln_yield_raw `main' ca_raw irr_frac_raw `inter' `xirr' ///
            SR_x_irr `triple' `companions' pr_sum_raw et0_sum_raw gdd_10_30_raw aridity_raw ///
            if sample_`scale' == 1, absorb(grid_code year_code) vce(cluster grid_code)
        local t = _b[`triple'] / _se[`triple']
        local p = 2 * ttail(e(df_r), abs(`t'))
        post `handle' ("`scale'") ("irrigation") ("`hazard'") ("`triple'") ///
            (_b[`triple']) (_se[`triple']) (`p') (e(N)) (e(df_r))
    }
}

postclose `handle'

use "temp/2026-06-18_story_stata_verify/stata_verify_results.dta", clear
export delimited using "temp/2026-06-18_story_stata_verify/stata_verify_results.csv", replace

log close
