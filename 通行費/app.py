import streamlit as st
import requests

# ===== 設定 =====
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
DEFAULT_START = "實威國際 台中分公司"

# ===== Google 路徑 =====
def get_route(origin, destination):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "key": GOOGLE_API_KEY,
        "language": "zh-TW"
    }
    return requests.get(url, params=params).json()

# ===== 判斷是否國道 =====
def is_highway_step(step):
    text = step["html_instructions"]
    keywords = ["國道", "National", "Freeway"]
    return any(k in text for k in keywords)

# ===== 國道距離 =====
def get_highway_distance(data):
    steps = data["routes"][0]["legs"][0]["steps"]

    total = 0
    for step in steps:
        if is_highway_step(step):
            total += step["distance"]["value"]

    return total / 1000

# ===== ETC 計算 =====
def calc_etc_by_distance(km):
    free_km = 20

    if km <= free_km:
        return 0

    km -= free_km
    fee = 0

    if km > 0:
        d = min(km, 200)
        fee += d * 1.2
        km -= d

    if km > 0:
        d = min(km, 200)
        fee += d * 1.0
        km -= d

    if km > 0:
        fee += km * 0.9

    return round(fee)

# ===== UI =====
st.set_page_config(layout="wide")
st.title("🚗 ETC 國道費用計算（企業版 v3）")

origin = st.text_input("出發地", DEFAULT_START)
destination = st.text_input("目的地（客戶）")

if st.button("計算"):

    if not destination:
        st.warning("請輸入目的地")
        st.stop()

    data = get_route(origin, destination)

    try:
        route = data["routes"][0]
        leg = route["legs"][0]

        highway_km = get_highway_distance(data)
        fee = calc_etc_by_distance(highway_km)

        col1, col2 = st.columns(2)

        with col1:
            st.success(f"""
🚗 國道距離：{highway_km:.1f} km  
💰 ETC費用：約 {fee} 元  
⏱ 行車時間：{leg['duration']['text']}
""")

        with col2:
            map_url = f"https://www.google.com/maps/embed/v1/directions?key={GOOGLE_API_KEY}&origin={origin}&destination={destination}"
            st.components.v1.iframe(map_url, height=500)

    except:
        st.error("❌ 無法解析路線（請確認地址）")
