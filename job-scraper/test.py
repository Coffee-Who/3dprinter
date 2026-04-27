from utils.scraper import scrape_104
from utils.storage import load_jobs, save_jobs

print("開始爬取...")
r = scrape_104('SOLIDWORKS', max_pages=1)
print(f"爬到 {len(r)} 筆")

jobs = load_jobs()
jobs.extend(r)
save_jobs(jobs)
print(f"已儲存，目前共 {len(jobs)} 筆")