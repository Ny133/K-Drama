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

if "Genre" in df.columns and "_rating_clean" in df.columns:

    # 장르 목록 구성
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
        filtered = df[
            df["Genre"].astype(str).str.contains(selected_genre, case=False, na=False)
        ].dropna(subset=["_rating_clean"])

        if not filtered.empty:
            # 순위 계산
            filtered = filtered.sort_values("_rating_clean", ascending=False).reset_index(drop=True)
            filtered["Rank"] = filtered.index + 1

            # Top N slider
            top_n = st.slider("Top N Results", min_value=1, max_value=20, value=5)

            # 시각적으로 보기 좋게 Display
            st.write(f"### ✅ Top {top_n} Dramas in {selected_genre}")
            display_cols = [c for c in df.columns if c not in ["_rating_clean"]]
            st.dataframe(filtered[["Rank", col_name, "_rating_clean"] + display_cols[1:]].head(top_n))

            # 카드 방식 추천 (상위 3)
            st.markdown("### 🎯 Recommended Picks")
            top_card = filtered.head(min(3, top_n))
            for _, row in top_card.iterrows():
                st.markdown(
                    f"""
                    **#{row['Rank']} — {row[col_name]}**
                    ⭐ `{row['_rating_clean']}`
                    📅 `{row.get('Year', 'Unknown')}`
                    """
                )

        else:
            st.warning("⚠️ No valid rating data for this genre.")
else:
    st.error("❌ Genre or cleaned rating column is missing.")
