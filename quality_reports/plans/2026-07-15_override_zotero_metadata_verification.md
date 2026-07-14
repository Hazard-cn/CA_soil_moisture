# 三个 override 方向的 Zotero 元数据核验

核验时间为 2026-07-15，核验对象限定为三个 override 方向当前实际使用的核心定位文献。本记录只证明本地 Zotero 元数据与项目 37 篇统一索引的一致性；出版社正文、代码和数据仓库的核验仍分别以各方向的方法记录和来源清单为准，不能用本记录替代全文或代码核验。

## 本地接口状态

通过 Zotero 插件的只读 helper 执行 `status --json` 与 `probe --json`。Zotero Desktop 版本为 9.0.6，本地 API 版本为 3、schema 版本为 42；`local_api_enabled_pref=true`，本地 API 与 connector 均返回 HTTP 200。文库包含 760 个顶层条目、66 个 collections 和 850 个 tags。本次未写入、导入或修改 Zotero 文库。

## 题名检索与项目索引对照

| 用途 | Zotero item key | 年份 | 题名 | 与37篇统一索引 |
|---|---|---:|---|---|
| 地区异质温度阈值 | `262BTEKM` | 2026 | *Temperature thresholds of extreme heat-induced yield loss in maize and soybean reveal geographic heterogeneity across the northern hemisphere* | rank 1，匹配 |
| 事件定义与强度—持续时间 | `ZS7TKPCV` | 2025 | *Heat, drought, and compound events: Thresholds and impacts on crop yield variability* | rank 10，匹配 |
| 土壤水分状态与产量函数 | `5KW4A6ZV` | 2022 | *More accurate specification of water supply shows its importance for global crop production* | rank 2，匹配；本地存在重复条目，不据此重复计数 |
| 中国农业温度适应与条件斜率 | `ERVPNYQ4` | 2024 | *Adaptation to temperature extremes in Chinese agriculture, 1981 to 2010* | rank 6，匹配 |
| G185 中介识别边界 | `G9ZAK6JY` | 2010 | *A general approach to causal mediation analysis* | rank 12，匹配 |

其中 Proctor et al. (2022) 在本地检索中返回三个同题名条目：`5KW4A6ZV`、`3WQHVXYB` 和 `PW6I5G9Q`。三个记录的作者和年份一致；项目 37 篇代码索引固定使用 `5KW4A6ZV`，因此所有方向继续引用该 item key，不将重复条目解释为不同来源。

## 边界

Zotero 核验只用于确认本地文库中题名、作者、年份与 item key。地区异质阈值的算法实现仍须以 rank 1 的公开代码和用户提供的 `maize.tif` 为准；土壤水分模型边界仍须以出版社全文及 Proctor 复现代码为准；事件定义与强度—持续时间的构念仍须以论文全文而不是 Zotero 摘要为准。三个方向的最终稿不得将观察性条件关联写成因果效应或已识别中介。
