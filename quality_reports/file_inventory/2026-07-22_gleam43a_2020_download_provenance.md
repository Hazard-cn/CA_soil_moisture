# GLEAM 4.3a 2020 下载与校验谱系

## 状态与范围

- 状态：`SUCCESS`
- 范围：GLEAM 4.3a 日度 `SMrz` 与 `SMs`，公历年 2020
- 授权记录：`decision-climate-stress-input-authorization-20260722`
- 开始时间：`2026-07-22T13:18:01+08:00`
- 首条传输日志时间：`2026-07-22T13:18:06+08:00`
- 完成时间：`2026-07-22T13:22:37+08:00`
- 原始机器可读审计：工作站本地保留的同名 `.json`；该 JSON 不进入 Git。本文件是允许跟踪的耐久证据呈现。
- 原始机器可读审计 SHA-256：`D4363F2A71EA0B74023A2BA7DB623B43D7D72A276F6801C82887AA24D521EF6E`

## 官方逻辑来源与远端清单

- 官方网站：`https://www.gleam.eu/`
- 逻辑远端根：`gleam43a:data/v4.3a/daily/2020`
- 已解析后端：SFTP，`aether.ugent.be:2225`
- rclone：`v1.74.4`
- 凭据是否记录：否
- 上游校验和是否可用：否
- 远端原生哈希：无
- 本次 canonical remote listing SHA-256：`AF862B02640999CE43888F981ADE21DC9FFE70911667410A6496CFE5DE7C9B5D`
- 先前完整远端清单：`${GLEAM_ROOT}/_meta/remote_inventory_20260721_014703.json`
- 先前完整远端清单 SHA-256：`229B0B8D8A16B89B5806F27B92153C09C29EA04E1342F807AA41B462387E9FA6`

远端对象：

| 对象 | 字节数 | 远端修改时间 |
|---|---:|---|
| `gleam43a:data/v4.3a/daily/2020/SMrz_2020_GLEAM_v4.3a.nc` | 1,797,037,847 | `2026-05-14T19:07:01+08:00` |
| `gleam43a:data/v4.3a/daily/2020/SMs_2020_GLEAM_v4.3a.nc` | 1,805,992,442 | `2026-05-14T19:05:14+08:00` |

## 实际传输与不可覆盖语义

- 入口：安全 fetcher 加固前，经授权对不存在的新目标目录执行的 rclone 直接传输。
- 目标目录预检：不存在。
- 逻辑目标：`${GLEAM_ROOT}/2020`。
- 覆盖策略：新目录加 `rclone --immutable`；没有替换、移动或删除既有文件。
- 完整性相关参数：`--immutable --transfers 2 --checkers 2 --retries 3 --low-level-retries 10`。
- rclone 退出码：`0`。
- 日志：`${GLEAM_ROOT}/_logs/gleam2020_20260722_131707.log`。
- 日志 SHA-256：`4EFCDCDCDC71A038BBD6C580A689504D8DD7C1CC8DB9A5235482513B1392607A`。
- 传输中观察到两个唯一 `.partial` 对象；最终目录包含两个文件、零个 `.partial`。
- 发布证据：两层均记录 `Multi-thread Copied (new)`。
- 警告：目标文件系统拒绝 sparse-file 标记但传输继续；一次官方 SFTP 连接 unexpected EOF，由既定重试恢复。
- 实际发布语义：rclone 临时 partial 对象发布到新 final 名称，随后立即执行内容校验。

远端未提供 checksum，因此以下本地 SHA-256 是“首次验证下载的本地基线”，不能解释为“与上游发布 checksum 相符”。

## 本地文件与内容合同

| 层 | 逻辑路径 | 字节数 | SHA-256 |
|---|---|---:|---|
| SMrz | `${GLEAM_ROOT}/2020/SMrz_2020_GLEAM_v4.3a.nc` | 1,797,037,847 | `D496E015C04A642A8E5BAEE791C67AD8270894554948C2F5A7ECA8EEEA79F357` |
| SMs | `${GLEAM_ROOT}/2020/SMs_2020_GLEAM_v4.3a.nc` | 1,805,992,442 | `C51FE087151604A5D335953E410931B3F27F133CE40BA2F8FB19EECCF0F9AD71` |

两层共同合同：

- 维度：`time=366, lat=1800, lon=3600`
- 变量维度：`time, lat, lon`
- 数据类型：`float32`
- 单位：`m3.m-3`
- 填充值：`-999.0`
- 时间单位：`days since 1900-01-01`
- 日历：`proleptic_gregorian`
- 时间轴：`2020-01-01` 至 `2020-12-31`，共 366 日
- 产品版本：`4.3a`
- 纬度轴：89.95 至 -89.95，步长 -0.1，共 1800
- 经度轴：-179.95 至 179.95，步长 0.1，共 3600

## 校验与代码证据

- 内容审计：`${GLEAM_ROOT}/_meta/gleam43a_2020_input_audit_20260722_131707.json`
- 内容审计 SHA-256：`B3A8264F92F444DD8CF40B83EE491643ED06051D6AA12A88C6EC3EEA632D6C0F`
- 加固后复验审计：`${GLEAM_ROOT}/_meta/gleam43a_2020_fetch_20260722T053718.236884Z_98396.json`
- 加固后复验审计 SHA-256：`C98C01F80369E88D8027B72947E76070BA33E5683DC8A3016F620CA939F4D458`
- pipeline inventory 已发现 `gleam43a.SMrz.2020` 与 `gleam43a.SMs.2020`。
- 下载时仓库 HEAD：`10a7eba3fbb9860eae0927aaa6566ac93c6f7527`
- validator：`data_build/scripts/python/validate_gleam43a_year_input.py`，schema version 1
- 下载完成复验时 validator 内容 SHA-256：`EADD603FF9F1AC7F43DDAE43CADCF76E854465374CB3946D1DA8B97DBFFD5302`
- 当前安全入口：`data_build/scripts/python/fetch_gleam43a_year.py`
- PowerShell 薄包装：`data_build/scripts/powershell/fetch_gleam43a_year.ps1`
- 历史边界：安全的 attempt→validate→create-only 发布是在本次直接新目标传输后加入；已完成的 NetCDF 文件未被修改。
