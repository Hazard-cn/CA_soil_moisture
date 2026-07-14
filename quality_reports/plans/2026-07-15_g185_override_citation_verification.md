# G185 override draft 引文三层核验

核验对象为draft v1实际引用的5篇定位文献。第一层使用本项目37篇Zotero综合排序中的题名、作者、年份和DOI；第二层使用Crossref Works API逐条核对题名、完整作者、期刊、卷期、页码或文章号；第三层使用出版社正式页面或NCBI PubMed/MEDLINE记录核对。Lesk、Liu和Proctor另与Nature正式文章页及本地代码索引核对；Imai与Vansteelandt另与PubMed 20954780、27922534及本地已安装方法代码条目核对。

| DOI | Zotero/37篇 | Crossref | 出版社或MEDLINE | 结论 |
|---|---|---|---|---|
| 10.1037/a0020761 | 匹配 | 匹配 | PubMed 20954780匹配 | PASS |
| 10.1038/s43016-021-00341-6 | 匹配 | 匹配 | Nature Food正式页匹配 | PASS |
| 10.1038/s41467-020-18631-1 | 匹配 | 匹配 | Nature Communications正式页匹配 | PASS |
| 10.1038/s43016-022-00592-x | 匹配 | 匹配 | Nature Food正式页匹配；作者修正为Proctor、Rigden、Chan和Huybers | PASS |
| 10.1097/EDE.0000000000000596 | 匹配 | 匹配 | PubMed 27922534/PMC5289540匹配 | PASS |

本次发现并修正一项初稿书目错误：Proctor et al. (2022)曾误套用另一篇Proctor论文的作者列表；正文论证未使用该错误作者信息，参考文献现已按Crossref和Nature正式页修正。未加入37篇语料之外的新文献。
