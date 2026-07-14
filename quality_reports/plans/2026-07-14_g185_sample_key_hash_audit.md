# G185 样本键哈希冲突审计

## 判定

历史初始状态：`STOP_DESIGN_CONTRACT_CONFLICT`。当前状态：设计方已采用双哈希修订并授权重新执行smoke；最终有效候选只能是修复非覆盖接口后的 `smoke_v4`，仍须通过独立smoke审查。本审计从未授权绕过任一样本键断言。

显式 G185 谓词重新得到 46,299 个 `grid_id,year` 键；与历史 `G185` 枚举路径得到的键集合完全相同，旧集合减新集合与新集合减旧集合均为 0。因此，当前冲突不是样本选择差异，而是冻结哈希的生成算法与设计 v2 后续写明的唯一序列化规则不一致。

## 冻结值的确切来源

冻结值

```text
5474250d140bef9a8fc0957158ed815f635220e0c0df7080d7a1b5f7d4469b89
```

可由下列算法精确复现：

```python
keys = sample[["grid_id", "year"]].sort_values(["grid_id", "year"], kind="stable")
payload = "\n".join(keys["grid_id"].astype(str) + "|" + keys["year"].astype(str)).encode("utf-8")
digest = hashlib.sha256(payload).hexdigest()
```

该算法按数值型 `grid_id` 排序，使用竖线分隔两个字段，不含表头，记录之间使用 LF，最后一条记录后不含 LF。它不符合设计 v2 第107行冻结的 `sample-key-csv-v1`：后者要求逗号分隔、包含一次 `grid_id,year` 表头、CSV 最小双引号转义，并将 `grid_id` 先规范化为 UTF-8 字符串后排序。

## 候选算法核验

| 候选算法 | SHA-256 | 是否匹配冻结值 |
|---|---|---|
| 历史竖线串：数值排序、`grid_id|year`、无表头、无末尾LF | `5474250d140bef9a8fc0957158ed815f635220e0c0df7080d7a1b5f7d4469b89` | 是 |
| 严格按设计文字执行 `sample-key-csv-v1`：字符串排序、CSV表头、逗号、LF、最小转义 | `36029c5f8ba689a1cbf6a14b688e8a43342ab8b7acd9b704136cb152fa170bcb` | 否 |
| 保留数值排序，其余使用CSV表头、逗号、LF、最小转义 | `11c0931bebe5b14dea90617ea1368cc4b75dcfce7102c15ab051fc82710ddcf0` | 否 |
| `pandas.util.hash_pandas_object(index=False)` 的uint64字节流 | `0b60b2815777b5936c64cf5071cfa6a60e040b8859dfbdcb1236cd9766047f01` | 否 |
| 数值排序、CSV全部字段强制双引号 | `70c5d13d875105f308ac480f838eba5dc582c1ef948f067b86ac8bc6c2b5aa92` | 否 |

另对 960 种常见文本组合进行了核验，组合包括五种 `grid_id` 格式、数值/字符串两种排序、四种分隔符、有无表头、LF/CRLF、UTF-8/UTF-8-SIG、CSV最小/全部/不加引号；除上述历史竖线串的单独算法外，没有候选匹配冻结值。

## smoke 状态

八项纯函数单元测试通过。首次 smoke 在输入文件哈希、1:1 合并、D/W 公式与显式样本谓词之后，于样本键硬门槛停止；尚未运行任何区域回归或 bootstrap。入口已创建但未写入内容的目录 `temp/2026-07-14_g185_old_method_unified_smoke_v1/` 按不删除约束保留。设计方解决冲突之前，不得使用该 run ID，也不得启动 v2。

可接受的设计修复只能由独立审查重新冻结二者之一：保留旧哈希并把序列化版本明确写为历史竖线算法，或保留 `sample-key-csv-v1` 并重新冻结相应的新哈希。实现阶段不得自行选择。

## 后续设计裁定与 smoke 历史

设计方在上述 STOP 后完成非估计量复现元数据修订并授权继续：`5474250d...` 保留为 `legacy-sample-key-pipe-v1`，严格执行设计文字规则得到的 `36029c5f...` 登记为 `sample-key-csv-v1` canonical secondary hash。后续入口必须同时计算并断言二者，任一不符仍触发 STOP；该裁定没有改变G185样本谓词、估计量或实证结果。

`smoke_v2` 曾被误报为通过，原因是程序生成了全国统一的 grid Rademacher 权重矩阵，却只实际调用了2°空间块 Rademacher/Webb 的 `score_bootstrap_betas`，未把 grid-cluster Rademacher draw 送入15维联合协方差、Romano–Wolf和区域 omnibus 接口。`smoke_v3` 增加了实际 grid draw 调用和如下防回归断言：grid、2° Rademacher、2° Webb 三套矩阵均必须为 `B×15`；两类FE下三套协方差均须完整；grid Romano–Wolf必须返回15项有限结果；每个胁迫的grid区域omnibus秩必须为4。由于历史run不可覆盖，`v2`被保留但不得作为有效 smoke 证据。

`smoke_v3` 后的独立代码审查又发现一个非覆盖Critical：旧异常处理在 `ensure_new_output_dir` 因目标已存在而抛错后，仍可能向该既有目录写入 `SMOKE_FAILED.json`。修订接口将目录创建放在异常记录作用域之外；只有创建函数已经由本次调用成功返回，后续异常才可在本次新目录内登记失败。新增回归测试预先建立含sentinel的run目录，调用入口后同时断言目录成员、sentinel SHA-256、文件mtime、目录mtime均不变化且不存在 `SMOKE_FAILED.json`。修订后的有效运行必须使用新的 `smoke_v4`，不得改写 `v1`—`v3`。

## smoke_v5 运行级契约返修

`smoke_v4` 的独立审查确认非覆盖Critical已关闭，同时提出运行契约层面的Major/Minor：详细 `smoke_manifest.json` 未提供项目统一 `run_manifest` 数据契约；PASS状态主要依赖过程内布尔值，没有把manifest声明的两类FE和三套权重方法与diagnostics完成集合逐项绑定；`all_hac_finite`为常量而非全部HAC状态的派生值；CLI还允许只传入部分FE或score cluster，可能形成不完整运行。

`smoke_v5` 按以下方式关闭这些问题：在内存中生成标准 `run_manifest.json`，使用 `jsonschema.Draft202012Validator` 和format checker按 `docs/contracts/run_manifest.schema.json` 验证；详细manifest继续作为扩展。运行级完成验证器固定声明 `grid_year`、`grid_provyear` 与 `grid_rademacher`、`spatial_block_rademacher`、`spatial_block_webb` 的六个笛卡尔组合，并逐一要求draw矩阵为 `B×15`、协方差秩15、Romano–Wolf恰有15项且全部有限、三个预设胁迫omnibus均秩4且有限。HAC状态从 `2 FE × 15区域胁迫模型 × 3带宽 × 2方程=180` 项逐项解析汇总，任一非有限即停止。CLI在创建输出目录前拒绝任何不完整FE/score-cluster集合、非2°块或非seed 42。只有运行级完成验证、180项HAC汇总和JSON Schema验证全部返回后，程序才写入任何包含PASS的产物。`smoke_v5` 必须使用新目录并保留 `v1`—`v4`。
