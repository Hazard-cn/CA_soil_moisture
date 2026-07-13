* =============================================================================
* v3med_macros_include.do
* Purpose: Define all global macros for Model 8 moderated mediation analysis.
*          Two mirror modules (Drought / Heat), 6 SM sources, 2 ctrl versions.
*          Sourced at the top of each v3med_step*.do file via `do`.
* Date:    2026-04-16
* =============================================================================

* --- Paths ---
global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global datadir  "$projdir/data/processed"
global outdir   "$projdir/output/tables"
global figdir   "$projdir/output/figures"
global logdir   "$projdir/output/logs"

* --- SM data sources: 3 products x 2 depths = 6 ---
global SM_SOURCES  "gleam_sms_mean gleam_smrz_mean swsm_l1_mean swsm_l3_mean era5l_swvl1_mean era5l_swvl3_mean"
global SM_LABELS   `" "GLEAM-Sfc" "GLEAM-Root" "SWSM-L1" "SWSM-L3" "ERA5L-L1" "ERA5L-L3" "'
global SM_PREFIXES "gsms gsmrz ssl1 ssl3 esl1 esl3"
global N_SM = 6

* --- Control variables: dual version ---
*     Version A (full): all controls, consistent with v3 main pipeline
*     Version B (reduced): drop pr_sum, et0_sum, aridity (overlap with D/H/SM)
global CTRL_full_med    "irr_frac pr_sum et0_sum aridity gdd_ge10"
global CTRL_reduced_med "irr_frac gdd_ge10"
global CTRL_VERSIONS    "full reduced"

* --- Fixed effect levels (L0 most strict -> L3 most relaxed) ---
*     L0: grid + year  (default, matches v3 main)
*     L1: county + year
*     L2: city + year
*     L3: province + year
global FE_LEVELS "L0 L1 L2 L3"

* --- Subsample groupings ---
global ZONE_LIST "NE HHH SW SH NW Other"
global IRR_LIST  "low_irr high_irr"

* --- Core RHS variable names (full-season only for v3med) ---
*     D = D_full, H = hdd_ge32, SR = ca
*     Interactions already built in v3_step0_preamble.do:
*       SR_x_D_full  = ca * D_full
*       SR_x_Heat_full = ca * hdd_ge32

* --- Drought Module Model 8 ---
* Mediator eq:  SM = a1*D_full + a2*ca + a3*(SR_x_D_full) + rho*hdd_ge32 + Z + FE
* Outcome eq:   lnY = c1*D_full + c2*ca + c3*(SR_x_D_full) + b*SM + rho_y*hdd_ge32 + Z + FE
* NOTE: no W, no D×H

global MED_drought_mediator "D_full ca SR_x_D_full hdd_ge32"
global MED_drought_outcome_base "D_full ca SR_x_D_full hdd_ge32"
* SM variable appended at runtime per source

* --- Heat Module Model 8 ---
* Mediator eq:  SM = a1h*hdd_ge32 + a2h*ca + a3h*(SR_x_Heat_full) + rho_d*D_full + Z + FE
* Outcome eq:   lnY = c1h*hdd_ge32 + c2h*ca + c3h*(SR_x_Heat_full) + b_h*SM + rho_dy*D_full + Z + FE
global MED_heat_mediator "hdd_ge32 ca SR_x_Heat_full D_full"
global MED_heat_outcome_base "hdd_ge32 ca SR_x_Heat_full D_full"

* --- Nested check (Set 3): drop X×RR from outcome eq ---
global MED_drought_nested "D_full ca hdd_ge32"
global MED_heat_nested    "hdd_ge32 ca D_full"

di "=== v3med_macros_include.do loaded ==="
