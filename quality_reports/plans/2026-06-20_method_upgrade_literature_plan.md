# 2026-06-20 方法升级与因果识别文献探索计划

## 任务

基于本 project 既有方法脉络和其他相关对话，评估除当前 G185/G057 region-first damage-slope framing 之外，是否存在更适合补强因果解释、异质性识别和同行认可度的方法。用户已提出的候选方法是 causal forest，本轮需要同时寻找其他论文中被认可的方法并比较。

## 当前项目约束

本轮不修改现有草稿、脚本、结果表或 Zotero 库。只读取项目历史、现有报告、线程摘要、Zotero/Google Scholar/DOI 元数据，并输出方法建议。任何新方法都必须兼容当前项目语言纪律：除非识别设计显著增强，否则仍使用 conditional association、damage-slope modification、buffering margin 等表述。

## 信息来源

1. 本 project 历史线程摘要：G185 draft、region-first scale search、GGCP10 mediation branches、Zotero 文献重构。
2. 本地项目文件：G185 draft package、method-alternative report、story follow-up/stata verification reports。
3. Google Scholar via `cookjohn/gs-skills + Chrome DevTools MCP`：检索 causal forest、DML、panel causal inference、synthetic DID、causal ML in agriculture/climate。
4. DOI/Crossref/publisher page：核验题名、作者、年份、期刊和 DOI。
5. Zotero 本地库：检查项目内是否已有相关方法文献。

## 评价标准

每个候选方法按四个维度排序：第一，是否真正增强因果解释；第二，是否被经济学、统计学或农业气候影响文献同行认可；第三，是否适配当前 2016-2019 grid-year panel、连续 SR adoption、hazard interactions、grid/year FE 和 region-first 主线；第四，实施成本和审稿风险。

## 预期产出

输出一份报告，包含当前方法诊断、causal forest 的定位、其他可选方法、推荐执行顺序、哪些方法不建议作为主线，以及可直接写入论文 methods/limitations 的句式。
