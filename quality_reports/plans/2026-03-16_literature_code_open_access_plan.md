# 文献与代码开源核查及下载计划

## 摘要

- 先对两组清单去重，形成 27 篇唯一论文主表，并保留原始编号映射，如 `1/R6`、`2/R10`、`6/R2`。
- 只使用合法开放来源：官方期刊页、出版社 OA PDF、PMC、机构库、作者自存档；代码按“官方声明优先，官方无入口时扩展到 GitHub/Zenodo/OSF/作者主页”执行。
- 先产出双格式清单，再按清单批量下载全文和代码，避免直接下载后才发现 DOI、权限或重复项有误。

## 产物与接口

- 生成 `references/manifests/literature_code_manifest.md` 和 `references/manifests/literature_code_manifest.csv`。
- Manifest 字段固定为：`paper_key`、`source_ids`、`title`、`first_author`、`year`、`journal`、`doi_corrected`、`official_url`、`fulltext_status`、`best_pdf_url`、`code_status`、`code_url`、`data_url`、`license_or_notes`、`checked_on`。
- 下载目录固定为 `references/papers` 和 `references/code`，命名统一为 `year_firstauthor_shortslug`。

## 实施步骤

1. 逐条核对题名、期刊和 DOI，修正录入错误并合并重复项。
2. 用 DOI 或官方题名定位出版社页面，提取 `Data availability`、`Code availability`、`Source data`、补充材料和 PMC 全文链接。
3. 若官方页无代码链接，则扩展检索 GitHub、Zenodo、OSF、作者主页；只有能与论文标题、作者或补充材料对应的仓库才记为有效，并区分 `official`、`author-related`、`not found`。
4. 对可合法下载的全文和代码做批量拉取；代码优先 release 包或浅克隆，避免无必要地拉取完整历史。
5. 输出短报告，按“全文+代码”“仅全文”“仅官方页”“无公开代码”四类汇总。

## 验收

- 27 个唯一条目全部进入 manifest，且每条都有 `official_url`，并有 `doi_corrected` 或“待核验”标记。
- 重复项全部合并成功，且能回溯到原始编号。
- 所有 `best_pdf_url` 都能打开并对应正确论文；无法合法获取全文的条目必须明确标记。
- 所有 `code_url` 都必须有可追溯依据；不能确认与原文对应的仓库只能标为 `author-related`，不能混作官方代码。
