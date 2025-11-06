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

st.subheader("🎬 연도별 K-Drama Top 추천")

# ✅ 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv("kdrama.csv")
    
    # Rank 값 정제 (#1 → 1 형태)
    if "Rank" in df.columns:
        df["Rank_clean"] = (
            df["Rank"].astype(str)
            .str.replace("#", "", regex=False)
            .astype(float)
        )
    return df

df = load_data()

# ✅ 연도 목록 만들기
if "Year of release" in df.columns:
    years = sorted(df["Year of release"].dropna().unique(), reverse=True)
else:
    st.error("❌ 'Year of release' 컬럼이 없습니다.")
    st.stop()

selected_year = st.selectbox("📌 연도 선택", years)

# ✅ 선택 연도 필터링
filtered_df = df[df["Year of release"] == selected_year]

if filtered_df.empty:
    st.warning("😥 해당 연도에 방송된 드라마 정보가 없습니다.")
else:
    st.subheader(f"📌 {selected_year}년 Top Drama")
    
    # ✅ Rank 기준 최상위 콘텐츠 1개 추천
    filtered_sort = filtered_df.sort_values("Rank_clean", ascending=True).dropna(subset=["Rank_clean"])
    
    if filtered_sort.empty:
        st.warning("⚠️ Rank 데이터가 없습니다.")
    else:
        top1 = filtered_sort.iloc[0]
        
        st.success(f"🎖️ 올해의 TOP 드라마: **{top1['Name']}**")
        st.write(f"📊 Rank: `{top1['Rank']}`")
        st.write(f"🎭 Genre: `{top1['Genre']}`")
        st.write(f"📝 Synopsis: {top1['Synopsis']}")
        
        # ✅ 상세 정보 보기
        with st.expander("📘 상세 정보 보기"):
            st.dataframe(filtered_sort.head(10))  # Top 10 테이블
