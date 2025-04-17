import streamlit as st
import openai
import os
import datetime

# ✅ OpenAI 키를 환경변수에서 가져오기
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai.api_key)

# ✅ 페이지 기본 설정
st.set_page_config(page_title="AI 여행 플래너", page_icon="🌍")
st.title("🌍 AI 여행 일정 추천기")
st.markdown("여행 조건을 입력하면, AI가 하루치 여행 일정을 짜줍니다!")

# ✅ 사용자 입력 받기
st.sidebar.header("📌 여행 조건 입력")
travel_city = st.sidebar.text_input("여행 도시는?", "서울")
travel_date = st.sidebar.date_input("여행 날짜는?", datetime.date.today())
companion = st.sidebar.selectbox("동행 유형은?", ["혼자", "커플", "가족", "친구"])
vibe = st.sidebar.multiselect("여행 분위기?", ["힐링", "핫플", "감성", "자연", "가성비"])
food = st.sidebar.multiselect("음식 취향은?", ["한식", "양식", "디저트", "채식", "분식"])
budget = st.sidebar.selectbox("예산은?", ["저렴", "중간", "고급"])

# ✅ 버튼 클릭 시 GPT 호출
if st.sidebar.button("✈️ 여행 일정 추천받기"):
    with st.spinner("AI가 여행 일정을 생성 중입니다..."):

        prompt = f"""
        당신은 여행 일정을 추천해주는 AI 플래너입니다.

        사용자의 요청 정보를 바탕으로 여행 코스를 하루치로 구성해주세요.
        각 코스는 아침 - 점심 - 오후 카페 - 저녁 - 야경 장소의 흐름으로 구성해주세요.

        🧾 사용자 입력
        - 여행 도시: {travel_city}
        - 여행 날짜: {travel_date.strftime('%Y-%m-%d')}
        - 동행 유형: {companion}
        - 여행 분위기: {', '.join(vibe)}
        - 음식 취향: {', '.join(food)}
        - 예산: {budget}

        일정은 이동 동선이 자연스럽게 연결되도록 구성해주세요.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 여행 일정을 짜주는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        result = response.choices[0].message.content

        def extract_place_names(text):
            lines = text.split('\n')
            places = []
            for line in lines:
                if '-' in line:
                    place = line.split('-')[-1].strip()
                    if place and len(place) > 2:
                        places.append(place)
            return places

        def generate_google_map_links(places):
            links = []
            for place in places:
                url = f"https://www.google.com/maps/search/{place.replace(' ', '+')}"
                links.append(f"📍 {place}: {url}")
            return links

        places = extract_place_names(result)
        map_links = generate_google_map_links(places)

        # ✅ 결과 출력
        st.subheader("🗓️ AI가 추천한 여행 일정")
        st.text(result)

        st.subheader("🗺️ Google Maps 링크")
        st.text("\n".join(map_links))

        # ✅ 텍스트 다운로드
        full_text = result + "\n\n🗺️ 지도 링크:\n" + "\n".join(map_links)
        st.download_button(
            label="📄 일정 .txt로 저장하기",
            data=full_text,
            file_name=f"{travel_city}_{travel_date}_여행일정.txt",
            mime="text/plain"
        )
