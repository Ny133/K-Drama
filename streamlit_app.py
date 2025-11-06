import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="TV Series Dashboard", layout="wide")
st.title("📺 TV Series Analytics Dashboard")

# ✅ Raw URL을 아래에 넣어주세요
RAW_GITHUB_CSV_URL = "https://raw.githubusercontent.com/Ny133/K-Drama/main/kdrama.csv"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url, encoding="utf-8")
    df["Year of release"] = pd.to_numeric(df["Year of release"], errors="coerce")
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    return df

df = load_data(RAW_GITHUB_CSV_URL)

# Sidebar Filters
st.sidebar.header("🔍 Filters")
genres = st.sidebar.multiselect("Genre", df["Genre"].dropna().unique())
networks = st.sidebar.multiselect("Original Network", df["Original Network"].dropna().unique())

year_min = int(df["Year of release"].min())
year_max = int(df["Year of release"].max())
years = st.sidebar.slider("Release Year Range", year_min, year_max, (year_min, year_max))

filtered = df.copy()
if genres:
    filtered = filtered[filtered["Genre"].isin(genres)]
if networks:
    filtered = filtered[filtered["Original Network"].isin(networks)]
filtered = filtered[filtered["Year of release"].between(years[0], years[1])]

# KPI Cards
c1, c2, c3 = st.columns(3)
c1.metric("Total Series", len(filtered))
c2.metric("Average Rating", round(filtered["Rating"].mean(), 2))
c3.metric("Max Episodes", filtered["Number of Episodes"].max())

# Genre Chart
st.subheader("📊 Genre Distribution")
fig_genre = px.bar(filtered["Genre"].value_counts().reset_index(),
                   x="index", y="Genre", labels={"index":"Genre","Genre":"Count"})
st.plotly_chart(fig_genre, use_container_width=True)

# Release Trend
st.subheader("📈 Release Trend by Year")
trend = filtered.groupby("Year of release").size().reset_index(name="Count")
fig_year = px.line(trend, x="Year of release", y="Count")
st.plotly_chart(fig_year, use_container_width=True)

# Top Rated Table
st.subheader("⭐ Top Rated Series")
top10 = filtered.nlargest(10, "Rating")
st.table(top10[["Name","Rating","Genre","Original Network"]])
