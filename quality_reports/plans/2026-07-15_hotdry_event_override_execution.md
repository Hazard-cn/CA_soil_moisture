# 热干事件强度—持续时间方向继续执行设计

## 授权与版本边界

- Canonical ID：`compound-event-intensity-duration-override-v1`。
- 用户于2026-07-15明确取消原small-smoke两轮上限和原支持数值门槛的阻断效力。本版本不修改`compound-event-intensity-duration-v1`及其历史STOP报告。
- 事件定义、扩展V3—成熟窗口、seed 42、GLEAM SMrz前置状态、drawdown和30日恢复口径均沿用已审设计，不按结果调整。
- 原支持门槛继续逐项计算并作为warning披露，但不触发STOP。只有输入缺失、日历或坐标错误、事件算法/契约错误、面板键错误或模型不可计算才停止。

## 身份闭包smoke

新run必须登记V3面板、12个逐日输入、产区映射、原core/validator/runner、override runner/validator、两个JSON契约、原设计与通过记录、override计划、历史Round 2 STOP、历史STOP公开报告，以及实际执行的全部四份测试文件。每项登记bytes、MD5和SHA-256。manifest通过shared schema与override语义validator后，才认为身份闭包。

## Stage 1与性能

- Stata面板只读取冻结模型需要的11列，不载入1,679列全表。
- 逐年读取NetCDF；超过1,000点时读取单个变量的连续数组后执行NumPy pairwise gather，禁止逐点高级索引。
- 每年记录面板行数、event-panel行数、耗时和峰值RSS。全量输出写入新的`temp/2026-07-15_compound_event_override_*`目录，不覆盖历史run。
- Stage 1输出event panel、grid-year支持、产区—年份支持、产区汇总、400条坐标值抽查、输入清单、性能清单、extension和manifest。

## 产量模型

Stage 1可计算后，使用每个grid-year唯一代表行与V3模型字段连接。持续时间和平均强度分别估计五区完全交互模型；以迭代去均值吸收grid FE和province×year FE，控制`gdd_10_29`、`pr_sum`和`pr_sum^2`。报告五区共同样本CA P25/P75与各区暴露P50/P90对应的条件损害差异。主推断执行同步2°空间块Rademacher wild-score bootstrap 1,999次、seed 42，并报告grid聚类标准误和四折LOYO方向。所有五区结果完整保留。

## SM接口

Stage 1直接交付事件级antecedent SM、drawdown、恢复/删失字段及其支持汇总。若本轮不能完成预注册IPCW pooled-logit、cloglog标准化曲线与RMST30，则报告当前已完成的机械事件接口和所需的后续估计步骤，不用未调整恢复曲线替代冻结estimand。

## 验收

运行原三份测试与override测试；验证schema、跨记录恒等式、manifest身份角色、`grid_id year`唯一性、五区支持、样本哈希、输出哈希和不可覆盖。最终形成中文执行报告，明确区分支持warning、可计算性错误和推断结果。
