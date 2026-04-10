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
        session.get("https://www.104.com.tw/", headers={'User-Agent': headers['User-Agent']}, timeout=10)
        time.sleep(random.uniform(1, 2))
        resp = session.get(api_url, headers=headers, timeout=15)
        
        if "application/json" not in resp.headers.get("Content-Type", ""):
            return "BLOCKED"
            
        data = resp.json()
        job_list = data.get('data', {}).get('list', [])
        
        results = []
        for j in job_list:
            results.append({
                "來源": "104",
                "公司名稱": j.get('custName'),
                "職位名稱": j.get('jobName', '').replace('<b>', '').replace('</b>', ''),
                "地點": j.get('jobAddrNoDesc'),
                "工作內容摘要": j.get('description', '').replace('\n', ' '),
                "連結": f"https://www.104.com.tw/job/{j.get('jobNo')}"
            })
        return results
    except Exception as e:
        return []

# --- 1111 爬蟲邏輯 ---
def scrape_1111(keyword):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    url = f"https://www.1111.com.tw/search/job?ks={quote(keyword)}"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = soup.select('.job_item_info') 
        results = []
        for item in items:
            try:
                results.append({
                    "來源": "1111",
                    "公司名稱": item.select_one('.job_item_company').text.strip(),
                    "職位名稱": item.select_one('.job_item_title').text.strip(),
                    "地點": "請點擊連結確認",
                    "工作內容摘要": item.select_one('.job_item_description').text.strip() if item.select_one('.job_item_description') else "點擊連結查看詳情",
                    "連結": "https://www.1111.com.tw" + item.select_one('a')['href'] if item.select_one('a') else ""
                })
            except:
                continue
        return results
    except:
        return []

# --- UI 介面 ---
st.title("🏗️ 跨平台 3D 列印企業情報搜集器")

with st.sidebar:
    st.header("🔍 搜尋設定")
    target_sites = st.multiselect(
        "選擇要爬取的平台",
        ["104 人力銀行", "1111 人力銀行"],
        default=["104 人力銀行"]
    )
    user_keywords = st.text_area("關鍵字 (多個請用英文逗號隔開)", "Formlabs, Phrozen")
    start_btn = st.button("🚀 開始跨平台搜集")

if start_btn:
    keywords = [k.strip() for k in user_keywords.split(',')]
    all_data = []
    progress_bar = st.progress(0)
    
    total_steps = len(target_sites) * len(keywords)
    step = 0

    for site in target_sites:
        for kw in keywords:
            step += 1
            st.write(f"正在從 **{site}** 抓取 **{kw}**...")
            
            if site == "104 人力銀行":
                res = scrape_104(kw)
            elif site == "1111 人力銀行":
                res = scrape_1111(kw)
            
            if res == "BLOCKED":
                st.error(f"❌ {site} 暫時封鎖了你的 IP。")
            elif isinstance(res, list):
                all_data.extend(res)
            
            progress_bar.progress(step / total_steps)
            time.sleep(random.uniform(2, 4))

    if all_data:
        df = pd.DataFrame(all_data)
        df_clean = df.drop_duplicates(subset=['公司名稱', '職位名稱']).reset_index(drop=True)
        st.success(f"完成！共找到 {len(df_clean)} 筆職缺資訊。")
        st.dataframe(df_clean, use_container_width=True)
        
        csv = df_clean.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 下載完整 CSV", csv, "leads_report.csv", "text/csv")
    else:
        st.warning("⚠️ 查無資料，請確認關鍵字或更換網路環境。")
