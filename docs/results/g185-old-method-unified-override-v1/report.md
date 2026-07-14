# 秸秆还田采用强度与中国玉米极端胁迫损失斜率：G185网格面板的同期土壤水分两方程分解

- Canonical ID：`g185-old-method-unified-override-v1`
- 文稿类型：中文实证小稿
- 审查状态：`PASS_ROUND2`，90/100；无Critical、无Major，尚未达到95分投稿完成门槛
- 数据家族：GGCP10-G185，2016—2019年
- 机器结果来源：`g185-old-method-unified-v1`已审查`FULL_STOP`归档的哈希锁定派生包
- Override边界：用户取消“东北干旱2°空间块Rademacher同向比例至少90%”的执行阻断效力；实际比例84.1921%继续完整报告
- 解释边界：IE、DE和TE均为同期两方程代数组件，不是已识别的因果中介效应

## 摘要

极端干旱、高温和热干复合暴露可能改变玉米产量，而秸秆还田采用强度是否与较平缓的胁迫损失斜率相关，以及这种关联是否与根区土壤水分的同期变化一致，仍缺少统一的全国与产区证据。本研究使用中国0.1°网格的2016—2019年G185面板，保留46,299个grid-years和13,236个grids，估计grid固定效应加year固定效应的历史线性两方程，并以grid固定效应加province×year固定效应、2°空间块wild bootstrap及100—300 km空间HAC进行核验。全国样本中，当胁迫取P90、秸秆还田采用强度由P25增加至P75时，干旱、高温和热干分别转换的代数TE端点为0.577%（95%区间0.181%—0.972%）、1.158%（0.753%—1.621%）和1.146%（0.660%—1.696%）。分别转换的同期土壤水分IE端点为0.024%、0.037%和0.125%，其幅度小于对应DE端点；由于百分比端点经非线性指数转换后并不严格可加，这种差异不能解释为IE占TE的比例，更不能据此建立土壤水分因果中介。历史区域规格中，东北干旱、黄淮海高温和黄淮海热干的校正TE分别为1.850%、3.168%和2.425%；加入province×year固定效应后分别缩小至0.842%、2.200%和1.622%，只有黄淮海高温的2°Rademacher区间未跨零。东北干旱在1,999次空间扰动中的正向比例为84.19%，低于原90%门槛；其点估计未反号，但空间不确定性较强。结果支持“秸秆还田采用强度与部分胁迫损失斜率较平缓相关”的有限表述，不支持稳定的全国因果效应或已识别的土壤水分中介机制。

关键词：秸秆还田；玉米产量；干旱；高温；热干事件；土壤水分；空间推断

## 一、研究问题与文献定位

本文检验三个相互关联但不等同的问题。第一，在既定G185样本中，较高观测秸秆还田采用强度是否对应较平缓的干旱、高温和热干产量损害斜率。第二，该条件关联是否在东北、黄淮海、西北、西南和华南五个玉米产区之间不同。第三，完整生育季GLEAM根区土壤水分方程产生的同期代数组件能够解释多少TE差异。

文献将水分供给与温度暴露共同纳入作物产量函数，并提示温度—土壤水分耦合及区域状态依赖需要在解释中显式处理（Lesk et al., 2021；Proctor et al., 2022；Liu et al., 2020）。因果中介文献同时表明，把暴露后的同期变量放入第二条方程并不能自动识别natural indirect effect（Imai et al., 2010；Vansteelandt et al., 2017）。因此，本文的贡献不是识别新的因果中介，而是统一复现全国、连续区域曲线和五区IE/DE/TE代数分解，并把更强固定效应和空间推断下的衰减与不确定性放入同一结果体系。Liu et al.（2020）研究的是全球生态系统生产而非玉米产量，本文只把它作为土壤水分状态依赖的结构性旁证。

## 二、数据、样本与选择披露

G185通过既有尺度筛选形成，并非预注册尺度，也不是筛选结果中唯一或综合排序最优的尺度；既有综合排序中G057高于G185。本文不比较不同尺度的显著性，也不据此重新选择尺度。冻结样本依次要求`ggcp10_maize_frac>=0.05`、`main_sample==1`、`0.5<=yield_tons_ha<18`、排除相邻连续年份中`abs(ln_yield_t-ln_yield_t-1)>1`的成对成员，以及`gleam_smrz_sd>=0.001`。样本键同时通过历史序列哈希`5474250d...b89`和规范序列哈希`36029c5f...bcb`。

