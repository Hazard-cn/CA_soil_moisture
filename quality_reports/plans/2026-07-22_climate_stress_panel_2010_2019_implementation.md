# 2010—2019 气候与土壤水分胁迫面板实施计划

- [x] 建立隔离工作树并完成只读输入预检
- [x] 冻结输入清单、配置、稳定网格与物候窗口
- [x] 实现分阶段可恢复CLI、运行锁和资源门禁
- [x] 实现`non2w-dual-severity`范围内的核心算法、流式聚合和导出
- [x] 完成单元测试与“合成上游合同＋生产下游完整DAG”集成测试（232项）
- [ ] 完成100格点×2010/2016/2019 pilot（`BLOCKED_INPUT`）
- [ ] 完成全量2010—2019构建与格式导出（受pilot和输入门禁阻断）
- [ ] 归档独立事实、方法和代码终审（代码/方法审查已执行，发布终审待真实pilot）
- [ ] 更新版本谱系并对实际暂存范围通过仓库政策检查

实施规范以用户于 2026-07-22 批准的 `data-climate-stress-2010-2019-v1` 方案为准；原始数据只读，所有大体量产物写入 E 盘不可覆盖运行目录，当前脏工作树不作修改。

## 2026-07-22 实施状态

- 隔离工作树与 `work/climate-stress-panel-2010-2019` 分支已经建立，基线提交为 `4868c9bc96d9ee294372b6549184c955173d0322`。
- 分阶段CLI、不可覆盖运行目录、OS级并发锁、资源预算、核心算法、空间分块聚合、Parquet/NetCDF/DTA导出及验证模块已经实现；当前合同严格限定为`PARTIAL_SCOPE/non2w-dual-severity`，不包含未经用户确认的SPEI-2W数值链。
- pilot资产门禁按设计中止。逐文件时间轴、目标区域逐值块与整文件SHA-256三重核验确认：`ERA1980_clipped.nc`与`ERA2001_clipped.nc`完全相同，`ERA1985_clipped.nc`与`ERA2002_clipped.nc`完全相同，`ERA1986_clipped.nc`与`ERA2003_clipped.nc`完全相同。真实1985和1986数据缺失，因此当前输入不能满足1981—2010完整30年温度历史期。
- V3坐标以float32存储产生的最大偏差为纬度`1.831054689e-6°`、经度`7.324218757e-6°`；仅V3入口采用`1e-5°`归位容差并保存残差，ERA原生格点匹配仍保持严格容差。
- 已建立隔离的CPython 3.12运行环境并补齐完整依赖锁。NumPy 2.4.1源码将`numpy.ndarray size changed`列为Cython harmless warning；测试配置仅精确豁免该消息，其他`RuntimeWarning`仍为错误。稳定快照由执行线程和监督线程分别完成全套测试，结果均为`232 passed`，用时分别为139.34秒和147.93秒。
- 月度SPEI、ERA/GLEAM事件、聚合、宽表、审计事件层及三种导出格式均采用空间分块、不可覆盖分区、输入/产物哈希和断点恢复；测试覆盖跨年完整事件与窗口bridge分区、损坏partial隔离、资源超限resume不可旁路及V3列投影。
- 无下载assets预检在139.6秒内按设计中止，失败检查为`assets.present`、`era5_hourly.year_continuity`和`gleam.year_continuity`；这不是正式100格点pilot，也不能替代真实数据上的stage、peak RSS、往返和resume证据。
- 输入资产仍有两类硬门禁：ERA 1985、1986历史期修复及1980 UTC+8首日边界输入证据未闭合，GLEAM 2020年SMrz/SMs缺失。任何下载均未启动。
- 独立监督对稳定代码快照给出方法91/100、工程93/100且代码层Critical/Major为0；审查时由于真实pilot、版本谱系和实际暂存范围政策证据尚缺，发布证据评分为84/100，结论为`STOP`。此后实际暂存范围政策已补验通过，但真实pilot与版本谱系仍未完成，因此发布结论不变，不得宣称完整v1或发布通过。
- 本任务39个实现、测试与文档路径暂存后，仓库政策脚本从实际index检查605个文件并解析187个Python文件，结果为`errors=0`；唯一warning来自244个既有文件保留的历史机器路径，本次没有新增绝对路径。版本谱系仍须等待真实pilot产生可登记的数据和运行证据，因此第9项保持未完成。

## 两级pilot与输出契约

- A级`non2w-dual-severity`是缩减范围pilot：在SPEI-2W时间支持语义未确认时，2W数值链和字段保持禁用；复合热—土壤水事件只保留累计热超额和累计土壤水亏缺两个独立severity，不生成混合量纲标量。该运行必须标记`PARTIAL_SCOPE`，只能用于验证非2W算法、资源和输出接口，不得称为完整`data-climate-stress-2010-2019-v1`。
- B级为完整`data-climate-stress-2010-2019-v1` pilot：双独立severity已确认并保持，不生成混合量纲标量；仍须用户确认SPEI-2W事件状态端点，随后原子更新正式scope/config/审计证据并完成真实pilot。未经端点确认，任何manifest、Material Passport或质量报告均不得标记完整v1通过。

## 2026-07-22 增量状态：端点决定仍待确认

- 用户已确认复合事件维持热超额与土壤水亏缺两套独立severity，不生成单一混合量纲severity；资源门禁确认为pilot 4 GiB、full 16 GiB。
- GLEAM 2020年SMrz/SMs输入及其来源证据已闭合。ERA 1985、1986历史期修复与1980 UTC+8首日边界的三项CDS获取任务已排队，但下载后输入校验与资产清单证据尚未闭合。
- SPEI-2W开发候选实现明确区分后向14日累积支持`[label-13,label]`与前向7日事件状态；事件状态是否采用`[label,label+6]`仍为`PENDING_USER_DECISION`，不得写成用户已确认。
- 正式YAML继续保持`PARTIAL_SCOPE/non2w-dual-severity`、`spei_2w_numeric=false`和`spei_2w_output=false`。候选`CONFIRMED/FULL_SCOPE`测试夹具只验证代码门禁，不授权正式配置、pilot或发布。
- 正式100格点×2010/2016/2019 pilot和full均未启动；发布状态继续为`STOP`，版本谱系与真实运行证据仍须在输入和端点决定闭合后完成。
