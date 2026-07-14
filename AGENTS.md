# AGENTS.md -- SR Buffering Effect on Maize Yield

**Project:** Straw Return (SR) Buffering of Compound Extreme Yield Losses in Chinese Maize
**Languages:** Stata (primary), R/Python (auxiliary)
**Data:** Grid-year panel (0.1 deg, 2016-2019, N=69,038)

---

## Core Principles

- **Plan first** -- enter plan mode before non-trivial tasks; save plans to `quality_reports/plans/`
- **Verify after** -- run scripts and confirm output at the end of every task
- **[LEARN] tags** -- when corrected, save `[LEARN:category] wrong -> right` to MEMORY.md
- **Quality gates** -- nothing ships below 80/100
- **Chinese docs, English code** -- documentation/logs in Chinese, code/variables in English

---

## Folder Structure

```
regression_SR/
├── README.md                    # Human-facing project entry
├── AGENTS.md                    # This file
├── MEMORY.md                    # Persistent learnings
├── .AGENT/                      # Rules, skills, agents, hooks
├── docs/                        # DATA_SOURCES.md, VARIABLES.md
├── data/processed/              # Analysis-ready CSV
├── scripts/stata/               # .do files (primary)
├── scripts/R/                   # .R files (auxiliary)
├── scripts/python/              # .py files (DML etc.)
├── output/tables/               # Regression tables
├── output/figures/              # Publication-quality figures
├── output/logs/                 # Stata .log files
├── explorations/                # Research sandbox (60/100 threshold)
├── quality_reports/             # Plans, session logs, specs
├── references/code/             # Reference code
└── templates/                   # Session log, quality report templates
```

---

## Commands

```bash
# Stata (batch mode) -- Windows path
"C:/Sofewares/Stata/Stata18/StataMP-64.exe" /e do scripts/stata/filename.do

# R
Rscript scripts/R/filename.R

# Python
python scripts/python/filename.py
```

---

## Quality Thresholds

| Score | Gate | Meaning |
|-------|------|---------|
| 80 | Commit | Good enough to save |
| 90 | PR | Ready for review |
| 95 | Excellence | Publication-ready |

---

## Skills Quick Reference

| Command | What It Does |
|---------|-------------|
| `/data-analysis [task]` | End-to-end Stata+R analysis |
| `/review-stata [file]` | Stata code quality review |
| `/review-r [file]` | R code quality review |
| `/review-paper [file]` | Manuscript review |
| `/research-ideation [topic]` | Research question generation |
| `/lit-review [topic]` | Literature search + synthesis |
| `/context-status` | Show session health |
| `/deep-audit` | Repository consistency audit |
| `/commit [msg]` | Stage + commit (when git enabled) |

---

## Non-Negotiables

- Panel structure: `xtset grid_id year` (Stata) / keyed by `grid_id`, `year`
- Clustering: `vce(cluster grid_id)` default; two-way optional
- Seeds: `set seed 42` (Stata), `set.seed(42)` (R) at file top
- Figures: white bg, 300 DPI, width 12 height 5 (adjustable), sans-serif font
- 删除操作：任何删除文件、目录、输出、日志、计划或中间产物的操作，都必须先获得用户明确允许
- Paths: Stata `global` macros, R `here::here()` or relative paths
- Tolerance: point estimates < 0.01, SE < 0.05, p-values same significance level

---

## Git and GitHub Automation

- Default authorization: after an in-scope change passes verification, the agent may automatically create a work branch, commit, push, open and merge a pull request, and create an approved research tag or release without requesting a second confirmation.
- Stable branch: `main` contains reviewed states only. Use `work/<topic>` for changes and squash-merge through a pull request after the `integrity` check passes.
- Destructive boundary: deleting files, branches or tags; rewriting history; and force-pushing still require an explicit user instruction for that specific destructive operation.
- Commit format: `type(scope): subject`, with English type/scope and a concise Chinese or English subject.
- Data boundary: never track raw data, processed data, intermediate panels, model objects, caches, logs or binary analytical outputs.
- Result boundary: publish durable results only under `docs/results/<canonical-id>/` as Markdown or self-contained HTML. Markdown is the default GitHub review format.
- Version boundary: distinguish `report-*`, `data-*`, `analysis-*`, `mechanism-*`, `area-*`, `scale-*` and `g185-*`; every version must separately document its data, method and result-presentation changes in `quality_reports/version_registry.csv` and the normalized lineage registries.
- Run boundary: never overwrite a historical run and then treat it as the same version. A changed input hash, sample rule, estimand, method or public claim requires a new artifact/run ID and an updated result manifest.
- Evidence boundary: Git-prehistory conversations are metadata evidence only. Commit thread IDs, decisions and command hashes when needed, but never raw conversations, JSONL exports or complete shell commands.
- Documentation boundary: regenerate `docs/VERSION_MAP.md`, `docs/VERSION_CHANGELOG.md`, `docs/DATA_LINEAGE.md`, `docs/CONVERSATION_EVIDENCE.md` and `docs/PRE_GIT_RECONSTRUCTION_GAPS.md` after a lineage change.
- Verification: run `python .github/scripts/check_repository_policy.py --source index`, language syntax checks and Git status/range checks before every automated push or merge.

