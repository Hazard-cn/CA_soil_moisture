"""
Helpers for deterministic Stata-safe variable aliases.
"""

import hashlib
import re
from datetime import date

import pandas as pd

from config import FULLNEW_SUFFIX, STATA_ALIAS_MARKDOWN_PATH, STATA_ALIAS_TABLE_PATH, WINDOW_SUFFIXES


SOURCE_ALIAS = {
    "gleam_smrz": "gsr",
    "gleam_sms": "gss",
    "swsm_l1": "sl1",
    "swsm_l3": "sl3",
    "era5l_swvl1": "e1",
    "era5l_swvl3": "e3",
    "smrz": "gsr",
    "sms": "gss",
    "pr_lt1": "pr1",
}

METRIC_ALIAS = {
    "drydays": "dd",
    "wetdays": "wd",
    "dryshare": "ds",
    "wetshare": "ws",
    "drydeficit": "ddf",
    "wetexcess": "wex",
    "hotdrydays": "hdy",
}

WINDOW_ALIAS = {
    "": "f",
    "_v3pre30": "p30",
    "_v3pm10": "v10",
    "_hepm10": "h10",
    "_v3he": "v3h",
    "_hema": "hma",
    "_fullnew": "fn",
}

VALID_STATA_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,31}$")


def split_window_suffix(col):
    """Split off known phenological window suffix."""
    suffixes = list(WINDOW_SUFFIXES[1:]) + [FULLNEW_SUFFIX]
    for suffix in sorted(suffixes, key=len, reverse=True):
        if col.endswith(suffix):
            return col[: -len(suffix)], WINDOW_ALIAS.get(suffix, WINDOW_ALIAS[""])
    return col, WINDOW_ALIAS[""]


def sanitize_stata_name(name):
    """Ensure a candidate alias uses valid Stata name characters."""
    alias = re.sub(r"[^A-Za-z0-9_]", "_", name.lower())
    alias = re.sub(r"_+", "_", alias).strip("_")
    if not alias or alias[0].isdigit():
        alias = f"v_{alias}"
    return alias[:32]


def fallback_alias(col):
    """Deterministic fallback alias for any unmatched long variable."""
    digest = hashlib.md5(col.encode("utf-8")).hexdigest()[:8]
    base = sanitize_stata_name(col)[:21]
    return f"x_{base}_{digest}"[:32]


def build_rule_alias(col):
    """Build a deterministic alias for supported long-name families."""
    col_base, win_code = split_window_suffix(col)

    match = re.match(
        r"^(dryshare|wetshare|drydeficit|wetexcess)_(pl|mz)_"
        r"(gleam_smrz|gleam_sms|swsm_l1|swsm_l3|era5l_swvl1|era5l_swvl3)_(?:le|ge)_p(\d+)$",
        col_base,
    )
    if match:
        metric, scope, source, pct = match.groups()
        return f"{METRIC_ALIAS[metric]}_{scope}_{SOURCE_ALIAS[source]}_p{pct}_{win_code}", "sm_state"

    match = re.match(
        r"^(drydays|wetdays|dryshare|wetshare|drydeficit|wetexcess)_"
        r"(gleam_smrz|gleam_sms|swsm_l1|swsm_l3|era5l_swvl1|era5l_swvl3)_(?:le|ge)_p(\d+)$",
        col_base,
    )
    if match:
        metric, source, pct = match.groups()
        return f"{METRIC_ALIAS[metric]}_bl_{SOURCE_ALIAS[source]}_p{pct}_{win_code}", "sm_state"

    match = re.match(
        r"^hotdrydays_ge(\d+)_(smrz|sms|swsm_l1|swsm_l3|era5l_swvl1|era5l_swvl3|pr_lt1)_p(\d+)$",
        col_base,
    )
    if match:
        thresh, source, pct = match.groups()
        return f"hdy_{SOURCE_ALIAS[source]}_t{thresh}_p{pct}_{win_code}", "hotdrydays"

    match = re.match(r"^mdduration_(dry|wet)_(gleam_smrz|gleam_sms)$", col_base)
    if match:
        side, source = match.groups()
        return f"mdd_{side[0]}_{SOURCE_ALIAS[source]}_{win_code}", "gleam_md_event"

    match = re.match(r"^mddurshare_(dry|wet)_(gleam_smrz|gleam_sms)$", col_base)
    if match:
        side, source = match.groups()
        return f"mds_{side[0]}_{SOURCE_ALIAS[source]}_{win_code}", "gleam_md_event"

    match = re.match(r"^mdseverity_(dry|wet)_(gleam_smrz|gleam_sms)$", col_base)
    if match:
        side, source = match.groups()
        return f"mdv_{side[0]}_{SOURCE_ALIAS[source]}_{win_code}", "gleam_md_event"

    match = re.match(r"^blduration_(dry|wet)_(gleam_smrz|gleam_sms)_p(\d+)$", col_base)
    if match:
        side, source, pct = match.groups()
        return f"bld_{side[0]}_{SOURCE_ALIAS[source]}_p{pct}_{win_code}", "gleam_window_baseline"

    match = re.match(r"^bldurshare_(dry|wet)_(gleam_smrz|gleam_sms)_p(\d+)$", col_base)
    if match:
        side, source, pct = match.groups()
        return f"bls_{side[0]}_{SOURCE_ALIAS[source]}_p{pct}_{win_code}", "gleam_window_baseline"

    match = re.match(r"^blseveritymean_(ddf|wex)_(gleam_smrz|gleam_sms)_p(\d+)$", col_base)
    if match:
        metric, source, pct = match.groups()
        return f"blm_{metric}_{SOURCE_ALIAS[source]}_p{pct}_{win_code}", "gleam_window_baseline"

    match = re.match(r"^blseveritysum_(ddf|wex)_(gleam_smrz|gleam_sms)_p(\d+)$", col_base)
    if match:
        metric, source, pct = match.groups()
        return f"blu_{metric}_{SOURCE_ALIAS[source]}_p{pct}_{win_code}", "gleam_window_baseline"

    return None, None


