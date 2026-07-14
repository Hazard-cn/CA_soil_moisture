# 热干事件强度—持续时间方向：small smoke审查STOP报告

- Canonical ID：`compound-event-intensity-duration-v1`
- 数据版本：`data-v3-main`与2016—2019年对齐逐日Tmax、降水、GLEAM SMrz
- 样本边界：40个grid-years的确定性接口smoke；未完成全量支持审计
- 运行日期：2026-07-15
- 生成入口：`scripts/python/run_hotdry_event_stage1.py`
- 可复核位置：`temp/2026-07-15_compound_event_smoke_review_stop/`
- 解释边界：`STOP_AT_SMOKE_REVIEW`；未估计产量或恢复estimand

## 摘要

本方向预先设计了“连续至少3天同时满足Tmax≥32°C且降水<1 mm”的热干事件，拟在五个玉米产区分别检验SR与事件总持续时间、平均超温强度的条件产量损害差异，并以GLEAM根区土壤水分刻画前置状态、drawdown和30日恢复。设计审查以92/100通过，但small smoke在两轮独立审查后仍有一项可复现性Major：第二轮run没有把新增runner等价测试文件登记为输入身份。冻结流程规定同一审查阶段最多两轮，Round 2仍有Major即停止。因此该方向在small smoke处终止，没有运行全量支持审计、产量模型、IPCW恢复模型或任何显著性检验，不能写成“结果不显著”。

## 冻结方法与数据边界

数据入口固定为V3主面板、2016—2019年0.1°对齐逐日Tmax、降水和GLEAM SMrz。确认性事件窗口为项目既有的扩展V3—成熟窗口，即`v3_doy-30`至`ma_doy`，不是严格播种至成熟的完整生育季。事件期暴露包括事件数、总天数、最长连续期、事件日平均超温、累计超温及热日中的干旱同期比例；无事件年份保留。SM前置状态为onset前14日至前1日均值，drawdown为前置均值减去onset至事件结束后3日内最低SM，恢复时间从事件结束日开始，至下一事件、成熟日、数据结束或30日上限右删失。

若进入完整模型，主结果原定为五区合并完全交互模型，吸收grid FE和province×year FE，控制GDD10–29、季节降水及平方项；持续时间与强度分别估计，五区×两项estimand用同步2°空间块wild-score和Romano–Wolf stepdown推断。恢复分析原定使用IPCW加权离散cloglog和30日RMST。上述内容只是通过审查的设计，不是已经执行的实证结果。

## 两轮small smoke及审查

| 轮次 | run | 已完成内容 | 审查 | 状态 |
|---|---|---|---:|---|
| Round 1 | `2026-07-15_compound_event_interface_smoke_v1` | 40个grid-years、75条event-panel记录、五区×四年、400条坐标日值抽查；38项测试 | 88/100 | `REVISE_SMOKE` |
| Round 2 | `2026-07-15_compound_event_interface_smoke_v2` | 与v1逐字段一致；23项输入身份、7项输出哈希；41项测试 | 89/100 | `STOP_AT_SMOKE_REVIEW` |

Round 1的唯一Major是run manifest只锁定14项数据输入，所登记Git提交不包含当时尚未提交的core、validator、runner、schema和设计。Round 2把14项数据和9项实现、契约、设计、审查及测试文件共23项的bytes、MD5与SHA-256写入manifest；这关闭了大部分身份缺失，但新增的两项runner索引等价测试位于第三个文件`tests/test_hotdry_event_stage1_runner.py`，该文件没有进入23项inputs。其实际SHA-256为`fe9616abd196e09d7ae8aee3fa9e15a2cc945383071aeb8e8e1301e1f97e3b55`。因此，v2能在没有锁定全部41项测试身份的情况下通过方向manifest validator，该覆盖盲点属于未关闭Major。

Round 2的`run_manifest.json` SHA-256为`724589d62bbadf0cc5b44e0a3c77f921308cd6ccec686d88668df871ea2a18b4`，`event_run_extension.json` SHA-256为`741578cbf7abd100da61622619ff213f49dd1a1626566bd1b00ef6e8749b6f0d`。独立审查记录分别为`quality_reports/plans/2026-07-15_hotdry_event_smoke_review_round1.md`和`quality_reports/plans/2026-07-15_hotdry_event_smoke_review_round2_stop.md`。

## 已通过但不能解除STOP的检查

三份测试文件的41项人工和契约测试在当前工作树中全部通过，覆盖连续三日、间断日、窗口边界、天气缺失、多事件、无热日、前置SM缺失、立即恢复、下一事件删失、成熟日删失、30日上限、跨记录聚合、run manifest语义以及point/bulk索引等价。v2的23项已登记输入双哈希和7项输出哈希逐字节一致；v1与v2解压后的75×37 event panel、40条grid-year support、400条坐标值和stage decision逐字段一致；逐行schema、跨记录validator、不可覆盖保护和`yield_model_run=false`均通过。

这些检查只证明当前接口在40个grid-years上可计算，并证明v1/v2没有因读取路径变化而改变small-smoke值；它们不能替代缺失的第三测试文件身份，也不能证明五区全量支持门槛通过。

## Stage 1与结果边界

Stage 1 v1因低效NetCDF高级点索引和实施身份不完整，在1814秒后停止，`support_audit_completed=false`；Stage 1 v2在Round 2确认身份Major后于54秒停止，同样没有完成支持表。两个目录均保留终止记录，均为`yield_model_run=false`、`claims=[]`和`not_for_inference=true`。没有区域支持数值、系数、区间、p值、恢复曲线或图表可供报告；缺少这些结果表示“未运行”，不是“估计为零”或“统计不显著”。

## 结论

方向三在方法设计上保留了产区异质性、事件强度—持续时间、前置SM、drawdown和恢复时序，但没有通过冻结的small smoke可复现性门槛。根据两轮上限，不生成v3，不补登记后继续模型，不改换阈值、事件长度、空间映射或窗口。该方向只作为可复核失败证据保存，不进入候选小稿，不形成期刊匹配或实证主张。
