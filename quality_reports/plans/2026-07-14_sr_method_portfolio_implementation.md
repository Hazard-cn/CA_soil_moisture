# SR 缓冲机制多方向实证与小稿实施计划

## Material Passport

- Origin Skill: academic-research-suite / academic-pipeline + experiment-agent
- Origin Mode: full pipeline / design freeze
- Origin Date: 2026-07-14
- Verification Status: DESIGN_REVIEW_PENDING
- Version Label: sr_method_portfolio_design_v2
- Git Base: `b7f17f7`
- Data Inventory Commit: `3da8a12`（cherry-pick of `721dd7e`）
- Work Branch: `work/sr-method-portfolio`
- Worktree: 当前仓库的隔离工作树，分支为 `work/sr-method-portfolio`

## 1. 研究组合与执行边界

本轮固定三个候选方向：`g185-old-method-unified-v1`、`regional-threshold-sr-v1`、`compound-event-intensity-duration-v1`。每个方向先冻结研究问题、估计量、数据入口、支持规则、土壤水分时间角色、固定效应、推断、多重检验、图表与停止规则；设计者与审稿人必须不同。设计审稿无 Critical、无未解决 Major 且评分不低于 90 后才能运行 smoke test。smoke test 通过结果审查后才能运行完整模型。

`g185-response-surface-v3` 不进入任何方向。SWSM 在日期轴修复并登记新哈希前不得进入主结果。任何输入哈希、样本规则、估计量、方法或公开主张变化均创建新 run ID，不覆盖历史产物。

## 2. G185 旧方法统一方向

研究问题是：在 G185 固定样本中，较高观测 SR 是否与较平缓的干旱、高温和热干损害斜率相关，以及这种条件关联是否具有产区差异。估计量保持旧两方程代数组件：`IE(s)=(a1+a3*s)b`、`DE(s)=c1+c3*s`、`TE(s)=IE(s)+DE(s)`。

输入固定为 GGCP10 baseline suite 与 V3 precipitation hot-dry sidecar，G185 raw support 必须恢复 46,299 行、13,236 grids；五个命名区域为 44,556 行、12,745 grids。主要证据为全国固定 P90 下 SR P25/P50/P75 的 IE/DE/TE、核心区域 0 到 P90 的同一线性 TE 投影、五区校正 IE/DE/TE 矩阵。旧 `1.50/3.27/2.56` 仅可标为 DE；校正 TE 必须为东北干旱 `1.85%`、黄淮海高温 `3.17%`、黄淮海热干 `2.43%`，并在项目容差内复现。

历史 grid FE + year FE 为估计量复现主规格；grid FE + province×year FE、2°空间块 wild bootstrap 与空间 HAC 仅作明确标注的稳健性。空间推断后核心方向系统反向、样本筛选无法披露或校正组件无法复现时停止投稿稿件。

## 3. 空间异质温度阈值方向

**Stage 1状态：STOP。** 独立数据审计按GeoTIFF PixelIsArea规则复算后，西南产区正式pre-EDD complete-case的有效外生阈值覆盖为12,637/18,094=69.84%，低于预注册80%硬门槛；其余四区为84.49%—98.79%。核心控制、物候和GLEAM字段在五区无缺失，不能通过后续complete-case自然提高西南覆盖。按预注册规则，本方向不进入smoke test或完整模型，只交付覆盖失败报告。不得以双线性插值、删除云南、改变西南定义或内部阈值搜索补位。

确认性暴露使用用户提供的本地附件 `maize.tif`（记为 `external://user-supplied/maize.tif`）。已验证文件为 328,745 bytes、MD5 `0d9e6c21bf1b25f113e14315863372f2`、SHA-256 `f05e634664c4c6c2e2df352702acd421507162bc54cc067649071521ab1285b0`、WGS84、0.5°、514×76、float32。主映射按项目 0.1°格网中心所在的原始0.5°单元赋值；双线性插值只作敏感性。