def build_stata_alias_map(columns):
    """Create deterministic original -> Stata alias mapping for a column list."""
    used = {}
    rows = []

    for col in columns:
        changed = len(col) > 32 or not VALID_STATA_RE.match(col)
        alias = col
        alias_family = "unchanged"
        alias_method = "identity"

        if changed:
            alias, alias_family = build_rule_alias(col)
            alias_method = "rule" if alias is not None else "fallback"
            if alias is None:
                alias_family = "fallback"
                alias = fallback_alias(col)

        alias = sanitize_stata_name(alias)
        if len(alias) > 32 or not VALID_STATA_RE.match(alias):
            alias = fallback_alias(col)
            alias_family = "fallback"
            alias_method = "fallback"

        if alias in used and used[alias] != col:
            digest = hashlib.md5(col.encode("utf-8")).hexdigest()[:6]
            alias = f"{alias[:25]}_{digest}"[:32]
            alias = sanitize_stata_name(alias)
            alias_family = "collision"
            alias_method = "collision_fix"

        used[alias] = col
        rows.append(
            {
                "original_name": col,
                "stata_name": alias,
                "changed": int(col != alias),
                "alias_family": alias_family,
                "alias_method": alias_method,
                "orig_len": len(col),
                "stata_len": len(alias),
            }
        )

    return pd.DataFrame(rows)


def write_alias_outputs(alias_df):
    """Write alias CSV and markdown outputs."""
    alias_df.to_csv(STATA_ALIAS_TABLE_PATH, index=False, encoding="utf-8-sig")

    changed_df = alias_df[alias_df["changed"] == 1].copy()
    changed_df = changed_df.sort_values(["alias_family", "original_name"])

    lines = []
    lines.append("# Stata Alias Map (V3)")
    lines.append("")
    lines.append(f"**Generated:** {date.today().isoformat()}  ")
    lines.append(f"**Total columns:** {len(alias_df)}  ")
    lines.append(f"**Renamed for Stata:** {int(alias_df['changed'].sum())}")
    lines.append("")
    lines.append("本表记录 `.dta` 导出时使用的 Stata-safe 变量名映射。`CSV/Parquet` 仍保留原始长变量名。")
    lines.append("")
    lines.append("## Alias Rules")
    lines.append("")
    lines.append("- SM state families: `dd/wd/ds/ws/ddf/wex` + `bl/pl/mz` + compressed source token + percentile + window code")
    lines.append("- `hotdrydays`: `hdy` + compressed source token + temperature threshold + percentile + window code")
    lines.append("- GLEAM rework: `mdd/mds/mdv` for md-event family and `bld/bls/blm/blu` for window-baseline family")
    lines.append("- Window codes: `f`, `p30`, `v10`, `h10`, `v3h`, `hma`, `fn`")
    lines.append("")
    lines.append("## Changed Variables")
    lines.append("")
    lines.append("| Original | Stata | Family | Method | Len(old) | Len(new) |")
    lines.append("|----------|-------|--------|--------|----------|----------|")
    for _, row in changed_df.iterrows():
        lines.append(
            f"| `{row['original_name']}` | `{row['stata_name']}` | {row['alias_family']} | "
            f"{row['alias_method']} | {row['orig_len']} | {row['stata_len']} |"
        )
    lines.append("")

    with open(STATA_ALIAS_MARKDOWN_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def build_variable_labels(alias_df):
    """Use original names as Stata variable labels for renamed columns."""
    labels = {}
    changed_df = alias_df[alias_df["changed"] == 1]
    for _, row in changed_df.iterrows():
        labels[row["stata_name"]] = row["original_name"][:80]
    return labels
