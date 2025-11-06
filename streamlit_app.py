import pandas as pd
import streamlit as st
import plotly.express as px

CSV_URL = "https://raw.githubusercontent.com/Ny133/K-Drama/main/kdrama.csv"

# ✅ 원본 컬럼 자동 파악 & 정리
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)

    # ✅ 모든 컬럼명 통일 (공백 제거 + 특수문자 제거)
    df.columns = df.columns.str.strip().str.replace(r'[^A-Za-z0-9_]+', '_', regex=True)

    return df

df = load_data()

st.title("📺 K-Drama Dashboard")



# ✅ 실제 존재하는 컬럼 기반 사용
valid_cols = df.columns.tolist()

col_year = next((c for c in valid_cols if "Year" in c), None)
col_network = next((c for c in valid_cols if "Network" in c), None)
col_rating = next((c for c in valid_cols if "Rating" in c), None)
col_genre = next((c for c in valid_cols if "Genre" in c), None)
col_episodes = next((c for c in valid_cols if "Number" in c or "Episode" in c), None)

# ✅ 데이터 타입 변환
if col_rating:
    df[col_rating] = pd.to_numeric(df[col_rating], errors="coerce")

if col_episodes:
    df[col_episodes] = pd.to_numeric(df[col_episodes], errors="coerce")

# ✅ Sidebar Filters
st.sidebar.header("Filters")

# ✅ 연도 필터
if col_year:
    year_filter = st.sidebar.multiselect(
        "Select Year",
        sorted(df[col_year].dropna().unique()),
        default=sorted(df[col_year].dropna().unique())
    )
    df = df[df[col_year].isin(year_filter)]

# ✅ 방송사 필터
if col_network:
    network_filter = st.sidebar.multiselect(
        "Select Network",
        sorted(df[col_network].dropna().unique()),
        default=sorted(df[col_network].dropna().unique())
    )
    df = df[df[col_network].isin(network_filter)]


# ✅ 데이터 미리보기
st.subheader("📋 Filtered Data")
st.dataframe(df)


# ✅ Genre Bar Chart
if col_genre:
    st.subheader("🎭 Genre Distribution")
    genre_counts = (
        df[col_genre]
        .dropna().astype(str)
        .str.split(",").explode().str.strip()
        .value_counts().reset_index()
    )
    genre_counts.columns = ["Genre", "Count"]
    fig_genre = px.bar(genre_counts, x="Genre", y="Count")
    st.plotly_chart(fig_genre, use_container_width=True)

rating_clean = (
    df[col_rating]
    .astype(str)
    .str.extract(r'([0-9]+[.,]?[0-9]*)')[0]
    .str.replace(',', '.', regex=False)
)

df["_rating_clean"] = pd.to_numeric(rating_clean, errors="coerce")

# ====== Rating by Drama Title ======
st.subheader("📊 Rating by Drama Title")

if col_rating and df["_rating_clean"].notna().sum() > 0:
    # 유효한 rating 있는 데이터만 사용
    df_valid = df.dropna(subset=["_rating_clean"])

    # 평점 높은 순 정렬
    df_sorted = df_valid.sort_values("_rating_clean", ascending=False)

    # 작품명 컬럼 찾기 (보통 첫 컬럼이 Name)
    col_name = df.columns[0]

    fig_bar = px.bar(
        df_sorted,
        x="_rating_clean",
        y=col_name,
        orientation="h",
        title="Drama Ratings",
        labels={"_rating_clean": "Rating", col_name: "Drama"},
        hover_data=[col_name, col_rating],
    )

    fig_bar.update_layout(
        yaxis={'categoryorder':'total ascending'},  # 높은 평점이 위로 오도록
        height=800
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # ✅ 작품 검색 기능 추가(Optional)
    search_title = st.text_input("🔍 Search Drama Title")
    if search_title:
        result = df[df[col_name].str.contains(search_title, case=False, na=False)]
        st.write(result[[col_name, col_rating, "_rating_clean"]])
else:
    st.warning("⚠ 유효한 Rating 데이터가 부족합니다.")
