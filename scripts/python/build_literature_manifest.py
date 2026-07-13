import csv
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from difflib import SequenceMatcher
from http.client import IncompleteRead, RemoteDisconnected
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urljoin, urlparse, urlunparse
from urllib.request import Request, build_opener


ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = ROOT / "references" / "manifests" / "literature_seed.csv"
CSV_OUT = ROOT / "references" / "manifests" / "literature_code_manifest.csv"
MD_OUT = ROOT / "references" / "manifests" / "literature_code_manifest.md"
RAW_OUT = ROOT / "references" / "manifests" / "literature_code_manifest_raw.json"
REPORT_OUT = ROOT / "quality_reports" / "session_logs" / "2026-03-16_literature_code_download_report.md"
PAPERS_DIR = ROOT / "references" / "papers"
CODE_DIR = ROOT / "references" / "code"

CHECKED_ON = datetime.now().strftime("%Y-%m-%d")
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)
TIMEOUT = 30
REPOSITORY_DOMAINS = ("github.com", "gitlab.com", "zenodo.org", "osf.io", "codeocean.com")
DATA_DOMAINS = ("figshare.com", "dryad", "zenodo.org", "osf.io", "data.mendeley.com", "dataverse")
NETWORK_ERRORS = (HTTPError, URLError, TimeoutError, OSError, RemoteDisconnected, IncompleteRead)
CSV_FIELDS = [
    "paper_key",
    "source_ids",
    "title",
    "first_author",
    "year",
    "journal",
    "doi_corrected",
    "official_url",
    "fulltext_status",
    "best_pdf_url",
    "code_status",
    "code_url",
    "data_url",
    "license_or_notes",
    "checked_on",
]
MANUAL_OVERRIDES = {
    "2019_runge_detecting-and-quantifying-causal-associations-in": {
        "doi": "10.1126/sciadv.aau4996",
        "code_status": "author-related",
        "code_url": "https://github.com/jakobrunge/tigramite",
    },
    "2020_liu_soil-moisture-dominates-dryness-stress-on-ecosys": {
        "doi": "10.1038/s41467-020-15461-y",
    },
    "2021_lesk_stronger-temperature-moisture-couplings-exacerba": {
        "code_status": "author-related",
        "code_url": "https://github.com/clesk/couplings-heat-crops",
    },
    "2022_wang_associations-between-long-term-drought-and-diarr": {
        "doi": "10.1038/s41467-022-31291-7",
    },
    "2023_li_land-atmosphere-feedbacks-contribute-to-crop-fai": {
        "code_status": "official",
        "code_url": "https://github.com/h-cel/hamster",
    },
    "2024_bandopadhyay_disentangling-plant-and-environment-mediated-dri": {
        "code_status": "official",
        "code_url": "https://github.com/ShadeLab/PAPER_DroughtRhizobiome_Bandopadhyay_2023",
        "data_url": "https://datadryad.org/stash/share/vkqIFDwKkWd0_U36mKWee1z1-pb3Xha3ajrZ7x_HO2c",
    },
    "2024_hu_nutrient-induced-acidification-modulates-soil-bi": {
        "doi": "10.1038/s41467-024-47323-3",
    },
    "2024_qiu_optimizing-cover-crop-practices-as-a-sustainable": {
        "doi": "10.1038/s41467-024-50085-7",
    },
    "2024_tian_microbially-mediated-mechanisms-underlie-soil-ca": {
        "code_status": "not_found",
        "code_url": "",
    },
    "2025_zhang_irrigation-cooling-effect-reduced-by-water-savin": {
        "code_status": "author-related",
        "code_url": "https://github.com/Chao21/Watersaving_Irrigation_CN",
    },
    "2026_correia_best-practices-for-moving-from-correlation-to": {
        "doi": "10.1038/s41467-026-69878-z",
    },
}


def normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48]


def make_paper_key(row: dict) -> str:
    short_slug = slugify(" ".join(row["title"].split()[:7]))
    return f"{row['year']}_{row['first_author'].lower()}_{short_slug}"


def build_request(url: str, accept: str = "*/*") -> Request:
    return Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": accept,
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "close",
        },
    )


OPENER = build_opener()


def fetch_bytes(url: str, accept: str = "*/*") -> tuple[bytes, str]:
    request = build_request(url, accept=accept)
    with OPENER.open(request, timeout=TIMEOUT) as response:
        return response.read(), response.geturl()


def fetch_text(url: str, accept: str = "text/html,*/*;q=0.8") -> tuple[str, str]:
    payload, final_url = fetch_bytes(url, accept=accept)
    return payload.decode("utf-8", errors="replace"), final_url


