---
layout: default
title: SR缓冲机制方法组合：GPT网页端统一入口
---

# SR缓冲机制方法组合：GPT网页端统一入口

- Canonical ID：`report-sr-method-portfolio-web-reader-v1`
- 发布日期：2026-07-18
- 构建基线提交：`ce8d2235a49b9dcb70798f01983a65b59b35805d`；本次发布提交以GitHub文件历史为准
- 版本性质：GitHub原生报告呈现版本
- 数据或方法变化：无
- 当前用途：供GPT网页端、人类合作者和独立审阅者统一读取三个实证方向、37篇文献方法索引及外部审阅修正

本入口不生成新估计、不修改既有机器结果，也不把任何候选稿提升为投稿完成稿。既有机器运行和内部审查记录保持不变；版本登记仅把G185与事件方向从“当前候选”调整为“存在后续未解决方法问题的历史内部候选记录”。本入口的新增内容是阅读顺序、跨方向边界和外部审阅后的解释更新。若本入口与较早候选稿的概括存在冲突，应采用本入口及其链接的分类规则，并回到既有报告中的机器数值核对。

## 核心阅读顺序

1. [三方向状态、主结果与待处理问题](portfolio/portfolio_status.md)，并核对[G185全国端点斜率表](portfolio/g185_endpoint_slopes.md)。
2. [两次网页端审阅的结构化综合与校正](review/external_review_synthesis.md)。
3. [数据家族、暴露和estimand边界](methods/data_family_estimand_matrix.md)。
4. [事件稿主产量模型结构审计](methods/event_model_structure_audit.md)。
5. [条件斜率结果分类规则](methods/claim_classification_rules.md)。
6. 三个方向的公开报告：G185[Markdown](../g185-old-method-unified-override-v1/report.md)、事件持续时间—强度[Markdown](../compound-event-intensity-duration-override-v1/report.md)、地区异质阈值[失败报告](../regional-threshold-sr-override-v1/report.md)。
7. 从[37篇文献公开阅读入口](literature/README.md)进入综合排序、代码与数据状态、方法模块及核验限制。
8. 需要网页端继续审阅或brainstorm时，直接使用[GPT网页端任务说明](GPT_WEB_PROMPT.md)。

数据资产、变量和机器接口另见仓库级[数据资产盘点](../../DATA_ASSET_INVENTORY.md)、[变量说明](../../VARIABLES.md)、[数据来源](../../DATA_SOURCES.md)及既有`threshold_grid`、`event_panel`、`run_manifest`契约。

## 三个方向的当前判定

| 方向 | 数据家族与样本 | 当前状态 | 当前可保留的信息 | 外部审阅后的必要修正 |
|---|---|---|---|---|
| G185旧方法统一稿 | GGCP10-G185；46,299 grid-years、13,236 grids | 2026-07-15内部92/100候选记录；后续外部方法Major未解决，当前不是投稿候选 | 全国、连续区域和五区的同期两方程代数组件；历史校正TE和更强FE下的衰减 | 不能仅凭P75−P25差值为正统称损失缓冲；必须同时报告低、高SR端点及区间。year FE热干点估计为正向增强，province×year FE端点整体精度有限 |
| 热干事件持续时间—强度 | V3；61,918 grid-years、19,749 grids | 2026-07-15内部`PASS_CANDIDATE` 91/100记录；后续事件结构Critical未解决，当前不是投稿候选 | 黄淮海季节累计事件天数的高减低SR差值、五区完整结果和SM时序描述 | 当前28列产量设计没有事件指示变量，现有估计是含无事件0值的季节聚合暴露关系，不是纯事件阳性严重程度边际；黄淮海−3.34%→7.71%只构成点估计跨零形态，低SR端点区间跨0 |
| 地区异质温度阈值 | V3；54,890 grid-years、17,450 grids | `REVIEWED_NOT_CANDIDATE`，72/100 | 完整失败证据、外生阈值覆盖、五区正向/反向/不精确结果及外推边界 | 冻结结果不支持“SR缓冲温度损害”；黄淮海低、高SR条件变化均为正。旧80%覆盖门槛已取消，但覆盖与共同支持限制仍必须报告，不授权阈值、窗口或样本救援 |

## 关键解释边界

第一，G185与V3不是同一数据家族，不能把三套现有系数直接组成一个规格分布。若研究“暴露表征如何改变推断”，必须在同一V3共同样本、同一物候窗口、同一SR端点、同一固定效应和空间推断下重新构造全部暴露，并建立新canonical ID。

第二，IE、DE和TE是同期两方程代数组件，不是natural、interventional或其他已识别因果中介效应。先行SM、事件期drawdown和事件后轨迹是状态或独立通道结果，也不能自动转换为中介比例。

第三，结果分类必须区分“点估计形态”和“同一主推断下是否得到统计确认”。高减低SR差值区间不跨0，不能替代低、高SR两个端点的方向和精度检查。

第四，事件方向的`total_duration_days`是当季全部合格事件累计天数；`mean_event_intensity_c`是全部合格事件累计超温°C-day除以全部合格事件总天数。无事件年份两者置0。若下一版要分离事件发生与严重程度，应采用新的两部分模型并保留SR主效应。

第五，先行SM新方向尚未冻结。必须在所有年份均可定义的固定物候风险窗口前SM、事件阳性年份首个事件前SM、或预设唯一事件/聚合规则中选择一个；任何情况下产量方程都必须保持每个`grid_id year`一行。

## 37篇文献资产边界

37篇均完成DOI、题名和出版来源存在性核验，但这不表示37篇均已阅读全文。自动请求仅有1/37读取到出版社页面题名或有效页面内容，36/37受验证码、403或跳转限制；4篇另经Chrome强化核验。代码状态为：本地静态可读代码16篇、仅数据7篇、未发现公开代码9篇、官方链接受阻3篇、需作者申请2篇。16个静态可读包共登记271个代码文件，全部未执行。

逐篇证据及其限制从[文献公开阅读入口](literature/README.md)进入；Zotero数量是2026-07-14保存的历史快照，2026-07-18没有实时桌面端连接。这些材料用于限定可借鉴的方法操作，不得据此虚构代码可运行性或全文主张。

## GitHub发布边界

本目录只包含Markdown。图表使用既有方向目录中的自包含HTML：[G185正文与内嵌图](../g185-old-method-unified-override-v1/report.html)和[事件稿三图](../compound-event-intensity-duration-override-v1/figures.html)。原始及中间面板、CSV/DTA/Parquet、PNG/PDF、压缩包、bootstrap draws、模型对象、日志、Zotero全文以及许可证缺失或受限的第三方代码均不进入Git历史；许可证明确的纯文本代码单独发布于[许可代码子集](../../../references/code/published-literature-37/README.md)，且没有执行。

本版本只改变结果的组织和公开入口，不改变数据、样本、方法、estimand、推断或数值。版本变化与谱系见[版本变化详表](../../VERSION_CHANGELOG.md)和[版本地图](../../VERSION_MAP.md)。
