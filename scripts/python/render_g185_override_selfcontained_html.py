"""Render the reviewed G185 Markdown report as deterministic standalone HTML.

This formatter performs no analytical computation and does not alter the source
Markdown or the reviewed PNG figures. It uses only the Python standard library,
embeds the three PNG files as base64 data URIs, and keeps relative links to
untracked ``temp/`` tables clearly labelled as local artifacts.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = PROJECT_ROOT / "docs/results/g185-old-method-unified-override-v1/report.md"
DEFAULT_OUTPUT = PROJECT_ROOT / "docs/results/g185-old-method-unified-override-v1/report.html"
EXPECTED_SOURCE_SHA256 = "8767cf008d67550d9708e313f529dcc6cc1042768413300e8f8037ae9afd5e1a"

IMAGE_PATTERN = re.compile(r"^!\[([^]]*)\]\(([^)]+)\)$")
LINK_PATTERN = re.compile(r"\[([^]]+)\]\(([^)]+)\)")
CODE_PATTERN = re.compile(r"`([^`]+)`")
URL_PATTERN = re.compile(r"https?://[^\s<]+")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")
TABLE_DIVIDER_PATTERN = re.compile(r"^\|(?:\s*:?-+:?\s*\|)+$")
WINDOWS_ABSOLUTE_PATTERN = re.compile(r"^[A-Za-z]:[\\/]")


CSS = r"""
:root {
  color-scheme: light;
  --ink: #20262d;
  --muted: #5b6470;
  --rule: #d9dee5;
  --panel: #f6f8fa;
  --accent: #174a73;
  --link: #075e9d;
}
* { box-sizing: border-box; }
html { background: #ffffff; }
body {
  margin: 0;
  background: #ffffff;
  color: var(--ink);
  font-family: Arial, "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  font-size: 16px;
  line-height: 1.72;
}
article {
  width: min(1120px, calc(100% - 48px));
  margin: 0 auto;
  padding: 44px 0 72px;
}
h1, h2, h3 {
  color: var(--accent);
  line-height: 1.3;
  break-after: avoid-page;
}
h1 { margin: 0 0 24px; font-size: 2rem; }
h2 { margin: 2.3rem 0 0.85rem; padding-bottom: 0.25rem; border-bottom: 2px solid var(--rule); font-size: 1.42rem; }
h3 { margin: 1.8rem 0 0.65rem; font-size: 1.15rem; }
p { margin: 0.72rem 0; text-align: justify; }
ul { margin: 0.7rem 0 1.2rem; padding-left: 1.55rem; }
li { margin: 0.25rem 0; }
a { color: var(--link); text-decoration-thickness: 1px; text-underline-offset: 2px; overflow-wrap: anywhere; }
code {
  border-radius: 3px;
  background: var(--panel);
  padding: 0.08em 0.28em;
  font-family: Consolas, "Liberation Mono", monospace;
  font-size: 0.92em;
  overflow-wrap: anywhere;
}
.math-block {
  margin: 1rem auto;
  padding: 0.8rem 1rem;
  border-left: 3px solid #8ca8bf;
  background: #fbfcfd;
  overflow-x: auto;
  text-align: center;
}
.math-block code { display: block; background: transparent; white-space: pre-wrap; font-size: 0.96rem; }
.table-wrap { margin: 1rem 0 1.45rem; overflow-x: auto; border: 1px solid var(--rule); }
table { width: 100%; border-collapse: collapse; font-size: 0.9rem; font-variant-numeric: tabular-nums; }
th, td { padding: 0.52rem 0.62rem; border-right: 1px solid var(--rule); border-bottom: 1px solid var(--rule); vertical-align: top; }
th { background: #eef3f7; text-align: left; white-space: nowrap; }
tr:last-child td { border-bottom: 0; }
th:last-child, td:last-child { border-right: 0; }
.align-right { text-align: right; }
figure { margin: 1.25rem 0 0.55rem; break-inside: avoid-page; }
figure img { display: block; width: 100%; height: auto; background: #ffffff; border: 1px solid var(--rule); }
.figure-note { margin: 0.35rem 0 1.5rem; color: #3f4852; font-size: 0.91rem; text-align: left; }
.local-artifact-label {
  display: inline-block;
  margin-left: 0.35em;
  padding: 0.02em 0.42em;
  border: 1px solid #9aa6b2;
  border-radius: 999px;
  color: var(--muted);
  font-size: 0.74em;
  line-height: 1.45;
  vertical-align: 0.08em;
  white-space: nowrap;
}
@media (max-width: 720px) {
  article { width: min(100% - 24px, 1120px); padding-top: 24px; }
  body { font-size: 15px; }
  h1 { font-size: 1.6rem; }
  th, td { padding: 0.42rem; }
}
@media print {
  @page { size: A4; margin: 16mm; }
  body { font-size: 10.5pt; line-height: 1.55; color: #000000; }
  article { width: 100%; padding: 0; }
  a { color: #000000; text-decoration: none; }
  h2 { break-before: auto; }
  .table-wrap { overflow: visible; border-color: #888888; }
  table { font-size: 8pt; }
  figure { margin: 8mm 0 3mm; }
  .local-artifact-label { border-color: #777777; color: #333333; }
}
""".strip()


def sha256_bytes(payload: bytes) -> str:
    """Return a lowercase SHA-256 digest."""

    return hashlib.sha256(payload).hexdigest()


def _placeholder(store: list[str], fragment: str) -> str:
    token = f"@@G185HTML{len(store):04d}@@"
    store.append(fragment)
    return token


def _safe_href(raw_href: str) -> str:
    href = raw_href.strip()
    if href.lower().startswith("file:") or WINDOWS_ABSOLUTE_PATTERN.match(href):
        raise ValueError(f"Absolute or file URI is not allowed in HTML: {href}")
    return href


def render_inline(text: str) -> str:
    """Render the small inline Markdown subset used by the reviewed report."""

    fragments: list[str] = []

    def replace_link(match: re.Match[str]) -> str:
        label = render_inline(match.group(1))
        href = _safe_href(match.group(2))
        target = ' target="_blank" rel="noopener noreferrer"' if href.startswith(("http://", "https://")) else ""
        anchor = f'<a href="{html.escape(href, quote=True)}"{target}>{label}</a>'
        if "/temp/" in href.replace("\\", "/"):
            anchor += '<span class="local-artifact-label" title="仅在本地分析工作区可用">本地制品</span>'
        return _placeholder(fragments, anchor)

    value = LINK_PATTERN.sub(replace_link, text)

    def replace_code(match: re.Match[str]) -> str:
        return _placeholder(fragments, f"<code>{html.escape(match.group(1))}</code>")

    value = CODE_PATTERN.sub(replace_code, value)

    def replace_url(match: re.Match[str]) -> str:
        url = match.group(0)
        trailing = ""
        while url and url[-1] in ".,;，。；":
            trailing = url[-1] + trailing
            url = url[:-1]
        anchor = f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(url)}</a>'
        return _placeholder(fragments, anchor) + trailing

    value = URL_PATTERN.sub(replace_url, value)
    value = html.escape(value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", value)
    for index, fragment in enumerate(fragments):
        value = value.replace(f"@@G185HTML{index:04d}@@", fragment)
    return value


def _split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _table_html(lines: list[str]) -> str:
    header = _split_table_row(lines[0])
    aligners = _split_table_row(lines[1])
    rows = [_split_table_row(line) for line in lines[2:]]
    if len(header) != len(aligners) or any(len(row) != len(header) for row in rows):
        raise ValueError("Malformed Markdown table in reviewed report")
    classes = ["align-right" if marker.endswith(":") else "" for marker in aligners]
    head = "".join(
        f'<th{f" class=\"{classes[i]}\"" if classes[i] else ""}>{render_inline(cell)}</th>'
        for i, cell in enumerate(header)
    )
    body_rows = []
    for row in rows:
        cells = "".join(
            f'<td{f" class=\"{classes[i]}\"" if classes[i] else ""}>{render_inline(cell)}</td>'
            for i, cell in enumerate(row)
        )
        body_rows.append(f"<tr>{cells}</tr>")
    return (
        '<div class="table-wrap"><table><thead><tr>'
        + head
        + "</tr></thead><tbody>"
        + "".join(body_rows)
        + "</tbody></table></div>"
    )


def _image_html(line: str, source_dir: Path, project_root: Path) -> str:
    match = IMAGE_PATTERN.match(line)
    if not match:
        raise ValueError(f"Invalid image line: {line}")
    alt, raw_path = match.groups()
    if raw_path.startswith(("http://", "https://", "data:")):
        raise ValueError("Reviewed figures must be local PNG inputs before embedding")
    image_path = (source_dir / raw_path).resolve()
    project_resolved = project_root.resolve()
    if image_path.suffix.lower() != ".png" or not image_path.is_file():
        raise FileNotFoundError(image_path)
    if project_resolved not in image_path.parents:
        raise ValueError(f"Image escapes the project workspace: {image_path}")
    payload = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return (
        '<figure><img src="data:image/png;base64,'
        + payload
        + f'" alt="{html.escape(alt, quote=True)}"></figure>'
    )


def markdown_body_to_html(markdown_text: str, source_dir: Path, project_root: Path) -> str:
    """Convert the reviewed Markdown body without changing its content."""

    lines = markdown_text.splitlines()
    blocks: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue

        heading = HEADING_PATTERN.match(line)
        if heading:
            level = len(heading.group(1))
            blocks.append(f"<h{level}>{render_inline(heading.group(2))}</h{level}>")
            index += 1
            continue

        if stripped == r"\[":
            formula_lines: list[str] = []
            index += 1
            while index < len(lines) and lines[index].strip() != r"\]":
                formula_lines.append(lines[index])
                index += 1
            if index >= len(lines):
                raise ValueError("Unclosed display formula in reviewed report")
            formula = "\n".join(formula_lines)
            blocks.append(f'<div class="math-block"><code>{html.escape(formula)}</code></div>')
            index += 1
            continue

        if IMAGE_PATTERN.match(stripped):
            blocks.append(_image_html(stripped, source_dir, project_root))
            index += 1
            continue

        if stripped.startswith("|") and index + 1 < len(lines) and TABLE_DIVIDER_PATTERN.match(lines[index + 1].strip()):
            table_lines = [stripped, lines[index + 1].strip()]
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            blocks.append(_table_html(table_lines))
            continue

        if line.startswith("- "):
            items: list[str] = []
            while index < len(lines) and lines[index].startswith("- "):
                items.append(f"<li>{render_inline(lines[index][2:].strip())}</li>")
                index += 1
            blocks.append("<ul>" + "".join(items) + "</ul>")
            continue

        paragraph_lines = [stripped]
        index += 1
        while index < len(lines):
            candidate = lines[index]
            candidate_stripped = candidate.strip()
            if not candidate_stripped:
                break
            if (
                HEADING_PATTERN.match(candidate)
                or candidate_stripped == r"\["
                or IMAGE_PATTERN.match(candidate_stripped)
                or candidate.startswith("- ")
                or (
                    candidate_stripped.startswith("|")
                    and index + 1 < len(lines)
                    and TABLE_DIVIDER_PATTERN.match(lines[index + 1].strip())
                )
            ):
                break
            paragraph_lines.append(candidate_stripped)
            index += 1
        paragraph = " ".join(paragraph_lines)
        class_attr = ' class="figure-note"' if paragraph.startswith("*图") and paragraph.endswith("*") else ""
        blocks.append(f"<p{class_attr}>{render_inline(paragraph)}</p>")

    return "\n".join(blocks)


def render_document(markdown_text: str, source_dir: Path, project_root: Path) -> str:
    """Build deterministic UTF-8 standalone HTML bytes as text."""

    source_sha = sha256_bytes(markdown_text.encode("utf-8"))
    body = markdown_body_to_html(markdown_text, source_dir, project_root)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="source-sha256" content="{source_sha}">
<title>秸秆还田采用强度与中国玉米极端胁迫损失斜率：G185网格面板的同期土壤水分两方程分解</title>
<style>
{CSS}
</style>
</head>
<body>
<article>
{body}
</article>
</body>
</html>
"""


def render_file(source: Path, output: Path, project_root: Path) -> str:
    """Render a locked source file and return the output SHA-256 digest."""

    source_bytes = source.read_bytes()
    if source_bytes.startswith(b"\xef\xbb\xbf"):
        raise ValueError("Source Markdown must be UTF-8 without BOM")
    source_sha = sha256_bytes(source_bytes)
    if source.resolve() == DEFAULT_SOURCE.resolve() and source_sha != EXPECTED_SOURCE_SHA256:
        raise ValueError(f"Reviewed source hash mismatch: {source_sha}")
    markdown_text = source_bytes.decode("utf-8")
    document = render_document(markdown_text, source.parent, project_root)
    payload = document.encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)
    return sha256_bytes(payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    digest = render_file(args.source.resolve(), args.output.resolve(), args.project_root.resolve())
    print(f"Wrote {args.output.resolve()}")
    print(f"SHA256 {digest}")


if __name__ == "__main__":
    main()
