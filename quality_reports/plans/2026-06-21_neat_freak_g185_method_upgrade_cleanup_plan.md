# 2026-06-21 neat-freak cleanup plan

## Scope

Synchronize project-level documentation after the 2026-06-20 G185 method-upgrade report run. This cleanup is documentation-only and does not delete files or rerun empirical models.

## Source artifacts checked

- `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/report.md`
- `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/report.html`
- `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/run_manifest.csv`
- `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/figures/`
- `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/tables/`
- `scripts/python/build_g185_method_upgrade_report.py`
- `scripts/env/g185_ml_env.ps1`
- `requirements-ml.txt`

## Actions

1. Add a handoff note for the G185 method-upgrade report.
2. Add a concise current-status pointer to `AGENTS.md` and `CLAUDE.md`.
3. Add a project-memory entry in root `MEMORY.md` for the report entry point and environment.
4. Verify that the report, six figures, thirteen tables, and manifest still exist.

## Non-actions

- No deletion of logs, temporary directories, figures, tables, or intermediate outputs.
- No change to statistical estimates.
- No update to global Codex memory.
