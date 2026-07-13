* =============================================================================
* 00_preamble.do — Shared preamble for SR buffering regression analysis
* Purpose: Path macros, data loading, sample filtering, variable construction
* Author: YangSu / Claude Code
* Date: 2026-03-12
* Dependencies: data_v1_with_climate.csv, reghdfe, estout
* =============================================================================

clear all
set more off
set seed 42

* -----------------------------------------------------------------------------
* 1. Path macros
* -----------------------------------------------------------------------------
global projdir  "C:/YangSu/00_Project/CA_mechanism/regression_SR"
global datadir  "C:/YangSu/00_Project/CA_mechanism/data/master"
global outdir   "$projdir/output/tables"
global figdir   "$projdir/output/figures"
global logdir   "$projdir/output/logs"

* Ensure output directories exist
cap mkdir "$outdir"
cap mkdir "$figdir"
cap mkdir "$logdir"

* -----------------------------------------------------------------------------
* 2. Data loading
* -----------------------------------------------------------------------------
import delimited "$datadir/data_v1_with_climate.csv", clear case(preserve)

* -----------------------------------------------------------------------------
* 3. Sample filtering
* -----------------------------------------------------------------------------
keep if china_mask == 1
keep if yield_tons_ha > 0 & !missing(yield_tons_ha)
keep if maize_area_km2 > 0 & !missing(maize_area_km2)
drop if missing(ln_yield)
drop if missing(ca)
drop if missing(SPEI_season)

* Report sample size
di "=== Sample size after filtering: " _N " ==="

* -----------------------------------------------------------------------------
* 4. Variable construction (Blueprint-aligned)
* -----------------------------------------------------------------------------

* --- D (drought) and W (wetness) from SPEI decomposition ---
gen D_season = max(0, -SPEI_season)
gen W_season = max(0,  SPEI_season)
label var D_season "Drought stress: max(0, -SPEI)"
label var W_season "Wetness stress: max(0, SPEI)"

* --- SR variable (already exists as `ca`) ---
* ca = straw return adoption ratio [0,1]
label var ca "Straw return adoption ratio"

* --- Main heat indicator (default: HDD >= 32°C) ---
* hdd_tmax_ge32 already in data (tasseling-window or season aggregate)
label var hdd_tmax_ge32 "Hot degree days (Tmax >= 32C)"

* --- Interaction terms ---
gen SR_x_D    = ca * D_season
gen SR_x_W    = ca * W_season
gen SR_x_Heat = ca * hdd_tmax_ge32
label var SR_x_D    "SR x Drought"
label var SR_x_W    "SR x Wetness"
label var SR_x_Heat "SR x Heat (HDD>=32)"

* --- Controls ---
global CTRL irr_frac pre_sum et0_sum wd_aridity_et0divpre gdd_30

* --- Panel setup ---
xtset grid_id year

di "=== Preamble complete. Panel: grid_id x year. N = " _N " ==="
