* =============================================================================
* v3med_step0_preamble.do
* Purpose: Prepare data for Model 8 moderated mediation analysis.
*          - Load v3_analysis_ready.dta
*          - Confirm interaction terms exist
*          - Compute ca representative values (P25/P50/P75)
*          - Construct FE group variables for relaxation (county/city/year)
*          - Lock common sample across all 6 SM sources
*          - Export diagnostics
* Author:  YangSu + Claude
* Date:    2026-04-16
* Input:   data/processed/v3_analysis_ready.dta
* Output:  data/processed/v3med_analysis_ready.dta
*          output/tables/v3med_diagnostics.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3med_macros_include.do"

cap mkdir "$outdir"
cap mkdir "$figdir"
cap mkdir "$logdir"

log using "$logdir/v3med_step0_preamble.log", replace

* =============================================================================
* 1. LOAD DATA
* =============================================================================
use "$datadir/v3_analysis_ready.dta", clear
desc, short
di "N total = " _N

xtset grid_id year
di "Panel: " r(panelvar) " x " r(timevar)

* Confirm key variables exist
confirm variable ln_yield D_full hdd_ge32 ca
confirm variable SR_x_D_full SR_x_Heat_full
confirm variable grid_id year county_code city_code prov_code
confirm variable main_sample irr_frac

* Confirm 6 SM sources
foreach sm of global SM_SOURCES {
	confirm variable `sm'
}

di "=== All key variables confirmed ==="

* =============================================================================
* 2. CA REPRESENTATIVE VALUES (P25, P50, P75)
* =============================================================================
_pctile ca if main_sample == 1, p(25 50 75)
scalar ca_p25 = r(r1)
scalar ca_p50 = r(r2)
scalar ca_p75 = r(r3)

di "ca P25 = " %9.4f ca_p25
di "ca P50 = " %9.4f ca_p50
di "ca P75 = " %9.4f ca_p75

* Store as globals for downstream scripts
global CA_P25 = ca_p25
global CA_P50 = ca_p50
global CA_P75 = ca_p75

* =============================================================================
* 3. CONSTRUCT FE GROUP VARIABLES FOR RELAXATION
* =============================================================================

* prov_year should already exist; recreate if missing
cap confirm variable prov_year
if _rc != 0 {
	egen prov_year = group(prov_code year)
	label var prov_year "Province x Year FE"
}

* county_year
cap drop county_year
egen county_year = group(county_code year)
label var county_year "County x Year FE"

* city_year
cap drop city_year
egen city_year = group(city_code year)
label var city_year "City x Year FE"

di "FE groups constructed:"
qui levelsof grid_id if main_sample == 1
di "  grid_id  groups = " r(r)
qui levelsof county_code if main_sample == 1
di "  county   groups = " r(r)
qui levelsof city_code if main_sample == 1
di "  city     groups = " r(r)
qui levelsof prov_code if main_sample == 1
di "  province groups = " r(r)

* =============================================================================
* 4. LOCK COMMON SAMPLE (all 6 SM + D + H + ca + ln_yield non-missing)
* =============================================================================
gen v3med_common = (main_sample == 1) if !missing(main_sample)
replace v3med_common = 0 if missing(v3med_common)

* Check each SM source for missing
foreach sm of global SM_SOURCES {
	replace v3med_common = 0 if missing(`sm') & v3med_common == 1
}

* Check focal variables
foreach v in ln_yield D_full hdd_ge32 ca SR_x_D_full SR_x_Heat_full {
	replace v3med_common = 0 if missing(`v') & v3med_common == 1
}

* Check controls (full version)
foreach v of global CTRL_full_med {
	replace v3med_common = 0 if missing(`v') & v3med_common == 1
}

label var v3med_common "Common sample for v3med (all 6 SM non-missing)"

qui count if v3med_common == 1
local n_common = r(N)
qui count if main_sample == 1
local n_main = r(N)
di "main_sample N    = " `n_main'
di "v3med_common N   = " `n_common'
di "Dropped by SM    = " `n_main' - `n_common'

* =============================================================================
* 5. SUBSAMPLE VARIABLES (reuse v3sub definitions)
* =============================================================================
* maize_zone
cap confirm variable maize_zone
if _rc != 0 {
	gen maize_zone = "Other"
	replace maize_zone = "NE"  if inlist(province, "黑龙江省", "吉林省", "辽宁省", "内蒙古自治区")
	replace maize_zone = "HHH" if inlist(province, "河南省", "山东省", "河北省", "安徽省", "江苏省")
	replace maize_zone = "SW"  if inlist(province, "四川省", "贵州省", "云南省") ///
	                            | inlist(province, "广西壮族自治区", "重庆市")
	replace maize_zone = "NW"  if inlist(province, "甘肃省", "宁夏回族自治区") ///
	                            | inlist(province, "新疆维吾尔自治区", "陕西省")
	replace maize_zone = "SH"  if inlist(province, "广东省", "福建省", "浙江省", "江西省") ///
	                            | inlist(province, "海南省", "湖南省", "湖北省")
	label var maize_zone "Maize production zone (5+Other)"
}

* irr_group
cap confirm variable irr_group
if _rc != 0 {
	qui sum irr_frac if main_sample == 1, detail
	local irr_med = r(p50)
	gen irr_group = ""
	replace irr_group = "low_irr"  if irr_frac < `irr_med' & !missing(irr_frac)
	replace irr_group = "high_irr" if irr_frac >= `irr_med' & !missing(irr_frac)
	label var irr_group "Irrigation group (median split)"
}

tab maize_zone if v3med_common == 1
tab irr_group  if v3med_common == 1

* =============================================================================
* 6. DIAGNOSTICS TABLE
* =============================================================================
tempname pf
postfile `pf' str30 item str60 value using "$outdir/v3med_diagnostics_raw.dta", replace

post `pf' ("N_main_sample")   ("`n_main'")
post `pf' ("N_v3med_common")  ("`n_common'")
post `pf' ("ca_P25")          (string(ca_p25, "%9.4f"))
post `pf' ("ca_P50")          (string(ca_p50, "%9.4f"))
post `pf' ("ca_P75")          (string(ca_p75, "%9.4f"))

* SM descriptive stats
foreach sm of global SM_SOURCES {
	qui sum `sm' if v3med_common == 1
	post `pf' ("`sm'_mean") (string(r(mean), "%12.6f"))
	post `pf' ("`sm'_sd")   (string(r(sd), "%12.6f"))
	post `pf' ("`sm'_N")    (string(r(N), "%12.0f"))
}

* Zone sample sizes
foreach z of global ZONE_LIST {
	qui count if v3med_common == 1 & maize_zone == "`z'"
	post `pf' ("N_zone_`z'") ("`r(N)'")
}

* Irrigation group sizes
foreach g of global IRR_LIST {
	qui count if v3med_common == 1 & irr_group == "`g'"
	post `pf' ("N_irr_`g'") ("`r(N)'")
}

postclose `pf'

preserve
use "$outdir/v3med_diagnostics_raw.dta", clear
export delimited using "$outdir/v3med_diagnostics.csv", replace
restore

cap erase "$outdir/v3med_diagnostics_raw.dta"

* =============================================================================
* 7. SAVE
* =============================================================================
compress
save "$datadir/v3med_analysis_ready.dta", replace

log close
di "=== v3med_step0_preamble.do COMPLETE ==="