全国样本包含46,299个grid-years和13,236个grids；五个命名产区包含44,556行和12,745个grids。三个胁迫在同一区域使用相同complete-case行数。黄淮海有25个2°有效空间块，华南只有13个，因此华南的空间块推断只能作为低块数描述性证据。

| 产区 | grid-years | grids | 2°空间块 | 推断说明 |
|---|---:|---:|---:|---|
| 东北（NE） | 20,794 | 5,715 | 45 | 常规报告 |
| 黄淮海（HHH） | 12,213 | 3,324 | 25 | 低于30块，结合Webb核验 |
| 西北（NW） | 3,414 | 1,191 | 50 | 常规报告 |
| 西南（SW） | 7,232 | 2,231 | 31 | 常规报告 |
| 华南（SH） | 903 | 284 | 13 | 低块数描述性结果 |

## 三、模型、估计量与推断

令`M=gleam_smrz_mean_raw`，单位为m³/m³，窗口为项目定义的完整生育季`v3_doy-30`至`ma_doy`；令共同控制向量`Z=(pr_sum_raw, et0_sum_raw, gdd_10_30_raw, irr_frac_raw, aridity_raw)`。对每个胁迫`k`，同期两方程写为：

\[
M_{it}=a_{1k}H_{kit}+a_{2k}SR_{it}+a_{3k}(SR_{it}\times H_{kit})+\Gamma_kX_{kit}+\alpha_i+F_{it}+u_{kit},
\]

\[
\ln(Y_{it})=c_{1k}H_{kit}+c_{2k}SR_{it}+c_{3k}(SR_{it}\times H_{kit})+b_kM_{it}+\Pi_kX_{kit}+\alpha_i+F_{it}+\varepsilon_{kit}.
\]

其中`α_i`为grid固定效应；历史层的`F_it=λ_t`为year固定效应，新增层的`F_it=λ_{p(i),t}`为province×year固定效应。三类胁迫的完整RHS如下，产量方程只比对应SM方程增加同期`M`，从而保证两方程使用同一个联合complete-case样本。

| 胁迫 | SM方程RHS | 产量方程RHS |
|---|---|---|
| 干旱 | `D_full_raw ca_raw SR_x_D_full_raw W_full_raw hdd_ge32_raw Z` | `D_full_raw ca_raw SR_x_D_full_raw M W_full_raw hdd_ge32_raw Z` |
| 高温 | `hdd_ge32_raw ca_raw SR_x_Heat_full_raw D_full_raw W_full_raw Z` | `hdd_ge32_raw ca_raw SR_x_Heat_full_raw M D_full_raw W_full_raw Z` |
| 热干 | `HotDryPr_full_raw ca_raw SR_x_HotDryPr_full_raw D_full_raw hdd_ge32_raw W_full_raw Z` | `HotDryPr_full_raw ca_raw SR_x_HotDryPr_full_raw M D_full_raw hdd_ge32_raw W_full_raw Z` |

每个全国或区域—胁迫模型先同时检查两方程结果变量和全部RHS，只有所有字段均非缺失的`grid_id year`行才进入两条方程；不得分别为SM方程和产量方程选择样本。对胁迫`k`和SR水平`s`，下列量首先定义在`ln(yield)`对胁迫的线性预测斜率尺度：

\[
IE_k^{log}(s)=(a_{1k}+a_{3k}s)b_k,\qquad
DE_k^{log}(s)=c_{1k}+c_{3k}s,\qquad
TE_k^{log}(s)=IE_k^{log}(s)+DE_k^{log}(s).
\]

因此，`TE=IE+DE`是对数斜率尺度的代数恒等式。令`q=P75(SR)-P25(SR)`、胁迫水平为`x`，P75相对P25的对数斜率差记为`Δ_IE,k^log=a3k×bk×q`、`Δ_DE,k^log=c3k×q`和`Δ_TE,k^log=Δ_IE,k^log+Δ_DE,k^log`。三类百分比端点分别定义为：

\[
B_{j,k}(x)=100\{\exp(\Delta_{j,k}^{log}x)-1\},\qquad j\in\{IE,DE,TE\}.
\]

