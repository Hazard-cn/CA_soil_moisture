# V3 Decomposition Equation Plan

日期：2026-04-09

## 任务目标

在现有 `v3` panel FE 框架下，不直接上全 SEM，而是先建立一套可解释、可分解、可汇报的两层 decomposition system，用来把 `SR` 对产量损失的缓解拆成：

1. `direct buffering`
2. `SM-mediated buffering`

核心不再是一般性的 Baron-Kenny 中介，而是 stress-profile-specific decomposition。

## 数据与主规格边界

- 主数据：`data/processed/v3_analysis_ready.dta`
- 主样本：`if main_sample == 1`
- 主 FE：`absorb(grid_id year)`
- 主聚类：`vce(cluster grid_id)`
- 主 controls：沿用 `v3_macros_include.do` 中对应窗口的 `CTRL_*`
- 主热阈值：沿用当前 `H = hdd_ge32*`
- 主 mediator：`gleam_sms_mean`

## 为什么主 mediator 先用 `gleam_sms_mean`

- 现有 formal mediation 主规格已经把 `gleam_sms_mean` 定义为 primary mediator。
- `step_moderated_mediation.do`、`step4_mediation_formal.do` 的参数提取与报告接口也围绕 `gleam_sms_mean` 建立。
- 这一步的目标是先把 decomposition algebra 和 FE identification 跑通，不先把 mediator source comparison 混进主结论。

第一轮 robustness：

- `gleam_smrz_mean`

第二轮 source robustness：

- `swsm_l3_mean`
- `era5l_swvl3_mean`

## 估计系统

### Layer 2: Mediator equation

对主窗口 `w`，先估：

\[
SM_{it}
=
\alpha_i + \gamma_t
+ \pi_D D_{it}
+ \pi_H H_{it}
+ \pi_W W_{it}
+ \pi_{DH}(D_{it}\times H_{it})
+ \pi_{SR} SR_{it}
+ \lambda_D(SR_{it}\times D_{it})
+ \lambda_H(SR_{it}\times H_{it})
+ \lambda_W(SR_{it}\times W_{it})
+ \lambda_{DH}(SR_{it}\times D_{it}\times H_{it})
+ \kappa'X_{it}
+ u_{it}
\]

这一层回答的是：在给定 stress profile 下，`SR` 对 `SM` 的边际影响有多大。

定义：

\[
a(d,h,w) \equiv
\frac{\partial SM}{\partial SR}\Big|_{d,h,w}
=
\pi_{SR} + \lambda_D d + \lambda_H h + \lambda_W w + \lambda_{DH} d h
\]

如果汇报时不希望 wetness 维度进入 headline decomposition，可以把主文固定为 `w = 0`，但估计方程本身保留 `W` 和 `SR×W`。

### Layer 3: Outcome decomposition equation

在同一窗口、同一样本上估：

\[
\ln y_{it}
=
\alpha_i + \gamma_t
+ \beta_D D_{it}
+ \beta_H H_{it}
+ \beta_W W_{it}
+ \beta_{DH}(D_{it}\times H_{it})
+ \beta_{SR} SR_{it}
+ \theta_D(SR_{it}\times D_{it})
+ \theta_H(SR_{it}\times H_{it})
+ \theta_W(SR_{it}\times W_{it})
+ \theta_{DH}(SR_{it}\times D_{it}\times H_{it})
+ \delta SM_{it}
+ \phi_D(D_{it}\times SM_{it})
+ \phi_H(H_{it}\times SM_{it})
+ \rho'X_{it}
+ \varepsilon_{it}
\]

主规格先不放：

- `SR×SM`
- `SR×D×SM`
- `SR×H×SM`

原因是这会把问题从“SM 是否承接了一部分缓解”升级成“SR 是否还改变了 SM 的调节斜率”，主问题会失焦。

定义：

\[
b(d,h) \equiv
\frac{\partial \ln y}{\partial SM}\Big|_{d,h}
=
\delta + \phi_D d + \phi_H h
\]

## 直接部分与间接部分

### Direct buffering

控制了 `SM`、`D×SM`、`H×SM` 之后，`SR` 对产量的剩余边际作用定义为：

\[
DE(d,h,w)
\equiv
\frac{\partial \ln y}{\partial SR}\Big|_{SM,d,h,w}
=
\beta_{SR} + \theta_D d + \theta_H h + \theta_W w + \theta_{DH} d h
\]

