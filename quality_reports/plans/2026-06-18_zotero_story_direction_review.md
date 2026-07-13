# 2026-06-18 Zotero 最新文献与故事方向复核计划

## 目标

基于 `C:\Users\Lenovo\Zotero\zotero.sqlite.codex-backup-20260618-152113` 的本地 Zotero 备份库，复核最新整理文献是否提示当前 SR buffering / region-first 故事线还存在优化空间。用户追加要求后，本轮重点限定为 Nature 系列、Science 系列、PNAS/PNAS Nexus 的文章风格和偏好的内容类型。只读查询备份库，不新增 Zotero 写入。

## 方法

1. 使用 Zotero skill 的本地库读取原则，先确认 Zotero 状态；由于用户明确给出 sqlite 备份路径，核心抽取直接读取该备份。
2. 解析 Zotero collections、items、creators、DOI、abstract、date、publicationTitle、tags、notes，并尽量读取 Better BibTeX citation key。
3. 用项目关键词筛选相关文献：straw return/residue retention/conservation agriculture/no-till/mulch/soil moisture/drought/heat/irrigation/aridity/maize/yield/adaptation/China。
4. 在候选文献中进一步识别 Nature、Science、PNAS 及其子刊来源，并把这些来源作为故事方向校准的主证据。
5. 使用官方 aims/scope、article type 或 editorial 信息校准三类刊物偏好的叙事风格；仅用官方网页作为刊物风格依据。
6. 按 ARS deep-research 的 corpus-first lit-review 流程，先做本地 corpus pre-screen，再综合为“目标刊物风格—文献命题—当前实证故事—可优化方向”。
7. 对每条建议执行反证检查，避免把秸秆还田、残茬覆盖、免耕和完整保护性农业组合直接替换。

## 输出

- 数据抽取表：`temp/2026-06-18_zotero_story_direction/`
- 报告：`quality_reports/2026-06-18_zotero_story_direction_review.md`
- 对话中给出精简结论，重点回答“故事方向有没有优化空间，以及哪种写法更接近 Nature/Science/PNAS 及其子刊”。

## 质量约束

- 不做 Zotero 写操作。
- 不把分区域相关性写成因果。
- 引用每篇核心文献时尽量提供 DOI、Zotero item key、citation key；若缺失则明确缺失。
- 至少标注一个最强反论点或边界条件。
- 区分“文献支持该机制命题”和“目标刊物可能喜欢该表达方式”；后者不得伪装成文献实证结论。
