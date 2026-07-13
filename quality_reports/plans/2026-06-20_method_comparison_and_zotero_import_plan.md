# 2026-06-20 原方法与新增方法比较及 Zotero 导入计划

## 任务

比较 `quality_reports/2026-06-20_methods_and_model_equations_from_code.md` 中的原方法体系与前两份新增方法建议报告，明确每类方法的优缺点、适配边界和推荐改进方向。同时将本轮找到的新方法文献写入 Zotero，写入前先做本地库检索去重，写入后再验证。

## 输入文件

- 原方法清单：`quality_reports/2026-06-20_methods_and_model_equations_from_code.md`
- 新方法报告：`quality_reports/agent_runs/2026-06-20_method_upgrade_causal_peer_review.md`
- 高影响期刊补充：`quality_reports/agent_runs/2026-06-20_high_impact_journal_method_supplement.md`

## 工作顺序

1. 读取原方法中的 scale selection、FE interaction、TE/IE/DE、region buffer、pooled Wald、irrigation triple、phenology D×H、spec curve、DML 和 bootstrap inference。
2. 将新增方法分为 GRF/causal forest、orthogonal DML/R-learner、sensitivity analysis、panel counterfactual、structural adaptation model、IV/instrumental forest。
3. 按识别增量、同行认可、当前数据适配、实施成本和审稿风险进行逐项比较。
4. 对拟加入 Zotero 的新方法文献做本地检索去重；只导入缺失条目。
5. 生成项目内比较报告，并记录 Zotero 导入清单与验证结果。

## 预期产出

- 方法比较报告：`quality_reports/agent_runs/2026-06-20_method_comparison_original_vs_new.md`
- Zotero 导入文件：`quality_reports/zotero_imports/2026-06-20_method_upgrade_new_methods.bib`
- Zotero 导入验证记录写入比较报告。
