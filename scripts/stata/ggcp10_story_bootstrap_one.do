* =============================================================================
* ggcp10_story_bootstrap_one.do
* Purpose: Run one selective bootstrap job from the frozen S0-ready panel.
* Usage:
*   Stata /e do scripts/stata/ggcp10_story_bootstrap_one.do job_id branch medtag hazard transform reps stage
* =============================================================================

args job_id branch medtag hazard transform reps stage

clear all
set more off
set seed 42

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global rundir "$projdir/temp/2026-06-02_story_s0_spec_search_mean_drytop3"
global jobdir "$rundir/bootstrap_jobs"
global logdir "$jobdir/logs"

cap mkdir "$jobdir"
cap mkdir "$logdir"

cap log close master
log using "$logdir/bootstrap_`job_id'.log", replace text name(master)

di "=== bootstrap job `job_id' started ==="
di "branch=`branch' medtag=`medtag' hazard=`hazard' transform=`transform' reps=`reps' stage=`stage'"

use "$rundir/story_s0_ready.dta", clear
xtset grid_id year
xtset, clear

local sx "raw"
if "`transform'" == "winsor_1_99" local sx "w"

local mediator "gleam_smrz_mean_`sx'"
if "`medtag'" == "mean_surface" local mediator "gleam_sms_mean_`sx'"
if "`medtag'" == "mean_root" local mediator "gleam_smrz_mean_`sx'"
if "`medtag'" == "dry_mdf_p10_sfc" local mediator "v6mdf_p10_fn_gss_`sx'"
if "`medtag'" == "dry_sdf_p10_root" local mediator "v6sdf_p10_fn_gsr_`sx'"
if "`medtag'" == "dry_dur_p10_sfc" local mediator "v6dur_p10_fn_gss_`sx'"

local y "ln_yield_`sx'"
local ca "ca_`sx'"
local d "D_full_`sx'"
local w "W_full_`sx'"
local h "hdd_ge32_`sx'"
local hd "HotDryPr_full_`sx'"
local srd "SR_x_D_full_`sx'"
local srw "SR_x_W_full_`sx'"
local srh "SR_x_Heat_full_`sx'"
local srhd "SR_x_HotDryPr_full_`sx'"
local ctrl "pr_sum_`sx' et0_sum_`sx' gdd_10_30_`sx' irr_frac_`sx' aridity_`sx'"

gen byte __sample = 1
foreach v in `y' `ca' `d' `w' `h' `hd' `srd' `srh' `srhd' `mediator' `ctrl' {
    replace __sample = 0 if missing(`v') & __sample == 1
}
keep if __sample == 1
count
local modelN = r(N)
di "model sample N = `modelN'"

_pctile `ca', p(25 50 75)
global BOOT_CA_P25 = r(r1)
global BOOT_CA_P50 = r(r2)
global BOOT_CA_P75 = r(r3)

capture program drop boot_model
program define boot_model, rclass
    args hazard y ca d w h hd srd srw srh srhd mediator sx
    local abs_id "grid_id"
    capture confirm variable boot_grid
    if _rc == 0 local abs_id "boot_grid"
    local ctrl "pr_sum_`sx' et0_sum_`sx' gdd_10_30_`sx' irr_frac_`sx' aridity_`sx'"
    if "`hazard'" == "drought" {
        local rhs_m "`d' `ca' `srd' `w' `h' `ctrl'"
        local rhs_y "`d' `ca' `srd' `mediator' `w' `h' `ctrl'"
        local main "`d'"
        local inter "`srd'"
    }
    if "`hazard'" == "heat" {
        local rhs_m "`h' `ca' `srh' `d' `w' `ctrl'"
        local rhs_y "`h' `ca' `srh' `mediator' `d' `w' `ctrl'"
        local main "`h'"
        local inter "`srh'"
    }
    if "`hazard'" == "hotdry" {
        local rhs_m "`hd' `ca' `srhd' `d' `h' `w' `ctrl'"
        local rhs_y "`hd' `ca' `srhd' `mediator' `d' `h' `w' `ctrl'"
        local main "`hd'"
        local inter "`srhd'"
    }
    capture quietly reghdfe `mediator' `rhs_m', absorb(`abs_id' year) vce(cluster `abs_id')
    if _rc != 0 exit
    local a1 = _b[`main']
    local a3 = _b[`inter']
    capture quietly reghdfe `y' `rhs_y', absorb(`abs_id' year) vce(cluster `abs_id')
    if _rc != 0 exit
    local b = _b[`mediator']
    local c1 = _b[`main']
    local c3 = _b[`inter']
    foreach q in 25 50 75 {
        local r = $BOOT_CA_P`q'
        local ie = (`a1' + `a3' * `r') * `b'
        local de = `c1' + `c3' * `r'
        return scalar ie`q' = `ie'
        return scalar de`q' = `de'
        return scalar te`q' = `ie' + `de'
    }
end

tempname pb
postfile `pb' str16 job_id str100 set_id str12 branch str28 mediator_tag ///
    str12 hazard str16 transform str16 boot_stage str2 effect str4 ca_level ///
    double(point_est bs_se ci_lo ci_hi) long(N_boot N_model) ///
    using "$jobdir/bootstrap_`job_id'_raw.dta", replace

local set_id "S0_fullnew_`transform'_`branch'_`medtag'_`hazard'"
local bseed = 71000 + real("`job_id'")
bootstrap ie25=r(ie25) ie50=r(ie50) ie75=r(ie75) ///
    de25=r(de25) de50=r(de50) de75=r(de75) ///
    te25=r(te25) te50=r(te50) te75=r(te75), ///
    reps(`reps') cluster(grid_id) idcluster(boot_grid) seed(`bseed') nodots: ///
    boot_model `hazard' `y' `ca' `d' `w' `h' `hd' `srd' `srw' `srh' `srhd' `mediator' `sx'

estat bootstrap, bc
matrix bcCI = r(ci_bc)
matrix pe = e(b)
matrix vv = e(V)
local stats "ie25 ie50 ie75 de25 de50 de75 te25 te50 te75"
local j = 0
foreach sname of local stats {
    local ++j
    local point = pe[1,`j']
    local bs = sqrt(vv[`j',`j'])
    scalar __ll = .
    scalar __ul = .
    capture scalar __ll = bcCI[`j',1]
    capture scalar __ul = bcCI[`j',2]
    local ll = scalar(__ll)
    local ul = scalar(__ul)
    if missing(`ll') | missing(`ul') {
        local ll = `point' - 1.96 * `bs'
        local ul = `point' + 1.96 * `bs'
    }
    local eff = upper(substr("`sname'",1,2))
    local lvl = substr("`sname'",3,.)
    post `pb' ("`job_id'") ("`set_id'") ("`branch'") ("`medtag'") ///
        ("`hazard'") ("`transform'") ("`stage'") ("`eff'") ("P`lvl'") ///
        (`point') (`bs') (`ll') (`ul') (`reps') (`modelN')
}
postclose `pb'

preserve
use "$jobdir/bootstrap_`job_id'_raw.dta", clear
export delimited using "$jobdir/bootstrap_`job_id'.csv", replace
restore

di "=== bootstrap job `job_id' COMPLETE ==="
log close master
