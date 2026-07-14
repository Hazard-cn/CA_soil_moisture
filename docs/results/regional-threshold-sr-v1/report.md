# 地区异质温度阈值下的SR缓冲：Stage 1数据支持失败报告

- Canonical ID：`regional-threshold-sr-v1`
- 数据版本：`data-v3-main`与官方0.5°连续玉米阈值栅格
- 样本边界：五个命名产区的pre-EDD complete-case；未锁定G185
- 运行日期：2026-07-14
- 生成入口：`scripts/python/audit_regional_threshold_coverage.py`
- 可复核位置：`temp/2026-07-14_regional_threshold_stage1_audit_v5/`
- 解释边界：`STOP_DATA_SUPPORT_GATE`；未估计SR缓冲estimand

## 摘要

本方向拟使用公开的0.5°连续玉米高温损害阈值，为中国0.1°玉米格网构造地区特定的高温暴露，并检验秸秆还田（SR）是否改变高温产量损害。设计在任何产量回归之前冻结了硬性数据门槛：五个玉米产区的主分析行都必须至少有80%能够映射到有效外生阈值。官方原始像元映射得到东北94.7366%、黄淮海98.1542%、西北84.4946%、华南98.7928%、西南69.8408%。西南没有通过门槛，因此本方向在Stage 1机械停止。没有运行产量模型、内部阈值交叉验证或物候窗口比较，也不存在可解释为显著或不显著的SR缓冲系数。

## 研究设计与停止规则

确认性暴露原计划使用Zhao等提供的连续玉米阈值，而不是在2016—2019项目样本内选择使 `SR×heat` 更有利的阈值。门槛由用户在任务 `019f60e3-a5a6-7f83-af78-26ac04e7cac2` 中明确批准，相关消息先于覆盖计算；项目不存在可验证的计算前文件快照，因此本文只称“有任务批准记录的预先冻结门槛”，不称为外部注册平台上的正式预注册。

停止规则是：任一命名产区的有效外生阈值行覆盖率低于80%，即不进入smoke test和完整模型。该规则不允许通过插值、固定32°C回填、删除云南、改变西南定义或更换complete-case分母补救。

## 来源与算法核验

