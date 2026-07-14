---
layout: default
title: 2026 年版本地图
---

# 2026 年版本地图

> 本页由 `scripts/python/version_lineage.py build-docs` 生成。Git 前版本是证据重建结果，不等同于可 checkout 的历史提交。

## 研究设计

| Canonical ID | 日期 | 状态 | 当前角色 | 主要改变 | 当前用途 | 证据等级 |
|---|---|---|---|---|---|---|
| design-2026-02 | 2026-02-10 | design_only | design_reference | Recorded the pre-analysis research blueprint without treating it as an implemented method | Historical design context | three-source-confirmed |

## 数据

| Canonical ID | 日期 | 状态 | 当前角色 | 主要改变 | 当前用途 | 证据等级 |
|---|---|---|---|---|---|---|
| data-v1 | 2026-03-12 | reference | historical_data_reference | Registered the 69038-row V1 grid-year family and its physical variants | Reference data base | three-source-confirmed |
| data-v1-county-city | 2026-03-22 | historical | historical_data_component | Added county and city identifiers through coordinate-to-polygon matching | Input to the locked Phase 0 panel | three-source-confirmed |
| data-v1-locked-panel | 2026-03-22 | historical | historical_analysis_input | Locked the main estimation sample and generated county or city FE identifiers | Input to late report-line and V2 build work | three-source-confirmed |
| data-v2 | 2026-03-29 | historical | historical_data_family | Built multi-window and multi-source climate inputs; SPEI extraction was corrected on 2026-04-04 | Historical data family | three-source-confirmed |
| data-v2-main-pre-spei-fix | 2026-03-29 | missing_snapshot | historical_missing_input | Produced the 69038-row and 523-column V2 main panel used by analysis-v2 | Unavailable historical input snapshot | missing-snapshot |
| data-v2-analysis-ready | 2026-04-02 | historical | historical_analysis_input | Constructed drought and wetness windows, interactions, controls and a locked V2 analysis sample | Reproducible evidence for analysis-v2 conditional on the missing upstream snapshot | three-source-confirmed |
| data-v2-main-post-spei-fix | 2026-04-04 | missing_snapshot | historical_missing_input | Corrected endpoint SPEI extraction and expanded the panel to 621 columns for the V3 systematic rerun | Unavailable corrected historical input snapshot | missing-snapshot |
| data-v3-expanded | 2026-04-07 | current_data_base | current_shared_data | Added capped GDD; retained and expanded multi-source soil-moisture-threshold hot-dry; separately added precipitation-threshold hot-dry; stabilized Stata aliases | Current shared climate and state data family | three-source-confirmed |
| data-v3-main | 2026-04-23 | reference | current_data_component | Exported the analysis main view including yield fields | Primary V3 module input | three-source-confirmed |
| data-v3-no-yield | 2026-04-23 | reference | current_data_component | Exported the yield-missing row partition while retaining the full schema | Yield-missing row partition for non-outcome data reuse | three-source-confirmed |
| data-v3-phenowindows | 2026-04-23 | reference | current_data_component | Preserved the full phenology-window table before export filtering | Local source for the V3 main and no-yield exports | three-source-confirmed |

## 报告框架

| Canonical ID | 日期 | 状态 | 当前角色 | 主要改变 | 当前用途 | 证据等级 |
|---|---|---|---|---|---|---|
| report-v1 | 2026-03-13 | historical | historical_framework | Combined Steps 1-7 baseline FE, placebo, SM attenuation, heterogeneity, DML and sensitivity | Historical framework | single-source-inferred |
| report-v2 | 2026-03-13 | superseded | historical_qa | Added Step 7B, LOPO, winsorization, nonlinear checks, leave-year-out and Oster | Historical QA | two-source-supported |
| report-v3 | 2026-03-17 | superseded | historical_framework | Reframed mechanism evidence around a-path, attenuation, bootstrap or Sobel and dose response | Historical framework only | two-source-supported |
| report-v4 | 2026-03-17 | historical | historical_compound_framework | Shifted the main framing to D by H compound stress and SR by D by H | Historical compound-stress framework | two-source-supported |
| report-v5 | 2026-03-22 | superseded | historical_framework | Locked the Phase 0 sample and added exposure frequency, support bounds, non-monotonicity and D-H corner interpretation | Historical framework | two-source-supported |
| report-v6.1 | 2026-03-23 | historical_latest | historical_report_latest | Repositioned SM as a state variable and added Mundlak, conditioning sets, irrigation and two-equation decomposition | Latest report-line framework | two-source-supported |

