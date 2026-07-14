# SR方法组合最终完整性独立审查

## 一、最终判定

**判定：`PASS_PORTFOLIO_INTEGRITY`，96/100。Critical=0，Major=0，Minor=2。**

本审查只读核验当前未提交工作树、三个override公共结果目录、设计—执行—返修—终审记录、机器结果、代码与测试、规范化lineage及公开索引。除本报告外未修改任何文件。审查中先后发现两处把G185方法Round 2的90/100误写成92/100的谱系说明；执行方已分别更正`artifact_registry.csv`与`version_registry.csv`，并重新生成版本文档。本审查复核后确认：方法Round 2为90/100，公共Markdown终审为91/100，自包含HTML终审为92/100；最终候选状态以92/100为准。

## 二、三个方向的状态与历史边界

| Canonical ID | 最终状态 | 独立核验 |
|---|---|---|
| `g185-old-method-unified-override-v1` | 候选稿；自包含HTML终审92/100 | 0 Critical、0 Major；方法Round 2的90分与后续HTML终审92分已分层登记；不是95分投稿完成稿 |
| `compound-event-intensity-duration-override-v1` | `PASS_CANDIDATE`，91/100 | 0 Critical、0 Major、3 Minor；联合持续时间—强度模型为主结果；不是95分投稿完成稿 |
| `regional-threshold-sr-override-v1` | `FAIL / REVIEWED_NOT_CANDIDATE`，72/100 | 公共失败报告PASS只确认披露准确；方法终审仍为0 Critical、3 Major、4 Minor，不进入候选集 |

三个override均使用新canonical ID。其parent依次为`g185-old-method-unified-v1`、`compound-event-intensity-duration-v1`和`regional-threshold-sr-v1`，`supersedes`均为空；旧版FULL_STOP、small-smoke STOP和Stage 1 STOP报告未出现在本轮修改清单中，未被覆盖、删除或改写。`docs/results/index.md`、`docs/results/README.md`、`docs/VERSION_MAP.md`和版本登记对两个候选稿及一个失败reference的分组一致。

## 三、公开主张与机器证据抽样复算

G185全国TE机器值重新读取为干旱0.576838%、高温1.157980%、热干1.146443%，与公共稿一致；旧1.50%、3.27%和2.56%仍只标为DE，校正历史TE与province-by-year FE衰减均完整披露。公共HTML SHA-256为`9d5d9fc0c795d46712ca94320796e59fe62b467a76606745248a71c0a212a1e5`，与artifact登记一致。IE、DE和TE始终限定为同期两方程代数组件，没有被写成已识别因果中介。

事件联合模型的黄淮海持续时间机器值重新读取为低SR −3.3406%、高SR 7.7076%、乘法尺度对比11.4300%及区间[5.1724%, 18.2377%]；强度对比为3.4884%、区间[−2.1691%, 9.3294%]、Romano–Wolf p=0.817。公开稿同时保留低SR负变化转为高SR正变化、联合强度不明确、南方边界结果、其余区域区间跨零、分别模型、严格窗口、LOYO限制和五区恢复区间均跨零。自包含三图HTML SHA-256为`d92d7c489f7579cea7328275716704a0ed52575e1110bb6d28084e17420da457`，与登记一致。

阈值方向黄淮海完整窗口机器值重新读取为低SR 0.58216、高SR 0.71138、高减低0.12922；公共失败报告准确说明两条条件变化均为正，不能解释为温度损害缓冲。东北和西南反向、华南两条负变化但对比不精确、西北多重校正后不通过、四川最终无模型支持、SM推断与物候边界敏感性不完整等结果均未删除。公共报告SHA-256为`3738baac2ea8fee851a7986f060f1b3ed51850955342771afc1838a51e3ef68b`。

用户提供`maize.tif`重新计算得到MD5 `0d9e6c21bf1b25f113e14315863372f2`、SHA-256 `f05e634664c4c6c2e2df352702acd421507162bc54cc067649071521ab1285b0`，与Zenodo核验记录、公共失败报告及lineage一致。G185五个DOI、事件方向两个核心DOI、阈值论文/Zenodo/Figshare DOI均与各自三层核验记录一致；未发现新增未核验文献主张。

## 四、方法边界与结果完整性

