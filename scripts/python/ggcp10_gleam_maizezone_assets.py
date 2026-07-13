"""
Build Markdown and coefficient-plot PNG assets for the GGCP10 GLEAM
maize-zone-only Feishu report.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
from reportlab.graphics import renderPDF

from ggcp10_gleam_three_mediator_report import (
    HAZARD_LABELS,
    MEDIATOR_META,
    PATH_META,
    coef_plot,
    load_data,
    register_fonts,
)


PROJ_DIR = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
RUN_DIR = PROJ_DIR / "temp" / "2026-05-18_ggcp10_harvarea_agg_baseline_suite"
ASSET_DIR = RUN_DIR / "feishu_maizezone_assets"
MD_PATH = RUN_DIR / "ggcp10_gleam_maizezone_feishu_doc.md"

MEDIATOR_TITLES = {
    "raw_sm": "SM mean",
    "sm_dry_state": "SM drought state - maize-zone only",
    "sm_wet_state": "SM wet state - maize-zone only",
}


def filtered_data() -> pd.DataFrame:
    df = load_data()
    return df[
        (df["mediator_type"].eq("raw_sm"))
        | (df["threshold_scheme"].eq("maize_zone_state"))
    ].copy()


def render_assets(df: pd.DataFrame) -> list[tuple[str, Path]]:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    assets: list[tuple[str, Path]] = []
    for mediator_type in MEDIATOR_META:
        for path in PATH_META:
            drawing = coef_plot(df, mediator_type, path, width=165 * 2.83465, row_h=14 * 2.83465)
            pdf_out = ASSET_DIR / f"{mediator_type}_{path}.pdf"
            out = ASSET_DIR / f"{mediator_type}_{path}.png"
            renderPDF.drawToFile(drawing, str(pdf_out))
            subprocess.run(
                ["pdftoppm", "-png", "-singlefile", str(pdf_out), str(out.with_suffix(""))],
                check=True,
            )
            assets.append((f"FIG::{mediator_type}::{path}", out))
    return assets


def subset_summary(df: pd.DataFrame, mediator_type: str, hazard: str, path: str) -> pd.DataFrame:
    meta = PATH_META[path]
    dd = df[
        (df["mediator_type"] == mediator_type)
        & (df["hazard"] == hazard)
        & (df["equation"] == meta["equation"])
        & (df["term"] == meta["term"])
    ].copy()
    return dd


def sig_label(p: float) -> str:
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return "n.s."


def make_markdown(df: pd.DataFrame) -> None:
    lines: list[str] = []
    lines.append("# GGCP10 新面积分支 - GLEAM maize-zone baseline 结果")
    lines.append("")
    lines.append("口径：只使用新面积分支；只看 GLEAM；状态变量只保留 maize-zone-state；当前只整理两条 baseline 方程，不包含 IE、DE 和异质性。")
    lines.append("")
    lines.append("## 1. 研究范围")
    lines.append("")
    lines.append("样本 N = 62,018；外生灾害分为 Drought、Heat、HotDry；固定效应为 `grid_id + year`，标准误按 `grid_id` 聚类。")
    lines.append("")
    lines.append("## 2. 方程")
    lines.append("")
    lines.append("`M = a0 + a1·Hazard + a2·SR + a3·(SR×Hazard) + controls + FE`")
    lines.append("")
    lines.append("`ln(Yield) = c0 + c1·Hazard + c2·SR + c3·(SR×Hazard) + b·M + controls + FE`")
    lines.append("")
    lines.append("## 3. 为什么这版没有出现参考 PDF 里的 22 个 dry-state 指标")
    lines.append("")
    lines.append("你刚发的参考 PDF 使用的是 2026-04-23 新增的 dry-side metric family：`mdduration_dry`、`mddurshare_dry`、`mdseverity_dry`、`blduration_dry`、`bldurshare_dry`、`blseveritymean_ddf`、`blseveritysum_ddf`，并在 `p10/p20` 下展开成 22 个 spec cell。那一套 family 在变量说明中被明确列为新增 GLEAM 指标，不属于 legacy `pooled-state / maize-zone-state`。")
    lines.append("")
    lines.append("本次按“只用 maize-zone”执行时，dry-state 严格对应的只有 `ds_mz_gsms` 与 `ds_mz_gsmrz` 两个变量；所以若严格坚持 maize-zone，就不会同时出现那 22 个 dry-side 指标。前一版文档之所以没有体现它们，是因为使用的是压缩后的 `core baseline`，不是 `v6gleambl_nomwet` 的 full-family 结果。")
    lines.append("")

    notes = {
        "raw_sm": "Drought 组最接近理论预期：a1<0、a3>0、c1<0、b>0，但 c3 在两层 GLEAM 下均为负。Heat 组中 a1<0、a3<0、b>0，c1/c3 不显著。HotDry 组中 a1<0、a3 主要为负、c1>0、c3 不显著。",
        "sm_dry_state": "三类灾害的 a1 都为正、a3 都为负，说明 maize-zone dry-state 能稳定响应灾害及其与 SR 的交互；但 b 全部为正，与 dry-state 理论预期相反，Drought 的 c3 也主要为负。",
        "sm_wet_state": "wet-state 的方向更不稳定。Drought 与 Heat 的 a1 主要为正、a3 主要为负，HotDry 的 a1 也多为正、a3 为负；但 b 缺乏稳定方向，因此更适合作为补充变量。",
    }

    for idx, mediator_type in enumerate(MEDIATOR_META, start=4):
        lines.append(f"## {idx}. {MEDIATOR_TITLES[mediator_type]}")
        lines.append("")
        if mediator_type == "raw_sm":
            lines.append("变量：`gleam_sms_mean`、`gleam_smrz_mean`。")
        elif mediator_type == "sm_dry_state":
            lines.append("变量：`ds_mz_gsms`、`ds_mz_gsmrz`。")
        else:
            lines.append("变量：`ws_mz_gsms`、`ws_mz_gsmrz`。")
        lines.append("")
        lines.append(notes[mediator_type])
        lines.append("")
        lines.append("| Hazard | Path | GLEAM-Sfc | GLEAM-Root |")
        lines.append("|---|---:|---:|---:|")
        for hazard in HAZARD_LABELS:
            for path in PATH_META:
                dd = subset_summary(df, mediator_type, hazard, path).sort_values("sm_label")
                vals = {r["sm_label"]: f"{r['b']:+.4g} {sig_label(r['p'])}" for _, r in dd.iterrows()}
                lines.append(
                    f"| {HAZARD_LABELS[hazard]} | {path} | {vals.get('GLEAM-Sfc', '')} | {vals.get('GLEAM-Root', '')} |"
                )
        lines.append("")
        for path in PATH_META:
            lines.append(f"### {PATH_META[path]['title']}")
            lines.append("")
            lines.append(f"FIG::{mediator_type}::{path}")
            lines.append("")

    MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    register_fonts()
    df = filtered_data()
    render_assets(df)
    make_markdown(df)
    print(f"Saved: {MD_PATH}")
    print(f"Saved assets in: {ASSET_DIR}")


if __name__ == "__main__":
    main()
