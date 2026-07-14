# 地区异质温度阈值方向：Stage 1 STOP审计

## 审计结论

- Canonical ID：`regional-threshold-sr-v1`
- Gate：`STOP`
- 后续禁止：smoke test、内部阈值CV、逐小时全量暴露、完整模型和结果筛选。
- 原因：确认性规格预先冻结的“五个产区分别达到80%有效外生阈值覆盖”没有满足；SW为12,637/18,094=69.8408%。

停止依据是数据支持硬门槛，不是估计结果。不得通过双线性插值、删除云南、调整产区定义、固定32°C回填缺失像元或更换分母补救。

## 三层来源核验

Nature Food正式页面将阈值数据指向Zenodo DOI `10.5281/zenodo.17142122`；Zenodo v2记录给出0.5°分辨率、文件名和MD5；用户提供的本地附件 `maize.tif`（记为 `external://user-supplied/maize.tif`）的328,745 bytes与MD5 `0d9e6c21bf1b25f113e14315863372f2`完全一致，SHA-256为 `f05e634664c4c6c2e2df352702acd421507162bc54cc067649071521ab1285b0`。GeoTIFF为EPSG:4326、PixelIsArea、514×76、float32，有效单元5,627/39,064，有效阈值范围26.8—44.0°C。

Zotero本地条目为 `262BTEKM`。Figshare官方代码包为 `10.6084/m9.figshare.27238629.v3`；代码包共37个文件，其中只有 `CalExposure.m` 和制图notebook两个代码候选文件。notebook读取预先计算的Excel结果制图，未发现阈值估计流程，因此公开包没有可用于复刻阈值估计的程序。

覆盖门槛由用户在实施任务 `019f60e3-a5a6-7f83-af78-26ac04e7cac2` 中于2026-07-14明确批准，相关消息先于覆盖率计算；本地实施计划为 `quality_reports/plans/2026-07-14_sr_method_portfolio_implementation.md`。该计划在执行期间继续补充技术细节，当前文件SHA-256为 `694ccc749c85a7b48582d78ccf16dc33e640c2d943f7e96147a1dbd6ed6e28e2`，只标识当前文件，不能单独证明时间先后；项目中不存在可验证的计算前文件快照。本记录因此只称“有任务批准记录的预先冻结门槛”，不称为外部注册平台上的正式预注册。

## 确认性映射和覆盖

栅格边界 `west=-122.93843501676258`、`north=56.38937358482315`。0.1°项目格网中心到0.5°原始单元的确认性映射为：

\[
col=\lfloor(lon-west)/0.5\rfloor,\qquad
row=\lfloor(north-lat)/0.5\rfloor.
\]

不得先取整经纬度、使用最近中心、插值或外推。映射输出字段应为 `source_row`、`source_col`、`source_pixel_id=row*514+col`、原始阈值、coverage flag和映射方法；`source_row`和`source_col`均为零基索引。

| 产区 | 总行数 | 有效阈值行 | 行覆盖率 | 总grids | 有效grids |
|---|---:|---:|---:|---:|---:|
| NE | 25,041 | 23,723 | 94.7366% | 7,365 | 6,967 |
| HHH | 13,165 | 12,922 | 98.1542% | 3,844 | 3,775 |
| NW | 5,540 | 4,681 | 84.4946% | 2,228 | 1,849 |
| SH | 4,556 | 4,501 | 98.7928% | 1,692 | 1,668 |
| SW | 18,094 | 12,637 | **69.8408%** | 6,208 | 4,487 |

SW内部：云南35.5549%、贵州80.5942%、四川84.6172%、广西99.4704%、重庆100%。pre-EDD complete-case谓词固定为五个命名产区且 `ln_yield`、`ca`、`gdd_10_29`、`pr_sum`、`v3_doy`、`he_doy`、`ma_doy` 和 `gleam_smrz_mean` 非缺失；这些字段在五区没有缺失，故SW分母仍为18,094，不能靠complete-case顺序提高覆盖。`irr_frac`在SW缺4,219行、`crc_lag1`缺2,577行，但二者不是该覆盖门槛的预设主控制，不能用于改变门槛分母。

