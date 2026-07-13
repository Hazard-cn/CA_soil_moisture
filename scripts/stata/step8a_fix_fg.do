* =============================================================================
* step8a_fix_fg.do — Fix Parts F & G from step8a_boundary.do
* Issue: decode prov_year fails because prov_year is numeric, not labeled
* =============================================================================

global projdir "C:/YangSu/00_Project/CA_mechanism/regression_SR"
do "$projdir/scripts/stata/00_preamble.do"

log using "$logdir/step8a_fix_fg_20260317.log", replace

* Reconstruct needed variables
cap drop D_x_Heat SR_x_D_x_Heat
gen D_x_Heat = D_season * hdd_tmax_ge32
gen SR_x_D_x_Heat = ca * D_season * hdd_tmax_ge32

global RHS_COMPOUND D_season W_season hdd_tmax_ge32 ca ///
	SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat $CTRL

reghdfe ln_yield $RHS_COMPOUND, absorb(grid_id year) vce(cluster grid_id)
gen main_sample = e(sample)
local main_N = e(N)

* Discretization
xtile D_bin3 = D_season if main_sample==1, nq(3)
xtile H_bin3 = hdd_tmax_ge32 if main_sample==1, nq(3)
sum ca if main_sample==1, detail
gen SR_high = (ca >= r(p50)) if main_sample==1

* Stress corner
gen stress_corner = (D_bin3==3 & H_bin3==3) if main_sample==1

* =============================================================================
* Part F: D-H Support (四合一)
* =============================================================================

di _n "=== Part F: D-H Joint Support (四合一) ==="

* --- F1: D×H density ---
di _n "--- F1: D×H Density ---"
tab D_bin3 H_bin3 if main_sample==1

* --- F2: Stress corner SR variation ---
di _n "--- F2: Stress Corner SR Variation ---"
sum ca if stress_corner==1, detail
local sr_mean_corner = r(mean)
local sr_sd_corner = r(sd)
local sr_cv_corner = r(sd) / r(mean)
di "Stress corner: SR mean=" round(`sr_mean_corner', 0.001) ///
	" SD=" round(`sr_sd_corner', 0.001) ///
	" CV=" round(`sr_cv_corner', 0.01)

sum ca if main_sample==1, detail
local sr_mean_full = r(mean)
local sr_sd_full = r(sd)

* --- F3: Province-year concentration (FIX: use tostring instead of decode) ---
di _n "--- F3: Province-Year Concentration ---"

preserve
keep if stress_corner==1

* Use province and year directly (prov_year is just a group ID)
contract province year, freq(n_obs)
gsort -n_obs
gen cum_n = sum(n_obs)
local total_corner = cum_n[_N]
gen cum_share = cum_n / `total_corner' * 100

* Also compute SR mean and yield loss for each prov-year in corner
* (need to merge back from full data)

di "Total obs in stress corner: `total_corner'"
di "Top province-year units:"
list province year n_obs cum_share in 1/10, sep(0) noobs
export delimited "$outdir/step8a_corner_provyr.csv", replace
restore

* Get SR mean and yield for top prov-years in corner
preserve
keep if stress_corner==1
collapse (mean) sr_mean=ca yield_mean=ln_yield (count) n=ca, by(province year)
gsort -n
gen cum_n = sum(n)
local total_corner2 = cum_n[_N]
gen cum_share = cum_n / `total_corner2' * 100

di _n "Province-year concentration with SR and yield:"
list province year n cum_share sr_mean yield_mean in 1/10, sep(0) noobs

* Top1, Top3, Top5 cumulative share
di "Top 1 share: " cum_share[1] "%"
if _N >= 3 di "Top 3 share: " cum_share[3] "%"
if _N >= 5 di "Top 5 share: " cum_share[5] "%"

export delimited "$outdir/step8a_corner_provyr_detail.csv", replace
restore

* --- F4: Corner avg loss vs full sample ---
di _n "--- F4: Corner Average Loss ---"
sum ln_yield if stress_corner==1, detail
local yield_corner = r(mean)
local n_corner = r(N)
sum ln_yield if main_sample==1, detail
local yield_full = r(mean)
local loss_diff = `yield_corner' - `yield_full'
di "Avg ln_yield in stress corner: " round(`yield_corner', 0.001)
di "Avg ln_yield full sample:      " round(`yield_full', 0.001)
di "Difference (corner - full):    " round(`loss_diff', 0.001)

* Export summary
preserve
clear
set obs 9
gen str40 metric = ""
gen value = .
replace metric = "corner_N" in 1
replace value = `n_corner' in 1
replace metric = "corner_SR_mean" in 2
replace value = `sr_mean_corner' in 2
replace metric = "corner_SR_sd" in 3
replace value = `sr_sd_corner' in 3
replace metric = "corner_SR_cv" in 4
replace value = `sr_cv_corner' in 4
replace metric = "full_SR_mean" in 5
replace value = `sr_mean_full' in 5
replace metric = "full_SR_sd" in 6
replace value = `sr_sd_full' in 6
replace metric = "corner_avg_lnyield" in 7
replace value = `yield_corner' in 7
replace metric = "full_avg_lnyield" in 8
replace value = `yield_full' in 8
replace metric = "loss_diff" in 9
replace value = `loss_diff' in 9
export delimited "$outdir/step8a_dh_support.csv", replace
restore

di "Part F complete."

* =============================================================================
* Part G: Response Surface (model-based adjusted predictions)
* =============================================================================

di _n "=== Part G: Response Surface (Model-Based Adjusted Predictions) ==="

* Use areg with full interaction for margins
areg ln_yield i.D_bin3##i.H_bin3##i.SR_high ///
	$CTRL i.year if main_sample==1, ///
	absorb(grid_id) vce(cluster grid_id)

margins D_bin3#H_bin3#SR_high, post

* Extract adjusted means manually
matrix B = e(b)
matrix V = e(V)
local ncols = colsof(B)
di "Number of margins estimates: `ncols'"

* Build output dataset
preserve
clear
set obs 18

gen D_bin = .
gen H_bin = .
gen SR_group = .
gen adj_mean = .
gen adj_se = .

local row = 0
forvalues d = 1/3 {
	forvalues h = 1/3 {
		forvalues s = 0/1 {
			local row = `row' + 1
			replace D_bin = `d' in `row'
			replace H_bin = `h' in `row'
			replace SR_group = `s' in `row'
			replace adj_mean = B[1, `row'] in `row'
			replace adj_se = sqrt(V[`row', `row']) in `row'
		}
	}
}

export delimited "$outdir/step8a_response_surface.csv", replace
list, sep(0) noobs
restore

di "Part G complete."

di _n "============================================================"
di "Step 8A Fix (Parts F & G) — COMPLETE"
di "============================================================"

log close
