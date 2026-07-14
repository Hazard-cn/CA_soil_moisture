# `regional-threshold-sr-override-v1` 独立方法与结果审稿（Round 1）

## 审稿身份与决定

- 工作流：Academic Research Suite / academic-paper-reviewer / methodology-focus
- 审稿对象：`regional-threshold-sr-override-v1`
- 审稿边界：只读核查设计、代码、测试、全量manifest、全部CSV和三幅图；原80%覆盖率门槛按用户授权不再作为计算阻断条件
- 结论：**REVISE**
- 评分：**57/100**
- 问题计数：Critical 0；Major 6；Minor 4
- 进入稿件门槛：当前存在未解决Major且总分低于90，**不得进入小稿或投稿主张阶段**

本轮没有发现主产量模型的系数符号在代码中被机械翻转，也没有发现图表点位与CSV相反；但是，SM状态模型存在一个确定的端点键覆盖错误，执行报告把SH的LOYO同向折数由实际2/4写成3/4，而且当前主产量结果在五区中只有SH满足“低SR下暴露增加对应产量下降”这一损害前提，SH的高低SR差异区间又跨0。因此，现有结果不能支持“地区异质阈值证明SR缓冲热害”的主张。覆盖门槛被取消只允许继续计算，不消除西南样本选择、四川完全缺失和共同CA高端点缺乏支持等识别问题。

## 一、可复现性与逐值核查

审查证据包括：

- `quality_reports/plans/2026-07-15_regional_threshold_override_execution.md`
- `quality_reports/plans/2026-07-15_regional_threshold_override_execution_report.md`
- `scripts/python/regional_threshold_daily_core.py`
- `scripts/python/run_regional_threshold_daily_override.py`
- `tests/test_regional_threshold_daily_core.py`
- `temp/2026-07-15_regional_threshold_daily_override_full_v1/run_manifest.json`
- 同一run下的七个CSV、`daily_exposure_panel.parquet`和三幅PNG
- `repo://references/code/related_literature_2026-07-14/rank_01_262BTEKM_eddthreshold/source/EDDthreshold/CalExposure.m`

全量run的11个已登记输出均通过bytes与SHA-256复核，runner和core的当前bytes与SHA-256也与manifest完全一致；`run_manifest.json`中的panel行数69,038、grids 22,180、输入哈希、日期轴、坐标误差、模型秩和FE收敛记录均能与执行代码或输出对应。10项单元测试全部通过，两个Python文件通过语法编译。三个PNG均为3,600×1,500像素、约300 DPI、白底；图1对应`yield_results.csv`的10个`full_ext`点，图2对应外生阈值的15个窗口点，图3对应`sm_channel_results.csv`的10个点，未发现点估计或区间方向与CSV不一致。

CSV内部恒等式复核结果如下：`yield_results.csv`为30个唯一的`exposure × window × zone`组合，`damage_at_ca_p75 - damage_at_ca_p25 = buffer_contrast`的最大绝对误差为`1.13×10^-16`；对数点估计及上下界转换为百分比的最大误差低于`1.7×10^-14`；各区P50/P90端点与行级parquet重新计算的最大误差为`2.84×10^-14`。`daily_support_by_zone_window.csv`与行级数据逐项完全一致，`exposure_quantiles.csv`的最大数值误差为`5.68×10^-14`。因此，主产量表的正负号不是导出或百分比换算造成的。

## 二、主要方法问题

### Major 1：SM状态端点发生跨单位键覆盖，10行状态结果必须全部重算

`scripts/python/regional_threshold_daily_core.py:239`将暴露端点字典与SM状态端点字典用`{**endpoints[zone], **state_points[zone]}`合并；两者都使用键`p50`，后写入的SM P50覆盖了暴露P50。随后`run_regional_threshold_daily_override.py:374`使用`endpoints[zone]["p90"] - endpoints[zone]["p50"]`构造暴露变化，实际计算成“暴露P90减SM P50”，混合了`°C-day`与`m3 m-3`两个单位。

| 产区 | 当前代码使用的暴露差 | 正确的暴露P90−P50 | 正确值/当前值 |
|---|---:|---:|---:|
| NE | 45.6841 | 43.6769 | 0.9561 |
| HHH | 291.1376 | 275.2547 | 0.9454 |
| NW | 179.5953 | 173.0534 | 0.9636 |
| SH | 37.6322 | 37.9971 | 1.0097 |
| SW | 23.4091 | 23.7716 | 1.0155 |

因为状态模型的两个线性组合权重都整体乘以该暴露差，当前`sm_state_results.csv`中的点估计、SE、CI和百分比均不属于预设estimand。方向大概率不变且当前误差小于0.01，但单位错误本身不能由数值容差豁免。必须把返回值改为不重名的`exposure_p50/exposure_p90/state_p25/state_p50/state_p75`，增加端点单位测试，重新生成SM状态表并修改执行报告。图3只使用SM通道表，不受此错误影响。

