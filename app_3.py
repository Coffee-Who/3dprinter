import streamlit as st
import requests
import pandas as pd
import time
import random
from urllib.parse import quote
from bs4 import BeautifulSoup

# --- 頁面配置 ---
st.set_page_config(page_title="萬用企業情報搜集器", layout="wide")

def scrape_custom_site(keyword, domain):
    """
    優化後的 Google 站內搜尋邏輯
    """
    # 隨機更換 User-Agent 減少被擋機率
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
    ]
    
    headers = {
        'User-Agent': random.choice(ua_list),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://www.google.com/'
    }

    # 處理 domain 格式，確保只保留主網域
    clean_domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
    
    # 組合搜尋字串
    if clean_domain.lower() == "google.com":
        search_query = f"{keyword} 3D列印 徵才"
    else:
        search_query = f"{keyword} site:{clean_domain}"
    
    url = f"https://www.google.com/search?q={quote(search_query)}&hl=zh-TW"
    
    try:
        # 增加隨機延遲模擬真人行為
        time.sleep(random.uniform(1, 3))
        resp = requests.get(url, headers=headers, timeout=15)
        
        if resp.status_code != 200:
            return f"ERROR: Google 回傳狀態碼 {resp.status_code} (可能被擋了)"
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Google 搜尋結果的標籤結構 (標題在 h3, 連結在 a)
        items = soup.select('div.g') # 這是 Google 搜尋結果最外層的 div
        
        results = []
        for item in items:
            title_tag = item.select_one('h3')
            link_tag = item.select_one('a')
            desc_tag = item.select_one('div.VwiC3b') # 描述摘要
            
            if title_tag and link_tag:
                results.append({
                    "來源平台": clean_domain,
                    "公司名稱/標題": title_tag.text,
                    "內容摘要": desc_tag.text if desc_tag else "無摘要",
                    "連結": link_tag['href']
                })
        return results
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- 104 API 邏輯 (保持穩定) ---
def scrape_104(keyword):
    safe_keyword = quote(keyword)
    headers = {'User-Agent': 'Mozilla/5.0', 'X-Requested-With': 'XMLHttpRequest'}
    api_url = f"https://www.104.com.tw/jobs/search/list?ro=0&kw={safe_keyword}&order=1&asc=0&page=1&mode=s"
    try:
        resp = requests.get(api_url, headers=headers, timeout=10)
        data = resp.json()
        job_list = data.get('data', {}).get('list', [])
        return [{"來源平台": "104人力銀行", "公司名稱/標題": j.get('custName'), "內容摘要": f"{j.get('jobName')} | {j.get('description')[:50]}", "連結": f"https://www.104.com.tw/job/{j.get('jobNo')}"} for j in job_list]
    except: return []

# --- UI 介面 ---
st.title("🚀 萬用企業情報搜集器")

with st.sidebar:
    st.header("🔍 設定搜尋目標")
    user_keywords = st.text_input("1. 輸入關鍵字 (如: Formlabs)", "Formlabs")
    
    base_sites = st.multiselect("2. 內建平台", ["104人力銀行", "Google 全域"], default=["104人力銀行"])
    
    custom_domain = st.text_input("3. 自定義搜尋平台 (選填)", placeholder="例如: yes123.com.tw")
    
    start_btn = st.button("🚀 開始搜集")

if start_btn:
    all_data = []
    
    # 處理 104
    if "104人力銀行" in base_sites:
        st.write("正在搜尋：**104人力銀行**...")
        all_data.extend(scrape_104(user_keywords))

    # 處理 Google 全域
    if "Google 全域" in base_sites:
        st.write("正在搜尋：**Google 全域**...")
        res = scrape_custom_site(user_keywords, "google.com")
        if isinstance(res, list): all_data.extend(res)

    # 處理自定義平台
    if custom_domain:
        st.write(f"正在搜尋自定義平台：**{custom_domain}**...")
        res = scrape_custom_site(user_keywords, custom_domain)
        if isinstance(res, list):
            all_data.extend(res)
        elif isinstance(res, str) and "ERROR" in res:
            st.error(res)

    if all_data:
        df = pd.DataFrame(all_data)
        st.success(f"完成！共找到 {len(df)} 筆資料。")
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 下載 Excel CSV", csv, "search_results.csv", "text/csv")
    else:
        st.warning("查無資料。可能原因：關鍵字太冷門、網址輸入錯誤，或 Google 暫時封鎖了頻繁查詢。")
