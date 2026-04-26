"""
scraper.py - 104 & 1111 人力銀行爬蟲（Playwright 版）
使用真實瀏覽器繞過反爬蟲，在你的 Windows 電腦上執行才有效
⚠️  注意：爬取行為請遵守各網站 ToS，自行承擔風險
"""
import re, time, json, requests
from datetime import datetime
from bs4 import BeautifulSoup

TODAY = datetime.now().strftime("%Y-%m-%d")

def _clean(text):
    return re.sub(r"\s+", " ", text or "").strip()

def _parse_salary_min(s):
    nums = re.findall(r"\d[\d,]*", s or "")
    try: return int(nums[0].replace(",","")) if nums else 0
    except: return 0

def _get_driver():
    """取得 Playwright 瀏覽器（無頭模式）"""
    try:
        from playwright.sync_api import sync_playwright
        return sync_playwright
    except ImportError:
        return None

# ══════════════════════════════════════════════
# 104 人力銀行
# ══════════════════════════════════════════════
def scrape_104(keyword, max_pages=3):
    results = _scrape_104_playwright(keyword, max_pages)
    if not results:
        # 備用：requests（在台灣 IP 可能有效）
        results = _scrape_104_requests(keyword, max_pages)
    return results


def _scrape_104_playwright(keyword, max_pages):
    """使用 Playwright 真實瀏覽器爬取 104"""
    results = []
    sync_playwright = _get_driver()
    if not sync_playwright:
        print("[104] Playwright 未安裝，跳過")
        return []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                ]
            )
            ctx = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="zh-TW",
                viewport={"width": 1280, "height": 800},
                extra_http_headers={
                    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
                }
            )
            page = ctx.new_page()

            # 先訪問首頁取得 Cookie
            page.goto("https://www.104.com.tw/", wait_until="domcontentloaded", timeout=20000)
            time.sleep(2)

            for pg in range(1, max_pages + 1):
                try:
                    kw_enc = requests.utils.quote(keyword)
                    url = (
                        f"https://www.104.com.tw/jobs/search/?"
                        f"ro=0&kwop=7&keyword={kw_enc}"
                        f"&order=15&asc=0&page={pg}&mode=s"
                    )
                    page.goto(url, wait_until="networkidle", timeout=25000)
                    time.sleep(2)

                    # 等待職缺列表出現
                    try:
                        page.wait_for_selector(
                            "article[data-job-no], .job-list-item, [data-job-no]",
                            timeout=8000
                        )
                    except Exception:
                        pass

                    html = page.content()
                    soup = BeautifulSoup(html, "html.parser")

                    # 嘗試從 script 取 JSON
                    page_results = _parse_104_html(soup)
                    if page_results:
                        results.extend(page_results)
                        print(f"[104] p{pg}: {len(page_results)} 筆 (Playwright)")
                    else:
                        print(f"[104] p{pg} 無資料，停止")
                        break

                    time.sleep(2)
                except Exception as e:
                    print(f"[104] Playwright p{pg} 錯誤: {e}")
                    break

            browser.close()
    except Exception as e:
        print(f"[104] Playwright 失敗: {e}")
    return results


