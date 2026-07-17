# 事件稿主产量模型结构审计

## 已核对事实

事件面板确实包含`event_indicator`，无事件grid-year的`total_duration_days`和`mean_event_intensity_c`均置为0。`total_duration_days`是当季全部合格事件的累计天数；`mean_event_intensity_c`是全部合格事件的累计超温°C-day除以全部合格事件总天数，不是单次事件强度的简单平均。然而当前主产量联合设计由三个气候控制项，加上五个产区各自的`duration`、`intensity`、`ca`、`ca×duration`和`ca×intensity`构成，共28列；设计矩阵没有`event_indicator`或`ca×event_indicator`。权威代码入口为`run_hotdry_event_round1_revision.py`的`joint_design()`，机器诊断也记录`rank=28`。

这不必然表示数值计算错误，但会改变estimand的解释。当前模型估计的是把无事件年份0值也纳入后的季节聚合暴露条件关系。东北和西南的持续时间、强度P50为0，因此P50→P90对比同时跨越“无事件→有事件”和“事件严重程度增加”，不能只解释成事件已经发生后多持续一天或强度增加的边际。

## 建议的新canonical设计

若研究问题要区分事件发生与严重程度，应新建版本并固定以下结构。该建议来自结果生成后的外部审阅，只能作为新canonical follow-up，不能追溯性称为原确认性规格：

$$
\ln Y=FE+\sum_z1_z\{\psi_zSR+\phi_z I+\omega_z(SR\times I)+\beta_zD^++\delta_z(SR\times D^+)+\eta_zA^++\kappa_z(SR\times A^+)\}+X\Gamma+\varepsilon,
$$

其中，\(I\)是事件发生指示，\(\psi_zSR\)保留SR低阶主效应，并定义

$$
D^+=I(D-\widetilde D_{z,E=1}),\qquad A^+=I(A-\widetilde A_{z,E=1}).
$$

中心值只由各区事件阳性样本按预设规则计算，无事件年份的\(D^+\)和\(A^+\)置0。发生、持续时间和强度必须分别报告低、高SR条件变化、差值、共同支持和联合空间区间。修正模型无论结果是否更有利，都应取代旧模型成为新版本主规格；旧28列模型作为历史总暴露规格保留。

## 术语修正

当前`total_duration_days`是一个生育季内全部合格事件的累计天数，不是单次事件长度。黄淮海22→40天应称为“季节累计热干事件天数P50→P90”。点估计呈低SR−3.34%到高SR7.71%的跨零形态，但低SR端点区间跨0，因此端点方向未被精确确认；不能写成“SR使产量恢复11.43%”“SR平均增产11.43%”或“高SR消除热干损失”。

## SM恢复端点

现有90%恢复定义在112,832个事件中有94.39%于`t=0`达到阈值，区分度不足。下一版不应搜索85%、95%或100%以寻找更有利结果；应优先评估不依赖人为恢复阈值的SM异常轨迹、最低值、累计亏缺面积、事件后固定日数AUC或预设斜率。
