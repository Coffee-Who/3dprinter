import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os

# --- 頁面設定 ---
st.set_page_config(page_title="3D列印企業搜集器", layout="wide")

# --- 爬蟲核心函式 ---
def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    # 針對 Streamlit Cloud 環境的特殊設定
    # 雲端 Linux 環境通常將 chromium 放在此路徑
    if os.path.exists("/usr/bin/chromium-browser"):
        options.binary_location = "/usr/bin/chromium-browser"
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        st.error(f"瀏覽器啟動失敗: {e}")
        return None

def scrape_104(keywords):
    driver = get_driver()
    if not driver:
        return pd.DataFrame()

    all_results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for index, kw in enumerate(keywords):
        status_text.text(f"🔍 正在搜尋關鍵字：{kw} ...")
        
        # 104 搜尋 URL
        url = f"https://www.104.com.tw/jobs/search/?ro=0&kw={kw}&order=1&asc=0&page=1&mode=s&jobsource=2018indexpoc"
        
        try:
            driver.get(url)
            time.sleep(3)  # 給予足夠時間載入內容
            
            job_cards = driver.find_elements(By.CSS_SELECTOR, 'article.job-list-item')
            
            for card in job_cards:
                company_name = card.get_attribute('data-cust-name')
                job_title = card.get_attribute('data-job-name')
                
                if company_name:
                    all_results.append({
                        "來源關鍵字": kw,
                        "公司名稱": company_name,
                        "職缺名稱": job_title
                    })
        except Exception as e:
            st.warning(f"搜尋 {kw} 時發生錯誤: {e}")
        
        # 更新進度
        progress_bar.progress((index + 1) / len(keywords))
    
    driver.quit()
    status_text.text("✅ 爬取任務完成！")
    return pd.DataFrame(all_results)

# --- Streamlit 介面 ---
st.title("🏗️ 3D 列印使用企業搜集器 (104人力銀行)")
st.info("本工具透過模擬瀏覽器搜尋職缺描述，找出可能使用特定 3D 列印設備的公司。")

with st.sidebar:
    st.header("搜尋設定")
    default_keywords = "Formlabs, Form 3, SLA 3D Printing, Phrozen, Bambu Lab, Creality, Ultimaker, Stratasys"
    user_input = st.text_area("關鍵字清單 (請用逗號隔開)", default_keywords, height=200)
    
    start_btn = st.button("🚀 開始執行爬蟲")

if start_btn:
    keywords = [k.strip() for k in user_input.split(',')]
    
    with st.spinner('正在與 104 進行連線...'):
        result_df = scrape_104(keywords)
    
    if not result_df.empty:
        # 資料整理：去重
        clean_df = result_df.drop_duplicates(subset=['公司名稱']).reset_index(drop=True)
        
        # 顯示統計
        c1, c2 = st.columns(2)
        c1.metric("總共抓取項目", len(result_df))
        c2.metric("不重複公司數", len(clean_df))
        
        # 顯示資料與下載
        st.subheader("🏢 找到的公司清單")
        st.dataframe(clean_df, use_container_width=True)
        
        csv_data = clean_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 下載企業名單 (.csv)",
            data=csv_data,
            file_name="3d_printing_companies.csv",
            mime="text/csv"
        )
    else:
        st.error("未能抓取到任何資料，請確認網路連線或稍後再試。")
