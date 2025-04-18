
import sqlite3
import pandas as pd
import argparse
from tabulate import tabulate

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--year", type=int, help="Filter by year")
    parser.add_argument("--feature", type=str, help="Filter by feature substring")
    args = parser.parse_args()

    conn = sqlite3.connect("data/podcasts.db")
    df = pd.read_sql("SELECT * FROM podcasts", conn)
    conn.close()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year"] = df["date"].dt.year

    if args.year:
        df = df[df["year"] == args.year]

    if args.feature:
        df = df[df["feature"].str.contains(args.feature, case=False, na=False)]

    if "eq_full" not in df.columns:
        df["eq_full"] = df["full"] + 0.5 * df["partial"]

    top_df = df.sort_values("eq_full", ascending=False)[
        ["feature", "title", "code", "eq_full", "full", "partial", "year"]
    ].head(args.limit)

    # Manually format each row for clean display
    columns = ["feature", "title", "code", "eq_full", "full", "partial", "year"]
    formatted_rows = []

    for _, row in top_df.iterrows():
        formatted_rows.append([
            row["feature"],
            row["title"],
            f"{int(row['code']):03}" if pd.notnull(row["code"]) else "n/a",
            str(int(round(row["eq_full"]))) if pd.notnull(row["eq_full"]) else "n/a",
            str(int(round(row["full"]))) if pd.notnull(row["full"]) else "n/a",
            str(int(round(row["partial"]))) if pd.notnull(row["partial"]) else "n/a",
            str(int(row["year"])) if pd.notnull(row["year"]) else "n/a",
        ])

    print(tabulate(formatted_rows, headers=columns, tablefmt="psql", showindex=False))

if __name__ == "__main__":
    main()
