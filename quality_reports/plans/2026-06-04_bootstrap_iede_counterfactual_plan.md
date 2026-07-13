# Bootstrap IE/DE/TE + 异质性 + 反事实估计方案

**日期:** 2026-06-04
**样本:** F4 最宽版(zone_core=1, sr_within=1, 其余开关全关),N≈11,656, grid≈3,200
**模型:** 有调节中介(两方程),3 hazard × 2 mediator × 2 transform = 12 specs
**目标:** 对选定主设定跑完完整实证 → 填入 SL2 draft

---

## 总架构(三个模块,顺序执行)

```
Module 1: Baseline bootstrap IE/DE/TE (主设定, 1000 reps)
    → 12 specs × 3 SR levels = 36 组效应 + BC CI
    ↓
Module 2: 异质性 bootstrap (子组, 500 reps each)
    → 灌溉 (2组) + 产区 (5-6组) + AI>2灌溉 (2组)
    → 每组 × 12 specs × 3 SR levels
    ↓
Module 3: 反事实情景 (基于 Module 1+2 的系数)
    → 复合极端情景 × 区域权重 → 潜在保护产量 + 不确定性带
```

**总算力估计:** Module 1 ≈ 12 × 1000 × 2 回归 = 24,000 次 reghdfe;Module 2 ≈ 10 子组 × 12 × 500 × 2 = 120,000 次;Module 3 几乎不耗时(纯计算)。StataMP 18 with ~3,200 grids,估计 Module 1 ≈ 2-4 小时,Module 2 ≈ 8-15 小时。

---

## Module 1: Baseline Bootstrap IE/DE/TE

### 1.1 设计

对 F4 最宽版的 12 个 specs(3 hazard × 2 mediator × 2 transform),每个 spec 做:
1. 跑两方程(mediator eq + outcome eq),提取 a1, a3, b, c1, c3
2. 在 SR 的 P25/P50/P75 处算 IE(r), DE(r), TE(r)
3. cluster bootstrap 1000 reps,输出 BC 百分位 CI

### 1.2 关键 Stata 实现

