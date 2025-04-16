import sqlite3
import typer
import pandas as pd
from tabulate import tabulate
from datetime import datetime, timedelta

def top_episodes(
    by: str = typer.Option("eq_full", help="Field to rank by (e.g., eq_full, downloads_full, downloads_partial)"),
    limit: int = typer.Option(10, help="Number of episodes to display"),
    verbose: bool = typer.Option(False, help="Show all columns"),
    year: int = typer.Option(None, help="Only include entries from this year"),
    after: str = typer.Option(None, help="Only include entries on or after this date (YYYY-MM-DD)"),
    before: str = typer.Option(None, help="Only include entries before this date (YYYY-MM-DD)"),
    months: int = typer.Option(None, help="Only include entries from the past X months"),
    features: list[str] = typer.Option(None, help="Partial feature match (e.g. --features HPC HPCpodcast Mktg)"),
):
    """Show top podcast episodes ranked by eq_full or other metrics, with optional date and feature filters."""
    conn = sqlite3.connect("logs/podcast_trends.db")

    columns_basic = "title, feature, code, date, downloads_full, downloads_partial, eq_full"
    columns_verbose = "*"
    columns = columns_verbose if verbose else columns_basic

    where_clauses = []
    if year:
        where_clauses.append(f"date LIKE '{year}-%'")
    if after:
        where_clauses.append(f"date >= '{after}'")
    if before:
        where_clauses.append(f"date <= '{before}'")
    if months:
        cutoff = (datetime.today() - timedelta(days=months*30)).strftime("%Y-%m-%d")
        where_clauses.append(f"date >= '{cutoff}'")
    if features:
        like_clauses = [f"feature LIKE '%{f}%'" for f in features]
        where_clauses.append("(" + " OR ".join(like_clauses) + ")")

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"""SELECT {columns}
               FROM podcasts
               {where_sql}
               ORDER BY {by} DESC
               LIMIT {limit}"""

    try:
        df = pd.read_sql_query(query, conn)
        if not verbose:
            df["title"] = df["title"].apply(lambda t: t if len(t) <= 40 else t[:40] + "…")
        print(tabulate(df, headers="keys", tablefmt="rounded_grid", showindex=False))
    except Exception as e:
        print("⚠️ Error:", e)
    finally:
        conn.close()
