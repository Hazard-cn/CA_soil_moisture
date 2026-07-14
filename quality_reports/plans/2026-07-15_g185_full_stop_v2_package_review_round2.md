# G185 旧方法统一稿 full_stop_v2 失败包独立审查（Round 2）

## 审查结论

**判定：`PASS_FAILURE_PACKAGE`。** 本判定只表示 `temp/2026-07-15_g185_old_method_unified_full_stop_v2/` 已构成边界明确、文件完整、可复核运行身份充分的失败归档包；它不改变冻结设计的 `STOP`，不将该方向恢复为候选稿，也不授权将结果改写为投稿结论。标准 `run_manifest.json` 必须继续保持 `status=STOP`、`not_for_inference=true`、`claims=[]`，扩展 `full_manifest.json` 必须继续保持 `status=FULL_STOP`、`public_claim=none`。

本次外部审查只新增本文件，没有修改运行包、运行时 `README_REVIEW_PENDING.md` 快照或公开稿。运行时README是程序生成并纳入哈希的边界快照，本文件是运行结束后的独立审查记录，两者用途不同，不能相互覆盖。

## 审查对象与身份

- canonical ID：`g185-old-method-unified-v1`
- run ID：`2026-07-15_g185_old_method_unified_full_stop_v2`
- 冻结设计：`quality_reports/plans/2026-07-14_g185_old_method_unified_design_v2.md`
- `full_manifest.json` SHA-256：`3a23e22b421f052a4afc5f83c6aa806dd5a8f081bdb83aded357b2af6ca8aaec`
- `run_manifest.json` SHA-256：`1012f385dcfe4939a4fbe90472f577afd373334b23041532361db16252783393`
- v1冻结STOP数值参考 `FULL_STOP.json` SHA-256：`13de582e903adf782ba977a6dff22f2de15b4590d579b109469618841c580871`
- 运行时代码基线：`3da8a12f94c04f7d19b6153bb1691787340ba4a8`；该值只表示Git基线，实际执行脚本、core、schema和设计文件均另有直接字节哈希。

逐字节复算确认：`full_manifest.output_hashes` 登记了运行目录21个文件中除 `full_manifest.json` 自身外的全部20个文件，20项均匹配；`run_manifest.inputs` 登记的G185基础面板、V3 hot-dry sidecar、v1冻结参考、三个执行代码文件、标准manifest schema和冻结设计共8项，其字节数与SHA-256均匹配；`full_manifest.execution_file_hashes` 的5项执行身份哈希也均匹配。标准manifest通过 `jsonschema.Draft202012Validator`，扩展包通过 `validate_full_output_bundle()`。

## 冻结STOP门槛复核

冻结设计第140行规定：三个核心区域—胁迫组合在 `grid FE + province×year FE` 下任一点估计符号反转，或者2° Rademacher同步bootstrap中同向非线性统计量比例低于90%，即停止投稿稿件。v2结果机械触发后半项：

| 核心组合 | 历史grid+year端点（%） | province×year端点（%） | 同向draw数 | 同向比例 | 判定 |
|---|---:|---:|---:|---:|---|
| NE—干旱 | 1.8502198111 | 0.8415784270 | 1683/1999 | 0.8419209605 | `STOP` |
| HHH—高温 | 3.1683722634 | 2.1996347138 | 1972/1999 | 0.9864932466 | 通过本项 |
| HHH—热干 | 2.4254343577 | 1.6215617026 | 1834/1999 | 0.9174587294 | 通过本项 |

三个点估计均未反号，但NE—干旱的同向比例低于0.90。因此 `stop_reasons=["province-year core sign/share STOP rule triggered"]` 与冻结规则一致；不得通过降低门槛、改换固定效应、改换空间块或选择其他规格解除。

## 机器表完整性与结构核验

15张CSV均存在、哈希匹配且数值字段有限。行数分别为：`all_component_estimates` 486、`all_endpoint_estimates` 162、`conley_diagnostics` 108、`core_curve_data` 909、`inference_robustness` 198、`legacy_core_te_reproduction` 3、`legacy_values_de_only` 3、`model_registry` 36、`national_components` 81、`national_p90_endpoints` 27、`regional_components` 405、`regional_iede_matrix` 135、`regional_joint_tests` 45、`regional_omnibus_tests` 9、`regional_te_matrix` 45。

组合基数进一步核验如下：五区×三胁迫×三bootstrap方法的区域IE/DE/TE端点为135行，五区×三胁迫×三方法的TE矩阵为45行，完整15检验族×三方法的Romano–Wolf/Holm表为45行，三胁迫×三方法的区域同质性检验为9行且 `rank(RVR')` 全部等于4；三层同步bootstrap形状分别为 `999×15`、`1999×15`、`1999×15`，联合协方差秩均为15。100/200/300 km、全国/五区、两类固定效应和三胁迫组合形成108项Conley诊断，全部 `finite=true` 且最小特征值满足冻结容差；36个模型登记项无缺失，吸收后设计矩阵满秩，最大固定效应组均值低于 `1e-10`。

