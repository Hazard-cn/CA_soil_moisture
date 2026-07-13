"""
Create a Feishu online document for the GGCP10 new-area GLEAM maize-zone
baseline results, then insert coefficient-plot images.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd


ROOTDIR = Path(r"C:\YangSu\00_Project\CA_mechanism\regression_SR")
RUN_DIR = ROOTDIR / "temp" / "2026-05-18_ggcp10_harvarea_agg_baseline_suite"
FOCUS_CSV = RUN_DIR / "ggcp10_core_baseline_focus_terms.csv"
ASSET_DIR = RUN_DIR / "feishu_maizezone_assets"
DOC_URL_TXT = RUN_DIR / "ggcp10_gleam_maizezone_feishu_url.txt"

DOC_TITLE = "GGCP10 新面积分支 - GLEAM maize-zone baseline 结果"
LARK_CLI = [r"C:\Program Files\nodejs\npx.cmd", "--yes", "@larksuite/cli"]

ENV = os.environ.copy()
ENV["MSYS_NO_PATHCONV"] = "1"
ENV["LARK_CLI_NO_PROXY"] = "1"
for proxy_key in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy"):
    ENV.pop(proxy_key, None)


def decode_output(raw: bytes) -> str:
    for enc in ("utf-8", "gbk"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def lark_api(method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    cmd = list(LARK_CLI) + ["api", method, path, "--as", "user"]
    if data is not None:
        cmd += ["--data", json.dumps(data, ensure_ascii=False)]

    last_error = ""
    for attempt in range(1, 6):
        result = subprocess.run(
            cmd,
            capture_output=True,
            shell=False,
            env=ENV,
            cwd=str(ROOTDIR),
            check=False,
        )
        stdout = decode_output(result.stdout)
        stderr = decode_output(result.stderr)
        if result.returncode == 0 and stdout.strip():
            payload = json.loads(stdout)
            if payload.get("code") in (0, None):
                return payload
            last_error = json.dumps(payload, ensure_ascii=False)
        else:
            last_error = stderr or stdout
        if "502" in last_error or "Bad Gateway" in last_error or "EOF" in last_error:
            time.sleep(attempt * 2)
            continue
        break
    raise RuntimeError(last_error[:1000])


def create_document(title: str) -> str:
    resp = lark_api("POST", "/open-apis/docx/v1/documents", {"title": title})
    return resp["data"]["document"]["document_id"]


def append_text(document_id: str, text: str, bold: bool = False) -> None:
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
    lark_api(
        "POST",
        f"/open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/children",
        payload,
    )


def fmt_sig(p: float) -> str:
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return "n.s."


def filtered_df() -> pd.DataFrame:
    df = pd.read_csv(FOCUS_CSV)
    keep_raw = df["mediator_type"].eq("raw_sm")
    keep_mz = df["threshold_scheme"].eq("maize_zone_state")
    df = df[keep_raw | keep_mz].copy()
    return df[df["sm_label"].isin(["GLEAM-Sfc", "GLEAM-Root"])].copy()


def pair_line(df: pd.DataFrame, mediator_type: str, hazard: str, equation: str, term: str) -> str:
    dd = df[
        (df["mediator_type"] == mediator_type)
        & (df["hazard"] == hazard)
        & (df["equation"] == equation)
        & (df["term"] == term)
    ].sort_values("sm_label")
    parts = [f"{r.sm_label} {r.b:+.4g} {fmt_sig(r.p)}" for r in dd.itertuples()]
    return "; ".join(parts)


def append_result_block(document_id: str, df: pd.DataFrame, mediator_type: str, title: str, variable_text: str, note: str) -> None:
    append_text(document_id, title, bold=True)
    append_text(document_id, variable_text)
    append_text(document_id, note)
    lines = []
    for hazard, label in [("drought", "Drought"), ("heat", "Heat"), ("hotdry", "HotDry")]:
        lines.extend(
            [
                label,
                f"a1: {pair_line(df, mediator_type, hazard, 'mediator', 'Main')}",
                f"a3: {pair_line(df, mediator_type, hazard, 'mediator', 'SR_x_Main')}",
                f"c1: {pair_line(df, mediator_type, hazard, 'outcome', 'Main')}",
                f"c3: {pair_line(df, mediator_type, hazard, 'outcome', 'SR_x_Main')}",
                f"b: {pair_line(df, mediator_type, hazard, 'outcome', 'M')}",
            ]
        )
    append_text(document_id, "\n".join(lines))
    for path in ["a1", "a3", "c1", "c3", "b"]:
        append_text(document_id, f"FIG::{mediator_type}::{path}")


def insert_image(document_id: str, marker: str, image_path: Path) -> None:
    rel_path = image_path.relative_to(ROOTDIR).as_posix()
    cmd = list(LARK_CLI) + [
        "docs",
        "+media-insert",
        "--as",
        "user",
        "--doc",
        document_id,
        "--file",
        rel_path,
        "--selection-with-ellipsis",
        marker,
        "--align",
        "center",
        "--width",
        "900",
    ]
    last_error = ""
    for attempt in range(1, 6):
        result = subprocess.run(
            cmd,
            capture_output=True,
            shell=False,
            env=ENV,
            cwd=str(ROOTDIR),
            check=False,
        )
        if result.returncode == 0:
            return
        last_error = decode_output(result.stderr) or decode_output(result.stdout)
        retryable = any(
            token in last_error
            for token in ("502", "Bad Gateway", "server time out error", "EOF")
        )
        if retryable and attempt < 5:
            time.sleep(attempt * 3)
            continue
        break
    raise RuntimeError(last_error[:1000])


def main() -> None:
    df = filtered_df()
    document_id = create_document(DOC_TITLE)

    append_text(document_id, DOC_TITLE, bold=True)
    append_text(document_id, "口径：只使用新面积分支；只看 GLEAM；状态变量只保留 maize-zone-state；当前只整理两条 baseline 方程，不包含 IE、DE 和异质性。")
    append_text(document_id, "1. 研究范围", bold=True)
    append_text(document_id, "样本 N = 62,018；外生灾害分为 Drought、Heat、HotDry；固定效应为 grid_id + year，标准误按 grid_id 聚类。")
    append_text(document_id, "2. 方程", bold=True)
    append_text(document_id, "M = a0 + a1·Hazard + a2·SR + a3·(SR×Hazard) + controls + FE\nln(Yield) = c0 + c1·Hazard + c2·SR + c3·(SR×Hazard) + b·M + controls + FE")
    append_text(document_id, "3. 为什么这版没有出现参考 PDF 里的 22 个 dry-state 指标", bold=True)
    append_text(
        document_id,
        "参考 PDF 使用的是 2026-04-23 新增的 dry-side metric family：mdduration_dry、mddurshare_dry、mdseverity_dry、"
        "blduration_dry、bldurshare_dry、blseveritymean_ddf、blseveritysum_ddf，并在 p10/p20 下展开成 22 个 spec cell。"
        "这套 family 在变量说明里被明确列为新增 GLEAM 指标，不属于 legacy pooled-state / maize-zone-state。"
    )
    append_text(
        document_id,
        "本次按“只用 maize-zone”执行时，dry-state 严格对应的只有 ds_mz_gsms 与 ds_mz_gsmrz 两个变量；"
        "因此若严格坚持 maize-zone，就不会同时出现那 22 个 dry-side 指标。前一版文档没有体现它们，是因为使用的是压缩后的 core baseline，而不是 v6gleambl_nomwet 的 full-family 结果。"
    )

    append_result_block(
        document_id,
        df,
        "raw_sm",
        "4. SM mean",
        "变量：gleam_sms_mean、gleam_smrz_mean。",
        "Drought 组最接近理论预期：a1 为负、a3 为正、c1 为负、b 为正，但 c3 在两层 GLEAM 下均为负。Heat 组中 a1 为负、a3 为负、b 为正，c1/c3 不显著。HotDry 组中 a1 为负、a3 主要为负、c1 为正、c3 不显著。",
    )
    append_result_block(
        document_id,
        df,
        "sm_dry_state",
        "5. SM drought state - maize-zone only",
        "变量：ds_mz_gsms、ds_mz_gsmrz。",
        "三类灾害的 a1 都为正、a3 都为负，说明 maize-zone dry-state 能稳定响应灾害及其与 SR 的交互；但 b 全部为正，与 dry-state 理论预期相反，Drought 的 c3 也主要为负。",
    )
    append_result_block(
        document_id,
        df,
        "sm_wet_state",
        "6. SM wet state - maize-zone only",
        "变量：ws_mz_gsms、ws_mz_gsmrz。",
        "wet-state 的方向更不稳定。Drought 与 Heat 的 a1 主要为正、a3 主要为负，HotDry 的 a1 也多为正、a3 为负；但 b 缺乏稳定方向，因此更适合作为补充变量。",
    )

    for mediator_type in ["raw_sm", "sm_dry_state", "sm_wet_state"]:
        for path in ["a1", "a3", "c1", "c3", "b"]:
            marker = f"FIG::{mediator_type}::{path}"
            insert_image(document_id, marker, ASSET_DIR / f"{mediator_type}_{path}.png")

    doc_url = f"https://vcn7opmi92n5.feishu.cn/docx/{document_id}"
    DOC_URL_TXT.write_text(doc_url, encoding="utf-8")
    print(doc_url)


if __name__ == "__main__":
    main()
