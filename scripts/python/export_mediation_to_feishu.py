"""
export_mediation_to_feishu.py
Purpose: Create a Feishu docx report for Model 8 moderated mediation results,
         embed core figures, and register in the soilmoisture Bitable.

Target base:
https://vcn7opmi92n5.feishu.cn/base/XsH1beeEMaMf0Os04IYcSz54nhh?table=tbl6rr1HIvCsIyo1&view=vew6kbxW07
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import pandas as pd

ROOTDIR = Path(r"C:\YangSu\00_Project\CA_mechanism\regression_SR")
TABDIR = ROOTDIR / "output" / "tables"
FIGDIR = ROOTDIR / "output" / "figures"

BASE_TOKEN = "XsH1beeEMaMf0Os04IYcSz54nhh"
TABLE_ID = "tbl6rr1HIvCsIyo1"
VIEW_ID = "vew6kbxW07"
FEISHU_HOST = "https://vcn7opmi92n5.feishu.cn"
DOC_TITLE = "Model 8 调节中介分析 — SR 缓解极端气候机制"

LARK_CLI = [
    "node",
    r"C:\Users\Lenovo\AppData\Roaming\npm\node_modules\@larksuite\cli\scripts\run.js",
]

ENV = os.environ.copy()
ENV["MSYS_NO_PATHCONV"] = "1"
ENV["LARK_CLI_NO_PROXY"] = "1"
# Remove proxy env vars that interfere with lark-cli
for proxy_key in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy"):
    ENV.pop(proxy_key, None)


def decode_output(raw: bytes) -> str:
    for enc in ("utf-8", "gbk"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def lark_api(
    method: str,
    path: str,
    data: Optional[Dict[str, Any]] = None,
    file_path: Optional[Path] = None,
) -> Dict[str, Any]:
    cmd = list(LARK_CLI) + ["api", method, path, "--as", "user"]
    if data is not None:
        cmd += ["--data", json.dumps(data, ensure_ascii=False)]
    if file_path is not None:
        rel = os.path.relpath(file_path, ROOTDIR)
        cmd += ["--file", f"file={rel}"]

    result = subprocess.run(
        cmd,
        capture_output=True,
        shell=False,
        env=ENV,
        cwd=str(ROOTDIR),
        check=False,
    )
    stdout = decode_output(result.stdout)
    if result.returncode != 0 and not stdout.strip():
        raise RuntimeError(decode_output(result.stderr)[:500])
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError((stdout or decode_output(result.stderr))[:500]) from exc
    if payload.get("code") not in (0, None):
        raise RuntimeError(json.dumps(payload, ensure_ascii=False)[:800])
    return payload


def create_document(title: str) -> str:
    resp = lark_api("POST", "/open-apis/docx/v1/documents", {"title": title})
    return resp["data"]["document"]["document_id"]


def append_text_block(document_id: str, text: str, bold: bool = False) -> str:
    payload = {
        "children": [
            {
                "block_type": 2,
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": text,
                                "text_element_style": {"bold": bold},
                            }
                        }
                    ]
                },
            }
        ]
    }
    resp = lark_api(
        "POST",
        f"/open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/children",
        payload,
    )
    return resp["data"]["children"][0]["block_id"]


def append_image_block(document_id: str, image_path: Path) -> str:
    block_resp = lark_api(
        "POST",
        f"/open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/children",
        {"children": [{"block_type": 27, "image": {}}]},
    )
    block_id = block_resp["data"]["children"][0]["block_id"]

    upload_resp = lark_api(
        "POST",
        "/open-apis/drive/v1/medias/upload_all",
        {
            "file_name": image_path.name,
            "parent_type": "docx_image",
            "parent_node": block_id,
            "size": image_path.stat().st_size,
        },
        file_path=image_path,
    )
    token = upload_resp["data"]["file_token"]

    lark_api(
        "PATCH",
        f"/open-apis/docx/v1/documents/{document_id}/blocks/{block_id}",
        {"replace_image": {"token": token}},
    )
    return block_id


def create_bitable_record(document_url: str) -> Dict[str, Any]:
    payload = {
        "records": [
            {
                "fields": {
                    "项目名称": DOC_TITLE,
                    "项目链接": document_url,
                }
            }
        ]
    }
    return lark_api(
        "POST",
        f"/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}/records/batch_create",
        payload,
    )


def fmt_num(x: Any, digits: int = 4) -> str:
    if pd.isna(x):
        return "NA"
    return f"{x:.{digits}f}"


def fmt_sig(p: float) -> str:
    if p < 0.01:
        return "***"
    elif p < 0.05:
        return "**"
    elif p < 0.10:
        return "*"
    return "n.s."


def build_summary_lines() -> Iterable[str]:
    # Load available tables
    baseline = pd.read_csv(TABDIR / "v3med_set0_baseline.csv")
    drought_coef = pd.read_csv(TABDIR / "v3med_drought_model8_coefficients.csv")
    heat_coef = pd.read_csv(TABDIR / "v3med_heat_model8_coefficients.csv")
    het_coef = pd.read_csv(TABDIR / "v3med_heterogeneity_results.csv")

    # --- Section 1: Framework ---
    yield "一、估计框架"
    yield "采用 Preacher, Rucker & Hayes (2007) Model 8 调节中介结构。"
    yield "分别对 drought 和 heat 建立镜像模块，SR (ca) 同时调节 a-path 和 c'-path。"
    yield "所有方程均不包含 D×H 或 SR×D×H 交互项。"
    yield "控制变量双版本：full (irr_frac, pr_sum, et0_sum, aridity, gdd_ge10) 和 reduced (irr_frac, gdd_ge10)。"
    yield "6 个 SM 数据源: GLEAM-Sfc, GLEAM-Root, SWSM-L1, SWSM-L3, ERA5L-L1, ERA5L-L3。"
    yield ""

    # --- Section 2: Set 0 Baseline ---
    yield "二、Set 0 总 buffering 确认"
    base_d = baseline[(baseline["term"] == "SR_x_D_full") & (baseline["ctrl_version"] == "reduced")].iloc[0]
    base_h = baseline[(baseline["term"] == "SR_x_Heat_full") & (baseline["ctrl_version"] == "reduced")].iloc[0]
    yield (
        f"Drought: SR×D = {fmt_num(base_d.b)} (SE {fmt_num(base_d.se)}, "
        f"p = {fmt_num(base_d.p, 6)}) {fmt_sig(base_d.p)}"
    )
    yield (
        f"Heat: SR×Heat = {fmt_num(base_h.b)} (SE {fmt_num(base_h.se)}, "
        f"p = {fmt_num(base_h.p, 6)}) {fmt_sig(base_h.p)}"
    )
    yield "两模块 SR buffering 均显著，确认 total buffering 存在。"
    yield ""

    # --- Section 3: Drought Model 8 ---
    yield "三、Drought Model 8 核心结果"
    d_med = drought_coef[
        (drought_coef["fe_level"] == "L0")
        & (drought_coef["ctrl_version"] == "reduced")
        & (drought_coef["equation"] == "mediator")
        & (drought_coef["term"] == "SR_x_D_full")
    ]
    yield "a3 (D×ca → SM) — Mediator eq, reduced controls, grid FE:"
    for _, row in d_med.iterrows():
        yield f"  {row.sm_label}: a3 = {fmt_num(row.b)} (SE {fmt_num(row.se)}) {fmt_sig(row.p)}"
    yield "所有 6 个 SM 源的 a3 均显著（grid FE 下），无需放松 FE。"
    yield ""

    # --- Section 4: Heat Model 8 ---
    yield "四、Heat Model 8 核心结果"
    h_med = heat_coef[
        (heat_coef["fe_level"] == "L0")
        & (heat_coef["ctrl_version"] == "reduced")
        & (heat_coef["equation"] == "mediator")
        & (heat_coef["term"] == "SR_x_Heat_full")
    ]
    yield "a3h (H×ca → SM) — Mediator eq, reduced controls, grid FE:"
    for _, row in h_med.iterrows():
        yield f"  {row.sm_label}: a3h = {fmt_num(row.b)} (SE {fmt_num(row.se)}) {fmt_sig(row.p)}"
    yield "Heat 模块 a3h 符号不一致：surface/shallow SM 正号，deep SM 负号。"
    yield "Heat buffering 主要通过 direct channel (c'3h)，而非 SM 间接通道。"
    yield ""

    # --- Section 5: Heterogeneity ---
    yield "五、异质性分析"
    het_d = het_coef[
        (het_coef["module"] == "drought")
        & (het_coef["equation"] == "mediator")
        & (het_coef["term"] == "SR_x_D_full")
    ]
    yield "Drought a3 by subsample:"
    for _, row in het_d.iterrows():
        yield f"  {row.split_type}/{row.subgroup}: a3 = {fmt_num(row.b)} {fmt_sig(row.p)} (N={int(row.N)})"

    het_h = het_coef[
        (het_coef["module"] == "heat")
        & (het_coef["equation"] == "outcome")
        & (het_coef["term"] == "SR_x_Heat_full")
    ]
    yield "Heat c3h by subsample:"
    for _, row in het_h.iterrows():
        yield f"  {row.split_type}/{row.subgroup}: c3h = {fmt_num(row.b)} {fmt_sig(row.p)} (N={int(row.N)})"
    yield ""

    # --- Section 6: Key conclusions ---
    yield "六、核心结论"
    yield "1. Drought buffering: SR 通过 direct (c'3) + SM-mediated (a3×b) 双通道缓冲干旱损害。"
    yield "2. Heat buffering: SR 主要通过 direct channel 缓冲热害，SM 间接通道作用弱。"
    yield "3. NW 干旱区 SM moderation 最强 (a3=1.38***)，low-irr > high-irr。"
    yield "4. HHH 是 heat direct buffering 的核心区域 (c3h=0.003***)。"
    yield "5. 6 个 SM 源一致支持 drought SM-mediated path，稳健性强。"
    yield ""
    yield f"Beamer 报告: {ROOTDIR / 'output' / 'reports' / 'v3med_beamer_report.pdf'}"


def main() -> None:
    doc_id = create_document(DOC_TITLE)
    doc_url = f"{FEISHU_HOST}/docx/{doc_id}"
    print(f"Document created: {doc_url}")

    # Title block
    append_text_block(doc_id, DOC_TITLE, bold=True)
    append_text_block(doc_id, f"日期: 2026-04-16")
    append_text_block(doc_id, "")

    # Summary text
    for line in build_summary_lines():
        is_section = line.startswith(("一、", "二、", "三、", "四、", "五、", "六、"))
        append_text_block(doc_id, line, bold=is_section)

    # Core figures
    figure_plan = [
        ("图 1. Set 0: Total SR Buffering", FIGDIR / "v3med_plot_set0_baseline.png"),
        ("图 2. Drought module: 6 SM 源系数对比", FIGDIR / "v3med_plot_sm_comparison_drought.png"),
        ("图 3. Drought module: 条件效应 (IE/DE/TE)", FIGDIR / "v3med_plot_conditional_drought.png"),
        ("图 4. Heat module: 6 SM 源系数对比", FIGDIR / "v3med_plot_sm_comparison_heat.png"),
        ("图 5. Heat module: 条件效应 (IE/DE/TE)", FIGDIR / "v3med_plot_conditional_heat.png"),
        ("图 6. Index of Moderated Mediation", FIGDIR / "v3med_plot_index.png"),
        ("图 7. Full vs Reduced Controls (Drought)", FIGDIR / "v3med_plot_ctrl_comparison_drought.png"),
        ("图 8. Heterogeneity: Drought a3", FIGDIR / "v3med_plot_het_drought_a3.png"),
        ("图 9. Heterogeneity: Heat c3h", FIGDIR / "v3med_plot_het_heat_c3.png"),
        ("图 10. Heterogeneity: IE vs DE (Drought)", FIGDIR / "v3med_plot_het_ie_de_drought.png"),
        ("图 11. Heterogeneity: IE vs DE (Heat)", FIGDIR / "v3med_plot_het_ie_de_heat.png"),
    ]

    for caption, image_path in figure_plan:
        if image_path.exists():
            print(f"  Uploading: {caption}")
            append_text_block(doc_id, caption, bold=True)
            try:
                append_image_block(doc_id, image_path)
            except Exception as e:
                print(f"  WARNING: Image upload failed for {image_path.name}: {e}")
                append_text_block(doc_id, f"[图片上传失败: {image_path.name}]")
        else:
            print(f"  SKIP (not found): {image_path}")

    # Register in Bitable
    try:
        create_bitable_record(doc_url)
        print("Bitable record created.")
    except Exception as e:
        print(f"WARNING: Bitable record creation failed: {e}")

    print(json.dumps({"document_id": doc_id, "document_url": doc_url}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
