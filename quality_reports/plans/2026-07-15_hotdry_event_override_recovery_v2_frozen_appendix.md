# 热干事件恢复分析override v2冻结方法附录

## 版本与边界

- Canonical ID继续使用`compound-event-intensity-duration-override-v1`，新run ID为`2026-07-15_compound_event_override_recovery_v2`。
- `recovery_audit_v1`及其day-dummy分离结论保持不变。本附录是用户授权后的新恢复估计规格，不回写历史run。
- 事件定义、恢复目标、风险起点、CA端点、seed、空间块和30日上限均不改变。结果只能称为恢复关联，不能称为因果中介。

## 风险集与删失定义

事件级恢复时间沿用Stage 1机械字段。事件结束日为`t=0`；风险记录保留`t=0,...,29`，用于估计30日内恢复。`t=30`的`thirty-day-limit`是固定行政删失，不作为随机删失hazard的结局；事件在第30日仍未恢复时，其`t=0,...,29`风险记录保留，但不在删失模型中制造一次随机删失。

随机早期删失只包括day<30时由`next-event`、`ma-end`或`data-end`引起的右删失。缺失SM产生的`insufficient-sm`不由IPCW处理，继续complete-case排除。模型时间固定为`time=t/30`和`time_sq=time^2`，不再使用day dummy。

## IPCW

分子删失logit固定为：

```text
early_censor ~ time + time_sq + C(year)
```

分母删失logit固定为：

```text
early_censor ~ time + time_sq + C(zone) + C(year) + ca
             + antecedent_smrz + duration_days
             + event_mean_excess_c + onset_doy
```

两模型统一使用L2=1e-6的预设惩罚，不按收敛结果调整。逐日未删失概率为`1-p`；稳定权重为事件内分子未删失概率与分母未删失概率比值的累计乘积。权重固定在全风险集1%和99%分位截尾，并报告截尾前后最大值、1/99分位、均值、99分位与`ESS=(sum w)^2/sum(w^2)`。

## 加权恢复模型与标准化

IPCW加权pooled cloglog固定为：

```text
recovered_now ~ time + time_sq + C(zone) + C(year)
              + ca + ca:C(zone) + antecedent_smrz
              + duration_days + event_mean_excess_c + onset_doy
```

五区共同CA端点沿用产量模型P25/P75。对每个产区分别保留该区事件的year、antecedent SM、duration、mean intensity和onset DOY经验分布，事件等权标准化；只将CA替换为共同P25或P75。对`t=0,...,29`递推个体生存概率，区级曲线为事件均值，`RMST30=sum_{t=0}^{29}S(t)`。主要检验为每区`RMST30(P75)-RMST30(P25)`；负值表示较高SR对应更快恢复。

## 空间推断

结果模型使用全球原点锚定的2°空间块。主抽样为1,999次Rademacher wild-score、seed 42。计算上固定已估计并截尾的IPCW，通过加权cloglog得分和Hessian执行一次Newton score更新；标准化曲线与RMST使用解析梯度线性化，不在每个bootstrap折重新估计删失模型。该实现保留同一全国块权重向量和五区联合协方差，但不传播IPCW模型估计误差，必须作为局限披露。

五个`RMST30(P75)-RMST30(P25)`构成一个检验族，执行Romano–Wolf stepdown；Holm作为复核。机器输出另存五区联合bootstrap协方差矩阵。曲线区间使用同一组线性化bootstrap抽样的2.5%和97.5%分位数。

## 停止条件

只有以下计算性问题停止recovery v2：complete-case风险集为空；L2删失模型参数或预测概率非有限；稳定权重非有限或99分位超过50；加权cloglog不收敛、设计降秩或Hessian不可逆；任一区标准化事件为空；任一bootstrap抽样缺失五区RMST差。出现问题时不继续搜索时间函数、惩罚强度、截尾点或替代模型。