## 分析

| Canonical ID | 日期 | 状态 | 当前角色 | 主要改变 | 当前用途 | 证据等级 |
|---|---|---|---|---|---|---|
| analysis-v2 | 2026-04-02 | superseded | historical_diagnostic | Ran about 190 regressions and found unstable SR by D and mixed cross-source SM evidence | Historical diagnostic | three-source-confirmed |
| analysis-v3 | 2026-04-04 | historical | historical_foundation | Reran the systematic specifications after the SPEI correction and added period and bootstrap updates | Historical foundation | three-source-confirmed |
| analysis-v3-modules | 2026-04-07 | historical | historical_module_family | Added precipitation hot-dry, multi-source SM outcomes, algebraic decomposition, sample boundaries and b-path audit | Container for completed historical modules | three-source-confirmed |
| analysis-v3prhd | 2026-04-07 | historical | historical_module | Defined HotDryPr as temperature at least 32 C with daily precipitation below 1 mm and estimated yield interactions across six windows | Historical precipitation hot-dry module | three-source-confirmed |
| analysis-v3prhdsm | 2026-04-07 | historical | historical_module | Changed outcomes to six soil-moisture source and depth measures under matching interaction structures | Historical SM response module | three-source-confirmed |
| analysis-v3decomp | 2026-04-09 | historical | historical_module | Built common-sample two-equation direct and SM-associated algebraic components | Historical decomposition module | three-source-confirmed |
| analysis-v3sub | 2026-04-09 | historical | historical_module | Reran structures by irrigation group and maize region after removing W from selected specifications | Historical sample-boundary module | three-source-confirmed |
| analysis-v3med-model8 | 2026-04-16 | historical | historical_module | Estimated drought and heat mediator and yield equations across six SM measures and conditional SR levels | Historical Model 8 module | three-source-confirmed |
| analysis-v3proxy | 2026-04-16 | historical | historical_module | Compared drought proxies, HotDryPr inclusion, cut definitions, controls and six SM measures | Historical proxy audit | three-source-confirmed |
| analysis-v3bpath | 2026-04-20 | historical | historical_module | Audited timing alignment, controls, wet-side terms, nonlinearity, proxy competition, source depth and heat consistency | Historical b-path audit | three-source-confirmed |
| analysis-ggcp10-baseline-suite | 2026-05-18 | historical | historical_ggcp10_baseline | Ran paired mediator and yield equations for drought, heat and precipitation hot-dry using raw, dry-state and wet-state SM mediators | Input foundation for later GGCP10 scale work | three-source-confirmed |
| ggcp10-mediation-ext | 2026-05-19 | exploratory | exploratory_ggcp10_family | Created SM mean, wet-state mirror and dry-state top-3 branches with baseline, bootstrap and heterogeneity outputs | Completed exploratory family | three-source-confirmed |
| regional-threshold-sr-v1 | 2026-07-14 | reference | reviewed_failure_stop_data_support | Audited the official continuous maize heat-damage threshold before any yield model and stopped at the frozen five-zone coverage gate | Reviewed failure evidence only; not a submission candidate | git-native |
| compound-event-intensity-duration-override-v1 | 2026-07-15 | current_parallel | current_reviewed_event_duration_intensity_candidate | Continued the stopped smoke branch to full five-zone event, yield and soil-moisture analyses and made the triggered joint duration-intensity model the reviewed main specification | Reviewed candidate manuscript; not 95 publication-ready | git-native |
| compound-event-intensity-duration-v1 | 2026-07-15 | reference | reviewed_failure_stop_smoke_review | Designed the hot-dry event intensity-duration and soil-moisture timing interface, then stopped after the second small-smoke review retained a reproducibility Major | Reviewed failure evidence only; not a submission candidate | git-native |
| regional-threshold-sr-override-v1 | 2026-07-15 | reference | reviewed_failure_not_candidate_external_threshold | Continued past the historical coverage gate without imputing thresholds, executed the frozen external-threshold daily exposure model and retained the independent Round 2 failure decision | Reviewed failure evidence only; not a submission candidate | git-native |

## 机制

| Canonical ID | 日期 | 状态 | 当前角色 | 主要改变 | 当前用途 | 证据等级 |
|---|---|---|---|---|---|---|
| mechanism-v4smstate | 2026-04-21 | exploratory | exploratory_mechanism | Compared raw SM with pooled-local and maize-zone dry or wet state variables | Exploratory state-variable family | three-source-confirmed |
| mechanism-v5drymed | 2026-04-22 | exploratory | exploratory_mechanism | Tested drydays, dryshare and drydeficit families under baseline-local, pooled-state and maize-zone thresholds | Exploratory drought-only family | three-source-confirmed |
| mechanism-v6gleambl | 2026-04-23 | historical | historical_mechanism_precursor | Added four-window GLEAM surface and root-zone dry or wet mediator families plus heat and hot-dry variants | Historical precursor to the GGCP10 suite | three-source-confirmed |

