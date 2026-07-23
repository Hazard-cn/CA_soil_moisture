# 2010—2019 气候与土壤水分胁迫面板实施计划

- [x] 建立隔离工作树并完成只读输入预检
- [x] 冻结输入清单、配置、稳定网格与物候窗口
- [x] 实现分阶段可恢复CLI、运行锁和资源门禁
- [x] 实现`full-spei2w-dual-severity`范围内的核心算法、流式聚合和导出，并保留`PARTIAL_SCOPE`负向门禁
- [x] 完成候选提交单元测试与“合成上游合同＋生产下游完整DAG”集成测试；当前测试结果见本计划末尾验收段
- [ ] 完成100格点×2010/2016/2019可信pilot（`NEW_RUN_REQUIRED_AFTER_EXPORT_METADATA_FIX`；两条已登记物理run均为只读`failed_quality_gate`，规范可信替代run仍为`NOT_RUN / planned_not_run`）
- [ ] 完成全量2010—2019构建与格式导出（仅受真实pilot尚未完成的门禁阻断）
- [ ] 归档独立事实、方法和代码终审（代码/方法审查已执行，发布终审待真实pilot）
- [x] 更新端点决定与版本谱系；候选提交的实际index仓库政策检查已通过

实施规范以用户于 2026-07-22 批准的 `data-climate-stress-2010-2019-v1` 方案及端点A决定为准；原始数据只读，所有大体量产物写入仓库外不可覆盖运行目录。当前export元数据修复轮只修改代码、测试、谱系和计划状态，不续跑旧候选run、不创建新run、不写外部数据。

## 2026-07-22 实施状态

- 隔离工作树与 `work/climate-stress-panel-2010-2019` 分支已经建立，监督锁定基线提交为 `26a507357b4add4e4871558f68a20594a54e247d`。
- 分阶段CLI、不可覆盖运行目录、OS级并发锁、资源预算、核心算法、空间分块聚合、Parquet/NetCDF/DTA导出及验证模块已经实现；正式合同已切换为`FULL_SCOPE/full-spei2w-dual-severity`，包含用户确认的SPEI-2W端点A数值链。
- 修复前历史快照：初始pilot资产门禁曾按设计中止。逐文件时间轴、目标区域逐值块与整文件SHA-256三重核验当时确认旧目录中的`ERA1980_clipped.nc`与`ERA2001_clipped.nc`完全相同，`ERA1985_clipped.nc`与`ERA2002_clipped.nc`完全相同，`ERA1986_clipped.nc`与`ERA2003_clipped.nc`完全相同；该段只记录修复前缺口，不代表当前repair输入状态。
- V3坐标以float32存储产生的最大偏差为纬度`1.831054689e-6°`、经度`7.324218757e-6°`；仅V3入口采用`1e-5°`归位容差并保存残差，ERA原生格点匹配仍保持严格容差。
- 已建立隔离的CPython 3.12运行环境并补齐完整依赖锁。NumPy 2.4.1源码将`numpy.ndarray size changed`列为Cython harmless warning；测试配置仅精确豁免该消息，其他`RuntimeWarning`仍为错误。代码与谱系测试只验证实现合同，不把测试结果表述为真实pilot。
- 月度SPEI、ERA/GLEAM事件、聚合、宽表、审计事件层及三种导出格式均采用空间分块、不可覆盖分区、输入/产物哈希和断点恢复；测试覆盖跨年完整事件与窗口bridge分区、损坏partial隔离、资源超限resume不可旁路及V3列投影。
- 修复前历史快照：无下载assets预检曾在139.6秒内按设计中止，失败检查为`assets.present`、`era5_hourly.year_continuity`和`gleam.year_continuity`。此段保留初始故障证据；后续repair输入与GLEAM右边界已经闭合，但任何preflight仍不能替代真实数据上的stage、peak RSS、往返和resume证据。
- GLEAM 2020年SMrz/SMs、ERA 1980/1985/1986修复输入证据和SPEI-2W端点均已闭合。inventory与逐日温度提取对repair/legacy跨文件轴采用形状相同且`rtol=0, atol=1e-8`，目标子网格逐文件严格`1e-8`门禁保持不变；旧候选run曾推进至`era_baseline`，但因初始化失败审计链缺口被判为不可续跑的失效证据，可信pilot仍未完成。
- 历史审查快照：独立监督当时对稳定代码给出方法91/100、工程93/100且代码层Critical/Major为0；由于真实pilot、版本谱系和实际暂存范围政策证据尚缺，发布证据评分为84/100，结论为`STOP`。该轮建立了独立的`planned_not_run`替代pilot并补齐正式YAML直接输入及planned lineage；后续物理run不改写这条计划记录。
- 修复前候选index快照曾得到`Checked 613 files / parsed 192 Python / warnings=1 legacy-only / errors=0`；该结果不覆盖本轮未暂存增量，不能作为当前候选提交证据。谱系登记继续明确pilot/full产物与manifest缺失；配置和输入完整不替代真实运行证据。

