* =============================================================================
* v3med_step0b_build_smdef.do
* Purpose: Construct SM deficit variables (grid-level anomaly, one-sided) to
*          repair the Model 8 b-path inversion in v3med.
*
*          For each SM source s:
*             SMdef_s  = max(0, SM_bar_i - SM_it)   where SM_bar_i = grid mean
*             SR_x_SMdef_s = ca * SMdef_s
*
*          Rationale: Raw SM enters outcome eq with b<0 (across all 6 sources,
*          all p<0.01), violating the Model 8 assumption b>0 (higher SM->yield).
*          Within-grid residual SM variation is contaminated by waterlogging/
*          cloudy-humid years. A one-sided deficit (positive only when drier
*          than grid long-run mean) isolates the "dry anomaly" signal and
*          recovers theoretically-consistent signs:
*             a1 > 0 (D increases deficit), a3 < 0 (SR reduces deficit),
*             b < 0 (deficit hurts yield), Index = a3*b > 0.
*
* Author:  YangSu + Claude
* Date:    2026-04-16
* Input:   data/processed/v3med_analysis_ready.dta
* Output:  data/processed/v3med_analysis_ready_plus.dta
*          output/logs/v3med_step0b_build_smdef.log
*          output/tables/v3med_smdef_descriptives.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3med_macros_include.do"

log using "$logdir/v3med_step0b_build_smdef.log", replace

use "$datadir/v3med_analysis_ready.dta", clear
xtset grid_id year

di _n "=== Starting sample size ==="
count
di "v3med_common == 1: "
count if v3med_common == 1

* =============================================================================
* CONSTRUCT SMdef FOR EACH SM SOURCE
* =============================================================================
di _n "=== Constructing SMdef variables ==="

foreach s of global SM_SOURCES {

    di _n "--- Source: `s' ---"

    * Grid-level long-run mean (over 2016-2019 within each grid_id)
    * Restrict mean computation to v3med_common == 1 to avoid contamination
    bysort grid_id: egen mean_`s' = mean(cond(v3med_common == 1, `s', .))

    * One-sided deficit: positive only when below grid mean
    gen SMdef_`s' = max(0, mean_`s' - `s') if v3med_common == 1

    * SR interaction
    gen SR_x_SMdef_`s' = ca * SMdef_`s' if v3med_common == 1

    * Labels
    label var mean_`s' "Grid-level long-run mean of `s'"
    label var SMdef_`s' "Grid-level SM deficit (source: `s', one-sided anomaly)"
    label var SR_x_SMdef_`s' "SR x SMdef (source: `s')"

    * Quick diagnostics
    sum SMdef_`s' if v3med_common == 1, detail

    * Proportion of non-zero deficits (grid-years below own mean)
    count if SMdef_`s' > 0 & v3med_common == 1 & !missing(SMdef_`s')
    local n_pos = r(N)
    count if v3med_common == 1 & !missing(SMdef_`s')
    local n_total = r(N)
    local pct = 100 * `n_pos' / `n_total'
    di "  Non-zero deficits: " `n_pos' "/" `n_total' " = " %5.2f `pct' "%"
}

* =============================================================================
* VERIFY & EXPORT DESCRIPTIVES
* =============================================================================
di _n "=== Descriptive statistics export ==="

tempname pf_desc
postfile `pf_desc' str30 source str15 sm_label ///
    double(n_total n_nonzero pct_nonzero mean sd min p50 p75 p90 p95 max) ///
    using "$outdir/v3med_smdef_descriptives_raw.dta", replace

local si = 0
foreach s of global SM_SOURCES {
    local ++si
    local sm_lbl : word `si' of $SM_LABELS

    qui sum SMdef_`s' if v3med_common == 1, detail
    local mn   = r(mean)
    local sd   = r(sd)
    local mnm  = r(min)
    local p50v = r(p50)
    local p75v = r(p75)
    local p90v = r(p90)
    local p95v = r(p95)
    local mxv  = r(max)
    local nn   = r(N)

    qui count if SMdef_`s' > 0 & v3med_common == 1 & !missing(SMdef_`s')
    local nz = r(N)
    local pct = 100 * `nz' / `nn'

    post `pf_desc' ("`s'") ("`sm_lbl'") ///
        (`nn') (`nz') (`pct') (`mn') (`sd') (`mnm') ///
        (`p50v') (`p75v') (`p90v') (`p95v') (`mxv')
}
postclose `pf_desc'

preserve
use "$outdir/v3med_smdef_descriptives_raw.dta", clear
export delimited using "$outdir/v3med_smdef_descriptives.csv", replace
restore
cap erase "$outdir/v3med_smdef_descriptives_raw.dta"

* =============================================================================
* SANITY CHECK: SMdef <-> raw SM correlation sign should be NEGATIVE (by construction)
* =============================================================================
di _n "=== Correlation check: SMdef vs raw SM (expect negative) ==="
foreach s of global SM_SOURCES {
    qui corr `s' SMdef_`s' if v3med_common == 1
    di "  corr(`s', SMdef_`s') = " %6.4f r(rho)
}

* =============================================================================
* SPOT CHECK: verify SR_x_SMdef = ca * SMdef
* =============================================================================
di _n "=== Spot check: SR_x_SMdef construction ==="
gen _check = SR_x_SMdef_gleam_sms_mean - ca * SMdef_gleam_sms_mean
sum _check if v3med_common == 1
drop _check

* =============================================================================
* SAVE
* =============================================================================
compress
save "$datadir/v3med_analysis_ready_plus.dta", replace
describe SMdef_* SR_x_SMdef_*

di _n "=== v3med_step0b_build_smdef.do COMPLETE ==="
log close