输入使用 V3 69,038 行产量面板、`external://ERA5/ERA2016.nc` 至 `ERA2019.nc` 的逐小时 2 m 气温、V3/HE/MA 物候、逐日降水和 GLEAM SMrz。rank 1 代码的 `CalExposure.m` 已核验为：在生育期逐小时温度数组中计数 `temperature >= threshold` 的小时并除以24得到暴露天数，同时以该小时数除以生育期总小时数得到暴露比例；本方向的确认性主暴露据此计算，不将逐日 Tmax/Tmin 近似称为原算法或标准 degree-days。逐日 Tmax/Tmin 仅用于固定32°C事件方向及阈值方向的预设敏感性。若逐小时源不能形成完整窗口或算法数值测试不能通过则停止。主窗口为完整生育季，次级窗口固定 V3-HE 与 HE-MA，边界敏感性为 ±7 与 ±14 日。

阈值栅格的预审计显示：全栅格有效值范围为26.8–44.0°C；按 pixel-is-area 的0.5°原始单元将V3格网中心映射后，69,038行中60,792行、22,180个唯一格网中19,493个获得有效阈值，原始全样本覆盖率分别为88.06%和87.89%。该结果只用于设计可行性，正式门槛仍按五个产区分别计算并要求每区主分析行覆盖不低于80%。

主模型使用 pooled five-zone fully interacted specification、grid FE + province×year FE、固定 GDD10-29、季节降水及平方项。主 estimand 为每区暴露从 P50 到 P90、SR 从五区共同 complete-case 样本 P25 到 P75 的条件损害差异。内部阈值仅作敏感性：28-40°C、0.5°C 步长、外层 LOYO、内层2°空间块 CV，阈值选择模型不得包含 CA 或 CA 交互；固定30/32/35°C为对照。

GLEAM SMrz 的窗口前14日至前1日为 antecedent state；窗口内均值、最低值和相对前置状态变化为通道结果。每区有效阈值覆盖低于80%、少于50个三年以上且具有 CA/EDD within variation 的 grids、阈值以上暴露不足三年、外生阈值 LOYO 预测不优于固定32°C或主交互少于3/4折同向时停止。第一项已触发，因此后续模型门槛不再运行，也不以未运行结果作任何实质推断。

## 4. 热干事件强度—持续时间方向

事件固定为生育期内连续至少3日同时满足 `Tmax >= 32°C` 与 `precipitation < 1 mm`。事件不得由土壤水分定义。grid-year 指标固定为事件数、总事件天数、最长连续期、事件日平均超温强度、累计超温强度、热日中的干旱同期比例及 event indicator。

主模型分别估计 `ca × total_duration` 与 `ca × mean_intensity`；只有 VIF < 5 时联合模型才进入主结果。产量单位始终是 grid-year。SM 事件层定义为 onset 前14日至前1日 antecedent mean、onset 到 event end+3 的最低值相对 antecedent 的 drawdown、结束后首次恢复到 antecedent 90%的 recovery；最长跟踪30日，在下一事件、生育季结束或数据结束时右删失，使用 IPCW/RMST 与空间块 bootstrap。

每区少于50 grids、150 qualifying grid-years、100个完整 antecedent 事件，覆盖不足三年，恢复右删失超过30%，单一年份贡献超过50%事件或主交互少于3/4 LOYO 折同向时停止。

## 5. 共同推断、审核与交付

新方向主区间使用2°空间块 wild bootstrap、1,999 draws、seed 42；grid cluster 与100/200/300 km空间HAC为核验。五区与物候 family 使用 Romano-Wolf stepdown，Holm复核。规格曲线只在同一数据家族内运行。

审核顺序固定为：设计审查 → smoke test → 数据和数值审查 → 完整运行 → 结果审查 → 中文小稿 → 完整性审查 → 独立同行评议 → 最多两轮返修。评分为创新/期刊匹配20、数据/五区支持20、estimand/识别20、SM构念/时序15、精度/稳定性15、可复现/图表10；评分不奖励显著性。小稿低于90不得进入候选集，投稿稿低于95不得定稿。

所有原始数据、派生面板、模型、日志和二进制图进入 `temp/<run-id>/` 且不跟踪。通过审核的公开结果仅以 Markdown 或自包含 HTML 进入 `docs/results/<canonical-id>/`，并同步版本与血缘登记。
