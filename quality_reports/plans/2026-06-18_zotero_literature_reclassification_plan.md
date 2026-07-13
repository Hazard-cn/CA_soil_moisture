# 2026-06-18 Zotero 文献分类重构计划

## 目标

围绕 SR buffering of compound extreme yield losses in Chinese maize，对本地 Zotero 中 `CA_mechanism` 相关文献重新划分分类，并补充来自 Nature、Science、PNAS 及其子刊的高相关文献。分类不再按零散变量或数据源拆分为主，而按论文论证链条组织：气候冲击与作物损失、复合极端事件、土壤水分与作物水分胁迫、保护性农业/秸秆还田与韧性、数据与方法、识别和稳健性。

## 执行步骤

1. 验证 Zotero local API 状态，读取现有 `CA_mechanism` collection、tags 和项目相关条目。
2. 对现有库内文献按标题、标签和集合归属做初筛，识别现有分类的重复、过窄和缺口。
3. 通过官方期刊页、DOI/Crossref、PNAS/Nature/Science 页面和索引页交叉核验新增候选文献；无法至少被权威元数据与期刊页面核验的条目不进入新增清单。
4. 生成新的 Zotero collection 分类方案，并把每篇候选文献映射到主分类与次级标签。
5. 生成可导入 Zotero 的 BibTeX/RIS 文件；如使用 Zotero helper 写入，则只导入已经列明题名、DOI、来源和目标分类的条目。
6. 验证导入文件可解析、条目数正确，并输出执行报告。

## 分类框架草案

`CA_mechanism` 下建议改为：

1. `01 climate-yield response`
2. `02 compound drought-heat extremes`
3. `03 soil moisture and crop water stress`
4. `04 conservation agriculture and residue return`
5. `05 adaptation, risk, and yield stability`
6. `06 datasets and remote sensing`
7. `07 empirical methods and robustness`
8. `99 review and theory`

## 质量门槛

新增文献必须满足：题名、作者、年份、期刊、DOI 或官方永久 URL 可核验；来源优先级为期刊官方页面、DOI/Crossref、PubMed/OpenAlex/Semantic Scholar 等权威索引；Google Scholar 只作为发现入口，不作为唯一真实性依据。

## 写入边界

不删除现有 Zotero 条目和集合；若需要移动或重命名现有 collection，需先保留原结构映射。新增文献可通过导入文件写入 Zotero；实际 collection 重排若 helper 不支持，则输出可执行映射供 Zotero GUI 或本地 API 后续执行。
