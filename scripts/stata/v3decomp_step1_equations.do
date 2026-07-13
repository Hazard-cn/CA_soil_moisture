* =============================================================================
* v3decomp_step1_equations.do
* Purpose: Estimate Layer 2 and Layer 3 FE equations, export coefficient table,
*          validation table, and profile-specific point decomposition.
* Input:   data/processed/v3decomp_analysis_ready.dta
*          output/tables/v3decomp_profile_constants.dta
* Output:  output/tables/v3decomp_equation_coefficients.csv
*          output/tables/v3decomp_profile_point_estimates.csv
*          output/tables/v3decomp_validation.csv
* =============================================================================

clear all
set more off
set seed 42

do "C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata/v3decomp_macros_include.do"

log using "$logdir/v3decomp_step1_equations.log", replace

use "$decomp_panel", clear
xtset grid_id year

local med "$DECOMP_MEDIATOR"
local sample_tag "full_main_common"

capture program drop post_terms_v3decomp
program define post_terms_v3decomp
    syntax anything(name=terms), POST(name) EQUATION(string) MEDIATOR(string) ///
        SAMPLETAG(string)

    local cnames : colnames e(b)
    local dfr = e(df_r)
    local N   = e(N)
    local r2  = e(r2)

    foreach v of local terms {
        if strpos(" `cnames' ", " `v' ") == 0 {
            post `post' ("`equation'") ("`mediator'") ("`sampletag'") ///
                ("`v'") (.) (.) (.) (`N') (`r2')
            continue
        }

        local b  = _b[`v']
        local se = _se[`v']
        local p  = 2 * ttail(`dfr', abs(`b' / `se'))

        post `post' ("`equation'") ("`mediator'") ("`sampletag'") ///
            ("`v'") (`b') (`se') (`p') (`N') (`r2')
    }
end

tempname coef_pf
postfile `coef_pf' str16 equation str20 mediator str20 sample_tag ///
    str32 term double b se p N r2 using "$decomp_coef_dta", replace

* ---------------------------------------------------------------------------
* Validation regression: Layer 3 without mediator terms
* ---------------------------------------------------------------------------
tempname val_pf
postfile `val_pf' str24 model str20 sample_tag str24 term ///
    double b se p N r2 using "$decomp_validation_dta", replace

quietly reghdfe ln_yield $DECOMP_L2_RHS $DECOMP_CTRL ///
    if v3decomp_common_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

local val_dfr = e(df_r)
foreach v in ca SR_x_D_full SR_x_Heat_full SR_x_W_full D_x_Heat_full SR_x_D_x_Heat_full {
    local b  = _b[`v']
    local se = _se[`v']
    local p  = 2 * ttail(`val_dfr', abs(`b' / `se'))
    post `val_pf' ("baseline_no_sm") ("`sample_tag'") ("`v'") ///
        (`b') (`se') (`p') (e(N)) (e(r2))
}

* ---------------------------------------------------------------------------
* Layer 2: mediator equation
* ---------------------------------------------------------------------------
quietly reghdfe `med' $DECOMP_L2_RHS $DECOMP_CTRL ///
    if v3decomp_common_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

local N_l2  = e(N)
local r2_l2 = e(r2)
post_terms_v3decomp $DECOMP_L2_COEFS, post(`coef_pf') ///
    equation("layer2_sm") mediator("`med'") sampletag("`sample_tag'")

local pi_sr = _b[ca]
local lam_d = _b[SR_x_D_full]
local lam_h = _b[SR_x_Heat_full]
local lam_w = _b[SR_x_W_full]
local lam_dh = _b[SR_x_D_x_Heat_full]

* ---------------------------------------------------------------------------
* Layer 3: outcome equation with mediator
* ---------------------------------------------------------------------------
quietly reghdfe ln_yield $DECOMP_L3_RHS $DECOMP_CTRL ///
    if v3decomp_common_sample == 1, ///
    absorb(grid_id year) vce(cluster grid_id)

local N_l3  = e(N)
local r2_l3 = e(r2)

if `N_l2' != `N_l3' {
    di as error "Layer 2 and Layer 3 N mismatch: `N_l2' vs `N_l3'"
    log close
    exit 459
}

post_terms_v3decomp $DECOMP_L3_COEFS, post(`coef_pf') ///
    equation("layer3_yield") mediator("`med'") sampletag("`sample_tag'")

local beta_sr = _b[ca]
local th_d    = _b[SR_x_D_full]
local th_h    = _b[SR_x_Heat_full]
local th_w    = _b[SR_x_W_full]
local th_dh   = _b[SR_x_D_x_Heat_full]
local delta   = _b[`med']
local phi_d   = _b[SM_x_D_full]
local phi_h   = _b[SM_x_H_full]

di "Layer 2 N = `N_l2', R2 = " %6.4f `r2_l2'
di "Layer 3 N = `N_l3', R2 = " %6.4f `r2_l3'

* ---------------------------------------------------------------------------
* Profile-specific point decomposition
* ---------------------------------------------------------------------------
tempname point_pf
postfile `point_pf' str16 profile str24 profile_label str12 profile_group ///
    str20 mediator str20 sample_tag ///
    double d h w a_hat b_hat DE DE_stress IE TE share ///
    using "$decomp_point_dta", replace

preserve
use "$decomp_profiles", clear
levelsof profile, local(profile_list)

foreach p of local profile_list {
    quietly summarize d if profile == "`p'", meanonly
    local d = r(mean)
    quietly summarize h if profile == "`p'", meanonly
    local h = r(mean)
    quietly summarize w if profile == "`p'", meanonly
    local w = r(mean)
    quietly levelsof profile_label if profile == "`p'", local(profile_label) clean
    quietly levelsof profile_group if profile == "`p'", local(profile_group) clean

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

    post `point_pf' ("`p'") ("`profile_label'") ("`profile_group'") ///
        ("`med'") ("`sample_tag'") ///
        (`d') (`h') (`w') (`a_hat') (`b_hat') (`DE') (`DE_stress') ///
        (`IE') (`TE') (`share')
}
restore

postclose `coef_pf'
postclose `point_pf'
postclose `val_pf'

preserve
use "$decomp_coef_dta", clear
format b se %9.6f
format p %7.4f
format N %12.0f
format r2 %7.4f
sort equation term
export delimited using "$decomp_coef_csv", replace
restore

preserve
use "$decomp_point_dta", clear
format d h w %9.6f
format a_hat b_hat DE DE_stress IE TE share %9.6f
sort profile
list profile d h a_hat b_hat DE IE TE share, noobs sep(0)
export delimited using "$decomp_point_csv", replace
restore

preserve
use "$decomp_validation_dta", clear
format b se %9.6f
format p %7.4f
export delimited using "$decomp_validation_csv", replace
restore

* ---------------------------------------------------------------------------
* Manual formula checks for two profiles
* ---------------------------------------------------------------------------
preserve
use "$decomp_point_dta", clear

foreach p in baseline dh_p75 {
    list profile a_hat b_hat DE DE_stress IE TE share ///
        if profile == "`p'", noobs
}
restore

log close
di "=== v3decomp_step1_equations.do COMPLETE ==="
