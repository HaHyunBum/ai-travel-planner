
import streamlit as st
import openai
import os
import datetime

st.set_page_config(page_title="AI 여행 플래너", page_icon="🌍", layout="wide")

st.markdown("<h1>🌍 여행지를 알려주세요</h1>", unsafe_allow_html=True)
st.markdown("AI가 자동으로 여행 코스를 추천해드립니다")

# 사용자 입력 섹션
travel_city = st.text_input("여행 도시는 어디인가요?", placeholder="예: 서울, 부산, 제주도 등")
travel_date = st.date_input("여행 날짜는 언제인가요?", datetime.date.today())
trip_days_label = st.selectbox("여행 일수는?", ["당일치기", "1박2일", "2박3일", "3박4일", "4박5일"])
trip_days = int(trip_days_label[0]) if trip_days_label != "당일치기" else 1

# 인원 구성
cols = st.columns(4)
adult = cols[0].number_input("성인", 0, 10, 1)
kids = cols[1].number_input("어린이", 0, 10)
babies = cols[2].number_input("유아", 0, 10)
pets = cols[3].checkbox("반려동물 포함")

# 세부 필터
with st.expander("🎨 여행 분위기 선택"):
    vibe = st.multiselect("여행 분위기", ["힐링", "핫플", "감성", "자연", "맛집", "로맨틱", "레저"])

with st.expander("🍽 음식 취향 선택"):
    food = st.multiselect("음식 취향", ["한식", "양식", "일식", "중식", "해산물", "디저트"])

with st.expander("💸 예산 설정"):
    budget = st.slider("예산 (KRW)", 0, 10000000, 500000, step=1000)

# 추천 요청
if st.button("✈️ AI에게 추천받기"):
    st.success("추천 일정을 생성했습니다! (샘플입니다)")
    st.markdown("✅ 아침: 서울숲 근처 브런치 카페  
✅ 점심: 성수 맛집 순대국  
✅ 카페: 성수 루프탑 카페  
✅ 저녁: 압구정 감성 레스토랑")

# 하트 기반 음식점 취향 체크
st.markdown("---")
st.subheader("❤️ 선호 음식점 선택 (가중치 반영 테스트)")
for name, category in [("을지로 우육면", "중식"), ("성수 카페 어니언", "디저트"), ("망원 떡볶이 성지", "분식")]:
    col1, col2 = st.columns([6, 1])
    col1.markdown(f"**{name}** ({category})")
    col2.toggle("하트", key=f"like_{name}")