## 数值复现与代数边界

从机器表独立复算，固定SR水平的 `TE slope = IE slope + DE slope` 最大绝对误差为 `1.0408341e-16`；P75−P25端点的scaled-slope恒等式最大绝对误差为 `1.0061396e-16`；`scaled_slope_delta=slope_delta_per_sr×SR IQR` 最大绝对误差为 `9.3458227e-17`。固定水平和端点的指数转换最大误差分别为 `2.1884716e-12` 和 `1.4552803e-12` 个百分点，三条核心曲线与对应P90端点最大误差为0。CSV十进制序列化后的误差略高于运行内存中登记的 `3.4694470e-18`，但远低于项目容差。

全国历史grid+year、P75−P25、胁迫P90下的TE复算为干旱 `0.5768382689%`、高温 `1.1579801424%`、热干 `1.1464431613%`，相对冻结目标的最大误差为 `2.6893413e-07` 个百分点。三个校正核心TE的点估计与历史seed区间最大复现误差为 `9.4391162e-12`；旧 `1.50%`、`3.27%`、`2.56%` 在机器表中全部标记为 `DE`，没有再次混写为TE。

`historical_validation.json` 与v1 `FULL_STOP.json` 的全国误差、三个核心复现误差、TE恒等式误差、曲线端点误差、三个核心方向诊断和STOP原因逐项相同；`full_v1_exact_numeric_match=true` 有对应冻结文件及其直接哈希支持。

## v1与v2的输出顺序关系

首次 `2026-07-14_g185_old_method_unified_full_v1` 在计算出STOP后先抛出异常，仅留下 `FULL_STOP.json` 和异常包装器生成的 `FULL_FAILED.json`，没有继续写标准manifest和完整机器表。v2使用新的run ID，先写入全部机器表、标准manifest、运行日志、运行时README和扩展manifest，随后执行完整包验证，最后把同一冻结STOP作为 `PresetStop` 返回；v2没有 `RUNTIME_FAILED.json` 或冒充通过的图表/主张。该调整只改变失败产物落盘顺序，不改变v1冻结数值、估计规格或STOP结论，也没有回写或覆盖v1目录。

运行时README的SHA-256为 `ff57d203b21fa201e7183e673ec6db9cbd54d314f6a0bd667d1f11ffd7610add`，并被 `full_manifest.output_hashes` 绑定。对已存在v2输出路径调用非覆盖保护得到预期 `FileExistsError`；14项 `unittest` 全部通过，其中包含既有目录拒写、逃逸路径拒绝、冻结CLI组合、完整STOP包、六类运行级完成状态和180项HAC状态汇总测试。

## 问题分级

无Critical，无Major。存在一个不阻断归档的Minor：运行时README写有“完整机器结果和图表”，实际失败包包含完整机器表但没有图文件。由于冻结STOP已经禁止该方向进入候选稿，且本轮验收对象是失败证据和机器结果，该措辞不影响 `PASS_FAILURE_PACKAGE`；后续如建立新的失败包模板，应改为“完整机器结果”，不能修改本运行时哈希快照来消除该措辞。

## 固定六维评分

| 维度 | 得分 | 依据 |
|---|---:|---|
| 创新与期刊匹配 | 14/20 | 旧方法统一整理具有证据组织价值，但冻结稳定性门槛失败，不能形成投稿主张。 |
| 数据和五区支持 | 20/20 | 样本、双重样本键、46,299/13,236及命名区44,556/12,745边界均被manifest和完整五区机器表绑定。 |
| estimand与识别边界 | 18/20 | IE/DE/TE始终限定为同期两方程代数组件，旧DE未混写为TE；非因果边界明确。 |
| SM构念及时序 | 13/15 | 同期SM的代数组件角色披露清楚，但该旧方法本身不提供严格时序中介识别。 |
| 精度与稳定性 | 8/15 | 数值复现、联合推断和HAC均完整，但NE—干旱明确未通过预设90%稳定性门槛。 |
| 可复现性和图表完整性 | 10/10 | 输入、代码、设计、schema和全部失败输出被直接哈希，测试与非覆盖保护通过；失败包不要求生成投稿图。 |
| **合计** | **83/100** | 分数不奖励显著性；83分表示失败归档达到保存门槛，不表示投稿门槛通过。 |

## 最终边界

本轮允许将该run作为可复核失败证据归档，并允许另行形成明确标注 `STOP` 的失败报告；不允许将其列入候选小稿，不允许把 `PASS_FAILURE_PACKAGE` 解释为结果审查通过，也不允许用其他更有利规格补位。G185旧方法统一方向的投稿状态继续为 `STOP`。
