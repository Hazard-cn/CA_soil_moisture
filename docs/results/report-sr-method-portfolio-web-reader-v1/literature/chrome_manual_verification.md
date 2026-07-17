# Chrome 人工强化核验记录

核验日期：2026-07-14。本文件用于补充出版方对脚本请求返回验证码、403或简化题名时的人工复核，不替代Crossref与OpenAlex的机器检查；浏览器会话名称和原始机器记录不进入公开材料。

## 1. Nature Food 最高优先级条目

- DOI：`10.1038/s43016-026-01298-0`。
- Chrome 直接打开 Nature Food 正式页面 `https://www.nature.com/articles/s43016-026-01298-0`。
- 页面显示题名 *Temperature thresholds of extreme heat-induced yield loss in maize and soybean reveal geographic heterogeneity across the Northern Hemisphere*、2026-02-18、*Nature Food* 7:194–205、22 位作者，并提供摘要。摘要说明研究使用北半球次国家产量资料估计玉米和大豆的地区特定 EDD 临界阈值及其空间变异，支持“地区特定热阈值、阈值地图和固定阈值敏感性”三个学习点。
- 判定：题名、期刊、年份、卷页、作者和学习点均由正式期刊页面确认。

## 2. 中国农业温度适应条目

- DOI：`10.1016/j.jdeveco.2023.103196`。
- Chrome 在 Google Scholar 中以完整 DOI 精确检索，结果唯一对应 *Adaptation to temperature extremes in Chinese agriculture, 1981 to 2010*，作者 D. Wang、P. Zhang、S. Chen、N. Zhang，*Journal of Development Economics*，2024；结果链接到 Elsevier 正式页面。
- Scholar 摘要明确列出时期特定 panel fixed effects、灌溉扩张自然实验、投入边际适应和约 40% 的总体适应解释比例，支持当前稿对 damage-slope modifier、灌溉边界和识别措辞的学习点。
- 判定：题名、作者、期刊、年份和摘要内容由 DOI 精确 Scholar 结果强化确认。

## 3. 复合热旱阈值条目

- DOI：`10.1016/j.agrformet.2025.110836`。
- Chrome 在 Google Scholar 中以完整 DOI 精确检索，结果唯一对应 *Heat, drought, and compound events: Thresholds and impacts on crop yield variability*，作者 J. Bogenreuther、C. Bogner、S. Siebert、T. Koellner，*Agricultural and Forest Meteorology*，2025；结果链接到 Elsevier 正式页面。
- Scholar 摘要明确比较相对与绝对阈值、玉米与冬小麦、营养生长与生殖生长阶段，并指出复合事件对籽粒玉米的影响强于单一事件，支持阈值统一、生育期分窗和复合事件对照三个学习点。
- 判定：题名、作者、期刊、年份和摘要内容由 DOI 精确 Scholar 结果强化确认。

## 4. SAGE 题名副标题异常条目

- DOI：`10.1177/0049124115610347`。
- Crossref 与 OpenAlex 只返回短题名 *Model Uncertainty and Robustness*；Chrome 在 Google Scholar 中以完整 DOI 精确检索，结果显示完整正式题名 *Model uncertainty and robustness: A computational framework for multimodel analysis*，作者 C. Young、K. Holsteen，*Sociological Methods & Research*，2017，并链接到 SAGE 正式 DOI 页面。
- Scholar 摘要明确说明跨控制变量、函数形式、变量定义、标准误计算和估计命令的 computational multimodel analysis，与本项目的 specification-search transparency 用途一致。
- 判定：副标题并非误配；短题名来自 Crossref/OpenAlex 元数据简化，完整题名由 DOI 精确 Scholar 结果确认。

## 5. 核验边界

内部机器记录中的出版方路径通过只表示DOI或正式URL到达已知出版方域名；验证码页和403被保留为“出版方路径存在但自动化读取受阻”，不表示脚本已读取官网摘要。最终内容学习点以候选检索记录中的官方页或权威索引摘要、上述浏览器强化核验和独立来源核验报告共同为准。
