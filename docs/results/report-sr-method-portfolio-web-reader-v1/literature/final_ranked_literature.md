# CA_mechanism 相关文献学习排序与导入清单

核验日期：2026-07-14。用户输入中的 `PANS` 按 `PNAS` 处理。

## 1. 结果概况

最终纳入37篇；Crossref、OpenAlex、DOI/出版方路径三重核验通过37/37。2026-07-14写入前Zotero快照有146个顶层条目，其中本清单已存在12篇、缺失25篇；随后25篇完成写入且未重复导入。该计数不是2026-07-18实时查询结果。

这里的“三重核验”首先表示来源存在性、DOI—题名一致性和正式出版方路由已经确认，不表示自动程序读取了 37 个出版社正文页面。自动请求中 36 个出版社页面受到验证码、403 或 redirect 阻断；其题名和摘要信息由 Crossref、OpenAlex、Semantic Scholar，以及 PubMed/PMC、机构存档或 Chrome 精确 DOI 复核补强。rank 1、6、10、24 另有 Chrome 人工强化核验，具体边界见 `phase2_source_verification.md` 与 `chrome_manual_verification.md`。

期刊家族分布：{'Nature': 16, 'Science': 3, 'other': 15, 'PNAS': 3}。类比类型分布：{'direct': 14, 'method': 11, 'structural': 12}。排序规则为 `combined_score = 0.70 × learnability + 0.30 × journal_score`；该分数只服务于本项目的阅读优先级，不表示论文质量的绝对排名。

## 2. 本清单的使用边界

本清单服务于方法学习和后续设计，不代表37篇均已阅读全文，也不表示排序靠前的方法已经在本项目数据中复现。代码与数据获取状态见[37篇代码与数据状态](code_library_status.md)，当前三个实证方向及外部审阅后的解释边界见[GitHub网页端统一入口](../report.md)。

G185固定样本为46,299行、13,236个grids；IE、DE、TE只能称为同期两方程代数组件。旧值1.50%、3.27%、2.56%是控制同期土壤水分后的DE/residual-component contrasts，不是`TE = IE + DE`。方法学习点不得用于把观察性条件关联改写为采纳影响或因果中介。

## 3. 综合排序

### 1. Temperature thresholds of extreme heat-induced yield loss in maize and soybean reveal geographic heterogeneity across the Northern Hemisphere

