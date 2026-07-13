* =============================================================================
* v3_macros_include.do
* Purpose: Define all global macros (controls, RHS, paths) for v3 analysis.
*          Sourced at the top of each v3_step*.do file via `do`.
* =============================================================================

* --- Paths ---
global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global datadir  "$projdir/data_build/data/processed"
global outdata  "$projdir/data/processed"
global outdir   "$projdir/output/tables"
global figdir   "$projdir/output/figures"
global logdir   "$projdir/output/logs"

* --- Control variable macros (6 windows) ---
global CTRL_full    irr_frac pr_sum et0_sum aridity gdd_ge10
global CTRL_v3pm10  irr_frac pr_sum_v3pm10 et0_sum_v3pm10 aridity gdd_ge10_v3pm10
global CTRL_hepm10  irr_frac pr_sum_hepm10 et0_sum_hepm10 aridity gdd_ge10_hepm10
global CTRL_v3he    irr_frac pr_sum_v3he et0_sum_v3he aridity gdd_ge10_v3he
global CTRL_hema    irr_frac pr_sum_hema et0_sum_hema aridity gdd_ge10_hema
global CTRL_v3pre30 irr_frac pr_sum_v3pre30 et0_sum_v3pre30 aridity gdd_ge10_v3pre30

* --- RHS macros: Full season ---
global RHS_spec1_full  D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full

global RHS_spec2_full  D_full W_full hdd_ge32 ca ///
    SR_x_D_full SR_x_W_full SR_x_Heat_full ///
    D_x_Heat_full SR_x_D_x_Heat_full

foreach slbl in gleam swsm era5l {
    local sv = cond("`slbl'" == "gleam", "gleam_smrz_mean", ///
               cond("`slbl'" == "swsm", "swsm_l3_mean", "era5l_swvl3_mean"))
    local sp = cond("`slbl'" == "gleam", "gsm", ///
               cond("`slbl'" == "swsm", "ssm", "esm"))

    global RHS_spec3_full_`slbl'  D_full W_full hdd_ge32 ca ///
        SR_x_D_full SR_x_W_full SR_x_Heat_full ///
        `sv' `sp'_x_D_full `sp'_x_H_full `sp'_x_SR_full

    global RHS_spec4_full_`slbl'  D_full W_full hdd_ge32 ca ///
        SR_x_D_full SR_x_W_full SR_x_Heat_full ///
        D_x_Heat_full SR_x_D_x_Heat_full ///
        `sv' `sp'_x_D_full `sp'_x_H_full `sp'_x_SR_full ///
        `sp'_x_DH_full `sp'_x_SRDH_full
}

* --- RHS macros: Sub-windows ---
foreach wsfx in v3pm10 hepm10 v3he hema v3pre30 {
    local h "hdd_ge32_`wsfx'"

    global RHS_spec1_`wsfx'  D_`wsfx' W_`wsfx' `h' ca ///
        SR_x_D_`wsfx' SR_x_W_`wsfx' SR_x_Heat_`wsfx'

    global RHS_spec2_`wsfx'  D_`wsfx' W_`wsfx' `h' ca ///
        SR_x_D_`wsfx' SR_x_W_`wsfx' SR_x_Heat_`wsfx' ///
        D_x_Heat_`wsfx' SR_x_D_x_Heat_`wsfx'

    foreach slbl in gleam swsm era5l {
        local sv = cond("`slbl'" == "gleam", "gleam_smrz_mean_`wsfx'", ///
                   cond("`slbl'" == "swsm", "swsm_l3_mean_`wsfx'", ///
                        "era5l_swvl3_mean_`wsfx'"))
        local sp = cond("`slbl'" == "gleam", "gsm", ///
                   cond("`slbl'" == "swsm", "ssm", "esm"))

        global RHS_spec3_`wsfx'_`slbl'  D_`wsfx' W_`wsfx' `h' ca ///
            SR_x_D_`wsfx' SR_x_W_`wsfx' SR_x_Heat_`wsfx' ///
            `sv' `sp'_x_D_`wsfx' `sp'_x_H_`wsfx' `sp'_x_SR_`wsfx'

        global RHS_spec4_`wsfx'_`slbl'  D_`wsfx' W_`wsfx' `h' ca ///
            SR_x_D_`wsfx' SR_x_W_`wsfx' SR_x_Heat_`wsfx' ///
            D_x_Heat_`wsfx' SR_x_D_x_Heat_`wsfx' ///
            `sv' `sp'_x_D_`wsfx' `sp'_x_H_`wsfx' `sp'_x_SR_`wsfx' ///
            `sp'_x_DH_`wsfx' `sp'_x_SRDH_`wsfx'
    }
}

* --- Horse-Race Scheme RHS macros (Spec 2) ---
global RHS_hr_scheme_i  ///
    D_v3pm10 W_v3pm10 hdd_ge32_v3pm10 ///
    SR_x_D_v3pm10 SR_x_W_v3pm10 SR_x_Heat_v3pm10 ///
    D_x_Heat_v3pm10 SR_x_D_x_Heat_v3pm10 ///
    D_hepm10 W_hepm10 hdd_ge32_hepm10 ///
    SR_x_D_hepm10 SR_x_W_hepm10 SR_x_Heat_hepm10 ///
    D_x_Heat_hepm10 SR_x_D_x_Heat_hepm10 ///
    ca

global RHS_hr_scheme_ii  ///
    D_v3he W_v3he hdd_ge32_v3he ///
    SR_x_D_v3he SR_x_W_v3he SR_x_Heat_v3he ///
    D_x_Heat_v3he SR_x_D_x_Heat_v3he ///
    D_hema W_hema hdd_ge32_hema ///
    SR_x_D_hema SR_x_W_hema SR_x_Heat_hema ///
    D_x_Heat_hema SR_x_D_x_Heat_hema ///
    ca

global RHS_hr_scheme_iii  ///
    D_v3pre30 W_v3pre30 hdd_ge32_v3pre30 ///
    SR_x_D_v3pre30 SR_x_W_v3pre30 SR_x_Heat_v3pre30 ///
    D_x_Heat_v3pre30 SR_x_D_x_Heat_v3pre30 ///
    D_v3he W_v3he hdd_ge32_v3he ///
    SR_x_D_v3he SR_x_W_v3he SR_x_Heat_v3he ///
    D_x_Heat_v3he SR_x_D_x_Heat_v3he ///
    D_hema W_hema hdd_ge32_hema ///
    SR_x_D_hema SR_x_W_hema SR_x_Heat_hema ///
    D_x_Heat_hema SR_x_D_x_Heat_hema ///
    ca