V3规范输入为本地数据资产 `data-v3-expanded-main-dta`，逻辑定位为 `repo://data_build/data/processed/data_v3_main.dta`，SHA-256为 `3f3f045a8040b876565873febab3918d166b8bd6f6938669b48c634a46172517`。五区赋值依据 `scripts/stata/v3sub_step0_subsamples.do` 第18行起的省份规则。机器复算入口为 `scripts/python/audit_regional_threshold_coverage.py`，最终机器可读输出为 `temp/2026-07-14_regional_threshold_stage1_audit_v5/threshold_coverage_by_zone.csv`、`threshold_grid.csv`、`threshold_grid.jsonl`、`run_manifest.json` 和扩展审计manifest；`threshold_grid.jsonl`逐行执行 `docs/contracts/threshold_grid.schema.json` Draft 2020-12校验，扩展manifest登记全部输出哈希。共同manifest的 `git_commit` 记录运行时工作树基线，因执行文件尚未提交，manifest的 `inputs` 另行冻结执行脚本和两个schema的路径、字节数、MD5与SHA-256；代码身份以这些直接哈希为准。脚本只读取输入并复算覆盖，不估计任何产量模型。`audit_v1`因JSONL缺失值序列化检查失败而保留为不完整历史运行，`audit_v2`完成覆盖复算但遗漏共同 `run_manifest` 契约，`audit_v3`补齐共同契约但其栅格schema尚未强制无效像元索引语义，`audit_v4`修复schema但没有在manifest冻结未提交执行代码；四者均未被覆盖，也不得作为最终证据。

常见GIS缺失值处理会改变门槛结果：对NoData重归一化的双线性插值可把SW覆盖提高到81.6901%，3×3邻域最近有效像元回填可提高到90.2343%。这两种结果都以估算值替代官方NoData，不再是预设的“格网中心所在原始像元”确认性暴露，故只作为映射敏感性披露，不能用于通过80%门槛。最近原始像元中心映射与所在单元赋值相同，仍为69.8408%；把PixelIsArea误读为PixelIsPoint也只有71.6757%。

## 算法和命名边界

`CalExposure.m` 可精确复现的是逐小时阈值暴露计数：

\[
H_{itw}=\sum_{h\in w}1(T_{ith}\ge\tau_i),\quad
ExposureDays_{itw}=H_{itw}/24,\quad
ExposureFraction_{itw}=H_{itw}/N_{total,itw},\qquad N_{total,itw}=m\times n.
\]

这里的分母严格沿用 `CalExposure.m` 的 `m*n`，即输入窗口中的全部网格—小时位置数。本项目若未来运行暴露算法，将另外断言每个grid-window具有完整24小时记录；只有该新增完整窗口断言成立时，`N_valid=N_total`。

若以后经用户明确修改覆盖门槛，确认性实现应使用 `external://ERA5/ERA{year}.nc` 逐小时 `t2m`，K减273.15，严格 `>=`，窗口从开始日00:00至结束日23:00，要求完整24小时；`sum(max(T_h-tau_i,0))/24`只能另称 `threshold_hdd_cday` 敏感性。主文应称“地区阈值特定的极端高温暴露天数”，不能把公开代码未实现的温度超额积分称为直接复刻EDD。

当前项目“full”实际为 `V3-30日至MA`，正式名称应为“扩展V3—成熟窗口”，不能写成严格播种至成熟。物候次级窗口应为不重叠的 `V3<=d<HE` 与 `HE<=d<=MA`。

## 若未来重新授权时仍需遵守的边界

外生阈值没有像元级不确定性层，不能声称传播其估计误差。内部候选28—40°C只是有限敏感性，不覆盖官方26.8—44.0°C范围。LOYO预测不能使用留出年份不可估计的province×year FE。GLEAM antecedent与窗口内通道必须分开；同期SM不能加入产量方程后解释为因果中介。

## Critical与Major

Critical：SW覆盖69.8408%低于80%；栅格缺失与原研究能否识别阈值/是否经历高温暴露有关，不能当作普通随机缺失；任何插值、云南排除、固定阈值回填或产区重定义都会改变确认性暴露。

Major：公开代码没有阈值估计程序；EDD与ExposureDays必须分开；当前full窗口名称需纠正；外生阈值误差无法传播；内部候选范围比外生阈值窄；LOYO与province×year FE不可共用同一预测规格。

## 交付规则

本方向只交付数据支持表、来源与算法核验、STOP依据和未来重新授权边界。不存在主模型、显著或非显著系数；不得写成“阈值结果不显著”或暗示已估计SR缓冲效应。
