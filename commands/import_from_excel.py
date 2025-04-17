import pandas as pd
import os
import re
from pathlib import Path
from collections import defaultdict
import sqlite3

def extract_feature(filename):
    match = re.search(r"(Mktg_podcast|HPCpodcast|HPCNB|OXD|OXDcast|MktgPodcast|Mktg_Podcast)", filename, re.IGNORECASE)
    return match.group(1) if match else None

def extract_code(filename):
    match = re.search(r"(\d{2,3})(?=@)", filename)
    return match.group(1) if match else None

def extract_date(filename, url):
    match = re.search(r"(20\d{2})[-_](\d{1,2})", filename)
    if match:
        return f"{match.group(1)}-{int(match.group(2)):02d}-01"
    match = re.search(r"/(20\d{2})/(\d{1,2})/", url)
    if match:
        return f"{match.group(1)}-{int(match.group(2)):02d}-01"
    return None

def extract_title(filename):
    name = Path(filename).stem
    parts = re.split(r"[_\-]", name)
    if len(parts) > 5:
        parts = parts[:5]
    return "_".join(parts)

def normalize_columns(df):
    column_map = {}
    for col in df.columns:
        col_clean = col.strip().lower()
        if col_clean == 'url':
            column_map[col] = 'url'
        elif 'full' in col_clean:
            column_map[col] = 'full'
        elif 'partial' in col_clean:
            column_map[col] = 'partial'
        elif 'avg' in col_clean:
            column_map[col] = 'avg_bw'
        elif 'total' in col_clean:
            column_map[col] = 'total_bw'
    return df.rename(columns=column_map)

def import_from_excel(filepath, overwrite=False):
    if overwrite and os.path.exists("data/podcasts.db"):
        os.remove("data/podcasts.db")
        print("🧨 Existing database deleted due to --overwrite-db flag")

    print(f"📥 Importing from {filepath}")
    wb = pd.read_excel(filepath, sheet_name=None)
    seen = {}
    dedup_buffer = defaultdict(list)
    output_rows = []
    skipped = []
    db_path = "data/podcasts.db"

    for sheet_name, df in wb.items():
        df = normalize_columns(df)
        for _, row in df.iterrows():
            url = str(row.get("url") or "").strip().lower()
            sheet = str(sheet_name).strip()
            if "/wp-content/uploads" not in url:
                skipped.append({**row.to_dict(), "sheet_name": sheet_name, "reason": "invalid url"})
                continue

            dedupe_key = (url, sheet)
            full = pd.to_numeric(row.get("full"), errors="coerce") or 0
            partial = pd.to_numeric(row.get("partial"), errors="coerce") or 0
            avg_bw = pd.to_numeric(row.get("avg_bw"), errors="coerce") or 0
            total_bw = pd.to_numeric(row.get("total_bw"), errors="coerce") or 0

            filename = os.path.basename(url)
            feature = extract_feature(filename)
            code = extract_code(filename)
            date = extract_date(filename, url)
            title = extract_title(filename)

            if dedupe_key in seen:
                dedup_buffer[dedupe_key].append((full, partial, avg_bw, total_bw))
                continue

            seen[dedupe_key] = True
            dedup_buffer[dedupe_key].append((full, partial, avg_bw, total_bw))
            output_rows.append({
                "url": url,
                "full": full,
                "partial": partial,
                "avg_bw": avg_bw,
                "total_bw": total_bw,
                "feature": feature,
                "code": code,
                "sheet_name": sheet,
                "year": int(date[:4]) if date else None,
                "month": int(date[5:7]) if date else None,
                "date": date,
                "title": title
            })

    for row in output_rows:
        key = (row["url"], row["sheet_name"])
        entries = dedup_buffer[key]
        if len(entries) > 1:
            row["full"] = sum(e[0] for e in entries)
            row["partial"] = sum(e[1] for e in entries)
            row["avg_bw"] = sum(e[2] for e in entries) / len(entries)
            row["total_bw"] = sum(e[3] for e in entries)
        row["eq_full"] = row["full"] + 0.5 * row["partial"]

    duplicate_rows = []
    for key, entries in dedup_buffer.items():
        if len(entries) > 1:
            for entry in entries[1:]:
                duplicate_rows.append({
                    "url": key[0],
                    "sheet_name": key[1],
                    "full": entry[0],
                    "partial": entry[1],
                    "avg_bw": entry[2],
                    "total_bw": entry[3],
                    "reason": "duplicate in sheet"
                })
    if duplicate_rows:
        pd.DataFrame(duplicate_rows).to_csv("logs/duplicate_rows.csv", index=False)
    if skipped:
        pd.DataFrame(skipped).to_csv("logs/skipped_rows.csv", index=False)

    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS podcasts (
        url TEXT NOT NULL,
        full INTEGER,
        partial INTEGER,
        avg_bw REAL,
        total_bw REAL,
        eq_full REAL,
        feature TEXT,
        code TEXT,
        sheet_name TEXT NOT NULL,
        year INTEGER,
        month INTEGER,
        date TEXT,
        title TEXT,
        UNIQUE(url, sheet_name)
    )
    """)
    conn.commit()

    inserted_count = 0
    for row in output_rows:
        c.execute("""
        INSERT OR IGNORE INTO podcasts (url, full, partial, avg_bw, total_bw, eq_full, feature, code, sheet_name, year, month, date, title)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["url"], row["full"], row["partial"], row["avg_bw"], row["total_bw"], row["eq_full"], row["feature"],
            row["code"], row["sheet_name"], row["year"], row["month"], row["date"], row["title"]
        ))
        if c.rowcount > 0:
            inserted_count += 1

    conn.commit()
    conn.close()

    print(f"✅ Inserted {inserted_count} new rows")
    print(f"🗂️  Duplicates logged: {len(duplicate_rows)}")
    print(f"🚫 Skipped rows: {len(skipped)}")
