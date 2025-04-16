
import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
import uuid

DB_PATH = Path("logs/podcast_trends.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_data(conn):
    return pd.read_sql("SELECT * FROM podcasts", conn)

def filter_top_downloads(df, year_start, year_end, sort_by, feature_filter):
    df = df.copy()
    df['year'] = df['year'].fillna('').astype(str)
    df = df[df['year'].str.isnumeric()]
    df['year'] = df['year'].astype(int)
    if year_start:
        df = df[df['year'] >= year_start]
    if year_end:
        df = df[df['year'] <= year_end]
    if feature_filter:
        df = df[df['feature'] == feature_filter]
    return df.sort_values(by=sort_by, ascending=False)

def filter_general(df, year, feature, search_term):
    if year:
        df = df[df['year'] == year]
    if feature:
        df = df[df['feature'] == feature]
    if search_term:
        df = df[df['title'].str.contains(search_term, case=False, na=False)]
    return df

def main():
    st.set_page_config(page_title="Podcast Trends", layout="wide")
    st.title("🎧 Podcast Trends")

    conn = get_connection()
    df = load_data(conn)

    tab1, tab2 = st.tabs(["📊 Top Downloads", "🔬 Explore Library"])

    with tab1:
        with st.sidebar:
            st.subheader("Top Downloads Filters")
            year_start = st.number_input("Start Year", min_value=2000, max_value=2100, value=2015, key="start")
            year_end = st.number_input("End Year", min_value=2000, max_value=2100, value=2025, key="end")
            sort_by = st.selectbox("Sort By", options=["downloads_total", "eq_full"], key="sort")
            feature_filter = st.selectbox("Feature (optional)", options=[""] + sorted(df['feature'].dropna().unique().tolist()), key="feature")

        filtered_top = filter_top_downloads(df, year_start, year_end, sort_by, feature_filter)
        display_cols = ["date", "title", "year", "feature", "code", "downloads_total", "eq_full"]
        st.markdown(f"""**Total Downloads:** {filtered_top["downloads_total"].sum():,}  
**Average eq_full:** {filtered_top["eq_full"].mean():.2f}  
**Episodes:** {len(filtered_top):,}""")
        st.dataframe(filtered_top[display_cols], use_container_width=True, hide_index=True)
        csv_top = filtered_top[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", data=csv_top, file_name="top_downloads.csv", mime="text/csv", key=f"top_csv_{uuid.uuid4()}")

    with tab2:
        with st.sidebar:
            st.subheader("Explore Library Filters")
            years = sorted(df['year'].dropna().unique().tolist())
            year = st.selectbox("Year", options=[""] + years, key="fb_year")
            features = sorted(df['feature'].dropna().unique().tolist())
            feature = st.selectbox("Feature", options=[""] + features, key="fb_feature")
            search_term = st.text_input("Search Title", key="fb_search")

        filtered_df = filter_general(df, year, feature, search_term)
        st.markdown(f"""**Total Downloads:** {filtered_df["downloads_total"].sum():,}  
**Average eq_full:** {filtered_df["eq_full"].mean():.2f}  
**Episodes:** {len(filtered_df):,}""")
        st.dataframe(filtered_df[["date", "title", "year", "feature", "code", "downloads_total", "eq_full"]].sort_values("downloads_total", ascending=False), use_container_width=True, hide_index=True)
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", data=csv, file_name="filtered_podcasts.csv", mime="text/csv", key=f"full_csv_{uuid.uuid4()}")

if __name__ == "__main__":
    main()
