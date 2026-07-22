# 气候与土壤水分胁迫面板 v1 运行说明

## 当前范围状态

当前正式配置的 `scope_profile` 为 `full-spei2w-dual-severity`，运行、阶段标记和质量摘要必须记录 `completion_scope_status=FULL_SCOPE`，SPEI-2W 数值计算与输出契约均为 `true`。用户于 2026-07-22 确认端点A：标签值的14日累积支持为闭区间 `[label-13,label]`，事件状态为闭区间 `[label,label+6]`。复合事件继续保留热超额与土壤水亏缺两套独立 severity，不生成混合量纲标量。配置和端点合同已经闭合不等于真实运行已经完成；正式100格点pilot及full仍未启动，当前不得声称完整v1数据产物已经生成。

## 环境与路径

提交的 YAML 不保存机器绝对路径。运行前必须在当前 PowerShell 会话提供下列八个变量，且展开结果必须为绝对路径；`CLIMATE_STRESS_OUTPUT_ROOT` 必须位于仓库或 worktree 外，并且不能是盘根、用户目录等宽泛目录。

| 环境变量 | 逻辑内容 |
|---|---|
| `CLIMATE_STRESS_MANUAL_PATH` | 冻结操作手册文件 |
| `PROJECT_DATA_ROOT` | 本项目数据根，供 V3 main 与 phenowindows 使用 |
| `ERA5_ROOT` | ERA5 小时数据及修复输入根 |
| `DAILY_TEMP_ROOT` | 逐日温度验证数据根 |
| `GLEAM_ROOT` | GLEAM 4.3a 输入根 |
| `CHM_SPEI_ROOT` | CHM SPEI 月度及 2W 文件根 |
| `PHENOLOGY_ROOT` | 中国玉米物候输入根 |
| `CLIMATE_STRESS_OUTPUT_ROOT` | 仓库外不可覆盖运行根 |

可在会话中设置这些变量，也可把路径作为参数传给无机器默认值的 [PowerShell 包装器](../scripts/powershell/run_climate_stress_panel.ps1)。变量缺失、空白、展开后为相对路径或输出根不安全时，配置加载会一次列出问题并 fail closed；不读取 `.env`，也不提交本机值。

## Python 环境与入口

使用项目隔离环境 `.venv-climate`。依赖冻结在 `data_build/requirements-climate-stress-lock.txt`，正式运行应先确认解释器和锁文件与 `_RUN.json` 中的 environment hash 一致。CLI 帮助不访问外部数据：

```powershell
& .\.venv-climate\Scripts\python.exe .\data_build\scripts\python\build_climate_stress_panel.py --help
```

只读资产预检示例；该命令不会下载 ERA5 或 GLEAM：

```powershell
& .\data_build\scripts\powershell\run_climate_stress_panel.ps1 -Stage assets -RunId preflight-001 -PilotCells 100 -HashMode pilot
```

以下pilot、full和断点续跑命令仅是后续运行示例；ERA 1980/1985/1986修复输入虽已闭合，但本轮授权不包括启动pilot，不得在本轮执行：

```powershell
# 冻结 pilot：100 cells，配置中的 pilot years
& .\data_build\scripts\powershell\run_climate_stress_panel.ps1 -Stage all -RunId pilot-001 -PilotCells 100 -HashMode pilot

# full：不传 PilotCells；年份使用完整 target
& .\data_build\scripts\powershell\run_climate_stress_panel.ps1 -Stage all -RunId full-001 -HashMode full

# 只允许同 run-id、同配置、同源码、同环境和同原始输入指纹续跑
& .\data_build\scripts\powershell\run_climate_stress_panel.ps1 -Stage all -RunId pilot-001 -PilotCells 100 -HashMode pilot -Resume
```

## 不可覆盖、并发和资源门禁

新 run 先在 `output.root` 同卷的唯一 staging 目录完成布局和 `_RUN.json`，随后原子发布最终目录。初始化中断会保留唯一 `.incomplete` 目录和失败证据；重试不会删除或覆盖旧证据。每个 run-id 使用持久 lock 文件与操作系统非阻塞文件锁；acquire、reject 和 release 分别写入不可覆盖审计 JSON。进程异常退出后由操作系统释放锁，锁文件和审计仍保留；并发 session 在初始化前直接拒绝，不能写入另一进程的 partial。

每个 stage 的 `_SUCCESS.json` 或 `_FAILED.*.json` 记录 stage 起止 current RSS、准确命名的 process-lifetime peak working set、pilot/full 预算判断、关键 block/chunk 形状和估算字节。每次 CLI invocation 另写唯一 `audit/quality_summaries/run_quality_summary.*.json`。任一 attempt 超过预算时不会发布 `_SUCCESS.json`；同 run-id 后续低 RSS `--resume` 仍继承历史最大 peak 并拒绝发布，必须使用新 run-id 重新计算。

## 当前输入门禁

截至 2026-07-22，GLEAM 2020 的 SMrz/SMs 输入、ERA 1980/1985/1986修复输入和SPEI-2W端点A均已闭合；端点不再构成`spei_2w_only`范围限制。repair与legacy ERA文件的坐标轴仅存在浮点表示差时，跨文件一致性按形状相同且`rtol=0, atol=quality.coordinate_tolerance=1e-8`判断；每个文件到目标子网格仍逐坐标执行严格`1e-8`验证。正式100格点pilot和full均尚未启动，本入口不会自行触发下载或运行。

## 2026-07-22 增量确认状态

用户已确认复合事件维持两套独立severity、不得生成混合量纲标量，并确认pilot/full进程峰值预算分别为4 GiB与16 GiB。主任务决策`decision-climate-stress-confirmations-20260722`确认：14日累积区间为`[label-13,label]`，7日状态区间为`[label,label+6]`。正式YAML已原子切换为`CONFIRMED`、`FULL_SCOPE/full-spei2w-dual-severity`与2W数值/输出开启；实现继续覆盖7日缺档、主版K=-1至少1个release、严格版K=-1.5至少3个连续release、事件/bridge审计和FULL_SCOPE输出门禁。`PARTIAL_SCOPE/PENDING_USER_DECISION`仅保留为fail-closed反例合同，不是正式运行默认值。以上配置与测试证据均不构成正式pilot完成证据。
