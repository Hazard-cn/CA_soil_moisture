# 2010—2019 气候与土壤水分胁迫面板实施计划

- [x] 建立隔离工作树并完成只读输入预检
- [x] 冻结输入清单、配置、稳定网格与物候窗口
- [x] 实现分阶段可恢复CLI、运行锁和资源门禁
- [x] 实现`full-spei2w-dual-severity`范围内的核心算法、流式聚合和导出，并保留`PARTIAL_SCOPE`负向门禁
- [x] 完成候选提交单元测试与“合成上游合同＋生产下游完整DAG”集成测试；当前测试结果见本计划末尾验收段
- [ ] 完成100格点×2010/2016/2019 pilot（`NOT_RUN / planned_not_run`；输入事实已闭合，当前监督门尚未关闭且尚未启动）
- [ ] 完成全量2010—2019构建与格式导出（仅受真实pilot尚未完成的门禁阻断）
- [ ] 归档独立事实、方法和代码终审（代码/方法审查已执行，发布终审待真实pilot）
- [x] 更新端点决定与版本谱系；候选提交的实际index仓库政策检查已通过

实施规范以用户于 2026-07-22 批准的 `data-climate-stress-2010-2019-v1` 方案及端点A决定为准；原始数据只读，所有大体量产物写入仓库外不可覆盖运行目录。本轮只修改配置、代码文案、测试和谱系文档，不启动pilot、不写外部数据。

## 2026-07-22 实施状态

- 隔离工作树与 `work/climate-stress-panel-2010-2019` 分支已经建立，监督锁定基线提交为 `26a507357b4add4e4871558f68a20594a54e247d`。
- 分阶段CLI、不可覆盖运行目录、OS级并发锁、资源预算、核心算法、空间分块聚合、Parquet/NetCDF/DTA导出及验证模块已经实现；正式合同已切换为`FULL_SCOPE/full-spei2w-dual-severity`，包含用户确认的SPEI-2W端点A数值链。
- 修复前历史快照：初始pilot资产门禁曾按设计中止。逐文件时间轴、目标区域逐值块与整文件SHA-256三重核验当时确认旧目录中的`ERA1980_clipped.nc`与`ERA2001_clipped.nc`完全相同，`ERA1985_clipped.nc`与`ERA2002_clipped.nc`完全相同，`ERA1986_clipped.nc`与`ERA2003_clipped.nc`完全相同；该段只记录修复前缺口，不代表当前repair输入状态。
- V3坐标以float32存储产生的最大偏差为纬度`1.831054689e-6°`、经度`7.324218757e-6°`；仅V3入口采用`1e-5°`归位容差并保存残差，ERA原生格点匹配仍保持严格容差。
- 已建立隔离的CPython 3.12运行环境并补齐完整依赖锁。NumPy 2.4.1源码将`numpy.ndarray size changed`列为Cython harmless warning；测试配置仅精确豁免该消息，其他`RuntimeWarning`仍为错误。代码与谱系测试只验证实现合同，不把测试结果表述为真实pilot。
- 月度SPEI、ERA/GLEAM事件、聚合、宽表、审计事件层及三种导出格式均采用空间分块、不可覆盖分区、输入/产物哈希和断点恢复；测试覆盖跨年完整事件与窗口bridge分区、损坏partial隔离、资源超限resume不可旁路及V3列投影。
- 修复前历史快照：无下载assets预检曾在139.6秒内按设计中止，失败检查为`assets.present`、`era5_hourly.year_continuity`和`gleam.year_continuity`。此段保留初始故障证据；后续repair输入与GLEAM右边界已经闭合，但任何preflight仍不能替代真实数据上的stage、peak RSS、往返和resume证据。
- GLEAM 2020年SMrz/SMs、ERA 1980/1985/1986修复输入证据和SPEI-2W端点均已闭合。inventory与逐日温度提取对repair/legacy跨文件轴采用形状相同且`rtol=0, atol=1e-8`，目标子网格逐文件严格`1e-8`门禁保持不变；当前监督门尚未关闭，因此pilot尚未启动。
- 独立监督对稳定代码快照给出方法91/100、工程93/100且代码层Critical/Major为0；审查时由于真实pilot、版本谱系和实际暂存范围政策证据尚缺，发布证据评分为84/100，结论为`STOP`。本轮已把候选run改为`planned_not_run`并补齐正式YAML直接输入及planned lineage；真实pilot仍未完成，因此发布结论不变，不得宣称完整v1或发布通过。
- 修复前候选index快照曾得到`Checked 613 files / parsed 192 Python / warnings=1 legacy-only / errors=0`；该结果不覆盖本轮未暂存增量，不能作为当前候选提交证据。谱系登记继续明确pilot/full产物与manifest缺失；配置和输入完整不替代真实运行证据。

## 两级pilot与输出契约

- A级`non2w-dual-severity/PARTIAL_SCOPE`现仅保留为负向兼容和fail-closed测试合同：2W数值链和字段禁用，不能作为正式配置，也不能替代完整pilot。
- B级`full-spei2w-dual-severity/FULL_SCOPE`是正式`data-climate-stress-2010-2019-v1`合同：双独立severity保持不变，SPEI-2W采用端点A。只有真实pilot完成且输入、资源、往返、审计和manifest门禁全部通过后，才能声明完整v1运行通过。

## 2026-07-22 增量状态：端点A已确认

- 用户已确认复合事件维持热超额与土壤水亏缺两套独立severity，不生成单一混合量纲severity；资源门禁确认为pilot 4 GiB、full 16 GiB。
- GLEAM 2020年SMrz/SMs及ERA 1980/1985/1986修复输入与来源证据均已闭合。
- 用户在主任务中选择端点A，并由`decision-climate-stress-confirmations-20260722`统一登记本任务的直接确认：后向14日累积支持为`[label-13,label]`，前向7日事件状态为`[label,label+6]`。
- 正式YAML已原子切换为`CONFIRMED/FULL_SCOPE/full-spei2w-dual-severity`，`spei_2w_numeric=true`且`spei_2w_output=true`；`PENDING_USER_DECISION/PARTIAL_SCOPE`继续由测试覆盖为反例。
- 正式100格点×2010/2016/2019 pilot和full均未启动；本轮继续`STOP`且不执行pilot，不得把输入闭合、配置确认、合成测试或谱系更新写成pilot完成。

## 2026-07-22 监督 Major 1/2/4 修复与验收

- [x] 将候选run状态改为`planned_not_run`，并由validator禁止该状态携带`result_manifest`、`public_result`、code Git SHA、开始时间或完成时间。
- [x] 按正式YAML补齐V3 phenowindows、CHM monthly、CHM 2W、2013—2019 daily validation和2010—2019逐年物候输入artifact ID；四个新增外部bundle均完成只读全文件SHA-256与文件头核验，未知拟合参考期保持`unknown`。
- [x] 补齐上述直接输入到pilot/full缺失输出的planned edges，并登记缺失输出到缺失manifest的planned finalization edges；所有边保持`single-source-inferred`，不表述为已执行。
- [x] 将本计划中的旧`BLOCKED_INPUT`和无下载preflight段统一标为修复前历史快照；当前pilot为`NOT_RUN / planned_not_run`，full仅等待真实pilot通过。
- [x] 完成完整测试`281 passed, 5 subtests passed`、strict validator `673 rows/errors=0`、生成文档一致性与cached diff检查；当前30文件index政策为`Checked 614 / parsed 192 Python / warning 1 legacy-only / errors 0`，仍须监督线程独立复核后才能解除`STOP`。
