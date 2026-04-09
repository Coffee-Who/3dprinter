import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# --- 爬蟲核心函式 ---
def scrape_104(keywords):
    options = Options()
    options.add_argument('--headless')  # 必備：不啟動實體瀏覽器視窗
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # 初始化 WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    all_results = []
    
    progress_bar = st.progress(0)
    for index, kw in enumerate(keywords):
        st.write(f"🔍 正在搜尋關鍵字：{kw}...")
        url = f"https://www.104.com.tw/jobs/search/?ro=0&kw={kw}&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&order=1&asc=0&page=1&mode=s&jobsource=2018indexpoc&lang=tw"
        
        driver.get(url)
        time.sleep(2)  # 等待頁面加載
        
        job_cards = driver.find_elements(By.TAG_NAME, 'article')
        for card in job_cards:
            try:
                company_name = card.get_attribute('data-cust-name')
                job_title = card.get_attribute('data-job-name')
                if company_name:
                    all_results.append({
                        "搜尋關鍵字": kw,
                        "公司名稱": company_name,
                        "職缺名稱": job_title
                    })
            except:
                continue
        
        # 更新進度條
        progress_bar.progress((index + 1) / len(keywords))
    
    driver.quit()
    return pd.DataFrame(all_results)

# --- Streamlit 介面設計 ---
st.set_page_config(page_title="3D 列印企業情報站", layout="wide")

st.title("🏗️ 3D 列印使用企業搜集器")
st.markdown("""
這個工具會自動爬取 **104 人力銀行**，尋找職缺描述中提到特定 3D 列印技術或品牌的公司。
""")

with st.sidebar:
    st.header("設定搜尋條件")
    input_kw = st.text_area("關鍵字 (請用逗號分隔)", 
                           "Formlabs, Phrozen, Bambu Lab, SLA 3D Printing")
    submit_button = st.button("🚀 開始爬取")

if submit_button:
    keyword_list = [k.strip() for k in input_kw.split(',')]
    
    with st.spinner('爬蟲運作中，請稍候...'):
        df_result = scrape_104(keyword_list)
    
    if not df_result.empty:
        # 資料清洗：去除重複公司
        df_clean = df_result.drop_duplicates(subset=['公司名稱']).reset_index(drop=True)
        
        st.success(f"✅ 抓取完成！共找到 {len(df_clean)} 家不重複公司。")
        
        # 顯示統計數據
        col1, col2 = st.columns(2)
        col1.metric("總搜尋量", len(df_result))
        col2.metric("獨特企業數", len(df_clean))
        
        # 顯示表格
        st.dataframe(df_clean, use_container_width=True)
        
        # 下載按鈕
        csv = df_clean.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 下載企業名單 CSV",
            data=csv,
            file_name="3d_printing_companies.csv",
            mime="text/csv",
        )
    else:
        st.warning("查無資料，請更換關鍵字再試一次。")
