# 热干事件方向：执行前文献与代码三层核验矩阵

## 核验范围

本矩阵只核验事件强度—持续时间、固定效应、区域差异、阈值和物候分窗等设计主张。它不把全文方法描述写成代码复现，也不假定受阻补充材料包含可执行代码。

37篇综合排序文件SHA-256为 `6e42a8aa141b481aa04cb99b9a7c3d73ba534289577c77d91b54099841ab14cf`；机器清单SHA-256为 `341dd21bf50f0580f2378ec579030b55f31e15ed8bf6276104bf8790fc596a9e`。

| 文献与主张 | Zotero/DOI元数据 | 出版者或全文核验 | 代码或数据仓库核验 | 设计允许使用的结论 |
|---|---|---|---|---|
| Kuwayama et al. (2019), DOI `10.1093/ajae/aay037`：持续时间、强度、固定效应、区域差异和联合检验 | Zotero parent `GVC6XC5J`；题名、作者、年份、AJAE与DOI一致 | Zotero本地附件ID `EM4662HK`，PDF SHA-256 `f780d77d8d577b7b0fee3b580e3019a2378ff5cff737f3a11e30e8f22d9b5545`；Zotero全文缓存SHA-256 `18d67a1d47acabab736e6af5d0c4e678f5c8e8f25574aee0ab901f9511315acf`。PDF第1页说明panel fixed effects和region-specific results，第3页明确marginal increases in duration and intensity，第11页报告联合显著性 | 官方补充端点 `ajaeajaeaay037-sup-0001.zip` 返回HTTP 403；机器清单状态为`blocked`，未取得包内容、版本或代码哈希 | 只借鉴把持续时间和强度分开、使用固定效应和联合检验、完整报告区域差异；不得声称复刻其代码 |
| Bogenreuther et al. (2025), DOI `10.1016/j.agrformet.2025.110836`：绝对/相对阈值、复合日、物候阶段 | Zotero parent `ZS7TKPCV`；题名、作者、年份、Agricultural and Forest Meteorology与DOI一致 | Zotero本地附件ID `EGZ3IE4R`，PDF SHA-256 `dd8eb24508e3df01bcef926585d4ac9902f463209130dd1fbae326ec8f7f4d32`；Zotero全文缓存SHA-256 `53ad274d324699d3f0f0884fb5a31a0c8da7656cfefb28e62f2bf138b8f92481`。PDF第1页报告营养/生殖阶段差异，第2页说明绝对温度和降水阈值与复合事件，第10页讨论百分位与绝对阈值、同日复合事件和连续日替代定义 | 机器清单状态为`data_only`；Elsevier补充材料与Bayreuth记录未识别代码归档，`code_file_count=0` | 只借鉴预先定义阈值、同日复合条件和物候分窗敏感性；不得声称移植其事件识别代码 |

## 执行门禁

两篇文献的元数据、全文和仓库状态均已在设计执行前登记。Kuwayama补充包受阻、Bogenreuther仅识别数据而无代码，因此本方向的事件识别、IPCW/RMST和推断程序必须由本项目自行定义、人工单元测试和跨语言复算；不能使用“公开代码复刻”措辞。
