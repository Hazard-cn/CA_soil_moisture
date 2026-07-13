* =============================================================================
* v4smstate_macros_include.do
* Purpose: Shared paths and macros for the state-based soil moisture sidecar.
* =============================================================================

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global datadir "$projdir/data/processed"
global tempdir "$projdir/temp/2026-04-21_sm_state_audit"

cap mkdir "$tempdir"

global state_ready_dta  "$tempdir/sm_state_analysis_ready.dta"
global state_wide_dta   "$tempdir/sm_state_panel_wide.dta"
global state_thresh_csv "$tempdir/sm_state_thresholds.csv"
global state_diag_csv   "$tempdir/sm_state_diagnostics.csv"
global state_raw_csv    "$tempdir/sm_raw_descriptives.csv"
global state_desc_csv   "$tempdir/sm_state_descriptives.csv"
global state_wetlean_csv "$tempdir/sm_state_wet_leaning_summary.csv"
global state_model_all_csv "$tempdir/sm_state_model_all.csv"
global state_model_main_csv "$tempdir/sm_state_model_main.csv"
global state_model_neg_csv "$tempdir/sm_state_model_v3pm10.csv"

global STATE_WINDOWS "full v3pre30 v3pm10"
global STATE_MAIN_WINDOWS "full v3pre30"
global STATE_SCHEMES "pooled maize_zone"
global STATE_SCHEME_SHORTS "pl mz"
global STATE_SOURCES "gleam gleam swsm swsm era era"
global STATE_LAYERS  "surface rootzone surface rootzone surface rootzone"
global STATE_SM_LABELS "GLEAM-Sfc GLEAM-Root SWSM-L1 SWSM-L3 ERA5L-L1 ERA5L-L3"
global STATE_SM_BASES "gleam_sms_mean gleam_smrz_mean swsm_l1_mean swsm_l3_mean era5l_swvl1_mean era5l_swvl3_mean"
global STATE_PREFIXES "gsms gsmrz ssl1 ssl3 esl1 esl3"

di "=== v4smstate_macros_include.do loaded ==="
