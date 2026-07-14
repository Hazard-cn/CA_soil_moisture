# 热干事件方向 small smoke 独立审查：Round 1

- 审查对象：`temp/2026-07-15_compound_event_interface_smoke_v1/`
- 冻结设计：`quality_reports/plans/2026-07-15_hotdry_event_duration_intensity_design_v1.md`
- 设计授权：`quality_reports/plans/2026-07-15_hotdry_event_design_review_round2_pass.md`
- canonical ID：`compound-event-intensity-duration-v1`
- 独立审查结论：`REVISE_SMOKE`
- 评分：88/100
- Critical：0
- 未解决Major：1
- 授权边界：不得以本run签发`PASS_SMOKE`；不得据此运行完整产量模型。Stage 1只读支持审计不属于产量模型授权。

## 评分

| 维度 | 得分 |
|---|---:|
| 创新与期刊匹配 | 19/20 |
| 数据与五区支持 | 19/20 |
| estimand与识别边界 | 18/20 |
| SM构念及时序 | 14/15 |
| 精度与稳定性 | 14/15 |
| 可复现性和图表完整性 | 4/10 |
| **合计** | **88/100** |

本次扣分不涉及显著性。small smoke没有估计产量模型，也没有生成可作推断的系数、区间或图表。

## Major 1：manifest没有锁定实际执行实现

`run_manifest.json`把`git_commit`登记为`3da8a12f94c04f7d19b6153bb1691787340ba4a8`，但本次执行实际使用的core、validator、runner、event schema、shared run schema和冻结设计均未包含在该提交中；审查时这些文件在worktree中仍为untracked。manifest的14项`inputs`只登记V3面板、产区映射和12个逐日数据文件，没有直接登记上述实现文件的bytes、MD5和SHA-256。因此，仅依据manifest及其`git_commit`不能重建本次执行代码，也不能排除未来同一路径内容改变后仍被误认为同一实现。

审查时实际文件身份如下，这些身份只能作为本轮审查证据，不能补写进已经冻结的v1 run：

| 文件 | bytes | MD5 | SHA-256 |
|---|---:|---|---|
| `scripts/python/hotdry_event_core.py` | 12,110 | `8467559c96a7cfd477e588d6fee33686` | `a6658b8f29a337106438db2343d4285f03ef582fa7eef195b83616a80bd25899` |
| `scripts/python/hotdry_event_validators.py` | 12,163 | `1dca7c5e8f26c54e90ad4897de55a4af` | `46a09160606aee4a0e955a1d5133b68d2060af826f9a360dd5dd50de8d39b0cc` |
| `scripts/python/run_hotdry_event_stage1.py` | 29,584 | `fe6f2108146a57acb490cfa2af9e197a` | `469039471911b7605dbd7b0913bcf56b89079b25ec43ddfffb94d0f8cc2211de` |
| `docs/contracts/event_panel.schema.json` | 9,231 | `590648c1148753ab8e912fb7f341213d` | `e59d07784320f0391b5474adc4cb844ecd7c1d9ab5d570c22f8713e62736d363` |
| `docs/contracts/run_manifest.schema.json` | 3,756 | `af2d9877a0d52f9209af5e8dfd5ba753` | `08c87cbbd95609f6f2290f516807e5b9a821e4fe36f713570d05be8ef51fc86a` |
| `quality_reports/plans/2026-07-15_hotdry_event_duration_intensity_design_v1.md` | 14,922 | `4f76821824b5fc554fe7b866abf085f6` | `5e165317a43e4c9ff8ae870018e503838238c3d2c21faacaa1ad190610fc8938` |

关闭条件为：保留v1不变，使用新run ID重新执行small smoke；新run的机器清单必须直接登记上述实际实现和schema的bytes、MD5与SHA-256，并使`git_commit`与已提交实现一致，或者明确登记可唯一重建工作树的实现哈希。建议同时登记两份测试文件和Round 2设计审查授权记录的哈希。修订run必须重新完成全部数值、schema、跨记录和不可覆盖核验。

## 已通过的独立核验

### 测试与契约

使用项目Python环境独立复跑：

```text
python -m pytest -q tests/test_hotdry_event_core.py tests/test_hotdry_event_validators.py
...................................... [100%]
38 passed in 0.26s
```