指数转换是非线性的，故一般有`B_TE,k ≠ B_IE,k+B_DE,k`。本文表格和图形中的IE、DE、TE百分比均由各自的对数斜率组件单独转换，不能解释为百分比尺度上的严格可加分解。固定SR水平`s`的图1柱高同样是`100{exp[IE_log(s)x]-1}`、`100{exp[DE_log(s)x]-1}`和`100{exp[TE_log(s)x]-1}`分别转换后的水平，不能通过相减柱高恢复P75−P25端点。

连续区域曲线只把同一线性`Δ_TE,k^log`从胁迫0计算至区域P90，不是非线性响应面。历史grid wild使用全国13,236个grid的同步Rademacher权重、999次、seed 42；新增空间层以全球原点确定2°块，`block_lon=floor((longitude+180)/2)`、`block_lat=floor((latitude+90)/2)`，全国有151块、五个命名区联合得分有149个非零块，Rademacher与Webb均为1,999次、seed 42，并对所有区域模型使用同一组同步权重。bootstrap区间是对每次非线性端点重新计算后的2.5%和97.5%分位数。

Conley型HAC先把吸收固定效应后的得分聚合到grid，再对全部有序grid对使用Bartlett核`K(d/L)=max(1-d/L,0)`，固定带宽为100、200和300 km，并以正态临界值形成区间。五区15项主要检验针对单位SR—胁迫对数斜率`θ_rk=a3_rk×b_rk+c3_rk`，而不是区域特定百分比端点；同步bootstrap实施Romano–Wolf max-T stepdown，Holm为复核。区域同质性使用相对东北的四行对比矩阵、rank-4 Wald omnibus，并对三个胁迫的p值再作Holm校正。

完整生育季GLEAM SMrz与胁迫和产量同期，可能位于胁迫之后。因而IE只是上述同期两方程的代数组件，DE只是控制同期SM后的剩余斜率组件。历史上曾被写成TE的1.50%、3.27%和2.56%实际分别是东北干旱、黄淮海高温和黄淮海热干的DE；本文只把1.850%、3.168%和2.425%称为相应校正TE。

## 四、全国结果

在历史grid加year固定效应规格中，SR从P25（0.0487）提高到P75（0.5314）时，三类胁迫的TE端点均为正。这里的“正”表示高SR对应较小的负向胁迫斜率或更大的条件产量差异，并不等同于干预效应。

| 胁迫 | IE差异，% [95%区间] | DE差异，% [95%区间] | TE差异，% [95%区间] |
|---|---:|---:|---:|
| 干旱 | 0.0238 [-0.0013, 0.0524] | 0.5529 [0.1577, 0.9490] | 0.5768 [0.1815, 0.9720] |
| 高温 | 0.0374 [0.0002, 0.0771] | 1.1202 [0.7085, 1.5694] | 1.1580 [0.7531, 1.6208] |
| 热干 | 0.1248 [0.0780, 0.1722] | 1.0203 [0.5244, 1.5494] | 1.1464 [0.6595, 1.6956] |

三个分别转换的IE端点幅度都小于对应DE端点。高温IE下界实值为0.000186%，表中以四位小数显示为0.0002%，不是零。热干IE区间未跨零，但这种统计结构仍不能替代中介识别，因为SM与胁迫同期且可能受到未观测时变条件共同影响。上述三个百分比端点并不严格可加，例如干旱IE端点与DE端点之和为0.576706%，TE端点为0.576838%；差异来自非线性指数转换，而不是代数恒等式失效。

![全国不同SR分位点下的同期两方程代数组件](../../../temp/2026-07-15_g185_old_method_unified_override_v1/figures/fig1_national_iede.png)

*图1注：历史grid加year固定效应。柱高是在胁迫P90处对IE、DE和TE对数斜率组件分别作指数转换的百分比水平，三者在百分比尺度不严格可加。图中不显示27个组件水平各自的区间；上表报告的是不同estimand，即P75相对P25端点的区间，不能替代柱高区间。*

## 五、产区异质性

历史区域规格的三个核心组合均为正：东北干旱1.850%（历史独立区域复现区间1.232%—2.555%）、黄淮海高温3.168%（2.067%—4.259%）和黄淮海热干2.425%（1.039%—3.871%）。图2使用全国统一的999次grid权重，因此其带状区间与上述历史独立区域随机种子复现区间略有差异，但点估计完全一致。连续曲线的直线形状由冻结线性估计量决定，不提供阈值、平台或其他非线性信息。

