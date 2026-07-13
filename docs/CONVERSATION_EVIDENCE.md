---
layout: default
title: 2026 年对话与修改证据
---

# 2026 年对话与修改证据

> 本页由 `scripts/python/version_lineage.py build-docs` 生成。只展示脱敏元数据、决策摘要和修改事件统计；原始对话与完整命令不进入仓库。

初筛发现 124 个项目相关记录；按 thread ID 去重并完成语义 disposition 后，正式登记 120 个候选，其中纳入 81 个、排除 context-only 39 个。

版本关联使用北京时间核对任务结束日期与版本 first_evidence_date；excluded 任务的 canonical_ids 为空，最终不存在早于版本首证据日期的关联。21 个纳入任务因缺少足够的版本级交叉证据而保持未映射。

修改记录从 1935 个候选操作聚合为 149 条代表事件，聚合键为 thread ID 与 operation；登记表保留代表路径、候选数、去重路径数和命令哈希，不保留完整命令。

## 覆盖统计

| 维度 | 值 | 数量 |
|---|---|---:|
| 月份 | 2026-03 | 11 |
| 月份 | 2026-04 | 18 |
| 月份 | 2026-05 | 28 |
| 月份 | 2026-06 | 56 |
| 月份 | 2026-07 | 7 |
| 来源 | legacy-user | 38 |
| 来源 | subagent | 39 |
| 来源 | user | 43 |
| disposition | included | 81 |
| disposition | excluded:context-only-reference | 39 |
| 修改事件 | add-file | 26 |
| 修改事件 | analysis-run | 30 |
| 修改事件 | delete-observed | 9 |
| 修改事件 | file-write-command | 26 |
| 修改事件 | handoff-write | 3 |
| 修改事件 | manifest-write | 1 |
| 修改事件 | plan-write | 29 |
| 修改事件 | update-file | 25 |

## 对话候选与 disposition

