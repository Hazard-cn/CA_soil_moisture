# 2026-06-20 G185 Nature-style HTML enhancement plan

## Objective

Use the local Nature Geoscience supplemental-material pattern to upgrade the current
G185 method-upgrade report into two static HTML reading entries:

- English: `report_nature_style_en.html`
- Chinese: `report_nature_style_cn.html`

The new report must keep the current G185 fixed-effect margins as the main evidence,
place ML diagnostics in appendix-level robustness, and add new figures that make the
story more intuitive for a Nature Portfolio subjournal audience.

## Source report

Input report:

- `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/report.html`
- `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/tables/*.csv`
- `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/figures/*.png`

Local method reference:

- `references/code/literature_methods_2026-06-20/24137280-Nature supplemental materials/`

## New output directory

`quality_reports/agent_runs/2026-06-20_g185_nature_style_html/`

Required contents:

- `report_nature_style_en.html`
- `report_nature_style_cn.html`
- `figures/` with copied original figures and new figures
- `tables/` with copied source CSVs and new derived CSVs
- `run_manifest.csv`

## New figures

1. `fig7_g185_sr_response_gap_curve.png`
   - Nature-style response/gap plot.
   - Shows fitted P90 stress-response slope at SR P25/P50/P75.
   - Annotates the P75-minus-P25 damage-avoidance margin.

2. `fig8_g185_region_hazard_targeting_matrix.png`
   - Region-hazard targeting matrix.
   - Shows which region-hazard cells carry the interpretable signal.
   - Highlights NE drought, HHH heat, and HHH hot-dry.

3. `fig9_g185_targeting_amplification.png`
   - Compares national G185 margin with the central region-targeted margin.
   - Converts the region story into a direct targeting-gain visual.

4. `fig10_g185_support_uncertainty_panel.png`
   - Support and uncertainty panel.
   - Displays estimate, confidence interval, and grid support by region-hazard cell.

## Language discipline

Use `conditional association`, `SR-associated buffering`, `damage-avoidance margin`,
`targeted-use interpretation`, and `heterogeneity concordance`. Do not use
`causal effect`, `causal mediation`, `direct/indirect effect`, or `ML proves`.

Chinese report wording should preserve the same evidence hierarchy:

- 主文结果：fixed-effect G185 margins
- 条件边界：region and irrigation targeting
- 机制诊断：renamed component diagnostics
- 附录稳健性：ML concordance

## Verification

- Run the builder script.
- Confirm both HTML files exist.
- Confirm every `<img src="">` in each HTML points to an existing file.
- Open both HTML files in the local browser and confirm the title, main sections,
  and images load.
