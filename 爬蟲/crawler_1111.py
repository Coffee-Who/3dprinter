"""
1111 人力銀行 3D 產業職缺爬蟲
"""

import time
import random
import logging
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-TW,zh;q=0.9",
    "Referer": "https://www.1111.com.tw/",
}

BASE_URL = "https://www.1111.com.tw/job-bank/list"
API_URL = "https://www.1111.com.tw/voc/jobanal/ajaxGetJobList.asp"


def _sleep(min_s=2.0, max_s=4.0):
    time.sleep(random.uniform(min_s, max_s))


def _is_within_24h(date_str: str) -> bool:
    if not date_str:
        return False
    now = datetime.now()
    cutoff = now - timedelta(hours=24)
    try:
        # 1111 格式如 "2024/04/15" 或 "04/15"
        if len(date_str.strip()) == 5:
            date_str = f"{now.year}/{date_str.strip()}"
        job_date = datetime.strptime(date_str.strip(), "%Y/%m/%d")
        return job_date >= cutoff.replace(hour=0, minute=0, second=0, microsecond=0)
    except ValueError:
        return False


def _extract_keyword_snippet(text: str, keyword: str, window: int = 60) -> str:
    if not text or not keyword:
        return ""
    idx = text.find(keyword)
    if idx == -1:
        return ""
    start = max(0, idx - window)
    end = min(len(text), idx + len(keyword) + window)
    snippet = text[start:end].strip()
    if start > 0:
        snippet = "…" + snippet
    if end < len(text):
        snippet += "…"
    return snippet


def fetch_1111_jobs(keyword: str, max_pages: int = 5) -> list[dict]:
    """抓取 1111 人力銀行指定關鍵字的職缺（過去 24 小時）"""
    results = []
    session = requests.Session()

    for page in range(1, max_pages + 1):
        params = {
            "isnew": "1",       # 最新職缺
            "kw": keyword,
            "p": page,
            "sort": "date",
        }

        try:
            resp = session.get(
                BASE_URL,
                params=params,
                headers=HEADERS,
                timeout=15,
            )
            resp.raise_for_status()
        except Exception as e:
            logger.warning(f"[1111] 第 {page} 頁請求失敗 (關鍵字={keyword}): {e}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        job_cards = soup.select(".job-list-item, .job-item, article.job")

        if not job_cards:
            logger.info(f"[1111] 關鍵字「{keyword}」第 {page} 頁無資料")
            break

        found_old = False
        for card in job_cards:
            # 嘗試多種選擇器（1111 可能更新 HTML 結構）
            date_el = card.select_one(".date, .job-date, time")
            date_str = date_el.get_text(strip=True) if date_el else ""

            if date_str and not _is_within_24h(date_str):
                found_old = True
                continue

            title_el = card.select_one(".job-title a, h2 a, .title a")
            company_el = card.select_one(".company-name, .custName, .cust-name")
            salary_el = card.select_one(".salary, .job-salary")
            location_el = card.select_one(".location, .job-addr, .address")
            link_el = card.select_one("a[href*='/job/']")

            job_url = ""
            if link_el:
                href = link_el.get("href", "")
                job_url = href if href.startswith("http") else f"https://www.1111.com.tw{href}"

            desc_el = card.select_one(".job-desc, .description, .job-content")
            job_desc = desc_el.get_text(" ", strip=True) if desc_el else ""
            snippet = _extract_keyword_snippet(job_desc, keyword)

            results.append({
                "日期": date_str,
                "公司名稱": company_el.get_text(strip=True) if company_el else "",
                "職缺名稱": title_el.get_text(strip=True) if title_el else "",
                "薪資範圍": salary_el.get_text(strip=True) if salary_el else "面議",
                "工作地點": location_el.get_text(strip=True) if location_el else "",
                "職缺連結": job_url,
                "關鍵字": keyword,
                "關鍵字匹配段落": snippet,
                "來源": "1111人力銀行",
            })

        if found_old:
            logger.info(f"[1111] 關鍵字「{keyword}」已遇到 24 小時前資料，停止翻頁")
            break

        _sleep()

    logger.info(f"[1111] 關鍵字「{keyword}」共找到 {len(results)} 筆近 24 小時職缺")
    return results
