# 🖨️ Formlabs 列印儀表板

> 實威國際 × Formlabs Dashboard API — 應用工程師工具平台

---

## 📁 專案結構

```
formlabs_dashboard/
├── app.py                  # Streamlit 主入口（導覽列 + 路由）
├── formlabs_api.py         # Formlabs API 封裝 + Demo mock 資料
├── requirements.txt        # Python 套件清單
├── .streamlit/
│   └── config.toml         # Streamlit 主題設定（深色）
└── pages/
    ├── __init__.py
    ├── home.py             # 首頁（入口網站）
    └── dashboard.py        # 列印儀表板（主功能頁）
```

---

## 🚀 部署到 Streamlit Cloud

### 1. 上傳到 GitHub

```bash
git init
git add .
git commit -m "init: Formlabs dashboard"
git remote add origin https://github.com/<你的帳號>/<repo名稱>.git
git push -u origin main
```

### 2. 到 Streamlit Cloud 部署

1. 前往 [share.streamlit.io](https://share.streamlit.io)
2. 點「New app」→ 選你的 GitHub repo
3. Main file：`app.py`
4. 點「Deploy」

### 3. 整合到現有 App

若要整合到 `https://3dprinter-aggkdobxbzfyxgxgxpwon8.streamlit.app/`，
直接將 `app.py` 的內容**取代**現有 app 的 `app.py`，
並將 `pages/` 資料夾、`formlabs_api.py` 一起上傳即可。

---

## 🔑 取得 Formlabs API 憑證

1. 登入 [dashboard.formlabs.com/#developer](https://dashboard.formlabs.com/#developer)
2. 點「Create Application」
3. 複製 **Client ID** 與 **Client Secret**
4. 在儀表板側邊欄輸入後點「連線」

> ⚠️ Access Token 有效期 24 小時，系統會在下次載入時自動重新取得。

---

## 📊 功能說明

### 首頁（主頁）
- 平台功能介紹卡片
- 三步驟快速開始指引
- 直接跳轉儀表板按鈕

### 儀表板
| 區塊 | 說明 |
|------|------|
| **KPI 數字列** | 印表機總數、列印中數量、任務數、成功率、材料用量、累計時數 |
| **印表機狀態卡** | 每台機器即時狀態、任務進度、材料餘量 |
| **統計圖表** | 可切換「人員 / 機器 / 材料 / 狀態 / 日期趨勢」5 種維度 |
| **列印紀錄表** | 支援機器、人員、材料、狀態 4 維度篩選，最新 200 筆 |

### 導覽列
- **上方 Nav Bar**：桌面版主導覽
- **下方 Tab Bar**：手機版底部標籤列

---

## 🛠️ 本機執行（開發用）

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📡 API 端點參考

| 功能 | 端點 |
|------|------|
| 取得 Token | `POST https://api.formlabs.com/developer/v1/o/token/` |
| 列出印表機 | `GET  https://api.formlabs.com/developer/v1/printers/` |
| 列印紀錄 | `GET  https://api.formlabs.com/developer/v1/prints/` |
| 材料匣 | `GET  https://api.formlabs.com/developer/v1/cartridges/` |
| 料槽 | `GET  https://api.formlabs.com/developer/v1/tanks/` |

完整文件：[Formlabs Web API 0.8.1](https://formlabs-dashboard-api-resources.s3.amazonaws.com/formlabs-web-api-latest.html)

---

*🗓️ 建立：2026 年 4 月 ｜ 實威國際 台中分公司應用工程師*
