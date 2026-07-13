* =============================================================================
* v3proxy_macros_include.do
* Purpose: Shared macros for the v3proxy drought-proxy analysis line.
* =============================================================================

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global datadir  "$projdir/data/processed"
global outdir   "$projdir/output/tables"
global figdir   "$projdir/output/figures"
global logdir   "$projdir/output/logs"
global repdir   "$projdir/output/reports"

cap mkdir "$outdir"
cap mkdir "$figdir"
cap mkdir "$logdir"
cap mkdir "$repdir"

global RAW_WINDOWS "full v3pm10 hepm10 v3pre30 v3he hema"
global CUTS "full ii iv"
global CUT_full_WINDOWS "full"
global CUT_ii_WINDOWS "v3pm10 hepm10"
global CUT_iv_WINDOWS "v3pre30 v3he hema"

global SOURCES "gleam swsm era"
global LAYERS  "surface rootzone"

global SM_BASES "gleam_sms_mean gleam_smrz_mean swsm_l1_mean swsm_l3_mean era5l_swvl1_mean era5l_swvl3_mean"
global SM_LABELS `" "GLEAM-Sfc" "GLEAM-Root" "SWSM-L1" "SWSM-L3" "ERA5L-L1" "ERA5L-L3" "'

* --- HotDryPr dimension (on/off) ---
global HDP_LEVELS "off on"

global CTRL_reduced_full "irr_frac gdd_10_30"
global CTRL_reduced_ii   "irr_frac gdd_10_30_v3pm10 gdd_10_30_hepm10"
global CTRL_reduced_iv   "irr_frac gdd_10_30_v3pre30 gdd_10_30_v3he gdd_10_30_hema"

global CTRL_full_full "irr_frac pr_sum et0_sum gdd_10_30"
global CTRL_full_ii   "irr_frac pr_sum_v3pm10 et0_sum_v3pm10 gdd_10_30_v3pm10 pr_sum_hepm10 et0_sum_hepm10 gdd_10_30_hepm10"
global CTRL_full_iv   "irr_frac pr_sum_v3pre30 et0_sum_v3pre30 gdd_10_30_v3pre30 pr_sum_v3he et0_sum_v3he gdd_10_30_v3he pr_sum_hema et0_sum_hema gdd_10_30_hema"

di "=== v3proxy_macros_include.do loaded ==="
