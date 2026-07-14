# 热干事件强度—持续时间方向独立方法与结果审查：Round 1

## 审查结论

- Canonical ID：`compound-event-intensity-duration-override-v1`
- 审查模式：Academic Research Suite `methodology-focus`，只读独立审查
- 决定：**REVISE**
- 总分：**68/100**
- Critical：**0**
- Major：**6**
- Minor：**5**
- 通过门槛：总分不低于90，且Critical=0、Major=0；本轮未通过。

当前事件识别、五区支持、grid FE与province×year FE吸收、同步2°空间块Rademacher wild-score、Romano–Wolf/Holm以及recovery v2的点估计均可从代码和机器结果复现。阻断通过的主要问题不是数值表错误，而是主交互项被写成“损害缓冲”时没有同时报告低SR和高SR各自的条件暴露变化；黄淮海两项结果实际均由低SR负斜率转为高SR正斜率，不能直接表述为“两条损害斜率之间的缓冲”。此外，冻结设计触发的联合duration/intensity模型、预设窗口和空间推断核验、drawdown重叠事件敏感性以及失败run的标准身份闭包尚未完成。

## 固定评分

| 维度 | 得分 | 审查依据 |
|---|---:|---|
| 创新与期刊匹配 | 13/20 | 将事件持续时间、强度与事件级SM恢复连接具有方法增量，但公开稿尚无独立文献定位和期刊匹配部分，联合模型也未执行。 |
| 数据和五区支持 | 19/20 | 五区均满足原支持门槛，日历、坐标、事件panel键和全量支持表可核验；西南共同CA P75以上只有242个事件，需要持续披露外推支持。 |
| estimand与识别边界 | 9/20 | FE与交互公式实现正确，因果边界披露正确；但正文把只含交互差的量写成“损害差异”，没有报告两条条件变化，且缺少按冻结规则应进入主结果的联合模型。 |
| SM构念及时序 | 11/15 | antecedent、drawdown、行政删失、IPCW、cloglog与RMST30时序清楚；drawdown重叠下一事件的预设敏感性未执行，恢复终点在事件结束日高度集中。 |
| 精度与稳定性 | 9/15 | 1,999次同步Rademacher、RW/Holm和LOYO已执行；Webb、100/200/300 km HAC、严格V3—MA窗口和Stata/R复算未执行。 |
| 可复现性和图表完整性 | 7/10 | 正式run的输入/输出哈希全部闭包，点估计可精确复算；两个失败模型run和report run缺少标准manifest，主图标签与estimand语义不一致，公开Markdown未呈现图片。 |

## 独立核验记录

### 已通过的机器核验

1. `identity_smoke_v1`、`stage1_v1`、`models_v3`、`recovery_audit_v1`和`recovery_v2`五个run的manifest输入哈希及extension登记产物哈希均逐项复算一致，未发现缺失文件或哈希漂移。
2. override smoke的75条event-panel记录和40条grid-year支持记录与历史`compound_event_interface_smoke_v2`逐字段相等；该比较结论为真，但历史v2机器文件尚未作为新smoke的输入身份登记。
3. 原事件、validator、stage1、override、产量模型和recovery v1测试共50项在项目Python环境通过；recovery v2的4项测试在执行解释器Python 3.14.2逐项通过。
4. 从`model_ready_panel.csv.gz`重新吸收grid FE和province×year FE并使用同一seed重算，duration与intensity两套18列设计均为rank 18，标准化条件数分别为4.9788和5.3360，产量主结果、区间和RW/Holm p值与机器表的最大绝对差不超过`2.22e-14`。
5. 从`recovery_risk_set.csv.gz`重新估计固定IPCW加权cloglog、同一165个2°块和1,999次抽样，五区RMST30点估计、区间和RW/Holm p值与机器表的最大绝对差不超过`9.61e-15`。
6. 四幅机器图均为3600×1500像素、约300 DPI、白底。产量主图的数值绘制正确，但横轴“Conditional damage difference”不符合两条条件斜率的实际符号。

