* =============================================================================
* step_compound_interaction.do — Drought×Heat compound extremes & SR buffering
* Purpose: Test D×Heat amplification and SR×D×Heat triple interaction
* Author: YangSu / Claude Code
* Date: 2026-03-15
* Blueprint: Step ED2 (compound drought-heat amplification)
*   Tests: β4(D×Heat) < 0? SR buffers compound extremes via θ4(SR×D×Heat)?
* =============================================================================

* --- Load preamble ---
global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/00_preamble.do"

* --- Log ---
local today : di %tdCYND date(c(current_date), "DMY")
log using "$logdir/step_compound_`today'.log", replace

di "============================================================"
di "Compound Extremes: Drought×Heat Interaction & SR Buffering"
di "Date: `c(current_date)' `c(current_time)'"
di "N = " _N
di "============================================================"

* =============================================================================
* Section 1: Construct compound interaction variables
* =============================================================================

di ""
di "--- Constructing compound interaction variables ---"

* D x Heat interaction (climate-based)
gen D_x_Heat = D_season * hdd_tmax_ge32
label var D_x_Heat "Drought x Heat (D * HDD>=32)"

* SR x D x Heat triple interaction
gen SR_x_D_x_Heat = ca * D_season * hdd_tmax_ge32
label var SR_x_D_x_Heat "SR x Drought x Heat (triple)"

* SR x Hotdrydays (SM-mediated compound measure)
* Note: hotdrydays_tmax_ge32_smrz_le_basep10 loads as truncated name (32 char limit)
gen SR_x_HotDry = ca * hotdrydays_tmax_ge32_smrz_le_bas
label var SR_x_HotDry "SR x Hot-dry days (SM-mediated)"

di "Compound variables created: D_x_Heat, SR_x_D_x_Heat, SR_x_HotDry"

* =============================================================================
* Section 2: Diagnostics — Multicollinearity and compound event prevalence
* =============================================================================

di ""
di "=== Diagnostics: Correlation & Prevalence ==="

* Correlation matrix
corr D_season hdd_tmax_ge32 D_x_Heat
di ""

* Summary stats for compound variables
sum D_x_Heat SR_x_D_x_Heat hotdrydays_tmax_ge32_smrz_le_bas SR_x_HotDry, detail
di ""

* Prevalence of compound events
local n_d_heat = 0
local n_hotdry = 0
count if D_x_Heat > 0
local n_d_heat = r(N)
count if hotdrydays_tmax_ge32_smrz_le_bas > 0
local n_hotdry = r(N)

di "Observations with D×Heat > 0: " `n_d_heat' " (" round(`n_d_heat'/_N*100, 0.1) "%)"
di "Observations with hotdrydays > 0: " `n_hotdry' " (" round(`n_hotdry'/_N*100, 0.1) "%)"

* =============================================================================
* Section 3: Progressive specification (Main models)
* =============================================================================

di ""
di "=== Estimating progressive models (5 specifications) ==="

eststo clear

* Model 1 (Baseline) — Reproduce Step 1 full model for comparison
eststo m1: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"
estadd local Compound "—"
di "Model 1 (Baseline): " e(N) " obs, R2 = " round(e(r2), 0.001)

* Model 2 — Add D×Heat interaction
eststo m2: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	D_x_Heat ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"
estadd local Compound "D×Heat"
di "Model 2 (+D×Heat): " e(N) " obs, R2 = " round(e(r2), 0.001)

* Model 3 — Add SR×D×Heat triple interaction
eststo m3: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	D_x_Heat ///
	ca SR_x_D SR_x_W SR_x_Heat SR_x_D_x_Heat $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"
estadd local Compound "D×Heat, SR×D×H"
di "Model 3 (+SR×D×Heat): " e(N) " obs, R2 = " round(e(r2), 0.001)

