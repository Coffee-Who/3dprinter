# 🎯 職缺雷達系統

自動爬取 104 & 1111 人力銀行，Web 介面管理，定時排程，匯出 Excel。

## 📁 目錄結構
```
job-scraper/
├── app.py                          # Streamlit 主程式（Web 介面）
├── run_scraper.py                  # CLI 爬蟲腳本（Actions 用）
├── requirements.txt
├── utils/
│   ├── scraper.py                  # 104 & 1111 爬蟲
│   ├── storage.py                  # 資料讀寫
│   └── exporter.py                 # Excel 匯出
├── data/
│   ├── jobs.json                   # 職缺資料庫
│   └── config.json                 # 系統設定
└── .github/workflows/
    └── daily_scrape.yml            # 定時排程
```

## 🚀 部署步驟

### 1. Push 到 GitHub
```bash
git init
git add .
git commit -m "init"
git remote add origin https://github.com/你的帳號/job-scraper.git
git push -u origin main
```

### 2. 部署到 Streamlit Cloud（免費）
1. 前往 https://share.streamlit.io
2. 點選「New app」
3. 選擇你的 GitHub repo
4. Main file path: `app.py`
5. 點擊 Deploy

### 3. GitHub Actions 自動排程
- 已自動設定為每天台灣時間 09:00 執行
- 可在 GitHub → Actions 頁面手動觸發測試

## ⚠️ 注意事項
- 爬取行為請遵守各網站使用條款
- 建議設定適當的爬取間隔（已內建 1.5 秒延遲）
- 大量爬取可能導致 IP 被封鎖
