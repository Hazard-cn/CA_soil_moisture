# 故事可讲性准则(Story-Acceptance Rules)v2

**日期:** 2026-06-02 ｜ **版本:** v2(经 ARS 多轮对抗审升级;v1 见文末 changelog)
**适用:** SR × 干旱/高温/复合 → 玉米产量的有调节中介 spec-search(配合 `empirical-spec-search` 技能与计划 §8)
**目标刊标尺:** Nature Food(主)/ Communications Earth & Environment(保底)
**目的:** 给定**任意一版数据结果**,用一套**可机械执行、不可游戏化、外部锚定**的规则,判定它是 `headline / suggestive(bounded) / exploratory-only / reject / no-story`,从而既挑出能讲的故事,又杜绝 spec-chasing 与自欺。

---

## 0. 关键定义(先把"一版结果"说清楚)

- **一个 spec(set)** = 一个 frozen 组合 `sample+transform+mediator+depth+fe+weight`(+window),产出两方程系数 + bootstrap IE/DE/TE + 异质性。
- **铁律 D0:单个 spec 永远不单独构成"故事"。** "故事" = **预声明的主设定(primary spec)** + **整个多元宇宙的模式** + **通过确认性检验**。任何只引用单个 spec 的"结果"一律视为探索性。
- **原则次序(冲突时上位胜):** 测量可信 > 真实性 > 稳健性 > 内部一致 > 可辩护 > 贡献/卖点。

---

## 1. 元规则(一套"优秀规则"自身的标准)

- **M1 可操作:** 每条 rule 给出可机械判定的 pass/fail(阈值、统计量、log 字段)。
- **M2 不可游戏化:** 凡分析者能自由选择的自由度(baseline、legal set、scope),都必须**外部锚定 + 运行前冻结**(见 §3、§6)。
- **M3 外部锚定:** "对/不对"的判据尽量来自数据外部(生物学、文献、预声明),而非"哪个结果好看"。
- **M4 明确裁决:** 对每版产出一个确定标签 + 机械理由(见 §7)。

---

## 2. 前置门(Preconditions;不过门 → 结果不进入评价)

- **P1 产量出处非循环:** 产量数据集(来自 Scientific Data/ESSD)其构造**不得以 SM/气候为预测因子**;Methods 点名数据集与降尺度方法。若用气候协变量训练 → 该结果不可用于 SM/气候自变量(循环)。
- **P2 处理构念披露:** `ca_ratio` = grid 内还田采纳份额(处理强度);正文显式声明 "share ≠ 秸秆生物量",并讨论其作为代理的局限。
- **P3 清洗冻结:** 结果须建立在冻结的 S0(计划 §8.2b)之上,附 `cleaning_log.csv` waterfall;清洗规则按质量/理论,非系数。
- 任一前置门不过 → **reject(技术性)**,不进入 R-A~R-E。

---

## 3. 预声明与冻结(Pre-registration;运行前提交,带时间戳/hash 入 log)

- **PR1 Gate 先写死:** A/C/B 三故事的 gate(计划 §8.2,含 buffering 方向、p/CI 门槛)在**看结果前**提交。
- **PR2 Legal spec 全集先锁:** 明确列出 spec 全集(每维取值),**分母固定**;事后**不得增删** legal set(要加 → 作新批次显式记录)。
- **PR3 Baseline 的外部理由先写:** primary spec(`fullnew + S0 + GLEAM 根区`)的选择理由必须是**外部的**(气候-产量面板标准口径 + `sm_state_audit` 已证其阈值稳健),且在出结果前写明——**禁止"因为这里好看所以选它"**。
- PR1–PR3 的提交快照(文本 + 时间)存入 `output/logs/spec_search_*/prereg.md`。

---

## 4. 探索 vs 确认分离(防"同数据既搜又证")

- **S1 搜索=探索:** §8 的多元宇宙是**探索性**;其产出的任何 gate-pass 都只是"候选故事"。
- **S2 准确认检验:** 候选故事选定后,必须在**留出片**复算并保持结论:**leave-one-year-out(4 折)** 与 **leave-one-region-out(产区折)**。
  - 通过 = 结论(符号 + 达门槛)在**全部折**不翻、且效应量同量级。
  - 仅探索集成立、留出片翻 → 至多 *exploratory-only*,不得 headline。
