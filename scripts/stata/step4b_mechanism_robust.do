* =============================================================================
* step4b_mechanism_robust.do — Strengthening SM Mechanism Evidence
* Purpose: Multiple indirect tests for SM mediation channel
* Author: YangSu / Claude Code
* Date: 2026-03-12
* Dependencies: 00_preamble.do, reghdfe, estout
* =============================================================================

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/00_preamble.do"

log using "$logdir/step4b_mechanism_robust_20260312.log", replace

di "============================================================"
di "Step 4B: Strengthening SM Mechanism Evidence"
di "============================================================"

* =============================================================================
* Part A: SM Anomaly Attenuation
* Rationale: SM anomaly = within-grid deviation, transparent display of
*            what grid FE already does. Equivalent to grid FE + SM level.
* =============================================================================

di _n "=== Part A: SM Anomaly Attenuation ==="

* Construct anomalies for root zone and surface
bysort grid_id: egen smrz_grid_mean = mean(gleam_smrz_mean)
gen smrz_anomaly = gleam_smrz_mean - smrz_grid_mean
label var smrz_anomaly "Root zone SM anomaly (within-grid)"

bysort grid_id: egen sms_grid_mean = mean(gleam_sms_mean)
gen sms_anomaly = gleam_sms_mean - sms_grid_mean
label var sms_anomaly "Surface SM anomaly (within-grid)"

* Descriptive stats
sum smrz_anomaly sms_anomaly, detail
corr smrz_anomaly D_season W_season

eststo clear

* (A1) Baseline (no SM)
eststo a_base: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

* (A2) + Root zone SM anomaly
eststo a_smrz_anom: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat smrz_anomaly $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

* (A3) + Root zone SM anomaly + dry days (tail risk)
eststo a_smrz_tails: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat ///
	smrz_anomaly drydays_gleam_smrz_le_basep10 $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

* (A4) + SM level (original approach, for comparison)
eststo a_sm_level: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat gleam_smrz_mean $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

esttab a_base a_smrz_anom a_smrz_tails a_sm_level ///
	using "$outdir/step4b_sm_anomaly.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("Baseline" "+SM anomaly" "+Anomaly+Tails" "+SM level") ///
	title("Step 4B-A: SM Anomaly vs Level Attenuation")

esttab a_base a_smrz_anom a_smrz_tails a_sm_level ///
	using "$outdir/step4b_sm_anomaly.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("Baseline" "+SM anomaly" "+Anomaly+Tails" "+SM level") booktabs

di _n "=== Part A complete ==="

* =============================================================================
* Part B: Surface vs Root Zone SM Comparison
* Rationale: SR works mainly through root zone moisture retention.
*            Root zone SM should attenuate more than surface SM.
* =============================================================================

di _n "=== Part B: Surface vs Root Zone SM ==="

eststo clear

* (B1) Baseline
eststo b_base: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

* (B2) + Root zone SM + dry days
eststo b_rootzone: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat ///
	gleam_smrz_mean drydays_gleam_smrz_le_basep10 $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

* (B3) + Surface SM + dry days
eststo b_surface: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat ///
	gleam_sms_mean drydays_gleam_sms_le_basep10 $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

* (B4) + SWSM L3 (deep layer 15-100cm)
eststo b_deep: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat ///
	swsm_l3_mean $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

esttab b_base b_rootzone b_surface b_deep ///
	using "$outdir/step4b_sm_layers.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("Baseline" "Root zone" "Surface" "Deep (SWSM)") ///
	title("Step 4B-B: Root Zone vs Surface SM Attenuation")

esttab b_base b_rootzone b_surface b_deep ///
	using "$outdir/step4b_sm_layers.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("Baseline" "Root zone" "Surface" "Deep (SWSM)") booktabs

di _n "=== Part B complete ==="

