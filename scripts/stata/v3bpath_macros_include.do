* =============================================================================
* v3bpath_macros_include.do
* Purpose: Shared paths and macros for the v3bpath unified audit line.
* =============================================================================

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global datadir  "$projdir/data/processed"
global outdir   "$projdir/output/tables"
global logdir   "$projdir/output/logs"
global qadir    "$projdir/quality_reports"
global plandir  "$projdir/quality_reports/plans"

cap mkdir "$outdir"
cap mkdir "$logdir"
cap mkdir "$qadir"
cap mkdir "$plandir"

global BPATH_WINDOWS "full v3pre30 v3pm10 v3he hepm10 hema"
global BPATH_SM_BASES "gleam_sms_mean gleam_smrz_mean swsm_l1_mean swsm_l3_mean era5l_swvl1_mean era5l_swvl3_mean"
global BPATH_SOURCES "gleam gleam swsm swsm era era"
global BPATH_LAYERS  "surface rootzone surface rootzone surface rootzone"
global BPATH_SM_LABELS "GLEAM-Sfc GLEAM-Root SWSM-L1 SWSM-L3 ERA5L-L1 ERA5L-L3"

global BPATH_FULL_SAMPLE  "bpath_full6_sample"
global BPATH_STAGE_SAMPLE "bpath_stage6_sample"

global BPATH_CTRL_REDUCED "irr_frac gdd_10_30 W_full"
global BPATH_CTRL_FULL    "irr_frac gdd_10_30 W_full pr_sum et0_sum aridity"
global BPATH_LADDERS      "L0 L1 L2 L3"

di "=== v3bpath_macros_include.do loaded ==="
