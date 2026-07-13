* =============================================================================
* v3sub_step2_stage_effects.do
* Purpose: Stage-specific structure-1 reruns for subsamples without W terms
* =============================================================================

clear all
set more off
set seed 42

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3sub_macros_include.do"

log using "$logdir/v3sub_step2_stage_effects.log", replace

use "$subdata", clear
xtset grid_id year

tempname pf pf2
postfile `pf' str12 split_type str12 subgroup str10 window ///
    b_SRD se_SRD p_SRD ///
    b_SRH se_SRH p_SRH ///
    b_DH se_DH p_DH ///
    b_SRDH se_SRDH p_SRDH ///
    b_D se_D p_D ///
    b_H se_H p_H ///
    r2 N ///
    using "$outdir/v3sub_step2_stage_single.dta", replace

postfile `pf2' str12 split_type str12 subgroup str10 scheme str10 window str18 coef_type ///
    b se p ///
    using "$outdir/v3sub_step2_stage_horserace.dta", replace

foreach split in zone irrigation {
    local svar = cond("`split'" == "zone", "maize_zone", "irr_group")
    local groups "NE HHH SW SH NW Other"
    if "`split'" == "irrigation" {
        local groups "low_irr high_irr"
    }

    foreach g in `groups' {
        foreach w in full v3pre30 v3pm10 hepm10 v3he hema {
            local hsfx = cond("`w'" == "full", "", "_`w'")

            cap noi reghdfe ln_yield ${RHS_sub_spec2_`w'} ${CTRL_`w'} ///
                if main_sample == 1 & `svar' == "`g'", absorb(grid_id year) vce(cluster grid_id)

            if _rc == 0 {
                local dfr = e(df_r)
                post `pf' ("`split'") ("`g'") ("`w'") ///
                    (_b[SR_x_D_`w']) (_se[SR_x_D_`w']) ///
                    (2*ttail(`dfr', abs(_b[SR_x_D_`w']/_se[SR_x_D_`w']))) ///
                    (_b[SR_x_Heat_`w']) (_se[SR_x_Heat_`w']) ///
                    (2*ttail(`dfr', abs(_b[SR_x_Heat_`w']/_se[SR_x_Heat_`w']))) ///
                    (_b[D_x_Heat_`w']) (_se[D_x_Heat_`w']) ///
                    (2*ttail(`dfr', abs(_b[D_x_Heat_`w']/_se[D_x_Heat_`w']))) ///
                    (_b[SR_x_D_x_Heat_`w']) (_se[SR_x_D_x_Heat_`w']) ///
                    (2*ttail(`dfr', abs(_b[SR_x_D_x_Heat_`w']/_se[SR_x_D_x_Heat_`w']))) ///
                    (_b[D_`w']) (_se[D_`w']) ///
                    (2*ttail(`dfr', abs(_b[D_`w']/_se[D_`w']))) ///
                    (_b[hdd_ge32`hsfx']) (_se[hdd_ge32`hsfx']) ///
                    (2*ttail(`dfr', abs(_b[hdd_ge32`hsfx']/_se[hdd_ge32`hsfx']))) ///
                    (e(r2)) (e(N))
            }
            else {
                post `pf' ("`split'") ("`g'") ("`w'") ///
                    (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) ///
                    (.) (.) (.) (.) (.) (.) (.) (0)
            }
        }

        foreach scheme in i ii iii {
            cap noi reghdfe ln_yield ${RHS_sub_hr_scheme_`scheme'} $CTRL_full ///
                if main_sample == 1 & `svar' == "`g'", absorb(grid_id year) vce(cluster grid_id)

            if _rc != 0 {
                local windows ""
                if "`scheme'" == "i" local windows "v3pm10 hepm10"
                if "`scheme'" == "ii" local windows "v3he hema"
                if "`scheme'" == "iii" local windows "v3pre30 v3he hema"
                foreach w in `windows' {
                    foreach ctype in SR_x_D SR_x_Heat D_x_Heat SR_x_D_x_Heat {
                        post `pf2' ("`split'") ("`g'") ("`scheme'") ("`w'") ("`ctype'") (.) (.) (.)
                    }
                }
                continue
            }

            local windows ""
            if "`scheme'" == "i" local windows "v3pm10 hepm10"
            if "`scheme'" == "ii" local windows "v3he hema"
            if "`scheme'" == "iii" local windows "v3pre30 v3he hema"

            foreach w in `windows' {
                foreach ctype in SR_x_D SR_x_Heat D_x_Heat SR_x_D_x_Heat {
                    post `pf2' ("`split'") ("`g'") ("`scheme'") ("`w'") ("`ctype'") ///
                        (_b[`ctype'_`w']) (_se[`ctype'_`w']) ///
                        (2*ttail(e(df_r), abs(_b[`ctype'_`w']/_se[`ctype'_`w'])))
                }
            }
        }
    }
}

postclose `pf'
postclose `pf2'

preserve
use "$outdir/v3sub_step2_stage_single.dta", clear
export delimited using "$outdir/v3sub_step2_stage_single.csv", replace
restore

preserve
use "$outdir/v3sub_step2_stage_horserace.dta", clear
export delimited using "$outdir/v3sub_step2_stage_horserace.csv", replace
restore

log close
di "=== v3sub_step2_stage_effects.do COMPLETE ==="
