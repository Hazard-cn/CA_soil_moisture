# 秸秆还田对联合极端气候胁迫下玉米产量的调节作用 — 分析说明书

> **版本**: v6.1 (2026-03-23)
> **定位**: 论文 methods section 底稿 + 代码-论文对照手册
> **语言**: 中文叙述，英文变量名，LaTeX 公式

---

## 0. 数据与面板结构

### 0.1 数据来源

| 数据类型 | 来源 | 分辨率 | 时间范围 |
|----------|------|--------|----------|
| 玉米产量 | 县级统计年鉴 → 面积加权分配至 grid | 0.1° (~10 km) | 2016–2019 |
| 秸秆还田 (SR) | 遥感分类 (Sentinel-2 / Landsat) | 0.1° | 2016–2019 |
| 气候极端 | ERA5 再分析 (Tmax, 降水) + SPEI | 0.1° | 2016–2019 |
| 土壤水分 (SM) | GLEAM v3.8a (根区 smrz / 表面 sms) | 0.25° → 0.1° | 2016–2019 |
| 土壤属性 | SoilGrids (clay, sand, bdod, pH, silt) | 0.1° | 静态 (0–5cm) |
| 灌溉 | 灌溉面积比例 | 0.1° | 年度 |

### 0.2 面板结构

- **单位**: 0.1° × 0.1° 网格 (grid)
- **面板设定**: `xtset grid_id year`
- **原始样本**: 69,038 grid-years
- **有效样本**: ~61,795 (扣除 singleton grids + 缺失值，由 `reghdfe` 自动处理)
- **数据文件**: `data/processed/data_v1_with_climate.csv` (69,038 行, 143 列, GBK 编码)

### 0.3 核心变量定义

| 符号 | 变量名 | 定义 | 单位/取值 |
|------|--------|------|-----------|
| $Y$ | `ln_yield` | 玉米单产的自然对数 | $\ln(\text{tons/ha})$ |
| $D$ | `D_season` | 干旱暴露 = $\max(0, -\text{SPEI\_season})$ | 标准差单位 |
| $W$ | `W_season` | 湿润暴露 = $\max(0, \text{SPEI\_season})$ | 标准差单位 |
| $H$ | `hdd_tmax_ge32` | 热量暴露 = $\sum_d \max(T_{max,d} - 32, 0)$ (生育期累积) | °C·days |
| $SR$ | `ca` | 秸秆还田采纳率 (当年) | 0–1 连续 |
| $SR_{lag}$ | `crc_lag1` | 秸秆还田采纳率 (滞后一年) | 0–1 连续 |
| $SM^{sfc}$ | `gleam_sms_mean` | 表层土壤水分 (生育期均值, GLEAM) | m³/m³ |
| $SM^{rz}$ | `gleam_smrz_mean` | 根区土壤水分 (生育期均值, GLEAM) | m³/m³ |
| $DryDays$ | `drydays_gleam_sms_le_basep10` | 干旱天数: 表面 SM ≤ 基准期 P10 的天数 | days |
| $HotDryDays$ | `hotdrydays_tmax_ge32_and_smrz_le_basep20` | 复合胁迫天数: Tmax≥32 且 SM_rz ≤ P20 | days |

**控制变量** ($\mathbf{X}$):

| 宏名 | 包含变量 | 说明 |
|------|---------|------|
| `$CTRL` | `irr_frac`, `pre_sum`, `et0_sum`, `wd_aridity_et0divpre`, `gdd_30` | 基础气候+灌溉控制 |
| `$SOIL_CTRL` | `clay_0_5cm_01deg`, `sand_0_5cm_01deg`, `bdod_0_5cm_01deg`, `phh2o_0_5cm_01deg`, `silt_0_5cm_01deg` | 土壤属性控制 |

**交互项构造** (Stata 中预生成):
- `SR_x_D` = `ca` × `D_season`
- `SR_x_W` = `ca` × `W_season`
- `SR_x_Heat` = `ca` × `hdd_tmax_ge32`
- `D_x_Heat` = `D_season` × `hdd_tmax_ge32`
- `SR_x_D_x_Heat` = `ca` × `D_season` × `hdd_tmax_ge32`

**固定效应 (FE) 结构**:

| 简称 | Stata 语法 | 识别变异 |
|------|-----------|---------|
| Grid+Year | `absorb(grid_id year)` | Grid 内时间变化 (within-grid, T=4) |
| County+Year | `absorb(county_id year)` | 县内跨 grid 空间差异 |
| Prov×Year | `absorb(grid_id prov_year)` | 吸收省级年际冲击后的 grid 内变化 |

**默认推断**: `vce(cluster grid_id)` (grid 级聚类标准误)

---

## 1. 分析框架总览

### 1.1 论文主轴

