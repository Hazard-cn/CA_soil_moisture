* =============================================================================
* ggcp10_core_baseline_run_all.do
* Purpose: Build and run the compact full-season baseline-only suite.
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/ggcp10_core_baseline_step0_preamble.do"
do "$projdir/scripts/stata/ggcp10_core_baseline_step1_models.do"

di "=== ggcp10_core_baseline_run_all.do COMPLETE ==="
