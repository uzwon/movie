# ============================================================
# 어제의 박스오피스 - Streamlit 앱
# ============================================================

import requests
import pandas as pd
import streamlit as st

# Python 기본 라이브러리이므로 따로 설치할 필요가 없습니다.
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# ============================================================
# 1. 페이지 기본 설정
# ============================================================

st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 어제의 박스오피스")
st.caption("KOBIS 영화관입장권통합전산망 일일 박스오피스")


# ============================================================
# 2. 한국 시간 기준으로 '어제' 날짜 계산
# ============================================================

# Streamlit Cloud 서버는 한국 시간으로 동작하지 않을 수 있으므로
# 반드시 Asia/Seoul 시간대를 직접 지정합니다.
korea_time = datetime.now(ZoneInfo("Asia/Seoul"))

# 오늘에서 하루를 빼서 어제 날짜를 구합니다.
yesterday = korea_time.date() - timedelta(days=1)

# KOBIS API가 요구하는 형식: yyyymmdd
target_date = yesterday.strftime("%Y%m%d")

# 화면에 보여 줄 날짜 형식
display_date = yesterday.strftime("%Y년 %m월 %d일")

st.subheader(f"📅 {display_date} 박스오피스")


# ============================================================
# 3. secrets에서 KOBIS 인증키 불러오기
# ============================================================

# 인증키는 코드에 직접 적지 않고
# Streamlit Cloud의 Secrets에 저장해야 합니다.
try:
    KOBIS_KEY = st.secrets["KOBIS_KEY"]

except KeyError:
    st.error("🔑 KOBIS 인증키를 찾을 수 없습니다.")

    st.info(
        """
        Streamlit Cloud의 **Secrets**에 인증키를 등록해 주세요.

        다음과 같은 형식으로 입력하면 됩니다.

        `KOBIS_KEY = "발급받은_인증키"`

        인증키를 등록한 뒤 앱을 다시 실행해 주세요.
        """
    )

    # 인증키가 없으면 아래 코드를 실행하지 않습니다.
    st.stop()


# ============================================================
# 4. KOBIS API 주소
# ============================================================

API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)


# ============================================================
# 5. KOBIS API 호출 함수
# ============================================================

@st.cache_data(ttl=3600)
def get_boxoffice_data(api_key, date):

    # API에 전달할 요청 변수입니다.
    params = {
        "key": api_key,
        "targetDt": date
    }

    # 최대 15초 동안 응답을 기다립니다.
    response = requests.get(
        API_URL,
        params=params,
        timeout=15
    )

    # HTTP 오류가 발생하면 예외를 발생시킵니다.
    response.raise_for_status()

    # JSON 형식의 응답을 Python 딕셔너리로 변환합니다.
    return response.json()


# ============================================================
# 6. API 요청
# ============================================================

try:

    data = get_boxoffice_data(
        KOBIS_KEY,
        target_date
    )


# 인터넷 연결 문제, 서버 문제, 시간 초과 등이 발생한 경우
except requests.exceptions.RequestException as error:

    st.error("🚨 KOBIS 서버에서 데이터를 불러오지 못했습니다.")

    st.info(
        """
        다음 내용을 확인해 주세요.

        - 인터넷 연결 상태
        - KOBIS 서버의 일시적인 장애 여부
        - API 요청 주소가 올바른지
        - 잠시 후 다시 실행했을 때 정상적으로 동작하는지
        """
    )

    st.caption(f"오류 정보: {error}")

    st.stop()


# JSON 응답을 읽지 못한 경우
except ValueError:

    st.error("🚨 서버 응답을 JSON 형식으로 읽을 수 없습니다.")

    st.info(
        """
        KOBIS 서버에서 예상하지 못한 형식의 응답이 왔습니다.

        잠시 후 다시 실행하거나
        KOBIS OpenAPI 서비스 상태를 확인해 주세요.
        """
    )

    st.stop()


# 그 밖의 예상하지 못한 오류
except Exception as error:

    st.error("🚨 데이터를 처리하는 중 예상하지 못한 오류가 발생했습니다.")

    st.info(
        """
        다음 사항을 확인해 주세요.

        - Streamlit Secrets에 인증키가 정상적으로 저장되어 있는지
        - 인터넷 연결이 정상인지
        - KOBIS OpenAPI 서비스가 정상 운영 중인지
        """
    )

    st.caption(f"오류 정보: {error}")

    st.stop()


# ============================================================
# 7. KOBIS의 faultInfo 오류 확인
# ============================================================

# KOBIS는 인증키가 틀려도 HTTP 상태코드 200을 보낼 수 있고,
# 정상 데이터 대신 faultInfo를 반환할 수 있습니다.
if "faultInfo" in data:

    fault = data["faultInfo"]

    st.error("🚨 KOBIS API에서 오류 응답을 보냈습니다.")

    # faultInfo 안의 메시지가 있다면 함께 표시합니다.
    if isinstance(fault, dict):

        error_message = (
            fault.get("message")
            or fault.get("errorMessage")
            or "오류 메시지를 확인할 수 없습니다."
        )

        st.warning(f"KOBIS 응답: {error_message}")

    st.info(
        """
        다음 내용을 확인해 주세요.

        - Streamlit Secrets의 `KOBIS_KEY`가 정확한지
        - KOBIS OpenAPI에서 발급받은 인증키가 활성화되어 있는지
        - 인증키 앞뒤에 불필요한 공백이 들어가 있지 않은지
        """
    )

    st.stop()


