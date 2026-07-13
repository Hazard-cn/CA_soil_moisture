* =============================================================================
* step2_apath.do — Channel Validation + a-path: SR → SM Mediators
* Purpose: (A) Verify SM is drought→yield damage pathway
*          (B) Test whether SR improves SM under stress (a-path)
*          (C) Falsification mediator (t2m_mean)
* Author: YangSu / Claude Code
* Date: 2026-03-17
* Dependencies: 00_preamble.do, reghdfe, estout
* =============================================================================

* --- Preamble ---
global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/00_preamble.do"

* --- Log ---
local today : di %tdCYND date(c(current_date), "DMY")
log using "$logdir/step2_apath_`today'.log", replace

* --- Mechanism controls (drop et0_sum = bad control) ---
global CTRL_mech "irr_frac pre_sum wd_aridity_et0divpre gdd_30"

di "============================================================"
di "  PART A: Channel Validation — Is SM a drought→yield pathway?"
di "============================================================"

* -------------------------------------------------------------------------
* A1: Climate extremes → SM deterioration
*     DryDays = f(Drought, Heat, controls) + grid + year FE
* -------------------------------------------------------------------------
eststo clear

* A1a: D → DryDays (root zone, P10)
eststo ch_dry: reghdfe drydays_gleam_smrz_le_basep10 ///
    D_season W_season hdd_tmax_ge32 $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

* A1b: D → SM mean (root zone)
eststo ch_smrz: reghdfe gleam_smrz_mean ///
    D_season W_season hdd_tmax_ge32 $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

* A1c: D → Compound hot-dry days
eststo ch_hotdry: reghdfe hotdrydays_tmax_ge32_smrz_le_bas ///
    D_season W_season hdd_tmax_ge32 $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

* Export Table: Climate → SM
esttab ch_dry ch_smrz ch_hotdry using "$outdir/step2a_climate_to_sm.csv", ///
    replace b(%9.4f) se(%9.4f) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(D_season W_season hdd_tmax_ge32) ///
    stats(r2 N, labels("R-squared" "N") fmt(%9.4f %9.0f)) ///
    mtitles("DryDays_rz" "SM_rz_mean" "HotDryDays") ///
    title("Part A1: Climate Extremes -> SM Variables")

di ""
di "--- A1 Key checks ---"
estimates restore ch_dry
di "D → DryDays (expect > 0): " _b[D_season] " from ch_dry"
di "  D_season coef = " %9.4f _b[D_season] ", SE = " %9.4f _se[D_season]
estimates restore ch_smrz
di "  D → SM_rz (expect < 0): coef = " %9.4f _b[D_season] ", SE = " %9.4f _se[D_season]
estimates restore ch_hotdry
di "  Heat → HotDryDays: coef = " %9.4f _b[hdd_tmax_ge32] ", SE = " %9.4f _se[hdd_tmax_ge32]

* -------------------------------------------------------------------------
* A2: SM deterioration → Yield loss (controlling climate extremes)
* -------------------------------------------------------------------------
eststo clear

* A2a: Yield ~ D + Heat (no SM) — baseline
eststo y_base: reghdfe ln_yield ///
    D_season W_season hdd_tmax_ge32 $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

* A2b: Yield ~ D + Heat + DryDays
eststo y_dry: reghdfe ln_yield ///
    D_season W_season hdd_tmax_ge32 ///
    drydays_gleam_smrz_le_basep10 $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

* A2c: Yield ~ D + Heat + SM_rz_mean
eststo y_smrz: reghdfe ln_yield ///
    D_season W_season hdd_tmax_ge32 ///
    gleam_smrz_mean $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

* A2d: Yield ~ D + Heat + DryDays + SM_rz_mean
eststo y_both: reghdfe ln_yield ///
    D_season W_season hdd_tmax_ge32 ///
    drydays_gleam_smrz_le_basep10 gleam_smrz_mean $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

* Export Table: SM → Yield
esttab y_base y_dry y_smrz y_both using "$outdir/step2a_sm_to_yield.csv", ///
    replace b(%9.4f) se(%9.4f) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(D_season W_season hdd_tmax_ge32 ///
         drydays_gleam_smrz_le_basep10 gleam_smrz_mean) ///
    stats(r2 N, labels("R-squared" "N") fmt(%9.4f %9.0f)) ///
    mtitles("No SM" "+DryDays" "+SM_rz" "+Both") ///
    title("Part A2: SM Variables -> Yield (controlling climate)")

