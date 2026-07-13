# GGCP10 GLEAM mediation extensions

## Scope

This document indexes the 2026-05-19 GGCP10 aggregated-area GLEAM mechanism
extensions. The branch uses the aggregated GGCP10 harvested-area base and keeps
the older `v3/v6` outputs unchanged.

- Base panel: `temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_baseline_suite_analysis_ready.dta`
- Extension root: `temp/2026-05-19_ggcp10_mediation_extensions/`
- Soil-moisture source: GLEAM only
- Hazards: drought, heat, hot-dry compound
- Fixed effects: `grid_id` and `year`
- Cluster: `grid_id`
- Bootstrap policy: smoke bootstrap with 80 reps

## Branches

### SoilMoisture mean

- Directory: `temp/2026-05-19_ggcp10_mediation_extensions/mean/`
- Main script: `scripts/stata/ggcp10_mean_ext_run_all.do`
- TE update script: `scripts/stata/ggcp10_mean_overall_bootstrap_iede_te.do`
- Figure script: `scripts/R/ggcp10_mediation_extensions_make_figures.R`
- Feishu document:
  `https://vcn7opmi92n5.feishu.cn/docx/MGcwd6q3GoCp9Dxc1JbcBAIRnvb`

Outputs:

| File | Rows | Notes |
|------|------|-------|
| `ggcp10_mean_baseline_coefficients.csv` | 120 | Baseline coefficients for four windows, two GLEAM layers, and three hazards |
| `ggcp10_mean_bootstrap_iede.csv` | 216 | Overall smoke bootstrap for IE, DE, and TE |
| `ggcp10_mean_heterogeneity_coefficients.csv` | 960 | Irrigation and maize-zone heterogeneity coefficients |
| `ggcp10_mean_heterogeneity_effects.csv` | 384 | Irrigation and maize-zone IE/DE point estimates |
| `figures/*.png` | 21 | Coefficient, bootstrap, and heterogeneity plots |

The bootstrap file name keeps the historical `iede` suffix, but as of
2026-05-19 it contains `IE`, `DE`, and `TE` in the `effect` column. In the
figures, baseline significance uses `p < 0.05`; bootstrap significance uses
whether the interval excludes zero. Heterogeneity effect plots do not contain
inference intervals and are shown as hollow points.

### Wet-state mirror

- Directory: `temp/2026-05-19_ggcp10_mediation_extensions/wet_mirror/`
- Main script: `scripts/stata/ggcp10_wet_mirror_run_all.do`
- Figure script: `scripts/R/ggcp10_mediation_extensions_make_figures.R`
- Feishu document:
  `https://vcn7opmi92n5.feishu.cn/docx/GRn1dccSXofgUxxtasEc9Fi3nce`

Outputs:

| File | Rows | Notes |
|------|------|-------|
| `ggcp10_wet_mirror_baseline_coefficients.csv` | 330 | Fullnew-only wet-side baseline mirror |
| `figures/*.png` | 12 | Four path plots for each hazard |

### Dry-state top-3

- Directory: `temp/2026-05-19_ggcp10_mediation_extensions/dry_top3/`
- Main script: `scripts/stata/ggcp10_dry_top3_ext_run_all.do`
- Figure script: `scripts/R/ggcp10_mediation_extensions_make_figures.R`
- Feishu document:
  `https://vcn7opmi92n5.feishu.cn/docx/NZpid7wvVo4GVHxKwxDcWHzOnZg`

Selected mediators:

| Rank | Metric | Percentile | Layer | Variable | Selection basis |
|------|--------|------------|-------|----------|-----------------|
| 1 | `blseveritymean_ddf` | `p10` | GLEAM surface | `v6mdf_p10_fn_gss` | expected sign stability 9 of 9 |
| 2 | `blseveritysum_ddf` | `p10` | GLEAM rootzone | `v6sdf_p10_fn_gsr` | expected sign stability 9 of 9 |
| 3 | `blduration_dry` | `p10` | GLEAM surface | `v6dur_p10_fn_gss` | expected sign stability 8 of 9 |

Outputs:

| File | Rows | Notes |
|------|------|-------|
| `ggcp10_dry_top3_selection.csv` | 3 | Selection table |
| `ggcp10_dry_top3_baseline_coefficients.csv` | 45 | Baseline coefficients for the selected mediators |
| `ggcp10_dry_top3_bootstrap_iede.csv` | 54 | Smoke bootstrap for IE and DE |
| `ggcp10_dry_top3_heterogeneity_coefficients.csv` | 360 | Irrigation and maize-zone heterogeneity coefficients |
| `ggcp10_dry_top3_heterogeneity_effects.csv` | 144 | Irrigation and maize-zone IE/DE point estimates |
| `figures/*.png` | 21 | Coefficient, bootstrap, and heterogeneity plots |

## Verification

The following logs were checked and end with `COMPLETE`:

- `temp/2026-05-19_ggcp10_mediation_extensions/mean/logs/ggcp10_mean_ext_run_all.log`
- `temp/2026-05-19_ggcp10_mediation_extensions/mean/logs/ggcp10_mean_overall_bootstrap_iede_te.log`
- `temp/2026-05-19_ggcp10_mediation_extensions/wet_mirror/logs/ggcp10_wet_mirror_run_all.log`
- `temp/2026-05-19_ggcp10_mediation_extensions/dry_top3/logs/ggcp10_dry_top3_ext_run_all.log`

The Markdown-to-Feishu workflow uses:

- `scripts/python/render_markdown_feishu_doc.py`
- Source Markdown files inside each branch directory
- Local PNG figures under each branch's `figures/` directory
