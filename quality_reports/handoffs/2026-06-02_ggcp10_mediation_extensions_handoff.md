# 2026-06-02 GGCP10 mediation extensions handoff

## Current truth locations

- Branch index: `docs/GGCP10_MEDIATION_EXTENSIONS.md`
- Area branch context: `docs/GGCP10_HARVAREA_BRANCH.md`
- Extension root: `temp/2026-05-19_ggcp10_mediation_extensions/`
- Full-family dry-side precursor:
  `temp/2026-05-18_ggcp10_harvarea_agg_v6gleambl_fullfamily/`

## Online documents

- SoilMoisture mean:
  `https://vcn7opmi92n5.feishu.cn/docx/MGcwd6q3GoCp9Dxc1JbcBAIRnvb`
- Wet-state mirror:
  `https://vcn7opmi92n5.feishu.cn/docx/GRn1dccSXofgUxxtasEc9Fi3nce`
- Dry-state top-3:
  `https://vcn7opmi92n5.feishu.cn/docx/NZpid7wvVo4GVHxKwxDcWHzOnZg`

## Reproduction entry points

- Mean baseline, bootstrap, and heterogeneity:
  `scripts/stata/ggcp10_mean_ext_run_all.do`
- Mean overall IE/DE/TE smoke bootstrap update:
  `scripts/stata/ggcp10_mean_overall_bootstrap_iede_te.do`
- Wet-state mirror:
  `scripts/stata/ggcp10_wet_mirror_run_all.do`
- Dry-state top-3:
  `scripts/stata/ggcp10_dry_top3_ext_run_all.do`
- Figures for all three branches:
  `scripts/R/ggcp10_mediation_extensions_make_figures.R`
- Markdown-to-Feishu renderer:
  `scripts/python/render_markdown_feishu_doc.py`

## Verification snapshot

- `mean`: 21 figures; 120 baseline rows; 216 bootstrap rows; 960 heterogeneity coefficient rows; 384 heterogeneity effect rows.
- `wet_mirror`: 12 figures; 330 baseline rows.
- `dry_top3`: 21 figures; 3 selection rows; 45 baseline rows; 54 bootstrap rows; 360 heterogeneity coefficient rows; 144 heterogeneity effect rows.
- Checked logs end with `COMPLETE`:
  - `mean/logs/ggcp10_mean_ext_run_all.log`
  - `mean/logs/ggcp10_mean_overall_bootstrap_iede_te.log`
  - `wet_mirror/logs/ggcp10_wet_mirror_run_all.log`
  - `dry_top3/logs/ggcp10_dry_top3_ext_run_all.log`

## Notes

- The `SM mean` bootstrap CSV keeps the historical `ggcp10_mean_bootstrap_iede.csv` file name, but the `effect` column now includes `IE`, `DE`, and `TE`.
- Baseline plots mark `p < 0.05` coefficients with filled points and non-significant coefficients with hollow points.
- Bootstrap plots mark intervals excluding zero with filled points and intervals crossing zero with hollow points.
- Heterogeneity effect CSVs do not include standard errors or intervals, so heterogeneity effect plots are shown with hollow points.
