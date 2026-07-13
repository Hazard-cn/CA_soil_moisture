* =============================================================================
* v3decomp_macros_include.do
* Purpose: Shared paths and macros for full-season FE decomposition analysis
* =============================================================================

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global outdata  "$projdir/data/processed"
global outdir   "$projdir/output/tables"
global figdir   "$projdir/output/figures"
global logdir   "$projdir/output/logs"
global repdir   "$projdir/output/reports"

cap mkdir "$outdata"
cap mkdir "$outdir"
cap mkdir "$figdir"
cap mkdir "$logdir"
cap mkdir "$repdir"

global decomp_infile           "$outdata/v3_analysis_ready.dta"
global decomp_panel            "$outdata/v3decomp_analysis_ready.dta"
global decomp_profiles         "$outdir/v3decomp_profile_constants.dta"
global decomp_profiles_csv     "$outdir/v3decomp_profile_constants.csv"
global decomp_coef_dta         "$outdir/v3decomp_equation_coefficients.dta"
global decomp_coef_csv         "$outdir/v3decomp_equation_coefficients.csv"
global decomp_point_dta        "$outdir/v3decomp_profile_point_estimates.dta"
global decomp_point_csv        "$outdir/v3decomp_profile_point_estimates.csv"
global decomp_boot_dryrun_dta  "$outdir/v3decomp_bootstrap_dryrun_reps.dta"
global decomp_boot_dryrun_sum  "$outdir/v3decomp_bootstrap_dryrun_summary.dta"
global decomp_boot_dryrun_csv  "$outdir/v3decomp_bootstrap_dryrun_summary.csv"
global decomp_boot_reps_dta    "$outdir/v3decomp_bootstrap_reps.dta"
global decomp_boot_summary_dta "$outdir/v3decomp_bootstrap_summary.dta"
global decomp_boot_summary_csv "$outdir/v3decomp_bootstrap_summary.csv"
global decomp_validation_dta   "$outdir/v3decomp_validation.dta"
global decomp_validation_csv   "$outdir/v3decomp_validation.csv"

global DECOMP_MEDIATOR gleam_sms_mean
global DECOMP_CTRL irr_frac pr_sum et0_sum aridity gdd_ge10

global DECOMP_L2_RHS D_full W_full hdd_ge32 D_x_Heat_full ca ///
    SR_x_D_full SR_x_Heat_full SR_x_W_full SR_x_D_x_Heat_full

global DECOMP_L3_RHS D_full W_full hdd_ge32 D_x_Heat_full ca ///
    SR_x_D_full SR_x_Heat_full SR_x_W_full SR_x_D_x_Heat_full ///
    $DECOMP_MEDIATOR SM_x_D_full SM_x_H_full

global DECOMP_L2_COEFS D_full W_full hdd_ge32 D_x_Heat_full ca ///
    SR_x_D_full SR_x_Heat_full SR_x_W_full SR_x_D_x_Heat_full ///
    $DECOMP_CTRL

global DECOMP_L3_COEFS D_full W_full hdd_ge32 D_x_Heat_full ca ///
    SR_x_D_full SR_x_Heat_full SR_x_W_full SR_x_D_x_Heat_full ///
    $DECOMP_MEDIATOR SM_x_D_full SM_x_H_full ///
    $DECOMP_CTRL

global DECOMP_SAMPLE_VARS ln_yield $DECOMP_MEDIATOR ///
    D_full W_full hdd_ge32 D_x_Heat_full ca ///
    SR_x_D_full SR_x_Heat_full SR_x_W_full SR_x_D_x_Heat_full ///
    SM_x_D_full SM_x_H_full ///
    $DECOMP_CTRL grid_id year main_sample

global DECOMP_MAIN_PROFILES baseline d_only h_only dh_p75
global DECOMP_ALT_PROFILES dh_p90 joint_tail
global DECOMP_ALL_PROFILES baseline d_only h_only dh_p75 dh_p90 joint_tail
