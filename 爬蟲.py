import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

st.set_page_config(page_title="3D列印企業多平台搜集", layout="wide")

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

def scrape_104(driver, keyword):
    results = []
    url = f"https://www.104.com.tw/jobs/search/?kw={keyword}"
    driver.get(url)

    wait = WebDriverWait(driver, 10)

    try:
        items = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//article[contains(@class, "job-list-item")]')
            )
        )

        for item in items:
            try:
                company = item.get_attribute('data-cust-name')
                job = item.get_attribute('data-job-name')
                if company:
                    results.append({"來源": "104", "公司名稱": company, "職缺": job})
            except:
                continue
    except:
        st.warning(f"104 抓取失敗：{keyword}")

    return results

def scrape_1111(driver, keyword):
    results = []
    url = f"https://www.1111.com.tw/search/job?ks={keyword}"
    driver.get(url)

    wait = WebDriverWait(driver, 10)

    try:
        items = wait.until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, 'job_item_info')
            )
        )

        for item in items:
            try:
                company = item.find_element(By.CLASS_NAME, 'job_item_company').text
                job = item.find_element(By.CLASS_NAME, 'job_item_title').text
                results.append({"來源": "1111", "公司名稱": company, "職缺": job})
            except:
                continue
    except:
        st.warning(f"1111 抓取失敗：{keyword}")

    return results

# UI
st.title("🏗️ 3D列印企業情報搜集器")

keywords = st.text_input("關鍵字（逗號分隔）", "Formlabs, Phrozen")
start = st.button("開始")

if start:
    driver = get_driver()
    all_data = []

    try:
        for kw in keywords.split(","):
            kw = kw.strip()
            st.write(f"搜尋：{kw}")

            all_data += scrape_104(driver, kw)
            all_data += scrape_1111(driver, kw)

        if all_data:
            df = pd.DataFrame(all_data).drop_duplicates()
            st.dataframe(df)
        else:
            st.info("沒有資料")

        screenshot = driver.get_screenshot_as_png()

    finally:
        driver.quit()

    st.image(screenshot)