### Major 2：主交互没有形成“损害缓冲”estimand所需的损害前提

外生连续阈值、扩展V3—MA窗口下，低SR的P50→P90条件`ln_yield`变化分别为NE `+0.0580`、HHH `+0.5822`、NW `+0.0550`、SH `-0.1115`、SW `+0.0317`。五区中四区的低SR条件变化为正；HHH和NW显著为正的高低SR差异表示高SR组的正向条件斜率更大，不是较小的负向热害。只有SH同时满足低SR和高SR变化均为负且差异为正，但差异`0.0218`的grid-cluster区间`[-0.0167, 0.0603]`跨0。

代码中的`damage_at_ca_p25`、`damage_at_ca_p75`、`buffer_contrast`及图题中的buffer语义会把一般条件斜率差预设为损害缓冲，应统一改为`conditional_yield_change_at_*`和`high_minus_low_sr_slope_contrast`。当前结果可报告为地区异质的条件斜率结构，但不能以“SR缓冲温度损害”为稿件结论。应在主图同时展示低SR和高SR的条件产量变化及其区间，而不是只画两者差值；不得通过更换窗口、阈值或样本寻找负向基础斜率。

### Major 3：西南最终样本只保留原分母的50.11%，且四川完全退出识别样本

| 产区 | 阈值前行数 | 阈值有效行 | 逐日Tmax完整行 | 阈值覆盖率 | Tmax完整/阈值有效 | 最终/阈值前 |
|---|---:|---:|---:|---:|---:|---:|
| NE | 25,041 | 23,723 | 23,719 | 94.74% | 99.98% | 94.72% |
| HHH | 13,165 | 12,922 | 12,922 | 98.15% | 100.00% | 98.15% |
| NW | 5,540 | 4,681 | 4,681 | 84.49% | 100.00% | 84.49% |
| SH | 4,556 | 4,501 | 4,501 | 98.79% | 100.00% | 98.79% |
| SW | 18,094 | 12,637 | 9,067 | 69.84% | 71.75% | **50.11%** |

逐日Tmax缺失不是随机散点：阈值有效的四川3,570行、1,295个grids全部全年masked并全部退出模型；辽宁另有4行退出。西南结果实际由云南、贵州、广西和重庆构成，不能再解释为包含四川的完整西南玉米产区。取消80%规则不改变该目标总体变化。必须增加“阈值前→阈值有效→Tmax完整→模型complete-case”的省级样本漏斗、纳入与排除样本的CA/产量/气候比较以及空间覆盖图；若无法恢复四川逐日温度，则公开estimand必须明确限定为当前有支持的四省区，而不是整个SW。

共同CA端点也存在支持问题：共同P25/P75为`0.030048/0.510907`，在SW分布中分别约处于第66.7和第96.8百分位；SW的高暴露十分位内只有22行满足`CA≥0.510907`。因此，SW高SR端点主要依赖线性外推。共同端点可以保留为预设主比较，但必须报告每区端点百分位、联合`CA × HDD`支持和region-specific端点敏感性；在缺少该审计前不能把五区差异解释为真实产区异质性。

### Major 4：计划规定的主推断尚未执行，现有p值和CI不能作为投稿主推断

当前只有grid-cluster协方差，尚缺2°空间块wild bootstrap 1,999次、100/200/300 km空间HAC、五区与物候联合协方差、Romano–Wolf stepdown及Holm复核，也没有Stata点估计与SE复算。30个产量对比、20个LOYO结果、10个SM状态和10个SM通道结果同时报告而未处理多重检验。空间相关可能显著改变当前NE、HHH和NW的区间，尤其四年面板的LOYO只能诊断方向，不能替代空间推断。完成上述推断和跨软件容差核验之前，所有显著性只能标为初步grid-cluster结果。

### Major 5：逐日HDD不是`CalExposure.m`公开算法的数值近似

公开`CalExposure.m`对逐小时生育期矩阵统计`phase_data >= threshold`的小时数，输出`exposure_hours/24`和暴露小时占全部生育期小时的比例；它不计算阈值以上温度积分。当前主变量则为`sum(max(daily Tmax - threshold, 0))`，次变量为日最高温达到阈值的天数。逐日Tmax既无法恢复一天中超过阈值的持续时长，也无法恢复逐小时超温强度，因而这两个变量应称为“外生阈值下的daily-Tmax exposure”，不能称为公开CalExposure算法的移植或其可验证近似。

执行报告已经明确写出`not_hourly_replication`，这一边界表述是正确的；但稿件若引用该文献的方法贡献，必须二选一：使用逐小时输入按公开代码计算原暴露，或者把当前日尺度指标明确写成新的测量选择，并在可获得的小时样本上报告测量误差/排序一致性。外生阈值来源可靠不等于日尺度暴露定义已由原论文验证。

