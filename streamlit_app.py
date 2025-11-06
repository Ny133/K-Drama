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

st.title("📺 K-Drama Dashboard_GENRE")



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


# ====== 🎭 Genre-based Top Ranked Dramas ======
st.subheader("🎭 Genre-based Top Ranked Dramas")

# 필요한 컬럼 체크
required_cols = ["Name", "Genre", "Rank"]
if not all(col in df.columns for col in required_cols):
    st.error("❌ Required columns missing: Name, Genre, Rank")
else:
    # 장르 목록 생성
    genre_list = (
        df["Genre"]
        .dropna()
        .astype(str)
        .str.split(",")
        .explode()
        .str.strip()
        .unique()
    )
    genre_list = sorted(genre_list)

    selected_genre = st.selectbox("📌 Select a Genre", genre_list)

    if selected_genre:
        # 장르 포함한 작품 필터링
        filtered = df[
            df["Genre"].astype(str).str.contains(selected_genre, case=False, na=False)
        ].copy()

        if not filtered.empty:
            # Rank 오름차순 정렬 (Rank 1이 최고 순위)
            filtered["Rank"] = pd.to_numeric(filtered["Rank"], errors="coerce")
            filtered = filtered.dropna(subset=["Rank"])
            filtered = filtered.sort_values("Rank").reset_index(drop=True)

            # Top N 선택 슬라이더
            top_n = st.slider("Top N Results", 1, min(20, len(filtered)), 5)

            st.write(f"### ✅ Top {top_n} Dramas in *{selected_genre}*")
            show_cols = ["Rank", "Name", "Year", "Genre"]
            available_cols = [c for c in show_cols if c in filtered.columns]

            st.dataframe(filtered[available_cols].head(top_n))

            # 추천 카드 상위 3개
            st.markdown("### 🎯 Recommended Picks")
            top_card = filtered.head(min(3, top_n))

            for _, row in top_card.iterrows():
                st.markdown(
                    f"""
                    **#{int(row['Rank'])} — {row['Name']}**  
                    📅 Year: `{row.get('Year', 'Unknown')}`  
                    🎭 Genre: `{row['Genre']}`
                    """
                )
        else:
            st.warning("⚠️ No data for selected genre.")

