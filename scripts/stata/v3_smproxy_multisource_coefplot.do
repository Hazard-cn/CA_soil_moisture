* =============================================================================
* v3_smproxy_multisource_coefplot.do
* Purpose: Replace SPEI drought with standardized soil-moisture proxy and
*          estimate H-SM-SR interaction models across 3 sources x 2 layers
*          x 6 windows, exporting coefficient plots only.
* Input:   data/processed/v3prhdsm_analysis_ready.dta
* Output:  output/tables/v3_smproxy_multisource_long.csv
*          output/figures/v3_smproxy_surface_coefplot.png
*          output/figures/v3_smproxy_rootzone_coefplot.png
*          output/figures/v3_smproxy_term_dry_sm.png
*          output/figures/v3_smproxy_term_H.png
*          output/figures/v3_smproxy_term_SR.png
*          output/figures/v3_smproxy_term_dry_sm_x_H.png
*          output/figures/v3_smproxy_term_SR_x_H.png
*          output/figures/v3_smproxy_term_SR_x_dry_sm.png
*          output/figures/v3_smproxy_term_SR_x_dry_sm_x_H.png
* =============================================================================

clear all
set more off
set seed 42

do "C:/YangSu/00_Project/CA_mechanism/regression_SR/scripts/stata/v3prhdsm_macros_include.do"

log using "$logdir/v3_smproxy_multisource_coefplot.log", replace

use "$outdata/v3prhdsm_analysis_ready.dta", clear
xtset grid_id year

confirm variable ln_yield ca grid_id year main_sample
confirm variable hdd_ge32 hdd_ge32_v3pre30 hdd_ge32_v3pm10 hdd_ge32_hepm10 hdd_ge32_v3he hdd_ge32_hema

