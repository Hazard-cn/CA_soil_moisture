"""
Build a PDF report for the GGCP10 new-area GLEAM baseline results, organized by
SM mean, drought-state, and wet-state mediators.
"""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String


PROJ_DIR = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
RUN_DIR = PROJ_DIR / "temp" / "2026-05-18_ggcp10_harvarea_agg_baseline_suite"
INPUT_CSV = RUN_DIR / "ggcp10_core_baseline_focus_terms.csv"
SUMMARY_CSV = RUN_DIR / "ggcp10_gleam_three_mediator_summary.csv"
OUTPUT_PDF = RUN_DIR / "ggcp10_gleam_three_mediator_baseline_report.pdf"

FONT_PATH = Path("C:/Windows/Fonts/simhei.ttf")
FONT_NAME = "SimHei"

PAGE_W, PAGE_H = A4
LEFT = 18 * mm
RIGHT = 18 * mm
TOP = 16 * mm
BOTTOM = 16 * mm

LAYER_COLORS = {
    "GLEAM-Sfc": colors.HexColor("#1f7a3f"),
    "GLEAM-Root": colors.HexColor("#63b56f"),
}

MEDIATOR_META = OrderedDict(
    [
        (
            "raw_sm",
            {
                "title": "A. SM mean",
                "subtitle": "原生 GLEAM 土壤湿度均值",
                "expected": {
                    "a1": "-",
                    "a3": "+",
                    "c1": "-",
                    "c3": "+",
                    "b": "+",
                },
            },
        ),
        (
            "sm_dry_state",
            {
                "title": "B. SM drought state",
                "subtitle": "基于 GLEAM 构造的干旱状态变量",
                "expected": {
                    "a1": "+",
                    "a3": "-",
                    "c1": "-",
                    "c3": "+",
                    "b": "-",
                },
            },
        ),
        (
            "sm_wet_state",
            {
                "title": "C. SM wet state",
                "subtitle": "基于 GLEAM 构造的湿涝状态变量",
                "expected": {
                    "a1": "不预设",
                    "a3": "不预设",
                    "c1": "-",
                    "c3": "+",
                    "b": "不预设",
                },
            },
        ),
    ]
)

MEDIATOR_NOTES = {
    "raw_sm": (
        "Drought 组与理论预期最接近：a1、a3、c1、b 均在两层 GLEAM 中同向且显著，"
        "但 c3 为显著负号。Heat 组中 a1 为负、b 为正，但 a3 同样为显著负号，"
        "而 c1 与 c3 均不显著。HotDry 组中 a1 为负、b 为正，但 c1 为显著正号，"
        "a3 主要为负，c3 不显著。"
    ),
    "sm_dry_state": (
        "三类灾害在中介方程中的 a1 均为显著正号，a3 均为显著负号，说明 dry-state 的构造本身能够稳定响应外生胁迫及其与 SR 的交互。"
        "但在产量方程中，b 全部为正号，与 dry-state 理论预期相反；Drought 的 c3 也主要为显著负号，"
        "Heat 与 HotDry 的 c3 则多数不显著。"
    ),
    "sm_wet_state": (
        "wet-state 的结果更不一致。Drought 与 Heat 的 a1 主要为正，a3 主要为负；HotDry 的 a1 也多数为正，a3 为负。"
        "c1 在 Drought 下为负、在 HotDry 下为正，Heat 下不显著；b 在各组均缺乏稳定方向，"
        "因此 wet-state 更适合作为补充状态变量，而不是当前 baseline 的主解释通道。"
    ),
}

PATH_META = OrderedDict(
    [
        (
            "a1",
            {
                "equation": "mediator",
                "term": "Main",
                "title": "a1: hazard -> M",
                "desc": "灾害主效应进入中介方程",
            },
        ),
        (
            "a3",
            {
                "equation": "mediator",
                "term": "SR_x_Main",
                "title": "a3: SR x hazard -> M",
                "desc": "SR 与灾害交互项进入中介方程",
            },
        ),
        (
            "c1",
            {
                "equation": "outcome",
                "term": "Main",
                "title": "c1: hazard -> ln(yield)",
                "desc": "灾害主效应进入产量方程",
            },
        ),
        (
            "c3",
            {
                "equation": "outcome",
                "term": "SR_x_Main",
                "title": "c3: SR x hazard -> ln(yield)",
                "desc": "SR 与灾害交互项进入产量方程",
            },
        ),
        (
            "b",
            {
                "equation": "outcome",
                "term": "M",
                "title": "b: M -> ln(yield)",
                "desc": "中介变量进入产量方程",
            },
        ),
    ]
)

