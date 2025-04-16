import pandas as pd
from podcast_trends.parser import parse_podcast_url

def load_excel(file_path):
    xls = pd.ExcelFile(file_path)
    year_sheets = [s for s in xls.sheet_names if s.isdigit()]
    records = []

    for sheet in year_sheets:
        df = pd.read_excel(xls, sheet_name=sheet)
        for _, row in df.iterrows():
            parsed = parse_podcast_url(str(row.get("URL", "")))
            full = row.get("Full", 0) or 0
            partial = row.get("Partial", 0) or 0
            parsed.update({
                "download_year": sheet,
                "full": int(full),
                "partial": int(partial),
                "total": int(full) + int(partial)
            })
            records.append(parsed)

    return records
