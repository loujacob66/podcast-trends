
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from commands.import_from_excel import import_from_excel

DB_PATH = "data/podcasts.db"
SUMMARY_PATH = "logs/import_summary.txt"

def apply_sidebar_filters(df):
    st.sidebar.title("🔍 Filters")
    features = df["feature"].dropna().unique().tolist()
    selected_features = st.sidebar.multiselect("Feature(s)", sorted(features))

    years = df["year"].dropna().unique().astype(int)
    selected_years = st.sidebar.multiselect("Year(s)", sorted(years, reverse=True))

    df = df[df["date"].notnull()]
    min_date = df["date"].min()
    max_date = df["date"].max()
    start_date, end_date = st.sidebar.date_input("Date Range", [min_date, max_date], format="MM/DD/YYYY")

    if selected_features:
        df = df[df["feature"].isin(selected_features)]
    if selected_years:
        df = df[df["year"].isin(selected_years)]
    if isinstance(start_date, datetime) and isinstance(end_date, datetime):
        df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]

    return df

def show_explore_tab(df):
    st.header("📊 Explore Data")
    display_df = df.copy()
    display_df["eq_full"] = display_df["eq_full"].apply(lambda x: int(round(x)) if pd.notnull(x) else "n/a")
    display_df["partial"] = display_df["partial"].apply(lambda x: int(round(x)) if pd.notnull(x) else "n/a")
    display_df["full"] = display_df["full"].apply(lambda x: int(round(x)) if pd.notnull(x) else "n/a")
    display_df["code"] = display_df["code"].apply(lambda x: f"{int(x):03}" if pd.notnull(x) else "n/a")
    display_df["date"] = display_df["date"].dt.strftime("%m-%d-%Y")
    st.dataframe(display_df[["feature", "title", "date", "code", "eq_full", "full", "partial"]].sort_values("eq_full", ascending=False), use_container_width=True, hide_index=True)

def show_raw_tab(df):
    st.header("🧾 Raw Table View")
    st.dataframe(df)

def show_trend_tab(df):
    st.header("📈 Trend by Title")
    titles = df["title"].dropna().unique().tolist()
    selected_title = st.selectbox("Select Title", sorted(titles))
    trend_df = df[df["title"] == selected_title].sort_values("date")
    if not trend_df.empty:
        st.line_chart(trend_df.set_index("date")[["eq_full"]])
    else:
        st.warning("No trend data available for this title.")

def show_upload_tab():
    st.header("📤 Upload Data")
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    overwrite = st.checkbox("Overwrite existing DB", value=False)
    if st.button("Run Import"):
        if uploaded_file:
            save_path = os.path.join("data", f"uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
            with open(save_path, "wb") as f:
                f.write(uploaded_file.read())
            import_from_excel(save_path, overwrite=overwrite)
            st.success("✅ Import completed.")
            if os.path.exists(SUMMARY_PATH):
                with open(SUMMARY_PATH, "r") as f:
                    summary = f.read()
                st.text("Import Summary:")
                st.code(summary)
        else:
            st.warning("⚠️ Please upload a file.")

def main():
    st.set_page_config(page_title="Podcast Trends", layout="wide")
    st.title("🎧 Podcast Trends Dashboard")

    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM podcasts", conn)
        conn.close()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["year"] = df["date"].dt.year.astype("Int64")
    else:
        df = pd.DataFrame()

    if not df.empty:
        df = apply_sidebar_filters(df)

    tab1, tab2, tab3, tab4 = st.tabs(["Explore Data", "Raw Table View", "Trend by Title", "Upload Data"])
    with tab1:
        if not df.empty:
            show_explore_tab(df)
        else:
            st.info("No data found.")
    with tab2:
        if not df.empty:
            show_raw_tab(df)
    with tab3:
        if not df.empty:
            show_trend_tab(df)
    with tab4:
        show_upload_tab()

if __name__ == "__main__":
    main()
