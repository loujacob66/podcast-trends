
import pandas as pd
import argparse
import sqlite3
import os
from pathlib import Path
import re
import sys

def extract_feature_from_filename(filename: str) -> str | None:
    lowered = filename.lower()
    feature_map = {
        "hpcpodcas": "hpcpodcast",
        "hpcpodcast": "hpcpodcast",
        "mktg_podcast": "mktg_podcast",
        "oxd": "oxd",
        "hpcnb": "hpcnb"
    }
    for key, val in feature_map.items():
        if key in lowered:
            return val
    return None


def extract_date(url: str) -> str | None:
    filename = Path(url).name
    match_filename = re.search(r"(\d{4})[-_]?(\d{2})[-_]?(\d{2})", filename)
    if match_filename:
        return f"{match_filename.group(1)}-{match_filename.group(2)}-{match_filename.group(3)}"
    match_path = re.search(r"/(\d{4})/(\d{2})/", url)
    if match_path:
        return f"{match_path.group(1)}-{match_path.group(2)}-01"
    return None



def extract_code_from_filename(url: str) -> int | None:
    filename = Path(url).name
    match = re.match(r"^(\d+)[@_]", filename)
    return int(match.group(1)) if match else None


def extract_title_from_filename(url: str) -> str:
    filename = Path(url).name
    return re.sub(r'^\d+@', '', filename.split('.')[0])

def import_from_excel(path: str, db_path: str = "data/podcasts.db", override_db: bool = False):
    if os.path.exists(db_path) and not override_db:
        print("❌ Refusing to overwrite existing DB without --override-db")
        sys.exit(1)
    elif override_db and os.path.exists(db_path):
        os.remove(db_path)

    xls = pd.ExcelFile(path)
    all_rows = []

    for sheet_name in xls.sheet_names:
        df = xls.parse(sheet_name)
        df.columns = df.columns.str.strip().str.lower()
        df['sheet'] = sheet_name
        all_rows.append(df)

    df = pd.concat(all_rows, ignore_index=True)

    skipped_rows = 0
    processed_rows = []

    for _, row in df.iterrows():
        url = str(row.get("url", "")).strip()
        if "/wp-content/uploads" not in url:
            skipped_rows += 1
            continue

        try: full = int(float(row.get("full", 0) or 0))
        except: full = 0
        try: partial = int(float(row.get("partial", 0) or 0))
        except: partial = 0
        try: avg_bw = float(row.get("avg bw", 0) or 0)
        except: avg_bw = 0.0
        try: total_bw = float(row.get("total bw", 0) or 0)
        except: total_bw = 0.0

        processed_rows.append({
            "url": url,
            "full": full,
            "partial": partial,
            "avg_bw": avg_bw,
            "total_bw": total_bw,
            "eq_full": full + 0.5 * partial,
            "code": extract_code_from_filename(url),
            "title": extract_title_from_filename(url),
            "feature": extract_feature_from_filename(url),
            "date": extract_date(url),
            "sheet": row["sheet"]
        })

    clean_df = pd.DataFrame(processed_rows)
    clean_df["dupe_key"] = clean_df["url"].apply(lambda x: str(x).strip()) + "::" + clean_df["sheet"]

    deduped = clean_df.drop_duplicates(subset='dupe_key').copy()
    dups = clean_df[clean_df.duplicated('dupe_key', keep=False)]

    if not dups.empty:
        os.makedirs("logs", exist_ok=True)
        dups.to_csv("logs/duplicate_rows.csv", index=False)

    conn = sqlite3.connect(db_path)
    deduped.drop(columns=["dupe_key"], inplace=True)
    deduped.to_sql("podcasts", conn, if_exists="replace", index=False)
    conn.close()

    print(f"✅ Imported {len(deduped)} new rows (deduplicated by URL + sheet-derived year)")
    print(f"🗂️  Duplicates logged: {len(dups)}")
    print(f"🚫 Skipped rows: {skipped_rows}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Excel file to import")
    parser.add_argument("--override-db", action="store_true", help="Delete and recreate podcasts.db before import")
    args = parser.parse_args()
    import_from_excel(args.path, override_db=args.override_db)
