"""
scraper.py - 104 & 1111 人力銀行爬蟲
⚠️  注意：爬取行為請遵守各網站 ToS，自行承擔風險
"""
import requests
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

TODAY = datetime.now().strftime("%Y-%m-%d")


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


# ══════════════════════════════════
# 104 人力銀行
# ══════════════════════════════════
def scrape_104(keyword: str, max_pages: int = 3) -> list:
    """爬取 104 人力銀行職缺"""
    results = []
    session = requests.Session()
    session.headers.update(HEADERS)
    session.headers["Referer"] = "https://www.104.com.tw"

    for page in range(1, max_pages + 1):
        try:
            url = (
                f"https://www.104.com.tw/jobs/search/?"
                f"ro=0&kwop=7&keyword={requests.utils.quote(keyword)}"
                f"&order=15&asc=0&page={page}&mode=s&jobsource=2018indexpoc"
            )
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # 找職缺卡片
            cards = soup.select("article.b-block--top-bord") or \
                    soup.select("[data-job-no]") or \
                    soup.select(".job-list-item")

            if not cards:
                # 嘗試 API 方式
                api_results = _scrape_104_api(keyword, page, session)
                results.extend(api_results)
                if not api_results:
                    break
                continue

            for card in cards:
                try:
                    title_el = card.select_one("a.info-job__title, .job-name a, h2 a")
                    if not title_el:
                        continue

                    title   = _clean(title_el.get_text())
                    job_url = title_el.get("href", "")
                    if job_url and not job_url.startswith("http"):
                        job_url = "https:" + job_url if job_url.startswith("//") \
                                  else "https://www.104.com.tw" + job_url

                    company_el = card.select_one("a.info-company__name, .company-name a")
                    company    = _clean(company_el.get_text()) if company_el else ""

                    loc_el  = card.select_one(".info-tags__item:first-child, .job-address")
                    location= _clean(loc_el.get_text()) if loc_el else ""

                    sal_el  = card.select_one(".b-tag--default, .salary")
                    salary  = _clean(sal_el.get_text()) if sal_el else "面議"

                    content_el = card.select_one(".info-description, .job-description")
                    content    = _clean(content_el.get_text()) if content_el else ""

                    # 技能 tags
                    skill_els = card.select(".b-badge__item, .skill-tag")
                    skills    = [_clean(s.get_text()) for s in skill_els[:8]]

                    results.append({
                        "source":     "104",
                        "title":      title,
                        "company":    company,
                        "location":   location,
                        "salary":     salary,
                        "content":    content,
                        "skills":     skills,
                        "experience": "",
                        "education":  "",
                        "url":        job_url,
                        "date":       TODAY,
                        "salary_min": _parse_salary_min(salary),
                    })
                except Exception:
                    continue

            time.sleep(1.5)

        except requests.RequestException as e:
            print(f"[104] 第{page}頁失敗：{e}")
            break

    return results


def _scrape_104_api(keyword: str, page: int, session: requests.Session) -> list:
    """使用 104 非官方 API"""
    results = []
    try:
        api_url = (
            f"https://www.104.com.tw/jobs/search/list?"
            f"ro=0&kwop=7&keyword={requests.utils.quote(keyword)}"
            f"&order=15&asc=0&page={page}&mode=s&jobsource=2018indexpoc"
        )
        session.headers["Accept"] = "application/json, text/plain, */*"
        resp = session.get(api_url, timeout=15)
        data = resp.json()

        for item in data.get("data", {}).get("list", []):
            job_no  = item.get("jobNo", "")
            job_url = f"https://www.104.com.tw/job/{job_no}" if job_no else ""
            salary  = item.get("salaryDesc", "面議")
            skills  = [t.get("description","") for t in item.get("tags", [])[:8]]

            results.append({
                "source":     "104",
                "title":      item.get("jobName", ""),
                "company":    item.get("custName", ""),
                "location":   item.get("jobAddrNoDesc", ""),
                "salary":     salary,
                "content":    item.get("description", ""),
                "skills":     skills,
                "experience": item.get("periodDesc", ""),
                "education":  item.get("eduDesc", ""),
                "url":        job_url,
                "date":       TODAY,
                "salary_min": _parse_salary_min(salary),
            })
    except Exception as e:
        print(f"[104 API] 失敗：{e}")
    return results


