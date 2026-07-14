# 热干事件方向设计审查第1轮

- 审查结论：`REVISE_DESIGN`
- 评分：78/100
- Critical：0
- Major：8

主要问题为执行门禁提前允许smoke、canonical ID不一致、五区支持与STOP矛盾、主字段和模型未冻结、estimand/VIF不可机械执行、IPCW/RMST结果模型缺失、空间推断/Romano–Wolf/HAC/LOYO定义不足、文献三层核验推迟，以及schema不能约束代表行、SM删失和STOP manifest。

设计包v2已逐项修订：只读支持审计是PASS_DESIGN前唯一允许动作；统一canonical ID；任一区门槛失败即STOP；冻结字段、方程、estimand、VIF和条件数；定义IPCW与离散hazard标准化曲线；冻结wild-score、RW、HAC和逐项LOYO；新增执行前文献矩阵；强化event schema并要求方向专用跨记录与manifest语义validator。
