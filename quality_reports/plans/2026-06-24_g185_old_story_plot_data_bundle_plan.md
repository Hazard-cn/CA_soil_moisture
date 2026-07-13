# G185 old-story plot data bundle plan

## Scope

本轮生成 `g185_old_story_plot_data_bundle.zip`。该包用于交付 v3 response-surface 之前的 G185 old-story 绘图数据与对应图像，不混入 `quality_reports/agent_runs/2026-06-20_g185_response_surface_v3/figure_data/`。

## Included sources

1. `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/`
   - `tables/*.csv`
   - `figures/*.png`
   - `report.md`
   - `run_manifest.csv`
2. `quality_reports/agent_runs/2026-06-20_g185_nature_style_html/`
   - `tables/*.csv`
   - `figures/*.png`
   - `report_nature_style_cn.html`
   - `report_nature_style_en.html`
   - `run_manifest.csv`
3. `quality_reports/agent_runs/2026-06-20_g185_draft_bootstrap_v1/`
   - `*.csv`
   - `figures/*.png`
   - figure-caption and bootstrap markdown files
4. `quality_reports/agent_runs/2026-06-20_scale_specific_story_pack_v2/`
   - `figures/*.png`
5. Reproducibility scripts
   - `scripts/python/build_g185_method_upgrade_report.py`
   - `scripts/python/build_g185_nature_style_html.py`
   - `scripts/python/build_g185_draft_bootstrap_v1.py`

## Verification

1. Create a manifest with relative path, size, and SHA-256 for every bundled file.
2. Build `g185_old_story_plot_data_bundle.zip` at project root.
3. Run `ZipFile.testzip()` and confirm it returns `None`.
4. Confirm the zip contains no `2026-06-20_g185_response_surface_v3/figure_data/` entries.
