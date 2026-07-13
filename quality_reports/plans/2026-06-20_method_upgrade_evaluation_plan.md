# Method upgrade evaluation plan

## Goal

评估 `quality_reports/agent_runs/2026-06-20_method_comparison_original_vs_new.md` 中对 `TE/IE/DE` 的新增操作、`damage-avoidance margin` 改写，以及新增 machine-learning / causal-ML 方法是否适合作为当前论文方法升级。

## Scope

1. 读取 ARS reviewer workflow、methodology reviewer、devil's advocate、editorial synthesizer 和统计报告标准。
2. 读取用户指定的 method comparison 报告。
3. 使用 Zotero 本地库核验报告中列出的核心方法文献是否存在，并提取可用于判断的题名、item key、citation key 或 DOI。
4. 对以下问题做评估：
   - `IE/DE/TE` 是否应保留、改名、降级或替换；
   - `damage-avoidance margin / yield-loss buffering margin` 是否适合进入主文；
   - GRF / causal forest / R-learner / orthogonal DML 是否适合作为主方法、稳健性还是附录；
   - Oster / Cinelli-Hazlett sensitivity 是否应补；
   - 是否存在目标期刊子刊审稿风险。
5. 输出评估报告和简短结论。

## Deliverable

写入 `quality_reports/agent_runs/2026-06-20_method_upgrade_evaluation.md`，并在对话中给出排序后的建议。

