# Phase 2 独立来源核验报告

核验日期：2026-07-14。核验角色：`academic-research-suite` deep-research / `source_verification_agent`。核验对象为37篇最终候选；内部核验时逐项对照候选检索记录、机器来源检查和只读Zotero基线。原始机器文件与内部标识不进入公开仓库。本报告记录的是写入前只读快照，写入后的历史计数见[Zotero公开审计摘要](zotero_write_verification.md)。

## 一、最终判定

按“DOI 与正式期刊身份明确，且至少三个相互独立的渠道支持题名/核心书目信息或摘要”的口径，最终结果为：**VERIFIED 37 篇，REJECTED 0 篇，NEEDS_REVIEW 0 篇**。其中 12 篇已存在于 Zotero collection `CA_mechanism_reclassified_2026-06-18`，25 篇经 DOI 与标准化题名复核后未在该 collection 的 146 个顶层条目中命中，因此构成可导入新条目清单。37 个 DOI 互不重复，37 个标准化题名互不重复；Crossref 均返回 `journal-article`，未发现 preprint、working paper 或仅有 journal pre-proof 的污染。

内部机器记录中的“37项三层通过”不能解释为“37篇的出版社正文均可读取并完成内容级核验”。其出版社路径检查只要求DOI或正式URL到达预期出版方路由；自动请求中只有rank 9的Econometric Society页面返回了可读题名，另外36篇分别落在验证码、403或跳转页面。因此，准确表述应为：**37/37通过来源存在性与DOI—出版社路由核验；1/37在自动请求中通过出版社页面内容读取；36/37的出版社内容读取被反自动化页面阻断。** 这36篇仍判为VERIFIED，是因为独立复核中Crossref、OpenAlex与Semantic Scholar均能按DOI返回对应论文，题名与期刊身份一致；部分核心条目还由PubMed/PMC、NASA GISS或机构存档补强。验证码页本身没有被当作题名、摘要或方法证据。

Chrome/Google Scholar 又对四个高风险或高优先级条目实施了人工强化核验：rank 1 的 Nature Food 正式页确认题名、作者、卷页与摘要；rank 6 的 JDE 条目、rank 10 的 AFM 条目均按精确 DOI 确认题名、作者、期刊和摘要；rank 24 的 Google Scholar 结果确认完整题名 *Model Uncertainty and Robustness: A Computational Framework for Multimodel Analysis*、作者 C. Young 与 K. Holsteen、2017 年正式卷期和摘要用途。由此，rank 24 在 Crossref/OpenAlex/Semantic Scholar 中仅显示短题名 *Model Uncertainty and Robustness* 的差异被解释为注册元数据的题名截短，而不是 DOI 指错论文。

## 二、逐项核验结果

下表中的“路由/内容”分别表示出版社正式URL的存在性与自动环境中的页面内容可读性；`blocked`不降低来源存在性判定，但禁止把相应验证码页当作第三条元数据或摘要证据。Zotero状态由2026-07-14写入前分页读取的146个顶层条目计算，并与内部机器核验一致。

