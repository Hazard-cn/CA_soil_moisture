# G185 workstream handoff (updated 2026-07-10)

## Superseding estimand correction

The 2026-06-24 old-method redraw supersedes the interpretation of the earlier region-specific `1.50%`, `3.27%`, and `2.56%` values. Those three values are DE / residual-component contrasts from the yield equation after conditioning on contemporaneous root-zone soil moisture; they are not TE under the old two-equation definition `TE = IE + DE`.

Current corrected regional TE contrasts at regional SR P75 versus P25 and regional hazard P90 are:

- NE drought: `1.85% [1.23, 2.56]`.
- HHH heat: `3.17% [2.07, 4.26]`.
- HHH hot-dry: `2.43% [1.04, 3.87]`.

Corrected truth locations:

- Bundle: `quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/g185_old_method_region_tiede_redraw_bundle.zip`
- Contact sheet: `quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/figures_png/contact_sheet_corrected_old_method.png`
- Core table: `quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/tables/core_three_corrected_te_results.csv`
- All 15 region-hazard components: `quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/tables/region_tiede_delta_components.csv`
- Diagnostics: `quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/diagnostics/assertions.json`
- Export script: `scripts/python/export_g185_old_method_region_tiede_redraw.py`

## Method-upgrade report truth locations

- Main readable report:
  `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/report.html`
- Editable Markdown report:
  `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/report.md`
- Run manifest:
  `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/run_manifest.csv`
- Figures:
  `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/figures/`
- Machine-readable tables:
  `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/tables/`
- Logs:
  `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/logs/`
- Review notes:
  `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/review/`

## Reproduction entry points

Corrected old-method redraw:

```powershell
& .\.venv-ml\Scripts\python.exe .\scripts\python\export_g185_old_method_region_tiede_redraw.py --reps 999 --seed 42
```

The redraw reads `temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_baseline_suite_analysis_ready.dta` and `data_build/data/processed/data_v3_main.dta`.

Method-upgrade report:

- Report builder:
  `scripts/python/build_g185_method_upgrade_report.py`
- ML environment wrapper:
  `scripts/env/g185_ml_env.ps1`
- Python package pins:
  `requirements-ml.txt`
- Existing G185 fixed-effect source run:
  `quality_reports/agent_runs/2026-06-20_g185_draft_bootstrap_v1/`

Example command:

```powershell
. scripts/env/g185_ml_env.ps1
& $env:PYTHON_ML scripts/python/build_g185_method_upgrade_report.py --bootstrap-reps 999 --seed 42
```

## Verification snapshot

Corrected old-method redraw:

- Scale: `G185`; regions: NE, HHH, NW, SW, SH; hazards: drought, heat, hot-dry.
- Sample assertions: full G185 `N=46,299`, `13,236` grids; named-region `N=44,556`.
- Fixed effects: grid and year; bootstrap cluster: grid; seed: `42`; repetitions: `999`.
- Output: 5 PNG figures, 5 SVG figures, 5 plot-data CSV files, 5 result tables, one contact sheet, diagnostics, script snapshot, and ZIP.
- `diagnostics/assertions.json` reports `overall_status = PASS` and no row-level identifiers in exported plot/result data.

Method-upgrade report:

- Scale: `G185`.
- Seed: `42`.
- Bootstrap repetitions requested: `999`.
- Python ML sample cap: `12000`.
- Python ML learner count: `econml_trees=240`.
- R `grf` learner count: `grf_trees=500`.
- Python ML interpreter: `.venv-ml/Scripts/python.exe`.
- Rscript executable: `C:/Users/Lenovo/AppData/Local/Programs/R/bin/Rscript.exe`.
- Report output: 1 Markdown report and 1 HTML report.
- Figure output: 6 PNG files.
- Table output: 13 CSV files.

## Corrected old-method figure inventory

- `fig1_core_three_buffers.png`: three corrected region-specific TE contrasts.
- `fig2_core_buffer_curves.png`: TE contrast over hazard exposure for the three core region-hazard combinations.
- `fig3_region_hazard_heatmap.png`: corrected TE contrasts for all 15 named-region combinations.
- `fig4_irrigation_boundary_heat_hotdry.png`: separate continuous-irrigation boundary result; not IE/DE/TE.
- `fig5_te_iede_delta_components.png`: IE, DE, and combined TE components for the three core combinations.

## Method-upgrade report figure inventory

- `fig1_g185_damage_avoidance_margin.png`: fixed-effect damage-avoidance margin by hazard.
- `fig2_g185_region_targeted_margin.png`: region-targeted G185 margin, centered on NE drought and HHH heat/hot-dry.
- `fig3_g185_irrigation_conditioned_margin.png`: continuous-irrigation boundary pattern.
- `fig4_g185_component_profile.png`: renamed IE/DE/TE component diagnostics.
- `fig5_g185_python_ml_concordance.png`: Python/R ML concordance summary; ML-only diagnostic.
- `fig6_g185_r_grf_heterogeneity.png`: R `grf` irrigation-bin heterogeneity; ML-only diagnostic.

## Interpretation boundaries

- Do not label `1.50%`, `3.27%`, or `2.56%` as regional TE. They are DE / residual-component values and are retained only in the component figure.
- Use `1.85%`, `3.17%`, and `2.43%` for the corrected old-method regional TE figure and text.
- IE/DE/TE are algebraic components formed from two fitted equations, not identified causal mediation effects.
- Treat the irrigation boundary as a separate continuous triple-interaction association, not as part of the IE/DE/TE decomposition.
- Use the fixed-effect G185 damage-avoidance margins for the main Results claim.
- Use renamed component diagnostics as mechanism-consistent evidence, not identified mediation evidence.
- Use `econml`, `DoubleML`, and R `grf` only as appendix-level heterogeneity concordance checks.
- Do not combine G057/G049/G185 estimates inside a single final story; if G185 is chosen, all main empirical claims should come from G185.
- Do not write that ML validates the adoption impact, that G185 is uniquely optimal, or that IE/DE/TE separate causal pathways.

## Current concise story

At the G185 scale, the old two-equation specification yields positive corrected TE contrasts for NE drought and HHH heat/hot-dry, with the DE component carrying most of each contrast and the IE component adding to NE drought but subtracting slightly from HHH heat and hot-dry. These are region-targeted fitted associations rather than causal mediation estimates. Irrigation remains a separate boundary condition, and ML outputs remain appendix-level heterogeneity concordance checks.