```stata
* ===== 核心 bootstrap 程序 =====
* 必须定义为 program(bootstrap 要求 eclass/rclass)
* 关键: globals 不穿透 program → 控制变量必须硬写或通过 args 传入

capture program drop boot_iede
program define boot_iede, rclass
    syntax, hazard_var(string) sr_var(string) mediator_var(string) ///
           outcome_var(string) interaction_var(string) ///
           ctrl_list(string) sr_p25(real) sr_p50(real) sr_p75(real)

    * --- mediator equation ---
    quietly reghdfe `mediator_var' `hazard_var' `sr_var' `interaction_var' ///
        `ctrl_list', absorb(grid_id year) vce(robust)
    local a1 = _b[`hazard_var']
    local a3 = _b[`interaction_var']

    * --- outcome equation ---
    quietly reghdfe `outcome_var' `hazard_var' `sr_var' `interaction_var' ///
        `mediator_var' `ctrl_list', absorb(grid_id year) vce(robust)
    local c1 = _b[`hazard_var']
    local c3 = _b[`interaction_var']
    local b  = _b[`mediator_var']

    * --- IE/DE/TE at three SR levels ---
    foreach lev in 25 50 75 {
        local r = `sr_p`lev''
        return scalar IE_P`lev' = (`a1' + `a3' * `r') * `b'
        return scalar DE_P`lev' = `c1' + `c3' * `r'
        return scalar TE_P`lev' = (`a1' + `a3' * `r') * `b' + `c1' + `c3' * `r'
    }

    * --- 也返回原始系数(供诊断) ---
    return scalar a1 = `a1'
    return scalar a3 = `a3'
    return scalar b  = `b'
    return scalar c1 = `c1'
    return scalar c3 = `c3'
end
```

### 1.3 调用(单个 spec 示例)

```stata
* --- 准备: 算 SR 的分位数(在 bootstrap 前、全样本上算一次,冻结) ---
quietly summarize ca_ratio, detail
local sr_p25 = r(p25)
local sr_p50 = r(p50)
local sr_p75 = r(p75)

* --- 关键: xtset, clear 必须在 bootstrap 前调用! ---
* bootstrap 按 grid_id 重抽 → 产生重复 panel ID → xtset 会报 r(451)
* reghdfe 的 absorb() 不需要 xtset,所以 clear 是安全的
xtset, clear

* --- bootstrap ---
set seed 42

bootstrap ///
    IE_P25=r(IE_P25) IE_P50=r(IE_P50) IE_P75=r(IE_P75) ///
    DE_P25=r(DE_P25) DE_P50=r(DE_P50) DE_P75=r(DE_P75) ///
    TE_P25=r(TE_P25) TE_P50=r(TE_P50) TE_P75=r(TE_P75) ///
    a1=r(a1) a3=r(a3) b=r(b) c1=r(c1) c3=r(c3), ///
    reps(1000) cluster(grid_id) idcluster(newgrid) ///
    seed(42) saving("$tempdir/boot_drought_mean_raw.dta", replace) : ///
    boot_iede, ///
        hazard_var(D_full_raw) sr_var(ca_ratio) ///
        mediator_var(gleam_smrz_mean_raw) ///
        outcome_var(ln_yield_raw) ///
        interaction_var(SR_x_D_full_raw) ///
        ctrl_list(W_full_raw hdd_ge32_raw pr_sum et0_sum gdd_10_30 irr_frac aridity) ///
        sr_p25(`sr_p25') sr_p50(`sr_p50') sr_p75(`sr_p75')

* --- 提取 BC CI ---
estat bootstrap, bc percentile
```

### 1.4 循环跑 12 个 specs

```stata
* 用 hazard × mediator × transform 三层嵌套循环
* 每轮输出: $tempdir/boot_{hazard}_{mediator}_{transform}.dta
* 汇总到: $outdir/baseline_bootstrap_iede.csv

local hazards   "drought heat hotdry"
local mediators "mean dry"
local transforms "raw winsor_1_99"

foreach h of local hazards {
    foreach m of local mediators {
        foreach t of local transforms {
            * ... 构造变量名(hazard_var/mediator_var 等)
            * ... 调用 bootstrap (如上)
            * ... estat bootstrap, bc → 存 CI
            * ... 追加一行到 results csv
        }
    }
}
```

### 1.5 输出格式

```
baseline_bootstrap_iede.csv:
  hazard, mediator, transform, effect, ca_level, ca_value,
  point_est, bs_se, ci_lo_bc, ci_hi_bc, ci_lo_pct, ci_hi_pct, N_boot
```

---

## Module 2: 异质性 Bootstrap(子组)

### 2.1 设计

三类异质性,每类在子组内重估**同一套 12 specs**:
- **灌溉:** high_irr / low_irr(全样本二分)
- **产区:** NE / HHH / NW / SW / SH (/ Other)
- **AI>2 灌溉:** 干旱区内 high_irr / low_irr

每组 bootstrap **500 reps**(子组 N 小,1000 reps 不现实;500 足以出 BC CI)。

### 2.2 实现要点

```stata
* --- 子组循环模板 ---
local subgroups_irr "high_irr low_irr"
local subgroups_zone "NE HHH NW SW SH"
local subgroups_ai2irr "ai2_high_irr ai2_low_irr"

foreach sg_type in irr zone ai2irr {
    foreach sg of local subgroups_`sg_type' {
        * --- 限制样本 ---
        preserve
        keep if `sg_flag' == 1   // 事先生成的 0/1 标记

        * --- 重算该子组的 SR P25/P50/P75(子组特异) ---
        quietly summarize ca_ratio, detail
        local sr_p25 = r(p25)
        local sr_p50 = r(p50)
        local sr_p75 = r(p75)

        * --- xtset, clear ---
        xtset, clear

        * --- bootstrap 500 ---
        set seed 42
        bootstrap ..., reps(500) cluster(grid_id) idcluster(newgrid) ///
            saving("$tempdir/boot_`sg'_`h'_`m'_`t'.dta", replace) : ///
            boot_iede, ...

        restore
    }
}
```

### 2.3 子组样本量预警

| 子组 | 预估 N | 预估 grids | 风险 |
|---|---|---|---|
| high_irr(全样本) | ~5,400 | ~1,500 | OK |
| low_irr(全样本) | ~6,200 | ~1,700 | OK |
| NE | ~4,800 | ~1,200 | OK |
| HHH | ~2,500 | ~650 | 偏小,CI 宽 |
| NW | ~1,500 | ~400 | 小,CI 宽 |
| SW | ~1,800 | ~500 | 小 + 可能无 SR 变异 |
| SH | ~500 | ~150 | **很小,bootstrap 可能不稳** |
| AI>2 high_irr | ~4,200–5,400 | ~1,200 | OK |
| AI>2 low_irr | ~600–750 | ~200 | **小,但 draft 已标注 caveat** |

**SH 和 AI>2 low_irr:** N<1000 / grids<250 → bootstrap SE 可能不稳;报告时加"small-sample caveat"。若 bootstrap 不收敛(极端 CI),改用 delta method 近似。

### 2.4 输出格式

```
het_bootstrap_iede.csv:
  het_type, subgroup, hazard, mediator, transform, effect, ca_level, ca_value,
  point_est, bs_se, ci_lo_bc, ci_hi_bc, N_boot, N_sample, N_grids
