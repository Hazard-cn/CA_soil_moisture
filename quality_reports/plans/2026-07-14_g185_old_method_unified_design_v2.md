# G185 旧方法统一稿：冻结设计 v2

## 状态与审计链

- Canonical ID：`g185-old-method-unified-v1`
- Design version：`v2`
- 当前状态：`DESIGN_PASS_92_SMOKE_AUTHORIZED`
- 第一轮设计审计：78/100，`REVISE`；三个Critical和七个Major已转化为下述机器接口、推断与停止规则。
- 独立复审第1轮：84/100，`REVISE`；六个Major已在第2轮前关闭。
- 独立复审第2轮：92/100，`PASS`；无Critical、无Major，仅余数值实现约定，已冻结如下。
- 禁止范围：`g185-response-surface-v3`、RCS/GAM联合响应面、DML、causal forest，以及把IE/DE/TE称为已识别因果中介。

## 研究问题与解释边界

研究问题固定为：在G185样本和既定线性两方程规格下，较高观测SR是否与干旱、高温和热干条件下较平缓的玉米产量损害斜率相关，这种条件关联在五个玉米产区之间如何变化，其中有多少与同期GLEAM根区土壤水分方程形成的代数组件一致？

全文只使用“条件关联”“损害斜率差异”“两方程代数组件”。G185来自既有尺度筛选，G057在综合排序中高于G185；本稿必须披露完整筛选过程，不称G185为唯一最优或预注册尺度。

## 数据、哈希与样本

固定输入：

- GGCP10基础面板 SHA-256：`03a36e25ed5375d055c7dc58e0b3b7b237ab4b16b9ce89e61f1b1b7fc3dcbaaa`。
- V3 hot-dry来源 SHA-256：`3f3f045a8040b876565873febab3918d166b8bd6f6938669b48c634a46172517`。
- 显式G185样本排序键保留两个不可互换的 SHA-256：历史兼容值 `5474250d140bef9a8fc0957158ed815f635220e0c0df7080d7a1b5f7d4469b89`（`legacy-sample-key-pipe-v1`）和规范化值 `36029c5f8ba689a1cbf6a14b688e8a43342ab8b7acd9b704136cb152fa170bcb`（`sample-key-csv-v1`）。两者必须同时通过；前者用于核对历史证据，后者用于新运行的跨实现复现。

新入口必须显式执行G185样本谓词，不得通过 `unique_variants()` 枚举序号恢复样本。基础面板与V3 hot-dry sidecar先分别断言 `grid_id year` 唯一，再按这两个键执行 `one_to_one` 左合并并要求全部匹配；`HotDryPr_full=hotdrydays_ge32_pr_lt1`。G185谓词按以下顺序机械执行：`ggcp10_maize_frac>=0.05`；`main_sample==1`；`0.5<=yield_tons_ha<18`；按grid和year排序后，若相邻年份连续且 `abs(ln_yield_t-ln_yield_t-1)>1`，则相邻两行的对应previous/next jump标记触发排除；`gleam_smrz_sd>=0.001`。`zone_core=0`表示不因`Other`排除全国样本，`sm_coverage=sr_within=years_ge3=stable_province=0`表示这些规则不参与谓词。结果必须断言46,299行、13,236个grids，五个命名产区44,556行、12,745个grids，并逐项断言五区×三胁迫共15个区域模型。`Other`只作描述。

`D_full` 与 `W_full` 已完成代码追溯：`scripts/stata/v2_step0_preamble.do` 和 `scripts/stata/v3_step0_preamble.do` 将完整生育季月度加权SPEI-6均值 `spei6_mean` 分别转换为 `D_full=max(0,-spei6_mean)` 与 `W_full=max(0,spei6_mean)`；二者单位均为无量纲SPEI尺度，`D_full=0`表示该SPEI-6值非负，`W_full=0`表示该值非正。`ggcp10_parallel_rules_69038_search.load_panel()` 只把原变量复制为 `D_full_raw`、`W_full_raw`，没有再缩放。对基础面板69,038行的独立复算显示两式最大绝对差均为 `1.1826e-07`，符合float32精度。新入口仍须逐行断言该关系；无法在输入中复算或误差超过 `1e-6` 即STOP。

## 估计量

对胁迫 `k` 与区域 `r`：

\[
IE_k(s)=(a_{1k}+a_{3k}s)b_k,\quad
DE_k(s)=c_{1k}+c_{3k}s,\quad
TE_k(s)=IE_k(s)+DE_k(s).
\]

全国端点固定为：