16项core测试覆盖恰好三日、间断、窗口边界、天气缺失中断、同窗双事件、无热日、孤立热干日、14/14日前置SM、前置缺失、结束即恢复、30日内恢复、下一事件删失、`ma-end`删失、drawdown重叠、30日上限和恢复前SM缺失。22项validator测试覆盖逐行schema、键唯一、事件序列、代表行、聚合量复制与恒等式、event ID、恢复状态、SM状态、SMOKE/STOP/FULL manifest语义和最小反例。两份JSON Schema均通过Draft 2020-12 meta-schema检查；将落盘的75行gzip CSV按15位双精度往返解析后，逐行schema和跨记录validator再次通过；run manifest也再次通过shared schema和方向语义validator。

### 输入与输出逐字节哈希

独立以单次字节流同时复算MD5与SHA-256。14项输入的bytes、MD5和SHA-256均与`run_manifest.json`及`input_inventory.json`完全一致，覆盖V3面板、产区映射以及2016—2019四年的Tmax、对齐降水和对齐SMrz。7项已完成输出的bytes和SHA-256均与`event_run_extension.json`完全一致：

| 输出 | bytes | SHA-256 | 复核 |
|---|---:|---|---|
| `event_panel.csv.gz` | 5,214 | `5e978584845b2ea4d76f2a2a3bf74dec3dc9e347ecbf06e6da7a5a03a64116d2` | PASS |
| `grid_year_support.csv` | 1,556 | `e0fc9abc811b1013033f5574298f19b49224ec687634fdee201fcd95c9eef95f` | PASS |
| `coordinate_value_audit.csv` | 81,638 | `cd287c9a6ad344076a4fcef528657e848af12a9e7f5ddb27ec231172adb21122` | PASS |
| `input_inventory.json` | 3,961 | `31d8ca0bfc6b7b74afc787b1d09c43ed1bcbf9c6033701348bd4f88d09ec0843` | PASS |
| `support_by_zone_year.csv` | 5 | `f01a374e9c81e3db89b3a42940c4d6a5447684986a1296e42bf13f196eed6295` | PASS |
| `support_by_zone.csv` | 5 | `f01a374e9c81e3db89b3a42940c4d6a5447684986a1296e42bf13f196eed6295` | PASS |
| `stage_decision.json` | 199 | `85cfdeca93e3a6f435577e6082c8505a349f9adbc11af08c871a211c3e566886` | PASS |

两个5-byte支持文件是interface smoke阶段的UTF-8 BOM空占位，Stage 1支持表在本阶段按设计标记为`SKIP`，不能把这些空文件解释为支持门槛结果。

### 样本、五区、四年与数值映射

manifest的40个sample keys经`grid_id|YYYY\n`排序序列化后独立复算SHA-256为`9902448054d0489f161f64257e98cde76cbda5ee42dcdfb786790ba44dbd1b08`，与manifest一致。40个grid-years严格分布为五区×四年×每格2个，全部`analysis_ready=true`；`event_panel.csv.gz`含75行、40个唯一grid-years和54个事件行，五区均有代表行，SH在该机械小样本中无合格事件但仍保留8个无事件代表行，符合smoke接口目的。

坐标和值审计含400行，严格为五区×四年×20个抽查。直接从12个NetCDF按登记的year、索引和DOY重新读取后，Tmax、降水、SMrz与参考坐标同落盘CSV的最大绝对差分别为`7.11e-15`、`3.55e-15`、`9.71e-17`、纬度`3.55e-15`和经度`1.42e-14`，均只是十进制序列化误差。面板到参考格网的最大纬度/经度绝对误差为`1.831055e-6`/`3.356935e-6`度，低于冻结的`1e-5`度门槛。

### 阶段门禁与不可覆盖

`run_manifest.json`为`status=SMOKE`、`not_for_inference=true`、`claims=[]`、CA分位点和暴露端点为null；`stage_decision.json`为`PASS_SMOKE`接口自检，但该字段不替代独立审查；`event_run_extension.json`和decision均为`yield_model_run=false`。对同一非空run目录再次调用runner时，在任何输入读取和输出写入前触发`FileExistsError: refusing to overwrite nonempty run directory`，历史run不可覆盖保护有效。

## Round 1结论

事件定义、SM时序、人工序列、逐行schema、跨记录语义、40/75接口、五区四年映射、坐标和值抽查、数据输入哈希、已完成输出哈希、`not_for_inference`和不可覆盖均通过本轮独立复核。唯一未关闭Major是实际实现身份没有被manifest或其git提交锁定；该问题影响run的可重建性，因此即使数值接口通过，仍不满足“无Critical/Major且评分不低于90”的`PASS_SMOKE`门槛。
