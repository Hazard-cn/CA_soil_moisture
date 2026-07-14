# 公开结果索引

本目录是仓库唯一允许提交正式结果的目录。GitHub 代码审阅以 Markdown 为默认格式；只有需要保留完整排版或交互内容，并且图片、CSS 和 JavaScript 均已内嵌时，才发布自包含 HTML。原始数据、中间数据、CSV/DTA/Parquet、图片、PDF、压缩包和模型对象不进入本目录或 Git 历史。

各结果相对前版的数据、方法和结果呈现变化见 [`docs/VERSION_CHANGELOG.md`](../VERSION_CHANGELOG.md)，物理输入及转换关系见 [`docs/DATA_LINEAGE.md`](../DATA_LINEAGE.md)。

## 当前结果

- [`data-v3-expanded`](data-v3-expanded/report.md)：V3 expanded 三个物理视图、两类 hot-dry 定义与元数据运行 manifest。
- [`area-ggcp10-aggregated`](area-ggcp10-aggregated/report.md)：GGCP10 面积守恒聚合、结果变量分母重定义与静态验证边界。
- [`scale-g185`](scale-g185/run-manifest.md)：G185 固定规则向量、46,299 行与 13,236 grids 的运行 manifest。
- [`scale-search-region-first`](scale-search-region-first/report.md)：256 个 Gxxx scale 的区域优先探索、208 个聚类复核候选和 G057/G185/G049 选择边界。
- [`g185-method-upgrade`](g185-method-upgrade/report.md)：G185 固定效应 damage-avoidance margins 主结果与 ML 附录边界。
- [`g185-old-method-corrected`](g185-old-method-corrected/report.md)：G185 旧线性两方程区域 IE/DE/TE 修正版摘要，更新至 2026-07-10。
- [`g185-response-surface-v3`](g185-response-surface-v3/report.md)：低自由度 drought-heat response surface 的审阅与敏感性判定。
- [`g185-region-irrigation-boundary`](g185-region-irrigation-boundary/report.md)：old-method 区域连续灌溉三重交互边界。

## 当前候选稿

- [`g185-old-method-unified-override-v1`](g185-old-method-unified-override-v1/report.html)：G185旧线性两方程全国、连续区域与五区证据统一稿；同目录保留[Markdown正文](g185-old-method-unified-override-v1/report.md)。独立审查92/100，IE/DE/TE仍仅解释为代数组件，尚非95分投稿完成稿。
- [`compound-event-intensity-duration-override-v1`](compound-event-intensity-duration-override-v1/report.md)：热干事件持续时间—强度联合模型、五区异质性及SM时序证据；[自包含三图](compound-event-intensity-duration-override-v1/figures.html)。独立审查91/100，尚非95分投稿完成稿。

## Override 完整执行后审核失败

- [`regional-threshold-sr-override-v1`](regional-threshold-sr-override-v1/report.md)：在不插值或回填阈值的前提下继续运行完整外生阈值EDD模型；最终方法审查72/100、0 Critical、3 Major、4 Minor，公共失败报告最终核验PASS不改变`REVIEWED_NOT_CANDIDATE`状态。

## 审核通过的STOP报告

- [`regional-threshold-sr-v1`](regional-threshold-sr-v1/report.md)：官方连续玉米热害阈值在西南产区覆盖不足80%，方向停止于Stage 1数据支持门槛；未运行EDD或产量模型。
- [`g185-old-method-unified-v1`](g185-old-method-unified-v1/report.md)：历史结果完成复现，但东北干旱空间扰动同向比例为84.19%、低于90%稳定性门槛；不进入候选稿。
- [`compound-event-intensity-duration-v1`](compound-event-intensity-duration-v1/report.md)：事件接口完成两轮small smoke审查后仍有一项可复现性Major，按两轮上限停止；全量支持审计和模型均未运行。

## 发布要求

每个结果目录使用 `docs/results/<canonical-id>/`，至少包含 `report.md` 或 `report.html`。报告必须写明 canonical ID、数据版、分析 scale、估计量、日期、生成脚本、解释边界及可复核位置。若结果改变数据口径、样本、方法、estimand 或呈现方式，应分别更新 `data_change`、`method_change`、`result_presentation_change`，同步维护规范化 lineage registries，并重新生成版本文档。
