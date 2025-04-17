import streamlit as st
import openai
import os
import datetime
import urllib.parse

# ✅ OpenAI 키를 환경변수에서 가져오기
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai.api_key)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ✅ 페이지 기본 설정
st.set_page_config(page_title="AI 여행 플래너", page_icon="🌍")
st.title("🌍 AI 여행 일정 추천기")

# ✅ 공유 링크 파라미터 로딩
query_params = st.experimental_get_query_params()
travel_city = query_params.get("city", ["서울"])[0]
travel_date = datetime.date.fromisoformat(query_params.get("date", [str(datetime.date.today())])[0])
trip_days = int(query_params.get("days", ["1"])[0])
companion = query_params.get("with", ["혼자"])[0]
vibe = query_params.get("vibe", [])
food = query_params.get("food", [])
budget = query_params.get("budget", ["저렴"])[0]

# ✅ 사용자 입력 받기
st.sidebar.header("📌 여행 조건 입력")
travel_city = st.sidebar.text_input("여행 도시는?", travel_city)
travel_date = st.sidebar.date_input("여행 날짜는?", travel_date)
trip_days = st.sidebar.slider("여행 일수는?", 1, 5, trip_days)
companion = st.sidebar.selectbox("동행 유형은?", ["혼자", "커플", "가족", "친구"], index=["혼자", "커플", "가족", "친구"].index(companion))
vibe = st.sidebar.multiselect("여행 분위기?", ["힐링", "핫플", "감성", "자연", "가성비"], default=vibe)
food = st.sidebar.multiselect("음식 취향은?", ["한식", "양식", "디저트", "채식", "분식"], default=food)
budget = st.sidebar.selectbox("예산은?", ["저렴", "중간", "고급"], index=["저렴", "중간", "고급"].index(budget))

# ✅ 다시 생성 버튼 구현
if "generate_count" not in st.session_state:
    st.session_state.generate_count = 0

if st.sidebar.button("✈️ 여행 일정 추천받기") or st.session_state.generate_count > 0:
    st.session_state.generate_count += 1
    with st.spinner("AI가 여행 일정을 생성 중입니다..."):

        prompt = f"""
        당신은 여행 일정을 추천해주는 AI 플래너입니다.

        사용자의 요청 정보를 바탕으로 여행 코스를 {trip_days}일로 구성해주세요.
        하루당 아침 - 점심 - 오후 카페 - 저녁 - 야경 장소의 흐름으로 구성해주세요.

        각 장소는 다음 형식으로 구성해주세요:
        장소명 - 한 줄 설명 (이유나 명소 특징) - 사용자 후기 요약

        🧾 사용자 입력
        - 여행 도시: {travel_city}
        - 여행 날짜: {travel_date.strftime('%Y-%m-%d')}부터 {trip_days}일간
        - 동행 유형: {companion}
        - 여행 분위기: {', '.join(vibe)}
        - 음식 취향: {', '.join(food)}
        - 예산: {budget}

        일정은 이동 동선이 자연스럽게 연결되도록 구성해주세요.
        출력 형식은 각 날짜별로 구분되도록 해주세요 (예: Day 1, Day 2...) 
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 여행 일정을 짜주는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1800
        )

        result = response.choices[0].message.content

        def extract_place_names(text):
            lines = text.split('\n')
            places = []
            for line in lines:
                if '-' in line:
                    place = line.split('-')[0].strip()
                    if place and len(place) > 2:
                        places.append(place)
            return places

        def generate_google_map_links(places):
            links = []
            for place in places:
                url = f"https://www.google.com/maps/search/{place.replace(' ', '+')}"
                links.append(f"📍 {place}: {url}")
            return links

        def generate_image_urls(places):
            image_urls = []
            for place in places:
                query = place + " 관광지"
                fallback = f"https://source.unsplash.com/600x400/?{query.replace(' ', '+')}"
                image_urls.append((place, fallback))
            return image_urls

        places = extract_place_names(result)
        map_links = generate_google_map_links(places)
        image_urls = generate_image_urls(places)

        st.subheader("🗓️ AI가 추천한 여행 일정")

        import re
        day_blocks = re.split(r"(?=Day [0-9]+)", result)
        for block in day_blocks:
            if block.strip():
                with st.expander(block.split('\n')[0].strip(), expanded=True):
                    st.code(block.strip())

        with st.container():
            st.markdown("### 🙌 일정이 마음에 드시나요?")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("👍 좋아요! 일정 마음에 들어요"):
                    count = st.session_state.get("likes", 0) + 1
                    st.session_state.likes = count
                    st.success(f"지금까지 {count}명이 좋아요를 눌렀어요! 😊")
            with col2:
                if st.button("🔄 다른 추천 일정 보기"):
                    st.rerun()

        st.subheader("🖼️ 장소별 이미지 + 요약")
        for place, img in image_urls:
            st.markdown(f"**{place}**")
            st.image(img)
            st.markdown(f"[📍 {place} 지도에서 보기](https://www.google.com/maps/search/{place.replace(' ', '+')})")

        st.subheader("🗺️ 전체 Google Maps 링크")
        st.text("\n".join(map_links))

        # ✅ 공유 링크 만들기
        base_url = st.request.url.split('?')[0] if hasattr(st, 'request') else ''
        query_string = urllib.parse.urlencode({
            "city": travel_city,
            "date": travel_date,
            "days": trip_days,
            "with": companion,
            "vibe": vibe,
            "food": food,
            "budget": budget
        }, doseq=True)
        share_url = f"{base_url}?{query_string}"
        st.markdown("### 🔗 친구에게 공유하기")
        st.code(share_url, language="text")

        # ✅ 텍스트 다운로드
        full_text = result + "\n\n🗺️ 지도 링크:\n" + "\n".join(map_links)
        st.download_button(
            label="📄 일정 .txt로 저장하기",
            data=full_text,
            file_name=f"{travel_city}_{travel_date}_여행일정.txt",
            mime="text/plain"
        )