\[
\Delta TE_k^N=100\{\exp([TE_k(P75)-TE_k(P25)]Q_{90}^N(H_k))-1\}.
\]

区域端点固定为：

\[
\Delta TE_{rk}=100\{\exp([TE_{rk}(P75_r)-TE_{rk}(P25_r)]Q_{90,r}(H_k))-1\}.
\]

连续曲线固定为：

\[
C_{rk}(x)=100\{\exp([TE_{rk}(P75_r)-TE_{rk}(P25_r)]x)-1\},\quad x\in[0,Q_{90,r}(H_k)].
\]

区域端点使用各区不同SR IQR和胁迫P90，因此只能描述区域内幅度，不能据此进行区域大小排序。正式异质性检验使用每单位SR—胁迫斜率 `delta_rk=a3_rk*b_rk+c3_rk`，由同步bootstrap形成五区联合协方差并进行omnibus Wald检验。

## 主规格与稳健性

历史复现主规格固定为grid FE + year FE。新增稳健性固定为grid FE + province×year FE。两条方程在同一重抽样权重下联合重估，区域模型使用全国统一的重抽样权重；不得为各区域另设随机种子。

完整两方程RHS冻结如下，其中 `M=gleam_smrz_mean_raw`，共同控制向量 `Z=(pr_sum_raw, et0_sum_raw, gdd_10_30_raw, irr_frac_raw, aridity_raw)`：

| 胁迫 | SM方程RHS | 产量方程RHS |
|---|---|---|
| 干旱 | `D_full_raw ca_raw SR_x_D_full_raw W_full_raw hdd_ge32_raw Z` | `D_full_raw ca_raw SR_x_D_full_raw M W_full_raw hdd_ge32_raw Z` |
| 高温 | `hdd_ge32_raw ca_raw SR_x_Heat_full_raw D_full_raw W_full_raw Z` | `hdd_ge32_raw ca_raw SR_x_Heat_full_raw M D_full_raw W_full_raw Z` |
| 热干 | `HotDryPr_full_raw ca_raw SR_x_HotDryPr_full_raw D_full_raw hdd_ge32_raw W_full_raw Z` | `HotDryPr_full_raw ca_raw SR_x_HotDryPr_full_raw M D_full_raw hdd_ge32_raw W_full_raw Z` |

每个区域—胁迫的两条方程必须使用其RHS联合complete-case；五区比较使用15个模型的同步抽样，但保留历史各区域complete-case，不事后改成更有利样本。

`M`是完整生育季GLEAM 4.2b根区土壤水分均值，单位m3/m3；项目完整窗口为 `v3_doy-30` 至 `ma_doy`。它与同季胁迫和产量同期，可能位于暴露之后，因而不能建立时间先行的因果中介识别；IE/DE/TE始终只作同期两方程代数组件。SM方程的因变量和产量方程的 `M` 使用同一数值与同一complete-case。

推断层固定为：

