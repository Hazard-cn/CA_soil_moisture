# `regional-threshold-sr-override-v1` Round 1 返修答复

## Material Passport

- Canonical ID：`regional-threshold-sr-override-v1`
- 原审稿记录：`repo://quality_reports/plans/2026-07-15_regional_threshold_override_method_review_round1.md`
- 返修后全量 run：`local://temp/2026-07-15_regional_threshold_daily_override_full_v2/`
- 返修方式：新建 full_v2，不覆盖 `full_v1`；原始审稿记录和原执行报告均保持不变
- 返修后验证状态：`PASS`，13项机器检查无失败；是否通过稿件准入门槛由原方法审稿代理 Round 2 独立判定
- 解释边界：结果只识别外生连续阈值下的日最高温暴露与产量、SMrz之间的条件相关结构；不识别因果中介，也不支持五区共同的“SR缓冲热害”结论

本答复逐项处理Round 1提出的6项Major和4项Minor。用户取消的是原80%覆盖率阻断规则，未取消样本选择、共同端点支持、推断和测量误差的披露要求；因此，四川完全退出逐日Tmax样本、SW共同CA P75支持弱以及缺少逐小时一致性样本仍作为明确限制保留。

## 一、Major问题答复

### Major 1：SM状态端点跨单位键覆盖

**处理状态：已修复并全量重算。**

`scripts/python/regional_threshold_daily_core.py`不再合并两个含有`p50`的字典，而是返回五个不重名字段：`exposure_p50_cday`、`exposure_p90_cday`、`state_p25_m3m3`、`state_p50_m3m3`和`state_p75_m3m3`。`sm_state_results.csv`同时保留暴露端点、状态端点和单位后缀；测试新增跨单位键冲突检查。

重算后的全季P25/P75前置SM状态下高SR减低SR条件斜率差为：NE `-0.13633/0.09044`，HHH `0.11871/0.14259`，NW `-0.00332/0.08483`，SH `0.01142/0.04551`，SW `0.00090/0.01765`。这些是使用各区正确的暴露P90减P50得到的新结果，旧run中的10行状态结果不再被引用。

核查位置：

- `repo://scripts/python/regional_threshold_daily_core.py`
- `repo://tests/test_regional_threshold_daily_core.py`
- `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/sm_state_results.csv`

### Major 2：损害缓冲语义预设

**处理状态：已修复字段、表述和图形；实质性限制保留。**

机器结果字段已统一改为`conditional_yield_change_low_sr`、`conditional_yield_change_high_sr`和`high_minus_low_sr_slope_contrast`，代码、CSV、manifest和三幅结果图不再使用`damage`或`buffer`作为估计量名称。图1和图2同时展示低SR、高SR条件产量变化及两者之差，而不是只展示差值。

全季外生阈值结果仍显示：NE、HHH、NW和SW的低SR条件变化为正，只有SH的低SR和高SR条件变化均为负，而SH差值的2°空间块wild-bootstrap区间跨0。因此，返修没有通过更换窗口、阈值或样本寻找更有利结果；公开解释仍限定为地区异质条件斜率结构，不形成五区热害缓冲结论。

核查位置：

- `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/yield_results.csv`
- `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/fig1_conditional_yield_changes.png`
- `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/fig2_conditional_yield_changes_by_window.png`

### Major 3：SW样本选择、四川退出和共同CA端点支持

**处理状态：样本审计已补齐；无法恢复的支持限制保留。**

新增五区和省级四阶段漏斗、纳入与排除样本对比、空间覆盖图以及CA×HDD联合支持表。五区从阈值前样本到模型complete-case的保留率为：NE `94.72%`、HHH `98.15%`、NW `84.49%`、SH `98.79%`、SW `50.11%`。阈值有效的四川3,570行、1,295个grids因逐日Tmax全年masked而全部退出；SW估计对象因此明确限定为本次数据中具有有效逐日温度支持的云南、贵州、广西和重庆样本，不代表含四川的完整西南产区。