> **SR 改变了作物在干旱(D)×高温(H)联合暴露下的产量损失斜率**，土壤水分(SM)是方向一致的状态变量通道——state-shift 证据强，loss-function closure 证据弱。

### 1.2 三类证据

| 证据类型 | 问题 | 方法 | 对应步骤 |
|----------|------|------|----------|
| **Type I: Stress-Surface** | D×H 超加性损失是否存在？SM 状态是否影响胁迫斜率？ | 联合胁迫回归 + SM 分位数分层 | Step 8, Step 8a |
| **Type II: Modifier** | SR 能否调节 D×H 联合胁迫下的产量损失？ | 三重交互 SR×D×H + 边界诊断 | Step_compound, Step 8a, Step 8b |
| **Type III: Pathway** | SR→SM 改善 + SM→减缓产量损失 方向是否一致？ | 三链机制检验 + 正式中介 | Step 4v2, Step 4 formal |

### 1.3 步骤-证据对应表

| 步骤 | 脚本 | 论文角色 | 证据类型 |
|------|------|---------|---------|
| Step 1: Baseline FE | `step1_baseline_FE.do` | 基础总效应 | 前导 |
| Step 2: Placebo & Lead | `step2_placebo.do` | 识别检验 | 前导 |
| Step 8: Joint Stress SM | `step8_joint_stress.do` | SM state-dependence | Type I |
| Step_compound | `step_compound_interaction.do` | SR×D×H 三重交互 | Type II |
| Step 8a: Boundary | `step8a_boundary.do` | FE 梯度、lead、年份诊断 | Type II 边界 |
| Step 8b: Spec Curve | `step8b_spec_curve.do` | 72 规格透明性 | Type II 边界 |
| Step 4v2: 三链机制 | `step4_mechanism_v2.do` | SM 状态变量一致性 | Type III |
| Step 4 Formal | `step4_mediation_formal.do` | 正式中介分解 | Type III |
| Step 5: Heterogeneity | `step5_heterogeneity.do` | 区域/灌溉/SM 异质性 | 补充 |
| Step 7: Sensitivity | `step7_sensitivity.do` | 热量阈值/FE/聚类/滞后 SR | 稳健性 |
| Step 7B: Extra Robustness | `step7b_robustness_extra.do` | LOPO/winsor/Oster/nonlinear | 稳健性 |
| Step 6: DML | `step6_dml.py` | 机器学习交叉验证 | 稳健性 |

---

## 2. [Step 1] Baseline FE — SR 缓冲效应

### 研究问题
秸秆还田(SR)是否缓冲干旱(D)和高温(H)导致的玉米产量损失？

### 计量方程

**Eq. (1) — 基础固定效应模型**:

$$\ln Y_{it} = \alpha_1 D_{it} + \alpha_2 W_{it} + \alpha_3 H_{it} + \beta_0 SR_{it} + \theta_1(SR \times D)_{it} + \theta_2(SR \times W)_{it} + \theta_3(SR \times H)_{it} + \Gamma \mathbf{X}_{it} + \mu_i + \tau_t + \varepsilon_{it}$$

其中:
- $\mu_i$: grid 固定效应; $\tau_t$: 年份固定效应
- $\theta_1 > 0$: SR 缓冲干旱损失（核心假设）
- $\theta_2 \leq 0$: SR 在湿润条件下无缓冲（边界条件）
- $\theta_3 > 0$: SR 缓冲热量损失

### 实施细节

| 项目 | 设定 |
|------|------|
| 因变量 | `ln_yield` |
| FE | `absorb(grid_id year)` |
| 聚类 | `vce(cluster grid_id)` |
| 渐进模型 | (1) 仅极端 → (2) +SR → (3) +SR×D → (4) +SR×W → (5) Full |
| 有效 N | ~61,795 |

### 关键结果

| 系数 | 估计值 | 预期方向 | 通过？ |
|------|--------|---------|--------|
| $\theta_1$ (SR×D) | 0.042** | > 0 | ✓ |
| $\theta_2$ (SR×W) | 0.004 n.s. | ≤ 0 | ✓ (边界) |
| $\theta_3$ (SR×Heat) | 0.0011*** | > 0 | ✓ |

### 对应脚本与输出
- **脚本**: `scripts/stata/step1_baseline_FE.do`
- **输出**: `output/tables/step1_baseline_FE.csv`, `.tex`
- **附加**: `step1_heat_sensitivity.csv` (HDD ≥ 30/32/35), `step1_FE_robustness.csv` (prov×year FE 对比)

---

## 3. [Step 2] Placebo & Lead Test — 识别检验

### 研究问题
SR×极端气候交互效应是否为当期因果关联，而非虚假相关？

### 计量方程

