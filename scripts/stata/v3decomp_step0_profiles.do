* =============================================================================
* v3decomp_step0_profiles.do
* Purpose: Build common-sample panel and stress profile constants for FE
*          decomposition equations.
* Input:   data/processed/v3_analysis_ready.dta
* Output:  data/processed/v3decomp_analysis_ready.dta
*          output/tables/v3decomp_profile_constants.csv
* =============================================================================

clear all
set more off
set seed 42

do "C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata/v3decomp_macros_include.do"

log using "$logdir/v3decomp_step0_profiles.log", replace

use "$decomp_infile", clear
xtset grid_id year

* ---------------------------------------------------------------------------
* Variable checks
* ---------------------------------------------------------------------------
foreach v in grid_id year main_sample ln_yield ca ///
    D_full W_full hdd_ge32 D_x_Heat_full ///
    SR_x_D_full SR_x_Heat_full SR_x_W_full SR_x_D_x_Heat_full ///
    gleam_sms_mean irr_frac pr_sum et0_sum aridity gdd_ge10 {
    confirm variable `v'
}

* ---------------------------------------------------------------------------
* Construct mediator interactions used in Layer 3
* ---------------------------------------------------------------------------
cap drop SM_x_D_full
cap drop SM_x_H_full

gen double SM_x_D_full = $DECOMP_MEDIATOR * D_full
gen double SM_x_H_full = $DECOMP_MEDIATOR * hdd_ge32

label var SM_x_D_full "Surface SM x Drought (full season)"
label var SM_x_H_full "Surface SM x Heat (full season)"

* ---------------------------------------------------------------------------
* Strict common sample across Layer 2 and Layer 3
* ---------------------------------------------------------------------------
cap drop __decomp_missing
cap drop v3decomp_common_sample

egen byte __decomp_missing = rowmiss($DECOMP_SAMPLE_VARS)
gen byte v3decomp_common_sample = (main_sample == 1 & __decomp_missing == 0)
label var v3decomp_common_sample "Strict common sample for v3 decomposition equations"
drop __decomp_missing

count if main_sample == 1
local N_main = r(N)
count if v3decomp_common_sample == 1
local N_common = r(N)

di "Main sample N     = `N_main'"
di "Common sample N   = `N_common'"

sum ln_yield $DECOMP_MEDIATOR D_full W_full hdd_ge32 if v3decomp_common_sample == 1

* ---------------------------------------------------------------------------
* Stress profile constants
*   All profile constants are computed on main_sample == 1 by design.
* ---------------------------------------------------------------------------
quietly centile D_full if main_sample == 1 & D_full > 0, centile(75 90)
local d_p75 = r(c_1)
local d_p90 = r(c_2)

quietly centile hdd_ge32 if main_sample == 1 & hdd_ge32 > 0, centile(75 90)
local h_p75 = r(c_1)
local h_p90 = r(c_2)

quietly count if main_sample == 1 & D_full >= `d_p90' & hdd_ge32 >= `h_p90'
local N_joint = r(N)

if `N_joint' > 0 {
    quietly summarize D_full if main_sample == 1 & D_full >= `d_p90' & hdd_ge32 >= `h_p90', meanonly
    local d_joint = r(mean)
    quietly summarize hdd_ge32 if main_sample == 1 & D_full >= `d_p90' & hdd_ge32 >= `h_p90', meanonly
    local h_joint = r(mean)
}
else {
    local d_joint = `d_p90'
    local h_joint = `h_p90'
}

di "P75(D | D>0) = " %9.6f `d_p75'
di "P90(D | D>0) = " %9.6f `d_p90'
di "P75(H | H>0) = " %9.6f `h_p75'
di "P90(H | H>0) = " %9.6f `h_p90'
di "Joint upper-tail N = `N_joint'"
di "Joint upper-tail mean D = " %9.6f `d_joint'
di "Joint upper-tail mean H = " %9.6f `h_joint'

tempname pf
postfile `pf' str16 profile str24 profile_label str12 profile_group ///
    double d h w byte is_main using "$decomp_profiles", replace

post `pf' ("baseline")   ("Baseline")         ("main")    (0)        (0)        (0) (1)
post `pf' ("d_only")     ("D only (P75)")     ("main")    (`d_p75')  (0)        (0) (1)
post `pf' ("h_only")     ("H only (P75)")     ("main")    (0)        (`h_p75')  (0) (1)
post `pf' ("dh_p75")     ("D + H (P75)")      ("main")    (`d_p75')  (`h_p75')  (0) (1)
post `pf' ("dh_p90")     ("D + H (P90)")      ("appendix") (`d_p90')  (`h_p90')  (0) (0)
post `pf' ("joint_tail") ("Joint tail mean")  ("appendix") (`d_joint') (`h_joint') (0) (0)

postclose `pf'

preserve
use "$decomp_profiles", clear
format d h w %9.6f
list, noobs sep(0)
export delimited using "$decomp_profiles_csv", replace
restore

quietly compress
save "$decomp_panel", replace
di "Saved panel:    $decomp_panel"
di "Saved profiles: $decomp_profiles_csv"

log close
di "=== v3decomp_step0_profiles.do COMPLETE ==="
