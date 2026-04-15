"""
3D 產業徵才自動爬蟲 - 主程式
執行方式：
  python main.py              → 立即執行一次
  python main.py --schedule   → 每天 09:00 定時執行
  python main.py --mode B     → 使用累計模式（選項 B）
"""

import argparse
import logging
import sys
from datetime import datetime

import schedule
import time

from crawler_104 import fetch_104_jobs, KEYWORDS
from crawler_1111 import fetch_1111_jobs
from exporter import export_daily, export_cumulative

# ── 設定 logging ──────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("crawler.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = "output"
CUMULATIVE_FILE = f"{OUTPUT_DIR}/3D產業職缺_累計.xlsx"
RUN_TIME = "09:00"   # 定時執行時間，可修改


def run_crawl(mode: str = "A"):
    logger.info(f"{'='*50}")
    logger.info(f"開始爬取 | 時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 模式: {mode}")
    logger.info(f"{'='*50}")

    all_jobs: list[dict] = []

    # ── 104 人力銀行 ──
    for kw in KEYWORDS:
        jobs = fetch_104_jobs(kw, max_pages=5)
        all_jobs.extend(jobs)

    # ── 1111 人力銀行 ──
    for kw in KEYWORDS:
        jobs = fetch_1111_jobs(kw, max_pages=5)
        all_jobs.extend(jobs)

    # ── 去除跨來源重複（以 公司+職缺名 為 key）──
    seen = set()
    deduped = []
    for j in all_jobs:
        key = f"{j.get('公司名稱','')}|{j.get('職缺名稱','')}"
        if key not in seen:
            seen.add(key)
            deduped.append(j)

    logger.info(f"合計抓取 {len(all_jobs)} 筆，去重後剩 {len(deduped)} 筆")

    if not deduped:
        logger.info("今日無新職缺，不產生 Excel。")
        return

    if mode.upper() == "B":
        saved = export_cumulative(deduped, CUMULATIVE_FILE)
    else:
        saved = export_daily(deduped, OUTPUT_DIR)

    logger.info(f"完成！檔案已儲存：{saved}")


def main():
    parser = argparse.ArgumentParser(description="3D 產業職缺自動爬蟲")
    parser.add_argument(
        "--mode", choices=["A", "B"], default="A",
        help="A=每天新建 Excel；B=統一累計 Excel（預設 A）"
    )
    parser.add_argument(
        "--schedule", action="store_true",
        help="啟用定時排程（每天 09:00 自動執行）"
    )
    parser.add_argument(
        "--time", default=RUN_TIME,
        help=f"定時執行時間，格式 HH:MM（預設 {RUN_TIME}）"
    )
    args = parser.parse_args()

    if args.schedule:
        logger.info(f"定時排程模式：每天 {args.time} 執行（模式 {args.mode}）")
        schedule.every().day.at(args.time).do(run_crawl, mode=args.mode)
        # 啟動時先跑一次
        run_crawl(mode=args.mode)
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        run_crawl(mode=args.mode)


if __name__ == "__main__":
    main()