### 低SR与高SR条件变化复算

下表按现有系数和冻结端点计算`100×[exp{(beta_z+delta_z×CA_q)×(E90-E50)}−1]`。最后一列是现有报告量`100×[exp{delta_z×(CA75−CA25)×(E90−E50)}−1]`，它是两个条件变化因子的比率差，不是前两列百分比的简单百分点差。

| 产区 | 暴露 | CA P25条件变化 | CA P75条件变化 | 现有P75相对P25对比 |
|---|---|---:|---:|---:|
| NE | duration | 11.54% | 8.65% | -2.59% |
| NE | intensity | 14.00% | 7.75% | -5.48% |
| HHH | duration | -3.10% | 9.42% | 12.93% |
| HHH | intensity | -4.32% | 6.22% | 11.02% |
| NW | duration | 4.37% | 12.59% | 7.88% |
| NW | intensity | 8.74% | 12.99% | 3.91% |
| SW | duration | 5.92% | 4.27% | -1.56% |
| SW | intensity | 13.75% | 11.92% | -1.61% |
| SH | duration | 13.89% | 12.09% | -1.59% |
| SH | intensity | -1.30% | 2.26% | 3.61% |

黄淮海的正交互对比由条件变化从负值转为正值形成；东北、西北和西南的多数低、高SR条件变化本身均为正。由此，现有交互结果可以称为“较高SR与暴露—产量条件斜率之差相关”，不能在不展示两条斜率的情况下统一称为“较小损害”或“缓冲”。

## Major问题与必修项

### Major 1：主estimand的“损害/缓冲”语义与实际条件斜率不一致

- 位置：`docs/results/compound-event-intensity-duration-override-v1/report.md:14`、`:39`、`:43-56`、`:124`；`scripts/python/run_hotdry_event_override_models.py:240-277`；`scripts/python/run_hotdry_event_override_models.py:153-179`；`scripts/python/render_hotdry_event_override_results.py:38-61`。
- 问题：当前机器表只保存交互对比，没有保存CA P25和P75各自的P50→P90条件变化。公开稿和图1据此把正对比解释为“较小损害”，但黄淮海两项均从低SR负变化转为高SR正变化；其余多个区的两条条件变化本来就是正值。这不是两条负损害斜率之间的单纯衰减。
- 影响：主结论的经济含义无法由当前表和图验证，并存在把“斜率上移”自动等同于“损害缓冲”的过度解释。
- 必修：在新的非覆盖run中生成`conditional_changes_by_ca.csv`，对五区×两暴露同时保存CA P25、P75的log change、百分比变化、同一1,999次抽样区间和交互对比；机器字段与正文统一改为`high_minus_low_sr_conditional_change_contrast`等中性名称。图1至少同时显示两条条件变化及其区间，交互对比可放同图右侧或独立面板。摘要、主结果、结论和图轴不得继续把所有正对比直接称为损害缓冲。若保留“缓冲”一词，必须限定为低、高SR两条条件变化均为负且高SR绝对损失更小的情形；当前黄淮海结果应写成“条件斜率由负转正的正交互对比”。

### Major 2：冻结触发规则要求的联合duration/intensity模型未执行

- 位置：`quality_reports/plans/2026-07-15_hotdry_event_duration_intensity_design_v1.md:60-62`；`scripts/python/run_hotdry_event_override_models.py:67-80`、`:221-277`；`docs/results/compound-event-intensity-duration-override-v1/report.md:124`。
- 问题：执行程序只拟合两个独立模型。按冻结FWL规则独立复算，共同残差暴露VIF为1.107，各区残差暴露VIF最大为1.613；联合28列吸收后设计rank 28/28，标准化条件数7.846，均满足VIF<5、满秩和条件数<30的预设触发条件。
- 影响：联合模型按设计应进入主结果而非留待后续；缺失时不能判断黄淮海duration与intensity结果是否为同一暴露结构的替代表示。
- 必修：新增冻结联合模型run，保存FWL-VIF、联合设计秩和条件数、完整系数、五区两项条件变化与交互对比、同步2°空间块推断及同一检验族的调整结果。独立模型继续保留，不得用联合模型替换或隐藏其结果。