| Rank | DOI | 正式期刊 | 独立证据 | 路由/内容 | Zotero | 判定与备注 |
|---:|---|---|---|---|---|---|
| 1 | `10.1038/s43016-026-01298-0` | Nature Food | Crossref + OpenAlex + Semantic Scholar + Nature/Chrome | 存在 / 人工可读 | missing | VERIFIED；人工确认题名、作者、卷页和摘要 |
| 2 | `10.1038/s43016-022-00592-x` | Nature Food | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | existing | VERIFIED |
| 3 | `10.1038/s43016-021-00341-6` | Nature Food | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | existing | VERIFIED |
| 4 | `10.1126/science.1251423` | Science | Crossref + OpenAlex + Semantic Scholar + PubMed | 存在 / blocked | existing | VERIFIED |
| 5 | `10.1038/s43017-022-00368-8` | Nature Reviews Earth & Environment | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | existing | VERIFIED |
| 6 | `10.1016/j.jdeveco.2023.103196` | Journal of Development Economics | Crossref + OpenAlex + Semantic Scholar + Scholar/Chrome | 存在 / blocked；Scholar 可读 | missing | VERIFIED；2023 online-first、正式卷 166 为 2024，不构成年份冲突 |
| 7 | `10.1038/s41467-026-71045-3` | Nature Communications | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | existing | VERIFIED |
| 8 | `10.1038/s41467-024-53169-6` | Nature Communications | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | existing | VERIFIED |
| 9 | `10.3982/qe1626` | Quantitative Economics | Crossref + OpenAlex + Semantic Scholar + Econometric Society | 存在 / 可读 | missing | VERIFIED；题名中的 Unicode 连字符差异无实质影响 |
| 10 | `10.1016/j.agrformet.2025.110836` | Agricultural and Forest Meteorology | Crossref + OpenAlex + Semantic Scholar + Scholar/Chrome | 存在 / blocked；Scholar 可读 | missing | VERIFIED；人工确认题名、作者、期刊和摘要 |
| 11 | `10.1093/ajae/aay037` | American Journal of Agricultural Economics | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | missing | VERIFIED；2018 online-first、正式卷期为 2019；DOI 当前转至 Wiley，OUP 卷期页仍是正式存档页 |
| 12 | `10.1037/a0020761` | Psychological Methods | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | missing | VERIFIED；句末标点差异无实质影响 |
| 13 | `10.1038/s41558-021-01075-w` | Nature Climate Change | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | missing | VERIFIED；2020 online-first、正式引文年 2021 |
| 14 | `10.1038/nature13809` | Nature | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | missing | VERIFIED；2014 online-first、正式卷期年 2015 |
| 15 | `10.1038/s41558-018-0156-3` | Nature Climate Change | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | missing | VERIFIED |
| 16 | `10.1073/pnas.0906865106` | PNAS | Crossref + OpenAlex + Semantic Scholar + PubMed | 存在 / blocked | existing | VERIFIED |
| 17 | `10.1088/1748-9326/10/5/054013` | Environmental Research Letters | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | missing | VERIFIED；IOP 验证码页未作为内容证据 |
| 18 | `10.1016/j.jeem.2021.102462` | Journal of Environmental Economics and Management | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | missing | VERIFIED |
| 19 | `10.1016/s0304-4076(98)00084-0` | Journal of Econometrics | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | missing | VERIFIED |
| 20 | `10.1088/1748-9326/aac4b1` | Environmental Research Letters | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | missing | VERIFIED；IOP 验证码页未作为内容证据 |
| 21 | `10.1097/ede.0000000000000596` | Epidemiology | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | missing | VERIFIED；索引中 2016 online-first 与 2017 正式卷期并存 |
| 22 | `10.1038/s41467-020-18631-1` | Nature Communications | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | existing | VERIFIED |
| 23 | `10.1177/1745691616658637` | Perspectives on Psychological Science | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | missing | VERIFIED |
| 24 | `10.1177/0049124115610347` | Sociological Methods & Research | Crossref + OpenAlex + Semantic Scholar + Scholar/Chrome | 存在 / blocked；Scholar 可读 | missing | VERIFIED；Scholar 确认完整副标题，短题名注册记录不是另一篇论文；2015/2016 online-first、正式卷期年 2017 |
| 25 | `10.1088/1748-9326/10/3/034009` | Environmental Research Letters | Crossref + OpenAlex + Semantic Scholar + Harvard DASH | 存在 / blocked | missing | VERIFIED |
| 26 | `10.1073/pnas.1701762114` | PNAS | Crossref + OpenAlex + Semantic Scholar + PubMed | 存在 / blocked | existing | VERIFIED |
| 27 | `10.1073/pnas.1718031115` | PNAS | Crossref + OpenAlex + Semantic Scholar + PMC | 存在 / blocked | existing | VERIFIED；现有 Zotero 条目类型误为 `webpage`，后续应修正既有条目而不是新建重复条目 |
| 28 | `10.1038/nature16467` | Nature | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | missing | VERIFIED |
| 29 | `10.1126/science.aal4369` | Science | Crossref + OpenAlex + Semantic Scholar + PubMed | 存在 / blocked | missing | VERIFIED |
| 30 | `10.1038/s41598-023-29378-2` | Scientific Reports | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | existing | VERIFIED |
| 31 | `10.1038/s41467-018-05956-1` | Nature Communications | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | missing | VERIFIED |
| 32 | `10.1038/ncomms6989` | Nature Communications | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | existing | VERIFIED |
| 33 | `10.1038/s41467-020-19639-3` | Nature Communications | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | missing | VERIFIED |
| 34 | `10.1088/1748-9326/ac592e` | Environmental Research Letters | Crossref + OpenAlex + Semantic Scholar + NASA GISS | 存在 / blocked | missing | VERIFIED |
| 35 | `10.1038/nature15725` | Nature | Crossref + OpenAlex + Semantic Scholar | 存在 / blocked | missing | VERIFIED |
| 36 | `10.1126/sciadv.aba1715` | Science Advances | Crossref + OpenAlex + Semantic Scholar + PubMed | 存在 / blocked | missing | VERIFIED |
| 37 | `10.1088/1748-9326/aadeef` | Environmental Research Letters | Crossref + OpenAlex + Semantic Scholar + 机构存档 | 存在 / blocked | missing | VERIFIED |

