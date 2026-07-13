* =============================================================================
* v3sub_step0_subsamples.do
* Purpose: Build subsample tags and diagnostics for v3 subsample reruns
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3sub_macros_include.do"

log using "$logdir/v3sub_step0_subsamples.log", replace

use "$outdata/v3_analysis_ready.dta", clear
xtset grid_id year

gen maize_zone = "Other"
replace maize_zone = "NE"  if inlist(province, "黑龙江省", "吉林省", "辽宁省", "内蒙古自治区")
replace maize_zone = "HHH" if inlist(province, "河南省", "山东省", "河北省", "安徽省", "江苏省")
replace maize_zone = "SW"  if inlist(province, "四川省", "贵州省", "云南省") ///
                            | inlist(province, "广西壮族自治区", "重庆市")
replace maize_zone = "NW"  if inlist(province, "甘肃省", "宁夏回族自治区") ///
                            | inlist(province, "新疆维吾尔自治区", "陕西省")
replace maize_zone = "SH"  if inlist(province, "广东省", "福建省", "浙江省", "江西省") ///
                            | inlist(province, "海南省", "湖南省", "湖北省")

qui sum irr_frac if main_sample == 1, detail
local irr_med = r(p50)
gen irr_group = ""
replace irr_group = "low_irr"  if irr_frac < `irr_med' & !missing(irr_frac)
replace irr_group = "high_irr" if irr_frac >= `irr_med' & !missing(irr_frac)

label var maize_zone "Maize production zone (5+Other)"
label var irr_group "Irrigation group from main-sample median split"

tempname pf
postfile `pf' str12 split_type str12 subgroup double N_main_sample str24 threshold_if_any ///
    using "$subdiag", replace

foreach z in NE HHH SW SH NW Other {
    qui count if main_sample == 1 & maize_zone == "`z'"
    post `pf' ("zone") ("`z'") (r(N)) ("")
}

foreach g in low_irr high_irr {
    qui count if main_sample == 1 & irr_group == "`g'"
    post `pf' ("irrigation") ("`g'") (r(N)) ("`irr_med'")
}
postclose `pf'

tab maize_zone if main_sample == 1
tab irr_group if main_sample == 1
di "irr_frac median within main_sample = " %9.6f `irr_med'

compress
save "$subdata", replace

preserve
use "$subdiag", clear
export delimited using "$outdir/v3sub_subsample_defs.csv", replace
restore

log close
di "=== v3sub_step0_subsamples.do COMPLETE ==="
