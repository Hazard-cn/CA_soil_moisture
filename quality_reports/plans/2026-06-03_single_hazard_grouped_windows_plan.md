# Single-hazard grouped-window screen plan

日期：2026-06-03

## 目标

在固定 `main_sample == 1` 且 `ggcp10_maize_frac >= 0.05` 后的 128 个唯一样本版本上，改用单一 hazard 的多窗口联合方程，检查窗口信号是否会因为同类窗口之间相互控制而改善。

## 样本

- 固定筛选：`main_sample == 1`、`ggcp10_maize_frac >= 0.05`
- 平行规则：`zone_core`、`yield_domain`、`yield_jump`、`sm_sd`、`sm_coverage`、`sr_within`、`years_ge3`、`stable_province`
- 去重后样本版本：沿用 128 版

## 方程

对每个样本版本、每个 hazard、每个窗口组分别估计：

```text
ln_yield_it = sum_k beta_k hazard_window_k,it
              + ca_it + window controls + grid FE + year FE + e_it
```

其中 window controls 为窗口组内每个窗口对应的 `pr_sum`、`et0_sum`、`gdd`，再加 `irr_frac` 与 `aridity`。不纳入 SR 交互项。

## 窗口组

- `v3pm10_hepm10`: `v3pm10` + `hepm10`
- `v3pre30_v3he_hema`: `v3pre30` + `v3he` + `hema`
- `v3he_hema`: `v3he` + `hema`

## Hazard

- `drought`: `D_*`
- `heat32`: `hdd_ge32_*`
- `heat35`: `hdd_ge35_*`
- `hotdry`: `HotDryPr_*`

## 主要输出

- 每个窗口组的系数、p 值、负向显著标记
- 按 hazard-window group 汇总 `hepm10` 负向显著、组内最强负向窗口、placebo 负向显著等指标
- 对三组窗口分别说明是否改善当前生物学窗口筛
