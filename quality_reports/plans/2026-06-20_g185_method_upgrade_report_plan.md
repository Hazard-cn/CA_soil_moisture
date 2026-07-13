# 2026-06-20 G185 method upgrade report plan

## Objective

Configure Python and R ML dependencies, then generate a G185-only method-upgrade report with embedded figures, tables, logs, review notes, and machine-readable outputs.

## Environment choices

- Python ML environment: `.venv-ml` using Python 3.12.
- R execution: project wrapper with absolute `Rscript.exe` path.
- Scale: G185 only.
- Report output: `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/`.

## Required outputs

- `report.md`
- `report.html`
- `figures/`
- `tables/`
- `logs/`
- `review/`
- `run_manifest.csv`

## Quality gates

- Existing G185 draft directory must not be overwritten.
- Report must embed all core figures.
- Core claims must trace back to `tables/*.csv`.
- ML output must be framed as heterogeneity concordance, not causal identification.
- Report text must not use prohibited causal language.
