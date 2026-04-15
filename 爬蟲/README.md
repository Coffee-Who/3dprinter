# 3D 產業徵才自動爬蟲

自動從 **104 人力銀行** 與 **1111 人力銀行** 抓取近 24 小時內的 3D 相關職缺，輸出為格式化 Excel 檔。

---

## 📁 專案結構

```
3d_job_crawler/
├── main.py           ← 主程式（入口）
├── crawler_104.py    ← 104 人力銀行爬蟲
├── crawler_1111.py   ← 1111 人力銀行爬蟲
├── exporter.py       ← Excel 輸出模組
├── requirements.txt  ← 套件清單
├── crawler.log       ← 執行日誌（自動產生）
└── output/           ← Excel 輸出資料夾（自動產生）
```

---

## 🔧 安裝環境

### 1. 確認 Python 版本

需要 **Python 3.10+**

```bash
python --version
```

### 2. 建立虛擬環境（建議）

```bash
# 建立
python -m venv venv

# 啟動（Windows）
venv\Scripts\activate

# 啟動（macOS / Linux）
source venv/bin/activate
```

### 3. 安裝套件

```bash
pip install -r requirements.txt
```

---

## 🚀 執行方式

### 立即執行一次（每天產生新 Excel）

```bash
python main.py
```

輸出範例：`output/3D產業職缺_20240415.xlsx`

---

### 立即執行一次（累計到同一個 Excel）

```bash
python main.py --mode B
```

輸出：`output/3D產業職缺_累計.xlsx`（自動過濾重複職缺）

---

### 定時排程（每天 09:00 自動執行）

```bash
python main.py --schedule
```

自訂執行時間：

```bash
python main.py --schedule --time 08:30
```

搭配累計模式：

```bash
python main.py --schedule --mode B --time 09:00
```

> 程式會在啟動時先執行一次，之後每天定時執行。
> 請保持終端機視窗開啟，或使用系統排程（見下方）。

---

## ⏰ 使用系統排程（讓程式在背景自動執行）

### Windows — 工作排程器

1. 搜尋「工作排程器」並開啟
2. 建立基本工作 → 設定觸發時間（每天 09:00）
3. 動作 → 啟動程式，填入：
   - 程式：`C:\Path\To\venv\Scripts\python.exe`
   - 引數：`main.py --mode A`
   - 起始位置：`C:\Path\To\3d_job_crawler\`

### macOS / Linux — crontab

```bash
crontab -e
```

加入以下行（每天 09:00 執行，模式 A）：

```
0 9 * * * cd /path/to/3d_job_crawler && /path/to/venv/bin/python main.py --mode A >> crawler.log 2>&1
```

---

## 📊 Excel 輸出欄位說明

| 欄位 | 說明 |
|------|------|
| 日期 | 職缺刊登日期 |
| 公司名稱 | 徵才廠商全名 |
| 職缺名稱 | 完整職位標題 |
| 薪資範圍 | 月薪區間或「面議」 |
| 工作地點 | 縣市與行政區 |
| 職缺連結 | 可點擊的原始網頁 URL |
| 關鍵字 | 觸發此筆資料的搜尋關鍵字 |
| 關鍵字匹配段落 | 含關鍵字的工作內容摘要（選填）|
| 來源 | 104 或 1111 人力銀行 |

---

## 🔍 搜尋關鍵字

預設搜尋關鍵字（可在 `crawler_104.py` 的 `KEYWORDS` 清單修改）：

- `3D掃描`
- `3D列印`
- `3D Scanning`
- `3D Printing`
- `逆向工程`

---

## 🛡️ 防爬蟲說明

本程式已內建以下防偵測機制：

- **隨機 User-Agent**：模擬真實瀏覽器
- **隨機延遲**：每次請求間隔 1.5～3.5 秒
- **Referer 標頭**：模擬從網站首頁來的請求
- **Session 保持**：維持 cookies 連線

---

## ❓ 常見問題

**Q：執行後 output 資料夾是空的？**  
A：代表過去 24 小時內沒有新刊登的 3D 相關職缺，屬正常情況。

**Q：出現 `requests.exceptions.ConnectionError`？**  
A：請確認網路連線，或等待幾分鐘後重試（可能觸發了網站的臨時封鎖）。

**Q：如何新增 Yourator 等其他網站？**  
A：參考 `crawler_104.py` 的結構，新增一個 `crawler_yourator.py`，再在 `main.py` 中 import 並呼叫即可。

**Q：如何修改排程時間？**  
A：在 `main.py` 中修改 `RUN_TIME = "09:00"` 這一行，或使用 `--time` 參數指定。
