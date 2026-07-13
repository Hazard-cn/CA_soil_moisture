* =============================================================================
* v6gleambl_nowet_nop30_run_all.do
* =============================================================================

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"

do "$projdir/scripts/stata/v6gleambl_nowet_nop30_step0_preamble.do"
do "$projdir/scripts/stata/v6gleambl_nowet_nop30_step1_model8.do"