---

## Analysis Progress (Blueprint Steps 1-8)

| Step | Description | Status | Script |
|------|-------------|--------|--------|
| 1 | Baseline FE: SR buffering interactions | DONE | `scripts/stata/step1_baseline_FE.do` |
| 2 | Placebo windows diagnostic | DONE | `scripts/stata/step2_placebo.do` |
| 3 | Mechanism I: extremes -> SM (monthly) | SKIP | (需月度数据) |
| 4 | Mechanism II: SM tails -> yield + attenuation | DONE | `scripts/stata/step4_mechanism_annual.do` |
| 5 | Boundary conditions & heterogeneity | DONE | `scripts/stata/step5_heterogeneity.do` |
| 6 | DML robustness | DONE | `scripts/python/step6_dml.py` |
| 7 | Sensitivity checks | DONE | `scripts/stata/step7_sensitivity.do` |
| 7B | Extra robustness (LOPO, Oster, winsorize) | DONE | `scripts/stata/step7b_robustness_extra.do` |
| 8 | Joint stress: SM×Heat gap | DONE | `scripts/stata/step8_joint_stress.do` |
| 8a | Boundary: FE gradient, lead, support | DONE | `scripts/stata/step8a_boundary.do` |
| 8b | Specification curve (72 specs) | DONE | `scripts/stata/step8b_spec_curve.do` |
| -- | Compound interaction (D×H, SR×D×H) | DONE | `scripts/stata/step_compound_interaction.do` |

---

## Current Data Assets and Merge Guardrails (verified 2026-07-14)

- Required first read: `docs/DATA_ASSET_INVENTORY.md`; it records current source assets, physical panels, hashes, schema boundaries, missing snapshots and reproducible checks. Version-level lineage remains in `docs/DATA_LINEAGE.md` and `quality_reports/lineage/*.csv`.
- Historical V1: `external://CA_mechanism/data/master/data_v1_with_climate.csv`, reachable from this workspace as `../data/master/data_v1_with_climate.csv`; 69,038 rows × 143 columns, 22,180 grids, 2016-2019, GB18030 encoding. `data/processed/analysis_main_sample.dta` is the 69,038 × 181 V1 locked panel; its `main_sample=1` support is 61,795 rows and 17,832 grids.
- Current shared climate/state base: `data_build/data/processed/data_v3_main.parquet` for Python/R and `data_v3_main.dta` for Stata; both represent 69,038 grid-years × 1,679 logical fields. `data_v3_phenowindows` is the 122,533-row coverage view; `data_v3_noyield.parquet` contains 53,495 yield-missing rows and is not an outcome-regression sample.
- Current G185 is a virtual sample, not a standalone panel file. Rebuild it with `scripts/python/g185_v3_data.py::load_g185_sample()` from `temp/2026-05-18_ggcp10_harvarea_agg_baseline_suite/ggcp10_baseline_suite_analysis_ready.dta` plus `data_build/data/processed/data_v3_main.dta`; `assert_g185()` must recover 46,299 rows and 13,236 grids.
- Frozen G185 rule: `ggcp10_maize_frac >= 0.05` plus `main_sample`, `yield_domain`, `yield_jump`, and `sm_sd`; `zone_core`, `sm_coverage`, `sr_within`, `years_ge3`, and `stable_province` are off. A changed rule vector, count or input hash requires a new scale/artifact/run ID.
- V1/V1-locked and V2/V3/GGCP10 use different numeric `grid_id` namespaces. Never merge across these families on `grid_id year`; use `round(latitude*10)`, `round(longitude*10)`, and `year`, or a verified one-to-one crosswalk. Within V2/V3/GGCP10, `grid_id year` is unique and compatible.
- `prov_year` is a branch-specific generated group ID. Recompute it from stable province identifiers and `year`; never use the raw integer `prov_year` as a cross-branch merge key.
- V1/V3 and GGCP10 use different maize-area denominators for `yield_tons_ha`. Current G185 uses `maize_prod / ggcp10_maize_area_km2 * 10`; do not mix its outcome, coefficients or descriptives with V1/V3 results.
- `main_sample` is not invariant: V1 locked has 61,795 flagged rows, analysis-v2/v3 and GGCP10 base have 62,018, several derived branches have 62,034, and G185 has 46,299 after its own rules. Always use the sample definition attached to the target canonical version and report model complete cases separately.
- Schema routing: V1 file header is authoritative for V1; `docs/VARIABLES.md` is only a partial historical dictionary. V3 Parquet/CSV uses `data_build/docs/VARIABLES_v3.md`; V3 DTA renames 592 long fields and must use `data_build/output/tables/stata_alias_map_v3.csv`; GGCP10 fields use `docs/VARIABLES_GGCP10_HARVAREA.md`.
- Variable names are schema-specific. V1 uses families such as `hdd_tmax_ge*`, `hotdays_tmax_ge*`, and `SPEI_season`; current G185 uses `hdd_ge32`, `D_full/W_full`, and V3 `hotdrydays_ge32_pr_lt1` loaded as `HotDryPr_full`. Soil-moisture-threshold hot-dry variables are different estimands.
- Raw-source machine locators are defined in `data_build/scripts/python/config.py`; upstream archives and notebook provenance are indexed in `data_build/docs/DATA_AUDIT_20260328.md`. The aligned SWSM files have verified missing/duplicate dates while the current script indexes by array position, so new date-sensitive SWSM work requires a dedicated audit or rebuild.
- Before estimation, record canonical data ID, physical path, SHA-256, row/column counts, key namespace, sample predicate and outcome definition; assert key uniqueness after loading. Data, intermediate panels, caches, logs, models and binary outputs remain outside Git.

