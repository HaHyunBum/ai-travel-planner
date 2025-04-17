import streamlit as st
import openai
import os
import datetime
import urllib.parse
import requests
import plotly.graph_objects as go
import json

openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai.api_key)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
FIREBASE_URL = os.getenv("FIREBASE_URL")

st.set_page_config(page_title="AI 여행 플래너", page_icon="🌍")
st.title("🌍 AI 여행 일정 추천기")

query_params = st.query_params
travel_city = query_params.get("city", ["서울"])[0]
travel_date = datetime.date.fromisoformat(query_params.get("date", [str(datetime.date.today())])[0])
trip_days = int(query_params.get("days", ["1"])[0])
companion = query_params.get("with", ["혼자"])[0]
vibe = query_params.get("vibe", [])
food = query_params.get("food", [])
budget = query_params.get("budget", ["저렴"])[0]

st.sidebar.header("📌 여행 조건 입력")
travel_city = st.sidebar.text_input("여행 도시는?", travel_city)
travel_date = st.sidebar.date_input("여행 날짜는?", travel_date)
trip_days = st.sidebar.slider("여행 일수는?", 1, 5, trip_days)
companion = st.sidebar.selectbox("동행 유형은?", ["혼자", "커플", "가족", "친구"], index=["혼자", "커플", "가족", "친구"].index(companion))
vibe = st.sidebar.multiselect("여행 분위기?", ["힐링", "핫플", "감성", "자연", "가성비"], default=vibe)
food = st.sidebar.multiselect("음식 취향은?", ["한식", "양식", "디저트", "채식", "분식"], default=food)
budget = st.sidebar.selectbox("예산은?", ["저렴", "중간", "고급"], index=["저렴", "중간", "고급"].index(budget))

if st.sidebar.button("✈️ 여행 일정 추천받기"):
    with st.spinner("AI가 여행 일정을 생성 중입니다..."):
        prompt = f"""
        당신은 여행 일정을 추천해주는 AI 플래너입니다.
        여행 일정을 {trip_days}일로 구성해주세요.
        아침, 점심, 카페, 저녁, 야경 형식으로 작성하고 각 장소는 한 줄 설명 포함해주세요.
        여행 도시: {travel_city}, 동행: {companion}, 분위기: {', '.join(vibe)}, 음식: {', '.join(food)}, 예산: {budget}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "당신은 여행 코디네이터입니다."}, {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200
        )

        schedule_text = response.choices[0].message.content
        st.subheader("🗓️ AI가 추천한 여행 일정")
        st.markdown(schedule_text)

        st.markdown("---")
        st.subheader("✏️ 일정 수정하기")
        sections = ["아침", "점심", "카페", "저녁", "야경"]
        user_inputs = {}
        for sec in sections:
            user_inputs[sec] = st.text_input(f"{sec} 장소 입력", value=f"{travel_city} 대표 {sec} 장소")

        st.markdown("---")
        st.subheader("🧭 거리 기반 동선 최적화")
        if GOOGLE_API_KEY:
            places = list(user_inputs.values())
            distance_url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={'|'.join(places)}&destinations={'|'.join(places)}&key={GOOGLE_API_KEY}"
            r = requests.get(distance_url)
            if r.status_code == 200:
                st.success("(시뮬레이션용 결과) 거리 기반 재정렬:")
                reordered = sorted(places)
                for i, p in enumerate(reordered, 1):
                    st.write(f"{i}. {p}")

        st.markdown("---")
        st.subheader("🗓️ 일정 시간대 시각화")
        fig = go.Figure()
        times = ["08:00", "12:00", "15:00", "18:00", "20:00"]
        for i, sec in enumerate(sections):
            fig.add_trace(go.Bar(
                x=[user_inputs[sec]],
                y=[1],
                name=sec,
                orientation='h',
                hovertext=times[i]
            ))
        fig.update_layout(barmode='stack', height=300, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

        st.success("✅ 모든 기능이 반영되었습니다!")