![三个核心区域与胁迫组合的旧线性连续曲线](../../../temp/2026-07-15_g185_old_method_unified_override_v1/figures/fig2_core_linear_curves.png)

*图2注：历史grid加year固定效应。带状区间使用全国统一的999次grid Rademacher权重和seed 42，不是三个历史独立区域seed区间。纵轴为分别指数转换后的TE端点，曲线不表示非线性响应面。*

五区完整province×year固定效应结果如下。各区使用本区SR四分位距和胁迫P90，因此表中百分比只适合解释各区内部P75相对P25的条件差异，不应直接用于区域间幅度排序。

| 产区 | 干旱TE，% [95%区间] | 高温TE，% [95%区间] | 热干TE，% [95%区间] |
|---|---:|---:|---:|
| 东北 | 0.842 [-0.691, 2.444] | 0.716 [-0.989, 2.597] | 0.242 [-1.312, 1.883] |
| 黄淮海 | 0.546 [-1.150, 2.283] | 2.200 [0.184, 4.235] | 1.622 [-0.613, 3.719] |
| 西北 | -0.792 [-2.105, 0.484] | 2.309 [-0.911, 5.726] | 2.114 [-1.324, 5.775] |
| 西南 | -0.147 [-0.541, 0.252] | 0.246 [-0.024, 0.530] | 0.309 [-0.152, 0.784] |
| 华南 | -1.767 [-5.588, 2.097] | 4.531 [1.993, 6.721] | 4.148 [-0.838, 8.974] |

15项Romano–Wolf校正后，黄淮海高温的调整p值为0.195，华南高温为0.0005；但华南只有13个空间块，该结果不能单独承担主结论。区域同质性检验显示，province×year加Rademacher规格中的高温Wald p值为0.0125，三胁迫Holm校正后为0.0375；Webb对应原始p值0.0170、Holm p值0.0510。干旱和热干的区域同质性检验均未提供相同强度的证据。因此，较可靠的异质性表述是“高温关联存在产区差异迹象，但强度对空间权重分布和低块数产区敏感”。

图3完整展示历史规格下五区三胁迫的IE、DE和TE，未删除负向或区间跨零的组合。各柱是相应对数斜率组件单独指数转换后的端点，不能在百分比尺度作严格加法。图中区间使用统一grid权重，避免为各产区分别选择更有利的随机序列。

![五区IE、DE与TE完整对照](../../../temp/2026-07-15_g185_old_method_unified_override_v1/figures/fig3_five_zone_iede.png)

*图3注：历史grid加year固定效应；误差棒使用全国统一的999次grid Rademacher权重和seed 42。各百分比柱分别转换，非严格可加。黄淮海在后续2°空间块核验中只有25块，华南只有13块；华南空间块结果仅作低块数描述。*

## 六、空间推断与核心稳定性

| 组合 | year FE/grid wild | province×year/2° Rademacher | province×year/2° Webb | HAC 100 km | HAC 200 km | HAC 300 km |
|---|---:|---:|---:|---:|---:|---:|
| 东北干旱 | 1.850 [1.187, 2.502] | 0.842 [-0.691, 2.444] | 0.842 [-0.666, 2.445] | 0.842 [-0.663, 2.369] | 0.842 [-0.645, 2.351] | 0.842 [-0.489, 2.190] |
| 黄淮海高温 | 3.168 [2.029, 4.220] | 2.200 [0.184, 4.235] | 2.200 [0.201, 4.235] | 2.200 [-0.086, 4.538] | 2.200 [-0.022, 4.471] | 2.200 [-0.197, 4.654] |
| 黄淮海热干 | 2.425 [1.149, 3.711] | 1.622 [-0.613, 3.719] | 1.622 [-0.546, 3.731] | 1.622 [-0.972, 4.283] | 1.622 [-0.828, 4.132] | 1.622 [-0.939, 4.248] |

加入province×year固定效应后，三个历史核心点估计都保持正号，但均有所缩小。东北干旱的2°Rademacher端点在1,999次扰动中有1,683次与正向点估计同号，即84.1921%；黄淮海高温和热干分别为98.6493%和91.7459%。本轮override仅取消原90%规则的执行阻断效力，不改变这些比例，也不把84.19%重新描述为方法学通过。东北干旱在三种HAC带宽和两种空间块权重下区间均跨零，因此它只能作为方向一致、精度不足的结果。

### 完整15项主要多重检验