## 2026-07-22 候选pilot失效与审计修复STOP

- 历史候选run `pilot-fullscope-a-20260722T202653`已留下`assets`、`grid`、`phenology`、`era_daily`和`era_baseline`阶段证据，但首次错误路径调用发生在初始化失败审计边界修复前，仅有lease acquire/release而无对应失败summary。该run不回填retrospective记录、不再`--resume`、不作为可信pilot或完整v1证据。
- 该轮唯一允许的工作是修复并复核初始化、stage控制流、锁释放和审计持久化失败合同。每次已取得lease的调用须在锁内冻结run-derived质量摘要内容，release尝试后只补充逐项锁终态；成功路径的CLI响应须明确把目标summary标为`PENDING`，响应写入/flush也纳入异常和退出码合同，最终summary再向invocation唯一路径不可覆盖发布。stage已成功而release失败时必须保持stage为`COMPLETED`、把invocation标为`FAILED/LEASE_RELEASE`，不得补造stage失败产物。修复提交获监督GO后，可信pilot必须使用新唯一run-id从`assets`重新开始；规范谱系中的pilot保持`planned_not_run`，直至新run实际启动并由其自身证据更新。
- 新run的`assets`、后续各stage、validate和最终输出仍须逐阶段取得监督GO；旧候选run已完成的数值复核不能替代新run证据，也不能授权直接运行`spei`。

## 2026-07-23 第二个候选pilot在aggregate审计接口停止

- 新run `pilot-fullscope-a-auditfix-20260723T000001`使用提交`82cbbf80aa1a9280731cfaf24ba1fd4bd079f6aa`，在逐阶段监督GO下完成`assets`至`events`，并发布`aggregate`阶段产物。canonical long为100格点×3年×6窗的1800个唯一键；温度、SPEI、GLEAM、compound及hot-flash窗口字段的独立重汇未发现数值漂移，SPEI-2W字段完整，compound热超额与土壤水亏缺severity继续分列。
- `aggregate`正式审计接口未通过：3,719条GLEAM完整事件的通用`event_family`、`source_left_censored`和`source_right_censored`为空而真实值留在自动生成的`*_x/*_y`列；4,084条GLEAM bridge的`layer`为空；通用`severity`在无逐行measure/unit的条件下同时承载ERA热浪的degree-Celsius-day、GLEAM daily P10的m3 m-3 day和GLEAM flash drought的percentile-point day。该问题不改变canonical数值，但使事件审计层不能独立解释或安全跨来源汇总，按一个发布阻断级Major处理。
- 第十次调用的aggregate handler、`_STAGE_RESULT.json`和`_SUCCESS.json`已完成发布；调用方stdout提前关闭后，最终response写入产生`BrokenPipeError`，质量摘要准确区分`stage_execution_status=COMPLETED`与`invocation_status=FAILED`、`failure_phase=RESPONSE_WRITE`、`exit_status=2`，lease正常释放。该记录原样保留，不补写stage失败、不重跑当前aggregate。
- 该轮只允许修复`soil.py`、`aggregate.py`与`pipeline.py`的审计字段合同并补永久测试：GLEAM event/bridge显式`layer`，主事件通用字段保持非空，hot-flash冲突字段改为明确前缀，所有非空`severity`逐行携带`severity_measure`和`severity_unit`，发布前禁止`*_x/*_y`残留并执行source-specific fail-closed。不得改变severity数值、事件识别、阈值、最短期数、SPEI-2W端点或compound双独立severity。
- 本run以及历史run `pilot-fullscope-a-20260722T202653`均只读保留，不覆盖、不删除、不再`--resume`。源码、测试、文档、谱系与Git政策门全部通过后，必须创建第三个唯一run-id，从`assets`逐阶段重做；在其`validate`和最终输出门通过前，可信pilot与full均保持未完成。

## 2026-07-23 第三个候选pilot在export元数据质量门停止

