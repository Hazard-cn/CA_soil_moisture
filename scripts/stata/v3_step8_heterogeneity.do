* =============================================================================
* v3_step8_heterogeneity.do
* Purpose: Heterogeneity analysis — 5 maize production zones + irrigation split
*          Spec(2) across 6 windows, grid+year FE, cluster(grid_id)
* Author:  YangSu + Claude
* Date:    2026-04-05
* Input:   data/processed/v3_analysis_ready.dta
* Output:  output/tables/v3_step8_zone.csv
*          output/tables/v3_step8_irrigation.csv
* =============================================================================

clear all
set more off
set seed 42

* Load macros
do "C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata/v3_macros_include.do"

log using "$logdir/v3_step8_heterogeneity_20260405.log", replace

use "$outdata/v3_analysis_ready.dta", clear
xtset grid_id year

* =============================================================================
* PART A: Five Maize Production Zones
* =============================================================================
di "========================================================"
di "PART A: Five Maize Production Zones"
di "========================================================"

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

* Diagnostic: zone distribution
tab maize_zone if main_sample == 1
di _n "--- Provinces in Other zone ---"
tab province if maize_zone == "Other" & main_sample == 1

* --- Postfile setup ---
tempname pf
postfile `pf' str6 zone str10 window ///
    b_SRD se_SRD p_SRD ///
    b_SRH se_SRH p_SRH ///
    b_DH se_DH p_DH ///
    b_SRDH se_SRDH p_SRDH ///
    N r2 ///
    using "$outdir/v3_step8_zone.dta", replace

* --- Loop over zones x windows ---
foreach z in NE HHH SW SH NW Other {

    * Check minimum N
    qui count if maize_zone == "`z'" & main_sample == 1
    local nz = r(N)
    di _n "Zone `z': N = `nz'"

    if `nz' < 500 {
        di "WARNING: zone `z' has only `nz' obs — skipping"
        continue
    }

    foreach win in full v3pre30 v3pm10 hepm10 v3he hema {

        local wlbl "_`win'"
        if "`win'" == "full" {
            local hsfx ""
            local ctrl "$CTRL_full"
        }
        else {
            local hsfx "_`win'"
            local ctrl "${CTRL_`win'}"
        }

        di "--- `z' x `win' ---"

        * Spec(2) regression
        cap noi reghdfe ln_yield ///
            D`wlbl' W`wlbl' hdd_ge32`hsfx' ca ///
            SR_x_D`wlbl' SR_x_W`wlbl' SR_x_Heat`wlbl' ///
            D_x_Heat`wlbl' SR_x_D_x_Heat`wlbl' ///
            `ctrl' if main_sample == 1 & maize_zone == "`z'", ///
            absorb(grid_id year) vce(cluster grid_id)

        if _rc != 0 {
            di "WARNING: regression failed for `z' x `win' (rc=" _rc ")"
            post `pf' ("`z'") ("`win'") (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (0) (.)
            continue
        }

        local dfr = e(df_r)
        post `pf' ("`z'") ("`win'") ///
            (_b[SR_x_D`wlbl']) (_se[SR_x_D`wlbl']) ///
            (2*ttail(`dfr', abs(_b[SR_x_D`wlbl']/_se[SR_x_D`wlbl']))) ///
            (_b[SR_x_Heat`wlbl']) (_se[SR_x_Heat`wlbl']) ///
            (2*ttail(`dfr', abs(_b[SR_x_Heat`wlbl']/_se[SR_x_Heat`wlbl']))) ///
            (_b[D_x_Heat`wlbl']) (_se[D_x_Heat`wlbl']) ///
            (2*ttail(`dfr', abs(_b[D_x_Heat`wlbl']/_se[D_x_Heat`wlbl']))) ///
            (_b[SR_x_D_x_Heat`wlbl']) (_se[SR_x_D_x_Heat`wlbl']) ///
            (2*ttail(`dfr', abs(_b[SR_x_D_x_Heat`wlbl']/_se[SR_x_D_x_Heat`wlbl']))) ///
            (e(N)) (e(r2))
    }
}