def fetch_json(url: str) -> dict | None:
    try:
        text, _ = fetch_text(url, accept="application/json")
    except NETWORK_ERRORS:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def doi_metadata_lookup(doi: str) -> dict | None:
    encoded = quote_plus(doi)
    return fetch_json(f"https://api.crossref.org/works/{encoded}")


def extract_crossref_primary_url(message: dict) -> str:
    primary = message.get("resource", {}).get("primary", {}).get("URL", "")
    return primary or message.get("URL", "")


def extract_crossref_pdf_url(message: dict) -> str:
    for link in message.get("link", []) or []:
        if "pdf" in (link.get("content-type", "") or "").lower():
            return link.get("URL", "")
    return ""


def title_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, normalize_text(left), normalize_text(right)).ratio()


def crossref_lookup(title: str, year: str, journal: str) -> dict | None:
    query = quote_plus(title)
    url = f"https://api.crossref.org/works?rows=5&query.title={query}"
    data = fetch_json(url)
    if not data:
        return None

    best_item = None
    best_score = -1.0
    target_year = int(year)
    target_journal = normalize_text(journal)
    for item in data.get("message", {}).get("items", []):
        candidate_title = (item.get("title") or [""])[0]
        score = title_similarity(title, candidate_title)
        issued = item.get("issued", {}).get("date-parts", [[None]])[0][0]
        if issued == target_year:
            score += 0.15
        container = " ".join(item.get("container-title") or [])
        if target_journal and target_journal in normalize_text(container):
            score += 0.10
        if score > best_score:
            best_item = item
            best_score = score

    if best_item and best_score >= 0.78:
        return {
            "doi": best_item.get("DOI", ""),
            "official_url": best_item.get("URL", ""),
            "score": round(best_score, 3),
        }
    return None


def resolve_official_url(doi: str) -> str:
    metadata = doi_metadata_lookup(doi)
    if metadata:
        url = extract_crossref_primary_url(metadata.get("message", {}))
        if url:
            return url
    try:
        _, final_url = fetch_text(f"https://doi.org/{doi}")
        return final_url
    except NETWORK_ERRORS:
        metadata = doi_metadata_lookup(doi)
        if metadata:
            return metadata.get("message", {}).get("URL", "")
        raise


def find_pdf_url(html: str, official_url: str) -> str:
    meta_match = re.search(
        r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE,
    )
    if meta_match:
        return urljoin(official_url, meta_match.group(1))

    link_match = re.search(r'href=["\']([^"\']+\.pdf(?:\?[^"\']*)?)["\']', html, re.IGNORECASE)
    if link_match:
        return urljoin(official_url, link_match.group(1))
    return ""


def sanitize_official_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    if "nature.com" in parsed.netloc.lower() and parsed.path.startswith("/articles/"):
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))
    return url


def publisher_article_url_from_doi(doi: str) -> str:
    if doi.startswith("10.1038/"):
        suffix = doi.split("/", 1)[1]
        return f"https://www.nature.com/articles/{suffix}"
    if doi.startswith("10.1073/pnas."):
        return f"https://www.pnas.org/doi/full/{doi}"
    if doi.startswith("10.1126/"):
        return f"https://www.science.org/doi/{doi}"
    return ""


def publisher_pdf_candidate(doi: str, official_url: str) -> str:
    parsed = urlparse(official_url)
    if "nature.com" in parsed.netloc.lower() and parsed.path.startswith("/articles/"):
        return urlunparse((parsed.scheme, parsed.netloc, f"{parsed.path}.pdf", "", "", ""))
    if doi.startswith("10.1073/pnas."):
        return f"https://www.pnas.org/doi/pdf/{doi}"
    if doi.startswith("10.1126/"):
        return f"https://www.science.org/doi/pdf/{doi}"
    return ""


def probe_pdf(pdf_url: str) -> bool:
    try:
        request = build_request(pdf_url, accept="application/pdf,*/*;q=0.8")
        request.add_header("Range", "bytes=0-255")
        with OPENER.open(request, timeout=TIMEOUT) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            sample = response.read(32)
            return "pdf" in content_type or sample.startswith(b"%PDF")
    except NETWORK_ERRORS:
        return False


def extract_links(html: str, official_url: str) -> list[str]:
    raw_links = re.findall(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE)
    seen = set()
    cleaned = []
    for raw in raw_links:
        link = urljoin(official_url, raw.strip())
        if not link.startswith("http") or link in seen:
            continue
        seen.add(link)
        cleaned.append(link)
    return cleaned


def classify_links(links: list[str]) -> tuple[str, str]:
    code_candidates = []
    data_candidates = []
    for link in links:
        domain = urlparse(link).netloc.lower()
        if any(token in domain for token in REPOSITORY_DOMAINS):
            code_candidates.append(link)
        if any(token in domain for token in DATA_DOMAINS):
            data_candidates.append(link)
    return (code_candidates[0] if code_candidates else "", data_candidates[0] if data_candidates else "")


