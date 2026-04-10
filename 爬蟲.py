import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

st.set_page_config(page_title="3D列印企業搜集器", layout="wide")

def scrape_104_fast(keyword):
    # 偽裝成真實瀏覽器的 Headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.104.com.tw/'
    }
    
    # 104 的搜尋網址
    url = f"https://www.104.com.tw/jobs/search/?ro=0&kw={keyword}&order=1&asc=0&page=1&mode=s&lang=tw"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            st.error(f"無法連線到 104 (狀態碼: {response.status_code})")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 104 的公司名稱通常存在於 article 標籤的 data-cust-name 屬性
        job_articles = soup.find_all('article', class_='job-list-item')
        
        results = []
        for article in job_articles:
            company = article.get('data-cust-name')
            job = article.get('data-job-name')
            if company:
                results.append({"來源": "104", "公司名稱": company, "職缺": job})
        return results
    except Exception as e:
        st.error(f"搜尋 {keyword} 時發生錯誤: {e}")
        return []

# --- 介面 ---
st.title("🚀 高速版 3D 列印企業搜集器")
st.write("此版本不使用瀏覽器模擬，更穩定且不易崩潰。")

kw_input = st.text_input("輸入關鍵字 (如: Formlabs, Phrozen)", "Formlabs")

if st.button("開始執行"):
    with st.spinner("搜尋中..."):
        data = scrape_104_fast(kw_input)
        if data:
            df = pd.DataFrame(data).drop_duplicates(subset=['公司名稱'])
            st.success(f"成功找到 {len(df)} 家企業！")
            st.dataframe(df)
            
            csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("下載 CSV", csv, "data.csv", "text/csv")
        else:
            st.warning("未找到資料。這可能是因為 104 擋住了雲端伺服器的 IP。")
