# 地区异质温度阈值继续执行：全量计算报告

## Material Passport

- Canonical ID：`regional-threshold-sr-override-v1`
- Parent evidence：`regional-threshold-sr-v1`，历史STOP报告未修改
- Run ID：`2026-07-15_regional_threshold_daily_override_full_v1`
- 工作流：Academic Research Suite / experiment-agent，`run` + `validate`
- Verification Status：`COMPUTATION VERIFIED`；尚未完成2°空间块wild bootstrap、空间HAC、Stata复算和独立结果审稿，不能标记为publication-ready
- 运行状态：`COMPLETED_DAILY_APPROXIMATION`

## 一、执行范围

用户明确取消原“五区外生阈值覆盖率均须达到80%”规则的阻断效力。本轮据此在原始外生阈值有效的complete-case上继续，但没有插值、外推、固定32°C回填或修改产区。原西南覆盖率69.8408%继续完整披露。新结果只属于`regional-threshold-sr-override-v1`，不得回写为原`regional-threshold-sr-v1`已经通过。

温度暴露使用逐日Tmax，不能称为Figshare `CalExposure.m`逐小时算法的精确移植。主暴露为逐日Tmax超过连续地区阈值的温度超额积分`threshold_hdd_cday_daily`；同时生成逐日超阈值天数，固定32°C使用完全相同的日尺度算法作预设对照。没有运行28—40°C阈值搜索，也没有依据显著性改变窗口或样本。

## 二、输入身份和只读核验

| 输入角色 | 逻辑定位 | Bytes | SHA-256 |
|---|---|---:|---|
| V3主面板 | `local://data_build/data/processed/data_v3_main.parquet` | 350,946,854 | `1aed2f71427d379bf1a71fdce58904d806061842d644dc45d65638e763bab948` |
| 外生阈值 | `external://zenodo/17142122/maize.tif` | 328,745 | `f05e634664c4c6c2e2df352702acd421507162bc54cc067649071521ab1285b0` |
| 物候—CA | `source://phenology-ca-0p1deg` | 2,199,909 | `130e1aec6e72f89f249c89c7eb2236a885d3ebd2b04db546d1b684b52c3783a7` |
| Tmax 2016 | `source://daily-temp-cn/2016` | 204,661,068 | `e29772bbdda3a3f1da2a35887d822bf814abcb062d4aa3179d04589bff9f2340` |
| Tmax 2017 | `source://daily-temp-cn/2017` | 201,442,593 | `9008d5841d490cb968c58e85ea56de7080136b4de494a2186910fe676c5b76b5` |
| Tmax 2018 | `source://daily-temp-cn/2018` | 203,603,563 | `b706e612978c6c1143d6def329793d46e5a56adee4abd7be8f1b8228f79f9e6b` |
| Tmax 2019 | `source://daily-temp-cn/2019` | 202,124,071 | `5ac13661fd244ed03a8b20f895d8cf5d094d994cc81717bdbe7022f956d943b7` |
| GLEAM 2016 | `source://gleam-aligned/2016` | 421,212,024 | `bfe0c40a56531c70ca514f7f1e32cf0b6b6517b614e7ec9bf664e3b21d9a511b` |
| GLEAM 2017 | `source://gleam-aligned/2017` | 426,789,100 | `81644bf01e75fe3c8e8ca9c71f2044a663362c72f2d445c97f4b67bac3dbe3e2` |
| GLEAM 2018 | `source://gleam-aligned/2018` | 411,146,203 | `e2601779e6e455a3e85c9baa6d46d38f12c0eec25d52b1ade984fd511be2884c` |
| GLEAM 2019 | `source://gleam-aligned/2019` | 407,615,508 | `8b76a4088ebcefb4aa382f9e2ad4b1c28886322a3c7ff67dfa7dc288f8b66a86` |

V3重新读取为69,038行、22,180个grids，`grid_id year`无重复，grid内province不变化。V3的V3、HE、MA三个DOY字段与物候NetCDF逐行比对均为0个不一致。四年Tmax和GLEAM日期轴分别与对应公历年的逐日序列完全一致；二者格网坐标一致。V3索引与NetCDF坐标的最大绝对误差为纬度`1.831055×10^-6`度、经度`7.324216×10^-6`度。

