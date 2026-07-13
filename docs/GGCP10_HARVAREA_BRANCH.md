# GGCP10 harvested-area branch

## Purpose

This branch keeps the existing `v3/v6` chain unchanged and reruns the latest `v6gleambl`
workflow with GGCP10 harvested area substituted into the area-dependent variables.

## Raw input

- Source folder: `data_build/data/raw/GGCP10_HarvArea_2010-2020/GGCP10_HarvArea_2010-2020/`
- Files used: `HarvArea_Maize_2016.tif` to `HarvArea_Maize_2019.tif`
- CRS: `EPSG:4326`
- Raster nodata: `-9999`
- Raw unit: `thousand ha`
- Conversion: `1 thousand ha = 10 km2`

## Branch outputs

- Run directory: `temp/2026-05-18_ggcp10_harvarea_v6gleambl/`
- Area sidecar: `ggcp10_harvarea_sidecar.{csv,dta}`
- Regression-ready branch base: `v3_analysis_ready_ggcp10_harvarea.dta`
- v6 outputs: `v6gleambl_harvarea_*`
- Bootstrap policy for this branch: smoke bootstrap only, `V6_BOOT_REPS = 20`

## Aggregated-area follow-up branch

The later aggregated-area rerun is a separate branch and should be treated as the
current GGCP10 area base for the May 2026 GLEAM mechanism extensions.

- Base directory: `temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/`
- Canonical aggregated-area panel: `v3_analysis_ready_ggcp10_harvarea_agg.dta`
- Baseline suite panel: `ggcp10_baseline_suite_analysis_ready.dta`
- Full-family dry-side v6 directory:
  `temp/2026-05-18_ggcp10_harvarea_agg_v6gleambl_fullfamily/`
- Full-family dry-side online document:
  `https://vcn7opmi92n5.feishu.cn/docx/VR9Nd74YKo4OMLxp4hhczCMUnzf`
- Follow-up mechanism extension index:
  `docs/GGCP10_MEDIATION_EXTENSIONS.md`

## Variable policy

- `maize_area_km2` is replaced by GGCP10 harvested area after unit conversion.
- `ggcp10_maize_frac = maize_area_km2 / pixel_area_km2`.
- `maize_yield_km2 = maize_prod / maize_area_km2`.
- `yield_tons_ha = maize_yield_km2 * 10`.
- `ln_yield = ln(yield_tons_ha)`.
- Legacy `maize_frac` is retained unchanged because it comes from the phenology source
  and is not the same construct as GGCP10 harvested-area share.
