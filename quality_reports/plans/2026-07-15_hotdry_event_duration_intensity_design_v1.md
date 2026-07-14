# 热干事件强度—持续时间与SR缓冲：设计包v2

## 状态与研究边界

- Canonical ID：`compound-event-intensity-duration-v1`。早期工作名 `hotdry-event-sr-v1` 只作为alias登记，不得用于run、manifest或公开目录。
- 当前阶段：`DESIGN_REVIEW_REQUIRED`
- 允许的下一步：只读数据支持审计。独立方法审查达到90分且无Critical/Major并明确给出 `PASS_DESIGN` 后，才允许小样本smoke；smoke结果另经独立审查通过后才允许完整产量模型。
- 研究问题：在固定的日尺度热干事件定义下，较高观测SR是否与较低的持续时间损害和强度损害相关，这些条件关联是否跨五个玉米产区一致，是否伴随更小的GLEAM根区土壤水分下降或更短的恢复时间？

全文只使用“条件损害差异”“通道一致证据”“恢复关联”。2016—2019只有四年，不能把grid固定效应和province×year固定效应下的估计写成已识别因果效应；GLEAM事件通道也不能写成因果中介。

## 文献与代码依据

37篇代码库中，Kuwayama等的固定效应框架将极端事件的持续时间和强度作为可分离暴露，并报告联合向量和区域差异；Zotero本地条目为 `GVC6XC5J`、全文附件为 `EM4662HK`。Bogenreuther等区分绝对/相对阈值、复合日以及全季、营养生长和生殖生长窗口；Zotero条目为 `ZS7TKPCV`、全文附件为 `EGZ3IE4R`。本方向只借鉴预先定义事件、分离强度与持续时间和分窗口报告，不从这些文献移植不同作物或不同数据生成过程中的系数。

执行前三层核验已经冻结在 `quality_reports/plans/2026-07-15_hotdry_event_literature_verification_matrix.md`。Kuwayama的官方补充端点返回HTTP 403，Bogenreuther只识别到数据而没有代码归档；因此本方向只能称“借鉴全文方法”，不能称“复刻公开代码”。

## 输入、日历与空间映射

面板使用 `data_build/data/processed/data_v3_main.dta`，其SHA-256为 `3f3f045a8040b876565873febab3918d166b8bd6f6938669b48c634a46172517`。日最高温使用 `external://daily_temp_CN/daily_temp_{year}.nc` 中 `t2m_max`，单位°C；降水主输入使用已经对齐温度格网的 `external://Processed_Panel_CN_2016-2019/PRE_0.1deg/CHM_PRE_0.1deg_{year}.nc` 中 `pre`，单位mm/day；根区土壤水分主输入使用 `external://Processed_Panel_CN_2016-2019/GLEAM_SM_0.1deg_TEMPgrid_2013_2019/GLEAM_SM_0.1deg_TEMPgrid_{year}.nc` 中 `SMrz`，单位m3/m3。原始 `external://CHM_PRE_0.1dg_19612022.nc` 与 `external://GLEAM_soil-mositure/SMrz_{year}_GLEAM_v4.2b.nc` 只作上游provenance，不直接进入事件识别。2016—2019全部分析输入必须登记bytes、MD5与SHA-256。

所有日期以公历日期连接，不能只按数组位置连接。2016闰年必须有366天，2017—2019必须各有365天；温度、对齐降水和对齐SM必须验证日期单调、无重复。三个逐日对齐产品的376×616坐标数组必须逐值完全相同；V3因Stata float32坐标存储允许与唯一参考格网中心相差至 `1e-5` 度，超过即停止，不再次做nearest。只读预审计得到V3到参考中心的最大纬度/经度差为 `1.8311e-6`/`7.3242e-6` 度。原始CHM-PRE与原始GLEAM中心相对温度格网约偏移0.02°/0.03°，故禁止直接把原始格网伪装成精确匹配；使用上述对齐产品是冻结的数据定义，不是结果导向补救。必须随机抽查至少每年每区20个grid-days，并登记原始索引、坐标和值。

