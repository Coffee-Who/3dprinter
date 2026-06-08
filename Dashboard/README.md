# 3D 列印 · 工作管理平台

白底科技感內部管理工具，Firebase 即時資料庫版本。

## 檔案結構

```
.
├── index.html          ← 主入口（登入、Sidebar、管理員後台）
├── workboard.html      ← 工作看板（可獨立開啟，也可被 index 嵌入）
├── issues.html         ← 異常與資源（同上）
├── firebase-config.js  ← ⚠️ 填入你的 Firebase 設定
└── README.md
```

---

## 快速開始

### Step 1 — 建立 Firebase 專案

1. [Firebase Console](https://console.firebase.google.com/) → 新增專案
2. 左側「建構」→ **Authentication** → Sign-in method → 啟用 **電子郵件/密碼**
3. 左側「建構」→ **Firestore Database** → 建立資料庫（選 `asia-east1`）

### Step 2 — 填寫設定

編輯 `firebase-config.js`，將 `YOUR_*` 換成你的 Firebase 設定：

```
Firebase Console → 專案設定（齒輪圖示）→ 你的應用程式 → firebaseConfig
```

### Step 3 — 建立第一個管理員

**Firebase Console → Authentication → 使用者 → 新增使用者**  
填入 Email 和密碼，複製產生的 **User UID**。

**Firebase Console → Firestore → 新增集合 → `users` → 新增文件**  
- Document ID = 剛才的 User UID
- 加入以下欄位：

| 欄位 | 類型 | 值 |
|------|------|-----|
| `displayName` | string | 管理員 |
| `email`       | string | 你的 Email |
| `permissions` | array  | `admin` |
| `active`      | boolean | `true` |

### Step 4 — Firestore Security Rules

Firebase Console → Firestore → **規則** → 貼上以下內容：

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function isLoggedIn() { return request.auth != null; }
    function isAdmin()    {
      return isLoggedIn() &&
        get(/databases/$(database)/documents/users/$(request.auth.uid))
          .data.permissions.hasAny(['admin']);
    }
    function hasPerm(p) {
      return isLoggedIn() &&
        get(/databases/$(database)/documents/users/$(request.auth.uid))
          .data.permissions.hasAny([p, 'admin']);
    }

    match /users/{uid} {
      allow read: if isLoggedIn();
      allow write: if isAdmin();
    }
    match /orders/{id} {
      allow read:   if hasPerm('view_board');
      allow create,update: if hasPerm('edit_board');
      allow delete: if hasPerm('delete_board');
    }
    match /anomalies/{id} {
      allow read:   if hasPerm('view_issues');
      allow create,update: if hasPerm('edit_issues');
      allow delete: if hasPerm('delete_issues');
    }
    match /ipa_purchases/{id} {
      allow read:   if hasPerm('view_issues');
      allow create,update: if hasPerm('edit_issues');
      allow delete: if hasPerm('delete_issues');
    }
    match /equipment/{id} {
      allow read:   if hasPerm('view_issues');
      allow create,update: if hasPerm('edit_issues');
      allow delete: if hasPerm('delete_issues');
    }
  }
}
```

### Step 5 — 部署到 GitHub Pages

```bash
git init
git add .
git commit -m "3D print dashboard"
git remote add origin https://github.com/你的帳號/你的repo.git
git push -u origin main
```

GitHub → Settings → Pages → Branch: `main` / `(root)` → Save

等幾分鐘後，網址為：`https://你的帳號.github.io/你的repo/`

---

## 本機測試

```bash
# Python（推薦）
python3 -m http.server 8000

# Node
npx serve .
```

開啟 `http://localhost:8000/`

> ⚠️ 請勿直接雙擊 `index.html` 開啟（`file://` 協定會阻擋 Firebase）

---

## 權限說明

| 代碼 | 說明 |
|------|------|
| `view_board` | 查看工作看板 |
| `edit_board` | 新增、編輯訂單 |
| `delete_board` | 刪除訂單 |
| `view_issues` | 查看異常與資源 |
| `edit_issues` | 新增、編輯異常/IPA/設備 |
| `delete_issues` | 刪除異常與資源 |
| `view_report` | 查看報表分析 |
| `admin` | 管理員（所有權限） |

### 角色預設

| 角色 | 包含權限 |
|------|---------|
| 👑 管理員 | 全部 (`admin`) |
| 🔷 主管   | view+edit 看板 + 異常 + 報表 |
| 🔩 工程師 | view+edit 看板 + 異常 |
| 👁 檢視者 | 僅查看 |

---

## 應用功能

### 🗂 工作看板 (`workboard.html`)
- **總表** — 13 欄完整資料，可排序、多重篩選、分頁、匯出 CSV，支援新增/編輯/刪除
- **看板** — KPI strip + 卡片欄，依狀態/進度/工程師/機台分欄，支援拖曳換欄、卡片詳情抽屜
- **時間軸** — 工程師泳道甘特圖，bar 內填色 = 進度 %
- **Dashboard** — 5 KPI + 3 預設圖 + 3 自由圖表

### ⚠️ 異常與資源 (`issues.html`)
- **客戶異常** — 含多筆後續進度，支援新增/編輯/刪除
- **IPA 採購** — 含合計桶數，支援新增/編輯/刪除
- **設備清單** — 含合計金額，支援新增/編輯/刪除
- **分析** — 5 KPI + 6 圖表

---

MIT License
