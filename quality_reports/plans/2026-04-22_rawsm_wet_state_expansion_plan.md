# rawSM 旱湿状态变量扩展实施计划

- 范围：在 `data_build` 的 `v3` 主流水线内，为 6 个 SM source-layer × 6 个窗口补齐 baseline-local、pooled-state、maize-zone-state 三类旱湿状态变量。
- 变量：保留现有 `drydays_*_le_p10/p20`，新增 `wetdays_*_ge_p90/p80`、baseline `dryshare/wetshare/drydeficit/wetexcess`，以及 pooled / maize-zone 两套 state `share` 与 `deficit/excess`。
- 规则：baseline 使用逐格历史 `P10/P20/P80/P90`；state 使用 pooled `P25/P75` 与 maize-zone `P25/P75`。
- 文档：`VARIABLES_v3.md` 在三个 SM section 内强制分成 `baseline-local`、`pooled-state`、`maize-zone-state` 三个子块，并在 notes 中明确三类变量不能默认互为稳健性替代。
- 验证：重跑 `s04a/s04b/s04c -> s08 -> s10 -> gen_data_dictionary`，并检查阈值顺序、份额边界、文档分层、Stata 导出无截断覆盖。
