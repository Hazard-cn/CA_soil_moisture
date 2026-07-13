* =============================================================================
* step5_heterogeneity.do — Boundary Conditions & Heterogeneity Analysis
* Purpose: Test SR buffering heterogeneity across regions, SM, irrigation, aridity
* Author: YangSu / Claude Code
* Date: 2026-03-12
* Dependencies: 00_preamble.do, reghdfe, estout
* =============================================================================

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/00_preamble.do"

log using "$logdir/step5_heterogeneity_20260313.log", replace

di "============================================================"
di "Step 5: Heterogeneity Analysis"
di "============================================================"

* =============================================================================
* Part A: Production Region Grouping
* =============================================================================

di _n "=== Part A: Production Region Heterogeneity ==="

gen region = "Other"
replace region = "NE"    if inlist(province, "黑龙江省", "吉林省", "辽宁省", "内蒙古自治区")
replace region = "HHH"   if inlist(province, "河南省", "山东省", "河北省", "安徽省", "江苏省")
replace region = "SW"    if inlist(province, "四川省", "贵州省", "云南省") ///
                          | inlist(province, "广西壮族自治区", "重庆市")
replace region = "NW"    if inlist(province, "甘肃省", "宁夏回族自治区") ///
                          | inlist(province, "新疆维吾尔自治区", "陕西省")

tab region, mi
label var region "Maize production region (5 zones)"

* Run full Eq.1 for each region
eststo clear

foreach r in NE HHH SW NW Other {
	di _n "--- Region: `r' ---"
	eststo reg_`r': reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
		ca SR_x_D SR_x_W SR_x_Heat $CTRL ///
		if region == "`r'", ///
		absorb(grid_id year) vce(cluster grid_id)
}

esttab reg_NE reg_HHH reg_SW reg_NW reg_Other ///
	using "$outdir/step5_region.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("NE" "HHH" "SW" "NW" "Other") ///
	title("Step 5A: Heterogeneity by Maize Production Zone") ///
	addnote("NE=东北春玉米区 HHH=黄淮海夏玉米区 SW=西南山地区 NW=西北灌溉区" ///
		"Grid FE: Yes. Year FE: Yes. Cluster: grid_id.")

esttab reg_NE reg_HHH reg_SW reg_NW reg_Other ///
	using "$outdir/step5_region.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("NE" "HHH" "SW" "NW" "Other") booktabs

di _n "=== Region results exported ==="

* =============================================================================
* Part B: Soil Moisture Quartile Heterogeneity
* =============================================================================

di _n "=== Part B: SM Quartile Heterogeneity ==="

* Compute grid-level SM mean (time-invariant stratifier)
bysort grid_id: egen sm_grid_avg = mean(gleam_smrz_mean)
xtile sm_q4 = sm_grid_avg, nq(4)
label var sm_q4 "SM quartile (1=driest, 4=wettest)"
tab sm_q4, mi

eststo clear

forvalues q = 1/4 {
	di _n "--- SM quartile: `q' ---"
	eststo sm_q`q': reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
		ca SR_x_D SR_x_W SR_x_Heat $CTRL ///
		if sm_q4 == `q', ///
		absorb(grid_id year) vce(cluster grid_id)
}

esttab sm_q1 sm_q2 sm_q3 sm_q4 ///
	using "$outdir/step5_sm_quartile.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("Q1(dry)" "Q2" "Q3" "Q4(wet)") ///
	title("Step 5B: Heterogeneity by Baseline SM Quartile")

esttab sm_q1 sm_q2 sm_q3 sm_q4 ///
	using "$outdir/step5_sm_quartile.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("Q1(dry)" "Q2" "Q3" "Q4(wet)") booktabs

di _n "=== SM quartile results exported ==="

* =============================================================================
* Part C: Irrigation & Aridity Splits
* =============================================================================

di _n "=== Part C: Irrigation & Aridity Heterogeneity ==="

* Irrigation split at median
sum irr_frac, detail
local irr_med = r(p50)
gen irr_high = (irr_frac >= `irr_med') if !missing(irr_frac)
label var irr_high "High irrigation (>= median)"

* Aridity split at median
sum aridity, detail
local arid_med = r(p50)
gen arid_high = (aridity >= `arid_med') if !missing(aridity)
label var arid_high "High aridity (>= median, drier)"

eststo clear

* Irrigation subgroups
eststo irr_lo: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL ///
	if irr_high == 0, ///
	absorb(grid_id year) vce(cluster grid_id)

eststo irr_hi: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL ///
	if irr_high == 1, ///
	absorb(grid_id year) vce(cluster grid_id)

* Aridity subgroups
eststo arid_lo: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL ///
	if arid_high == 0, ///
	absorb(grid_id year) vce(cluster grid_id)

eststo arid_hi: reghdfe ln_yield D_season W_season hdd_tmax_ge32 ///
	ca SR_x_D SR_x_W SR_x_Heat $CTRL ///
	if arid_high == 1, ///
	absorb(grid_id year) vce(cluster grid_id)

esttab irr_lo irr_hi arid_lo arid_hi ///
	using "$outdir/step5_irr_aridity.csv", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("Low Irr" "High Irr" "Humid" "Arid") ///
	title("Step 5C: Heterogeneity by Irrigation and Aridity")

esttab irr_lo irr_hi arid_lo arid_hi ///
	using "$outdir/step5_irr_aridity.tex", replace ///
	se star(* 0.10 ** 0.05 *** 0.01) ///
	b(%9.4f) se(%9.4f) ///
	stats(r2 r2_a N, labels("R-squared" "Adj. R-squared" "Observations") ///
		fmt(%9.4f %9.4f %9.0f)) ///
	mtitles("Low Irr" "High Irr" "Humid" "Arid") booktabs

di _n "=== Irrigation & Aridity results exported ==="

* =============================================================================
* Summary: Key coefficients across all splits
* =============================================================================

di _n "============================================================"
di "Step 5 Summary: θ1(SR×D) and θ3(SR×Heat) across subgroups"
di "============================================================"
di "Check: θ1 stronger in dry/arid regions? θ3 stronger in hot regions?"
di "============================================================"

log close
di "=== Step 5 complete. Outputs in $outdir/step5_*.csv ==="