- **S3 诚实标注:** T=4 限制真正的样本外确认;留出检验是**准确认**,文中如实表述。

---

## 5. 准则组(每版结果逐条判)

### R-A 机制可信 + 内部一致
- **R-A1(物理符号硬门):** a-path 符号须合域先验(hazard→SM **必须<0**);`b`(SM→产量)符号物理合理;若出现反常(如 hema `b<0`)→ **必须有独立机制解释**(涝/寡照…)且非"为符号改口径",否则该窗口结果不可用。
- **R-A2 分解自洽:** `TE ≈ IE + DE`,三者符号与两方程一致。
- **R-A3 异质性同向强化:** 效应在理论预期子组(雨养/易旱/敏感期)更强且与 baseline 同向;反向 → 不算一个故事。
- **R-A4 一句话:** baseline→分解→异质性能串成一句不矛盾的话。

### R-B 多元宇宙稳健(防 spec-chasing 核心;分母已由 PR2 锁定)
- **R-B1 汇总统计(报全集,不挑):** 在锁定的 spec 全集上报 ① median 效应、② %同号、③ %达显著门槛、④ **sign-consistency index**(同号占比);预设通过线:**同号 ≥ 80% 且 显著占比 ≥ 50%**(可在 PR 阶段调,但先定后跑)。
- **R-B2 核心 spec 不翻号:** 载荷系数(`c3` 或 IE)在**预声明的 core 子集**(主样本×主中介×两 FE×两土层)内**不翻号**;翻 → 见 §6 bounded 规则。
- **R-B3 不靠单点:** 不得仅 1 spec / 1 年 / 1 子样本成立;leave-one-out(年/区)任一折翻 → 不达 R-B。
- **R-B4 具区分度:** 计入稳健的 specs 必须**彼此实质不同**(不能用近乎相同的 spec 灌"高存活率")。
- **R-B5 多重比较意识:** 跨 hazard×组的显著点用方向一致性解读,不堆星号;必要时报 specs 的显著占比 vs 零假设期望。

### R-C 推断 + 效应量
- **R-C1 载荷量必 bootstrap:** cluster(`grid_id`)、`xtset,clear` 先行、BC 百分位 CI、reps ≥1000(final)。
- **R-C2 Gate 达标:** CI 排除 0 / p<预设门槛。
- **R-C3 异质性带 CI** 方可下子组断言。
- **R-C4 经济显著性门:** 不止统计显著——效应量须达**实质量级**(预声明一个最小有意义效应,如对产量的 %影响),否则即便显著也只作 "precisely-estimated null/small"。

### R-D 可辩护(给定 T=4 + 观测 + 中介内生)
- **R-D1 关联语言:** 全程 conditional association;禁因果中介/buffering 因果动词/Sobel。
- **R-D2 证伪通过:** 任何 effect 断言须 `v3pm10` placebo≈0 且 lead(`SR_f1×hazard`)不显著。
- **R-D3 边界透明:** T=4、观测性采纳、SR 选择性内生、中介内生,显式写明。
- **R-D4 允许诚实不完整:** "强 a-path + 弱 closure + 清晰边界" 是合法故事,但须明说不对称、不假装闭环。

### R-E 贡献/外推(子刊门)
- **R-E1 新 claim:** 现象/机制/类型学/可操作措施至少一项新。
- **R-E2 外部有效性:** 给出对中国 2016–2019 之外的可外推性论证(或明确限定)。
- **R-E3 可证伪:** 该 claim 必须是"本可能被数据推翻"的(若任何结果都能讲成它,则不是 claim)。
- **R-E4 "so what" 门:** 退化成教科书结论(如"胁迫降 SM、SM 助产量")不足以单独 headline。
- **R-E5 卖点从属:** 与 R-A~R-D 冲突时,truth 胜。

---

## 6. 反游戏化守则(anti-gaming;DA 重点)