**Eq. (1b) — Lead Test (未来 SR 替代当期 SR)**:

$$\ln Y_{it} = \cdots + \theta_1^{lead}(SR_{i,t+1} \times D_{it}) + \theta_3^{lead}(SR_{i,t+1} \times H_{it}) + \cdots + \mu_i + \tau_t + \varepsilon_{it}$$

- 若 $\theta_1^{lead} \approx 0$ 且 $\theta_3^{lead} \approx 0$: 通过 placebo（未来 SR 不应缓冲当期胁迫）
- 若 $\theta_1^{lead}$ 显著: SR 可能有持续性效应或存在遗漏变量

**Eq. (1c) — Placebo 热量窗口**:

$$\ln Y_{it} = \cdots + \theta_3^{placebo}(SR_{it} \times H_{it}^{pre}) + \cdots$$

其中 $H^{pre}$ 为生育前期热量 (`lag30_hdd_32`)，不应被 SR 缓冲。

### 关键结果

| 检验 | 系数 | 值 | 通过？ |
|------|------|-----|--------|
| SR(t+1)×Heat | $\theta_3^{lead}$ | -0.0001 n.s. | ✓ |
| SR(t+1)×D | $\theta_1^{lead}$ | 0.107*** | ✗ (SR 持续性) |
| SR×Placebo Heat | $\theta_3^{placebo}$ | 0.193 n.s. | ✓ |

> **注意**: SR(t+1)×D 的 lead test 失败（$\rho$(ca, ca\_f1) = 0.437），表明干旱缓冲可能部分来自 SR 的累积效应，而非仅当年效应。此问题在后续 compound 框架中通过三重交互 lead test 重新检验。

### 对应脚本与输出
- **脚本**: `scripts/stata/step2_placebo.do`
- **输出**: `output/tables/step2_placebo_lead.csv`, `.tex`

---

## 4. [Step 8 系列] 联合胁迫响应面 — 论文核心

### 4.1 [Step_compound] D×H 超加性 + SR×D×H 三重交互 (Type I + II)

#### 研究问题
(1) 干旱与高温同时发生时，产量损失是否超过各自独立效应之和（超加性）？
(2) SR 能否系统性地缓解这种联合损失？

#### 计量方程

**Eq. (2) — 联合胁迫响应面模型**:

$$\ln Y_{it} = \alpha_1 D_{it} + \alpha_2 H_{it} + \beta_0 SR_{it} + \theta_1(SR \times D)_{it} + \theta_3(SR \times H)_{it} + \delta_1(D \times H)_{it} + \delta_2(SR \times D \times H)_{it} + \Gamma \mathbf{X}_{it} + \mu_i + \tau_t + \varepsilon_{it}$$

其中:
- $\delta_1 < 0$: D×H 超加性损失（Type I 核心）
- $\delta_2 > 0$: SR 缓冲联合胁迫（Type II 核心）

#### 渐进模型

| 模型 | RHS 新增 | 目的 |
|------|---------|------|
| (1) | Eq.(1) baseline | 参照 |
| (2) | + $D \times H$ | 检验超加性 |
| (3) | + $SR \times D \times H$ | 检验 SR 调节 |
| (4) | 模型(3) 换 Prov×Year FE | 吸收省级趋势稳健性 |

#### 关键结果

| 系数 | Grid+Year FE | Prov×Year FE | 解读 |
|------|-------------|-------------|------|
| $\delta_1$ (D×H) | -0.0003** | -0.0007*** | 超加性损失存在 |
| $\delta_2$ (SR×D×H) | 0.0005** | 0.0010*** | SR 缓解 compound 损失 |

#### 对应脚本与输出
- **脚本**: `scripts/stata/step_compound_interaction.do`
- **输出**: `output/tables/step_compound_*.csv`, `.tex`

---

### 4.2 [Step 8] SM State-Dependence (Type I 补充)

#### 研究问题
热量损失的大小是否依赖于土壤水分状态？（验证 SM 是联合胁迫的状态调节变量）

#### 计量方程

**Eq. (2a) — SM×Heat 状态依赖 (三种表达)**:

(i) 连续: $\ln Y = \cdots + \gamma_1 (SM^{sfc} \times H) + \cdots$

(ii) 二值 P25: $\ln Y = \cdots + \gamma_2 (SM_{low} \times H) + \cdots$ 其中 $SM_{low} = \mathbb{1}(SM < P_{25})$

(iii) 分位数斜率: $\ln Y = \cdots + \sum_{q=1}^{4} \gamma_q (H \times SM_Q^{(q)}) + \cdots$

> **注意**: 这三种表达检验的是同一个 state-dependence 概念，不应视为三个独立的胜利。

**Eq. (2b) — Compound by SM Quartile**:

在每个 SM 分位数子样本内运行 Eq.(2):

