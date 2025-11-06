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

st.subheader("⭐ Rating Distribution (debug & safe)")

# 1) 원본 샘플과 타입 확인 (문제 진단용)
st.write("원본 샘플 (최대 20개):")
st.write(df[col_rating].head(20))
st.write("dtype:", df[col_rating].dtype)
st.write("고유값 예시 (최대 50):")
st.write(df[col_rating].dropna().unique()[:50])

# 2) 숫자 추출 및 정제
# 숫자 패턴(예: 9, 9.2, 9,2, 9.2/10 등)에서 첫 번째 숫자 그룹을 추출
rating_clean = (
    df[col_rating]
    .astype(str)                                # 우선 문자열로
    .str.extract(r'([0-9]+[.,]?[0-9]*)')[0]    # 숫자(소수점 포함) 추출
    .str.replace(',', '.', regex=False)         # 콤마 소수 -> 점으로
)

# 숫자로 변환 (변환 불가 항목은 NaN)
rating_clean = pd.to_numeric(rating_clean, errors="coerce")

# 정제 결과 컬럼 추가(원본 보존)
df["_rating_clean"] = rating_clean

st.write("정제된 샘플:")
st.write(df[["_rating_clean"]].head(20))

# 3) 유효한 값이 충분한지 체크
num_valid = df["_rating_clean"].notna().sum()
st.write(f"정제된 유효 Rating 개수: {num_valid}")

if num_valid == 0:
    st.warning("⚠️ 정제 후 유효한 Rating 값이 없습니다. 원본 데이터를 확인해 주세요.")
    # 유효값이 없으면 원본 고유값 일부 보여주기
    st.write(df[col_rating].dropna().unique()[:100])
else:
    # 4) 히스토그램 그리기 (nbins 조정 가능)
    fig_rating = px.histogram(
        df,
        x="_rating_clean",
        nbins=20,
        title="Rating Distribution (cleaned)",
        labels={"_rating_clean": "Rating"}
    )
    # 축 범위나 레이아웃 더 깔끔히 하고 싶으면 update_layout 사용
    fig_rating.update_layout(xaxis_title="Rating", yaxis_title="Count", bargap=0.05)
    st.plotly_chart(fig_rating, use_container_width=True)

    # 추가: 기초 통계 출력
    st.write("기초 통계 (정제된 Rating):")
    st.write(df["_rating_clean"].describe())

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

