import pandas as pd
import re
from datetime import datetime
import sqlite3
import os

DB_PATH = "logs/podcast_trends.db"

def parse_row(row):
    url = row["URL"]
    downloads_full = int(row["Full"])
    downloads_partial = int(row["Partial"])
    size_per_download = row["Avg BW"]

    filename = url.split("/")[-1]
    file_ext = "." + filename.split(".")[-1] if "." in filename else ""

    upper = filename.upper()
    if "HPCNB" in upper:
        feature = "HPCNB"
    elif "HPCPODCAST" in upper:
        feature = "HPCpodcast"
    elif "OXD" in upper:
        feature = "OXD"
    elif "MKTG_PODCAST" in upper:
        feature = "Mktg_podcast"
    else:
        feature = "Other"

    code_match = re.match(r"(\d{3})@", filename)
    code = code_match.group(1) if code_match else None

    date_match = re.search(r"(20\d{6})", url)
    date_str = None
    year = None
    month = None
    if not date_match:
        date_match = re.search(r"(20\d{6})", filename)
    if not date_match:
        # Try folder structure: /uploads/YYYY/MM/
        folder_date_match = re.search(r"/(20\d{2})/(\d{2})/", url)
        if folder_date_match:
            year = folder_date_match.group(1)
            month = folder_date_match.group(2)
            date_str = f"{year}-{month}-01"
    if date_match:
        try:
            date_str = datetime.strptime(date_match.group(1), "%Y%m%d").strftime("%Y-%m-%d")
            year = date_str[:4]
            month = date_str[5:7]
        except:
            pass

    title = filename.replace(".mp3", "")

    downloads_total = downloads_full + downloads_partial
    eq_full = downloads_full + (downloads_partial / 2)

    return {
        "url": url,
        "filename": filename,
        "title": title,
        "feature": feature,
        "code": code,
        "date": date_str,
        "year": year,
        "month": month,
        "downloads_full": downloads_full,
        "downloads_partial": downloads_partial,
        "downloads_total": downloads_total,
        "eq_full": eq_full,
        "size_per_download": size_per_download,
        "file_ext": file_ext
    }

def recreate_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE podcasts (
        url TEXT,
        filename TEXT,
        title TEXT,
        feature TEXT,
        code TEXT,
        date TEXT,
        year TEXT,
        month TEXT,
        downloads_full INTEGER,
        downloads_partial INTEGER,
        downloads_total INTEGER,
        eq_full REAL,
        size_per_download TEXT,
        file_ext TEXT
    )
    """)
    conn.commit()
    conn.close()

def import_excel(path):
    xls = pd.read_excel(path, sheet_name=None)
    df = pd.concat(xls.values(), ignore_index=True)
    df.columns = df.columns.str.strip()
    rows = df.apply(parse_row, axis=1).tolist()
    df_clean = pd.DataFrame(rows)
    print(f"📊 Preparing to import {len(df_clean)} records...")

    conn = sqlite3.connect(DB_PATH)
    df_clean.to_sql("podcasts", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python import_from_excel.py <spreadsheet.xlsx>")
        sys.exit(1)
    recreate_database()
    import_excel(sys.argv[1])
    print(f"✅ Imported into {DB_PATH}")