di ""
di "--- A2 Key checks ---"
estimates restore y_base
local D_base = _b[D_season]
di "  D → Yield (no SM): " %9.4f `D_base'
estimates restore y_dry
local D_with_dry = _b[D_season]
di "  D → Yield (+DryDays): " %9.4f `D_with_dry'
di "  DryDays → Yield (expect < 0): " %9.4f _b[drydays_gleam_smrz_le_basep10]
di "  D attenuation: " %5.1f ((`D_base' - `D_with_dry') / `D_base' * 100) "%"


di ""
di "============================================================"
di "  PART B: a-path — Does SR improve SM under stress?"
di "============================================================"

* -------------------------------------------------------------------------
* B1: a-path regressions (4 mediators)
*     M = f(SR, D, Heat, SR×D, SR×Heat, controls) + grid + year FE
* -------------------------------------------------------------------------
eststo clear

* B1a: SR → Root-zone SM mean
eststo a_smrz: reghdfe gleam_smrz_mean ///
    D_season W_season hdd_tmax_ge32 ///
    ca SR_x_D SR_x_W SR_x_Heat $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

* B1b: SR → Root-zone dry days (P10)
eststo a_dry: reghdfe drydays_gleam_smrz_le_basep10 ///
    D_season W_season hdd_tmax_ge32 ///
    ca SR_x_D SR_x_W SR_x_Heat $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

* B1c: SR → Compound hot-dry days (Tmax≥32 & SM≤P10)
eststo a_hotdry: reghdfe hotdrydays_tmax_ge32_smrz_le_bas ///
    D_season W_season hdd_tmax_ge32 ///
    ca SR_x_D SR_x_W SR_x_Heat $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

* B1d: SR → Surface SM mean (weaker expected)
eststo a_sms: reghdfe gleam_sms_mean ///
    D_season W_season hdd_tmax_ge32 ///
    ca SR_x_D SR_x_W SR_x_Heat $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

* Export Table 3: a-path
esttab a_smrz a_dry a_hotdry a_sms using "$outdir/step2b_apath.csv", ///
    replace b(%9.4f) se(%9.4f) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(ca SR_x_D SR_x_W SR_x_Heat D_season W_season hdd_tmax_ge32) ///
    stats(r2 N, labels("R-squared" "N") fmt(%9.4f %9.0f)) ///
    mtitles("SM_rz_mean" "DryDays_rz" "HotDryDays" "SM_sfc_mean") ///
    title("Table 3: a-path — SR Effects on SM Mediators")

* Also export LaTeX version
esttab a_smrz a_dry a_hotdry a_sms using "$outdir/step2b_apath.tex", ///
    replace b(%9.4f) se(%9.4f) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(ca SR_x_D SR_x_W SR_x_Heat) ///
    stats(r2 N, labels("R-squared" "N") fmt(%9.4f %9.0f)) ///
    mtitles("SM\_rz" "DryDays" "HotDryDays" "SM\_sfc") ///
    title("a-path: SR Effects on SM Mediators") booktabs

di ""
di "--- B1 Key a-path coefficients ---"
estimates restore a_smrz
di "  SR×D → SM_rz (expect > 0): " %9.4f _b[SR_x_D] " (" %9.4f _se[SR_x_D] ")"
di "  SR×Heat → SM_rz (expect ≈ 0): " %9.6f _b[SR_x_Heat] " (" %9.6f _se[SR_x_Heat] ")"
estimates restore a_dry
di "  SR×D → DryDays (expect < 0): " %9.4f _b[SR_x_D] " (" %9.4f _se[SR_x_D] ")"
estimates restore a_hotdry
di "  SR×D → HotDryDays: " %9.4f _b[SR_x_D] " (" %9.4f _se[SR_x_D] ")"

* Store a-path coefficients for Sobel test later
estimates restore a_dry
local a_dry_coef = _b[SR_x_D]
local a_dry_se   = _se[SR_x_D]
di ""
di "  [Stored for Sobel] a_dry_coef = " %9.4f `a_dry_coef' ", a_dry_se = " %9.4f `a_dry_se'

* Permanently store a-path estimates (survive eststo clear)
foreach est in a_smrz a_dry a_hotdry a_sms {
    estimates restore `est'
    estimates store `est'_perm
}

di ""
di "============================================================"
di "  PART C: Falsification Mediator — t2m_mean"
di "============================================================"

* SR should NOT affect grid-level atmospheric temperature
eststo clear
eststo a_t2m: reghdfe t2m_mean ///
    D_season W_season hdd_tmax_ge32 ///
    ca SR_x_D SR_x_W SR_x_Heat $CTRL_mech, ///
    absorb(grid_id year) vce(cluster grid_id)

esttab a_t2m using "$outdir/step2c_falsification.csv", ///
    replace b(%9.4f) se(%9.4f) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(ca SR_x_D SR_x_W SR_x_Heat) ///
    stats(r2 N, labels("R-squared" "N") fmt(%9.4f %9.0f)) ///
    mtitles("t2m_mean") ///
    title("Falsification: SR -> Atmospheric Temperature")

di ""
di "--- Falsification check ---"
di "  ca → t2m (expect ≈ 0): " %9.4f _b[ca] " (" %9.4f _se[ca] ")"
di "  SR×D → t2m (expect ≈ 0): " %9.4f _b[SR_x_D] " (" %9.4f _se[SR_x_D] ")"
di "  SR×Heat → t2m (expect ≈ 0): " %9.6f _b[SR_x_Heat] " (" %9.6f _se[SR_x_Heat] ")"


di ""
di "============================================================"
di "  PART D: Bonferroni Correction for a-path"
di "============================================================"

* 4 mediators × 3 interaction terms = 12 tests
* Bonferroni threshold: 0.05 / 12 = 0.00417

local bonf_alpha = 0.05 / 12
di "Bonferroni-corrected alpha (12 tests): " %7.5f `bonf_alpha'
di ""

foreach est in a_smrz_perm a_dry_perm a_hotdry_perm a_sms_perm {
    estimates restore `est'
    di "--- `est' ---"
    foreach v in SR_x_D SR_x_W SR_x_Heat {
        local coef = _b[`v']
        local se = _se[`v']
        local t = `coef' / `se'
        local p = 2 * ttail(e(df_r), abs(`t'))
        local sig "n.s."
        if `p' < 0.05 local sig "* (nominal only)"
        if `p' < `bonf_alpha' local sig "*** (Bonferroni)"
        di "  `v': coef=" %9.4f `coef' " p=" %7.5f `p' " `sig'"
    }
    di ""
}


di ""
di "============================================================"
di "  PART E: a-path with prov×year FE (robustness)"
di "============================================================"

eststo clear

eststo ap_smrz: reghdfe gleam_smrz_mean ///
    D_season W_season hdd_tmax_ge32 ///
    ca SR_x_D SR_x_W SR_x_Heat $CTRL_mech, ///
    absorb(grid_id prov_year) vce(cluster grid_id)

eststo ap_dry: reghdfe drydays_gleam_smrz_le_basep10 ///
    D_season W_season hdd_tmax_ge32 ///
    ca SR_x_D SR_x_W SR_x_Heat $CTRL_mech, ///
    absorb(grid_id prov_year) vce(cluster grid_id)

esttab ap_smrz ap_dry using "$outdir/step2e_apath_provyear.csv", ///
    replace b(%9.4f) se(%9.4f) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(ca SR_x_D SR_x_W SR_x_Heat) ///
    stats(r2 N, labels("R-squared" "N") fmt(%9.4f %9.0f)) ///
    mtitles("SM_rz (prov×yr)" "DryDays (prov×yr)") ///
    title("a-path Robustness: Province × Year FE")

di "--- a-path under prov×year FE ---"
estimates restore ap_smrz
di "  SR×D → SM_rz: " %9.4f _b[SR_x_D] " (" %9.4f _se[SR_x_D] ")"
estimates restore ap_dry
di "  SR×D → DryDays: " %9.4f _b[SR_x_D] " (" %9.4f _se[SR_x_D] ")"


di ""
di "============================================================"
di "  Step 2 Complete"
di "============================================================"

log close
