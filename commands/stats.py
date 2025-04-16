import sqlite3
import pandas as pd

def show_stats():
    conn = sqlite3.connect("logs/podcast_trends.db")
    query = "SELECT COUNT(*) as total_episodes, AVG(eq_full) as avg_eq_full FROM podcasts"
    df = pd.read_sql_query(query, conn)
    print("🎧 Podcast Summary")
    print(df.to_string(index=False))
    conn.close()