Quanbo Zhao et al. (2026), *Nature Food*. [DOI](https://doi.org/10.1038/s43016-026-01298-0)；类比：`direct`；可学习度 10.0/10，期刊层级 10.0/10，综合分 10.00/10；Zotero：本次已新导入。

- estimand 定义：使用地区特定阈值以上的 EDD，而不是预设统一阈值。
- 区域异质性：用阈值地图同时呈现空间差异及不确定性。
- 敏感性披露：明确固定阈值如何改变暴露和损失判断。

### 2. More accurate specification of water supply shows its importance for global crop production

Jonathan Proctor et al. (2022), *Nature Food*. [DOI](https://doi.org/10.1038/s43016-022-00592-x)；类比：`direct`；可学习度 10.0/10，期刊层级 10.0/10，综合分 10.00/10；Zotero：已存在，未重复导入。

- 机制边界：把土壤湿度写作与高温共同进入产量函数的状态变量，而不是已识别中介。
- 识别与推断：利用灌溉组差异检验水分胁迫和高温胁迫的可分离性。
- 图表表达：联合展示 temperature–soil-moisture surface 和 irrigation-modified slopes。

### 3. Stronger temperature–moisture couplings exacerbate the impact of climate warming on global crop yields

Corey Lesk et al. (2021), *Nature Food*. [DOI](https://doi.org/10.1038/s43016-021-00341-6)；类比：`direct`；可学习度 10.0/10，期刊层级 10.0/10，综合分 10.00/10；Zotero：已存在，未重复导入。

- estimand 定义：把 temperature–moisture coupling 作为 heat slope 的修饰项。
- 区域异质性：把方向差异和模型不确定性写入主结论。
- 禁用措辞修正：不把统计耦合直接写成机制识别。

### 4. Greater Sensitivity to Drought Accompanies Maize Yield Increase in the U.S. Midwest

David B. Lobell et al. (2014), *Science*. [DOI](https://doi.org/10.1126/science.1251423)；类比：`direct`；可学习度 10.0/10，期刊层级 10.0/10，综合分 10.00/10；Zotero：已存在，未重复导入。

- 论点构造：平均产量提高不等于气候损害斜率下降。
- estimand 定义：直接估计 stress sensitivity，而不是用极端年均值差替代。
- 禁用措辞修正：以观察性边界解释 agronomic trend。

### 5. Compound heat and moisture extreme impacts on global crop yields under climate change

Corey Lesk et al. (2022), *Nature Reviews Earth & Environment*. [DOI](https://doi.org/10.1038/s43017-022-00368-8)；类比：`direct`；可学习度 10.0/10，期刊层级 10.0/10，综合分 10.00/10；Zotero：已存在，未重复导入。

- 论点构造：组织胁迫表面、管理修饰和水分边界三层叙述。
- 复合胁迫度量：区分共同发生、物理耦合和生理相互作用。
- 禁用措辞修正：避免把所有复合胁迫写成协同增损。

### 6. Adaptation to temperature extremes in Chinese agriculture, 1981 to 2010

Di Wang et al. (2024), *Journal of Development Economics*. [DOI](https://doi.org/10.1016/j.jdeveco.2023.103196)；类比：`direct`；可学习度 9.8/10，期刊层级 9.6/10，综合分 9.74/10；Zotero：本次已新导入。

- 将 management × hazard 系数解释为损害斜率的条件差异，并报告从低到高管理水平的边际损害曲线。
- 借鉴省份×年份固定效应与县级趋势对时间变动混杂的处理。
- 将灌溉作为外部边界机制，用于校准秸秆还田的关联性措辞。

### 7. Cultivar evolution underpins maize yield sensitivity to adverse climate conditions

Li Zhang et al. (2026), *Nature Communications*. [DOI](https://doi.org/10.1038/s41467-026-71045-3)；类比：`direct`；可学习度 10.0/10，期刊层级 9.0/10，综合分 9.70/10；Zotero：已存在，未重复导入。

- 论点构造：把长期 yield gain 与 climate sensitivity 分开。
- 区域异质性：同一适应过程在中国不同玉米区对应不同主导胁迫。
- 图表表达：按区域并列气候趋势、产量趋势和 sensitivity slope。

### 8. Conservation agriculture improves soil health and sustains crop yields after long-term warming

Jialing Teng et al. (2024), *Nature Communications*. [DOI](https://doi.org/10.1038/s41467-024-53169-6)；类比：`direct`；可学习度 10.0/10，期刊层级 9.0/10，综合分 9.70/10；Zotero：已存在，未重复导入。

- 论点构造：区分残茬覆盖、土壤微气候、土壤健康和产量的证据层级。
- 机制边界：田间实验的过程解释不能直接移植为观察性因果中介。
- 图表表达：管理×增温四组设计适合作为交互图范式。

### 9. Bootstrap inference under cross-sectional dependence

Timothy G. Conley et al. (2023), *Quantitative Economics*. [DOI](https://doi.org/10.3982/qe1626)；类比：`method`；可学习度 9.4/10，期刊层级 9.3/10，综合分 9.37/10；Zotero：本次已新导入。

- 区分 grid-cluster bootstrap 与显式保留空间相关的 wild bootstrap。
- 把空间块或空间核带宽选择列为推断敏感性。
- 当不同空间推断给出不同显著性时，不写成共同验证。

### 10. Heat, drought, and compound events: Thresholds and impacts on crop yield variability

Jakob Bogenreuther et al. (2025), *Agricultural and Forest Meteorology*. [DOI](https://doi.org/10.1016/j.agrformet.2025.110836)；类比：`direct`；可学习度 9.6/10，期刊层级 8.7/10，综合分 9.33/10；Zotero：本次已新导入。

- 将干旱、高温和热旱放入同一阈值框架，保持不同胁迫的比较口径一致。
- 并列绝对阈值与百分位阈值作为敏感性检验。
- 用生育期分窗解释特定区域—胁迫组合中的缓冲差异。

### 11. Estimating the Impact of Drought on Agriculture Using the U.S. Drought Monitor

Yusuke Kuwayama et al. (2019), *American Journal of Agricultural Economics*. [DOI](https://doi.org/10.1093/ajae/aay037)；类比：`method`；可学习度 9.3/10，期刊层级 9.3/10，综合分 9.30/10；Zotero：本次已新导入。

- 将胁迫拆为强度与持续时间，而不是只使用单一复合指数。
- 用联合 Wald 检验判断一组非线性或分级胁迫项的整体信息。
- 讨论更强固定效应与有效胁迫变异、估计精度之间的权衡。

### 12. A general approach to causal mediation analysis

Kosuke Imai et al. (2010), *Psychological Methods*. [DOI](https://doi.org/10.1037/a0020761)；类比：`method`；可学习度 9.3/10，期刊层级 9.3/10，综合分 9.30/10；Zotero：本次已新导入。

- 把现有 IE、DE、TE 明确为拟合方程的代数组件，而非系数乘积自动识别的 natural effects。
- 若主张因果中介，必须单独陈述三组混杂识别假设。
- 当前版本使用 component 或 pathway-consistent pattern，不使用 identified mediation effect。

### 13. The impact of climate change on the productivity of conservation agriculture

Yang Su et al. (2021), *Nature Climate Change*. [DOI](https://doi.org/10.1038/s41558-021-01075-w)；类比：`direct`；可学习度 9.0/10，期刊层级 10.0/10，综合分 9.30/10；Zotero：本次已新导入。

- 区域异质性：以收益概率组织作物、管理组合和气候区差异。
- 机制边界：区分 no tillage 单项与完整管理系统。
- 敏感性披露：不把概率机器学习输出写成因果验证。

### 14. Productivity limits and potentials of the principles of conservation agriculture

Cameron M. Pittelkow et al. (2015), *Nature*. [DOI](https://doi.org/10.1038/nature13809)；类比：`direct`；可学习度 9.0/10，期刊层级 10.0/10，综合分 9.30/10；Zotero：本次已新导入。

- 机制边界：把单项措施与 conservation agriculture 系统组合分开。
- 区域异质性：以 rainfed × aridity × residue/rotation 分层解释条件效应。
- 论点构造：同时报告适应潜力与适用限制。

### 15. Future climate risk from compound events

Jakob Zscheischler et al. (2018), *Nature Climate Change*. [DOI](https://doi.org/10.1038/s41558-018-0156-3)；类比：`structural`；可学习度 9.0/10，期刊层级 10.0/10，综合分 9.30/10；Zotero：本次已新导入。

- 复合胁迫度量：区分 driver、hazard、impact 和联合结构。
- 禁用措辞修正：共同发生不自动等于统计交互或非加性损失。
- 图表表达：extended risk framework 可解释 D×H 与 hot-dry exposure 的区别。

### 16. Nonlinear temperature effects indicate severe damages to U.S. crop yields under climate change

Wolfram Schlenker et al. (2009), *Proceedings of the National Academy of Sciences*. [DOI](https://doi.org/10.1073/pnas.0906865106)；类比：`method`；可学习度 9.0/10，期刊层级 10.0/10，综合分 9.30/10；Zotero：已存在，未重复导入。

- estimand 定义：阈值以上的 marginal damage slope 与平均温度效应不同。
- 敏感性披露：并列多种函数形式和样本外预测表现。
- 识别与推断：时间序列与横截面响应相近不能自动证明无适应。

### 17. The impact of climate extremes and irrigation on US crop yields

T. J. Troy et al. (2015), *Environmental Research Letters*. [DOI](https://doi.org/10.1088/1748-9326/10/5/054013)；类比：`direct`；可学习度 9.5/10，期刊层级 8.8/10，综合分 9.29/10；Zotero：本次已新导入。

- 把缓冲效应画成不同管理水平下的完整损害响应曲线，而不只展示三重交互系数。
- 分别报告阈值移动与损害斜率变缓。
- 借鉴灌溉/雨养对照设计连续灌溉边界图。

### 18. Global vulnerability of crop yields to climate change

Ian Sue Wing et al. (2021), *Journal of Environmental Economics and Management*. [DOI](https://doi.org/10.1016/j.jeem.2021.102462)；类比：`method`；可学习度 9.2/10，期刊层级 9.4/10，综合分 9.26/10；Zotero：本次已新导入。

- 区分当期缓冲与较长期管理调整，避免把截面和时间差异混为同一机制。
- 借鉴网格面板动态响应的表述，并说明短面板对长期适应推断的限制。
- 区分历史观察到的适应边际与未来额外适应。

### 19. GMM estimation with cross sectional dependence

Timothy G. Conley et al. (1999), *Journal of Econometrics*. [DOI](https://doi.org/10.1016/s0304-4076(98)00084-0)；类比：`method`；可学习度 9.1/10，期刊层级 9.6/10，综合分 9.25/10；Zotero：本次已新导入。

- grid_id 聚类允许同一网格跨期相关，但不自动允许不同网格之间的空间相关。
- 报告距离度量、核函数和截断带宽，并把它们视为推断选择。
- 并列 grid-cluster 与 spatial-HAC 或空间 bootstrap 置信区间。

### 20. Changes in rainfed and irrigated crop yield response to climate in the western US

X. Li et al. (2018), *Environmental Research Letters*. [DOI](https://doi.org/10.1088/1748-9326/aac4b1)；类比：`direct`；可学习度 9.4/10，期刊层级 8.8/10，综合分 9.22/10；Zotero：本次已新导入。

- 把边界条件写成缓冲收益随背景资源而变化，避免描述为普遍有效。
- 报告连续灌溉水平下的边际收益区间与置信区间。
- 同时呈现农业收益与水资源代价。

### 21. Interventional Effects for Mediation Analysis with Multiple Mediators

Stijn Vansteelandt et al. (2017), *Epidemiology*. [DOI](https://doi.org/10.1097/ede.0000000000000596)；类比：`method`；可学习度 9.2/10，期刊层级 9.1/10，综合分 9.17/10；Zotero：本次已新导入。

- 当 soil moisture 存在暴露后混杂时，简单放入第二方程不能解决因果中介识别。
- interventional effects 与现有代数组件是不同 estimand，不能仅重命名后等同。
- IE/DE/TE 图注应明确 algebraic two-equation definition 和非因果边界。

### 22. Soil moisture dominates dryness stress on ecosystem production globally

Laibao Liu et al. (2020), *Nature Communications*. [DOI](https://doi.org/10.1038/s41467-020-18631-1)；类比：`structural`；可学习度 9.0/10，期刊层级 9.0/10，综合分 9.00/10；Zotero：已存在，未重复导入。

- 机制边界：soil moisture 与 VPD/temperature 共变会造成难以分离。
- 识别与推断：先处理耦合再讨论相对贡献。
- 区域异质性：semi-arid 区域的状态依赖更强。

### 23. Increasing Transparency Through a Multiverse Analysis

Sara Steegen et al. (2016), *Perspectives on Psychological Science*. [DOI](https://doi.org/10.1177/1745691616658637)；类比：`method`；可学习度 9.0/10，期刊层级 8.9/10，综合分 8.97/10；Zotero：本次已新导入。

- 把 256-scale 搜索和 208 个候选复核呈现为预定义选择维度，而不是只展示 G185。
- 让最终主张由跨合理分支的稳定模式支持，单个优选规格只承担展示作用。
- 把 region-first 选择明确标为 exploratory selection。

### 24. Model Uncertainty and Robustness: A Computational Framework for Multimodel Analysis

Cristobal Young et al. (2017), *Sociological Methods & Research*. [DOI](https://doi.org/10.1177/0049124115610347)；类比：`method`；可学习度 8.9/10，期刊层级 8.7/10，综合分 8.84/10；Zotero：本次已新导入。

- 把 scale、hazard definition、fixed effects、sample rule、clustering 与函数形式编码为规格维度。
- 在规格曲线中同时显示点估计、置信区间和规格特征。
- 把 G185 放在完整估计分布中，并说明选择规则与事后复核。

### 25. Variations in the sensitivity of US maize yield to extreme temperatures by region and growth phase

Ethan E. Butler et al. (2015), *Environmental Research Letters*. [DOI](https://doi.org/10.1088/1748-9326/10/3/034009)；类比：`structural`；可学习度 9.0/10，期刊层级 8.0/10，综合分 8.70/10；Zotero：本次已新导入。

- estimand 定义：区分全季暴露与 growth-phase-specific exposure。
- 区域异质性：避免全国平均温度斜率覆盖区域阈值。
- 图表表达：地区×生育期二维组织可迁移到区域与 hazard columns。

### 26. Temperature increase reduces global yields of major crops in four independent estimates

Chuang Zhao et al. (2017), *Proceedings of the National Academy of Sciences*. [DOI](https://doi.org/10.1073/pnas.1701762114)；类比：`structural`；可学习度 8.0/10，期刊层级 10.0/10，综合分 8.60/10；Zotero：已存在，未重复导入。

- 识别与推断：多方法一致性提高 assessment confidence，但不证明单一机制。
- 敏感性披露：分别报告方法、作物和地区差异。
- 图表表达：用森林图式呈现多方法 slope 和置信区间。

### 27. Future warming increases probability of globally synchronized maize production shocks

Michelle Tigchelaar et al. (2018), *Proceedings of the National Academy of Sciences*. [DOI](https://doi.org/10.1073/pnas.1718031115)；类比：`structural`；可学习度 8.0/10，期刊层级 10.0/10，综合分 8.60/10；Zotero：已存在，未重复导入。

- estimand 定义：区分 slope、mean loss、variance 和 tail probability。
- 图表表达：从局地产量响应转换到高暴露尾部风险时明确每一步。
- 敏感性披露：单列未纳入的 breeding heat tolerance 等适应。

### 28. Influence of extreme weather disasters on global crop production

Corey Lesk et al. (2016), *Nature*. [DOI](https://doi.org/10.1038/nature16467)；类比：`structural`；可学习度 8.0/10，期刊层级 10.0/10，综合分 8.60/10；Zotero：本次已新导入。

- estimand 定义：区分产量率损失与总生产损失。
- 区域异质性：把区域和时期差异作为主结果。
- 图表表达：事件损失、产量和面积三个层级并列。

### 29. Estimating economic damage from climate change in the United States

Solomon Hsiang et al. (2017), *Science*. [DOI](https://doi.org/10.1126/science.aal4369)；类比：`method`；可学习度 8.0/10，期刊层级 10.0/10，综合分 8.60/10；Zotero：本次已新导入。

- estimand 定义：区分经验 damage function、情景输入和最终损害转换。
- 图表表达：同时报告点估计、概率分布和空间不平等。
- 敏感性披露：在聚合前保留空间异质性和情景不确定性。

### 30. Increased probability of hot and dry weather extremes during the growing season threatens global crop yields

Matias Heino et al. (2023), *Scientific Reports*. [DOI](https://doi.org/10.1038/s41598-023-29378-2)；类比：`direct`；可学习度 9.0/10，期刊层级 7.0/10，综合分 8.40/10；Zotero：已存在，未重复导入。

- 复合胁迫度量：使用 same place/same time 的联合极端定义。
- 图表表达：同时展示单一与复合角点及其历史概率变化。
- 敏感性披露：对不稳定的复合结果保留不确定性表述。

### 31. A global meta-analysis of yield stability in organic and conservation agriculture

Samuel Knapp et al. (2018), *Nature Communications*. [DOI](https://doi.org/10.1038/s41467-018-05956-1)；类比：`structural`；可学习度 8.0/10，期刊层级 9.0/10，综合分 8.30/10；Zotero：本次已新导入。

- estimand 定义：平均产量、绝对波动和单位产量相对稳定性不可互换。
- 敏感性披露：解释稳定性结论如何受分母和营养投入影响。
- 机制边界：把 residue retention 与 rotation 作为组合条件。

### 32. Climate variation explains a third of global crop yield variability

Deepak K. Ray et al. (2015), *Nature Communications*. [DOI](https://doi.org/10.1038/ncomms6989)；类比：`structural`；可学习度 8.0/10，期刊层级 9.0/10，综合分 8.30/10；Zotero：已存在，未重复导入。

- 区域异质性：用空间图识别 weather-sensitive breadbaskets。
- 图表表达：把解释度、主导气候因子和不显著区域同图展示。
- 禁用措辞修正：使用 explain/correlate 的观察性语言。

### 33. Global hotspots for the occurrence of compound events

Nina N. Ridder et al. (2020), *Nature Communications*. [DOI](https://doi.org/10.1038/s41467-020-19639-3)；类比：`structural`；可学习度 8.0/10，期刊层级 9.0/10，综合分 8.30/10；Zotero：本次已新导入。

- 复合胁迫度量：联合概率、联合暴露和影响函数必须分开。
- 区域异质性：用 hotspot 识别地区主导 compound pair。
- 禁用措辞修正：不能从 compound exposure 直接推断产量协同损失。

### 34. Global gridded crop models underestimate yield responses to droughts and heatwaves

Stefanie Heinicke et al. (2022), *Environmental Research Letters*. [DOI](https://doi.org/10.1088/1748-9326/ac592e)；类比：`structural`；可学习度 8.0/10，期刊层级 8.0/10，综合分 8.00/10；Zotero：本次已新导入。

- 敏感性披露：模型捕捉方向不等于捕捉损失幅度。
- 识别与推断：把 exposure error 与 response error 分开诊断。
- 禁用措辞修正：模型一致性不能自动提高因果识别。

### 35. Global non-linear effect of temperature on economic production

Marshall Burke et al. (2015), *Nature*. [DOI](https://doi.org/10.1038/nature15725)；类比：`method`；可学习度 7.0/10，期刊层级 10.0/10，综合分 7.90/10；Zotero：本次已新导入。

- 识别与推断：统一曲线与地区异质性之间需要显式检验。
- 图表表达：清楚分层微观非线性到宏观聚合的转换步骤。
- 敏感性披露：适应假设必须单列，不能隐含在未来投影中。

### 36. Agricultural diversification promotes multiple ecosystem services without compromising yield

Giovanni Tamburini et al. (2020), *Science Advances*. [DOI](https://doi.org/10.1126/sciadv.aba1715)；类比：`structural`；可学习度 7.0/10，期刊层级 9.0/10，综合分 7.60/10；Zotero：本次已新导入。

- 论点构造：并列产量、水分调节和土壤功能而不自动推断机制。
- 敏感性披露：主结论同时保留变异和 trade-off。
- 图表表达：以 win–win、trade-off 和 neutral 象限组织多结果证据。

### 37. Closing the yield gap while ensuring water sustainability

Lorenzo Rosa et al. (2018), *Environmental Research Letters*. [DOI](https://doi.org/10.1088/1748-9326/aadeef)；类比：`structural`；可学习度 7.0/10，期刊层级 8.0/10，综合分 7.30/10；Zotero：本次已新导入。

- 机制边界：灌溉支持不是无条件可扩张的控制变量。
- estimand 定义：区分技术潜力、资源可行潜力和实际产量差。
- 图表表达：用空间 mask 呈现边界条件。

## 4. 可复核文件

来源存在性、页面可读性和浏览器补强边界见[来源核验](phase2_source_verification.md)与[浏览器强化核验](chrome_manual_verification.md)；脱敏后的历史写入计数见[Zotero公开审计摘要](zotero_write_verification.md)。原始候选清单、机器JSON和内部item key不进入公开仓库。