[Nature Food论文](https://www.nature.com/articles/s43016-026-01298-0)指向[Zenodo阈值数据记录](https://zenodo.org/records/17142122)和[Figshare v3代码包](https://doi.org/10.6084/m9.figshare.27238629.v3)。Zotero本地条目为 `262BTEKM`。Zenodo v2记录给出0.5°玉米阈值文件；用户提供的本地附件 `maize.tif`（记为 `external://user-supplied/maize.tif`）为328,745 bytes，MD5 `0d9e6c21bf1b25f113e14315863372f2`，与官方记录一致，SHA-256为 `f05e634664c4c6c2e2df352702acd421507162bc54cc067649071521ab1285b0`。

GeoTIFF为EPSG:4326、PixelIsArea、514×76、float32，像元0.5°，有效单元5,627/39,064，阈值范围26.8—44.0°C。Figshare下载归档解压后共37个文件，其中只有 `CalExposure.m` 和制图notebook两个代码候选；notebook读取预计算Excel制图，未发现阈值估计程序。`CalExposure.m` 实现逐小时超过连续阈值的计数：

\[
H_{itw}=\sum_{h\in w}1(T_{ith}\ge\tau_i),\quad
ExposureDays_{itw}=H_{itw}/24,\quad
ExposureFraction_{itw}=H_{itw}/N_{total,itw}.
\]

其中 `N_total=m×n`，不是自动剔除缺失后的 `N_valid`。若未来重新运行暴露算法，项目还需增加完整24小时窗口断言。温度超额积分只能另称 `threshold_hdd_cday`，不能写成对公开暴露算法的直接复刻。

## 数据与映射

V3输入为 `data-v3-expanded-main-dta`，SHA-256 `3f3f045a8040b876565873febab3918d166b8bd6f6938669b48c634a46172517`，包含69,038个grid-years和22,180个grids，`grid_id year`无重复。五区pre-EDD complete-case要求 `ln_yield`、`ca`、`gdd_10_29`、`pr_sum`、`v3_doy`、`he_doy`、`ma_doy` 和 `gleam_smrz_mean` 非缺失；这些字段在五区均完整，得到66,396行和21,337个grids。`irr_frac`和`crc_lag1`不是该覆盖门槛的预设主控制，不能用其缺失改变分母。

映射把每个0.1°格网中心赋给其所在的原始0.5°PixelIsArea单元，不先取整坐标，不插值或外推。行列使用零基索引，`source_pixel_id=source_row×514+source_col`。最终22,180个grids中，19,493个获得有效阈值，2,642个落在官方NoData单元，45个在栅格外；全部记录通过机器契约和跨字段语义检查。

| 产区 | 主分析行 | 有效阈值行 | 行覆盖率 | 主分析grids | 有效阈值grids | 80%门槛 |
|---|---:|---:|---:|---:|---:|---|
| 东北（NE） | 25,041 | 23,723 | 94.7366% | 7,365 | 6,967 | 通过 |
| 黄淮海（HHH） | 13,165 | 12,922 | 98.1542% | 3,844 | 3,775 | 通过 |
| 西北（NW） | 5,540 | 4,681 | 84.4946% | 2,228 | 1,849 | 通过 |
| 华南（SH） | 4,556 | 4,501 | 98.7928% | 1,692 | 1,668 | 通过 |
| 西南（SW） | 18,094 | 12,637 | **69.8408%** | 6,208 | 4,487 | **停止** |

西南内部的原始覆盖率为云南35.5549%、贵州80.5942%、四川84.6172%、广西99.4704%、重庆100%。主要缺口来自官方阈值栅格在云南的大量NoData，而不是项目面板中产量、SR、物候或GLEAM字段的缺失。

## 映射敏感性与确认性边界

对NoData重归一化的双线性插值可把西南覆盖提高到81.6901%，3×3邻域最近有效像元回填可提高到90.2343%。两者都会用估算阈值替代官方NoData，因而改变确认性暴露和样本支持门槛，不能用于使本方向通过。最近原始像元中心映射与所在单元赋值相同，西南仍为69.8408%；把PixelIsArea误读为PixelIsPoint也只有71.6757%。这些敏感性解释了不同GIS默认处理可能产生的表面差异，但不改变停止决定。

## 结论与未来重新授权条件

本方向的失败发生在模型之前，结论仅限于：按照官方原始连续阈值和预设五区口径，西南产区的数据支持不足以满足80%确认性覆盖门槛。不能据此判断SR是否缓冲地区特定高温损害，也不能写成阈值模型结果不显著。

只有在用户明确改变覆盖门槛或授权一个新的、可单独标识的阈值插补estimand后，才能建立新canonical ID重新设计；新设计不得覆盖本次STOP记录。若重新授权，仍须使用逐小时ERA5温度、完整窗口断言、独立的GLEAM antecedent与同期通道，并明确当前项目“full”窗口是V3前30日至MA，不是严格播种至成熟。

## 复现与审查

最终审计run为 `temp/2026-07-14_regional_threshold_stage1_audit_v5/`。其中 `threshold_coverage_by_zone.csv`、`threshold_grid.csv`、`threshold_grid.jsonl`、`run_manifest.json` 和扩展 `audit_manifest.json` 提供样本、映射、契约、输入与输出哈希。执行入口为 `scripts/python/audit_regional_threshold_coverage.py`；复算必须指定新的输出目录，脚本拒绝修改既有run。

独立第3轮审查判定为 `PASS_PUBLIC_STOP_REPORT`，97/100，Critical 0、Major 0。唯一Minor是当前schema尚未把全部标准输出字段列入顶层required；v5实际记录字段完整，额外语义检查为0错误，因此不影响本次STOP结论。审查记录见 `quality_reports/plans/2026-07-14_threshold_review_round3_pass.md`。
