import streamlit as st
import pandas as pd

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# ============================================================
# 1. 페이지 기본 설정
# ============================================================

st.set_page_config(
    page_title="일일 사망원인 통계",
    page_icon="🏥",
    layout="wide"
)


# ============================================================
# 2. 병원 · 환자복 느낌 디자인
# ============================================================

st.markdown(
    """
<style>

/* ---------------------------------------------------------
전체 배경
병원 환자복의 옅은 파란 체크 패턴 느낌
--------------------------------------------------------- */

.stApp {

    background-color: #eef8fb;

    background-image:
        linear-gradient(
            90deg,
            rgba(104, 178, 201, 0.10) 1px,
            transparent 1px
        ),
        linear-gradient(
            rgba(104, 178, 201, 0.10) 1px,
            transparent 1px
        );

    background-size: 36px 36px;
}


/* 전체 본문 영역 */
.block-container {

    max-width: 1150px;

    padding-top: 2.5rem;

    padding-bottom: 4rem;
}


/* ---------------------------------------------------------
상단 제목
--------------------------------------------------------- */

.hospital-label {

    text-align: center;

    color: #43849a;

    font-size: 13px;

    letter-spacing: 5px;

    font-weight: 800;

    margin-bottom: 10px;
}


.main-title {

    text-align: center;

    color: #234b59;

    font-size: 45px;

    font-weight: 900;

    margin-bottom: 8px;
}


.subtitle {

    text-align: center;

    color: #66838d;

    font-size: 15px;

    margin-bottom: 30px;
}


/* 제목 아래 선 */

.title-line {

    width: 70px;

    height: 3px;

    background-color: #6eb2c5;

    margin: 0 auto 35px auto;

    border-radius: 10px;
}


/* ---------------------------------------------------------
날짜 선택
--------------------------------------------------------- */

.stDateInput label {

    color: #315866 !important;

    font-size: 16px;

    font-weight: 800 !important;
}


div[data-baseweb="input"] {

    border-radius: 10px;
}


/* ---------------------------------------------------------
Metric 카드
--------------------------------------------------------- */

div[data-testid="stMetric"] {

    background-color: rgba(255,255,255,0.94);

    border: 1px solid #c7e0e8;

    border-radius: 16px;

    padding: 20px;

    box-shadow:
        0 8px 22px rgba(60, 110, 130, 0.10);
}


div[data-testid="stMetricLabel"] {

    color: #60818d;

    font-weight: 700;
}


div[data-testid="stMetricValue"] {

    color: #264d5a;

    font-weight: 900;
}


/* ---------------------------------------------------------
1위 / 2위 비교 카드
--------------------------------------------------------- */

.cause-card {

    background: rgba(255,255,255,0.96);

    border: 1px solid #c7e1e8;

    border-radius: 18px;

    padding: 28px;

    min-height: 300px;

    box-shadow:
        0 9px 28px rgba(64, 115, 130, 0.10);
}


.rank-label {

    color: #5791a4;

    font-size: 13px;

    letter-spacing: 3px;

    font-weight: 900;
}


.cause-name {

    color: #244b58;

    font-size: 27px;

    font-weight: 900;

    margin-top: 10px;

    margin-bottom: 22px;
}


.cause-info {

    color: #57717a;

    font-size: 15px;

    line-height: 2;
}


/* ---------------------------------------------------------
설명 박스
--------------------------------------------------------- */

.notice-box {

    background: rgba(255,255,255,0.91);

    border-left: 5px solid #65aabd;

    border-radius: 10px;

    padding: 18px 20px;

    margin-top: 20px;

    color: #526c74;

    line-height: 1.8;
}


/* ---------------------------------------------------------
소제목
--------------------------------------------------------- */

h1, h2, h3 {

    color: #254f5d !important;
}


/* ---------------------------------------------------------
footer
--------------------------------------------------------- */

.footer {

    text-align: center;

    color: #7899a3;

    margin-top: 50px;

    font-size: 12px;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# 3. 상단 화면
# ============================================================

st.markdown(
    '<div class="hospital-label">HEALTH DATA DASHBOARD</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-title">🏥 일일 사망원인 통계</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    '날짜별 사망원인 순위와 사망 인원 데이터를 확인해 보세요.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="title-line"></div>',
    unsafe_allow_html=True
)


# ============================================================
# 4. 한국 시간 기준 어제 날짜 계산
# ============================================================

# Streamlit Cloud 서버는 한국에 있지 않을 수 있기 때문에
# Asia/Seoul 시간대를 직접 지정합니다.

korea_now = datetime.now(
    ZoneInfo("Asia/Seoul")
)

today_korea = korea_now.date()

# 오늘 자료는 아직 집계되지 않았다고 가정하여
# 마지막 선택 가능 날짜는 어제로 설정합니다.

yesterday = today_korea - timedelta(days=1)


# ============================================================
# 5. 날짜 선택
# ============================================================

selected_date = st.date_input(

    "📅 통계를 확인할 날짜를 선택해 주세요",

    value=yesterday,

    max_value=yesterday
)


display_date = selected_date.strftime(
    "%Y년 %m월 %d일"
)


# ============================================================
# 6. 학습용 예시 데이터 생성 함수
# ============================================================

# 주의:
# 아래 데이터는 실제 국가 사망 통계가 아니라
# Streamlit 수행평가 기능 구현을 위한 예시 데이터입니다.
#
# 실제 공공데이터 API를 사용하게 되면
# 이 함수 부분을 API 요청 코드로 교체하면 됩니다.


def load_data(date):

    # 예시로 사용할 사망원인
    causes = [
        "악성신생물(암)",
        "심장질환",
        "폐렴",
        "뇌혈관질환",
        "당뇨병",
        "알츠하이머병",
        "고혈압성 질환",
        "간질환",
        "신장질환",
        "만성 하기도 질환"
    ]


    # 날짜마다 약간 다른 값이 나오도록 만들기 위한 숫자
    date_number = int(
        date.strftime("%d")
    )


    data = []


    for i, cause in enumerate(causes):

        # 학습용 임의 사망자 수
        death_count = (
            220
            - i * 15
            + (date_number % 7)
            - (i % 3) * 2
        )


        # 학습용 평균 연령
        average_age = (
            68
            + i * 1.4
            + (date_number % 3) * 0.3
        )


        data.append(
            {
                "사망원인": cause,
                "사망자수": death_count,
                "평균연령": round(
                    average_age,
                    1
                )
            }
        )


    return pd.DataFrame(data)


# ============================================================
# 7. 선택한 날짜 데이터
# ============================================================

df = load_data(
    selected_date
)


# ============================================================
# 8. 데이터가 없는 경우
# ============================================================

if df.empty:

    st.warning(
        "🏥 그날은 아직 집계 전입니다."
    )

    st.info(
        """
        선택한 날짜의 사망원인 통계가 아직 제공되지 않았습니다.

        다른 날짜를 선택하여 다시 확인해 주세요.
        """
    )

    st.stop()


# ============================================================
# 9. 전날 데이터
# ============================================================

previous_date = (
    selected_date
    - timedelta(days=1)
)

previous_df = load_data(
    previous_date
)


# ============================================================
# 10. 현재 날짜 순위 계산
# ============================================================

df = (
    df.sort_values(
        "사망자수",
        ascending=False
    )
    .reset_index(drop=True)
)


df["순위"] = (
    df.index + 1
)


# ============================================================
# 11. 전날 순위 계산
# ============================================================

previous_df = (
    previous_df
    .sort_values(
        "사망자수",
        ascending=False
    )
    .reset_index(drop=True)
)


previous_df["전날순위"] = (
    previous_df.index + 1
)


# ============================================================
# 12. 전날 순위와 합치기
# ============================================================

df = df.merge(

    previous_df[
        [
            "사망원인",
            "전날순위"
        ]
    ],

    on="사망원인",

    how="left"
)


# ============================================================
# 13. 순위 증감 계산
# ============================================================

# 예:
#
# 어제 4위 → 오늘 2위
#
# 4 - 2 = +2
#
# 따라서 +2는 순위 상승입니다.


df["순위변동값"] = (
    df["전날순위"]
    - df["순위"]
)


def make_rank_change(value):

    if pd.isna(value):

        return "NEW"


    value = int(value)


    if value > 0:

        return f"▲ {value}"


    elif value < 0:

        return f"▼ {abs(value)}"


    else:

        return "－"


df["순위 변동"] = (
    df["순위변동값"]
    .apply(make_rank_change)
)


# ============================================================
# 14. 1위 사망원인에 병원 이모지 추가
# ============================================================

df["표시 사망원인"] = df["사망원인"]


df.loc[
    df["순위"] == 1,
    "표시 사망원인"
] = (
    "🏥 "
    + df.loc[
        df["순위"] == 1,
        "사망원인"
    ]
)


# ============================================================
# 15. 상단 지표 카드
# ============================================================

first = df.iloc[0]


st.markdown("---")

st.subheader(
    f"📊 {display_date} 사망원인 통계"
)


metric1, metric2, metric3 = st.columns(3)


with metric1:

    st.metric(
        label="🏥 사망원인 1위",
        value=first["사망원인"]
    )


with metric2:

    st.metric(
        label="👥 1위 사망 인원",
        value=f"{first['사망자수']:,}명"
    )


with metric3:

    st.metric(
        label="🎂 평균 연령",
        value=f"{first['평균연령']:.1f}세"
    )


# ============================================================
# 16. 1위와 2위 따로 비교
# ============================================================

st.markdown("---")

st.subheader(
    "🥇 사망원인 1위와 2위 비교"
)


if len(df) >= 2:

    first = df.iloc[0]

    second = df.iloc[1]


    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # 1위
    # --------------------------------------------------------

    with col1:

        st.markdown(
            f"""
<div class="cause-card">

<div class="rank-label">
RANK 01
</div>

<div class="cause-name">
🏥 {first["사망원인"]}
</div>

<div class="cause-info">

<b>사망 인원</b><br>
{first["사망자수"]:,}명

<br><br>

<b>평균 연령</b><br>
{first["평균연령"]:.1f}세

<br><br>

<b>전날 대비 순위</b><br>
{first["순위 변동"]}

</div>

</div>
""",
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # 2위
    # --------------------------------------------------------

    with col2:

        st.markdown(
            f"""
<div class="cause-card">

<div class="rank-label">
RANK 02
</div>

<div class="cause-name">
{second["사망원인"]}
</div>

<div class="cause-info">

<b>사망 인원</b><br>
{second["사망자수"]:,}명

<br><br>

<b>평균 연령</b><br>
{second["평균연령"]:.1f}세

<br><br>

<b>전날 대비 순위</b><br>
{second["순위 변동"]}

</div>

</div>
""",
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # 두 원인 비교
    # --------------------------------------------------------

    death_difference = (
        first["사망자수"]
        - second["사망자수"]
    )


    age_difference = abs(
        first["평균연령"]
        - second["평균연령"]
    )


    st.info(
        f"👥 **{first['사망원인']}**으로 인한 사망자는 "
        f"**{second['사망원인']}**보다 "
        f"**{death_difference:,}명 많습니다.**  \n"
        f"🎂 두 사망원인의 평균 연령 차이는 "
        f"**{age_difference:.1f}세**입니다."
    )


# ============================================================
# 17. 사망자 수 상위 5개 막대그래프
# ============================================================

st.markdown("---")

st.subheader(
    "📈 사망 인원 상위 5개 원인"
)


top5 = (
    df.nlargest(
        5,
        "사망자수"
    )[
        [
            "사망원인",
            "사망자수"
        ]
    ]
    .copy()
)


top5 = top5.set_index(
    "사망원인"
)


st.bar_chart(
    top5,
    y="사망자수"
)


# ============================================================
# 18. 전체 순위표
# ============================================================

st.markdown("---")

st.subheader(
    "📋 전체 사망원인 순위"
)


table_df = df[
    [
        "순위",
        "순위 변동",
        "표시 사망원인",
        "사망자수",
        "평균연령"
    ]
].copy()


table_df = table_df.rename(
    columns={
        "표시 사망원인": "사망원인",
        "사망자수": "사망 인원",
        "평균연령": "평균 연령"
    }
)


# ============================================================
# 19. 순위 변동 색상
# ============================================================

def color_rank_change(value):

    text = str(value)


    # 순위 상승 → 빨간색
    if "▲" in text:

        return (
            "color: #d62828;"
            "font-weight: bold;"
        )


    # 순위 하락 → 파란색
    elif "▼" in text:

        return (
            "color: #2878c8;"
            "font-weight: bold;"
        )


    else:

        return (
            "color: #777777;"
        )


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
# 20. 안내
# ============================================================

st.markdown(
    """
<div class="notice-box">

<b>📌 표 읽는 방법</b><br><br>

<span style="color:#d62828;"><b>▲ 빨간 위 화살표</b></span>
: 전날보다 순위가 상승한 사망원인<br>

<span style="color:#2878c8;"><b>▼ 파란 아래 화살표</b></span>
: 전날보다 순위가 하락한 사망원인<br>

🏥 : 선택한 날짜의 사망원인 1위

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# 21. 데이터 안내
# ============================================================

st.warning(
    "⚠️ 현재 이 버전의 사망자 수와 평균 연령은 "
    "웹앱 기능 구현을 위한 학습용 예시 데이터입니다. "
    "실제 통계로 해석하면 안 됩니다."
)


# ============================================================
# 22. Footer
# ============================================================

st.markdown(
    f"""
<div class="footer">

🏥 HEALTH DATA DASHBOARD<br><br>

선택 날짜 · {display_date}

</div>
""",
    unsafe_allow_html=True
)
