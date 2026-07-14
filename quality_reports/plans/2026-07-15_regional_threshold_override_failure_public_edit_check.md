# `regional-threshold-sr-override-v1`失败公共报告编辑核验

## 核验范围与边界

- 交付文件：`docs/results/regional-threshold-sr-override-v1/report.md`
- 冻结机器run：`temp/2026-07-15_regional_threshold_daily_override_full_v2/`
- 审查真值：`quality_reports/plans/2026-07-15_regional_threshold_override_method_review_round2.md`
- 编辑状态：`REVIEWED_NOT_CANDIDATE`，72/100，0 Critical、3 Major、4 Minor
- 本次操作只编辑Markdown和执行只读验证；没有运行新模型、新规格、新阈值、新窗口、新推断或新图，也没有修改任何`temp/`机器文件、manifest、历史审查、lineage、index或registry。

报告SHA-256为`3738baac2ea8fee851a7986f060f1b3ed51850955342771afc1838a51e3ef68b`，大小23,525 bytes，共254行。

## 已读证据

编辑前完整读取并交叉核对：

1. 项目`AGENTS.md`；
2. 项目本地`academic-research-suite/SKILL.md`；
3. `academic-paper/WORKFLOW.md`、`draft_writer_agent.md`、`academic_writing_style.md`和`writing_quality_check.md`；
4. `2026-07-15_regional_threshold_override_full_v2_report.md`；
5. `2026-07-15_regional_threshold_override_round1_revision_response.md`；
6. `2026-07-15_regional_threshold_override_method_review_round2.md`；
7. full_v2的`run_manifest.json`、`round1_post_validation_manifest.json`及产量、wild bootstrap、HAC、LOYO、SM、样本漏斗、支持、Stata复算和四图机器文件。

核心文献与数据身份经过三层核验：本地Zotero核验记录的item key为`262BTEKM`；Nature Food正式页给出论文题名、作者、卷页和DOI `10.1038/s43016-026-01298-0`；Zenodo正式记录给出数据DOI `10.5281/zenodo.17142122`、0.5°说明、`maize.tif`文件名、328.7 kB和MD5 `0d9e6c21bf1b25f113e14315863372f2`。Nature正式页同时把代码指向Figshare，项目既有全文/代码核验记录固定版本DOI为`10.6084/m9.figshare.27238629.v3`。

## 机器文件身份核验

按`round1_post_validation_manifest.json::run_files_after_stata_replication`逐文件重算bytes和SHA-256，共核验29项，29项通过、0项失败。关键文件与公共报告登记值一致：

| 文件 | 机器SHA-256 | 结果 |
|---|---|---|
| `run_manifest.json` | `5f6ebccaf11748300ff4034a598a0fcfe65f649ce7668bb555a022b060c9b76c` | 一致 |
| `yield_results.csv` | `780cf40fe887076c8afa39f437905e59863f68a48b227cab8a197a5909347de8` | 一致 |
| `wild_bootstrap_primary_results.csv` | `0d6d6c4db519c4f0300efaa5661a986e1cc5dde88c737ce20fe3e05041c667c9` | 一致 |
| `wild_bootstrap_joint_covariance.csv` | `7b107721070c2b2818c219a1fb4b8fa87bc3cfdb8bd2c6a455ad1372823986aa` | 一致 |
| `spatial_hac_primary_results.csv` | `8f0dc0a8326f4ddd1e5578671bed1e8b4aeff04869e72fca8d428dcffa5492f2` | 一致 |
| `sm_state_results.csv` | `a89df043cd6b11412510e8fe804c6550228509c3d39eb9ea2f5c74534068563c` | 一致 |
| `sm_channel_results.csv` | `481408cac16267c209a3b442f60a2b88ab2c7f8261ebf436201e9cadc4d1affc` | 一致 |
| `sample_funnel_zone.csv` | `5f1f90babc0cc8c2a4ca22b90566baaed5cc2af5f561b75cd7d2e30a6fd945c5` | 一致 |
| `ca_hdd_joint_support.csv` | `fe44fa1211f1fcb87db1ed44c46491e2ff28e65b4cc5234e648749bfce61a38f` | 一致 |
| `stata_python_replication_comparison_round1.csv` | `42a61362266cf7c946e56039f67d84662d9dc7735bad994b20687aee7da5eadb` | 一致 |

四图SHA-256与manifest全部一致：图1 `bf50925...d8b5d`，图2 `ae63e3...3110`，图3 `0363c5...63c5`，图4 `89cb99...2844`。四图均经可视检查：图1、图2标题明确标注`preliminary grid-cluster CI`且实际只含低/高SR条件变化；图3为SM通道grid-cluster图；图4为样本选择图。

## 数值与转录核验

### 样本和端点