共同CA P25/P75为`0.030048/0.510915`。这两个端点在SW区内分别约为第66.70和96.78百分位；SW高HDD十分位907行中，只有22行、21个grids达到共同P75，表明共同高SR端点主要依赖线性外推。作为不重新估计模型、不改变规格的端点敏感性，使用各区自身P25/P75后，全季差值为NE `-0.03205`、HHH `0.14940`、NW `0.06559`、SH `0.02224`、SW `-0.00027`；SW结果仍接近0，但该敏感性不消除目标总体变化和弱共同支持。

核查位置：

- `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/sample_funnel_zone.csv`
- `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/sample_funnel_province.csv`
- `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/sample_selection_comparison.csv`
- `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/ca_hdd_joint_support.csv`
- `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/fig4_sample_coverage_map.png`

### Major 4：空间主推断、多重检验和跨软件复算

**处理状态：已完成。**

返修后主推断使用同一次2°空间块Rademacher multiplier wild bootstrap，空间块数162，1,999次，seed 42；15个外生阈值“产区×物候窗口”差值共用联合bootstrap抽样和联合协方差。该方法是基于线性模型区块得分的一阶multiplier wild bootstrap，不是每次重拟合固定效应模型。主检验同时报告未校正bootstrap p、Romano–Wolf stepdown p和Holm p。

全季五区结果如下：

| 产区 | 差值 | Wild-bootstrap SE | 95%区间 | 未校正p | Romano–Wolf p | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| NE | -0.04031 | 0.03651 | [-0.10974, 0.02661] | 0.3010 | 0.8140 | 1.0000 |
| HHH | 0.12922 | 0.03811 | [0.05825, 0.20100] | 0.0005 | 0.0005 | 0.0075 |
| NW | 0.07202 | 0.03640 | [0.00291, 0.14327] | 0.0445 | 0.2300 | 0.5340 |
| SH | 0.02179 | 0.03251 | [-0.03811, 0.08107] | 0.5060 | 0.8140 | 1.0000 |
| SW | -0.00146 | 0.02472 | [-0.04520, 0.04393] | 0.9510 | 0.9510 | 1.0000 |

15项联合检验中只有HHH三个窗口通过两种家族错误率校正，但HHH低SR和高SR条件产量变化均为正，因此这些显著差值仍不能解释为负向热损害被缓冲。NW全季未校正p为0.0445，Romano–Wolf和Holm校正后均不通过。

空间HAC使用年内Conley Bartlett空间核并允许grid内跨年任意序列相关，带宽100/200/300 km。HHH在三带宽均保持正向且p不超过0.0002，NW约为0.020—0.022，NE约为0.072—0.132，SH和SW均不通过；这些HAC结果作为核验，不替代联合wild-bootstrap主推断。

Stata 18 `reghdfe`复算使用grid FE、province×year FE和grid聚类。Stata显式删除2,287个singleton grid观测，保留52,603行；Python输入为54,890行，但这些singleton对within估计没有贡献。18个系数最大绝对差`9.02×10^-16`，18个grid-cluster SE最大绝对差`4.93×10^-5`，分别通过项目`0.01/0.05`容差。

核查位置：

- `repo://scripts/python/regional_threshold_inference.py`
- `repo://scripts/stata/verify_regional_threshold_override.do`
- `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/wild_bootstrap_primary_results.csv`
- `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/wild_bootstrap_joint_covariance.csv`
- `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/spatial_hac_primary_results.csv`
- `local://temp/2026-07-15_regional_threshold_daily_override_full_v2/stata_python_replication_comparison_round1.csv`

### Major 5：日尺度暴露与公开小时算法的关系

**处理状态：选择日尺度独立测量路线；小时一致性限制保留。**

manifest将主变量定义为`sum(max(daily Tmax - external continuous threshold, 0))`，测量角色固定为“独立的daily-Tmax exposure”，不再将其称为`CalExposure.m`逐小时超阈值时长算法的移植、复现或近似。公开小时算法仍只用于说明相关文献存在空间异质阈值测量思想，不能验证本项目日尺度暴露的数值性质。

本轮没有可同时计算小时指标和日尺度指标的共同小时样本，故小时—日尺度排序或测量误差验证未执行，manifest明确登记为`NOT_PERFORMED_NO_COMMON_HOURLY_SAMPLE`。这项未完成内容是测量限制，而不是以其他数据或定义替代。