$$\ln Y_{it} = \alpha_1 D + \alpha_2 H + \beta_0 SR + \theta_1(SR \times D) + \theta_3(SR \times H) + \delta_1(D \times H) + \delta_2(SR \times D \times H) + \Gamma\mathbf{X} + \mu_i + \tau_t + \varepsilon \quad \text{for } SM \in Q_q$$

#### 对应脚本与输出
- **脚本**: `scripts/stata/step8_joint_stress.do`
- **输出**: `step8_sm_heat_state_dependence.csv`, `step8_compound_by_sm.csv`, `step8_sm_heat_gradient.png`

---

### 4.3 [Step 8a] 边界诊断 (Type II 边界)

#### 研究问题
SR×D×H 的估计是否在不同 FE、年份子样本、lead test 下保持稳定？

#### 方法矩阵

**A. FE 梯度** — 检验 SR×D×H 在不同 FE 吸收水平下的变化:

| FE 结构 | Stata 语法 |
|---------|-----------|
| Grid+Year | `absorb(grid_id year)` |
| Grid+Region×Year | `absorb(grid_id region_year)` |
| Grid+Prov×Year | `absorb(grid_id prov_year)` |
| Grid+Year + Soil×Year | `absorb(grid_id year)` + `$SOIL_CTRL` |

**B. Wild Bootstrap** — 有限样本聚类推断校正:

```stata
boottest SR_x_D_x_Heat, reps(999) cluster(grid_id) seed(42)
```

**C. 年份特定 + Drop-2017**:

$$\ln Y = \cdots + \sum_{t=2016}^{2019} \delta_{2t}(SR \times D \times H \times \mathbb{1}_{year=t}) + \cdots$$

**D. Triple Lead Test** — compound 框架下的 placebo:

$$\ln Y = \cdots + \delta_2^{lead}(SR_{t+1} \times D \times H) + \cdots$$

- $\delta_2^{lead} \approx 0$: 通过 → compound buffering 非 SR 持续性伪迹

**E. D×H 支撑域分析**:
- 交叉表: D\_bin3 × H\_bin3 的样本分布
- 胁迫角落 (高D高H) 的 SR 分布 (均值、标准差、CV)
- 省×年集中度 (top 5)

**F. 响应面 (模型调整后预测值)**:
- 18 个单元: 3D\_bin × 3H\_bin × 2SR\_high
- `areg` + `margins` 导出调整后产量

#### 关键结果

| 诊断 | 结果 | 通过？ |
|------|------|--------|
| Prov×Year FE 下 SR×D×H | 0.0010*** (更强) | ✓ |
| Drop-2017 | 0.0009*** | ✓ |
| 年份特定: 4/4 年正号 | ✓ | ✓ |
| Triple lead test | SR(t+1)×D×H = -0.0003 n.s. | ✓ |
| Wild bootstrap p | < 0.05 | ✓ |

#### 对应脚本与输出
- **脚本**: `scripts/stata/step8a_boundary.do`
- **输出**: `step8a_fe_gradient.csv`, `step8a_wild_bootstrap.csv`, `step8a_year_specific.csv`, `step8a_triple_lead.csv`, `step8a_dh_support.csv`, `step8a_response_surface.csv`

---

### 4.4 [Step 8b] Specification Curve (72 规格)

#### 研究问题
SR×D×H、SR×Heat、SR×D 的估计在 72 种规格组合下符号是否稳定？

#### 设计矩阵

| 维度 | 选项 | 水平数 |
|------|------|--------|
| 热量阈值 | HDD ≥ 30°C, 32°C, 35°C | 3 |
| FE 结构 | grid+year, grid+region×year, grid+prov×year | 3 |
| 聚类 | grid, two-way (grid+year) | 2 |
| 控制变量 | 基础 ($CTRL), 扩展 ($CTRL + $SOIL\_CTRL) | 2 |
| SR 度量 | 当期 (ca), 滞后 (crc\_lag1) | 2 |

**总计**: $3 \times 3 \times 2 \times 2 \times 2 = 72$ 种规格

每种规格提取三个估计量:
- $\delta_2$ (SR×D×H): compound buffering
- $\theta_3$ (SR×Heat): 热量缓冲
- $\theta_1$ (SR×D): 干旱缓冲

#### 对应脚本与输出
- **脚本**: `scripts/stata/step8b_spec_curve.do`
- **输出**: `step8b_spec_curve.csv` (72 行 × 3 estimand), `step8b_spec_curve_figure.png`

---

## 5. [Step 4v2] SM 核心机制 — 三条主链 (Type III)

### 总体框架