1. 历史复现：grid-cluster wild-score bootstrap，999次，seed 42。对吸收固定效应后的线性模型，令grid得分 `S_g=sum_t x_gt*u_gt`，每次抽取Rademacher权重并计算 `beta_b=beta+(X'X)^(-1)sum_g(w_gb*S_g)`；不完全重估固定效应。IE/DE/TE对每个 `beta_b` 非线性重算，95%区间取1,999或999个非线性统计量的2.5%与97.5%分位数。
2. 新增主稳健性：2°空间块固定锚定全球原点 `(-180,-90)`，`block_lon=floor((longitude+180)/2)`、`block_lat=floor((latitude+90)/2)`。全国G185含151块；五个命名区分析宇宙含149块。先把观测得分在块内求和，再使用与第1项相同的linearized wild-score公式。区域模型必须从这149个命名区块的同一权重向量取对应块权重，1,999次、seed 42，不按区域独立抽取。
3. Rademacher权重为 `{-1,+1}`、各概率1/2。Webb六点权重为 `{-sqrt(3/2),-1,-sqrt(1/2),sqrt(1/2),1,sqrt(3/2)}`、各概率1/6；Webb同样运行1,999次、seed 42并使用percentile interval。HHH只有25个、SH只有13个有效块，因此Webb为强制敏感性，SH标为低有效块数描述性结果，不承担摘要主张。
4. 空间HAC固定为grid聚合score的Conley型估计。令 `B=(X'X)^(-1)`、`S_g=sum_t x_gt*u_gt`，则 `M_L=sum_g sum_h K(d_gh/L) S_g S_h'`，其中使用全部有序grid对并包含 `g=h` 对角项，`d_gh` 为grid中心haversine距离，`K(d/L)=max(1-d/L,0)`，`L`固定为100/200/300 km；数值实现对 `M_L` 与最终协方差显式对称化。协方差为 `V_L=c*B*M_L*B`，`c=[G/(G-1)]*[(N-1)/(N-K)]`，G为grid数、N为观测数、K为吸收后RHS列数；报告基于正态临界值的双侧95%区间。不进行结果导向的特征值裁剪或PSD修复；若最小特征值小于 `-1e-8*max(1,max(diag(V_L)))`，该带宽判为无效，否则仅把绝对值小于该容差的负零对角数值置零。score必须在对应规格的固定效应吸收和冻结complete-case之后计算。该定义允许grid内任意时间相关，只对grid间相关施加空间核；三个带宽全部报告，不能按结果选择。
5. 15个 `delta_rk` 的同步bootstrap向量形成联合协方差。主检验族为15个双侧 `H0:delta_rk=0`：先以同步bootstrap标准差 `se_j=sd(delta_jb)` 固定标准化，观测统计量为 `abs(delta_hat_j/se_j)`，中心化bootstrap统计量为 `abs((delta_jb-delta_hat_j)/se_j)`，按max-T逐步剔除算法实施Romano–Wolf stepdown；Holm为复核。每个胁迫另检验区域同质性 `H0:delta_NE,k=delta_HHH,k=delta_NW,k=delta_SW,k=delta_SH,k`，对比矩阵固定为相对NE的四行差，观测Wald统计量为 `(R*delta)'[R*V*R']^+ (R*delta)`；`V`固定为同步bootstrap样本协方差，秩按特征值容差 `1e-10*lambda_max` 计算，自由度等于 `rank(RVR')`，若秩小于4则该omnibus无效并触发STOP。bootstrap p值以 `R*(delta_b-delta_hat)` 的同式统计量为零假设分布计算，三项omnibus p值再用Holm校正。协方差、p值和校正顺序均不能按结果更改。
6. grid聚类、Rademacher空间块、Webb空间块与三个HAC带宽全部进入同一稳健性表；任何实现失败均保留日志并按下述STOP规则处理，不用替代规格补位。

## 非覆盖执行接口

禁止直接运行会写回原项目历史目录的旧脚本。新增统一入口必须支持：

```text
--project-root
--worktree-root
--base-dta
--hotdry-dta
--output-dir
--fe grid_year|grid_provyear
--score-cluster grid|spatial_block
--block-degrees 2
--reps 999|1999
--seed 42
```

`project-root`只作为只读数据与历史真值根，`worktree-root`只作为代码与输出根；新入口不得导入任何在模块顶层创建目录、写文件或执行分析的旧模块，所需纯函数在新模块中以来源注释和哈希冻结。`output-dir` 必须不存在；若已存在立即退出，且不提供 `--overwrite`。程序须先将 `worktree-root/temp` 与 `output-dir` 解析为绝对规范路径，要求 `output-dir` 是前者的严格后代而不等于前者；使用 `os.path.commonpath` 再核验，拒绝任何 `..` 逃逸。对所有已存在祖先逐一拒绝Windows reparse point、junction或symlink；创建目录后再次解析并复核同一后代约束。入口不得修改原项目、历史run或用户主目录中的任何文件。所有数据、日志、图和模型只写入隔离worktree的 `temp/2026-07-14_g185_old_method_unified_v1/`；通过审查的Markdown/自包含HTML才进入 `docs/results/g185-old-method-unified-v1/`。

run manifest必须记录全部导入脚本及其哈希、输入输出哈希、Git提交、Python/R/Stata版本、FE、权重类型、空间块定义、完整样本谓词、样本键哈希、分位点和公开主张。

样本键哈希固定为双序列化断言。`legacy-sample-key-pipe-v1` 选择 `grid_id,year` 两列，按数值型 `grid_id`、数值型 `year` 稳定升序排列，每条记录写为 `grid_id|year`，记录之间使用LF，不含表头且末条记录后不加LF，以UTF-8编码后计算SHA-256；预期值为 `5474250d140bef9a8fc0957158ed815f635220e0c0df7080d7a1b5f7d4469b89`。`sample-key-csv-v1` 将 `grid_id`规范化为UTF-8字符串、`year`规范化为无小数四位ASCII整数，按字符串 `grid_id`、数值 `year` 稳定升序排列，使用UTF-8、LF换行、逗号分隔、包含一次ASCII表头 `grid_id,year`，所有字段采用CSV最小双引号转义；预期值为 `36029c5f8ba689a1cbf6a14b688e8a43342ab8b7acd9b704136cb152fa170bcb`。manifest必须同时保存算法版本、哈希值和通过状态，不得把两个值写成同一算法的替代结果。

