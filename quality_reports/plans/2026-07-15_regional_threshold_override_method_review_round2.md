# 地区异质温度阈值方向：独立方法复审（Round 2）

**Canonical ID：** `regional-threshold-sr-override-v1`
**复审对象：** `2026-07-15_regional_threshold_override_full_v2_report.md`、Round 1 返修说明、当前代码、测试与 `temp/2026-07-15_regional_threshold_daily_override_full_v2/` 冻结机器输出
**复审角色：** 独立方法审稿；只读核验，不改写代码、机器结果、执行报告或公开谱系
**复审轮次：** Round 2（本方向最多两轮方法审查中的最后一轮）

## 一、最终判定

**判定：`FAIL / REVIEWED_NOT_CANDIDATE`。**
**评分：72/100。**
**未解决问题：0 Critical，3 Major，4 Minor。**

Round 1 后，SM 端点单位覆盖错误、结果变量语义、日尺度暴露与 CalExposure 的边界、LOYO 方向计数、VIF/条件数、2°空间块 wild bootstrap、Romano–Wolf/Holm、空间 HAC 以及 Stata 复算均有实质修正或补充，机器结果也具有较强的哈希和复算证据。但是，冻结结果不能支持“SR 缓冲温度损害”这一核心解释：五区中四区的低 SR 条件产量变化为正，唯一同时为负的华南区高低 SR 差异又缺乏精度；黄淮海显著为正的高低 SR 斜率差出现在低、高 SR 条件变化均为正的情形，不能解释为负损害被缓冲。与此同时，SM 证据仍未接受与主产量结果同等级的空间推断和多重检验，预设物候边界敏感性与阶段联合检验没有完成，公开主图仍展示初步 grid-cluster 区间而非主推断的 wild-bootstrap 高低 SR 对比。上述问题使该方向不能进入投稿候选集。

本判定不恢复用户已经取消的样本覆盖停止门槛，也不以统计显著性本身评分；西南缺失四川和共同 CA 端点支持偏弱被作为适用范围及外推限制处理。失败依据是冻结 estimand 的实质含义与预设研究问题不一致，以及预设推断链条和主图尚不完整。依两轮上限，本方向不进入 Round 3，不再通过改阈值、窗口、样本、函数形式或其他规格搜索候选结论；现有产物应保留为带完整非显著结果的已审查失败报告。

## 二、Round 1 问题关闭矩阵

| Round 1 问题 | Round 2 核验 | 状态 |
|---|---|---|
| Major 1：SM endpoint 的 `p50` 被暴露 P50 覆盖，导致单位错误 | `regional_threshold_daily_core.py` 已分离 `exposure_p50_cday`、`exposure_p90_cday`、`state_p25_m3m3`、`state_p50_m3m3`、`state_p75_m3m3`；runner 分别使用暴露差与 SM 状态差。冻结 SM 结果与修正后的端点运算一致 | **Closed** |
| Major 2：把条件产量变化统称为 damage/buffer | 输出字段已改为 `conditional_yield_change_low_sr`、`conditional_yield_change_high_sr`、`high_minus_low_sr_slope_contrast`，代码和主报告不再把代数差直接命名为损害或缓冲 | **Closed at naming level; substantive interpretation remains Major A below** |
| Major 3：西南样本选择、四川缺失和共同端点缺乏披露 | 漏斗表、地图、共同端点分位位置及区域端点敏感性已提供；四川在最终日温度 complete-case 中为 0，西南最终样本限于云南、贵州、广西和重庆；共同 CA P75 在西南约为第 96.78 百分位，高 HDD 端仅 22 行达到该端点 | **Closed as disclosure; permanent external-validity limitation** |
| Major 4：缺少主空间推断、多重检验、HAC 和 Stata 复算 | 15 个五区×三窗口产量高低 SR 对比已用同一组 1,999 次、seed 42、162 个 2°块 Rademacher multiplier draws 构造联合协方差，并报告 Romano–Wolf 与 Holm；全季对比有 100/200/300 km HAC；Stata 与 Python 18 个系数最大差 `9.02e-16`、SE 最大差 `4.926e-05` | **Partly closed; SM 和预设物候推断仍未完成，见 Major B** |
| Major 5：把日 Tmax HDD 表述为 CalExposure 算法的复现 | 当前代码和报告明确将日尺度阈值以上 degree-days 作为独立度量，并登记 `NOT_PERFORMED_NO_COMMON_HOURLY_SAMPLE`，不再声称与小时级 CalExposure 等价 | **Closed by corrected scope** |
| Major 6：华南 LOYO 计数错误及 SM 共线性诊断不足 | LOYO 已重算为东北 3/4、黄淮海 4/4、西北 4/4、华南 2/4、西南 2/4；最大 VIF 为降水平方项 5.879，最大 SM 状态交互 VIF 为西南 5.251，标准化条件数约 5.927，并已披露 | **Closed** |
| Minor 1：测试覆盖不足 | 三个测试模块共 18 项全部通过；另有运行后验证和哈希清单。但单元测试并未覆盖 HAC 数值、空间块 score 聚合、图表主推断一致性等返修信中声称的全部范围 | **Partly closed，见 Minor 3** |
| Minor 2：单位/维度断言不足 | runner 增加 NetCDF 单位与维度检查，暴露和 SM 字段单位已显式区分 | **Closed** |
| Minor 3：图表标签未区分初步推断与主推断 | 图 1、图 2 已明确写为 `preliminary grid-cluster CI`，避免把它伪装成主空间推断；但两图仍未呈现 primary wild-bootstrap 的高低 SR 对比，返修信称其包含“两者之差”与实际图形不符 | **Open，升级并合并至 Major C** |
| Minor 4：SM 图题带有机制断言 | 图 3 已改为中性的 `Conditional GLEAM SMrz response contrasts` | **Closed** |

