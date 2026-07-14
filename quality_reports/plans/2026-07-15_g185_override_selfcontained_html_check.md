# G185 override自包含HTML专项检查

## 检查结论

`docs/results/g185-old-method-unified-override-v1/report.html`通过本轮格式转换与自包含性检查。该文件完整转换已审查的`report.md`正文，三幅已核验PNG均以`data:image/png;base64`内嵌，CSS全部写入HTML，不依赖外部样式表或脚本。检查未发现`file://`、Windows绝对路径或外部CSS/JavaScript依赖。四个仍指向`temp/`中补充CSV、表目录、图目录和manifest的相对链接均带有“本地制品”可见标签，没有声称这些制品已在远端仓库发布。

本轮属于ARS academic-paper formatter的Phase 7格式转换，只增加renderer、HTML、测试和本检查记录。未修改`report.md`、三幅PNG、六张机器表、模型代码、分析manifest、谱系、索引或版本注册表，也未引入新的估计值、文献、结果解释或投稿主张。

## 输入身份

| 输入 | SHA-256 | 本轮状态 |
|---|---|---|
| `docs/results/g185-old-method-unified-override-v1/report.md` | `8767cf008d67550d9708e313f529dcc6cc1042768413300e8f8037ae9afd5e1a` | 未修改；renderer硬编码核验该审查哈希 |
| `fig1_national_iede.png` | `3a631fae43790d4bbabec599b773fcc31788ff1e46db4d89bf8af7a7962539f7` | 未修改；解码后哈希一致 |
| `fig2_core_linear_curves.png` | `ce7457b31ec391ba058649d4e53318480da2494792c9eb1b5b36c740d920eeb9` | 未修改；解码后哈希一致 |
| `fig3_five_zone_iede.png` | `82aa88eaa7a34fa100dc5a25ec7b8f770407e58770b2e53b8bea86f0192143d9` | 未修改；解码后哈希一致 |

## 输出与可复现性

- Renderer：`scripts/python/render_g185_override_selfcontained_html.py`。
- 输出：`docs/results/g185-old-method-unified-override-v1/report.html`。
- 输出编码：UTF-8，无BOM；UTF-8读取后回写字节完全一致。
- 输出大小：748,315 bytes。
- 输出SHA-256：`9d5d9fc0c795d46712ca94320796e59fe62b467a76606745248a71c0a212a1e5`。
- Renderer不写入时间戳、机器路径或随机值；同一Markdown和三幅PNG连续生成两次得到完全相同字节及相同SHA-256。
- Renderer只使用Python标准库，公式以保留原LaTeX字符的本地数学文本块呈现，不请求MathJax、KaTeX、字体或其他网络资源。

复现命令：

```powershell
python scripts/python/render_g185_override_selfcontained_html.py
```

## HTML解析与内容完整性检查

Python标准库`html.parser.HTMLParser`成功解析完整输出。解析后的结构为1个`article`、1个`h1`、11个`h2`、1个`h3`、44个正文段落、6张表、40个表格行、4个公式块、3个`figure`和3个`img`。三幅`img`的`src`均为PNG data URI；逐一base64解码后的三个SHA-256集合与输入PNG集合完全相同。

内容完整性测试逐行处理197行源Markdown，跳过空行、表格分隔符和公式外层定界符，将Markdown标题、列表、代码、强调、链接和图片语法规范化后，检查每个实质内容行都能在HTML可见文本或图片alt中找到，缺失为0。该检查同时覆盖标题、摘要、全部章节、六张表、四个公式、三段可见图注、五个DOI和研究声明。核心显示值`0.5768`、`1.1580`、`1.1464`、`84.1921%`以及`1,683次/1,999次`均存在，未增加或改写数值。

## 自包含与链接安全检查

| 检查项 | 结果 |
|---|---|
| `data:image/png;base64`数量 | 3，PASS |
| PNG解码哈希与已审查输入 | 3/3一致，PASS |
| 内嵌`style` | 1，PASS |
| 外部`link`或`script` | 0，PASS |
| `file://` | 0，PASS |
| Windows绝对路径 | 0，PASS |
| 剩余`temp/`相对链接 | 4，均带“本地制品”标签，PASS |
| DOI | 5个原稿DOI全部保留，PASS |
| 表格横向溢出处理 | 屏幕端滚动容器、打印端展开，PASS |
| 页面背景与打印 | 白底、无衬线字体栈、A4打印CSS，PASS |

## 自动测试

执行命令：

```powershell
python -m unittest tests.test_render_g185_override_selfcontained_html -v
python -m py_compile scripts/python/render_g185_override_selfcontained_html.py tests/test_render_g185_override_selfcontained_html.py
```

结果为6项unittest全部通过，Python语法编译通过。测试覆盖源稿哈希锁定、确定性输出、无绝对机器路径、三图data URI数量、内嵌图哈希、核心标题与数值、五个DOI、六张表、全部Markdown内容行以及四个本地制品标签。

## 边界说明

自包含HTML关闭了公共最终审查中“三幅本地图无法随远端Markdown呈现”的唯一持久化Minor。HTML内的正文、数值和解释仍以`report.md`为审查真值；本次格式转换不改变该稿`PASS_PUBLIC_FINAL`、91/100及“尚未达到95分投稿完成门槛”的既有状态。`temp/`补充机器链接继续只用于本地复核，标签已明确其本地属性；如需面向外部读者分发完整机器表，仍须另行建立符合数据许可和项目结果边界的持久制品。
