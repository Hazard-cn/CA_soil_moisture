* =============================================================================
* v5drymed_step4_summary.do
* Purpose: Build sign diagnostic table from v5drymed outputs.
* Output:  output/tables/v5drymed_sign_diagnostic.csv
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v5drymed_macros_include.do"

log using "$logdir/v5drymed_step4_summary.log", replace

tempfile a1 a3 bpath c3

import delimited "$v5coef_csv", clear
keep if module == "drought"

preserve
keep if equation == "mediator" & term == "D_full"
keep module family threshold_scheme percentile source_depth sm_label sample_tag b p
rename b a1
rename p p_a1
save `a1', replace
restore

preserve
keep if equation == "mediator" & term == "SR_x_D_full"
keep module family threshold_scheme percentile source_depth sm_label sample_tag b p
rename b a3
rename p p_a3
save `a3', replace
restore

preserve
keep if equation == "outcome" & term == "M"
keep module family threshold_scheme percentile source_depth sm_label sample_tag b p
rename b b_path
rename p p_b
save `bpath', replace
restore

preserve
keep if equation == "outcome" & term == "SR_x_D_full"
keep module family threshold_scheme percentile source_depth sm_label sample_tag b p
rename b c3
rename p p_c3
save `c3', replace
restore

use `a1', clear
merge 1:1 module family threshold_scheme percentile source_depth sm_label sample_tag using `a3'
drop _merge
merge 1:1 module family threshold_scheme percentile source_depth sm_label sample_tag using `bpath'
drop _merge
merge 1:1 module family threshold_scheme percentile source_depth sm_label sample_tag using `c3'
drop _merge

gen double idx = a3 * b_path
gen byte a1_pos = (a1 > 0) if !missing(a1)
gen byte a3_neg = (a3 < 0) if !missing(a3)
gen byte b_neg = (b_path < 0) if !missing(b_path)
gen byte sign_all = (a1_pos == 1 & a3_neg == 1 & b_neg == 1) if !missing(a1_pos, a3_neg, b_neg)

order module family threshold_scheme percentile source_depth sm_label sample_tag ///
    a1 p_a1 a3 p_a3 b_path p_b c3 p_c3 idx a1_pos a3_neg b_neg sign_all

export delimited using "$v5sign_csv", replace

log close
di "=== v5drymed_step4_summary.do COMPLETE ==="
