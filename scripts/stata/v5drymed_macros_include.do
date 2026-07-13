* =============================================================================
* v5drymed_macros_include.do
* Purpose: Shared macros for drought-only dry-side moderated mediation.
* =============================================================================

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global datadir "$projdir/data/processed"
global builddir "$projdir/data_build/data/processed"
global tempdir "$projdir/temp/2026-04-21_sm_state_audit"
global v5rundir "$projdir/temp/2026-04-22_v5drymed_run"
global outdir "$v5rundir/tables"
global figdir "$v5rundir/figures"
global logdir "$v5rundir/logs"

cap mkdir "$v5rundir"
cap mkdir "$outdir"
cap mkdir "$figdir"
cap mkdir "$logdir"

global v5ready_dta "$datadir/v5drymed_analysis_ready.dta"
global v5diag_csv "$outdir/v5drymed_diagnostics.csv"
global v5coef_csv "$outdir/v5drymed_model8_coefficients.csv"
global v5ce_csv "$outdir/v5drymed_conditional_effects.csv"
global v5boot_csv "$outdir/v5drymed_bootstrap.csv"
global v5hetcoef_csv "$outdir/v5drymed_heterogeneity_coefficients.csv"
global v5hetce_csv "$outdir/v5drymed_heterogeneity_effects.csv"
global v5hetskip_csv "$outdir/v5drymed_heterogeneity_skips.csv"
global v5sign_csv "$outdir/v5drymed_sign_diagnostic.csv"

global CTRL_full_drymed "irr_frac pr_sum et0_sum aridity gdd_10_30"

global DRY_SOURCE_TOKENS "gleam_sms gleam_smrz swsm_l1 swsm_l3 era5l_swvl1 era5l_swvl3"
global DRY_PREFIXES "gsms gsmrz ssl1 ssl3 esl1 esl3"
global DRY_SOURCE_DEPTHS "gleam_surface gleam_rootzone swsm_surface swsm_rootzone era5l_surface era5l_rootzone"
global DRY_SM_LABELS `" "GLEAM-Sfc" "GLEAM-Root" "SWSM-L1" "SWSM-L3" "ERA5L-L1" "ERA5L-L3" "'

global V5_SAMPLE_TAGS "dd_bl_p10 dd_bl_p20 dd_pl_p25 dd_mz_p25 ds_bl_p10 ds_bl_p20 ds_pl_p25 ds_mz_p25 ddf_bl_p10 ddf_bl_p20 ddf_pl_p25 ddf_mz_p25"
global V5_SAMPLE_FAMILIES "dd dd dd dd ds ds ds ds ddf ddf ddf ddf"
global V5_SAMPLE_SCHEMES "bl bl pl mz bl bl pl mz bl bl pl mz"
global V5_SAMPLE_PCTS "p10 p20 p25 p25 p10 p20 p25 p25 p10 p20 p25 p25"

global V5_MAIN_TAGS "ds_pl_p25 ds_mz_p25 ddf_pl_p25 ddf_mz_p25"
global V5_MAIN_FAMILIES "ds ds ddf ddf"
global V5_MAIN_SCHEMES "pl mz pl mz"
global V5_MAIN_PCTS "p25 p25 p25 p25"

global ZONE_LIST "NE HHH SW SH NW Other"
global IRR_LIST "low_irr high_irr"

di "=== v5drymed_macros_include.do loaded ==="