* =============================================================================
* Part C: Conditional SM (SM on Hot Days)
* Rationale: SM specifically during heat stress most relevant for yield.
*            smrz_mean_onhot_ge32 = mean root zone SM on days when Tmax>=32C
* =============================================================================

di _n "=== Part C: Conditional SM (Hot Day SM) ==="

eststo clear

* (C1) Baseline
eststo c_base: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

* (C2) + SM on hot days (Tmax>=32)
eststo c_smhot32: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat ///
	smrz_mean_onhot_ge32 $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

* (C3) + SM on hot days (Tmax>=35, more extreme)
eststo c_smhot35: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat ///
	smrz_mean_onhot_ge35 $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

* (C4) + Compound hot-dry days (Tmax>=32 AND SM<=P10)
eststo c_hotdry: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat ///
	hotdrydays_tmax_ge32_smrz_le_bas $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

esttab c_base c_smhot32 c_smhot35 c_hotdry ///
	using "$outdir/step4b_conditional_sm.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("Baseline" "+SM|Hot32" "+SM|Hot35" "+HotDryDays") ///
	title("Step 4B-C: Conditional SM Attenuation")

esttab c_base c_smhot32 c_smhot35 c_hotdry ///
	using "$outdir/step4b_conditional_sm.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("Baseline" "+SM|Hot32" "+SM|Hot35" "+HotDryDays") booktabs

di _n "=== Part C complete ==="

* =============================================================================
* Part D: Formal Mediation Analysis (Baron-Kenny 3-step)
* Step 1: Total effect (SR_x_D -> Y)
* Step 2: Treatment -> Mediator (SR_x_D -> SM variables)
* Step 3: Treatment + Mediator -> Y (direct effect)
* Indirect effect = Step2_coef * Step3_mediator_coef
* =============================================================================

di _n "=== Part D: Formal Mediation (Baron-Kenny) ==="

eststo clear

* --- D1: Total effect (same as baseline) ---
eststo d_total: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
local theta_total = _b[SR_x_D]
di "Total effect (SR_x_D -> Y): " `theta_total'

* --- D2a: SR_x_D -> SM root zone (path a) ---
eststo d_path_a_rz: reghdfe gleam_smrz_mean D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
local a_coef_rz = _b[SR_x_D]
local a_se_rz = _se[SR_x_D]
di "Path a (SR_x_D -> SMrz): " `a_coef_rz' " (SE=" `a_se_rz' ")"

* --- D2b: SR_x_D -> SM dry days (path a, alternative mediator) ---
eststo d_path_a_dry: reghdfe drydays_gleam_smrz_le_basep10 ///
	D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
local a_coef_dry = _b[SR_x_D]
local a_se_dry = _se[SR_x_D]
di "Path a (SR_x_D -> DryDays): " `a_coef_dry' " (SE=" `a_se_dry' ")"

* --- D2c: SR_x_D -> hot-dry days (path a) ---
eststo d_path_a_hd: reghdfe hotdrydays_tmax_ge32_smrz_le_bas ///
	D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
local a_coef_hd = _b[SR_x_D]
local a_se_hd = _se[SR_x_D]
di "Path a (SR_x_D -> HotDryDays): " `a_coef_hd' " (SE=" `a_se_hd' ")"

* --- D3: Direct effect (Y ~ SR_x_D + SM mediators) ---
eststo d_direct: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat ///
	gleam_smrz_mean drydays_gleam_smrz_le_basep10 $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
