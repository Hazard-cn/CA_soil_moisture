## 任务
重跑 11 类 `M_dry` 的四窗 GLEAM baseline，去掉对应 `M_wet` 控制，结果写入新文件，不覆盖既有 `v6gleambl` 输出。

## 实施
1. 核对 `v6gleambl_nomwet_*` 脚本中的方程、样本锁定与输出路径是否都已改成不含 `M_wet`。
2. 顺序执行 `v6gleambl_nomwet_step0_preamble.do` 与 `v6gleambl_nomwet_step1_model8.do`。
3. 校验新结果文件是否生成，并核对规格数、family 列表、结果项中是否不存在 `M_wet`。

## 验证
- 新结果文件为 `temp/2026-04-23_newSMsplit/v6gleambl_nomwet_baseline_coefficients.csv`
- 规格数应为 `88`
- family 应覆盖 11 类 `M_dry` 对应的 7 个 family 名称
- `term` 与 `regressor` 中不应出现 `M_wet`
