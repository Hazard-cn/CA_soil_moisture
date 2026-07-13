"""Read a Zotero sqlite backup and screen papers for SR story direction review."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import defaultdict
from html import unescape
from pathlib import Path

import pandas as pd


PROJ = Path("C:/YangSu/00_Project/CA_mechanism/regression_SR")
DEFAULT_DB = Path(
    "C:/Users/Lenovo/Zotero/zotero.sqlite.codex-backup-20260618-152113"
)
OUT_DIR = PROJ / "temp/2026-06-18_zotero_story_direction"
REPORT = PROJ / "quality_reports/2026-06-18_zotero_story_direction_review.md"

RELEVANT_COLLECTION_HINTS = {
    "ca_mechanism",
    "dataset",
    "soil moisture",
    "yield",
    "气象",
    "干旱",
    "高温",
    "作物",
    "老师新补充",
    "introduction",
    "reference",
    "refererence",
    "老师给的文献",
    "ca adoption",
    "conservation practice adoption",
}

KEYWORD_GROUPS = {
    "sr_ca": [
        "straw",
        "residue",
        "residues",
        "retention",
        "return",
        "returning",
        "mulch",
        "mulching",
        "conservation agriculture",
        "no-till",
        "no till",
        "minimum till",
        "tillage",
        "cover crop",
    ],
    "climate_stress": [
        "drought",
        "heat",
        "heatwave",
        "hot",
        "dry",
        "compound",
        "concurrent",
        "aridity",
        "atmospheric aridity",
        "vapor pressure deficit",
        "vpd",
        "flood",
        "climate change",
        "warming",
    ],
    "water_sm": [
        "soil moisture",
        "water",
        "irrigation",
        "rainfed",
        "groundwater",
        "evapotranspiration",
        "land-atmosphere",
        "land atmosphere",
    ],
    "crop_yield": [
        "maize",
        "corn",
        "crop",
        "crops",
        "yield",
        "agriculture",
        "agricultural",
        "breadbasket",
        "nitrogen",
    ],
    "region_adaptation": [
        "china",
        "regional",
        "region",
        "adaptation",
        "adaptive",
        "dryland",
        "semi-arid",
        "semiarid",
        "arid",
        "north china",
        "climate zone",
    ],
}

THEME_RULES = {
    "compound_climate_risk": ["compound", "concurrent", "drought", "heat", "heatwave", "breadbasket"],
    "water_mediated_buffering": ["soil moisture", "water", "irrigation", "rainfed", "groundwater", "land-atmosphere", "aridity"],
    "conservation_agriculture_sr": ["straw", "residue", "conservation agriculture", "mulch", "no-till", "tillage"],
    "adaptation_region": ["adaptation", "regional", "region", "china", "cultivar", "dryland", "semiarid"],
    "boundary_or_tradeoff": ["environmental impacts", "nitrogen", "flood", "pest", "weed", "disease", "losses"],
}


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def connect_readonly(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def collection_paths(con: sqlite3.Connection) -> tuple[dict[int, str], pd.DataFrame]:
    collections = pd.read_sql_query(
        """
        select collectionID, collectionName, parentCollectionID, key
        from collections
        order by collectionName
        """,
        con,
    )
    by_id = {
        int(row.collectionID): row
        for row in collections.itertuples(index=False)
    }

    def resolve(collection_id: int) -> str:
        parts: list[str] = []
        current = collection_id
        seen: set[int] = set()
        while current and current not in seen and current in by_id:
            seen.add(current)
            row = by_id[current]
            parts.append(str(row.collectionName))
            current = (
                int(row.parentCollectionID)
                if pd.notna(row.parentCollectionID)
                else 0
            )
        return " / ".join(reversed(parts))

    paths = {cid: resolve(cid) for cid in by_id}
    collections["path"] = collections["collectionID"].map(paths)
    return paths, collections


def field_map(con: sqlite3.Connection) -> dict[str, int]:
    return {
        str(name): int(fid)
        for fid, name in con.execute("select fieldID, fieldName from fields")
    }


def item_metadata(con: sqlite3.Connection) -> pd.DataFrame:
    fids = field_map(con)
    wanted = [
        "title",
        "abstractNote",
        "DOI",
        "date",
        "publicationTitle",
        "url",
        "extra",
        "citationKey",
        "language",
    ]
    field_select = []
    for field in wanted:
        field_select.append(
            f"max(case when f.fieldName = '{field}' then v.value end) as {field}"
        )
    query = f"""
    select
        i.itemID,
        i.key as item_key,
        it.typeName as item_type,
        i.dateAdded,
        i.dateModified,
        {', '.join(field_select)}
    from items i
    join itemTypes it on i.itemTypeID = it.itemTypeID
    left join itemData d on d.itemID = i.itemID
    left join fields f on f.fieldID = d.fieldID
    left join itemDataValues v on v.valueID = d.valueID
    where it.typeName not in ('attachment', 'note', 'annotation')
    group by i.itemID
    """
    frame = pd.read_sql_query(query, con)
    for col in wanted:
        if col not in frame:
            frame[col] = ""
        frame[col] = frame[col].map(clean_text)

    creators = pd.read_sql_query(
        """
        select ic.itemID, ic.orderIndex, c.firstName, c.lastName, ct.creatorType
        from itemCreators ic
        join creators c on c.creatorID = ic.creatorID
        join creatorTypes ct on ct.creatorTypeID = ic.creatorTypeID
        order by ic.itemID, ic.orderIndex
        """,
        con,
    )
    creator_map: dict[int, list[str]] = defaultdict(list)
    for row in creators.itertuples(index=False):
        name = " ".join(
            part for part in [clean_text(row.firstName), clean_text(row.lastName)] if part
        )
        if name:
            creator_map[int(row.itemID)].append(name)
    frame["creators"] = frame["itemID"].map(
        lambda item_id: "; ".join(creator_map.get(int(item_id), []))
    )

    tags = pd.read_sql_query(
        """
        select it.itemID, t.name
        from itemTags it
        join tags t on t.tagID = it.tagID
        order by t.name
        """,
        con,
    )
    tag_map: dict[int, list[str]] = defaultdict(list)
    for row in tags.itertuples(index=False):
        tag_map[int(row.itemID)].append(clean_text(row.name))
    frame["tags"] = frame["itemID"].map(
        lambda item_id: "; ".join(sorted(set(tag_map.get(int(item_id), []))))
    )

    paths, _ = collection_paths(con)
    coll = pd.read_sql_query(
        "select collectionID, itemID from collectionItems",
        con,
    )
    collection_map: dict[int, list[str]] = defaultdict(list)
    for row in coll.itertuples(index=False):
        collection_map[int(row.itemID)].append(paths.get(int(row.collectionID), ""))
    frame["collections"] = frame["itemID"].map(
        lambda item_id: "; ".join(sorted(set(collection_map.get(int(item_id), []))))
    )

    notes = pd.read_sql_query(
        """
        select parentItemID as itemID, note
        from itemNotes
        where parentItemID is not null
        """,
        con,
    )
    note_map: dict[int, list[str]] = defaultdict(list)
    for row in notes.itertuples(index=False):
        note_map[int(row.itemID)].append(clean_text(row.note))
    frame["child_notes"] = frame["itemID"].map(
        lambda item_id: " || ".join(note_map.get(int(item_id), []))
    )

    attachments = pd.read_sql_query(
        """
        select parentItemID as itemID, count(*) as attachment_count
        from itemAttachments
        where parentItemID is not null
        group by parentItemID
        """,
        con,
    )
    attach_map = {
        int(row.itemID): int(row.attachment_count)
        for row in attachments.itertuples(index=False)
    }
    frame["attachment_count"] = frame["itemID"].map(
        lambda item_id: attach_map.get(int(item_id), 0)
    )

    frame["citation_key"] = frame["citationKey"]
    missing = frame["citation_key"].eq("")
    frame.loc[missing, "citation_key"] = frame.loc[missing, "extra"].str.extract(
        r"(?i)citation key\s*:\s*([^\s;]+)", expand=False
    ).fillna("")
    return frame


def year_from_date(value: str) -> int | None:
    match = re.search(r"(19|20)\d{2}", value or "")
    if not match:
        return None
    return int(match.group(0))


def score_items(items: pd.DataFrame) -> pd.DataFrame:
    scored = items.copy()
    text_columns = [
        "title",
        "abstractNote",
        "publicationTitle",
        "tags",
        "collections",
        "child_notes",
    ]
    scored["screen_text"] = scored[text_columns].fillna("").agg(" ".join, axis=1)
    scored["screen_text_lower"] = scored["screen_text"].str.lower()
    scored["year"] = scored["date"].map(year_from_date)

    for group, terms in KEYWORD_GROUPS.items():
        pattern = "|".join(re.escape(term) for term in terms)
        scored[f"hit_{group}"] = scored["screen_text_lower"].str.contains(
            pattern, regex=True, na=False
        )
    scored["collection_relevant"] = scored["collections"].str.lower().map(
        lambda value: any(hint in value for hint in RELEVANT_COLLECTION_HINTS)
    )
    scored["keyword_group_count"] = scored[
        [f"hit_{group}" for group in KEYWORD_GROUPS]
    ].sum(axis=1)
    scored["relevance_score"] = (
        scored["keyword_group_count"] * 2
        + scored["collection_relevant"].astype(int) * 3
        + scored["hit_sr_ca"].astype(int) * 2
        + scored["hit_climate_stress"].astype(int) * 2
        + scored["hit_water_sm"].astype(int)
        + scored["hit_crop_yield"].astype(int)
    )

    def themes(text: str) -> str:
        found = []
        for theme, terms in THEME_RULES.items():
            if any(term in text for term in terms):
                found.append(theme)
        return "; ".join(found)

    scored["themes"] = scored["screen_text_lower"].map(themes)
    scored["included_for_review"] = (
        (scored["relevance_score"] >= 7)
        | (
            scored["collection_relevant"]
            & (scored["keyword_group_count"] >= 2)
        )
    )
    return scored


def compact_authors(value: str) -> str:
    names = [name.strip() for name in value.split(";") if name.strip()]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return f"{names[0]} et al."


def write_report(scored: pd.DataFrame, collections: pd.DataFrame, db_path: Path) -> None:
    included = scored.loc[scored["included_for_review"]].copy()
    included = included.sort_values(
        ["relevance_score", "dateAdded"],
        ascending=[False, False],
    )
    latest = scored.sort_values("dateAdded", ascending=False).head(20)
    collection_counts = (
        collections[["path"]]
        .assign(n=1)
        .groupby("path", as_index=False)
        .size()
        .sort_values("path")
    )

    def row_line(row: pd.Series) -> str:
        year = int(row["year"]) if pd.notna(row["year"]) else ""
        doi = row["DOI"] or ""
        ckey = row["citation_key"] or ""
        return (
            f"| {row['item_key']} | {ckey} | {year} | {clean_text(row['title'])} | "
            f"{compact_authors(row['creators'])} | {clean_text(row['publicationTitle'])} | "
            f"{doi} | {int(row['relevance_score'])} | {row['themes']} |"
        )

    lines = [
        "# Zotero 最新文献与故事方向复核",
        "",
        "日期：2026-06-18",
        "",
        "## 一、Corpus 摘要",
        "",
        f"- Zotero 备份库：`{db_path}`",
        f"- 非附件、非笔记、非 annotation 条目：{len(scored)}",
        f"- collection 数：{len(collections)}",
        f"- 纳入本轮故事复核的候选条目：{len(included)}",
        f"- 其中 2026-06-18 新增条目：{int(included['dateAdded'].astype(str).str.startswith('2026-06-18').sum())}",
        "",
        "筛选依据为 collection 命中和标题、摘要、标签、笔记中的关键词命中。该步骤只读本地 Zotero 备份，不做外部检索，也不写回 Zotero。",
        "",
        "## 二、最新新增条目概览",
        "",
        "| item key | citation key | year | title | first author | venue | DOI | relevance | themes |",
        "|---|---|---:|---|---|---|---|---:|---|",
    ]
    for _, row in latest.iterrows():
        lines.append(row_line(row))
    lines.extend(
        [
            "",
            "## 三、核心候选文献",
            "",
            "| item key | citation key | year | title | first author | venue | DOI | relevance | themes |",
            "|---|---|---:|---|---|---|---|---:|---|",
        ]
    )
    for _, row in included.head(40).iterrows():
        lines.append(row_line(row))
    lines.extend(
        [
            "",
            "## 四、机器筛选说明",
            "",
            "该报告是抽取与预筛选结果，不等同于最终文献综述。后续故事方向判断需要基于核心条目的摘要、DOI 和必要时的原文进一步人工校正。",
            "",
            "## 五、输出文件",
            "",
            "- `all_zotero_items.csv`：全部 metadata。",
            "- `screened_story_items.csv`：含筛选分数和主题标签的条目。",
            "- `included_story_items.csv`：本轮用于故事方向判断的候选条目。",
            "- `collection_inventory.csv`：collection 路径清单。",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(DEFAULT_DB))
    args = parser.parse_args()
    db_path = Path(args.db)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with connect_readonly(db_path) as con:
        paths, collections = collection_paths(con)
        items = item_metadata(con)
    scored = score_items(items)
    collections.to_csv(OUT_DIR / "collection_inventory.csv", index=False)
    items.to_csv(OUT_DIR / "all_zotero_items.csv", index=False)
    scored.drop(columns=["screen_text"], errors="ignore").to_csv(
        OUT_DIR / "screened_story_items.csv",
        index=False,
    )
    scored.loc[scored["included_for_review"]].drop(
        columns=["screen_text"], errors="ignore"
    ).to_csv(OUT_DIR / "included_story_items.csv", index=False)
    manifest = {
        "db_path": str(db_path),
        "n_items": int(len(items)),
        "n_collections": int(len(collections)),
        "n_included": int(scored["included_for_review"].sum()),
        "outputs": [
            "collection_inventory.csv",
            "all_zotero_items.csv",
            "screened_story_items.csv",
            "included_story_items.csv",
        ],
    }
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_report(scored, collections, db_path)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
