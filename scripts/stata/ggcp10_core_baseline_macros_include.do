* =============================================================================
* ggcp10_core_baseline_macros_include.do
* Purpose: Shared macros for the compact full-season baseline-only suite.
* =============================================================================

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global builddir "$projdir/data_build/data/processed"
global suitedir "$projdir/temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite"
global statedir "$projdir/temp/2026-04-21_sm_state_audit"
global logdir "$suitedir/logs"
global corebase_dta "$suitedir/v3_analysis_ready_ggcp10_harvarea_agg.dta"
global core_ready_dta "$suitedir/ggcp10_core_baseline_analysis_ready.dta"
global core_diag_csv "$suitedir/ggcp10_core_baseline_diagnostics.csv"
global core_coef_csv "$suitedir/ggcp10_core_baseline_coefficients.csv"

cap mkdir "$suitedir"
cap mkdir "$logdir"

global CORE_CTRL_FULL "hdd_ge32 pr_sum et0_sum gdd_10_30 irr_frac aridity"
global CORE_CTRL_NOHEAT "pr_sum et0_sum gdd_10_30 irr_frac aridity"

di "=== ggcp10_core_baseline_macros_include.do loaded ==="
