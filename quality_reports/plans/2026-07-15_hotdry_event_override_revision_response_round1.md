# 热干事件方向 Round 1 审稿意见返修说明

返修对象为`quality_reports/plans/2026-07-15_hotdry_event_override_method_review_round1.md`。本轮没有按结果方向替换阈值、窗口、样本或估计式；所有新增分析均对应审稿意见中已经列明的条件变化、联合模型、严格窗口、空间推断、SM重叠、失败闭包、报告结构和数值审计要求。主实证运行是`temp/2026-07-15_compound_event_override_round1_revision_v3/`。

## Major 1：estimand语义

已新增机器表`conditional_changes_by_ca.csv`，分别报告联合模型和两个分别模型在CA P25、P75下的P50至P90条件产量变化、同一1,999次2°空间块抽样区间以及高减低中性对比。图1同时画出两条条件变化和对比。公开稿不再使用概括性“损害”或“缓冲”表述，并明确分别模型中黄淮海持续时间为−3.10%转9.42%、强度为−4.32%转6.22%；联合模型中对应结果为持续时间−3.34%转7.71%、强度2.19%转5.75%。

## Major 2：联合持续时间—强度模型

联合模型已执行。共同VIF为1.1066，五区VIF最大值为1.5726，均低于冻结触发值5；28列吸收后设计满秩，标准化条件数为7.8457。联合模型因此按设计成为主结果，两个分别模型保留为分解核验。机器输出包括`joint_model_diagnostics.json`、`model_coefficients.csv`、`joint_bootstrap_covariance.csv`和`joint_bootstrap_draws.csv.gz`。联合模型中黄淮海持续时间对比为11.43% [5.17%, 18.24%]、RW p=0.0005；黄淮海强度为3.49% [−2.17%, 9.33%]、RW p=0.817，后者未沿用分别模型的较大结果。

## Major 3：严格窗口、Webb、HAC和跨语言复算

严格日期Stage 1以新run `temp/2026-07-15_compound_event_override_strict_window_stage1_v1/`完成，extension明确标记`FULL_STAGE1_NONINFERENTIAL`和`yield_model_run=false`；产量模型在返修run内另行执行。严格窗口黄淮海持续时间和强度对比分别为9.84% [4.76%, 15.31%]和11.97% [5.37%, 19.04%]，其余八项区间跨0。

联合模型已完成Webb六点权重和100/200/300 km空间HAC。黄淮海持续时间在Webb和三种HAC下方向与主结果一致；黄淮海强度的相应区间跨0。R与Stata使用相同28列机器输入复算，闭环run为`temp/2026-07-15_compound_event_override_cross_language_validation_v2/`：28项中Python—R最大点估计差7.27×10⁻¹⁵、最大聚类SE差6.06×10⁻⁵；Python—Stata对应为2.03×10⁻¹⁴和6.06×10⁻⁵，均满足项目容差。

## Major 4：drawdown重叠敏感性

已生成`drawdown_overlap_support.csv`和`sm_antecedent_drawdown_overlap_sensitivity.csv`。下一事件进入前一事件drawdown跟踪窗口的比例分别为东北4.10%、黄淮海18.31%、西北28.47%、西南7.78%和南方13.20%，合计15.90%。公开稿和图2同时报告全样本及排除重叠后的前置SMrz和drawdown；排除重叠后黄淮海高SR组drawdown略高，未选择性省略。

## Major 5：失败run与图表run身份闭包

历史模型v1、v2及历史small-smoke比较由`temp/2026-07-15_compound_event_override_failure_closure_v1/`登记；历史v2与override smoke共75行、37字段逐项相等。返修过程中产生的两个部分模型run及一次跨语言闭环脚本失败由`temp/2026-07-15_compound_event_override_round1_failure_closure_v1/`单独登记，保留全部已有文件哈希并明确无法恢复未提交的精确pre-fix实现身份。

最终图表运行是`temp/2026-07-15_compound_event_override_report_v3/`。`report_run_manifest.json`登记renderer、返修输入、冻结与缩放recovery输入、三幅PNG、自包含HTML和公开Markdown的SHA-256；历史图和历史run未被覆盖。

## Major 6：中文小draft与可见图表

`docs/results/compound-event-intensity-duration-override-v1/report.md`已改写为中文小draft，包含摘要、研究问题、文献定位、数据、模型和estimand、联合主结果、分别模型、严格窗口、SM证据、恢复、稳健性、局限、投稿匹配、声明和复现位置。Kuwayama等和Bogenreuther等的DOI、Zotero parent/附件、全文及代码/数据仓库状态均按三层核验矩阵披露。三幅12×5英寸、白底、300 DPI、无衬线字体图在Markdown中可见，并有自包含`figures.html`。

## Minor问题闭环

严格窗口Stage 1的语义已改为全量非推断Stage 1。恢复缩放审计run为`temp/2026-07-15_compound_event_override_recovery_scaling_audit_v1/`：138,096行原始和缩放模型均收敛，Hessian条件数从1.918×10^8降至409.28，逐行预测最大绝对差6.17×10⁻¹⁴。进一步的`temp/2026-07-15_compound_event_override_recovery_scaled_inference_v1/`用缩放参数化重做1,999次固定IPCW空间推断，五区点估计、区间、SE和调整p值与冻结run全部报告字段的最大差为5.10×10⁻¹⁴；公开稿以缩放run为首选并保留原run。t=0已恢复比例总计94.3917%，东北90.4644%、黄淮海95.0109%、西北95.4508%、西南95.3409%、南方99.2891%，已按区报告。

固定环境记录为`requirements-event-override.txt`和CPython 3.14.2。新增测试覆盖L2完全分离、标准化曲线的有限性/单调性和RMST解析梯度的中心有限差分核验；事件方向16项测试在同一解释器一次执行，全部通过。历史v2与override smoke的逐字段相等性已进入机器闭包。

## 返修后解释边界

主结果以联合模型为准。可支持的表述限于：黄淮海持续时间在低、高SR端点对应不同的条件产量变化，该对比在严格窗口、Webb和三个HAC带宽下方向一致。黄淮海强度在分别模型和严格窗口中较大，但在联合扩展窗口模型中区间跨0；南方两项在联合模型中对带宽或多重检验较敏感；其余地区缺乏精确对比。SM分组和恢复模型不能被写成因果通道确认。
