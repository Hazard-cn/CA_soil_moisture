"""
import_to_feishu_base.py
Purpose: Batch import data_dictionary_v3.csv into Feishu Bitable
Base: SR项目数据说明 (YFsvbhCDdahXw0s2HEHcPMf6nxf)
Table: 变量字典_v3 (tblWvKlrRwnlntsI)
Date: 2026-04-14

Strategy: use 'lark-cli api POST' with small batches (20 records)
to stay within Windows command-line length limit.
MSYS_NO_PATHCONV=1 prevents Git Bash path mangling.
"""

import csv
import json
import subprocess
import sys
import os

# ── Config ──────────────────────────────────────────────────────────────
BASE_TOKEN = "YFsvbhCDdahXw0s2HEHcPMf6nxf"
TABLE_ID   = "tblWvKlrRwnlntsI"
BASE_URL   = f"/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}"
CSV_PATH   = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "../../data_build/output/tables/data_dictionary_v3.csv")
# Call node directly to bypass cmd.exe (which interprets <, >, & in args)
LARK_CLI   = ["node",
              r"C:\Users\Lenovo\AppData\Roaming\npm\node_modules\@larksuite\cli\scripts\run.js"]
BATCH_SIZE = 20

env = os.environ.copy()
env["MSYS_NO_PATHCONV"] = "1"


# ── Helper: call lark-cli api ─────────────────────────────────────────────
def lark_api(method, path, data=None):
    cmd = list(LARK_CLI) + ["api", method, path, "--as", "user"]
    if data:
        cmd += ["--data", json.dumps(data, ensure_ascii=False)]
    result = subprocess.run(cmd, capture_output=True, env=env, shell=False)
    # lark-cli on Windows uses system code page (GBK/CP936) for output
    stdout = result.stdout.decode("gbk", errors="replace")
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        stderr = result.stderr.decode("gbk", errors="replace") if result.stderr else ""
        return {"code": -1, "msg": (stderr or stdout)[:300]}


# ── Clear all existing records ────────────────────────────────────────────
def clear_table():
    print("Clearing existing records...")
    deleted = 0
    page_token = None

    while True:
        params = f"?page_size=100"
        if page_token:
            params += f"&page_token={page_token}"
        resp = lark_api("GET", f"{BASE_URL}/records{params}")
        if resp.get("code") != 0:
            print(f"  List failed: {resp.get('msg')}")
            break

        items = resp.get("data", {}).get("items", [])
        if not items:
            break

        ids = [r["record_id"] for r in items]
        # Batch delete (max 500 per call)
        del_resp = lark_api("POST", f"{BASE_URL}/records/batch_delete",
                            {"records": ids})
        if del_resp.get("code") == 0:
            deleted += len(ids)
            print(f"  Deleted {deleted} records...")
        else:
            print(f"  Delete failed: {del_resp.get('msg')}")
            break

        has_more = resp.get("data", {}).get("has_more", False)
        page_token = resp.get("data", {}).get("page_token")
        if not has_more:
            break

    print(f"  Total deleted: {deleted}")
    return deleted


# ── Load CSV ─────────────────────────────────────────────────────────────
def load_records(path):
    records = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fields = {
                "Variable": row["Variable"],
                "Category": row["Category"],
                "Window":   row["Window"],
                "Label_CN": row["Label_CN"],
                "Label_EN": row["Label_EN"],
                "Unit":     row["Unit"],
                "Dtype":    row["Dtype"],
                "Range":    row["Range"],
            }
            for num_col in ["N_valid", "Missing_pct"]:
                try:
                    v = row[num_col].strip()
                    fields[num_col] = float(v) if v else None
                except (ValueError, KeyError):
                    fields[num_col] = None

            fields = {k: v for k, v in fields.items() if v is not None and v != ""}
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

        resp = lark_api("POST", f"{BASE_URL}/records/batch_create",
                        {"records": batch})

        if resp.get("code") == 0:
            n = len(resp.get("data", {}).get("records", []))
            created += n
            pct = created / total * 100
            print(f"  [{batch_num}/{total_batches}] +{n}  ({created}/{total}, {pct:.0f}%)")
        else:
            msg = resp.get("msg", "unknown")
            print(f"  [{batch_num}/{total_batches}] FAILED: {msg}", file=sys.stderr)
            failed += len(batch)

    return created, failed


# ── Main ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"CSV: {CSV_PATH}")
    records = load_records(CSV_PATH)
    print(f"Loaded {len(records)} records\n")

    clear_table()
    print()

    print(f"Importing ({BATCH_SIZE}/batch, {(len(records)+BATCH_SIZE-1)//BATCH_SIZE} batches)...")
    n_created, n_failed = batch_import(records)

    print(f"\n{'='*45}")
    print(f"Result: {n_created} created, {n_failed} failed / {len(records)} total")
