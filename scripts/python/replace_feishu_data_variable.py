"""
replace_feishu_data_variable.py
Purpose: Replace content of "4-Data and Variable" table in existing Feishu Base
         with the latest data_dictionary_v3.csv (855 records)
Target:  Base XsH1beeEMaMf0Os04IYcSz54nhh / Table tblig2Z0qGeiTHe7
Date:    2026-04-14

Field mapping (target <- CSV):
  Variable Name  <- Variable
  Label          <- Label_CN
  Unit           <- Unit
  Window         <- Window
  Range          <- Range
  Missing        <- Missing_pct  (formatted as "X.X%")
  type           <- Category
  Sources        <- Label_EN
  Link           <- Dtype
"""

import csv
import json
import subprocess
import sys
import os

# ── Config ──────────────────────────────────────────────────────────────
BASE_TOKEN = "XsH1beeEMaMf0Os04IYcSz54nhh"
TABLE_ID   = "tblig2Z0qGeiTHe7"
BASE_URL   = f"/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}"
CSV_PATH   = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "../../data_build/output/tables/data_dictionary_v3.csv")
LARK_CLI   = ["node",
              r"C:\Users\Lenovo\AppData\Roaming\npm\node_modules\@larksuite\cli\scripts\run.js"]
BATCH_SIZE = 20

env = os.environ.copy()
env["MSYS_NO_PATHCONV"] = "1"


# ── Helper ────────────────────────────────────────────────────────────────
def lark_api(method, path, data=None):
    cmd = list(LARK_CLI) + ["api", method, path, "--as", "user"]
    if data:
        cmd += ["--data", json.dumps(data, ensure_ascii=False)]
    result = subprocess.run(cmd, capture_output=True, env=env, shell=False)
    stdout = result.stdout.decode("utf-8", errors="replace")
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""
        return {"code": -1, "msg": (stderr or stdout)[:300]}


# ── Delete all existing records ───────────────────────────────────────────
def clear_table():
    print("Clearing existing records...")
    deleted = 0
    page_token = None

    while True:
        params = "?page_size=100"
        if page_token:
            params += f"&page_token={page_token}"
        resp = lark_api("GET", f"{BASE_URL}/records{params}")
        if resp.get("code") != 0:
            print(f"  List failed: {resp.get('msg', '')[:200]}")
            break

        items = resp.get("data", {}).get("items", [])
        if not items:
            break

        ids = [r["record_id"] for r in items]
        del_resp = lark_api("POST", f"{BASE_URL}/records/batch_delete", {"records": ids})
        if del_resp.get("code") == 0:
            deleted += len(ids)
            print(f"  Deleted {deleted}...")
        else:
            print(f"  Delete failed: {del_resp.get('msg', '')[:200]}")
            break

        page_token = resp.get("data", {}).get("page_token")
        if not resp.get("data", {}).get("has_more", False):
            break

    print(f"  Done. Deleted {deleted} records total.")
    return deleted


# ── Load and map CSV records ──────────────────────────────────────────────
def load_records(path):
    records = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            # Format missing_pct as percentage string
            try:
                pct = float(row["Missing_pct"])
                missing_str = f"{pct:.1f}%"
            except (ValueError, KeyError):
                missing_str = ""

            fields = {
                "Variable Name": row.get("Variable", ""),
                "Label":         row.get("Label_CN", ""),
                "Unit":          row.get("Unit", ""),
                "Window":        row.get("Window", ""),
                "Range":         row.get("Range", ""),
                "Missing":       missing_str,
                "type":          row.get("Category", ""),
                "Sources":       row.get("Label_EN", ""),
                "Link":          row.get("Dtype", ""),
            }
            # Drop empty strings to keep records clean
            fields = {k: v for k, v in fields.items() if v}
            records.append({"fields": fields})
    return records


# ── Batch import ─────────────────────────────────────────────────────────
def batch_import(records, batch_size=BATCH_SIZE):
    total = len(records)
    created = 0
    failed = 0
    total_batches = (total + batch_size - 1) // batch_size

    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]
        batch_num = i // batch_size + 1

        resp = lark_api("POST", f"{BASE_URL}/records/batch_create", {"records": batch})

        if resp.get("code") == 0:
            n = len(resp.get("data", {}).get("records", []))
            created += n
            pct = created / total * 100
            print(f"  [{batch_num}/{total_batches}] +{n}  ({created}/{total}, {pct:.0f}%)")
        else:
            msg = resp.get("msg", "unknown")
            print(f"  [{batch_num}/{total_batches}] FAILED: {msg[:200]}", file=sys.stderr)
            failed += len(batch)

    return created, failed


# ── Main ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Source: {CSV_PATH}")
    records = load_records(CSV_PATH)
    print(f"Loaded {len(records)} records\n")

    clear_table()
    print()

    print(f"Importing {len(records)} records ({BATCH_SIZE}/batch)...")
    n_created, n_failed = batch_import(records)

    print(f"\n{'='*45}")
    print(f"Result: {n_created} created, {n_failed} failed / {len(records)} total")
    if n_created == len(records):
        print("✓ All records imported successfully")
    print(f"\nBase URL: https://vcn7opmi92n5.feishu.cn/base/{BASE_TOKEN}")
