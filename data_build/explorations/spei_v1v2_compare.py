"""
spei_v1v2_compare.py
目的: 比较 v1 (SPEI_season) 与 v2 (spei6_mean) 在 full season 窗口上的差异大小
方法: 按 grid_id + year 合并，计算相关系数、MAE、分布差异
作者: Yang Su
日期: 2026-04-04
"""

import pandas as pd
import numpy as np

# ── 路径 ─────────────────────────────────────────────────────────────────────
V1_PATH = "C:/YangSu/00_Project/CA_mechanism/data/master/data_v1_with_climate.csv"
V2_PATH = "C:/YangSu/00_Project/CA_mechanism/regression_SR/data_build/data/processed/data_v2_main.parquet"

# ── 载入数据 ──────────────────────────────────────────────────────────────────
print("Loading v1...")
v1 = pd.read_csv(V1_PATH, encoding="gbk", usecols=["grid_id", "year", "SPEI_season"])
print(f"  v1 rows: {len(v1):,}  |  SPEI_season non-null: {v1['SPEI_season'].notna().sum():,}")

print("Loading v2...")
v2 = pd.read_parquet(V2_PATH, columns=["grid_id", "year", "spei6_mean"])
print(f"  v2 rows: {len(v2):,}  |  spei6_mean non-null: {v2['spei6_mean'].notna().sum():,}")

# ── 合并 ──────────────────────────────────────────────────────────────────────
df = v1.merge(v2, on=["grid_id", "year"], how="inner")
print(f"\nMerged rows: {len(df):,}")

# ── 差异统计 ──────────────────────────────────────────────────────────────────
df["diff"] = df["spei6_mean"] - df["SPEI_season"]
diff = df["diff"].dropna()

print("\n" + "="*55)
print("  v1: SPEI_season (end-month extraction, scale ~ season)")
print("  v2: spei6_mean  (monthly weighted mean, SPEI-6)")
print("="*55)

print(f"\n[v1 SPEI_season 描述统计]")
print(df["SPEI_season"].describe().round(4).to_string())

print(f"\n[v2 spei6_mean 描述统计]")
print(df["spei6_mean"].describe().round(4).to_string())

print(f"\n[差值 = v2 - v1 描述统计]")
print(diff.describe().round(4).to_string())

# ── 关键指标 ──────────────────────────────────────────────────────────────────
mae   = diff.abs().mean()
rmse  = np.sqrt((diff**2).mean())
corr  = df[["SPEI_season","spei6_mean"]].corr().iloc[0,1]
pct90 = diff.abs().quantile(0.90)
pct99 = diff.abs().quantile(0.99)

print(f"\n[关键差异指标]")
print(f"  相关系数 (r):           {corr:.4f}")
print(f"  MAE  (平均绝对差):      {mae:.4f}")
print(f"  RMSE:                  {rmse:.4f}")
print(f"  |diff| P90:            {pct90:.4f}")
print(f"  |diff| P99:            {pct99:.4f}")
print(f"  |diff| > 0.5 比例:     {(diff.abs()>0.5).mean()*100:.1f}%")
print(f"  |diff| > 1.0 比例:     {(diff.abs()>1.0).mean()*100:.1f}%")

# ── 按年分组 ──────────────────────────────────────────────────────────────────
print(f"\n[按年份的 MAE 和相关系数]")
for yr, g in df.groupby("year"):
    d = g["spei6_mean"] - g["SPEI_season"]
    r = g[["SPEI_season","spei6_mean"]].corr().iloc[0,1]
    print(f"  {yr}: MAE={d.abs().mean():.4f}  r={r:.4f}  N={len(g):,}")

# ── 方向一致性 ────────────────────────────────────────────────────────────────
same_sign = ((df["SPEI_season"] < 0) == (df["spei6_mean"] < 0)).mean()
print(f"\n[干旱/湿润方向一致性 (同号比例)]: {same_sign*100:.1f}%")

print("\nDone.")
