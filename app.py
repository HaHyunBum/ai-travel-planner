import streamlit as st
import openai
import os
import datetime
import urllib.parse
import requests
import plotly.graph_objects as go
import json
import qrcode
from io import BytesIO
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

def make_qr_code(link):
    qr = qrcode.make(link)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf

st.set_page_config(page_title="AI 여행 플래너", page_icon="🌍")
st.title("🌍 AI 여행 일정 추천기")

query_params = st.query_params
travel_city = query_params.get("city", ["서울"])[0]
travel_date = datetime.date.fromisoformat(query_params.get("date", [str(datetime.date.today())])[0])
trip_days = int(query_params.get("days", ["1"])[0])
companion = query_params.get("with", ["혼자"])[0]
vibe = query_params.get("vibe", [])
food = query_params.get("food", [])
budget = query_params.get("budget", ["100000"])[0]

st.sidebar.header("📌 여행 조건 입력")
travel_city = st.sidebar.text_input("여행 도시는?", travel_city, help="원하는 도시를 검색하세요.")
travel_date = st.sidebar.date_input("여행 날짜는?", travel_date)
trip_days_label = st.sidebar.selectbox("여행 일수는?", ["당일치기", "1박2일", "2박3일", "3박4일", "4박5일"], index=trip_days - 1)
trip_days = int(trip_days_label[0]) if trip_days_label != "당일치기" else 1

st.sidebar.markdown("### 동행 인원 수")
adult = st.sidebar.number_input("성인", min_value=0, max_value=10, value=1, step=1)
kids = st.sidebar.number_input("어린이", min_value=0, max_value=10, step=1)
babies = st.sidebar.number_input("유아", min_value=0, max_value=10, step=1)
pets = st.sidebar.checkbox("반려동물 동반")
people = f"성인 {adult}, 어린이 {kids}, 유아 {babies}, 반려동물 {'있음' if pets else '없음'}"

companion = st.sidebar.selectbox("동행 유형은?", ["혼자", "커플", "가족", "친구"], index=["혼자", "커플", "가족", "친구"].index(companion))
vibe = st.sidebar.multiselect("여행 분위기?", ["힐링", "핫플", "감성", "자연", "가성비", "로맨틱", "모험", "역사", "맛집", "휴양", "문화", "레저"], default=vibe)
food = st.sidebar.multiselect("음식 취향은?", ["한식", "양식", "디저트", "채식", "분식", "일식", "중식", "고기", "해산물", "패스트푸드", "아시아", "퓨전"], default=food)
budget = st.sidebar.slider("예산은? (KRW)", 0, 100000000, int(budget), step=10000)

if st.sidebar.button("✈️ 여행 일정 추천받기"):
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

        st.subheader("🗓️ 추천 일정")
        with st.expander("자세히 보기"):
            st.markdown(schedule_text)

        st.markdown("---")
        st.subheader("📎 공유 링크 및 QR 코드")
        params = urlencode({"city": travel_city, "date": travel_date, "days": trip_days, "with": companion})
        share_str = f"https://{st.request.url.split('?')[0]}?{params}"
        qr_buf = make_qr_code(share_str)
        st.image(qr_buf.getvalue(), caption="QR 코드로 공유하기")
        st.markdown(f"🔗 [공유 링크 바로가기]({share_str})")

        st.markdown("---")
        st.subheader("👍 일정이 마음에 드시나요?")
        if st.button("❤️ 좋아요! 저장하기") and FIREBASE_URL:
            requests.post(FIREBASE_URL, json={"city": travel_city, "date": str(travel_date), "schedule": schedule_text})
            st.success("✅ Firebase에 저장 완료")

    except Exception as e:
        st.error(f"⚠️ 오류 발생: {str(e)}")
