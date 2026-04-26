from playwright.sync_api import sync_playwright
import time
pw = sync_playwright().start()
browser = pw.chromium.launch(headless=True)
page = browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
page.goto('https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword=SOLIDWORKS&order=15&asc=0&page=1&mode=s', wait_until='networkidle', timeout=30000)
time.sleep(3)
html = page.content()
print('頁面長度:', len(html))
print('包含職缺:', 'jobNo' in html or 'job-list' in html or 'custName' in html)
print('前500字:', html[:500])
browser.close()
pw.stop()
