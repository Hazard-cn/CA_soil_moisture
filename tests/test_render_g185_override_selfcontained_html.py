"""Contract tests for the G185 standalone HTML formatter."""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import re
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/python/render_g185_override_selfcontained_html.py"
SOURCE = ROOT / "docs/results/g185-old-method-unified-override-v1/report.md"
OUTPUT = ROOT / "docs/results/g185-old-method-unified-override-v1/report.html"

SPEC = importlib.util.spec_from_file_location("g185_html_renderer", SCRIPT)
assert SPEC and SPEC.loader
RENDERER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDERER)


class ReportHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text: list[str] = []
        self.images: list[dict[str, str]] = []
        self.tables = 0
        self.headings: list[str] = []
        self._heading_depth = 0
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"style", "script"}:
            self._ignored_depth += 1
        attr_map = {key: value or "" for key, value in attrs}
        if tag == "img":
            self.images.append(attr_map)
            self.text.append(attr_map.get("alt", ""))
        if tag == "table":
            self.tables += 1
        if tag in {"h1", "h2", "h3"}:
            self._heading_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"style", "script"}:
            self._ignored_depth -= 1
        if tag in {"h1", "h2", "h3"}:
            self._heading_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth and data.strip():
            self.text.append(data)
            if self._heading_depth:
                self.headings.append(data.strip())


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def markdown_line_payload(line: str) -> str:
    value = line.strip()
    if not value or value in {r"\[", r"\]"} or re.match(r"^\|(?:\s*:?-+:?\s*\|)+$", value):
        return ""
    if value.startswith("!["):
        match = re.match(r"^!\[([^]]*)\]", value)
        return match.group(1) if match else ""
    value = re.sub(r"^#{1,6}\s+", "", value)
    value = re.sub(r"^-\s+", "", value)
    value = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("|", " ").replace("`", "").replace("*", "")
    return normalize_text(value)


class TestG185SelfContainedHTML(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.markdown_bytes = SOURCE.read_bytes()
        cls.markdown = cls.markdown_bytes.decode("utf-8")
        cls.html_bytes = OUTPUT.read_bytes()
        cls.html = cls.html_bytes.decode("utf-8")
        cls.parser = ReportHTMLParser()
        cls.parser.feed(cls.html)

    def test_source_identity_and_deterministic_output(self) -> None:
        self.assertEqual(hashlib.sha256(self.markdown_bytes).hexdigest(), RENDERER.EXPECTED_SOURCE_SHA256)
        rendered_a = RENDERER.render_document(self.markdown, SOURCE.parent, ROOT).encode("utf-8")
        rendered_b = RENDERER.render_document(self.markdown, SOURCE.parent, ROOT).encode("utf-8")
        self.assertEqual(rendered_a, rendered_b)
        self.assertEqual(self.html_bytes, rendered_a)
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "report.html"
            digest = RENDERER.render_file(SOURCE, candidate, ROOT)
            self.assertEqual(candidate.read_bytes(), self.html_bytes)
            self.assertEqual(digest, hashlib.sha256(self.html_bytes).hexdigest())

    def test_standalone_resources_and_path_safety(self) -> None:
        self.assertEqual(self.html.count("data:image/png;base64,"), 3)
        self.assertNotIn("file://", self.html.lower())
        self.assertNotRegex(self.html, r"(?<![A-Za-z])[A-Za-z]:[\\/]")
        self.assertNotIn("<link", self.html.lower())
        self.assertNotIn("<script", self.html.lower())
        self.assertIn("<style>", self.html)
        self.assertEqual(len(self.parser.images), 3)
        for image in self.parser.images:
            self.assertTrue(image["src"].startswith("data:image/png;base64,"))

    def test_embedded_png_hashes_match_reviewed_inputs(self) -> None:
        expected_paths = [
            ROOT / "temp/2026-07-15_g185_old_method_unified_override_v1/figures/fig1_national_iede.png",
            ROOT / "temp/2026-07-15_g185_old_method_unified_override_v1/figures/fig2_core_linear_curves.png",
            ROOT / "temp/2026-07-15_g185_old_method_unified_override_v1/figures/fig3_five_zone_iede.png",
        ]
        embedded_hashes = {
            hashlib.sha256(base64.b64decode(image["src"].split(",", 1)[1])).hexdigest()
            for image in self.parser.images
        }
        expected_hashes = {hashlib.sha256(path.read_bytes()).hexdigest() for path in expected_paths}
        self.assertEqual(embedded_hashes, expected_hashes)

    def test_structure_core_values_and_dois(self) -> None:
        visible = normalize_text(" ".join(self.parser.text))
        self.assertIn("秸秆还田采用强度与中国玉米极端胁迫损失斜率", visible)
        for value in ("0.5768", "1.1580", "1.1464", "84.1921%", "1,683次", "1,999次"):
            self.assertIn(value, visible)
        for doi in (
            "10.1037/a0020761",
            "10.1038/s43016-021-00341-6",
            "10.1038/s41467-020-18631-1",
            "10.1038/s43016-022-00592-x",
            "10.1097/EDE.0000000000000596",
        ):
            self.assertIn(doi, self.html)
        self.assertEqual(self.parser.tables, 6)
        self.assertEqual(sum(1 for heading in self.parser.headings if heading.startswith("图")), 0)
        self.assertIn("完整15项主要多重检验", self.parser.headings)

    def test_every_markdown_content_line_is_visible(self) -> None:
        visible = re.sub(r"\s+", "", " ".join(self.parser.text)).replace("本地制品", "")
        missing: list[tuple[int, str]] = []
        for line_number, line in enumerate(self.markdown.splitlines(), start=1):
            payload = markdown_line_payload(line)
            if payload and re.sub(r"\s+", "", payload) not in visible:
                missing.append((line_number, payload))
        self.assertEqual(missing, [], f"Markdown content not visible in HTML: {missing[:5]}")

    def test_local_temp_links_are_labelled(self) -> None:
        remaining_local_links = re.findall(r'<a href="([^"]*?/temp/[^"]*)"', self.html)
        self.assertEqual(len(remaining_local_links), 4)
        self.assertEqual(self.html.count('class="local-artifact-label"'), 4)
        self.assertEqual(self.html.count("本地制品"), 4)


if __name__ == "__main__":
    unittest.main()