如果只想看“stress-driven buffering”而不把 baseline `SR` 主效应算进去，则另报：

\[
DE^{stress}(d,h,w)
=
\theta_D d + \theta_H h + \theta_W w + \theta_{DH} d h
\]

### SM-mediated buffering

\[
IE(d,h,w)
=
a(d,h,w)\times b(d,h)
\]

即：

\[
IE(d,h,w)
=
(\pi_{SR} + \lambda_D d + \lambda_H h + \lambda_W w + \lambda_{DH} d h)
(\delta + \phi_D d + \phi_H h)
\]

### Total SR slope under a stress profile

\[
TE(d,h,w)
=
DE(d,h,w) + IE(d,h,w)
\]

并可进一步报告：

\[
Share_{med}(d,h,w)
=
\frac{IE(d,h,w)}{DE(d,h,w)+IE(d,h,w)}
\]

## 第一轮实现范围

主文不直接做 “6 windows × 4 SM sources × 多 profile” 的全矩阵，先做一个 anchor specification。

### Main specification

- window：`full`
- mediator：`gleam_sms_mean`
- FE：`grid_id + year`
- controls：`CTRL_full`
- 样本：`main_sample == 1`

### First robustness

- 同一 full-season decomposition
- mediator 换成 `gleam_smrz_mean`

### Optional extension after main run is stable

- 6-window extension
- `swsm_l3_mean` / `era5l_swvl3_mean` source comparison
- county + year + soil controls robustness

## Stress profile design

第一轮不做连续 3D surface，先做离散 profile decomposition。

建议主文报告 4 个 profile：

1. `Baseline`: `d = 0`, `h = 0`, `w = 0`
2. `D only`: `d = P75(D | D>0)`, `h = 0`, `w = 0`
3. `H only`: `d = 0`, `h = P75(H | H>0)`, `w = 0`
4. `D+H`: `d = P75(D | D>0)`, `h = P75(H | H>0)`, `w = 0`

appendix 可再加：

- `P90 + P90`
- empirical 90th percentile joint-stress profile

## 不确定性估计

这一步不建议硬上 `suest + reghdfe`。

主方案：

- point estimates：两条 FE 方程分别用 `reghdfe`
- uncertainty for `IE/DE/TE`：按 `grid_id` 做 cluster bootstrap

每次 bootstrap 复制中：

1. 重估 Layer 2
2. 重估 Layer 3
3. 计算 `a(d,h,w)`、`b(d,h)`、`IE`、`DE`、`TE`

输出：

- bootstrap mean
- bootstrap SE
- percentile CI 或 normal-approx CI

## 拟新增文件

- `scripts/stata/v3decomp_macros_include.do`
- `scripts/stata/v3decomp_step0_profiles.do`
- `scripts/stata/v3decomp_step1_equations.do`
- `scripts/stata/v3decomp_step2_bootstrap.do`
- `scripts/R/v3decomp_plots.R`
- `output/reports/v3decomp_beamer_report.Rmd`

## 结果表与图

### Tables

1. Layer 2 mediator equation coefficient table
2. Layer 3 decomposition equation coefficient table
3. `DE / IE / TE / mediated share` across stress profiles

### Figures

1. `a(d,h,w)` profile plot
2. `b(d,h)` profile plot
3. `DE vs IE vs TE` grouped bar or point-range plot
4. mediated share by stress profile

## 验证清单

- Layer 2 和 Layer 3 使用完全一致的 estimation sample
- mediator 主效应与交乘项命名映射无误
- `DE` 与 `IE` 的 profile formula 和脚本计算一致
- bootstrap 程序按 `grid_id` cluster resample，而不是逐行 resample
- `w=0` 的 headline decomposition 与含 `w` 的完整公式可以相互核对
- 主规格 full-season 先能稳定复现，再扩展到窗口/来源 robustness

## 识别与解释纪律

- 语言上不称为 “causal mediation”
- 称为 `direct buffering component` 与 `SM-mediated component`
- 明确说明这是基于 FE conditional association 的 profile-specific decomposition
- 不把 `SR×SM` 类高阶项放入主规格，以保持“直接部分 vs 通过 SM 的部分”这一分解含义稳定
