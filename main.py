# ============================================================
# 날짜별 박스오피스 - Streamlit 앱
# ============================================================

import requests
import pandas as pd
import streamlit as st

# datetime과 zoneinfo는 파이썬 기본 기능이라
# requirements.txt에 따로 적지 않아도 됩니다.
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# ============================================================
# 1. 페이지 기본 설정
# ============================================================

st.set_page_config(
    page_title="오늘 뭐 보지? 🎬",
    page_icon="🍿",
    layout="wide"
)


# ============================================================
# 2. 영화관 느낌의 화면 디자인
# ============================================================

st.markdown(
    """
<style>

/* ---------------------------------
   전체 배경
---------------------------------- */
.stApp {
    background:
        radial-gradient(circle at 10% 10%, #fff2a8 0%, transparent 25%),
        radial-gradient(circle at 90% 15%, #ffc9d9 0%, transparent 25%),
        radial-gradient(circle at 15% 90%, #cfe5ff 0%, transparent 26%),
        linear-gradient(135deg, #fffaf2 0%, #fff4f7 48%, #f3f1ff 100%);
}


/* ---------------------------------
   전체 내용 폭
---------------------------------- */
.block-container {
    max-width: 1200px;
    padding-top: 2.8rem;
    padding-bottom: 4rem;
}


/* ---------------------------------
   상단 작은 문구
---------------------------------- */
.cinema-label {
    text-align: center;
    color: #e45062;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 4px;
    margin-bottom: 10px;
}


/* ---------------------------------
   메인 제목
---------------------------------- */
.cinema-title {
    text-align: center;
    font-size: 48px;
    font-weight: 900;
    color: #29243a;
    letter-spacing: -2px;
    margin-bottom: 8px;
}


/* ---------------------------------
   설명
---------------------------------- */
.cinema-subtitle {
    text-align: center;
    color: #777085;
    font-size: 16px;
    margin-bottom: 35px;
}


/* ---------------------------------
   날짜 선택창
---------------------------------- */
div[data-testid="stDateInput"] > div {
    background: rgba(255, 255, 255, 0.80);
    border-radius: 16px;
}


/* ---------------------------------
   지표 카드
---------------------------------- */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.88);
    border: 1px solid rgba(255,255,255,0.95);
    border-radius: 20px;
    padding: 20px 22px;
    box-shadow: 0px 10px 28px rgba(65, 55, 85, 0.08);
}


/* ---------------------------------
   소제목
---------------------------------- */
h2, h3 {
    color: #302a42;
}


/* ---------------------------------
   안내 박스 느낌
---------------------------------- */
.info-box {
    background: rgba(255,255,255,0.72);
    border-radius: 18px;
    padding: 18px 22px;
    margin-top: 18px;
    color: #676071;
    line-height: 1.8;
    border: 1px solid rgba(255,255,255,0.9);
}


/* ---------------------------------
   하단 문구
---------------------------------- */
.footer {
    text-align: center;
    color: #98919f;
    margin-top: 40px;
    font-size: 12px;
    line-height: 1.8;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# 3. 상단 제목
# ============================================================

st.markdown(
    '<div class="cinema-label">DAILY BOX OFFICE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="cinema-title">오늘 뭐 보지? 🎬🍿</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="cinema-subtitle">'
    '원하는 날짜를 선택하고 그날의 박스오피스를 확인해 보세요.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# 4. 한국 시간 기준 '어제' 계산
# ============================================================

# Streamlit Cloud 서버는 한국 시간이 아닐 수 있기 때문에
# Asia/Seoul 시간대를 직접 지정합니다.
korea_now = datetime.now(
    ZoneInfo("Asia/Seoul")
)

# 오늘 데이터는 아직 집계 전일 수 있으므로
# 가장 늦게 선택 가능한 날짜는 어제입니다.
yesterday = (
    korea_now.date()
    - timedelta(days=1)
)


# ============================================================
# 5. 날짜 선택
# ============================================================

selected_date = st.date_input(
    "📅 박스오피스 날짜 선택",
    value=yesterday,
    max_value=yesterday
)

# KOBIS API에서 사용하는 날짜 형식
# 예: 2026년 9월 14일 → 20260914
target_date = selected_date.strftime(
    "%Y%m%d"
)

# 사용자에게 보여 줄 날짜
display_date = selected_date.strftime(
    "%Y년 %m월 %d일"
)


# ============================================================
# 6. Secrets에서 KOBIS 인증키 읽기
# ============================================================

try:

    KOBIS_KEY = st.secrets[
        "KOBIS_KEY"
    ]

except KeyError:

    st.error(
        "🔑 KOBIS 인증키를 찾을 수 없습니다."
    )

    st.info(
        """
        Streamlit Cloud의 **Secrets**에
        KOBIS 인증키를 등록해 주세요.

        형식은 다음과 같습니다.

        `KOBIS_KEY = "발급받은_인증키"`

        인증키는 main.py에 직접 작성하지 마세요.
        """
    )

    st.stop()


# ============================================================
# 7. KOBIS API 주소
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
def get_boxoffice_data(
    api_key,
    date
):

    # KOBIS 서버로 전달할 값
    params = {
        "key": api_key,
        "targetDt": date
    }

    # API 요청
    response = requests.get(
        API_URL,
        params=params,
        timeout=15
    )

    # 400, 500 등의 HTTP 오류가 있으면
    # 오류를 발생시킵니다.
    response.raise_for_status()

    # JSON → 파이썬 딕셔너리
    return response.json()


# ============================================================
# 9. API 데이터 요청
# ============================================================

try:

    data = get_boxoffice_data(
        KOBIS_KEY,
        target_date
    )


# 인터넷, 서버, 시간 초과 등의 오류
except requests.exceptions.RequestException as error:

    st.error(
        "🚨 KOBIS 데이터를 불러오지 못했습니다."
    )

    st.info(
        """
        다음 내용을 확인해 주세요.

        - 인터넷 연결 상태
        - KOBIS 서버가 정상적으로 운영 중인지
        - API 주소가 올바른지
        - 잠시 뒤 다시 실행하면 정상적으로 동작하는지
        """
    )

    st.caption(
        f"오류 정보: {error}"
    )

    st.stop()


# JSON 처리 오류
except ValueError:

    st.error(
        "🚨 KOBIS 서버 응답을 읽을 수 없습니다."
    )

    st.info(
        """
        서버에서 정상적인 JSON 데이터가 오지 않았습니다.

        잠시 뒤 다시 시도하거나
        KOBIS OpenAPI 서비스 상태를 확인해 주세요.
        """
    )

    st.stop()


# 그 외 예상하지 못한 오류
except Exception as error:

    st.error(
        "🚨 데이터를 처리하는 중 오류가 발생했습니다."
    )

    st.info(
        """
        다음 내용을 확인해 주세요.

        - KOBIS_KEY가 Secrets에 올바르게 등록되어 있는지
        - 인터넷 연결이 정상인지
        - KOBIS OpenAPI 서비스가 정상인지
        """
    )

    st.caption(
        f"오류 정보: {error}"
    )

    st.stop()


# ============================================================
# 10. KOBIS faultInfo 확인
# ============================================================

# KOBIS는 인증키가 틀린 경우에도
# HTTP 상태코드가 200일 수 있습니다.
# 따라서 faultInfo가 있는지 별도로 확인해야 합니다.

if "faultInfo" in data:

    fault = data[
        "faultInfo"
    ]

    st.error(
        "🚨 KOBIS API에서 오류를 반환했습니다."
    )

    if isinstance(
        fault,
        dict
    ):

        fault_message = (
            fault.get("message")
            or fault.get("errorMessage")
            or "오류 내용을 확인할 수 없습니다."
        )

        st.warning(
            f"KOBIS 응답: {fault_message}"
        )

    st.info(
        """
        다음 내용을 확인해 주세요.

        - Streamlit Secrets의 `KOBIS_KEY`
        - 인증키에 오타가 없는지
        - 인증키 앞뒤에 공백이 없는지
        - KOBIS에서 발급된 인증키가 정상 상태인지
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

except (
    KeyError,
    TypeError
):

    st.error(
        "🚨 박스오피스 데이터를 찾을 수 없습니다."
    )

    st.info(
        """
        정상적인 KOBIS 응답에서는

        `boxOfficeResult → dailyBoxOfficeList`

        안에 영화 목록이 들어 있어야 합니다.

        API 응답 구조와 인증키를 확인해 주세요.
        """
    )

    st.stop()


# ============================================================
# 12. 영화 목록이 비어 있는 경우
# ============================================================

if not movie_list:

    st.warning(
        "🎞️ 그날은 아직 집계 전입니다."
    )

    st.info(
        f"""
        선택한 날짜는 **{display_date}**입니다.

        해당 날짜의 영화 목록이 아직 제공되지 않았습니다.

        KOBIS에서 집계가 완료된 뒤 다시 확인해 주세요.
        """
    )

    st.stop()


# ============================================================
# 13. 영화 데이터 정리
# ============================================================

rows = []


for movie in movie_list:

    # API 문서에 따르면 숫자도 문자열로 전달되므로
    # 계산하기 위해 int로 변환합니다.

    rank = int(
        movie.get(
            "rank",
            0
        )
    )

    rank_change = int(
        movie.get(
            "rankInten",
            0
        )
    )

    audience = int(
        movie.get(
            "audiCnt",
            0
        )
    )

    total_audience = int(
        movie.get(
            "audiAcc",
            0
        )
    )

    screen_count = int(
        movie.get(
            "scrnCnt",
            0
        )
    )


    # ----------------------------------------------
    # 전날 대비 순위 변동 표시
    # ----------------------------------------------

    if rank_change > 0:

        rank_display = (
            f"▲ {rank_change}"
        )

    elif rank_change < 0:

        rank_display = (
            f"▼ {abs(rank_change)}"
        )

    else:

        rank_display = "―"


    # ----------------------------------------------
    # 누적 관객 100만 명 초과 표시
    # ----------------------------------------------

    movie_name = movie.get(
        "movieNm",
        ""
    )

    if total_audience > 1_000_000:

        movie_name_display = (
            f"{movie_name} 🏆❗"
        )

    else:

        movie_name_display = movie_name


    # ----------------------------------------------
    # 한 영화의 정보를 딕셔너리로 저장
    # ----------------------------------------------

    rows.append(
        {
            "순위": rank,

            "순위 변동":
                rank_display,

            "영화명":
                movie_name_display,

            "원래영화명":
                movie_name,

            "개봉일":
                movie.get(
                    "openDt",
                    ""
                ),

            "관객수":
                audience,

            "누적관객":
                total_audience,

            "스크린수":
                screen_count,

            "순위증감값":
                rank_change
        }
    )


# ============================================================
# 14. DataFrame 만들기
# ============================================================

df = pd.DataFrame(
    rows
)

# 박스오피스 순위 순으로 정렬
df = (
    df.sort_values(
        "순위"
    )
    .reset_index(
        drop=True
    )
)


# ============================================================
# 15. 선택 날짜 표시
# ============================================================

st.markdown("---")

st.subheader(
    f"🎟️ {display_date} 박스오피스"
)


# ============================================================
# 16. 1위 영화 지표 카드
# ============================================================

first_movie = df.iloc[0]


metric1, metric2, metric3 = st.columns(
    3
)


with metric1:

    st.metric(
        label="🏆 박스오피스 1위",
        value=first_movie[
            "원래영화명"
        ]
    )


with metric2:

    st.metric(
        label="🍿 당일 관객수",
        value=(
            f"{first_movie['관객수']:,}명"
        )
    )


with metric3:

    st.metric(
        label="🎫 누적 관객수",
        value=(
            f"{first_movie['누적관객']:,}명"
        )
    )


# ============================================================
# 17. 관객수 상위 5편 막대그래프
# ============================================================

st.markdown("---")

st.subheader(
    "📊 관객수 TOP 5"
)


top5 = (
    df.nlargest(
        5,
        "관객수"
    )
    [
        [
            "원래영화명",
            "관객수"
        ]
    ]
    .copy()
)


# 그래프에 영화명을 표시하기 위해
# 영화명을 인덱스로 바꿉니다.
chart_data = (
    top5.set_index(
        "원래영화명"
    )
)


st.bar_chart(
    chart_data,
    y="관객수"
)


# ============================================================
# 18. 전체 박스오피스 표
# ============================================================

st.markdown("---")

st.subheader(
    "🎬 일일 박스오피스 순위"
)


# 표에 보여 줄 데이터만 복사
table_df = df[
    [
        "순위",
        "순위 변동",
        "영화명",
        "개봉일",
        "관객수",
        "누적관객",
        "스크린수"
    ]
].copy()


# 숫자에 천 단위 쉼표 적용
table_df["관객수"] = (
    table_df["관객수"]
    .map(
        lambda x: f"{x:,}"
    )
)

table_df["누적관객"] = (
    table_df["누적관객"]
    .map(
        lambda x: f"{x:,}"
    )
)

table_df["스크린수"] = (
    table_df["스크린수"]
    .map(
        lambda x: f"{x:,}"
    )
)


# ============================================================
# 19. 순위 변동 글자 색 지정 함수
# ============================================================

def color_rank_change(value):

    # ▲가 들어 있으면
    # 순위가 오른 것이므로 빨간색
    if "▲" in str(value):

        return (
            "color: #e53935; "
            "font-weight: bold;"
        )

    # ▼가 들어 있으면
    # 순위가 내려간 것이므로 파란색
    elif "▼" in str(value):

        return (
            "color: #2878d0; "
            "font-weight: bold;"
        )

    # 변동이 없으면 회색
    else:

        return (
            "color: #888888;"
        )


# Pandas Styler를 이용해
# '순위 변동' 열에만 색을 적용합니다.
styled_table = (
    table_df.style
    .map(
        color_rank_change,
        subset=[
            "순위 변동"
        ]
    )
)


st.dataframe(
    styled_table,
    width="stretch",
    hide_index=True
)


# ============================================================
# 20. 표 읽는 방법 안내
# ============================================================

st.markdown(
    """
<div class="info-box">

<b>🍿 표 보는 방법</b><br><br>

🔴 <b>▲ 숫자</b>
&nbsp; 전날보다 순위가 오른 영화<br>

🔵 <b>▼ 숫자</b>
&nbsp; 전날보다 순위가 내려간 영화<br>

➖ <b>―</b>
&nbsp; 전날과 순위가 같은 영화<br><br>

🏆❗
&nbsp; 누적 관객수가 <b>100만 명을 넘은 영화</b>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# 21. 하단 설명
# ============================================================

st.markdown(
    """
<div class="footer">

영화진흥위원회 KOBIS 영화관입장권통합전산망 OpenAPI<br>

오늘 날짜는 아직 집계가 완료되지 않을 수 있기 때문에
선택 가능한 가장 늦은 날짜는 한국 시간 기준 어제입니다.

</div>
""",
    unsafe_allow_html=True
)
