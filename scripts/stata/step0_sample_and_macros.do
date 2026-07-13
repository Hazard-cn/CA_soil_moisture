* =============================================================================
* step0_sample_and_macros.do — Lock main sample, macros, discretization, exposure
* Purpose: Single source of truth for all downstream compound-stress scripts.
*          All subsequent scripts load analysis_main_sample.dta, never re-import CSV.
*          Now uses NEW CSV with county/city codes (independent of 00_preamble.do).
* Author: YangSu / Claude Code
* Date: 2026-03-22 (updated 2026-03-22 for county/city + SM mechanism v2)
* Dependencies: reghdfe
* =============================================================================

clear all
set more off
set seed 42

* =============================================================================
* 0. Path macros (replicated from preamble — step0 is self-contained)
* =============================================================================
global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global datadir  "C:/YangSu/00_Project/CA_mechanism/data/master"
global outdir   "$projdir/output/tables"
global figdir   "$projdir/output/figures"
global logdir   "$projdir/output/logs"

cap mkdir "$outdir"
cap mkdir "$figdir"
cap mkdir "$logdir"

log using "$logdir/step0_sample_and_macros.log", replace

di "============================================================"
di "step0_sample_and_macros.do — Lock main sample & macros"
di "Date: $S_DATE $S_TIME"
di "============================================================"

* =============================================================================
* 1. Data loading — NEW CSV with county/city (NOT via preamble)
* =============================================================================
* NOTE: 00_preamble.do is NOT called here. This script is self-contained.
*       Preamble loads the OLD CSV (data_v1_with_climate.csv) without county/city.
*       This script loads the NEW CSV with county_name/county_code/city_name/city_code.
*       Existing scripts that call preamble are unaffected.

import delimited "$datadir/data_v1_with_climate_with_county_city.csv", ///
	clear case(preserve)

di "=== Raw data loaded: " _N " observations ==="

* =============================================================================
* 2. Sample filtering (replicated from preamble)
* =============================================================================
keep if china_mask == 1
keep if yield_tons_ha > 0 & !missing(yield_tons_ha)
keep if maize_area_km2 > 0 & !missing(maize_area_km2)
drop if missing(ln_yield)
drop if missing(ca)
drop if missing(SPEI_season)

di "=== Sample size after filtering: " _N " ==="

* =============================================================================
* 3. Variable construction (replicated from preamble)
* =============================================================================

* --- D (drought) and W (wetness) from SPEI decomposition ---
gen D_season = max(0, -SPEI_season)
gen W_season = max(0,  SPEI_season)
label var D_season "Drought stress: max(0, -SPEI)"
label var W_season "Wetness stress: max(0, SPEI)"

* --- SR variable (already exists as `ca`) ---
label var ca "Straw return adoption ratio"

* --- Main heat indicator ---
label var hdd_tmax_ge32 "Hot degree days (Tmax >= 32C)"

* --- Interaction terms (from preamble) ---
gen SR_x_D    = ca * D_season
gen SR_x_W    = ca * W_season
gen SR_x_Heat = ca * hdd_tmax_ge32
label var SR_x_D    "SR x Drought"
label var SR_x_W    "SR x Wetness"
label var SR_x_Heat "SR x Heat (HDD>=32)"

* --- Controls ---
global CTRL irr_frac pre_sum et0_sum wd_aridity_et0divpre gdd_30

* --- Panel setup ---
xtset grid_id year

di "=== Variable construction complete. Panel: grid_id x year. N = " _N " ==="

* =============================================================================
* 4. Generate compound interaction variables
* =============================================================================

* D x H compound term
cap drop D_x_Heat
gen D_x_Heat = D_season * hdd_tmax_ge32
label var D_x_Heat "Drought x Heat compound (D_season x HDD>=32)"

* SR x D x H triple interaction (core estimand)
cap drop SR_x_D_x_Heat
gen SR_x_D_x_Heat = ca * D_season * hdd_tmax_ge32
label var SR_x_D_x_Heat "SR x Drought x Heat (core estimand)"

* =============================================================================
* 5. Define main RHS macros
* =============================================================================

