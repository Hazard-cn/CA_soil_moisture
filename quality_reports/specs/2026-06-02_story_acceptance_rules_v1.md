# 故事可讲性准则(Story-Acceptance Rules)— v1(存档)

> **存档说明:** 这是 ARS 对抗审**之前**的初版。现行版本为 `2026-06-02_story_acceptance_rules.md`(v2)。逐处差异见 `2026-06-02_story_acceptance_rules_v1_to_v2_changes.md`。保留 v1 仅为版本追溯,不作执行依据。

**日期:** 2026-06-02
**适用:** SR × 干旱/高温/复合 → 玉米产量的有调节中介 spec-search(配合 `empirical-spec-search` 技能与计划文档 §8)
**目的:** 给定**一版数据结果**(= 一个 frozen spec:S0 清洗 + `set_id` + 两方程系数 + bootstrap IE/DE/TE + 异质性),用明确 rule 判定它是否**"能讲一个连贯、稳健、可辩护、且 sellable 的故事"**,从而:① 防 spec-chasing 与自欺;② 决定哪条故事/哪版结果可作 headline、哪些降级、哪些拒。

**一句话定义:** 一版结果"能讲故事" ⇔ 它在**预声明门槛**下,让"两方程 → IE/DE/TE 分解 → 异质性"串成**一句不自相矛盾、跨设定稳健、可辩护、有新意**的话。

**原则次序(冲突时上位胜):** 真实性 > 稳健性 > 内部一致性 > 可辩护性 > 卖点。**卖点永不凌驾前四。**

---

## R0. 前置纪律(运行前锁定,不可事后改)

- **R0.1 故事先声明:** 三故事的 gate 在看结果前写死(机器可判)。
- **R0.2 同一矩阵:** 三故事跑同一搜索矩阵;清洗与样本过滤**只按数据质量/理论**,不按系数。
- **R0.3 全程留痕:** passed 与 failed 都记;改估计量就**标新估计量**。
- **R0.4 Baseline 锁死:** headline 数字只来自 `fullnew + S0 + GLEAM 根区(主)`。生物学窗口只做机制下钻,不出 headline 数。

---

## R-A. 内部一致性(两方程 + 异质性 = 一句话)

- **R-A1 两方程不打架:** a-path、b-path、direct(c3)、indirect(IE)的符号能组成一个非矛盾的机制叙述。
- **R-A2 分解自洽:** `TE ≈ IE + DE`,符号与两方程一致。
- **R-A3 异质性强化而非推翻:** 效应在理论预期子组更强、与 baseline 同向;反向 → 不算故事。
- **R-A4 可一句话化:** baseline → 分解 → 异质性能串成一句不绕弯的话。

---

## R-B. 稳健性(区分"稳健故事"与"spec-chased 伪迹")

- **R-B1 跨设定存活:** headline 关系在预声明稳健集里 **≥ 70% 的 legal specs** 保持同向且达显著门槛。
- **R-B2 符号稳定:** 载荷系数不得在 legal 空间里翻号;若翻 → 显式 scope 并降为 *bounded/suggestive*。
- **R-B3 不靠单点:** 不能只在 1 spec / 1 年 / 1 子样本成立。
- **R-B4 方向一致 > 个别星号。**

---

## R-C. 统计推断门槛

- **R-C1 载荷量必 bootstrap:** cluster grid、`xtset,clear`、BC CI、reps ≥500 promote / ≥1000 final。
- **R-C2 Gate 系数达标:** CI 排除 0 / p<门槛。
- **R-C3 异质性须带 CI** 方可下子组断言。

---

## R-D. 可辩护性(给定 T=4 + 观测 + 中介内生)

- **R-D1 关联语言:** 全程 conditional association;禁因果中介话语。
- **R-D2 证伪通过:** effect 断言须 `v3pm10` placebo≈0 且 lead 不显著。
- **R-D3 边界透明:** T=4、观测性采纳、中介内生显式写明。
- **R-D4 允许不对称(诚实不完整可发表)**,但须明说,不假装闭环。

---

## R-E. 卖点(必要但从属)

- **R-E1 有明确新 claim。**
- **R-E2 有现实含义。**
- **R-E3 卖点不得违反 R-A~R-D:** truth 与 sell 冲突时 truth 胜。

---

## R-F. 决策规则(哪版/哪故事胜出)

1. 过 baseline gate(`fullnew+S0`)?否 → 出局。
2. 过 R-B + R-C + R-A + R-D?
3. 判定:全过 → headline;仅窄设定过 → suggestive/SI;多故事都过 → 选最稳那条;无一干净过 → 报诚实不完整子集。
- 先验预期:A/C 大概率过;B 的 c3 buffering 多半翻号 → 降 suggestive。

---

## R-G. 一页 checklist(每版结果填一行)

set_id | baseline gate | 稳健存活% | 符号是否翻 | TE≈IE+DE | 异质性同向 | 可一句话 | bootstrap | het 带 CI | placebo+lead | 关联语言 | 卖点 | 判定(headline/suggestive/reject)

---

## 附:三故事的故事句模板(过准则后填实)

- **A(共同通道):** "三胁迫都先压低土壤水(`a1`<0)、土壤水助产量(`b`>0);热几乎全程经土壤水。"
- **C(类型学):** "三胁迫作用部位不同——热≈经土壤水、旱≈直接+间接、复合≈直接为主;据此差异化适应。"
- **B(还田缓冲,需先过 R-B2/R-D2):** "在[scope]下,还田更高处旱/热减产更缓,且部分经维持土壤水。"——若翻号或仅单点,不可作 headline。