### Major 6：LOYO转录和SM状态共线性诊断

**处理状态：LOYO已由脚本生成并更正；共线性诊断已补充。**

LOYO同向折数现在直接从20行fold结果生成，结果为NE 3/4、HHH 4/4、NW 4/4、SH 2/4、SW 2/4；原报告中的SH 3/4不再沿用。四折LOYO只作为方向稳定性诊断。

SM状态设计经within变换后标准化，最大VIF为`5.8786`，来自降水平方项；降水水平项为`5.8523`，最大的状态交互VIF为SW暴露×前置SM `5.2511`。标准化条件数为`5.9269`，原始条件数7,624主要受变量量纲影响。该结果不显示普遍严重的共线性，但三个VIF略高于预设5，SM状态结果仍按敏感构造处理，不升级为稳定机制证据。

## 二、Minor问题答复

### Minor 1：测试覆盖不足

新增并扩展三个测试文件，当前共18项测试，覆盖三方状态端点及单位、人工已知系数恢复、PixelIsArea边界映射、NetCDF单位/维度/日期、线性组合恒等式、bootstrap确定性、Romano–Wolf/Holm取值边界和runner输出契约。`python -m unittest tests.test_regional_threshold_daily_core tests.test_regional_threshold_inference tests.test_regional_threshold_runner_contract -q`为18/18通过。

### Minor 2：输入单位和cube维度没有显式断言

runner现已对Tmax变量、摄氏度单位、`time/lat/lon`维度及公历日轴进行显式检查，也对GLEAM SMrz变量、`m3.m-3`单位、维度和日期进行断言；检查结果写入manifest。GeoTIFF同时登记CRS、分辨率、PixelIsArea、nodata、边界、有效值范围及MD5/SHA-256。

### Minor 3：图内内部标签和信息不足

图1—图4均重新生成，窗口名称改为可读名称；图1和图2展示低SR、高SR条件变化及差值，配套数据包含CA端点、暴露端点、样本量和最终推断。四幅图均为白底、无衬线字体、3,600×1,500像素、约300 DPI。图形文件保存在temp，不进入Git。

### Minor 4：SM图标题含机制一致性暗示

图3标题改为中性的`Conditional GLEAM SMrz response contrasts`，不再使用`channel-consistent`。当前SM方向在五区之间不一致，只报告条件响应差异。

## 三、返修后验证

`round1_post_validation_manifest.json`记录13项检查全部通过，包括中性字段、恒等式、端点单位、LOYO脚本生成、Stata/Python容差、2°联合bootstrap、三带宽HAC、Tmax和SMrz单位/日期、GeoTIFF身份及四幅图尺寸。full_v2 manifest冻结的关键代码哈希为：runner `10b44b0242dc6397d1bcff37ef5a55396d250f0dc845fcab26c9e656db0e01fb`，core `5abb61f87337df250631126957b7bbb0cf55cce5e28c1f9d5956486254f6d81b`，inference `256de80606c4bf27c212dfe57bc378ff30d7b6c53ea0f5aff0a32f6db12b8193`。

官方`maize.tif`在本run登记的MD5为`0d9e6c21bf1b25f113e14315863372f2`，SHA-256为`f05e634664c4c6c2e2df352702acd421507162bc54cc067649071521ab1285b0`；格式为float32 GeoTIFF，514×76，EPSG:4326，PixelIsArea，0.5°，有效值5,627个，范围26.8—44.0°C。

## 四、请求Round 2审查的判定边界

本轮请求原方法审稿代理重新核查6项Major和4项Minor是否关闭。返修没有提出“地区异质阈值证明SR缓冲热害”的主张；如果稿件准入要求五区共同负向损害前提、完整SW总体或有共同小时样本的暴露一致性证据，则该方向应按结果不支持或测量限制处理，而不是继续搜索更有利规格。若允许将稿件问题调整为“地区异质阈值下SR条件斜率的区域差异及其支持边界”，则是否达到90分由Round 2按既定评分体系决定。