SM 是核心状态变量，检验三个独立可证伪的方向预测是否同时满足:
- **Chain 1**: SM 是否比 D/H 更直接地解释产量变异？（loss function）
- **Chain 2**: SR 是否将水分状态拉向更有利的方向？（state shift）
- **Chain 3**: 控制 SM 后，compound 交互项是否发生定向变化？（conditioning）

> 三链方向都一致 → mechanism-consistent；任一不一致 → 诚实报告断裂环节。

---

### 5.1 Chain 1: SM→Yield (SM-centered loss function)

#### 研究问题
产量损失是否明显依赖于 SM 所定义的水分状态？

#### 计量方程

**Eq. (3) — FE 阶梯 (SM 系数包络)**:

$$\ln Y_{it} = \lambda \cdot SM_{it}^{sfc} + \alpha_1 D + \alpha_2 W + \alpha_3 H + \beta_0 SR + \theta_1(SR \times D) + \theta_3(SR \times H) + \Gamma\mathbf{X} + \Gamma_s\mathbf{Z}^{soil} + \text{FE} + \varepsilon$$

| 模型 | SM 变量 | FE | 聚类 | 目的 |
|------|---------|----|----|------|
| A1 | $SM^{sfc}$ | Grid+Year | grid\_id | Grid 内时间变化 |
| A2 | $SM^{sfc}$ | County+Year | county\_id | 县内空间差异 |
| A3 | $SM^{sfc}$ + $\mathbf{Z}^{soil}$ | County+Year | county\_id | 控制土壤属性 |
| A4 | $SM^{rz}$ + $\mathbf{Z}^{soil}$ | County+Year | county\_id | 根区 SM 对照 |

**Eq. (3b) — Mundlak 分解**:

$$\ln Y_{it} = \lambda_B \cdot \overline{SM}_i + \lambda_W \cdot (SM_{it} - \overline{SM}_i) + \cdots$$

- $\lambda_B$ 显著 + $\lambda_W$ 不显著 → SM-yield 关联主要来自空间差异（between），非时间变化（within）
- $\lambda_W$ 也显著 → 时间变化有贡献，信号更强

**R² 比较 (同一 common sample)**:
- F0: 无 SM (仅 D/H + controls)
- F1: + $SM^{sfc}$
- F2: + $SM^{rz}$
- $\Delta R^2$ 衡量 SM 的增量解释力

#### Chain 1 LOYO
逐年剔除 (2016–2019)，检验 SM 系数 $\lambda$ 的年份稳定性。

#### 对应脚本与输出
- **脚本**: `scripts/stata/step4_mechanism_v2.do` (Chain 1 部分)
- **输出**: `step4v2_chain1_fe_ladder.csv`, `step4v2_chain1_r2_comparison.csv`, `step4v2_chain1_loyo.csv`

---

### 5.2 Chain 2: SR→SM (State Shift)

#### 研究问题
SR 是否与更湿的 surface state 和更少的 hot-dry exposure 相关联？

#### 计量方程

**Eq. (4) — SR 位移水分状态 (以 $SM^{sfc}$ 为例)**:

$$SM_{it}^{sfc} = a_0 \cdot SR_{it} + a_1 D_{it} + a_2 W_{it} + a_3 H_{it} + a_4(SR \times D)_{it} + \Gamma\mathbf{X} + \Gamma_s\mathbf{Z}^{soil} + \mu_c + \tau_t + u_{it}$$

- $a_0 > 0$: SR 主效应提高 SM
- $a_4 > 0$: SR 在干旱条件下尤其提高 SM

**四个因变量**:

| DV | 变量 | 预期方向 |
|----|------|---------|
| $SM^{sfc}$ | `gleam_sms_mean` | $a_0 > 0$, $a_4 > 0$ |
| $SM^{rz}$ | `gleam_smrz_mean` | $a_0 > 0$, $a_4 > 0$ |
| $HotDryDays$ | `hotdrydays_tmax_ge32_and_smrz_le_basep20` | $a_0 < 0$ |
| $DryDays$ | `drydays_gleam_sms_le_basep10` | $a_0 < 0$ |

每个 DV 在 County+Year FE 和 Grid+Year FE 两种结构下分别估计。

#### 关键结果

| DV | FE | SR 主效应 ($a_0$) | SR×D ($a_4$) |
|----|----|-------------------|------------|
| $SM^{sfc}$ | County+Year | 0.0009** | 0.0038*** |
| $HotDryDays$ | County+Year | -7.49*** | — |
| $DryDays$ | County+Year | -11.37*** | — |

> **State-shift 证据清晰**: SR 提高 SM、减少极端干旱天数，方向与假设一致。

#### 对应脚本与输出
- **脚本**: `scripts/stata/step4_mechanism_v2.do` (Chain 2 部分)
- **输出**: `step4v2_chain2_sr_shifts_sm.csv`, `step4v2_chain2_loyo.csv`