# ============================================================
# 8. 영화 목록 가져오기
# ============================================================

try:

    movie_list = data["boxOfficeResult"]["dailyBoxOfficeList"]

except (KeyError, TypeError):

    st.error("🚨 예상한 형태의 박스오피스 데이터를 찾을 수 없습니다.")

    st.info(
        """
        KOBIS API 응답 구조가 정상적인지 확인해 주세요.

        정상적인 경우에는

        `boxOfficeResult → dailyBoxOfficeList`

        안에 영화 목록이 들어 있어야 합니다.
        """
    )

    st.stop()


# 영화 목록이 비어 있는 경우
if not movie_list:

    st.warning("📭 해당 날짜의 박스오피스 영화 목록이 비어 있습니다.")

    st.info(
        """
        다음 내용을 확인해 주세요.

        - 조회 날짜의 박스오피스 집계가 완료되었는지
        - KOBIS에서 해당 날짜의 데이터가 제공되는지
        - API 인증키가 정상적으로 작동하는지

        이 앱은 한국 시간 기준으로 자동 계산한 **어제 날짜**를 조회합니다.
        """
    )

    st.stop()


# ============================================================
# 9. 필요한 데이터만 정리
# ============================================================

rows = []

for movie in movie_list:

    # KOBIS의 숫자 값은 문자열로 오므로
    # int()를 이용해 숫자로 변환합니다.
    rows.append(
        {
            "순위": int(movie.get("rank", 0)),
            "영화명": movie.get("movieNm", ""),
            "개봉일": movie.get("openDt", ""),
            "관객수": int(movie.get("audiCnt", 0)),
            "누적관객": int(movie.get("audiAcc", 0)),
            "스크린수": int(movie.get("scrnCnt", 0)),
        }
    )


# 리스트를 표 형태로 다루기 위해 DataFrame으로 변환합니다.
df = pd.DataFrame(rows)

# 순위가 낮은 숫자부터 정렬합니다.
df = df.sort_values("순위").reset_index(drop=True)


# ============================================================
# 10. 1위 영화 정보
# ============================================================

first_movie = df.iloc[0]

st.markdown("---")

st.subheader("🏆 박스오피스 1위")


# 세 개의 지표 카드를 나란히 배치합니다.
card1, card2, card3 = st.columns(3)


with card1:

    st.metric(
        label="🎞️ 1위 영화",
        value=first_movie["영화명"]
    )


with card2:

    st.metric(
        label="👥 어제 관객수",
        value=f"{first_movie['관객수']:,}명"
    )


with card3:

    st.metric(
        label="🎟️ 누적 관객수",
        value=f"{first_movie['누적관객']:,}명"
    )


# ============================================================
# 11. 관객수 상위 5편 막대그래프
# ============================================================

st.markdown("---")

st.subheader("📊 관객수 상위 5편")


# 관객수를 기준으로 상위 5편을 선택합니다.
top5 = (
    df.nlargest(5, "관객수")
    [["영화명", "관객수"]]
    .copy()
)


# 영화명을 그래프의 가로축 이름으로 사용합니다.
chart_data = top5.set_index("영화명")


# Streamlit 기본 막대그래프 기능을 사용합니다.
# 별도의 그래프 라이브러리를 추가로 설치할 필요가 없습니다.
st.bar_chart(
    chart_data,
    y="관객수"
)


# ============================================================
# 12. 전체 박스오피스 표
# ============================================================

st.markdown("---")

st.subheader("📋 일일 박스오피스 순위")


# 숫자를 읽기 쉽게 천 단위 구분 기호를 적용할 별도 표를 만듭니다.
table_df = df.copy()

table_df["관객수"] = table_df["관객수"].map(
    lambda x: f"{x:,}"
)

table_df["누적관객"] = table_df["누적관객"].map(
    lambda x: f"{x:,}"
)

table_df["스크린수"] = table_df["스크린수"].map(
    lambda x: f"{x:,}"
)


# 사용자가 요청한 순서대로 열을 표시합니다.
table_df = table_df[
    [
        "순위",
        "영화명",
        "개봉일",
        "관객수",
        "누적관객",
        "스크린수"
    ]
]


st.dataframe(
    table_df,
    width="stretch",
    hide_index=True
)


# ============================================================
# 13. 하단 설명
# ============================================================

st.markdown("---")

st.caption(
    f"📅 조회 기준일: {display_date} · "
    "한국 시간(Asia/Seoul) 기준으로 자동 계산된 어제 날짜"
)

st.caption(
    "출처: 영화진흥위원회 KOBIS 영화관입장권통합전산망 OpenAPI"
)
