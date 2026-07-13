# CLAUDE.MD -- Data Build: 精细化栅格数据构建

**Project:** Straw Return (SR) Buffering — 栅格气象数据精细化重构
**Parent Project:** `../` (regression_SR)
**Languages:** R (primary), Python (auxiliary)
**Spatial Unit:** 0.1° grid (+ finer resolution TBD)
**Temporal Unit:** Daily → phenological window aggregation

---

## Core Principles

- **Plan first** -- enter plan mode before non-trivial tasks; save plans to `quality_reports/plans/`
- **Verify after** -- run scripts and confirm output at the end of every task
- **Quality gates** -- nothing ships below 80/100
- **Chinese docs, English code** -- documentation/logs in Chinese, code/variables in English

---

## Folder Structure

```
data_build/
├── CLAUDE.md                    # This file
├── .claude/                     # Rules, skills
├── docs/                        # DATA_SOURCES.md, VARIABLES.md, etc.
├── data/
│   ├── raw/                     # 原始日尺度栅格数据（从E盘梳理后放入）
│   ├── intermediate/            # 中间处理结果（窗口聚合、指标计算）
│   └── processed/               # 最终分析数据（面板格式，可直接用于回归）
├── scripts/
│   ├── R/                       # R 数据处理脚本
│   └── python/                  # Python 数据处理脚本
├── output/
│   ├── tables/                  # 描述性统计/数据质量表
│   ├── figures/                 # 数据质量可视化
│   └── logs/                    # 运行日志
├── explorations/                # 数据探索沙盒（60/100 threshold）
├── quality_reports/             # Plans, session logs, specs
├── references/                  # 参考代码/文献
└── templates/                   # Session log, quality report templates
```

---

## Commands

```bash
# R
Rscript scripts/R/filename.R

# Python
python scripts/python/filename.py
```

---

## 数据构建核心设计

### 物候节点

| 节点 | 变量 | 含义 |
|------|------|------|
| V3 | `v3_doy` | 三叶期 DOY |
| HE | `he_doy` | 抽穗期 DOY |
| MA | `ma_doy` | 成熟期 DOY |

### 时间窗口方案

**方案A：节点前后±10天窗口**
| 窗口 | 定义 | 说明 |
|------|------|------|
| V3±10 | `[v3_doy - 10, v3_doy + 10]` | 三叶期窗口 |
| HE±10 | `[he_doy - 10, he_doy + 10]` | 抽穗期窗口 |
| ~~MA±10~~ | 不做 | 用户明确排除成熟期前后 |

**方案B：节点之间（生育阶段）**
| 窗口 | 定义 | 说明 |
|------|------|------|
| V3→HE | `[v3_doy, he_doy]` | 营养生长→生殖生长过渡期 |
| HE→MA | `[he_doy, ma_doy]` | 灌浆-成熟期 |

### 需重算的气象变量（ALL）

| 类别 | 变量 | 原始日数据字段 |
|------|------|----------------|
| 温度 | t2m, tmax, tmin | 日均温、日最高温、日最低温 |
| 降水 | pr | 日降水量 |
| VPD | vpd | 日VPD |
| 土壤水分 | gleam_smrz, gleam_sms | GLEAM 根区/表面 SM |
| 蒸散 | et0 | 参考蒸散量 |

### 每个变量在每个窗口内计算的统计量

| 统计量 | 说明 |
|--------|------|
| `_mean` | 窗口均值 |
| `_sum` | 窗口累积 |
| `_min` | 窗口最小值 |
| `_max` | 窗口最大值 |
| `_sd` | 窗口标准差 |

### 降水专项指标体系