确认性事件窗口为项目既有“扩展V3—成熟窗口”：`v3_doy-30 <= doy <= ma_doy`。它不是严格播种至成熟，主文不得简称完整生育季。严格 `v3_doy <= doy <= ma_doy` 只作预设窗口敏感性，不搜索其他起止日。

## 事件识别与grid-year指标

对每个grid-year-window，定义日热干标记：

\[
C_{itd}=1(Tmax_{itd}\ge 32^\circ C\ \land\ Pre_{itd}<1\text{ mm/day}).
\]

事件是窗口内连续至少3个 `C=1` 日组成的最大连续段。窗口边界截断连续段，窗口外日期不能把窗口内1—2日片段补成事件。温度或降水缺失会中断连续段，不能当作不满足条件的有效观测；主支持审计另外报告有效日覆盖。

每个grid-year机械生成：事件数、合格事件总天数、最长连续期、所有合格事件日的平均超温 `mean(max(Tmax-32,0))`、累计超温 `sum(max(Tmax-32,0))`，以及当前事件窗口内全部热日 `Tmax>=32` 中同时 `Pre<1` 的比例。无合格事件时，事件数、总天数、最长连续期、平均超温和累计超温均置0，并保留 `event_indicator=0`；若当前事件窗口没有热日，热日干旱同期比例为null。

`event_panel`键为 `grid_id year event_seq`。事件ID固定为UTF-8字符串 `grid_id|YYYY|event_seq`，其中year为四位整数、event_seq无前导零。有事件的grid-year每个事件一行，`event_seq`从1连续编号；第1行标记 `is_grid_year_representative=true`，其余事件行标记false。为保持单一记录契约，所有事件行复制同一组grid-year聚合指标；产量回归只能使用代表行。无事件grid-year保留一行 `event_seq=0`、`event_id=null`、`is_grid_year_representative=true`。

## 土壤水分状态、下降与恢复

每个事件的初始状态为onset前14日至前1日的GLEAM SMrz均值，并记录 `antecedent_valid_days`；“完整前置窗口”要求14/14日有效。事件期最低SM为onset至 `min(event_end+3, ma_doy)` 的最低值。下降定义为

\[
drawdown=antecedent\_smrz-event\_min\_smrz,
\]

正值表示事件期比初始状态更干，负值表示没有发生净下降。若 `event_end+3` 与下一事件重叠，仍按冻结窗口计算最低值，但设置 `drawdown_overlap_next_event=true` 并报告数量及排除重叠事件的敏感性。它是独立通道结果，不加入主产量方程后再解释为中介。

恢复目标为初始均值的90%。风险集离散日为 `t=0,...,30`：事件结束日已经达到目标时 `recovery_days=0`；否则从结束后第1日起查找首次 `SMrz>=0.9×antecedent_smrz`。`recovery_days`是统一的生存时间变量：已恢复事件记录首次恢复日，右删失事件记录最后一个仍在风险集的随访日，两者都在0—30之间，并由 `recovery_observed` 区分。恢复跟踪在下一事件onset、`ma_doy`、数据结束或30日上限处右删失；下一事件onset当天不计为可恢复日，删失原因分别记为 `next-event`、`ma-end`、`data-end` 或 `thirty-day-limit`。SM缺失不能被线性插值；缺失使首次恢复不可确定时标记 `insufficient-sm`，此时 `recovery_observed/right_censored/recovery_days`均为null，该类事件在恢复模型前complete-case排除，不由IPCW补偿。事件结束后30日内的完整日历记录、删失原因与风险集必须保留。

恢复分析使用事件为单位，但推断按2°空间块重抽样以处理同一grid多事件相关。删失IPCW在事件—日风险集上用pooled logit估计：分母模型含日虚拟变量、连续 `ca`、五区、year、antecedent SM、事件duration、事件mean intensity、onset DOY及 `ca×zone`；分子模型只含日虚拟变量、五区和year。所有变量在随访开始时已知。稳定权重为逐日未删失概率的分子/分母累积乘积，在1%与99%预设截尾；同时报告未截尾权重、有效样本量、最大值和99分位。若99分位超过50或任一模型分离，恢复结果STOP。