* Model 4 — Use SM-mediated hotdrydays compound measure
eststo m4: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	hotdrydays_tmax_ge32_smrz_le_bas ///
	ca SR_x_D SR_x_W SR_x_Heat SR_x_HotDry $CTRL, ///
	absorb(grid_id year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_year "Yes"
estadd local Compound "HotDryDays"
di "Model 4 (HotDryDays): " e(N) " obs, R2 = " round(e(r2), 0.001)

* Model 5 — Province-year FE (robustness check)
eststo m5: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	D_x_Heat ///
	ca SR_x_D SR_x_W SR_x_Heat SR_x_D_x_Heat $CTRL, ///
	absorb(grid_id prov_year) vce(cluster grid_id)
estadd local FE_grid "Yes"
estadd local FE_provyr "Yes"
estadd local Compound "D×Heat, SR×D×H"
di "Model 5 (Prov-Yr FE): " e(N) " obs, R2 = " round(e(r2), 0.001)

* =============================================================================
* Section 4: Export table (CSV and LaTeX)
* =============================================================================

di ""
di "--- Exporting tables ---"

esttab m1 m2 m3 m4 m5 using "$outdir/step_compound_interaction.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	keep(D_season W_season hdd_tmax_ge32 D_x_Heat ///
	     ca SR_x_D SR_x_W SR_x_Heat SR_x_D_x_Heat ///
	     hotdrydays_tmax_ge32_smrz_le_bas SR_x_HotDry) ///
	order(D_season hdd_tmax_ge32 D_x_Heat W_season ///
	      ca SR_x_D SR_x_Heat SR_x_D_x_Heat SR_x_W ///
	      hotdrydays_tmax_ge32_smrz_le_bas SR_x_HotDry) ///
	stats(r2 r2_a N FE_grid FE_year FE_provyr Compound, ///
		labels("R-squared" "Adj. R-squared" "Observations" ///
		       "Grid FE" "Year FE" "Prov-Yr FE" "Compound terms") ///
		fmt(%9.4f %9.4f %9.0f %s %s %s %s)) ///
	title("Compound Drought×Heat Interaction & SR Buffering") ///
	mtitles("Baseline" "+D×Heat" "+SR*D×H" "HotDry" "ProvYr FE")

esttab m1 m2 m3 m4 m5 using "$outdir/step_compound_interaction.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) booktabs ///
	keep(D_season W_season hdd_tmax_ge32 D_x_Heat ///
	     ca SR_x_D SR_x_W SR_x_Heat SR_x_D_x_Heat ///
	     hotdrydays_tmax_ge32_smrz_le_bas SR_x_HotDry) ///
	order(D_season hdd_tmax_ge32 D_x_Heat W_season ///
	      ca SR_x_D SR_x_Heat SR_x_D_x_Heat SR_x_W ///
	      hotdrydays_tmax_ge32_smrz_le_bas SR_x_HotDry) ///
	stats(r2 r2_a N FE_grid FE_year FE_provyr Compound, ///
		labels("R-squared" "Adj. R-squared" "Observations" ///
		       "Grid FE" "Year FE" "Prov-Yr FE" "Compound terms") ///
		fmt(%9.4f %9.4f %9.0f %s %s %s %s)) ///
	title("Compound Drought×Heat Interaction & SR Buffering") ///
	mtitles("Baseline" "+D×Heat" "+SR*D×H" "HotDry" "ProvYr FE")

di "Tables exported: step_compound_interaction.{csv,tex}"

* =============================================================================
* Section 5: Key coefficient report
* =============================================================================

di ""
di "=== Key Results ==="
di ""

