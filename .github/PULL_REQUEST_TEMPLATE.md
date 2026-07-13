## 变更摘要

说明本次变更解决的问题，以及是否改变数据口径、样本、估计量、核心脚本或公开结果。

## 版本影响

- 关联 canonical ID：
- 是否新增或替代版本：否 / 是，请说明
- 是否需要更新 `quality_reports/version_registry.csv`：否 / 是
- 数据变化：
- 方法或 estimand 变化：
- 结果呈现或公开结论变化：
- 是否新增 artifact、sample rule、method 或 analysis run ID：

## 验证

- [ ] 已运行 `python .github/scripts/check_repository_policy.py --source index`
- [ ] Python 和 R 源文件语法检查通过
- [ ] 未提交原始数据、中间数据、缓存、日志或二进制分析产物
- [ ] 新增结果只位于 `docs/results/`，且仅为 Markdown 或自包含 HTML
- [ ] HTML 不依赖本地图片、CSS、JavaScript 或绝对文件路径
- [ ] 估计量和解释边界已在文档中说明
- [ ] 已运行 `python scripts/python/version_lineage.py validate --strict`
- [ ] 已运行 `python scripts/python/version_lineage.py build-docs --check`

## Post-Deploy Monitoring & Validation

本仓库没有在线生产运行时。说明合并后需要复核的 GitHub Actions、Pages 页面、版本登记外键或公开结果链接；如无额外运行影响，写明原因。
