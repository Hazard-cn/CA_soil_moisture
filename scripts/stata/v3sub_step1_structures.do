* =============================================================================
* v3sub_step1_structures.do
* Purpose: Structure 1 and Structure 2 regressions for subsamples
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3sub_macros_include.do"

log using "$logdir/v3sub_step1_structures.log", replace

use "$subdata", clear
xtset grid_id year

tempname pf1 pf2 pf3
postfile `pf1' str12 split_type str12 subgroup str10 spec ///
    b_SRD se_SRD p_SRD ///
    b_SRH se_SRH p_SRH ///
    b_DH se_DH p_DH ///
    b_SRDH se_SRDH p_SRDH ///
    b_D se_D p_D ///
    b_H se_H p_H ///
    r2 N ///
    using "$outdir/v3sub_structure1.dta", replace

postfile `pf2' str12 split_type str12 subgroup str10 spec str10 sm_src ///
    b_SRD se_SRD p_SRD ///
    b_SRH se_SRH p_SRH ///
    b_DH se_DH p_DH ///
    b_SRDH se_SRDH p_SRDH ///
    b_D se_D p_D ///
    b_H se_H p_H ///
    b_SM se_SM p_SM ///
    b_SMD se_SMD p_SMD ///
    b_SMH se_SMH p_SMH ///
    b_SMSR se_SMSR p_SMSR ///
    b_SMDH se_SMDH p_SMDH ///
    b_SMSRDH se_SMSRDH p_SMSRDH ///
    r2 N ///
    using "$outdir/v3sub_structure2.dta", replace

