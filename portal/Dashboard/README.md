# 工作看板 · 3D 列印進度管理

白底科技感的工作進度看板,4 個分頁:**總表 / 看板 / 時間軸 / Dashboard**。

## 功能

- **總表** — 13 欄完整資料、可點擊欄位排序、多重篩選、搜尋、分頁、匯出 CSV
- **看板** — KPI strip + 卡片欄,可依狀態 / 進度 / 工程師 / 機台分欄,支援拖曳換欄、卡片詳情抽屜
- **時間軸** — 工程師泳道甘特圖,bar 內填色 = 進度 %,支援月 / 季 / 半年三段檢視
- **Dashboard** — 5 KPI + 3 預設分析(狀態 Donut、工程師橫條、進度長條) + 3 個自由分析(維度 × 圖表類型自由組合)

四個分頁共用同一份資料,改一處全處更新。

## 技術棧

- **純 HTML + CSS + React 18(透過 CDN UMD)+ Babel Standalone**
- 沒有 build step、沒有 npm,點兩下 `index.html` 即可開啟
- 也可直接放上 GitHub Pages

## 部署到 GitHub Pages

1. 在 GitHub 建立新 repo,把整個資料夾推上去
2. **Settings → Pages → Source** 選 `main` branch / root
3. 等幾分鐘,網址會像 `https://<你的帳號>.github.io/<repo-name>/`(會自動讀 `index.html`)

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
├── index.html                ← 入口檔(GitHub Pages 自動讀取)
├── README.md
├── .gitignore
│
├── src/
│   ├── app.jsx               ← 主外殼:四個分頁的容器
│   ├── helpers.js            ← 共用工具(狀態判定、日期、篩選、tokens)
│   ├── data.js               ← 訂單資料(mock,17 筆)
│   │
│   ├── views/
│   │   ├── view-table.jsx        ← 總表:13 欄 + 排序/篩選/匯出
│   │   ├── view-kanban.jsx       ← 看板:KPI + 拖曳卡片 + 抽屜
│   │   ├── view-gantt.jsx        ← 時間軸/甘特圖
│   │   └── view-dashboard.jsx    ← Dashboard:KPI + 預設/自由分析
│   │
│   └── styles/
│       ├── styles-shell.css      ← 外殼/分頁
│       ├── styles-kanban.css     ← 看板 + 抽屜
│       ├── styles-table.css      ← 總表
│       ├── styles-gantt.css      ← 時間軸
│       └── styles-dashboard.css  ← Dashboard
│
└── dist/
    └── 工作看板_standalone.html  ← 單檔離線版(所有 CSS/JS 內嵌)
```

## 修改資料

打開 `src/data.js`,`window.KANBAN_DATA` 是陣列,每筆物件欄位:

```js
{
  seq: 1,                      // 序列
  id: '202512100001',          // EF 單號
  customer: '客戶名稱',
  engineer: 'Jimmy',           // Jimmy | Jaylen | Bill | Barry
  dueDate: '2026-01-21',       // 期望交期 (yyyy-mm-dd)
  startDate: '2026-01-16',     // 開始日 (空字串 = 未排程)
  endDate: '2026-01-19',
  material: '足夠',            // '足夠' | '需調撥'
  progress: 100,               // 0 | 25 | 50 | 75 | 100
  machine: 'Form4',            // Form4 | Form4L | Fuse1+ | Mark2
  complete: '是',              // '是' | '否'
  remark: '',
}
```

要新增工程師或機台,改 `src/helpers.js` 內的 `K.ENG_ORDER` / `K.ENG_LABEL` / `K.ENG_TONE` / `K.MACHINES`。

## 今日基準日

預設 `2026-05-14`。要改成「當下系統日期」,把 `src/helpers.js` 裡的

```js
K.TODAY = new Date('2026-05-14');
```

改成

```js
K.TODAY = new Date();
```

## License

MIT — 自由使用、修改、商用。