HAZARD_LABELS = {
    "drought": "Drought",
    "heat": "Heat",
    "hotdry": "HotDry",
}

SCHEME_LABELS = {
    "native": "native",
    "pooled_state": "pooled",
    "maize_zone_state": "maize-zone",
}


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))


def sig_label(p: float) -> str:
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return "n.s."


def path_key(row: pd.Series) -> str:
    for key, meta in PATH_META.items():
        if row["equation"] == meta["equation"] and row["term"] == meta["term"]:
            return key
    raise ValueError(f"Unmapped path for {row['equation']} / {row['term']}")


def load_data() -> pd.DataFrame:
    df = pd.read_csv(INPUT_CSV)
    df = df[df["sm_label"].isin(["GLEAM-Sfc", "GLEAM-Root"])].copy()
    df["path"] = df.apply(path_key, axis=1)
    df["ci_lo"] = df["b"] - 1.96 * df["se"]
    df["ci_hi"] = df["b"] + 1.96 * df["se"]
    df["sig_label"] = df["p"].map(sig_label)
    df["cell_label"] = df.apply(
        lambda r: f"{HAZARD_LABELS[r['hazard']]} | {SCHEME_LABELS[r['threshold_scheme']]}",
        axis=1,
    )
    return df


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for mediator_type in MEDIATOR_META:
        for hazard in HAZARD_LABELS:
            for path in PATH_META:
                dd = df[
                    (df["mediator_type"] == mediator_type)
                    & (df["hazard"] == hazard)
                    & (df["path"] == path)
                ]
                if dd.empty:
                    continue
                rows.append(
                    {
                        "mediator_type": mediator_type,
                        "hazard": hazard,
                        "path": path,
                        "n": len(dd),
                        "positive": int((dd["b"] > 0).sum()),
                        "negative": int((dd["b"] < 0).sum()),
                        "p_lt_001": int((dd["p"] < 0.01).sum()),
                        "p_lt_005": int(((dd["p"] >= 0.01) & (dd["p"] < 0.05)).sum()),
                        "p_lt_010": int(((dd["p"] >= 0.05) & (dd["p"] < 0.10)).sum()),
                        "ns": int((dd["p"] >= 0.10).sum()),
                    }
                )
    out = pd.DataFrame(rows)
    out.to_csv(SUMMARY_CSV, index=False)
    return out


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontName=FONT_NAME,
            fontSize=22,
            leading=28,
            spaceAfter=10,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName=FONT_NAME,
            fontSize=16,
            leading=22,
            spaceBefore=8,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName=FONT_NAME,
            fontSize=13,
            leading=18,
            spaceBefore=8,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["BodyText"],
            fontName=FONT_NAME,
            fontSize=10.5,
            leading=16,
            spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "small",
            parent=base["BodyText"],
            fontName=FONT_NAME,
            fontSize=8.5,
            leading=12,
            spaceAfter=4,
        ),
        "caption": ParagraphStyle(
            "caption",
            parent=base["BodyText"],
            fontName=FONT_NAME,
            fontSize=9,
            leading=13,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#59616c"),
            spaceBefore=3,
            spaceAfter=8,
        ),
    }