### Major 3：预设窗口与空间推断核验尚未完成

- 位置：`quality_reports/plans/2026-07-15_hotdry_event_duration_intensity_design_v1.md:24`、`:64-72`、`:86`；`scripts/python/run_hotdry_event_override_models.py:408-413`；`docs/results/compound-event-intensity-duration-override-v1/report.md:124`。
- 问题：现有run只完成扩展V3—MA窗口、Rademacher主抽样、grid聚类SE和LOYO。manifest列出100/200/300 km HAC带宽，但没有对应计算产物；Webb六点抽样、严格`v3_doy..ma_doy`五区窗口敏感性和Stata/R点估计复算均缺失。
- 影响：manifest中的规划字段与实际完成的推断产物边界不够清楚，且尚不能满足冻结设计和最终验收的稳定性要求。
- 必修：用新run补齐五区严格窗口结果、2° Webb、100/200/300 km HAC和Stata/R复算；完整披露反向和不显著结果。manifest必须把“已执行”与“预设但未执行”分开，不得只列带宽数组。产量10项应另存同步bootstrap联合协方差或可审计抽样矩阵，以便独立复核RW family。

### Major 4：预设drawdown重叠事件敏感性缺失

- 位置：`quality_reports/plans/2026-07-15_hotdry_event_duration_intensity_design_v1.md:42-54`；`scripts/python/hotdry_event_core.py:189-203`；`scripts/python/run_hotdry_event_override_models.py:315-339`；`docs/results/compound-event-intensity-duration-override-v1/report.md:58-68`。
- 问题：核心程序正确生成`drawdown_overlap_next_event`，但SM表只报告未调整高低SR组均值。独立统计显示五区112,832个事件中17,944个与下一事件窗口重叠，占15.90%；西北为4,775/16,772，即28.47%。冻结设计明确要求报告数量并执行排除重叠事件的敏感性。
- 影响：西北等地区的最低SM可能部分来自下一事件，当前drawdown组间差不能作为完整的通道一致证据。
- 必修：新增五区重叠支持表，并用同一CA端点同时报告全样本和排除重叠事件后的antecedent、drawdown描述结果；不得只保留方向更有利的一套。原始未调整表继续保留，并在图注中标为描述性、非中介估计。

### Major 5：失败run和图表run尚未达到标准身份闭包

- 位置：`temp/2026-07-15_compound_event_override_models_v1/`、`temp/2026-07-15_compound_event_override_models_v2/`、`temp/2026-07-15_compound_event_override_report_v1/`；`quality_reports/plans/2026-07-15_hotdry_event_duration_intensity_design_v1.md:86`；`docs/results/compound-event-intensity-duration-override-v1/report.md:88-108`。
- 问题：models v1只有`FAILED_NUMERICAL_ABSORPTION.json`；models v2保存部分结果和`FAILED_PLOTTING_ENVIRONMENT.json`，但两者均无标准`run_manifest.json`与extension，v2部分产物也未形成run内哈希表。report v1只有三幅图，没有renderer身份、输入哈希、图哈希和manifest。公开稿虽然文字披露两个失败，但机器闭包不完整。
- 影响：失败路径和最终绘图无法按同一可复现标准审计。
- 必修：不得回写或覆盖历史目录；创建新的`failure_closure_v1`审计run，逐项登记v1/v2目录内容、输入身份、失败阶段、partial outputs哈希和`not_for_inference=true`。创建新的report run，登记renderer、输入manifest、全部图哈希和图规格。公开稿引用新闭包run并继续保留原失败说明。