---

### 5.3 Chain 3: Conditioning Sets (Compound under SM)

#### 研究问题
将 SM 代理带入 compound 模型后，SR×D×H 是否发生定向变化？

#### 计量方程

**Eq. (5) — 三组条件集 (同一 $\ln Y$ 因变量)**:

| 条件集 | RHS 新增 | Stata 命令 (County+Year FE) |
|--------|---------|----------------------------|
| Set 0 (无 SM) | — | `reghdfe ln_yield $RHS_COMPOUND $SOIL_CTRL, absorb(county_id year) vce(cluster county_id)` |
| Set 1 (+SM) | $SM^{sfc}$ | `reghdfe ln_yield $RHS_COMPOUND gleam_sms_mean $SOIL_CTRL, absorb(county_id year) vce(cluster county_id)` |
| Set 2 (+conditional) | $HotDryDays + DryDays$ | `reghdfe ln_yield $RHS_COMPOUND hotdrydays_... drydays_... $SOIL_CTRL, absorb(county_id year) vce(cluster county_id)` |

其中 `$RHS_COMPOUND` = `D_season W_season hdd_tmax_ge32 ca SR_x_D SR_x_W SR_x_Heat D_x_Heat SR_x_D_x_Heat $CTRL`

- Set 0 → Set 1: 若 $\delta_2$ 衰减 → SM 是 compound 效应的部分通道
- Set 0 → Set 2: 条件化和尾部变量通常更敏感

#### 附加: 灌溉 split (VZ2025 方向检验)

$$\text{Eq.(2)} \quad \text{分别在 } irr\_high=1 \text{ 和 } irr\_high=0 \text{ 子样本中估计}$$

- 低灌溉区: heat 损失更大，SR 缓冲更强
- 高灌溉区: heat 损失更小，SR 缓冲更弱

#### 附加: County-Year 聚合

将数据聚合至 county-year 级别（取均值），重跑 Chain 1/2/3 核心模型，检验结果在空间聚合尺度下是否一致（回应 Moulton 问题和伪精度质疑）。

#### 对应脚本与输出
- **脚本**: `scripts/stata/step4_mechanism_v2.do` (Chain 3 部分)
- **输出**: `step4v2_chain3_compound_sm.csv`, `step4v2_chain3_loyo.csv`, `step4v2_chain3_irrigation_split.csv`, `step4v2_county_aggregated.csv`

---

## 6. [Step 4 Formal] 正式中介分析 (Type III 补充)

### 研究问题
以 SM 为唯一中介变量，SR×D → SM → Yield 和 SR×D×H → SM → Yield 的间接效应是否显著？

### 计量方程

**Eq. (6a) — Mediator 方程 (a-path)**:

$$SM_{it}^{sfc} = a_4(SR \times D)_{it} + a_7(SR \times D \times H)_{it} + \text{[所有低阶项 + controls]} + \mu_c + \tau_t + u_{it}$$

**Eq. (6b) — Outcome 方程 ($\lambda$ + direct)**:

$$\ln Y_{it} = \lambda \cdot SM_{it}^{sfc} + \beta_4^{dir}(SR \times D)_{it} + \beta_7^{dir}(SR \times D \times H)_{it} + \text{[同上]} + \mu_c + \tau_t + \varepsilon_{it}$$

**间接效应**:
- Drought-water path: $\hat{a}_4 \times \hat{\lambda}$
- Compound-water path: $\hat{a}_7 \times \hat{\lambda}$

**Sobel SE** (Delta method):

$$SE_{indirect} = \sqrt{\hat{a}^2 \cdot SE_\lambda^2 + \hat{\lambda}^2 \cdot SE_a^2}$$

### 推断方法

| 方法 | 实施 | 目的 |
|------|------|------|
| Sobel SE | Delta method | 点估计 + 近似 SE |
| Cluster Bootstrap | 1000 reps, `bsample cluster(county_id)`, percentile CI | 有限样本推断 |
| LOYO | 逐年剔除 2016–2019 | 年份稳定性 |

### 两个中介变量

| 变量 | 角色 | 预期 |
|------|------|------|
| `gleam_sms_mean` (SM surface) | 主中介 | a-path 显著，λ 可能弱 |
| `drydays_gleam_sms_le_basep10` | 支撑中介 | 尾部变量，信号更锐利 |

### 关键结果 (County FE)

| Path | a-path | $\lambda$ | Indirect | Boot CI |
|------|--------|-----------|----------|---------|
| Drought (SM sfc) | 0.0073*** | 0.41 n.s. | 0.003 | [-0.001, 0.009] |
| Compound (SM sfc) | 0.00002 n.s. | 0.41 n.s. | ≈0 | — |
| Drought (drydays) | -11.37*** | -0.0014** | 0.016 | — |

