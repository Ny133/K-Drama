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


import streamlit as st
import pandas as pd

# ✅ 데이터 로드
df = pd.read_csv("your_movies.csv")

# ✅ 연도(Release Year) 필터 UI
years = sorted(df["Release Year"].dropna().unique())
selected_year = st.selectbox("연도 선택", years)

# ✅ 선택한 연도의 영화 목록 필터링
filtered_df = df[df["Release Year"] == selected_year]

# ✅ 데이터 없는 경우 예외 처리
if filtered_df.empty:
    st.warning("😥 해당 연도에 영화 데이터가 없습니다.")
else:
    st.subheader(f"📌 {selected_year}년 영화 추천 목록")
    
    # ✅ Top 10 작품 기준 (평가 컬럼이 없다면 Popularity 기준 등으로)
    if "Popularity" in df.columns:
        filtered_df = filtered_df.sort_values("Popularity", ascending=False).head(10)
    else:
        # Popularity도 없으면 그냥 정렬 없이 상위 10개만
        filtered_df = filtered_df.head(10)
    
    # ✅ 리스트 출력
    for idx, row in filtered_df.iterrows():
        st.write(f"🎬 **{row['Title']}** ({row['Release Year']})")

    # ✅ 테이블 표시 (선택)
    st.dataframe(filtered_df)

