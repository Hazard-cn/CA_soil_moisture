# 热干事件方向公开STOP报告审查

- 审查对象：`quality_reports/plans/2026-07-15_hotdry_event_smoke_stop_public_draft.md`
- 独立审查结论：`PASS_PUBLIC_STOP_REPORT`
- 评分：97/100
- Critical：0
- 未解决Major：0
- 底层方向状态：`STOP_AT_SMOKE_REVIEW`；不得解除两轮审查上限。

## 核验结果

v2登记的23项inputs共3,602,818,190 bytes，逐项bytes、MD5和SHA-256全部匹配；7项v2 outputs全部匹配；机器STOP摘要登记的12项artifact SHA-256全部匹配。未登记的runner测试文件为1,219 bytes、MD5 `6b1ab85d4261ecc5c9919f92d200604b`、SHA-256 `fe9616abd196e09d7ae8aee3fa9e15a2cc945383071aeb8e8e1301e1f97e3b55`。v2 `run_manifest.json` SHA-256 `724589d62bbadf0cc5b44e0a3c77f921308cd6ccec686d88668df871ea2a18b4`，extension SHA-256 `741578cbf7abd100da61622619ff213f49dd1a1626566bd1b00ef6e8749b6f0d`，均与公开稿一致。

41项测试复跑通过。v1/v2解压CSV完全一致，均为75×37、40个grid-years、54个事件行；grid-year support、400条coordinate审计和stage decision逐字节一致。两个Stage 1终止记录分别为1,814秒和54秒，均为`support_audit_completed=false`。

首轮指出的窗口含义Major已修订：公开稿现在明确`v3_doy-30`至`ma_doy`是扩展V3—成熟窗口，不是严格播种至成熟的完整生育季。修订稿区分冻结设计与已执行接口、全量支持未完成与不显著、接口自检PASS与独立审查STOP，并遵守两轮上限。

## 评分

| 维度 | 得分 |
|---|---:|
| 创新与期刊匹配 | 19/20 |
| 数据和五区支持 | 20/20 |
| estimand与识别边界 | 20/20 |
| SM构念及时序 | 15/15 |
| 精度与稳定性 | 14/15 |
| 可复现性和图表完整性 | 9/10 |
| **合计** | **97/100** |

本评分评价公开失败报告质量，不改变底层small smoke审查89/100和方向STOP状态。