- **G1 baseline/scope 外部锚定:** primary spec 与任何 bounded scope 的选择理由必须外部(生物学/文献/预声明),且 PR 阶段冻结;**禁动机化选择**。
- **G2 bounded-claim 合法性(翻号才用):** 当载荷只在子区域成立,可作 *bounded/suggestive* 当且仅当同时满足:① 该 scope 有**独立 a-priori 理由**(非"这里显著");② 存在**该 scope 能预测的 placebo/对照**并通过;③ 全集统计(R-B1)仍如实呈现。否则 = HARKing → reject 该 claim。
- **G3 legal set 不可事后改:** 见 PR2;新增 spec 永远作显式新批次,旧批次结果不被悄悄替换。
- **G4 failed 全留痕:** `failed_sets.csv` 完整;任何"调整后才成立"必有 before/after 记录。
- **G5 改估计量标新估计量:** 口径变了(加权/样本/中介定义)就视作新估计量,不冒充同一结果。

---

## 7. 裁决(每版结果 → 一个标签 + 机械理由)

按序判:
1. 过前置门 §2?否 → **reject(技术)**。
2. PR/分离齐备(§3、§4)?否 → 至多 **exploratory-only**。
3. 逐条 R-A~R-E + §6:
   - **headline:** 过 P+PR+S2(留出确认)+ R-A + R-B(全集统计达线且核心不翻)+ R-C(含效应量)+ R-D + R-E。
   - **suggestive(bounded):** 仅在 scope 内成立,且满足 G2 三条;全集统计如实报;不作无限定主张。
   - **exploratory-only:** 探索集成立但留出片翻 / 未过 R-B3。
   - **reject:** 违反前置门、R-A1 物理符号、R-D1 语言、或 G2/G3(HARKing)。
   - **no-story(合法结论):** 若无任何故事达 headline,且稳健核仅支持有限论断 → 按 R-D4 报"诚实不完整"的稳健子集并**明确宣布不强行成篇**(防 spec-chasing 的终点)。
- **先验预期:** A/C 趋向 headline;**B 多半触发 R-B2 翻号 → 走 G2 检验,过则 suggestive(bounded)、不过则 reject 该 claim**。

---

## 8. 一页 Scorecard(每版填一行)

| 字段 | 取值 |
|---|---|
| set_id | sample+transform+mediator+depth+fe+weight(+window) |
| 前置门 P1/P2/P3 | pass / fail(注明) |
| PR1-3 冻结 | 是(prereg.md hash) / 否 |
| 留出确认 S2(年/区) | 全过 / 部分翻(注明) |
| R-A1 物理符号 | 合规 / 反常(解释:__) |
| TE≈IE+DE | 是 / 否 |
| 异质性同向 R-A3 | 同向 / 反向 |
| R-B1 全集:median/%同号/%显著 | __ / __% / __% |
| R-B2 核心翻号 | 否 / 是→scope=__ |
| R-B3 单点/留出 | 稳 / 靠单点 |
| R-C bootstrap+效应量 | reps=__,BC;效应量=__(过/不过门) |
| R-D1 语言 / R-D2 证伪 | 合规·通过 / 违规·失败 |
| R-E 新claim/外推/so-what | __ |
| G2 bounded 合法性(如适用) | a-priori 理由=__;scope-placebo=过/否 |
| **裁决** | **headline / suggestive(bounded) / exploratory-only / reject / no-story** |

---

## Changelog
- **v2(2026-06-02,经 ARS 对抗审):** 新增 §2 前置门、§3 预声明冻结、§4 探索-确认分离、R-A1 物理符号硬门、R-B1 多元宇宙汇总统计(固定分母)+R-B4 区分度+R-B5 多重比较、R-C4 效应量门、R-E2/E3/E4 外推·可证伪·so-what、§6 反游戏化(baseline/scope 外部锚定、bounded-claim 合法性三条件)、§7 明确 no-story 裁决、§8 升级 scorecard。
- **v1:** R0/R-A~R-G 初版(结构正确但 baseline/scope 可游戏化、缺效应量/探索-确认分离/物理符号门/前置门)。