def _parse_104_html(soup):
    """解析 104 HTML / inline JSON"""
    results = []

    # 方法1：從 script tag 取 inline JSON
    for script in soup.find_all("script"):
        txt = script.string or ""
        if '"jobNo"' in txt or '"jobName"' in txt:
            # 嘗試多種 JSON 結構
            patterns = [
                r'"list"\s*:\s*(\[.*?\])\s*[,}]',
                r'jobList\s*=\s*(\[.*?\])',
                r'"jobs"\s*:\s*(\[.*?\])',
            ]
            for pat in patterns:
                m = re.search(pat, txt, re.DOTALL)
                if m:
                    try:
                        items = json.loads(m.group(1))
                        for it in items:
                            job_no = it.get("jobNo","")
                            salary = it.get("salaryDesc","") or "面議"
                            tags = it.get("tags",{})
                            skills = []
                            if isinstance(tags, dict):
                                for v in tags.values():
                                    if isinstance(v, list):
                                        skills += [t.get("des","") for t in v if t.get("des")]
                            results.append({
                                "source":"104","title":_clean(it.get("jobName","")),"company":_clean(it.get("custName","")),
                                "location":_clean(it.get("jobAddrNoDesc","") or it.get("district","")),"salary":salary,
                                "content":_clean(it.get("description","") or it.get("jobContent","")),"skills":[s for s in skills if s][:8],
                                "experience":_clean(it.get("periodDesc","")),"education":_clean(it.get("eduDesc","")),
                                "url":f"https://www.104.com.tw/job/{job_no}","date":TODAY,"salary_min":_parse_salary_min(salary),
                            })
                        if results:
                            return results
                    except Exception:
                        pass

    # 方法2：CSS 選取器
    cards = soup.select("article[data-job-no],[data-job-no],.job-list-item")
    for card in cards:
        job_no = card.get("data-job-no","")
        title_el = card.select_one("a.info-job__title,a[href*='/job/'],h2 a,h3 a")
        if not title_el: continue
        title = _clean(title_el.get_text())
        co_el = card.select_one("a.info-company__name,.company-name,a[href*='/company/']")
        company = _clean(co_el.get_text()) if co_el else ""
        loc_el = card.select_one(".b-tag--default,.job-tags li:first-child,.location")
        location = _clean(loc_el.get_text()) if loc_el else ""
        sal_el = card.select_one(".b-tag--default ~ .b-tag--default,.salary,[class*='salary']")
        salary = _clean(sal_el.get_text()) if sal_el else "面議"
        skill_els = card.select(".b-badge__item,.skill-tag,.b-tag--default")
        skills = [_clean(s.get_text()) for s in skill_els[:8]]
        results.append({
            "source":"104","title":title,"company":company,"location":location,"salary":salary,
            "content":"","skills":skills,"experience":"","education":"",
            "url":f"https://www.104.com.tw/job/{job_no}" if job_no else "","date":TODAY,"salary_min":_parse_salary_min(salary),
        })
    return results


def _scrape_104_requests(keyword, max_pages):
    """備用 requests 方案（適合台灣本機 IP）"""
    results = []
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-TW,zh;q=0.9",
        "Referer": "https://www.104.com.tw/",
    })
    try: s.get("https://www.104.com.tw/", timeout=8); time.sleep(1)
    except: pass

    kw = requests.utils.quote(keyword)
    for pg in range(1, max_pages + 1):
        try:
            url = (f"https://www.104.com.tw/jobs/search/list"
                   f"?ro=0&kwop=7&keyword={kw}&order=15&asc=0&page={pg}&mode=s&jobsource=2018indexpoc")
            r = s.get(url, timeout=15)
            if r.status_code == 403:
                print(f"[104] IP 被封鎖（403），請在台灣本機執行")
                break
            data = r.json()
            items = data.get("data",{}).get("list",[]) or []
            for it in items:
                job_no = it.get("jobNo","")
                salary = it.get("salaryDesc","") or "面議"
                results.append({
                    "source":"104","title":_clean(it.get("jobName","")),"company":_clean(it.get("custName","")),
                    "location":_clean(it.get("jobAddrNoDesc","")),"salary":salary,"content":_clean(it.get("description","")),
                    "skills":[],"experience":_clean(it.get("periodDesc","")),"education":_clean(it.get("eduDesc","")),
                    "url":f"https://www.104.com.tw/job/{job_no}","date":TODAY,"salary_min":_parse_salary_min(salary),
                })
            if items: print(f"[104] p{pg}: {len(items)} 筆 (requests)")
            else: break
        except Exception as e:
            print(f"[104] requests p{pg} 失敗: {e}"); break
        time.sleep(2)
    return results


# ══════════════════════════════════════════════
# 1111 人力銀行
# ══════════════════════════════════════════════
def scrape_1111(keyword, max_pages=3):
    results = _scrape_1111_playwright(keyword, max_pages)
    if not results:
        results = _scrape_1111_requests(keyword, max_pages)
    return results


