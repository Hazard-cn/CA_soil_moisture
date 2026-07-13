* =============================================================================
* ggcp10_baseline_suite_run_all.do
* Purpose: Build the aggregated GGCP10 suite data and run baseline equations.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global V6_MACROS_INCLUDE "$projdir/scripts/stata/ggcp10_baseline_suite_macros_include.do"

do "$projdir/scripts/stata/v6gleambl_step0_preamble.do"
do "$projdir/scripts/stata/ggcp10_baseline_suite_step1_models.do"

di "=== ggcp10_baseline_suite_run_all.do COMPLETE ==="
