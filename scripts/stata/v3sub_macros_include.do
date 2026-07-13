* =============================================================================
* v3sub_macros_include.do
* Purpose: Macros for v3 subsample reruns without W terms
* =============================================================================

global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/v3_macros_include.do"

* --- Outputs ---
global subdata  "$outdata/v3sub_analysis_ready.dta"
global subdiag  "$outdir/v3sub_subsample_defs.dta"

* --- Structure 1: Yield ~ SR + D + H ---
global RHS_sub_spec1_full  D_full hdd_ge32 ca ///
    SR_x_D_full SR_x_Heat_full

global RHS_sub_spec2_full  D_full hdd_ge32 ca ///
    SR_x_D_full SR_x_Heat_full ///
    D_x_Heat_full SR_x_D_x_Heat_full

* --- Structure 2: Yield ~ SR + D + H + SM ---
foreach slbl in gleam swsm era5l {
    local sv = cond("`slbl'" == "gleam", "gleam_smrz_mean", ///
               cond("`slbl'" == "swsm", "swsm_l3_mean", "era5l_swvl3_mean"))
    local sp = cond("`slbl'" == "gleam", "gsm", ///
               cond("`slbl'" == "swsm", "ssm", "esm"))

    global RHS_sub_spec3_full_`slbl'  D_full hdd_ge32 ca ///
        SR_x_D_full SR_x_Heat_full ///
        `sv' `sp'_x_D_full `sp'_x_H_full `sp'_x_SR_full

    global RHS_sub_spec4_full_`slbl'  D_full hdd_ge32 ca ///
        SR_x_D_full SR_x_Heat_full ///
        D_x_Heat_full SR_x_D_x_Heat_full ///
        `sv' `sp'_x_D_full `sp'_x_H_full `sp'_x_SR_full ///
        `sp'_x_DH_full `sp'_x_SRDH_full
}

* --- Structure 3 and Step 2 windows without W ---
foreach wsfx in full v3pre30 v3pm10 hepm10 v3he hema {
    local hsfx = cond("`wsfx'" == "full", "", "_`wsfx'")

    global RHS_sub_spec2_`wsfx'  D_`wsfx' hdd_ge32`hsfx' ca ///
        SR_x_D_`wsfx' SR_x_Heat_`wsfx' ///
        D_x_Heat_`wsfx' SR_x_D_x_Heat_`wsfx'

    foreach slbl in gleam swsm era5l {
        local src = cond("`slbl'" == "gleam", "gleam_smrz_mean", ///
                    cond("`slbl'" == "swsm", "swsm_l3_mean", "era5l_swvl3_mean"))
        local sp = cond("`slbl'" == "gleam", "gsm", ///
                   cond("`slbl'" == "swsm", "ssm", "esm"))
        local sv = cond("`wsfx'" == "full", "`src'", "`src'_`wsfx'")

        global RHS_sub_sm_`wsfx'_`slbl'  D_`wsfx' hdd_ge32`hsfx' ca ///
            SR_x_D_`wsfx' SR_x_Heat_`wsfx'

        global SMVAR_sub_`wsfx'_`slbl' "`sv'"
        global SMPFX_sub_`wsfx'_`slbl' "`sp'"
    }
}

* --- Horse-race without W terms ---
global RHS_sub_hr_scheme_i  ///
    D_v3pm10 hdd_ge32_v3pm10 ///
    SR_x_D_v3pm10 SR_x_Heat_v3pm10 ///
    D_x_Heat_v3pm10 SR_x_D_x_Heat_v3pm10 ///
    D_hepm10 hdd_ge32_hepm10 ///
    SR_x_D_hepm10 SR_x_Heat_hepm10 ///
    D_x_Heat_hepm10 SR_x_D_x_Heat_hepm10 ///
    ca

global RHS_sub_hr_scheme_ii  ///
    D_v3he hdd_ge32_v3he ///
    SR_x_D_v3he SR_x_Heat_v3he ///
    D_x_Heat_v3he SR_x_D_x_Heat_v3he ///
    D_hema hdd_ge32_hema ///
    SR_x_D_hema SR_x_Heat_hema ///
    D_x_Heat_hema SR_x_D_x_Heat_hema ///
    ca

global RHS_sub_hr_scheme_iii  ///
    D_v3pre30 hdd_ge32_v3pre30 ///
    SR_x_D_v3pre30 SR_x_Heat_v3pre30 ///
    D_x_Heat_v3pre30 SR_x_D_x_Heat_v3pre30 ///
    D_v3he hdd_ge32_v3he ///
    SR_x_D_v3he SR_x_Heat_v3he ///
    D_x_Heat_v3he SR_x_D_x_Heat_v3he ///
    D_hema hdd_ge32_hema ///
    SR_x_D_hema SR_x_Heat_hema ///
    D_x_Heat_hema SR_x_D_x_Heat_hema ///
    ca
