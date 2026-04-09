import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os

# --- 頁面配置 ---
st.set_page_config(page_title="3D列印企業搜集器", layout="wide")

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    # 解決版本衝突的關鍵：優先使用系統內建的路徑
    cloud_chromium_path = "/usr/bin/chromium"
    cloud_driver_path = "/usr/bin/chromedriver"
    
    if os.path.exists(cloud_chromium_path):
        options.binary_location = cloud_chromium_path
        # 雲端環境：直接使用系統安裝的 ChromeDriver
        try:
            return webdriver.Chrome(service=Service(cloud_driver_path), options=options)
        except Exception:
            # 如果失敗，嘗試不帶路徑啟動
            return webdriver.Chrome(options=options)
    else:
        # 本地環境 (Windows/Mac)：使用 webdriver-manager 自動下載
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_104(keywords):
    driver = get_driver()
    if not driver:
        st.error("無法啟動瀏覽器，請確認 packages.txt 設定是否正確。")
        return pd.DataFrame()

    all_results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        for index, kw in enumerate(keywords):
            status_text.text(f"🔍 正在搜尋關鍵字：{kw} ...")
            url = f"https://www.104.com.tw/jobs/search/?ro=0&kw={kw}&order=1&asc=0&page=1&mode=s&jobsource=2018indexpoc"
            
            driver.get(url)
            time.sleep(4) # 稍微加長等待時間，確保頁面載入完全
            
            job_cards = driver.find_elements(By.CSS_SELECTOR, 'article.job-list-item')
            
            for card in job_cards:
                company_name = card.get_attribute('data-cust-name')
                job_title = card.get_attribute('data-job-name')
                if company_name:
                    all_results.append({
                        "搜尋關鍵字": kw,
                        "公司名稱": company_name,
                        "職缺名稱": job_title
                    })
            
            progress_bar.progress((index + 1) / len(keywords))
    except Exception as e:
        st.warning(f"爬取過程中發生意外: {e}")
    finally:
        driver.quit()
    
    status_text.text("✅ 任務執行結束！")
    return pd.DataFrame(all_results)

# --- 介面設計 ---
st.title("🏗️ 3D 列印使用企業搜集器")
st.markdown("透過 104 人力銀行搜尋特定設備關鍵字，分析潛在客戶。")

with st.sidebar:
    st.header("搜尋設定")
    user_input = st.text_area("關鍵字 (逗號隔開)", 
                           "Formlabs, Phrozen, Bambu Lab, Creality, Stratasys")
    start_btn = st.button("🚀 開始爬取")

if start_btn:
    keywords = [k.strip() for k in user_input.split(',')]
    df_raw = scrape_104(keywords)
    
    if not df_raw.empty:
        df_clean = df_raw.drop_duplicates(subset=['公司名稱']).reset_index(drop=True)
        st.success(f"找到 {len(df_clean)} 家不重複公司")
        st.dataframe(df_clean, use_container_width=True)
        
        csv = df_clean.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 下載 CSV 結果", data=csv, file_name="companies.csv")
    else:
        st.info("本次搜尋未發現相關資料。")