## 三、样本支持

| 产区 | 阈值前行数 | 有效外生阈值行 | 原始覆盖率 | 有效阈值grids | 完整逐日Tmax行 | 完整逐日Tmaxgrids |
|---|---:|---:|---:|---:|---:|---:|
| NE | 25,041 | 23,723 | 94.7366% | 6,967 | 23,719 | 6,966 |
| HHH | 13,165 | 12,922 | 98.1542% | 3,775 | 12,922 | 3,775 |
| NW | 5,540 | 4,681 | 84.4946% | 1,849 | 4,681 | 1,849 |
| SH | 4,556 | 4,501 | 98.7928% | 1,668 | 4,501 | 1,668 |
| SW | 18,094 | 12,637 | 69.8408% | 4,487 | 9,067 | 3,192 |

外生阈值有效的58,464行中，最终产量模型为54,890行和17,450个grids。新增缺口不是窗口日期错误：四川省3,570个grid-years以及辽宁省4个grid-years的逐日Tmax在对应格点全年均为masked，三个窗口因此机械地使用同一complete-case；这些四川行的V3 `gdd_10_29`为0。GLEAM前置14日和窗口内SMrz在58,464个阈值有效grid-years中全部完整。该Tmax空间缺口必须在后续稿件中与外生阈值缺口分别披露，不能用V3聚合字段回填逐日源数据。

## 四、模型和估计对象

三个固定窗口为扩展V3—成熟`[V3-30, MA]`、V3—HE`[V3, HE)`和HE—MA`[HE, MA]`。后两个阶段不重叠。五区合并模型为grid FE与重新生成的province×year FE，控制`gdd_10_29`、季节降水和降水平方；每区分别保留CA、HDD和CA×HDD低阶项。共同CA端点为P25=`0.030048`、P50=`0.235915`、P75=`0.510907`，暴露端点为各区各窗口P50/P90。

报告量是高SR与低SR在HDD从各区P50升至P90时的条件`ln_yield`变化差：

\[
\hat\beta_{CA\times HDD,z}(CA_{75}-CA_{25})(HDD_{90,z}-HDD_{50,z}).
\]

只有在HDD对应的低SR条件产量变化为负时，正差值才具有“损害缓冲”的直接含义；若低SR和高SR下的HDD—产量条件变化都为正，正交互只能称为更正的条件斜率差，不能包装成热损害缓冲。

## 五、产量结果

### 5.1 外生连续阈值，扩展V3—成熟窗口

| 产区 | HDD P50→P90 | 低SR条件变化 | 高SR条件变化 | 高SR−低SR | 换算百分比及95%CI | grid-cluster p |
|---|---:|---:|---:|---:|---:|---:|
| NE | 2.237→45.914 | 0.0580 | 0.0177 | -0.0403 | -3.95% [-6.43, -1.41] | 0.0025 |
| HHH | 16.096→291.351 | 0.5822 | 0.7114 | 0.1292 | 13.79% [9.72, 18.02] | <0.0001 |
| NW | 6.664→179.718 | 0.0550 | 0.1271 | 0.0720 | 7.47% [2.52, 12.65] | 0.0027 |
| SH | 0→37.997 | -0.1115 | -0.0897 | 0.0218 | 2.20% [-1.65, 6.21] | 0.2669 |
| SW | 0→23.772 | 0.0317 | 0.0303 | -0.0015 | -0.15% [-3.68, 3.52] | 0.9368 |

NE、HHH、NW和SW的低SR条件变化并不是负向热损害；因此，虽然HHH和NW的交互为正且区间不跨0，当前主规格不能把它们直接表述为“SR缓冲了温度损害”。SH的低SR和高SR条件变化均为负且差值为正，但其区间跨0。五区没有形成同一种可投稿的损害缓冲结构。

### 5.2 物候窗口和固定32°C