## 三、独立机器核验

### 3.1 可复现性与文件完整性

运行 `python -m unittest tests.test_regional_threshold_daily_core tests.test_regional_threshold_inference tests.test_regional_threshold_runner_contract -v`，18/18 项通过。`run_manifest.json` 所登记的输出文件字节数与 SHA-256 全部匹配；当前 runner、core、inference 脚本的哈希也与 manifest 一致。运行后验证清单为 PASS，13 项验证对应文件的字节数和哈希均匹配。上述证据支持“当前报告所引用的机器输出没有在审查后被静默替换”，但不能替代对 estimand 和推断设计的独立审查。

### 3.2 主空间推断复算

wild-bootstrap draws 为 1,999×15，报告 SE 可由 draws 完全复算，15×15 联合协方差的最大绝对误差约为 `9.6e-17`；未调整 p 值、Romano–Wolf stepdown 和 Holm 值的独立复算均与输出一致。全季五区主要对比为：

| 产区 | 高 SR − 低 SR 斜率对比 | 95% wild-bootstrap CI | Romano–Wolf p |
|---|---:|---:|---:|
| Northeast | -0.0403 | [-0.1097, 0.0266] | 0.814 |
| Huang-Huai-Hai | 0.1292 | [0.0582, 0.2010] | 0.0005 |
| Northwest | 0.0720 | [0.0029, 0.1433] | 0.230 |
| South China | 0.0218 | [-0.0381, 0.0811] | 0.814 |
| Southwest | -0.0015 | [-0.0452, 0.0439] | 0.951 |

黄淮海三个物候窗口的对比通过联合多重检验，西北全季未调整 p 值约为 0.0445，但 Romano–Wolf 为 0.230、Holm 为 0.534。该结果说明空间联合推断已按主结果执行，且没有把未调整单项显著误报为多重检验后的证据。

### 3.3 条件变化语义

全季低 SR 条件产量变化依次约为东北 `+0.0580`、黄淮海 `+0.5822`、西北 `+0.0550`、华南 `-0.1115`、西南 `+0.0317`。因此，黄淮海的正高低 SR 差异是两条均为正的条件斜率之间的差，并不是“更高温度暴露导致负产量变化，而高 SR 使该负变化减弱”。华南是唯一低、高 SR 条件变化均为负的区域，但其高低 SR 差异区间跨 0。代码、Stata 复算与主表没有发现符号翻转错误；这是冻结模型的实质结果，而非展示问题。

### 3.4 样本与共同端点

五区从阈值前模型 complete-case 到最终样本的保留率分别约为东北 94.72%、黄淮海 98.15%、西北 84.49%、华南 98.79%、西南 50.11%。四川阈值前有 4,219 行、外生阈值匹配后 3,570 行，但最终日温度 complete-case 为 0，因此主结果不能外推为包含四川的完整西南玉米区证据。全样本共同 CA 端点约为 P25 `0.030048`、P75 `0.510907`；在西南中，该共同 P75 位于约第 96.78 百分位，且高 HDD 区间仅有 22 行、21 个 grids 达到或超过共同 P75。图 4 准确显示了四川和西南日温度缺失，是有效的样本选择证据；该图应随失败报告保留。

## 四、未解决 Major

### Major A：冻结 estimand 不支持预设的“SR 缓冲温度损害”解释

主模型的条件变化在五区中的四区为正，黄淮海的稳定正高低 SR 对比也建立在低、高 SR 条件变化均为正的基础上。仅凭交互或高低 SR 差为正，不能在基准温度变化本身不是损害时称为“缓冲损害”。将稿件改写为“SR 对阈值以上日尺度温度暴露条件相关性的异质修饰”能够保持统计描述正确，但这已经不再回答冻结的缓冲研究问题，也不能作为当前优先投稿方向的等价替代。两轮后不得再以改端点、改窗口、改样本或选择区域来寻找满足缓冲叙事的规格。

