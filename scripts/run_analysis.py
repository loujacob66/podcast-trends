import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
from pathlib import Path
from podcast_trends.importer import load_excel
from podcast_trends.storage import save_to_json, load_from_json
from podcast_trends.trends import top_podcasts
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--input", help="Path to Excel file", required=True)
parser.add_argument("--json", help="Output JSON path", default="data/podcasts.json")
parser.add_argument("--top", action="store_true", help="Show top podcasts")
parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
parser.add_argument("--end", help="End date (YYYY-MM-DD)")
parser.add_argument("--limit", type=int, default=10)

args = parser.parse_args()

json_path = Path(args.json)
if not json_path.exists():
    print("📥 Importing from Excel...")
    records = load_excel(args.input)
    save_to_json(records, json_path)
else:
    print("📂 Loading from JSON...")
    records = load_from_json(json_path)

if args.top:
    start = datetime.strptime(args.start, "%Y-%m-%d") if args.start else None
    end = datetime.strptime(args.end, "%Y-%m-%d") if args.end else None
    top = top_podcasts(records, start=start, end=end, limit=args.limit)
    print(f"🎧 Top {args.limit} Podcasts:")
    for title, count in top:
        print(f"{title:40} {count}")
