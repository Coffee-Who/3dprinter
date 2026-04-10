import streamlit as st
import requests
import pandas as pd
import time
import random
from urllib.parse import quote
from bs4 import BeautifulSoup

# --- 頁面配置 ---
st.set_page_config(page_title="跨平台企業情報搜集", layout="wide")

# --- 通用 Google 站內搜尋邏輯 (核心新增功能) ---
def scrape_custom_site(keyword, domain):
    """
    利用 Google 的 site: 指令去特定網站搜尋資料
    這讓你可以輸入任何網站，如 518.com.tw 或 yes123.com.tw
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    # 組合 Google 指令，例如: "Formlabs site:518.com.tw"
    search_query = f"{keyword} site:{domain.replace('https://', '').replace('http://', '').split('/')[0]}"
    url = f"https://www.google.com/search?q={quote(search_query)}"
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = soup.select('div.tF2Cxc') 
        
        results = []
        for item in items:
            title = item.select_one('h3').text if item.select_one('h3') else "無標題"
            link = item.select_one('a')['href'] if item.select_one('a') else ""
            desc = item.select_one('div.VwiC3b').text if item.select_one('div.VwiC3b') else ""
            
            results.append({
                "來源平台": domain,
                "公司/標題": title,
                "摘要內容": desc,
                "連結": link
            })
        return results
    except Exception as e:
        return [f"搜尋出錯: {e}"]

# --- 104 專用 API 邏輯 ---
def scrape_104(keyword):
    safe_keyword = quote(keyword)
    headers = {'User-Agent': 'Mozilla/5.0', 'X-Requested-With': 'XMLHttpRequest'}
    api_url = f"https://www.104.com.tw/jobs/search/list?ro=0&kw={safe_keyword}&order=1&asc=0&page=1&mode=s"
    try:
        resp = requests.get(api_url, headers=headers, timeout=10)
        data = resp.json()
        job_list = data.get('data', {}).get('list', [])
        return [{"來源平台": "104人力銀行", "公司/標題": j.get('custName'), "摘要內容": j.get('jobName') + " | " + j.get('description')[:50], "連結": f"https://www.104.com.tw/job/{j.get('jobNo')}"} for j in job_list]
    except: return []

# --- UI 介面 ---
st.title("🏗️ 萬用企業情報搜集器")
st.info("您可以指定特定的網站（如 yes123.com.tw）來進行深度搜尋。")

with st.sidebar:
    st.header("🔍 設定搜尋目標")
    
    # 1. 關鍵字輸入
    user_keywords = st.text_input("1. 輸入設備/關鍵字", "Formlabs")
    
    # 2. 平台選擇 (固定 + 自定義)
    base_sites = st.multiselect("2. 選擇內建平台", ["104人力銀行", "Google 全域搜尋"], default=["104人力銀行"])
    
    # 3. 自定義平台輸入 (這就是你要的功能！)
    custom_domain = st.text_input("3. 想要額外搜尋的網址 (選填)", placeholder="例如: yes123.com.tw")
    
    start_btn = st.button("🚀 開始搜集資料")

if start_btn:
    all_data = []
    
    # 處理內建平台
    for site in base_sites:
        st.write(f"正在搜尋內建平台：**{site}**...")
        if site == "104人力銀行":
            all_data.extend(scrape_104(user_keywords))
        elif site == "Google 全域搜尋":
            all_data.extend(scrape_custom_site(user_keywords, "google.com"))
        time.sleep(2)

    # 處理使用者自定義的平台 (利用 Google site: 語法)
    if custom_domain:
        st.write(f"正在對指定網站 **{custom_domain}** 進行精確搜尋...")
        res = scrape_custom_site(user_keywords, custom_domain)
        if isinstance(res, list):
            all_data.extend(res)
        time.sleep(2)

    # 顯示結果
    if all_data:
        df = pd.DataFrame(all_data)
        st.success(f"搜集完成！共找到 {len(df)} 筆潛在資訊。")
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 下載 Excel CSV 報表", csv, "leads_data.csv", "text/csv")
    else:
        st.warning("查無資料，請確認網址格式是否正確（例如只需要輸入 domain.com）。")