### Major 6：当前公开文件仍是执行报告，不满足计划要求的小draft结构和可见图表

- 位置：`docs/results/compound-event-intensity-duration-override-v1/report.md:1-124`。
- 问题：现有Markdown有数据、模型、结果和局限，但缺少独立的文献定位、稳健性汇总、期刊匹配和引用核验部分；正文没有嵌入或链接呈现三幅主图。原冻结图表要求中的“antecedent与drawdown”联合图也未形成，recovery曲线没有进入可见稿件并缺少fixed-IPCW one-step、不传播删失模型误差的图注。
- 影响：即使机器结果存在，当前文件仍不能作为评分不低于90的小draft进入候选集。
- 必修：按既定结构重排为中文小draft，至少含摘要、研究问题、文献定位、数据、模型与estimand、五区主结果、SM证据、事件/窗口扩展、稳健性、局限和投稿匹配；嵌入或稳定链接三幅主图。图1使用中性条件变化语义，图2同时呈现antecedent与drawdown，图3呈现五区恢复曲线并在图注写明固定IPCW one-step和未传播删失模型估计误差。

## Minor问题

1. `temp/2026-07-15_compound_event_override_stage1_v1/run_manifest.json`对全量Stage 1仍使用`status=SMOKE`。其`not_for_inference=true`是正确的，但状态名称不能与全量支持run混淆；新run或lineage说明应明确“FULL_STAGE1_NONINFERENTIAL”。
2. recovery v2的加权cloglog Hessian条件数为`1.918×10^8`。独立等价缩放复算把连续变量标准化后，条件数降为9,272，预测概率最大绝对差仅`2.42e-14`，说明主要是量纲问题而非不同最优解；仍应把该缩放等价核验登记为机器表，并优先用缩放参数化生成推断，避免直接逆高条件数Hessian。
3. 五区恢复样本中94.40%的事件在事件结束日即达到`0.9×antecedent SMrz`，恢复终点辨别度有限。公开稿应报告该比例及分区比例，而不只用“多数事件”解释RMST量级。
4. 当前测试不能在单一已登记环境一次运行：项目venv缺少`patsy`，执行解释器缺少`pytest`；recovery v2测试也只检查风险编码和权重算术，没有直接构造分离数据并验证L2拟合有限。应固定一份可运行的环境清单，并补充L2分离、标准化曲线和解析梯度有限差分测试。
5. 新smoke与历史v2逐字段相等的结论已经独立验证，但新manifest只登记历史STOP审查和公开报告，没有登记历史v2 manifest/event panel或单独comparison artifact。应在新的比较审计run中补齐该来源闭包。

## 结果完整性判断

非显著和反向结果已完整保留：五区十项产量交互全部报告，只有黄淮海两项RW调整后区间和p值支持非零正对比；其余八项区间跨0，西南强度LOYO仅2/4同向；五区RMST30区间均跨0且RW p值均大于0.35。公开稿没有把恢复结果包装为机制确认，也没有声称全国一致缓冲或因果中介。这部分符合结果完整性要求。

## Round 2验收清单

Round 2只核验上述问题是否关闭，不允许按显著性更换阈值、事件长度、窗口或样本。重新送审至少应提供：

1. 中性命名的低/高SR条件变化机器表、区间和新主图；
2. 预设联合模型及FWL-VIF、rank、condition诊断；
3. 严格窗口、Webb、HAC三带宽、Stata/R复算和产量联合bootstrap协方差；
4. drawdown重叠事件支持及排除敏感性；
5. failure closure与新report run manifest；
6. 完整中文小draft及三幅可见主图；
7. 全部新run输入/输出哈希、测试记录及不覆盖历史run的证明。

以上七项全部通过、Critical=0、Major=0且总分不低于90时，事件方向方可通过Round 2。
