# 公开结果索引

本目录是仓库唯一允许提交正式结果的目录。GitHub 代码审阅以 Markdown 为默认格式；只有需要保留完整排版或交互内容，并且图片、CSS 和 JavaScript 均已内嵌时，才发布自包含 HTML。原始数据、中间数据、CSV/DTA/Parquet、图片、PDF、压缩包和模型对象不进入本目录或 Git 历史。

各结果相对前版的数据、方法和结果呈现变化见 [`docs/VERSION_CHANGELOG.md`](../VERSION_CHANGELOG.md)，物理输入及转换关系见 [`docs/DATA_LINEAGE.md`](../DATA_LINEAGE.md)。

## GPT网页端统一入口

- [`report-sr-method-portfolio-web-reader-v1`](report-sr-method-portfolio-web-reader-v1/report.md)：集中提供三个实证方向的状态与解释更新、37篇文献方法索引、数据与estimand边界及可直接提交网页端的任务说明。该入口不产生新估计，也不改变三个方向的canonical状态。

## 当前结果

- [`data-v3-expanded`](data-v3-expanded/report.md)：V3 expanded 三个物理视图、两类 hot-dry 定义与元数据运行 manifest。
- [`area-ggcp10-aggregated`](area-ggcp10-aggregated/report.md)：GGCP10 面积守恒聚合、结果变量分母重定义与静态验证边界。
- [`scale-g185`](scale-g185/run-manifest.md)：G185 固定规则向量、46,299 行与 13,236 grids 的运行 manifest。
- [`scale-search-region-first`](scale-search-region-first/report.md)：256 个 Gxxx scale 的区域优先探索、208 个聚类复核候选和 G057/G185/G049 选择边界。
- [`g185-method-upgrade`](g185-method-upgrade/report.md)：G185 固定效应 damage-avoidance margins 主结果与 ML 附录边界。
- [`g185-old-method-corrected`](g185-old-method-corrected/report.md)：G185 旧线性两方程区域 IE/DE/TE 修正版摘要，更新至 2026-07-10。
- [`g185-response-surface-v3`](g185-response-surface-v3/report.md)：低自由度 drought-heat response surface 的审阅与敏感性判定。
- [`g185-region-irrigation-boundary`](g185-region-irrigation-boundary/report.md)：old-method 区域连续灌溉三重交互边界。

## 历史内部候选记录与后续外部审阅

- [`g185-old-method-unified-override-v1`](g185-old-method-unified-override-v1/report.md)：2026-07-15内部92/100候选记录；后续外部方法审阅发现端点分类与强固定效应披露Major，当前不是投稿候选。[自包含HTML](g185-old-method-unified-override-v1/report.html)保留历史版式，当前解释以[统一入口](report-sr-method-portfolio-web-reader-v1/report.md)为准。
- [`compound-event-intensity-duration-override-v1`](compound-event-intensity-duration-override-v1/report.md)：2026-07-15内部91/100候选记录；后续确认28列主模型未包含事件指示变量，当前不是投稿候选。[自包含三图](compound-event-intensity-duration-override-v1/figures.html)保留历史结果，修正模型须使用新canonical ID。

## Override 完整执行后审核失败

- [`regional-threshold-sr-override-v1`](regional-threshold-sr-override-v1/report.md)：在不插值或回填阈值的前提下继续运行完整外生阈值EDD模型；最终方法审查72/100、0 Critical、3 Major、4 Minor，公共失败报告最终核验PASS不改变`REVIEWED_NOT_CANDIDATE`状态。

## 审核通过的STOP报告

- [`regional-threshold-sr-v1`](regional-threshold-sr-v1/report.md)：历史Stage 1 STOP记录，当时以西南覆盖不足80%停止；该机械门槛已被后续用户授权取消，不是现行规则。后续override完整运行的失败状态见上一节。
- [`g185-old-method-unified-v1`](g185-old-method-unified-v1/report.md)：历史结果完成复现，但东北干旱空间扰动同向比例为84.19%、低于90%稳定性门槛；不进入候选稿。
- [`compound-event-intensity-duration-v1`](compound-event-intensity-duration-v1/report.md)：事件接口完成两轮small smoke审查后仍有一项可复现性Major，按两轮上限停止；全量支持审计和模型均未运行。

## 发布要求

每个结果目录使用 `docs/results/<canonical-id>/`，至少包含 `report.md` 或 `report.html`。报告必须写明 canonical ID、数据版、分析 scale、估计量、日期、生成脚本、解释边界及可复核位置。若结果改变数据口径、样本、方法、estimand 或呈现方式，应分别更新 `data_change`、`method_change`、`result_presentation_change`，同步维护规范化 lineage registries，并重新生成版本文档。
