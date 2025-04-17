import sqlite3
from tabulate import tabulate

def top_episodes(limit=20, year=None, feature=None):
    conn = sqlite3.connect("data/podcasts.db")
    cursor = conn.cursor()

    query = "SELECT title, eq_full, full, partial, feature, year FROM podcasts WHERE 1=1"
    params = []

    if year:
        query += " AND year = ?"
        params.append(year)

    if feature:
        query += " AND feature LIKE ?"
        params.append(f"%{feature}%")

    query += " ORDER BY eq_full DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    conn.close()

    if results:
        print(tabulate(results, headers=["Title", "Eq Full", "Full", "Partial", "Feature", "Year"]))
    else:
        print("No results found.")
