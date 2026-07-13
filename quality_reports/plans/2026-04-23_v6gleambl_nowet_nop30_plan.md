## 任务
在 11 类 `M_dry` 的 GLEAM baseline 上进一步收紧规格，去掉 `M_wet` 和 `D` 对应的 `W` 控制，同时不跑 `v3pre30`，结果写入新文件。

## 实施
1. 基于 `v6gleambl_nomwet_*` 复制出新的 `v6gleambl_nowet_nop30_*` 脚本。
2. 在 `step0` 中去掉 `W_w` 的样本锁定条件，并把窗口集合改为 `v3he hema fullnew`。
3. 在 `step1` 中从 mediator equation 和 outcome equation 同时移除 `W_w`，保留 `D_w`、`ca`、`SR_x_D_w`、`M_dry`、`hdd_ge32`、`pr_sum`、`et0_sum`、`gdd_10_30`、`irr_frac`、`aridity`。
4. 顺序执行新的 `step0` 和 `step1`，结果写入 `v6gleambl_nowet_nop30_*` 文件，不覆盖旧版输出。

## 验证
- 新结果文件为 `temp/2026-04-23_newSMsplit/v6gleambl_nowet_nop30_baseline_coefficients.csv`
- 规格数应为 `66`
- sample tag 数应为 `33`
- family 仍覆盖 11 类 `M_dry` 对应的 7 个 family 名称
- `window` 中不应出现 `v3pre30`
- `term` 与 `regressor` 中不应出现 `M_wet` 或 `W_w`