下表完整报告province×year固定效应加2°Rademacher层的15项单位SR—胁迫对数斜率`θ_rk`检验。`p_raw`为同步bootstrap双侧原始p值，`p_RW`为15项family Romano–Wolf stepdown值，`p_Holm`为同一批原始p值的Holm复核；它们检验单位斜率，而不是各区不同IQR和P90形成的百分比端点。

| 产区 | 胁迫 | p_raw | p_RW | p_Holm |
|---|---|---:|---:|---:|
| NE | 干旱 | 0.3310 | 0.9065 | 1.0000 |
| NE | 高温 | 0.4710 | 0.9065 | 1.0000 |
| NE | 热干 | 0.7765 | 0.9065 | 1.0000 |
| HHH | 干旱 | 0.5915 | 0.9065 | 1.0000 |
| HHH | 高温 | 0.0255 | 0.1950 | 0.3570 |
| HHH | 热干 | 0.1525 | 0.7855 | 1.0000 |
| NW | 干旱 | 0.2385 | 0.9065 | 1.0000 |
| NW | 高温 | 0.1945 | 0.8460 | 1.0000 |
| NW | 热干 | 0.2545 | 0.9065 | 1.0000 |
| SW | 干旱 | 0.5220 | 0.9065 | 1.0000 |
| SW | 高温 | 0.0940 | 0.6780 | 1.0000 |
| SW | 热干 | 0.2885 | 0.9065 | 1.0000 |
| SH | 干旱 | 0.4055 | 0.9065 | 1.0000 |
| SH | 高温 | 0.0005 | 0.0005 | 0.0075 |
| SH | 热干 | 0.1200 | 0.7555 | 1.0000 |

历史grid wild、province×year Rademacher和Webb三个推断层的全部45行`p_raw/p_RW/p_Holm`均保留在[补充机器表table5_complete_region_joint_tests.csv](../../../temp/2026-07-15_g185_old_method_unified_override_v1/tables/table5_complete_region_joint_tests.csv)，未按显著性删行。

## 七、稳健性、局限与可复现性

历史全国端点相对冻结值的最大误差为`2.69e-7`个百分点，三个历史核心TE的最大复现误差为`9.44e-12`。`3.47e-18`是`Δ_TE,k^log=Δ_IE,k^log+Δ_DE,k^log`在对数斜率/线性预测尺度上的最大绝对恒等式误差，不是三个百分比端点的加法误差；百分比端点因分别指数转换而非严格可加。曲线P90端点误差为0。三个15维同步bootstrap层的协方差秩均为15，九项区域omnibus秩均为4；108项Conley诊断全部为有限值。派生override包再次逐字节核验原机器包登记的20个输出，20/20通过，并生成6张机器表和3幅白底、无衬线、3600×1500像素、300 DPI图。

本文仍有五项限制。第一，G185来自既有尺度筛选，存在选择历史，不能表述为唯一最优尺度。第二，面板只有四年，固定效应增强后有效时间变异和精度明显下降。第三，SM与胁迫同期，IE/DE/TE不能识别因果中介。第四，SR采用强度可能与未观测的管理能力、投入或地方趋势共同变化。第五，黄淮海和华南空间块较少，特别是华南结果对有限块推断敏感。以上限制意味着本文当前更适合作为条件关联和机制一致性小稿，而不是因果效应稿。

模型重估入口与派生导出入口分开。[`run_g185_old_method_full.py`](../../../scripts/python/run_g185_old_method_full.py)调用[`g185_old_method_core.py`](../../../scripts/python/g185_old_method_core.py)，从冻结GGCP10基础面板和V3 hot-dry sidecar重新应用G185谓词、估计两条方程并生成完整机器表；它要求显式提供`--project-root`、`--worktree-root`、`--base-dta`、`--hotdry-dta`和新的`--output-dir`，并固定同时运行`grid_year/grid_provyear`、`grid/spatial_block`、2°块、999/1,999次和seed 42。该入口还要求运行环境中存在冻结的`full_v1/FULL_STOP.json`数值参照，且输出目录必须不存在，不能覆盖历史run。数值核心、样本序列化、固定效应吸收、wild bootstrap、Romano–Wolf及Conley计算均在`g185_old_method_core.py`中实现。

