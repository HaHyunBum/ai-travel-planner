import streamlit as st
import openai
import os
import datetime

# 환경 변수로부터 API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai.api_key)

# 기본 페이지 설정
st.set_page_config(page_title="AI 여행 플래너", page_icon="🌍", layout="wide")
st.markdown("<h1>🌍 여행지를 알려주세요</h1>", unsafe_allow_html=True)
st.markdown("AI가 자동으로 여행 코스를 추천해드립니다")

# 여행 조건 입력
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    travel_city = st.text_input("여행 도시는 어디인가요?", "서울")
    if travel_city == "서울":
        st.caption("🔍 추천 여행지: 부산(해변), 강릉(자연), 전주(감성), 여수(야경)")
with col2:
    travel_date = st.date_input("여행 날짜는 언제인가요?", datetime.date.today())
with col3:
    trip_days_label = st.selectbox("여행 일수는?", ["당일치기", "1박2일", "2박3일", "3박4일", "4박5일"])
    trip_days = int(trip_days_label[0]) if trip_days_label != "당일치기" else 1

# 동행 인원 구성
st.markdown("## 👥 동행 인원 구성")
cols = st.columns(4)
adult = cols[0].number_input("성인", min_value=0, max_value=10, value=1, step=1)
kids = cols[1].number_input("어린이", min_value=0, max_value=10, step=1)
babies = cols[2].number_input("유아", min_value=0, max_value=10, step=1)
pets = cols[3].checkbox("반려동물 포함")
people = f"성인 {adult}, 어린이 {kids}, 유아 {babies}, 반려동물 {'있음' if pets else '없음'}"

# 동행 유형
companion = st.selectbox("동행 유형은?", ["혼자", "커플", "가족", "친구"])

# 분위기, 음식, 예산 선택
with st.expander("🍜 여행 분위기 / 음식 / 예산 설정"):
    vibe = st.multiselect("여행 분위기?", ["힐링", "핫플", "감성", "자연", "가성비", "로맨틱", "모험", "역사", "맛집", "휴양", "문화", "레저"], default=[])
    food = st.multiselect("음식 취향은?", ["한식", "양식", "디저트", "채식", "분식", "일식", "중식", "고기", "해산물", "패스트푸드", "아시아", "퓨전"], default=[])
    budget = st.slider("예산은? (KRW)", 0, 10000000, 100000, step=1000)

# AI 프롬프트 생성
def generate_prompt(city, date, days, companion, vibe, food, budget, people): return f""" 당신은 '{city}'를 여행하는 사람들을 위한 여행 전문가이자 블로거입니다.
    여행 관련 정보를 수집하기 위해 네이버 블로그, 유튜브, 인스타그램 등에서 '{city} {days}일 여행 코스', '{city} 여행 맛집', '{city} 명소'를 검색한 것처럼 행동해주세요.

수집된 정보들을 바탕으로 현실적인 여행 일정을 작성해 주세요. 각 일차별로 오전/오후/저녁 시간대별로 구분하고, 방문할 장소와 설명을 포함해주세요.

결과는 아래 형식을 꼭 지켜주세요:

📅 1일차
**오전**
- 장소명: 설명

**오후**
- 장소명: 설명

**저녁**
- 장소명: 설명

📅 2일차 (이하 반복)

조건 요약:
- 도시: {city}
- 날짜: {date}
- 여행 기간: {days}일
- 동행: {companion}, 인원: {people}
- 분위기 키워드: {', '.join(vibe)}
- 음식 취향: {', '.join(food)}
- 예산: {budget}원
"""


# 버튼 클릭 시 실행
if st.button("✈️ AI에게 추천받기"):
    with st.spinner("AI가 취향 기반 맞춤 일정을 생성 중입니다..."):
        try:
            prompt = generate_prompt(travel_city, travel_date, trip_days, companion, vibe, food, budget, people)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 여행 코디네이터입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            result = response.choices[0].message.content
            st.success("✅ AI 추천 일정 생성 완료!")
            st.markdown("### 예시 📍")
            st.markdown(result)
        except Exception as e:
            st.error(f"⚠️ 오류 발생: {str(e)}")