### Major 6：LOYO稳定性存在一处确定的报告错误，SM状态模型还缺少共线性诊断

`loyo_results.csv`与全样本主交互逐区复核得到NE 3/4、HHH 4/4、NW 4/4、SH **2/4**、SW 2/4；执行报告把SH写为3/4。SH四折符号依次为负、正、负、正，必须更正。SM状态模型虽为38/38满秩，但condition number为7,624.5，远高于产量模型296.9—474.4；condition number受量纲影响，不能直接证明共线性，但必须报告标准化设计下的VIF或等价诊断，特别是`CA × HDD × antecedent SM`全部低阶项，才能判断状态反转是否由弱支持或共线性放大。

## 三、次要问题

1. 现有10项测试覆盖窗口、日暴露、SM摘要、双FE去除和两方交互列，但没有覆盖三方状态端点、已知系数恢复、GeoTIFF边界映射、NetCDF单位/日历、线性组合、manifest和图表数据映射；本轮发现的`p50`键覆盖正是现有测试无法发现的类型。
2. runner依赖输入哈希，但没有显式断言Tmax单位为摄氏度、SMrz单位为`m3 m-3`及cube维度顺序。现场元数据分别为`°C`和`m3.m-3`，本次计算单位正确；仍应把单位核验写入代码和manifest。
3. 图1和图2使用`external_continuous`、`fixed_32c`、`full_ext`、`v3he`和`hema`内部代码作为横轴标签，缺少CA端点、HDD端点、样本量和“grid-cluster初步区间”的图内或配套图注，不符合投稿图的自解释要求。
4. 图3标题“channel-consistent associations”在NE、NW、HHH、SH方向相互冲突的情况下仍带有机制一致性暗示，建议改为中性的“conditional SMrz response contrasts”；机制判断应由预先规定的有利方向和联合检验决定。

## 四、评分

| 维度 | 得分 | 审稿依据 |
|---|---:|---|
| 创新与期刊匹配 | 16/20 | 连续地区阈值、物候和SM状态组合具有方法新意，但日尺度暴露不是公开小时算法，且当前没有共同的损害缓冲主张 |
| 数据和五区支持 | 10/20 | 输入身份、日期和坐标核验充分，五区均有输出；SW最终只保留50.11%且四川完全缺失，共同CA P75在SW支持很弱 |
| estimand与识别边界 | 10/20 | 主交互代数、grid FE和province×year FE实现正确，报告也意识到损害前提；但四区基础斜率为正，buffer命名与实质estimand不一致 |
| SM构念及时序 | 6/15 | 前置14日和窗口内SM时序合理、未作因果中介表述；SM状态端点存在跨单位键覆盖，状态表必须重算 |
| 精度与稳定性 | 7/15 | grid聚类和LOYO已运行；空间主推断、多重检验、HAC、Stata复算未完成，且SH LOYO计数写错 |
| 可复现性和图表完整性 | 8/10 | manifest、哈希、CSV恒等式和三图对应关系良好；测试面未覆盖状态端点和runner关键接口，图注仍非投稿规格 |
| **总分** | **57/100** | 显著性不计加分 |

## 五、必须修改后才可提交Round 2的项目

1. 修复三方状态端点键覆盖，增加回归测试，重新运行SM状态模型并更新所有受影响数值。
2. 将`damage/buffer`机器字段、表题和图题改为中性条件变化名称；主表同时报告低SR与高SR斜率，明确当前结果不支持五区共同热害缓冲。
3. 更正SH LOYO为2/4，并由脚本自动生成LOYO同向折数，避免手工转录。
4. 补充五区和省级样本漏斗、四川完全缺失说明、最终/原分母比例、纳入排除比较、阈值空间覆盖和共同CA端点联合支持审计。
5. 明确选择小时CalExposure复现或日尺度新指标路线；若保留日尺度路线，不得使用“严格移植EDD算法”表述，并增加小时—日尺度测量一致性证据或将其列为未验证限制。
6. 完成2°空间块wild bootstrap、空间HAC、Romano–Wolf/Holm和Stata复算；五区和物候主检验必须使用同一次bootstrap联合协方差。
7. 对38列SM状态设计报告标准化VIF/条件指标，新增已知系数、三方端点、单位、映射、线性组合和runner manifest测试。
8. 重新生成三幅投稿候选图，使用可读窗口名称、完整图注和明确的初步/最终推断标识；SM图使用中性标题。

## Round 1最终判定

**REVISE，57/100，未通过90分且无Critical/Major的稿件准入门槛。** 当前全量计算可保留为可复核探索run；在上述Major全部关闭前，不得生成“地区异质温度阈值证明SR缓冲热害”的小稿，也不得把覆盖门槛的用户豁免解释为对选择偏差、支持不足或推断缺口的豁免。