postclose `pf'

* Export
preserve
use "$outdir/v3_step8_zone.dta", clear
format b_* se_* %9.6f
format p_* %7.4f
list, sep(6) noobs
export delimited using "$outdir/v3_step8_zone.csv", replace
restore

* =============================================================================
* PART B: Irrigation Split
* =============================================================================
di _n "========================================================"
di "PART B: Irrigation Split (median of irr_frac)"
di "========================================================"

* Compute median within estimation sample
qui sum irr_frac if main_sample == 1, detail
local irr_med = r(p50)
di "Irrigation median = " `irr_med'

gen irr_high = (irr_frac >= `irr_med') if !missing(irr_frac)
label var irr_high "High irrigation (>=median)"
tab irr_high if main_sample == 1

* --- Postfile setup ---
tempname pf2
postfile `pf2' str10 irr_group str10 window ///
    b_SRD se_SRD p_SRD ///
    b_SRH se_SRH p_SRH ///
    b_DH se_DH p_DH ///
    b_SRDH se_SRDH p_SRDH ///
    N r2 ///
    using "$outdir/v3_step8_irrigation.dta", replace

* --- Loop over irrigation groups x windows ---
foreach ig in 0 1 {
    local glbl = cond(`ig' == 0, "low_irr", "high_irr")

    foreach win in full v3pre30 v3pm10 hepm10 v3he hema {

        local wlbl "_`win'"
        if "`win'" == "full" {
            local hsfx ""
            local ctrl "$CTRL_full"
        }
        else {
            local hsfx "_`win'"
            local ctrl "${CTRL_`win'}"
        }

        di "--- `glbl' x `win' ---"

        cap noi reghdfe ln_yield ///
            D`wlbl' W`wlbl' hdd_ge32`hsfx' ca ///
            SR_x_D`wlbl' SR_x_W`wlbl' SR_x_Heat`wlbl' ///
            D_x_Heat`wlbl' SR_x_D_x_Heat`wlbl' ///
            `ctrl' if main_sample == 1 & irr_high == `ig', ///
            absorb(grid_id year) vce(cluster grid_id)

        if _rc != 0 {
            di "WARNING: regression failed for `glbl' x `win' (rc=" _rc ")"
            post `pf2' ("`glbl'") ("`win'") (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (0) (.)
            continue
        }

        local dfr = e(df_r)
        post `pf2' ("`glbl'") ("`win'") ///
            (_b[SR_x_D`wlbl']) (_se[SR_x_D`wlbl']) ///
            (2*ttail(`dfr', abs(_b[SR_x_D`wlbl']/_se[SR_x_D`wlbl']))) ///
            (_b[SR_x_Heat`wlbl']) (_se[SR_x_Heat`wlbl']) ///
            (2*ttail(`dfr', abs(_b[SR_x_Heat`wlbl']/_se[SR_x_Heat`wlbl']))) ///
            (_b[D_x_Heat`wlbl']) (_se[D_x_Heat`wlbl']) ///
            (2*ttail(`dfr', abs(_b[D_x_Heat`wlbl']/_se[D_x_Heat`wlbl']))) ///
            (_b[SR_x_D_x_Heat`wlbl']) (_se[SR_x_D_x_Heat`wlbl']) ///
            (2*ttail(`dfr', abs(_b[SR_x_D_x_Heat`wlbl']/_se[SR_x_D_x_Heat`wlbl']))) ///
            (e(N)) (e(r2))
    }
}

postclose `pf2'

* Export
preserve
use "$outdir/v3_step8_irrigation.dta", clear
format b_* se_* %9.6f
format p_* %7.4f
list, sep(6) noobs
export delimited using "$outdir/v3_step8_irrigation.csv", replace
restore

log close
di "=== v3_step8_heterogeneity.do COMPLETE ==="
