# 热干事件方向 small smoke 独立审查：Round 2（最终停止）

- 审查对象：`temp/2026-07-15_compound_event_interface_smoke_v2/`
- 对照run：`temp/2026-07-15_compound_event_interface_smoke_v1/`
- Round 1：`quality_reports/plans/2026-07-15_hotdry_event_smoke_review_round1.md`
- 冻结设计：`quality_reports/plans/2026-07-15_hotdry_event_duration_intensity_design_v1.md`
- canonical ID：`compound-event-intensity-duration-v1`
- 独立审查结论：`STOP_AT_SMOKE_REVIEW`
- 评分：89/100
- Critical：0
- 未解决Major：1
- 最终授权边界：不得签发`PASS_SMOKE`，不得生成small smoke v3补位，不得运行事件方向的完整产量模型，不得把Stage 1未完成状态写成实证结果或不显著结论。

## 评分

| 维度 | 得分 |
|---|---:|
| 创新与期刊匹配 | 19/20 |
| 数据与五区支持 | 19/20 |
| estimand与识别边界 | 18/20 |
| SM构念及时序 | 14/15 |
| 精度与稳定性 | 14/15 |
| 可复现性和图表完整性 | 5/10 |
| **合计** | **89/100** |

评分不奖励或惩罚显著性。本阶段没有估计产量模型，没有可供显著性判断的结果。

## Round 1 Major的修订状态

v2把Round 1缺失的大部分实现身份纳入`run_manifest.json`与`input_inventory.json`。23项inputs包括14项数据输入和9项实现、契约与审核输入：core、validator、runner、event schema、shared run schema、冻结设计、Round 2设计审查记录、core测试和validator测试。独立逐字节复算这23项的bytes、MD5与SHA-256，全部与两份机器清单一致。v2因此关闭了Round 1所指出的core、validator、runner、schema和设计身份缺失，但没有完全关闭“全部实际测试身份可重建”的要求。

## 未解决Major：第41项测试所在文件没有被run锁定

本轮要求复跑的41项测试分布在三个文件中，其中新增的两项runner索引测试位于：

```text
tests/test_hotdry_event_stage1_runner.py
bytes   = 1219
MD5     = 6b1ab85d4261ecc5c9919f92d200604b
SHA-256 = fe9616abd196e09d7ae8aee3fa9e15a2cc945383071aeb8e8e1301e1f97e3b55
```

该文件测试`daily_values()`的普通point索引和1,000-point bulk索引是否与NumPy pairwise gather完全一致，直接针对本轮runner实施变化；但v2的23项inputs没有该文件。`scripts/python/run_hotdry_event_stage1.py`的implementation inputs只列出`test_core`和`test_validators`，`scripts/python/hotdry_event_validators.py`中的`REQUIRED_EVENT_INPUT_ROLES`也只强制这两个测试角色。因此，v2可以在第三测试文件未被登记的情况下通过方向manifest validator，不能证明本轮实际复跑的全部41项测试具有固定身份。

本问题属于可复现性Major，不因41项测试当前均通过而消失。冻结审核流程规定每个阶段最多两轮返修；Round 2仍有Major时该方向必须停止。因此不得再生成v3以补录该哈希，也不得以另一个规格或run ID绕过停止门槛。

## 其余独立复核结果

### 41项测试

使用项目Python环境独立复跑三个测试文件：

```text
python -m pytest -q \
  tests/test_hotdry_event_core.py \
  tests/test_hotdry_event_validators.py \
  tests/test_hotdry_event_stage1_runner.py
......................................... [100%]
41 passed in 0.82s
```

所有人工事件、SM恢复、schema反例、跨记录反例、manifest语义和pairwise gather测试均通过。该测试结果证明当前工作树下的接口可计算性，不替代缺失的第三测试文件身份登记。

### 23项inputs与7项outputs

独立以字节流重新计算23项inputs。每项文件长度、MD5与SHA-256均与v2 manifest完全一致；14项数据输入与v1一致，新增9项已登记实现身份也均与当前文件一致。独立重新计算`event_run_extension.json`所列7项输出，文件长度与SHA-256全部通过：event panel、grid-year support、400条坐标值审计、input inventory、两个smoke阶段空支持表和stage decision均未发现哈希差异。

### v1/v2逐字段一致性

v1与v2的`grid_year_support.csv`、`coordinate_value_audit.csv`、两个空支持表和`stage_decision.json`逐字节一致。两版`event_panel.csv.gz`因gzip封装时间戳而压缩文件SHA-256不同，但解压后的CSV字节完全一致；按字段读取后75行×37列逐值、逐类型和缺失位置完全一致。两版共同保持：

- 40个唯一grid-years，五区×2016—2019每个区年单元2个；
- 75条event panel记录和40条grid-year support记录；
- 400条坐标值审计，即五区×四年×每单元20条；
- `stage_decision`逐字段同为`status=PASS_SMOKE`接口自检、`not_for_inference=true`、`yield_model_run=false`、空`stop_reasons`、75条records和40条grid-year statuses。

落盘v2 event panel经过15位双精度往返解析后，逐行schema与跨记录validator再次通过；v2 run manifest也通过当前shared schema和方向validator。上述通过项不改变第三测试身份缺失这一validator覆盖盲点。

### 不可覆盖与推断门禁

对v2同一非空run目录再次调用runner，在读取分析输入和写出结果前触发：

```text
FileExistsError: refusing to overwrite nonempty run directory
```

v2 run中只有interface smoke产物，`run_manifest.json`为`status=SMOKE`、`not_for_inference=true`、`claims=[]`，CA分位点与五区暴露端点均为null；extension与decision均为`yield_model_run=false`。Stage 1 v2没有完成独立结果审查，本报告不审查或解释其支持数值；没有运行完整产量模型，也没有事件方向的结果主张。

## 最终结论

v2保持了v1的全部事件、SM、五区四年、坐标和值结果，并锁定了23项已登记输入，数值接口和阶段门禁未发现其他Critical或Major。然而，实际41项测试中的第三测试文件没有进入run身份清单，导致可复现性Major在Round 2结束时仍未关闭。依据“每阶段最多两轮返修”的冻结规则，事件强度—持续时间方向在small smoke审查处最终停止，只保留本报告、两版smoke包和全部非推断性失败证据，不进入候选小稿或完整模型。