def download_binary(url: str, destination: Path) -> bool:
    try:
        payload, _ = fetch_bytes(url, accept="application/octet-stream,*/*;q=0.8")
    except NETWORK_ERRORS:
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    return True


def github_repo_root(link: str) -> str:
    parsed = urlparse(link)
    if "github.com" not in parsed.netloc.lower():
        return ""
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        return ""
    return f"https://github.com/{parts[0]}/{parts[1]}.git"


def clone_github(link: str, destination: Path) -> tuple[bool, str]:
    repo_url = github_repo_root(link)
    if not repo_url:
        return False, ""
    if destination.exists():
        return True, repo_url
    destination.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(destination)],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, repo_url


def build_markdown(rows: list[dict]) -> str:
    lines = ["# 文献与代码核查清单", "", f"- 生成日期: {CHECKED_ON}", f"- 唯一论文数: {len(rows)}", ""]
    for row in rows:
        lines.extend(
            [
                f"## {row['paper_key']}",
                "",
                f"- `source_ids`: {row['source_ids']}",
                f"- `title`: {row['title']}",
                f"- `first_author`: {row['first_author']}",
                f"- `year`: {row['year']}",
                f"- `journal`: {row['journal']}",
                f"- `doi_corrected`: {row['doi_corrected'] or '待核验'}",
                f"- `official_url`: {row['official_url'] or '未找到'}",
                f"- `fulltext_status`: {row['fulltext_status']}",
                f"- `best_pdf_url`: {row['best_pdf_url'] or '无'}",
                f"- `code_status`: {row['code_status']}",
                f"- `code_url`: {row['code_url'] or '无'}",
                f"- `data_url`: {row['data_url'] or '无'}",
                f"- `license_or_notes`: {row['license_or_notes'] or '无'}",
                f"- `checked_on`: {row['checked_on']}",
                "",
            ]
        )
    return "\n".join(lines)


def write_csv(rows: list[dict]) -> None:
    with CSV_OUT.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_report(rows: list[dict]) -> None:
    fulltext_and_code = [row for row in rows if row["fulltext_status"] != "official_page_only" and row["code_status"] != "not_found"]
    fulltext_only = [row for row in rows if row["fulltext_status"] != "official_page_only" and row["code_status"] == "not_found"]
    official_only = [row for row in rows if row["fulltext_status"] == "official_page_only"]
    no_public_code = [row for row in rows if row["code_status"] == "not_found"]

    lines = [
        "# 文献下载与代码核查短报告",
        "",
        f"- 日期: {CHECKED_ON}",
        f"- 唯一条目: {len(rows)}",
        f"- 全文+代码: {len(fulltext_and_code)}",
        f"- 仅全文: {len(fulltext_only)}",
        f"- 仅官方页: {len(official_only)}",
        f"- 无公开代码: {len(no_public_code)}",
        "",
        "## 全文+代码",
    ]
    lines.extend([f"- {row['paper_key']}" for row in fulltext_and_code] or ["- 无"])
    lines.extend(["", "## 仅全文"])
    lines.extend([f"- {row['paper_key']}" for row in fulltext_only] or ["- 无"])
    lines.extend(["", "## 仅官方页"])
    lines.extend([f"- {row['paper_key']}" for row in official_only] or ["- 无"])
    lines.extend(["", "## 无公开代码"])
    lines.extend([f"- {row['paper_key']}" for row in no_public_code] or ["- 无"])
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def cleanup_stale_code_dirs(rows: list[dict]) -> None:
    allowed = {row["paper_key"] for row in rows if row["code_status"] != "not_found"}
    for path in CODE_DIR.iterdir():
        if not path.is_dir():
            continue
        if path.name not in allowed:
            shutil.rmtree(path, ignore_errors=True)


