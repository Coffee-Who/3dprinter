"""
run_scraper.py - 供 GitHub Actions / 命令列執行的爬蟲腳本
"""
import sys
import time
from datetime import datetime
sys.path.insert(0, ".")

from utils.scraper  import scrape_104, scrape_1111
from utils.storage  import load_jobs, save_jobs, load_config, save_config
from utils.exporter import export_excel
from pathlib import Path

def main():
    print(f"\n{'='*50}")
    print(f"  職缺雷達系統 - 自動爬取")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    config   = load_config()
    jobs     = load_jobs()
    keywords = config.get("keywords", [])

    if not keywords:
        print("⚠️  未設定關鍵字，請先在 Web 介面設定")
        return

    print(f"📌 關鍵字：{', '.join(keywords)}")
    print(f"📄 已有資料：{len(jobs)} 筆\n")

    all_new = []
    for kw in keywords:
        if config.get("use_104", True):
            print(f"🔶 104 搜尋：{kw}")
            try:
                r = scrape_104(kw, max_pages=config.get("max_pages", 3))
                print(f"   → {len(r)} 筆")
                all_new.extend(r)
            except Exception as e:
                print(f"   ❌ 失敗：{e}")
            time.sleep(2)

        if config.get("use_1111", True):
            print(f"🔷 1111 搜尋：{kw}")
            try:
                r = scrape_1111(kw, max_pages=config.get("max_pages", 3))
                print(f"   → {len(r)} 筆")
                all_new.extend(r)
            except Exception as e:
                print(f"   ❌ 失敗：{e}")
            time.sleep(2)

    # 去重
    existing_urls = {j["url"] for j in jobs}
    added = [j for j in all_new if j["url"] not in existing_urls]

    # 排除關鍵字
    excl = config.get("exclude_keywords", [])
    if excl:
        before = len(added)
        added = [j for j in added if not any(
            e.lower() in j.get("title","").lower() for e in excl
        )]
        print(f"🚫 排除 {before - len(added)} 筆含排除關鍵字的職缺")

    jobs.extend(added)
    save_jobs(jobs)

    # 更新最後執行時間
    config["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_config(config)

    print(f"\n✅ 完成！新增 {len(added)} 筆職缺（總計 {len(jobs)} 筆）")

    # 自動匯出 Excel
    if config.get("auto_export", True):
        export_dir = Path("data/exports")
        export_dir.mkdir(parents=True, exist_ok=True)
        fname = f"職缺資料_{datetime.now().strftime('%Y%m%d')}.xlsx"
        fpath = export_dir / fname
        cols  = ["職缺名稱","公司名稱","工作地點","薪資","技能需求","工作內容","來源","連結","抓取日期"]
        excel = export_excel(jobs, cols)
        fpath.write_bytes(excel)
        print(f"📥 Excel 已匯出：{fpath}")

if __name__ == "__main__":
    main()
