import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------
# App Title
# ------------------------------------------
st.set_page_config(page_title="TV Series Dashboard", layout="wide")

st.title("📺 K-DRAMA TV Series Analytics Dashboard")

# CSV Upload
file = st.file_uploader("📂 Upload your dataset (CSV)", type=["csv"])
if file is not None:
    df = pd.read_csv(file)

    # Clean Data
    df["Year of release"] = pd.to_numeric(df["Year of release"], errors="coerce")
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")

    # Sidebar Filters
    st.sidebar.header("🔍 Filters")
    genres = st.sidebar.multiselect("Select Genre", options=df["Genre"].unique())
    networks = st.sidebar.multiselect("Select Network", options=df["Original Network"].unique())
    years = st.sidebar.slider("Select Release Year Range",
                              int(df["Year of release"].min()),
                              int(df["Year of release"].max()),
                              (int(df["Year of release"].min()),
                               int(df["Year of release"].max())))

    filtered_df = df.copy()
    if genres:
        filtered_df = filtered_df[filtered_df["Genre"].isin(genres)]
    if networks:
        filtered_df = filtered_df[filtered_df["Original Network"].isin(networks)]
    filtered_df = filtered_df[
        filtered_df["Year of release"].between(years[0], years[1])
    ]

    # ------------------------------------------
    # KPI Cards
    # ------------------------------------------
    total = len(filtered_df)
    avg_rating = round(filtered_df["Rating"].mean(), 2)
    max_eps = filtered_df["Number of Episodes"].max()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Series", total)
    c2.metric("Average Rating", avg_rating)
    c3.metric("Max Episode Count", max_eps)

    # ------------------------------------------
    # Visualizations
    # ------------------------------------------
    st.subheader("📊 Genre Distribution")
    fig_genre = px.bar(filtered_df["Genre"].value_counts().reset_index(),
                       x="index", y="Genre", labels={"index": "Genre", "Genre": "Count"})
    st.plotly_chart(fig_genre, use_container_width=True)

    st.subheader("📈 Release Trend by Year")
    fig_year = px.line(filtered_df.groupby("Year of release").size().reset_index(name="Count"),
                       x="Year of release", y="Count")
    st.plotly_chart(fig_year, use_container_width=True)

    # ------------------------------------------
    # Top 10 by Rating
    # ------------------------------------------
    st.subheader("⭐ Top Rated Series")
    top10 = filtered_df.nlargest(10, "Rating")
    st.table(top10[["Name", "Rating", "Genre", "Original Network"]])

else:
    st.info("👆 CSV 파일을 업로드하면 분석을 시작합니다!")
