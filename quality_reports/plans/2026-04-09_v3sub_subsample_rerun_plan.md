# V3 子样本重跑方案：灌溉分组 + 玉米产区分组

## Summary

- 数据入口固定为 `data/processed/v3_analysis_ready.dta`
- 子样本维度固定为 `maize_zone` 六组与 `irr_frac` 中位数二分
- 实现四个模块：
  - 结构一：`Yield ~ SR + D + H`
  - 结构二：`Yield ~ SR + D + H + SM`
  - 结构三：`SM ~ SR + D + H`
  - `Step 2` 窗口与 horse-race
- 全部子样本回归不放 `W` 或 `SR×W`
- 不进入 formal mediation，不生成新的 beamer 报告

## Key Changes

- 新建 `v3sub_*` 前缀脚本与输出，避免覆盖现有 `v3_*`
- 统一预处理脚本负责生成 `maize_zone`、`irr_group` 与诊断表
- 结构一和结构二使用 full-season
- 结构三与 `Step 2` 保留窗口维度
- 输出统一为长表，字段按 `split_type / subgroup / spec / sm_src / window / scheme` 组织

## Test Plan

- 校验 `maize_zone` 与 `v3_step8_heterogeneity.do` 完全一致
- 校验 `irr_group` 阈值来自 `main_sample == 1` 的 `irr_frac` 中位数
- 校验所有子样本模型 RHS 不含 `W_*` 或 `SR_x_W_*`
- 校验 2 个灌溉组和 6 个产区组的四个模块均成功导出结果或明确写入失败记录
- 校验 FE、cluster 与 seed 纪律不变

## Assumptions

- 用户提到的 `R` 按当前项目变量解释为 drought 项 `D`
- `Step 2` 只服务于结构一，不给结构二和结构三追加 horse-race
- 控制变量继续沿用当前 `v3` 控制宏