恢复结果模型为IPCW加权pooled complementary-log-log离散hazard，含日虚拟变量、连续 `ca`、五区、year、antecedent SM、duration、mean intensity、onset DOY和 `ca×zone`。对每区分别把CA设为五区共同恢复样本P25/P75，其余事件协变量按该区事件的经验分布事件等权标准化，得到 `S_z(t|CA)=P(T>t)`；`RMST30=sum_{t=0}^{29}S_z(t)`，较小RMST表示更快恢复。缺失SM排除只作complete-case边界，不由IPCW覆盖。曲线和RMST的空间块bootstrap使用与产量模型相同的全国块权重向量。

## 主产量模型与estimand

主结果固定为 `ln_yield`，SR变量固定为 `ca`，控制固定为 `gdd_10_29`、`pr_sum` 和机械生成的 `pr_sum_sq=pr_sum^2`。complete-case字段全集为 `grid_id year province latitude longitude ln_yield ca gdd_10_29 pr_sum v3_doy ma_doy` 以及对应事件暴露。五区按 `scripts/stata/v3sub_step0_subsamples.do` 第18行起的省份映射生成，该脚本SHA-256为 `bb2b4c379486cf6a315f610710f2e688b2a3067aa0de729a015a7c5f2b456e3a`。

对暴露 `E`（分别为total duration和mean intensity），合并完全交互方程固定为 `ln_yield = grid FE + province×year FE + gdd_10_29 + pr_sum + pr_sum_sq + sum_z 1(zone=z)×[beta_z E + gamma_z ca + delta_z(ca×E)] + error`。zone主项被grid FE吸收，不另行解释；所有五区的 `E`、`ca` 与 `ca×E` 列均保留并检查秩。持续时间和强度各自为独立主模型。联合模型先对duration和intensity按主样本执行FWL残差化，吸收固定效应、控制、zone-specific CA和两项暴露的全部非交互低阶项；两项残差暴露VIF都小于5、完整联合交互块满秩且标准化条件数小于30时，联合模型才进入主结果，否则降为附录且不得替代两个独立主模型。

每个模型的CA端点为五区共同主样本P25/P75；暴露端点为各区P50/P90。每区估计量固定为 `B_z={m_z(CA75,E90)-m_z(CA75,E50)}-{m_z(CA25,E90)-m_z(CA25,E50)}`，在线性模型中等于 `delta_z×(CA75-CA25)×(E90-E50)`。正文统一报告 `100[exp(B_z)-1]%`：正值表示较高SR对应较小的暴露产量损害，负值表示较高SR对应更大的损害；机器表同时保留log-point。持续时间和强度分别冻结五个P50/P90端点。所有分位点在完整模型前写入manifest；无事件年份保留，使0暴露具有观测支持。

## 推断、异质性与稳定性

主区间使用2°空间块wild-score bootstrap，1,999次、seed 42，区块锚定全球原点：`block_lon=floor((longitude+180)/2)`、`block_lat=floor((latitude+90)/2)`。吸收固定效应后，令块得分 `S_b=sum_{i in b}x_i*u_i`，每次抽Rademacher权重并计算 `beta*=beta_hat+(X'X)^(-1)sum_b w_b S_b`；十个estimand在同一全国块权重向量下非线性重算。Webb六点权重以同样1,999次、seed42作敏感性。任一抽样缺失十项中的一项即STOP。

十项双侧主检验固定为五区×duration/intensity。以同步bootstrap标准差 `se_j=sd(B_j*)`（ddof=1）标准化，观测统计量为 `abs(B_hat_j/se_j)`，中心化抽样统计量为 `abs((B_j*-B_hat_j)/se_j)`；Romano–Wolf使用max-T逐步剔除、经验尾概率 `>=` 和 `(1+#)/(R+1)`修正，并按预设顺序 `NE,HHH,NW,SW,SH × duration,intensity`做累计最大值单调化；Holm复核同一十项family。