def table_style() -> TableStyle:
    return TableStyle(
        [
            ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
            ("FONTSIZE", (0, 0), (-1, 0), 8.5),
            ("FONTSIZE", (0, 1), (-1, -1), 8.2),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#20262d")),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d6dde5")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    )


def summary_table(summary: pd.DataFrame, mediator_type: str) -> Table:
    rows = [["Hazard", "Path", "Expected", "Positive", "Negative", "p<0.01", "p<0.05", "p<0.10", "n.s."]]
    expected = MEDIATOR_META[mediator_type]["expected"]
    dd = summary[summary["mediator_type"] == mediator_type].copy()
    for hazard in HAZARD_LABELS:
        for path in PATH_META:
            row = dd[(dd["hazard"] == hazard) & (dd["path"] == path)]
            if row.empty:
                continue
            r = row.iloc[0]
            rows.append(
                [
                    HAZARD_LABELS[hazard],
                    path,
                    expected[path],
                    str(int(r["positive"])),
                    str(int(r["negative"])),
                    str(int(r["p_lt_001"])),
                    str(int(r["p_lt_005"])),
                    str(int(r["p_lt_010"])),
                    str(int(r["ns"])),
                ]
            )
    tbl = Table(rows, colWidths=[20 * mm, 12 * mm, 18 * mm, 16 * mm, 16 * mm, 16 * mm, 16 * mm, 16 * mm, 14 * mm])
    tbl.setStyle(table_style())
    return tbl


def row_order(df: pd.DataFrame, mediator_type: str) -> list[str]:
    dd = df[df["mediator_type"] == mediator_type].copy()
    if mediator_type == "raw_sm":
        keys = [f"{HAZARD_LABELS[h]} | native" for h in HAZARD_LABELS]
    else:
        keys = []
        for h in HAZARD_LABELS:
            keys.extend(
                [
                    f"{HAZARD_LABELS[h]} | pooled",
                    f"{HAZARD_LABELS[h]} | maize-zone",
                ]
            )
    return [k for k in keys if k in set(dd["cell_label"])]


def coef_plot(
    df: pd.DataFrame,
    mediator_type: str,
    path: str,
    width: float = 170 * mm,
    row_h: float = 17 * mm,
) -> Drawing:
    dd = df[(df["mediator_type"] == mediator_type) & (df["path"] == path)].copy()
    rows = row_order(df, mediator_type)
    meta = PATH_META[path]
    height = 22 * mm + row_h * len(rows) + 14 * mm
    d = Drawing(width, height)

    left_label_w = 42 * mm
    plot_x0 = left_label_w
    plot_x1 = width - 8 * mm
    center_x = (plot_x0 + plot_x1) / 2

    d.add(
        String(
            0,
            height - 7 * mm,
            f"{meta['title']}  ({meta['desc']})",
            fontName=FONT_NAME,
            fontSize=11,
            fillColor=colors.black,
        )
    )
    d.add(
        String(
            0,
            height - 13 * mm,
            f"{MEDIATOR_META[mediator_type]['title']} | expected sign: {MEDIATOR_META[mediator_type]['expected'][path]}",
            fontName=FONT_NAME,
            fontSize=8.5,
            fillColor=colors.HexColor("#4d5560"),
        )
    )

    for idx, cell in enumerate(rows):
        y_mid = height - 24 * mm - idx * row_h
        sub = dd[dd["cell_label"] == cell].copy()
        max_abs = max(float(sub[["ci_lo", "ci_hi"]].abs().to_numpy().max()), 1e-9)
        x_scale = (plot_x1 - plot_x0) / (2 * max_abs * 1.12)

        d.add(String(0, y_mid - 2, cell, fontName=FONT_NAME, fontSize=8.3))
        d.add(Line(center_x, y_mid - 6 * mm, center_x, y_mid + 6 * mm, strokeColor=colors.black, strokeWidth=0.7))
        d.add(
            Line(
                plot_x0,
                y_mid,
                plot_x1,
                y_mid,
                strokeColor=colors.HexColor("#e4e8ed"),
                strokeWidth=0.6,
            )
        )
        d.add(
            String(
                plot_x0,
                y_mid - 5.5 * mm,
                f"{-max_abs:.3g}",
                fontName=FONT_NAME,
                fontSize=6.8,
                fillColor=colors.HexColor("#68717d"),
            )
        )
        d.add(
            String(
                center_x - 3 * mm,
                y_mid - 5.5 * mm,
                "0",
                fontName=FONT_NAME,
                fontSize=6.8,
                fillColor=colors.HexColor("#68717d"),
            )
        )
        d.add(
            String(
                plot_x1 - 10 * mm,
                y_mid - 5.5 * mm,
                f"{max_abs:.3g}",
                fontName=FONT_NAME,
                fontSize=6.8,
                fillColor=colors.HexColor("#68717d"),
            )
        )

        y_offsets = {"GLEAM-Sfc": -2.5 * mm, "GLEAM-Root": 2.5 * mm}
        for _, r in sub.iterrows():
            color = LAYER_COLORS[r["sm_label"]]
            y = y_mid + y_offsets[r["sm_label"]]
            x_lo = center_x + float(r["ci_lo"]) * x_scale
            x_hi = center_x + float(r["ci_hi"]) * x_scale
            x_b = center_x + float(r["b"]) * x_scale
            d.add(Line(x_lo, y, x_hi, y, strokeColor=color, strokeWidth=1.1))
            significant = float(r["p"]) < 0.10
            d.add(
                Circle(
                    x_b,
                    y,
                    1.8 * mm,
                    strokeColor=color,
                    fillColor=color if significant else colors.white,
                    strokeWidth=0.9,
                )
            )
            label = f"{float(r['b']):+.3g}{r['sig_label'] if significant else ''}"
            tx = x_b + 2.5 * mm
            if x_b > plot_x1 - 18 * mm:
                tx = x_b - 17 * mm
            d.add(String(tx, y + 1.2 * mm, label, fontName=FONT_NAME, fontSize=6.8, fillColor=color))

    legend_y = 5 * mm
    x = 0
    d.add(String(x, legend_y, "Layer:", fontName=FONT_NAME, fontSize=8))
    x += 15 * mm
    for layer, color in LAYER_COLORS.items():
        d.add(Line(x, legend_y + 1.5 * mm, x + 7 * mm, legend_y + 1.5 * mm, strokeColor=color, strokeWidth=1.2))
        d.add(Circle(x + 3.5 * mm, legend_y + 1.5 * mm, 1.8 * mm, strokeColor=color, fillColor=color))
        d.add(String(x + 9 * mm, legend_y, layer, fontName=FONT_NAME, fontSize=8))
        x += 33 * mm
    d.add(String(x, legend_y, "filled = p<0.10; hollow = n.s.", fontName=FONT_NAME, fontSize=8))
    return d


def on_page(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont(FONT_NAME, 8)
    canvas.setFillColor(colors.HexColor("#6a7380"))
    canvas.drawRightString(PAGE_W - RIGHT, 10 * mm, str(doc.page))
    canvas.restoreState()


def build_pdf(df: pd.DataFrame, summary: pd.DataFrame) -> None:
    styles = make_styles()
    doc = BaseDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=LEFT,
        rightMargin=RIGHT,
        topMargin=TOP,
        bottomMargin=BOTTOM,
    )
    frame = Frame(LEFT, BOTTOM, PAGE_W - LEFT - RIGHT, PAGE_H - TOP - BOTTOM, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=on_page)])

    story: list = []
    story.append(Paragraph("GGCP10 新面积分支 - GLEAM baseline 结果", styles["title"]))
    story.append(
        Paragraph(
            "仅使用新数据分支；仅保留 GLEAM-Sfc 与 GLEAM-Root；按 SM mean、SM drought state、SM wet state 三类中介变量整理。"
            "当前文档只呈现两条 baseline 方程，不含 IE、DE、异质性或旧数据对照。",
            styles["body"],
        )
    )
    story.append(Paragraph("1. 研究范围", styles["h1"]))
    story.append(
        Paragraph(
            "样本 N = 62,018。外生灾害分为 Drought、Heat、HotDry；中介方程与产量方程共用 grid_id + year 固定效应，"
            "并以 grid_id 聚类标准误。SM mean 使用原生 GLEAM 均值；两类状态变量使用 pooled-state 与 maize-zone-state 两套构造。",
            styles["body"],
        )
    )
    story.append(Paragraph("2. 方程", styles["h1"]))
    story.append(
        Paragraph(
            "M = a0 + a1·Hazard + a2·SR + a3·(SR×Hazard) + controls + FE<br/>"
            "ln(Yield) = c0 + c1·Hazard + c2·SR + c3·(SR×Hazard) + b·M + controls + FE",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "控制变量沿用本轮 baseline：hdd_ge32、pr_sum、et0_sum、aridity、gdd_10_30、irr_frac；HotDry 组在其各自 baseline 中按既有设定保留对应控制。",
            styles["body"],
        )
    )
    story.append(Paragraph("3. 图表读法", styles["h1"]))
    story.append(
        Paragraph(
            "每张图只对应一个路径；每一行是一个 hazard × state-definition cell；每行两个点分别表示 GLEAM-Sfc 与 GLEAM-Root。"
            "横线为 95% CI；横轴在每一行内围绕 0 对称缩放；实心点表示 p<0.10，空心点表示不显著。",
            styles["body"],
        )
    )

    for mediator_type, meta in MEDIATOR_META.items():
        story.append(PageBreak())
        story.append(Paragraph(meta["title"], styles["h1"]))
        story.append(Paragraph(meta["subtitle"], styles["body"]))
        story.append(Paragraph(MEDIATOR_NOTES[mediator_type], styles["body"]))
        story.append(summary_table(summary, mediator_type))
        story.append(Spacer(1, 5 * mm))
        for path in PATH_META:
            story.append(PageBreak())
            plot = coef_plot(df, mediator_type, path)
            story.append(
                KeepTogether(
                    [
                        plot,
                        Paragraph(
                            f"{meta['title']} - {PATH_META[path]['title']}",
                            styles["caption"],
                        ),
                    ]
                )
            )

    doc.build(story)


def main() -> None:
    register_fonts()
    df = load_data()
    summary = summarize(df)
    build_pdf(df, summary)
    print(f"Saved: {SUMMARY_CSV}")
    print(f"Saved: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
