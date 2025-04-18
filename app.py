import streamlit as st
import openai
import os
import datetime
import urllib.parse
import requests

# API 키 설정 (환경변수 또는 secrets.toml 이용)
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]
kakao_api_key = os.getenv("KAKAO_API_KEY") or st.secrets["KAKAO_API_KEY"]

# 기본 페이지 설정
st.set_page_config(page_title="AI 여행 플래너", page_icon="🌍", layout="wide")
st.markdown("<h1>🌍 여행지를 알려주세요</h1>", unsafe_allow_html=True)
st.markdown("AI가 자동으로 여행 코스를 추천해드립니다")

# 여행 조건 입력
st.header("여행 정보를 입력하세요")
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    cities = ["서울", "인천", "부산", "대구", "광주", "대전", "울산"]
    travel_city = st.selectbox("여행 도시는 어디인가요?", cities, index=0)
    travel_city_custom = st.text_input("또는 직접 도시 입력", value="")
    if travel_city_custom:
        travel_city = travel_city_custom
    if travel_city == "서울":
        st.caption("🔍 추천 여행지: 부산(해변), 강릉(자연), 전주(감성), 여수(야경)")
with col2:
    travel_date = st.date_input("여행 날짜는 언제인가요?", datetime.date.today())
with col3:
    trip_days_label = st.selectbox("여행 일수는?", ["당일치기", "1박2일", "2박3일", "3박4일", "4박5일"])
    trip_days = int(trip_days_label[0]) if trip_days_label != "당일치기" else 1

# 행정동 선택 (카카오 API 이용)
def get_districts(city):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {kakao_api_key}"}
    params = {"query": f"{city} 맛집", "size": 30}
    res = requests.get(url, headers=headers, params=params)
    districts = set()
    if res.status_code == 200:
        for doc in res.json().get("documents", []):
            addr = doc.get("road_address") or doc.get("address")
            if addr:
                region = addr.get("region_3depth_name")
                if region:
                    districts.add(region)
    return sorted(list(districts))

if travel_city:
    st.markdown("### 📍 여행 지역 세부 선택")
    manual_districts = {
    "서울": ["홍익동", "망원동", "성수동", "잠실동", "이태원동", "연남동", "합정동", "한남동"],
    "인천": ["송도동", "을왕동", "연안동", "중구", "영종동", "동춘동", "주안동"],
    "부산": ["해운대구", "서면", "광안리", "남포동", "송정동"],
    "대구": ["동성로", "반월당", "수성구", "앞산동", "동대구"],
    "광주": ["상무지구", "충장로", "첨단지구", "양림동", "금남로"],
    "대전": ["둔산동", "은행동", "유성구", "도룡동"],
    "울산": ["삼산동", "성남동", "무거동", "남구"]
}
    district_list = manual_districts.get(travel_city, get_districts(travel_city))
    selected_district = st.selectbox("세부 지역(동/면/읍)을 선택하세요", district_list) if district_list else ""
else:
    selected_district = ""

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

# AI 프롬프트 생성 함수
def generate_prompt(city, district, date, days, companion, vibe, food, budget, people):
    return f"""
당신은 {city} {district}에 대해 인스타그램, 네이버 블로그, 유튜브를 참고해 여행 코스를 제안해주는 여행 코디네이터입니다.

{days}일 간의 여행 일정으로 오전 / 점심 / 오후 / 저녁 / 숙소 순으로 시간대별 일정을 구성해 주세요.
각 장소에 대해:
- 장소명
- 간단한 설명
- 추천 이유 (핫한지, 감성적인지 등)
- 예상 비용 (인당 또는 전체)
- 출처 (네이버 블로그, 인스타그램, 유튜브 등)

각 장소명 끝에 '지도: 네이버 지도 검색 링크'를 추가해 주세요. 예: 지도: https://map.naver.com/v5/search/장소명

조건 요약:
- 지역: {city} {district}
- 날짜: {date}
- 여행 기간: {days}일
- 동행: {companion}, 인원: {people}
- 분위기 키워드: {', '.join(vibe)}
- 음식 취향: {', '.join(food)}
- 총 예산: {budget:,}원 이내에서 해결
"""

    return None

# 버튼 클릭 시 실행
if st.button("✈️ AI에게 추천받기"):
    with st.spinner("AI가 취향 기반 맞춤 일정을 생성 중입니다..."):
        try:
            prompt = generate_prompt(travel_city, selected_district, travel_date, trip_days, companion, vibe, food, budget, people)
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 여행 일정 전문가입니다. 사용자의 조건을 바탕으로 현실적인 여행 계획을 작성하세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1800
            )
            result = response.choices[0].message.content
            st.success("✅ AI 추천 일정 생성 완료!")
            st.markdown("### 예시 📍")
            st.markdown(result)

            # 네이버 지도 링크 강조
            st.markdown("### 🗺️ 네이버 지도로 장소 검색하기")
            for line in result.split('\n'):

                if any(keyword in line for keyword in ["장소명", "- ", "* "]):
                    parts = line.split(":")
                    if len(parts) > 1:
                        place = parts[1].strip()
                        encoded = urllib.parse.quote(place)
                        link = f"https://map.naver.com/v5/search/{encoded}"
                        st.markdown(f"🔗 [{place} 네이버 지도 검색 링크]({link})")
            st.write("🧪 GPT 결과 확인:", result)

            
        except Exception as e:
            st.error(f"⚠️ 오류 발생: {str(e)}")
