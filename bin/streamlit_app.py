
import streamlit as st
import sqlite3
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from commands.import_from_excel import import_from_excel

DB_PATH = 'data/podcasts.db'

st.set_page_config(page_title="Podcast Import Tool", layout="wide")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Explore Data",
    "📈 Title Trend Chart",
    "🧾 Raw Table View",
    "📥 Upload Data"
])

with tab1:
    st.title("🔍 Explore Imported Podcast Data")

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT feature, title, date, code, eq_full, full, partial FROM podcasts", conn)
    conn.close()

    if not df.empty:
        df['year'] = pd.to_datetime(df['date'], errors='coerce').dt.year.astype('Int64')
        df['month'] = pd.to_datetime(df['date'], errors='coerce').dt.month.astype('Int64')

        df_filtered = df.dropna(subset=['year', 'month'])
        df_filtered['year'] = df_filtered['year'].astype(int).astype(str)
        df_filtered['month'] = df_filtered['month'].astype(int).astype(str)

        with st.sidebar:
            st.header("📅 Filters")
            years = st.multiselect("Year", sorted(df_filtered['year'].unique()))
            months = st.multiselect("Month", sorted(df_filtered['month'].unique(), key=lambda x: int(x)))
            features = st.multiselect("Feature", sorted(df_filtered['feature'].dropna().unique()))

        if years:
            df_filtered = df_filtered[df_filtered['year'].isin(years)]
        if months:
            df_filtered = df_filtered[df_filtered['month'].isin(months)]
        if features:
            df_filtered = df_filtered[df_filtered['feature'].isin(features)]

        st.subheader("Top Titles")
        st.dataframe(df_filtered.sort_values("eq_full", ascending=False, ignore_index=True))
    else:
        st.info("No podcast data available yet. Please import a file first.")

with tab2:
    st.title("📈 EQ_Full Over Time for Title")

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT title, date, eq_full FROM podcasts", conn)
    conn.close()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    title_input = st.text_input("Paste a podcast title to chart")

    if title_input and title_input.strip() in df['title'].values:
        title_df = df[df['title'] == title_input.strip()].sort_values("date")
        st.line_chart(title_df.set_index("date")["eq_full"])
    elif title_input:
        st.warning("That title was not found in the database.")

with tab3:
    st.title("🧾 Raw Podcast Table")
    conn = sqlite3.connect(DB_PATH)
    raw_df = pd.read_sql_query("SELECT * FROM podcasts", conn)
    conn.close()
    st.dataframe(raw_df)

with tab4:
    st.title("🎙️ Podcast Import Tool")
    st.markdown("Upload an Excel file containing podcast data. Optionally overwrite the existing database.")
    
    overwrite = st.checkbox("🛑 Overwrite existing database on import")
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

    if uploaded_file and st.button("Start Import"):
        temp_path = f"data/temp_uploaded.xlsx"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        result = import_from_excel(temp_path, overwrite=overwrite)
        if result is None:
            st.success("✅ Import complete, but no summary was returned.")
        elif isinstance(result, dict):
            st.success(f"✅ {result.get('rows_imported', '?')} rows imported, {result.get('duplicates_found', '?')} duplicates.")
        else:
            st.warning("Import complete, but unexpected return format.")