---

## Current G185 Workstream (updated 2026-07-10)

### Corrected old-method regional IE/DE/TE redraw (2026-06-24)

- Bundle: `quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/g185_old_method_region_tiede_redraw_bundle.zip`
- Contact sheet: `quality_reports/agent_runs/2026-06-24_g185_old_method_region_tiede_redraw/figures_png/contact_sheet_corrected_old_method.png`
- Script: `scripts/python/export_g185_old_method_region_tiede_redraw.py`
- Handoff: `quality_reports/handoffs/2026-06-21_g185_method_upgrade_report_handoff.md`
- Corrected core TE contrasts: NE drought `1.85% [1.23, 2.56]`; HHH heat `3.17% [2.07, 4.26]`; HHH hot-dry `2.43% [1.04, 3.87]`.
- Estimand correction: legacy `1.50%`, `3.27%`, and `2.56%` are DE / residual-component contrasts after conditioning on contemporaneous soil moisture, not `TE = IE + DE`.
- IE/DE/TE are algebraic two-equation components, not identified causal mediation effects. Figure 4's irrigation boundary is a separate continuous triple-interaction result.

### Method-upgrade report (2026-06-20)

- Main readable entry: `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/report.html`
- Editable Markdown: `quality_reports/agent_runs/2026-06-20_g185_method_upgrade_report/report.md`
- Handoff: `quality_reports/handoffs/2026-06-21_g185_method_upgrade_report_handoff.md`
- Builder: `scripts/python/build_g185_method_upgrade_report.py`
- Environment wrapper: `scripts/env/g185_ml_env.ps1`
- Python ML environment: `.venv-ml` with Python 3.12; pinned package list in `requirements-ml.txt`
- R entry: `C:/Users/Lenovo/AppData/Local/Programs/R/bin/Rscript.exe`
- Scale rule: G185 only in this report; G057/G049 are scale-selection context and should not be mixed as evidence inside the G185 claim.
- Main framing: fixed-effect G185 damage-avoidance margins carry the substantive claim; `econml`, `DoubleML`, and R `grf` are appendix-level heterogeneity concordance checks.
- Language boundary: do not write that ML validates an adoption impact, that renamed IE/DE/TE components identify mediation, or that G185 is uniquely optimal.

---

## Historical Joint Stress Response Surface (v4, 2026-03-22)

**核心转变:** 从单通道中介 (SR→SM→yield) 转为联合胁迫响应面 (SR modifies D×H compound damage)

**论文主轴:** SR改变了作物在 D(drought)×H(heat) 联合暴露下的产量损失斜率

**三类证据:**
- Type I (Stress-Surface): D×H超加性损失存在 (-0.0003**), SM state dependence
- Type II (Modifier): SR×D×H triple = 0.0005** (32°C) → 0.0035*** (35°C), prov×yr下0.0010***
- Type III (Pathway): SR→SM改善, SR→减少hot-dry days (方向一致, 非因果分解)

**关键结果:**
- Compound SR×D×H: 4/4年份均正号显著, drop-2017仍0.0009***, lead test通过
- 单独SR×D: event-year依赖(2017), lead test失败, prov×yr下不显著 → suggestive only
- SR×Heat: 0.0011***, 3/4年份显著, lead test通过, 但spec curve符号不完全稳定

**语言纪律:**
- 禁止: causal effect, robust finding, 因果中介, a-path/b-path/Sobel
- 替代: conditional association, channel-consistent correlation structure, well-bounded association
- 历史框架说明：`docs/analysis_specification.md`

**报告:** `output/reports/complete_report_v4.Rmd` (30 slides, 7 sections)
- v4 QA Round 1已完成，发现3个致命级问题待修:
  1. SR×Heat spec curve 31/72负号显著(符号不稳定)
  2. D-H corner yield > 全样本(方向反常，需查corner定义)
  3. SM×Heat Type I证据弱(连续版n.s., P25仅10%水平)

**可复核报告:** `output/reports/complete_report_v4.Rmd`