三个方向均保留五个命名产区，没有按方向或显著性删除区域。G185完整报告15个产区—胁迫组合及空间推断；事件稿完整报告联合模型、分别模型、严格V3—MA窗口、Webb、100/200/300 km HAC、R/Stata复算、土壤水分重叠敏感性与固定IPCW恢复；阈值失败报告完整保留全窗口、V3—HE、HE—MA、LOYO和SM结果，并明确未完成±7/±14日边界敏感性和阶段联合Wald是失败Major。

土壤水分边界保持一致：G185为同期代数组件；事件方向为antecedent、drawdown和recovery的描述性通道证据；阈值方向的SM未放入主产量方程后再解释为中介，且空间联合推断不足被保留为失败依据。三个方向均排除因果效应、因果中介和全国一致缓冲等超范围主张。设计计划、方法登记及公共稿均禁止通过阈值、窗口、样本、区域、函数形式或推断方式搜索更有利结论；阈值方向依两轮上限停止，事件联合模型即使使强度结果减弱仍被置于主结果。

## 五、代码、测试、lineage与Git边界

组合测试分两种框架执行：26项`unittest`覆盖G185导出/自包含HTML及阈值core/inference/runner，16项`pytest`覆盖冻结人工事件与SM序列，合计42/42通过。当前diff中的34个Python文件均用内存`compile()`逐一语法编译，34/34通过且未生成待跟踪字节码。`version_lineage.py validate --strict`验证632行、0错误；`build-docs --check`返回文档为当前状态；`git diff --check`通过。

`validate --strict --verify-local`仍返回81个错误，但错误全部位于旧`artifact_registry.csv`第2—74行和旧`sample_rules.csv`第3—29行；HEAD分别已有73个artifact行和28个sample行。本轮新增19个artifact从第75行开始、新增2个sample从第30行开始，未产生任何local verify错误。因此81项均为历史基线的缺失本地制品或旧代码CRLF/哈希漂移，不是本轮引入；本轮不应借机改写历史哈希。

当前拟提交范围不含`temp/`、`data/`、日志、PNG/JPEG、DTA、Parquet、压缩机器表或模型对象。新增HTML仅为规则允许的自包含公共结果；修改的CSV仅是项目规范化lineage/version元数据登记，不是分析数据或机器结果。未发现绝对本机路径、`file://`资源或被误纳入Git的二进制分析制品。

仓库policy工具的`--source index`只检查暂存快照；在尚未暂存时运行只能重复检查HEAD，不能证明当前工作树合规。正确顺序是：暂存前完成测试、strict、build-docs和diff检查；仅暂存预期代码、审查记录、lineage与`docs/results` Markdown/自包含HTML；随后运行`python .github/scripts/check_repository_policy.py --source index`。如果该检查后再修改文件，必须重新暂存并重新运行；提交后还应以`--source HEAD`或明确commit SHA复核。未通过暂存快照policy不得commit、push或建PR。

## 六、评分与残余Minor

| 维度 | 得分 | 依据 |
|---|---:|---|
| 状态、审查链与历史保全 | 20/20 | 两候选一失败映射正确；旧STOP未覆盖；两轮规则完整 |
| 公开主张与机器一致性 | 20/20 | 关键值、区间、哈希独立抽样一致；反向与非显著结果完整 |
| 方法、SM与窗口边界 | 19/20 | no-search和非因果边界清楚；候选稿仍有已披露的投稿级Minor |
| 代码、测试与可复现性 | 20/20 | 42项组合测试、34个Python编译及跨语言/哈希闭环通过 |
| Lineage、索引与Git范围 | 18/20 | 632行strict和文档检查通过；历史81项local verify错误仍存在 |
| 公共制品与期刊前状态 | 9/10 | 两个候选均有自包含图表入口；均明确未达95分投稿完成状态 |
| **总分** | **96/100** | **0 Critical，0 Major，2 Minor** |

残余Minor为：第一，81项历史`verify-local`错误仍需未来单独治理，但不得在本轮把历史漂移冒充本轮修复；第二，repository policy必须在正式暂存后对index运行，本只读审查不授权或代替暂存操作。两项均不改变本轮三个方向的数值、状态、公开主张或候选/失败映射。

## 七、结论

本轮组合满足`PASS_PORTFOLIO_INTEGRITY`条件。允许进入正式暂存与repository-policy门槛；只有暂存快照policy通过后，才允许继续commit、push和PR。最终候选集为G185 92/100与事件稿91/100；地区异质温度阈值方向保持72/100的已审查失败reference，不得提升为候选稿。
