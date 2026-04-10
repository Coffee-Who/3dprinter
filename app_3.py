import streamlit as st
import requests
import pandas as pd
import time
import random
from urllib.parse import quote
from bs4 import BeautifulSoup

# --- 頁面配置 ---
st.set_page_config(page_title="3D列印跨平台搜集", layout="wide")

# --- 104 API 邏輯 ---
def scrape_104(keyword):
    safe_keyword = quote(keyword)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Referer': f'https://www.104.com.tw/jobs/search/?kw={safe_keyword}',
        'X-Requested-With': 'XMLHttpRequest',
    }
    api_url = f"https://www.104.com.tw/jobs/search/list?ro=0&kw={safe_keyword}&order=1&asc=0&page=1&mode=s"
    try:
        session = requests.Session()
        session.get("https://www.104.com.tw/", headers=headers, timeout=10)
        time.sleep(random.uniform(1, 2))
        resp = session.get(api_url, headers=headers, timeout=15)
        if "application/json" not in resp.headers.get("Content-Type", ""):
            return "BLOCKED"
        data = resp.json()
        job_list = data.get('data', {}).get('list', [])
        return [{"來源": "104", "公司": j.get('custName'), "職位": j.get('jobName'), "內容": j.get('description')[:50]+"...", "連結": f"https://www.104.com.tw/job/{j.get('jobNo')}"} for j in job_list]
    except: return []

# --- 1111 爬蟲邏輯 ---
def scrape_1111(keyword):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
    url = f"https://www.1111.com.tw/search/job?ks={quote(keyword)}"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = soup.select('.job_item_info') # 這是 1111 的常見標籤類名
        results = []
        for item in items:
            results.append({
                "來源": "1111",
                "公司": item.select_one('.job_item_company').text.strip(),
                "職位": item.select_one('.job_item_title').text.strip(),
                "內容": "點擊連結查看詳情",
                "連結": "https://www.1111.com.tw" + item.select_one('a')['href']
            })
        return results
    except: return []

# --- UI 介面 ---
st.title("🏗️ 跨平台 3D 列印企業搜集器")

with st.sidebar:
    st.header("🔍 搜尋設定")
    # 新增：讓使用者勾選要爬哪些地方
    target_sites = st.multiselect(
        "選擇要爬取的平台",
        ["104 人力銀行", "1111 人力銀行"],
        default=["104 人力銀行"]
    )
    user_keywords = st.text_input("輸入關鍵字 (如: Formlabs)", "Formlabs")
    start_btn = st.button("🚀 開始跨平台搜集")

if start_btn:
    all_data = []
    progress_bar = st.progress(0)
    
    # 根據勾選的平台執行相對應的函式
    for i, site in enumerate(target_sites):
        st.write(f"正在從 **{site}** 抓取 **{user_keywords}**...")
        
        if site == "104 人力銀行":
            res = scrape_104(user_keywords)
        elif site == "1111 人力銀行":
            res = scrape_1111(user_keywords)
        
        if res == "BLOCKED":
            st.error(f"❌ {site} 暫時封鎖了你的 IP。")
        elif res:
            all_data.extend(res)
        
        progress_bar.progress((i + 1) / len(target_sites))
        time.sleep(2)

    if all_data:
        df = pd.DataFrame(all_data)
        st.success(f"完成！共找到 {len(df)} 筆結果。")
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 下載完整 CSV", csv, "results.csv", "text/csv")
    else:
        st.warning("查無資料。")
