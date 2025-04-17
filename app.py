
import streamlit as st
import datetime

st.set_page_config(page_title="AI 여행 추천", page_icon="🧭", layout="wide")

# 섹션 1: 에어비앤비 스타일 여행지 입력 + 추천
st.markdown("### 🌍 여행 도시는 어디인가요?")
travel_city = st.text_input("예: 서울, 부산, 제주", key="city_input")
if travel_city.strip() == "":
    st.caption("📍 추천 도시: 부산, 강릉, 전주, 여수")

# 섹션 2: 여행일정 입력
col1, col2 = st.columns(2)
with col1:
    travel_date = st.date_input("여행 날짜", datetime.date.today())
with col2:
    trip_days_label = st.selectbox("여행 기간", ["당일치기", "1박2일", "2박3일", "3박4일"])
    trip_days = int(trip_days_label[0]) if trip_days_label != "당일치기" else 1

# 섹션 3: 여행 인원
st.markdown("### 👥 동행 인원")
a, b, c, d = st.columns(4)
adult = a.number_input("성인", 0, 10, 1)
child = b.number_input("어린이", 0, 10)
baby = c.number_input("유아", 0, 10)
pet = d.checkbox("반려동물 포함")
people = f"성인 {adult}, 어린이 {child}, 유아 {baby}, 반려동물 {'있음' if pet else '없음'}"

# 섹션 4: 음식점 3개 하트 선택 → 음식 취향 가중치 반영
st.markdown("### 🍽️ 당신의 취향을 골라주세요")
rest = [("연안 해물탕", "해산물"), ("부산 떡볶이", "분식"), ("공화춘 짜장면", "중식")]
food_weights = {}
for name, cat in rest:
    col1, col2 = st.columns([7, 1])
    col1.markdown(f"**{name}** - {cat}")
    if col2.toggle("♥", key=name):
        food_weights[cat] = food_weights.get(cat, 0) + 1

# 섹션 5: 예산, 분위기
with st.expander("🎨 여행 분위기 / 음식 / 예산 설정"):
    vibe = st.multiselect("여행 분위기", ["힐링", "핫플", "감성", "자연", "로맨틱"])
    food = st.multiselect("음식 취향", ["한식", "중식", "일식", "양식", "분식", "해산물", "디저트"])
    budget = st.slider("예산 (KRW)", 0, 10_000_000, 300_000, step=1000)

# 섹션 6: 추천 버튼
if st.button("✈️ AI에게 추천받기"):
    st.success("AI가 취향 기반 맞춤 일정을 생성 중입니다...")
    st.markdown("##### 예시 📍")
    st.markdown("1일차")
- 아침: 감천문화마을 산책
- 점심: 부산국밥 거리
- 카페: 해운대 루프탑
- 저녁: 광안리 포장마차
- 야경: 광안대교")

# 섹션 7: TODO 지도 기반 코스 + 카드 타임라인