postfile `pf3' str12 split_type str12 subgroup str10 sm_src ///
    str10 baseline_spec str10 sm_spec str18 term ///
    b_base b_sm attenuation N ///
    using "$outdir/v3sub_structure2_attenuation.dta", replace

foreach split in zone irrigation {
    local svar = cond("`split'" == "zone", "maize_zone", "irr_group")
    local groups "NE HHH SW SH NW Other"
    if "`split'" == "irrigation" {
        local groups "low_irr high_irr"
    }

    foreach g in `groups' {
        di _n "=== split=`split' subgroup=`g' ==="

        cap noi reghdfe ln_yield $RHS_sub_spec1_full $CTRL_full ///
            if main_sample == 1 & `svar' == "`g'", absorb(grid_id year) vce(cluster grid_id)
        if _rc == 0 {
            local dfr = e(df_r)
            local b1_SRD = _b[SR_x_D_full]
            local b1_SRH = _b[SR_x_Heat_full]
            post `pf1' ("`split'") ("`g'") ("spec1_sub") ///
                (_b[SR_x_D_full]) (_se[SR_x_D_full]) ///
                (2*ttail(`dfr', abs(_b[SR_x_D_full]/_se[SR_x_D_full]))) ///
                (_b[SR_x_Heat_full]) (_se[SR_x_Heat_full]) ///
                (2*ttail(`dfr', abs(_b[SR_x_Heat_full]/_se[SR_x_Heat_full]))) ///
                (.) (.) (.) (.) (.) (.) ///
                (_b[D_full]) (_se[D_full]) ///
                (2*ttail(`dfr', abs(_b[D_full]/_se[D_full]))) ///
                (_b[hdd_ge32]) (_se[hdd_ge32]) ///
                (2*ttail(`dfr', abs(_b[hdd_ge32]/_se[hdd_ge32]))) ///
                (e(r2)) (e(N))
        }
        else {
            post `pf1' ("`split'") ("`g'") ("spec1_sub") ///
                (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) ///
                (.) (.) (.) (.) (.) (.) (.) (0)
        }

        cap noi reghdfe ln_yield $RHS_sub_spec2_full $CTRL_full ///
            if main_sample == 1 & `svar' == "`g'", absorb(grid_id year) vce(cluster grid_id)
        if _rc == 0 {
            local dfr = e(df_r)
            local b2_SRD = _b[SR_x_D_full]
            local b2_SRH = _b[SR_x_Heat_full]
            local b2_SRDH = _b[SR_x_D_x_Heat_full]
            post `pf1' ("`split'") ("`g'") ("spec2_sub") ///
                (_b[SR_x_D_full]) (_se[SR_x_D_full]) ///
                (2*ttail(`dfr', abs(_b[SR_x_D_full]/_se[SR_x_D_full]))) ///
                (_b[SR_x_Heat_full]) (_se[SR_x_Heat_full]) ///
                (2*ttail(`dfr', abs(_b[SR_x_Heat_full]/_se[SR_x_Heat_full]))) ///
                (_b[D_x_Heat_full]) (_se[D_x_Heat_full]) ///
                (2*ttail(`dfr', abs(_b[D_x_Heat_full]/_se[D_x_Heat_full]))) ///
                (_b[SR_x_D_x_Heat_full]) (_se[SR_x_D_x_Heat_full]) ///
                (2*ttail(`dfr', abs(_b[SR_x_D_x_Heat_full]/_se[SR_x_D_x_Heat_full]))) ///
                (_b[D_full]) (_se[D_full]) ///
                (2*ttail(`dfr', abs(_b[D_full]/_se[D_full]))) ///
                (_b[hdd_ge32]) (_se[hdd_ge32]) ///
                (2*ttail(`dfr', abs(_b[hdd_ge32]/_se[hdd_ge32]))) ///
                (e(r2)) (e(N))
        }
        else {
            post `pf1' ("`split'") ("`g'") ("spec2_sub") ///
                (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) ///
                (.) (.) (.) (.) (.) (.) (.) (0)
        }

        foreach slbl in gleam swsm era5l {
            local sv = cond("`slbl'" == "gleam", "gleam_smrz_mean", ///
                       cond("`slbl'" == "swsm", "swsm_l3_mean", "era5l_swvl3_mean"))
            local sp = cond("`slbl'" == "gleam", "gsm", ///
                       cond("`slbl'" == "swsm", "ssm", "esm"))

            cap noi reghdfe ln_yield ${RHS_sub_spec3_full_`slbl'} $CTRL_full ///
                if main_sample == 1 & `svar' == "`g'", absorb(grid_id year) vce(cluster grid_id)
            if _rc == 0 {
                local dfr = e(df_r)
                local b3_SRD = _b[SR_x_D_full]
                local b3_SRH = _b[SR_x_Heat_full]
                post `pf2' ("`split'") ("`g'") ("spec3_sub") ("`slbl'") ///
                    (_b[SR_x_D_full]) (_se[SR_x_D_full]) ///
                    (2*ttail(`dfr', abs(_b[SR_x_D_full]/_se[SR_x_D_full]))) ///
                    (_b[SR_x_Heat_full]) (_se[SR_x_Heat_full]) ///
                    (2*ttail(`dfr', abs(_b[SR_x_Heat_full]/_se[SR_x_Heat_full]))) ///
                    (.) (.) (.) (.) (.) (.) ///
                    (_b[D_full]) (_se[D_full]) ///
                    (2*ttail(`dfr', abs(_b[D_full]/_se[D_full]))) ///
                    (_b[hdd_ge32]) (_se[hdd_ge32]) ///
                    (2*ttail(`dfr', abs(_b[hdd_ge32]/_se[hdd_ge32]))) ///
                    (_b[`sv']) (_se[`sv']) ///
                    (2*ttail(`dfr', abs(_b[`sv']/_se[`sv']))) ///
                    (_b[`sp'_x_D_full]) (_se[`sp'_x_D_full]) ///
                    (2*ttail(`dfr', abs(_b[`sp'_x_D_full]/_se[`sp'_x_D_full]))) ///
                    (_b[`sp'_x_H_full]) (_se[`sp'_x_H_full]) ///
                    (2*ttail(`dfr', abs(_b[`sp'_x_H_full]/_se[`sp'_x_H_full]))) ///
                    (_b[`sp'_x_SR_full]) (_se[`sp'_x_SR_full]) ///
                    (2*ttail(`dfr', abs(_b[`sp'_x_SR_full]/_se[`sp'_x_SR_full]))) ///
                    (.) (.) (.) (.) (.) (.) ///
                    (e(r2)) (e(N))

                post `pf3' ("`split'") ("`g'") ("`slbl'") ///
                    ("spec1_sub") ("spec3_sub") ("SR_x_D_full") ///
                    (`b1_SRD') (`b3_SRD') ///
                    (cond(`b1_SRD'!=0,100*(1-`b3_SRD'/`b1_SRD'),.)) (e(N))
                post `pf3' ("`split'") ("`g'") ("`slbl'") ///
                    ("spec1_sub") ("spec3_sub") ("SR_x_Heat_full") ///
                    (`b1_SRH') (`b3_SRH') ///
                    (cond(`b1_SRH'!=0,100*(1-`b3_SRH'/`b1_SRH'),.)) (e(N))
            }
            else {
                post `pf2' ("`split'") ("`g'") ("spec3_sub") ("`slbl'") ///
                    (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) ///
                    (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) ///
                    (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) ///
                    (.) (.) (0)
            }

            cap noi reghdfe ln_yield ${RHS_sub_spec4_full_`slbl'} $CTRL_full ///
                if main_sample == 1 & `svar' == "`g'", absorb(grid_id year) vce(cluster grid_id)
            if _rc == 0 {
                local dfr = e(df_r)
                local b4_SRD = _b[SR_x_D_full]
                local b4_SRH = _b[SR_x_Heat_full]
                local b4_SRDH = _b[SR_x_D_x_Heat_full]
                post `pf2' ("`split'") ("`g'") ("spec4_sub") ("`slbl'") ///
                    (_b[SR_x_D_full]) (_se[SR_x_D_full]) ///
                    (2*ttail(`dfr', abs(_b[SR_x_D_full]/_se[SR_x_D_full]))) ///
                    (_b[SR_x_Heat_full]) (_se[SR_x_Heat_full]) ///
                    (2*ttail(`dfr', abs(_b[SR_x_Heat_full]/_se[SR_x_Heat_full]))) ///
                    (_b[D_x_Heat_full]) (_se[D_x_Heat_full]) ///
                    (2*ttail(`dfr', abs(_b[D_x_Heat_full]/_se[D_x_Heat_full]))) ///
                    (_b[SR_x_D_x_Heat_full]) (_se[SR_x_D_x_Heat_full]) ///
                    (2*ttail(`dfr', abs(_b[SR_x_D_x_Heat_full]/_se[SR_x_D_x_Heat_full]))) ///
                    (_b[D_full]) (_se[D_full]) ///
                    (2*ttail(`dfr', abs(_b[D_full]/_se[D_full]))) ///
                    (_b[hdd_ge32]) (_se[hdd_ge32]) ///
                    (2*ttail(`dfr', abs(_b[hdd_ge32]/_se[hdd_ge32]))) ///
                    (_b[`sv']) (_se[`sv']) ///
                    (2*ttail(`dfr', abs(_b[`sv']/_se[`sv']))) ///
                    (_b[`sp'_x_D_full]) (_se[`sp'_x_D_full]) ///
                    (2*ttail(`dfr', abs(_b[`sp'_x_D_full]/_se[`sp'_x_D_full]))) ///
                    (_b[`sp'_x_H_full]) (_se[`sp'_x_H_full]) ///
                    (2*ttail(`dfr', abs(_b[`sp'_x_H_full]/_se[`sp'_x_H_full]))) ///
                    (_b[`sp'_x_SR_full]) (_se[`sp'_x_SR_full]) ///
                    (2*ttail(`dfr', abs(_b[`sp'_x_SR_full]/_se[`sp'_x_SR_full]))) ///
                    (_b[`sp'_x_DH_full]) (_se[`sp'_x_DH_full]) ///
                    (2*ttail(`dfr', abs(_b[`sp'_x_DH_full]/_se[`sp'_x_DH_full]))) ///
                    (_b[`sp'_x_SRDH_full]) (_se[`sp'_x_SRDH_full]) ///
                    (2*ttail(`dfr', abs(_b[`sp'_x_SRDH_full]/_se[`sp'_x_SRDH_full]))) ///
                    (e(r2)) (e(N))

                post `pf3' ("`split'") ("`g'") ("`slbl'") ///
                    ("spec2_sub") ("spec4_sub") ("SR_x_D_full") ///
                    (`b2_SRD') (`b4_SRD') ///
                    (cond(`b2_SRD'!=0,100*(1-`b4_SRD'/`b2_SRD'),.)) (e(N))
                post `pf3' ("`split'") ("`g'") ("`slbl'") ///
                    ("spec2_sub") ("spec4_sub") ("SR_x_Heat_full") ///
                    (`b2_SRH') (`b4_SRH') ///
                    (cond(`b2_SRH'!=0,100*(1-`b4_SRH'/`b2_SRH'),.)) (e(N))
                post `pf3' ("`split'") ("`g'") ("`slbl'") ///
                    ("spec2_sub") ("spec4_sub") ("SR_x_D_x_Heat_full") ///
                    (`b2_SRDH') (`b4_SRDH') ///
                    (cond(`b2_SRDH'!=0,100*(1-`b4_SRDH'/`b2_SRDH'),.)) (e(N))
            }
            else {
                post `pf2' ("`split'") ("`g'") ("spec4_sub") ("`slbl'") ///
                    (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) ///
                    (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) ///
                    (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) ///
                    (.) (.) (0)
            }
        }
    }
}

postclose `pf1'
postclose `pf2'
postclose `pf3'

preserve
use "$outdir/v3sub_structure1.dta", clear
export delimited using "$outdir/v3sub_structure1.csv", replace
restore

preserve
use "$outdir/v3sub_structure2.dta", clear
export delimited using "$outdir/v3sub_structure2.csv", replace
restore

preserve
use "$outdir/v3sub_structure2_attenuation.dta", clear
export delimited using "$outdir/v3sub_structure2_attenuation.csv", replace
restore

log close
di "=== v3sub_step1_structures.do COMPLETE ==="
