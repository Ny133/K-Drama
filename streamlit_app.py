import pandas as pd
import streamlit as st
import plotly.express as px

# ✅ GitHub CSV URL
CSV_URL = "https://raw.githubusercontent.com/Ny133/K-Drama/main/kdrama.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)

    # ✅ 컬럼명 정리 (공백/깨진 컬럼명 수정)
    df.columns = df.columns.str.strip().str.replace(r'[^A-Za-z0-9 ]', '', regex=True)
    df = df.rename(columns={
        "Aired Date": "Aired_Date",
        "Year of re": "Year",
        "Original N": "Network",
        "Aired On": "Aired_On",
        "Number c": "Num_Episodes",
        "Duration": "Duration",
        "Content R": "Content_Rating",
        "Rating": "Rating",
        "Synopsis": "Synopsis",
        "Genre": "Genre",
        "Tags": "Tags",
        "Director": "Director",
        "Screenwri": "Screenwriter",
        "Cast": "Cast",
        "Production": "Production",
        "Rank": "Rank"
    })

    # ✅ 숫자형 변환
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df["Num_Episodes"] = pd.to_numeric(df["Num_Episodes"], errors="coerce")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    return df


df = load_data()

st.title("📺 K-Drama Dashboard")
st.write("Korean Drama Analytics with Streamlit")

# ✅ Sidebar Filters
st.sidebar.header("Filters")

year_filter = st.sidebar.multiselect(
    "Select Year", options=sorted(df["Year"].dropna().unique()),
    default=sorted(df["Year"].dropna().unique())
)

network_filter = st.sidebar.multiselect(
    "Select Network", options=df["Network"].dropna().unique(),
    default=df["Network"].dropna().unique()
)

filtered = df[
    (df["Year"].isin(year_filter)) &
    (df["Network"].isin(network_filter))
]

# ✅ Show Data Table
st.subheader("📋 Filtered K-Drama Table")
st.dataframe(filtered)

# ✅ Rating Distribution
st.subheader("⭐ Rating Distribution")
fig_rating = px.histogram(
    filtered,
    x="Rating",
    nbins=10,
    title="Rating Distribution of K-Dramas"
)
st.plotly_chart(fig_rating, use_container_width=True)

# ✅ Genre Distribution Chart
st.subheader("🎭 Genre Distribution")

genre_counts = (
    filtered["Genre"]
    .dropna()
    .astype(str)
    .str.split(",")
    .explode()
    .str.strip()
    .value_counts()
    .reset_index()
)
genre_counts.columns = ["Genre", "Count"]

fig_genre = px.bar(
    genre_counts,
    x="Genre",
    y="Count",
    title="Genre Frequency"
)
st.plotly_chart(fig_genre, use_container_width=True)

# ✅ Rating vs Episodes
st.subheader("📈 Rating vs Number of Episodes")
fig_scatter = px.scatter(
    filtered,
    x="Num_Episodes",
    y="Rating",
    color="Genre",
    hover_data=["Name", "Network"],
    title="Rating vs Episode Count"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ✅ Top-rated Dramas Table
st.subheader("🏆 Top 10 Dramas by Rating")
top10 = filtered.sort_values(by="Rating", ascending=False).head(10)
st.table(top10[["Name", "Year", "Rating", "Network"]])