```

---

## Module 3: 反事实情景估计

### 3.1 设计思路

反事实不是"如果没有还田会怎样"(因果断言,数据不支持),而是**"在复合极端情景下,不同还田水平的条件产量差异有多大"**(情景计算,基于估计的条件梯度)。

**语言:** "潜在产量保护"/ "情景下的条件差异",**不是**"因果反事实"。

### 3.2 三个情景

| 情景 | 定义 | 含义 |
|---|---|---|
| **S1: 当前暴露 × SR 从 P25→P75** | 在各区的**实际**复合暴露下,SR 从低到高的条件产量差 | "如果在当前条件下扩大还田" |
| **S2: 极端年暴露 × SR 从 P25→P75** | 把复合暴露设为**样本 P90**(极端年),SR 从低到高 | "如果在极端年扩大还田" |
| **S3: 区域靶向** | 各产区/灌溉组分别算 S1、S2 | "哪里的潜在保护最大" |

### 3.3 计算公式

```
对胁迫 h、SR 水平 r:
  条件产量(对数) = TE(r) × Hazard_level
                  = [IE(r) + DE(r)] × Hazard_level

SR 从 P25 到 P75 的条件产量差:
  Δln_yield = TE(P75) × Hazard - TE(P25) × Hazard
            = [TE(P75) - TE(P25)] × Hazard

换算为产量百分比变化:
  %ΔY ≈ exp(Δln_yield) - 1

不确定性: 从 bootstrap 的 1000 次 TE(P75)-TE(P25) 分布中取 BC CI
```

### 3.4 Stata 实现

```stata
* ===== 反事实情景计算(纯后处理,不需要重跑回归) =====
* 输入: baseline_bootstrap_iede.csv (Module 1 输出)
*       het_bootstrap_iede.csv (Module 2 输出)
*       原始数据中的 hazard 暴露分布

* --- Step 1: 从原始数据算暴露量 ---
use "$datadir/F4_main_sample.dta", clear

* 各区域的 hazard 暴露 P50 和 P90
foreach h in D_full_raw hdd_ge32_raw HotDryPr_full_raw {
    quietly summarize `h', detail
    local `h'_p50 = r(p50)
    local `h'_p90 = r(p90)

    * 按产区
    levelsof maize_zone, local(zones)
    foreach z of local zones {
        quietly summarize `h' if maize_zone == "`z'", detail
        local `h'_`z'_p50 = r(p50)
        local `h'_`z'_p90 = r(p90)
    }
}

* --- Step 2: 从 bootstrap saved datasets 算 ΔTE ---
* 每个 bootstrap rep 已存了 TE_P25 和 TE_P75 → 逐 rep 算差
use "$tempdir/boot_hotdry_mean_raw.dta", clear

gen delta_TE = TE_P75 - TE_P25

* --- Step 3: 乘以暴露量 → 条件保护量(对数) ---
* S1: 中位暴露
gen delta_lnY_S1 = delta_TE * `HotDryPr_full_raw_p50'
* S2: 极端暴露(P90)
gen delta_lnY_S2 = delta_TE * `HotDryPr_full_raw_p90'

* 换算百分比
gen pct_protect_S1 = exp(delta_lnY_S1) - 1
gen pct_protect_S2 = exp(delta_lnY_S2) - 1

