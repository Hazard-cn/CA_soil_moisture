* =============================================================================
* v6gleambl_nowet_nop30_macros_include.do
* Purpose: Shared macros for GLEAM baseline rerun without M_wet/W_w and
*          excluding v3pre30.
* =============================================================================

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global datadir "$projdir/data/processed"
global builddir "$projdir/data_build/data/processed"
global v6rundir "$projdir/temp/2026-04-23_newSMsplit"
global outdir "$v6rundir"
global logdir "$v6rundir/logs"
global v6mdsidecar "$v6rundir/v6gleambl_md_event_sidecar.dta"

cap mkdir "$v6rundir"
cap mkdir "$logdir"

global v6xready_dta "$v6rundir/v6gleambl_nowet_nop30_analysis_ready.dta"
global v6xdiag_csv "$outdir/v6gleambl_nowet_nop30_diagnostics.csv"
global v6xcoef_csv "$outdir/v6gleambl_nowet_nop30_baseline_coefficients.csv"

global V6_CTRL_FULL "hdd_ge32 pr_sum et0_sum gdd_10_30 irr_frac aridity"

global V6_MD_METRIC_CODES "mdd mds mdv"
global V6_MD_METRIC_FAMILIES `" "mdduration_dry" "mddurshare_dry" "mdseverity_dry" "'
global V6_MD_DRY_STUBS "mdd_d mds_d mdv_d"

global V6_METRIC_CODES "dur shr mdf sdf"
global V6_METRIC_FAMILIES `" "blduration_dry" "bldurshare_dry" "blseveritymean_ddf" "blseveritysum_ddf" "'
global V6_DRY_STUBS "bld_d bls_d blm_ddf blu_ddf"

global V6_DRY_PCTS "p10 p20"
global V6_WET_PCTS "p90 p80"

global V6_WINDOWS "v3he hema fullnew"
global V6_WINDOW_CODES "v3h hma fn"

global V6_SOURCE_CODES "gss gsr"
global V6_SOURCE_LAYERS "gleam_surface gleam_rootzone"
global V6_SOURCE_LABELS `" "GLEAM-Sfc" "GLEAM-Root" "'

di "=== v6gleambl_nowet_nop30_macros_include.do loaded ==="