def build_manifest(download: bool = False) -> int:
    rows = []
    raw_rows = []
    with SEED_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for seed_row in reader:
            row = {key: value.strip() for key, value in seed_row.items()}
            paper_key = make_paper_key(row)
            notes = []
            doi = row["doi_guess"]
            overrides = MANUAL_OVERRIDES.get(paper_key, {})
            if overrides.get("doi"):
                doi = overrides["doi"]
                notes.append("DOI from manual override")

            if not doi:
                lookup = crossref_lookup(row["title"], row["year"], row["journal"])
                if lookup:
                    doi = lookup["doi"]
                    notes.append(f"Crossref title match score={lookup['score']}")
                else:
                    notes.append("DOI unresolved by Crossref title search")

            official_url = ""
            html = ""
            metadata_message = {}
            if doi:
                metadata = doi_metadata_lookup(doi)
                metadata_message = metadata.get("message", {}) if metadata else {}
                try:
                    official_url = resolve_official_url(doi)
                except NETWORK_ERRORS:
                    official_url = f"https://doi.org/{doi}"
                    notes.append("DOI redirect unresolved; kept DOI URL")
            derived_official_url = publisher_article_url_from_doi(doi) if doi else ""
            if derived_official_url and (not official_url or "doi.org/" in official_url):
                official_url = derived_official_url
                notes.append("Official URL derived from DOI pattern")
            official_url = sanitize_official_url(official_url)

            if official_url:
                try:
                    html, official_url = fetch_text(official_url)
                    official_url = sanitize_official_url(official_url)
                except NETWORK_ERRORS:
                    notes.append("Official page fetch failed")

            pdf_url = find_pdf_url(html, official_url) if html else ""
            if not pdf_url and metadata_message:
                pdf_url = extract_crossref_pdf_url(metadata_message)
            if not pdf_url:
                pdf_url = publisher_pdf_candidate(doi, official_url)
            pdf_open = probe_pdf(pdf_url) if pdf_url else False
            if pdf_url and not pdf_open:
                notes.append("PDF link discovered but probe failed")

            links = extract_links(html, official_url) if html else []
            code_url, data_url = classify_links(links)
            code_url = overrides.get("code_url", code_url)
            data_url = overrides.get("data_url", data_url)
            code_status = overrides.get("code_status", "official" if code_url else "not_found")
            fulltext_status = "publisher_pdf_open" if pdf_open else "official_page_only"

            if official_url and "pmc.ncbi.nlm.nih.gov" in official_url:
                fulltext_status = "pmc_html_open"

            pdf_saved = False
            if download and pdf_open and pdf_url:
                pdf_saved = download_binary(pdf_url, PAPERS_DIR / f"{paper_key}.pdf")
                notes.append("PDF downloaded" if pdf_saved else "PDF download failed")
            elif download and pdf_url:
                pdf_saved = download_binary(pdf_url, PAPERS_DIR / f"{paper_key}.pdf")
                if pdf_saved:
                    notes.append("PDF downloaded after direct fetch")
            local_pdf_path = PAPERS_DIR / f"{paper_key}.pdf"
            if local_pdf_path.exists() and not pdf_saved:
                notes.append("Local PDF present from earlier successful download")
            if pdf_saved or local_pdf_path.exists():
                fulltext_status = "publisher_pdf_open"

            code_saved = False
            if download and code_url:
                if "github.com" in urlparse(code_url).netloc.lower():
                    code_saved, clone_url = clone_github(code_url, CODE_DIR / paper_key)
                    notes.append(f"GitHub cloned: {clone_url}" if code_saved else "GitHub clone failed")
                elif re.search(r"\.(zip|tar\.gz|tgz)$", code_url, re.IGNORECASE):
                    suffix = ".zip" if code_url.lower().endswith(".zip") else ".tar.gz"
                    code_saved = download_binary(code_url, CODE_DIR / f"{paper_key}{suffix}")
                    notes.append("Archive downloaded" if code_saved else "Archive download failed")
                else:
                    notes.append("Code link recorded but not auto-downloaded")

            manifest_row = {
                "paper_key": paper_key,
                "source_ids": row["source_ids"],
                "title": row["title"],
                "first_author": row["first_author"],
                "year": row["year"],
                "journal": row["journal"],
                "doi_corrected": doi,
                "official_url": official_url,
                "fulltext_status": fulltext_status,
                "best_pdf_url": pdf_url,
                "code_status": code_status,
                "code_url": code_url,
                "data_url": data_url,
                "license_or_notes": "; ".join(notes),
                "checked_on": CHECKED_ON,
            }
            rows.append(manifest_row)
            raw_rows.append({**manifest_row, "seed": row, "pdf_downloaded": pdf_saved, "code_downloaded": code_saved, "link_count": len(links)})

    rows.sort(key=lambda item: (item["year"], item["first_author"], item["title"]))
    RAW_OUT.write_text(json.dumps(raw_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    write_csv(rows)
    MD_OUT.write_text(build_markdown(rows), encoding="utf-8")
    write_report(rows)
    cleanup_stale_code_dirs(rows)

    missing_official = [row["paper_key"] for row in rows if not row["official_url"]]
    unresolved_doi = [row["paper_key"] for row in rows if not row["doi_corrected"]]
    if missing_official or unresolved_doi:
        print("MANIFEST_WARN")
        if missing_official:
            print("missing_official_url:", ",".join(missing_official))
        if unresolved_doi:
            print("unresolved_doi:", ",".join(unresolved_doi))
        return 2

    print(f"MANIFEST_OK rows={len(rows)} download={download}")
    return 0


def main(argv: list[str]) -> int:
    return build_manifest(download="--download" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
