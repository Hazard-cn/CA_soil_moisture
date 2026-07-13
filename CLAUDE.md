# CLAUDE.MD -- SR Buffering Effect on Maize Yield

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
├── CLAUDE.md                    # This file
├── MEMORY.md                    # Persistent learnings
├── .claude/                     # Rules, skills, agents, hooks
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
- Paths: Stata `global` macros, R `here::here()` or relative paths
- Tolerance: point estimates < 0.01, SE < 0.05, p-values same significance level
- **Beamer报告:** 每页results前面**必须**配上对应的回归方程（LaTeX公式）
- **分支隔离:** 不得把 D×H 响应面分支与旧 G185 两方程 IE/DE/TE 结果合并成同一个估计量或图表。
- **Beamer报告多放图:** 结果展示以系数图和条件效应图为主，表格仅作 backup

---

## Analysis Progress

### V1 (Blueprint Steps 1-8) — COMPLETED

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

### V2 (新数据, 3SM源×5窗口×4规格) — IN PROGRESS

| Step | Description | Status | Script |
|------|-------------|--------|--------|
| 0 | 数据准备: 变量构造、交乘项、样本锁定 | DONE | `scripts/stata/v2_step0_preamble.do` |
| 1 | 全生育期四规格×三SM源 (v1→v2桥接) | DONE | `scripts/stata/v2_step1_baseline_fullseason.do` |
| 2 | 分时期效应: 单窗口+赛马回归 | DONE | `scripts/stata/v2_step2_stage_reduced_form.do` |
| 3 | SM数据源稳健性: 衰减/a-path/状态依赖 | DONE | `scripts/stata/v2_step3_sm_source_comparison.do` |
| 4 | 四规格×三SM×五窗口完整矩阵 | DONE | `scripts/stata/v2_step4_interaction_grid.do` |
| 5 | 跨时期机制: 前期D→后期SM→产量 | DONE | `scripts/stata/v2_step5_biological_ordering.do` |
| 6 | 正式中介: Baron-Kenny+bootstrap, 3源 | DONE | `scripts/stata/v2_step6_mediation.do` |
| 7 | 稳健性: FE/聚类/阈值+一致性矩阵 | DONE | `scripts/stata/v2_step7_robustness.do` |

---

## Key Data Reference

### V1 Dataset (legacy)
- Dataset: `C:/YangSu/00_Project/CA_mechanism/data/master/data_v1_with_climate.csv` (69,038 rows, 143 cols; shared external path)

### V2 Analysis-ready Dataset
- Analysis-ready: `data/processed/v2_analysis_ready.dta` (present)
- Historical upstream path `data_build/data/processed/data_v2_main.dta` is not present in the current workspace.
- Outcome: `yield_tons_ha`, `ln_yield`
- SR lever: `ca` (adoption ratio 0-1, ≡ `ca_ratio`)
- Heat: `hdd_ge32` + window suffixes (`_v3pm10`, `_hepm10`, `_v3he`, `_hema`)
- Drought: constructed from SPEI (`spei6_mean`→full, `spei1_mean`→±10, `spei2_mean`→between)
- SM sources: GLEAM (`gleam_smrz_mean`), SWSM (`swsm_l3_mean`), ERA5-Land (`era5l_swvl3_mean`)
- Controls: `irr_frac`, `pr_sum`, `et0_sum`, `aridity`, `gdd_ge10` + window versions
- FE keys: `grid_id`, `year`, `prov_year`
- Variable dictionary: `data_build/docs/VARIABLES_v2.md` (523 vars)

---

## V2 Four Core Specifications (两条路径, 逐步叠加)

**核心研究问题:**
- **路径1 (直接):** D/H → Yield Loss, SR缓解多少？
- **路径2 (SM通道):** D/H → SM → Yield Loss, SR缓解多少？

| Spec | 公式 (简写) | 回答的问题 |
|------|------------|-----------|
| (1) | Y = D + H + SR + **SR·D + SR·H** + Z + FE | SR是否缓冲D/H直接损害？ |
| (2) | (1) + **D·H + SR·D·H** | D×H是否超加性？SR是否缓冲复合损害？ |
| (3) | (1) + **SM + SM·D + SM·H + SM·SR** | SM通道能解释多少SR的缓冲？ |
| (4) | (2) + **SM + SM·D + SM·H + SM·SR + SM·D·H + SM·SR·D·H** | 控制SM后，SR直接缓冲是否仍存在？ |

**衰减比较:** (1)→(3)的SR·D衰减 = SM通道份额; (2)→(4)的SR·D·H衰减 = SM对复合缓冲的解释

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