| 类别 | 指标 | 说明 |
|------|------|------|
| **基础** | `pr_sum`, `pr_mean`, `pr_max` | 累积、均值、最大日降水 |
| **极端天数** | `drydays_lt1mm`, `wetdays_ge10mm`, `wetdays_ge20mm` | 干旱/强降水天数 |
| **连续性** | `max_cdd` (连续干旱天), `max_cwd` (连续湿润天) | 持续性指标 |
| **标准化** | `SPI_window`, `SPEI_window` | 不同窗口尺度的 SPI/SPEI |
| **水分平衡** | `wd_deficit` (ET0-P), `aridity_index` (ET0/P) | 水分亏缺/干旱指数 |
| **强度** | `pr_intensity` (降水日均降水量), `pr_concentration` | 降水集中度 |

### 温度专项指标

| 类别 | 指标 | 说明 |
|------|------|------|
| **热度日** | `hdd_ge29` ~ `hdd_ge40` | max(Tmax - threshold, 0) 累积 |
| **高温天数** | `hotdays_ge29` ~ `hotdays_ge40` | Tmax ≥ threshold 天数 |
| **基于百分位** | `hdd_ge_p90`, `hdd_ge_p95` | 基于baseline的阈值 |
| **GDD** | `gdd_ge10` | 生长度日 |

### 空间尺度

| 尺度 | 说明 | 状态 |
|------|------|------|
| 0.1° (~10km) | 当前基准 | 确定 |
| 更细尺度 | 待定 | 后续确定 |

---

## 数据版本管理

- 每个处理版本保存为 `data/processed/data_v{N}_{description}.csv`
- 中间步骤保存到 `data/intermediate/`，带时间戳
- 每次重大修改写 changelog 到 `docs/CHANGELOG.md`

---

## 质量校验清单

- [ ] 行数与预期一致（每年 grid 数 × 年数）
- [ ] 无全NA列
- [ ] 物候日期合理（V3 < HE < MA）
- [ ] 气象变量范围合理（温度 -30~50°C, 降水 ≥ 0）
- [ ] 窗口天数 = 预期天数（±10天 → 21天, V3→HE → he_doy - v3_doy）
- [ ] 空间覆盖完整（与 v1 版本 grid 一致或可解释差异）
- [ ] 缺失值记录（记录每变量缺失率）
- [ ] 与 v1 版本可比性检查（同窗口覆盖时，统计量应近似）

---

## Quality Thresholds

| Score | Gate | Meaning |
|-------|------|---------|
| 80 | Commit | Good enough to save |
| 90 | PR | Ready for review |
| 95 | Excellence | Publication-ready |

---

## Non-Negotiables

- Panel structure: keyed by `grid_id`, `year`
- Seeds: `set.seed(42)` (R), `random_state=42` (Python) at file top
- Figures: white bg, 300 DPI, width 12 height 5 (adjustable), sans-serif font
- Paths: R `here::here()` or relative paths; Python relative paths
- All raw data transformations must be reproducible from scripts

---

## Key Data Reference

- **Parent dataset:** `C:/YangSu/00_Project/CA_mechanism/data/master/data_v1_with_climate.csv` (69,038 rows, 143 cols, GBK encoding; shared external path)
- **Raw data source:** E: drive (to be organized into `data/raw/`)
- **Outcome:** `yield_tons_ha`, `ln_yield` (from parent)
- **SR lever:** `ca`, `crc_ca_ratio`, `crc_lag1` (from parent)
- **Phenology DOY:** `v3_doy`, `he_doy`, `ma_doy`
- **FE keys:** `grid_id`, `year`, `prov_id`, `prov_year`
- **Full variable dictionary:** `docs/VARIABLES.md` (v1 reference)
- **Data provenance:** `docs/DATA_SOURCES.md` / `docs/DATA_SOURCES_CN.md`

---

## Skills Quick Reference

| Command | What It Does |
|---------|-------------|
| `/data-analysis [task]` | End-to-end R+Python analysis |
| `/review-r [file]` | R code quality review |
| `/context-status` | Show session health |
| `/commit [msg]` | Stage + commit (when git enabled) |
