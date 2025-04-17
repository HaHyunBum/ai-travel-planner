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
from fpdf import FPDF

# 전역 설정
openai.api_key = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
FIREBASE_URL = os.getenv("FIREBASE_URL")

client = openai.OpenAI(api_key=openai.api_key)

# 유틸 함수들
@st.cache_data(show_spinner=False)
def generate_prompt(city, date, days, companion, vibe, food, budget):
    return f"""
    당신은 여행 일정을 추천해주는 AI 플래너입니다.
    여행 일정을 {days}일로 구성해주세요.
    아침, 점심, 카페, 저녁, 야경 형식으로 작성하고 각 장소는 한 줄 설명 포함해주세요.
    여행 도시: {city}, 동행: {companion}, 분위기: {', '.join(vibe)}, 음식: {', '.join(food)}, 예산: {budget}
    """

@st.cache_data(show_spinner=False)
def fetch_distance_matrix(places):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={'|'.join(places)}&destinations={'|'.join(places)}&key={GOOGLE_API_KEY}"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    return None

def make_qr_code(link):
    qr = qrcode.make(link)
    buf = BytesIO()
    qr.save(buf)
    return buf

def generate_pdf(sections, user_inputs):
    pdf = FPDF()
    pdf.add_page()
    try:
        pdf.add_font('NanumGothic', '', 'NanumGothic.ttf', uni=True)
        pdf.set_font("NanumGothic", size=12)
    except:
        pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="AI 여행 일정 추천기", ln=True, align="C")
    for sec in sections:
        pdf.cell(200, 10, txt=f"{sec}: {user_inputs[sec]}", ln=True)
    output = BytesIO()
    pdf.output(output, 'F')
    output.seek(0)
    return output

# UI 시작
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
    try:
        with st.spinner("AI가 여행 일정을 생성 중입니다..."):
            prompt = generate_prompt(travel_city, travel_date, trip_days, companion, vibe, food, budget)
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
            st.subheader("🗓️ AI가 추천한 여행 일정")
            st.markdown(schedule_text)

            sections = ["아침", "점심", "카페", "저녁", "야경"]
            st.markdown("---")
            st.subheader("✏️ 일정 수정하기")
            user_inputs = {sec: st.text_input(f"{sec} 장소 입력", value=f"{travel_city} 대표 {sec} 장소") for sec in sections}

            st.markdown("---")
            st.subheader("🖼️ 장소별 이미지 불러오기")
            for sec in sections:
                query = f"{user_inputs[sec]} {travel_city}"
                st.image(f"https://source.unsplash.com/featured/?{urllib.parse.quote(query)}", caption=f"{sec}: {user_inputs[sec]}", use_column_width=True)

            st.markdown("---")
            st.subheader("🗺️ Google Static Maps로 위치 시각화")
            for sec in sections:
                map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={urllib.parse.quote(user_inputs[sec])}&zoom=15&size=600x300&markers=color:red%7C{urllib.parse.quote(user_inputs[sec])}&key={GOOGLE_API_KEY}"
                st.image(map_url, caption=f"{sec} 위치", use_column_width=True)

            st.markdown("---")
            st.subheader("🧭 거리 기반 동선 최적화")
            matrix_data = fetch_distance_matrix(list(user_inputs.values()))
            if matrix_data:
                st.success("(시뮬레이션용 결과) 거리 기반 재정렬:")
                rows = matrix_data['rows']
                distances = [rows[0]['elements'][i]['distance']['value'] if 'distance' in rows[0]['elements'][i] else float('inf') for i in range(len(rows[0]['elements']))]
                reordered = [place for _, place in sorted(zip(distances, user_inputs.values()), key=lambda x: x[0])]
                for i, p in enumerate(reordered, 1):
                    st.write(f"{i}. {p}")

            st.markdown("---")
            st.subheader("🗓️ 일정 시간대 시각화")
            fig = go.Figure()
            for i, sec in enumerate(sections):
                fig.add_trace(go.Bar(x=[user_inputs[sec]], y=[1], name=sec, orientation='h', hovertext=[f"{['08:00','12:00','15:00','18:00','20:00'][i]}"]))
            fig.update_layout(barmode='stack', height=300, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.subheader("👍 일정이 마음에 드시나요?")
            if st.button("❤️ 좋아요! 일정 마음에 들어요") and FIREBASE_URL:
                requests.post(FIREBASE_URL, json={"city": travel_city, "date": str(travel_date), "schedule": user_inputs})
                st.success("Firebase에 일정이 저장되었습니다!")

            st.markdown("---")
            st.subheader("📥 일정 .txt 파일로 다운로드")
            st.download_button("📄 일정 텍스트 다운로드", "\n".join([f"{k}: {v}" for k, v in user_inputs.items()]), file_name=f"{travel_city}_{travel_date}_일정.txt")

            st.markdown("---")
            st.subheader("📎 공유 링크 및 QR 코드")
            share_str = f"https://{st.request.url.split('?')[0]}?city={travel_city}&date={travel_date}&days={trip_days}&with={companion}"
            qr_buf = make_qr_code(share_str)
            st.image(qr_buf.getvalue(), caption="QR 코드로 공유하기")
            st.markdown(f"🔗 [공유 링크 바로가기]({share_str})")

            st.markdown("---")
            st.subheader("🖨️ PDF로 일정 저장하기")
            pdf_bytes = generate_pdf(sections, user_inputs)
            st.download_button("📄 PDF 다운로드", data=pdf_bytes, file_name="itinerary.pdf")

            st.success("✅ 모든 기능이 반영되었습니다!")

    except Exception as e:
        st.error(f"⚠️ 오류가 발생했습니다: {str(e)}")
