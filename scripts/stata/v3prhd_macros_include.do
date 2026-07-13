* =============================================================================
* v3prhd_macros_include.do
* Purpose: Shared macros for precipitation-based hot-dry regressions/report
* =============================================================================

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global builddir "$projdir/data_build/data/processed"
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

* Controls: no aridity, GDD capped at 30C
global CTRL_full    irr_frac pr_sum et0_sum gdd_10_30
global CTRL_v3pre30 irr_frac pr_sum_v3pre30 et0_sum_v3pre30 gdd_10_30_v3pre30
global CTRL_v3pm10  irr_frac pr_sum_v3pm10 et0_sum_v3pm10 gdd_10_30_v3pm10
global CTRL_hepm10  irr_frac pr_sum_hepm10 et0_sum_hepm10 gdd_10_30_hepm10
global CTRL_v3he    irr_frac pr_sum_v3he et0_sum_v3he gdd_10_30_v3he
global CTRL_hema    irr_frac pr_sum_hema et0_sum_hema gdd_10_30_hema

* Four cuts
global RHS_spec1_cut_i  ca D_full hdd_ge32 ///
    SR_x_D_full SR_x_Heat_full
global RHS_spec2_cut_i  $RHS_spec1_cut_i ///
    D_x_Heat_full SR_x_D_x_Heat_full
global RHS_spec3_cut_i  $RHS_spec1_cut_i ///
    HotDryPr_full SR_x_HotDryPr_full
global RHS_spec4_cut_i  ca HotDryPr_full SR_x_HotDryPr_full

global RHS_spec1_cut_ii  ca ///
    D_v3pm10 hdd_ge32_v3pm10 SR_x_D_v3pm10 SR_x_Heat_v3pm10 ///
    D_hepm10 hdd_ge32_hepm10 SR_x_D_hepm10 SR_x_Heat_hepm10
global RHS_spec2_cut_ii  $RHS_spec1_cut_ii ///
    D_x_Heat_v3pm10 SR_x_D_x_Heat_v3pm10 ///
    D_x_Heat_hepm10 SR_x_D_x_Heat_hepm10
global RHS_spec3_cut_ii  $RHS_spec1_cut_ii ///
    HotDryPr_v3pm10 SR_x_HotDryPr_v3pm10 ///
    HotDryPr_hepm10 SR_x_HotDryPr_hepm10
global RHS_spec4_cut_ii  ca ///
    HotDryPr_v3pm10 SR_x_HotDryPr_v3pm10 ///
    HotDryPr_hepm10 SR_x_HotDryPr_hepm10

global RHS_spec1_cut_iii  ca ///
    D_v3he hdd_ge32_v3he SR_x_D_v3he SR_x_Heat_v3he ///
    D_hema hdd_ge32_hema SR_x_D_hema SR_x_Heat_hema
global RHS_spec2_cut_iii  $RHS_spec1_cut_iii ///
    D_x_Heat_v3he SR_x_D_x_Heat_v3he ///
    D_x_Heat_hema SR_x_D_x_Heat_hema
global RHS_spec3_cut_iii  $RHS_spec1_cut_iii ///
    HotDryPr_v3he SR_x_HotDryPr_v3he ///
    HotDryPr_hema SR_x_HotDryPr_hema
global RHS_spec4_cut_iii  ca ///
    HotDryPr_v3he SR_x_HotDryPr_v3he ///
    HotDryPr_hema SR_x_HotDryPr_hema

global RHS_spec1_cut_iv  ca ///
    D_v3pre30 hdd_ge32_v3pre30 SR_x_D_v3pre30 SR_x_Heat_v3pre30 ///
    D_v3he hdd_ge32_v3he SR_x_D_v3he SR_x_Heat_v3he ///
    D_hema hdd_ge32_hema SR_x_D_hema SR_x_Heat_hema
global RHS_spec2_cut_iv  $RHS_spec1_cut_iv ///
    D_x_Heat_v3pre30 SR_x_D_x_Heat_v3pre30 ///
    D_x_Heat_v3he SR_x_D_x_Heat_v3he ///
    D_x_Heat_hema SR_x_D_x_Heat_hema
global RHS_spec3_cut_iv  $RHS_spec1_cut_iv ///
    HotDryPr_v3pre30 SR_x_HotDryPr_v3pre30 ///
    HotDryPr_v3he SR_x_HotDryPr_v3he ///
    HotDryPr_hema SR_x_HotDryPr_hema
global RHS_spec4_cut_iv  ca ///
    HotDryPr_v3pre30 SR_x_HotDryPr_v3pre30 ///
    HotDryPr_v3he SR_x_HotDryPr_v3he ///
    HotDryPr_hema SR_x_HotDryPr_hema
