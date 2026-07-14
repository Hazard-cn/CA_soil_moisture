# G185旧方法统一override公共稿最终独立核验

## 最终判定

**判定：`PASS_PUBLIC_FINAL`，91/100。** Round 2遗留的可见图注和符号复用两类Minor均已在公共稿中实际关闭。本轮没有发现新的Critical或Major；存在1项不阻断的公共持久化Minor：三幅图和若干补充机器链接只指向本地未纳入Git的 `temp/`，适合当前本地90分候选稿审阅，但在远端GitHub单独查看Markdown时不会随仓库呈现。该问题不影响当前数值、图注或审查结论，进入95分投稿完成阶段时需生成自包含HTML或另行提供受控的持久图表制品。

审查对象：

- `docs/results/g185-old-method-unified-override-v1/report.md`
- `quality_reports/plans/2026-07-15_g185_override_public_edit_check.md`
- Round 2审查记录、引用核验文件、override机器包和来源FULL_STOP包

本轮没有修改公共稿、机器表、PNG、代码、manifest、历史STOP或谱系；唯一新增文件为本审查报告。

## Round 2两类Minor关闭核验

### 1. 可见caption：CLOSED

公共稿第91、99和117行保留简短图片alt文本，第93、101和119行分别新增独立、可见的斜体图注。三图与三段图注一一对应：

- 图1注明确历史grid加year FE、三个百分比水平分别转换、27个组件水平不显示区间，以及全国端点区间不能替代柱高区间；
- 图2注明统一999次grid Rademacher、seed 42、区别于历史独立区域seed，并禁止把直线读成非线性响应面；
- 图3注明历史FE、统一999次权重、百分比非可加、HHH 25块、SH 13块及SH空间结果只作描述。

这些信息已从不可见alt字段移到标准Markdown会实际呈现的正文图注，Round 2 Minor A完全关闭。

### 2. `delta`符号复用：CLOSED

公共稿第65—68行把含SR四分位距的对数斜率差记为 `Delta_IE,k^log`、`Delta_DE,k^log`和`Delta_TE,k^log`，百分比端点另记为 `B_j,k(x)`；第75和133行把单位SR—胁迫对数斜率检验量记为 `theta_rk=a3_rk*b_rk+c3_rk`。全文检索不存在旧 `delta_rk`/`δ_rk`，第157行恒等式也使用新的IQR差符号。Romano–Wolf检验对象和区域百分比端点不再共用符号，Round 2 Minor B完全关闭。

## 公共稿身份、路径与结构

- 公共稿实算SHA-256为 `8767cf008d67550d9708e313f529dcc6cc1042768413300e8f8037ae9afd5e1a`，与公共编辑检查登记值一致；UTF-8文本共197行。
- 结构包含1个一级标题、11个二级章节、3幅图片和3段可见图注；没有遗留计划稿pending状态或行尾空白。
- 3个图片路径、补充CSV、两个模型代码入口、派生导出脚本、表目录、图目录及override manifest共10个本地相对链接均可解析到现有文件。
- 模型重估入口与派生导出入口继续分开；公共稿没有把 `export_g185_old_method_override.py`重新写成模型重估程序。

公共编辑检查登记的五个输入文件和override manifest哈希均重新计算匹配，包括Round 2审查记录SHA-256 `d6f6b94aa6fbaaacbb2e5fa4f2b79741b352dc60744b26a673fb6270591b9f45`。

## 机器数值独立复核

本轮没有直接采信 `PASS_PUBLIC_EDIT_CHECK`的86项自报，而是从六张机器CSV重新生成公共稿对应显示字符串并逐项比对。独立检查覆盖96项，失败0项：

| 核验对象 | 机器来源 | 独立结果 |
|---|---|---|
| 五区样本N、grids与空间块 | `table1_sample_support.csv` | 5区逐行一致 |
| 全国IE/DE/TE点估计与区间 | `table2_national_iede_endpoints.csv` | 3胁迫×3组件逐行一致 |
| 五区province×year TE与区间 | `table3_five_zone_iede_both_fe.csv` | 5区×3胁迫逐行一致 |
| 三个核心组合六类空间推断 | `table4_core_spatial_inference.csv` | 3组合×6推断层逐行一致 |
| 主要多重检验 | `table5_complete_region_joint_tests.csv` | 15行、45个显示p值零误差 |
| 高温区域omnibus正文值 | `table6_region_omnibus_tests.csv` | Rademacher/Webb原始及Holm值一致 |

关键边界再次确认：

- 全国TE为干旱0.576838%、高温1.157980%、热干1.146443%；
- 旧1.50%、3.27%和2.56%仍只写为DE，校正历史TE仍为1.850%、3.168%和2.425%；
- province×year核心端点仍为0.842%、2.200%和1.622%；
- NE干旱仍为1683/1999、84.1921%，公共稿明确写成“取消执行阻断效力不等于方法学通过”；
- SH仍为903行、284个grids和13个2°块，其显著结果没有被提升为全国主张；
- HHH高温percentile区间未跨零，但Romano–Wolf值仍为0.1950，公共稿没有混淆两类检验。

