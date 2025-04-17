#!/usr/bin/env python3

import sys
import os

# Fix path so Python can find commands/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def from_excel(path, overwrite_db=False):
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        sys.exit(1)

    print(f"▶️  Importing: {path}")

    try:
        from commands.import_from_excel import import_from_excel
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        sys.exit(1)

    import_from_excel(path, overwrite=overwrite_db)

def run_top(args):
    from commands.top import top_episodes

    limit = 20
    year = None
    feature = None

    if "--limit" in args:
        idx = args.index("--limit")
        if idx + 1 < len(args):
            limit = int(args[idx + 1])

    if "--year" in args:
        idx = args.index("--year")
        if idx + 1 < len(args):
            year = int(args[idx + 1])

    if "--feature" in args:
        idx = args.index("--feature")
        if idx + 1 < len(args):
            feature = args[idx + 1]

    top_episodes(limit=limit, year=year, feature=feature)

def show_help():
    print("Usage:")
    print("  python bin/podcast.py from-excel <path-to-excel-file> [--overwrite-db]")
    print("  python bin/podcast.py top [--limit N] [--year YYYY] [--feature HPC]")

if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        show_help()
        sys.exit(1)

    cmd = args[1]
    if cmd == "from-excel":
        if len(args) < 3:
            show_help()
            sys.exit(1)
        overwrite_flag = "--overwrite-db" in args
        file_arg = args[2]
        from_excel(file_arg, overwrite_db=overwrite_flag)
    elif cmd == "top":
        run_top(args[2:])
    else:
        show_help()
