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

## 发布要求

每个结果目录使用 `docs/results/<canonical-id>/`，至少包含 `report.md` 或 `report.html`。报告必须写明 canonical ID、数据版、分析 scale、估计量、日期、生成脚本、解释边界及可复核位置。若结果改变数据口径、样本、方法、estimand 或呈现方式，应分别更新 `data_change`、`method_change`、`result_presentation_change`，同步维护规范化 lineage registries，并重新生成版本文档。
