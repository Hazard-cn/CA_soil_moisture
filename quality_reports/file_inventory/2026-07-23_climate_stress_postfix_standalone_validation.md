# 气候胁迫面板 post-fix 独立完整验证证据

## 结论与边界

- 技术 pilot 验证：`PASS`。
- 原 pipeline validate invocation：`FAILED_RESOURCE`；原记录、partial 和缺少 `stages/validate/_SUCCESS.json` 的事实保持不变。
- 正式 validate stage SUCCESS：不存在，本次不补写、不覆盖旧 run。
- full 运行：`NOT_RUN`。
- public result：未发布。

用户于 2026-07-23 明确裁决：旧 validate 因内存实现超过 4 GiB 而失败，但同一冻结 bundle 经修复后的完整 validator 在小内存下通过后，应将技术验证判为成功并直接使用既有工作，不再重跑数据阶段。该决定记录为 `decision-climate-stress-postfix-validation-20260723`。

## 冻结输入 bundle

- producer run-id：`pilot-fullscope-a-exportfix-20260723T112218Z`
- producer commit：`29b4052d34932502a38c890f6359755bbdc5e402`
- run signature：`60b72b191a2ae9cca4eb266e5f73b572a7d0bb200a7acfb97f42f938be2e26e3`
- effective config SHA-256：`a5e2fefc8aa41bcf056806ba91df03106b79a1b7f70c8c15ed2411d554120039`
- source tree SHA-256：`9f35f9b81f458b56328ede3628cc5fedfab15abe9c8cad363bd81c1c7ae6abfb`
- environment SHA-256：`a4d22f8b7a6310f3476be18df05d668877d431c5ed0e93d8cb5a4a7e0e2be783`

验证只读取该 run 下列相对路径，不登记机器绝对路径：

- `stages/aggregate/climate_window_long.parquet`
- `stages/export/bundle/climate_stress_long.parquet`
- `stages/export/bundle/climate_stress_wide.parquet`
- `stages/export/bundle/climate_stress_cube.nc`
- `stages/export/bundle/climate_stress_merge_ready.dta`
- `stages/export/bundle/stata_alias_map.csv`

主要生产哈希如下：

| artifact | SHA-256 |
|---|---|
| long parquet | `a2f1edefcfafb39057b8e5bf8fdee1cd62be0f0f612e868f3aa99b6dae378b3c` |
| wide parquet | `81e4af81553a9b2cd1251096899912dbda6a53dabd88e5d806efc810b7dce82a` |
| wide partitions | `445146778d689afcb76ef5ad57b94c66cc38bfb82ec61fc49ccb4016bd19685a` |
| NetCDF | `d2fa40e33e52f658fa5ddf21e8f805859add5400e515545f1edc82c8ff8fd958` |
| Stata | `a3cd6a21a59634650daf3bea13ee03993d9b3c781e3e86b179e61c872efe5f9d` |
| alias map | `4bf9134fa394edf79652523734cf1085ee069418a4f7c55321595368fef232d9` |
| manifest | `d20aacee57294e34dec17abb0d647279dc5418481d69559c71a1ed6410c6ea0a` |
| material passport | `a98fd0b304378ac2344604b736287de03a2d89e0ae200434dd42f83941a905ab` |
| output contract | `b0304d044f0aff6bff73116189872d87a8b9c899b05063dda30f359a29cea293` |

## validator 与执行口径

- 冻结 validator commit：`bf1a810f017bfd99aaaa317184f4880899882f20`
- 入口：`repo://data_build/scripts/python/climate_stress/validate.py::validate_export_bundle_full`
- 年份：`2010, 2016, 2019`
- 窗口：规范六窗
- tolerance：`1e-6`
- metric batch：`8`
- DTA row batch：`50000`
- spatial row block：`32`
- NetCDF variable chunk cache：每变量 `1,048,576` bytes
- 执行开始：`2026-07-23T14:03:53.097901Z`
- 执行完成：`2026-07-23T14:04:59.729643Z`
- 捕获记录 SHA-256：`fd13fad6b49ecd16a8d6cb384b64ecaf1d1373d6158fc6a90e0da71f1579b2ca`

完整复验运行时使用的 batching 数值路径随后原样进入 `bf1a810f`；该提交另增加 `0 < cache <= 1 MiB` 的硬上限守卫，不改变本次以 1 MiB 参数执行的数值循环。

## 完整比较结果

| format | rows | numeric columns | finite | missing | max absolute difference |
|---|---:|---:|---:|---:|---:|
| long Parquet | 1,800 | 379 | 573,624 | 108,576 | 0 |
| wide Parquet | 300 | 2,274 | 573,624 | 108,576 | 0 |
| NetCDF | 1,800 | 379 | 573,624 | 108,576 | 0 |
| DTA | 300 | 2,274 | 573,624 | 108,576 | 0 |

NetCDF 另完成：

- 379 个 cube 指标；
- 18 个 year-window 分区；
- 48 次按指标批次打开 Dataset；
- 每次最多 8 个指标；
- 379 个变量均设置不超过 1 MiB 的 chunk cache；
- 完整检查 `1,579,402,152` 个非目标格值；
- Windows `GetProcessMemoryInfo` 记录进程生命周期峰值 `203,075,584` bytes；
- stderr 为空；
- 复验时间窗内既有 run 修改文件数为 0。

## 后续处理

本次验证不重算气候数据、不生成新的数据 bundle、不补造 pipeline stage SUCCESS。`pilot-fullscope-a-memoryfix-20260723T144003Z`只完成 assets/grid 后因用户接受上述既有 bundle 的 post-fix 完整验证而停止；该 run 不再 resume，也不作为技术 PASS 的数值来源。full 数据运行仍未开始。