local theta_direct = _b[SR_x_D]
local b_sm = _b[gleam_smrz_mean]
local b_dry = _b[drydays_gleam_smrz_le_basep10]
di "Direct effect (SR_x_D | SM): " `theta_direct'
di "SM mean -> Y (path b): " `b_sm'
di "Dry days -> Y (path b): " `b_dry'

* --- Compute indirect effects ---
local indirect_rz = `a_coef_rz' * `b_sm'
local indirect_dry = `a_coef_dry' * `b_dry'
local indirect_total = `indirect_rz' + `indirect_dry'
local pct_mediated = (`theta_total' - `theta_direct') / `theta_total' * 100

di _n "============================================================"
di "MEDIATION SUMMARY"
di "============================================================"
di "Total effect (c):      " %9.6f `theta_total'
di "Direct effect (c'):    " %9.6f `theta_direct'
di "Indirect via SM mean:  " %9.6f `indirect_rz'
di "Indirect via dry days: " %9.6f `indirect_dry'
di "Total indirect:        " %9.6f `indirect_total'
di "% mediated (c-c')/c:   " %5.1f `pct_mediated' "%"
di "============================================================"

esttab d_total d_path_a_rz d_path_a_dry d_path_a_hd d_direct ///
	using "$outdir/step4b_mediation.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.6f) se(%9.6f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("Total(Y)" "a:SR->SMrz" "a:SR->DryD" "a:SR->HotDry" "Direct(Y)") ///
	title("Step 4B-D: Baron-Kenny Mediation Analysis") ///
	addnote("Cols 2-4: DV is SM variable. Cols 1,5: DV is ln_yield.")

esttab d_total d_path_a_rz d_path_a_dry d_path_a_hd d_direct ///
	using "$outdir/step4b_mediation.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.6f) se(%9.6f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("Total(Y)" "a:SR->SMrz" "a:SR->DryD" "a:SR->HotDry" "Direct(Y)") booktabs

di _n "=== Part D complete ==="

* =============================================================================
* Part E: SR Reduces Compound Hot-Dry Days (Direct Mechanism Test)
* Rationale: If SR reduces the count of compound hot-dry days, this is
*            direct evidence that SR improves SM specifically under stress.
* =============================================================================

di _n "=== Part E: SR Effect on Compound Stress Days ==="

eststo clear

* (E1) SR -> hot-dry days (Tmax>=32 AND SM<=P10)
eststo e_hd32_p10: reghdfe hotdrydays_tmax_ge32_smrz_le_bas ///
	D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

* (E2) SR -> hot-dry days (Tmax>=35 AND SM<=P10)
eststo e_hd35_p10: reghdfe hotdrydays_tmax_ge35_smrz_le_bas ///
	D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

* (E3) SR -> dry days (SM root zone <= P10)
eststo e_dry_rz10: reghdfe drydays_gleam_smrz_le_basep10 ///
	D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

* (E4) SR -> dry days (SM root zone <= P20)
eststo e_dry_rz20: reghdfe drydays_gleam_smrz_le_basep20 ///
	D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)

esttab e_hd32_p10 e_hd35_p10 e_dry_rz10 e_dry_rz20 ///
	using "$outdir/step4b_sr_reduces_stress.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("HotDry32" "HotDry35" "DryDays(P10)" "DryDays(P20)") ///
	title("Step 4B-E: SR Effect on Compound Stress Days") ///
	addnote("DV = count of stress days. Negative SR_x_D = SR reduces stress under drought.")

esttab e_hd32_p10 e_hd35_p10 e_dry_rz10 e_dry_rz20 ///
	using "$outdir/step4b_sr_reduces_stress.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("HotDry32" "HotDry35" "DryDays(P10)" "DryDays(P20)") booktabs

di _n "=== Part E complete ==="

* =============================================================================
* Summary
* =============================================================================

di _n "============================================================"
di "Step 4B Summary: SM Mechanism Robustness"
di "============================================================"
di "Part A: SM anomaly attenuation (transparent FE display)"
di "Part B: Root zone vs surface SM (layer specificity)"
di "Part C: Conditional SM on hot days (stress-specific)"
di "Part D: Baron-Kenny mediation (formal indirect effect)"
di "Part E: SR reduces stress days (direct mechanism)"
di "============================================================"

log close
di "=== Step 4B complete. Outputs in $outdir/step4b_*.csv ==="
