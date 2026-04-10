import streamlit as st
import requests
import pandas as pd
import time
import random
from urllib.parse import quote
from bs4 import BeautifulSoup

st.set_page_config(page_title="3D列印設備企業搜集器", layout="wide")

def google_search_leads(keyword, strategy):
    """
    根據不同策略組合 Google 指令，精準挖掘有設備的企業
    """
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
    ]
    headers = {'User-Agent': random.choice(ua_list)}

    # --- 核心：策略指令組合 ---
    if strategy == "找徵才中的企業 (有職缺代表有設備)":
        query = f'"{keyword}" (徵才 OR 招募 OR "工程師") site:com.tw'
    elif strategy == "找新聞/標案 (引進新設備的報導)":
        query = f'"{keyword}" (採購 OR 引進 OR 發表 OR "導入")'
    elif strategy == "找合作案例 (設備商官網的客戶名單)":
        query = f'"{keyword}" (客戶案例 OR 成功案例 OR "應用實績")'
    else: # 自定義
        query = keyword

    st.caption(f"🔍 執行指令: {query}")
    url = f"https://www.google.com/search?q={quote(query)}&hl=zh-TW"
    
    try:
        time.sleep(random.uniform(2, 4))
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200: return "BLOCKED"
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = soup.select('div.g')
        results = []
        for item in items:
            title = item.select_one('h3').text if item.select_one('h3') else ""
            link = item.select_one('a')['href'] if item.select_one('a') else ""
            desc = item.select_one('div.VwiC3b').text if item.select_one('div.VwiC3b') else ""
            if title and link:
                results.append({"可能企業/標題": title, "資訊摘要": desc, "網址連結": link})
        return results
    except: return []

# --- UI 介面 ---
st.title("🏭 3D 列印潛在企業開發工具")
st.markdown("透過掃描全網資訊（新聞、徵才、案例），找出哪些公司正在使用特定的 3D 列印技術。")

with st.sidebar:
    st.header("🎯 開發設定")
    keyword = st.text_input("輸入設備或型號", "Formlabs")
    
    strategy = st.selectbox("選擇搜集策略", [
        "找徵才中的企業 (有職缺代表有設備)",
        "找新聞/標案 (引進新設備的報導)",
        "找合作案例 (設備商官網的客戶名單)",
        "單純搜尋關鍵字"
    ])
    
    st.divider()
    st.info("💡 提示：若出現查無資料，請嘗試更換『策略』或點擊上方按鈕重試。")

if st.button("🚀 開始挖掘潛在客戶"):
    with st.spinner("正在掃描網路資料..."):
        res = google_search_leads(keyword, strategy)
        
        if res == "BLOCKED":
            st.error("❌ Google 暫時限制了您的訪問。建議：1. 等 5 分鐘再試 2. 使用手機熱點換 IP。")
        elif res:
            df = pd.DataFrame(res)
            st.success(f"找到 {len(df)} 筆潛在關聯資訊！")
            st.dataframe(df, use_container_width=True)
            
            # 檔案下載
            csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("📥 下載企業潛在名單 (CSV)", csv, f"3D_leads_{keyword}.csv", "text/csv")
        else:
            st.warning("⚠️ 查無資料。請嘗試更換搜尋策略或關鍵字（如換成：SLA、工業級3D列印）。")