2026-07-14 smoke前置检查发现原设计将历史值 `5474250d...` 错标为 `sample-key-csv-v1`。独立集合核验显示显式谓词与历史枚举路径均为46,299个键，双向集合差均为0；冲突仅来自序列化元数据。上述双哈希修订不改变输入、样本、估计量、模型或公开主张，完整审计记录见 `quality_reports/plans/2026-07-14_g185_sample_key_hash_audit.md`。

Romano–Wolf数值约定固定为：bootstrap标准差使用 `ddof=1`；经验尾概率以 `>=` 计数并使用 `(1+#)/(B+1)` Monte Carlo修正；同值统计量按预设检验顺序 `NE,HHH,NW,SW,SH` × `drought,heat,hotdry`稳定处理；逐步调整p值按剔除顺序执行累计最大值单调化。每组调整p值必须在manifest注明FE与bootstrap层：历史grid-year/grid-cluster、新增grid-province-year/2°Rademacher、新增grid-province-year/2°Webb。

## 数值验收

新版统一入口必须重新生成、而不是复制旧表，并在项目容差内满足：

- 全国P75−P25的TE：干旱0.576838%、高温1.157980%、热干1.146443%。
- NE干旱1.850220% [1.231529, 2.555323]。
- HHH高温3.168372% [2.067127, 4.258913]。
- HHH热干2.425434% [1.038955, 3.871321]。
- 三条0—P90曲线的P90端点与校正TE表最大绝对差小于 `1e-10`。
- 15组 `TE_delta=IE_delta+DE_delta` 最大绝对误差小于 `1e-10`。
- 仅对历史 `grid FE + year FE + grid-cluster wild-score bootstrap` 复现层，要求新旧点估计误差小于0.01个百分点、SE误差小于0.05且显著性等级一致；该容差不用于新增province×year、空间块或HAC结果。

旧1.50%、3.27%、2.56%只能标为DE，不得出现在TE列或TE图注中。

## 图表与完整报告

主图固定为：全国P25/P50/P75下IE/DE/TE及P75−P25；NE干旱、HHH高温和HHH热干的0—P90旧线性曲线；五区×三胁迫完整“代数综合分量（TE）”矩阵。矩阵按预设产区与胁迫顺序排列，不按估计值排序，使用以零为中心的固定对称色阶，并在SH单元标注“低有效空间块数”。附图报告三核心组合IE/DE/TE分量和FE/空间推断稳健性。全部图为白底、无衬线、300 DPI、约12×5英寸。

所有15个区域—胁迫组合、omnibus检验和非显著结果必须进入机器表；不得只展示核心三组。

## STOP规则

任一条件成立即停止投稿稿件，仅保留可复核历史证据报告：

- 输入哈希、样本键哈希、行数、grid数或五区计数不符；
- `D_full`/`W_full`不能按已追溯公式逐行复算，或最大绝对误差超过 `1e-6`；
- 数值验收不通过，或TE再次被混写为DE；
- 三个核心区域—胁迫组合在province×year规格中任一点估计符号反转，或2°Rademacher同步bootstrap中同向非线性统计量比例低于90%；
- 2°Rademacher主空间块推断无法形成有效区间；Webb无法运行；或100/200/300 km任一预设HAC带宽不能形成有限、满足预设特征值容差的协方差；
- 全样本/命名区空间块数不是151/149，任一同步抽样的区域权重不等于对应全国块权重，15模型或15维联合协方差不完整，任一omnibus `rank(RVR')<4`，或Romano–Wolf不能对完整15检验族给出调整p值；
- 路径解析、严格后代、reparse point或非覆盖断言任一失败；
- 使用各区不同端点进行区域大小排序；
- 无法完整披露G185尺度筛选；
- 使用因果中介语言或引入明确排除的方法族。

## 设计通过标准

独立复审必须确认无Critical、无未解决Major且评分不低于90，才允许编写并运行小样本smoke test。smoke test只验证接口、样本谓词、数值代数、空间块和HAC可计算性，不接触主结果筛选。

province×year键固定为规范化省名字符串与四位年份的笛卡尔键；必须断言87个非空组。grid FE、year FE和province×year FE均采用交替投影，收敛条件为所有吸收组残差均值最大绝对值小于 `1e-10`。不递归删除singleton；singleton grid吸收后应产生零within信息并保留在样本审计中，程序必须记录其数量、吸收后零范数行数、设计矩阵秩与每一规格实际N。任何关键RHS列被吸收为零或设计降秩均触发STOP。