来源 `full_manifest.json` 实算SHA-256仍为 `3a23e22b421f052a4afc5f83c6aa806dd5a8f081bdb83aded357b2af6ca8aaec`，来源输出20/20哈希匹配；override manifest登记的12项派生输出为12/12匹配。三幅PNG没有重绘，继续为3600×1500像素、299.9994 DPI，哈希分别与manifest登记的 `3a631fae...39f7`、`ce7457b...eeb9`和`82aa88ea...43d9`一致。

`python -m unittest tests.test_export_g185_old_method_override tests.test_g185_old_method_core -v` 的16项测试全部通过；覆盖来源身份、冻结CLI、代数恒等式、完整STOP包、非覆盖保护、Romano–Wolf/Holm和Conley实现。

## DOI与文献主张核验

公共稿包含且只包含以下5个DOI，与三层引用核验文件的集合完全相等：

- `10.1037/a0020761`
- `10.1038/s43016-021-00341-6`
- `10.1038/s41467-020-18631-1`
- `10.1038/s43016-022-00592-x`
- `10.1097/EDE.0000000000000596`

本轮再次通过Crossref Works实时核对题名、作者、期刊、卷和页码/文章号，五项均匹配。Proctor文献作者继续正确写为Proctor、Rigden、Chan和Huybers；Imai及Vansteelandt的书目信息无误。公共稿没有新增37篇核验语料之外的学术文献。Liu研究生态系统生产而非玉米产量，公共稿第21行已明确把它限定为结构性旁证，不再形成对象外推。

## 声明与解释边界

- 顶部元数据同时保留来源FULL_STOP、用户override和84.1921%实际比例，没有把取消门槛写成方法学通过。
- IE/DE/TE始终限定为同期两方程代数组件；摘要、方法、结果和结论均明确百分比端点非严格可加，不能解释为中介份额。
- 全文没有将相关性写成causal effect、identified mediation或robust buffering。G185选择历史、G057排序更高、四年面板、未观测管理混杂和低块数限制均保留。
- 全部15项province×year TE和15项主要多重检验进入正文，45项三层检验保留机器表链接，没有按方向、区间或显著性删行。
- 数据可得性没有承诺超出上游许可的公开共享；代码可得性明确机器数据、日志和二进制图表不进入Git；伦理、CRediT、利益冲突和经费声明没有虚构作者级信息；AI工具使用被如实披露，并保留按目标期刊届时政策调整的边界。
- 公共稿明确标注当前是90分候选稿而非95分投稿完成稿，未冒充完整投稿包。

## 新发现的非阻断Minor

三幅PNG、补充CSV及override manifest位于项目规则不纳入Git历史的 `temp/`，`git ls-files`确认三幅图均未被追踪。当前相对链接在本地工作树全部有效，公共稿也已在代码可得性声明中披露二进制图表不进Git，因此不存在错误陈述；但若只把Markdown推送到远端仓库，三幅图及部分补充链接不会在GitHub渲染或可供外部读者访问。

该问题不阻断当前本地候选小稿PASS，也不授权把PNG直接加入Git。进入95分投稿阶段时应选择以下合规路径之一：生成并审查包含base64图像的自包含HTML置于 `docs/results/g185-old-method-unified-override-v1/`；或把图表上传到具有版本、哈希和持久标识的受控制品存储，并把公共稿链接改为该制品。未完成前不得把当前Markdown称为远端自包含投稿附件。

## 固定六维评分

| 维度 | 得分 | 最终核验依据 |
|---|---:|---|
| 创新与期刊匹配 | 16/20 | 统一组织和推断披露具有价值，但仍是既有G185旧估计量的复核。 |
| 数据和五区支持 | 19/20 | 全国、五区、双样本哈希和15组合完整；SH 13块限制保留。 |
| estimand与识别边界 | 20/20 | IQR对数差、百分比端点和单位SR检验量完全分开；因果与中介边界一致。 |
| SM构念及时序 | 15/15 | SM变量、单位、窗口、RHS、联合complete-case及同期限制完整。 |
| 精度与稳定性 | 12/15 | 推断和多重检验完整，但NE 84.19%、SH 13块及多数组合跨零继续限制稳定性。 |
| 可复现性和图表完整性 | 9/10 | 本地路径、哈希、代码与图注均可复核；远端Markdown不自包含图表。 |
| **合计** | **91/100** | 无Critical、无Major；不按显著性加分，尚未达到95分投稿完成门槛。 |

## 最终结论

公共稿通过最终本地候选稿核验，判定 `PASS_PUBLIC_FINAL`。Round 2两类Minor已经关闭，机器数值、DOI、图注、选择披露和非因果声明一致，没有新Major或Critical。后续若仅做caption排版、自包含HTML或持久链接补全且不改变数值与主张，可作为发布整理；若改变样本、估计量、图中数据、公开结论或引用集合，必须重新进入独立审查。
