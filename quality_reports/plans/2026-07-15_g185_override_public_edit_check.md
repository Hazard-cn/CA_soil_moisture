# G185 override公共小稿编辑与一致性检查

- 检查对象：`docs/results/g185-old-method-unified-override-v1/report.md`
- 检查状态：`PASS_PUBLIC_EDIT_CHECK`
- 公共稿SHA-256：`8767cf008d67550d9708e313f529dcc6cc1042768413300e8f8037ae9afd5e1a`
- 公共稿行数：197
- 审查依据：Round 2 `PASS_ROUND2`，90/100；无Critical、无Major
- 范围边界：本次只生成公共Markdown并关闭Round 2的两个不阻断Minor，没有修改模型、估计量、样本、机器CSV、PNG、历史STOP、随机权重、manifest或谱系登记

## 输入身份

| 输入 | SHA-256 |
|---|---|
| `quality_reports/plans/2026-07-15_g185_old_method_unified_override_draft_v1.md` | `c7cb977eac3a808033c653a2cf1ecd1a6e1593152c198e6a8158ddcfc733affa` |
| `quality_reports/plans/2026-07-15_g185_override_method_review_round1.md` | `237b51e4fcdcc1709cd5d3b1cf9331d0335b3a0e9a6909367efcb320f8c8bd8d` |
| `quality_reports/plans/2026-07-15_g185_override_revision_response_round1.md` | `a1f05b059fcc927ac4313f1670ccc9112787714d209d9096f3a13c1ae377f17d` |
| `quality_reports/plans/2026-07-15_g185_override_method_review_round2.md` | `d6f6b94aa6fbaaacbb2e5fa4f2b79741b352dc60744b26a673fb6270591b9f45` |
| `quality_reports/plans/2026-07-15_g185_override_citation_verification.md` | `c7d0d0045d98a98511eda4d4c4a8d873a627c40f625aebaf54791ee8125f9035` |
| `temp/2026-07-15_g185_old_method_unified_override_v1/override_manifest.json` | `006b186661a0453569cf7fc58dbfd6031f9ffea1cae9741943c871b9c85e2287` |

## Round 2 Minor关闭

第一，原稿把含SR四分位距的对数斜率差与单位SR斜率同时写成`delta`。公共稿把前者统一记为`Δ_IE,k^log`、`Δ_DE,k^log`和`Δ_TE,k^log`，把分别指数转换的百分比端点记为`B_j,k(x)`，并把Romano–Wolf检验的单位SR—胁迫对数斜率改记为`θ_rk=a3_rk×b_rk+c3_rk`。正文不再出现`δ_rk=`，计算和CSV列没有修改。

第二，三幅图的详细限制不再只存放在Markdown alt字段。公共稿保留简短alt文本，并在每幅图后增加可见的斜体图注：图1明确27个组件水平未显示区间且不能用端点区间替代；图2明确历史FE、统一999次grid Rademacher、seed 42和非线性响应面禁读；图3明确历史FE、统一权重、百分比非可加、黄淮海25块和华南13块限制。结构检查得到3幅图片、3段可见图注，数量一一对应。

## 机器数值一致性

使用机器CSV按公共稿显示精度重新生成每一行Markdown，并与公共稿逐行比较。结果如下：

| 公共稿表格或正文数值 | 机器来源 | 核验范围 | 结果 |
|---|---|---:|---|
| 五区样本支持表 | `table1_sample_support.csv` | 5区的N、grids、空间块 | 逐行零差异 |
| 全国IE/DE/TE表 | `table2_national_iede_endpoints.csv` | 3胁迫×3组件的点估计和区间 | 逐行零差异 |
| 五区province×year TE表 | `table3_five_zone_iede_both_fe.csv` | 5区×3胁迫的点估计和区间 | 逐行零差异 |
| 三个核心组合空间推断表 | `table4_core_spatial_inference.csv` | 3组合×6推断层的点估计和区间 | 逐行零差异 |
| 完整主要多重检验表 | `table5_complete_region_joint_tests.csv` | 5区×3胁迫的`p_raw/p_RW/p_Holm` | 45个显示p值零差异 |
| 高温区域omnibus正文值 | `table6_region_omnibus_tests.csv` | Rademacher与Webb的原始及Holm p值 | 4个显示p值零差异 |

自动检查共86项，失败0项。该检查还确认五个产区均出现、15项主要多重检验完整、正文保留“未按显著性删行”边界，以及补充机器表链接可解析。

## 哈希、引用与路径

`override_manifest.json`登记的12项派生输出重新计算为12/12匹配；来源`full_manifest.json`哈希仍为`3a23e22b421f052a4afc5f83c6aa806dd5a8f081bdb83aded357b2af6ca8aaec`，来源20项登记输出为20/20匹配。三幅图的实际哈希继续分别为`3a631fae...39f7`、`ce7457b...eeb9`和`82aa88ea...43d9`，没有重绘。

公共稿参考文献的5个DOI集合与三层引文核验文件完全相等：`10.1037/a0020761`、`10.1038/s43016-021-00341-6`、`10.1038/s41467-020-18631-1`、`10.1038/s43016-022-00592-x`和`10.1097/EDE.0000000000000596`。公共稿没有加入37篇核验语料之外的新学术文献。3个图链接、补充CSV链接、模型重估代码、数值核心、派生导出脚本和manifest链接均能解析到现有文件。

## 代码测试与格式检查

执行`python -m unittest tests.test_export_g185_old_method_override tests.test_g185_old_method_core -v`，16项测试全部通过。测试覆盖来源manifest身份、冻结CLI、样本序列化、代数恒等式、固定效应吸收、wild权重、Romano–Wolf/Holm、Conley有序对与对角项、HAC诊断、非覆盖输出及完整STOP包验证。

Markdown检查得到：行尾空白0处，一级标题1个，二级章节11个，图片3幅，可见图注3段，旧`δ_rk`符号和计划稿的pending状态均为0处。公共稿明确报告G185选择历史、东北干旱84.1921%、华南13块、多数空间区间跨零、同期SM时序和非因果边界；没有把取消门槛改写成方法学通过。

## 未完成项

本次公共编辑范围内无未完成项。该文件仍是90分候选小稿，不是95分投稿完成稿；作者名单与CRediT、经费、利益冲突、上游数据许可和目标期刊届时有效的AI披露文本只能由作者依据真实信息补齐。机器包manifest保留其生成时的`DERIVED_OVERRIDE_REVIEW_PENDING/not_for_public_claim`状态，本次没有越权修改运行时身份或谱系；后续统一谱系发布应由组合根任务单独处理。
