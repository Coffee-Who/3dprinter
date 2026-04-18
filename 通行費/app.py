import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ===== 設定 =====
GOOGLE_API_KEY = "你的API KEY"
DEFAULT_START = "實威國際 台中分公司"

# ===== 載入 ETC 表 =====
df_fee = pd.read_csv("etc_fee.csv")

# ===== 交流道對應 =====
interchange_keywords = {
    "台中交流道": "台中",
    "南屯交流道": "南屯",
    "彰化交流道": "彰化",
    "新竹交流道": "新竹",
    "桃園交流道": "桃園"
}

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

# ===== 抓交流道 =====
def extract_interchanges(data):
    steps = data["routes"][0]["legs"][0]["steps"]

    start_ic = None
    end_ic = None

    for step in steps:
        text = step["html_instructions"]

        if "國道" in text and "入口" in text and not start_ic:
            for key in interchange_keywords:
                if key in text:
                    start_ic = interchange_keywords[key]

        if "出口" in text:
            for key in interchange_keywords:
                if key in text:
                    end_ic = interchange_keywords[key]

    return start_ic, end_ic

# ===== ETC 計算 =====
def get_fee(start, end):
    try:
        fee = df_fee[
            (df_fee["起點"] == start) &
            (df_fee["終點"] == end)
        ]["費用"].values[0]
        return fee
    except:
        return "查無費率"

# ===== 建立報帳 =====
def create_report(origin, destination, start_ic, end_ic, fee):
    df = pd.DataFrame([{
        "日期": datetime.now().strftime("%Y-%m-%d"),
        "出發地": origin,
        "目的地": destination,
        "起點交流道": start_ic,
        "終點交流道": end_ic,
        "ETC費用": fee
    }])
    file_name = "ETC報帳.xlsx"
    df.to_excel(file_name, index=False)
    return file_name

# ===== UI =====
st.set_page_config(layout="wide")
st.title("🚗 ETC 費用計算系統（企業版 v2）")

origin = st.text_input("出發地", DEFAULT_START)
destination = st.text_input("客戶公司 / 地址")

if st.button("開始計算"):

    if not destination:
        st.warning("請輸入目的地")
    else:
        data = get_route(origin, destination)

        try:
            route = data["routes"][0]
            leg = route["legs"][0]

            start_ic, end_ic = extract_interchanges(data)
            fee = get_fee(start_ic, end_ic)

            # ===== 顯示資訊 =====
            col1, col2 = st.columns(2)

            with col1:
                st.success(f"""
                🚏 起點交流道：{start_ic}  
                🏁 終點交流道：{end_ic}  
                💰 ETC費用：{fee} 元  
                ⏱ 行車時間：{leg['duration']['text']}
                """)

                file = create_report(origin, destination, start_ic, end_ic, fee)

                with open(file, "rb") as f:
                    st.download_button(
                        "📥 下載報帳Excel",
                        f,
                        file_name=file
                    )

            with col2:
                # ===== 顯示地圖 =====
                map_url = f"https://www.google.com/maps/embed/v1/directions?key={GOOGLE_API_KEY}&origin={origin}&destination={destination}"
                st.components.v1.iframe(map_url, height=500)

        except:
            st.error("解析失敗（可能抓不到交流道）")