* --- Step 4: BC CI ---
* 点估计 = 原始系数(non-bootstrap)算的 delta_TE × Hazard
* CI = bootstrap 分布的 2.5% 和 97.5% 分位(BC 校正)
foreach scenario in S1 S2 {
    quietly summarize pct_protect_`scenario', detail
    local pt_`scenario' = pct_protect_`scenario'[1]  // rep=0 是原始估计
    * BC CI(简化版,完整版用 estat bootstrap 的 BC 公式)
    _pctile pct_protect_`scenario', percentiles(2.5 97.5)
    local ci_lo_`scenario' = r(r1)
    local ci_hi_`scenario' = r(r2)
}
```

### 3.5 输出(反事实结果表)

```
counterfactual_scenarios.csv:
  scenario, hazard, region, irr_status,
  hazard_level(P50/P90), SR_from, SR_to,
  delta_TE, delta_lnY,
  pct_protection, pct_ci_lo, pct_ci_hi,
  N_sample, N_boot
```

### 3.6 可视化(Nature Food 主图之一)

**Fig 5 (反事实地图):** 中国玉米产区地图,颜色 = 各区 S2(极端年)下 SR 从 P25→P75 的潜在保护百分比;误差棒 = BC CI。叠加灌溉状态底图。→ 用 R/ggplot2 + `sf` 出图(Stata 出数据,R 出图)。

---

## 执行顺序 & 文件产出

| 步骤 | 脚本 | 输出 | 预估时间 |
|---|---|---|---|
| 0 | 锁定 F4 最宽版样本 + 生成子组标记 | `F4_main_sample.dta` | 5 min |
| 1 | Module 1: baseline bootstrap 1000 | `baseline_bootstrap_iede.csv` + 12 个 `.dta` | 2-4 h |
| 2 | Module 2: het bootstrap 500 | `het_bootstrap_iede.csv` + N×12 个 `.dta` | 8-15 h |
| 3 | Module 3: 反事实计算(纯后处理) | `counterfactual_scenarios.csv` | 10 min |
| 4 | 汇总表 + 出图(R) | 主表/主图(填 draft) | 1-2 h |

**总计:** 约 10-20 小时 Stata 运行(可后台/过夜)+ 2 小时 R 出图。

---

## 陷阱清单(必须避免)

| # | 陷阱 | 后果 | 防护 |
|---|---|---|---|
| 1 | 忘记 `xtset, clear` | bootstrap 重抽产生重复 panel ID → r(451) | **每个 bootstrap 调用前必须 xtset, clear** |
| 2 | globals 不穿透 program | $CTRL 在 program 内为空 → 遗漏控制变量 | 通过 `ctrl_list()` 参数传入,或在 program 内硬写 |
| 3 | SR 分位数在 bootstrap 内重算 | 每次重抽的 P25/P50/P75 不同 → IE/DE 定义漂移 | **SR 分位数在 bootstrap 外算一次,冻结传入** |
| 4 | 子组太小 bootstrap 不收敛 | CI 为 [−∞, +∞] 或极端值 | 检查 N_grids>100;若 <100 改用 delta method |
| 5 | seed 不一致 | 不同 spec 的 bootstrap 结果不可比 | 每个 spec **统一 `set seed 42`** 在 bootstrap 前 |
| 6 | 反事实用因果语言 | 审稿人攻击 | 全程"潜在保护/条件差异",不碰"反事实效应" |
| 7 | reghdfe + bootstrap 的 absorb | reghdfe 的 absorb 在 bootstrap 内正常工作,但 `vce(cluster)` 要改成 `vce(robust)` | program 内用 `vce(robust)`(外层 bootstrap 已做 cluster) |

---

## 与 SL2 Draft 的对接

| Draft 段落 | 需要的数字 | 来自 |
|---|---|---|
| R1(三通道类型学) | a1, b, IE share | Module 1 baseline |
| R2(SR 衰减) | c3, a3, IE/DE/TE at P25/P50/P75 + CI | Module 1 |
| R3(干旱区灌溉梯度) | 2×2 表的 c3 + CI | Module 2 (AI>2 irr) |
| R4(产区异质性) | 各区 c3 + CI | Module 2 (zone) |
| R5(反事实,如写入) | %保护量 + CI | Module 3 |
| ED Fig 2(稳定性) | 128-scale 已有 | 现有数据 |
| Methods(bootstrap 描述) | reps, BC CI, cluster | 本文档 |
