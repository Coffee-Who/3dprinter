"""
scraper.py - 104 & 1111 爬蟲（正式版）
已確認 104 HTML 結構，選取器完全對應
"""
import re, time, urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup

TODAY = datetime.now().strftime("%Y-%m-%d")

def _clean(text):
    return re.sub(r"\s+", " ", text or "").strip()

def _parse_salary_min(s):
    nums = re.findall(r"\d[\d,]*", s or "")
    try: return int(nums[0].replace(",","")) if nums else 0
    except: return 0

def _make_browser():
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.launch(
        headless=True,
        args=["--no-sandbox","--disable-setuid-sandbox","--disable-blink-features=AutomationControlled"]
    )
    page = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        locale="zh-TW",
        viewport={"width":1280,"height":800},
    ).new_page()
    return pw, browser, page

# ══════════════════════════════════════════════
# 104 人力銀行
# ══════════════════════════════════════════════
def scrape_104(keyword, max_pages=3):
    results = []
    pw = browser = page = None
    try:
        pw, browser, page = _make_browser()
        page.goto("https://www.104.com.tw/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        for pg in range(1, max_pages + 1):
            try:
                kw_enc = urllib.parse.quote(keyword)
                url = (f"https://www.104.com.tw/jobs/search/?"
                       f"ro=0&kwop=7&keyword={kw_enc}&order=15&asc=0&page={pg}&mode=s")
                page.goto(url, wait_until="networkidle", timeout=30000)
                time.sleep(3)

                try:
                    page.wait_for_selector("div.job-summary", timeout=10000)
                except Exception:
                    pass

                soup = BeautifulSoup(page.content(), "html.parser")
                cards = soup.select("div.job-summary")

                found = 0
                for card in cards:
                    try:
                        # 職缺名稱 + URL
                        title_el = card.select_one("a.info-job__text")
                        if not title_el:
                            continue
                        title = _clean(title_el.get("title","") or title_el.get_text())
                        job_url = title_el.get("href","")

                        # 公司名稱
                        co_el = card.select_one("a.info-company__text")
                        company = _clean(co_el.get("title","").split("\n")[0].replace("公司名：","") if co_el else "")
                        if not company and co_el:
                            company = _clean(co_el.get_text())

                        # 地點、薪資、年資、學歷（info-tags）
                        tag_spans = card.select("div.info-tags span.info-tags__text")
                        tag_texts = [_clean(t.get_text()) for t in tag_spans if _clean(t.get_text())]
                        location  = tag_texts[0] if len(tag_texts) > 0 else ""
                        salary    = tag_texts[1] if len(tag_texts) > 1 else "面議"
                        exp       = tag_texts[2] if len(tag_texts) > 2 else ""
                        edu       = tag_texts[3] if len(tag_texts) > 3 else ""
                        # 若薪資看起來像地址就換成面議
                        if salary and ("市" in salary or "縣" in salary or "區" in salary):
                            salary = "面議"

                        # 工作內容描述
                        desc_el = card.select_one("p.info-description, div.info-description, [class*='description']")
                        content = _clean(desc_el.get_text()) if desc_el else ""

                        # 技能標籤
                        skill_els = card.select("a.b-badge__content, span.b-badge__content, [class*='badge__content']")
                        skills = [_clean(s.get_text()) for s in skill_els if _clean(s.get_text())][:8]

                        results.append({
                            "source":"104", "title":title, "company":company,
                            "location":location, "salary":salary, "content":content,
                            "skills":skills, "experience":exp, "education":edu,
                            "url":job_url, "date":TODAY,
                            "salary_min":_parse_salary_min(salary),
                        })
                        found += 1
                    except Exception:
                        continue

                print(f"[104] 第{pg}頁：{found} 筆")
                if found == 0:
                    break
                time.sleep(2)

            except Exception as e:
                print(f"[104] 第{pg}頁錯誤：{e}")
                break

    except Exception as e:
        print(f"[104] 瀏覽器錯誤：{e}")
    finally:
        try:
            if browser: browser.close()
            if pw: pw.stop()
        except Exception:
            pass

    return results


# ══════════════════════════════════════════════
# 1111 人力銀行
# ══════════════════════════════════════════════
def scrape_1111(keyword, max_pages=3):
    results = []
    pw = browser = page = None
    try:
        pw, browser, page = _make_browser()
        page.goto("https://www.1111.com.tw/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        for pg in range(1, max_pages + 1):
            try:
                kw_enc = urllib.parse.quote(keyword)
                url = f"https://www.1111.com.tw/search/job?kw={kw_enc}&page={pg}"
                page.goto(url, wait_until="networkidle", timeout=30000)
                time.sleep(3)

                # 先嘗試攔截 API JSON
                try:
                    resp = page.request.get(
                        f"https://www.1111.com.tw/search/job?kw={kw_enc}&page={pg}&pageSize=30&order=1",
                        headers={"Accept":"application/json","Referer":"https://www.1111.com.tw/"}
                    )
                    data = resp.json()
                    items = (data.get("data",{}).get("list",[]) or
                             data.get("data",{}).get("jobs",[]) or
                             data.get("list",[]) or [])
                    if items:
                        for it in items:
                            job_id = it.get("jobId") or it.get("id","")
                            salary = it.get("salaryDesc","") or it.get("salary","") or "面議"
                            skills = it.get("skills",[]) or []
                            if isinstance(skills, str):
                                skills = [s.strip() for s in skills.split(",")]
                            results.append({
                                "source":"1111",
                                "title":_clean(it.get("jobName","") or it.get("title","")),
                                "company":_clean(it.get("companyName","") or it.get("company","")),
                                "location":_clean(it.get("district","") or it.get("area","")),
                                "salary":salary,
                                "content":_clean(it.get("jobContent","") or it.get("content","")),
                                "skills":[s for s in skills if s][:8],
                                "experience":_clean(it.get("workExp","") or it.get("experience","")),
                                "education":_clean(it.get("edu","") or it.get("education","")),
                                "url":f"https://www.1111.com.tw/job-bank/job-description/{job_id}",
                                "date":TODAY,
                                "salary_min":_parse_salary_min(salary),
                            })
                        print(f"[1111] 第{pg}頁：{len(items)} 筆（API）")
                        time.sleep(2)
                        continue
                except Exception:
                    pass

                # 備用：HTML 解析
                soup = BeautifulSoup(page.content(), "html.parser")
                cards = soup.select("li[class*='job-item'], article[class*='job-item'], [class*='job-list'] > li")

                found = 0
                for card in cards:
                    try:
                        title_el = (card.select_one("a[class*='job-title']") or
                                    card.select_one("h3 a") or
                                    card.select_one("a[href*='job-description']"))
                        if not title_el: continue
                        title = _clean(title_el.get_text())
                        if not title: continue
                        href = title_el.get("href","")
                        job_url = ("https://www.1111.com.tw" + href
                                   if href and not href.startswith("http") else href)
                        co_el = card.select_one("[class*='company-name'],[class*='corp-name']")
                        company = _clean(co_el.get_text()) if co_el else ""
                        loc_el = card.select_one("[class*='job-area'],[class*='location'],[class*='area']")
                        location = _clean(loc_el.get_text()) if loc_el else ""
                        sal_el = card.select_one("[class*='salary'],[class*='pay']")
                        salary = _clean(sal_el.get_text()) if sal_el else "面議"
                        results.append({
                            "source":"1111","title":title,"company":company,
                            "location":location,"salary":salary,"content":"",
                            "skills":[],"experience":"","education":"",
                            "url":job_url,"date":TODAY,
                            "salary_min":_parse_salary_min(salary),
                        })
                        found += 1
                    except Exception:
                        continue

                print(f"[1111] 第{pg}頁：{found} 筆（HTML）")
                if found == 0:
                    break
                time.sleep(2)

            except Exception as e:
                print(f"[1111] 第{pg}頁錯誤：{e}")
                break

    except Exception as e:
        print(f"[1111] 瀏覽器錯誤：{e}")
    finally:
        try:
            if browser: browser.close()
            if pw: pw.stop()
        except Exception:
            pass

    return results