* Model 2: Does heat amplify drought losses?
estimates restore m2
local beta4_m2 = _b[D_x_Heat]
local se4_m2   = _se[D_x_Heat]
local sig_m2   = 2 * (1 - normal(abs(`beta4_m2'/`se4_m2')))
di "Model 2: β4(D×Heat) = " round(`beta4_m2', 0.0001) " (SE: " round(`se4_m2', 0.0001) ")"
if `sig_m2' < 0.01 di "  → *** Significant at 1% level"
else if `sig_m2' < 0.05 di "  → ** Significant at 5% level"
else if `sig_m2' < 0.10 di "  → * Significant at 10% level"
else di "  → Not significant"
if `beta4_m2' < 0 di "  ✓ Heat amplifies drought losses (β4 < 0)"
else di "  ⚠ Unexpected: β4 > 0 (additive or substitution effect)"
di ""

* Model 3: Triple interaction
estimates restore m3
local beta4_m3   = _b[D_x_Heat]
local theta4_m3  = _b[SR_x_D_x_Heat]
local se4_m3     = _se[D_x_Heat]
local se_th4_m3  = _se[SR_x_D_x_Heat]
di "Model 3: β4(D×Heat) = " round(`beta4_m3', 0.0001) " (SE: " round(`se4_m3', 0.0001) ")"
di "Model 3: θ4(SR×D×Heat) = " round(`theta4_m3', 0.0001) " (SE: " round(`se_th4_m3', 0.0001) ")"
if `theta4_m3' > 0 di "  ✓ SR provides additional buffering of compound extremes (θ4 > 0)"
else di "  ⚠ SR does not buffer compound extremes (θ4 ≤ 0)"
di ""

* Stability check: θ1 and θ3 across models
di "--- Stability Check: Original Buffering Effects ---"
estimates restore m1
local th1_m1 = _b[SR_x_D]
local th3_m1 = _b[SR_x_Heat]
estimates restore m3
local th1_m3 = _b[SR_x_D]
local th3_m3 = _b[SR_x_Heat]
di "θ1(SR×D):    M1=" round(`th1_m1', 0.0001) " → M3=" round(`th1_m3', 0.0001) ///
   " (change: " round((`th1_m3'-`th1_m1')/`th1_m1'*100, 0.1) "%)"
di "θ3(SR×Heat): M1=" round(`th3_m1', 0.0001) " → M3=" round(`th3_m3', 0.0001) ///
   " (change: " round((`th3_m3'-`th3_m1')/`th3_m1'*100, 0.1) "%)"
if abs((`th1_m3'-`th1_m1')/`th1_m1') < 0.05 & abs((`th3_m3'-`th3_m1')/`th3_m1') < 0.05 di "  ✓ Stable (<5% change)"
else di "  ⚠ Substantial change: possible omitted variable bias in M1"
di ""

* =============================================================================
* Section 6: Heat threshold sensitivity (optional sub-table)
* =============================================================================

di ""
di "=== Heat Threshold Sensitivity for Compound Interaction ==="

eststo clear
local hcount = 0

foreach thresh in 30 32 35 {
	local hcount = `hcount' + 1

	* Build compound and triple interactions for this threshold
	cap drop D_x_H_tmp SR_x_Heat_tmp SR_x_DxH_tmp
	gen D_x_H_tmp     = D_season * hdd_tmax_ge`thresh'
	gen SR_x_Heat_tmp = ca * hdd_tmax_ge`thresh'
	gen SR_x_DxH_tmp  = ca * D_season * hdd_tmax_ge`thresh'

	eststo h`hcount': reghdfe ln_yield D_season W_season hdd_tmax_ge`thresh' ///
		D_x_H_tmp ///
		ca SR_x_D SR_x_W SR_x_Heat_tmp SR_x_DxH_tmp $CTRL, ///
		absorb(grid_id year) vce(cluster grid_id)
	estadd local Heat_thresh "`thresh'C"
	estadd local FE_grid "Yes"
	estadd local FE_year "Yes"

	di ""
	di "--- HDD >= `thresh'°C ---"
	di "β4(D×Heat): " round(_b[D_x_H_tmp], 0.0001) " (SE: " round(_se[D_x_H_tmp], 0.0001) ")"
	di "θ4(SR×D×H): " round(_b[SR_x_DxH_tmp], 0.0001) " (SE: " round(_se[SR_x_DxH_tmp], 0.0001) ")"
}

esttab h1 h2 h3 using "$outdir/step_compound_heat_sensitivity.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	keep(D_season hdd_tmax_ge30 hdd_tmax_ge32 hdd_tmax_ge35 ///
	     D_x_H_tmp SR_x_Heat_tmp SR_x_DxH_tmp ca SR_x_D SR_x_W) ///
	stats(r2 r2_a N Heat_thresh FE_grid FE_year, ///
		labels("R-squared" "Adj. R-squared" "Observations" ///
		       "Heat threshold" "Grid FE" "Year FE") ///
		fmt(%9.4f %9.4f %9.0f %s %s %s)) ///
	title("Heat Threshold Sensitivity: Compound Interaction") ///
	mtitles("HDD≥30C" "HDD≥32C" "HDD≥35C")

esttab h1 h2 h3 using "$outdir/step_compound_heat_sensitivity.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) booktabs ///
	keep(D_season hdd_tmax_ge30 hdd_tmax_ge32 hdd_tmax_ge35 ///
	     D_x_H_tmp SR_x_Heat_tmp SR_x_DxH_tmp ca SR_x_D SR_x_W) ///
	stats(r2 r2_a N Heat_thresh FE_grid FE_year, ///
		labels("R-squared" "Adj. R-squared" "Observations" ///
		       "Heat threshold" "Grid FE" "Year FE") ///
		fmt(%9.4f %9.4f %9.0f %s %s %s)) ///
	title("Heat Threshold Sensitivity: Compound Interaction") ///
	mtitles("HDD≥30C" "HDD≥32C" "HDD≥35C")

cap drop D_x_H_tmp SR_x_Heat_tmp SR_x_DxH_tmp

di ""
di "Heat sensitivity tables exported: step_compound_heat_sensitivity.{csv,tex}"

* =============================================================================
* Section 7: Close
* =============================================================================

di ""
di "============================================================"
di "Step: Compound Interaction — COMPLETE"
di "============================================================"

log close
