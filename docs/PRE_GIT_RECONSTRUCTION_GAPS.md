---
layout: default
title: Git 前版本重建缺口
---

# Git 前版本重建缺口

> 本页由 `scripts/python/version_lineage.py build-docs` 生成。缺口被保留为可审计状态，不用当前文件替代历史快照。

## 缺失或被覆盖的 artifact

| Artifact | 状态 | 证据等级 | 说明 |
|---|---|---|---|
| data-v2-main-initial-missing | missing | missing-snapshot | 2026-03-29 pre-SPEI-correction snapshot documented in the changelog; same-named file was overwritten and is now absent. |
| data-v2-main-corrected-missing | missing | missing-snapshot | 2026-04-04 corrected SPEI/V3pre30 snapshot documented by code and downstream scripts; no physical snapshot remains. |
| mechanism-sm-state-wide-april-missing | missing | missing-snapshot | The exact April snapshot consumed by v4/v5 is unavailable; the present same-named file was modified on 2026-05-18 and cannot substitute for it. |
| mechanism-sm-state-analysis-ready-missing | missing | missing-snapshot | Historical analysis-ready output referenced by scripts and plans but absent from the current filesystem. |
| mechanism-v6-nowet-nop30-ready-missing | missing | missing-snapshot | Historical variant referenced by code but absent from the current filesystem. |
| data-climate-stress-panel-v1-pilot-output | missing | single-source-inferred | Planned 100-grid by 2010/2016/2019 real pilot output under confirmed endpoint A; it has not been generated. Configuration confirmation and synthetic DAG tests are not substitutes for this artifact. |
| data-climate-stress-panel-v1-full-output | missing | single-source-inferred | Planned full output: 221800 grid-years in the wide panel and 1330800 grid-year-window rows in the long panel, plus NetCDF, DTA and audit layers; no full run exists. |
| data-climate-stress-panel-v1-pilot-manifest | missing | single-source-inferred | Decision_id=decision-climate-stress-confirmations-20260722 confirms endpoint A, but the real pilot manifest has not been generated; no run_id, stage-resource evidence, round-trip validation or output hashes are registered. |
| data-climate-stress-panel-v1-full-manifest | missing | single-source-inferred | The full-run manifest has not been generated and cannot be inferred from configuration or synthetic tests. |

## 不能解释为同期可复现的运行

| Run | 版本 | 状态 |
|---|---|---|
| run-report-v1-20260313 | report-v1 | historical_static |
| run-report-v2-20260313 | report-v2 | historical_static |
| run-report-v3-20260317 | report-v3 | historical_static |
| run-report-v4-20260317 | report-v4 | historical_static |
| run-report-v5-20260322 | report-v5 | historical_static |
| run-report-v6.1-20260323 | report-v6.1 | historical_static |
| run-data-v3-expanded-20260423 | data-v3-expanded | historical_static |
| run-analysis-v2-20260402 | analysis-v2 | blocked_upstream_snapshot |
| run-analysis-v3-20260404 | analysis-v3 | blocked_upstream_snapshot |
| run-analysis-v3prhd-20260407 | analysis-v3prhd | reconstructed_executable |
| run-analysis-v3prhdsm-20260407 | analysis-v3prhdsm | reconstructed_executable |
| run-analysis-v3decomp-20260409 | analysis-v3decomp | reconstructed_executable |
| run-analysis-v3sub-20260409 | analysis-v3sub | reconstructed_executable |
| run-analysis-v3med-model8-20260416 | analysis-v3med-model8 | reconstructed_executable |
| run-analysis-v3proxy-20260416 | analysis-v3proxy | reconstructed_executable |
| run-analysis-v3bpath-20260420 | analysis-v3bpath | reconstructed_executable |
| run-mechanism-v4smstate-20260421 | mechanism-v4smstate | reconstructed_executable |
| run-mechanism-v5drymed-20260422 | mechanism-v5drymed | reconstructed_executable |
| run-mechanism-v6gleambl-20260423 | mechanism-v6gleambl | reconstructed_executable |
| run-area-ggcp10-point-20260518 | area-ggcp10-point-sample | reconstructed_executable |
| run-area-ggcp10-aggregated-20260518 | area-ggcp10-aggregated | historical_static |
| run-analysis-ggcp10-baseline-suite-20260518 | analysis-ggcp10-baseline-suite | reconstructed_executable |
| run-ggcp10-mediation-ext-20260519 | ggcp10-mediation-ext | reconstructed_executable |
| run-scale-region-first-20260611 | scale-search-region-first | reconstructed_executable |
| run-g185-draft-bootstrap-v1-20260620 | g185-draft-bootstrap-v1 | verified_superseded_interpretation |
| run-data-climate-stress-panel-v1-pilot-planned-20260722 | data-climate-stress-2010-2019-v1 | planned_not_run |
| run-data-climate-stress-panel-v1-pilot-fullscope-a-auditfix-20260723T000001 | data-climate-stress-2010-2019-v1 | failed_quality_gate |
| run-data-climate-stress-panel-v1-pilot-fullscope-a-aggfix-20260723T054913 | data-climate-stress-2010-2019-v1 | failed_quality_gate |
| run-data-climate-stress-panel-v1-pilot-fullscope-a-exportfix-20260723T112218Z | data-climate-stress-2010-2019-v1 | failed_quality_gate |

## 解释规则

- 2026-07-13 以前没有 commit 级历史；文件时间只表示当前观察到的时间。
- 历史报告使用的共享结果文件可能被后续运行覆盖，重新渲染不等于恢复原始报告。
- `three-source-confirmed` 只表示至少三类证据一致，不表示历史环境和输入快照仍可完整复现。
- response-surface 与 old-method 使用不同估计量、固定效应和函数形式，不能解释为相互验证。

## 当前节点中的低置信度项

- `report-v1`：The v1 label is inferred from the later report sequence
- `data-v2-main-pre-spei-fix`：The former local data_build/data/processed/data_v2_main.dta is missing and cannot be substituted by a later file
- `data-v2-main-post-spei-fix`：The same historical path named data_v2_main.dta referred to a structurally different file
- `data-climate-stress-2010-2019-v1`：The physical run pilot-fullscope-a-auditfix-20260723T000001 reached aggregate and failed the event-audit quality gate. The physical run pilot-fullscope-a-aggfix-20260723T054913 fixed aggregate, reached export, and failed the export metadata quality gate. The physical run pilot-fullscope-a-exportfix-20260723T112218Z fixed export metadata and completed the full numeric validation logic, but its validate process exceeded the frozen 4 GiB budget and published no validate SUCCESS. Partial validation PASS is not a result manifest. All three physical runs are non-publishable; the separate replacement pilot remains planned_not_run.