| Thread ID | 开始时间 | 来源 | 范围判定 | 关联版本 | 决策摘要 | 证据等级 |
|---|---|---|---|---|---|---|
| 019cb2e6-85fb-7cc1-97c0-ccf544316a6c | 2026-03-03T08:52:57.983Z | legacy-user | included:exact-project-cwd | 未映射 | 文献管理或研究检索支持；未形成分析版本节点。 | two-source-supported |
| 019cb2ed-e71a-7b73-8aae-b60202f55998 | 2026-03-03T09:01:01.597Z | legacy-user | included:exact-project-cwd | design-2026-02 | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019cf584-4269-7b42-bce6-41d6cd53ae25 | 2026-03-16T07:20:11.631Z | legacy-user | included:exact-project-cwd | 未映射 | Git/GitHub 管理、仓库结构或版本治理任务。 | two-source-supported |
| 019d157f-642e-7f01-8c7e-160d88108588 | 2026-03-22T12:22:43.507Z | legacy-user | included:exact-project-cwd | data-v1;data-v1-county-city | 数据版本构建、变量映射、样本口径或谱系核验。 | two-source-supported |
| 019d2a6f-b76f-7640-b293-854467324495 | 2026-03-26T13:57:37.782Z | legacy-user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019d3c7a-ac0c-75f2-81f0-2941bb2d5786 | 2026-03-30T02:02:45.650Z | legacy-user | included:exact-project-cwd | 未映射 | Git/GitHub 管理、仓库结构或版本治理任务。 | two-source-supported |
| 019d3c8b-a43c-7372-9817-81d9a87bdaa4 | 2026-03-30T02:21:17.761Z | legacy-user | included:exact-project-cwd | 未映射 | Git/GitHub 管理、仓库结构或版本治理任务。 | two-source-supported |
| 019d3c96-c6f0-7fe0-8bba-cb8ee97c357e | 2026-03-30T02:33:27.540Z | legacy-user | included:explicit-user-reference | 未映射 | 项目内技术任务；未发现可稳定归入既有 canonical ID 的版本决策。 | two-source-supported |
| 019d3cd7-dacc-7be1-997a-2e14a6750c27 | 2026-03-30T03:44:32.466Z | legacy-user | included:exact-project-cwd | data-v1;data-v2;report-v4 | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019d3d7b-5333-77e0-98b3-4fa969fe8633 | 2026-03-30T06:43:05.657Z | legacy-user | included:project-subdir-cwd | data-v2;report-v4 | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019d3ed4-7d77-7bb1-9165-361c1d66473f | 2026-03-30T13:00:06.396Z | legacy-user | included:project-subdir-cwd | data-v2;report-v4 | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019d65ba-d2f2-71a1-b7b5-7d287d93ba5b | 2026-04-07T02:17:15.768Z | legacy-user | included:exact-project-cwd | 未映射 | 项目支持或治理任务；未形成可按现存文件、代码或日志交叉核验的版本节点。 | two-source-supported |
| 019d6728-c6a4-7301-81a1-6de3a20491e2 | 2026-04-07T08:56:58.793Z | legacy-user | included:exact-project-cwd | data-v2 | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019d6739-944c-7c02-8430-6101e53a4e11 | 2026-04-07T09:15:20.018Z | legacy-user | included:exact-project-cwd | 未映射 | 项目内技术任务；未发现可稳定归入既有 canonical ID 的版本决策。 | two-source-supported |
| 019d6740-9170-7aa1-9f1c-b796e37ac3b1 | 2026-04-07T09:22:58.037Z | legacy-user | included:exact-project-cwd | 未映射 | 项目内技术任务；未发现可稳定归入既有 canonical ID 的版本决策。 | two-source-supported |
| 019d67f9-cc39-7e20-b71b-f6b66a5ebd06 | 2026-04-07T12:45:17.249Z | legacy-user | included:exact-project-cwd | analysis-v2;analysis-v3decomp;analysis-v3prhd;analysis-v3prhdsm;analysis-v3sub;data-v2;report-v4 | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019d6825-0ea5-7110-836c-436e25facd1c | 2026-04-07T13:32:32.298Z | legacy-user | included:exact-project-cwd | 未映射 | Git/GitHub 管理、仓库结构或版本治理任务。 | two-source-supported |
| 019d6875-ea4e-7c52-adf5-df61eb5c95d3 | 2026-04-07T15:00:51.411Z | legacy-user | included:exact-project-cwd | 未映射 | Git/GitHub 管理、仓库结构或版本治理任务。 | two-source-supported |
| 019d8c5c-9810-7a73-823c-fd614dcf92ac | 2026-04-14T14:19:31.761Z | legacy-user | included:exact-project-cwd | 未映射 | Git/GitHub 管理、仓库结构或版本治理任务。 | two-source-supported |
| 019d904f-5282-7b01-8c09-058c22579b38 | 2026-04-15T08:43:30.846Z | legacy-user | included:exact-project-cwd | analysis-v3prhd;analysis-v3prhdsm;data-v1 | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019d91d5-35b5-7462-a0aa-9e398b1327fc | 2026-04-15T15:49:22.524Z | legacy-user | included:exact-project-cwd | analysis-v3decomp;analysis-v3med-model8;analysis-v3sub | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019d935f-5035-7551-ab1b-231a44be7e61 | 2026-04-15T22:59:50.480Z | legacy-user | included:exact-project-cwd | analysis-v3med-model8;analysis-v3prhd;analysis-v3prhdsm;analysis-v3proxy | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019daaf0-516e-7060-ae50-132f60936172 | 2026-04-20T12:49:29.499Z | legacy-user | included:exact-project-cwd | analysis-v3bpath;analysis-v3decomp;analysis-v3med-model8;analysis-v3prhd;analysis-v3prhdsm;analysis-v3proxy;analysis-v3sub;mechanism-v4smstate | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019dae1f-560e-7f42-a587-fd7f1c43d622 | 2026-04-21T03:39:42.503Z | legacy-user | included:exact-project-cwd | analysis-v3bpath;analysis-v3prhd;analysis-v3prhdsm;analysis-v3proxy;data-v1;mechanism-v4smstate | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019db335-446d-7140-8445-4da55726e898 | 2026-04-22T03:21:45.857Z | legacy-user | included:exact-project-cwd | data-v1;data-v3-main;data-v3-phenowindows;mechanism-v4smstate;mechanism-v6gleambl | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019db408-ee6f-7552-be7e-206e06c45586 | 2026-04-22T07:12:57.477Z | legacy-user | included:exact-project-cwd | analysis-v3bpath;analysis-v3med-model8;analysis-v3prhd;analysis-v3prhdsm;analysis-v3sub;data-v3-main;mechanism-v4smstate;mechanism-v5drymed;mechanism-v6gleambl | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019db52b-0d8c-78f2-8615-ec811707595c | 2026-04-22T12:29:50.883Z | legacy-user | included:exact-project-cwd | 未映射 | 土壤水分变量、数据或机制设计审计。 | two-source-supported |
| 019db730-57a1-7bd1-b648-26bcceb52232 | 2026-04-22T21:54:51.967Z | legacy-user | included:exact-project-cwd | 未映射 | 项目内技术任务；未发现可稳定归入既有 canonical ID 的版本决策。 | two-source-supported |
| 019db858-951b-70b3-b532-b96eb5a8ff77 | 2026-04-23T03:18:26.365Z | legacy-user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019ded7c-98b5-7a21-a326-25aabab80ff2 | 2026-05-03T10:57:39.037Z | legacy-user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e015a-7c29-7f20-b89e-406352b678bb | 2026-05-07T07:32:47.818Z | legacy-user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e0169-7794-7092-91c9-cea50a325e56 | 2026-05-07T07:49:09.693Z | legacy-user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e0d25-35d2-79a2-b9b4-ed9a074a855d | 2026-05-09T14:30:02.962Z | legacy-user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e2752-f28c-7ea2-8d4d-568a3eb7ce1a | 2026-05-14T16:30:08.012Z | legacy-user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e2a74-4d69-7b83-a411-deb34deeaddb | 2026-05-15T07:05:25.609Z | legacy-user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e2ab2-bf93-7160-b8cb-307e3a973085 | 2026-05-15T08:13:38.067Z | legacy-user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e2b68-f17f-7b52-8ca3-a8ff4f955934 | 2026-05-15T11:32:38.399Z | legacy-user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e38da-b845-7d72-a4fc-4114074bf4a5 | 2026-05-18T02:11:58.661Z | user | included:exact-project-cwd | 未映射 | 项目内技术任务；未发现可稳定归入既有 canonical ID 的版本决策。 | two-source-supported |
| 019e38dc-de94-7243-8b9f-91fd94ac876f | 2026-05-18T02:14:19.540Z | subagent | included:exact-project-cwd | 未映射 | Git/GitHub 管理、仓库结构或版本治理任务。 | single-source-inferred |
| 019e3906-9fd5-7fb0-bd11-92feac00a2d6 | 2026-05-18T02:59:55.989Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e3914-25b3-71a0-a21e-f6784d19bc84 | 2026-05-18T03:14:42.227Z | user | included:exact-project-cwd | analysis-ggcp10-baseline-suite;analysis-v3bpath;analysis-v3med-model8;analysis-v3prhd;analysis-v3prhdsm;analysis-v3sub;area-ggcp10-aggregated;area-ggcp10-harvarea;data-v1;data-v1-county-city;data-v2;data-v3-main;ggcp10-mediation-ext;mechanism-v4smstate;mechanism-v5drymed;mechanism-v6gleambl | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019e3916-9a57-76f2-95a2-aef5a2f36c9e | 2026-05-18T03:17:23.159Z | subagent | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e391e-ba51-7061-85bf-7bec3ead27f8 | 2026-05-18T03:26:15.633Z | subagent | included:exact-project-cwd | analysis-v3med-model8;analysis-v3proxy;area-ggcp10-harvarea;data-v1;data-v1-county-city;data-v2;data-v3-main;data-v3-phenowindows;mechanism-v4smstate;mechanism-v6gleambl | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | single-source-inferred |
| 019e3aa1-9b80-7861-b2e8-44c8fa13e075 | 2026-05-18T10:28:50.177Z | subagent | included:exact-project-cwd | analysis-ggcp10-baseline-suite;area-ggcp10-aggregated;area-ggcp10-harvarea;data-v3-main;mechanism-v4smstate;mechanism-v6gleambl | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | single-source-inferred |
| 019e3b57-b745-7eb1-8d72-65c4ccb6718f | 2026-05-18T13:47:44.837Z | subagent | included:exact-project-cwd | analysis-ggcp10-baseline-suite;analysis-v2;analysis-v3bpath;analysis-v3med-model8;analysis-v3prhd;analysis-v3proxy;area-ggcp10-aggregated;area-ggcp10-harvarea;data-v1-county-city;data-v3-main;data-v3-phenowindows;mechanism-v4smstate;mechanism-v5drymed;mechanism-v6gleambl | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | single-source-inferred |
| 019e3df0-9321-7622-9863-506b7f7143e6 | 2026-05-19T01:53:57.026Z | user | included:exact-project-cwd | analysis-ggcp10-baseline-suite;analysis-v3sub;area-ggcp10-aggregated;area-ggcp10-harvarea;ggcp10-mediation-ext;mechanism-v5drymed | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019e4b4e-67b4-78a2-b62b-f2ea6f851181 | 2026-05-21T16:11:30.100Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e4d80-aa95-7f20-a920-4bec5ba666b3 | 2026-05-22T02:25:38.453Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e4e6f-9137-7070-8bc3-b4a4c7559da6 | 2026-05-22T06:46:35.064Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e4f07-52f1-73d3-ad74-8138d6d436d7 | 2026-05-22T09:32:20.593Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e5021-8f91-7123-9eba-7585001923ed | 2026-05-22T14:40:37.266Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e5a16-da49-7061-b5df-cf5ffbcfac1e | 2026-05-24T13:05:07.658Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e5a25-86ba-76d3-8578-db248bc67e32 | 2026-05-24T13:21:09.307Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e6246-dafc-7210-9b00-3ca58be36dd1 | 2026-05-26T03:14:31.293Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e64fb-91fb-7c31-ba04-7e2685a168e4 | 2026-05-26T15:51:09.052Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e6a5c-0c06-7e61-b527-33fe0c57a295 | 2026-05-27T16:54:37.831Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e796e-dae3-7681-8e8a-7c0e817dac9f | 2026-05-30T15:09:28.676Z | legacy-user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e8232-1440-7883-a5b0-886929fa2ae2 | 2026-06-01T07:59:40.609Z | user | included:exact-project-cwd | 未映射 | 项目内技术任务；未发现可稳定归入既有 canonical ID 的版本决策。 | two-source-supported |
| 019e8637-07d2-7321-a45f-c9f3895dd3fd | 2026-06-02T02:43:35.596Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019e884b-1009-7843-b711-d6012099e289 | 2026-06-02T12:24:41.226Z | user | included:project-tool-operation | area-ggcp10-harvarea;ggcp10-mediation-ext | GGCP10 harvested-area 数据构建、基线套件或样本审计。 | two-source-supported |
| 019e884d-0a81-7b71-b40f-61dd29272dbc | 2026-06-02T12:26:50.882Z | user | included:exact-project-cwd | analysis-ggcp10-baseline-suite;area-ggcp10-aggregated;area-ggcp10-harvarea;data-v1;data-v3-main;ggcp10-mediation-ext;mechanism-v5drymed;mechanism-v6gleambl;scale-b067-g195 | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019e932f-9a02-7f61-a01c-864611666049 | 2026-06-04T15:10:30.915Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019ea028-a925-71c1-8965-76cb5ca0b141 | 2026-06-07T03:37:59.846Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019ea115-91b4-7193-9aa3-dae5d5ae6db0 | 2026-06-07T07:56:45.876Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019eb245-b21e-7d10-8cdf-0034d66c5472 | 2026-06-10T16:02:52.575Z | user | included:exact-project-cwd | analysis-ggcp10-baseline-suite;analysis-v2;analysis-v3bpath;analysis-v3sub;area-ggcp10-aggregated;area-ggcp10-harvarea;area-ggcp10-point-sample;data-v1;data-v3-main;g185-draft-bootstrap-v1;g185-method-upgrade;g185-response-surface-v3;ggcp10-mediation-ext;mechanism-v4smstate;scale-b067-g195;scale-g049;scale-g057;scale-g185;scale-search-region-first | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019eb27a-8167-7f12-b75b-756c65bce6ba | 2026-06-10T17:00:33.512Z | user | included:exact-project-cwd | 未映射 | Git/GitHub 管理、仓库结构或版本治理任务。 | two-source-supported |
| 019ebace-2224-73a3-8424-546d2596e938 | 2026-06-12T07:48:51.877Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019ebcc8-03d8-7fe3-9329-dab27f7dcddf | 2026-06-12T17:01:25.337Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019ec4f1-6c11-7252-b5de-fabe6563fbba | 2026-06-14T07:03:36.722Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019ec602-f8f9-7650-ac8a-21695b4e377b | 2026-06-14T12:02:24.122Z | user | included:exact-project-cwd | area-ggcp10-harvarea;mechanism-v4smstate;scale-b067-g195;scale-g049 | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ec6c9-7802-7953-9711-33183c3dfae0 | 2026-06-14T15:39:17.785Z | user | included:project-tool-operation | 未映射 | Git/GitHub 管理、仓库结构或版本治理任务。 | two-source-supported |
| 019ecfcd-82d3-7f42-90c2-faf09525eefe | 2026-06-16T09:40:13.853Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019ed590-0ee3-7433-8498-39f71a53f946 | 2026-06-17T12:30:48.548Z | user | included:explicit-user-reference | area-ggcp10-harvarea | GGCP10 harvested-area 数据构建、基线套件或样本审计。 | two-source-supported |
| 019ed590-d668-7be3-a610-5cecb46ceee5 | 2026-06-17T12:31:39.625Z | subagent | included:linked-subagent | scale-b067-g195 | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ed590-d8d5-7713-a242-970755a9b31f | 2026-06-17T12:31:40.247Z | subagent | included:project-tool-operation | 未映射 | Git/GitHub 管理、仓库结构或版本治理任务。 | two-source-supported |
| 019ed590-db98-7db0-8f86-e0b717876b36 | 2026-06-17T12:31:40.953Z | subagent | included:linked-subagent | area-ggcp10-harvarea | GGCP10 harvested-area 数据构建、基线套件或样本审计。 | two-source-supported |
| 019ed98d-c46b-7ac0-a29c-92684069e4e7 | 2026-06-18T07:06:47.276Z | user | included:exact-project-cwd | area-ggcp10-harvarea;mechanism-v4smstate | GGCP10 harvested-area 数据构建、基线套件或样本审计。 | two-source-supported |
| 019ed9bf-6e97-7c01-a976-60970c225f8c | 2026-06-18T08:01:02.105Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019edfe8-7738-71b2-a9eb-11daad0104d2 | 2026-06-19T12:43:34.585Z | subagent | included:exact-project-cwd | area-ggcp10-harvarea | GGCP10 harvested-area 数据构建、基线套件或样本审计。 | two-source-supported |
| 019edfe8-7888-7c90-9d27-11bc9dfc85b4 | 2026-06-19T12:43:34.920Z | subagent | included:exact-project-cwd | area-ggcp10-harvarea;scale-b067-g195;scale-g057;scale-g185;scale-search-region-first | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019edfe8-7a0c-7161-ba49-3eb94df051f6 | 2026-06-19T12:43:35.309Z | subagent | included:exact-project-cwd | analysis-ggcp10-baseline-suite;area-ggcp10-aggregated;area-ggcp10-harvarea;data-v1;scale-b067-g195;scale-g057;scale-g185;scale-search-region-first | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019edfe8-7bd3-7c82-80c7-cc16dfd1ea92 | 2026-06-19T12:43:35.764Z | subagent | included:exact-project-cwd | area-ggcp10-harvarea;scale-b067-g195;scale-g049;scale-g057;scale-g185;scale-search-region-first | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee019-e031-76f2-8885-2004ba9dce4f | 2026-06-19T13:37:32.722Z | subagent | included:exact-project-cwd | scale-b067-g195;scale-g049;scale-g057;scale-g185;scale-search-region-first | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee019-e0cd-7313-891f-470d3d9f404e | 2026-06-19T13:37:32.878Z | subagent | included:exact-project-cwd | area-ggcp10-harvarea;scale-b067-g195;scale-g057;scale-g185 | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019ee019-e166-7fa2-836a-53f0c941e341 | 2026-06-19T13:37:33.031Z | subagent | included:exact-project-cwd | scale-b067-g195;scale-g049;scale-g057;scale-g185;scale-search-region-first | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee019-e2b9-7a60-81b8-388669a75ed3 | 2026-06-19T13:37:33.370Z | subagent | included:exact-project-cwd | area-ggcp10-harvarea;ggcp10-mediation-ext;scale-b067-g195;scale-g049;scale-g057;scale-g185;scale-search-region-first | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee0c7-8b6c-7a52-8b22-21c8eaa6263d | 2026-06-19T16:47:14.285Z | subagent | included:exact-project-cwd | area-ggcp10-harvarea;scale-b067-g195;scale-g049;scale-g057;scale-g185;scale-search-region-first | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee0c7-b387-7ba0-8481-218de04aa4ac | 2026-06-19T16:47:24.552Z | subagent | included:exact-project-cwd | area-ggcp10-harvarea;scale-b067-g195;scale-g057;scale-g185;scale-search-region-first | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee0c7-d2b1-7151-b884-ea0a1f7fdffd | 2026-06-19T16:47:32.529Z | subagent | included:exact-project-cwd | scale-b067-g195;scale-g057;scale-g185;scale-search-region-first | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee0c7-fa99-7f20-9adc-7662e88541c5 | 2026-06-19T16:47:42.746Z | subagent | included:exact-project-cwd | area-ggcp10-harvarea;scale-b067-g195;scale-g049;scale-g057;scale-g185;scale-search-region-first | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee0d2-6412-7ed0-88ef-ae7200eb6028 | 2026-06-19T16:59:05.107Z | subagent | included:exact-project-cwd | scale-b067-g195;scale-g057;scale-g185;scale-search-region-first | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee0d2-64c6-73c2-86f9-b994a44cb79a | 2026-06-19T16:59:05.287Z | subagent | included:exact-project-cwd | area-ggcp10-harvarea;scale-b067-g195;scale-g057;scale-g185;scale-search-region-first | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee0d2-656a-7a02-90f1-0b2f5216c78e | 2026-06-19T16:59:05.452Z | subagent | included:exact-project-cwd | scale-b067-g195;scale-g057;scale-g185 | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee0d2-6614-7f90-a784-5c92f936ed7c | 2026-06-19T16:59:05.621Z | subagent | included:exact-project-cwd | area-ggcp10-harvarea;scale-b067-g195;scale-g057;scale-g185;scale-search-region-first | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee0d2-6712-7972-9a52-1ce197fe902b | 2026-06-19T16:59:05.875Z | subagent | included:exact-project-cwd | scale-b067-g195;scale-g057;scale-g185 | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee0d2-67dc-7882-93f2-8d2a0b8b88c5 | 2026-06-19T16:59:06.078Z | subagent | included:exact-project-cwd | area-ggcp10-harvarea;scale-b067-g195;scale-g057;scale-g185;scale-search-region-first | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee0d6-5a12-73d1-8188-e36ed2c732f4 | 2026-06-19T17:03:24.691Z | subagent | included:exact-project-cwd | scale-g049 | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee0d6-5ac1-7923-b1d1-eba0374a12b0 | 2026-06-19T17:03:24.866Z | subagent | included:exact-project-cwd | area-ggcp10-harvarea;scale-search-region-first | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee0d9-fe1e-7571-a061-e7c3dde8f08e | 2026-06-19T17:07:23.296Z | subagent | included:exact-project-cwd | 未映射 | 文献管理或研究检索支持；未形成分析版本节点。 | two-source-supported |
| 019ee0d9-fef8-7282-b3e6-eac61d98d682 | 2026-06-19T17:07:23.513Z | subagent | included:exact-project-cwd | 未映射 | 文献管理或研究检索支持；未形成分析版本节点。 | two-source-supported |
| 019ee0d9-ffc5-7022-b3e1-4ffab5b03345 | 2026-06-19T17:07:23.718Z | subagent | included:exact-project-cwd | scale-search-region-first | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee0da-00a3-7e80-9043-9de25da10e7f | 2026-06-19T17:07:23.940Z | subagent | included:exact-project-cwd | area-ggcp10-harvarea | GGCP10 harvested-area 数据构建、基线套件或样本审计。 | two-source-supported |
| 019ee0df-55a5-70c3-8014-8c160af1b82c | 2026-06-19T17:13:13.381Z | subagent | included:exact-project-cwd | area-ggcp10-harvarea;scale-b067-g195;scale-g049;scale-g057;scale-g185;scale-search-region-first | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee109-bb28-7d61-bea2-6a17a6c7437b | 2026-06-19T17:59:31.881Z | subagent | included:exact-project-cwd | analysis-ggcp10-baseline-suite;area-ggcp10-aggregated;area-ggcp10-harvarea;data-v3-main;g185-draft-bootstrap-v1;scale-g057;scale-g185;scale-search-region-first | G185 draft-bootstrap 运行、结果整理或证据核验。 | two-source-supported |
| 019ee109-d730-72c3-aff7-2e0a7874273b | 2026-06-19T17:59:39.057Z | subagent | included:exact-project-cwd | area-ggcp10-harvarea;scale-g185;scale-search-region-first | GGCP10 候选尺度搜索、区域优先选择或样本规则核验。 | two-source-supported |
| 019ee112-552c-7f51-bac7-b3b3f3699185 | 2026-06-19T18:08:55.596Z | subagent | included:exact-project-cwd | area-ggcp10-harvarea;g185-draft-bootstrap-v1;scale-b067-g195;scale-g049;scale-g057;scale-g185;scale-search-region-first | G185 draft-bootstrap 运行、结果整理或证据核验。 | two-source-supported |
| 019ee20f-cb16-7af2-a99f-87c8e8fc5275 | 2026-06-19T22:45:46.391Z | user | included:exact-project-cwd | area-ggcp10-harvarea;g185-draft-bootstrap-v1;g185-method-upgrade;scale-g057;scale-g185;scale-search-region-first | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019ee3ae-01ed-7171-a5f0-535a3b57ac20 | 2026-06-20T06:18:12.334Z | user | included:exact-project-cwd | area-ggcp10-harvarea;g185-draft-bootstrap-v1;g185-method-upgrade;scale-g057;scale-g185;scale-search-region-first | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019ee65b-340f-7293-a148-7bf9fedd66c0 | 2026-06-20T18:46:37.328Z | user | included:exact-project-cwd | analysis-ggcp10-baseline-suite;area-ggcp10-aggregated;area-ggcp10-harvarea;data-v1;data-v2;data-v2-analysis-ready;data-v3-main;g185-draft-bootstrap-v1;g185-method-upgrade;g185-old-method-corrected;g185-region-irrigation-boundary;g185-response-surface-v3;ggcp10-mediation-ext;mechanism-v4smstate;report-v4;report-v6.1;scale-g049;scale-g057;scale-g185;scale-search-region-first | G185 旧方法区域 IE/DE/TE 组件的更正、重绘或证据核验。 | two-source-supported |
| 019ee8f4-bd03-7af1-8978-940fd475d485 | 2026-06-21T06:53:33.828Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019ef49f-cf2e-7dc0-9a45-ea5317f67243 | 2026-06-23T13:16:14.511Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019f0977-50b1-7c42-a550-4e6353bfba51 | 2026-06-27T14:24:02.226Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019f0ce2-581a-72b1-a76f-3fba689bded6 | 2026-06-28T06:19:48.124Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019f31f3-ad5e-7da2-af5a-bb423e9f577d | 2026-07-05T11:04:41.055Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019f3c1f-06c0-7bf2-838b-0d7784c0ccdd | 2026-07-07T10:28:14.145Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019f3c44-995e-7970-912d-7967bec9becc | 2026-07-07T11:09:16.511Z | user | excluded:context-only-reference | 未映射 | 跨项目任务仅因注入上下文或历史工具输出出现项目路径；不作为版本谱系证据。 | not-evidence |
| 019f485b-9517-76d1-a1c7-61588e44cfe5 | 2026-07-09T19:29:49.336Z | user | included:exact-project-cwd | analysis-ggcp10-baseline-suite;analysis-v2;analysis-v3;analysis-v3-modules;analysis-v3bpath;analysis-v3decomp;analysis-v3med-model8;analysis-v3prhd;analysis-v3prhdsm;analysis-v3proxy;analysis-v3sub;area-ggcp10-aggregated;area-ggcp10-harvarea;area-ggcp10-point-sample;data-v1;data-v1-county-city;data-v1-locked-panel;data-v2;data-v2-main-post-spei-fix;data-v2-main-pre-spei-fix;data-v3-expanded;data-v3-main;design-2026-02;g185-draft-bootstrap-v1;g185-method-upgrade;g185-old-method-corrected;g185-region-irrigation-boundary;g185-response-surface-v3;ggcp10-mediation-ext;mechanism-v4smstate;mechanism-v5drymed;mechanism-v6gleambl;report-v1;report-v2;report-v3;report-v4;report-v5;report-v6.1;scale-b067-g195;scale-g049;scale-g057;scale-g185;scale-search-region-first | 列示版本的项目任务或核验记录；仅保留脱敏关联，未将晚于该对话日期的版本节点回填为历史证据。 | two-source-supported |
| 019f485c-3afe-70f2-9d52-12c88ce87eaa | 2026-07-09T19:30:31.807Z | subagent | included:exact-project-cwd | analysis-v3bpath;analysis-v3med-model8;analysis-v3prhd;analysis-v3prhdsm;area-ggcp10-aggregated;area-ggcp10-harvarea;g185-old-method-corrected;mechanism-v6gleambl;scale-g185 | G185 旧方法区域 IE/DE/TE 组件的更正、重绘或证据核验。 | two-source-supported |
| 019f485c-582e-7101-9bdc-5a999b8ed87e | 2026-07-09T19:30:39.279Z | subagent | included:exact-project-cwd | analysis-ggcp10-baseline-suite;analysis-v2;analysis-v3bpath;analysis-v3decomp;analysis-v3prhd;analysis-v3prhdsm;analysis-v3proxy;analysis-v3sub;area-ggcp10-aggregated;area-ggcp10-harvarea;data-v1;data-v3-main;g185-draft-bootstrap-v1;g185-method-upgrade;g185-old-method-corrected;g185-response-surface-v3;ggcp10-mediation-ext;mechanism-v4smstate;mechanism-v5drymed;mechanism-v6gleambl;report-v2;report-v3;report-v4;report-v5;report-v6.1;scale-b067-g195;scale-g049;scale-g057;scale-g185;scale-search-region-first | G185 旧方法区域 IE/DE/TE 组件的更正、重绘或证据核验。 | two-source-supported |
| 019f485c-6db6-7d03-baeb-1aa913758407 | 2026-07-09T19:30:44.791Z | subagent | included:exact-project-cwd | analysis-ggcp10-baseline-suite;analysis-v3decomp;analysis-v3med-model8;analysis-v3prhd;analysis-v3prhdsm;area-ggcp10-aggregated;area-ggcp10-harvarea;data-v1;data-v2;data-v3-main;g185-method-upgrade;g185-old-method-corrected;g185-response-surface-v3;ggcp10-mediation-ext;scale-g185 | G185 旧方法区域 IE/DE/TE 组件的更正、重绘或证据核验。 | two-source-supported |

## 修改事件的使用边界

- `apply_patch` 或写入命令只能证明对话中发生过修改动作；只有与当前文件、日志、manifest 或结果相互核对后，才能提升为版本谱系证据。
- `command_sha256` 用于在本机原始 session 中复核同一命令，不公开命令原文。
- `path_or_artifact_id` 只使用规范化仓库 URI 或逻辑 artifact ID，不保存用户机器绝对路径。
