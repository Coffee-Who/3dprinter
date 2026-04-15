"""
104 人力銀行 3D 產業職缺爬蟲
支援關鍵字：3D掃描、3D列印、3D Scanning、3D Printing、逆向工程
"""

import time
import random
import logging
from datetime import datetime, timedelta
from typing import Optional
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS_POOL = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.104.com.tw/",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept-Language": "zh-TW,zh;q=0.9",
        "Referer": "https://www.104.com.tw/",
    },
]

KEYWORDS = [
    "3D掃描",
    "3D列印",
    "3D Scanning",
    "3D Printing",
    "逆向工程",
]

BASE_API = "https://www.104.com.tw/jobs/search/api/jobs"


def _get_headers():
    return random.choice(HEADERS_POOL)


def _sleep(min_s=1.5, max_s=3.5):
    time.sleep(random.uniform(min_s, max_s))


def _is_within_24h(date_str: str) -> bool:
    """判斷刊登日期是否在過去 24 小時內"""
    if not date_str:
        return False
    now = datetime.now()
    cutoff = now - timedelta(hours=24)
    try:
        # 104 API 回傳格式如 "2024/04/15"
        job_date = datetime.strptime(date_str.strip(), "%Y/%m/%d")
        return job_date >= cutoff.replace(hour=0, minute=0, second=0, microsecond=0)
    except ValueError:
        return False


def _extract_keyword_snippet(text: str, keyword: str, window: int = 60) -> str:
    """從文字中節錄包含關鍵字的片段"""
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
        snippet = snippet + "…"
    return snippet


def fetch_104_jobs(keyword: str, max_pages: int = 5) -> list[dict]:
    """抓取 104 人力銀行指定關鍵字的職缺（過去 24 小時）"""
    results = []
    session = requests.Session()

    for page in range(1, max_pages + 1):
        params = {
            "keyword": keyword,
            "order": "1",       # 依最新刊登排序
            "asc": "0",
            "page": page,
            "pagesize": "40",
            "mode": "s",
            "jobsource": "2018indexpoc",
        }

        try:
            resp = session.get(
                BASE_API,
                params=params,
                headers=_get_headers(),
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning(f"[104] 第 {page} 頁請求失敗 (關鍵字={keyword}): {e}")
            break

        jobs = data.get("data", {}).get("list", [])
        if not jobs:
            logger.info(f"[104] 關鍵字「{keyword}」第 {page} 頁無資料，停止翻頁")
            break

        found_old = False
        for job in jobs:
            date_str = job.get("appearDate", "")
            if not _is_within_24h(date_str):
                found_old = True
                continue

            job_no = job.get("jobNo", "")
            job_url = f"https://www.104.com.tw/job/{job_no}" if job_no else ""

            # 取薪資
            salary = job.get("salaryDesc", "面議")
            if not salary:
                salary = "面議"

            # 取地點
            address = job.get("jobAddrNoDesc", "") or job.get("jobAddress", "")

            # 取關鍵字片段
            job_desc = job.get("description", "") or ""
            snippet = _extract_keyword_snippet(job_desc, keyword)

            results.append({
                "日期": date_str,
                "公司名稱": job.get("custName", ""),
                "職缺名稱": job.get("jobName", ""),
                "薪資範圍": salary,
                "工作地點": address,
                "職缺連結": job_url,
                "關鍵字": keyword,
                "關鍵字匹配段落": snippet,
                "來源": "104人力銀行",
            })

        if found_old:
            logger.info(f"[104] 關鍵字「{keyword}」已遇到 24 小時前資料，停止翻頁")
            break

        _sleep()

    logger.info(f"[104] 關鍵字「{keyword}」共找到 {len(results)} 筆近 24 小時職缺")
    return results