> **解读**: SM surface 的 a-path 清晰但 λ 不显著（closure 弱）；drydays 的 λ 显著，提供最强通道证据。Grid FE 下 λ 甚至反号 (-0.24 n.s.)，反映 T=4 短面板 grid 内 SM 变异不足。

### 对应脚本与输出
- **脚本**: `scripts/stata/step4_mediation_formal.do`
- **输出**: `step4v2_mediation_primary.csv`, `step4v2_mediation_bootstrap.csv`, `step4v2_mediation_supporting.csv`, `step4v2_mediation_loyo.csv`

---

## 7. [Step 5] 异质性分析

### 研究问题
SR 缓冲效应在不同区域、水分条件、灌溉水平下是否有差异？

### 计量方程

在各子样本内运行 Eq.(1):

$$\ln Y_{it} = \cdots + \theta_1(SR \times D) + \theta_3(SR \times H) + \cdots + \mu_i + \tau_t + \varepsilon \quad \text{for subsample } s$$

### 分层维度

| 维度 | 分组 | 子样本 N |
|------|------|---------|
| 产区 (5区) | NE, HHH, SW, NW, Other | 25,041 / 13,165 / 18,094 / 5,540 / 7,198 |
| SM 分位数 | Q1 (最干) – Q4 (最湿) | ~15,449 each |
| 灌溉 | Low irr / High irr | 约 1:1 |
| 干燥度 | Humid / Arid | 约 1:1 |

### 关键结果

| 维度 | SR×D 最强 | SR×Heat 最强 |
|------|----------|-------------|
| 产区 | NE: 0.131***, NW: 1.174*** | HHH: 0.004*** |
| SM 分位数 | Q1(driest): 0.239*** | — |
| 灌溉 | Low irr: 0.169*** (high irr: 0.025 n.s.) | — |

### 对应脚本与输出
- **脚本**: `scripts/stata/step5_heterogeneity.do`
- **输出**: `step5_region.csv`, `step5_sm_quartile.csv`, `step5_irr_aridity.csv`

---

## 8. [Step 7 / 7B] 稳健性检验

### 8.1 [Step 7] 基础稳健性

#### 方法矩阵

| 检验 | 变化 | 方程 |
|------|------|------|
| 热量阈值 | HDD ≥ 30/32/35 | Eq.(1) 替换 H 定义 |
| Prov×Year FE | 替代 FE | Eq.(1) 换 `absorb(grid_id prov_year)` |
| Two-way cluster | SE 膨胀 | Eq.(1) 换 `vce(cluster grid_id year)` |
| 滞后 SR | `crc_lag1` 替代 `ca` | Eq.(1) 替换 SR 定义 |
| SR 自相关 | $\rho$(ca, ca\_f1), CV(ca) | 描述性诊断 |

#### 关键结果

| 检验 | SR×D | SR×Heat | 判定 |
|------|------|---------|------|
| Prov×Year FE | 0.022 n.s. | 0.0013** | SR×D 弱化，SR×Heat 稳健 |
| Two-way cluster | SE 膨胀 | 5% 水平 | SR×Heat 边际稳健 |
| 滞后 SR | 0.059*** | -0.0009*** (反号!) | SR×Heat 不稳健 |

### 8.2 [Step 7B] 额外稳健性

| 检验 | 方法 | 结果 |
|------|------|------|
| LOPO | 逐省剔除 | SR×D: [0.004, 0.092] 全正; SR×Heat: [0.0002, 0.0014] 全正 |
| Winsorize (1/99) | 极端值处理 | SR×D: 0.042→0.057 (增强); SR×Heat: 稳定 |
| Oster bounds | OVB 诊断 ($\delta$) | SR×D: $\delta$=9,554; SR×Heat: $\delta$=883 (极稳健) |
| 非线性 | SPEI bins / D² / HDD bins | SR×Heat 在所有规格下稳健 |
| Year-drop | 逐年剔除 | ⚠ Drop-2017 使 SR×D 反号 (-0.026 n.s.) |

### 对应脚本与输出
- **Step 7**: `scripts/stata/step7_sensitivity.do` → `step7_heat_threshold.csv`, `step7_fe_cluster.csv`, `step7_sm_mechanism.csv`
- **Step 7B**: `scripts/stata/step7b_robustness_extra.do` → `step7b_lopo.csv`, `step7b_winsor.csv`, `step7b_oster.csv`, `step7b_nonlinear.csv`, `step7b_yearly.csv`

---

## 9. [Step 6] DML 检验

### 研究问题
固定效应估计是否对函数形式假设敏感？用机器学习方法作为交叉验证。

### 方法

**Partially Linear Regression (PLR) via Double Machine Learning**:

