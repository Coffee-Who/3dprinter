import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# --- 頁面配置 ---
st.set_page_config(page_title="3D列印企業情報搜集", layout="wide")

def scrape_104(keyword):
    """抓取 104 人力銀行資料"""
    # 模擬真實瀏覽器的 Header，避免被當成機器人
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.104.com.tw/'
    }
    url = f"https://www.104.com.tw/jobs/search/?ro=0&kw={keyword}&order=1&asc=0&page=1&mode=s&lang=tw"
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        # 104 的職缺資訊存在於 <article> 標籤中
        articles = soup.find_all('article', class_='job-list-item')
        
        results = []
        for art in articles:
            company = art.get('data-cust-name')
            job = art.get('data-job-name')
            if company:
                results.append({"來源": "104", "公司名稱": company, "相關職缺": job})
        return results
    except Exception as e:
        st.error(f"104 搜尋出錯: {e}")
        return []

def scrape_1111(keyword):
    """抓取 1111 人力銀行資料"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    # 1111 搜尋 URL
    url = f"https://www.1111.com.tw/search/job?ks={keyword}"
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 1111 結構較複雜，通常公司名稱在特定的 class 中
        # 注意：網站結構可能隨時變動，此為常用標籤範例
        items = soup.select('.job_item_info')
        results = []
        for item in items:
            try:
                company = item.select_one('.job_item_company').text.strip()
                job = item.select_one('.job_item_title').text.strip()
                results.append({"來源": "1111", "公司名稱": company, "相關職缺": job})
            except:
                continue
        return results
    except Exception as e:
        st.error(f"1111 搜尋出錯: {e}")
        return []

# --- Streamlit UI ---
st.title("🏗️ 3D 列印企業情報搜集器 (輕量版)")
st.info("此版本使用 Requests 技術，不啟動瀏覽器，運行更快速穩定。")

with st.sidebar:
    st.header("搜尋設定")
    selected_sites = st.multiselect("選擇平台", ["104 人力銀行", "1111 人力銀行"], default=["104 人力銀行"])
    user_input = st.text_area("關鍵字 (逗號隔開)", "Formlabs, Phrozen, Bambu Lab, Stratasys")
    start_btn = st.button("🚀 開始搜集")

if start_btn:
    keywords = [k.strip() for k in user_input.split(',')]
    all_res = []
    
    progress_bar = st.progress(0)
    total = len(selected_sites) * len(keywords)
    count = 0
    
    for site in selected_sites:
        for kw in keywords:
            count += 1
            st.write(f"正在搜尋 {site}：**{kw}**...")
            
            if site == "104 人力銀行":
                all_res.extend(scrape_104(kw))
            elif site == "1111 人力銀行":
                all_res.extend(scrape_1111(kw))
            
            progress_bar.progress(count / total)
            # 隨機延遲，避免被封鎖
            time.sleep(random.uniform(1.5, 3.0))

    if all_res:
        df = pd.DataFrame(all_res).drop_duplicates(subset=['公司名稱']).reset_index(drop=True)
        st.success(f"完成！共找到 {len(df)} 家不重複公司。")
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 下載 Excel 格式 (CSV)", data=csv, file_name="3d_printing_list.csv", mime="text/csv")
    else:
        st.warning("⚠️ 未發現資料。可能是關鍵字太冷門，或是雲端 IP 被網站暫時屏蔽。")
