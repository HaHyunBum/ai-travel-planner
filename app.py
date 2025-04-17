import streamlit as st
import openai
import os
import datetime

# API 키
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai.api_key)

# 페이지 설정
st.set_page_config(page_title="AI 여행 플래너", page_icon="🌍", layout="wide")

st.markdown("""
    <style>
    .big-title { font-size: 36px !important; font-weight: 700; margin-bottom: 0; }
    .subtitle { font-size: 18px; color: gray; margin-top: -10px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='big-title'>🌍 여행지를 알려주세요</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI가 자동으로 여행 코스를 추천해드립니다</div>", unsafe_allow_html=True)

# 여행지 검색 입력창
travel_city = st.text_input("여행 도시는 어디인가요?", placeholder="도시를 입력하세요 (예: 서울)")

# 추천 여행지 예시 출력
if travel_city == "":
    st.markdown("##### 🔥 인기 여행지 추천")
    st.markdown("- 📍 부산 - 광안리 해변과 맛집이 많은 도시\n- 📍 강릉 - 감성 바다 드라이브와 카페\n- 📍 전주 - 한옥마을과 전통음식\n- 📍 여수 - 낭만적인 야경 여행지")

# 날짜 입력
col1, col2 = st.columns([1, 1])
with col1:
    travel_date = st.date_input("여행 날짜는 언제인가요?", datetime.date.today())

with col2:
    trip_days_label = st.selectbox("여행 일수는?", ["당일치기", "1박2일", "2박3일", "3박4일", "4박5일"])
    trip_days = int(trip_days_label[0]) if trip_days_label != "당일치기" else 1

st.divider()

# 동행 인원
st.subheader("👥 동행 인원 구성")
a, b, c, d = st.columns(4)
adult = a.number_input("성인", min_value=0, max_value=10, value=1)
child = b.number_input("어린이", min_value=0, max_value=10, value=0)
baby = c.number_input("유아", min_value=0, max_value=10, value=0)
pet = d.checkbox("반려동물 포함")
people = f"성인 {adult}, 어린이 {child}, 유아 {baby}, 반려동물 {'있음' if pet else '없음'}"

# 동행 유형
companion = st.selectbox("동행 유형은?", ["혼자", "커플", "가족", "친구"])

# 분위기, 음식, 예산 - 확장 메뉴
with st.expander("🎨 여행 분위기 선택"):
    vibe = st.multiselect("분위기 선택", ["힐링", "핫플", "감성", "자연", "가성비", "로맨틱", "모험", "역사", "맛집", "휴양", "문화", "레저"])

with st.expander("🍽 음식 취향 선택"):
    food = st.multiselect("음식 선택", ["한식", "양식", "디저트", "채식", "분식", "일식", "중식", "고기", "해산물", "패스트푸드", "아시아", "퓨전"])

with st.expander("💰 예산 설정"):
    budget = st.slider("여행 예산 (KRW)", 0, 10000000, 100000, step=1000)

# 프롬프트 생성
def generate_prompt(city, date, days, companion, vibe, food, budget, people):
    return f"""
    당신은 여행 코디네이터입니다. 아래 조건에 따라 일정을 짜주세요.

    도시: {city}
    날짜: {date}
    일수: {days}일
    동행: {companion} ({people})
    분위기: {', '.join(vibe)}
    음식 취향: {', '.join(food)}
    예산: {budget}원

    하루당 아침/점심/카페/저녁/야경으로 5개 장소를 추천하고, 장소별 설명도 포함해주세요.
    """

# 버튼 클릭 시
if st.button("✈️ AI에게 추천받기"):
    if travel_city == "":
        st.warning("도시를 입력해주세요.")
    else:
        with st.spinner("AI가 일정을 추천 중입니다..."):
            prompt = generate_prompt(travel_city, travel_date, trip_days, companion, vibe, food, budget, people)
            try:
                res = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 여행 코디네이터입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1200
                )
                st.subheader("📋 AI 추천 일정")
                st.markdown(res.choices[0].message.content)
            except Exception as e:
                st.error(f"⚠️ 오류 발생: {e}")