* Full compound model RHS (hierarchy-complete)
global RHS_COMPOUND D_season W_season hdd_tmax_ge32 ca ///
	SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat $CTRL

di "RHS_COMPOUND = $RHS_COMPOUND"

* Soil controls (time-invariant properties, for mechanism v2)
global SOIL_CTRL clay_0_5cm_01deg sand_0_5cm_01deg bdod_0_5cm_01deg ///
	phh2o_0_5cm_01deg silt_0_5cm_01deg

di "SOIL_CTRL = $SOIL_CTRL"

* Soil x Year extended controls (for specification sensitivity)
foreach sv in clay_0_5cm_01deg sand_0_5cm_01deg bdod_0_5cm_01deg phh2o_0_5cm_01deg {
	forvalues y = 2017/2019 {
		cap drop `sv'_y`y'
		gen `sv'_y`y' = `sv' * (year == `y')
	}
}
global SOIL_YEAR clay_0_5cm_01deg_y2017 clay_0_5cm_01deg_y2018 clay_0_5cm_01deg_y2019 ///
	sand_0_5cm_01deg_y2017 sand_0_5cm_01deg_y2018 sand_0_5cm_01deg_y2019 ///
	bdod_0_5cm_01deg_y2017 bdod_0_5cm_01deg_y2018 bdod_0_5cm_01deg_y2019 ///
	phh2o_0_5cm_01deg_y2017 phh2o_0_5cm_01deg_y2018 phh2o_0_5cm_01deg_y2019

di "SOIL_YEAR = $SOIL_YEAR"

* =============================================================================
* 6. County/City FE infrastructure (NEW)
* =============================================================================

di ""
di "============================================================"
di "COUNTY/CITY FE INFRASTRUCTURE"
di "============================================================"

* Verify county variables exist (county_code is numeric in CSV)
capture confirm variable county_code
if _rc != 0 {
	di as error "ERROR: county_code not found — wrong CSV?"
	exit 198
}
capture confirm numeric variable county_code
if _rc != 0 {
	di as error "WARNING: county_code is string, converting to numeric"
	destring county_code, replace force
}

* Generate numeric FE group variables
cap drop county_id
egen county_id = group(county_code)
label var county_id "County FE group (from county_code)"

cap drop county_year
egen county_year = group(county_id year)
label var county_year "County x Year group"

cap drop city_id
egen city_id = group(city_code)
label var city_id "City FE group (from city_code)"

* --- County diagnostics ---
di ""
di "--- County structure diagnostics ---"

* Number of unique counties
qui tab county_id
di "Unique counties: " r(r)

* Grids per county distribution
tempvar grids_per_county
bysort county_id: gen `grids_per_county' = _N / 4  // approx grids (4 years)
bysort county_id: gen byte _first_county = (_n == 1)

di ""
di "--- Grids per county (approx, one row per county) ---"
sum `grids_per_county' if _first_county == 1, detail

* Counties with very few observations (<=4 obs total, i.e., ~1 grid)
tempvar obs_per_county
bysort county_id: gen `obs_per_county' = _N
count if `obs_per_county' <= 4 & _first_county == 1
di "Counties with <= 4 obs (roughly 1 grid): " r(N)

count if `obs_per_county' <= 8 & _first_county == 1
di "Counties with <= 8 obs (roughly 2 grids): " r(N)

drop _first_county

* =============================================================================
* 7. Lock main estimation sample
* =============================================================================

* Run base compound model to define main_sample via e(sample)
reghdfe ln_yield $RHS_COMPOUND, absorb(grid_id year) vce(cluster grid_id)

cap drop main_sample
gen main_sample = e(sample)
label var main_sample "Main estimation sample (compound model, grid+year FE)"

local MAIN_N = e(N)
di "============================================================"
di "MAIN SAMPLE N = `MAIN_N'"
di "============================================================"

global MAIN_N = `MAIN_N'

count if main_sample == 1
assert r(N) == `MAIN_N'

* Verify county_id has no missing in main_sample
count if missing(county_id) & main_sample == 1
local n_missing_county = r(N)
di "Missing county_id in main_sample: `n_missing_county'"
assert `n_missing_county' == 0

* =============================================================================
* 8. Discretization variables (all on main_sample)
* =============================================================================

* --- D terciles ---
cap drop D_bin3
xtile D_bin3 = D_season if main_sample == 1, nq(3)
label define D_bin3_lbl 1 "Normal" 2 "Moderate" 3 "Severe"
label values D_bin3 D_bin3_lbl
label var D_bin3 "Drought tercile (on main_sample)"

* --- H terciles ---
cap drop H_bin3
xtile H_bin3 = hdd_tmax_ge32 if main_sample == 1, nq(3)
label define H_bin3_lbl 1 "Cool" 2 "Moderate" 3 "Hot"
label values H_bin3 H_bin3_lbl
label var H_bin3 "Heat tercile (on main_sample)"

* --- SR binary (median split) ---
cap drop SR_high
sum ca if main_sample == 1, detail
local sr_median = r(p50)
gen SR_high = (ca >= `sr_median') if main_sample == 1
label var SR_high "SR high (>= median ca on main_sample)"
di "SR median split at ca = `sr_median'"

* --- SM quartiles (rootzone, for existing scripts) ---
cap drop sm_quartile
xtile sm_quartile = gleam_smrz_mean if main_sample == 1, nq(4)
label define sm_q_lbl 1 "Q1(Driest)" 2 "Q2" 3 "Q3" 4 "Q4(Wettest)"
label values sm_quartile sm_q_lbl
label var sm_quartile "SM rootzone quartile (on main_sample)"

* --- SM binary P25 (rootzone, for existing scripts) ---
cap drop sm_low
sum gleam_smrz_mean if main_sample == 1, detail
local sm_p25 = r(p25)
gen sm_low = (gleam_smrz_mean < `sm_p25') if main_sample == 1
label var sm_low "SM rootzone below P25 (on main_sample)"
di "SM rootzone P25 threshold = `sm_p25'"

* --- SM surface quartiles (for mechanism v2) ---
cap drop sms_quartile
xtile sms_quartile = gleam_sms_mean if main_sample == 1, nq(4)
label define sms_q_lbl 1 "Q1(Driest)" 2 "Q2" 3 "Q3" 4 "Q4(Wettest)"
label values sms_quartile sms_q_lbl
label var sms_quartile "SM surface quartile (on main_sample)"

* --- Stress corner (high D x high H) ---
cap drop stress_corner
gen stress_corner = (D_bin3 == 3 & H_bin3 == 3) if main_sample == 1
label var stress_corner "Stress corner: top tercile D x top tercile H"

* --- Irrigation binary (median split, for VZ2025 test) ---
cap drop irr_high
sum irr_frac if main_sample == 1, detail
local irr_median = r(p50)
gen irr_high = (irr_frac >= `irr_median') if main_sample == 1
label var irr_high "High irrigation (>= median irr_frac)"
di "Irrigation median split at irr_frac = `irr_median'"

* Report discretization
tab D_bin3 if main_sample == 1
tab H_bin3 if main_sample == 1
tab SR_high if main_sample == 1
tab sm_quartile if main_sample == 1
tab sms_quartile if main_sample == 1
tab stress_corner if main_sample == 1
tab irr_high if main_sample == 1

* Cross-tab D x H
di ""
di "=== D x H cross-tabulation (main_sample) ==="
tab D_bin3 H_bin3 if main_sample == 1

* =============================================================================
* 9. Exposure frequency statistics (32C and 35C)
* =============================================================================

di ""
di "============================================================"
di "EXPOSURE FREQUENCY STATISTICS"
di "============================================================"

* --- HDD >= 32C ---
di ""
di "--- hdd_tmax_ge32 (main_sample) ---"
sum hdd_tmax_ge32 if main_sample == 1, detail
local hdd32_mean = r(mean)
local hdd32_med  = r(p50)
local hdd32_sd   = r(sd)
local hdd32_N    = r(N)

count if hdd_tmax_ge32 == 0 & main_sample == 1
local hdd32_zero = r(N)
local hdd32_zero_pct = 100 * `hdd32_zero' / `hdd32_N'

di "32C: mean = " %6.2f `hdd32_mean' " days, median = " %6.2f `hdd32_med' ///
	", zero share = " %5.1f `hdd32_zero_pct' "%"

* --- HDD >= 35C ---
di ""
di "--- hdd_tmax_ge35 (main_sample) ---"
sum hdd_tmax_ge35 if main_sample == 1, detail
local hdd35_mean = r(mean)
local hdd35_med  = r(p50)
local hdd35_sd   = r(sd)
local hdd35_N    = r(N)

count if hdd_tmax_ge35 == 0 & main_sample == 1
local hdd35_zero = r(N)
local hdd35_zero_pct = 100 * `hdd35_zero' / `hdd35_N'

di "35C: mean = " %6.2f `hdd35_mean' " days, median = " %6.2f `hdd35_med' ///
	", zero share = " %5.1f `hdd35_zero_pct' "%"

* --- Export to CSV ---
tempname fh
file open `fh' using "$outdir/step0_exposure_frequency.csv", write replace
file write `fh' "threshold,mean_hdd,median_hdd,sd_hdd,N,zero_count,zero_share_pct" _n
file write `fh' "32C," %8.4f (`hdd32_mean') "," %8.4f (`hdd32_med') "," ///
	%8.4f (`hdd32_sd') "," (`hdd32_N') "," (`hdd32_zero') "," ///
	%6.2f (`hdd32_zero_pct') _n
file write `fh' "35C," %8.4f (`hdd35_mean') "," %8.4f (`hdd35_med') "," ///
	%8.4f (`hdd35_sd') "," (`hdd35_N') "," (`hdd35_zero') "," ///
	%6.2f (`hdd35_zero_pct') _n
file close `fh'

di ""
di "Exposure frequency exported to: $outdir/step0_exposure_frequency.csv"

* =============================================================================
* 10. Region encoding (one-time, using province strings)
* =============================================================================

capture confirm string variable province
if _rc != 0 {
	di as error "ERROR: province variable not found or not string type"
	exit 198
}

cap drop region
gen region = "Other"
replace region = "NE"  if inlist(province, "黑龙江省", "吉林省", "辽宁省", "内蒙古自治区")
replace region = "HHH" if inlist(province, "河南省", "山东省", "河北省", "安徽省", "江苏省")
replace region = "SW"  if inlist(province, "四川省", "贵州省", "云南省") ///
	| inlist(province, "广西壮族自治区", "重庆市")
replace region = "NW"  if inlist(province, "甘肃省", "宁夏回族自治区") ///
	| inlist(province, "新疆维吾尔自治区", "陕西省")
label var region "5-zone region classification"

cap drop region_id
encode region, gen(region_id)
label var region_id "Region (numeric)"

cap drop regyr
egen regyr = group(region_id year)
label var regyr "Region x Year group"

di ""
di "=== Region distribution (main_sample) ==="
tab region if main_sample == 1

count if region == "Other" & main_sample == 1
local n_other = r(N)
di "Observations in 'Other' region: `n_other'"

* =============================================================================
* 11. Save canonical analysis dataset
* =============================================================================

cap mkdir "$projdir/data/processed"

* Clean up any leftover temp variables before saving
cap drop __*

compress
save "$projdir/data/processed/analysis_main_sample.dta", replace

di ""
di "============================================================"
di "STEP 0 COMPLETE"
di "Main sample N = $MAIN_N"
di "Saved: data/processed/analysis_main_sample.dta"
di "Exposure: output/tables/step0_exposure_frequency.csv"
di "============================================================"
di ""
di "NEW in this version:"
di "  - county_id, county_year, city_id for county/city FE"
di "  - $SOIL_CTRL macro for mechanism v2"
di "  - sms_quartile (surface SM) for mechanism v2"
di "  - irr_high (irrigation median split) for VZ2025 test"
di ""
di "DOWNSTREAM SCRIPTS: use analysis_main_sample.dta"
di `"  use "$projdir/data/processed/analysis_main_sample.dta", clear"'
di "  count if main_sample == 1"
di `"  assert r(N) == $MAIN_N"'
di "============================================================"

log close