### Major B：SM 与物候推断链条没有完成预设分析

主产量结果已使用 2°空间块联合 wild bootstrap 和多重检验，但 10 个 SM 状态结果及 10 个 SM 通道结果仍只报告 grid-cluster 推断，没有与产量结果同等级的空间块联合协方差、Romano–Wolf/Holm 或空间 HAC 核验。由于 SM 是本方向的必含状态/通道证据，当前证据不足以承担当机制相关结论。预设物候分析还要求阶段 SR 交互的联合 Wald 检验，并要求窗口边界 ±7 日和 ±14 日敏感性；冻结 v2 未提供这两类结果，因而无法执行预设的“结果系统反向则降为附录”判据。现有逐窗口单项对比及联合多重检验不能替代阶段联合 Wald 和日期边界敏感性。

### Major C：公开主图没有呈现主推断 estimand

图 1、图 2 的标题均明确为 `preliminary grid-cluster CI`，视觉内容只包含低 SR 与高 SR 的条件变化及 grid-cluster 区间，没有显示高 SR − 低 SR 的对比，也没有使用 1,999 次 2°空间块 wild-bootstrap 区间。Round 1 返修信称两图呈现低、高 SR “及两者之差”，与实际代码和图形不一致。将初步分组点估计图作为机器诊断图可以接受，但不能作为以高低 SR 对比为主 estimand、以空间 wild bootstrap 为主推断的公开主图。冻结包因此没有达到计划要求的主结果图表完整性。

## 五、未解决 Minor

1. full-v2 报告把 `58,464` 行写成“阈值前五区 complete-case”；该数实际为外生阈值有效行数，阈值前五区 complete-case 总数为 `66,396`。后续分区保留率使用的是正确分母，但总量标签需要视为报告错误。
2. 主报告/返修信使用共同 CA P75 `0.510915`，实际 yield model CSV 使用 `0.510907`；差异约 `8e-06`，来自窗口展开后重复观测上的分位数插值，不影响数值结论，但单一 estimand 应引用实际模型端点。
3. 返修信对自动化测试覆盖范围有夸大：18 项测试和运行后验证能覆盖端点、单位、固定效应、基本 bootstrap/RW/Holm 函数及文件一致性，但没有单元测试 HAC 数值、空间块 score 聚合、图表与 primary estimand 的一致性。
4. wild-bootstrap 区间由点估计加中心化 draws 的经验分位数构造；报告没有明确说明这一有限重复次数下可能产生轻微非对称的实现细节。独立复算未发现数值错误，但方法说明应精确到区间构造规则。

## 六、固定评分

| 维度 | 满分 | 得分 | 复审依据 |
|---|---:|---:|---|
| 创新与期刊匹配 | 20 | 15 | 外生连续区域阈值与五区异质性有方法价值；冻结结果不能支持缓冲主张，稿件贡献需要降格重述 |
| 数据和五区支持 | 20 | 14 | 五区均有估计结果并完整披露漏斗；西南缺四川、共同 P75 极端且高暴露端支持稀疏，限制完整产区解释 |
| estimand 与识别边界 | 20 | 13 | 结果字段与非因果边界已纠正；核心条件变化的方向不允许解释为损害缓冲 |
| SM 构念及时序 | 15 | 10 | endpoint 单位 bug 已修复，antecedent/current/change 构造和 VIF 已披露；空间联合推断与多重检验未完成 |
| 精度与稳定性 | 15 | 12 | 产量 wild bootstrap、RW/Holm、HAC、LOYO 和 Stata 复算较完整；物候边界和阶段联合检验缺失，只有黄淮海达到多重检验后的精度 |
| 可复现性和图表完整性 | 10 | 8 | 哈希、manifest、18 项测试和运行后核验较强；主图仍是 preliminary grid-cluster，未展示 primary contrast/wild-bootstrap CI |
| **总分** | **100** | **72** | **低于 90，且仍有 3 个 Major** |

## 七、两轮上限后的处置

该方向在 Round 2 后终止候选稿流程，正式标记为 **`REVIEWED_NOT_CANDIDATE`**。现有执行报告、完整主表、所有非显著结果、样本漏斗、图 4 选择地图、哈希清单及本复审意见应原样保留，以便复核；不得删除或覆盖。不得启动 Round 3，不得通过阈值、窗口、样本、区域、函数形式或推断方式搜索更有利规格，也不得把黄淮海正对比重新包装为“缓冲”。如项目未来提出不同于本方向的新研究问题，应建立新的 canonical ID、独立设计冻结和新一轮审核，不能沿用本方向的候选状态。
