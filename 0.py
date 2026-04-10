import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# --- 頁面配置 ---
st.set_page_config(page_title="3D列印企業情報搜集", layout="wide")

def scrape_104(keyword):
    """抓取 104 人力銀行：包含公司、職位、工作內容摘要"""
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
        articles = soup.find_all('article', class_='job-list-item')
        
        results = []
        for art in articles:
            # 1. 抓取公司名稱
            company = art.get('data-cust-name')
            # 2. 抓取職位名稱
            job_title = art.get('data-job-name')
            # 3. 抓取工作內容描述 (通常在 class 為 job-list-item__info 的 p 標籤)
            # 104 的結構中，描述通常放在 class="job-list-item__info b-dot--hide b-clearfix"
            description = ""
            desc_tag = art.find('p', class_='job-list-item__info')
            if desc_tag:
                description = desc_tag.text.strip()
            
            # 4. 抓取詳細連結 (選配)
            link = "https:" + art.find('a', class_='js-job-link')['href'] if art.find('a', class_='js-job-link') else ""

            if company:
                results.append({
                    "來源": "104",
                    "公司名稱": company,
                    "職位名稱": job_title,
                    "工作內容摘要": description,
                    "連結": link
                })
        return results
    except Exception as e:
        st.error(f"104 搜尋出錯: {e}")
        return []

def scrape_1111(keyword):
    """抓取 1111 人力銀行：包含公司、職位、工作內容摘要"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    url = f"https://www.1111.com.tw/search/job?ks={keyword}"
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        items = soup.select('.job_item_info')
        results = []
        for item in items:
            try:
                company = item.select_one('.job_item_company').text.strip()
                job_title = item.select_one('.job_item_title').text.strip()
                # 1111 的描述通常在 .job_item_description
                description = item.select_one('.job_item_description').text.strip() if item.select_one('.job_item_description') else ""
                
                results.append({
                    "來源": "1111",
                    "公司名稱": company,
                    "職位名稱": job_title,
                    "工作內容摘要": description,
                    "連結": "N/A"
                })
            except:
                continue
        return results
    except Exception as e:
        st.error(f"1111 搜尋出錯: {e}")
        return []

# --- Streamlit UI ---
st.title("🏗️ 3D 列印企業情報搜集器 (詳細版)")

with st.sidebar:
    st.header("搜尋設定")
    selected_sites = st.multiselect("選擇平台", ["104 人力銀行", "1111 人力銀行"], default=["104 人力銀行"])
    user_input = st.text_area("關鍵字 (逗號隔開)", "Formlabs, Phrozen, Bambu Lab")
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
            time.sleep(random.uniform(2, 4)) # 增加延遲，讓網站覺得你更像真人

    if all_res:
        df = pd.DataFrame(all_res)
        # 去重，但保留職位資訊
        df_clean = df.drop_duplicates(subset=['公司名稱', '職位名稱']).reset_index(drop=True)
        
        st.success(f"完成！共找到 {len(df_clean)} 筆職缺資訊。")
        
        # 顯示搜尋結果
        st.dataframe(df_clean, use_container_width=True)
        
        # 下載按鈕
        csv = df_clean.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 下載完整 Excel 報表 (CSV)", data=csv, file_name="3d_printing_jobs.csv", mime="text/csv")
    else:
        st.warning("⚠️ 未發現資料。建議手動打開 104 搜尋看看關鍵字是否有結果。")