foreach smvar in gleam_sms_mean gleam_smrz_mean swsm_l1_mean swsm_l3_mean ///
    era5l_swvl1_mean era5l_swvl3_mean ///
    gleam_sms_mean_v3pre30 gleam_smrz_mean_v3pre30 swsm_l1_mean_v3pre30 swsm_l3_mean_v3pre30 era5l_swvl1_mean_v3pre30 era5l_swvl3_mean_v3pre30 ///
    gleam_sms_mean_v3pm10 gleam_smrz_mean_v3pm10 swsm_l1_mean_v3pm10 swsm_l3_mean_v3pm10 era5l_swvl1_mean_v3pm10 era5l_swvl3_mean_v3pm10 ///
    gleam_sms_mean_hepm10 gleam_smrz_mean_hepm10 swsm_l1_mean_hepm10 swsm_l3_mean_hepm10 era5l_swvl1_mean_hepm10 era5l_swvl3_mean_hepm10 ///
    gleam_sms_mean_v3he gleam_smrz_mean_v3he swsm_l1_mean_v3he swsm_l3_mean_v3he era5l_swvl1_mean_v3he era5l_swvl3_mean_v3he ///
    gleam_sms_mean_hema gleam_smrz_mean_hema swsm_l1_mean_hema swsm_l3_mean_hema era5l_swvl1_mean_hema era5l_swvl3_mean_hema {
    confirm variable `smvar'
}

capture program drop post_smproxy_terms
program define post_smproxy_terms
    syntax, POST(name) SOURCE(string) LAYER(string) WINDOW(string)

    local dfr = e(df_r)
    local N   = e(N)
    local r2  = e(r2)

    foreach pair in ///
        "sm_proxy dry_sm" ///
        "heat_proxy H" ///
        "ca SR" ///
        "int_smh dry_sm_x_H" ///
        "int_srh SR_x_H" ///
        "int_srsm SR_x_dry_sm" ///
        "int_srsmh SR_x_dry_sm_x_H" {
        tokenize `"`pair'"'
        local coef = "`1'"
        local label = "`2'"
        local p = 2 * ttail(`dfr', abs(_b[`coef'] / _se[`coef']))
        post `post' ("`source'") ("`layer'") ("`window'") ///
            ("`coef'") ("`label'") ///
            (_b[`coef']) (_se[`coef']) (`p') (`N') (`r2')
    }
end

capture program drop make_coefplot_panel_smproxy
program define make_coefplot_panel_smproxy
    syntax, LAYER(string) SOURCE(string) NAME(name) TITLE(string)

    local m_full    m_`layer'_`source'_full
    local m_v3pre30 m_`layer'_`source'_v3pre30
    local m_v3pm10  m_`layer'_`source'_v3pm10
    local m_hepm10  m_`layer'_`source'_hepm10
    local m_v3he    m_`layer'_`source'_v3he
    local m_hema    m_`layer'_`source'_hema

    coefplot ///
        (`m_full',    label("Full")) ///
        (`m_v3pre30', label("V3pre30")) ///
        (`m_v3pm10',  label("V3pm10")) ///
        (`m_hepm10',  label("HEpm10")) ///
        (`m_v3he',    label("V3HE")) ///
        (`m_hema',    label("HEMA")), ///
        keep(int_smh int_srh int_srsm int_srsmh) ///
        order(int_smh int_srh int_srsm int_srsmh) ///
        coeflabels( ///
            int_smh   = "dry_sm x H" ///
            int_srh   = "SR x H" ///
            int_srsm  = "SR x dry_sm" ///
            int_srsmh = "SR x dry_sm x H") ///
        drop(_cons) ///
        xline(0, lcolor(gs10) lpattern(dash)) ///
        ciopts(recast(rcap)) ///
        levels(95) ///
        xlabel(#4, format(%9.3f) labsize(vsmall)) ///
        ylabel(, labsize(medsmall)) ///
        legend(rows(2) size(vsmall)) ///
        title("`title'") ///
        graphregion(color(white) margin(l+4 r+4 t+2 b+2)) ///
        plotregion(color(white) margin(l+8 r+2 t+1 b+1)) ///
        name(`name', replace)
end

capture program drop make_manual_panel_smproxy
program define make_manual_panel_smproxy
    syntax, LAYER(string) SOURCE(string) NAME(name) TITLE(string)

    preserve
    use "$outdir/v3_smproxy_multisource_long.dta", clear
    keep if layer == "`layer'" & source == "`source'"

    gen term_id = .
    replace term_id = 4 if term == "int_smh"
    replace term_id = 3 if term == "int_srh"
    replace term_id = 2 if term == "int_srsm"
    replace term_id = 1 if term == "int_srsmh"
    assert !missing(term_id)

    gen offset = .
    replace offset = -0.30 if window == "full"
    replace offset = -0.18 if window == "v3pre30"
    replace offset = -0.06 if window == "v3pm10"
    replace offset =  0.06 if window == "hepm10"
    replace offset =  0.18 if window == "v3he"
    replace offset =  0.30 if window == "hema"
    assert !missing(offset)

    gen y = term_id + offset
    gen ci_lo = b - 1.96 * se
    gen ci_hi = b + 1.96 * se

    twoway ///
        (rcap ci_hi ci_lo y if window == "full", horizontal lcolor(navy)) ///
        (scatter y b if window == "full", msymbol(O) mcolor(navy) msize(small)) ///
        (rcap ci_hi ci_lo y if window == "v3pre30", horizontal lcolor(maroon)) ///
        (scatter y b if window == "v3pre30", msymbol(D) mcolor(maroon) msize(small)) ///
        (rcap ci_hi ci_lo y if window == "v3pm10", horizontal lcolor(forest_green)) ///
        (scatter y b if window == "v3pm10", msymbol(T) mcolor(forest_green) msize(small)) ///
        (rcap ci_hi ci_lo y if window == "hepm10", horizontal lcolor(orange_red)) ///
        (scatter y b if window == "hepm10", msymbol(S) mcolor(orange_red) msize(small)) ///
        (rcap ci_hi ci_lo y if window == "v3he", horizontal lcolor(teal)) ///
        (scatter y b if window == "v3he", msymbol(O) mcolor(teal) msize(small)) ///
        (rcap ci_hi ci_lo y if window == "hema", horizontal lcolor(cranberry)) ///
        (scatter y b if window == "hema", msymbol(D) mcolor(cranberry) msize(small)), ///
        xline(0, lcolor(gs10) lpattern(dash)) ///
        ylabel(1 "SR x dry_sm x H" 2 "SR x dry_sm" 3 "SR x H" 4 "dry_sm x H", angle(0)) ///
        xlabel(#4, format(%9.3f) labsize(vsmall)) ///
        yscale(range(0.5 4.5)) ///
        ytitle("") ///
        xtitle("Coefficient") ///
        title("`title'") ///
        legend(order(2 "Full" 4 "V3pre30" 6 "V3pm10" 8 "HEpm10" 10 "V3HE" 12 "HEMA") ///
            rows(2) size(vsmall)) ///
        graphregion(color(white) margin(l+4 r+4 t+2 b+2)) ///
        plotregion(color(white) margin(l+8 r+2 t+1 b+1)) ///
        name(`name', replace)
    restore
end

capture program drop make_term_panel_smproxy
program define make_term_panel_smproxy
    syntax, TERM(string) NAME(name) TITLE(string) SHOWLEGEND(integer)

    preserve
    use "$outdir/v3_smproxy_multisource_long.dta", clear
    keep if term == "`term'"

    gen group_id = .
    replace group_id = 6 if source == "gleam" & layer == "surface"
    replace group_id = 5 if source == "gleam" & layer == "rootzone"
    replace group_id = 4 if source == "swsm"  & layer == "surface"
    replace group_id = 3 if source == "swsm"  & layer == "rootzone"
    replace group_id = 2 if source == "era"   & layer == "surface"
    replace group_id = 1 if source == "era"   & layer == "rootzone"
    assert !missing(group_id)

    gen offset = .
    replace offset = -0.30 if window == "full"
    replace offset = -0.18 if window == "v3pre30"
    replace offset = -0.06 if window == "v3pm10"
    replace offset =  0.06 if window == "hepm10"
    replace offset =  0.18 if window == "v3he"
    replace offset =  0.30 if window == "hema"
    assert !missing(offset)

    gen y = group_id + offset
    gen ci_lo = b - 1.96 * se
    gen ci_hi = b + 1.96 * se

    local legendopt "legend(off)"
    if `showlegend' == 1 {
        local legendopt ///
            legend(order(2 "Full" 4 "V3pre30" 6 "V3pm10" 8 "HEpm10" 10 "V3HE" 12 "HEMA") ///
            rows(2) size(vsmall) region(lstyle(none)))
    }

    twoway ///
        (rcap ci_hi ci_lo y if window == "full", horizontal lcolor(navy)) ///
        (scatter y b if window == "full", msymbol(O) mcolor(navy) msize(small)) ///
        (rcap ci_hi ci_lo y if window == "v3pre30", horizontal lcolor(maroon)) ///
        (scatter y b if window == "v3pre30", msymbol(D) mcolor(maroon) msize(small)) ///
        (rcap ci_hi ci_lo y if window == "v3pm10", horizontal lcolor(forest_green)) ///
        (scatter y b if window == "v3pm10", msymbol(T) mcolor(forest_green) msize(small)) ///
        (rcap ci_hi ci_lo y if window == "hepm10", horizontal lcolor(orange_red)) ///
        (scatter y b if window == "hepm10", msymbol(S) mcolor(orange_red) msize(small)) ///
        (rcap ci_hi ci_lo y if window == "v3he", horizontal lcolor(teal)) ///
        (scatter y b if window == "v3he", msymbol(O) mcolor(teal) msize(small)) ///
        (rcap ci_hi ci_lo y if window == "hema", horizontal lcolor(cranberry)) ///
        (scatter y b if window == "hema", msymbol(D) mcolor(cranberry) msize(small)), ///
        xline(0, lcolor(gs10) lpattern(dash)) ///
        ylabel(1 "ERA rootzone" 2 "ERA surface" 3 "SWSM rootzone" 4 "SWSM surface" 5 "GLEAM rootzone" 6 "GLEAM surface", angle(0) labsize(small)) ///
        xlabel(#4, format(%9.3f) labsize(vsmall)) ///
        yscale(range(0.5 6.5)) ///
        ytitle("") ///
        xtitle("Coefficient") ///
        title("`title'") ///
        `legendopt' ///
        graphregion(color(white) margin(l+6 r+4 t+2 b+2)) ///
        plotregion(color(white) margin(l+10 r+2 t+1 b+1)) ///
        name(`name', replace)
    restore
end

tempname pf
postfile `pf' str12 source str12 layer str10 window str16 term str24 term_label ///
    double b se p N r2 using "$outdir/v3_smproxy_multisource_long.dta", replace

local windows "full v3pre30 v3pm10 hepm10 v3he hema"
local sources "gleam swsm era"
local layers  "surface rootzone"

foreach layer in `layers' {
    foreach source in `sources' {
        foreach window in `windows' {
            preserve

            local hsfx = cond("`window'" == "full", "", "_`window'")
            local heat_var = "hdd_ge32`hsfx'"
            local ctrl "${CTRL_`window'}"
            if "`window'" == "full" {
                local ctrl "$CTRL_full"
            }

            if "`source'" == "gleam" & "`layer'" == "surface"  local sm_var "gleam_sms_mean`hsfx'"
            if "`source'" == "gleam" & "`layer'" == "rootzone" local sm_var "gleam_smrz_mean`hsfx'"
            if "`source'" == "swsm"  & "`layer'" == "surface"  local sm_var "swsm_l1_mean`hsfx'"
            if "`source'" == "swsm"  & "`layer'" == "rootzone" local sm_var "swsm_l3_mean`hsfx'"
            if "`source'" == "era"   & "`layer'" == "surface"  local sm_var "era5l_swvl1_mean`hsfx'"
            if "`source'" == "era"   & "`layer'" == "rootzone" local sm_var "era5l_swvl3_mean`hsfx'"

            confirm variable `sm_var'
            confirm variable `heat_var'

            quietly summarize `sm_var' if main_sample == 1, detail
            local sm_mean = r(mean)
            local sm_sd   = r(sd)
            local sm_n    = r(N)

            if `sm_n' <= 0 {
                di as error "No usable main_sample observations for `sm_var'"
                exit 2000
            }
            if `sm_sd' <= 0 {
                di as error "Zero SD for `sm_var' in main_sample"
                exit 498
            }

            gen double sm_proxy = -((`sm_var' - `sm_mean') / `sm_sd') if main_sample == 1
            gen double heat_proxy = `heat_var' if main_sample == 1
            gen double int_smh = sm_proxy * heat_proxy if main_sample == 1
            gen double int_srh = ca * heat_proxy if main_sample == 1
            gen double int_srsm = ca * sm_proxy if main_sample == 1
            gen double int_srsmh = ca * sm_proxy * heat_proxy if main_sample == 1

            quietly correlate sm_proxy `sm_var' if main_sample == 1
            matrix C = r(C)
            local rho = el(C, 1, 2)
            di as txt "Model: `layer' | `source' | `window' | corr(sm_proxy, raw_sm) = " ///
                %6.4f `rho' " | sd = " %8.4f `sm_sd'

            reghdfe ln_yield ///
                sm_proxy heat_proxy ca ///
                int_smh int_srh int_srsm int_srsmh ///
                `ctrl' ///
                if main_sample == 1, ///
                absorb(grid_id year) vce(cluster grid_id)

            local estname m_`layer'_`source'_`window'
            estimates store `estname'
            post_smproxy_terms, post(`pf') source("`source'") layer("`layer'") window("`window'")

            restore
        }
    }
}

postclose `pf'

preserve
use "$outdir/v3_smproxy_multisource_long.dta", clear
format b se %9.6f
format p %7.4f
format N %12.0f
format r2 %7.4f
sort layer source window term
export delimited using "$outdir/v3_smproxy_multisource_long.csv", replace

count
assert r(N) == 252

bysort source layer window: gen byte _model_tag = (_n == 1)
count if _model_tag == 1
assert r(N) == 36
drop _model_tag
restore

cap which coefplot
local has_coefplot = (_rc == 0)
di as txt "coefplot available = " `has_coefplot'

foreach layer in `layers' {
    local layer_title = cond("`layer'" == "surface", "Surface", "Rootzone")
    foreach source in `sources' {
        local panel_name g_`layer'_`source'
        local panel_title = upper("`source'")

        if `has_coefplot' {
            make_coefplot_panel_smproxy, ///
                layer("`layer'") source("`source'") name(`panel_name') title("`panel_title'")
        }
        else {
            make_manual_panel_smproxy, ///
                layer("`layer'") source("`source'") name(`panel_name') title("`panel_title'")
        }
    }

    graph combine g_`layer'_gleam g_`layer'_swsm g_`layer'_era, ///
        col(3) xcommon imargin(small) ///
        title("`layer_title' SM proxy coefficients") ///
        subtitle("Models: ln_yield on H, dry_sm, SR, and hierarchical interactions") ///
        graphregion(color(white) margin(l+12 r+6 t+4 b+4)) name(g_`layer'_combined, replace)

    graph export "$figdir/v3_smproxy_`layer'_coefplot.png", replace width(4200)
}

make_term_panel_smproxy, term("sm_proxy")   name(g_term_sm)     title("dry_sm")            showlegend(1)
make_term_panel_smproxy, term("heat_proxy") name(g_term_h)      title("H")                 showlegend(0)
make_term_panel_smproxy, term("ca")         name(g_term_sr)     title("SR")                showlegend(0)
make_term_panel_smproxy, term("int_smh")   name(g_term_smh)   title("dry_sm x H")       showlegend(1)
make_term_panel_smproxy, term("int_srh")   name(g_term_srh)   title("SR x H")           showlegend(0)
make_term_panel_smproxy, term("int_srsm")  name(g_term_srsm)  title("SR x dry_sm")      showlegend(0)
make_term_panel_smproxy, term("int_srsmh") name(g_term_srsmh) title("SR x dry_sm x H")  showlegend(0)

graph display g_term_sm, xsize(8) ysize(6)
graph export "$figdir/v3_smproxy_term_dry_sm.png", replace width(3200)
graph display g_term_h, xsize(8) ysize(6)
graph export "$figdir/v3_smproxy_term_H.png", replace width(3200)
graph display g_term_sr, xsize(8) ysize(6)
graph export "$figdir/v3_smproxy_term_SR.png", replace width(3200)
graph display g_term_smh, xsize(8) ysize(6)
graph export "$figdir/v3_smproxy_term_dry_sm_x_H.png", replace width(3200)
graph display g_term_srh, xsize(8) ysize(6)
graph export "$figdir/v3_smproxy_term_SR_x_H.png", replace width(3200)
graph display g_term_srsm, xsize(8) ysize(6)
graph export "$figdir/v3_smproxy_term_SR_x_dry_sm.png", replace width(3200)
graph display g_term_srsmh, xsize(8) ysize(6)
graph export "$figdir/v3_smproxy_term_SR_x_dry_sm_x_H.png", replace width(3200)

foreach fig in ///
    "$figdir/v3_smproxy_surface_coefplot.png" ///
    "$figdir/v3_smproxy_rootzone_coefplot.png" ///
    "$figdir/v3_smproxy_term_dry_sm.png" ///
    "$figdir/v3_smproxy_term_H.png" ///
    "$figdir/v3_smproxy_term_SR.png" ///
    "$figdir/v3_smproxy_term_dry_sm_x_H.png" ///
    "$figdir/v3_smproxy_term_SR_x_H.png" ///
    "$figdir/v3_smproxy_term_SR_x_dry_sm.png" ///
    "$figdir/v3_smproxy_term_SR_x_dry_sm_x_H.png" ///
    "$outdir/v3_smproxy_multisource_long.csv" {
    capture confirm file `"`fig'"'
    if _rc != 0 {
        di as error "Missing expected output: `fig'"
        exit 601
    }
}

di "========================================================"
di "v3_smproxy_multisource_coefplot.do COMPLETE"
di "Outputs:"
di "  $outdir/v3_smproxy_multisource_long.csv"
di "  $figdir/v3_smproxy_surface_coefplot.png"
di "  $figdir/v3_smproxy_rootzone_coefplot.png"
di "  $figdir/v3_smproxy_term_dry_sm.png"
di "  $figdir/v3_smproxy_term_H.png"
di "  $figdir/v3_smproxy_term_SR.png"
di "  $figdir/v3_smproxy_term_dry_sm_x_H.png"
di "  $figdir/v3_smproxy_term_SR_x_H.png"
di "  $figdir/v3_smproxy_term_SR_x_dry_sm.png"
di "  $figdir/v3_smproxy_term_SR_x_dry_sm_x_H.png"
di "========================================================"

log close
