* =============================================================================
* v3sub_run_all.do
* Purpose: Master runner for v3 subsample reruns
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"

do "$projdir/scripts/stata/v3sub_step0_subsamples.do"
do "$projdir/scripts/stata/v3sub_step1_structures.do"
do "$projdir/scripts/stata/v3sub_step2_stage_effects.do"
do "$projdir/scripts/stata/v3sub_step3_sm_response.do"

di "=== v3sub_run_all.do COMPLETE ==="