1. Within-demean by grid\_id + year（模拟 FE 吸收）
2. 分别对 SR×D 和 SR×Heat 做 PLR-DML:
   - Nuisance model: Random Forest (500 trees, max\_depth=10)
   - Cross-validation: 5-fold
3. 比较 DML $\hat{\theta}$ 与 FE $\hat{\theta}$ 的符号和量级

### 关键结果

| Estimand | FE | DML | 一致？ |
|----------|-----|-----|--------|
| SR×D | 0.042 | 0.047 | ✓ (同号，近似量级) |
| SR×Heat | 0.0011 | 0.0002 | ✓ (同号，DML 更小) |

### 对应脚本与输出
- **脚本**: `scripts/python/step6_dml.py`
- **输出**: `output/tables/step6_dml.csv`

---

## 10. 关键结果速查表

### 10.1 核心估计量

| Finding | Estimate | 框架角色 | 稳健性 |
|---------|----------|---------|--------|
| D×H compound damage | -0.0003** | Type I: 超加性 | ✓ |
| SR×D×H (32°C, grid+yr) | 0.0005** | Type II: 调节 | ✓ (4/4 年, lead pass) |
| SR×D×H (prov×yr) | 0.0010*** | Type II: 调节 | ✓ |
| SR×D→SM (county) | 0.0038*** | Type III: state-shift | ✓ |
| SR→DryDays (county) | -11.37*** | Type III: state-shift | ✓ |
| SM→Yield (grid) | 0.41 n.s. | Type III: closure | ✗ (弱) |
| SM→Yield (county agg.) | 1.581*** | Type III: closure | ✓ (区域级) |
| Formal indirect (SM sfc) | 0.003, CI incl. 0 | Type III: mediation | ✗ (弱) |
| Supporting indirect (drydays) | 0.016*** (grid FE) | Type III: mediation | ✓ |

### 10.2 Estimand–Script 交叉索引

| Estimand | 主脚本 | 输出表 | 报告 Slide |
|----------|--------|--------|-----------|
| $\theta_1$ (SR×D) | step1\_baseline\_FE.do | step1\_baseline\_FE.csv | 6 |
| $\theta_3$ (SR×Heat) | step1\_baseline\_FE.do | step1\_baseline\_FE.csv | 6 |
| $\delta_1$ (D×H) | step\_compound\_interaction.do | step\_compound\_*.csv | 7 |
| $\delta_2$ (SR×D×H) | step\_compound\_interaction.do | step\_compound\_*.csv | 7–8 |
| $\delta_2$ FE gradient | step8a\_boundary.do | step8a\_fe\_gradient.csv | 21 |
| $\delta_2$ lead test | step8a\_boundary.do | step8a\_triple\_lead.csv | 10 |
| $\delta_2$ year-specific | step8a\_boundary.do | step8a\_year\_specific.csv | 10 |
| $\delta_2$ spec curve | step8b\_spec\_curve.do | step8b\_spec\_curve.csv | 23 |
| SM×H state-dep | step8\_joint\_stress.do | step8\_sm\_heat\_state\_dep.csv | 25 |
| $\lambda$ (SM→Y) | step4\_mechanism\_v2.do | step4v2\_chain1\_fe\_ladder.csv | 13–14 |
| SR→SM | step4\_mechanism\_v2.do | step4v2\_chain2\_sr\_shifts\_sm.csv | 15 |
| Conditioning sets | step4\_mechanism\_v2.do | step4v2\_chain3\_compound\_sm.csv | 16 |
| Formal indirect | step4\_mediation\_formal.do | step4v2\_mediation\_primary.csv | 19 |
| Heterogeneity | step5\_heterogeneity.do | step5\_*.csv | 26–27 |
| DML | step6\_dml.py | step6\_dml.csv | — |
| LOPO/Oster/winsor | step7b\_robustness\_extra.do | step7b\_*.csv | 22 |

---

## 附录: 语言纪律

### 禁止用语
- ❌ causal effect, robust finding, 因果中介, a-path/b-path/Sobel test (作为因果声明)
- ❌ identification strategy, natural experiment, instrumental variable

### 替代用语
- ✅ conditional association, channel-consistent correlation structure
- ✅ well-bounded association, mechanism-consistent pathway
- ✅ state-shift evidence, state-dependence, response surface modifier

### 定位语句
- "SR modifies the joint stress response surface" ≠ "SR has a causal effect on yield through SM"
- "Grid 级主效应识别 + 区域状态级机制一致性"
- "State-shift 强, closure 弱 — 这不是降格，而是校准"

---

> **文档维护**: 本说明书与 `output/reports/complete_report_v6.Rmd` (v6.1) 同步，对应 `CLAUDE.md` 中的 Analysis Progress 表。如有方程或结果更新，两处需同步修改。