空间HAC把同一grid跨年份得分先聚合为 `S_g`，使用haversine距离、Bartlett核 `max(1-d/L,0)`、全部有序grid对和对角项，带宽固定100/200/300 km；协方差和有限样本修正沿用G185设计的明确定义，不做结果导向PSD修复。grid聚类、2°Rademacher、2°Webb和三带宽HAC全部报告。LOYO对十个五区estimand逐项检查：每项必须至少3/4个留出年份折与全样本同向；不得称其为外部验证。

SM通道分别报告antecedent state、drawdown和recovery，不把三者合并为单一中介检验。产区异质性是主结果，不得只报告有利产区；窗口敏感性必须同时列出五区。

## 支持门槛与STOP规则

Stage 1通过要求五个产区中的每一个同时满足：至少50个分析就绪grids、150个分析就绪grid-years、100个具有14/14日前置SM的事件，事件覆盖至少3年；任一年不贡献超过50%的合格事件。恢复主样本右删失率不得超过30%。分析就绪grid-year指日温度与降水窗口覆盖100%、能够机械识别事件且产量主规格字段complete-case，不要求发生事件；支持表必须把全部分析就绪grid-years、event-positive grid-years和事件数分列。

下列任一项触发STOP：五个命名产区中任一区不满足任一支持门槛；对齐产品坐标或日历无法精确连接；事件人工单元测试失败；SM时间序列不能形成有效drawdown；恢复删失率超过30%；某一年贡献超过50%；十个主要estimand中任一项少于3/4个LOYO折同向；关键RHS被吸收为零、设计降秩或结果由单一年份机械驱动。STOP后只交付完整支持表、已计算的全部结果和失败原因，不更换阈值、事件长度、空间映射或窗口补位。

## 单元测试与验收

事件识别至少包含以下人工序列：恰好连续3日；2日后间断再3日；窗口起点/终点截断；温度或降水缺失中断；同一窗口两个事件；无热日；有孤立热干日但无事件。SM测试至少包含：14/14日前置、前置缺失、事件结束即恢复、30日内恢复、下一事件删失、MA删失、30日上限和SM缺失使首次恢复不可确定。

数据验收包括输入哈希、69,038行与22,180 grids、`grid_id year`唯一性、五区支持、坐标抽查和事件panel键唯一性。除逐行 `docs/contracts/event_panel.schema.json` 外，方向专用跨记录validator必须检查：键唯一、event_seq连续、每个grid-year恰好一个代表行、event_count等于事件行数、grid-year聚合量在事件行间一致、duration/cumulative/longest等于事件行汇总、事件ID序列化正确，以及恢复状态与删失原因一致。最小反例测试必须证明违反这些条件的记录被拒绝。

所有run写入新目录并先通过 `docs/contracts/run_manifest.schema.json`，再通过方向语义validator。该validator强制：SMOKE/STOP/FAILED均 `not_for_inference=true`；STOP/FAILED的 `stop_rules_triggered` 非空、claims为空、verification非空；所有inputs含MD5与SHA-256；FULL阶段CA分位点与五区×两暴露端点非空；manifest或扩展manifest登记失败阶段、失败原因、全部已完成产物哈希。共同schema保持v1不变以保留已审阈值/G185 run的哈希，事件额外约束由冻结validator承担。失败run也必须落盘标准manifest、完整已计算结果和STOP原因。Stata主估计与Python/R复算的点估计误差须小于0.01、SE误差小于0.05、显著性等级一致。

## 预设交付

若通过，中文小稿至少包含摘要、文献定位、数据与事件定义、模型与estimand、五区持续时间/强度结果、SM下降与恢复、稳健性、局限和期刊匹配。三幅主图固定为：图1五区duration与intensity条件损害差异森林图；图2五区antecedent与drawdown的SR P25/P75差异；图3五区CA P25/P75的30日恢复曲线并附RMST差异。全部采用白底、无衬线、300 DPI和约12×5英寸。若停止，只发布审核通过的失败报告，不将未运行写成不显著。
