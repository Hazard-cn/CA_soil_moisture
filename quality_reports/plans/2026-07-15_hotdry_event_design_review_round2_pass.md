# 热干事件方向设计审查：Round 2

- 审查对象：`quality_reports/plans/2026-07-15_hotdry_event_duration_intensity_design_v1.md`
- canonical ID：`compound-event-intensity-duration-v1`
- 独立审查结论：`PASS_DESIGN`
- 评分：92/100
- Critical：0
- 未解决Major：0
- 授权边界：允许代码实现与小样本smoke；不授权完整模型。

## 评分

| 维度 | 得分 |
|---|---:|
| 创新与期刊匹配 | 19/20 |
| 数据与五区支持 | 19/20 |
| estimand与识别边界 | 18/20 |
| SM构念及时序 | 14/15 |
| 精度与稳定性 | 14/15 |
| 可复现性和图表 | 8/10 |
| **合计** | **92/100** |

## Major关闭情况

第一，执行门禁和canonical ID已统一，设计通过前只允许只读审计。第二，五个命名产区中任一区未满足任一支持门槛即Stage 1 STOP，支持表分列分析就绪grid-years、event-positive grid-years和事件数。第三，冻结了`ln_yield`、`ca`、`gdd_10_29`、`pr_sum`、`pr_sum_sq`、complete-case字段、产区映射脚本及合并完全交互方程。第四，冻结了五区共同CA端点、各区暴露端点、条件损害差异、FWL-VIF、满秩和条件数。第五，恢复分析已定义风险集、统一生存时间变量`recovery_days`、IPCW、cloglog、区域标准化和RMST。第六，空间推断已定义同步wild-score、Rademacher/Webb、十项Romano–Wolf family、Holm、HAC和逐项LOYO。第七，两篇核心文献完成DOI/Zotero、PDF、全文缓存和仓库状态核验，没有使用“公开代码复刻”措辞。第八，逐行event schema与跨记录、run manifest语义validator的职责边界已经明确。

## schema反例

合法的无事件、已恢复、右删失和`insufficient-sm`记录通过；无事件但代表标记为false、无事件但平均强度非零、事件记录缺少SM/恢复字段、恢复与删失同时false、恢复状态全为null、已恢复但SM状态缺失、右删失但没有0—30日随访时间均被拒绝。

## smoke前实施项

现有core和测试必须把`window-end`统一为`ma-end`；实现事件panel跨记录validator和事件run manifest语义validator；补充事件记录非null平均强度与复合热日比例、`daily_complete_flag`与有效日计数一致、`duration=end-onset+1`等自动化反例。上述验证全部通过后，smoke才可写出PASS；完整模型仍需独立smoke结果审查。
