import pandas as pd

df = pd.read_csv("kdrama.csv")

# 컬럼명 일괄 트리밍 + 특수문자 제거
df.columns = df.columns.str.strip().str.replace(r'[^A-Za-z0-9 ]', '', regex=True)

# 컬럼명 맵핑(사진 기반으로 정확하게 수정)
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

# 데이터 타입 처리 (숫자형 변환)
df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
df["Num_Episodes"] = pd.to_numeric(df["Num_Episodes"], errors="coerce")
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

st.write("✅ CSV 컬럼 정리 완료!")
st.subheader("📊 Genre Distribution")

if "Genre" in df.columns:
    genre_counts = (
        df["Genre"]
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
        title="Genre Distribution",
    )
    st.plotly_chart(fig_genre, use_container_width=True)
else:
    st.error("Genre column not found!")
