
import streamlit as st
import openai
import os
import datetime
import urllib.parse
import requests
import plotly.graph_objects as go
import json
from urllib.parse import urlencode

# 전역 설정
openai.api_key = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
FIREBASE_URL = os.getenv("FIREBASE_URL")

client = openai.OpenAI(api_key=openai.api_key)

@st.cache_data(show_spinner=False)
def generate_prompt(city, date, days, companion, vibe, food, budget, people):
    return f"""
    당신은 여행 일정을 추천해주는 AI 플래너입니다.
    여행 일정을 {days}일로 구성해주세요.
    아침, 점심, 카페, 저녁, 야경 형식으로 작성하고 각 장소는 한 줄 설명 포함해주세요.
    여행 도시: {city}, 동행: {companion}, 인원: {people}, 분위기: {', '.join(vibe)}, 음식: {', '.join(food)}, 예산: {budget}
    """

st.set_page_config(page_title="AI 여행 플래너", page_icon="🌍", layout="wide")
st.markdown("""
    <style>
    .big-title { font-size: 36px !important; font-weight: 700; }
    .subtitle { font-size: 20px; color: gray; margin-top: -20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='big-title'>🌍 여행지를 알려주세요</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI가 자동으로 여행 코스를 추천해드립니다</div>", unsafe_allow_html=True)

query_params = st.query_params
travel_city = query_params.get("city", ["서울"])[0]
travel_date = datetime.date.fromisoformat(query_params.get("date", [str(datetime.date.today())])[0])
trip_days = int(query_params.get("days", ["1"])[0])
companion = query_params.get("with", ["혼자"])[0]
vibe = query_params.get("vibe", [])
food = query_params.get("food", [])
budget = query_params.get("budget", ["100000"])[0]

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    travel_city = st.text_input("여행 도시는 어디인가요?", travel_city)
    if travel_city == "서울":
        st.caption("🔍 추천 여행지: 부산(해변), 강릉(자연), 전주(감성), 여수(야경)")

with col2:
    travel_date = st.date_input("여행 날짜는 언제인가요?", travel_date)

with col3:
    trip_days_label = st.selectbox("여행 일수는?", ["당일치기", "1박2일", "2박3일", "3박4일", "4박5일"], index=trip_days - 1)
    trip_days = int(trip_days_label[0]) if trip_days_label != "당일치기" else 1

st.markdown("---")

st.subheader("👥 동행 인원 구성")
cols = st.columns(4)
adult = cols[0].number_input("성인", min_value=0, max_value=10, value=1, step=1)
kids = cols[1].number_input("어린이", min_value=0, max_value=10, step=1)
babies = cols[2].number_input("유아", min_value=0, max_value=10, step=1)
pets = cols[3].checkbox("반려동물 포함")
people = f"성인 {adult}, 어린이 {kids}, 유아 {babies}, 반려동물 {'있음' if pets else '없음'}"

companion = st.selectbox("동행 유형은?", ["혼자", "커플", "가족", "친구"], index=["혼자", "커플", "가족", "친구"].index(companion))

with st.expander("🎨 여행 분위기 선택"):
    vibe = st.multiselect("여행 분위기?", ["힐링", "핫플", "감성", "자연", "가성비", "로맨틱", "모험", "역사", "맛집", "휴양", "문화", "레저"], default=vibe)

with st.expander("🍽️ 음식 취향 선택"):
    food = st.multiselect("음식 취향은?", ["한식", "양식", "디저트", "채식", "분식", "일식", "중식", "고기", "해산물", "패스트푸드", "아시아", "퓨전"], default=food)

with st.expander("💸 예산 설정"):
    budget = st.slider("예산은? (KRW)", 0, 10000000, int(budget), step=1000)

if st.button("✈️ AI에게 추천받기"):
    try:
        with st.spinner("AI가 여행 일정을 생성 중입니다..."):
            prompt = generate_prompt(travel_city, travel_date, trip_days, companion, vibe, food, budget, people)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 여행 코디네이터입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1200
            )
            schedule_text = response.choices[0].message.content

        st.markdown("---")
        st.subheader("📋 AI 추천 여행 일정")
        st.markdown(schedule_text)

    except Exception as e:
        st.error(f"⚠️ 오류 발생: {str(e)}")
