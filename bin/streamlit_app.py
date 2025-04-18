import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from commands.import_from_excel import import_from_excel

DB_PATH = 'data/podcasts.db'

st.set_page_config(layout="wide", page_title="Podcast Trends")

st.title("🎙️ Podcast Analytics Explorer")

tabs = st.tabs(["Explore Data", "Raw Table View", "Upload Data", "Chart View"])
tab1, tab2, tab3, tab4 = tabs

df = None
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM podcasts", conn)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year"] = df["date"].dt.year.astype("Int64")
    df["month"] = df["date"].dt.month.astype("Int64")

with tab1:
    st.header("📊 Explore Data")
    if df is not None and not df.empty:
        st.markdown("Use filters in the sidebar to explore podcast trends.")
        with st.sidebar:
            st.header("📅 Filters")
            years = st.multiselect("Year", sorted(df['year'].dropna().unique()))
            months = st.multiselect("Month", sorted(df['month'].dropna().unique()))
            features = st.multiselect("Feature", sorted(df['feature'].dropna().unique()))

        df_filtered = df.copy()
        if years:
            df_filtered = df_filtered[df_filtered["year"].isin(years)]
        if months:
            df_filtered = df_filtered[df_filtered["month"].isin(months)]
        if features:
            df_filtered = df_filtered[df_filtered["feature"].isin(features)]

        df_filtered = df_filtered.drop(columns=['year', 'month'], errors='ignore')
        df_filtered[["eq_full", "full", "partial"]] = df_filtered[["eq_full", "full", "partial"]].fillna(0).astype(int)

        if not df_filtered.empty:
            st.subheader("Top Titles")
            st.dataframe(
                df_filtered[["feature", "title", "date", "code", "eq_full", "full", "partial"]]
                .sort_values("eq_full", ascending=False),
                use_container_width=True, hide_index=True
            )
        else:
            st.info("No matching results for selected filters.")

with tab2:
    st.header("🧾 Raw Table View")
    if df is not None:
        st.dataframe(df, use_container_width=True)

with tab3:
    st.header("📤 Upload Data")
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    overwrite = st.checkbox("Overwrite database", value=False)
    if uploaded_file is not None:
        with open("/tmp/uploaded.xlsx", "wb") as f:
            f.write(uploaded_file.read())
        result = import_from_excel("/tmp/uploaded.xlsx", overwrite_db=overwrite)
        if result:
            st.success(f"Imported {result.get('rows_imported', 0)} rows with {result.get('duplicates_found', 0)} duplicates.")
        else:
            st.error("Import failed.")

with tab4:
    st.header("📈 Chart View")
    if df is not None and not df.empty:
        title_input = st.selectbox("Select a title", sorted(df["title"].dropna().unique()))
        title_df = df[df["title"] == title_input].sort_values("date")
        if 'eq_full' in title_df.columns:
            st.line_chart(title_df.set_index("date")["eq_full"])
            st.markdown("#### 📋 Chart Data Preview")
            st.dataframe(
                title_df,
                use_container_width=True, hide_index=True,
            )