外生阈值在V3—HE窗口的差值依次为NE -3.80%、HHH 18.83%、NW 7.88%、SH 0.32%、SW -0.39%；HE—MA依次为NE -2.96%、HHH 9.85%、NW 1.87%、SH 2.73%、SW 1.92%。方向保持明显地区差异，HHH正向差值集中在V3—HE，NE三个窗口均为负。

固定32°C扩展窗口依次为NE -3.91%、HHH 18.50%、NW 3.29%、SH 1.25%、SW 1.04%。其中仅NE和HHH的grid-cluster区间不跨0；HHH低SR和高SR的条件变化同样均为正，仍不能直接称为损害缓冲。固定32°C没有把五区结果统一到相同方向或相同损害前提。

LOYO四折相对全样本主交互的同向折数为NE 3/4、HHH 4/4、NW 4/4、SH 3/4、SW 2/4。SW不满足原计划中的3/4方向稳定性；本轮用户授权使其不阻断计算，但不改变稳定性诊断。

## 六、SM状态和通道

GLEAM前置状态模型显示：NE在antecedent SMrz P25时差值为-13.29% [-16.76, -9.67]，P75时为9.92% [5.70, 14.32]，出现系统性反向；HHH为13.38%和16.28%，NW为-0.34%和9.20%，SH为1.14%和4.61%，SW为0.09%和1.75%。这些结果表明条件斜率差依赖初始土壤水状态，但仍受上节“基础HDD—产量变化未必为损害”的解释限制。

以`窗口SMrz均值−前置SMrz`为结果时，CA×HDD条件差在NE、NW为负，HHH、SH为正，SW区间跨0；以`窗口最低SMrz−前置SMrz`为结果时，HHH、SH为正，NW为负，NE和SW区间跨0。土壤水通道没有形成五区共同方向，只能称为地区异质的通道一致条件相关结构，不能称为因果中介证据。

## 七、计算验证

执行代码身份为：runner SHA-256 `c9d7516b7598d228e42eccacfc5d7eefe0e143185850a642d4b67dcee85450f6`，core SHA-256 `5ee06ab5a79c407ccdb5e223ac1fb708e889a6d00275a76ef1eff1c56540bd33`。`python -m py_compile`通过；`python -m unittest tests.test_regional_threshold_daily_core -v`为10/10通过。20 grids/zone的smoke完成376个grid-years、100个grids，六个产量模型、四折LOYO、SM状态和两个SM通道模型均满秩。

全量六个产量模型均为18/18满秩，condition number为296.9—474.4；SM状态模型为38/38满秩，condition number为7,624.5；两个SM通道模型为18/18满秩。双固定效应去除均在62轮收敛，最后最大变化`9.1493×10^-11`。全量stderr为空。

机器命令结构如下；机器展开后的实际路径、文件字节数和完整哈希保存在本run的`run_manifest.json`中：

```powershell
python scripts/python/run_regional_threshold_daily_override.py `
  --panel $V3_MAIN_PARQUET `
  --raster $MAIZE_THRESHOLD_TIF `
  --temperature-dir $DAILY_TEMP_DIR `
  --smrz-dir $GLEAM_ALIGNED_DIR `
  --phenology $PHENOLOGY_CA_NC `
  --output-dir temp/2026-07-15_regional_threshold_daily_override_full_v1
```

## 八、输出与未完成项

本run保存在`local://temp/2026-07-15_regional_threshold_daily_override_full_v1/`，包括`daily_exposure_panel.parquet`、两张支持/分母表、暴露分位数表、完整30行产量结果、20行LOYO结果、10行SM状态结果、10行SM通道结果、三幅300 DPI图和`run_manifest.json`。这些数据与二进制图均不进入Git。

本阶段完成了全量暴露与grid-cluster模型，但没有执行2°空间块wild bootstrap 1,999次、100/200/300 km空间HAC、Romano–Wolf、多软件点估计复算或逐小时ERA5暴露。尤其是主规格中多数地区的HDD—产量条件变化不是负向损害，且四川逐日Tmax存在结构性空间缺失；在这些问题完成独立结果审查前，本方向只能作为完整的可计算探索结果，不能形成“外生地区阈值证明SR缓冲热害”的投稿结论。
