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
st.set_page_config(page_title="3D列印企業多平台搜集", layout="wide")

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    cloud_chromium_path = "/usr/bin/chromium"
    cloud_driver_path = "/usr/bin/chromedriver"
    
    if os.path.exists(cloud_chromium_path):
        options.binary_location = cloud_chromium_path
        return webdriver.Chrome(service=Service(cloud_driver_path), options=options)
    else:
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_logic(driver, site, keyword):
    """
    根據不同的網站，執行不同的爬取邏輯
    """
    results = []
    
    if site == "104 人力銀行":
        url = f"https://www.104.com.tw/jobs/search/?ro=0&kw={keyword}&order=1&asc=0&page=1&mode=s&lang=tw"
        driver.get(url)
        time.sleep(4)
        # 抓取 104 的公司與職缺
        items = driver.find_elements(By.XPATH, '//article[contains(@class, "job-list-item")]')
        for item in items:
            try:
                company = item.get_attribute('data-cust-name')
                job = item.get_attribute('data-job-name')
                if company:
                    results.append({"來源": "104", "公司名稱": company, "職缺/內容": job})
            except: continue

    elif site == "1111 人力銀行":
        url = f"https://www.1111.com.tw/search/job?ks={keyword}"
        driver.get(url)
        time.sleep(4)
        # 1111 的標籤結構不同，範例抓取邏輯：
        items = driver.find_elements(By.CLASS_NAME, 'job_item_info')
        for item in items:
            try:
                company = item.find_element(By.CLASS_NAME, 'job_item_company').text
                job = item.find_element(By.CLASS_NAME, 'job_item_title').text
                results.append({"來源": "1111", "公司名稱": company, "職缺/內容": job})
            except: continue

    return results

# --- 介面設計 ---
st.title("🏗️ 3D 列印企業多平台情報搜集器")

with st.sidebar:
    st.header("1. 設定搜尋平台")
    selected_sites = st.multiselect(
        "選擇要搜尋的網站",
        ["104 人力銀行", "1111 人力銀行"],
        default=["104 人力銀行"]
    )
    
    st.header("2. 設定關鍵字")
    user_input = st.text_area("關鍵字 (逗號隔開)", "Formlabs, Phrozen, Bambu Lab")
    
    start_btn = st.button("🚀 開始跨平台爬取")

if start_btn:
    if not selected_sites:
        st.warning("請至少選擇一個搜尋平台。")
    else:
        keywords = [k.strip() for k in user_input.split(',')]
        all_data = []
        
        driver = get_driver()
        progress_bar = st.progress(0)
        
        total_tasks = len(selected_sites) * len(keywords)
        current_task = 0
        
        try:
            for site in selected_sites:
                for kw in keywords:
                    current_task += 1
                    st.write(f"正在從 {site} 搜尋：**{kw}**...")
                    data = scrape_logic(driver, site, kw)
                    all_data.extend(data)
                    progress_bar.progress(current_task / total_tasks)
            
            if all_data:
                df = pd.DataFrame(all_data)
                # 簡單去重
                df_clean = df.drop_duplicates(subset=['公司名稱']).reset_index(drop=True)
                st.success(f"跨平台搜尋完成！共找到 {len(df_clean)} 家公司。")
                st.dataframe(df_clean, use_container_width=True)
                
                csv = df_clean.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button("📥 下載完整報表", data=csv, file_name="multi_site_companies.csv")
            else:
                st.info("所有平台皆未發現相關資料。")
        finally:
            driver.quit()