# ══════════════════════════════════
# 1111 人力銀行
# ══════════════════════════════════
def scrape_1111(keyword: str, max_pages: int = 3) -> list:
    """爬取 1111 人力銀行職缺"""
    results = []
    session = requests.Session()
    session.headers.update(HEADERS)
    session.headers["Referer"] = "https://www.1111.com.tw"

    for page in range(1, max_pages + 1):
        try:
            url = (
                f"https://www.1111.com.tw/search/job?"
                f"kw={requests.utils.quote(keyword)}&page={page}"
            )
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            cards = soup.select(".job-list-item, article.job-item, .job_item")

            if not cards:
                api_results = _scrape_1111_api(keyword, page, session)
                results.extend(api_results)
                if not api_results:
                    break
                continue

            for card in cards:
                try:
                    title_el = card.select_one("a.job-title, .job-name a, h3 a")
                    if not title_el:
                        continue

                    title   = _clean(title_el.get_text())
                    job_url = title_el.get("href", "")
                    if job_url and not job_url.startswith("http"):
                        job_url = "https://www.1111.com.tw" + job_url

                    company_el = card.select_one(".company-name, .corp-name")
                    company    = _clean(company_el.get_text()) if company_el else ""

                    loc_el  = card.select_one(".job-area, .location")
                    location= _clean(loc_el.get_text()) if loc_el else ""

                    sal_el  = card.select_one(".salary, .job-salary")
                    salary  = _clean(sal_el.get_text()) if sal_el else "面議"

                    content_el = card.select_one(".job-description, .description")
                    content    = _clean(content_el.get_text()) if content_el else ""

                    skill_els = card.select(".skill, .tag, .job-tag")
                    skills    = [_clean(s.get_text()) for s in skill_els[:8]]

                    exp_el = card.select_one(".experience, .exp")
                    exp    = _clean(exp_el.get_text()) if exp_el else ""

                    results.append({
                        "source":     "1111",
                        "title":      title,
                        "company":    company,
                        "location":   location,
                        "salary":     salary,
                        "content":    content,
                        "skills":     skills,
                        "experience": exp,
                        "education":  "",
                        "url":        job_url,
                        "date":       TODAY,
                        "salary_min": _parse_salary_min(salary),
                    })
                except Exception:
                    continue

            time.sleep(1.5)

        except requests.RequestException as e:
            print(f"[1111] 第{page}頁失敗：{e}")
            break

    return results


def _scrape_1111_api(keyword: str, page: int, session: requests.Session) -> list:
    """使用 1111 API"""
    results = []
    try:
        api_url = (
            f"https://www.1111.com.tw/job-bank/job-search?"
            f"kw={requests.utils.quote(keyword)}&page={page}&pageSize=30"
        )
        session.headers["Accept"] = "application/json"
        resp = session.get(api_url, timeout=15)
        data = resp.json()

        for item in data.get("data", {}).get("jobs", []) or data.get("jobs", []):
            job_id  = item.get("jobId") or item.get("id", "")
            job_url = f"https://www.1111.com.tw/job-bank/job-description/{job_id}"
            salary  = item.get("salaryDesc", "") or item.get("salary", "面議")
            skills  = item.get("skills", []) or []
            if isinstance(skills, str):
                skills = [s.strip() for s in skills.split(",")]

            results.append({
                "source":     "1111",
                "title":      item.get("jobName", "") or item.get("title", ""),
                "company":    item.get("companyName", "") or item.get("company", ""),
                "location":   item.get("district", "") or item.get("location", ""),
                "salary":     salary,
                "content":    item.get("jobContent", "") or item.get("content", ""),
                "skills":     skills[:8],
                "experience": item.get("workExp", "") or item.get("experience", ""),
                "education":  item.get("edu", "") or item.get("education", ""),
                "url":        job_url,
                "date":       TODAY,
                "salary_min": _parse_salary_min(salary),
            })
    except Exception as e:
        print(f"[1111 API] 失敗：{e}")
    return results


def _parse_salary_min(salary_text: str) -> int:
    """解析薪資最低值（用於排序）"""
    nums = re.findall(r"\d[\d,]*", salary_text or "")
    if not nums:
        return 0
    try:
        return int(nums[0].replace(",", ""))
    except Exception:
        return 0