| 项目 | 机器真值 | 公共报告 | 结果 |
|---|---:|---:|---|
| V3面板 | 69,038行、22,180 grids | 一致 | 通过 |
| 五区阈值前complete-case | 66,396行、21,337 grids | 一致 | 通过 |
| 外生阈值有效 | 58,464行、18,746 grids | 明确标为“外生阈值有效”，未再标为阈值前 | 通过 |
| 最终模型 | 54,890行、17,450 grids | 一致 | 通过 |
| 四川最终支持 | 0行、0 grids | 一致 | 通过 |
| 产量模型CA P25/P75 | 0.03004790325 / 0.510906605 | 报告精确值并简写为0.030048/0.510907 | 通过 |
| 支持表CA P75 | 0.51091456 | 只用于支持诊断，并解释与模型端点约`8e-06`差异 | 通过 |

### 五区完整窗口主结果

公共报告逐行使用`yield_results.csv`的低/高SR点估计，并使用`wild_bootstrap_primary_results.csv`的对比、区间和三类p值。核验结果为：

| 产区 | 低SR | 高SR | 对比 | wild 95% CI | RW p | 转录 |
|---|---:|---:|---:|---:|---:|---|
| NE | 0.05798 | 0.01766 | -0.04031 | [-0.10974, 0.02661] | 0.8140 | 一致 |
| HHH | 0.58216 | 0.71138 | 0.12922 | [0.05825, 0.20100] | 0.0005 | 一致 |
| NW | 0.05504 | 0.12706 | 0.07202 | [0.00291, 0.14327] | 0.2300 | 一致 |
| SH | -0.11152 | -0.08973 | 0.02179 | [-0.03811, 0.08107] | 0.8140 | 一致 |
| SW | 0.03171 | 0.03025 | -0.00146 | [-0.04520, 0.04393] | 0.9510 | 一致 |

公共报告同时逐行登记15个产区×物候窗口的低/高SR变化、对比、wild区间、Romano–Wolf和Holm值；五区LOYO同向折数为3/4、4/4、4/4、2/4、2/4，与机器文件一致。报告没有删除东北、西南的负对比，没有删除华南、西南及多数物候窗口的不精确结果，也没有把西北未校正`p=0.0445`改写为多重检验后通过。

### SM、HAC和Stata

公共报告逐项转录10行SM状态与10行SM通道结果，保留东北/西北状态翻向、西南不精确及各区正负方向。SM区间明确标记为grid-cluster，不声称已有空间联合推断或多重检验。100/200/300 km HAC共15行以五区三带宽表完整呈现。

Stata/Python复算登记18个系数最大绝对差`9.02×10^-16`、18个grid-cluster SE最大绝对差`4.93×10^-5`、Stata删除2,287个singleton后`N=52,603`、Python输入`N=54,890`，均与运行后验证文件一致。

对报告执行48项关键文字/数值token检查，覆盖状态、评分、三个样本总量、实际CA端点、15个物候对比、20个SM点估计、Stata容差、preliminary图形标签、经验分位数区间说明和阈值SHA-256；48项通过、0项缺失。

## Round 2四项Minor的编辑更正

1. 把58,464明确改为“外生阈值有效行数”，并报告正确的阈值前五区complete-case 66,396。
2. 主estimand使用`yield_results.csv`实际CA P75 0.510906605（简写0.510907）；0.510915只作为窗口展开支持表值披露。
3. 测试说明限定为18项实际覆盖范围，明确不覆盖HAC数值、空间块score聚合和图形—primary estimand一致性。
4. 方法部分明确95% wild-bootstrap区间为“点估计加中心化draws的经验2.5%/97.5%分位数”，并说明有限1,999次下可轻微非对称。

这些都是Markdown编辑更正，没有修改机器结果或重算推断。

## 语义、路径与声明核验

- 报告明确用户取消的是旧覆盖停止门槛的阻断作用，不是取消解释边界；失败依据是冻结estimand不支持缓冲主张及预设链条/主图不完整。
- 报告没有把黄淮海正对比称为缓冲，没有把SM称为因果中介，没有把daily-Tmax degree-day称为`CalExposure.m`复现或近似。
- 图1、图2明确为初步grid-cluster诊断；primary contrast/wild-bootstrap图缺失作为Major保留。
- 报告包含全部3 Major和4 Minor，不提出Round 3或任何规格搜索。
- 公共Markdown未出现本机盘符绝对路径；`maize.tif`只以`external://regional-threshold-maize-raster`公共定位符表述。
- 数据、代码、伦理、CRediT、利益冲突、经费和AI声明均已加入。未知作者、基金、冲突和公共仓库信息保持显式占位，没有虚构姓名、项目号、无冲突或无资助结论。

## 单元测试

对`test_regional_threshold_daily_core`、`test_regional_threshold_inference`和`test_regional_threshold_runner_contract`三个既有模块执行Python `unittest`。结果为18/18通过，运行0.071秒。该验证只运行已有人工与契约测试，没有加载全量模型、生成新估计或改变机器run。

## 最终判定

`PASS_FAILURE_PUBLIC_EDIT`。该判定只表示失败公共报告与冻结机器证据、Round 2审稿意见和公开路径边界一致，不改变研究方向的`REVIEWED_NOT_CANDIDATE`状态，也不表示稿件达到投稿候选或publication-ready门槛。