## 三、Zotero 去重与可导入 DOI

2026-07-14写入前的只读复核得到146个顶层条目和134个唯一canonical DOI。内部机器记录标记的12个`existing`与collection逐项一致，分别为ranks 2、3、4、5、7、8、16、22、26、27、30、32；其余25篇均未按canonical DOI命中，也没有与现有条目形成题名相似度不低于0.80的可疑近重复。写入前缺失DOI如下，次序沿用综合排序：

```text
10.1038/s43016-026-01298-0
10.1016/j.jdeveco.2023.103196
10.3982/qe1626
10.1016/j.agrformet.2025.110836
10.1093/ajae/aay037
10.1037/a0020761
10.1038/s41558-021-01075-w
10.1038/nature13809
10.1038/s41558-018-0156-3
10.1088/1748-9326/10/5/054013
10.1016/j.jeem.2021.102462
10.1016/s0304-4076(98)00084-0
10.1088/1748-9326/aac4b1
10.1097/ede.0000000000000596
10.1177/1745691616658637
10.1177/0049124115610347
10.1088/1748-9326/10/3/034009
10.1038/nature16467
10.1126/science.aal4369
10.1038/s41467-018-05956-1
10.1038/s41467-020-19639-3
10.1088/1748-9326/ac592e
10.1038/nature15725
10.1126/sciadv.aba1715
10.1088/1748-9326/aadeef
```

“写入前缺失”只描述2026-07-14只读快照；随后25篇已按正常接口写入并完成去重计数审计。未来再次导入时仍应在写入瞬间重新按DOI查询collection，并将PDF作为bibliographic parent的附件处理，避免产生新的顶层attachment。

## 四、排序字段与数据完整性审计

37个`rank`唯一且连续为1—37，`combined_score`严格按`0.7 × preliminary_learnability_score + 0.3 × journal_score`计算并保留两位小数，列表按该分数非升序排列。来源构成为core 25篇、adjacent 12篇；类别构成为direct 14篇、structural 12篇、method 11篇。每篇均有3个学习点。37个DOI、题名与内部来源核验顺序一致，未发现排序字段串位、候选合并错位或DOI—题名错配。

需要保留的元数据说明有三类。第一，ranks 6、11、13、14、21、24 的 online-first 年与正式卷期年不同，最终条目宜使用正式卷期年，并可在 `date` 或 `extra` 中保留 online-first 日期；这不是来源冲突。第二，rank 24 的 DOI 注册索引使用短题名，而出版社/Google Scholar 使用含副标题的完整题名；导入时应保留完整题名。第三，rank 27 虽已按 DOI 去重成功，但现有 Zotero `itemType=webpage` 且缺少正式期刊字段，后续应修复现有记录而不是重复导入。

## 五、质量结论与后续约束

本批次没有发现伪造DOI、DOI指向不同论文、虚构正式期刊、预印本冒充正式发表版或候选内部重复项。37篇可作为经过三渠道以上核验的正式期刊来源使用。后续生成用户可读的学习清单时，应继续区分“来源存在性已核验”“摘要层面可学习点已核验”和“全文方法细节已逐句核验”三个层级，尤其不能用出版社验证码页支持摘要或方法判断，也不能把跨文献结构类比写成对G185结果的外部因果验证。
