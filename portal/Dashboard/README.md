# 3D 列印 · 工作管理平台

白底科技感的內部工作管理工具,左側 sidebar 切換 2 個 app:

## 應用

### 🟦 工作看板 (WORK BOARD)
4 個分頁共用同一份訂單資料:
- **總表** — 13 欄完整資料、可點擊欄位排序、多重篩選、搜尋、分頁、匯出 CSV
- **看板** — KPI strip + 卡片欄,可依狀態 / 進度 / 工程師 / 機台分欄,支援拖曳換欄、卡片詳情抽屜
- **時間軸** — 工程師泳道甘特圖,bar 內填色 = 進度 %,支援月 / 季 / 半年三段檢視
- **Dashboard** — 5 KPI + 3 預設分析(狀態 Donut、工程師橫條、進度長條) + 3 個自由分析(維度 × 圖表類型自由組合)

### ⚠️ 異常與資源 (ISSUES · RESOURCES)
4 個子分頁:
- **客戶異常** — 含多筆後續進度,支援搜尋 / 狀態 / 工程師篩選
- **IPA 採購** — 採購紀錄,含合計桶數顯示
- **設備清單** — 工具與器材,含合計金額顯示
- **分析** — 5 KPI + 6 張圖表(異常工程師/狀態分布、IPA 人員/月份趨勢、設備支出方式/金額排行)

## 技術棧

- **純 HTML + CSS + React 18(透過 CDN UMD)+ Babel Standalone**
- 沒有 build step、沒有 npm,點兩下 `index.html` 即可開啟
- 也可直接放上 GitHub Pages

## 部署到 GitHub Pages

1. 在 GitHub 建立新 repo,把整個資料夾推上去
2. **Settings → Pages → Source** 選 `main` branch / root
3. 等幾分鐘,網址會像 `https://<你的帳號>.github.io/<repo-name>/`

> URL 有 hash 記憶 — `#board/kanban` 直連看板分頁、`#issues/ipa` 直連 IPA 採購頁。

## 本機預覽

由於用了 CDN script,有些瀏覽器在 `file://` 下會擋,建議起個小 server:

```bash
# Python
python3 -m http.server 8000

# Node
npx serve .
```

打開 `http://localhost:8000/`。

## 檔案結構

```
.
├── index.html                  ← 入口檔(GitHub Pages 自動讀取)
├── README.md
├── .gitignore
│
├── src/
│   ├── app.jsx                 ← 主外殼:sidebar + tabs 切換
│   ├── helpers.js              ← 共用工具(狀態判定、日期、篩選、tokens)
│   ├── data.js                 ← 訂單資料(17 筆)
│   ├── data-issues.js          ← 異常 / IPA / 設備資料
│   │
│   ├── views/
│   │   ├── view-table.jsx        ← 總表
│   │   ├── view-kanban.jsx       ← 看板
│   │   ├── view-gantt.jsx        ← 時間軸
│   │   ├── view-dashboard.jsx    ← Dashboard
│   │   └── view-issues.jsx       ← 異常與資源(4 子分頁)
│   │
│   └── styles/
│       ├── styles-shell.css      ← 外殼 + sidebar + 通用 toolbar
│       ├── styles-kanban.css     ← 看板 + 抽屜
│       ├── styles-table.css      ← 總表(共用 .kt-* class)
│       ├── styles-gantt.css      ← 時間軸
│       ├── styles-dashboard.css  ← Dashboard 圖表
│       └── styles-issues.css     ← 異常頁專用補強
│
└── dist/
    └── 工作看板_standalone.html  ← 單檔離線版(所有 CSS/JS 內嵌)
```

## 修改資料

**訂單資料**:`src/data.js` 內的 `window.KANBAN_DATA`,每筆物件:

```js
{
  seq: 1,                      // 序列
  id: '202512100001',          // EF 單號
  customer: '客戶名稱',
  engineer: 'Jimmy',           // Jimmy | Jaylen | Bill | Barry
  dueDate: '2026-01-21',       // 期望交期
  startDate: '2026-01-16',     // 開始日
  endDate: '2026-01-19',
  material: '足夠',            // '足夠' | '需調撥'
  progress: 100,               // 0 | 25 | 50 | 75 | 100
  machine: 'Form4',            // Form4 | Form4L | Fuse1+ | Mark2
  complete: '是',              // '是' | '否'
  remark: '',
}
```

**異常 / IPA / 設備**:`src/data-issues.js` 內的三個 `window.ISSUES_*` 陣列。

要新增工程師或機台,改 `src/helpers.js` 內的 `K.ENG_ORDER` / `K.ENG_LABEL` / `K.ENG_TONE` / `K.MACHINES`。

## 今日基準日

預設 `2026-05-14`(用於倒數天數、甘特圖今日線)。要改成「當下系統日期」,把 `src/helpers.js` 裡的

```js
K.TODAY = new Date('2026-05-14');
```

改成

```js
K.TODAY = new Date();
```

## License

MIT — 自由使用、修改、商用。
