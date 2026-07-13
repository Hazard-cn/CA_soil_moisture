"""
Render a Markdown-first GGCP10 full-family report into a Feishu document.

The Markdown file is the source of truth. This script only translates the
small Markdown subset used by the report into docx blocks, then replaces image
markers with local coefficient-plot PNGs.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional


ROOTDIR = Path(r"C:\YangSu\00_Project\CA_mechanism\regression_SR")
RUN_DIR = ROOTDIR / "temp" / "2026-05-18_ggcp10_harvarea_agg_v6gleambl_fullfamily"
FIG_DIR = RUN_DIR / "figures"
MD_PATH = RUN_DIR / "ggcp10_fullfamily_report.md"
DOC_URL_TXT = RUN_DIR / "ggcp10_fullfamily_feishu_url.txt"

LARK_CLI = [r"C:\Program Files\nodejs\npx.cmd", "--yes", "@larksuite/cli"]
HEADING_TYPES = {1: 3, 2: 4, 3: 5, 4: 6}

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
        if any(token in last_error for token in ("502", "Bad Gateway", "EOF")) and attempt < 5:
            time.sleep(attempt * 2)
            continue
        break
    raise RuntimeError(last_error[:1000])


def create_document(title: str) -> str:
    resp = lark_api("POST", "/open-apis/docx/v1/documents", {"title": title})
    return resp["data"]["document"]["document_id"]


def append_text_block(document_id: str, text: str, block_type: int = 2) -> None:
    text_key = {
        2: "text",
        3: "heading1",
        4: "heading2",
        5: "heading3",
        6: "heading4",
    }[block_type]
    payload = {
        "children": [
            {
                "block_type": block_type,
                text_key: {
                    "elements": [
                        {
                            "text_run": {
                                "content": text,
                                "text_element_style": {},
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


def strip_inline_markdown(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    return text


def iter_markdown_blocks(md_text: str):
    paragraph: list[str] = []
    for raw_line in md_text.splitlines():
        line = raw_line.strip()
        if not line:
            if paragraph:
                yield ("paragraph", " ".join(paragraph))
                paragraph = []
            continue
        if line.startswith("#"):
            if paragraph:
                yield ("paragraph", " ".join(paragraph))
                paragraph = []
            level = len(line) - len(line.lstrip("#"))
            yield ("heading", level, strip_inline_markdown(line[level:].strip()))
            continue
        if line.startswith("- "):
            if paragraph:
                yield ("paragraph", " ".join(paragraph))
                paragraph = []
            yield ("paragraph", "• " + strip_inline_markdown(line[2:].strip()))
            continue
        if line.startswith("FIG::"):
            if paragraph:
                yield ("paragraph", " ".join(paragraph))
                paragraph = []
            yield ("image_marker", line)
            continue
        paragraph.append(strip_inline_markdown(line))
    if paragraph:
        yield ("paragraph", " ".join(paragraph))


def marker_to_image(marker: str) -> Path:
    _, tag, path = marker.split("::")
    return FIG_DIR / f"v6gleambl_agg_{tag}_fig_{path}.png"


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


def render_markdown_to_doc(document_id: str, md_text: str) -> list[tuple[str, Path]]:
    markers: list[tuple[str, Path]] = []
    for block in iter_markdown_blocks(md_text):
        if block[0] == "heading":
            _, level, text = block
            if level == 1:
                continue
            append_text_block(document_id, text, HEADING_TYPES[min(level - 1, 4)])
        elif block[0] == "paragraph":
            _, text = block
            append_text_block(document_id, text)
        else:
            _, marker = block
            append_text_block(document_id, marker)
            markers.append((marker, marker_to_image(marker)))
    return markers


def main() -> None:
    md_text = MD_PATH.read_text(encoding="utf-8")
    title = md_text.splitlines()[0].removeprefix("# ").strip()
    document_id = create_document(title)
    markers = render_markdown_to_doc(document_id, md_text)
    for marker, image_path in markers:
        insert_image(document_id, marker, image_path)
    doc_url = f"https://vcn7opmi92n5.feishu.cn/docx/{document_id}"
    DOC_URL_TXT.write_text(doc_url, encoding="utf-8")
    print(doc_url)


if __name__ == "__main__":
    main()
