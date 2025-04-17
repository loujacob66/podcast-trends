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

def show_help():
    print("Usage:")
    print("  python bin/podcast.py from-excel <path-to-excel-file> [--overwrite-db]")

if __name__ == "__main__":
    args = sys.argv
    if len(args) < 3 or args[1] != "from-excel":
        show_help()
        sys.exit(1)

    overwrite_flag = "--overwrite-db" in args
    file_arg = args[2]
    from_excel(file_arg, overwrite_db=overwrite_flag)
