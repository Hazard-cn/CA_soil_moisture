# Data Sources and Definitions

## Primary analysis dataset

File: `C:/YangSu/00_Project/CA_mechanism/data/master/data_v1_with_climate.csv`  
Repository-local alias: `data/processed/data_v1_with_climate.csv` is not present.  
Unit of observation: grid-year (0.1 degree grid, annual panel)  
Time coverage: 2016-2019 (`year` min/max from file scan)  
Spatial coverage/resolution: China maize-relevant grids, approx. 0.1 degree; latitude 21.73 to 51.13, longitude 75.58 to 134.58

## Provenance

- Created by: not explicitly documented in repo; analysis code bundle is in `references/code/*.R` (all files last modified 2024-12-19)
- Raw inputs: not fully enumerated in a single script in this repo; variable names indicate merged inputs from climate/reanalysis (`t2m_*`, `pre_sum`, `et0_*`, `gleam_*`), management (`crc_ca_ratio`, `crc_lag1`, `irr_frac`, `ca`), and maize production/area fields
- Processing steps (high level):
  1) Build grid-year panel keyed by `year`, `latitude`, `longitude` and grouped keys (`grid_id`, `prov_id`, `prov_year`)
  2) Aggregate in-season climate/water indicators (including lag30 windows and threshold-based extreme metrics)
  3) Merge management/adoption, irrigation, and yield-related variables to produce analysis-ready table

## Variable dictionary (core)

Columns:

- y: `yield_tons_ha`, maize yield in tons/ha; `ln_yield` is natural log transform of `yield_tons_ha`
- CA: `ca` (adoption ratio, 0-1), `crc_ca_ratio` (current-year adoption ratio, 0-1), `crc_lag1` (lag-1 adoption ratio, 0-1)
- n_level: not found as a standalone column in this dataset version (`n_level` absent from header)
- controls_*: climate and water controls are column families such as `*_mean`, `*_sum`, `*_min`, `*_max`, `lag30_*`, and threshold metrics (`*basep10`, `*basep20`, `*basep90`, `*basep95`); examples include `t2m_mean`, `pre_sum`, `gleam_smrz_mean`, `wd_deficit_et0minuspre`, `hotdays_tmax_ge32`, `drydays_gleam_smrz_le_basep20`, `SPEI_season`, `VPD_season_mean`
- id/time keys: `year`, `latitude`, `longitude`, `grid_id`, `prov_id`, `prov_year`

## Missing values and filters

- Missing codes: observed missing values are blank/`NA`; sentinel values `-999`/`-9999` were not found in a full-table scan
- Sample filters: explicit filter rules are not documented in repo-level docs; observed sample is positive-yield maize grid-years (in this file, `yield_tons_ha` is always > 0)
- Outlier handling: no universal winsorization or trimming rule is defined in the root variable dictionary; branch-specific scripts document their own transformations

## Notes for reproducibility

- Sort keys: `grid_id`, `year` (or full key `year`, `latitude`, `longitude`)
- Expected row count: 69,038 rows; 143 columns
- Sanity checks:
  - soc range: N/A in this file (no explicit `soc` column present)
  - y range: `yield_tons_ha` in [0.2001, 19.9958], `ln_yield` in [-1.6089, 2.9955]
  - missing rate thresholds: no formal threshold documented; current core-key missingness is 0% for `year`, `latitude`, `longitude`, `grid_id`, `prov_id`, `prov_year`; core outcome missingness is 0% for `yield_tons_ha` and `ln_yield`

## Current G185 branch inputs

- Base panel: `temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_baseline_suite_analysis_ready.dta`
- Hot-dry source: `data_build/data/processed/data_v3_main.dta`
- Current reconstruction entry: `scripts/python/ggcp10_parallel_rules_69038_search.py::load_panel`

## Heterogeneity threshold rules (CA-CC GRF)

- Heat indicators:
  - `hdd_tmax_ge32`: high-heat group = `>= p75`
  - `hdd_tmax_ge35`: high-heat group = `>= p75`
  - `hdd_tmax_ge38`: if `p75 == 0`, use high-heat group `> 0`; otherwise `>= p75`
- Drought indicators:
  - `wd_deficit_et0minuspre`: drought group = `>= p75`
  - `SPEI_season` (robustness): drought group = `<= p25`
- Soil moisture indicator:
  - `gleam_smrz_mean`: low-soil-moisture group = `<= p25`
- Irrigation indicator:
  - `irr_frac`: high-irrigation group = `>= p75`