def _scrape_1111_playwright(keyword, max_pages):
    results = []
    sync_playwright = _get_driver()
    if not sync_playwright:
        return []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox","--disable-dev-shm-usage"])
            ctx = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
                locale="zh-TW", viewport={"width":1280,"height":800}
            )
            page = ctx.new_page()
            page.goto("https://www.1111.com.tw/", wait_until="domcontentloaded", timeout=20000)
            time.sleep(2)

            for pg in range(1, max_pages + 1):
                try:
                    kw_enc = requests.utils.quote(keyword)
                    url = f"https://www.1111.com.tw/search/job?kw={kw_enc}&page={pg}"
                    page.goto(url, wait_until="networkidle", timeout=25000)
                    time.sleep(2)
                    try:
                        page.wait_for_selector("li.job-item,.job-list-item,article.job-card", timeout=8000)
                    except: pass
                    html = page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    page_results = _parse_1111_html(soup)
                    if page_results:
                        results.extend(page_results)
                        print(f"[1111] p{pg}: {len(page_results)} 筆 (Playwright)")
                    else:
                        print(f"[1111] p{pg} 無資料，停止"); break
                    time.sleep(2)
                except Exception as e:
                    print(f"[1111] Playwright p{pg} 錯誤: {e}"); break
            browser.close()
    except Exception as e:
        print(f"[1111] Playwright 失敗: {e}")
    return results


def _parse_1111_html(soup):
    results = []
    cards = soup.select("li.job-item,.job-list-item,article.job-card,[data-job-id]")
    for card in cards:
        title_el = card.select_one("a.job-title,h3 a,.title a,a[href*='job-description']")
        if not title_el: continue
        title = _clean(title_el.get_text())
        job_url = title_el.get("href","")
        if job_url and not job_url.startswith("http"):
            job_url = "https://www.1111.com.tw" + job_url
        co_el = card.select_one(".company-name,.corp-name,.company a")
        company = _clean(co_el.get_text()) if co_el else ""
        loc_el = card.select_one(".job-area,.location,.area")
        location = _clean(loc_el.get_text()) if loc_el else ""
        sal_el = card.select_one(".salary,.job-salary,.pay")
        salary = _clean(sal_el.get_text()) if sal_el else "面議"
        skill_els = card.select(".skill,.tag,.job-tag")
        skills = [_clean(s.get_text()) for s in skill_els[:8]]
        results.append({
            "source":"1111","title":title,"company":company,"location":location,"salary":salary,
            "content":"","skills":skills,"experience":"","education":"",
            "url":job_url,"date":TODAY,"salary_min":_parse_salary_min(salary),
        })
    return results


def _scrape_1111_requests(keyword, max_pages):
    results = []
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-TW,zh;q=0.9",
        "Referer": "https://www.1111.com.tw/",
    })
    try: s.get("https://www.1111.com.tw/", timeout=8); time.sleep(1)
    except: pass

    kw = requests.utils.quote(keyword)
    for pg in range(1, max_pages + 1):
        try:
            url = f"https://www.1111.com.tw/search/job?kw={kw}&page={pg}&pageSize=30&order=1"
            r = s.get(url, timeout=15)
            data = r.json()
            items = (data.get("data",{}).get("list",[]) or
                     data.get("data",{}).get("jobs",[]) or
                     data.get("list",[]) or data.get("jobs",[]) or [])
            for it in items:
                job_id = it.get("jobId") or it.get("id","")
                salary = it.get("salaryDesc","") or it.get("salary","") or "面議"
                results.append({
                    "source":"1111","title":_clean(it.get("jobName","") or it.get("title","")),"company":_clean(it.get("companyName","") or it.get("company","")),
                    "location":_clean(it.get("district","") or it.get("area","")),"salary":salary,
                    "content":_clean(it.get("jobContent","") or it.get("content","")),"skills":[],"experience":"","education":"",
                    "url":f"https://www.1111.com.tw/job-bank/job-description/{job_id}","date":TODAY,"salary_min":_parse_salary_min(salary),
                })
            if items: print(f"[1111] p{pg}: {len(items)} 筆 (requests)")
            else: break
        except Exception as e:
            print(f"[1111] requests p{pg} 失敗: {e}"); break
        time.sleep(2)
    return results