- 新run `pilot-fullscope-a-aggfix-20260723T054913`使用提交`46800627b7bab0e94a96eaff524c450cf98916e9`，在逐阶段监督GO下从`assets`执行至`export`。上一run暴露的aggregate审计接口Major已经由该run真实关闭；canonical long、事件审计量纲和compound双独立severity合同通过阶段门。
- export阶段发布了12项候选bundle产物，但最终质量门发现两个Major：`era5u8_tmax_coverage`、`era5u8_tmin_coverage`、`era5u8_tmax_p90_coverage`和`era5u8_tmin_p90_coverage`在变量字典及NetCDF中被误标为`degree_Celsius`而非无量纲`1`；`manifest.json`、`material_passport.json`和`output_contract.json`没有共同且自包含的六字段`run_identity`，因而不能脱离运行目录证明run、Git提交、source tree、effective config和environment身份。
- export进程的峰值RSS为`4,287,688,704`字节，未超过冻结的4 GiB门槛，但只余`7,278,592`字节（约6.94 MiB），登记为高风险资源观察项；不提高预算、不把余量表述为充足，替代pilot必须重新实测。
- 该物理run登记为`failed_quality_gate`，`result_manifest`、`public_result`和`run_completed_at`保持空；export `_SUCCESS`只表示stage发布完成，不是最终result manifest或可发布结果。该run只读保留、不补写、不覆盖、不再`--resume`，并且不得运行`validate`。
- 当前仅修复coverage单位推断、统一`run_identity`传递与validate交叉核对，并补测试和谱系。源码变化后，可信替代pilot必须等待新的监督GO并使用新唯一run-id从`assets`重新执行；独立的规范替代pilot继续保持`planned_not_run`，full仅受该替代pilot尚未通过的门禁阻断。

## 两级pilot与输出契约

- A级`non2w-dual-severity/PARTIAL_SCOPE`现仅保留为负向兼容和fail-closed测试合同：2W数值链和字段禁用，不能作为正式配置，也不能替代完整pilot。
- B级`full-spei2w-dual-severity/FULL_SCOPE`是正式`data-climate-stress-2010-2019-v1`合同：双独立severity保持不变，SPEI-2W采用端点A。只有真实pilot完成且输入、资源、往返、审计和manifest门禁全部通过后，才能声明完整v1运行通过。

## 2026-07-22 增量状态：端点A已确认

- 用户已确认复合事件维持热超额与土壤水亏缺两套独立severity，不生成单一混合量纲severity；资源门禁确认为pilot 4 GiB、full 16 GiB。
- GLEAM 2020年SMrz/SMs及ERA 1980/1985/1986修复输入与来源证据均已闭合。
- 用户在主任务中选择端点A，并由`decision-climate-stress-confirmations-20260722`统一登记本任务的直接确认：后向14日累积支持为`[label-13,label]`，前向7日事件状态为`[label,label+6]`。
- 正式YAML已原子切换为`CONFIRMED/FULL_SCOPE/full-spei2w-dual-severity`，`spei_2w_numeric=true`且`spei_2w_output=true`；`PENDING_USER_DECISION/PARTIAL_SCOPE`继续由测试覆盖为反例。
- 旧候选100格点run已部分执行但证据链失效；可信正式100格点×2010/2016/2019 pilot和full均未完成。本轮继续`STOP`且不执行pilot，不得把旧阶段、输入闭合、配置确认、合成测试或谱系更新写成可信pilot完成。

## 2026-07-22 监督 Major 1/2/4 修复与验收

- [x] 将候选run状态改为`planned_not_run`，并由validator禁止该状态携带`result_manifest`、`public_result`、code Git SHA、开始时间或完成时间。
- [x] 按正式YAML补齐V3 phenowindows、CHM monthly、CHM 2W、2013—2019 daily validation和2010—2019逐年物候输入artifact ID；四个新增外部bundle均完成只读全文件SHA-256与文件头核验，未知拟合参考期保持`unknown`。
- [x] 补齐上述直接输入到pilot/full缺失输出的planned edges，并登记缺失输出到缺失manifest的planned finalization edges；所有边保持`single-source-inferred`，不表述为已执行。
- [x] 将本计划中的旧`BLOCKED_INPUT`和无下载preflight段统一标为修复前历史快照；规范可信pilot仍为`NOT_RUN / planned_not_run`，物理旧候选run另标为不可续跑失效证据，full仅等待新run可信pilot通过。
- [x] 完成完整测试`281 passed, 5 subtests passed`、strict validator `673 rows/errors=0`、生成文档一致性与cached diff检查；当前30文件index政策为`Checked 614 / parsed 192 Python / warning 1 legacy-only / errors 0`，仍须监督线程独立复核后才能解除`STOP`。
