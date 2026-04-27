from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup

pw = sync_playwright().start()
browser = pw.chromium.launch(headless=True)
page = browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
page.goto('https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword=SOLIDWORKS&order=15&asc=0&page=1&mode=s', wait_until='networkidle', timeout=30000)
time.sleep(3)

soup = BeautifulSoup(page.content(), 'html.parser')
cards = soup.select('div.job-summary')
print(f'找到 {len(cards)} 個職缺卡片')

if cards:
    card = cards[0]
    print('\n=== 第一筆職缺原始結構 ===')
    print(card.prettify()[:2000])

browser.close()
pw.stop()