## 种植面积

| Canonical ID | 日期 | 状态 | 当前角色 | 主要改变 | 当前用途 | 证据等级 |
|---|---|---|---|---|---|---|
| area-ggcp10-aggregated | 2026-05-18 | current_data_base | current_ggcp10_area_data | Area-preserving aggregation from the native raster grid to the 0.1-degree panel and recomputed area-weighted yield | Current GGCP10 area base | three-source-confirmed |
| area-ggcp10-harvarea | 2026-05-18 | historical | historical_area_family | Replaced area-related variables with GGCP10 harvested area while retaining original maize_frac | Container for point-sample and aggregated branches | three-source-confirmed |
| area-ggcp10-point-sample | 2026-05-18 | historical | historical_area_component | Sampled native GGCP10 harvested area at panel grid coordinates | Historical point-sample comparison branch | three-source-confirmed |

## 样本尺度

| Canonical ID | 日期 | 状态 | 当前角色 | 主要改变 | 当前用途 | 证据等级 |
|---|---|---|---|---|---|---|
| scale-b067-g195 | 2026-06-04 | reference | legacy_scale_reference | Registered the historical national B067 rule and its G195 mapping in the expanded scale enumeration | Legacy comparison reference | two-source-supported |
| scale-g049 | 2026-06-11 | reference | scale_reference | Registered the near-twin of G057 with one fewer SM quality rule | Selection reference | three-source-confirmed |
| scale-g057 | 2026-06-11 | reference | scale_reference | Ranked first in the exploratory region-first search with a region-specific hazard pattern | Selection reference | three-source-confirmed |
| scale-g185 | 2026-06-11 | current | current_analysis_scale | Retained main_sample, yield-domain, yield-jump and SM-SD rules while omitting the other optional rules | Current G185 analysis sample | three-source-confirmed |
| scale-search-region-first | 2026-06-11 | reference | scale_selection_context | Scanned 256 Gxxx rules and cluster-revalidated 208 high-score candidates under a region-first ranking | Exploratory selection context | three-source-confirmed |

## G185 方法与结果

| Canonical ID | 日期 | 状态 | 当前角色 | 主要改变 | 当前用途 | 证据等级 |
|---|---|---|---|---|---|---|
| g185-draft-bootstrap-v1 | 2026-06-20 | superseded | historical_g185_construction | Built G185-only two-equation, region, continuous irrigation and phenology results with wild-score bootstrap intervals | Historical construction logic | three-source-confirmed |
| g185-method-upgrade | 2026-06-20 | current_parallel | current_fixed_effects_and_ml_appendix | Made fixed-effect damage-avoidance margins the main evidence and retained econml, DoubleML and R grf as appendix heterogeneity concordance checks | Current parallel method entry | three-source-confirmed |
| g185-response-surface-v3 | 2026-06-21 | reviewed_sensitivity | reviewed_alternative_method | Added restricted-cubic low-degree drought-heat surfaces, spatial-block inference and explicit claim adjudication | Reviewed alternative-method sensitivity | three-source-confirmed |
| g185-old-method-corrected | 2026-06-24 | current | current_old_method_te | Recomputed regional IE, DE and TE and corrected the earlier DE-as-TE interpretation | Current truth for old-method regional TE | three-source-confirmed |
| g185-region-irrigation-boundary | 2026-06-24 | current_parallel | current_irrigation_boundary | Estimated region-specific continuous irrigation triple interactions and support-aware margins | Current separate boundary result | three-source-confirmed |
| g185-old-method-unified-v1 | 2026-07-14 | reference | reviewed_failure_stop_stability | Unified the historical linear two-equation evidence and added province-by-year fixed effects, spatial-block inference and explicit stability adjudication | Reviewed failure evidence only; not a submission candidate | git-native |
| g185-old-method-unified-override-v1 | 2026-07-15 | current_parallel | current_reviewed_g185_unified_candidate | Continued the previously stopped G185 branch under the user-authorized nonblocking stability gate and assembled the historical national, continuous regional and five-zone algebraic evidence into one reviewed candidate | Reviewed 92/100 candidate manuscript; not 95 publication-ready | git-native |
