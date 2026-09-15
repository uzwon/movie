# ============================================================
# 날짜별 박스오피스 - Streamlit 앱
# ============================================================

import requests
import pandas as pd
import streamlit as st

# datetime, zoneinfo는 파이썬 기본 라이브러리라
# requirements.txt에 따로 적지 않아도 됩니다.
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# ============================================================
# 1. 페이지 기본 설정
# ============================================================

st.set_page_config(
    page_title="오늘의 시네마 박스오피스",
    page_icon="🎬",
    layout="wide"
)


# ============================================================
# 2. 영화관 느낌 CSS 디자인
# ============================================================

st.markdown(
    """
<style>

/* ------------------------------------------------
전체 화면
짙은 빨간색 영화관 커튼 느낌
------------------------------------------------ */
.stApp {
    background:
        radial-gradient(
            circle at top,
            #9e1b32 0%,
            #721426 35%,
            #470b17 70%,
            #25050c 100%
        );
}


/* 중앙 콘텐츠 */
.block-container {
    max-width: 1150px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}


/* ------------------------------------------------
메인 타이틀
------------------------------------------------ */
.cinema-label {
    text-align: center;
    color: #f3c66a;
    font-size: 13px;
    letter-spacing: 5px;
    font-weight: 800;
    margin-bottom: 10px;
}


.cinema-title {
    text-align: center;
    color: #fff8e8;
    font-size: 48px;
    font-weight: 900;
    margin-bottom: 7px;
}


.cinema-subtitle {
    text-align: center;
    color: #e7c8c8;
    font-size: 15px;
    margin-bottom: 30px;
}


/* 금색 장식선 */
.gold-line {
    width: 80px;
    height: 3px;
    margin: 0 auto 35px auto;

    background: linear-gradient(
        90deg,
        #c89232,
        #ffe19a,
        #c89232
    );

    border-radius: 10px;
}


/* ------------------------------------------------
날짜 선택 영역
------------------------------------------------ */
.date-box {
    background: rgba(255, 248, 232, 0.96);
    border: 2px solid #d6aa54;
    border-radius: 18px;
    padding: 22px 25px 10px 25px;
    margin-bottom: 25px;

    box-shadow:
        0 10px 30px rgba(0,0,0,0.25);
}


/* 날짜 선택 위젯 글자 */
.stDateInput label {
    color: #fff5e5 !important;
    font-weight: 800 !important;
}


/* ------------------------------------------------
일반 Streamlit 글자
------------------------------------------------ */
h1, h2, h3 {
    color: #fff7e9 !important;
}


/* ------------------------------------------------
Metric 카드
------------------------------------------------ */
div[data-testid="stMetric"] {

    background: rgba(255, 248, 232, 0.97);

    border: 2px solid #d8af5f;

    border-radius: 16px;

    padding: 18px 20px;

    box-shadow:
        0px 9px 25px rgba(0, 0, 0, 0.20);
}


div[data-testid="stMetricLabel"] {
    color: #7c2434;
    font-weight: 800;
}


div[data-testid="stMetricValue"] {
    color: #2b1718;
    font-weight: 900;
}


/* ------------------------------------------------
1위 / 2위 비교 카드
------------------------------------------------ */
.movie-card {

    background:
        linear-gradient(
            145deg,
            #fffaf0,
            #f8e7ca
        );

    border: 2px solid #d7ad5a;

    border-radius: 20px;

    padding: 28px;

    min-height: 310px;

    box-shadow:
        0 10px 30px rgba(0,0,0,0.25);
}


.rank-number {

    color: #a51e36;

    font-size: 14px;

    font-weight: 900;

    letter-spacing: 3px;
}


.movie-title {

    color: #321517;

    font-size: 28px;

    font-weight: 900;

    margin-top: 10px;

    margin-bottom: 18px;
}


.movie-info {

    color: #5f4141;

    font-size: 15px;

    line-height: 2;
}


.star-info {

    margin-top: 18px;

    padding: 14px;

    background: rgba(255,255,255,0.65);

    border-radius: 12px;

    color: #725e46;

    font-size: 13px;

    line-height: 1.7;
}


/* ------------------------------------------------
관객수 비교
------------------------------------------------ */
.compare-title {

    margin-top: 35px;

    margin-bottom: 15px;

    color: #ffe6a6;

    font-size: 20px;

    font-weight: 800;
}


/* ------------------------------------------------
설명 박스
------------------------------------------------ */
.notice-box {

    background: rgba(255, 245, 225, 0.96);

    color: #573b3b;

    border-left: 6px solid #d5a44b;

    padding: 18px 22px;

    border-radius: 10px;

    margin-top: 20px;

    line-height: 1.8;
}


/* ------------------------------------------------
푸터
------------------------------------------------ */
.footer {

    text-align: center;

    color: #d8aeb4;

    margin-top: 50px;

    font-size: 12px;

    letter-spacing: 1px;
}


/* dataframe 주변 흰 배경 완화 */
div[data-testid="stDataFrame"] {

    background-color: white;

    border-radius: 10px;
}


/* bar chart 카드 느낌 */
div[data-testid="stVegaLiteChart"] {

    background: rgba(255,255,255,0.97);

    border-radius: 14px;

    padding: 10px;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# 3. 상단 제목
# ============================================================

st.markdown(
    '<div class="cinema-label">DAILY CINEMA</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="cinema-title">🎬 CINEMA BOX OFFICE 🍿</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="cinema-subtitle">'
    '원하는 날짜를 골라 그날의 박스오피스를 확인해 보세요.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="gold-line"></div>',
    unsafe_allow_html=True
)


# ============================================================
# 4. 한국 시간 기준 어제 계산
# ============================================================

# Streamlit Cloud 서버가 한국에 있지 않을 수 있으므로
# 반드시 한국 시간대를 직접 지정합니다.

korea_now = datetime.now(
    ZoneInfo("Asia/Seoul")
)

today_korea = korea_now.date()

# 오늘 자료는 아직 집계되지 않았기 때문에
# 사용자가 고를 수 있는 마지막 날짜는 어제입니다.

yesterday = today_korea - timedelta(days=1)


# ============================================================
# 5. 날짜 선택 달력
# ============================================================

selected_date = st.date_input(

    "📅 박스오피스를 확인할 날짜",

    # 처음 앱을 열면 어제가 선택되어 있습니다.
    value=yesterday,

    # 오늘이나 미래 날짜는 선택할 수 없습니다.
    max_value=yesterday
)


# API에서 요구하는 yyyymmdd 형식으로 변환
target_date = selected_date.strftime("%Y%m%d")

# 사용자에게 표시할 날짜
display_date = selected_date.strftime(
    "%Y년 %m월 %d일"
)


st.markdown(
    f"""
<div class="notice-box">
🎟️ 현재 선택된 날짜는 <b>{display_date}</b>입니다.
</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# 6. Streamlit Secrets에서 KOBIS 인증키 가져오기
# ============================================================

try:

    KOBIS_KEY = st.secrets["KOBIS_KEY"]


except KeyError:

    st.error(
        "🔑 KOBIS 인증키가 등록되어 있지 않습니다."
    )

    st.info(
        """
        Streamlit Cloud의 **Secrets**에 다음과 같이 등록해 주세요.

        `KOBIS_KEY = "발급받은_인증키"`

        인증키는 main.py 코드 안에 직접 입력하지 마세요.
        """
    )

    st.stop()


# ============================================================
# 7. KOBIS 일일 박스오피스 API 주소
# ============================================================

API_URL = (
    "https://www.kobis.or.kr/"
    "kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)


# ============================================================
# 8. API 호출 함수
# ============================================================

@st.cache_data(ttl=3600)
def get_boxoffice_data(api_key, date):

    # KOBIS에 전달할 값
    params = {

        "key": api_key,

        "targetDt": date
    }


    # 인터넷을 통해 API 요청
    response = requests.get(

        API_URL,

        params=params,

        timeout=15
    )


    # 400, 500 등의 HTTP 오류가 있다면
    # 여기서 예외를 발생시킵니다.
    response.raise_for_status()


    # JSON 데이터를 Python 딕셔너리로 변환
    return response.json()


# ============================================================
# 9. API 요청
# ============================================================

try:

    data = get_boxoffice_data(
        KOBIS_KEY,
        target_date
    )


except requests.exceptions.Timeout:

    st.error(
        "⏰ KOBIS 서버의 응답 시간이 너무 오래 걸리고 있습니다."
    )

    st.info(
        "잠시 후 다시 시도해 주세요."
    )

    st.stop()


except requests.exceptions.RequestException as error:

    st.error(
        "🚨 KOBIS 서버에서 데이터를 불러오지 못했습니다."
    )

    st.info(
        """
        다음 사항을 확인해 주세요.

        - 인터넷 연결 상태
        - KOBIS 서버가 정상적으로 운영 중인지
        - API 주소가 올바른지
        """
    )

    st.caption(
        f"오류 정보: {error}"
    )

    st.stop()


except ValueError:

    st.error(
        "🚨 KOBIS 응답을 JSON으로 읽을 수 없습니다."
    )

    st.info(
        "잠시 후 다시 시도하거나 KOBIS 서비스 상태를 확인해 주세요."
    )

    st.stop()


except Exception as error:

    st.error(
        "🚨 데이터를 처리하는 중 오류가 발생했습니다."
    )

    st.caption(
        f"오류 정보: {error}"
    )

    st.stop()


# ============================================================
# 10. faultInfo 검사
# ============================================================

# KOBIS는 인증키가 틀린 경우에도
# HTTP 상태 코드 200이 올 수 있습니다.
#
# 따라서 faultInfo가 있는지 따로 확인해야 합니다.

if "faultInfo" in data:

    fault = data["faultInfo"]


    st.error(
        "🚨 KOBIS API에서 오류 응답을 보냈습니다."
    )


    if isinstance(fault, dict):

        message = (

            fault.get("message")

            or fault.get("errorMessage")

            or "오류 메시지가 없습니다."
        )


        st.warning(
            f"KOBIS 응답: {message}"
        )


    st.info(
        """
        다음 사항을 확인해 주세요.

        - Streamlit Secrets의 KOBIS_KEY가 정확한지
        - 인증키가 활성화되어 있는지
        - 인증키 앞뒤에 공백이 없는지
        """
    )

    st.stop()


# ============================================================
# 11. 영화 목록 가져오기
# ============================================================

try:

    movie_list = (
        data["boxOfficeResult"]
        ["dailyBoxOfficeList"]
    )


except (KeyError, TypeError):

    st.error(
        "🚨 박스오피스 데이터를 찾을 수 없습니다."
    )

    st.info(
        """
        정상 응답이라면

        boxOfficeResult → dailyBoxOfficeList

        안에 영화 목록이 있어야 합니다.
        """
    )

    st.stop()


# ============================================================
# 12. 영화 목록이 없는 경우
# ============================================================

if not movie_list:

    st.warning(
        "🎬 그날은 아직 집계 전입니다."
    )

    st.info(
        """
        선택한 날짜의 영화 목록이 아직 제공되지 않고 있습니다.

        다른 날짜를 골라 다시 확인해 주세요.
        """
    )

    st.stop()


# ============================================================
# 13. API 자료를 표 형태로 정리
# ============================================================

rows = []


for movie in movie_list:

    # 숫자 값이 모두 문자열이므로 int로 변환합니다.

    rank = int(
        movie.get("rank", 0)
    )

    rank_change = int(
        movie.get("rankInten", 0)
    )

    audience = int(
        movie.get("audiCnt", 0)
    )

    accumulated = int(
        movie.get("audiAcc", 0)
    )

    screens = int(
        movie.get("scrnCnt", 0)
    )


    # ------------------------------------------
    # 전날 대비 순위 증감 표시
    # ------------------------------------------

    if rank_change > 0:

        rank_text = f"▲ {rank_change}"

    elif rank_change < 0:

        # 음수 부호 대신 절댓값을 사용
        rank_text = f"▼ {abs(rank_change)}"

    else:

        rank_text = "－"


    # ------------------------------------------
    # 누적 관객 100만 이상 영화 표시
    # ------------------------------------------

    movie_name = movie.get(
        "movieNm",
        ""
    )


    if accumulated >= 1_000_000:

        movie_name += " 🏆 ❗"


    rows.append(

        {
            "순위": rank,

            "순위 변동": rank_text,

            "영화명": movie_name,

            "개봉일": movie.get(
                "openDt",
                ""
            ),

            "관객수": audience,

            "누적관객": accumulated,

            "스크린수": screens
        }
    )


# DataFrame 만들기
df = pd.DataFrame(rows)


# 순위 순서대로 정렬
df = (
    df
    .sort_values("순위")
    .reset_index(drop=True)
)


# ============================================================
# 14. 1위 영화 지표 카드
# ============================================================

first = df.iloc[0]


st.markdown("---")

st.subheader(
    f"🏆 {display_date} 박스오피스 1위"
)


metric1, metric2, metric3 = st.columns(3)


with metric1:

    st.metric(

        "🎞️ 영화",

        first["영화명"]
    )


with metric2:

    st.metric(

        "👥 당일 관객수",

        f"{first['관객수']:,}명"
    )


with metric3:

    st.metric(

        "🍿 누적 관객수",

        f"{first['누적관객']:,}명"
    )


# ============================================================
# 15. 1위와 2위 영화 비교
# ============================================================

st.markdown(
    '<div class="compare-title">'
    '🥇 TOP 1 vs 🥈 TOP 2'
    '</div>',
    unsafe_allow_html=True
)


# 혹시 영화가 한 편밖에 없는 경우도 대비
if len(df) >= 2:

    movie1 = df.iloc[0]

    movie2 = df.iloc[1]


    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # 1위 카드
    # --------------------------------------------------------

    with col1:

        st.markdown(
            f"""
<div class="movie-card">

<div class="rank-number">
RANK 01
</div>

<div class="movie-title">
🥇 {movie1["영화명"]}
</div>

<div class="movie-info">

<b>당일 관객수</b><br>
{movie1["관객수"]:,}명

<br><br>

<b>누적 관객수</b><br>
{movie1["누적관객"]:,}명

<br><br>

<b>스크린 수</b><br>
{movie1["스크린수"]:,}개

</div>

<div class="star-info">

⭐ <b>관람객 별점</b><br>
KOBIS 일일 박스오피스 API에서 제공하지 않는 정보입니다.

<br><br>

💬 <b>관람객 한줄평 요약</b><br>
KOBIS API에는 실제 관람객 리뷰 데이터가 포함되어 있지 않습니다.

</div>

</div>
""",
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # 2위 카드
    # --------------------------------------------------------

    with col2:

        st.markdown(
            f"""
<div class="movie-card">

<div class="rank-number">
RANK 02
</div>

<div class="movie-title">
🥈 {movie2["영화명"]}
</div>

<div class="movie-info">

<b>당일 관객수</b><br>
{movie2["관객수"]:,}명

<br><br>

<b>누적 관객수</b><br>
{movie2["누적관객"]:,}명

<br><br>

<b>스크린 수</b><br>
{movie2["스크린수"]:,}개

</div>

<div class="star-info">

⭐ <b>관람객 별점</b><br>
KOBIS 일일 박스오피스 API에서 제공하지 않는 정보입니다.

<br><br>

💬 <b>관람객 한줄평 요약</b><br>
KOBIS API에는 실제 관람객 리뷰 데이터가 포함되어 있지 않습니다.

</div>

</div>
""",
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # 두 영화 관객수 차이
    # --------------------------------------------------------

    audience_difference = (
        movie1["관객수"]
        - movie2["관객수"]
    )


    st.info(
        f"🎟️ 이날 1위 **{movie1['영화명']}**은 "
        f"2위 **{movie2['영화명']}**보다 "
        f"**{audience_difference:,}명** 더 많은 관객을 기록했습니다."
    )


else:

    st.info(
        "이 날짜에는 1위와 2위를 비교할 만큼 충분한 영화 데이터가 없습니다."
    )


# ============================================================
# 16. 관객수 상위 5편 막대그래프
# ============================================================

st.markdown("---")

st.subheader(
    "🍿 관객수 TOP 5"
)


top5 = (

    df.nlargest(
        5,
        "관객수"
    )

    [
        [
            "영화명",
            "관객수"
        ]
    ]

    .copy()
)


# 인덱스를 영화명으로 변경
top5_chart = top5.set_index(
    "영화명"
)


st.bar_chart(

    top5_chart,

    y="관객수"
)


# ============================================================
# 17. 전체 박스오피스 표
# ============================================================

st.markdown("---")

st.subheader(
    "🎟️ 전체 박스오피스"
)


table_df = df.copy()


# 천 단위 쉼표 표시
table_df["관객수"] = (
    table_df["관객수"]
    .map(lambda x: f"{x:,}")
)


table_df["누적관객"] = (
    table_df["누적관객"]
    .map(lambda x: f"{x:,}")
)


table_df["스크린수"] = (
    table_df["스크린수"]
    .map(lambda x: f"{x:,}")
)


# ============================================================
# 18. 순위 변동 색상 함수
# ============================================================

def color_rank_change(value):

    # ▲가 들어 있으면 빨간색
    if "▲" in str(value):

        return (
            "color: #d62728;"
            "font-weight: bold;"
        )


    # ▼가 들어 있으면 파란색
    elif "▼" in str(value):

        return (
            "color: #2368c4;"
            "font-weight: bold;"
        )


    # 변화가 없으면 회색
    else:

        return (
            "color: #777777;"
        )


# 순위 변동 열에만 색을 적용
styled_table = (

    table_df.style

    .map(
        color_rank_change,
        subset=["순위 변동"]
    )
)


st.dataframe(

    styled_table,

    width="stretch",

    hide_index=True
)


# ============================================================
# 19. 표 설명
# ============================================================

st.markdown(
    """
<div class="notice-box">

<b>📌 표 읽는 방법</b><br><br>

🔺 <b style="color:#d62728;">빨간 ▲</b>
: 전날보다 순위가 오른 영화<br>

🔻 <b style="color:#2368c4;">파란 ▼</b>
: 전날보다 순위가 내려간 영화<br>

🏆 ❗
: 누적 관객수가 100만 명 이상인 영화

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# 20. 별점 / 리뷰 안내
# ============================================================

st.markdown(
    """
<div class="notice-box">

<b>⭐ 별점과 감상평에 대하여</b><br><br>

현재 사용하는 KOBIS 일일 박스오피스 API에는
관객 별점이나 실제 관람객 리뷰가 포함되어 있지 않습니다.

따라서 존재하지 않는 별점이나 감상평을 임의로 만들어 표시하지 않고,
현재 화면에서는 해당 데이터가 제공되지 않는다는 사실을 표시합니다.

추후 실제 별점·리뷰 데이터를 제공하는 별도의 API를 연결하면
1위와 2위의 별점 비교와 관람객 한줄평 요약 기능을 추가할 수 있습니다.

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# 21. Footer
# ============================================================

st.markdown(
    f"""
<div class="footer">

🎬 CINEMA BOX OFFICE · {display_date}<br><br>

영화진흥위원회 KOBIS 영화관입장권통합전산망 OpenAPI

</div>
""",
    unsafe_allow_html=True
)
