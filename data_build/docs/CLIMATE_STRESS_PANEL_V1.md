# 气候与土壤水分胁迫面板 v1 运行说明

## 当前范围状态

当前可执行配置的 `scope_profile` 为 `non2w-dual-severity`，运行、阶段标记和质量摘要均记录 `completion_scope_status=PARTIAL_SCOPE`。该状态明确表示：SPEI-2W 数值计算与输出契约均为 `false`，复合事件只保留两套独立 severity，不代替尚未由用户确认的 2W 时间戳语义和复合 severity 处理。只有相关语义经用户确认、实现和回归验证后，才可另建 run/version 并声明完整 v1；当前运行不得标记为完整 v1。

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

pilot、full 和断点续跑示例：

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

截至 2026-07-22，正式 pilot/full 仍受以下输入或用户决定约束：ERA 1985、1986历史期修复及1980 UTC+8首日边界输入证据未闭合；GLEAM 2020两层输入未闭合；SPEI-2W时间支持和复合severity处理未获用户确认。assets阶段只把required/fatal或pipeline-scope检查作为全局阻断；`spei_2w_only`的unresolved检查保留审计并继续非2W的`PARTIAL_SCOPE`流水线。任何下载必须另行取得授权，本入口不会自动下载。