[`export_g185_old_method_override.py`](../../../scripts/python/export_g185_old_method_override.py)不是模型重估入口。它锁定已审查来源`full_manifest.json`哈希`3a23e22b421f052a4afc5f83c6aa806dd5a8f081bdb83aded357b2af6ca8aaec`，逐字节验证20个登记输出后，只生成override专属六表三图。完整派生机器表位于[`temp/2026-07-15_g185_old_method_unified_override_v1/tables/`](../../../temp/2026-07-15_g185_old_method_unified_override_v1/tables/)，图位于同一run的[`figures/`](../../../temp/2026-07-15_g185_old_method_unified_override_v1/figures/)，导出身份及12项派生输出哈希记录在[`override_manifest.json`](../../../temp/2026-07-15_g185_old_method_unified_override_v1/override_manifest.json)。原`g185-old-method-unified-v1`的`FULL_STOP`状态没有被删除或覆盖。

## 八、结论与投稿匹配

在G185冻结样本和历史线性估计量下，较高观测秸秆还田采用强度与全国干旱、高温和热干损害斜率较平缓相关。该关联在更强province×year固定效应和空间推断后明显减弱，产区结果主要体现为高温异质性，东北干旱则表现为正向点估计但空间稳定性不足。分别指数转换的同期土壤水分IE端点幅度小于对应DE端点，但三类百分比端点不能作份额分解，也不能支撑“土壤水分已被识别为主要中介”的结论。

本稿暂定匹配[Scientific Reports的自然科学与环境科学范围](https://www.nature.com/srep/about/aims)。其可投稿价值主要来自全国、连续曲线与五区结果的统一组织，以及固定效应和空间推断增强后对边界的完整披露；方法本身属于既有线性两方程估计量的统一复核，创新度有限。后续标题、摘要和投稿材料不得使用“causal effect”“identified mediation”或“robust buffering”等措辞。

## 九、数据、代码与研究声明

**数据可得性。** 本稿使用项目内部冻结的GGCP10-G185派生面板。上游数据的公开共享范围受各来源许可约束；当前可复核的样本谓词、输入身份、行列支持和输出哈希记录在项目数据盘点、来源`full_manifest.json`和本run的`override_manifest.json`中。投稿前需按上游数据许可补齐正式数据可得性文本。

**代码可得性。** 模型重估入口、数值核心和派生导出入口已在第七节给出；公共仓库发布范围需在投稿前确认。机器数据、中间面板、模型对象、日志和二进制图表不纳入Git历史。

**伦理声明。** 本研究使用网格化二手农业与环境数据，不涉及人类受试者、个人可识别信息或动物实验。

**作者贡献（CRediT）。** 具体作者名单及Conceptualization、Methodology、Software、Validation、Formal analysis、Data curation、Writing和Visualization分工待作者团队确认，本稿不代填。

**利益冲突。** 待全体作者确认后填写；当前分析材料未提供可据实声明的作者级信息。

**经费声明。** 待作者团队依据真实资助信息填写，本稿不推定经费来源。

**AI工具使用声明。** 本稿使用Codex辅助代码执行、数值核验、文稿整理和审校；研究设计、结果解释、作者责任及投稿决定由作者承担。投稿时应按目标期刊届时有效的政策调整表述。

## 参考文献

Imai, K., Keele, L., & Tingley, D. (2010). A general approach to causal mediation analysis. *Psychological Methods, 15*(4), 309–334. https://doi.org/10.1037/a0020761

Lesk, C., Coffel, E., Winter, J., Ray, D., Zscheischler, J., Seneviratne, S. I., & Horton, R. (2021). Stronger temperature–moisture couplings exacerbate the impact of climate warming on global crop yields. *Nature Food, 2*, 683–691. https://doi.org/10.1038/s43016-021-00341-6

Liu, L., Gudmundsson, L., Hauser, M., Qin, D., Li, S., & Seneviratne, S. I. (2020). Soil moisture dominates dryness stress on ecosystem production globally. *Nature Communications, 11*, 4892. https://doi.org/10.1038/s41467-020-18631-1

Proctor, J., Rigden, A., Chan, D., & Huybers, P. (2022). More accurate specification of water supply shows its importance for global crop production. *Nature Food, 3*, 753–763. https://doi.org/10.1038/s43016-022-00592-x

Vansteelandt, S., & Daniel, R. M. (2017). Interventional effects for mediation analysis with multiple mediators. *Epidemiology, 28*(2), 258–265. https://doi.org/10.1097/EDE.0000000000000596
