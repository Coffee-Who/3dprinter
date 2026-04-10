import streamlit as st
import requests
import pandas as pd
import time
import random

# --- 頁面配置 ---
st.set_page_config(page_title="3D列印企業情報搜集", layout="wide")

def scrape_104_api(keyword):
    """透過 104 API 抓取：包含公司、職位、工作內容摘要"""
    # 模擬 104 內部 AJAX 請求的 Headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': f'https://www.104.com.tw/jobs/search/?kw={keyword}',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # 104 實際儲存資料的 API 介面
    api_url = f"https://www.104.com.tw/jobs/search/list?ro=0&kw={keyword}&order=1&asc=0&page=1&mode=s"
    
    try:
        resp = requests.get(api_url, headers=headers, timeout=15)
        if resp.status_code != 200:
            st.warning(f"104 伺服器回應異常 (Status: {resp.status_code})，可能 IP 已被封鎖。")
            return []
            
        data = resp.json()
        job_list = data.get('data', {}).get('list', [])
        
        results = []
        for job in job_list:
            # 清除 HTML 標籤 (例如職稱裡的 <b>)
            clean_title = job.get('jobName', '').replace('<b>', '').replace('</b>', '')
            clean_desc = job.get('description', '').replace('\n', ' ').replace('\r', '')
            
            results.append({
                "來源": "104 (API)",
                "公司名稱": job.get('custName'),
                "職位名稱": clean_title,
                "工作內容摘要": clean_desc,
                "地點": job.get('jobAddrNoDesc'),
                "連結": f"https://www.104.com.tw/job/{job.get('jobNo')}"
            })
        return results
    except Exception as e:
        st.error(f"104 API 抓取失敗: {e}")
        return []

def scrape_1111(keyword):
    """抓取 1111 人力銀行 (保持 HTML 解析)"""
    from bs4 import BeautifulSoup
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
                results.append({
                    "來源": "1111",
                    "公司名稱": item.select_one('.job_item_company').text.strip(),
                    "職位名稱": item.select_one('.job_item_title').text.strip(),
                    "工作內容摘要": item.select_one('.job_item_description').text.strip() if item.select_one('.job_item_description') else "",
                    "地點": "N/A",
                    "連結": "https://www.1111.com.tw" + item.select_one('a')['href'] if item.select_one('a') else ""
                })
            except: continue
        return results
    except Exception as e:
        return []

# --- Streamlit UI ---
st.title("🏗️ 3D 列印企業情報搜集器 (API 加速版)")
st.info("此版本直接串接網站數據介面，抓取更精準且包含地點與工作摘要。")

with st.sidebar:
    st.header("搜尋設定")
    selected_sites = st.multiselect("選擇平台", ["104 人力銀行", "1111 人力銀行"], default=["104 人力銀行"])
    user_input = st.text_area("關鍵字 (逗號隔開)", "Formlabs, Phrozen, Bambu Lab, 3D列印")
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
                all_res.extend(scrape_104_api(kw))
            elif site == "1111 人力銀行":
                all_res.extend(scrape_1111(kw))
            
            progress_bar.progress(count / total)
            time.sleep(random.uniform(1, 2)) # API 版不需要太長等待，但建議仍保留間隔

    if all_res:
        df = pd.DataFrame(all_res)
        df_clean = df.drop_duplicates(subset=['公司名稱', '職位名稱']).reset_index(drop=True)
        
        st.success(f"完成！共找到 {len(df_clean)} 筆職缺資訊。")
        st.dataframe(df_clean, use_container_width=True)
        
        csv = df_clean.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 下載詳細名單 (CSV)", data=csv, file_name="3d_printing_jobs_full.csv", mime="text/csv")
    else:
        st.error("❌ 所有平台皆未發現資料。這通常意味著 Streamlit Cloud 的 IP 已被封鎖。")
        st.markdown("""
        ### 🛡️ 為什麼會這樣？
        104 等大型網站會阻擋來自 **Google Cloud/AWS** (Streamlit Cloud 的所在地) 的自動化請求。
        
        **建議解決方案：**
        1. **在個人電腦執行：** 下載此程式碼並在本地 CMD 執行 `streamlit run app_2.py`。
        2. **更換關鍵字：** 嘗試「3D打印」或「光固化」測試。
        """)
